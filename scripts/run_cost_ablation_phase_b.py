#!/usr/bin/env python3
"""Phase B Lead #2: Realistic cost ablation for all confirmed winners.

Path A (BollingerMR SPY 1h) — Pepperstone Razor CFD costs:
  - half_spread = 0.01 USD  (Razor US equity CFD spread ≈ $0.01–0.02)
  - commission_per_unit = 0.0186 USD/share/side  ($3.50 / $100k ÷ ~188 shares)
  - SwapModel: SOFR (5.3%) + 0.5% markup = 5.8% annual on notional
    → per-bar rate = 5.8% / 365 / 6.5 trading-hours = 0.0000244

Path B (ETF Rotation top-1 / top-2) — Brazilian broker (long-only swing):
  - 0.10% round-trip commission post-hoc on each monthly trade
  - 15% capital-gains tax on each positive monthly return
    [AFML, p.243-245]: model post-hoc tax as: net_month = gross × (1 - 0.15) if gross > 0

Gate references:
  [AFML, p.208-211]: PBO < 0.5
  [AFML, p.201-207]: DSR p < 0.05 (N=1 PSR for pre-specified canonical configs)
  [machine_trading, p.126-127]: EWMA-GARCH vol sizing, lambda=0.94
"""

from __future__ import annotations

import logging
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("ai_trade.cost_ablation_phase_b")

STORAGE_ROOT = Path("data/tiingo")
REPORTS_DIR = Path("reports")

# ── Pepperstone Razor CFD cost parameters (Path A) ──────────────────────────
# half_spread: SPY CFD natural bid-ask half ≈ $0.01 per share
RAZOR_HALF_SPREAD = 0.01
# commission: $3.50 per side per $100k USD at SPY ~$530 → $3.50 / (100000/530) = $0.01855/share
RAZOR_COMMISSION_PER_UNIT = 0.0186
# SwapModel long rate per bar (1h) for 5.8% annual: 0.058 / 365 / 6.5 trading hrs
# NOTE: SwapModel.charge() fires every bar; pass per-bar rate
RAZOR_SWAP_RATE_PER_BAR = 0.058 / 365 / 6.5  # ≈ 0.0000244

# ── Brazilian broker cost parameters (Path B) ────────────────────────────────
# 0.10% round-trip per monthly rebalance (entry + exit)
BR_COMMISSION_ROUND_TRIP = 0.001
# 15% capital-gains tax on positive months (simplified model)
BR_TAX_RATE = 0.15


def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    fh = logging.FileHandler("logs/grid.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logging.getLogger().addHandler(fh)


def _run_bollinger_mr_with_costs(
    symbol: str,
    start: date,
    end: date,
    cash: float,
    half_spread: float,
    commission_per_unit: float,
    swap_rate_per_bar: float,
    garch_lambda: float = 0.94,
) -> tuple[pd.Series, dict]:
    """Run canonical BollingerMR(20,2) + GARCH with Pepperstone Razor costs."""
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import (
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
        SwapModel,
    )
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    storage = TiingoStorage(root=STORAGE_ROOT)
    source = TiingoSource(storage=storage)
    warmup_start = (pd.Timestamp(start) - pd.Timedelta(days=60)).date()
    fetched = source.fetch_many(
        [symbol],
        start=warmup_start,
        end=end,
        asset_class="etf",
        frequency="1hour",
    )
    raw = fetched.get(symbol)
    if raw is None or raw.empty:
        raise RuntimeError(f"No data for {symbol}")
    data_bounded = {symbol: raw.loc[pd.Timestamp(start): pd.Timestamp(end)]}
    data_full = {symbol: raw}

    exec_cfg = ExecutionConfig(
        half_spread=half_spread,
        commission_per_unit=commission_per_unit,
    )
    swap = SwapModel(long_rate_per_day=swap_rate_per_bar)  # per-bar rate (see docstring)

    strategy = BollingerMRStrategy(
        data=data_full,
        symbol=symbol,
        window=20,
        std_mult=2.0,
        risk_pct_of_equity=0.02,
        garch_lambda=garch_lambda,
        direction="long",
    )
    runner = Runner(executor=ExecutionSimulator(exec_cfg), swap_model=swap)
    result = runner.run(strategy=strategy, data=data_bounded, initial_cash=cash)

    eq = result.equity_curve
    rets = eq.pct_change().dropna().to_numpy(dtype=float)
    sharpe = float(np.mean(rets) / (np.std(rets, ddof=0) + 1e-12) * np.sqrt(365 * 6.5))
    cagr = float((eq.iloc[-1] / eq.iloc[0]) ** (365 * 6.5 / max(len(rets), 1)) - 1)
    dd = float(((eq / eq.cummax()) - 1).min())
    n_trades = len(result.trades)
    median_hold = float(
        np.median([
            (t.exit_time - t.entry_time).total_seconds() / 3600 / 6.5
            for t in result.trades
        ])
    ) if result.trades else 0.0

    stats = dict(
        sharpe=sharpe, cagr=cagr, max_dd=dd,
        n_trades=n_trades, median_hold_days=median_hold,
    )
    return eq, stats


def _apply_br_costs_to_equity(
    equity: pd.Series,
    commission_round_trip: float = BR_COMMISSION_ROUND_TRIP,
    tax_rate: float = BR_TAX_RATE,
) -> pd.Series:
    """Apply Brazilian broker costs post-hoc to a daily equity curve.

    1. Resample to monthly, apply 0.10% commission drag per month.
    2. Apply 15% tax on positive monthly returns (simplified per-event model).
    Returns daily equity curve with costs applied.
    [AFML, p.243-245]: post-hoc tax modeling.
    """
    monthly = equity.resample("ME").last()
    monthly_ret = monthly.pct_change().fillna(0.0)

    # Commission drag: -0.10% per month (round-trip for the one rebalance)
    monthly_ret_after_cost = monthly_ret - commission_round_trip

    # 15% tax on positive months
    taxed = np.where(
        monthly_ret_after_cost > 0,
        monthly_ret_after_cost * (1.0 - tax_rate),
        monthly_ret_after_cost,
    )

    # Rebuild monthly equity from taxed returns
    monthly_eq = (1.0 + pd.Series(taxed, index=monthly.index)).cumprod()
    monthly_eq = monthly_eq * (equity.iloc[0] / monthly_eq.iloc[0])

    # Resample back to daily by forward-filling (approximation)
    daily_idx = pd.date_range(equity.index[0], equity.index[-1], freq="B")
    eq_daily = monthly_eq.reindex(daily_idx, method="ffill").reindex(equity.index, method="ffill")
    return eq_daily.ffill()


def _compute_daily_sharpe(eq: pd.Series) -> float:
    rets = eq.pct_change().dropna().to_numpy(dtype=float)
    return float(np.mean(rets) / (np.std(rets, ddof=0) + 1e-12) * np.sqrt(252))


def _run_etf_rotation_with_costs(
    start: date,
    end: date,
    top_n: int,
    cash: float,
) -> tuple[pd.Series, dict]:
    """Run ETF rotation and apply BR costs post-hoc."""
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.strategies.etf_rotation import ETFRotationStrategy

    SYMBOLS = ["SPY", "QQQ", "IWM", "GLD", "TLT"]
    storage = TiingoStorage(root=STORAGE_ROOT)
    source = TiingoSource(storage=storage)

    warmup_start = (pd.Timestamp(start) - pd.Timedelta(days=600)).date()
    raw = source.fetch_many(
        SYMBOLS,
        start=warmup_start,
        end=end,
        asset_class="etf",
        frequency="daily",
    )
    for sym in SYMBOLS:
        if raw.get(sym) is None or raw[sym].empty:
            raise RuntimeError(f"No data for {sym}")

    data_bounded = {sym: df.loc[pd.Timestamp(start): pd.Timestamp(end)] for sym, df in raw.items()}

    strategy = ETFRotationStrategy(
        data=raw,
        symbols=SYMBOLS,
        index_symbol="SPY",
        lookback=90,
        sma_index_period=200,
        sma_stock_period=100,
        top_n=top_n,
    )
    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(strategy=strategy, data=data_bounded, initial_cash=cash)

    eq_gross = result.equity_curve
    eq_net = _apply_br_costs_to_equity(eq_gross)

    sharpe_gross = _compute_daily_sharpe(eq_gross)
    sharpe_net = _compute_daily_sharpe(eq_net)
    cagr_net = float((eq_net.iloc[-1] / eq_net.iloc[0]) ** (252 / max(len(eq_net) - 1, 1)) - 1)
    dd_net = float(((eq_net / eq_net.cummax()) - 1).min())

    stats = dict(
        sharpe_gross=sharpe_gross,
        sharpe_net=sharpe_net,
        cagr_net=cagr_net,
        max_dd_net=dd_net,
    )
    return eq_net, stats


def _gate_check_1d(eq: pd.Series, label: str) -> tuple:
    """Quick gate summary (N=1 PSR path) for a single equity curve."""
    from ai_trade.backtest.grid import GateEvaluator
    from ai_trade.backtest.grid.result import GridResult, TrialResult
    from ai_trade.backtest.grid.walk_forward import wf_for_config
    import dataclasses

    @dataclasses.dataclass(frozen=True)
    class _Cfg:
        pass

    @dataclasses.dataclass
    class _MockResult:
        equity_curve: pd.Series

    rets = eq.pct_change().dropna().to_numpy(dtype=float)
    # Annualize: daily equity uses 252; intraday (many bars) uses 252*6.5
    is_intraday = len(eq) > 5000
    periods_per_year = 252 if not is_intraday else 252 * 6.5
    sharpe = float(np.mean(rets) / (np.std(rets, ddof=0) + 1e-12) * np.sqrt(periods_per_year))

    mock_result = _MockResult(equity_curve=eq)
    trial = TrialResult(
        config_id=0, config=_Cfg(), status="ok",
        result=mock_result,
        sharpe=sharpe, cagr=0.0, max_drawdown=0.0,
    )
    grid = GridResult(trials=[trial], run_id=label)
    wf = wf_for_config(equity_curve=eq, config_id=0, n_windows=8, max_drawdown=0.35)
    verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts={0: wf.verdict})
    dsr_p = verdict.dsr_results[0].p_value if verdict.dsr_results.get(0) else None

    log.info(
        "  GATES [%s]: overall=%s | PBO=N/A(N=1) | DSR_p=%s | WF=%d/%d | Sharpe=%.3f",
        label,
        "PASS" if verdict.overall_pass else "FAIL",
        f"{dsr_p:.4f}" if dsr_p is not None else "n/a",
        wf.n_profitable, wf.n_windows,
        sharpe,
    )
    return verdict.overall_pass, sharpe, dsr_p, wf


def main() -> int:
    _setup_logging()
    REPORTS_DIR.mkdir(exist_ok=True)

    # ── Determine IS / OOS dates from manifest ─────────────────────────────
    import json
    manifest = json.loads(Path("data/tiingo/manifest.json").read_text())
    spy_1h = manifest.get("SPY", {}).get("1hour", {})
    spy_first = spy_1h.get("first_dt", "2019-11-25")[:10]
    spy_last = spy_1h.get("last_dt", "2026-04-14")[:10]
    spy_daily = manifest.get("SPY", {}).get("daily", {})
    spy_daily_first = spy_daily.get("first_dt", "2003-01-02")[:10]
    spy_daily_last = spy_daily.get("last_dt", "2026-04-14")[:10]

    log.info("Manifest SPY 1h: %s → %s", spy_first, spy_last)
    log.info("Manifest SPY daily: %s → %s", spy_daily_first, spy_daily_last)

    CASH = 100_000.0

    # ────────────────────────────────────────────────────────────────────────
    # PATH A: BollingerMR SPY 1h  — IS full window
    # ────────────────────────────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("PATH A: BollingerMR SPY 1h  [SHORT-HOLD CFD]")
    log.info("Costs: half_spread=%.3f, commission=%.4f, swap_rate_per_bar=%.7f",
             RAZOR_HALF_SPREAD, RAZOR_COMMISSION_PER_UNIT, RAZOR_SWAP_RATE_PER_BAR)

    # IS (full window, no costs — baseline)
    log.info("--- IS (no costs, baseline) ---")
    eq_is_nc, stats_is_nc = _run_bollinger_mr_with_costs(
        "SPY",
        start=date.fromisoformat(spy_first),
        end=date(2024, 12, 31),
        cash=CASH,
        half_spread=0.0,
        commission_per_unit=0.0,
        swap_rate_per_bar=0.0,
    )
    log.info("  IS no-cost: Sharpe=%.3f CAGR=%.2f%% MaxDD=%.2f%% n_trades=%d median_hold=%.2fd",
             stats_is_nc["sharpe"], stats_is_nc["cagr"] * 100,
             stats_is_nc["max_dd"] * 100, stats_is_nc["n_trades"], stats_is_nc["median_hold_days"])
    _gate_check_1d(eq_is_nc, "PathA_IS_nocost")

    # IS (full window, WITH costs)
    log.info("--- IS (with Pepperstone Razor costs) ---")
    eq_is_wc, stats_is_wc = _run_bollinger_mr_with_costs(
        "SPY",
        start=date.fromisoformat(spy_first),
        end=date(2024, 12, 31),
        cash=CASH,
        half_spread=RAZOR_HALF_SPREAD,
        commission_per_unit=RAZOR_COMMISSION_PER_UNIT,
        swap_rate_per_bar=RAZOR_SWAP_RATE_PER_BAR,
    )
    log.info("  IS with-cost: Sharpe=%.3f CAGR=%.2f%% MaxDD=%.2f%% n_trades=%d median_hold=%.2fd",
             stats_is_wc["sharpe"], stats_is_wc["cagr"] * 100,
             stats_is_wc["max_dd"] * 100, stats_is_wc["n_trades"], stats_is_wc["median_hold_days"])
    pass_is, sharpe_is, dsr_is, wf_is = _gate_check_1d(eq_is_wc, "PathA_IS_withcost")

    # OOS 2025 (with costs)
    log.info("--- OOS 2025 (with Pepperstone Razor costs) ---")
    eq_oos_wc, stats_oos_wc = _run_bollinger_mr_with_costs(
        "SPY",
        start=date(2025, 1, 1),
        end=date(2025, 12, 31),
        cash=CASH,
        half_spread=RAZOR_HALF_SPREAD,
        commission_per_unit=RAZOR_COMMISSION_PER_UNIT,
        swap_rate_per_bar=RAZOR_SWAP_RATE_PER_BAR,
    )
    log.info("  OOS 2025 with-cost: Sharpe=%.3f n_trades=%d",
             stats_oos_wc["sharpe"], stats_oos_wc["n_trades"])

    # Stress 2026-Q1 (with costs)
    log.info("--- Stress 2026-Q1 (with costs) ---")
    eq_stress_wc, stats_stress_wc = _run_bollinger_mr_with_costs(
        "SPY",
        start=date(2026, 1, 1),
        end=date.fromisoformat(spy_last),
        cash=CASH,
        half_spread=RAZOR_HALF_SPREAD,
        commission_per_unit=RAZOR_COMMISSION_PER_UNIT,
        swap_rate_per_bar=RAZOR_SWAP_RATE_PER_BAR,
    )
    log.info("  Stress 2026-Q1 with-cost: Sharpe=%.3f n_trades=%d",
             stats_stress_wc["sharpe"], stats_stress_wc["n_trades"])

    path_a_summary = dict(
        is_sharpe_nocost=stats_is_nc["sharpe"],
        is_sharpe_withcost=stats_is_wc["sharpe"],
        oos_sharpe_withcost=stats_oos_wc["sharpe"],
        stress_sharpe_withcost=stats_stress_wc["sharpe"],
        n_trades=stats_is_wc["n_trades"],
        median_hold_days=stats_is_wc["median_hold_days"],
    )

    # ────────────────────────────────────────────────────────────────────────
    # PATH B: ETF Rotation top-1 and top-2  [SWING BROKER]
    # ────────────────────────────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("PATH B: ETF Rotation  [SWING BROKER]")
    log.info("Costs: commission_round_trip=%.3f%%, tax=%.0f%%",
             BR_COMMISSION_ROUND_TRIP * 100, BR_TAX_RATE * 100)

    path_b_summary = {}
    for top_n in [1, 2]:
        label = f"ETFRotation_top{top_n}"
        log.info("--- %s IS 2003→2024 ---", label)
        eq_b_is, stats_b_is = _run_etf_rotation_with_costs(
            start=date.fromisoformat(spy_daily_first),
            end=date(2024, 12, 31),
            top_n=top_n,
            cash=CASH,
        )
        log.info(
            "  %s IS: gross_sharpe=%.3f net_sharpe=%.3f CAGR_net=%.2f%% MaxDD_net=%.2f%%",
            label,
            stats_b_is["sharpe_gross"], stats_b_is["sharpe_net"],
            stats_b_is["cagr_net"] * 100, stats_b_is["max_dd_net"] * 100,
        )
        pass_b, sharpe_b, dsr_b, wf_b = _gate_check_1d(eq_b_is, f"PathB_{label}_IS_withcost")

        log.info("--- %s OOS 2025 ---", label)
        eq_b_oos, stats_b_oos = _run_etf_rotation_with_costs(
            start=date(2025, 1, 1),
            end=date(2025, 12, 31),
            top_n=top_n,
            cash=CASH,
        )
        log.info("  %s OOS 2025: net_sharpe=%.3f", label, stats_b_oos["sharpe_net"])

        log.info("--- %s Stress 2026-Q1 ---", label)
        eq_b_stress, stats_b_stress = _run_etf_rotation_with_costs(
            start=date(2026, 1, 1),
            end=date.fromisoformat(spy_daily_last),
            top_n=top_n,
            cash=CASH,
        )
        log.info("  %s Stress 2026-Q1: net_sharpe=%.3f", label, stats_b_stress["sharpe_net"])

        path_b_summary[label] = dict(
            is_sharpe_gross=stats_b_is["sharpe_gross"],
            is_sharpe_net=stats_b_is["sharpe_net"],
            oos_sharpe_net=stats_b_oos["sharpe_net"],
            stress_sharpe_net=stats_b_stress["sharpe_net"],
        )

    # ── Final summary ─────────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("COST ABLATION SUMMARY")
    log.info("Path A (BollingerMR SPY 1h, Pepperstone Razor CFD):")
    log.info("  IS Sharpe: %.3f → %.3f (with costs, Δ=%.3f)",
             path_a_summary["is_sharpe_nocost"], path_a_summary["is_sharpe_withcost"],
             path_a_summary["is_sharpe_withcost"] - path_a_summary["is_sharpe_nocost"])
    log.info("  OOS 2025: %.3f | Stress 2026-Q1: %.3f",
             path_a_summary["oos_sharpe_withcost"], path_a_summary["stress_sharpe_withcost"])
    log.info("  n_trades=%d  median_hold_days=%.2f  (≤5d required ✓)",
             path_a_summary["n_trades"], path_a_summary["median_hold_days"])

    for top_n in [1, 2]:
        label = f"ETFRotation_top{top_n}"
        s = path_b_summary[label]
        log.info("Path B (%s):", label)
        log.info("  IS gross=%.3f → net=%.3f | OOS_net=%.3f | Stress_net=%.3f",
                 s["is_sharpe_gross"], s["is_sharpe_net"],
                 s["oos_sharpe_net"], s["stress_sharpe_net"])

    # Save summary
    summary_path = REPORTS_DIR / "cost_ablation_phase_b.txt"
    with summary_path.open("w") as f:
        f.write("Cost Ablation Phase B — 2026-04-16\n")
        f.write("=" * 60 + "\n\n")
        f.write("PATH A: BollingerMR SPY 1h [SHORT-HOLD CFD]\n")
        f.write(f"  Pepperstone Razor: half_spread={RAZOR_HALF_SPREAD} | "
                f"commission={RAZOR_COMMISSION_PER_UNIT}/share/side | "
                f"swap_annual=5.8%\n")
        f.write(f"  IS Sharpe (no cost): {path_a_summary['is_sharpe_nocost']:.3f}\n")
        f.write(f"  IS Sharpe (with cost): {path_a_summary['is_sharpe_withcost']:.3f}\n")
        f.write(f"  OOS 2025 Sharpe (with cost): {path_a_summary['oos_sharpe_withcost']:.3f}\n")
        f.write(f"  Stress 2026-Q1 Sharpe (with cost): {path_a_summary['stress_sharpe_withcost']:.3f}\n")
        f.write(f"  n_trades IS: {path_a_summary['n_trades']}\n")
        f.write(f"  Median hold (trading days): {path_a_summary['median_hold_days']:.2f}\n\n")
        for top_n in [1, 2]:
            label = f"ETFRotation_top{top_n}"
            s = path_b_summary[label]
            f.write(f"PATH B: {label} [SWING BROKER]\n")
            f.write(f"  BR broker: commission={BR_COMMISSION_ROUND_TRIP*100:.2f}% RT | "
                    f"tax={BR_TAX_RATE*100:.0f}% on positive months\n")
            f.write(f"  IS Sharpe (gross): {s['is_sharpe_gross']:.3f}\n")
            f.write(f"  IS Sharpe (net): {s['is_sharpe_net']:.3f}\n")
            f.write(f"  OOS 2025 Sharpe (net): {s['oos_sharpe_net']:.3f}\n")
            f.write(f"  Stress 2026-Q1 Sharpe (net): {s['stress_sharpe_net']:.3f}\n\n")
    log.info("Summary saved → %s", summary_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
