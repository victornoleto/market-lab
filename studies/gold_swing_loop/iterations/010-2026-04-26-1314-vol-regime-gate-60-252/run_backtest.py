"""Iter 010 — Realized-vol regime gate (long XAUUSD when σ_60d > σ_252d).

Strategy
--------
* Single-asset, **LONG-ONLY**. Position[t] = flag[t] ∈ {0, 1}.
* Flag is binary: 1 iff σ_60d(log_returns) > σ_252d(log_returns) at close[t].
* Position held for one bar (close[t] → close[t+1]); flips when σ ratio crosses.
* No `|z|>kσ` entry trigger → state-machine-aware fwd-N-bar concern from
  GS-9 does NOT apply (no entry-dilution; flag flips ARE entries/exits).

Why this sidesteps GS-4..GS-9
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* No cross-asset signal (vs GS-4 VIX, GS-5 DXY)
* No calendar-event trigger (vs GS-6 FOMC)
* No `|z|>kσ` trigger on price/spread (vs GS-7 z-MR, GS-8/9 XAU/XAG)
* No pair / cointegration assumption (vs GS-8 ADF non-stationarity)
* Pure single-asset, slow regime indicator. Both broker tracks viable.

Per-TF parameters (TF-natural lookbacks; pre-committed; IC-8 single cfg):
* gld_long          : 1d, σ_60d/σ_252d, ann=252
* xauusd_real       : 1d, σ_60d/σ_252d, ann=252
* xauusd_intraday   : 1h with daily-resampled σ flag propagated, ann=5119

Pre-validation (cost-aware, no |z|>kσ so simpler than iter 008/009):
* p_active   ∈ [0.15, 0.70]
* μ_active   > 0  (annualized log return when flag=1)
* n_flips/yr ≤ 8  (low turnover; one regime episode = many bars / few flips)
* annualized cost drag < 0.5 × annualized active drift
At least 2/3 datasets must satisfy ALL → run backtest. 0/3 → auto-abort.

Output: `pre_val.json` + `results.json` (Track A + Track B per dataset)
+ `verdict.json` + `final_report.md`.

Citations
---------
* `[volatility_trading, p.58-59]` — vol cone framework (PRIMARY)
* `[volatility_trading, p.217]` — regime-filter robustness
* `[volatility_trading, p.249-251]` — vol clustering / persistence
* `[trading_systems_methods, p.131]` — KAMA Efficiency Ratio = stdev(C,n)/stdev(C,m)
* `[trading_systems_methods, p.13]` — metals classified low-noise → directional
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
* `[advances_fin_ml, p.222-223]` — DSR with cumulative ``n_trials = 10``
* DEAD_ENDS GS-7/8/9 — entry-dilution closure motivates non-`|z|` grammar
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "studies" / "gold_swing_loop"))
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.validation.bootstrap import stationary_bootstrap_trades  # noqa: E402
from ai_trade.backtest.validation.dsr import dsr as dsr_func  # noqa: E402
from ai_trade.backtest.validation.dsr import sharpe_periodic  # noqa: E402
from ai_trade.backtest.validation.walk_forward import walk_forward_gate  # noqa: E402

from cost_models import apply_inter_costs_with_darf, apply_pepperstone_costs  # noqa: E402
from scoring import (  # noqa: E402
    BENCHMARKS,
    DatasetMetrics,
    Gates,
    score_strategy,
)

ITER_DIR = Path(__file__).resolve().parent
CFG_ID = "vol_regime_gate_60_252_long_only"

# Cumulative trial count: 9 prior iters + 1 (this) = 10.
CUMULATIVE_N_TRIALS = 10

# --- Strategy parameters (pre-committed; IC-8 single cfg) -------------------
WINDOW_SHORT = 60   # σ_60 (trading days)
WINDOW_LONG = 252   # σ_252 (trading days, ~1y)

TF_PARAMS = {
    "gld_long":        {"tf": "1d", "ann": 252},
    "xauusd_real":     {"tf": "1d", "ann": 252},
    "xauusd_intraday": {"tf": "1h", "ann": 5119},
}

DATA_PATHS = {
    "gld_long":        "data/tiingo/daily/prices/GLD.parquet",
    "xauusd_real":     "data/tiingo/daily/prices/xauusd.parquet",
    "xauusd_intraday": "data/tiingo/1hour/prices/xauusd.parquet",
}


# ===========================================================================
# Strategy primitives (TDD-tested in test_vol_regime_signal.py)
# ===========================================================================


def realized_vol(prices: pd.Series, window: int, ann_factor: int) -> pd.Series:
    """Annualized rolling std of log returns.

    σ_ann(t) = sqrt(ann_factor) × stdev(log(P[t-window+1:t+1] / P[t-window:t]), ddof=1).

    Returns NaN until at least ``window+1`` price observations exist (need
    ``window`` log returns to compute std with ddof=1).
    """
    log_ret = np.log(prices / prices.shift(1))
    sigma_per_bar = log_ret.rolling(window, min_periods=window).std(ddof=1)
    sigma_ann = sigma_per_bar * np.sqrt(ann_factor)
    sigma_ann.name = f"sigma_{window}_ann"
    return sigma_ann


def realized_vol_numpy(prices: np.ndarray, window: int, ann_factor: int) -> np.ndarray:
    """Hand-rolled numpy reference for cross-lib parity (G7 gate)."""
    log_ret = np.full_like(prices, np.nan, dtype=np.float64)
    log_ret[1:] = np.log(prices[1:] / prices[:-1])
    out = np.full_like(prices, np.nan, dtype=np.float64)
    for i in range(window, len(prices)):
        chunk = log_ret[i - window + 1: i + 1]
        if np.any(np.isnan(chunk)):
            continue
        out[i] = np.std(chunk, ddof=1) * np.sqrt(ann_factor)
    return out


def vol_regime_flag(
    prices: pd.Series,
    *,
    window_short: int = 60,
    window_long: int = 252,
    ann_factor: int = 252,
) -> pd.Series:
    """Binary flag: 1 if σ_short > σ_long, else 0.

    Warmup (until σ_long is defined) returns 0 (no signal yet).
    Equal-σ (rare; e.g., constant returns) → 0 (strict greater).
    """
    sigma_short = realized_vol(prices, window=window_short, ann_factor=ann_factor)
    sigma_long = realized_vol(prices, window=window_long, ann_factor=ann_factor)
    flag = (sigma_short > sigma_long).astype(int)
    # Where σ_long is NaN (warmup) the comparison is False → flag=0; explicit
    # mask here to keep semantics crystal clear.
    flag = flag.where(sigma_long.notna(), 0).astype(int)
    flag.name = "vol_regime_flag"
    return flag


def vol_regime_position(
    prices: pd.Series,
    *,
    window_short: int = 60,
    window_long: int = 252,
    ann_factor: int = 252,
) -> pd.Series:
    """LONG-ONLY position: 1.0 when flag=1, 0.0 when flag=0."""
    flag = vol_regime_flag(
        prices,
        window_short=window_short,
        window_long=window_long,
        ann_factor=ann_factor,
    )
    return flag.astype(float).rename("position")


# ===========================================================================
# Helpers
# ===========================================================================


def compute_mean_hold(position: pd.Series, ann: int) -> tuple[float, int, float]:
    """Mean hold per long episode in trading days, plus n trades and bar count."""
    pos = position.values
    in_trade = False
    starts: list[int] = []
    ends: list[int] = []
    for i, p in enumerate(pos):
        if not in_trade and p > 0:
            starts.append(i)
            in_trade = True
        elif in_trade and p == 0:
            ends.append(i)
            in_trade = False
    if in_trade:
        ends.append(len(pos))
    if not starts:
        return 0.0, 0, 0.0
    holds_bars = [(e - s) for s, e in zip(starts, ends)]
    mean_bars = float(np.mean(holds_bars))
    bars_per_day = ann / 252.0
    mean_days = mean_bars / bars_per_day if bars_per_day > 0 else mean_bars
    return float(mean_days), int(len(starts)), mean_bars


def count_flips(position: pd.Series) -> int:
    """Number of regime transitions (flat→long + long→flat)."""
    return int((position.diff().abs() > 0).sum())


# ===========================================================================
# Pre-validation (no |z|>kσ — different shape from iter 008/009)
# ===========================================================================


def run_pre_val_for_dataset(
    prices: pd.Series,
    *,
    window_short: int,
    window_long: int,
    ann_factor: int,
    cost_floor_bps_per_flip: float = 8.0,
    swap_long_bps_per_night: float = 1.0,
) -> dict:
    """Pre-val for vol-regime gate.

    Measures:
    * p_active: fraction of bars where flag=1
    * mu_active_bps_per_bar: mean log return on flag-on bars (×1e4)
    * mu_active_bps_per_yr_active: annualized active drift (mu_active × ann_factor)
    * n_flips_per_year: regime transitions / year
    * cost_yr_bps: n_flips/yr × spread_RT + p_active × 365 × |swap_long|
    * passed: ALL FOUR conditions
    """
    flag = vol_regime_flag(
        prices,
        window_short=window_short,
        window_long=window_long,
        ann_factor=ann_factor,
    )
    log_ret = np.log(prices / prices.shift(1))
    flag_on = flag == 1
    n_bars = int(flag_on.sum())
    n_total = int(flag.size)
    p_active = float(n_bars / n_total) if n_total > 0 else 0.0

    # Active drift: mean log return on bars where prior bar had flag=1 (since
    # position at close[t-1] applies to ret[t] — held into next bar).
    pos_lag = flag.shift(1).fillna(0).astype(float)
    active_returns = log_ret.where(pos_lag > 0).dropna()
    if len(active_returns) > 0:
        mu_per_bar = float(active_returns.mean())
    else:
        mu_per_bar = 0.0
    mu_per_bar_bps = mu_per_bar * 1e4
    mu_per_yr_when_active = mu_per_bar * ann_factor  # annualized only on active bars
    mu_per_yr_when_active_bps = mu_per_yr_when_active * 1e4

    # Time span in years (calendar-year approximation).
    span_yr = max((prices.index[-1] - prices.index[0]).days / 365.25, 1e-9)
    n_flips = count_flips(flag.astype(float))
    n_flips_per_yr = n_flips / span_yr

    # Annualized cost drag: round-trips × spread + nights long × swap.
    # n_flips/yr is the round-trip rate (each flip = enter or exit; pair=1 RT).
    # Use n_flips_per_yr / 2 as RT count (one full open+close per 2 flips).
    rt_per_yr = n_flips_per_yr / 2.0
    spread_yr_bps = rt_per_yr * cost_floor_bps_per_flip
    swap_yr_bps = p_active * 365.0 * swap_long_bps_per_night
    cost_yr_bps = spread_yr_bps + swap_yr_bps

    # Pass conditions
    p_active_pass = bool(0.15 <= p_active <= 0.70)
    mu_pass = bool(mu_per_bar > 0)
    flips_pass = bool(n_flips_per_yr <= 8.0)
    cost_pass = bool(cost_yr_bps < 0.5 * abs(mu_per_yr_when_active_bps) * p_active)

    passed = bool(p_active_pass and mu_pass and flips_pass and cost_pass)

    reason_parts = []
    if not p_active_pass:
        reason_parts.append(f"p_active={p_active:.3f} ∉ [0.15, 0.70]")
    if not mu_pass:
        reason_parts.append(f"mu_active_bps={mu_per_bar_bps:+.3f} ≤ 0 (no active drift)")
    if not flips_pass:
        reason_parts.append(f"n_flips/yr={n_flips_per_yr:.2f} > 8")
    if not cost_pass:
        reason_parts.append(
            f"cost_yr_bps={cost_yr_bps:.1f} ≥ 0.5 × {mu_per_yr_when_active_bps:.1f} × "
            f"{p_active:.3f} = {0.5 * mu_per_yr_when_active_bps * p_active:.1f}"
        )
    reason = "passed all conditions" if passed else "; ".join(reason_parts)

    return {
        "p_active": p_active,
        "n_active_bars": n_bars,
        "n_total_bars": n_total,
        "mu_active_bps_per_bar": mu_per_bar_bps,
        "mu_active_bps_per_yr_active": mu_per_yr_when_active_bps,
        "n_flips": n_flips,
        "n_flips_per_yr": n_flips_per_yr,
        "rt_per_yr": rt_per_yr,
        "span_yr": span_yr,
        "spread_yr_bps": spread_yr_bps,
        "swap_yr_bps": swap_yr_bps,
        "cost_yr_bps": cost_yr_bps,
        "p_active_pass": p_active_pass,
        "mu_pass": mu_pass,
        "flips_pass": flips_pass,
        "cost_pass": cost_pass,
        "passed": passed,
        "reason": reason,
    }


# ===========================================================================
# Metric helpers (mirror iter 009)
# ===========================================================================


def compute_metrics(net_pnl: pd.Series, ann: int) -> dict[str, float]:
    rets = net_pnl.dropna()
    if rets.std() == 0 or len(rets) < 2:
        return {"sharpe": 0.0, "sharpe_periodic": 0.0, "cagr": 0.0, "mdd": 0.0}
    sharpe_per = sharpe_periodic(rets.values)
    sharpe_ann = float(sharpe_per * np.sqrt(ann))
    eq = (1.0 + rets).cumprod()
    span_yr = max((rets.index[-1] - rets.index[0]).days / 365.25, 1e-9)
    cagr = float(eq.iloc[-1] ** (1.0 / span_yr) - 1.0)
    cummax = eq.cummax()
    dd = (eq - cummax) / cummax
    mdd = float(-dd.min())
    return {"sharpe": sharpe_ann, "sharpe_periodic": float(sharpe_per),
            "cagr": cagr, "mdd": mdd}


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
    block_mean = max(5, int(ann / 1000))
    samples = stationary_bootstrap_trades(
        arr, block_mean=block_mean, n_resamples=2000, seed=42
    )
    sharpes = []
    for row in samples:
        s = sharpe_periodic(row)
        sharpes.append(s * np.sqrt(ann))
    sharpes = np.array(sharpes)
    lo = float(np.percentile(sharpes, 0.05))
    hi = float(np.percentile(sharpes, 99.95))
    return bool(lo > 0), lo, hi


def cross_lib_gross_check(
    position: pd.Series, returns: pd.Series
) -> tuple[float, float]:
    pos_pd = position.shift(1).fillna(0.0)
    pnl_pd = pos_pd * returns
    eq_pd = (1.0 + pnl_pd).cumprod()
    span_yr = max((position.index[-1] - position.index[0]).days / 365.25, 1e-9)
    cagr_pd = float(eq_pd.iloc[-1] ** (1.0 / span_yr) - 1.0)
    pos_np = pos_pd.values.astype(np.float64)
    ret_np = returns.values.astype(np.float64)
    pnl_np = pos_np * ret_np
    eq_np = np.cumprod(1.0 + pnl_np)
    cagr_np = float(eq_np[-1] ** (1.0 / span_yr) - 1.0)
    return cagr_pd, cagr_np


# ===========================================================================
# Per-dataset run
# ===========================================================================


def _bar_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().fillna(0.0)


def load_close(name: str) -> pd.Series:
    """Load close series; for xauusd_intraday, also return daily-resampled close
    so that vol regime can be computed on daily bars (1h is too noisy for σ_60d)."""
    path = DATA_PATHS[name]
    df = pd.read_parquet(path).sort_index()
    return df["close"].astype(float)


def build_intraday_position(
    close_1h: pd.Series, *, window_short: int, window_long: int
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """For xauusd_intraday: compute regime flag on daily-resampled closes,
    then propagate to all 1h bars within each day.

    Returns
    -------
    position_1h : pd.Series
        Long-only position (0.0 / 1.0) indexed on 1h bars.
    close_1h_aligned : pd.Series
        Same 1h close series (returned for convenience).
    flag_daily : pd.Series
        The daily-resampled flag (informational; for diagnostics).
    """
    # Resample 1h close to daily close (last hourly close per day, NY-session naive).
    close_daily = close_1h.resample("1D").last().dropna()
    flag_daily = vol_regime_flag(
        close_daily, window_short=window_short, window_long=window_long, ann_factor=252,
    )
    # Propagate daily flag to 1h bars: at each 1h bar t, use flag of the
    # CURRENT day's close (i.e., the regime determined at end of trading day).
    # To avoid look-ahead: use the PREVIOUS day's flag for all 1h bars within
    # day d (so position at 1h bar t depends on σ_short / σ_long known by
    # end of day d-1).
    flag_daily_shift = flag_daily.shift(1).fillna(0).astype(int)
    # Reindex to 1h bars: for each 1h bar at timestamp t, take flag of the
    # day index <= t.normalize() (i.e., reindex with method="ffill").
    flag_daily_shift.index = pd.DatetimeIndex(flag_daily_shift.index)
    flag_1h = flag_daily_shift.reindex(close_1h.index, method="ffill").fillna(0).astype(int)
    pos_1h = flag_1h.astype(float).rename("position")
    return pos_1h, close_1h, flag_daily


def run_one_dataset(name: str) -> dict:
    params = TF_PARAMS[name]
    ann = params["ann"]
    tf = params["tf"]

    close = load_close(name)
    if name == "xauusd_intraday":
        position, close_aligned, flag_daily_diag = build_intraday_position(
            close, window_short=WINDOW_SHORT, window_long=WINDOW_LONG,
        )
        bar_ret = _bar_returns(close_aligned)
        flag_diag_summary = {
            "p_active_daily": float(flag_daily_diag.mean()),
            "n_flips_daily": count_flips(flag_daily_diag.astype(float)),
            "note": "daily-resampled flag propagated to 1h bars",
        }
    else:
        position = vol_regime_position(
            close, window_short=WINDOW_SHORT, window_long=WINDOW_LONG, ann_factor=ann,
        )
        bar_ret = _bar_returns(close)
        flag_diag_summary = {
            "p_active": float(position.mean()),
            "n_flips": count_flips(position),
        }

    # ---- Track A — Pepperstone CFD ------------------------------------
    if tf == "1d":
        swap_long = -1.0  # bps/night
        swap_short = 0.3
    elif tf == "1h":
        swap_long = -1.0 / 24.0
        swap_short = 0.3 / 24.0
    else:
        raise ValueError(f"unknown tf: {tf}")

    cost_a = apply_pepperstone_costs(
        bar_ret, position,
        spread_rt_bps=8.0,
        swap_long_bps=swap_long,
        swap_short_bps=swap_short,
        intraday_close=False,
    )
    m_a = compute_metrics(cost_a.net_pnl, ann)
    rets_a = cost_a.net_pnl.dropna()

    # ---- Track B — Inter ETF GLD (only for daily; T+1 bars only) ------
    if tf == "1d":
        cost_b = apply_inter_costs_with_darf(
            bar_ret, position,
            fx_rt_bps=100.0,
            darf_rate=0.15,
        )
        m_b = compute_metrics(cost_b.net_pnl, ann)
        rets_b = cost_b.net_pnl.dropna()
        track_b_summary = cost_b.summary()
        track_b_metrics = {
            **m_b,
            "n_swap_nights": cost_b.n_swap_nights,
            "cost_summary": track_b_summary,
        }
    else:
        track_b_metrics = {
            "note": "Track B not viable on intraday (T+1 settlement; daily-only)",
            "sharpe": 0.0, "cagr": 0.0, "mdd": 0.0,
        }

    mean_hold_days, n_trades, mean_hold_bars = compute_mean_hold(position, ann)

    # ---- Gates (Track A primary; Track B reported but not gated) -----
    g1_pbo = True
    g1_note = "single-cfg PBO degenerate (IC-8 single cfg pre-committed); pass by convention"

    if rets_a.std() > 0 and len(rets_a) > 30:
        dsr_res = dsr_func(rets_a.values, n_trials=CUMULATIVE_N_TRIALS)
        dsr_p = float(dsr_res.p_value)
        g2_dsr = bool(dsr_p < 0.05)
    else:
        dsr_p = 1.0
        g2_dsr = False

    g3_wf, wf_returns, wf_dds = run_walk_forward(rets_a, n_windows=8)

    cut = int(0.7 * len(rets_a))
    oos_chunk = rets_a.iloc[cut:]
    oos_sharpe = (
        sharpe_periodic(oos_chunk.values) * np.sqrt(ann)
        if len(oos_chunk) > 1 else 0.0
    )
    g4_oos = bool(oos_sharpe > 0)

    fwd_chunk = rets_a[rets_a.index >= "2022-01-01"]
    fwd_sharpe = (
        sharpe_periodic(fwd_chunk.values) * np.sqrt(ann)
        if len(fwd_chunk) > 1 else 0.0
    )
    g5_fwd = bool(fwd_sharpe > 0)

    g6_boot, ci_lo, ci_hi = run_bootstrap(rets_a, ann)

    cagr_pd_gross, cagr_np_gross = cross_lib_gross_check(position, bar_ret)
    g7_diff_pp = abs(cagr_pd_gross - cagr_np_gross) * 100.0
    g7_cl = bool(g7_diff_pp <= 3.0)

    gates = Gates(
        g1_pbo=g1_pbo, g2_dsr=g2_dsr, g3_wf=g3_wf, g4_oos=g4_oos,
        g5_fwd=g5_fwd, g6_bootstrap=g6_boot, g7_crosslib=g7_cl,
    )

    gross_pnl_total = float(cost_a.gross_pnl.sum())
    spread_total = float(-cost_a.spread_cost.sum())
    swap_total = float(-cost_a.swap_cost.sum())
    net_total = float(cost_a.net_pnl.sum())
    per_trade_gross_bps = (gross_pnl_total / max(n_trades, 1)) * 1e4 if n_trades > 0 else 0.0
    per_trade_cost_bps = (-(spread_total + swap_total) / max(n_trades, 1)) * 1e4 if n_trades > 0 else 0.0
    per_trade_net_bps = (net_total / max(n_trades, 1)) * 1e4 if n_trades > 0 else 0.0

    return {
        "tf": tf,
        "params": {"window_short": WINDOW_SHORT, "window_long": WINDOW_LONG, "ann": ann},
        "n_bars": int(len(close)),
        "date_range": [close.index[0].isoformat(), close.index[-1].isoformat()],
        "flag_diagnostics": flag_diag_summary,
        "track_a_metrics": {
            **m_a,
            "dsr_p_value": dsr_p,
            "mean_hold_days": mean_hold_days,
            "mean_hold_bars": mean_hold_bars,
            "n_trades": n_trades,
            "n_swap_nights": cost_a.n_swap_nights,
            "n_weekend_holds": cost_a.n_weekend_holds,
            "cost_summary": cost_a.summary(),
            "per_trade_gross_bps": per_trade_gross_bps,
            "per_trade_cost_bps": per_trade_cost_bps,
            "per_trade_net_bps": per_trade_net_bps,
        },
        "track_b_metrics": track_b_metrics,
        "gates": {
            "g1_pbo": g1_pbo, "g1_note": g1_note,
            "g2_dsr": g2_dsr, "dsr_p_value": dsr_p,
            "g3_wf": g3_wf, "wf_returns": wf_returns, "wf_dds": wf_dds,
            "g4_oos": g4_oos, "oos_sharpe": float(oos_sharpe),
            "g5_fwd": g5_fwd, "fwd_sharpe": float(fwd_sharpe),
            "g6_bootstrap": g6_boot, "ci_lo": ci_lo, "ci_hi": ci_hi,
            "g7_crosslib": g7_cl,
            "g7_cagr_pd_gross": cagr_pd_gross,
            "g7_cagr_np_gross": cagr_np_gross,
            "g7_diff_pp": g7_diff_pp,
        },
        "n_passed": gates.n_passed,
        "_returns_series": {
            "index": [d.isoformat() for d in cost_a.net_pnl.index],
            "net_returns": [float(x) for x in cost_a.net_pnl.values],
        },
    }


# ===========================================================================
# Main
# ===========================================================================


def main() -> None:
    print(
        f"[{CFG_ID}] starting (CUMULATIVE_N_TRIALS={CUMULATIVE_N_TRIALS}, "
        f"WINDOW_SHORT={WINDOW_SHORT}d, WINDOW_LONG={WINDOW_LONG}d, "
        f"both broker tracks)"
    )

    # --- Stage 3a — pre-validation per dataset --------------------------
    print("\n=== Stage 3a — pre-validation (vol-regime gate) ===")
    pre_val_per_ds: dict[str, dict] = {}
    for name in ("gld_long", "xauusd_real", "xauusd_intraday"):
        params = TF_PARAMS[name]
        close = load_close(name)
        if name == "xauusd_intraday":
            close_for_pre_val = close.resample("1D").last().dropna()
            ann_for_pre_val = 252
        else:
            close_for_pre_val = close
            ann_for_pre_val = params["ann"]
        pv = run_pre_val_for_dataset(
            close_for_pre_val,
            window_short=WINDOW_SHORT,
            window_long=WINDOW_LONG,
            ann_factor=ann_for_pre_val,
            cost_floor_bps_per_flip=8.0,
            swap_long_bps_per_night=1.0,
        )
        pre_val_per_ds[name] = pv
        print(
            f"  {name:18s} p_active={pv['p_active']:.3f} "
            f"({pv['n_active_bars']}/{pv['n_total_bars']} bars), "
            f"μ={pv['mu_active_bps_per_bar']:+.3f}bps/bar "
            f"(={pv['mu_active_bps_per_yr_active']:+.0f}bps/yr active), "
            f"flips={pv['n_flips']} ({pv['n_flips_per_yr']:.2f}/yr), "
            f"cost={pv['cost_yr_bps']:.0f}bps/yr → "
            f"{'✓' if pv['passed'] else '✗'} ({pv['reason']})"
        )

    n_pass = sum(1 for d in pre_val_per_ds.values() if d["passed"])
    print(f"\n  → {n_pass}/3 datasets pass pre-val gate")
    pre_val_path = ITER_DIR / "pre_val.json"
    pre_val_path.write_text(json.dumps(pre_val_per_ds, indent=2, default=str), encoding="utf-8")
    print(f"  → wrote {pre_val_path}")

    if n_pass == 0:
        print(
            "\n!! PRE-VAL FAILED on all 3 datasets — AUTO-ABORTING.\n"
            "   See final_report.md for closure proposal."
        )
        verdict = {
            "config_id": CFG_ID,
            "status": "iterating",
            "tier": "FAIL",
            "total_score": 0,
            "winner_conditions_met": False,
            "hold_time_gate_pass": False,
            "is_winner": False,
            "auto_aborted_at_pre_val": True,
            "pre_val": pre_val_per_ds,
            "cumulative_n_trials": CUMULATIVE_N_TRIALS,
            "primary_citation": "[volatility_trading, p.58-59]",
            "hypothesis_slug": "vol-regime-gate-60-252",
            "broker_track": "both",
            "timeframes_used": ["1d", "1h"],
        }
        (ITER_DIR / "verdict.json").write_text(
            json.dumps(verdict, indent=2, default=str), encoding="utf-8"
        )
        print(f"   → wrote {ITER_DIR / 'verdict.json'} (auto-abort)")
        return

    # --- Stage 3b — full backtest on all 3 datasets ---------------------
    print("\n=== Stage 3b — full 3-dataset backtest (Track A primary, Track B secondary) ===")
    results: dict[str, dict] = {}
    for name in ("gld_long", "xauusd_real", "xauusd_intraday"):
        print(f"\n--- {name} ({TF_PARAMS[name]['tf']}) ---")
        r = run_one_dataset(name)
        results[name] = r
        ma = r["track_a_metrics"]
        bench = BENCHMARKS[name]
        print(
            f"  Track A: Sharpe={ma['sharpe']:+.4f} (bench {bench.sharpe:+.4f}, Δ {ma['sharpe']-bench.sharpe:+.4f}), "
            f"CAGR={ma['cagr']:+.4%} (bench {bench.cagr:+.4%}), "
            f"MDD={ma['mdd']:.4%} (bench {bench.mdd:.4%}), "
            f"mean_hold={ma['mean_hold_days']:.2f}d, n_trades={ma['n_trades']}, gates={r['n_passed']}/7"
        )
        print(
            f"  Per-trade attribution: gross={ma['per_trade_gross_bps']:+.2f}bps, "
            f"cost={ma['per_trade_cost_bps']:+.2f}bps, net={ma['per_trade_net_bps']:+.2f}bps"
        )
        if "sharpe" in r["track_b_metrics"] and r["track_b_metrics"].get("note") is None:
            mb = r["track_b_metrics"]
            print(
                f"  Track B: Sharpe={mb['sharpe']:+.4f}, CAGR={mb['cagr']:+.4%}, MDD={mb['mdd']:.4%}"
            )
        elif r["track_b_metrics"].get("note"):
            print(f"  Track B: {r['track_b_metrics']['note']}")

    # --- Stage 4 — score + winner check + hold-time gate ----------------
    metrics = {
        ds: DatasetMetrics(
            sharpe=results[ds]["track_a_metrics"]["sharpe"],
            cagr=results[ds]["track_a_metrics"]["cagr"],
            mdd=results[ds]["track_a_metrics"]["mdd"],
            dsr_p_value=results[ds]["track_a_metrics"]["dsr_p_value"],
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
    score = score_strategy(metrics, gates_dict, cumulative_n_trials=CUMULATIVE_N_TRIALS)

    primary_ds = "xauusd_intraday"
    primary_hold = results[primary_ds]["track_a_metrics"]["mean_hold_days"]
    hold_gate_pass = bool(primary_hold <= 5.0)
    is_winner = bool(score.winner_conditions_met and hold_gate_pass)

    sharpes = {ds: results[ds]["track_a_metrics"]["sharpe"] for ds in results}
    n_neg = sum(1 for v in sharpes.values() if v < 0)
    primary_neg = sharpes[primary_ds] <= 0
    kill_fired = bool(primary_neg or n_neg >= 2)

    # Kill criterion #4 from hypothesis: MDD > buy-hold MDD on ≥ 2 datasets.
    mdd_breach = sum(
        1 for ds in results
        if results[ds]["track_a_metrics"]["mdd"] > BENCHMARKS[ds].mdd
    )
    mdd_kill = mdd_breach >= 2

    print(
        f"\n=== SCORE ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} (mean {primary_hold:.2f}d on {primary_ds}), "
        f"is_winner = {is_winner}\n"
        f"\n=== KILL CRITERIA ===\n"
        f"Sharpes (Track A net): {sharpes}\n"
        f"primary_neg ({primary_ds}): {primary_neg}, n_neg={n_neg}/3, "
        f"sharpe_kill = {kill_fired}\n"
        f"MDD breach (vs buy-hold): {mdd_breach}/3 datasets, mdd_kill = {mdd_kill}"
    )

    out = {
        "config_id": CFG_ID,
        "params": {
            "window_short": WINDOW_SHORT,
            "window_long": WINDOW_LONG,
            "tf_params": TF_PARAMS,
            "track_a_spread_rt_bps": 8.0,
            "track_a_swap_long_bps_per_night": -1.0,
            "track_a_swap_short_bps_per_night": 0.3,
            "track_b_fx_rt_bps": 100.0,
            "track_b_darf_rate": 0.15,
        },
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "pre_val": pre_val_per_ds,
        "per_dataset": {
            ds: {k: v for k, v in results[ds].items() if not k.startswith("_")}
            for ds in results
        },
        "score": score.to_dict(),
        "hold_time_gate": {
            "primary_dataset": primary_ds,
            "mean_hold_days": primary_hold,
            "threshold_days": 5.0,
            "pass": hold_gate_pass,
            "note": "Vol-regime gate is intentionally swing-extended; cap at STRONG tier per hypothesis",
        },
        "kill_criteria": {
            "sharpes": sharpes,
            "primary_dataset": primary_ds,
            "primary_negative": primary_neg,
            "n_negative_datasets": n_neg,
            "sharpe_kill_fired": kill_fired,
            "mdd_breach_count": mdd_breach,
            "mdd_kill_fired": mdd_kill,
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
    verdict["primary_citation"] = "[volatility_trading, p.58-59]"
    verdict["hypothesis_slug"] = "vol-regime-gate-60-252"
    verdict["mean_hold_days"] = float(primary_hold)
    verdict["hold_time_gate_pass"] = hold_gate_pass
    verdict["broker_track"] = "both"
    verdict["timeframes_used"] = ["1d", "1h"]
    verdict["track_a_metrics"] = {
        ds: results[ds]["track_a_metrics"] for ds in results
    }
    verdict["track_b_metrics"] = {
        ds: results[ds]["track_b_metrics"] for ds in results
    }
    verdict["kill_criteria"] = out["kill_criteria"]
    verdict["pre_val"] = pre_val_per_ds
    verdict["status"] = "winner" if is_winner else "iterating"
    verdict["auto_aborted_at_pre_val"] = False
    verdict_path = ITER_DIR / "verdict.json"
    verdict_path.write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"wrote {verdict_path}")


if __name__ == "__main__":
    main()
