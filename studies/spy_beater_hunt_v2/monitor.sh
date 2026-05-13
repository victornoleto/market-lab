#!/usr/bin/env bash
# Periodic status monitor for spy_beater_hunt_v2.

set -euo pipefail

cd "$(dirname "$0")/../.."

: "${LOOP_PID:=1524252}"
: "${INTERVAL_SECONDS:=300}"
: "${MAX_CHECKS:=144}"

STUDY_DIR="studies/spy_beater_hunt_v2"
MEMORY_FILE="$STUDY_DIR/MEMORY.md"
LOG_DIR="logs/spy_beater_hunt_v2"
MONITOR_LOG="$LOG_DIR/monitor_$(date +%Y%m%d-%H%M%S).md"

mkdir -p "$LOG_DIR"

read_memory_key() {
    local key="$1"
    awk -v k="$key" '
        /^---$/ {f++; if (f==2) exit; next}
        f==1 && $0 ~ "^"k":" {sub("^"k": *", ""); gsub(/^ +| +$/, ""); gsub(/^"/, ""); gsub(/"$/, ""); print; exit}
    ' "$MEMORY_FILE"
}

latest_iter_dir() {
    local path base n max=0 best=""
    shopt -s nullglob
    for path in "$STUDY_DIR"/iterations/[0-9][0-9][0-9]-*/; do
        base=${path%/}
        base=${base##*/}
        n=${base%%-*}
        if [[ "$n" =~ ^[0-9]{3}$ ]] && ((10#$n > max)); then
            max=$((10#$n))
            best=${path%/}
        fi
    done
    shopt -u nullglob
    [[ -n "$best" ]] && printf '%s\n' "$best"
}

snapshot() {
    local now pid_state elapsed total status latest latest_status trials winner latest_dir results summary
    now=$(date -Iseconds)
    if ps -p "$LOOP_PID" >/dev/null 2>&1; then
        pid_state=$(ps -p "$LOOP_PID" -o stat= | tr -d ' ')
        elapsed=$(ps -p "$LOOP_PID" -o etime= | tr -d ' ')
    else
        pid_state="not_running"
        elapsed="n/a"
    fi
    total=$(read_memory_key total_iterations || true)
    status=$(read_memory_key status || true)
    latest=$(read_memory_key latest_iteration || true)
    latest_status=$(read_memory_key latest_status || true)
    trials=$(read_memory_key cumulative_n_trials || true)
    winner=$(read_memory_key latest_winner || true)
    latest_dir=$(latest_iter_dir || true)

    {
        printf '\n## %s\n\n' "$now"
        printf -- '- loop_pid: `%s` (%s, elapsed %s)\n' "$LOOP_PID" "$pid_state" "$elapsed"
        printf -- '- memory: total_iterations `%s`, status `%s`, latest `%s`, latest_status `%s`, cumulative_n_trials `%s`, latest_winner `%s`\n' "$total" "$status" "$latest" "$latest_status" "$trials" "$winner"
        if [[ -n "$latest_dir" ]]; then
            printf -- '- latest_iter_dir: `%s`\n' "$latest_dir"
            results="$latest_dir/RESULTS.json"
            summary="$latest_dir/SUMMARY.md"
            [[ -f "$results" ]] && printf -- '- latest_results: `%s`\n' "$results"
            [[ -f "$summary" ]] && printf -- '- latest_summary: `%s`\n' "$summary"
        fi
    } >> "$MONITOR_LOG"
}

echo "monitor_log=$MONITOR_LOG"
for i in $(seq 1 "$MAX_CHECKS"); do
    snapshot
    if ! ps -p "$LOOP_PID" >/dev/null 2>&1; then
        exit 0
    fi
    if [[ "$i" -lt "$MAX_CHECKS" ]]; then
        sleep "$INTERVAL_SECONDS"
    fi
done
