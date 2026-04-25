"""Iter 053 — 7-gate battery + score for the iter 037 + iter 046 70/30 combo.

Single pre-committed cfg (N=1) → no Bonferroni penalty.
G1 PBO is 1-cfg → reported as N/A (vacuous), gate auto-passes by convention.
G2 DSR uses raw α=0.05 (no multi-test penalty).

Cumulative n_trials advance: 4319 + 1 = **4320**.

Citations
---------
* `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
* Markowitz (1952), JoF 7(1) — closed-form Sharpe identity.
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
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"
ITER_051_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "051-2026-04-25-0753-iter037-plus-iter026-w080"
ITER_052_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "052-2026-04-25-0822-iter041-plus-iter026-w082"

sys.path.insert(0, str(ROOT / "studies" / "strategy_hunt_loop"))
sys.path.insert(0, str(ITER_DIR))

from scoring import (  # noqa: E402
    BENCHMARKS,
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

CUMULATIVE_N_TRIALS = 4319 + 1  # = 4320
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
    cl = data["crosslib"][dataset_name]
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
    iter046_ref = _load_reference(ITER_046_DIR)
    iter051_ref = _load_reference(ITER_051_DIR)
    iter052_ref = _load_reference(ITER_052_DIR)
    iter037_score = _load_score(ITER_037_DIR)
    iter046_score = _load_score(ITER_046_DIR)
    iter051_score = _load_score(ITER_051_DIR)
    iter052_score = _load_score(ITER_052_DIR)

    cfg_id = data["configs"][0]["cfg_id"]
    cfg = data["configs"][0]
    print(f"Single cfg: {cfg_id}")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (4319 + 1)")
    print(f"raw α = {RAW_ALPHA} (no Bonferroni at N=1)")
    print(f"References: iter 037 score {iter037_score}, iter 046 score "
          f"{iter046_score}, iter 051 score {iter051_score}, iter 052 score "
          f"{iter052_score}")

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
        print(
            f"  {ds:12s} Sharpe={run['sharpe']:+.4f} (Δ frozen {edge_frozen:+.4f}) "
            f"CAGR={run['cagr']:+.2%} MDD={run['mdd']:.2%} "
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

    result = score_strategy(
        metrics=metrics_by_ds, gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS, benchmarks=BENCHMARKS,
    )
    score = min(100, result.total_score + bonus_pts)
    tier = tier_from_score(
        score, winner_conditions_met=result.winner_conditions_met,
    )

    print(
        f"\n=== Score ===\n"
        f"  Frozen bench: {score}/100 ({tier.value}, "
        f"winner_conds={result.winner_conditions_met})"
    )
    for k, v in result.criteria.items():
        print(f"  frozen {k}: {v['points']}/{v['max']}")

    # ---- iter 053 pre-committed kill criteria (from hypothesis.md) ----
    print("\n=== Pre-committed kill evaluation ===")
    kill_status: dict[str, dict] = {}

    # A: Combined Sharpe drops ≥ 0.10 vs Markowitz pre-screen on ≥ 2 ds
    prescreen_pred = {
        "educational": 1.029,
        "spy_real": 1.193,
        "ndx_real": 1.220,
    }
    sharpe_below_pred = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if metrics_by_ds[ds].sharpe < prescreen_pred[ds] - 0.10
    )
    kill_status["A_sharpe_below_prescreen_010_2plus_ds"] = {
        "fired": sharpe_below_pred >= 2,
        "n_datasets_below_prescreen_010": sharpe_below_pred,
        "predictions": prescreen_pred,
        "observed": {ds: float(metrics_by_ds[ds].sharpe) for ds in metrics_by_ds},
        "deltas": {
            ds: float(metrics_by_ds[ds].sharpe - prescreen_pred[ds])
            for ds in metrics_by_ds
        },
        "threshold": "Sharpe < pre-screen prediction − 0.10 on ≥ 2 of 3 datasets",
    }

    # B: DSR worst-p ≥ 0.10
    iter053_worst_p = max(
        gate_details[ds]["G2_dsr_p_raw"]
        for ds in ["educational", "spy_real", "ndx_real"]
    )
    kill_status["B_dsr_worst_p_above_010"] = {
        "fired": iter053_worst_p >= 0.10,
        "iter053_worst_p": float(iter053_worst_p),
        "per_dataset_p": {
            ds: gate_details[ds]["G2_dsr_p_raw"] for ds in gate_details
        },
        "threshold": "iter 053 worst DSR p ≥ 0.10",
    }

    # C: CAGR floor passes on < 3 of 3 datasets (pre-committed: predicted 3/3)
    cagr_floor = {"educational": 0.0918, "spy_real": 0.1198, "ndx_real": 0.1535}
    n_cagr_pass = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if metrics_by_ds[ds].cagr >= cagr_floor[ds]
    )
    kill_status["C_cagr_floor_below_3of3"] = {
        "fired": n_cagr_pass < 3,
        "n_passes": n_cagr_pass,
        "floors": cagr_floor,
        "observed_cagr": {ds: float(metrics_by_ds[ds].cagr) for ds in metrics_by_ds},
        "threshold": "CAGR floor passes on < 3 of 3 datasets (kill C as pre-committed)",
    }

    # D: Markowitz formula mispredicts observed Sharpe by ≥ 0.05 on ≥ 2 datasets
    residuals = {
        ds: float(data["runs"][ds][cfg_id]["markowitz_residual_sharpe"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    n_mispredict = sum(1 for r in residuals.values() if abs(r) >= 0.05)
    kill_status["D_markowitz_mispredicts_005_2plus_ds"] = {
        "fired": n_mispredict >= 2,
        "n_datasets_mispredicting_005": n_mispredict,
        "residuals": residuals,
        "threshold": "|observed S − formula S| ≥ 0.05 on ≥ 2 of 3 datasets",
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

    # F: corr(iter 037, iter 046) ≥ 0.85 on any dataset
    # PRE-FIRED by pre-screen (corr 0.93-0.96). Documented confirmation.
    corr_per_ds = {
        ds: float(data["runs"][ds][cfg_id]["corr_037_046"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    max_corr = max(corr_per_ds.values())
    kill_status["F_corr_037_046_above_085"] = {
        "fired": max_corr >= 0.85,
        "max_corr": max_corr,
        "per_dataset_corr": corr_per_ds,
        "threshold": "corr(iter 037, iter 046) ≥ 0.85 on any dataset (PRE-FIRED by pre-screen)",
    }

    n_kills_fired = sum(1 for k in kill_status.values() if k["fired"])
    print(f"  Kills fired: {n_kills_fired}/6")
    for k, v in kill_status.items():
        marker = "❌ FIRED" if v["fired"] else "✓ clean"
        print(f"    {k:48s} {marker}")

    verdict = {
        "status": "winner" if (result.winner_conditions_met and score >= 90) else tier.value.lower(),
        "tier": tier.value,
        "total_score": score,
        "winner_conditions_met": result.winner_conditions_met,
        "criteria": result.criteria,
        "metrics_used": {
            ds: asdict(metrics_by_ds[ds]) for ds in metrics_by_ds
        },
        "benchmarks_used": {ds: asdict(BENCHMARKS[ds]) for ds in BENCHMARKS},
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "configs_tested": 1,
        "primary_citation": (
            "[risk_parity, ch.5] (iter 037 base) + "
            "iter 046 = 0.5*iter 041 + 0.5*iter 039 (preserved) + "
            "Whaley 2009 JPM 35(3) (VIX regime modulator inside iter 041) + "
            "[volatility_trading, p.218] (iter 026 base architecture inside iter 039) + "
            "Markowitz (1952) JoF 7(1) (score-Pareto weight derivation) + "
            "[advances_fin_ml, p.222-223] (DSR cumulative) + "
            "[advances_fin_ml, p.31-34] (G7 parity)"
        ),
        "hypothesis_slug": "iter037-plus-iter046-w070",
        "cfg_id": cfg_id,
        "cfg": cfg,
        "gate_details": gate_details,
        "robustness_bonus": bonus_detail,
        "pre_committed_kills": kill_status,
        "n_kills_fired": n_kills_fired,
        "iter037_reference_metrics": iter037_ref,
        "iter046_reference_metrics": iter046_ref,
        "iter051_reference_metrics": iter051_ref,
        "iter052_reference_metrics": iter052_ref,
        "iter037_reference_score": iter037_score,
        "iter046_reference_score": iter046_score,
        "iter051_reference_score": iter051_score,
        "iter052_reference_score": iter052_score,
        "delta_vs_iter051_baseline": {
            ds: {
                "sharpe_delta": float(metrics_by_ds[ds].sharpe - iter051_ref[ds]["sharpe"]),
                "cagr_delta":   float(metrics_by_ds[ds].cagr   - iter051_ref[ds]["cagr"]),
                "mdd_delta":    float(metrics_by_ds[ds].mdd    - iter051_ref[ds]["mdd"]),
            }
            for ds in ["educational", "spy_real", "ndx_real"]
        },
        "delta_vs_iter046_topk1": {
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
    print(f"Total score (frozen + bonus): {score}/100")
    print(f"Winner conditions met: {result.winner_conditions_met}")
    print(f"Status: {verdict['status']}")
    print(f"Kills fired: {n_kills_fired}/6")


if __name__ == "__main__":
    main()
