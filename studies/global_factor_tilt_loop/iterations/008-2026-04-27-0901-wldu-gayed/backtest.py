"""
WLDU + Gayed 200d SMA — 2x Global Equity LETF with Trend Filter (iter 008)

Mechanism: Gayed (2021) Leverage Rotation Strategy (LRS) applied to global equity.
  - RISK ON:  SPYSIM close > SMA(200d) → hold 100% WLDU (2x VTSIM daily-reset)
  - RISK OFF: SPYSIM close ≤ SMA(200d) → hold 100% CASHX
  - Monthly rebalance check (Gayed canonical)

WLDU synthetic daily return:
  WLDU_ret = 2 × VTSIM_ret − 1 × CASHX_ret − 0.0075/252
  (75bps/y drag: 50bps financing spread + 25bps effective expense)

Edge vs HAA/VAA/Plano C: complete equity exit (0% equity) during bear regimes.
HAA rotates to bonds; VAA holds partial-defensive; Plano C never exits equity.
During 2008-2009, 2022, 2020-03: WLDU_Gayed holds CASHX = zero equity exposure.

Pre-committed kill criteria:
  1. 32y CAGR < 12% → fail
  2. Max single WF-window MDD > 35% → fail
  3. Whipsaw cost > 1%/y (informational, not hard gate)

Citations:
  [leverage_for_the_long_run, ch.3-4, p.40-60]  PRIMARY — Gayed LRS Table 8
  [stocks_on_the_move, p.21-30]                  trend signal as regime indicator
  [advances_fin_ml, p.208-211]                   G1 PBO
  [advances_fin_ml, p.222-223]                   G2 DSR
  [advances_fin_ml, p.196-202]                   G6 Bootstrap
  [advances_fin_ml, p.31-34]                     G7 cross-lib

Run from repo root:
    uv run python studies/global_factor_tilt_loop/iterations/008-2026-04-27-0901-wldu-gayed/backtest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).parents[4]
sys.path.insert(0, str(REPO_ROOT))

from ai_trade.backtest.data.testfolio_loader import load_testfolio_frame
from ai_trade.backtest.metrics.performance import sharpe, cagr, max_drawdown
from ai_trade.backtest.validation.pbo import MIN_HONEST_N_CONFIGS
from ai_trade.backtest.validation.dsr import dsr as compute_dsr, psr as compute_psr
from ai_trade.backtest.validation.walk_forward import walk_forward_splits

LOOP_ROOT = REPO_ROOT / "studies" / "global_factor_tilt_loop"
sys.path.insert(0, str(LOOP_ROOT))
from scoring import score_strategy, DatasetMetrics, Gates

ITER_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Pre-committed parameters (single config, no grid)
# [leverage_for_the_long_run, p.16]: 200-day SMA, monthly check, ~5 rotations/yr
# ---------------------------------------------------------------------------
N_CONFIGS = 1
SMA_WINDOW = 200       # 200-day simple moving average [p.16]
ANNUAL_DRAG = 0.0075   # 75bps/y: financing (50bps) + expense (25bps)
NOTIONAL_FACTOR = 2.0  # 2x daily-resetting LETF → G3' adapted gate applies
WF_N_WINDOWS = 8
BOOTSTRAP_N = 2000

# Dataset definitions
DATASETS = {
    "educational": {
        # SPYSIM binding: 1986+; 200d warmup; effective start ~late 1986
        "start": "1986-01-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "label": "VTSIM b&h ~39y (SPYSIM+SMA200 binding ~1987+)",
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

# Raw tickers needed
RAW_TICKERS = ["VTSIM", "SPYSIM", "CASHX", "QQQSIM"]


# ---------------------------------------------------------------------------
# WLDU synthetic construction
# [leverage_for_the_long_run, p.40-60]: 2x daily-reset LETF
# WLDU_ret = 2 × VTSIM_ret - 1 × CASHX_ret - annual_drag/252
# ---------------------------------------------------------------------------

def build_wldu_price(prices: pd.DataFrame) -> pd.DataFrame:
    """Add WLDU synthetic column to prices DataFrame.

    2x daily-resetting LETF on VTSIM (global equity).
    Borrowing cost = 1x CASHX daily rate (Fed Funds proxy).
    Additional drag = 0.75%/y (financing spread + expense).
    """
    ret = prices.pct_change()
    wldu_ret = 2.0 * ret["VTSIM"] - ret["CASHX"] - ANNUAL_DRAG / 252.0
    clean = wldu_ret.dropna()
    price_series = (1 + clean).cumprod() * 100.0
    out = prices.copy()
    out["WLDU"] = price_series
    return out


# ---------------------------------------------------------------------------
# SMA-200 signal on SPYSIM (daily, sampled at month-ends)
# [leverage_for_the_long_run, p.8, footnote 15]: SMA = unweighted mean of prior
# n daily closing prices of the total return series
# ---------------------------------------------------------------------------

def compute_monthly_signal(prices: pd.DataFrame) -> pd.Series:
    """Monthly risk-on/off signal from SPYSIM 200d SMA.

    Returns a Series indexed by month-end dates with 1.0 (risk-on) or 0.0 (risk-off).
    NaN for months before SMA warmup is complete.
    """
    spysim_daily = prices["SPYSIM"].dropna()
    sma_daily = spysim_daily.rolling(SMA_WINDOW).mean()
    daily_signal = (spysim_daily > sma_daily).astype(float)
    # NaN before warmup
    daily_signal[sma_daily.isna()] = float("nan")
    # Sample at month-ends
    monthly = daily_signal.resample("ME").last()
    return monthly


# ---------------------------------------------------------------------------
# WLDU + Gayed pandas simulation (monthly rebalance)
# ---------------------------------------------------------------------------

def simulate_wldu_gayed(
    prices: pd.DataFrame,
    prices_for_signal: pd.DataFrame | None = None,
) -> pd.Series:
    """Monthly WLDU/CASHX allocation driven by SPYSIM 200d SMA.

    prices            — dataset-window prices (for WLDU daily returns)
    prices_for_signal — full history (for SMA warmup); if None, uses prices.

    Logic each month-end (using full-history SMA so vt_real/ndx_real windows
    don't lose 200 days of warmup inside the truncated window):
      if SPYSIM > SMA(200d): next month = 100% WLDU
      else:                  next month = 100% CASHX
    Returns daily portfolio return series for the dataset window.
    """
    if prices_for_signal is None:
        prices_for_signal = prices

    # Build extended prices with WLDU (using dataset window)
    px = build_wldu_price(prices)

    # Compute SMA signal on full history (fixes truncation warmup bug)
    monthly_signal_full = compute_monthly_signal(prices_for_signal)
    # Restrict to dataset end
    monthly_signal = monthly_signal_full.loc[:prices.index[-1]]

    valid_months = monthly_signal.dropna().index
    if len(valid_months) == 0:
        return pd.Series(dtype=float)

    # Forward-fill signal to all calendar days covered by px
    daily_signal = monthly_signal.reindex(px.index, method="ffill").fillna(0.0)

    # Daily return sources
    daily_ret = px[["WLDU", "CASHX"]].pct_change()

    # Weights: 1.0 WLDU if risk-on, else 1.0 CASHX
    w_wldu = daily_signal
    w_cashx = 1.0 - w_wldu

    # Portfolio return with shift(1) to avoid lookahead
    port_ret = (w_wldu.shift(1) * daily_ret["WLDU"] +
                w_cashx.shift(1) * daily_ret["CASHX"])

    # Trim to dataset start (SMA is valid since we use full history)
    dataset_start = prices.index[0]
    port_ret = port_ret[port_ret.index >= dataset_start].dropna()

    return port_ret


# ---------------------------------------------------------------------------
# Numpy cross-lib reference (G7)
# [advances_fin_ml, p.31-34]: same logic in pure numpy
# ---------------------------------------------------------------------------

def simulate_wldu_gayed_numpy(
    prices: pd.DataFrame,
    prices_for_signal: pd.DataFrame | None = None,
    dataset_start: str | None = None,
) -> np.ndarray:
    """Numpy-pure WLDU+Gayed reference for G7 cross-lib validation.

    prices_for_signal — full-history DataFrame for SMA warmup (mirrors pandas fix).
    dataset_start     — ISO date string; trim returns to this date.
    """
    if prices_for_signal is None:
        prices_for_signal = prices

    # --- Signal computation from full history ---
    spysim_full = prices_for_signal["SPYSIM"].dropna()
    spysim_v_full = spysim_full.values.astype(float)
    n_full = len(spysim_v_full)
    dates_full = spysim_full.index

    sma_full = np.full(n_full, np.nan)
    for i in range(SMA_WINDOW - 1, n_full):
        sma_full[i] = spysim_v_full[i - SMA_WINDOW + 1:i + 1].mean()
    daily_signal_full = np.where(np.isnan(sma_full), np.nan, (spysim_v_full > sma_full).astype(float))

    # Sample signal at month-ends of full history
    periods_full = pd.DatetimeIndex(dates_full).to_period("M")
    me_indices_full = []
    for i in range(1, n_full):
        if periods_full[i] != periods_full[i - 1]:
            me_indices_full.append(i - 1)
    if not me_indices_full or me_indices_full[-1] != n_full - 1:
        me_indices_full.append(n_full - 1)
    me_indices_full = np.array(me_indices_full)

    monthly_sigs_full = daily_signal_full[me_indices_full]
    filled_daily_signal_full = np.full(n_full, np.nan)
    for k, me_idx in enumerate(me_indices_full):
        sig = monthly_sigs_full[k]
        if np.isnan(sig):
            continue
        end = me_indices_full[k + 1] if k + 1 < len(me_indices_full) else n_full
        filled_daily_signal_full[me_idx:end] = sig

    # Build a lookup: date → signal (for the dataset window)
    signal_by_date = {
        d: filled_daily_signal_full[i]
        for i, d in enumerate(dates_full)
    }

    # --- Dataset window computation ---
    vtsim = prices["VTSIM"].dropna()
    cashx = prices["CASHX"].dropna()
    common = vtsim.index.intersection(cashx.index)
    if dataset_start:
        common = common[common >= pd.Timestamp(dataset_start)]
    vtsim_v = vtsim.loc[common].values.astype(float)
    cashx_v = cashx.loc[common].values.astype(float)
    dates_ds = common

    n_ds = len(dates_ds)
    vtsim_ret = np.diff(vtsim_v) / vtsim_v[:-1]
    cashx_ret = np.diff(cashx_v) / cashx_v[:-1]
    wldu_ret = 2.0 * vtsim_ret - cashx_ret - ANNUAL_DRAG / 252.0

    # Map full-history signals to dataset dates (shift-1: use yesterday's signal)
    port_rets = []
    for i in range(1, n_ds):
        yesterday = dates_ds[i - 1]
        sig = signal_by_date.get(yesterday, np.nan)
        if np.isnan(sig):
            continue
        if sig > 0.5:
            port_rets.append(wldu_ret[i - 1])
        else:
            port_rets.append(cashx_ret[i - 1])

    return np.array(port_rets)


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
# Rolling-window robustness
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
# Gate helpers
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
    v_hybrid_mf_mdd: float = 0.4471,
) -> tuple[bool, bool, list[float], list[float], list[float]]:
    """G3: WF 6/8 windows; compute G3 nominal and G3' adapted.

    G3' ref_mdd per window = max(VT_window_MDD * notional_factor, v_hybrid_mf_mdd).
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
        ref_mdd = max(vt_mdd * notional_factor, v_hybrid_mf_mdd)
        ref_mdds.append(ref_mdd)

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


def gate_crosslib(
    prices: pd.DataFrame,
    prices_full: pd.DataFrame,
    pandas_cagr: float,
    dataset_start: str,
) -> tuple[bool, float, float]:
    """G7: Numpy cross-lib ±3pp CAGR. [advances_fin_ml, p.31-34]"""
    np_rets = simulate_wldu_gayed_numpy(
        prices, prices_for_signal=prices_full, dataset_start=dataset_start
    )

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
# Whipsaw cost estimation
# ---------------------------------------------------------------------------

def estimate_whipsaw_cost(port_ret: pd.Series, daily_signal_ffill: pd.Series) -> float:
    """Estimate annualized whipsaw cost from number of switches.

    Assumes each switch = 0.0% explicit transaction cost (ETF bid/ask ~0.01%),
    but the drag from being out of bull market portions is captured in the backtest.
    Returns estimated switches per year.
    """
    switches = (daily_signal_ffill.diff().abs() > 0.5).sum()
    years = len(port_ret) / 252.0
    if years < 0.01:
        return 0.0
    return float(switches / years)


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
    print(f"  Config: WLDU=2xVTSIM, signal=SPYSIM_SMA({SMA_WINDOW}d), monthly check, "
          f"drag={ANNUAL_DRAG:.2%}/y (pre-committed, n_trials=1)")

    # Pass full history for SMA warmup (fixes truncation warmup bug)
    port_ret = simulate_wldu_gayed(prices, prices_for_signal=prices_full)

    if len(port_ret) < 252:
        print(f"  ERROR: series too short ({len(port_ret)} days)")
        return {"error": "too short"}

    m = metrics_from_returns(port_ret)
    vs_bm = "✓" if m["sharpe"] > bm_sharpe else "✗"
    print(f"  Portfolio: Sharpe={m['sharpe']:.4f} {vs_bm}  "
          f"CAGR={m['cagr']:.2%}  MDD={m['mdd']:.2%}")
    print(f"  Returns: {port_ret.index[0].date()} → {port_ret.index[-1].date()} "
          f"({len(port_ret)} days)")

    # Estimate whipsaw (informational) — use full history for signal
    monthly_sig = compute_monthly_signal(prices_full).loc[:prices.index[-1]]
    daily_sig = monthly_sig.reindex(prices.index, method="ffill").fillna(0.0)
    daily_sig = daily_sig.loc[port_ret.index]
    switches_per_year = estimate_whipsaw_cost(port_ret, daily_sig)
    time_in_market = daily_sig.mean()
    print(f"  Whipsaw: {switches_per_year:.1f} switches/yr, "
          f"{time_in_market:.1%} time in WLDU (risk-on)")

    # Kill criteria check
    years_approx = len(port_ret) / 252
    if years_approx >= 20:  # only check if we have long enough window
        kill1 = m["cagr"] < 0.12
        kill2 = m["mdd"] > 0.35
        if kill1:
            print(f"  KILL 1 TRIGGERED: CAGR={m['cagr']:.2%} < 12%")
        if kill2:
            print(f"  KILL 2 TRIGGERED: MDD={m['mdd']:.2%} > 35% (full-period)")
    else:
        kill1, kill2 = False, False

    # G1: PBO (trivial, n_configs=1)
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
    # NOTIONAL_FACTOR=2.0 > 1.05 → use G3' adapted
    g3_pass = g3_prime

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
    g7_pass, np_cagr, pd_cagr = gate_crosslib(
        prices, prices_full, m["cagr"], start
    )
    print(f"  G7 Cross-lib: np={np_cagr:.2%} pd={pd_cagr:.2%} "
          f"diff={abs(np_cagr - pd_cagr)*100:.2f}pp → {'PASS' if g7_pass else 'FAIL'}")

    gates_passed = sum([g1_pass, g2_pass, g3_pass, g4_pass, g5_pass, g6_pass, g7_pass])
    print(f"  Gates: {gates_passed}/7")

    return {
        "dataset": ds_name,
        "config": f"WLDU_2xVTSIM_SMA{SMA_WINDOW}_monthly",
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
        "auxiliary": {
            "switches_per_year": switches_per_year,
            "time_in_market": float(time_in_market),
            "kill1_triggered": kill1,
            "kill2_triggered": kill2,
        },
        "returns_series": {
            "WLDU_SMA200_monthly": {
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

    # Verify required tickers
    for t in RAW_TICKERS:
        if t not in raw.columns:
            print(f"  WARNING: {t} not in cache!")
        else:
            ndays = raw[t].dropna().__len__()
            first = raw[t].dropna().index[0].date()
            print(f"  {t}: {ndays} days, from {first}")

    results = {}
    for ds_name in ["educational", "vt_real", "ndx_real"]:
        results[ds_name] = run_dataset(ds_name, raw)

    # Rolling robustness on educational
    print(f"\n{'='*60}")
    print("ROLLING-WINDOW ROBUSTNESS (educational, 5-year windows)")
    cfg_edu = DATASETS["educational"]
    prices_edu = raw.loc[cfg_edu["start"]:cfg_edu["end"]].dropna(how="all")
    edu_port = simulate_wldu_gayed(prices_edu, prices_for_signal=raw)
    rob_pts, pct_pos, n_windows, roll_sharpes = rolling_window_robustness(edu_port)
    print(f"  Windows: {n_windows}")
    print(f"  % positive Sharpe: {pct_pos:.1%}")
    if roll_sharpes:
        print(f"  Min rolling Sharpe: {min(roll_sharpes):.3f}")
        print(f"  Max rolling Sharpe: {max(roll_sharpes):.3f}")
    print(f"  Robustness bonus: {rob_pts}/5")

    # Score
    print(f"\n{'='*60}")
    print("SCORING")

    # cumulative: iters 001-007 = 24, this iter = 1 → total = 25
    cumulative_n_trials = 25

    metrics_map = {}
    gates_map = {}
    for ds_name in ["educational", "vt_real", "ndx_real"]:
        r = results[ds_name]
        if "error" in r:
            metrics_map[ds_name] = DatasetMetrics(sharpe=0.0, cagr=0.0, mdd=1.0, dsr_p_value=1.0)
            gates_map[ds_name] = Gates(False, False, False, False, False, False, False)
            continue
        m_ = r["metrics"]
        g_ = r["gates"]
        gd_ = r["gate_details"]
        metrics_map[ds_name] = DatasetMetrics(
            sharpe=m_["sharpe"], cagr=m_["cagr"], mdd=m_["mdd"],
            dsr_p_value=gd_["g2_dsr_p"],
        )
        gates_map[ds_name] = Gates(
            g1_pbo=g_["g1_pbo"], g2_dsr=g_["g2_dsr"], g3_wf=g_["g3_wf"],
            g4_oos=g_["g4_oos"], g5_fwd=g_["g5_fwd"],
            g6_bootstrap=g_["g6_bootstrap"], g7_crosslib=g_["g7_crosslib"],
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

    # Kill criteria summary
    print(f"\n{'='*60}")
    print("KILL CRITERIA SUMMARY")
    for ds_name in ["educational", "vt_real", "ndx_real"]:
        r = results[ds_name]
        if "error" not in r:
            aux = r.get("auxiliary", {})
            print(f"  {ds_name}: kill1={aux.get('kill1_triggered', 'N/A')} "
                  f"kill2={aux.get('kill2_triggered', 'N/A')} "
                  f"switches/yr={aux.get('switches_per_year', 0):.1f} "
                  f"pct_in_mkt={aux.get('time_in_market', 0):.1%}")

    # Save outputs
    verdict = score_result.to_dict()
    verdict["configs_tested"] = N_CONFIGS
    verdict["primary_citation"] = "[leverage_for_the_long_run, ch.3-4, p.40-60]"
    verdict["hypothesis_slug"] = "wldu-gayed"
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
        "hypothesis_slug": "wldu-gayed",
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
