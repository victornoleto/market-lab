"""VolExpansionBreakoutStrategy — multi-asset momentum orchestrator.

Orchestrates DonchianBreakout + YangZhangCone (regime gate) + VolTargetSizer +
ExitManager per symbol, maintaining independent per-symbol position state in
the shared ``context`` dict passed by the Runner.

Performance note: YangZhangCone.read() is O(n) per call because it rebuilds
the full sigma history. Calling it once per bar per symbol naively yields
O(n²) total.  __post_init__ pre-caches one RegimeReading per timestamp so
on_bar() is O(1) per symbol per bar (after warmup).

References
----------
- Entry channel: Donchian breakout [trading_systems_methods, p.353]
- Regime filter: Yang-Zhang cone percentile [volatility_trading, p.58-60]
- Sizing: Carver vol-targeting [systematic_trading, p.144, p.159]
- Exits: opposite channel, time-stop, disaster-stop [systematic_trading, p.212]
"""

from __future__ import annotations

import collections
import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.strategies.vol_expansion_breakout._breakout_signal import (
    BreakoutDirection,
    DonchianBreakout,
)
from ai_trade.backtest.strategies.vol_expansion_breakout._exit_manager import (
    ExitManager,
    ExitReason,
    PositionState,
)
from ai_trade.backtest.strategies.vol_expansion_breakout._regime_filter import (
    RegimeReading,
    YangZhangCone,
)
from ai_trade.backtest.strategies.vol_expansion_breakout._vol_target_sizer import (
    VolTargetSizer,
)

_logger = logging.getLogger("ai_trade.strategy.vol_expansion")

_STATE_KEY_PREFIX = "vol_expansion_state"


def _state_key(symbol: str) -> str:
    return f"{_STATE_KEY_PREFIX}_{symbol}"


@dataclass
class VolExpansionBreakoutStrategy:
    """Multi-asset momentum strategy gated by a Yang-Zhang volatility cone.

    Parameters
    ----------
    data:
        Full OHLCV DataFrame per symbol (pre-loaded at construction). Must
        contain columns ``open``, ``high``, ``low``, ``close``, ``volume``
        indexed by ``pd.Timestamp``.
    symbol_specs:
        Per-symbol metadata; currently ``{"bars_per_year": int}``.
    n_entry:
        Donchian channel lookback for breakout entry [trading_systems_methods, p.353].
    n_exit:
        Donchian channel lookback for opposite-side exit [trading_systems_methods, p.353].
    cone_lookback:
        Number of historical YZ readings that form the cone
        [volatility_trading, p.58-60].
    yz_window:
        Rolling window (bars) for the Yang-Zhang estimator
        [volatility_trading, p.22-23, Eq.2.17a].
    k_filter:
        Percentile below which regime is considered "quiet" (entry allowed)
        [volatility_trading, p.58-60].
    target_vol_annual:
        Target annualised P&L volatility fraction for position sizing
        [systematic_trading, p.144, p.159].
    max_hold_hours:
        Hard wall-clock time cap before forced exit [tiingo-service spec §1.4].
    disaster_n_sigma:
        Sigma multiple for the disaster stop loss [systematic_trading, p.212].
    ref_hold_bars:
        Reference holding period in bars used to scale per-bar vol to the
        disaster threshold [systematic_trading, ch.13].
    """

    data: dict[str, pd.DataFrame]
    symbol_specs: dict[str, dict]

    # Grid knobs
    n_entry: int = 20
    n_exit: int = 10

    # Fixed params
    cone_lookback: int = 800
    yz_window: int = 20
    k_filter: float = 33.0
    target_vol_annual: float = 0.10
    max_hold_hours: float = 48.0
    disaster_n_sigma: float = 4.0
    ref_hold_bars: int = 24

    # Internal — set in __post_init__
    _breakout: DonchianBreakout = field(init=False, repr=False)
    _sizer: VolTargetSizer = field(init=False, repr=False)
    _exit_mgr: ExitManager = field(init=False, repr=False)
    # Pre-cached regime readings: symbol → pd.Series[bool] indexed by timestamp
    _regime_cache: dict[str, pd.Series] = field(init=False, default_factory=dict, repr=False)
    # Pre-cached annual sigma: symbol → pd.Series[float] indexed by timestamp
    _sigma_cache: dict[str, pd.Series] = field(init=False, default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._breakout = DonchianBreakout(n_entry=self.n_entry)
        self._sizer = VolTargetSizer(target_vol_annual=self.target_vol_annual)
        self._exit_mgr = ExitManager(
            n_exit=self.n_exit,
            max_hold_hours=self.max_hold_hours,
            disaster_n_sigma=self.disaster_n_sigma,
            ref_hold_bars=self.ref_hold_bars,
        )
        for symbol, spec in self.symbol_specs.items():
            if symbol not in self.data:
                continue
            bars_per_year = spec["bars_per_year"]
            cone = YangZhangCone(
                yz_window=self.yz_window,
                cone_lookback=self.cone_lookback,
                k_filter=self.k_filter,
                bars_per_year=bars_per_year,
            )
            self._precompute_regime(symbol, self.data[symbol], cone)

    def _precompute_regime(
        self,
        symbol: str,
        df: pd.DataFrame,
        cone: YangZhangCone,
    ) -> None:
        """Pre-compute is_quiet and sigma_yz_annual for every bar in df.

        Uses an incremental approach for O(n) total cost (vs. O(n³) if
        cone.read() were naively called once per bar from on_bar):

        1. Call cone._yz_per_bar(df[:end]) for each end — each call is O(yz_window)
           so total cost is O(n × yz_window).
        2. Maintain a rolling deque of the last cone_lookback sigmas to compute
           the percentile at each step in O(1) (using the sorted insertion approach
           would be O(log n) but a simple numpy array rank is fine here).
        3. Store results in two pd.Series indexed by the df.index for O(1)
           lookup in on_bar().

        References
        ----------
        - YZ estimator: [volatility_trading, p.22-23, Eq.2.17a]
        - Cone percentile: [volatility_trading, p.58-60]
        """
        is_quiet_list: list[bool] = []
        sigma_annual_list: list[float] = []

        min_required = cone.yz_window + 1
        # Circular buffer of at most cone_lookback sigma_per_bar values
        window: collections.deque[float] = collections.deque(maxlen=cone.cone_lookback)

        for end in range(1, len(df) + 1):
            if end < min_required:
                is_quiet_list.append(False)
                sigma_annual_list.append(0.0)
                continue

            sigma_per_bar = cone._yz_per_bar(df.iloc[:end])  # O(yz_window)
            sigma_annual = cone._annualize(sigma_per_bar)
            window.append(sigma_per_bar)

            if len(window) < cone.cone_lookback:
                # Not enough history yet → regime unknown → not quiet
                is_quiet_list.append(False)
                sigma_annual_list.append(sigma_annual)
                continue

            # Compute percentile rank within the rolling window — O(cone_lookback)
            arr = np.asarray(window, dtype=float)
            pct = float((arr <= sigma_per_bar).sum()) / len(arr) * 100.0
            is_quiet = pct <= cone.k_filter

            is_quiet_list.append(is_quiet)
            sigma_annual_list.append(sigma_annual)

        self._regime_cache[symbol] = pd.Series(
            is_quiet_list, index=df.index, dtype=bool
        )
        self._sigma_cache[symbol] = pd.Series(
            sigma_annual_list, index=df.index, dtype=float
        )
        _logger.debug(
            "precomputed %d regime readings for %s", len(is_quiet_list), symbol
        )

    # ------------------------------------------------------------------
    # Protocol implementation
    # ------------------------------------------------------------------

    def on_bar(
        self,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        """Evaluate every symbol present in ``bars`` and return orders.

        For each symbol the logic is:
        1. Look up pre-cached is_quiet + sigma at the current timestamp.
        2. Slice data up to current bar (needed by breakout signal + exit manager).
        3. If in position → check ExitManager → close if any condition fires.
        4. If flat + quiet regime → check DonchianBreakout →
           size and emit an Order if both pass.

        Per-symbol state (a :class:`PositionState`) is stored in
        ``context[f"vol_expansion_state_{symbol}"]``.
        """
        orders: list[Order] = []

        for symbol, bar in bars.items():
            if symbol not in self.data:
                continue  # symbol not in our universe — skip silently
            if symbol not in self._regime_cache:
                continue  # no regime data built for this symbol — skip

            df_full = self.data[symbol]
            ts = bar.timestamp  # pd.Timestamp

            # O(1): pre-cached regime reading at this timestamp
            regime_series = self._regime_cache[symbol]
            sigma_series = self._sigma_cache[symbol]
            if ts not in regime_series.index:
                continue
            is_quiet: bool = bool(regime_series.loc[ts])
            sigma_annual: float = float(sigma_series.loc[ts])

            # Slice data up to (and including) current bar for breakout / exit
            mask = df_full.index <= ts
            df_slice = df_full.loc[mask]
            if len(df_slice) == 0:
                continue

            state_key = _state_key(symbol)
            in_position = symbol in portfolio.positions

            if in_position:
                state: PositionState | None = context.get(state_key)
                if state is None:
                    # Orphaned position (opened externally); cannot evaluate
                    # exits without entry state — skip.
                    continue

                # Convert pd.Timestamp to datetime for ExitManager
                now_dt = ts.to_pydatetime()
                exit_reason: ExitReason | None = self._exit_mgr.should_exit(
                    df=df_slice,
                    position=state,
                    now=now_dt,
                )
                if exit_reason is not None:
                    pos = portfolio.positions[symbol]
                    close_side = "sell" if pos.side == "long" else "buy"
                    orders.append(Order(symbol=symbol, side=close_side, volume=pos.volume))
                    context.pop(state_key, None)
                    _logger.debug(
                        "EXIT %s side=%s reason=%s at %.4f",
                        symbol, pos.side, exit_reason.value, bar.close,
                    )
            else:
                if not is_quiet:
                    continue

                # Check breakout signal
                direction = self._breakout.fire(df_slice)
                if direction is None:
                    continue

                # Size position
                equity = portfolio.equity
                entry_price = bar.close
                _notional, shares = self._sizer.size(
                    equity=equity,
                    sigma_yz_annual=sigma_annual,
                    entry_price=entry_price,
                )
                if shares <= 0:
                    continue

                # Emit order
                order_side = "buy" if direction == BreakoutDirection.LONG else "sell"
                orders.append(Order(symbol=symbol, side=order_side, volume=shares))

                # Record position state for exit evaluation
                bars_per_year = self.symbol_specs[symbol]["bars_per_year"]
                context[state_key] = PositionState(
                    direction=direction,
                    entry_price=entry_price,
                    entry_timestamp=ts.to_pydatetime(),
                    sigma_yz_at_entry_annual=sigma_annual,
                    bars_per_year_at_entry=bars_per_year,
                )
                _logger.debug(
                    "ENTER %s dir=%s shares=%.2f price=%.4f sigma=%.4f",
                    symbol, direction.value, shares, entry_price, sigma_annual,
                )

        return orders
