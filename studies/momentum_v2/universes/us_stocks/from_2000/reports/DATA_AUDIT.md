# Data Audit — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

## Database coverage

| country | asset_class | n_tickers | first_date | last_date | n_active | n_with_error |
|---|---|---|---|---|---|---|
| br | etf | 27 | 2007-01-29 | 2026-06-15 | 26 | 1 |
| br | stock | 279 | 2000-01-03 | 2026-06-15 | 279 | 0 |
| global | crypto | 12 | 2014-09-17 | 2026-06-16 | 12 | 0 |
| us | etf | 5348 | 1986-04-03 | 2026-06-15 | 5341 | 7 |
| us | stock | 7438 | 1962-01-02 | 2026-06-15 | 7136 | 302 |

## Filter attrition

- Start: `2000-01-01`
- Tickers loaded: `7136` -> passed filters: `2301` (32.2%).
- Expanding-universe caveat: filters (min history) plus sparse early coverage mean the tradable set in early years is much smaller than today; cross-era CAGR comparisons are affected.

### Top rejection reasons

| reason | n |
|---|---|
| liquidity | 1509 |
| history,liquidity | 1055 |
| price,liquidity | 893 |
| history,price,liquidity | 845 |
| history | 363 |
| price | 126 |
| history,price | 26 |
| liquidity,sparse | 4 |
| history,liquidity,sparse | 3 |
| history,price,liquidity,sparse | 3 |
| liquidity,stale | 2 |
| history,liquidity,sparse,stale | 2 |
