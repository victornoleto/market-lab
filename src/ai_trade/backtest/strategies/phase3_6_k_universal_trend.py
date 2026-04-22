"""Phase 3.6 — Family K: Penfold's Universal Trend Tactics.

Multi-asset Donchian-breakout + ATR-trailing-stop strategy on a P24
ETF-proxy basket, sized by fixed-fraction risk-per-position with a
gross-leverage cap. Clean return-series implementation in the spirit of
:mod:`ai_trade.backtest.strategies.letf_rotation` and
:mod:`ai_trade.backtest.strategies.phase3_6_f_vol_target_managed_futures`.

Penfold-specific differentiators (mandatory per brief)
------------------------------------------------------

Family K is structurally distinct from prior Wave 1/2/2b families on
three Penfold-specific axes — these are the raison d'être of the
family:

1. **Exit rule = ATR trailing stop** [universal_trend_tactics, p.338-343,
   p.68-69]. Long position exits when ``close_t < trailing_max - ATR(14)
   × k``, where ``trailing_max`` is the highest close seen since entry.
   This is the "cut losses short / let profits run" operationalization
   (golden tenets 2 + 3, p.68-69 — Ricardo 1838). Prior families D/E/F/H/J
   used signal-reversal exits (regime flip / forecast sign change /
   classifier prediction) — none used an explicit ATR-distance trail.
   **No look-ahead:** ATR_t uses returns through bar t-1 only; trailing
   max at bar t uses closes through t-1 only.

2. **P24 portfolio approximation** [universal_trend_tactics, p.168-169,
   p.261-262]. Penfold mandates "diversity + average daily volume" as
   the ONLY market-selection criteria — no curve-fitting on which
   markets work. We approximate the futures P24 (24 contracts across 8
   sectors) with **9 liquid Tiingo ETFs across 5 sectors**:
   - **Equities** (4): SPY, QQQ, EFA, EEM
   - **Rates/Bonds** (2): TLT (20Y), IEF (7-10Y)
   - **Metals** (2): GLD, SLV
   - **Energy** (1): USO
   Penfold's grains/livestock/softs/currencies sectors have no liquid
   ETF coverage in the Tiingo bulk usable for the IS window — DBA stops
   trading 2023-12-29 (before FWD), UUP/FXE/DBE absent. Honest scope
   limitation; documented in AGGREGATE.md §Data caveats.

3. **Ulcer Performance Index (UPI) as supplementary metric**
   [universal_trend_tactics, p.245-246, p.251-255]. UPI = (R_p − R_f) /
   UI where UI = √(Σ D_i² / n) and D_i is the percentage drawdown at
   period i from running peak. Penfold argues UPI > Sharpe for trend
   strategies because it measures depth × duration of drawdown
   (p.245). UPI is **NOT a gate** — it's a diagnostic alongside the 13
   plan gates.

Penfold also mandates the **3 golden tenets** (p.68-69):
   (1) Follow the trend → Donchian breakout long-only entry
   (2) Cut losses short → ATR-distance trail
   (3) Let profits run → trailing max tracks new highs

Long-only on ETFs (Penfold uses long-short on futures, but ETF shorts
have borrow + dividend friction that the cost model doesn't capture
honestly; long-only is the conservative honest choice per
``[universal_trend_tactics, p.272]`` — "always rank by CAGR with money
management applied", and money management here mandates honest cost
treatment).

Design parameters (every choice cites a page)
---------------------------------------------

* **Universe (P24 proxy):** 9 ETFs above. Citation
  ``[universal_trend_tactics, p.168-169, p.261-262]`` for "diversity +
  volume only" rationale and 8-sector framework. We honestly trim from
  8 → 5 sectors due to Tiingo coverage; documented as scope limitation.

* **Donchian breakout entry:** long if ``close_t > max(high_{t-N},
  ..., high_{t-1})`` for lookback ``N``. The Turtle System 1 4-week =
  20 trading days ``[universal_trend_tactics, p.295-299]`` is the
  benchmark; we test ``N ∈ {20, 50, 80, 120}``. Lookback>20 = "slower"
  trend → fewer whipsaws, longer holds. Penfold benchmarks Turtle
  Trading 4-week entry / 2-week stop ``[universal_trend_tactics,
  p.295-299, p.210-217]``.

* **ATR trailing stop:** ATR(14) per Wilder's standard
  ``[universal_trend_tactics, p.338-343]`` (Penfold uses bar-level
  swing stops; ATR(14) is the universal proxy used by Turtle System
  ``[universal_trend_tactics, p.295-299]`` and is the accepted
  "industry-standard volatility unit"). Multiplier ``k ∈ {2.0, 3.0,
  4.0}``. Long exit when ``close_t < trailing_max − ATR_{t-1} × k``.

* **Position sizing — fixed fraction per position:** risk per position
  ``r ∈ {0.0025, 0.005, 0.010}`` of equity, position_size = ``r ×
  equity / (k × ATR_{t-1})`` (units of 1.0 notional per dollar of
  underlying). Cap aggregated gross at **100% of equity** to AVOID
  Family F's swap-drag trap (avg gross there was 2.22×). Penfold
  uses 2% per trade ``[universal_trend_tactics, p.291]`` as standard;
  we test 0.25/0.5/1.0% per leg because we have 9 simultaneous slots
  → 9 × 1.0% = 9% gross potential vs 100% cap. The lower per-leg
  risk reflects basket-level scaling per Penfold p.272 "money
  management applied".

* **Rebalance cadence:** signals are evaluated every bar; positions
  enter on the close of the breakout bar, exit on the close of the
  ATR-stop bar. No periodic rebalance — pure entry/exit driven.
  Cadence grid axis kept for the brief but defaulted to 1d (event-
  driven). Some swing-trend interpretations rebalance weekly to reduce
  noise; we offer 5d cadence (only re-evaluate signals every 5 bars)
  as an alternative.

* **Frictions — Pepperstone Razor (plan §3.1):**
  - Spread one-way 0.025% on SPY/QQQ/EFA/TLT/IEF/EEM, 0.05% on GLD/
    SLV, 0.10% on USO.
  - Commission $0.35 per 100k USD notional per side ≈ 3.5e-5 round-trip.
  - Overnight swap: −0.03%/night on long notional. (Long-only here.)
  - NO BR CG tax (Pepperstone non-BR jurisdiction).

* **Cost×2 sensitivity (gate 13):** spread + swap + commission all
  doubled.

Look-ahead audit
----------------

For each bar ``t``:

* ``donchian_high_{t-1}`` = max of ``high`` over [t-N, t-1]. Computed
  by ``rolling(N).max().shift(1)``.
* ``ATR_{t-1}`` = Wilder ATR over [t-14, t-1], shifted by 1.
* ``trailing_max[t]`` = max of close over the active long segment up to
  bar t-1; updated AFTER the bar's exit decision.
* Entry: if no position and ``close_t > donchian_high_{t-1}`` →
  long entry on close of bar t at price ``close_t``, sized by ATR_{t-1}.
* Exit: if long and ``close_t < trailing_max - k × ATR_{t-1}`` → exit
  on close of bar t at ``close_t``.
* **Alignment:** ``daily_return[t] = Σ_i prev_weight_i[t-1] × return_i[t]``
  is the F2-patched ``prev_weight × ret`` convention
  ``[advances_fin_ml, p.31-34]``.

The Donchian channel and ATR are computed on close-only / true-range
inputs through bar t-1; the entry decision uses today's close (close-
based breakout). This matches the Turtle System interpretation in
``[universal_trend_tactics, p.295-299]`` where signals are evaluated
at bar close and positions enter at close.

Citations
---------

* 3 golden tenets (follow trend / cut losses / let profits run):
  ``[universal_trend_tactics, p.68-69]`` (Ricardo 1800; print 1838).
* P24 portfolio = diversity + ADV across 8 sectors:
  ``[universal_trend_tactics, p.168-169, p.261-262]``.
* Donchian / Turtle channel breakout:
  ``[universal_trend_tactics, p.295-299, p.210-217]``.
* Two-stop trade plan (cut losses + let profits run):
  ``[universal_trend_tactics, p.338-343, p.361]``.
* Fixed-fraction position sizing:
  ``[universal_trend_tactics, p.271-272, p.291]``.
* Ulcer Index / UPI:
  ``[universal_trend_tactics, p.245-246, p.251-255, p.259]``.
* Equity-curve stability / minimal-variable design:
  ``[universal_trend_tactics, p.46-47, p.140, p.145-157, p.266-267,
  p.274-279]``.
* Lookahead audit + alignment: ``[advances_fin_ml, p.31-34]``.
* Pepperstone Razor cost model: plan
  ``docs/plans/2026-04-23-find-swing-winner-phase-3-6.md`` §3.1.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Mapping

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "UniversalTrendConfig",
    "UniversalTrendResult",
    "compute_atr_wilder",
    "simulate_universal_trend",
]

TRADING_DAYS_PER_YEAR = 252

#: Default per-asset one-way spread fraction (Pepperstone Razor, plan §3.1).
DEFAULT_SPREAD_ONE_WAY: dict[str, float] = {
    "SPY": 0.00025,
    "QQQ": 0.00025,
    "EFA": 0.00025,
    "EEM": 0.00025,
    "TLT": 0.00025,
    "IEF": 0.00025,
    "GLD": 0.00050,
    "SLV": 0.00050,
    "USO": 0.00100,
}


@dataclass(frozen=True)
class UniversalTrendConfig:
    """Immutable configuration for one Family K backtest cell.

    Parameters
    ----------
    donchian_lookback : int
        Donchian-channel lookback in trading days (entry triggers on
        ``close_t > max(high[t-N..t-1])``). Penfold benchmark is the
        Turtle System 4-week (20d). [universal_trend_tactics, p.295-299]
    atr_period : int
        ATR period (Wilder smoothing). 14 = standard Wilder.
        [universal_trend_tactics, p.338-343, p.295-299]
    atr_multiplier : float
        ATR multiplier ``k`` for trailing stop distance. Long exit when
        ``close_t < trailing_max − k × ATR_{t-1}``. Penfold's two-stop
        plan p.338-343; canonical Turtle k=2.
    risk_per_position : float
        Fixed fraction of equity risked per position (so position size
        = ``r × equity / (k × ATR_{t-1})``). Penfold p.291 uses 2%
        per trade for single-instrument tests; for a 9-asset basket
        we test 0.25/0.5/1.0% per leg to keep gross within the
        100%-of-equity cap. [universal_trend_tactics, p.291]
    rebalance_days : int
        Signal-evaluation cadence (1 = bar-by-bar). Some swing
        interpretations evaluate weekly (5d) to reduce noise.
    max_gross_exposure : float
        Cap on Σ|w_i|. 1.0 = no portfolio leverage (long-only basket).
        Set to keep swap drag bounded vs Family F's 2.22×.
    spread_one_way : mapping[str, float]
        Per-ticker spread fraction. Defaults from Pepperstone plan §3.1.
    commission_round_trip : float
        Round-trip commission fraction. 3.5e-5 = $0.35/100k Razor.
    swap_daily_long : float
        Daily long swap. −0.03%/night default (Pepperstone).
    tax_rate : float
        Capital-gains tax. 0.0 for Pepperstone (plan §3.1).
    """

    donchian_lookback: int = 50
    atr_period: int = 14
    atr_multiplier: float = 3.0
    risk_per_position: float = 0.005
    rebalance_days: int = 1
    max_gross_exposure: float = 1.0
    spread_one_way: dict[str, float] = field(
        default_factory=lambda: dict(DEFAULT_SPREAD_ONE_WAY)
    )
    commission_round_trip: float = 3.5e-5
    swap_daily_long: float = -0.0003
    tax_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.donchian_lookback < 5:
            raise ValueError(
                f"donchian_lookback must be ≥ 5, got {self.donchian_lookback}"
            )
        if self.atr_period < 2:
            raise ValueError(f"atr_period must be ≥ 2, got {self.atr_period}")
        if self.atr_multiplier <= 0:
            raise ValueError(
                f"atr_multiplier must be > 0, got {self.atr_multiplier}"
            )
        if not 0 < self.risk_per_position <= 0.10:
            raise ValueError(
                f"risk_per_position must be in (0, 0.10], "
                f"got {self.risk_per_position}"
            )
        if self.rebalance_days < 1:
            raise ValueError(
                f"rebalance_days must be ≥ 1, got {self.rebalance_days}"
            )
        if self.max_gross_exposure <= 0:
            raise ValueError(
                f"max_gross_exposure must be > 0, got {self.max_gross_exposure}"
            )


@dataclass
class UniversalTrendResult:
    """Output of one Family K simulation."""

    daily_returns: pd.Series
    gross_returns: pd.Series
    weights: pd.DataFrame
    entries: pd.DataFrame  # boolean — True on entry bar per asset
    exits: pd.DataFrame  # boolean — True on exit bar per asset
    hold_lengths: list[int] = field(default_factory=list)
    cum_spread_pct: float = 0.0
    cum_commission_pct: float = 0.0
    cum_swap_pct: float = 0.0
    n_trades: int = 0
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

    def ulcer_index(self) -> float:
        """UI = √(Σ D_i² / n) where D_i is percent drawdown from peak.

        [universal_trend_tactics, p.245-246]
        """
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        eq = (1.0 + r).cumprod()
        peak = eq.cummax()
        # D_i in PERCENT (Penfold uses percent units, p.246).
        d = (eq / peak - 1.0) * 100.0
        return float(np.sqrt(np.mean(d ** 2)))

    def upi(
        self,
        rf_annual: float = 0.0,
        periods_per_year: int = TRADING_DAYS_PER_YEAR,
    ) -> float:
        """UPI = (CAGR − R_f) / UI.

        [universal_trend_tactics, p.246, p.251-255]
        """
        ui = self.ulcer_index()
        if ui <= 0:
            return 0.0
        cagr = self.cagr(periods_per_year)
        # Convert CAGR to percent units to match UI's percent units.
        return float((cagr * 100.0 - rf_annual * 100.0) / ui)


def compute_atr_wilder(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """Wilder ATR — the canonical 1978 specification.

    ``TR_t = max(high_t − low_t, |high_t − close_{t-1}|,
                 |low_t − close_{t-1}|)``
    ``ATR_t = (ATR_{t-1} × (period-1) + TR_t) / period`` (Wilder smoothing).

    Returns the full ATR series indexed like ``close``. The first
    ``period-1`` values are NaN (warmup).
    """
    if not (high.index.equals(low.index) and high.index.equals(close.index)):
        raise ValueError("high/low/close must share the same index")
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    # Wilder smoothing == EMA with alpha = 1/period (≡ ewm with com=period-1).
    atr = tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    return atr


def simulate_universal_trend(
    panel: Mapping[str, pd.DataFrame],
    config: UniversalTrendConfig,
) -> UniversalTrendResult:
    """Run one Family K Donchian + ATR-trail simulation.

    Parameters
    ----------
    panel : mapping[str, pd.DataFrame]
        Per-ticker DataFrames with columns ``open, high, low, close,
        adj_close``. Daily Tiingo format.
    config : :class:`UniversalTrendConfig`
        Grid cell.

    Returns
    -------
    :class:`UniversalTrendResult`
    """
    if not panel:
        raise ValueError("panel is empty")
    tickers = tuple(sorted(panel.keys()))

    # --- Build aligned per-asset series (close, high, returns, ATR) ---
    closes: dict[str, pd.Series] = {}
    highs: dict[str, pd.Series] = {}
    rets: dict[str, pd.Series] = {}
    atrs: dict[str, pd.Series] = {}
    donchian_prev: dict[str, pd.Series] = {}
    for t in tickers:
        df = panel[t]
        for col in ("open", "high", "low", "close", "adj_close"):
            if col not in df.columns:
                raise ValueError(f"{t} missing column {col}")
        d = df.copy()
        d.index = pd.DatetimeIndex(d.index).normalize()
        d = d[~d.index.duplicated(keep="last")].sort_index()
        # Use unadjusted high/low/close for ATR + Donchian (these are
        # raw bar levels). Use adj_close for return series so dividends
        # are reinvested correctly per Penfold p.272 ("CAGR with money
        # management applied").
        c = d["close"].astype(float)
        h = d["high"].astype(float)
        l_ = d["low"].astype(float)
        ac = d["adj_close"].astype(float)
        closes[t] = c
        highs[t] = h
        rets[t] = ac.pct_change(fill_method=None)
        atrs[t] = compute_atr_wilder(h, l_, c, period=config.atr_period)
        # Donchian channel high using the prior N bars (exclusive of t).
        donchian_prev[t] = (
            h.rolling(window=config.donchian_lookback, min_periods=config.donchian_lookback)
            .max()
            .shift(1)
        )

    # Master index = union, restricted to weekdays (Tiingo is already weekdays).
    union_idx = sorted(set().union(*(s.index for s in closes.values())))
    union_idx = [d for d in union_idx if d.weekday() < 5]
    union_idx = pd.DatetimeIndex(union_idx)

    close_df = pd.DataFrame(
        {t: closes[t].reindex(union_idx) for t in tickers},
        index=union_idx,
    )
    ret_df = pd.DataFrame(
        {t: rets[t].reindex(union_idx) for t in tickers},
        index=union_idx,
    )
    atr_df = pd.DataFrame(
        {t: atrs[t].reindex(union_idx) for t in tickers},
        index=union_idx,
    )
    donchian_df = pd.DataFrame(
        {t: donchian_prev[t].reindex(union_idx) for t in tickers},
        index=union_idx,
    )
    # Shift ATR by 1 to avoid using today's TR in today's sizing/exit.
    atr_prev_df = atr_df.shift(1)

    n_bars = len(union_idx)
    n_assets = len(tickers)

    # --- Per-asset state arrays ---
    in_pos = np.zeros(n_assets, dtype=bool)
    entry_price = np.zeros(n_assets, dtype=float)
    trailing_max = np.zeros(n_assets, dtype=float)  # max close since entry
    weight_arr = np.zeros((n_bars, n_assets), dtype=float)
    entry_arr = np.zeros((n_bars, n_assets), dtype=bool)
    exit_arr = np.zeros((n_bars, n_assets), dtype=bool)
    seg_len = np.zeros(n_assets, dtype=int)
    hold_lengths: list[int] = []
    n_trades = 0

    close_v = close_df.to_numpy()
    atr_prev_v = atr_prev_df.to_numpy()
    donchian_v = donchian_df.to_numpy()

    last_signal_bar = -config.rebalance_days

    for t_idx in range(n_bars):
        signal_bar = (t_idx - last_signal_bar) >= config.rebalance_days
        if signal_bar:
            last_signal_bar = t_idx
        for i in range(n_assets):
            c_t = close_v[t_idx, i]
            atr_p = atr_prev_v[t_idx, i]
            don_p = donchian_v[t_idx, i]
            # If close is NaN (asset hasn't started trading) — flat.
            if not np.isfinite(c_t):
                if in_pos[i]:
                    # Force-close on missing data.
                    exit_arr[t_idx, i] = True
                    in_pos[i] = False
                    if seg_len[i] > 0:
                        hold_lengths.append(int(seg_len[i]))
                    seg_len[i] = 0
                continue

            if in_pos[i]:
                # Update trailing max with t-1's close (already known).
                # Then test exit on today's close vs trail − k × ATR_{t-1}.
                # We evaluate exits regardless of cadence (stop-loss is
                # always live per Penfold "cut losses short", p.68-69).
                if np.isfinite(atr_p) and atr_p > 0:
                    stop_level = trailing_max[i] - config.atr_multiplier * atr_p
                    if c_t < stop_level:
                        exit_arr[t_idx, i] = True
                        in_pos[i] = False
                        weight_arr[t_idx, i] = 0.0
                        if seg_len[i] > 0:
                            hold_lengths.append(int(seg_len[i]))
                        seg_len[i] = 0
                        # After exit, keep flat for the rest of this bar.
                        continue
                # Held — retain prior weight, update trailing max for
                # next bar's stop check.
                weight_arr[t_idx, i] = weight_arr[t_idx - 1, i] if t_idx > 0 else 0.0
                if c_t > trailing_max[i]:
                    trailing_max[i] = c_t
                seg_len[i] += 1
            else:
                # Flat — check entry only on signal bars.
                if not signal_bar:
                    weight_arr[t_idx, i] = 0.0
                    continue
                if (
                    np.isfinite(don_p)
                    and np.isfinite(atr_p)
                    and atr_p > 0
                    and c_t > don_p
                ):
                    # Long entry on close.
                    entry_arr[t_idx, i] = True
                    in_pos[i] = True
                    entry_price[i] = c_t
                    trailing_max[i] = c_t
                    seg_len[i] = 1
                    n_trades += 1
                    # Position size as fraction of equity:
                    # risk_per_position × 1.0 / (k × ATR / price)
                    # = risk_per_position × price / (k × ATR)
                    pos_w = (
                        config.risk_per_position
                        * c_t
                        / (config.atr_multiplier * atr_p)
                    )
                    weight_arr[t_idx, i] = pos_w
                else:
                    weight_arr[t_idx, i] = 0.0

    # --- Apply gross-exposure cap ---
    weights = pd.DataFrame(weight_arr, index=union_idx, columns=list(tickers))
    gross = weights.abs().sum(axis=1)
    scale = np.minimum(1.0, config.max_gross_exposure / gross.replace(0.0, np.nan))
    scale = scale.fillna(1.0)
    weights = weights.mul(scale, axis=0)

    # --- Returns with prev_weight × ret alignment ---
    prev_weights = weights.shift(1).fillna(0.0)
    per_asset = prev_weights * ret_df.fillna(0.0)
    gross_ret = per_asset.sum(axis=1)

    # --- Costs ---
    weight_changes = (weights - weights.shift(1).fillna(0.0)).abs()
    spread_drag = pd.Series(0.0, index=union_idx)
    for t_name in tickers:
        s_one_way = float(config.spread_one_way.get(t_name, 0.00025))
        spread_drag = spread_drag + weight_changes[t_name] * s_one_way
    commission_drag = weight_changes.sum(axis=1) * config.commission_round_trip
    long_exposure = prev_weights.clip(lower=0.0).sum(axis=1)
    swap_drag = long_exposure * abs(config.swap_daily_long)

    net_ret = gross_ret - spread_drag - commission_drag - swap_drag

    # Append any open segments at the end of the run.
    for i in range(n_assets):
        if in_pos[i] and seg_len[i] > 0:
            hold_lengths.append(int(seg_len[i]))

    entries_df = pd.DataFrame(entry_arr, index=union_idx, columns=list(tickers))
    exits_df = pd.DataFrame(exit_arr, index=union_idx, columns=list(tickers))

    return UniversalTrendResult(
        daily_returns=net_ret,
        gross_returns=gross_ret,
        weights=weights,
        entries=entries_df,
        exits=exits_df,
        hold_lengths=hold_lengths,
        cum_spread_pct=float(spread_drag.sum()),
        cum_commission_pct=float(commission_drag.sum()),
        cum_swap_pct=float(swap_drag.sum()),
        n_trades=int(n_trades),
        universe_tickers=tickers,
    )
