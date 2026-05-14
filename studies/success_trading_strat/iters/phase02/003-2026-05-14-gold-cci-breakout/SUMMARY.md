# SUMMARY — 003-2026-05-14-gold-cci-breakout

## Verdict

`fail`. Daily close-only CCI breakout on gold reduced drawdown versus same-asset
buy-and-hold, but did not beat `xauusd` buy-and-hold on Sharpe and failed multiple
strict validation gates. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily close-only CCI breakout configs on `GLD` and `xauusd`.
- Entry: `CCI > 100` with close above `SMA200`; exit: `CCI < 0` or close below
  `SMA200`.
- Signals were shifted one bar before execution.
- Physical audit confirmed daily `GLD`, `xauusd`, `SHV` and `SPY` files exist.
- Intraday audit confirmed `1hour/prices` exists but has 0 parquet files; `15min/prices`
  is absent. No intraday bars were synthesized.

## Benchmark Comparison

Best config: `xau_cci40_e100_x0_sma200`.

- Strategy: CAGR 9.92%, Sharpe 0.820, MDD -14.68%.
- `xauusd` buy-and-hold: CAGR 17.36%, Sharpe 1.070, MDD -20.36%.
- `SPY` context over aligned window: CAGR 11.21%, Sharpe 0.765.

The strategy improved drawdown but gave up too much upside and failed same-asset
Sharpe.

## Gates

- Economic Sharpe vs `xauusd`: FAIL.
- IS MCPT: FAIL (`p=0.280`, 200 reps).
- WF MCPT: FAIL (`p=0.450`, 100 reps).
- PBO: PASS (`0.214`).
- DSR: FAIL (`p=0.7023`, cumulative trials after iteration = 112).
- WF windows: FAIL (`3/3` positive, fewer than 8 windows).
- OOS: PASS (`+33.23%`).
- Latest 63d FWD stress: FAIL (`-6.27%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0002044`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- CCI breakout is another gold drawdown reducer, not an edge versus same-asset
  buy-and-hold on the available daily sample.
- The `xauusd` file has a short 2020+ range and high missing-business-day rate, so
  WF sufficiency remains structurally weak for XAU-specific daily configs.
- More local CCI threshold/lookback tuning would be curve-fit risk without a new
  mechanism `[testing_tuning, p.327-335]`.

## Recommended Next Step

Pivot away from daily gold oscillator/breakout variants. Either restore/audit true
1h/15m gold data for Track B/C, or test a distinct daily swing mechanism outside
gold-only CCI/RSI/Donchian families.
