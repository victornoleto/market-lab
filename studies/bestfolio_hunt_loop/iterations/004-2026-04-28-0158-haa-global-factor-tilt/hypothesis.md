# Hypothesis — Iter 004 HAA Global Factor Tilt

## Hypothesis

Keep the iter 009 HAA+Gold architecture intact, but replace the plain international developed offensive sleeve with a small/value-tilted blend. The simple version is a pre-committed four-point tilt ladder where the HAA `NTSI` leg uses `VEASIM` blended with `VBRSIM` and `VSSSIM`, while the canary, defensive assets, top-2 offensive selection, 10% `KMLMSIM`, and 5% `GLDSIM` sleeves remain unchanged. The design follows HAA-style relative/absolute momentum for the regime shell `[stocks_on_the_move, ch.6]` and tests whether factor diversification inside the offensive sleeve can add return without losing the canary drawdown control.

## Primary Citation

- HAA / relative momentum shell: `[stocks_on_the_move, ch.6]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Edge Source

Iter 009 HAA+Gold captures regime switching, managed futures, and gold, but its international offensive exposure is mostly developed-market beta; this test asks whether a modest small/value tilt captures an additional rewarded factor while preserving the HAA canary.

## Datasets

- `educational`: VTSIM proxy, `1995-01-01` to `2026-04-24`.
- `vt_real`: VTSIM proxy, `2008-06-01` to `2026-04-24`.
- `ndx_real`: QQQSIM stretch, `2010-02-01` to `2026-04-24`.

## Pre-Committed Kill Criteria

- Kill if selected config educational net Sharpe is `<= 1.120`; this direction must improve on iter 009, not merely pass robustness gates.
- Kill if fewer than two datasets beat iter 009 Sharpe by `+0.10`, because the loop's winner condition is explicitly a Sharpe frontier advance.

## Expected Budget

- Configs: 4 pre-committed factor-tilt variants.
- Wall-time: under 10 minutes for simulation, gates, scoring, and plots.
- Tax: `AnnualDarfEngine` only.

## Implementation Plan

1. Reuse the iter 009 HAA+Gold simulator mechanics and bestfolio scoring rubric.
2. Add a loop-local `backtest.py` that builds `NTSI_TILT` as `0.90 * blended_equity + 0.60 * IEFSIM - 0.50 * CASHX`.
3. Run all four configs across `educational`, `vt_real`, and `ndx_real`, select by mean Sharpe divided by iter 009 Sharpe across datasets.
4. Apply `AnnualDarfEngine` to the selected daily tactical path.
5. Save `results.json`, `verdict.json`, plots, final report, and update loop memory.
