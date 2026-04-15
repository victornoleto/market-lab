#!/usr/bin/env bash
# Run Ehlers BP Swing grid across a curated basket of assets.
#
# Each asset gets its own grid_ehlers_<timestamp>/ under reports/. After all
# runs finish, parse the per-run diagnostic.md to build
# reports/ehlers_multi_asset_summary.md (Reddit-post material).
#
# Sequential by design: TiingoStorage uses single-writer manifests.
# Uses the canonical bulk storage at data/tiingo (safe now that the
# bulk download has completed — see manifest with ~1660 tickers).
#
# Usage:
#   scripts/run_ehlers_multi_asset.sh                 # full basket
#   scripts/run_ehlers_multi_asset.sh QQQ SLV TLT     # subset
set -euo pipefail

cd "$(dirname "$0")/.."

LOG="logs/ehlers_multi_asset_$(date +%Y%m%d-%H%M).log"
mkdir -p logs reports

# Asset basket: symbol|asset_class|start|end|rationale
# Windows chosen to start at or after each instrument's listing date.
read -r -d '' BASKET <<'EOF' || true
SPY|etf|2005-01-01|2023-12-31|baseline equity index (re-run with longer window)
QQQ|etf|2005-01-01|2023-12-31|tech-heavy index, more trending than SPY
IWM|etf|2005-01-01|2023-12-31|small caps, higher vol
EFA|etf|2005-01-01|2023-12-31|developed ex-US
EEM|etf|2005-01-01|2023-12-31|emerging markets, cyclical
GLD|etf|2005-01-01|2023-12-31|gold, commodity cycle
SLV|etf|2007-01-01|2023-12-31|silver, commodity cycle
USO|etf|2007-01-01|2023-12-31|oil, strong cycles
DBA|etf|2008-01-01|2023-12-31|agriculture commodity
TLT|etf|2003-01-01|2023-12-31|long bonds, rate cycle
XLE|etf|2005-01-01|2023-12-31|energy sector cycles
XLU|etf|2005-01-01|2023-12-31|utilities, rate-sensitive
XLF|etf|2005-01-01|2023-12-31|financials
XLK|etf|2005-01-01|2023-12-31|tech sector
VXX|etf|2010-01-01|2023-12-31|volatility ETF, mean-reverting
eurusd|forex|2014-01-01|2023-12-31|range-bound major FX (Tiingo FX format = lowercase)
usdjpy|forex|2014-01-01|2023-12-31|carry trade FX
gbpusd|forex|2014-01-01|2023-12-31|volatile cross
btcusd|crypto|2017-01-01|2023-12-31|bitcoin, extreme cycles
ethusd|crypto|2017-01-01|2023-12-31|ethereum
EOF

# Optional ticker filter from CLI args.
FILTER="${*:-}"

echo "=== Ehlers multi-asset run @ $(date -Iseconds) ===" | tee "$LOG"
echo "Storage: data/tiingo (canonical bulk)" | tee -a "$LOG"
echo "" | tee -a "$LOG"

declare -A RESULTS

while IFS='|' read -r SYMBOL ASSET_CLASS START END RATIONALE; do
    [[ -z "${SYMBOL:-}" ]] && continue
    if [[ -n "$FILTER" ]] && ! echo " $FILTER " | grep -qi " $SYMBOL "; then
        continue
    fi

    echo "--- $SYMBOL ($ASSET_CLASS) [$START..$END] — $RATIONALE ---" | tee -a "$LOG"
    # Per-asset run-id avoids collisions when multiple runs finish in the
    # same minute (default run_id is grid_ehlers_<YYYYMMDD-HHMM>).
    SAFE_SYM=$(echo "$SYMBOL" | tr '/' '_' | tr '[:upper:]' '[:lower:]')
    RUN_ID="grid_ehlers_${SAFE_SYM}_$(date +%Y%m%d-%H%M%S)"
    set +e
    .venv/bin/python scripts/run_grid_ehlers.py \
        --data-source tiingo \
        --symbol "$SYMBOL" \
        --asset-class "$ASSET_CLASS" \
        --storage-root data/tiingo \
        --start "$START" --end "$END" \
        --cash 100000 \
        --output-dir reports/ \
        --run-id "$RUN_ID" \
        --n-jobs 4 2>&1 | tee -a "$LOG" | tail -5
    EXIT=$?
    set -e

    case $EXIT in
        0) RESULTS[$SYMBOL]="PASS" ;;
        2) RESULTS[$SYMBOL]="FAIL" ;;
        *) RESULTS[$SYMBOL]="ERROR(exit=$EXIT)" ;;
    esac
    echo "" | tee -a "$LOG"
done <<< "$BASKET"

echo "=== Done @ $(date -Iseconds) ===" | tee -a "$LOG"
echo "" | tee -a "$LOG"
for k in "${!RESULTS[@]}"; do
    echo "$k: ${RESULTS[$k]}" | tee -a "$LOG"
done

echo ""
echo "Log: $LOG"
echo "Reports under: reports/grid_ehlers_*"
echo ""
echo "Next: run scripts/build_ehlers_summary.py to consolidate diagnostics."
