# SUMMARY - Phase 3 Iteration 015

## Verdict

`fail`. No winner, no deploy implication, mandate remains 100% Plano C.

## Tested

LETF-light dual-momentum rotation using real daily `QLD`, `SSO`, `TLT`, `GLD`,
`SHV` and `SPY` data. Four configs were pre-registered: top-1/top-2 selection by
126d or 252d positive momentum, monthly or quarterly rebalance. The mechanism was
intended to own the strongest available return engine rather than sit mostly in
cash `[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`,
`[leverage_for_the_long_run, p.13]`.

Physical daily files existed for all required tickers through 2026-05-13.

## Benchmark Comparison

Best config: `top1_m252_monthly`.

- Strategy CAGR: 13.74%.
- Strategy terminal wealth: 12.01x.
- Primary equal-weight `QLD/SSO/TLT/GLD` buy-and-hold CAGR/terminal wealth: 16.43% / 18.84x.
- `SPY` buy-and-hold CAGR/terminal wealth: 10.97% / 7.45x.
- Strategy MDD: -59.93% vs equal-weight -50.39% and `SPY` -55.20%.
- Context `QLD` buy-and-hold was much stronger: 24.84% CAGR and 72.37x.

The strategy beat `SPY`, but failed the pre-registered primary equal-weight
opportunity-universe benchmark in both CAGR and terminal wealth. Phase 3 therefore
requires `fail`.

## Gates

- Economic CAGR vs equal-weight `QLD/SSO/TLT/GLD`: fail.
- Economic terminal wealth vs equal-weight `QLD/SSO/TLT/GLD`: fail.
- Economic CAGR vs `SPY`: pass.
- Economic terminal wealth vs `SPY`: pass.
- MDD not worse than 1.5x primary benchmark MDD: pass.
- IS MCPT: fail (`p=0.420`; pass requires `p <= 0.01`).
- WF MCPT: fail (`p=0.770`; pass requires `p <= 0.05`).
- PBO: fail (`0.837`; pass requires `<0.5`).
- DSR: fail (`p=0.6558`; cumulative trials after = 284).
- Walk-forward windows: pass (`11/16` positive).
- OOS: pass (`+173.83%`).
- FWD 63d: pass (`+1.40%`).
- Bootstrap 99.9% mean daily CI: fail (low `-0.0002369`).
- Cross-lib/reference parity: pass (`0.0pp` CAGR delta).

## Lessons

The LETF-light rotation reduced the raw `QLD` exposure enough to lose to the
pre-registered opportunity universe while still carrying a large drawdown. The
validation stack was also weak: MCPT, PBO, DSR and bootstrap all failed. This is a
dead end unless a genuinely different return engine is specified.

## Next Step

Do not tune lookbacks, top-k, rebalance cadence or positive-momentum floors for
this family. Next Phase 3 work should move to a different mechanism, preferably a
pre-registered stress/consolidation audit of prior economic beaters or a distinct
crash-rearm/long-short design with explicit gross exposure `[testing_tuning,
p.327-335]`.
