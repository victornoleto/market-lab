# Iter 041 — F7-US-Stacked-MF (Phase 2 finalist construction)

## Hypothesis (one paragraph)

Tests the **stacked managed-futures** finalist (F7): RSST (ReturnStacked
US Equity & Managed Futures, 100% SPY + 100% KMLM via 2× notional)
combined with NTSX (90/60 stack), GDE (90/90 stack), KMLM separate, and
TLT. RSST encodes the "1+1=2" thesis: each dollar held delivers both
SPY beta and KMLM trend exposure. F7 is independent of Phase 1 sleeve
findings (RSST is its own axis). 4 weights sweep RSST 15→50% to find
whether stacked-MF philosophy beats separate NTSX+KMLM sleeves.

## Primary citation

`[risk_parity, ch.5]` Carlson capital-efficient stacking + ReSolve/
Newfound Return Stacked methodology (2023): RSST = 100% SPY + 100%
KMLM via 2× gross notional, single ETF wrapper.

## Configs (4)

| config | NTSX | RSST | GDE | KMLM | TLT |
|---|---:|---:|---:|---:|---:|
| f7_lite        | 25% | 15% | 25% | 20% | 15% |
| f7_balanced    | 15% | 30% | 25% | 15% | 15% |
| f7_rsst_heavy  | 10% | 40% | 25% | 10% | 15% |
| f7_pure_stack  |  0% | 50% | 25% | 10% | 15% |

ETF count: 4-5. Notional: ~150-160% (NTSX 1.5× + RSST 2.0× + GDE 1.5×).

## Phase 1 input

F7 is **independent of Phase 1** sleeve findings — RSST tests a new
axis (stacked MF) not validated by the Phase 1 sleeve sweep. KILL #5
(RSST standalone Sharpe < 1.5) was already validated in synth tests.

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: no F7 config beats iter 023 mean
  Sharpe across ≥1/3 datasets → F7 fails the finalist bar.
- **KILL #2 (monotonic regression)**: if RSST weight monotonically
  degrades Sharpe across the 15-50% band, stacked-MF philosophy is
  rejected; revert to NTSX+KMLM separate-sleeve baseline.
- **KILL #4 (frankenstein degradation)**: F7 is on independent axis,
  no constituent Phase 1 baseline test. Compare F7 best vs iter 023
  baseline (1.189 lh_56y) directly.
- **KILL #5 (no-free-lunch synth)**: already validated pre-iter 030
  (RSST standalone Sharpe < 1.5).

## Expected outcome

Two scenarios:

1. **f7_pure_stack** (50% RSST + 25% GDE + 10% KMLM + 15% TLT) achieves
   Sharpe ≥ iter 023 with much higher notional efficiency (4 ETFs vs
   iter 023's 4 — same count) → stacked-MF wins simplicity tie-breaker
   on C4 + C5 if score tied with F1/F3.

2. **Sharpe degrades** with RSST weight → RSST stacking philosophy does
   NOT beat separate sleeves (RSST internals already capture KMLM
   exposure that's accessible cheaper via direct KMLM ETF). In that
   case, f7_lite is selected and F7 acts as a slightly-worse F1 with
   marginally higher cost (RSST TER ≈ 0.97% vs KMLM 0.85%).

The pure-stack config (f7_pure_stack, NTSX 0%) is the most extreme
test: if RSST + GDE alone (no NTSX) underperforms iter 023, stacking
philosophy doesn't dominate diversified-stacking blend.
