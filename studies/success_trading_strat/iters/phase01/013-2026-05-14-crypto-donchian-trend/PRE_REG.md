# PRE_REG — 013 crypto Donchian trend

## Hypothesis

Pivot away from the fragile VIX-managed family into a different asset class and
mechanism: BTC/ETH Donchian breakout trend following with a cash sleeve. The
economic thesis is that crypto trends can persist after breakouts, while a
simple Donchian ensemble is a literature-grounded baseline rather than another
local parameter tweak `[paper.zarattini_2025_crypto_trends, §methodology]`,
`[testing_tuning, p.327-335]`.

The local Tiingo crypto cache is known to be stale/weekend-limited in this repo.
Conservative rule: use only common dated observations with `SHV`; if common
history is insufficient or ends before 2026-03-31, mark `data_blocked` or record
the staleness caveat and do not allow `winner` promotion
`[paper.zarattini_2025_crypto_trends, §applicability-to-market-lab]`.

## Data And Window

- Local cache: `data/tiingo/daily/prices/btcusd.parquet`,
  `data/tiingo/daily/prices/ethusd.parquet`, `data/tiingo/daily/prices/SHV.parquet`.
- Window: common intersection from `2016-01-01` onward, truncated by local data
  availability.
- Execution timing: signal is computed on prior prices and applied with a one-bar
  lag; no same-close execution claim `[advances_fin_ml, p.196-202]`.

## Exact Configs

Four fixed configs, no intra-iteration redesign:

| name | assets | Donchian lookback | selection | defensive |
|---|---|---:|---|---|
| `btc_don20` | `BTCUSD` | 20 | invest if prior close > prior rolling high | `SHV` |
| `btc_don55` | `BTCUSD` | 55 | invest if prior close > prior rolling high | `SHV` |
| `eth_don20` | `ETHUSD` | 20 | invest if prior close > prior rolling high | `SHV` |
| `eth_don55` | `ETHUSD` | 55 | invest if prior close > prior rolling high | `SHV` |

Donchian lookbacks are short/medium trend breakout baselines rather than an
optimized grid `[paper.zarattini_2025_crypto_trends, §methodology]`.

## Benchmark

- Same-asset buy-and-hold for single-asset configs.
- Secondary reference: equal-weight `BTCUSD/ETHUSD` buy-and-hold over the common
  window.
- Economic gate requires best config Sharpe to exceed its same-asset buy-and-hold
  Sharpe; CAGR/MDD are classification only per mandate.

## Planned Gates

- IS MCPT: 200 permutations, pass only if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT: 100 permutations, pass if `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO: 8-block PBO over 4 configs, pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR: pass if `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: annual rolling test windows, pass if at least 6 positive windows
  and at least 6/8 if 8+ windows exist `[testing_tuning, p.148-150]`.
- OOS: final 20% return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 trading observations positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% mean daily return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy implementation CAGR within ±3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If required parquet files are missing, status is `data_blocked` and `n_trials=0`.
- If crypto common history is too short for walk-forward/MCPT, status cannot be
  `winner`.
- If local crypto data are stale before 2026-03-31, record the caveat and block
  `winner` even if metrics pass.
- If PBO or DSR fails, verdict is `fail` regardless of economic metrics.

## Trial Accounting

- `cumulative_n_trials` before: 36.
- New strategy configs: 4.
- `cumulative_n_trials` after planned run: 40.
