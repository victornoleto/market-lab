# Momentum 13612 Universe Data Audit

Status: data-readiness audit for `studies/momentum_13612_universes/`.

Tiingo parquets are preferred for US stock/ETF historical screens when restored. yfinance is explicit screen-only. BR stocks can use the local Postgres 1m quote database, collapsed to daily last-bar closes; corporate-action/PIT quality remains a separate audit before promotion `[advances_fin_ml, p.208-211]`.

| Item | Value |
|---|---|
| tiingo_manifest_exists | True |
| tiingo_asset_classes | {'crypto': 10, 'equity': 1669, 'etf': 62, 'forex': 12} |
| tiingo_prices_dir_exists | False |
| tiingo_parquet_count | 0 |
| us_source_effective | yfinance |
| benchmark | SPY |
| benchmark_source | yfinance |
| plots_enabled | True |
| us_stock_universe | sp500 |
| us_etf_universe | curated |
| br_stock_source | postgres |
| br_postgres_url | postgresql://***:***@localhost:5435/market_lab |
| br_postgres_table | quotes_1m |
| br_postgres_columns | {'ticker': 'ticker', 'timestamp': 'ts', 'close': 'close'} |
| br_postgres_strip_sa_suffix | True |
| br_curated_etf_count | 27 |
