"""Hurst exponent estimator via structure function.

Formula from Chan (2013) ``[algo_trading_chan, p.44-46, ch.2]``:

    <|z(t+τ) - z(t)|^2> ~ τ^{2H}

So a log-log regression of the mean-squared displacement on lag τ yields
slope ``2H``; we return ``H = slope/2``.

Interpretation [algo_trading_chan, p.44-45]:
    H ≈ 0.5 → geometric random walk
    H < 0.5 → mean-reverting (anti-persistent)
    H > 0.5 → trending (persistent)

Caveat from cycle_analytics.md p.74-75: Hurst is sample-length sensitive.
We restrict τ ∈ [2, n/4] and require ``min_obs`` bars to keep the estimate
stable. We also bootstrap a 95% CI by resampling residuals so callers can
gauge noise.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HurstResult:
    """Hurst estimate plus diagnostics."""

    h: float
    r2: float
    n_obs: int
    n_lags: int
    ci_low: float | None
    ci_high: float | None


def _mean_sq_displacement(log_p: np.ndarray, lag: int) -> float:
    diff = log_p[lag:] - log_p[:-lag]
    return float(np.mean(diff * diff))


def _fit_hurst(log_p: np.ndarray, lags: np.ndarray) -> tuple[float, float]:
    msd = np.array([_mean_sq_displacement(log_p, int(t)) for t in lags])
    # Drop any zero/negative MSDs (degenerate constant-price segments)
    mask = msd > 0
    if mask.sum() < 3:
        raise ValueError("hurst_exponent: insufficient non-degenerate lags")
    log_tau = np.log(lags[mask].astype(float))
    log_msd = np.log(msd[mask])
    # OLS slope of log_msd ~ 2H * log_tau + c
    t_mean = log_tau.mean()
    m_mean = log_msd.mean()
    var_t = ((log_tau - t_mean) ** 2).sum()
    if var_t <= 0:
        raise ValueError("hurst_exponent: log-tau variance is zero")
    cov = ((log_tau - t_mean) * (log_msd - m_mean)).sum()
    slope = cov / var_t
    intercept = m_mean - slope * t_mean
    pred = slope * log_tau + intercept
    sse = ((log_msd - pred) ** 2).sum()
    sst = ((log_msd - m_mean) ** 2).sum()
    r2 = 1.0 - sse / sst if sst > 0 else 0.0
    return float(slope / 2.0), float(r2)


def hurst_exponent(
    prices: pd.Series,
    *,
    min_obs: int = 100,
    max_lag: int | None = None,
    n_lags: int = 20,
    bootstrap: int = 0,
    random_state: int | None = None,
) -> HurstResult:
    """Return :class:`HurstResult` for ``prices`` (positive close series).

    Parameters
    ----------
    prices
        Pandas Series of strictly positive prices indexed by datetime.
    min_obs
        Minimum number of observations required. Default 100 follows the
        cycle_analytics warning (p.74-75) that very short series produce
        unstable Hurst values.
    max_lag
        Largest lag τ used in the regression. Defaults to ``n//4``.
    n_lags
        Number of log-spaced lags from 2 to ``max_lag`` used for the fit.
    bootstrap
        If > 0, resample log-returns ``bootstrap`` times to compute a 95%
        CI on H. Set to 0 to skip (faster).
    random_state
        Optional seed for the bootstrap.

    Citation: ``[algo_trading_chan, p.44-46, ch.2]``.
    """

    if not isinstance(prices, pd.Series):
        raise TypeError("hurst_exponent: prices must be a pd.Series")
    series = prices.dropna().astype(float)
    n = len(series)
    if n < min_obs:
        raise ValueError(
            f"hurst_exponent: need at least {min_obs} observations, got {n}"
        )
    if (series <= 0).any():
        raise ValueError("hurst_exponent: prices must be strictly positive")

    log_p = np.log(series.to_numpy())
    upper = max_lag if max_lag is not None else max(2, n // 4)
    upper = min(upper, n - 1)
    if upper < 4:
        raise ValueError("hurst_exponent: not enough range to fit Hurst")
    raw_lags = np.unique(
        np.round(np.geomspace(2, upper, num=n_lags)).astype(int)
    )
    raw_lags = raw_lags[raw_lags >= 2]
    if len(raw_lags) < 3:
        raise ValueError("hurst_exponent: need at least 3 distinct lags")

    h, r2 = _fit_hurst(log_p, raw_lags)

    ci_low: float | None = None
    ci_high: float | None = None
    if bootstrap > 0:
        rng = np.random.default_rng(random_state)
        log_ret = np.diff(log_p)
        if log_ret.size < 10:
            raise ValueError(
                "hurst_exponent: not enough returns for bootstrap"
            )
        boots = np.empty(bootstrap, dtype=float)
        for i in range(bootstrap):
            sample = rng.choice(log_ret, size=log_ret.size, replace=True)
            sim_log_p = np.concatenate(([log_p[0]], log_p[0] + np.cumsum(sample)))
            try:
                bh, _ = _fit_hurst(sim_log_p, raw_lags)
            except ValueError:
                continue
            boots[i] = bh
        boots = boots[~np.isnan(boots)]
        if boots.size > 0:
            ci_low = float(np.quantile(boots, 0.025))
            ci_high = float(np.quantile(boots, 0.975))

    return HurstResult(
        h=h,
        r2=r2,
        n_obs=n,
        n_lags=int(len(raw_lags)),
        ci_low=ci_low,
        ci_high=ci_high,
    )
