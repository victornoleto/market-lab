# Iter 035 — AVDV-realloc (Phase 1B substitution source variation)

## Hypothesis (one paragraph)

Phase 1A iter 029 tested AVDV (intl SCV factor) at 5/10/15/20% weights
with balanced 50/50 substitution from NTSX+KMLM. Result: KILL #1 + #2
both fired (Δ vs iter 023 −0.108 / −0.019 / −0.012, loses 3/3). This
iter retests at fixed 10% weight with 3 alternative substitution sources
(from NTSX-only, GDE-only, KMLM-only) to determine if the Phase 1A
failure was due to suboptimal substitution source rather than structural
sleeve subordination of intl SCV factor at 1× notional.

## Primary citation

`[ilmanen_expected_returns, ch.19]` intl factor diversification.

## Configs (3, fixed 10% sleeve weight)

| config | NTSX | GDE | KMLM | TLT | AVDV |
|---|---:|---:|---:|---:|---:|
| avdv10_subNTSX | 15% | 25% | 35% | 15% | 10% |
| avdv10_subGDE  | 25% | 15% | 35% | 15% | 10% |
| avdv10_subKMLM | 25% | 25% | 25% | 15% | 10% |

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: no sub-source produces +signal vs
  iter 023 across ≥1/3 datasets → sleeve confirmed closed.
- **KILL #2 (monotonic regression)**: not directly applicable.

## Phase 1A reference

Phase 1A iter 029 selected `avdv_lite` (5% AVDV, balanced sub) with Δ
vs iter 023: −0.108 / −0.019 / −0.012 (loses 3/3). At 10% weight under
balanced sub (`avdv_mod`), Δ was −0.114 / −0.042 / −0.033. This iter
tests if alternative substitutions improve any of the 3 datasets.
