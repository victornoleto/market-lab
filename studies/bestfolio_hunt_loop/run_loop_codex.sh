#!/usr/bin/env bash
# Bestfolio Hunt Loop — codex-cli backend
#
# Drop-in replacement for run_loop.sh that uses `codex exec` instead of
# `claude -p`. Identical orchestration logic; only the agent invocation
# and the model env var differ.
#
# Usage:
#   bash studies/bestfolio_hunt_loop/run_loop_codex.sh            # default: o4-mini, 5 iters
#   CODEX_MODEL=o3 MAX_ITER=3 bash ...                             # o3, 3 iters
#   DRY_RUN=1 bash studies/bestfolio_hunt_loop/run_loop_codex.sh  # print prompt only
#
# Env vars:
#   CODEX_MODEL          (default o4-mini)   o4-mini | o3 | gpt-4o
#   CODEX_EXTRA_FLAGS    (default "")        e.g. "-s danger-full-access"
#   MAX_ITER             (default 5)
#   ITER_TIMEOUT         (default 5400)      seconds per iteration (90 min)
#   COOLDOWN             (default 30)        seconds between iterations
#   DRY_RUN              (default "")        if set, print prompt and exit
#
# Prerequisites:
#   - codex-cli installed and authenticated (codex login / OPENAI_API_KEY)
#   - AGENTS.md exists in repo root (see RUN_WITH_CODEX.md)
#   - GNU timeout available

set -euo pipefail
cd "$(dirname "$0")/../.."

: "${CODEX_MODEL:=o4-mini}"
: "${CODEX_EXTRA_FLAGS:=}"
: "${MAX_ITER:=5}"
: "${ITER_TIMEOUT:=5400}"
: "${COOLDOWN:=30}"
: "${DRY_RUN:=}"

LOOP_DIR="studies/bestfolio_hunt_loop"
MEMORY_FILE="$LOOP_DIR/BASE_MEMORY.md"
PROMPT_FILE="$LOOP_DIR/PROMPT.md"
CRITERIA_FILE="$LOOP_DIR/WINNER_AND_RANKING.md"
DEAD_ENDS_FILE="$LOOP_DIR/DEAD_ENDS.md"
ITER_BASE_DIR="$LOOP_DIR/iterations"
LOG_DIR="logs/bestfolio_hunt_loop"
RUN_LOG="$LOG_DIR/codex_loop_$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$ITER_BASE_DIR" "$LOG_DIR"

# Pre-flight checks
for f in "$MEMORY_FILE" "$PROMPT_FILE" "$CRITERIA_FILE" "$DEAD_ENDS_FILE"; do
    [[ -f "$f" ]] || { echo "FATAL: missing $f" >&2; exit 1; }
done
if [[ -z "$DRY_RUN" ]]; then
    command -v codex  >/dev/null || { echo "FATAL: codex not in PATH (npm install -g @openai/codex)" >&2; exit 1; }
    command -v timeout >/dev/null || { echo "FATAL: GNU timeout missing" >&2; exit 1; }
    if [[ ! -f "AGENTS.md" ]]; then
        echo "WARN: AGENTS.md not found. codex may not load CLAUDE.md automatically." | tee -a "$RUN_LOG"
        echo "      See studies/bestfolio_hunt_loop/RUN_WITH_CODEX.md for setup." | tee -a "$RUN_LOG"
    fi
fi

read_memory_key() {
    local key="$1"
    awk -v k="$key" '
        /^---$/{f++; if (f==2) exit; next}
        f==1 && $0 ~ "^"k":" {sub("^"k": *", ""); gsub(/"/, ""); print; exit}
    ' "$MEMORY_FILE"
}

next_iteration_number() {
    local total
    total=$(read_memory_key "total_iterations")
    if [[ "$total" =~ ^[0-9]+$ ]]; then
        printf "%03d" $((total + 1))
        return
    fi
    local last
    last=$(ls "$ITER_BASE_DIR" 2>/dev/null | grep -E '^[0-9]{3}-' | sort -n | tail -1 | cut -d- -f1 || echo "000")
    printf "%03d" $((10#${last:-000} + 1))
}

# Branch guard: auto-create feature branch when on main/master
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
    NEXT_N=$(next_iteration_number)
    AUTO_BRANCH="bestfolio-hunt/iter-${NEXT_N}"
    if git rev-parse --verify "$AUTO_BRANCH" >/dev/null 2>&1; then
        AUTO_BRANCH="bestfolio-hunt/iter-${NEXT_N}-$(date +%Y%m%d-%H%M%S)"
    fi
    echo "=== on '$CURRENT_BRANCH' — auto-creating feature branch '$AUTO_BRANCH' ===" | tee -a "$RUN_LOG"
    git checkout -b "$AUTO_BRANCH" 2>&1 | tee -a "$RUN_LOG"
    CURRENT_BRANCH="$AUTO_BRANCH"
fi

check_memory_size() {
    local bytes
    bytes=$(wc -c < "$MEMORY_FILE")
    if [[ "$bytes" -gt 20000 ]]; then
        echo "WARN: BASE_MEMORY.md is ${bytes} bytes (> 20 KB). Next iter should prune old log entries." | tee -a "$RUN_LOG"
    fi
}

build_prompt() {
    local iter_n="$1"
    local stamp
    stamp=$(date +%Y-%m-%d-%H%M)
    sed -e "s|{{ITERATION_N}}|$iter_n|g" -e "s|{{STAMP}}|$stamp|g" "$PROMPT_FILE"
}

echo "=== bestfolio_hunt_loop [codex backend] @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
echo "Branch: $CURRENT_BRANCH" | tee -a "$RUN_LOG"
echo "MAX_ITER=$MAX_ITER  ITER_TIMEOUT=${ITER_TIMEOUT}s  COOLDOWN=${COOLDOWN}s  MODEL=$CODEX_MODEL" | tee -a "$RUN_LOG"
echo "Memory: $MEMORY_FILE" | tee -a "$RUN_LOG"
echo "Loop log: $RUN_LOG" | tee -a "$RUN_LOG"
echo "" | tee -a "$RUN_LOG"

check_memory_size

STATUS=$(read_memory_key "status")
if [[ "$STATUS" == "winner" ]]; then
    echo "=== BASE_MEMORY already has status: winner — loop stopped ===" | tee -a "$RUN_LOG"
    exit 0
fi

if [[ -n "$DRY_RUN" ]]; then
    NEXT_N=$(next_iteration_number)
    echo "=== DRY_RUN: next iteration would be $NEXT_N ===" | tee -a "$RUN_LOG"
    echo "=== codex command that would run: ===" | tee -a "$RUN_LOG"
    echo "  codex exec -m $CODEX_MODEL --full-auto $CODEX_EXTRA_FLAGS <PROMPT>" | tee -a "$RUN_LOG"
    echo "=== prompt: ===" | tee -a "$RUN_LOG"
    build_prompt "$NEXT_N" | tee -a "$RUN_LOG"
    exit 0
fi

for round in $(seq 1 "$MAX_ITER"); do
    NEXT_N=$(next_iteration_number)
    STAMP=$(date +%Y%m%d-%H%M%S)
    ITER_LOG="$LOG_DIR/codex_iter_${NEXT_N}_${STAMP}.log"

    echo "--- round $round/$MAX_ITER → iteration $NEXT_N (log=$ITER_LOG) @ $(date -Iseconds) ---" | tee -a "$RUN_LOG"

    PROMPT=$(build_prompt "$NEXT_N")

    set +e
    # shellcheck disable=SC2086
    timeout "$ITER_TIMEOUT" codex exec \
        -m "$CODEX_MODEL" \
        --full-auto \
        $CODEX_EXTRA_FLAGS \
        "$PROMPT" 2>&1 | tee -a "$ITER_LOG"
    EXIT=${PIPESTATUS[0]}
    set -e

    if [[ "$EXIT" -eq 124 ]]; then
        echo "=== iteration $NEXT_N TIMED OUT (${ITER_TIMEOUT}s) — aborting loop ===" | tee -a "$RUN_LOG"
        exit 124
    fi
    if [[ "$EXIT" -ne 0 ]]; then
        echo "=== iteration $NEXT_N exited with code=$EXIT — aborting loop ===" | tee -a "$RUN_LOG"
        exit "$EXIT"
    fi

    # Post-iteration: commit any changes on current branch
    if git diff --quiet HEAD 2>/dev/null && [[ -z "$(git ls-files --others --exclude-standard)" ]]; then
        echo "--- iteration $NEXT_N: no changes to commit ---" | tee -a "$RUN_LOG"
    else
        ITER_SUMMARY=$(awk -v n="$NEXT_N" '
            /^### '"$NEXT_N"' / {found=1; next}
            found && /^- \*\*Hypothesis:\*\*/ {sub(/^- \*\*Hypothesis:\*\* */, ""); print; exit}
        ' "$MEMORY_FILE" | head -c 72)
        [[ -z "$ITER_SUMMARY" ]] && ITER_SUMMARY="iteration $NEXT_N"

        git add -A
        git commit -m "$(cat <<EOF
bestfolio-hunt: iter $NEXT_N — $ITER_SUMMARY
EOF
        )" --no-gpg-sign 2>&1 | tee -a "$RUN_LOG" || true
    fi

    STATUS=$(read_memory_key "status")
    WINNERS=$(read_memory_key "winners_found")
    echo "--- iteration $NEXT_N done | status=$STATUS winners=$WINNERS ---" | tee -a "$RUN_LOG"

    if [[ "$STATUS" == "winner" ]]; then
        echo "" | tee -a "$RUN_LOG"
        echo "=================================================================" | tee -a "$RUN_LOG"
        echo "=== WINNER FOUND at iteration $NEXT_N ===" | tee -a "$RUN_LOG"
        echo "=== inspect BASE_MEMORY.md '## Winners found' section ===" | tee -a "$RUN_LOG"
        echo "=== iteration dir: $ITER_BASE_DIR/${NEXT_N}-* ===" | tee -a "$RUN_LOG"
        echo "=================================================================" | tee -a "$RUN_LOG"
        exit 0
    fi

    check_memory_size

    if [[ "$round" -lt "$MAX_ITER" ]]; then
        echo "--- cooldown ${COOLDOWN}s before next iteration ---" | tee -a "$RUN_LOG"
        sleep "$COOLDOWN"
    fi
done

echo "" | tee -a "$RUN_LOG"
echo "=== reached MAX_ITER=$MAX_ITER without winner @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
echo "Final state:" | tee -a "$RUN_LOG"
echo "  total_iterations=$(read_memory_key total_iterations)" | tee -a "$RUN_LOG"
echo "  winners_found=$(read_memory_key winners_found)" | tee -a "$RUN_LOG"
echo "" | tee -a "$RUN_LOG"
echo "Re-run with higher MAX_ITER to continue, or inspect BASE_MEMORY.md" | tee -a "$RUN_LOG"
