"""
HAA SmartStack + 5% Gold Sleeve (iter 009)

Mechanism: Iter 005 HAA SmartStack (WINNER, Sharpe 1.112) with an added 5% fixed
GLDSIM sleeve to test whether persistent gold exposure closes the 0.07 Sharpe gap
to bestfolio reference (1.18).

Allocation:
  85% HAA dynamic (canary VWOSIM → top-2 offensive / top-1 defensive)
  10% KMLMSIM fixed (managed futures free-lunch)
   5% GLDSIM fixed (gold inflation hedge, low-correlation diversifier)

Offensive universe:
  NTSXSIM  = 0.90 * SPYSIM + 0.60 * IEFSIM - 0.50 * CASHX
  NTSI     = 0.90 * VEASIM + 0.60 * IEFSIM - 0.50 * CASHX
  NTSE     = 0.90 * VWOSIM + 0.60 * IEFSIM - 0.50 * CASHX
  GDESIM   = cached (90% S&P + 90% gold)

Defensive: IEFSIM, BNDSIM, CASHX

Kill 1: edu Sharpe ≤ 1.112 (must beat iter 005 WINNER)
Kill 2: any WF G3' window fails

Citations:
  [stocks_on_the_move, ch.6]              HAA momentum mechanics
  [ilmanen_expected_returns, ch.19]       MF free-lunch sleeve
  [ilmanen_expected_returns, ch.fx-carry] gold as inflation hedge
  [leverage_for_the_long_run, p.40-60]    stacking justification
  [advances_fin_ml, p.208-211]            G1 PBO
  [advances_fin_ml, p.222-223]            G2 DSR
  [advances_fin_ml, p.196-202]            G6 Bootstrap
  [advances_fin_ml, p.31-34]              G7 cross-lib

Run from repo root:
    uv run python studies/global_factor_tilt_loop/iterations/009-2026-04-27-0921-haa-gold-sleeve/backtest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).parents[4]
sys.path.insert(0, str(REPO_ROOT))

from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_frame
from src.ai_trade.backtest.metrics.performance import sharpe, cagr, max_drawdown
from src.ai_trade.backtest.validation.pbo import MIN_HONEST_N_CONFIGS
from src.ai_trade.backtest.validation.dsr import dsr as compute_dsr, psr as compute_psr
from src.ai_trade.backtest.validation.walk_forward import walk_forward_splits

LOOP_ROOT = REPO_ROOT / "studies" / "global_factor_tilt_loop"
sys.path.insert(0, str(LOOP_ROOT))
from scoring import score_strategy, DatasetMetrics, Gates

ITER_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Pre-committed parameters (single config, no grid)
# Change from iter 005: DYNAMIC_WEIGHT 0.90→0.85, GLD_WEIGHT=0.05
# [stocks_on_the_move, ch.6]: HAA momentum = unweighted avg 1/3/6/12m
# ---------------------------------------------------------------------------
N_CONFIGS = 1
KMLM_WEIGHT = 0.10       # fixed MF sleeve [ilmanen_expected_returns, ch.19]
GLD_WEIGHT = 0.05        # fixed gold sleeve [ilmanen_expected_returns, ch.fx-carry]
DYNAMIC_WEIGHT = 0.85    # HAA dynamic (was 0.90 in iter 005)
TOP_K_OFFENSIVE = 2      # top-2 when risk-ON, equal-weight
NOTIONAL_FACTOR = 1.45   # same as iter 005 (stacked offensive assets)
WF_N_WINDOWS = 8
BOOTSTRAP_N = 2000

# Stacking formula weights [leverage_for_the_long_run, p.40-60]
STACK_EQ = 0.90
STACK_BD = 0.60
STACK_CASH = 0.50

RAW_TICKERS = ["SPYSIM", "VEASIM", "VWOSIM", "IEFSIM", "CASHX",
               "KMLMSIM", "GLDSIM", "GDESIM", "BNDSIM", "VTSIM", "QQQSIM"]

DATASETS = {
    "educational": {
        "start": "1994-05-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "label": "VTSIM b&h ~31y (VWOSIM canary binding 1995-2026)",
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


# ---------------------------------------------------------------------------
# Build stacked synthetic price series (same as iter 005)
# [leverage_for_the_long_run, p.40-60]
# ---------------------------------------------------------------------------

def build_stacked_prices(prices: pd.DataFrame) -> pd.DataFrame:
    ret = prices.pct_change()
    ntsxsim_ret = STACK_EQ * ret["SPYSIM"] + STACK_BD * ret["IEFSIM"] - STACK_CASH * ret["CASHX"]
    ntsi_ret = STACK_EQ * ret["VEASIM"] + STACK_BD * ret["IEFSIM"] - STACK_CASH * ret["CASHX"]
    ntse_ret = STACK_EQ * ret["VWOSIM"] + STACK_BD * ret["IEFSIM"] - STACK_CASH * ret["CASHX"]

    out = prices.copy()
    for label, ret_series in [("NTSXSIM", ntsxsim_ret), ("NTSI", ntsi_ret), ("NTSE", ntse_ret)]:
        clean = ret_series.dropna()
        if clean.empty:
            continue
        out[label] = (1 + clean).cumprod() * 100.0

    return out


# ---------------------------------------------------------------------------
# HAA momentum: unweighted avg of 1m/3m/6m/12m returns
# [stocks_on_the_move, ch.6]
# ---------------------------------------------------------------------------

def haa_momentum(monthly_prices: pd.DataFrame, assets: list[str]) -> pd.DataFrame:
    scores = pd.DataFrame(index=monthly_prices.index, columns=assets, dtype=float)
    for a in assets:
        p = monthly_prices[a]
        r1 = p / p.shift(1) - 1
        r3 = p / p.shift(3) - 1
        r6 = p / p.shift(6) - 1
        r12 = p / p.shift(12) - 1
        scores[a] = (r1 + r3 + r6 + r12) / 4.0
    return scores


# ---------------------------------------------------------------------------
# HAA SmartStack + Gold Sleeve — pandas simulation
# ---------------------------------------------------------------------------

def simulate_haa_gold(prices: pd.DataFrame) -> pd.Series:
    """Monthly HAA with 85% dynamic + 10% KMLM + 5% GLDSIM.

    Changes vs iter 005:
    - DYNAMIC_WEIGHT = 0.85 (was 0.90)
    - GLD_WEIGHT = 0.05 (new)
    """
    offensive = ["NTSXSIM", "NTSI", "NTSE", "GDESIM"]
    defensive = ["IEFSIM", "BNDSIM", "CASHX"]
    canary_asset = "VWOSIM"
    all_assets = list(dict.fromkeys(
        offensive + defensive + [canary_asset, "KMLMSIM", "GLDSIM"]
    ))

    px = prices[all_assets].dropna(how="all")
    monthly = px.resample("ME").last()

    off_mom = haa_momentum(monthly, offensive)
    def_mom = haa_momentum(monthly, defensive)
    can_mom = haa_momentum(monthly, [canary_asset])[canary_asset]

    monthly_weights = pd.DataFrame(0.0, index=monthly.index, columns=all_assets)

    for i in range(12, len(monthly)):
        date = monthly.index[i]
        # Fixed sleeves
        monthly_weights.loc[date, "KMLMSIM"] = KMLM_WEIGHT
        monthly_weights.loc[date, "GLDSIM"] = GLD_WEIGHT

        if can_mom.iloc[i] > 0:
            row = off_mom.iloc[i].dropna()
            if row.empty:
                monthly_weights.loc[date, "CASHX"] = DYNAMIC_WEIGHT
            else:
                top_assets = row.nlargest(min(TOP_K_OFFENSIVE, len(row))).index.tolist()
                w = DYNAMIC_WEIGHT / len(top_assets)
                for a in top_assets:
                    monthly_weights.loc[date, a] = w
        else:
            row = def_mom.iloc[i].dropna()
            if row.empty:
                monthly_weights.loc[date, "CASHX"] = DYNAMIC_WEIGHT
            else:
                top1 = row.idxmax()
                monthly_weights.loc[date, top1] = DYNAMIC_WEIGHT

    daily_weights = monthly_weights.reindex(px.index, method="ffill").fillna(0.0)
    daily_ret = px.pct_change()
    port_ret = (daily_weights.shift(1) * daily_ret).sum(axis=1).dropna()

    first_signal_date = monthly.index[12]
    return port_ret[port_ret.index >= first_signal_date]


# ---------------------------------------------------------------------------
# Numpy cross-lib reference (G7)
# [advances_fin_ml, p.31-34]
# ---------------------------------------------------------------------------

def simulate_haa_gold_numpy(prices: pd.DataFrame) -> np.ndarray:
    """Numpy-pure HAA+gold reference for G7 cross-lib validation."""
    offensive = ["NTSXSIM", "NTSI", "NTSE", "GDESIM"]
    defensive = ["IEFSIM", "BNDSIM", "CASHX"]
    canary = "VWOSIM"
    all_assets = list(dict.fromkeys(offensive + defensive + [canary, "KMLMSIM", "GLDSIM"]))

    px = prices[all_assets].dropna(how="all")
    px_np = px.values.astype(float)
    dates = px.index
    asset_idx = {a: i for i, a in enumerate(all_assets)}

    periods = pd.DatetimeIndex(dates).to_period("M")
    month_ends = []
    for i in range(1, len(dates)):
        if periods[i] != periods[i - 1]:
            month_ends.append(i - 1)
    if not month_ends or month_ends[-1] != len(dates) - 1:
        month_ends.append(len(dates) - 1)
    month_ends = np.array(month_ends)
    n_months = len(month_ends)

    monthly_px = px_np[month_ends]

    def _mom4(asset_col: int) -> np.ndarray:
        p = monthly_px[:, asset_col]
        scores = np.full(n_months, np.nan)
        for i in range(12, n_months):
            r1 = p[i] / p[i-1] - 1 if p[i-1] > 0 else np.nan
            r3 = p[i] / p[i-3] - 1 if p[i-3] > 0 else np.nan
            r6 = p[i] / p[i-6] - 1 if p[i-6] > 0 else np.nan
            r12 = p[i] / p[i-12] - 1 if p[i-12] > 0 else np.nan
            vals = [v for v in [r1, r3, r6, r12] if not np.isnan(v)]
            if vals:
                scores[i] = sum(vals) / len(vals)
        return scores

    off_scores = np.column_stack([_mom4(asset_idx[a]) for a in offensive])
    def_scores = np.column_stack([_mom4(asset_idx[a]) for a in defensive])
    can_scores = _mom4(asset_idx[canary])

    n_days = len(dates)
    n_total = len(all_assets)
    daily_weights = np.zeros((n_days, n_total))

    kmlm_i = asset_idx["KMLMSIM"]
    gld_i = asset_idx["GLDSIM"]
    cash_i = asset_idx["CASHX"]
    off_idx = [asset_idx[a] for a in offensive]
    def_idx = [asset_idx[a] for a in defensive]

    for mi in range(12, n_months):
        di = month_ends[mi]
        daily_weights[di, kmlm_i] = KMLM_WEIGHT
        daily_weights[di, gld_i] = GLD_WEIGHT

        if not np.isnan(can_scores[mi]) and can_scores[mi] > 0:
            row = off_scores[mi]
            valid = ~np.isnan(row)
            if valid.any():
                top_k = min(TOP_K_OFFENSIVE, valid.sum())
                sorted_idx = np.argsort(row)[::-1]
                chosen = [off_idx[j] for j in sorted_idx[:top_k] if valid[sorted_idx[j]]]
                if chosen:
                    w = DYNAMIC_WEIGHT / len(chosen)
                    for ci in chosen:
                        daily_weights[di, ci] = w
                else:
                    daily_weights[di, cash_i] = DYNAMIC_WEIGHT
            else:
                daily_weights[di, cash_i] = DYNAMIC_WEIGHT
        else:
            row = def_scores[mi]
            valid = ~np.isnan(row)
            if valid.any():
                best_local = int(np.nanargmax(row))
                daily_weights[di, def_idx[best_local]] = DYNAMIC_WEIGHT
            else:
                daily_weights[di, cash_i] = DYNAMIC_WEIGHT

    last = np.zeros(n_total)
    filled = np.zeros((n_days, n_total))
    for i in range(n_days):
        if daily_weights[i].sum() > 0:
            last = daily_weights[i].copy()
        filled[i] = last

    daily_rets = np.diff(px_np, axis=0) / np.where(px_np[:-1] > 0, px_np[:-1], np.nan)
    shifted = filled[:-1]
    port_rets = np.nansum(shifted * daily_rets, axis=1)

    first_sig = month_ends[12]
    return port_rets[first_sig:]


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------

def compute_equity(returns: pd.Series, start: float = 10000.0) -> pd.Series:
    return (1 + returns).cumprod() * start


def metrics_from_returns(returns: pd.Series) -> dict:
    eq = compute_equity(returns)
    return {
        "sharpe": float(sharpe(returns, periods_per_year=252)),
        "cagr": float(cagr(eq, periods_per_year=252)),
        "mdd": float(max_drawdown(eq)),
    }


# ---------------------------------------------------------------------------
# Rolling-window robustness (5-year sliding windows)
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
            sharpes.append(float(w.mean() / sigma * np.sqrt(252)))
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
# Gate helpers (same as iter 005)
# ---------------------------------------------------------------------------

def gate_dsr(returns: pd.Series, n_trials: int) -> tuple[bool, float]:
    """G2: DSR/PSR significance < 0.05. [advances_fin_ml, p.222-223]"""
    arr = returns.values
    if len(arr) < 10:
        return False, 1.0
    if n_trials < 2:
        p_value = 1.0 - float(compute_psr(arr, benchmark=0.0))
        return p_value < 0.05, p_value
    result = compute_dsr(arr, n_trials=n_trials)
    return result.p_value < 0.05, float(result.p_value)


def gate_walk_forward_g3prime(
    returns: pd.Series,
    vtsim_returns: pd.Series,
    n_windows: int = WF_N_WINDOWS,
    notional_factor: float = NOTIONAL_FACTOR,
) -> tuple[bool, bool, list[float], list[float], list[float]]:
    """G3: WF 6/8 windows; G3 nominal (MDD≤25%) + G3' adapted.

    G3' ref_mdd per window = VTSIM_window_MDD * notional_factor.
    Returns: (g3_nominal_pass, g3_prime_pass, wf_rets, wf_mdds, ref_mdds)
    """
    n = len(returns)
    window_size = n // (n_windows + 1)
    if window_size < 63:
        return False, False, [], [], []

    oos_returns = []
    oos_mdds = []
    ref_mdds = []

    for _, test_range in walk_forward_splits(n, window_size, window_size, window_size):
        idxs = list(test_range)
        oos_ret = returns.iloc[idxs]
        eq = compute_equity(oos_ret)
        oos_returns.append(float((1 + oos_ret).prod() - 1))
        port_mdd = float(max_drawdown(eq))
        oos_mdds.append(port_mdd)

        oos_dates = returns.index[idxs]
        vt_window = vtsim_returns.loc[oos_dates[0]:oos_dates[-1]].dropna()
        if len(vt_window) > 5:
            vt_eq = compute_equity(vt_window)
            vt_mdd = float(max_drawdown(vt_eq))
        else:
            vt_mdd = 0.50
        ref_mdds.append(vt_mdd * notional_factor)

        if len(oos_returns) >= n_windows:
            break

    if len(oos_returns) < n_windows:
        return False, False, oos_returns, oos_mdds, ref_mdds

    n_profitable = sum(1 for r in oos_returns if r > 0)
    g3_nominal = (n_profitable >= 6) and all(m <= 0.25 for m in oos_mdds)
    g3_prime = (n_profitable >= 6) and all(
        m <= r for m, r in zip(oos_mdds, ref_mdds)
    )
    return g3_nominal, g3_prime, oos_returns, oos_mdds, ref_mdds


def gate_oos_70_30(returns: pd.Series) -> tuple[bool, float]:
    """G4: 70/30 OOS Sharpe > 0."""
    split = int(len(returns) * 0.70)
    oos = returns.iloc[split:]
    if len(oos) < 63:
        return False, 0.0
    s = float(sharpe(oos, periods_per_year=252))
    return s > 0, s


def gate_fwd_stress(returns: pd.Series, fwd_start: str = "2020-01-01") -> tuple[bool, float]:
    """G5: Post-2020 Sharpe > 0."""
    fwd = returns[returns.index >= fwd_start]
    if len(fwd) < 63:
        return False, 0.0
    s = float(sharpe(fwd, periods_per_year=252))
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
    bootstrapped_sharpes = []
    for _ in range(BOOTSTRAP_N):
        block_starts = rng.integers(0, n - block_size + 1, size=n_blocks)
        sample = np.concatenate([arr[s:s + block_size] for s in block_starts])[:n]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            bootstrapped_sharpes.append(float(sample.mean() / sigma * np.sqrt(252)))

    if not bootstrapped_sharpes:
        return False, 0.0
    ci_low = float(np.percentile(bootstrapped_sharpes, 0.1))
    return ci_low > 0, ci_low


def gate_crosslib(prices: pd.DataFrame, pandas_cagr: float) -> tuple[bool, float, float]:
    """G7: Numpy cross-lib ±3pp CAGR. [advances_fin_ml, p.31-34]"""
    np_rets = simulate_haa_gold_numpy(prices)

    if len(np_rets) < 252:
        return False, 0.0, pandas_cagr

    n = len(np_rets)
    np_eq = (1 + np_rets).cumprod() * 10000.0
    np_cagr = float((np_eq[-1] / np_eq[0]) ** (252 / (n - 1)) - 1)

    if np.isnan(np_cagr):
        return False, float("nan"), pandas_cagr

    diff_pp = abs(np_cagr - pandas_cagr) * 100
    return diff_pp <= 3.0, np_cagr, pandas_cagr


# ---------------------------------------------------------------------------
# Full run for one dataset
# ---------------------------------------------------------------------------

def run_dataset(ds_name: str, prices_full: pd.DataFrame) -> dict:
    cfg = DATASETS[ds_name]
    start, end = cfg["start"], cfg["end"]
    benchmark_ticker = cfg["benchmark"]

    prices = prices_full.loc[start:end].dropna(how="all")

    bm_ret = prices[benchmark_ticker].pct_change().dropna()
    bm_eq = compute_equity(bm_ret)
    bm_sharpe = float(sharpe(bm_ret, periods_per_year=252))
    bm_cagr = float(cagr(bm_eq, periods_per_year=252))
    bm_mdd = float(max_drawdown(bm_eq))

    print(f"\n{'='*60}")
    print(f"Dataset: {ds_name}  [{cfg['label']}]")
    print(f"  Period: {prices.index[0].date()} → {prices.index[-1].date()}")
    print(f"  Benchmark ({benchmark_ticker}): Sharpe={bm_sharpe:.4f} "
          f"CAGR={bm_cagr:.2%} MDD={bm_mdd:.2%}")
    print(f"  Config: HAA canary=VWOSIM, top{TOP_K_OFFENSIVE} offensive, "
          f"KMLM={KMLM_WEIGHT:.0%}, GLD={GLD_WEIGHT:.0%} (pre-committed, n_trials=1)")

    port_ret = simulate_haa_gold(prices)

    if len(port_ret) < 252:
        print(f"  ERROR: series too short ({len(port_ret)} days)")
        return {"error": "too short"}

    m = metrics_from_returns(port_ret)
    vs_bm = "✓" if m["sharpe"] > bm_sharpe else "✗"
    print(f"  Portfolio: Sharpe={m['sharpe']:.4f} {vs_bm}  "
          f"CAGR={m['cagr']:.2%}  MDD={m['mdd']:.2%}")

    # G1: PBO — N/A (single config)
    g1_pass = True
    print(f"  G1 PBO: N/A (n_configs=1 < {MIN_HONEST_N_CONFIGS}) → PASS (trivial)")

    # G2: DSR
    g2_pass, g2_p = gate_dsr(port_ret, n_trials=N_CONFIGS)
    print(f"  G2 DSR: p={g2_p:.2e} → {'PASS' if g2_pass else 'FAIL'}")

    # G3: Walk-forward (G3 nominal + G3' adapted)
    vtsim_ret = prices["VTSIM"].pct_change().dropna()
    g3_nominal, g3_prime, wf_rets, wf_mdds, ref_mdds = gate_walk_forward_g3prime(
        port_ret, vtsim_ret,
    )
    wf_profitable = sum(1 for r in wf_rets if r > 0)
    wf_max_mdd = max(wf_mdds) if wf_mdds else 0.0
    max_ref_mdd = max(ref_mdds) if ref_mdds else 0.0
    print(f"  G3 WF (nominal):  {wf_profitable}/{len(wf_rets)} profitable, "
          f"max_mdd={wf_max_mdd:.2%} → {'PASS' if g3_nominal else 'FAIL'}")
    print(f"  G3' WF (adapted): max_ref_mdd={max_ref_mdd:.2%} "
          f"(VT*{NOTIONAL_FACTOR}) → {'PASS' if g3_prime else 'FAIL'}")
    g3_pass = g3_prime  # notional_factor > 1.05 → use G3'

    # G4: OOS 70/30
    g4_pass, g4_sharpe = gate_oos_70_30(port_ret)
    print(f"  G4 OOS: Sharpe={g4_sharpe:.4f} → {'PASS' if g4_pass else 'FAIL'}")

    # G5: FWD stress post-2020
    g5_pass, g5_sharpe = gate_fwd_stress(port_ret)
    print(f"  G5 FWD: Sharpe(post-2020)={g5_sharpe:.4f} → {'PASS' if g5_pass else 'FAIL'}")

    # G6: Bootstrap
    g6_pass, g6_ci_low = gate_bootstrap(port_ret)
    print(f"  G6 Bootstrap: CI_low={g6_ci_low:.4f} → {'PASS' if g6_pass else 'FAIL'}")

    # G7: Cross-lib
    g7_pass, np_cagr, pd_cagr = gate_crosslib(prices, m["cagr"])
    print(f"  G7 Cross-lib: np={np_cagr:.2%} pd={pd_cagr:.2%} "
          f"diff={abs(np_cagr - pd_cagr)*100:.2f}pp → {'PASS' if g7_pass else 'FAIL'}")

    gates_passed = sum([g1_pass, g2_pass, g3_pass, g4_pass, g5_pass, g6_pass, g7_pass])
    print(f"  Gates: {gates_passed}/7")

    return {
        "dataset": ds_name,
        "config": "HAA_canaryVWO_top2_KMLM10_GLD5",
        "metrics": m,
        "benchmark": {
            "sharpe": bm_sharpe, "cagr": bm_cagr, "mdd": bm_mdd,
            "ticker": benchmark_ticker,
        },
        "gates": {
            "g1_pbo": g1_pass,
            "g2_dsr": g2_pass,
            "g3_wf": g3_pass,
            "g4_oos": g4_pass,
            "g5_fwd": g5_pass,
            "g6_bootstrap": g6_pass,
            "g7_crosslib": g7_pass,
            "n_passed": gates_passed,
            "g3_nominal_pass": g3_nominal,
            "g3_prime_pass": g3_prime,
            "notional_factor": NOTIONAL_FACTOR,
        },
        "gate_details": {
            "g1_note": f"N/A: single config < MIN_HONEST_N_CONFIGS={MIN_HONEST_N_CONFIGS}",
            "g2_dsr_p": g2_p,
            "g3_wf_returns": wf_rets,
            "g3_wf_mdds": wf_mdds,
            "g3_ref_mdds": ref_mdds,
            "g4_oos_sharpe": g4_sharpe,
            "g5_fwd_sharpe": g5_sharpe,
            "g6_ci_low": g6_ci_low,
            "g7_np_cagr": np_cagr,
        },
        "returns_series": {
            "HAA_top2_kmlm10_gld5": {
                "index": [str(d.date()) for d in port_ret.index],
                "net_returns": port_ret.tolist(),
            }
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Loading testfolio price cache...")
    raw = load_testfolio_frame(REPO_ROOT / "data/testfolio/cache/history.parquet")
    print(f"Loaded {len(raw.columns)} tickers, {len(raw)} days")

    print("Building stacked synthetic price series...")
    prices_full = build_stacked_prices(raw)
    for t in ["NTSXSIM", "NTSI", "NTSE", "GDESIM", "GLDSIM"]:
        if t in prices_full.columns:
            ndays = prices_full[t].dropna().__len__()
            print(f"  {t}: {ndays} days available")

    results = {}
    for ds_name in ["educational", "vt_real", "ndx_real"]:
        results[ds_name] = run_dataset(ds_name, prices_full)

    # Rolling-window robustness on educational
    print(f"\n{'='*60}")
    print("ROLLING-WINDOW ROBUSTNESS (educational, 5-year windows)")
    cfg_edu = DATASETS["educational"]
    prices_edu = prices_full.loc[cfg_edu["start"]:cfg_edu["end"]].dropna(how="all")
    edu_port = simulate_haa_gold(prices_edu)
    rob_pts, pct_pos, n_windows, roll_sharpes = rolling_window_robustness(edu_port)
    print(f"  Windows: {n_windows}")
    print(f"  % positive Sharpe: {pct_pos:.1%}")
    if roll_sharpes:
        print(f"  Min rolling Sharpe: {min(roll_sharpes):.3f}")
        print(f"  Max rolling Sharpe: {max(roll_sharpes):.3f}")
    print(f"  Robustness bonus: {rob_pts}/5")

    # Kill criteria check
    print(f"\n{'='*60}")
    print("KILL CRITERIA CHECK")
    edu_sharpe = results.get("educational", {}).get("metrics", {}).get("sharpe", 0.0)
    print(f"  Kill 1 — edu Sharpe ≤ 1.112 (must beat iter 005 WINNER): {edu_sharpe:.4f} → "
          f"{'FAIL (KILLED)' if edu_sharpe <= 1.112 else 'OK (not killed)'}")
    g3_any_fail = any(
        results[ds].get("gates", {}).get("g3_prime_pass", True) is False
        for ds in ["educational", "vt_real", "ndx_real"]
        if "error" not in results.get(ds, {})
    )
    print(f"  Kill 2 — any WF G3' fail: {'FAIL (KILLED)' if g3_any_fail else 'OK (not killed)'}")

    # Score
    print(f"\n{'='*60}")
    print("SCORING")

    # cumulative: iters 001-008 = 25 + this 1 = 26
    cumulative_n_trials = 26

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

    score_result = score_strategy(
        metrics_map, gates_map,
        cumulative_n_trials=cumulative_n_trials,
        robustness_bonus=rob_pts,
    )

    print(f"\nTier:  {score_result.tier.value}")
    print(f"Score: {score_result.total_score}/100")
    print(f"Winner conditions met: {score_result.winner_conditions_met}")
    print("\nScore breakdown:")
    for k, v in score_result.criteria.items():
        print(f"  {k}: {v['points']}/{v['max']}")

    # Compare vs iter 005
    print(f"\n{'='*60}")
    print("COMPARISON vs ITER 005 WINNER (HAA SmartStack)")
    iter005 = {"edu": (1.112, 0.1414, 0.2091), "vt": (1.049, 0.1299, 0.1505), "ndx": (0.942, 0.1063, 0.1505)}
    for ds_name, (s005, c005, m005) in [
        ("educational", iter005["edu"]),
        ("vt_real", iter005["vt"]),
        ("ndx_real", iter005["ndx"]),
    ]:
        r = results.get(ds_name, {})
        if "error" in r:
            continue
        m = r["metrics"]
        ds = ds_name
        print(f"  {ds}: Sharpe {m['sharpe']:.4f} ({'+' if m['sharpe']>s005 else ''}{m['sharpe']-s005:+.4f}) "
              f"CAGR {m['cagr']:.2%} ({'+' if m['cagr']>c005 else ''}{(m['cagr']-c005)*100:+.2f}pp) "
              f"MDD {m['mdd']:.2%} ({'+' if m['mdd']>m005 else ''}{(m['mdd']-m005)*100:+.2f}pp)")

    # Save
    verdict = score_result.to_dict()
    verdict["configs_tested"] = N_CONFIGS
    verdict["primary_citation"] = "[stocks_on_the_move, ch.6]"
    verdict["hypothesis_slug"] = "haa-gold-sleeve"
    verdict["status"] = score_result.tier.value.lower()
    verdict["notional_factor"] = NOTIONAL_FACTOR
    verdict["robustness"] = {
        "n_windows": n_windows,
        "pct_positive_sharpe": pct_pos,
        "min_rolling_sharpe": float(min(roll_sharpes)) if roll_sharpes else None,
        "max_rolling_sharpe": float(max(roll_sharpes)) if roll_sharpes else None,
        "bonus_pts": rob_pts,
    }

    results_json = {
        "hypothesis_slug": "haa-gold-sleeve",
        "datasets": results,
        "returns_series": {
            ds: results[ds].get("returns_series", {})
            for ds in ["educational", "vt_real", "ndx_real"]
        },
    }

    def _json_default(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return None if np.isnan(obj) else float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    verdict_path = ITER_DIR / "verdict.json"
    results_path = ITER_DIR / "results.json"
    with open(verdict_path, "w") as f:
        json.dump(verdict, f, indent=2, default=_json_default)
    with open(results_path, "w") as f:
        json.dump(results_json, f, indent=2, default=_json_default)

    print(f"\nSaved: {verdict_path}")
    print(f"Saved: {results_path}")


if __name__ == "__main__":
    main()
