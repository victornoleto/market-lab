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

from studies.long_term_portfolio.run_iter import _resolve_tickers_to_returns


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
}

B4_WEIGHTS = {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25}

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
