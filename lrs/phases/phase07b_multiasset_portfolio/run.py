"""Phase 7B - equal-weight portfolio of single-asset SMA200 rotations (DIAGNOSTIC).

Research-only. Tests whether cross-instrument diversification of the Gayed
rotation itself lifts walk-forward consistency: an EW portfolio of N
single-asset SMA200 legs, uniform grammar (one shared L, ZROZ risk-off, shared
vol-gate choice), no per-leg recipe fitting `[systematic_trading, p.42]`,
`[systematic_trading, p.170-171]`, `[risk_parity, p.80-81]`,
`[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.208-211]`. Legs
without a cached leveraged proxy use in-memory synthetic 2x series
`[leverage_for_the_long_run, p.16, fn.22-23]`. Pre-registered grid: 72 rows
(3 compositions x 2 leverages x 2 vol gates x 6 lags); +72 to the n_trials
ledger (4077 -> 4149). No deployment, no paper-trade label, no mandate change.
"""
from __future__ import annotations

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
    load_price_frame,
    md_table,
    metrics_from_returns,
    simulate_weight_frame,
    synth_leveraged_returns,
)
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase06b_vol_target_continuous.run import wf_beats  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase07b_multiasset_portfolio.csv"

SMA_WINDOW = 200
SYNTH_FEE_ANNUAL = 0.0095
RISK_OFF_WEIGHTS = {"ZROZSIM": 1.0}
LEGS: dict[str, dict[str, object]] = {
    "SPY": {"underlying": "SPYSIM", "lev2": "SSOSIM", "synth": False},
    "QQQ": {"underlying": "QQQSIM", "lev2": "QLDSIM", "synth": False},
    "IWM": {"underlying": "IWMSIM", "lev2": "IWM2XSYN", "synth": True},
    "XLK": {"underlying": "XLKSIM", "lev2": "XLK2XSYN", "synth": True},
    "GLD": {"underlying": "GLDSIM", "lev2": "GLD2XSYN", "synth": True},
}
COMPOSITIONS: dict[str, list[str]] = {
    "EW5": ["SPY", "QQQ", "IWM", "XLK", "GLD"],
    "EW4_no_qqq": ["SPY", "IWM", "XLK", "GLD"],
    "EW3_spy_qqq_gld": ["SPY", "QQQ", "GLD"],
}
LEVERAGES = [1.75, 2.00]
VOL_GATES: list[dict[str, object]] = [
    {"name": "none", "window": 0, "threshold": None},
    {"name": "RV63 <= 40%", "window": 63, "threshold": 0.40},
]
LAGS = list(range(6))
N_TRIALS_ADDED = len(COMPOSITIONS) * len(LEVERAGES) * len(VOL_GATES) * len(LAGS)  # 72
N_TRIALS_LEDGER_BEFORE = 4077
MDD_FLOOR = -0.50


def composition_universe(comp_legs: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Prices and returns (with synthetic 2x columns) on the composition window."""
    cache_assets = {"ZROZSIM", "CASHX"}
    for leg in comp_legs:
        spec = LEGS[leg]
        cache_assets.add(str(spec["underlying"]))
        if not spec["synth"]:
            cache_assets.add(str(spec["lev2"]))
    prices = load_price_frame(sorted(cache_assets))
    returns = prices.pct_change().dropna()
    prices = prices.reindex(returns.index)
    for leg in comp_legs:
        spec = LEGS[leg]
        if spec["synth"]:
            returns[str(spec["lev2"])] = synth_leveraged_returns(
                returns[str(spec["underlying"])], 2.0, returns["CASHX"], SYNTH_FEE_ANNUAL
            )
    return prices, returns


def leg_vol_gate(returns: pd.DataFrame, underlying: str, vol_spec: dict[str, object]) -> pd.Series:
    if vol_spec["threshold"] is None:
        return pd.Series(True, index=returns.index)
    window = int(vol_spec["window"])
    threshold = float(vol_spec["threshold"])
    rv = returns[underlying].rolling(window).std(ddof=0).shift(1) * np.sqrt(252.0)
    return (rv <= threshold).reindex(returns.index).fillna(False)


def leg_risk_on_weights(leg: str, target_leverage: float) -> dict[str, float]:
    """Uniform ladder at L <= 2 using underlying + (real or synthetic) 2x."""
    if not 1.0 <= target_leverage <= 2.0:
        raise ValueError(f"shared leverage out of the pre-registered range: {target_leverage}")
    spec = LEGS[leg]
    return clean_weights(
        {str(spec["underlying"]): 2.0 - target_leverage, str(spec["lev2"]): target_leverage - 1.0}
    )


def leg_weight_frame(
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    leg: str,
    target_leverage: float,
    vol_spec: dict[str, object],
    lag: int,
) -> pd.DataFrame:
    """Single-leg LRS weight frame (identical grammar for every leg)."""
    underlying = str(LEGS[leg]["underlying"])
    signal = (
        build_sma_signal(prices[underlying], SMA_WINDOW).reindex(returns.index).fillna(False)
        & leg_vol_gate(returns, underlying, vol_spec)
    )
    risk_on = leg_risk_on_weights(leg, target_leverage)
    assets = sorted(set(risk_on) | set(RISK_OFF_WEIGHTS) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=returns.index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on.get(asset, 0.0), RISK_OFF_WEIGHTS.get(asset, 0.0))
    weights, _ = build_weekly_lagged_weights(desired, lag_days=lag, risk_on_weights=risk_on)
    return weights


def portfolio_frame(leg_frames: list[pd.DataFrame]) -> pd.DataFrame:
    columns = sorted(set().union(*[set(f.columns) for f in leg_frames]))
    total = sum(f.reindex(columns=columns, fill_value=0.0) for f in leg_frames)
    return total / float(len(leg_frames))


def buy_and_hold_taxed(returns: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """No-rebalance B&H, after-tax = final-liquidation DARF only (6A convention)."""
    frame = constant_weight_frame(returns.index, weights)
    taxed, _ = simulate_weight_frame(returns, frame, taxable=True)
    return taxed


def fraction_of_legs_on(
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    comp_legs: list[str],
    vol_spec: dict[str, object],
) -> pd.Series:
    members = []
    for leg in comp_legs:
        underlying = str(LEGS[leg]["underlying"])
        sig = (
            build_sma_signal(prices[underlying], SMA_WINDOW).reindex(returns.index).fillna(False)
            & leg_vol_gate(returns, underlying, vol_spec)
        )
        members.append(sig.astype(float))
    return sum(members) / float(len(members))


def evaluate_trial(
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    comp_name: str,
    comp_legs: list[str],
    target_leverage: float,
    vol_spec: dict[str, object],
    lag: int,
    bench_taxed: pd.Series,
    bench_metrics,
) -> tuple[dict[str, object], pd.Series]:
    frames = [
        leg_weight_frame(prices, returns, leg, target_leverage, vol_spec, lag) for leg in comp_legs
    ]
    weights = portfolio_frame(frames)
    taxed, tax_summary = simulate_weight_frame(returns, weights, taxable=True)
    metrics = metrics_from_returns(taxed)
    beats, n_windows = wf_beats(taxed, bench_taxed)
    row: dict[str, object] = {
        "config_type": "portfolio",
        "composition": comp_name,
        "n_legs": len(comp_legs),
        "target_leverage": target_leverage,
        "vol_filter": vol_spec["name"],
        "lag_days": lag,
        "window_start": str(returns.index[0].date()),
        "window_end": str(returns.index[-1].date()),
        "taxed_cagr": metrics.cagr,
        "taxed_mdd": metrics.mdd,
        "taxed_sharpe": metrics.sharpe,
        "taxed_sortino": metrics.sortino,
        "taxed_calmar": metrics.calmar,
        "taxed_terminal": metrics.terminal,
        "wf_beats": beats,
        "wf_windows": n_windows,
        "wf_ratio": beats / n_windows if n_windows else float("nan"),
        "bench_cagr": bench_metrics.cagr,
        "bench_mdd": bench_metrics.mdd,
        "turnover_per_year": tax_summary["turnover_per_year"],
        "total_tax_paid_pct_initial": tax_summary["total_tax_paid_pct_initial"],
    }
    return row, taxed


def standalone_leg_controls(
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    comp_legs: list[str],
    target_leverage: float,
    vol_spec: dict[str, object],
    lag: int,
) -> list[dict[str, object]]:
    """Each leg as a standalone rotation, WF vs its own underlying B&H (non-trial)."""
    out = []
    for leg in comp_legs:
        underlying = str(LEGS[leg]["underlying"])
        frame = leg_weight_frame(prices, returns, leg, target_leverage, vol_spec, lag)
        taxed, _ = simulate_weight_frame(returns, frame, taxable=True)
        u_taxed = buy_and_hold_taxed(returns, {underlying: 1.0})
        beats, n_windows = wf_beats(taxed, u_taxed)
        metrics = metrics_from_returns(taxed)
        out.append(
            {
                "leg": leg,
                "wf_beats": beats,
                "wf_windows": n_windows,
                "wf_ratio": beats / n_windows if n_windows else float("nan"),
                "taxed_cagr": metrics.cagr,
                "taxed_mdd": metrics.mdd,
            }
        )
    return out


def sanity_degenerate_spy(prices: pd.DataFrame, returns: pd.DataFrame) -> float:
    """{SPY}-only composition vs phase04.simulate_returns on the SAME window.

    The reference context is rebuilt on this phase's universe window (the DARF
    engine is path-dependent, so a different start date would differ
    legitimately); only the mechanical pipeline is under test here.
    """
    frame = leg_weight_frame(prices, returns, "SPY", 2.00, VOL_GATES[1], 0)
    taxed, _ = simulate_weight_frame(returns, frame, taxable=True)

    branch = phase04.BRANCHES["SPY"]
    context = phase04.BranchContext(
        branch=branch,
        returns=returns,
        sma_signal=build_sma_signal(prices[branch["underlying"]], SMA_WINDOW)
        .reindex(returns.index)
        .fillna(False),
        underlying_taxed=pd.Series(dtype=float),
    )
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == "RV63 <= 40%")
    reference = phase04.simulate_returns(context, 2.00, dict(RISK_OFF_WEIGHTS), vol_spec, 0)
    aligned = pd.concat({"a": taxed, "b": reference}, axis=1, sort=False).dropna()
    return float((aligned["a"] - aligned["b"]).abs().max())


def screen_composition(
    frame: pd.DataFrame,
    comp_name: str,
    controls: list[dict[str, object]],
) -> dict[str, object]:
    trials = frame[(frame["config_type"] == "portfolio") & (frame["composition"] == comp_name)]
    best = trials.sort_values(["wf_ratio", "taxed_calmar"], ascending=False).iloc[0]
    max_leg = max(controls, key=lambda c: c["wf_ratio"])
    crit_wf = bool(best["wf_ratio"] > max_leg["wf_ratio"])
    crit_cagr = bool(best["taxed_cagr"] > best["bench_cagr"])
    crit_mdd = bool(best["taxed_mdd"] >= MDD_FLOOR)
    return {
        "composition": comp_name,
        "best": best,
        "controls": controls,
        "max_leg": max_leg,
        "crit_wf": crit_wf,
        "crit_cagr": crit_cagr,
        "crit_mdd": crit_mdd,
        "success": bool(crit_wf and crit_cagr and crit_mdd),
    }


# --------------------------------------------------------------------------- plots


def plot_equity_dd(best_returns: dict[str, pd.Series], bench_returns: dict[str, pd.Series]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    comps = list(best_returns)
    fig, axes = plt.subplots(2, len(comps), figsize=(6.0 * len(comps), 8.5), squeeze=False)
    for col, comp in enumerate(comps):
        pair = pd.concat(
            {"portfolio best": best_returns[comp], "EW underlying B&H": bench_returns[comp]},
            axis=1,
        ).dropna()
        eq = pair.apply(equity_curve)
        eq.plot(ax=axes[0][col], logy=True, linewidth=1.0)
        axes[0][col].set_title(f"{comp}: after-tax equity")
        axes[0][col].grid(True, alpha=0.3)
        dd = eq / eq.cummax() - 1.0
        (dd * 100.0).plot(ax=axes[1][col], linewidth=0.9)
        axes[1][col].set_title(f"{comp}: drawdown (%)")
        axes[1][col].grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07b_equity_dd.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_wf_ratio(screens: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, len(screens), figsize=(5.5 * len(screens), 4.5), squeeze=False)
    for ax, screen in zip(axes[0], screens):
        best = screen["best"]
        labels = ["portfolio"] + [str(c["leg"]) for c in screen["controls"]]
        values = [float(best["wf_ratio"])] + [float(c["wf_ratio"]) for c in screen["controls"]]
        colors = ["tab:blue"] + ["#888888"] * len(screen["controls"])
        ax.bar(labels, values, color=colors)
        ax.axhline(0.75, color="red", linestyle="--", linewidth=0.9, label="G3 75% level")
        ax.set_ylim(0, 1.0)
        ax.set_title(f"{screen['composition']}: WF beat ratio")
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase07b_wf_ratio.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6))
    trials = frame[frame["config_type"] == "portfolio"]
    for comp, sub in trials.groupby("composition"):
        ax.scatter(sub["taxed_mdd"] * 100.0, sub["taxed_cagr"] * 100.0, s=30, alpha=0.7, label=str(comp))
    ax.axvline(MDD_FLOOR * 100.0, color="red", linestyle="--", linewidth=0.9, label="MDD -50% floor")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.set_title("Phase 7B frontier: EW rotation portfolios")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase07b_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_fraction_series(fractions: dict[str, pd.Series]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(fractions), 1, figsize=(13, 2.8 * len(fractions)), squeeze=False)
    for ax, (label, frac) in zip(axes.ravel(), fractions.items()):
        ax.plot(frac.index, frac.to_numpy(dtype=float), linewidth=0.6, color="tab:blue")
        ax.set_title(f"{label}: fraction of legs risk-on")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07b_legs_on_fraction.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def top_rows_table(frame: pd.DataFrame, comp_name: str, limit: int = 6) -> str:
    sub = frame[(frame["config_type"] == "portfolio") & (frame["composition"] == comp_name)]
    sub = sub.sort_values(["wf_ratio", "taxed_calmar"], ascending=False).head(limit)
    rows = [
        {
            "L": fmt_num(r["target_leverage"], 2),
            "Vol": r["vol_filter"],
            "Lag": int(r["lag_days"]),
            "WF": f"{int(r['wf_beats'])}/{int(r['wf_windows'])} ({fmt_pct(r['wf_ratio'], 1)})",
            "CAGR": fmt_pct(r["taxed_cagr"]),
            "Bench CAGR": fmt_pct(r["bench_cagr"]),
            "MDD": fmt_pct(r["taxed_mdd"]),
            "Sharpe": fmt_num(r["taxed_sharpe"]),
            "Calmar": fmt_num(r["taxed_calmar"]),
            "Turnover/y": fmt_num(r["turnover_per_year"], 2),
        }
        for _, r in sub.iterrows()
    ]
    return md_table(rows, ["L", "Vol", "Lag", "WF", "CAGR", "Bench CAGR", "MDD", "Sharpe", "Calmar", "Turnover/y"])


def screen_section(screen: dict[str, object]) -> str:
    best = screen["best"]
    control_rows = [
        {
            "Leg": c["leg"],
            "WF": f"{int(c['wf_beats'])}/{int(c['wf_windows'])} ({fmt_pct(c['wf_ratio'], 1)})",
            "CAGR": fmt_pct(c["taxed_cagr"]),
            "MDD": fmt_pct(c["taxed_mdd"]),
        }
        for c in screen["controls"]
    ]
    return (
        f"### {screen['composition']} — best row "
        f"`L {best['target_leverage']:.2f} / {best['vol_filter']} / lag {int(best['lag_days'])}` "
        f"(window {best['window_start']}..{best['window_end']})\n\n"
        f"- Portfolio WF {int(best['wf_beats'])}/{int(best['wf_windows'])} ({fmt_pct(best['wf_ratio'], 1)}) "
        f"vs max standalone leg {fmt_pct(screen['max_leg']['wf_ratio'], 1)} ({screen['max_leg']['leg']}): "
        f"{'P' if screen['crit_wf'] else 'F'}\n"
        f"- CAGR {fmt_pct(best['taxed_cagr'])} vs EW B&H bench {fmt_pct(best['bench_cagr'])}: "
        f"{'P' if screen['crit_cagr'] else 'F'}\n"
        f"- MDD {fmt_pct(best['taxed_mdd'])} >= -50%: {'P' if screen['crit_mdd'] else 'F'}\n"
        f"- **Screen: {'SUCCESS' if screen['success'] else 'FAIL'}**\n\n"
        "Standalone-leg controls (same L/vol/lag/window, WF vs own underlying B&H):\n\n"
        + md_table(control_rows, ["Leg", "WF", "CAGR", "MDD"])
    )


def write_report(
    frame: pd.DataFrame,
    screens: list[dict[str, object]],
    plot_rows: list[dict[str, str]],
    sanity_diff: float,
) -> None:
    n_success = sum(1 for s in screens if s["success"])
    sections = [
        "# Phase 7B - Multi-Asset Portfolio of SMA200 Rotations (DIAGNOSTIC)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "Equal-weight portfolio of single-asset Gayed SMA200 rotations with a UNIFORM grammar (shared L, ZROZ risk-off, shared vol-gate choice; no per-leg recipe fitting) `[systematic_trading, p.42]`, `[systematic_trading, p.170-171]`, `[risk_parity, p.80-81]`, `[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.208-211]`. IWM/XLK/GLD legs use in-memory synthetic 2x (`r = 2*r_u - r_cash - 0.95%/252`) `[leverage_for_the_long_run, p.16, fn.22-23]` - a DISCLOSED limitation: synthetic legs understate real-ETF tracking frictions.\n\n"
        f"Pre-registered grid: 3 compositions x 2 leverages x 2 vol gates x 6 lags = {N_TRIALS_ADDED} rows. **n_trials ledger: {N_TRIALS_LEDGER_BEFORE} + {N_TRIALS_ADDED} = {N_TRIALS_LEDGER_BEFORE + N_TRIALS_ADDED}.** EW B&H benchmarks and standalone-leg controls are comparisons, not trials.\n\n"
        f"**Built-in sanity ({{SPY}}-only composition vs `phase04.simulate_returns`):** max abs diff {sanity_diff:.3g}.\n\n"
        "## Executive Conclusion\n\n"
        f"Pre-registered screen (best trial row per composition by WF ratio, tie-break Calmar): **{n_success}/{len(screens)} compositions SUCCESS**. Criteria: WF ratio (vs EW-underlying B&H) strictly above the max standalone-leg WF ratio AND CAGR > EW B&H bench AND MDD >= -50%. A SUCCESS feeds the Phase 7F composition slot only - NOT a gate pass, NOT a promotion `[advances_fin_ml, p.208-211]`.\n\n",
    ]
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    sections.append("## Screen Results\n")
    for screen in screens:
        sections.append(screen_section(screen))
    for comp_name in COMPOSITIONS:
        sections.append(f"## Top {comp_name} Rows (by WF ratio, then Calmar)\n\n" + top_rows_table(frame, comp_name))
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        + "".join(
            f"| {s['composition']}: EW portfolio beats every standalone leg on WF ratio? | {'Yes' if s['crit_wf'] else 'No'} ({fmt_pct(float(s['best']['wf_ratio']), 1)} vs {fmt_pct(float(s['max_leg']['wf_ratio']), 1)}). |\n"
            for s in screens
        )
        + f"| Screen successes? | {n_success}/{len(screens)}. |\n"
        "| Did we promote anything? | No - diagnostic only. |\n"
        "| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    best_returns: dict[str, pd.Series] = {}
    bench_returns: dict[str, pd.Series] = {}
    fractions: dict[str, pd.Series] = {}
    screens: list[dict[str, object]] = []
    sanity_diff = float("nan")

    for comp_name, comp_legs in COMPOSITIONS.items():
        prices, returns = composition_universe(comp_legs)
        if comp_name == "EW5":
            sanity_diff = sanity_degenerate_spy(prices, returns)
            print(f"  sanity degenerate SPY: max abs diff {sanity_diff:.3g}")
        bench_weights = {str(LEGS[leg]["underlying"]): 1.0 / len(comp_legs) for leg in comp_legs}
        bench_taxed = buy_and_hold_taxed(returns, bench_weights)
        bench_metrics = metrics_from_returns(bench_taxed)
        bench_returns[comp_name] = bench_taxed

        best_key: tuple[float, float] | None = None
        best_spec: tuple[float, dict[str, object], int] | None = None
        for target_leverage in LEVERAGES:
            for vol_spec in VOL_GATES:
                for lag in LAGS:
                    row, taxed = evaluate_trial(
                        prices, returns, comp_name, comp_legs, target_leverage, vol_spec, lag,
                        bench_taxed, bench_metrics,
                    )
                    rows.append(row)
                    key = (float(row["wf_ratio"]), float(row["taxed_calmar"]))
                    if best_key is None or key > best_key:
                        best_key = key
                        best_returns[comp_name] = taxed
                        best_spec = (target_leverage, vol_spec, lag)
        assert best_spec is not None
        controls = standalone_leg_controls(
            prices, returns, comp_legs, best_spec[0], best_spec[1], best_spec[2]
        )
        frame_so_far = pd.DataFrame(rows)
        screens.append(screen_composition(frame_so_far, comp_name, controls))
        fractions[f"{comp_name} ({best_spec[1]['name']})"] = fraction_of_legs_on(
            prices, returns, comp_legs, best_spec[1]
        )
        print(f"  {comp_name}: grid done ({returns.index[0].date()}..{returns.index[-1].date()})")

    frame = pd.DataFrame(rows)
    frame.to_csv(CSV, index=False)
    plot_rows = []
    eq = plot_equity_dd(best_returns, bench_returns)
    plot_rows.append({"Plot": "Equity/drawdown vs EW B&H benchmark", "File": f"[plots/{eq.name}](plots/{eq.name})"})
    wf = plot_wf_ratio(screens)
    plot_rows.append({"Plot": "WF ratio: portfolio vs standalone legs", "File": f"[plots/{wf.name}](plots/{wf.name})"})
    frontier = plot_frontier(frame)
    plot_rows.append({"Plot": "CAGR x MDD frontier", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    frac_plot = plot_fraction_series(fractions)
    plot_rows.append({"Plot": "Fraction of legs risk-on (best rows)", "File": f"[plots/{frac_plot.name}](plots/{frac_plot.name})"})
    write_report(frame, screens, plot_rows, sanity_diff)

    for screen in screens:
        best = screen["best"]
        print(
            f"Phase 7B {screen['composition']}: best L{best['target_leverage']:.2f} {best['vol_filter']} "
            f"lag {int(best['lag_days'])} WF {int(best['wf_beats'])}/{int(best['wf_windows'])} "
            f"({float(best['wf_ratio']):.1%}) vs max leg {float(screen['max_leg']['wf_ratio']):.1%} "
            f"CAGR {best['taxed_cagr']:.2%} (bench {best['bench_cagr']:.2%}) MDD {best['taxed_mdd']:.2%} "
            f"screen={'SUCCESS' if screen['success'] else 'FAIL'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
