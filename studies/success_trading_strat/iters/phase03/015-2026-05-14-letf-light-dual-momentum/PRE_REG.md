# PRE_REG - Phase 3 Iteration 015

## Hypothesis

Test a LETF-light dual-momentum rotation across `QLD`, `SSO`, `TLT` and `GLD`,
using `SHV` only when no candidate has positive absolute momentum. The intended
return engine is owning the strongest available leveraged/bond/gold sleeve rather
than stepping mostly to cash, consistent with Phase 3 high-beta rotation guidance
`[stocks_on_the_move, p.66-67]`, relative-strength rotation
`[trading_systems_methods, p.542-544]`, and controlled leverage/path-dependency
risk awareness `[leverage_for_the_long_run, p.13]`.

This is not a deployment claim. Capital remains 100% Plano C.

## Data And Window

Use physical daily Tiingo parquet files only:

- traded assets: `QLD`, `SSO`, `TLT`, `GLD`, `SHV`;
- opportunity benchmark: `SPY` buy-and-hold;
- primary opportunity universe: equal-weight `QLD/SSO/TLT/GLD` buy-and-hold.

The script must audit rows, first/last date, columns, timezone, missing-business-day
rate and close availability before testing. If any required physical file is absent
or lacks close data, close `data_blocked` with zero trials.

## Exact Configs

Four pre-registered configs, all lagged by one bar through next-period weights:

- `top1_m126_monthly`: monthly top-1 by 126-day total return, only assets with
  positive 126-day return eligible; otherwise `SHV`.
- `top2_m126_monthly`: monthly top-2 equal-weight by 126-day total return, only
  positive candidates eligible; otherwise `SHV`.
- `top1_m252_monthly`: monthly top-1 by 252-day total return, positive candidates
  only; otherwise `SHV`.
- `top2_m252_quarterly`: quarterly top-2 equal-weight by 252-day total return,
  positive candidates only; otherwise `SHV`.

Momentum lookbacks and top-k selection are the indicator/parameter choices and are
cited to dual/relative momentum literature `[stocks_on_the_move, p.66-67]`,
`[trading_systems_methods, p.542-544]`. Monthly/quarterly rebalance is used to
avoid daily noise overfitting `[testing_tuning, p.327-335]`.

## Benchmarks

Primary benchmark hierarchy:

1. Equal-weight `QLD/SSO/TLT/GLD` buy-and-hold on aligned dates.
2. `SPY` buy-and-hold opportunity cost on aligned dates.

Context benchmarks: each component buy-and-hold plus `SHV`.

## Economic Kill Rule

If the selected best strategy has CAGR or terminal wealth less than or equal to the
primary equal-weight `QLD/SSO/TLT/GLD` benchmark, status must be `fail`. If it also
does not beat `SPY` buy-and-hold in CAGR and terminal wealth, status must be `fail`.
No `economic_beater_not_validated`, `candidate_watchlist`, `paper_trade_candidate`
or `strict_winner` label is allowed without both CAGR and terminal wealth beating
the primary aligned B&H benchmark `[systematic_trading, p.40]`.

## Planned Gates

- IS MCPT with 200 joint-return permutations, pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT with 100 joint-return permutations after the initial train window, pass
  `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the four configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward at least 6 positive windows and at least 8 total where possible
  `[testing_tuning, p.148-150]`.
- OOS, latest 63-day FWD stress, bootstrap 99.9% mean daily CI low > 0, and
  cross-lib/reference CAGR parity within +/-3pp `[advances_fin_ml, p.196-202]`,
  `[testing_tuning, p.246-247]`, `[advances_fin_ml, p.31-34]`.

## Trial Accounting

- `cumulative_n_trials` before: 280.
- New configs: 4.
- `cumulative_n_trials` after: 284.

## Kill Rules

- Missing required physical daily files or close data => `data_blocked`, zero trials.
- CAGR or terminal wealth <= equal-weight `QLD/SSO/TLT/GLD` B&H => `fail`.
- CAGR or terminal wealth <= `SPY` B&H => `fail` for Phase 3 opportunity-cost
  comparison.
- Any failed strict validation gate blocks `strict_winner`; if economics pass but
  validation fails, status can only be `economic_beater_not_validated`.
- Do not tune lookbacks/top-k/rebalance after seeing results in this iteration.
