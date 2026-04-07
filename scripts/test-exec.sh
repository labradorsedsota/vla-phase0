#!/bin/bash
# =============================================================================
# test-exec.sh — mano-cua wrapper（VLA-T015）
#
# 职责：
#   1. 强制要求 --expected-result，缺失则 exit 1
#   2. 执行 mano-cua run，捕获输出
#   3. 解析输出，提取 observation / verdict
#   4. observation 与 verdict 逻辑一致性检查（矛盾标红）
#   5. verdict 与 expected-result 交叉校验（不一致标记人工复核）
#   6. 输出结构化结果 JSON
#
# 用法：
#   ./test-exec.sh --task "任务描述" \
#                  --expected-result "期望结果" \
#                  --log-dir ./trajectories \
#                  --test-id L2.5 \
#                  [--url "file:///path/to/app.html"] \
#                  [--minimize] \
#                  [--dry-run]
#
# 产出标准：
#   - 不带 --expected-result → exit 1，100% 拦截
#   - observation 与 verdict 矛盾 → 标红 WARNING
#   - verdict 与 expected-result 不一致 → 标记 REVIEW_REQUIRED
#   - 输出结构化 JSON 报告
# =============================================================================

set -eo pipefail

# ── 颜色定义 ──
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ── 参数解析 ──
TASK=""
EXPECTED_RESULT=""
LOG_DIR=""
TEST_ID=""
URL=""
MINIMIZE=false
DRY_RUN=false
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --task)         TASK="$2";            shift 2 ;;
    --expected-result) EXPECTED_RESULT="$2"; shift 2 ;;
    --log-dir)      LOG_DIR="$2";         shift 2 ;;
    --test-id)      TEST_ID="$2";         shift 2 ;;
    --url)          URL="$2";             shift 2 ;;
    --minimize)     MINIMIZE=true;        shift ;;
    --dry-run)      DRY_RUN=true;         shift ;;
    *)              EXTRA_ARGS+=("$1");   shift ;;
  esac
done

# ── 规则 1：强制 --expected-result ──
if [[ -z "$EXPECTED_RESULT" ]]; then
  echo -e "${RED}${BOLD}[BLOCKED] --expected-result 未设置，拒绝执行。${NC}"
  echo -e "${RED}所有 mano-cua 测试必须提供 expected-result（执行规范条款 9）。${NC}"
  echo -e "${RED}用法：$0 --task \"...\" --expected-result \"...\" --test-id L2.5${NC}"
  exit 1
fi

if [[ -z "$TASK" ]]; then
  echo -e "${RED}${BOLD}[BLOCKED] --task 未设置，拒绝执行。${NC}"
  exit 1
fi

if [[ -z "$TEST_ID" ]]; then
  echo -e "${YELLOW}[WARNING] --test-id 未设置，日志文件名将使用时间戳。${NC}"
  TEST_ID="unknown-$(date +%H%M%S)"
fi

# ── 准备日志路径 ──
if [[ -z "$LOG_DIR" ]]; then
  LOG_DIR="./trajectories"
fi
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="${LOG_DIR}/${TEST_ID}_${TIMESTAMP}.log"
REPORT_FILE="${LOG_DIR}/${TEST_ID}_${TIMESTAMP}_report.json"

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}test-exec.sh — mano-cua wrapper${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Test ID:         ${BOLD}${TEST_ID}${NC}"
echo -e "Expected Result: ${EXPECTED_RESULT}"
echo -e "Log File:        ${LOG_FILE}"
echo -e "Report File:     ${REPORT_FILE}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ── dry-run 模式 ──
if [[ "$DRY_RUN" == "true" ]]; then
  echo -e "${YELLOW}[DRY-RUN] 仅验证参数，不执行 mano-cua。${NC}"
  echo -e "${GREEN}[OK] 参数校验通过。${NC}"
  # 输出空报告
  cat > "$REPORT_FILE" <<EOF
{
  "test_id": "${TEST_ID}",
  "mode": "dry-run",
  "expected_result": $(echo "$EXPECTED_RESULT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))"),
  "task": $(echo "$TASK" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))"),
  "status": "DRY_RUN",
  "checks": {
    "expected_result_present": true
  }
}
EOF
  echo -e "Report: ${REPORT_FILE}"
  exit 0
fi

# ── 执行 mano-cua ──
echo -e "\n${BOLD}[EXEC] 启动 mano-cua...${NC}"

MANO_CMD=(mano-cua run "$TASK" --expected-result "$EXPECTED_RESULT")
if [[ "$MINIMIZE" == "true" ]]; then
  MANO_CMD+=(--minimize)
fi
if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
  MANO_CMD+=("${EXTRA_ARGS[@]}")
fi

# 使用 PYTHONUNBUFFERED 确保实时输出
MANO_EXIT_CODE=0
PYTHONUNBUFFERED=1 "${MANO_CMD[@]}" 2>&1 | tee "$LOG_FILE" || MANO_EXIT_CODE=$?

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}[ANALYSIS] 解析 mano-cua 输出...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ── 解析输出 ──
# 提取 Status
STATUS=$(grep -m1 "^Status:" "$LOG_FILE" | sed 's/^Status: //' || echo "UNKNOWN")

# 提取 Total steps
TOTAL_STEPS=$(grep -m1 "^Total steps:" "$LOG_FILE" | sed 's/^Total steps: //' || echo "0")

# 提取 Last reasoning（observation + verdict 合一）
# mano-cua 的 Last reasoning 包含最终步的完整 reasoning，其中包含观测事实和结论
LAST_REASONING=$(sed -n '/^Last reasoning:/,/^={10,}/p' "$LOG_FILE" | sed '$d' | sed '1s/^Last reasoning: //')

# 提取所有 reasoning 步骤中的负面关键词
NEGATIVE_KEYWORDS="未渲染|raw text|NOT proper|failed|error|失败|不正确|无法|乱码|缺失|missing|broken|garbled|not found|not displayed|not rendered|not visible|incorrect|wrong"
NEGATIVE_OBSERVATIONS=$(grep -i "Reasoning:" "$LOG_FILE" | grep -iE "$NEGATIVE_KEYWORDS" || true)
NEGATIVE_COUNT=$(echo "$NEGATIVE_OBSERVATIONS" | grep -c . 2>/dev/null || echo "0")
if [[ -z "$NEGATIVE_OBSERVATIONS" ]]; then
  NEGATIVE_COUNT=0
fi

# 提取 verdict（从 Last reasoning 中判断正/负面结论）
POSITIVE_VERDICT_KEYWORDS="成功|✅|PASS|pass|correct|properly|正确|完成|符合|satisfied|working|正常"
NEGATIVE_VERDICT_KEYWORDS="失败|❌|FAIL|fail|incorrect|错误|不正确|未通过|not working|broken"

HAS_POSITIVE_VERDICT=false
HAS_NEGATIVE_VERDICT=false

if echo "$LAST_REASONING" | grep -qiE "$POSITIVE_VERDICT_KEYWORDS"; then
  HAS_POSITIVE_VERDICT=true
fi
if echo "$LAST_REASONING" | grep -qiE "$NEGATIVE_VERDICT_KEYWORDS"; then
  HAS_NEGATIVE_VERDICT=true
fi

# ── 规则 2：observation 与 verdict 逻辑一致性检查 ──
CONSISTENCY_CHECK="PASS"
CONSISTENCY_DETAIL=""

# 情况 1：过程中有负面观测，但最终 verdict 全正面
if [[ $NEGATIVE_COUNT -gt 0 ]] && [[ "$HAS_POSITIVE_VERDICT" == "true" ]] && [[ "$HAS_NEGATIVE_VERDICT" == "false" ]]; then
  CONSISTENCY_CHECK="WARNING"
  CONSISTENCY_DETAIL="过程中存在 ${NEGATIVE_COUNT} 条负面观测，但最终 verdict 为正面。需人工确认负面观测是否已被解决。"
  echo -e "${RED}${BOLD}[WARNING] observation 与 verdict 可能矛盾${NC}"
  echo -e "${RED}  负面观测数: ${NEGATIVE_COUNT}${NC}"
  echo -e "${RED}  最终 verdict: 正面${NC}"
  echo -e "${RED}  ${CONSISTENCY_DETAIL}${NC}"
  if [[ -n "$NEGATIVE_OBSERVATIONS" ]]; then
    echo -e "${RED}  负面观测摘录:${NC}"
    echo "$NEGATIVE_OBSERVATIONS" | head -5 | while IFS= read -r line; do
      echo -e "${RED}    → ${line}${NC}"
    done
  fi
fi

# 情况 2：verdict 同时包含正面和负面关键词
if [[ "$HAS_POSITIVE_VERDICT" == "true" ]] && [[ "$HAS_NEGATIVE_VERDICT" == "true" ]]; then
  CONSISTENCY_CHECK="WARNING"
  CONSISTENCY_DETAIL="verdict 中同时包含正面和负面关键词，判定自相矛盾。"
  echo -e "${RED}${BOLD}[WARNING] verdict 内部矛盾${NC}"
  echo -e "${RED}  ${CONSISTENCY_DETAIL}${NC}"
fi

if [[ "$CONSISTENCY_CHECK" == "PASS" ]]; then
  echo -e "${GREEN}[OK] observation 与 verdict 逻辑一致。${NC}"
fi

# ── 规则 3：verdict 与 expected-result 交叉校验（LLM 语义判定） ──
CROSS_CHECK="PASS"
CROSS_DETAIL=""

# 将 LAST_REASONING 写入临时文件
REASONING_TMPFILE=$(mktemp)
echo "$LAST_REASONING" > "$REASONING_TMPFILE"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 调用 verdict_check.py（LLM 优先，自动 fallback 到 n-gram）
CROSS_RESULT=$(python3 "${SCRIPT_DIR}/verdict_check.py" \
  --expected-result "$EXPECTED_RESULT" \
  --verdict-file "$REASONING_TMPFILE" \
  --method llm 2>/dev/null)

CROSS_METHOD=$(echo "$CROSS_RESULT" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('method','unknown'))" 2>/dev/null || echo "unknown")
ER_MATCHED=$(echo "$CROSS_RESULT" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('matched',0))" 2>/dev/null || echo "0")
ER_TOTAL=$(echo "$CROSS_RESULT" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('total',0))" 2>/dev/null || echo "0")

# 提取未匹配项
ER_UNMATCHED=()
while IFS= read -r line; do
  [[ -n "$line" ]] && ER_UNMATCHED+=("$line")
done < <(echo "$CROSS_RESULT" | python3 -c "import sys,json; [print(u) for u in json.loads(sys.stdin.read()).get('unmatched',[])]" 2>/dev/null)

# 提取每条的判定理由（用于报告）
CROSS_ITEMS_JSON=$(echo "$CROSS_RESULT" | python3 -c "import sys,json; print(json.dumps(json.loads(sys.stdin.read()).get('items',[]),ensure_ascii=False))" 2>/dev/null || echo "[]")

rm -f "$REASONING_TMPFILE"

echo -e "  Cross-check method: ${BOLD}${CROSS_METHOD}${NC}"

if [[ ${#ER_UNMATCHED[@]} -gt 0 ]]; then
  CROSS_CHECK="REVIEW_REQUIRED"
  CROSS_DETAIL="expected-result 中 ${#ER_UNMATCHED[@]}/${ER_TOTAL} 条未在 verdict 中得到明确回应。"
  echo -e "${YELLOW}${BOLD}[REVIEW_REQUIRED] verdict 与 expected-result 交叉校验不完全${NC}"
  echo -e "${YELLOW}  匹配: ${ER_MATCHED}/${ER_TOTAL}${NC}"
  echo -e "${YELLOW}  未匹配项:${NC}"
  for u in "${ER_UNMATCHED[@]}"; do
    echo -e "${YELLOW}    → ${u}${NC}"
  done
else
  echo -e "${GREEN}[OK] verdict 覆盖了全部 expected-result 条目 (${ER_MATCHED}/${ER_TOTAL})。${NC}"
fi

# ── 综合判定 ──
FINAL_VERDICT="AUTO_PASS"
if [[ "$CONSISTENCY_CHECK" == "WARNING" ]] || [[ "$CROSS_CHECK" == "REVIEW_REQUIRED" ]]; then
  FINAL_VERDICT="REVIEW_REQUIRED"
fi
if [[ "$STATUS" != "COMPLETED" ]]; then
  FINAL_VERDICT="INCOMPLETE"
fi

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}[RESULT] 综合判定${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

case $FINAL_VERDICT in
  AUTO_PASS)
    echo -e "${GREEN}${BOLD}  ● AUTO_PASS — 可自动通过${NC}" ;;
  REVIEW_REQUIRED)
    echo -e "${YELLOW}${BOLD}  ● REVIEW_REQUIRED — 需人工复核${NC}" ;;
  INCOMPLETE)
    echo -e "${RED}${BOLD}  ● INCOMPLETE — 执行未完成${NC}" ;;
esac

echo -e "  Status:            ${STATUS}"
echo -e "  Steps:             ${TOTAL_STEPS}"
echo -e "  Consistency:       ${CONSISTENCY_CHECK}"
echo -e "  Cross-check:       ${CROSS_CHECK}"
echo -e "  Final:             ${FINAL_VERDICT}"

# ── 输出结构化 JSON 报告 ──
python3 -c "
import json, sys

report = {
    'test_id': '${TEST_ID}',
    'timestamp': '${TIMESTAMP}',
    'status': '${STATUS}',
    'total_steps': int('${TOTAL_STEPS}' or '0'),
    'mano_exit_code': ${MANO_EXIT_CODE},
    'expected_result': $(echo "$EXPECTED_RESULT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))"),
    'task': $(echo "$TASK" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))"),
    'observation': {
        'negative_count': ${NEGATIVE_COUNT},
        'has_positive_verdict': $( [[ "$HAS_POSITIVE_VERDICT" == "true" ]] && echo "True" || echo "False" ),
        'has_negative_verdict': $( [[ "$HAS_NEGATIVE_VERDICT" == "true" ]] && echo "True" || echo "False" ),
    },
    'checks': {
        'expected_result_present': True,
        'consistency': '${CONSISTENCY_CHECK}',
        'consistency_detail': $(echo "$CONSISTENCY_DETAIL" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))") or None,
        'cross_check': '${CROSS_CHECK}',
        'cross_check_method': '${CROSS_METHOD}',
        'cross_check_detail': $(echo "$CROSS_DETAIL" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))") or None,
        'cross_check_items': json.loads('''${CROSS_ITEMS_JSON}''') if '''${CROSS_ITEMS_JSON}''' != '[]' else [],
        'er_matched': ${ER_MATCHED},
        'er_total': ${ER_TOTAL},
    },
    'final_verdict': '${FINAL_VERDICT}',
    'log_file': '${LOG_FILE}',
}

with open('${REPORT_FILE}', 'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(json.dumps(report, indent=2, ensure_ascii=False))
" 2>/dev/null || echo -e "${YELLOW}[WARNING] JSON 报告生成失败，回退到纯文本。${NC}"

echo -e "\n${CYAN}Log:    ${LOG_FILE}${NC}"
echo -e "${CYAN}Report: ${REPORT_FILE}${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

exit $MANO_EXIT_CODE
