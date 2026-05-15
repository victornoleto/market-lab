# PRE_REG - Phase 3 Iteration 008

## Hypothesis

Test drawdown-adaptive gross exposure on the already confirmed high-beta equity
universe `QQQ/SMH/SOXX/XLK`. The return engine is not another long/flat filter:
it stays invested and changes sizing after portfolio drawdowns, using leverage as
the explicit upside mechanism. Vince treats position sizing as a migration path
through leverage space and evaluates drawdown-constrained probability of profit
`[leverage_space, p.149-167]`; Carver separates forecast, volatility target and
position sizing, warning that sizing design can dominate the trading rule
`[systematic_trading, p.137-148]`.

This is a research-only Phase 3 test. It does not authorize capital allocation;
capital remains 100% Plano C.

## Data And Window

Physical daily parquet files required before testing:

- `data/tiingo/daily/prices/QQQ.parquet`
- `data/tiingo/daily/prices/SMH.parquet`
- `data/tiingo/daily/prices/SOXX.parquet`
- `data/tiingo/daily/prices/XLK.parquet`
- `data/tiingo/daily/prices/SPY.parquet`

`SHV` is audited for context but not used as a sleeve because the mechanism must
not become defensive cash timing. Use the common adjusted-close window across the
required universe. Signals and exposure multipliers are one-bar lagged.

## Configs

Four explicit trials:

1. `ew_dd15_boost125_cap150`: equal-weight universe; gross exposure 1.25 after
   strategy drawdown <= -15%, otherwise 1.00; cap 1.50.
2. `ew_dd25_boost150_cap175`: equal-weight universe; gross exposure 1.50 after
   strategy drawdown <= -25%, otherwise 1.00; cap 1.75.
3. `top2_m63_dd15_boost125_cap150`: previous fixed top-2 63d momentum selection,
   but only the new drawdown-adaptive sizing overlay is under test; gross 1.25
   after drawdown <= -15%, otherwise 1.00; cap 1.50.
4. `top2_m63_dd25_boost150_cap175`: same fixed top-2 63d selection; gross 1.50
   after drawdown <= -25%, otherwise 1.00; cap 1.75.

No lookback or top-k tuning is allowed in this iteration; `top2_m63` is held fixed
as a previously documented high-beta selection rule. Gross exposure above 1.0 is
modeled directly on daily returns with no financing/tax adjustment, so any
positive result would require a later cost/financing audit before promotion.

## Benchmarks

Primary benchmark: equal-weight buy-and-hold of `QQQ/SMH/SOXX/XLK` on the exact
aligned dates.

Opportunity benchmark: `SPY` buy-and-hold on the same dates.

Context benchmarks: individual buy-and-hold for `QQQ`, `SMH`, `SOXX`, `XLK`.

## Economic Kill Rule

If strategy CAGR or terminal wealth is <= the primary equal-weight buy-and-hold
benchmark, close as `fail`. No `economic_beater_not_validated`,
`candidate_watchlist`, `paper_trade_candidate` or `strict_winner` label is allowed
without beating both aligned CAGR and aligned terminal wealth.

## Planned Gates

- IS MCPT with 200 joint-return-row permutations, pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations after the first train window, pass if `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the four pre-registered configs
  `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward positives: at least 6 positive windows and at least 8 total windows.
- Single-block OOS positive.
- Latest 63-trading-day FWD stress positive.
- Bootstrap 99.9% mean daily return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Trial Accounting

`cumulative_n_trials` before: 252.

New strategy configs: 4.

`cumulative_n_trials` after if tested: 256.

If required physical files are missing or malformed, close `data_blocked` with
`n_trials=0` and keep `cumulative_n_trials=252`.
