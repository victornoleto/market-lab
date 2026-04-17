#!/usr/bin/env python3
"""Phase B Lead #5 — Cross-strategy correlation.

Checks daily PnL correlation between the two confirmed winners on
their overlapping IS period (2019-12-02 → 2024-12-31, ~5y):
  - BollingerMR_GARCH SPY 1h (Path A)
  - ETFRotation_top1 daily (Path B)

If ρ > 0.7, treat as 1 edge × N assets (no portfolio diversification gain).
If ρ ≤ 0.7, strategies are sufficiently independent for portfolio use.

Citations:
  [advances_fin_ml, ch.4] — strategy independence / portfolio benefit
  [machine_trading, p.142-143] — correlation threshold for portfolio sizing

Usage:
    .venv/bin/python scripts/run_cross_strategy_correlation_phase_b.py
"""

from __future__ import annotations

import logging
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

LOG = logging.getLogger("ai_trade.correlation")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/grid.log", mode="a"),
    ],
)

# Overlap period: BollingerMR 1h starts 2019-11-25, ETF daily starts 2003-01-02
# Use 2019-12-02 → 2024-12-31 (BollingerMR canonical IS window)
OVERLAP_START = date(2019, 12, 2)
OVERLAP_END   = date(2024, 12, 31)
WARMUP_DAYS   = 500
DATA_ROOT     = Path("data/tiingo")

ETF_SYMBOLS   = ["SPY", "QQQ", "IWM", "GLD", "TLT"]


def _run_bollinger_mr(start: date, end: date) -> pd.Series:
    """Return daily equity curve for BollingerMR SPY 1h over [start, end]."""
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    src = TiingoSource(storage=TiingoStorage(root=DATA_ROOT))
    fetch_start = start - timedelta(days=30)
    raw = src.fetch_many(["SPY"], fetch_start, end,
                         asset_class="etf", frequency="1hour")
    df_full = raw["SPY"]
    data_bounded = {"SPY": df_full.loc[pd.Timestamp(start): pd.Timestamp(end)]}

    strategy = BollingerMRStrategy(
        data={"SPY": df_full}, symbol="SPY",
        window=20, std_mult=2.0, garch_lambda=0.94, risk_pct_of_equity=0.95,
    )
    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(strategy=strategy, data=data_bounded, initial_cash=100_000.0)
    eq = result.equity_curve  # type: ignore[union-attr]

    # Resample hourly equity to daily (close of last bar of each day)
    eq.index = pd.to_datetime(eq.index)
    daily_eq = eq.resample("D").last().dropna()
    return daily_eq


def _run_etf_rotation(start: date, end: date) -> pd.Series:
    """Return daily equity curve for ETFRotation top-1 over [start, end]."""
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.strategies.etf_rotation import ETFRotationStrategy

    src = TiingoSource(storage=TiingoStorage(root=DATA_ROOT))
    fetch_start = start - timedelta(days=WARMUP_DAYS)
    raw = src.fetch_many(ETF_SYMBOLS, fetch_start, end,
                         asset_class="etf", frequency="daily")
    data_full = {s: raw[s] for s in ETF_SYMBOLS}
    data_bounded = {s: df.loc[pd.Timestamp(start): pd.Timestamp(end)]
                    for s, df in data_full.items()}

    strategy = ETFRotationStrategy(
        data=data_full, symbols=ETF_SYMBOLS, index_symbol="SPY",
        lookback=90, sma_index_period=200, sma_stock_period=100, top_n=1,
    )
    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(strategy=strategy, data=data_bounded, initial_cash=100_000.0)
    eq = result.equity_curve  # type: ignore[union-attr]
    eq.index = pd.to_datetime(eq.index)
    return eq


def main() -> int:
    LOG.info("=== Phase B Lead #5: Cross-strategy correlation ===")
    LOG.info("Overlap window: %s → %s", OVERLAP_START, OVERLAP_END)

    LOG.info("Running BollingerMR SPY 1h …")
    eq_bmr = _run_bollinger_mr(OVERLAP_START, OVERLAP_END)

    LOG.info("Running ETFRotation top-1 daily …")
    eq_etf = _run_etf_rotation(OVERLAP_START, OVERLAP_END)

    # Daily returns
    ret_bmr = eq_bmr.pct_change().dropna()
    ret_etf = eq_etf.pct_change().dropna()

    # Align on common trading days
    common = ret_bmr.index.intersection(ret_etf.index)
    r1 = ret_bmr.loc[common]
    r2 = ret_etf.loc[common]

    if len(common) < 30:
        LOG.error("Insufficient overlap: %d common days", len(common))
        return 1

    corr = float(r1.corr(r2))
    LOG.info("Common days: %d  Pearson ρ = %.4f", len(common), corr)

    # Sharpe per strategy (daily annualized)
    sh_bmr = float(np.mean(r1) / (np.std(r1, ddof=0) + 1e-12) * np.sqrt(252))
    sh_etf = float(np.mean(r2) / (np.std(r2, ddof=0) + 1e-12) * np.sqrt(252))
    LOG.info("Sharpe BMR=%.3f  ETF=%.3f  (on daily common return series)", sh_bmr, sh_etf)

    # Portfolio blend (50/50) Sharpe
    r_blend = (r1 + r2) / 2.0
    sh_blend = float(np.mean(r_blend) / (np.std(r_blend, ddof=0) + 1e-12) * np.sqrt(252))
    LOG.info("50/50 blend Sharpe=%.3f", sh_blend)

    threshold = 0.7
    if corr > threshold:
        verdict = f"CORRELATED (ρ={corr:.3f} > {threshold}) — treat as 1 edge, no portfolio diversification gain"
    else:
        verdict = f"INDEPENDENT (ρ={corr:.3f} ≤ {threshold}) — strategies provide genuine portfolio diversification"

    LOG.info("=== VERDICT: %s ===", verdict)
    LOG.info("=== Phase B Lead #5 complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
