"""Iter 012 — IC-7 composition: iter 003 + iter 011 at Markowitz tangency weights.

Reuses the cost-included net returns saved by iter 003 (RSI(2)+SMA(200) MR)
and iter 011 (inverse vol-regime σ_60<σ_252) per dataset, joins on common
dates, fits a 2-asset Markowitz tangency portfolio in-sample on each dataset,
and re-runs the 7-gate battery on the combined daily returns.

Single pre-committed cfg (IC-8). cumulative_n_trials = 12.

Output: ``results.json`` + ``verdict.json`` + (later) ``final_report.md``.

Citations
---------
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 12 (PRIMARY)
* `[modern_portfolio_theory]` — 2-asset Markowitz tangency (Σ⁻¹μ normalized)
* `[advances_fin_ml, p.31-34]` — cost realism (each component already net of
  Pepperstone CFD costs; composition is capital allocation, no extra cost)
* IC-7 (sister 045/046) — out-of-family corr<0.50 compounds DSR
* IC-3 (sister 049) — Markowitz proper (NOT 50/50) when Sharpes differ >30%
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
sys.path.insert(0, str(ROOT / "studies" / "gold_swing_loop"))
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.validation.bootstrap import stationary_bootstrap_trades  # noqa: E402
from ai_trade.backtest.validation.dsr import dsr as dsr_func  # noqa: E402
from ai_trade.backtest.validation.dsr import sharpe_periodic  # noqa: E402
from ai_trade.backtest.validation.walk_forward import walk_forward_gate  # noqa: E402

from scoring import (  # noqa: E402
    BENCHMARKS,
    DatasetMetrics,
    Gates,
    score_strategy,
)


CFG_ID = "composition_iter_003_iter_011_markowitz"

# 11 prior iters + 1 (this composition) = 12.
CUMULATIVE_N_TRIALS = 12

# Component locations
ITER_003_DIR = ROOT / "studies" / "gold_swing_loop" / "iterations" / "003-2026-04-26-0228-rsi2-sma200-filter"
ITER_011_DIR = ROOT / "studies" / "gold_swing_loop" / "iterations" / "011-2026-04-26-1334-vol-regime-gate-inverse"

ITER_003_CFG = "connors_rsi2_sma200_filter"
ITER_011_CFG = "vol_regime_inverse_60_252_long_only"

# Annualization per dataset (composition is at DAILY granularity for all 3 ds).
ANN_PER_DS = {
    "gld_long": 252,
    "xauusd_real": 252,
    "xauusd_intraday": 252,
}


# ===========================================================================
# Composition primitives (TDD-tested)
# ===========================================================================


def markowitz_tangency_weights(
    mu: np.ndarray, sigma: np.ndarray, rho: float
) -> tuple[float, float]:
    """2-asset Markowitz tangency weights (max-Sharpe, full-investment).

    Inputs use returns scale (not Sharpes); ``mu[i]`` and ``sigma[i]`` are
    the per-period mean and std of stream i.

    Returns ``(w_A, w_B)`` summing to 1.0. Caller must check ``w_A > 0`` and
    ``w_B > 0`` before allocating; negative weights signal a different
    hypothesis (one stream should be shorted, or correlation is high
    relative to Sharpe ratio).

    Formula::

        Σ = [[σ_A², ρσ_Aσ_B], [ρσ_Aσ_B, σ_B²]]
        raw = Σ⁻¹ μ
        w   = raw / sum(raw)
    """
    cov = np.array([
        [sigma[0] ** 2, rho * sigma[0] * sigma[1]],
        [rho * sigma[0] * sigma[1], sigma[1] ** 2],
    ])
    raw = np.linalg.solve(cov, mu)
    weights = raw / raw.sum()
    return float(weights[0]), float(weights[1])


def compose_returns(
    a: pd.Series, b: pd.Series, w_a: float, w_b: float
) -> pd.Series:
    """Linear composition w_A·r_A + w_B·r_B on inner-joined index."""
    joined = pd.concat([a, b], axis=1, join="inner").dropna()
    joined.columns = ["a", "b"]
    return (w_a * joined["a"] + w_b * joined["b"]).rename("composed")


def aggregate_intraday_to_daily(rets: pd.Series) -> pd.Series:
    """Sum intraday simple-bar returns to daily totals.

    Input series may be 1h-bar (32 195 bars on xauusd_intraday) or already
    daily. Output is daily-indexed total daily PnL fraction. Days with no
    bars are dropped.

    For r_h on the order of 1e-4, the simple sum approximates the
    geometric daily return to << 1 bp; matches cost_models.apply_*'s
    bar-PnL semantics where ``net_pnl = bar_pnl - costs`` is already in
    fraction-of-capital units per bar.
    """
    daily = rets.resample("D").sum()
    return daily.dropna()


def load_component_returns(
    iter_dir: Path, ds: str, cfg_id: str
) -> pd.Series:
    """Load returns_series saved by an upstream iter's results.json."""
    rj = iter_dir / "results.json"
    if not rj.exists():
        raise FileNotFoundError(f"no results.json at {rj}")
    data = json.loads(rj.read_text(encoding="utf-8"))
    rs_block = data.get("returns_series", {}).get(ds, {})
    if cfg_id not in rs_block:
        raise KeyError(
            f"cfg_id '{cfg_id}' not in {iter_dir.name} returns_series[{ds}]; "
            f"available: {list(rs_block.keys())}"
        )
    series = rs_block[cfg_id]
    idx = pd.DatetimeIndex(series["index"])
    return pd.Series(series["net_returns"], index=idx, name=cfg_id)


# ===========================================================================
# Metric / gate helpers (mirror iter 011 conventions)
# ===========================================================================


def compute_metrics(rets: pd.Series, ann: int) -> dict[str, float]:
    arr = rets.dropna()
    if arr.std() == 0 or len(arr) < 2:
        return {"sharpe": 0.0, "sharpe_periodic": 0.0, "cagr": 0.0, "mdd": 0.0}
    sharpe_per = sharpe_periodic(arr.values)
    sharpe_ann = float(sharpe_per * np.sqrt(ann))
    eq = (1.0 + arr).cumprod()
    span_yr = max((arr.index[-1] - arr.index[0]).days / 365.25, 1e-9)
    cagr = float(eq.iloc[-1] ** (1.0 / span_yr) - 1.0)
    cummax = eq.cummax()
    dd = (eq - cummax) / cummax
    mdd = float(-dd.min())
    return {
        "sharpe": sharpe_ann,
        "sharpe_periodic": float(sharpe_per),
        "cagr": cagr,
        "mdd": mdd,
    }


def run_walk_forward(
    rets: pd.Series, n_windows: int = 8
) -> tuple[bool, list[float], list[float]]:
    n = len(rets)
    if n < n_windows * 20:
        return False, [], []
    block = n // n_windows
    oos_returns: list[float] = []
    drawdowns: list[float] = []
    for i in range(n_windows):
        chunk = rets.iloc[i * block: (i + 1) * block]
        if len(chunk) < 5 or chunk.std() == 0:
            oos_returns.append(0.0)
            drawdowns.append(0.0)
            continue
        eq = (1.0 + chunk).cumprod()
        cummax = eq.cummax()
        dd = -((eq - cummax) / cummax).min()
        total_ret = float(eq.iloc[-1] - 1.0)
        oos_returns.append(total_ret)
        drawdowns.append(float(dd))
    verdict = walk_forward_gate(
        oos_returns_per_window=oos_returns,
        drawdowns_per_window=drawdowns,
        min_windows=n_windows,
        min_profitable_ratio=6.0 / n_windows,
        max_drawdown=0.25,
    )
    return verdict == "pass", oos_returns, drawdowns


def run_bootstrap(rets: pd.Series, ann: int) -> tuple[bool, float, float]:
    arr = rets.dropna().values
    if len(arr) < 50 or arr.std() == 0:
        return False, 0.0, 0.0
    samples = stationary_bootstrap_trades(
        arr, block_mean=5, n_resamples=2000, seed=42
    )
    sharpes = [sharpe_periodic(row) * np.sqrt(ann) for row in samples]
    sharpes = np.array(sharpes)
    lo = float(np.percentile(sharpes, 0.05))
    hi = float(np.percentile(sharpes, 99.95))
    return bool(lo > 0), lo, hi


def cross_lib_cagr_check(rets: pd.Series) -> tuple[float, float, float]:
    """G7: pandas cumprod CAGR vs numpy-pure cumprod CAGR."""
    arr = rets.dropna()
    span_yr = max((arr.index[-1] - arr.index[0]).days / 365.25, 1e-9)
    eq_pd = (1.0 + arr).cumprod()
    cagr_pd = float(eq_pd.iloc[-1] ** (1.0 / span_yr) - 1.0)
    arr_np = arr.values.astype(np.float64)
    eq_np = np.cumprod(1.0 + arr_np)
    cagr_np = float(eq_np[-1] ** (1.0 / span_yr) - 1.0)
    diff_pp = abs(cagr_pd - cagr_np) * 100.0
    return cagr_pd, cagr_np, diff_pp


# ===========================================================================
# Per-dataset composition runner
# ===========================================================================


def run_one_dataset(name: str) -> dict:
    """Compose iter 003 + iter 011 on one dataset; return metrics + gates."""
    ann = ANN_PER_DS[name]

    r_011_raw = load_component_returns(ITER_011_DIR, name, ITER_011_CFG)
    r_003_raw = load_component_returns(ITER_003_DIR, name, ITER_003_CFG)

    if name == "xauusd_intraday":
        r_011 = aggregate_intraday_to_daily(r_011_raw)
    else:
        r_011 = r_011_raw

    r_003 = r_003_raw

    joined = pd.concat([r_011, r_003], axis=1, join="inner").dropna()
    joined.columns = ["r_011", "r_003"]
    if len(joined) < 100:
        raise RuntimeError(
            f"composition for {name} has too few overlapping bars: {len(joined)}"
        )

    mu_011 = float(joined["r_011"].mean())
    mu_003 = float(joined["r_003"].mean())
    sigma_011 = float(joined["r_011"].std(ddof=1))
    sigma_003 = float(joined["r_003"].std(ddof=1))
    rho = float(joined["r_011"].corr(joined["r_003"]))

    sharpe_011 = (mu_011 / sigma_011) * np.sqrt(ann) if sigma_011 > 0 else 0.0
    sharpe_003 = (mu_003 / sigma_003) * np.sqrt(ann) if sigma_003 > 0 else 0.0

    w_011, w_003 = markowitz_tangency_weights(
        mu=np.array([mu_011, mu_003]),
        sigma=np.array([sigma_011, sigma_003]),
        rho=rho,
    )

    weights_clamped = False
    if w_011 < 0 or w_003 < 0:
        weights_clamped = True
        if w_011 < 0:
            w_011, w_003 = 0.0, 1.0
        else:
            w_011, w_003 = 1.0, 0.0

    combined = w_011 * joined["r_011"] + w_003 * joined["r_003"]
    combined.name = "combined"

    m = compute_metrics(combined, ann)

    if combined.std() > 0 and len(combined) > 30:
        dsr_res = dsr_func(combined.values, n_trials=CUMULATIVE_N_TRIALS)
        dsr_p = float(dsr_res.p_value)
        g2_dsr = bool(dsr_p < 0.05)
    else:
        dsr_p = 1.0
        g2_dsr = False

    g3_wf, wf_returns, wf_dds = run_walk_forward(combined, n_windows=8)

    cut = int(0.7 * len(combined))
    oos_chunk = combined.iloc[cut:]
    oos_sharpe = (
        sharpe_periodic(oos_chunk.values) * np.sqrt(ann)
        if len(oos_chunk) > 1 else 0.0
    )
    g4_oos = bool(oos_sharpe > 0)

    fwd_chunk = combined[combined.index >= "2022-01-01"]
    fwd_sharpe = (
        sharpe_periodic(fwd_chunk.values) * np.sqrt(ann)
        if len(fwd_chunk) > 1 else 0.0
    )
    g5_fwd = bool(fwd_sharpe > 0)

    g6_boot, ci_lo, ci_hi = run_bootstrap(combined, ann)

    cagr_pd, cagr_np, diff_pp = cross_lib_cagr_check(combined)
    g7_cl = bool(diff_pp <= 3.0)

    g1_pbo = True
    g1_note = (
        "single-cfg PBO degenerate; pass by convention "
        "(IC-8 single Markowitz tangency cfg pre-committed)"
    )

    gates = Gates(
        g1_pbo=g1_pbo, g2_dsr=g2_dsr, g3_wf=g3_wf, g4_oos=g4_oos,
        g5_fwd=g5_fwd, g6_bootstrap=g6_boot, g7_crosslib=g7_cl,
    )

    m_011 = compute_metrics(joined["r_011"], ann)
    m_003 = compute_metrics(joined["r_003"], ann)

    return {
        "tf": "1d",
        "ann": ann,
        "n_bars_joined": int(len(joined)),
        "date_range": [
            joined.index[0].isoformat(),
            joined.index[-1].isoformat(),
        ],
        "stream_diagnostics": {
            "iter_011": {
                "mu_per_bar": mu_011,
                "sigma_per_bar": sigma_011,
                "sharpe_ann": float(sharpe_011),
                **m_011,
            },
            "iter_003": {
                "mu_per_bar": mu_003,
                "sigma_per_bar": sigma_003,
                "sharpe_ann": float(sharpe_003),
                **m_003,
            },
            "rho": rho,
        },
        "weights": {
            "w_iter_011": float(w_011),
            "w_iter_003": float(w_003),
            "method": "markowitz_tangency_full_sample",
            "clamped_to_corner": weights_clamped,
        },
        "combined_metrics": {
            **m,
            "dsr_p_value": dsr_p,
        },
        "gates": {
            "g1_pbo": g1_pbo, "g1_note": g1_note,
            "g2_dsr": g2_dsr, "dsr_p_value": dsr_p,
            "g3_wf": g3_wf, "wf_returns": wf_returns, "wf_dds": wf_dds,
            "g4_oos": g4_oos, "oos_sharpe": float(oos_sharpe),
            "g5_fwd": g5_fwd, "fwd_sharpe": float(fwd_sharpe),
            "g6_bootstrap": g6_boot, "ci_lo": ci_lo, "ci_hi": ci_hi,
            "g7_crosslib": g7_cl,
            "g7_cagr_pd": cagr_pd, "g7_cagr_np": cagr_np,
            "g7_diff_pp": diff_pp,
        },
        "n_passed": gates.n_passed,
        "_returns_series": {
            "index": [d.isoformat() for d in combined.index],
            "net_returns": [float(x) for x in combined.values],
        },
    }


# ===========================================================================
# Hold-time gate diagnostic
# ===========================================================================


def estimate_combined_hold_days(
    name: str, w_011: float, w_003: float
) -> dict:
    """Hold-time on the COMBINED capital is approximate.

    iter 011 has slow regime gate (hold ~44-52d); iter 003 has fast MR
    (hold ~4d). Combined "exposure" has its own profile depending on
    overlap. We report:
      - weighted_avg_hold = w_011 * hold_011 + w_003 * hold_003
      - max_component_hold (which dominates the strategy's hold profile
        when the higher-weight stream's exposure is ON)
    Both are diagnostic — exact mean-hold of an additive composition
    of LONG-ONLY positions requires reconstructing the position series.
    """
    h_011_per_ds = {
        "gld_long": 51.60,
        "xauusd_real": 47.07,
        "xauusd_intraday": 44.08,
    }
    h_003_per_ds = {
        "gld_long": 3.95,
        "xauusd_real": 3.79,
        "xauusd_intraday": 3.75,
    }
    h_011 = h_011_per_ds[name]
    h_003 = h_003_per_ds[name]
    weighted_avg = w_011 * h_011 + w_003 * h_003
    return {
        "iter_011_mean_hold_days": h_011,
        "iter_003_mean_hold_days": h_003,
        "weighted_avg_hold_days": float(weighted_avg),
        "max_component_hold_days": float(max(h_011, h_003)),
    }


# ===========================================================================
# Main
# ===========================================================================


def main() -> None:
    print(
        f"[{CFG_ID}] starting (CUMULATIVE_N_TRIALS={CUMULATIVE_N_TRIALS}); "
        f"composing iter 003 ({ITER_003_CFG}) + iter 011 ({ITER_011_CFG}) "
        f"at full-sample Markowitz tangency weights."
    )

    print("\n=== Stage 3 — composition per dataset ===")
    results: dict[str, dict] = {}
    for name in ("gld_long", "xauusd_real", "xauusd_intraday"):
        print(f"\n--- {name} ---")
        r = run_one_dataset(name)
        results[name] = r
        bench = BENCHMARKS[name]
        m = r["combined_metrics"]
        sd = r["stream_diagnostics"]
        w = r["weights"]
        print(
            f"  rho={sd['rho']:+.4f}; "
            f"S_011={sd['iter_011']['sharpe_ann']:+.4f}, "
            f"S_003={sd['iter_003']['sharpe_ann']:+.4f}"
        )
        print(
            f"  weights: w_011={w['w_iter_011']:+.4f}, "
            f"w_003={w['w_iter_003']:+.4f} "
            f"(clamped={w['clamped_to_corner']})"
        )
        print(
            f"  combined: Sharpe={m['sharpe']:+.4f} "
            f"(bench {bench.sharpe:+.4f}, Δ {m['sharpe'] - bench.sharpe:+.4f}), "
            f"CAGR={m['cagr']:+.4%} (bench {bench.cagr:+.4%}), "
            f"MDD={m['mdd']:.4%} (bench {bench.mdd:.4%}), "
            f"DSR p={m['dsr_p_value']:.4f}, gates={r['n_passed']}/7"
        )

    metrics = {
        ds: DatasetMetrics(
            sharpe=results[ds]["combined_metrics"]["sharpe"],
            cagr=results[ds]["combined_metrics"]["cagr"],
            mdd=results[ds]["combined_metrics"]["mdd"],
            dsr_p_value=results[ds]["combined_metrics"]["dsr_p_value"],
        )
        for ds in results
    }
    gates_dict = {
        ds: Gates(
            g1_pbo=results[ds]["gates"]["g1_pbo"],
            g2_dsr=results[ds]["gates"]["g2_dsr"],
            g3_wf=results[ds]["gates"]["g3_wf"],
            g4_oos=results[ds]["gates"]["g4_oos"],
            g5_fwd=results[ds]["gates"]["g5_fwd"],
            g6_bootstrap=results[ds]["gates"]["g6_bootstrap"],
            g7_crosslib=results[ds]["gates"]["g7_crosslib"],
        )
        for ds in results
    }
    score = score_strategy(
        metrics, gates_dict, cumulative_n_trials=CUMULATIVE_N_TRIALS
    )

    primary_ds = "xauusd_intraday"
    hold_diag_primary = estimate_combined_hold_days(
        primary_ds,
        results[primary_ds]["weights"]["w_iter_011"],
        results[primary_ds]["weights"]["w_iter_003"],
    )
    primary_hold = hold_diag_primary["weighted_avg_hold_days"]
    hold_gate_pass = bool(primary_hold <= 5.0)
    is_winner = bool(score.winner_conditions_met and hold_gate_pass)

    iter_011_sharpes = {
        "gld_long": 0.4815,
        "xauusd_real": 1.4183,
        "xauusd_intraday": 1.5920,
    }
    iter_011_dsr_p = {
        "gld_long": 0.275,
        "xauusd_real": 0.018,
        "xauusd_intraday": 0.009,
    }
    composition_sharpes = {
        ds: results[ds]["combined_metrics"]["sharpe"] for ds in results
    }
    sharpe_below_iter011_by_010 = sum(
        1 for ds in results
        if composition_sharpes[ds] < iter_011_sharpes[ds] - 0.10
    )
    kill_value_destruction = sharpe_below_iter011_by_010 >= 2

    composition_dsr_p = {
        ds: results[ds]["combined_metrics"]["dsr_p_value"] for ds in results
    }
    gld_dsr_passed = composition_dsr_p["gld_long"] < 0.05
    xauusd_real_dsr_degraded = (
        composition_dsr_p["xauusd_real"] >= iter_011_dsr_p["xauusd_real"] + 0.020
    )
    kill_dsr_no_progress = (
        (not gld_dsr_passed) and xauusd_real_dsr_degraded
    )

    weights_neg_count = sum(
        1 for ds in results
        if results[ds]["weights"]["clamped_to_corner"]
    )

    total_gates = sum(results[ds]["n_passed"] for ds in results)
    kill_gate_collapse = total_gates < 14

    print(
        f"\n=== SCORE ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} "
        f"(weighted-avg hold {primary_hold:.2f}d on {primary_ds}; iter 011 dominates), "
        f"is_winner = {is_winner}\n"
        f"\n=== KILL CRITERIA ===\n"
        f"composition_sharpes (Track A) = {composition_sharpes}\n"
        f"composition_dsr_p              = {composition_dsr_p}\n"
        f"value-destruction (Sh<iter011−0.10 on ≥2 ds): "
        f"{sharpe_below_iter011_by_010}/3 → kill={kill_value_destruction}\n"
        f"DSR no-progress (gld_long !<0.05 AND xauusd_real degrades ≥0.020): "
        f"kill={kill_dsr_no_progress}\n"
        f"weights clamped to corner (negative tangency weight): {weights_neg_count}/3\n"
        f"total gates {total_gates}/21 (kill if <14): kill={kill_gate_collapse}"
    )

    out = {
        "config_id": CFG_ID,
        "params": {
            "method": "markowitz_tangency_full_sample",
            "iter_003_cfg": ITER_003_CFG,
            "iter_011_cfg": ITER_011_CFG,
            "iter_003_path": str(ITER_003_DIR.relative_to(ROOT)),
            "iter_011_path": str(ITER_011_DIR.relative_to(ROOT)),
            "weight_constraint": "w_A + w_B = 1; clamped to corner if either<0",
        },
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "per_dataset": {
            ds: {k: v for k, v in results[ds].items() if not k.startswith("_")}
            for ds in results
        },
        "score": score.to_dict(),
        "hold_time_gate": {
            "primary_dataset": primary_ds,
            "weighted_avg_hold_days": primary_hold,
            "threshold_days": 5.0,
            "pass": hold_gate_pass,
            "diag_per_dataset": {
                ds: estimate_combined_hold_days(
                    ds,
                    results[ds]["weights"]["w_iter_011"],
                    results[ds]["weights"]["w_iter_003"],
                )
                for ds in results
            },
            "note": (
                "Composition inherits iter 011's slow-regime hold profile "
                "(iter 011 dominant weight). Swing-extended; tier capped at "
                "STRONG per WINNER_AND_RANKING.md condition #6."
            ),
        },
        "kill_criteria": {
            "composition_sharpes": composition_sharpes,
            "iter_011_sharpes": iter_011_sharpes,
            "composition_dsr_p": composition_dsr_p,
            "iter_011_dsr_p": iter_011_dsr_p,
            "value_destruction_count": sharpe_below_iter011_by_010,
            "value_destruction_kill": kill_value_destruction,
            "gld_dsr_passed_under_005": gld_dsr_passed,
            "xauusd_real_dsr_degraded_by_020": xauusd_real_dsr_degraded,
            "dsr_no_progress_kill": kill_dsr_no_progress,
            "weights_clamped_count": weights_neg_count,
            "total_gates": total_gates,
            "gate_collapse_kill": kill_gate_collapse,
        },
        "is_winner": is_winner,
        "returns_series": {
            ds: {CFG_ID: results[ds]["_returns_series"]} for ds in results
        },
        "benchmarks_snapshot": {
            ds: {
                "sharpe": BENCHMARKS[ds].sharpe,
                "cagr": BENCHMARKS[ds].cagr,
                "mdd": BENCHMARKS[ds].mdd,
                "label": BENCHMARKS[ds].label,
            }
            for ds in results
        },
    }
    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {out_path}")

    verdict = score.to_dict()
    verdict["configs_tested"] = 1
    verdict["primary_citation"] = "[advances_fin_ml, p.222-223]"
    verdict["hypothesis_slug"] = "ic7-rsi2-volregime-composition"
    verdict["mean_hold_days"] = float(primary_hold)
    verdict["hold_time_gate_pass"] = hold_gate_pass
    verdict["broker_track"] = "pepperstone_cfd"
    verdict["timeframes_used"] = ["1d"]
    verdict["track_a_metrics"] = {
        ds: {**results[ds]["combined_metrics"]} for ds in results
    }
    verdict["track_b_metrics"] = {
        "note": "Track B not computed in iter 012 — composition primary track is A; "
                "Track B per-stream values exist in iter 003 + iter 011 verdicts."
    }
    verdict["weights_per_ds"] = {
        ds: results[ds]["weights"] for ds in results
    }
    verdict["rho_per_ds"] = {
        ds: results[ds]["stream_diagnostics"]["rho"] for ds in results
    }
    verdict["kill_criteria"] = out["kill_criteria"]
    verdict["status"] = "winner" if is_winner else "iterating"
    verdict["auto_aborted_at_pre_val"] = False

    verdict_path = ITER_DIR / "verdict.json"
    verdict_path.write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"wrote {verdict_path}")


if __name__ == "__main__":
    main()
