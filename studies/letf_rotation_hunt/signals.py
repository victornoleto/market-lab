"""Signal indicators for LETF rotation hunt.

Implements binary entry/exit gates and continuous forecasts per spec §2.7.

All gates return pd.Series of {0, 1, NaN} (NaN = warmup); continuous forecasts
return pd.Series of floats. Index matches input prices.

Citations:
  - SMA/EMA gates: [leverage_for_the_long_run, p.13]
  - EMA decay α = 2/(L+1): [systematic_trading, p.283]
  - Realized vol gate 40%: [leverage_for_the_long_run, p.5-6]
  - VIX scaling: [paper.bozovic_2024_vix_managed]
  - AR(1) regime: [paper.hsieh_2025_letf_compounding]
  - HMM 2-state: [knowledge/indicators/regime_hmm], [ml_for_algo_trading, ch.9]
  - EWMAC: [systematic_trading, ch.7-8 p.122-133]
  - Clenow slope×R²: [stocks_on_the_move, p.98]
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def sma_gate(prices: pd.Series, period: int = 200) -> pd.Series:
    """Binary gate: 1 if price > SMA(period), else 0. NaN during warmup.

    Per [leverage_for_the_long_run, p.13]: canonical Gayed LRS signal.

    Parameters
    ----------
    prices : pd.Series
        Daily close prices (datetime index).
    period : int
        SMA lookback (e.g. 200 for canonical 200-day).

    Returns
    -------
    pd.Series
        {0, 1, NaN}. Same index as prices.
    """
    sma = prices.rolling(window=period, min_periods=period).mean()
    gate = (prices > sma).astype(float)
    gate[sma.isna()] = np.nan
    return gate


def ema_gate(prices: pd.Series, period: int = 200) -> pd.Series:
    """Binary gate: 1 if price > EMA(period), else 0. NaN during warmup.

    EMA decay α = 2 / (period + 1) per [systematic_trading, p.283].
    Warmup: same period as SMA for fair comparison (per spec §2.2 T1b).

    Parameters
    ----------
    prices : pd.Series
        Daily close prices.
    period : int
        EMA span.

    Returns
    -------
    pd.Series
        {0, 1, NaN}. Same index as prices.
    """
    ema = prices.ewm(span=period, min_periods=period, adjust=False).mean()
    gate = (prices > ema).astype(float)
    gate[ema.isna()] = np.nan
    return gate


TRADING_DAYS_PER_YEAR = 252


def realized_vol_gate(
    returns: pd.Series,
    window: int = 21,
    threshold: float = 0.40,
) -> pd.Series:
    """Binary gate: 1 if rolling realized vol < threshold (annualized), else 0.

    Per [leverage_for_the_long_run, p.5-6]: above 40% annualized vol, daily
    re-leveraging decay dominates returns. Default threshold 40%.

    Parameters
    ----------
    returns : pd.Series
        Daily returns (decimal, e.g. 0.01 for +1%).
    window : int
        Rolling window for realized vol (default 21 trading days = 1 month).
    threshold : float
        Annualized vol threshold above which gate = 0 (default 0.40).

    Returns
    -------
    pd.Series
        {0, 1, NaN}. Same index as returns.
    """
    realized_vol = returns.rolling(window=window, min_periods=window).std() * np.sqrt(
        TRADING_DAYS_PER_YEAR
    )
    gate = (realized_vol < threshold).astype(float)
    gate[realized_vol.isna()] = np.nan
    return gate


def vix_scaling(
    vix: pd.Series,
    lookback_baseline: int = 252,
    lookback_prev_month: int = 21,
) -> pd.Series:
    """Continuous weight = clip(VIX_baseline / VIX_prev_month, 0, 1).

    Per [paper.bozovic_2024_vix_managed]: scale exposure inversely to recent VIX.
    Lower VIX_prev_month → weight → 1; higher VIX_prev_month → weight → 0.

    Parameters
    ----------
    vix : pd.Series
        Daily VIX index closes.
    lookback_baseline : int
        Long-term VIX baseline window (default 252 = 1 year).
    lookback_prev_month : int
        Recent VIX window (default 21 = 1 month).

    Returns
    -------
    pd.Series
        Float in [0, 1]. NaN during warmup.
    """
    baseline = vix.rolling(window=lookback_baseline, min_periods=lookback_baseline).mean()
    prev_month = vix.rolling(window=lookback_prev_month, min_periods=lookback_prev_month).mean()
    raw = baseline / prev_month.replace(0, np.nan)  # avoid div-by-zero
    weight = raw.clip(lower=0.0, upper=1.0)
    return weight


def ar1_coefficient(returns: pd.Series, window: int = 30) -> pd.Series:
    """Rolling AR(1) coefficient of returns.

    Per [paper.hsieh_2025_letf_compounding]: positive AR(1) → momentum regime
    (LETF outperforms); negative AR(1) → mean-reversion (LETF decay dominates).

    Parameters
    ----------
    returns : pd.Series
        Daily returns.
    window : int
        Rolling window for AR(1) estimation (default 30).

    Returns
    -------
    pd.Series
        AR(1) coefficient ∈ [-1, 1] approx. NaN during warmup.
    """

    def _ar1(x: np.ndarray) -> float:
        if len(x) < 2 or np.any(np.isnan(x)):
            return np.nan
        x_lag = x[:-1]
        x_curr = x[1:]
        if np.std(x_lag) == 0 or np.std(x_curr) == 0:
            return 0.0
        return float(np.corrcoef(x_lag, x_curr)[0, 1])

    return returns.rolling(window=window, min_periods=window).apply(_ar1, raw=True)


def vote_of_k(signals: list[pd.Series], k: int) -> pd.Series:
    """Composite gate: 1 if ≥ k of len(signals) signals are ON, else 0.

    Per spec §2.4 T3d: anti-whipsaw vote-of-K composite.

    Parameters
    ----------
    signals : list[pd.Series]
        List of binary {0, 1} signals; aligned indices required.
    k : int
        Minimum ON count.

    Returns
    -------
    pd.Series
        {0, 1, NaN}. NaN propagated from any input NaN.
    """
    if not signals:
        raise ValueError("vote_of_k requires at least one signal")
    if k > len(signals):
        raise ValueError(f"k={k} exceeds number of signals ({len(signals)})")
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    df = pd.concat(signals, axis=1)
    total_on = df.sum(axis=1)
    any_nan = df.isna().any(axis=1)
    gate = (total_on >= k).astype(float)
    gate[any_nan] = np.nan
    return gate


def hmm_regime_gate(
    returns: pd.Series,
    n_states: int = 2,
    refit_every: int = 252,
    train_window: int = 252,
    sticky_days: int = 3,
) -> pd.Series:
    """HMM regime classifier; gate ON if state has higher mean return.

    Per [knowledge/indicators/regime_hmm] + [ml_for_algo_trading, ch.9]:
    Gaussian Mixture HMM, refit periodically (avoid look-ahead). Sticky
    transition: state must persist `sticky_days` to flip.

    Parameters
    ----------
    returns : pd.Series
        Daily returns.
    n_states : int
        HMM hidden states (default 2 = bull/bear).
    refit_every : int
        Refit interval (days; default 252 = annual).
    train_window : int
        Rolling training window (default 252).
    sticky_days : int
        Required consecutive days in new state to flip gate (default 3).

    Returns
    -------
    pd.Series
        {0, 1, NaN}. Same index as returns.
    """
    try:
        from hmmlearn.hmm import GaussianHMM
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "hmm_regime_gate requires hmmlearn; install via `uv pip install hmmlearn`"
        ) from exc

    n = len(returns)
    raw_states = np.full(n, np.nan)
    bull_state_id = None
    model = None

    for t in range(train_window, n):
        # Refit on schedule
        if (t - train_window) % refit_every == 0:
            train_data = returns.iloc[t - train_window:t].values.reshape(-1, 1)
            model = GaussianHMM(
                n_components=n_states,
                covariance_type="diag",
                n_iter=100,
                random_state=42,
            )
            try:
                model.fit(train_data)
                # Identify bull state = state with higher mean
                bull_state_id = int(np.argmax(model.means_.flatten()))
            except Exception:
                continue

        if model is None:
            continue

        # Predict current state
        try:
            current_window = returns.iloc[t - train_window:t + 1].values.reshape(-1, 1)
            states = model.predict(current_window)
            raw_states[t] = states[-1]
        except Exception:
            continue

    # Convert states → {0, 1}: 1 if bull state, 0 otherwise
    raw_gate = pd.Series(raw_states, index=returns.index)
    if bull_state_id is not None:
        binary = (raw_gate == bull_state_id).astype(float)
    else:
        binary = pd.Series(np.nan, index=returns.index)
    binary[raw_gate.isna()] = np.nan

    # Apply sticky filter: flip only if new state persists sticky_days
    sticky = binary.copy()
    for t in range(sticky_days, len(binary)):
        if pd.isna(binary.iloc[t]):
            continue
        # Check last sticky_days are all the same
        recent = binary.iloc[t - sticky_days + 1:t + 1]
        if recent.isna().any():
            sticky.iloc[t] = sticky.iloc[t - 1] if t > 0 else np.nan
        elif (recent == recent.iloc[-1]).all():
            sticky.iloc[t] = recent.iloc[-1]
        else:
            sticky.iloc[t] = sticky.iloc[t - 1] if t > 0 else np.nan

    return sticky


def ewmac_forecast(
    prices: pd.Series,
    lfast: int = 16,
    lslow: int = 64,
    scalar: float = 3.75,
    cap: float = 20.0,
) -> pd.Series:
    """EWMAC forecast per Carver [systematic_trading, ch.7-8 p.122-133].

    forecast = scalar × (EMA_fast - EMA_slow) / sigma_price_points
    Capped at ±cap (default 20).

    Default scalar from Table 49 [p.285]: EWMAC(16,64) → 3.75.

    Parameters
    ----------
    prices : pd.Series
        Daily close prices.
    lfast : int
        Fast EMA span.
    lslow : int
        Slow EMA span.
    scalar : float
        Forecast scalar (per Carver Table 49).
    cap : float
        Forecast cap (default ±20).

    Returns
    -------
    pd.Series
        Forecast in [-cap, +cap]. NaN during warmup.
    """
    if lfast >= lslow:
        raise ValueError(f"lfast ({lfast}) must be < lslow ({lslow})")
    if scalar <= 0:
        raise ValueError(f"scalar must be > 0, got {scalar}")
    if cap <= 0:
        raise ValueError(f"cap must be > 0, got {cap}")
    afast = 2.0 / (lfast + 1)
    aslow = 2.0 / (lslow + 1)
    efast = prices.ewm(alpha=afast, min_periods=lfast, adjust=False).mean()
    eslow = prices.ewm(alpha=aslow, min_periods=lslow, adjust=False).mean()
    raw_crossover = efast - eslow
    # sigma in price-points: rolling std of daily price changes (not %)
    price_changes = prices.diff()
    sigma_pp = price_changes.rolling(window=lslow, min_periods=lslow).std()
    forecast = (raw_crossover / sigma_pp.replace(0, np.nan)) * scalar
    return forecast.clip(lower=-cap, upper=cap)


def clenow_score(prices: pd.Series, window: int = 90) -> pd.Series:
    """Clenow ranking score = annualized exp regression slope × R².

    Per [stocks_on_the_move, p.70-77, p.98]: ranking signal for cross-sectional
    momentum. Higher = better trend with smoother fit.

    Parameters
    ----------
    prices : pd.Series
        Daily close prices.
    window : int
        Regression window (default 90 trading days).

    Returns
    -------
    pd.Series
        Score = ((exp(slope))^250 - 1) × R². NaN during warmup.
    """

    def _score(x: np.ndarray) -> float:
        if len(x) < window or np.any(x <= 0):
            return np.nan
        log_x = np.log(x)
        t = np.arange(len(log_x), dtype=float)
        # Linear regression
        slope, intercept = np.polyfit(t, log_x, 1)
        y_pred = slope * t + intercept
        ss_res = np.sum((log_x - y_pred) ** 2)
        ss_tot = np.sum((log_x - log_x.mean()) ** 2)
        if ss_tot == 0:
            return 0.0
        r_squared = 1.0 - ss_res / ss_tot
        annualized = (np.exp(slope)) ** 250 - 1
        return float(annualized * r_squared)

    return prices.rolling(window=window, min_periods=window).apply(_score, raw=True)
