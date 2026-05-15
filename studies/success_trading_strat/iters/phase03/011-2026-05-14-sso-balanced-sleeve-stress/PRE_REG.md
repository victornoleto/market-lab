# PRE_REG - Phase 3 Iteration 011

## Hypothesis

Stress the fixed levered balanced-sleeve economic beater from iteration 010 by
replacing `UPRO` with lower-leverage real `SSO`. The return engine remains embedded
equity leverage plus structural diversification, not a defensive long/flat timing
filter. Lower embedded leverage should reduce path dependency but may also reduce
the upside engine; this iteration tests whether the mechanism still beats
buy-and-hold in CAGR and terminal wealth `[leverage_for_the_long_run, p.13]`,
`[systematic_trading, p.137-148]`, `[leverage_space, p.149-167]`.

## Data And Window

- Source: physical Tiingo daily parquet files under `data/tiingo/daily/prices/`.
- Required traded assets: `SSO`, `TLT`, `GLD`.
- Required benchmarks/context: `SPY`, `SHV`.
- Window: maximum common adjusted-close history across required assets, expected to
  start no earlier than `SSO` inception and end at latest shared date.
- Signals: none; fixed weights with one-day realized close-to-close returns.
- Rebalance: calendar month or quarter starts, implemented from prior close returns.

## Configs

Four pre-registered configs, each one trial:

1. `sso60_tlt30_gld10_monthly`: 60% `SSO`, 30% `TLT`, 10% `GLD`, monthly rebalance.
2. `sso65_tlt25_gld10_monthly`: 65% `SSO`, 25% `TLT`, 10% `GLD`, monthly rebalance.
3. `sso70_tlt20_gld10_quarterly`: 70% `SSO`, 20% `TLT`, 10% `GLD`, quarterly rebalance.
4. `sso75_tlt15_gld10_quarterly`: 75% `SSO`, 15% `TLT`, 10% `GLD`, quarterly rebalance.

## Benchmarks

- Conservative primary economic benchmark: both `SPY` buy-and-hold and equal-weight
  `SSO/TLT/GLD` buy-and-hold on the same aligned dates must be beaten in CAGR and
  terminal wealth. This conservative interpretation is chosen because the sleeve is
  both S&P LETF-based and multi-asset.
- Opportunity/context benchmarks: `SSO`, `TLT`, `GLD`, `SHV` buy-and-hold.
- SPY buy-and-hold opportunity benchmark is also reported explicitly.

## Kill Rule

If strategy CAGR or terminal wealth is less than or equal to either primary
buy-and-hold benchmark (`SPY` or equal-weight `SSO/TLT/GLD`) on aligned dates, the
iteration closes `fail`. No `economic_beater_not_validated`, `candidate_watchlist`,
`paper_trade_candidate` or `strict_winner` label is allowed.

## Planned Gates

- IS MCPT with 200 joint-return permutations; pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations, 756-trading-day train, 252-day test, 252-day step;
  pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` over the four configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward at least 6 positive windows out of at least 8
  `[testing_tuning, p.148-150]`.
- OOS last 20% positive; latest 63 trading days positive
  `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% daily mean CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/reference implementation CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Trial Accounting

- `cumulative_n_trials` before: 264.
- New strategy trials: 4.
- `cumulative_n_trials` after: 268.

## Additional Kill Rules

- Missing required parquet or close column => `data_blocked`.
- MDD worse than 1.5x the worse primary benchmark MDD blocks `strict_winner` even if
  other gates pass.
- If validation fails after economic pass, status can be at most
  `economic_beater_not_validated`; no deploy implication.
