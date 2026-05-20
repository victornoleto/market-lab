"""Universe and exposure helpers for the static SPY-beater portfolio study.

The effective-exposure map is diagnostic only. It approximates economic exposure
hidden inside LETFs and stacked ETFs so reports do not confuse sleeve weight with
notional risk `[risk_parity, ch.5, p.10]`, `[leverage_for_the_long_run, p.13]`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.long_term_portfolio.run_iter import _resolve_tickers_to_returns  # noqa: E402


CORE_1986 = [
    "SPYSIM",
    "SSOSIM",
    "UPROSIM",
    "QQQSIM",
    "QLDSIM",
    "TQQQSIM",
    "TLTSIM",
    "TMFSIM",
    "ZROZSIM",
    "GLDSIM",
    "GDESIM",
    "NTSXSIM",
    "RSSBSIM",
    "IEFSIM",
    "BNDSIM",
    "CASHX",
    "VTISIM",
    "VTSIM",
    "UGLSIM",
]

MINIMAL_AGGRESSIVE = [
    "SPYSIM",
    "SSOSIM",
    "UPROSIM",
    "QQQSIM",
    "QLDSIM",
    "TQQQSIM",
    "TLTSIM",
    "ZROZSIM",
    "TMFSIM",
    "GLDSIM",
    "GDESIM",
    "KMLMSIM",
    "DBMFSIM",
    "RSSTSIM",
    "CASHX",
]

BALANCED_NO_3X = [
    "SPYSIM",
    "SSOSIM",
    "QQQSIM",
    "QLDSIM",
    "TLTSIM",
    "ZROZSIM",
    "GLDSIM",
    "GDESIM",
    "KMLMSIM",
    "DBMFSIM",
    "RSSTSIM",
    "NTSXSIM",
    "RSSBSIM",
    "CASHX",
]

LEVERED_HEDGE_CORE = [
    "SPYSIM",
    "SSOSIM",
    "UPROSIM",
    "QQQSIM",
    "QLDSIM",
    "TQQQSIM",
    "TLTSIM",
    "ZROZSIM",
    "TMFSIM",
    "GLDSIM",
    "UGLSIM",
    "GDESIM",
    "RSSTSIM",
    "CASHX",
]

LEVERED_HEDGE_NO_TMF = [ticker for ticker in LEVERED_HEDGE_CORE if ticker != "TMFSIM"]

LEAD_FAMILY_FOCUSED = [
    "SPYSIM",
    "QQQSIM",
    "QLDSIM",
    "TQQQSIM",
    "TLTSIM",
    "ZROZSIM",
    "GLDSIM",
    "UGLSIM",
    "GDESIM",
    "RSSTSIM",
    "CASHX",
]

LEAD_FAMILY_NO_3X_BOOSTER = [ticker for ticker in LEAD_FAMILY_FOCUSED if ticker != "TQQQSIM"]

CORE_BEATER_NO_MARGIN = [
    "GDESIM",
    "RSSTSIM",
    "KMLMSIM",
    "ZROZSIM",
    "SPYSIM",
    "SSOSIM",
    "UPROSIM",
    "QQQSIM",
    "QLDSIM",
    "TQQQSIM",
    "IEFSIM",
    "CASHX",
]

# Factor probe adds small/value and momentum proxies to the no-margin core-beater
# universe without changing the benchmark; factor sleeves are discovery-only
# candidates, not a mandate change `[ml_for_algo_trading, ch.4 p.82-93]`.
CORE_BEATER_FACTOR_NO_MARGIN = CORE_BEATER_NO_MARGIN + ["VBRSIM", "MTUMSIM", "EFVSIM"]

# Stacked-ETF expansion universe (B4-v2 triage). The proxies CTAPSIM, RSBTSIM,
# RSITSIM, HOLDSIM, MATESIM, ESBGSIM, GDTSIM, ALLWSIM are LOCAL composition
# proxies built in scripts/build_stacked_sim_proxies.py; they ignore fund fees
# and internal rebalancing and over-estimate CAGR by ~3-6pp vs real ETFs.
# Discovery-only triage; promote survivors to Testfol.io SIMs before any
# validation claim `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
CORE_BEATER_STACKED_EXPANSION = [
    # B4-v2 core anchors
    "GDESIM", "RSSTSIM", "ZROZSIM",
    # Alternative stacked equity + MF (substitutes/complements to RSST)
    "CTAPSIM", "RSBTSIM", "MATESIM", "HOLDSIM",
    # International stacked
    "RSITSIM", "RSSBSIM", "NTSXSIM", "NTSISIM", "NTSDSIM",
    # All-weather / inflation-protected stacked
    "ESBGSIM", "ALLWSIM", "GDTSIM",
    # Alpha sleeves
    "BTALSIM", "DBMFSIM", "KMLMSIM",
    # Treasury family
    "IEISIM", "IEFSIM",
    # Cash anchor
    "CASHX",
    # Levered Nasdaq booster (kept for cross-report comparability with prior GA_aggressive)
    "TQQQSIM",
]

STACKED_CORE = [
    "NTSXSIM",
    "GDESIM",
    "RSSTSIM",
    "RSSBSIM",
    "ZROZSIM",
    "KMLMSIM",
    "DBMFSIM",
    "CASHX",
]

GLOBAL_CORE = [
    "SPYSIM",
    "SSOSIM",
    "QQQSIM",
    "QLDSIM",
    "VEASIM",
    "VWOSIM",
    "VXUSSIM",
    "VBRSIM",
    "EFVSIM",
    "NTSXSIM",
    "NTSESIM",
    "TLTSIM",
    "ZROZSIM",
    "GLDSIM",
    "GDESIM",
    "KMLMSIM",
    "DBMFSIM",
    "RSSTSIM",
    "CASHX",
]

UNIVERSES: dict[str, list[str]] = {
    "core_1986": CORE_1986,
    "mf_1988": CORE_1986 + ["KMLMSIM", "RSSTSIM"],
    "global_1994": CORE_1986
    + ["KMLMSIM", "RSSTSIM", "NTSESIM", "VEASIM", "VWOSIM", "VXUSSIM", "EFVSIM", "VBRSIM"],
    "full_2000": CORE_1986
    + [
        "KMLMSIM",
        "RSSTSIM",
        "NTSESIM",
        "VEASIM",
        "VWOSIM",
        "VXUSSIM",
        "EFVSIM",
        "VBRSIM",
        "DBMFSIM",
    ],
    # Curated universes preserve leverage ladders (1x/2x/3x) so the optimizer can
    # discover intermediate effective leverage through weights, while removing broad
    # duplicate noise like VTISIM from focused runs `[leverage_for_the_long_run, p.13]`.
    "minimal_aggressive": MINIMAL_AGGRESSIVE,
    "balanced_no_3x": BALANCED_NO_3X,
    "levered_hedge_core": LEVERED_HEDGE_CORE,
    "levered_hedge_no_tmf": LEVERED_HEDGE_NO_TMF,
    "lead_family_focused": LEAD_FAMILY_FOCUSED,
    "lead_family_no_3x_booster": LEAD_FAMILY_NO_3X_BOOSTER,
    "core_beater_no_margin": CORE_BEATER_NO_MARGIN,
    "core_beater_factor_no_margin": CORE_BEATER_FACTOR_NO_MARGIN,
    "core_beater_stacked_expansion": CORE_BEATER_STACKED_EXPANSION,
    "stacked_core": STACKED_CORE,
    "global_core": GLOBAL_CORE,
}

B4_WEIGHTS = {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25}
CORE_35_40_25_WEIGHTS = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}

# Approximate notional exposures per $1 sleeve weight. Negative cash means embedded
# financing inside capital-efficient products.
EXPOSURE_MAP: dict[str, dict[str, float]] = {
    "SPYSIM": {"us_large_equity": 1.0},
    "SSOSIM": {"us_large_equity": 2.0},
    "UPROSIM": {"us_large_equity": 3.0},
    "QQQSIM": {"nasdaq_equity": 1.0},
    "QLDSIM": {"nasdaq_equity": 2.0},
    "TQQQSIM": {"nasdaq_equity": 3.0},
    "VTISIM": {"us_total_equity": 1.0},
    "VTSIM": {"global_equity": 1.0},
    "VEASIM": {"intl_developed_equity": 1.0},
    "VWOSIM": {"em_equity": 1.0},
    "VXUSSIM": {"intl_equity": 1.0},
    "EFVSIM": {"intl_value_equity": 1.0},
    "VBRSIM": {"us_small_value_equity": 1.0},
    "MTUMSIM": {"us_momentum_equity": 1.0},
    "TLTSIM": {"long_treasury": 1.0},
    "TMFSIM": {"long_treasury": 3.0},
    "ZROZSIM": {"zero_coupon_treasury": 1.0},
    "IEFSIM": {"intermediate_treasury": 1.0},
    "BNDSIM": {"aggregate_bond": 1.0},
    "GLDSIM": {"gold": 1.0},
    "UGLSIM": {"gold": 2.0},
    "KMLMSIM": {"managed_futures": 1.0},
    "DBMFSIM": {"managed_futures": 1.0},
    "CASHX": {"cash": 1.0},
    "NTSXSIM": {"us_large_equity": 0.9, "intermediate_treasury": 0.6, "cash": -0.5},
    "NTSESIM": {"em_equity": 0.9, "intermediate_treasury": 0.6, "cash": -0.5},
    "GDESIM": {"us_large_equity": 0.9, "gold": 0.9, "cash": -0.8},
    "RSSTSIM": {"us_large_equity": 1.0, "managed_futures": 1.0, "cash": -1.0},
    "RSSBSIM": {"global_equity": 1.0, "aggregate_bond": 1.0, "cash": -1.0},
    "NTSDSIM": {"us_large_equity": 0.9, "intl_equity": 0.6, "cash": -0.5},
    "NTSISIM": {"intl_developed_equity": 0.9, "intermediate_treasury": 0.6, "cash": -0.5},
    "IEISIM": {"intermediate_short_treasury": 1.0},
    "LTPZSIM": {"tips_long": 1.0},
    "STIPSIM": {"tips_short": 1.0},
    "GSGSIM": {"broad_commodity": 1.0},
    "BTALSIM": {"anti_beta_hedge": 1.0},
    # Local composition proxies (see scripts/build_stacked_sim_proxies.py).
    # Exposure reflects the proxy formula, not the real ETF's nominal definition.
    "CTAPSIM": {"us_large_equity": 1.0, "managed_futures": 1.0, "cash": -1.0},
    "RSBTSIM": {"intermediate_treasury": 1.0, "managed_futures": 1.0, "cash": -1.0},
    "RSITSIM": {"intl_equity": 1.0, "managed_futures": 1.0, "cash": -1.0},
    "HOLDSIM": {"us_large_equity": 0.75, "managed_futures": 0.75, "cash": -0.5},
    "MATESIM": {"us_large_equity": 1.0, "managed_futures": 1.0, "cash": -1.0},
    "ESBGSIM": {
        "us_large_equity": 0.7, "intermediate_short_treasury": 0.7,
        "gold": 0.7, "cash": -1.1,
    },
    "GDTSIM": {"tips_short": 0.9, "gold": 0.9, "cash": -0.8},
    "ALLWSIM": {
        "broad_commodity": 0.37, "global_equity": 0.42,
        "aggregate_bond": 0.72, "tips_long": 0.32, "cash": -0.83,
    },
}


def load_universe_returns(universe: str) -> pd.DataFrame:
    """Load raw daily returns for a named universe and aligned benchmarks."""
    if universe not in UNIVERSES:
        raise KeyError(f"unknown universe {universe!r}; choose from {list(UNIVERSES)}")
    tickers = list(dict.fromkeys(UNIVERSES[universe] + ["SPYSIM", "QQQSIM"]))
    returns = _resolve_tickers_to_returns(tickers)
    return pd.concat(returns, axis=1, sort=True).dropna(how="all").sort_index()


def common_window(frame: pd.DataFrame, tickers: list[str]) -> tuple[pd.Timestamp, pd.Timestamp, int]:
    """Return common non-null window for tickers."""
    aligned = frame[tickers].dropna()
    if aligned.empty:
        raise ValueError(f"no common data for {tickers}")
    return aligned.index[0], aligned.index[-1], len(aligned)


def portfolio_effective_exposure(weights: dict[str, float]) -> dict[str, float]:
    """Approximate economic exposure by family for a portfolio."""
    exposures: dict[str, float] = {}
    for ticker, weight in weights.items():
        for family, coef in EXPOSURE_MAP.get(ticker, {"unknown": 1.0}).items():
            exposures[family] = exposures.get(family, 0.0) + weight * coef
    return dict(sorted(exposures.items()))


def equal_weight_for_universe(universe: str) -> dict[str, float]:
    tickers = UNIVERSES[universe]
    weight = 1.0 / len(tickers)
    return {ticker: weight for ticker in tickers}


def has_b4(universe: str) -> bool:
    return set(B4_WEIGHTS).issubset(set(UNIVERSES[universe]))
