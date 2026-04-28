# Hypothesis — Iter 009 HAA Gayed Trend Canary

## Hypothesis

Keep the iter 009 HAA+Gold allocation shell unchanged, but replace or
confirm the `VWOSIM` HAA canary with a simple monthly Gayed-style trend
input on `SPYSIM` and `VTSIM`. The simple version is tested first:
12-month/252-day trend state only controls the HAA risk-on/risk-off switch;
the offensive assets, defensive assets, 10% `KMLMSIM`, and 5% `GLDSIM`
remain fixed. This is structurally different from standalone leveraged
equity because no 2x global-equity sleeve is introduced; the trend input is
only a regime classifier. Primary citation: `[leverage_for_the_long_run, p.40-60]`.

## Edge Source

Iter 009 HAA+Gold may miss gradual bear-market transitions because the
single `VWOSIM` absolute-momentum canary can lag broad US/global trend
deterioration; Gayed's moving-average filter explicitly targets the
large-loss left tail in equity exposure `[leverage_for_the_long_run, p.40-60]`.

## Datasets

- `educational`: VTSIM synthetic long window.
- `vt_real`: VTSIM proxy from 2008-06 because live VT is not pulled.
- `ndx_real`: QQQSIM stretch window from 2010-02.

## Pre-Committed Kill Criteria

Kill if the selected config has educational net Sharpe `<= 1.120`, or if
either real-data dataset has MDD above iter 009 + 5pp (`> 19.20%`). PBO,
DSR, walk-forward, OOS, forward-stress, bootstrap, and cross-lib gates use
the loop battery from `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Expected Budget

- Configs: 4 pre-committed canary modes.
- Wall-time: under 10 minutes for simulation, gates, scoring, and plots.
- Tax: `AnnualDarfEngine` only.

## Implementation Plan

1. Reuse iter 008 HAA+Gold simulator and validation helpers.
2. Keep offensive universe `NTSXSIM/NTSI/NTSE/GDESIM`, defensive universe
   `IEFSIM/BNDSIM/CASHX`, fixed `KMLMSIM` 10%, and fixed `GLDSIM` 5%.
3. Test four canary rules:
   - `vwo_original`: original HAA `VWOSIM` 1/3/6/12 momentum canary.
   - `spy_trend`: risk-on if `SPYSIM` is above its 10-month trend.
   - `vt_trend`: risk-on if `VTSIM` is above its 10-month trend.
   - `vwo_and_spy_trend`: risk-on only if `VWOSIM` HAA momentum and
     `SPYSIM` trend are both positive.
4. Select by maximum mean Sharpe divided by iter 009 Sharpe across the
   three datasets.
5. Save `results.json`, `verdict.json`, plots, final report, and memory
   updates.
