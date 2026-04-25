"""Iter 047 — 7-gate battery + Bonferroni-adjusted DSR + score for the
3-cfg weight sweep (`iter046_w50_50` / `iter046_w65_35` / `iter046_w80_20`).

Differences from iter 046's gate code:

1. **G1 PBO is REAL, not vacuous**: with N=3 cfgs we run CSCV across the
   3-cfg grid (still below `MIN_HONEST_N_CONFIGS=4` so we surface a
   warning + report the value, but PASS only if PBO < 0.5 honestly).
2. **G2 DSR uses Bonferroni-adjusted threshold**: α' = 0.05/3 = 0.01667.
   Each cfg's worst-p across 3 datasets is compared against α', and we
   ALSO record raw α=0.05 for transparency.
3. **Per-cfg scoring**: score each of the 3 cfgs independently with
   `scoring.score_strategy(...)`, pick the highest-scoring cfg as
   reportable. This is NOT post-hoc selection on observed data — the
   pre-commitment is on the GRID; choosing best-of-N within the
   pre-committed grid is what the grid is FOR. The Bonferroni penalty
   accounts for the 3-way multiple test.

Cumulative n_trials after iter 047: 4311 + 3 = **4314**
(per BASE_MEMORY.md frontmatter, post-iter-046 = 4311).

Citations
---------
* `[advances_fin_ml, p.208-211]` — PBO via CSCV.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
* Bonferroni (1936) — multiple-testing correction α' = α/k for k tests.
"""

from __future__ import annotations

import json
import sys
import warnings
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_039_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "039-2026-04-25-0313-vrp-basket-3etf"
ITER_041_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "041-2026-04-25-0358-regime-weights-vix-static-stack"
ITER_045_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "045-2026-04-25-0528-iter039-overlay-on-iter037"
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"

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
from ai_trade.backtest.validation.pbo import pbo as pbo_test  # noqa: E402

OUT_DIR = ITER_DIR
RESULTS_PATH = OUT_DIR / "results.json"

# Cumulative n_trials.
CUMULATIVE_N_TRIALS = 4311 + 3  # = 4314 (3 new pre-committed cfgs)

# Bonferroni: α' = α / k for k pre-committed cfgs.
RAW_ALPHA = 0.05
N_CFGS = 3
BONFERRONI_ALPHA = RAW_ALPHA / N_CFGS  # ≈ 0.01667


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


def g1_pbo_grid(returns_matrix: np.ndarray) -> tuple[bool, float, dict]:
    """Real PBO via CSCV over the 3-cfg grid.

    With N=3 the function fires a UserWarning (`MIN_HONEST_N_CONFIGS=4`),
    but the value is still computed; we honestly PASS the gate only if
    PBO < 0.5 and document the small-N warning in the report.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # we surface the small-N caveat in the report
        result = pbo_test(returns_matrix, n_blocks=10)
    return (
        result.pbo < 0.5,
        float(result.pbo),
        {
            "pbo_value": float(result.pbo),
            "n_blocks": int(result.n_blocks),
            "n_combinations": int(result.n_combinations),
            "small_n_warning": "N=3 < MIN_HONEST_N_CONFIGS=4 — PBO is statistically noisy",
        },
    )


def g2_dsr_bonferroni(returns: np.ndarray, n_trials: int) -> tuple[bool, bool, float]:
    """Returns (raw_pass, bonferroni_pass, p_value)."""
    r = dsr_test(returns, n_trials=n_trials)
    p = float(r.p_value)
    return (p < RAW_ALPHA, p < BONFERRONI_ALPHA, p)


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
# Robustness (3 sub-windows × 3 datasets = 9 windows)
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
# Per-cfg gates (called for each of the 3 sweep cfgs)
# ---------------------------------------------------------------------------


def compute_per_cfg_gates(
    cfg_id: str, dataset_name: str, data: dict, pbo_pass_global: bool,
    pbo_value_global: float,
) -> tuple[Gates, dict, pd.Series]:
    series = data["returns_series"][dataset_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    rets = pd.Series(series["net_returns"], index=idx)

    g1_pass = pbo_pass_global  # PBO is grid-level: same per cfg within a dataset
    raw_pass, bonf_pass, p_val = g2_dsr_bonferroni(rets.to_numpy(), CUMULATIVE_N_TRIALS)
    g3_pass, g3_det = g3_walk_forward(rets)
    g4_pass, g4_sr = g4_oos_split(rets)
    g5_pass, g5_sr = g5_forward_post2020(rets)
    g6_pass, g6_ci = g6_bootstrap_ci_low(rets.to_numpy())
    g7_pass, g7_pp = g7_cross_lib(dataset_name, cfg_id, data)

    # G2 strict: use Bonferroni-adjusted threshold for the SCORING gate
    # (more conservative; the multi-cfg pre-commitment paid for it).
    g2_pass = bonf_pass

    gates = Gates(
        g1_pbo=g1_pass, g2_dsr=g2_pass, g3_wf=g3_pass, g4_oos=g4_pass,
        g5_fwd=g5_pass, g6_bootstrap=g6_pass, g7_crosslib=g7_pass,
    )
    detail = {
        "cfg_id": cfg_id,
        "g1_pbo_value": pbo_value_global,
        "g1_note": (
            f"Real CSCV PBO over N={N_CFGS} cfgs "
            f"(below MIN_HONEST_N=4 → noisy but reported)"
        ),
        "g2_dsr_p_raw": p_val,
        "g2_dsr_raw_pass_at_alpha_005": raw_pass,
        "g2_dsr_bonferroni_pass_at_alpha_0167": bonf_pass,
        "g2_alpha_raw": RAW_ALPHA,
        "g2_alpha_bonferroni": BONFERRONI_ALPHA,
        "g3_wf": g3_det,
        "g4_oos_sharpe": g4_sr,
        "g5_fwd_sharpe": g5_sr,
        "g6_bootstrap_ci_low": g6_ci,
        "g7_cross_lib_diff_pp": g7_pp,
        "dsr_p_value": p_val,
    }
    return gates, detail, rets


# ---------------------------------------------------------------------------
# Custom benchmarks (match iter 046 — edu window-stable)
# ---------------------------------------------------------------------------


def build_custom_benchmarks(data: dict) -> dict[str, Benchmark]:
    edu_bench = data["benchmarks"]["educational"]
    return {
        "educational": Benchmark(
            sharpe=edu_bench["sharpe"],
            cagr=edu_bench["cagr"],
            mdd=edu_bench["mdd"],
            label=f"SPY b&h {edu_bench['first']}→{edu_bench['last']} (iter 047 GLD-aligned)",
        ),
        "spy_real": BENCHMARKS["spy_real"],
        "ndx_real": BENCHMARKS["ndx_real"],
    }


# ---------------------------------------------------------------------------
# Main: per-cfg score, then pick highest
# ---------------------------------------------------------------------------


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    custom_benchmarks = build_custom_benchmarks(data)
    iter039_ref = _load_reference(ITER_039_DIR)
    iter041_ref = _load_reference(ITER_041_DIR)
    iter045_ref = _load_reference(ITER_045_DIR)
    iter046_ref = _load_reference(ITER_046_DIR)
    iter046_score = _load_score(ITER_046_DIR)

    cfg_ids = [c["cfg_id"] for c in data["configs"]]
    print(f"Sweep cfgs: {cfg_ids}")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (4311 + {N_CFGS})")
    print(f"Bonferroni α' = {RAW_ALPHA}/{N_CFGS} = {BONFERRONI_ALPHA:.5f}")

    # ---- G1 PBO computed ONCE per dataset across the 3-cfg grid ----
    print("\n=== G1 PBO (grid-level, computed per dataset across 3 cfgs) ===")
    pbo_per_dataset: dict[str, dict] = {}
    for ds in ["educational", "spy_real", "ndx_real"]:
        # Stack the 3 cfg returns into a (T, 3) matrix on their inner-join.
        rets_by_cfg: dict[str, pd.Series] = {}
        for cfg_id in cfg_ids:
            s = data["returns_series"][ds][cfg_id]
            idx = pd.to_datetime(s["index"])
            rets_by_cfg[cfg_id] = pd.Series(s["net_returns"], index=idx)
        common_idx = rets_by_cfg[cfg_ids[0]].index
        for cid in cfg_ids[1:]:
            common_idx = common_idx.intersection(rets_by_cfg[cid].index)
        matrix = np.column_stack([rets_by_cfg[cid].loc[common_idx].to_numpy() for cid in cfg_ids])
        g1_pass, g1_val, g1_det = g1_pbo_grid(matrix)
        pbo_per_dataset[ds] = {
            "pbo_value": g1_val,
            "pass": g1_pass,
            "n_combinations": g1_det["n_combinations"],
            "small_n_warning": g1_det["small_n_warning"],
        }
        print(f"  {ds:12s} PBO={g1_val:.4f} ({'PASS' if g1_pass else 'FAIL'}) "
              f"n_combinations={g1_det['n_combinations']}")

    # ---- Per-cfg gates + per-cfg score ----
    per_cfg_results: dict[str, dict] = {}

    print("\n=== Per-cfg gates + score (Bonferroni-adjusted DSR) ===")
    for cfg_id in cfg_ids:
        print(f"\n--- cfg {cfg_id} ---")
        gates_by_ds: dict[str, Gates] = {}
        metrics_by_ds: dict[str, DatasetMetrics] = {}
        gate_details: dict[str, dict] = {}
        returns_by_ds: dict[str, pd.Series] = {}

        for ds in ["educational", "spy_real", "ndx_real"]:
            run = data["runs"][ds][cfg_id]
            gates, details, rets = compute_per_cfg_gates(
                cfg_id, ds, data,
                pbo_pass_global=pbo_per_dataset[ds]["pass"],
                pbo_value_global=pbo_per_dataset[ds]["pbo_value"],
            )
            returns_by_ds[ds] = rets
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
                "G2_dsr_pass_bonferroni": gates.g2_dsr,
                "G2_dsr_p_raw": details["g2_dsr_p_raw"],
                "G2_dsr_raw_pass_at_alpha_005": details["g2_dsr_raw_pass_at_alpha_005"],
                "G3_wf_pass": gates.g3_wf,
                "G3_wf_profitable": details["g3_wf"].get("profitable_windows", 0),
                "G4_oos_pass": gates.g4_oos, "G4_oos_sharpe": details["g4_oos_sharpe"],
                "G5_fwd_pass": gates.g5_fwd, "G5_fwd_sharpe": details["g5_fwd_sharpe"],
                "G6_boot_pass": gates.g6_bootstrap,
                "G6_boot_ci_low": details["g6_bootstrap_ci_low"],
                "G7_xlib_pass": gates.g7_crosslib,
                "G7_xlib_diff_pp": details["g7_cross_lib_diff_pp"],
            }
            edge_frozen = run["sharpe"] - {
                "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
            }[ds]
            edge_046 = run["sharpe"] - iter046_ref[ds]["sharpe"]
            print(
                f"  {ds:12s} Sharpe={run['sharpe']:+.4f} "
                f"(Δ frozen {edge_frozen:+.4f}, Δ046 {edge_046:+.4f}) "
                f"CAGR={run['cagr']:+.2%} MDD={run['mdd']:.2%} "
                f"DSR p={details['g2_dsr_p_raw']:.4f} "
                f"({'raw≤0.05' if details['g2_dsr_raw_pass_at_alpha_005'] else 'raw>0.05'}, "
                f"{'BF≤0.0167' if gates.g2_dsr else 'BF>0.0167'}) "
                f"gates={gates.n_passed}/7"
            )

        # Robustness bonus per cfg
        bonus_pts, bonus_detail = compute_robustness_bonus(returns_by_ds)

        # Score per cfg (custom + frozen)
        result_custom = score_strategy(
            metrics=metrics_by_ds,
            gates=gates_by_ds,
            cumulative_n_trials=CUMULATIVE_N_TRIALS,
            benchmarks=custom_benchmarks,
        )
        result_frozen = score_strategy(
            metrics=metrics_by_ds,
            gates=gates_by_ds,
            cumulative_n_trials=CUMULATIVE_N_TRIALS,
            benchmarks=BENCHMARKS,
        )
        score_custom = min(100, result_custom.total_score + bonus_pts)
        score_frozen = min(100, result_frozen.total_score + bonus_pts)

        per_cfg_results[cfg_id] = {
            "metrics_by_ds": {ds: asdict(metrics_by_ds[ds]) for ds in metrics_by_ds},
            "gate_details": gate_details,
            "robustness_bonus": bonus_detail,
            "score_custom": score_custom,
            "score_frozen": score_frozen,
            "tier_custom": tier_from_score(
                score_custom, winner_conditions_met=result_custom.winner_conditions_met,
            ).value,
            "tier_frozen": tier_from_score(
                score_frozen, winner_conditions_met=result_frozen.winner_conditions_met,
            ).value,
            "winner_conds_custom": result_custom.winner_conditions_met,
            "winner_conds_frozen": result_frozen.winner_conditions_met,
            "criteria_frozen": result_frozen.criteria,
            "criteria_custom": result_custom.criteria,
        }
        print(f"  → score_frozen={score_frozen}/100 "
              f"({per_cfg_results[cfg_id]['tier_frozen']}, "
              f"winner_conds={result_frozen.winner_conditions_met}); "
              f"score_custom={score_custom}/100")

    # ---- Pick best cfg by FROZEN score ----
    best_cfg_id = max(cfg_ids, key=lambda c: per_cfg_results[c]["score_frozen"])
    best = per_cfg_results[best_cfg_id]
    print(f"\n=== BEST CFG (by frozen score) = {best_cfg_id} → "
          f"{best['score_frozen']}/100 ({best['tier_frozen']}) ===")

    # ---- Pre-committed kill criteria ----
    print("\n=== Pre-committed kill evaluation ===")
    kill_status: dict[str, dict] = {}

    # A: best score < iter 046's 85
    iter_046_score_baseline = iter046_score if iter046_score > 0 else 85
    kill_status["A_top_score_below_iter046"] = {
        "fired": best["score_frozen"] < iter_046_score_baseline,
        "best_score": best["score_frozen"],
        "iter_046_baseline": iter_046_score_baseline,
        "threshold": f"< {iter_046_score_baseline}",
        "note": "If fired → weight axis ENTIRELY DOMINATED by 50/50",
    }

    # B: all 3 cfgs fail Bonferroni-adjusted DSR on >= 2 datasets
    cfgs_failing_bonf_on_2plus_ds = sum(
        1 for cid in cfg_ids
        if sum(
            1 for ds in ["educational", "spy_real", "ndx_real"]
            if not per_cfg_results[cid]["gate_details"][ds]["G2_dsr_pass_bonferroni"]
        ) >= 2
    )
    kill_status["B_all_cfgs_fail_bonferroni_dsr"] = {
        "fired": cfgs_failing_bonf_on_2plus_ds == N_CFGS,
        "n_cfgs_failing": cfgs_failing_bonf_on_2plus_ds,
        "n_total_cfgs": N_CFGS,
        "threshold": "all 3 cfgs fail Bonferroni-DSR on ≥2 of 3 datasets",
        "note": "If fired → multi-test penalty erases iter 046 edge",
    }

    # C: PBO ≥ 0.5 on >= 1 dataset
    kill_status["C_pbo_above_05_any_dataset"] = {
        "fired": any(not v["pass"] for v in pbo_per_dataset.values()),
        "pbo_per_dataset": {ds: pbo_per_dataset[ds]["pbo_value"] for ds in pbo_per_dataset},
        "threshold": "PBO ≥ 0.5 on ≥1 dataset",
        "note": "If fired → weight grid is itself overfit",
    }

    # D: best cfg Sharpe drops by >= 0.10 vs iter 046 50/50 on >= 2 datasets
    sharpe_drop_count = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if best["metrics_by_ds"][ds]["sharpe"] - iter046_ref[ds]["sharpe"] <= -0.10
    )
    kill_status["D_sharpe_regress_vs_iter046_2plus_ds"] = {
        "fired": sharpe_drop_count >= 2,
        "n_datasets_dropping_010": sharpe_drop_count,
        "threshold": "Best cfg Sharpe ≤ iter 046 − 0.10 on ≥2 of 3 datasets",
        "note": "If fired → variance reduction was load-bearing; weight asymmetry destroys it",
    }

    # E: G7 cross-lib > 3pp on any cfg×dataset
    max_xlib_pp = 0.0
    for cid in cfg_ids:
        for ds in ["educational", "spy_real", "ndx_real"]:
            v = per_cfg_results[cid]["gate_details"][ds]["G7_xlib_diff_pp"]
            if v > max_xlib_pp:
                max_xlib_pp = v
    kill_status["E_g7_crosslib_above_3pp"] = {
        "fired": max_xlib_pp > 3.0,
        "max_diff_pp": max_xlib_pp,
        "threshold": "> 3.0 pp on any cfg×dataset",
        "note": "If fired → engine bug; abort and fix",
    }

    # F: best cfg passes 0 CAGR floors with custom benchmark (iter 046 already passed 0)
    cagr_floors_passed_custom = sum(
        1 for ds_v in best["criteria_custom"]["4_cagr_floor"]["per_dataset"].values()
        if ds_v
    )
    kill_status["F_best_cfg_zero_cagr_floors_custom"] = {
        "fired": cagr_floors_passed_custom == 0,
        "cagr_floors_passed_custom": cagr_floors_passed_custom,
        "threshold": "Best cfg passes 0 CAGR floors with custom-bench",
        "note": "If fired → CAGR axis is uncrosseable from iter 041+iter 039 components",
    }

    n_kills_fired = sum(1 for k in kill_status.values() if k["fired"])
    print(f"  Kills fired: {n_kills_fired}/6")
    for k, v in kill_status.items():
        marker = "❌ FIRED" if v["fired"] else "✓ clean"
        print(f"    {k:42s} {marker}")

    # ---- Build verdict.json ----
    canonical_score = best["score_frozen"]
    canonical_tier = best["tier_frozen"]
    canonical_winner_conds = best["winner_conds_frozen"]

    verdict = {
        "status": "winner" if canonical_winner_conds and canonical_score >= 90 else canonical_tier.lower(),
        "tier": canonical_tier,
        "total_score": canonical_score,
        "winner_conditions_met": canonical_winner_conds,
        "criteria": best["criteria_frozen"],
        "metrics_used": best["metrics_by_ds"],
        "benchmarks_used": {ds: asdict(BENCHMARKS[ds]) for ds in BENCHMARKS},
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "configs_tested": N_CFGS,
        "primary_citation": (
            "[risk_parity, ch.5] + [volatility_trading, p.218] + "
            "[advances_fin_ml, p.208-211] (PBO grid-level, N=3); "
            "[advances_fin_ml, p.222-223] (DSR cumulative); "
            "[advances_fin_ml, p.31-34] (G7); "
            "Markowitz (1952), JoF 7(1) (convex-combo Pareto frontier); "
            "Bonferroni (1936) (multi-test correction α'=α/k); "
            "Whaley (2009), JPM 35(3) DOI 10.3905/JPM.2009.35.3.098; "
            "Bondarenko (2014), QJF 4(3) 1450015; "
            "Carr-Wu (2009), RFS 22(3) 1311-1341; "
            "Erb-Harvey (2006), FAJ 62(2) DOI 10.2469/faj.v62.n2.4084"
        ),
        "hypothesis_slug": "iter046-weight-sweep",
        "best_cfg_id": best_cfg_id,
        "pbo_per_dataset": pbo_per_dataset,
        "bonferroni_alpha": BONFERRONI_ALPHA,
        "raw_alpha": RAW_ALPHA,
        "n_cfgs": N_CFGS,
        "per_cfg_results": per_cfg_results,
        "pre_committed_kills": kill_status,
        "n_kills_fired": n_kills_fired,
        "iter039_reference_metrics": iter039_ref,
        "iter041_reference_metrics": iter041_ref,
        "iter045_reference_metrics": iter045_ref,
        "iter046_reference_metrics": iter046_ref,
        "iter046_reference_score": iter046_score,
        "delta_vs_iter046": {
            ds: {
                "sharpe_delta": best["metrics_by_ds"][ds]["sharpe"] - iter046_ref[ds]["sharpe"],
                "cagr_delta":   best["metrics_by_ds"][ds]["cagr"]   - iter046_ref[ds]["cagr"],
                "mdd_delta":    best["metrics_by_ds"][ds]["mdd"]    - iter046_ref[ds]["mdd"],
            }
            for ds in ["educational", "spy_real", "ndx_real"]
        },
    }

    # Inject the robustness bonus into the canonical criteria block.
    verdict["criteria"]["6_robustness_bonus"] = {
        "points": best["robustness_bonus"]["bonus_awarded"],
        "max": 5,
        "method": "3 non-overlapping sub-windows per dataset; positive count across 9 windows",
        "detail": best["robustness_bonus"],
    }

    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8",
    )

    print(f"\n=== CANONICAL VERDICT (frozen benchmarks, best cfg) ===")
    print(f"Best cfg: {best_cfg_id}")
    print(f"Tier: {canonical_tier}")
    print(f"Total score (with bonus): {canonical_score}/100")
    print(f"Winner conditions met: {canonical_winner_conds}")
    print(f"Status: {verdict['status']}")
    print(f"Kills fired: {n_kills_fired}/6")
    for k, v in best["criteria_frozen"].items():
        print(f"  {k}: {v['points']}/{v['max']}")


if __name__ == "__main__":
    main()
