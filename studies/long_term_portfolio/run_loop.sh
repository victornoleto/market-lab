#!/usr/bin/env bash
# Long-Term Portfolio Loop — shell orchestrator
#
# Each iteration runs Claude Code in a FRESH context window. The continuity
# between sessions is studies/long_term_portfolio/BASE_MEMORY.md.
#
# The loop reads BASE_MEMORY.md frontmatter `status` field after each
# iteration. Halt logic:
#   1. status: hunting     → keep iterating up to MAX_ITER
#   2. status: winner      → halt (legacy behavior; first-ever winner)
#   3. beats_incumbent: true → halt (a NEW iter strictly beat the incumbent
#                              winner per BASE_MEMORY's incumbent_winner_score
#                              field — set by the iter prompt at STAGE 5)
# Otherwise continue. This lets the loop hunt past iter 011 while still
# halting promptly when a stronger candidate emerges.
#
# Usage:
#   bash studies/long_term_portfolio/run_loop.sh                   # default 5 iterations
#   MAX_ITER=10 bash studies/long_term_portfolio/run_loop.sh       # more iterations
#   ITER_TIMEOUT=7200 bash studies/long_term_portfolio/run_loop.sh # 2h per iter (default 1.5h)
#   DRY_RUN=1 bash studies/long_term_portfolio/run_loop.sh         # just print prompt, don't invoke claude
#
# Env vars:
#   MAX_ITER        (default 5)     hard cap on iterations
#   ITER_TIMEOUT    (default 5400)  seconds per iteration (90 min)
#   COOLDOWN        (default 30)    seconds between iterations
#   CLAUDE_MODEL    (default opus)  opus | sonnet | haiku
#   DRY_RUN         (default "")    if set, print prompt and exit
#
# Safety:
#   - Auto-creates bestfolio-hunt/iter-NNN branch when invoked from main/master
#   - --dangerously-skip-permissions passed to claude: audit logs/ after each run
#   - Auto-commits after each iteration on the current (non-main) branch

set -euo pipefail
cd "$(dirname "$0")/../.."

: "${MAX_ITER:=5}"
: "${ITER_TIMEOUT:=5400}"
: "${COOLDOWN:=30}"
: "${CLAUDE_MODEL:=opus}"
: "${DRY_RUN:=}"

LOOP_DIR="studies/long_term_portfolio"
MEMORY_FILE="$LOOP_DIR/BASE_MEMORY.md"
PROMPT_FILE="$LOOP_DIR/PROMPT.md"
CRITERIA_FILE="$LOOP_DIR/WINNER_AND_RANKING.md"
DEAD_ENDS_FILE="$LOOP_DIR/DEAD_ENDS.md"
ITER_BASE_DIR="$LOOP_DIR/iterations"
LOG_DIR="logs/long_term_portfolio"
RUN_LOG="$LOG_DIR/loop_$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$ITER_BASE_DIR" "$LOG_DIR"

# Pre-flight checks
for f in "$MEMORY_FILE" "$PROMPT_FILE" "$CRITERIA_FILE" "$DEAD_ENDS_FILE"; do
    [[ -f "$f" ]] || { echo "FATAL: missing $f" >&2; exit 1; }
done
if [[ -z "$DRY_RUN" ]]; then
    command -v claude >/dev/null || { echo "FATAL: claude CLI not in PATH" >&2; exit 1; }
    command -v timeout >/dev/null || { echo "FATAL: GNU timeout missing" >&2; exit 1; }
fi

# Helper: read YAML frontmatter key from BASE_MEMORY.md
read_memory_key() {
    local key="$1"
    awk -v k="$key" '
        /^---$/{f++; if (f==2) exit; next}
        f==1 && $0 ~ "^"k":" {sub("^"k": *", ""); gsub(/"/, ""); print; exit}
    ' "$MEMORY_FILE"
}

# Helper: find next iteration number.
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

# Branch guard: auto-create a feature branch when on main/master.
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

# Memory-size guard
check_memory_size() {
    local bytes
    bytes=$(wc -c < "$MEMORY_FILE")
    if [[ "$bytes" -gt 20000 ]]; then
        echo "WARN: BASE_MEMORY.md is ${bytes} bytes (> 20 KB). Next iter should prune old log entries." | tee -a "$RUN_LOG"
    fi
}

# Build the iteration prompt (substituting placeholders)
build_prompt() {
    local iter_n="$1"
    local stamp
    stamp=$(date +%Y-%m-%d-%H%M)
    sed -e "s|{{ITERATION_N}}|$iter_n|g" -e "s|{{STAMP}}|$stamp|g" "$PROMPT_FILE"
}

echo "=== long_term_portfolio @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
echo "Branch: $CURRENT_BRANCH" | tee -a "$RUN_LOG"
echo "MAX_ITER=$MAX_ITER  ITER_TIMEOUT=${ITER_TIMEOUT}s  COOLDOWN=${COOLDOWN}s  MODEL=$CLAUDE_MODEL" | tee -a "$RUN_LOG"
echo "Memory: $MEMORY_FILE" | tee -a "$RUN_LOG"
echo "Loop log: $RUN_LOG" | tee -a "$RUN_LOG"
echo "" | tee -a "$RUN_LOG"

check_memory_size

# Check halt state. The legacy halt is `status: winner` (first-ever winner).
# Post-iter-011, the loop runs in "hunting" mode with an incumbent winner
# tracked in BASE_MEMORY frontmatter; halt only when a NEW iter sets
# `beats_incumbent: true` (i.e., score > incumbent_winner_score OR
# Sharpe edge ≥ +0.10 vs incumbent on ≥2 datasets — the iter prompt sets
# this flag at STAGE 5).
STATUS=$(read_memory_key "status")
INCUMBENT_ITER=$(read_memory_key "incumbent_winner_iter")
if [[ "$STATUS" == "winner" ]]; then
    echo "=== BASE_MEMORY status: winner — loop halted ===" | tee -a "$RUN_LOG"
    echo "=== inspect BASE_MEMORY.md + iterations/ for the winner details ===" | tee -a "$RUN_LOG"
    exit 0
fi
if [[ -n "$INCUMBENT_ITER" ]]; then
    echo "=== Hunting past incumbent winner: $INCUMBENT_ITER ===" | tee -a "$RUN_LOG"
fi

# Dry run: print prompt and exit
if [[ -n "$DRY_RUN" ]]; then
    NEXT_N=$(next_iteration_number)
    echo "=== DRY_RUN: next iteration would be $NEXT_N ===" | tee -a "$RUN_LOG"
    echo "=== prompt that would be sent: ===" | tee -a "$RUN_LOG"
    build_prompt "$NEXT_N" | tee -a "$RUN_LOG"
    exit 0
fi

for round in $(seq 1 "$MAX_ITER"); do
    NEXT_N=$(next_iteration_number)
    STAMP=$(date +%Y%m%d-%H%M%S)
    ITER_LOG="$LOG_DIR/iter_${NEXT_N}_${STAMP}.log"

    echo "--- round $round/$MAX_ITER → iteration $NEXT_N (log=$ITER_LOG) @ $(date -Iseconds) ---" | tee -a "$RUN_LOG"

    PROMPT=$(build_prompt "$NEXT_N")

    set +e
    timeout "$ITER_TIMEOUT" claude -p "$PROMPT" \
        --model "$CLAUDE_MODEL" \
        --dangerously-skip-permissions 2>&1 | tee -a "$ITER_LOG"
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
    BEATS=$(read_memory_key "beats_incumbent")
    LATEST_SCORE=$(read_memory_key "latest_score")
    echo "--- iteration $NEXT_N done | status=$STATUS winners=$WINNERS score=$LATEST_SCORE beats_incumbent=$BEATS ---" | tee -a "$RUN_LOG"

    # Halt: first-ever winner (legacy) OR strict beat of incumbent winner.
    if [[ "$STATUS" == "winner" || "$BEATS" == "true" ]]; then
        echo "" | tee -a "$RUN_LOG"
        echo "=================================================================" | tee -a "$RUN_LOG"
        if [[ "$BEATS" == "true" ]]; then
            echo "=== 🏆 NEW WINNER at iteration $NEXT_N — beats incumbent ===" | tee -a "$RUN_LOG"
        else
            echo "=== 🏆 WINNER FOUND at iteration $NEXT_N ===" | tee -a "$RUN_LOG"
        fi
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
echo "  cumulative_n_trials=$(read_memory_key cumulative_n_trials)" | tee -a "$RUN_LOG"
echo "" | tee -a "$RUN_LOG"
echo "Re-run with higher MAX_ITER to continue, or inspect BASE_MEMORY.md" | tee -a "$RUN_LOG"
echo "to review what was tried and plan next direction manually." | tee -a "$RUN_LOG"
