# PRE_REG — 006 RSI(2) mean reversion

## Hypothesis

Short-horizon equity ETF mean reversion can produce a cleaner risk-adjusted path
than buy-and-hold when entries are restricted to oversold closes and exits wait
for a mean-reversion recovery. This is a mechanism pivot away from trend,
cross-sectional momentum and volatility targeting. The design is deliberately
small and parameter-light because data-snooping and parameter proliferation are
primary failure modes `[quant_trading_chan, p.52-53]`, `[quant_trading_chan,
p.116]`.

The indicator is Wilder-style `RSI(2)`: a very short lookback is used only as an
oversold/mean-reversion trigger, not as a trend-following score. Signals are
lagged one bar before returns are applied to avoid look-ahead bias
`[quant_trading_chan, p.51]`. No stop loss is used because Chan warns that stops
can be harmful in mean-reverting systems by forcing exits near the worst point
`[quant_trading_chan, p.142-143]`.

## Data And Window

- Source: local Tiingo daily adjusted close parquet cache.
- Tickers: `SPY`, `QQQ`, `SHV`.
- Window: common adjusted-close history from `2008-01-01` onward.
- Defensive asset: `SHV` when the rule is flat.
- Survivorship note: ETFs are current listed instruments; no single-stock
  survivorship claim is made.

## Exact Configs

All configs hold the risk ETF after `RSI(2)` closes below the entry threshold and
stay invested until `RSI(2)` closes above `70`. Daily position is shifted by one
bar before multiplying returns `[quant_trading_chan, p.51]`.

| config | risk asset | RSI period | entry | exit |
|---|---|---:|---:|---:|
| `spy_rsi2_e5_x70` | `SPY` | 2 | 5 | 70 |
| `spy_rsi2_e10_x70` | `SPY` | 2 | 10 | 70 |
| `qqq_rsi2_e5_x70` | `QQQ` | 2 | 5 | 70 |
| `qqq_rsi2_e10_x70` | `QQQ` | 2 | 10 | 70 |

## Benchmark

Primary benchmark for economic comparison is buy-and-hold of the same risk ETF
as the selected best config over the same post-warmup dates. `SPY` buy-and-hold
is also reported as a broad-market reference.

## Planned Gates

- IS MCPT on the selected best fixed config: `200` permutations, pass if
  `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT on the selected best fixed config: `100` permutations, pass if
  `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO over the four pre-registered configs with 8 blocks, pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR on the selected best config with cumulative trials after this iteration,
  pass if `p < 0.05` `[advances_fin_ml, p.222-223]`.
- Walk-forward: 4-year train, 1-year test, 1-year step; pass if at least `6/8`
  windows are positive `[testing_tuning, p.148-150]`.
- Single-block OOS: last 20% of the best return series positive
  `[advances_fin_ml, p.196-202]`.
- FWD stress: last 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: stationary bootstrap `99.9%` mean daily return CI low > 0
  `[testing_tuning, p.246-247]`.
- Cross-lib: not computed in this minimal iteration; therefore a promotional
  `winner` is impossible even if all other gates pass `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If best config does not beat same-asset buy-and-hold Sharpe, the family is a
  fail even if some statistical gates pass.
- If IS MCPT or WF MCPT fails, do not tune RSI thresholds locally in this study
  without a new mechanism `[testing_tuning, p.327-335]`.
- If PBO or DSR fails, the family is not a valid strategy under the mandate.
- If data are missing for any required ETF, mark `data_blocked` instead of
  substituting a new universe.

## Trial Accounting

- `cumulative_n_trials_before = 12`
- `n_trials_this_iteration = 4`
- `cumulative_n_trials_after = 16`
