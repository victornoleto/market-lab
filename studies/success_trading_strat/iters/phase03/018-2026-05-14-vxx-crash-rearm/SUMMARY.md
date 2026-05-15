# SUMMARY - Phase 3 Iteration 018

## Verdict

`economic_beater_not_validated`. No strict winner, no candidate/watchlist label, no
paper-trade label, no deploy implication. Capital remains 100% Plano C.

## Tested

Pre-registered `VXX`-triggered Nasdaq crash rearm: hold `QQQ` as core exposure,
detect stress from lagged `VXX`, then temporarily switch to `QLD` or `TQQQ` after
volatility partially normalizes. Four configs were tested; `VXX` was signal-only.

Best config: `qqq_tqqq_vxx95_norm70_h126`.

## Benchmark Comparison

Aligned window: 2010-02-12 to 2026-05-13.

- Strategy CAGR: 28.85%; terminal wealth: 61.04x.
- Primary `QQQ` B&H CAGR: 19.84%; terminal wealth: 18.83x.
- `SPY` opportunity B&H CAGR: 14.65%; terminal wealth: 9.18x.
- Context `TQQQ` B&H CAGR: 44.12%; terminal wealth: 375.14x.

The strategy passed the Phase 3 economic floor versus `QQQ` and `SPY`, but did not
beat raw `TQQQ` buy-and-hold context.

## Gates

- Physical daily files: pass for `QQQ`, `QLD`, `TQQQ`, `VXX`, `SPY`, `SHV`.
- Economic CAGR/terminal wealth vs `QQQ`: pass.
- IS MCPT: fail (`p=0.070`; required `<=0.010`).
- WF MCPT: fail (`p=0.070`; required `<=0.050`).
- PBO: fail (`0.790`; required `<0.500`).
- DSR: fail (`p=0.1111`; required `<0.050`, `cumulative_n_trials=288`).
- WF windows: pass (`11/13` positive).
- OOS: pass (`+215.71%`).
- FWD 63d: pass (`+16.72%`).
- Bootstrap 99.9% mean daily CI: pass (`low=0.000182`).
- Cross-lib/reference parity: pass (`0.00pp` CAGR delta).

## Lessons

The mechanism is economically strong on the full aligned window, but the high PBO
and failed MCPT/DSR indicate selection/path fragility. The result is useful as a
diagnostic crash-rearm variant, not as a promotable strategy.

## Next Step

Do not locally tune `VXX` thresholds, normalization fractions or booster hold
lengths. Continue only with a different Phase 3 mechanism, or run a consolidation
audit that compares all economic beaters under common stress rules
`[testing_tuning, p.327-335]`.
