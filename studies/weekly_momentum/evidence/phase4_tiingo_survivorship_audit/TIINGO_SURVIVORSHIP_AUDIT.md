# Tiingo Survivorship Coverage Audit

## Scope

- Window: `2013-01-01` to `2026-05-10`.
- Universe: current S&P 500, reconstructed start-date S&P 500, and all selected-change added/removed tickers in the window.
- Fetch enabled: `True`.
- Purpose: determine whether Tiingo can supply removed/delisted/renamed symbols before rerunning the frozen `lb80/k5` leads `[advances_fin_ml, p.208-211]`.

## Summary

| generated_at        | start      | end        | fetch_enabled   |   n_universe |   n_available |   pct_available |   n_missing_or_error |   n_fetch_errors |   n_likely_removed_or_renamed |   n_likely_removed_or_renamed_available |   pct_likely_removed_or_renamed_available |   n_current_available |   n_start_available |
|:--------------------|:-----------|:-----------|:----------------|-------------:|--------------:|----------------:|---------------------:|-----------------:|------------------------------:|----------------------------------------:|------------------------------------------:|----------------------:|--------------------:|
| 2026-05-10T10:57:53 | 2013-01-01 | 2026-05-10 | True            |          769 |           745 |        0.968791 |                   24 |                0 |                           260 |                                     240 |                                  0.923077 |                   503 |                 493 |

## Removed/Renamed Proxy Sample

| ticker   | fetch_status   | first_dt            | last_dt             |   n_bars | selected_change_dates   |
|:---------|:---------------|:--------------------|:--------------------|---------:|:------------------------|
| AAL      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2015-03-23;2024-09-23   |
| AAP      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2015-07-08;2023-08-25   |
| AIV      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2020-12-21              |
| ALK      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2016-05-13;2023-12-18   |
| AMG      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2014-07-01;2019-12-23   |
| AN       | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 1998-12-11;2017-08-08   |
| ANF      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2013-12-23              |
| ATI      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2015-07-02              |
| AYI      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2016-05-03;2018-06-18   |
| BBBY     | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2017-07-26              |
| BBWI     | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2024-10-01              |
| BIO      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2020-06-22;2024-09-23   |
| BWA      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2011-12-16;2025-03-24   |
| CE       | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2018-12-24;2025-03-24   |
| CLF      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2009-12-18;2014-04-02   |
| CNX      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2016-03-04              |
| CPRI     | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2020-05-12              |
| EMN      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2025-11-04              |
| ENPH     | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2021-01-07;2025-09-22   |
| FHN      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2013-06-21              |
| FII      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2013-01-02              |
| FLR      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2019-06-03              |
| FLS      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2021-03-22              |
| FMC      | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2009-08-19;2025-03-24   |
| FOSL     | cached         | 2013-01-02T00:00:00 | 2026-05-08T00:00:00 |     3358 | 2012-04-03;2016-01-05   |

## Missing Or Error Sample

| ticker   | fetch_status   | error   | selected_change_dates   |
|:---------|:---------------|:--------|:------------------------|
| ACE      | empty          |         | 2016-01-19              |
| ADS      | empty          |         | 2013-12-23;2020-06-22   |
| BIG      | empty          |         | 2013-02-15              |
| BMC      | empty          |         | 2013-09-10              |
| CCE      | empty          |         | 2016-05-31              |
| CDAY     | empty          |         | 2021-09-20              |
| DF       | empty          |         | 2013-05-23              |
| ENDP     | empty          |         | 2015-01-27;2017-03-02   |
| ESV      | empty          |         | 2012-07-31;2016-03-30   |
| FBHS     | empty          |         | 2016-06-22;2022-12-19   |
| FLT      | empty          |         | 2018-06-20              |
| FRC      | empty          |         | 2019-01-02;2023-05-04   |
| GPS      | empty          |         | 2022-02-03              |
| HFC      | empty          |         | 2018-06-18;2021-06-04   |
| IGT      | empty          |         | 2014-06-20              |
| JCP      | empty          |         | 2013-12-02              |
| MNK      | empty          |         | 2014-08-18;2017-07-26   |
| MOLX     | empty          |         | 2013-12-10              |
| NYX      | empty          |         | 2013-11-13              |
| RE       | empty          |         | 2017-06-19              |
| SAI      | empty          |         | 2009-12-18;2013-09-20   |
| TYC      | empty          |         | 2010-08-26;2016-09-06   |
| WIN      | empty          |         | 2015-04-07              |
| WLTW     | empty          |         | 2016-01-05              |

## Artifacts

- `sp500_pit_tiingo_universe.csv`: full candidate universe and selected-change provenance.
- `tiingo_fetch_audit.csv`: per-ticker cache/API status and coverage.
- `summary.json`: machine-readable summary.

## Interpretation Rules

- High removed/renamed availability supports using Tiingo as the price layer, but it does not make Wikipedia membership exhaustive.
- Missing rows are blockers only if they appear in the PIT universe during high-impact periods; the next backtest must quantify active missing names per signal date.
- Ticker-class and rename cases can still require manual mapping even when Tiingo has the surviving/new ticker.
