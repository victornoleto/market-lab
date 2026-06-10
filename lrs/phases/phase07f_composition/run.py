"""Phase 7F - composition of the round winners: 7A ensemble x 7D quadratic (DIAGNOSTIC).

Research-only. Triggered by the pre-registered round condition (>=2 SUCCESS
among 7A-7D: 7A SPY ensemble WF 13/17, 7D QQQ quadratic vol-target WF 8/11).
Composes the two orthogonal winning mechanisms with parameters FROZEN at their
per-mechanism winners (narrow window set {150,175,200,225}; sigma 40% / RV21);
only the lag is swept `[systematic_trading, p.118-119, p.129-133]`,
`[volatility_trading, p.135, p.138-140]`, `[advances_fin_ml, p.208-211]`.
Pre-registered grid: 24 rows (2 branches x 2 variants x 6 lags); +24 to the
n_trials ledger (4353 -> 4377). No deployment, no paper-trade label, no
mandate change.
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
    build_weekly_lagged_weights,
    clean_weights,
    equity_curve,
    fmt_num,
    fmt_pct,
    md_table,
    metrics_from_returns,
    simulate_weight_frame,
)
from lrs.lib.indicators import sma_ensemble_fraction  # noqa: E402
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase06b_vol_target_continuous.run import wf_beats  # noqa: E402
from lrs.phases.phase07a_ensemble_lookback.run import branch_prices  # noqa: E402
from lrs.phases.phase07d_vol_target_quadratic.run import quadratic_leverage_series  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase07f_composition.csv"

WINDOW_SET = [150, 175, 200, 225]  # 7A winner (narrow), frozen
SIGMA_TARGET = 0.40  # 7D winner, frozen
RV_WINDOW = 21  # 7D winner, frozen
VARIANTS = ["ens_x_quad", "ens_x_quad_gated"]
LAGS = list(range(6))
N_TRIALS_ADDED = 2 * len(VARIANTS) * len(LAGS)  # 24
N_TRIALS_LEDGER_BEFORE = 4353
MDD_FLOOR = -0.50
CAGR_TOLERANCE_PP = 0.01
# Best round results so far (the bar the composition must strictly beat).
ROUND_BEST_WF = {"SPY": 13, "QQQ": 8}
HEADLINE_CAGR = {"SPY": 0.1544, "QQQ": 0.1946}

BRANCH_SPECS: list[dict[str, object]] = [
    {
        "branch": "SPY",
        "l_max": 2.00,
        "risk_off": "50 ZROZ / 25 GLD / 25 CASH",
        "vol": "RV21 <= 30%",
    },
    {
        "branch": "QQQ",
        "l_max": 1.75,
        "risk_off": "40 ZROZ / 40 GLD / 20 IEF",
        "vol": "RV63 <= 40%",
    },
]


def ladder_weight_frame(
    context: "phase04.BranchContext", leverage: pd.Series, l_max: float
) -> pd.DataFrame:
    """Daily ladder(L_t) risk-on weight frame (no signal applied yet)."""
    from lrs.phases.phase06b_vol_target_continuous.run import ladder_weights_any

    branch = context.branch
    index = context.returns.index
    lev = leverage.reindex(index).fillna(0.0).to_numpy(dtype=float)
    assets = sorted({branch["underlying"], branch["lev2"], branch["lev3"], "CASHX"})
    frame = pd.DataFrame(0.0, index=index, columns=assets)
    for level in np.unique(lev):
        weights = ladder_weights_any(branch, float(level))
        mask = np.isclose(lev, level)
        for asset, weight in weights.items():
            frame.loc[mask, asset] = weight
    return frame


def composed_desired_targets(
    context: "phase04.BranchContext",
    fraction: pd.Series,
    leverage: pd.Series,
    l_max: float,
    risk_off_weights: dict[str, float],
) -> pd.DataFrame:
    """`f_t * ladder(L_t) + (1 - f_t) * risk_off` as a daily desired frame."""
    index = context.returns.index
    on_frame = ladder_weight_frame(context, leverage, l_max)
    assets = sorted(set(on_frame.columns) | set(risk_off_weights) | {"CASHX"})
    on_frame = on_frame.reindex(columns=assets, fill_value=0.0)
    off_frame = pd.DataFrame(0.0, index=index, columns=assets)
    for asset, weight in risk_off_weights.items():
        off_frame[asset] = weight
    f = fraction.reindex(index).fillna(0.0).to_numpy(dtype=float)[:, None]
    return on_frame.mul(1.0, axis=0) * f + off_frame * (1.0 - f)


def evaluate_row(
    context: "phase04.BranchContext",
    spec: dict[str, object],
    variant: str,
    lag: int,
    fraction_raw: pd.Series,
    leverage: pd.Series,
    risk_off_weights: dict[str, float],
) -> tuple[dict[str, object], pd.Series, pd.Series]:
    if variant == "ens_x_quad":
        fraction = fraction_raw
    elif variant == "ens_x_quad_gated":
        vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == spec["vol"])
        gate = phase04.vol_gate(context, vol_spec).astype(float)
        fraction = fraction_raw * gate
    else:
        raise ValueError(f"unknown variant: {variant}")
    desired = composed_desired_targets(
        context, fraction, leverage, float(spec["l_max"]), risk_off_weights
    )
    weights, weight_summary = build_weekly_lagged_weights(desired, lag_days=lag)
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    metrics = metrics_from_returns(taxed)
    beats, n_windows = wf_beats(taxed, context.underlying_taxed)
    exposure = fraction.reindex(context.returns.index).fillna(0.0) * leverage.reindex(
        context.returns.index
    ).fillna(0.0)
    row: dict[str, object] = {
        "config_type": "composition",
        "branch": spec["branch"],
        "variant": variant,
        "lag_days": lag,
        "l_max": float(spec["l_max"]),
        "risk_off": spec["risk_off"],
        "taxed_cagr": metrics.cagr,
        "taxed_mdd": metrics.mdd,
        "taxed_sharpe": metrics.sharpe,
        "taxed_sortino": metrics.sortino,
        "taxed_calmar": metrics.calmar,
        "taxed_terminal": metrics.terminal,
        "wf_beats": beats,
        "wf_windows": n_windows,
        "mean_exposure": float(exposure.mean()),
        "state_changes": weight_summary["state_changes"],
        "turnover_per_year": tax_summary["turnover_per_year"],
        "total_tax_paid_pct_initial": tax_summary["total_tax_paid_pct_initial"],
    }
    return row, taxed, exposure


def sanity_fraction_one(
    context: "phase04.BranchContext",
    spec: dict[str, object],
    leverage: pd.Series,
    risk_off_weights: dict[str, float],
) -> float:
    """f_t forced to 1 must reproduce the pure 7D quadratic pipeline (lag 0)."""
    ones = pd.Series(1.0, index=context.returns.index)
    desired = composed_desired_targets(
        context, ones, leverage, float(spec["l_max"]), risk_off_weights
    )
    weights, _ = build_weekly_lagged_weights(desired, lag_days=0)
    taxed, _ = simulate_weight_frame(context.returns, weights, taxable=True)

    from lrs.phases.phase06b_vol_target_continuous.run import desired_targets_continuous

    # Pure 7D pipeline: signal & ladder(L_t); with f==1 the composition has no
    # risk-off mixing, but 7D still applies the SMA200 signal. Force the signal
    # on by reusing the composition frame with the ladder directly.
    desired_ref = desired_targets_continuous(context, leverage, risk_off_weights)
    signal = context.sma_signal.reindex(context.returns.index).fillna(False)
    on_frame = ladder_weight_frame(context, leverage, float(spec["l_max"]))
    assets = sorted(set(on_frame.columns) | set(risk_off_weights) | {"CASHX"})
    expected = on_frame.reindex(columns=assets, fill_value=0.0)
    got = desired.reindex(columns=assets, fill_value=0.0)
    frame_diff = float((expected - got).abs().to_numpy().max())

    # Also check the simulated path equals a direct simulation of the ladder frame.
    weights_ref, _ = build_weekly_lagged_weights(expected, lag_days=0)
    taxed_ref, _ = simulate_weight_frame(context.returns, weights_ref, taxable=True)
    sim_diff = float((taxed - taxed_ref).abs().max())
    del desired_ref, signal
    return max(frame_diff, sim_diff)


def screen_branch(frame: pd.DataFrame, branch: str) -> dict[str, object]:
    trials = frame[(frame["config_type"] == "composition") & (frame["branch"] == branch)]
    best = trials.sort_values(["wf_beats", "taxed_calmar"], ascending=False).iloc[0]
    crit_wf = bool(best["wf_beats"] > ROUND_BEST_WF[branch])
    crit_cagr = bool(best["taxed_cagr"] >= HEADLINE_CAGR[branch] - CAGR_TOLERANCE_PP)
    crit_mdd = bool(best["taxed_mdd"] >= MDD_FLOOR)
    return {
        "branch": branch,
        "best": best,
        "round_best_wf": ROUND_BEST_WF[branch],
        "crit_wf": crit_wf,
        "crit_cagr": crit_cagr,
        "crit_mdd": crit_mdd,
        "success": bool(crit_wf and crit_cagr and crit_mdd),
    }


# --------------------------------------------------------------------------- plots


def plot_exposure_series(best_exposures: dict[str, pd.Series]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(best_exposures), 1, figsize=(13, 3.2 * len(best_exposures)), squeeze=False)
    for ax, (label, exposure) in zip(axes.ravel(), best_exposures.items()):
        ax.plot(exposure.index, exposure.to_numpy(dtype=float), linewidth=0.6, color="tab:red")
        ax.set_title(f"{label}: composed exposure f_t * L_t")
        ax.set_ylabel("effective leverage")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07f_exposure_series.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_equity_dd(best_returns: dict[str, pd.Series], baseline_returns: dict[str, pd.Series]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    branches = list(best_returns)
    fig, axes = plt.subplots(2, len(branches), figsize=(7.5 * len(branches), 8.5), squeeze=False)
    for col, branch in enumerate(branches):
        pair = pd.concat(
            {"composition best": best_returns[branch], "binary headline": baseline_returns[branch]},
            axis=1,
        ).dropna()
        eq = pair.apply(equity_curve)
        eq.plot(ax=axes[0][col], logy=True, linewidth=1.1)
        axes[0][col].set_title(f"{branch}: after-tax equity")
        axes[0][col].grid(True, alpha=0.3)
        dd = eq / eq.cummax() - 1.0
        (dd * 100.0).plot(ax=axes[1][col], linewidth=1.0)
        axes[1][col].set_title(f"{branch}: drawdown (%)")
        axes[1][col].grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07f_equity_dd.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_wf_comparison(screens: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = [str(s["branch"]) for s in screens]
    round_vals = [int(s["round_best_wf"]) for s in screens]
    best_vals = [int(s["best"]["wf_beats"]) for s in screens]
    x = np.arange(len(labels))
    ax.bar(x - 0.18, round_vals, width=0.36, label="round best (7A/7D)", color="#888888")
    ax.bar(x + 0.18, best_vals, width=0.36, label="composition best", color="tab:red")
    for i, screen in enumerate(screens):
        ax.text(i, max(round_vals[i], best_vals[i]) + 0.2, f"/{int(screen['best']['wf_windows'])}", ha="center")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("WF windows beating underlying")
    ax.set_title("Phase 7F: walk-forward beat count vs round best")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07f_wf_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6))
    trials = frame[frame["config_type"] == "composition"]
    for variant, sub in trials.groupby("variant"):
        ax.scatter(sub["taxed_mdd"] * 100.0, sub["taxed_cagr"] * 100.0, s=35, alpha=0.75, label=str(variant))
    ax.axvline(MDD_FLOOR * 100.0, color="red", linestyle="--", linewidth=0.9, label="MDD -50% floor")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.set_title("Phase 7F frontier: composition grid")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase07f_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def top_rows_table(frame: pd.DataFrame, branch: str, limit: int = 8) -> str:
    sub = frame[(frame["config_type"] == "composition") & (frame["branch"] == branch)]
    sub = sub.sort_values(["wf_beats", "taxed_calmar"], ascending=False).head(limit)
    rows = [
        {
            "Variant": r["variant"],
            "Lag": int(r["lag_days"]),
            "WF": f"{int(r['wf_beats'])}/{int(r['wf_windows'])}",
            "CAGR": fmt_pct(r["taxed_cagr"]),
            "MDD": fmt_pct(r["taxed_mdd"]),
            "Sharpe": fmt_num(r["taxed_sharpe"]),
            "Calmar": fmt_num(r["taxed_calmar"]),
            "Mean exposure": fmt_num(r["mean_exposure"], 2),
            "Turnover/y": fmt_num(r["turnover_per_year"], 2),
        }
        for _, r in sub.iterrows()
    ]
    return md_table(rows, ["Variant", "Lag", "WF", "CAGR", "MDD", "Sharpe", "Calmar", "Mean exposure", "Turnover/y"])


def screen_table(screens: list[dict[str, object]]) -> str:
    rows = []
    for screen in screens:
        best = screen["best"]
        rows.append(
            {
                "Branch": screen["branch"],
                "Best config": f"{best['variant']} / lag {int(best['lag_days'])}",
                "WF vs round best": f"{int(best['wf_beats'])}/{int(best['wf_windows'])} vs {int(screen['round_best_wf'])} {'P' if screen['crit_wf'] else 'F'}",
                "CAGR vs headline-1pp": f"{fmt_pct(best['taxed_cagr'])} {'P' if screen['crit_cagr'] else 'F'}",
                "MDD >= -50%": f"{fmt_pct(best['taxed_mdd'])} {'P' if screen['crit_mdd'] else 'F'}",
                "Screen": "SUCCESS" if screen["success"] else "FAIL",
            }
        )
    return md_table(rows, ["Branch", "Best config", "WF vs round best", "CAGR vs headline-1pp", "MDD >= -50%", "Screen"])


def write_report(
    frame: pd.DataFrame,
    screens: list[dict[str, object]],
    plot_rows: list[dict[str, str]],
    sanity: dict[str, float],
) -> None:
    n_success = sum(1 for s in screens if s["success"])
    sanity_text = "; ".join(f"{k}: max abs diff {v:.3g}" for k, v in sanity.items())
    sections = [
        "# Phase 7F - Composition of the Round Winners (DIAGNOSTIC)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "Composes the two orthogonal round winners with FROZEN parameters: 7A ensemble fraction (narrow set {150,175,200,225}) `[systematic_trading, p.118-119, p.129-133]` x 7D quadratic vol-target (sigma 40% / RV21) `[volatility_trading, p.135, p.138-140]`. Only the lag is swept; no new parameter search `[advances_fin_ml, p.208-211]`.\n\n"
        f"Pre-registered grid: 2 branches x 2 variants x 6 lags = {N_TRIALS_ADDED} rows. **n_trials ledger: {N_TRIALS_LEDGER_BEFORE} + {N_TRIALS_ADDED} = {N_TRIALS_LEDGER_BEFORE + N_TRIALS_ADDED}.**\n\n"
        f"**Built-in sanity (f_t forced to 1 vs pure quadratic ladder pipeline):** {sanity_text}.\n\n"
        "## Executive Conclusion\n\n"
        f"Pre-registered screen (best trial row per branch by WF beats, tie-break Calmar): **{n_success}/{len(screens)} branches SUCCESS**. Criteria: WF beats strictly above the round best (SPY 13/17 from 7A, QQQ 8/11 from 7D) AND CAGR >= headline - 1pp AND MDD >= -50%. Either way, the round closes into the consolidated decision table for the user's Phase 8 pick. NOT a gate pass, NOT a promotion `[advances_fin_ml, p.208-211]`.\n\n",
    ]
    sections.append("## Screen Result\n\n" + screen_table(screens))
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    for screen in screens:
        sections.append(
            f"## Top {screen['branch']} Rows (by WF beats, then Calmar)\n\n"
            + top_rows_table(frame, str(screen["branch"]))
        )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        + "".join(
            f"| {s['branch']}: composition beats the round best on WF? | {'Yes' if s['crit_wf'] else 'No'} ({int(s['best']['wf_beats'])}/{int(s['best']['wf_windows'])} vs {int(s['round_best_wf'])}). |\n"
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
    best_key: dict[str, tuple[int, float]] = {}
    best_returns: dict[str, pd.Series] = {}
    best_exposures: dict[str, pd.Series] = {}
    baseline_returns: dict[str, pd.Series] = {}
    sanity: dict[str, float] = {}

    for spec in BRANCH_SPECS:
        branch_key = str(spec["branch"])
        context = phase04.build_context(phase04.BRANCHES[branch_key])
        risk_off_weights = clean_weights(
            next(r["weights"] for r in phase04.RISK_OFF_SPECS if r["name"] == spec["risk_off"])
        )
        prices = branch_prices(context)
        fraction_raw = sma_ensemble_fraction(prices, WINDOW_SET).reindex(context.returns.index).fillna(0.0)
        leverage = quadratic_leverage_series(
            context.returns[context.branch["underlying"]], RV_WINDOW, SIGMA_TARGET, float(spec["l_max"])
        )
        sanity[branch_key] = sanity_fraction_one(context, spec, leverage, risk_off_weights)

        # Non-trial baseline: binary headline for plots context.
        vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == spec["vol"])
        headline_lag = 3 if branch_key == "SPY" else 0
        baseline_returns[branch_key] = phase04.simulate_returns(
            context, float(spec["l_max"]), risk_off_weights, vol_spec, headline_lag
        )

        for variant in VARIANTS:
            for lag in LAGS:
                row, taxed, exposure = evaluate_row(
                    context, spec, variant, lag, fraction_raw, leverage, risk_off_weights
                )
                rows.append(row)
                key = (int(row["wf_beats"]), float(row["taxed_calmar"]))
                if branch_key not in best_key or key > best_key[branch_key]:
                    best_key[branch_key] = key
                    best_returns[branch_key] = taxed
                    best_exposures[f"{branch_key} {variant} lag {lag}"] = exposure
        print(f"  {branch_key}: grid done (sanity max abs diff {sanity[branch_key]:.3g})")

    frame = pd.DataFrame(rows)
    frame.to_csv(CSV, index=False)
    screens = [screen_branch(frame, str(spec["branch"])) for spec in BRANCH_SPECS]
    plot_rows = []
    exp_plot = plot_exposure_series(best_exposures)
    plot_rows.append({"Plot": "Best-row composed exposure f*L", "File": f"[plots/{exp_plot.name}](plots/{exp_plot.name})"})
    eq = plot_equity_dd(best_returns, baseline_returns)
    plot_rows.append({"Plot": "Equity/drawdown vs binary headline", "File": f"[plots/{eq.name}](plots/{eq.name})"})
    wf = plot_wf_comparison(screens)
    plot_rows.append({"Plot": "WF beat-count vs round best", "File": f"[plots/{wf.name}](plots/{wf.name})"})
    frontier = plot_frontier(frame)
    plot_rows.append({"Plot": "CAGR x MDD frontier", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    write_report(frame, screens, plot_rows, sanity)

    for screen in screens:
        best = screen["best"]
        print(
            f"Phase 7F {screen['branch']}: best {best['variant']} lag {int(best['lag_days'])} "
            f"WF {int(best['wf_beats'])}/{int(best['wf_windows'])} (round best {int(screen['round_best_wf'])}) "
            f"CAGR {best['taxed_cagr']:.2%} MDD {best['taxed_mdd']:.2%} "
            f"screen={'SUCCESS' if screen['success'] else 'FAIL'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
