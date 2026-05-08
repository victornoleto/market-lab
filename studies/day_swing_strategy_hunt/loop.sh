#!/usr/bin/env bash
# Day/Swing Strategy Hunt — automatic loop orchestrator.
#
# Each iteration invokes a fresh agent CLI process and uses next_prompt.md as the
# single source of truth for what the next session must do. The default backend
# is opencode with GPT-5.5. The loop never commits or pushes; the per-iteration
# prompt also repeats that guardrail.
#
# Usage:
#   bash studies/day_swing_strategy_hunt/loop.sh
#   MAX_ITER=10 bash studies/day_swing_strategy_hunt/loop.sh
#   DRY_RUN=1 bash studies/day_swing_strategy_hunt/loop.sh
#
# Env vars:
#   MAX_ITER        (default 5)      hard cap on iterations in this run
#   ITER_TIMEOUT    (default 7200)   seconds per iteration
#   COOLDOWN        (default 30)     seconds between iterations
#   BACKEND         (default opencode) opencode | claude | codex
#   OPENCODE_MODEL  (default openai/gpt-5.5)
#   CLAUDE_MODEL    (default opus)   used only with BACKEND=claude
#   CODEX_MODEL     (default gpt-5.1) used only with BACKEND=codex
#   CODEX_EXTRA_FLAGS (default "")   extra flags for codex exec
#   SUCCESS_SCORE   (default 80)     minimum score if RESULTS.json has score
#   DRY_RUN         (default "")     print the prompt/command and exit
#
# Success definition:
#   - latest RESULTS.json has status positive or winner;
#   - no gate has value FAIL;
#   - kill_switches is empty;
#   - if a numeric score field exists, score >= SUCCESS_SCORE.
#
# This intentionally treats a merely positive data-audit as insufficient when it
# has no strategy_results. Strategy iterations must leave evidence in
# RESULTS.json; paper/live remains forbidden.

set -euo pipefail

cd "$(dirname "$0")/../.."

: "${MAX_ITER:=5}"
: "${ITER_TIMEOUT:=7200}"
: "${COOLDOWN:=30}"
: "${BACKEND:=opencode}"
: "${OPENCODE_MODEL:=openai/gpt-5.5}"
: "${CLAUDE_MODEL:=opus}"
: "${CODEX_MODEL:=gpt-5.1}"
: "${CODEX_EXTRA_FLAGS:=}"
: "${SUCCESS_SCORE:=80}"
: "${DRY_RUN:=}"

LOOP_DIR="studies/day_swing_strategy_hunt"
ITER_BASE_DIR="$LOOP_DIR/iterations"
PROMPT_FILE="$LOOP_DIR/next_prompt.md"
MEMORY_FILE="$LOOP_DIR/MEMORY.md"
SPEC_FILE="$LOOP_DIR/SPEC.md"
PROTOCOL_FILE="$LOOP_DIR/LOOP_PROTOCOL.md"
LOG_DIR="logs/day_swing_strategy_hunt"
RUN_LOG="$LOG_DIR/loop_$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$ITER_BASE_DIR" "$LOG_DIR"

for f in "CLAUDE.md" "jornada/README.md" "$PROMPT_FILE" "$MEMORY_FILE" "$SPEC_FILE" "$PROTOCOL_FILE"; do
    [[ -f "$f" ]] || { echo "FATAL: missing $f" >&2; exit 1; }
done

if [[ -z "$DRY_RUN" ]]; then
    case "$BACKEND" in
        opencode) command -v opencode >/dev/null || { echo "FATAL: opencode CLI not in PATH" >&2; exit 1; } ;;
        claude) command -v claude >/dev/null || { echo "FATAL: claude CLI not in PATH" >&2; exit 1; } ;;
        codex) command -v codex >/dev/null || { echo "FATAL: codex CLI not in PATH" >&2; exit 1; } ;;
        *) echo "FATAL: unsupported BACKEND=$BACKEND (use opencode|claude|codex)" >&2; exit 1 ;;
    esac
    command -v timeout >/dev/null || { echo "FATAL: GNU timeout missing" >&2; exit 1; }
fi

latest_iteration_dir() {
    local latest
    latest=$(ls "$ITER_BASE_DIR" 2>/dev/null | grep -E '^[0-9]{3}-' | sort -n | tail -1 || true)
    [[ -n "$latest" ]] && printf '%s/%s\n' "$ITER_BASE_DIR" "$latest"
}

next_iteration_number() {
    local latest dir_name n
    latest=$(latest_iteration_dir || true)
    if [[ -z "$latest" ]]; then
        printf '001\n'
        return
    fi
    dir_name=$(basename "$latest")
    n=${dir_name%%-*}
    printf '%03d\n' $((10#$n + 1))
}

latest_results_path() {
    local latest
    latest=$(latest_iteration_dir || true)
    if [[ -n "$latest" && -f "$latest/RESULTS.json" ]]; then
        printf '%s/RESULTS.json\n' "$latest"
    fi
}

success_probe() {
    local results_path
    results_path=$(latest_results_path || true)
    if [[ -z "$results_path" ]]; then
        return 1
    fi

    SUCCESS_SCORE="$SUCCESS_SCORE" uv run python - "$results_path" <<'PY'
import json
import os
import sys

path = sys.argv[1]
score_floor = float(os.environ["SUCCESS_SCORE"])
data = json.loads(open(path, encoding="utf-8").read())

status = str(data.get("status", "")).lower()
gates = data.get("gates") or {}
kill_switches = data.get("kill_switches") or []
strategy_results = data.get("strategy_results") or {}
score = data.get("score")
if score is None and isinstance(data.get("summary"), dict):
    score = data["summary"].get("score")

gate_fail = False
if isinstance(gates, dict):
    for value in gates.values():
        if str(value).upper() == "FAIL":
            gate_fail = True
            break

has_strategy = bool(strategy_results)
score_ok = True if score is None else float(score) >= score_floor
success = status in {"positive", "winner"} and has_strategy and not gate_fail and not kill_switches and score_ok

print(json.dumps({
    "success": success,
    "status": status,
    "score": score,
    "score_floor": score_floor,
    "has_strategy_results": has_strategy,
    "gate_fail": gate_fail,
    "kill_switches": kill_switches,
    "results_path": path,
}, sort_keys=True))
sys.exit(0 if success else 1)
PY
}

build_prompt() {
    local next_n="$1"
    local prompt_body
    prompt_body=$(cat "$PROMPT_FILE")
    cat <<EOF
Estamos no repo /var/www/pessoal/ai-trade, branch day_swing_strategy_hunt.

Esta e uma execucao automatica do loop, rodada para a iteracao ${next_n}, em uma sessao zerada. Siga exatamente o arquivo studies/day_swing_strategy_hunt/next_prompt.md abaixo. Nao espere resposta do usuario no meio da iteracao: se houver decisao ambigua, escolha a opcao mais conservadora que preserve os guardrails e registre no SUMMARY.md.

Guardrails adicionais do orquestrador:
- Nao fazer paper/live.
- Nao mexer em docs/investment-mandate.md.
- Nao mexer em frozen_rules/.
- Nao usar HappyForex como dataset de treino.
- Nao usar selecao ex-post por PnL.
- Nao aceitar single-asset winner.
- Nao otimizar threshold apos ver resultado.
- Nao fazer commit/push.
- Ao final, garanta RESULTS.json e SUMMARY.md da iteracao e encerre.

--- next_prompt.md ---

${prompt_body}
EOF
}

echo "=== day_swing_strategy_hunt loop @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
echo "MAX_ITER=$MAX_ITER ITER_TIMEOUT=${ITER_TIMEOUT}s COOLDOWN=${COOLDOWN}s BACKEND=$BACKEND OPENCODE_MODEL=$OPENCODE_MODEL CLAUDE_MODEL=$CLAUDE_MODEL CODEX_MODEL=$CODEX_MODEL SUCCESS_SCORE=$SUCCESS_SCORE" | tee -a "$RUN_LOG"
echo "Loop log: $RUN_LOG" | tee -a "$RUN_LOG"

set +e
probe_output=$(success_probe 2>/dev/null)
probe_status=$?
set -e
if [[ "$probe_status" -eq 0 ]]; then
    echo "=== latest iteration already meets success condition ===" | tee -a "$RUN_LOG"
    echo "$probe_output" | tee -a "$RUN_LOG"
    exit 0
fi

if [[ -n "$DRY_RUN" ]]; then
    NEXT_N=$(next_iteration_number)
    echo "=== DRY_RUN: next iteration would be $NEXT_N ===" | tee -a "$RUN_LOG"
    echo "=== prompt that would be sent to a fresh $BACKEND process: ===" | tee -a "$RUN_LOG"
    build_prompt "$NEXT_N" | tee -a "$RUN_LOG"
    exit 0
fi

for round in $(seq 1 "$MAX_ITER"); do
    NEXT_N=$(next_iteration_number)
    STAMP=$(date +%Y%m%d-%H%M%S)
    ITER_LOG="$LOG_DIR/iter_${NEXT_N}_${STAMP}.log"

    echo "--- round $round/$MAX_ITER -> iteration $NEXT_N (log=$ITER_LOG) @ $(date -Iseconds) ---" | tee -a "$RUN_LOG"
    PROMPT=$(build_prompt "$NEXT_N")

    set +e
    case "$BACKEND" in
        opencode)
            timeout "$ITER_TIMEOUT" opencode run \
                --model "$OPENCODE_MODEL" \
                --dir "$PWD" \
                --dangerously-skip-permissions \
                "$PROMPT" 2>&1 | tee -a "$ITER_LOG"
            ;;
        claude)
            timeout "$ITER_TIMEOUT" claude \
                --model "$CLAUDE_MODEL" \
                --dangerously-skip-permissions \
                --print "$PROMPT" 2>&1 | tee -a "$ITER_LOG"
            ;;
        codex)
            # shellcheck disable=SC2086
            timeout "$ITER_TIMEOUT" codex exec \
                -m "$CODEX_MODEL" \
                --full-auto \
                $CODEX_EXTRA_FLAGS \
                "$PROMPT" 2>&1 | tee -a "$ITER_LOG"
            ;;
    esac
    EXIT=${PIPESTATUS[0]}
    set -e

    if [[ "$EXIT" -eq 124 ]]; then
        echo "=== iteration $NEXT_N timed out after ${ITER_TIMEOUT}s; aborting loop ===" | tee -a "$RUN_LOG"
        exit 124
    fi
    if [[ "$EXIT" -ne 0 ]]; then
        echo "=== iteration $NEXT_N exited with code=$EXIT; aborting loop ===" | tee -a "$RUN_LOG"
        exit "$EXIT"
    fi

    set +e
    probe_output=$(success_probe 2>&1)
    probe_status=$?
    set -e
    echo "--- success probe after iteration $NEXT_N: $probe_output ---" | tee -a "$RUN_LOG"
    if [[ "$probe_status" -eq 0 ]]; then
        echo "=== success condition met at iteration $NEXT_N; stopping loop ===" | tee -a "$RUN_LOG"
        exit 0
    fi

    if [[ "$round" -lt "$MAX_ITER" ]]; then
        echo "--- cooldown ${COOLDOWN}s before next fresh session ---" | tee -a "$RUN_LOG"
        sleep "$COOLDOWN"
    fi
done

echo "=== reached MAX_ITER=$MAX_ITER without success @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
exit 0
