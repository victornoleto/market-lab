#!/usr/bin/env bash
# success_trading_strat — autonomous clean-session loop.

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
: "${DRY_RUN:=}"
: "${STOP_ON_WINNER:=0}"
: "${LOOP_PHASE:=phase02}"

LOOP_DIR="studies/success_trading_strat"
ITER_BASE_DIR="$LOOP_DIR/iters/$LOOP_PHASE"
MEMORY_FILE="$LOOP_DIR/MEMORY.md"
PROMPT_FILE="$LOOP_DIR/LOOP_PROMPT.md"
SPEC_FILE="$LOOP_DIR/SPEC.md"
PROTOCOL_FILE="$LOOP_DIR/LOOP_PROTOCOL.md"
LOG_DIR="logs/success_trading_strat"
RUN_LOG="$LOG_DIR/loop_$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$ITER_BASE_DIR" "$LOG_DIR"

for f in "CLAUDE.md" "docs/investment-mandate.md" "$MEMORY_FILE" "$PROMPT_FILE" "$SPEC_FILE" "$PROTOCOL_FILE"; do
    [[ -f "$f" ]] || { echo "FATAL: missing $f" >&2; exit 1; }
done

if [[ -n "$(git status --porcelain -- docs/investment-mandate.md)" ]]; then
    echo "FATAL: docs/investment-mandate.md has uncommitted changes; refusing autonomous loop" >&2
    exit 1
fi

if [[ -z "$DRY_RUN" ]]; then
    case "$BACKEND" in
        opencode) command -v opencode >/dev/null || { echo "FATAL: opencode CLI not in PATH" >&2; exit 1; } ;;
        claude) command -v claude >/dev/null || { echo "FATAL: claude CLI not in PATH" >&2; exit 1; } ;;
        codex) command -v codex >/dev/null || { echo "FATAL: codex CLI not in PATH" >&2; exit 1; } ;;
        *) echo "FATAL: unsupported BACKEND=$BACKEND (use opencode|claude|codex)" >&2; exit 1 ;;
    esac
    command -v timeout >/dev/null || { echo "FATAL: GNU timeout missing" >&2; exit 1; }
fi

read_memory_key() {
    local key="$1"
    awk -v k="$key" '
        /^---$/ {f++; if (f==2) exit; next}
        f==1 && $0 ~ "^"k":" {sub("^"k": *", ""); gsub(/^ +| +$/, ""); gsub(/^"/, ""); gsub(/"$/, ""); print; exit}
    ' "$MEMORY_FILE"
}

memory_int_key() {
    local key="$1" value
    value=$(read_memory_key "$key")
    [[ "$value" =~ ^[0-9]+$ ]] || { echo "FATAL: $key missing/non-integer in $MEMORY_FILE: '$value'" >&2; exit 1; }
    printf '%s\n' "$value"
}

latest_iteration_prefix() {
    local path base n max=0
    shopt -s nullglob
    for path in "$ITER_BASE_DIR"/[0-9][0-9][0-9]-*/; do
        base=${path%/}
        base=${base##*/}
        n=${base%%-*}
        if [[ "$n" =~ ^[0-9]{3}$ ]] && ((10#$n > max)); then
            max=$((10#$n))
        fi
    done
    shopt -u nullglob
    printf '%s\n' "$max"
}

next_iteration_number() {
    local total latest next
    total=$(memory_int_key "total_iterations")
    latest=$(latest_iteration_prefix)
    next=$((total + 1))
    if (( latest >= next )); then
        next=$((latest + 1))
    fi
    printf '%03d\n' "$next"
}

latest_results_path() {
    local path base n max=0 best=""
    shopt -s nullglob
    for path in "$ITER_BASE_DIR"/[0-9][0-9][0-9]-*/; do
        base=${path%/}
        base=${base##*/}
        n=${base%%-*}
        if [[ "$n" =~ ^[0-9]{3}$ ]] && ((10#$n > max)) && [[ -f "${path}RESULTS.json" ]]; then
            max=$((10#$n))
            best="${path}RESULTS.json"
        fi
    done
    shopt -u nullglob
    [[ -n "$best" ]] && printf '%s\n' "$best"
}

success_probe() {
    local results_path
    results_path=$(latest_results_path || true)
    if [[ -z "$results_path" ]]; then
        echo '{"probe":"no_results_yet"}'
        return 1
    fi
    uv run python - "$results_path" <<'PY'
import json
import sys

path = sys.argv[1]
data = json.loads(open(path, encoding="utf-8").read())
probe = {
    "probe": "ok",
    "iteration": data.get("iteration"),
    "status": data.get("status"),
    "winner": bool(data.get("winner", False)),
    "best_config": data.get("best_config"),
}
print(json.dumps(probe, sort_keys=True))
sys.exit(0 if probe["winner"] else 1)
PY
}

build_prompt() {
    local next_n="$1" total target trials prompt_body
    total=$(memory_int_key "total_iterations")
    target=$(memory_int_key "target_total_iterations")
    trials=$(memory_int_key "cumulative_n_trials")
    prompt_body=$(cat "$PROMPT_FILE")
    cat <<EOF
Estamos no repo /var/www/github/finances/market-lab.

Execução automática do success_trading_strat, fase ${LOOP_PHASE}, iteração ${next_n}.
Estado atual: total_iterations=${total}, target_total_iterations=${target}, cumulative_n_trials=${trials}.
Diretório de artefatos desta fase: ${ITER_BASE_DIR}.

Siga exatamente o prompt abaixo. Se houver ambiguidade, escolha a opção mais
conservadora que preserve os guardrails e registre no SUMMARY.md. Não espere
resposta humana. Não faça commit/push. Pare após uma iteração.

--- LOOP_PROMPT.md ---

${prompt_body}
EOF
}

echo "=== success_trading_strat loop @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
echo "MAX_ITER=$MAX_ITER ITER_TIMEOUT=${ITER_TIMEOUT}s COOLDOWN=${COOLDOWN}s BACKEND=$BACKEND OPENCODE_MODEL=$OPENCODE_MODEL STOP_ON_WINNER=$STOP_ON_WINNER LOOP_PHASE=$LOOP_PHASE" | tee -a "$RUN_LOG"
echo "Loop log: $RUN_LOG" | tee -a "$RUN_LOG"

CURRENT_TOTAL=$(memory_int_key "total_iterations")
TARGET_TOTAL=$(memory_int_key "target_total_iterations")
STATUS=$(read_memory_key "status")
if [[ "$STOP_ON_WINNER" == "1" && "$STATUS" == "winner" ]]; then
    echo "=== status=winner; nothing to run ===" | tee -a "$RUN_LOG"
    exit 0
fi
if (( CURRENT_TOTAL >= TARGET_TOTAL )); then
    echo "=== total_iterations=$CURRENT_TOTAL reached target_total_iterations=$TARGET_TOTAL; nothing to run ===" | tee -a "$RUN_LOG"
    exit 0
fi

set +e
probe_output=$(success_probe 2>/dev/null)
set -e
echo "--- initial probe: $probe_output ---" | tee -a "$RUN_LOG"

if [[ -n "$DRY_RUN" ]]; then
    NEXT_N=$(next_iteration_number)
    echo "=== DRY_RUN: next iteration would be $NEXT_N ===" | tee -a "$RUN_LOG"
    build_prompt "$NEXT_N" | tee -a "$RUN_LOG"
    exit 0
fi

for round in $(seq 1 "$MAX_ITER"); do
    CURRENT_TOTAL=$(memory_int_key "total_iterations")
    TARGET_TOTAL=$(memory_int_key "target_total_iterations")
    STATUS=$(read_memory_key "status")
    if [[ "$STOP_ON_WINNER" == "1" && "$STATUS" == "winner" ]] || (( CURRENT_TOTAL >= TARGET_TOTAL )); then
        echo "=== stop condition reached: status=$STATUS total=$CURRENT_TOTAL target=$TARGET_TOTAL ===" | tee -a "$RUN_LOG"
        exit 0
    fi

    NEXT_N=$(next_iteration_number)
    PREV_TOTAL="$CURRENT_TOTAL"
    STAMP=$(date +%Y%m%d-%H%M%S)
    ITER_LOG="$LOG_DIR/iter_${NEXT_N}_${STAMP}.log"
    PROMPT=$(build_prompt "$NEXT_N")

    echo "--- round $round/$MAX_ITER -> iteration $NEXT_N (log=$ITER_LOG) @ $(date -Iseconds) ---" | tee -a "$RUN_LOG"

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
                -C "$PWD" \
                --dangerously-bypass-approvals-and-sandbox \
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
    set -e
    echo "--- success probe after iteration $NEXT_N: $probe_output ---" | tee -a "$RUN_LOG"

    CURRENT_TOTAL=$(memory_int_key "total_iterations")
    if (( CURRENT_TOTAL <= PREV_TOTAL )); then
        echo "=== iteration $NEXT_N did not advance MEMORY total_iterations ($PREV_TOTAL -> $CURRENT_TOTAL); aborting loop ===" | tee -a "$RUN_LOG"
        exit 1
    fi

    STATUS=$(read_memory_key "status")
    if [[ "$STOP_ON_WINNER" == "1" && "$STATUS" == "winner" ]]; then
        echo "=== winner status reached at iteration $NEXT_N; stopping ===" | tee -a "$RUN_LOG"
        exit 0
    elif [[ "$STATUS" == "winner" ]]; then
        echo "=== winner status reached at iteration $NEXT_N; continuing because STOP_ON_WINNER=0 ===" | tee -a "$RUN_LOG"
    fi

    if [[ "$round" -lt "$MAX_ITER" ]]; then
        echo "--- cooldown ${COOLDOWN}s before next fresh session ---" | tee -a "$RUN_LOG"
        sleep "$COOLDOWN"
    fi
done

echo "=== reached MAX_ITER=$MAX_ITER without halt @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
