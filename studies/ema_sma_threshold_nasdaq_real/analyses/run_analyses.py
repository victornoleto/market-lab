"""Run rolling-window analyses on the NASDAQ-real study."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from ai_trade.backtest.grid.real_etf_analyses import run_rolling_windows_analysis
from ai_trade.backtest.grid.real_etf_regime_runner import NDX_MARKET

STUDY_DIR = Path(__file__).parent.parent


def main() -> int:
    logger = logging.getLogger("ndx_real_analyses")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(sh)

    run_rolling_windows_analysis(
        study_dir=STUDY_DIR, market=NDX_MARKET,
        windows=(3, 5, 7, 10), stride_years=0.5, log=logger,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
