# SUMMARY - Phase 3 Iteration 008

## Verdict

`economic_beater_not_validated`. No winner, no deploy implication, mandate remains
100% Plano C.

## Tested

Drawdown-adaptive gross exposure on the confirmed high-beta universe
`QQQ/SMH/SOXX/XLK`. Four configs stayed invested and increased gross exposure
defensive long/flat filter `[leverage_space, p.149-167]`,
`[systematic_trading, p.137-148]`.

## Benchmark Comparison

Best config: `top2_m63_dd15_boost125_cap150`.

- Strategy CAGR: 17.02%.
- Primary equal-weight `QQQ/SMH/SOXX/XLK` buy-and-hold CAGR: 15.50%.
- Strategy terminal wealth: 47.19x.
- Primary benchmark terminal wealth: 34.28x.
- Strategy MDD: -66.42% vs benchmark MDD -59.35%.
- SPY opportunity CAGR: 10.19%.

The economic Phase 3 floor passed, but this is not sufficient for promotion.

## Gates

- IS MCPT: fail (`p=0.105`; pass requires `p <= 0.01`).
- WF MCPT: fail (`p=0.960`; pass requires `p <= 0.05`).
- PBO: fail (`0.623`; pass requires `<0.5`).
- DSR: fail (`p=0.3293`; cumulative trials after = 256).
- Walk-forward windows: pass (`19/21` positive).
- OOS: pass (`+330.70%`).
- FWD 63d: pass (`+43.26%`).
- Bootstrap 99.9% mean daily CI: pass (low `0.000051`).
- Cross-lib/reference parity: pass (`0.0pp` CAGR delta).

## Lessons

Drawdown-adaptive sizing can lift terminal wealth above the equal-weight
opportunity benchmark, but the edge did not survive the anti-overfit stack. The
very high turnover of the top-2 sleeve (`18.03` annual gross turnover) and the
missing financing/tax model are additional caveats, not promotion blockers only
because statistical gates already failed.

## Next Step

Pivot to a different Phase 3 mechanism. Do not locally tune `top2_m63` lookback,
top-k, drawdown triggers or boost/cap values without a new mechanism
`[testing_tuning, p.327-335]`.
