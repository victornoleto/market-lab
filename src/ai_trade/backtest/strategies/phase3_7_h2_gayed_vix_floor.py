"""Phase 3.7 H2.b — Gayed 2016/2020 LRS × 2x LETF with VIX-floor gate.

Canonical Gayed Leverage Rotation Strategy (SMA-200 regime filter on
SPX-TR) applied to a 2x leveraged ETF (UPRO synthetic pre-2009-06,
real UPRO 2009-06+), **gated by a VIX floor** — only go RISK_ON when
both the MA filter is ON **and** the VIX is below a configured
threshold (default 25.0).

Rationale
---------

* Gayed's LRS is a tail-volatility regime filter: SMA-200 catches the
  structural low-vol regime where 2-3x leverage compounds favourably
  [leverage_for_the_long_run, p.7-8, p.13-17, Table 6-8]. The paper
  reports ~10-16% CAGR uplift over buy-hold at the cost of higher
  drawdowns (~-78.7% for 2x, ~-85% for 3x in the 1928-2015 sample —
  p.17, Table 8). Our H2.a canonical variant reproduced this.
* Bozovic 2024 (`[bozovic_2024_irfa]`) documents that LETF long-hold
  drawdowns are concentrated in high-VIX regimes (VIX > 25) where the
  volatility drag compounds against leverage. Adding a VIX floor
  should trim the worst 20-30% of LETF-on days and reduce MDD without
  hurting CAGR materially.
* Mandate §2.3 rota B MDD tier Reject > 50%; canonical 2x LRS sits at
  the Reject boundary historically. VIX floor is a pre-specified
  mitigation — no OOS peek.

Signal (canonical + VIX gate, **all t-1 data only**)
----------------------------------------------------

    sma200_{t-1}    = SMA(SPY_close, 200) through t-1
    regime_sma_t    = 1 if SPY_close_{t-1} > sma200_{t-1} else 0
    vix_gate_t      = 1 if VIXCLS_{t-1} < vix_threshold else 0
    exposure_t      = leverage * (regime_sma_t AND vix_gate_t)

Daily rebalance at close. When exposure_t==0, the strategy sits in
cash (SHV or flat 4%/yr proxy pre-2007).

Universe
--------

* **SPY** — SPX-TR stitched (Ken French Mkt+RF pre-2001-05-14, Tiingo
  SPY adj_close post). See
  :func:`ai_trade.backtest.data.spx_tr_loader.load_spx_tr_daily`.
* **UPRO / 2x synthetic** — for pre-2009-06 uses
  :func:`ai_trade.backtest.helpers.synthetic_letf.synthesize_letf_returns_ffr_aware`
  with ``leverage=2, expense_ratio=0.0095``. Post-2009-06 uses
  real UPRO daily pct_change from
  ``data/tiingo/daily/prices/UPRO.parquet``.
* **VIXCLS** — from ``data/phase3_7/vix/VIXCLS.parquet`` (1990-01-02+).
  Pre-1990 has no VIX; see :data:`DEFAULT_IS_START_WITH_VIX` — we trim
  IS to 1990-01-01 when VIX-gated. A second variant ignores VIX
  (``vix_threshold=float("inf")``) to replicate canonical Gayed.
* **Cash sleeve** — flat 4%/yr pre-2007 (proxy for 3mo T-bill),
  computed from ``cash_rate_annual`` param. Post-2007 could use SHV
  but for simplicity we keep a single annualized rate throughout.

Cost model — Rota B Inter (Strategy B, mandate §4.6)
-----------------------------------------------------

* Commission: 0 (Inter zero-corretagem)
* FX spread: 1.20%/conversion — negligible within USD sub-account.
  Applied once at deposit; not modelled per-trade.
* DARF 15% on realized gain, liquidated at year-end. Modelled as a
  deduction at 31-Dec of every year equity > that year's Jan-01
  equity.
* LETF expense ratio 0.95%/yr — embedded in synthesize_letf_returns
  (pre-2009) and in real UPRO prices (post-2009).
* Switch cost (commission + spread at regime change): bundled into the
  commission_bps/spread_bps params for rota B moderate sizing. Set to
  10bps total per switch (5bps each), conservative for equity ETF.

Citations
---------

* LRS signal (SMA 200, above→RISK_ON, below→RISK_OFF):
  ``[leverage_for_the_long_run, p.13]``.
* Leverage via SMA = low-vol regime proxy:
  ``[leverage_for_the_long_run, p.7, p.11]``.
* Gayed 2x reported Sharpe 0.68, CAGR 13.5%, MaxDD -78.7% (1928-2015):
  ``[leverage_for_the_long_run, p.17, Table 8]``.
* Synthetic LETF formula ``r = L·r_SPX - fee/252`` +
  FFR-aware variant ``cost = SW·(L-1)·(FFR+SP) + ER``:
  ``[leverage_for_the_long_run, p.16]`` + ``synthetic_letf.py``.
* VIX as LETF drawdown regime:
  ``[bozovic_2024_irfa]`` (Sept 2024; LETF long-hold SSRN study).
* F2-alignment (prev_weight × ret): ``[advances_fin_ml, p.31-34]``.
* Rota B cost model: ``docs/investment-mandate.md §4.6``.
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
    "DEFAULT_IS_START_WITH_VIX",
    "H2GayedVixFloorConfig",
    "H2GayedVixFloorResult",
    "compute_regime_and_vix_signal",
    "simulate_h2_gayed_vix_floor",
    "stitch_2x_letf_returns",
]


# VIX starts 1990-01-02 — trim IS to 1990-01-01 when the VIX gate is
# active. Canonical Gayed can still run 1970+ if the VIX gate is
# disabled (vix_threshold=+inf).
DEFAULT_IS_START_WITH_VIX = pd.Timestamp("1990-01-01")

# UPRO real-data start. We stitch synth pre + real post.
UPRO_REAL_START = pd.Timestamp("2009-06-25")


FilterKind = Literal["SMA", "EMA"]


@dataclass(frozen=True)
class H2GayedVixFloorConfig:
    """Immutable config for one H2.b backtest cell.

    Defaults implement the canonical Gayed 2x LRS with a VIX<25 floor
    (pre-specified; NOT tuned on OOS).

    Parameters
    ----------
    sma_period : int
        SMA window applied to SPX-TR closes. Default 200 (Gayed canonical).
    filter_kind : {"SMA", "EMA"}
        MA flavour. Default SMA (Gayed canonical).
    vix_threshold : float
        Strict upper bound on VIX for the gate to be OPEN. Default 25.0.
        Set to ``float("inf")`` to disable the VIX gate (canonical Gayed).
    leverage : float
        Leverage factor. Default 2.0 (UPRO). Can be 3.0 for UPRO-3x or
        1.25 for modest leverage — but **Strategy B mandate canonical
        is 2x** (SSO/UPRO-2x variant).
    expense_ratio : float
        Annualized LETF ER applied on the synth-period. Default 0.0095
        (UPRO/SSO post-2021).
    swap_exposure, ffr_spread : float
        FFR-aware synth cost parameters (testfolio model). Defaults
        track :mod:`synthetic_letf`.
    cash_rate_annual : float
        Annualized cash sleeve return on off-regime days. Default 0.04
        (approximately the long-term US 3mo T-bill; mandate §4.6 proxy).
    commission_bps, spread_bps : float
        Per-switch cost components in bps. Default 5/5 = 10bps total.
    tax_rate : float
        Realized-gain DARF at year-end. Default 0.15 (BR 15%, rota B).
    use_real_upro : bool
        If True, stitch real UPRO pct_change post-2009-06-25 onto the
        synth series; else use synth throughout. Default True.
    """

    sma_period: int = 200
    filter_kind: FilterKind = "SMA"
    vix_threshold: float = 25.0
    leverage: float = 2.0
    expense_ratio: float = DEFAULT_EXPENSE_RATIO
    swap_exposure: float = DEFAULT_SWAP_EXPOSURE
    ffr_spread: float = DEFAULT_FFR_SPREAD
    cash_rate_annual: float = 0.04
    commission_bps: float = 5.0
    spread_bps: float = 5.0
    tax_rate: float = 0.15
    use_real_upro: bool = True

    def __post_init__(self) -> None:
        if self.sma_period <= 1:
            raise ValueError(f"sma_period must be > 1, got {self.sma_period}")
        if self.filter_kind not in ("SMA", "EMA"):
            raise ValueError(
                f"filter_kind must be SMA or EMA, got {self.filter_kind!r}"
            )
        if self.leverage <= 0:
            raise ValueError(f"leverage must be > 0, got {self.leverage}")
        if self.vix_threshold <= 0:
            raise ValueError(
                f"vix_threshold must be > 0, got {self.vix_threshold}"
            )

    @property
    def switch_cost_pct(self) -> float:
        return (self.commission_bps + self.spread_bps) / 10_000.0


@dataclass
class H2GayedVixFloorResult:
    """Output of :func:`simulate_h2_gayed_vix_floor`.

    Attributes
    ----------
    equity : pd.Series
        Daily equity curve starting at 1.0.
    daily_returns : pd.Series
        Net daily return (after switch costs, annual tax at year-end).
    regime_sma : pd.Series
        Boolean (1/0) — MA filter state per day.
    vix_gate : pd.Series
        Boolean (1/0) — VIX<threshold state per day.
    exposure : pd.Series
        Combined long exposure fraction (0.0 or ``leverage``).
    switches : pd.Series
        Boolean — True when exposure changed from prior day.
    cum_cost_pct : float
        Cumulative switch-cost drag.
    cum_tax_pct : float
        Cumulative DARF paid.
    """

    equity: pd.Series
    daily_returns: pd.Series
    regime_sma: pd.Series
    vix_gate: pd.Series
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


def compute_regime_and_vix_signal(
    spy_close: pd.Series,
    vix_close: pd.Series | None,
    config: H2GayedVixFloorConfig,
) -> tuple[pd.Series, pd.Series]:
    """Compute MA regime + VIX floor gate, **both shifted by t-1**.

    Returns
    -------
    regime_sma : pd.Series of {0, 1} (int) — 1 iff close_{t-1} > MA_{t-1}
    vix_gate   : pd.Series of {0, 1} (int) — 1 iff VIX_{t-1} < threshold
                 If ``vix_close`` is None OR ``vix_threshold = +inf``, gate is
                 1 everywhere (disabled).

    Lookahead guard
    ---------------

    Both outputs are shifted by 1 day so that the signal for trading day
    ``t`` depends only on information through ``t-1`` close. This is the
    F2-alignment convention [advances_fin_ml, p.31-34].
    """
    px = spy_close.astype(float)
    if config.filter_kind == "SMA":
        ma = px.rolling(window=config.sma_period, min_periods=config.sma_period).mean()
    else:
        ma = px.ewm(
            span=config.sma_period, min_periods=config.sma_period, adjust=False
        ).mean()
    # Raw regime at time t (price > MA at close_t). Shift(1) → signal used at t
    # is based on close_{t-1}, MA_{t-1}.
    raw_regime = (px > ma).astype(float)
    regime_sma = raw_regime.shift(1).fillna(0.0).astype(int)

    if vix_close is None or not np.isfinite(config.vix_threshold):
        vix_gate = pd.Series(1, index=px.index, dtype=int)
    else:
        vix_aligned = vix_close.reindex(px.index).ffill()
        raw_vix = (vix_aligned < config.vix_threshold).astype(float)
        vix_gate = raw_vix.shift(1).fillna(0.0).astype(int)
        # For pre-VIX days (no value at all), gate is 0 (conservative:
        # refuse to go on without VIX data).
        vix_gate = vix_gate.where(
            vix_aligned.shift(1).notna(),
            other=0,
        ).astype(int)

    return regime_sma, vix_gate


def stitch_2x_letf_returns(
    spx_tr_returns: pd.Series,
    upro_real: pd.Series | None,
    ffr_annualized: pd.Series,
    config: H2GayedVixFloorConfig,
    *,
    stitch_date: pd.Timestamp = UPRO_REAL_START,
) -> pd.Series:
    """Build a daily 2x-LETF return series by stitching synth + real UPRO.

    Pre-``stitch_date`` uses
    :func:`synthesize_letf_returns_ffr_aware` on the SPX-TR returns.
    On/post ``stitch_date`` — if ``config.use_real_upro`` and ``upro_real``
    is given — uses ``upro_real`` daily returns.

    Parameters
    ----------
    spx_tr_returns : pd.Series
        Daily SPX-TR decimal returns (from
        :func:`load_spx_tr_daily`).
    upro_real : pd.Series | None
        Daily UPRO pct_change from Tiingo adj_close (indexed post-2009).
        If None or ``config.use_real_upro = False``, synth is used throughout.
    ffr_annualized : pd.Series
        Annualized FFR proxy (Ken French rf × 252) aligned to
        spx_tr_returns.
    config : H2GayedVixFloorConfig
        Leverage + cost params.

    Returns
    -------
    pd.Series
        Daily 2x LETF returns, same index as ``spx_tr_returns``.
    """
    synth = synthesize_letf_returns_ffr_aware(
        spx_tr_returns,
        leverage=config.leverage,
        ffr_annualized=ffr_annualized,
        swap_exposure=config.swap_exposure,
        ffr_spread=config.ffr_spread,
        expense_ratio=config.expense_ratio,
    )
    if not config.use_real_upro or upro_real is None:
        return synth

    upro_aligned = upro_real.reindex(spx_tr_returns.index)
    stitched = synth.copy()
    on_or_after = spx_tr_returns.index >= stitch_date
    # Use real UPRO where we have data on/after stitch_date, else synth.
    mask = on_or_after & upro_aligned.notna()
    stitched.loc[mask] = upro_aligned.loc[mask].astype(float)
    return stitched


def simulate_h2_gayed_vix_floor(
    spx_tr_returns: pd.Series,
    spy_close: pd.Series,
    vix_close: pd.Series | None,
    ffr_annualized: pd.Series,
    config: H2GayedVixFloorConfig,
    upro_real: pd.Series | None = None,
) -> H2GayedVixFloorResult:
    """Run one H2.b (Gayed + VIX floor) config end-to-end.

    Parameters
    ----------
    spx_tr_returns : pd.Series
        Daily SPX-TR decimal returns (stitched KF+Tiingo).
    spy_close : pd.Series
        Daily SPY (or SPX-TR) close price series for the SMA signal.
        Must share index with ``spx_tr_returns``. Typically computed
        as ``(1+spx_tr_returns).cumprod()*100`` — "TR-aware" MA.
    vix_close : pd.Series | None
        Daily VIXCLS. Index can be different from spx_tr_returns — it
        is reindex/ffilled internally. Pass ``None`` to disable the VIX
        gate completely.
    ffr_annualized : pd.Series
        FFR proxy (Ken French rf × 252), aligned to spx_tr_returns.
    config : H2GayedVixFloorConfig
        Strategy parameters.
    upro_real : pd.Series | None
        Real UPRO daily returns for stitching post-2009. None → synth
        throughout.

    Returns
    -------
    H2GayedVixFloorResult

    Raises
    ------
    ValueError
        If ``spx_tr_returns`` and ``spy_close`` index do not match.
    """
    if not spx_tr_returns.index.equals(spy_close.index):
        raise ValueError(
            "spx_tr_returns and spy_close must share index (pass stitched SPX-TR)"
        )
    if not ffr_annualized.index.equals(spx_tr_returns.index):
        ffr_annualized = ffr_annualized.reindex(spx_tr_returns.index).ffill().bfill()

    regime_sma, vix_gate = compute_regime_and_vix_signal(
        spy_close, vix_close, config
    )

    letf_returns = stitch_2x_letf_returns(
        spx_tr_returns, upro_real, ffr_annualized, config
    )

    cash_daily = config.cash_rate_annual / TRADING_DAYS_PER_YEAR
    # Binary exposure: leverage when both gates on, else 0.
    exposure = (regime_sma * vix_gate * config.leverage).astype(float)

    # F2-alignment: on day t, the position was established using signals
    # built from t-1 data. The daily return at t is exposure_t * letf_t
    # (when exposure>0) or cash_daily (when exposure==0).
    # Since exposure is already the notional weight, and letf_returns is
    # already leveraged return, we apply exposure/leverage (0 or 1) as
    # the gate, then use letf_returns for the active return.
    gate = (exposure > 0).astype(float)
    gross = gate * letf_returns.fillna(0.0) + (1.0 - gate) * cash_daily

    # Detect regime switches (exposure changes from day to day).
    prev_exp = exposure.shift(1).fillna(0.0)
    switches = (exposure != prev_exp)

    switch_cost_pct = config.switch_cost_pct
    # Cost on switch days — applied to current day's return, proportional to
    # the notional that changed (we conservatively apply to full notional).
    cost_drag = switches.astype(float) * switch_cost_pct

    daily_net = gross - cost_drag

    # Apply year-end DARF 15% on realized yearly gain (simple year-by-year
    # liquidation model per mandate §4.6 swing rota B).
    equity_list: list[float] = []
    cum_cost = 0.0
    cum_tax = 0.0
    equity = 1.0
    last_year_end_equity = 1.0
    prev_year: int | None = None
    tax_rate = config.tax_rate

    # We need to detect end-of-year days and apply tax deduction after the
    # last bar of each calendar year. We walk through the index, keep track
    # of year boundaries, and apply the tax at the last bar of each year.
    idx = daily_net.index
    daily_arr = daily_net.to_numpy(dtype=float, copy=True)
    switches_arr = switches.to_numpy()
    # Precompute "is last trading day of year?"
    years = pd.Series(idx).dt.year.to_numpy()
    is_last_day_of_year = np.zeros(len(idx), dtype=bool)
    for i in range(len(idx)):
        if i == len(idx) - 1:
            is_last_day_of_year[i] = True
        elif years[i] != years[i + 1]:
            is_last_day_of_year[i] = True

    for i, ts in enumerate(idx):
        r = daily_arr[i]
        if not np.isfinite(r):
            r = 0.0
        if switches_arr[i]:
            cum_cost += abs(switch_cost_pct) * equity
        equity *= 1.0 + r
        if is_last_day_of_year[i] and tax_rate > 0:
            gain = max(0.0, equity - last_year_end_equity)
            tax = gain * tax_rate
            equity -= tax
            cum_tax += tax
            # Adjust the bar's net return to incorporate the tax drag on
            # the equity path (so Sharpe/CAGR reflect post-tax).
            daily_arr[i] = (equity / (equity_list[-1] if equity_list else 1.0)) - 1.0 if equity_list else r
            last_year_end_equity = equity
        equity_list.append(equity)

    equity_series = pd.Series(equity_list, index=idx, name="equity_h2")
    # Recompute daily_net from final equity path to include tax hits
    # consistently (Sharpe/CAGR will match equity).
    eq_vals = np.asarray(equity_list, dtype=float)
    daily_final = pd.Series(
        np.concatenate(([0.0], eq_vals[1:] / eq_vals[:-1] - 1.0)),
        index=idx,
        name="daily_h2_net",
    )

    return H2GayedVixFloorResult(
        equity=equity_series,
        daily_returns=daily_final,
        regime_sma=regime_sma,
        vix_gate=vix_gate,
        exposure=exposure,
        switches=switches,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
    )
