#!/usr/bin/env python3
"""Phase B Lead #4 — Cross-asset transport.

Tests whether the two confirmed winners replicate on related assets:
  1. ETFRotation (top-1): expanded 8-ETF universe (adds XLK, XLF, EEM)
  2. BollingerMR_GARCH: 1h transport on XLF (untested financial-sector ETF)

For BollingerMR, all other sector ETFs (QQQ, IWM, XLK, XLE, GLD, EEM,
DIA, TLT) have already been tested and failed IS or OOS 2025 (see Dead ends).
XLF is the final untested hourly ETF in the manifest.

Gating protocol (same as IS): N=1 PSR p<0.05 + WF>=6/8 for daily;
WF>=4/4 for 1h (shorter IS window).

Citations:
  [stocks_on_the_move, p.81] — ranking signal
  [stocks_on_the_move, p.66-67] — regime filter
  [advances_fin_ml, p.208-211] — DSR / PSR gate

Usage:
    .venv/bin/python scripts/run_cross_asset_transport_phase_b.py
"""

from __future__ import annotations

import dataclasses
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

LOG = logging.getLogger("ai_trade.transport")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/grid.log", mode="a"),
    ],
)

IS_START = date(2005, 1, 3)
IS_END   = date(2024, 12, 31)
OOS_START = date(2025, 1, 1)
OOS_END   = date(2025, 12, 31)
STRESS_START = date(2026, 1, 1)
STRESS_END   = date(2026, 4, 14)
WARMUP_DAYS = 500
DATA_ROOT = Path("data/tiingo")

# Universe variants for ETFRotation transport
UNIVERSES = {
    "original_5": ["SPY", "QQQ", "IWM", "GLD", "TLT"],            # winner baseline
    "expanded_8": ["SPY", "QQQ", "IWM", "GLD", "TLT", "XLK", "XLF", "EEM"],
}


def _sharpe_daily(eq: pd.Series) -> float:
    rets = eq.pct_change().dropna().to_numpy(dtype=float)
    return float(np.mean(rets) / (np.std(rets, ddof=0) + 1e-12) * np.sqrt(252))


def _sharpe_hourly(eq: pd.Series) -> float:
    rets = eq.pct_change().dropna().to_numpy(dtype=float)
    return float(np.mean(rets) / (np.std(rets, ddof=0) + 1e-12) * np.sqrt(252 * 7))


def _run_rotation(symbols: list[str], start: date, end: date, label: str) -> dict:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.grid import GateEvaluator
    from ai_trade.backtest.grid.result import GridResult, TrialResult
    from ai_trade.backtest.grid.walk_forward import wf_for_config
    from ai_trade.backtest.strategies.etf_rotation import ETFRotationStrategy

    src = TiingoSource(storage=TiingoStorage(root=DATA_ROOT))
    fetch_start = start - timedelta(days=WARMUP_DAYS)
    index_sym = "SPY"  # always SPY for regime

    raw = src.fetch_many(symbols, fetch_start, end, asset_class="etf", frequency="daily")
    missing = [s for s in symbols if s not in raw or raw[s].empty]
    if missing:
        LOG.warning("[%s] missing: %s — skip", label, missing)
        return {"label": label, "sharpe": float("nan"), "gate_pass": False}

    data_full = {s: raw[s] for s in symbols}
    data_bounded = {s: df.loc[pd.Timestamp(start): pd.Timestamp(end)]
                    for s, df in data_full.items()}
    n_bars = len(data_bounded[index_sym])

    strategy = ETFRotationStrategy(
        data=data_full, symbols=symbols, index_symbol=index_sym,
        lookback=90, sma_index_period=200, sma_stock_period=100, top_n=1,
    )

    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(strategy=strategy, data=data_bounded, initial_cash=100_000.0)
    if result is None:
        LOG.error("[%s] backtest returned None", label)
        return {"label": label, "sharpe": float("nan"), "gate_pass": False}

    eq = result.equity_curve
    sharpe = _sharpe_daily(eq)
    cagr = float((eq.iloc[-1] / eq.iloc[0]) ** (252 / max(len(eq) - 1, 1)) - 1)
    dd = float(((eq / eq.cummax()) - 1).min())

    # Gates (only for IS)
    gate_pass = None
    wf_str = "n/a"
    dsr_p = None
    if start == IS_START:
        @dataclasses.dataclass(frozen=True)
        class _Cfg:
            pass
        trial = TrialResult(config_id=0, config=_Cfg(), status="ok",
                            result=result, sharpe=sharpe, cagr=cagr, max_drawdown=abs(dd))
        grid = GridResult(trials=[trial], run_id=label)
        wf = wf_for_config(equity_curve=eq, config_id=0, n_windows=8, max_drawdown=0.35)
        verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts={0: wf.verdict})
        gate_pass = verdict.overall_pass
        wf_str = f"{wf.n_profitable}/{wf.n_windows}"
        if verdict.dsr_results.get(0):
            dsr_p = verdict.dsr_results[0].p_value

    LOG.info("[%s] n=%d Sharpe=%.3f CAGR=%.1f%% MaxDD=%.1f%% WF=%s DSR_p=%s gate=%s",
             label, n_bars, sharpe, cagr * 100, dd * 100, wf_str,
             f"{dsr_p:.4f}" if dsr_p is not None else "n/a", gate_pass)

    return {"label": label, "n_bars": n_bars, "sharpe": sharpe, "cagr": cagr,
            "max_dd": dd, "wf": wf_str, "dsr_p": dsr_p, "gate_pass": gate_pass}


def _run_bollinger_xlf() -> None:
    """BollingerMR canonical (20,2) + GARCH on XLF 1h IS+OOS+Stress."""
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.grid import GateEvaluator
    from ai_trade.backtest.grid.result import GridResult, TrialResult
    from ai_trade.backtest.grid.walk_forward import wf_for_config
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    # XLF 1h manifest: 2020-04-15 → 2026-04-14
    xlf_full_start = date(2020, 4, 15)
    xlf_full_end   = date(2026, 4, 14)
    xlf_is_end     = date(2024, 12, 31)
    xlf_oos_start  = date(2025, 1, 1)
    xlf_oos_end    = date(2025, 12, 31)
    xlf_str_start  = date(2026, 1, 1)

    src = TiingoSource(storage=TiingoStorage(root=DATA_ROOT))
    fetch_start = xlf_full_start - timedelta(days=30)
    raw = src.fetch_many(["XLF"], fetch_start, xlf_full_end,
                         asset_class="etf", frequency="1hour")

    if "XLF" not in raw or raw["XLF"].empty:
        LOG.error("[XLF 1h] no data in manifest — skip")
        return

    df_full = raw["XLF"]
    LOG.info("[XLF 1h] total bars in cache: %d  [%s → %s]",
             len(df_full), df_full.index[0].date(), df_full.index[-1].date())

    periods = [
        ("IS",     xlf_full_start, xlf_is_end),
        ("OOS",    xlf_oos_start,  xlf_oos_end),
        ("Stress", xlf_str_start,  xlf_full_end),
    ]

    sharpes = {}
    is_result = None
    is_eq = None

    for pname, ps, pe in periods:
        data_bounded = {"XLF": df_full.loc[pd.Timestamp(ps): pd.Timestamp(pe)]}
        n = len(data_bounded["XLF"])
        strategy = BollingerMRStrategy(
            data={"XLF": df_full},  # full data for indicator warmup
            symbol="XLF", window=20, std_mult=2.0,
            garch_lambda=0.94, risk_pct_of_equity=0.95,
        )
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        result = runner.run(strategy=strategy, data=data_bounded, initial_cash=100_000.0)
        if result is None:
            LOG.warning("[XLF 1h %s] no result", pname)
            sharpes[pname] = float("nan")
            continue
        eq = result.equity_curve
        sh = _sharpe_hourly(eq)
        sharpes[pname] = sh
        LOG.info("[XLF 1h %s] n=%d Sharpe=%.3f", pname, n, sh)
        if pname == "IS":
            is_result = result
            is_eq = eq

    # IS gates
    if is_result is not None and is_eq is not None:
        sh_is = sharpes.get("IS", float("nan"))
        cagr_is = float((is_eq.iloc[-1] / is_eq.iloc[0]) ** (252 * 7 / max(len(is_eq) - 1, 1)) - 1)
        dd_is = float(((is_eq / is_eq.cummax()) - 1).min())

        @dataclasses.dataclass(frozen=True)
        class _Cfg:
            pass

        trial = TrialResult(config_id=0, config=_Cfg(), status="ok",
                            result=is_result, sharpe=sh_is, cagr=cagr_is, max_drawdown=abs(dd_is))
        grid = GridResult(trials=[trial], run_id="BollingerMR_XLF_1h")
        wf = wf_for_config(equity_curve=is_eq, config_id=0, n_windows=4, max_drawdown=0.25)
        verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts={0: wf.verdict})
        dsr_p = None
        if verdict.dsr_results.get(0):
            dsr_p = verdict.dsr_results[0].p_value
        LOG.info(
            "[XLF 1h IS gates] Sharpe=%.3f WF=%d/%d DSR_p=%s gate=%s",
            sh_is, wf.n_profitable, wf.n_windows,
            f"{dsr_p:.4f}" if dsr_p is not None else "n/a",
            verdict.overall_pass,
        )

    LOG.info("[XLF 1h] SUMMARY: IS=%.3f OOS=%.3f Stress=%.3f",
             sharpes.get("IS", float("nan")),
             sharpes.get("OOS", float("nan")),
             sharpes.get("Stress", float("nan")))


def main() -> int:
    LOG.info("=== Phase B Lead #4: Cross-asset transport ===")

    # --- ETFRotation universe transport ---
    for uname, symbols in UNIVERSES.items():
        LOG.info("--- ETFRotation universe=%s ---", uname)
        for ps, pe, label_suffix in [
            (IS_START, IS_END, "IS"),
            (OOS_START, OOS_END, "OOS"),
            (STRESS_START, STRESS_END, "Stress"),
        ]:
            _run_rotation(symbols, ps, pe, f"ETFRotation_{uname}_{label_suffix}")

    # --- BollingerMR XLF 1h ---
    LOG.info("--- BollingerMR XLF 1h transport ---")
    _run_bollinger_xlf()

    LOG.info("=== Phase B Lead #4 complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
