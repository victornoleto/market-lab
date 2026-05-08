"""Iter 074 — 7-gate battery + score for the iter 016 + iter 064 ensemble (7 cfgs).

Multi-cfg grid (N=7 weight sweep). G1 PBO via CSCV (10 blocks, grid-level).
G2 DSR uses raw α=0.05 with cumulative_n_trials = 4360 + 21 = 4381
(7 cfgs × 3 datasets, matching iter 073's per-dataset trial counting).

Pre-committed kill criteria (from hypothesis.md §"Kill criteria"):

  A — Combined Sharpe regress vs iter 064 by ≥ 0.05 on ≥ 2 datasets
  B — DSR worst-p ≥ 0.05 on best cfg (winner cond #3 fails)
  C — Score < 90 (winner threshold) on best cfg
  D — corr(r_016, r_064) > 0.85 on ≥ 2 datasets
  E — Markowitz outer residual ≥ 0.05 Sharpe abs
  F — G7 cross-lib > 3 pp absolute CAGR difference
  G — PBO grid-level ≥ 0.5 on ≥ 2 datasets
  H — edu CAGR < 9.18% on best cfg (winner cond #4)
  I — combined MDD on best cfg > 25% on ≥ 2 datasets

Citations
---------
* `[advances_fin_ml, p.208-211]` — PBO via CSCV.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
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
ITER_016_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "016-2026-04-24-1729-static-stack-vm-hybrid"
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

CUMULATIVE_N_TRIALS = 4360 + 21  # = 4381 (7 cfgs × 3 datasets)
RAW_ALPHA = 0.05


def _load_iter_metrics(iter_dir: Path) -> dict:
    p = iter_dir / "verdict.json"
    if not p.exists():
        return {}
    v = json.loads(p.read_text())
    return v.get("metrics_used", {})


def _load_iter_score(iter_dir: Path) -> int:
    p = iter_dir / "verdict.json"
    if not p.exists():
        return 0
    return int(json.loads(p.read_text())["total_score"])


def g1_pbo_grid(returns_matrix: np.ndarray) -> tuple[bool, dict]:
    """G1 PBO via CSCV at N≥4 cfgs. Pass if PBO < 0.5."""
    if returns_matrix.shape[1] < 2:
        return True, {
            "pbo_value": float("nan"),
            "n_combinations": 0,
            "small_n_warning": "N<2 cfgs — PBO vacuous",
        }
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
        details[ds] = {"window_sharpes": sharpes_list, "positive_count": n_pos, "total": len(sharpes_list)}
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
    """Build (n_obs, n_strategies) matrix for PBO across all 7 cfgs of dataset `ds`."""
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
    cfg_id: str, ds: str, data: dict, pbo_p: bool, pbo_d: dict
) -> tuple[Gates, dict, pd.Series]:
    s = data["returns_series"][ds][cfg_id]
    idx = pd.to_datetime(s["index"])
    rets = pd.Series(s["net_returns"], index=idx)

    g2_p, p_val = g2_dsr_raw(rets.to_numpy(), CUMULATIVE_N_TRIALS)
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
    cfg_id: str,
    data: dict,
    pbo_by_ds: dict,
    iter064_metrics: dict,
    iter016_metrics: dict,
) -> dict:
    """Return full evaluation (gates, score, kills) for a single cfg."""
    gates_by_ds: dict[str, Gates] = {}
    metrics_by_ds: dict[str, DatasetMetrics] = {}
    gate_details: dict[str, dict] = {}
    returns_by_ds: dict[str, pd.Series] = {}

    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        pbo_p, pbo_d = pbo_by_ds[ds]
        gates, detail, rets = compute_per_dataset_gates(
            cfg_id, ds, data, pbo_p, pbo_d
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
        cumulative_n_trials=CUMULATIVE_N_TRIALS, benchmarks=BENCHMARKS,
    )
    score = min(100, result.total_score + bonus_pts)
    tier = tier_from_score(score, winner_conditions_met=result.winner_conditions_met)

    # Pre-committed kills evaluation
    kills = {}

    # A: Combined Sharpe regress vs iter 064 by ≥ 0.05 on ≥ 2 datasets
    deltas_064 = {
        ds: float(metrics_by_ds[ds].sharpe - iter064_metrics.get(ds, {}).get("sharpe", 0.0))
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    n_regress = sum(1 for v in deltas_064.values() if v <= -0.05)
    kills["A_sharpe_regress_vs_064_ge_005_2ds"] = {
        "fired": n_regress >= 2, "n_regress_005": n_regress,
        "deltas_vs_064": deltas_064,
    }

    # B: DSR worst-p ≥ 0.05
    worst_p = max(gate_details[ds]["G2_dsr_p_raw"]
                  for ds in ["educational", "spy_real", "ndx_real"])
    kills["B_dsr_worst_p_ge_005"] = {
        "fired": worst_p >= 0.05, "worst_p": float(worst_p),
        "per_ds": {ds: float(gate_details[ds]["G2_dsr_p_raw"])
                   for ds in ["educational", "spy_real", "ndx_real"]},
    }

    # C: Score < 90 (winner threshold)
    kills["C_score_below_90"] = {"fired": score < 90, "score": score}

    # D: corr(r_016, r_064) > 0.85 on ≥ 2 datasets
    corr_legs = {ds: float(data["runs"][ds][cfg_id]["corr_016_064"])
                 for ds in ["educational", "spy_real", "ndx_real"]}
    n_high_corr = sum(1 for v in corr_legs.values() if v > 0.85)
    kills["D_corr_legs_above_085_2ds"] = {
        "fired": n_high_corr >= 2, "n_above_085": n_high_corr,
        "corr_016_064": corr_legs,
    }

    # E: Markowitz residual ≥ 0.05 Sharpe abs (per-cfg, max across datasets)
    residuals = {ds: float(data["runs"][ds][cfg_id]["markowitz_residual_sharpe"])
                 for ds in ["educational", "spy_real", "ndx_real"]}
    max_abs_residual = max(abs(v) for v in residuals.values())
    kills["E_markowitz_residual_ge_005"] = {
        "fired": max_abs_residual >= 0.05,
        "max_abs_residual": float(max_abs_residual),
        "residuals": residuals,
    }

    # F: G7 cross-lib > 3 pp on any ds
    max_xlib = max(gate_details[ds]["G7_xlib_diff_pp"]
                   for ds in ["educational", "spy_real", "ndx_real"])
    kills["F_g7_crosslib_above_3pp"] = {
        "fired": max_xlib > 3.0, "max_diff_pp": float(max_xlib),
    }

    # G: PBO grid-level ≥ 0.5 on ≥ 2 datasets
    pbo_per_ds = {ds: float(pbo_by_ds[ds][1]["pbo_value"])
                  for ds in ["educational", "spy_real", "ndx_real"]}
    n_high_pbo = sum(1 for v in pbo_per_ds.values() if v >= 0.5)
    kills["G_pbo_above_05_2ds"] = {
        "fired": n_high_pbo >= 2, "n_above_05": n_high_pbo,
        "pbo_per_ds": pbo_per_ds,
    }

    # H: edu CAGR < 9.18%
    edu_cagr = float(metrics_by_ds["educational"].cagr)
    kills["H_edu_cagr_below_0918"] = {
        "fired": edu_cagr < 0.0918, "edu_cagr": edu_cagr,
    }

    # I: combined MDD > 25% on ≥ 2 datasets
    mdds = {ds: float(metrics_by_ds[ds].mdd)
            for ds in ["educational", "spy_real", "ndx_real"]}
    n_high_mdd = sum(1 for v in mdds.values() if v > 0.25)
    kills["I_mdd_above_25pct_2ds"] = {
        "fired": n_high_mdd >= 2, "n_above_25": n_high_mdd, "mdds": mdds,
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
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    cfgs = data["configs"]

    iter016_score = _load_iter_score(ITER_016_DIR)
    iter016_metrics = _load_iter_metrics(ITER_016_DIR)
    iter064_score = _load_iter_score(ITER_064_DIR)
    iter064_metrics = _load_iter_metrics(ITER_064_DIR)

    print(f"Configs: {len(cfgs)} ({[c['cfg_id'] for c in cfgs]})")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (= 4360 + 21)")
    print(f"raw α = {RAW_ALPHA}")
    print(f"iter 016 reference score: {iter016_score}")
    print(f"iter 064 reference score: {iter064_score}")

    # PBO is computed ONCE per dataset across all 7 cfgs (grid-level CSCV)
    print("\n=== G1 PBO (grid-level CSCV across 7 cfgs) ===")
    pbo_by_ds: dict[str, tuple[bool, dict]] = {}
    for ds in ["educational", "spy_real", "ndx_real"]:
        mat, cfg_ids = get_returns_matrix(data, ds)
        pbo_p, pbo_d = g1_pbo_grid(mat)
        pbo_by_ds[ds] = (pbo_p, pbo_d)
        print(
            f"  {ds:12s} N={mat.shape[1]} bars={mat.shape[0]} "
            f"PBO={pbo_d.get('pbo_value', 'NA'):.4f} "
            f"({'PASS' if pbo_p else 'FAIL'})"
        )

    # Evaluate ALL cfgs
    print("\n=== Per-cfg evaluation ===")
    cfg_evals: list[dict] = []
    for cfg in cfgs:
        ev = evaluate_cfg(cfg["cfg_id"], data, pbo_by_ds, iter064_metrics, iter016_metrics)
        cfg_evals.append(ev)
        s_e = ev["metrics_by_ds"]["educational"]["sharpe"]
        s_s = ev["metrics_by_ds"]["spy_real"]["sharpe"]
        s_n = ev["metrics_by_ds"]["ndx_real"]["sharpe"]
        c_e = ev["metrics_by_ds"]["educational"]["cagr"]
        c_s = ev["metrics_by_ds"]["spy_real"]["cagr"]
        c_n = ev["metrics_by_ds"]["ndx_real"]["cagr"]
        print(
            f"  {cfg['cfg_id']:32s} score={ev['score']}/100 ({ev['tier']:9s}) "
            f"WC={'Y' if ev['winner_conditions_met'] else 'n'} "
            f"S={s_e:.3f}/{s_s:.3f}/{s_n:.3f} "
            f"C={c_e:.2%}/{c_s:.2%}/{c_n:.2%} "
            f"gates={'/'.join(str(ev['gates_by_ds'][d]) for d in ['educational','spy_real','ndx_real'])} "
            f"kills={ev['n_kills_fired']}/9"
        )

    # Pick best by (score, then -kills, then sum-Sharpe)
    def best_key(ev):
        s_sum = sum(ev["metrics_by_ds"][ds]["sharpe"]
                    for ds in ["educational", "spy_real", "ndx_real"])
        return (ev["score"], -ev["n_kills_fired"], s_sum)

    best = max(cfg_evals, key=best_key)
    print(f"\n=== BEST cfg: {best['cfg_id']} ===")
    print(f"  Score: {best['score']}/100 ({best['tier']})")
    print(f"  Winner conds: {best['winner_conditions_met']}")
    print(f"  Kills fired: {best['n_kills_fired']}/9")

    # Print kill detail for best
    print("\n--- Kill details (best cfg) ---")
    for k, v in best["kills"].items():
        marker = "❌ FIRED" if v["fired"] else "✓ clean"
        print(f"    {k:50s} {marker}")

    # Build canonical verdict from BEST cfg
    best_cfg = next(c for c in cfgs if c["cfg_id"] == best["cfg_id"])
    metrics_used = best["metrics_by_ds"]

    verdict = {
        "status": (
            "winner" if (best["winner_conditions_met"] and best["score"] >= 90)
            else best["tier"].lower()
        ),
        "tier": best["tier"],
        "total_score": best["score"],
        "winner_conditions_met": best["winner_conditions_met"],
        "criteria": best["criteria"],
        "metrics_used": metrics_used,
        "benchmarks_used": {ds: asdict(BENCHMARKS[ds]) for ds in BENCHMARKS},
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "configs_tested": len(cfgs),
        "primary_citation": (
            "Markowitz (1952) JoF 7(1) DOI 10.1111/j.1540-6261.1952.tb01525.x + "
            "[risk_parity, ch.5] (iter 016 leg) + "
            "Faber (2007) SSRN 962461 + [stocks_on_the_move, p.21-30] + "
            "[volatility_trading, p.218] (iter 064 leg via iter 046+iter 039) + "
            "Whaley (2009) JPM 35(3) DOI 10.3905/JPM.2009.35.3.098 + "
            "Moreira-Muir (2017) JoF 72(4) DOI 10.1111/jofi.12513 + "
            "[advances_fin_ml, p.222-223] (DSR cumulative) + "
            "[advances_fin_ml, p.31-34] (G7) + "
            "[advances_fin_ml, p.208-211] (PBO via CSCV)"
        ),
        "hypothesis_slug": "iter016-iter064-ensemble",
        "cfg_id": best["cfg_id"],
        "cfg": best_cfg,
        "pbo_by_dataset": {ds: pbo_by_ds[ds][1] for ds in pbo_by_ds},
        "gate_details": best["gate_details"],
        "robustness_bonus": best["robustness_bonus"],
        "pre_committed_kills": best["kills"],
        "n_kills_fired": best["n_kills_fired"],
        "iter016_reference_score": iter016_score,
        "iter016_reference_metrics": iter016_metrics,
        "iter064_reference_score": iter064_score,
        "iter064_reference_metrics": iter064_metrics,
        "deltas_vs_064": best["deltas_vs_064"],
        "all_cfg_evaluations": [
            {
                "cfg_id": ev["cfg_id"],
                "score": ev["score"],
                "tier": ev["tier"],
                "winner_conditions_met": ev["winner_conditions_met"],
                "metrics_by_ds": ev["metrics_by_ds"],
                "gates_by_ds": ev["gates_by_ds"],
                "n_kills_fired": ev["n_kills_fired"],
                "deltas_vs_064": ev["deltas_vs_064"],
            }
            for ev in cfg_evals
        ],
    }
    verdict["criteria"]["6_robustness_bonus"] = {
        "points": best["robustness_bonus"]["bonus_awarded"],
        "max": 5,
        "method": "3 non-overlapping sub-windows per dataset; positive count across 9 windows",
        "detail": best["robustness_bonus"],
    }

    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8",
    )

    print(f"\n=== CANONICAL VERDICT ===")
    print(f"Tier: {verdict['tier']}")
    print(f"Total score (frozen + bonus): {best['score']}/100")
    print(f"Winner conditions met: {best['winner_conditions_met']}")
    print(f"Status: {verdict['status']}")
    print(f"Kills fired: {best['n_kills_fired']}/9")


if __name__ == "__main__":
    main()
