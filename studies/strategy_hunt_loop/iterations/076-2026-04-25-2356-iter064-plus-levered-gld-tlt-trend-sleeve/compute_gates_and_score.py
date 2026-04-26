"""Iter 076 — 7-gate battery + score for iter 064 + LEVERED GLD/TLT trend sleeve ensemble.

Multi-cfg grid (N=20 = 4 target_vol × 5 w_sleeve). G1 PBO via CSCV (10
blocks, grid-level). G2 DSR computed under v2 native convention
(per-iter n_trials = 20). cumulative_n_trials advanced to 4402 + 60 =
4462 for audit trail only.

Pre-committed kill criteria (from hypothesis.md §"Kill criteria"):

  A — borrow-drag math wrong (G7 abs_diff_pp > 0 on any cfg)
  B — At target_vol=0.30, sleeve gross CAGR ≤ 6% on ≥ 2 datasets
  C — Best combined cfg's Sharpe < iter 064 - 0.05 on ≥ 2 datasets
  D — Best cfg score < 75 (drops below STRONG)
  E — G7 cross-lib > 3 pp absolute CAGR difference on ≥ 1 ds
  F — PBO grid-level > 0.5 on ≥ 2 datasets
  G — DSR worst-p ≥ 0.05 on best cfg (v2 convention; winner cond #3 fails)

Citations
---------
* `[advances_fin_ml, p.208-211]` — PBO via CSCV.
* `[advances_fin_ml, p.222-223]` — DSR with n_trials (cumulative v1 audit; per-iter v2 native).
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
* `[leverage_for_the_long_run, ch.5]` — leg-level borrow drag.
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

# v1 audit DSR — cumulative across all 76 iters
CUMULATIVE_N_TRIALS_V1 = 4402 + 60  # = 4462 (76th iter contributes 20 cfgs × 3 ds)
# v2 operational native — per-iter convention
N_TRIALS_PER_ITER_V2 = 20
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


def evaluate_cfg_cached(
    cfg_id: str, data: dict, gates_cache: dict, iter064_metrics: dict,
    *, n_trials_for_dsr: int, n_trials_for_score: int,
) -> dict:
    gates_by_ds: dict[str, Gates] = {}
    metrics_by_ds: dict[str, DatasetMetrics] = {}
    gate_details: dict[str, dict] = {}
    returns_by_ds: dict[str, pd.Series] = {}

    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        cache = gates_cache[cfg_id][ds]
        rets = cache["rets"]
        pbo_p, pbo_d = cache["pbo_p"], cache["pbo_d"]
        g2_p, p_val = g2_dsr_raw(rets.to_numpy(), n_trials_for_dsr)
        g3_p, g3_d = cache["g3"]
        g4_p, g4_s = cache["g4"]
        g5_p, g5_s = cache["g5"]
        g6_p, g6_c = cache["g6"]
        g7_p, g7_d = cache["g7"]
        gates = Gates(g1_pbo=pbo_p, g2_dsr=g2_p, g3_wf=g3_p, g4_oos=g4_p,
                      g5_fwd=g5_p, g6_bootstrap=g6_p, g7_crosslib=g7_p)
        detail = {
            "G1_pbo_pass": pbo_p, "G1_pbo_value": pbo_d.get("pbo_value", float("nan")),
            "G1_n_strategies": pbo_d.get("n_strategies", 0),
            "G2_dsr_pass": g2_p, "G2_dsr_p_raw": p_val, "G2_alpha_raw": RAW_ALPHA,
            "G2_n_trials_used": n_trials_for_dsr,
            "G3_wf_pass": g3_p, "G3_wf_profitable": g3_d.get("profitable_windows", 0),
            "G3_wf_windows": g3_d.get("windows", []),
            "G4_oos_pass": g4_p, "G4_oos_sharpe": g4_s,
            "G5_fwd_pass": g5_p, "G5_fwd_sharpe": g5_s,
            "G6_boot_pass": g6_p, "G6_boot_ci_low": g6_c,
            "G7_xlib_pass": g7_p, "G7_xlib_diff_pp": g7_d,
            "dsr_p_value": p_val,
        }
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

    kills: dict = {}
    # A: G7 abs_diff_pp > 0 on any cfg (borrow-drag math wrong)
    max_xlib_thiscfg = max(gate_details[ds]["G7_xlib_diff_pp"]
                           for ds in ["educational", "spy_real", "ndx_real"])
    kills["A_borrow_math_wrong_g7_above_0"] = {
        "fired": max_xlib_thiscfg > 0.001,  # tolerate 1e-3 pp numerical noise
        "max_diff_pp": float(max_xlib_thiscfg),
    }

    # B: At target_vol=0.30, sleeve gross CAGR ≤ 6% on ≥ 2 datasets
    # (we evaluate this kill globally across ALL tv=0.30 cfgs, not per-cfg —
    # since it's a sleeve-mechanism kill, not an ensemble-cfg kill)
    sleeve_cagrs_at_tv030 = {}
    for ds in ["educational", "spy_real", "ndx_real"]:
        # Find any cfg with target_vol=0.30 and read its sleeve CAGR
        for cid, run in data["runs"][ds].items():
            if run.get("target_vol") == 0.30:
                sleeve_cagrs_at_tv030[ds] = float(run["r_sleeve_cagr"])
                break
    n_low_sleeve_cagr = sum(1 for v in sleeve_cagrs_at_tv030.values() if v <= 0.06)
    kills["B_sleeve_gross_cagr_below_6pct_at_tv030_2ds"] = {
        "fired": n_low_sleeve_cagr >= 2,
        "n_below_6pct": n_low_sleeve_cagr,
        "sleeve_cagrs_at_tv030": sleeve_cagrs_at_tv030,
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
    pbo_per_ds = {ds: float(gates_cache[cfg_id][ds]["pbo_d"]["pbo_value"])
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

    n_kills_fired = sum(1 for v in kills.values() if v["fired"])

    return {
        "cfg_id": cfg_id, "score": score, "tier": tier.value,
        "winner_conditions_met": result.winner_conditions_met,
        "criteria": result.criteria,
        "metrics_by_ds": {ds: asdict(metrics_by_ds[ds]) for ds in metrics_by_ds},
        "gates_by_ds": {ds: gates_by_ds[ds].n_passed for ds in gates_by_ds},
        "gate_details": gate_details, "robustness_bonus": bonus_detail,
        "kills": kills, "n_kills_fired": n_kills_fired,
        "deltas_vs_064": deltas_064,
    }


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    cfgs = data["configs"]
    iter064_score = _load_iter_score(ITER_064_DIR)
    iter064_metrics = _load_iter_metrics(ITER_064_DIR)

    print(f"Configs: {len(cfgs)}")
    print(f"v1 audit cumulative_n_trials = {CUMULATIVE_N_TRIALS_V1} (= 4402 + 60)")
    print(f"v2 native per-iter n_trials  = {N_TRIALS_PER_ITER_V2}")
    print(f"raw α = {RAW_ALPHA}")
    print(f"iter 064 reference score: {iter064_score}")

    print("\n=== G1 PBO (grid-level CSCV across 20 cfgs) ===")
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

    print(f"\n=== Pre-computing slow gates once per (cfg, ds) ===")
    gates_cache: dict = {}
    for cfg in cfgs:
        cid = cfg["cfg_id"]
        gates_cache[cid] = {}
        for ds in ["educational", "spy_real", "ndx_real"]:
            s = data["returns_series"][ds][cid]
            idx = pd.to_datetime(s["index"])
            rets = pd.Series(s["net_returns"], index=idx)
            pbo_p, pbo_d = pbo_by_ds[ds]
            g3_p, g3_d = g3_walk_forward(rets)
            g4_p, g4_s = g4_oos_split(rets)
            g5_p, g5_s = g5_forward_post2020(rets)
            g6_p, g6_c = g6_bootstrap_ci_low(rets.to_numpy())
            g7_p, g7_d = g7_cross_lib(ds, cid, data)
            gates_cache[cid][ds] = {
                "rets": rets,
                "pbo_p": pbo_p, "pbo_d": pbo_d,
                "g3": (g3_p, g3_d), "g4": (g4_p, g4_s),
                "g5": (g5_p, g5_s), "g6": (g6_p, g6_c),
                "g7": (g7_p, g7_d),
            }
        print(f"  {cid}: cached")

    # Evaluate ALL cfgs under v2 native (per-iter DSR)
    print(f"\n=== Per-cfg evaluation (v2 native DSR n_trials={N_TRIALS_PER_ITER_V2}) ===")
    cfg_evals = []
    for cfg in cfgs:
        ev = evaluate_cfg_cached(
            cfg["cfg_id"], data, gates_cache, iter064_metrics,
            n_trials_for_dsr=N_TRIALS_PER_ITER_V2,
            n_trials_for_score=N_TRIALS_PER_ITER_V2,
        )
        cfg_evals.append(ev)
        s_e = ev["metrics_by_ds"]["educational"]["sharpe"]
        s_s = ev["metrics_by_ds"]["spy_real"]["sharpe"]
        s_n = ev["metrics_by_ds"]["ndx_real"]["sharpe"]
        c_e = ev["metrics_by_ds"]["educational"]["cagr"]
        c_s = ev["metrics_by_ds"]["spy_real"]["cagr"]
        c_n = ev["metrics_by_ds"]["ndx_real"]["cagr"]
        print(
            f"  {cfg['cfg_id']:42s} score={ev['score']}/100 ({ev['tier']:9s}) "
            f"WC={'Y' if ev['winner_conditions_met'] else 'n'} "
            f"S={s_e:.3f}/{s_s:.3f}/{s_n:.3f} "
            f"C={c_e:.2%}/{c_s:.2%}/{c_n:.2%} "
            f"gates={'/'.join(str(ev['gates_by_ds'][d]) for d in ['educational','spy_real','ndx_real'])} "
            f"kills={ev['n_kills_fired']}/7"
        )

    def best_key(ev):
        s_sum = sum(ev["metrics_by_ds"][ds]["sharpe"]
                    for ds in ["educational", "spy_real", "ndx_real"])
        return (ev["score"], -ev["n_kills_fired"], s_sum)
    best = max(cfg_evals, key=best_key)
    print(f"\n  BEST cfg (v2 native): {best['cfg_id']} score={best['score']} "
          f"tier={best['tier']} WC={best['winner_conditions_met']} "
          f"kills={best['n_kills_fired']}/7")

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
        "cumulative_n_trials": CUMULATIVE_N_TRIALS_V1,
        "configs_tested": len(cfgs),
        "primary_citation": (
            "[leverage_for_the_long_run, ch.5] (Hsiao-Williams 2017 borrow primitive) + "
            "Faber (2007) SSRN 962461 + [stocks_on_the_move, p.81] + "
            "[risk_parity, ch.5] (Asness-Frazzini-Pedersen 2012 FAJ 68(1)) + "
            "Erb-Harvey (2006) FAJ 62(2) DOI 10.2469/faj.v62.i2.4084 + "
            "[volatility_trading, p.218] + Markowitz (1952) JoF 7(1) "
            "DOI 10.1111/j.1540-6261.1952.tb01525.x + "
            "Frazzini-Pedersen (2014) JFE 111(1) DOI 10.1016/j.jfineco.2013.10.005 + "
            "[advances_fin_ml, p.222-223] (DSR per-iter v2) + "
            "[advances_fin_ml, p.31-34] (G7) + "
            "[advances_fin_ml, p.208-211] (PBO via CSCV)"
        ),
        "hypothesis_slug": "iter064-plus-levered-gld-tlt-trend-sleeve",
        "iter_id": 76,
        "cfg_id": best["cfg_id"],
        "cfg": best_cfg,
        "pbo_by_dataset": {ds: pbo_by_ds[ds][1] for ds in pbo_by_ds},
        "gate_details": best["gate_details"],
        "robustness_bonus": best["robustness_bonus"],
        "pre_committed_kills": best["kills"],
        "n_kills_fired": best["n_kills_fired"],
        "iter064_reference_score": iter064_score,
        "iter064_reference_metrics": iter064_metrics,
        "deltas_vs_064": best["deltas_vs_064"],
        "v2_meta": {
            "convention": "v2 native per-iter",
            "n_trials": N_TRIALS_PER_ITER_V2,
        },
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
    out_path = OUT_DIR / "verdict.json"
    out_path.write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8",
    )
    print(f"  wrote {out_path.name}")

    print("\n  --- Kill details (best cfg, v2 native) ---")
    for k, v in best["kills"].items():
        marker = "❌ FIRED" if v["fired"] else "✓ clean"
        print(f"      {k:50s} {marker}")


if __name__ == "__main__":
    main()
