"""Iter 037 — 7-gate battery + scoring for leverage-preserved 3-leg static stack.

Pattern adapted verbatim from iter 036 (vacuous G1 PASS for N=1, same
G2-G7 definitions). G7 cross-lib uses the local
``numpy_reference_stacked_3leg.apply_static_stack_3leg_np`` (vendored
verbatim from iter 036 / 034 — the 3-leg static-stack primitive is
asset-agnostic).

Cumulative n_trials after iter 037:
  * Before iter 037: 4297 (per BASE_MEMORY.md frontmatter, post-iter-036)
  * This iter: 1 cfg × 3 datasets = 3 new trials
  * Post iter 037: **4300**
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
ITER015_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "015-2026-04-24-1704-return-stacked-static-ntsx"
ITER035_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "035-2026-04-25-0142-static-stack-spy-gld"
ITER036_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "036-2026-04-25-0206-ntsx-3leg-additive-spy-ief-gld"

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

from numpy_reference_stacked_3leg import (  # noqa: E402
    apply_static_stack_3leg_np,
    cagr_np,
)

OUT_DIR = ITER_DIR
RESULTS_PATH = OUT_DIR / "results.json"

# Iter 036 cumulative = 4297 (per BASE_MEMORY.md frontmatter).
# This iter adds 1 cfg × 3 datasets = 3 trials.
CUMULATIVE_N_TRIALS = 4297 + 1 * 3  # = 4300


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


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def g1_pbo_single_cfg() -> tuple[bool, None]:
    """N=1 → PBO undefined; vacuous PASS (per iter 008/010/015/033/034/035/036 rationale)."""
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


def g7_cross_lib(
    dataset_name: str,
    cfg: dict,
    engine_cagr: float,
) -> tuple[bool, float]:
    from run_backtests import load_triple_returns, DATASETS, COST_BPS_PER_LEG
    ds = DATASETS[dataset_name]
    raw = load_triple_returns(
        ds["equity_symbol"], ds["bond_symbol"], ds["gold_symbol"], ds["start"], ds["end"],
    )
    eq_col, bd_col, gld_col = raw.columns
    net_np, _, _ = apply_static_stack_3leg_np(
        raw[eq_col].to_numpy(),
        raw[bd_col].to_numpy(),
        raw[gld_col].to_numpy(),
        eq_w=cfg["eq_w"],
        bd_short_w=cfg["bd_w"],
        bd_long_w=cfg["gld_w"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    ref_cagr = cagr_np(net_np)
    diff_pp = abs(ref_cagr - engine_cagr) * 100
    return diff_pp <= 3.0, float(diff_pp)


# ---------------------------------------------------------------------------
# Robustness
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
# Compute gates per dataset
# ---------------------------------------------------------------------------


def compute_gates_for_dataset(
    dataset_name: str, data: dict
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
    g7_pass, g7_pp = g7_cross_lib(dataset_name, cfg, engine_cagr)

    gates = Gates(
        g1_pbo=g1_pass, g2_dsr=g2_pass, g3_wf=g3_pass, g4_oos=g4_pass,
        g5_fwd=g5_pass, g6_bootstrap=g6_pass, g7_crosslib=g7_pass,
    )
    detail = {
        "g1_pbo_value": g1_val,
        "g1_note": "N=1 → PBO undefined; vacuous PASS (no grid, no overfit)",
        "g2_dsr_p": g2_p,
        "g3_wf": g3_det,
        "g4_oos_sharpe": g4_sr,
        "g5_fwd_sharpe": g5_sr,
        "g6_bootstrap_ci_low": g6_ci,
        "g7_cross_lib_diff_pp": g7_pp,
        "dsr_p_value": g2_p,
    }
    return gates, detail, rets


def build_custom_benchmarks(data: dict) -> dict[str, Benchmark]:
    """Custom edu benchmark on iter 037's GLD-aligned 21y window (matches
    iter 035/036 verbatim). spy_real / ndx_real benchmarks remain frozen
    to scoring.BENCHMARKS for cross-iter comparability."""
    edu_bench = data["benchmarks"]["educational"]
    return {
        "educational": Benchmark(
            sharpe=edu_bench["sharpe"],
            cagr=edu_bench["cagr"],
            mdd=edu_bench["mdd"],
            label=f"SPY b&h {edu_bench['first']}→{edu_bench['last']} (iter 037 GLD-aligned)",
        ),
        "spy_real": BENCHMARKS["spy_real"],
        "ndx_real": BENCHMARKS["ndx_real"],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    custom_benchmarks = build_custom_benchmarks(data)
    iter015_ref = _load_reference(ITER015_DIR)
    iter035_ref = _load_reference(ITER035_DIR)
    iter036_ref = _load_reference(ITER036_DIR)

    cfg_id = data["configs"][0]["cfg_id"]
    print(f"Single pre-committed cfg: {cfg_id}")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (4297 + 3)")
    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        bench = custom_benchmarks[ds]
        edge = run["sharpe"] - bench.sharpe
        edge_frozen = run["sharpe"] - BENCHMARKS[ds].sharpe
        edge_iter015 = run["sharpe"] - iter015_ref[ds]["sharpe"]
        edge_iter035 = run["sharpe"] - iter035_ref[ds]["sharpe"]
        edge_iter036 = run["sharpe"] - iter036_ref[ds]["sharpe"]
        print(
            f"  {ds:12s} Sharpe={run['sharpe']:.4f} (Δ vs custom {edge:+.4f}, "
            f"Δ vs frozen {edge_frozen:+.4f}, Δ015 {edge_iter015:+.4f}, "
            f"Δ035 {edge_iter035:+.4f}, Δ036 {edge_iter036:+.4f})"
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
            "cfg_id": cfg_id,
            "n_passed": gates.n_passed,
            "G1_pbo_pass": gates.g1_pbo,
            "G1_pbo_value": details["g1_pbo_value"],
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
        sharpes_str = ", ".join(f"{s:+.2f}" for s in d["window_sharpes"])
        print(f"    {ds:12s} windows=[{sharpes_str}] positive={d['positive_count']}/{d['total']}")

    print("\n=== Score (with custom benchmark for educational) ===")
    result = score_strategy(
        metrics=metrics_by_ds,
        gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        benchmarks=custom_benchmarks,
    )
    final_score = min(100, result.total_score + bonus_pts)

    print("\n=== Strict winner-cond check vs FROZEN benchmarks (per WINNER_AND_RANKING.md) ===")
    result_frozen = score_strategy(
        metrics=metrics_by_ds,
        gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        benchmarks=BENCHMARKS,
    )
    final_score_frozen = min(100, result_frozen.total_score + bonus_pts)
    print(f"  custom-bench score: {final_score}/100 (winner_conds={result.winner_conditions_met})")
    print(f"  frozen-bench score: {final_score_frozen}/100 (winner_conds={result_frozen.winner_conditions_met})")

    canonical = result_frozen
    canonical_score = final_score_frozen

    verdict = canonical.to_dict()
    verdict["criteria"]["6_robustness_bonus"] = {
        "points": bonus_pts,
        "max": 5,
        "method": "3 non-overlapping sub-windows per dataset; positive count across 9 total windows",
        "detail": bonus_detail,
    }
    verdict["total_score"] = canonical_score
    verdict["tier"] = tier_from_score(
        canonical_score, winner_conditions_met=canonical.winner_conditions_met,
    ).value

    verdict["configs_tested"] = 1
    verdict["primary_citation"] = (
        "[risk_parity, ch.5]; [risk_parity, p.5, p.10-11, ch.1]; "
        "[leverage_for_the_long_run, p.19-20]; "
        "Asness-Moskowitz-Pedersen (2013), JF 68(3), DOI 10.1111/jofi.12021; "
        "Erb & Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084; "
        "Koijen-Moskowitz-Pedersen-Vrugt (2018), JFE 127(2) §3, DOI 10.1016/j.jfineco.2017.11.002; "
        "Ilmanen (2011), Expected Returns, ch.6 + ch.10"
    )
    verdict["hypothesis_slug"] = "ntsx-3leg-preserved-lev"
    verdict["pre_committed_cfg"] = data["configs"][0]
    verdict["gate_details"] = gate_details
    verdict["leg_correlations"] = data["leg_correlations"]
    verdict["benchmarks_used_custom"] = {
        ds: asdict(bm) for ds, bm in custom_benchmarks.items()
    }
    verdict["score_with_custom_benchmark"] = {
        "total_score": final_score,
        "winner_conditions_met": result.winner_conditions_met,
        "tier": tier_from_score(final_score, winner_conditions_met=result.winner_conditions_met).value,
        "criteria": result.criteria,
    }
    verdict["iter015_reference_metrics"] = iter015_ref
    verdict["iter035_reference_metrics"] = iter035_ref
    verdict["iter036_reference_metrics"] = iter036_ref
    for ref_name, ref in [
        ("iter015", iter015_ref),
        ("iter035", iter035_ref),
        ("iter036", iter036_ref),
    ]:
        verdict[f"delta_vs_{ref_name}"] = {
            ds: {
                "sharpe_delta": metrics_by_ds[ds].sharpe - ref[ds]["sharpe"],
                "cagr_delta":   metrics_by_ds[ds].cagr   - ref[ds]["cagr"],
                "mdd_delta":    metrics_by_ds[ds].mdd    - ref[ds]["mdd"],
            }
            for ds in ["educational", "spy_real", "ndx_real"]
        }
    verdict["funding_cost_sensitivity_note"] = (
        "Synthetic stack does NOT subtract futures-stacking funding cost on the "
        "50% additional notional (1.5× total). Real product would have ~50-80 bps "
        "annual drag depending on rate regime — same magnitude as iter 015/035 "
        "(funding scales with total leverage 1.5×, not leg count). Estimated Sharpe "
        "haircut: ~0.05-0.10 across 17y. GLD futures basis ≈ 0 (KMPV §3); IEF coupons "
        "partially offset; net drag identical to iter 015's 1.5× lev case."
    )
    deltas_iter015 = verdict["delta_vs_iter015"]
    sharpe_below_iter015_by_5 = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if deltas_iter015[ds]["sharpe_delta"] < -0.05
    )
    sharpe_edge_below_010 = sum(
        1 for ds in ["educational", "spy_real", "ndx_real"]
        if (metrics_by_ds[ds].sharpe - BENCHMARKS[ds].sharpe) < 0.10
    )
    verdict["pre_committed_kills"] = {
        "A_sharpe_edge_below_010_vs_frozen": {
            "fired": sharpe_edge_below_010 >= 2,
            "datasets_below_010": sharpe_edge_below_010,
            "threshold": "≥ 2 of 3 datasets with Sharpe edge < +0.10 vs frozen benchmark",
            "note": "If fired → equity-cut drag dominates 3-leg orthogonality benefit; closes static-stack ≤ 1.5×",
        },
        "B_sharpe_regress_vs_iter015_by_005": {
            "fired": sharpe_below_iter015_by_5 >= 2,
            "datasets_below_005": sharpe_below_iter015_by_5,
            "threshold": "≥ 2 of 3 datasets with Sharpe Δ vs iter 015 < −0.05",
            "note": "If fired → 3-leg at preserved lev destroys 2-leg edge",
        },
        "C_dsr_worst_p_above_0p20": {
            "fired": result_frozen.criteria["3_dsr"]["worst_p_value"] > 0.20,
            "worst_p": result_frozen.criteria["3_dsr"]["worst_p_value"],
            "threshold": "> 0.20",
        },
        "D_g7_crosslib_above_3pp": {
            "fired": any(
                gate_details[ds]["G7_xlib_diff_pp"] > 3.0
                for ds in ["educational", "spy_real", "ndx_real"]
            ),
            "max_diff_pp": max(
                gate_details[ds]["G7_xlib_diff_pp"]
                for ds in ["educational", "spy_real", "ndx_real"]
            ),
            "threshold": "> 3.0 pp",
        },
        "E_score_below_60": {
            "fired": canonical_score < 60,
            "score": canonical_score,
            "threshold": "< 60",
        },
        "F_robustness_below_7_of_9": {
            "fired": bonus_detail["positive_sub_windows"] < 7,
            "positive_windows": bonus_detail["positive_sub_windows"],
            "threshold": "< 7/9 sub-windows positive",
        },
        "G_ndx_mdd_above_40pct": {
            "fired": metrics_by_ds["ndx_real"].mdd > 0.40,
            "ndx_mdd": metrics_by_ds["ndx_real"].mdd,
            "threshold": "> 0.40",
        },
    }
    n_kills_fired = sum(
        1 for v in verdict["pre_committed_kills"].values() if v["fired"]
    )
    verdict["n_kills_fired"] = n_kills_fired
    verdict["status"] = (
        "winner" if canonical.winner_conditions_met and canonical_score >= 90
        else verdict["tier"].lower()
    )

    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"\n=== CANONICAL VERDICT (frozen benchmarks) ===")
    print(f"Tier: {verdict['tier']}")
    print(f"Total score (with bonus): {canonical_score}/100")
    print(f"Winner conditions met: {canonical.winner_conditions_met}")
    print(f"Status: {verdict['status']}")
    print(f"Kills fired: {n_kills_fired}/7")
    for k, v in verdict["criteria"].items():
        print(f"  {k}: {v['points']}/{v['max']}")
    print()
    print("Pre-committed kill criteria status:")
    for k, v in verdict["pre_committed_kills"].items():
        marker = "❌ FIRED" if v["fired"] else "✓ clean"
        print(f"  {k:42s} {marker}")


if __name__ == "__main__":
    main()
