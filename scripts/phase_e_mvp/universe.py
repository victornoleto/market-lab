"""Strategy E universe — SP500 top-200 + IBrX-100 = ~300 tickers.

US segment: top 200 of the S&P 500 by approximate market cap as of
2026-04 (hand-curated snapshot; rebuild periodically). Covers ~80% of
S&P 500 market cap — the liquid, index-tradable slice. yfinance fetches
these without suffix.

BR segment: reuses ``IBRX100_TICKERS`` from
``ai_trade.backtest.data.br_tickers`` (``.SA`` suffix). ~100 tickers.

Per-ticker market (``"US"`` or ``"BR"``) is exposed via
:func:`market_of` so the cost/tax model can select the right jurisdiction.

Survivorship bias caveat (documented in every Strategy E report):
yfinance does not return delisted tickers. Both sets are current-member
snapshots; the liquidity proxy in ``get_universe_on`` filters dynamically
by volume, which mitigates (but doesn't eliminate) the bias.
"""

from __future__ import annotations

from ai_trade.backtest.data.br_tickers import IBRX100_TICKERS

# ---------------------------------------------------------------------------
# SP500 top-200 by market cap (2026-04 snapshot)
# ---------------------------------------------------------------------------
# Source: S&P Dow Jones Indices + Yahoo finance market cap ranking, top 200.
# Tickers without suffix — yfinance defaults to NYSE/NASDAQ.
# Rebuild when SPX composition shifts meaningfully (rare for top-200).
SP500_TOP200: list[str] = [
    # --- Top 50 (mega caps) ---
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "UNH",
    "LLY", "JPM", "V", "XOM", "JNJ", "WMT", "MA", "PG", "AVGO", "HD",
    "CVX", "MRK", "ABBV", "COST", "PEP", "ADBE", "KO", "CSCO", "CRM", "MCD",
    "BAC", "TMO", "PFE", "ACN", "LIN", "ABT", "DHR", "NFLX", "CMCSA", "WFC",
    "AMD", "ORCL", "DIS", "TXN", "PM", "VZ", "INTC", "COP", "NEE", "AMGN",
    # --- 51-100 ---
    "QCOM", "HON", "IBM", "LOW", "RTX", "UNP", "INTU", "NKE", "SPGI", "GE",
    "CAT", "SBUX", "ISRG", "BA", "BMY", "GS", "DE", "BKNG", "ELV", "MDT",
    "T", "LMT", "AXP", "BLK", "PLD", "SYK", "MMC", "MO", "AMT", "GILD",
    "ADP", "CI", "CB", "TMUS", "REGN", "VRTX", "ZTS", "SO", "PYPL", "NOW",
    "CVS", "SCHW", "ADI", "MU", "FI", "PANW", "DUK", "BSX", "ETN", "EQIX",
    # --- 101-150 ---
    "AON", "CL", "ICE", "PGR", "SHW", "ITW", "TJX", "FDX", "CME", "CSX",
    "SLB", "NSC", "MMM", "CDNS", "APD", "WM", "USB", "PSA", "NOC", "TRV",
    "EOG", "MCK", "ADSK", "MRNA", "MPC", "F", "GM", "MCO", "GIS", "WBA",
    "COF", "ORLY", "EMR", "AEP", "AFL", "HUM", "PSX", "KLAC", "HCA", "LRCX",
    "SRE", "CTAS", "TGT", "DG", "EW", "OXY", "ROP", "D", "MAR", "ALL",
    # --- 151-200 ---
    "AZO", "PCAR", "MSI", "FIS", "MET", "PAYX", "PRU", "SPG", "NEM", "BDX",
    "TEL", "TT", "EXC", "BK", "YUM", "HSY", "KHC", "MNST", "WMB", "VRSK",
    "A", "CARR", "MCHP", "KMB", "TFC", "IQV", "LHX", "AIG", "CNC", "DOW",
    "IDXX", "EA", "DVN", "PEG", "SYY", "AJG", "ROST", "ODFL", "O", "ON",
    "AME", "FTV", "KR", "DLR", "CMG", "BIIB", "RSG", "FERG", "AMP", "STZ",
]

US_TICKERS = SP500_TOP200
BR_TICKERS = IBRX100_TICKERS  # re-export from br_tickers

# Combined — plain list, no de-dup needed (US and BR tickers don't collide).
MULTIMARKET_TICKERS: list[str] = US_TICKERS + BR_TICKERS

_US_SET = set(US_TICKERS)
_BR_SET = set(BR_TICKERS)


def market_of(ticker: str) -> str:
    """Return ``"US"`` or ``"BR"`` for a given ticker, else ``"UNKNOWN"``."""
    if ticker in _US_SET:
        return "US"
    if ticker in _BR_SET:
        return "BR"
    # Heuristic fallback — ``.SA`` tickers are Bovespa.
    if ticker.endswith(".SA"):
        return "BR"
    return "UNKNOWN"


__all__ = [
    "BR_TICKERS",
    "MULTIMARKET_TICKERS",
    "SP500_TOP200",
    "US_TICKERS",
    "market_of",
]
