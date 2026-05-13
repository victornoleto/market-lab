# PRE_REG — 007-vol-scaled-relative-momentum

## Hypothesis

Iteration 006 showed that Clenow-style SPY/QQQ relative momentum has strong
economic signal but failed the bootstrap 99.9% hard gate. This iteration tests
whether pre-fixed volatility-scaled exposure can preserve SPY-beating CAGR while
improving robustness of the same relative-momentum mechanism.

The relative-momentum rank uses 90-day adjusted slope, defined as annualized
log-price regression slope times `R^2` `[stocks_on_the_move, p.75-77, p.82]`.
The broad risk-on filter is `SPYSIM > SMA200` `[stocks_on_the_move, p.66-67]`.
Volatility scaling uses lagged 63-day realized volatility and fixed annualized
targets because robust position sizing should adapt exposure to risk rather than
only nominal leverage `[systematic_trading, p.40]`, `[systematic_trading, p.137-148]`,
`[volatility_trading, p.14]`. Signals and sizing are shifted by one trading day
before return application to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.

## Exact Configs

Two pre-registered configs, no adaptive selection beyond choosing the best CAGR
for gate reporting:

1. `relmom90_3x_vt20_cash`: rank `SPYSIM` vs `QQQSIM`; if `SPYSIM > SMA200`, hold
   the selected 3x LETF (`UPROSIM` or `TQQQSIM`) scaled to 20% annualized vol using
   lagged 63-day realized volatility; otherwise `CASHX`; max gross exposure 1.0.
2. `relmom90_3x_vt25_cash`: same, scaled to 25% annualized vol; max gross exposure
   1.0.

No lookback, SMA, target-vol, cap, or asset grid is allowed in this iteration.

## Data And Window

Use existing testfol.io long-history cache via `load_testfolio_series` for:
`SPYSIM`, `QQQSIM`, `UPROSIM`, `TQQQSIM`, and `CASHX`.

Expected common window is approximately 1986-01-03 to 2026-04-17, subject to the
loaded cache intersection. SPY buy-and-hold over the same return dates is the
primary benchmark.

## Planned Gates

- Economic: best candidate CAGR and terminal equity ratio must beat SPY.
- PBO: `< 0.5` using 10 blocks over the two config return matrix
  `[advances_fin_ml, p.208-211]`; note that two-config PBO is unstable.
- DSR: `p < 0.05` using cumulative `n_trials=14` after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6/8 windows beat SPY `[testing_tuning, ch.12]`.
- OOS: final 25% candidate CAGR beats SPY `[advances_fin_ml, p.196-202]`.
- FWD stress: final 3y candidate CAGR beats SPY `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% CI low of daily excess-return mean annualized is `> 0`
  `[advances_fin_ml, p.196-202]`.
- Cross-lib: vectorized and explicit-loop CAGR must match within ±3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If the best config does not beat SPY CAGR, mark `fail` immediately.
- If bootstrap 99.9% CI low remains `<= 0`, mark `fail`; do not round near-zero.
- If DSR fails after cumulative trial accounting, mark `fail`.
- If only the 25% target works by adding drawdown without bootstrap pass, do not
  continue local volatility-target tuning.
- If data labels are unavailable, mark `data_blocked`; do not substitute Tiingo or
  shorter modern windows.

## Trial Accounting

- `cumulative_n_trials_before`: 12.
- `n_trials_this_iteration`: 2.
- `cumulative_n_trials_after`: 14.
