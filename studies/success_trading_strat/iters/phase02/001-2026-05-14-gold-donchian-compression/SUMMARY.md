# SUMMARY — 001-2026-05-14-gold-donchian-compression

## Verdict

`fail`. Daily gold/XAUUSD Donchian-compression breakout did not beat the primary
same-asset benchmark and failed core validation gates. No deploy implication;
capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily configs over `GLD` and `xauusd`.
- Entry: close-only Donchian breakout after low 20d realized-volatility percentile.
- Exit: 20d Donchian low; flat sleeve in `SHV`.
- Intraday audit: `data/tiingo/1hour/prices/` exists but has 0 parquet files;
  `GLD`/`xauusd` 1h are physically absent, so no 1h test was run.

## Benchmark Comparison

Best config: `xau_dc100_rv20_p30`.

- Strategy: CAGR 7.11%, Sharpe 0.726, MDD -14.68%.
- Same-asset XAU buy-and-hold: CAGR 18.17%, Sharpe 1.099, MDD -20.36%.
- SPY context over aligned window: CAGR 10.69%, Sharpe 0.725.

The strategy reduced drawdown versus XAU buy-and-hold but lost decisively on CAGR
and Sharpe.

## Gates

- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.315`, 200 reps).
- WF MCPT: FAIL (`p=0.220`, 100 reps).
- PBO: FAIL (`0.615`).
- DSR: FAIL (`p=0.7716`, cumulative trials after iteration = 104).
- WF windows: FAIL by sufficiency; only 2 windows available for the XAU best config.
- OOS: PASS (`+26.98%`).
- Latest 63d FWD stress: FAIL (`-9.73%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.000232`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Gold breakout-after-compression reduced drawdown but mostly underexposed a strong
  XAU trend; the opportunity cost versus buy-and-hold was too high.
- XAU daily cache is shorter and has a higher missing-business-day rate than GLD,
  so future strict tests should prefer GLD for long-history diagnostics unless a
  new XAU-specific microstructure hypothesis requires spot data.
- Phase 2 intraday gold work is currently blocked by absent physical 1h cache files;
  manifest entries are not enough.

## Recommended Next Step

Pivot to a different Track C daily mechanism on `GLD` with longer history, or first
restore/audit physical 1h gold/XAUUSD data before any short-swing hybrid test
`[testing_tuning, p.327-335]`.
