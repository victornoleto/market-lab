# PRE_REG — 008 VXX volatility-carry proxy

## Hypothesis

Short-volatility ETP decay can act as a long-only risk-on filter for equity ETFs:
when trailing `VXX` return is negative, volatility carry/roll pressure is benign
enough to hold `SPY` or `QQQ`; otherwise hold `SHV`. Carry premia are
negative-skewed, so promotion requires MCPT plus repo hard gates
`[systematic_trading, p.32-35]`, `[systematic_trading, p.119]`,
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

Iteration 007 was blocked because `VIXY` data were absent. Before this
pre-registration, `test -f` confirmed these local cache files exist:
`VXX.parquet`, `SPY.parquet`, `QQQ.parquet`, `SHV.parquet`. This is a new,
explicit `VXX` registration, not a substitution inside iteration 007
`[testing_tuning, p.327-335]`.

## Data And Window

- Source: local Tiingo daily adjusted-close parquet cache under
  `data/tiingo/daily/prices/`.
- Assets: `VXX`, `SPY`, `QQQ`, `SHV`.
- Common-date window: from `2012-01-01` onward after inner join.
- Execution timing: signal computed on close and shifted by one trading day before
  applying returns to avoid same-close lookahead `[quant_trading_chan, p.51]`.
- Survivorship/disclaimer: Tiingo ETF cache only; this is research evidence, not
  live authorization.

## Configs

Exactly 4 configs, no additions after test:

| config | risk asset | signal asset | rule |
|---|---:|---:|---|
| `vxx_neg21_spy` | `SPY` | `VXX` | hold risk asset if `VXX` 21-trading-day return < 0, else `SHV` |
| `vxx_neg63_spy` | `SPY` | `VXX` | hold risk asset if `VXX` 63-trading-day return < 0, else `SHV` |
| `vxx_neg63_qqq` | `QQQ` | `VXX` | hold risk asset if `VXX` 63-trading-day return < 0, else `SHV` |
| `vxx_neg126_spy` | `SPY` | `VXX` | hold risk asset if `VXX` 126-trading-day return < 0, else `SHV` |

Lookbacks retain the prior blocked hypothesis family and represent roughly 1, 3
and 6 trading months; no local tuning beyond this small grid
`[systematic_trading, p.185-188]`, `[testing_tuning, p.327-335]`.

## Benchmark

- Primary economic benchmark: same risk asset buy-and-hold on the aligned result
  index (`SPY` for SPY configs, `QQQ` for QQQ config).
- Secondary benchmark: `SPY` buy-and-hold on the aligned result index.
- Economic pass requires the selected best config Sharpe to exceed the same-asset
  benchmark and CAGR to be positive; CAGR/MDD remain warning tiers, not hard
  gates per mandate.

## Planned Gates

- IS MCPT on selected best fixed config: 200 permutations, pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT on selected best fixed config: 100 permutations, pass if `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO across the 4 pre-registered configs with 8 CSCV blocks, pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR on selected best config with cumulative trials after this iteration,
  pass if `p < 0.05` `[advances_fin_ml, p.222-223]`.
- WF: at least 8 windows and at least 6 positive windows
  `[testing_tuning, p.148-150]`.
- OOS: final 20% of best returns positive `[advances_fin_ml, p.196-202]`.
- FWD stress: last 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: stationary bootstrap 99.9% CI low of mean daily return > 0
  `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy implementation CAGR within +/-3pp; fail if not
  computed or not concordant `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If any required parquet file is missing or common history is insufficient, return
  `data_blocked` with `n_trials=0`.
- If best config does not beat same-asset Sharpe, verdict is `fail` even if some
  validation gates pass.
- If PBO or DSR fails, verdict cannot be `winner`.
- If MCPT fails, do not tune this family inside the same iteration.
- Do not substitute another volatility ticker after this pre-registration
  `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials_before = 16`.
- `n_trials = 4` if data load succeeds and configs are evaluated.
- `cumulative_n_trials_after = 20`.
