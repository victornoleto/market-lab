# Iter 033 — NTSD-realloc (Phase 1B substitution source variation)

## Hypothesis (one paragraph)

Phase 1A iter 027 tested NTSD at 5/10/15/20% weights with balanced 50/50
substitution from NTSX+KMLM. Result: KILL #1 (no-positive-config) and
KILL #2 (monotonic regression) both fired (Sharpe Δ −0.097 / −0.024 / −0.010
vs iter 023 across lh_56y / vt_real / ndx_real). This iter retests at
fixed 10% weight with 3 alternative substitution sources (from NTSX-only,
GDE-only, KMLM-only) to determine if the Phase 1A failure was due to
suboptimal substitution source rather than structural sleeve subordination.
A positive Δ on ≥1/3 datasets under any sub source would re-open the
sleeve for Phase 2; otherwise sleeve closure is reaffirmed.

## Primary citation

`[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking + WisdomTree
NTSD prospectus 2026-03-19 (90% SPY + 60% VEA futures internal).

## Configs (3, fixed 10% sleeve weight)

| config | NTSX | GDE | KMLM | TLT | NTSD |
|---|---:|---:|---:|---:|---:|
| ntsd10_subNTSX | 15% | 25% | 35% | 15% | 10% |
| ntsd10_subGDE  | 25% | 15% | 35% | 15% | 10% |
| ntsd10_subKMLM | 25% | 25% | 25% | 15% | 10% |

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: no sub-source produces +signal vs
  iter 023 (lh_56y=1.189, vt_real=1.004, ndx_real=1.135) across ≥1/3
  datasets → sleeve confirmed closed (no re-open).
- **KILL #2 (monotonic regression)**: not directly applicable (only 1
  weight tested across sub-sources).
- **KILL #3 (no-free-lunch synth)**: not applicable (NTSDSIM is the
  literal WisdomTree blueprint, not an academic UMD overlay).

## Phase 1A reference

Phase 1A iter 027 selected `ntsd_lite_2055` (5% NTSD, balanced sub from
NTSX+KMLM 50/50) with Δ vs iter 023: −0.097 / −0.024 / −0.010 (loses
3/3). At 10% weight under balanced sub (`ntsd_mod_15105`), Δ was
−0.117 / −0.048 / −0.027. This iter tests if alternative substitutions
(from NTSX-only, GDE-only, or KMLM-only) at 10% weight improve any of
the 3 datasets vs iter 023 baseline.
