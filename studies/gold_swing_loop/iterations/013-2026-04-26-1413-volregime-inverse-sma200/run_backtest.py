"""Iter 013 — Inverse vol-regime gate AND close > SMA(200) regime filter.

Strategy (extends iter 011 with one extra parameter)
----------------------------------------------------
* Single-asset, **LONG-ONLY**. Position[t] ∈ {0, 1}.
* Flag[t] = 1 iff (σ_60d(log_ret) < σ_252d(log_ret)) AND (close > SMA_200).
* Both inputs lagged 1 bar at execution; look-ahead-free.
* Pre-committed window_short=60, window_long=252, sma_trend_window=200.
* Single cfg per IC-8.

Citations
---------
* `[short_term_trading_strategies, p.106]` — Connors SMA(200) trend gate (PRIMARY)
* `[volatility_trading, p.58-59]` — Sinclair vol cone (iter 011 base)
* `[trading_systems_methods, p.13-14]` — Kaufman metals = low-noise → trending
* `[trading_systems_methods, p.301-310]` — Kaufman regime-conditional rules
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest
* `[advances_fin_ml, p.222-223]` — DSR with ``cumulative_n_trials = 13``
* DEAD_ENDS GS-11/GS-12 — single-stream gld_long bear-regime fix path explicitly preserved
"""

from __future__ import annotations

import importlib.util
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
ITER_011_DIR = ITER_DIR.parent / "011-2026-04-26-1334-vol-regime-gate-inverse"
CFG_ID = "vol_regime_inverse_sma200_long_only"

# Cumulative trial count: 12 prior iters + 1 (this) = 13.
CUMULATIVE_N_TRIALS = 13


# --- Strategy parameters (pre-committed; IC-8 single cfg) -------------------
WINDOW_SHORT = 60          # σ_60 (trading days)
WINDOW_LONG = 252          # σ_252 (trading days, ~1y)
SMA_TREND_WINDOW = 200     # Connors classic trend gate

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
# Re-import iter 011's primitives (avoid duplicating realized_vol code)
# ===========================================================================


def _load_iter011():
    spec = importlib.util.spec_from_file_location(
        "iter011_run_backtest", ITER_011_DIR / "run_backtest.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("iter011_run_backtest", mod)
    parent = str(ITER_011_DIR)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    spec.loader.exec_module(mod)
    return mod


_ITER011 = _load_iter011()
realized_vol = _ITER011.realized_vol
realized_vol_numpy = _ITER011.realized_vol_numpy
vol_regime_inverse_flag = _ITER011.vol_regime_inverse_flag
count_flips = _ITER011.count_flips
compute_mean_hold = _ITER011.compute_mean_hold


# ===========================================================================
# New primitives (TDD-tested in test_volregime_sma200_signal.py)
# ===========================================================================


def sma_simple(prices: pd.Series, window: int) -> pd.Series:
    """Simple moving average; NaN until ``window`` observations exist."""
    return prices.rolling(window, min_periods=window).mean().rename(
        f"sma_{window}"
    )


def sma_simple_numpy(prices: np.ndarray, window: int) -> np.ndarray:
    """Hand-rolled numpy reference for the G7 cross-lib parity check."""
    out = np.full_like(prices, np.nan, dtype=np.float64)
    for i in range(window - 1, len(prices)):
        chunk = prices[i - window + 1: i + 1]
        if np.any(np.isnan(chunk)):
            continue
        out[i] = float(np.mean(chunk))
    return out


def vol_regime_inverse_with_sma200_flag(
    prices: pd.Series,
    *,
    window_short: int = 60,
    window_long: int = 252,
    sma_trend_window: int = 200,
    ann_factor: int = 252,
) -> pd.Series:
    """Binary flag: 1 iff σ_short < σ_long AND close > SMA(sma_trend_window).

    Subset of iter 011's flag (purely restrictive). Warmup until BOTH
    σ_long AND SMA_window have enough data; warmup → 0.
    """
    inverse = vol_regime_inverse_flag(
        prices,
        window_short=window_short,
        window_long=window_long,
        ann_factor=ann_factor,
    )
    sma_trend = sma_simple(prices, window=sma_trend_window)
    above_sma = (prices > sma_trend).fillna(False).astype(int)
    flag = (inverse & above_sma).astype(int)
    flag.name = "vol_regime_inverse_sma200_flag"
    return flag


def vol_regime_inverse_with_sma200_position(
    prices: pd.Series,
    *,
    window_short: int = 60,
    window_long: int = 252,
    sma_trend_window: int = 200,
    ann_factor: int = 252,
) -> pd.Series:
    flag = vol_regime_inverse_with_sma200_flag(
        prices,
        window_short=window_short,
        window_long=window_long,
        sma_trend_window=sma_trend_window,
        ann_factor=ann_factor,
    )
    return flag.astype(float).rename("position")


# ===========================================================================
# Pre-validation (relaxed lower bound on p_active vs iter 011)
# ===========================================================================


def run_pre_val_for_dataset(
    prices: pd.Series,
    *,
    window_short: int,
    window_long: int,
    sma_trend_window: int,
    ann_factor: int,
    cost_floor_bps_per_flip: float = 8.0,
    swap_long_bps_per_night: float = 1.0,
    p_active_lower: float = 0.10,  # relaxed vs iter 011 (was 0.15) — see hypothesis kill #4
) -> dict:
    flag = vol_regime_inverse_with_sma200_flag(
        prices,
        window_short=window_short,
        window_long=window_long,
        sma_trend_window=sma_trend_window,
        ann_factor=ann_factor,
    )
    log_ret = np.log(prices / prices.shift(1))
    flag_on = flag == 1
    n_bars = int(flag_on.sum())
    n_total = int(flag.size)
    p_active = float(n_bars / n_total) if n_total > 0 else 0.0

    pos_lag = flag.shift(1).fillna(0).astype(float)
    active_returns = log_ret.where(pos_lag > 0).dropna()
    if len(active_returns) > 0:
        mu_per_bar = float(active_returns.mean())
    else:
        mu_per_bar = 0.0
    mu_per_bar_bps = mu_per_bar * 1e4
    mu_per_yr_when_active = mu_per_bar * ann_factor
    mu_per_yr_when_active_bps = mu_per_yr_when_active * 1e4

    span_yr = max((prices.index[-1] - prices.index[0]).days / 365.25, 1e-9)
    n_flips = count_flips(flag.astype(float))
    n_flips_per_yr = n_flips / span_yr

    rt_per_yr = n_flips_per_yr / 2.0
    spread_yr_bps = rt_per_yr * cost_floor_bps_per_flip
    swap_yr_bps = p_active * 365.0 * swap_long_bps_per_night
    cost_yr_bps = spread_yr_bps + swap_yr_bps

    p_active_pass = bool(p_active_lower <= p_active <= 0.70)
    mu_pass = bool(mu_per_bar > 0)
    flips_pass = bool(n_flips_per_yr <= 8.0)
    cost_pass = bool(cost_yr_bps < 0.5 * abs(mu_per_yr_when_active_bps) * p_active)

    passed = bool(p_active_pass and mu_pass and flips_pass and cost_pass)

    reason_parts = []
    if not p_active_pass:
        reason_parts.append(f"p_active={p_active:.3f} ∉ [{p_active_lower}, 0.70]")
    if not mu_pass:
        reason_parts.append(f"mu_active_bps={mu_per_bar_bps:+.3f} ≤ 0")
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
# Metric helpers (mirror iter 011)
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
    path = DATA_PATHS[name]
    df = pd.read_parquet(path).sort_index()
    return df["close"].astype(float)


def build_intraday_position(
    close_1h: pd.Series, *, window_short: int, window_long: int,
    sma_trend_window: int,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """xauusd_intraday: compute regime flag on daily-resampled closes,
    then propagate to all 1h bars within each day. Look-ahead-free:
    use PREVIOUS day's flag for all 1h bars within day d.
    """
    close_daily = close_1h.resample("1D").last().dropna()
    flag_daily = vol_regime_inverse_with_sma200_flag(
        close_daily,
        window_short=window_short,
        window_long=window_long,
        sma_trend_window=sma_trend_window,
        ann_factor=252,
    )
    flag_daily_shift = flag_daily.shift(1).fillna(0).astype(int)
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
            close,
            window_short=WINDOW_SHORT,
            window_long=WINDOW_LONG,
            sma_trend_window=SMA_TREND_WINDOW,
        )
        bar_ret = _bar_returns(close_aligned)
        flag_diag_summary = {
            "p_active_daily": float(flag_daily_diag.mean()),
            "n_flips_daily": count_flips(flag_daily_diag.astype(float)),
            "note": "daily-resampled inverse+SMA200 flag propagated to 1h bars",
        }
    else:
        position = vol_regime_inverse_with_sma200_position(
            close,
            window_short=WINDOW_SHORT,
            window_long=WINDOW_LONG,
            sma_trend_window=SMA_TREND_WINDOW,
            ann_factor=ann,
        )
        bar_ret = _bar_returns(close)
        flag_diag_summary = {
            "p_active": float(position.mean()),
            "n_flips": count_flips(position),
        }

    # ---- Track A — Pepperstone CFD ------------------------------------
    if tf == "1d":
        swap_long = -1.0
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

    # ---- Track B — Inter ETF GLD (only for daily; T+1) ----------------
    if tf == "1d":
        cost_b = apply_inter_costs_with_darf(
            bar_ret, position,
            fx_rt_bps=100.0,
            darf_rate=0.15,
        )
        m_b = compute_metrics(cost_b.net_pnl, ann)
        track_b_metrics = {
            **m_b,
            "n_swap_nights": cost_b.n_swap_nights,
            "cost_summary": cost_b.summary(),
        }
    else:
        track_b_metrics = {
            "note": "Track B not viable on intraday (T+1 settlement; daily-only)",
            "sharpe": 0.0, "cagr": 0.0, "mdd": 0.0,
        }

    mean_hold_days, n_trades, mean_hold_bars = compute_mean_hold(position, ann)

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
        "params": {
            "window_short": WINDOW_SHORT,
            "window_long": WINDOW_LONG,
            "sma_trend_window": SMA_TREND_WINDOW,
            "ann": ann,
        },
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
# Comparison vs iter 011 standalone (apples-to-apples on the SAME data)
# ===========================================================================


def _load_iter011_returns(ds: str) -> pd.Series | None:
    rj = ITER_011_DIR / "results.json"
    if not rj.exists():
        return None
    data = json.loads(rj.read_text(encoding="utf-8"))
    rs = data.get("returns_series", {}).get(ds, {})
    series = rs.get("vol_regime_inverse_60_252_long_only")
    if not series:
        return None
    idx = pd.DatetimeIndex(series["index"])
    return pd.Series(series["net_returns"], index=idx)


def comparison_vs_iter_011(results: dict) -> dict:
    """Per-dataset diff (Sharpe, CAGR, MDD, DSR p, MDD) vs iter 011 standalone."""
    iter011_verdict = ITER_011_DIR / "verdict.json"
    if not iter011_verdict.exists():
        return {"available": False}
    v11 = json.loads(iter011_verdict.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for ds in ("gld_long", "xauusd_real", "xauusd_intraday"):
        m11 = v11["metrics_used"].get(ds, {})
        m13 = results[ds]["track_a_metrics"]
        out[ds] = {
            "iter_011": {
                "sharpe": m11.get("sharpe"),
                "cagr": m11.get("cagr"),
                "mdd": m11.get("mdd"),
                "dsr_p_value": m11.get("dsr_p_value"),
            },
            "iter_013": {
                "sharpe": m13["sharpe"],
                "cagr": m13["cagr"],
                "mdd": m13["mdd"],
                "dsr_p_value": m13["dsr_p_value"],
            },
            "delta": {
                "sharpe": m13["sharpe"] - m11.get("sharpe", 0.0),
                "cagr": m13["cagr"] - m11.get("cagr", 0.0),
                "mdd": m13["mdd"] - m11.get("mdd", 0.0),
                "dsr_p_value": m13["dsr_p_value"] - m11.get("dsr_p_value", 1.0),
            },
        }
    return {"available": True, "per_dataset": out}


# ===========================================================================
# Main
# ===========================================================================


def main() -> None:
    print(
        f"[{CFG_ID}] starting (CUMULATIVE_N_TRIALS={CUMULATIVE_N_TRIALS}, "
        f"WINDOW_SHORT={WINDOW_SHORT}, WINDOW_LONG={WINDOW_LONG}, "
        f"SMA_TREND_WINDOW={SMA_TREND_WINDOW})"
    )

    # --- Stage 3a — pre-validation per dataset --------------------------
    print("\n=== Stage 3a — pre-validation (inverse vol-regime + SMA200 gate) ===")
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
            sma_trend_window=SMA_TREND_WINDOW,
            ann_factor=ann_for_pre_val,
            cost_floor_bps_per_flip=8.0,
            swap_long_bps_per_night=1.0,
            p_active_lower=0.10,
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
        print("\n!! PRE-VAL FAILED on all 3 datasets — AUTO-ABORTING.")
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
            "primary_citation": "[short_term_trading_strategies, p.106]",
            "hypothesis_slug": "volregime-inverse-sma200",
            "broker_track": "both",
            "timeframes_used": ["1d", "1h"],
        }
        (ITER_DIR / "verdict.json").write_text(
            json.dumps(verdict, indent=2, default=str), encoding="utf-8"
        )
        return

    # --- Stage 3b — full backtest ---------------------------------------
    print("\n=== Stage 3b — full 3-dataset backtest ===")
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
            f"mean_hold={ma['mean_hold_days']:.2f}d, n_trades={ma['n_trades']}, gates={r['n_passed']}/7, "
            f"DSR p={ma['dsr_p_value']:.4f}"
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

    # --- Comparison vs iter 011 ------------------------------------------
    print("\n=== Comparison vs iter 011 standalone ===")
    comp = comparison_vs_iter_011(results)
    if comp.get("available"):
        for ds, d in comp["per_dataset"].items():
            print(
                f"  {ds:18s} Sharpe Δ={d['delta']['sharpe']:+.4f}, "
                f"CAGR Δ={d['delta']['cagr']:+.4%}, "
                f"MDD Δ={d['delta']['mdd']:+.4%}, "
                f"DSR Δ={d['delta']['dsr_p_value']:+.4f}"
            )

    # --- Stage 4 — score + winner check + hold-time gate -----------------
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

    # --- Pre-committed kill criteria ------------------------------------
    iter011_verdict = json.loads(
        (ITER_011_DIR / "verdict.json").read_text(encoding="utf-8")
    )
    iter011_metrics = iter011_verdict["metrics_used"]

    # Kill #1: gld_long Sharpe drops below iter 011 baseline by > 0.05
    gld_sharpe_kill = bool(
        sharpes["gld_long"] < iter011_metrics["gld_long"]["sharpe"] - 0.05
    )
    # Kill #2: xauusd_real Sharpe drops by > 0.30 vs iter 011
    xau_real_kill = bool(
        sharpes["xauusd_real"] < iter011_metrics["xauusd_real"]["sharpe"] - 0.30
    )
    # Kill #3: gld_long active fraction drops below 10%
    gld_p_active = pre_val_per_ds["gld_long"]["p_active"]
    gld_active_kill = bool(gld_p_active < 0.10)

    any_kill = bool(gld_sharpe_kill or xau_real_kill or gld_active_kill)

    print(
        f"\n=== SCORE ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} (mean {primary_hold:.2f}d on {primary_ds}), "
        f"is_winner = {is_winner}\n"
        f"\n=== PRE-COMMITTED KILL CRITERIA ===\n"
        f"Sharpes (Track A net): {sharpes}\n"
        f"  Kill #1 gld Sharpe < {iter011_metrics['gld_long']['sharpe']-0.05:.4f}: "
        f"{gld_sharpe_kill}\n"
        f"  Kill #2 xauusd_real Sharpe < {iter011_metrics['xauusd_real']['sharpe']-0.30:.4f}: "
        f"{xau_real_kill}\n"
        f"  Kill #3 gld_long p_active < 0.10 (got {gld_p_active:.3f}): {gld_active_kill}\n"
        f"  Any kill: {any_kill}"
    )

    out = {
        "config_id": CFG_ID,
        "params": {
            "window_short": WINDOW_SHORT,
            "window_long": WINDOW_LONG,
            "sma_trend_window": SMA_TREND_WINDOW,
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
        "comparison_vs_iter_011": comp,
        "score": score.to_dict(),
        "hold_time_gate": {
            "primary_dataset": primary_ds,
            "mean_hold_days": primary_hold,
            "threshold_days": 5.0,
            "pass": hold_gate_pass,
            "note": "Inverse vol-regime + SMA200 is intentionally swing-extended; cap at STRONG tier per hypothesis",
        },
        "kill_criteria": {
            "sharpes": sharpes,
            "gld_sharpe_kill": gld_sharpe_kill,
            "xauusd_real_kill": xau_real_kill,
            "gld_active_kill": gld_active_kill,
            "any_kill": any_kill,
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
    verdict["primary_citation"] = "[short_term_trading_strategies, p.106]"
    verdict["hypothesis_slug"] = "volregime-inverse-sma200"
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
    verdict["comparison_vs_iter_011"] = comp
    verdict["status"] = "winner" if is_winner else "iterating"
    verdict["auto_aborted_at_pre_val"] = False
    verdict_path = ITER_DIR / "verdict.json"
    verdict_path.write_text(
        json.dumps(verdict, indent=2, default=str), encoding="utf-8"
    )
    print(f"wrote {verdict_path}")


if __name__ == "__main__":
    main()
