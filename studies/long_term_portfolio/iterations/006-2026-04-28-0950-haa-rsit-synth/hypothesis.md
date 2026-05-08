# Hypothesis — Iter 006 HAA RSIT Synth

## Hypothesis

Keep the iter 009 HAA+Gold shell unchanged, but add a synthetic `RSIT_PROXY`
offensive candidate built as `VEASIM + KMLMSIM - 50bps/year`. The simple thesis
is that international equity plus managed futures in one capital-efficient
sleeve can capture the return-stacking diversification return without forcing
HAA to separately rank more low-return defensive sleeves `[risk_parity, ch.5]`.

This is marked **INCOMPLETE synthetic exploration** because RSIT has a filing
but no live ETF history in this cache. It is acceptable only as a directional
test before real RSIT data exists.

## Primary Citation

- Return-stacked / capital-efficient portfolio construction:
  `[risk_parity, ch.5]`, especially diversification return and leveraged
  benchmark construction.
- HAA monthly momentum ranking: `[stocks_on_the_move, ch.6]`.
- Gate battery: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Edge Source

Iter 009 HAA+Gold gets its convexity from fixed KMLM/gold sleeves; RSIT tests
whether putting managed futures on top of the international equity sleeve adds
return per unit risk without diluting the offensive book the way broader
RSST/RSSB/CTA substitutions did.

## Datasets

- `educational`: VTSIM long synthetic window.
- `vt_real`: VTSIM proxy from 2008-06 because VT cache is not pulled.
- `ndx_real`: QQQ stretch window from 2010-02.

## Pre-Committed Kill Criteria

Kill if educational net Sharpe is `<= 0.990`, the iter 004 plain HAA
international tilt result. This falsifies the idea that RSIT adds a distinct
incremental return source beyond the previous HAA+VEA/factor variants.

## Expected Budget

- 4 pre-committed configs.
- Expected wall time: under 10 minutes for backtest + gates + plots.
- No new shared simulator; reuse the iteration-local HAA harness and existing
  loop validation helpers.

## Implementation Plan

1. Build `RSIT_PROXY = VEASIM + KMLMSIM - 50bps/year` and keep `NTSXSIM`,
   `NTSI`, and `NTSE` construction from earlier HAA tests.
2. Test four offensive sets centered on `RSIT_PROXY`, selecting by mean
   Sharpe divided by iter 009 benchmark Sharpe across the three datasets.
3. Apply annual DARF through `AnnualDarfEngine`.
4. Run the seven gates, score via `scoring.py`, save `results.json`,
   `verdict.json`, plots, final report, and memory updates.
