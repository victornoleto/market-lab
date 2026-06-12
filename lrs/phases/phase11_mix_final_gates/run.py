"""Phase 11 - final gates for the Phase 6A RSC/LRS mix candidate (DIAGNOSTIC).

Research-only. Validates the already-selected Phase 6A row
``mix_lrs_spy_headline_20`` (80% RSC-US after-tax + 20%
``lrs_spy_headline`` after-tax satellite) against ``bench_rsc``. This phase adds
no search trials: it reuses Phase 6A's tax/accounting convention and runs the
mandate SS5 hard-block suite without changing thresholds. PBO uses the full
Phase 6A mix family rather than a narrowed ex-post grid; DSR uses the final LRS
lineage ledger (4569 trials). Walk-forward uses 5y IS / 2y OOS / 2y step so the
2000+ RSC window can still produce at least eight OOS windows; 7y/3y is reported
only as a low-power diagnostic `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.273-275]`, `[testing_tuning, p.318-320]`.
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
from lrs.lib.validation import gate_dsr, gate_walk_forward, run_gate_suite  # noqa: E402
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase06a_aftertax_frontier import run as phase06a  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase11_mix_final_gates.csv"
PHASE6A_CSV = RESULTS / "phase06a_aftertax_frontier.csv"

CANDIDATE_ID = "mix_lrs_spy_headline_20"
BENCHMARK_ID = "bench_rsc"
N_TRIALS = 4569  # final LRS lineage ledger; +0 here `[advances_fin_ml, p.273-275]`
N_TRIALS_STRESS = 4569 + 95601  # optional stress includes RSC evolution raw trials.

# 5y/2y preserves the mandate requirement for >=8 WF windows on the 2000+ RSC window.
WF_IS_SIZE = 252 * 5
WF_OOS_SIZE = 252 * 2
WF_STEP = 252 * 2
WF_DIAG_IS_SIZE = 252 * 7
WF_DIAG_OOS_SIZE = 252 * 3
WF_DIAG_STEP = 252 * 3

GATE_KEYS = phase04.GATE_KEYS
GATE_LABELS = dict(phase04.GATE_LABELS)
GATE_LABELS["g3_walk_forward"] = "G3 WF>=75%"


def phase6a_sanity(frame: pd.DataFrame) -> float:
    """Max abs diff against the committed Phase 6A CSV row."""
    if not PHASE6A_CSV.exists():
        return float("nan")
    committed = pd.read_csv(PHASE6A_CSV)
    old = committed[committed["candidate_id"] == CANDIDATE_ID].iloc[0]
    new = frame[frame["candidate_id"] == CANDIDATE_ID].iloc[0]
    return float(
        max(
            abs(float(old["cagr"]) - float(new["cagr"])),
            abs(float(old["mdd"]) - float(new["mdd"])),
            abs(float(old["calmar"]) - float(new["calmar"])),
        )
    )


def build_pbo_matrix(
    frame: pd.DataFrame, return_map: dict[str, pd.Series]
) -> tuple[np.ndarray, list[str], int]:
    """Return the Phase 6A mix-family matrix: T observations x N configs."""
    mix_ids = sorted(str(x) for x in frame.loc[frame["candidate_type"] == "mix", "candidate_id"])
    matrix_frame = pd.concat(
        [return_map[cid].rename(cid) for cid in mix_ids], axis=1, sort=False
    ).dropna()
    return matrix_frame.to_numpy(dtype=float), mix_ids, len(matrix_frame)


def evaluate_candidate() -> tuple[dict[str, object], pd.Series, pd.Series, list[str]]:
    components = phase06a.build_components_frame()
    frame, return_map, _satellite_series = phase06a.build_all(components)
    if CANDIDATE_ID not in return_map:
        raise KeyError(f"missing candidate {CANDIDATE_ID}")
    if BENCHMARK_ID not in return_map:
        raise KeyError(f"missing benchmark {BENCHMARK_ID}")

    matrix, mix_ids, matrix_rows = build_pbo_matrix(frame, return_map)
    candidate = return_map[CANDIDATE_ID]
    benchmark = return_map[BENCHMARK_ID]
    suite = run_gate_suite(
        candidate,
        matrix,
        benchmark,
        n_trials=N_TRIALS,
        wf_is_size=WF_IS_SIZE,
        wf_oos_size=WF_OOS_SIZE,
        wf_step=WF_STEP,
    )
    stress_dsr = gate_dsr(candidate, n_trials=N_TRIALS_STRESS)
    wf_diag = gate_walk_forward(
        candidate,
        benchmark,
        is_size=WF_DIAG_IS_SIZE,
        oos_size=WF_DIAG_OOS_SIZE,
        step=WF_DIAG_STEP,
    )

    candidate_metrics = metrics_from_returns(candidate)
    benchmark_metrics = metrics_from_returns(benchmark)
    gates = suite["gates"]
    row = {
        "config": CANDIDATE_ID,
        "benchmark": BENCHMARK_ID,
        "n_trials": N_TRIALS,
        "n_trials_stress": N_TRIALS_STRESS,
        "pbo_matrix_configs": int(matrix.shape[1]),
        "pbo_matrix_rows": int(matrix_rows),
        "sanity_vs_phase06a_csv": phase6a_sanity(frame),
        "taxed_cagr": candidate_metrics.cagr,
        "taxed_mdd": candidate_metrics.mdd,
        "taxed_sharpe": candidate_metrics.sharpe,
        "taxed_calmar": candidate_metrics.calmar,
        "benchmark_cagr": benchmark_metrics.cagr,
        "benchmark_mdd": benchmark_metrics.mdd,
        "benchmark_sharpe": benchmark_metrics.sharpe,
        "benchmark_calmar": benchmark_metrics.calmar,
        "cagr_spread_vs_benchmark": candidate_metrics.cagr - benchmark_metrics.cagr,
        "mdd_spread_vs_benchmark": candidate_metrics.mdd - benchmark_metrics.mdd,
        "calmar_spread_vs_benchmark": candidate_metrics.calmar - benchmark_metrics.calmar,
        "g1_pbo": gates["g1_pbo"]["pbo"],
        "g1_pass": gates["g1_pbo"]["pass_gate"],
        "g2_dsr_p": gates["g2_dsr"]["p_value"],
        "g2_observed_sharpe": gates["g2_dsr"]["observed_sharpe"],
        "g2_benchmark_sharpe": gates["g2_dsr"]["benchmark_sharpe"],
        "g2_pass": gates["g2_dsr"]["pass_gate"],
        "g2_stress_p": stress_dsr["p_value"],
        "g2_stress_pass": stress_dsr["pass_gate"],
        "g3_windows": gates["g3_walk_forward"]["n_windows"],
        "g3_beat": gates["g3_walk_forward"]["windows_beat_benchmark"],
        "g3_pass": gates["g3_walk_forward"]["pass_gate"],
        "g3_diag_7y3y_windows": wf_diag["n_windows"],
        "g3_diag_7y3y_beat": wf_diag["windows_beat_benchmark"],
        "g3_diag_7y3y_pass": wf_diag["pass_gate"],
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
        "_stress_dsr": stress_dsr,
        "_wf_diag": wf_diag,
    }
    return row, candidate, benchmark, mix_ids


def gate_table_rows(row: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "Config": row["config"],
            "G1 PBO": f"{row['g1_pbo']:.3f} {'P' if row['g1_pass'] else 'F'}",
            "G2 DSR p": f"{row['g2_dsr_p']:.3f} {'P' if row['g2_pass'] else 'F'}",
            "G3 WF": f"{int(row['g3_beat'])}/{int(row['g3_windows'])} {'P' if row['g3_pass'] else 'F'}",
            "G4 OOS": "P" if row["g4_pass"] else "F",
            "G5 FWD": "P" if row["g5_pass"] else "F",
            "G6 Boot": f"{row['g6_ci_low_sharpe']:.2f} {'P' if row['g6_pass'] else 'F'}",
            "G7 xlib": f"{row['g7_delta_pp']:.2g} {'P' if row['g7_pass'] else 'F'}",
            "Overall": "PASS" if row["overall_pass"] else "FAIL",
        }
    ]


def plot_gate_heatmap(row: dict[str, object]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap

    grid = np.array([[1.0 if row["_gates"][g]["pass_gate"] else 0.0 for g in GATE_KEYS]])
    fig, ax = plt.subplots(figsize=(9.5, 2.8))
    ax.imshow(grid, cmap=ListedColormap(["#d65f5f", "#4c9a6b"]), vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(GATE_KEYS)))
    ax.set_xticklabels([GATE_LABELS[g] for g in GATE_KEYS], rotation=30, ha="right")
    ax.set_yticks([0])
    ax.set_yticklabels([str(row["config"])])
    for j, gate in enumerate(GATE_KEYS):
        ax.text(
            j,
            0,
            "PASS" if row["_gates"][gate]["pass_gate"] else "FAIL",
            ha="center",
            va="center",
            fontsize=8,
            color="white",
        )
    ax.set_title("Phase 11 mandate gates (green=pass, red=fail) - DIAGNOSTIC")
    fig.tight_layout()
    out = PLOTS / "phase11_gate_heatmap.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_wf_spread(row: dict[str, object]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rel = np.array(row["_gates"]["g3_walk_forward"]["oos_rel_returns"], dtype=float) * 100.0
    colors = ["#4c9a6b" if x > 0 else "#d65f5f" for x in rel]
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    ax.bar(range(1, len(rel) + 1), rel, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title(f"Phase 11 WF OOS spread vs RSC ({int(row['g3_beat'])}/{int(row['g3_windows'])})")
    ax.set_xlabel("WF window")
    ax.set_ylabel("Candidate - RSC (% total return)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase11_wf_spread.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_relative_equity(candidate: pd.Series, benchmark: pd.Series) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    aligned = pd.concat({"candidate": candidate, "benchmark": benchmark}, axis=1).dropna()
    rel = (1.0 + aligned["candidate"]).cumprod() / (1.0 + aligned["benchmark"]).cumprod()
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    ax.plot(rel.index, rel, color="#345995", linewidth=1.6)
    ax.axhline(1.0, color="black", linewidth=0.8)
    ax.set_title("Phase 11 relative equity: mix_lrs_spy_headline_20 / RSC")
    ax.set_ylabel("Relative wealth")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase11_relative_equity.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def write_report(
    row: dict[str, object], plot_rows: list[dict[str, str]], mix_ids: list[str]
) -> None:
    failing = [GATE_LABELS[g] for g in GATE_KEYS if not row["_gates"][g]["pass_gate"]]
    verdict = (
        "The candidate passes all seven gates, but remains research-only pending a separate mandate SS7 decision."
        if row["overall_pass"]
        else "The candidate fails the pre-registered hard-block suite. Per the rule, no threshold changes, no re-runs and no promotion."
    )
    metrics_rows = [
        {
            "Series": CANDIDATE_ID,
            "CAGR": fmt_pct(row["taxed_cagr"]),
            "MDD": fmt_pct(row["taxed_mdd"]),
            "Sharpe": fmt_num(row["taxed_sharpe"]),
            "Calmar": fmt_num(row["taxed_calmar"]),
        },
        {
            "Series": BENCHMARK_ID,
            "CAGR": fmt_pct(row["benchmark_cagr"]),
            "MDD": fmt_pct(row["benchmark_mdd"]),
            "Sharpe": fmt_num(row["benchmark_sharpe"]),
            "Calmar": fmt_num(row["benchmark_calmar"]),
        },
        {
            "Series": "Spread vs RSC",
            "CAGR": fmt_pct(row["cagr_spread_vs_benchmark"]),
            "MDD": fmt_pct(row["mdd_spread_vs_benchmark"]),
            "Sharpe": "",
            "Calmar": fmt_num(row["calmar_spread_vs_benchmark"]),
        },
    ]
    diag_rows = [
        {
            "Diagnostic": "DSR stress incl. RSC evolution raw trials",
            "Value": f"n={N_TRIALS_STRESS}, p={row['g2_stress_p']:.3f}, {'PASS' if row['g2_stress_pass'] else 'FAIL'}",
        },
        {
            "Diagnostic": "WF canonical 7y/3y low-power check",
            "Value": f"{int(row['g3_diag_7y3y_beat'])}/{int(row['g3_diag_7y3y_windows'])}, {'PASS' if row['g3_diag_7y3y_pass'] else 'FAIL'}",
        },
        {
            "Diagnostic": "Phase 6A CSV sanity",
            "Value": f"max abs diff {row['sanity_vs_phase06a_csv']:.3g}",
        },
    ]
    sections = [
        "# Phase 11 - Final Gates for `mix_lrs_spy_headline_20` (DIAGNOSTIC)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading, capital allocation, or a mandate change. Maintenance mode remains unchanged.\n\n"
        f"Candidate: `{CANDIDATE_ID}` = 80% Phase 6A after-tax RSC leg + 20% `lrs_spy_headline` after-tax satellite, using Phase 6A's two-account contribution-funded convention. Benchmark: `{BENCHMARK_ID}`.\n\n"
        f"Pre-registered suite: canonical mandate SS5 wrappers (`lrs.lib.validation.run_gate_suite`), **DSR n_trials = {N_TRIALS}**, **+0 new trials**, PBO matrix = all Phase 6A mixes (**{len(mix_ids)} configs**, {row['pbo_matrix_rows']} common observations), WF = 5y IS / 2y OOS / 2y step to keep >=8 OOS windows on the 2000+ RSC window `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`, `[testing_tuning, p.318-320]`.\n\n"
        "## Executive Conclusion\n\n"
        f"Configs passing ALL seven gates: **{1 if row['overall_pass'] else 0}/1**. "
        + (f"Failing gates: {', '.join(failing)}. " if failing else "")
        + f"{verdict}\n\n",
        "## Gate Results\n\n"
        + md_table(
            gate_table_rows(row),
            [
                "Config",
                "G1 PBO",
                "G2 DSR p",
                "G3 WF",
                "G4 OOS",
                "G5 FWD",
                "G6 Boot",
                "G7 xlib",
                "Overall",
            ],
        ),
        "## Metrics (warning-only tiers, NOT gates)\n\n"
        + md_table(metrics_rows, ["Series", "CAGR", "MDD", "Sharpe", "Calmar"]),
        "## Diagnostics\n\n" + md_table(diag_rows, ["Diagnostic", "Value"]),
        "## PBO Family\n\n"
        f"The PBO matrix uses every Phase 6A mix row, not a narrowed post-result grid: `{', '.join(mix_ids)}`.\n\n",
        "## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]),
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Candidate passes all 7 gates? | {'Yes' if row['overall_pass'] else 'No'}. |\n"
        f"| Failing gates? | {', '.join(failing) if failing else 'none'}. |\n"
        "| Did we promote anything? | No. This is research-only and mandate §1 remains unchanged. |\n"
        "| Is this deployment-ready? | No. No deploy, no paper trade, no capital movement. |\n\n"
        f"{verdict}\n",
    ]
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)

    row, candidate, benchmark, mix_ids = evaluate_candidate()
    csv_row = {k: v for k, v in row.items() if not k.startswith("_")}
    pd.DataFrame([csv_row]).to_csv(CSV, index=False)
    heatmap = plot_gate_heatmap(row)
    wf = plot_wf_spread(row)
    rel = plot_relative_equity(candidate, benchmark)
    plot_rows = [
        {"Plot": "Gate pass/fail heatmap", "File": f"[plots/{heatmap.name}](plots/{heatmap.name})"},
        {"Plot": "Walk-forward OOS spread", "File": f"[plots/{wf.name}](plots/{wf.name})"},
        {"Plot": "Relative equity vs RSC", "File": f"[plots/{rel.name}](plots/{rel.name})"},
    ]
    write_report(row, plot_rows, mix_ids)

    flags = "".join("P" if row[f"g{i}_pass"] else "F" for i in range(1, 8))
    print(
        f"Phase 11: {CANDIDATE_ID} G1-7={flags} overall={'PASS' if row['overall_pass'] else 'FAIL'} "
        f"(PBO {row['g1_pbo']:.3f}, DSR p {row['g2_dsr_p']:.3f}, WF {int(row['g3_beat'])}/{int(row['g3_windows'])})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
