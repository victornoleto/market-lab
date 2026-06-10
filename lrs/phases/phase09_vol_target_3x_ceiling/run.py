"""Phase 9 - quadratic vol-targeting with a 3x ceiling (DIAGNOSTIC, return-first).

Research-only, user-directed (2026-06-10): raise the 7D quadratic sizing cap
to L_max {2.50, 3.00} so the ladder reaches the cached 3x sleeves
(UPROSIM/TQQQSIM) only in calm regimes - the continuous-Kelly reading of when
3x is the right exposure `[volatility_trading, p.135, p.138]`,
`[volatility_trading, p.139-140]`, `[systematic_trading, p.137-148]`.
Mechanism verbatim from Phase 7D/6B; new axis values L_max {2.50, 3.00} and
sigma_target 45%. Pre-registered grid: 48 rows (2 branches x 2 caps x 2
sigmas x 6 lags); +48 to the n_trials ledger (4377 -> 4425). Return-first
screen per the user's direction; NOT a gate pass either way. No deployment,
no paper-trade label, no mandate change.
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
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase06b_vol_target_continuous import run as phase06b  # noqa: E402
from lrs.phases.phase07d_vol_target_quadratic.run import quadratic_leverage_series  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase09_vol_target_3x_ceiling.csv"
PHASE7D_CSV = RESULTS / "phase07d_vol_target_quadratic.csv"

L_MAXES = [2.50, 3.00]
SIGMA_TARGETS = [0.40, 0.45]
RV_WINDOW = 21
LAGS = list(range(6))
N_TRIALS_ADDED = 2 * len(L_MAXES) * len(SIGMA_TARGETS) * len(LAGS)  # 48
N_TRIALS_LEDGER_BEFORE = 4377
MDD_FLOOR = -0.50

# 7D branch winners (committed comparison bars, read from the 7D CSV at runtime).
WINNER_7D = {
    "SPY": {"sigma_target": 0.40, "rv_window": 21, "lag_days": 3, "l_max": 2.00},
    "QQQ": {"sigma_target": 0.40, "rv_window": 21, "lag_days": 2, "l_max": 1.75},
}

BRANCH_SPECS: list[dict[str, object]] = [
    {
        "branch": "SPY",
        "risk_off": "50 ZROZ / 25 GLD / 25 CASH",
        "baseline_name": "spy_top",
        "baseline_vol": "RV21 <= 30%",
        "baseline_lag": 3,
        "headline_l_max": 2.00,
    },
    {
        "branch": "QQQ",
        "risk_off": "40 ZROZ / 40 GLD / 20 IEF",
        "baseline_name": "qqq_top",
        "baseline_vol": "RV63 <= 40%",
        "baseline_lag": 0,
        "headline_l_max": 1.75,
    },
]


def evaluate_row(
    context: "phase04.BranchContext",
    spec: dict[str, object],
    l_max: float,
    sigma_target: float,
    lag: int,
    risk_off_weights: dict[str, float],
) -> tuple[dict[str, object], pd.Series, pd.Series]:
    leverage = quadratic_leverage_series(
        context.returns[context.branch["underlying"]], RV_WINDOW, sigma_target, l_max
    )
    desired = phase06b.desired_targets_continuous(context, leverage, risk_off_weights)
    weights, weight_summary = build_weekly_lagged_weights(desired, lag_days=lag)
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    metrics = metrics_from_returns(taxed)
    beats, n_windows = phase06b.wf_beats(taxed, context.underlying_taxed)
    risk_on = context.sma_signal.reindex(context.returns.index).fillna(False)
    lev_on = leverage[risk_on]
    row: dict[str, object] = {
        "config_type": "ceiling",
        "branch": spec["branch"],
        "l_max": l_max,
        "sigma_target": sigma_target,
        "rv_window": RV_WINDOW,
        "lag_days": lag,
        "risk_off": spec["risk_off"],
        "taxed_cagr": metrics.cagr,
        "taxed_mdd": metrics.mdd,
        "taxed_sharpe": metrics.sharpe,
        "taxed_sortino": metrics.sortino,
        "taxed_calmar": metrics.calmar,
        "taxed_terminal": metrics.terminal,
        "wf_beats": beats,
        "wf_windows": n_windows,
        "mean_leverage_risk_on": float(lev_on.mean()) if len(lev_on) else float("nan"),
        "pct_risk_on_above_2x": float((lev_on > 2.0 + 1e-9).mean()) if len(lev_on) else float("nan"),
        "pct_risk_on_at_lmax": float((lev_on >= l_max - 1e-9).mean()) if len(lev_on) else float("nan"),
        "state_changes": weight_summary["state_changes"],
        "turnover_per_year": tax_summary["turnover_per_year"],
        "total_tax_paid_pct_initial": tax_summary["total_tax_paid_pct_initial"],
    }
    return row, taxed, leverage


def winner_7d_row(branch: str) -> pd.Series:
    df = pd.read_csv(PHASE7D_CSV)
    spec = WINNER_7D[branch]
    rows = df[
        (df["config_type"] == "quadratic")
        & (df["branch"] == branch)
        & (df["sigma_target"] == spec["sigma_target"])
        & (df["rv_window"] == spec["rv_window"])
        & (df["lag_days"] == spec["lag_days"])
    ]
    return rows.iloc[0]


def sanity_reproduce_7d_winner(
    context: "phase04.BranchContext", spec: dict[str, object], risk_off_weights: dict[str, float]
) -> float:
    """Re-run the 7D winner through this pipeline; must match its committed CSV row."""
    branch = str(spec["branch"])
    committed = winner_7d_row(branch)
    w = WINNER_7D[branch]
    row, _taxed, _lev = evaluate_row(
        context, spec, float(w["l_max"]), float(w["sigma_target"]), int(w["lag_days"]), risk_off_weights
    )
    return float(
        max(
            abs(float(committed["taxed_cagr"]) - float(row["taxed_cagr"])),
            abs(float(committed["taxed_mdd"]) - float(row["taxed_mdd"])),
        )
    )


def screen_branch(frame: pd.DataFrame, branch: str) -> dict[str, object]:
    """Return-first pre-registered screen: best CAGR among MDD>=-50% rows."""
    trials = frame[(frame["config_type"] == "ceiling") & (frame["branch"] == branch)]
    eligible = trials[trials["taxed_mdd"] >= MDD_FLOOR]
    winner = winner_7d_row(branch)
    if eligible.empty:
        return {
            "branch": branch,
            "best": None,
            "winner_7d": winner,
            "crit_cagr": False,
            "crit_mdd": False,
            "crit_wf": False,
            "success": False,
        }
    best = eligible.sort_values(["taxed_cagr", "taxed_calmar"], ascending=False).iloc[0]
    crit_cagr = bool(best["taxed_cagr"] > float(winner["taxed_cagr"]))
    crit_mdd = bool(best["taxed_mdd"] >= MDD_FLOOR)
    crit_wf = bool(best["wf_beats"] >= int(winner["wf_beats"]))
    return {
        "branch": branch,
        "best": best,
        "winner_7d": winner,
        "crit_cagr": crit_cagr,
        "crit_mdd": crit_mdd,
        "crit_wf": crit_wf,
        "success": bool(crit_cagr and crit_mdd and crit_wf),
    }


# --------------------------------------------------------------------------- plots


def plot_leverage_series(best_levs: dict[str, pd.Series]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(best_levs), 1, figsize=(13, 3.2 * len(best_levs)), squeeze=False)
    for ax, (label, lev) in zip(axes.ravel(), best_levs.items()):
        ax.plot(lev.index, lev.to_numpy(dtype=float), linewidth=0.7, color="tab:orange")
        ax.axhline(2.0, color="grey", linestyle=":", linewidth=0.8)
        ax.set_title(f"{label}: ceiling ladder leverage L_t (dotted = 2x line)")
        ax.set_ylabel("L_t")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase09_leverage_series.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_rung_share(best_levs: dict[str, pd.Series]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, len(best_levs), figsize=(6.5 * len(best_levs), 4.2), squeeze=False)
    for ax, (label, lev) in zip(axes[0], best_levs.items()):
        counts = lev.round(2).value_counts(normalize=True).sort_index()
        ax.bar([f"{x:.2f}" for x in counts.index], counts.to_numpy() * 100.0, color="tab:orange")
        ax.set_title(f"{label}: time share per ladder rung")
        ax.set_ylabel("% of days")
        ax.tick_params(axis="x", rotation=60)
        ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase09_rung_share.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_equity_dd(
    best_returns: dict[str, pd.Series],
    winner_returns: dict[str, pd.Series],
    baseline_returns: dict[str, pd.Series],
) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    branches = list(best_returns)
    fig, axes = plt.subplots(2, len(branches), figsize=(7.5 * len(branches), 8.5), squeeze=False)
    for col, branch in enumerate(branches):
        pair = pd.concat(
            {
                "3x-ceiling best": best_returns[branch],
                "7D winner (old cap)": winner_returns[branch],
                "binary headline": baseline_returns[branch],
            },
            axis=1,
        ).dropna()
        eq = pair.apply(equity_curve)
        eq.plot(ax=axes[0][col], logy=True, linewidth=1.0)
        axes[0][col].set_title(f"{branch}: after-tax equity")
        axes[0][col].grid(True, alpha=0.3)
        dd = eq / eq.cummax() - 1.0
        (dd * 100.0).plot(ax=axes[1][col], linewidth=0.9)
        axes[1][col].set_title(f"{branch}: drawdown (%)")
        axes[1][col].grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase09_equity_dd.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6))
    trials = frame[frame["config_type"] == "ceiling"]
    for (l_max, sigma), sub in trials.groupby(["l_max", "sigma_target"]):
        ax.scatter(
            sub["taxed_mdd"] * 100.0, sub["taxed_cagr"] * 100.0, s=35, alpha=0.75,
            label=f"L_max {float(l_max):.2f} / sigma {float(sigma):.0%}",
        )
    ax.axvline(MDD_FLOOR * 100.0, color="red", linestyle="--", linewidth=0.9, label="MDD -50% floor")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.set_title("Phase 9 frontier: quadratic vol-targeting with 2.5x/3x ceilings")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase09_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def top_rows_table(frame: pd.DataFrame, branch: str, limit: int = 10) -> str:
    sub = frame[(frame["config_type"] == "ceiling") & (frame["branch"] == branch)]
    sub = sub.sort_values(["taxed_cagr", "taxed_calmar"], ascending=False).head(limit)
    rows = [
        {
            "L_max": fmt_num(r["l_max"], 2),
            "Sigma": fmt_pct(r["sigma_target"], 0),
            "Lag": int(r["lag_days"]),
            "CAGR": fmt_pct(r["taxed_cagr"]),
            "MDD": fmt_pct(r["taxed_mdd"]),
            "Floor": "ok" if r["taxed_mdd"] >= MDD_FLOOR else "BREACH",
            "WF": f"{int(r['wf_beats'])}/{int(r['wf_windows'])}",
            "Sharpe": fmt_num(r["taxed_sharpe"]),
            "Calmar": fmt_num(r["taxed_calmar"]),
            "Mean L (on)": fmt_num(r["mean_leverage_risk_on"], 2),
            ">2x days (on)": fmt_pct(r["pct_risk_on_above_2x"], 1),
            "Turnover/y": fmt_num(r["turnover_per_year"], 2),
        }
        for _, r in sub.iterrows()
    ]
    return md_table(rows, ["L_max", "Sigma", "Lag", "CAGR", "MDD", "Floor", "WF", "Sharpe", "Calmar", "Mean L (on)", ">2x days (on)", "Turnover/y"])


def screen_table(screens: list[dict[str, object]]) -> str:
    rows = []
    for screen in screens:
        winner = screen["winner_7d"]
        best = screen["best"]
        if best is None:
            rows.append(
                {
                    "Branch": screen["branch"],
                    "Best eligible row": "none (all rows breach the -50% floor)",
                    "CAGR vs 7D winner": "F",
                    "MDD >= -50%": "F",
                    "WF not worse": "F",
                    "Screen": "FAIL",
                }
            )
            continue
        rows.append(
            {
                "Branch": screen["branch"],
                "Best eligible row": f"L_max {float(best['l_max']):.2f} / sigma {fmt_pct(best['sigma_target'], 0)} / lag {int(best['lag_days'])}",
                "CAGR vs 7D winner": f"{fmt_pct(best['taxed_cagr'])} vs {fmt_pct(float(winner['taxed_cagr']))} {'P' if screen['crit_cagr'] else 'F'}",
                "MDD >= -50%": f"{fmt_pct(best['taxed_mdd'])} {'P' if screen['crit_mdd'] else 'F'}",
                "WF not worse": f"{int(best['wf_beats'])}/{int(best['wf_windows'])} vs {int(winner['wf_beats'])}/{int(winner['wf_windows'])} {'P' if screen['crit_wf'] else 'F'}",
                "Screen": "SUCCESS" if screen["success"] else "FAIL",
            }
        )
    return md_table(rows, ["Branch", "Best eligible row", "CAGR vs 7D winner", "MDD >= -50%", "WF not worse", "Screen"])


def write_report(
    frame: pd.DataFrame,
    screens: list[dict[str, object]],
    plot_rows: list[dict[str, str]],
    sanity: dict[str, float],
) -> None:
    n_success = sum(1 for s in screens if s["success"])
    sanity_text = "; ".join(f"{k}: max abs diff {v:.3g}" for k, v in sanity.items())
    sections = [
        "# Phase 9 - Quadratic Vol-Targeting with a 3x Ceiling (DIAGNOSTIC, RETURN-FIRST)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "User-directed phase (2026-06-10): raise the 7D quadratic sizing cap so the ladder reaches the cached 3x sleeves (UPROSIM/TQQQSIM) only in calm regimes - the continuous-Kelly reading of when 3x is the right exposure `[volatility_trading, p.135, p.138]`, `[volatility_trading, p.139-140]`, `[systematic_trading, p.137-148]`. Mechanism verbatim from Phase 7D/6B; new axis values L_max {2.50, 3.00}, sigma_target 45%.\n\n"
        f"Pre-registered grid: 2 branches x 2 caps x 2 sigmas x 6 lags = {N_TRIALS_ADDED} rows. **n_trials ledger: {N_TRIALS_LEDGER_BEFORE} + {N_TRIALS_ADDED} = {N_TRIALS_LEDGER_BEFORE + N_TRIALS_ADDED}.** Binary headline and 7D winner rows are comparisons, not trials.\n\n"
        f"**Built-in sanity (7D winner re-run through this pipeline vs committed CSV):** {sanity_text}.\n\n"
        "## Executive Conclusion\n\n"
        f"Return-first pre-registered screen (best CAGR among MDD>=-50% rows): **{n_success}/{len(screens)} branches SUCCESS**. Criteria: CAGR strictly above the branch 7D winner AND MDD >= -50% AND WF beats not worse. A SUCCESS is a return-first diagnostic lead only - NOT a gate pass; a promotion-grade claim would need the full SS5 suite at the grown ledger, where DSR only gets harder `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.\n\n",
    ]
    sections.append("## Screen Result\n\n" + screen_table(screens))
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    for screen in screens:
        winner = screen["winner_7d"]
        sections.append(
            f"## Top {screen['branch']} Rows (by CAGR; floor breaches marked)\n\n"
            + top_rows_table(frame, str(screen["branch"]))
            + f"\n7D winner (old cap): L_max {float(winner['l_max']):.2f}, sigma {fmt_pct(float(winner['sigma_target']), 0)}/RV{int(winner['rv_window'])}/lag {int(winner['lag_days'])}: CAGR {fmt_pct(float(winner['taxed_cagr']))}, MDD {fmt_pct(float(winner['taxed_mdd']))}, WF {int(winner['wf_beats'])}/{int(winner['wf_windows'])}.\n"
        )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        + "".join(
            (
                f"| {s['branch']}: does a 2.5x/3x ceiling add CAGR within the -50% floor without losing WF? | "
                + ("Yes" if s["success"] else "No")
                + (
                    f" ({fmt_pct(float(s['best']['taxed_cagr']))} @ {fmt_pct(float(s['best']['taxed_mdd']))}, WF {int(s['best']['wf_beats'])}/{int(s['best']['wf_windows'])}). |\n"
                    if s["best"] is not None
                    else " (no row inside the floor). |\n"
                )
            )
            for s in screens
        )
        + f"| Screen successes? | {n_success}/{len(screens)}. |\n"
        "| Did we promote anything? | No - return-first diagnostic only. |\n"
        "| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    best_returns: dict[str, pd.Series] = {}
    best_levs: dict[str, pd.Series] = {}
    winner_returns: dict[str, pd.Series] = {}
    baseline_returns: dict[str, pd.Series] = {}
    sanity: dict[str, float] = {}

    for spec in BRANCH_SPECS:
        branch_key = str(spec["branch"])
        context = phase04.build_context(phase04.BRANCHES[branch_key])
        risk_off = next(r for r in phase04.RISK_OFF_SPECS if r["name"] == spec["risk_off"])
        risk_off_weights = clean_weights(dict(risk_off["weights"]))  # type: ignore[arg-type]

        sanity[branch_key] = sanity_reproduce_7d_winner(context, spec, risk_off_weights)

        # Non-trial comparison curves for plots: 7D winner + binary headline.
        w = WINNER_7D[branch_key]
        _r, winner_taxed, _l = evaluate_row(
            context, spec, float(w["l_max"]), float(w["sigma_target"]), int(w["lag_days"]), risk_off_weights
        )
        winner_returns[branch_key] = winner_taxed
        vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == spec["baseline_vol"])
        baseline_returns[branch_key] = phase04.simulate_returns(
            context, float(spec["headline_l_max"]), risk_off_weights, vol_spec, int(spec["baseline_lag"])
        )

        best_key: tuple[float, float] | None = None
        for l_max in L_MAXES:
            for sigma_target in SIGMA_TARGETS:
                for lag in LAGS:
                    row, taxed, leverage = evaluate_row(
                        context, spec, l_max, sigma_target, lag, risk_off_weights
                    )
                    rows.append(row)
                    if row["taxed_mdd"] >= MDD_FLOOR:
                        key = (float(row["taxed_cagr"]), float(row["taxed_calmar"]))
                        if best_key is None or key > best_key:
                            best_key = key
                            best_returns[branch_key] = taxed
                            best_levs[
                                f"{branch_key} L_max {l_max:.2f} sigma {sigma_target:.0%} lag {lag}"
                            ] = leverage
        print(f"  {branch_key}: grid done (sanity max abs diff {sanity[branch_key]:.3g})")

    frame = pd.DataFrame(rows)
    frame.to_csv(CSV, index=False)
    screens = [screen_branch(frame, str(spec["branch"])) for spec in BRANCH_SPECS]
    plot_rows = []
    if best_levs:
        lev_plot = plot_leverage_series(best_levs)
        plot_rows.append({"Plot": "Best-row ceiling leverage series", "File": f"[plots/{lev_plot.name}](plots/{lev_plot.name})"})
        rung = plot_rung_share(best_levs)
        plot_rows.append({"Plot": "Time share per ladder rung", "File": f"[plots/{rung.name}](plots/{rung.name})"})
    if best_returns:
        eq = plot_equity_dd(best_returns, winner_returns, baseline_returns)
        plot_rows.append({"Plot": "Equity/drawdown vs 7D winner and binary headline", "File": f"[plots/{eq.name}](plots/{eq.name})"})
    frontier = plot_frontier(frame)
    plot_rows.append({"Plot": "CAGR x MDD frontier by cap/sigma", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    write_report(frame, screens, plot_rows, sanity)

    for screen in screens:
        best = screen["best"]
        winner = screen["winner_7d"]
        if best is None:
            print(f"Phase 9 {screen['branch']}: no row inside the -50% floor -> FAIL")
            continue
        print(
            f"Phase 9 {screen['branch']}: best L_max {float(best['l_max']):.2f} sigma {float(best['sigma_target']):.0%} "
            f"lag {int(best['lag_days'])} CAGR {best['taxed_cagr']:.2%} (7D winner {float(winner['taxed_cagr']):.2%}) "
            f"MDD {best['taxed_mdd']:.2%} WF {int(best['wf_beats'])}/{int(best['wf_windows'])} "
            f"screen={'SUCCESS' if screen['success'] else 'FAIL'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
