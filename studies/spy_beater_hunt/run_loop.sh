#!/usr/bin/env bash
# spy_beater_hunt — shell orchestrator for the 50-iter loop
#
# Each iteration spawns Claude Code with a FRESH context window. Continuity
# across sessions lives in studies/spy_beater_hunt/BASE_MEMORY.md (the iter
# log + frontmatter). Halt conditions:
#
#   1. status: winner          → halt (first WINNER tier ≥ 90 + all bars met)
#   2. total_iterations >= 50  → halt (hunt budget exhausted)
#   3. otherwise               → keep iterating
#
# Usage:
#   bash studies/spy_beater_hunt/run_loop.sh                # default 5 iters
#   MAX_ITER=20 bash studies/spy_beater_hunt/run_loop.sh    # more
#   ITER_TIMEOUT=5400 bash studies/spy_beater_hunt/run_loop.sh  # 90 min/iter
#   DRY_RUN=1 bash studies/spy_beater_hunt/run_loop.sh      # print and exit
#
# Env vars:
#   MAX_ITER        (default 5)     hard cap on iterations this run
#   ITER_TIMEOUT    (default 5400)  seconds per iter (90 min)
#   COOLDOWN        (default 30)    seconds between iters
#   CLAUDE_MODEL    (default opus)  opus | sonnet | haiku
#   DRY_RUN         (default "")    if set, print prompt and exit
#
# Safety:
#   - --dangerously-skip-permissions passed to claude: audit logs/ after run
#   - Auto-commits after each iter (the per-iter prompt does this itself)

set -euo pipefail
cd "$(dirname "$0")/../.."

: "${MAX_ITER:=5}"
: "${ITER_TIMEOUT:=5400}"
: "${COOLDOWN:=30}"
: "${CLAUDE_MODEL:=opus}"
: "${DRY_RUN:=}"

LOOP_DIR="studies/spy_beater_hunt"
MEMORY_FILE="$LOOP_DIR/BASE_MEMORY.md"
PROMPT_FILE="$LOOP_DIR/SESSION_PROMPT.md"
LOG_DIR="logs/spy_beater_hunt"
RUN_LOG="$LOG_DIR/loop_$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$LOG_DIR"

# Pre-flight checks
for f in "$MEMORY_FILE" "$PROMPT_FILE"; do
    [[ -f "$f" ]] || { echo "FATAL: missing $f" >&2; exit 1; }
done
if [[ -z "$DRY_RUN" ]]; then
    command -v claude >/dev/null || { echo "FATAL: claude CLI not in PATH" >&2; exit 1; }
    command -v timeout >/dev/null || { echo "FATAL: GNU timeout missing" >&2; exit 1; }
fi

read_memory_key() {
    local key="$1"
    awk -v k="$key" '
        /^---$/{f++; if (f==2) exit; next}
        f==1 && $0 ~ "^"k":" {sub("^"k": *", ""); gsub(/"/, ""); print; exit}
    ' "$MEMORY_FILE"
}

run_one_iter() {
    local iter_n="$1"
    local prompt_body
    prompt_body=$(cat "$PROMPT_FILE")

    local prompt
    prompt="Estamos rodando o spy_beater_hunt (iter $iter_n).

Siga RIGOROSAMENTE o prompt template abaixo (de SESSION_PROMPT.md). Faça
TODOS os 11 passos antes de parar. Não pule etapas. Não mude metodologia
sem disparar KILL ou pedir permissão (não tem usuário ouvindo agora).

Após executar PASSO 11 (STOP), seu output deve terminar.

---

$prompt_body
"

    if [[ -n "$DRY_RUN" ]]; then
        echo "[DRY_RUN] would invoke claude with prompt below:"
        echo "$prompt"
        return 0
    fi

    echo "[iter $iter_n] starting at $(date -Iseconds)" | tee -a "$RUN_LOG"
    timeout "$ITER_TIMEOUT" claude \
        --model "$CLAUDE_MODEL" \
        --dangerously-skip-permissions \
        --print "$prompt" 2>&1 | tee -a "$RUN_LOG" || {
        local rc=$?
        echo "[iter $iter_n] claude exited with code $rc" | tee -a "$RUN_LOG"
        return "$rc"
    }
    echo "[iter $iter_n] done at $(date -Iseconds)" | tee -a "$RUN_LOG"
}

main() {
    local total_at_start
    total_at_start=$(read_memory_key "total_iterations")
    [[ "$total_at_start" =~ ^[0-9]+$ ]] || total_at_start=0
    local target
    target=$(read_memory_key "target_total_iterations")
    [[ "$target" =~ ^[0-9]+$ ]] || target=50

    echo "=== spy_beater_hunt loop start ==="
    echo "  total_iterations at start: $total_at_start"
    echo "  target_total_iterations:   $target"
    echo "  this-run MAX_ITER:         $MAX_ITER"
    echo "  ITER_TIMEOUT:              $ITER_TIMEOUT s"
    echo "  CLAUDE_MODEL:              $CLAUDE_MODEL"
    echo "  RUN_LOG:                   $RUN_LOG"
    echo "================================="

    local iters_done=0
    while ((iters_done < MAX_ITER)); do
        local total
        total=$(read_memory_key "total_iterations")
        [[ "$total" =~ ^[0-9]+$ ]] || total=0
        if ((total >= target)); then
            echo "[loop] total_iterations=$total ≥ target=$target — halt"
            break
        fi
        local status
        status=$(read_memory_key "status")
        if [[ "$status" == "winner" ]]; then
            echo "[loop] status=winner — halt"
            break
        fi

        local next_iter
        next_iter=$(printf "%03d" $((total + 1)))
        run_one_iter "$next_iter" || {
            echo "[loop] iter $next_iter failed; continue with next attempt"
        }
        iters_done=$((iters_done + 1))
        ((iters_done < MAX_ITER)) && sleep "$COOLDOWN"
    done

    echo "=== spy_beater_hunt loop done — $iters_done iters this run ==="
}

main "$@"
