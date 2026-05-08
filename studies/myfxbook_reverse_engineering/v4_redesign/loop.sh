#!/usr/bin/env bash
# MyFxBook Pipeline v4 Redesign — automatic loop orchestrator.
#
# Cada iteracao invoca uma sessao zerada de Claude Code. A continuidade entre
# sessoes vem dos arquivos PROGRESS.md, next_prompt.md, iterations/ e jornada/.
#
# Modelo task-driven: o loop termina quando todas as tasks em PROGRESS.md
# estiverem DONE, ou quando uma task FAIL/BLOCKED requer intervencao humana.
#
# Usage:
#   bash studies/myfxbook_reverse_engineering/v4_redesign/loop.sh
#   MAX_ITER=5 bash studies/myfxbook_reverse_engineering/v4_redesign/loop.sh
#   DRY_RUN=1 bash studies/myfxbook_reverse_engineering/v4_redesign/loop.sh
#   ITER_TIMEOUT=5400 CLAUDE_MODEL=sonnet MAX_ITER=12 bash studies/myfxbook_reverse_engineering/v4_redesign/loop.sh
#   TASK_RUNNER=opencode OPENCODE_MODEL=openai/gpt-5.5 MAX_ITER=5 bash studies/myfxbook_reverse_engineering/v4_redesign/loop.sh
#
# Env vars:
#   MAX_ITER       (default 1)     hard cap em iteracoes nesta execucao
#   ITER_TIMEOUT   (default 5400)  segundos por iteracao (90 min)
#   COOLDOWN       (default 30)    segundos entre iteracoes
#   TASK_RUNNER    (default claude) claude | opencode
#   CLAUDE_MODEL   (default sonnet) opus | sonnet | haiku
#   OPENCODE_MODEL (default openai/gpt-5.5) usado quando TASK_RUNNER=opencode
#   DRY_RUN        (default "")    se set, imprime prompt e sai
#   VALIDATOR_REQUIRED (default 0)  se 1, aborta quando validador nao roda/passa
#   VALIDATOR_MODEL    (default "") modelo opencode, ex: openai/gpt-5.5
#   VALIDATOR_CMD      (default "") comando alternativo; recebe prompt via stdin
#   VALIDATOR_TIMEOUT  (default 1800) segundos para validacao bloqueante
#
# Stop conditions:
#   - Todas tasks DONE ou BLOCKED → exit 0
#   - Uma task FAILED → exit 1, intervencao humana
#   - PROGRESS.md nao mudou apos iteracao (sessao nao avancou) → exit 2
#   - PROTOCOL.md alterado durante sessao → exit 3 (security guard)
#   - Validacao bloqueante STOP/indeterminada → exit 5

set -euo pipefail

cd "$(dirname "$0")/../../.."

: "${MAX_ITER:=1}"
: "${ITER_TIMEOUT:=5400}"
: "${COOLDOWN:=30}"
: "${TASK_RUNNER:=claude}"
: "${CLAUDE_MODEL:=sonnet}"
: "${OPENCODE_MODEL:=openai/gpt-5.5}"
: "${DRY_RUN:=}"
: "${VALIDATOR_REQUIRED:=0}"
: "${VALIDATOR_MODEL:=}"
: "${VALIDATOR_CMD:=}"
: "${VALIDATOR_TIMEOUT:=1800}"

LOOP_DIR="studies/myfxbook_reverse_engineering/v4_redesign"
PROGRESS_FILE="$LOOP_DIR/PROGRESS.md"
PROTOCOL_FILE="$LOOP_DIR/PROTOCOL.md"
PROMPT_FILE="$LOOP_DIR/next_prompt.md"
SPEC_FILE="$LOOP_DIR/SPEC.md"
TASKS_FILE="$LOOP_DIR/TASKS.md"
LOG_DIR="logs/myfxbook_v4_redesign"
RUN_LOG="$LOG_DIR/loop_$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$LOG_DIR"

# Pre-flight checks
for f in "CLAUDE.md" "jornada/README.md" "$PROGRESS_FILE" "$PROTOCOL_FILE" "$PROMPT_FILE" "$SPEC_FILE" "$TASKS_FILE"; do
    [[ -f "$f" ]] || { echo "FATAL: missing $f" >&2; exit 1; }
done
if [[ -z "$DRY_RUN" ]]; then
    case "$TASK_RUNNER" in
        claude)
            command -v claude >/dev/null || { echo "FATAL: claude CLI not in PATH" >&2; exit 1; }
            ;;
        opencode)
            command -v opencode >/dev/null || { echo "FATAL: TASK_RUNNER=opencode but opencode CLI not in PATH" >&2; exit 1; }
            ;;
        *)
            echo "FATAL: TASK_RUNNER must be claude|opencode; got '$TASK_RUNNER'" >&2
            exit 1
            ;;
    esac
    command -v timeout >/dev/null || { echo "FATAL: GNU timeout missing" >&2; exit 1; }
    if [[ -n "$VALIDATOR_MODEL" ]]; then
        command -v opencode >/dev/null || { echo "FATAL: VALIDATOR_MODEL set but opencode CLI not in PATH" >&2; exit 1; }
    fi
fi

# Helper: contar tasks por status em PROGRESS.md.
# Implementado com awk para evitar bug de pipefail quando grep nao acha match.
count_tasks_with_status() {
    local status="$1"
    awk -v s="$status" '
        /^\| [0-9][0-9][0-9]-[a-z0-9-]+ \|/ {
            split($0, parts, /\|/)
            # parts[1]=before first |, parts[2]=" id ", parts[3]=" phase ", parts[4]=" status "
            gsub(/^[ \t]+|[ \t]+$/, "", parts[4])
            if (parts[4] == s) count++
        }
        END { print count + 0 }
    ' "$PROGRESS_FILE"
}

# Helper: contar tasks PENDING cujas dependencias estao todas DONE.
# PENDING por si so nao significa trabalho elegivel; apos um decision gate STOP,
# tasks futuras podem permanecer PENDING mas depender de uma cadeia BLOCKED.
count_eligible_pending_tasks() {
    awk '
        /^\| [0-9][0-9][0-9]-[a-z0-9-]+ \|/ {
            split($0, parts, /\|/)
            gsub(/^[ \t]+|[ \t]+$/, "", parts[2])
            gsub(/^[ \t]+|[ \t]+$/, "", parts[4])
            gsub(/^[ \t]+|[ \t]+$/, "", parts[7])
            id = parts[2]
            ids[++n] = id
            status[id] = parts[4]
            status[substr(id, 1, 3)] = parts[4]
            depends[id] = parts[7]
        }
        END {
            for (i = 1; i <= n; i++) {
                id = ids[i]
                if (status[id] != "PENDING") continue
                if (depends[id] == "-") {
                    count++
                    continue
                }
                split(depends[id], deps, /,/)
                ok = 1
                for (j in deps) {
                    dep = deps[j]
                    gsub(/^[ \t]+|[ \t]+$/, "", dep)
                    if (status[dep] != "DONE") ok = 0
                }
                if (ok) count++
            }
            print count + 0
        }
    ' "$PROGRESS_FILE"
}

# Helper: imprimir snapshot resumido do PROGRESS
progress_snapshot() {
    local pending done_count failed blocked in_progress
    pending=$(count_tasks_with_status "PENDING")
    done_count=$(count_tasks_with_status "DONE")
    failed=$(count_tasks_with_status "FAILED")
    blocked=$(count_tasks_with_status "BLOCKED")
    in_progress=$(count_tasks_with_status "IN_PROGRESS")
    echo "PENDING=$pending DONE=$done_count FAILED=$failed BLOCKED=$blocked IN_PROGRESS=$in_progress"
}

# Helper: hash do PROTOCOL.md (para detectar tampering durante sessao)
protocol_hash() {
    sha256sum "$PROTOCOL_FILE" | awk '{print $1}'
}

# Helper: hash do PROGRESS.md (para detectar avanco)
progress_hash() {
    sha256sum "$PROGRESS_FILE" | awk '{print $1}'
}

# Helper: lista paths em git status (modificados/criados/deletados/untracked).
# Saida e ordenada e unique para diff posterior.
git_changed_paths() {
    git status -s 2>/dev/null | awk '{print $NF}' | sort -u
}

# Helper: verificar se a iteracao tocou apenas paths permitidos.
# Recebe duas snapshots (PRE e POST de git_changed_paths) e isola os paths que
# apareceram so no POST — esses sao os tocados pela iteracao. Em worktree ja
# sujo (mudancas pre-existentes), nao gera falso positivo.
#
# Args: $1 = arquivo com snapshot PRE, $2 = arquivo com snapshot POST.
verify_iter_allowlist_compliance() {
    local pre_file="$1"
    local post_file="$2"
    local violations=()
    local forbidden_patterns=(
        "frozen_rules/"
        "docs/investment-mandate.md"
        "studies/day_swing_strategy_hunt/"
        "studies/global_factor_tilt_loop/"
        "studies/spy_beater_hunt/"
        "studies/long_term_portfolio/"
        "studies/bestfolio_meta_wf_hunt/"
        "studies/bitcoin_satellite/"
        "app/"
        "backtest/"
    )
    # Paths novos = apareceram no POST mas nao estavam no PRE
    local new_paths
    new_paths=$(comm -13 "$pre_file" "$post_file" 2>/dev/null || true)
    while IFS= read -r path; do
        [[ -z "$path" ]] && continue
        for pat in "${forbidden_patterns[@]}"; do
            if [[ "$path" == "$pat"* ]]; then
                violations+=("$path matches forbidden $pat")
            fi
        done
    done <<< "$new_paths"
    if [[ ${#violations[@]} -gt 0 ]]; then
        echo "ALLOWLIST VIOLATION (apenas mudancas desta iteracao):" >&2
        for v in "${violations[@]}"; do echo "  - $v" >&2; done
        return 1
    fi
    return 0
}

# Helper: detectar diretorio iterations/NNN-slug criado/modificado nesta rodada.
detect_iter_dir() {
    local pre_file="$1"
    local post_file="$2"
    local path
    while IFS= read -r path; do
        [[ -z "$path" ]] && continue
        if [[ "$path" == "$LOOP_DIR"/iterations/[0-9][0-9][0-9]-*/* ]]; then
            echo "${path%/*}"
            return 0
        fi
    done < <(comm -13 "$pre_file" "$post_file" 2>/dev/null || true)
    return 1
}

# Helper: escreve prompt de validacao read-only para GPT-5.5/opencode.
write_validation_prompt() {
    local iter_dir="$1"
    local iter_log="$2"
    local out_file="$3"
    {
        echo "# MyFxBook v4 Blocking Validation"
        echo ""
        echo "Repo: $(pwd)"
        echo "Iteration dir: ${iter_dir:-unknown}"
        echo "Iteration log: $iter_log"
        echo "Progress snapshot: $(progress_snapshot)"
        echo ""
        echo "You are GPT-5.5 acting as a READ-ONLY validator for the last Claude task."
        echo "Do not edit files, do not commit, do not run destructive commands."
        echo "Review the last completed task with code-review mindset: correctness, mandate compliance, tests, and documentation."
        echo "Focus on blockers that should stop the autonomous loop. Non-blocking caveats are allowed."
        echo ""
        echo "Mandatory reads:"
        echo "- CLAUDE.md"
        echo "- $PROTOCOL_FILE"
        echo "- $SPEC_FILE"
        echo "- $PROGRESS_FILE"
        echo "- $TASKS_FILE"
        if [[ -n "$iter_dir" ]]; then
            echo "- $iter_dir/PRE_REG.md"
            echo "- $iter_dir/RESULTS.json"
            echo "- $iter_dir/SUMMARY.md"
            echo "- $iter_dir/run.log"
        fi
        echo ""
        echo "Git status after task:"
        git status --short
        echo ""
        echo "Git diff stat after task:"
        git diff --stat
        echo ""
        echo "Return exactly one verdict line first:"
        echo "- VALIDATION_VERDICT: PROCEED"
        echo "- VALIDATION_VERDICT: STOP"
        echo ""
        echo "Then provide concise findings. Use STOP only for issues that should block the next task."
    } > "$out_file"
}

# Helper: roda validacao bloqueante se configurada.
run_blocking_validator() {
    local iter_dir="$1"
    local iter_log="$2"
    local round="$3"
    local stamp="$4"

    if [[ -z "$VALIDATOR_MODEL" && -z "$VALIDATOR_CMD" ]]; then
        if [[ "$VALIDATOR_REQUIRED" == "1" ]]; then
            echo "=== VALIDATOR_REQUIRED=1 mas VALIDATOR_MODEL/VALIDATOR_CMD nao configurado. Abortando. ===" | tee -a "$RUN_LOG"
            exit 5
        fi
        return 0
    fi

    local validation_dir validation_prompt validation_out
    validation_dir="$iter_dir"
    if [[ -z "$validation_dir" || ! -d "$validation_dir" ]]; then
        validation_dir="$LOG_DIR"
    fi
    validation_prompt="$validation_dir/VALIDATION_PROMPT_round_${round}_${stamp}.md"
    validation_out="$validation_dir/VALIDATION_round_${round}_${stamp}.md"

    write_validation_prompt "$iter_dir" "$iter_log" "$validation_prompt"

    echo "=== Rodando validacao bloqueante (${VALIDATOR_MODEL:-VALIDATOR_CMD}) ===" | tee -a "$RUN_LOG"
    set +e
    if [[ -n "$VALIDATOR_CMD" ]]; then
        timeout "$VALIDATOR_TIMEOUT" bash -lc "$VALIDATOR_CMD" < "$validation_prompt" 2>&1 | tee "$validation_out"
    else
        timeout "$VALIDATOR_TIMEOUT" opencode run \
            --model "$VALIDATOR_MODEL" \
            --dir "$(pwd)" \
            --dangerously-skip-permissions \
            "$(<"$validation_prompt")" 2>&1 | tee "$validation_out"
    fi
    local validator_exit=${PIPESTATUS[0]}
    set -e

    if [[ "$validator_exit" -eq 124 ]]; then
        echo "=== Validacao TIMED OUT (${VALIDATOR_TIMEOUT}s). Abortando loop. ===" | tee -a "$RUN_LOG"
        exit 5
    fi
    if [[ "$validator_exit" -ne 0 ]]; then
        echo "=== Validador saiu com codigo=$validator_exit. Abortando loop. ===" | tee -a "$RUN_LOG"
        exit 5
    fi
    if grep -Eq '^VALIDATION_VERDICT:[[:space:]]*PROCEED[[:space:]]*$' "$validation_out"; then
        echo "=== Validacao PROCEED. Loop pode continuar. ===" | tee -a "$RUN_LOG"
        return 0
    fi
    if grep -Eq '^VALIDATION_VERDICT:[[:space:]]*STOP[[:space:]]*$' "$validation_out"; then
        echo "=== Validacao STOP. Abortando loop para correcao humana/GPT-5.5. ===" | tee -a "$RUN_LOG"
        exit 5
    fi
    echo "=== Validacao sem verdict parseavel. Abortando loop fail-safe. ===" | tee -a "$RUN_LOG"
    exit 5
}

echo "=== myfxbook_v4_redesign loop @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
echo "MAX_ITER=$MAX_ITER ITER_TIMEOUT=${ITER_TIMEOUT}s COOLDOWN=${COOLDOWN}s RUNNER=$TASK_RUNNER CLAUDE_MODEL=$CLAUDE_MODEL OPENCODE_MODEL=$OPENCODE_MODEL" | tee -a "$RUN_LOG"
echo "Run log: $RUN_LOG" | tee -a "$RUN_LOG"
echo "Initial: $(progress_snapshot)" | tee -a "$RUN_LOG"
echo "" | tee -a "$RUN_LOG"

# Stop antecipado: ja terminou?
PENDING_INIT=$(count_tasks_with_status "PENDING")
IN_PROG_INIT=$(count_tasks_with_status "IN_PROGRESS")
FAILED_INIT=$(count_tasks_with_status "FAILED")
ELIGIBLE_INIT=$(count_eligible_pending_tasks)

if [[ "$FAILED_INIT" -gt 0 ]]; then
    echo "=== ${FAILED_INIT} task(s) em FAILED — intervencao humana necessaria. Saindo. ===" | tee -a "$RUN_LOG"
    grep -E "^\| [0-9]{3}-[a-z0-9-]+ \| [^|]+\| FAILED " "$PROGRESS_FILE" | tee -a "$RUN_LOG"
    exit 1
fi

if [[ "$PENDING_INIT" -eq 0 && "$IN_PROG_INIT" -eq 0 ]]; then
    echo "=== Todas tasks DONE/BLOCKED. Loop nada a fazer. ===" | tee -a "$RUN_LOG"
    exit 0
fi

if [[ "$ELIGIBLE_INIT" -eq 0 && "$IN_PROG_INIT" -eq 0 ]]; then
    echo "=== Nenhuma task PENDING elegivel (dependencias DONE). Intervencao humana/decision gate necessaria. Saindo. ===" | tee -a "$RUN_LOG"
    exit 0
fi

# Dry run
if [[ -n "$DRY_RUN" ]]; then
    echo "=== DRY_RUN: prompt que seria enviado ===" | tee -a "$RUN_LOG"
    cat "$PROMPT_FILE" | tee -a "$RUN_LOG"
    exit 0
fi

# Loop principal
for round in $(seq 1 "$MAX_ITER"); do
    STAMP=$(date +%Y%m%d-%H%M%S)
    ITER_LOG="$LOG_DIR/iter_${round}_${STAMP}.log"

    echo "--- round $round/$MAX_ITER (log=$ITER_LOG) @ $(date -Iseconds) ---" | tee -a "$RUN_LOG"
    echo "Before: $(progress_snapshot)" | tee -a "$RUN_LOG"

    # Snapshot PROTOCOL hash + PROGRESS hash antes
    PROTO_HASH_BEFORE=$(protocol_hash)
    PROG_HASH_BEFORE=$(progress_hash)

    # Snapshot de paths sujos antes da iteracao (para diff de allow-list)
    PRE_SNAPSHOT=$(mktemp -t v4_pre_snapshot.XXXXXX)
    POST_SNAPSHOT=$(mktemp -t v4_post_snapshot.XXXXXX)
    trap 'rm -f "$PRE_SNAPSHOT" "$POST_SNAPSHOT"' EXIT
    git_changed_paths > "$PRE_SNAPSHOT"

    # Carregar prompt
    PROMPT=$(cat "$PROMPT_FILE")

    # Spawn sessao limpa
    set +e
    if [[ "$TASK_RUNNER" == "opencode" ]]; then
        timeout "$ITER_TIMEOUT" opencode run \
            --model "$OPENCODE_MODEL" \
            --dir "$(pwd)" \
            --dangerously-skip-permissions \
            "$PROMPT" 2>&1 | tee -a "$ITER_LOG"
    else
        timeout "$ITER_TIMEOUT" claude -p "$PROMPT" \
            --model "$CLAUDE_MODEL" \
            --dangerously-skip-permissions 2>&1 | tee -a "$ITER_LOG"
    fi
    EXIT=${PIPESTATUS[0]}
    set -e

    # Timeout?
    if [[ "$EXIT" -eq 124 ]]; then
        echo "=== iteracao $round TIMED OUT (${ITER_TIMEOUT}s). Saindo. ===" | tee -a "$RUN_LOG"
        exit 124
    fi
    if [[ "$EXIT" -ne 0 ]]; then
        echo "=== iteracao $round saiu com codigo=$EXIT. Saindo. ===" | tee -a "$RUN_LOG"
        exit "$EXIT"
    fi

    # Security: PROTOCOL nao deve ter mudado
    PROTO_HASH_AFTER=$(protocol_hash)
    if [[ "$PROTO_HASH_BEFORE" != "$PROTO_HASH_AFTER" ]]; then
        echo "=== ALERTA: PROTOCOL.md foi modificado durante a sessao. Abortando loop. ===" | tee -a "$RUN_LOG"
        exit 3
    fi

    # PROGRESS deve ter mudado (caso contrario sessao nao avancou)
    PROG_HASH_AFTER=$(progress_hash)
    if [[ "$PROG_HASH_BEFORE" == "$PROG_HASH_AFTER" ]]; then
        echo "=== ALERTA: PROGRESS.md nao mudou — sessao nao avancou. Abortando loop. ===" | tee -a "$RUN_LOG"
        echo "Provavel causa: sessao terminou sem completar checklist do PROTOCOL." | tee -a "$RUN_LOG"
        exit 2
    fi

    # Allow-list compliance: comparar PRE vs POST snapshot
    git_changed_paths > "$POST_SNAPSHOT"
    if ! verify_iter_allowlist_compliance "$PRE_SNAPSHOT" "$POST_SNAPSHOT"; then
        echo "=== ALERTA: sessao tocou paths fora da allow-list (PROTOCOL.md). Abortando loop. ===" | tee -a "$RUN_LOG"
        exit 4
    fi
    echo "After:  $(progress_snapshot)" | tee -a "$RUN_LOG"

    # Stop se algo failed
    FAILED_NOW=$(count_tasks_with_status "FAILED")
    if [[ "$FAILED_NOW" -gt 0 ]]; then
        echo "=== ${FAILED_NOW} task(s) FAILED. Intervencao humana. ===" | tee -a "$RUN_LOG"
        grep -E "^\| [0-9]{3}-[a-z0-9-]+ \| [^|]+\| FAILED " "$PROGRESS_FILE" | tee -a "$RUN_LOG"
        exit 1
    fi

    ITER_DIR=$(detect_iter_dir "$PRE_SNAPSHOT" "$POST_SNAPSHOT" || true)
    run_blocking_validator "$ITER_DIR" "$ITER_LOG" "$round" "$STAMP"

    rm -f "$PRE_SNAPSHOT" "$POST_SNAPSHOT"
    trap - EXIT

    # Stop se nada mais pendente
    PENDING_NOW=$(count_tasks_with_status "PENDING")
    IN_PROG_NOW=$(count_tasks_with_status "IN_PROGRESS")
    ELIGIBLE_NOW=$(count_eligible_pending_tasks)
    if [[ "$PENDING_NOW" -eq 0 && "$IN_PROG_NOW" -eq 0 ]]; then
        echo "" | tee -a "$RUN_LOG"
        echo "=================================================================" | tee -a "$RUN_LOG"
        echo "=== TODAS TASKS DONE/BLOCKED apos iteracao $round @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
        echo "=== Inspect: studies/myfxbook_reverse_engineering/_diagnostics/PIPELINE_V4_FINAL.md ===" | tee -a "$RUN_LOG"
        echo "=================================================================" | tee -a "$RUN_LOG"
        exit 0
    fi
    if [[ "$ELIGIBLE_NOW" -eq 0 && "$IN_PROG_NOW" -eq 0 ]]; then
        echo "" | tee -a "$RUN_LOG"
        echo "=================================================================" | tee -a "$RUN_LOG"
        echo "=== NENHUMA TASK PENDING ELEGIVEL apos iteracao $round @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
        echo "=== Decision gate/intervencao humana necessaria; loop parado limpo. ===" | tee -a "$RUN_LOG"
        echo "=================================================================" | tee -a "$RUN_LOG"
        exit 0
    fi

    if [[ "$round" -lt "$MAX_ITER" ]]; then
        echo "--- cooldown ${COOLDOWN}s antes da proxima sessao ---" | tee -a "$RUN_LOG"
        sleep "$COOLDOWN"
    fi
done

echo "" | tee -a "$RUN_LOG"
echo "=== Atingiu MAX_ITER=$MAX_ITER @ $(date -Iseconds) ===" | tee -a "$RUN_LOG"
echo "Final: $(progress_snapshot)" | tee -a "$RUN_LOG"
echo "Re-rodar com MAX_ITER maior para continuar." | tee -a "$RUN_LOG"
exit 0
