"""Phase 3.6 — Family F: Vol-targeting managed-futures basket.

Multi-asset managed-futures basket simulator for the Phase 3.6 swing-
winner hunt. This is a **clean return-series strategy** (no bar-level
portfolio engine) in the spirit of
:mod:`ai_trade.backtest.strategies.letf_rotation` and
:mod:`ai_trade.backtest.strategies.phase3_6_a_clenow_momentum`.

Differentiation from V2-L1 TSMOM (mandatory, documented)
--------------------------------------------------------

V2-L1 TSMOM (`tsmom_multi_asset.py`) was rejected under the honest
engine (`reports/phase_3_5f/honest_revalidation/v2_l1_tsmom/AGGREGATE.md`).
Family F is **structurally different** on three axes — these are NOT
cosmetic tweaks:

1. **Trend signal.** V2-L1 uses a **binary** past-return sign test:
   ``sig_i = 1 if (close_t / close_{t-L} - 1) > 0 else 0``. Family F
   uses Carver's **continuous EWMAC** (exponentially-weighted moving
   average crossover): ``forecast_i = 10 × (EMA_fast − EMA_slow) /
   σ_price_i / scalar`` capped at ±20. EWMAC produces a *strength*
   signal and supports shorts [systematic_trading, p.118-119,
   p.282-285]. The V2-L1 binary rule has no notion of trend
   strength and is long-only.

2. **Vol targeting.** V2-L1 applies vol targeting **per leg**
   (``w_i = sig × vol_tgt / σ_i``) then averages. Family F uses
   Carver's **portfolio-level vol target** with the instrument
   diversification multiplier IDM: at the portfolio level, the target
   annualised vol is 15% and each instrument's notional exposure is
   ``(vol_tgt × forecast_i × IDM) / (N × σ_i × √252 × 10)``. Portfolio
   rebalancing every 10-20 days (not monthly) and IDM is capped at 2.5
   per Carver's handcrafting rule [systematic_trading, p.170-171,
   p.174, ch.10-11].

3. **Basket composition.** V2-L1 uses a 30-asset CFD-proxy universe
   dominated by 3 USD-pair FX crosses (structurally the lowest-vol
   instruments). Family F uses a 6-asset managed-futures-proxy basket
   across **explicit asset classes** — equities (SPY/EFA), bonds
   (TLT/IEF), commodities (GLD/USO). This avoids the FX-dominant bias
   that was one of V2-L1's diagnosed failure modes (see V2-L1
   post-mortem: "vol-weighting pushes allocations into FX crosses
   ambushed by 2024-2026 USD-strength regime"). Citations:
   [systematic_trading, p.135-140] (instrument selection), Family F
   plan brief (multi-class requirement).

Design parameters (every choice cites a page)
---------------------------------------------

* **Universe:** 6 Tiingo ETFs as managed-futures proxies — SPY (US
  equity, 2001-05-14 inception), TLT (US 20Y Treasuries, 2002-07-26),
  GLD (gold, 2004-11-18), USO (oil, 2006-04-10), EFA (EAFE, 2003-08-20),
  IEF (7-10Y Treasuries, 2006-01-03). Pepperstone CFD-compatible
  underliers where applicable. Honest truncation: the full 6-asset
  panel is only active from 2006-04-10 onward; earlier bars use the
  dynamic-universe active-set rule (an asset enters when it has
  enough history). Cite [systematic_trading, p.135-140] for
  instrument-class coverage rationale.

* **Trend signal — EWMAC:** six canonical fast/slow pairs
  {2:8, 4:16, 8:32, 16:64, 32:128, 64:256} with forecast scalar tables
  per Carver [systematic_trading, p.282-285, appendix B, Table 57].
  Fast = ``2 / (fast_span + 1)``, slow = ``2 / (slow_span + 1)`` in
  EMA smoothing. Raw crossover = ``EMA_fast − EMA_slow``, normalized
  by rolling price-change vol and scaled by the canonical scalar so
  that the expected average absolute forecast is 10 [p.112-114, p.283-
  284, appendix B]. Winner cell uses 16:64 (median-hold
  target ≈ 16-40 trading days per Carver's look-back tables).

* **Vol targeting (Carver portfolio-level):** target portfolio vol =
  15% annualised [systematic_trading, p.137-148, ch.9 — Half-Kelly rule
  σ_target = SR_realistic ≈ 0.4-0.5 so σ_target ≈ 15-20%]. Per-asset
  instrument vol σ_i computed as EWMA of returns with 35-day span,
  annualised by √252 [p.112-114 (ch.7)]. Per-asset forecast →
  subsystem position: ``pos_i = (σ_target × forecast_i × IDM) / (N ×
  σ_i × 10)``, capped at ±2.0 per leg (gross-notional cap on a single
  sleeve) and aggregated to total notional capped at leverage_max.
  IDM = min(2.5, √N) with N the number of active assets
  [systematic_trading, p.170-171, ch.11, max IDM 2.5].

* **Rebalance cadence:** positions are recomputed on every business
  day using position-inertia (don't trade unless the target position
  differs from current by > inertia_frac). Trade bar ≈ every 10-20
  days in practice [systematic_trading, p.174 (ch.11) — position
  inertia 10%]. Grid tests 10d vs 20d cadence.

* **Long-short:** EWMAC forecast is signed; the strategy can be short.
  Short sleeve subject to the same gross-notional cap per leg as the
  long sleeve. This differs from V2-L1 (long-only binary).

* **Frictions — Pepperstone Razor (plan §3.1):**
  - Spread one-way 0.025% on SPY/EFA/TLT/IEF, 0.05% on GLD, 0.10% on
    USO (wider commodity spread).
  - Commission $0.35 per 100k USD notional per side = ~0.0035% of
    notional per round-trip.
  - Overnight swap: −0.03%/night on levered long notional,
    +0.0% on short notional (simplification — futures/CFD swaps are
    asymmetric but close to zero net for a vol-targeted basket).
  - NO BR CG tax (Pepperstone non-BR jurisdiction).

* **Cost×2 sensitivity (gate 13):** spread doubled.

Look-ahead audit
----------------

For each bar ``t``:

* EMA_fast[t] and EMA_slow[t] use price data through bar ``t``
  (EWMA with no look-ahead).
* σ_price[t] uses return data through bar ``t``.
* forecast_i[t] and weight_i[t] are therefore known at close of bar t.
* **Alignment:** ``daily_return[t] = Σ_i prev_weight_i[t-1] × return_i[t]``.
  This matches the F2-patched ``prev_weight × ret`` convention
  [advances_fin_ml, p.31-34].

Citations
---------

* Carver EWMAC trend rule: [systematic_trading, p.118-119 (ch.7),
  p.282-285 (appendix B)].
* Forecast scalars per EWMAC pair: [systematic_trading, p.285, Table
  in appendix B].
* Volatility target via Half-Kelly: [systematic_trading, p.137-148,
  ch.9].
* Portfolio-level vol scaling + IDM: [systematic_trading, p.159-173,
  ch.10-11].
* IDM max 2.5: [systematic_trading, p.170-171, ch.11].
* Position inertia 10%: [systematic_trading, p.174, ch.11].
* Standardised cost / turnover budget: [systematic_trading, p.182,
  p.185-188, ch.12].
* Multi-asset instrument coverage: [systematic_trading, p.135-140].
* Kelly-based sizing cross-reference: [volatility_trading, p.135,
  p.138-140] (Sinclair — fractional Kelly discipline).
* Look-ahead audit: [advances_fin_ml, p.31-34].
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "VolTargetMFConfig",
    "VolTargetMFResult",
    "EWMAC_SCALARS",
    "compute_ewmac_forecast",
    "simulate_vol_target_mf",
]

TRADING_DAYS_PER_YEAR = 252

#: Forecast scalars per EWMAC pair so that average absolute forecast
#: ≈ 10. Values from [systematic_trading, p.285, Appendix B Table].
EWMAC_SCALARS: dict[tuple[int, int], float] = {
    (2, 8): 10.6,
    (4, 16): 7.5,
    (8, 32): 5.3,
    (16, 64): 3.75,
    (32, 128): 2.65,
    (64, 256): 1.87,
}

#: Default per-asset one-way spread in fraction-of-notional
#: (Pepperstone Razor retail, plan §3.1).
DEFAULT_SPREAD_ONE_WAY: dict[str, float] = {
    "SPY": 0.00025,
    "QQQ": 0.00025,
    "EFA": 0.00025,
    "TLT": 0.00025,
    "IEF": 0.00025,
    "GLD": 0.00050,
    "USO": 0.00100,
}


@dataclass(frozen=True)
class VolTargetMFConfig:
    """Immutable configuration for one Family F backtest cell.

    Parameters
    ----------
    fast_span : int
        EWMAC fast EMA span (e.g. 16). Must pair with ``slow_span``
        such that ``(fast, slow)`` is in :data:`EWMAC_SCALARS`.
        [systematic_trading, p.282-285, appendix B]
    slow_span : int
        EWMAC slow EMA span (e.g. 64).
    target_vol_annual : float
        Portfolio-level annualised vol target. Carver's Half-Kelly rule
        recommends σ_target = realistic_SR; 15% is the standard MF
        basket value. [systematic_trading, p.137-148, ch.9]
    rebalance_days : int
        Position-recomputation cadence in trading days. 10d or 20d per
        brief. [systematic_trading, p.174, ch.11]
    sigma_ewma_span : int
        EWMA span for rolling return-vol σ_i estimation. 35d matches
        Carver's default. [systematic_trading, p.112-114, ch.7]
    inertia_frac : float
        Position-inertia threshold; don't rebalance if |Δw| < inertia ×
        |w_current|. 0.10 per Carver. [systematic_trading, p.174]
    max_per_leg : float
        Cap on per-instrument weight absolute value (gross leverage
        per asset). Default 2.0.
    max_gross_leverage : float
        Cap on Σ|w_i| across all active instruments (portfolio gross).
        Default 4.0.
    idm_cap : float
        Cap on instrument-diversification multiplier. Default 2.5 per
        [systematic_trading, p.170-171].
    min_active_assets : int
        Below this count the portfolio is flat. Default 3.
    forecast_cap : float
        Absolute cap on the per-asset forecast. Carver 20.
        [systematic_trading, p.112-114, ch.7]
    spread_one_way : mapping[str, float]
        Per-ticker one-way trading cost fraction. Defaults from plan
        §3.1 Pepperstone Razor table.
    commission_round_trip : float
        Round-trip commission fraction of notional. Pepperstone Razor
        ≈ 0.0035% = $0.35 per 100k. Default 3.5e-5.
    swap_daily_long : float
        Daily swap on the aggregate LONG notional. −0.03%/night default.
    swap_daily_short : float
        Daily swap on the aggregate SHORT notional. 0.0 default.
    tax_rate : float
        Capital-gains tax rate. 0.0 for Pepperstone (plan §3.1).
    """

    fast_span: int = 16
    slow_span: int = 64
    target_vol_annual: float = 0.15
    rebalance_days: int = 10
    sigma_ewma_span: int = 35
    inertia_frac: float = 0.10
    max_per_leg: float = 2.0
    max_gross_leverage: float = 4.0
    idm_cap: float = 2.5
    min_active_assets: int = 3
    forecast_cap: float = 20.0
    spread_one_way: dict[str, float] = field(
        default_factory=lambda: dict(DEFAULT_SPREAD_ONE_WAY)
    )
    commission_round_trip: float = 3.5e-5
    swap_daily_long: float = -0.0003
    swap_daily_short: float = 0.0
    tax_rate: float = 0.0

    def __post_init__(self) -> None:
        if (self.fast_span, self.slow_span) not in EWMAC_SCALARS:
            raise ValueError(
                f"(fast, slow) = ({self.fast_span}, {self.slow_span}) "
                f"not in canonical Carver EWMAC pairs {list(EWMAC_SCALARS.keys())}"
            )
        if self.target_vol_annual <= 0:
            raise ValueError(
                f"target_vol_annual must be > 0, got {self.target_vol_annual}"
            )
        if self.rebalance_days < 1:
            raise ValueError(
                f"rebalance_days must be >= 1, got {self.rebalance_days}"
            )
        if self.sigma_ewma_span < 5:
            raise ValueError(
                f"sigma_ewma_span must be >= 5, got {self.sigma_ewma_span}"
            )
        if self.forecast_cap <= 0:
            raise ValueError(
                f"forecast_cap must be > 0, got {self.forecast_cap}"
            )
        if self.min_active_assets < 1:
            raise ValueError(
                f"min_active_assets must be >= 1, got {self.min_active_assets}"
            )

    @property
    def ewmac_scalar(self) -> float:
        return EWMAC_SCALARS[(self.fast_span, self.slow_span)]


@dataclass
class VolTargetMFResult:
    """Output of one Family F simulation."""

    daily_returns: pd.Series
    gross_returns: pd.Series
    weights: pd.DataFrame
    forecasts: pd.DataFrame
    active_count: pd.Series
    hold_lengths: list[int] = field(default_factory=list)
    cum_cost_pct: float = 0.0
    cum_swap_pct: float = 0.0
    cum_commission_pct: float = 0.0
    n_rebalances: int = 0
    universe_tickers: tuple[str, ...] = ()

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        return float(r.mean() / sd * np.sqrt(periods_per_year)) if sd > 0 else 0.0

    def cagr(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        r = self.daily_returns.dropna()
        if len(r) < 2:
            return 0.0
        n = len(r)
        eq = float((1.0 + r).prod())
        if eq <= 0:
            return -1.0
        return eq ** (periods_per_year / n) - 1.0

    def max_drawdown(self) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        eq = (1.0 + r).cumprod()
        peak = eq.cummax()
        return float((eq / peak - 1.0).min())

    def median_hold_days(self) -> float:
        if not self.hold_lengths:
            return float("nan")
        return float(np.median(self.hold_lengths))


def compute_ewmac_forecast(
    prices: pd.Series,
    fast_span: int,
    slow_span: int,
    scalar: float,
    sigma_ewma_span: int,
    forecast_cap: float,
) -> pd.Series:
    """Carver EWMAC forecast for a single price series.

    Steps:
      1. EMA_fast − EMA_slow (raw crossover).
      2. Normalize by rolling price-change vol σ_price (EWMA).
      3. Multiply by canonical scalar so mean |forecast| ≈ 10.
      4. Cap at ±forecast_cap.

    [systematic_trading, p.282-285, appendix B].
    """
    p = prices.astype(float).copy()
    p = p[~p.index.duplicated(keep="last")].sort_index()
    ema_fast = p.ewm(span=fast_span, adjust=False).mean()
    ema_slow = p.ewm(span=slow_span, adjust=False).mean()
    raw = ema_fast - ema_slow
    # σ_price as EWMA of absolute daily price changes.
    dprice = p.diff()
    sigma_price = dprice.ewm(span=sigma_ewma_span, adjust=False).std()
    # Avoid div-by-zero: where σ_price is tiny relative to price, set NaN.
    vol_adj = raw.divide(sigma_price.replace(0.0, np.nan))
    forecast = vol_adj * scalar
    forecast = forecast.clip(lower=-forecast_cap, upper=forecast_cap)
    return forecast


def _realised_vol(returns: pd.Series, span: int) -> pd.Series:
    """Annualised EWMA vol of returns."""
    return returns.ewm(span=span, adjust=False).std() * np.sqrt(
        TRADING_DAYS_PER_YEAR
    )


def _resolve_spread(
    ticker: str,
    spread_map: dict[str, float],
) -> float:
    """Look up the per-ticker spread, falling back to ETF default."""
    t = ticker.upper()
    if t in spread_map:
        return float(spread_map[t])
    # Reasonable default for other equity ETFs.
    return 0.00025


def simulate_vol_target_mf(
    panel: dict[str, pd.DataFrame],
    config: VolTargetMFConfig,
) -> VolTargetMFResult:
    """Run one Family F vol-targeted managed-futures-basket config.

    Parameters
    ----------
    panel : dict[str, pd.DataFrame]
        Per-ticker DataFrames with ``adj_close`` column, daily Tiingo
        format.
    config : :class:`VolTargetMFConfig`
        Grid cell.

    Returns
    -------
    :class:`VolTargetMFResult`
    """
    if not panel:
        raise ValueError("panel is empty")

    tickers = tuple(sorted(panel.keys()))

    # Build aligned price matrix (outer-joined on union index).
    price_cols: dict[str, pd.Series] = {}
    for t in tickers:
        df = panel[t]
        if "adj_close" not in df.columns:
            raise ValueError(f"ticker {t} missing adj_close column")
        s = df["adj_close"].astype(float)
        s.index = pd.DatetimeIndex(s.index).normalize()
        s = s[~s.index.duplicated(keep="last")].sort_index()
        price_cols[t] = s
    prices = pd.concat(price_cols, axis=1).sort_index()
    # Restrict to weekdays to stay on NYSE-like calendar.
    prices = prices[prices.index.dayofweek < 5]
    returns = prices.pct_change(fill_method=None)

    # Per-asset forecasts (Carver EWMAC, scaled + capped).
    forecasts_cols: dict[str, pd.Series] = {}
    for t in tickers:
        p = prices[t].dropna()
        f = compute_ewmac_forecast(
            p,
            config.fast_span,
            config.slow_span,
            config.ewmac_scalar,
            config.sigma_ewma_span,
            config.forecast_cap,
        )
        forecasts_cols[t] = f.reindex(prices.index)
    forecasts = pd.concat(forecasts_cols, axis=1)

    # Per-asset annualised vol σ_i (EWMA span from config).
    sigmas_cols: dict[str, pd.Series] = {}
    for t in tickers:
        r_t = returns[t]
        sigmas_cols[t] = _realised_vol(r_t, config.sigma_ewma_span)
    sigmas = pd.concat(sigmas_cols, axis=1)
    # Shift σ by 1 to avoid look-ahead: the σ used to size today's
    # target position uses data through yesterday.
    sigmas_prev = sigmas.shift(1)
    forecasts_prev = forecasts.shift(1)

    # Active mask: asset has non-NaN forecast AND σ_prev > 0 AND a
    # non-NaN return today (the return column governs whether the asset
    # actually traded on this date — crypto/FX-style weekends already
    # filtered via weekday mask).
    active_mask = (
        forecasts_prev.notna()
        & sigmas_prev.notna()
        & (sigmas_prev > 0)
        & returns.notna()
    )

    # IDM = min(idm_cap, √N) where N = count of active assets on bar t.
    n_active = active_mask.sum(axis=1)
    idm = n_active.astype(float).pow(0.5).clip(upper=config.idm_cap)
    # Where N_active < min_active, force flat.
    flat_bars = n_active < config.min_active_assets

    # --- Target position sizing (before inertia + caps) ---
    # Carver subsystem position:
    #   target_w_i = (σ_target × forecast_i × IDM) / (N × σ_i × 10)
    # where dividing by 10 normalizes the forecast to its expected
    # average (|forecast| ≈ 10) — i.e. when forecast = 10 the subsystem
    # uses σ_target × IDM / (N × σ_i) of capital, which is the standard
    # equal-risk-budget allocation with the diversification boost.

    # Safely handle asset-rows where active==False (target = 0).
    raw_w = (
        config.target_vol_annual
        * forecasts_prev
        * idm.values.reshape(-1, 1)
    ) / (
        n_active.replace(0, np.nan).values.reshape(-1, 1)
        * sigmas_prev.replace(0, np.nan)
        * 10.0
    )
    raw_w = raw_w.where(active_mask, 0.0).fillna(0.0)
    # Per-leg cap.
    raw_w = raw_w.clip(lower=-config.max_per_leg, upper=config.max_per_leg)
    # On flat bars: zero everything.
    raw_w.loc[flat_bars] = 0.0

    # Gross-leverage cap: scale down if Σ|w| > max_gross.
    gross = raw_w.abs().sum(axis=1)
    scale = np.minimum(1.0, config.max_gross_leverage / gross.replace(0.0, np.nan))
    scale = scale.fillna(1.0)
    raw_w = raw_w.mul(scale, axis=0)

    # --- Apply rebalance cadence + position inertia ---
    # Positions are only updated on every ``rebalance_days``-th bar OR
    # when the change exceeds ``inertia_frac × |current|`` (Carver
    # rule). Between rebalance bars the position is held.
    n_bars = len(prices.index)
    weights_arr = np.zeros_like(raw_w.values)
    n_rebalances = 0
    last_rebal_idx = -config.rebalance_days  # allow first bar to rebalance
    current = np.zeros(len(tickers), dtype=float)

    raw_w_vals = raw_w.values
    for t_idx in range(n_bars):
        target = raw_w_vals[t_idx]
        # Cadence test.
        cadence_fire = (t_idx - last_rebal_idx) >= config.rebalance_days
        # Inertia test (per-asset).
        if cadence_fire:
            # Accept the target vector wholesale on rebalance bars,
            # modulated by inertia: only change legs whose |Δw| exceeds
            # inertia × max(|current|, |target|).
            delta = target - current
            significance = np.maximum(np.abs(current), np.abs(target))
            # Avoid div-by-zero: where both current and target are zero,
            # skip leg — the delta is zero anyway.
            threshold = config.inertia_frac * significance
            # Default fallback: if both are ~0, move to target (pick up
            # brand-new signals).
            near_zero = significance < 1e-10
            move_mask = (np.abs(delta) > threshold) | near_zero
            new_w = np.where(move_mask, target, current)
            if np.any(new_w != current):
                n_rebalances += 1
                last_rebal_idx = t_idx
            current = new_w
        weights_arr[t_idx] = current

    weights = pd.DataFrame(weights_arr, index=prices.index, columns=tickers)

    # --- Returns with lookahead-safe alignment ---
    prev_weights = weights.shift(1).fillna(0.0)
    per_asset = prev_weights * returns.fillna(0.0)
    gross_ret = per_asset.sum(axis=1)

    # --- Costs ---
    # Spread: applied on |Δw_i| when a rebalance happens.
    weight_changes = (weights - weights.shift(1).fillna(0.0)).abs()
    spread_drag_per_asset = pd.DataFrame(0.0, index=prices.index, columns=tickers)
    for t in tickers:
        s_one_way = _resolve_spread(t, config.spread_one_way)
        spread_drag_per_asset[t] = weight_changes[t] * s_one_way
    spread_drag = spread_drag_per_asset.sum(axis=1)

    # Commission: applied on |Δw| (per-leg) × commission_rt fraction.
    commission_drag = weight_changes.sum(axis=1) * config.commission_round_trip

    # Swap: long side pays, short side (net) per config.
    long_exposure = prev_weights.clip(lower=0.0).sum(axis=1)
    short_exposure = (-prev_weights.clip(upper=0.0)).sum(axis=1)
    swap_drag = (
        long_exposure * abs(config.swap_daily_long)
        + short_exposure * abs(config.swap_daily_short)
    )
    # Tax: 0 for Pepperstone (config.tax_rate default 0.0).
    # Month-end BR CG tax kept here only for schema parity — no-op at 0%.

    net_ret = gross_ret - spread_drag - commission_drag - swap_drag

    # --- Hold-length bookkeeping ---
    # A "hold segment" for asset i = contiguous run of bars where
    # sign(w_i) is non-zero and unchanged. Used for the median-hold
    # gate. Flips (+→−) reset the segment.
    hold_lengths: list[int] = []
    n_assets = len(tickers)
    in_segment = np.zeros(n_assets, dtype=bool)
    seg_sign = np.zeros(n_assets, dtype=int)
    seg_len = np.zeros(n_assets, dtype=int)
    w_sign = np.sign(weights_arr).astype(int)
    for t_idx in range(n_bars):
        for i in range(n_assets):
            s = w_sign[t_idx, i]
            if s == 0:
                if in_segment[i]:
                    hold_lengths.append(int(seg_len[i]))
                    in_segment[i] = False
                    seg_len[i] = 0
                    seg_sign[i] = 0
            else:
                if in_segment[i] and s == seg_sign[i]:
                    seg_len[i] += 1
                else:
                    if in_segment[i]:
                        hold_lengths.append(int(seg_len[i]))
                    in_segment[i] = True
                    seg_sign[i] = s
                    seg_len[i] = 1
    for i in range(n_assets):
        if in_segment[i] and seg_len[i] > 0:
            hold_lengths.append(int(seg_len[i]))

    cum_cost_pct = float(spread_drag.sum())
    cum_swap_pct = float(swap_drag.sum())
    cum_commission_pct = float(commission_drag.sum())

    active_count = n_active.astype(int)

    return VolTargetMFResult(
        daily_returns=net_ret,
        gross_returns=gross_ret,
        weights=weights,
        forecasts=forecasts,
        active_count=active_count,
        hold_lengths=hold_lengths,
        cum_cost_pct=cum_cost_pct,
        cum_swap_pct=cum_swap_pct,
        cum_commission_pct=cum_commission_pct,
        n_rebalances=n_rebalances,
        universe_tickers=tickers,
    )
