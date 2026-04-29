# Iter 034 — AVUV-realloc (Phase 1B substitution source variation)

## Hypothesis (one paragraph)

Phase 1A iter 028 tested AVUV at 5/10/15/20% weights with balanced 50/50
substitution from NTSX+KMLM. Result: KILL #2 fired (Sharpe falls
monotonically with AVUV weight), KILL #1 cosmetic (1/3 datasets beat
iter 023 only +0.005 ndx_real). Δ vs iter 023 −0.074 / −0.008 / +0.005.
This iter retests at fixed 10% weight with 3 alternative substitution
sources (from NTSX-only, GDE-only, KMLM-only) to determine if the
Phase 1A subordination was due to suboptimal substitution source rather
than structural sleeve weakness in the post-2008 "death of value"
regime spanned by lh_56y.

## Primary citation

`[risk_parity, ch.2, p.37-41]` Fama-French SCV factor framework +
[FF 1993] size+value premia.

## Configs (3, fixed 10% sleeve weight)

| config | NTSX | GDE | KMLM | TLT | AVUV |
|---|---:|---:|---:|---:|---:|
| avuv10_subNTSX | 15% | 25% | 35% | 15% | 10% |
| avuv10_subGDE  | 25% | 15% | 35% | 15% | 10% |
| avuv10_subKMLM | 25% | 25% | 25% | 15% | 10% |

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: no sub-source produces +signal vs
  iter 023 (lh_56y=1.189, vt_real=1.004, ndx_real=1.135) across ≥1/3
  datasets → sleeve confirmed closed.
- **KILL #2 (monotonic regression)**: not directly applicable (only 1
  weight tested across sub-sources).

## Phase 1A reference

Phase 1A iter 028 selected `avuv_lite` (5% AVUV, balanced sub from
NTSX+KMLM 50/50) with Δ vs iter 023: −0.074 / −0.008 / +0.005. At 10%
weight under balanced sub (`avuv_mod`), Δ was −0.077 / −0.023 / −0.003.
This iter tests if alternative substitutions at 10% weight improve any
of the 3 datasets vs iter 023 baseline.
