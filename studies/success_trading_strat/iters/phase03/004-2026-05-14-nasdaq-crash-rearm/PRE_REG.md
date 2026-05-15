# PRE_REG - Phase 3 Iteration 004

## Hypothesis

Nasdaq crash-rearmed exposure can beat `QQQ` buy-and-hold by remaining fully invested in `QQQ` during normal regimes and temporarily switching to `QLD` after a material `QQQ` drawdown has begun to recover. The return engine is explicit upside re-risking after stress, not cash defense: leverage is useful when post-crash volatility normalizes and streaks resume, while unmanaged constant leverage remains path-dependent and ruin-prone `[leverage_for_the_long_run, p.5-7]`, `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.16-17]`. Fixed re-risk windows and one-bar signal lag preserve idea-first discipline and avoid validation-driven retuning `[testing_tuning, p.327-335]`.

## Data And Window

- Physical daily files audited before testing: `QQQ`, `QLD`, `SPY`, `SHV`.
- Data source: local `data/tiingo/daily/prices/*.parquet`.
- Price column: `adj_close` when present, otherwise `close`.
- Expected aligned window: maximum common daily overlap after warmup and one-bar lag.

## Exact Configs

Six configs are tested; each consumes one strategy trial for DSR accounting `[advances_fin_ml, p.222-223]`.
The pre-registered selection metric is full-window annualized Sharpe, with terminal wealth as a tie-breaker, because the validation stack uses Sharpe-sensitive MCPT/DSR while Phase 3 economic gates separately require CAGR and terminal wealth to beat `QQQ` buy-and-hold `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.

| name | core | booster | drawdown trigger | recovery SMA | booster hold |
|---|---|---|---:|---:|---:|
| `qqq_qld_rearm_dd15_sma50_h63` | `QQQ` | `QLD` | `-15%` | `50` | `63` |
| `qqq_qld_rearm_dd20_sma50_h63` | `QQQ` | `QLD` | `-20%` | `50` | `63` |
| `qqq_qld_rearm_dd25_sma50_h126` | `QQQ` | `QLD` | `-25%` | `50` | `126` |
| `qqq_qld_rearm_dd20_sma100_h126` | `QQQ` | `QLD` | `-20%` | `100` | `126` |
| `qqq_qld_rearm_dd30_sma100_h126` | `QQQ` | `QLD` | `-30%` | `100` | `126` |
| `qqq_qld_rearm_dd35_sma100_h189` | `QQQ` | `QLD` | `-35%` | `100` | `189` |

Signal rule: when `QQQ` drawdown from its prior high is at or below the trigger and `QQQ` closes above its recovery SMA, arm the booster. Hold `QLD` for the fixed hold length unless a new rearm refreshes the countdown. Otherwise hold `QQQ`. All positions are shifted by one trading day to avoid lookahead `[advances_fin_ml, p.31-34]`.

## Benchmarks

- Primary Phase 3 benchmark: `QQQ` buy-and-hold on identical aligned dates.
- Opportunity benchmark: `SPY` buy-and-hold on identical aligned dates.
- Context benchmark: `QLD` buy-and-hold on identical aligned dates.

## Economic Kill Rule

- If best strategy CAGR <= primary `QQQ` buy-and-hold CAGR, verdict must be `fail`.
- If best strategy terminal wealth <= primary `QQQ` buy-and-hold terminal wealth, verdict must be `fail`.
- No `economic_beater_not_validated`, `candidate_watchlist`, `paper_trade_candidate` or `strict_winner` label is allowed unless both economic gates pass `[systematic_trading, p.40]`.

## Planned Gates

- IS MCPT with 200 permutations; pass threshold `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations; pass threshold `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` over the six configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trial count after this iteration `[advances_fin_ml, p.222-223]`.
- Walk-forward positive windows: at least 6 positive windows and at least 8 total windows when data permits `[testing_tuning, p.148-150]`.
- OOS positive on the last 20% of observations `[advances_fin_ml, p.196-202]`.
- Latest 63-trading-day FWD stress positive `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% mean daily return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity within +/-3pp CAGR `[advances_fin_ml, p.31-34]`.

## Trial Accounting

- `cumulative_n_trials` before: `234`.
- New trials: `6`.
- `cumulative_n_trials` after: `240`.

## Conservative Ambiguity Handling

MCPT permutes the `QQQ` signal path and uses a synthetic 2x `QQQ` booster proxy for the fixed-rule null because permuting `QQQ` and `QLD` jointly while preserving actual LETF path dependency is not implemented in the scaffold. This caveat cannot improve the verdict: if all gates appear to pass, promotion remains blocked pending stricter joint-path MCPT.
