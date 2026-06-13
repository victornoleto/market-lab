# HAA Data Audit

Status: data-readiness audit for `studies/haa_hybrid_asset_allocation/`.

The Tiingo cache is the preferred source for `only_stocks` and `stocks_plus_etfs`, because yfinance/current-universe stock tests carry survivorship bias [advances_fin_ml, p.208-211]. Testfol.io is the preferred source only for canonical long-history ETF reproduction.

| Item | Value |
|---|---|
| tiingo_manifest_exists | True |
| tiingo_prices_dir_exists | False |
| tiingo_manifest_count | 1753 |
| tiingo_asset_classes | {'crypto': 10, 'equity': 1669, 'etf': 62, 'forex': 12} |
| tiingo_parquet_count | 0 |
| canonical_haa_tiingo_missing | ['BIL', 'DBC', 'IEF', 'IWM', 'SPY', 'TIP', 'TLT', 'VEA', 'VNQ', 'VWO'] |
| testfolio_cache_exists | True |

## Interpretation

If `tiingo_parquet_count` is `0`, restore `data/tiingo/daily/prices/*.parquet` from the subscription-era backup before running stock or ETF Tiingo variants. The committed manifest alone is not enough for a backtest.
