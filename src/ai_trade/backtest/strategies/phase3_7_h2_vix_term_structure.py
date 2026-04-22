"""Phase 3.7 — H2.c: VIX term-structure regime rotation (VIXY/VXX → SPY/TLT).

Honest replication of a **term-structure-of-vol regime filter** applied to
a SPY (or SSO 2x) long-leg / TLT off-leg rotation on daily closes.

Premise (Božović 2024, Cboe consensus 2013-2024)
-------------------------------------------------

The VIX term structure conveys regime:

* **Contango** (VIX spot < front-month futures) — "normal" regime, realized
  vol expected to mean-revert down; SPY-bullish.
* **Backwardation** (VIX spot > front-month futures) — "stress" regime,
  realized vol spiked; SPY-bearish.

Tiingo does not carry raw VIX futures. We proxy the term-structure state
via the *sign of trailing VIXY returns*. VIXY tracks a ~1-month VIX
futures portfolio — under persistent contango it bleeds (roll loss), so a
falling VIXY is the tell-tale of normal regime; a rising VIXY signals
stress / backwardation. This is the reduced-form signal recommended by
the Phase 3.7-3 H2.c hunt prompt.

Canonical rule
--------------

At the close of day ``t-1``:

* ``vixy_lb_ret_{t-1} = (VIXY_{t-1} / VIXY_{t-1-lookback}) - 1``
* ``regime_t = 1`` (risk-on, SPY/SSO) iff ``vixy_lb_ret_{t-1} <= 0``
* ``regime_t = 0`` (risk-off, TLT)     iff ``vixy_lb_ret_{t-1} >  0``

Exposure on day ``t`` equals the regime signal decided at close(t-1),
consistent with the F2-patched ``prev_weight × ret`` convention
[advances_fin_ml, p.31-34]. Daily rebalance at close.

Citations
---------
* Božović 2026/2024 — "VIX-managed portfolios", IRFA v95 Part A —
  `[bozovic_2024_irfa]` (knowledge entry; literature-sprint
  ``docs/research/2026-04-23-phase3.7-literature-sprint.md §T2.Paper1``).
* Wang-Li-Liu-Chen-Tang 2024 — "VIX constant maturity futures trading
  strategy: a walk-forward ML study" — `[wang_li_vix_ml_2024]`
  (literature-sprint §T2.Paper2).
* Cboe/Macroption consensus on VIX backwardation as regime signal —
  literature-sprint §T2.Paper3.
* `[advances_fin_ml, p.31-34]` — prev_weight × ret lookahead alignment.
* `[advances_fin_ml, p.196-202, p.208-211, p.273-275]` — stationary
  bootstrap, CSCV/PBO, DSR.
* `[leverage_for_the_long_run, p.16]` — synthetic LETF pre-history
  formula (not used here — we rely on actual SSO post-2006 prices).
* `docs/investment-mandate.md §2.2 rota B / §2.4 / §4.6` — cost model
  (Inter), tier framework, 13 gates.

Design notes
------------

* **Rota B cost model (Inter):** spread 0.00 (we don't convert FX
  intra-strategy — capital is already USD in Inter Intl), commission 0,
  15% DARF on realized yearly gain. SSO expense ratio 0.0091/yr
  deducted on RISK_ON SSO days as ``ER / 252``.
* **No lookahead audit:** VIXY signal uses only close[t-1-lb], close[t-1].
  Weight at day t equals prior-close decision; realized return applied
  ``prev_weight × ret`` (shift(1) fillna(0)).
* **Transaction costs on regime switch:** ``commission_bps`` + half-
  ``spread_bps`` per side, applied on each regime change.
* **Tax:** annual 15% DARF on realized NET gain at each year-end +
  on each RISK_ON → RISK_OFF transition (realizing the SPY/SSO leg).
  This mirrors the `letf_rotation.py` convention.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "H2VixTermConfig",
    "H2VixTermResult",
    "compute_vix_regime_signal",
    "simulate_h2_vix_term_structure",
]

TRADING_DAYS_PER_YEAR = 252

SignalFeed = Literal["VIXY", "VXX"]
LongAsset = Literal["SPY", "SSO"]


@dataclass(frozen=True)
class H2VixTermConfig:
    """Immutable H2.c configuration cell.

    Parameters
    ----------
    lookback : int
        Trailing-return window on the VIX-ETF feed (VIXY/VXX). Falling
        trailing-return → contango → risk-on.
    signal_feed : {"VIXY", "VXX"}
        Which VIX ETF to use for the regime probe. VIXY inception 2011,
        VXX 2009 (VXX has a reverse-split scar in 2019). Default VIXY.
    long_asset : {"SPY", "SSO"}
        Long-leg ticker. SSO adds ~2× embedded leverage (+ expense ratio
        drag applied daily on RISK_ON).
    off_asset_return : "TLT" or None
        Off-leg feed. "TLT" rotates to TLT daily return on risk-off,
        "None" holds cash at zero return.
    sso_expense_annual : float
        SSO expense ratio, applied as daily drag on RISK_ON days when
        ``long_asset == "SSO"``. ProShares reports 0.91%.
    commission_bps : float
        Per-switch commission cost in bps of switched notional.
        Banco Inter US brokerage → 0 bps commission.
    spread_bps : float
        Per-switch bid-ask spread cost in bps. 5 bps ≈ 0.05%.
    tax_rate : float
        DARF 15% on realized swing-trade gains per mandate rota B.
        Apply on each RISK_ON exit and at each calendar-year boundary.
    threshold : float
        Decision threshold on the trailing-return signal. 0.0 (sign
        rule). Kept as a tunable for PBO analysis.
    """

    lookback: int = 21
    signal_feed: SignalFeed = "VIXY"
    long_asset: LongAsset = "SPY"
    off_asset_return: Literal["TLT", "NONE"] = "TLT"
    sso_expense_annual: float = 0.0091
    commission_bps: float = 0.0
    spread_bps: float = 5.0
    tax_rate: float = 0.15
    threshold: float = 0.0

    def __post_init__(self) -> None:
        if self.lookback < 2:
            raise ValueError(f"lookback must be >= 2, got {self.lookback}")
        if self.long_asset not in ("SPY", "SSO"):
            raise ValueError(
                f"long_asset must be SPY or SSO, got {self.long_asset!r}"
            )
        if self.signal_feed not in ("VIXY", "VXX"):
            raise ValueError(
                f"signal_feed must be VIXY or VXX, got {self.signal_feed!r}"
            )
        if self.off_asset_return not in ("TLT", "NONE"):
            raise ValueError(
                f"off_asset_return must be TLT or NONE, got {self.off_asset_return!r}"
            )
        if self.sso_expense_annual < 0:
            raise ValueError("sso_expense_annual must be >= 0")
        if self.commission_bps < 0:
            raise ValueError("commission_bps must be >= 0")
        if self.spread_bps < 0:
            raise ValueError("spread_bps must be >= 0")
        if not 0.0 <= self.tax_rate < 1.0:
            raise ValueError("tax_rate must be in [0, 1)")

    @property
    def switch_cost_pct(self) -> float:
        """Combined commission + spread as fraction, applied once per switch."""
        return (self.commission_bps + self.spread_bps) / 10_000.0


@dataclass
class H2VixTermResult:
    """Simulation output for a single H2.c config."""

    equity: pd.Series  # daily equity path, start = 1.0
    daily_returns: pd.Series  # net daily returns aligned to equity
    regime: pd.Series  # 1 = risk-on (SPY/SSO), 0 = risk-off (TLT/cash)
    switches: pd.Series  # bool True on regime-change bar
    cum_cost_pct: float
    cum_tax_pct: float
    n_switches: int
    long_days: int
    off_days: int

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        if sd == 0.0:
            return 0.0
        return float(r.mean() / sd * np.sqrt(periods_per_year))

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

    def median_hold_days(self) -> float:
        """Median length (in days) of a single contiguous risk-on run."""
        r = self.regime.dropna()
        if r.empty:
            return float("nan")
        blocks: list[int] = []
        cur = 0
        prev = None
        for v in r.to_numpy():
            vi = int(v)
            if prev is None:
                cur = 1
            elif vi == prev:
                cur += 1
            else:
                if prev == 1:
                    blocks.append(cur)
                cur = 1
            prev = vi
        if prev == 1 and cur > 0:
            blocks.append(cur)
        if not blocks:
            return float("nan")
        return float(np.median(blocks))


def compute_vix_regime_signal(
    signal_feed_close: pd.Series,
    lookback: int,
    threshold: float = 0.0,
) -> pd.Series:
    """Return a daily 1/0 regime series from a VIX-ETF close series.

    Signal at day t uses close[t-1] and close[t-1-lookback] — strictly
    past data only (F2 alignment). The caller applies the resulting
    signal to returns on day t via ``prev_weight × ret``.

    Parameters
    ----------
    signal_feed_close : pd.Series
        VIXY or VXX daily close series, DatetimeIndex.
    lookback : int
        Trailing window for the return (in trading days).
    threshold : float
        Decision threshold. Default 0.0 (pure sign rule).

    Returns
    -------
    pd.Series
        Int series {0, 1} or NaN (warmup) on the same index.
    """
    if lookback < 2:
        raise ValueError(f"lookback must be >= 2, got {lookback}")
    s = signal_feed_close.astype(float).sort_index()
    # Trailing return using close values; shift by 1 so day t reads
    # close[t-1] only.
    trail_ret = (s / s.shift(lookback) - 1.0).shift(1)
    regime = pd.Series(np.nan, index=s.index, dtype="float64")
    valid = trail_ret.notna()
    regime[valid] = (trail_ret[valid] <= threshold).astype(float)
    return regime


def simulate_h2_vix_term_structure(
    spy_close: pd.Series,
    tlt_close: pd.Series,
    vixy_close: pd.Series,
    vxx_close: pd.Series,
    config: H2VixTermConfig,
    *,
    sso_close: pd.Series | None = None,
) -> H2VixTermResult:
    """Run a single H2.c regime-rotation simulation end-to-end.

    Parameters
    ----------
    spy_close, tlt_close, vixy_close, vxx_close : pd.Series
        Daily adjusted-close series. Must cover the joint intersection
        of the requested config's window (union-left-join inner on
        the output index).
    config : :class:`H2VixTermConfig`
        Frozen config for this cell.
    sso_close : pd.Series | None
        Required only when ``config.long_asset == "SSO"``.

    Returns
    -------
    :class:`H2VixTermResult`
    """
    if config.long_asset == "SSO" and sso_close is None:
        raise ValueError("sso_close required when long_asset == 'SSO'")

    # --- Build the common index ---
    long_close = sso_close if config.long_asset == "SSO" else spy_close
    if long_close is None:
        raise ValueError("long asset close series is None")

    feed_close = vixy_close if config.signal_feed == "VIXY" else vxx_close

    # Intersect indices to guarantee aligned daily returns.
    idx = long_close.index
    if config.off_asset_return == "TLT":
        idx = idx.intersection(tlt_close.index)
    idx = idx.intersection(feed_close.index).sort_values()

    if len(idx) < config.lookback + 10:
        raise ValueError(
            f"insufficient overlap: {len(idx)} bars, need "
            f"> {config.lookback + 10}"
        )

    long_c = long_close.loc[idx].astype(float)
    feed_c = feed_close.loc[idx].astype(float)
    tlt_c = tlt_close.loc[idx].astype(float) if config.off_asset_return == "TLT" else None

    # --- Regime signal (no lookahead) ---
    regime = compute_vix_regime_signal(
        feed_c, lookback=config.lookback, threshold=config.threshold
    )

    # --- Daily returns on each leg ---
    long_ret = long_c.pct_change(fill_method=None).fillna(0.0)
    if tlt_c is not None:
        off_ret = tlt_c.pct_change(fill_method=None).fillna(0.0)
    else:
        off_ret = pd.Series(0.0, index=idx)

    # SSO embedded-expense drag on RISK_ON only (daily fraction).
    sso_daily_fee = (
        config.sso_expense_annual / TRADING_DAYS_PER_YEAR
        if config.long_asset == "SSO"
        else 0.0
    )

    # --- Walk the simulation day-by-day for switch-cost + DARF accounting ---
    equity = 1.0
    entry_equity = 1.0  # book value at last RISK_ON entry — for DARF
    year_start_equity = 1.0  # for annual DARF sweep
    last_year: int | None = None

    eq_curve: list[float] = []
    net_ret: list[float] = []
    switches = pd.Series(False, index=idx)
    prev_regime: int | None = None
    cum_cost = 0.0
    cum_tax = 0.0
    n_switches = 0
    long_days = 0
    off_days = 0

    reg_v = regime.to_numpy()
    long_r_v = long_ret.to_numpy()
    off_r_v = off_ret.to_numpy()
    dates = idx.to_numpy()

    # t-1 regime is applied to day-t return (F2-patched alignment).
    # Iterate over t from 0..n-1; initial prev_regime=None → warmup.
    for i, ts in enumerate(idx):
        cur_regime_f = reg_v[i]
        if not np.isfinite(cur_regime_f):
            # Warmup — flat cash, 0 return.
            eq_curve.append(equity)
            net_ret.append(0.0)
            last_year = pd.Timestamp(ts).year
            continue
        cur_regime = int(cur_regime_f)

        # Switch-cost + DARF at regime transition, realized at open of
        # the new regime (deducted BEFORE applying new regime's return).
        if prev_regime is not None and cur_regime != prev_regime:
            switches.iloc[i] = True
            n_switches += 1
            cost = config.switch_cost_pct * equity
            equity -= cost
            cum_cost += cost
            # DARF on realized LONG leg gain — only when EXITING risk-on.
            if prev_regime == 1 and config.tax_rate > 0:
                gain = max(0.0, equity - entry_equity)
                tax = gain * config.tax_rate
                equity -= tax
                cum_tax += tax
            # New risk-on entry — reset book value.
            if cur_regime == 1:
                entry_equity = equity

        # Annual DARF sweep (year boundary) — reset yearly book value.
        # Skipped if mid-year; applied at first bar of new year on any
        # residual realized gain since year_start_equity. Matches Inter
        # monthly DARF-approximation with annual realization heuristic.
        this_year = pd.Timestamp(ts).year
        if last_year is not None and this_year != last_year and config.tax_rate > 0:
            # No realized trade — but if still in RISK_ON, book is not
            # realized. Keep entry_equity and year_start_equity aligned
            # so a future exit DARF only taxes gain since last realization.
            year_start_equity = equity
        last_year = this_year

        # Compute today's per-leg return + SSO expense drag.
        if cur_regime == 1:
            r = float(long_r_v[i])
            if sso_daily_fee > 0:
                r -= sso_daily_fee
            long_days += 1
        else:
            r = float(off_r_v[i])
            off_days += 1

        new_equity = equity * (1.0 + r)
        day_net = (new_equity / eq_curve[-1] - 1.0) if eq_curve else 0.0
        eq_curve.append(new_equity)
        net_ret.append(day_net)
        equity = new_equity
        prev_regime = cur_regime

    equity_s = pd.Series(eq_curve, index=idx[: len(eq_curve)], dtype=float)
    ret_s = pd.Series(net_ret, index=idx[: len(net_ret)], dtype=float)

    return H2VixTermResult(
        equity=equity_s,
        daily_returns=ret_s,
        regime=regime,
        switches=switches,
        cum_cost_pct=float(cum_cost),
        cum_tax_pct=float(cum_tax),
        n_switches=int(n_switches),
        long_days=int(long_days),
        off_days=int(off_days),
    )
