"""Brazilian equity universe + B3 trading calendar for Strategy D.

This module provides:

1. ``IBRX100_TICKERS``: hand-curated list of ~100 tickers with ``.SA`` suffix,
   approximating the B3 IBrX-100 composition as of 2026-04. Source URL logged
   below; rebuild when composition shifts (quadrimestral B3 rebalance).

2. ``SECTOR_MAP``: coarse GICS-style sector mapping per ticker. Used by the
   monthly ranking strategies to enforce sector concentration caps
   `[stocks_on_the_move, p.229-230]` — avoids the IBOV concentration trap
   where 3 banks + 2 commodity giants dominate ~50% of the index.

3. ``b3_calendar``: list of B3 trading days between two dates. Wraps
   ``holidays.Brazil(subdiv='SP')`` and adds the four B3-specific closures
   that are NOT federal holidays: Carnaval Monday/Tuesday, Corpus Christi,
   and (historically, through 2019) the Christmas/New Year Eves. This is
   cheaper and more transparent than pulling ``pandas_market_calendars``.

4. ``get_universe_on``: dynamic universe filter — returns the top N tickers
   from ``IBRX100_TICKERS`` whose median daily (close × volume) over a
   lookback exceeds a threshold. Serves as the IBrX-100 point-in-time proxy
   while we skip scraping the B3 PDFs.

Strategy D relies on this as the universe source; do not import yfinance or
any broker client here — this module is purely declarative/config + a bit of
calendar math.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd
from dateutil.easter import easter

import holidays


# ---------------------------------------------------------------------------
# IBrX-100 proxy (B3 top ~100 by free-float liquidity, as of 2026-04)
# ---------------------------------------------------------------------------
# Composition pulled from B3 public data (Carteira Teórica IBrX-100 vigente
# em 2026-04). Composition rotates quadrimestrally (Jan / May / Sep); when a
# rebalance shifts the list, update here and re-run Strategy D backtests.
# This is a STATIC snapshot — for strict point-in-time, see Phase D-1.6 proxy
# that rebuilds the universe each month from actual volume data.
#
# Source: https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-amplos/ibrx-100.htm
#
# Tickers use the yfinance ``.SA`` suffix.
IBRX100_TICKERS: list[str] = [
    # Top-30 by market cap (most liquid, tight spreads ~15 bps)
    "PETR4.SA", "PETR3.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA",
    "BBAS3.SA", "B3SA3.SA", "WEGE3.SA", "ABEV3.SA", "ITSA4.SA",
    "SUZB3.SA", "RENT3.SA", "RAIL3.SA", "EQTL3.SA", "PRIO3.SA",
    "UGPA3.SA", "BBSE3.SA", "RDOR3.SA", "HAPV3.SA", "ELET3.SA",
    "ELET6.SA", "KLBN11.SA", "RADL3.SA", "VIVT3.SA", "SBSP3.SA",
    "EMBR3.SA", "CMIG4.SA", "GGBR4.SA", "LREN3.SA", "ASAI3.SA",
    # Next 30
    "CPFE3.SA", "ENEV3.SA", "NTCO3.SA", "CYRE3.SA", "BRFS3.SA",
    "MGLU3.SA", "CCRO3.SA", "TOTS3.SA", "SANB11.SA", "CSAN3.SA",
    "HYPE3.SA", "RAIZ4.SA", "CPLE6.SA", "BRAP4.SA", "FLRY3.SA",
    "GOAU4.SA", "MULT3.SA", "CVCB3.SA", "ENGI11.SA", "EGIE3.SA",
    "TAEE11.SA", "BPAC11.SA", "CXSE3.SA", "ARZZ3.SA", "SMFT3.SA",
    "VIVA3.SA", "YDUQ3.SA", "STBP3.SA", "AURE3.SA", "COGN3.SA",
    # Remaining 40 (smaller mid-caps, spreads 20-40 bps)
    "TIMS3.SA", "JBSS3.SA", "BEEF3.SA", "MRFG3.SA", "USIM5.SA",
    "CSNA3.SA", "GOLL4.SA", "AZUL4.SA", "EZTC3.SA", "MRVE3.SA",
    "QUAL3.SA", "ALPA4.SA", "PETZ3.SA", "VBBR3.SA", "TRPL4.SA",
    "KLBN4.SA", "POSI3.SA", "LWSA3.SA", "MOVI3.SA", "ECOR3.SA",
    "DIRR3.SA", "SMTO3.SA", "SLCE3.SA", "SOMA3.SA", "IGTI11.SA",
    "BRKM5.SA", "CEAB3.SA", "GRND3.SA", "PCAR3.SA", "ALOS3.SA",
    "IFCM3.SA", "INTB3.SA", "TEND3.SA", "SRNA3.SA", "MDIA3.SA",
    "SAPR11.SA", "TUPY3.SA", "RECV3.SA", "ONCO3.SA", "ANIM3.SA",
]


# ---------------------------------------------------------------------------
# Sector map — coarse GICS-style. Used for sector concentration caps.
# ---------------------------------------------------------------------------
# `[stocks_on_the_move, p.229-230]`: 5-6 positions "dependency on luck";
# recommends 20-30 + diversification. In the IBOV/IBrX-100, banks + commodities
# dominate, so a cap per sector is the natural diversifier.
SECTOR_MAP: dict[str, str] = {
    # Oil & Gas
    "PETR3.SA": "Energy", "PETR4.SA": "Energy", "PRIO3.SA": "Energy",
    "RAIZ4.SA": "Energy", "VBBR3.SA": "Energy", "RECV3.SA": "Energy",
    "UGPA3.SA": "Energy", "CSAN3.SA": "Energy", "ENEV3.SA": "Utilities",
    # Mining / Metals & Paper
    "VALE3.SA": "Materials", "SUZB3.SA": "Materials", "KLBN11.SA": "Materials",
    "KLBN4.SA": "Materials", "GGBR4.SA": "Materials", "GOAU4.SA": "Materials",
    "USIM5.SA": "Materials", "CSNA3.SA": "Materials", "BRAP4.SA": "Materials",
    "BRKM5.SA": "Materials",
    # Banks / Financials
    "ITUB4.SA": "Financials", "BBDC4.SA": "Financials", "BBAS3.SA": "Financials",
    "ITSA4.SA": "Financials", "SANB11.SA": "Financials", "BPAC11.SA": "Financials",
    "B3SA3.SA": "Financials", "BBSE3.SA": "Financials", "CXSE3.SA": "Financials",
    # Utilities
    "ELET3.SA": "Utilities", "ELET6.SA": "Utilities", "EQTL3.SA": "Utilities",
    "CPFE3.SA": "Utilities", "CMIG4.SA": "Utilities", "SBSP3.SA": "Utilities",
    "CPLE6.SA": "Utilities", "ENGI11.SA": "Utilities", "EGIE3.SA": "Utilities",
    "TAEE11.SA": "Utilities", "AURE3.SA": "Utilities", "TRPL4.SA": "Utilities",
    "SAPR11.SA": "Utilities",
    # Consumer Staples (Food/Beverage)
    "ABEV3.SA": "Consumer Staples", "JBSS3.SA": "Consumer Staples",
    "BEEF3.SA": "Consumer Staples", "MRFG3.SA": "Consumer Staples",
    "BRFS3.SA": "Consumer Staples", "MDIA3.SA": "Consumer Staples",
    "SMTO3.SA": "Consumer Staples", "SLCE3.SA": "Consumer Staples",
    # Consumer Discretionary (retail, apparel, travel)
    "LREN3.SA": "Consumer Disc.", "MGLU3.SA": "Consumer Disc.",
    "ASAI3.SA": "Consumer Disc.", "NTCO3.SA": "Consumer Disc.",
    "SMFT3.SA": "Consumer Disc.", "ARZZ3.SA": "Consumer Disc.",
    "ALPA4.SA": "Consumer Disc.", "VIVA3.SA": "Consumer Disc.",
    "SOMA3.SA": "Consumer Disc.", "CEAB3.SA": "Consumer Disc.",
    "GRND3.SA": "Consumer Disc.", "PCAR3.SA": "Consumer Disc.",
    "CVCB3.SA": "Consumer Disc.", "AZUL4.SA": "Consumer Disc.",
    "GOLL4.SA": "Consumer Disc.", "RENT3.SA": "Consumer Disc.",
    "MOVI3.SA": "Consumer Disc.", "PETZ3.SA": "Consumer Disc.",
    "COGN3.SA": "Consumer Disc.", "YDUQ3.SA": "Consumer Disc.",
    "ANIM3.SA": "Consumer Disc.",
    # Healthcare
    "RDOR3.SA": "Health Care", "HAPV3.SA": "Health Care",
    "FLRY3.SA": "Health Care", "HYPE3.SA": "Health Care",
    "RADL3.SA": "Health Care", "QUAL3.SA": "Health Care",
    "ONCO3.SA": "Health Care",
    # Industrials
    "WEGE3.SA": "Industrials", "EMBR3.SA": "Industrials",
    "RAIL3.SA": "Industrials", "CCRO3.SA": "Industrials",
    "ECOR3.SA": "Industrials", "STBP3.SA": "Industrials",
    "TUPY3.SA": "Industrials", "POSI3.SA": "Industrials",
    # Telecom
    "VIVT3.SA": "Telecom", "TIMS3.SA": "Telecom",
    # IT / Software
    "TOTS3.SA": "IT", "LWSA3.SA": "IT", "IFCM3.SA": "IT",
    "INTB3.SA": "IT", "SRNA3.SA": "IT",
    # Real Estate
    "CYRE3.SA": "Real Estate", "EZTC3.SA": "Real Estate",
    "MRVE3.SA": "Real Estate", "MULT3.SA": "Real Estate",
    "ALOS3.SA": "Real Estate", "IGTI11.SA": "Real Estate",
    "TEND3.SA": "Real Estate", "DIRR3.SA": "Real Estate",
}


def sector_of(ticker: str) -> str:
    """Return the sector of ``ticker`` (``'Unknown'`` if unmapped)."""
    return SECTOR_MAP.get(ticker, "Unknown")


# ---------------------------------------------------------------------------
# B3 trading calendar
# ---------------------------------------------------------------------------
def _b3_extra_closures(year: int) -> set[date]:
    """B3-specific closures that ``holidays.Brazil(subdiv='SP')`` misses.

    These are not federal or state legal holidays, but the exchange is closed:

    * Carnaval Monday + Tuesday — the 48 and 47 days before Easter
      (historically the "segunda gorda" + "terça gorda").
    * Corpus Christi — 60 days after Easter.
    * Good Friday (Sexta-Feira Santa) — already in the holidays library, but
      listed here for clarity.
    * Christmas Eve (Dec 24) + New Year's Eve (Dec 31) — B3 operated half-day
      until 2019; from 2020 onwards these are full closures. Added from 2020.
    """
    e = easter(year)
    closures: set[date] = {
        e - timedelta(days=48),   # Carnaval Monday
        e - timedelta(days=47),   # Carnaval Tuesday
        e + timedelta(days=60),   # Corpus Christi
    }
    if year >= 2020:
        closures.add(date(year, 12, 24))
        closures.add(date(year, 12, 31))
    return closures


def b3_calendar(start: date, end: date) -> pd.DatetimeIndex:
    """Return B3 trading days in ``[start, end]`` inclusive.

    Drops weekends + ``holidays.Brazil(subdiv='SP')`` + B3-specific closures
    (Carnaval Mon+Tue, Corpus Christi, and the Christmas/New Year eves from
    2020 onwards).
    """
    if start > end:
        return pd.DatetimeIndex([])

    br_sp = holidays.Brazil(subdiv="SP", years=range(start.year, end.year + 1))
    extra: set[date] = set()
    for y in range(start.year, end.year + 1):
        extra.update(_b3_extra_closures(y))

    days = pd.bdate_range(start=start, end=end)  # weekdays only
    mask = [
        (d.date() not in br_sp) and (d.date() not in extra)
        for d in days
    ]
    return days[mask]


# ---------------------------------------------------------------------------
# Dynamic universe (IBrX-100 proxy by rolling liquidity)
# ---------------------------------------------------------------------------
@dataclass
class UniverseConfig:
    """Parameters for :func:`get_universe_on`.

    Attributes
    ----------
    lookback_days
        Rolling window to compute median daily notional value (close × volume).
    min_median_notional_brl
        Minimum R$ daily notional for inclusion. Default R$5M/day matches the
        IBrX-100 documented floor for effective tradability.
    n_top
        Cap on the number of tickers returned. Default 100 = IBrX-100 size.
    """

    lookback_days: int = 60
    min_median_notional_brl: float = 5_000_000.0
    n_top: int = 100


def get_universe_on(
    as_of: date,
    ohlcv_all: dict[str, pd.DataFrame],
    config: UniverseConfig | None = None,
) -> list[str]:
    """Return the liquidity-filtered universe as of ``as_of``.

    For each ticker in ``ohlcv_all``, computes the median of
    ``close × volume`` over the last ``lookback_days`` trading days ending
    at ``as_of`` (inclusive). Ticks below ``min_median_notional_brl`` are
    dropped; the survivors are ranked descending by median notional and the
    top ``n_top`` are returned.

    Note: this is the **proxy** for point-in-time IBrX-100 membership —
    strictly, the index is rebalanced quadrimestrally from B3 PDFs. The
    proxy here eliminates survivorship at the *index level* (we don't include
    a ticker that wasn't liquid yet) but is still survivorship-biased at the
    yfinance level (delisted tickers are absent from ``ohlcv_all``).
    """
    cfg = config or UniverseConfig()
    as_of_ts = pd.Timestamp(as_of)
    window_start = as_of_ts - pd.Timedelta(days=cfg.lookback_days * 2)

    scored: list[tuple[str, float]] = []
    for ticker, df in ohlcv_all.items():
        if df.empty or "close" not in df.columns or "volume" not in df.columns:
            continue
        window = df.loc[
            (df.index >= window_start) & (df.index <= as_of_ts)
        ]
        if len(window) < max(5, cfg.lookback_days // 4):
            continue
        notional = window["close"] * window["volume"]
        median_notional = float(notional.median())
        if median_notional < cfg.min_median_notional_brl:
            continue
        scored.append((ticker, median_notional))

    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [ticker for ticker, _ in scored[: cfg.n_top]]


__all__ = [
    "IBRX100_TICKERS",
    "SECTOR_MAP",
    "UniverseConfig",
    "b3_calendar",
    "get_universe_on",
    "sector_of",
]
