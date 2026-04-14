"""Performance metrics: pure functions over returns / equity series.

References
----------
* Sharpe, Sortino, Calmar — classical definitions, e.g. Kaufman (2020) ch.21,
  Carver (2015) ch.3, López de Prado (2018) ch.14.
* CAGR — compound annual growth rate: ``(V_T/V_0)^(P/T) − 1`` where ``P`` is
  the annualization factor (252 for daily business days, 52 for weekly, 12
  for monthly).
* Historical VaR — quantile of realized returns, reported as a positive
  magnitude of loss.

Conventions
-----------
* All volatilities and Sharpe-like ratios use population std (``ddof=0``).
  This matches the ``validation.dsr.sharpe_periodic`` convention so the
  metric values printed in reports are consistent with the DSR inputs.
* Returns-based functions (``sharpe``, ``sortino``, ``volatility``, ``var``)
  take a ``pd.Series`` of per-period returns.
* Equity-based functions (``cagr``, ``max_drawdown``, ``calmar``) take a
  ``pd.Series`` of equity values indexed by timestamp.
* Ill-defined ratios (zero-volatility Sharpe, zero-downside Sortino,
  zero-drawdown Calmar) return ``0.0`` / ``+inf`` rather than raising — the
  report surface wants to print *something* for every field.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def returns_from_equity(equity: pd.Series) -> pd.Series:
    """Simple per-period returns from an equity curve (``pct_change`` dropping NaN)."""
    return equity.pct_change().dropna()


def volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Annualized return volatility ``σ · √P`` (population std, ``ddof=0``)."""
    if len(returns) == 0:
        return 0.0
    return float(returns.std(ddof=0) * np.sqrt(periods_per_year))


def sharpe(
    returns: pd.Series, periods_per_year: int = 252, risk_free: float = 0.0
) -> float:
    """Annualized Sharpe ratio ``(μ − rf) / σ · √P``.

    ``risk_free`` is interpreted as a per-period rate (not annual) so the
    caller controls its own compounding convention.
    """
    if len(returns) == 0:
        return 0.0
    sigma = float(returns.std(ddof=0))
    if sigma <= 1e-12:
        return 0.0
    return (float(returns.mean()) - risk_free) / sigma * np.sqrt(periods_per_year)


def sortino(
    returns: pd.Series, periods_per_year: int = 252, target: float = 0.0
) -> float:
    """Annualized Sortino ratio: ``(μ − target) / downside_dev · √P``.

    Downside deviation uses the Estrada-style formula
    ``√(mean(min(r − target, 0)²))`` — the denominator counts every period,
    not just losing ones. If no period falls below the target the series has
    no downside risk; by convention this returns ``+inf``.
    """
    if len(returns) == 0:
        return 0.0
    downside = np.minimum(returns - target, 0.0)
    dev = float(np.sqrt(np.mean(downside**2)))
    if dev <= 1e-12:
        return float("inf")
    return (float(returns.mean()) - target) / dev * np.sqrt(periods_per_year)


def cagr(equity: pd.Series, periods_per_year: int = 252) -> float:
    """Compound annual growth rate ``(V_T / V_0)^(P / n) − 1``.

    ``n`` is the number of periods (``len(equity) − 1``), not the length of
    the series, because ``equity`` includes the starting value.
    """
    if len(equity) < 2:
        return 0.0
    v0 = float(equity.iloc[0])
    vT = float(equity.iloc[-1])
    if v0 <= 0:
        raise ValueError(f"equity[0]={v0} must be positive for CAGR")
    n_periods = len(equity) - 1
    return (vT / v0) ** (periods_per_year / n_periods) - 1.0


def max_drawdown(equity: pd.Series) -> float:
    """Maximum peak-to-trough drawdown as a positive magnitude in [0, 1]."""
    if len(equity) == 0:
        return 0.0
    running_peak = equity.cummax()
    dd = (running_peak - equity) / running_peak
    return float(dd.max())


def calmar(equity: pd.Series, periods_per_year: int = 252) -> float:
    """Calmar ratio ``CAGR / |max_drawdown|``. ``+inf`` if no drawdown."""
    dd = max_drawdown(equity)
    if dd <= 1e-12:
        return float("inf")
    return cagr(equity, periods_per_year=periods_per_year) / dd


def var(returns: pd.Series, alpha: float = 0.05) -> float:
    """Historical Value-at-Risk at confidence ``1 − α``, positive magnitude.

    For returns normally distributed around zero, α=0.05 yields ≈ 1.645·σ.
    If the α-quantile is non-negative (all returns positive at that level),
    VaR is floored at 0 — a positive quantile represents a gain, not a loss.
    """
    if len(returns) == 0:
        return 0.0
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    q = float(np.quantile(returns, alpha))
    return max(-q, 0.0)
