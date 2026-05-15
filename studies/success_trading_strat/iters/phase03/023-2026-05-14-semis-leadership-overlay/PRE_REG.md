# PRE_REG - Phase 3 Iteration 023

## Hypothesis

Test a Nasdaq core-plus-semiconductor leadership overlay. The strategy keeps a
permanent `QQQ` core and adds partial gross exposure to `SOXL` or `TECL` only when
lagged semiconductor/technology leadership versus `QQQ` is positive and realized
volatility is below a fixed cap. The return engine is controlled high-beta LETF
exposure, not a defensive long/flat filter `[leverage_for_the_long_run, p.13]`,
`[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`,
`[systematic_trading, p.137-148]`.

This is a new mechanism relative to iteration 022 because the overlay asset and
trigger are sector-leadership based (`SMH/SOXX` relative strength), not local
`QQQ` momentum/vol tuning. Validation keeps MCPT, PBO and DSR as hard anti-overfit
controls `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

## Data And Window

Use physical Tiingo daily parquet files only:

- Required traded/signal assets: `QQQ`, `SMH`, `SOXX`, `SOXL`, `TECL`, `SPY`, `SHV`.
- Aligned window: intersection of available adjusted closes after loading.
- If any required physical parquet or close column is missing, close `data_blocked`.
- No intraday data, no synthetic crypto, no manifest-only assumption.

## Exact Configs

Four configs, all one-bar lagged:

| name | leadership pair | LETF overlay | relative momentum lookback | vol lookback | vol cap | overlay weight |
|---|---|---|---:|---:|---:|---:|
| `smh_qqq_m63_v63_soxl25` | `SMH/QQQ` | `SOXL` | 63 | 63 | 0.40 | 0.25 |
| `smh_qqq_m126_v63_soxl25` | `SMH/QQQ` | `SOXL` | 126 | 63 | 0.40 | 0.25 |
| `soxx_qqq_m63_v63_tecl25` | `SOXX/QQQ` | `TECL` | 63 | 63 | 0.35 | 0.25 |
| `soxx_qqq_m126_v63_tecl25` | `SOXX/QQQ` | `TECL` | 126 | 63 | 0.35 | 0.25 |

Financing drag: 5% annualized on gross exposure above 1.0, charged daily
`[systematic_trading, p.137-148]`.

## Benchmarks

Primary buy-and-hold benchmarks on the same aligned dates:

- `QQQ` buy-and-hold.
- Equal-weight `SMH/SOXX` buy-and-hold opportunity universe.

Opportunity-cost benchmark:

- `SPY` buy-and-hold.

Context benchmarks:

- `SOXL`, `TECL` and `SHV` buy-and-hold.

## Kill Rules

- CAGR <= primary `QQQ` B&H CAGR => `fail`.
- Terminal wealth <= primary `QQQ` B&H terminal wealth => `fail`.
- CAGR <= equal-weight `SMH/SOXX` B&H CAGR => `fail`.
- Terminal wealth <= equal-weight `SMH/SOXX` B&H terminal wealth => `fail`.
- CAGR <= `SPY` opportunity B&H CAGR => `fail`.
- MDD worse than 1.5x `QQQ` B&H MDD blocks `strict_winner`.
- Any failed strict validation gate blocks `strict_winner`.
- If economically beating but failing validation, status may be only
  `economic_beater_not_validated`, never `candidate_watchlist`,
  `paper_trade_candidate` or deploy.

## Planned Gates

- IS MCPT with 200 joint-return permutations, pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations, pass `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO `< 0.5` using 10 blocks `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward positives: at least 6 positive windows and at least 8 windows total.
- OOS: final 20% compounded return positive.
- FWD stress: latest 63 trading days positive.
- Bootstrap 99.9% mean daily return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/reference arithmetic CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Trial Accounting

- `cumulative_n_trials` before: 300.
- Strategy configs tested: 4.
- `cumulative_n_trials` after: 304.

## Guardrails

Capital remains 100% Plano C. This iteration is research-only and does not modify
`docs/investment-mandate.md`.
