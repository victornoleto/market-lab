"""Iter 006 — 7-gate battery + scoring for vol-managed SPY+TLT blend.

Mirrors iter 005 harness (same G1-G7 definitions and CSCV / DSR wiring)
but with the blend-specific G7 numpy reference.

Cumulative ``n_trials`` after iter 006:
  * Before iter 006: 4192 (per BASE_MEMORY.md frontmatter)
  * This iter: 12 configs × 3 datasets = 36 new trials
  * Post iter 006: **4228**

Benchmark note
--------------
``educational`` slot for iter 006 uses SPY+TLT 2002-2026 (TLT cache
only starts 2002-07-26, so the SPYSIM 40y synth is not available with
a paired TLT stream). The custom benchmark for this slot is SPY b&h
over the same window, computed at run time and injected into
``score_strategy(benchmarks=...)``. ``spy_real`` and ``ndx_real`` keep
the frozen scoring.BENCHMARKS (SPY 0.90 / QQQ 0.955) — comparability
across iterations on those slots is preserved.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "studies" / "strategy_hunt_loop"))
sys.path.insert(0, str(Path(__file__).parent))

from scoring import (  # noqa: E402
    BENCHMARKS,
    Benchmark,
    DatasetMetrics,
    Gates,
    score_strategy,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    max_drawdown,
    sharpe,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_test  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as pbo_test  # noqa: E402

from numpy_reference import (  # noqa: E402
    apply_blend_variance_target_np,
    cagr_np,
)

OUT_DIR = Path(__file__).parent
RESULTS_PATH = OUT_DIR / "results.json"

# iter 005 cumulative = 4192. This iter adds 12 × 3 = 36 trials.
CUMULATIVE_N_TRIALS = 4192 + 12 * 3  # = 4228


def load_raw_pair(dataset_name: str):
    from run_backtests import load_paired_returns, DATASETS
    ds = DATASETS[dataset_name]
    return load_paired_returns(
        ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"]
    )


def g1_pbo_grid(dataset_name: str, data: dict) -> tuple[bool, float]:
    series_map = data["returns_series"][dataset_name]
    frames = {}
    for cfg_id, payload in series_map.items():
        idx = pd.to_datetime(payload["index"])
        frames[cfg_id] = pd.Series(payload["net_returns"], index=idx)
    df = pd.DataFrame(frames).dropna(how="any")
    matrix = df.to_numpy()
    result = pbo_test(matrix, n_blocks=10)
    return (result.pbo < 0.5, result.pbo)


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
    raw = load_raw_pair(dataset_name)
    eq_col, bd_col = raw.columns
    net_np, _, _, _ = apply_blend_variance_target_np(
        raw[eq_col].to_numpy(),
        raw[bd_col].to_numpy(),
        target_vol=cfg["target_vol"],
        lookback=cfg["lookback"],
        max_leverage=cfg["max_leverage"],
    )
    ref_cagr = cagr_np(net_np)
    diff_pp = abs(ref_cagr - engine_cagr) * 100
    return diff_pp <= 3.0, float(diff_pp)


def compute_gates_for_config(
    dataset_name: str, cfg_id: str, data: dict
) -> tuple[Gates, dict]:
    series = data["returns_series"][dataset_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    rets = pd.Series(series["net_returns"], index=idx)
    if len(rets) < 2:
        return Gates(False, False, False, False, False, False, False), {}

    cfg = data["runs"][dataset_name][cfg_id]
    engine_cagr = cfg["cagr"]

    g1_pass, g1_val = g1_pbo_grid(dataset_name, data)
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
        "g2_dsr_p": g2_p,
        "g3_wf": g3_det,
        "g4_oos_sharpe": g4_sr,
        "g5_fwd_sharpe": g5_sr,
        "g6_bootstrap_ci_low": g6_ci,
        "g7_cross_lib_diff_pp": g7_pp,
        "dsr_p_value": g2_p,
    }
    return gates, detail


def pick_top_candidate(data: dict) -> dict[str, str]:
    return {
        ds: max(data["runs"][ds].items(), key=lambda kv: kv[1]["sharpe"])[0]
        for ds in data["runs"]
    }


def build_custom_benchmarks(data: dict) -> dict[str, Benchmark]:
    """Custom benchmarks — educational uses measured SPY 2002-2026 b&h;
    spy_real and ndx_real keep the FROZEN scoring.BENCHMARKS (SPY 0.90
    and QQQ 0.955) so the +0.10 Sharpe gate is compared against the same
    numbers iter 004/005 used."""
    edu_bench = data["benchmarks"]["educational"]
    return {
        "educational": Benchmark(
            sharpe=edu_bench["sharpe"],
            cagr=edu_bench["cagr"],
            mdd=edu_bench["mdd"],
            label=f"SPY b&h {edu_bench['first']}→{edu_bench['last']} (iter 006 TLT-aligned window)",
        ),
        "spy_real": BENCHMARKS["spy_real"],
        "ndx_real": BENCHMARKS["ndx_real"],
    }


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    top_cfg = pick_top_candidate(data)
    custom_benchmarks = build_custom_benchmarks(data)

    print("Top config per dataset (by Sharpe):")
    for ds, c in top_cfg.items():
        run = data["runs"][ds][c]
        bench = custom_benchmarks[ds]
        edge = run["sharpe"] - bench.sharpe
        print(
            f"  {ds:12s} {c} Sharpe={run['sharpe']:.3f} "
            f"(Δ={edge:+.3f} vs bench {bench.sharpe:.3f})"
        )

    gates_by_ds: dict[str, Gates] = {}
    metrics_by_ds: dict[str, DatasetMetrics] = {}
    gate_details: dict[str, dict] = {}

    for ds, cfg_id in top_cfg.items():
        print(f"\n=== Gates: {ds} / {cfg_id} ===")
        gates, details = compute_gates_for_config(ds, cfg_id, data)
        run = data["runs"][ds][cfg_id]

        metrics_by_ds[ds] = DatasetMetrics(
            sharpe=run["sharpe"], cagr=run["cagr"], mdd=run["mdd"],
            dsr_p_value=details["dsr_p_value"],
        )
        gates_by_ds[ds] = gates
        gate_details[ds] = {
            "cfg_id": cfg_id,
            "n_passed": gates.n_passed,
            "G1_pbo_pass": gates.g1_pbo, "G1_pbo_value": details["g1_pbo_value"],
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
            ("G1 PBO", gates.g1_pbo, f"{details['g1_pbo_value']:.3f}"),
            ("G2 DSR p", gates.g2_dsr, f"{details['g2_dsr_p']:.4f}"),
            ("G3 WF", gates.g3_wf, f"{details['g3_wf'].get('profitable_windows', 0)}/8"),
            ("G4 OOS Sh", gates.g4_oos, f"{details['g4_oos_sharpe']:+.3f}"),
            ("G5 FWD Sh", gates.g5_fwd, f"{details['g5_fwd_sharpe']:+.3f}"),
            ("G6 boot CI", gates.g6_bootstrap, f"{details['g6_bootstrap_ci_low']:+.3f}"),
            ("G7 xlib pp", gates.g7_crosslib, f"{details['g7_cross_lib_diff_pp']:.4f}"),
        ]
        for name, passed, val in flags:
            print(f"    {name:12s} {'PASS' if passed else 'FAIL'} ({val})")

    print("\n=== Score ===")
    print(f"cumulative_n_trials = {CUMULATIVE_N_TRIALS}")
    result = score_strategy(
        metrics=metrics_by_ds,
        gates=gates_by_ds,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        benchmarks=custom_benchmarks,
    )
    verdict = result.to_dict()
    verdict["configs_tested"] = len(data["configs"])
    verdict["primary_citation"] = (
        "[risk_parity, p.10-11, ch.1]; [systematic_trading, p.170-171, ch.11]; "
        "Moreira & Muir (2017), JoF 72(4) DOI 10.1111/jofi.12513"
    )
    verdict["hypothesis_slug"] = "vol-managed-60-40"
    verdict["top_candidate"] = top_cfg
    verdict["gate_details"] = gate_details
    verdict["leg_correlations"] = data["leg_correlations"]
    verdict["benchmarks_used_custom"] = {
        ds: asdict(bm) for ds, bm in custom_benchmarks.items()
    }
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
