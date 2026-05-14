# PRE_REG — 022 KAMA efficiency regime

## Hypothesis

Kaufman's Efficiency Ratio (ER) measures whether price movement is directional
or noisy, and KAMA adapts smoothing speed to that ER. A daily ETF rule that only
holds `SPY`/`QQQ` when KAMA trend or ER-filtered trend is positive may beat
same-asset buy-and-hold on Sharpe while reducing drawdown, without reusing the
prior SMA/EWMAC/Ehlers/VIX/carry/calendar families `[trading_systems_methods,
p.10-11]`, `[trading_systems_methods, p.780-782]`, `[testing_tuning,
p.327-335]`.

## Data And Window

- Source: local Tiingo daily adjusted close parquet files in `data/tiingo/daily/prices/`.
- Required tickers: `SPY`, `QQQ`, `SHV`.
- Window: common daily observations from `2010-01-01` through the latest common
  available date.
- Staleness kill: block if common data end is before `2026-03-31`.
- Execution lag: all risk-on/off decisions use signals shifted by one trading
  day to avoid same-close look-ahead `[advances_fin_ml, p.196-202]`.

## Exact Configs

1. `spy_kama_slope`: `SPY`; KAMA ER lookback `10`, fast `2`, slow `30`; hold
   `SPY` when lagged KAMA slope is positive, otherwise `SHV`.
2. `qqq_kama_slope`: same as config 1 on `QQQ`.
3. `spy_kama_er20`: `SPY`; same KAMA; require lagged positive KAMA slope and
   lagged ER(10) >= `0.20`, otherwise `SHV`.
4. `qqq_kama_er20`: same as config 3 on `QQQ`.

The 10/2/30 KAMA parameters are Kaufman's standard ER/KAMA example, and ER 0.20
is a conservative minimum directional-efficiency filter chosen before testing
to avoid trading low-direction/noisy regimes `[trading_systems_methods,
p.780-782]`, `[trading_systems_methods, p.10-11]`.

## Benchmark

Each config is compared to same-window buy-and-hold of its own risky asset
(`SPY` or `QQQ`) on CAGR, Sharpe and MDD. Promotional economics require strategy
Sharpe greater than same-asset buy-and-hold; CAGR/MDD remain tier/warning metrics
under the mandate.

## Planned Gates

- Data freshness: common data end >= `2026-03-31`.
- Economic Sharpe vs same-asset benchmark.
- IS MCPT on the selected best config: 200 row-order permutations of daily return
  rows, recomputing KAMA/ER and strategy path each time; pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT on selected best config: 100 permutations after the first train window;
  pass if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO across the 4 pre-registered configs with 8 blocks; pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR on the best config using cumulative trials after this iteration; pass if
  `p < 0.05` `[advances_fin_ml, p.222-223]`.
- Walk-forward: 1008-trading-day train, 252-day test, 252-day step; require at
  least 6 positive test windows when at least 8 windows exist `[testing_tuning,
  p.148-150]`.
- OOS: final 20% of observations positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 observations positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: stationary bootstrap 2,000 samples; 99.9% mean-daily CI low > 0
  `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy-style implementation CAGR within +/-3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If any required ticker parquet is missing or stale, close `data_blocked` with
  `n_trials=0`.
- If KAMA/ER rules fail MCPT, PBO or DSR, do not tune ER thresholds, KAMA lengths
  or add filters locally; mark the family as dead-end `[testing_tuning,
  p.327-335]`.
- No live/deploy claim regardless of result; mandate keeps capital 100% Plano C.

## Trial Accounting

- `cumulative_n_trials` before: 72.
- Configs tested: 4.
- `cumulative_n_trials` after: 76.
