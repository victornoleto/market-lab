"""Iter 024 — Cross-cluster gold_complex (60% GLD + 40% GDX) RSI(2)<5 + SMA(200)
basket strategy.

Strategy
--------
* Apply iter 003's per-asset Connors RSI(2)<5 + SMA(5) exit + SMA(200)
  trend-filter signal independently to gold ETF (GLD) and gold-MINERS ETF (GDX).
* Aggregate at FIXED 60/40 weights (gold/gdx, GLD/XAU >= 40% per spec).
* Pepperstone Track A cost model PER LEG: gold leg 8 bps RT spread, GDX
  leg 12 bps RT spread (US-equity CFD typical, slightly wider than spot
  gold), -1 bps/night swap on long, weekend 3x.
* Long-only per asset; portfolio position in [0, 1].

Cross-cluster hypothesis: GDX has documented S&P 500 ρ ~0.45 (stock-market
beta) absent from spot gold; miner-side oversold dips fire on a partially-
different macro driver. Iter 023's GLD+SLV (within-precious-metals) closed
at IC-6 rolling-60d 96.8% (GS-23). Iter 024 tests whether cross-cluster
diversification meaningfully breaks that ceiling: target rolling exceed-frac
≤ 80% AND basket Sharpe lift ≥ +0.05 over iter 003 alone.

Datasets
--------
* PRIMARY:       gld_gdx_basket_long  = 60% GLD + 40% GDX daily, 2006-05-22 → 2026-04-15 (~19.9y)
* CORROBORATING: xau_gdx_basket       = 60% XAUUSD + 40% GDX daily, 2020-01-02 → 2026-04-15 (~6.3y)

Citations
---------
* `[risk_parity, ch.7]` — multi-asset basket weighting (PRIMARY)
* `[short_term_trading_strategies, p.105-118]` — RSI(2)+SMA(200) per-asset signal
* `[ilmanen_expected_returns, ch.10]` — gold complex (bullion vs miners) separate factor exposures
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 24
* IC-6 rolling-correlation pre-val mandate (sister loop)
* IC-7 multi-stream Markowitz weighting framework (sister loop)
* GS-23 — within-precious-metals basket extension closure (motivates this cross-cluster test)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
LOOP_DIR = ITER_DIR.parents[1]
ROOT = LOOP_DIR.parents[1]

sys.path.insert(0, str(LOOP_DIR))
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.validation.bootstrap import stationary_bootstrap_trades  # noqa: E402
from ai_trade.backtest.validation.dsr import dsr as dsr_func  # noqa: E402
from ai_trade.backtest.validation.dsr import sharpe_periodic  # noqa: E402
from ai_trade.backtest.validation.walk_forward import walk_forward_gate  # noqa: E402

from cost_models import apply_pepperstone_costs  # noqa: E402
from scoring import (  # noqa: E402
    Benchmark,
    DatasetMetrics,
    Gates,
    score_strategy_v2,
)

CFG_ID = "cross_cluster_rsi2_sma200_gld60_gdx40_basket"
# 23 cumulative + this iter = 24
CUMULATIVE_N_TRIALS = 24

WEIGHTS = {"gold": 0.60, "gdx": 0.40}
# 8 bps gold (XAUUSD spot CFD baseline); 12 bps GDX (US-equity CFD typical)
SPREADS_RT_BPS = {"gold": 8.0, "gdx": 12.0}

# Datasets: (name, gold_path, gdx_path)
DATASETS = {
    "gld_gdx_basket_long": (
        "data/tiingo/daily/prices/GLD.parquet",
        "data/tiingo/daily/prices/GDX.parquet",
    ),
    "xau_gdx_basket": (
        "data/tiingo/daily/prices/xauusd.parquet",
        "data/tiingo/daily/prices/GDX.parquet",
    ),
}


# ---------------------------------------------------------------------------
# Per-asset signal (reused unchanged from iter 003)
# ---------------------------------------------------------------------------


def wilder_rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    return (100.0 - 100.0 / (1.0 + rs)).fillna(50.0)


def connors_rsi2_signal_with_trend_filter(
    df: pd.DataFrame,
    *,
    rsi_period: int = 2,
    rsi_threshold: float = 5.0,
    sma_period: int = 5,
    sma_trend_period: int | None = 200,
) -> pd.Series:
    """RSI(2)<5 mean-reversion entry, gated by close > SMA(N_trend).
    Long-only; binary {0, 1}; identical to iter 003's helper."""
    close = df["close"].astype(float)
    rsi = wilder_rsi(close, rsi_period)
    sma = close.rolling(sma_period, min_periods=sma_period).mean()

    enter = (rsi < rsi_threshold) & (close < sma)
    if sma_trend_period is not None:
        sma_trend = close.rolling(sma_trend_period, min_periods=sma_trend_period).mean()
        trend_ok = (close > sma_trend).fillna(False)
        enter = enter & trend_ok
    exit_ = close > sma

    pos = np.zeros(len(close), dtype=np.float64)
    state = 0
    for i in range(len(close)):
        if state == 0:
            if bool(enter.iloc[i]):
                state = 1
        else:
            if bool(exit_.iloc[i]):
                state = 0
        pos[i] = state
    return pd.Series(pos, index=close.index, name="position")


# ---------------------------------------------------------------------------
# Basket aggregation
# ---------------------------------------------------------------------------


def build_basket_position(
    signals: dict[str, pd.Series],
    weights: dict[str, float],
) -> pd.Series:
    """Weighted sum of per-asset binary signals.

    Returns a series in [0, 1] with the same index as the input signals
    (which must share an index).
    """
    if set(weights) != set(signals):
        raise ValueError(
            f"weights keys {set(weights)} must equal signals keys {set(signals)} "
            f"(missing or extra)"
        )
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError(f"weights must sum to 1.0, got {sum(weights.values())}")

    keys = list(signals.keys())
    base_idx = signals[keys[0]].index
    for k in keys[1:]:
        if not signals[k].index.equals(base_idx):
            raise ValueError(f"signal indices must match across keys")

    out = pd.Series(0.0, index=base_idx, name="basket_position")
    for k, sig in signals.items():
        out = out + weights[k] * sig
    return out


def basket_buyhold_returns(
    closes: dict[str, pd.Series],
    weights: dict[str, float],
) -> pd.Series:
    """Continuous-rebalance 60/40 basket buy-hold returns."""
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError(f"weights must sum to 1.0")
    keys = list(closes.keys())
    base_idx = closes[keys[0]].index
    out = pd.Series(0.0, index=base_idx, name="basket_buyhold_returns")
    for k in keys:
        ret = closes[k].pct_change().fillna(0.0)
        out = out + weights[k] * ret
    return out


# ---------------------------------------------------------------------------
# Per-leg cost application
# ---------------------------------------------------------------------------


def compute_basket_pnl(
    returns: dict[str, pd.Series],
    signals: dict[str, pd.Series],
    weights: dict[str, float],
    spreads_rt_bps: dict[str, float],
) -> dict:
    """Apply Pepperstone cost model per leg with leg-specific spread.

    Returns dict with: net_pnl (Series), gross_pnl (Series),
    spread_total_bps (per-leg dict), swap_total_bps (per-leg dict),
    n_trades (per-leg), turnover (per-leg).
    """
    if set(returns) != set(signals) or set(returns) != set(weights):
        raise ValueError("returns/signals/weights must share the same keys")
    if set(returns) != set(spreads_rt_bps):
        raise ValueError("spreads_rt_bps must share keys with returns")

    legs: dict[str, dict] = {}
    base_idx = next(iter(returns.values())).index
    net = pd.Series(0.0, index=base_idx)
    gross = pd.Series(0.0, index=base_idx)

    for k in returns:
        pos_full = (signals[k].astype(float) * weights[k]).reindex(base_idx).fillna(0.0)
        ret = returns[k].reindex(base_idx).fillna(0.0)
        br = apply_pepperstone_costs(
            ret, pos_full,
            spread_rt_bps=spreads_rt_bps[k],
            intraday_close=False,
        )
        n_trades = int((signals[k].diff().fillna(0.0) > 0).sum())
        legs[k] = {
            "n_trades": n_trades,
            "turnover": br.total_turnover,
            "spread_cost_pnl": float(-br.spread_cost.sum()),
            "swap_cost_pnl": float(-br.swap_cost.sum()),
            "gross_pnl": float(br.gross_pnl.sum()),
            "net_pnl": float(br.net_pnl.sum()),
            "n_swap_nights": br.n_swap_nights,
            "n_weekend_holds": br.n_weekend_holds,
        }
        net = net + br.net_pnl.reindex(base_idx).fillna(0.0)
        gross = gross + br.gross_pnl.reindex(base_idx).fillna(0.0)

    return {
        "net_pnl": net,
        "gross_pnl": gross,
        "legs": legs,
        "spread_total_bps": {k: legs[k]["spread_cost_pnl"] * 1e4 for k in legs},
        "swap_total_bps": {k: legs[k]["swap_cost_pnl"] * 1e4 for k in legs},
    }


# ---------------------------------------------------------------------------
# IC-6 rolling-correlation diagnostic
# ---------------------------------------------------------------------------


def ic6_rolling_correlation_diagnostic(
    a: pd.Series,
    b: pd.Series,
    window: int = 60,
    threshold: float = 0.30,
) -> dict:
    """Rolling-window |ρ| diagnostic; return exceed-fraction at threshold."""
    a, b = a.align(b, join="inner")
    if len(a) == 0:
        return {
            "window": window, "threshold": threshold,
            "static_rho": float("nan"), "exceed_frac": float("nan"),
            "n_valid_windows": 0, "n_total": 0,
        }
    rolling_rho = a.rolling(window).corr(b).dropna()
    valid = rolling_rho.dropna()
    if len(valid) == 0:
        exceed = float("nan")
    else:
        exceed = float((valid.abs() > threshold).mean())
    static_rho = float(a.corr(b)) if len(a) > 1 else float("nan")
    return {
        "window": window, "threshold": threshold,
        "static_rho": static_rho, "exceed_frac": exceed,
        "n_valid_windows": int(len(valid)),
        "n_total": int(len(a)),
    }


# ---------------------------------------------------------------------------
# Mean-hold-time on weighted basket positions
# ---------------------------------------------------------------------------


def compute_basket_mean_hold(position: pd.Series) -> tuple[float, int]:
    """Mean hold (bars) where in_trade ⇔ position > 0 (any exposure)."""
    pos_arr = position.values.astype(float)
    in_trade = False
    starts: list[int] = []
    ends: list[int] = []
    for i, p in enumerate(pos_arr):
        if not in_trade and p > 0:
            starts.append(i)
            in_trade = True
        elif in_trade and p == 0:
            ends.append(i)
            in_trade = False
    if in_trade:
        ends.append(len(pos_arr))
    if not starts:
        return 0.0, 0
    holds = [(e - s) for s, e in zip(starts, ends)]
    return float(np.mean(holds)), int(len(starts))


# ---------------------------------------------------------------------------
# Metric helpers (per dataset)
# ---------------------------------------------------------------------------


def compute_metrics(net_pnl: pd.Series) -> dict[str, float]:
    rets = net_pnl.dropna()
    if rets.std() == 0 or len(rets) < 2:
        return {"sharpe": 0.0, "cagr": 0.0, "mdd": 0.0}
    sharpe_per = sharpe_periodic(rets.values)
    sharpe_ann = float(sharpe_per * np.sqrt(252))
    eq = (1.0 + rets).cumprod()
    span_yr = max((rets.index[-1] - rets.index[0]).days / 365.25, 1e-9)
    cagr = float(eq.iloc[-1] ** (1.0 / span_yr) - 1.0)
    cummax = eq.cummax()
    dd = (eq - cummax) / cummax
    mdd = float(-dd.min())
    return {"sharpe": sharpe_ann, "cagr": cagr, "mdd": mdd}


def measure_benchmark(closes: dict[str, pd.Series], weights: dict[str, float], label: str) -> Benchmark:
    bh = basket_buyhold_returns(closes, weights)
    m = compute_metrics(bh)
    return Benchmark(sharpe=m["sharpe"], cagr=m["cagr"], mdd=m["mdd"], label=label)


# ---------------------------------------------------------------------------
# Gate runners
# ---------------------------------------------------------------------------


def run_walk_forward(rets: pd.Series, n_windows: int = 8) -> tuple[bool, list[float], list[float]]:
    n = len(rets)
    if n < n_windows * 20:
        return False, [], []
    block = n // n_windows
    oos_returns: list[float] = []
    drawdowns: list[float] = []
    for i in range(n_windows):
        chunk = rets.iloc[i * block : (i + 1) * block]
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


def run_bootstrap(rets: pd.Series) -> tuple[bool, float, float]:
    arr = rets.dropna().values
    if len(arr) < 50 or arr.std() == 0:
        return False, 0.0, 0.0
    samples = stationary_bootstrap_trades(arr, block_mean=5, n_resamples=2000, seed=42)
    sharpes = np.array([sharpe_periodic(row) * np.sqrt(252) for row in samples])
    lo = float(np.percentile(sharpes, 0.05))
    hi = float(np.percentile(sharpes, 99.95))
    return bool(lo > 0), lo, hi


def cross_lib_check_basket(
    pnl_combined: pd.Series, gross_returns_per_leg: dict[str, pd.Series],
    signals_per_leg: dict[str, pd.Series], weights: dict[str, float],
    spreads_rt_bps: dict[str, float], pandas_cagr: float,
) -> tuple[bool, float, float]:
    """Hand-roll a numpy-only PnL computation to verify the basket aggregation."""
    base_idx = pnl_combined.index
    net_np = np.zeros(len(base_idx), dtype=np.float64)
    for k in gross_returns_per_leg:
        pos = (signals_per_leg[k].astype(float) * weights[k]).reindex(base_idx).fillna(0.0).values
        ret = gross_returns_per_leg[k].reindex(base_idx).fillna(0.0).values
        gross_pnl = np.concatenate([[0.0], pos[:-1] * ret[1:]])
        # spread cost: per-side = spread_rt/2, on |position.diff()|
        per_side = spreads_rt_bps[k] / 1e4 / 2.0
        delta = np.abs(np.diff(pos, prepend=pos[0]))
        spread_cost = delta * per_side
        # swap: -1 bps/night on long position; weekend 3x
        swap_long = -1.0 / 1e4
        swap_per_bar = np.where(pos[:-1] > 0, -pos[:-1] * swap_long, 0.0)  # long pays
        swap_per_bar = np.concatenate([[0.0], swap_per_bar])
        # crude weekend mult check via index
        if isinstance(base_idx, pd.DatetimeIndex):
            wd = base_idx.dayofweek.values
            is_mon = wd == 0
            prev_was_fri = np.concatenate([[False], wd[:-1] == 4])
            wend = is_mon & prev_was_fri
            swap_per_bar = swap_per_bar * np.where(wend, 3.0, 1.0)
        net_np = net_np + gross_pnl - spread_cost - swap_per_bar

    eq = np.cumprod(1.0 + net_np)
    span_yr = max((base_idx[-1] - base_idx[0]).days / 365.25, 1e-9)
    cagr_np = float(eq[-1] ** (1.0 / span_yr) - 1.0)
    diff_pp = abs(cagr_np - pandas_cagr) * 100.0
    return diff_pp <= 3.0, cagr_np, diff_pp


# ---------------------------------------------------------------------------
# Per-dataset run
# ---------------------------------------------------------------------------


def load_aligned_basket(name: str) -> tuple[dict[str, pd.DataFrame], pd.DatetimeIndex]:
    """Load both legs and inner-join on date index. Returns (frames_dict, joint_index)."""
    paths = DATASETS[name]
    df_gold = pd.read_parquet(ROOT / paths[0]).sort_index()
    df_gdx = pd.read_parquet(ROOT / paths[1]).sort_index()
    # Strip timezone if present, normalize to dates
    if df_gold.index.tz is not None:
        df_gold.index = df_gold.index.tz_localize(None)
    if df_gdx.index.tz is not None:
        df_gdx.index = df_gdx.index.tz_localize(None)
    df_gold.index = pd.to_datetime(df_gold.index).normalize()
    df_gdx.index = pd.to_datetime(df_gdx.index).normalize()
    df_gold = df_gold[~df_gold.index.duplicated(keep="last")]
    df_gdx = df_gdx[~df_gdx.index.duplicated(keep="last")]
    joint = df_gold.index.intersection(df_gdx.index)
    return {
        "gold": df_gold.loc[joint].copy(),
        "gdx": df_gdx.loc[joint].copy(),
    }, joint


def run_one_dataset(name: str, ic6_baselines: dict | None = None) -> dict:
    frames, joint = load_aligned_basket(name)
    closes = {k: frames[k]["close"].astype(float) for k in frames}
    returns = {k: closes[k].pct_change().fillna(0.0) for k in closes}

    # Per-asset signal
    signals = {
        k: connors_rsi2_signal_with_trend_filter(
            frames[k], rsi_period=2, rsi_threshold=5.0,
            sma_period=5, sma_trend_period=200,
        )
        for k in frames
    }

    basket_pos = build_basket_position(signals, WEIGHTS)
    pnl_out = compute_basket_pnl(returns, signals, WEIGHTS, SPREADS_RT_BPS)
    net_pnl = pnl_out["net_pnl"]

    # Benchmark: 60/40 buy-hold of same universe over same window
    bench = measure_benchmark(closes, WEIGHTS, label=f"basket 60/40 buy-hold {name}")

    # Strategy metrics
    m = compute_metrics(net_pnl)

    # Mean hold + n_trades on basket position (any exposure)
    mean_hold, n_trades_basket = compute_basket_mean_hold(basket_pos)

    # DSR (cumulative n_trials = 23) — relaxed-rules v2: primary p<0.05, corroborating p<0.20
    dsr_p = 1.0
    if net_pnl.std() > 0 and len(net_pnl) > 30:
        dsr_res = dsr_func(net_pnl.dropna().values, n_trials=CUMULATIVE_N_TRIALS)
        dsr_p = float(dsr_res.p_value)

    # Gate battery
    g1_pbo = True  # single cfg, degenerate by convention
    g1_note = "single-cfg PBO degenerate; pass by convention"

    # Determine threshold per spec rules: primary p<0.05, corroborating p<0.20
    # Decided per-call by caller; here we compute both flags
    g2_dsr_strict = bool(dsr_p < 0.05)
    g2_dsr_relaxed = bool(dsr_p < 0.20)

    g3_wf, wf_returns, wf_dds = run_walk_forward(net_pnl)

    cut = int(0.7 * len(net_pnl))
    oos_chunk = net_pnl.iloc[cut:]
    oos_sharpe = float(sharpe_periodic(oos_chunk.values) * np.sqrt(252)) if len(oos_chunk) > 1 else 0.0
    g4_oos = bool(oos_sharpe > 0)

    fwd_chunk = net_pnl[net_pnl.index >= "2022-01-01"]
    fwd_sharpe = float(sharpe_periodic(fwd_chunk.values) * np.sqrt(252)) if len(fwd_chunk) > 1 else 0.0
    g5_fwd = bool(fwd_sharpe > 0)

    g6_boot, ci_lo, ci_hi = run_bootstrap(net_pnl)

    g7_cl, cagr_np, cagr_diff = cross_lib_check_basket(
        net_pnl, returns, signals, WEIGHTS, SPREADS_RT_BPS, m["cagr"],
    )

    # IC-6 vs iter 003 (single-asset RSI MR) and iter 011 (vol regime)
    ic6_vs_iter003 = None
    ic6_vs_iter011 = None
    if ic6_baselines is not None and name in ic6_baselines:
        baselines = ic6_baselines[name]
        if "iter003" in baselines:
            ic6_vs_iter003 = ic6_rolling_correlation_diagnostic(
                net_pnl, baselines["iter003"], window=60, threshold=0.30,
            )
        if "iter011" in baselines:
            ic6_vs_iter011 = ic6_rolling_correlation_diagnostic(
                net_pnl, baselines["iter011"], window=60, threshold=0.30,
            )

    return {
        "name": name,
        "joint_window": (str(joint[0].date()), str(joint[-1].date())),
        "n_bars": int(len(joint)),
        "metrics": m,
        "benchmark": {"sharpe": bench.sharpe, "cagr": bench.cagr, "mdd": bench.mdd, "label": bench.label},
        "dsr_p_value": dsr_p,
        "mean_hold_days": mean_hold,
        "n_trades_basket": n_trades_basket,
        "n_trades_per_leg": {k: pnl_out["legs"][k]["n_trades"] for k in pnl_out["legs"]},
        "spread_cost_total_pnl_per_leg": {k: pnl_out["legs"][k]["spread_cost_pnl"] for k in pnl_out["legs"]},
        "swap_cost_total_pnl_per_leg": {k: pnl_out["legs"][k]["swap_cost_pnl"] for k in pnl_out["legs"]},
        "gates": {
            "g1_pbo": g1_pbo, "g1_note": g1_note,
            "g2_dsr": g2_dsr_strict, "g2_dsr_relaxed": g2_dsr_relaxed, "dsr_p_value": dsr_p,
            "g3_wf": g3_wf, "wf_returns": wf_returns, "wf_dds": wf_dds,
            "g4_oos": g4_oos, "oos_sharpe": oos_sharpe,
            "g5_fwd": g5_fwd, "fwd_sharpe": fwd_sharpe,
            "g6_bootstrap": g6_boot, "ci_lo": ci_lo, "ci_hi": ci_hi,
            "g7_crosslib": g7_cl, "cagr_pandas": m["cagr"], "cagr_numpy": cagr_np, "cagr_diff_pp": cagr_diff,
        },
        "ic6_vs_iter003": ic6_vs_iter003,
        "ic6_vs_iter011": ic6_vs_iter011,
        "_returns_series": {
            "index": [d.isoformat() for d in net_pnl.index],
            "net_returns": [float(x) for x in net_pnl.values],
        },
    }


# ---------------------------------------------------------------------------
# IC-6 baseline loader (iter 003 + iter 011 prior net-return series)
# ---------------------------------------------------------------------------


def load_ic6_baselines() -> dict[str, dict[str, pd.Series]]:
    """Load iter 003 and iter 011 net-return series for IC-6 diagnostic.

    Returns a nested dict ``{dataset_name: {iter_id: net_returns_series}}``
    aligned by date. iter 003 used original 3 datasets; map gld_long
    (iter 003) → gld_gdx_basket_long (iter 023 primary), since iter 003
    on gld_long is the closest single-asset comparator.

    For corroborating ``xau_gdx_basket`` (2020+), we slice iter 003's
    gld_long series to 2020+ as the comparator (same calendar window).
    """
    out: dict[str, dict[str, pd.Series]] = {}

    def _load(iter_dir_name: str, ds_key: str) -> pd.Series | None:
        path = LOOP_DIR / "iterations" / iter_dir_name / "results.json"
        if not path.exists():
            return None
        with open(path) as f:
            data = json.load(f)
        rs = data.get("returns_series", {})
        # iter 003: returns_series[ds_key][CFG_ID] = {"index": [...], "net_returns": [...]}
        if ds_key not in rs:
            return None
        cfgs = rs[ds_key]
        if isinstance(cfgs, dict):
            # find first cfg
            cfg_data = next(iter(cfgs.values()))
        else:
            cfg_data = cfgs
        idx = pd.to_datetime(cfg_data["index"]).normalize()
        vals = cfg_data["net_returns"]
        return pd.Series(vals, index=idx, name=f"{iter_dir_name}_net")

    iter003_dir = "003-2026-04-26-0228-rsi2-sma200-filter"
    iter011_dir = "011-2026-04-26-1334-vol-regime-gate-inverse"

    iter003_gld = _load(iter003_dir, "gld_long")
    iter011_gld = _load(iter011_dir, "gld_long")

    out["gld_gdx_basket_long"] = {}
    if iter003_gld is not None:
        out["gld_gdx_basket_long"]["iter003"] = iter003_gld
    if iter011_gld is not None:
        out["gld_gdx_basket_long"]["iter011"] = iter011_gld

    iter003_xau = _load(iter003_dir, "xauusd_real")
    iter011_xau = _load(iter011_dir, "xauusd_real")
    out["xau_gdx_basket"] = {}
    if iter003_xau is not None:
        out["xau_gdx_basket"]["iter003"] = iter003_xau
    if iter011_xau is not None:
        out["xau_gdx_basket"]["iter011"] = iter011_xau

    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print(f"[{CFG_ID}] running on {len(DATASETS)} basket datasets (CUMULATIVE_N_TRIALS={CUMULATIVE_N_TRIALS})")
    print(f"  weights={WEIGHTS}, spreads_rt_bps={SPREADS_RT_BPS}")

    ic6_baselines = load_ic6_baselines()
    for ds, base in ic6_baselines.items():
        avail = list(base.keys())
        print(f"  IC-6 baselines for {ds}: {avail}")

    results: dict[str, dict] = {}
    for name in DATASETS:
        print(f"\n--- {name} ---")
        r = run_one_dataset(name, ic6_baselines=ic6_baselines)
        results[name] = r
        m = r["metrics"]
        b = r["benchmark"]
        print(
            f"  metrics: Sharpe={m['sharpe']:+.4f} (bench {b['sharpe']:+.4f}, Δ {m['sharpe']-b['sharpe']:+.4f}), "
            f"CAGR={m['cagr']:+.4%} (bench {b['cagr']:+.4%}), MDD={m['mdd']:.4%} (bench {b['mdd']:.4%})"
        )
        print(
            f"  hold: mean={r['mean_hold_days']:.2f}d on basket, n_trades_basket={r['n_trades_basket']}, "
            f"per_leg={r['n_trades_per_leg']}"
        )
        print(
            f"  gates: 1={r['gates']['g1_pbo']} 2={r['gates']['g2_dsr']}(p={r['gates']['dsr_p_value']:.3f},rlx={r['gates']['g2_dsr_relaxed']}) "
            f"3={r['gates']['g3_wf']} 4={r['gates']['g4_oos']}(oos_Sh={r['gates']['oos_sharpe']:+.3f}) "
            f"5={r['gates']['g5_fwd']}(fwd_Sh={r['gates']['fwd_sharpe']:+.3f}) "
            f"6={r['gates']['g6_bootstrap']}(CI_lo={r['gates']['ci_lo']:+.3f}) "
            f"7={r['gates']['g7_crosslib']}(diff_pp={r['gates']['cagr_diff_pp']:.6f})"
        )
        if r["ic6_vs_iter003"]:
            d = r["ic6_vs_iter003"]
            print(f"  IC-6 vs iter003: static_rho={d['static_rho']:+.3f}, rolling-60d exceed_frac={d['exceed_frac']*100:.1f}% (n_valid={d['n_valid_windows']})")
        if r["ic6_vs_iter011"]:
            d = r["ic6_vs_iter011"]
            print(f"  IC-6 vs iter011: static_rho={d['static_rho']:+.3f}, rolling-60d exceed_frac={d['exceed_frac']*100:.1f}% (n_valid={d['n_valid_windows']})")

    # ------------------------------------------------------------------
    # Score with score_strategy_v2 (new benchmarks for new datasets)
    # ------------------------------------------------------------------
    metrics: dict[str, DatasetMetrics] = {}
    gates_v2: dict[str, Gates] = {}
    bms: dict[str, Benchmark] = {}
    for ds in results:
        r = results[ds]
        metrics[ds] = DatasetMetrics(
            sharpe=r["metrics"]["sharpe"], cagr=r["metrics"]["cagr"],
            mdd=r["metrics"]["mdd"], dsr_p_value=r["dsr_p_value"],
        )
        # For corroborating, use relaxed DSR threshold via g2_dsr_relaxed
        is_primary = ds == "gld_gdx_basket_long"
        g2 = r["gates"]["g2_dsr"] if is_primary else r["gates"]["g2_dsr_relaxed"]
        gates_v2[ds] = Gates(
            g1_pbo=r["gates"]["g1_pbo"], g2_dsr=g2,
            g3_wf=r["gates"]["g3_wf"], g4_oos=r["gates"]["g4_oos"],
            g5_fwd=r["gates"]["g5_fwd"], g6_bootstrap=r["gates"]["g6_bootstrap"],
            g7_crosslib=r["gates"]["g7_crosslib"],
        )
        bms[ds] = Benchmark(
            sharpe=r["benchmark"]["sharpe"], cagr=r["benchmark"]["cagr"],
            mdd=r["benchmark"]["mdd"], label=r["benchmark"]["label"],
        )

    score = score_strategy_v2(
        metrics=metrics, gates=gates_v2,
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
        declared_primary="gld_gdx_basket_long",
        declared_corroborating=["xau_gdx_basket"],
        benchmarks=bms,
    )

    # Hold-time gate (short_swing: 2-10 trading days)
    primary_hold = results["gld_gdx_basket_long"]["mean_hold_days"]
    hold_gate_pass = bool(2.0 <= primary_hold <= 10.0)
    is_winner = bool(score.winner_conditions_met and hold_gate_pass)

    # Pre-committed kill criteria evaluation
    primary_sh = results["gld_gdx_basket_long"]["metrics"]["sharpe"]
    iter003_gld_sh = 0.30  # iter 003 net Sh on gld_long (from BASE_MEMORY)
    sh_lift_vs_iter003 = primary_sh - iter003_gld_sh

    ic6_v003 = results["gld_gdx_basket_long"].get("ic6_vs_iter003") or {}
    ic6_v011 = results["gld_gdx_basket_long"].get("ic6_vs_iter011") or {}
    rolling_rho_v003 = ic6_v003.get("exceed_frac", 0.0) * 100 if ic6_v003 else 0.0
    rolling_rho_v011 = ic6_v011.get("exceed_frac", 0.0) * 100 if ic6_v011 else 0.0

    primary_dsr = results["gld_gdx_basket_long"]["dsr_p_value"]
    primary_g6 = results["gld_gdx_basket_long"]["gates"]["g6_bootstrap"]
    primary_ci_lo = results["gld_gdx_basket_long"]["gates"]["ci_lo"]

    # Cross-cluster IC-6 threshold relaxed from iter 023's 95% bar to 80%:
    # the cross-cluster hypothesis is precisely that miner-side dips diverge
    # from gold-side dips at least 20% of rolling windows. Iter 023 (within-PM)
    # measured 96.8% at 95% threshold; iter 024 must beat 80% to falsify GS-23.
    kills = {
        "kill_1_sh_lt_0_30": bool(primary_sh < 0.30),
        "kill_2_sh_lift_lt_0_05": bool(sh_lift_vs_iter003 < 0.05),
        "kill_3_ic6_rho_v003_gt_80pct": bool(rolling_rho_v003 > 80.0),
        "kill_4_g6_boot_fail": bool(not primary_g6),
        "kill_3b_ic6_rho_v011_gt_30pct": bool(rolling_rho_v011 > 30.0),
        "kill_5_dsr_p_gt_0_30": bool(primary_dsr > 0.30),
    }
    n_kills_fired = sum(kills.values())

    print(
        f"\n=== SCORE ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} (mean_hold {primary_hold:.2f}d on PRIMARY ∈ [2,10]?), "
        f"is_winner = {is_winner}\n"
        f"\n=== KILLS ===\n"
        f"  primary Sh = {primary_sh:+.4f}, lift vs iter003 = {sh_lift_vs_iter003:+.4f}\n"
        f"  IC-6 rolling vs iter003 = {rolling_rho_v003:.1f}%, vs iter011 = {rolling_rho_v011:.1f}%\n"
        f"  primary DSR p = {primary_dsr:.4f}, G6 boot = {primary_g6} (CI_lo={primary_ci_lo:+.3f})\n"
        f"  kills fired: {n_kills_fired} of {len(kills)}: {[k for k,v in kills.items() if v]}\n"
    )

    out = {
        "config_id": CFG_ID,
        "rules_version": "2026-04-26-relaxed-r1",
        "params": {
            "weights": WEIGHTS,
            "spreads_rt_bps": SPREADS_RT_BPS,
            "rsi_period": 2, "rsi_threshold": 5.0, "sma_period": 5,
            "sma_trend_period": 200,
            "swap_long_bps_per_night": -1.0,
            "long_only_per_asset": True,
            "broker_track": "pepperstone_cfd",
            "universe": "gold_complex",
            "hold_time_track": "short_swing",
            "declared_primary": "gld_gdx_basket_long",
            "declared_corroborating": ["xau_gdx_basket"],
        },
        "cumulative_n_trials": CUMULATIVE_N_TRIALS,
        "per_dataset": {
            ds: {k: v for k, v in results[ds].items() if not k.startswith("_")}
            for ds in results
        },
        "score": score.to_dict(),
        "hold_time_gate": {
            "primary_dataset": "gld_gdx_basket_long",
            "mean_hold_days": primary_hold,
            "track": "short_swing", "bounds": [2.0, 10.0],
            "pass": hold_gate_pass,
        },
        "kill_criteria": {
            "primary_sharpe": primary_sh,
            "iter003_gld_sharpe_baseline": iter003_gld_sh,
            "sh_lift_vs_iter003": sh_lift_vs_iter003,
            "ic6_rolling_v_iter003_pct": rolling_rho_v003,
            "ic6_rolling_v_iter011_pct": rolling_rho_v011,
            "primary_dsr_p_value": primary_dsr,
            "primary_g6_bootstrap_pass": primary_g6,
            "primary_g6_ci_lo": primary_ci_lo,
            "kills": kills,
            "n_kills_fired": n_kills_fired,
        },
        "is_winner": is_winner,
        "returns_series": {
            ds: {CFG_ID: results[ds]["_returns_series"]} for ds in results
        },
        "benchmarks_snapshot": {
            ds: results[ds]["benchmark"] for ds in results
        },
    }
    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {out_path}")

    verdict = score.to_dict()
    verdict["configs_tested"] = 1
    verdict["primary_citation"] = "[risk_parity, ch.7]"
    verdict["hypothesis_slug"] = "cross-cluster-gld-gdx-basket"
    verdict["mean_hold_days"] = float(primary_hold)
    verdict["hold_time_gate_pass"] = hold_gate_pass
    verdict["broker_track"] = "pepperstone_cfd"
    verdict["timeframes_used"] = ["1d"]
    verdict["universe"] = "gold_complex"
    verdict["weights"] = WEIGHTS
    verdict["track_a_metrics"] = {ds: results[ds]["metrics"] for ds in results}
    verdict["kills"] = out["kill_criteria"]
    verdict["status"] = "winner" if is_winner else "iterating"
    verdict_path = ITER_DIR / "verdict.json"
    verdict_path.write_text(json.dumps(verdict, indent=2, default=str), encoding="utf-8")
    print(f"wrote {verdict_path}")


if __name__ == "__main__":
    main()
