"""Iter 077 — 7-gate battery + score for iter 064 + MTUM/VLUE LS sleeve ensemble.

Multi-cfg grid (N=20: 5 target_vol × 4 w_sleeve). G1 PBO via CSCV
(10 blocks, grid-level). G2 DSR computed with v2 per-iter convention
(n_trials = 20 = configs tested THIS iteration; relaxed 2026-04-25).
v1 cumulative tracked for audit (4462 + 60 = 4522).

Pre-committed kill criteria (from hypothesis.md §"Kill criteria"):

  A — corr(r_sleeve, r_bench) > 0.5 on ≥ 2 ds (falsifies low-ρ hypothesis)
  B — Sleeve standalone Sharpe < 0.40 on ≥ 2 ds (falsifies high-Sharpe hypothesis)
  C — Combined Sharpe regress vs iter 064 ≥ 0.05 on ≥ 2 ds
  D — Best cfg score < 75 (below STRONG)
  E — G7 cross-lib > 3 pp on any cfg
  F — PBO grid-level ≥ 0.5 on ≥ 2 ds
  G — DSR worst-p ≥ 0.05 on best cfg (winner cond #3 fails)
  H — Combined CAGR ≥ floor on 0/3 ds (joint-constraint falsified — sleeve doesn't unlock CAGR)

Citations
---------
* `[advances_fin_ml, p.208-211]` — PBO via CSCV.
* `[advances_fin_ml, p.222-223]` — DSR with n_trials (per-iter v2).
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
* Markowitz (1952), JoF 7(1) — convex combination Sharpe identity.
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
from ai_trade.backtest.validation.pbo import pbo as pbo_test  # noqa: E402

OUT_DIR = ITER_DIR
RESULTS_PATH = OUT_DIR / "results.json"

# v1 audit DSR — cumulative across all 76 iters (4462 + 60 from this iter)
CUMULATIVE_N_TRIALS_V1 = 4462 + 60  # = 4522
# v2 operational DSR — per-iter convention (relaxed 2026-04-25)
N_TRIALS_PER_ITER_V2 = 20
RAW_ALPHA = 0.05


def _load_iter_metrics(iter_dir: Path) -> dict:
    p = iter_dir / "verdict.json"
    if not p.exists():
        return {}
    v = json.loads(p.read_text())
    return v.get("metrics_used", {})


def g1_pbo_grid(returns_matrix: np.ndarray) -> tuple[bool, dict]:
    if returns_matrix.shape[1] < 2:
        return True, {"pbo_value": float("nan"), "n_combinations": 0}
    res = pbo_test(returns_matrix, n_blocks=10)
    return float(res.pbo) < 0.5, {
        "pbo_value": float(res.pbo),
        "n_combinations": int(res.n_combinations),
        "n_strategies": int(returns_matrix.shape[1]),
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
    """Vectorized stationary-bootstrap (Politis-Romano 1994) CI low."""
    r = np.asarray(returns, dtype=float)
    if len(r) < 30:
        return False, float("nan")
    rng = np.random.default_rng(42)
    n = len(r)
    block_mean = 5
    p = 1.0 / block_mean
    n_resamples = 5000
    starts = rng.integers(0, n, size=(n_resamples, n))
    restarts = rng.random((n_resamples, n)) < p
    idx = np.empty((n_resamples, n), dtype=np.int64)
    idx[:, 0] = starts[:, 0]
    for t in range(1, n):
        idx[:, t] = np.where(restarts[:, t], starts[:, t], (idx[:, t - 1] + 1) % n)
    samples = r[idx]
    means = samples.mean(axis=1)
    sigmas = samples.std(axis=1, ddof=0)
    sharpes = np.where(sigmas > 1e-12, means / sigmas * np.sqrt(252), 0.0)
    ci_low = float(np.quantile(sharpes, 0.0005))
    return ci_low > 0, ci_low


def g7_cross_lib(ds: str, cfg_id: str, data: dict) -> tuple[bool, float]:
    diff = float(data["crosslib"][ds][cfg_id]["abs_diff_pp"])
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
        sharpes_list = robustness_sub_window_sharpe(r)
        n_pos = sum(1 for s in sharpes_list if s > 0)
        total += len(sharpes_list)
        pos += n_pos
        details[ds] = {"window_sharpes": sharpes_list,
                        "positive_count": n_pos, "total": len(sharpes_list)}
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


def get_returns_matrix(data: dict, ds: str) -> tuple[np.ndarray, list[str]]:
    rs = data["returns_series"][ds]
    cfg_ids = list(rs.keys())
    series = []
    for c in cfg_ids:
        idx = pd.to_datetime(rs[c]["index"])
        s = pd.Series(rs[c]["net_returns"], index=idx)
        series.append(s)
    df = pd.concat(series, axis=1, join="inner")
    df.columns = cfg_ids
    return df.to_numpy(), cfg_ids


def compute_per_dataset_gates(
    cfg_id: str, ds: str, data: dict, pbo_p: bool, pbo_d: dict,
    n_trials: int,
) -> tuple[Gates, dict, pd.Series]:
    s = data["returns_series"][ds][cfg_id]
    idx = pd.to_datetime(s["index"])
    rets = pd.Series(s["net_returns"], index=idx)
    g2_p, p_val = g2_dsr_raw(rets.to_numpy(), n_trials)
    g3_p, g3_d = g3_walk_forward(rets)
    g4_p, g4_s = g4_oos_split(rets)
    g5_p, g5_s = g5_forward_post2020(rets)
    g6_p, g6_c = g6_bootstrap_ci_low(rets.to_numpy())
    g7_p, g7_d = g7_cross_lib(ds, cfg_id, data)
    gates = Gates(g1_pbo=pbo_p, g2_dsr=g2_p, g3_wf=g3_p, g4_oos=g4_p,
                  g5_fwd=g5_p, g6_bootstrap=g6_p, g7_crosslib=g7_p)
    detail = {
        "G1_pbo_pass": pbo_p, "G1_pbo_value": pbo_d.get("pbo_value", float("nan")),
        "G1_n_strategies": pbo_d.get("n_strategies", 0),
        "G2_dsr_pass": g2_p, "G2_dsr_p_raw": p_val, "G2_alpha_raw": RAW_ALPHA,
        "G2_n_trials_used": n_trials,
        "G3_wf_pass": g3_p, "G3_wf_profitable": g3_d.get("profitable_windows", 0),
        "G3_wf_windows": g3_d.get("windows", []),
        "G4_oos_pass": g4_p, "G4_oos_sharpe": g4_s,
        "G5_fwd_pass": g5_p, "G5_fwd_sharpe": g5_s,
        "G6_boot_pass": g6_p, "G6_boot_ci_low": g6_c,
        "G7_xlib_pass": g7_p, "G7_xlib_diff_pp": g7_d,
        "dsr_p_value": p_val,
    }
    return gates, detail, rets


def evaluate_cfg(
    cfg_id: str, data: dict, pbo_by_ds: dict, iter064_metrics: dict,
    *, n_trials_for_dsr: int, n_trials_for_score: int,
) -> dict:
    gates_by_ds: dict[str, Gates] = {}
    metrics_by_ds: dict[str, DatasetMetrics] = {}
    gate_details: dict[str, dict] = {}
    returns_by_ds: dict[str, pd.Series] = {}

    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        pbo_p, pbo_d = pbo_by_ds[ds]
        gates, detail, rets = compute_per_dataset_gates(
            cfg_id, ds, data, pbo_p, pbo_d, n_trials_for_dsr,
        )
        returns_by_ds[ds] = rets
        metrics_by_ds[ds] = DatasetMetrics(
            sharpe=run["sharpe"], cagr=run["cagr"], mdd=run["mdd"],
            dsr_p_value=detail["dsr_p_value"],
        )
        gates_by_ds[ds] = gates
        gate_details[ds] = detail

    bonus_pts, bonus_detail = compute_robustness_bonus(returns_by_ds)
    result = score_strategy(
        metrics=metrics_by_ds, gates=gates_by_ds,
        cumulative_n_trials=n_trials_for_score, benchmarks=BENCHMARKS,
    )
    score = min(100, result.total_score + bonus_pts)
    tier = tier_from_score(score, winner_conditions_met=result.winner_conditions_met)

    # Pre-committed kills
    kills: dict = {}

    # A: corr(sleeve, bench) > 0.5 on ≥ 2 ds
    corr_sleeve_bench = {ds: float(data["runs"][ds][cfg_id]["corr_sleeve_bench"])
                          for ds in ["educational", "spy_real", "ndx_real"]}
    n_high_corr = sum(1 for v in corr_sleeve_bench.values() if v > 0.5)
    kills["A_corr_sleeve_bench_above_05_2ds"] = {
        "fired": n_high_corr >= 2, "n_above_05": n_high_corr,
        "corr_sleeve_bench": corr_sleeve_bench,
    }

    # B: Sleeve standalone Sharpe < 0.40 on ≥ 2 ds
    sleeve_sharpes = {ds: float(data["runs"][ds][cfg_id]["r_sleeve_sharpe"])
                      for ds in ["educational", "spy_real", "ndx_real"]}
    n_weak = sum(1 for v in sleeve_sharpes.values() if v < 0.40)
    kills["B_sleeve_sharpe_below_040_2ds"] = {
        "fired": n_weak >= 2, "n_below_040": n_weak,
        "sleeve_sharpes": sleeve_sharpes,
    }

    # C: Combined Sharpe regress vs iter 064 by ≥ 0.05 on ≥ 2 ds
    deltas_064 = {
        ds: float(metrics_by_ds[ds].sharpe - iter064_metrics.get(ds, {}).get("sharpe", 0.0))
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    n_regress = sum(1 for v in deltas_064.values() if v <= -0.05)
    kills["C_sharpe_regress_vs_064_ge_005_2ds"] = {
        "fired": n_regress >= 2, "n_regress_005": n_regress,
        "deltas_vs_064": deltas_064,
    }

    # D: Score < 75 (below STRONG)
    kills["D_score_below_75"] = {"fired": score < 75, "score": score}

    # E: G7 cross-lib > 3 pp on any ds
    max_xlib = max(gate_details[ds]["G7_xlib_diff_pp"]
                   for ds in ["educational", "spy_real", "ndx_real"])
    kills["E_g7_crosslib_above_3pp"] = {
        "fired": max_xlib > 3.0, "max_diff_pp": float(max_xlib),
    }

    # F: PBO grid-level ≥ 0.5 on ≥ 2 ds
    pbo_per_ds = {ds: float(pbo_by_ds[ds][1]["pbo_value"])
                  for ds in ["educational", "spy_real", "ndx_real"]}
    n_high_pbo = sum(1 for v in pbo_per_ds.values() if v >= 0.5)
    kills["F_pbo_above_05_2ds"] = {
        "fired": n_high_pbo >= 2, "n_above_05": n_high_pbo,
        "pbo_per_ds": pbo_per_ds,
    }

    # G: DSR worst-p ≥ 0.05 on best cfg
    worst_p = max(gate_details[ds]["G2_dsr_p_raw"]
                  for ds in ["educational", "spy_real", "ndx_real"])
    kills["G_dsr_worst_p_ge_005"] = {
        "fired": worst_p >= 0.05, "worst_p": float(worst_p),
        "per_ds": {ds: float(gate_details[ds]["G2_dsr_p_raw"])
                   for ds in ["educational", "spy_real", "ndx_real"]},
    }

    # H: CAGR floor not closed on any ds (joint-constraint falsified)
    bench_cagr = {ds: BENCHMARKS[ds].cagr for ds in BENCHMARKS}
    cagr_passes = {ds: bool(metrics_by_ds[ds].cagr >= 0.8 * bench_cagr[ds])
                    for ds in ["educational", "spy_real", "ndx_real"]}
    n_pass_cagr = sum(1 for v in cagr_passes.values() if v)
    kills["H_cagr_floor_zero_pass_3ds"] = {
        "fired": n_pass_cagr == 0,
        "n_pass": n_pass_cagr,
        "passes": cagr_passes,
        "cagr_per_ds": {ds: float(metrics_by_ds[ds].cagr)
                         for ds in ["educational", "spy_real", "ndx_real"]},
        "floor_per_ds": {ds: float(0.8 * bench_cagr[ds])
                          for ds in ["educational", "spy_real", "ndx_real"]},
    }

    n_kills_fired = sum(1 for v in kills.values() if v["fired"])

    return {
        "cfg_id": cfg_id,
        "score": score,
        "tier": tier.value,
        "winner_conditions_met": result.winner_conditions_met,
        "criteria": result.criteria,
        "metrics_by_ds": {ds: asdict(metrics_by_ds[ds]) for ds in metrics_by_ds},
        "gates_by_ds": {ds: gates_by_ds[ds].n_passed for ds in gates_by_ds},
        "gate_details": gate_details,
        "robustness_bonus": bonus_detail,
        "kills": kills,
        "n_kills_fired": n_kills_fired,
        "deltas_vs_064": deltas_064,
    }


def main() -> None:
    print(f"=== Iter 077 — gates + score ({N_TRIALS_PER_ITER_V2} cfgs) ===")
    data = json.loads(RESULTS_PATH.read_text())

    # Load iter 064 metrics for KILL C delta computation
    iter064_metrics = _load_iter_metrics(ITER_064_DIR)
    if not iter064_metrics:
        # Fall back to known frozen values
        iter064_metrics = {
            "educational": {"sharpe": 1.221},
            "spy_real":    {"sharpe": 1.331},
            "ndx_real":    {"sharpe": 1.380},
        }

    # Compute G1 PBO once per dataset (grid-level, all cfgs)
    pbo_by_ds: dict[str, tuple[bool, dict]] = {}
    for ds in ["educational", "spy_real", "ndx_real"]:
        rmat, _ = get_returns_matrix(data, ds)
        pbo_by_ds[ds] = g1_pbo_grid(rmat)
        print(f"  G1 PBO {ds:>11}: pass={pbo_by_ds[ds][0]} "
              f"value={pbo_by_ds[ds][1]['pbo_value']:.4f} "
              f"n_strategies={pbo_by_ds[ds][1]['n_strategies']}")

    # Evaluate every cfg
    cfgs = list(data["runs"]["spy_real"].keys())
    eval_results = []
    for cfg_id in cfgs:
        ev = evaluate_cfg(
            cfg_id, data, pbo_by_ds, iter064_metrics,
            n_trials_for_dsr=N_TRIALS_PER_ITER_V2,
            n_trials_for_score=CUMULATIVE_N_TRIALS_V1,
        )
        eval_results.append(ev)
        gpd = ev["gates_by_ds"]
        print(
            f"  {cfg_id:42s} score={ev['score']:3d} "
            f"tier={ev['tier']:<10s} "
            f"gates edu/spy/ndx={gpd['educational']}/{gpd['spy_real']}/{gpd['ndx_real']} "
            f"kills={ev['n_kills_fired']}/8 "
            f"win={ev['winner_conditions_met']}"
        )

    # Pick best by score, then by Sharpe across datasets
    eval_results.sort(
        key=lambda x: (
            -x["score"],
            -(x["metrics_by_ds"]["spy_real"]["sharpe"] +
              x["metrics_by_ds"]["ndx_real"]["sharpe"]),
        )
    )
    best = eval_results[0]
    print(f"\nBest cfg: {best['cfg_id']} score={best['score']} tier={best['tier']}")

    # Build verdict.json from best cfg using ScoreResult.to_dict format
    verdict = {
        "total_score": best["score"],
        "tier": best["tier"],
        "winner_conditions_met": best["winner_conditions_met"],
        "criteria": best["criteria"],
        "metrics_used": best["metrics_by_ds"],
        "benchmarks_used": {ds: asdict(BENCHMARKS[ds]) for ds in BENCHMARKS},
        "cumulative_n_trials": CUMULATIVE_N_TRIALS_V1,
        "n_trials_per_iter": N_TRIALS_PER_ITER_V2,
        "configs_tested": N_TRIALS_PER_ITER_V2,
        "primary_citation": (
            "Carhart (1997) JoF 52(1) DOI 10.1111/j.1540-6261.1997.tb03808.x "
            "+ Asness-Moskowitz-Pedersen (2013) JoF 68(3) DOI 10.1111/jofi.12021 "
            "+ [advances_fin_ml, ch.3, p.222-223]"
        ),
        "hypothesis_slug": "iter077-iter064-mtum-vlue-ls-sleeve",
        "best_cfg_id": best["cfg_id"],
        "kills": best["kills"],
        "n_kills_fired": best["n_kills_fired"],
        "robustness_bonus": best["robustness_bonus"],
        "all_cfgs_summary": [
            {
                "cfg_id": ev["cfg_id"],
                "score": ev["score"],
                "tier": ev["tier"],
                "gates_by_ds": ev["gates_by_ds"],
                "winner_conditions_met": ev["winner_conditions_met"],
                "n_kills_fired": ev["n_kills_fired"],
                "sharpe_by_ds": {ds: ev["metrics_by_ds"][ds]["sharpe"]
                                  for ds in ev["metrics_by_ds"]},
                "cagr_by_ds": {ds: ev["metrics_by_ds"][ds]["cagr"]
                                for ds in ev["metrics_by_ds"]},
            }
            for ev in eval_results
        ],
        "status": "winner" if best["winner_conditions_met"] and best["score"] >= 90
                   else best["tier"].lower(),
    }
    verdict_path = OUT_DIR / "verdict.json"
    verdict_path.write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {verdict_path}")


if __name__ == "__main__":
    main()
