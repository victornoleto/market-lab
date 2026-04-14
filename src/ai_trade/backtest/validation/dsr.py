"""Probabilistic and Deflated Sharpe Ratios.

References
----------
* AFML ch.14 p.273-275 — Sharpe, PSR, DSR derivations.
* Bailey, López de Prado (2012) "The Sharpe Ratio Efficient Frontier",
  *Journal of Risk* 15(2) — PSR formula with skew/kurt correction.
* AFML ch.12 p.222-223 — asymptotic expected maximum Sharpe under the Gumbel
  approximation: ``E[SR_max] ≈ (1-γ)·Φ⁻¹(1-1/N) + γ·Φ⁻¹(1-1/(N·e))``.

Conventions
-----------
Sharpe ratios in this module are *periodic* by default (no annualization)
because PSR/DSR treat ``T`` as "number of observations in the track record"
and the sample skewness/kurtosis are per-period quantities. Use
:func:`sharpe_annualized` when reporting; the annualized SR is monotone in
the periodic one, so DSR gates built from periodic values are equivalent.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import ndtr, ndtri


EULER_MASCHERONI = 0.5772156649015329


def sharpe_periodic(returns: np.ndarray, risk_free: float = 0.0) -> float:
    """Per-period Sharpe ``(μ - rf) / σ`` with population std (ddof=0)."""
    returns = np.asarray(returns, dtype=float)
    sigma = returns.std(ddof=0)
    if sigma <= 1e-12:
        return 0.0
    return (returns.mean() - risk_free) / sigma


def sharpe_annualized(
    returns: np.ndarray, periods_per_year: int = 252, risk_free: float = 0.0
) -> float:
    """Annualized Sharpe = periodic Sharpe × ``√periods_per_year``."""
    return sharpe_periodic(returns, risk_free=risk_free) * np.sqrt(periods_per_year)


def psr(returns: np.ndarray, benchmark: float = 0.0) -> float:
    """Probabilistic Sharpe Ratio [AFML p.273-274; Bailey & LdP 2012].

    Returns the probability that the true (unknown) Sharpe exceeds
    ``benchmark`` given the observed periodic Sharpe, sample skewness,
    sample kurtosis (non-excess), and track-record length ``T``:

        PSR[SR*] = Φ( (SR_hat - SR*) · √(T-1) /
                      √(1 - γ3·SR_hat + (γ4-1)/4·SR_hat²) )
    """
    returns = np.asarray(returns, dtype=float)
    T = len(returns)
    if T < 3:
        raise ValueError("PSR needs at least 3 observations")

    sr_hat = sharpe_periodic(returns)
    mu = returns.mean()
    sigma = returns.std(ddof=0)
    if sigma <= 1e-12:
        # Degenerate series — Sharpe ill-defined; return boundary.
        return 0.5

    centered = returns - mu
    gamma3 = float(np.mean(centered**3) / sigma**3)
    gamma4 = float(np.mean(centered**4) / sigma**4)  # raw, not excess

    denom_sq = 1.0 - gamma3 * sr_hat + (gamma4 - 1.0) / 4.0 * sr_hat**2
    # Numeric guard: under extreme fat tails the quadratic correction can dip
    # below zero, which would make PSR undefined. Floor at a small positive.
    denom = np.sqrt(max(denom_sq, 1e-12))
    z = (sr_hat - benchmark) * np.sqrt(T - 1) / denom
    return float(ndtr(z))


def expected_max_sharpe(n_trials: int, var_sharpe: float = 1.0) -> float:
    """Asymptotic expected max Sharpe under ``N`` iid-noise trials [AFML p.222-223].

    Returns ``√V · [(1 - γ)·Φ⁻¹(1 - 1/N) + γ·Φ⁻¹(1 - 1/(N·e))]`` where γ is
    the Euler-Mascheroni constant and ``V = var_sharpe`` is the variance of
    the Sharpe estimators being compared.

    * ``var_sharpe = 1`` (default) returns the value in *estimator-std units*
      (i.e., assuming Sharpes are already studentized — AFML ch.14 context).
    * For a single-strategy DSR test of sample size ``T``, the iid-null
      variance of ``SR_hat`` is ``1/(T-1)``, so pass ``var_sharpe=1/(T-1)``
      to obtain ``E[SR_max]`` in the same periodic-Sharpe units as
      :func:`sharpe_periodic`.
    """
    if n_trials < 2:
        raise ValueError(f"need n_trials >= 2, got {n_trials}")
    a = ndtri(1.0 - 1.0 / n_trials)
    b = ndtri(1.0 - 1.0 / (n_trials * np.e))
    core = (1.0 - EULER_MASCHERONI) * a + EULER_MASCHERONI * b
    return float(np.sqrt(var_sharpe) * core)


@dataclass
class DSRResult:
    dsr: float
    p_value: float
    observed_sharpe: float
    benchmark_sharpe: float
    n_trials: int


def dsr(returns: np.ndarray, n_trials: int) -> DSRResult:
    """Deflated Sharpe Ratio [AFML p.275].

    DSR = PSR evaluated at benchmark = ``E[SR_max]`` under ``n_trials`` tries,
    answering: is the observed Sharpe still significant AFTER correcting for
    multiple-testing bias?

    ``p_value = 1 - DSR`` is the probability that the observed SR is a product
    of selection bias rather than skill.
    """
    if n_trials < 2:
        raise ValueError("DSR requires at least 2 trials; for a single configuration use PSR")
    returns = np.asarray(returns, dtype=float)
    T = len(returns)
    # Under the iid null, Var(SR_hat) ≈ 1/(T-1); scale E[SR_max] into the
    # same periodic-Sharpe units PSR consumes.
    benchmark = expected_max_sharpe(n_trials, var_sharpe=1.0 / (T - 1))
    p = psr(returns, benchmark=benchmark)
    return DSRResult(
        dsr=p,
        p_value=1.0 - p,
        observed_sharpe=sharpe_periodic(returns),
        benchmark_sharpe=benchmark,
        n_trials=n_trials,
    )
