# Iter 039 — F2-US-Factor-only (Phase 2 finalist construction)

## Hypothesis (one paragraph)

Tests the **pure factor philosophy** finalist (F2): equity exposure
delivered exclusively via vanilla VTI plus US factor tilts (AVUV small-
value + SPMO momentum), diversified by KMLM/TLT/GLD. **No stacking
ETFs**. AVUV is included despite both Phase 1A (Δ vs iter 023 −0.074 /
−0.008 / +0.005) and Phase 1B (best subGDE Δ −0.021 / −0.029 / −0.013)
indicating it is the best-available US non-momentum factor near-miss in
the testfolio universe — its lh_56y delta of −0.021 in Phase 1B subGDE
is the least bad of the Avantis family. SPMO is the single Phase 1
winner. The hypothesis: a 100%-notional, no-leverage 6-ETF factor
portfolio scores well on simplicity (C4) and TER (C5) even if its
Sharpe is modestly below F1/F3.

## Primary citation

`[risk_parity, ch.2, p.37-41]` Fama-French factor framework +
`[stocks_on_the_move, p.21-30]` Clenow time-series momentum
(SPMO retention) + Frazzini-Israel-Moskowitz 2018 (long-only momentum
capture coefficient ~0.60).

## Configs (4)

| config | VTI | AVUV | SPMO | KMLM | TLT | GLD |
|---|---:|---:|---:|---:|---:|---:|
| f2_balanced     | 35% | 15% | 10% | 20% | 10% | 10% |
| f2_factor_heavy | 25% | 25% | 15% | 15% | 10% | 10% |
| f2_avuv_heavy   | 30% | 25% |  5% | 20% | 10% | 10% |
| f2_spmo_heavy   | 30% | 10% | 20% | 20% | 10% | 10% |

ETF count: 6. Notional: 100% (no leverage).

## Phase 1 input

F2 uses:
- **AVUV** sleeve (despite Phase 1A/1B both negative on substantive
  metrics; included as best-available US non-momentum factor — Phase
  1B subGDE lh_56y delta −0.021 is least bad of Avantis family).
- **SPMO** sleeve (Phase 1 WINNER; Δ vs iter 023 ndx_real +0.044
  with subKMLM, +0.032 with balanced sub).

Diversifiers KMLM/TLT/GLD are not Phase 1 sleeves but conventional
defensive ballast (already validated in iter 011/023 baselines).

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: best F2 config does not beat iter
  023 mean Sharpe across ≥1/3 datasets → F2 fails the finalist bar.
- **KILL #2 (monotonic regression)**: not directly applicable (configs
  vary in 2 dimensions).
- **KILL #4 (frankenstein degradation)**: best F2 Sharpe must beat the
  mean of (best AVUV Phase 1 Sharpe, best SPMO Phase 1 Sharpe) per
  dataset. If F2 < mean, factor combination is non-additive.
  - AVUV Phase 1 best: lh_56y 1.115 / vt 0.996 / ndx 1.140 (iter 028).
  - SPMO Phase 1 best: lh_56y 1.117 / vt 1.009 / ndx 1.167 (iter 030).
  - Mean: lh_56y **1.116** / vt **1.003** / ndx **1.153**.

## Expected outcome

Expected to underperform F1 (iter 023) and F3 on Sharpe by 0.05-0.10
(no leverage on equity sleeve = no stacking edge). Expected to score
modestly on C1 (Sharpe edge) but well on C4 (simplicity, 6 ETFs all
single-style) and C5 (TER, no expensive stacking ETF wrappers). KILL
#4 likely fires given that AVUV+SPMO synth correlation should be
high (both US large/mid cap factor) — non-additive blend is the
most likely mechanism.
