"""Leverage math helpers — Kelly fraction, intra-bar ruin check, bootstrap PoR.

Pure functions used by ``scripts/run_leverage_sweep_bollinger_mr.py``
(Phase 3 Lead A1). Kept free of ``Portfolio``/``Bar``/``Order`` coupling
so they remain testable in isolation.

Citations
---------

* Kelly criterion for bet sizing:
  ``[math_money_mgmt, Vince]`` — Kelly f from win-rate / avg-win /
  avg-loss of realized trades. Fractional Kelly (f/2) is the standard
  practitioner cap.
* Leverage space & ruin curves:
  ``[leverage_space, Vince]`` — each strategy has a leverage level
  that maximises growth (f*) beyond which the compounded return
  collapses.
* Gayed-style ruin protection & equity preservation:
  ``[leverage_for_the_long_run, p.7]`` — 1x leverage (buy-and-hold)
  vs levered variants: margin-call below cash floor wipes compound
  growth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

__all__ = [
    "kelly_fraction_from_trades",
    "intra_bar_ruin_scan",
    "bootstrap_prob_of_ruin",
    "RuinScanResult",
]


# ---------------------------------------------------------------------------
# Kelly fraction
# ---------------------------------------------------------------------------


def kelly_fraction_from_trades(
    pnls: Sequence[float], capital_at_entry: Sequence[float] | None = None,
) -> float:
    """Kelly f* estimated from realized trade P&Ls.

    Uses the binomial Kelly form ``f* = p/L - q/W`` where ``W`` = mean
    winning return, ``L`` = mean absolute losing return, ``p`` = win
    rate, ``q = 1 - p``. Returns in ``[0, 1]`` (clamped).

    Parameters
    ----------
    pnls : sequence of float
        Per-trade P&L in currency units.
    capital_at_entry : sequence of float, optional
        Equity at each trade's entry. If provided, P&L is normalized
        to per-trade return ``pnl / capital``; otherwise uses raw
        dollars (valid only if the account size was constant).

    Citation: ``[math_money_mgmt, Vince]``.
    """
    pnls_arr = np.asarray(list(pnls), dtype=float)
    if pnls_arr.size == 0:
        return 0.0

    if capital_at_entry is not None:
        cap = np.asarray(list(capital_at_entry), dtype=float)
        if cap.size != pnls_arr.size:
            raise ValueError("capital_at_entry length mismatch")
        safe_cap = np.where(cap > 0, cap, np.nan)
        rets = pnls_arr / safe_cap
        rets = rets[np.isfinite(rets)]
    else:
        rets = pnls_arr

    if rets.size == 0:
        return 0.0

    wins = rets[rets > 0]
    losses = rets[rets < 0]
    if wins.size == 0 or losses.size == 0:
        return 0.0

    p = wins.size / rets.size
    q = 1.0 - p
    w = float(wins.mean())
    loss = float(-losses.mean())  # positive magnitude

    if w <= 0 or loss <= 0:
        return 0.0

    f_star = p / loss - q / w
    return float(max(0.0, min(1.0, f_star)))


# ---------------------------------------------------------------------------
# Intra-bar ruin scan
# ---------------------------------------------------------------------------


@dataclass
class RuinScanResult:
    """Outcome of an intra-bar ruin scan.

    Attributes
    ----------
    ruined : bool
        True if any bar's worst-case equity breached the threshold.
    ruin_time : pd.Timestamp | None
        First bar where worst intra-bar equity <= threshold.
    worst_equity : float
        Lowest worst-case intra-bar equity observed over the run.
    worst_equity_time : pd.Timestamp | None
        Timestamp where ``worst_equity`` occurred.
    """

    ruined: bool
    ruin_time: pd.Timestamp | None
    worst_equity: float
    worst_equity_time: pd.Timestamp | None


def intra_bar_ruin_scan(
    trades: Iterable,
    bar_data: pd.DataFrame,
    initial_cash: float,
    ruin_threshold: float = 0.0,
) -> RuinScanResult:
    """Reconstruct the position timeline from ``trades`` and scan bar lows/highs.

    For each bar a position was held, computes the worst-case intra-bar
    equity using ``bar.low`` for long positions and ``bar.high`` for
    short positions. If that worst-case equity ever <= ``ruin_threshold``
    the run is flagged ruined at the first such bar.

    The engine itself uses close-to-close marks and doesn't enforce
    margin; this helper approximates what would happen if a broker
    liquidated intra-bar when equity crossed a ruin floor. Approximation
    because engine cash and position volume are re-computed deterministically
    from trades (no overlapping positions in BollingerMR / ETFRotation).

    Parameters
    ----------
    trades : iterable of ai_trade.backtest.engine.portfolio.Trade
    bar_data : pd.DataFrame
        OHLCV indexed by timestamp.
    initial_cash : float
        Cash the portfolio started with.
    ruin_threshold : float
        Equity floor in currency units (default 0).

    Returns
    -------
    RuinScanResult
    """
    trades_list = list(trades)
    if not trades_list:
        return RuinScanResult(False, None, initial_cash, None)

    # Running cash ledger following the same debit/credit convention as
    # Portfolio.open_position/close_position (no commission here — we
    # only care about gross intra-bar equity reachability).
    cash = float(initial_cash)
    worst_equity = float("inf")
    worst_time: pd.Timestamp | None = None
    ruin_time: pd.Timestamp | None = None

    idx = bar_data.index

    for tr in trades_list:
        entry_price = float(tr.entry_price)
        exit_price = float(tr.exit_price)
        vol = float(tr.volume)
        side = tr.side

        # Apply entry: long debits, short credits.
        cash += -vol * entry_price if side == "long" else vol * entry_price

        # Bars held inclusive of entry_time up to exit_time.
        try:
            start = idx.get_loc(tr.entry_time)
            stop = idx.get_loc(tr.exit_time)
        except KeyError:
            # Trade ts not in bar index (shouldn't happen, but stay safe).
            start = stop = None

        if start is not None and stop is not None and stop >= start:
            held_bars = bar_data.iloc[start : stop + 1]
            for ts, row in held_bars.iterrows():
                low = float(row["low"])
                high = float(row["high"])
                # Long: worst at low. Short: worst at high.
                worst_price = low if side == "long" else high
                position_value = vol * worst_price if side == "long" else -vol * worst_price
                eq = cash + position_value
                if eq < worst_equity:
                    worst_equity = eq
                    worst_time = ts
                if eq <= ruin_threshold and ruin_time is None:
                    ruin_time = ts

        # Apply exit.
        cash += vol * exit_price if side == "long" else -vol * exit_price

    if worst_equity == float("inf"):
        worst_equity = initial_cash

    return RuinScanResult(
        ruined=ruin_time is not None,
        ruin_time=ruin_time,
        worst_equity=worst_equity,
        worst_equity_time=worst_time,
    )


# ---------------------------------------------------------------------------
# Bootstrap probability-of-ruin
# ---------------------------------------------------------------------------


def bootstrap_prob_of_ruin(
    trade_returns: Sequence[float],
    leverage: float,
    n_paths: int = 10_000,
    block_size: int = 5,
    horizon: int | None = None,
    ruin_floor: float = 0.0,
    seed: int | None = 42,
) -> float:
    """Stationary block bootstrap estimate of P(account ruin) under leverage L.

    Each trade's return (``pnl / capital_at_entry``) is multiplied by
    ``leverage`` and applied as a compounded geometric path. If equity
    ever <= ``ruin_floor`` the path is counted ruined. Returns the
    fraction of ruined paths over ``n_paths`` simulations.

    Block bootstrap with block size 5 preserves short-horizon
    autocorrelation (losing streaks).

    Citation: ``[leverage_space, Vince]`` — ruin curves as a function
    of fractional f applied to a return distribution.
    """
    rets = np.asarray(list(trade_returns), dtype=float)
    rets = rets[np.isfinite(rets)]
    if rets.size == 0:
        return 0.0

    n_trades = rets.size
    horizon = int(horizon) if horizon is not None else n_trades
    if horizon <= 0:
        return 0.0
    if block_size < 1:
        block_size = 1

    rng = np.random.default_rng(seed)
    ruined = 0

    for _ in range(n_paths):
        path_returns = np.empty(horizon, dtype=float)
        filled = 0
        while filled < horizon:
            start = int(rng.integers(0, n_trades))
            take = min(block_size, horizon - filled)
            for k in range(take):
                path_returns[filled + k] = rets[(start + k) % n_trades]
            filled += take

        equity = 1.0
        for r in path_returns:
            equity *= 1.0 + leverage * r
            if equity <= ruin_floor:
                ruined += 1
                break

    return ruined / n_paths
