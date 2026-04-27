# Global Factor-Tilt Loop — Iter 009: HAA+Gold WINNER (90/100)

## O que aconteceu

Testamos o iter 009 da fila Tier 0b: **HAA SmartStack (iter 005 WINNER) + 5% GLDSIM fixo**.
Resultado: **WINNER 90/100** — novo Pareto frontier, supersede iter 005.

## O que descobrimos

**A adição de 5% de ouro melhora marginalmente todas as métricas:**

| métrica | iter 009 (HAA+GLD) | iter 005 (HAA) | delta |
|---|---|---|---|
| Sharpe (edu) | 1.120 | 1.112 | +0.008 |
| Sharpe (vt_real) | 1.061 | 1.049 | +0.012 |
| MDD (vt_real) | 14.20% | 15.05% | **-0.85pp** |
| CAGR (edu) | 13.89% | 14.14% | -0.25pp |
| Gates | 7/7/7 | 7/7/7 | = |

**Por que funciona:**

O GLDSIM tem correlação ~0 com equity global e ~0.1 com bonds em períodos de stress.
Manter 5% de ouro fixo (não dependente do sinal HAA) fornece hedge persistente:
- No bear de 2022 (rate hikes): gold caiu menos que equity; buffer parcial de MDD
- No bear de 2008: gold subiu +5-10% enquanto equity caiu 50%+

O custo é -0.25pp CAGR na janela educacional — ouro cresce mais devagar que stacked
equity em bull markets.

**G3 nominal passa** (max_mdd 20.81% < 25%) — resultado mais limpo que iter 005.

## O que isso significa para o loop

4 WINNERs encontrados (iters 002, 004, 005, 009). O iter 009 é o novo Pareto frontier
de Sharpe e MDD. Gap para bestfolio (1.18 Sharpe) = 0.06 — reduzido de 0.07 mas
não fechado ainda.

Próximo: **iter 010 — VAA-G3 SmartStack** (substituir BNDSIM como 4° ativo ofensivo
por equity puro — testa se bond contamination era a única fraqueza do iter 006).

## Contexto do projeto

Mandate §1 MAINTENANCE 100% Plano C continua ativo. Os 4 winners encontrados
(iters 002, 004, 005, 009) são candidatos, não deployments. Override §7 necessário
para qualquer uso real.
