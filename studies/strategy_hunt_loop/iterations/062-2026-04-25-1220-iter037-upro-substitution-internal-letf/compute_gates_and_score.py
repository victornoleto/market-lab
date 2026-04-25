"""Iter 062 — 7-gate battery + score for internal-LETF UPRO substitution.

Single pre-committed cfg (N=1) → no Bonferroni penalty.
G1 PBO is 1-cfg → reported as N/A (vacuous), gate auto-passes by convention.
G2 DSR uses raw α=0.05.
G7 cross-lib check uses ``crosslib_3leg`` slot from results.json (the
3-leg static stack). The synth-LETF formula has its own parity check
in ``crosslib_synth_letf`` (educational only) — also reported.

Cumulative n_trials advance: 4331 + 1 = **4332**.

Citations
---------
* `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
* `[leverage_for_the_long_run, p.19-25]` — Hsiao-Williams 2017 daily-reset LETF.
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
ITER_037_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "037-2026-04-25-0224-ntsx-3leg-preserved-lev"
ITER_058_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "058-2026-04-25-1044-hyg-credit-carry-3rd-stream"
ITER_061_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "061-2026-04-25-1154-iter037-eq075-plus-hyg-tsm"

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

OUT_DIR = ITER_DIR
RESULTS_PATH = OUT_DIR / "results.json"

CUMULATIVE_N_TRIALS = 4331 + 1  # = 4332
RAW_ALPHA = 0.05


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


def _load_score(iter_dir: Path) -> int:
    verdict_path = iter_dir / "verdict.json"
    if not verdict_path.exists():
        return -1
    v = json.loads(verdict_path.read_text(encoding="utf-8"))
    return int(v.get("total_score", -1))


def _load_dsr_p(iter_dir: Path) -> dict:
    verdict_path = iter_dir / "verdict.json"
    if not verdict_path.exists():
        return {}
    v = json.loads(verdict_path.read_text(encoding="utf-8"))
    out = {}
    for ds in ["educational", "spy_real", "ndx_real"]:
        m = v.get("metrics_used", {}).get(ds, {})
        if "dsr_p_value" in m and m["dsr_p_value"] is not None:
            out[ds] = m["dsr_p_value"]
    return out


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def g1_pbo_single_cfg() -> tuple[bool, dict]:
    return True, {
        "pbo_value": float("nan"),
        "n_combinations": 0,
        "small_n_warning": "N=1 cfg — PBO is vacuous; G1 reported as PASS (uninformative)",
        "note": "single pre-committed cfg (no grid); PBO not applicable",
    }


def g2_dsr_raw(returns: np.ndarray, n_trials: int) -> tuple[bool, float]:
    r = dsr_test(returns, n_trials=n_trials)
    p = float(r.p_value)
    return (p < RAW_ALPHA, p)


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


def g7_cross_lib(dataset_name: str, data: dict) -> tuple[bool, float]:
    cl = data["crosslib_3leg"][dataset_name]
    diff_pp = cl["abs_diff_pp"]
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


def compute_per_dataset_gates(
    cfg_id: str, dataset_name: str, data: dict,
) -> tuple[Gates, dict, pd.Series]:
    series = data["returns_series"][dataset_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    rets = pd.Series(series["net_returns"], index=idx)

    g1_pass, g1_det = g1_pbo_single_cfg()
    g2_pass, p_val = g2_dsr_raw(rets.to_numpy(), CUMULATIVE_N_TRIALS)
    g3_pass, g3_det = g3_walk_forward(rets)
    g4_pass, g4_sr = g4_oos_split(rets)
    g5_pass, g5_sr = g5_forward_post2020(rets)
    g6_pass, g6_ci = g6_bootstrap_ci_low(rets.to_numpy())
    g7_pass, g7_pp = g7_cross_lib(dataset_name, data)

    gates = Gates(
        g1_pbo=g1_pass, g2_dsr=g2_pass, g3_wf=g3_pass, g4_oos=g4_pass,
        g5_fwd=g5_pass, g6_bootstrap=g6_pass, g7_crosslib=g7_pass,
    )
    detail = {
        "cfg_id": cfg_id,
        "G1_pbo_pass": g1_pass,
        "G1_pbo_value": g1_det["pbo_value"],
        "G1_note": g1_det["small_n_warning"],
        "G2_dsr_pass": g2_pass,
        "G2_dsr_p_raw": p_val,
        "G2_alpha_raw": RAW_ALPHA,
        "G3_wf_pass": g3_pass,
        "G3_wf_profitable": g3_det.get("profitable_windows", 0),
        "G3_wf_windows": g3_det.get("windows", []),
        "G4_oos_pass": g4_pass,
        "G4_oos_sharpe": g4_sr,
        "G5_fwd_pass": g5_pass,
        "G5_fwd_sharpe": g5_sr,
        "G6_boot_pass": g6_pass,
        "G6_boot_ci_low": g6_ci,
        "G7_xlib_pass": g7_pass,
        "G7_xlib_diff_pp": g7_pp,
        "dsr_p_value": p_val,
    }
    return gates, detail, rets


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    iter037_ref = _load_reference(ITER_037_DIR)
    iter037_score = _load_score(ITER_037_DIR)
    iter037_dsr = _load_dsr_p(ITER_037_DIR)
    iter058_score = _load_score(ITER_058_DIR)
    iter058_dsr = _load_dsr_p(ITER_058_DIR)
    iter061_ref = _load_reference(ITER_061_DIR)
    iter061_score = _load_score(ITER_061_DIR)
    iter061_dsr = _load_dsr_p(ITER_061_DIR)

    cfg_id = data["configs"][0]["cfg_id"]
    cfg = data["configs"][0]
    print(f"Single cfg: {cfg_id}")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (4331 + 1)")
    print(f"raw α = {RAW_ALPHA} (no Bonferroni at N=1)")
    print(f"iter 037 reference score: {iter037_score}, "
          f"iter 058 score: {iter058_score}, iter 061 score: {iter061_score}")

    print("\n=== Per-dataset gates ===")
    gates_by_ds: dict[str, Gates] = {}
    metrics_by_ds: dict[str, DatasetMetrics] = {}
    gate_details: dict[str, dict] = {}
    returns_by_ds: dict[str, pd.Series] = {}

    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        gates, details, rets = compute_per_dataset_gates(cfg_id, ds, data)
        returns_by_ds[ds] = rets
        metrics_by_ds[ds] = DatasetMetrics(
            sharpe=run["sharpe"], cagr=run["cagr"], mdd=run["mdd"],
            dsr_p_value=details["dsr_p_value"],
        )
        gates_by_ds[ds] = gates
        gate_details[ds] = details
        edge_frozen = run["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds]
        edge_037 = run["sharpe"] - iter037_ref[ds]["sharpe"]
        edge_061 = run["sharpe"] - iter061_ref[ds]["sharpe"]
        cagr_uplift_037 = run["cagr"] - iter037_ref[ds]["cagr"]
        print(
            f"  {ds:12s} S={run['sharpe']:+.4f} "
            f"(Δ frozen {edge_frozen:+.4f}, Δ037 {edge_037:+.4f}, Δ061 {edge_061:+.4f}) "
            f"CAGR={run['cagr']:+.2%} (Δ037 {cagr_uplift_037:+.2%}) "
            f"MDD={run['mdd']:.2%} "
            f"DSR p={details['G2_dsr_p_raw']:.4f} "
            f"({'PASS' if details['G2_dsr_pass'] else 'FAIL'}) "
            f"gates={gates.n_passed}/7 "
            f"(G1={int(gates.g1_pbo)}{int(gates.g2_dsr)}{int(gates.g3_wf)}"
            f"{int(gates.g4_oos)}{int(gates.g5_fwd)}{int(gates.g6_bootstrap)}"
            f"{int(gates.g7_crosslib)})"
        )

    bonus_pts, bonus_detail = compute_robustness_bonus(returns_by_ds)
    print(f"\n=== Robustness ===")
    print(
        f"  Sub-windows positive: {bonus_detail['positive_sub_windows']}/"
        f"{bonus_detail['total_sub_windows']} → bonus {bonus_pts}/5"
    )
    for ds, det in bonus_detail["per_dataset"].items():
        print(f"  {ds:12s} sharpes {[round(x,3) for x in det['window_sharpes']]} "
              f"({det['positive_count']}/{det['total']})")

    result_frozen = score_strategy(
        metrics=metrics_by_ds, gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS, benchmarks=BENCHMARKS,
    )
    score_frozen = min(100, result_frozen.total_score + bonus_pts)
    tier_frozen = tier_from_score(
        score_frozen, winner_conditions_met=result_frozen.winner_conditions_met,
    )

    print(
        f"\n=== Score ===\n"
        f"  Frozen bench: {score_frozen}/100 ({tier_frozen.value}, "
        f"winner_conds={result_frozen.winner_conditions_met})"
    )
    for k, v in result_frozen.criteria.items():
        print(f"  {k}: {v['points']}/{v['max']}")

    # ---- iter 062 pre-committed kill criteria (6 kills) ----
    print("\n=== Pre-committed kill evaluation ===")
    kill_status: dict[str, dict] = {}

    # A: Combined Sharpe regress vs iter 037 by ≥ 0.10 on ≥ 2 datasets
    sharpe_drop_count = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if metrics_by_ds[ds].sharpe - iter037_ref[ds]["sharpe"] <= -0.10
    )
    kill_status["A_sharpe_regress_vs_iter037_010_2plus_ds"] = {
        "fired": sharpe_drop_count >= 2,
        "n_datasets_dropping_010": sharpe_drop_count,
        "deltas": {
            ds: float(metrics_by_ds[ds].sharpe - iter037_ref[ds]["sharpe"])
            for ds in ["educational", "spy_real", "ndx_real"]
        },
        "threshold": "Sharpe ≤ iter 037 − 0.10 on ≥ 2 of 3 datasets",
    }

    # B: DSR worst-p ≥ 0.222 (no improvement vs iter 037 baseline)
    iter062_worst_p = max(
        gate_details[ds]["G2_dsr_p_raw"]
        for ds in ["educational", "spy_real", "ndx_real"]
    )
    kill_status["B_dsr_worst_p_above_iter037_baseline"] = {
        "fired": iter062_worst_p >= 0.222,
        "iter062_worst_p": float(iter062_worst_p),
        "iter037_worst_p_baseline": 0.222,
        "iter037_worst_p_actual": max(iter037_dsr.values()) if iter037_dsr else 0.222,
        "iter058_worst_p": max(iter058_dsr.values()) if iter058_dsr else 0.0494,
        "iter061_worst_p": max(iter061_dsr.values()) if iter061_dsr else float("nan"),
        "threshold": "iter 062 worst DSR p ≥ 0.222 (iter 037 baseline)",
    }

    # C: Score < iter 037's 79 (anchor baseline)
    kill_status["C_score_below_iter037_baseline_79"] = {
        "fired": score_frozen < 79,
        "score_frozen": score_frozen,
        "iter037_score": iter037_score,
        "iter058_score": iter058_score,
        "iter061_score": iter061_score,
        "threshold": "score < 79 (iter 037 anchor baseline)",
    }

    # D: G7 cross-lib > 3pp on any dataset (3-leg stack)
    max_xlib_pp = max(
        gate_details[ds]["G7_xlib_diff_pp"]
        for ds in ["educational", "spy_real", "ndx_real"]
    )
    kill_status["D_g7_crosslib_above_3pp"] = {
        "fired": max_xlib_pp > 3.0,
        "max_diff_pp": float(max_xlib_pp),
        "synth_letf_diff_pp_educational": data["crosslib_synth_letf"].get(
            "educational", {"abs_diff_pp": 0.0})["abs_diff_pp"],
        "threshold": "> 3.0 pp on any dataset",
    }

    # E: MDD breach > bench+5pp on ≥ 2 datasets
    mdd_ceilings = {"educational": 0.6014, "spy_real": 0.3870, "ndx_real": 0.4012}
    mdd_breach = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if metrics_by_ds[ds].mdd > mdd_ceilings[ds]
    )
    kill_status["E_mdd_breach_2plus_ds"] = {
        "fired": mdd_breach >= 2,
        "n_datasets_breaching": mdd_breach,
        "per_dataset": {
            ds: {
                "mdd": float(metrics_by_ds[ds].mdd),
                "ceiling": mdd_ceilings[ds],
                "breach": metrics_by_ds[ds].mdd > mdd_ceilings[ds],
            }
            for ds in ["educational", "spy_real", "ndx_real"]
        },
        "threshold": "combined MDD > bench+5pp on ≥ 2 of 3 datasets",
    }

    # F: CAGR floor regress on ≥ 2 datasets (combined CAGR < 0.8×bench)
    bench_cagr = {"educational": 0.1147, "spy_real": 0.1497, "ndx_real": 0.1918}
    cagr_floor_fail = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if metrics_by_ds[ds].cagr < 0.8 * bench_cagr[ds]
    )
    kill_status["F_cagr_floor_fail_2plus_ds"] = {
        "fired": cagr_floor_fail >= 2,
        "n_datasets_failing_floor": cagr_floor_fail,
        "per_dataset": {
            ds: {
                "cagr": float(metrics_by_ds[ds].cagr),
                "floor": float(0.8 * bench_cagr[ds]),
                "passed": metrics_by_ds[ds].cagr >= 0.8 * bench_cagr[ds],
            }
            for ds in ["educational", "spy_real", "ndx_real"]
        },
        "threshold": "combined CAGR < 0.8×bench on ≥ 2 of 3 datasets",
    }

    n_kills_fired = sum(1 for k in kill_status.values() if k["fired"])
    print(f"  Kills fired: {n_kills_fired}/6")
    for k, v in kill_status.items():
        marker = "❌ FIRED" if v["fired"] else "✓ clean"
        print(f"    {k:48s} {marker}")

    verdict = {
        "status": "winner" if (result_frozen.winner_conditions_met and score_frozen >= 90) else tier_frozen.value.lower(),
        "tier": tier_frozen.value,
        "total_score": score_frozen,
        "winner_conditions_met": result_frozen.winner_conditions_met,
        "criteria": result_frozen.criteria,
        "metrics_used": {
            ds: asdict(metrics_by_ds[ds]) for ds in metrics_by_ds
        },
        "benchmarks_used": {ds: asdict(BENCHMARKS[ds]) for ds in BENCHMARKS},
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "configs_tested": 1,
        "primary_citation": (
            "[leverage_for_the_long_run, p.19-25] (Hsiao-Williams 2017 daily-reset LETF) + "
            "[risk_parity, ch.5] (preserved-NAV multi-leg stack, iter 037 architecture) + "
            "[advances_fin_ml, p.222-223] (DSR cumulative) + "
            "[advances_fin_ml, p.31-34] (G7 cross-lib parity)"
        ),
        "hypothesis_slug": "iter037-upro-substitution-internal-letf",
        "cfg_id": cfg_id,
        "cfg": cfg,
        "gate_details": gate_details,
        "robustness_bonus": bonus_detail,
        "pre_committed_kills": kill_status,
        "n_kills_fired": n_kills_fired,
        "iter037_reference_metrics": iter037_ref,
        "iter037_reference_score": iter037_score,
        "iter037_reference_dsr": iter037_dsr,
        "iter058_reference_score": iter058_score,
        "iter058_reference_dsr": iter058_dsr,
        "iter061_reference_metrics": iter061_ref,
        "iter061_reference_score": iter061_score,
        "iter061_reference_dsr": iter061_dsr,
        "delta_vs_iter037": {
            ds: {
                "sharpe_delta": float(metrics_by_ds[ds].sharpe - iter037_ref[ds]["sharpe"]),
                "cagr_delta":   float(metrics_by_ds[ds].cagr   - iter037_ref[ds]["cagr"]),
                "mdd_delta":    float(metrics_by_ds[ds].mdd    - iter037_ref[ds]["mdd"]),
            }
            for ds in ["educational", "spy_real", "ndx_real"]
        },
        "delta_vs_iter061": {
            ds: {
                "sharpe_delta": float(metrics_by_ds[ds].sharpe - iter061_ref[ds]["sharpe"]),
                "cagr_delta":   float(metrics_by_ds[ds].cagr   - iter061_ref[ds]["cagr"]),
                "mdd_delta":    float(metrics_by_ds[ds].mdd    - iter061_ref[ds]["mdd"]),
            }
            for ds in ["educational", "spy_real", "ndx_real"]
        },
    }
    verdict["criteria"]["6_robustness_bonus"] = {
        "points": bonus_pts,
        "max": 5,
        "method": "3 non-overlapping sub-windows per dataset; positive count across 9 windows",
        "detail": bonus_detail,
    }

    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8",
    )

    print(f"\n=== CANONICAL VERDICT ===")
    print(f"Tier: {verdict['tier']}")
    print(f"Total score (frozen + bonus): {score_frozen}/100")
    print(f"Winner conditions met: {result_frozen.winner_conditions_met}")
    print(f"Status: {verdict['status']}")
    print(f"Kills fired: {n_kills_fired}/6")


if __name__ == "__main__":
    main()
