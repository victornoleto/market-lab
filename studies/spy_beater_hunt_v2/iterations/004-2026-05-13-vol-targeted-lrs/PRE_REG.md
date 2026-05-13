# PRE_REG — 004-vol-targeted-lrs

## Hypothesis

Canonical Gayed SPY LRS beat SPY economically in iteration 003 but failed the
99.9% bootstrap excess-return gate. This iteration tests whether a pre-fixed
volatility-targeted overlay on the same `SPYSIM > SMA200` regime rule can keep
the economic edge while reducing high-volatility tail exposure. Volatility
standardisation and fixed volatility targets follow Carver's position-sizing
framework `[systematic_trading, p.40]`, `[systematic_trading, p.137-148]`; close-
to-close realized volatility estimation follows Sinclair `[volatility_trading,
p.14]`; the 200-day LRS filter follows Gayed `[leverage_for_the_long_run, p.13]`,
`[leverage_for_the_long_run, p.16-17]`, `[leverage_for_the_long_run, p.21]`.

## Data And Window

- Source: `data/testfolio/cache/history.parquet` via `load_testfolio_series`.
- Required labels: `SPYSIM`, `UPROSIM`, `CASHX`.
- Window: common available history after all required labels align, expected
  long-history 1986-01-03..2026-04-17.
- Benchmark: same-window `SPYSIM` buy-and-hold.

## Exact Configs

Both configs use the same one-day-lagged Gayed regime:

- Risk-on if yesterday's `SPYSIM` close was above its 200-trading-day SMA.
- Risk-off otherwise.
- Risk-on asset: `UPROSIM`.
- Risk-off asset: `CASHX`.
- Realized volatility estimator: trailing 63 trading days of `UPROSIM` daily
  returns, annualized by `sqrt(252)`.
- Exposure weight in risk-on state: `min(1.0, target_vol / realized_vol_63d)`.
- Unused capital in risk-on state earns `CASHX` returns.
- Risk-off state earns `CASHX` returns.

Pre-registered configs:

1. `vt_lrs_upro_target20`: target annualized vol `20%`.
2. `vt_lrs_upro_target25`: target annualized vol `25%`.

The targets are not optimized locally: 20% approximates broad equity volatility,
and 25% allows modestly higher risk while staying below full 3x UPRO exposure.
Both are fixed before testing `[systematic_trading, p.137-148]`.

## Planned Gates

- Economic: candidate CAGR and terminal equity must beat same-window SPY.
- PBO `< 0.5` on the two-config panel `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6/8 windows beat SPY `[testing_tuning, ch.12]`.
- OOS: final 25% CAGR beats SPY `[advances_fin_ml, p.196-202]`.
- FWD: final 3y CAGR beats SPY `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% annualized daily excess-return CI low `> 0`
  `[advances_fin_ml, p.196-202]`.
- Cross-lib: vectorized and explicit-loop CAGR within +/-3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If either `SPYSIM`, `UPROSIM`, or `CASHX` is unavailable, mark `data_blocked`;
  do not substitute Tiingo or a shorter window.
- If the best config does not beat SPY CAGR, mark `fail` regardless of risk
  improvement.
- If any hard gate fails, mark `fail`; no near-miss promotion.
- If PBO passes with only two configs, record it as unstable rather than strong
  evidence.

## Trial Accounting

- `cumulative_n_trials` before: `6`.
- This iteration `n_trials`: `2`.
- `cumulative_n_trials` after: `8`.
