"""Iter 031 — 7-gate battery + scoring for VIX AND-composite VRP-primary.

Pattern mirrors iter 026/028/029/030: G1 N=1 vacuous PASS; G2-G6
standard definitions; G7 via the numpy reference computed in
run_backtests.py.

Cumulative n_trials:
  * Before iter 031: 4283 (BASE_MEMORY frontmatter post-iter-030)
  * This iter adds:  1 cfg
  * Post iter 031:   **4284**

Pre-committed kill criteria (from hypothesis.md):
  * Kill A: AND-composite fires 0 rolls across educational
  * Kill B: educational Sharpe < 1.03 (iter 026's 1.1334 - 0.10)
  * Kill C: spy_real Sharpe < 1.23 OR ndx_real Sharpe < 1.32
  * Kill D: 21d worst loss > 30 % on any dataset
  * Kill E: G7 cross-lib > 3 pp on any dataset
  * Kill F: total canonical score < 76 (iter 026 reference)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]

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

CUMULATIVE_N_TRIALS = 4283 + 1   # = 4284

ITER_026_REF: dict[str, dict] = {
    "educational": {"sharpe": 1.1334, "cagr": 0.0485, "mdd": 0.1682, "dsr_p": 0.0828},
    "spy_real":    {"sharpe": 1.2819, "cagr": 0.0497, "mdd": 0.0635, "dsr_p": 0.0698},
    "ndx_real":    {"sharpe": 1.3673, "cagr": 0.0631, "mdd": 0.0818, "dsr_p": 0.0376},
}

ITER_028_REF: dict[str, dict] = {
    "educational": {"sharpe": 1.2596, "cagr": 0.0504, "mdd": 0.0663, "dsr_p": 0.0287},
    "spy_real":    {"sharpe": 1.1811, "cagr": 0.0446, "mdd": 0.0635, "dsr_p": 0.1364},
    "ndx_real":    {"sharpe": 1.3005, "cagr": 0.0590, "mdd": 0.0818, "dsr_p": 0.0640},
}

ITER_029_REF: dict[str, dict] = {
    "educational": {"sharpe": 1.2735, "cagr": 0.0511, "mdd": 0.0663, "dsr_p": 0.0251},
    "spy_real":    {"sharpe": 1.2295, "cagr": 0.0471, "mdd": 0.0635, "dsr_p": 0.1002},
    "ndx_real":    {"sharpe": 1.3005, "cagr": 0.0590, "mdd": 0.0818, "dsr_p": 0.0640},
}

ITER_030_REF: dict[str, dict] = {
    "educational": {"sharpe": 1.1390, "cagr": 0.0450, "mdd": 0.1447, "dsr_p": 0.0820},
    "spy_real":    {"sharpe": 1.3620, "cagr": 0.0478, "mdd": 0.0712, "dsr_p": 0.0345},
    "ndx_real":    {"sharpe": 1.2368, "cagr": 0.0549, "mdd": 0.0818, "dsr_p": 0.1010},
}


def g1_pbo_single_cfg() -> tuple[bool, None]:
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


def g7_cross_lib(crosslib_payload: dict) -> tuple[bool, float]:
    diff_pp = crosslib_payload["abs_diff_pp"]
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


def compute_gates_for_dataset(
    dataset_name: str, data: dict
) -> tuple[Gates, dict, pd.Series]:
    cfg_id = next(iter(data["runs"][dataset_name].keys()))
    series = data["returns_series"][dataset_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    rets = pd.Series(series["net_returns"], index=idx)
    crosslib = data["crosslib"][dataset_name]

    g1_pass, g1_val = g1_pbo_single_cfg()
    g2_pass, g2_p = g2_dsr(rets.to_numpy(), CUMULATIVE_N_TRIALS)
    g3_pass, g3_det = g3_walk_forward(rets)
    g4_pass, g4_sr = g4_oos_split(rets)
    g5_pass, g5_sr = g5_forward_post2020(rets)
    g6_pass, g6_ci = g6_bootstrap_ci_low(rets.to_numpy())
    g7_pass, g7_pp = g7_cross_lib(crosslib)

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


def evaluate_kill_criteria(
    metrics_by_ds: dict[str, DatasetMetrics],
    runs_by_ds: dict[str, dict],
    crosslib_by_ds: dict[str, dict],
    canonical_score: int,
) -> dict:
    """Pre-committed kill criteria check (from iter 031 hypothesis.md)."""
    kills: dict = {}

    edu_skipped = (
        runs_by_ds["educational"]["filter_diagnostic"]["rolls_skipped_composite_AND"]
    )
    kills["A_composite_vacuous"] = {
        "edu_rolls_skipped_composite": edu_skipped,
        "triggered": edu_skipped == 0,
        "threshold": 0,
        "note": (
            "AND-composite must fire at least once on educational over "
            "20y; zero fires means the intersection is structurally empty"
        ),
    }

    edu_sharpe = metrics_by_ds["educational"].sharpe
    edu_floor = ITER_026_REF["educational"]["sharpe"] - 0.10
    edu_delta_vs_026 = edu_sharpe - ITER_026_REF["educational"]["sharpe"]
    kills["B_educational_collapse"] = {
        "edu_sharpe": edu_sharpe,
        "iter026_edu_sharpe": ITER_026_REF["educational"]["sharpe"],
        "delta_vs_iter026": edu_delta_vs_026,
        "floor": edu_floor,
        "triggered": edu_sharpe < edu_floor,
        "threshold_delta": -0.10,
    }

    spy_sharpe = metrics_by_ds["spy_real"].sharpe
    spy_floor = ITER_026_REF["spy_real"]["sharpe"] - 0.05
    spy_delta_vs_026 = spy_sharpe - ITER_026_REF["spy_real"]["sharpe"]

    ndx_sharpe = metrics_by_ds["ndx_real"].sharpe
    ndx_floor = ITER_026_REF["ndx_real"]["sharpe"] - 0.05
    ndx_delta_vs_026 = ndx_sharpe - ITER_026_REF["ndx_real"]["sharpe"]

    kills["C_postgfc_regress"] = {
        "spy_sharpe": spy_sharpe,
        "spy_floor_iter026_minus_005": spy_floor,
        "spy_delta_vs_iter026": spy_delta_vs_026,
        "spy_regress": spy_sharpe < spy_floor,
        "ndx_sharpe": ndx_sharpe,
        "ndx_floor_iter026_minus_005": ndx_floor,
        "ndx_delta_vs_iter026": ndx_delta_vs_026,
        "ndx_regress": ndx_sharpe < ndx_floor,
        "triggered": (spy_sharpe < spy_floor) or (ndx_sharpe < ndx_floor),
        "threshold_delta": -0.05,
    }

    worst_21d = {ds: runs_by_ds[ds]["rolling21_worst"] for ds in runs_by_ds}
    kills["D_21d_loss"] = {
        "worst_21d": worst_21d,
        "exceeders": {ds: v for ds, v in worst_21d.items() if v < -0.30},
        "triggered": any(v < -0.30 for v in worst_21d.values()),
        "threshold": -0.30,
    }

    diffs = {ds: crosslib_by_ds[ds]["abs_diff_pp"] for ds in crosslib_by_ds}
    kills["E_engine_dirty"] = {
        "diffs_pp": diffs,
        "exceeders": {ds: v for ds, v in diffs.items() if v > 3.0},
        "triggered": any(v > 3.0 for v in diffs.values()),
        "threshold_pp": 3.0,
    }

    kills["F_no_score_improvement"] = {
        "canonical_score": canonical_score,
        "iter026_reference_score": 76,
        "triggered": canonical_score < 76,
        "threshold_score": 76,
        "note": "AND-composite axis must produce score >= 76 to add value",
    }

    kills["any_triggered"] = any(
        k.get("triggered", False)
        for k in (
            kills["A_composite_vacuous"],
            kills["B_educational_collapse"],
            kills["C_postgfc_regress"],
            kills["D_21d_loss"],
            kills["E_engine_dirty"],
            kills["F_no_score_improvement"],
        )
    )
    return kills


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

    cfg_id = data["configs"][0]["cfg_id"]
    print(f"Single pre-committed cfg: {cfg_id}")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS} (4283 + 1)")
    for ds in ["educational", "spy_real", "ndx_real"]:
        run = data["runs"][ds][cfg_id]
        bench_frozen = BENCHMARKS[ds].sharpe
        ref026 = ITER_026_REF[ds]["sharpe"]
        ref028 = ITER_028_REF[ds]["sharpe"]
        ref029 = ITER_029_REF[ds]["sharpe"]
        ref030 = ITER_030_REF[ds]["sharpe"]
        print(
            f"  {ds:12s} Sharpe={run['sharpe']:.4f} "
            f"(Δ frozen {run['sharpe'] - bench_frozen:+.4f}, "
            f"Δ iter026 {run['sharpe'] - ref026:+.4f}, "
            f"Δ iter028 {run['sharpe'] - ref028:+.4f}, "
            f"Δ iter029 {run['sharpe'] - ref029:+.4f}, "
            f"Δ iter030 {run['sharpe'] - ref030:+.4f})"
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
            "G3_wf_windows": details["g3_wf"].get("windows", []),
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

    print("\n=== Score against FROZEN benchmarks (canonical) ===")
    result_frozen = score_strategy(
        metrics=metrics_by_ds,
        gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        benchmarks=BENCHMARKS,
    )
    final_score_frozen = min(100, result_frozen.total_score + bonus_pts)

    canonical = result_frozen
    canonical_score = final_score_frozen
    print(f"  frozen-bench score: {final_score_frozen}/100 "
          f"(winner_conds={result_frozen.winner_conditions_met})")

    print("\n=== Kill criteria (pre-committed) ===")
    runs_by_ds = {ds: data["runs"][ds][cfg_id]
                  for ds in ["educational", "spy_real", "ndx_real"]}
    kills = evaluate_kill_criteria(
        metrics_by_ds, runs_by_ds, data["crosslib"], canonical_score,
    )
    for kn, kv in kills.items():
        if kn == "any_triggered":
            print(f"  ANY KILL TRIGGERED: {kv}")
            continue
        trig = kv.get("triggered", False)
        print(f"  {kn}: {'TRIGGERED' if trig else 'clean'}")
        for k, v in kv.items():
            if k not in ("triggered", "note"):
                print(f"      {k}: {v}")

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
        "[volatility_trading, p.217-218] Sinclair level + sustained → "
        "AND-composite intersection of both axes; "
        "[volatility_trading, p.39, p.58-59] vol-of-vol + cone middle horizon; "
        "[volatility_trading, ch.3] VRP mechanics; "
        "Bondarenko (2014) QJF 4(3) §3 level AND persistence both matter; "
        "Whaley (2009) JPM 35(3) VIX innovation analysis (z-score); "
        "Carr-Wu (2009) RFS 22(3) VRP decomposition"
    )
    verdict["hypothesis_slug"] = "vix-and-composite-vrp-primary"
    verdict["pre_committed_cfg"] = data["configs"][0]
    verdict["gate_details"] = gate_details
    verdict["crosslib"] = data["crosslib"]
    verdict["benchmarks_used_custom"] = {
        ds: data["benchmarks"][ds] for ds in ["educational", "spy_real", "ndx_real"]
    }
    verdict["kill_criteria"] = kills
    verdict["iter026_reference_metrics"] = ITER_026_REF
    verdict["iter028_reference_metrics"] = ITER_028_REF
    verdict["iter029_reference_metrics"] = ITER_029_REF
    verdict["iter030_reference_metrics"] = ITER_030_REF
    for ref_name, ref in [
        ("delta_vs_iter026", ITER_026_REF),
        ("delta_vs_iter028", ITER_028_REF),
        ("delta_vs_iter029", ITER_029_REF),
        ("delta_vs_iter030", ITER_030_REF),
    ]:
        verdict[ref_name] = {
            ds: {
                "sharpe": metrics_by_ds[ds].sharpe - ref[ds]["sharpe"],
                "cagr": metrics_by_ds[ds].cagr - ref[ds]["cagr"],
                "mdd": metrics_by_ds[ds].mdd - ref[ds]["mdd"],
                "dsr_p": metrics_by_ds[ds].dsr_p_value - ref[ds]["dsr_p"],
            }
            for ds in ["educational", "spy_real", "ndx_real"]
        }

    out = OUT_DIR / "verdict.json"
    out.write_text(
        json.dumps(verdict, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"\nWrote {out}")
    print(f"Final tier: {verdict['tier']} (score {verdict['total_score']}/100)")
    print(f"Winner conditions met: {verdict['winner_conditions_met']}")


if __name__ == "__main__":
    main()
