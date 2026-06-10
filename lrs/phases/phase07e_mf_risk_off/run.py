"""Phase 7E - managed-futures risk-off sleeve (DIAGNOSTIC, low-power).

Research-only. Swaps part of the headline bond/gold risk-off sleeve for
managed-futures trend proxies (DBMFSIM / KMLMSIM from the RSC sleeve matrix,
read-only): the MLM-style trend-following risk premium as crisis
diversification `[evidence_based_ta, p.380-384, p.398]`, `[risk_parity,
p.80-81]`. DBMFSIM starts 2000 so all rows (controls included) run on the
2000+ window with only ~6 WF windows - declared low-power. Pre-registered
grid: 60 rows (2 branches x 5 sleeves x 6 lags); +60 to the n_trials ledger
(4293 -> 4353). No deployment, no paper-trade label, no mandate change.
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
)
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase06b_vol_target_continuous.run import wf_beats  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase07e_mf_risk_off.csv"
REMOTE_PRICES = (
    REPO_ROOT / "studies" / "return_stacked_core" / "us_core" / "series" / "remote_prices.parquet"
)

SMA_WINDOW = 200
LAGS = list(range(6))
N_TRIALS_LEDGER_BEFORE = 4293
MDD_FLOOR = -0.50

BRANCH_SPECS: list[dict[str, object]] = [
    {
        "branch": "SPY",
        "target_leverage": 2.00,
        "risk_off_name": "50 ZROZ / 25 GLD / 25 CASH",
        "vol": "RV21 <= 30%",
        "headline_lag": 3,
    },
    {
        "branch": "QQQ",
        "target_leverage": 1.75,
        "risk_off_name": "40 ZROZ / 40 GLD / 20 IEF",
        "vol": "RV63 <= 40%",
        "headline_lag": 0,
    },
]


def sleeve_specs(base_weights: dict[str, float]) -> list[dict[str, object]]:
    """The 5 pre-registered risk-off sleeves for a branch headline base."""
    mf_blend = {"DBMFSIM": 0.70, "KMLMSIM": 0.30}
    half_base = {asset: 0.5 * weight for asset, weight in base_weights.items()}
    return [
        {"name": "control", "weights": dict(base_weights)},
        {"name": "100% DBMF", "weights": {"DBMFSIM": 1.0}},
        {"name": "50 base / 50 DBMF", "weights": {**half_base, "DBMFSIM": half_base.get("DBMFSIM", 0.0) + 0.5}},
        {"name": "70 DBMF / 30 KMLM", "weights": dict(mf_blend)},
        {
            "name": "50 base / 50 MF-blend",
            "weights": {**half_base, "DBMFSIM": half_base.get("DBMFSIM", 0.0) + 0.35, "KMLMSIM": 0.15},
        },
    ]


def build_branch_data(branch_key: str) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Window-aligned prices/returns incl. MF proxies, SMA signal, taxed underlying."""
    branch = phase04.BRANCHES[branch_key]
    prices = load_price_frame(phase04.branch_assets(branch))
    remote = pd.read_parquet(REMOTE_PRICES)[["DBMFSIM", "KMLMSIM"]].astype(float)
    remote.index = pd.DatetimeIndex(remote.index).tz_localize(None)
    merged = prices.join(remote, how="inner").dropna()
    returns = merged.pct_change().dropna()
    merged = merged.reindex(returns.index)
    sma_signal = (
        build_sma_signal(merged[branch["underlying"]], SMA_WINDOW)
        .reindex(returns.index)
        .fillna(False)
    )
    underlying_frame = constant_weight_frame(returns.index, {branch["underlying"]: 1.0})
    underlying_taxed, _ = simulate_weight_frame(returns, underlying_frame, taxable=True)
    return branch, merged, returns, sma_signal, underlying_taxed


def vol_gate_series(returns: pd.DataFrame, underlying: str, vol_name: str) -> pd.Series:
    spec = next(v for v in phase04.VOL_SPECS if v["name"] == vol_name)
    window = int(spec["window"])
    threshold = float(spec["threshold"])
    rv = returns[underlying].rolling(window).std(ddof=0).shift(1) * np.sqrt(252.0)
    return (rv <= threshold).reindex(returns.index).fillna(False)


def simulate_sleeve(
    branch: dict[str, str],
    returns: pd.DataFrame,
    signal: pd.Series,
    target_leverage: float,
    risk_off_weights: dict[str, float],
    lag: int,
) -> tuple[pd.Series, dict[str, float]]:
    risk_on = phase04.target_leverage_weights(branch, target_leverage)
    assets = sorted(set(risk_on) | set(risk_off_weights) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=returns.index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on.get(asset, 0.0), risk_off_weights.get(asset, 0.0))
    weights, _ = build_weekly_lagged_weights(desired, lag_days=lag, risk_on_weights=risk_on)
    taxed, tax_summary = simulate_weight_frame(returns, weights, taxable=True)
    return taxed, tax_summary


def screen_branch(frame: pd.DataFrame, branch_key: str) -> dict[str, object]:
    sub = frame[frame["branch"] == branch_key]
    controls = sub[sub["sleeve"] == "control"]
    trials = sub[sub["sleeve"] != "control"]
    control_best = controls.sort_values(["wf_beats", "taxed_calmar"], ascending=False).iloc[0]
    best = trials.sort_values(["wf_beats", "taxed_calmar"], ascending=False).iloc[0]
    crit_wf = bool(best["wf_beats"] > control_best["wf_beats"])
    crit_mdd_rel = bool(best["taxed_mdd"] >= control_best["taxed_mdd"])
    crit_mdd_floor = bool(best["taxed_mdd"] >= MDD_FLOOR)
    return {
        "branch": branch_key,
        "best": best,
        "control": control_best,
        "crit_wf": crit_wf,
        "crit_mdd_rel": crit_mdd_rel,
        "crit_mdd_floor": crit_mdd_floor,
        "success": bool(crit_wf and crit_mdd_rel and crit_mdd_floor),
    }


# --------------------------------------------------------------------------- plots


def plot_equity_dd(best_returns: dict[str, pd.Series], control_returns: dict[str, pd.Series]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    branches = list(best_returns)
    fig, axes = plt.subplots(2, len(branches), figsize=(7.5 * len(branches), 8.5), squeeze=False)
    for col, branch in enumerate(branches):
        pair = pd.concat(
            {"MF sleeve best": best_returns[branch], "control sleeve": control_returns[branch]},
            axis=1,
        ).dropna()
        eq = pair.apply(equity_curve)
        eq.plot(ax=axes[0][col], logy=True, linewidth=1.1)
        axes[0][col].set_title(f"{branch}: after-tax equity (2000+)")
        axes[0][col].grid(True, alpha=0.3)
        dd = eq / eq.cummax() - 1.0
        (dd * 100.0).plot(ax=axes[1][col], linewidth=1.0)
        axes[1][col].set_title(f"{branch}: drawdown (%)")
        axes[1][col].grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07e_equity_dd.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_wf_comparison(screens: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = [str(s["branch"]) for s in screens]
    control_vals = [int(s["control"]["wf_beats"]) for s in screens]
    best_vals = [int(s["best"]["wf_beats"]) for s in screens]
    x = np.arange(len(labels))
    ax.bar(x - 0.18, control_vals, width=0.36, label="control sleeve best", color="#888888")
    ax.bar(x + 0.18, best_vals, width=0.36, label="MF sleeve best", color="tab:green")
    for i, screen in enumerate(screens):
        ax.text(i, max(control_vals[i], best_vals[i]) + 0.1, f"/{int(screen['best']['wf_windows'])}", ha="center")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("WF windows beating underlying (2000+)")
    ax.set_title("Phase 7E: walk-forward beat count (~6 windows, low power)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase07e_wf_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6))
    for sleeve, sub in frame.groupby("sleeve"):
        marker = "*" if sleeve == "control" else "o"
        size = 90 if sleeve == "control" else 30
        ax.scatter(sub["taxed_mdd"] * 100.0, sub["taxed_cagr"] * 100.0, s=size, marker=marker, alpha=0.75, label=str(sleeve))
    ax.axvline(MDD_FLOOR * 100.0, color="red", linestyle="--", linewidth=0.9, label="MDD -50% floor")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.set_title("Phase 7E frontier by risk-off sleeve (2000+)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase07e_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def top_rows_table(frame: pd.DataFrame, branch_key: str, limit: int = 8) -> str:
    sub = frame[frame["branch"] == branch_key]
    sub = sub.sort_values(["wf_beats", "taxed_calmar"], ascending=False).head(limit)
    rows = [
        {
            "Sleeve": r["sleeve"],
            "Lag": int(r["lag_days"]),
            "WF": f"{int(r['wf_beats'])}/{int(r['wf_windows'])}",
            "CAGR": fmt_pct(r["taxed_cagr"]),
            "MDD": fmt_pct(r["taxed_mdd"]),
            "Sharpe": fmt_num(r["taxed_sharpe"]),
            "Calmar": fmt_num(r["taxed_calmar"]),
            "Turnover/y": fmt_num(r["turnover_per_year"], 2),
        }
        for _, r in sub.iterrows()
    ]
    return md_table(rows, ["Sleeve", "Lag", "WF", "CAGR", "MDD", "Sharpe", "Calmar", "Turnover/y"])


def screen_table(screens: list[dict[str, object]]) -> str:
    rows = []
    for screen in screens:
        best = screen["best"]
        control = screen["control"]
        rows.append(
            {
                "Branch": screen["branch"],
                "Best MF sleeve": f"{best['sleeve']} / lag {int(best['lag_days'])}",
                "WF vs control": f"{int(best['wf_beats'])}/{int(best['wf_windows'])} vs {int(control['wf_beats'])}/{int(control['wf_windows'])} {'P' if screen['crit_wf'] else 'F'}",
                "MDD vs control": f"{fmt_pct(best['taxed_mdd'])} vs {fmt_pct(control['taxed_mdd'])} {'P' if screen['crit_mdd_rel'] else 'F'}",
                "MDD >= -50%": f"{'P' if screen['crit_mdd_floor'] else 'F'}",
                "Screen": "SUCCESS" if screen["success"] else "FAIL",
            }
        )
    return md_table(rows, ["Branch", "Best MF sleeve", "WF vs control", "MDD vs control", "MDD >= -50%", "Screen"])


def write_report(
    frame: pd.DataFrame,
    screens: list[dict[str, object]],
    plot_rows: list[dict[str, str]],
    sanity: dict[str, float],
    n_trials_added: int,
) -> None:
    n_success = sum(1 for s in screens if s["success"])
    sanity_text = "; ".join(f"{k}: max abs diff {v:.3g}" for k, v in sanity.items())
    sections = [
        "# Phase 7E - Managed-Futures Risk-Off Sleeve (DIAGNOSTIC, LOW-POWER)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "Swaps part of the headline bond/gold risk-off sleeve for managed-futures trend proxies (`DBMFSIM`/`KMLMSIM`, read-only from the RSC sleeve matrix): the MLM-style trend-following risk premium as crisis diversification `[evidence_based_ta, p.380-384, p.398]`, `[risk_parity, p.80-81]`. Risk-on geometry, vol gates, cadence and DARF tax verbatim from the headline bases.\n\n"
        f"Pre-registered grid: 2 branches x 5 sleeves x 6 lags = {n_trials_added} rows. **n_trials ledger: {N_TRIALS_LEDGER_BEFORE} + {n_trials_added} = {N_TRIALS_LEDGER_BEFORE + n_trials_added}.** DECLARED LOW-POWER: DBMFSIM starts 2000-01-03, so every row (controls included) runs on the 2000+ window with only ~6 WF windows; this phase can only yield a weak lead or weak negative.\n\n"
        f"**Built-in sanity (control sleeve at headline lag vs direct rerun on the same window):** {sanity_text}.\n\n"
        "## Executive Conclusion\n\n"
        f"Pre-registered screen (best non-control row per branch by WF beats, tie-break Calmar): **{n_success}/{len(screens)} branches SUCCESS**. Criteria: WF beats strictly above the best control row AND MDD no worse than control AND MDD >= -50%. A SUCCESS is a weak lead only (it does NOT feed 7F - incompatible window). NOT a gate pass, NOT a promotion `[advances_fin_ml, p.208-211]`.\n\n",
    ]
    sections.append("## Screen Result\n\n" + screen_table(screens))
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    for screen in screens:
        sections.append(
            f"## Top {screen['branch']} Rows (by WF beats, then Calmar; control rows marked)\n\n"
            + top_rows_table(frame, str(screen["branch"]))
        )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        + "".join(
            f"| {s['branch']}: MF sleeve beats control on WF without worse MDD? | {'Yes' if s['success'] else 'No'} ({int(s['best']['wf_beats'])}/{int(s['best']['wf_windows'])} vs {int(s['control']['wf_beats'])}/{int(s['control']['wf_windows'])}; MDD {fmt_pct(s['best']['taxed_mdd'])} vs {fmt_pct(s['control']['taxed_mdd'])}). |\n"
            for s in screens
        )
        + f"| Screen successes? | {n_success}/{len(screens)} (low-power window). |\n"
        "| Did we promote anything? | No - diagnostic only. |\n"
        "| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    best_returns: dict[str, pd.Series] = {}
    control_returns: dict[str, pd.Series] = {}
    sanity: dict[str, float] = {}
    n_trials_added = 0

    for spec in BRANCH_SPECS:
        branch_key = str(spec["branch"])
        branch, prices, returns, sma_signal, underlying_taxed = build_branch_data(branch_key)
        base_weights = clean_weights(
            next(r["weights"] for r in phase04.RISK_OFF_SPECS if r["name"] == spec["risk_off_name"])
        )
        gate = vol_gate_series(returns, branch["underlying"], str(spec["vol"]))
        signal = sma_signal & gate

        best_key: tuple[int, float] | None = None
        control_key: tuple[int, float] | None = None
        for sleeve in sleeve_specs(base_weights):
            sleeve_weights = clean_weights(dict(sleeve["weights"]))  # type: ignore[arg-type]
            for lag in LAGS:
                taxed, tax_summary = simulate_sleeve(
                    branch, returns, signal, float(spec["target_leverage"]), sleeve_weights, lag
                )
                metrics = metrics_from_returns(taxed)
                beats, n_windows = wf_beats(taxed, underlying_taxed)
                n_trials_added += 1
                rows.append(
                    {
                        "branch": branch_key,
                        "sleeve": sleeve["name"],
                        "lag_days": lag,
                        "target_leverage": float(spec["target_leverage"]),
                        "vol_filter": spec["vol"],
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
                        "turnover_per_year": tax_summary["turnover_per_year"],
                        "total_tax_paid_pct_initial": tax_summary["total_tax_paid_pct_initial"],
                    }
                )
                key = (beats, float(metrics.calmar))
                if sleeve["name"] == "control":
                    if control_key is None or key > control_key:
                        control_key = key
                        control_returns[branch_key] = taxed
                elif best_key is None or key > best_key:
                    best_key = key
                    best_returns[branch_key] = taxed

        # Sanity: control at the committed headline lag vs an independent rerun.
        control_taxed, _ = simulate_sleeve(
            branch, returns, signal, float(spec["target_leverage"]), base_weights, int(spec["headline_lag"])
        )
        rerun_taxed, _ = simulate_sleeve(
            branch, returns, signal, float(spec["target_leverage"]), dict(base_weights), int(spec["headline_lag"])
        )
        sanity[branch_key] = float((control_taxed - rerun_taxed).abs().max())
        print(f"  {branch_key}: grid done ({returns.index[0].date()}..{returns.index[-1].date()})")

    frame = pd.DataFrame(rows)
    frame.to_csv(CSV, index=False)
    screens = [screen_branch(frame, str(spec["branch"])) for spec in BRANCH_SPECS]
    plot_rows = []
    eq = plot_equity_dd(best_returns, control_returns)
    plot_rows.append({"Plot": "Equity/drawdown vs control sleeve", "File": f"[plots/{eq.name}](plots/{eq.name})"})
    wf = plot_wf_comparison(screens)
    plot_rows.append({"Plot": "WF beat-count comparison", "File": f"[plots/{wf.name}](plots/{wf.name})"})
    frontier = plot_frontier(frame)
    plot_rows.append({"Plot": "CAGR x MDD frontier by sleeve", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    write_report(frame, screens, plot_rows, sanity, n_trials_added)

    for screen in screens:
        best = screen["best"]
        control = screen["control"]
        print(
            f"Phase 7E {screen['branch']}: best sleeve '{best['sleeve']}' lag {int(best['lag_days'])} "
            f"WF {int(best['wf_beats'])}/{int(best['wf_windows'])} (control {int(control['wf_beats'])}/{int(control['wf_windows'])}) "
            f"CAGR {best['taxed_cagr']:.2%} MDD {best['taxed_mdd']:.2%} (control MDD {control['taxed_mdd']:.2%}) "
            f"screen={'SUCCESS' if screen['success'] else 'FAIL'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
