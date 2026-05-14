# PRE_REG — 004 cross-sectional ETF momentum

## Hypothesis

Cross-sectional ETF selection may be more robust than single-asset SMA timing
because it chooses the strongest liquid asset class rather than only deciding
risk-on/risk-off for one index. The signal is trailing total return divided by
realized volatility, a conservative momentum/risk normalization consistent with
relative-strength momentum and volatility-aware sizing `[stocks_on_the_move,
p.76-77]`, `[systematic_trading, p.185-188]`. Monthly rebalancing limits
turnover and reduces signal noise `[testing_tuning, p.148-150]`.

This is research only. Capital remains 100% Plano C and no deployment is
authorized by this iteration.

## Data And Window

- Source: local Tiingo daily adjusted close cache in `data/tiingo/daily/prices/`.
- Risk universe: `SPY`, `QQQ`, `IWM`, `TLT`, `GLD`.
- Defensive asset: `SHV` when the average cross-sectional score is not positive.
- Window: common valid daily window from 2008-01-01 through the last common cached
  date, expected near 2026-05-13.
- Execution: signals are computed from data available at the prior close and
  applied to next-day returns. Rebalances occur on month-end signal dates, then
  hold until the next rebalance `[advances_fin_ml, p.31-34]`.

## Exact Configs

Four configs are tested; `n_trials=4`.

| config | lookback_days | top_k | weighting | defensive rule |
|---|---:|---:|---|---|
| `mom63_top1` | 63 | 1 | equal weight selected ETF | hold `SHV` if mean universe score <= 0 |
| `mom63_top2` | 63 | 2 | equal weight selected ETFs | hold `SHV` if mean universe score <= 0 |
| `mom126_top1` | 126 | 1 | equal weight selected ETF | hold `SHV` if mean universe score <= 0 |
| `mom126_top2` | 126 | 2 | equal weight selected ETFs | hold `SHV` if mean universe score <= 0 |

The score is `lookback_total_return / annualized_realized_vol_lookback`.
Realized volatility uses daily simple returns over the same lookback, annualized
by `sqrt(252)` `[systematic_trading, p.185-188]`.

## Benchmark

Primary benchmark: equal-weight buy-and-hold of `SPY`, `QQQ`, `IWM`, `TLT`, and
`GLD` on the same common window. Secondary reference: `SPY` buy-and-hold.

## Planned Gates

- Economic screen: best config should beat primary benchmark on Sharpe and not
  have worse max drawdown; CAGR is reported as warning-tier context, not a hard
  block per mandate.
- IS MCPT on the best fixed config, 200 permutations, `p <= 0.01` required for
  promotion `[testing_tuning, p.318-320]`.
- WF-MCPT on rolling 4-year train / 1-year test / 1-year step, 100 permutations,
  `p <= 0.05` required for promotion `[testing_tuning, p.318-320]`.
- PBO across the 4 configs with 8 blocks; hard gate `<0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR with cumulative trials after this iteration: `8`; hard gate `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6/8 positive OOS windows when enough windows exist
  `[testing_tuning, p.148-150]`.
- OOS: final 20% of daily returns positive `[advances_fin_ml, p.196-202]`.
- FWD stress: final 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% CI low of mean daily return > 0 `[testing_tuning, p.246-247]`.
- Cross-lib: not planned in this minimal iteration; absence blocks `winner`.

## Kill Rules

- If any required ETF is absent or has insufficient common history, stop as
  `data_blocked` rather than substituting a new universe.
- If the best config does not beat the primary benchmark on Sharpe or has worse
  drawdown, status is `fail` even if some statistical gates pass.
- If PBO or DSR fails, status cannot exceed `fail`.
- If MCPT gates fail but economics/PBO/DSR pass, status can be at most
  `promising_not_validated`.
- Do not tune lookbacks, universe or defensive rule after seeing results.

## Trial Accounting

- `cumulative_n_trials` before: 4.
- New strategy/config trials: 4.
- `cumulative_n_trials` after: 8.
