"""Data layer for the RSC evolution sub-study.

Extends the discussion sleeve matrix with the pre-registered new sleeves
(PLAN.md): RSBTSIM / RSSBSIM synthetic stacked proxies and the unbundled
QQQSIM diversifier. Financing convention is identical to the RSST tracking
proxy: weighted returns minus 100% notional of (CASHX + 200bps/yr)
`[risk_parity, ch.5]`, `[leverage_for_the_long_run, p.13]`.

Long-window (1988+) variants swap the MF blend for KMLM-only, mirroring the
repo's KMLM-only long-window lens (DBMFSIM starts in 2000).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from studies.return_stacked_core.discussion import discussion_data as dd

EVO_DIR = Path(__file__).resolve().parent
TABLES_DIR = EVO_DIR / "tables"

FIN_DAILY = dd.FINANCING_SPREAD_ANNUAL / dd.TRADING_DAYS

# Canonical benchmark (discussion/tables/ablations_primary.csv row A0).
CORE_WEIGHTS = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}
CORE_CAGR = 0.125241
CORE_MDD = -0.307605
CORE_SHARPE = 0.846870

MDD_CAP = -0.30
C2_PRIMARY = CORE_CAGR + 0.0075
START_DATES = [f"{y}-01-01" for y in range(2000, 2016, 2)]  # 8, as s04


def _financed_stack(legs: pd.DataFrame, weights: dict[str, float], cashx: pd.Series) -> pd.Series:
    """Stacked-sleeve daily returns: sum(w*leg) - (CASHX + spread) financing."""
    out = sum(w * legs[c] for c, w in weights.items())
    return out - (cashx + FIN_DAILY)


def load_primary_matrix() -> pd.DataFrame:
    """Daily returns 2000-01-04..2026-05-21 with the evolution sleeve set.

    Columns: GDESIM, RSSTSIM, ZROZSIM (core) + RSBTSIM, RSSBSIM, GLDSIM,
    KMLMSIM, QQQSIM (new) + SPYSIM, IEFSIM, CASHX, MFBLEND (helpers).
    """
    base = dd.load_primary_returns()
    qqq = dd.load_cache_returns(["QQQSIM"])
    out = base.join(qqq, how="left")
    out["RSBTSIM"] = _financed_stack(
        out, {"IEFSIM": 1.0, "MFBLEND": 1.0}, out["CASHX"]
    )
    out["RSSBSIM"] = _financed_stack(
        out, {"SPYSIM": 1.0, "IEFSIM": 1.0}, out["CASHX"]
    )
    return out.loc[dd.PRIMARY_START : dd.PRIMARY_END]


def load_longwindow_matrix() -> pd.DataFrame:
    """Daily returns 1988+ diagnostic matrix, KMLM-only MF sleeve.

    RSST88/RSBT88 use 100% KMLMSIM as the trend leg (DBMFSIM unavailable
    pre-2000); GDESIM comes from the remote Testfol.io pull (1968+).
    LOW-fidelity lens: KMLM-only is a single-manager proxy of the MF sleeve.
    """
    cache = dd.load_cache_returns(
        ["SPYSIM", "GLDSIM", "ZROZSIM", "IEFSIM", "CASHX", "QQQSIM"]
    )
    remote = dd.load_remote_returns(["GDESIM", "KMLMSIM"])
    out = cache.join(remote, how="left")
    out["RSST88"] = _financed_stack(
        out, {"SPYSIM": 1.0, "KMLMSIM": 1.0}, out["CASHX"]
    )
    out["RSBT88"] = _financed_stack(
        out, {"IEFSIM": 1.0, "KMLMSIM": 1.0}, out["CASHX"]
    )
    out = out.loc["1988-01-04" : dd.PRIMARY_END]
    return out
