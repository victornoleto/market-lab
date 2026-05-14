# PRE_REG — 019 yield-carry rotation

## Hypothesis

Test a small carry/yield family that allocates to the asset with the stronger
ex-ante carry proxy instead of another local technical-price signal. Carry is a
distinct return source with negative-skew risk, so it must pass MCPT plus the repo
hard gates before any winner claim `[systematic_trading, p.32-35]`,
`[systematic_trading, p.119]`, `[systematic_trading, p.288]`,
`[testing_tuning, p.318-320]`.

## Data And Window

- Prices: local Tiingo daily adjusted close for `SPY`, `TLT`, `IEF`, `SHV` under
  `data/tiingo/daily/prices/`.
- Yield inputs: existing loader `studies.letf_rotation_hunt.core.data_loader_yields`
  for `3m`, `10y`, `30y` constant-maturity Treasury yields and `SPY` trailing
  dividend yield. If these cannot be loaded honestly, close as `data_blocked` and
  do not substitute after registration.
- Window: common daily observations from 2010-01-01 through the latest shared
  available date.
- Staleness kill: latest common date must be at least 2026-03-31.

## Exact Configs

1. `spy_div_gt_cash_tlt_term`: risk-on `SPY` if `SPY_dividend_yield > 3m_yield`,
   otherwise `TLT` if `30y_yield > 3m_yield`, else `SHV`.
2. `spy_div_gt_cash_ief_term`: same equity gate, but bond sleeve `IEF` if
   `10y_yield > 3m_yield`, else `SHV`.
3. `bond_steep_tlt_else_shv`: `TLT` if `30y_yield - 3m_yield > 0`, else `SHV`.
4. `bond_steep_ief_else_shv`: `IEF` if `10y_yield - 3m_yield > 0`, else `SHV`.

All signals are lagged one trading day. No parameter additions after results.

## Benchmark

- Configs containing `SPY`: same-window 60/40 `SPY/TLT` or `SPY/IEF` benchmark,
  matching the bond sleeve.
- Bond-only configs: same-window `SHV` benchmark.
- Economic gate: best strategy Sharpe must beat its pre-registered benchmark.

## Gates Planned

- Data freshness.
- Economic Sharpe vs benchmark.
- IS MCPT on fixed best config: 200 permutations, pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT on fixed best config: 100 permutations, pass `p <= 0.05`.
- PBO over the 4 pre-registered configs with 8 blocks, pass `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR on best config with cumulative trials after this iteration, pass `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: annual OOS windows after 4-year train; require at least 6 positive
  windows when 8+ windows exist `[testing_tuning, p.148-150]`.
- Single-block OOS final 20% positive.
- Latest 63-trading-day FWD stress positive.
- Bootstrap 99.9% mean daily return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib NumPy-style recomputation CAGR delta <= 3pp.

## Kill Rules

- Missing or unusable yield inputs => `data_blocked`, `n_trials=0`.
- Missing Tiingo price input => `data_blocked`, `n_trials=0`.
- Any PBO/DSR/MCPT hard-gate failure => no winner.
- Do not tune thresholds, yield tenors, or sleeves after observing results
  `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials` before: 60.
- Planned `n_trials`: 4 if data load succeeds, else 0.
- `cumulative_n_trials` after: 64 if tested, else 60.
