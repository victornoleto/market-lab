"""Phase 3.8 B1 — Gayed canonical 1-leg SMA-200 LETF rotation (rota B Inter).

Canonical Leverage Rotation Strategy exactly as specified in the Gayed
SSRN paper (Gayed 2016/2020). One underlying (SPX-TR stitched), one
leveraged leg (UPRO-3x or SSO-2x — synth pre-inception, real post),
one risk-off leg (cash-sleeve annualized). No VIX overlay, no grid
over MA length — the paper's canonical ``SMA-200`` is used verbatim.

Thesis (literal Gayed p.7-8, p.13-17)
-------------------------------------

* ``[leverage_for_the_long_run, p.7-8]`` — Volatility is the enemy of
  leverage; SMA is primarily a **volatility-regime** signal, not a
  trend signal. Above the MA, the index exhibits positive
  autocorrelation (streaks) and lower forward volatility — the
  compounding-friendly regime for daily-leveraged exposure.
* ``[leverage_for_the_long_run, p.13-17, Table 8]`` — Canonical LRS:
  *if price > SMA-200 → leveraged S&P 500 (2x or 3x), else T-bill*.
  Table 8 (1928-2020): 3x 200d LRS delivers CAGR 26.7%, Sharpe 0.61,
  MDD -92.2%; 2x 200d LRS delivers CAGR 19.0%, Sharpe 0.61, MDD
  -78.7%. These are the paper's headline numbers for our canonical
  exercise.
* ``[leverage_for_the_long_run, p.21]`` — ETF implementation uses
  **cash** (not BIL) on RISK_OFF; we use a flat annualized cash rate
  (``cash_rate_annual``) as a proxy.
* ``[leverage_for_the_long_run, p.16]`` — SMA-200 is the
  minimum-turnover period (~5 rotations/yr) and is recommended over
  shorter MAs for implementation. Our B1 test is the canonical
  SMA-200 only — **no MA grid** in this module (that is the B2 job).

Signal (canonical, t-1 data only — F2-alignment)
------------------------------------------------

    sma200_{t-1}  = SMA(SPX-TR_close, 200) through t-1
    regime_t      = 1 if SPX-TR_close_{t-1} > sma200_{t-1} else 0
    exposure_t    = leverage × regime_t     (so 0 or L when ON)

Lookahead audit
---------------

For each trading day ``t``:

* ``close_{t-1}`` and ``SMA(200)_{t-1}`` are both known before the
  t-open → the regime flag used for the bar ``t`` position is built
  **from t-1 data only**. We enforce this via
  ``regime = (close > SMA).shift(1).fillna(0)``.
* Daily returns at ``t`` are applied via F2-alignment
  ``daily_pnl_t = prev_weight_t × return_t`` where
  ``prev_weight_t = exposure_t`` (the exposure we carried into bar t
  after seeing t-1 data). Concretely, we compute
  ``gross_t = gate_t × letf_return_t + (1 − gate_t) × cash_daily``
  where ``gate_t`` is the 0/1 version of exposure — the product
  ``exposure_t × return_t`` is equivalent because the LETF return is
  already the leveraged return, so multiplying the gate by the LETF
  return yields the correct leveraged on-regime return.
* No look-ahead on tax: year-end DARF is applied on the **last
  trading day of the calendar year** using only the equity path
  realized through that day — the next-year path has no influence on
  that year's tax.
* No look-ahead on synth LETF: the FFR-aware synth uses the FFR
  value at time ``t`` to compute the cost for the return at ``t`` —
  this is the correct convention since FFR is public at open on day
  ``t`` (central-bank-published).

Citations sweep
---------------

* LRS canonical signal: ``[leverage_for_the_long_run, p.13-17]``.
* SMA as vol-regime: ``[leverage_for_the_long_run, p.7, p.11]``.
* SMA-200 recommended (~5 trades/yr): ``[leverage_for_the_long_run, p.16]``.
* Cash (not BIL) on RISK_OFF: ``[leverage_for_the_long_run, p.21]``.
* Synth LETF formula + ER 0.95%: ``[leverage_for_the_long_run, p.16]``.
* F2-alignment (prev_weight × ret): ``[advances_fin_ml, p.31-34]``.
* Rota B Inter cost model (DARF 15% year-end): ``docs/investment-mandate.md §4.6``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from ai_trade.backtest.helpers.synthetic_letf import (
    DEFAULT_EXPENSE_RATIO,
    DEFAULT_FFR_SPREAD,
    DEFAULT_SWAP_EXPOSURE,
    TRADING_DAYS_PER_YEAR,
    synthesize_letf_returns_ffr_aware,
)

log = logging.getLogger(__name__)

__all__ = [
    "B1Config",
    "B1Result",
    "UPRO_REAL_START",
    "SSO_REAL_START",
    "apply_darf_year_end",
    "compute_regime_signal",
    "simulate_b1",
    "stitch_letf_returns",
]


# Inception dates of the real LETFs — synth is used strictly before these,
# real adj_close pct_change strictly on/after.
UPRO_REAL_START = pd.Timestamp("2009-06-25")
"""UPRO (3x S&P 500) Tiingo inception — first real pct_change bar."""

SSO_REAL_START = pd.Timestamp("2006-06-21")
"""SSO (2x S&P 500) Tiingo inception — first real pct_change bar."""


LETFKind = Literal["UPRO", "SSO"]


@dataclass(frozen=True)
class B1Config:
    """Immutable config for a single B1 variant backtest.

    The canonical Gayed parameters are **frozen** — no OOS sweep. The
    only user-facing axis is the leverage/real-ETF choice (UPRO-3x or
    SSO-2x), documented in the B1 hypothesis spec.

    Parameters
    ----------
    leverage : float
        Daily leverage factor. ``3.0`` for UPRO variant, ``2.0`` for SSO.
        Gayed tests 1.25/2/3 [p.17 Table 8].
    letf_kind : {"UPRO", "SSO"}
        Which real LETF is stitched post-inception. Determines the
        inception date used for synth → real handoff.
    sma_period : int
        MA lookback on SPX-TR close. **Always 200** per Gayed canonical
        [p.16]. Exposed so the B2 (`MA sweep`) module can re-use this
        config, but B1 itself does not sweep.
    expense_ratio : float
        Annualized LETF ER applied in the synth formula. Default
        0.0095 (0.95% = current UPRO/SSO ER per [p.16] footnote 23).
    swap_exposure, ffr_spread : float
        FFR-aware synth cost params (testfolio model). Defaults track
        :mod:`synthetic_letf`.
    cash_rate_annual : float
        Flat annualized cash-sleeve return (RISK_OFF days). Default
        0.04 (~long-run 3-mo T-bill proxy per mandate §4.6).
    commission_bps, spread_bps : float
        Per-regime-switch cost in bps (sum gets deducted on transition
        days). Default 0/5 = 5 bps total per switch (Inter zero
        commission + 5 bps half-spread for equity ETF).
    tax_rate : float
        DARF rate on realized year-end net gain. Default 0.15 (rota B
        Inter, mandate §4.6). Set to 0.0 to disable for ablation.
    use_real_letf : bool
        If True, stitch the real LETF pct_change starting on its
        inception (``UPRO_REAL_START`` or ``SSO_REAL_START``); else use
        synth throughout. Default True.
    """

    leverage: float = 3.0
    letf_kind: LETFKind = "UPRO"
    sma_period: int = 200
    expense_ratio: float = DEFAULT_EXPENSE_RATIO
    swap_exposure: float = DEFAULT_SWAP_EXPOSURE
    ffr_spread: float = DEFAULT_FFR_SPREAD
    cash_rate_annual: float = 0.04
    commission_bps: float = 0.0
    spread_bps: float = 5.0
    tax_rate: float = 0.15
    use_real_letf: bool = True

    def __post_init__(self) -> None:
        if self.leverage <= 0:
            raise ValueError(f"leverage must be > 0, got {self.leverage}")
        if self.letf_kind not in ("UPRO", "SSO"):
            raise ValueError(
                f"letf_kind must be UPRO or SSO, got {self.letf_kind!r}"
            )
        if self.sma_period <= 1:
            raise ValueError(
                f"sma_period must be > 1, got {self.sma_period}"
            )

    @property
    def switch_cost_pct(self) -> float:
        """Combined commission+spread per regime switch, fraction."""
        return (self.commission_bps + self.spread_bps) / 10_000.0

    @property
    def real_start(self) -> pd.Timestamp:
        """Inception date of the real LETF for synth → real handoff."""
        return UPRO_REAL_START if self.letf_kind == "UPRO" else SSO_REAL_START


@dataclass
class B1Result:
    """Output of :func:`simulate_b1`.

    Attributes
    ----------
    equity : pd.Series
        Daily equity curve starting at 1.0, **post-tax**.
    daily_returns : pd.Series
        Net daily return series (derived from equity — Sharpe/CAGR
        are consistent).
    regime : pd.Series
        0/1 series — 1 iff the MA regime is ON at t (t-1 shifted).
    exposure : pd.Series
        Leverage factor or 0 per day (= ``leverage * regime``).
    switches : pd.Series
        True on days where exposure changed vs prior day.
    cum_cost_pct : float
        Total switch-cost drag (fraction of starting equity).
    cum_tax_pct : float
        Total DARF paid (fraction of starting equity).
    """

    equity: pd.Series
    daily_returns: pd.Series
    regime: pd.Series
    exposure: pd.Series
    switches: pd.Series
    cum_cost_pct: float = 0.0
    cum_tax_pct: float = 0.0

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        rets = self.daily_returns.dropna()
        if rets.empty:
            return 0.0
        std = float(rets.std(ddof=1))
        if std == 0.0:
            return 0.0
        return float(rets.mean() / std * np.sqrt(periods_per_year))

    def cagr(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        eq = self.equity.dropna()
        if len(eq) < 2:
            return 0.0
        n_periods = len(eq) - 1
        years = n_periods / periods_per_year
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
        dd = eq / peak - 1.0
        return float(dd.min())


def compute_regime_signal(
    spx_price: pd.Series,
    sma_period: int = 200,
) -> pd.Series:
    """Canonical Gayed SMA-regime signal, **t-1 shifted** (F2-alignment).

    Returns a 0/1 integer series — 1 iff ``close_{t-1} > SMA(n)_{t-1}``.

    ``sma_period`` defaults to 200 per Gayed canonical
    [leverage_for_the_long_run, p.16].
    """
    if sma_period <= 1:
        raise ValueError(f"sma_period must be > 1, got {sma_period}")
    px = spx_price.astype(float)
    sma = px.rolling(window=sma_period, min_periods=sma_period).mean()
    raw = (px > sma).astype(float)
    # shift(1) → the signal used to position bar t uses data through t-1 only.
    return raw.shift(1).fillna(0.0).astype(int)


def stitch_letf_returns(
    spx_tr_returns: pd.Series,
    real_letf_returns: pd.Series | None,
    ffr_annualized: pd.Series,
    config: B1Config,
) -> pd.Series:
    """Build the daily LETF return series: synth pre-inception + real post.

    Uses :func:`synthesize_letf_returns_ffr_aware` for the synth leg
    (FFR-aware cost model — testfolio ``cost = SW*(L-1)*(FFR+SP) + ER``
    per ``data/external/README.md`` Task 7a). Switches to real
    ``pct_change`` of ``adj_close`` on and after the LETF inception date
    declared by ``config.real_start``.

    Parameters
    ----------
    spx_tr_returns : pd.Series
        Daily decimal SPX-TR returns. DatetimeIndex sorted asc.
    real_letf_returns : pd.Series | None
        Daily real LETF pct_change (from Tiingo ``adj_close``). If
        ``None`` or ``config.use_real_letf=False``, synth is used throughout.
    ffr_annualized : pd.Series
        Annualized FFR proxy series (e.g. Ken French ``rf × 252``). Must
        cover ``spx_tr_returns.index``.
    config : B1Config

    Returns
    -------
    pd.Series
        Stitched LETF daily returns, same index as ``spx_tr_returns``.
    """
    synth = synthesize_letf_returns_ffr_aware(
        spx_tr_returns,
        leverage=config.leverage,
        ffr_annualized=ffr_annualized,
        swap_exposure=config.swap_exposure,
        ffr_spread=config.ffr_spread,
        expense_ratio=config.expense_ratio,
    )
    if not config.use_real_letf or real_letf_returns is None:
        return synth

    real_aligned = real_letf_returns.reindex(spx_tr_returns.index)
    stitched = synth.copy()
    on_or_after = spx_tr_returns.index >= config.real_start
    mask = on_or_after & real_aligned.notna()
    stitched.loc[mask] = real_aligned.loc[mask].astype(float)
    return stitched


def apply_darf_year_end(
    daily_gross: pd.Series,
    tax_rate: float = 0.15,
) -> tuple[pd.Series, pd.Series, float]:
    """Apply 15% year-end DARF on realized yearly NET gain (rota B Inter).

    Mandate §4.6 model: *at the last trading day of each calendar year,
    if the equity path closed higher than at the prior year-end, subtract
    ``tax_rate × (current_YE_equity − prior_YE_equity)`` from equity*.
    Losses within the year net against gains (we only tax net > 0). No
    cross-year carry — a losing year's loss is not credited against the
    next year's gains (conservative per mandate).

    Parameters
    ----------
    daily_gross : pd.Series
        Daily gross (pre-tax) returns, DatetimeIndex sorted asc.
    tax_rate : float
        Default 0.15. Set to 0.0 to bypass.

    Returns
    -------
    tuple of (equity_post_tax, daily_net, cum_tax_fraction)
        * ``equity_post_tax`` — compounded equity including year-end tax
          drag, indexed as input, starting at 1.0.
        * ``daily_net`` — derived daily return series from
          ``equity_post_tax`` (exact; Sharpe/CAGR will be consistent).
        * ``cum_tax_fraction`` — sum of tax paid / starting equity (1.0).

    Notes
    -----
    The implementation walks the index sequentially so that each
    year's tax is computed only on realized year-end-to-year-end
    gain. The tax deduction hits the **last bar of the year** so the
    equity series reflects it on that day. This is the "year-end
    realization" convention requested by the Plano B prompt.
    """
    if tax_rate < 0:
        raise ValueError(f"tax_rate must be >= 0, got {tax_rate}")

    idx = daily_gross.index
    arr = daily_gross.to_numpy(dtype=float, copy=True)
    # Sanitize non-finite to 0 (defensive; input should not have NaN
    # after the simulator's gross construction, but be explicit).
    arr = np.where(np.isfinite(arr), arr, 0.0)

    years = pd.Series(idx).dt.year.to_numpy()
    is_last_day_of_year = np.zeros(len(idx), dtype=bool)
    if len(idx) > 0:
        is_last_day_of_year[-1] = True
        for i in range(len(idx) - 1):
            if years[i] != years[i + 1]:
                is_last_day_of_year[i] = True

    equity = 1.0
    prior_ye_equity = 1.0
    cum_tax = 0.0
    equity_path = np.empty(len(idx), dtype=float)

    for i in range(len(idx)):
        equity *= 1.0 + arr[i]
        if is_last_day_of_year[i] and tax_rate > 0.0:
            gain = max(0.0, equity - prior_ye_equity)
            tax = gain * tax_rate
            equity -= tax
            cum_tax += tax
            prior_ye_equity = equity
        equity_path[i] = equity

    eq_series = pd.Series(equity_path, index=idx, name="equity_b1")
    # Derive daily net return from the final equity path so it is
    # exactly consistent with Sharpe/CAGR computed downstream.
    if len(eq_series) > 0:
        daily_net = eq_series.pct_change().fillna(eq_series.iloc[0] - 1.0)
        daily_net.name = "daily_b1_net"
    else:
        daily_net = pd.Series(dtype=float)
    return eq_series, daily_net, cum_tax


def simulate_b1(
    spx_tr_returns: pd.Series,
    spx_tr_price: pd.Series,
    ffr_annualized: pd.Series,
    config: B1Config,
    real_letf_returns: pd.Series | None = None,
) -> B1Result:
    """Run one B1 canonical config end-to-end.

    Pipeline
    --------

    1. Compute the SMA-regime signal on ``spx_tr_price`` with ``t-1``
       shift (F2-alignment).
    2. Stitch the LETF return series (synth pre-inception + real post).
    3. Build the binary gate and the **gross** (pre-tax, post-switch)
       daily return series:
       ``gross_t = gate_t × letf_t + (1 − gate_t) × cash_daily − switch_cost``.
    4. Apply **year-end DARF** via :func:`apply_darf_year_end` to
       transform gross → post-tax equity and post-tax daily returns.

    Parameters
    ----------
    spx_tr_returns : pd.Series
        Daily SPX-TR decimal returns.
    spx_tr_price : pd.Series
        Daily SPX-TR cumulative price (``(1+r).cumprod() * 100``).
        Must share index with ``spx_tr_returns``.
    ffr_annualized : pd.Series
        Annualized FFR proxy aligned to ``spx_tr_returns``.
    config : B1Config
    real_letf_returns : pd.Series | None
        Daily real LETF pct_change for post-inception stitch. None →
        synth throughout.

    Returns
    -------
    B1Result

    Raises
    ------
    ValueError
        If index alignment is violated.
    """
    if not spx_tr_returns.index.equals(spx_tr_price.index):
        raise ValueError("spx_tr_returns and spx_tr_price must share index")
    if not ffr_annualized.index.equals(spx_tr_returns.index):
        ffr_annualized = (
            ffr_annualized.reindex(spx_tr_returns.index).ffill().bfill()
        )

    regime = compute_regime_signal(spx_tr_price, sma_period=config.sma_period)

    letf = stitch_letf_returns(
        spx_tr_returns, real_letf_returns, ffr_annualized, config
    ).fillna(0.0)

    cash_daily = config.cash_rate_annual / TRADING_DAYS_PER_YEAR
    # Binary gate — identical to regime, kept as float for arithmetic.
    gate = regime.astype(float)
    exposure = (gate * config.leverage).astype(float)

    # Gross daily return before switch cost + tax.
    #   on-regime:  gate=1 → gate * letf = letf (already leveraged)
    #   off-regime: gate=0 → (1-gate) * cash_daily = cash_daily
    gross_noswitch = gate * letf + (1.0 - gate) * cash_daily

    # Switch detection on exposure (canonical per H2 template). A
    # transition day's return absorbs the round-trip switch cost.
    prev_exp = exposure.shift(1).fillna(0.0)
    switches = exposure != prev_exp
    switch_drag = switches.astype(float) * config.switch_cost_pct

    gross = gross_noswitch - switch_drag
    cum_cost = float(switch_drag.sum())

    # Year-end DARF → post-tax equity + daily series consistent with it.
    equity, daily_net, cum_tax = apply_darf_year_end(gross, config.tax_rate)

    return B1Result(
        equity=equity,
        daily_returns=daily_net,
        regime=regime,
        exposure=exposure,
        switches=switches,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
    )
