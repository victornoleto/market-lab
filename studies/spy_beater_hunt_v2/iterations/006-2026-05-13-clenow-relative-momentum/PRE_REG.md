# PRE_REG — 006-clenow-relative-momentum

## Hypothesis

Test a pre-fixed relative-momentum control between `SPYSIM` and `QQQSIM`: rank the
two equity indices by Clenow-style 90-day adjusted slope, invest next day in the
leveraged ETF proxy for the stronger index only when the broad SPY regime is above
its 200-day SMA, otherwise hold `CASHX`. Momentum ranking uses annualized log-price
slope times `R^2` `[stocks_on_the_move, p.75-77, p.82]`; the broad market regime
filter uses SPY above SMA200 `[stocks_on_the_move, p.66-67]`; next-day execution
avoids same-close look-ahead `[advances_fin_ml, p.31-34]`.

This is distinct from the prior dead ends because it is not a single-index LRS,
not EWMAC speed tuning, and not a static diversifier. It first chooses between two
equity risk premia by cross-sectional momentum before applying leverage.

## Exact Configs

1. `clenow_relmom_90d_2x_cash`: 90 trading-day adjusted slope rank over `SPYSIM`
   and `QQQSIM`; if `SPYSIM > SMA200`, hold `SSOSIM` when SPY ranks higher or
   `QLDSIM` when QQQ ranks higher; otherwise hold `CASHX`.
2. `clenow_relmom_90d_3x_cash`: same signal and regime, but risk-on assets are
   `UPROSIM` for SPY and `TQQQSIM` for QQQ; otherwise hold `CASHX`.

No parameter tuning is allowed inside the iteration. The 90-day slope, `R^2`,
SMA200 regime, and weekly-stock-book momentum concept are pre-fixed from Clenow;
the daily ETF implementation is a diagnostic transport, not a claim that the
original stock strategy was tested `[stocks_on_the_move, p.98-100]`.

## Data And Window

Use `data/testfolio/cache/history.parquet` via `load_testfolio_series` for:
`SPYSIM`, `QQQSIM`, `SSOSIM`, `QLDSIM`, `UPROSIM`, `TQQQSIM`, and `CASHX`.
The test window is the common non-null daily window after signal warmup. Benchmark
is same-window `SPYSIM` buy-and-hold.

## Planned Gates

- Economic: candidate CAGR and terminal equity must beat same-window SPY.
- PBO `< 0.5` on the two pre-registered config return panel
  `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6/8 windows beat SPY `[testing_tuning, ch.12]`.
- OOS: final 25% CAGR beats SPY `[advances_fin_ml, p.196-202]`.
- FWD stress: final 3y CAGR beats SPY `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% CI low of annualized daily excess return over SPY is positive
  `[advances_fin_ml, p.196-202]`.
- Cross-lib: vectorized and explicit-loop CAGR agree within +/-3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If either required data label is unavailable, mark `data_blocked`; do not
  substitute assets.
- If best config fails economic comparison vs SPY, verdict is `fail` even if any
  statistical gate passes.
- If PBO or DSR fails, verdict is not winner regardless of CAGR.
- If the result depends only on the 3x variant while 2x fails badly, record
  leverage concentration as a lesson and do not extend leverage locally.
- Do not update `docs/investment-mandate.md`; capital remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials` before: 10.
- `n_trials` this iteration: 2.
- `cumulative_n_trials` after: 12.
