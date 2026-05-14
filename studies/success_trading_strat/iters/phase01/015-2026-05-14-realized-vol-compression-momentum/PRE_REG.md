# PRE_REG — 015 realized volatility compression momentum

## Hypothesis

Equity trend exposure may be more robust when enabled only during realized-volatility
compression: volatility clusters over time, volatility cones contextualize current
realized volatility, and simple positive momentum supplies directional confirmation
`[volatility_trading, p.36]`, `[volatility_trading, p.58-59]`,
`[quant_trading_chan, p.142-143]`. This is a pivot away from crypto-only local
variants and from VIX-managed floors/windows, not a continuation of either failed
branch `[testing_tuning, p.327-335]`.

## Exact Configs

Common rule: hold the risk asset when the prior-day 20-trading-day realized
volatility is at or below its prior 252-day percentile threshold and the prior-day
63-trading-day total return is positive; otherwise hold `SHV`. All signals are
lagged one bar to avoid same-close lookahead `[advances_fin_ml, p.196-202]`.

1. `spy_rv20_p40_m63`: risk asset `SPY`, realized-vol percentile threshold `40%`, momentum lookback `63`.
2. `spy_rv20_p60_m63`: risk asset `SPY`, realized-vol percentile threshold `60%`, momentum lookback `63`.
3. `qqq_rv20_p40_m63`: risk asset `QQQ`, realized-vol percentile threshold `40%`, momentum lookback `63`.
4. `qqq_rv20_p60_m63`: risk asset `QQQ`, realized-vol percentile threshold `60%`, momentum lookback `63`.

Parameter rationale: 20 days approximates a one-month volatility estimate; 252 days
is a one-year cone/rank context; 63 days is one quarter of momentum confirmation;
two percentile thresholds are a deliberately small robustness check, not a broad
optimization `[volatility_trading, p.14]`, `[volatility_trading, p.58-59]`,
`[quant_trading_chan, p.142-143]`, `[testing_tuning, p.327-335]`.

## Data And Window

Local Tiingo daily adjusted prices from `data/tiingo/daily/prices/` for `SPY`,
`QQQ` and `SHV`. Use the common adjusted-close window from `2010-01-01` onward.
If any required file is missing or the common window is insufficient for at least
5 years after warmup, close as `data_blocked` and consume zero trials.

## Benchmark

Each config is compared against buy-and-hold of its same risk asset over the same
post-warmup dates. A winner must beat the same-asset benchmark Sharpe and pass all
hard gates; CAGR and MDD are reported but not hard-blocks per mandate.

## Planned Gates

- Data freshness: common data must extend past `2026-03-31`.
- Economic Sharpe vs same-asset buy-and-hold.
- IS MCPT on best pre-registered config: 200 permutations, pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT on best pre-registered config: 100 permutations, pass `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO across the 4 configs with 8 blocks, pass `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR using cumulative trials after this iteration, pass `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward positive windows: require all windows if fewer than 8, otherwise at
  least 6 positives `[testing_tuning, p.148-150]`.
- Single-block final 20% OOS return positive `[advances_fin_ml, p.196-202]`.
- Latest 63-observation FWD stress positive `[advances_fin_ml, p.196-202]`.
- Stationary bootstrap 99.9% mean daily CI low > 0 `[testing_tuning, p.246-247]`.
- NumPy cross-check CAGR within +/-3 percentage points `[advances_fin_ml, p.31-34]`.

## Kill Rules

- Do not add thresholds, windows or assets after seeing results.
- If PBO or DSR fails, mark `fail` even if economic metrics improve.
- If MCPT fails, do not continue local tuning of realized-vol thresholds without a
  new mechanism.
- Do not modify `docs/investment-mandate.md`; no deploy claim.

## Trial Accounting

- `cumulative_n_trials` before: 44.
- New strategy configs: 4.
- `cumulative_n_trials` after if data are available: 48.
