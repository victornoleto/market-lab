# PRE_REG — 005-2026-05-14-equity-gap-continuation

## Hypothesis

Daily opening gaps can identify short swing demand/supply imbalance. A down gap
that recovers by the close is treated as a reversal/accumulation signal; the rule
holds the next daily close-to-close bar in `SPY` or `QQQ`, otherwise `SHV`. Gap
and close-location rules are classical OHLC pattern inputs, but promotion still
requires MCPT, WF-MCPT, PBO and DSR because data-mined technical patterns are
suspect by default `[trading_systems_methods, p.635]`, `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Data And Window

- Files audited before testing: `data/tiingo/daily/prices/SPY.parquet`,
  `QQQ.parquet`, `SHV.parquet`.
- Intraday audit still required by Phase 2: inspect physical
  `data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/`; if absent or empty,
  no intraday data will be synthesized.
- Expected window: maximum common adjusted-OHLC daily window available after warmup.
- Timezone/session convention: daily bars with timezone stripped after file audit;
  signals use completed daily bars only and are shifted one bar before returns.

## Exact Configs

Four configs, no local tuning after results:

| name | ticker | gap_down_threshold | close_recovery |
|---|---:|---:|---:|
| `spy_gap05_recover` | `SPY` | `-0.005` | `close > open` |
| `spy_gap10_recover` | `SPY` | `-0.010` | `close > open` |
| `qqq_gap05_recover` | `QQQ` | `-0.005` | `close > open` |
| `qqq_gap10_recover` | `QQQ` | `-0.010` | `close > open` |

Return rule: if `open / previous_close - 1 <= threshold` and `close > open`,
hold the ticker for the next close-to-close return; otherwise hold `SHV`.

## Benchmarks

- Primary: same-asset buy-and-hold over the aligned window.
- Context: `SPY` buy-and-hold over the aligned window.

## Planned Gates

- Economic Sharpe versus same-asset buy-and-hold.
- IS MCPT with 200 fixed-rule permutations on adjusted close paths.
- WF MCPT with 100 fixed-rule permutations after first train window.
- PBO across the four pre-registered configs.
- DSR using cumulative trials after this iteration: `116 + 4 = 120`.
- Walk-forward windows: require at least 8 windows and 6 positive windows.
- OOS: last 20% total return positive.
- FWD stress: latest 63 trading days positive.
- Bootstrap 99.9% mean-daily CI low > 0.
- Cross-lib/vector parity within ±3pp CAGR.

## Kill Rules

- If any required daily file is absent, status is `data_blocked` and `n_trials=0`.
- If physical 1h/15m files are absent, record intraday as blocked and continue only
  with the pre-registered daily OHLC mechanism.
- If MCPT, PBO or DSR fails, do not tune thresholds locally.
- A `candidate_watchlist` is not deployable; capital remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials` before: 116.
- Planned `n_trials`: 4.
- `cumulative_n_trials` after if data are available: 120.
