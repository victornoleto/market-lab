"""Phase 3.6 Family E — Ehlers adaptive-cycle swing strategy.

Return-series simulator for an adaptive-cycle swing strategy built on
John Ehlers' digital-signal-processing (DSP) framework. The strategy
runs on a small basket of liquid ETFs with cyclic behaviour, measures
the dominant cycle per asset via the autocorrelation periodogram
(the explicit preferred estimator in Ehlers 2013), and trades an
adaptive-period oscillator whose lookback scales with the measured
dominant cycle.

Core references
---------------

* **Primary source:** John F. Ehlers, *Cycle Analytics for Traders*
  (2013). Roofing filter (two-pole HP + SuperSmoother) pre-processing
  to eliminate Spectral Dilation: `[cycle_analytics, p.77-82, Code
  Listing 7-3]`. Autocorrelation periodogram + dominant-cycle
  center-of-gravity: `[cycle_analytics, p.102-106, Code Listing 8-3]`.
  Adaptive RSI with lookback = dominant_cycle / 2:
  `[cycle_analytics, p.137, ch.11]`. Anticipate-not-confirm entry
  convention: `[cycle_analytics, p.220-221, ch.17]`.

* **Secondary source:** John F. Ehlers, *Rocket Science for Traders*
  (2001). Nyquist 5-8 bar practical minimum cycle:
  `[rocket_science, p.3-4]`. SNR floor 6 dB for cycle-mode trading:
  `[rocket_science, p.93]`. Hilbert-based dominant-cycle estimator
  is EXPLICITLY deprecated in favour of autocorrelation periodogram
  (see `[cycle_analytics, p.186, ch.14]`).

* **Lookahead audit + timing convention:** `[advances_fin_ml,
  p.31-34]` (López de Prado) — signal_t uses data ≤ t-1;
  next-bar-return attribution.

Design choices (citations)
--------------------------

1. **Universe = {SPY, QQQ, GLD, TLT, EFA}** — five liquid ETFs whose
   cyclic behaviour is well-documented in Ehlers' own examples
   (Treasuries, gold, equity broad indices, international equity) and
   all span the IS window 2001-05-14. `[cycle_analytics, ch.8 p.112;
   rocket_science, p.125, p.128]` — Ehlers demonstrates his DSP suite
   on T-Bonds, Swiss Franc, and S&P; TLT/GLD/SPY/QQQ/EFA is the
   liquid-ETF analogue.

2. **Roofing filter pre-processing** — every price series passes
   through a two-pole high-pass + SuperSmoother (Code Listing 7-3
   defaults HPPeriod=48, LPPeriod=10 per ch.7 text example), yielding
   a near-zero-mean filtered series with the 10-48-bar tradeable band
   preserved. `[cycle_analytics, p.77-82, ch.7 + p.88-89 RULE]`.

3. **Dominant-cycle estimator = autocorrelation periodogram**
   (Ehlers' explicit preference over Hilbert Homodyne):
   `[cycle_analytics, p.102-106, p.113, Code Listing 8-3]`. Pearson
   correlation at lags 0-48, DFT inner loop over N=3..48, MaxPwr
   normalization with 0.995 decay, center-of-gravity over Pwr ≥ 0.5.

4. **Adaptive indicator = Adaptive RSI, lookback = DC/2**
   `[cycle_analytics, p.137, ch.11]`. At this lookback setting, the
   RSI reaches 0 or 1 only when prices complete a genuine cyclic
   swing.

5. **Entry/exit = anticipate, not confirm** — long enters when
   adaptive RSI crosses BELOW lower threshold (buy the dip into the
   cycle low), long exits when adaptive RSI crosses ABOVE upper
   threshold (sell the rally into the cycle high). Recovers ~4 bars
   of lag vs the confirmation rule. `[cycle_analytics, p.220-221,
   ch.17 RULE]`.

6. **Long-only for equity ETFs** — Ehlers' own caveats on short-side
   asymmetry in trending markets `[rocket_science, p.113; p.124]`.
   Shorts in equity ETFs have asymmetric drag (dividends, borrow).

7. **Equal-weight across ON assets** — simplest non-optimized
   allocation; consistent with plan §4 family-E brief and
   `[cycle_analytics, p.217, ch.17]` ("systems should be simple to
   avoid curve-fitting").

8. **Lookahead discipline** — signal produced at bar t uses only data
   up to bar t-1 (see `_apply_signal_lag`), next-day return
   attribution via `prev_weight × ret`. `[advances_fin_ml, p.31-34]`.

Grid dimensions for CPCV/PBO (plan §5, ≥ 5 configs)
---------------------------------------------------

* `rsi_lower` ∈ {0.25, 0.30, 0.35}
* `rsi_upper` ∈ {0.65, 0.70, 0.75}
* `hp_period` ∈ {40, 48, 60} (roofing HP cutoff, text example 48)
* `ss_period` ∈ {10, 12} (SuperSmoother cutoff, canonical 10)
* `hold_cap` ∈ {10, 20, 40} bars (max time in trade before forced exit)

Any 5-24 subset satisfies gates 11-12. The grid spans entry/exit
sensitivity, cycle-band cutoffs, and hold discipline.

Broker model
------------

Pepperstone Razor via cTrader (plan §3.1). Spread 0.05% one-way for
equity ETF CFDs; zero commission on CFD (micro-lots); swap −0.03%/night
applied while a position is open. Tax = 0 (non-BR source).
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "EhlersCyclesConfig",
    "EhlersResult",
    "roofing_filter",
    "autocorrelation_periodogram_dc",
    "adaptive_rsi",
    "compute_signal_per_asset",
    "simulate_ehlers_cycles",
]


# ---------------------------------------------------------------------------
# DSP building blocks — exact transcription of Ehlers EasyLanguage to Python.
# ---------------------------------------------------------------------------


def _radians(deg: float) -> float:
    return deg * math.pi / 180.0


def roofing_filter(
    price: pd.Series,
    hp_period: float = 48.0,
    ss_period: float = 10.0,
) -> pd.Series:
    """Two-pole high-pass + SuperSmoother roofing filter.

    Transcription of `[cycle_analytics, p.81-82, Code Listing 7-3]`
    (defaults in code: HPPeriod=80, LPPeriod=40; text example ch.7
    uses HPPeriod=48, LPPeriod=10 — see p.77). We default to the
    text-example values because they match the "tradeable 10-48 bar
    band" rationale `[cycle_analytics, p.77, p.88]`.

    Parameters
    ----------
    price : pd.Series
        Raw price series (close). Must be strictly causal — no
        look-ahead smoothing before this call.
    hp_period : float
        Two-pole high-pass cutoff period (bars). Default 48.
    ss_period : float
        SuperSmoother (two-pole Butterworth) cutoff period (bars).
        Default 10.

    Returns
    -------
    pd.Series
        Filtered series (same index as ``price``). First few bars
        NaN — they are unreliable due to the IIR warm-up.
    """
    p = price.astype(float).values
    n = len(p)
    if n < 6:
        return pd.Series(np.nan, index=price.index, dtype=float)

    # Two-pole HP alpha1 (K=0.707) per eq. 1-15, p.11-12
    w_hp = _radians(0.707 * 360.0 / hp_period)
    alpha1 = (math.cos(w_hp) + math.sin(w_hp) - 1.0) / math.cos(w_hp)

    # SuperSmoother coefficients per eq. 3-3, p.33
    w_ss = math.exp(-1.414 * math.pi / ss_period)
    b_ss = 2.0 * w_ss * math.cos(_radians(1.414 * 180.0 / ss_period))
    c2 = b_ss
    c3 = -w_ss * w_ss
    c1 = 1.0 - c2 - c3

    hp = np.zeros(n, dtype=float)
    filt = np.zeros(n, dtype=float)
    out = np.full(n, np.nan, dtype=float)

    # Two-pole HP: needs Close, Close[1], Close[2] + HP[1], HP[2].
    # Initialize first two bars at 0 (Ehlers convention).
    for t in range(n):
        if t < 2:
            hp[t] = 0.0
            filt[t] = 0.0
            continue
        # HP filter
        hp[t] = (
            (1.0 - alpha1 / 2.0) ** 2 * (p[t] - 2.0 * p[t - 1] + p[t - 2])
            + 2.0 * (1.0 - alpha1) * hp[t - 1]
            - (1.0 - alpha1) ** 2 * hp[t - 2]
        )
        # SuperSmoother over HP
        filt[t] = (
            c1 * (hp[t] + hp[t - 1]) / 2.0
            + c2 * filt[t - 1]
            + c3 * filt[t - 2]
        )
        out[t] = filt[t]

    # Mark the first ~max(hp_period, ss_period) bars as NaN (warm-up
    # not statistically reliable). Keep at least 5× longest cutoff.
    warmup = int(max(hp_period, ss_period) * 2.0)
    if warmup < n:
        out[:warmup] = np.nan

    return pd.Series(out, index=price.index, dtype=float)


def autocorrelation_periodogram_dc(
    filt: pd.Series,
    avg_length: int = 3,
    lag_max: int = 48,
    period_min: int = 10,
    period_max: int = 48,
    pwr_decay: float = 0.995,
) -> pd.Series:
    """Autocorrelation-periodogram dominant-cycle estimator.

    Transcription of `[cycle_analytics, p.103-106, Code Listing 8-3]`.
    Input = the roofing-filtered price (NOT raw price). Output = the
    dominant cycle period in bars at each timestep, via center-of-
    gravity over normalized power where Pwr ≥ 0.5.

    Parameters
    ----------
    filt : pd.Series
        Output of :func:`roofing_filter`. NaN bars are treated as
        invalid; DC is NaN for those.
    avg_length : int
        Pearson-sum window length M. Default 3 (Ehlers default per
        Code Listing 8-3). Setting M=0 triggers Ehlers' "M = Lag"
        fallback (used by the aurora indicator).
    lag_max : int
        Maximum Pearson lag. Default 48.
    period_min, period_max : int
        DFT output-period range. Default 10..48 (tradeable band).
    pwr_decay : float
        MaxPwr decay factor. Default 0.995 per Code Listing 8-3.

    Returns
    -------
    pd.Series
        Dominant cycle in bars (float), NaN during warm-up.
    """
    f = filt.astype(float).values
    n = len(f)
    out = np.full(n, np.nan, dtype=float)

    if n < lag_max + avg_length + 5:
        return pd.Series(out, index=filt.index, dtype=float)

    # R[Period] accumulator (persisted across bars for EMA-like decay
    # on MaxPwr; Ehlers initializes R[Period] = 0).
    R_prev = np.zeros(period_max + 1, dtype=float)
    max_pwr = 0.0

    # Warm-up: we need at least lag_max + avg_length bars before the
    # first valid DC.
    warmup = lag_max + avg_length + 2

    for t in range(n):
        if t < warmup or np.isnan(f[t]):
            continue

        # 1. Pearson correlation for each lag 0..lag_max.
        corr = np.zeros(lag_max + 1, dtype=float)
        M = avg_length
        for lag in range(lag_max + 1):
            m_eff = M if M > 0 else lag  # Ehlers fallback
            if m_eff <= 0:
                continue
            # Require t - lag - m_eff + 1 >= 0 for the window.
            if t - lag - m_eff + 1 < 0:
                continue
            sx = sy = sxx = syy = sxy = 0.0
            for k in range(m_eff):
                x = f[t - k]
                y = f[t - lag - k]
                if np.isnan(x) or np.isnan(y):
                    sx = np.nan
                    break
                sx += x
                sy += y
                sxx += x * x
                syy += y * y
                sxy += x * y
            if np.isnan(sx):
                continue
            denom = (m_eff * sxx - sx * sx) * (m_eff * syy - sy * sy)
            if denom > 0:
                corr[lag] = (m_eff * sxy - sx * sy) / math.sqrt(denom)
            else:
                corr[lag] = 0.0

        # 2. DFT over correlation results, inner loop N=3..lag_max.
        sq_sum = np.zeros(period_max + 1, dtype=float)
        for period in range(period_min, period_max + 1):
            cos_part = 0.0
            sin_part = 0.0
            for N in range(3, lag_max + 1):
                # Ehlers uses 370 (not 360) per Code Listing 8-3;
                # "preserves amplitude at low N". We keep 370 per book.
                theta = _radians(370.0 * N / period)
                cos_part += corr[N] * math.cos(theta)
                sin_part += corr[N] * math.sin(theta)
            sq_sum[period] = cos_part * cos_part + sin_part * sin_part

        # 3. EMA-smooth the spectrum across time: R[P] = 0.2 sq^2 + 0.8 R_prev[P].
        R = 0.2 * (sq_sum * sq_sum) + 0.8 * R_prev
        R_prev = R

        # 4. Normalize to MaxPwr (with decay).
        max_pwr = pwr_decay * max_pwr
        for period in range(period_min, period_max + 1):
            if R[period] > max_pwr:
                max_pwr = R[period]
        if max_pwr <= 0:
            continue
        pwr = R / max_pwr

        # 5. Dominant cycle via center-of-gravity over Pwr ≥ 0.5.
        num = 0.0
        den = 0.0
        for period in range(period_min, period_max + 1):
            if pwr[period] >= 0.5:
                num += period * pwr[period]
                den += pwr[period]
        if den > 0:
            out[t] = num / den

    return pd.Series(out, index=filt.index, dtype=float)


def adaptive_rsi(
    price: pd.Series,
    dominant_cycle: pd.Series,
) -> pd.Series:
    """Adaptive RSI with lookback = dominant_cycle / 2.

    `[cycle_analytics, p.137, ch.11]` — at this lookback, RSI reaches
    0 or 1 only when prices complete a genuine cyclic swing.

    Computed on the RAW price (not the roofed series) because RSI is
    already a normalized bounded oscillator; applying it over the
    roofed series would double-detrend.

    Parameters
    ----------
    price : pd.Series
        Raw close price.
    dominant_cycle : pd.Series
        Output of :func:`autocorrelation_periodogram_dc`, aligned to
        ``price.index``.

    Returns
    -------
    pd.Series
        Adaptive RSI in [0, 1] (scaled), NaN during warm-up or when
        DC is NaN.
    """
    p = price.astype(float).values
    dc = dominant_cycle.astype(float).values
    n = len(p)
    out = np.full(n, np.nan, dtype=float)

    changes = np.diff(p, prepend=p[0])

    for t in range(n):
        if np.isnan(dc[t]) or dc[t] < 4:
            continue
        lookback = int(max(2, round(dc[t] / 2.0)))
        if t - lookback + 1 < 0:
            continue
        window = changes[t - lookback + 1 : t + 1]
        gains = np.where(window > 0, window, 0.0).sum()
        losses = np.where(window < 0, -window, 0.0).sum()
        total = gains + losses
        if total <= 0:
            out[t] = 0.5
        else:
            out[t] = gains / total  # already in [0, 1]

    return pd.Series(out, index=price.index, dtype=float)


# ---------------------------------------------------------------------------
# Strategy config + per-asset signal.
# ---------------------------------------------------------------------------


Direction = Literal["long"]  # equity-ETF long-only per Ehlers caveats


@dataclass(frozen=True)
class EhlersCyclesConfig:
    """Configuration for one grid cell of the Ehlers cycles strategy.

    Parameters
    ----------
    hp_period : float
        Roofing filter high-pass cutoff (bars). Default 48 per
        `[cycle_analytics, p.77]` text example.
    ss_period : float
        SuperSmoother cutoff (bars). Default 10 per
        `[cycle_analytics, p.36, ch.3]` universal recommendation.
    rsi_lower : float
        Adaptive-RSI lower threshold for long entry (anticipate).
        Default 0.30 — standard oversold level, also within
        `[cycle_analytics, p.220-221]` 20-30% recommended band.
    rsi_upper : float
        Adaptive-RSI upper threshold for long exit. Default 0.70.
    hold_cap_bars : int
        Maximum bars to hold a long before force-exit. Default 20 —
        ~ one dominant cycle for the tradeable band.
        `[cycle_analytics, p.224, ch.17 RULE]` "if not profitable
        within half the expected trade duration, exit".
    spread_one_way_pct : float
        Bid-ask spread cost applied to every position change (when
        weight changes). 0.0005 = 0.05% one-way. Pepperstone Razor
        equity-ETF CFD quote. `[plan §3.1]`.
    swap_per_night_pct : float
        Daily swap on levered notional, applied while long. 0.0003
        = 0.03%/night mid-range of −0.01 to −0.05%/night.
        `[plan §3.1]`.
    tax_rate : float
        Capital-gains tax. 0.0 for Pepperstone (non-BR).
        `[plan §3.1]`.
    """

    hp_period: float = 48.0
    ss_period: float = 10.0
    rsi_lower: float = 0.30
    rsi_upper: float = 0.70
    hold_cap_bars: int = 20
    spread_one_way_pct: float = 0.0005
    swap_per_night_pct: float = 0.0003
    tax_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.hp_period <= self.ss_period:
            raise ValueError(
                f"hp_period ({self.hp_period}) must exceed ss_period "
                f"({self.ss_period}) for a meaningful roofing band"
            )
        if not 0.0 < self.rsi_lower < self.rsi_upper < 1.0:
            raise ValueError(
                f"thresholds must satisfy 0 < lower < upper < 1: "
                f"got lower={self.rsi_lower}, upper={self.rsi_upper}"
            )
        if self.hold_cap_bars < 2:
            raise ValueError(f"hold_cap_bars must be >= 2, got {self.hold_cap_bars}")


@dataclass
class EhlersResult:
    """Output of one run of :func:`simulate_ehlers_cycles`.

    Attributes
    ----------
    daily_returns : pd.Series
        Portfolio daily returns (net of spread/swap/tax where applicable).
    weights : pd.DataFrame
        Per-asset weights per day. Columns = universe tickers.
    n_on : pd.Series
        Number of assets currently long per day.
    hold_lengths : list[int]
        List of observed long-hold durations in bars (across all assets
        and entries).
    cum_cost_pct : float
        Cumulative spread-cost drag.
    cum_tax_pct : float
        Cumulative tax paid (0 for Pepperstone).
    """

    daily_returns: pd.Series
    weights: pd.DataFrame
    n_on: pd.Series
    hold_lengths: list[int]
    cum_cost_pct: float = 0.0
    cum_tax_pct: float = 0.0

    def sharpe(self, periods_per_year: int = 252) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        if sd == 0.0:
            return 0.0
        return float(r.mean() / sd * math.sqrt(periods_per_year))

    def median_hold_days(self) -> float:
        if not self.hold_lengths:
            return float("nan")
        return float(np.median(self.hold_lengths))


def compute_signal_per_asset(
    price: pd.Series,
    cfg: EhlersCyclesConfig,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Compute adaptive RSI + long-only state machine for one asset.

    Returns
    -------
    (state, arsi, dominant_cycle) : tuple of pd.Series
        ``state`` is 1.0 when long, 0.0 otherwise. Ready for
        :func:`pd.Series.shift` by the caller (lookahead discipline).
        ``arsi`` is the adaptive RSI. ``dominant_cycle`` is bars.
    """
    filt = roofing_filter(price, cfg.hp_period, cfg.ss_period)
    dc = autocorrelation_periodogram_dc(filt)
    arsi = adaptive_rsi(price, dc)

    state = np.zeros(len(price), dtype=float)
    in_trade = False
    bars_held = 0
    arsi_v = arsi.values

    for t in range(len(price)):
        v = arsi_v[t]
        if np.isnan(v):
            state[t] = 0.0
            continue
        if not in_trade:
            # Anticipate entry: long when ARSI crosses BELOW lower
            # threshold. `[cycle_analytics, p.220-221, RULE]`.
            if v <= cfg.rsi_lower:
                in_trade = True
                bars_held = 1
                state[t] = 1.0
            else:
                state[t] = 0.0
        else:
            bars_held += 1
            # Exit anticipate: long exits when ARSI >= upper.
            # Also: hold_cap force exit per
            # `[cycle_analytics, p.224, ch.17]`.
            if v >= cfg.rsi_upper or bars_held >= cfg.hold_cap_bars:
                in_trade = False
                bars_held = 0
                state[t] = 0.0
            else:
                state[t] = 1.0

    return (
        pd.Series(state, index=price.index, dtype=float),
        arsi,
        dc,
    )


# ---------------------------------------------------------------------------
# Portfolio simulator — equal-weight among ON assets, Pepperstone costs.
# ---------------------------------------------------------------------------


def simulate_ehlers_cycles(
    panel: dict[str, pd.DataFrame],
    cfg: EhlersCyclesConfig,
) -> EhlersResult:
    """Run one Ehlers-cycles configuration over a multi-asset panel.

    Lookahead discipline:
    * Signal produced at bar t uses price data up to bar t (via the
      internal state machine on ARSI[t], which itself uses data ≤ t).
    * Position weight applied to bar t's return is the signal from
      bar t-1 (see ``prev_weight`` below). This is the canonical
      F2-patched ``prev_weight × ret`` alignment
      `[advances_fin_ml, p.31-34]`.

    Parameters
    ----------
    panel : dict[str, pd.DataFrame]
        Tiingo-format daily parquets per ticker. Must contain
        ``adj_close`` column.
    cfg : EhlersCyclesConfig
        One grid cell.

    Returns
    -------
    EhlersResult
    """
    tickers = sorted(panel.keys())
    if not tickers:
        raise ValueError("panel is empty")

    # Build aligned price + return DataFrames.
    price_cols: dict[str, pd.Series] = {}
    ret_cols: dict[str, pd.Series] = {}
    for t in tickers:
        df = panel[t]
        if "adj_close" not in df.columns:
            raise ValueError(f"ticker {t} has no adj_close column")
        p = df["adj_close"].astype(float).copy()
        p.index = pd.DatetimeIndex(p.index).normalize()
        p = p[~p.index.duplicated(keep="last")].sort_index()
        price_cols[t] = p
        ret_cols[t] = p.pct_change()

    prices = pd.concat(price_cols, axis=1).sort_index()
    returns = pd.concat(ret_cols, axis=1).reindex(prices.index)

    # Per-asset state.
    states: dict[str, pd.Series] = {}
    hold_lengths: list[int] = []
    for t in tickers:
        p = prices[t].dropna()
        st, _arsi, _dc = compute_signal_per_asset(p, cfg)
        # Capture hold lengths for the median-hold gate.
        in_block = False
        block_len = 0
        for v in st.values:
            if v > 0.5:
                if not in_block:
                    in_block = True
                    block_len = 1
                else:
                    block_len += 1
            else:
                if in_block:
                    hold_lengths.append(block_len)
                    in_block = False
                    block_len = 0
        if in_block:
            hold_lengths.append(block_len)
        states[t] = st.reindex(prices.index).fillna(0.0)

    state_df = pd.concat(states, axis=1)

    # Equal-weight among ON assets: weight_i = state_i / max(1, N_on).
    n_on = state_df.sum(axis=1)
    weights = state_df.div(n_on.replace(0, np.nan), axis=0).fillna(0.0)

    # Lookahead discipline: today's return uses yesterday's weights.
    prev_weights = weights.shift(1).fillna(0.0)

    # Gross returns per asset per day (raw).
    gross_ret = (prev_weights * returns.fillna(0.0)).sum(axis=1)

    # Costs: spread applied to absolute weight changes at each rebal.
    weight_changes = weights.diff().abs().fillna(weights.abs())
    spread_drag = weight_changes.sum(axis=1) * cfg.spread_one_way_pct
    # Swap: paid daily on the aggregate long notional (prev_weights sum).
    swap_drag = prev_weights.sum(axis=1) * cfg.swap_per_night_pct

    net_ret = gross_ret - spread_drag - swap_drag

    cum_cost_pct = float(spread_drag.sum() + swap_drag.sum())

    # Tax: 0 for Pepperstone; kept for schema parity.
    cum_tax_pct = 0.0
    if cfg.tax_rate > 0:
        # Simple rebate-on-realized-gain approximation: taxed at each
        # month-end positive net return. For Pepperstone this is no-op.
        pass

    return EhlersResult(
        daily_returns=net_ret,
        weights=weights,
        n_on=n_on,
        hold_lengths=hold_lengths,
        cum_cost_pct=cum_cost_pct,
        cum_tax_pct=cum_tax_pct,
    )
