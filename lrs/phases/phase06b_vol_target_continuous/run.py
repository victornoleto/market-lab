"""Phase 6B - continuous vol-targeted sizing on the headline LRS bases (DIAGNOSTIC).

Research-only. Replaces Phase 2's binary realized-vol gate with continuous
exposure sizing `L_t = clip(sigma_target / RV_t, 0, L_max)` on the risk-on
sleeve, quantized to the 0.25 ladder grid with position inertia
`[systematic_trading, p.137-148]`, `[systematic_trading, p.159]`,
`[systematic_trading, p.174]`. Hypothesis: smooth sizing improves walk-forward
consistency (the binding Phase 4 gate) without giving up headline CAGR
`[leverage_for_the_long_run, p.4-7]`. Pre-registered grid: 72 rows
(2 branches x 3 sigma_targets x 2 RV windows x 6 lags); +72 to the n_trials
ledger (3876 -> 3948). No deployment, no paper-trade label, no mandate change.
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
    fmt_pp,
    md_table,
    metrics_from_returns,
    simulate_weight_frame,
)
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase06c_wf_forensics.run import total_return  # noqa: E402
from market_lab.backtest.validation import walk_forward_splits  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase06b_vol_target_continuous.csv"

LADDER_STEP = 0.25
SIGMA_TARGETS = [0.20, 0.30, 0.40]
RV_WINDOWS = [21, 63]
LAGS = list(range(6))
N_TRIALS_ADDED = len(SIGMA_TARGETS) * len(RV_WINDOWS) * len(LAGS) * 2  # 72
MDD_FLOOR = -0.50
CAGR_TOLERANCE_PP = 0.01

# Headline geometries fixed from Phase 2/4; the binary vol gate is replaced by
# continuous sizing in the grid rows and kept only in the baseline rows.
BRANCH_SPECS: list[dict[str, object]] = [
    {
        "branch": "SPY",
        "l_max": 2.00,
        "risk_off": "50 ZROZ / 25 GLD / 25 CASH",
        "baseline_name": "spy_top",
        "baseline_vol": "RV21 <= 30%",
        "baseline_lag": 3,
    },
    {
        "branch": "QQQ",
        "l_max": 1.75,
        "risk_off": "40 ZROZ / 40 GLD / 20 IEF",
        "baseline_name": "qqq_top",
        "baseline_vol": "RV63 <= 40%",
        "baseline_lag": 0,
    },
]


def continuous_leverage_series(
    underlying_returns: pd.Series,
    rv_window: int,
    sigma_target: float,
    l_max: float,
    step: float = LADDER_STEP,
) -> pd.Series:
    """Vol-target leverage `clip(sigma_target / RV_t, 0, l_max)` with inertia.

    RV uses the Phase 2 estimator (`rolling.std(ddof=0).shift(1) * sqrt(252)`)
    so today's leverage only uses information known at the previous close
    `[testing_tuning, p.327-335]`. Holdings move only when the raw scalar
    deviates from the held level by >= ``step``; the new held level is the raw
    value rounded to the ladder grid `[systematic_trading, p.159]`,
    `[systematic_trading, p.174]`.
    """
    rv = underlying_returns.rolling(rv_window).std(ddof=0).shift(1) * np.sqrt(252.0)
    raw = (sigma_target / rv).clip(lower=0.0, upper=l_max)
    raw = raw.where(np.isfinite(raw), 0.0).fillna(0.0)
    held = 0.0
    out: list[float] = []
    for value in raw.to_numpy(dtype=float):
        if abs(value - held) >= step:
            held = float(min(l_max, max(0.0, round(value / step) * step)))
        out.append(held)
    return pd.Series(out, index=raw.index, name="leverage")


def ladder_weights_any(branch: dict[str, str], target_leverage: float) -> dict[str, float]:
    """Ladder weights for any leverage in [0, 3]; cash fills the gap below 1x.

    For ``L >= 1`` this delegates to the Phase 4 ladder (underlying/2x/3x mix).
    For ``0 <= L < 1`` the un-invested remainder of the vol-target scalar sits
    in cash `[systematic_trading, p.137-148]`.
    """
    if target_leverage < 0.0 or target_leverage > 3.0:
        raise ValueError(f"target leverage out of range: {target_leverage}")
    if target_leverage >= 1.0:
        return phase04.target_leverage_weights(branch, target_leverage)
    return clean_weights({branch["underlying"]: target_leverage, "CASHX": 1.0 - target_leverage})


def desired_targets_continuous(
    context: "phase04.BranchContext",
    leverage: pd.Series,
    risk_off_weights: dict[str, float],
) -> pd.DataFrame:
    """Daily desired weights: ladder(L_t) on risk-on days, risk-off sleeve else."""
    branch = context.branch
    index = context.returns.index
    signal = context.sma_signal.reindex(index).fillna(False).to_numpy(dtype=bool)
    lev = leverage.reindex(index).fillna(0.0).to_numpy(dtype=float)
    assets = sorted(
        {branch["underlying"], branch["lev2"], branch["lev3"]} | set(risk_off_weights) | {"CASHX"}
    )
    frame = pd.DataFrame(0.0, index=index, columns=assets)
    for level in np.unique(lev):
        weights = ladder_weights_any(branch, float(level))
        mask = signal & np.isclose(lev, level)
        for asset, weight in weights.items():
            frame.loc[mask, asset] = weight
    off_mask = ~signal
    for asset, weight in risk_off_weights.items():
        frame.loc[off_mask, asset] = weight
    return frame


def wf_beats(strategy: pd.Series, underlying: pd.Series) -> tuple[int, int]:
    """Walk-forward beat count on the exact Phase 4 split geometry."""
    aligned = pd.concat({"s": strategy, "b": underlying}, axis=1).dropna()
    s = aligned["s"]
    b = aligned["b"]
    beats = 0
    n = 0
    for _train, test in walk_forward_splits(
        len(aligned), is_size=phase04.WF_IS_SIZE, oos_size=phase04.WF_OOS_SIZE, step=phase04.WF_STEP
    ):
        seg = slice(test.start, test.stop)
        n += 1
        if total_return(s.iloc[seg]) - total_return(b.iloc[seg]) > 0.0:
            beats += 1
    return beats, n


def evaluate_row(
    context: "phase04.BranchContext",
    spec: dict[str, object],
    sigma_target: float,
    rv_window: int,
    lag: int,
    risk_off_weights: dict[str, float],
) -> tuple[dict[str, object], pd.Series, pd.Series]:
    leverage = continuous_leverage_series(
        context.returns[context.branch["underlying"]], rv_window, sigma_target, float(spec["l_max"])
    )
    desired = desired_targets_continuous(context, leverage, risk_off_weights)
    weights, weight_summary = build_weekly_lagged_weights(desired, lag_days=lag)
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    metrics = metrics_from_returns(taxed)
    beats, n_windows = wf_beats(taxed, context.underlying_taxed)
    risk_on = context.sma_signal.reindex(context.returns.index).fillna(False)
    lev_on = leverage[risk_on]
    row: dict[str, object] = {
        "config_type": "continuous",
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


def evaluate_baseline(context: "phase04.BranchContext", spec: dict[str, object]) -> tuple[dict[str, object], pd.Series]:
    """Binary headline base recomputed in-run for exact comparability (not a trial)."""
    risk_off = next(r for r in phase04.RISK_OFF_SPECS if r["name"] == spec["risk_off"])
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == spec["baseline_vol"])
    risk_off_weights = clean_weights(dict(risk_off["weights"]))  # type: ignore[arg-type]
    taxed = phase04.simulate_returns(
        context, float(spec["l_max"]), risk_off_weights, vol_spec, int(spec["baseline_lag"])
    )
    metrics = metrics_from_returns(taxed)
    beats, n_windows = wf_beats(taxed, context.underlying_taxed)
    row: dict[str, object] = {
        "config_type": "binary_baseline",
        "branch": spec["branch"],
        "sigma_target": float("nan"),
        "rv_window": int(vol_spec["window"]),
        "lag_days": int(spec["baseline_lag"]),
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
        "mean_leverage_risk_on": float(spec["l_max"]),
        "pct_risk_on_at_lmax": float("nan"),
        "state_changes": float("nan"),
        "turnover_per_year": float("nan"),
        "total_tax_paid_pct_initial": float("nan"),
    }
    return row, taxed


def screen_branch(frame: pd.DataFrame, branch: str) -> dict[str, object]:
    """Pre-registered screen on the branch best row (WF beats, tie-break Calmar)."""
    cont = frame[(frame["config_type"] == "continuous") & (frame["branch"] == branch)]
    base = frame[(frame["config_type"] == "binary_baseline") & (frame["branch"] == branch)].iloc[0]
    best = cont.sort_values(["wf_beats", "taxed_calmar"], ascending=False).iloc[0]
    crit_wf = bool(best["wf_beats"] > base["wf_beats"])
    crit_cagr = bool(best["taxed_cagr"] >= base["taxed_cagr"] - CAGR_TOLERANCE_PP)
    crit_mdd = bool(best["taxed_mdd"] >= MDD_FLOOR)
    return {
        "branch": branch,
        "best": best,
        "baseline": base,
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
        ax.plot(lev.index, lev.to_numpy(dtype=float), linewidth=0.7, color="tab:blue")
        ax.set_title(f"{label}: continuous ladder leverage L_t")
        ax.set_ylabel("L_t")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase06b_leverage_series.png"
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
            {"continuous best": best_returns[branch], "binary baseline": baseline_returns[branch]},
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
    out = PLOTS / "phase06b_equity_dd.png"
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
    ax.bar(x - 0.18, base_vals, width=0.36, label="binary baseline", color="#888888")
    ax.bar(x + 0.18, best_vals, width=0.36, label="continuous best", color="tab:blue")
    for i, screen in enumerate(screens):
        ax.text(i, max(base_vals[i], best_vals[i]) + 0.2, f"/{int(screen['best']['wf_windows'])}", ha="center")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("WF windows beating underlying")
    ax.set_title("Phase 6B: walk-forward beat count (Phase 4 splits)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase06b_wf_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6))
    cont = frame[frame["config_type"] == "continuous"]
    for sigma, sub in cont.groupby("sigma_target"):
        ax.scatter(sub["taxed_mdd"] * 100.0, sub["taxed_cagr"] * 100.0, s=30, alpha=0.7, label=f"sigma {float(sigma):.0%}")
    base = frame[frame["config_type"] == "binary_baseline"]
    ax.scatter(base["taxed_mdd"] * 100.0, base["taxed_cagr"] * 100.0, s=90, marker="*", color="black", label="binary baselines")
    ax.axvline(MDD_FLOOR * 100.0, color="red", linestyle="--", linewidth=0.9, label="MDD -50% floor")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.set_title("Phase 6B frontier: continuous vol-targeting grid")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase06b_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def top_rows_table(frame: pd.DataFrame, branch: str, limit: int = 8) -> str:
    sub = frame[(frame["config_type"] == "continuous") & (frame["branch"] == branch)]
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
        base = screen["baseline"]
        rows.append(
            {
                "Branch": screen["branch"],
                "Best config": f"sigma {fmt_pct(best['sigma_target'], 0)} / RV{int(best['rv_window'])} / lag {int(best['lag_days'])}",
                "WF best vs base": f"{int(best['wf_beats'])}/{int(best['wf_windows'])} vs {int(base['wf_beats'])}/{int(base['wf_windows'])} {'P' if screen['crit_wf'] else 'F'}",
                "CAGR best vs base": f"{fmt_pct(best['taxed_cagr'])} vs {fmt_pct(base['taxed_cagr'])} {'P' if screen['crit_cagr'] else 'F'}",
                "MDD >= -50%": f"{fmt_pct(best['taxed_mdd'])} {'P' if screen['crit_mdd'] else 'F'}",
                "Screen": "SUCCESS" if screen["success"] else "FAIL",
            }
        )
    return md_table(rows, ["Branch", "Best config", "WF best vs base", "CAGR best vs base", "MDD >= -50%", "Screen"])


def write_report(frame: pd.DataFrame, screens: list[dict[str, object]], plot_rows: list[dict[str, str]]) -> None:
    n_success = sum(1 for s in screens if s["success"])
    sections = [
        "# Phase 6B - Continuous Vol-Targeting (DIAGNOSTIC)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "Replaces the Phase 2 binary realized-vol gate with continuous vol-target sizing `L_t = clip(sigma_target / RV_t, 0, L_max)` on the risk-on sleeve, quantized to the 0.25 ladder grid with position inertia `[systematic_trading, p.137-148]`, `[systematic_trading, p.159]`, `[systematic_trading, p.174]`. SMA200 weekly gate, risk-off sleeves, lag convention and DARF tax unchanged. Hypothesis: smooth sizing improves walk-forward consistency, the binding Phase 4 gate `[leverage_for_the_long_run, p.4-7]`, `[testing_tuning, p.327-335]`.\n\n"
        f"Pre-registered grid: 2 branches x 3 sigma_targets x 2 RV windows x 6 lags = {N_TRIALS_ADDED} rows. **n_trials ledger: 3876 + {N_TRIALS_ADDED} = {3876 + N_TRIALS_ADDED}.** Baseline rows (binary headline bases, recomputed) are comparisons, not trials.\n\n"
        "## Executive Conclusion\n\n"
        f"Pre-registered screen (best row per branch by WF beats, tie-break Calmar): **{n_success}/{len(screens)} branches SUCCESS**. Criteria: WF beats strictly above the binary baseline AND after-tax CAGR >= headline - 1pp AND MDD >= -50%. A SUCCESS is a diagnostic lead for Phase 6A's satellite set only - it is NOT a gate pass (the actual G3 gate would need >=13/17 SPY, >=9/11 QQQ) and NOT a promotion `[advances_fin_ml, p.208-211]`.\n\n",
    ]
    sections.append("## Screen Result\n\n" + screen_table(screens))
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    for screen in screens:
        base = screen["baseline"]
        sections.append(
            f"## Top {screen['branch']} Rows (by WF beats, then Calmar)\n\n"
            + top_rows_table(frame, str(screen["branch"]))
            + f"\nBinary baseline: WF {int(base['wf_beats'])}/{int(base['wf_windows'])}, CAGR {fmt_pct(base['taxed_cagr'])}, MDD {fmt_pct(base['taxed_mdd'])}, Sharpe {fmt_num(base['taxed_sharpe'])}, Calmar {fmt_num(base['taxed_calmar'])}.\n"
        )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        + "".join(
            f"| {s['branch']}: continuous sizing beats binary on WF consistency? | {'Yes' if s['crit_wf'] else 'No'} ({int(s['best']['wf_beats'])}/{int(s['best']['wf_windows'])} vs {int(s['baseline']['wf_beats'])}/{int(s['baseline']['wf_windows'])}). |\n"
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

    for spec in BRANCH_SPECS:
        branch_key = str(spec["branch"])
        context = phase04.build_context(phase04.BRANCHES[branch_key])
        risk_off = next(r for r in phase04.RISK_OFF_SPECS if r["name"] == spec["risk_off"])
        risk_off_weights = clean_weights(dict(risk_off["weights"]))  # type: ignore[arg-type]

        baseline_row, baseline_taxed = evaluate_baseline(context, spec)
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
    screens = [screen_branch(frame, str(spec["branch"])) for spec in BRANCH_SPECS]
    lev_plot = plot_leverage_series(best_levs)
    plot_rows = [
        {"Plot": "Best-row leverage series", "File": f"[plots/{lev_plot.name}](plots/{lev_plot.name})"},
    ]
    eq = plot_equity_dd(best_returns, baseline_returns)
    plot_rows.append({"Plot": "Equity/drawdown vs binary baseline", "File": f"[plots/{eq.name}](plots/{eq.name})"})
    wf = plot_wf_comparison(screens)
    plot_rows.append({"Plot": "WF beat-count comparison", "File": f"[plots/{wf.name}](plots/{wf.name})"})
    frontier = plot_frontier(frame)
    plot_rows.append({"Plot": "CAGR x MDD frontier", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    write_report(frame, screens, plot_rows)

    for screen in screens:
        best = screen["best"]
        base = screen["baseline"]
        print(
            f"Phase 6B {screen['branch']}: best sigma {best['sigma_target']:.0%} RV{int(best['rv_window'])} "
            f"lag {int(best['lag_days'])} WF {int(best['wf_beats'])}/{int(best['wf_windows'])} "
            f"(base {int(base['wf_beats'])}/{int(base['wf_windows'])}) CAGR {best['taxed_cagr']:.2%} "
            f"MDD {best['taxed_mdd']:.2%} screen={'SUCCESS' if screen['success'] else 'FAIL'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
