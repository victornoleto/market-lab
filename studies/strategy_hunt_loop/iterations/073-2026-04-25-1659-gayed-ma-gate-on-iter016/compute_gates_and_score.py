"""Iter 073 — 7-gate battery + scoring for Gayed-gate × vol-managed stack.

Multi-cfg grid (N=4 sensitivity sweep). G1 PBO via CSCV (10 blocks).
G2 DSR uses raw α=0.05 with cumulative_n_trials = 4360 (4348 + 12).
G7 cross-lib parity via numpy reference (computed in run_backtests).

Pre-committed kill criteria (from hypothesis.md):
  A — Sharpe < (bench + 0.10) on ≥ 2 ds
  B — Score < 75 (not STRONG)
  C — G3 walk-forward < 6/8 on ≥ 2 ds
  D — gate_on bar fraction < 0.55 or > 0.92 on any ds
  E — corr(net_073_best, net_016) > 0.985 on ≥ 2 ds
  F — PBO grid > 0.5 on any ds
  G — G7 cross-lib > 0.5 pp on any cfg × ds
  H — DSR worst p > 0.10
  I — best cfg edu CAGR < 9.18%
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

sys.path.insert(0, str(ROOT / "studies" / "strategy_hunt_loop"))
sys.path.insert(0, str(ITER_DIR))

from scoring import (  # noqa: E402
    BENCHMARKS, Benchmark, DatasetMetrics, Gates,
    score_strategy, tier_from_score,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    max_drawdown, sharpe,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_test  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as pbo_test  # noqa: E402

OUT_DIR = ITER_DIR
RESULTS_PATH = OUT_DIR / "results.json"

CUMULATIVE_N_TRIALS = 4348 + 4 * 3  # = 4360
RAW_ALPHA = 0.05


def g1_pbo_grid(returns_matrix: np.ndarray) -> tuple[bool, dict]:
    if returns_matrix.shape[1] < 2:
        return True, {"pbo_value": float("nan"), "n_combinations": 0,
                       "small_n_warning": "N<2 cfgs — PBO vacuous"}
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


def build_custom_benchmarks(data: dict) -> dict[str, Benchmark]:
    """Educational benchmark re-measured on iter 016's IEF-aligned window.
    spy_real / ndx_real remain frozen."""
    edu_bench = data["benchmarks"]["educational"]
    return {
        "educational": Benchmark(
            sharpe=edu_bench["sharpe"], cagr=edu_bench["cagr"], mdd=edu_bench["mdd"],
            label=f"SPY b&h {edu_bench['first']}→{edu_bench['last']} (IEF-aligned)",
        ),
        "spy_real": BENCHMARKS["spy_real"],
        "ndx_real": BENCHMARKS["ndx_real"],
    }


def compute_corr_with_iter016(cfg_id: str, ds: str, data: dict) -> float:
    """Compute correlation between iter 073 cfg and iter 016 net returns
    on the common date intersection (after both warm-ups)."""
    iter016_results_path = ITER_016_DIR / "results.json"
    if not iter016_results_path.exists():
        return float("nan")
    iter016_data = json.loads(iter016_results_path.read_text())
    rs016 = iter016_data["returns_series"][ds]
    cfg016 = next(iter(rs016.keys()))
    s016 = pd.Series(
        rs016[cfg016]["net_returns"],
        index=pd.to_datetime(rs016[cfg016]["index"]),
    )
    rs073 = data["returns_series"][ds][cfg_id]
    s073 = pd.Series(
        rs073["net_returns"],
        index=pd.to_datetime(rs073["index"]),
    )
    common = s016.index.intersection(s073.index)
    if len(common) < 30:
        return float("nan")
    return float(s016.loc[common].corr(s073.loc[common]))


def evaluate_cfg(
    cfg_id: str, data: dict, pbo_by_ds: dict, custom_bms: dict[str, Benchmark],
) -> dict:
    gates_by_ds: dict[str, Gates] = {}
    metrics_by_ds: dict[str, DatasetMetrics] = {}
    gate_details: dict[str, dict] = {}
    returns_by_ds: dict[str, pd.Series] = {}
    corr016_by_ds: dict[str, float] = {}

    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        pbo_p, pbo_d = pbo_by_ds[ds]
        gates, detail, rets = compute_per_dataset_gates(cfg_id, ds, data, pbo_p, pbo_d)
        returns_by_ds[ds] = rets
        metrics_by_ds[ds] = DatasetMetrics(
            sharpe=run["sharpe"], cagr=run["cagr"], mdd=run["mdd"],
            dsr_p_value=detail["dsr_p_value"],
        )
        gates_by_ds[ds] = gates
        gate_details[ds] = detail
        corr016_by_ds[ds] = compute_corr_with_iter016(cfg_id, ds, data)

    bonus_pts, bonus_detail = compute_robustness_bonus(returns_by_ds)
    # Score against custom benchmarks (edu re-measured on iter 016 window).
    result = score_strategy(
        metrics=metrics_by_ds, gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        benchmarks=custom_bms,
    )
    score_with_bonus = min(100, result.total_score + bonus_pts)
    tier = tier_from_score(score_with_bonus, winner_conditions_met=result.winner_conditions_met)

    # Pre-committed kills
    kills = {}
    # A: Sharpe < bench + 0.10 on ≥ 2 ds
    edges = {
        ds: float(metrics_by_ds[ds].sharpe - custom_bms[ds].sharpe)
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    n_below_010 = sum(1 for v in edges.values() if v < 0.10)
    kills["A_sharpe_edge_below_010"] = {
        "fired": n_below_010 >= 2, "n_below_010": n_below_010, "edges": edges,
    }
    # B: Score < 75 (not STRONG)
    kills["B_score_below_75"] = {"fired": score_with_bonus < 75, "score": score_with_bonus}
    # C: G3 walk-forward < 6/8 on ≥ 2 ds
    wf = {ds: gate_details[ds]["G3_wf_profitable"] for ds in gate_details}
    n_low_wf = sum(1 for v in wf.values() if v < 6)
    kills["C_g3_wf_below_6_on_2ds"] = {"fired": n_low_wf >= 2, "wf_windows": wf}
    # D: gate_on bar fraction out of [0.55, 0.92]
    on_frac = {
        ds: float(data["runs"][ds][cfg_id]["gate_on_fraction"])
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    out_of_range = {ds: not (0.55 <= v <= 0.92) for ds, v in on_frac.items()}
    kills["D_gate_fraction_out_of_range"] = {
        "fired": any(out_of_range.values()),
        "gate_on_fraction": on_frac,
        "out_of_range": out_of_range,
    }
    # E: corr(net_073, net_016) > 0.985 on ≥ 2 ds
    n_high_corr = sum(1 for v in corr016_by_ds.values()
                      if not np.isnan(v) and v > 0.985)
    kills["E_corr_with_iter016_above_0985"] = {
        "fired": n_high_corr >= 2,
        "corr_with_iter016": corr016_by_ds,
    }
    # F: PBO > 0.5 on any ds
    max_pbo = max(pbo_by_ds[ds][1].get("pbo_value", 0.0) for ds in pbo_by_ds)
    kills["F_pbo_above_05"] = {"fired": max_pbo > 0.5, "max_pbo": float(max_pbo)}
    # G: G7 cross-lib > 0.5 pp on any ds
    max_xlib = max(
        gate_details[ds]["G7_xlib_diff_pp"]
        for ds in ["educational", "spy_real", "ndx_real"]
    )
    kills["G_g7_above_05pp"] = {"fired": max_xlib > 0.5, "max_xlib_pp": float(max_xlib)}
    # H: DSR worst p > 0.10
    worst_p = max(gate_details[ds]["dsr_p_value"]
                  for ds in ["educational", "spy_real", "ndx_real"])
    kills["H_dsr_worst_p_above_010"] = {"fired": worst_p > 0.10, "worst_p": float(worst_p)}
    # I: edu CAGR < 9.18%
    edu_cagr = float(data["runs"]["educational"][cfg_id]["cagr"])
    kills["I_edu_cagr_below_0918"] = {"fired": edu_cagr < 0.0918, "edu_cagr": edu_cagr}

    return {
        "cfg_id": cfg_id,
        "score": score_with_bonus,
        "score_base": result.total_score,
        "robustness_bonus": bonus_pts,
        "tier": tier.value,
        "winner_conditions_met": result.winner_conditions_met,
        "metrics_by_ds": {ds: asdict(metrics_by_ds[ds]) for ds in metrics_by_ds},
        "gates_by_ds": {ds: asdict(gates_by_ds[ds]) for ds in gates_by_ds},
        "gate_details": gate_details,
        "edges_vs_custom_bench": edges,
        "robustness_detail": bonus_detail,
        "criteria_detail": result.criteria,
        "corr_with_iter016": corr016_by_ds,
        "kills": kills,
        "n_kills_fired": sum(1 for k in kills.values() if k["fired"]),
    }


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    custom_bms = build_custom_benchmarks(data)
    cfg_ids = [c["cfg_id"] for c in data["configs"]]
    print(f"N configs: {len(cfg_ids)}, datasets: 3")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (4348 + 12)")

    # G1 PBO computed ONCE per dataset across all 4 cfgs (grid-level CSCV).
    print("\n=== G1 PBO (grid-level CSCV across 4 cfgs) ===")
    pbo_by_ds: dict[str, tuple[bool, dict]] = {}
    for ds in ["educational", "spy_real", "ndx_real"]:
        mat, _ = get_returns_matrix(data, ds)
        pbo_p, pbo_d = g1_pbo_grid(mat)
        pbo_by_ds[ds] = (pbo_p, pbo_d)
        v = pbo_d.get("pbo_value", float("nan"))
        print(f"  {ds:12s} N={pbo_d.get('n_strategies', 0)} "
              f"PBO={v:.4f} ({'PASS' if pbo_p else 'FAIL'})")

    # Per-cfg evaluation.
    cfg_evals: list[dict] = []
    for cfg_id in cfg_ids:
        print(f"\n=== Evaluating {cfg_id} ===")
        ev = evaluate_cfg(cfg_id, data, pbo_by_ds, custom_bms)
        cfg_evals.append(ev)
        for ds in ["educational", "spy_real", "ndx_real"]:
            n_passed = ev["gates_by_ds"][ds]["g1_pbo"] + ev["gates_by_ds"][ds]["g2_dsr"] + \
                       ev["gates_by_ds"][ds]["g3_wf"] + ev["gates_by_ds"][ds]["g4_oos"] + \
                       ev["gates_by_ds"][ds]["g5_fwd"] + ev["gates_by_ds"][ds]["g6_bootstrap"] + \
                       ev["gates_by_ds"][ds]["g7_crosslib"]
            run = data["runs"][ds][cfg_id]
            print(
                f"  {ds:12s} S={run['sharpe']:.4f} (Δ{ev['edges_vs_custom_bench'][ds]:+.4f}) "
                f"CAGR={run['cagr']:+.2%} MDD={run['mdd']:.2%} "
                f"DSR_p={ev['gate_details'][ds]['dsr_p_value']:.4f} gates={n_passed}/7"
            )
        kills_fired = [k for k, v in ev["kills"].items() if v["fired"]]
        print(f"  score={ev['score']}/100 ({ev['score_base']}+{ev['robustness_bonus']} bonus) "
              f"tier={ev['tier']} kills_fired={len(kills_fired)}/9 → {kills_fired}")

    # Pick best by composite (highest min-Sharpe across 3 ds).
    def cfg_composite(ev: dict) -> tuple[float, int]:
        min_sharpe = min(ev["metrics_by_ds"][ds]["sharpe"] for ds in
                         ["educational", "spy_real", "ndx_real"])
        return (min_sharpe, ev["score"])
    best = max(cfg_evals, key=cfg_composite)
    print(f"\n=== Best cfg (highest min-Sharpe; tiebreak score): {best['cfg_id']} ===")
    print(f"  score={best['score']}/100 tier={best['tier']} "
          f"winner_conditions_met={best['winner_conditions_met']}")

    # Build verdict.json from BEST cfg.
    metrics_used = best["metrics_by_ds"]
    gates_used = {ds: best["gates_by_ds"][ds] for ds in best["gates_by_ds"]}

    verdict = {
        "status": best["tier"].lower(),
        "tier": best["tier"],
        "total_score": best["score"],
        "winner_conditions_met": best["winner_conditions_met"],
        "criteria": best["criteria_detail"],
        "metrics_used": metrics_used,
        "benchmarks_used": {
            ds: {"sharpe": custom_bms[ds].sharpe,
                  "cagr": custom_bms[ds].cagr,
                  "mdd": custom_bms[ds].mdd,
                  "label": custom_bms[ds].label}
            for ds in custom_bms
        },
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "configs_tested": len(cfg_ids),
        "primary_citation": "[leverage_for_the_long_run, p.13, p.16, p.21]",
        "hypothesis_slug": "gayed-ma-gate-on-iter016",
        "best_cfg": best["cfg_id"],
        "all_cfgs_summary": [
            {
                "cfg_id": ev["cfg_id"], "score": ev["score"], "tier": ev["tier"],
                "min_sharpe": min(ev["metrics_by_ds"][ds]["sharpe"]
                                  for ds in ["educational", "spy_real", "ndx_real"]),
                "n_kills_fired": ev["n_kills_fired"],
                "edges_vs_custom_bench": ev["edges_vs_custom_bench"],
            }
            for ev in cfg_evals
        ],
        "best_cfg_kills": best["kills"],
        "best_cfg_corr_with_iter016": best["corr_with_iter016"],
        "best_cfg_robustness": best["robustness_detail"],
        "pbo_by_dataset": {ds: pbo_by_ds[ds][1] for ds in pbo_by_ds},
        "g3_wf_detail_best": {
            ds: best["gate_details"][ds]["G3_wf_windows"]
            for ds in ["educational", "spy_real", "ndx_real"]
        },
        "all_cfgs_full_eval": [
            {
                "cfg_id": ev["cfg_id"], "score": ev["score"], "tier": ev["tier"],
                "metrics_by_ds": ev["metrics_by_ds"],
                "edges_vs_custom_bench": ev["edges_vs_custom_bench"],
                "gates_by_ds": ev["gates_by_ds"],
                "kills": ev["kills"],
                "corr_with_iter016": ev["corr_with_iter016"],
            }
            for ev in cfg_evals
        ],
    }

    out = ITER_DIR / "verdict.json"
    out.write_text(json.dumps(verdict, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
