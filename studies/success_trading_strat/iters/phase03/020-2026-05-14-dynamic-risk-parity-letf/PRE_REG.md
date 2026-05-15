# PRE_REG - Phase 3 Iteration 020

## Hypothesis

Test a dynamic risk-parity LETF sleeve: allocate monthly across a levered equity ETF
(`UPRO` or `SSO`), `TLT` and `GLD` using lagged inverse realized volatility, with
optional modest gross exposure and explicit financing drag. The return engine is
controlled leverage plus diversification/risk-budgeting, not a daily defensive
long/flat filter `[leverage_for_the_long_run, p.13]`, `[risk_parity, p.80-81]`,
`[systematic_trading, p.137-148]`.

This is intentionally distinct from prior static balanced sleeves/HFEA tests: weights
are determined by trailing vol and rebalanced monthly, rather than fixed percentages.
If it fails, do not tune lookbacks, gross caps or asset sets locally
`[testing_tuning, p.327-335]`.

## Data And Window

Physical daily parquet files to audit before testing:

- `SPY`, `UPRO`, `SSO`, `TLT`, `GLD`, `SHV`.

Use adjusted close when available. The aligned test window starts after all required
assets have valid adjusted closes and after the pre-registered volatility warmup.
No synthetic LETF, no intraday data and no post-result substitutions.

## Exact Configs

Four pre-registered configs, each one strategy trial:

1. `upro_rp63_g100`: universe `UPRO/TLT/GLD`, 63d realized-vol inverse weights, gross `1.00`.
2. `upro_rp126_g125`: universe `UPRO/TLT/GLD`, 126d realized-vol inverse weights, gross `1.25`.
3. `sso_rp63_g100`: universe `SSO/TLT/GLD`, 63d realized-vol inverse weights, gross `1.00`.
4. `sso_rp126_g125`: universe `SSO/TLT/GLD`, 126d realized-vol inverse weights, gross `1.25`.

Financing drag: `5%` annualized on gross exposure above `1.0`; no tax model.
Signals and weights are lagged one trading day to avoid lookahead.

## Benchmarks

Primary Phase 3 benchmark hierarchy:

- For `UPRO` configs: must beat both `SPY` buy-and-hold and equal-weight
  `UPRO/TLT/GLD` buy-and-hold in CAGR and terminal wealth on aligned dates.
- For `SSO` configs: must beat both `SPY` buy-and-hold and equal-weight
  `SSO/TLT/GLD` buy-and-hold in CAGR and terminal wealth on aligned dates.
- `SHV` and the traded LETF buy-and-hold are context only.

SPY buy-and-hold is the opportunity benchmark required by Phase 3.

## Kill Rules

- If best strategy CAGR <= its primary buy-and-hold CAGR, close `fail`.
- If best strategy terminal wealth <= its primary buy-and-hold terminal wealth,
  close `fail`.
- If best strategy CAGR <= `SPY` buy-and-hold CAGR or terminal wealth <= `SPY`
  buy-and-hold terminal wealth, close `fail`.
- If MDD is worse than `1.5x` the worse drawdown of `SPY` and equal-weight primary
  benchmark, block `strict_winner` even if CAGR passes.
- Any PBO >= 0.5, DSR p >= 0.05, insufficient WF, negative OOS, negative latest
  FWD, failed bootstrap or cross-lib mismatch blocks `strict_winner`
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Planned Gates

- IS MCPT: 200 joint row permutations, pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: 100 joint row permutations after initial train, pass `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO with 10 blocks, pass `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR with cumulative trials after this iteration, pass `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward windows: train 756, test 252, step 252, at least 8 windows and 6
  positive `[testing_tuning, p.148-150]`.
- OOS: final 20% total return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% mean daily return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/reference parity: vectorized reference CAGR within +/-3pp
  `[advances_fin_ml, p.31-34]`.

## Trial Accounting

- `cumulative_n_trials` before: `292`.
- New strategy trials: `4`.
- `cumulative_n_trials` after: `296`.

## Conservative Ambiguity Handling

If a config from a higher-vol universe and a lower-vol universe tie on terminal
wealth, select the lower-MDD config as best. If any required daily file is missing
or lacks adjusted/regular close, close `data_blocked` and consume zero trials.
