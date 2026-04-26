"""Iter 009 — XAU/XAG pair TREND-FOLLOW (sign-flipped twin of iter 008).

Strategy
--------
* Pair instrument: dollar-neutral XAU vs XAG. Position p ∈ {-1, 0, +1}.
* p=+1 means LONG ratio = LONG gold + SHORT silver.
* p=-1 means SHORT ratio = SHORT gold + LONG silver.
* Signal: rolling z-score of log(gold/silver) over ``lookback`` bars.
* **Entry (sign-flipped from iter 008's MR)**:
    z[t] > +z_entry → p := +1 (LONG ratio expecting trend to extend UP)
    z[t] < -z_entry → p := -1 (SHORT ratio expecting trend to extend DOWN)
* **Exit (TIMEOUT-ONLY)**: bars_held > timeout → p := 0.

Why timeout-only exit
~~~~~~~~~~~~~~~~~~~~~
The pre-val measures fwd-N-bar return at every entry trigger; a
timeout-only state machine matches that measurement window exactly,
keeping the empirical pre-val maximally predictive of realised
per-trade return. (Set ``Z_EXIT = -1.0`` so ``|z|≤z_exit`` never
fires; structurally identical to a no-z-exit state machine.)

Cost model (Track A — Pepperstone CFD pair, identical to iter 008):
* Combined RT spread = 30 bps (gold 8 + silver 20 + slip 2).
* Net pair swap conservative -0.8 bps/night long / +0.5 bps/night short.

Per-TF parameters (TF-natural lookbacks; pre-committed; no grid search):
* gld_long          : 1d, lookback=60d,  timeout=10d, ann=252
* xauusd_real       : 1d, lookback=60d,  timeout=10d, ann=252
* xauusd_intraday   : 1h, lookback=60h,  timeout=24h, ann=5119

Pre-val (augmented per iter 007 GS-7 corollary, sign-flipped per
iter 008 GS-8 escape #1):
* ADF on log(ratio) per dataset (informational only; non-stationarity
  is the trend-follow signal regime, not a kill criterion)
* Cost-aware fwd-N-bar return gate: mean fwd_bps > 1.5 × 30 = 45 bps
  AND t-stat > 1.0 AND hit_rate > 0.50 AND n_events >= 30, with
  signed_fwd = +sign(z) × Δlog_ratio (sign flip vs iter 008).

Output: ``pre_val.json`` (per-dataset signal+stationarity diagnostics)
+ ``results.json`` (per-dataset metrics, gates, returns) + ``verdict.json``
(score + tier + winner check + hold-time gate).

Citations
---------
* `[algo_trading_chan, p.133, ch.6]` — time-series momentum: past
  returns positively correlate with future returns
* `[algo_trading_chan, p.151, ch.6]` — momentum strategies' regime
  fragility post-crisis (acknowledged risk for 2020+ data window)
* `[algo_trading_chan, p.153, ch.6]` — short fwd-horizon justification
  (momentum decay)
* `[algo_trading_chan, p.51-58, ch.2]` — z-score grammar on pair spreads
  (signal construction inherited; entry direction sign-flipped)
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
* `[advances_fin_ml, p.222-223]` — DSR with cumulative ``n_trials = 9``
* DEAD_ENDS GS-8 — empirical evidence (iter 008 pre-val × −1) directly
  drives this iter's hypothesis
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

ROOT = Path(__file__).resolve().parents[4]  # repo root (worktree)
sys.path.insert(0, str(ROOT / "studies" / "gold_swing_loop"))
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.validation.bootstrap import stationary_bootstrap_trades  # noqa: E402
from ai_trade.backtest.validation.dsr import dsr as dsr_func  # noqa: E402
from ai_trade.backtest.validation.dsr import sharpe_periodic  # noqa: E402
from ai_trade.backtest.validation.walk_forward import walk_forward_gate  # noqa: E402

from cost_models import apply_pepperstone_costs  # noqa: E402
from scoring import (  # noqa: E402
    BENCHMARKS,
    DatasetMetrics,
    Gates,
    score_strategy,
)

ITER_DIR = Path(__file__).resolve().parent
CFG_ID = "xau_xag_pair_trend_lb60_z2_timeoutonly_to10"

# Cumulative trial count: 8 prior iters + 1 (this) = 9.
CUMULATIVE_N_TRIALS = 9

# --- Pair cost model (identical to iter 008) --------------------------------
PAIR_SPREAD_RT_BPS = 30.0
PAIR_SWAP_LONG_BPS = -0.8
PAIR_SWAP_SHORT_BPS = +0.5

# --- Strategy parameters (pre-committed; IC-8 single cfg) -------------------
TF_PARAMS = {
    "gld_long":        {"lookback": 60, "timeout": 10, "ann": 252,  "tf": "1d"},
    "xauusd_real":     {"lookback": 60, "timeout": 10, "ann": 252,  "tf": "1d"},
    "xauusd_intraday": {"lookback": 60, "timeout": 24, "ann": 5119, "tf": "1h"},
}
Z_ENTRY = 2.0
Z_EXIT = -1.0  # never fires; effectively timeout-only exit

PAIR_PATHS = {
    "gld_long": (
        "data/tiingo/daily/prices/GLD.parquet",
        "data/tiingo/daily/prices/SLV.parquet",
    ),
    "xauusd_real": (
        "data/tiingo/daily/prices/xauusd.parquet",
        "data/tiingo/daily/prices/xagusd.parquet",
    ),
    "xauusd_intraday": (
        "data/tiingo/1hour/prices/xauusd.parquet",
        "data/tiingo/1hour/prices/xagusd.parquet",
    ),
}


# ===========================================================================
# Strategy primitives
# ===========================================================================


def pair_log_ratio(gold_close: pd.Series, silver_close: pd.Series) -> pd.Series:
    df = pd.concat({"g": gold_close, "s": silver_close}, axis=1).dropna()
    out = np.log(df["g"] / df["s"])
    out.name = "log_ratio"
    return out


def rolling_zscore(series: pd.Series, lookback: int) -> pd.Series:
    ma = series.rolling(lookback, min_periods=lookback).mean()
    sd = series.rolling(lookback, min_periods=lookback).std(ddof=1)
    z = (series - ma) / sd
    z.name = "zscore"
    return z


def pair_trend_signal(
    z: pd.Series,
    z_entry: float = 2.0,
    z_exit: float = -1.0,
    timeout: int = 10,
) -> pd.Series:
    """Signed-position state machine for pair TREND-FOLLOW (sign-flipped MR).

    State transitions (one-position-at-a-time, no pyramiding):

    * flat (0) and z[t] >  +z_entry  → enter LONG ratio  (pos = +1)  ← FLIP
    * flat (0) and z[t] <  -z_entry  → enter SHORT ratio (pos = -1)  ← FLIP
    * in position and (|z[t]| ≤ z_exit OR bars_held > timeout) → exit (pos = 0)

    With z_exit = -1.0 the |z|≤z_exit branch never fires (always false),
    so exits are timeout-only — exactly matching the pre-val fwd-N-bar
    measurement window.
    """
    pos = np.zeros(len(z), dtype=np.float64)
    state = 0
    bars_held = 0
    z_vals = z.values
    for i in range(len(z)):
        zi = z_vals[i]
        if state == 0:
            if not np.isnan(zi):
                if zi > z_entry:
                    state = +1   # ← sign flip vs iter 008 MR
                    bars_held = 1
                elif zi < -z_entry:
                    state = -1   # ← sign flip vs iter 008 MR
                    bars_held = 1
        else:
            bars_held += 1
            mean_revert = (not np.isnan(zi)) and (abs(zi) <= z_exit)
            if mean_revert or bars_held > timeout:
                state = 0
                bars_held = 0
        pos[i] = float(state)
    return pd.Series(pos, index=z.index, name="position")


def pair_gross_returns(
    position: pd.Series,
    gold_returns: pd.Series,
    silver_returns: pd.Series,
) -> pd.Series:
    """PnL[t] = pos[t-1] × (gold_ret[t] − silver_ret[t])."""
    pos_lag = position.shift(1).fillna(0.0)
    return pos_lag * (gold_returns - silver_returns)


def compute_mean_hold(position: pd.Series, ann: int) -> tuple[float, int, float]:
    pos = position.values
    in_trade = False
    starts: list[int] = []
    ends: list[int] = []
    for i, p in enumerate(pos):
        if not in_trade and p != 0:
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
    bars_per_trading_day = ann / 252.0
    mean_days = mean_bars / bars_per_trading_day if bars_per_trading_day > 0 else mean_bars
    return float(mean_days), int(len(starts)), mean_bars


# ===========================================================================
# Pre-validation (sign-flipped vs iter 008)
# ===========================================================================


def cost_aware_pre_val_gate(
    fwd_bps: np.ndarray,
    *,
    cost_floor_bps: float = 30.0,
    margin: float = 1.5,
    min_t_stat: float = 1.0,
    min_hit_rate: float = 0.50,
    min_events: int = 30,
) -> dict:
    """Augmented pre-val: magnitude > cost floor (sign-flipped from iter 008's MR test).

    Reasoning identical to iter 008's gate, applied to TREND-FOLLOW
    signed_fwd (+sign(z) × Δlog_ratio). A positive mean here means the
    spread continues in the entry direction.
    """
    arr = np.asarray(fwd_bps, dtype=np.float64)
    n = len(arr)
    if n < 1:
        return {
            "n_events": 0, "mean_fwd_bps": 0.0, "std_fwd_bps": 0.0,
            "t_stat": 0.0, "hit_rate": 0.0,
            "required_edge_bps": margin * cost_floor_bps,
            "cost_floor_bps": cost_floor_bps,
            "passed": False, "reason": "no events",
        }
    mean_bps = float(arr.mean())
    std_bps = float(arr.std(ddof=1)) if n > 1 else 0.0
    t_stat = mean_bps / (std_bps / np.sqrt(n)) if std_bps > 0 else 0.0
    hit_rate = float((arr > 0).mean())
    required_edge = margin * cost_floor_bps

    if n < min_events:
        passed, reason = False, f"insufficient events (n={n} < {min_events})"
    elif mean_bps <= 0:
        passed, reason = False, f"directional inversion (mean fwd={mean_bps:.2f} bps ≤ 0)"
    elif mean_bps <= required_edge:
        passed = False
        reason = (
            f"magnitude below cost floor: mean fwd={mean_bps:.2f} bps ≤ "
            f"required {required_edge:.2f} bps (= {margin}× cost floor {cost_floor_bps})"
        )
    elif t_stat <= min_t_stat:
        passed, reason = False, f"t-stat too low ({t_stat:.3f} ≤ {min_t_stat})"
    elif hit_rate <= min_hit_rate:
        passed, reason = False, f"hit-rate too low ({hit_rate:.3f} ≤ {min_hit_rate})"
    else:
        passed, reason = True, "passed all augmented gates"

    return {
        "n_events": n,
        "mean_fwd_bps": mean_bps,
        "std_fwd_bps": std_bps,
        "t_stat": float(t_stat),
        "hit_rate": hit_rate,
        "required_edge_bps": required_edge,
        "cost_floor_bps": cost_floor_bps,
        "min_t_stat": min_t_stat,
        "min_hit_rate": min_hit_rate,
        "min_events": min_events,
        "passed": bool(passed),
        "reason": reason,
    }


def run_pre_val_for_dataset(
    log_ratio: pd.Series,
    *,
    lookback: int,
    timeout: int,
    z_entry: float,
) -> dict:
    """Pre-val: ADF (informational) + cost-aware fwd-N-bar gate (sign-flipped).

    For TREND-FOLLOW, signed_fwd = +sign(z) × (log_ratio[t+timeout] −
    log_ratio[t]):
      z>+2 → enter LONG ratio (pos=+1) → profit if log_ratio rises
      z<-2 → enter SHORT ratio (pos=-1) → profit if log_ratio falls

    Note: ADF non-stationarity here is the SIGNAL REGIME (trend follow
    works on non-stationary series), not a kill criterion. Reported.
    """
    z = rolling_zscore(log_ratio, lookback=lookback)

    entry_mask = z.notna() & (z.abs() > z_entry)

    # SIGN-FLIP from iter 008: +sign(z) instead of -sign(z).
    fwd_log_ratio = log_ratio.shift(-timeout) - log_ratio
    sign = np.sign(z)
    signed_fwd = (sign * fwd_log_ratio).where(entry_mask & fwd_log_ratio.notna()).dropna()
    signed_fwd_bps = signed_fwd.values * 1e4

    gate = cost_aware_pre_val_gate(
        signed_fwd_bps,
        cost_floor_bps=PAIR_SPREAD_RT_BPS,
        margin=1.5,
        min_t_stat=1.0,
        min_hit_rate=0.50,
        min_events=30,
    )

    log_ratio_clean = log_ratio.dropna()
    try:
        adf_res = adfuller(log_ratio_clean.values, autolag="AIC")
        adf_stat = float(adf_res[0])
        adf_p = float(adf_res[1])
    except Exception as exc:  # pragma: no cover
        adf_stat = float("nan")
        adf_p = 1.0
        adf_res = (None, None, None, None, None, str(exc))
    adf_passed = adf_p < 0.05

    return {
        "adf": {
            "stat": adf_stat,
            "p_value": adf_p,
            "passed": adf_passed,
            "n_obs": int(len(log_ratio_clean)),
            "note": "non-stationarity is the trend-follow regime; not a kill criterion",
        },
        "cost_aware": gate,
        "n_entry_events": int(entry_mask.sum()),
        # For trend-follow, ADF passing is irrelevant; only cost-aware matters.
        "passed_either": bool(gate["passed"]),
        "passed_both": bool(gate["passed"] and adf_passed),
    }


# ===========================================================================
# Metric helpers (mirror iter 008)
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
    position: pd.Series, pair_returns: pd.Series
) -> tuple[float, float]:
    pos_pd = position.shift(1).fillna(0.0)
    pnl_pd = pos_pd * pair_returns
    eq_pd = (1.0 + pnl_pd).cumprod()
    span_yr = max((position.index[-1] - position.index[0]).days / 365.25, 1e-9)
    cagr_pd = float(eq_pd.iloc[-1] ** (1.0 / span_yr) - 1.0)
    pos_np = pos_pd.values.astype(np.float64)
    ret_np = pair_returns.values.astype(np.float64)
    pnl_np = pos_np * ret_np
    eq_np = np.cumprod(1.0 + pnl_np)
    cagr_np = float(eq_np[-1] ** (1.0 / span_yr) - 1.0)
    return cagr_pd, cagr_np


# ===========================================================================
# Per-dataset run
# ===========================================================================


def _bar_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().fillna(0.0)


def load_pair(name: str) -> tuple[pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    gold_path, silver_path = PAIR_PATHS[name]
    gold_df = pd.read_parquet(gold_path).sort_index()
    silver_df = pd.read_parquet(silver_path).sort_index()
    df = pd.concat(
        {
            "gold_close": gold_df["close"].astype(float),
            "silver_close": silver_df["close"].astype(float),
        },
        axis=1,
    ).dropna()
    log_ratio = pair_log_ratio(df["gold_close"], df["silver_close"])
    return df, df["gold_close"], df["silver_close"], log_ratio


def run_one_dataset(name: str) -> dict:
    params = TF_PARAMS[name]
    lookback = params["lookback"]
    timeout = params["timeout"]
    ann = params["ann"]
    tf = params["tf"]

    df, gold_close, silver_close, log_ratio = load_pair(name)
    z = rolling_zscore(log_ratio, lookback=lookback)
    position = pair_trend_signal(z, z_entry=Z_ENTRY, z_exit=Z_EXIT, timeout=timeout)

    gold_ret = _bar_returns(gold_close)
    silver_ret = _bar_returns(silver_close)
    pair_ret = (gold_ret - silver_ret).reindex(position.index).fillna(0.0)

    if tf == "1d":
        swap_long = PAIR_SWAP_LONG_BPS
        swap_short = PAIR_SWAP_SHORT_BPS
    elif tf == "1h":
        swap_long = PAIR_SWAP_LONG_BPS / 24.0
        swap_short = PAIR_SWAP_SHORT_BPS / 24.0
    else:
        raise ValueError(f"unknown tf: {tf}")

    cost = apply_pepperstone_costs(
        pair_ret, position,
        spread_rt_bps=PAIR_SPREAD_RT_BPS,
        swap_long_bps=swap_long,
        swap_short_bps=swap_short,
        intraday_close=False,
    )

    m_a = compute_metrics(cost.net_pnl, ann)
    mean_hold_days, n_trades, mean_hold_bars = compute_mean_hold(position, ann)
    rets_a = cost.net_pnl.dropna()

    # Gates --------------------------------------------------------------
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

    cagr_pd_gross, cagr_np_gross = cross_lib_gross_check(position, pair_ret)
    g7_diff_pp = abs(cagr_pd_gross - cagr_np_gross) * 100.0
    g7_cl = bool(g7_diff_pp <= 3.0)

    gates = Gates(
        g1_pbo=g1_pbo, g2_dsr=g2_dsr, g3_wf=g3_wf, g4_oos=g4_oos,
        g5_fwd=g5_fwd, g6_bootstrap=g6_boot, g7_crosslib=g7_cl,
    )

    gross_pnl_total = float(cost.gross_pnl.sum())
    spread_total = float(-cost.spread_cost.sum())
    swap_total = float(-cost.swap_cost.sum())
    net_total = float(cost.net_pnl.sum())
    per_trade_gross_bps = (gross_pnl_total / max(n_trades, 1)) * 1e4 if n_trades > 0 else 0.0
    per_trade_cost_bps = (-(spread_total + swap_total) / max(n_trades, 1)) * 1e4 if n_trades > 0 else 0.0
    per_trade_net_bps = (net_total / max(n_trades, 1)) * 1e4 if n_trades > 0 else 0.0

    return {
        "tf": tf,
        "params": {"lookback": lookback, "timeout": timeout, "ann": ann},
        "n_bars": int(len(df)),
        "date_range": [df.index[0].isoformat(), df.index[-1].isoformat()],
        "track_a_metrics": {
            **m_a,
            "dsr_p_value": dsr_p,
            "mean_hold_days": mean_hold_days,
            "mean_hold_bars": mean_hold_bars,
            "n_trades": n_trades,
            "n_swap_nights": cost.n_swap_nights,
            "n_weekend_holds": cost.n_weekend_holds,
            "cost_summary": cost.summary(),
            "per_trade_gross_bps": per_trade_gross_bps,
            "per_trade_cost_bps": per_trade_cost_bps,
            "per_trade_net_bps": per_trade_net_bps,
        },
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
            "index": [d.isoformat() for d in cost.net_pnl.index],
            "net_returns": [float(x) for x in cost.net_pnl.values],
        },
    }


# ===========================================================================
# Main
# ===========================================================================


def main() -> None:
    print(
        f"[{CFG_ID}] starting (CUMULATIVE_N_TRIALS={CUMULATIVE_N_TRIALS}, "
        f"PAIR_SPREAD_RT={PAIR_SPREAD_RT_BPS} bps)"
    )

    # --- Stage 3a — pre-validation per dataset --------------------------
    print("\n=== Stage 3a — pre-validation (cost-aware fwd-N-bar, sign-flipped from iter 008) ===")
    pre_val_per_ds: dict[str, dict] = {}
    for name in ("gld_long", "xauusd_real", "xauusd_intraday"):
        params = TF_PARAMS[name]
        _, _, _, log_ratio = load_pair(name)
        pv = run_pre_val_for_dataset(
            log_ratio,
            lookback=params["lookback"],
            timeout=params["timeout"],
            z_entry=Z_ENTRY,
        )
        pre_val_per_ds[name] = pv
        print(
            f"  {name:18s} ADF p={pv['adf']['p_value']:.4f} "
            f"(stat={pv['adf']['stat']:+.3f}, n={pv['adf']['n_obs']}) "
            f"| cost-aware n={pv['cost_aware']['n_events']}, "
            f"mean={pv['cost_aware']['mean_fwd_bps']:+.2f}bps, "
            f"t={pv['cost_aware']['t_stat']:+.3f}, "
            f"hit={pv['cost_aware']['hit_rate']:.3f} → "
            f"{'✓' if pv['cost_aware']['passed'] else '✗'} "
            f"({pv['cost_aware']['reason']})"
        )

    n_pass = sum(1 for d in pre_val_per_ds.values() if d["passed_either"])
    print(f"\n  → {n_pass}/3 datasets pass cost-aware gate (trend-follow direction)")
    pre_val_path = ITER_DIR / "pre_val.json"
    pre_val_path.write_text(json.dumps(pre_val_per_ds, indent=2, default=str), encoding="utf-8")
    print(f"  → wrote {pre_val_path}")

    if n_pass == 0:
        print(
            "\n!! PRE-VAL FAILED on all 3 datasets — AUTO-ABORTING.\n"
            "   See final_report.md for GS-9 closure proposal."
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
            "primary_citation": "[algo_trading_chan, p.133, ch.6]",
            "hypothesis_slug": "xau-xag-pair-trend",
            "broker_track": "pepperstone_cfd",
            "timeframes_used": ["1d", "1h"],
        }
        (ITER_DIR / "verdict.json").write_text(
            json.dumps(verdict, indent=2, default=str), encoding="utf-8"
        )
        print(f"   → wrote {ITER_DIR / 'verdict.json'} (auto-abort)")
        return

    # --- Stage 3b — full backtest on all 3 datasets ---------------------
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
            f"mean_hold={ma['mean_hold_days']:.2f}d, n_trades={ma['n_trades']}, gates={r['n_passed']}/7"
        )
        print(
            f"  Per-trade attribution: gross={ma['per_trade_gross_bps']:+.2f}bps, "
            f"cost={ma['per_trade_cost_bps']:+.2f}bps, net={ma['per_trade_net_bps']:+.2f}bps "
            f"(cost floor {PAIR_SPREAD_RT_BPS} bps RT)"
        )

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
    gates = {
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
    score = score_strategy(metrics, gates, cumulative_n_trials=CUMULATIVE_N_TRIALS)

    primary_ds = "xauusd_intraday"
    primary_hold = results[primary_ds]["track_a_metrics"]["mean_hold_days"]
    hold_gate_pass = bool(primary_hold <= 5.0)
    is_winner = bool(score.winner_conditions_met and hold_gate_pass)

    sharpes = {ds: results[ds]["track_a_metrics"]["sharpe"] for ds in results}
    n_neg = sum(1 for v in sharpes.values() if v < 0)
    primary_neg = sharpes[primary_ds] <= 0
    kill_fired = bool(primary_neg or n_neg >= 2)

    print(
        f"\n=== SCORE ===\n"
        f"total = {score.total_score}/100, tier = {score.tier.value}, "
        f"winner_conds_met = {score.winner_conditions_met}, "
        f"hold_gate_pass = {hold_gate_pass} (mean {primary_hold:.2f}d on {primary_ds}), "
        f"is_winner = {is_winner}\n"
        f"\n=== KILL CRITERION ===\n"
        f"Sharpes (Track A net): {sharpes}\n"
        f"primary_neg ({primary_ds}): {primary_neg}, n_neg={n_neg}/3, "
        f"kill_fired = {kill_fired}"
    )

    out = {
        "config_id": CFG_ID,
        "params": {
            "z_entry": Z_ENTRY,
            "z_exit": Z_EXIT,
            "exit_mode": "timeout-only (z_exit=-1.0 never fires)",
            "tf_params": TF_PARAMS,
            "pair_spread_rt_bps": PAIR_SPREAD_RT_BPS,
            "pair_swap_long_bps": PAIR_SWAP_LONG_BPS,
            "pair_swap_short_bps": PAIR_SWAP_SHORT_BPS,
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
        },
        "kill_criterion": {
            "sharpes": sharpes,
            "primary_dataset": primary_ds,
            "primary_negative": primary_neg,
            "n_negative_datasets": n_neg,
            "fired": kill_fired,
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
    verdict["primary_citation"] = "[algo_trading_chan, p.133, ch.6]"
    verdict["hypothesis_slug"] = "xau-xag-pair-trend"
    verdict["mean_hold_days"] = float(primary_hold)
    verdict["hold_time_gate_pass"] = hold_gate_pass
    verdict["broker_track"] = "pepperstone_cfd"
    verdict["timeframes_used"] = ["1d", "1h"]
    verdict["track_a_metrics"] = {
        ds: results[ds]["track_a_metrics"] for ds in results
    }
    verdict["track_b_metrics"] = {
        ds: {"note": "Track B not viable: pair trend-follow requires shorting silver leg, blocked on Inter retail US accounts (long-only constraint, INFRASTRUCTURE.md Track B)"}
        for ds in results
    }
    verdict["kill_criterion"] = out["kill_criterion"]
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
