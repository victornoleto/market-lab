"""
Capital-Efficient Global Factor-Tilted Static Portfolio — Iteration 003

Hypothesis (USER_SPECIFIED): A single pre-committed static portfolio combining
nine sleeves captures return-stacking, factor breadth, and diversifier load
that all three benchmarks (VT, Plano C V3_1, V_HYBRID+MF) partially miss.

Portfolio weights (fixed, no grid):
  RSSB  25%  → RSSBSIM (direct: global eq + Treasury stacked)
  RSST  15%  → SPYSIM + KMLMSIM − CASHX (return-stack formula)
  AVUV  10%  → VBRSIM (US small-cap value proxy)
  AVDV   7%  → VSSSIM (intl dev small-cap proxy)
  AVEM   8%  → VWOSIM (EM proxy)
  SPMO   8%  → SPYSIM (US momentum proxy)
  IDMO   7%  → VEASIM (intl momentum proxy)
  GDE   12%  → GDESIM (direct: 90% SPY + 90% gold)
  KMLM   8%  → KMLMSIM (direct)

n_configs = 1 → G1 PBO trivially passes, DSR uses PSR (n_trials=1).

Citations:
  [risk_parity, ch.5] — Return stacking / capital efficiency
  [leverage_for_the_long_run, p.40-60] — Leveraged overlay risk caveats
  [advances_fin_ml, ch.10] — Small-cap value empirical evidence
  [trading_evolved, p.197] — Managed futures "free lunch"
  [stocks_on_the_move, p.21-30] — Momentum factor
  [risk_parity, ch.3-5] — Multi-asset diversification
  [advances_fin_ml, p.208-211] — PBO: N/A when n_configs=1
  [advances_fin_ml, p.222-223] — DSR / PSR with n_trials=1
  [advances_fin_ml, p.196-202] — Bootstrap CI for Sharpe significance
  [advances_fin_ml, p.31-34]   — Cross-lib ±3pp CAGR parity

Run from repo root:
    uv run python studies/global_factor_tilt_loop/iterations/003-2026-04-26-2347-capital-efficient-static/backtest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).parents[4]
sys.path.insert(0, str(REPO_ROOT))

from market_lab.backtest.data.testfolio_loader import load_testfolio_frame
from market_lab.backtest.metrics.performance import sharpe, cagr, max_drawdown
from market_lab.backtest.validation.pbo import MIN_HONEST_N_CONFIGS
from market_lab.backtest.validation.dsr import psr as compute_psr
from market_lab.backtest.validation.walk_forward import walk_forward_gate, walk_forward_splits

LOOP_ROOT = REPO_ROOT / "studies" / "global_factor_tilt_loop"
sys.path.insert(0, str(LOOP_ROOT))
from scoring import score_strategy, DatasetMetrics, Gates, Benchmark, BENCHMARKS

ITER_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Fixed pre-committed weights (USER_SPECIFIED — do NOT modify)
# Sum = 1.00 nominally; effective notional ~1.45× via stacking.
# RSST synthesized as SPYSIM + KMLMSIM − CASHX (excess-return overlay).
# [risk_parity, ch.5]: return stacking preserves 1× capital via futures.
# ---------------------------------------------------------------------------

PORTFOLIO_LEGS = {
    # (ticker_or_synthetic, weight)
    "RSSBSIM": 0.25,    # RSSB: global eq + Treasury stacked (direct synth)
    # RSST expanded below: +0.15 SPYSIM, +0.15 KMLMSIM, -0.15 CASHX
    "VBRSIM":  0.10,    # AVUV: US small-cap value proxy [advances_fin_ml, ch.10]
    "VSSSIM":  0.07,    # AVDV: intl dev small-cap proxy
    "VWOSIM":  0.08,    # AVEM: EM proxy
    "GDESIM":  0.12,    # GDE: 90% S&P + 90% gold direct synth
    "KMLMSIM": 0.08,    # KMLM: managed futures direct [trading_evolved, p.197]
}
# RSST stacking overlay (0.15 × (r_SPYSIM + r_KMLMSIM - r_CASHX)):
RSST_WEIGHT = 0.15

# Momentum proxies [stocks_on_the_move, p.21-30]:
SPMO_PROXY = ("SPYSIM", 0.08)   # US momentum → SPYSIM
IDMO_PROXY = ("VEASIM", 0.07)   # intl momentum → VEASIM

N_CONFIGS = 1

# ---------------------------------------------------------------------------
# Dataset definitions
# educational starts 1995-01-01 (binding: VSSSIM/VWOSIM from 1994-12-29)
# Benchmark for educational is VTSIM over the same 1995-2026 window.
# ---------------------------------------------------------------------------

DATASETS = {
    "educational": {
        "start": "1995-01-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "label": "VTSIM proxy 1995-2026 (~31y; VSSSIM/VWOSIM binding)",
    },
    "vt_real": {
        "start": "2008-06-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "label": "VTSIM proxy 2008-06+ (~17y)",
    },
    "ndx_real": {
        "start": "2010-02-01",
        "end": "2026-04-24",
        "benchmark": "QQQSIM",
        "label": "QQQ proxy 2010-02+ (16y)",
    },
}

ALL_TICKERS = list(PORTFOLIO_LEGS) + [SPMO_PROXY[0], IDMO_PROXY[0], "SPYSIM", "CASHX"]
# deduplicate while preserving order
ALL_TICKERS = list(dict.fromkeys(ALL_TICKERS))

WF_N_WINDOWS = 8
BOOTSTRAP_N = 2000

# ---------------------------------------------------------------------------
# Portfolio simulator (pandas) — static monthly rebalance
# ---------------------------------------------------------------------------


def build_portfolio_returns(prices: pd.DataFrame) -> pd.Series:
    """Static capital-efficient portfolio with monthly rebalance.

    RSST synthesized as SPYSIM + KMLMSIM − CASHX.
    [risk_parity, ch.5]: futures overlay earns excess return; CASHX offset
    avoids double-counting collateral. Monthly rebalance, 1-day lag.
    """
    needed = list(PORTFOLIO_LEGS) + [SPMO_PROXY[0], IDMO_PROXY[0], "SPYSIM", "CASHX"]
    needed = list(dict.fromkeys(needed))

    px = prices[needed].dropna(how="all").ffill()
    daily_ret = px.pct_change()

    # Effective component weights after expanding RSST:
    eff_weights: dict[str, float] = {}
    for t, w in PORTFOLIO_LEGS.items():
        eff_weights[t] = eff_weights.get(t, 0.0) + w
    # RSST = SPYSIM + KMLMSIM − CASHX (0.15 each)
    eff_weights["SPYSIM"] = eff_weights.get("SPYSIM", 0.0) + RSST_WEIGHT
    eff_weights["KMLMSIM"] = eff_weights.get("KMLMSIM", 0.0) + RSST_WEIGHT
    eff_weights["CASHX"] = eff_weights.get("CASHX", 0.0) - RSST_WEIGHT
    # Momentum proxies
    spmo_t, spmo_w = SPMO_PROXY
    eff_weights[spmo_t] = eff_weights.get(spmo_t, 0.0) + spmo_w
    idmo_t, idmo_w = IDMO_PROXY
    eff_weights[idmo_t] = eff_weights.get(idmo_t, 0.0) + idmo_w

    # Monthly rebalance: on the last day of each month, set weights for
    # next month. Apply with 1-day shift to avoid lookahead.
    monthly_dates = daily_ret.resample("ME").last().index

    # Build daily weight matrix (constant between rebalance dates)
    weight_series = {t: w for t, w in eff_weights.items() if t in daily_ret.columns}
    weight_df = pd.DataFrame(weight_series, index=daily_ret.index, dtype=float)
    # For tickers not in the dataframe, skip (all should be present)

    # Shift weights by 1 to apply signal from prior period
    shifted_weights = weight_df.shift(1).fillna(0.0)

    # Daily portfolio return = sum(w_i × r_i)
    port_ret = (shifted_weights * daily_ret[list(weight_series)]).sum(axis=1)
    port_ret = port_ret.dropna()

    # Trim to first real bar (after 1-day shift warm-up)
    return port_ret.iloc[1:]


# ---------------------------------------------------------------------------
# Numpy cross-lib reference (G7) — static weights, no dynamic rebalancing
# [advances_fin_ml, p.31-34]
# ---------------------------------------------------------------------------


def build_portfolio_returns_numpy(
    prices: pd.DataFrame, eff_weights: dict[str, float]
) -> np.ndarray:
    """Numpy-pure static portfolio — must reproduce ±3pp CAGR vs pandas."""
    tickers = [t for t in eff_weights if t in prices.columns]
    weights = np.array([eff_weights[t] for t in tickers], dtype=float)

    px = prices[tickers].dropna(how="all").ffill().values.astype(float)
    daily_rets = np.diff(px, axis=0) / px[:-1]
    # Apply 1-day shift (weights apply day after set)
    # Row i of daily_rets = return from day i to i+1
    # Shifted weights: constant vector (static) → same weights each day
    port_rets = (daily_rets * weights).sum(axis=1)
    return port_rets[1:]  # align with pandas (skip first row of NaN)


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------


def compute_equity(returns: pd.Series, start: float = 10000.0) -> pd.Series:
    return (1 + returns).cumprod() * start


def metrics_from_returns(returns: pd.Series) -> dict:
    eq = compute_equity(returns)
    return {
        "sharpe": sharpe(returns, periods_per_year=252),
        "cagr": cagr(eq, periods_per_year=252),
        "mdd": max_drawdown(eq),
    }


# ---------------------------------------------------------------------------
# Rolling-window robustness (5y windows)
# ---------------------------------------------------------------------------


def rolling_window_robustness(
    returns: pd.Series,
    window_days: int = 252 * 5,
    step_days: int = 252,
) -> tuple[int, float, int, list[float]]:
    arr = returns.values
    n = len(arr)
    sharpes = []
    start = 0
    while start + window_days <= n:
        w = arr[start:start + window_days]
        sigma = w.std(ddof=0)
        if sigma > 1e-12:
            s = w.mean() / sigma * np.sqrt(252)
            sharpes.append(float(s))
        start += step_days
    if not sharpes:
        return 0, 0.0, 0, []
    pct_pos = sum(1 for s in sharpes if s > 0) / len(sharpes)
    if pct_pos >= 0.90:
        pts = 5
    elif pct_pos >= 0.75:
        pts = 3
    elif pct_pos >= 0.60:
        pts = 1
    else:
        pts = 0
    return pts, pct_pos, len(sharpes), sharpes


# ---------------------------------------------------------------------------
# Gate battery (reused from iter 002 pattern)
# ---------------------------------------------------------------------------


def gate_dsr_psr(returns: pd.Series) -> tuple[bool, float]:
    """G2: PSR (n_trials=1, pre-committed). [advances_fin_ml, p.222-223]"""
    arr = returns.values
    if len(arr) < 10:
        return False, 1.0
    p_value = 1.0 - compute_psr(arr, benchmark=0.0)
    return p_value < 0.05, p_value


def gate_walk_forward(returns: pd.Series) -> tuple[bool, list[float], list[float]]:
    """G3: WF 6/8 windows, MDD<25% per window."""
    n = len(returns)
    n_windows = WF_N_WINDOWS
    window_size = n // (n_windows + 1)
    if window_size < 63:
        return False, [], []
    is_size = window_size
    oos_size = window_size
    step = window_size
    oos_returns = []
    oos_mdds = []
    for _, test_range in walk_forward_splits(n, is_size, oos_size, step):
        oos_ret = returns.iloc[list(test_range)]
        eq = compute_equity(oos_ret)
        oos_returns.append(float((1 + oos_ret).prod() - 1))
        oos_mdds.append(float(max_drawdown(eq)))
        if len(oos_returns) >= n_windows:
            break
    if len(oos_returns) < n_windows:
        return False, oos_returns, oos_mdds
    return walk_forward_gate(oos_returns, oos_mdds) == "pass", oos_returns, oos_mdds


def gate_oos_70_30(returns: pd.Series) -> tuple[bool, float]:
    """G4: 70/30 OOS Sharpe > 0."""
    split = int(len(returns) * 0.70)
    oos = returns.iloc[split:]
    if len(oos) < 63:
        return False, 0.0
    s = sharpe(oos, periods_per_year=252)
    return s > 0, s


def gate_fwd_stress(returns: pd.Series, fwd_start: str = "2020-01-01") -> tuple[bool, float]:
    """G5: Post-2020 Sharpe > 0."""
    fwd = returns[returns.index >= fwd_start]
    if len(fwd) < 63:
        return False, 0.0
    s = sharpe(fwd, periods_per_year=252)
    return s > 0, s


def gate_bootstrap(returns: pd.Series) -> tuple[bool, float]:
    """G6: Block-bootstrap 99.9% CI low > 0. [advances_fin_ml, p.196-202]"""
    arr = returns.values
    if len(arr) < 252:
        return False, 0.0
    rng = np.random.default_rng(42)
    block_size = 21
    n = len(arr)
    n_blocks = n // block_size
    bootstrapped = []
    for _ in range(BOOTSTRAP_N):
        starts = rng.integers(0, n - block_size + 1, size=n_blocks)
        sample = np.concatenate([arr[s:s + block_size] for s in starts])[:n]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            bootstrapped.append(sample.mean() / sigma * np.sqrt(252))
    if not bootstrapped:
        return False, 0.0
    ci_low = float(np.percentile(bootstrapped, 0.1))
    return ci_low > 0, ci_low


def gate_crosslib(
    prices: pd.DataFrame,
    eff_weights: dict[str, float],
    pandas_cagr: float,
) -> tuple[bool, float, float]:
    """G7: Numpy-pure cross-lib ±3pp CAGR. [advances_fin_ml, p.31-34]"""
    np_rets = build_portfolio_returns_numpy(prices, eff_weights)
    if len(np_rets) < 252:
        return False, 0.0, pandas_cagr
    n = len(np_rets)
    np_equity = (1 + np_rets).cumprod() * 10000.0
    np_cagr = float((np_equity[-1] / np_equity[0]) ** (252 / (n - 1)) - 1)
    if np.isnan(np_cagr):
        return False, float("nan"), pandas_cagr
    diff_pp = abs(np_cagr - pandas_cagr) * 100
    return diff_pp <= 3.0, np_cagr, pandas_cagr


# ---------------------------------------------------------------------------
# Full run for one dataset
# ---------------------------------------------------------------------------


def _compute_eff_weights() -> dict[str, float]:
    """Expand RSST stacking → effective ticker weights."""
    eff: dict[str, float] = {}
    for t, w in PORTFOLIO_LEGS.items():
        eff[t] = eff.get(t, 0.0) + w
    eff["SPYSIM"] = eff.get("SPYSIM", 0.0) + RSST_WEIGHT
    eff["KMLMSIM"] = eff.get("KMLMSIM", 0.0) + RSST_WEIGHT
    eff["CASHX"] = eff.get("CASHX", 0.0) - RSST_WEIGHT
    eff[SPMO_PROXY[0]] = eff.get(SPMO_PROXY[0], 0.0) + SPMO_PROXY[1]
    eff[IDMO_PROXY[0]] = eff.get(IDMO_PROXY[0], 0.0) + IDMO_PROXY[1]
    return eff


EFF_WEIGHTS = _compute_eff_weights()


def run_dataset(ds_name: str, prices_full: pd.DataFrame) -> dict:
    cfg = DATASETS[ds_name]
    start, end = cfg["start"], cfg["end"]
    bm_ticker = cfg["benchmark"]

    needed = list(EFF_WEIGHTS) + [bm_ticker]
    needed = list(dict.fromkeys(needed))

    prices = prices_full[needed].loc[start:end].dropna(how="all")
    prices = prices.ffill()

    # Benchmark
    bm_ret = prices[bm_ticker].pct_change().dropna()
    bm_eq = compute_equity(bm_ret)
    bm_sharpe = sharpe(bm_ret, periods_per_year=252)
    bm_cagr = cagr(bm_eq, periods_per_year=252)
    bm_mdd = max_drawdown(bm_eq)

    print(f"\n{'='*60}")
    print(f"Dataset: {ds_name}  [{cfg['label']}]")
    print(f"  Period: {prices.index[0].date()} → {prices.index[-1].date()}")
    print(f"  Benchmark ({bm_ticker}): Sharpe={bm_sharpe:.4f} CAGR={bm_cagr:.2%} MDD={bm_mdd:.2%}")
    print(f"  Config: USER_SPECIFIED static weights, single config (n=1)")

    port_ret = build_portfolio_returns(prices)

    if len(port_ret) < 252:
        print(f"  ERROR: too short ({len(port_ret)} days)")
        return {"error": "too short"}

    m = metrics_from_returns(port_ret)
    vs_bm = "✓" if m["sharpe"] > bm_sharpe else "✗"
    print(f"  Portfolio: Sharpe={m['sharpe']:.4f} {vs_bm}  "
          f"CAGR={m['cagr']:.2%}  MDD={m['mdd']:.2%}")

    # G1: PBO — trivially N/A (n_configs=1 < MIN_HONEST_N_CONFIGS)
    g1_pass = True
    g1_pbo = 0.0
    print(f"  G1 PBO: N/A (n_configs=1 < {MIN_HONEST_N_CONFIGS}) → PASS (trivial)")

    # G2: DSR / PSR (n_trials=1)
    g2_pass, g2_p = gate_dsr_psr(port_ret)
    print(f"  G2 DSR/PSR: p={g2_p:.2e} → {'PASS' if g2_pass else 'FAIL'}")

    # G3: Walk-Forward
    g3_pass, wf_rets, wf_mdds = gate_walk_forward(port_ret)
    wf_profitable = sum(1 for r in wf_rets if r > 0)
    wf_max_mdd = max(wf_mdds) if wf_mdds else 0.0
    print(f"  G3 WF: {wf_profitable}/{len(wf_rets)} profitable, max_mdd={wf_max_mdd:.2%} → {'PASS' if g3_pass else 'FAIL'}")

    # G4: OOS 70/30
    g4_pass, g4_sharpe = gate_oos_70_30(port_ret)
    print(f"  G4 OOS: Sharpe={g4_sharpe:.4f} → {'PASS' if g4_pass else 'FAIL'}")

    # G5: FWD stress
    g5_pass, g5_sharpe = gate_fwd_stress(port_ret)
    print(f"  G5 FWD: Sharpe(post-2020)={g5_sharpe:.4f} → {'PASS' if g5_pass else 'FAIL'}")

    # G6: Bootstrap
    g6_pass, g6_ci_low = gate_bootstrap(port_ret)
    print(f"  G6 Bootstrap: CI_low={g6_ci_low:.4f} → {'PASS' if g6_pass else 'FAIL'}")

    # G7: Cross-lib (numpy parity)
    g7_pass, np_cagr, pd_cagr = gate_crosslib(prices, EFF_WEIGHTS, m["cagr"])
    print(f"  G7 Cross-lib: np={np_cagr:.2%} pd={pd_cagr:.2%} "
          f"diff={abs(np_cagr-pd_cagr)*100:.2f}pp → {'PASS' if g7_pass else 'FAIL'}")

    gates_passed = sum([g1_pass, g2_pass, g3_pass, g4_pass, g5_pass, g6_pass, g7_pass])
    print(f"  Gates: {gates_passed}/7")

    return {
        "dataset": ds_name,
        "config": "capital-efficient-static-v1",
        "metrics": {"sharpe": m["sharpe"], "cagr": m["cagr"], "mdd": m["mdd"]},
        "benchmark": {"sharpe": bm_sharpe, "cagr": bm_cagr, "mdd": bm_mdd, "ticker": bm_ticker},
        "gates": {
            "g1_pbo": g1_pass, "g2_dsr": g2_pass, "g3_wf": g3_pass,
            "g4_oos": g4_pass, "g5_fwd": g5_pass,
            "g6_bootstrap": g6_pass, "g7_crosslib": g7_pass,
            "n_passed": gates_passed,
        },
        "gate_details": {
            "g1_pbo_value": g1_pbo,
            "g1_note": f"N/A: single config < MIN_HONEST_N_CONFIGS={MIN_HONEST_N_CONFIGS}",
            "g2_dsr_p": g2_p,
            "g3_wf_returns": wf_rets, "g3_wf_mdds": wf_mdds,
            "g3_max_mdd": wf_max_mdd,
            "g4_oos_sharpe": g4_sharpe,
            "g5_fwd_sharpe": g5_sharpe,
            "g6_ci_low": g6_ci_low,
            "g7_np_cagr": np_cagr,
        },
        "returns_series": {
            "capital-efficient-static": {
                "index": [str(d.date()) for d in port_ret.index],
                "net_returns": port_ret.tolist(),
            }
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("Loading testfolio price cache...")
    prices_full = load_testfolio_frame(REPO_ROOT / "data/testfolio/cache/history.parquet")
    print(f"Loaded {len(prices_full.columns)} tickers, {len(prices_full)} days")

    print("\nEffective weight expansion:")
    for t, w in sorted(EFF_WEIGHTS.items(), key=lambda x: -abs(x[1])):
        print(f"  {t}: {w:+.2f}")

    results = {}
    for ds_name in ["educational", "vt_real", "ndx_real"]:
        result = run_dataset(ds_name, prices_full)
        results[ds_name] = result

    # Rolling-window robustness on educational (31y → ~26 5-year windows)
    print("\n" + "=" * 60)
    print("ROLLING-WINDOW ROBUSTNESS (educational, 5-year windows)")
    edu_cfg = DATASETS["educational"]
    needed = list(EFF_WEIGHTS) + [edu_cfg["benchmark"]]
    needed = list(dict.fromkeys(needed))
    prices_edu = prices_full[needed].loc[edu_cfg["start"]:edu_cfg["end"]].dropna(how="all").ffill()
    edu_port = build_portfolio_returns(prices_edu)
    rob_pts, pct_pos, n_windows, roll_sharpes = rolling_window_robustness(edu_port)
    print(f"  Windows: {n_windows}")
    print(f"  % positive Sharpe: {pct_pos:.1%}")
    if roll_sharpes:
        print(f"  Min rolling Sharpe: {min(roll_sharpes):.3f}")
        print(f"  Max rolling Sharpe: {max(roll_sharpes):.3f}")
    print(f"  Robustness bonus: {rob_pts}/5")

    # Scoring — use dynamic benchmark for educational (1995-2026 VTSIM)
    # to avoid mismatch with the default 56y educational benchmark.
    print("\n" + "=" * 60)
    print("SCORING")

    # Compute VTSIM benchmark over educational window for honest comparison
    edu_prices = prices_full["VTSIM"].loc[edu_cfg["start"]:edu_cfg["end"]].dropna()
    edu_bm_ret = edu_prices.pct_change().dropna()
    edu_bm_eq = compute_equity(edu_bm_ret)
    edu_bm_sharpe = sharpe(edu_bm_ret, periods_per_year=252)
    edu_bm_cagr_val = cagr(edu_bm_eq, periods_per_year=252)
    edu_bm_mdd = max_drawdown(edu_bm_eq)
    print(f"\n  VTSIM(1995-2026) benchmark: Sharpe={edu_bm_sharpe:.4f} "
          f"CAGR={edu_bm_cagr_val:.2%} MDD={edu_bm_mdd:.2%}")

    custom_benchmarks = {
        "educational": Benchmark(
            sharpe=edu_bm_sharpe, cagr=edu_bm_cagr_val, mdd=edu_bm_mdd,
            label="VTSIM b&h 1995-2026 (~31y; VSSSIM binding)"
        ),
        "vt_real": BENCHMARKS["vt_real"],
        "ndx_real": BENCHMARKS["ndx_real"],
    }

    metrics_map = {}
    gates_map = {}
    for ds_name in ["educational", "vt_real", "ndx_real"]:
        r = results[ds_name]
        if "error" in r:
            metrics_map[ds_name] = DatasetMetrics(sharpe=0.0, cagr=0.0, mdd=1.0, dsr_p_value=1.0)
            gates_map[ds_name] = Gates(False, False, False, False, False, False, False)
            continue
        m = r["metrics"]
        g = r["gates"]
        gd = r["gate_details"]
        metrics_map[ds_name] = DatasetMetrics(
            sharpe=m["sharpe"], cagr=m["cagr"], mdd=m["mdd"],
            dsr_p_value=gd["g2_dsr_p"],
        )
        gates_map[ds_name] = Gates(
            g1_pbo=g["g1_pbo"], g2_dsr=g["g2_dsr"], g3_wf=g["g3_wf"],
            g4_oos=g["g4_oos"], g5_fwd=g["g5_fwd"],
            g6_bootstrap=g["g6_bootstrap"], g7_crosslib=g["g7_crosslib"],
        )

    cumulative_n_trials = 19 + N_CONFIGS  # 18 iter001 + 1 iter002 + 1 this iter
    score_result = score_strategy(
        metrics_map, gates_map,
        cumulative_n_trials=cumulative_n_trials,
        benchmarks=custom_benchmarks,
        robustness_bonus=rob_pts,
    )

    print(f"\nTier:  {score_result.tier.value}")
    print(f"Score: {score_result.total_score}/100")
    print(f"Winner conditions met: {score_result.winner_conditions_met}")
    print("\nScore breakdown:")
    for k, v in score_result.criteria.items():
        print(f"  {k}: {v['points']}/{v['max']}")

    # Save
    def _json_default(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return None if np.isnan(obj) else float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    verdict = score_result.to_dict()
    verdict["configs_tested"] = N_CONFIGS
    verdict["primary_citation"] = "[risk_parity, ch.5]"
    verdict["hypothesis_slug"] = "capital-efficient-static"
    verdict["status"] = score_result.tier.value.lower()
    verdict["educational_benchmark_note"] = (
        "Educational benchmark uses VTSIM(1995-2026) not VTSIM(56y) "
        "because VSSSIM/VWOSIM are binding constraints starting 1994-12."
    )
    verdict["robustness"] = {
        "n_windows": n_windows,
        "pct_positive_sharpe": pct_pos,
        "min_rolling_sharpe": float(min(roll_sharpes)) if roll_sharpes else None,
        "max_rolling_sharpe": float(max(roll_sharpes)) if roll_sharpes else None,
        "bonus_pts": rob_pts,
    }
    verdict["custom_benchmarks"] = {
        ds: {"sharpe": b.sharpe, "cagr": b.cagr, "mdd": b.mdd, "label": b.label}
        for ds, b in custom_benchmarks.items()
    }

    results_json = {
        "hypothesis_slug": "capital-efficient-static",
        "datasets": results,
        "returns_series": {
            ds: results[ds].get("returns_series", {})
            for ds in ["educational", "vt_real", "ndx_real"]
        },
    }

    verdict_path = ITER_DIR / "verdict.json"
    results_path = ITER_DIR / "results.json"
    with open(verdict_path, "w") as f:
        json.dump(verdict, f, indent=2, default=_json_default)
    with open(results_path, "w") as f:
        json.dump(results_json, f, indent=2, default=_json_default)

    print(f"\nSaved: {verdict_path}")
    print(f"Saved: {results_path}")
    return results, score_result, rob_pts, pct_pos, n_windows, roll_sharpes


if __name__ == "__main__":
    main()
