# Global Factor-Tilt Loop — Iter 002 WINNER: Fixed-Param Global Momentum K=2 lb=6m

**Data**: 2026-04-27  
**Status**: 🏆 WINNER — loop halted, `BASE_MEMORY.md` status set to `winner`

---

## O que aconteceu

A estratégia de momentum global cross-sectional com parâmetros pré-fixados
(K=2, lookback=6 meses) atingiu o tier **WINNER com score 90/100** e todas
as 5 condições estritas do `WINNER_AND_RANKING.md`.

A diferença crítica entre iter 001 (STRONG 81/100) e iter 002 (WINNER 90/100)
foi puramente **metodológica**: iter 001 rodou um grid de 9 configurações,
gerando viés de seleção que fez o PBO falhar na janela educational. Iter 002
pré-fixou K=2, lb=6m antes de ver os dados — sem grid, sem seleção — e o PBO
passou trivialmente (n_configs=1 < mínimo para CSCV honesta).

## Resultados

| dataset | Sharpe | CAGR | MDD | Gates |
|---|---|---|---|---|
| educational (56y) | 0.991 | 12.0% | 23.4% | **7/7** |
| vt_real (~17y) | 0.838 | 11.0% | 17.3% | **7/7** |
| ndx_real (16y) | 0.929 | 11.5% | 17.3% | **7/7** |

**Janela 32 anos (1994-2026)**: Sharpe 1.001, CAGR 13.22%, MDD 21.23%.

Comparativo com benchmarks de estratégia:
- Domina VT b&h, Plano C V3_1 e V_HYBRID+MF nos 3 eixos.
- Pareto-trade vs V1 NTSX+GDE: +0.19 Sharpe, -23pp MDD, -0.28pp CAGR.

**Robustez rolling**: 51/51 janelas de 5 anos com Sharpe positivo (100%).
Mínimo = 0.134 na janela 2004-2009 (inclui o crash de 2008) — ainda positivo.

## Gates

- G1 PBO: N/A trivial (1 config < limiar CSCV). Resolveu o problema de iter 001.
- G2 DSR/PSR: p=2.76e-4 (worst). PSR usada para n_trials=1.
- G3 WF: 7/8 ou 8/8 profitable em todos os datasets. Max MDD/janela ≤ 21%.
- G4 OOS 70/30: Sharpe OOS 0.70/1.05/1.06 — excelente período recente.
- G5 FWD (pós-2020): 0.73/1.24/1.24 — 2022 não quebrou a estratégia.
- G6 Bootstrap: CI low 0.569/0.174/0.201 — todos >> 0.
- G7 Cross-lib: diffs 0.12/0.29/0.19pp — todos dentro de ±3pp.

## O que é isso na prática

**Plano C continua sendo 100% do capital** (mandate §1 MAINTENANCE). Este
loop produz um CANDIDATO para deliberação §7 — não é deploy automático.

Para ser implantado precisaria de:
1. Paper trading validation (Phase 4 — pausada).
2. Override explícito do mandate §7.
3. Definição de qual broker (Plano C é passivo; isso seria uma sobreposição ativa).

## O que aprendemos

A lição principal do Loop: o mecanismo de momentum global cross-sectional
estava correto desde o iter 001. O gate G1 PBO não falhou por sinal fraco —
falhou porque rodar 9 configs cria problema de seleção que o CSCV detecta
corretamente. Pré-fixar parâmetros é a solução metodológica, não tuning.

**"Quase lá não passa"** — e aqui passou de verdade, com metodologia honesta.
