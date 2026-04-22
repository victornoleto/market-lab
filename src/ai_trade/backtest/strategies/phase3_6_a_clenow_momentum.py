"""Phase 3.6 — Family A: Clenow cross-sectional momentum (top-N stocks).

Return-series simulator for the swing-horizon variant of the Clenow
*Stocks on the Move* strategy [stocks_on_the_move] applied to a Tiingo
US-equity panel with a 21-trading-day rebalance cadence.

This module is a **clean return-series strategy** in the spirit of
:mod:`ai_trade.backtest.strategies.letf_rotation`: it does NOT touch the
bar-level portfolio engine. The simulation is fully vectorized on the
daily close panel; each rebalance produces a weight vector applied to
the *next* day's simple returns (so there is no look-ahead — all signals
use information through the close of day ``t``, and positions pay/earn
the return of day ``t+1``).

Design choices (every parameter cites a page in Clenow's book)
--------------------------------------------------------------

* **Universe:** Tiingo daily panel (1695 tickers) intersected with a
  liquidity screen (median 252-day dollar volume ≥ ``adv_usd_floor``)
  AND a minimum-history filter (≥ 90 trading days of data at the
  rebalance). The full PIT S&P 500 membership is not available in this
  repo — the screen is documented as a proxy. Rationale for universe
  choice: [stocks_on_the_move, p.238-239] (need survivorship-adjusted
  liquid universe) + [stocks_on_the_move, p.60-70] (Clenow uses S&P
  500 historical members; we approximate with a liquidity filter on
  Tiingo bulk data).

  Survivorship caveat: the Tiingo panel does include delisted tickers
  that were added historically, but the 1695-ticker snapshot is still
  an approximation. This is explicitly flagged in the AGGREGATE report.

* **Ranking score (adjusted slope):** annualized exponential regression
  slope of log-close over 90 trading days, multiplied by R² of the
  same regression. [stocks_on_the_move, p.75-77, p.81-82].

  Formula: ``(exp(slope_m))^250 - 1`` × R² where ``slope_m`` is the
  daily log-slope of ``ln(P_t) = a + m·t`` fit over the last 90 bars.

* **Per-stock trend filter:** close > SMA(close, 100).
  [stocks_on_the_move, p.81, p.104].

* **Per-stock gap filter:** any single-bar move > 15% in the past 90
  days disqualifies the stock. [stocks_on_the_move, p.82, p.98, p.104].

* **Market regime filter:** SPY close > SMA(SPY close, 200).
  When OFF, no NEW positions are opened. Existing holdings exit on
  their own criteria (ranking / trend / gap). [stocks_on_the_move,
  p.66-67, p.98-99, p.111].

* **Position sizing:** ATR-based risk parity at 0.1% daily risk per
  stock. ``shares ∝ account_value · 0.001 / ATR_20``.
  [stocks_on_the_move, p.86-89, p.228-229].

  Implementation note: this simulator operates on weights (fractions
  of equity), not share counts — we express the rule as
  ``weight_i ∝ 1 / (ATR_20_i / close_i)`` (the inverse of the
  relative-price ATR) and normalize so the sum equals
  ``gross_exposure`` (≤ 1.0). This is mathematically equivalent to
  Clenow's dollar-risk-parity sizing at each rebalance.

* **Rebalance cadence:** every 21 trading days (~1 calendar month).
  Clenow uses Wednesday weekly [p.98-99]; the plan brief locks 21d for
  swing-horizon evaluation. Shorter cadence {10d} and longer {21d} are
  included in the grid for CPCV/PBO purposes.

* **Top-N holding cutoff:** N ∈ {10, 20, 30}. Clenow reports [p.229-230]
  that 20-30 is optimal; we extend down to 10 for the grid sensitivity
  required by gates 11-12.

* **Exits:** on each rebalance, drop any held stock that (a) ranks
  outside top-N, (b) fell below its 100d SMA, (c) had a >15% gap,
  or (d) has insufficient history. [stocks_on_the_move, p.99, p.110].

* **Frictions (Inter broker, plan §3.2):** 0 commission on stocks,
  0.05% one-way spread/slippage applied to the turnover fraction at
  each rebalance. BR 15% capital-gains tax on realized gains
  (positive-month net) is applied at end-of-month on the monthly
  portfolio return (simplified: tax on the positive part of the
  monthly aggregated return; modeling realized-per-lot gains would
  require share-lot tracking, out-of-scope for a return-series sim).
  [plan §3.2 + mandate §1 dual broker strategy].

* **Cost×2 sensitivity (gate 13):** spread doubled to 0.10% one-way.

Look-ahead audit
----------------

The signal for rebalance day ``t`` uses:

* Regression slope / R² over ``[t-89, t]`` inclusive.
* SMA 100 / 200 ending on day ``t``.
* ATR 20 ending on day ``t``.
* Gap filter looking back 90 bars ending on day ``t``.

The resulting weight vector ``w_t`` is applied to the return ``r_{t+1}``
(i.e. ``prev_weight × next_return``). No information from day ``t+1`` or
later enters the signal. This matches the convention audited in
[advances_fin_ml, p.31-34] and used by the F2-patched
:func:`simulate_plano_a_rotation` engine.

Citations
---------

* Clenow core methodology: [stocks_on_the_move, p.66-111].
* Anti-optimization principle (we stay within Clenow's ranges):
  [stocks_on_the_move, p.219-220, p.229].
* Look-ahead bias audit pattern:
  [advances_fin_ml, p.31-34].
* Risk-parity ATR sizing cross-reference:
  [systematic_trading, p.~175] (Carver vol-targeting).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "ClenowMomentumConfig",
    "ClenowMomentumResult",
    "adjusted_slope",
    "compute_atr",
    "simulate_clenow_momentum",
]


TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class ClenowMomentumConfig:
    """Immutable configuration for one Clenow momentum backtest cell.

    Parameters
    ----------
    top_n : int
        Number of stocks to hold at any time. Clenow canonical ~20
        [p.229]. Grid covers {10, 20, 30}.
    rebalance_days : int
        Trading-day rebalance period. Canonical weekly (5d) [p.98]; we
        test {10, 21} for swing horizon.
    use_regime_filter : bool
        When True, do not open new positions while SPY < SMA200
        [p.66-67, p.98-99]. Default True (Clenow canonical).
    regression_days : int
        Window for the exponential-regression slope ranking. Clenow
        canonical 90 [p.73]; fixed here (p.223-224 sensitivity check
        says 60-240 all similar).
    per_stock_ma_days : int
        Per-stock trend filter SMA length [p.81].
    market_ma_days : int
        Market regime SMA on SPY [p.66].
    gap_threshold : float
        Single-bar move that disqualifies (fraction, e.g. 0.15) [p.82].
    gap_lookback_days : int
        Lookback window for the gap filter [p.82].
    atr_days : int
        ATR window for sizing [p.88].
    atr_risk_factor : float
        Target daily-dollar-risk fraction per position [p.88, p.228-229].
    spread_one_way_pct : float
        Bid-ask + slippage per one-way trade, as fraction of notional.
        Inter default 0.0005 (5 bps one-way); cost×2 sensitivity uses
        0.0010.
    commission_per_trade : float
        Inter: 0 on US stocks [plan §3.2].
    tax_rate : float
        BR capital-gains rate applied to positive monthly net returns.
        0.15 per plan §3.2 + mandate §1.
    adv_usd_floor : float
        Liquidity filter: 252-day median dollar volume (USD) needed to
        be considered. 50M = approx S&P 400+ liquidity floor. Proxy for
        S&P 500 membership [p.238-239].
    """

    top_n: int = 20
    rebalance_days: int = 21
    use_regime_filter: bool = True
    regression_days: int = 90
    per_stock_ma_days: int = 100
    market_ma_days: int = 200
    gap_threshold: float = 0.15
    gap_lookback_days: int = 90
    atr_days: int = 20
    atr_risk_factor: float = 0.001
    spread_one_way_pct: float = 0.0005
    commission_per_trade: float = 0.0
    tax_rate: float = 0.15
    adv_usd_floor: float = 50_000_000.0

    def __post_init__(self) -> None:
        if self.top_n < 1:
            raise ValueError(f"top_n must be >= 1, got {self.top_n}")
        if self.rebalance_days < 1:
            raise ValueError(f"rebalance_days must be >= 1, got {self.rebalance_days}")
        if self.regression_days < 10:
            raise ValueError(f"regression_days must be >= 10, got {self.regression_days}")
        if self.gap_threshold <= 0:
            raise ValueError(f"gap_threshold must be > 0, got {self.gap_threshold}")


@dataclass
class ClenowMomentumResult:
    """Output of a Clenow momentum simulation.

    Attributes
    ----------
    equity : pd.Series
        Daily equity curve starting at 1.0 (post-cost, post-tax).
    daily_returns : pd.Series
        Daily net return (post-cost, post-tax).
    gross_returns : pd.Series
        Daily return before costs/taxes (useful for cost ablation).
    n_held : pd.Series
        Number of positions held each day.
    turnover : pd.Series
        Fraction of portfolio turned over at each rebalance
        (one-way). 0 on non-rebalance days.
    hold_lengths : list[int]
        Observed hold-length distribution (trading days) across all
        position entries/exits in the run. Used for the median-hold gate.
    cum_cost_pct : float
        Cumulative cost drag as fraction of initial equity.
    cum_tax_pct : float
        Cumulative tax paid as fraction of initial equity.
    """

    equity: pd.Series
    daily_returns: pd.Series
    gross_returns: pd.Series
    n_held: pd.Series
    turnover: pd.Series
    hold_lengths: list[int] = field(default_factory=list)
    cum_cost_pct: float = 0.0
    cum_tax_pct: float = 0.0

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        return float(r.mean() / sd * np.sqrt(periods_per_year)) if sd > 0 else 0.0

    def cagr(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        eq = self.equity.dropna()
        if len(eq) < 2:
            return 0.0
        years = (len(eq) - 1) / periods_per_year
        total = float(eq.iloc[-1] / eq.iloc[0])
        if years <= 0 or total <= 0:
            return 0.0
        return total ** (1.0 / years) - 1.0

    def max_drawdown(self) -> float:
        eq = self.equity.dropna()
        if eq.empty:
            return 0.0
        peak = eq.cummax()
        return float((eq / peak - 1.0).min())

    def median_hold_days(self) -> float:
        if not self.hold_lengths:
            return float("nan")
        return float(np.median(self.hold_lengths))


def adjusted_slope(log_prices: np.ndarray) -> tuple[float, float]:
    """Clenow's adjusted-slope score for a single 90-bar window.

    Returns ``(annualized_slope, r_squared)``. The ranking score is the
    product. Formula: :math:`(e^{m})^{250} - 1` where ``m`` is the OLS
    slope of ``log_prices`` vs. ``t``. [stocks_on_the_move, p.75-77].
    """
    n = len(log_prices)
    if n < 2 or not np.all(np.isfinite(log_prices)):
        return float("nan"), float("nan")
    t = np.arange(n, dtype=float)
    # Simple OLS: slope, intercept, R²
    t_mean = t.mean()
    y_mean = log_prices.mean()
    dt = t - t_mean
    dy = log_prices - y_mean
    denom = float((dt * dt).sum())
    if denom <= 0:
        return float("nan"), float("nan")
    slope_m = float((dt * dy).sum() / denom)
    intercept = y_mean - slope_m * t_mean
    pred = intercept + slope_m * t
    ss_res = float(((log_prices - pred) ** 2).sum())
    ss_tot = float(((log_prices - y_mean) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    # Annualize: (e^m)^250 - 1 per Clenow's Excel formula p.77
    annualized = float(np.exp(slope_m) ** 250 - 1.0)
    return annualized, r2


def compute_atr(
    high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20
) -> pd.Series:
    """True-range moving average (Wilder-style simple mean).

    [stocks_on_the_move, p.88].
    """
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window=window, min_periods=window).mean()


def _build_panel(
    panel: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Stack per-ticker OHLC+ADV into dense wide DataFrames on union index.

    Returns (close_adj, high_adj, low_adj, adv_usd, valid) where ``valid``
    is a bool-frame marking cells with finite price + sufficient history.
    """
    tickers = sorted(panel.keys())
    # Build via per-ticker Series concatenation — avoids the pathological
    # `.loc` assignment pattern that silently drops rows at scale.
    close_cols: dict[str, pd.Series] = {}
    high_cols: dict[str, pd.Series] = {}
    low_cols: dict[str, pd.Series] = {}
    raw_close_cols: dict[str, pd.Series] = {}
    volume_cols: dict[str, pd.Series] = {}
    for t in tickers:
        df = panel[t]
        ratio = (df["adj_close"] / df["close"]).astype(float)
        close_cols[t] = df["adj_close"].astype(float)
        high_cols[t] = df["high"].astype(float) * ratio
        low_cols[t] = df["low"].astype(float) * ratio
        raw_close_cols[t] = df["close"].astype(float)
        volume_cols[t] = df["volume"].astype(float)
    close = pd.DataFrame(close_cols).sort_index()
    high = pd.DataFrame(high_cols).sort_index()
    low = pd.DataFrame(low_cols).sort_index()
    raw_close = pd.DataFrame(raw_close_cols).sort_index()
    volume = pd.DataFrame(volume_cols).sort_index()
    adv_usd = (raw_close * volume).rolling(window=252, min_periods=60).median()
    valid = close.notna()
    return close, high, low, adv_usd, valid


def simulate_clenow_momentum(
    panel: dict[str, pd.DataFrame],
    spy: pd.DataFrame,
    config: ClenowMomentumConfig,
) -> ClenowMomentumResult:
    """Run a single Clenow cross-sectional momentum configuration.

    Parameters
    ----------
    panel : dict[str, pd.DataFrame]
        Per-ticker DataFrames with columns ['open','high','low','close',
        'adj_close','volume'] indexed by trading date. The simulator
        uses ``adj_close`` for return/ranking and derives split-adjusted
        high/low by the ``adj_close/close`` ratio.
    spy : pd.DataFrame
        SPY DataFrame in the same schema, for the 200d regime filter
        [p.66].
    config : ClenowMomentumConfig

    Returns
    -------
    ClenowMomentumResult
    """
    close, high, low, adv_usd, valid = _build_panel(panel)
    tickers = close.columns.tolist()
    # SPY regime series aligned to the panel index
    spy_close = spy["adj_close"].astype(float).reindex(close.index)
    spy_sma = spy_close.rolling(
        window=config.market_ma_days, min_periods=config.market_ma_days
    ).mean()
    regime_on = (spy_close > spy_sma).fillna(False)

    # Per-stock rolling stats
    sma_per_stock = close.rolling(
        window=config.per_stock_ma_days, min_periods=config.per_stock_ma_days
    ).mean()
    # ATR per ticker — build TR then rolling mean per-column.
    # Use element-wise numpy max over three aligned matrices (avoids the
    # brittle concat+groupby pattern that fails at wide-panel scale).
    prev_close = close.shift(1)
    hl = (high - low).abs()
    hc = (high - prev_close).abs()
    lc = (low - prev_close).abs()
    tr_values = np.nanmax(
        np.stack([hl.to_numpy(), hc.to_numpy(), lc.to_numpy()], axis=0), axis=0
    )
    tr = pd.DataFrame(tr_values, index=close.index, columns=close.columns)
    atr = tr.rolling(
        window=config.atr_days, min_periods=config.atr_days
    ).mean()

    # Pct returns for gap filter and equity compounding.
    # fill_method=None → strict NaN handling (no pad); prevents synthetic
    # returns at ticker inception boundaries.
    ret = close.pct_change(fill_method=None)
    # Max absolute gap over last gap_lookback_days
    max_gap = ret.abs().rolling(
        window=config.gap_lookback_days, min_periods=10
    ).max()

    # Scan bars and rebalance every rebalance_days (starting after
    # enough warmup). Weights held constant between rebalances, applied
    # to the *next* day's returns (prev_weight × ret convention).
    n_bars = len(close.index)
    warmup = max(
        config.regression_days,
        config.per_stock_ma_days,
        config.market_ma_days,
        config.gap_lookback_days,
        config.atr_days + 1,
    )

    # Weight matrix: weights[i, j] = weight held at close of day i, applied
    # to day i's close-to-close return to get the return *earned* on day i+1.
    weights = pd.DataFrame(0.0, index=close.index, columns=tickers)
    # Track per-ticker entry bar index → for hold-length stats.
    entry_bar: dict[str, int] = {}
    hold_lengths: list[int] = []
    turnover = pd.Series(0.0, index=close.index)
    gross_r = pd.Series(0.0, index=close.index)
    net_r = pd.Series(0.0, index=close.index)
    cost_cum = 0.0

    current_w = pd.Series(0.0, index=tickers)
    log_close = np.log(close.to_numpy())  # precompute for slope speed
    close_arr = close.to_numpy()
    adv_arr = adv_usd.to_numpy()
    sma_arr = sma_per_stock.to_numpy()
    max_gap_arr = max_gap.to_numpy()
    atr_arr = atr.to_numpy()
    next_rebal = warmup  # first rebalance at this bar

    for i in range(n_bars):
        # Apply current_w to day i's return (which was computed as
        # close_i / close_{i-1} - 1, i.e. *today's* return earned given
        # *yesterday's close* weight — but our convention stores weights
        # AS-OF day i applied to the return from i to i+1, realized at
        # close i+1). We therefore use fwd_ret.iloc[i-1] as the return
        # booked *today* from yesterday's weights.
        if i > 0:
            r_today = ret.iloc[i].reindex(tickers).fillna(0.0)
            g = float((current_w * r_today).sum())
            gross_r.iloc[i] = g

        # Rebalance logic at next_rebal
        if i == next_rebal and i >= warmup:
            # --- eligibility mask ---
            j_start = i - config.regression_days + 1
            # Need finite close at i and finite close at j_start (history)
            have_hist = (
                np.isfinite(close_arr[i])
                & np.isfinite(close_arr[j_start])
            )
            # Liquidity
            liquid = np.isfinite(adv_arr[i]) & (adv_arr[i] >= config.adv_usd_floor)
            # Per-stock trend filter
            trend_ok = np.isfinite(sma_arr[i]) & (close_arr[i] > sma_arr[i])
            # Gap filter
            gap_ok = np.isfinite(max_gap_arr[i]) & (max_gap_arr[i] <= config.gap_threshold)
            # ATR for sizing
            atr_ok = np.isfinite(atr_arr[i]) & (atr_arr[i] > 0.0)
            eligible = have_hist & liquid & trend_ok & gap_ok & atr_ok

            # --- score eligible stocks ---
            scores = np.full(len(tickers), -np.inf, dtype=float)
            if eligible.any():
                lp_window = log_close[j_start : i + 1, :]  # (N_bars, N_tickers)
                # Per eligible column, compute slope + R²
                elig_idx = np.where(eligible)[0]
                for jj in elig_idx:
                    ann, r2 = adjusted_slope(lp_window[:, jj])
                    if not np.isfinite(ann) or not np.isfinite(r2):
                        continue
                    scores[jj] = ann * r2

            # --- build target weights ---
            # Regime gate: when OFF, do not ADD. But we can keep existing.
            market_on = bool(regime_on.iloc[i]) if not config.use_regime_filter else bool(regime_on.iloc[i])
            # If regime filter disabled, treat market as always ON:
            if not config.use_regime_filter:
                market_on = True

            # Drop held stocks that no longer meet rank / trend / gap /
            # liquidity (per rules p.99, p.110).
            held = [t for t, w in current_w.items() if w > 0.0]
            # Rank scores descending — get top candidates
            order = np.argsort(-scores)
            # Top-N cutoff (among those with a finite positive score?)
            top_set: list[str] = []
            for idx_rank in order[: max(config.top_n * 3, config.top_n)]:
                if scores[idx_rank] <= -np.inf:
                    break
                top_set.append(tickers[idx_rank])
                if len(top_set) >= config.top_n:
                    break

            # Decide which held names to keep vs drop
            keep: list[str] = []
            drop: list[str] = []
            for t in held:
                jj = tickers.index(t)
                # drop if: not eligible OR rank outside top_N
                if (not eligible[jj]) or (t not in top_set):
                    drop.append(t)
                else:
                    keep.append(t)

            # If market OFF, do not add new names; only drops allowed.
            add: list[str] = []
            if market_on:
                for t in top_set:
                    if t not in keep and len(keep) + len(add) < config.top_n:
                        add.append(t)

            # Final target basket
            basket = keep + add
            # Compute ATR risk-parity weights over the basket
            new_w = pd.Series(0.0, index=tickers)
            if basket:
                raw = np.zeros(len(basket))
                for idx_b, t in enumerate(basket):
                    jj = tickers.index(t)
                    c = close_arr[i, jj]
                    a = atr_arr[i, jj]
                    if a > 0 and c > 0:
                        # Relative ATR — dollar-risk-parity equivalent
                        raw[idx_b] = config.atr_risk_factor / (a / c)
                total = raw.sum()
                if total > 0:
                    # Normalize so weights sum to min(1.0, total) — i.e.
                    # if atr-risk sizing totals < 1.0 we leave cash; if
                    # > 1.0 we cap gross exposure at 1.0 (no leverage).
                    gross_target = min(1.0, total)
                    scale_factor = gross_target / total
                    for idx_b, t in enumerate(basket):
                        new_w[t] = raw[idx_b] * scale_factor

            # Turnover + costs on this rebalance
            delta = (new_w - current_w).abs()
            tov = float(delta.sum())  # one-way turnover fraction
            turnover.iloc[i] = tov
            cost_today = (
                tov * config.spread_one_way_pct + config.commission_per_trade
            )
            # Apply cost as a negative return today (on top of gross)
            gross_r.iloc[i] = gross_r.iloc[i] - cost_today
            cost_cum += cost_today

            # Hold-length tracking
            for t in drop:
                if t in entry_bar:
                    hold_lengths.append(i - entry_bar[t])
                    del entry_bar[t]
            for t in add:
                entry_bar[t] = i

            current_w = new_w
            next_rebal = i + config.rebalance_days

        weights.iloc[i] = current_w

    # Close out any still-held positions at the last bar for hold-length stat
    last_i = n_bars - 1
    for t, bar0 in entry_bar.items():
        hold_lengths.append(last_i - bar0)

    # Monthly tax on positive net monthly returns (BR Inter path).
    # For simplicity: aggregate gross_r (already net of transaction cost) by
    # calendar month; on each positive month, apply tax_rate on that month's
    # cumulative excess-over-zero. Reduce returns on the last day of the
    # month by the equivalent drag so the daily series compounds to the
    # net-of-tax monthly result.
    net_r_arr = gross_r.to_numpy().copy()
    gross_r_arr = gross_r.to_numpy()
    index = gross_r.index
    tax_cum = 0.0
    if config.tax_rate > 0:
        month_key = pd.DatetimeIndex(index).to_period("M")
        # Build month→last-bar index
        last_of_month: dict = {}
        for i_, m in enumerate(month_key):
            last_of_month[m] = i_
        for m, i_last in last_of_month.items():
            mask = month_key == m
            month_slice = gross_r_arr[mask]
            if len(month_slice) == 0:
                continue
            monthly_ret = float(np.prod(1.0 + month_slice) - 1.0)
            if monthly_ret > 0:
                tax = monthly_ret * config.tax_rate
                # Apply tax as a one-time drag on the last bar: multiply
                # equity by (1 - tax/(1+monthly_ret)) equivalent — we
                # encode as subtracting tax/(1+monthly_ret) from that
                # day's net return.
                # Simpler & sufficient: subtract tax fraction from that
                # day's return (accepting O(tax²) approximation).
                net_r_arr[i_last] = net_r_arr[i_last] - tax
                tax_cum += tax

    net_r = pd.Series(net_r_arr, index=index)
    equity = (1.0 + net_r).cumprod()
    n_held = (weights > 0).sum(axis=1).astype(int)

    return ClenowMomentumResult(
        equity=equity,
        daily_returns=net_r,
        gross_returns=pd.Series(gross_r_arr, index=index),
        n_held=n_held,
        turnover=turnover,
        hold_lengths=hold_lengths,
        cum_cost_pct=cost_cum,
        cum_tax_pct=tax_cum,
    )
