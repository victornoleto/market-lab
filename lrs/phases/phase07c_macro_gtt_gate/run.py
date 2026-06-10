"""Phase 7C - macro Growth-Trend-Timing gate via UNRATE (DIAGNOSTIC).

Research-only. Applies the trend rule only when the macro regime signals
recession risk (`UNRATE > SMA12m(UNRATE)`, publication-lagged); in expansions
the portfolio holds the target-leverage sleeve unconditionally. CITATION
EXCEPTION (user-approved 2026-06-09): the specific rule is from the
Philosophical Economics "Growth-Trend Timing" essay (blog, no book source);
the family anchors on the paper's regime evidence - S&P 500 below its 200dma
68.2% of recession time vs 19.4% of expansion time
`[leverage_for_the_long_run, p.9]`. Honest alignment: 25-trading-day publish
lag from the FRED month stamp `[advances_fin_ml, p.31-34]`. Pre-registered
grid: 72 rows (6 bases x 2 override scopes x 6 lags); +72 to the n_trials
ledger (4149 -> 4221). No deployment, no paper-trade label, no mandate change.
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
from lrs.phases.phase06b_vol_target_continuous.run import wf_beats  # noqa: E402
from market_lab.backtest.data.macro_data_loader import (  # noqa: E402
    UNRATE_LAG_TD,
    load_unrate_monthly,
    resample_to_daily_with_lag,
)


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase07c_macro_gtt_gate.csv"

UNRATE_SMA_MONTHS = 12
SCOPES = ["trend_only", "trend_and_vol"]
LAGS = list(range(6))
N_TRIALS_ADDED = len(phase04.BASE_SPECS) * len(SCOPES) * len(LAGS)  # 72
N_TRIALS_LEDGER_BEFORE = 4149
MDD_FLOOR = -0.50
CAGR_TOLERANCE_PP = 0.01
HEADLINE_BASES = {"SPY": "spy_top", "QQQ": "qqq_top"}


def macro_risk_series(index: pd.DatetimeIndex) -> pd.Series:
    """Daily recession-risk regime: UNRATE above its 12m SMA, publication-lagged.

    Warmup (SMA12 NaN) and any unaligned day default to ``True`` so the
    fallback is always the FULL base rule, never unconditional leverage.
    """
    unrate = load_unrate_monthly()
    sma12 = unrate.rolling(UNRATE_SMA_MONTHS).mean()
    risk_monthly = (unrate > sma12).astype(float)
    risk_monthly[sma12.isna()] = 1.0
    daily = resample_to_daily_with_lag(risk_monthly, index, UNRATE_LAG_TD)
    return (daily.fillna(1.0) > 0.5)


def gtt_signal(
    context: "phase04.BranchContext",
    vol_spec: dict[str, object],
    macro_risk: pd.Series,
    scope: str,
) -> pd.Series:
    """Composite signal: base rule under macro risk, override in expansions."""
    index = context.returns.index
    base = (context.sma_signal & phase04.vol_gate(context, vol_spec)).reindex(index).fillna(False)
    macro = macro_risk.reindex(index).fillna(True)
    if scope == "trend_only":
        override = phase04.vol_gate(context, vol_spec).reindex(index).fillna(False)
    elif scope == "trend_and_vol":
        override = pd.Series(True, index=index)
    else:
        raise ValueError(f"unknown scope: {scope}")
    return pd.Series(np.where(macro, base, override), index=index).astype(bool)


def simulate_with_signal(
    context: "phase04.BranchContext",
    signal: pd.Series,
    target_leverage: float,
    risk_off_weights: dict[str, float],
    lag_days: int,
) -> tuple[pd.Series, dict[str, float], dict[str, float]]:
    """After-tax daily returns for an arbitrary boolean risk-on signal."""
    risk_on = phase04.target_leverage_weights(context.branch, target_leverage)
    assets = sorted(set(risk_on) | set(risk_off_weights) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=context.returns.index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on.get(asset, 0.0), risk_off_weights.get(asset, 0.0))
    weights, weight_summary = build_weekly_lagged_weights(
        desired, lag_days=lag_days, risk_on_weights=risk_on
    )
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    return taxed, weight_summary, tax_summary


def evaluate_row(
    context: "phase04.BranchContext",
    base: dict[str, object],
    scope: str,
    lag: int,
    macro_risk: pd.Series,
) -> tuple[dict[str, object], pd.Series]:
    risk_off_weights = clean_weights(
        next(r["weights"] for r in phase04.RISK_OFF_SPECS if r["name"] == base["risk_off"])
    )
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == base["vol"])
    signal = gtt_signal(context, vol_spec, macro_risk, scope)
    taxed, weight_summary, tax_summary = simulate_with_signal(
        context, signal, float(base["target_leverage"]), risk_off_weights, lag
    )
    metrics = metrics_from_returns(taxed)
    beats, n_windows = wf_beats(taxed, context.underlying_taxed)
    macro = macro_risk.reindex(context.returns.index).fillna(True)
    row: dict[str, object] = {
        "config_type": "gtt",
        "branch": base["branch"],
        "base_name": base["name"],
        "scope": scope,
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
        "pct_expansion_days": float((~macro).mean()),
        "pct_risk_on_days": float(signal.mean()),
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
        "scope": "none",
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
        "pct_expansion_days": float("nan"),
        "pct_risk_on_days": float("nan"),
        "state_changes": float("nan"),
        "turnover_per_year": float("nan"),
        "total_tax_paid_pct_initial": float("nan"),
    }
    return row, taxed


def sanity_forced_risk(context: "phase04.BranchContext", base: dict[str, object]) -> float:
    """macro_risk forced True everywhere must reproduce the binary base."""
    lag = phase04.best_lag_for_base(str(base["name"]))
    risk_off_weights = clean_weights(
        next(r["weights"] for r in phase04.RISK_OFF_SPECS if r["name"] == base["risk_off"])
    )
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == base["vol"])
    forced = pd.Series(True, index=context.returns.index)
    signal = gtt_signal(context, vol_spec, forced, "trend_and_vol")
    taxed, _, _ = simulate_with_signal(
        context, signal, float(base["target_leverage"]), risk_off_weights, lag
    )
    reference = phase04.simulate_returns(
        context, float(base["target_leverage"]), risk_off_weights, vol_spec, lag
    )
    aligned = pd.concat({"a": taxed, "b": reference}, axis=1, sort=False).dropna()
    return float((aligned["a"] - aligned["b"]).abs().max())


def screen_branch(frame: pd.DataFrame, branch: str) -> dict[str, object]:
    trials = frame[(frame["config_type"] == "gtt") & (frame["branch"] == branch)]
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


def plot_regime_equity(
    best_returns: dict[str, pd.Series],
    baseline_returns: dict[str, pd.Series],
    macro_risk: pd.Series,
) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    branches = list(best_returns)
    fig, axes = plt.subplots(len(branches), 1, figsize=(13, 4.2 * len(branches)), squeeze=False)
    for ax, branch in zip(axes.ravel(), branches):
        pair = pd.concat(
            {"GTT best": best_returns[branch], "binary headline": baseline_returns[branch]},
            axis=1,
        ).dropna()
        eq = pair.apply(equity_curve)
        eq.plot(ax=ax, logy=True, linewidth=1.0)
        macro = macro_risk.reindex(eq.index).fillna(True).to_numpy(dtype=bool)
        ax.fill_between(
            eq.index, ax.get_ylim()[0], ax.get_ylim()[1], where=macro,
            color="red", alpha=0.08, label="macro risk (UNRATE > SMA12)",
        )
        ax.set_title(f"{branch}: after-tax equity with macro-risk shading")
        ax.grid(True, alpha=0.3)
        ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase07c_regime_equity.png"
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
            {"GTT best": best_returns[branch], "binary headline": baseline_returns[branch]},
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
    out = PLOTS / "phase07c_equity_dd.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_wf_comparison(screens: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = [str(s["branch"]) for s in screens]
    base_vals = [int(s["baseline"]["wf_beats"]) for s in screens]
    best_vals = [int(s["best"]["wf_beats"]) for s in screens]
    x = np.arange(len(labels))
    ax.bar(x - 0.18, base_vals, width=0.36, label="best binary baseline", color="#888888")
    ax.bar(x + 0.18, best_vals, width=0.36, label="GTT best", color="tab:blue")
    for i, screen in enumerate(screens):
        ax.text(i, max(base_vals[i], best_vals[i]) + 0.2, f"/{int(screen['best']['wf_windows'])}", ha="center")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("WF windows beating underlying")
    ax.set_title("Phase 7C: walk-forward beat count (Phase 4 splits)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07c_wf_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6))
    trials = frame[frame["config_type"] == "gtt"]
    for scope, sub in trials.groupby("scope"):
        ax.scatter(sub["taxed_mdd"] * 100.0, sub["taxed_cagr"] * 100.0, s=30, alpha=0.7, label=str(scope))
    base = frame[frame["config_type"] == "binary_baseline"]
    ax.scatter(base["taxed_mdd"] * 100.0, base["taxed_cagr"] * 100.0, s=90, marker="*", color="black", label="binary baselines")
    ax.axvline(MDD_FLOOR * 100.0, color="red", linestyle="--", linewidth=0.9, label="MDD -50% floor")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.set_title("Phase 7C frontier: GTT macro-gate grid")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase07c_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def top_rows_table(frame: pd.DataFrame, branch: str, limit: int = 8) -> str:
    sub = frame[(frame["config_type"] == "gtt") & (frame["branch"] == branch)]
    sub = sub.sort_values(["wf_beats", "taxed_calmar"], ascending=False).head(limit)
    rows = [
        {
            "Base": r["base_name"],
            "Scope": r["scope"],
            "Lag": int(r["lag_days"]),
            "WF": f"{int(r['wf_beats'])}/{int(r['wf_windows'])}",
            "CAGR": fmt_pct(r["taxed_cagr"]),
            "MDD": fmt_pct(r["taxed_mdd"]),
            "Sharpe": fmt_num(r["taxed_sharpe"]),
            "Calmar": fmt_num(r["taxed_calmar"]),
            "Expansion days": fmt_pct(r["pct_expansion_days"], 1),
            "Risk-on days": fmt_pct(r["pct_risk_on_days"], 1),
            "Turnover/y": fmt_num(r["turnover_per_year"], 2),
        }
        for _, r in sub.iterrows()
    ]
    return md_table(rows, ["Base", "Scope", "Lag", "WF", "CAGR", "MDD", "Sharpe", "Calmar", "Expansion days", "Risk-on days", "Turnover/y"])


def screen_table(screens: list[dict[str, object]]) -> str:
    rows = []
    for screen in screens:
        best = screen["best"]
        base = screen["baseline"]
        rows.append(
            {
                "Branch": screen["branch"],
                "Best config": f"{best['base_name']} / {best['scope']} / lag {int(best['lag_days'])}",
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
        "# Phase 7C - Macro Growth-Trend-Timing Gate via UNRATE (DIAGNOSTIC)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "Applies the trend rule only when `UNRATE > SMA12m(UNRATE)` (publication-lagged 25 trading days); in expansions the target-leverage sleeve is held unconditionally (scope `trend_and_vol`) or gated by vol only (scope `trend_only`). **Citation EXCEPTION approved by the user (2026-06-09):** the rule is from the Philosophical Economics \"Growth-Trend Timing\" essay; the family anchors on the S&P-below-200dma recession/expansion asymmetry (68.2% vs 19.4%) `[leverage_for_the_long_run, p.9]`, honest alignment per `[advances_fin_ml, p.31-34]`. Vintage caveat: FRED serves revised UNRATE data (ALFRED point-in-time check = future work).\n\n"
        f"Pre-registered grid: 6 bases x 2 scopes x 6 lags = {N_TRIALS_ADDED} rows. **n_trials ledger: {N_TRIALS_LEDGER_BEFORE} + {N_TRIALS_ADDED} = {N_TRIALS_LEDGER_BEFORE + N_TRIALS_ADDED}.** Baseline rows are comparisons, not trials.\n\n"
        f"**Built-in sanity (macro_risk forced True vs binary base):** {sanity_text}.\n\n"
        "## Executive Conclusion\n\n"
        f"Pre-registered screen (best trial row per branch by WF beats, tie-break Calmar): **{n_success}/{len(screens)} branches SUCCESS**. Criteria: WF beats strictly above the best binary baseline AND after-tax CAGR >= headline - 1pp AND MDD >= -50%. A SUCCESS feeds the Phase 7F composition slot only - NOT a gate pass, NOT a promotion `[advances_fin_ml, p.208-211]`.\n\n",
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
            f"| {s['branch']}: GTT macro gate beats binary on WF consistency? | {'Yes' if s['crit_wf'] else 'No'} ({int(s['best']['wf_beats'])}/{int(s['best']['wf_windows'])} vs {int(s['baseline']['wf_beats'])}/{int(s['baseline']['wf_windows'])}). |\n"
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
    headline_returns: dict[str, pd.Series] = {}
    sanity: dict[str, float] = {}
    macro_for_plot: pd.Series | None = None

    contexts = {name: phase04.build_context(branch) for name, branch in phase04.BRANCHES.items()}
    for branch_key, context in contexts.items():
        macro_risk = macro_risk_series(pd.DatetimeIndex(context.returns.index))
        if macro_for_plot is None:
            macro_for_plot = macro_risk
        branch_bases = [b for b in phase04.BASE_SPECS if b["branch"] == branch_key]
        headline_base = next(b for b in branch_bases if b["name"] == HEADLINE_BASES[branch_key])
        sanity[branch_key] = sanity_forced_risk(context, headline_base)

        for base in branch_bases:
            baseline_row, baseline_taxed = evaluate_baseline(context, base)
            rows.append(baseline_row)
            if base["name"] == HEADLINE_BASES[branch_key]:
                headline_returns[branch_key] = baseline_taxed
            for scope in SCOPES:
                for lag in LAGS:
                    row, taxed = evaluate_row(context, base, scope, lag, macro_risk)
                    rows.append(row)
                    key = (int(row["wf_beats"]), float(row["taxed_calmar"]))
                    if branch_key not in best_key or key > best_key[branch_key]:
                        best_key[branch_key] = key
                        best_returns[branch_key] = taxed
        print(f"  {branch_key}: grid done (sanity max abs diff {sanity[branch_key]:.3g})")

    frame = pd.DataFrame(rows)
    frame.to_csv(CSV, index=False)
    screens = [screen_branch(frame, branch_key) for branch_key in phase04.BRANCHES]
    plot_rows = []
    assert macro_for_plot is not None
    regime = plot_regime_equity(best_returns, headline_returns, macro_for_plot)
    plot_rows.append({"Plot": "Equity with macro-risk shading", "File": f"[plots/{regime.name}](plots/{regime.name})"})
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
            f"Phase 7C {screen['branch']}: best {best['base_name']} {best['scope']} lag {int(best['lag_days'])} "
            f"WF {int(best['wf_beats'])}/{int(best['wf_windows'])} (base {int(base['wf_beats'])}/{int(base['wf_windows'])}) "
            f"CAGR {best['taxed_cagr']:.2%} MDD {best['taxed_mdd']:.2%} "
            f"screen={'SUCCESS' if screen['success'] else 'FAIL'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
