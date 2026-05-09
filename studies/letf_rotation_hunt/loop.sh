#!/usr/bin/env bash
# letf_rotation_hunt — post-close strategy hunt orchestrator (multi-backend).
#
# Each iteration spawns a fresh agent CLI process and uses LOOP_PROMPT.md as
# the single source of truth for what the next session must do. The default
# backend is claude (opus). The loop never commits or pushes; the per-iter
# prompt also repeats that guardrail.
#
# This is DISTINCT from the legacy run_loop.sh in this same directory, which
# is a config-driven (yaml-queue) python loop for the closed study. Do NOT
# confuse the two:
#   - run_loop.sh: queue of pre-existing configs/iter_*.yaml → run_iter.py
#                  (closed study T0-T5).
#   - loop.sh:     autonomous LLM-driven loop researching new strategies and
#                  benchmarking vs the study winner Sortino 1.3246.
#
# Usage:
#   bash studies/letf_rotation_hunt/loop.sh
#   MAX_ITER=10 bash studies/letf_rotation_hunt/loop.sh
#   BACKEND=opencode OPENCODE_MODEL=openai/gpt-5.5 bash studies/letf_rotation_hunt/loop.sh
#   DRY_RUN=1 bash studies/letf_rotation_hunt/loop.sh
#
# Env vars:
#   MAX_ITER          (default 10)        hard cap on iterations in this run
#   ITER_TIMEOUT      (default 5400)      seconds per iteration (90 min)
#   COOLDOWN          (default 30)        seconds between iterations
#   BACKEND           (default claude)    claude | opencode | codex
#   CLAUDE_MODEL      (default opus)
#   OPENCODE_MODEL    (default openai/gpt-5.5)
#   CODEX_MODEL       (default gpt-5.1)
#   CODEX_EXTRA_FLAGS (default "")
#   DRY_RUN           (default "")        if set, print prompt and exit 0
#
# Halt conditions:
#   - reached MAX_ITER iterations this run                  → exit 0
#   - reached LOOP_MEMORY target_total_iterations           → exit 0
#   - iter timed out (timeout returns 124)                  → exit 124
#   - iter agent exited with non-zero rc                    → exit <rc>
#
# beats_winner is informational only — loop continues even if a beater is
# found (per design: broad sweep over fast halt). Beaters are recorded in
# LOOP_MEMORY.md frontmatter (loop_winner_iter list).

set -euo pipefail

cd "$(dirname "$0")/../.."

: "${MAX_ITER:=10}"
: "${ITER_TIMEOUT:=5400}"
: "${COOLDOWN:=30}"
: "${BACKEND:=claude}"
: "${CLAUDE_MODEL:=opus}"
: "${OPENCODE_MODEL:=openai/gpt-5.5}"
: "${CODEX_MODEL:=gpt-5.1}"
: "${CODEX_EXTRA_FLAGS:=}"
: "${DRY_RUN:=}"

LOOP_DIR="studies/letf_rotation_hunt"
ITER_BASE_DIR="$LOOP_DIR/loop_iterations"
PROMPT_FILE="$LOOP_DIR/LOOP_PROMPT.md"
MEMORY_FILE="$LOOP_DIR/LOOP_MEMORY.md"
PROTOCOL_FILE="$LOOP_DIR/LOOP_PROTOCOL.md"
BASE_MEMORY_FILE="$LOOP_DIR/BASE_MEMORY.md"
SCHEMA_FILE="$LOOP_DIR/loop_verdict_schema.json"
LOG_DIR="logs/letf_rotation_hunt_loop"
RUN_LOG="$LOG_DIR/loop_$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$ITER_BASE_DIR" "$LOG_DIR"

# Pre-flight: required files
for f in "CLAUDE.md" "$PROMPT_FILE" "$MEMORY_FILE" "$PROTOCOL_FILE" "$BASE_MEMORY_FILE" "$SCHEMA_FILE"; do
    [[ -f "$f" ]] || { echo "FATAL: missing $f" >&2; exit 1; }
done

# Mandate guard: this loop must never run while the canonical allocation rules
# are locally modified. A beater only creates research evidence, not deployment.
if [[ -n "$(git status --porcelain -- docs/investment-mandate.md)" ]]; then
    echo "FATAL: docs/investment-mandate.md has uncommitted changes; refusing autonomous loop run" >&2
    exit 1
fi

# Pre-flight: backend CLI + GNU timeout (skip CLI check if DRY_RUN)
if [[ -z "$DRY_RUN" ]]; then
    case "$BACKEND" in
        claude)   command -v claude   >/dev/null || { echo "FATAL: claude CLI not in PATH"   >&2; exit 1; } ;;
        opencode) command -v opencode >/dev/null || { echo "FATAL: opencode CLI not in PATH" >&2; exit 1; } ;;
        codex)    command -v codex    >/dev/null || { echo "FATAL: codex CLI not in PATH"    >&2; exit 1; } ;;
        *) echo "FATAL: unsupported BACKEND=$BACKEND (use claude|opencode|codex)" >&2; exit 1 ;;
    esac
    command -v timeout >/dev/null || { echo "FATAL: GNU timeout missing" >&2; exit 1; }
fi

# Helpers
read_memory_key() {
    # Extract a key from the YAML frontmatter (between the first two `---` lines)
    # Usage: read_memory_key <file> <key>
    local file="$1" key="$2"
    awk -v k="$key" '
        /^---$/ {f++; if (f==2) exit; next}
        f==1 && $0 ~ "^"k":" {sub("^"k": *", ""); gsub(/^ +| +$/, ""); gsub(/^"|"$/, ""); print; exit}
    ' "$file"
}

memory_int_key() {
    local file="$1" key="$2" value
    value=$(read_memory_key "$file" "$key")
    [[ "$value" =~ ^[0-9]+$ ]] || { echo "FATAL: $key missing or non-integer in $file: '$value'" >&2; exit 1; }
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
    local total next latest_prefix
    total=$(memory_int_key "$MEMORY_FILE" "total_iterations")
    next=$((total + 1))
    latest_prefix=$(latest_iteration_prefix)
    if (( latest_prefix >= next )); then
        next=$((latest_prefix + 1))
    fi
    printf '%03d\n' "$next"
}

latest_verdict_path() {
    local path base best_path="" n max=0
    shopt -s nullglob
    for path in "$ITER_BASE_DIR"/[0-9][0-9][0-9]-*/; do
        base=${path%/}
        base=${base##*/}
        n=${base%%-*}
        if [[ "$n" =~ ^[0-9]{3}$ ]] && ((10#$n > max)) && [[ -f "${path}verdict.json" ]]; then
            max=$((10#$n))
            best_path="${path}verdict.json"
        fi
    done
    shopt -u nullglob
    [[ -n "$best_path" ]] && printf '%s\n' "$best_path"
}

success_probe() {
    # Reads the latest verdict.json and prints a single-line JSON summary.
    # Returns 0 if beats_winner=true, 1 otherwise (or if no verdict yet).
    # The loop logs the probe but does NOT halt on it.
    local verdict_path
    verdict_path=$(latest_verdict_path || true)
    if [[ -z "$verdict_path" ]]; then
        echo '{"probe":"no_verdict_yet"}'
        return 1
    fi
    uv run python - "$verdict_path" <<'PY'
import json
import sys

path = sys.argv[1]
data = json.loads(open(path, encoding="utf-8").read())

probe = {
    "probe": "ok",
    "iter": data.get("iter"),
    "best_config": data.get("best_config"),
    "best_score": data.get("best_score"),
    "best_tier": data.get("best_tier"),
    "beats_winner": bool(data.get("beats_winner", False)),
    "sortino_edge_vs_winner": data.get("sortino_edge_vs_winner"),
    "winner_benchmark_sortino": data.get("winner_benchmark_sortino"),
}
print(json.dumps(probe, sort_keys=True))
sys.exit(0 if probe["beats_winner"] else 1)
PY
}

build_prompt() {
    local next_n="$1"
    local current_total winner_sortino winner_config beats_threshold target_total n_trials_global
    current_total=$(memory_int_key "$MEMORY_FILE" "total_iterations")
    target_total=$(memory_int_key "$MEMORY_FILE" "target_total_iterations")
    n_trials_global=$(memory_int_key "$MEMORY_FILE" "cumulative_n_trials_global")
    winner_sortino=$(read_memory_key "$MEMORY_FILE" "incumbent_winner_sortino_lh56y")
    winner_config=$(read_memory_key "$MEMORY_FILE" "incumbent_winner_config")
    beats_threshold=$(read_memory_key "$MEMORY_FILE" "beats_winner_threshold_sortino")
    [[ -n "$winner_sortino" && -n "$winner_config" && -n "$beats_threshold" ]] || { echo "FATAL: missing winner fields in $MEMORY_FILE" >&2; exit 1; }

    local prompt_body
    prompt_body=$(cat "$PROMPT_FILE")

    cat <<EOF
Estamos no repo /var/www/github/finances/market-lab.

Esta é uma execução automática do letf_rotation_hunt LOOP, iteração ${next_n}
(total_iterations atual = ${current_total}; target = ${target_total}; cumulative_n_trials_global atual = ${n_trials_global}). Sessão zerada.

Benchmark fixo desta rodada:
  - winner config:   ${winner_config}
  - winner Sortino:  ${winner_sortino}
  - beats threshold: ${beats_threshold} (= ${winner_sortino} + 0.05)

Siga EXATAMENTE o template em studies/letf_rotation_hunt/LOOP_PROMPT.md
abaixo. Não espere resposta humana — se houver decisão ambígua, escolha a
opção mais conservadora que preserve os guardrails (mandate §1, study
módulos read-only, sem deploy automático) e registre no SUMMARY.md.

Guardrails do orquestrador (reforço — também listados no prompt):
  - NÃO realocar capital (mandate §1; 100% Plano C permanece).
  - NÃO modificar BASE_MEMORY.md, gates.py, scoring.py, plot_helper.py,
    data_loader.py, signals.py, signals_carry.py, synths.py, tax_layer.py, kill_rules.py,
    run_iter*.py, configs/, iterations/, verdict_schema.json.
  - NÃO push, apenas commit local.
  - PARE após PASSO 10 — não rodar próximo iter na mesma sessão.

--- LOOP_PROMPT.md ---

${prompt_body}
EOF
}

echo "=== letf_rotation_hunt loop @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
echo "MAX_ITER=$MAX_ITER ITER_TIMEOUT=${ITER_TIMEOUT}s COOLDOWN=${COOLDOWN}s BACKEND=$BACKEND CLAUDE_MODEL=$CLAUDE_MODEL OPENCODE_MODEL=$OPENCODE_MODEL CODEX_MODEL=$CODEX_MODEL" | tee -a "$RUN_LOG"
echo "Loop log: $RUN_LOG" | tee -a "$RUN_LOG"

CURRENT_TOTAL=$(memory_int_key "$MEMORY_FILE" "total_iterations")
TARGET_TOTAL=$(memory_int_key "$MEMORY_FILE" "target_total_iterations")
if (( CURRENT_TOTAL >= TARGET_TOTAL )); then
    echo "=== total_iterations=$CURRENT_TOTAL reached target_total_iterations=$TARGET_TOTAL; nothing to run ===" | tee -a "$RUN_LOG"
    exit 0
fi

# Initial probe (informational)
set +e
probe_output=$(success_probe 2>/dev/null)
set -e
echo "--- initial probe: $probe_output ---" | tee -a "$RUN_LOG"

if [[ -n "$DRY_RUN" ]]; then
    NEXT_N=$(next_iteration_number)
    echo "=== DRY_RUN: next iteration would be $NEXT_N ===" | tee -a "$RUN_LOG"
    echo "=== prompt that would be sent to a fresh $BACKEND process: ===" | tee -a "$RUN_LOG"
    build_prompt "$NEXT_N" | tee -a "$RUN_LOG"
    exit 0
fi

for round in $(seq 1 "$MAX_ITER"); do
    CURRENT_TOTAL=$(memory_int_key "$MEMORY_FILE" "total_iterations")
    TARGET_TOTAL=$(memory_int_key "$MEMORY_FILE" "target_total_iterations")
    if (( CURRENT_TOTAL >= TARGET_TOTAL )); then
        echo "=== total_iterations=$CURRENT_TOTAL reached target_total_iterations=$TARGET_TOTAL; stopping loop ===" | tee -a "$RUN_LOG"
        exit 0
    fi

    NEXT_N=$(next_iteration_number)
    PREV_TOTAL="$CURRENT_TOTAL"
    STAMP=$(date +%Y%m%d-%H%M%S)
    ITER_LOG="$LOG_DIR/iter_${NEXT_N}_${STAMP}.log"

    echo "--- round $round/$MAX_ITER -> iteration $NEXT_N (log=$ITER_LOG) @ $(date -Iseconds) ---" | tee -a "$RUN_LOG"
    PROMPT=$(build_prompt "$NEXT_N")

    set +e
    case "$BACKEND" in
        claude)
            timeout "$ITER_TIMEOUT" claude \
                --model "$CLAUDE_MODEL" \
                --dangerously-skip-permissions \
                --print "$PROMPT" 2>&1 | tee -a "$ITER_LOG"
            ;;
        opencode)
            timeout "$ITER_TIMEOUT" opencode run \
                --model "$OPENCODE_MODEL" \
                --dir "$PWD" \
                --dangerously-skip-permissions \
                "$PROMPT" 2>&1 | tee -a "$ITER_LOG"
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

    # Probe after iter (logs result; does NOT halt on beats_winner=true)
    set +e
    probe_output=$(success_probe 2>&1)
    set -e
    echo "--- success probe after iteration $NEXT_N: $probe_output ---" | tee -a "$RUN_LOG"

    CURRENT_TOTAL=$(memory_int_key "$MEMORY_FILE" "total_iterations")
    if (( CURRENT_TOTAL <= PREV_TOTAL )); then
        echo "=== iteration $NEXT_N did not advance LOOP_MEMORY total_iterations ($PREV_TOTAL -> $CURRENT_TOTAL); aborting loop ===" | tee -a "$RUN_LOG"
        exit 1
    fi

    if [[ "$round" -lt "$MAX_ITER" ]]; then
        echo "--- cooldown ${COOLDOWN}s before next fresh session ---" | tee -a "$RUN_LOG"
        sleep "$COOLDOWN"
    fi
done

echo "=== reached MAX_ITER=$MAX_ITER without halt @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
exit 0
