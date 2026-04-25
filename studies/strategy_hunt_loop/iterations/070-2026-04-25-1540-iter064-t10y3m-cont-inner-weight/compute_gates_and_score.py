"""Iter 070 — 7-gate battery + score for the continuous T10Y3M inner-weight blend.

Single pre-committed cfg ``iter064_t10y3m_cont_alpha025_lb1260_w005_020``
(N=1). G1 PBO is vacuous at N=1. G2 DSR uses raw α=0.05.

Cumulative n_trials advance: 4339 + 1 = 4340.

Pre-committed kill criteria (see hypothesis.md §"Kill criteria"):

* A — Sharpe lift vs iter 064 < +0.02 on ≥ 2 ds (continuous gate fails to break 90 ceiling)
* B — DSR worst-p ≥ 0.05 (degrades from iter 069's 0.0429)
* C — Total score < 75 (drops below STRONG)
* D — edu CAGR < 9.18% (loses iter 064 unlock)
* E — G7 cross-lib > 0.5 pp (engine bug)
* F — corr(070, 064) > 0.995 on ≥ 2 ds (continuous gate inert vs iter 064 static)
* G — max|Σw - 1| > 1e-9 (composition bug)
* H — flips/yr < 1 OR > 100 on any ds (regime pathology — for continuous gate the upper
  bound here is more permissive since infinitesimal weight changes can register as flips;
  diagnostic but blocking)
* I — mean(w_qqqt) outside [0.08, 0.13] (continuous mapping doesn't preserve iter 064's
  static `w=0.10` time-mean → drift confounds with mechanism)
* J — corr(z_t10y3m, vix_lag) > 0.7 on ≥ 2 ds (T10Y3M signal not orthogonal to VIX)
* K — iter 070 Sharpe < iter 069 Sharpe on ≥ 2 ds (continuous regime fails to even
  match the binary baseline — granularity hypothesis empirically falsified)

Citations
---------
* `[advances_fin_ml, p.208-211]` — PBO via CSCV.
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
ITER_064_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "064-2026-04-25-1315-iter058-qqq-trend-substitution"
ITER_069_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "069-2026-04-25-1518-iter064-vix-inner-weight-reverse"

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

CUMULATIVE_N_TRIALS = 4339 + 1  # = 4340
RAW_ALPHA = 0.05


def _load_iter_score(iter_dir: Path) -> int:
    p = iter_dir / "verdict.json"
    if not p.exists():
        return 0
    return int(json.loads(p.read_text())["total_score"])


def _load_iter_metrics(iter_dir: Path) -> dict:
    p = iter_dir / "verdict.json"
    if not p.exists():
        return {}
    v = json.loads(p.read_text())
    return v.get("metrics_used", {})


def _load_iter_dsr(iter_dir: Path) -> dict:
    p = iter_dir / "verdict.json"
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

    iter064_score = _load_iter_score(ITER_064_DIR)
    iter064_metrics = _load_iter_metrics(ITER_064_DIR)
    iter064_dsr = _load_iter_dsr(ITER_064_DIR)
    iter069_score = _load_iter_score(ITER_069_DIR)
    iter069_metrics = _load_iter_metrics(ITER_069_DIR)

    print(f"Single cfg: {cfg_id}")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (= 4339 + 1)")
    print(f"raw α = {RAW_ALPHA} (no Bonferroni at N=1)")
    print(f"iter 064 reference score: {iter064_score}")
    print(f"iter 069 reference score: {iter069_score}")

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
        edge_069 = run["sharpe"] - iter069_metrics.get(ds, {}).get("sharpe", 0.0)
        cagr_064 = run["cagr"] - iter064_metrics.get(ds, {}).get("cagr", 0.0)
        print(
            f"  {ds:12s} Sharpe={run['sharpe']:+.4f} "
            f"(Δ frozen {edge_frozen:+.4f}, Δ064 {edge_064:+.4f}, Δ069 {edge_069:+.4f}) "
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

    # A: Sharpe lift vs iter 064 < +0.02 on ≥ 2 ds
    sharpe_lift_count = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if metrics_by_ds[ds].sharpe - iter064_metrics.get(ds, {}).get("sharpe", 0.0) >= 0.02
    )
    n_below_lift = 3 - sharpe_lift_count
    kill_status["A_sharpe_lift_vs_iter064_002_below_2plus_ds"] = {
        "fired": n_below_lift >= 2,
        "n_datasets_lifting_002": sharpe_lift_count,
        "n_datasets_below_002_lift": n_below_lift,
        "deltas_vs_064": {
            ds: float(metrics_by_ds[ds].sharpe - iter064_metrics.get(ds, {}).get("sharpe", 0.0))
            for ds in ["educational", "spy_real", "ndx_real"]
        },
        "threshold": "Sharpe lift vs iter 064 < +0.02 on ≥ 2 of 3 (continuous gate fails to break 90 ceiling)",
    }

    # B: DSR worst-p ≥ 0.05
    iter070_worst_p = max(gate_details[ds]["G2_dsr_p_raw"]
                          for ds in ["educational", "spy_real", "ndx_real"])
    iter069_worst_p_ref = max(v for v in _load_iter_dsr(ITER_069_DIR).values() if v is not None) if _load_iter_dsr(ITER_069_DIR) else 0.0429
    kill_status["B_dsr_worst_p_above_005"] = {
        "fired": iter070_worst_p >= 0.05,
        "iter070_worst_p": float(iter070_worst_p),
        "iter069_worst_p": float(iter069_worst_p_ref),
        "threshold": "iter 070 worst DSR p ≥ 0.05 (degrades from iter 069's 0.0429)",
    }

    # C: Score < 75 (drops below STRONG)
    kill_status["C_score_below_75"] = {
        "fired": score_frozen < 75,
        "score_frozen": score_frozen,
        "iter064_score": iter064_score,
        "iter069_score": iter069_score,
        "threshold": "score < 75 (drops below STRONG threshold)",
    }

    # D: edu CAGR < 9.18%
    edu_cagr = float(metrics_by_ds["educational"].cagr)
    kill_status["D_edu_cagr_below_918"] = {
        "fired": edu_cagr < 0.0918,
        "edu_cagr": edu_cagr,
        "iter064_edu_cagr": float(iter064_metrics.get("educational", {}).get("cagr", 0.0949)),
        "threshold": "edu CAGR < 9.18% floor (loses iter 064 unlock)",
    }

    # E: G7 cross-lib > 0.5 pp
    max_xlib_pp = max(gate_details[ds]["G7_xlib_diff_pp"]
                      for ds in ["educational", "spy_real", "ndx_real"])
    kill_status["E_g7_crosslib_above_05pp"] = {
        "fired": max_xlib_pp > 0.5,
        "max_diff_pp": float(max_xlib_pp),
        "threshold": "> 0.5 pp on any dataset (engine bug)",
    }

    # F: corr(070, 064) > 0.995 on ≥ 2 ds (continuous gate inert vs iter 064 static)
    corrs_064 = {
        ds: float(data["runs"][ds][cfg_id]["corr_070_064"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    n_high_corr = sum(1 for c in corrs_064.values() if c > 0.995)
    kill_status["F_corr_iter070_iter064_above_0995_2plus_ds"] = {
        "fired": n_high_corr >= 2,
        "n_datasets_above_0995": n_high_corr,
        "per_dataset": corrs_064,
        "threshold": "corr(070,064) > 0.995 on ≥ 2 of 3 (continuous gate inert)",
    }

    # G: max|Σw - 1| > 1e-9 anywhere (composition bug)
    max_devs = {
        ds: float(data["runs"][ds][cfg_id]["max_total_exposure_dev"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    kill_status["G_total_exposure_dev_above_1e9"] = {
        "fired": any(v > 1e-9 for v in max_devs.values()),
        "per_dataset": max_devs,
        "threshold": "max|Σw - 1| > 1e-9 (composition bug)",
    }

    # H: flips/yr < 1 OR > 100 on any ds (regime pathology)
    # Continuous gate naturally registers many tiny flips; the upper bound here
    # is intentionally tight to flag noise-driven over-flicker.
    flip_rates = {
        ds: float(data["runs"][ds][cfg_id]["flips_per_year"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    kill_status["H_flip_rate_outside_1_to_100"] = {
        "fired": any(v < 1 or v > 100 for v in flip_rates.values()),
        "per_dataset": flip_rates,
        "threshold": "flips/yr < 1 (no switching) or > 100 (continuous-gate over-flicker)",
    }

    # I: mean(w_qqqt) outside [0.08, 0.13] (drift from iter 064's static 0.10)
    mean_ws = {
        ds: float(data["runs"][ds][cfg_id]["mean_w_qqqt"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    kill_status["I_mean_w_qqqt_outside_008_013"] = {
        "fired": any(not (0.08 <= v <= 0.13) for v in mean_ws.values()),
        "per_dataset": mean_ws,
        "threshold": "mean(w_qqqt) outside [0.08, 0.13] on any ds (drifts from iter 064 static 0.10)",
    }

    # J: corr(z, vix_lag) > 0.7 on ≥ 2 ds (T10Y3M signal not orthogonal to VIX)
    corrs_z_vix = {
        ds: float(data["runs"][ds][cfg_id]["corr_z_vix_lag"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    n_high_corr_zvix = sum(1 for c in corrs_z_vix.values() if abs(c) > 0.7)
    kill_status["J_corr_z_vix_above_07_2plus_ds"] = {
        "fired": n_high_corr_zvix >= 2,
        "n_datasets_above_07": n_high_corr_zvix,
        "per_dataset": corrs_z_vix,
        "threshold": "|corr(z_t10y3m, vix_lag)| > 0.7 on ≥ 2 ds (T10Y3M not orthogonal to VIX)",
    }

    # K: iter 070 Sharpe < iter 069 Sharpe on ≥ 2 ds (continuous fails to match binary)
    sharpe_below_069 = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if metrics_by_ds[ds].sharpe < iter069_metrics.get(ds, {}).get("sharpe", 0.0)
    )
    kill_status["K_iter070_sharpe_below_iter069_2plus_ds"] = {
        "fired": sharpe_below_069 >= 2,
        "n_datasets_iter070_below_iter069": sharpe_below_069,
        "deltas_vs_069": {
            ds: float(metrics_by_ds[ds].sharpe - iter069_metrics.get(ds, {}).get("sharpe", 0.0))
            for ds in ["educational", "spy_real", "ndx_real"]
        },
        "threshold": "iter 070 Sharpe < iter 069 Sharpe on ≥ 2 of 3 (continuous fails to beat binary baseline)",
    }

    n_kills_fired = sum(1 for k in kill_status.values() if k["fired"])
    print(f"  Kills fired: {n_kills_fired}/11")
    for k, v in kill_status.items():
        marker = "❌ FIRED" if v["fired"] else "✓ clean"
        print(f"    {k:60s} {marker}")

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
            "[advances_fin_ml, ch.17-18] (regime detection / Markov-switching) + "
            "[regime_change, p.27, ch.3] (continuous regime indicator) + "
            "Faber 2007 SSRN 962461 + [risk_parity, ch.5] + "
            "Estrella & Mishkin 1998 RES 80(1):45-61 (T10Y3M as recession lead) + "
            "iter 069 final report (binary VIX inner-weight 90 ceiling) + "
            "[advances_fin_ml, p.162-164] (no peek) + "
            "[advances_fin_ml, p.222-223] (DSR cumulative) + "
            "[advances_fin_ml, p.31-34] (G7 cross-lib)"
        ),
        "hypothesis_slug": "iter064-t10y3m-cont-inner-weight",
        "cfg_id": cfg_id,
        "cfg": cfg,
        "gate_details": gate_details,
        "robustness_bonus": bonus_detail,
        "pre_committed_kills": kill_status,
        "n_kills_fired": n_kills_fired,
        "iter064_reference_score": iter064_score,
        "iter064_reference_metrics": iter064_metrics,
        "iter064_reference_dsr": iter064_dsr,
        "iter069_reference_score": iter069_score,
        "iter069_reference_metrics": iter069_metrics,
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
        "delta_vs_iter069": {
            ds: {
                "sharpe_delta": float(
                    metrics_by_ds[ds].sharpe - iter069_metrics.get(ds, {}).get("sharpe", 0.0)
                ),
                "cagr_delta": float(
                    metrics_by_ds[ds].cagr - iter069_metrics.get(ds, {}).get("cagr", 0.0)
                ),
                "mdd_delta": float(
                    metrics_by_ds[ds].mdd - iter069_metrics.get(ds, {}).get("mdd", 0.0)
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
    print(f"Kills fired: {n_kills_fired}/11")


if __name__ == "__main__":
    main()
