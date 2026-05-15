# SUMMARY - Phase 3 Iteration 007

## Verdict

`data_blocked`. No trials consumed, no winner, no deploy implication, mandate remains 100% Plano C.

## Tested

Pre-registered a crypto/equity relative-rotation mechanism over `BTCUSD`, `ETHUSD`, `QQQ` and `GLD`, with six always-invested top-1/top-2 momentum or volatility-adjusted momentum configs. The mechanism was intended to test cross-sectional high-beta return selection rather than another defensive long/flat filter `[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`.

No backtest was run because the required physical crypto daily files were absent.

## Benchmark Comparison

Not computed. The pre-registered primary benchmark was equal-weight buy-and-hold of `BTCUSD`/`ETHUSD`/`QQQ`/`GLD`, with `SPY` buy-and-hold as opportunity benchmark.

Audit result:

- Missing: `data/tiingo/daily/prices/BTCUSD.parquet`.
- Missing: `data/tiingo/daily/prices/ETHUSD.parquet`.
- Present through 2026-05-13: `QQQ`, `GLD`, `SPY`, `SHV`.

## Gates

Not computed because the data-block fired before any strategy trial. `n_trials=0`, so `cumulative_n_trials` remains `252`.

## Lessons

The crypto/equity branch in `PHASE3_BH_BEATER_SPEC.md` cannot be tested honestly from the current daily cache using the pre-registered tickers. Manifest-level expectations were insufficient; physical parquet existence is binding.

## Next Step

Pivot to drawdown-adaptive sizing on the already confirmed high-beta equity universe, or restore/audit physical `BTCUSD`/`ETHUSD` daily files before attempting crypto/equity rotation again. Do not substitute crypto proxies after this preregistration `[testing_tuning, p.327-335]`.
