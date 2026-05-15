# PRE_REG - Phase 3 Iteration 013

## Hypothesis

Test a Nasdaq crash-rearmed booster mechanism: stay invested in Nasdaq exposure,
but increase embedded leverage after a completed drawdown/recovery setup and reduce
the most aggressive sleeve when realized volatility is extreme. The return engine is
controlled LETF exposure and post-crash re-risking, not a defensive long/flat filter
`[leverage_for_the_long_run, p.5-7]`, `[leverage_for_the_long_run, p.13]`,
`[leverage_for_the_long_run, p.16-17]`, `[systematic_trading, p.119]`,
`[systematic_trading, p.137-148]`.

The mechanism is intentionally different from prior Phase 3 HFEA/balanced sleeves
and from the earlier fixed-hold crash-rearm variants. It uses dynamic booster state
based on distance from prior high and recovery confirmation, plus a pre-registered
volatility cap because daily leverage is path-dependent and high-volatility
seesawing can destroy compounded returns `[leverage_for_the_long_run, p.4-7]`.

## Data And Window

Required physical daily Tiingo parquet files before any test:

- `QQQ`, `QLD`, `TQQQ`, `SHV`, `SPY`.

Use adjusted close when available. Align all assets to the common daily index after
loading physical files. No manifest-only data and no intraday synthesis.

## Exact Configs

Four configs, all pre-registered before running:

1. `qqq_qld_tqqq_dd25_recover_sma50_rv40`: base `QQQ`; if `QQQ` drawdown from 252d high is <= -25% and close > SMA50, hold 50% `QLD` + 50% `TQQQ`; if 21d realized vol > 40%, cap to 75% `QLD` + 25% `TQQQ`.
2. `qld_tqqq_dd25_recover_sma50_rv40`: base `QLD`; if trigger/recovery is active, hold 50% `QLD` + 50% `TQQQ`; if 21d realized vol > 40%, cap to 100% `QLD`.
3. `qqq_qld_tqqq_dd35_recover_sma100_rv45`: base `QQQ`; trigger -35%, recovery close > SMA100, booster 60% `QLD` + 40% `TQQQ`; cap to 100% `QLD` above 45% realized vol.
4. `qld_tqqq_dd35_recover_sma100_rv45`: base `QLD`; trigger -35%, recovery close > SMA100, booster 60% `QLD` + 40% `TQQQ`; cap to 100% `QLD` above 45% realized vol.

Signals use completed daily bars only; portfolio returns apply yesterday's chosen
weights to today's returns to avoid lookahead `[advances_fin_ml, p.31-34]`.

## Benchmarks

Primary benchmark per Phase 3 mapping: `QQQ` buy-and-hold on aligned dates.

Secondary primary/opportunity benchmark: equal-weight `QQQ/QLD/TQQQ` buy-and-hold on
aligned dates, because the strategy explicitly chooses among Nasdaq embedded-leverage
instruments.

Opportunity-cost benchmark: `SPY` buy-and-hold on aligned dates.

Context benchmarks: `QLD`, `TQQQ`, `SHV` buy-and-hold.

## Economic Kill Rule

If best strategy CAGR <= primary `QQQ` buy-and-hold CAGR or terminal wealth <=
primary `QQQ` buy-and-hold terminal wealth, status must be `fail`.

If best strategy CAGR <= equal-weight `QQQ/QLD/TQQQ` buy-and-hold CAGR or terminal
wealth <= equal-weight terminal wealth, status must be `fail` by conservative Phase
3 interpretation.

No `economic_beater_not_validated`, `candidate_watchlist`, `paper_trade_candidate`
or `strict_winner` label is allowed unless both CAGR and terminal wealth beat both
primary benchmarks on identical dates.

## Planned Gates

- IS MCPT with 200 joint row permutations; pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT with 100 post-initial-train permutations; pass if `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the four configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6 positive windows and at least 8 total windows
  `[testing_tuning, p.148-150]`.
- OOS last 20% positive `[advances_fin_ml, p.196-202]`.
- Latest 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% mean daily CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/reference parity within +/-3pp CAGR `[advances_fin_ml, p.31-34]`.

## Kill Rules

- Missing required physical daily parquet or missing close column => `data_blocked`.
- Economic benchmark failure => `fail` regardless of lower MDD or higher Sharpe.
- Any strict validation failure blocks `strict_winner`.
- MDD worse than 1.5x the worse primary benchmark MDD blocks `strict_winner` unless
  a future human review explicitly overrides; no such override exists.
- No local tuning of trigger depths, SMA windows, volatility thresholds or booster
  weights after seeing results `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials` before: 272.
- `n_trials` planned: 4.
- `cumulative_n_trials` after if tested: 276.
