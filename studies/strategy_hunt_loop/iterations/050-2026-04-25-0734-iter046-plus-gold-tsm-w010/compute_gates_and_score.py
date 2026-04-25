"""Iter 050 — 7-gate battery + score for the iter 046 + gold TSM (w=0.10) combo.

Single pre-committed cfg (N=1) → no Bonferroni penalty.
G1 PBO is 1-cfg → reported as N/A (vacuous), gate auto-passes by convention.
G2 DSR uses raw α=0.05 (no multi-test penalty).

Cumulative n_trials advance: 4316 + 1 = **4317**.

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
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"
ITER_049_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "049-2026-04-25-0705-iter046-plus-gold-tsm"

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

CUMULATIVE_N_TRIALS = 4316 + 1  # = 4317
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


def build_custom_benchmarks(data: dict) -> dict[str, Benchmark]:
    edu_bench = data["benchmarks"]["educational"]
    return {
        "educational": Benchmark(
            sharpe=edu_bench["sharpe"],
            cagr=edu_bench["cagr"],
            mdd=edu_bench["mdd"],
            label=f"SPY b&h {edu_bench['first']}→{edu_bench['last']} (iter 050 GLD-aligned)",
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
    iter049_score = _load_score(ITER_049_DIR)

    cfg_id = data["configs"][0]["cfg_id"]
    cfg = data["configs"][0]
    print(f"Single cfg: {cfg_id}")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (4316 + 1)")
    print(f"raw α = {RAW_ALPHA} (no Bonferroni at N=1)")
    print(f"iter 046 reference score: {iter046_score}")
    print(f"iter 049 prior score: {iter049_score}")

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
    result_custom = score_strategy(
        metrics=metrics_by_ds, gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS, benchmarks=custom_benchmarks,
    )
    score_frozen = min(100, result_frozen.total_score + bonus_pts)
    score_custom = min(100, result_custom.total_score + bonus_pts)

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

    # ---- iter 050 pre-committed kill criteria ----
    print("\n=== Pre-committed kill evaluation ===")
    kill_status: dict[str, dict] = {}

    # A: Combined Sharpe drops by ≥ 0.10 vs iter 046 on ≥ 2 datasets
    sharpe_drop_count = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if metrics_by_ds[ds].sharpe - iter046_ref[ds]["sharpe"] <= -0.10
    )
    kill_status["A_sharpe_regress_vs_iter046_010_2plus_ds"] = {
        "fired": sharpe_drop_count >= 2,
        "n_datasets_dropping_010": sharpe_drop_count,
        "deltas": {
            ds: float(metrics_by_ds[ds].sharpe - iter046_ref[ds]["sharpe"])
            for ds in ["educational", "spy_real", "ndx_real"]
        },
        "threshold": "Sharpe ≤ iter 046 − 0.10 on ≥ 2 of 3 datasets",
    }

    # B: DSR worst-p ≥ 0.10
    iter050_worst_p = max(
        gate_details[ds]["G2_dsr_p_raw"]
        for ds in ["educational", "spy_real", "ndx_real"]
    )
    kill_status["B_dsr_worst_p_above_010"] = {
        "fired": iter050_worst_p >= 0.10,
        "iter050_worst_p": float(iter050_worst_p),
        "iter046_worst_p": max(iter046_dsr.values()) if iter046_dsr else 0.0438,
        "threshold": "iter 050 worst DSR p ≥ 0.10 (doubling iter 046's worst)",
    }

    # C: Score < 84 (regression vs iter 046's 85)
    kill_status["C_score_below_84"] = {
        "fired": score_frozen < 84,
        "score_frozen": score_frozen,
        "iter046_score": iter046_score,
        "threshold": "score < 84 (iter 046 anchor regression)",
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

    # F: MDD increase > 1pp on ≥ 2 datasets
    mdd_deltas = {
        ds: float(metrics_by_ds[ds].mdd - iter046_ref[ds]["mdd"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    n_mdd_worse = sum(1 for d in mdd_deltas.values() if d > 0.01)
    kill_status["F_mdd_increase_2plus_ds"] = {
        "fired": n_mdd_worse >= 2,
        "n_datasets_with_mdd_worse_1pp": n_mdd_worse,
        "deltas": mdd_deltas,
        "threshold": "MDD - iter046 MDD > 0.01 on ≥ 2 of 3 datasets",
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
            "[advances_fin_ml, p.222-223] (DSR cumulative) + "
            "Markowitz (1952) JoF 7(1) (closed-form combo) + "
            "[risk_parity, ch.5] + [volatility_trading, p.218] (iter 046 base preserved) + "
            "[systematic_trading] (Carver TSM) + "
            "[advances_fin_ml, p.31-34] (G7) + "
            "Moskowitz-Ooi-Pedersen 2012 JFE 104(2) 228-250 DOI 10.1016/j.jfineco.2011.11.003"
        ),
        "hypothesis_slug": "iter046-plus-gold-tsm-w010",
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
        "iter049_reference_score": iter049_score,
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
