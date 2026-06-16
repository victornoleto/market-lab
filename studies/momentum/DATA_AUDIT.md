# Momentum Data Audit

Status: Postgres-backed yfinance cache audit for `studies/momentum/`.

Database: `local Postgres yfinance cache`

## Database Coverage

| country | asset_class | n_tickers | first_date | last_date | n_active | n_with_error |
|---|---|---|---|---|---|---|
| br | etf | 27 | 2007-01-29 | 2026-06-15 | 26 | 1 |
| br | stock | 279 | 2000-01-03 | 2026-06-15 | 279 | 0 |
| global | crypto | 12 | 2014-09-17 | 2026-06-16 | 12 | 0 |
| us | etf | 5348 | 1986-04-03 | 2026-06-15 | 5341 | 7 |
| us | stock | 7438 | 1962-01-02 | 2026-06-15 | 7136 | 302 |

## Universe Filter Coverage

| universe | raw_symbols | loaded_symbols | passed_filter | start | end | filter_keys |
|---|---|---|---|---|---|---|
| us_stocks | 7136 | 7136 | 2301 | 2000-01-03 | 2026-06-15 | us_stock |

## Caveat

The local cache accelerates tests, but yfinance/current-universe data remain screen-only until point-in-time membership, delisted symbols and corporate actions are audited `[advances_fin_ml, p.208-211]`.
