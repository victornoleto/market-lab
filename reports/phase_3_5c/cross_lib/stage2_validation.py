"""Stage-2 independent validation for Phase 3.5 sweep scripts.

Replaces the legacy per-script ``run_stage2(yfinance_re_fetch)`` pattern that
produced unstable yfinance-vs-yfinance ΔCAGR (8.21pp on QLD, 15.16pp on TQQQ
during Phase 3.5e iter 21 and 23 — see ``jornada/2026-04-21-*-data-pipeline-
tiingo-first.md``).

Data routing
------------
- SSO (2× SPY) → testfol.io `spy_2x_equity` series (1885-03-20 to 2026-04-16)
- UPRO (3× SPY) → testfol.io `spy_3x_equity` series (1885-03-20 to 2026-04-16)
- SPXL (3× SPY) → testfol.io `spy_3x_equity` series
- QLD (2× QQQ) / TQQQ (3× QQQ) → N/A (no QQQSIM payload; future work)
- UGL (2× GLD) / TMF (3× TLT) → N/A (no commodity/bond SIM payload)

Citations
---------
- testfol.io methodology documented in ``data/external/README.md``.
- Two-stage isolation rationale: ``[advances_fin_ml, p.31-34]``.
- Tolerance 3pp ΔCAGR: spec §6.3 of the 3.5c cross-lib design doc.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd


TESTFOLIO_PARQUET = Path("data/external/testfolio_spysim_leverage.parquet")

# LETF ticker → testfol.io series mapping. None marks "no independent
# reference available" (N/A Stage-2).
_TESTFOLIO_COLUMN: dict[str, str | None] = {
    "SSO": "spy_2x_equity",
    "UPRO": "spy_3x_equity",
    "SPXL": "spy_3x_equity",
    # QQQ-based: testfol.io parquet does not carry a QQQSIM leveraged series.
    "QLD": None,
    "TQQQ": None,
    # Commodity/bond: same story.
    "UGL": None,
    "TMF": None,
}

# Strategy portfolios (e.g. c01_sma200_gld on SSO) also need a Stage-2 check
# by running the same rule on the testfol.io series. For backtest frameworks
# that compute CAGR from daily returns, the SIM series converts trivially:
# returns = (equity[t] / equity[t-1]) - 1.

Stage2Status = Literal["concordant", "divergent", "na"]


@dataclass(frozen=True)
class Stage2Result:
    """Result of a Stage-2 cross-source CAGR check.

    Attributes
    ----------
    cagr_stage2 : float | None
        CAGR reproduced on the independent source, or None when N/A.
    cagr_delta_pp : float | None
        ``|cagr_stage1 - cagr_stage2| * 100`` in percentage points.
    status : Stage2Status
        ``concordant`` when ΔCAGR ≤ tolerance, ``divergent`` when over,
        ``na`` when no independent reference exists for this ticker.
    reason : str
        Free-form note (why N/A, which series was used, etc.).
    """

    cagr_stage2: float | None
    cagr_delta_pp: float | None
    status: Stage2Status
    reason: str


def load_testfolio_returns(ticker: str) -> pd.Series | None:
    """Return daily simple returns from testfol.io for ``ticker``, or None.

    The testfol.io parquet contains three equity curves (SPY 1x/2x/3x) since
    1885. We convert the mapped column to daily simple returns for direct
    use by backtest frameworks.
    """
    col = _TESTFOLIO_COLUMN.get(ticker)
    if col is None:
        return None

    if not TESTFOLIO_PARQUET.exists():
        return None

    df = pd.read_parquet(TESTFOLIO_PARQUET)
    series = df[col]
    returns = series.pct_change().dropna()
    returns.name = ticker
    return returns


def run_stage2(
    ticker: str,
    cagr_stage1: float,
    *,
    strategy_cagr_fn=None,
    window_start: str | None = None,
    window_end: str | None = None,
    tolerance_pp: float = 3.0,
) -> Stage2Result:
    """Validate ``cagr_stage1`` against an independent reference source.

    Parameters
    ----------
    ticker : str
        LETF ticker (SSO, UPRO, SPXL, QLD, TQQQ, UGL, TMF).
    cagr_stage1 : float
        CAGR decimal (e.g. 0.15 = 15%) computed on the Stage-1
        reference_prices.parquet run.
    strategy_cagr_fn : callable, optional
        If provided, a function ``fn(returns_series) -> cagr_float`` that
        reproduces the strategy on testfol.io returns. When None, we
        compute buy-hold CAGR of the testfol.io equity curve directly
        (appropriate only for passive benchmarks).
    window_start, window_end : str, optional
        ISO dates bounding the testfol.io slice.
    tolerance_pp : float
        Maximum ΔCAGR (percentage points) for concordance. Default 3pp
        per spec §6.3.
    """
    returns = load_testfolio_returns(ticker)
    if returns is None:
        return Stage2Result(
            cagr_stage2=None,
            cagr_delta_pp=None,
            status="na",
            reason=(
                f"No independent reference available for {ticker}. "
                "SPY-based LETFs (SSO/UPRO/SPXL) map to testfol.io spy_{2x,3x}_equity; "
                "QQQ/GLD/TLT-based (QLD/TQQQ/UGL/TMF) need a future testfol.io payload."
            ),
        )

    if window_start or window_end:
        start_ts = pd.Timestamp(window_start) if window_start else returns.index.min()
        end_ts = pd.Timestamp(window_end) if window_end else returns.index.max()
        returns = returns.loc[start_ts:end_ts]

    if returns.empty:
        return Stage2Result(
            cagr_stage2=None,
            cagr_delta_pp=None,
            status="na",
            reason=f"testfol.io window [{window_start},{window_end}] is empty for {ticker}.",
        )

    if strategy_cagr_fn is not None:
        cagr_stage2 = float(strategy_cagr_fn(returns))
    else:
        cagr_stage2 = _buy_hold_cagr(returns)

    delta_pp = abs(cagr_stage1 - cagr_stage2) * 100.0
    status: Stage2Status = "concordant" if delta_pp <= tolerance_pp else "divergent"

    return Stage2Result(
        cagr_stage2=cagr_stage2,
        cagr_delta_pp=delta_pp,
        status=status,
        reason=f"testfol.io {_TESTFOLIO_COLUMN[ticker]} (ΔCAGR={delta_pp:.2f}pp, tolerance={tolerance_pp}pp).",
    )


def _buy_hold_cagr(returns: pd.Series) -> float:
    """CAGR of (1 + r).cumprod() over the series' calendar window."""
    if returns.empty:
        return float("nan")
    total = float((1.0 + returns).prod())
    years = (returns.index[-1] - returns.index[0]).days / 365.25
    if years <= 0 or total <= 0:
        return float("nan")
    return total ** (1.0 / years) - 1.0
