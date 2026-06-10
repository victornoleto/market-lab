"""Phase 7D - quadratic vol-targeting sigma^2/RV^2 (DIAGNOSTIC).

Research-only. Single citable variation on Phase 6B: continuous-Kelly sizing
is proportional to inverse VARIANCE, `f = r / sigma^2` `[volatility_trading,
p.135, p.138]`, so the leverage scalar becomes
`L_t = clip(sigma_target^2 / RV_t^2, 0, L_max)` - cutting exposure faster as
vol rises than 6B's linear form. The L_max cap is the fractional-Kelly
discipline `[volatility_trading, p.139-140]`; sizing frame per
`[systematic_trading, p.137-148]`. Hypothesis: the harder vol response flips
`bear_mid` windows (0% beat in 6C) and lifts WF consistency above 6B.
Pre-registered grid: 72 rows (2 branches x 3 sigma_targets x 2 RV windows x 6
lags); +72 to the n_trials ledger (4221 -> 4293). No deployment, no
paper-trade label, no mandate change.
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
    clean_weights,
    equity_curve,
    fmt_num,
    fmt_pct,
    md_table,
    metrics_from_returns,
)
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase06b_vol_target_continuous import run as phase06b  # noqa: E402
from lrs.lib.backtest import build_weekly_lagged_weights, simulate_weight_frame  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase07d_vol_target_quadratic.csv"
PHASE6B_CSV = RESULTS / "phase06b_vol_target_continuous.csv"

LADDER_STEP = 0.25
SIGMA_TARGETS = [0.30, 0.35, 0.40]
RV_WINDOWS = [21, 63]
LAGS = list(range(6))
N_TRIALS_ADDED = len(SIGMA_TARGETS) * len(RV_WINDOWS) * len(LAGS) * 2  # 72
N_TRIALS_LEDGER_BEFORE = 4221
MDD_FLOOR = -0.50
CAGR_TOLERANCE_PP = 0.01


def quadratic_leverage_series(
    underlying_returns: pd.Series,
    rv_window: int,
    sigma_target: float,
    l_max: float,
    step: float = LADDER_STEP,
) -> pd.Series:
    """Quadratic vol-target scalar `clip((sigma_target / RV_t)^2, 0, L_max)`.

    Identical conventions to `phase06b.continuous_leverage_series` (RV
    estimator, one-bar lag, 0.25-ladder quantization with inertia); only the
    raw scalar is squared - the continuous-Kelly inverse-variance form
    `[volatility_trading, p.135, p.138]`, capped per `[volatility_trading,
    p.139-140]`.
    """
    rv = underlying_returns.rolling(rv_window).std(ddof=0).shift(1) * np.sqrt(252.0)
    raw = ((sigma_target / rv) ** 2).clip(lower=0.0, upper=l_max)
    raw = raw.where(np.isfinite(raw), 0.0).fillna(0.0)
    held = 0.0
    out: list[float] = []
    for value in raw.to_numpy(dtype=float):
        if abs(value - held) >= step:
            held = float(min(l_max, max(0.0, round(value / step) * step)))
        out.append(held)
    return pd.Series(out, index=raw.index, name="leverage")


def evaluate_row(
    context: "phase04.BranchContext",
    spec: dict[str, object],
    sigma_target: float,
    rv_window: int,
    lag: int,
    risk_off_weights: dict[str, float],
) -> tuple[dict[str, object], pd.Series, pd.Series]:
    leverage = quadratic_leverage_series(
        context.returns[context.branch["underlying"]], rv_window, sigma_target, float(spec["l_max"])
    )
    desired = phase06b.desired_targets_continuous(context, leverage, risk_off_weights)
    weights, weight_summary = build_weekly_lagged_weights(desired, lag_days=lag)
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    metrics = metrics_from_returns(taxed)
    beats, n_windows = phase06b.wf_beats(taxed, context.underlying_taxed)
    risk_on = context.sma_signal.reindex(context.returns.index).fillna(False)
    lev_on = leverage[risk_on]
    row: dict[str, object] = {
        "config_type": "quadratic",
        "branch": spec["branch"],
        "sigma_target": sigma_target,
        "rv_window": rv_window,
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
        "mean_leverage_risk_on": float(lev_on.mean()) if len(lev_on) else float("nan"),
        "pct_risk_on_at_lmax": float((lev_on >= float(spec["l_max"]) - 1e-9).mean()) if len(lev_on) else float("nan"),
        "state_changes": weight_summary["state_changes"],
        "turnover_per_year": tax_summary["turnover_per_year"],
        "total_tax_paid_pct_initial": tax_summary["total_tax_paid_pct_initial"],
    }
    return row, taxed, leverage


def best_6b_linear(branch: str) -> dict[str, object]:
    """Best Phase 6B linear row per branch (by WF beats, tie Calmar), from its CSV."""
    df = pd.read_csv(PHASE6B_CSV)
    sub = df[(df["config_type"] == "continuous") & (df["branch"] == branch)]
    return sub.sort_values(["wf_beats", "taxed_calmar"], ascending=False).iloc[0].to_dict()


def screen_branch(frame: pd.DataFrame, branch: str, linear_best: dict[str, object]) -> dict[str, object]:
    quad = frame[(frame["config_type"] == "quadratic") & (frame["branch"] == branch)]
    base = frame[(frame["config_type"] == "binary_baseline") & (frame["branch"] == branch)].iloc[0]
    best = quad.sort_values(["wf_beats", "taxed_calmar"], ascending=False).iloc[0]
    control_wf = max(int(base["wf_beats"]), int(linear_best["wf_beats"]))
    crit_wf = bool(best["wf_beats"] > control_wf)
    crit_cagr = bool(best["taxed_cagr"] >= base["taxed_cagr"] - CAGR_TOLERANCE_PP)
    crit_mdd = bool(best["taxed_mdd"] >= MDD_FLOOR)
    return {
        "branch": branch,
        "best": best,
        "baseline": base,
        "linear_best": linear_best,
        "control_wf": control_wf,
        "crit_wf": crit_wf,
        "crit_cagr": crit_cagr,
        "crit_mdd": crit_mdd,
        "success": bool(crit_wf and crit_cagr and crit_mdd),
    }


# --------------------------------------------------------------------------- plots


def plot_leverage_series(best_levs: dict[str, pd.Series]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(best_levs), 1, figsize=(13, 3.2 * len(best_levs)), squeeze=False)
    for ax, (label, lev) in zip(axes.ravel(), best_levs.items()):
        ax.plot(lev.index, lev.to_numpy(dtype=float), linewidth=0.7, color="tab:purple")
        ax.set_title(f"{label}: quadratic ladder leverage L_t")
        ax.set_ylabel("L_t")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07d_leverage_series.png"
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
            {"quadratic best": best_returns[branch], "binary baseline": baseline_returns[branch]},
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
    out = PLOTS / "phase07d_equity_dd.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_wf_comparison(screens: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    labels = [str(s["branch"]) for s in screens]
    base_vals = [int(s["baseline"]["wf_beats"]) for s in screens]
    lin_vals = [int(s["linear_best"]["wf_beats"]) for s in screens]
    quad_vals = [int(s["best"]["wf_beats"]) for s in screens]
    x = np.arange(len(labels))
    ax.bar(x - 0.25, base_vals, width=0.25, label="binary baseline", color="#888888")
    ax.bar(x, lin_vals, width=0.25, label="6B linear best", color="tab:blue")
    ax.bar(x + 0.25, quad_vals, width=0.25, label="7D quadratic best", color="tab:purple")
    for i, screen in enumerate(screens):
        ax.text(i, max(base_vals[i], lin_vals[i], quad_vals[i]) + 0.2, f"/{int(screen['best']['wf_windows'])}", ha="center")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("WF windows beating underlying")
    ax.set_title("Phase 7D: walk-forward beat count (Phase 4 splits)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07d_wf_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6))
    quad = frame[frame["config_type"] == "quadratic"]
    for sigma, sub in quad.groupby("sigma_target"):
        ax.scatter(sub["taxed_mdd"] * 100.0, sub["taxed_cagr"] * 100.0, s=30, alpha=0.7, label=f"sigma {float(sigma):.0%}")
    base = frame[frame["config_type"] == "binary_baseline"]
    ax.scatter(base["taxed_mdd"] * 100.0, base["taxed_cagr"] * 100.0, s=90, marker="*", color="black", label="binary baselines")
    ax.axvline(MDD_FLOOR * 100.0, color="red", linestyle="--", linewidth=0.9, label="MDD -50% floor")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.set_title("Phase 7D frontier: quadratic vol-targeting grid")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase07d_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def top_rows_table(frame: pd.DataFrame, branch: str, limit: int = 8) -> str:
    sub = frame[(frame["config_type"] == "quadratic") & (frame["branch"] == branch)]
    sub = sub.sort_values(["wf_beats", "taxed_calmar"], ascending=False).head(limit)
    rows = [
        {
            "Sigma": fmt_pct(r["sigma_target"], 0),
            "RV": int(r["rv_window"]),
            "Lag": int(r["lag_days"]),
            "WF": f"{int(r['wf_beats'])}/{int(r['wf_windows'])}",
            "CAGR": fmt_pct(r["taxed_cagr"]),
            "MDD": fmt_pct(r["taxed_mdd"]),
            "Sharpe": fmt_num(r["taxed_sharpe"]),
            "Calmar": fmt_num(r["taxed_calmar"]),
            "Mean L (on)": fmt_num(r["mean_leverage_risk_on"], 2),
            "Turnover/y": fmt_num(r["turnover_per_year"], 2),
        }
        for _, r in sub.iterrows()
    ]
    return md_table(rows, ["Sigma", "RV", "Lag", "WF", "CAGR", "MDD", "Sharpe", "Calmar", "Mean L (on)", "Turnover/y"])


def screen_table(screens: list[dict[str, object]]) -> str:
    rows = []
    for screen in screens:
        best = screen["best"]
        rows.append(
            {
                "Branch": screen["branch"],
                "Best config": f"sigma {fmt_pct(best['sigma_target'], 0)} / RV{int(best['rv_window'])} / lag {int(best['lag_days'])}",
                "WF vs control": f"{int(best['wf_beats'])}/{int(best['wf_windows'])} vs {int(screen['control_wf'])} {'P' if screen['crit_wf'] else 'F'}",
                "CAGR vs headline-1pp": f"{fmt_pct(best['taxed_cagr'])} vs {fmt_pct(screen['baseline']['taxed_cagr'])} {'P' if screen['crit_cagr'] else 'F'}",
                "MDD >= -50%": f"{fmt_pct(best['taxed_mdd'])} {'P' if screen['crit_mdd'] else 'F'}",
                "Screen": "SUCCESS" if screen["success"] else "FAIL",
            }
        )
    return md_table(rows, ["Branch", "Best config", "WF vs control", "CAGR vs headline-1pp", "MDD >= -50%", "Screen"])


def write_report(frame: pd.DataFrame, screens: list[dict[str, object]], plot_rows: list[dict[str, str]]) -> None:
    n_success = sum(1 for s in screens if s["success"])
    sections = [
        "# Phase 7D - Quadratic Vol-Targeting sigma^2/RV^2 (DIAGNOSTIC)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "Single variation on Phase 6B: the leverage scalar is the continuous-Kelly inverse-variance form `L_t = clip(sigma_target^2 / RV_t^2, 0, L_max)` `[volatility_trading, p.135, p.138]`, capped per fractional-Kelly practice `[volatility_trading, p.139-140]`, with 6B's 0.25-ladder quantization, inertia, SMA200 weekly gate, risk-off sleeves and DARF tax verbatim `[systematic_trading, p.137-148]`.\n\n"
        f"Pre-registered grid: 2 branches x 3 sigma_targets x 2 RV windows x 6 lags = {N_TRIALS_ADDED} rows. **n_trials ledger: {N_TRIALS_LEDGER_BEFORE} + {N_TRIALS_ADDED} = {N_TRIALS_LEDGER_BEFORE + N_TRIALS_ADDED}.** Binary-baseline rows and the 6B linear-best comparison are not trials.\n\n"
        "## Executive Conclusion\n\n"
        f"Pre-registered screen (best row per branch by WF beats, tie-break Calmar): **{n_success}/{len(screens)} branches SUCCESS**. Criteria: WF beats strictly above the better of {{binary baseline, 6B linear best}} AND after-tax CAGR >= headline - 1pp AND MDD >= -50%. A SUCCESS feeds the Phase 7F composition slot only - NOT a gate pass, NOT a promotion `[advances_fin_ml, p.208-211]`.\n\n",
    ]
    sections.append("## Screen Result\n\n" + screen_table(screens))
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    for screen in screens:
        base = screen["baseline"]
        lin = screen["linear_best"]
        sections.append(
            f"## Top {screen['branch']} Rows (by WF beats, then Calmar)\n\n"
            + top_rows_table(frame, str(screen["branch"]))
            + f"\nBinary baseline: WF {int(base['wf_beats'])}/{int(base['wf_windows'])}, CAGR {fmt_pct(base['taxed_cagr'])}, MDD {fmt_pct(base['taxed_mdd'])}. "
            f"6B linear best: sigma {fmt_pct(float(lin['sigma_target']), 0)}/RV{int(lin['rv_window'])}/lag {int(lin['lag_days'])}, WF {int(lin['wf_beats'])}/{int(lin['wf_windows'])}, CAGR {fmt_pct(float(lin['taxed_cagr']))}, MDD {fmt_pct(float(lin['taxed_mdd']))}.\n"
        )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        + "".join(
            f"| {s['branch']}: quadratic sizing beats binary AND 6B linear on WF? | {'Yes' if s['crit_wf'] else 'No'} ({int(s['best']['wf_beats'])}/{int(s['best']['wf_windows'])} vs control {int(s['control_wf'])}). |\n"
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
    best_levs: dict[str, pd.Series] = {}
    baseline_returns: dict[str, pd.Series] = {}

    for spec in phase06b.BRANCH_SPECS:
        branch_key = str(spec["branch"])
        context = phase04.build_context(phase04.BRANCHES[branch_key])
        risk_off = next(r for r in phase04.RISK_OFF_SPECS if r["name"] == spec["risk_off"])
        risk_off_weights = clean_weights(dict(risk_off["weights"]))  # type: ignore[arg-type]

        baseline_row, baseline_taxed = phase06b.evaluate_baseline(context, spec)
        rows.append(baseline_row)
        baseline_returns[branch_key] = baseline_taxed

        branch_best: tuple[int, float] | None = None
        branch_best_lev: tuple[str, pd.Series] | None = None
        for sigma_target in SIGMA_TARGETS:
            for rv_window in RV_WINDOWS:
                for lag in LAGS:
                    row, taxed, leverage = evaluate_row(
                        context, spec, sigma_target, rv_window, lag, risk_off_weights
                    )
                    rows.append(row)
                    key = (int(row["wf_beats"]), float(row["taxed_calmar"]))
                    if branch_best is None or key > branch_best:
                        branch_best = key
                        best_returns[branch_key] = taxed
                        label = f"{branch_key} sigma {sigma_target:.0%} RV{rv_window} lag {lag}"
                        branch_best_lev = (label, leverage)
        if branch_best_lev is not None:
            best_levs[branch_best_lev[0]] = branch_best_lev[1]
        print(f"  {branch_key}: grid done")

    frame = pd.DataFrame(rows)
    frame.to_csv(CSV, index=False)
    screens = [
        screen_branch(frame, str(spec["branch"]), best_6b_linear(str(spec["branch"])))
        for spec in phase06b.BRANCH_SPECS
    ]
    plot_rows = []
    lev_plot = plot_leverage_series(best_levs)
    plot_rows.append({"Plot": "Best-row quadratic leverage series", "File": f"[plots/{lev_plot.name}](plots/{lev_plot.name})"})
    eq = plot_equity_dd(best_returns, baseline_returns)
    plot_rows.append({"Plot": "Equity/drawdown vs binary baseline", "File": f"[plots/{eq.name}](plots/{eq.name})"})
    wf = plot_wf_comparison(screens)
    plot_rows.append({"Plot": "WF beat-count: baseline vs 6B linear vs 7D quadratic", "File": f"[plots/{wf.name}](plots/{wf.name})"})
    frontier = plot_frontier(frame)
    plot_rows.append({"Plot": "CAGR x MDD frontier", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    write_report(frame, screens, plot_rows)

    for screen in screens:
        best = screen["best"]
        print(
            f"Phase 7D {screen['branch']}: best sigma {best['sigma_target']:.0%} RV{int(best['rv_window'])} "
            f"lag {int(best['lag_days'])} WF {int(best['wf_beats'])}/{int(best['wf_windows'])} "
            f"(control {int(screen['control_wf'])}) CAGR {best['taxed_cagr']:.2%} "
            f"MDD {best['taxed_mdd']:.2%} screen={'SUCCESS' if screen['success'] else 'FAIL'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
