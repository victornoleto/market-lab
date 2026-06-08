"""Phase 3A-2 - alternative regime signals as REPLACEMENTS for the SMA gate.

Research-only. This runner does NOT authorize deployment, paper trading or any
mandate change. Phase 3A showed that ANDing a confirmation filter onto the
`price > SMA200` base can only further restrict risk-on; a hysteresis band as an
AND-gate was identical to `none` in 36/36 configs. So here each alternative
regime signal G REPLACES the SMA trend gate and is compared head-to-head against
the SMA200 control over the Phase 2 exposure geometry::

    signal = G(underlying) & vol_gate(base.vol)

`G = SMA200` reproduces the Phase 2 result for that base+lag exactly, which is a
built-in sanity check against `lrs/results/phase02_target_leverage_vol.csv`.

Lookback is held FIXED at 200 across all forms to isolate signal *form* from
*window*; the window question is entirely Phase 3C's `[trading_systems_methods,
p.939]`, `[advances_fin_ml, p.208-211]`.

Grid: 2 branches x 3 branch-specific bases x 6 regime forms x lag 0..5 = 216 rows.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
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
    clenow_gate,
    ema_gate,
    roc_gate,
    trend_hysteresis_gate,
)


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase03b_regime_signals.csv"
PHASE2_CSV = RESULTS / "phase02_target_leverage_vol.csv"

BRANCHES = {
    "SPY": {"branch": "SPY", "underlying": "SPYSIM", "lev2": "SSOSIM", "lev3": "UPROSIM"},
    "QQQ": {"branch": "QQQ", "underlying": "QQQSIM", "lev2": "QLDSIM", "lev3": "TQQQSIM"},
}

# Named risk-off sleeves and vol throttles reused verbatim from Phase 2 / 3A.
RISK_OFF_LIBRARY: dict[str, dict[str, float]] = {
    "50 ZROZ / 25 GLD / 25 CASH": {"ZROZSIM": 0.50, "GLDSIM": 0.25, "CASHX": 0.25},
    "40 ZROZ / 40 GLD / 20 IEF": {"ZROZSIM": 0.40, "GLDSIM": 0.40, "IEFSIM": 0.20},
}

VOL_LIBRARY: dict[str, dict[str, object]] = {
    "RV21 <= 30%": {"name": "RV21 <= 30%", "window": 21, "threshold": 0.30},
    "RV63 <= 40%": {"name": "RV63 <= 40%", "window": 63, "threshold": 0.40},
}

# Phase 2 top per branch + 2 one-lever neighbours - identical to Phase 3A so the
# SMA200 control rows match Phase 2/3A exactly `[advances_fin_ml, p.208-211]`.
BASE_SPECS: list[dict[str, object]] = [
    {"branch": "SPY", "name": "spy_top", "target_leverage": 2.00, "risk_off": "50 ZROZ / 25 GLD / 25 CASH", "vol": "RV21 <= 30%"},
    {"branch": "SPY", "name": "spy_lower_lev", "target_leverage": 1.75, "risk_off": "50 ZROZ / 25 GLD / 25 CASH", "vol": "RV21 <= 30%"},
    {"branch": "SPY", "name": "spy_alt_off", "target_leverage": 2.00, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV21 <= 30%"},
    {"branch": "QQQ", "name": "qqq_top", "target_leverage": 1.75, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV63 <= 40%"},
    {"branch": "QQQ", "name": "qqq_lower_lev", "target_leverage": 1.50, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV63 <= 40%"},
    {"branch": "QQQ", "name": "qqq_alt_vol", "target_leverage": 1.75, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV21 <= 30%"},
]

# Alternative regime signals. `SMA200` is the control; lookback/window/span all
# fixed at 200 to isolate form from window (Phase 3C owns the window question).
REGIME_FORMS: list[dict[str, object]] = [
    {"name": "SMA200", "family": "control", "kind": "sma", "lookback": 200},
    {"name": "EMA200", "family": "ema", "kind": "ema", "span": 200},
    {"name": "hyst200 band5%", "family": "hysteresis", "kind": "hysteresis", "lookback": 200, "band": 0.05},
    {"name": "hyst200 band8%", "family": "hysteresis", "kind": "hysteresis", "lookback": 200, "band": 0.08},
    {"name": "ROC200>0", "family": "roc", "kind": "roc", "lookback": 200},
    {"name": "Clenow200>0", "family": "clenow", "kind": "clenow", "window": 200},
]

CONTROL_FORM = "SMA200"


def build_regime_gate(prices: pd.Series, spec: dict[str, object]) -> pd.Series:
    """Dispatch a regime-form spec to its boolean gate (all `.shift(1)`-lagged).

    Each gate REPLACES the SMA trend component (it is not ANDed onto it). The
    `sma` control dispatches to `build_sma_signal`, so the SMA200 form reproduces
    the Phase 2 base signal exactly `[leverage_for_the_long_run, p.13]`.
    """
    kind = spec["kind"]
    if kind == "sma":
        return build_sma_signal(prices, int(spec["lookback"]))
    if kind == "ema":
        return ema_gate(prices, int(spec["span"]))
    if kind == "hysteresis":
        return trend_hysteresis_gate(prices, int(spec["lookback"]), float(spec["band"]))
    if kind == "roc":
        return roc_gate(prices, int(spec["lookback"]))
    if kind == "clenow":
        return clenow_gate(prices, int(spec["window"]))
    raise ValueError(f"unknown regime form kind: {kind}")


@dataclass
class BranchContext:
    branch: dict[str, str]
    prices: pd.DataFrame
    returns: pd.DataFrame
    underlying_taxed: pd.Series
    underlying_gross: pd.Series
    underlying_metrics: object
    benchmark_by_l: dict[float, pd.Series]
    benchmark_metrics_by_l: dict[float, object]
    regime_gates: dict[str, pd.Series]


def branch_assets(branch: dict[str, str]) -> list[str]:
    assets = {branch["underlying"], branch["lev2"], branch["lev3"], "CASHX", "GLDSIM", "IEFSIM", "ZROZSIM"}
    return sorted(assets)


def target_leverage_weights(branch: dict[str, str], target_leverage: float) -> dict[str, float]:
    """Map target leverage to adjacent ETF sleeves without external margin
    (same construction as Phase 2/3A) `[leverage_for_the_long_run, p.13]`."""
    if target_leverage < 1.0 or target_leverage > 3.0:
        raise ValueError(f"target leverage out of range: {target_leverage}")
    if target_leverage <= 2.0:
        return clean_weights(
            {
                branch["underlying"]: 2.0 - target_leverage,
                branch["lev2"]: target_leverage - 1.0,
            }
        )
    return clean_weights(
        {
            branch["lev2"]: 3.0 - target_leverage,
            branch["lev3"]: target_leverage - 2.0,
        }
    )


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
    underlying_gross, _ = simulate_weight_frame(returns, underlying_frame, taxable=False)
    benchmark_by_l: dict[float, pd.Series] = {}
    benchmark_metrics_by_l: dict[float, object] = {}
    for target_leverage in base_leverages(branch["branch"]):
        frame = constant_weight_frame(returns.index, target_leverage_weights(branch, target_leverage))
        taxed, _ = simulate_weight_frame(returns, frame, taxable=True)
        benchmark_by_l[target_leverage] = taxed
        benchmark_metrics_by_l[target_leverage] = metrics_from_returns(taxed)
    underlying_prices = prices[branch["underlying"]]
    regime_gates: dict[str, pd.Series] = {}
    for spec in REGIME_FORMS:
        gate = build_regime_gate(underlying_prices, spec)
        regime_gates[str(spec["name"])] = gate.reindex(returns.index).fillna(False).astype(bool)
    return BranchContext(
        branch=branch,
        prices=prices,
        returns=returns,
        underlying_taxed=underlying_taxed,
        underlying_gross=underlying_gross,
        underlying_metrics=metrics_from_returns(underlying_taxed),
        benchmark_by_l=benchmark_by_l,
        benchmark_metrics_by_l=benchmark_metrics_by_l,
        regime_gates=regime_gates,
    )


def vol_gate(context: BranchContext, spec: dict[str, object]) -> pd.Series:
    if spec["threshold"] is None:
        return pd.Series(True, index=context.returns.index)
    window = int(spec["window"])
    threshold = float(spec["threshold"])
    underlying_returns = context.returns[context.branch["underlying"]]
    realized_vol = underlying_returns.rolling(window).std(ddof=0).shift(1) * np.sqrt(252.0)
    return (realized_vol <= threshold).reindex(context.returns.index).fillna(False)


def desired_targets(
    context: BranchContext,
    target_leverage: float,
    risk_off_weights: dict[str, float],
    vol_spec: dict[str, object],
    regime_gate: pd.Series,
) -> pd.DataFrame:
    risk_on = target_leverage_weights(context.branch, target_leverage)
    gate = regime_gate.reindex(context.returns.index).fillna(False).astype(bool)
    # Phase 3A-2 mechanism: the regime gate REPLACES the SMA trend gate; the only
    # AND is with the realized-vol throttle (kept from Phase 2 geometry).
    signal = gate & vol_gate(context, vol_spec)
    assets = sorted(set(risk_on) | set(risk_off_weights) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=context.returns.index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on.get(asset, 0.0), risk_off_weights.get(asset, 0.0))
    return desired


def simulate_candidate(
    context: BranchContext,
    base: dict[str, object],
    form_spec: dict[str, object],
    lag_days: int,
) -> dict[str, object]:
    target_leverage = float(base["target_leverage"])
    risk_off_weights = clean_weights(RISK_OFF_LIBRARY[str(base["risk_off"])])
    vol_spec = VOL_LIBRARY[str(base["vol"])]
    risk_on_weights = target_leverage_weights(context.branch, target_leverage)
    regime_gate = context.regime_gates[str(form_spec["name"])]
    desired = desired_targets(context, target_leverage, risk_off_weights, vol_spec, regime_gate)
    weights, schedule_summary = build_weekly_lagged_weights(
        desired,
        lag_days=lag_days,
        risk_on_weights=risk_on_weights,
    )
    gross, _ = simulate_weight_frame(context.returns, weights, taxable=False)
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    taxed_metrics = metrics_from_returns(taxed)
    gross_metrics = metrics_from_returns(gross)
    benchmark = context.benchmark_by_l[target_leverage]
    benchmark_metrics = context.benchmark_metrics_by_l[target_leverage]
    rel_underlying = relative_stats(taxed, context.underlying_taxed)
    rel_benchmark = relative_stats(taxed, benchmark)
    cagr_spread = taxed_metrics.cagr - context.underlying_metrics.cagr
    # Phase 2 scoring kept verbatim for cross-phase comparability (user decision).
    drawdown_component = max(-1.0, min(1.0, (taxed_metrics.mdd + 0.65) / 0.25))
    score = (
        6.0 * cagr_spread
        + 2.25 * taxed_metrics.calmar
        + 0.75 * taxed_metrics.sortino
        + 1.00 * rel_underlying.get("hit_10y", 0.0)
        + 1.75 * drawdown_component
        + 0.25 * rel_underlying["worst_relative_drawdown"]
        - 0.10 * float(tax_summary["turnover_per_year"])
    )
    return {
        "branch": context.branch["branch"],
        "base_name": base["name"],
        "regime_form": form_spec["name"],
        "regime_family": form_spec["family"],
        "target_leverage": target_leverage,
        "lag_days": lag_days,
        "lookback": 200,
        "cadence": "weekly",
        "risk_on": weights_label(risk_on_weights),
        "risk_off_name": base["risk_off"],
        "risk_off_weights": weights_label(risk_off_weights),
        "vol_filter": vol_spec["name"],
        "start": taxed_metrics.start,
        "end": taxed_metrics.end,
        "years": taxed_metrics.years,
        "score": score,
        "drawdown_tier": drawdown_tier(taxed_metrics.mdd),
        "practical_pass": bool(cagr_spread > 0.0 and taxed_metrics.mdd >= -0.50 and rel_underlying["terminal_vs_benchmark"] > 1.0),
        "gross_cagr": gross_metrics.cagr,
        "gross_mdd": gross_metrics.mdd,
        "taxed_cagr": taxed_metrics.cagr,
        "taxed_mdd": taxed_metrics.mdd,
        "taxed_sharpe": taxed_metrics.sharpe,
        "taxed_sortino": taxed_metrics.sortino,
        "taxed_calmar": taxed_metrics.calmar,
        "taxed_terminal": taxed_metrics.terminal,
        "underlying_taxed_cagr": context.underlying_metrics.cagr,
        "underlying_taxed_mdd": context.underlying_metrics.mdd,
        "underlying_taxed_terminal": context.underlying_metrics.terminal,
        "levered_taxed_cagr": benchmark_metrics.cagr,
        "levered_taxed_mdd": benchmark_metrics.mdd,
        "levered_taxed_terminal": benchmark_metrics.terminal,
        "cagr_spread_vs_underlying": cagr_spread,
        "mdd_spread_vs_underlying": taxed_metrics.mdd - context.underlying_metrics.mdd,
        "terminal_vs_underlying": rel_underlying["terminal_vs_benchmark"],
        "terminal_vs_levered_bh": rel_benchmark["terminal_vs_benchmark"],
        "worst_relative_dd_vs_underlying": rel_underlying["worst_relative_drawdown"],
        "worst_relative_dd_vs_levered_bh": rel_benchmark["worst_relative_drawdown"],
        "hit_3y_vs_underlying": rel_underlying.get("hit_3y", pd.NA),
        "hit_5y_vs_underlying": rel_underlying.get("hit_5y", pd.NA),
        "hit_10y_vs_underlying": rel_underlying.get("hit_10y", pd.NA),
        "hit_15y_vs_underlying": rel_underlying.get("hit_15y", pd.NA),
        "hit_20y_vs_underlying": rel_underlying.get("hit_20y", pd.NA),
        "turnover_per_year": tax_summary["turnover_per_year"],
        "trade_count": tax_summary["trade_count"],
        "state_changes": schedule_summary["state_changes"],
        "delayed_entries": schedule_summary["delayed_entries"],
        "pct_risk_on_days": schedule_summary["pct_risk_on_days"],
        "tax_paid_pct_initial": tax_summary["total_tax_paid_pct_initial"],
        "tax_events": tax_summary["tax_events"],
        "final_taxed_equity": float(equity_curve(taxed).iloc[-1]),
        "final_underlying_taxed_equity": float(equity_curve(context.underlying_taxed).iloc[-1]),
        "final_levered_taxed_equity": float(equity_curve(benchmark).iloc[-1]),
        "gross_vs_tax_cagr_drag": gross_metrics.cagr - taxed_metrics.cagr,
    }


def sma200_sanity_max_diff(results: pd.DataFrame) -> tuple[float, int]:
    """Cross-check: the SMA200 control form must reproduce the Phase 2 base+lag
    rows exactly (same `sma & vol` geometry). Returns (max abs diff in after-tax
    CAGR/MDD across matched rows, number of matched rows). Diff should be ~0."""
    if not PHASE2_CSV.exists():
        return float("nan"), 0
    phase2 = pd.read_csv(PHASE2_CSV)
    key = ["branch", "target_leverage", "risk_off_name", "vol_filter", "lag_days"]
    sma_rows = results[results["regime_form"] == CONTROL_FORM].copy()
    merged = sma_rows.merge(phase2[key + ["taxed_cagr", "taxed_mdd"]], on=key, suffixes=("", "_p2"))
    if merged.empty:
        return float("nan"), 0
    diff_cagr = (merged["taxed_cagr"] - merged["taxed_cagr_p2"]).abs()
    diff_mdd = (merged["taxed_mdd"] - merged["taxed_mdd_p2"]).abs()
    return float(max(diff_cagr.max(), diff_mdd.max())), int(len(merged))


def simulate_paths_for_row(row: pd.Series, context: BranchContext) -> dict[str, pd.Series]:
    base = next(b for b in BASE_SPECS if b["name"] == row["base_name"])
    form_spec = next(spec for spec in REGIME_FORMS if spec["name"] == row["regime_form"])
    risk_off_weights = clean_weights(RISK_OFF_LIBRARY[str(base["risk_off"])])
    vol_spec = VOL_LIBRARY[str(base["vol"])]
    regime_gate = context.regime_gates[str(form_spec["name"])]
    desired = desired_targets(context, float(base["target_leverage"]), risk_off_weights, vol_spec, regime_gate)
    weights, _ = build_weekly_lagged_weights(
        desired,
        lag_days=int(row["lag_days"]),
        risk_on_weights=target_leverage_weights(context.branch, float(base["target_leverage"])),
    )
    taxed, _ = simulate_weight_frame(context.returns, weights, taxable=True)
    benchmark = context.benchmark_by_l[float(base["target_leverage"])]
    return {"strategy": taxed, "underlying": context.underlying_taxed, "levered": benchmark}


def _safe_form(name: str) -> str:
    return str(name).lower().replace(" ", "_").replace(">", "gt").replace("%", "pct")


def plot_candidate_panel(row: pd.Series, context: BranchContext) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    paths = simulate_paths_for_row(row, context)
    aligned = pd.concat(
        {
            "LRS": equity_curve(paths["strategy"]),
            "Underlying B&H": equity_curve(paths["underlying"]),
            "Target-Lev B&H": equity_curve(paths["levered"]),
        },
        axis=1,
    ).dropna()
    dd = pd.concat(
        {
            "LRS": drawdown(paths["strategy"]),
            "Underlying B&H": drawdown(paths["underlying"]),
            "Target-Lev B&H": drawdown(paths["levered"]),
        },
        axis=1,
    ).dropna()
    relative = aligned["LRS"] / aligned["Underlying B&H"]

    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    aligned.plot(ax=axes[0], logy=True, linewidth=1.2)
    axes[0].set_title(
        f"{row['branch']} base={row['base_name']} form={row['regime_form']} "
        f"L={float(row['target_leverage']):.2f} lag={int(row['lag_days'])}"
    )
    axes[0].set_ylabel("Growth of $1")
    axes[0].grid(True, alpha=0.3)
    (dd * 100.0).plot(ax=axes[1], linewidth=1.0)
    axes[1].set_title("Drawdown")
    axes[1].set_ylabel("Drawdown (%)")
    axes[1].grid(True, alpha=0.3)
    relative.plot(ax=axes[2], linewidth=1.2, color="tab:blue")
    axes[2].axhline(1.0, color="black", linewidth=0.8, linestyle="--")
    axes[2].set_title("LRS relative equity vs underlying")
    axes[2].set_ylabel("Relative equity")
    axes[2].grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / f"phase03b_{str(row['branch']).lower()}_{row['base_name']}_{_safe_form(row['regime_form'])}_lag{int(row['lag_days'])}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(results: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 7))
    for family, subset in results.groupby("regime_family", sort=True):
        ax.scatter(
            subset["taxed_mdd"] * 100.0,
            subset["taxed_cagr"] * 100.0,
            s=24,
            alpha=0.6,
            label=family,
        )
    ax.axvline(-40.0, color="green", linestyle="--", linewidth=0.9, label="preferred 40%")
    ax.axvline(-50.0, color="black", linestyle="--", linewidth=0.9, label="tolerable 50%")
    ax.set_title("Phase 3A-2 frontier by regime family")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase03b_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_form_sensitivity(results: pd.DataFrame) -> Path:
    """Per branch, best-lag CAGR/MDD across regime forms on that branch's top base."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    form_order = [str(spec["name"]) for spec in REGIME_FORMS]
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for branch, branch_rows in results.groupby("branch", sort=True):
        top_base = branch_rows.sort_values("score", ascending=False).iloc[0]["base_name"]
        base_rows = branch_rows[branch_rows["base_name"] == top_base]
        best_per_form = base_rows.sort_values("score", ascending=False).groupby("regime_form", sort=False).head(1)
        best_per_form = best_per_form.set_index("regime_form").reindex(form_order)
        label = f"{branch} ({top_base})"
        axes[0].plot(form_order, best_per_form["taxed_cagr"] * 100.0, marker="o", label=label)
        axes[1].plot(form_order, best_per_form["taxed_mdd"] * 100.0, marker="o", label=label)
    axes[0].set_title("Regime-form sensitivity (best lag) - after-tax CAGR")
    axes[0].set_ylabel("CAGR (%)")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[1].set_title("Regime-form sensitivity (best lag) - MDD")
    axes[1].set_ylabel("MDD (%)")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    for ax in axes:
        ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    out = PLOTS / "phase03b_form_sensitivity.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def make_plots(results: pd.DataFrame, contexts: dict[str, BranchContext]) -> list[dict[str, str]]:
    PLOTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    top_by_branch = results.sort_values("score", ascending=False).groupby("branch", sort=True).head(1)
    for _, row in top_by_branch.iterrows():
        path = plot_candidate_panel(row, contexts[str(row["branch"])])
        rows.append({"Plot": f"{row['branch']} best score", "File": f"[plots/{path.name}](plots/{path.name})"})
    frontier = plot_frontier(results)
    rows.append({"Plot": "Frontier by regime family", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    sensitivity = plot_form_sensitivity(results)
    rows.append({"Plot": "Regime-form sensitivity (top base)", "File": f"[plots/{sensitivity.name}](plots/{sensitivity.name})"})
    return rows


def formatted_rows(frame: pd.DataFrame, limit: int = 30) -> list[dict[str, object]]:
    rows = []
    for _, row in frame.head(limit).iterrows():
        rows.append(
            {
                "Branch": row["branch"],
                "Base": row["base_name"],
                "Form": row["regime_form"],
                "L": fmt_num(row["target_leverage"], 2),
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Spread vs U": fmt_pp(row["cagr_spread_vs_underlying"]),
                "Terminal/U": fmt_x(row["terminal_vs_underlying"]),
                "Hit 10y": fmt_pct(row["hit_10y_vs_underlying"], 1),
                "Pass": "yes" if row["practical_pass"] else "no",
            }
        )
    return rows


def best_by_branch_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for branch, subset in results.sort_values("score", ascending=False).groupby("branch", sort=True):
        row = subset.iloc[0]
        rows.append(
            {
                "Branch": branch,
                "Base": row["base_name"],
                "Form": row["regime_form"],
                "L": fmt_num(row["target_leverage"], 2),
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Terminal/U": fmt_x(row["terminal_vs_underlying"]),
            }
        )
    return rows


def best_by_form_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    best = results.sort_values("score", ascending=False).groupby(["branch", "regime_form"], sort=True).head(1)
    for _, row in best.sort_values(["branch", "score"], ascending=[True, False]).iterrows():
        rows.append(
            {
                "Branch": row["branch"],
                "Form": row["regime_form"],
                "Family": row["regime_family"],
                "Base": row["base_name"],
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Score": fmt_num(row["score"], 3),
            }
        )
    return rows


def form_vs_sma_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    """Per branch, on that branch's top base, compare each regime form (best lag)
    to the SMA200 control on the same base. Answers: does any form beat SMA200?"""
    rows = []
    for branch, branch_rows in results.sort_values("score", ascending=False).groupby("branch", sort=True):
        top_base = branch_rows.iloc[0]["base_name"]
        base_rows = branch_rows[branch_rows["base_name"] == top_base]
        best_per_form = base_rows.sort_values("score", ascending=False).groupby("regime_form", sort=False).head(1)
        sma_row = base_rows[base_rows["regime_form"] == CONTROL_FORM].sort_values("score", ascending=False).iloc[0]
        sma_cagr = float(sma_row["taxed_cagr"])
        sma_mdd = float(sma_row["taxed_mdd"])
        sma_score = float(sma_row["score"])
        ordered = best_per_form.set_index("regime_form").reindex([str(s["name"]) for s in REGIME_FORMS]).dropna(subset=["taxed_cagr"])
        for form_name, row in ordered.iterrows():
            rows.append(
                {
                    "Branch": branch,
                    "Base": top_base,
                    "Form": form_name,
                    "Lag": int(row["lag_days"]),
                    "CAGR": fmt_pct(row["taxed_cagr"]),
                    "dCAGR vs SMA200": fmt_pp(float(row["taxed_cagr"]) - sma_cagr),
                    "MDD": fmt_pct(row["taxed_mdd"]),
                    "dMDD vs SMA200": fmt_pp(float(row["taxed_mdd"]) - sma_mdd),
                    "dScore vs SMA200": fmt_num(float(row["score"]) - sma_score, 3),
                }
            )
    return rows


def hit_rate_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for branch, subset in results.sort_values("score", ascending=False).groupby("branch", sort=True):
        row = subset.iloc[0]
        rows.append(
            {
                "Branch": branch,
                "Base": row["base_name"],
                "Form": row["regime_form"],
                "Hit 3y": fmt_pct(row["hit_3y_vs_underlying"], 1),
                "Hit 5y": fmt_pct(row["hit_5y_vs_underlying"], 1),
                "Hit 10y": fmt_pct(row["hit_10y_vs_underlying"], 1),
                "Hit 15y": fmt_pct(row["hit_15y_vs_underlying"], 1),
                "Hit 20y": fmt_pct(row["hit_20y_vs_underlying"], 1),
            }
        )
    return rows


def operational_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for branch, subset in results.sort_values("score", ascending=False).groupby("branch", sort=True):
        row = subset.iloc[0]
        rows.append(
            {
                "Branch": branch,
                "Base": row["base_name"],
                "Form": row["regime_form"],
                "Turnover/yr": fmt_num(row["turnover_per_year"], 2),
                "Trades": int(row["trade_count"]),
                "Risk-on days": fmt_pct(row["pct_risk_on_days"], 1),
                "Tax paid % init": fmt_pct(row["tax_paid_pct_initial"], 1),
            }
        )
    return rows


def test_window_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for branch, subset in results.groupby("branch", sort=True):
        row = subset.iloc[0]
        rows.append(
            {
                "Branch": branch,
                "Start": row["start"],
                "End": row["end"],
                "Years": fmt_num(row["years"], 1),
                "Underlying CAGR": fmt_pct(row["underlying_taxed_cagr"]),
                "Underlying MDD": fmt_pct(row["underlying_taxed_mdd"]),
            }
        )
    return rows


def _any_form_beats_sma(results: pd.DataFrame) -> dict[str, bool]:
    """Per branch: does any non-control form beat the best SMA200 score on the
    same top base?"""
    verdict: dict[str, bool] = {}
    for branch, branch_rows in results.sort_values("score", ascending=False).groupby("branch", sort=True):
        top_base = branch_rows.iloc[0]["base_name"]
        base_rows = branch_rows[branch_rows["base_name"] == top_base]
        sma_best = base_rows[base_rows["regime_form"] == CONTROL_FORM]["score"].max()
        other_best = base_rows[base_rows["regime_form"] != CONTROL_FORM]["score"].max()
        verdict[str(branch)] = bool(other_best > sma_best)
    return verdict


def write_report(results: pd.DataFrame, plot_rows: list[dict[str, str]], sanity: tuple[float, int]) -> None:
    top = results.iloc[0]
    practical = results[results["practical_pass"]]
    preferred = results[results["drawdown_tier"] == "preferred"]
    qqq_practical = practical[practical["branch"] == "QQQ"]
    beats = _any_form_beats_sma(results)
    beats_both = all(beats.values())
    beats_text = ", ".join(f"{branch}: {'yes' if won else 'no'}" for branch, won in sorted(beats.items()))
    top_is_control = top["regime_form"] == CONTROL_FORM
    sanity_diff, sanity_n = sanity
    sanity_text = (
        f"SMA200 control sanity vs Phase 2: matched `{sanity_n}` base+lag rows, max abs diff in after-tax CAGR/MDD `{sanity_diff:.2e}` (expected ~0, reproduces `lrs/results/phase02_target_leverage_vol.csv`)."
        if sanity_n
        else "SMA200 control sanity vs Phase 2: skipped (Phase 2 CSV not found)."
    )

    sections = [
        "# Phase 3A-2 - Alternative Regime Signals (Replacement)\n\n"
        "Status: research-only regime-signal sweep over the Phase 2 geometry. This report does not authorize deployment, paper trading or a mandate change.\n\n"
        "Method references: each row REPLACES the Gayed SMA200 trend gate with an alternative regime signal `G`, keeping the realized-vol throttle and exposure geometry of Phase 2 (`signal = G & vol_gate`) `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.4-7]`. "
        "This follows directly from the Phase 3A finding that ANDing a trend-hold filter onto `price > SMA200` can only further restrict risk-on; to test a trend mechanism it must replace the SMA gate, not AND onto it `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`. "
        "Lookback is held FIXED at 200 across all forms to isolate signal *form* from *window* (the window question is Phase 3C's). "
        "Regime forms: SMA200 control `[leverage_for_the_long_run, p.13]`; EMA200 `[systematic_trading, p.283]`; SMA hysteresis band as a state machine `[trading_systems_methods, p.383]`; ROC200 momentum `[stocks_on_the_move, p.58, p.60]`; Clenow annualized slope x R^2 `[stocks_on_the_move, p.70-77, p.98]`.\n\n"
        f"{sanity_text}\n\n"
        "## Executive Conclusion\n\n"
        f"Phase 3A-2 evaluated `{len(results):,}` rows: SPY/QQQ x {len(BASE_SPECS) // 2} branch-specific bases x {len(REGIME_FORMS)} regime forms x lags `0..5`. "
        f"Top score row: `{top['branch']}` base `{top['base_name']}` form `{top['regime_form']}` L`{float(top['target_leverage']):.2f}` lag `{int(top['lag_days'])}` with after-tax CAGR {fmt_pct(top['taxed_cagr'])}, MDD {fmt_pct(top['taxed_mdd'])}, Calmar {fmt_num(top['taxed_calmar'])}, terminal {fmt_x(top['terminal_vs_underlying'])} vs underlying. "
        f"The overall top row {'uses the SMA200 control' if top_is_control else 'uses an alternative regime form'}. "
        f"Does any non-control form beat SMA200 on the same top base (by score)? {beats_text}. "
        f"Practical-pass rows (`MDD >= -50%` and after-tax underlying outperformance): `{len(practical):,}`. Preferred drawdown rows (`MDD >= -40%`): `{len(preferred):,}`. QQQ practical-pass rows: `{len(qqq_practical):,}`.\n\n"
        f"Practical read: {'at least one alternative regime form beats the SMA200 control on both branches - a candidate worth carrying into Phase 3C' if beats_both else 'the SMA200 control is not beaten on every branch, so an alternative regime form is not yet justified'} `[trading_systems_methods, p.939]`.\n\n"
        "## Source And Rules\n\n"
        "| Item | Value |\n|---|---|\n"
        "| Data | `data/testfolio/cache/history.parquet` (close-only equity curves) |\n"
        "| Signal | `G(underlying) & realized-vol gate`, G REPLACES the SMA trend gate |\n"
        "| Regime form G | one of {SMA200 control, EMA200, hyst200 band5%/8%, ROC200>0, Clenow200>0} |\n"
        "| Lookback | fixed at 200 for every form (window study deferred to Phase 3C) |\n"
        "| Target leverage | adjacent ETF ladder, no negative cash |\n"
        "| Settlement lag | `n = 0..5` daily bars in `CASHX` before entering the new sleeve |\n"
        "| Tax | annual 15% DARF on realized net gains plus final liquidation |\n\n"
    ]
    sections.append("## Test Windows\n\n" + md_table(test_window_rows(results), ["Branch", "Start", "End", "Years", "Underlying CAGR", "Underlying MDD"]))
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    cols = ["Branch", "Base", "Form", "L", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Spread vs U", "Terminal/U", "Hit 10y", "Pass"]
    sections.append("## Top Ranked Rows\n\n" + md_table(formatted_rows(results, 30), cols))
    sections.append("## Best Row By Branch\n\n" + md_table(best_by_branch_rows(results), ["Branch", "Base", "Form", "L", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Terminal/U"]))
    sections.append("## Best Row By Regime Form\n\n" + md_table(best_by_form_rows(results), ["Branch", "Form", "Family", "Base", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Score"]))
    sections.append(
        "## Form vs SMA200 control (top base per branch, best lag)\n\n"
        + md_table(form_vs_sma_rows(results), ["Branch", "Base", "Form", "Lag", "CAGR", "dCAGR vs SMA200", "MDD", "dMDD vs SMA200", "dScore vs SMA200"])
    )
    sections.append("## Rolling Hit Rates (top row per branch)\n\n" + md_table(hit_rate_rows(results), ["Branch", "Base", "Form", "Hit 3y", "Hit 5y", "Hit 10y", "Hit 15y", "Hit 20y"]))
    sections.append("## Operational / Tax (top row per branch)\n\n" + md_table(operational_rows(results), ["Branch", "Base", "Form", "Turnover/yr", "Trades", "Risk-on days", "Tax paid % init"]))
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Did any non-control form beat SMA200 on both branches? | {'Yes' if beats_both else 'No'} ({beats_text}). |\n"
        f"| Is the overall top row the control or an alternative form? | {'Control (SMA200)' if top_is_control else 'An alternative regime form'}. |\n"
        f"| Did the SMA200 control reproduce Phase 2 (sanity)? | {'Yes' if sanity_n and sanity_diff < 1e-9 else 'Check needed'} (max diff `{sanity_diff:.2e}` over `{sanity_n}` rows). |\n"
        f"| Did any row meet the <=50% MDD practical target and beat underlying? | {'Yes' if not practical.empty else 'No'}. |\n"
        f"| Did any row meet preferred <=40% MDD? | {'Yes' if not preferred.empty else 'No'}. |\n"
        "| Is this deployment-ready? | No. This is a diagnostic regime-form phase only. No deploy, no paper-trade label, no mandate change. |\n\n"
        f"Next step: {'carry the form(s) that beat SMA200 into Phase 3C alongside SMA itself' if beats_both else 'Phase 3C studies SMA + EMA (and hysteresis only if promoted here); the SMA200 level remains the control'} `[advances_fin_ml, p.208-211]`.\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    contexts = {name: build_context(branch) for name, branch in BRANCHES.items()}
    rows = []
    for base in BASE_SPECS:
        context = contexts[str(base["branch"])]
        for form_spec in REGIME_FORMS:
            for lag_days in range(6):
                rows.append(simulate_candidate(context, base, form_spec, lag_days))
    results = pd.DataFrame(rows).sort_values(
        ["practical_pass", "score", "terminal_vs_underlying", "taxed_calmar"],
        ascending=[False, False, False, False],
    )
    results.to_csv(CSV, index=False)
    sanity = sma200_sanity_max_diff(results)
    sanity_diff, sanity_n = sanity
    if sanity_n and not (sanity_diff < 1e-9):
        raise AssertionError(
            f"SMA200 control does not reproduce Phase 2: max abs diff {sanity_diff:.3e} over {sanity_n} rows"
        )
    plot_rows = make_plots(results, contexts)
    write_report(results, plot_rows, sanity)
    print(f"Phase 3A-2: {len(results)} rows; SMA200 sanity max diff {sanity_diff:.2e} over {sanity_n} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
