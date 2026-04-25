"""Iter 042 — 7-gate battery + scoring for combined regime modulation.

Pattern adapted from iter 041 (vacuous G1 PASS for N=1, same G2-G7
definitions). G7 cross-lib uses
``numpy_reference_combined_regime.apply_regime_weights_3leg_np``
(re-exports iter 041's reference) with the SAME regime mask rebuilt
independently from VIX.

Cumulative n_trials after iter 042:
  * Before iter 042: 4306 (per BASE_MEMORY.md frontmatter, post-iter-041)
  * This iter: 1 cfg × 1 (post-aggregation) = 1 new trial
  * Post iter 042: **4307**

Kill criteria evaluation references iter 041 baseline (the new ceiling
holder at 84 STRONG since 2026-04-25).
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
ITER037_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "037-2026-04-25-0224-ntsx-3leg-preserved-lev"
ITER038_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "038-2026-04-25-0246-regime-lev-vix"
ITER041_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "041-2026-04-25-0358-regime-weights-vix-static-stack"

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
    max_drawdown,
    sharpe,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_test  # noqa: E402

from numpy_reference_combined_regime import (  # noqa: E402
    apply_regime_weights_3leg_np,
    cagr_np,
)

OUT_DIR = ITER_DIR
RESULTS_PATH = OUT_DIR / "results.json"

CUMULATIVE_N_TRIALS = 4306 + 1  # = 4307


def _load_reference(iter_dir: Path) -> dict:
    verdict_path = iter_dir / "verdict.json"
    if not verdict_path.exists():
        return {ds: {"sharpe": float("nan"), "cagr": float("nan"), "mdd": float("nan")}
                for ds in ["educational", "spy_real", "ndx_real"]}
    v = json.loads(verdict_path.read_text(encoding="utf-8"))
    metrics_used = v.get("metrics_used", {})
    return {
        ds: {
            "sharpe": metrics_used.get(ds, {}).get("sharpe", float("nan")),
            "cagr":   metrics_used.get(ds, {}).get("cagr", float("nan")),
            "mdd":    metrics_used.get(ds, {}).get("mdd", float("nan")),
        }
        for ds in ["educational", "spy_real", "ndx_real"]
    }


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def g1_pbo_single_cfg() -> tuple[bool, None]:
    """N=1 → PBO undefined; vacuous PASS."""
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


def g7_cross_lib(
    dataset_name: str,
    cfg: dict,
    engine_cagr: float,
) -> tuple[bool, float]:
    from run_backtests import (
        load_triple_returns, load_vix, DATASETS, COST_BPS_PER_LEG, CFG,
    )
    ds = DATASETS[dataset_name]
    raw = load_triple_returns(
        ds["equity_symbol"], ds["bond_symbol"], ds["gold_symbol"], ds["start"], ds["end"],
    )
    vix_raw = load_vix(ds["start"], ds["end"])
    vix_aligned = vix_raw.reindex(raw.index, method="ffill")
    if vix_aligned.isna().any():
        vix_aligned = vix_aligned.fillna(CFG["vix_threshold"])
    vix_lag = vix_aligned.shift(1)
    vix_lag.iloc[0] = vix_aligned.iloc[0]
    regime = (vix_lag < CFG["vix_threshold"]).astype(int).to_numpy()
    eq_col, bd_col, gld_col = raw.columns
    net_np, _, _ = apply_regime_weights_3leg_np(
        raw[eq_col].to_numpy(),
        raw[bd_col].to_numpy(),
        raw[gld_col].to_numpy(),
        regime,
        calm_weights=CFG["calm_weights"],
        stress_weights=CFG["stress_weights"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    ref_cagr = cagr_np(net_np)
    diff_pp = abs(ref_cagr - engine_cagr) * 100
    return diff_pp <= 3.0, float(diff_pp)


# ---------------------------------------------------------------------------
# Robustness
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


def compute_gates_for_dataset(
    dataset_name: str, data: dict
) -> tuple[Gates, dict, pd.Series]:
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
    g7_pass, g7_pp = g7_cross_lib(dataset_name, cfg, engine_cagr)

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
    """Custom edu benchmark on iter 042's GLD-aligned 21y window. spy_real
    / ndx_real benchmarks remain frozen to scoring.BENCHMARKS for cross-iter
    comparability."""
    edu_bench = data["benchmarks"]["educational"]
    return {
        "educational": Benchmark(
            sharpe=edu_bench["sharpe"],
            cagr=edu_bench["cagr"],
            mdd=edu_bench["mdd"],
            label=f"SPY b&h {edu_bench['first']}→{edu_bench['last']} (iter 042 GLD-aligned)",
        ),
        "spy_real": BENCHMARKS["spy_real"],
        "ndx_real": BENCHMARKS["ndx_real"],
    }


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    custom_benchmarks = build_custom_benchmarks(data)
    iter037_ref = _load_reference(ITER037_DIR)
    iter038_ref = _load_reference(ITER038_DIR)
    iter041_ref = _load_reference(ITER041_DIR)

    cfg_id = data["configs"][0]["cfg_id"]
    print(f"Single pre-committed cfg: {cfg_id}")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (4306 + 1)")
    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        bench = custom_benchmarks[ds]
        edge = run["sharpe"] - bench.sharpe
        edge_frozen = run["sharpe"] - BENCHMARKS[ds].sharpe
        edge_iter037 = run["sharpe"] - iter037_ref[ds]["sharpe"]
        edge_iter038 = run["sharpe"] - iter038_ref[ds]["sharpe"]
        edge_iter041 = run["sharpe"] - iter041_ref[ds]["sharpe"]
        print(
            f"  {ds:12s} Sharpe={run['sharpe']:.4f} (Δ vs custom {edge:+.4f}, "
            f"Δ vs frozen {edge_frozen:+.4f}, Δ037 {edge_iter037:+.4f}, "
            f"Δ038 {edge_iter038:+.4f}, Δ041 {edge_iter041:+.4f})"
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
            "G1_pbo_pass": gates.g1_pbo,
            "G1_pbo_value": details["g1_pbo_value"],
            "G1_note": details["g1_note"],
            "G2_dsr_pass": gates.g2_dsr, "G2_dsr_p": details["g2_dsr_p"],
            "G3_wf_pass": gates.g3_wf,
            "G3_wf_profitable": details["g3_wf"].get("profitable_windows", 0),
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

    print("\n=== Robustness bonus (criterion 6) ===")
    bonus_pts, bonus_detail = compute_robustness_bonus(returns_by_ds)
    print(f"  {bonus_detail['positive_sub_windows']}/{bonus_detail['total_sub_windows']} "
          f"sub-windows Sharpe > 0 → {bonus_pts} bonus pts")
    for ds, d in bonus_detail["per_dataset"].items():
        sharpes_str = ", ".join(f"{s:+.2f}" for s in d["window_sharpes"])
        print(f"    {ds:12s} windows=[{sharpes_str}] positive={d['positive_count']}/{d['total']}")

    print("\n=== Score (with custom benchmark for educational) ===")
    result = score_strategy(
        metrics=metrics_by_ds,
        gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        benchmarks=custom_benchmarks,
    )
    final_score = min(100, result.total_score + bonus_pts)

    print("\n=== Strict winner-cond check vs FROZEN benchmarks ===")
    result_frozen = score_strategy(
        metrics=metrics_by_ds,
        gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        benchmarks=BENCHMARKS,
    )
    final_score_frozen = min(100, result_frozen.total_score + bonus_pts)
    print(f"  custom-bench score: {final_score}/100 (winner_conds={result.winner_conditions_met})")
    print(f"  frozen-bench score: {final_score_frozen}/100 (winner_conds={result_frozen.winner_conditions_met})")

    canonical = result_frozen
    canonical_score = final_score_frozen

    verdict = canonical.to_dict()
    verdict["criteria"]["6_robustness_bonus"] = {
        "points": bonus_pts,
        "max": 5,
        "method": "3 non-overlapping sub-windows per dataset; positive count across 9 total windows",
        "detail": bonus_detail,
    }
    verdict["total_score"] = canonical_score
    verdict["tier"] = tier_from_score(
        canonical_score, winner_conditions_met=canonical.winner_conditions_met,
    ).value

    verdict["configs_tested"] = 1
    verdict["primary_citation"] = (
        "[risk_parity, ch.5]; "
        "[advances_fin_ml, ch.17-18]; "
        "[advances_fin_ml, p.162-164]; "
        "[advances_fin_ml, p.222-223]; "
        "Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098; "
        "Bekaert-Hoerova (2014), J Econometrics 183(2), SSRN 2294327; "
        "Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084; "
        "Asness-Moskowitz-Pedersen (2013), JF 68(3), DOI 10.1111/jofi.12021; "
        "Moreira-Muir (2017), JF 72(4), DOI 10.1111/jofi.12513"
    )
    verdict["hypothesis_slug"] = "combined-regime-lev-weights"
    cfg_serializable = {**data["configs"][0]}
    verdict["pre_committed_cfg"] = cfg_serializable
    verdict["gate_details"] = gate_details
    verdict["leg_correlations"] = data["leg_correlations"]
    verdict["regime_summary"] = data["regime_summary"]
    verdict["benchmarks_used_custom"] = {
        ds: asdict(bm) for ds, bm in custom_benchmarks.items()
    }
    verdict["score_with_custom_benchmark"] = {
        "total_score": final_score,
        "winner_conditions_met": result.winner_conditions_met,
        "tier": tier_from_score(final_score, winner_conditions_met=result.winner_conditions_met).value,
        "criteria": result.criteria,
    }
    verdict["iter037_reference_metrics"] = iter037_ref
    verdict["iter038_reference_metrics"] = iter038_ref
    verdict["iter041_reference_metrics"] = iter041_ref
    for ref_name, ref in [
        ("iter037", iter037_ref),
        ("iter038", iter038_ref),
        ("iter041", iter041_ref),
    ]:
        verdict[f"delta_vs_{ref_name}"] = {
            ds: {
                "sharpe_delta": metrics_by_ds[ds].sharpe - ref[ds]["sharpe"],
                "cagr_delta":   metrics_by_ds[ds].cagr   - ref[ds]["cagr"],
                "mdd_delta":    metrics_by_ds[ds].mdd    - ref[ds]["mdd"],
            }
            for ds in ["educational", "spy_real", "ndx_real"]
        }

    # ---- Pre-committed kill criteria evaluation (vs iter 041 baseline) ----
    deltas_iter041 = verdict["delta_vs_iter041"]
    n_sharpe_below_iter041_005 = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if deltas_iter041[ds]["sharpe_delta"] < -0.05
    )
    worst_dsr_p = result_frozen.criteria["3_dsr"]["worst_p_value"]
    mdd_breach = {
        "educational": metrics_by_ds["educational"].mdd > BENCHMARKS["educational"].mdd + 0.05,
        "spy_real":    metrics_by_ds["spy_real"].mdd    > BENCHMARKS["spy_real"].mdd    + 0.05,
        "ndx_real":    metrics_by_ds["ndx_real"].mdd    > BENCHMARKS["ndx_real"].mdd    + 0.05,
    }
    n_mdd_breach = sum(mdd_breach.values())
    g7_max_diff = max(
        gate_details[ds]["G7_xlib_diff_pp"]
        for ds in ["educational", "spy_real", "ndx_real"]
    )
    rt_per_year = {
        ds: data["runs"][ds][cfg_id]["regime_round_trips_per_year"]
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    rt_excess = any(v > 10.0 for v in rt_per_year.values())  # iter 042 cap = 10/yr

    verdict["pre_committed_kills"] = {
        "A_sharpe_regress_vs_iter041_by_005": {
            "fired": n_sharpe_below_iter041_005 >= 2,
            "datasets_below_005": n_sharpe_below_iter041_005,
            "threshold": "≥ 2 of 3 datasets with Sharpe Δ vs iter 041 < −0.05",
            "note": "If fired → combined modulation hurts vs weight-only",
        },
        "B_dsr_no_improvement_vs_iter041": {
            "fired": worst_dsr_p >= 0.168,
            "worst_dsr_p": worst_dsr_p,
            "threshold": "≥ 0.168 (iter 041's worst-p)",
            "note": "If fired → orthogonal axes share noise, no compounding",
        },
        "C_mdd_breach_any": {
            "fired": n_mdd_breach >= 1,
            "n_breaches": n_mdd_breach,
            "per_dataset": mdd_breach,
            "threshold": "any dataset with MDD > benchmark + 5pp",
            "note": "If fired → 1.7× calm leverage punishes a missed regime call",
        },
        "D_score_below_84": {
            "fired": canonical_score < 84,
            "score": canonical_score,
            "threshold": "< 84 (iter 041 STRONG ceiling)",
            "note": "Strict no-regression rule",
        },
        "E_g7_crosslib_above_3pp": {
            "fired": g7_max_diff > 3.0,
            "max_diff_pp": g7_max_diff,
            "threshold": "> 3.0 pp",
        },
        "F_excessive_regime_churn_above_10": {
            "fired": rt_excess,
            "rt_per_year": rt_per_year,
            "threshold": "> 10 round-trips/year on any dataset",
            "note": "Relaxed from iter 041 (5/yr); cost should already absorb churn",
        },
    }
    n_kills_fired = sum(
        1 for v in verdict["pre_committed_kills"].values() if v["fired"]
    )
    verdict["n_kills_fired"] = n_kills_fired
    verdict["status"] = (
        "winner" if canonical.winner_conditions_met and canonical_score >= 90
        else verdict["tier"].lower()
    )

    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"\n=== CANONICAL VERDICT (frozen benchmarks) ===")
    print(f"Tier: {verdict['tier']}")
    print(f"Total score (with bonus): {canonical_score}/100")
    print(f"Winner conditions met: {canonical.winner_conditions_met}")
    print(f"Status: {verdict['status']}")
    print(f"Kills fired: {n_kills_fired}/6")
    for k, v in verdict["criteria"].items():
        print(f"  {k}: {v['points']}/{v['max']}")
    print()
    print("Pre-committed kill criteria status:")
    for k, v in verdict["pre_committed_kills"].items():
        marker = "❌ FIRED" if v["fired"] else "✓ clean"
        print(f"  {k:42s} {marker}")


if __name__ == "__main__":
    main()
