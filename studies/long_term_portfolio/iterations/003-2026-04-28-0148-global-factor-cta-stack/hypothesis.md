# Hypothesis — Iter 003 Global Factor + CTA Stack

## Hypothesis

A low-turnover static capital-efficient stack can Pareto-advance iter 009 HAA+Gold by replacing tactical rotation with persistent exposure to global equity, Treasuries, gold, managed futures, and small/value factors. The core premise is risk-budget diversification: a capital-weighted stock/bond mix is equity-risk dominated, while combining independent risk premia and using stacked exposure can improve return per unit of drawdown `[risk_parity, p.1-2, p.10]`.

## Primary Citation

- `[risk_parity, p.1-2, p.10]`: traditional capital allocation hides risk concentration; risk parity starts with target risk allocation and can use leverage/capital efficiency to reach the desired return.
- Gate citations: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Edge Source

Iter 009 HAA+Gold misses the persistent global/factor core: it rotates through stacked offensive assets and fixed diversifiers, but still pays turnover/tax drag and defensive-state opportunity cost. This iteration tests whether static stacking captures similar protection with less regime-switching.

## Datasets

- `educational`: VTSIM synthetic long window, constrained by factor/CTA history.
- `vt_real`: VTSIM proxy from 2008-06 because real VT is not pulled.
- `ndx_real`: QQQSIM stretch test from 2010-02.

## Pre-Committed Kill Criteria

Kill if the selected best global config has educational net Sharpe `<= 1.120`, or if no tested config improves either Sharpe or CAGR versus the prior static stack family. Also kill as non-winner unless Sharpe beats iter 009 by `+0.10` on at least two datasets.

## Expected Budget

- Configs: 6 static weight mixes around `RSSBSIM`, `GDESIM`, `KMLMSIM`, `VBRSIM`, `VSSSIM`, `VWOSIM`, and `SPYSIM`.
- Wall time: less than 10 minutes for simulation, gates, scoring, reports, plots.
- Tax: `AnnualDarfEngine` only.

## Implementation Plan

1. Build iteration-local static portfolio runner using existing testfolio loader and metrics.
2. Expand return-stacked ETF proxies into effective synthetic legs.
3. Evaluate all configs on educational, vt_real, ndx_real.
4. Select one global config by mean normalized Sharpe across the three datasets.
5. Run the 7-gate battery on the selected config per dataset, including grid-level PBO and DSR with `n_trials = 6`.
6. Save `results.json`, `verdict.json`, plots, final report, memory updates, and jornada entry.
