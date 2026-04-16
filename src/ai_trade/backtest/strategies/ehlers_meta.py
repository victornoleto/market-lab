"""Ehlers BP Swing with AFML meta-labeling [advances_fin_ml, §3.6, p.50-54].

Primary strategy = :class:`EhlersBPSwingStrategy`. Secondary classifier
(RandomForest) scores each primary-trigger event and trades only when
``p_act >= threshold``. Intent: boost precision enough that the Deflated
Sharpe Ratio [advances_fin_ml, ch.14] passes on SPY, where the baseline
Ehlers 0/24 trials clear DSR at p<0.05.

Pipeline
--------

1. Precompute Ehlers indicators (roofing → DCP → band-pass → AGC →
   trend).
2. Extract **primary events** — each anticipatory cross of the AGC
   oscillator through ±thresholds (same rule the baseline uses to open
   a position).
3. Build per-event **features**: ``[osc, dcp, smooth, trend, atr20,
   regime]``. These are the state the primary strategy already computes;
   AFML §3.6 recommends reusing them rather than inventing new ones.
4. Apply **triple-barrier** labels with
   ``pt_sl × trgt = atr/close`` [triple_barrier, AFML p.45-49].
5. Compute **sample weights** via concurrent-event uniqueness + return
   attribution [sample_weights, AFML p.59-69].
6. **Train/test split** by calendar — first ``train_fraction`` of the
   events fit the classifier, the rest get its predictions. The backtest
   only opens trades on events in the test range.
7. Runtime: on each bar, if the primary would enter, consult ``p_act[t]``;
   if below threshold → skip. Exits unchanged (primary owns the exit).

Determinism
-----------

Classifier is seeded (``random_state``) so re-runs reproduce. The event
set is fully determined by the Ehlers oscillator (same seed as the
primary). Training data ends at a calendar cutoff derived from
``train_fraction`` over the event index — does not peek at post-cutoff
prices or features.

Gates & grid
------------

Designed to be swept via a 5-D grid: ``(hp, lp, pct, stop, p_act)``.
Training per trial is cheap (RandomForest on ~100-300 events, 6
features). Intended runner: :func:`grid.runner.GridRunner` with
:class:`grid.ehlers_meta_config.EhlersMetaGridConfig`.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import ClassVar

import numpy as np
import pandas as pd

from ai_trade.backtest.data.adjust import adjust_ohlc
from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.indicators.ehlers_bp import band_pass
from ai_trade.backtest.indicators.ehlers_dcp import dominant_cycle_period
from ai_trade.backtest.indicators.ehlers_roofing import roofing_filter
from ai_trade.backtest.indicators.ehlers_ss import super_smoother
from ai_trade.backtest.meta.meta_labeler import MetaLabeler


def _agc_normalize(series: pd.Series, decay: float = 0.991) -> pd.Series:
    """Automatic Gain Control — identical to EhlersBPSwingStrategy's version.

    Kept local rather than imported to avoid coupling the private helper;
    behavior must match exactly [cycle_analytics, p.54-55, ch.5].
    """
    values = series.to_numpy(dtype=float, copy=True)
    n = len(values)
    peak = np.zeros(n)
    for t in range(1, n):
        peak[t] = max(abs(values[t]), decay * peak[t - 1])
    safe = np.where(peak > 1e-9, peak, 1.0)
    return pd.Series(values / safe, index=series.index, name=series.name)


def _atr(ohlc: pd.DataFrame, window: int = 20) -> pd.Series:
    """Wilder-style Average True Range, normalised by close.

    Returns ``atr / close`` so the feature is scale-invariant across
    instruments [systematic_trading, p.66-67, ch.4: pooled volatility
    estimator]. Falls back to ``|high - low| / close`` when prior close
    is missing.
    """
    high = ohlc["high"]
    low = ohlc["low"]
    close = ohlc["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = tr.rolling(window=window, min_periods=1).mean()
    return (atr / close).rename("atr20")


@dataclass
class EhlersMetaStrategy:
    """Ehlers BP Swing with RandomForest meta-label filter.

    All Ehlers-primary parameters are identical to
    :class:`EhlersBPSwingStrategy`. Meta parameters sit below the
    separator — training / barrier / threshold.
    """

    # -- Primary (Ehlers) params -----------------------------------------
    data: dict[str, pd.DataFrame]
    symbol: str = "SPY"
    hp_period: int = 48
    lp_period: int = 10
    pct_of_dcp: float = 0.90
    stop_pct: float = 0.05
    upper_threshold: float = 0.70
    lower_threshold: float = -0.70
    agc_decay: float = 0.991
    risk_pct_of_equity: float = 0.95
    period_min: int = 6
    period_max: int = 50

    # -- Meta-label params ------------------------------------------------
    p_act_threshold: float = 0.55
    train_fraction: float = 0.5
    pt: float = 2.0
    sl: float = 2.0
    vertical_bars: int = 20
    atr_window: int = 20
    sma_regime_window: int = 200
    n_estimators: int = 100
    max_depth: int | None = 5
    min_train_events: int = 20
    random_state: int = 42

    # Internal state ------------------------------------------------------
    _indicators: dict[str, pd.DataFrame] = field(init=False, default_factory=dict)
    _features: pd.DataFrame | None = field(init=False, default=None, repr=False)
    _events: pd.DataFrame | None = field(init=False, default=None, repr=False)
    _p_act: pd.Series | None = field(init=False, default=None, repr=False)
    _train_cutoff: pd.Timestamp | None = field(init=False, default=None, repr=False)
    _filter_active: bool = field(init=False, default=True)
    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.ehlers_meta"),
        repr=False,
    )

    FEATURES: ClassVar[tuple[str, ...]] = ("osc", "dcp", "smooth", "trend", "atr20", "regime")

    # -- Construction -----------------------------------------------------

    def __post_init__(self) -> None:
        if not (0 < self.stop_pct < 1):
            raise ValueError(f"stop_pct must be in (0, 1), got {self.stop_pct}")
        if self.lower_threshold >= self.upper_threshold:
            raise ValueError(
                f"lower_threshold ({self.lower_threshold}) must be strictly "
                f"less than upper_threshold ({self.upper_threshold})"
            )
        if not (0.0 <= self.p_act_threshold <= 1.0):
            raise ValueError(f"p_act_threshold must be in [0,1], got {self.p_act_threshold}")
        if not (0.0 < self.train_fraction < 1.0):
            raise ValueError(f"train_fraction must be in (0,1), got {self.train_fraction}")
        if self.symbol not in self.data:
            raise KeyError(f"symbol {self.symbol!r} not in data")

        self.data = {sym: adjust_ohlc(df) for sym, df in self.data.items()}
        self._precompute_indicators()
        self._build_events_features()
        self._fit_meta_labeler()

    def _precompute_indicators(self) -> None:
        ohlc = self.data[self.symbol]
        close = ohlc["close"]
        roofed = roofing_filter(close, self.hp_period, self.lp_period)
        dcp = dominant_cycle_period(
            roofed, period_min=self.period_min, period_max=self.period_max
        )
        bp = band_pass(roofed, dcp, pct_of_dcp=self.pct_of_dcp)
        osc = _agc_normalize(bp, decay=self.agc_decay)
        trend = super_smoother(close, self.lp_period)
        atr20 = _atr(ohlc, window=self.atr_window)
        sma = close.rolling(window=self.sma_regime_window, min_periods=1).mean()
        regime = (close > sma).astype(float).rename("regime")

        self._indicators[self.symbol] = pd.DataFrame(
            {
                "smooth": roofed,
                "dcp": dcp,
                "bp": bp,
                "osc": osc,
                "trend": trend,
                "atr20": atr20,
                "regime": regime,
            }
        )

    # -- Events + features + labels --------------------------------------

    def _detect_events(self) -> pd.DataFrame:
        """Find each anticipatory oscillator cross (long or short).

        Same rule the primary uses to open a trade — [cycle_analytics,
        p.220-221, ch.17]. Returns a frame indexed by the cross timestamp
        ``t0`` with columns ``side`` and ``t1`` (vertical barrier).
        """
        ind = self._indicators[self.symbol]
        osc = ind["osc"]
        osc_prev = osc.shift(1)

        long_mask = (osc_prev > self.lower_threshold) & (osc <= self.lower_threshold)
        short_mask = (osc_prev < self.upper_threshold) & (osc >= self.upper_threshold)

        side = pd.Series(0, index=osc.index, dtype="int64")
        side.loc[long_mask] = 1
        side.loc[short_mask] = -1
        triggers = side[side != 0]
        if triggers.empty:
            return pd.DataFrame(columns=["t1", "trgt", "side"])

        index = osc.index
        # Vertical barrier = N bars ahead (clamped to last available bar).
        positions = index.get_indexer(triggers.index)
        t1_positions = np.minimum(positions + self.vertical_bars, len(index) - 1)
        t1 = index[t1_positions]

        trgt = ind["atr20"].reindex(triggers.index).fillna(0.01)
        trgt = trgt.clip(lower=1e-4)  # avoid zero-width barriers

        return pd.DataFrame(
            {
                "t1": t1,
                "trgt": trgt.to_numpy(),
                "side": triggers.to_numpy(),
            },
            index=triggers.index,
        )

    def _extract_features(self, event_ts: pd.Index) -> pd.DataFrame:
        ind = self._indicators[self.symbol]
        feats = ind.reindex(event_ts)[list(self.FEATURES)].copy()
        return feats.fillna(0.0)

    def _build_events_features(self) -> None:
        events = self._detect_events()
        self._events = events
        if events.empty:
            self._features = pd.DataFrame(columns=list(self.FEATURES))
            return
        self._features = self._extract_features(events.index)

    def _fit_meta_labeler(self) -> None:
        events = self._events
        assert events is not None and self._features is not None

        if events.empty:
            self._p_act = pd.Series(dtype="float64", name="p_act")
            self._filter_active = False
            self._logger.warning(
                "ehlers_meta: no primary events detected — filter disabled"
            )
            return

        # Calendar-based train/test split over event index.
        n_events = len(events)
        n_train = max(1, int(n_events * self.train_fraction))
        train_events = events.iloc[:n_train]
        self._train_cutoff = train_events.index[-1]

        if n_train < self.min_train_events:
            # Not enough data to train a meaningful classifier —
            # disable the filter and let the primary run unmuted. The
            # grid runner still records this as a valid trial with
            # p_act = 1.0 everywhere.
            self._p_act = pd.Series(
                1.0, index=events.index, name="p_act", dtype="float64"
            )
            self._filter_active = False
            self._logger.warning(
                "ehlers_meta: %d train events < %d min — filter disabled",
                n_train, self.min_train_events,
            )
            return

        try:
            from sklearn.ensemble import RandomForestClassifier
        except ImportError as e:
            raise RuntimeError(
                "ehlers_meta requires scikit-learn; add to pyproject.toml"
            ) from e

        clf = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=1,  # grid runner owns parallelism
            class_weight="balanced",
        )

        close = self.data[self.symbol]["close"]
        labeler = MetaLabeler(
            close=close,
            primary_events=train_events,
            classifier=clf,
            pt_sl=(self.pt, self.sl),
        )

        train_features = self._features.loc[train_events.index]

        # Guard: classifier needs both classes present. If triple-barrier
        # labels collapse to one class on the train window, skip fitting.
        labs = labeler.labels()
        y_train = (labs["bin"] != 0).astype(int)
        if y_train.nunique() < 2:
            self._p_act = pd.Series(
                1.0, index=events.index, name="p_act", dtype="float64"
            )
            self._filter_active = False
            self._logger.warning(
                "ehlers_meta: single-class train labels — filter disabled"
            )
            return

        labeler.fit(train_features)

        all_features = self._features
        p_act_values = labeler.predict_proba_act(all_features)
        self._p_act = p_act_values

    # -- Main dispatch ----------------------------------------------------

    def on_bar(
        self,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        if self.symbol not in bars:
            return []

        bar = bars[self.symbol]
        ts = bar.timestamp
        ind = self._indicators[self.symbol]
        try:
            idx = ind.index.get_loc(ts)
        except KeyError:
            return []

        if idx < 1:
            return []

        osc_now = float(ind["osc"].iloc[idx])
        osc_prev = float(ind["osc"].iloc[idx - 1])
        trend_now = float(ind["trend"].iloc[idx])
        dcp_now = float(ind["dcp"].iloc[idx])

        pos = portfolio.positions.get(self.symbol)
        state = context.setdefault(f"ehlers_meta_state_{self.symbol}", {})

        if pos is not None:
            exit_order = self._maybe_exit(pos, bar, idx, state, trend_now)
            if exit_order is not None:
                state.clear()
                return [exit_order]
            return []

        return self._maybe_enter(
            bar, ts, idx, state, portfolio, osc_now, osc_prev, dcp_now
        )

    # -- Exit (identical to primary) --------------------------------------

    def _maybe_exit(self, pos, bar, idx, state, trend_now):
        side = pos.side
        entry_price = pos.avg_entry_price
        entry_idx = state.get("entry_idx", idx)
        bars_held = idx - entry_idx
        dcp_at_entry = state.get("dcp_at_entry", self.period_min)
        half_dcp = max(1, int(0.5 * dcp_at_entry))
        pnl_per_unit = (
            bar.close - entry_price if side == "long" else entry_price - bar.close
        )

        if side == "long" and bar.close <= entry_price * (1 - self.stop_pct):
            return Order(symbol=self.symbol, side="sell", volume=pos.volume)
        if side == "short" and bar.close >= entry_price * (1 + self.stop_pct):
            return Order(symbol=self.symbol, side="buy", volume=pos.volume)

        if side == "long" and bar.close < trend_now:
            return Order(symbol=self.symbol, side="sell", volume=pos.volume)
        if side == "short" and bar.close > trend_now:
            return Order(symbol=self.symbol, side="buy", volume=pos.volume)

        if bars_held >= half_dcp and pnl_per_unit <= 0:
            close_side = "sell" if side == "long" else "buy"
            return Order(symbol=self.symbol, side=close_side, volume=pos.volume)

        return None

    # -- Entry (meta-filtered) --------------------------------------------

    def _maybe_enter(
        self,
        bar: Bar,
        ts: pd.Timestamp,
        idx: int,
        state: dict,
        portfolio: Portfolio,
        osc_now: float,
        osc_prev: float,
        dcp_now: float,
    ) -> list[Order]:
        if math.isnan(osc_now) or math.isnan(osc_prev):
            return []

        is_long_cross = osc_prev > self.lower_threshold and osc_now <= self.lower_threshold
        is_short_cross = osc_prev < self.upper_threshold and osc_now >= self.upper_threshold
        if not (is_long_cross or is_short_cross):
            return []

        # Meta filter — only enforced outside the training window. Events
        # at or before train_cutoff are the fit set; we do not replay them.
        if self._filter_active and self._train_cutoff is not None:
            if ts <= self._train_cutoff:
                return []
            if self._p_act is None or ts not in self._p_act.index:
                return []
            p = float(self._p_act.loc[ts])
            if p < self.p_act_threshold:
                return []

        equity = portfolio.equity
        if equity <= 0:
            return []
        notional = equity * self.risk_pct_of_equity
        if bar.close <= 0:
            return []
        volume = notional / bar.close
        if volume <= 0:
            return []

        side = "buy" if is_long_cross else "sell"
        state["entry_idx"] = idx
        state["dcp_at_entry"] = dcp_now
        return [Order(symbol=self.symbol, side=side, volume=volume)]

    # -- Introspection (for tests / reports) -----------------------------

    @property
    def p_act(self) -> pd.Series | None:
        return self._p_act

    @property
    def train_cutoff(self) -> pd.Timestamp | None:
        return self._train_cutoff

    @property
    def filter_active(self) -> bool:
        return self._filter_active

    @property
    def events(self) -> pd.DataFrame:
        return self._events if self._events is not None else pd.DataFrame()
