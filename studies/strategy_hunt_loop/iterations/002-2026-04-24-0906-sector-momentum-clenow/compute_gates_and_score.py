"""Iteration 002 — compute 7-gate battery + score for each dataset.

Runs gates on the "top candidate" per dataset — defined as the config with
highest annualized Sharpe on that dataset. Writes `verdict.json` using
`studies/strategy_hunt_loop/scoring.py` with OVERRIDDEN benchmarks so the
educational slot reflects the measured SPY 2006-2026 reality (not the 40y
SPYSIM synth, which doesn't apply to a cross-sectional strategy).

Gates (per spec §0):
  G1 PBO < 0.5 on the 4-config grid
  G2 DSR p < 0.05 with cumulative n_trials (4020 from iter 001 + 4 from this
     iter = 4024)
  G3 Walk-forward 6/8 windows profitable + MDD < 25% per window
  G4 OOS 70/30 split: OOS Sharpe > 0
  G5 Forward stress post-2020 Sharpe > 0
  G6 Bootstrap 99.9% CI low > 0 (stationary bootstrap on trade returns)
  G7 Cross-lib ±3pp CAGR (numpy-pure adjusted_slope reference)
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "studies" / "strategy_hunt_loop"))

from scoring import (  # noqa: E402
    Benchmark,
    DatasetMetrics,
    Gates,
    score_strategy,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr,
    max_drawdown,
    returns_from_equity,
    sharpe,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_test  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as pbo_test  # noqa: E402

OUT_DIR = Path(__file__).parent
RESULTS_PATH = OUT_DIR / "results.json"

# Map our iteration's dataset names → the scoring.py canonical slot names.
DATASET_MAP = {
    "sectors_long": "educational",
    "sectors_spy":  "spy_real",
    "sectors_ndx":  "ndx_real",
}


def g1_pbo_grid(dataset_name: str, data: dict) -> tuple[bool, float]:
    """PBO on the 4 configs for this dataset `[advances_fin_ml, p.208-211]`.

    Build (T, N=4) returns matrix aligned on the common date index.
    """
    curves = data["equity_curves"][dataset_name]
    rets_frames = {}
    for cfg_id, payload in curves.items():
        idx = pd.to_datetime(payload["returns_full_index"])
        rets_frames[cfg_id] = pd.Series(payload["returns_full"], index=idx)
    df = pd.DataFrame(rets_frames).dropna(how="any")
    matrix = df.to_numpy()  # shape (T, 4)
    # CSCV needs even n_blocks; 10 is default.
    result = pbo_test(matrix, n_blocks=10)
    return (result.pbo < 0.5, result.pbo)


def g2_dsr(returns: np.ndarray, cumulative_n_trials: int) -> tuple[bool, float]:
    """DSR p-value with cumulative n_trials `[advances_fin_ml, p.222-223, 275]`."""
    r = dsr_test(returns, n_trials=cumulative_n_trials)
    return (r.p_value < 0.05, r.p_value)


def g3_walk_forward(returns: pd.Series) -> tuple[bool, dict]:
    """Walk-forward 6/8 windows, MDD < 25% per OOS window.

    Splits total returns into 8 equal contiguous blocks, OOS Sharpe > 0 and
    OOS MDD < 25% counted as "profitable". Simple implementation — the
    project's `walk_forward_splits` uses a rolling (IS, OOS) pair which is
    overkill here since we're not re-fitting, just checking consistency.
    """
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
        block_eq = (1 + block).cumprod()
        if len(block_eq) < 2:
            continue
        block_sharpe = sharpe(block)
        block_mdd = max_drawdown(block_eq)
        is_prof = block_sharpe > 0 and block_mdd < 0.25
        if is_prof:
            profitable += 1
        details.append({
            "window": i,
            "sharpe": block_sharpe,
            "mdd": block_mdd,
            "profitable": is_prof,
        })
    passed = profitable >= 6
    return passed, {"profitable_windows": profitable, "windows": details}


def g4_oos_split(returns: pd.Series) -> tuple[bool, float]:
    """70/30 IS/OOS split; OOS Sharpe > 0."""
    n = len(returns)
    split = int(n * 0.7)
    oos = returns.iloc[split:]
    sr = sharpe(oos)
    return sr > 0, sr


def g5_forward_post2020(returns: pd.Series) -> tuple[bool, float]:
    """Forward stress on post-2020 block; Sharpe > 0."""
    post = returns[returns.index >= pd.Timestamp("2020-01-01")]
    if len(post) < 20:
        return False, 0.0
    sr = sharpe(post)
    return sr > 0, sr


def g6_bootstrap_ci_low(returns: np.ndarray) -> tuple[bool, float]:
    """Stationary bootstrap 99.9% CI low on annualized Sharpe `[p.196-202]`.

    Lightweight implementation — block bootstrap 5000 resamples of the
    raw daily returns, compute Sharpe per resample, take 0.05% quantile.
    """
    returns = np.asarray(returns, dtype=float)
    if len(returns) < 30:
        return False, float("nan")
    rng = np.random.default_rng(42)
    n = len(returns)
    block_mean = 5
    p = 1.0 / block_mean
    n_resamples = 5000
    sharpes = np.empty(n_resamples)
    for k in range(n_resamples):
        # Politis-Romano stationary bootstrap
        idx = np.empty(n, dtype=np.int64)
        idx[0] = rng.integers(0, n)
        restarts = rng.random(n) < p
        for t in range(1, n):
            if restarts[t]:
                idx[t] = rng.integers(0, n)
            else:
                idx[t] = (idx[t - 1] + 1) % n
        r = returns[idx]
        sigma = r.std(ddof=0)
        if sigma <= 1e-12:
            sharpes[k] = 0.0
        else:
            sharpes[k] = r.mean() / sigma * np.sqrt(252)
    ci_low = float(np.quantile(sharpes, 0.0005))  # 99.9% CI → 0.05% tail
    return ci_low > 0, ci_low


def g7_cross_lib_cagr(returns: pd.Series, engine_cagr: float) -> tuple[bool, float]:
    """Cross-lib check: independent numpy CAGR vs engine CAGR, ±3pp.

    The engine's CAGR uses the equity curve; the numpy reference computes
    product of (1+r) then annualizes.
    """
    n = len(returns)
    if n < 2:
        return False, float("inf")
    growth = float(np.prod(1.0 + returns.to_numpy()))
    if growth <= 0:
        return False, float("inf")
    ref_cagr = growth ** (252.0 / n) - 1
    diff_pp = abs(ref_cagr - engine_cagr) * 100
    return diff_pp <= 3.0, diff_pp


def compute_gates_for_config(
    dataset_name: str, cfg_id: str, data: dict, cumulative_n_trials: int
) -> tuple[Gates, dict]:
    """Run all 7 gates on a single (dataset, config) pair; return Gates + details."""
    curves = data["equity_curves"][dataset_name][cfg_id]
    idx = pd.to_datetime(curves["returns_full_index"])
    rets = pd.Series(curves["returns_full"], index=idx)
    if len(rets) < 2:
        # Degenerate — all gates fail.
        return Gates(False, False, False, False, False, False, False), {}

    g1_pass, g1_val = g1_pbo_grid(dataset_name, data)
    g2_pass, g2_p   = g2_dsr(rets.to_numpy(), cumulative_n_trials=cumulative_n_trials)
    g3_pass, g3_det = g3_walk_forward(rets)
    g4_pass, g4_sr  = g4_oos_split(rets)
    g5_pass, g5_sr  = g5_forward_post2020(rets)
    g6_pass, g6_ci  = g6_bootstrap_ci_low(rets.to_numpy())
    engine_cagr     = data["runs"][dataset_name][cfg_id]["cagr"]
    g7_pass, g7_pp  = g7_cross_lib_cagr(rets, engine_cagr)

    gates = Gates(
        g1_pbo=g1_pass,
        g2_dsr=g2_pass,
        g3_wf=g3_pass,
        g4_oos=g4_pass,
        g5_fwd=g5_pass,
        g6_bootstrap=g6_pass,
        g7_crosslib=g7_pass,
    )
    detail = {
        "g1_pbo_value": g1_val,
        "g2_dsr_p":    g2_p,
        "g3_wf":       g3_det,
        "g4_oos_sharpe": g4_sr,
        "g5_fwd_sharpe": g5_sr,
        "g6_bootstrap_ci_low": g6_ci,
        "g7_cross_lib_diff_pp": g7_pp,
        "dsr_p_value": g2_p,
    }
    return gates, detail


def pick_top_candidate(data: dict) -> dict[str, str]:
    """Per dataset, pick the config with highest Sharpe."""
    top = {}
    for dataset in data["runs"]:
        by_sharpe = sorted(
            data["runs"][dataset].items(),
            key=lambda kv: kv[1]["sharpe"],
            reverse=True,
        )
        top[dataset] = by_sharpe[0][0]
    return top


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    cumulative = 4020 + len(data["configs"])  # 4024

    top_cfg = pick_top_candidate(data)
    print("Top config per dataset (by Sharpe):")
    for ds, c in top_cfg.items():
        print(f"  {ds}: {c}")

    gates_by_ds: dict[str, Gates] = {}
    metrics_by_ds: dict[str, DatasetMetrics] = {}
    benchmarks_by_ds: dict[str, Benchmark] = {}
    gate_details: dict[str, dict] = {}

    for ds, cfg_id in top_cfg.items():
        print(f"\n=== Gates: {ds} / {cfg_id} ===")
        gates, details = compute_gates_for_config(ds, cfg_id, data, cumulative)
        run = data["runs"][ds][cfg_id]
        bench = data["benchmarks"][ds]

        slot = DATASET_MAP[ds]
        metrics_by_ds[slot] = DatasetMetrics(
            sharpe=run["sharpe"],
            cagr=run["cagr"],
            mdd=run["mdd"],
            dsr_p_value=details.get("dsr_p_value"),
        )
        gates_by_ds[slot] = gates
        benchmarks_by_ds[slot] = Benchmark(
            sharpe=bench["sharpe"],
            cagr=bench["cagr"],
            mdd=bench["mdd"],
            label=f"{bench['symbol']} b&h (measured {ds})",
        )
        gate_details[ds] = {
            "cfg_id": cfg_id,
            "n_passed": gates.n_passed,
            "G1_pbo_pass":  gates.g1_pbo,    "G1_pbo_value":  details["g1_pbo_value"],
            "G2_dsr_pass":  gates.g2_dsr,    "G2_dsr_p":      details["g2_dsr_p"],
            "G3_wf_pass":   gates.g3_wf,     "G3_wf_profitable": details["g3_wf"].get("profitable_windows", 0),
            "G4_oos_pass":  gates.g4_oos,    "G4_oos_sharpe": details["g4_oos_sharpe"],
            "G5_fwd_pass":  gates.g5_fwd,    "G5_fwd_sharpe": details["g5_fwd_sharpe"],
            "G6_boot_pass": gates.g6_bootstrap, "G6_boot_ci_low": details["g6_bootstrap_ci_low"],
            "G7_xlib_pass": gates.g7_crosslib, "G7_xlib_diff_pp": details["g7_cross_lib_diff_pp"],
        }
        print(f"  gates passed: {gates.n_passed}/7")
        for k in ["G1", "G2", "G3", "G4", "G5", "G6", "G7"]:
            pass_key = f"{k}_pbo_pass" if k == "G1" else (
                f"{k}_dsr_pass" if k == "G2" else (
                f"{k}_wf_pass" if k == "G3" else (
                f"{k}_oos_pass" if k == "G4" else (
                f"{k}_fwd_pass" if k == "G5" else (
                f"{k}_boot_pass" if k == "G6" else f"{k}_xlib_pass")))))
            print(f"    {k}: {'PASS' if gate_details[ds][pass_key] else 'FAIL'}")

    print("\n=== Score ===")
    result = score_strategy(
        metrics=metrics_by_ds,
        gates=gates_by_ds,
        cumulative_n_trials=cumulative,
        benchmarks=benchmarks_by_ds,
    )
    verdict = result.to_dict()
    verdict["configs_tested"]     = len(data["configs"])
    verdict["primary_citation"]   = "[stocks_on_the_move, p.76-77, p.82, p.88-89, p.98-99]"
    verdict["hypothesis_slug"]    = "sector-momentum-clenow"
    verdict["top_candidate"]      = top_cfg
    verdict["gate_details"]       = gate_details
    verdict["status"] = (
        "winner" if result.winner_conditions_met and result.total_score >= 90
        else result.tier.value.lower()
    )

    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"Tier: {result.tier.value}")
    print(f"Total score: {result.total_score}/100")
    print(f"Winner conditions met: {result.winner_conditions_met}")
    for k, v in result.criteria.items():
        print(f"  {k}: {v['points']}/{v['max']}")


if __name__ == "__main__":
    main()
