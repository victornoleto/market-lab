"""Iter 013 — 7-gate battery + scoring for meta-labeling pipeline.

Mirrors iter 009's harness with G7 extended to the meta-labeling
numpy-reference parity check.

Cumulative n_trials after iter 013:
  * Before iter 013: 4252 (per BASE_MEMORY.md frontmatter after iter 012)
  * This iter: 1 meta-cfg × 1 blend-cfg × 3 datasets = 3 new trials
  * Post iter 013: **4255**
"""

from __future__ import annotations

import json
import sys
import warnings
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    module=r"sklearn\..*",
)

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]

sys.path.insert(0, str(ROOT / "studies" / "strategy_hunt_loop"))
sys.path.insert(0, str(ITER_DIR))

from scoring import (  # noqa: E402
    BENCHMARKS,
    Benchmark,
    DatasetMetrics,
    Gates,
    score_strategy,
    tier_from_score,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    max_drawdown, sharpe,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_test  # noqa: E402

from meta_labeling_numpy_reference import apply_blend_with_meta_np  # noqa: E402


OUT_DIR = ITER_DIR
RESULTS_PATH = OUT_DIR / "results.json"
CUMULATIVE_N_TRIALS = 4252 + 3  # = 4255


# ---------------------------------------------------------------------------
# Gate implementations (same as iter 009; G7 uses iter 013 numpy ref)
# ---------------------------------------------------------------------------


def g1_pbo_single_cfg() -> tuple[bool, None]:
    """N=1 combined meta × blend → PBO undefined. Vacuous PASS."""
    return True, None


def g2_dsr(returns: np.ndarray, cumulative_n_trials: int) -> tuple[bool, float]:
    r = dsr_test(returns, n_trials=cumulative_n_trials)
    return (r.p_value < 0.05, r.p_value)


def g3_walk_forward(returns: pd.Series) -> tuple[bool, dict]:
    n = len(returns)
    if n < 8:
        return False, {"reason": "too few bars"}
    block_size = n // 8
    profitable = 0
    details = []
    for i in range(8):
        start = i * block_size
        end = start + block_size if i < 7 else n
        block = returns.iloc[start:end]
        if len(block) < 2:
            continue
        block_eq = (1 + block).cumprod()
        block_sharpe = sharpe(block)
        block_mdd = max_drawdown(block_eq)
        is_prof = block_sharpe > 0 and block_mdd < 0.25
        if is_prof:
            profitable += 1
        details.append({
            "window": i,
            "sharpe": float(block_sharpe),
            "mdd": float(block_mdd),
            "profitable": is_prof,
        })
    return profitable >= 6, {"profitable_windows": profitable, "windows": details}


def g4_oos_split(returns: pd.Series) -> tuple[bool, float]:
    split = int(len(returns) * 0.7)
    oos = returns.iloc[split:]
    sr = sharpe(oos)
    return sr > 0, float(sr)


def g5_forward_post2020(returns: pd.Series) -> tuple[bool, float]:
    post = returns[returns.index >= pd.Timestamp("2020-01-01")]
    if len(post) < 20:
        return False, 0.0
    sr = sharpe(post)
    return sr > 0, float(sr)


def g6_bootstrap_ci_low(returns: np.ndarray) -> tuple[bool, float]:
    r = np.asarray(returns, dtype=float)
    if len(r) < 30:
        return False, float("nan")
    rng = np.random.default_rng(42)
    n = len(r)
    block_mean = 5
    p = 1.0 / block_mean
    n_resamples = 5000
    sharpes = np.empty(n_resamples)
    for k in range(n_resamples):
        idx = np.empty(n, dtype=np.int64)
        idx[0] = rng.integers(0, n)
        restarts = rng.random(n) < p
        for t in range(1, n):
            if restarts[t]:
                idx[t] = rng.integers(0, n)
            else:
                idx[t] = (idx[t - 1] + 1) % n
        resampled = r[idx]
        sigma = resampled.std(ddof=0)
        if sigma <= 1e-12:
            sharpes[k] = 0.0
        else:
            sharpes[k] = resampled.mean() / sigma * np.sqrt(252)
    ci_low = float(np.quantile(sharpes, 0.0005))
    return ci_low > 0, ci_low


def g7_cross_lib(dataset_name: str, engine_cagr: float) -> tuple[bool, float]:
    """Numpy-reference CAGR parity check for meta-labeled pipeline."""
    import importlib.util as _ilu
    spec = _ilu.spec_from_file_location(
        "iter013_run_backtests", ITER_DIR / "run_backtests.py"
    )
    module = _ilu.module_from_spec(spec)
    spec.loader.exec_module(module)
    BLEND_CFG = module.BLEND_CFG
    COST_BPS_PER_LEG = module.COST_BPS_PER_LEG
    DATASETS = module.DATASETS
    META_CFG_loc = module.META_CFG
    load_paired_returns = module.load_paired_returns
    load_vix = module.load_vix

    ds = DATASETS[dataset_name]
    raw = load_paired_returns(
        ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"]
    )
    vix = load_vix(raw.index)
    eq_col, bd_col = raw.columns

    net_np = apply_blend_with_meta_np(
        raw[eq_col].to_numpy(), raw[bd_col].to_numpy(), vix.to_numpy(),
        target_vol=BLEND_CFG["target_vol"],
        lookback=BLEND_CFG["lookback"],
        max_leverage=BLEND_CFG["max_leverage"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
        train_window=META_CFG_loc["train_window"],
        retrain_cadence=META_CFG_loc["retrain_cadence"],
        warmup_bars=META_CFG_loc["warmup_bars"],
        decision_threshold=META_CFG_loc["decision_threshold"],
        random_state=META_CFG_loc["random_state"],
    )
    # CAGR from numpy stream.
    eq_np = np.cumprod(1.0 + net_np)
    n = len(net_np)
    ref_cagr = float(eq_np[-1] ** (252.0 / n) - 1.0)
    diff_pp = abs(ref_cagr - engine_cagr) * 100
    return diff_pp <= 3.0, float(diff_pp)


# ---------------------------------------------------------------------------
# Robustness bonus (criterion 6)
# ---------------------------------------------------------------------------


def robustness_sub_window_sharpe(returns: pd.Series) -> list[float]:
    n = len(returns)
    third = n // 3
    segs = [
        returns.iloc[0:third],
        returns.iloc[third:2 * third],
        returns.iloc[2 * third:],
    ]
    return [float(sharpe(s)) if len(s) > 1 else 0.0 for s in segs]


def compute_robustness_bonus(
    per_dataset_returns: dict[str, pd.Series],
) -> tuple[int, dict]:
    details: dict[str, dict] = {}
    total_windows = 0
    positive_windows = 0
    for ds, returns in per_dataset_returns.items():
        per_window = robustness_sub_window_sharpe(returns)
        positives = sum(1 for sr in per_window if sr > 0)
        total_windows += len(per_window)
        positive_windows += positives
        details[ds] = {
            "window_sharpes": per_window,
            "positive_count": positives,
            "total": len(per_window),
        }
    if total_windows == 0:
        pts = 0
    else:
        frac = positive_windows / total_windows
        pts = int(np.floor(5 * frac + 1e-9)) if frac < 1.0 else 5
    pts = max(0, min(5, pts))
    summary = {
        "total_sub_windows": total_windows,
        "positive_sub_windows": positive_windows,
        "fraction_positive": positive_windows / total_windows if total_windows else 0.0,
        "bonus_awarded": pts,
        "per_dataset": details,
    }
    return pts, summary


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


def compute_gates_for_dataset(dataset_name: str, data: dict) -> tuple[Gates, dict, pd.Series]:
    cfg_id = next(iter(data["runs"][dataset_name].keys()))
    series = data["returns_series"][dataset_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    rets = pd.Series(series["net_returns"], index=idx)
    cfg = data["runs"][dataset_name][cfg_id]
    engine_cagr = cfg["cagr"]

    g1_pass, g1_val = g1_pbo_single_cfg()
    g2_pass, g2_p = g2_dsr(rets.to_numpy(), CUMULATIVE_N_TRIALS)
    g3_pass, g3_det = g3_walk_forward(rets)
    g4_pass, g4_sr = g4_oos_split(rets)
    g5_pass, g5_sr = g5_forward_post2020(rets)
    g6_pass, g6_ci = g6_bootstrap_ci_low(rets.to_numpy())
    g7_pass, g7_pp = g7_cross_lib(dataset_name, engine_cagr)

    gates = Gates(
        g1_pbo=g1_pass, g2_dsr=g2_pass, g3_wf=g3_pass, g4_oos=g4_pass,
        g5_fwd=g5_pass, g6_bootstrap=g6_pass, g7_crosslib=g7_pass,
    )
    detail = {
        "g1_pbo_value": g1_val,
        "g1_note": "N=1 combined (meta+blend) → PBO undefined; vacuous PASS",
        "g2_dsr_p": g2_p,
        "g3_wf": g3_det,
        "g4_oos_sharpe": g4_sr,
        "g5_fwd_sharpe": g5_sr,
        "g6_bootstrap_ci_low": g6_ci,
        "g7_cross_lib_diff_pp": g7_pp,
        "dsr_p_value": g2_p,
    }
    return gates, detail, rets


def build_custom_benchmarks(data: dict) -> dict[str, Benchmark]:
    edu_bench = data["benchmarks"]["educational"]
    return {
        "educational": Benchmark(
            sharpe=edu_bench["sharpe"], cagr=edu_bench["cagr"], mdd=edu_bench["mdd"],
            label=f"SPY b&h {edu_bench['first']}→{edu_bench['last']} (iter 013 TLT-aligned)",
        ),
        "spy_real": BENCHMARKS["spy_real"],
        "ndx_real": BENCHMARKS["ndx_real"],
    }


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    custom_benchmarks = build_custom_benchmarks(data)

    cfg_id = data["combined_cfg_id"]
    print(f"Single pre-committed combined cfg: {cfg_id}")
    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        bench = custom_benchmarks[ds]
        edge = run["sharpe"] - bench.sharpe
        print(
            f"  {ds:12s} Sharpe={run['sharpe']:.4f} "
            f"(Δ={edge:+.4f} vs bench {bench.sharpe:.4f} "
            f"[{bench.label}])"
        )

    gates_by_ds: dict[str, Gates] = {}
    metrics_by_ds: dict[str, DatasetMetrics] = {}
    gate_details: dict[str, dict] = {}
    returns_by_ds: dict[str, pd.Series] = {}

    for ds in ["educational", "spy_real", "ndx_real"]:
        print(f"\n=== Gates: {ds} ===")
        gates, details, rets = compute_gates_for_dataset(ds, data)
        returns_by_ds[ds] = rets
        run = data["runs"][ds][cfg_id]
        metrics_by_ds[ds] = DatasetMetrics(
            sharpe=run["sharpe"], cagr=run["cagr"], mdd=run["mdd"],
            dsr_p_value=details["dsr_p_value"],
        )
        gates_by_ds[ds] = gates
        gate_details[ds] = {
            "cfg_id": cfg_id,
            "n_passed": gates.n_passed,
            "G1_pbo_pass": gates.g1_pbo, "G1_pbo_value": details["g1_pbo_value"],
            "G1_note": details["g1_note"],
            "G2_dsr_pass": gates.g2_dsr, "G2_dsr_p": details["g2_dsr_p"],
            "G3_wf_pass": gates.g3_wf,
            "G3_wf_profitable": details["g3_wf"].get("profitable_windows", 0),
            "G4_oos_pass": gates.g4_oos, "G4_oos_sharpe": details["g4_oos_sharpe"],
            "G5_fwd_pass": gates.g5_fwd, "G5_fwd_sharpe": details["g5_fwd_sharpe"],
            "G6_boot_pass": gates.g6_bootstrap, "G6_boot_ci_low": details["g6_bootstrap_ci_low"],
            "G7_xlib_pass": gates.g7_crosslib, "G7_xlib_diff_pp": details["g7_cross_lib_diff_pp"],
        }
        print(f"  gates passed: {gates.n_passed}/7")
        flags = [
            ("G1 PBO", gates.g1_pbo, "N=1 undef"),
            ("G2 DSR p", gates.g2_dsr, f"{details['g2_dsr_p']:.4f}"),
            ("G3 WF", gates.g3_wf, f"{details['g3_wf'].get('profitable_windows', 0)}/8"),
            ("G4 OOS Sh", gates.g4_oos, f"{details['g4_oos_sharpe']:+.3f}"),
            ("G5 FWD Sh", gates.g5_fwd, f"{details['g5_fwd_sharpe']:+.3f}"),
            ("G6 boot CI", gates.g6_bootstrap, f"{details['g6_bootstrap_ci_low']:+.3f}"),
            ("G7 xlib pp", gates.g7_crosslib, f"{details['g7_cross_lib_diff_pp']:.4f}"),
        ]
        for name, passed, val in flags:
            print(f"    {name:12s} {'PASS' if passed else 'FAIL'} ({val})")

    print("\n=== Robustness bonus (criterion 6) ===")
    bonus_pts, bonus_detail = compute_robustness_bonus(returns_by_ds)
    print(f"  {bonus_detail['positive_sub_windows']}/{bonus_detail['total_sub_windows']} "
          f"sub-windows Sharpe > 0 → {bonus_pts} bonus pts")
    for ds, d in bonus_detail["per_dataset"].items():
        sharpes = ", ".join(f"{s:+.2f}" for s in d["window_sharpes"])
        print(f"    {ds:12s} windows=[{sharpes}] positive={d['positive_count']}/{d['total']}")

    print("\n=== Score ===")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS}")
    result = score_strategy(
        metrics=metrics_by_ds, gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        benchmarks=custom_benchmarks,
    )
    final_score = min(100, result.total_score + bonus_pts)

    verdict = result.to_dict()
    verdict["criteria"]["6_robustness_bonus"] = {
        "points": bonus_pts, "max": 5,
        "method": "3 non-overlapping sub-windows per dataset; positive count",
        "detail": bonus_detail,
    }
    verdict["total_score"] = final_score
    verdict["tier"] = tier_from_score(
        final_score, winner_conditions_met=result.winner_conditions_met
    ).value

    verdict["configs_tested"] = 1
    verdict["primary_citation"] = (
        "[advances_fin_ml, ch.3, p.50-56] (meta-labeling); [advances_fin_ml, p.162-164] (no-lookahead); "
        "[regime_change, ch.2]; [systematic_trading, ch.12]; [risk_parity, p.10-11, ch.1]; "
        "Moreira & Muir (2017), JoF 72(4); López de Prado (2018) AFML, Wiley, ISBN 978-1119482086."
    )
    verdict["hypothesis_slug"] = "meta-labeling-blend"
    verdict["pre_committed_cfg"] = {
        "blend": data["blend_cfg"],
        "meta": data["meta_cfg"],
        "combined_cfg_id": cfg_id,
    }
    verdict["gate_details"] = gate_details
    verdict["leg_correlations"] = data["leg_correlations"]
    verdict["benchmarks_used_custom"] = {
        ds: asdict(bm) for ds, bm in custom_benchmarks.items()
    }
    verdict["iter008_reference_metrics"] = {
        "educational": {"sharpe": 0.8651, "cagr": 0.1349, "mdd": 0.3721},
        "spy_real":    {"sharpe": 1.0001, "cagr": 0.1608, "mdd": 0.3721},
        "ndx_real":    {"sharpe": 1.0211, "cagr": 0.1790, "mdd": 0.3721},
    }
    verdict["deltas_vs_iter008"] = {
        ds: {
            "sharpe_delta": metrics_by_ds[ds].sharpe - verdict["iter008_reference_metrics"][ds]["sharpe"],
            "cagr_delta": metrics_by_ds[ds].cagr - verdict["iter008_reference_metrics"][ds]["cagr"],
            "mdd_delta": metrics_by_ds[ds].mdd - verdict["iter008_reference_metrics"][ds]["mdd"],
        }
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    verdict["meta_diagnostics_summary"] = {
        ds: {
            "gate_fire_rate": data["runs"][ds][cfg_id]["gate_fire_rate"],
            "p_act_mean": data["runs"][ds][cfg_id]["p_act_mean"],
            "p_act_std": data["runs"][ds][cfg_id]["p_act_std"],
            "gate_bottom20_overlap_frac": data["runs"][ds][cfg_id]["gate_bottom20_overlap_frac"],
            "label_base_rate": data["runs"][ds][cfg_id]["label_base_rate"],
            "turnover_annual": data["runs"][ds][cfg_id]["turnover_annual"],
        }
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    verdict["status"] = (
        "winner" if result.winner_conditions_met and final_score >= 90
        else verdict["tier"].lower()
    )

    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"\nTier: {verdict['tier']}")
    print(f"Total score (with bonus): {final_score}/100")
    print(f"Winner conditions met: {result.winner_conditions_met}")
    for k, v in verdict["criteria"].items():
        print(f"  {k}: {v['points']}/{v['max']}")

    print("\n=== Kill criteria post-mortem ===")
    kills = []
    edu_sharpe = metrics_by_ds["educational"].sharpe
    spy_sharpe = metrics_by_ds["spy_real"].sharpe
    ndx_sharpe = metrics_by_ds["ndx_real"].sharpe
    iter008 = verdict["iter008_reference_metrics"]
    spy_delta = spy_sharpe - iter008["spy_real"]["sharpe"]
    ndx_delta = ndx_sharpe - iter008["ndx_real"]["sharpe"]
    # Kill #1: Sharpe regresses on BOTH real slots by > 0.02
    if spy_delta < -0.02 and ndx_delta < -0.02:
        kills.append(
            f"Kill #1 spy_Δ={spy_delta:+.3f} AND ndx_Δ={ndx_delta:+.3f} both < −0.02"
        )
    # Kill #2: CAGR < 0.75 × bench on any 2 of 3
    floor_counts = 0
    for ds, floor in [
        ("educational", 0.75 * data["benchmarks"]["educational"]["cagr"]),
        ("spy_real", 0.75 * BENCHMARKS["spy_real"].cagr),
        ("ndx_real", 0.75 * BENCHMARKS["ndx_real"].cagr),
    ]:
        if metrics_by_ds[ds].cagr < floor:
            floor_counts += 1
            kills.append(
                f"Kill #2 {ds} CAGR {metrics_by_ds[ds].cagr:.2%} < 0.75× bench {floor:.2%}"
            )
    # Kill #3: score < 70
    if final_score < 70:
        kills.append(f"Kill #3 final_score {final_score} < 70")
    # Kill #4: degenerate classifier (p_act std < 0.05 on ≥ 2 datasets)
    low_std = 0
    for ds in ["educational", "spy_real", "ndx_real"]:
        std = data["runs"][ds][cfg_id]["p_act_std"]
        if std < 0.05:
            low_std += 1
    if low_std >= 2:
        kills.append(f"Kill #4 degenerate classifier on {low_std}/3 datasets")
    # Kill #5: cross-lib > 3 pp
    for ds in ["educational", "spy_real", "ndx_real"]:
        pp = gate_details[ds]["G7_xlib_diff_pp"]
        if pp > 3.0:
            kills.append(f"Kill #5 {ds} xlib_diff {pp:.2f} pp > 3")
    if kills:
        print("  TRIGGERED:")
        for k in kills:
            print(f"    - {k}")
    else:
        print("  NONE triggered.")
    verdict["kill_criteria_triggered"] = kills
    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
