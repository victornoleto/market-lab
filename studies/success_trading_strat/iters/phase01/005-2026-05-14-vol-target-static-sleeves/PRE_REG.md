# PRE_REG — 005 volatility-targeted static sleeves

## Hypothesis

Prior iterations failed local timing and ETF momentum. This iteration pivots to a
different mechanism: fixed multi-asset sleeves with volatility targeting. The
idea is not to forecast winners, but to standardize risk through time and across
asset mixes `[systematic_trading, p.40]`, using a slow 20-week volatility estimate
to reduce turnover `[systematic_trading, p.196-197]`. The volatility target is
kept at 10% annualized and leverage is capped at 1.5x because backtested Sharpe
should not be used to justify aggressive risk targets `[systematic_trading,
p.146]`.

## Data And Window

- Source: local Tiingo daily adjusted closes in `data/tiingo/daily/prices/`.
- Assets: `SPY`, `QQQ`, `IEF`, `GLD`, `SHV`.
- Window: common adjusted-close history from 2008-01-01 through latest available
  cache date.
- Execution: daily sleeve returns use close-to-close returns; volatility scale is
  shifted by one bar to avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

## Exact Configs

All configs use:

- `vol_lookback=100` trading days, a 20-week proxy `[systematic_trading,
  p.196-197]`.
- `target_vol=0.10` annualized `[systematic_trading, p.137-148]`.
- `max_leverage=1.5` `[systematic_trading, p.146]`.
- residual cash from scale below 1.0 earns `SHV` daily returns.

Configs:

| name | weights |
|---|---|
| `vt_60spy_40ief` | 60% `SPY`, 40% `IEF` |
| `vt_45spy_35ief_20gld` | 45% `SPY`, 35% `IEF`, 20% `GLD` |
| `vt_40spy_20qqq_20ief_20gld` | 40% `SPY`, 20% `QQQ`, 20% `IEF`, 20% `GLD` |
| `vt_35spy_15qqq_30ief_20gld` | 35% `SPY`, 15% `QQQ`, 30% `IEF`, 20% `GLD` |

## Benchmark

Primary benchmark: unscaled 60/40 `SPY`/`IEF` static sleeve on the same window.
Secondary benchmark: `SPY` buy-and-hold.

## Gates Planned

- Economic: best config must beat primary benchmark on Sharpe and have positive
  CAGR; CAGR/MDD are reported as warning tiers, not hard gates.
- IS MCPT: 200 row-permutation reps, pass if `p <= 0.01` `[testing_tuning,
  p.318-320]`.
- WF MCPT: 100 reps, pass if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO: 8-block PBO over the 4 configs, pass if `<0.5` `[advances_fin_ml,
  p.208-211]`.
- DSR: cumulative `n_trials=12` after this iteration, pass if `p<0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: train 1008 bars, test 252, step 252; require at least 6 positive
  windows if 8+ windows exist `[testing_tuning, p.148-150]`.
- OOS: final 20% total return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: stationary bootstrap 99.9% mean CI low > 0 `[testing_tuning,
  p.246-247]`.
- Cross-lib: intentionally not computed in this minimal iteration, so `winner`
  cannot be true even if other gates pass.

## Kill Rules

- If the best config fails primary benchmark Sharpe, record `fail` and do not tune
  vol targets locally.
- If MCPT fails, treat the result as path-order dependent and do not promote.
- If PBO or DSR fails, hard-block promotion regardless of economic metrics.
- If results are merely drawdown-improving but return/Sharpe-lagging, mark the
  family as defensive allocation evidence, not a trading winner.

## Trial Accounting

- `cumulative_n_trials_before=8`.
- `n_trials=4`.
- `cumulative_n_trials_after=12`.
