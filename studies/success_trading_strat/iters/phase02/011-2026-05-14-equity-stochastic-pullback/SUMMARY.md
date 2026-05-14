# SUMMARY — 011-2026-05-14-equity-stochastic-pullback

## Verdict

`fail`. The best stochastic close-location pullback config improved Sharpe and
drawdown versus QQQ buy-and-hold, and passed IS/WF MCPT, but failed the Phase 2
economic CAGR floor, PBO, DSR and latest FWD stress. No deploy implication;
capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily `SPY`/`QQQ` stochastic-style close-location pullback
  configs.
- Rule: enter after an oversold close-location reading while price is above
  `SMA200`; exit on mid-range recovery, trend break or 10-bar max hold.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `SPY`, `QQQ` and `SHV` files exist. `1hour/prices`
  exists but has 0 parquet files; `15min/prices` is absent. No intraday bars were
  synthesized.

## Benchmark Comparison

Best config: `qqq_stoch14_os20_exit50_hold10`.

- Strategy: CAGR 6.64%, Sharpe 0.699, MDD -24.60%.
- `QQQ` buy-and-hold: CAGR 8.89%, Sharpe 0.454, MDD -82.97%.
- Same-asset total return: strategy +440.54% vs `QQQ` buy-and-hold +834.50%.

The rule materially reduced drawdown and improved Sharpe, but the pre-registered
kill rule fired because CAGR did not beat same-asset buy-and-hold.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: PASS.
- IS MCPT: PASS (`p=0.005`, 200 reps; strict gate `<=0.01`).
- WF MCPT: PASS (`p=0.010`, 100 reps).
- PBO: FAIL (`0.512`).
- DSR: FAIL (`p=0.1815`, cumulative trials after iteration = 144).
- WF windows: PASS (`19/23` positive).
- OOS: PASS (`+45.31%`).
- Latest 63d FWD stress: FAIL (`-1.00%`).
- Bootstrap 99.9% mean-daily CI low: PASS (`+0.0000132`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Stochastic pullbacks can de-risk QQQ's long-history drawdown profile, but they
  sacrifice too much compounded return for Phase 2's non-hedge mandate.
- The borderline PBO and failed DSR keep the result non-promotional even ignoring
  the CAGR kill switch `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune stochastic thresholds or close-location lookbacks locally. Continue
Phase 2 with a different daily swing mechanism, or restore true 1h/15m data before
testing short-swing hybrids.
