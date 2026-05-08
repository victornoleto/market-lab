# Hypothesis — Iter 007 HAA Defensive KMLM/CASH

## Hypothesis

Keep the iter 009 HAA+Gold offensive shell unchanged, but replace only the
defensive-state candidate set. The simple version tests whether HAA's false
defensive states can lose less Sharpe by moving the 85% dynamic sleeve into
`KMLMSIM`, `CASHX`, or a small `IEFSIM` bridge instead of the original
`IEFSIM`/`BNDSIM`/`CASHX` top-1 defense. The HAA relative/absolute momentum
shell remains monthly and simple `[stocks_on_the_move, ch.6]`; the defensive
choice is motivated by diversifier risk budgeting rather than adding another
offensive return-stacked sleeve `[risk_parity, ch.5]`.

The formal `BASE_MEMORY.md` promising entry left active for this iteration is
blocked as "DO NOT RUN AS PLAIN STATIC". This hypothesis therefore uses the
next documented open direction from `DEAD_ENDS.md` DE-007/DE-008 and iter 006:
HAA defensive-state changes focused on Sharpe.

## Primary Citation

- HAA / cross-sectional momentum shell: `[stocks_on_the_move, ch.6]`.
- Defensive diversifier/risk-budget rationale: `[risk_parity, ch.5]`.
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Edge Source

Iter 009 HAA+Gold may miss Sharpe in false defensive states: it already owns
fixed KMLM/gold convexity, but its dynamic 85% sleeve can still rotate into
low-return bonds/cash when `VWOSIM` briefly flags risk-off.

## Datasets

- `educational`: `VTSIM` proxy, 1995-01-01 to 2026-04-24.
- `vt_real`: `VTSIM` proxy, 2008-06-01 to 2026-04-24.
- `ndx_real`: `QQQSIM` stretch, 2010-02-01 to 2026-04-24.

## Pre-Committed Kill Criteria

Kill if the selected config has educational net Sharpe `<= 1.120` or if zero
datasets beat iter 009 by `+0.10` Sharpe. A defensive-only change must either
match the existing HAA+Gold Sharpe frontier on the long window or show a clear
cross-dataset Sharpe edge; otherwise the original defense remains superior.

## Expected Budget

- Configs: 4 pre-committed defensive variants.
- Wall-time: ~5-10 minutes for all datasets, gates, scoring, plots.
- New shared simulator: no. Reuse the iteration-local HAA harness and
  `AnnualDarfEngine`.

## Implementation Plan

1. Reuse the iter 006 HAA harness but restore iter 009 offensive candidates:
   `NTSXSIM`, `NTSI`, `NTSE`, `GDESIM`.
2. Test four defensive-state configs: original `IEFSIM/BNDSIM/CASHX`,
   `KMLMSIM/CASHX`, `KMLMSIM/IEFSIM/CASHX`, and `CASHX`-only.
3. Select by mean Sharpe divided by iter 009 Sharpe across the three datasets.
4. Run all seven gates with DSR `n_trials = 4`, score using
   `studies/long_term_portfolio/scoring.py`, save `results.json` and
   `verdict.json`, then generate mandatory plots.
