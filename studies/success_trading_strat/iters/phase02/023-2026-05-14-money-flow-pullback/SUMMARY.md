# SUMMARY — 023-2026-05-14-money-flow-pullback

## Verdict

`fail`. The best Money Flow Index pullback config (`gld_mfi14_os20_x50_sma200_h10`) failed the Phase 2 same-asset CAGR floor and failed IS MCPT, WF MCPT and DSR. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily configs on `SPY`, `QQQ` and `GLD`.
- Rule: enter long when MFI is oversold under a 200-day SMA trend filter; exit on MFI recovery or max hold `[trading_systems_methods, p.540]`, `[trading_systems_methods, p.285]`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `SPY`/`QQQ`/`GLD`/`xauusd`/`SHV` files exist and configured ETF volume is present. `1hour/prices` still has 0 parquet files and `15min/prices` is absent, so no intraday hybrid was synthesized.

## Benchmark Comparison

Best config: `gld_mfi14_os20_x50_sma200_h10`.

- Strategy: CAGR 1.90%, Sharpe 0.730, MDD -4.88%.
- `GLD` buy-and-hold: CAGR 11.64%, Sharpe 0.693, MDD -45.56%.
- `SPY` opportunity benchmark: CAGR 11.10%, Sharpe 0.645.
- Same-asset total return: strategy +47.34% vs `GLD` buy-and-hold +871.13%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset buy-and-hold. Lower drawdown alone is insufficient under the economic floor `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: PASS.
- IS MCPT: FAIL (`p=0.475`, 200 reps).
- WF MCPT: FAIL (`p=0.100`, 100 reps).
- PBO: PASS (`0.246`).
- DSR: FAIL (`p=0.2840`, cumulative trials after iteration = 192).
- WF windows: PASS (`14/17` positive).
- OOS: PASS (`+20.87%`).
- Latest 63d FWD stress: PASS (`+4.17%`).
- Bootstrap 99.9% mean-daily CI low: PASS (`+0.00000529`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- MFI strongly reduced drawdown but mostly acted as a low-participation GLD filter, not a return-compounding alternative to buy-and-hold.
- MCPT and DSR indicate the observed Sharpe was not compelling after null-path and cumulative-trial adjustment.
- Do not locally tune MFI period, oversold threshold, recovery exit or hold length after this fail `[testing_tuning, p.327-335]`.

## Recommended Next Step

Continue Phase 2 with a different daily mechanism, or restore and audit true `1h`/`15m` files before testing short-swing hybrids. Avoid local tuning of MFI parameters.
