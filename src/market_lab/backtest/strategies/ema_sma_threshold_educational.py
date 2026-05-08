"""EMA/SMA Threshold Crossover on SPY with Leveraged ETFs — Educational.

Return-series simulator for a trend-following rule on SPY total return,
with both long and short leveraged legs selected via a moving-average
band. Mirror of the Gayed LRS pattern in
:mod:`ai_trade.backtest.strategies.letf_rotation`, extended to allow
negative leverage on the SELL leg (inverse / short leveraged ETFs).

Signal (daily, hysteresis band)
-------------------------------

Let ``P(t)`` be SPYSIM close (TR). Let ``MA(t)`` be SMA or EMA over
``lookback`` bars, ``threshold`` the band width as fraction.

* ``P(t) > MA(t) · (1 + threshold)`` → ``regime = +1`` (BUY — long leg)
* ``P(t) < MA(t) · (1 − threshold)`` → ``regime = −1`` (SELL — short/cash)
* Otherwise → ``regime = regime(t−1)`` (HOLD — anti-whipsaw)

At the first day past warmup with no prior regime, defaults to ``-1``
(conservative).

Leg returns
-----------

* ``regime = +1`` → ``r(t) = buy_leverage · r_SPX(t) − fee/252``.
* ``regime = −1``:
    * ``sell_leverage = 0`` → ``r(t) = cash_daily`` (cash sleeve).
    * ``sell_leverage < 0`` → ``r(t) = sell_leverage · r_SPX(t) − fee/252``.

Fee drag is applied on both long and short synth legs (inverse ETFs also
charge ER; real SDS/SPXU ER ~0.90%). Gayed formula
``[leverage_for_the_long_run, p.16, footnote 22]`` extended to negative
leverage (same algebra — the sign of ``L`` only changes directional
exposure; fee drag is always a cost).

Switch cost (commission + spread, ``switch_cost_bps``) is taken on each
regime change (same pattern as :mod:`letf_rotation`).

Tax (BR DARF 15% swing)
-----------------------

Optional ``tax_rate`` applies a 15% withholding on every profitable
regime exit (``equity_exit > equity_entry``). Mirrors
:mod:`letf_rotation` §Investment Mandate §4 — educational approximation
of the Brazilian swing-sale rule. Loss-making exits incur no tax, and
losses are NOT carried forward (worst-case model; real BR compensates
losses intra-month up to R$20k/month exemption).

Citations
---------

* Synth LETF formula: ``[leverage_for_the_long_run, p.16, footnote 22]``.
* Expense ratio 0.95% (post-2021 UPRO): ``[leverage_for_the_long_run, p.16, footnote 23]``.
* SMA regime filter canonical: ``[leverage_for_the_long_run, p.8, p.13]``.
* MA periods 10-200 positive alpha: ``[leverage_for_the_long_run, p.14, Table 6]``.
* Leverage levels tested: ``[leverage_for_the_long_run, p.17, Table 8]``.
* Band hysteresis (Reddit-style 5%): ``[leverage_for_the_long_run, p.11]``.
* Cash as RISK_OFF asset: ``[leverage_for_the_long_run, p.21]``.
* Honest alignment (no look-ahead): ``[advances_fin_ml, p.31-34]``.
* BR DARF 15% swing: Investment Mandate §4.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

FilterKind = Literal["SMA", "EMA"]

TRADING_DAYS_PER_YEAR = 252
DEFAULT_FEE = 0.0095  # UPRO/SSO post-2021 ER [leverage_for_the_long_run, p.16, fn.23]

__all__ = [
    "EMASMAThresholdConfig",
    "ThresholdResult",
    "Trade",
    "compute_threshold_regime",
    "simulate_ema_sma_threshold",
    "simulate_regime_threshold_with_legs",
    "TRADING_DAYS_PER_YEAR",
    "DEFAULT_FEE",
]


@dataclass(frozen=True)
class EMASMAThresholdConfig:
    """Immutable configuration for one sweep cell.

    Parameters
    ----------
    filter : {"SMA", "EMA"}
        Moving-average flavour on SPY TR closes.
    lookback : int
        MA window in trading days. Must be > 1.
    threshold_pct : float
        Hysteresis band half-width as fraction of MA. ``0.05 = ±5%``.
        Must be >= 0. 0 = strict cross (Gayed canonical).
    buy_leverage : float
        Leverage on BUY regime (long leg). Typical {1.0, 2.0, 3.0}.
        Must be > 0.
    sell_leverage : float
        Leverage on SELL regime. ``0.0`` = cash (pays ``cash_rate_annual``).
        Negative values = synthetic inverse LETF (−1, −2, −3).
        Positive values are rejected (use a long-only rotation module instead).
    fee : float
        Annual fee applied to both long and short synth legs. Default 0.95%.
    switch_cost_bps : float
        Round-trip transaction cost per regime transition, in bps.
        Default 15 bps (10 commission + 5 spread, matching letf_rotation).
    cash_rate_annual : float
        Risk-free rate for cash sleeve when ``sell_leverage == 0``.
        Default 0.0 (Gayed canonical — literal cash, p.21).
    tax_rate : float
        Swing-sale tax (e.g. 0.15 for BR DARF 15%). Applied to the gain
        of every profitable regime exit. Default 0.0 (no tax — "pure"
        strategy view). Real BR rule also has a R$20k/mo exemption which
        this model does NOT credit — worst-case conservative view.
    """

    filter: FilterKind = "SMA"
    lookback: int = 200
    threshold_pct: float = 0.05
    buy_leverage: float = 2.0
    sell_leverage: float = 0.0
    fee: float = DEFAULT_FEE
    switch_cost_bps: float = 15.0
    cash_rate_annual: float = 0.0
    tax_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.filter not in ("SMA", "EMA"):
            raise ValueError(f"filter must be SMA or EMA, got {self.filter!r}")
        if self.lookback <= 1:
            raise ValueError(f"lookback must be > 1, got {self.lookback}")
        if self.threshold_pct < 0:
            raise ValueError(f"threshold_pct must be >= 0, got {self.threshold_pct}")
        if self.buy_leverage <= 0:
            raise ValueError(f"buy_leverage must be > 0, got {self.buy_leverage}")
        if self.sell_leverage > 0:
            raise ValueError(
                f"sell_leverage must be <= 0 (short or cash), "
                f"got {self.sell_leverage}. Use letf_rotation for long-only."
            )
        if self.fee < 0:
            raise ValueError(f"fee must be >= 0, got {self.fee}")
        if self.tax_rate < 0 or self.tax_rate >= 1:
            raise ValueError(f"tax_rate must be in [0, 1), got {self.tax_rate}")

    @property
    def switch_cost_pct(self) -> float:
        return self.switch_cost_bps / 10_000.0

    @property
    def cfg_id(self) -> str:
        """Short deterministic id for this config, stable across runs."""
        return (
            f"{self.filter}"
            f"_N{self.lookback}"
            f"_th{int(self.threshold_pct * 100)}"
            f"_bL{self.buy_leverage:g}"
            f"_sL{self.sell_leverage:g}"
        )


@dataclass(frozen=True)
class Trade:
    """One contiguous regime block (entry → exit)."""

    regime: int  # +1 long or -1 short/cash
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_equity: float
    exit_equity: float  # after fees/switch/tax
    gross_return: float  # (exit / entry) - 1 before tax
    tax_paid: float  # 0 if loss-making or tax_rate == 0
    bars_held: int

    @property
    def net_pnl_pct(self) -> float:
        return self.exit_equity / self.entry_equity - 1.0


@dataclass
class ThresholdResult:
    """Output of one simulation run."""

    equity: pd.Series
    daily_returns: pd.Series
    regime: pd.Series  # int: +1, -1 (warmup rows are NaN)
    n_switches: int
    cum_cost_pct: float
    cum_tax_pct: float = 0.0
    trades: list[Trade] = field(default_factory=list)


def compute_threshold_regime(
    prices: pd.Series,
    cfg: EMASMAThresholdConfig,
) -> pd.Series:
    """Daily regime signal {+1, -1} with hysteresis band.

    The first ``lookback - 1`` bars are NaN (insufficient history). On
    the first post-warmup day with the price inside the band, the
    default regime is ``-1`` (conservative: wait for a definitive buy).
    """
    if cfg.lookback <= 1:
        raise ValueError(f"lookback must be > 1, got {cfg.lookback}")

    px = prices.astype(float)
    if cfg.filter == "SMA":
        ma = px.rolling(window=cfg.lookback, min_periods=cfg.lookback).mean()
    else:
        ma = px.ewm(span=cfg.lookback, min_periods=cfg.lookback, adjust=False).mean()

    upper = ma * (1.0 + cfg.threshold_pct)
    lower = ma * (1.0 - cfg.threshold_pct)

    out: list[float] = []
    prev: int | None = None
    for p, up, lo in zip(px.values, upper.values, lower.values):
        if np.isnan(up) or np.isnan(lo):
            out.append(np.nan)
            continue
        if p > up:
            prev = 1
        elif p < lo:
            prev = -1
        # Inside band: hold previous. If no previous, default to -1.
        out.append(prev if prev is not None else -1)

    return pd.Series(out, index=prices.index, dtype=float)


def _synth_leveraged_returns(
    spx_returns: pd.Series,
    leverage: float,
    fee: float,
) -> pd.Series:
    """Apply ``r = L · r_SPX − fee/252`` for any sign of L.

    Extends :func:`synthesize_letf_returns` (which guards L > 0) to allow
    negative L for synthetic inverse LETFs. Fee drag is always a cost.

    Cite ``[leverage_for_the_long_run, p.16, footnote 22]``.
    """
    daily_drag = fee / TRADING_DAYS_PER_YEAR
    return leverage * spx_returns - daily_drag


def simulate_ema_sma_threshold(
    spx_prices: pd.Series,
    spx_returns: pd.Series,
    cfg: EMASMAThresholdConfig,
) -> ThresholdResult:
    """Run one sweep cell on a signal series with **synth** leg returns.

    This is the path used by the SPYSIM educational study: both buy and
    sell legs are synthesized from ``spx_returns`` via
    ``r = L · r_SPX − fee/252``. Use
    :func:`simulate_regime_threshold_with_legs` for real ETF returns.

    Parameters
    ----------
    spx_prices : pd.Series
        Daily SPYSIM close (TR). Used for the MA signal.
    spx_returns : pd.Series
        Daily SPYSIM total returns (``pct_change``). Must share index
        with ``spx_prices`` (may be 1 row shorter — aligned internally).
    cfg : EMASMAThresholdConfig
        Immutable grid cell.

    Returns
    -------
    ThresholdResult
    """
    idx = spx_returns.index
    if not idx.is_monotonic_increasing:
        raise ValueError("spx_returns index must be monotonic increasing")

    # Pre-compute leg returns once (synthetic).
    long_leg = _synth_leveraged_returns(spx_returns, cfg.buy_leverage, cfg.fee)
    if cfg.sell_leverage == 0.0:
        cash_daily = cfg.cash_rate_annual / TRADING_DAYS_PER_YEAR
        short_leg = pd.Series(cash_daily, index=idx)
    else:
        short_leg = _synth_leveraged_returns(spx_returns, cfg.sell_leverage, cfg.fee)

    return simulate_regime_threshold_with_legs(
        signal_prices=spx_prices,
        buy_leg_returns=long_leg,
        sell_leg_returns=short_leg,
        cfg=cfg,
    )


def simulate_regime_threshold_with_legs(
    signal_prices: pd.Series,
    buy_leg_returns: pd.Series,
    sell_leg_returns: pd.Series,
    cfg: EMASMAThresholdConfig,
) -> ThresholdResult:
    """Run one sweep cell with **explicit** leg return series (real ETFs).

    Use this when you have real daily returns for the buy/sell legs
    (e.g. UPRO from Tiingo). The MA regime is still computed from
    ``signal_prices`` (typically the underlying index, e.g. SPY).

    Parameters
    ----------
    signal_prices : pd.Series
        Daily close of the signal asset (e.g. SPY or QQQ). Used for
        the MA regime filter only.
    buy_leg_returns : pd.Series
        Daily returns of the BUY leg (e.g. real UPRO returns). Used
        whenever ``regime == +1``.
    sell_leg_returns : pd.Series
        Daily returns of the SELL leg. For cash, pass a constant series
        (e.g. ``cfg.cash_rate_annual / 252``). For a synth inverse, pass
        the output of ``_synth_leveraged_returns(signal_returns,
        negative_L, fee)``.
    cfg : EMASMAThresholdConfig
        Rule parameters. The ``buy_leverage`` / ``sell_leverage`` /
        ``fee`` fields are metadata only on this path — real returns are
        taken from the passed series. ``filter``, ``lookback``,
        ``threshold_pct``, ``switch_cost_bps``, ``cash_rate_annual``,
        ``tax_rate`` are all honoured.

    Returns
    -------
    ThresholdResult
    """
    # Align everything to the buy_leg_returns index (which should be the
    # union of available data for the used legs).
    idx = buy_leg_returns.index
    if not idx.is_monotonic_increasing:
        raise ValueError("buy_leg_returns index must be monotonic increasing")
    # Reindex sell_leg and signal_prices to the same index.
    sell_leg = sell_leg_returns.reindex(idx)
    long_leg = buy_leg_returns
    short_leg = sell_leg
    prices_on_ret_idx = signal_prices.reindex(idx)

    regime = compute_threshold_regime(prices_on_ret_idx, cfg)

    # Equity path — HONEST alignment: yesterday's regime earns today's
    # return. Pairing regime[t] (needs close[t]) with return[t] (close[t-1]
    # → close[t]) is look-ahead — the rule observes the very bar whose
    # return it pretends to collect. Fix follows the pattern applied in
    # plano_a_leveraged_rotation.py commit 7b90a8f:
    # ``[advances_fin_ml, p.31-34]``.
    equity = 1.0
    equity_curve: list[float] = []
    daily_net: list[float] = []
    n_switches = 0
    cum_cost = 0.0
    cum_tax = 0.0
    prev_regime: int | None = None
    switch_cost = cfg.switch_cost_pct
    tax_rate = cfg.tax_rate

    long_vals = long_leg.values
    short_vals = short_leg.values
    regime_vals = regime.values
    idx_values = idx

    # Trade ledger — tracks each regime block (entry to exit).
    trades: list[Trade] = []
    entry_equity = 1.0
    entry_idx: int | None = None

    for i in range(len(idx)):
        cur = regime_vals[i]
        if np.isnan(cur):
            # Warmup — no signal yet, hold cash (no return, no cost).
            equity_curve.append(equity)
            daily_net.append(0.0)
            continue

        cur_int = int(cur)
        prev_eq = equity

        # Step 1: earn today's return at YESTERDAY's regime.
        if prev_regime is not None:
            r = long_vals[i] if prev_regime == 1 else short_vals[i]
            r = 0.0 if np.isnan(r) else float(r)
            equity *= 1.0 + r
        # On the first post-warmup bar, prev_regime is None → no return
        # applied yet (we're only now observing the signal that sets the
        # position for tomorrow).

        # Step 2: observe today's regime at close. If it changed vs
        # yesterday's, pay the switch cost AND (optional) swing tax on
        # the profitable portion of the prior regime's equity gain.
        if prev_regime is not None and cur_int != prev_regime:
            # Tax first (on realised gain BEFORE switch cost is charged).
            tax = 0.0
            if tax_rate > 0.0 and entry_idx is not None and equity > entry_equity:
                gain = equity - entry_equity
                tax = gain * tax_rate
                equity -= tax
                cum_tax += tax
            # Switch cost on the (post-tax) equity.
            cost = switch_cost * equity
            equity -= cost
            cum_cost += cost
            n_switches += 1

            # Close the prior trade.
            if entry_idx is not None:
                exit_ts = pd.Timestamp(idx_values[i])
                entry_ts = pd.Timestamp(idx_values[entry_idx])
                trades.append(
                    Trade(
                        regime=prev_regime,
                        entry_date=entry_ts,
                        exit_date=exit_ts,
                        entry_equity=entry_equity,
                        exit_equity=equity,
                        gross_return=(equity + tax + cost) / entry_equity - 1.0,
                        tax_paid=tax,
                        bars_held=i - entry_idx,
                    )
                )
            # Open a new trade.
            entry_equity = equity
            entry_idx = i
        elif prev_regime is None:
            # First post-warmup bar — record the initial entry.
            entry_equity = equity
            entry_idx = i

        equity_curve.append(equity)
        daily_net.append(equity / prev_eq - 1.0 if prev_eq > 0 else 0.0)
        prev_regime = cur_int

    # Close any still-open trade at the final bar.
    if entry_idx is not None and prev_regime is not None:
        last_i = len(idx) - 1
        if entry_idx < last_i:
            exit_ts = pd.Timestamp(idx_values[last_i])
            entry_ts = pd.Timestamp(idx_values[entry_idx])
            trades.append(
                Trade(
                    regime=prev_regime,
                    entry_date=entry_ts,
                    exit_date=exit_ts,
                    entry_equity=entry_equity,
                    exit_equity=equity,
                    gross_return=equity / entry_equity - 1.0,
                    tax_paid=0.0,
                    bars_held=last_i - entry_idx,
                )
            )

    equity_series = pd.Series(equity_curve, index=idx, name="equity")
    returns_series = pd.Series(daily_net, index=idx, name="returns")

    return ThresholdResult(
        equity=equity_series,
        daily_returns=returns_series,
        regime=regime,
        n_switches=n_switches,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
        trades=trades,
    )
