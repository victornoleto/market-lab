"""FFR-aware LETF synthesis for letf_rotation_hunt.

Wraps the daily-return formula from spec §4.2 with explicit ER + spread
defaults per ticker.

Default formula:
    r_synth[t] = L × r_underlying[t] - ER/252 - (L-1) × (FFR[t] + spread/252)

Citations:
  - Gayed [leverage_for_the_long_run, p.16, footnote 22-23]: daily rebalancing
    drag and financing cost decomposition for leveraged products.
  - Testfolio defaults [data/external/README.md]: per-LETF ER sourced from
    fund prospectuses as of 2024.

Per-LETF expense ratios (spec §4.4):
  UPRO 0.91%, SSO 0.91%, TQQQ 0.86%, QLD 0.95%, SOXL 0.91%, UGL 0.95%,
  TMF 1.06%, ZROZ 0.15%, IEF 0.15%, TLT 0.15%, BIL 0.13%, EDV 0.07%.
"""
from __future__ import annotations

import pandas as pd

TRADING_DAYS_PER_YEAR = 252

# Per-LETF expense ratios (decimal, per spec §4.4).
#
# UGL note: nominal prospectus ER is 0.0095, but iter 000 v2 parity (2026-05-05)
# measured a ~2.3pp/yr CAGR drift between formula synth and real UGL over
# 2008-2026 — gold LETFs incur tracking drag beyond the canonical L*r - ER -
# (L-1)*FFR formula (intraday gold vol + smaller AUM swap costs). Bisection
# calibration on real UGL data: ER=0.0296 closes the gap to <5bp. Rounded to
# 0.030 for clarity. See iter 000 v2 SYNTH_PARITY_REPORT.md and the jornada/
# entry on the calibration. UGL synth path uses GLDSIM as underlying via
# letf_synth_by_ticker (run_iter_t0._RESYNTH_UNDERLYINGS, run_iter_t1.LETF_TESTFOLIO).
LETF_EXPENSE_RATIOS: dict[str, float] = {
    "UPRO": 0.0091,
    "SSO": 0.0091,
    "TQQQ": 0.0086,
    "QLD": 0.0095,
    "SOXL": 0.0091,
    "UGL": 0.030,    # calibrated from prospectus 0.0095 + 2.3pp empirical drag
    "TMF": 0.0106,
    "ZROZ": 0.0015,
    "IEF": 0.0015,
    "TLT": 0.0015,
    "BIL": 0.0013,
    "EDV": 0.0007,
}

# Per-LETF leverage factors
LETF_LEVERAGE: dict[str, float] = {
    "UPRO": 3.0,
    "SSO": 2.0,
    "TQQQ": 3.0,
    "QLD": 2.0,
    "SOXL": 3.0,
    "UGL": 2.0,
    "TMF": 3.0,
    "ZROZ": 1.0,
    "IEF": 1.0,
    "TLT": 1.0,
    "BIL": 1.0,
    "EDV": 1.0,
}

DEFAULT_FFR_SPREAD_ANNUAL = 0.004


def letf_synth_returns(
    underlying_returns: pd.Series,
    leverage: float,
    expense_ratio_annual: float,
    ffr_daily: pd.Series,
    ffr_spread_annual: float = DEFAULT_FFR_SPREAD_ANNUAL,
) -> pd.Series:
    """FFR-aware LETF synthesized daily returns.

    Formula per spec §4.2 [leverage_for_the_long_run, p.16, footnote 22-23]:
        r_synth[t] = L × r_underlying[t] - ER/252 - (L-1) × (FFR[t] + spread/252)

    Parameters
    ----------
    underlying_returns : pd.Series
        Daily total return of underlying (e.g. SPY for UPRO/SSO).
    leverage : float
        Leverage factor (e.g. 1.0, 2.0, 3.0). Must be > 0.
    expense_ratio_annual : float
        ER as decimal (e.g. 0.0091 for UPRO 0.91%). Must be >= 0.
    ffr_daily : pd.Series
        Daily FFR rate (decimal, daily compounded). Aligned to underlying.
    ffr_spread_annual : float
        Spread over FFR for borrow modeling (default 0.4% per spec §4.2).

    Returns
    -------
    pd.Series
        Daily synthesized LETF returns, index = intersection of inputs.

    Raises
    ------
    ValueError
        If leverage <= 0 or expense_ratio_annual < 0.
    """
    if leverage <= 0:
        raise ValueError(f"leverage must be > 0, got {leverage}")
    if expense_ratio_annual < 0:
        raise ValueError(f"expense_ratio_annual must be >= 0, got {expense_ratio_annual}")

    aligned = pd.concat({"u": underlying_returns, "ffr": ffr_daily}, axis=1, sort=False).dropna()
    er_daily = expense_ratio_annual / TRADING_DAYS_PER_YEAR
    spread_daily = ffr_spread_annual / TRADING_DAYS_PER_YEAR
    return (
        leverage * aligned["u"]
        - er_daily
        - (leverage - 1) * (aligned["ffr"] + spread_daily)
    )


def letf_synth_by_ticker(
    ticker: str,
    underlying_returns: pd.Series,
    ffr_daily: pd.Series,
) -> pd.Series:
    """Convenience: synth from ticker name (looks up ER + leverage).

    Parameters
    ----------
    ticker : str
        LETF ticker symbol (must be in LETF_EXPENSE_RATIOS).
    underlying_returns : pd.Series
        Daily total return of the underlying index.
    ffr_daily : pd.Series
        Daily FFR rate (decimal, daily compounded).

    Returns
    -------
    pd.Series
        Daily synthesized LETF returns.

    Raises
    ------
    ValueError
        If ticker is not in the known LETF_EXPENSE_RATIOS table.
    """
    if ticker not in LETF_EXPENSE_RATIOS:
        raise ValueError(
            f"Unknown LETF ticker: {ticker!r}. Add to LETF_EXPENSE_RATIOS."
        )
    return letf_synth_returns(
        underlying_returns,
        leverage=LETF_LEVERAGE[ticker],
        expense_ratio_annual=LETF_EXPENSE_RATIOS[ticker],
        ffr_daily=ffr_daily,
    )
