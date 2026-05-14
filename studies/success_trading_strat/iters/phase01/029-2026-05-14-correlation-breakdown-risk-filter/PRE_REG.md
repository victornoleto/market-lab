# PRE_REG - 029 Correlation Breakdown Risk Filter

## Hypothesis

When equity and Treasury returns become positively correlated, the usual stock/bond
diversification hedge is impaired. A sparse risk-off filter that holds `SPY` or
`QQQ` only when lagged rolling equity/Treasury correlation is below zero may reduce
tail risk enough to improve risk-adjusted return versus same-asset buy-and-hold
`[risk_parity, p.69, p.80-81]`, `[systematic_trading, p.170-171]`,
`[trading_systems_methods, p.1085-1091]`.

This is a different information source from the prior Gayed LETF family: it uses
cross-asset dependence state, not price-vs-moving-average, VIX, volume, breadth,
seasonality, or yield carry. The design is intentionally small because DSR uses
cumulative trial accounting `[advances_fin_ml, p.222-223]`.

## Data And Window

- Source: local Tiingo daily adjusted close parquet cache.
- Required tickers: `SPY`, `QQQ`, `TLT`, `SHV`.
- Common aligned window: maximum overlap available through the freshest common end
  date, expected 2006-07-26 through 2026-05-13 if all files are present.
- Execution: daily close-to-close returns; all signals use one-bar lag.

## Exact Configs

Four configs, no additions after testing:

1. `spy_corr63_lt0`: hold `SPY` if lagged 63d rolling corr(`SPY`,`TLT`) < 0, else `SHV`.
2. `spy_corr126_lt0`: hold `SPY` if lagged 126d rolling corr(`SPY`,`TLT`) < 0, else `SHV`.
3. `qqq_corr63_lt0`: hold `QQQ` if lagged 63d rolling corr(`QQQ`,`TLT`) < 0, else `SHV`.
4. `qqq_corr126_lt0`: hold `QQQ` if lagged 126d rolling corr(`QQQ`,`TLT`) < 0, else `SHV`.

The 63d and 126d windows are quarterly/semiannual regime estimates, chosen as
coarse horizons rather than optimized local thresholds `[trading_systems_methods,
p.939]`. The zero threshold is economic: negative stock/bond correlation means
Treasuries are still diversifying; positive correlation marks risk-parity hedge
breakdown `[risk_parity, p.80-81]`.

## Benchmark

- `SPY` configs compare to same-window `SPY` buy-and-hold.
- `QQQ` configs compare to same-window `QQQ` buy-and-hold.
- Winner candidate must beat same-asset benchmark Sharpe and pass all gates.

## Planned Gates

- Data freshness: all required series present and common end date recent.
- Benchmark Sharpe comparison.
- IS MCPT with 200 permutations, pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO across the 4 configs, pass `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR on the best config with cumulative trials after this iteration, pass
  `p < 0.05` `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6 positive test windows.
- OOS: final 20% return positive.
- FWD stress: latest 63 trading days positive.
- Bootstrap: 99.9% stationary-bootstrap mean daily return CI low > 0.
- Cross-lib: independent vectorized recomputation CAGR within +/-3pp.

## Kill Rules

- If any required ticker parquet is absent, stop as `data_blocked`; do not
  substitute `IEF`, `AGG`, or another bond proxy after preregistration.
- If the family fails PBO/DSR/MCPT, mark as dead end; do not tune correlation
  windows, thresholds, or add VIX/price filters locally `[testing_tuning,
  p.327-335]`.
- If benchmark Sharpe fails, verdict cannot be `winner` even if some hard gates pass.
- Capital remains 100% Plano C; no deploy implication.

## Trial Accounting

- `cumulative_n_trials` before: 96.
- New strategy configs: 4.
- `cumulative_n_trials` after if tested: 100.
