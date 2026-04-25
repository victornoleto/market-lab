"""Iter 067 — 7-gate battery + score for the σ⁻² variance-target overlay (cap=1.0).

Single pre-committed cfg `iter064_vt_cap10_lookback21_target_full` (N=1).
G1 PBO is vacuous at N=1.  G2 DSR uses raw α=0.05.

Cumulative n_trials advance: 4336 + 1 = **4337**.

Citations
---------
* `[advances_fin_ml, p.208-211]` — PBO via CSCV.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
* Moreira-Muir (2017) JoF 72(4) — σ⁻² scaling.
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
ITER_064_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "064-2026-04-25-1315-iter058-qqq-trend-substitution"

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

CUMULATIVE_N_TRIALS = 4336 + 1  # = 4337
RAW_ALPHA = 0.05


def _load_iter064_score() -> int:
    p = ITER_064_DIR / "verdict.json"
    if not p.exists():
        return 90
    return int(json.loads(p.read_text())["total_score"])


def _load_iter064_metrics() -> dict:
    p = ITER_064_DIR / "verdict.json"
    if not p.exists():
        return {}
    v = json.loads(p.read_text())
    return v.get("metrics_used", {})


def _load_iter064_dsr() -> dict:
    p = ITER_064_DIR / "verdict.json"
    if not p.exists():
        return {}
    v = json.loads(p.read_text())
    return {
        ds: v.get("metrics_used", {}).get(ds, {}).get("dsr_p_value")
        for ds in ["educational", "spy_real", "ndx_real"]
    }


def g1_pbo_single_cfg() -> tuple[bool, dict]:
    return True, {
        "pbo_value": float("nan"),
        "n_combinations": 0,
        "small_n_warning": "N=1 cfg — PBO vacuous; pass by convention",
    }


def g2_dsr_raw(returns: np.ndarray, n_trials: int) -> tuple[bool, float]:
    r = dsr_test(returns, n_trials=n_trials)
    return float(r.p_value) < RAW_ALPHA, float(r.p_value)


def g3_walk_forward(returns: pd.Series) -> tuple[bool, dict]:
    n = len(returns)
    if n < 8:
        return False, {"reason": "too few bars"}
    block = n // 8
    profitable = 0
    details = []
    for i in range(8):
        start = i * block
        end = start + block if i < 7 else n
        b = returns.iloc[start:end]
        if len(b) < 2:
            continue
        s = float(sharpe(b))
        m = float(max_drawdown((1 + b).cumprod()))
        ok = s > 0 and m < 0.25
        if ok:
            profitable += 1
        details.append({"window": i, "sharpe": s, "mdd": m, "profitable": ok})
    return profitable >= 6, {"profitable_windows": profitable, "windows": details}


def g4_oos_split(returns: pd.Series) -> tuple[bool, float]:
    split = int(len(returns) * 0.7)
    s = float(sharpe(returns.iloc[split:]))
    return s > 0, s


def g5_forward_post2020(returns: pd.Series) -> tuple[bool, float]:
    post = returns[returns.index >= pd.Timestamp("2020-01-01")]
    if len(post) < 20:
        return False, 0.0
    s = float(sharpe(post))
    return s > 0, s


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
        rs = r[idx]
        sigma = rs.std(ddof=0)
        sharpes[k] = 0.0 if sigma <= 1e-12 else rs.mean() / sigma * np.sqrt(252)
    ci_low = float(np.quantile(sharpes, 0.0005))
    return ci_low > 0, ci_low


def g7_cross_lib(ds: str, data: dict) -> tuple[bool, float]:
    diff = float(data["crosslib"][ds]["abs_diff_pp"])
    return diff <= 3.0, diff


def robustness_sub_window_sharpe(returns: pd.Series) -> list[float]:
    n = len(returns)
    third = n // 3
    segs = [
        returns.iloc[0:third],
        returns.iloc[third:2 * third],
        returns.iloc[2 * third:],
    ]
    return [float(sharpe(s)) if len(s) > 1 else 0.0 for s in segs]


def compute_robustness_bonus(per_ds_returns: dict[str, pd.Series]) -> tuple[int, dict]:
    details = {}
    total = 0
    pos = 0
    for ds, r in per_ds_returns.items():
        sharpes = robustness_sub_window_sharpe(r)
        n_pos = sum(1 for s in sharpes if s > 0)
        total += len(sharpes)
        pos += n_pos
        details[ds] = {"window_sharpes": sharpes, "positive_count": n_pos, "total": len(sharpes)}
    if total == 0:
        pts = 0
    else:
        frac = pos / total
        pts = int(np.floor(5 * frac + 1e-9)) if frac < 1.0 else 5
    return max(0, min(5, pts)), {
        "total_sub_windows": total,
        "positive_sub_windows": pos,
        "fraction_positive": pos / total if total else 0.0,
        "bonus_awarded": pts,
        "per_dataset": details,
    }


def compute_per_dataset_gates(
    cfg_id: str, ds: str, data: dict
) -> tuple[Gates, dict, pd.Series]:
    s = data["returns_series"][ds][cfg_id]
    idx = pd.to_datetime(s["index"])
    rets = pd.Series(s["net_returns"], index=idx)

    g1_p, g1_d = g1_pbo_single_cfg()
    g2_p, p_val = g2_dsr_raw(rets.to_numpy(), CUMULATIVE_N_TRIALS)
    g3_p, g3_d = g3_walk_forward(rets)
    g4_p, g4_s = g4_oos_split(rets)
    g5_p, g5_s = g5_forward_post2020(rets)
    g6_p, g6_c = g6_bootstrap_ci_low(rets.to_numpy())
    g7_p, g7_d = g7_cross_lib(ds, data)

    gates = Gates(g1_pbo=g1_p, g2_dsr=g2_p, g3_wf=g3_p, g4_oos=g4_p,
                  g5_fwd=g5_p, g6_bootstrap=g6_p, g7_crosslib=g7_p)
    detail = {
        "G1_pbo_pass": g1_p, "G1_note": g1_d["small_n_warning"],
        "G2_dsr_pass": g2_p, "G2_dsr_p_raw": p_val, "G2_alpha_raw": RAW_ALPHA,
        "G3_wf_pass": g3_p, "G3_wf_profitable": g3_d.get("profitable_windows", 0),
        "G3_wf_windows": g3_d.get("windows", []),
        "G4_oos_pass": g4_p, "G4_oos_sharpe": g4_s,
        "G5_fwd_pass": g5_p, "G5_fwd_sharpe": g5_s,
        "G6_boot_pass": g6_p, "G6_boot_ci_low": g6_c,
        "G7_xlib_pass": g7_p, "G7_xlib_diff_pp": g7_d,
        "dsr_p_value": p_val,
    }
    return gates, detail, rets


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    cfg = data["configs"][0]
    cfg_id = cfg["cfg_id"]

    iter064_score = _load_iter064_score()
    iter064_metrics = _load_iter064_metrics()
    iter064_dsr = _load_iter064_dsr()

    print(f"Single cfg: {cfg_id}")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (= 4336 + 1)")
    print(f"raw α = {RAW_ALPHA} (no Bonferroni at N=1)")
    print(f"iter 064 reference score: {iter064_score}")

    gates_by_ds: dict[str, Gates] = {}
    metrics_by_ds: dict[str, DatasetMetrics] = {}
    gate_details: dict[str, dict] = {}
    returns_by_ds: dict[str, pd.Series] = {}

    print("\n=== Per-dataset gates ===")
    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        gates, detail, rets = compute_per_dataset_gates(cfg_id, ds, data)
        returns_by_ds[ds] = rets
        metrics_by_ds[ds] = DatasetMetrics(
            sharpe=run["sharpe"], cagr=run["cagr"], mdd=run["mdd"],
            dsr_p_value=detail["dsr_p_value"],
        )
        gates_by_ds[ds] = gates
        gate_details[ds] = detail
        edge_frozen = run["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds]
        edge_064 = run["sharpe"] - iter064_metrics.get(ds, {}).get("sharpe", 0.0)
        cagr_064 = run["cagr"] - iter064_metrics.get(ds, {}).get("cagr", 0.0)
        print(
            f"  {ds:12s} Sharpe={run['sharpe']:+.4f} "
            f"(Δ frozen {edge_frozen:+.4f}, Δ064 {edge_064:+.4f}) "
            f"CAGR={run['cagr']:+.2%} (Δ064 {cagr_064:+.2%}) "
            f"MDD={run['mdd']:.2%} "
            f"DSR p={detail['G2_dsr_p_raw']:.4f} "
            f"({'PASS' if detail['G2_dsr_pass'] else 'FAIL'}) "
            f"gates={gates.n_passed}/7 "
            f"(G1={int(gates.g1_pbo)}{int(gates.g2_dsr)}{int(gates.g3_wf)}"
            f"{int(gates.g4_oos)}{int(gates.g5_fwd)}{int(gates.g6_bootstrap)}"
            f"{int(gates.g7_crosslib)})"
        )

    bonus_pts, bonus_detail = compute_robustness_bonus(returns_by_ds)
    print(
        f"\n=== Robustness ===\n"
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
        f"\n=== Score ===\n  Frozen bench: {score_frozen}/100 "
        f"({tier_frozen.value}, winner_conds={result_frozen.winner_conditions_met})"
    )
    for k, v in result_frozen.criteria.items():
        print(f"  frozen {k}: {v['points']}/{v['max']}")

    # ---- Pre-committed kill evaluation ----
    print("\n=== Pre-committed kill evaluation ===")
    kill_status: dict[str, dict] = {}

    # A: Sharpe regress vs iter 064 by ≥ 0.05 on ≥ 2 ds
    sharpe_drop_count = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if metrics_by_ds[ds].sharpe - iter064_metrics.get(ds, {}).get("sharpe", 0.0) <= -0.05
    )
    kill_status["A_sharpe_regress_vs_iter064_005_2plus_ds"] = {
        "fired": sharpe_drop_count >= 2,
        "n_datasets_dropping_005": sharpe_drop_count,
        "deltas": {
            ds: float(metrics_by_ds[ds].sharpe - iter064_metrics.get(ds, {}).get("sharpe", 0.0))
            for ds in ["educational", "spy_real", "ndx_real"]
        },
        "threshold": "Sharpe ≤ iter 064 − 0.05 on ≥ 2 of 3 datasets",
    }

    # B: DSR worst-p ≥ 0.10 (2.5× iter 064's 0.039 ceiling)
    iter067_worst_p = max(gate_details[ds]["G2_dsr_p_raw"]
                           for ds in ["educational", "spy_real", "ndx_real"])
    iter064_worst_p_ref = max(v for v in iter064_dsr.values() if v is not None) if iter064_dsr else 0.0392
    kill_status["B_dsr_worst_p_above_010"] = {
        "fired": iter067_worst_p >= 0.10,
        "iter067_worst_p": float(iter067_worst_p),
        "iter064_worst_p": float(iter064_worst_p_ref),
        "threshold": "iter 067 worst DSR p ≥ 0.10",
    }

    # C: Score < 79
    kill_status["C_score_below_79"] = {
        "fired": score_frozen < 79,
        "score_frozen": score_frozen,
        "iter064_score": iter064_score,
        "threshold": "score < 79 (regression beyond PROMISING ceiling)",
    }

    # D: edu CAGR < 9.18%
    edu_cagr = float(metrics_by_ds["educational"].cagr)
    kill_status["D_edu_cagr_below_918"] = {
        "fired": edu_cagr < 0.0918,
        "edu_cagr": edu_cagr,
        "iter064_edu_cagr": float(iter064_metrics.get("educational", {}).get("cagr", 0.0949)),
        "threshold": "edu CAGR < 9.18% floor",
    }

    # E: G7 cross-lib > 0.5 pp
    max_xlib_pp = max(gate_details[ds]["G7_xlib_diff_pp"]
                      for ds in ["educational", "spy_real", "ndx_real"])
    kill_status["E_g7_crosslib_above_05pp"] = {
        "fired": max_xlib_pp > 0.5,
        "max_diff_pp": float(max_xlib_pp),
        "threshold": "> 0.5 pp on any dataset (engine bug)",
    }

    # F: corr(iter_067, iter_064) > 0.995 on ≥ 2 ds (overlay no-op)
    corrs = {
        ds: float(data["runs"][ds][cfg_id]["corr_overlay_064"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    n_high_corr = sum(1 for c in corrs.values() if c > 0.995)
    kill_status["F_corr_iter067_iter064_above_0995_2plus_ds"] = {
        "fired": n_high_corr >= 2,
        "n_datasets_above_0995": n_high_corr,
        "per_dataset": corrs,
        "threshold": "corr(067,064) > 0.995 on ≥ 2 of 3 (overlay no-op)",
    }

    # G: max(scale) > 1.0 + 1e-6 (cap violation)
    max_scales = {
        ds: float(data["runs"][ds][cfg_id]["scale_max"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    kill_status["G_cap_violation"] = {
        "fired": any(v > 1.0 + 1e-6 for v in max_scales.values()),
        "per_dataset": max_scales,
        "threshold": "scale > 1.0 + 1e-6 (implementation bug)",
    }

    # H: mean(scale) ≥ 0.99 (overlay never binds)
    mean_scales = {
        ds: float(data["runs"][ds][cfg_id]["scale_mean"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    n_no_bind = sum(1 for v in mean_scales.values() if v >= 0.99)
    kill_status["H_overlay_never_binds"] = {
        "fired": n_no_bind >= 2,
        "n_datasets_above_099": n_no_bind,
        "per_dataset": mean_scales,
        "threshold": "mean(scale) ≥ 0.99 on ≥ 2 of 3 (no-op)",
    }

    n_kills_fired = sum(1 for k in kill_status.values() if k["fired"])
    print(f"  Kills fired: {n_kills_fired}/8")
    for k, v in kill_status.items():
        marker = "❌ FIRED" if v["fired"] else "✓ clean"
        print(f"    {k:55s} {marker}")

    verdict = {
        "status": ("winner" if (result_frozen.winner_conditions_met and score_frozen >= 90)
                   else tier_frozen.value.lower()),
        "tier": tier_frozen.value,
        "total_score": score_frozen,
        "winner_conditions_met": result_frozen.winner_conditions_met,
        "criteria": result_frozen.criteria,
        "metrics_used": {ds: asdict(metrics_by_ds[ds]) for ds in metrics_by_ds},
        "benchmarks_used": {ds: asdict(BENCHMARKS[ds]) for ds in BENCHMARKS},
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "configs_tested": 1,
        "primary_citation": (
            "Moreira-Muir 2017 + [volatility_trading, p.218] + "
            "[advances_fin_ml, p.162-164] (no peek) + "
            "[advances_fin_ml, p.222-223] (DSR cumulative) + "
            "[advances_fin_ml, p.31-34] (G7) + "
            "iter 064 base preserved verbatim"
        ),
        "hypothesis_slug": "iter064-vol-target-cap10",
        "cfg_id": cfg_id,
        "cfg": cfg,
        "gate_details": gate_details,
        "robustness_bonus": bonus_detail,
        "pre_committed_kills": kill_status,
        "n_kills_fired": n_kills_fired,
        "iter064_reference_score": iter064_score,
        "iter064_reference_metrics": iter064_metrics,
        "iter064_reference_dsr": iter064_dsr,
        "delta_vs_iter064": {
            ds: {
                "sharpe_delta": float(
                    metrics_by_ds[ds].sharpe - iter064_metrics.get(ds, {}).get("sharpe", 0.0)
                ),
                "cagr_delta": float(
                    metrics_by_ds[ds].cagr - iter064_metrics.get(ds, {}).get("cagr", 0.0)
                ),
                "mdd_delta": float(
                    metrics_by_ds[ds].mdd - iter064_metrics.get(ds, {}).get("mdd", 0.0)
                ),
            }
            for ds in ["educational", "spy_real", "ndx_real"]
        },
    }
    verdict["criteria"]["6_robustness_bonus"] = {
        "points": bonus_pts, "max": 5,
        "method": "3 non-overlapping sub-windows per dataset; positive count across 9 windows",
        "detail": bonus_detail,
    }

    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8",
    )

    print(f"\n=== CANONICAL VERDICT ===")
    print(f"Tier: {verdict['tier']}")
    print(f"Total score: {score_frozen}/100")
    print(f"Winner conditions met: {result_frozen.winner_conditions_met}")
    print(f"Status: {verdict['status']}")
    print(f"Kills fired: {n_kills_fired}/8")


if __name__ == "__main__":
    main()
