"""Plot the Phase 3.5a-V2 winner (gayed_ema100_L2_off_gld) equity curve
versus SPY buy&hold, with a drawdown sub-panel and regime-off shading.

Inputs
------
reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld_daily_returns.parquet
data/tiingo/daily/prices/SPY.parquet (via load_spy_series)

Output
------
reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/equity_curve.png

Citation
--------
Gayed EMA-100 regime signal `[leverage_for_the_long_run, p.11-14]`.
L=2 cap at 25% MDD `[leverage_space, Vince]`.
SPY benchmark construction `[advances_fin_ml, ch.11]`.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from ai_trade.backtest.metrics.standard_report import (  # noqa: E402
    build_spy_benchmark,
    load_spy_series,
)

RETURNS_PATH = Path(
    "reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/"
    "gayed_ema100_L2_off_gld_daily_returns.parquet"
)
SPY_PATH = Path("data/tiingo/daily/prices/SPY.parquet")
OUT_PATH = Path(
    "reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/equity_curve.png"
)

INITIAL_CAPITAL = 100_000.0
EMA_SPAN = 100  # Gayed EMA-100 regime signal
IS_OOS_SPLIT = pd.Timestamp("2018-01-01")
OOS_FWD_SPLIT = pd.Timestamp("2024-01-01")


def _drawdown(equity: pd.Series) -> pd.Series:
    running_peak = equity.cummax()
    return equity / running_peak - 1.0


def _load_spy_close() -> pd.Series:
    df = pd.read_parquet(SPY_PATH)
    s = df["adj_close"].astype(float)
    s.index = pd.DatetimeIndex(s.index)
    s.name = "SPY_close"
    return s.sort_index()


def _window_metric(
    returns: pd.Series, start: pd.Timestamp, end: pd.Timestamp
) -> tuple[float, float, float]:
    r = returns.loc[(returns.index >= start) & (returns.index < end)]
    if len(r) < 2:
        return float("nan"), float("nan"), float("nan")
    eq = (1.0 + r).cumprod()
    years = len(r) / 252.0
    cagr = float(eq.iloc[-1] ** (1.0 / years) - 1.0)
    sharpe = float(r.mean() / r.std() * np.sqrt(252.0))
    mdd = float(_drawdown(eq).min())
    return sharpe, cagr, mdd


def main() -> None:
    returns = pd.read_parquet(RETURNS_PATH)["ret"].astype(float)
    returns.index = pd.DatetimeIndex(returns.index)
    returns = returns.sort_index()

    strategy_equity = INITIAL_CAPITAL * (1.0 + returns).cumprod()
    strategy_equity.iloc[0] = INITIAL_CAPITAL  # anchor start
    strat_dd = _drawdown(strategy_equity)

    spy_series = load_spy_series()
    spy_bench = build_spy_benchmark(
        spy_series,
        initial_capital=INITIAL_CAPITAL,
        window_start=pd.Timestamp(strategy_equity.index[0]),
        window_end=pd.Timestamp(strategy_equity.index[-1]),
    )
    spy_equity = spy_bench.equity_curve
    spy_dd = _drawdown(spy_equity)

    spy_close = _load_spy_close().reindex(strategy_equity.index).ffill()
    ema100 = spy_close.ewm(span=EMA_SPAN, adjust=False).mean()
    regime_off = spy_close <= ema100  # Gayed EMA-100 off-regime

    is_m = _window_metric(returns, returns.index[0], IS_OOS_SPLIT)
    oos_m = _window_metric(returns, IS_OOS_SPLIT, OOS_FWD_SPLIT)
    fwd_m = _window_metric(returns, OOS_FWD_SPLIT, returns.index[-1] + pd.Timedelta(days=1))

    fig, (ax_eq, ax_dd) = plt.subplots(
        2, 1, figsize=(13, 8), sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.0]},
    )

    ax_eq.fill_between(
        strategy_equity.index,
        1.0,
        1e12,
        where=regime_off.values,
        color="#d4a017",
        alpha=0.08,
        linewidth=0,
        label="Off-regime (GLD leg, SPY ≤ EMA100)",
    )
    ax_eq.plot(
        strategy_equity.index,
        strategy_equity.values,
        label="Strategy (gayed_ema100_L2_off_gld)",
        color="#1f6feb",
        linewidth=1.3,
    )
    ax_eq.plot(
        spy_equity.index,
        spy_equity.values,
        label="SPY buy&hold",
        color="#8b949e",
        linewidth=1.0,
        linestyle="--",
    )
    ax_eq.axvline(IS_OOS_SPLIT, color="#444", linewidth=0.8, linestyle=":")
    ax_eq.axvline(OOS_FWD_SPLIT, color="#444", linewidth=0.8, linestyle=":")
    ax_eq.set_yscale("log")
    ax_eq.set_ylim(strategy_equity.min() * 0.8, strategy_equity.max() * 1.3)
    ax_eq.set_ylabel("Equity (BRL, log scale)")
    ax_eq.set_title(
        "Plano A Winner — Gayed EMA-100 L=2 off-GLD (CFD Pepperstone Razor)\n"
        "Phase 3.5a-V2 · 2001-05-14 → 2026-04-14 · net of spread+commission+swap+slippage"
    )
    ax_eq.legend(loc="upper left", fontsize=9)
    ax_eq.grid(True, which="both", alpha=0.25)

    def _annotate(ax, x, label, sharpe, cagr, mdd):
        ax.text(
            x,
            ax.get_ylim()[1] * 0.55,
            f"{label}\nSharpe {sharpe:.2f}\nCAGR {cagr * 100:.1f}%\nMDD {mdd * 100:.1f}%",
            fontsize=8,
            va="top",
            ha="left",
            bbox={"facecolor": "white", "edgecolor": "#aaa", "alpha": 0.85, "boxstyle": "round,pad=0.3"},
        )

    _annotate(ax_eq, returns.index[0] + pd.Timedelta(days=60), "IS (2001-2017)", *is_m)
    _annotate(ax_eq, IS_OOS_SPLIT + pd.Timedelta(days=60), "OOS (2018-2023)", *oos_m)
    _annotate(ax_eq, OOS_FWD_SPLIT + pd.Timedelta(days=60), "FWD (2024-26)", *fwd_m)

    ax_dd.fill_between(
        strat_dd.index, strat_dd.values * 100.0, 0.0,
        color="#1f6feb", alpha=0.35, linewidth=0,
        label=f"Strategy (MDD {strat_dd.min() * 100:.1f}%)",
    )
    ax_dd.plot(
        spy_dd.index, spy_dd.values * 100.0,
        color="#8b949e", linewidth=1.0, linestyle="--",
        label=f"SPY (MDD {spy_dd.min() * 100:.1f}%)",
    )
    ax_dd.axvline(IS_OOS_SPLIT, color="#444", linewidth=0.8, linestyle=":")
    ax_dd.axvline(OOS_FWD_SPLIT, color="#444", linewidth=0.8, linestyle=":")
    ax_dd.axhline(-25.0, color="#c0392b", linewidth=0.7, linestyle="--",
                  label="L=2 MDD cap (−25%)")
    ax_dd.set_ylabel("Drawdown (%)")
    ax_dd.set_xlabel("Date")
    ax_dd.legend(loc="lower left", fontsize=9)
    ax_dd.grid(True, alpha=0.25)
    ax_dd.set_ylim(min(strat_dd.min(), spy_dd.min()) * 100.0 - 3.0, 2.0)

    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=130)
    plt.close(fig)

    print(f"wrote {OUT_PATH}")
    print(f"  strategy_equity_final = {strategy_equity.iloc[-1]:,.2f}")
    print(f"  spy_equity_final      = {spy_equity.iloc[-1]:,.2f}")
    print(f"  strategy_mdd          = {strat_dd.min() * 100:.2f}%")
    print(f"  spy_mdd               = {spy_dd.min() * 100:.2f}%")
    print(f"  OOS sharpe (recomputed) = {oos_m[0]:.3f} (gate expected 2.285)")
    print(f"  OOS CAGR  (recomputed)  = {oos_m[1] * 100:.2f}% (gate expected 79.14%)")
    print(f"  OOS MDD   (recomputed)  = {oos_m[2] * 100:.2f}% (gate expected -21.02%)")


if __name__ == "__main__":
    main()
