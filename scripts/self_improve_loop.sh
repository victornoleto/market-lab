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

: "${MAX_ITER:=100}"
: "${ITER_TIMEOUT:=1800}"
: "${SCOPE:=code}"
: "${COOLDOWN:=10}"
: "${CLAUDE_MODEL:=sonnet}"

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

# Branch guard: refuse to run on main/master
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
    echo "FATAL: self_improve_loop refuses to run on '$CURRENT_BRANCH'." >&2
    echo "Create a feature branch first: git checkout -b self-improve/<name>" >&2
    exit 1
fi

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

**FIRST ACTION (mandatory):** Read \`docs/self_improvement/memory.md\` in full. Your conversation history is empty — that file is your only continuity. It contains the goal, current phase (A or B), winners found per path, project state anchor, known dead ends, promising leads, binding constraints, and a history of prior iterations.

$scope_clause

## Mission (across all iterations)

The loop has TWO phases. Memory.md frontmatter has \`phase: A\` or \`phase: B\` — read it first.

**Phase A — Find ≥3 gate-passing strategies, with ≥1 per path.**
- Path A = [SHORT-HOLD CFD] (Pepperstone, swap, median hold ≤ 5 days). Use the Tiingo IEX 1h cache (or 5m/15m if added).
- Path B = [SWING BROKER] (Brazilian stock broker, no swap, 15% capital-gains tax modeled in net Sharpe). Use Tiingo daily cache.
- Each winner = a config that passes all 3 gates (PBO < 0.5 AND DSR p < 0.05 AND WF ≥ 6/8) on its path AND survives single-block OOS hold-out AND a forward-window stress (newest quarter).
- A winner enters \`winners_short_hold:\` or \`winners_swing:\` in memory.md frontmatter (YAML list of dicts: \`{strategy, asset, frequency, sharpe_is, sharpe_oos, jornada}\`).
- Phase A completes when: \`len(winners_short_hold) ≥ 1 AND len(winners_swing) ≥ 1 AND total ≥ 3\`. Set \`phase: B\` in frontmatter on the iteration that completes this.

**Phase B — Test, optimize, validate the winners. DO NOT exit yet.**
- Re-validate each winner on the LONGEST available historical window (manifest \`first_dt\` → \`last_dt\`).
- Cost ablation per path (real Pepperstone spreads/swap for A; 15% tax + spread for B).
- Multi-asset transport: does the winner replicate on a related asset?
- Cross-strategy correlation: are the winners independent edges or correlated?
- GARCH / vol-sized variants when applicable.
- Production-readiness checklist (CI bands via stationary bootstrap; regime decomposition; risk-pct sensitivity at \$1k account).
- Phase B leads are listed in memory.md \`## Phase B leads\` (separate from Phase A leads).
- Loop exits with \`status: done\` ONLY when Phase B leads are exhausted AND a production-readiness summary jornada exists.

## Per-iteration task

1. Read memory.md (especially: \`phase\`, \`winners_short_hold\`, \`winners_swing\`, \`## Leads\` if phase==A, \`## Phase B leads\` if phase==B).
2. Decide ONE concrete experiment for the current phase. Strict rules:
   - Do NOT repeat anything in \`## Dead ends\`.
   - Phase A: pick from \`## Leads\` in listed order unless documented reason to deviate.
   - Phase B: pick from \`## Phase B leads\` in listed order; if exhausted, propose a new B-task (e.g., a new asset for an existing winner) and append it.
   - The step must complete in under ~25 minutes wallclock.
3. Execute the step. Report intermediate findings in your output.
4. **HARD RULE — TIME WINDOW:** every backtest MUST use the LONGEST available historical window for each (ticker, frequency). Read \`data/tiingo/manifest.json\` first to get \`first_dt\` / \`last_dt\` per (ticker, freq). DO NOT use a shorter window unless explicitly justified (e.g., a regime cut). Reject your own design if it uses a window narrower than the manifest allows.
5. Update \`docs/self_improvement/memory.md\`:
   - Bump \`iteration:\` in the YAML frontmatter.
   - If a config passed: append it to \`winners_short_hold:\` or \`winners_swing:\` with the dict format above.
   - Update \`best_verdict:\`, \`best_sharpe:\`, \`best_asset:\`, \`best_config:\` if you produced a better result than the current best.
   - Recompute Phase A completion: if \`len(winners_short_hold) ≥ 1 AND len(winners_swing) ≥ 1 AND total ≥ phase_a_target\` → set \`phase: B\` (transition).
   - Set \`status: done\` ONLY when phase==B AND \`## Phase B leads\` is exhausted AND production-readiness jornada exists. Otherwise leave \`status: in_progress\`.
   - Append a terse iteration entry under \`## History\` (5 lines max each).
   - Move consumed leads to \`## Dead ends\` (one line each).
6. **Document significant results in jornada/.** Any gate-passing config or OOS/stress validation = mandatory \`jornada/YYYY-MM-DD-HHmm-slug.md\` entry, added to top of \`jornada/README.md\` index. Tag entries clearly with \`[SHORT-HOLD CFD]\` or \`[SWING BROKER]\` in the header.
7. **KEEP memory.md COMPACT (< 15 KB).** Rules:
   - \`## History\` entries: MAX 5 lines each. No tables, no code blocks.
   - \`## Dead ends\`: ONE LINE per entry.
   - Move detailed analyses to jornada/ entries.
   - If memory.md > 15 KB after edits, PRUNE oldest \`## History\` entries (keep 5 newest + all ★ PASS entries) before exiting. Check: \`wc -c < docs/self_improvement/memory.md\`.
8. Exit cleanly.

## Hard rules

- The memory file is sacred. Update conservatively — every edit is read by the next iteration.
- Phase B does NOT terminate the loop. Only \`status: done\` after Phase B leads exhausted does.
- All claims of "edge" or "winner" require passing all 3 gates + single-block OOS + forward-window stress. No partial credit.
- Cite \`[book.slug, p.X]\` for any strategy/parameter choice grounded in the knowledge base.
- Working directory: /var/www/pessoal/ai-trade.
- The shell loop auto-commits after each iteration on the isolated branch. Do NOT run \`git commit\` yourself.
- **TIME WINDOW (repeated for emphasis):** ALWAYS use the LONGEST available historical window per (ticker, frequency). Check \`data/tiingo/manifest.json\` before backtesting. Narrower windows = wasted iteration.
- **Path labelling:** every winner candidate must be tagged \`[SHORT-HOLD CFD]\` (Path A, median hold ≤ 5 days, Pepperstone swap modeled) or \`[SWING BROKER]\` (Path B, daily/swing, 15% BR tax modeled in net Sharpe).
- **Data source discipline:** intraday cache was cleaned 2026-04-16 of US-holiday placeholder bars. The \`_filter_orphan_intraday_bars\` guard is active for new fetches. If you suspect data contamination on any new ticker/freq, run \`scripts/clean_intraday_orphans.py --dry-run\` before trusting the result.

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

read_phase() {
    awk '/^---$/{f++; next} f==1 && /^phase:/{print $2; exit}' "$MEMORY_FILE"
}

# Count winners per path (YAML lists in frontmatter); naive grep — counts the
# number of "- " bullet lines under each list. Good enough to display progress.
read_winners_count() {
    local list_name="$1"
    awk -v lname="$list_name" '
        /^---$/{f++; next}
        f==1 && $0 ~ "^"lname":" {in_list=1; next}
        f==1 && in_list && /^[a-zA-Z_]+:/ {in_list=0}
        f==1 && in_list && /^  - / {n++}
        END{print n+0}
    ' "$MEMORY_FILE"
}

echo "=== self_improve_loop @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
echo "Branch: $CURRENT_BRANCH" | tee -a "$RUN_LOG"
echo "MAX_ITER=$MAX_ITER  SCOPE=$SCOPE  ITER_TIMEOUT=${ITER_TIMEOUT}s  COOLDOWN=${COOLDOWN}s  CLAUDE_MODEL=$CLAUDE_MODEL" | tee -a "$RUN_LOG"
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
        --model "$CLAUDE_MODEL" \
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

    # Auto-commit changes from this iteration (safe: we're on an isolated branch)
    MEM_ITER=$(read_iteration)
    ITER_SUMMARY=$(awk '/^### Iteration '"$MEM_ITER"'/{found=1; next} found && /^- Hypothesis:/{print; exit}' "$MEMORY_FILE" \
        | sed 's/^- Hypothesis: //' | head -c 72)
    [[ -z "$ITER_SUMMARY" ]] && ITER_SUMMARY="iteration $MEM_ITER"
    if git diff --quiet HEAD 2>/dev/null && [[ -z "$(git ls-files --others --exclude-standard)" ]]; then
        echo "--- No changes to commit for iteration $i ---" | tee -a "$RUN_LOG"
    else
        git add -A
        git commit -m "$(cat <<EOF
self-improve: iter $MEM_ITER — $ITER_SUMMARY
EOF
        )" --no-gpg-sign 2>&1 | tee -a "$RUN_LOG" || true
    fi

    STATUS=$(read_status)
    PHASE=$(read_phase)
    SHORT_HOLD_N=$(read_winners_count "winners_short_hold")
    SWING_N=$(read_winners_count "winners_swing")
    # Extract verdict from the iteration's Result line (★ = PASS, FAIL otherwise)
    ITER_VERDICT=$(awk '/^### Iteration '"$MEM_ITER"'/{found=1; next} found && /^- Result:/{print; exit}' "$MEMORY_FILE" \
        | grep -qo '★' && echo "★ PASS" || echo "FAIL")
    ITER_RESULT=$(awk '/^### Iteration '"$MEM_ITER"'/{found=1; next} found && /^- Result:/{sub(/^- Result: /,""); print; exit}' "$MEMORY_FILE" \
        | head -c 120)
    echo "--- Iteration $i done | $ITER_VERDICT | iter=$MEM_ITER status=$STATUS phase=$PHASE winners(short=$SHORT_HOLD_N, swing=$SWING_N) ---" \
        | tee -a "$RUN_LOG"
    [[ -n "$ITER_RESULT" ]] && echo "    $ITER_RESULT" | tee -a "$RUN_LOG"

    if [[ "$STATUS" == "done" ]]; then
        echo "=== SUCCESS at iteration $i — Phase B exhausted, mission complete ===" \
            | tee -a "$RUN_LOG"
        echo "=== winners: short_hold=$SHORT_HOLD_N, swing=$SWING_N ===" \
            | tee -a "$RUN_LOG"
        echo "=== Review memory.md + jornada/ and decide next steps ===" \
            | tee -a "$RUN_LOG"
        exit 0
    fi

    sleep "$COOLDOWN"
done

echo "=== Loop reached MAX_ITER=$MAX_ITER without status:done @ $(date -Iseconds) ===" \
    | tee -a "$RUN_LOG"
echo "Final state: phase=$PHASE  winners(short=$SHORT_HOLD_N, swing=$SWING_N)" \
    | tee -a "$RUN_LOG"
echo "Inspect $MEMORY_FILE for accumulated findings; re-run loop with higher MAX_ITER to continue."
