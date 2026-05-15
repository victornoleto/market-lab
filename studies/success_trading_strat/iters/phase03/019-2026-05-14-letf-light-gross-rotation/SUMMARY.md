# SUMMARY - Phase 3 Iteration 019

## Verdict

`economic_beater_not_validated`. No strict winner, no candidate/watchlist label,
no paper-trade label, no deploy implication. Capital remains 100% Plano C.

## Tested

Pre-registered LETF-light/high-beta monthly rotation: rank `QLD`, `SSO`, `SMH`
and `SOXX` by lagged 63d/126d momentum, hold top-1 or top-2, and optionally use
gross 1.25 with explicit 5% annual financing drag above gross 1.0. Four configs
were tested.

Best config: `top2_m126_g125`.

## Benchmark Comparison

Aligned window: 2007-08-02 to 2026-05-13.

- Strategy CAGR: 23.77%; terminal wealth: 54.51x.
- Primary equal-weight `QLD/SSO/SMH/SOXX` B&H CAGR: 21.42%; terminal wealth: 38.05x.
- `SPY` opportunity B&H CAGR: 11.08%; terminal wealth: 7.18x.
- Context `QLD` B&H CAGR: 25.15%; terminal wealth: 67.08x.

The strategy passed the Phase 3 economic floor versus the pre-registered primary
benchmark and `SPY`, but did not beat raw `QLD` buy-and-hold context.

## Gates

- Physical daily files: pass for `QLD`, `SSO`, `SMH`, `SOXX`, `SPY`, `QQQ`, `SHV`.
- Economic CAGR/terminal wealth vs primary equal-weight universe: pass.
- IS MCPT: fail (`p=0.290`; required `<=0.010`).
- WF MCPT: fail (`p=0.860`; required `<=0.050`).
- PBO: fail (`0.591`; required `<0.500`).
- DSR: fail (`p=0.4351`; required `<0.050`, `cumulative_n_trials=292`).
- WF windows: pass (`13/15` positive).
- OOS: pass (`+474.99%`).
- FWD 63d: pass (`+54.08%`).
- Bootstrap 99.9% mean daily CI: fail (`low=-0.000045`).
- Cross-lib/reference parity: pass (`0.00pp` CAGR delta).

## Lessons

The mechanism produced another economic beater, but the validation profile is weak:
MCPT p-values are high, PBO exceeds the hard threshold and DSR is far from passing.
The gross 1.25 config also increased drawdown to -79.28%, so the return uplift is
not robust enough for promotion.

## Next Step

Do not locally tune the same `QLD/SSO/SMH/SOXX` momentum/gross family. Either pivot
to a distinct long/short/gross-exposure alpha mechanism with financing modeled, or
run a consolidation stress audit of Phase 3 economic beaters before spending more
trials `[testing_tuning, p.327-335]`.
