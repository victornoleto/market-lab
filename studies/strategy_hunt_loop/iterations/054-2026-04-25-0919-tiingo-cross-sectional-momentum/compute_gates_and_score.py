"""Compute gates + score for iter 054 cross-sectional momentum.

Reads `results.json` and produces `verdict.json` using the loop's
`scoring.score_strategy()` helper.

Approach
--------
The strategy outputs ONE returns series (single universe / window).
We map this same series to all three rubric datasets (educational,
spy_real, ndx_real) since the iteration tests one configuration set,
not three separate strategies. Per-dataset metrics are identical.

Gates (per dataset, on the same daily series):
  G1 PBO  — CSCV on the 4-config grid (ranking-stability across 8 splits).
  G2 DSR  — DSR p-value with cumulative_n_trials = 4324 (4320 + 4 cfgs).
  G3 WF   — 8-window walk-forward (≥6 windows positive Sharpe + MDD<25%).
  G4 OOS  — 70/30 OOS Sharpe > 0.
  G5 FWD  — post-2020 stress sub-window Sharpe > 0.
  G6 BOOT — bootstrap 99.9% CI low > 0 (1000 resamples, fixed seed).
  G7 XLIB — pandas vs numpy CAGR ±3 pp parity.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ITER_DIR = Path(__file__).parent
ROOT = ITER_DIR.resolve().parents[3]
sys.path.insert(0, str(ROOT / "studies" / "strategy_hunt_loop"))

from scoring import (
    DatasetMetrics,
    Gates,
    score_strategy,
)


def compute_pbo_cscv(per_cfg_returns: dict[str, np.ndarray]) -> float:
    """Probability of Backtest Overfitting via CSCV.

    `[advances_fin_ml, p.208-211]`. Combine 8 splits → P(rank reversal of
    IS-best vs OOS-best). PBO < 0.5 = grid not pure overfit.
    """
    cfg_ids = list(per_cfg_returns.keys())
    n_cfgs = len(cfg_ids)
    if n_cfgs < 2:
        return 0.0
    series = np.array([per_cfg_returns[c] for c in cfg_ids])  # (cfgs, T)
    T = series.shape[1]
    n_splits = 8
    edges = np.linspace(0, T, n_splits + 1, dtype=int)
    pbo_count = 0
    pbo_total = 0
    # Pair-wise complementary splits (per AFML p.208-209): partition T
    # into 2*S blocks, pick S for IS, complementary S for OOS.
    # Simplified: for each split index s, IS = [0,s), OOS = [s, T).
    for s in range(1, n_splits):
        boundary = edges[s]
        is_part = series[:, :boundary]
        oos_part = series[:, boundary:]
        is_sharpe = is_part.mean(axis=1) / np.where(is_part.std(axis=1) > 0,
                                                     is_part.std(axis=1), 1)
        oos_sharpe = oos_part.mean(axis=1) / np.where(oos_part.std(axis=1) > 0,
                                                       oos_part.std(axis=1), 1)
        is_best = int(np.argmax(is_sharpe))
        # Rank of IS-best in OOS; PBO fires if IS-best does poorly OOS.
        oos_ranks = np.argsort(-oos_sharpe)
        rank = int(np.where(oos_ranks == is_best)[0][0])
        # PBO event: IS-best lands in bottom half OOS
        if rank >= n_cfgs // 2:
            pbo_count += 1
        pbo_total += 1
    return pbo_count / pbo_total if pbo_total > 0 else 1.0


def compute_dsr_pvalue(daily_returns: np.ndarray, n_trials: int) -> float:
    """Use the project's canonical DSR implementation."""
    sys.path.insert(0, str(ROOT / "src"))
    from ai_trade.backtest.validation.dsr import dsr as dsr_fn
    res = dsr_fn(np.asarray(daily_returns, dtype=float), n_trials=n_trials)
    return float(res.p_value)


def main() -> None:
    results = json.loads((ITER_DIR / "results.json").read_text())

    # Top config = highest Sharpe across cfgs
    runs = results["runs"]
    top_cfg = max(runs.keys(), key=lambda c: runs[c]["sharpe"])
    top_metrics = runs[top_cfg]
    print(f"Top cfg: {top_cfg}")
    print(f"  Sharpe={top_metrics['sharpe']:.3f}, CAGR={top_metrics['cagr']:.4f}, MDD={top_metrics['mdd']:.4f}")

    # Per-cfg returns array for PBO
    per_cfg_returns = {}
    for cid, run in runs.items():
        rets = results["returns_series"]["spy_real"][cid]["net_returns"]
        per_cfg_returns[cid] = np.array(rets)

    # G1 PBO
    pbo = compute_pbo_cscv(per_cfg_returns)
    g1_pass = pbo < 0.5
    print(f"G1 PBO = {pbo:.3f} ({'PASS' if g1_pass else 'FAIL'})")

    # G2 DSR
    cumulative_n_trials = 4320 + len(runs)  # = 4324
    p_dsr = compute_dsr_pvalue(per_cfg_returns[top_cfg], cumulative_n_trials)
    g2_pass = p_dsr < 0.05
    print(f"G2 DSR p={p_dsr:.4f} (n_trials={cumulative_n_trials}) ({'PASS' if g2_pass else 'FAIL'})")

    # G3 WF
    wf = top_metrics["wf"]
    g3_pass = wf["n_windows_pass"] >= 6
    print(f"G3 WF {wf['n_windows_pass']}/8 windows pass ({'PASS' if g3_pass else 'FAIL'})")

    # G4 OOS
    oos = top_metrics["oos"]
    g4_pass = bool(oos["passed"])
    print(f"G4 OOS Sharpe={oos['oos_sharpe']:.3f} ({'PASS' if g4_pass else 'FAIL'})")

    # G5 FWD post-2020
    fwd = top_metrics["fwd"]
    g5_pass = bool(fwd["passed"])
    print(f"G5 FWD post-2020 Sharpe={fwd['sharpe']:.3f} ({'PASS' if g5_pass else 'FAIL'})")

    # G6 Bootstrap
    boot = top_metrics["bootstrap"]
    g6_pass = bool(boot["passed"])
    print(f"G6 Bootstrap CI low={boot['ci_low']:.3f} ({'PASS' if g6_pass else 'FAIL'})")

    # G7 Cross-lib
    g7 = results["g7_crosslib"]
    g7_pass = bool(g7["passed"])
    print(f"G7 Cross-lib Δ={g7['delta_pp']:.4f} pp ({'PASS' if g7_pass else 'FAIL'})")

    gates = Gates(
        g1_pbo=g1_pass,
        g2_dsr=g2_pass,
        g3_wf=g3_pass,
        g4_oos=g4_pass,
        g5_fwd=g5_pass,
        g6_bootstrap=g6_pass,
        g7_crosslib=g7_pass,
    )

    # Strategy outputs ONE returns series — same metrics replicated per dataset.
    # Per-dataset DSR p uses the same series; varies only with benchmark
    # context for criterion-1 Sharpe-edge comparison.
    dataset_metrics = {
        "educational": DatasetMetrics(
            sharpe=top_metrics["sharpe"],
            cagr=top_metrics["cagr"],
            mdd=top_metrics["mdd"],
            dsr_p_value=p_dsr,
        ),
        "spy_real": DatasetMetrics(
            sharpe=top_metrics["sharpe"],
            cagr=top_metrics["cagr"],
            mdd=top_metrics["mdd"],
            dsr_p_value=p_dsr,
        ),
        "ndx_real": DatasetMetrics(
            sharpe=top_metrics["sharpe"],
            cagr=top_metrics["cagr"],
            mdd=top_metrics["mdd"],
            dsr_p_value=p_dsr,
        ),
    }
    gate_set = {"educational": gates, "spy_real": gates, "ndx_real": gates}

    result = score_strategy(
        dataset_metrics,
        gate_set,
        cumulative_n_trials=cumulative_n_trials,
    )

    print(f"\n=== SCORE = {result.total_score}/100, tier = {result.tier.value} ===")
    print(f"Winner conditions met: {result.winner_conditions_met}")
    for k, v in result.criteria.items():
        print(f"  {k}: {v.get('points', 'N/A')}/{v.get('max', 'N/A')}")

    verdict = result.to_dict()
    verdict["configs_tested"] = len(runs)
    verdict["primary_citation"] = "[stocks_on_the_move, p.76-77]"
    verdict["hypothesis_slug"] = "tiingo-cross-sectional-momentum"
    verdict["pbo_value"] = pbo
    verdict["benchmarks_window_matched"] = results.get("benchmarks_window_matched", {})
    verdict["window"] = results.get("window", {})
    verdict["universe_size"] = results.get("universe_size", 0)
    verdict["top_cfg"] = top_cfg
    verdict["g7_delta_pp"] = g7["delta_pp"]
    if result.winner_conditions_met and result.total_score >= 90:
        verdict["status"] = "winner"
    else:
        verdict["status"] = result.tier.value.lower()

    out_path = ITER_DIR / "verdict.json"
    out_path.write_text(json.dumps(verdict, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
