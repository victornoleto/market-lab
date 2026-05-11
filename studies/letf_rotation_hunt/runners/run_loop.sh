#!/usr/bin/env bash
# Run letf_rotation_hunt iters sequentially.
#
# Scans configs/iter_*.yaml (sorted alphabetically, i.e. by NNN prefix) and
# executes each via python -m studies.letf_rotation_hunt.runners.run_iter.  Skips
# configs whose output dir already exists.  Halts on the first error.
#
# Usage: bash studies/letf_rotation_hunt/runners/run_loop.sh [MAX_ITER]
#   MAX_ITER  max number of iters to run in this invocation (default: 25)
#
# Stdout + stderr are tee'd to logs/letf_hunt.log (append-only).
# Pre-existing iters are moved to configs/processed/ without re-running.
#
# Exit codes:
#   0  loop completed normally (or no configs left)
#   2  an iter failed — loop halted, config NOT moved to processed/

set -euo pipefail

MAX_ITER=${1:-25}
HUNT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HUNT_DIR/../.." && pwd)"
LOG_FILE="$REPO_ROOT/logs/letf_hunt.log"

mkdir -p "$REPO_ROOT/logs"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] letf_hunt loop start; MAX_ITER=$MAX_ITER" | tee -a "$LOG_FILE"

cd "$REPO_ROOT"

for i in $(seq 1 "$MAX_ITER"); do
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] iter cycle $i" | tee -a "$LOG_FILE"

    # Find next iter config (sorted by NNN prefix, take first)
    CONFIG=$(ls -1 "$HUNT_DIR/configs/iter_"*.yaml 2>/dev/null | sort | head -1 || true)
    if [ -z "$CONFIG" ]; then
        echo "[loop] no more configs; exiting" | tee -a "$LOG_FILE"
        break
    fi

    # Extract iter name from config YAML
    ITER_NAME=$(grep -E '^iter:' "$CONFIG" | sed 's/iter: *//;s/"//g;s/'"'"'//g' | tr -d '[:space:]')
    if [ -z "$ITER_NAME" ]; then
        echo "[loop] ERROR: could not parse iter: field from $CONFIG" | tee -a "$LOG_FILE"
        exit 2
    fi

    ITER_DIR="$HUNT_DIR/iterations/$ITER_NAME"
    if [ -d "$ITER_DIR" ]; then
        echo "[loop] iter $ITER_NAME already exists; moving config to processed/" | tee -a "$LOG_FILE"
        mkdir -p "$HUNT_DIR/configs/processed"
        mv "$CONFIG" "$HUNT_DIR/configs/processed/"
        continue
    fi

    echo "[loop] running $ITER_NAME from $CONFIG" | tee -a "$LOG_FILE"

    # Run iter; pipe output to log; capture exit code separately (pipefail
    # would catch the pipe failure but we want the python exit code)
    set +e
    python -m studies.letf_rotation_hunt.runners.run_iter \
        --iter "$ITER_NAME" \
        --config "$CONFIG" \
        2>&1 | tee -a "$LOG_FILE"
    ITER_RC=${PIPESTATUS[0]}
    set -e

    if [ "$ITER_RC" -ne 0 ]; then
        echo "[loop] iter $ITER_NAME FAILED (rc=$ITER_RC); halting loop" | tee -a "$LOG_FILE"
        exit 2
    fi

    mkdir -p "$HUNT_DIR/configs/processed"
    mv "$CONFIG" "$HUNT_DIR/configs/processed/"

    echo "[loop] iter $ITER_NAME done" | tee -a "$LOG_FILE"
done

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] letf_hunt loop end" | tee -a "$LOG_FILE"
