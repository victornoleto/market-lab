"""Iter 022 — 7-gate battery + scoring for TOM-seasonality overlay.

Pattern mirrors iter 020/021: single pre-committed cfg → G1 vacuous
PASS (N=1), G2-G7 standard, G7 via numpy_reference_tom parity.

Cumulative n_trials:
  * Before iter 022: 4270 (per BASE_MEMORY frontmatter post-iter-021)
  * This iter adds: 1 cfg × 3 datasets = 3 new trials
  * Post iter 022: **4273**
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

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
    cagr as _cagr,
    max_drawdown,
    sharpe,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_test  # noqa: E402

from numpy_reference_tom import tom_static_stack_vm_numpy  # noqa: E402
from run_backtests import load_pair_returns, DATASETS, COST_BPS_PER_LEG  # noqa: E402

OUT_DIR = ITER_DIR
RESULTS_PATH = OUT_DIR / "results.json"

CUMULATIVE_N_TRIALS = 4270 + 1 * 3  # = 4273

# iter 016 frozen reference (for kill criteria + delta tables)
ITER016_REF = {
    "educational": {"sharpe": 0.9810, "cagr": 0.1508, "mdd": 0.3133},
    "spy_real":    {"sharpe": 1.1405, "cagr": 0.1779, "mdd": 0.2665},
    "ndx_real":    {"sharpe": 1.1861, "cagr": 0.2073, "mdd": 0.2323},
}


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def g1_pbo_single_cfg() -> tuple[bool, None]:
    return True, None


def g2_dsr(returns: np.ndarray, n_trials: int) -> tuple[bool, float]:
    r = dsr_test(returns, n_trials=n_trials)
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


def g7_cross_lib(
    dataset_name: str, cfg: dict, engine_cagr: float,
) -> tuple[bool, float]:
    """Cross-lib parity via numpy-only reference on same data."""
    ds = DATASETS[dataset_name]
    r = load_pair_returns(
        ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"],
    )
    eq_col, bd_col = r.columns

    net_np = tom_static_stack_vm_numpy(
        r[eq_col].to_numpy(), r[bd_col].to_numpy(),
        index=r.index,
        eq_weight_tom=cfg["eq_weight_tom"],
        eq_weight_mid=cfg["eq_weight_mid"],
        bd_weight_tom=cfg["bd_weight_tom"],
        bd_weight_mid=cfg["bd_weight_mid"],
        tom_last_n=cfg["tom_last_n"],
        tom_first_n=cfg["tom_first_n"],
        target_vol=cfg["target_vol"],
        lookback=cfg["lookback"],
        max_leverage=cfg["max_leverage"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq_curve = np.cumprod(1.0 + net_np)
    years = len(net_np) / 252.0
    ref_cagr = eq_curve[-1] ** (1.0 / years) - 1.0
    diff_pp = abs(float(ref_cagr) - engine_cagr) * 100
    return diff_pp <= 3.0, float(diff_pp)


def robustness_sub_window_sharpe(returns: pd.Series) -> list[float]:
    n = len(returns)
    third = n // 3
    segs = [
        returns.iloc[0:third],
        returns.iloc[third:2 * third],
        returns.iloc[2 * third:],
    ]
    return [float(sharpe(s)) if len(s) > 1 else 0.0 for s in segs]


def compute_robustness_bonus(per_dataset_returns: dict[str, pd.Series]) -> tuple[int, dict]:
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
    return pts, {
        "total_sub_windows": total_windows,
        "positive_sub_windows": positive_windows,
        "fraction_positive": positive_windows / total_windows if total_windows else 0.0,
        "bonus_awarded": pts,
        "per_dataset": details,
    }


def compute_gates_for_dataset(
    dataset_name: str, data: dict,
) -> tuple[Gates, dict, pd.Series]:
    cfg_id = next(iter(data["runs"][dataset_name].keys()))
    series = data["returns_series"][dataset_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    rets = pd.Series(series["net_returns"], index=idx)
    cfg = data["runs"][dataset_name][cfg_id]
    engine_cagr = cfg["cagr"]

    full_cfg = dict(data["configs"][0])

    g1_pass, g1_val = g1_pbo_single_cfg()
    g2_pass, g2_p = g2_dsr(rets.to_numpy(), CUMULATIVE_N_TRIALS)
    g3_pass, g3_det = g3_walk_forward(rets)
    g4_pass, g4_sr = g4_oos_split(rets)
    g5_pass, g5_sr = g5_forward_post2020(rets)
    g6_pass, g6_ci = g6_bootstrap_ci_low(rets.to_numpy())
    g7_pass, g7_pp = g7_cross_lib(dataset_name, full_cfg, engine_cagr)

    gates = Gates(
        g1_pbo=g1_pass, g2_dsr=g2_pass, g3_wf=g3_pass, g4_oos=g4_pass,
        g5_fwd=g5_pass, g6_bootstrap=g6_pass, g7_crosslib=g7_pass,
    )
    detail = {
        "g1_pbo_value": g1_val,
        "g1_note": "N=1 → PBO undefined; vacuous PASS (no grid, no overfit)",
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
    edu = data["benchmarks"]["educational"]
    return {
        "educational": Benchmark(
            sharpe=edu["sharpe"], cagr=edu["cagr"], mdd=edu["mdd"],
            label=f"SPY b&h {edu['first']}→{edu['last']} (IEF-aligned)",
        ),
        "spy_real": BENCHMARKS["spy_real"],
        "ndx_real": BENCHMARKS["ndx_real"],
    }


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    custom_benchmarks = build_custom_benchmarks(data)

    cfg_id = data["configs"][0]["cfg_id"]
    print(f"Single pre-committed cfg: {cfg_id}")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (4270 + 3)")
    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        bench_frozen = BENCHMARKS[ds].sharpe
        bench_custom = custom_benchmarks[ds].sharpe
        iter016 = ITER016_REF[ds]
        print(
            f"  {ds:12s} Sharpe={run['sharpe']:.4f} "
            f"(Δ vs custom {run['sharpe']-bench_custom:+.4f}, "
            f"Δ vs frozen {run['sharpe']-bench_frozen:+.4f}, "
            f"Δ vs iter016 {run['sharpe']-iter016['sharpe']:+.4f})"
        )
        print(
            f"     MDD={run['mdd']:.4f} (iter016 {iter016['mdd']:.4f}, "
            f"Δ={run['mdd']-iter016['mdd']:+.4f}pp)"
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
            "G3_wf_windows": details["g3_wf"].get("windows", []),
            "G4_oos_pass": gates.g4_oos, "G4_oos_sharpe": details["g4_oos_sharpe"],
            "G5_fwd_pass": gates.g5_fwd, "G5_fwd_sharpe": details["g5_fwd_sharpe"],
            "G6_boot_pass": gates.g6_bootstrap,
            "G6_boot_ci_low": details["g6_bootstrap_ci_low"],
            "G7_xlib_pass": gates.g7_crosslib,
            "G7_xlib_diff_pp": details["g7_cross_lib_diff_pp"],
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

    print("\n=== Robustness bonus ===")
    bonus_pts, bonus_detail = compute_robustness_bonus(returns_by_ds)
    print(
        f"  {bonus_detail['positive_sub_windows']}/"
        f"{bonus_detail['total_sub_windows']} sub-windows positive → "
        f"{bonus_pts} bonus pts"
    )
    for ds, d in bonus_detail["per_dataset"].items():
        sharpes = ", ".join(f"{s:+.2f}" for s in d["window_sharpes"])
        print(f"    {ds:12s} windows=[{sharpes}] positive={d['positive_count']}/{d['total']}")

    print("\n=== Score (custom educational benchmark) ===")
    result_custom = score_strategy(
        metrics=metrics_by_ds, gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        benchmarks=custom_benchmarks,
    )
    final_score_custom = min(100, result_custom.total_score + bonus_pts)

    print("\n=== Strict winner-cond check vs FROZEN benchmarks (canonical) ===")
    result_frozen = score_strategy(
        metrics=metrics_by_ds, gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        benchmarks=BENCHMARKS,
    )
    final_score_frozen = min(100, result_frozen.total_score + bonus_pts)
    print(f"  custom-bench score: {final_score_custom}/100 (winner_conds={result_custom.winner_conditions_met})")
    print(f"  frozen-bench score: {final_score_frozen}/100 (winner_conds={result_frozen.winner_conditions_met})")

    canonical = result_frozen
    canonical_score = final_score_frozen

    verdict = canonical.to_dict()
    verdict["criteria"]["6_robustness_bonus"] = {
        "points": bonus_pts,
        "max": 5,
        "method": "3 non-overlapping sub-windows per dataset; positive count",
        "detail": bonus_detail,
    }
    verdict["total_score"] = canonical_score
    verdict["tier"] = tier_from_score(
        canonical_score, winner_conditions_met=canonical.winner_conditions_met,
    ).value
    verdict["configs_tested"] = 1
    verdict["primary_citation"] = (
        "[trading_systems_methods, p.479-481]; "
        "[risk_parity, p.10-11, ch.1]; "
        "[systematic_trading, p.40, ch.2]; "
        "Lakonishok & Smidt (1988) RFS; Etula et al (2020) JF; "
        "Kunkel et al (2003) IRFA; Moreira & Muir (2017)"
    )
    verdict["hypothesis_slug"] = "tom-seasonality-overlay"
    verdict["pre_committed_cfg"] = data["configs"][0]
    verdict["gate_details"] = gate_details
    verdict["leg_correlations"] = data["leg_correlations"]
    verdict["benchmarks_used_custom"] = {
        ds: asdict(bm) for ds, bm in custom_benchmarks.items()
    }
    verdict["score_with_custom_benchmark"] = {
        "total_score": final_score_custom,
        "winner_conditions_met": result_custom.winner_conditions_met,
        "tier": tier_from_score(
            final_score_custom, winner_conditions_met=result_custom.winner_conditions_met,
        ).value,
        "criteria": result_custom.criteria,
    }
    verdict["iter016_reference_metrics"] = ITER016_REF
    verdict["delta_vs_iter016"] = {
        ds: {
            "sharpe_delta": metrics_by_ds[ds].sharpe - ITER016_REF[ds]["sharpe"],
            "cagr_delta": metrics_by_ds[ds].cagr - ITER016_REF[ds]["cagr"],
            "mdd_delta": metrics_by_ds[ds].mdd - ITER016_REF[ds]["mdd"],
        }
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    verdict["tom_premium_raw"] = data.get("tom_premium_raw", {})
    verdict["tom_diagnostics_net"] = {
        ds: {
            "tom_bars_frac": data["runs"][ds][cfg_id]["tom_bars_frac"],
            "tom_net_mean_daily": data["runs"][ds][cfg_id]["tom_net_mean_daily"],
            "mid_net_mean_daily": data["runs"][ds][cfg_id]["mid_net_mean_daily"],
            "tom_net_ann_sharpe": data["runs"][ds][cfg_id]["tom_net_ann_sharpe"],
            "mid_net_ann_sharpe": data["runs"][ds][cfg_id]["mid_net_ann_sharpe"],
        }
        for ds in ["educational", "spy_real", "ndx_real"]
    }

    # Kill criteria (pre-committed in hypothesis.md)
    kill1_fails = sum(
        1 for v in verdict["tom_premium_raw"].values()
        if v["tom_minus_mid_bps"] <= 0
    )
    sharpe_not_improving = sum(
        1 for d in verdict["delta_vs_iter016"].values()
        if d["sharpe_delta"] <= 0.0
    )
    dsr_worst_p = max(
        metrics_by_ds[ds].dsr_p_value for ds in ["educational", "spy_real", "ndx_real"]
    )
    mdd_explodes_count = sum(
        1 for d in verdict["delta_vs_iter016"].values()
        if d["mdd_delta"] > 0.05
    )
    verdict["kill_criteria_check"] = {
        "kill_1_tom_premium_absent": {
            "criterion": "TOM-day mean equity return ≤ non-TOM-day mean on ≥ 2/3 datasets",
            "triggered": kill1_fails >= 2,
            "fails_count": kill1_fails,
        },
        "kill_2_no_sharpe_advance_vs_iter016": {
            "criterion": "Δ Sharpe ≤ 0.00 vs iter 016 on ≥ 2 of 3 ds",
            "triggered": sharpe_not_improving >= 2,
            "not_improving_count": sharpe_not_improving,
        },
        "kill_3_dsr_ceiling_not_penetrated": {
            "criterion": "DSR worst p ≥ 0.20 (no improvement over iter 016's 0.226)",
            "triggered": dsr_worst_p >= 0.20,
            "dsr_worst_p": dsr_worst_p,
        },
        "kill_4_mdd_explodes": {
            "criterion": "MDD > iter 016 + 5pp on ≥ 2 of 3 ds",
            "triggered": mdd_explodes_count >= 2,
            "explodes_count": mdd_explodes_count,
        },
    }
    verdict["any_kill_triggered"] = any(
        v["triggered"] for v in verdict["kill_criteria_check"].values()
    )
    verdict["status"] = (
        "winner" if canonical.winner_conditions_met and canonical_score >= 90
        else verdict["tier"].lower()
    )

    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8",
    )
    print(f"\n=== CANONICAL VERDICT (frozen benchmarks) ===")
    print(f"Tier: {verdict['tier']}")
    print(f"Total score (with bonus): {canonical_score}/100")
    print(f"Winner conditions met: {canonical.winner_conditions_met}")
    print(f"Status: {verdict['status']}")
    for k, v in verdict["criteria"].items():
        print(f"  {k}: {v['points']}/{v['max']}")
    print("\n=== Kill criteria ===")
    for k, v in verdict["kill_criteria_check"].items():
        icon = "✗ TRIGGERED" if v["triggered"] else "✓ clear"
        extra = ""
        if "dsr_worst_p" in v:
            extra = f" (p={v['dsr_worst_p']:.4f})"
        elif "fails_count" in v:
            extra = f" ({v['fails_count']}/3)"
        elif "not_improving_count" in v:
            extra = f" ({v['not_improving_count']}/3)"
        elif "explodes_count" in v:
            extra = f" ({v['explodes_count']}/3)"
        print(f"  {k}: {icon}{extra} — {v['criterion']}")
    print(f"\nAny kill triggered: {verdict['any_kill_triggered']}")


if __name__ == "__main__":
    main()
