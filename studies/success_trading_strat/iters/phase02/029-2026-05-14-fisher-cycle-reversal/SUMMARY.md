# SUMMARY — 029-2026-05-14-fisher-cycle-reversal

## Verdict

`fail`. The best Fisher cycle-reversal config (`spy_fisher10_reversal_sma200_h10`) did not beat `SPY` buy-and-hold on CAGR and failed strict PBO/DSR/FWD gates. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
- Rule: `Fisher(10)` exhaustion rebound with `SMA200`, exit at Fisher `0.5` or after 10 bars, otherwise hold `SHV` `[cycle_analytics, p.195-197]`, `[trading_systems_methods, p.284]`.
- Signals were shifted one completed daily bar before returns were earned `[advances_fin_ml, p.31-34]`.
- Physical audit confirmed required daily files exist. `data/tiingo/1hour/prices/` still has 0 parquet files and `data/tiingo/15min/prices/` is absent, so no intraday hybrid was synthesized.

## Benchmark Comparison

Best config: `spy_fisher10_reversal_sma200_h10`.

- Strategy: CAGR 4.70%, Sharpe 0.729, MDD -11.09%.
- `SPY` buy-and-hold: CAGR 10.90%, Sharpe 0.646, MDD -55.20%.
- Same-asset total return: strategy +343.50% vs `SPY` buy-and-hold +2762.43%.
- `SPY` opportunity context is the same as the primary benchmark for the best config.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset buy-and-hold. Lower drawdown and higher Sharpe do not compensate for lower compound return under this non-hedge hypothesis `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: PASS.
- IS MCPT: PASS (`p=0.000`, 200 reps).
- WF MCPT: PASS (`p=0.050`, 100 reps).
- PBO: FAIL (`0.587`).
- DSR: FAIL (`p=0.0882`, cumulative trials after iteration = 216).
- WF windows: PASS (`23/29` positive).
- OOS: PASS (`+16.54%`).
- Latest 63d FWD stress: FAIL (`-2.76%`).
- Bootstrap 99.9% mean-daily CI low: PASS (`0.0000545`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Fisher reversal behaved like another de-risking exposure filter: it improved drawdown and Sharpe but gave up too much compound return versus simply holding `SPY`.
- PBO and DSR remained hard blocks even after favorable MCPT diagnostics.
- Do not locally tune Fisher lookback, thresholds, hold length or SMA length after this fail `[testing_tuning, p.327-335]`.

## Recommended Next Step

Use the final Phase 2 iteration for a different mechanism or a conservative closure/audit of Phase 2. Do not expand daily oscillator variants unless true `1h`/`15m` files are restored and physically audited first.
