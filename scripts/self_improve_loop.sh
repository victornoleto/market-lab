#!/usr/bin/env bash
# Self-improvement loop: each iteration runs Claude Code in a FRESH context
# window. The memory file (docs/self_improvement/memory.md) is the only
# continuity between iterations — it stores goal, history, current best, and
# the binding constraints. Loop terminates when memory's `status: done` flag
# flips, when MAX_ITER is reached, or when an iteration exits non-zero.
#
# Usage:
#   bash scripts/self_improve_loop.sh                # research scope, 10 iter
#   MAX_ITER=20 SCOPE=research bash scripts/self_improve_loop.sh
#   SCOPE=code   bash scripts/self_improve_loop.sh   # allow code edits
#
# Env vars:
#   MAX_ITER       (default 10)   hard cap on iterations
#   ITER_TIMEOUT   (default 900)  seconds per iteration (15 min)
#   SCOPE          (default research)  research | code
#                  - research: read-only on src/, tests/; can write reports/
#                              and docs/self_improvement/. No git commits.
#                  - code: can also add/modify src/, tests/. Still no commits.
#   COOLDOWN       (default 5)    seconds between iterations
#
# Cost / safety:
#   Each iteration burns the budget of one full Claude Code session (could be
#   many Opus tokens). Start small (MAX_ITER=2-3) to gauge before scaling.
#   --dangerously-skip-permissions is set: Claude can run any tool without
#   confirmation. Audit logs/self_improve/iter_*.log after each run.
set -euo pipefail
cd "$(dirname "$0")/.."

: "${MAX_ITER:=10}"
: "${ITER_TIMEOUT:=900}"
: "${SCOPE:=research}"
: "${COOLDOWN:=5}"

MEMORY_DIR="docs/self_improvement"
MEMORY_FILE="$MEMORY_DIR/memory.md"
TEMPLATE="$MEMORY_DIR/memory.template.md"
LOG_DIR="logs/self_improve"
RUN_LOG="$LOG_DIR/loop_$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$MEMORY_DIR" "$LOG_DIR"

# Pre-flight checks
command -v claude >/dev/null || { echo "claude CLI not in PATH" >&2; exit 1; }
command -v timeout >/dev/null || { echo "GNU timeout missing" >&2; exit 1; }
[[ -f "$TEMPLATE" ]] || { echo "missing $TEMPLATE" >&2; exit 1; }

# Rotate old per-iteration logs (keep loop_* logs for audit; iter_* files
# accumulate quickly and are less valuable once their findings are in memory).
find "$LOG_DIR" -name 'iter_*.log' -mtime +14 -delete 2>/dev/null || true

# Bootstrap memory file from template on first run
if [[ ! -f "$MEMORY_FILE" ]]; then
    echo "Bootstrapping $MEMORY_FILE from template" | tee -a "$RUN_LOG"
    cp "$TEMPLATE" "$MEMORY_FILE"
fi

# Memory size guard: warn above ~60KB. memory.md gets re-sent to the model
# every iteration, so unbounded growth is a direct token cost. The next
# iteration's prompt already instructs Claude to prune ## History past 50
# entries — this is the visibility signal that it needs to happen now.
MEM_BYTES=$(wc -c < "$MEMORY_FILE" 2>/dev/null || echo 0)
if [[ "$MEM_BYTES" -gt 60000 ]]; then
    echo "WARN: memory.md is ${MEM_BYTES} bytes (> 60k). Next iteration should prune ## History." \
        | tee -a "$RUN_LOG"
fi

# Build per-iteration prompt according to scope.
#
# NOTE on cost: the rules + scope_clause block is static across iterations
# (~1.5-3k tokens), only the opening line and the fact that memory.md is
# fresh each time change. When `claude -p` exposes a flag to mark stable
# segments with cache_control: ephemeral (Anthropic prompt caching), split
# this heredoc into (STATIC) + (DYNAMIC_BOOTSTRAP) to save ~70% encoding
# tokens per iteration. Current CLI does not — we pay the full encode each
# call. Acceptable while MAX_ITER stays < 30/night on the R$200 plan.
build_prompt() {
    local scope_clause
    case "$SCOPE" in
        research)
            scope_clause="**Scope: RESEARCH ONLY.** You may read any file, run backtests via existing CLIs, write to reports/ and docs/self_improvement/. You MAY NOT edit anything under src/, tests/, or specs/. You MAY NOT run any git mutating command (commit, push, reset, etc.). The shell loop handles git outside iterations."
            ;;
        code)
            scope_clause="**Scope: CODE-ALLOWED.** You may add new files under src/ai_trade/ and tests/, and modify existing files there. Run pytest after every code change; the suite MUST stay green or revert. You MAY NOT run any git mutating command (commit, push, reset). The shell loop handles git outside iterations."
            ;;
        *)
            echo "Unknown SCOPE: $SCOPE (must be research|code)" >&2
            exit 2
            ;;
    esac

    cat <<PROMPT
You are resuming an autonomous self-improvement loop for the ai-trade project at /var/www/pessoal/ai-trade.

**FIRST ACTION (mandatory):** Read \`docs/self_improvement/memory.md\` in full. Your conversation history is empty — that file is your only continuity. It contains the goal, project state anchor, known dead ends, promising leads, binding constraints, and a history of prior iterations.

$scope_clause

## Per-iteration task

1. Read memory.md.
2. Decide ONE concrete next experiment, audit, or implementation step. Strict rules:
   - Do NOT repeat anything in "Known dead ends".
   - Prefer items from "Promising leads not yet explored" in the listed order, unless you have a specific reason to deviate (document it).
   - The step must be completable in under ~15 minutes wallclock.
3. Execute the step. Report intermediate findings in your output.
4. Update \`docs/self_improvement/memory.md\`:
   - Bump \`iteration:\` in the YAML frontmatter.
   - Update \`best_verdict:\`, \`best_sharpe:\`, \`best_asset:\`, \`best_config:\` if you produced a better result than the current best (any 3-gate-passing config beats any non-passing).
   - Set \`status: done\` ONLY if a config passed all 3 gates (PBO < 0.5 AND DSR p < 0.05 AND WF ≥ 6/8). Otherwise leave \`in_progress\`.
   - Append a terse iteration entry under \`## History\` with this template (5-15 lines):
     \`\`\`
     ### Iteration N — YYYY-MM-DD HH:MM
     - Hypothesis: <one sentence>
     - Action: <command(s) run, file(s) written>
     - Result: <verdict, key metrics>
     - Conclusion: <what we learned, what to try next>
     \`\`\`
   - If \`## History\` exceeds ~50 entries, prune oldest (preserve 5 newest + any breakthrough entries; document the pruning).
   - Move consumed items from "Promising leads" to "Known dead ends" (with a one-line reason) when the lead is exhausted.
5. Exit cleanly.

## Hard rules

- The memory file is sacred. Update it conservatively — every edit is read by the next iteration.
- All claims of "edge" or "improvement" require passing all 3 gates. No partial credit.
- Cite \`[book.slug, p.X]\` for any strategy/parameter choice grounded in the knowledge base.
- Working directory: /var/www/pessoal/ai-trade
- Goal: gate-passing strategy. Memory is single source of truth.

Begin by reading memory.md.
PROMPT
}

# Read status flag from memory frontmatter (between the first two `---` lines)
read_status() {
    awk '/^---$/{f++; next} f==1 && /^status:/{print $2; exit}' "$MEMORY_FILE"
}

read_iteration() {
    awk '/^---$/{f++; next} f==1 && /^iteration:/{print $2; exit}' "$MEMORY_FILE"
}

echo "=== self_improve_loop @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
echo "MAX_ITER=$MAX_ITER  SCOPE=$SCOPE  ITER_TIMEOUT=${ITER_TIMEOUT}s  COOLDOWN=${COOLDOWN}s" | tee -a "$RUN_LOG"
echo "Memory: $MEMORY_FILE" | tee -a "$RUN_LOG"
echo "Loop log: $RUN_LOG" | tee -a "$RUN_LOG"
echo "" | tee -a "$RUN_LOG"

START_ITER=$(($(read_iteration) + 1))
END_ITER=$((START_ITER + MAX_ITER - 1))

for i in $(seq "$START_ITER" "$END_ITER"); do
    ITER_LOG="$LOG_DIR/iter_$(printf '%04d' "$i")_$(date +%Y%m%d-%H%M%S).log"
    echo "--- Iteration $i (memory iter ↑ to $i, log=$ITER_LOG) @ $(date -Iseconds) ---" \
        | tee -a "$RUN_LOG"

    PROMPT=$(build_prompt)

    set +e
    timeout "$ITER_TIMEOUT" claude -p "$PROMPT" \
        --dangerously-skip-permissions 2>&1 | tee -a "$ITER_LOG"
    EXIT=${PIPESTATUS[0]}
    set -e

    if [[ "$EXIT" -eq 124 ]]; then
        echo "=== Iteration $i HIT TIMEOUT (${ITER_TIMEOUT}s) — aborting loop ===" \
            | tee -a "$RUN_LOG"
        exit 124
    fi
    if [[ "$EXIT" -ne 0 ]]; then
        echo "=== Iteration $i exited code=$EXIT — aborting loop ===" \
            | tee -a "$RUN_LOG"
        exit "$EXIT"
    fi

    STATUS=$(read_status)
    MEM_ITER=$(read_iteration)
    echo "--- Iteration $i done | memory iter=$MEM_ITER status=$STATUS ---" \
        | tee -a "$RUN_LOG"

    if [[ "$STATUS" == "done" ]]; then
        echo "=== SUCCESS at iteration $i — gate-passing config found ===" \
            | tee -a "$RUN_LOG"
        echo "=== Review memory.md and commit when ready ==="
        exit 0
    fi

    sleep "$COOLDOWN"
done

echo "=== Loop ended after $MAX_ITER iterations without SUCCESS @ $(date -Iseconds) ===" \
    | tee -a "$RUN_LOG"
echo "Inspect $MEMORY_FILE for accumulated findings."
