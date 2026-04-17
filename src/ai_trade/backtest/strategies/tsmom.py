"""Time-Series Momentum — Donchian channel breakout (Turtles basis).

Single-asset trend-follow strategy for Phase 3 Lead A3b (multi-strategy
per-asset matching). Where BollingerMR fails on trending assets (A3a FAIL
on IWM/TLT/xrpusd), this module tests whether a pure breakout signal
captures edge on those assets.

Signal (Donchian / Turtles canonical)
------------------------------------

* **Long entry:** ``close_t > max(high[t-entry_lookback : t])`` (breakout
  above prior high window).
* **Long exit:** ``close_t < min(low[t-exit_lookback : t])`` (breakdown
  below prior low window).
* **Hold prior state** between entry/exit triggers.

Path B [SWING BROKER] daily simulator — no swap, 15% BR capital-gains
tax modeled on realized profit at each LONG→FLAT transition. Round-trip
commission + spread applied on every regime flip.

Return-series style (like :mod:`ai_trade.backtest.strategies.letf_rotation`)
— each day outputs a single net return; no bar-level Portfolio/Order
machinery. Makes CPCV/PBO/bootstrap trivial.

Citations
---------

* Donchian 20/40 breakout (Turtle basis): ``[trading_systems_methods,
  p.353]`` — "Buy when high > max high 40 days; exit long when low <
  min low 20 days".
* Time-series momentum as a distinct family from cross-sectional:
  ``[algo_trading_chan, p.133, ch.6]`` — "past returns of a single
  instrument are positively correlated with future returns".
* Trend filter in ETF rotation (SMA regime) analogue:
  ``[stocks_on_the_move, p.110]`` — only take long signals in
  uptrends; breakout is the binary version.
* BR 15% capital-gains tax per Investment Mandate §4.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "TRADING_DAYS_PER_YEAR",
    "TSMOMConfig",
    "TSMOMResult",
    "compute_donchian_signal",
    "simulate_tsmom",
]


TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class TSMOMConfig:
    """Immutable configuration for a Donchian breakout run.

    Parameters
    ----------
    entry_lookback : int
        Prior window for the entry-high channel (days). Canonical 40 or
        55 for Turtles [trading_systems_methods, p.353].
    exit_lookback : int
        Prior window for the exit-low channel (days). Canonical 20.
    commission_bps : float
        Commission per regime flip in basis points of switched notional.
    spread_bps : float
        Bid-ask spread per flip in basis points.
    tax_rate : float
        Capital-gains tax on realized gain at each LONG→FLAT exit. BR
        swing = 0.15 per Investment Mandate §4.
    """

    entry_lookback: int = 40
    exit_lookback: int = 20
    commission_bps: float = 10.0
    spread_bps: float = 5.0
    tax_rate: float = 0.15

    def __post_init__(self) -> None:
        if self.entry_lookback < 2:
            raise ValueError(
                f"entry_lookback must be >= 2, got {self.entry_lookback}"
            )
        if self.exit_lookback < 1:
            raise ValueError(
                f"exit_lookback must be >= 1, got {self.exit_lookback}"
            )
        if self.commission_bps < 0:
            raise ValueError(
                f"commission_bps must be >= 0, got {self.commission_bps}"
            )
        if self.spread_bps < 0:
            raise ValueError(
                f"spread_bps must be >= 0, got {self.spread_bps}"
            )
        if not 0.0 <= self.tax_rate <= 1.0:
            raise ValueError(
                f"tax_rate must be in [0, 1], got {self.tax_rate}"
            )

    @property
    def switch_cost_pct(self) -> float:
        """Combined commission + spread per flip, as fraction."""
        return (self.commission_bps + self.spread_bps) / 10_000.0


@dataclass
class TSMOMResult:
    """Output of a TSMOM Donchian simulation.

    Attributes mirror :class:`ai_trade.backtest.strategies.letf_rotation.RotationResult`
    so downstream gate code (``grid/tsmom_a3b.py``) can stay symmetric.
    """

    equity: pd.Series
    daily_returns: pd.Series
    regime: pd.Series  # "LONG" or "FLAT"
    switches: pd.Series
    cum_cost_pct: float = 0.0
    cum_tax_pct: float = 0.0

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sigma = float(r.std(ddof=1))
        if sigma == 0.0:
            return 0.0
        return float(r.mean() / sigma * np.sqrt(periods_per_year))

    def cagr(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        eq = self.equity.dropna()
        if len(eq) < 2:
            return 0.0
        years = (len(eq) - 1) / periods_per_year
        if years <= 0:
            return 0.0
        total = float(eq.iloc[-1] / eq.iloc[0])
        if total <= 0:
            return -1.0
        return total ** (1.0 / years) - 1.0

    def max_drawdown(self) -> float:
        eq = self.equity.dropna()
        if eq.empty:
            return 0.0
        peak = eq.cummax()
        return float((eq / peak - 1.0).min())


def compute_donchian_signal(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    entry_lookback: int = 40,
    exit_lookback: int = 20,
) -> pd.Series:
    """Daily LONG/FLAT signal via Donchian breakout.

    Uses ``high[t-entry_lookback : t]`` (prior window, NOT including t)
    to compute the entry channel — avoids look-ahead. Same for exit
    via ``low[t-exit_lookback : t]``.

    The first ``max(entry_lookback, exit_lookback)`` bars produce NaN
    signal (insufficient history). After warmup, "FLAT" is the default
    until the first entry trigger fires.

    Returns
    -------
    pd.Series
        Object dtype: {"LONG", "FLAT"} or NaN during warmup.

    Citation
    --------
    Donchian 20/40 Turtle rule: ``[trading_systems_methods, p.353]``.
    """
    if entry_lookback < 2:
        raise ValueError(f"entry_lookback must be >= 2, got {entry_lookback}")
    if exit_lookback < 1:
        raise ValueError(f"exit_lookback must be >= 1, got {exit_lookback}")
    if not (len(high) == len(low) == len(close)):
        raise ValueError("high/low/close must share length")
    if not (high.index.equals(low.index) and high.index.equals(close.index)):
        raise ValueError("high/low/close must share the same index")

    # Prior-window extrema (strict "yesterday and before", no t peek).
    prior_high = high.shift(1).rolling(
        window=entry_lookback, min_periods=entry_lookback
    ).max()
    prior_low = low.shift(1).rolling(
        window=exit_lookback, min_periods=exit_lookback
    ).min()

    warmup = max(entry_lookback, exit_lookback)
    signal: list[str | float] = []
    prev: str | None = None
    close_vals = close.to_numpy(dtype=float)
    ph = prior_high.to_numpy(dtype=float)
    pl = prior_low.to_numpy(dtype=float)
    for i, c in enumerate(close_vals):
        if i < warmup or np.isnan(ph[i]) or np.isnan(pl[i]):
            signal.append(np.nan)
            continue
        if c > ph[i]:
            prev = "LONG"
        elif c < pl[i]:
            prev = "FLAT"
        signal.append(prev if prev is not None else "FLAT")

    return pd.Series(signal, index=close.index, dtype=object)


def simulate_tsmom(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    config: TSMOMConfig,
) -> TSMOMResult:
    """Run a single Donchian configuration end-to-end on (H, L, C).

    Computes daily close-to-close returns for the asset and routes them
    through the LONG/FLAT regime produced by :func:`compute_donchian_signal`.
    Costs and BR tax applied on each LONG↔FLAT transition.

    Raises
    ------
    ValueError
        If input series are misaligned or empty.
    """
    if close.empty:
        raise ValueError("close series must not be empty")
    if not (high.index.equals(low.index) and high.index.equals(close.index)):
        raise ValueError("high/low/close must share the same index")

    regime = compute_donchian_signal(
        high, low, close, config.entry_lookback, config.exit_lookback
    )
    asset_returns = close.astype(float).pct_change().fillna(0.0)

    daily_net = pd.Series(0.0, index=close.index)
    switches = pd.Series(False, index=close.index)
    equity = 1.0
    equity_curve: list[float] = []
    prev_regime: str | None = None
    entry_equity = 1.0
    cum_cost = 0.0
    cum_tax = 0.0

    for ts, cur in regime.items():
        if not isinstance(cur, str):
            equity_curve.append(equity)
            prev_regime = None
            continue

        # Switch-at-close convention: costs/tax deducted BEFORE applying
        # today's return on the new regime. Mirrors LETF rotation
        # (letf_rotation.py:391-395) so gate code stays symmetric.
        if prev_regime is not None and cur != prev_regime:
            switches.loc[ts] = True
            cost = config.switch_cost_pct * equity
            equity -= cost
            cum_cost += cost
            if prev_regime == "LONG" and config.tax_rate > 0:
                gain = max(0.0, equity - entry_equity)
                tax = gain * config.tax_rate
                equity -= tax
                cum_tax += tax
            if cur == "LONG":
                entry_equity = equity

        r = 0.0 if cur != "LONG" else float(asset_returns.loc[ts])
        if np.isnan(r):
            r = 0.0
        new_equity = equity * (1.0 + r)
        if equity_curve:
            daily_net.loc[ts] = new_equity / equity_curve[-1] - 1.0
        equity = new_equity
        equity_curve.append(equity)
        prev_regime = cur

    equity_series = pd.Series(
        equity_curve, index=close.index[: len(equity_curve)]
    )
    return TSMOMResult(
        equity=equity_series,
        daily_returns=daily_net,
        regime=regime,
        switches=switches,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
    )
