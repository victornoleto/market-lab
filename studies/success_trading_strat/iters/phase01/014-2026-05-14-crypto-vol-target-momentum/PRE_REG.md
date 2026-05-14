# PRE_REG — 014 crypto volatility-targeted momentum

## Hypothesis

Crypto trend-following in iteration 013 had strong MCPT/PBO/DSR diagnostics but
failed recent FWD stress and minimum WF positives. This iteration pivots to a new
economic mechanism: use simple trailing momentum to select BTC/ETH exposure, then
scale exposure by realized volatility with no leverage above 1.0. The hypothesis
is that crypto trend premia need volatility-standardized sizing to avoid recent
tail damage while preserving positive trend participation `[systematic_trading,
p.40]`, `[systematic_trading, p.137-148]`, `[systematic_trading, p.196-197]`,
`[paper.zarattini_2025_crypto_trends, §methodology]`.

This is not a Donchian lookback optimization. No Donchian breakout rule is tested.

## Exact Configs

All configs use one-bar lagged signals, `SHV` for unused capital/cash return,
100-trading-day realized volatility lookback, 20% annualized volatility target,
and max crypto exposure `1.0` `[systematic_trading, p.196-197]`.

1. `btc_mom63_vt20`: BTC only, 63d trailing return must be positive.
2. `eth_mom63_vt20`: ETH only, 63d trailing return must be positive.
3. `crypto_top1_mom63_vt20`: choose the stronger positive 63d momentum asset among BTC/ETH.
4. `crypto_top1_mom126_vt20`: choose the stronger positive 126d momentum asset among BTC/ETH.

## Data And Window

Local Tiingo daily cache:

- `data/tiingo/daily/prices/btcusd.parquet`
- `data/tiingo/daily/prices/ethusd.parquet`
- `data/tiingo/daily/prices/SHV.parquet`

Common aligned window starts `2016-01-01` or later, with data freshness gate
requiring common end date on/after `2026-03-31`. If required files are missing or
common history is too short, close `data_blocked` with `n_trials=0`.

## Benchmark

Single-asset configs compare Sharpe against same-asset buy-and-hold over the same
return index. Cross-asset configs compare Sharpe against 50/50 BTC/ETH
buy-and-hold over the same return index. CAGR/MDD are reported as tiers only;
Sharpe/economic comparison is not a substitute for hard gates.

## Planned Gates

- Data freshness: common end date >= `2026-03-31`.
- Economic Sharpe vs pre-registered benchmark.
- IS MCPT: 200 reps, pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: 100 reps, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO over 4 configs with 8 blocks, pass `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR with cumulative trials after this iteration, pass `p < 0.05` `[advances_fin_ml, p.222-223]`.
- Walk-forward: positive windows required as in the runner; if fewer than 8 windows exist, require all windows positive by conservative rule.
- OOS final 20% return > 0 `[advances_fin_ml, p.196-202]`.
- Latest 63-observation FWD stress > 0 `[advances_fin_ml, p.196-202]`.
- Stationary bootstrap 99.9% mean daily CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib NumPy/pandas CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If data is missing/stale, do not substitute another asset after registration.
- If best config fails PBO or DSR, status is `fail` regardless of economics.
- If MCPT fails, do not tune momentum lookbacks in this iteration.
- If FWD 63d remains negative, do not mark as winner even if PBO/DSR pass.
- Do not deploy or change capital allocation; mandate remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials` before: 40.
- `n_trials` planned: 4.
- `cumulative_n_trials` after if tested: 44.
