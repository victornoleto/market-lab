"""Time-Series Momentum multi-asset — V2-L1 (Phase 3.5a-V2 Plano A CFD).

Canonical time-series momentum (Moskowitz, Ooi, Pedersen 2012) adapted
for retail CFD via Carver-style instrument vol-targeting and dynamic
active universe. One config = (lookback_days, vol_target_annual). Each
month-end, for every active instrument i:

1. ``sig_i = (close_t / close_{t-lookback} - 1) > 0 ? 1 : 0`` — binary
   long/flat (no shorts — retail simplification per Carver
   ``[systematic_trading, ch.8-9]``).
2. ``w_i = sig_i * vol_target_annual / realized_vol_252d_i`` — per-
   instrument Carver vol scalar, clipped to ``[0, max_leverage_per_asset]``.
3. Equal dollar budget across active instruments:
   ``portfolio_weight_i = w_i / N_active_t``.

Between rebalances, weights are held constant (drift allowed on a
fixed-weight basis — we do NOT re-allocate intra-month). Daily
portfolio return is the weighted sum of instrument daily returns minus
costs.

Cost model (Pepperstone Razor retail, spec §3):

* Per-asset round-trip bps applied on any weight change (entry or exit)
  at the rebalance bar. Commission + spread + slippage bundled into a
  single round-trip bps number per asset class.
* Overnight swap: ``swap_daily_bps`` fraction applied daily to the
  gross long notional held (``sum_i portfolio_weight_i``).
  Pepperstone long equity swap ≈ 0.005-0.01%/day on the long side.

Dynamic universe handling:

* An instrument is ``active`` at ``t`` iff it has at least
  ``max(lookback, vol_lookback)`` prior bars of close data **and** its
  ``first_dt + max_warmup <= t``. Before the active set reaches
  ``min_active_instruments``, the portfolio return is ``0.0`` (flat).
* This satisfies the CLAUDE.md HARD RULE "LONGEST available historical
  window per (ticker, frequency)" — each instrument contributes data
  starting from its Tiingo ``first_dt`` + warmup.

Citations
---------

* Time-series momentum as a family: ``[algo_trading_chan, p.133, ch.6]``
  — "past returns of a single instrument are positively correlated with
  future returns".
* Binary signal + Carver vol scalar + monthly rebalance CTA template:
  ``[systematic_trading, ch.8-9]`` (Carver) — retail-appropriate vol
  standardisation with inverse-realised-vol weighting.
* Vol-target ex-ante rescaling (``σ̂_{t-1}`` lag, no look-ahead):
  ``[advances_fin_ml, p.162-164]``.
* Monthly EOM rebalance is the Moskowitz/Ooi/Pedersen 2012 canonical
  cadence: ``[trend_following_covel, ch.5-6]`` (Covel summarises the
  CTA breadth convention).
* Retail Pepperstone cost model (spread+commission dominant, swap
  non-negligible): Phase 3.5a-V2 spec §3.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "TRADING_DAYS_PER_YEAR",
    "DEFAULT_ROUND_TRIP_BPS_BY_CLASS",
    "TSMOMMultiAssetConfig",
    "TSMOMMultiAssetResult",
    "simulate_tsmom_multi_asset",
]


TRADING_DAYS_PER_YEAR = 252


#: Pepperstone Razor retail round-trip cost (spread half × 2 +
#: commission + slippage), bundled per asset class. Spec §3.
DEFAULT_ROUND_TRIP_BPS_BY_CLASS: dict[str, float] = {
    "etf": 10.0,          # equity/sector/FI ETFs (7-11 bps band → 10)
    "forex": 8.0,          # FX majors (6-10 bps → 8)
    "commodity_etf": 13.0,  # GLD/SLV/USO/UNG/DBA (10-15 bps → 13)
    "crypto": 20.0,        # BTCUSD (15-25 bps → 20)
}


def default_asset_class(ticker: str) -> str:
    """Classify a ticker into the cost-bucket key of
    :data:`DEFAULT_ROUND_TRIP_BPS_BY_CLASS`.

    This is a local heuristic (not the Tiingo asset_class taxonomy) —
    the cost bucket only has 4 entries because the round-trip bps
    spread is flat within each bucket.
    """
    t = ticker.upper()
    if t in {"GLD", "SLV", "USO", "UNG", "DBA"}:
        return "commodity_etf"
    if t in {"BTCUSD", "ETHUSD", "ADAUSD", "XRPUSD"}:
        return "crypto"
    if t.lower() == ticker or len(ticker) == 6:
        # 6-letter FX convention, e.g. EURUSD / usdjpy (parquet key).
        # Tiingo storage uses lower-case filenames for FX.
        return "forex"
    return "etf"


@dataclass(frozen=True)
class TSMOMMultiAssetConfig:
    """Immutable configuration for one V2-L1 TSMOM run.

    Parameters
    ----------
    lookback_days : int
        Past-return lookback window, in trading days (21=1m, 63=3m,
        126=6m, 252=12m). Must be ≥ 2.
    vol_target_annual : float
        Per-instrument annualised vol target (fraction, e.g. 0.10 for
        10%). Each instrument's weight is ``sig * vol_target / σ̂_i``.
    vol_lookback_days : int
        Rolling window for realised vol estimation (default 252 = 1y).
    max_leverage_per_asset : float
        Upper cap on ``vol_target / σ̂`` per instrument (default 2.0 —
        no single instrument gets more than 2× risk budget).
    min_active_instruments : int
        Below this, portfolio is flat (default 3 — Carver breadth floor
        ``[systematic_trading, ch.8-9]``).
    swap_daily_bps : float
        Pepperstone overnight swap (long side), bps of notional per day.
        Default 5 bps (≈ 0.005%/day, realistic for equity CFD longs).
    round_trip_bps_by_class : mapping
        Per-asset-class round-trip cost in bps (entry+exit+comm+spread
        +slippage). Defaults to
        :data:`DEFAULT_ROUND_TRIP_BPS_BY_CLASS`.
    """

    lookback_days: int
    vol_target_annual: float
    vol_lookback_days: int = 252
    max_leverage_per_asset: float = 2.0
    min_active_instruments: int = 3
    swap_daily_bps: float = 5.0
    round_trip_bps_by_class: Mapping[str, float] = field(
        default_factory=lambda: dict(DEFAULT_ROUND_TRIP_BPS_BY_CLASS)
    )

    def __post_init__(self) -> None:
        if self.lookback_days < 2:
            raise ValueError(
                f"lookback_days must be ≥ 2, got {self.lookback_days}"
            )
        if self.vol_target_annual <= 0:
            raise ValueError(
                f"vol_target_annual must be > 0, got {self.vol_target_annual}"
            )
        if self.vol_lookback_days < 20:
            raise ValueError(
                f"vol_lookback_days must be ≥ 20, got {self.vol_lookback_days}"
            )
        if self.max_leverage_per_asset <= 0:
            raise ValueError(
                f"max_leverage_per_asset must be > 0, got {self.max_leverage_per_asset}"
            )
        if self.min_active_instruments < 1:
            raise ValueError(
                f"min_active_instruments must be ≥ 1, got {self.min_active_instruments}"
            )
        if self.swap_daily_bps < 0:
            raise ValueError(
                f"swap_daily_bps must be ≥ 0, got {self.swap_daily_bps}"
            )


@dataclass
class TSMOMMultiAssetResult:
    """Output of a single V2-L1 TSMOM run over a multi-asset universe."""

    daily_returns: pd.Series
    equity: pd.Series
    weights: pd.DataFrame  # index=dates, columns=tickers; gross portfolio weights
    active_count: pd.Series
    rebalance_dates: pd.DatetimeIndex
    n_rebalances: int
    median_hold_days: float
    cum_cost_pct: float  # cumulative transaction cost as fraction
    cum_swap_pct: float  # cumulative swap cost as fraction
    n_long_bar_positions: int  # total (asset, bar) pairs held long
    universe_tickers: tuple[str, ...]

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


def _monthly_eom_mask(index: pd.DatetimeIndex) -> pd.Series:
    """Boolean mask: True on the last trading day of each month."""
    s = pd.Series(index.to_period("M"), index=index)
    # Last occurrence per month ⇒ True.
    last_idx = s.drop_duplicates(keep="last").index
    out = pd.Series(False, index=index)
    out.loc[last_idx] = True
    return out


def simulate_tsmom_multi_asset(
    price_panel: Mapping[str, pd.DataFrame],
    config: TSMOMMultiAssetConfig,
    *,
    asset_class_lookup: Mapping[str, str] | None = None,
) -> TSMOMMultiAssetResult:
    """Run ONE TSMOM multi-asset config over the supplied price panel.

    Parameters
    ----------
    price_panel : mapping of ticker → OHLC DataFrame (with ``close``
        column, DatetimeIndex). Per-instrument index lengths may differ
        — the portfolio uses a dynamic active set.
    config : :class:`TSMOMMultiAssetConfig`
    asset_class_lookup : optional mapping ticker → cost-bucket key.
        Defaults to :func:`default_asset_class` per ticker.

    Returns
    -------
    :class:`TSMOMMultiAssetResult`

    Raises
    ------
    ValueError
        If ``price_panel`` is empty or any DataFrame lacks ``close``.
    """
    if not price_panel:
        raise ValueError("price_panel must be non-empty")

    tickers = tuple(sorted(price_panel.keys()))
    class_lookup = dict(asset_class_lookup or {})

    # Build the close-price DataFrame aligned on the union date index.
    closes: dict[str, pd.Series] = {}
    for t in tickers:
        df = price_panel[t]
        if "close" not in df.columns:
            raise ValueError(f"price_panel[{t!r}] lacks 'close' column")
        s = df["close"].astype(float).sort_index()
        s = s[~s.index.duplicated(keep="last")]
        closes[t] = s

    # Master calendar = union of all native indexes, RESTRICTED to
    # weekdays (Mon-Fri). Using the raw union pollutes the calendar
    # with crypto/FX weekends, which would break the ``shift(lookback)``
    # semantics for equity instruments (the 21st prior union-row for
    # SPY lands on a weekend with NaN close). Weekdays-only keeps the
    # backtest on the dominant-asset NYSE-like calendar; crypto
    # weekend bars are dropped at load time, and crypto ret_t on a
    # Monday represents Fri-close → Mon-close (3-day return), which is
    # standard multi-asset daily convention.
    union_index = sorted(
        set().union(*(s.index for s in closes.values()))
    )
    idx = pd.DatetimeIndex(union_index)
    idx = idx[idx.dayofweek < 5]
    close_df = pd.DataFrame(
        {t: closes[t].reindex(idx) for t in tickers}, index=idx
    )

    # Per-instrument daily log-to-pct returns on the native index
    # (ffill within-asset is NOT applied — we only trade on bars where
    # the asset actually has a close).
    ret_df = close_df.pct_change()

    # Rolling realised vol (annualised), shifted by 1 to avoid look-ahead.
    ann_factor = np.sqrt(TRADING_DAYS_PER_YEAR)
    vol_df = (
        ret_df.rolling(config.vol_lookback_days, min_periods=config.vol_lookback_days)
        .std(ddof=0)
        * ann_factor
    )
    vol_prev = vol_df.shift(1)

    # Past-lookback cumulative return (ratio − 1) at each bar for each
    # asset; shifted by 0 because we compute it at t with close_t and
    # close_{t-lookback}, both known at end-of-t. Signal is evaluated
    # strictly at month-end t and applied from t+1 onward, so no
    # look-ahead.
    past_ret_df = close_df / close_df.shift(config.lookback_days) - 1.0

    # Active mask per asset: require lookback AND vol_lookback bars of
    # data (we use max of the two).
    warmup = max(config.lookback_days, config.vol_lookback_days)
    # An asset is active at t if close_df has ≥ warmup non-NaN bars
    # strictly before t (vol_prev and past_ret_df being non-NaN already
    # imply this).
    warmup_mask = vol_prev.notna() & past_ret_df.notna() & close_df.notna()

    # Rebalance calendar = last trading day of each month where
    # union_index has a bar.
    eom_mask = _monthly_eom_mask(idx)
    rebalance_dates = idx[eom_mask]

    n = len(idx)
    tickers_list = list(tickers)
    n_assets = len(tickers_list)

    # Output buffers.
    portfolio_weights = np.zeros((n, n_assets), dtype=float)
    active_count_arr = np.zeros(n, dtype=int)
    daily_net = np.zeros(n, dtype=float)

    # Per-asset cost lookup.
    per_asset_rt_bps = np.zeros(n_assets, dtype=float)
    for i, t in enumerate(tickers_list):
        cls = class_lookup.get(t, default_asset_class(t))
        per_asset_rt_bps[i] = config.round_trip_bps_by_class.get(
            cls, DEFAULT_ROUND_TRIP_BPS_BY_CLASS.get(cls, 10.0)
        )

    # Signal evaluation on rebalance bars only.
    current_weights = np.zeros(n_assets, dtype=float)
    cum_cost = 0.0
    cum_swap = 0.0
    long_bar_count = 0

    # Track per-asset bar-hold segments for median-hold-days metric.
    # A "hold segment" = contiguous run of bars where weight_i > 0.
    hold_lengths: list[int] = []
    in_segment = np.zeros(n_assets, dtype=bool)
    seg_bar_count = np.zeros(n_assets, dtype=int)

    close_vals = close_df.to_numpy(float)
    ret_vals = ret_df.to_numpy(float)
    vol_prev_vals = vol_prev.to_numpy(float)
    past_ret_vals = past_ret_df.to_numpy(float)
    active_vals = warmup_mask.to_numpy(bool)

    swap_daily_frac = config.swap_daily_bps / 10_000.0

    for t_idx in range(n):
        bar_date = idx[t_idx]

        # Rebalance decision — uses data known strictly at bar_date
        # (past_ret uses close_t / close_{t-L}; vol uses σ̂_{t-1}).
        if eom_mask.iloc[t_idx] if isinstance(eom_mask, pd.Series) else eom_mask[t_idx]:
            new_weights = np.zeros(n_assets, dtype=float)
            active_i = []
            for i in range(n_assets):
                if not active_vals[t_idx, i]:
                    continue
                active_i.append(i)
                sig = 1.0 if past_ret_vals[t_idx, i] > 0 else 0.0
                sigma_i = vol_prev_vals[t_idx, i]
                if not (sigma_i is not None and np.isfinite(sigma_i) and sigma_i > 0):
                    continue
                w = sig * config.vol_target_annual / sigma_i
                w = min(max(w, 0.0), config.max_leverage_per_asset)
                new_weights[i] = w

            n_active = len(active_i)
            if n_active >= config.min_active_instruments:
                # Equal-dollar budget: divide per-asset weight by N_active.
                # Gross notional then ranges roughly in [0, max_leverage_per_asset]
                # per instrument bucket ⇒ portfolio gross ≤ max_leverage_per_asset.
                new_weights = new_weights / float(n_active)
            else:
                new_weights[:] = 0.0

            # Transaction cost at the rebalance close.
            delta = np.abs(new_weights - current_weights)
            # Round-trip bps per asset, applied to |delta| weight change.
            # |delta| represents the fraction of portfolio turned over for
            # asset i, and round-trip bps covers entry+exit (factor of 1
            # on |delta| since a full round-trip is 1.0 turnover).
            cost_today = float(np.sum(delta * per_asset_rt_bps / 10_000.0))
            cum_cost += cost_today
            current_weights = new_weights
        else:
            cost_today = 0.0

        # Swap on held longs (applied EVERY day, not just rebalance).
        gross_long = float(np.sum(np.maximum(current_weights, 0.0)))
        swap_today = gross_long * swap_daily_frac
        cum_swap += swap_today

        # Store weights used for the bar.
        portfolio_weights[t_idx] = current_weights

        # Active count diagnostic.
        active_count_arr[t_idx] = int(np.sum(active_vals[t_idx]))

        # Portfolio daily return = Σ w_i * ret_i_t, NaN-treated-as-0
        # (if an asset has no bar at t, its ret is NaN and contributes
        # 0 — the weight is still notional, but no PnL).
        if t_idx == 0:
            port_ret = 0.0
        else:
            per_asset_contrib = current_weights * ret_vals[t_idx]
            # Where ret is NaN, contribute 0 (asset didn't trade).
            per_asset_contrib = np.where(
                np.isnan(per_asset_contrib), 0.0, per_asset_contrib
            )
            port_ret = float(np.sum(per_asset_contrib))

        # Subtract today's cost and swap.
        daily_net[t_idx] = port_ret - cost_today - swap_today

        # Hold-segment bookkeeping.
        for i in range(n_assets):
            is_long = current_weights[i] > 0
            if is_long:
                long_bar_count += 1
                if not in_segment[i]:
                    in_segment[i] = True
                    seg_bar_count[i] = 1
                else:
                    seg_bar_count[i] += 1
            else:
                if in_segment[i]:
                    hold_lengths.append(int(seg_bar_count[i]))
                    in_segment[i] = False
                    seg_bar_count[i] = 0

    # Close any open segments at end.
    for i in range(n_assets):
        if in_segment[i] and seg_bar_count[i] > 0:
            hold_lengths.append(int(seg_bar_count[i]))

    daily_net_s = pd.Series(daily_net, index=idx, dtype=float)
    equity = (1.0 + daily_net_s).cumprod()
    weights_df = pd.DataFrame(
        portfolio_weights, index=idx, columns=tickers_list
    )
    active_s = pd.Series(active_count_arr, index=idx, dtype=int)

    median_hold = float(np.median(hold_lengths)) if hold_lengths else 0.0

    return TSMOMMultiAssetResult(
        daily_returns=daily_net_s,
        equity=equity,
        weights=weights_df,
        active_count=active_s,
        rebalance_dates=pd.DatetimeIndex(rebalance_dates),
        n_rebalances=int(len(rebalance_dates)),
        median_hold_days=median_hold,
        cum_cost_pct=float(cum_cost),
        cum_swap_pct=float(cum_swap),
        n_long_bar_positions=int(long_bar_count),
        universe_tickers=tuple(tickers_list),
    )
