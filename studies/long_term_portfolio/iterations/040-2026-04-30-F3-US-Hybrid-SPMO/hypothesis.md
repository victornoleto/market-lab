# Iter 040 — F3-US-Hybrid-SPMO (Phase 2 finalist construction)

## Hypothesis (one paragraph)

Tests the **US Hybrid** finalist (F3): formalises iter 023 (NTSX+GDE+
KMLM+TLT) baseline plus SPMO at 4 candidate weights (5/10/15/20%) using
the Phase 1B-validated KMLM-substitution rule. Phase 1A iter 030 showed
SPMO 5% balanced-sub yields ndx_real +0.032 vs iter 023; Phase 1B iter
036 showed subKMLM at 10% yields ndx_real +0.044 (38% better than 1A).
This iter sweeps SPMO weight 5→20% with KMLM as the sole substitution
source to find the optimum and confirm whether SPMO is monotonic
beneficial in the 5-20% band or shows diminishing returns.

## Primary citation

`[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking baseline +
`[stocks_on_the_move, p.21-30]` Clenow time-series momentum (SPMO
sleeve choice).

## Configs (4)

| config | NTSX | GDE | KMLM | TLT | SPMO |
|---|---:|---:|---:|---:|---:|
| f3_spmo_5_subKMLM  | 25% | 25% | 30% | 15% |  5% |
| f3_spmo_10_subKMLM | 25% | 25% | 25% | 15% | 10% |
| f3_spmo_15_subKMLM | 25% | 25% | 20% | 15% | 15% |
| f3_spmo_20_subKMLM | 25% | 25% | 15% | 15% | 20% |

ETF count: 5. Notional: ~135% (NTSX 1.5× + GDE 1.5× internal leverage).

## Phase 1 input

F3 uses:
- **iter 023 baseline** (NTSX 25 + GDE 25 + KMLM 35 + TLT 15) as
  structural anchor — Phase 1 confirmed 12 iters of additions/swaps
  cannot improve it substantively.
- **SPMO** sleeve (Phase 1 WINNER) added at 5-20% with KMLM as the
  exclusive substitution source (per Phase 1B iter 036 finding that
  subKMLM yields the strongest ndx_real edge +0.044).

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: no SPMO weight in 5-20% band beats
  iter 023 mean Sharpe across ≥1/3 datasets → F3 = iter 023 (no SPMO
  add) as finalist; SPMO sleeve add is non-additive.
- **KILL #2 (monotonic regression)**: if Sharpe degrades monotonically
  with SPMO weight, signal is fragile; flag in report.
- **KILL #4 (frankenstein degradation)**: best F3 Sharpe should be ≥
  iter 023 baseline Sharpe (1.189 lh_56y). If significantly below,
  SPMO addition is hurting more than helping → revert to iter 023
  baseline as F3.
  - iter 023 baseline: lh_56y **1.189** / vt **1.004** / ndx **1.135**.
  - SPMO Phase 1 best: lh_56y 1.117 / vt 1.009 / ndx 1.167 (iter 030).
  - Expected F3 best: lh_56y ~1.16 / vt ~1.00 / ndx ~1.18 (iter 023 +
    SPMO ndx_real +0.044 from Phase 1B subKMLM).

## Expected outcome

Expected to beat iter 023 modestly: ndx_real +0.04 (Phase 1B finding
predicts), lh_56y modest drag (−0.03 to −0.05), vt_real near-flat. Best
config probably f3_spmo_10_subKMLM or f3_spmo_15_subKMLM (sweet spot
between sleeve dilution and momentum exposure). If KILL #1 fires (no
config beats iter 023 on any dataset), SPMO sleeve add is rejected
and F3 finalist reverts to iter 023.
