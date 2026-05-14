# PRE_REG — 026 sector risk appetite

## Hypothesis

Equity exposure may be more robust when cyclical/growth sectors lead defensive
sectors. This iteration tests sector relative-strength as a distinct intermarket
risk-appetite source: `XLY/XLP` and `XLK/XLU` ratios gate `SPY`/`QQQ` exposure,
otherwise capital sits in `SHV`. Relative strength and intermarket confirmation are
classical technical inputs, but any optimized selection is suspect until MCPT, PBO
and DSR clear `[trading_systems_methods, p.13]`, `[trading_systems_methods,
p.542-544]`, `[testing_tuning, p.327-335]`.

## Exact Configs

Four configs, all one-bar lagged and all counted as trials:

| name | asset | numerator | denominator | ratio momentum lookback |
|---|---|---|---|---:|
| `spy_xly_xlp_m63` | `SPY` | `XLY` | `XLP` | 63 |
| `qqq_xlk_xlu_m63` | `QQQ` | `XLK` | `XLU` | 63 |
| `spy_xly_xlp_m126` | `SPY` | `XLY` | `XLP` | 126 |
| `qqq_xlk_xlu_m126` | `QQQ` | `XLK` | `XLU` | 126 |

Risk-on rule: hold `asset` when `ratio / ratio.shift(lookback) - 1 > 0`, evaluated
with a one-bar lag. Otherwise hold `SHV`. No volatility targeting, leverage, cost
model or local threshold tuning.

## Data And Window

Local Tiingo daily adjusted closes from `data/tiingo/daily/prices/` for `SPY`,
`QQQ`, `SHV`, `XLY`, `XLP`, `XLK` and `XLU`. Common inner-join window starts at
`2010-01-01` and must end no earlier than `2026-03-31` to avoid stale-data claims.

## Benchmark

Same-window same-asset buy-and-hold: `SPY` configs compare to `SPY`; `QQQ` configs
compare to `QQQ`.

## Planned Gates

- Economic Sharpe versus same-asset benchmark.
- IS MCPT on the selected best fixed config, 200 reps, pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT on the selected best fixed config, 100 reps, pass `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO across the 4 configs with 8 blocks, pass `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR using cumulative trials after this iteration, pass `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward annual windows, OOS final 20%, latest 63d FWD stress, bootstrap
  99.9% mean daily CI low, and independent NumPy-style CAGR cross-check
  `[advances_fin_ml, p.196-202]`, `[testing_tuning, p.246-247]`.

## Kill Rules

- If required sector ETF data are absent/stale, stop as `data_blocked` with
  `n_trials=0`.
- If IS MCPT, WF MCPT, PBO or DSR fails, record `fail`; do not tune lookbacks,
  sector pairs or thresholds inside this iteration.
- If the family only reduces drawdown but loses Sharpe to same-asset buy-and-hold,
  record `fail` and do not promote.

## Trial Accounting

- `cumulative_n_trials` before: 88.
- `n_trials` planned: 4.
- `cumulative_n_trials` after if data are available: 92.

## Ambiguity Note

The conservative choice is to treat sector pair and lookback selection as four
explicit trials and to use `92` for DSR if all configs run. Pre-existing unrelated
worktree changes are not reverted or modified.
