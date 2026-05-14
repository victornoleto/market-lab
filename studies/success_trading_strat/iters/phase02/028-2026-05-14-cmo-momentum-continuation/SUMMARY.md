# SUMMARY — 028-2026-05-14-cmo-momentum-continuation

## Verdict

`fail`. The best CMO continuation config (`xau_cmo20_e50_x0_sma200_h20`) did not beat `xauusd` buy-and-hold on CAGR or Sharpe and failed the strict robustness gates. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
- Rule: enter when `CMO(20) >= 50` and price is above `SMA200`; exit at `CMO <= 0` or after 20 bars; otherwise hold `SHV` `[trading_systems_methods, p.388]`, `[trading_systems_methods, p.284]`.
- Signals were shifted one completed daily bar before returns were earned `[advances_fin_ml, p.31-34]`.
- Physical audit confirmed required daily close files exist. `data/tiingo/1hour/prices/` still has 0 parquet files and `data/tiingo/15min/prices/` is absent, so no intraday hybrid was synthesized.

## Benchmark Comparison

Best config: `xau_cmo20_e50_x0_sma200_h20`.

- Strategy: CAGR 5.91%, Sharpe 0.638, MDD -14.68%.
- `xauusd` buy-and-hold: CAGR 17.28%, Sharpe 1.060, MDD -20.36%.
- Same-asset total return: strategy +40.81% vs `xauusd` buy-and-hold +158.55%.
- `SPY` opportunity context on the same window: CAGR 10.65%, Sharpe 0.730.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset buy-and-hold. Lower drawdown does not compensate for lower compound return under this non-hedge hypothesis `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.470`, 200 reps).
- WF MCPT: FAIL (`p=0.790`, 100 reps).
- PBO: FAIL (`0.885`).
- DSR: FAIL (`p=0.8738`, cumulative trials after iteration = 212).
- WF windows: FAIL (`2/2` positive, fewer than 8 windows).
- OOS: PASS (`+27.29%`).
- Latest 63d FWD stress: PASS (`+0.69%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0002321`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- CMO continuation behaved like another exposure filter: it reduced drawdown but gave up too much compound return versus simply holding the asset.
- The `xauusd` daily cache starts only in 2020 and post-warmup leaves two annual WF windows, so gold spot daily-only tests remain weak for WF sufficiency unless using a longer proxy.
- Do not locally tune CMO length, thresholds, hold length or SMA length after this fail `[testing_tuning, p.327-335]`.

## Recommended Next Step

Continue Phase 2 with a different mechanism that can plausibly increase compound return, or restore and audit true `1h`/`15m` files before testing short-swing hybrids.
