# PRE_REG - Phase 3 Iteration 024

## Hypothesis

Test a `QLD/TLT/GLD` monthly sleeve with a small drawdown-triggered risk migration:
keep a levered Nasdaq growth engine, diversify with bonds/gold, and add controlled
`QLD` gross exposure only after the strategy is underwater. The return engine is
LETF participation plus Vince-style migration through leverage space, not another
long/flat defensive filter `[leverage_for_the_long_run, p.13]`,
`[leverage_space, p.149-167]`, `[systematic_trading, p.137-148]`.

## Data And Window

Physical daily parquet files required before testing: `QLD`, `TLT`, `GLD`, `QQQ`,
`SPY`, `SHV`. Use adjusted close when available. Aligned window starts at the
latest common first date and ends at the earliest common last date. No intraday
data, no synthetic series, no post-result substitution `[advances_fin_ml, p.31-34]`.

## Configs

Four pre-registered configs, one family:

- `qld60_tlt20_gld20_dd15_boost25`: base 60/20/20, add +25pp `QLD` gross while drawdown <= -15%.
- `qld70_tlt15_gld15_dd15_boost25`: base 70/15/15, add +25pp `QLD` gross while drawdown <= -15%.
- `qld60_tlt20_gld20_dd25_boost50`: base 60/20/20, add +50pp `QLD` gross while drawdown <= -25%.
- `qld70_tlt15_gld15_dd25_boost50`: base 70/15/15, add +50pp `QLD` gross while drawdown <= -25%.

Rebalance monthly using only previous-bar equity state. Financing drag on gross
exposure above 1.0 is 5% annualized. Trial count: 4 configs.

## Benchmarks

Primary buy-and-hold hierarchy:

- `QQQ` buy-and-hold because the growth engine is Nasdaq LETF exposure.
- Equal-weight `QLD/TLT/GLD` buy-and-hold as opportunity-universe benchmark.

Opportunity benchmark: `SPY` buy-and-hold. Context benchmarks: `QLD`, `TLT`,
`GLD`, and `SHV` buy-and-hold.

## Economic Kill Rule

If CAGR or terminal wealth is <= either primary benchmark on aligned dates,
iteration status must be `fail`. No `economic_beater_not_validated`,
`candidate_watchlist`, `paper_trade_candidate` or `strict_winner` label is allowed
without beating both primary benchmarks in CAGR and terminal wealth
`[systematic_trading, p.40]`.

## Planned Gates

- IS MCPT on joint return-row permutations, 200 reps, pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT after initial training, 100 reps, pass if `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the four configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` with cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- WF positive windows >= 6 and at least 8 total windows `[testing_tuning, p.148-150]`.
- OOS positive, latest 63d FWD positive, bootstrap 99.9% mean-return CI low > 0,
  and cross-lib/reference CAGR delta <= 3pp `[testing_tuning, p.246-247]`,
  `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.31-34]`.

## Kill Rules

- Required data missing or missing adjusted/close column => `data_blocked`.
- Economic kill fires => `fail` even if validation diagnostics look good.
- Any hard validation gate failure blocks `strict_winner`.
- If the family fails, do not tune nearby drawdown thresholds or boosts in this
  session `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials` before: 304.
- `n_trials`: 4.
- `cumulative_n_trials` after: 308.
