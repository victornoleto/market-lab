# PRE_REG - Phase 3 Iteration 002 - S&P LETF Vol Target

## Hypothesis

This iteration tests the Phase 3 spec's second recommended mechanism: controlled S&P LETF exposure (`SSO`/`UPRO`) with one-bar-lagged volatility targeting and explicit crash/path-dependency de-risking. This is not a local retune of the prior Nasdaq LETF family because the return engine, primary benchmark and traded LETFs change from `QQQ`/`QLD`/`TQQQ` to `SPY`/`SSO`/`UPRO`. LETF regime logic follows Gayed's leverage rotation framing `[leverage_for_the_long_run, p.13]`; daily leverage/path dependency and volatility control follow the warning that high-volatility paths impair leveraged compounding `[leverage_for_the_long_run, p.5-7]`; risk targeting follows Carver's volatility sizing discipline `[systematic_trading, p.137-148]`. Validation uses MCPT/WF-MCPT plus PBO/DSR gates `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Data And Audit

The runner will physically audit daily parquet files for the tested Phase 3 set: `SPY`, `SSO`, `UPRO`, `SHV`, plus context `QQQ`. The tested universe requires daily adjusted close data for `SPY`, `SSO`, `UPRO` and `SHV`. If any required tested asset is physically missing or lacks a usable close, close as `data_blocked`. Do not substitute after results.

## Exact Configs

Six pre-registered configs:

| name | risk asset | vol lookback | annual target vol | crash drawdown trigger | crash multiplier |
|---|---|---:|---:|---:|---:|
| `sso_vt25_rv63` | `SSO` | 63 | 25% | none | 1.0 |
| `sso_vt35_rv63` | `SSO` | 63 | 35% | none | 1.0 |
| `sso_vt40_rv63_dd30_half` | `SSO` | 63 | 40% | -30% | 0.5 |
| `upro_vt40_rv63_dd30_half` | `UPRO` | 63 | 40% | -30% | 0.5 |
| `upro_vt55_rv63_dd35_half` | `UPRO` | 63 | 55% | -35% | 0.5 |
| `sso_vt30_rv21_dd25_half` | `SSO` | 21 | 30% | -25% | 0.5 |

Rules: compute realized volatility from the traded LETF's own daily returns, lag the risk weight by one completed bar, cap risk-asset weight at 1.0, allocate the remainder to `SHV`. Crash drawdown is trailing drawdown from the traded LETF's own high-water mark, also lagged by one completed bar. No borrowing or synthetic leverage beyond the LETF itself is modeled.

## Benchmarks

Primary buy-and-hold benchmark: `SPY` buy-and-hold on the exact aligned dates, per Phase 3 S&P LETF mapping.

Context benchmarks: same traded LETF buy-and-hold (`SSO` or `UPRO` for the best config) and `QQQ` buy-and-hold opportunity cost.

## Economic Kill Rule

If best strategy CAGR <= primary `SPY` buy-and-hold CAGR or terminal wealth <= primary `SPY` buy-and-hold terminal wealth, status must be `fail`. It cannot receive `economic_beater_not_validated`, `candidate_watchlist`, `paper_trade_candidate` or `strict_winner`.

## Planned Gates

- IS MCPT on the fixed best rule with 200 permutations; pass if `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations; pass if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO over the six configs with 10 blocks; pass if `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR using cumulative trial count after this iteration; pass if `p < 0.05` `[advances_fin_ml, p.222-223]`.
- Walk-forward positive windows: at least 6 positive windows and at least 8 total windows where feasible `[testing_tuning, p.148-150]`.
- Single-block OOS, latest 63d FWD stress, bootstrap 99.9% CI low > 0 and cross-lib/vector parity within +/-3pp CAGR.

## Trial Accounting

`cumulative_n_trials` before: 222.

`n_trials`: 6.

`cumulative_n_trials` after: 228.

## Conservative Ambiguity Handling

If validation gives a borderline threshold value, treat it as fail unless it is strictly on the pass side. If the strategy beats `SPY` but fails any hard validation gate, the maximum allowed status is `economic_beater_not_validated`, never `candidate_watchlist` or deploy-related status.
