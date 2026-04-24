#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "== healthz =="
curl -sS "${BASE_URL}/healthz"
echo
echo

echo "== run: planning =="
curl -sS -X POST "${BASE_URL}/runs" \
  -H "Content-Type: application/json" \
  -d '{"task":"请先拆解M0里程碑，并给出可执行的两周计划"}'
echo
echo

echo "== run: coding =="
curl -sS -X POST "${BASE_URL}/runs" \
  -H "Content-Type: application/json" \
  -d '{"task":"请给出实现 /runs API 的代码改造建议，并补齐测试"}'
echo
echo

echo "== run: review (fallback planner) =="
curl -sS -X POST "${BASE_URL}/runs" \
  -H "Content-Type: application/json" \
  -d '{"task":"请评审这个PR的风险并指出需要补充的测试"}'
echo
