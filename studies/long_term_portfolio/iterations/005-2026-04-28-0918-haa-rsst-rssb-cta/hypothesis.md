# Iter 005 Hypothesis — HAA RSST/RSSB/CTA Stack

## Hypothesis

Keep the iter 009 HAA+Gold shell unchanged: `VWOSIM` canary, top-2 offensive
selection, top-1 defensive selection, 10% `KMLMSIM`, and 5% `GLDSIM`.
Replace only the risk-on offensive candidates with simple return-stacked
building blocks: `RSSBSIM`, an `RSST_PROXY = SPYSIM + KMLMSIM - CASHX`,
`CTAPSIM` proxied by managed futures, and retained capital-efficient equity
anchors such as `NTSXSIM`, `NTSI`, or `GDESIM`. The simple version comes first:
no ML, no HMM, no multi-signal overlay. HAA provides the canary drawdown control
that static stacks lacked, while RSST/RSSB/CTA candidates add independent
trend-following and bond convexity inside the rankable offensive set
`[risk_parity, ch.5]`.

## Primary Citation

Primary: `[risk_parity, ch.5]` for return stacking and capital-efficient
portfolio construction. Secondary: `[stocks_on_the_move, p.21-30]` for trend
and momentum persistence; gate citations use `[advances_fin_ml, p.208-211,
p.222-223, p.196-202, p.31-34]`.

## Edge Source

Iter 009 HAA+Gold may miss the edge from ranking managed-futures stacking as a
risk-on candidate: it holds KMLM as a fixed 10% sleeve, while this test lets HAA
choose between equity+bond, equity+MF, and pure CTA concepts under the same
`VWOSIM` canary.

## Datasets To Test

- `educational`: VTSIM long synthetic window, 1995-01-01 to 2026-04-24.
- `vt_real`: VTSIM proxy from 2008-06-01 to 2026-04-24 because VT is not yet
  pulled in Tiingo.
- `ndx_real`: QQQSIM stretch test from 2010-02-01 to 2026-04-24.

All metrics are net of annual DARF using `AnnualDarfEngine` from
`studies/global_factor_tilt_loop/tax_engine_v2.py`.

## Pre-Committed Kill Criteria

Kill this hypothesis if either observable fires:

1. selected educational net Sharpe is `<= 0.990`, the iter 004 HAA factor-tilt
   result; or
2. selected net MDD breaches iter 009 MDD + 5pp on at least two datasets.

The run must not select a plain static stack; the HAA shell is part of the
hypothesis.

## Expected Budget

- Configs: 4 pre-committed HAA offensive sets.
- Wall-time: under 15 minutes for simulation plus gates.
- New simulator: no. This reuses the iter 004 HAA shell and loop-local scoring
  with a new offensive-set builder.

## Implementation Plan

1. Reuse the iter 004 HAA simulation, validation gates, AnnualDarfEngine
   tax wrapper, PBO, DSR, walk-forward, bootstrap, and numpy reference path.
2. Build synthetic `NTSXSIM`, `NTSI`, `RSST_PROXY`, and `CTAPSIM` columns from
   cached testfolio assets.
3. Test four offensive-set configs, select by mean Sharpe divided by iter 009
   Sharpe across the three datasets.
4. Save `results.json`, `verdict.json`, plots, final report, and memory
   updates.
