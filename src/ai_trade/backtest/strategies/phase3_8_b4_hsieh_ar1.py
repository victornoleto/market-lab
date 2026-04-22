"""Phase 3.8 B4 — Hsieh-Chang-Chen 2025 AR(1) regime filter LETF rotation.

Novel regime filter based on the **return-autocorrelation thesis** of
Hsieh, Chang, Chen (2025) "Compounding Effects in Leveraged ETFs:
Beyond the Volatility Drag Paradigm" (arXiv 2504.20116).

Thesis (Hsieh-Chang-Chen 2025)
------------------------------

Contrary to the "volatility drag is destiny" paradigm, LETF performance
is **conditional on return autocorrelation**:

* **AR(1) > 0** (positive serial correlation, i.e. trending regime) →
  daily-rebalance leveraged compounding **amplifies** returns; LETF
  outperforms naive × L buy-hold.
* **AR(1) < 0** (mean-reverting regime) → daily rebalance **bleeds**
  from whipsaw drag; LETF decays vs the theoretical × L payoff.

This is a **novel** regime filter versus Gayed's SMA-200 (B1 canonical):
SMA-200 is a coarse proxy for "trending market" (Gayed p.7-8 explicitly
frames SMA as a volatility-regime signal), whereas AR(1) **directly
measures** the serial-correlation property that theoretically drives
LETF amplification vs decay.

Citation mapping
----------------

* ``[phase3_7_literature_sprint §T1, arXiv 2504.20116]`` — AR(1) as the
  primary regime signal; tested on SPY/QQQ + multi-L LETFs ~20y.
* ``[leverage_for_the_long_run, p.4]`` — Gayed's own framing: "AR(1) > 0
  is the statistical signature of a trending market where compounding
  works in your favor". B4 directly operationalizes this.
* ``[leverage_for_the_long_run, p.7-8]`` — same SMA-as-volatility-regime
  thesis B1 inherits; B4 is the AR(1) cousin.
* ``[advances_fin_ml, p.31-34]`` — F2-alignment ``prev_weight × ret``.
* ``docs/investment-mandate.md §4.6`` — rota B Inter cost model.

Signal (literal spec, t-1 data only)
------------------------------------

For each trading day ``t``:

    # Use ONLY returns through t-1 (no look-ahead). The 63-day window
    # ending at t-1 is fit to the AR(1) model
    #     r_i = α + β × r_{i-1} + ε
    # via ordinary least squares on the pairs (r_lagged, r_current),
    # where r_lagged = window[:-1], r_current = window[1:].
    window        = r[t - lookback : t - 1]       # inclusive of t-lookback
    beta_{t-1}    = Cov(window[:-1], window[1:]) / Var(window[:-1])
    regime_t      = 1 if beta_{t-1} > 0 else 0
    exposure_t    = leverage × regime_t

The vectorized covariance formula
``β = Cov(r_{i-1}, r_i) / Var(r_{i-1})`` is **mathematically identical**
to ordinary least squares on the pair series but ~100× faster than
``.rolling(n).apply(lambda w: ...)``.

Lookahead audit
---------------

* ``r_t-1`` and the preceding 62 returns are both observable at
  market-open t → the β slope used to gate bar ``t`` uses **only** data
  through ``t-1``. We enforce this via ``regime = raw.shift(1)``.
* Daily returns at ``t`` are applied via F2-alignment
  ``daily_pnl_t = prev_weight_t × return_t`` — the prev_weight is the
  exposure we carried into bar ``t`` after observing through ``t-1``.
  Concretely, ``gross_t = gate_t × letf_t + (1 − gate_t) × cash_daily``
  where ``gate_t ∈ {0, 1}`` is built from ``regime_t`` (already shifted).
* Year-end DARF realization: we **reuse** ``apply_darf_year_end`` from
  B1 so the tax semantics are identical across the Plano B hunt (no
  code duplication).
* Synth LETF FFR-awareness: the cost for return ``t`` uses FFR at ``t``,
  which is public at open (central-bank publication) — no look-ahead.

Parameter choices
-----------------

* **Lookback = 63 trading days** (default, paper-central). Our choice
  matches the Hsieh 2025 paper's primary specification and is included
  in a robustness sweep ``{42, 63, 84, 126}`` = {≈2, 3, 4, 6 months}
  documented in the PBO grid of the runner.
* **Leverage variants:** UPRO-3x and SSO-2x — identical to B1 (lowest
  turnover LETF choices in the Tiingo catalogue, ER 0.95%).
* **On-regime:** 100% LETF (no scaling by β magnitude — the paper uses
  sign-based regime; scaling-by-magnitude is a future extension).
* **Off-regime:** 100% cash (``cash_rate_annual=0.04`` flat — same as
  B1 per mandate §4.6).

Expected turnover
-----------------

AR(1) sign flips more often than an SMA-200 crossing (rolling OLS on a
63-day window is noisier than a 200-day MA by construction). Paper
estimates implicit ~12-20 regime changes per year versus Gayed's
~5/year. This is the **highest DARF-risk hypothesis** of the Plano B
hunt — the honest-gate stack (Gate 13 cost×2) is precisely where B4
will be stress-tested.
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
from ai_trade.backtest.strategies.phase3_8_b1_gayed_canonical import (
    SSO_REAL_START,
    UPRO_REAL_START,
    apply_darf_year_end,
)

log = logging.getLogger(__name__)

__all__ = [
    "B4Config",
    "B4Result",
    "UPRO_REAL_START",
    "SSO_REAL_START",
    "compute_ar1_regime_signal",
    "rolling_ar1_beta",
    "simulate_b4",
    "stitch_letf_returns",
]


LETFKind = Literal["UPRO", "SSO"]


@dataclass(frozen=True)
class B4Config:
    """Immutable config for a single B4 variant backtest.

    Parameters
    ----------
    leverage : float
        Daily leverage factor. ``3.0`` for UPRO variant, ``2.0`` for SSO.
    letf_kind : {"UPRO", "SSO"}
        Which real LETF is stitched post-inception.
    ar1_lookback : int
        AR(1) rolling window length in trading days. Default ``63``
        (paper-central); robustness sweep ``{42, 63, 84, 126}``
        documented in the runner's PBO grid.
    expense_ratio : float
        Annualized LETF ER applied in the synth formula. Default 0.95%.
    swap_exposure, ffr_spread : float
        FFR-aware synth cost params. Defaults track :mod:`synthetic_letf`.
    cash_rate_annual : float
        Flat annualized cash-sleeve return (RISK_OFF days). Default 0.04.
    commission_bps, spread_bps : float
        Per-regime-switch cost in bps. Default 0/5 (Inter zero
        commission + 5 bps half-spread equity ETF).
    tax_rate : float
        DARF rate on realized year-end net gain. Default 0.15 (rota B
        Inter). Set to 0.0 to disable for ablation.
    use_real_letf : bool
        If True, stitch real LETF pct_change starting on inception.
    """

    leverage: float = 3.0
    letf_kind: LETFKind = "UPRO"
    ar1_lookback: int = 63
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
        if self.ar1_lookback < 10:
            raise ValueError(
                f"ar1_lookback must be >= 10, got {self.ar1_lookback}"
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
class B4Result:
    """Output of :func:`simulate_b4`."""

    equity: pd.Series
    daily_returns: pd.Series
    regime: pd.Series
    exposure: pd.Series
    switches: pd.Series
    ar1_beta: pd.Series
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


def rolling_ar1_beta(returns: pd.Series, lookback: int) -> pd.Series:
    """Vectorized rolling AR(1) slope ``β = Cov(r_{i-1}, r_i) / Var(r_{i-1})``.

    Mathematically identical to OLS fit of ``r_i = α + β r_{i-1} + ε``
    over a rolling window of size ``lookback`` (the window contains
    ``lookback`` observations from which ``lookback - 1`` lagged pairs
    are formed). Uses ``pandas.Series.rolling(...).cov/var`` — ~100× faster
    than ``.rolling(n).apply(...)`` on a 14k-day series.

    NOT shifted — returns the raw β series aligned to the **last date
    of the window**. Callers must apply ``shift(1)`` before using the
    series to gate position at bar ``t``.

    Parameters
    ----------
    returns : pd.Series
        Daily decimal returns, DatetimeIndex sorted asc.
    lookback : int
        Window size (trading days). E.g. ``63`` for 3 months.

    Returns
    -------
    pd.Series
        β series, NaN for the first ``lookback`` observations (warmup).
    """
    if lookback < 2:
        raise ValueError(f"lookback must be >= 2, got {lookback}")
    r = returns.astype(float)
    lag = r.shift(1)

    # The rolling window contains pairs (lag_i, r_i). Over a window of
    # `lookback` observations starting at position `t - lookback + 1`
    # there are `lookback - 1` valid pairs (first position has lag=NaN).
    # We use `min_periods=lookback - 1` so the β is only defined once
    # the window has enough valid pairs.
    cov = r.rolling(window=lookback, min_periods=lookback - 1).cov(lag)
    var = lag.rolling(window=lookback, min_periods=lookback - 1).var(ddof=1)
    # Guard against zero variance (degenerate series).
    beta = cov / var.where(var > 0)
    beta.name = "ar1_beta"
    return beta


def compute_ar1_regime_signal(
    returns: pd.Series,
    lookback: int = 63,
) -> tuple[pd.Series, pd.Series]:
    """Hsieh-Chang-Chen 2025 AR(1) regime, **t-1 shifted** (F2-alignment).

    Returns ``(regime, beta_shifted)`` — both aligned to ``returns``.

    * ``regime`` is 0/1 integer, 1 iff ``beta_{t-1} > 0``.
    * ``beta_shifted`` is the t-1-shifted β series (for audit / testing).

    Parameters
    ----------
    returns : pd.Series
        Daily decimal returns.
    lookback : int
        AR(1) rolling window. Default 63.

    Citations
    ---------
    * ``[phase3_7_literature_sprint §T1, arXiv 2504.20116]``
    """
    if lookback < 10:
        raise ValueError(f"lookback must be >= 10, got {lookback}")
    beta = rolling_ar1_beta(returns, lookback=lookback)
    # shift(1) — β at row t is fit through t; shifting means the signal
    # used to position bar t is β through t-1 (look-ahead-safe).
    beta_shifted = beta.shift(1)
    raw = (beta_shifted > 0).astype(float)
    regime = raw.fillna(0.0).astype(int)
    return regime, beta_shifted


def stitch_letf_returns(
    spx_tr_returns: pd.Series,
    real_letf_returns: pd.Series | None,
    ffr_annualized: pd.Series,
    config: B4Config,
) -> pd.Series:
    """Build daily LETF return series: synth pre-inception + real post.

    Identical semantics to the B1 stitcher (synth FFR-aware pre + real
    pct_change post ``config.real_start``).
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


def simulate_b4(
    spx_tr_returns: pd.Series,
    ffr_annualized: pd.Series,
    config: B4Config,
    real_letf_returns: pd.Series | None = None,
) -> B4Result:
    """Run one B4 AR(1)-regime config end-to-end.

    Pipeline
    --------

    1. Compute the AR(1)-regime signal on ``spx_tr_returns`` with
       ``t-1`` shift (F2-alignment).
    2. Stitch the LETF return series (synth pre-inception + real post).
    3. Build the binary gate and the **gross** (pre-tax, post-switch)
       daily return series.
    4. Apply year-end DARF via ``apply_darf_year_end`` (shared with B1).

    Parameters
    ----------
    spx_tr_returns : pd.Series
        Daily SPX-TR decimal returns.
    ffr_annualized : pd.Series
        Annualized FFR proxy aligned to ``spx_tr_returns``.
    config : B4Config
    real_letf_returns : pd.Series | None
        Daily real LETF pct_change for post-inception stitch.

    Returns
    -------
    B4Result
    """
    if not ffr_annualized.index.equals(spx_tr_returns.index):
        ffr_annualized = (
            ffr_annualized.reindex(spx_tr_returns.index).ffill().bfill()
        )

    regime, beta_shifted = compute_ar1_regime_signal(
        spx_tr_returns, lookback=config.ar1_lookback
    )

    letf = stitch_letf_returns(
        spx_tr_returns, real_letf_returns, ffr_annualized, config
    ).fillna(0.0)

    cash_daily = config.cash_rate_annual / TRADING_DAYS_PER_YEAR
    gate = regime.astype(float)
    exposure = (gate * config.leverage).astype(float)

    # Gross daily return before switch cost + tax.
    gross_noswitch = gate * letf + (1.0 - gate) * cash_daily

    # Switch detection on exposure.
    prev_exp = exposure.shift(1).fillna(0.0)
    switches = exposure != prev_exp
    switch_drag = switches.astype(float) * config.switch_cost_pct

    gross = gross_noswitch - switch_drag
    cum_cost = float(switch_drag.sum())

    # Year-end DARF via SHARED helper from B1 (zero duplication).
    equity, daily_net, cum_tax = apply_darf_year_end(gross, config.tax_rate)

    return B4Result(
        equity=equity,
        daily_returns=daily_net,
        regime=regime,
        exposure=exposure,
        switches=switches,
        ar1_beta=beta_shifted,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
    )
