# Phase 3.5f Cross-lib — engine replication

**Date:** 2026-04-22  |  **Verdict:** ✅ PASS (2/3 libs within ±3pp CAGR on OOS)

Isolates engine math (weights × asset returns → portfolio P&L) from cost/swap model by running canonical with cost=0, swap=0. Same weights matrix + same prices fed to bt, vectorbt, and backtrader. Reference `numpy` dot-product also shown.

## Concordance matrix (gross returns)

| Split | Engine | Sharpe | CAGR | ΔCAGR vs canon | ΔSharpe vs canon |
|---|---|---:|---:|---:|---:|
| IS | canonical | 0.563 | 11.60% | — | — |
| IS | numpy_ref | 0.563 | 11.60% | +0.000pp | +0.000 |
| IS | bt | ERROR | Cannot allocate capital to off_gld becau… | — | — |
| IS | vectorbt | 0.563 | 11.60% | +0.000pp | +0.000 |
| IS | backtrader | 0.563 | 11.60% | +0.000pp | +0.000 |
| OOS | canonical | 0.810 | 20.79% | — | — |
| OOS | numpy_ref | 0.810 | 20.79% | +0.000pp | +0.000 |
| OOS | bt | ERROR | Cannot allocate capital to off_gld becau… | — | — |
| OOS | vectorbt | 0.810 | 20.79% | +0.000pp | +0.000 |
| OOS | backtrader | 0.810 | 20.79% | +0.000pp | +0.000 |
| FWD | canonical | 1.013 | 27.21% | — | — |
| FWD | numpy_ref | 1.013 | 27.21% | +0.000pp | +0.000 |
| FWD | bt | ERROR | Cannot allocate capital to off_gld becau… | — | — |
| FWD | vectorbt | 1.013 | 27.21% | +0.000pp | +0.000 |
| FWD | backtrader | 1.013 | 27.21% | +0.000pp | +0.000 |

## Citations

- Two-stage + engine replication: `[advances_fin_ml, p.31-34]`
- Phase 3.5c cross-lib spec: `docs/superpowers/specs/2026-04-20-plano-b-cross-lib-validation-design.md`
