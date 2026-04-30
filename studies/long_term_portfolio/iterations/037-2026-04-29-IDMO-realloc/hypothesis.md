# Iter 037 — IDMO-realloc (Phase 1B substitution source variation)

## Hypothesis (one paragraph)

Phase 1A iter 031 tested IDMO (intl mirror of SPMO; intl developed
momentum) at 5/10/15/20% with balanced 50/50 substitution. Result:
KILL #2 fired (Sharpe falls monotonically with IDMO weight on all 3
datasets), KILL #1 cosmetic (1/3 ndx_real +0.005). Δ vs iter 023
−0.082 / −0.020 / +0.005. This iter retests at fixed 10% weight under
3 alternative sub sources to determine if reallocation amplifies the
cosmetic ndx_real edge to substantive (±0.05) or recovers lh_56y drag.

## Primary citation

`[ilmanen_expected_returns, ch.19]` intl factor diversification +
`[stocks_on_the_move, p.21-30]` Clenow time-series momentum +
Jegadeesh-Titman 1993 cross-sectional momentum.

## Configs (3, fixed 10% sleeve weight)

| config | NTSX | GDE | KMLM | TLT | IDMO |
|---|---:|---:|---:|---:|---:|
| idmo10_subNTSX | 15% | 25% | 35% | 15% | 10% |
| idmo10_subGDE  | 25% | 15% | 35% | 15% | 10% |
| idmo10_subKMLM | 25% | 25% | 25% | 15% | 10% |

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: no sub-source produces +signal vs
  iter 023 across ≥1/3 datasets → close direction.
- **KILL #2 (monotonic regression)**: not directly applicable.
- **KILL #3 (no-free-lunch synth)**: IDMO standalone Sharpe < 1.5.

## Phase 1A reference

Phase 1A iter 031 selected `idmo_lite` (5% IDMO, balanced sub) Δ vs
iter 023: −0.082 / −0.020 / +0.005 (cosmetic 1/3). Best balanced-sub
at 10% (`idmo_mod`) Δ: −0.099 / −0.052 / −0.012. Phase 1B tests if
sub-source variation recovers the +signal.
