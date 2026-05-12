"""LRS baseline comparison vs t3d-k2 / iter030.

Builds a head-to-head comparison report: the two reference strategies from
the closed ``letf_rotation_hunt`` study against four naive Gayed LRS
variants (price > SMA200 → leveraged ETF, else FFR cash) plus SPY / NDX
buy-and-hold.

Eight series:
  - **t3d_k2**          — closed study anchor (Vote-of-K=2, QLD/ZROZ).
  - **iter030**         — post-close winner (T35D60 + LRS1.20 overlay).
  - **LRS_SPY_SSO_2x**  — Gayed LRS on SPY signal, SSO 2× on-leg.
  - **LRS_SPY_UPRO_3x** — Gayed LRS on SPY signal, UPRO 3× on-leg.
  - **LRS_QQQ_QLD_2x**  — Gayed LRS on QQQ signal, QLD 2× on-leg.
  - **LRS_QQQ_TQQQ_3x** — Gayed LRS on QQQ signal, TQQQ 3× on-leg.
  - **SPY_BH**          — SPY buy-and-hold.
  - **NDX_BH**          — QQQ buy-and-hold (NDX proxy; no NDX index in cache).

Citations
---------
* SMA200 LRS rule: ``[leverage_for_the_long_run, p.13]``.
* LETF synthetic daily return ``r = L·r - ER/252 - (L-1)·(FFR+spread/252)``:
  ``[leverage_for_the_long_run, p.16, footnote 22-23]``.
* Cash leg = FFR (CASHX testfolio proxy): testfol.io docs.
* Vote-of-K(2) anchor (t3d-k2): ``studies/letf_rotation_hunt/reports/STUDY_FINAL_REPORT.md``.
* T35D60 + LRS1.20 (iter030): ``studies/letf_rotation_hunt/reports/POST_CLOSE_LOOP_REPORT.md``.

Run
---
``uv run python -m studies.letf_rotation_hunt.runners.run_lrs_baseline_comparison``

Outputs land in ``studies/letf_rotation_hunt/reports/lrs_baseline/`` (plots
+ tables) and the headline report at
``studies/letf_rotation_hunt/reports/LRS_BASELINE_COMPARISON.md``.
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from market_lab.backtest.metrics.performance import (
    cagr,
    calmar,
    max_drawdown,
    sharpe,
    sortino,
)
from market_lab.backtest.strategies.letf_rotation import compute_regime_signal
from studies.letf_rotation_hunt.core import data_loader
from studies.letf_rotation_hunt.core.rolling_sortino import (
    rolling_sortino_at_windows,
)
from studies.letf_rotation_hunt.core.synths import letf_synth_returns
from studies.spy_beater_hunt.rolling_metrics import rolling_cagr_mdd_at_windows

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = REPO_ROOT / "studies/letf_rotation_hunt/reports"
OUT_DIR = REPORT_DIR / "lrs_baseline"
PLOTS_DIR = OUT_DIR / "plots"
TABLES_DIR = OUT_DIR / "tables"

T3D_K2_CSV = (
    REPO_ROOT
    / "studies/letf_rotation_hunt/runs/original/022-2026-05-06-T3d-extended-grid"
    / "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz_strategy_returns.csv"
)
ITER030_CSV = (
    REPO_ROOT
    / "studies/letf_rotation_hunt/runs/post_close/030-2026-05-10-tcrash-scan-lrs120-rearmonly"
    / "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120_strategy_returns.csv"
)

ROLLING_WINDOWS_YEARS: list[int] = [3, 5, 10, 15]

# Per-LETF defaults from spec §4.4 ``[leverage_for_the_long_run, p.16]``.
# Gross run: ER set to 0 to isolate signal vs LETF-product drag.
LRS_VARIANTS: list[tuple[str, str, str, float]] = [
    # (label, signal_underlying_ticker, on_leg_ticker, leverage)
    ("LRS_SPY_SSO_2x", "SPYSIM", "SSO", 2.0),
    ("LRS_SPY_UPRO_3x", "SPYSIM", "UPRO", 3.0),
    ("LRS_QQQ_QLD_2x", "QQQSIM", "QLD", 2.0),
    ("LRS_QQQ_TQQQ_3x", "QQQSIM", "TQQQ", 3.0),
]

# 8-line palette. iter030 + t3d-k2 take the visually dominant slots
# (red/black); LRS variants use the blue/orange family grouped by underlying;
# buy-and-hold baselines are gray.
PALETTE: dict[str, str] = {
    "iter030": "#d62728",          # red — post-close winner
    "t3d_k2": "#111111",            # near-black — study anchor
    "LRS_SPY_SSO_2x": "#1f77b4",    # blue
    "LRS_SPY_UPRO_3x": "#0b3d70",   # dark blue
    "LRS_QQQ_QLD_2x": "#ff7f0e",    # orange
    "LRS_QQQ_TQQQ_3x": "#b35400",   # dark orange
    "SPY_BH": "#777777",            # gray
    "NDX_BH": "#aaaaaa",            # light gray
}
LINESTYLE: dict[str, str] = {
    "iter030": "-",
    "t3d_k2": "-",
    "LRS_SPY_SSO_2x": "-",
    "LRS_SPY_UPRO_3x": "--",
    "LRS_QQQ_QLD_2x": "-",
    "LRS_QQQ_TQQQ_3x": "--",
    "SPY_BH": "-",
    "NDX_BH": "--",
}

# Plot order: heaviest hitters drawn last so they sit on top.
PLOT_ORDER: list[str] = [
    "SPY_BH",
    "NDX_BH",
    "LRS_SPY_SSO_2x",
    "LRS_QQQ_QLD_2x",
    "LRS_SPY_UPRO_3x",
    "LRS_QQQ_TQQQ_3x",
    "t3d_k2",
    "iter030",
]


def _load_csv_returns(path: Path) -> pd.Series:
    """Load a strategy daily-return CSV (``date,return`` schema)."""
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date")
    s = df["return"].astype(float)
    s.name = path.stem
    return s


def _simulate_lrs(
    signal_prices: pd.Series,
    on_returns: pd.Series,
    ffr_daily: pd.Series,
    lookback: int = 200,
) -> pd.Series:
    """One LRS run with FFR cash leg.

    Daily SMA gate on ``signal_prices`` (strict cross, no band — Gayed
    canonical ``[leverage_for_the_long_run, p.13]``). Risk-on: ``on_returns``
    (synth or real leveraged daily returns). Risk-off: daily FFR (cash leg
    matches the canonical paper interpretation; testfolio CASHX proxy).

    Signal lag: ``regime.shift(1)`` — decision at close[t] sets the position
    for close[t]→close[t+1], so today's position is yesterday's decision.
    Without the shift the same-day signal peeks at the return it's about to
    earn (verified against testfol.io 2026-05-11). The post-close study
    backtests (iter030 ``backtest.py``) lag their signals the same way.

    Gross — no commissions, no expense ratio, no tax — per user-locked
    decision in the comparison plan.
    """
    aligned = pd.concat(
        {"px": signal_prices, "on": on_returns, "ffr": ffr_daily},
        axis=1,
        sort=False,
    ).dropna()

    regime = compute_regime_signal(
        aligned["px"], filter="SMA", lookback=lookback, band_pct=0.0
    )
    # Lag by 1 day to remove the same-day lookahead — yesterday's decision
    # earns today's return. NaN-fill → OFF (cash) to keep the warmup flat.
    is_on = regime.shift(1).eq("ON")
    daily = np.where(is_on, aligned["on"].values, aligned["ffr"].values)
    out = pd.Series(daily, index=aligned.index, dtype=float)
    out.iloc[:lookback] = 0.0  # explicit warmup → flat (no equity drift)
    return out


def _equity_from_returns(returns: pd.Series, base: float = 10_000.0) -> pd.Series:
    """Compound a daily-return series into an equity curve starting at ``base``."""
    return (1.0 + returns.fillna(0.0)).cumprod() * base


def _headline_metrics(returns: pd.Series) -> dict[str, float]:
    eq = _equity_from_returns(returns)
    return {
        "CAGR": cagr(eq),
        "Sharpe": sharpe(returns),
        "Sortino": sortino(returns),
        "MaxDD": -max_drawdown(eq),  # signed (negative) for readability
        "Calmar": calmar(eq),
        "EndMult": float(eq.iloc[-1] / eq.iloc[0]),
    }


def _summarize_rolling_cagr(
    rolling: dict[int, list[dict]],
) -> dict[tuple[int, str], float]:
    out: dict[tuple[int, str], float] = {}
    for w, rows in rolling.items():
        if not rows:
            for stat in ("mean", "p25", "p50", "p75", "min"):
                out[(w, stat)] = float("nan")
            continue
        cagrs = np.array([r["cagr"] for r in rows], dtype=float)
        out[(w, "mean")] = float(np.nanmean(cagrs))
        out[(w, "p25")] = float(np.nanpercentile(cagrs, 25))
        out[(w, "p50")] = float(np.nanpercentile(cagrs, 50))
        out[(w, "p75")] = float(np.nanpercentile(cagrs, 75))
        out[(w, "min")] = float(np.nanmin(cagrs))
    return out


def _summarize_rolling_sortino(
    rolling: dict[int, list[dict]],
) -> dict[tuple[int, str], float]:
    out: dict[tuple[int, str], float] = {}
    for w, rows in rolling.items():
        if not rows:
            for stat in ("mean", "p25", "p50", "p75", "min"):
                out[(w, stat)] = float("nan")
            continue
        # +inf Sortino can occur on tiny windows with zero downside — replace
        # for percentile math (keep in raw "min" via nan-safe path).
        vals = np.array(
            [r["sortino"] for r in rows if np.isfinite(r["sortino"])], dtype=float
        )
        if vals.size == 0:
            for stat in ("mean", "p25", "p50", "p75", "min"):
                out[(w, stat)] = float("nan")
            continue
        out[(w, "mean")] = float(np.mean(vals))
        out[(w, "p25")] = float(np.percentile(vals, 25))
        out[(w, "p50")] = float(np.percentile(vals, 50))
        out[(w, "p75")] = float(np.percentile(vals, 75))
        out[(w, "min")] = float(np.min(vals))
    return out


def _plot_equity(equity: dict[str, pd.Series], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    for label in PLOT_ORDER:
        if label not in equity:
            continue
        eq = equity[label]
        ax.plot(
            eq.index,
            eq.values,
            color=PALETTE[label],
            linestyle=LINESTYLE[label],
            linewidth=1.6 if label in {"iter030", "t3d_k2"} else 1.2,
            alpha=0.95 if label in {"iter030", "t3d_k2"} else 0.85,
            label=label,
        )
    ax.set_yscale("log")
    ax.set_title("Equity curves — log scale, $10k base (gross)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($)")
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=9)
    plt.tight_layout()
    plt.savefig(path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def _plot_drawdown(equity: dict[str, pd.Series], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    for label in PLOT_ORDER:
        if label not in equity:
            continue
        eq = equity[label]
        peak = eq.cummax()
        dd = (eq - peak) / peak * 100.0
        ax.plot(
            dd.index,
            dd.values,
            color=PALETTE[label],
            linestyle=LINESTYLE[label],
            linewidth=1.4 if label in {"iter030", "t3d_k2"} else 1.0,
            alpha=0.9,
            label=label,
        )
    ax.set_title("Drawdown (peak-to-trough %, gross)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    ax.legend(loc="lower left", bbox_to_anchor=(1.02, 0), fontsize=9)
    plt.tight_layout()
    plt.savefig(path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def _plot_rolling_grid(
    series: dict[str, pd.Series],
    windows: list[int],
    metric: str,
    path: Path,
) -> None:
    """Rolling-metric 2×2 grid (one panel per window).

    ``metric`` ∈ {"CAGR", "Sortino"}. Plots per-bar trailing values so the
    curves are continuous — matches ``plot_helper.plot_rolling_cagr``/_sharpe.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
    axes = axes.flatten()
    for ax, w in zip(axes, windows):
        w_days = w * 252
        for label in PLOT_ORDER:
            if label not in series:
                continue
            rets = series[label].fillna(0.0)
            if metric == "CAGR":
                eq = _equity_from_returns(rets)
                ratio = eq / eq.shift(w_days)
                vals = ratio ** (1.0 / w) - 1.0
                vals = vals * 100.0
            else:  # Sortino
                # Per-bar trailing Sortino using a rolling window.
                # downside_dev = √mean(min(r,0)²) over the window, annualised √252.
                mean_r = rets.rolling(w_days).mean()
                neg = rets.clip(upper=0.0)
                down_sq_mean = (neg ** 2).rolling(w_days).mean()
                down_dev = np.sqrt(down_sq_mean)
                vals = (mean_r / down_dev.replace(0, np.nan)) * np.sqrt(252)
            ax.plot(
                vals.index,
                vals.values,
                color=PALETTE[label],
                linestyle=LINESTYLE[label],
                linewidth=1.4 if label in {"iter030", "t3d_k2"} else 1.0,
                alpha=0.9,
                label=label,
            )
        ax.set_title(f"Rolling {w}y {metric}")
        unit = "%" if metric == "CAGR" else ""
        ax.set_ylabel(f"{metric} ({unit})" if unit else metric)
        ax.axhline(y=0, color="black", linewidth=0.5)
        ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    axes[0].legend(loc="upper left", bbox_to_anchor=(0, 1.18), ncol=4, fontsize=8)
    fig.suptitle(f"Rolling {metric} — 3/5/10/15y windows", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def main() -> dict:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load underlyings + FFR.
    spy_px = data_loader.load_testfolio_series("SPYSIM").dropna()
    qqq_px = data_loader.load_testfolio_series("QQQSIM").dropna()
    ffr = data_loader.load_ffr_daily()

    spy_ret = spy_px.pct_change().dropna()
    qqq_ret = qqq_px.pct_change().dropna()

    # 2. Build the 4 LRS variants (FFR cash leg, gross — ER=0).
    returns: dict[str, pd.Series] = {}
    for label, signal_ticker, on_ticker, lev in LRS_VARIANTS:
        signal_px = spy_px if signal_ticker == "SPYSIM" else qqq_px
        underlying_ret = spy_ret if signal_ticker == "SPYSIM" else qqq_ret
        on_ret = letf_synth_returns(
            underlying_returns=underlying_ret,
            leverage=lev,
            expense_ratio_annual=0.0,  # gross — see plan: costs OFF
            ffr_daily=ffr,
            ffr_spread_annual=0.0,
        )
        returns[label] = _simulate_lrs(signal_px, on_ret, ffr, lookback=200)

    # 3. Load the two study CSVs.
    returns["t3d_k2"] = _load_csv_returns(T3D_K2_CSV)
    returns["iter030"] = _load_csv_returns(ITER030_CSV)

    # 4. Buy-and-hold baselines.
    returns["SPY_BH"] = spy_ret
    returns["NDX_BH"] = qqq_ret

    # 5. Align to common date range — intersection of indices.
    aligned = pd.concat(returns, axis=1).dropna()
    assert not aligned.empty, "no common date range across all 8 series"
    start, end = aligned.index[0], aligned.index[-1]
    log.info("Aligned window: %s → %s (%d days)", start.date(), end.date(), len(aligned))
    # Sanity per plan §verification:
    assert start <= pd.Timestamp("1987-01-15"), (
        f"common start {start.date()} later than 1987-01-15 — check warmup"
    )
    assert end >= pd.Timestamp("2026-04-01"), (
        f"common end {end.date()} earlier than 2026-04-01"
    )

    # 6. Equity curves + headline metrics.
    equity = {k: _equity_from_returns(aligned[k]) for k in aligned.columns}

    metrics_df = pd.DataFrame(
        {k: _headline_metrics(aligned[k]) for k in aligned.columns}
    ).T
    metrics_df.index.name = "strategy"
    metrics_df = metrics_df.loc[
        [k for k in PLOT_ORDER if k in metrics_df.index]
    ]  # canonical order
    metrics_df.to_csv(TABLES_DIR / "headline_metrics.csv")

    # 7. Rolling windows.
    rcm = {
        k: rolling_cagr_mdd_at_windows(aligned[k], ROLLING_WINDOWS_YEARS)
        for k in aligned.columns
    }
    rso = {
        k: rolling_sortino_at_windows(aligned[k], ROLLING_WINDOWS_YEARS)
        for k in aligned.columns
    }
    cagr_summary = pd.DataFrame(
        {k: _summarize_rolling_cagr(rcm[k]) for k in aligned.columns}
    ).T
    sortino_summary = pd.DataFrame(
        {k: _summarize_rolling_sortino(rso[k]) for k in aligned.columns}
    ).T
    cagr_summary.columns = pd.MultiIndex.from_tuples(
        cagr_summary.columns, names=["window_y", "stat"]
    )
    sortino_summary.columns = pd.MultiIndex.from_tuples(
        sortino_summary.columns, names=["window_y", "stat"]
    )
    cagr_summary.to_csv(TABLES_DIR / "rolling_cagr_summary.csv")
    sortino_summary.to_csv(TABLES_DIR / "rolling_sortino_summary.csv")

    # 8. Plots.
    _plot_equity(equity, PLOTS_DIR / "equity_curves.png")
    _plot_drawdown(equity, PLOTS_DIR / "drawdown_curves.png")
    _plot_rolling_grid(
        {k: aligned[k] for k in aligned.columns},
        ROLLING_WINDOWS_YEARS,
        metric="CAGR",
        path=PLOTS_DIR / "rolling_cagr_3_5_10_15y.png",
    )
    _plot_rolling_grid(
        {k: aligned[k] for k in aligned.columns},
        ROLLING_WINDOWS_YEARS,
        metric="Sortino",
        path=PLOTS_DIR / "rolling_sortino_3_5_10_15y.png",
    )

    # 9. Sanity reproduction checks per plan §verification.
    spy_sharpe = float(metrics_df.loc["SPY_BH", "Sharpe"])
    t3d_sortino = float(metrics_df.loc["t3d_k2", "Sortino"])
    iter030_sortino = float(metrics_df.loc["iter030", "Sortino"])
    iter030_cagr = float(metrics_df.loc["iter030", "CAGR"])
    log.info(
        "Sanity: SPY_BH Sharpe=%.3f, t3d_k2 Sortino=%.4f, iter030 Sortino=%.4f, "
        "iter030 CAGR=%.4f", spy_sharpe, t3d_sortino, iter030_sortino, iter030_cagr,
    )
    # Loose tolerances: study numbers are full CSV (10150 rows); aligned window
    # is the intersection, so values differ slightly. Plan §verification expects
    # ±0.005 Sortino and ±0.05pp CAGR but only over the *full* CSV range. We
    # check the loose intersection-period bounds here and report the full-CSV
    # values separately in the report.
    assert 0.55 <= spy_sharpe <= 0.80, f"SPY_BH Sharpe out of range: {spy_sharpe}"
    assert 1.0 <= t3d_sortino <= 1.5, f"t3d_k2 Sortino out of range: {t3d_sortino}"
    assert 1.1 <= iter030_sortino <= 1.6, (
        f"iter030 Sortino out of range: {iter030_sortino}"
    )

    return {
        "start": str(start.date()),
        "end": str(end.date()),
        "n_days": int(len(aligned)),
        "metrics": metrics_df.to_dict(),
        "plots_dir": str(PLOTS_DIR.relative_to(REPO_ROOT)),
        "tables_dir": str(TABLES_DIR.relative_to(REPO_ROOT)),
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    summary = main()
    print("Aligned window:", summary["start"], "→", summary["end"],
          f"({summary['n_days']} days)")
    print("Plots:", summary["plots_dir"])
    print("Tables:", summary["tables_dir"])
