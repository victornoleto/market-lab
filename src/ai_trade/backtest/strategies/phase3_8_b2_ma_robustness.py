"""Phase 3.8 B2 — Gayed MA-robustness sweep LETF rotation (rota B Inter).

Hypothesis under test
---------------------

Gayed tests MA periods of 10, 20, 50, 100, 200 days for the Leverage
Rotation Strategy (LRS) and reports **all are robust** — annual alpha
5.2%-6.4% and Sharpe 0.58-0.68 across the grid
[leverage_for_the_long_run, p.14, Table 6; p.16; p.17]. Turnover
ranges from ~38 trades/yr (10d MA) to ~5 trades/yr (200d MA)
[p.14, Table 6; p.16].

B1 ran the canonical SMA-200 only and **FAILED** both 2x (SSO) and 3x
(UPRO) legs under rota B Inter cost model (DARF 15% + FX spread +
ER 0.95%): gate 10 (bootstrap OOS CI>0) and gate 12 (DSR p<0.05)
failed, with OOS Sharpe 0.37-0.39 and CAGR 6.10-6.86% Folclore tier.

B2 tests whether Gayed's robustness claim — valid in the **pre-tax**
world of the paper — survives the **post-DARF** rota B environment.
Shorter MAs switch more often (gayed p.14, Table 6: 10-day ~38/yr;
100-day ~15/yr), and each switch that materializes a gain in the
calendar year can trigger DARF. We thus sweep:

* ``ma_type ∈ {SMA, EMA}`` — SMA per Gayed canonical; EMA as
  low-lag variant for comparison [cycle_analytics, p.9-10, ch.1-2]
  (paper does not test EMA; we extend per B2 prompt spec).
* ``ma_period ∈ {100, 125, 150, 200}`` — 100 and 200 direct Gayed
  grid points [leverage_for_the_long_run, p.14, Table 6]; 125 and
  150 are interpolated robustness points (inside Gayed's tested
  range, fulfilling 16-config PBO-meaningful family).
* ``leg ∈ {UPRO, SSO}`` — both Gayed-endorsed leverage levels
  [leverage_for_the_long_run, p.17, Table 8].

16 configs total; one feature family, so PBO is single-block CSCV
and the PBO gate is tightened to ``< 0.3`` per B2 prompt spec.

Lookahead audit
---------------

For each trading day ``t``:

* ``close_{t-1}`` and ``MA(n)_{t-1}`` are both known before the
  t-open — the regime flag used for the bar ``t`` position is built
  **from t-1 data only**. We enforce this via
  ``regime = (close > MA).shift(1).fillna(0)``.
* Daily returns at ``t`` are applied via F2-alignment
  ``daily_pnl_t = prev_weight_t × return_t`` where
  ``prev_weight_t = exposure_t``.
* No look-ahead on tax: year-end DARF via the shared
  :func:`phase3_8_b1_gayed_canonical.apply_darf_year_end` applies on
  the **last trading day of the calendar year** using only the
  equity path realized through that day.
* No look-ahead on synth LETF: the FFR-aware synth uses the FFR
  value at time ``t`` (central-bank-published at open).
* EMA is an IIR recursion with no future lookahead; the shift(1)
  on the output is applied identically to the SMA branch.

Signal spec (literal)
---------------------

For each config ``(ma_type, ma_period, leg)``::

    price = (1 + spx_tr_returns).cumprod() * 100
    if ma_type == "SMA":
        ma = SMA(price, window=ma_period)
    elif ma_type == "EMA":
        ma = EMA(price, span=ma_period, adjust=False)

    regime_t = 1 if price_{t-1} > ma_{t-1} else 0
    on_asset = UPRO (L=3) if leg == "UPRO" else SSO (L=2)
    off_asset = cash_daily (= cash_rate_annual / 252)

Citations sweep
---------------

* Gayed MA-period robustness: ``[leverage_for_the_long_run, p.14,
  Table 6; p.16]``.
* Gayed turnover by MA period: ``[leverage_for_the_long_run, p.14,
  Table 6; p.202]`` (shorter MA ⇒ higher turnover).
* Gayed 200d recommended (low turnover):
  ``[leverage_for_the_long_run, p.16]``.
* Gayed leverage grid 2x/3x: ``[leverage_for_the_long_run, p.17,
  Table 8]``.
* EMA lag / IIR recursion: ``[cycle_analytics, p.9-10, ch.1-2]``.
* F2-alignment (prev_weight × ret): ``[advances_fin_ml, p.31-34]``.
* PBO < 0.3 tighter single-feature family: B2 prompt
  ``docs/plans/2026-04-22-phase3.8-1-plano-b-hunt-prompt.md §B2``
  (spec decision; rationale: more configs ⇒ tighter threshold per
  AFML CSCV logic ``[advances_fin_ml, p.208-211]``).
* Rota B Inter cost model: ``docs/investment-mandate.md §4.6``.
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
)
from ai_trade.backtest.strategies.phase3_8_b1_gayed_canonical import (
    SSO_REAL_START,
    UPRO_REAL_START,
    apply_darf_year_end,
    stitch_letf_returns,
)

log = logging.getLogger(__name__)

__all__ = [
    "B2Config",
    "B2Result",
    "apply_darf_year_end",  # re-export (tests verify shared helper usage)
    "compute_regime_signal_b2",
    "simulate_b2",
]


MAFilter = Literal["SMA", "EMA"]
LETFKind = Literal["UPRO", "SSO"]


@dataclass(frozen=True)
class B2Config:
    """Immutable config for a single B2 MA-robustness variant.

    Parameters
    ----------
    filter : {"SMA", "EMA"}
        MA kernel: simple (canonical Gayed) or exponential (low-lag
        extension, ``[cycle_analytics, p.9-10, ch.1-2]``). Validated
        in __post_init__.
    ma_period : int
        MA window length. Must be > 1. B2 prompt grid is
        ``{100, 125, 150, 200}``; 100 and 200 are direct Gayed
        points [leverage_for_the_long_run, p.14, Table 6].
    leg : {"UPRO", "SSO"}
        Which leveraged ETF sits in the on-regime bucket. Determines
        ``leverage`` (3 for UPRO, 2 for SSO) and the real-ETF
        inception date for the synth → real stitch.
    expense_ratio : float
        Annualized LETF ER in the synth formula. Default 0.0095
        (0.95% = current UPRO/SSO ER per Gayed p.16 footnote 23).
    swap_exposure, ffr_spread : float
        FFR-aware synth cost params (testfolio model). Defaults
        track :mod:`synthetic_letf`.
    cash_rate_annual : float
        Flat annualized cash-sleeve return (RISK_OFF days). Default
        0.04 (~long-run 3-mo T-bill proxy per mandate §4.6).
    commission_bps, spread_bps : float
        Per-regime-switch cost in bps. Default 0/5 (Inter zero
        commission + 5 bps half-spread).
    tax_rate : float
        DARF rate on realized year-end net gain. Default 0.15 (rota
        B Inter, mandate §4.6). Set to 0.0 for ablation.
    use_real_letf : bool
        If True, stitch the real LETF pct_change on/after inception;
        else use synth throughout. Default True.
    """

    filter: MAFilter = "SMA"
    ma_period: int = 200
    leg: LETFKind = "UPRO"
    expense_ratio: float = DEFAULT_EXPENSE_RATIO
    swap_exposure: float = DEFAULT_SWAP_EXPOSURE
    ffr_spread: float = DEFAULT_FFR_SPREAD
    cash_rate_annual: float = 0.04
    commission_bps: float = 0.0
    spread_bps: float = 5.0
    tax_rate: float = 0.15
    use_real_letf: bool = True

    def __post_init__(self) -> None:
        if self.filter not in ("SMA", "EMA"):
            raise ValueError(
                f"filter must be 'SMA' or 'EMA', got {self.filter!r}"
            )
        if self.leg not in ("UPRO", "SSO"):
            raise ValueError(
                f"leg must be 'UPRO' or 'SSO', got {self.leg!r}"
            )
        if self.ma_period <= 1:
            raise ValueError(
                f"ma_period must be > 1, got {self.ma_period}"
            )

    @property
    def leverage(self) -> float:
        """Daily leverage factor (3 for UPRO, 2 for SSO per Gayed p.17)."""
        return 3.0 if self.leg == "UPRO" else 2.0

    @property
    def switch_cost_pct(self) -> float:
        """Combined commission + spread per switch, fraction."""
        return (self.commission_bps + self.spread_bps) / 10_000.0

    @property
    def real_start(self) -> pd.Timestamp:
        """Inception date of the real LETF for synth → real handoff."""
        return UPRO_REAL_START if self.leg == "UPRO" else SSO_REAL_START


@dataclass
class B2Result:
    """Output of :func:`simulate_b2`. Mirrors B1Result for consistency."""

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


def compute_regime_signal_b2(
    spx_price: pd.Series,
    *,
    filter: MAFilter = "SMA",
    ma_period: int = 200,
) -> pd.Series:
    """MA-regime signal with SMA/EMA selection, **t-1 shifted** (F2-align).

    Returns a 0/1 integer series — 1 iff ``close_{t-1} > MA(n)_{t-1}``.

    SMA branch matches ``phase3_8_b1_gayed_canonical.compute_regime_signal``
    byte-for-byte (so sma_period=200 is identical to B1 canonical).

    EMA branch uses ``pd.Series.ewm(span=n, adjust=False)`` — the
    standard IIR recursion ``[cycle_analytics, p.9-10, ch.1-2]``:
    ``EMA_t = alpha × close_t + (1 - alpha) × EMA_{t-1}``,
    ``alpha = 2 / (n + 1)``. No lookahead: ``ewm`` is causal.

    To avoid a low-quality signal during the EMA warmup, we null the
    first ``ma_period`` bars (analogous to SMA's ``min_periods``) so
    the pre-warmup regime is 0 in both branches.
    """
    if ma_period <= 1:
        raise ValueError(f"ma_period must be > 1, got {ma_period}")
    if filter not in ("SMA", "EMA"):
        raise ValueError(f"filter must be 'SMA' or 'EMA', got {filter!r}")

    px = spx_price.astype(float)
    if filter == "SMA":
        ma = px.rolling(window=ma_period, min_periods=ma_period).mean()
    else:  # EMA
        # EMA is causal (uses only past + current), but it has no warmup
        # NaNs by default. We enforce the same warmup discipline as SMA
        # by masking the first `ma_period` bars to NaN — this keeps
        # apples-to-apples comparison and avoids an early low-quality
        # signal when the EMA is still anchored near the first bar.
        ema = px.ewm(span=ma_period, adjust=False).mean()
        ema.iloc[: ma_period - 1] = np.nan
        ma = ema

    raw = (px > ma).astype(float)
    # shift(1) → bar t position uses data through t-1 only.
    return raw.shift(1).fillna(0.0).astype(int)


def simulate_b2(
    spx_tr_returns: pd.Series,
    spx_tr_price: pd.Series,
    ffr_annualized: pd.Series,
    config: B2Config,
    real_letf_returns: pd.Series | None = None,
) -> B2Result:
    """Run one B2 config end-to-end under rota B Inter cost model.

    Pipeline mirrors B1 with two differences:

    1. Signal uses ``compute_regime_signal_b2`` (SMA or EMA per
       config.filter).
    2. Leverage is derived from ``config.leg`` (3x UPRO or 2x SSO).

    Tax handling delegates to
    :func:`phase3_8_b1_gayed_canonical.apply_darf_year_end` — the
    **single shared DARF helper** per B2 prompt hard constraint.

    Parameters
    ----------
    spx_tr_returns : pd.Series
        Daily SPX-TR decimal returns.
    spx_tr_price : pd.Series
        Daily SPX-TR cumulative price, shared index with ``returns``.
    ffr_annualized : pd.Series
        Annualized FFR proxy aligned to ``returns``.
    config : B2Config
    real_letf_returns : pd.Series | None
        Daily real LETF pct_change for post-inception stitch. None →
        synth throughout.

    Returns
    -------
    B2Result
    """
    if not spx_tr_returns.index.equals(spx_tr_price.index):
        raise ValueError("spx_tr_returns and spx_tr_price must share index")
    if not ffr_annualized.index.equals(spx_tr_returns.index):
        ffr_annualized = (
            ffr_annualized.reindex(spx_tr_returns.index).ffill().bfill()
        )

    regime = compute_regime_signal_b2(
        spx_tr_price,
        filter=config.filter,
        ma_period=config.ma_period,
    )

    # Reuse B1's stitching (synth pre-inception + real post) by
    # building a shim config object with the two fields stitch_letf
    # cares about (leverage + letf_kind + use_real_letf + expense/ffr
    # params).  We construct an internal B1Config so the shared helper
    # is literally the B1 path — zero drift.
    from ai_trade.backtest.strategies.phase3_8_b1_gayed_canonical import (
        B1Config,
    )

    b1_shim = B1Config(
        leverage=config.leverage,
        letf_kind=config.leg,
        sma_period=200,  # unused in stitch_letf_returns
        expense_ratio=config.expense_ratio,
        swap_exposure=config.swap_exposure,
        ffr_spread=config.ffr_spread,
        cash_rate_annual=config.cash_rate_annual,
        commission_bps=config.commission_bps,
        spread_bps=config.spread_bps,
        tax_rate=config.tax_rate,
        use_real_letf=config.use_real_letf,
    )
    letf = stitch_letf_returns(
        spx_tr_returns, real_letf_returns, ffr_annualized, b1_shim
    ).fillna(0.0)

    cash_daily = config.cash_rate_annual / TRADING_DAYS_PER_YEAR
    gate = regime.astype(float)
    exposure = (gate * config.leverage).astype(float)

    # Gross daily return before switch cost + tax (identical to B1).
    gross_noswitch = gate * letf + (1.0 - gate) * cash_daily

    prev_exp = exposure.shift(1).fillna(0.0)
    switches = exposure != prev_exp
    switch_drag = switches.astype(float) * config.switch_cost_pct

    gross = gross_noswitch - switch_drag
    cum_cost = float(switch_drag.sum())

    # Year-end DARF via the **shared** helper (hard constraint).
    equity, daily_net, cum_tax = apply_darf_year_end(gross, config.tax_rate)

    return B2Result(
        equity=equity,
        daily_returns=daily_net,
        regime=regime,
        exposure=exposure,
        switches=switches,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
    )
