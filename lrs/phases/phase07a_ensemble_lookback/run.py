"""Phase 7A - ensemble multi-lookback fractional position (DIAGNOSTIC).

Research-only. Replaces the binary SMA200 gate of the Phase 2/4 bases with a
combined forecast over N SMA windows: the position fraction is the share of
member signals that are risk-on, `f_t = (1/N) sum_w 1[P>SMA_w]` lagged
`[systematic_trading, p.118-119, p.129-133]`. Equal weighting is justified by
the paper's own robustness table (all MA windows carry similar Sharpe)
`[leverage_for_the_long_run, p.14, Table 6]`. Hypothesis: averaging reduces
window-luck/whipsaw and improves walk-forward consistency, the binding Phase 4
gate `[testing_tuning, p.327-335]`. Pre-registered grid: 72 rows (6 bases x 2
window sets x 6 lags); +72 to the n_trials ledger (4005 -> 4077). No
deployment, no paper-trade label, no mandate change.
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
    load_price_frame,
    md_table,
    metrics_from_returns,
    simulate_weight_frame,
)
from lrs.lib.indicators import sma_ensemble_fraction  # noqa: E402
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase06b_vol_target_continuous.run import wf_beats  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase07a_ensemble_lookback.csv"

WINDOW_SETS: dict[str, list[int]] = {
    "narrow_150_225": [150, 175, 200, 225],
    "wide_100_300": [100, 150, 200, 250, 300],
}
LAGS = list(range(6))
N_TRIALS_ADDED = len(phase04.BASE_SPECS) * len(WINDOW_SETS) * len(LAGS)  # 72
N_TRIALS_LEDGER_BEFORE = 4005
MDD_FLOOR = -0.50
CAGR_TOLERANCE_PP = 0.01
# Reported-only G3 gate levels (>=75% of WF windows), not the screen bar.
GATE_LEVELS = {"SPY": "13/17", "QQQ": "9/11"}
HEADLINE_BASES = {"SPY": "spy_top", "QQQ": "qqq_top"}


def branch_prices(context: "phase04.BranchContext") -> pd.Series:
    """Underlying price series aligned to the context's return index.

    Mirrors `phase04.build_context`: prices are reindexed to the pct-change
    index so the degenerate `{200}` ensemble reproduces `context.sma_signal`
    exactly (sanity anchor).
    """
    prices = load_price_frame(phase04.branch_assets(context.branch))
    return prices[context.branch["underlying"]].reindex(context.returns.index)


def ensemble_fraction(context: "phase04.BranchContext", windows: list[int]) -> pd.Series:
    frac = sma_ensemble_fraction(branch_prices(context), windows)
    return frac.reindex(context.returns.index).fillna(0.0)


def desired_targets_fractional(
    context: "phase04.BranchContext",
    fraction: pd.Series,
    risk_on_weights: dict[str, float],
    risk_off_weights: dict[str, float],
) -> pd.DataFrame:
    """Daily desired weights: g_t * risk_on + (1 - g_t) * risk_off."""
    index = context.returns.index
    g = fraction.reindex(index).fillna(0.0).to_numpy(dtype=float)
    assets = sorted(set(risk_on_weights) | set(risk_off_weights) | {"CASHX"})
    frame = pd.DataFrame(0.0, index=index, columns=assets)
    for asset in assets:
        frame[asset] = g * risk_on_weights.get(asset, 0.0) + (1.0 - g) * risk_off_weights.get(asset, 0.0)
    return frame


def evaluate_row(
    context: "phase04.BranchContext",
    base: dict[str, object],
    set_name: str,
    lag: int,
    fraction_by_set: dict[str, pd.Series],
) -> tuple[dict[str, object], pd.Series]:
    risk_on = phase04.target_leverage_weights(context.branch, float(base["target_leverage"]))
    risk_off_weights = clean_weights(
        next(r["weights"] for r in phase04.RISK_OFF_SPECS if r["name"] == base["risk_off"])
    )
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == base["vol"])
    gate = phase04.vol_gate(context, vol_spec).astype(float)
    fraction = fraction_by_set[set_name] * gate
    desired = desired_targets_fractional(context, fraction, risk_on, risk_off_weights)
    weights, weight_summary = build_weekly_lagged_weights(desired, lag_days=lag)
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    metrics = metrics_from_returns(taxed)
    beats, n_windows = wf_beats(taxed, context.underlying_taxed)
    row: dict[str, object] = {
        "config_type": "ensemble",
        "branch": base["branch"],
        "base_name": base["name"],
        "window_set": set_name,
        "lag_days": lag,
        "target_leverage": float(base["target_leverage"]),
        "risk_off": base["risk_off"],
        "vol_filter": base["vol"],
        "taxed_cagr": metrics.cagr,
        "taxed_mdd": metrics.mdd,
        "taxed_sharpe": metrics.sharpe,
        "taxed_sortino": metrics.sortino,
        "taxed_calmar": metrics.calmar,
        "taxed_terminal": metrics.terminal,
        "wf_beats": beats,
        "wf_windows": n_windows,
        "mean_fraction": float(fraction.mean()),
        "pct_days_partial": float(((fraction > 1e-9) & (fraction < 1.0 - 1e-9)).mean()),
        "state_changes": weight_summary["state_changes"],
        "turnover_per_year": tax_summary["turnover_per_year"],
        "total_tax_paid_pct_initial": tax_summary["total_tax_paid_pct_initial"],
    }
    return row, taxed


def evaluate_baseline(
    context: "phase04.BranchContext", base: dict[str, object]
) -> tuple[dict[str, object], pd.Series]:
    """Binary base at its committed best-score lag (comparison, not a trial)."""
    risk_off_weights = clean_weights(
        next(r["weights"] for r in phase04.RISK_OFF_SPECS if r["name"] == base["risk_off"])
    )
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == base["vol"])
    lag = phase04.best_lag_for_base(str(base["name"]))
    taxed = phase04.simulate_returns(
        context, float(base["target_leverage"]), risk_off_weights, vol_spec, lag
    )
    metrics = metrics_from_returns(taxed)
    beats, n_windows = wf_beats(taxed, context.underlying_taxed)
    row: dict[str, object] = {
        "config_type": "binary_baseline",
        "branch": base["branch"],
        "base_name": base["name"],
        "window_set": "single_200",
        "lag_days": lag,
        "target_leverage": float(base["target_leverage"]),
        "risk_off": base["risk_off"],
        "vol_filter": base["vol"],
        "taxed_cagr": metrics.cagr,
        "taxed_mdd": metrics.mdd,
        "taxed_sharpe": metrics.sharpe,
        "taxed_sortino": metrics.sortino,
        "taxed_calmar": metrics.calmar,
        "taxed_terminal": metrics.terminal,
        "wf_beats": beats,
        "wf_windows": n_windows,
        "mean_fraction": float("nan"),
        "pct_days_partial": 0.0,
        "state_changes": float("nan"),
        "turnover_per_year": float("nan"),
        "total_tax_paid_pct_initial": float("nan"),
    }
    return row, taxed


def sanity_degenerate_set(context: "phase04.BranchContext", base: dict[str, object]) -> float:
    """Max abs daily-return diff: ensemble {200} vs the binary base (same lag)."""
    lag = phase04.best_lag_for_base(str(base["name"]))
    risk_on = phase04.target_leverage_weights(context.branch, float(base["target_leverage"]))
    risk_off_weights = clean_weights(
        next(r["weights"] for r in phase04.RISK_OFF_SPECS if r["name"] == base["risk_off"])
    )
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == base["vol"])
    gate = phase04.vol_gate(context, vol_spec).astype(float)
    fraction = ensemble_fraction(context, [200]) * gate
    desired = desired_targets_fractional(context, fraction, risk_on, risk_off_weights)
    weights, _ = build_weekly_lagged_weights(desired, lag_days=lag)
    taxed, _ = simulate_weight_frame(context.returns, weights, taxable=True)
    reference = phase04.simulate_returns(
        context, float(base["target_leverage"]), risk_off_weights, vol_spec, lag
    )
    aligned = pd.concat({"a": taxed, "b": reference}, axis=1).dropna()
    return float((aligned["a"] - aligned["b"]).abs().max())


def screen_branch(frame: pd.DataFrame, branch: str) -> dict[str, object]:
    """Pre-registered screen on the branch best trial row (WF beats, tie Calmar)."""
    trials = frame[(frame["config_type"] == "ensemble") & (frame["branch"] == branch)]
    baselines = frame[(frame["config_type"] == "binary_baseline") & (frame["branch"] == branch)]
    best = trials.sort_values(["wf_beats", "taxed_calmar"], ascending=False).iloc[0]
    base_best = baselines.sort_values(["wf_beats", "taxed_calmar"], ascending=False).iloc[0]
    headline = baselines[baselines["base_name"] == HEADLINE_BASES[branch]].iloc[0]
    crit_wf = bool(best["wf_beats"] > base_best["wf_beats"])
    crit_cagr = bool(best["taxed_cagr"] >= headline["taxed_cagr"] - CAGR_TOLERANCE_PP)
    crit_mdd = bool(best["taxed_mdd"] >= MDD_FLOOR)
    return {
        "branch": branch,
        "best": best,
        "baseline": base_best,
        "headline": headline,
        "crit_wf": crit_wf,
        "crit_cagr": crit_cagr,
        "crit_mdd": crit_mdd,
        "success": bool(crit_wf and crit_cagr and crit_mdd),
    }


# --------------------------------------------------------------------------- plots


def plot_fraction_series(best_fracs: dict[str, pd.Series]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(best_fracs), 1, figsize=(13, 3.0 * len(best_fracs)), squeeze=False)
    for ax, (label, frac) in zip(axes.ravel(), best_fracs.items()):
        ax.plot(frac.index, frac.to_numpy(dtype=float), linewidth=0.6, color="tab:blue")
        ax.set_title(f"{label}: ensemble risk-on fraction f_t")
        ax.set_ylabel("f_t")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07a_fraction_series.png"
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
            {"ensemble best": best_returns[branch], "binary headline": baseline_returns[branch]},
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
    out = PLOTS / "phase07a_equity_dd.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_wf_comparison(screens: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels: list[str] = []
    base_vals: list[int] = []
    best_vals: list[int] = []
    for screen in screens:
        labels.append(str(screen["branch"]))
        base_vals.append(int(screen["baseline"]["wf_beats"]))
        best_vals.append(int(screen["best"]["wf_beats"]))
    x = np.arange(len(labels))
    ax.bar(x - 0.18, base_vals, width=0.36, label="best binary baseline", color="#888888")
    ax.bar(x + 0.18, best_vals, width=0.36, label="ensemble best", color="tab:blue")
    for i, screen in enumerate(screens):
        ax.text(i, max(base_vals[i], best_vals[i]) + 0.2, f"/{int(screen['best']['wf_windows'])}", ha="center")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("WF windows beating underlying")
    ax.set_title("Phase 7A: walk-forward beat count (Phase 4 splits)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07a_wf_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6))
    trials = frame[frame["config_type"] == "ensemble"]
    for set_name, sub in trials.groupby("window_set"):
        ax.scatter(sub["taxed_mdd"] * 100.0, sub["taxed_cagr"] * 100.0, s=30, alpha=0.7, label=str(set_name))
    base = frame[frame["config_type"] == "binary_baseline"]
    ax.scatter(base["taxed_mdd"] * 100.0, base["taxed_cagr"] * 100.0, s=90, marker="*", color="black", label="binary baselines")
    ax.axvline(MDD_FLOOR * 100.0, color="red", linestyle="--", linewidth=0.9, label="MDD -50% floor")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.set_title("Phase 7A frontier: ensemble grid")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase07a_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def top_rows_table(frame: pd.DataFrame, branch: str, limit: int = 8) -> str:
    sub = frame[(frame["config_type"] == "ensemble") & (frame["branch"] == branch)]
    sub = sub.sort_values(["wf_beats", "taxed_calmar"], ascending=False).head(limit)
    rows = [
        {
            "Base": r["base_name"],
            "Set": r["window_set"],
            "Lag": int(r["lag_days"]),
            "WF": f"{int(r['wf_beats'])}/{int(r['wf_windows'])}",
            "CAGR": fmt_pct(r["taxed_cagr"]),
            "MDD": fmt_pct(r["taxed_mdd"]),
            "Sharpe": fmt_num(r["taxed_sharpe"]),
            "Calmar": fmt_num(r["taxed_calmar"]),
            "Mean f": fmt_num(r["mean_fraction"], 2),
            "Partial days": fmt_pct(r["pct_days_partial"], 1),
            "Turnover/y": fmt_num(r["turnover_per_year"], 2),
        }
        for _, r in sub.iterrows()
    ]
    return md_table(rows, ["Base", "Set", "Lag", "WF", "CAGR", "MDD", "Sharpe", "Calmar", "Mean f", "Partial days", "Turnover/y"])


def screen_table(screens: list[dict[str, object]]) -> str:
    rows = []
    for screen in screens:
        best = screen["best"]
        base = screen["baseline"]
        rows.append(
            {
                "Branch": screen["branch"],
                "Best config": f"{best['base_name']} / {best['window_set']} / lag {int(best['lag_days'])}",
                "WF best vs base": f"{int(best['wf_beats'])}/{int(best['wf_windows'])} vs {int(base['wf_beats'])}/{int(base['wf_windows'])} {'P' if screen['crit_wf'] else 'F'}",
                "CAGR vs headline-1pp": f"{fmt_pct(best['taxed_cagr'])} vs {fmt_pct(screen['headline']['taxed_cagr'])} {'P' if screen['crit_cagr'] else 'F'}",
                "MDD >= -50%": f"{fmt_pct(best['taxed_mdd'])} {'P' if screen['crit_mdd'] else 'F'}",
                "Screen": "SUCCESS" if screen["success"] else "FAIL",
            }
        )
    return md_table(rows, ["Branch", "Best config", "WF best vs base", "CAGR vs headline-1pp", "MDD >= -50%", "Screen"])


def write_report(
    frame: pd.DataFrame,
    screens: list[dict[str, object]],
    plot_rows: list[dict[str, str]],
    sanity: dict[str, float],
) -> None:
    n_success = sum(1 for s in screens if s["success"])
    sanity_text = "; ".join(f"{k}: max abs diff {v:.3g}" for k, v in sanity.items())
    sections = [
        "# Phase 7A - Ensemble Multi-Lookback Fractional Position (DIAGNOSTIC)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "Replaces the binary SMA200 gate with a combined forecast over N SMA windows: the risk-on fraction is the share of member signals on, `f_t = (1/N) sum_w 1[P.shift(1) > SMA_w.shift(1)]`, scaled by the base's binary vol gate `[systematic_trading, p.118-119, p.129-133]`, `[leverage_for_the_long_run, p.14, Table 6]`, `[testing_tuning, p.327-335]`. Weekly cadence, lag convention, risk-off sleeves, ladder and DARF tax unchanged. Hypothesis: averaging over window speeds reduces whipsaw/window-luck and lifts walk-forward consistency, the binding Phase 4 gate.\n\n"
        f"Pre-registered grid: 6 bases x 2 window sets x 6 lags = {N_TRIALS_ADDED} rows. **n_trials ledger: {N_TRIALS_LEDGER_BEFORE} + {N_TRIALS_ADDED} = {N_TRIALS_LEDGER_BEFORE + N_TRIALS_ADDED}.** Baseline rows (binary bases at committed lags, recomputed) are comparisons, not trials.\n\n"
        f"**Built-in sanity (degenerate set `{{200}}` vs binary base):** {sanity_text}.\n\n"
        "## Executive Conclusion\n\n"
        f"Pre-registered screen (best trial row per branch by WF beats, tie-break Calmar): **{n_success}/{len(screens)} branches SUCCESS**. Criteria: WF beats strictly above the best binary baseline AND after-tax CAGR >= headline - 1pp AND MDD >= -50%. A SUCCESS feeds the Phase 7F composition slot only - it is NOT a gate pass (the actual G3 level would need "
        + ", ".join(f"{b} >= {GATE_LEVELS[b]}" for b in GATE_LEVELS)
        + ") and NOT a promotion `[advances_fin_ml, p.208-211]`.\n\n",
    ]
    sections.append("## Screen Result\n\n" + screen_table(screens))
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    for screen in screens:
        base = screen["baseline"]
        sections.append(
            f"## Top {screen['branch']} Rows (by WF beats, then Calmar)\n\n"
            + top_rows_table(frame, str(screen["branch"]))
            + f"\nBest binary baseline ({base['base_name']}): WF {int(base['wf_beats'])}/{int(base['wf_windows'])}, CAGR {fmt_pct(base['taxed_cagr'])}, MDD {fmt_pct(base['taxed_mdd'])}, Sharpe {fmt_num(base['taxed_sharpe'])}, Calmar {fmt_num(base['taxed_calmar'])}.\n"
        )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        + "".join(
            f"| {s['branch']}: fractional ensemble beats binary on WF consistency? | {'Yes' if s['crit_wf'] else 'No'} ({int(s['best']['wf_beats'])}/{int(s['best']['wf_windows'])} vs {int(s['baseline']['wf_beats'])}/{int(s['baseline']['wf_windows'])}). |\n"
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
    best_fracs: dict[str, pd.Series] = {}
    headline_returns: dict[str, pd.Series] = {}
    sanity: dict[str, float] = {}

    contexts = {name: phase04.build_context(branch) for name, branch in phase04.BRANCHES.items()}
    for branch_key, context in contexts.items():
        fraction_by_set = {
            name: ensemble_fraction(context, windows) for name, windows in WINDOW_SETS.items()
        }
        branch_bases = [b for b in phase04.BASE_SPECS if b["branch"] == branch_key]
        headline_base = next(b for b in branch_bases if b["name"] == HEADLINE_BASES[branch_key])
        sanity[branch_key] = sanity_degenerate_set(context, headline_base)

        for base in branch_bases:
            baseline_row, baseline_taxed = evaluate_baseline(context, base)
            rows.append(baseline_row)
            if base["name"] == HEADLINE_BASES[branch_key]:
                headline_returns[branch_key] = baseline_taxed
            for set_name in WINDOW_SETS:
                for lag in LAGS:
                    row, taxed = evaluate_row(context, base, set_name, lag, fraction_by_set)
                    rows.append(row)
                    key = (int(row["wf_beats"]), float(row["taxed_calmar"]))
                    if branch_key not in best_key or key > best_key[branch_key]:
                        best_key[branch_key] = key
                        best_returns[branch_key] = taxed
                        vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == base["vol"])
                        gate = phase04.vol_gate(context, vol_spec).astype(float)
                        label = f"{branch_key} {base['name']} {set_name} lag {lag}"
                        best_fracs[label] = fraction_by_set[set_name] * gate
        print(f"  {branch_key}: grid done (sanity max abs diff {sanity[branch_key]:.3g})")

    frame = pd.DataFrame(rows)
    frame.to_csv(CSV, index=False)
    screens = [screen_branch(frame, branch_key) for branch_key in phase04.BRANCHES]
    plot_rows = []
    frac_plot = plot_fraction_series(best_fracs)
    plot_rows.append({"Plot": "Best-row ensemble fraction", "File": f"[plots/{frac_plot.name}](plots/{frac_plot.name})"})
    eq = plot_equity_dd(best_returns, headline_returns)
    plot_rows.append({"Plot": "Equity/drawdown vs binary headline", "File": f"[plots/{eq.name}](plots/{eq.name})"})
    wf = plot_wf_comparison(screens)
    plot_rows.append({"Plot": "WF beat-count comparison", "File": f"[plots/{wf.name}](plots/{wf.name})"})
    frontier = plot_frontier(frame)
    plot_rows.append({"Plot": "CAGR x MDD frontier", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    write_report(frame, screens, plot_rows, sanity)

    for screen in screens:
        best = screen["best"]
        base = screen["baseline"]
        print(
            f"Phase 7A {screen['branch']}: best {best['base_name']} {best['window_set']} lag {int(best['lag_days'])} "
            f"WF {int(best['wf_beats'])}/{int(best['wf_windows'])} (base {int(base['wf_beats'])}/{int(base['wf_windows'])}) "
            f"CAGR {best['taxed_cagr']:.2%} MDD {best['taxed_mdd']:.2%} "
            f"screen={'SUCCESS' if screen['success'] else 'FAIL'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
