# test-exec.sh — mano-cua Wrapper

> VLA-T015 | 强制执行测试规范的 mano-cua 入口脚本

## 解决的问题

Phase 0 复盘发现三个反复出现的问题：

1. 86% 的 session 没有设置 `--expected-result`，判定靠自由发挥
2. observation 与 verdict 有时逻辑矛盾，无机制自动发现
3. verdict 与 expected-result 不一致时直接进了报告

本脚本在执行入口处自动 enforce 这三条规则。

## 用法

```bash
# 基本用法
./scripts/test-exec.sh \
  --task "在当前页面中..." \
  --expected-result "1. 条件A；2. 条件B；3. 条件C" \
  --test-id L2.5 \
  --log-dir ./trajectories/golden \
  --minimize

# dry-run（仅校验参数，不执行 mano-cua）
./scripts/test-exec.sh \
  --task "..." \
  --expected-result "..." \
  --test-id L2.5 \
  --dry-run
```

## 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--task` | 是 | mano-cua 任务描述 |
| `--expected-result` | 是 | 期望结果（分号分隔多条） |
| `--test-id` | 否 | 测试点 ID（影响日志文件名） |
| `--log-dir` | 否 | 日志输出目录（默认 `./trajectories`） |
| `--minimize` | 否 | 传递给 mano-cua 的 `--minimize` |
| `--dry-run` | 否 | 仅校验参数，不执行 |

## 三条规则

### 规则 1：强制 expected-result

不带 `--expected-result` 直接 exit 1，拒绝执行。

```
[BLOCKED] --expected-result 未设置，拒绝执行。
```

### 规则 2：observation 与 verdict 一致性检查

执行完成后扫描所有 reasoning 步骤中的负面关键词（"失败"、"错误"、"未渲染"等）：

- 过程中有负面观测但最终 verdict 全正面 → 标红 WARNING
- verdict 同时包含正面和负面关键词 → 标红 WARNING（自相矛盾）

### 规则 3：verdict 与 expected-result 交叉校验

将 expected-result 拆分为逐条，用中文 n-gram 匹配检查 verdict 是否覆盖了每一条：

- 全部覆盖 → AUTO_PASS
- 部分未覆盖 → REVIEW_REQUIRED（不自动 PASS，需人工复核）

## 输出

### 终端输出

带颜色的结构化报告：

```
[OK] observation 与 verdict 逻辑一致。
[REVIEW_REQUIRED] verdict 与 expected-result 交叉校验不完全
  匹配: 2/3
  未匹配项:
    → 预览区的更新内容与编辑区修改一致

[RESULT] 综合判定
  ● REVIEW_REQUIRED — 需人工复核
```

### JSON 报告

每次执行生成 `<test-id>_<timestamp>_report.json`：

```json
{
  "test_id": "L1.2",
  "status": "COMPLETED",
  "total_steps": 7,
  "checks": {
    "expected_result_present": true,
    "consistency": "PASS",
    "cross_check": "REVIEW_REQUIRED",
    "er_matched": 2,
    "er_total": 3
  },
  "final_verdict": "REVIEW_REQUIRED"
}
```

### 综合判定

| 判定 | 条件 |
|------|------|
| AUTO_PASS | 一致性 PASS + 交叉校验全部覆盖 |
| REVIEW_REQUIRED | 一致性 WARNING 或交叉校验不完全 |
| INCOMPLETE | mano-cua Status 非 COMPLETED |

## 依赖

- bash 4+（macOS 可用 `brew install bash`）
- python3
- mano-cua（已安装在 PATH 中）

## 注意

- macOS 默认 shell 为 zsh，本脚本需用 `bash` 执行（shebang 已配置）
- 交叉校验使用 n-gram 模糊匹配，阈值 40%，低于阈值触发 REVIEW 而非 FAIL
