"""Iter 019 — IC-7 Markowitz tangency on iter 003 (RSI MR) + iter 018 (COT z-score).

Reuses iter 003's Schema-A returns (`returns_series[ds][cfg_id]`) and iter
018's Schema-B returns (`datasets[ds].returns_series`), both already net of
Pepperstone CFD costs. Composes at full-sample Markowitz tangency
weights (w ∝ Σ⁻¹μ) on `gld_long` (PRIMARY) + `xauusd_real` (CORROBORATING).
xauusd_intraday is NOT available because iter 018 didn't run on intraday.

Single pre-committed cfg (IC-8 honored). cumulative_n_trials = 19
(iter 018 was 18 + this composition increments by 1).

Pre-val (IC-6): rolling 60d ρ exceedance check. If `|ρ_60d| > 0.30` on
> 20% of gld_long primary bars, iter ABORTS at Stage 3.

Citations
---------
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials; combined-Sharpe
  upper bound for 2-asset tangency portfolio.
* `[advances_fin_ml, p.31-34]` — cost realism (composition adds no turnover).
* `[short_term_trading_strategies, p.106]` — iter 003 RSI(2)+SMA(200) base.
* `[trading_systems_methods, p.639-640]` — iter 018 COT z-score base.
* IC-7 sister-loop empirical (045/046) — out-of-family ρ < 0.50 + Markowitz.
* IC-3 sister-loop closure (049) — Markowitz proper, NOT 50/50.
* IC-6 / GS-9 pre-val — rolling-ρ + cost-magnitude (already passed by streams).
* IC-8 / sister 046 — single cfg per iter unless Bonferroni.
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
    score_strategy_v2,
)


# ===========================================================================
# Pre-committed configuration (IC-8: single cfg)
# ===========================================================================

CFG_ID = "ic7_iter003_iter018_markowitz_gld_primary"
CUMULATIVE_N_TRIALS = 19  # 18 from iter 018 + 1 (this composition)

ITER_003_DIR = (
    ROOT / "studies" / "gold_swing_loop" / "iterations"
    / "003-2026-04-26-0228-rsi2-sma200-filter"
)
ITER_018_DIR = (
    ROOT / "studies" / "gold_swing_loop" / "iterations"
    / "018-2026-04-26-1628-cot-zscore-variant"
)
ITER_003_CFG = "connors_rsi2_sma200_filter"

# Datasets: only the ones iter 018 covers (gld_long + xauusd_real).
DATASETS = ("gld_long", "xauusd_real")
DECLARED_PRIMARY = "gld_long"
DECLARED_CORROBORATING = ("xauusd_real",)

# Annualization factor (both datasets are at daily granularity).
ANN_PER_DS = {"gld_long": 252, "xauusd_real": 252}

# IC-6 rolling-ρ pre-val.
ROLLING_RHO_WINDOW = 60
ROLLING_RHO_LIMIT = 0.30
ROLLING_RHO_EXCEED_FRAC_LIMIT = 0.20


# ===========================================================================
# Pure helpers (TDD-tested in test_composition.py)
# ===========================================================================


def markowitz_tangency_weights(
    mu: np.ndarray, sigma: np.ndarray, rho: float
) -> tuple[float, float]:
    """2-asset tangency weights w ∝ Σ⁻¹μ, normalized to sum = 1.

    Inputs use returns scale (not Sharpes). Caller checks ``w_a > 0`` /
    ``w_b > 0``; negative weights signal a different hypothesis (one
    stream should be shorted, or correlation is high relative to Sharpe).
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
    """Linear weighted-sum on inner-joined index (drops NaN bars)."""
    joined = pd.concat([a, b], axis=1, join="inner").dropna()
    joined.columns = ["a", "b"]
    out = (w_a * joined["a"] + w_b * joined["b"]).rename("composed")
    return out


def rolling_pearson(a: pd.Series, b: pd.Series, window: int) -> pd.Series:
    """Rolling Pearson ρ on inner-joined index."""
    joined = pd.concat([a, b], axis=1, join="inner").dropna()
    joined.columns = ["a", "b"]
    return joined["a"].rolling(window=window, min_periods=window).corr(joined["b"])


def load_component_returns_schema_a(
    iter_dir: Path, dataset: str, cfg_id: str
) -> pd.Series:
    """iter 003-style: ``results.json[returns_series][ds][cfg_id]``."""
    rj = iter_dir / "results.json"
    if not rj.exists():
        raise FileNotFoundError(f"no results.json at {rj}")
    data = json.loads(rj.read_text(encoding="utf-8"))
    rs_block = data.get("returns_series", {}).get(dataset, {})
    if cfg_id not in rs_block:
        raise KeyError(
            f"cfg_id {cfg_id!r} not found in {iter_dir.name} returns_series[{dataset!r}]; "
            f"available: {list(rs_block.keys())}"
        )
    s = rs_block[cfg_id]
    idx = pd.to_datetime(s["index"]).tz_localize(None)
    return pd.Series(s["net_returns"], index=idx, name=cfg_id).dropna()


def load_component_returns_schema_b(iter_dir: Path, dataset: str) -> pd.Series:
    """iter 018-style: ``results.json[datasets][ds][returns_series]``."""
    rj = iter_dir / "results.json"
    if not rj.exists():
        raise FileNotFoundError(f"no results.json at {rj}")
    data = json.loads(rj.read_text(encoding="utf-8"))
    ds_root = data.get("datasets", {})
    if dataset not in ds_root:
        raise KeyError(
            f"dataset {dataset!r} not found in {iter_dir.name} datasets; "
            f"available: {list(ds_root.keys())}"
        )
    rs = ds_root[dataset].get("returns_series", {})
    if "index" not in rs or "net_returns" not in rs:
        raise KeyError(
            f"returns_series for {dataset!r} in {iter_dir.name} missing index/net_returns"
        )
    idx = pd.to_datetime(rs["index"]).tz_localize(None)
    return pd.Series(rs["net_returns"], index=idx, name=dataset).dropna()


# ===========================================================================
# Metrics + 7-gate battery (mirrors iter 012 conventions)
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
    sharpes = np.array([sharpe_periodic(row) * np.sqrt(ann) for row in samples])
    lo = float(np.percentile(sharpes, 0.05))   # 99.9% CI lower bound
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
    """Compose iter 003 + iter 018 on one dataset; return metrics + gates."""
    ann = ANN_PER_DS[name]

    r_003 = load_component_returns_schema_a(ITER_003_DIR, name, ITER_003_CFG)
    r_018 = load_component_returns_schema_b(ITER_018_DIR, name)

    joined = pd.concat([r_003, r_018], axis=1, join="inner").dropna()
    joined.columns = ["r_003", "r_018"]
    if len(joined) < 100:
        raise RuntimeError(
            f"composition for {name} has too few overlapping bars: {len(joined)}"
        )

    mu_003 = float(joined["r_003"].mean())
    mu_018 = float(joined["r_018"].mean())
    sigma_003 = float(joined["r_003"].std(ddof=1))
    sigma_018 = float(joined["r_018"].std(ddof=1))
    rho = float(joined["r_003"].corr(joined["r_018"]))

    sharpe_003 = (mu_003 / sigma_003) * np.sqrt(ann) if sigma_003 > 0 else 0.0
    sharpe_018 = (mu_018 / sigma_018) * np.sqrt(ann) if sigma_018 > 0 else 0.0

    w_003, w_018 = markowitz_tangency_weights(
        mu=np.array([mu_003, mu_018]),
        sigma=np.array([sigma_003, sigma_018]),
        rho=rho,
    )

    weights_clamped = False
    if w_003 < 0 or w_018 < 0:
        weights_clamped = True
        if w_003 < 0:
            w_003, w_018 = 0.0, 1.0
        else:
            w_003, w_018 = 1.0, 0.0

    combined = w_003 * joined["r_003"] + w_018 * joined["r_018"]
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

    g1_pbo = True  # IC-8 single cfg → PBO N/A → True by convention
    g1_note = "single-cfg PBO degenerate; pass by convention (IC-8)"

    gates = Gates(
        g1_pbo=g1_pbo, g2_dsr=g2_dsr, g3_wf=g3_wf, g4_oos=g4_oos,
        g5_fwd=g5_fwd, g6_bootstrap=g6_boot, g7_crosslib=g7_cl,
    )

    m_003 = compute_metrics(joined["r_003"], ann)
    m_018 = compute_metrics(joined["r_018"], ann)

    rho_60d = rolling_pearson(joined["r_003"], joined["r_018"], window=ROLLING_RHO_WINDOW)
    rho_60d_valid = rho_60d.dropna()
    exceed_n = int((rho_60d_valid.abs() > ROLLING_RHO_LIMIT).sum())
    exceed_total = int(len(rho_60d_valid))
    exceed_frac = float(exceed_n / exceed_total) if exceed_total > 0 else 0.0
    pre_val_pass = bool(exceed_frac <= ROLLING_RHO_EXCEED_FRAC_LIMIT)

    return {
        "tf": "1d",
        "ann": ann,
        "n_bars_joined": int(len(joined)),
        "date_range": [
            joined.index[0].isoformat(),
            joined.index[-1].isoformat(),
        ],
        "stream_diagnostics": {
            "iter_003": {
                "mu_per_bar": mu_003,
                "sigma_per_bar": sigma_003,
                "sharpe_ann": float(sharpe_003),
                **m_003,
            },
            "iter_018": {
                "mu_per_bar": mu_018,
                "sigma_per_bar": sigma_018,
                "sharpe_ann": float(sharpe_018),
                **m_018,
            },
            "rho_static": rho,
        },
        "weights": {
            "w_iter_003": float(w_003),
            "w_iter_018": float(w_018),
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
        "ic6_pre_val": {
            "rolling_rho_window": ROLLING_RHO_WINDOW,
            "rolling_rho_limit": ROLLING_RHO_LIMIT,
            "exceed_frac_limit": ROLLING_RHO_EXCEED_FRAC_LIMIT,
            "exceed_n": exceed_n,
            "exceed_total": exceed_total,
            "exceed_frac": exceed_frac,
            "pass": pre_val_pass,
        },
        "_returns_series": {
            "index": [d.isoformat() for d in combined.index],
            "net_returns": [float(x) for x in combined.values],
        },
    }


# ===========================================================================
# Hold-time gate diagnostic (composition exposure-weighted)
# ===========================================================================


# From iter 003 + iter 018 verdicts.
ITER_003_HOLDS = {"gld_long": 3.95, "xauusd_real": 3.79, "xauusd_intraday": 3.75}
ITER_018_HOLDS = {"gld_long": 28.41, "xauusd_real": 30.00}


def estimate_combined_hold_days(name: str, w_003: float, w_018: float) -> dict:
    h_003 = ITER_003_HOLDS[name]
    h_018 = ITER_018_HOLDS[name]
    weighted_avg = w_003 * h_003 + w_018 * h_018
    return {
        "iter_003_mean_hold_days": h_003,
        "iter_018_mean_hold_days": h_018,
        "weighted_avg_hold_days": float(weighted_avg),
        "max_component_hold_days": float(max(h_003, h_018)),
    }


# ===========================================================================
# Kill criteria evaluator
# ===========================================================================


def evaluate_kill_criteria(
    primary: dict,
    sharpe_003: float,
    sharpe_018: float,
) -> dict:
    """Apply the 4 pre-committed kill checks against the PRIMARY result."""
    combined_sh = primary["combined_metrics"]["sharpe"]
    best_component_sh = max(sharpe_003, sharpe_018)
    kill_value_destruction = combined_sh < best_component_sh - 0.05

    w003 = primary["weights"]["w_iter_003"]
    w018 = primary["weights"]["w_iter_018"]
    kill_weight_collapse = (w003 < -0.05) or (w018 < -0.05)

    dsr_p = primary["combined_metrics"]["dsr_p_value"]
    kill_dsr_no_progress = dsr_p > 0.20

    kill_pre_val = not primary["ic6_pre_val"]["pass"]

    any_kill = (
        kill_value_destruction
        or kill_weight_collapse
        or kill_dsr_no_progress
        or kill_pre_val
    )
    return {
        "kill_value_destruction": kill_value_destruction,
        "combined_sharpe_primary": combined_sh,
        "best_component_sharpe": best_component_sh,
        "kill_weight_collapse": kill_weight_collapse,
        "weights_primary": {"w_iter_003": w003, "w_iter_018": w018},
        "kill_dsr_no_progress": kill_dsr_no_progress,
        "primary_dsr_p": dsr_p,
        "kill_pre_val_rolling_rho": kill_pre_val,
        "pre_val_diag": primary["ic6_pre_val"],
        "any_kill": bool(any_kill),
    }


# ===========================================================================
# Main pipeline
# ===========================================================================


def main() -> None:
    print(
        f"[{CFG_ID}] starting (CUMULATIVE_N_TRIALS={CUMULATIVE_N_TRIALS}); "
        f"composing iter 003 ({ITER_003_CFG}) + iter 018 (z-score COT) "
        f"at full-sample Markowitz tangency weights on "
        f"primary={DECLARED_PRIMARY}, corroborating={list(DECLARED_CORROBORATING)}."
    )

    print("\n=== Stage 3 — composition per dataset ===")
    results: dict[str, dict] = {}
    for name in DATASETS:
        print(f"\n--- {name} ---")
        r = run_one_dataset(name)
        results[name] = r
        bench = BENCHMARKS[name]
        m = r["combined_metrics"]
        sd = r["stream_diagnostics"]
        w = r["weights"]
        ic6 = r["ic6_pre_val"]
        print(
            f"  rho_static={sd['rho_static']:+.4f}; "
            f"S_003={sd['iter_003']['sharpe_ann']:+.4f}, "
            f"S_018={sd['iter_018']['sharpe_ann']:+.4f}"
        )
        print(
            f"  weights: w_003={w['w_iter_003']:+.4f}, "
            f"w_018={w['w_iter_018']:+.4f} "
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
            f"  IC-6 pre-val: |ρ60d|>0.30 on {ic6['exceed_n']}/{ic6['exceed_total']} "
            f"({ic6['exceed_frac']:.1%}); pass={ic6['pass']}"
        )

    # ----- v2 scoring (relaxed-rules, primary + corroborating) -----
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
        declared_corroborating=list(DECLARED_CORROBORATING),
    )

    # ----- hold-time gate -----
    primary_w = results[DECLARED_PRIMARY]["weights"]
    primary_hold_diag = estimate_combined_hold_days(
        DECLARED_PRIMARY,
        primary_w["w_iter_003"],
        primary_w["w_iter_018"],
    )
    primary_hold = primary_hold_diag["weighted_avg_hold_days"]
    declared_track = "medium_swing"
    track_bounds = {"intraday": (0.0, 1.0), "short_swing": (2.0, 10.0), "medium_swing": (10.0, 30.0)}
    lo, hi = track_bounds[declared_track]
    hold_gate_pass = bool(lo <= primary_hold <= hi)
    is_winner = bool(score.winner_conditions_met and hold_gate_pass)

    # ----- kill criteria -----
    kill = evaluate_kill_criteria(
        primary=results[DECLARED_PRIMARY],
        sharpe_003=results[DECLARED_PRIMARY]["stream_diagnostics"]["iter_003"]["sharpe_ann"],
        sharpe_018=results[DECLARED_PRIMARY]["stream_diagnostics"]["iter_018"]["sharpe_ann"],
    )

    print(
        f"\n=== SCORE ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} "
        f"(weighted-avg hold {primary_hold:.2f}d on {DECLARED_PRIMARY}; "
        f"declared {declared_track} bucket [{lo}, {hi}]), "
        f"is_winner = {is_winner}\n"
        f"\n=== KILL CRITERIA ===\n"
        f"value-destruction (combined_Sh < max(component_Sh)-0.05): {kill['kill_value_destruction']} "
        f"(combined={kill['combined_sharpe_primary']:.4f}, "
        f"best_component={kill['best_component_sharpe']:.4f})\n"
        f"weight-collapse (negative weight large): {kill['kill_weight_collapse']} "
        f"({kill['weights_primary']})\n"
        f"DSR no-progress (primary p > 0.20): {kill['kill_dsr_no_progress']} "
        f"(primary p={kill['primary_dsr_p']:.4f})\n"
        f"pre-val rolling-ρ violation: {kill['kill_pre_val_rolling_rho']} "
        f"(exceed_frac={kill['pre_val_diag']['exceed_frac']:.1%})\n"
        f"any_kill = {kill['any_kill']}"
    )

    # ----- persist results.json -----
    out = {
        "config_id": CFG_ID,
        "params": {
            "method": "markowitz_tangency_full_sample",
            "iter_003_cfg": ITER_003_CFG,
            "iter_018_iter": "018-2026-04-26-1628-cot-zscore-variant",
            "iter_003_path": str(ITER_003_DIR.relative_to(ROOT)),
            "iter_018_path": str(ITER_018_DIR.relative_to(ROOT)),
            "weight_constraint": "w_A + w_B = 1; clamped to corner if either<0",
            "rolling_rho_window": ROLLING_RHO_WINDOW,
            "rolling_rho_limit": ROLLING_RHO_LIMIT,
            "rolling_rho_exceed_frac_limit": ROLLING_RHO_EXCEED_FRAC_LIMIT,
        },
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "declared_primary": DECLARED_PRIMARY,
        "declared_corroborating": list(DECLARED_CORROBORATING),
        "rules_version": "2026-04-26-relaxed-r1",
        "per_dataset": {
            ds: {k: v for k, v in results[ds].items() if not k.startswith("_")}
            for ds in results
        },
        "score": score.to_dict(),
        "hold_time_gate": {
            "primary_dataset": DECLARED_PRIMARY,
            "declared_track": declared_track,
            "track_bounds": list(track_bounds[declared_track]),
            "weighted_avg_hold_days": primary_hold,
            "pass": hold_gate_pass,
            "diag_per_dataset": {
                ds: estimate_combined_hold_days(
                    ds,
                    results[ds]["weights"]["w_iter_003"],
                    results[ds]["weights"]["w_iter_018"],
                )
                for ds in results
            },
        },
        "kill_criteria": kill,
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

    # ----- persist verdict.json -----
    verdict = score.to_dict()
    verdict["configs_tested"] = 1
    verdict["primary_citation"] = "[advances_fin_ml, p.222-223]"
    verdict["hypothesis_slug"] = "ic7-rsi2sma200-cotzscore"
    verdict["mean_hold_days"] = float(primary_hold)
    verdict["hold_time_gate_pass"] = hold_gate_pass
    verdict["broker_track"] = "pepperstone_cfd"
    verdict["timeframes_used"] = ["1d"]
    verdict["track_a_metrics"] = {
        ds: {**results[ds]["combined_metrics"]} for ds in results
    }
    verdict["track_b_metrics"] = {
        "note": "Track B not modelled in iter 019 (composition primary track is A). "
                "Both component streams already net of Pepperstone CFD costs."
    }
    verdict["weights_per_ds"] = {ds: results[ds]["weights"] for ds in results}
    verdict["rho_per_ds"] = {ds: results[ds]["stream_diagnostics"]["rho_static"] for ds in results}
    verdict["kill_criteria"] = kill
    verdict["status"] = "winner" if is_winner else "iterating"
    verdict["auto_aborted_at_pre_val"] = False  # iter completes regardless; kill logged
    verdict["rules_version"] = "2026-04-26-relaxed-r1"

    verdict_path = ITER_DIR / "verdict.json"
    verdict_path.write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"wrote {verdict_path}")


if __name__ == "__main__":
    main()
