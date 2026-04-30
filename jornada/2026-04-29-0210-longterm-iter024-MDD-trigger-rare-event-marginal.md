# Iter 024 — MDD-trigger defensive: rare-event firing, marginal positivo

**Data**: 2026-04-29 (UTC, 02:10)
**Iter**: 024, slug `iter011-MDD-trigger-defensive`
**Verdict**: NEW STRONG 82/100 winner_conds=True | LEGACY STRONG 87/100

## TL;DR

Testei trigger defensive: quando SPY 21d return < threshold negativo,
substituir 50% NTSX por TLT (ou CASH). 3 configs (10%/15% TLT, 15% CASH).
Resultado: trigger fires APENAS 1-2% do tempo — efetivamente é iter 011
99% do tempo + raras shifts em crises (2008 Q4, 2020 Q1, 2022 Q2).

Marginal +signal vs iter 011 nos 3 datasets (loose +0.099/+0.022/+0.019),
mas **iter 023 TLT-static (15% contínuo) domina iter 024 em todos os
datasets** — Sharpe 1.189 vs 1.145, 1.004 vs 0.982, 1.135 vs 1.123.

Lição DE-024: TLT contínuo > TLT condicional pra long-term portfolio.
A vantagem da defensiva episódica é tail-risk reduction concentrada em
~3 dias/ano, mas o cost of "OFF state being base 99% of time" se traduz
em zero accumulated alpha.

## Score

NEW SPY-only: 82/100 STRONG (winner_conds=True). 25 Sharpe edge + 17 gates
(c2 pior pois lh_56y 5/7) + 15 DSR + 5 CAGR (warning) + 15 MDD + 5 rob.

LEGACY: 87/100 STRONG (CAGR 10pts vs 5).

## Cross-config

| config | lh_56y | vt_real | ndx_real | pct_on |
|---|---:|---:|---:|---:|
| 10pct_TLT ✅ | 1.145 | 0.982 | 1.123 | 1.3% |
| 15pct_TLT | 1.141 | 0.978 | 1.124 | 0.7% |
| 15pct_CASH | 1.138 | 0.981 | 1.117 | 0.7% |

Cluster within 0.01 — selection at noise level. PBO N=3 warning (CSCV
unstable abaixo de N=4) reported informationally.

## Honesty checks

- Forward-looking signal (no peek): `pct_change(21).shift(1)` — signal
  observed at close t-1, action effective close t.
- Edge muito concentrado em <1% dos dias — 99% do tempo iter 024 é iter 011.
- Bootstrap CI low > 0 nos 3 datasets, mas vt_real edge +0.022 está dentro
  de typical PBO selection variance.

## Comparação iter 023 vs iter 024

iter 023 (TLT-static 15%) > iter 024 (TLT-trigger 10pct) em todos os
datasets:
- lh_56y: 1.189 vs 1.145 (Δ +0.044)
- vt_real: 1.004 vs 0.982 (Δ +0.022)
- ndx_real: 1.135 vs 1.123 (Δ +0.012)

E MDD também: iter 023 melhor em vt_real (17.40 vs 19.07%) e ndx_real
(11.76 vs 12.02%); essentially tied em lh_56y (21.13 vs 25.20%).

Decisão: continue testando iter 025/026 mas iter 023 é o forte candidate
do batch atual.

## Citações

- `[risk_parity, ch.5, p.10]` Carlson capital-efficient base
- `[systematic_trading, p.137-148]` Carver regime-conditional sizing
- `[advances_fin_ml, p.208-211, p.222-223]` PBO/DSR
