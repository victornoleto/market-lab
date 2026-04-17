#!/usr/bin/env python3
"""Phase B Lead #7 — GARCH/vol-sized variant for ETFRotation.

Tests whether vol-sizing (constant-vol targeting [machine_trading, p.126-127])
improves the ETFRotation monthly winner over equal-weight baseline.

Canonical params: top_n=1, lookback=90, sma_index=200, sma_stock=100.
Vol-sizing params: target_vol=0.15, vol_window=20, cap=1.0 (no leverage).

Runs: IS (2003-01-02 → 2024-12-31), OOS (2025), Stress (2026-Q1).
"""

from __future__ import annotations

import dataclasses
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("ai_trade.vol_sizing_etf_rotation")

SYMBOLS = ["SPY", "QQQ", "IWM", "GLD", "TLT"]
INDEX_SYMBOL = "SPY"
WARMUP_DAYS = 500

IS_START = date(2003, 1, 2)
IS_END = date(2024, 12, 31)
OOS_START = date(2025, 1, 1)
OOS_END = date(2025, 12, 31)
STRESS_START = date(2026, 1, 1)
STRESS_END = date(2026, 4, 15)


def _run_period(
    data_full: dict,
    period_start: date,
    period_end: date,
    vol_sizing: bool = False,
    target_vol: float = 0.15,
    vol_window: int = 20,
    cash: float = 100_000.0,
) -> dict:
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.grid import GateEvaluator
    from ai_trade.backtest.grid.result import GridResult, TrialResult
    from ai_trade.backtest.grid.walk_forward import wf_for_config
    from ai_trade.backtest.strategies.etf_rotation import ETFRotationStrategy

    data_bounded = {
        sym: df.loc[pd.Timestamp(period_start): pd.Timestamp(period_end)]
        for sym, df in data_full.items()
    }

    strategy = ETFRotationStrategy(
        data=data_full,
        symbols=SYMBOLS,
        index_symbol=INDEX_SYMBOL,
        lookback=90,
        sma_index_period=200,
        sma_stock_period=100,
        top_n=1,
        vol_sizing=vol_sizing,
        target_vol=target_vol,
        vol_window=vol_window,
    )

    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(strategy=strategy, data=data_bounded, initial_cash=cash)
    if result is None:
        return {"error": "no result"}

    eq = result.equity_curve
    rets = eq.pct_change().dropna().to_numpy(dtype=float)
    sharpe = float(np.mean(rets) / (np.std(rets, ddof=0) + 1e-12) * np.sqrt(252))
    cagr = float((eq.iloc[-1] / eq.iloc[0]) ** (252 / max(len(rets), 1)) - 1)
    dd = float(((eq / eq.cummax()) - 1).min())

    return {"sharpe": sharpe, "cagr": cagr, "max_dd": dd, "equity_curve": eq, "result": result}


def _gates(equity_curve: pd.Series, n_windows: int = 8) -> dict:
    from ai_trade.backtest.grid import GateEvaluator
    from ai_trade.backtest.grid.result import GridResult, TrialResult
    from ai_trade.backtest.grid.walk_forward import wf_for_config

    rets = equity_curve.pct_change().dropna().to_numpy(dtype=float)
    sharpe = float(np.mean(rets) / (np.std(rets, ddof=0) + 1e-12) * np.sqrt(252))
    cagr = float((equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (252 / max(len(rets), 1)) - 1)
    dd = float(((equity_curve / equity_curve.cummax()) - 1).min())

    @dataclasses.dataclass(frozen=True)
    class _Cfg:
        pass

    trial = TrialResult(config_id=0, config=_Cfg(), status="ok",
                        result=None, sharpe=sharpe, cagr=cagr, max_drawdown=abs(dd))

    class _MockResult:
        pass
    mock = _MockResult()
    mock.equity_curve = equity_curve  # type: ignore[attr-defined]

    trial = TrialResult(config_id=0, config=_Cfg(), status="ok",
                        result=mock, sharpe=sharpe, cagr=cagr, max_drawdown=abs(dd))
    grid = GridResult(trials=[trial], run_id="vol_sizing_gates")

    wf = wf_for_config(equity_curve=equity_curve, config_id=0, n_windows=n_windows, max_drawdown=0.35)
    verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts={0: wf.verdict})

    dsr_p = None
    if verdict.dsr_results.get(0):
        dsr_p = verdict.dsr_results[0].p_value

    return {
        "sharpe": sharpe,
        "cagr": cagr,
        "max_dd": dd,
        "dsr_p": dsr_p,
        "wf": f"{wf.n_profitable}/{wf.n_windows}",
        "wf_pass": wf.verdict == "PASS",
        "dsr_pass": dsr_p is not None and dsr_p < 0.05,
        "overall_pass": verdict.overall_pass,
    }


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage

    src = TiingoSource(storage=TiingoStorage(root=Path("data/tiingo")))
    fetch_start = IS_START - timedelta(days=WARMUP_DAYS)
    log.info("Fetching %s from %s to %s (daily)", SYMBOLS, fetch_start, STRESS_END)

    raw = src.fetch_many(SYMBOLS, fetch_start, STRESS_END, asset_class="etf", frequency="daily")
    missing = [s for s in SYMBOLS if s not in raw or raw[s].empty]
    if missing:
        log.error("No data for %s — abort", missing)
        return 1

    data_full = {sym: raw[sym] for sym in SYMBOLS}
    log.info("Data loaded. Running IS baseline (canonical) ...")

    # --- IS canonical (baseline, no vol-sizing) ---
    base_is = _run_period(data_full, IS_START, IS_END, vol_sizing=False)
    base_is_gates = _gates(base_is["equity_curve"])
    log.info("IS canonical: Sharpe=%.3f CAGR=%.2f%% MaxDD=%.2f%% DSR_p=%s WF=%s PASS=%s",
             base_is["sharpe"], base_is["cagr"] * 100, base_is["max_dd"] * 100,
             f"{base_is_gates['dsr_p']:.4f}" if base_is_gates["dsr_p"] else "n/a",
             base_is_gates["wf"], base_is_gates["overall_pass"])

    # --- IS vol-sized ---
    log.info("Running IS vol-sized (target_vol=0.15, window=20) ...")
    vs_is = _run_period(data_full, IS_START, IS_END, vol_sizing=True, target_vol=0.15, vol_window=20)
    vs_is_gates = _gates(vs_is["equity_curve"])
    log.info("IS vol-sized: Sharpe=%.3f CAGR=%.2f%% MaxDD=%.2f%% DSR_p=%s WF=%s PASS=%s",
             vs_is["sharpe"], vs_is["cagr"] * 100, vs_is["max_dd"] * 100,
             f"{vs_is_gates['dsr_p']:.4f}" if vs_is_gates["dsr_p"] else "n/a",
             vs_is_gates["wf"], vs_is_gates["overall_pass"])

    # --- OOS & Stress: both variants ---
    for label, vs in [("canonical", False), ("vol-sized", True)]:
        oos = _run_period(data_full, OOS_START, OOS_END, vol_sizing=vs)
        stress = _run_period(data_full, STRESS_START, STRESS_END, vol_sizing=vs)
        log.info("OOS 2025 %s: Sharpe=%.3f CAGR=%.2f%% MaxDD=%.2f%%",
                 label, oos["sharpe"], oos["cagr"] * 100, oos["max_dd"] * 100)
        log.info("Stress 2026-Q1 %s: Sharpe=%.3f CAGR=%.2f%% MaxDD=%.2f%%",
                 label, stress["sharpe"], stress["cagr"] * 100, stress["max_dd"] * 100)

    # --- Summary ---
    print("\n=== Vol-sizing ETFRotation Phase B Lead #7 Summary ===")
    base_dsr_str = f"{base_is_gates['dsr_p']:.4f}" if base_is_gates["dsr_p"] else "n/a"
    vs_dsr_str = f"{vs_is_gates['dsr_p']:.4f}" if vs_is_gates["dsr_p"] else "n/a"
    print(f"IS canonical:  Sharpe={base_is['sharpe']:.3f}  WF={base_is_gates['wf']}  DSR_p={base_dsr_str}  MaxDD={base_is['max_dd']*100:.1f}%")
    print(f"IS vol-sized:  Sharpe={vs_is['sharpe']:.3f}  WF={vs_is_gates['wf']}  DSR_p={vs_dsr_str}  MaxDD={vs_is['max_dd']*100:.1f}%")
    delta = vs_is["sharpe"] - base_is["sharpe"]
    print(f"Delta Sharpe: {delta:+.3f} ({'IMPROVEMENT' if delta > 0.05 else 'NEUTRAL' if abs(delta) <= 0.05 else 'DEGRADATION'})")
    print("Vol-sizing gates pass:", vs_is_gates["overall_pass"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
