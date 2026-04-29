"""Synthetic ETF returns for the long-term portfolio sweep iter 027-039.

All synths return pd.Series of daily returns (decimal, e.g. 0.0123 = +1.23%).
Each function citation links to a book or paper that justifies the formula.
INCOMPLETE flag in docstring means the synth makes simplifying assumptions
that should be disclosed in any iter's final_report.md.
"""

from __future__ import annotations

import pandas as pd

from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_series

TRADING_DAYS_PER_YEAR = 252  # standard US equity trading-days/yr [advances_fin_ml]


def _annual_drag_to_daily(annual_drag_decimal: float) -> float:
    """Convert annual drag in decimal form to daily multiplicative drag.

    e.g. 75bps/y = 0.0075 -> 0.0075 / 252 ~= 2.98e-5 daily.
    """
    return annual_drag_decimal / TRADING_DAYS_PER_YEAR


def ntsd_synth_returns(
    spy_returns: pd.Series,
    vea_returns: pd.Series,
    financing_drag_annual: float = 0.0075,
) -> pd.Series:
    """NTSD synth: 90% S&P + 60% EAFE - annual financing drag.

    INCOMPLETE: WisdomTree NTSD active management unmodeled (~0-50bps/y
    tracking error). Active management could add or subtract.

    Citation: WisdomTree NTSD prospectus 2026-03-19; [risk_parity, ch.5]
    Carlson cap-efficient stacking.
    """
    daily_drag = _annual_drag_to_daily(financing_drag_annual)
    aligned = pd.concat({"spy": spy_returns, "vea": vea_returns}, axis=1).dropna()
    return 0.90 * aligned["spy"] + 0.60 * aligned["vea"] - daily_drag


def ntsd_synth_returns_from_cache() -> pd.Series:
    """Convenience: load SPYSIM + VEASIM from testfolio cache and synth."""
    spy = load_testfolio_series("SPYSIM").pct_change().dropna()
    vea = load_testfolio_series("VEASIM").pct_change().dropna()
    return ntsd_synth_returns(spy, vea)


def factor_tilt_synth_returns(
    proxy_returns: pd.Series,
    tilt_premium_annual: float,
) -> pd.Series:
    """Avantis-style factor synth: proxy returns + annual tilt premium.

    INCOMPLETE: VBRSIM/VSSSIM/VWOSIM are broad index proxies; Avantis
    AVUV/AVDV/AVEM concentrate SCV+profitability+value tilts. Real Avantis
    premium may be larger or smaller than the literature midpoint.

    Citations: [risk_parity, ch.2, p.37-41] Fama-French SCV;
    [ilmanen_expected_returns, ch.19] intl/EM factor diversification;
    [advances_fin_ml, p.31-34] factor framework.

    Args:
        proxy_returns: VBRSIM/VSSSIM/VWOSIM daily returns.
        tilt_premium_annual: annualized tilt premium added (decimal).
            Spec midpoints: 0.0075 (AVUV), 0.0100 (AVDV), 0.0125 (AVEM).
    """
    daily_premium = _annual_drag_to_daily(tilt_premium_annual)
    return proxy_returns + daily_premium


def avuv_synth_returns_from_cache() -> pd.Series:
    """AVUV synth: VBRSIM + 75bps/y tilt premium."""
    vbr = load_testfolio_series("VBRSIM").pct_change().dropna()
    return factor_tilt_synth_returns(vbr, tilt_premium_annual=0.0075)


def avdv_synth_returns_from_cache() -> pd.Series:
    """AVDV synth: VSSSIM + 100bps/y tilt premium."""
    vss = load_testfolio_series("VSSSIM").pct_change().dropna()
    return factor_tilt_synth_returns(vss, tilt_premium_annual=0.0100)


def avem_synth_returns_from_cache() -> pd.Series:
    """AVEM synth: VWOSIM + 125bps/y tilt premium. INCOMPLETE - VWOSIM 1994+ bottleneck."""
    vwo = load_testfolio_series("VWOSIM").pct_change().dropna()
    return factor_tilt_synth_returns(vwo, tilt_premium_annual=0.0125)
