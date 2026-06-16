# yfinance Postgres Sync

Local cache for daily yfinance OHLCV in Postgres. This is meant to speed up
momentum screens and backtests by reading prices locally instead of calling
yfinance repeatedly.

## Data Policy

- BR stocks come from `data/yfinance/br.txt`.
- US stocks/ETFs come from current Nasdaq Trader symbol directories.
- Crypto uses a small curated USD-quoted list and `country='global'`.
- `country` means listing/data market (`us`, `br`, `global`), not issuer legal domicile.
- yfinance/current-universe data is research-only because delisted/PIT membership is not audited `[advances_fin_ml, p.208-211]`.

## Setup

Create a local database named `stocks`, then copy `.env.example` to `.env` and
adjust:

```bash
YFINANCE_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/stocks
```

## Commands

List the resolved BR universe without touching Postgres:

```bash
uv run python data/yfinance/sync.py --universe br --list-only
```

Smoke sync 5 BR tickers:

```bash
uv run python data/yfinance/sync.py --universe br-stocks --limit 5 --period max
```

Initial full sync:

```bash
uv run python data/yfinance/sync.py --universe all --period max
```

Incremental maintenance sync:

```bash
uv run python data/yfinance/sync.py --universe all --incremental
```

US-only broad universe:

```bash
uv run python data/yfinance/sync.py --universe us --period max
```

## Tables

`yf_tickers` stores ticker metadata:

- `yf_symbol`
- `asset_class`: `stock`, `etf`, `crypto`
- `country`: `us`, `br`, `global`
- `first_date`, `last_date`, `last_synced_at`, `last_error`

`yf_daily_prices` stores daily bars:

- primary key: `(ticker_id, date)`
- OHLC, `adj_close`, `volume`, `dividends`, `stock_splits`

Indexes are created for ticker-range and date cross-section reads:

- `(ticker_id, date)` primary key
- `(date, ticker_id) INCLUDE (adj_close, close, volume)`
- `(ticker_id, date DESC)`
- BRIN on `date`
- `(country, asset_class, active)` on `yf_tickers`

## Example Query

```sql
SELECT p.date, t.yf_symbol, p.adj_close
FROM yf_daily_prices p
JOIN yf_tickers t ON t.id = p.ticker_id
WHERE t.country = 'br'
  AND t.asset_class = 'stock'
  AND p.date >= DATE '2020-01-01'
ORDER BY p.date, t.yf_symbol;
```
