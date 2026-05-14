# PRE_REG — 016 credit risk appetite filter

## Hypothesis

Credit-risk appetite can act as a cross-asset regime filter for equity beta: hold
`SPY` or `QQQ` only when the lagged `HYG/IEF` total-return ratio is rising and
the equity asset has positive lagged momentum; otherwise hold `SHV`. The mechanism
is intentionally different from local equity volatility throttles: it uses a
credit-vs-Treasury intermarket proxy plus a simple momentum confirmation.

Rationale and constraints: diversify signals across imperfectly correlated markets
`[systematic_trading, p.42]`, keep the rule small and idea-first rather than
data-mined `[systematic_trading, p.26-27]`, match systematic strategy to market
noise and intermarket risk controls `[trading_systems_methods, p.13]`, and validate
selection bias with MCPT/PBO/DSR `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Exact Configs

All signals are lagged one trading day. Four configs only:

| name | risk asset | credit ratio | credit lookback | asset momentum lookback | defensive asset |
|---|---|---|---:|---:|---|
| `spy_hygief63_m63` | `SPY` | `HYG/IEF` | 63 | 63 | `SHV` |
| `spy_hygief126_m63` | `SPY` | `HYG/IEF` | 126 | 63 | `SHV` |
| `qqq_hygief63_m63` | `QQQ` | `HYG/IEF` | 63 | 63 | `SHV` |
| `qqq_hygief126_m63` | `QQQ` | `HYG/IEF` | 126 | 63 | `SHV` |

Risk-on rule: `lagged_return(HYG/IEF, credit_lookback) > 0` and
`lagged_return(asset, 63) > 0`. Risk-off: `SHV`.

## Data And Window

Local Tiingo adjusted-close cache under `data/tiingo/daily/prices/` for `SPY`,
`QQQ`, `HYG`, `IEF` and `SHV`. Use the common intersection from `2010-01-01`
through the latest common available date. If any required file is missing or the
common data ends before `2026-03-31`, mark `data_blocked` or fail the data gate;
do not substitute a new ticker after pre-registration.

## Benchmark

Same-asset buy-and-hold (`SPY` for SPY configs, `QQQ` for QQQ configs) over the
same post-warmup dates. A winner must beat the benchmark Sharpe; CAGR/MDD are
reported but not hard-blocking per mandate.

## Planned Gates

- Data freshness: common cache end date must be at least `2026-03-31`.
- Economic Sharpe vs benchmark: strategy Sharpe must exceed same-asset buy-hold.
- IS MCPT: 200 full-price permutation reps, pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT: 100 reps after initial training prefix, pass `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO: 8 blocks, pass `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: use cumulative `n_trials=52` after this iteration, pass `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: annual rolling train/test windows, require at least 6 positive
  windows when 8+ windows exist `[testing_tuning, p.148-150]`.
- OOS: final 20% strategy return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 observations positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: stationary bootstrap 99.9% mean-daily CI low > 0
  `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy implementation CAGR within +/-3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- Do not add thresholds, alternate credit ETFs, or new lookbacks after seeing
  results.
- If PBO/DSR/MCPT fail, mark the family as a dead end rather than locally tuning
  the `HYG/IEF` lookback `[testing_tuning, p.327-335]`.
- If data are unavailable, close `data_blocked` with `n_trials=0`.
- No deploy claim; capital remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials` before: 48.
- New strategy configs: 4.
- `cumulative_n_trials` after if data are testable: 52.
