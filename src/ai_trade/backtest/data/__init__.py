"""Data sources for backtesting.

Phase 2 initial: `yfinance` + Wikipedia scrape — free, survivorship-biased,
documented. Later adapters (Tiingo, EOD Historical, Norgate, cTrader
historical) plug into the same contract so the engine stays agnostic.

See ROADMAP.md §"Two-stage backtest" and README.md §"Clenow universe and
survivorship bias" for why this initial choice is intentional.
"""

from ai_trade.backtest.data.br_tickers import (
    IBRX100_TICKERS,
    SECTOR_MAP,
    UniverseConfig,
    b3_calendar,
    get_universe_on,
    sector_of,
)
from ai_trade.backtest.data.yfinance_source import YFinanceSource
from ai_trade.backtest.data.wikipedia_spx import WikipediaSPX, constituents_on

__all__ = [
    "IBRX100_TICKERS",
    "SECTOR_MAP",
    "UniverseConfig",
    "WikipediaSPX",
    "YFinanceSource",
    "b3_calendar",
    "constituents_on",
    "get_universe_on",
    "sector_of",
]
