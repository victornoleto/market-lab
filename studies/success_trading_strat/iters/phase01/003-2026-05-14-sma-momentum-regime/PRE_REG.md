# PRE_REG — 003 sma momentum regime

## Hypothesis

Daily long-only equity-index regime following may improve risk-adjusted returns by
holding a broad equity ETF only when both long-trend and medium-term momentum are
positive, otherwise holding short Treasury/cash. The trend filter uses SMA because
moving-average regime filters are the canonical LRS mechanism
`[leverage_for_the_long_run, p.13, p.16]`. The momentum lookback uses 63 trading
days as a quarterly trend horizon, consistent with time-series momentum/ranking
discipline rather than intraday noise `[stocks_on_the_move, p.76-77]`. No leverage,
shorting or capital deployment is authorized.

## Data And Window

- Source: local Tiingo daily cache through `TiingoStorage`.
- Risk assets: `SPY`, `QQQ`.
- Defensive asset: `SHV` when available; fallback to zero daily return if the
  cache is missing or shorter.
- Window: common daily overlap from 2008-01-01 through latest cached date, after
  warmup.
- Execution: signal from close `t-1` applied to return from `t-1` to `t`, avoiding
  same-close lookahead `[advances_fin_ml, p.31-34]`.

## Exact Configs

Four configs, counted as four strategy trials:

| config | risk_asset | sma_days | momentum_days | defensive |
|---|---|---:|---:|---|
| `spy_sma100_mom63` | SPY | 100 | 63 | SHV/cash |
| `spy_sma200_mom63` | SPY | 200 | 63 | SHV/cash |
| `qqq_sma100_mom63` | QQQ | 100 | 63 | SHV/cash |
| `qqq_sma200_mom63` | QQQ | 200 | 63 | SHV/cash |

Benchmark for each config is buy-and-hold of the same risk asset over the same
post-warmup dates. The headline benchmark is SPY buy-and-hold over the shared
window.

## Planned Gates

- Economic screen: best config must beat its same-asset buy-and-hold Sharpe and
  have positive CAGR.
- IS MCPT: fixed-rule MCPT on the best config with 200 permutations, `p <= 0.01`
  required for promotion `[testing_tuning, p.318-320]`.
- WF-MCPT: rolling 4y train / 1y test / 1y step with 200 permutations,
  `p <= 0.05` required for promotion `[testing_tuning, p.148-150]`,
  `[testing_tuning, p.318-320]`.
- PBO: CSCV over the four config return columns, 8 blocks, pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR: best config with `n_trials = cumulative_n_trials_after = 4`, pass if
  `p < 0.05` `[advances_fin_ml, p.222-223]`.
- WF: at least 6/8 positive OOS windows when enough windows exist
  `[testing_tuning, p.148-150]`.
- OOS: final 20% of returns positive `[advances_fin_ml, p.196-202]`.
- FWD stress: final 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% simple bootstrap CI low of mean daily return > 0
  `[testing_tuning, p.246-247]`.
- Cross-lib: not promotional in this iteration; if other gates pass, it remains
  `promising_not_validated` until an independent runner is added
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If no config beats its same-asset buy-and-hold Sharpe, close as `fail`.
- If PBO or DSR fails, no local tuning of SMA/momentum in the next step without a
  new mechanism `[testing_tuning, p.327-335]`.
- If MCPT rejects the real path, treat the family as a dead-end for this study.
- Do not touch `docs/investment-mandate.md`; capital remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials_before`: 0
- `n_trials_this_iteration`: 4
- `cumulative_n_trials_after`: 4
