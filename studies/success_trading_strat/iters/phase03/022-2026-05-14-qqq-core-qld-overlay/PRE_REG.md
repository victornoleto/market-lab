# PRE_REG - Phase 3 Iteration 022

## Hypothesis

Test a Nasdaq core-plus-overlay mechanism: hold `QQQ` as a permanent core and add
a partial `QLD` overlay only when lagged `QQQ` momentum is positive and lagged
realized volatility is below a pre-registered ceiling. The return engine is extra
gross exposure in favorable trend/volatility regimes, not stepping aside into cash
`[leverage_for_the_long_run, p.13]`, `[systematic_trading, p.137-148]`.

Momentum is used as a parsimonious trend proxy and volatility as the leverage-risk
control because leveraged exposure is path-dependent and volatility-sensitive
`[stocks_on_the_move, p.66-67]`, `[leverage_for_the_long_run, p.7]`.

## Data And Window

- Physical daily parquets required before testing: `QQQ`, `QLD`, `SPY`, `SHV`.
- Source: `data/tiingo/daily/prices/*.parquet`.
- Use aligned daily adjusted close series where available; no intraday synthesis.
- Audit rows, first/last date, columns, timezone and missing-business-day rate.

## Exact Configs

All signals are shifted one completed daily bar before use. Daily strategy return is
`1.0 * QQQ_return + overlay * QLD_return - financing_drag`, where financing drag is
`max(gross - 1.0, 0) * 5% / 252` `[systematic_trading, p.137-148]`.

1. `mom63_vol63_cap25`: QQQ 63d momentum > 0 and QQQ 63d vol <= 25%, overlay 0.25.
2. `mom63_vol63_cap30`: QQQ 63d momentum > 0 and QQQ 63d vol <= 30%, overlay 0.25.
3. `mom126_vol63_cap25`: QQQ 126d momentum > 0 and QQQ 63d vol <= 25%, overlay 0.50.
4. `mom126_vol126_cap30`: QQQ 126d momentum > 0 and QQQ 126d vol <= 30%, overlay 0.50.

Total strategy trials: 4.

## Benchmarks

- Primary Phase 3 benchmark: `QQQ` buy-and-hold on identical aligned dates.
- Opportunity benchmark: `SPY` buy-and-hold on identical aligned dates.
- Same-asset context: `QLD` buy-and-hold and `SHV` buy-and-hold.

## Economic Kill Rule

If the best strategy CAGR <= `QQQ` buy-and-hold CAGR or terminal wealth <= `QQQ`
buy-and-hold terminal wealth on aligned dates, status must be `fail`. If CAGR <=
`SPY` buy-and-hold CAGR, status also cannot exceed `fail` unless `QQQ` is explicitly
treated as the higher-beta primary opportunity benchmark. No `candidate_watchlist`,
`paper_trade_candidate` or `strict_winner` is allowed without beating primary B&H in
both CAGR and terminal wealth `[systematic_trading, p.40]`, `[testing_tuning,
p.327-335]`.

## Validation Gates

- IS MCPT with 200 joint-return permutations, pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT with 100 post-training joint-return permutations, pass if `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO `< 0.5` over the 4 pre-registered configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6 positive windows and at least 8 total windows.
- OOS: final 20% compound return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 trading days compound return positive.
- Bootstrap: 99.9% mean daily return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/reference arithmetic: CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- Missing required daily parquet or close column => `data_blocked`, no proxy.
- Economic B&H miss => `fail` regardless of drawdown or Sharpe improvement.
- Any strict validation gate failure after economic pass => at most
  `economic_beater_not_validated`, research-only.
- Do not tune thresholds after results; a follow-up requires a new preregistered
  mechanism `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials` before: 296.
- `n_trials` planned: 4.
- `cumulative_n_trials` after: 300.
