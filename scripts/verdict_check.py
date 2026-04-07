#!/usr/bin/env python3
"""
verdict_check.py — LLM 语义判定模块（VLA-T015-fix）

职责：
  将 expected-result 逐条与 verdict 做语义比对，
  判断 verdict 是否覆盖了每一条期望结果。

使用方式：
  python3 verdict_check.py \
    --expected-result "1. 条件A；2. 条件B" \
    --verdict-file /path/to/verdict.txt \
    [--method llm|ngram]  # 默认 llm，失败自动 fallback 到 ngram

环境变量：
  VERDICT_LLM_BASE_URL   — LLM API base URL（默认读取 openclaw 配置）
  VERDICT_LLM_API_KEY    — LLM API key（默认读取 openclaw 配置）
  VERDICT_LLM_MODEL      — 模型 ID（默认 gemini-3-flash-preview）

输出：JSON 格式的判定结果
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error


def parse_expected_items(er_text: str) -> list[str]:
    """将 expected-result 拆分为逐条。
    
    支持两种格式：
    - "1. xxx；2. yyy；3. zzz"（编号分隔）
    - "xxx；yyy；zzz"（纯分号分隔）
    
    优先按编号拆分（避免内容中的分号误切）。
    """
    # 方法1：按编号拆分（"1. "、"2. " 等）
    numbered = re.split(r'(?:^|[；;]\s*)(?=\d+\.\s)', er_text)
    numbered = [re.sub(r'^\d+\.\s*', '', i.strip()).strip('；; ') for i in numbered]
    numbered = [i for i in numbered if i and len(i) > 2]
    
    if len(numbered) >= 2:
        return numbered
    
    # 方法2：按中文分号拆分（仅在没有编号时使用）
    items = re.split(r'；', er_text)
    items = [re.sub(r'^\d+\.\s*', '', i.strip()) for i in items]
    return [i for i in items if i and len(i) > 2]


def load_openclaw_config() -> tuple[str, str, str]:
    """从 openclaw.json 读取 LLM 配置。"""
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    try:
        with open(config_path) as f:
            cfg = json.load(f)
        providers = cfg.get("models", {}).get("providers", {})
        # 优先找 mininglamp provider
        for pname, pcfg in providers.items():
            base_url = pcfg.get("baseUrl", "")
            api_key = pcfg.get("apiKey", "")
            models = pcfg.get("models", [])
            # 找轻量模型（优先 flash/mini/haiku）
            light_models = [m["id"] for m in models 
                          if any(kw in m["id"].lower() for kw in ["flash", "mini", "haiku"])]
            model_id = light_models[0] if light_models else (models[0]["id"] if models else "")
            if base_url and api_key:
                return base_url, api_key, model_id
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    return "", "", ""


def check_with_llm(expected_items: list[str], verdict: str,
                   base_url: str, api_key: str, model: str) -> dict:
    """使用 LLM 做语义判定（Anthropic Messages API 格式）。"""
    
    items_text = "\n".join(f"  {i+1}. {item}" for i, item in enumerate(expected_items))
    
    prompt = f"""你是一个测试验收判定器。给定一组"期望结果"和一段"实际观测与结论"，逐条判断每条期望结果是否被实际观测覆盖。

期望结果：
{items_text}

实际观测与结论：
{verdict}

请严格按以下 JSON 格式输出，不要输出任何其他内容（不要用 markdown 代码块包裹）：
{{"items": [{{"index": 1, "expected": "期望结果原文", "covered": true, "reason": "判定理由（一句话）"}}]}}

判定规则：
- covered=true：实际观测中有明确证据表明该期望结果已被验证且通过
- covered=false：实际观测中缺少该期望结果的验证证据，或证据显示未通过
- 语义等价视为覆盖（如"同步更新"等价于"实时刷新"）
- 部分覆盖视为 false"""

    # 构造 Anthropic Messages API 请求
    payload = {
        "model": model,
        "max_tokens": 2048,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    url = f"{base_url.rstrip('/')}/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        
        # 提取文本内容
        content = ""
        for block in result.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")
        
        if not content:
            return {"error": "LLM returned empty content"}
        
        # 解析 JSON
        return _parse_llm_json(content)
        
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        return {"error": f"HTTP {e.code}: {body}"}
    except urllib.error.URLError as e:
        return {"error": f"URL error: {e.reason}"}
    except Exception as e:
        return {"error": f"LLM call failed: {str(e)}"}


def _parse_llm_json(text: str) -> dict:
    """从 LLM 输出中提取 JSON，包含截断修复。"""
    text = text.strip()
    
    # 尝试去除 markdown 代码块
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1).strip()
    
    # 直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 找 { 到 } 的范围
    brace_start = text.find('{')
    brace_end = text.rfind('}')
    if brace_start >= 0 and brace_end > brace_start:
        candidate = text[brace_start:brace_end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        
        # 尝试截断修复：如果 items 数组被截断，补全它
        # 找到最后一个完整的 item 对象
        last_complete = candidate.rfind('}')
        if last_complete > 0:
            # 往前找到 items 数组的开始
            items_start = candidate.find('"items"')
            if items_start >= 0:
                # 尝试截取到最后一个完整 item 并补全
                truncated = candidate[:last_complete + 1]
                # 补全缺失的括号
                open_brackets = truncated.count('[') - truncated.count(']')
                open_braces = truncated.count('{') - truncated.count('}')
                repair = truncated + ']' * open_brackets + '}' * open_braces
                try:
                    return json.loads(repair)
                except json.JSONDecodeError:
                    pass
    
    return {"error": f"Cannot parse LLM output: {text[:200]}"}


def check_with_ngram(expected_items: list[str], verdict: str) -> dict:
    """n-gram fallback（原有逻辑）。"""
    results = []
    
    for i, item in enumerate(expected_items):
        hit = False
        
        # 方法1：直接子串匹配（4-8 字符片段）
        fragments = re.split(r'[，。；：、！？\s]+', item)
        for f in fragments:
            if 4 <= len(f) <= 8 and f in verdict:
                hit = True
                break
        
        # 方法2：中文 n-gram 匹配，40% 阈值
        if not hit:
            raw_phrases = re.findall(r'[\u4e00-\u9fff]+', item)
            ngrams = set()
            for rp in raw_phrases:
                for n in [3, 2]:
                    for j in range(len(rp) - n + 1):
                        ngrams.add(rp[j:j + n])
            if ngrams:
                m = sum(1 for ng in ngrams if ng in verdict)
                if m / len(ngrams) >= 0.40:
                    hit = True
        
        results.append({
            "index": i + 1,
            "expected": item,
            "covered": hit,
            "reason": "n-gram match" if hit else "n-gram: below threshold"
        })
    
    return {"items": results}


def main():
    parser = argparse.ArgumentParser(description="verdict cross-check")
    parser.add_argument("--expected-result", required=True)
    parser.add_argument("--verdict-file", required=True)
    parser.add_argument("--method", default="llm", choices=["llm", "ngram"])
    args = parser.parse_args()
    
    with open(args.verdict_file) as f:
        verdict = f.read()
    
    expected_items = parse_expected_items(args.expected_result)
    
    if not expected_items:
        print(json.dumps({"error": "No items", "items": [], "matched": 0, "total": 0},
                         ensure_ascii=False))
        sys.exit(1)
    
    if args.method == "llm":
        # 读取配置
        base_url = os.environ.get("VERDICT_LLM_BASE_URL", "")
        api_key = os.environ.get("VERDICT_LLM_API_KEY", "")
        model = os.environ.get("VERDICT_LLM_MODEL", "")
        
        if not base_url or not api_key:
            base_url_cfg, api_key_cfg, model_cfg = load_openclaw_config()
            base_url = base_url or base_url_cfg
            api_key = api_key or api_key_cfg
            model = model or model_cfg
        
        if not model:
            model = "gemini-3-flash-preview"
        
        if base_url and api_key:
            result = check_with_llm(expected_items, verdict, base_url, api_key, model)
            if "error" in result:
                print(f"[WARNING] LLM failed: {result['error']}. Falling back to n-gram.",
                      file=sys.stderr)
                result = check_with_ngram(expected_items, verdict)
                result["method"] = "ngram_fallback"
            else:
                result["method"] = f"llm_{model}"
        else:
            print("[WARNING] No LLM API configured. Using n-gram fallback.", file=sys.stderr)
            result = check_with_ngram(expected_items, verdict)
            result["method"] = "ngram_fallback"
    else:
        result = check_with_ngram(expected_items, verdict)
        result["method"] = "ngram"
    
    # 统计
    items = result.get("items", [])
    matched = sum(1 for item in items if item.get("covered", False))
    total = len(items)
    result["matched"] = matched
    result["total"] = total
    result["unmatched"] = [item["expected"] for item in items if not item.get("covered", False)]
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
