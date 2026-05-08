#!/usr/bin/env bash
# Re-run all spy_beater_hunt iters with the current run_iter pipeline.
#
# Use this after changing pipeline-level logic (e.g. net-of-tax integration,
# scoring rubric tweaks) to regenerate verdict.json + final_report.md + plots
# for every iter using the latest code.
#
# Skips:
#   - iters whose directory has no backtest.py (e.g. 011-IMPOSSIBILITY-RESULT
#     which is a meta-iter aggregating prior verdicts).
#
# Usage:
#   PYTHONPATH=. bash studies/spy_beater_hunt/rerun_all_iters.sh
#   FILTER='015|016' PYTHONPATH=. bash studies/spy_beater_hunt/rerun_all_iters.sh
#
# Env:
#   FILTER  optional regex matched against iter dir name; only matching iters run.

set -euo pipefail

cd "$(dirname "$0")/../.."
export PYTHONPATH="${PYTHONPATH:-.}"

ITER_ROOT="studies/spy_beater_hunt/iterations"
FILTER="${FILTER:-}"

count_total=0
count_skipped=0
count_done=0
count_failed=0
failed_iters=()

for d in "$ITER_ROOT"/*/; do
  iter_name=$(basename "$d")
  count_total=$((count_total + 1))

  if [ -n "$FILTER" ] && [[ ! "$iter_name" =~ $FILTER ]]; then
    count_skipped=$((count_skipped + 1))
    continue
  fi

  if [ ! -f "${d}backtest.py" ]; then
    echo "[skip] $iter_name (no backtest.py)"
    count_skipped=$((count_skipped + 1))
    continue
  fi

  echo "===================================================================="
  echo "[run]  $iter_name"
  echo "===================================================================="
  if python3 "${d}backtest.py" > "${d}rerun.log" 2>&1; then
    echo "[ok]   $iter_name"
    count_done=$((count_done + 1))
  else
    echo "[FAIL] $iter_name (see ${d}rerun.log)"
    count_failed=$((count_failed + 1))
    failed_iters+=("$iter_name")
  fi
done

echo
echo "=== rerun summary ==="
echo "total:   $count_total"
echo "done:    $count_done"
echo "skipped: $count_skipped"
echo "failed:  $count_failed"
if [ ${#failed_iters[@]} -gt 0 ]; then
  printf '  - %s\n' "${failed_iters[@]}"
  exit 1
fi
