"""Phase 8 - final mandate gate suite on the Phase 7 round survivors (DIAGNOSTIC).

Research-only. Runs the canonical mandate SS5 hard-block suite (PBO, DSR, WF,
OOS, FWD stress, bootstrap 99.9% CI, cross-lib) on the two user-chosen
configs: `spy_7a_ensemble` (7A ensemble, spy_alt_off / narrow / lag 2) and
`qqq_7d_quadratic` (7D quadratic vol-target, sigma 40% / RV21 / lag 2).
PBO trial matrix = the winning family grid per branch (36 configs each);
DSR n_trials = 4377 (full in-repo lineage through 7F; letf-lab excluded,
documented undercount) `[advances_fin_ml, p.208-211]`, `[advances_fin_ml,
p.273-275]`, `[testing_tuning, p.318-320]`. +0 trials - this phase
re-evaluates already-counted configs, it does not search. Even a 7/7 pass is
research-only; any allocation change is a separate mandate SS7 process.
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

from lrs.lib.backtest import fmt_num, fmt_pct, md_table, metrics_from_returns  # noqa: E402
from lrs.lib.validation import run_gate_suite  # noqa: E402
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase06b_vol_target_continuous import run as phase06b  # noqa: E402
from lrs.phases.phase07a_ensemble_lookback import run as phase07a  # noqa: E402
from lrs.phases.phase07d_vol_target_quadratic import run as phase07d  # noqa: E402
from lrs.lib.backtest import clean_weights  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase08_final_gates.csv"
PHASE7A_CSV = RESULTS / "phase07a_ensemble_lookback.csv"
PHASE7D_CSV = RESULTS / "phase07d_vol_target_quadratic.csv"

N_TRIALS = 4377  # full in-repo lineage through Phase 7F (+0 added here)
GATE_KEYS = phase04.GATE_KEYS
GATE_LABELS = phase04.GATE_LABELS

# The two user-chosen survivor configs (2026-06-10).
SPY_CONFIG = {"name": "spy_7a_ensemble", "base_name": "spy_alt_off", "window_set": "narrow_150_225", "lag": 2}
QQQ_CONFIG = {"name": "qqq_7d_quadratic", "sigma_target": 0.40, "rv_window": 21, "lag": 2}


def spy_family(context: "phase04.BranchContext") -> tuple[pd.Series, list[pd.Series], dict[str, float]]:
    """SPY survivor returns + the 7A SPY family grid (PBO matrix columns)."""
    fraction_by_set = {
        name: phase07a.ensemble_fraction(context, windows)
        for name, windows in phase07a.WINDOW_SETS.items()
    }
    spy_bases = [b for b in phase04.BASE_SPECS if b["branch"] == "SPY"]
    chosen: pd.Series | None = None
    chosen_row: dict[str, float] | None = None
    columns: list[pd.Series] = []
    for base in spy_bases:
        for set_name in phase07a.WINDOW_SETS:
            for lag in phase07a.LAGS:
                row, taxed = phase07a.evaluate_row(context, base, set_name, lag, fraction_by_set)
                columns.append(taxed.reset_index(drop=True))
                if (
                    base["name"] == SPY_CONFIG["base_name"]
                    and set_name == SPY_CONFIG["window_set"]
                    and lag == SPY_CONFIG["lag"]
                ):
                    chosen = taxed
                    chosen_row = {"taxed_cagr": float(row["taxed_cagr"]), "taxed_mdd": float(row["taxed_mdd"])}
    assert chosen is not None and chosen_row is not None
    return chosen, columns, chosen_row


def qqq_family(context: "phase04.BranchContext") -> tuple[pd.Series, list[pd.Series], dict[str, float]]:
    """QQQ survivor returns + the 7D QQQ family grid (PBO matrix columns)."""
    spec = next(s for s in phase06b.BRANCH_SPECS if s["branch"] == "QQQ")
    risk_off = next(r for r in phase04.RISK_OFF_SPECS if r["name"] == spec["risk_off"])
    risk_off_weights = clean_weights(dict(risk_off["weights"]))  # type: ignore[arg-type]
    chosen: pd.Series | None = None
    chosen_row: dict[str, float] | None = None
    columns: list[pd.Series] = []
    for sigma_target in phase07d.SIGMA_TARGETS:
        for rv_window in phase07d.RV_WINDOWS:
            for lag in phase07d.LAGS:
                row, taxed, _lev = phase07d.evaluate_row(
                    context, spec, sigma_target, rv_window, lag, risk_off_weights
                )
                columns.append(taxed.reset_index(drop=True))
                if (
                    sigma_target == QQQ_CONFIG["sigma_target"]
                    and rv_window == QQQ_CONFIG["rv_window"]
                    and lag == QQQ_CONFIG["lag"]
                ):
                    chosen = taxed
                    chosen_row = {"taxed_cagr": float(row["taxed_cagr"]), "taxed_mdd": float(row["taxed_mdd"])}
    assert chosen is not None and chosen_row is not None
    return chosen, columns, chosen_row


def pbo_matrix_from_columns(columns: list[pd.Series]) -> np.ndarray:
    matrix = pd.concat(columns, axis=1).dropna()
    return matrix.to_numpy(dtype=float)


def sanity_vs_phase7_csv(config_name: str, recomputed: dict[str, float]) -> float:
    """Max abs diff between recomputed CAGR/MDD and the committed Phase 7 CSV row."""
    if config_name == "spy_7a_ensemble":
        df = pd.read_csv(PHASE7A_CSV)
        row = df[
            (df["config_type"] == "ensemble")
            & (df["base_name"] == SPY_CONFIG["base_name"])
            & (df["window_set"] == SPY_CONFIG["window_set"])
            & (df["lag_days"] == SPY_CONFIG["lag"])
        ].iloc[0]
    else:
        df = pd.read_csv(PHASE7D_CSV)
        row = df[
            (df["config_type"] == "quadratic")
            & (df["branch"] == "QQQ")
            & (df["sigma_target"] == QQQ_CONFIG["sigma_target"])
            & (df["rv_window"] == QQQ_CONFIG["rv_window"])
            & (df["lag_days"] == QQQ_CONFIG["lag"])
        ].iloc[0]
    return float(
        max(
            abs(float(row["taxed_cagr"]) - recomputed["taxed_cagr"]),
            abs(float(row["taxed_mdd"]) - recomputed["taxed_mdd"]),
        )
    )


def evaluate_config(
    name: str,
    branch_key: str,
    returns: pd.Series,
    matrix: np.ndarray,
    benchmark: pd.Series,
    sanity_diff: float,
) -> dict[str, object]:
    metrics = metrics_from_returns(returns)
    suite = run_gate_suite(
        returns,
        matrix,
        benchmark,
        n_trials=N_TRIALS,
        wf_is_size=phase04.WF_IS_SIZE,
        wf_oos_size=phase04.WF_OOS_SIZE,
        wf_step=phase04.WF_STEP,
    )
    gates = suite["gates"]
    return {
        "config": name,
        "branch": branch_key,
        "n_trials": N_TRIALS,
        "pbo_matrix_configs": int(matrix.shape[1]),
        "sanity_vs_phase7_csv": sanity_diff,
        "taxed_cagr": metrics.cagr,
        "taxed_mdd": metrics.mdd,
        "taxed_sharpe": metrics.sharpe,
        "taxed_calmar": metrics.calmar,
        "g1_pbo": gates["g1_pbo"]["pbo"],
        "g1_pass": gates["g1_pbo"]["pass_gate"],
        "g2_dsr_p": gates["g2_dsr"]["p_value"],
        "g2_observed_sharpe": gates["g2_dsr"]["observed_sharpe"],
        "g2_pass": gates["g2_dsr"]["pass_gate"],
        "g3_windows": gates["g3_walk_forward"]["n_windows"],
        "g3_beat": gates["g3_walk_forward"]["windows_beat_benchmark"],
        "g3_pass": gates["g3_walk_forward"]["pass_gate"],
        "g4_oos_sharpe": gates["g4_oos"]["oos_sharpe"],
        "g4_beats": gates["g4_oos"]["beats_benchmark"],
        "g4_pass": gates["g4_oos"]["pass_gate"],
        "g5_fwd_sharpe": gates["g5_fwd_stress"]["fwd_sharpe"],
        "g5_pass": gates["g5_fwd_stress"]["pass_gate"],
        "g6_ci_low_sharpe": gates["g6_bootstrap"]["ci_low_sharpe"],
        "g6_pass": gates["g6_bootstrap"]["pass_gate"],
        "g7_delta_pp": gates["g7_cross_lib"]["delta_pp"],
        "g7_pass": gates["g7_cross_lib"]["pass_gate"],
        "overall_pass": suite["overall_pass"],
        "_gates": gates,
    }


# --------------------------------------------------------------------------- plots


def plot_gate_heatmap(rows: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap

    configs = [str(r["config"]) for r in rows]
    grid = np.array([[1.0 if r["_gates"][g]["pass_gate"] else 0.0 for g in GATE_KEYS] for r in rows])
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.imshow(grid, cmap=ListedColormap(["#d65f5f", "#4c9a6b"]), vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(GATE_KEYS)))
    ax.set_xticklabels([GATE_LABELS[g] for g in GATE_KEYS], rotation=30, ha="right")
    ax.set_yticks(range(len(configs)))
    ax.set_yticklabels(configs)
    for i in range(len(configs)):
        for j in range(len(GATE_KEYS)):
            ax.text(j, i, "PASS" if grid[i, j] else "FAIL", ha="center", va="center", fontsize=8, color="white")
    ax.set_title("Phase 8 mandate gates (green=pass, red=fail) - DIAGNOSTIC")
    fig.tight_layout()
    out = PLOTS / "phase08_gate_heatmap.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_wf_spread(rows: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, len(rows), figsize=(6 * len(rows), 4.5), squeeze=False)
    for ax, r in zip(axes[0], rows):
        rel = np.array(r["_gates"]["g3_walk_forward"]["oos_rel_returns"]) * 100.0
        colors = ["#4c9a6b" if x > 0 else "#d65f5f" for x in rel]
        ax.bar(range(len(rel)), rel, color=colors)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(f"{r['config']} WF OOS spread ({r['g3_beat']}/{r['g3_windows']})")
        ax.set_xlabel("Window")
        ax.set_ylabel("Strategy - underlying (% total)")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase08_wf_spread.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def gate_table_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for r in rows:
        out.append(
            {
                "Config": r["config"],
                "G1 PBO": f"{r['g1_pbo']:.3f} {'P' if r['g1_pass'] else 'F'}",
                "G2 DSR p": f"{r['g2_dsr_p']:.3f} {'P' if r['g2_pass'] else 'F'}",
                "G3 WF": f"{int(r['g3_beat'])}/{int(r['g3_windows'])} {'P' if r['g3_pass'] else 'F'}",
                "G4 OOS": "P" if r["g4_pass"] else "F",
                "G5 FWD": "P" if r["g5_pass"] else "F",
                "G6 Boot": f"{r['g6_ci_low_sharpe']:.2f} {'P' if r['g6_pass'] else 'F'}",
                "G7 xlib": f"{r['g7_delta_pp']:.2g} {'P' if r['g7_pass'] else 'F'}",
                "Overall": "PASS" if r["overall_pass"] else "FAIL",
            }
        )
    return out


def write_report(rows: list[dict[str, object]], plot_rows: list[dict[str, str]]) -> None:
    n_pass = sum(1 for r in rows if r["overall_pass"])
    fail_counts = {g: sum(1 for r in rows if not r["_gates"][g]["pass_gate"]) for g in GATE_KEYS}
    binding = ", ".join(f"{GATE_LABELS[g]} fails {c}/{len(rows)}" for g, c in fail_counts.items() if c)
    sanity_text = "; ".join(f"{r['config']}: max abs diff {r['sanity_vs_phase7_csv']:.3g}" for r in rows)
    verdict = (
        f"{n_pass} config(s) pass all seven gates - the line's FIRST formal gate pass, recorded as research-only. This is NOT a promotion: any allocation discussion is a separate, explicit mandate SS7 process."
        if n_pass
        else "No config passes all seven gates. Per the pre-registered rule, both configs are re-closed with the ledger as-is; the family returns to the shelf pending new literature or regime. No re-runs, no threshold adjustments."
    )
    sections = [
        "# Phase 8 - Final Mandate Gate Suite on the Round Survivors (DIAGNOSTIC)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome - even a 7/7 pass only makes a config eligible for a separate mandate SS7 decision.\n\n"
        "User-chosen configs (2026-06-10): `spy_7a_ensemble` (7A ensemble, `spy_alt_off / narrow {150,175,200,225} / lag 2`) and `qqq_7d_quadratic` (7D quadratic vol-target, `sigma 40% / RV21 / lag 2`). Honest prior recorded in the pre-registration: QQQ at 8/11 (72.7%) was EXPECTED to fail G3; it is validated for the record.\n\n"
        f"Suite: canonical mandate SS5 wrappers (`lrs/lib/validation.run_gate_suite`), Phase 4 geometry verbatim. **DSR n_trials = {N_TRIALS}** (full in-repo lineage through 7F; letf-lab excluded = honest undercount). PBO matrix = winning family grid per branch (36 configs each). **+0 trials; ledger stays {N_TRIALS}** `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`, `[testing_tuning, p.318-320]`.\n\n"
        f"**Built-in sanity (recomputed CAGR/MDD vs committed Phase 7 CSV rows):** {sanity_text}.\n\n"
        "## Executive Conclusion\n\n"
        f"Configs passing ALL seven gates (hard-block, zero bypass): **{n_pass}/{len(rows)}**. "
        + (f"Failing gates: {binding}. " if binding else "")
        + f"{verdict}\n\n",
    ]
    sections.append(
        "## Gate Results\n\n"
        + md_table(gate_table_rows(rows), ["Config", "G1 PBO", "G2 DSR p", "G3 WF", "G4 OOS", "G5 FWD", "G6 Boot", "G7 xlib", "Overall"])
    )
    metrics_rows = [
        {
            "Config": r["config"],
            "CAGR": fmt_pct(r["taxed_cagr"]),
            "MDD": fmt_pct(r["taxed_mdd"]),
            "Sharpe": fmt_num(r["taxed_sharpe"]),
            "Calmar": fmt_num(r["taxed_calmar"]),
            "Obs SR (ann)": fmt_num(r["g2_observed_sharpe"] * np.sqrt(252.0)),
        }
        for r in rows
    ]
    sections.append(
        "## Metrics (warning-only tiers, NOT gates)\n\n"
        + md_table(metrics_rows, ["Config", "CAGR", "MDD", "Sharpe", "Calmar", "Obs SR (ann)"])
    )
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Configs passing all 7 gates? | {n_pass}/{len(rows)}. |\n"
        f"| Failing gates? | {binding or 'none'}. |\n"
        "| Did we promote anything? | No - even a pass is research-only pending mandate SS7. |\n"
        "| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |\n\n"
        f"{verdict}\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)

    spy_context = phase04.build_context(phase04.BRANCHES["SPY"])
    spy_returns, spy_columns, spy_row = spy_family(spy_context)
    spy_sanity = sanity_vs_phase7_csv("spy_7a_ensemble", spy_row)
    print(f"  SPY family rebuilt ({len(spy_columns)} PBO columns; sanity {spy_sanity:.3g})")

    qqq_context = phase04.build_context(phase04.BRANCHES["QQQ"])
    qqq_returns, qqq_columns, qqq_row = qqq_family(qqq_context)
    qqq_sanity = sanity_vs_phase7_csv("qqq_7d_quadratic", qqq_row)
    print(f"  QQQ family rebuilt ({len(qqq_columns)} PBO columns; sanity {qqq_sanity:.3g})")

    rows = [
        evaluate_config(
            "spy_7a_ensemble", "SPY", spy_returns,
            pbo_matrix_from_columns(spy_columns), spy_context.underlying_taxed, spy_sanity,
        ),
        evaluate_config(
            "qqq_7d_quadratic", "QQQ", qqq_returns,
            pbo_matrix_from_columns(qqq_columns), qqq_context.underlying_taxed, qqq_sanity,
        ),
    ]

    csv_rows = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
    pd.DataFrame(csv_rows).to_csv(CSV, index=False)
    heatmap = plot_gate_heatmap(rows)
    wf = plot_wf_spread(rows)
    plot_rows = [
        {"Plot": "Gate pass/fail heatmap", "File": f"[plots/{heatmap.name}](plots/{heatmap.name})"},
        {"Plot": "Walk-forward OOS spread", "File": f"[plots/{wf.name}](plots/{wf.name})"},
    ]
    write_report(rows, plot_rows)

    n_pass = sum(1 for r in rows if r["overall_pass"])
    print(f"Phase 8: {len(rows)} configs; {n_pass} pass all 7 gates; n_trials={N_TRIALS}")
    for r in rows:
        flags = "".join("P" if r[f"g{i}_pass"] else "F" for i in range(1, 8))
        print(
            f"  {r['config']:18s} G1-7={flags} overall={'PASS' if r['overall_pass'] else 'FAIL'} "
            f"(PBO {r['g1_pbo']:.3f}, DSR p {r['g2_dsr_p']:.3f}, WF {int(r['g3_beat'])}/{int(r['g3_windows'])})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
