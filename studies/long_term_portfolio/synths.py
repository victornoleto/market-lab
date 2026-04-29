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


def momentum_synth_returns(
    base_equity_returns: pd.Series,
    umd_factor_returns: pd.Series,
    capture_coef: float = 0.60,
    expense_annual: float = 0.0035,
) -> pd.Series:
    """SPMO/IDMO-style momentum synth: base equity + UMD overlay - expense.

    INCOMPLETE: Frazzini-Israel-Moskowitz 2018 capture rate (~60-70%) is
    literature-cited, not direct SPMO/IDMO inception data. Real SPMO/IDMO
    tracking error unmeasured. Engine differs from Ken French academic UMD
    (long-short market-neutral, gross of cost).

    Citations: [stocks_on_the_move, p.21-30] Clenow time-series momentum;
    Jegadeesh-Titman 1993 cross-sectional momentum; Frazzini-Israel-Moskowitz
    2018 long-only momentum capture.
    """
    daily_expense = _annual_drag_to_daily(expense_annual)
    aligned = pd.concat({"base": base_equity_returns, "umd": umd_factor_returns}, axis=1).dropna()
    return aligned["base"] + capture_coef * aligned["umd"] - daily_expense


def _load_umd_kf_returns() -> pd.Series:
    """Load Ken French daily UMD factor returns from data/ken_french/.

    File format: F-F_Momentum_Factor_daily.csv has skip rows then columns
    Date, Mom (in percent units, e.g. 0.50 means +0.50%). Convert to decimal.
    """
    import pathlib
    csv_path = pathlib.Path("data/ken_french/F-F_Momentum_Factor_daily.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Ken French UMD daily file not found at {csv_path}")
    df = pd.read_csv(csv_path, skiprows=13, index_col=0, parse_dates=False)
    df = df[df.index.astype(str).str.match(r"^\d{8}$")]
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    # Column header may have trailing whitespace; find the Mom column
    mom_col = next(c for c in df.columns if c.strip() == "Mom")
    return (df[mom_col].astype(float) / 100.0).rename("UMD_KF")


def spmo_synth_returns_from_cache() -> pd.Series:
    """SPMO synth: SPYSIM + 0.60 * UMD_KF - 35bps/y."""
    spy = load_testfolio_series("SPYSIM").pct_change().dropna()
    umd = _load_umd_kf_returns()
    return momentum_synth_returns(spy, umd_factor_returns=umd, capture_coef=0.60, expense_annual=0.0035)


def idmo_synth_returns_from_cache() -> pd.Series:
    """IDMO synth: VEASIM + 0.60 * UMD_KF - 60bps/y. INCOMPLETE - US UMD proxy for intl."""
    vea = load_testfolio_series("VEASIM").pct_change().dropna()
    umd = _load_umd_kf_returns()
    return momentum_synth_returns(vea, umd_factor_returns=umd, capture_coef=0.60, expense_annual=0.0060)


def rsst_synth_returns(
    spy_returns: pd.Series,
    kmlm_returns: pd.Series,
    expense_annual: float = 0.0060,
) -> pd.Series:
    """Return Stacked US + MF (RSST) synth: 100% S&P + 100% MF - expense.

    INCOMPLETE: real RSST uses Newfound/ReSolve trend MF engine, not KFA
    MLM Index. Engine differs. Real RSST inception 2023-09. Long-history
    backtest using KMLMSIM as MF proxy will track imperfectly.

    Citation: ReSolve/Newfound Return Stacked methodology (2023);
    [risk_parity, ch.5] Carlson cap-efficient stacking.
    """
    daily_expense = _annual_drag_to_daily(expense_annual)
    aligned = pd.concat({"spy": spy_returns, "kmlm": kmlm_returns}, axis=1).dropna()
    return aligned["spy"] + aligned["kmlm"] - daily_expense


def rsst_synth_returns_from_cache() -> pd.Series:
    """RSST synth from cache."""
    spy = load_testfolio_series("SPYSIM").pct_change().dropna()
    kmlm = load_testfolio_series("KMLMSIM").pct_change().dropna()
    return rsst_synth_returns(spy, kmlm)


def dbmf_returns_from_cache() -> pd.Series:
    """DBMFSIM daily returns from cache: 1999+, 26y. Direct testfolio synth.

    Citation: testfolio extracts DBMFSIM as iMGP DBi Managed Futures
    proxy following SG CTA Index methodology.
    """
    return load_testfolio_series("DBMFSIM").pct_change().dropna()


def cta_simplify_proxy_returns(scaling: float = 1.0) -> pd.Series:
    """CTA Simplify proxy via KMLMSIM - INCOMPLETE for real CTA Simplify.

    Real CTA Simplify uses Altis Partners multi-strategy engine (trend +
    carry + mean-reversion + risk-off). KMLMSIM is single-strategy (KFA
    MLM rules-based trend). This proxy is KMLMSIM scaled by `scaling`
    (default 1.0 = pure KMLMSIM passthrough).

    Use only as DIAGNOSTIC in iter 039 MF sleeve sensitivity, with explicit
    INCOMPLETE caveat in final_report.md.

    Citation: Simplify Asset Mgmt CTA prospectus + Altis Partners docs.
    """
    kmlm = load_testfolio_series("KMLMSIM").pct_change().dropna()
    return kmlm * scaling
