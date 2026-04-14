"""Data sources for backtesting.

Phase 2 initial: `yfinance` + Wikipedia scrape — free, survivorship-biased,
documented. Later adapters (Tiingo, EOD Historical, Norgate, cTrader
historical) plug into the same contract so the engine stays agnostic.

See ROADMAP.md §"Backtest em duas etapas" and README.md §"Universo Clenow e
survivorship bias" for why this initial choice is intentional.
"""

from ai_trade.backtest.data.yfinance_source import YFinanceSource
from ai_trade.backtest.data.wikipedia_spx import WikipediaSPX, constituents_on

__all__ = ["YFinanceSource", "WikipediaSPX", "constituents_on"]
