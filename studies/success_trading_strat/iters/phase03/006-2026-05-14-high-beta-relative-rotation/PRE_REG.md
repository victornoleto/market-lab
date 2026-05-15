# PRE_REG - Phase 3 Iteration 006

## Hypothesis

Test high-beta relative rotation over `QQQ`, `SMH`, `SOXX` and `XLK`. Phase 3 needs a return-selection engine rather than another long/flat defensive filter: stay invested in the strongest high-beta sleeve using trailing relative strength, optionally volatility-adjusted, so upside can exceed a passive opportunity basket `[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`, `[systematic_trading, p.40]`.

This is a different mechanism from the prior LETF vol-target and crash-rearm tests. It does not use leverage and does not allocate to `SHV`; drawdown reduction is not the thesis.

## Data And Window

Physical daily parquet files required before testing:

- traded universe: `QQQ`, `SMH`, `SOXX`, `XLK`;
- opportunity benchmark: `SPY`;
- cash context only: `SHV`.

The script will audit file existence, rows, first/last date, columns, timezone, missing-business-day rate and close-column availability. If any traded or benchmark file is missing, close `data_blocked` with `n_trials=0`.

Aligned window: intersection of the four traded ETF close series plus `SPY`, after the maximum lookback warmup.

## Configs

Six pre-registered configs, all signals lagged one completed daily bar to avoid lookahead `[advances_fin_ml, p.31-34]`:

1. `top1_m63`: hold the single asset with highest 63-day total return.
2. `top1_m126`: hold the single asset with highest 126-day total return.
3. `top2_m63`: equal-weight the top 2 assets by 63-day total return.
4. `top2_m126`: equal-weight the top 2 assets by 126-day total return.
5. `top1_m126_rv63`: hold the single asset with highest 126-day return divided by 63-day annualized realized volatility.
6. `top2_m126_rv63`: equal-weight the top 2 assets by 126-day return divided by 63-day annualized realized volatility.

Trial count: `n_trials=6`.

Selection criterion before validation: choose the config with highest full-window Sharpe, tie-broken by terminal wealth. DSR and PBO account for the six tested configs, so this best-of-six selection is not treated as a single-trial result `[advances_fin_ml, p.222-223]`.

## Benchmarks

Primary Phase 3 benchmark: equal-weight buy-and-hold of the traded opportunity universe `QQQ/SMH/SOXX/XLK` on the same aligned dates.

Opportunity benchmark: `SPY` buy-and-hold on the same aligned dates.

Additional context: `QQQ` buy-and-hold and each traded sleeve buy-and-hold.

## Economic Kill Rule

If best strategy CAGR <= primary equal-weight universe buy-and-hold CAGR, close `fail`.

If best strategy terminal wealth <= primary equal-weight universe buy-and-hold terminal wealth, close `fail`.

No label above `fail` is allowed unless both economic gates pass. Sharpe, MDD or lower drawdown cannot override this `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Planned Gates

- IS MCPT by jointly permuting daily return rows across the full universe and re-running the fixed pre-registered rule; pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT by preserving the first train window and jointly permuting later daily return rows; pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the six configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration `[advances_fin_ml, p.222-223]`.
- Walk-forward positive windows: at least 6 positive OOS windows and at least 8 total windows when available `[testing_tuning, p.148-150]`.
- Single-block OOS: final 20% total return positive `[advances_fin_ml, p.196-202]`.
- Latest 63 trading-day FWD stress positive `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% mean daily return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity: independently computed loop and vector return paths within 3pp CAGR `[advances_fin_ml, p.31-34]`.

## Kill Rules

- Missing required data => `data_blocked`, `n_trials=0`.
- Economic underperformance versus primary equal-weight B&H => `fail` regardless of validation.
- Any hard validation failure blocks `strict_winner`; if economic gates pass but validation fails, status may only be `economic_beater_not_validated`.
- Do not tune lookbacks, top-k or scoring after seeing results.

## Trial Accounting

- cumulative_n_trials before: `246`.
- planned n_trials: `6`.
- cumulative_n_trials after: `252`.

## Guardrails

Capital remains 100% Plano C. No deploy, no paper-trade claim, no commit/push, and `docs/investment-mandate.md` must not be modified.
