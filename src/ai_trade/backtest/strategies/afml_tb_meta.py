"""AFML triple-barrier + meta-label pipeline — V2-L3 (Phase 3.5a-V2 CFD).

Implements López de Prado's two-model scheme on a single daily CFD
instrument:

1. **Primary** — EMA-50 crossover (long-only). Events fire on up-
   crossovers (close crosses from below EMA-50 to above).
2. **Triple-barrier label** — profit-take 2×ATR, stop-loss 1×ATR,
   time-stop 20 bars. Label is ``+1`` on PT touch, ``−1`` on SL touch,
   ``0`` on vertical.
3. **Meta-label** — binary "take / skip" target ``y_meta = (bin == +1)``.
   Features at ``t0``: ``ret_5d``, ``vol_20d`` (std of daily returns),
   ``rsi_14d``, ``atr_ratio_20d`` (= ATR/close).
4. **CPCV (8 groups × 2 test groups)** — 28 combinations; each event is
   tested 7 times. Average ``predict_proba[class=1]`` across all test
   assignments yields the event-level ``p_act``.
5. **Filter** — take events with ``p_act ≥ threshold`` (default 0.55).
6. **Attribution** — equity curve built daily by summing the held-path
   returns of accepted trades, net of Pepperstone Razor RT cost
   (spread half 2 bps × 2 + commission $3.50/side = 6.6 bps + slippage
   3 bps RT = 13.6 bps per trade) and daily swap cost
   (0.005%/day long, charged on the holding notional).
7. **Metrics** — IS/OOS/FWD split (chronological 70/20/10 of event
   timeline), walk-forward 8 windows, Sharpe/CAGR/MaxDD, median hold.

Costs model citation: Phase 3.5a-V2 spec §3, matching V2-L2
``plano_a_leveraged_rotation.py`` so L3 results are comparable to L2's
Pepperstone Razor baseline.

Primary signal and meta-label citations
---------------------------------------

* Triple-barrier labels: ``[advances_fin_ml, ch.3, p.45-49]``.
* Meta-labeling (primary recall → secondary precision):
  ``[advances_fin_ml, ch.3, p.50-54]``.
* CPCV with embargo: ``[advances_fin_ml, ch.7, p.149-154, p.219-222]``.
* Hold economics (retail cost amortization → hold ≥ 1-4 weeks):
  ``[systematic_trading, p.185-188]``.
* RandomForest as a robust meta-classifier: ``[advances_fin_ml, ch.6]``
  (small tree ensemble, low variance).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

from ai_trade.backtest.meta.triple_barrier import apply_triple_barrier
from ai_trade.backtest.validation.cpcv import cpcv_splits

log = logging.getLogger(__name__)


__all__ = [
    "TRADING_DAYS_PER_YEAR",
    "AFMLTBMetaConfig",
    "AFMLTBMetaResult",
    "run_afml_tb_meta_pipeline",
]


TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class AFMLTBMetaConfig:
    """Parameters for one V2-L3 AFML triple-barrier + meta-label run."""

    primary_fast: int = 50
    barrier_tp_atr_mult: float = 2.0
    barrier_sl_atr_mult: float = 1.0
    barrier_atr_lookback: int = 20
    barrier_time_bars: int = 20

    meta_n_estimators: int = 100
    meta_max_depth: int = 5
    meta_random_state: int = 42
    meta_label_threshold_p: float = 0.55
    meta_features: tuple[str, ...] = (
        "ret_5d",
        "vol_20d",
        "rsi_14d",
        "atr_ratio_20d",
    )

    cv_n_folds: int = 8
    cv_n_test_splits: int = 2
    cv_embargo_frac: float = 0.01

    spread_half_bps: float = 2.0
    commission_round_trip_bps: float = 6.6
    slippage_bps_round_trip: float = 3.0
    swap_daily_pct_long: float = -5e-5  # -0.005% per calendar day

    direction: Literal["long_only"] = "long_only"


@dataclass
class AFMLTBMetaResult:
    """Everything the per-ticker reporter / aggregator needs."""

    daily_returns: pd.Series
    equity: pd.Series
    events: pd.DataFrame  # t1, trgt, side, bin, t1_actual, ret_gross, p_act, taken
    features: pd.DataFrame
    n_events_total: int
    n_events_taken: int
    median_hold_days: float
    cum_cost_pct: float
    cum_swap_pct: float
    cv_fold_sharpes: list[float] = field(default_factory=list)
    per_bin_counts: dict[int, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Indicator helpers


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def _true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, lookback: int) -> pd.Series:
    """Wilder ATR via exponential average of true range (alpha = 1/lookback)."""
    tr = _true_range(high, low, close)
    return tr.ewm(alpha=1.0 / lookback, adjust=False, min_periods=lookback).mean()


def _rsi(close: pd.Series, lookback: int) -> pd.Series:
    """Wilder RSI on daily closes."""
    delta = close.diff()
    up = delta.clip(lower=0.0)
    down = -delta.clip(upper=0.0)
    roll_up = up.ewm(alpha=1.0 / lookback, adjust=False, min_periods=lookback).mean()
    roll_dn = down.ewm(alpha=1.0 / lookback, adjust=False, min_periods=lookback).mean()
    rs = roll_up / roll_dn.replace(0.0, np.nan)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    return rsi.fillna(50.0)


# ---------------------------------------------------------------------------
# Event + label generation


def _generate_events(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    cfg: AFMLTBMetaConfig,
) -> tuple[pd.DataFrame, pd.Series]:
    """Generate primary-signal events with triple-barrier metadata.

    Events fire on up-crossovers of the close through EMA(primary_fast).
    Returns (events_df with columns [t1, trgt, side], atr_series).
    """
    ema = _ema(close, cfg.primary_fast)
    atr = _atr(high, low, close, cfg.barrier_atr_lookback)
    above = close > ema
    # An event fires on the first bar where ``close`` crosses above EMA.
    crossed_up = above & (~above.shift(1, fill_value=False))

    n = len(close)
    idx = close.index
    event_rows: list[dict] = []
    for i, t0 in enumerate(idx):
        if not bool(crossed_up.iloc[i]):
            continue
        # Skip events with no ATR (insufficient warmup).
        a = atr.iloc[i]
        c = close.iloc[i]
        if not np.isfinite(a) or a <= 0 or not np.isfinite(c) or c <= 0:
            continue
        t1_pos = min(i + cfg.barrier_time_bars, n - 1)
        t1 = idx[t1_pos]
        trgt = float(a) / float(c)
        event_rows.append({"t0": t0, "t1": t1, "trgt": trgt, "side": 1})

    events = pd.DataFrame(event_rows).set_index("t0") if event_rows else pd.DataFrame(
        columns=["t1", "trgt", "side"]
    )
    return events, atr


def _build_features(
    close: pd.Series,
    atr: pd.Series,
    events: pd.DataFrame,
    cfg: AFMLTBMetaConfig,
) -> pd.DataFrame:
    """Compute the 4 meta-label features at each event ``t0``."""
    daily_ret = close.pct_change()
    features = pd.DataFrame(index=events.index)
    for name in cfg.meta_features:
        if name == "ret_5d":
            features[name] = close.pct_change(5).reindex(events.index)
        elif name == "vol_20d":
            features[name] = daily_ret.rolling(20, min_periods=20).std().reindex(
                events.index
            )
        elif name == "rsi_14d":
            features[name] = _rsi(close, 14).reindex(events.index)
        elif name == "atr_ratio_20d":
            features[name] = (atr / close).reindex(events.index)
        else:
            raise ValueError(f"unknown feature: {name}")
    return features.dropna(how="any")


# ---------------------------------------------------------------------------
# CPCV meta-label scoring


def _run_cpcv_meta(
    features: pd.DataFrame,
    labels: pd.Series,
    cfg: AFMLTBMetaConfig,
) -> tuple[pd.Series, list[float]]:
    """Fit RF across CPCV splits, return (mean p_act per event, per-fold OOS auc proxies).

    ``labels`` is ``bin == +1`` aka the meta-label (profit touched).
    Each event appears in ``(C(N,k)·k) / N`` test sets; we average
    ``predict_proba[:, 1]`` across them.
    """
    from sklearn.ensemble import RandomForestClassifier

    idx = features.index
    times = pd.Series(idx, index=idx, name="t1")

    proba_sum = pd.Series(0.0, index=idx)
    proba_count = pd.Series(0, index=idx, dtype=int)
    fold_sharpes: list[float] = []

    X = features.to_numpy(dtype=float)
    y = labels.astype(int).to_numpy()

    n_combos = 0
    for train_idx, test_idx in cpcv_splits(
        times,
        n_groups=cfg.cv_n_folds,
        n_test_groups=cfg.cv_n_test_splits,
        embargo_pct=cfg.cv_embargo_frac,
    ):
        n_combos += 1
        if train_idx.size < 10 or test_idx.size < 1:
            continue
        # Avoid single-class train errors; fall back to uniform 0.5 p.
        classes = np.unique(y[train_idx])
        if classes.size < 2:
            for i in test_idx:
                proba_sum.iloc[i] += 0.5
                proba_count.iloc[i] += 1
            continue
        rf = RandomForestClassifier(
            n_estimators=cfg.meta_n_estimators,
            max_depth=cfg.meta_max_depth,
            random_state=cfg.meta_random_state,
            n_jobs=1,
        )
        rf.fit(X[train_idx], y[train_idx])
        proba = rf.predict_proba(X[test_idx])
        # Robustly locate the positive-class column.
        if proba.shape[1] == 1:
            p_pos = proba[:, 0] if rf.classes_[0] == 1 else np.zeros(len(test_idx))
        else:
            pos_col = int(np.where(rf.classes_ == 1)[0][0])
            p_pos = proba[:, pos_col]
        for off, i in enumerate(test_idx):
            proba_sum.iloc[i] += float(p_pos[off])
            proba_count.iloc[i] += 1
        # Simple fold OOS accuracy as a sanity signal (not a gate).
        preds = (p_pos >= cfg.meta_label_threshold_p).astype(int)
        if len(preds) > 0 and preds.sum() > 0:
            correct = (preds == y[test_idx]).mean()
            fold_sharpes.append(float(correct))

    if n_combos == 0:
        p_act = pd.Series(0.5, index=idx)
    else:
        p_act = proba_sum / proba_count.replace(0, np.nan)
        p_act = p_act.fillna(0.5)
    return p_act, fold_sharpes


# ---------------------------------------------------------------------------
# Attribution — equity curve


def _build_daily_equity(
    close: pd.Series,
    events: pd.DataFrame,
    cfg: AFMLTBMetaConfig,
) -> tuple[pd.Series, pd.Series, float, float]:
    """Attribute accepted-trade PnL across the daily grid.

    For each accepted event, charge fixed RT cost at the entry bar and a
    daily swap cost on every holding day. The remaining daily P&L is the
    market return path ``close.pct_change()`` between ``t0`` and
    ``t1_actual``.

    Returns ``(daily_returns, equity, cum_cost_pct, cum_swap_pct)``
    aligned to ``close.index``.
    """
    daily_ret = pd.Series(0.0, index=close.index)
    underlying_ret = close.pct_change().fillna(0.0)

    rt_cost = (
        2.0 * cfg.spread_half_bps  # round-trip spread (half × 2)
        + cfg.commission_round_trip_bps
        + cfg.slippage_bps_round_trip
    ) * 1e-4  # bps → decimal

    total_cost = 0.0
    total_swap = 0.0

    taken_idx = events.index[events["taken"].astype(bool)]
    for t0 in taken_idx:
        t1 = events.loc[t0, "t1_actual"]
        # Interval (t0, t1] — daily returns charged on the day they occur.
        slice_ = daily_ret.loc[t0:t1]
        slice_ret = underlying_ret.loc[t0:t1]
        if len(slice_) == 0:
            continue
        # First bar is the entry bar — charge RT cost there. Market
        # return on entry bar is realized intra-bar, so we include it.
        daily_ret.loc[t0] += float(slice_ret.iloc[0]) - rt_cost
        total_cost += rt_cost
        if len(slice_) > 1:
            # Subsequent bars: market return minus per-day swap cost.
            for ts in slice_.index[1:]:
                r = float(slice_ret.loc[ts])
                swap = -cfg.swap_daily_pct_long  # positive number = cost
                daily_ret.loc[ts] += r - swap
                total_swap += swap

    equity = (1.0 + daily_ret).cumprod()
    return daily_ret, equity, total_cost, total_swap


# ---------------------------------------------------------------------------
# Pipeline entry point


def run_afml_tb_meta_pipeline(
    prices: pd.DataFrame,
    cfg: AFMLTBMetaConfig | None = None,
) -> AFMLTBMetaResult:
    """Execute the full V2-L3 pipeline on one daily OHLC frame.

    Parameters
    ----------
    prices : pd.DataFrame
        Daily OHLC with columns ``{open, high, low, close, adj_close}``.
        Index is ``pd.DatetimeIndex``. ``adj_close`` is preferred for
        returns; falls back to ``close``.
    cfg : AFMLTBMetaConfig
        Pipeline parameters (defaults match the V2-L3 registry entry).
    """
    cfg = cfg or AFMLTBMetaConfig()
    if "adj_close" in prices.columns:
        close = prices["adj_close"].astype(float)
        # Rescale raw H/L to the adjusted scale so ATR and barriers share
        # a common reference — Tiingo H/L are raw prices, while adj_close
        # has splits + dividends baked in (ratio up to ~6x on EFA pre-2010).
        raw_close = prices["close"].astype(float).replace(0.0, np.nan)
        factor = (close / raw_close).replace([np.inf, -np.inf], np.nan).ffill().bfill()
    else:
        close = prices["close"].astype(float)
        factor = pd.Series(1.0, index=close.index)
    high = (prices.get("high", close).astype(float) * factor).astype(float)
    low = (prices.get("low", close).astype(float) * factor).astype(float)
    close.index = pd.DatetimeIndex(close.index)
    high.index = close.index
    low.index = close.index

    events, atr = _generate_events(high, low, close, cfg)
    if events.empty:
        log.warning("no events generated")
        daily_ret = pd.Series(0.0, index=close.index)
        equity = (1.0 + daily_ret).cumprod()
        return AFMLTBMetaResult(
            daily_returns=daily_ret,
            equity=equity,
            events=events.assign(
                bin=pd.Series(dtype=int),
                t1_actual=pd.Series(dtype="datetime64[ns]"),
                ret_gross=pd.Series(dtype=float),
                p_act=pd.Series(dtype=float),
                taken=pd.Series(dtype=bool),
            ),
            features=pd.DataFrame(),
            n_events_total=0,
            n_events_taken=0,
            median_hold_days=0.0,
            cum_cost_pct=0.0,
            cum_swap_pct=0.0,
        )

    tb = apply_triple_barrier(
        close, events, pt_sl=(cfg.barrier_tp_atr_mult, cfg.barrier_sl_atr_mult)
    )
    events = events.join(tb)  # adds bin, t1_actual, ret (gross)
    events = events.rename(columns={"ret": "ret_gross"})

    features = _build_features(close, atr, events, cfg)
    # Align events to features (drop those without full feature warmup).
    events = events.loc[features.index]

    y_meta = (events["bin"] == 1).astype(int)
    p_act, fold_acc = _run_cpcv_meta(features, y_meta, cfg)
    events["p_act"] = p_act
    events["taken"] = events["p_act"] >= cfg.meta_label_threshold_p

    daily_ret, equity, cum_cost, cum_swap = _build_daily_equity(close, events, cfg)

    taken_events = events[events["taken"]]
    if len(taken_events):
        holds = (
            pd.to_datetime(taken_events["t1_actual"])
            - pd.to_datetime(taken_events.index)
        )
        median_hold = float(holds.dt.days.median())
    else:
        median_hold = 0.0

    bin_counts = events["bin"].value_counts().to_dict()
    bin_counts_int = {int(k): int(v) for k, v in bin_counts.items()}

    return AFMLTBMetaResult(
        daily_returns=daily_ret,
        equity=equity,
        events=events,
        features=features,
        n_events_total=int(len(events)),
        n_events_taken=int(events["taken"].sum()),
        median_hold_days=median_hold,
        cum_cost_pct=float(cum_cost),
        cum_swap_pct=float(cum_swap),
        cv_fold_sharpes=fold_acc,
        per_bin_counts=bin_counts_int,
    )
