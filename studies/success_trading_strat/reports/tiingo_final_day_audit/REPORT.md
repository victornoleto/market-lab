# Tiingo Final-Day Coverage Audit

Generated: `2026-05-14T03:11:18`
Storage root: `data/tiingo`
Freshness threshold: `2026-05-08`

## Manifest Summary

- Tickers in manifest: `1755`
- By asset class: `{'crypto': 11, 'equity': 1669, 'etf': 74, 'forex': 25}`
- By frequency: `{'1hour': 26, 'daily': 1753}`

## Critical Coverage

- Covered: `31`
- Stale: `19`
- Missing: `0`
- Invalid: `0`

| group | ticker | status | first_dt | last_dt | bars |
|---|---:|---|---:|---:|---:|
| broad_us_etfs | `SPY` | covered | 1993-01-29T00:00:00 | 2026-05-13T00:00:00 | 8379 |
| broad_us_etfs | `IVV` | covered | 2000-05-19T00:00:00 | 2026-05-13T00:00:00 | 6534 |
| broad_us_etfs | `VOO` | covered | 2010-09-09T00:00:00 | 2026-05-13T00:00:00 | 3943 |
| broad_us_etfs | `VTI` | covered | 2001-05-31T00:00:00 | 2026-05-13T00:00:00 | 6275 |
| broad_us_etfs | `QQQ` | covered | 1999-03-10T00:00:00 | 2026-05-13T00:00:00 | 6837 |
| broad_us_etfs | `DIA` | covered | 1998-01-20T00:00:00 | 2026-05-13T00:00:00 | 7123 |
| broad_us_etfs | `IWM` | covered | 2000-05-26T00:00:00 | 2026-05-13T00:00:00 | 6529 |
| international_etfs | `EFA` | covered | 2001-08-17T00:00:00 | 2026-05-13T00:00:00 | 6220 |
| international_etfs | `EEM` | covered | 2003-04-14T00:00:00 | 2026-05-13T00:00:00 | 5808 |
| international_etfs | `VEA` | covered | 2007-07-26T00:00:00 | 2026-05-13T00:00:00 | 4730 |
| international_etfs | `VWO` | covered | 2005-03-10T00:00:00 | 2026-05-13T00:00:00 | 5328 |
| defensive_and_macro_etfs | `TLT` | covered | 2002-07-26T00:00:00 | 2026-05-13T00:00:00 | 5988 |
| defensive_and_macro_etfs | `IEF` | covered | 2002-07-26T00:00:00 | 2026-05-13T00:00:00 | 5988 |
| defensive_and_macro_etfs | `AGG` | covered | 2003-09-26T00:00:00 | 2026-05-13T00:00:00 | 5693 |
| defensive_and_macro_etfs | `LQD` | covered | 2002-07-26T00:00:00 | 2026-05-13T00:00:00 | 5988 |
| defensive_and_macro_etfs | `HYG` | covered | 2007-04-11T00:00:00 | 2026-05-13T00:00:00 | 4804 |
| defensive_and_macro_etfs | `SHV` | covered | 2007-01-11T00:00:00 | 2026-05-13T00:00:00 | 4865 |
| defensive_and_macro_etfs | `GLD` | covered | 2004-11-18T00:00:00 | 2026-05-13T00:00:00 | 5404 |
| defensive_and_macro_etfs | `SLV` | covered | 2006-04-28T00:00:00 | 2026-05-13T00:00:00 | 5042 |
| defensive_and_macro_etfs | `USO` | covered | 2006-04-10T00:00:00 | 2026-05-13T00:00:00 | 5055 |
| defensive_and_macro_etfs | `UNG` | covered | 2007-04-18T00:00:00 | 2026-05-13T00:00:00 | 4799 |
| defensive_and_macro_etfs | `VXX` | covered | 2009-01-30T00:00:00 | 2026-05-13T00:00:00 | 4348 |
| leveraged_and_tactical_etfs | `SSO` | covered | 2006-06-21T00:00:00 | 2026-05-13T00:00:00 | 5005 |
| leveraged_and_tactical_etfs | `QLD` | covered | 2006-06-21T00:00:00 | 2026-05-13T00:00:00 | 5005 |
| leveraged_and_tactical_etfs | `UPRO` | covered | 2009-06-25T00:00:00 | 2026-05-13T00:00:00 | 4247 |
| leveraged_and_tactical_etfs | `TQQQ` | covered | 2010-02-11T00:00:00 | 2026-05-13T00:00:00 | 4088 |
| leveraged_and_tactical_etfs | `SOXL` | covered | 2010-03-11T00:00:00 | 2026-05-13T00:00:00 | 4069 |
| leveraged_and_tactical_etfs | `SMH` | covered | 2000-06-05T00:00:00 | 2026-05-13T00:00:00 | 6524 |
| leveraged_and_tactical_etfs | `DRAM` | covered | 2026-04-02T00:00:00 | 2026-05-13T00:00:00 | 29 |
| leveraged_and_tactical_etfs | `AIS` | covered | 2024-12-03T00:00:00 | 2026-05-13T00:00:00 | 361 |
| leveraged_and_tactical_etfs | `POW` | covered | 2021-03-04T00:00:00 | 2026-05-13T00:00:00 | 606 |
| crypto_daily | `btcusd` | stale | 2014-01-01T00:00:00 | 2026-04-14T00:00:00 | 4483 |
| crypto_daily | `ethusd` | stale | 2015-08-08T00:00:00 | 2026-04-14T00:00:00 | 3882 |
| crypto_daily | `bnbusd` | stale | 2021-08-03T00:00:00 | 2026-04-14T00:00:00 | 1033 |
| crypto_daily | `xrpusd` | stale | 2015-02-26T00:00:00 | 2026-04-14T00:00:00 | 3878 |
| crypto_daily | `adausd` | stale | 2017-12-29T00:00:00 | 2026-04-14T00:00:00 | 2993 |
| crypto_daily | `solusd` | stale | 2020-08-23T00:00:00 | 2026-04-14T00:00:00 | 2021 |
| crypto_daily | `dogeusd` | stale | 2017-03-09T00:00:00 | 2026-04-14T00:00:00 | 3294 |
| crypto_daily | `avaxusd` | stale | 2021-05-12T00:00:00 | 2026-04-14T00:00:00 | 1791 |
| crypto_daily | `maticusd` | stale | 2019-06-07T00:00:00 | 2025-10-14T00:00:00 | 2300 |
| crypto_daily | `dotusd` | stale | 2017-03-09T00:00:00 | 2026-04-14T00:00:00 | 2692 |
| forex_and_metals | `eurusd` | stale | 2020-01-01T00:00:00 | 2026-04-17T00:00:00 | 1957 |
| forex_and_metals | `gbpusd` | stale | 2020-01-01T00:00:00 | 2026-04-17T00:00:00 | 1957 |
| forex_and_metals | `usdjpy` | stale | 2020-01-01T00:00:00 | 2026-04-17T00:00:00 | 1958 |
| forex_and_metals | `usdchf` | stale | 2020-01-01T00:00:00 | 2026-04-17T00:00:00 | 1956 |
| forex_and_metals | `audusd` | stale | 2020-01-01T00:00:00 | 2026-04-17T00:00:00 | 1957 |
| forex_and_metals | `usdcad` | stale | 2020-01-01T00:00:00 | 2026-04-17T00:00:00 | 1957 |
| forex_and_metals | `nzdusd` | stale | 2020-01-01T00:00:00 | 2026-04-17T00:00:00 | 1956 |
| forex_and_metals | `xauusd` | stale | 2020-01-02T00:00:00 | 2026-04-17T00:00:00 | 1700 |
| forex_and_metals | `xagusd` | stale | 2020-01-02T00:00:00 | 2026-04-17T00:00:00 | 1700 |

## Download Priority

1. Fetch missing critical ETFs/crypto/forex while Tiingo access remains active.
2. Refresh stale critical daily data to the current date.
3. Create a compressed backup of `data/tiingo/` after downloads complete.

This audit is storage-only and makes no strategy claim. It exists to prevent
window-fit or stale-data research before optimization `[advances_fin_ml, p.196-202]`.
