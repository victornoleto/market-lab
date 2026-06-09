# Phase 5 - RSC Overlay Rebuilt-Sleeve Diagnostic

Status: research-only diagnostic. This phase does not authorize deployment,
paper trading or a mandate change.

## Purpose

Answer the follow-up question left by `lrs/CONCLUSION.md`: if standalone LRS is
inferior to RSC-US `35/40/25`, does a small LRS/T3d satellite improve the RSC
core enough to justify continued work?

## RSC Sleeve Data

This phase now uses the local RSC-US sleeve-return matrix at
`studies/return_stacked_core/us_core/series/return_stacked_core_sleeve_returns.parquet`.
The core is rebuilt monthly as `35% GDESIM / 40% RSSTSIM / 25% ZROZSIM`. Current
`RSSTSIM` is the user-requested tracking proxy:
`SPYSIM + 0.70*DBMFSIM + 0.30*KMLMSIM - (CASHX + 0.0200/252)`, equivalent to the
Testfol.io comparison payload `100% SPY + 70% DBMF + 30% KMLM - 100% CASHX?E=-2`.
It is not a live ETF backfill `[risk_parity, p.80-81]`, `[systematic_trading,
p.185-188]`.

## Candidate Set

- `100% RSC-US 35/40/25` baseline rebuilt from sleeve returns.
- `90/10`, `80/20`, `70/30` RSC + local `lrs/` SPY headline satellite.
- `90/10`, `80/20`, `70/30` RSC + local `lrs/` QQQ headline satellite.
- `90/10`, `80/20`, `70/30` RSC + `letf-lab` T3d-K2 saved equity satellite.

Allocations are monthly rebalanced as a diagnostic control, not as an account
tax implementation. RSC remains a gross/static sleeve diagnostic; local LRS
satellites are after-tax under the existing annual DARF model. This tax mix is
deliberately disclosed and should not be read as a deployable account-level tax
simulation `[testing_tuning, p.327-335]`, `[systematic_trading, p.185-188]`.
