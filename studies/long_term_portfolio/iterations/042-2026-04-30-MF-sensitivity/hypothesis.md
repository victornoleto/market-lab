# Iter 042 — MF sleeve sensitivity on iter 023 baseline (Phase 3)

## Hypothesis (one paragraph)

iter 023 (NTSX+GDE+KMLM+TLT 25/25/35/15) used KMLMSIM as the loop default
for MF sleeve due to its 38y testfolio history. For 20-30y deploy decisions,
DBMF (iMGP DBi, ~$3.2B AUM, replicates SG CTA Index — 5x AUM of KMLM ETF)
or 50/50 split may be more robust. This iter tests if substituting KMLMSIM
with DBMFSIM or 50/50 mix in iter 023 base materially affects Sharpe/CAGR/MDD.

## Primary citation

[ilmanen_expected_returns, ch.19] MF crisis-alpha role; iMGP DBi DBMF
prospectus + KFA MLM Index prospectus + Simplify CTA prospectus.

## Configs (4)

| config | NTSX | GDE | KMLM | DBMF | TLT | rationale |
|---|---:|---:|---:|---:|---:|---|
| mf_kmlm (baseline) | 25% | 25% | 35% | 0% | 15% | iter 023 unchanged |
| mf_dbmf | 25% | 25% | 0% | 35% | 15% | full DBMF substitution |
| mf_split | 25% | 25% | 17.5% | 17.5% | 15% | 50/50 engine + AUM diversification |
| mf_cta_proxy | 25% | 25% | 35% | 0% | 15% | structurally = mf_kmlm; flags CTA Simplify as deploy alternative requiring future modeling |

## Window caveat

DBMFSIM 1999+. mf_dbmf and mf_split limited to 26y intersection on lh_56y.
Comparison apples-to-apples on the 26y window only. Documented in final_report.md.

## Selection rule

Highest mean(gross_Sharpe) across the 3 datasets where DBMF and KMLM both
have data (1999-2026 effective for cross-MF comparison).

## Deploy recommendation

Output: in final_report.md, recommend the best MF sleeve for retirement deploy.
Factors: AUM (>$1B preferred for 20-30y), TER, engine transparency, Sharpe
robustness on the 26y intersection.

## INCOMPLETE flag

mf_cta_proxy uses KMLMSIM as proxy because Simplify CTA's Altis engine
(multi-strategy: trend + carry + mean-reversion + risk-off) is not modeled
in testfolio. This config is INCOMPLETE — only the kmlm/dbmf/split configs
are honest comparisons.
