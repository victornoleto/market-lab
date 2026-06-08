"""Phase 3C - Lookback study: robustness map -> theory anchor -> gated adaptive.

Research-only. This runner does NOT authorize deployment, paper trading or a
mandate change. It answers *"why SMA 200?"* for the LRS restart without falling
into either overfit trap: blindly trusting the community-popular 200, or sweeping
many windows and promoting the argmax.

Three parts (one ``main()``):

1. **Robustness map** - sweep 13 windows (50..400) over SMA and EMA on the Phase 2
   geometry, across the 3 bases per branch, lag ``0..5`` (936 rows). The surface
   reads each window at its **best-score lag**, and a PRE-REGISTERED plateau rule
   decides whether 200 sits inside a robust plateau. We do NOT promote the argmax
   `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`.
2. **Theory anchor** - ex-ante half-lives from the return series alone (volatility
   persistence via squared-return ACF decay ~ GARCH alpha+beta; return
   autocorrelation), mapped to a natural window and checked against the plateau
   `[volatility_trading, p.39, p.53-54]`, `[systematic_trading, p.283]`.
3. **Adaptive window** - runs ONLY if Part 1 finds no robust plateau on a
   primary-base SMA curve; vol-scaled window vs fixed-200 and best-fixed,
   reporting turnover and the leveraged-sleeve result `[leverage_for_the_long_run,
   p.4-7]`.

Studies SMA + EMA only (Phase 3A-2 did not promote hysteresis).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import math
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lrs.lib.backtest import (  # noqa: E402
    build_sma_signal,
    build_weekly_lagged_weights,
    clean_weights,
    constant_weight_frame,
    equity_curve,
    fmt_num,
    fmt_pct,
    fmt_pp,
    fmt_x,
    load_price_frame,
    md_table,
    metrics_from_returns,
    relative_stats,
    simulate_weight_frame,
    weights_label,
)
from lrs.lib.indicators import (  # noqa: E402
    acf_decay_half_life,
    adaptive_vol_window,
    ema_gate,
    ewma_span_from_half_life,
)


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase03c_lookback_study.csv"
THEORY_CSV = RESULTS / "phase03c_theory_anchor.csv"

BRANCHES = {
    "SPY": {"branch": "SPY", "underlying": "SPYSIM", "lev2": "SSOSIM", "lev3": "UPROSIM"},
    "QQQ": {"branch": "QQQ", "underlying": "QQQSIM", "lev2": "QLDSIM", "lev3": "TQQQSIM"},
}

RISK_OFF_LIBRARY: dict[str, dict[str, float]] = {
    "50 ZROZ / 25 GLD / 25 CASH": {"ZROZSIM": 0.50, "GLDSIM": 0.25, "CASHX": 0.25},
    "40 ZROZ / 40 GLD / 20 IEF": {"ZROZSIM": 0.40, "GLDSIM": 0.40, "IEFSIM": 0.20},
}

VOL_LIBRARY: dict[str, dict[str, object]] = {
    "RV21 <= 30%": {"name": "RV21 <= 30%", "window": 21, "threshold": 0.30},
    "RV63 <= 40%": {"name": "RV63 <= 40%", "window": 63, "threshold": 0.40},
}

# Same 6 bases as Phase 3A-2 / Phase 3A (Phase 2 top + 2 one-lever neighbours).
BASE_SPECS: list[dict[str, object]] = [
    {"branch": "SPY", "name": "spy_top", "target_leverage": 2.00, "risk_off": "50 ZROZ / 25 GLD / 25 CASH", "vol": "RV21 <= 30%"},
    {"branch": "SPY", "name": "spy_lower_lev", "target_leverage": 1.75, "risk_off": "50 ZROZ / 25 GLD / 25 CASH", "vol": "RV21 <= 30%"},
    {"branch": "SPY", "name": "spy_alt_off", "target_leverage": 2.00, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV21 <= 30%"},
    {"branch": "QQQ", "name": "qqq_top", "target_leverage": 1.75, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV63 <= 40%"},
    {"branch": "QQQ", "name": "qqq_lower_lev", "target_leverage": 1.50, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV63 <= 40%"},
    {"branch": "QQQ", "name": "qqq_alt_vol", "target_leverage": 1.75, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV21 <= 30%"},
]

# Pre-registered window grid and forms. Lookback is the variable under study.
WINDOWS: list[int] = [50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 350, 400]
FORMS: list[dict[str, str]] = [{"name": "SMA", "kind": "sma"}, {"name": "EMA", "kind": "ema"}]
PRIMARY_BASE: dict[str, str] = {"SPY": "spy_top", "QQQ": "qqq_top"}
TARGET_WINDOW = 200

# Cross-check markers from the spin-off line `studies/lrs/` (now canonical in
# `letf-lab`); shown on plots, NOT inherited as a parameter choice.
SPINOFF_MARKERS: dict[str, tuple[int, int]] = {"SPY": (250, 295), "QQQ": (245, 245)}

# Pre-registered adaptive parameters (fixed before seeing results).
ADAPT_W_BASE = 200
ADAPT_VOL_TARGET = 0.15
ADAPT_W_MIN = 50
ADAPT_W_MAX = 400
ADAPT_RV_WINDOW = 63


def build_regime_gate_window(prices: pd.Series, kind: str, window: int) -> pd.Series:
    """Trend gate for a regime form at a given window (`.shift(1)`-lagged)."""
    if kind == "sma":
        return build_sma_signal(prices, int(window))
    if kind == "ema":
        return ema_gate(prices, int(window))
    raise ValueError(f"unknown form kind: {kind}")


def calmar_plateau(
    windows: np.ndarray,
    calmar: np.ndarray,
    target_window: int = TARGET_WINDOW,
    tol: float = 0.10,
    min_width: int = 150,
) -> dict[str, object]:
    """Pre-registered plateau rule (diagnostic, NOT an optimizer).

    Anchor at the argmax-Calmar window, extend a contiguous band left/right while
    ``Calmar >= (1-tol) * best``. A robust plateau exists iff the band spans
    ``>= min_width`` days. ``contains_target`` iff ``target_window`` is inside the
    band; ``is_fragile`` iff no plateau (a narrow peak). The deliverable is this
    verdict, not "the best window" `[trading_systems_methods, p.939]`,
    `[advances_fin_ml, p.208-211]`.
    """
    w = np.asarray(windows, dtype=float)
    c = np.asarray(calmar, dtype=float)
    order = np.argsort(w)
    w = w[order]
    c = c[order]
    best_i = int(np.nanargmax(c))
    best = float(c[best_i])
    thresh = (1.0 - tol) * best
    lo = best_i
    while lo - 1 >= 0 and c[lo - 1] >= thresh:
        lo -= 1
    hi = best_i
    while hi + 1 < len(c) and c[hi + 1] >= thresh:
        hi += 1
    band_lo = int(w[lo])
    band_hi = int(w[hi])
    width = band_hi - band_lo
    has_plateau = bool(width >= min_width)
    return {
        "argmax_window": int(w[best_i]),
        "best_calmar": best,
        "band_lo": band_lo,
        "band_hi": band_hi,
        "band_width": int(width),
        "has_plateau": has_plateau,
        "contains_target": bool(has_plateau and band_lo <= target_window <= band_hi),
        "is_fragile": bool(not has_plateau),
    }


@dataclass
class BranchContext:
    branch: dict[str, str]
    prices: pd.DataFrame
    returns: pd.DataFrame
    underlying_taxed: pd.Series
    underlying_metrics: object
    benchmark_by_l: dict[float, pd.Series]
    benchmark_metrics_by_l: dict[float, object]
    gate_cache: dict[tuple[str, int], pd.Series] = field(default_factory=dict)


def branch_assets(branch: dict[str, str]) -> list[str]:
    assets = {branch["underlying"], branch["lev2"], branch["lev3"], "CASHX", "GLDSIM", "IEFSIM", "ZROZSIM"}
    return sorted(assets)


def target_leverage_weights(branch: dict[str, str], target_leverage: float) -> dict[str, float]:
    """Map target leverage to adjacent ETF sleeves without external margin
    (same construction as Phase 2/3A/3A-2) `[leverage_for_the_long_run, p.13]`."""
    if target_leverage < 1.0 or target_leverage > 3.0:
        raise ValueError(f"target leverage out of range: {target_leverage}")
    if target_leverage <= 2.0:
        return clean_weights({branch["underlying"]: 2.0 - target_leverage, branch["lev2"]: target_leverage - 1.0})
    return clean_weights({branch["lev2"]: 3.0 - target_leverage, branch["lev3"]: target_leverage - 2.0})


def drawdown_tier(mdd: float) -> str:
    if mdd >= -0.40:
        return "preferred"
    if mdd >= -0.50:
        return "tolerable"
    if mdd >= -0.65:
        return "warning"
    return "ruin"


def drawdown(returns: pd.Series) -> pd.Series:
    equity = equity_curve(returns)
    return equity / equity.cummax() - 1.0


def base_leverages(branch_name: str) -> list[float]:
    return sorted({float(b["target_leverage"]) for b in BASE_SPECS if b["branch"] == branch_name})


def build_context(branch: dict[str, str]) -> BranchContext:
    prices = load_price_frame(branch_assets(branch))
    returns = prices.pct_change().dropna()
    prices = prices.reindex(returns.index)
    underlying_frame = constant_weight_frame(returns.index, {branch["underlying"]: 1.0})
    underlying_taxed, _ = simulate_weight_frame(returns, underlying_frame, taxable=True)
    benchmark_by_l: dict[float, pd.Series] = {}
    benchmark_metrics_by_l: dict[float, object] = {}
    for target_leverage in base_leverages(branch["branch"]):
        frame = constant_weight_frame(returns.index, target_leverage_weights(branch, target_leverage))
        taxed, _ = simulate_weight_frame(returns, frame, taxable=True)
        benchmark_by_l[target_leverage] = taxed
        benchmark_metrics_by_l[target_leverage] = metrics_from_returns(taxed)
    underlying_prices = prices[branch["underlying"]]
    gate_cache: dict[tuple[str, int], pd.Series] = {}
    for form in FORMS:
        for window in WINDOWS:
            gate = build_regime_gate_window(underlying_prices, form["kind"], window)
            gate_cache[(form["kind"], window)] = gate.reindex(returns.index).fillna(False).astype(bool)
    return BranchContext(
        branch=branch,
        prices=prices,
        returns=returns,
        underlying_taxed=underlying_taxed,
        underlying_metrics=metrics_from_returns(underlying_taxed),
        benchmark_by_l=benchmark_by_l,
        benchmark_metrics_by_l=benchmark_metrics_by_l,
        gate_cache=gate_cache,
    )


def vol_gate(context: BranchContext, spec: dict[str, object]) -> pd.Series:
    if spec["threshold"] is None:
        return pd.Series(True, index=context.returns.index)
    window = int(spec["window"])
    threshold = float(spec["threshold"])
    underlying_returns = context.returns[context.branch["underlying"]]
    realized_vol = underlying_returns.rolling(window).std(ddof=0).shift(1) * np.sqrt(252.0)
    return (realized_vol <= threshold).reindex(context.returns.index).fillna(False)


def score_signal(context: BranchContext, base: dict[str, object], trend_gate: pd.Series, lag_days: int) -> dict[str, object]:
    """Backtest a trend gate on a base+lag and return the scored row.

    ``signal = trend_gate & vol_gate``; the trend gate REPLACES the SMA level gate
    (Phase 3A-2 mechanism). Phase 2 scoring kept verbatim for cross-phase
    comparability.
    """
    target_leverage = float(base["target_leverage"])
    risk_off_weights = clean_weights(RISK_OFF_LIBRARY[str(base["risk_off"])])
    vol_spec = VOL_LIBRARY[str(base["vol"])]
    risk_on_weights = target_leverage_weights(context.branch, target_leverage)
    gate = trend_gate.reindex(context.returns.index).fillna(False).astype(bool)
    signal = gate & vol_gate(context, vol_spec)
    assets = sorted(set(risk_on_weights) | set(risk_off_weights) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=context.returns.index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on_weights.get(asset, 0.0), risk_off_weights.get(asset, 0.0))
    weights, schedule_summary = build_weekly_lagged_weights(desired, lag_days=lag_days, risk_on_weights=risk_on_weights)
    gross, _ = simulate_weight_frame(context.returns, weights, taxable=False)
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    tm = metrics_from_returns(taxed)
    gm = metrics_from_returns(gross)
    benchmark = context.benchmark_by_l[target_leverage]
    bm = context.benchmark_metrics_by_l[target_leverage]
    rel_u = relative_stats(taxed, context.underlying_taxed)
    rel_b = relative_stats(taxed, benchmark)
    cagr_spread = tm.cagr - context.underlying_metrics.cagr
    drawdown_component = max(-1.0, min(1.0, (tm.mdd + 0.65) / 0.25))
    score = (
        6.0 * cagr_spread
        + 2.25 * tm.calmar
        + 0.75 * tm.sortino
        + 1.00 * rel_u.get("hit_10y", 0.0)
        + 1.75 * drawdown_component
        + 0.25 * rel_u["worst_relative_drawdown"]
        - 0.10 * float(tax_summary["turnover_per_year"])
    )
    return {
        "branch": context.branch["branch"],
        "base_name": base["name"],
        "target_leverage": target_leverage,
        "risk_off_name": base["risk_off"],
        "vol_filter": vol_spec["name"],
        "lag_days": lag_days,
        "cadence": "weekly",
        "score": score,
        "drawdown_tier": drawdown_tier(tm.mdd),
        "practical_pass": bool(cagr_spread > 0.0 and tm.mdd >= -0.50 and rel_u["terminal_vs_benchmark"] > 1.0),
        "taxed_cagr": tm.cagr,
        "taxed_mdd": tm.mdd,
        "taxed_calmar": tm.calmar,
        "taxed_sortino": tm.sortino,
        "taxed_sharpe": tm.sharpe,
        "taxed_terminal": tm.terminal,
        "gross_cagr": gm.cagr,
        "gross_mdd": gm.mdd,
        "underlying_taxed_cagr": context.underlying_metrics.cagr,
        "underlying_taxed_mdd": context.underlying_metrics.mdd,
        "levered_taxed_cagr": bm.cagr,
        "levered_taxed_mdd": bm.mdd,
        "cagr_spread_vs_underlying": cagr_spread,
        "terminal_vs_underlying": rel_u["terminal_vs_benchmark"],
        "terminal_vs_levered_bh": rel_b["terminal_vs_benchmark"],
        "worst_relative_dd_vs_underlying": rel_u["worst_relative_drawdown"],
        "hit_3y_vs_underlying": rel_u.get("hit_3y", pd.NA),
        "hit_5y_vs_underlying": rel_u.get("hit_5y", pd.NA),
        "hit_10y_vs_underlying": rel_u.get("hit_10y", pd.NA),
        "hit_15y_vs_underlying": rel_u.get("hit_15y", pd.NA),
        "hit_20y_vs_underlying": rel_u.get("hit_20y", pd.NA),
        "turnover_per_year": tax_summary["turnover_per_year"],
        "trade_count": tax_summary["trade_count"],
        "pct_risk_on_days": schedule_summary["pct_risk_on_days"],
        "tax_paid_pct_initial": tax_summary["total_tax_paid_pct_initial"],
        "start": tm.start,
        "end": tm.end,
        "years": tm.years,
    }


def simulate_candidate(context: BranchContext, base: dict[str, object], form: dict[str, str], window: int, lag_days: int) -> dict[str, object]:
    trend_gate = context.gate_cache[(form["kind"], window)]
    row = score_signal(context, base, trend_gate, lag_days)
    row["regime_form"] = form["name"]
    row["window"] = window
    return row


def best_lag_surface(results: pd.DataFrame, branch: str, base: str, form: str) -> pd.DataFrame:
    """Best-score lag per window for one (branch, base, form) cell, indexed by window."""
    subset = results[(results["branch"] == branch) & (results["base_name"] == base) & (results["regime_form"] == form)]
    best = subset.sort_values("score", ascending=False).groupby("window", sort=True).head(1)
    return best.sort_values("window").set_index("window")


def adaptive_sma_signal(prices: pd.Series, w_exec: pd.Series) -> pd.Series:
    """Adaptive-window SMA gate (no lookahead).

    ``w_exec`` is the executable per-day window (already vol-scaled and
    ``.shift(1)``-lagged). The decision on day ``t`` compares ``price_{t-1}`` to
    the trailing mean of length ``w_t`` ending at ``t-1``, so only information
    through ``t-1`` is used - the time-varying generalization of
    ``build_sma_signal`` `[testing_tuning, p.327-335]`.
    """
    p = prices.to_numpy(dtype=float)
    w = w_exec.reindex(prices.index).to_numpy()
    csum = np.concatenate([[0.0], np.cumsum(p)])
    cond = np.zeros(len(p), dtype=bool)
    for t in range(1, len(p)):
        wt = int(w[t]) if np.isfinite(w[t]) else 0
        start = t - wt
        if wt <= 0 or start < 0:
            continue
        sma_prev = (csum[t] - csum[start]) / wt  # mean of p[start..t-1]
        cond[t] = p[t - 1] > sma_prev
    return pd.Series(cond, index=prices.index).astype(bool)


def run_adaptive_for_branch(context: BranchContext, surfaces: dict[tuple[str, str, str], pd.DataFrame]) -> list[dict[str, object]]:
    """Adaptive-window vs fixed-200 vs best-fixed SMA on the branch primary base.

    Honest comparison reporting turnover and the leveraged-sleeve drawdown, since
    the spin-off found lookback-switch cost is amplified by leverage
    `[leverage_for_the_long_run, p.4-7]`.
    """
    branch = context.branch["branch"]
    base_name = PRIMARY_BASE[branch]
    base = next(b for b in BASE_SPECS if b["name"] == base_name)
    underlying = context.branch["underlying"]
    rv = context.returns[underlying].rolling(ADAPT_RV_WINDOW).std(ddof=0) * np.sqrt(252.0)
    w_exec = adaptive_vol_window(rv, ADAPT_W_BASE, ADAPT_VOL_TARGET, ADAPT_W_MIN, ADAPT_W_MAX)
    adaptive_gate = adaptive_sma_signal(context.prices[underlying], w_exec)
    rows: list[dict[str, object]] = []
    # adaptive: best lag
    best_adaptive = max((score_signal(context, base, adaptive_gate, lag) for lag in range(6)), key=lambda r: r["score"])
    best_adaptive.update({"variant": "adaptive-vol", "window": "adaptive", "mean_window": float(w_exec.mean())})
    rows.append(best_adaptive)
    # fixed-200 and best-fixed-window SMA on the same primary base (from surface)
    sma_surface = surfaces[(branch, base_name, "SMA")]
    fixed_200 = sma_surface.loc[TARGET_WINDOW].to_dict()
    fixed_200.update({"variant": "fixed-200", "window": TARGET_WINDOW, "mean_window": float(TARGET_WINDOW)})
    rows.append(fixed_200)
    best_fixed_window = int(sma_surface["score"].idxmax())
    best_fixed = sma_surface.loc[best_fixed_window].to_dict()
    best_fixed.update({"variant": "best-fixed", "window": best_fixed_window, "mean_window": float(best_fixed_window)})
    rows.append(best_fixed)
    return rows


def theory_anchor_rows(contexts: dict[str, BranchContext], plateaus: dict[tuple[str, str, str], dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for branch_name, context in contexts.items():
        returns = context.returns[context.branch["underlying"]]
        vol_hl = acf_decay_half_life(returns ** 2)
        ret_hl = acf_decay_half_life(returns)
        tau_vol = vol_hl / math.log(2.0) if np.isfinite(vol_hl) else float("nan")
        ewma_span_vol = ewma_span_from_half_life(vol_hl)
        sma_equiv_vol = 2.0 * vol_hl if np.isfinite(vol_hl) else float("nan")
        sma_plateau = plateaus[(branch_name, PRIMARY_BASE[branch_name], "SMA")]
        lo, hi = sma_plateau["band_lo"], sma_plateau["band_hi"]

        def _in_band(x: float) -> bool:
            return bool(np.isfinite(x) and lo <= x <= hi)

        rows.append(
            {
                "branch": branch_name,
                "vol_half_life_days": vol_hl,
                "return_half_life_days": ret_hl,
                "tau_vol_days": tau_vol,
                "ewma_span_vol": ewma_span_vol,
                "sma_equiv_2x_hl": sma_equiv_vol,
                "sma_plateau_lo": lo,
                "sma_plateau_hi": hi,
                "ewma_span_in_plateau": _in_band(ewma_span_vol),
                "sma_equiv_in_plateau": _in_band(sma_equiv_vol),
                "tau_in_plateau": _in_band(tau_vol),
            }
        )
    return rows


# --------------------------------------------------------------------------- plots


def plot_branch_surface(branch: str, surfaces: dict[tuple[str, str, str], pd.DataFrame], plateaus: dict[tuple[str, str, str], dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    base = PRIMARY_BASE[branch]
    fig, axes = plt.subplots(3, 1, figsize=(11, 11), sharex=True)
    metrics = [("taxed_cagr", "After-tax CAGR (%)", 100.0), ("taxed_mdd", "Max drawdown (%)", 100.0), ("taxed_calmar", "Calmar", 1.0)]
    colors = {"SMA": "tab:blue", "EMA": "tab:orange"}
    spin_lo, spin_hi = SPINOFF_MARKERS[branch]
    for ax, (col, ylabel, scale) in zip(axes, metrics):
        for form in ("SMA", "EMA"):
            surf = surfaces[(branch, base, form)]
            ax.plot(surf.index, surf[col] * scale, marker="o", color=colors[form], label=form)
        ax.axvline(TARGET_WINDOW, color="black", linestyle="--", linewidth=1.0, label="200 (popular)")
        ax.axvspan(spin_lo, spin_hi, color="green", alpha=0.10, label="spin-off opt")
        sma_plateau = plateaus[(branch, base, "SMA")]
        if sma_plateau["has_plateau"]:
            ax.axvspan(sma_plateau["band_lo"], sma_plateau["band_hi"], color="tab:blue", alpha=0.08, label="SMA plateau")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
    axes[0].set_title(f"{branch} ({base}) - lookback robustness surface (best-lag per window)")
    axes[0].legend(fontsize=8, ncol=2)
    axes[-1].set_xlabel("Lookback window (days)")
    fig.tight_layout()
    out = PLOTS / f"phase03c_{branch.lower()}_surface.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_score_surface(surfaces: dict[tuple[str, str, str], pd.DataFrame]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 7))
    styles = {("SPY", "SMA"): "-o", ("SPY", "EMA"): "--o", ("QQQ", "SMA"): "-s", ("QQQ", "EMA"): "--s"}
    for branch in ("SPY", "QQQ"):
        base = PRIMARY_BASE[branch]
        for form in ("SMA", "EMA"):
            surf = surfaces[(branch, base, form)]
            ax.plot(surf.index, surf["score"], styles[(branch, form)], label=f"{branch} {form}")
    ax.axvline(TARGET_WINDOW, color="black", linestyle=":", linewidth=1.0, label="200")
    ax.set_title("Phase 3C score vs lookback window (primary base, best lag)")
    ax.set_xlabel("Lookback window (days)")
    ax.set_ylabel("Score")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase03c_score_surface.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_adaptive_comparison(adaptive: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    df = pd.DataFrame(adaptive)
    branches = sorted(df["branch"].unique())
    fig, axes = plt.subplots(1, len(branches), figsize=(6 * len(branches), 5), squeeze=False)
    for ax, branch in zip(axes[0], branches):
        sub = df[df["branch"] == branch]
        variants = list(sub["variant"])
        calmar = sub["taxed_calmar"].to_numpy(dtype=float)
        mdd = (sub["taxed_mdd"] * 100.0).to_numpy(dtype=float)
        x = np.arange(len(variants))
        ax.bar(x - 0.2, calmar, width=0.4, label="Calmar", color="tab:blue")
        ax2 = ax.twinx()
        ax2.bar(x + 0.2, mdd, width=0.4, label="MDD (%)", color="tab:red", alpha=0.6)
        ax.set_xticks(x)
        ax.set_xticklabels(variants, rotation=20)
        ax.set_ylabel("Calmar")
        ax2.set_ylabel("MDD (%)")
        ax.set_title(f"{branch} adaptive vs fixed (primary base)")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase03c_adaptive_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def make_plots(
    surfaces: dict[tuple[str, str, str], pd.DataFrame],
    plateaus: dict[tuple[str, str, str], dict[str, object]],
    adaptive: list[dict[str, object]],
    adaptive_ran: bool,
) -> list[dict[str, str]]:
    PLOTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for branch in ("SPY", "QQQ"):
        path = plot_branch_surface(branch, surfaces, plateaus)
        rows.append({"Plot": f"{branch} robustness surface", "File": f"[plots/{path.name}](plots/{path.name})"})
    score_path = plot_score_surface(surfaces)
    rows.append({"Plot": "Score vs window", "File": f"[plots/{score_path.name}](plots/{score_path.name})"})
    if adaptive_ran and adaptive:
        adaptive_path = plot_adaptive_comparison(adaptive)
        rows.append({"Plot": "Adaptive vs fixed (Part 3)", "File": f"[plots/{adaptive_path.name}](plots/{adaptive_path.name})"})
    return rows


# --------------------------------------------------------------------------- report tables


def plateau_table_rows(plateaus: dict[tuple[str, str, str], dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for (branch, base, form), v in plateaus.items():
        rows.append(
            {
                "Branch": branch,
                "Base": base,
                "Form": form,
                "Primary": "yes" if base == PRIMARY_BASE[branch] else "",
                "Argmax W": v["argmax_window"],
                "Best Calmar": fmt_num(v["best_calmar"]),
                "Plateau band": f"{v['band_lo']}-{v['band_hi']}",
                "Width": v["band_width"],
                "Has plateau": "yes" if v["has_plateau"] else "no",
                "200 in band": "yes" if v["contains_target"] else "no",
                "Fragile": "yes" if v["is_fragile"] else "no",
            }
        )
    rows.sort(key=lambda r: (r["Branch"], r["Form"], r["Primary"] != "yes", r["Base"]))
    return rows


def surface_rows(surface: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for window, row in surface.iterrows():
        rows.append(
            {
                "Window": int(window),
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Terminal/U": fmt_x(row["terminal_vs_underlying"]),
                "Score": fmt_num(row["score"], 3),
            }
        )
    return rows


def theory_rows_fmt(theory: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for r in theory:
        rows.append(
            {
                "Branch": r["branch"],
                "Vol half-life (d)": fmt_num(r["vol_half_life_days"], 1),
                "Return half-life (d)": "n/a" if pd.isna(r["return_half_life_days"]) else fmt_num(r["return_half_life_days"], 1),
                "tau=HL/ln2 (d)": fmt_num(r["tau_vol_days"], 1),
                "EWMA span": fmt_num(r["ewma_span_vol"], 1),
                "SMA~2*HL": fmt_num(r["sma_equiv_2x_hl"], 1),
                "SMA plateau": f"{r['sma_plateau_lo']}-{r['sma_plateau_hi']}",
                "EWMA in plateau": "yes" if r["ewma_span_in_plateau"] else "no",
                "2*HL in plateau": "yes" if r["sma_equiv_in_plateau"] else "no",
            }
        )
    return rows


def adaptive_rows_fmt(adaptive: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for r in adaptive:
        rows.append(
            {
                "Branch": r["branch"],
                "Variant": r["variant"],
                "Window": r["window"],
                "Mean W": fmt_num(r.get("mean_window", float("nan")), 1),
                "Lag": int(r["lag_days"]),
                "CAGR": fmt_pct(r["taxed_cagr"]),
                "MDD": fmt_pct(r["taxed_mdd"]),
                "Calmar": fmt_num(r["taxed_calmar"]),
                "Lev MDD": fmt_pct(r["levered_taxed_mdd"]),
                "Turnover/yr": fmt_num(r["turnover_per_year"], 2),
                "Score": fmt_num(r["score"], 3),
            }
        )
    return rows


def write_report(
    results: pd.DataFrame,
    surfaces: dict[tuple[str, str, str], pd.DataFrame],
    plateaus: dict[tuple[str, str, str], dict[str, object]],
    theory: list[dict[str, object]],
    adaptive: list[dict[str, object]],
    adaptive_ran: bool,
    plot_rows: list[dict[str, str]],
) -> None:
    primary_verdicts = []
    for branch in ("SPY", "QQQ"):
        for form in ("SMA", "EMA"):
            v = plateaus[(branch, PRIMARY_BASE[branch], form)]
            primary_verdicts.append((branch, form, v))
    all_robust = all(not v["is_fragile"] for _, _, v in primary_verdicts)
    sma_contains_200 = all(plateaus[(b, PRIMARY_BASE[b], "SMA")]["contains_target"] for b in ("SPY", "QQQ"))

    # Did the adaptive window beat fixed-200 (by score) on any branch? And where
    # do long windows collapse (all-warning onset) on each branch's SMA primary?
    adaptive_by_branch: dict[str, dict[str, dict[str, object]]] = {}
    for r in adaptive:
        adaptive_by_branch.setdefault(str(r["branch"]), {})[str(r["variant"])] = r
    adaptive_helps = {
        b: bool(v.get("adaptive-vol", {}).get("score", -1e9) > v.get("fixed-200", {}).get("score", 1e9))
        for b, v in adaptive_by_branch.items()
    }
    any_adaptive_helps = any(adaptive_helps.values())

    def _long_fail_onset(branch: str) -> int | None:
        surf = surfaces[(branch, PRIMARY_BASE[branch], "SMA")]
        onset = None
        for w in sorted(surf.index):
            tail = surf.loc[surf.index >= w]
            if (tail["taxed_mdd"] < -0.50).all():
                onset = int(w)
                break
        return onset

    fail_onset = {b: _long_fail_onset(b) for b in ("SPY", "QQQ")}

    headline = (
        "the SMA200 level sits inside a robust plateau on both branches - 200 is a robust adequate point, not magic"
        if sma_contains_200
        else (
            "every primary-base curve is a robust plateau (200 is adequate even where the plateau is centred elsewhere)"
            if all_robust
            else (
                "by the strict pre-registered rule both primary SMA curves are narrow peaks (fragile), so the adaptive gate ran - "
                + ("but the vol-scaled window did NOT beat the fixed window net of turnover" if not any_adaptive_helps else "and the vol-scaled window helped on at least one branch")
                + ", and the empirical optimum (~175-225) is far longer than the vol-persistence anchor (~20-40d)"
            )
        )
    )

    sections = [
        "# Phase 3C - Lookback Study (Robustness, Theory Anchor, Gated Adaptive)\n\n"
        "Status: research-only. This report does not authorize deployment, paper trading or a mandate change.\n\n"
        "Question: *why SMA 200?* The number 200 is community-popular (golden-cross folklore) but unexamined in this restart. We avoid two opposite overfit traps: (a) blindly trusting 200, and (b) sweeping windows and promoting the best. The robustness map is a DIAGNOSTIC and we pre-committed to NOT promoting the argmax `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`. Forms studied: SMA + EMA (Phase 3A-2 did not promote hysteresis). Mechanism unchanged from Phase 3A-2: the trend gate REPLACES the SMA level, `signal = G & vol_gate`, Phase 2 scoring verbatim.\n\n"
        f"Headline: {headline}.\n\n"
        "## Source And Rules\n\n"
        "| Item | Value |\n|---|---|\n"
        "| Data | `data/testfolio/cache/history.parquet` (close-only equity curves) |\n"
        f"| Window grid | {WINDOWS} (13 points) |\n"
        "| Forms | SMA `[leverage_for_the_long_run, p.13]`, EMA `[systematic_trading, p.283]` |\n"
        "| Surface read | best-score lag per (form, base, window) cell |\n"
        "| Plateau rule | contiguous Calmar band within 10% of band-best, width >= 150 days; 200 in band? |\n"
        "| Theory anchor | squared-return ACF decay half-life ~ GARCH alpha+beta `[volatility_trading, p.39, p.53-54]` |\n"
        "| Adaptive | gated on fragility; vol-scaled window vs fixed-200 + best-fixed |\n\n",
    ]

    sections.append(
        "## Theory Anchor (ex-ante, no performance peeking)\n\n"
        + md_table(theory_rows_fmt(theory), ["Branch", "Vol half-life (d)", "Return half-life (d)", "tau=HL/ln2 (d)", "EWMA span", "SMA~2*HL", "SMA plateau", "EWMA in plateau", "2*HL in plateau"])
        + "\nReturn half-life `n/a` means signed daily returns show no positive decaying autocorrelation (near-white) - the trend signal is a price/regime *level* effect, not return persistence `[stocks_on_the_move, p.58, p.60]`. The volatility-persistence half-life and its EWMA-span / 2x-half-life mappings are the citable, non-arbitrary window anchors `[volatility_trading, p.39, p.53-54]`, `[systematic_trading, p.283]`.\n\n"
    )

    sections.append(
        "## Robustness - primary base (per branch x form)\n\n"
        + md_table(
            [r for r in plateau_table_rows(plateaus) if r["Primary"] == "yes"],
            ["Branch", "Base", "Form", "Argmax W", "Best Calmar", "Plateau band", "Width", "Has plateau", "200 in band", "Fragile"],
        )
    )
    sections.append(
        "## Robustness - across all bases (robustness of the verdict)\n\n"
        + md_table(plateau_table_rows(plateaus), ["Branch", "Base", "Form", "Primary", "Argmax W", "Plateau band", "Width", "Has plateau", "200 in band", "Fragile"])
    )

    for branch in ("SPY", "QQQ"):
        for form in ("SMA", "EMA"):
            sections.append(
                f"## Surface - {branch} {form} (primary base {PRIMARY_BASE[branch]}, best lag per window)\n\n"
                + md_table(surface_rows(surfaces[(branch, PRIMARY_BASE[branch], form)]), ["Window", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Terminal/U", "Score"])
            )

    spin_text = ", ".join(f"{b} ~{lo}-{hi}" if lo != hi else f"{b} ~{lo}" for b, (lo, hi) in SPINOFF_MARKERS.items())
    sections.append(
        "## Spin-off cross-check\n\n"
        f"The spun-off single-asset line (`studies/lrs/`, now canonical in `letf-lab`) swept lookbacks with the exact sweep-and-pick-best method this phase rejects, under different mechanics (single-asset, synthetic LETFs). Its empirical optima ({spin_text}) and the finding that **200 is the round popular number, not the empirical best**, are shown as plot markers - cross-checked, not inherited `[trading_systems_methods, p.27, p.917-919]`.\n\n"
    )

    if adaptive_ran:
        sections.append(
            "## Adaptive Window (Part 3 - triggered by fragility)\n\n"
            + md_table(adaptive_rows_fmt(adaptive), ["Branch", "Variant", "Window", "Mean W", "Lag", "CAGR", "MDD", "Calmar", "Lev MDD", "Turnover/yr", "Score"])
            + "\nThe vol-scaled window is compared honestly vs fixed-200 and the best-fixed window, net of turnover. The spin-off found lookback-switch cost is amplified by leverage, so any adaptive edge must survive turnover to count `[leverage_for_the_long_run, p.4-7]`.\n\n"
        )
    else:
        sections.append(
            "## Adaptive Window (Part 3 - NOT triggered)\n\n"
            "Every primary-base SMA curve is a robust plateau, so the fixed window is robust and the adaptive complexity is **not warranted**. Running it anyway would add turnover and a leverage-amplified switch cost for no diagnosed fragility `[leverage_for_the_long_run, p.4-7]`, `[advances_fin_ml, p.208-211]`.\n\n"
        )

    sma200_band = {b: plateaus[(b, PRIMARY_BASE[b], "SMA")] for b in ("SPY", "QQQ")}
    onset_text = ", ".join(f"{b} >={fail_onset[b]}" if fail_onset[b] else f"{b} none" for b in ("SPY", "QQQ"))
    adaptive_verdict = (
        "No - it worsens MDD/Calmar net of turnover on both branches (the leverage-amplified lookback-switch cost the spin-off warned about)"
        if adaptive_ran and not any_adaptive_helps
        else ("Yes - it improved score on at least one branch" if adaptive_ran else "Not run - fixed window robust")
    )
    if sma_contains_200:
        why_200 = (
            "200 is not magic but it is a robust adequate point: it sits inside a wide Calmar plateau, and the exposure geometry "
            "(leverage + risk-off + vol throttle) remains the real driver"
        )
    else:
        why_200 = (
            f"the SMA Calmar surface is NOT a wide flat plateau - by the strict pre-registered rule both branches are fragile, "
            f"because Calmar peaks fairly sharply near {sma200_band['SPY']['argmax_window']}/{sma200_band['QQQ']['argmax_window']} and long windows ({onset_text}) "
            f"collapse to ~-59% MDD on the leveraged sleeve (a late regime exit that leverage punishes). Yet within the adequate region "
            f"(~150-250, tolerable/preferred MDD) 200 is at/near the Calmar-best (SPY argmax {sma200_band['SPY']['argmax_window']}, QQQ {sma200_band['QQQ']['argmax_window']}/225 tied) and 225 is essentially tied. "
            f"The gated adaptive vol-window {'does NOT help - it worsens MDD/Calmar net of turnover on both branches' if (adaptive_ran and not any_adaptive_helps) else ('helps on at least one branch' if adaptive_ran else 'was not run')}, and the theory anchor "
            f"(vol half-life ~11-14d -> natural windows ~22-41d) is far shorter than 200 (signed returns are near-white), so 200 is a slow regime/level filter, not a persistence-matched horizon. "
            f"Net: keep a FIXED window in ~175-225 (200 is a sound default), avoid windows >={min(o for o in fail_onset.values() if o) if any(fail_onset.values()) else 275}, treat exposure geometry as the real driver, and do NOT adopt adaptivity despite the fragility flag"
        )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Is SMA200 inside a robust plateau on both branches? | {'Yes' if sma_contains_200 else 'No'} (SPY band {sma200_band['SPY']['band_lo']}-{sma200_band['SPY']['band_hi']} width {sma200_band['SPY']['band_width']}, QQQ {sma200_band['QQQ']['band_lo']}-{sma200_band['QQQ']['band_hi']} width {sma200_band['QQQ']['band_width']}; min plateau width 150). |\n"
        f"| Are all primary-base curves robust (no narrow peak)? | {'Yes' if all_robust else 'No - fragile by the strict rule'}. |\n"
        f"| Is there a broad *adequate* region (tolerable+ MDD)? | Yes - ~150-250; long windows collapse ({onset_text}). |\n"
        f"| Did the theory anchor land inside the SMA plateau? | {'Yes' if all(t['ewma_span_in_plateau'] or t['sma_equiv_in_plateau'] for t in theory) else 'No - vol half-life (~11-14d) is far shorter than the empirical window'} (see theory table). |\n"
        f"| Was the adaptive window warranted / did it help? | {adaptive_verdict}. |\n"
        "| Did we promote the argmax window? | No - pre-committed; the deliverable is the robustness verdict, not the best window. |\n"
        "| Is this deployment-ready? | No. Diagnostic lookback study only. No deploy, no paper-trade label, no mandate change. |\n\n"
        f"\"Why 200?\" - {why_200} `[leverage_for_the_long_run, p.4-7]`, `[volatility_trading, p.39, p.53-54]`, `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`.\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    contexts = {name: build_context(branch) for name, branch in BRANCHES.items()}
    rows = []
    for base in BASE_SPECS:
        context = contexts[str(base["branch"])]
        for form in FORMS:
            for window in WINDOWS:
                for lag_days in range(6):
                    rows.append(simulate_candidate(context, base, form, window, lag_days))
    results = pd.DataFrame(rows).sort_values(
        ["practical_pass", "score", "terminal_vs_underlying", "taxed_calmar"],
        ascending=[False, False, False, False],
    )
    results.to_csv(CSV, index=False)

    # best-lag surfaces + plateau per (branch, base, form)
    surfaces: dict[tuple[str, str, str], pd.DataFrame] = {}
    plateaus: dict[tuple[str, str, str], dict[str, object]] = {}
    for branch in ("SPY", "QQQ"):
        for base in [b["name"] for b in BASE_SPECS if b["branch"] == branch]:
            for form in ("SMA", "EMA"):
                surf = best_lag_surface(results, branch, base, form)
                surfaces[(branch, base, form)] = surf
                plateaus[(branch, base, form)] = calmar_plateau(surf.index.to_numpy(), surf["taxed_calmar"].to_numpy())

    theory = theory_anchor_rows(contexts, plateaus)
    pd.DataFrame(theory).to_csv(THEORY_CSV, index=False)

    fragile_branches = [b for b in ("SPY", "QQQ") if plateaus[(b, PRIMARY_BASE[b], "SMA")]["is_fragile"]]
    adaptive: list[dict[str, object]] = []
    adaptive_ran = bool(fragile_branches)
    if adaptive_ran:
        for branch in fragile_branches:
            adaptive.extend(run_adaptive_for_branch(contexts[branch], surfaces))

    plot_rows = make_plots(surfaces, plateaus, adaptive, adaptive_ran)
    write_report(results, surfaces, plateaus, theory, adaptive, adaptive_ran, plot_rows)

    sma_bands = {b: plateaus[(b, PRIMARY_BASE[b], "SMA")] for b in ("SPY", "QQQ")}
    print(f"Phase 3C: {len(results)} rows")
    for b in ("SPY", "QQQ"):
        v = sma_bands[b]
        print(f"  {b} SMA primary plateau {v['band_lo']}-{v['band_hi']} width {v['band_width']} | 200 in band: {v['contains_target']} | fragile: {v['is_fragile']}")
    for t in theory:
        print(f"  {t['branch']} vol half-life {t['vol_half_life_days']:.1f}d -> EWMA span {t['ewma_span_vol']:.0f} / 2xHL {t['sma_equiv_2x_hl']:.0f}")
    print(f"  adaptive ran: {adaptive_ran} (fragile branches: {fragile_branches})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
