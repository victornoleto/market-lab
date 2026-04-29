# Iter 036 — SPMO-realloc (Phase 1B substitution source variation)

## Hypothesis (one paragraph)

**Highest-priority Phase 1B test.** Phase 1A iter 030 SPMO was the only
sleeve to survive both KILL #1 and KILL #2 (Δ vs iter 023 −0.072 /
+0.005 / +0.032 — beats 023 on 2/3, ndx_real substantive +0.032). The
balanced 50/50 substitution from NTSX+KMLM produced this signal at
SPMO 5% weight; this iter retests at fixed 10% weight under 3
alternative sub sources (NTSX-only, GDE-only, KMLM-only) to determine
if SPMO's +signal can be amplified by re-allocating the substitution
optimally. If subGDE produces ≥ +0.05 ndx_real (substantive)
**without degrading lh_56y**, SPMO becomes the strongest Phase 2
candidate.

## Primary citation

`[stocks_on_the_move, p.21-30]` Clenow time-series momentum +
Jegadeesh-Titman 1993 cross-sectional momentum.

## Configs (3, fixed 10% sleeve weight)

| config | NTSX | GDE | KMLM | TLT | SPMO |
|---|---:|---:|---:|---:|---:|
| spmo10_subNTSX | 15% | 25% | 35% | 15% | 10% |
| spmo10_subGDE  | 25% | 15% | 35% | 15% | 10% |
| spmo10_subKMLM | 25% | 25% | 25% | 15% | 10% |

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: no sub-source produces +signal vs
  iter 023 across ≥1/3 datasets → close direction.
- **KILL #2 (monotonic regression)**: not directly applicable.
- **KILL #3 (no-free-lunch synth)**: SPMO standalone Sharpe < 1.5
  (verified at runtime).

## Phase 1A reference

Phase 1A iter 030 selected `spmo_lite` (5% SPMO, balanced sub) Δ vs
iter 023: −0.072 / +0.005 / +0.032 (beats 2/3, ndx_real substantive).
Best balanced-sub at 10% (`spmo_mod`) Δ: −0.075 / −0.001 / +0.040.
Phase 1B tests if subGDE or subKMLM at 10% produces a stronger ndx_real
edge or recovers the lh_56y drag.
