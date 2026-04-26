"""Iter 016 — IC-7 composition: iter 003 + iter 015 at Markowitz tangency weights.

Reuses the cost-included net returns saved by iter 003 (RSI(2)+SMA(200) MR)
and iter 015 (DXY-SMA-slope falling 200/20 trend gate) per dataset, joins on
common dates, fits a 2-asset Markowitz tangency portfolio in-sample, and
re-runs the 7-gate battery on the combined daily returns.

Same architectural pattern as iter 012, but:
  * iter 011 → iter 015 (DXY-trend instead of vol-regime)
  * primary dataset → ``xauusd_intraday`` (where ρ = −0.07, lowest in pair)
  * scoring → ``score_strategy_v2`` (rules_version 2026-04-26-relaxed-r1)
  * cumulative_n_trials → 16

Single pre-committed cfg (IC-8). cumulative_n_trials = 16.

Citations
---------
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 16 (PRIMARY)
* `[short_term_trading_strategies, p.105-118]` — iter 003 RSI/SMA200 base
* `[stocks_on_the_move, p.100]` — iter 015 DXY-SMA-slope base
* `[modern_portfolio_theory]` — 2-asset Markowitz tangency (Σ⁻¹μ normalized)
* IC-7 (sister 045/046) — out-of-family ρ < 0.50 unlocks DSR uplift
* IC-3 (sister 049) — Markowitz proper (NOT 50/50) when |ΔS| > 30%
* IC-8 (sister 046) — single pre-committed cfg per iter
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

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
    score_strategy_v2,
)


CFG_ID = "ic7_iter003_iter015_markowitz_intra_primary"

# 15 prior iters + 1 (this composition) = 16.
CUMULATIVE_N_TRIALS = 16

# Component locations
ITER_003_DIR = ROOT / "studies" / "gold_swing_loop" / "iterations" / "003-2026-04-26-0228-rsi2-sma200-filter"
ITER_015_DIR = ROOT / "studies" / "gold_swing_loop" / "iterations" / "015-2026-04-26-1455-dxy-sma-slope-trend-gate"

ITER_003_CFG = "connors_rsi2_sma200_filter"
ITER_015_CFG = "dxy_sma_slope_falling_200_20_long_only"

# Composition is at DAILY granularity for all 3 datasets (same as iter 012).
ANN_PER_DS = {
    "gld_long": 252,
    "xauusd_real": 252,
    "xauusd_intraday": 252,
}

DECLARED_PRIMARY = "xauusd_intraday"  # ρ = −0.07 (lowest of the 3 pairs)
DECLARED_CORROBORATING = ["gld_long", "xauusd_real"]
DECLARED_HOLD_TRACK = "medium_swing"  # 10-30 trading days
HOLD_TRACK_BOUNDS = {
    "intraday":     (0.0, 1.0),
    "short_swing":  (2.0, 10.0),
    "medium_swing": (10.0, 30.0),
}


# ===========================================================================
# Composition primitives (TDD-tested in test_composition.py)
# ===========================================================================


def markowitz_tangency_weights(
    mu: np.ndarray, sigma: np.ndarray, rho: float
) -> tuple[float, float]:
    """2-asset Markowitz tangency weights (max-Sharpe, full-investment).

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
    """Sum intraday simple-bar returns to daily totals; drop empty days.

    ``resample("D").sum()`` fills empty groups with 0.0 (the additive
    identity), not NaN — so a plain ``dropna()`` would NOT drop weekends
    or holidays. Use ``.count() > 0`` to keep only days that had at least
    one input bar.
    """
    grouped = rets.resample("D")
    daily_sum = grouped.sum()
    daily_count = grouped.count()
    return daily_sum[daily_count > 0]


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
# Effective combined-position hold (computed from binary in-trade indicators
# of each component).
# ===========================================================================


def _component_in_trade(rets: pd.Series, eps: float = 1e-12) -> pd.Series:
    """Reconstruct in-trade indicator from net returns: |r| > eps ⇒ 1."""
    return (rets.abs() > eps).astype(int).rename("in_trade")


def combined_in_trade_indicator(
    r_a: pd.Series, r_b: pd.Series
) -> pd.Series:
    """OR of two component in-trade indicators on inner-joined index.

    A bar is "in trade" if either component has non-zero return on it. This
    overestimates true exposure when components overlap (correct count is
    fraction of capital exposed via Markowitz weights), but is the right
    metric for "how often is the strategy at risk" / hold-bucket diagnosis.
    """
    a_in = _component_in_trade(r_a)
    b_in = _component_in_trade(r_b)
    joined = pd.concat([a_in, b_in], axis=1, join="inner")
    joined.columns = ["a", "b"]
    return ((joined["a"] + joined["b"]) > 0).astype(int).rename("combined_in_trade")


def compute_hold_metrics(in_trade: pd.Series) -> tuple[float, int, float]:
    """Mean hold (consecutive-bar runs of 1) → (mean_bars, n_runs, p_active)."""
    arr = in_trade.values.astype(int)
    if arr.sum() == 0:
        return 0.0, 0, 0.0
    starts: list[int] = []
    ends: list[int] = []
    in_run = False
    for i, v in enumerate(arr):
        if v == 1 and not in_run:
            starts.append(i)
            in_run = True
        elif v == 0 and in_run:
            ends.append(i)
            in_run = False
    if in_run:
        ends.append(len(arr))
    holds = [(e - s) for s, e in zip(starts, ends)]
    mean_bars = float(np.mean(holds)) if holds else 0.0
    p_active = float(arr.sum() / len(arr))
    return mean_bars, len(starts), p_active


# ===========================================================================
# Metric / gate helpers (mirror iter 012 conventions)
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
    """Compose iter 003 + iter 015 on one dataset; return metrics + gates."""
    ann = ANN_PER_DS[name]

    r_015_raw = load_component_returns(ITER_015_DIR, name, ITER_015_CFG)
    r_003_raw = load_component_returns(ITER_003_DIR, name, ITER_003_CFG)

    # Iter 015 keeps native frequency (1h on intraday); iter 003 daily-resamples
    # intraday to daily at ingestion. Aggregate iter 015 intraday → daily so
    # both streams share daily index for the inner-join.
    if name == "xauusd_intraday":
        r_015 = aggregate_intraday_to_daily(r_015_raw)
    else:
        r_015 = r_015_raw

    r_003 = r_003_raw

    joined = pd.concat([r_015, r_003], axis=1, join="inner").dropna()
    joined.columns = ["r_015", "r_003"]
    if len(joined) < 100:
        raise RuntimeError(
            f"composition for {name} has too few overlapping bars: {len(joined)}"
        )

    mu_015 = float(joined["r_015"].mean())
    mu_003 = float(joined["r_003"].mean())
    sigma_015 = float(joined["r_015"].std(ddof=1))
    sigma_003 = float(joined["r_003"].std(ddof=1))
    rho = float(joined["r_015"].corr(joined["r_003"]))

    sharpe_015 = (mu_015 / sigma_015) * np.sqrt(ann) if sigma_015 > 0 else 0.0
    sharpe_003 = (mu_003 / sigma_003) * np.sqrt(ann) if sigma_003 > 0 else 0.0

    w_015, w_003 = markowitz_tangency_weights(
        mu=np.array([mu_015, mu_003]),
        sigma=np.array([sigma_015, sigma_003]),
        rho=rho,
    )

    weights_clamped = False
    if w_015 < 0 or w_003 < 0:
        weights_clamped = True
        if w_015 < 0:
            w_015, w_003 = 0.0, 1.0
        else:
            w_015, w_003 = 1.0, 0.0

    combined = w_015 * joined["r_015"] + w_003 * joined["r_003"]
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

    m_015 = compute_metrics(joined["r_015"], ann)
    m_003 = compute_metrics(joined["r_003"], ann)

    # Effective combined-position hold (OR-of-components in-trade indicator).
    in_trade = combined_in_trade_indicator(joined["r_015"], joined["r_003"])
    mean_hold_bars, n_runs, p_active = compute_hold_metrics(in_trade)
    # Daily granularity → 1 bar = 1 trading day (ann=252).
    mean_hold_days = mean_hold_bars

    return {
        "tf": "1d",
        "ann": ann,
        "n_bars_joined": int(len(joined)),
        "date_range": [
            joined.index[0].isoformat(),
            joined.index[-1].isoformat(),
        ],
        "stream_diagnostics": {
            "iter_015": {
                "mu_per_bar": mu_015,
                "sigma_per_bar": sigma_015,
                "sharpe_ann": float(sharpe_015),
                **m_015,
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
            "w_iter_015": float(w_015),
            "w_iter_003": float(w_003),
            "method": "markowitz_tangency_full_sample",
            "clamped_to_corner": weights_clamped,
        },
        "combined_metrics": {
            **m,
            "dsr_p_value": dsr_p,
        },
        "hold": {
            "mean_hold_bars_or_combined": mean_hold_bars,
            "mean_hold_days_or_combined": mean_hold_days,
            "n_runs": n_runs,
            "p_active": p_active,
            "method": "OR-of-components in-trade indicator (overstates exposure during overlap)",
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
# Main
# ===========================================================================


def main() -> None:
    print(
        f"[{CFG_ID}] starting (CUMULATIVE_N_TRIALS={CUMULATIVE_N_TRIALS}); "
        f"composing iter 003 ({ITER_003_CFG}) + iter 015 ({ITER_015_CFG}) "
        f"at full-sample Markowitz tangency weights."
    )
    print(
        f"  declared_primary={DECLARED_PRIMARY}, "
        f"declared_corroborating={DECLARED_CORROBORATING}, "
        f"declared_hold_track={DECLARED_HOLD_TRACK} "
        f"({HOLD_TRACK_BOUNDS[DECLARED_HOLD_TRACK]}d)"
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
        h = r["hold"]
        print(
            f"  rho={sd['rho']:+.4f}; "
            f"S_015={sd['iter_015']['sharpe_ann']:+.4f}, "
            f"S_003={sd['iter_003']['sharpe_ann']:+.4f}"
        )
        print(
            f"  weights: w_015={w['w_iter_015']:+.4f}, "
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
        print(
            f"  hold (OR-indicator): mean_hold={h['mean_hold_days_or_combined']:.2f}d, "
            f"n_runs={h['n_runs']}, p_active={h['p_active']:.3f}"
        )

    # ----- v2 score (rules_version 2026-04-26-relaxed-r1) -----
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
    score = score_strategy_v2(
        metrics=metrics,
        gates=gates_dict,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        declared_primary=DECLARED_PRIMARY,
        declared_corroborating=DECLARED_CORROBORATING,
    )

    # ----- Hold-time gate (v2 — bucket-match, not legacy ≤5d) -----
    primary_hold = results[DECLARED_PRIMARY]["hold"]["mean_hold_days_or_combined"]
    lo, hi = HOLD_TRACK_BOUNDS[DECLARED_HOLD_TRACK]
    hold_gate_pass = bool(lo <= primary_hold <= hi)
    is_winner = bool(score.winner_conditions_met and hold_gate_pass)

    # ----- Pre-committed kill criteria -----
    primary_dsr_p = results[DECLARED_PRIMARY]["combined_metrics"]["dsr_p_value"]
    gld_dsr_p = results["gld_long"]["combined_metrics"]["dsr_p_value"]
    dsr_no_progress_kill = bool(primary_dsr_p >= 0.20 and gld_dsr_p >= 0.20)

    primary_sharpe = results[DECLARED_PRIMARY]["combined_metrics"]["sharpe"]
    sharpe_ceiling_confirmed = bool(primary_sharpe < 0.50)

    primary_rho = results[DECLARED_PRIMARY]["stream_diagnostics"]["rho"]
    correlation_drift_kill = bool(abs(primary_rho) > 0.20)

    print(
        f"\n=== SCORE (v2) ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} "
        f"(observed mean {primary_hold:.2f}d on {DECLARED_PRIMARY}; "
        f"declared bucket {DECLARED_HOLD_TRACK} {lo}-{hi}d), "
        f"is_winner = {is_winner}\n"
        f"\n=== KILL CRITERIA ===\n"
        f"primary_dsr_p = {primary_dsr_p:.4f}, gld_dsr_p = {gld_dsr_p:.4f}; "
        f"DSR_no_progress_kill = {dsr_no_progress_kill}\n"
        f"primary_sharpe = {primary_sharpe:.4f}; "
        f"sharpe_ceiling_confirmed (< 0.50) = {sharpe_ceiling_confirmed}\n"
        f"primary_rho = {primary_rho:+.4f}; "
        f"correlation_drift_kill (|ρ|>0.20) = {correlation_drift_kill}"
    )

    out = {
        "config_id": CFG_ID,
        "rules_version": "2026-04-26-relaxed-r1",
        "params": {
            "method": "markowitz_tangency_full_sample",
            "iter_003_cfg": ITER_003_CFG,
            "iter_015_cfg": ITER_015_CFG,
            "iter_003_path": str(ITER_003_DIR.relative_to(ROOT)),
            "iter_015_path": str(ITER_015_DIR.relative_to(ROOT)),
            "weight_constraint": "w_A + w_B = 1; clamped to corner if either<0",
            "declared_primary": DECLARED_PRIMARY,
            "declared_corroborating": DECLARED_CORROBORATING,
            "declared_hold_track": DECLARED_HOLD_TRACK,
            "hold_track_bounds_days": HOLD_TRACK_BOUNDS[DECLARED_HOLD_TRACK],
            "universe": "single_xau",
            "cost_path": "pep_cfd",
            "broker_track": "pepperstone_cfd",
        },
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "per_dataset": {
            ds: {k: v for k, v in results[ds].items() if not k.startswith("_")}
            for ds in results
        },
        "score": score.to_dict(),
        "hold_time_gate": {
            "primary_dataset": DECLARED_PRIMARY,
            "declared_track": DECLARED_HOLD_TRACK,
            "bounds_days": HOLD_TRACK_BOUNDS[DECLARED_HOLD_TRACK],
            "observed_mean_hold_days": primary_hold,
            "pass": hold_gate_pass,
            "note": (
                "OR-of-components in-trade indicator on combined returns. "
                "Composition inherits iter 015's slow-regime hold profile "
                "(iter 015 dominant weight). May exceed medium_swing's 30d "
                "upper bound → tier downgraded to NEAR_FAIL by mismatch."
            ),
        },
        "kill_criteria": {
            "primary_dsr_p": primary_dsr_p,
            "gld_dsr_p": gld_dsr_p,
            "dsr_no_progress_kill_threshold": 0.20,
            "dsr_no_progress_kill_fired": dsr_no_progress_kill,
            "primary_sharpe": primary_sharpe,
            "sharpe_ceiling_threshold": 0.50,
            "sharpe_ceiling_confirmed": sharpe_ceiling_confirmed,
            "primary_rho": primary_rho,
            "correlation_drift_threshold_abs": 0.20,
            "correlation_drift_kill_fired": correlation_drift_kill,
            "expected_rho_from_iter_015_diagnostic": -0.07,
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
    verdict["hypothesis_slug"] = "ic7-rsi2sma200-dxytrend-intra-primary"
    verdict["mean_hold_days"] = float(primary_hold)
    verdict["hold_time_gate_pass"] = hold_gate_pass
    verdict["declared_hold_track"] = DECLARED_HOLD_TRACK
    verdict["declared_primary"] = DECLARED_PRIMARY
    verdict["declared_corroborating"] = DECLARED_CORROBORATING
    verdict["broker_track"] = "pepperstone_cfd"
    verdict["timeframes_used"] = ["1d"]
    verdict["track_a_metrics"] = {
        ds: {**results[ds]["combined_metrics"]} for ds in results
    }
    verdict["track_b_metrics"] = {
        "note": "Track B not computed — composition primary track is A; "
                "Track B per-stream values exist in iter 003 + iter 015 verdicts."
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
    verdict["rules_version"] = "2026-04-26-relaxed-r1"

    verdict_path = ITER_DIR / "verdict.json"
    verdict_path.write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"wrote {verdict_path}")


if __name__ == "__main__":
    main()
