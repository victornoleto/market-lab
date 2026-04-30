# Iter 038 — AVEM-realloc (Phase 1B substitution source variation)

## Hypothesis (one paragraph)

Phase 1A iter 032 tested AVEM (Avantis EM Equity factor-tilted) at
5/10/15/20% with balanced 50/50 substitution. Result: BOTH KILLs
fired (steepest monotonic regression of any Phase 1 sleeve, Δ −0.107 /
−0.035 / −0.020 vs iter 023). This iter retests at fixed 10% weight
under 3 alternative sub sources. **CAVEAT**: AVEMSIM uses VWOSIM
which starts 1994-05-04 → effective lh_56y window is **32y (1994-2026)**,
NOT 56y. Sub-source variation does not change this fundamental window
constraint — the 32y window is biased against EM-tilted portfolios
since 1994-2026 was a US-large-cap regime ~3-4pp/yr CAGR ahead of EM.

## Primary citation

`[ilmanen_expected_returns, ch.19]` intl + EM diversification.

## Configs (3, fixed 10% sleeve weight)

| config | NTSX | GDE | KMLM | TLT | AVEM |
|---|---:|---:|---:|---:|---:|
| avem10_subNTSX | 15% | 25% | 35% | 15% | 10% |
| avem10_subGDE  | 25% | 15% | 35% | 15% | 10% |
| avem10_subKMLM | 25% | 25% | 25% | 15% | 10% |

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: no sub-source produces +signal vs
  iter 023 across ≥1/3 datasets → close direction.
- **KILL #2 (monotonic regression)**: not directly applicable.

## Phase 1A reference

Phase 1A iter 032 selected `avem_lite` (5% AVEM, balanced sub) Δ vs
iter 023: −0.107 / −0.035 / −0.020 (loses 3/3, steepest decline of all
6 Phase 1 sleeves). This iter tests if alternative substitutions at
10% weight improve any of the 3 datasets.

## Window caveat (CRITICAL)

VWOSIM (EM equity underlying AVEMSIM) starts 1994-05-04. Effective
lh_56y window is **32y (1994-2026)**, NOT 56y. Verified at runtime in
iter 032 (8042 daily obs). vt_real (2008+) and ndx_real (2010+) windows
unaffected. The 32y window is structurally biased against EM-tilted
portfolios — sub-source variation cannot fix this.
