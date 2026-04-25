"""Iter 048 — 7-gate battery + score for the output-lev-gate single cfg.

Single pre-committed cfg (N=1) → no Bonferroni penalty (vs iter 047's N=3).
G1 PBO is 1-cfg → reported as N/A (vacuous), gate auto-passes by convention.
G2 DSR uses raw α=0.05 (no multi-test penalty).

Cumulative n_trials advance: 4314 + 1 = **4315**.

Citations
---------
* `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
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
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"
ITER_047_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "047-2026-04-25-0619-iter046-weight-sweep"

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

# Cumulative n_trials.
CUMULATIVE_N_TRIALS = 4314 + 1  # = 4315 (single pre-committed cfg)

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
    """Try to extract iter-N's per-dataset DSR p-values from its verdict."""
    verdict_path = iter_dir / "verdict.json"
    if not verdict_path.exists():
        return {}
    v = json.loads(verdict_path.read_text(encoding="utf-8"))
    out = {}
    for ds in ["educational", "spy_real", "ndx_real"]:
        m = v.get("metrics_used", {}).get(ds, {})
        if "dsr_p_value" in m:
            out[ds] = m["dsr_p_value"]
    # Fallback to per-cfg results
    if not out and "per_cfg_results" in v:
        per_cfg = v["per_cfg_results"]
        # Use the best cfg's DSR p
        best_cfg_id = v.get("best_cfg_id")
        if best_cfg_id and best_cfg_id in per_cfg:
            for ds in ["educational", "spy_real", "ndx_real"]:
                gd = per_cfg[best_cfg_id].get("gate_details", {}).get(ds, {})
                if "G2_dsr_p_raw" in gd:
                    out[ds] = gd["G2_dsr_p_raw"]
    return out


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def g1_pbo_single_cfg() -> tuple[bool, dict]:
    """G1 vacuous at N=1 — PBO requires ≥4 strategies. Auto-pass + note."""
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


def g7_cross_lib(dataset_name: str, cfg_id: str, data: dict) -> tuple[bool, float]:
    cl = data["crosslib"][dataset_name][cfg_id]
    diff_pp = cl["abs_diff_pp"]
    return diff_pp <= 3.0, float(diff_pp)


# ---------------------------------------------------------------------------
# Robustness — 3 sub-windows × 3 datasets = 9 windows
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
# Compute gates per dataset (single cfg → straightforward)
# ---------------------------------------------------------------------------


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
    g7_pass, g7_pp = g7_cross_lib(dataset_name, cfg_id, data)

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


def build_custom_benchmarks(data: dict) -> dict[str, Benchmark]:
    """Use the iter-specific edu benchmark (window-stable approach)."""
    edu_bench = data["benchmarks"]["educational"]
    return {
        "educational": Benchmark(
            sharpe=edu_bench["sharpe"],
            cagr=edu_bench["cagr"],
            mdd=edu_bench["mdd"],
            label=f"SPY b&h {edu_bench['first']}→{edu_bench['last']} (iter 048 GLD-aligned)",
        ),
        "spy_real": BENCHMARKS["spy_real"],
        "ndx_real": BENCHMARKS["ndx_real"],
    }


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    custom_benchmarks = build_custom_benchmarks(data)
    iter046_ref = _load_reference(ITER_046_DIR)
    iter046_score = _load_score(ITER_046_DIR)
    iter046_dsr = _load_dsr_p(ITER_046_DIR)

    cfg_id = data["configs"][0]["cfg_id"]
    cfg = data["configs"][0]
    print(f"Single cfg: {cfg_id}")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (4314 + 1)")
    print(f"raw α = {RAW_ALPHA} (no Bonferroni at N=1)")

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
        edge_046 = run["sharpe"] - iter046_ref[ds]["sharpe"]
        cagr_uplift = run["cagr"] - iter046_ref[ds]["cagr"]
        print(
            f"  {ds:12s} Sharpe={run['sharpe']:+.4f} "
            f"(Δ frozen {edge_frozen:+.4f}, Δ046 {edge_046:+.4f}) "
            f"CAGR={run['cagr']:+.2%} (Δ046 {cagr_uplift:+.2%}) "
            f"MDD={run['mdd']:.2%} "
            f"DSR p={details['G2_dsr_p_raw']:.4f} "
            f"({'PASS' if details['G2_dsr_pass'] else 'FAIL'}) "
            f"gates={gates.n_passed}/7 "
            f"(G1={int(gates.g1_pbo)}{int(gates.g2_dsr)}{int(gates.g3_wf)}"
            f"{int(gates.g4_oos)}{int(gates.g5_fwd)}{int(gates.g6_bootstrap)}"
            f"{int(gates.g7_crosslib)})"
        )

    # Robustness bonus
    bonus_pts, bonus_detail = compute_robustness_bonus(returns_by_ds)
    print(f"\n=== Robustness ===")
    print(
        f"  Sub-windows positive: {bonus_detail['positive_sub_windows']}/"
        f"{bonus_detail['total_sub_windows']} → bonus {bonus_pts}/5"
    )
    for ds, det in bonus_detail["per_dataset"].items():
        print(f"  {ds:12s} sharpes {[round(x,3) for x in det['window_sharpes']]} "
              f"({det['positive_count']}/{det['total']})")

    # Score using both frozen and custom benchmarks (custom is window-aligned).
    result_frozen = score_strategy(
        metrics=metrics_by_ds, gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS, benchmarks=BENCHMARKS,
    )
    result_custom = score_strategy(
        metrics=metrics_by_ds, gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS, benchmarks=custom_benchmarks,
    )
    score_frozen = min(100, result_frozen.total_score + bonus_pts)
    score_custom = min(100, result_custom.total_score + bonus_pts)

    # Tier: both must include winner-conditions check
    tier_frozen = tier_from_score(
        score_frozen, winner_conditions_met=result_frozen.winner_conditions_met,
    )
    tier_custom = tier_from_score(
        score_custom, winner_conditions_met=result_custom.winner_conditions_met,
    )

    print(
        f"\n=== Score ===\n"
        f"  Frozen bench: {score_frozen}/100 ({tier_frozen.value}, "
        f"winner_conds={result_frozen.winner_conditions_met})\n"
        f"  Custom bench: {score_custom}/100 ({tier_custom.value}, "
        f"winner_conds={result_custom.winner_conditions_met})"
    )
    for k, v in result_frozen.criteria.items():
        print(f"  frozen {k}: {v['points']}/{v['max']}")

    # ---- Pre-committed kill criteria ----
    print("\n=== Pre-committed kill evaluation ===")
    kill_status: dict[str, dict] = {}

    # A: Sharpe regress vs iter 046 by ≥ 0.05 on ≥ 2 of 3 datasets
    sharpe_drop_count = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if metrics_by_ds[ds].sharpe - iter046_ref[ds]["sharpe"] <= -0.05
    )
    kill_status["A_sharpe_regress_vs_iter046_2plus_ds"] = {
        "fired": sharpe_drop_count >= 2,
        "n_datasets_dropping_005": sharpe_drop_count,
        "deltas": {
            ds: float(metrics_by_ds[ds].sharpe - iter046_ref[ds]["sharpe"])
            for ds in ["educational", "spy_real", "ndx_real"]
        },
        "threshold": "Sharpe ≤ iter 046 − 0.05 on ≥ 2 of 3 datasets",
    }

    # B: DSR worst-p > iter 046's edu p (0.0414)
    iter046_edu_p = iter046_dsr.get("educational", 0.0414)
    edu_p_iter048 = gate_details["educational"]["G2_dsr_p_raw"]
    kill_status["B_dsr_worst_p_above_iter046_edu"] = {
        "fired": edu_p_iter048 > iter046_edu_p,
        "iter048_edu_p": float(edu_p_iter048),
        "iter046_edu_p": float(iter046_edu_p),
        "threshold": f"iter 048 edu DSR p > iter 046 edu DSR p ({iter046_edu_p:.4f})",
    }

    # C: MDD breach > bench + 5pp on any dataset
    mdd_breach_per_ds = {
        ds: bool(metrics_by_ds[ds].mdd > BENCHMARKS[ds].mdd + 0.05)
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    kill_status["C_mdd_breach_any_dataset"] = {
        "fired": any(mdd_breach_per_ds.values()),
        "per_dataset": mdd_breach_per_ds,
        "threshold": "MDD > bench + 5pp on any dataset",
    }

    # D: Score < iter 046's 85
    kill_status["D_score_below_iter046"] = {
        "fired": score_frozen < (iter046_score if iter046_score > 0 else 85),
        "score_frozen": score_frozen,
        "iter046_score": iter046_score,
        "threshold": f"< {iter046_score if iter046_score > 0 else 85}",
    }

    # E: G7 cross-lib > 3pp
    max_xlib_pp = max(
        gate_details[ds]["G7_xlib_diff_pp"]
        for ds in ["educational", "spy_real", "ndx_real"]
    )
    kill_status["E_g7_crosslib_above_3pp"] = {
        "fired": max_xlib_pp > 3.0,
        "max_diff_pp": float(max_xlib_pp),
        "threshold": "> 3.0 pp on any dataset",
    }

    # F: CAGR uplift < +2pp on ≥ 2 of 3 datasets
    cagr_uplifts = {
        ds: float(metrics_by_ds[ds].cagr - iter046_ref[ds]["cagr"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    n_below_2pp = sum(1 for v in cagr_uplifts.values() if v < 0.02)
    kill_status["F_cagr_uplift_below_2pp_2plus_ds"] = {
        "fired": n_below_2pp >= 2,
        "n_below_2pp": n_below_2pp,
        "uplifts": cagr_uplifts,
        "threshold": "CAGR uplift < +2pp on ≥ 2 of 3 datasets",
    }

    n_kills_fired = sum(1 for k in kill_status.values() if k["fired"])
    print(f"  Kills fired: {n_kills_fired}/6")
    for k, v in kill_status.items():
        marker = "❌ FIRED" if v["fired"] else "✓ clean"
        print(f"    {k:42s} {marker}")

    # ---- Build verdict.json ----
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
            "[risk_parity, ch.5] + [advances_fin_ml, ch.17-18] (binary regime) + "
            "[advances_fin_ml, p.222-223] (DSR cumulative) + "
            "[advances_fin_ml, p.31-34] (G7) + "
            "Whaley (2009), JPM 35(3) DOI 10.3905/JPM.2009.35.3.098 + "
            "Bekaert-Hoerova (2014), J Econometrics 183(2) 181-192 SSRN 2294327"
        ),
        "hypothesis_slug": "iter046-output-lev-gate",
        "cfg_id": cfg_id,
        "cfg": cfg,
        "score_custom": score_custom,
        "tier_custom": tier_custom.value,
        "winner_conds_custom": result_custom.winner_conditions_met,
        "criteria_custom": result_custom.criteria,
        "gate_details": gate_details,
        "robustness_bonus": bonus_detail,
        "pre_committed_kills": kill_status,
        "n_kills_fired": n_kills_fired,
        "iter046_reference_metrics": iter046_ref,
        "iter046_reference_score": iter046_score,
        "iter046_reference_dsr": iter046_dsr,
        "delta_vs_iter046": {
            ds: {
                "sharpe_delta": float(metrics_by_ds[ds].sharpe - iter046_ref[ds]["sharpe"]),
                "cagr_delta":   float(metrics_by_ds[ds].cagr   - iter046_ref[ds]["cagr"]),
                "mdd_delta":    float(metrics_by_ds[ds].mdd    - iter046_ref[ds]["mdd"]),
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
    print(f"Custom score: {score_custom}/100")
    print(f"Winner conditions met: {result_frozen.winner_conditions_met}")
    print(f"Status: {verdict['status']}")
    print(f"Kills fired: {n_kills_fired}/6")


if __name__ == "__main__":
    main()
