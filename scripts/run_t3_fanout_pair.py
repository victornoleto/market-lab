#!/usr/bin/env python3
"""Phase 3.5a — Lead T3 fan-out per-pair runner.

Processes EXACTLY ONE pair from the T3 registry, runs the 3 pair-trade
configs (OLS rolling hedge, Kalman z_exit=0, Kalman z_exit=0.5), writes
``<pair>.json`` + ``<pair>.md`` atomically, and updates the registry
(pop pending → append done → advance status).

Protocol: ``docs/self_improvement/fanout_protocol.md`` §3.

Cointegration / pair-trade theory
---------------------------------
- Engle-Granger two-step cointegration: ``[algo_trading_chan, p.42-54, ch.2]``.
- Bollinger-band pair-trade z-score entry/exit: ``[algo_trading_chan, p.71-73, ch.3]``.
- Kalman dynamic hedge-ratio δ=1e-4, Ve=1e-3: ``[algo_trading_chan, p.75-80, ch.3]``.
- Overfit warning for KF state-space on pair data: ``[machine_trading, p.76-79, ch.3]``.
- 5-gate (PBO/DSR/WF): ``[advances_fin_ml, ch.7, p.208-211]``.
- Hold ≤ 5d swap-kill on CFD: ``[systematic_trading, p.185-188]``.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

log = logging.getLogger("ai_trade.phase3_5a.t3_fanout")

# ---------------------------------------------------------------------------
# Cost model — pair CFD at Pepperstone Razor tier.
# Two legs per trade; spread + commission charged on each leg on open and
# close. Symmetric swap conservative 0.5bp/day per leg while held.

_HALF_SPREAD_BPS = {
    "forex":    2.0,
    "fx_cross": 3.0,
    "metal":    5.0,
    "index":    5.0,
    "equity":  10.0,
}
_COMMISSION_PER_SIDE_USD = 3.5
_SWAP_RATE_PER_DAY = 0.00005  # 0.5 bp/day symmetric — conservative.

PERIODS_PER_YEAR_1H_FX = 252 * 24

# Split windows (same as T1/T2 for Phase 3.5a).
WINDOW_FULL = (pd.Timestamp("2020-01-06"), pd.Timestamp("2026-04-14"))
WINDOW_IS   = (pd.Timestamp("2020-01-06"), pd.Timestamp("2023-12-31"))
WINDOW_OOS  = (pd.Timestamp("2024-01-01"), pd.Timestamp("2025-12-31"))
WINDOW_FWD  = (pd.Timestamp("2026-01-01"), pd.Timestamp("2026-04-14"))

PAIR_META: Dict[str, Dict[str, Any]] = {
    "audusd_nzdusd":  {"legs": ("audusd", "nzdusd"),  "asset_class": "forex",    "freq": "1hour"},
    "eurusd_eurgbp":  {"legs": ("eurusd", "eurgbp"),  "asset_class": "forex",    "freq": "1hour"},
    "eurusd_gbpusd":  {"legs": ("eurusd", "gbpusd"),  "asset_class": "forex",    "freq": "1hour"},
    "spy_qqq":        {"legs": ("SPY",    "QQQ"),     "asset_class": "equity",   "freq": "1hour"},
    "usdjpy_usdchf":  {"legs": ("usdjpy", "usdchf"),  "asset_class": "fx_cross", "freq": "1hour"},
    "xauusd_xagusd":  {"legs": ("xauusd", "xagusd"),  "asset_class": "metal",    "freq": "1hour"},
}


# ---------------------------------------------------------------------------
# Atomic I/O helpers (mirror T2 runner).

def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _atomic_write_json(path: Path, data: Any) -> None:
    _atomic_write_text(path, json.dumps(data, indent=2, default=str) + "\n")


# ---------------------------------------------------------------------------
# Hedge-ratio estimators.

def _rolling_ols_beta(y: np.ndarray, x: np.ndarray, lookback: int) -> np.ndarray:
    """OLS rolling β for y ~ β * x + α over window ``lookback``.

    Returns array of length len(y); β[:lookback] = NaN.
    Uses the closed-form β = Cov(x, y) / Var(x) on each window.
    """
    n = len(y)
    out = np.full(n, np.nan, dtype=float)
    if n < lookback:
        return out
    # Incremental sums for vectorised rolling covariance.
    y_s = pd.Series(y)
    x_s = pd.Series(x)
    mean_x = x_s.rolling(lookback).mean()
    mean_y = y_s.rolling(lookback).mean()
    xy = (x_s * y_s).rolling(lookback).mean()
    xx = (x_s * x_s).rolling(lookback).mean()
    cov = xy - mean_x * mean_y
    var = xx - mean_x * mean_x
    beta = cov / var.replace(0, np.nan)
    out[:] = beta.to_numpy()
    return out


def _kalman_dynamic_beta(
    y: np.ndarray, x: np.ndarray, *, delta: float = 1e-4, Ve: float = 1e-3
) -> np.ndarray:
    """Chan ch.3 Kalman recursion for β_t: y_t = β_t x_t + ε.

    State = β_t (random walk); process noise Q = δ/(1-δ) P_{t-1}; obs
    noise Ve. Initialised with β_0 = OLS on first 60 bars to avoid the
    first dozen bars swinging wildly. Returns β_t at each t (causal: uses
    y_t, x_t from the current bar only — no look-ahead).
    """
    n = len(y)
    out = np.full(n, np.nan, dtype=float)
    warmup = 60
    if n <= warmup:
        return out
    y0, x0 = y[:warmup], x[:warmup]
    mx, my = float(np.mean(x0)), float(np.mean(y0))
    var_x = float(np.mean((x0 - mx) ** 2))
    cov_xy = float(np.mean((x0 - mx) * (y0 - my)))
    beta = cov_xy / var_x if var_x > 1e-12 else 1.0
    P = 1.0
    q_factor = delta / (1.0 - delta)
    for t in range(warmup, n):
        x_t, y_t = float(x[t]), float(y[t])
        # Predict (random walk): β stays, P grows by process noise.
        P_pred = P + q_factor * P
        # Innovation + variance.
        e = y_t - beta * x_t
        S = x_t * x_t * P_pred + Ve
        K = P_pred * x_t / S if S > 1e-12 else 0.0
        beta = beta + K * e
        P = (1.0 - K * x_t) * P_pred
        out[t] = beta
    return out


# ---------------------------------------------------------------------------
# Cointegration test (Engle-Granger two-step) on IS window.

def _engle_granger_pvalue(y: np.ndarray, x: np.ndarray) -> Tuple[float, float]:
    """Run Engle-Granger on (y, x). Returns (adf_stat, pvalue).

    Step 1: OLS β̂ from y on x (no intercept drop — use const).
    Step 2: ADF on residuals (no constant, no trend — residuals are
    mean-zero by construction).
    """
    from statsmodels.tsa.stattools import adfuller
    n = len(y)
    if n < 200:
        return float("nan"), 1.0
    X = np.column_stack([np.ones(n), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    try:
        stat, p, *_ = adfuller(resid, regression="n", autolag="AIC")
        return float(stat), float(p)
    except Exception as exc:
        log.warning("Engle-Granger ADF failed: %s", exc)
        return float("nan"), 1.0


# ---------------------------------------------------------------------------
# Pair backtest — causal, vectorised trade loop.

def _run_pair_backtest(
    df_y: pd.DataFrame, df_x: pd.DataFrame, cfg: Dict[str, Any],
    half_spread_bps_y: float, half_spread_bps_x: float,
    swap_rate_per_day: float, commission_usd: float, initial_cash: float,
) -> Dict[str, Any]:
    """Run one pair-trade config over the full aligned window.

    Returns dict with equity_curve (pd.Series), trades (list of dicts),
    hedge_series (pd.Series of β_t), spread_series, z_series.
    """
    # Align on common timestamps — pair trade needs simultaneous bars.
    joined = pd.concat(
        {"y": df_y["close"], "x": df_x["close"]}, axis=1, join="inner"
    ).dropna()
    if len(joined) < 300:
        return {"empty": True, "equity_curve": pd.Series(dtype=float),
                "trades": [], "hedge_series": pd.Series(dtype=float),
                "spread_series": pd.Series(dtype=float),
                "z_series": pd.Series(dtype=float)}
    y = joined["y"].to_numpy(dtype=float)
    x = joined["x"].to_numpy(dtype=float)
    idx = joined.index

    hedge_method = cfg["hedge_method"]
    hedge_lookback = int(cfg.get("hedge_lookback", 120))
    z_lookback     = int(cfg.get("zscore_lookback", 120))
    z_entry        = float(cfg["z_entry"])
    z_exit         = float(cfg["z_exit"])
    z_stop         = float(cfg.get("stop_loss_z", 3.5))

    if hedge_method == "ols_rolling":
        beta = _rolling_ols_beta(y, x, hedge_lookback)
    elif hedge_method == "kalman":
        beta = _kalman_dynamic_beta(
            y, x,
            delta=float(cfg.get("kalman_delta", 1e-4)),
            Ve=float(cfg.get("kalman_Ve", 1e-3)),
        )
    else:
        raise ValueError(f"unknown hedge_method {hedge_method!r}")

    spread = y - beta * x
    spread_s = pd.Series(spread, index=idx)
    mean_s = spread_s.rolling(z_lookback).mean()
    std_s  = spread_s.rolling(z_lookback).std(ddof=0)
    z = (spread_s - mean_s) / std_s.replace(0, np.nan)
    z_np = z.to_numpy(dtype=float)

    # Causal trade loop. Position state uses signals from the PREVIOUS
    # bar (i.e. decide at close of t-1, execute at close of t), so no
    # look-ahead. β snapshot at entry is held until exit.
    n = len(idx)
    equity = np.full(n, initial_cash, dtype=float)
    direction = 0     # +1 long spread, -1 short spread, 0 flat
    shares_y = 0.0
    shares_x = 0.0
    beta_entry = 0.0
    entry_idx = -1
    trades: List[Dict[str, Any]] = []
    bar_equity = float(initial_cash)

    # Costs — convert bps to fractional.
    hs_y = half_spread_bps_y / 10_000.0
    hs_x = half_spread_bps_x / 10_000.0
    swap_hour = swap_rate_per_day / 24.0  # applied per bar on notional

    def _close_trade(t_now: int) -> None:
        nonlocal direction, shares_y, shares_x, bar_equity
        # Close at y[t], x[t] with half-spread against.
        # Long spread: sell Y (price-half_spread), buy X (price+half_spread)
        # Short spread: buy Y (price+half_spread), sell X (price-half_spread)
        exit_price_y = y[t_now] * (1 - hs_y) if direction == 1 else y[t_now] * (1 + hs_y)
        exit_price_x = x[t_now] * (1 + hs_x) if direction == 1 else x[t_now] * (1 - hs_x)
        pnl_y = shares_y * (exit_price_y - entry_y_cost)
        pnl_x = shares_x * (exit_price_x - entry_x_cost)
        # Commission exit (per side, both legs).
        bar_equity_local = bar_equity + pnl_y + pnl_x - 2 * commission_usd
        trades.append({
            "entry_time": idx[entry_idx].isoformat(),
            "exit_time":  idx[t_now].isoformat(),
            "direction": int(direction),
            "beta_entry": float(beta_entry),
            "z_entry": float(z_np[entry_idx]) if np.isfinite(z_np[entry_idx]) else 0.0,
            "z_exit":  float(z_np[t_now])    if np.isfinite(z_np[t_now])    else 0.0,
            "hold_bars": int(t_now - entry_idx),
            "hold_days": (idx[t_now] - idx[entry_idx]).total_seconds() / 86400.0,
            "pnl": float(pnl_y + pnl_x - 2 * commission_usd),
            "equity_after": float(bar_equity_local),
        })
        bar_equity = bar_equity_local
        direction = 0
        shares_y = shares_x = 0.0

    # Track entry prices INCLUDING cost impact so PnL = shares * (exit - entry_cost).
    entry_y_cost = 0.0
    entry_x_cost = 0.0

    for t in range(1, n):
        # Mark-to-market if in position using bar close.
        if direction != 0:
            # MTM PnL for the bar (using prev equity reference is not needed;
            # we recompute every bar from shares * (close - entry_cost)).
            mtm_y = shares_y * (y[t] - entry_y_cost)
            mtm_x = shares_x * (x[t] - entry_x_cost)
            # Swap debit for holding 1 bar: charge on gross notional at entry.
            notional_entry = abs(shares_y) * entry_y_cost + abs(shares_x) * entry_x_cost
            swap_cost = swap_hour * notional_entry
            equity[t] = bar_equity + mtm_y + mtm_x - swap_cost * (t - entry_idx)
            # Note: equity[t] reflects mark-to-market + cumulative swap drag
            # while the position is open.
        else:
            equity[t] = bar_equity

        zt = z_np[t]
        if not np.isfinite(zt) or not np.isfinite(beta[t]):
            continue

        # Exit rules (priority over entry).
        if direction == 1:
            # Long spread: close when z ≥ -z_exit (mean-revert) or z ≤ -z_stop.
            if zt >= -z_exit or zt <= -z_stop:
                _close_trade(t)
                continue
        elif direction == -1:
            if zt <= z_exit or zt >= z_stop:
                _close_trade(t)
                continue

        # Entry rules (only when flat).
        if direction == 0:
            b = float(beta[t])
            if not np.isfinite(b):
                continue
            abs_b = abs(b)
            notional_total = 0.95 * bar_equity
            c = notional_total / (1.0 + abs_b)
            if c <= 0:
                continue
            if zt <= -z_entry:
                # Long spread: buy Y, short β·X.
                direction = 1
                entry_y_cost = y[t] * (1 + hs_y)
                entry_x_cost = x[t] * (1 - hs_x)
                shares_y = c / entry_y_cost
                shares_x = -np.sign(b) * abs_b * c / entry_x_cost
                beta_entry = b
                entry_idx = t
                # Debit commissions on entry (2 legs).
                bar_equity_pre = bar_equity
                bar_equity = bar_equity - 2 * commission_usd
                equity[t] = bar_equity
            elif zt >= z_entry:
                # Short spread: sell Y, buy β·X.
                direction = -1
                entry_y_cost = y[t] * (1 - hs_y)
                entry_x_cost = x[t] * (1 + hs_x)
                shares_y = -c / entry_y_cost
                shares_x = np.sign(b) * abs_b * c / entry_x_cost
                beta_entry = b
                entry_idx = t
                bar_equity = bar_equity - 2 * commission_usd
                equity[t] = bar_equity

    # Force-close any open trade at the final bar.
    if direction != 0:
        _close_trade(n - 1)
        equity[n - 1] = bar_equity

    equity_s = pd.Series(equity, index=idx, name="equity")
    return {
        "empty": False,
        "equity_curve": equity_s,
        "trades": trades,
        "hedge_series": pd.Series(beta, index=idx, name="beta"),
        "spread_series": spread_s,
        "z_series": z,
    }


# ---------------------------------------------------------------------------
# Metrics helpers.

def _annualized_sharpe(equity: pd.Series, ppy: int) -> float:
    if len(equity) < 2:
        return 0.0
    r = equity.pct_change().dropna()
    if r.std(ddof=0) <= 0 or len(r) < 2:
        return 0.0
    return float(np.sqrt(ppy) * r.mean() / r.std(ddof=0))


def _max_drawdown(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return float(dd.min())


def _cagr(final: float, initial: float, years: float) -> float:
    if initial <= 0 or years <= 0 or final <= 0:
        return 0.0
    return (final / initial) ** (1.0 / years) - 1.0


def _slice_equity(equity: pd.Series, trades: List[Dict[str, Any]],
                  start: pd.Timestamp, end: pd.Timestamp,
                  initial_cash: float, ppy: int) -> Dict[str, Any]:
    """Compute metrics on a window slice of the equity curve.

    Rebases slice to start at `initial_cash` so CAGR is comparable
    across windows. n_trades counted by entry_time ∈ [start, end+1d].
    """
    mask = (equity.index >= start) & (equity.index <= end + pd.Timedelta(days=1))
    eq_win = equity[mask]
    if len(eq_win) < 10:
        return dict(label="", start=str(start.date()), end=str(end.date()),
                    n_bars=len(eq_win), sharpe=0.0, cagr_pct=0.0,
                    max_dd_pct=0.0, final_equity=initial_cash,
                    n_trades=0, median_hold_days=0.0, median_hold_bars=0)
    # Rebase so the slice starts at initial_cash regardless of prior PnL.
    base = float(eq_win.iloc[0])
    if base <= 0:
        base = initial_cash
    eq_rebased = eq_win / base * initial_cash

    window_trades = [
        t for t in trades
        if start <= pd.Timestamp(t["entry_time"]) <= end + pd.Timedelta(days=1)
    ]
    holds_d = [t["hold_days"] for t in window_trades] if window_trades else []
    holds_b = [t["hold_bars"] for t in window_trades] if window_trades else []
    years = len(eq_rebased) / ppy
    return dict(
        start=str(start.date()), end=str(end.date()),
        n_bars=len(eq_rebased),
        sharpe=round(_annualized_sharpe(eq_rebased, ppy), 4),
        cagr_pct=round(_cagr(float(eq_rebased.iloc[-1]),
                             initial_cash, years) * 100, 3),
        max_dd_pct=round(_max_drawdown(eq_rebased) * 100, 3),
        final_equity=round(float(eq_rebased.iloc[-1]), 2),
        n_trades=len(window_trades),
        median_hold_days=round(float(np.median(holds_d)) if holds_d else 0.0, 3),
        median_hold_bars=int(np.median(holds_b)) if holds_b else 0,
    )


def _wf_verdict(equity: pd.Series, min_windows: int = 8,
                max_dd_each: float = 0.25,
                min_ratio: float = 6 / 8) -> Tuple[str, int, int]:
    if len(equity) < min_windows * 2:
        return "reject", 0, min_windows
    chunks = np.array_split(equity.values, min_windows)
    n_profitable = 0
    dd_fail = False
    for ch in chunks:
        if len(ch) < 2:
            continue
        start_v, end_v = float(ch[0]), float(ch[-1])
        ret = (end_v - start_v) / start_v if start_v != 0 else 0.0
        if ret > 0:
            n_profitable += 1
        peak = np.maximum.accumulate(ch)
        dd = float(((ch - peak) / peak).min())
        if abs(dd) > max_dd_each:
            dd_fail = True
    if dd_fail:
        return "reject", n_profitable, min_windows
    verdict = "pass" if n_profitable >= int(np.ceil(min_ratio * min_windows)) else "reject"
    return verdict, n_profitable, min_windows


def _pbo_and_dsr(equities: Dict[str, pd.Series], n_blocks: int = 10) -> Dict[str, Any]:
    from ai_trade.backtest.validation.dsr import psr
    from ai_trade.backtest.validation.pbo import pbo as run_pbo

    df = pd.concat(equities, axis=1).ffill().dropna()
    rets = df.pct_change().dropna()
    pbo_result = None
    pbo_pass = True
    if len(rets) >= n_blocks * 2 and rets.shape[1] >= 2:
        nb = n_blocks if n_blocks % 2 == 0 else n_blocks - 1
        try:
            pbo_result = run_pbo(rets.values.astype(float), n_blocks=nb)
            pbo_pass = float(pbo_result.pbo) < 0.5
        except Exception as exc:
            log.warning("PBO failed: %s", exc)
            pbo_pass = False

    dsr_out = {}
    for name, eq in equities.items():
        r = eq.pct_change().dropna().to_numpy(dtype=float)
        if len(r) < 3 or r.std(ddof=0) <= 0:
            dsr_out[name] = {"p_value": 1.0, "psr": 0.0}
            continue
        psr_val = float(psr(r, benchmark=0.0))
        p_val = 1.0 - psr_val
        dsr_out[name] = {"p_value": round(p_val, 6), "psr": round(psr_val, 6)}
    return {
        "pbo": round(float(pbo_result.pbo), 4) if pbo_result is not None else None,
        "pbo_pass": bool(pbo_pass),
        "dsr": dsr_out,
    }


# ---------------------------------------------------------------------------
# SPY benchmark block (daily, aligned to strategy window).

def _build_spy_block(full_equities: Dict[str, pd.Series], cash: float) -> Dict[str, Any]:
    try:
        from ai_trade.backtest.metrics.standard_report import (
            build_spy_benchmark, compare_vs_spy, load_spy_series,
        )
        spy = load_spy_series()
        first_eq = next(iter(full_equities.values()))
        strat_daily = first_eq.resample("D").last().dropna()
        spy_b = build_spy_benchmark(
            spy_series=spy, initial_capital=cash,
            window_start=strat_daily.index[0], window_end=strat_daily.index[-1],
            periods_per_year=252,
        )
        cmp = compare_vs_spy(strat_daily, spy_b.equity_curve, periods_per_year=252)
        return {
            "spy_return_pct": round(spy_b.return_pct * 100, 3),
            "spy_cagr_pct":   round(spy_b.cagr_pct * 100, 3),
            "spy_maxdd_pct":  round(spy_b.max_drawdown_pct * 100, 3),
            "spy_sharpe":     round(spy_b.sharpe, 3),
            "excess_return_pct": round(cmp.excess_return_pct * 100, 3),
            "excess_cagr_pct":   round(cmp.excess_cagr_pct * 100, 3),
            "information_ratio": round(cmp.information_ratio, 3),
            "correlation":       round(cmp.correlation, 4),
            "beta":              round(cmp.beta, 4),
            "note": "Strategy first-config equity resampled daily; SPY from Tiingo cache",
        }
    except Exception as exc:
        log.warning("SPY benchmark block failed: %s", exc)
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Per-ticker (pair) orchestrator.

def _run_pair(pair: str, registry_path: Path, iter_num: int, cash: float) -> Dict[str, Any]:
    from ai_trade.backtest.sweeps.registry import (
        load_registry, validate_schema_v1, pop_pending,
        append_done, advance_status, atomic_write_registry,
    )
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage

    reg = load_registry(registry_path)
    validate_schema_v1(reg)
    if reg["status"] not in ("pending", "sweeping"):
        raise RuntimeError(
            f"registry status {reg['status']!r} — cannot sweep; expected pending/sweeping"
        )
    if pair not in reg["tickers_pending"]:
        raise RuntimeError(
            f"pair {pair!r} not in tickers_pending {reg['tickers_pending']}"
        )
    if reg["tickers_pending"][0] != pair:
        raise RuntimeError(
            f"head-of-queue is {reg['tickers_pending'][0]!r} but asked {pair!r}"
        )

    meta = PAIR_META.get(pair)
    if meta is None:
        raise RuntimeError(f"no pair metadata for {pair!r}")
    leg_y, leg_x = meta["legs"]
    asset_class = meta["asset_class"]
    frequency = meta["freq"]

    storage = TiingoStorage(root="data/tiingo")
    try:
        df_y = storage.read(leg_y, frequency=frequency)
    except KeyError as exc:
        raise RuntimeError(f"leg Y {leg_y!r} not in Tiingo cache: {exc}") from exc
    try:
        df_x = storage.read(leg_x, frequency=frequency)
    except KeyError as exc:
        raise RuntimeError(f"leg X {leg_x!r} not in Tiingo cache: {exc}") from exc

    df_y = df_y[(df_y.index >= WINDOW_FULL[0]) &
                (df_y.index <= WINDOW_FULL[1] + pd.Timedelta(days=1))]
    df_x = df_x[(df_x.index >= WINDOW_FULL[0]) &
                (df_x.index <= WINDOW_FULL[1] + pd.Timedelta(days=1))]
    joined_idx = df_y.index.intersection(df_x.index)
    n_bars = len(joined_idx)
    if n_bars < 500:
        raise RuntimeError(
            f"only {n_bars} shared bars for {pair} — insufficient for backtest"
        )

    # Cointegration on IS window only (gate check, not trading filter).
    is_mask_y = (df_y.index >= WINDOW_IS[0]) & (df_y.index <= WINDOW_IS[1])
    is_mask_x = (df_x.index >= WINDOW_IS[0]) & (df_x.index <= WINDOW_IS[1])
    is_y = df_y.loc[is_mask_y, "close"].to_numpy(dtype=float)
    is_x_raw = df_x.loc[is_mask_x, "close"]
    # Align on intersection inside IS.
    is_joined = pd.concat({"y": df_y["close"], "x": df_x["close"]}, axis=1, join="inner")
    is_joined = is_joined[(is_joined.index >= WINDOW_IS[0]) & (is_joined.index <= WINDOW_IS[1])]
    adf_stat, eg_p = _engle_granger_pvalue(
        is_joined["y"].to_numpy(dtype=float),
        is_joined["x"].to_numpy(dtype=float),
    )
    cointegrated = eg_p < 0.05

    half_bps_y = _HALF_SPREAD_BPS[asset_class]
    half_bps_x = _HALF_SPREAD_BPS[asset_class]
    ppy = PERIODS_PER_YEAR_1H_FX

    configs_out: List[Dict[str, Any]] = []
    full_equities: Dict[str, pd.Series] = {}

    for cfg in reg["configs"]:
        log.info("--- %s | %s ---", pair, cfg["name"])
        bt = _run_pair_backtest(
            df_y=df_y, df_x=df_x, cfg=cfg,
            half_spread_bps_y=half_bps_y, half_spread_bps_x=half_bps_x,
            swap_rate_per_day=_SWAP_RATE_PER_DAY,
            commission_usd=_COMMISSION_PER_SIDE_USD,
            initial_cash=cash,
        )
        if bt["empty"]:
            configs_out.append({
                "name": cfg["name"], "type": cfg["type"],
                "params": {k: v for k, v in cfg.items()
                           if k not in {"name", "type", "citation"}},
                "error": "insufficient aligned bars",
            })
            continue
        equity = bt["equity_curve"]
        trades = bt["trades"]

        metrics = {}
        for label, (s, e) in [
            ("full", WINDOW_FULL), ("is", WINDOW_IS),
            ("oos", WINDOW_OOS), ("fwd", WINDOW_FWD),
        ]:
            m = _slice_equity(equity, trades, s, e, cash, ppy)
            m["label"] = label
            metrics[label] = m
            log.info("  [%s] sharpe=%.2f cagr=%.2f%% mdd=%.2f%% "
                     "trades=%d med_hold_d=%.2f",
                     label.upper(), m["sharpe"], m["cagr_pct"], m["max_dd_pct"],
                     m["n_trades"], m["median_hold_days"])

        wf_verdict, wf_wins, wf_total = _wf_verdict(equity)
        configs_out.append({
            "name": cfg["name"], "type": cfg["type"],
            "params": {k: v for k, v in cfg.items()
                       if k not in {"name", "type", "citation"}},
            "metrics_is":  metrics["is"],
            "metrics_oos": metrics["oos"],
            "metrics_fwd": metrics["fwd"],
            "metrics_full": metrics["full"],
            "wf": {"verdict": wf_verdict, "n_profitable": wf_wins,
                   "n_windows": wf_total},
        })
        full_equities[cfg["name"]] = equity

    if not full_equities:
        raise RuntimeError(f"no config produced an equity curve for {pair}")

    cross = _pbo_and_dsr(full_equities)
    for c in configs_out:
        if "error" in c:
            continue
        name = c["name"]
        dsr_p = cross["dsr"].get(name, {}).get("p_value", 1.0)
        c["dsr"] = cross["dsr"].get(name, {"p_value": 1.0, "psr": 0.0})
        oos_sharpe = c["metrics_oos"]["sharpe"]
        fwd_sharpe = c["metrics_fwd"]["sharpe"]
        oos_hold = c["metrics_oos"]["median_hold_days"]
        gates = {
            "pbo_pass": bool(cross["pbo_pass"]),
            "dsr_pass": bool(dsr_p < 0.05),
            "wf_pass":  bool(c["wf"]["verdict"] == "pass"),
            "oos_block_pass": bool(oos_sharpe > 0),
            "fwd_stress_pass": bool(fwd_sharpe > 0),
            "hold_le_5d_pass": bool(0.0 < oos_hold <= 5.0),
            "cointegration_pass": bool(cointegrated),
        }
        gates["any_pass"] = all(gates.values())
        c["gates"] = gates

    spy_block = _build_spy_block(full_equities, cash)
    non_error = [c for c in configs_out if "error" not in c]
    best = max(non_error,
               key=lambda c: (c["metrics_oos"]["sharpe"], c["metrics_fwd"]["sharpe"]))
    any_pass = any(c.get("gates", {}).get("any_pass", False) for c in configs_out)

    summary = {
        "pair": pair,
        "legs": {"y": leg_y, "x": leg_x},
        "asset_class": asset_class,
        "frequency": frequency,
        "window": {
            "start": str(WINDOW_FULL[0].date()),
            "end":   str(WINDOW_FULL[1].date()),
            "n_bars_aligned": int(n_bars),
        },
        "cointegration_is": {
            "adf_stat": None if np.isnan(adf_stat) else round(adf_stat, 4),
            "engle_granger_p": round(eg_p, 6),
            "cointegrated_at_5pct": bool(cointegrated),
        },
        "costs_model": {
            "half_spread_bps_y": half_bps_y,
            "half_spread_bps_x": half_bps_x,
            "commission_per_side_usd": _COMMISSION_PER_SIDE_USD,
            "swap_daily_pct": _SWAP_RATE_PER_DAY,
            "citation": "pepperstone razor tier (docs/investment-mandate.md §3)",
        },
        "cross_config": {"pbo": cross["pbo"], "pbo_pass": cross["pbo_pass"]},
        "configs": configs_out,
        "best_config": best["name"],
        "best_sharpe_oos": best["metrics_oos"]["sharpe"],
        "best_cagr_oos":   best["metrics_oos"]["cagr_pct"],
        "best_maxdd_oos":  best["metrics_oos"]["max_dd_pct"],
        "best_median_hold_days_oos": best["metrics_oos"]["median_hold_days"],
        "any_pass_5gate": any_pass,
        "benchmark_spy": spy_block,
    }

    base = registry_path.parent
    json_path = base / f"{pair}.json"
    md_path   = base / f"{pair}.md"
    _atomic_write_json(json_path, summary)
    _atomic_write_text(md_path, _render_md(summary))

    done_entry = {
        "ticker": pair,
        "frequency": frequency,
        "window_start": str(WINDOW_FULL[0].date()),
        "window_end":   str(WINDOW_FULL[1].date()),
        "iter": int(iter_num),
        "n_configs_tested": len(non_error),
        "best_config": best["name"],
        "best_sharpe_oos": best["metrics_oos"]["sharpe"],
        "best_cagr": best["metrics_oos"]["cagr_pct"] / 100.0,
        "best_maxdd": best["metrics_oos"]["max_dd_pct"] / 100.0,
        "any_pass_5gate": any_pass,
        "median_hold_days": best["metrics_oos"]["median_hold_days"],
        "cointegrated_at_5pct": bool(cointegrated),
        "engle_granger_p": round(eg_p, 6),
        "result_file_md":   str(md_path),
        "result_file_json": str(json_path),
    }
    _, new_reg = pop_pending(reg)
    new_reg = append_done(new_reg, done_entry)
    new_reg = advance_status(new_reg)
    atomic_write_registry(str(registry_path), new_reg)
    log.info("Registry updated: status=%s pending=%d done=%d",
             new_reg["status"], len(new_reg["tickers_pending"]),
             len(new_reg["tickers_done"]))
    return summary


def _render_md(summary: Dict[str, Any]) -> str:
    p = summary["pair"]
    legs = summary["legs"]
    coint = summary["cointegration_is"]
    lines = [
        f"# {p.upper()} 1h — T3 cointegration pair-trade",
        "",
        f"**Legs:** Y=`{legs['y']}` / X=`{legs['x']}` | "
        f"**Asset class:** {summary['asset_class']}",
        f"**Window:** {summary['window']['start']} → {summary['window']['end']} "
        f"({summary['window']['n_bars_aligned']} aligned bars, 1h)",
        f"**Costs:** half_spread={summary['costs_model']['half_spread_bps_y']}bps/leg, "
        f"swap={summary['costs_model']['swap_daily_pct']*100:.4f}%/day/leg, "
        f"commission=${summary['costs_model']['commission_per_side_usd']}/side",
        "",
        f"**Best config:** `{summary['best_config']}` — "
        f"**{'PASS 5-gate' if summary['any_pass_5gate'] else 'NO PASS'}**",
        "",
        "## Cointegration (IS 2020-2023)",
        f"- Engle-Granger ADF stat: **{coint['adf_stat']}** | p-value: "
        f"**{coint['engle_granger_p']:.4f}** | Cointegrated @ 5%: "
        f"**{'✓' if coint['cointegrated_at_5pct'] else '✗'}**",
        "",
        "## Cross-config gates",
        f"- PBO across {len(summary['configs'])} configs: "
        f"**{summary['cross_config']['pbo']}** (pass={summary['cross_config']['pbo_pass']})",
        "",
        "## All configs — OOS metrics + 5-gate",
        "",
        "| Config | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | "
        "DSR p | WF k/N | Coint | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |",
        "|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for c in summary["configs"]:
        if "error" in c:
            lines.append(
                f"| `{c['name']}` | ERROR | — | — | — | — | — | — | — | — | — | — | **skip** |"
            )
            continue
        oos = c["metrics_oos"]
        g = c["gates"]
        dsr_p = c["dsr"]["p_value"]
        wf = c["wf"]
        wf_str = f"{wf['n_profitable']}/{wf['n_windows']}"
        lines.append(
            f"| `{c['name']}` | "
            f"{oos['sharpe']:.2f} | {oos['cagr_pct']:.2f} | {oos['max_dd_pct']:.2f} | "
            f"{oos['n_trades']} | {oos['median_hold_days']:.2f} | "
            f"{dsr_p:.3f} | {wf_str} | "
            f"{'✓' if g['cointegration_pass'] else '✗'} | "
            f"{'✓' if g['oos_block_pass'] else '✗'} | "
            f"{'✓' if g['fwd_stress_pass'] else '✗'} | "
            f"{'✓' if g['hold_le_5d_pass'] else '✗'} | "
            f"**{'PASS' if g['any_pass'] else 'fail'}** |"
        )
    lines.append("")
    lines.append("## Per-config window breakdown")
    for c in summary["configs"]:
        if "error" in c:
            continue
        lines.append("")
        lines.append(f"### {c['name']}")
        lines.append("")
        lines.append(
            "| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |"
        )
        lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|")
        for lbl in ("full", "is", "oos", "fwd"):
            w = c[f"metrics_{lbl}"] if lbl != "full" else c["metrics_full"]
            lines.append(
                f"| {lbl.upper()} | {w['start']} | {w['end']} | {w['n_bars']} | "
                f"{w['sharpe']:.2f} | {w['cagr_pct']:.2f} | {w['max_dd_pct']:.2f} | "
                f"{w['n_trades']} | {w['median_hold_days']:.2f} |"
            )
    lines.append("")
    lines.append("## Benchmark — SPY buy & hold (same window)")
    spy = summary["benchmark_spy"]
    if "error" in spy:
        lines.append(f"_SPY benchmark unavailable: {spy['error']}_")
    else:
        lines.append(
            f"- SPY Return / CAGR / MaxDD / Sharpe: **{spy['spy_return_pct']:.2f}%** / "
            f"**{spy['spy_cagr_pct']:.2f}%/yr** / **{spy['spy_maxdd_pct']:.2f}%** / "
            f"**{spy['spy_sharpe']:.3f}**"
        )
        lines.append(
            f"- Strategy vs SPY — Excess CAGR: **{spy['excess_cagr_pct']:+.2f}%** | "
            f"IR: **{spy['information_ratio']:+.3f}** | "
            f"Corr: **{spy['correlation']:+.3f}** | Beta: **{spy['beta']:+.3f}**"
        )
        lines.append(f"- _{spy['note']}_")
    lines.append("")
    lines.append("## Citations")
    lines.append("- Engle-Granger cointegration (ADF on OLS residuals): "
                 "`[algo_trading_chan, p.42-54, ch.2]`")
    lines.append("- Bollinger-band pair-trade entry/exit: "
                 "`[algo_trading_chan, p.71-73, ch.3]`")
    lines.append("- Kalman dynamic hedge-ratio δ=1e-4, Ve=1e-3: "
                 "`[algo_trading_chan, p.75-80, ch.3]`")
    lines.append("- KF state-space overfit warning (EWA-EWC): "
                 "`[machine_trading, p.76-79, ch.3]`")
    lines.append("- 5-gate (PBO/DSR/WF): `[advances_fin_ml, ch.7, p.208-211]`")
    lines.append("- Hold ≤ 5d swap-kill: `[systematic_trading, p.185-188]`")
    return "\n".join(lines) + "\n"


def _parse_args(argv=None):
    ap = argparse.ArgumentParser(description="T3 fan-out per-pair runner")
    ap.add_argument("--pair", required=True,
                    help="pair id (must be head-of-queue in the registry)")
    ap.add_argument("--registry", type=Path,
                    default=Path("reports/phase3_5a/t3_intraday_pairs_statarb/registry.json"))
    ap.add_argument("--iter", dest="iter_num", type=int, required=True,
                    help="current iteration number (for registry done entry)")
    ap.add_argument("--cash", type=float, default=100_000.0)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout),
                  logging.FileHandler("logs/grid.log", mode="a")],
    )
    args = _parse_args(argv)
    summary = _run_pair(args.pair, args.registry, args.iter_num, args.cash)
    log.info("DONE: %s best=%s any_pass_5gate=%s",
             args.pair, summary["best_config"], summary["any_pass_5gate"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
