# PRE_REG — 003-gayed-lrs-control

## Hypothesis

Test the canonical Leverage Rotation Strategy control: use the S&P 500 200-day
moving average as a volatility/regime filter, hold leveraged S&P exposure when
`SPYSIM > SMA200`, and hold cash otherwise. Gayed frames moving averages as
volatility-regime controls for leveraged equity exposure and reports canonical
2x/3x LRS variants `[leverage_for_the_long_run, p.13]`,
`[leverage_for_the_long_run, p.16-17]`, `[leverage_for_the_long_run, p.21]`.

This is a control, not a local optimization. The 200-day lookback and 2x/3x
variants are fixed before testing. Signal is shifted by one trading day to avoid
same-close look-ahead `[advances_fin_ml, p.31-34]`.

## Exact Configs

1. `gayed_lrs_sma200_sso_cash`: `SPYSIM > SMA200(SPYSIM)` then `SSOSIM`, else
   `CASHX`.
2. `gayed_lrs_sma200_upro_cash`: `SPYSIM > SMA200(SPYSIM)` then `UPROSIM`, else
   `CASHX`.

## Data And Window

Primary source: `data/testfolio/cache/history.parquet` via
`load_testfolio_series`. Required labels: `SPYSIM`, `SSOSIM`, `UPROSIM`, and
`CASHX`. Use the common non-null window after the 200-day warmup and one-day
signal lag. If either leveraged S&P label is unavailable, record `data_blocked`
and do not substitute QQQ/QLD/TQQQ after the fact.

Benchmark: `SPYSIM` buy-and-hold over the identical post-warmup common window.

## Planned Gates

- Economic: candidate CAGR > same-window SPY CAGR and terminal equity ratio > 1.
- PBO: `< 0.5` over the two pre-fixed configs `[advances_fin_ml, p.208-211]`.
- DSR: `p < 0.05` with cumulative trials after this iteration, `n_trials=6`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6/8 windows beat SPY `[testing_tuning, ch.12]`.
- OOS: final 25% window beats SPY `[advances_fin_ml, p.196-202]`.
- FWD: final 3 years beat SPY `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% CI low of annualized daily excess return > 0
  `[advances_fin_ml, p.196-202]`.
- Cross-lib: vectorized implementation and explicit loop CAGR differ by <= 3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If required labels are unavailable, status is `data_blocked`.
- If neither config beats SPY CAGR and terminal equity, status is `fail` even if
  risk-adjusted metrics improve.
- If PBO or DSR fails, no winner is allowed regardless of CAGR.
- If the result depends on same-close signal timing, discard. This runner uses
  `signal.shift(1)` by construction.

## Trial Accounting

- `cumulative_n_trials_before = 4`.
- `n_trials_this_iteration = 2` if data are available, else `0`.
- `cumulative_n_trials_after = 6` if data are available, else `4`.
