# PRE_REG — 014-2026-05-14-vidya-adaptive-trend

## Hypothesis

Volatility Index Dynamic Average (VIDYA) can act as an adaptive daily trend filter:
hold the asset when the prior close is above its VIDYA and hold `SHV` otherwise.
VIDYA adapts smoothing by the ratio of short to long volatility, which may respond
faster than fixed SMAs while retaining a simple one-indicator regime rule
`[trading_systems_methods, p.784-785]`. Trend filters are only acceptable if they
preserve or improve compounded return versus buy-and-hold, because Phase 2 does not
promote lower-CAGR de-risking filters `[systematic_trading, p.40]`,
`[testing_tuning, p.327-335]`.

This is a daily swing hypothesis, not an intraday hypothesis. Before testing, the
script must audit physical daily files and report that `1hour`/`15min` data remain
blocked if files are absent; manifest-only availability is insufficient
`[testing_tuning, p.327-335]`.

## Exact Configs

All signals are lagged one completed daily bar before earning returns to avoid
same-close lookahead `[advances_fin_ml, p.31-34]`.

| config | asset | short vol | long vol | base EMA constant |
|---|---:|---:|---:|---:|
| `spy_vidya9_30` | `SPY` | 9 | 30 | 0.20 |
| `qqq_vidya9_30` | `QQQ` | 9 | 30 | 0.20 |
| `gld_vidya9_30` | `GLD` | 9 | 30 | 0.20 |
| `xau_vidya9_30` | `xauusd` | 9 | 30 | 0.20 |

No additional thresholds, exits or local tuning are allowed in this iteration.

## Data And Window

Primary data: local Tiingo daily parquet files under `data/tiingo/daily/prices/`.
Required daily files: `SPY`, `QQQ`, `GLD`, `xauusd`, `SHV`.

The aligned strategy window starts after the 30-day long-volatility warmup plus
one lagged signal bar for each asset. The audit must record physical file path,
row count, first/last timestamp, timezone, columns and missing-business-day rate.

Intraday audit: inspect `data/tiingo/1hour/prices/` and
`data/tiingo/15min/prices/`. If physical 1h/15m files are absent, no intraday bars
may be synthesized.

## Benchmarks

Primary benchmark: same-asset buy-and-hold on exactly the same aligned dates as
the tested strategy.

Opportunity benchmark: `SPY` buy-and-hold on the same aligned dates.

## Kill Rules

- If any required daily physical file is missing, close `data_blocked` and consume
  zero trials.
- If best strategy CAGR <= same-asset buy-and-hold CAGR, close `fail` and do not
  assign `candidate_watchlist`, `paper_trade_candidate` or `strict_winner`.
- If strict gates fail, close no better than `fail` unless economic floor and a
  majority of available robustness gates justify `candidate_watchlist`; PBO/DSR
  failures still block `strict_winner` `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.
- Do not tune VIDYA lengths or add confirmation filters after seeing validation
  results.

## Planned Gates

- IS MCPT with 200 permutations; promotion requires `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- Walk-forward MCPT with 100 permutations; promotion requires `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO `< 0.5` on the four pre-registered configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative strategy trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward windows: at least 8 windows and at least 6 positive
  `[testing_tuning, p.148-150]`.
- OOS last 20% total return positive `[advances_fin_ml, p.196-202]`.
- Latest 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% mean daily return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Trial Accounting

- `cumulative_n_trials` before: 152.
- New configs planned: 4.
- `cumulative_n_trials` after if all configs run: 156.
