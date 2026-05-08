"""market_lab.backtest.screener — multi-asset universe screener (Phase 3 A2).

Pure functions + a thin orchestrator. Inputs: a TiingoStorage instance and a
list of (ticker, asset_class) candidates. Outputs: a DataFrame ranked by
mean-reversion-favorability and liquidity.

Citations
---------
- Hurst exponent via structure function: ``[algo_trading_chan, p.44-46, ch.2]``
  (Chan 2013 — formula ``<|z(t+τ)-z(t)|^2> ~ τ^{2H}``).
- ATR(20) on daily bars: ``[stocks_on_the_move, p.88]`` (Clenow).
- Dollar-volume liquidity rank: ``[stocks_on_the_move, p.81]`` (Clenow uses
  it as a tradability filter on the S&P 500).
- Annualized realized vol from log returns: ``[volatility_trading]`` (Sinclair).
"""

from __future__ import annotations

from .hurst import hurst_exponent
from .metrics import atr_pct, dollar_volume, realized_vol_annualized
from .universe import screen_universe

__all__ = [
    "atr_pct",
    "dollar_volume",
    "hurst_exponent",
    "realized_vol_annualized",
    "screen_universe",
]
