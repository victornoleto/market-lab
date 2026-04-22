"""Phase 3.6 Family I — Statistically-sound indicator screening.

Clean return-series strategy for a swing-trade ensemble built from
indicators that survive a rigorous hypothesis-test screen on IS data
only. Horizon: median hold 5-15 trading days (plan §5 gate 7 ≥ 5d).

Design rationale (Masters / Aronson canon)
------------------------------------------

Unlike Families A-C (which commit to a specific mechanism), Family I's
core premise is the **screening protocol itself**: we enumerate a small
pool of well-known indicators, evaluate each one's predictive edge on
IS with a permutation test, apply multiple-testing correction
(Bonferroni) at ``p < 0.001`` (Masters' canonical threshold per
``[stat_sound_indicators, p.170, p.174]``) and form an equal-weight
ensemble only from **survivors**. If ≤ 0 survive, the verdict is
``FAIL-structural`` — a scientifically informative result, not a bug.

The discipline principle: **screening happens on IS only**. OOS and
FWD use the already-selected ensemble with zero peeking. This is the
operational form of Aronson's selection-bias control
``[stat_sound_indicators, p.306]`` and Masters' walkforward/OOS purity
``[testing_tuning, p.143-144, p.148-149]``.

Universe
--------

Five broad, liquid, long-history ETFs:

* ``SPY`` — US large-cap (equity risk premium)
* ``QQQ`` — US tech concentration (growth / equity)
* ``GLD`` — gold (inflation hedge, uncorrelated)
* ``TLT`` — long-duration Treasuries (duration / safe-haven)
* ``EEM`` — emerging-market equities (additional equity diversifier)

This matches Masters' focus on broad market indices
``[stat_sound_indicators, p.1, p.108]`` and overlaps zero with the
six rejected V2 leads (TSMOM, Gayed EMA, AFML, Carver RP, Kalman,
Donchian-55d vol breakout).

Candidate indicator pool
------------------------

All indicators parametrized so each produces a single long/flat signal
per asset per day; the strategy then holds equal-weight positions
across signalled assets.

1. **RSI(14) oversold-entry MR** — Enter long when RSI < 30; exit when
   RSI > 70 or after 10 days. RSI definition per
   ``[evidence_based_ta, p.429]``. Oversold thresholds are canonical
   Wilder values that have been tested repeatedly; the test determines
   whether they still carry edge.
2. **MACD histogram zero-cross momentum** — Enter long when
   ``MACD - signal`` crosses above zero; exit when it crosses below.
   MACD(12, 26, 9) per ``[evidence_based_ta, p.429]``.
3. **Connors 2-period RSI MR** — Enter long when RSI(2) < 10; exit when
   RSI(2) > 70 OR close > 5d-high OR 10 days elapsed. Documented
   short-term MR pattern used historically by Connors; selected to
   test MR regime specifically on liquid ETFs
   ``[testing_tuning, p.43]`` (linear-model-with-clean-indicators
   design principle).
4. **Donchian-20 breakout** — Enter long when close > prior 20-day
   high; exit on close < prior 10-day low. Parametrization matches
   Aronson's Channel Breakout Operator (CBO) with lookback 18-27 band
   ``[evidence_based_ta, p.397, p.398]``. EXPLICITLY different from
   V2-L6 (which used 55-day Donchian for vol-breakout, rejected).
5. **5-day z-score MR** — Enter long when
   ``(close - SMA_5)/std_5 < -1.5``; exit when z > 0 or after 5 days.
   Short-term MR via stationarity-induced z-score
   ``[stat_sound_indicators, p.87-89]`` (CENTER/SCALE/NORMALIZE
   operators).
6. **Bollinger band MR (2σ)** — Enter long when close touches lower
   band (2σ, 20-day); exit when close crosses middle band or after
   15 days. Same stationarity logic as 5-day z-score, different
   parameters; selected as a representative BB-MR variant per
   ``[testing_tuning, p.28]`` (extreme stationarity induction).
7. **200-day SMA trend** — Long when close > SMA(200); flat
   otherwise. Classical trend regime filter per
   ``[evidence_based_ta, p.398]`` (MLM Index 12-month MA analog).
8. **Channel normalization (stochastic K at 20 days) MR** — Compute
   CN = 100 * (close - min_20) / (max_20 - min_20); long when
   CN < 20, exit when CN > 80 or after 10 days
   ``[evidence_based_ta, p.402]`` (CN operator definition).

Screening protocol (IS-only)
----------------------------

For each indicator-config ``i``:

1. Generate daily signal ``s_i[t] ∈ {0, 1}`` per asset for the IS window
   (2001-05-14 → 2017-12-31).
2. Compute portfolio daily return:
   ``r_i[t+1] = (1/n_active) Σ s_i[a, t] · r_asset[a, t+1]``
   (shifted, long-only, equal-weight across assets whose signal is
   currently on; flat when no signal; ``[advances_fin_ml, p.31-34]``
   lookahead-free timing).
3. Compute periodic Sharpe ``SR_i_obs = mean / std`` (no annualization
   needed for permutation comparison).
4. Run **MCPT permutation test** ``[evidence_based_ta, p.255-256,
   p.341-344]``, ``[stat_sound_indicators, p.299-306]``:
   - For ``N_perm = 500`` reps: permute ``r_asset`` WITHIN the IS
     window (shuffle the time axis of each asset's daily returns
     independently; preserves marginal distribution, destroys serial
     structure and cross-asset co-movement — this is the canonical
     "simple-market permutation" ``[testing_tuning, p.327-328]``).
   - Recompute signals on the permuted bars (signals must be
     recomputable — which is true for all 8 indicators since they
     are pure functions of the shuffled close/high/low/volume).
   - Record ``SR_i_perm[k]``.
   - Raw p-value: ``p_raw = (1 + #{k: SR_perm[k] >= SR_obs}) / N_perm``
     ``[stat_sound_indicators, p.301]``.
5. **Bonferroni correction** across the pool of ``M = 8``
   ``[stat_sound_indicators, p.170, p.174]``: corrected threshold
   ``α_corr = α / M = 0.001 / 8 = 1.25e-4``. Equivalently, a candidate
   passes if ``p_raw < α_corr``, i.e. ``p_corrected = min(1, M * p_raw)
   < 0.001``.
6. **Survivors** form the ensemble. Zero survivors → FAIL-structural.

Ensemble construction
---------------------

If ≥ 1 indicator survives:

* Aggregate per-day per-asset signal ``S[a, t] = (1/k) Σ_{i∈survivors}
  s_i[a, t]`` ∈ [0, 1] — fractional allocation.
* Portfolio daily return:
  ``r_ens[t+1] = Σ_a S[a, t] · r_asset[a, t+1] / max(1, Σ_a S[a, t])``
  (normalize so gross notional ≤ 1 × equity; no leverage).
* Costs: Inter model (plan §3.2) — 0.05% one-way spread on net
  turnover, 15% BR CG tax applied monthly on positive realized gain
  (approximated as 15% on positive daily P&L scaled to monthly bucket
  for simplicity matching Family B runner).

Citations
---------

* Masters' 0.001 p-value threshold for accepted indicators:
  ``[stat_sound_indicators, p.170, p.174]``.
* MCPT canonical protocol:
  ``[stat_sound_indicators, p.299-306]``,
  ``[evidence_based_ta, p.255-256, p.341-344]``,
  ``[testing_tuning, p.310-319]``.
* Bonferroni as the simplest multiple-testing correction (inferior to
  Romano-Wolf but acceptable when pool size ≤ 10):
  ``[stat_sound_indicators, p.170]``.
* Lookahead-free ``prev_weight × next_ret`` alignment:
  ``[advances_fin_ml, p.31-34]``.
* IS-only screening; OOS purity:
  ``[stat_sound_indicators, p.306]``,
  ``[testing_tuning, p.143-144]``.
* Selection bias hazard (why correction is mandatory):
  ``[stat_sound_indicators, p.170, p.306]``,
  ``[evidence_based_ta, p.283-291]``.
* Universe (broad indices):
  ``[stat_sound_indicators, p.1, p.108]``.
* Inter broker cost model: plan §3.2.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Mapping

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "IStatSoundConfig",
    "IStatSoundResult",
    "INDICATOR_FUNCS",
    "compute_signal",
    "simulate_ensemble",
    "permutation_pvalue",
    "screen_indicators",
]

TRADING_DAYS_PER_YEAR = 252


# ---------------------------------------------------------------------------
# Config / Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IStatSoundConfig:
    """Immutable configuration for one stat-sound-indicator ensemble run.

    Parameters
    ----------
    universe
        Ordered ETF ticker tuple. Default (SPY, QQQ, GLD, TLT, EEM)
        per ``[stat_sound_indicators, p.1, p.108]`` — broad indices.
    pool
        Ordered tuple of candidate indicator slugs. Default = full
        8-indicator pool (see module docstring).
    screen_alpha
        Family-wise screening threshold (uncorrected). Default 0.001
        per ``[stat_sound_indicators, p.170, p.174]``.
    bonferroni_M
        Divisor for Bonferroni correction. If ``None``, defaults to
        ``len(pool)`` — the canonical family-wise correction.
    n_permutations
        Number of permutation reps per indicator. Default 500 per
        ``[stat_sound_indicators, p.170]`` (≥ 100 minimum, 1000
        preferred; 500 is the runtime compromise for 8 × 500 reps).
    spread_one_way_pct
        One-way spread at rebalance / signal change (0.05% per side
        plan §3.2 Inter).
    tax_rate
        Capital-gains tax on positive monthly realized P&L (15% BR).
    seed
        RNG seed for reproducibility of permutations.
    """

    universe: tuple[str, ...] = ("SPY", "QQQ", "GLD", "TLT", "EEM")
    pool: tuple[str, ...] = (
        "rsi14_mr",
        "macd_hist_cross",
        "connors_rsi2_mr",
        "donchian20_breakout",
        "zscore5_mr",
        "bollinger2_mr",
        "sma200_trend",
        "cn20_mr",
    )
    screen_alpha: float = 0.001
    bonferroni_M: int | None = None
    n_permutations: int = 500
    spread_one_way_pct: float = 0.0005
    tax_rate: float = 0.15
    seed: int = 42

    def __post_init__(self) -> None:
        if len(self.universe) < 1:
            raise ValueError("universe must be non-empty")
        if len(self.pool) < 1:
            raise ValueError("pool must be non-empty")
        if not 0 < self.screen_alpha < 1:
            raise ValueError(f"screen_alpha must be in (0,1), got {self.screen_alpha}")
        if self.n_permutations < 50:
            raise ValueError(f"n_permutations must be >= 50, got {self.n_permutations}")
        if self.spread_one_way_pct < 0:
            raise ValueError("spread_one_way_pct must be >= 0")
        if not 0 <= self.tax_rate < 0.5:
            raise ValueError("tax_rate must be in [0, 0.5)")

    @property
    def effective_M(self) -> int:
        return self.bonferroni_M if self.bonferroni_M is not None else len(self.pool)


@dataclass
class IStatSoundResult:
    """End-to-end simulation output."""

    equity: pd.Series
    daily_returns: pd.Series
    daily_returns_gross: pd.Series
    per_indicator_signals: dict[str, pd.DataFrame]  # slug -> (T, n_assets) 0/1
    ensemble_weights: pd.DataFrame  # (T, n_assets), sums to ≤ 1
    survivors: list[str]
    screening_rows: list[dict]  # one per candidate: slug, sr_obs, p_raw, p_corr, survive
    cum_cost: float = 0.0
    cum_tax: float = 0.0
    config: IStatSoundConfig | None = None
    median_hold: float = float("nan")
    hold_lengths: list[int] = field(default_factory=list)

    def sharpe(self, periods: int = TRADING_DAYS_PER_YEAR) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        if sd == 0.0:
            return 0.0
        return float(r.mean() / sd * np.sqrt(periods))

    def cagr(self, periods: int = TRADING_DAYS_PER_YEAR) -> float:
        eq = self.equity.dropna()
        if len(eq) < 2:
            return 0.0
        years = (len(eq) - 1) / periods
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


# ---------------------------------------------------------------------------
# Indicator signal generators
# ---------------------------------------------------------------------------
#
# Each generator takes a DataFrame with columns {close, high, low} indexed
# by date, returns a Series of 0/1 signals aligned with the index, with
# the semantics: signal[t] = 1 means "hold long for the day t+1 return".
# Signals are strictly computable from information available on day t.


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder RSI. ``[evidence_based_ta, p.429]``."""
    delta = close.diff()
    up = delta.clip(lower=0.0)
    dn = -delta.clip(upper=0.0)
    # Wilder smoothing ≡ EMA with alpha = 1/period
    roll_up = up.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    roll_dn = dn.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    rs = roll_up / roll_dn.replace(0.0, np.nan)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    return rsi


def sig_rsi14_mr(df: pd.DataFrame) -> pd.Series:
    """RSI(14) MR: enter long when RSI < 30, exit when RSI > 70 or 10d.

    ``[evidence_based_ta, p.429]`` — RSI as canonical TA indicator.
    """
    rsi_arr = _rsi(df["close"], 14).to_numpy(dtype=float)
    n = len(rsi_arr)
    out = np.zeros(n, dtype=np.int8)
    holding = 0
    days_held = 0
    for i in range(n):
        r = rsi_arr[i]
        if holding == 0:
            if np.isfinite(r) and r < 30:
                holding = 1
                days_held = 1
        else:
            days_held += 1
            if np.isfinite(r) and (r > 70 or days_held >= 10):
                holding = 0
                days_held = 0
        out[i] = holding
    return pd.Series(out, index=df.index)


def sig_macd_hist_cross(df: pd.DataFrame) -> pd.Series:
    """MACD(12,26,9) histogram zero-cross momentum.

    Long when ``hist = MACD - signal > 0``; flat when ≤ 0.
    ``[evidence_based_ta, p.429]``.
    """
    close = df["close"]
    ema12 = close.ewm(span=12, min_periods=12, adjust=False).mean()
    ema26 = close.ewm(span=26, min_periods=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, min_periods=9, adjust=False).mean()
    hist = macd - signal
    sig = (hist > 0).astype(int)
    # Mask warmup (first 34 bars of EMA26+signal)
    sig.iloc[:35] = 0
    return sig


def sig_connors_rsi2_mr(df: pd.DataFrame) -> pd.Series:
    """Connors 2-period RSI MR.

    Long when RSI(2) < 10; exit when RSI(2) > 70 or 10d or close > 5d-high.
    ``[testing_tuning, p.43]`` (linear-indicator design principle).
    """
    close = df["close"]
    rsi_arr = _rsi(close, 2).to_numpy(dtype=float)
    high5 = close.rolling(5, min_periods=5).max().shift(1).to_numpy(dtype=float)
    close_arr = close.to_numpy(dtype=float)
    n = len(close_arr)
    out = np.zeros(n, dtype=np.int8)
    holding = 0
    days_held = 0
    for i in range(n):
        r = rsi_arr[i]
        h5 = high5[i]
        c = close_arr[i]
        if holding == 0:
            if np.isfinite(r) and r < 10:
                holding = 1
                days_held = 1
        else:
            days_held += 1
            exit_cond = False
            if np.isfinite(r) and r > 70:
                exit_cond = True
            if np.isfinite(h5) and c > h5:
                exit_cond = True
            if days_held >= 10:
                exit_cond = True
            if exit_cond:
                holding = 0
                days_held = 0
        out[i] = holding
    return pd.Series(out, index=df.index)


def sig_donchian20_breakout(df: pd.DataFrame) -> pd.Series:
    """Donchian 20-day breakout. Long on close > prior 20d high.

    Exit on close < prior 10d low.
    ``[evidence_based_ta, p.397, p.398]`` — Channel Breakout Operator.
    EXPLICITLY 20-day (not 55-day V2-L6 rejected variant).
    """
    close = df["close"]
    hi20 = close.rolling(20, min_periods=20).max().shift(1).to_numpy(dtype=float)
    lo10 = close.rolling(10, min_periods=10).min().shift(1).to_numpy(dtype=float)
    close_arr = close.to_numpy(dtype=float)
    n = len(close_arr)
    out = np.zeros(n, dtype=np.int8)
    holding = 0
    for i in range(n):
        c = close_arr[i]
        h = hi20[i]
        l = lo10[i]
        if holding == 0:
            if np.isfinite(h) and c > h:
                holding = 1
        else:
            if np.isfinite(l) and c < l:
                holding = 0
        out[i] = holding
    return pd.Series(out, index=df.index)


def sig_zscore5_mr(df: pd.DataFrame) -> pd.Series:
    """5-day z-score MR.

    z_t = (close_t - SMA5_t) / std5_t (both computed from prior days).
    Long when z < -1.5; exit when z > 0 or 5d.
    ``[stat_sound_indicators, p.87-89]`` — CENTER/SCALE operators.
    """
    close = df["close"]
    sma5 = close.rolling(5, min_periods=5).mean()
    std5 = close.rolling(5, min_periods=5).std(ddof=1)
    z_arr = ((close - sma5) / std5.replace(0, np.nan)).to_numpy(dtype=float)
    n = len(z_arr)
    out = np.zeros(n, dtype=np.int8)
    holding = 0
    days_held = 0
    for i in range(n):
        zz = z_arr[i]
        if holding == 0:
            if np.isfinite(zz) and zz < -1.5:
                holding = 1
                days_held = 1
        else:
            days_held += 1
            if (np.isfinite(zz) and zz > 0) or days_held >= 5:
                holding = 0
                days_held = 0
        out[i] = holding
    return pd.Series(out, index=df.index)


def sig_bollinger2_mr(df: pd.DataFrame) -> pd.Series:
    """Bollinger band MR, 2σ, 20-day.

    Enter long when close ≤ lower band; exit when close ≥ mid band
    or 15d. ``[testing_tuning, p.28]`` (extreme stationarity via z-score).
    """
    close = df["close"]
    sma20 = close.rolling(20, min_periods=20).mean()
    std20 = close.rolling(20, min_periods=20).std(ddof=1)
    lower = (sma20 - 2.0 * std20).to_numpy(dtype=float)
    mid_arr = sma20.to_numpy(dtype=float)
    close_arr = close.to_numpy(dtype=float)
    n = len(close_arr)
    out = np.zeros(n, dtype=np.int8)
    holding = 0
    days_held = 0
    for i in range(n):
        c = close_arr[i]
        mid = mid_arr[i]
        lo = lower[i]
        if holding == 0:
            if np.isfinite(lo) and c <= lo:
                holding = 1
                days_held = 1
        else:
            days_held += 1
            if (np.isfinite(mid) and c >= mid) or days_held >= 15:
                holding = 0
                days_held = 0
        out[i] = holding
    return pd.Series(out, index=df.index)


def sig_sma200_trend(df: pd.DataFrame) -> pd.Series:
    """200-day SMA trend filter. Long when close > SMA(200).

    ``[evidence_based_ta, p.398]`` (MLM 12-month MA analog).
    """
    close = df["close"]
    sma200 = close.rolling(200, min_periods=200).mean()
    sig = (close > sma200).astype(int)
    sig.iloc[:200] = 0
    return sig


def sig_cn20_mr(df: pd.DataFrame) -> pd.Series:
    """Channel Normalization (stochastic K) 20-day MR.

    CN = 100 * (close - min20) / (max20 - min20).
    Long when CN < 20; exit when CN > 80 or 10d.
    ``[evidence_based_ta, p.402]``.
    """
    close = df["close"]
    hi20 = close.rolling(20, min_periods=20).max()
    lo20 = close.rolling(20, min_periods=20).min()
    cn_arr = (100.0 * (close - lo20) / (hi20 - lo20).replace(0, np.nan)).to_numpy(dtype=float)
    n = len(cn_arr)
    out = np.zeros(n, dtype=np.int8)
    holding = 0
    days_held = 0
    for i in range(n):
        c = cn_arr[i]
        if holding == 0:
            if np.isfinite(c) and c < 20:
                holding = 1
                days_held = 1
        else:
            days_held += 1
            if (np.isfinite(c) and c > 80) or days_held >= 10:
                holding = 0
                days_held = 0
        out[i] = holding
    return pd.Series(out, index=df.index)


INDICATOR_FUNCS: dict[str, Callable[[pd.DataFrame], pd.Series]] = {
    "rsi14_mr": sig_rsi14_mr,
    "macd_hist_cross": sig_macd_hist_cross,
    "connors_rsi2_mr": sig_connors_rsi2_mr,
    "donchian20_breakout": sig_donchian20_breakout,
    "zscore5_mr": sig_zscore5_mr,
    "bollinger2_mr": sig_bollinger2_mr,
    "sma200_trend": sig_sma200_trend,
    "cn20_mr": sig_cn20_mr,
}


def compute_signal(
    slug: str, data_panel: Mapping[str, pd.DataFrame]
) -> pd.DataFrame:
    """Compute per-asset signal panel for one indicator slug.

    Parameters
    ----------
    slug
        Key of ``INDICATOR_FUNCS``.
    data_panel
        Mapping ``ticker → DataFrame[close, high, low]``, all indexed
        on the same dates.

    Returns
    -------
    DataFrame with shape (T, n_assets), columns = tickers, values ∈ {0, 1}.
    """
    if slug not in INDICATOR_FUNCS:
        raise KeyError(f"Unknown indicator slug {slug!r}; known: {list(INDICATOR_FUNCS)}")
    func = INDICATOR_FUNCS[slug]
    sigs = {}
    for ticker, df in data_panel.items():
        sigs[ticker] = func(df)
    return pd.DataFrame(sigs)


# ---------------------------------------------------------------------------
# Ensemble simulation (clean return-series, long-only, equal-weight active)
# ---------------------------------------------------------------------------


def _portfolio_daily_returns(
    signals: pd.DataFrame,
    asset_returns: pd.DataFrame,
) -> pd.Series:
    """Pure gross daily-return computation with prev-day signals.

    ``weights[t] = signals[t-1] / max(1, Σ signals[t-1])``,
    ``r_p[t] = Σ weights[t] · r_asset[t]``.

    Long-only, no leverage, equal-weight across currently-active signals.
    ``[advances_fin_ml, p.31-34]`` (prev-weight × current-return).
    """
    prev_sig = signals.shift(1).fillna(0.0)
    # Normalize so total weight ≤ 1 (equal-split across active).
    total = prev_sig.sum(axis=1)
    denom = total.where(total > 0, 1.0)
    weights = prev_sig.div(denom, axis=0)
    # When total==0 (no active), weights are all zero — cash, r_p=0.
    r_p = (weights * asset_returns).sum(axis=1)
    return r_p


def simulate_ensemble(
    data_panel: Mapping[str, pd.DataFrame],
    asset_returns: pd.DataFrame,
    survivors: list[str],
    config: IStatSoundConfig,
) -> IStatSoundResult:
    """Run the surviving-indicator ensemble end-to-end (net of costs/tax).

    If ``survivors`` is empty, returns a flat (all-zero return) result
    — this is the FAIL-structural case.

    Parameters
    ----------
    data_panel
        Per-ticker DataFrame (close/high/low). Used to regenerate
        signals (screens of survivors).
    asset_returns
        DataFrame (T, n_assets) of daily asset returns aligned with
        data_panel.
    survivors
        List of indicator slugs that passed the IS screening.
    config
        Strategy config.
    """
    per_indicator: dict[str, pd.DataFrame] = {}
    if not survivors:
        idx = asset_returns.index
        return IStatSoundResult(
            equity=pd.Series(1.0, index=idx),
            daily_returns=pd.Series(0.0, index=idx),
            daily_returns_gross=pd.Series(0.0, index=idx),
            per_indicator_signals={},
            ensemble_weights=pd.DataFrame(0.0, index=idx, columns=asset_returns.columns),
            survivors=[],
            screening_rows=[],
            config=config,
        )

    # Per-indicator signal panel
    for slug in survivors:
        per_indicator[slug] = compute_signal(slug, data_panel)

    # Ensemble signal = mean of survivors' per-asset signals.
    # (Fractional ∈ [0, 1]; each asset held proportionally to how many
    # indicators fired.)
    stacked = np.stack([per_indicator[s].reindex(asset_returns.index).fillna(0.0).values
                        for s in survivors], axis=0)
    ens_sig = pd.DataFrame(stacked.mean(axis=0),
                           index=asset_returns.index,
                           columns=asset_returns.columns)

    # Normalize ensemble weights so Σ ≤ 1.
    prev_sig = ens_sig.shift(1).fillna(0.0)
    total = prev_sig.sum(axis=1)
    denom = total.where(total > 0, 1.0)
    scale = (1.0 / denom).where(total > 1.0, 1.0)  # cap Σ ≤ 1
    ens_weights = prev_sig.mul(scale, axis=0)

    # Gross daily return
    r_gross = (ens_weights * asset_returns).sum(axis=1)

    # Cost: spread applied to turnover (|Δw|) at each bar
    turnover = (ens_weights - ens_weights.shift(1).fillna(0.0)).abs().sum(axis=1)
    daily_cost = turnover * config.spread_one_way_pct
    r_net_pre_tax = r_gross - daily_cost

    # BR 15% tax applied monthly on positive realized return — same
    # approximation as Family B (Inter broker). For each calendar
    # month, if cumulative net > 0, multiply excess by (1 - tax).
    r_after_tax = r_net_pre_tax.copy()
    if config.tax_rate > 0:
        # Group by (year, month), apply tax to last day of each month.
        idx = r_net_pre_tax.index
        cum_month = pd.Series(0.0, index=idx)
        cum = 0.0
        prev_key = None
        month_indices: list[int] = []
        tax_paid = 0.0
        for i, ts in enumerate(idx):
            key = (ts.year, ts.month)
            if prev_key is None or key == prev_key:
                cum += r_net_pre_tax.iloc[i]
                month_indices.append(i)
            if prev_key is not None and key != prev_key:
                # close out previous month: if cum>0 apply tax
                if cum > 0:
                    drag = cum * config.tax_rate
                    # Apply drag evenly on the last day of prev month
                    last_i = month_indices[-1]
                    r_after_tax.iloc[last_i] -= drag
                    tax_paid += drag
                cum = r_net_pre_tax.iloc[i]
                month_indices = [i]
            prev_key = key
        # Final month
        if cum > 0 and month_indices:
            drag = cum * config.tax_rate
            last_i = month_indices[-1]
            r_after_tax.iloc[last_i] -= drag
            tax_paid += drag
    else:
        tax_paid = 0.0

    eq = (1.0 + r_after_tax.fillna(0.0)).cumprod()

    # Median hold: for each asset, compute run-lengths of prev_sig>0
    hold_lengths: list[int] = []
    for col in ens_weights.columns:
        active = ens_weights[col] > 0
        run = 0
        for v in active.values:
            if v:
                run += 1
            else:
                if run > 0:
                    hold_lengths.append(run)
                run = 0
        if run > 0:
            hold_lengths.append(run)
    mh = float(np.median(hold_lengths)) if hold_lengths else float("nan")

    return IStatSoundResult(
        equity=eq,
        daily_returns=r_after_tax,
        daily_returns_gross=r_gross,
        per_indicator_signals=per_indicator,
        ensemble_weights=ens_weights,
        survivors=list(survivors),
        screening_rows=[],  # filled by screen_indicators when used together
        cum_cost=float(daily_cost.sum()),
        cum_tax=float(tax_paid),
        config=config,
        median_hold=mh,
        hold_lengths=hold_lengths,
    )


# ---------------------------------------------------------------------------
# Screening protocol (MCPT + Bonferroni)
# ---------------------------------------------------------------------------


def _periodic_sharpe(r: np.ndarray) -> float:
    """Periodic (unit-time) Sharpe. Returns 0 for degenerate series."""
    r = r[np.isfinite(r)]
    if len(r) < 3:
        return 0.0
    s = r.std(ddof=1)
    if s <= 1e-12:
        return 0.0
    return float(r.mean() / s)


def _permute_panel(
    asset_returns: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    """Shuffle each column's rows independently (simple-market permutation).

    ``[testing_tuning, p.327-328]`` — simple-market permutation. Break
    serial + cross-correlation structure while preserving each asset's
    marginal return distribution. Returns a DataFrame with the same
    index/columns but shuffled values per column.
    """
    out = asset_returns.copy()
    for col in out.columns:
        vals = out[col].to_numpy(copy=True)
        rng.shuffle(vals)
        out[col] = vals
    return out


def _rebuild_prices_from_returns(
    prices0: pd.DataFrame, permuted_rets: pd.DataFrame
) -> pd.DataFrame:
    """Reconstruct a close-price panel from permuted returns.

    Used to regenerate indicator signals on permuted data. Starts from
    the first close of the original panel and compounds the permuted
    returns forward. ``[stat_sound_indicators, p.299-306]`` — TRAIN
    PERMUTED preconditions (indicators must be recomputable).
    """
    idx = permuted_rets.index
    out = pd.DataFrame(index=idx, columns=permuted_rets.columns, dtype=float)
    for col in out.columns:
        c0 = float(prices0[col].iloc[0])
        cum = (1.0 + permuted_rets[col].fillna(0.0)).cumprod()
        out[col] = c0 * cum.shift(1).fillna(1.0) * (
            cum / cum.shift(1).fillna(1.0)
        )
        # Simpler: close_t = c0 * prod(1+r)_1..t
        out[col] = c0 * (1.0 + permuted_rets[col].fillna(0.0)).cumprod()
    return out


def permutation_pvalue(
    slug: str,
    data_panel: Mapping[str, pd.DataFrame],
    asset_returns: pd.DataFrame,
    n_perm: int,
    seed: int,
) -> tuple[float, float, float]:
    """MCPT p-value for one indicator on the IS panel.

    Protocol:
    1. Compute observed periodic Sharpe of the long-only equal-weight
       ensemble using signal ``slug`` on the real data.
    2. For ``n_perm`` reps: permute each asset's return column
       independently, rebuild prices, recompute signals, measure
       permuted Sharpe.
    3. p_raw = (1 + #{perm ≥ obs}) / n_perm per
       ``[stat_sound_indicators, p.301]``.

    Returns
    -------
    (sr_obs, p_raw, runtime_seconds).
    """
    import time

    t0 = time.time()
    # Observed
    sig_obs = compute_signal(slug, data_panel)
    sig_obs = sig_obs.reindex(asset_returns.index).fillna(0.0)
    r_obs = _portfolio_daily_returns(sig_obs, asset_returns)
    sr_obs = _periodic_sharpe(r_obs.to_numpy(dtype=float))

    rng = np.random.default_rng(seed)
    # Precompute prices0 DataFrame for rebuild (just the first-close vector)
    prices0 = pd.DataFrame(
        {t: data_panel[t]["close"] for t in asset_returns.columns}
    ).reindex(asset_returns.index)

    count_ge = 0
    for k in range(n_perm):
        perm_ret = _permute_panel(asset_returns, rng)
        # Rebuild prices from permuted returns
        perm_close = pd.DataFrame(index=asset_returns.index, columns=asset_returns.columns, dtype=float)
        for col in asset_returns.columns:
            c0 = float(prices0[col].iloc[0])
            perm_close[col] = c0 * (1.0 + perm_ret[col].fillna(0.0)).cumprod()
        # Build permuted panel (use perm_close for ALL of close/high/low; high/low equal close
        # for the permuted regime — the indicators that use high/low will read degraded but
        # consistent info; most indicators only use close).
        perm_panel = {}
        for col in asset_returns.columns:
            perm_panel[col] = pd.DataFrame(
                {"close": perm_close[col], "high": perm_close[col], "low": perm_close[col]},
                index=asset_returns.index,
            )
        sig_k = compute_signal(slug, perm_panel)
        sig_k = sig_k.reindex(asset_returns.index).fillna(0.0)
        r_k = _portfolio_daily_returns(sig_k, perm_ret)
        sr_k = _periodic_sharpe(r_k.to_numpy(dtype=float))
        if sr_k >= sr_obs:
            count_ge += 1

    p_raw = (1.0 + count_ge) / (n_perm + 1.0)
    return float(sr_obs), float(p_raw), float(time.time() - t0)


def screen_indicators(
    data_panel_is: Mapping[str, pd.DataFrame],
    asset_returns_is: pd.DataFrame,
    config: IStatSoundConfig,
    verbose: bool = True,
) -> list[dict]:
    """Run the full Bonferroni-corrected screening on IS data.

    Returns a list of row-dicts, one per candidate, with keys
    ``{slug, sr_obs, p_raw, p_corrected, survive, runtime_s}``. Rows
    are in pool-order (not sorted).

    ``[stat_sound_indicators, p.170, p.174]`` — Bonferroni at
    α = 0.001 on family of M candidates.
    """
    M = config.effective_M
    alpha = config.screen_alpha
    rows: list[dict] = []
    for i, slug in enumerate(config.pool):
        # Different seed per candidate for independent permutation draws.
        seed_i = config.seed + i * 1000
        sr_obs, p_raw, rt = permutation_pvalue(
            slug, data_panel_is, asset_returns_is, config.n_permutations, seed_i
        )
        p_corr = min(1.0, M * p_raw)
        survive = p_corr < alpha
        row = {
            "slug": slug,
            "sr_obs": sr_obs,
            "p_raw": p_raw,
            "p_corrected_bonferroni": p_corr,
            "survive": bool(survive),
            "runtime_s": rt,
            "M": M,
            "alpha": alpha,
            "n_permutations": config.n_permutations,
        }
        rows.append(row)
        if verbose:
            mark = "KEEP" if survive else "drop"
            log.info(
                "[screen] %-22s SR=%.4f p_raw=%.4f p_corr=%.4f [%s] (%.1fs)",
                slug, sr_obs, p_raw, p_corr, mark, rt,
            )
            print(
                f"[screen] {slug:22s} SR={sr_obs:+.4f} p_raw={p_raw:.4f} "
                f"p_corr={p_corr:.4f} [{mark}] ({rt:.1f}s)"
            )
    return rows
