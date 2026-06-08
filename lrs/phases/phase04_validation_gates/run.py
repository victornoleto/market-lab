"""Phase 4 - mandate validation gates on the LRS final geometry (DIAGNOSTIC).

Research-only. This runner does NOT authorize deployment, paper trading or a
mandate change - regardless of outcome. It runs the canonical mandate §5 gate
suite (PBO, DSR, walk-forward, single-block OOS, FWD stress, bootstrap 99.9% CI,
cross-lib) on the 6 SMA200 bases (3 SPY + 3 QQQ, each at its best-score lag) and
records an honest pass/fail. Per `lrs/NEXT_STEPS.md`: "Nao e promocao; e
diagnostico para saber se a familia merece continuar." CAGR/MDD remain
warning-only tiers, not gates `[advances_fin_ml, p.208-211]`.

Gate wrappers live in `lrs/lib/validation.py` (thin layer over the canonical
`market_lab.backtest.validation`). The per-branch PBO trial matrix is the Phase 2
exposure-geometry grid at SMA200 (8 leverages x 5 risk-off x 5 vol = 200 configs,
fixed lag) - the search where the bases were selected. DSR uses the direct
lineage n_trials = 2400 + 324 + 216 + 936 = 3876.
"""
from __future__ import annotations

from dataclasses import dataclass
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
from lrs.lib.validation import run_gate_suite  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase04_validation_gates.csv"
PHASE3B_CSV = RESULTS / "phase03b_regime_signals.csv"

SMA_WINDOW = 200
PBO_LAG = 0
# Direct-lineage cumulative trials that produced/refined the pick (user decision).
N_TRIALS = 2400 + 324 + 216 + 936  # Phase 2 + 3A + 3A-2 + 3C = 3876
# Walk-forward: ~7y IS / ~3y OOS, non-overlapping -> >=8 windows on both branches.
WF_IS_SIZE = 1764
WF_OOS_SIZE = 756
WF_STEP = 756

BRANCHES = {
    "SPY": {"branch": "SPY", "underlying": "SPYSIM", "lev2": "SSOSIM", "lev3": "UPROSIM"},
    "QQQ": {"branch": "QQQ", "underlying": "QQQSIM", "lev2": "QLDSIM", "lev3": "TQQQSIM"},
}

# Phase 2 grid (verbatim) -> the per-branch PBO trial matrix at SMA200.
TARGET_LEVERAGES = [1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00]
RISK_OFF_SPECS: list[dict[str, object]] = [
    {"name": "CASHX", "weights": {"CASHX": 1.0}},
    {"name": "ZROZ", "weights": {"ZROZSIM": 1.0}},
    {"name": "50 ZROZ / 50 GLD", "weights": {"ZROZSIM": 0.50, "GLDSIM": 0.50}},
    {"name": "40 ZROZ / 40 GLD / 20 IEF", "weights": {"ZROZSIM": 0.40, "GLDSIM": 0.40, "IEFSIM": 0.20}},
    {"name": "50 ZROZ / 25 GLD / 25 CASH", "weights": {"ZROZSIM": 0.50, "GLDSIM": 0.25, "CASHX": 0.25}},
]
VOL_SPECS: list[dict[str, object]] = [
    {"name": "none", "window": 0, "threshold": None},
    {"name": "RV21 <= 40%", "window": 21, "threshold": 0.40},
    {"name": "RV63 <= 40%", "window": 63, "threshold": 0.40},
    {"name": "RV21 <= 30%", "window": 21, "threshold": 0.30},
    {"name": "RV63 <= 30%", "window": 63, "threshold": 0.30},
]

# The 6 bases under validation (Phase 2 top + 2 one-lever neighbours per branch).
BASE_SPECS: list[dict[str, object]] = [
    {"branch": "SPY", "name": "spy_top", "target_leverage": 2.00, "risk_off": "50 ZROZ / 25 GLD / 25 CASH", "vol": "RV21 <= 30%"},
    {"branch": "SPY", "name": "spy_lower_lev", "target_leverage": 1.75, "risk_off": "50 ZROZ / 25 GLD / 25 CASH", "vol": "RV21 <= 30%"},
    {"branch": "SPY", "name": "spy_alt_off", "target_leverage": 2.00, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV21 <= 30%"},
    {"branch": "QQQ", "name": "qqq_top", "target_leverage": 1.75, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV63 <= 40%"},
    {"branch": "QQQ", "name": "qqq_lower_lev", "target_leverage": 1.50, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV63 <= 40%"},
    {"branch": "QQQ", "name": "qqq_alt_vol", "target_leverage": 1.75, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV21 <= 30%"},
]
GATE_KEYS = ["g1_pbo", "g2_dsr", "g3_walk_forward", "g4_oos", "g5_fwd_stress", "g6_bootstrap", "g7_cross_lib"]
GATE_LABELS = {
    "g1_pbo": "G1 PBO<0.5",
    "g2_dsr": "G2 DSR p<.05",
    "g3_walk_forward": "G3 WF>=6/8",
    "g4_oos": "G4 OOS",
    "g5_fwd_stress": "G5 FWD",
    "g6_bootstrap": "G6 Boot99.9",
    "g7_cross_lib": "G7 xlib",
}


@dataclass
class BranchContext:
    branch: dict[str, str]
    returns: pd.DataFrame
    sma_signal: pd.Series
    underlying_taxed: pd.Series


def branch_assets(branch: dict[str, str]) -> list[str]:
    return sorted({branch["underlying"], branch["lev2"], branch["lev3"], "CASHX", "GLDSIM", "IEFSIM", "ZROZSIM"})


def target_leverage_weights(branch: dict[str, str], target_leverage: float) -> dict[str, float]:
    if target_leverage < 1.0 or target_leverage > 3.0:
        raise ValueError(f"target leverage out of range: {target_leverage}")
    if target_leverage <= 2.0:
        return clean_weights({branch["underlying"]: 2.0 - target_leverage, branch["lev2"]: target_leverage - 1.0})
    return clean_weights({branch["lev2"]: 3.0 - target_leverage, branch["lev3"]: target_leverage - 2.0})


def build_context(branch: dict[str, str]) -> BranchContext:
    prices = load_price_frame(branch_assets(branch))
    returns = prices.pct_change().dropna()
    prices = prices.reindex(returns.index)
    sma_signal = build_sma_signal(prices[branch["underlying"]], SMA_WINDOW).reindex(returns.index).fillna(False)
    underlying_frame = constant_weight_frame(returns.index, {branch["underlying"]: 1.0})
    underlying_taxed, _ = simulate_weight_frame(returns, underlying_frame, taxable=True)
    return BranchContext(branch=branch, returns=returns, sma_signal=sma_signal, underlying_taxed=underlying_taxed)


def vol_gate(context: BranchContext, spec: dict[str, object]) -> pd.Series:
    if spec["threshold"] is None:
        return pd.Series(True, index=context.returns.index)
    window = int(spec["window"])
    threshold = float(spec["threshold"])
    underlying_returns = context.returns[context.branch["underlying"]]
    realized_vol = underlying_returns.rolling(window).std(ddof=0).shift(1) * np.sqrt(252.0)
    return (realized_vol <= threshold).reindex(context.returns.index).fillna(False)


def simulate_returns(
    context: BranchContext,
    target_leverage: float,
    risk_off_weights: dict[str, float],
    vol_spec: dict[str, object],
    lag_days: int,
) -> pd.Series:
    """After-tax daily returns for an SMA200 LRS config (signal = SMA & vol_gate)."""
    risk_on = target_leverage_weights(context.branch, target_leverage)
    signal = context.sma_signal & vol_gate(context, vol_spec)
    assets = sorted(set(risk_on) | set(risk_off_weights) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=context.returns.index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on.get(asset, 0.0), risk_off_weights.get(asset, 0.0))
    weights, _ = build_weekly_lagged_weights(desired, lag_days=lag_days, risk_on_weights=risk_on)
    taxed, _ = simulate_weight_frame(context.returns, weights, taxable=True)
    return taxed


def best_lag_for_base(base_name: str) -> int:
    """Headline lag = best-score SMA200 lag for this base in Phase 3A-2 (committed)."""
    df = pd.read_csv(PHASE3B_CSV)
    rows = df[(df["base_name"] == base_name) & (df["regime_form"] == "SMA200")]
    return int(rows.sort_values("score", ascending=False).iloc[0]["lag_days"])


def build_pbo_matrix(context: BranchContext) -> np.ndarray:
    """T x N after-tax returns matrix over the Phase 2 geometry grid at SMA200."""
    columns: list[pd.Series] = []
    for target_leverage in TARGET_LEVERAGES:
        for risk_off in RISK_OFF_SPECS:
            for vol_spec in VOL_SPECS:
                taxed = simulate_returns(context, target_leverage, clean_weights(risk_off["weights"]), vol_spec, PBO_LAG)
                columns.append(taxed.reset_index(drop=True))
    matrix = pd.concat(columns, axis=1).dropna()
    return matrix.to_numpy(dtype=float)


def evaluate_base(context: BranchContext, base: dict[str, object], pbo_matrix: np.ndarray) -> dict[str, object]:
    risk_off_weights = clean_weights(next(r["weights"] for r in RISK_OFF_SPECS if r["name"] == base["risk_off"]))
    vol_spec = next(v for v in VOL_SPECS if v["name"] == base["vol"])
    lag = best_lag_for_base(str(base["name"]))
    base_returns = simulate_returns(context, float(base["target_leverage"]), risk_off_weights, vol_spec, lag)
    metrics = metrics_from_returns(base_returns)
    suite = run_gate_suite(
        base_returns,
        pbo_matrix,
        context.underlying_taxed,
        n_trials=N_TRIALS,
        wf_is_size=WF_IS_SIZE,
        wf_oos_size=WF_OOS_SIZE,
        wf_step=WF_STEP,
    )
    gates = suite["gates"]
    row: dict[str, object] = {
        "branch": base["branch"],
        "base_name": base["name"],
        "target_leverage": float(base["target_leverage"]),
        "risk_off": base["risk_off"],
        "vol_filter": base["vol"],
        "lag_days": lag,
        "n_trials": N_TRIALS,
        "taxed_cagr": metrics.cagr,
        "taxed_mdd": metrics.mdd,
        "taxed_sharpe": metrics.sharpe,
        "taxed_calmar": metrics.calmar,
        "g1_pbo": gates["g1_pbo"]["pbo"],
        "g1_pass": gates["g1_pbo"]["pass_gate"],
        "g2_dsr_p": gates["g2_dsr"]["p_value"],
        "g2_observed_sharpe": gates["g2_dsr"]["observed_sharpe"],
        "g2_benchmark_sharpe": gates["g2_dsr"]["benchmark_sharpe"],
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
        "_base_returns": base_returns,
    }
    return row


# --------------------------------------------------------------------------- plots


def plot_gate_heatmap(rows: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap

    bases = [str(r["base_name"]) for r in rows]
    grid = np.array([[1.0 if r["_gates"][g]["pass_gate"] else 0.0 for g in GATE_KEYS] for r in rows])
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(grid, cmap=ListedColormap(["#d65f5f", "#4c9a6b"]), vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(GATE_KEYS)))
    ax.set_xticklabels([GATE_LABELS[g] for g in GATE_KEYS], rotation=30, ha="right")
    ax.set_yticks(range(len(bases)))
    ax.set_yticklabels(bases)
    for i in range(len(bases)):
        for j in range(len(GATE_KEYS)):
            ax.text(j, i, "PASS" if grid[i, j] else "FAIL", ha="center", va="center", fontsize=8, color="white")
    ax.set_title("Phase 4 mandate gates (green=pass, red=fail) - DIAGNOSTIC")
    fig.tight_layout()
    out = PLOTS / "phase04_gate_heatmap.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_wf_spread(rows: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    headliners = [r for r in rows if r["base_name"] in ("spy_top", "qqq_top")]
    fig, axes = plt.subplots(1, len(headliners), figsize=(6 * len(headliners), 4.5), squeeze=False)
    for ax, r in zip(axes[0], headliners):
        rel = np.array(r["_gates"]["g3_walk_forward"]["oos_rel_returns"]) * 100.0
        colors = ["#4c9a6b" if x > 0 else "#d65f5f" for x in rel]
        ax.bar(range(len(rel)), rel, color=colors)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(f"{r['base_name']} WF OOS spread vs underlying ({r['g3_beat']}/{r['g3_windows']})")
        ax.set_xlabel("Window")
        ax.set_ylabel("Strategy - underlying (% total)")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase04_wf_spread.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def make_plots(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    PLOTS.mkdir(parents=True, exist_ok=True)
    plots = []
    heatmap = plot_gate_heatmap(rows)
    plots.append({"Plot": "Gate pass/fail heatmap", "File": f"[plots/{heatmap.name}](plots/{heatmap.name})"})
    wf = plot_wf_spread(rows)
    plots.append({"Plot": "Walk-forward OOS spread (headliners)", "File": f"[plots/{wf.name}](plots/{wf.name})"})
    return plots


# --------------------------------------------------------------------------- report


def gate_table_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for r in rows:
        out.append(
            {
                "Branch": r["branch"],
                "Base": r["base_name"],
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


def metrics_table_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for r in rows:
        out.append(
            {
                "Branch": r["branch"],
                "Base": r["base_name"],
                "L": fmt_num(r["target_leverage"], 2),
                "Lag": int(r["lag_days"]),
                "CAGR": fmt_pct(r["taxed_cagr"]),
                "MDD": fmt_pct(r["taxed_mdd"]),
                "Sharpe": fmt_num(r["taxed_sharpe"]),
                "Calmar": fmt_num(r["taxed_calmar"]),
                "Obs SR (daily-ann)": fmt_num(r["g2_observed_sharpe"] * np.sqrt(252.0)),
            }
        )
    return out


def write_report(rows: list[dict[str, object]], plot_rows: list[dict[str, str]]) -> None:
    n_pass = sum(1 for r in rows if r["overall_pass"])
    gate_fail_counts = {g: sum(1 for r in rows if not r["_gates"][g]["pass_gate"]) for g in GATE_KEYS}
    binding = sorted(gate_fail_counts.items(), key=lambda kv: kv[1], reverse=True)
    binding_text = ", ".join(f"{GATE_LABELS[g]} fails {c}/{len(rows)}" for g, c in binding if c)

    sections = [
        "# Phase 4 - Mandate Validation Gates (DIAGNOSTIC)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "Per `lrs/NEXT_STEPS.md`, Phase 4 is a diagnostic to decide whether the family deserves to continue - not a promotion. It runs the canonical mandate §5 gate suite on the 6 SMA200 bases (3 SPY + 3 QQQ, each at its best-score lag), wrapping `market_lab.backtest.validation`. CAGR/MDD remain warning-only tiers, not gates `[advances_fin_ml, p.208-211]`.\n\n"
        f"DSR `n_trials = {N_TRIALS}` (direct lineage: Phase 2 2400 + 3A 324 + 3A-2 216 + 3C 936). The spun-off `studies/lrs/`/`letf-lab` sweeps are excluded (separate repo), so the truly-honest count is higher; {N_TRIALS} is the defensible in-repo figure `[advances_fin_ml, p.273-275]`. PBO trial matrix = the Phase 2 geometry grid at SMA200 (8 leverages x 5 risk-off x 5 vol = 200 configs/branch, fixed lag).\n\n"
        "## Executive Conclusion\n\n"
        f"Bases passing ALL seven gates (hard-block, zero bypass): **{n_pass}/{len(rows)}**. "
        f"{'Binding gates: ' + binding_text + '.' if binding_text else 'All gates passed for every base.'} "
        "Gate definitions: G1 PBO<0.5; G2 DSR p<0.05; G3 walk-forward >=6/8 OOS windows beat underlying (per-window MDD diagnostic, no cap); G4 single-block OOS (last 30%) Sharpe>0 and beats underlying; G5 FWD stress (post-2020) Sharpe>0; G6 stationary-bootstrap 99.9% CI low of annualized Sharpe >0; G7 cross-lib CAGR |delta|<=3pp `[advances_fin_ml, p.208-211, p.273-275]`, `[testing_tuning, p.318-320, p.327-335]`.\n\n"
        "## Source And Rules\n\n"
        "| Item | Value |\n|---|---|\n"
        "| Data | `data/testfolio/cache/history.parquet` (close-only equity curves) |\n"
        "| Strategy | SMA200 LRS base (signal = SMA200 & vol_gate), after-tax weekly |\n"
        f"| DSR n_trials | {N_TRIALS} (direct lineage) |\n"
        f"| PBO matrix | Phase 2 geometry grid @ SMA200, lag {PBO_LAG}, ~200 configs/branch |\n"
        f"| Walk-forward | is={WF_IS_SIZE}d / oos={WF_OOS_SIZE}d / step={WF_STEP}d, >=8 windows, >=6/8 beat underlying |\n"
        "| Bootstrap | stationary block, 99.9% CI, block 21, 5000 resamples |\n"
        "| Verdict | G1 AND G2 AND ... AND G7 (hard-block) |\n\n",
    ]
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    sections.append(
        "## Gate Results (per base)\n\n"
        + md_table(gate_table_rows(rows), ["Branch", "Base", "G1 PBO", "G2 DSR p", "G3 WF", "G4 OOS", "G5 FWD", "G6 Boot", "G7 xlib", "Overall"])
    )
    sections.append(
        "## Metrics (warning-only tiers, NOT gates)\n\n"
        + md_table(metrics_table_rows(rows), ["Branch", "Base", "L", "Lag", "CAGR", "MDD", "Sharpe", "Calmar", "Obs SR (daily-ann)"])
    )
    verdict = (
        "No base passes all seven gates - the LRS family does NOT clear the mandate validation gates. Consistent with the restart's prior (geometry is the driver; 3C fragility; the repo's 113/113 honest-FAIL history), record the family as a research-only, negative-leaning line and close/shelve it pending new literature or regime. No mandate change."
        if n_pass == 0
        else f"{n_pass} base(s) pass all seven gates. This is a diagnostic pass only - it does NOT auto-promote; any allocation change would require a separate explicit decision under the mandate."
    )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Bases passing all 7 gates? | {n_pass}/{len(rows)}. |\n"
        f"| Binding (most-failed) gates? | {binding_text or 'none'}. |\n"
        "| Did we promote anything? | No - diagnostic only. |\n"
        "| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |\n\n"
        f"{verdict} `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`, `[leverage_for_the_long_run, p.4-7]`.\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    contexts = {name: build_context(branch) for name, branch in BRANCHES.items()}
    pbo_matrices = {name: build_pbo_matrix(ctx) for name, ctx in contexts.items()}
    rows: list[dict[str, object]] = []
    for base in BASE_SPECS:
        ctx = contexts[str(base["branch"])]
        rows.append(evaluate_base(ctx, base, pbo_matrices[str(base["branch"])]))

    csv_rows = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
    pd.DataFrame(csv_rows).to_csv(CSV, index=False)
    plot_rows = make_plots(rows)
    write_report(rows, plot_rows)

    n_pass = sum(1 for r in rows if r["overall_pass"])
    print(f"Phase 4: {len(rows)} bases; {n_pass} pass all 7 gates; n_trials={N_TRIALS}")
    for r in rows:
        flags = "".join("P" if r[f"g{i}_pass"] else "F" for i in range(1, 8))
        print(f"  {r['base_name']:14s} G1-7={flags} overall={'PASS' if r['overall_pass'] else 'FAIL'} "
              f"(PBO {r['g1_pbo']:.3f}, DSR p {r['g2_dsr_p']:.3f}, WF {int(r['g3_beat'])}/{int(r['g3_windows'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
