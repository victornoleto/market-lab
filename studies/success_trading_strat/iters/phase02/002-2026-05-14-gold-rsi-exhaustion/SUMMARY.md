# SUMMARY — 002-2026-05-14-gold-rsi-exhaustion

## Verdict

`fail`. Daily `GLD` RSI exhaustion mean reversion reduced drawdown versus `GLD`
buy-and-hold, but did not beat the same-asset benchmark on Sharpe and failed core
validation gates. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily `GLD` configs using `RSI(2)`/`RSI(3)` downside exhaustion
  with `SMA150`/`SMA200` trend filters and `SHV` while flat.
- Signals were shifted one bar before execution.
- Intraday audit confirmed `data/tiingo/1hour/prices/` exists but has 0 parquet
  files; `GLD`/`xauusd` 1h are physically absent, so no intraday test was run.

## Benchmark Comparison

Best config: `gld_rsi2_e5_x60_sma200`.

- Strategy: CAGR 6.35%, Sharpe 0.636, MDD -25.34%.
- `GLD` buy-and-hold: CAGR 11.65%, Sharpe 0.693, MDD -45.56%.
- `SPY` context over aligned window: CAGR 11.11%, Sharpe 0.645.

The rule lowered drawdown but gave up too much upside and slightly lost to `GLD`
on Sharpe.

## Gates

- Economic Sharpe vs `GLD`: FAIL.
- IS MCPT: FAIL (`p=0.200`, 200 reps).
- WF MCPT: FAIL (`p=0.140`, 100 reps).
- PBO: FAIL (`0.556`).
- DSR: FAIL (`p=0.3708`, cumulative trials after iteration = 108).
- WF windows: PASS (`11/17` positive).
- OOS: PASS (`+63.68%`).
- Latest 63d FWD stress: FAIL (`-3.81%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0000111`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

MCPT used log-price paths shifted positive and converted back inside the fixed rule
because Masters-style arithmetic change permutations can otherwise create nonpositive
`GLD` paths. This preserves the pre-registered rule and was the conservative way to
avoid invalid permuted prices `[testing_tuning, p.318-320]`.

## Lessons

- Gold short-horizon RSI mean reversion is a drawdown reducer, not an edge versus
  same-asset buy-and-hold on this daily sample.
- The family fails both the video MCPT gates and repo hard gates, so more local RSI
  tuning would be curve-fit risk without a materially new mechanism.
- Phase 2 short-swing gold remains blocked until physical 1h/15m data are restored
  and audited.

## Recommended Next Step

Pivot away from daily gold RSI/Donchian local variants. Either restore/audit true
1h gold data for Track B/C, or test a different daily swing mechanism with a distinct
economic rationale `[testing_tuning, p.327-335]`.
