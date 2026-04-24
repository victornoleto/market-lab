"""Iter 012 — 7-gate battery + scoring for asymmetric T10Y3M overlay.

Mirrors iter 009's harness; G7 cross-lib delegates to the asymmetric
numpy reference.

Cumulative n_trials after iter 012:
  * Before iter 012: 4249 (per BASE_MEMORY.md frontmatter after iter 011)
  * This iter: 1 combined cfg × 3 datasets = 3 new trials
  * Post iter 012: **4252**
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ITER008_DIR = ITER_DIR.parent / "008-2026-04-24-1411-single-cfg-ex-ante-blend"
ROOT = ITER_DIR.parents[3]

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

from overlay_numpy_reference import (  # noqa: E402
    apply_blend_with_asymmetric_overlay_np,
    cagr_np,
)

OUT_DIR = ITER_DIR
RESULTS_PATH = OUT_DIR / "results.json"

# After iter 011: 4249. Iter 012 adds 1 combined cfg × 3 datasets = 3.
CUMULATIVE_N_TRIALS = 4249 + 3  # = 4252


# ---------------------------------------------------------------------------
# Gate implementations
# ---------------------------------------------------------------------------


def g1_pbo_single_cfg() -> tuple[bool, None]:
    """N=1 combined → PBO undefined. Vacuous PASS."""
    return True, None


def g2_dsr(returns: np.ndarray, cumulative_n_trials: int) -> tuple[bool, float]:
    r = dsr_test(returns, n_trials=cumulative_n_trials)
    return (r.p_value < 0.05, r.p_value)


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
            "window": i, "sharpe": float(block_sharpe),
            "mdd": float(block_mdd), "profitable": is_prof,
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
    p = 1.0 / 5  # block mean 5
    n_resamples = 5000
    sharpes = np.empty(n_resamples)
    for k in range(n_resamples):
        idx = np.empty(n, dtype=np.int64)
        idx[0] = rng.integers(0, n)
        restarts = rng.random(n) < p
        for t in range(1, n):
            idx[t] = rng.integers(0, n) if restarts[t] else (idx[t - 1] + 1) % n
        resampled = r[idx]
        sigma = resampled.std(ddof=0)
        sharpes[k] = 0.0 if sigma <= 1e-12 else resampled.mean() / sigma * np.sqrt(252)
    ci_low = float(np.quantile(sharpes, 0.0005))
    return ci_low > 0, ci_low


def g7_cross_lib(dataset_name: str, engine_cagr: float) -> tuple[bool, float]:
    """Numpy-reference CAGR parity check for combined blend + asymmetric overlay."""
    import importlib.util as _ilu
    spec = _ilu.spec_from_file_location(
        "iter012_run_backtests", ITER_DIR / "run_backtests.py"
    )
    module = _ilu.module_from_spec(spec)
    spec.loader.exec_module(module)
    BLEND_CFG = module.BLEND_CFG
    COST_BPS_PER_LEG = module.COST_BPS_PER_LEG
    DATASETS = module.DATASETS
    T10Y3M_PATH = module.T10Y3M_PATH
    load_paired_returns = module.load_paired_returns
    from asymmetric_term_spread_overlay import OVERLAY_CFG

    ds = DATASETS[dataset_name]
    raw = load_paired_returns(
        ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"]
    )
    eq_col, bd_col = raw.columns
    ts_raw = pd.read_parquet(T10Y3M_PATH)["term_spread"].astype(float)
    ts_on_eq = ts_raw.reindex(raw.index, method="ffill")

    net_np, _, _, _, _ = apply_blend_with_asymmetric_overlay_np(
        raw[eq_col].to_numpy(),
        raw[bd_col].to_numpy(),
        ts_on_eq.to_numpy(),
        target_vol=BLEND_CFG["target_vol"],
        lookback=BLEND_CFG["lookback"],
        max_leverage=BLEND_CFG["max_leverage"],
        smoothing_window=OVERLAY_CFG["smoothing_window"],
        threshold=OVERLAY_CFG["threshold"],
        haircut=OVERLAY_CFG["haircut"],
        lag_bars=OVERLAY_CFG["lag_bars"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    ref_cagr = cagr_np(net_np)
    diff_pp = abs(ref_cagr - engine_cagr) * 100
    return diff_pp <= 3.0, float(diff_pp)


# ---------------------------------------------------------------------------
# Robustness bonus
# ---------------------------------------------------------------------------


def robustness_sub_window_sharpe(returns: pd.Series) -> list[float]:
    n = len(returns)
    third = n // 3
    segs = [returns.iloc[0:third], returns.iloc[third:2 * third], returns.iloc[2 * third:]]
    return [float(sharpe(s)) if len(s) > 1 else 0.0 for s in segs]


def compute_robustness_bonus(
    per_dataset_returns: dict[str, pd.Series],
) -> tuple[int, dict]:
    details: dict[str, dict] = {}
    total = 0
    positives = 0
    for ds, returns in per_dataset_returns.items():
        per_win = robustness_sub_window_sharpe(returns)
        pos = sum(1 for sr in per_win if sr > 0)
        total += len(per_win)
        positives += pos
        details[ds] = {
            "window_sharpes": per_win, "positive_count": pos, "total": len(per_win),
        }
    frac = positives / total if total else 0.0
    pts = int(np.floor(5 * frac + 1e-9)) if frac < 1.0 else 5
    pts = max(0, min(5, pts))
    return pts, {
        "total_sub_windows": total,
        "positive_sub_windows": positives,
        "fraction_positive": frac,
        "bonus_awarded": pts,
        "per_dataset": details,
    }


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


def compute_gates_for_dataset(
    dataset_name: str, data: dict,
) -> tuple[Gates, dict, pd.Series]:
    cfg_id = next(iter(data["runs"][dataset_name].keys()))
    series = data["returns_series"][dataset_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    rets = pd.Series(series["net_returns"], index=idx)
    cfg = data["runs"][dataset_name][cfg_id]
    engine_cagr = cfg["cagr"]

    g1_pass, g1_val = g1_pbo_single_cfg()
    g2_pass, g2_p = g2_dsr(rets.to_numpy(), CUMULATIVE_N_TRIALS)
    g3_pass, g3_det = g3_walk_forward(rets)
    g4_pass, g4_sr = g4_oos_split(rets)
    g5_pass, g5_sr = g5_forward_post2020(rets)
    g6_pass, g6_ci = g6_bootstrap_ci_low(rets.to_numpy())
    g7_pass, g7_pp = g7_cross_lib(dataset_name, engine_cagr)

    gates = Gates(
        g1_pbo=g1_pass, g2_dsr=g2_pass, g3_wf=g3_pass, g4_oos=g4_pass,
        g5_fwd=g5_pass, g6_bootstrap=g6_pass, g7_crosslib=g7_pass,
    )
    detail = {
        "g1_pbo_value": g1_val,
        "g1_note": "N=1 combined (overlay+blend) → PBO undefined; vacuous PASS",
        "g2_dsr_p": g2_p, "g3_wf": g3_det,
        "g4_oos_sharpe": g4_sr, "g5_fwd_sharpe": g5_sr,
        "g6_bootstrap_ci_low": g6_ci,
        "g7_cross_lib_diff_pp": g7_pp,
        "dsr_p_value": g2_p,
    }
    return gates, detail, rets


def build_custom_benchmarks(data: dict) -> dict[str, Benchmark]:
    """Custom edu SPY b&h on overlay window; spy/ndx frozen (full history)."""
    edu_bench = data["benchmarks"]["educational"]
    return {
        "educational": Benchmark(
            sharpe=edu_bench["sharpe"], cagr=edu_bench["cagr"], mdd=edu_bench["mdd"],
            label=f"SPY b&h {edu_bench['first']}→{edu_bench['last']} (iter 012 TLT-aligned)",
        ),
        "spy_real": BENCHMARKS["spy_real"],
        "ndx_real": BENCHMARKS["ndx_real"],
    }


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    custom_benchmarks = build_custom_benchmarks(data)

    cfg_id = data["combined_cfg_id"]
    print(f"Single pre-committed combined cfg: {cfg_id}")
    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        bench = custom_benchmarks[ds]
        edge = run["sharpe"] - bench.sharpe
        print(
            f"  {ds:12s} Sharpe={run['sharpe']:.4f} "
            f"(Δ={edge:+.4f} vs bench {bench.sharpe:.4f} [{bench.label}])"
        )

    gates_by_ds: dict[str, Gates] = {}
    metrics_by_ds: dict[str, DatasetMetrics] = {}
    gate_details: dict[str, dict] = {}
    returns_by_ds: dict[str, pd.Series] = {}

    for ds in ["educational", "spy_real", "ndx_real"]:
        print(f"\n=== Gates: {ds} ===")
        gates, details, rets = compute_gates_for_dataset(ds, data)
        returns_by_ds[ds] = rets
        run = data["runs"][ds][cfg_id]
        metrics_by_ds[ds] = DatasetMetrics(
            sharpe=run["sharpe"], cagr=run["cagr"], mdd=run["mdd"],
            dsr_p_value=details["dsr_p_value"],
        )
        gates_by_ds[ds] = gates
        gate_details[ds] = {
            "cfg_id": cfg_id, "n_passed": gates.n_passed,
            "G1_pbo_pass": gates.g1_pbo, "G1_pbo_value": details["g1_pbo_value"],
            "G1_note": details["g1_note"],
            "G2_dsr_pass": gates.g2_dsr, "G2_dsr_p": details["g2_dsr_p"],
            "G3_wf_pass": gates.g3_wf,
            "G3_wf_profitable": details["g3_wf"].get("profitable_windows", 0),
            "G4_oos_pass": gates.g4_oos, "G4_oos_sharpe": details["g4_oos_sharpe"],
            "G5_fwd_pass": gates.g5_fwd, "G5_fwd_sharpe": details["g5_fwd_sharpe"],
            "G6_boot_pass": gates.g6_bootstrap,
            "G6_boot_ci_low": details["g6_bootstrap_ci_low"],
            "G7_xlib_pass": gates.g7_crosslib,
            "G7_xlib_diff_pp": details["g7_cross_lib_diff_pp"],
        }
        print(f"  gates passed: {gates.n_passed}/7")
        flags = [
            ("G1 PBO", gates.g1_pbo, "N=1 undef"),
            ("G2 DSR p", gates.g2_dsr, f"{details['g2_dsr_p']:.4f}"),
            ("G3 WF", gates.g3_wf, f"{details['g3_wf'].get('profitable_windows', 0)}/8"),
            ("G4 OOS Sh", gates.g4_oos, f"{details['g4_oos_sharpe']:+.3f}"),
            ("G5 FWD Sh", gates.g5_fwd, f"{details['g5_fwd_sharpe']:+.3f}"),
            ("G6 boot CI", gates.g6_bootstrap, f"{details['g6_bootstrap_ci_low']:+.3f}"),
            ("G7 xlib pp", gates.g7_crosslib, f"{details['g7_cross_lib_diff_pp']:.4f}"),
        ]
        for name, passed, val in flags:
            print(f"    {name:12s} {'PASS' if passed else 'FAIL'} ({val})")

    print("\n=== Robustness bonus (criterion 6) ===")
    bonus_pts, bonus_detail = compute_robustness_bonus(returns_by_ds)
    print(f"  {bonus_detail['positive_sub_windows']}/{bonus_detail['total_sub_windows']} "
          f"sub-windows Sharpe > 0 → {bonus_pts} bonus pts")
    for ds, d in bonus_detail["per_dataset"].items():
        sharpes = ", ".join(f"{s:+.2f}" for s in d["window_sharpes"])
        print(f"    {ds:12s} windows=[{sharpes}] positive={d['positive_count']}/{d['total']}")

    print("\n=== Score ===")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS}")
    result = score_strategy(
        metrics=metrics_by_ds, gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS, benchmarks=custom_benchmarks,
    )
    final_score = min(100, result.total_score + bonus_pts)

    verdict = result.to_dict()
    verdict["criteria"]["6_robustness_bonus"] = {
        "points": bonus_pts, "max": 5,
        "method": "3 non-overlapping sub-windows per dataset; positive count across 9 total",
        "detail": bonus_detail,
    }
    verdict["total_score"] = final_score
    verdict["tier"] = tier_from_score(
        final_score, winner_conditions_met=result.winner_conditions_met
    ).value

    verdict["configs_tested"] = 1
    verdict["primary_citation"] = (
        "[regime_change, p.5-6, ch.2]; [risk_parity, p.10-11, ch.1]; "
        "[systematic_trading, p.144, ch.9]; [advances_fin_ml, p.162-164, 208-211, 222-223, 31-34]; "
        "Moreira & Muir (2017), JoF 72(4) DOI 10.1111/jofi.12513; "
        "Estrella & Mishkin (1998), REStat 80(1) DOI 10.1162/003465398557320."
    )
    verdict["hypothesis_slug"] = "asymmetric-term-spread-overlay"
    verdict["pre_committed_cfg"] = {
        "blend": data["blend_cfg"], "overlay": data["overlay_cfg"],
        "combined_cfg_id": cfg_id,
    }
    verdict["gate_details"] = gate_details
    verdict["leg_correlations"] = data["leg_correlations"]
    verdict["benchmarks_used_custom"] = {
        ds: asdict(bm) for ds, bm in custom_benchmarks.items()
    }
    # Iter 008 reference: edu 0.865 / 13.49% / 37.21% ; spy 1.000 / 16.08% / 37.21% ;
    # ndx 1.021 / 17.90% / 37.21%
    verdict["iter008_reference_metrics"] = {
        "educational": {"sharpe": 0.8651, "cagr": 0.1349, "mdd": 0.3721},
        "spy_real":    {"sharpe": 1.0001, "cagr": 0.1608, "mdd": 0.3721},
        "ndx_real":    {"sharpe": 1.0211, "cagr": 0.1790, "mdd": 0.3721},
    }
    verdict["deltas_vs_iter008"] = {
        ds: {
            "sharpe_delta": metrics_by_ds[ds].sharpe - verdict["iter008_reference_metrics"][ds]["sharpe"],
            "cagr_delta": metrics_by_ds[ds].cagr - verdict["iter008_reference_metrics"][ds]["cagr"],
            "mdd_delta": metrics_by_ds[ds].mdd - verdict["iter008_reference_metrics"][ds]["mdd"],
        }
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    verdict["overlay_diagnostics"] = {
        ds: {
            "gate_fire_rate": data["runs"][ds][cfg_id]["gate_fire_rate"],
            "gate_scale_corr": data["runs"][ds][cfg_id]["gate_scale_corr"],
            "gate_bottom20_overlap_frac": data["runs"][ds][cfg_id]["gate_bottom20_overlap_frac"],
        }
        for ds in ["educational", "spy_real", "ndx_real"]
    }
    verdict["status"] = (
        "winner" if result.winner_conditions_met and final_score >= 90
        else verdict["tier"].lower()
    )

    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"\nTier: {verdict['tier']}")
    print(f"Total score (with bonus): {final_score}/100")
    print(f"Winner conditions met: {result.winner_conditions_met}")
    for k, v in verdict["criteria"].items():
        print(f"  {k}: {v['points']}/{v['max']}")

    # Kill criteria post-mortem (pre-committed thresholds from hypothesis.md)
    print("\n=== Kill criteria post-mortem ===")
    kills = []
    spy_sharpe = metrics_by_ds["spy_real"].sharpe
    ndx_sharpe = metrics_by_ds["ndx_real"].sharpe
    iter008 = verdict["iter008_reference_metrics"]
    spy_delta = spy_sharpe - iter008["spy_real"]["sharpe"]
    ndx_delta = ndx_sharpe - iter008["ndx_real"]["sharpe"]
    # Kill #1: Sharpe regresses vs iter 008 on BOTH real slots.
    if spy_delta < 0 and ndx_delta < 0:
        kills.append(
            f"Kill #1 spy_real Δ={spy_delta:+.4f} AND ndx_real Δ={ndx_delta:+.4f} "
            f"— BOTH real slots regress vs iter 008 → asymmetric-equity-only principle falsified"
        )
    # Kill #2: CAGR < 0.75 × bench on any dataset.
    bench_cagr = {"educational": 0.1147, "spy_real": 0.1497, "ndx_real": 0.1918}
    for ds, bc in bench_cagr.items():
        c = metrics_by_ds[ds].cagr
        if c < 0.75 * bc:
            kills.append(f"Kill #2 {ds} CAGR {c:.2%} < 0.75×{bc:.2%} = {0.75*bc:.2%}")
    # Kill #3: score < 70.
    if final_score < 70:
        kills.append(f"Kill #3 score {final_score} < 70 threshold")
    # Kill #4: gate-fire/bottom-20% overlap ≥ 60% on any dataset → redundancy.
    for ds in ["educational", "spy_real", "ndx_real"]:
        ov = verdict["overlay_diagnostics"][ds]["gate_bottom20_overlap_frac"]
        if ov is not None and not np.isnan(ov) and ov >= 0.60:
            kills.append(
                f"Kill #4 {ds} gate-fire/bottom-20%-scale overlap {ov:.1%} ≥ 60% "
                f"→ 5d-smoothed signal STILL redundant with variance-scaling"
            )
    # Kill #5: xlib > 3pp CAGR.
    for ds in ["educational", "spy_real", "ndx_real"]:
        pp = gate_details[ds]["G7_xlib_diff_pp"]
        if pp > 3.0:
            kills.append(f"Kill #5 {ds} cross-lib ΔCAGR {pp:.3f}pp > 3.0pp")
    if kills:
        print("  TRIGGERED:")
        for k in kills:
            print(f"    - {k}")
    else:
        print("  NONE triggered.")
    verdict["kill_criteria_triggered"] = kills
    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
