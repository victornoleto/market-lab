# PRE_REG - Phase 3 Iteration 001 - Nasdaq LETF Vol Target

## Hypothesis

Phase 3 starts with the spec's first recommended mechanism: Nasdaq LETF exposure with explicit volatility targeting and crash/path-dependency control. The return engine is controlled leverage (`QLD`/`TQQQ`) rather than another long/flat defensive filter, because Phase 2 showed that cash timing usually gives up too much compounded return. LETF exposure and path dependency follow Gayed's leverage-for-the-long-run framing `[leverage_for_the_long_run, p.13]`; volatility targeting and conservative sizing follow Carver's risk-targeting discipline `[systematic_trading, p.137-148]`; validation uses MCPT/WF-MCPT plus PBO/DSR gates `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Data And Audit

Before testing, the runner will physically audit daily parquet files for the Phase 3 required set where available: `SPY`, `QQQ`, `QLD`, `TQQQ`, `SSO`, `UPRO`, `SMH`, `SOXX`, `SOXL`, `TECL`, `XLK`, `IBIT`, `ETHA`, `BTCUSD`/`btcusd`, `ETHUSD`/`ethusd`, `GLD`, `TLT`, `IEF`, `SHV`.

The tested universe requires daily adjusted close data for `QQQ`, `QLD`, `TQQQ`, `SPY` and `SHV`. If any required tested asset is physically missing or lacks a usable close, close as `data_blocked`. Do not substitute after results.

## Exact Configs

Six pre-registered configs:

| name | risk asset | vol lookback | annual target vol | crash drawdown trigger | crash multiplier |
|---|---|---:|---:|---:|---:|
| `qld_vt30_rv63` | `QLD` | 63 | 30% | none | 1.0 |
| `qld_vt40_rv63` | `QLD` | 63 | 40% | none | 1.0 |
| `qld_vt45_rv63_dd30_half` | `QLD` | 63 | 45% | -30% | 0.5 |
| `tqqq_vt45_rv63_dd30_half` | `TQQQ` | 63 | 45% | -30% | 0.5 |
| `tqqq_vt60_rv63_dd35_half` | `TQQQ` | 63 | 60% | -35% | 0.5 |
| `qld_vt35_rv21_dd25_half` | `QLD` | 21 | 35% | -25% | 0.5 |

Rules: compute realized volatility from the traded LETF's own daily returns, lag the risk weight by one completed bar, cap risk-asset weight at 1.0, allocate the remainder to `SHV`. Crash drawdown is trailing drawdown from the traded LETF's own high-water mark, also lagged by one completed bar. No borrowing or synthetic leverage beyond the LETF itself is modeled.

## Benchmarks

Primary buy-and-hold benchmark: `QQQ` buy-and-hold on the exact aligned dates, per Phase 3 Nasdaq LETF mapping.

Context benchmarks: same traded LETF buy-and-hold (`QLD` or `TQQQ` for the best config) and `SPY` buy-and-hold opportunity cost.

## Economic Kill Rule

If best strategy CAGR <= primary `QQQ` buy-and-hold CAGR or terminal wealth <= primary `QQQ` buy-and-hold terminal wealth, status must be `fail`. It cannot receive `economic_beater_not_validated`, `candidate_watchlist`, `paper_trade_candidate` or `strict_winner`.

## Planned Gates

- IS MCPT on the fixed best rule with 200 permutations; pass if `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations; pass if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO over the six configs with 10 blocks; pass if `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR using cumulative trial count after this iteration; pass if `p < 0.05` `[advances_fin_ml, p.222-223]`.
- Walk-forward positive windows: at least 6 positive windows and at least 8 total windows where feasible `[testing_tuning, p.148-150]`.
- Single-block OOS, latest 63d FWD stress, bootstrap 99.9% CI low > 0 and cross-lib/vector parity within +/-3pp CAGR.

## Trial Accounting

`cumulative_n_trials` before: 216.

`n_trials`: 6.

`cumulative_n_trials` after: 222.

## Conservative Ambiguity Handling

If ticker case is ambiguous for crypto audit (`BTCUSD` versus `btcusd`), audit both and record the physical file that exists. Crypto is not traded in this iteration, so crypto audit ambiguity cannot promote or block this LETF test.
