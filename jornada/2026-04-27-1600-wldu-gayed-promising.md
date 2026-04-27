# Global Factor-Tilt Loop — Iter 008: WLDU+Gayed PROMISING (61/100) + Dead End Documentado

## O que aconteceu

Testamos a hipótese do iter 008 da fila pre-committed: **WLDU + Gayed 200d SMA**, estratégia
de LETF 2× em equity global (VTSIM×2) com filtro de tendência (SMA de 200 dias no S&P 500).
Resultado: **PROMISING 61/100 — não chega a STRONG, não é winner**.

## O que descobrimos

**O problema central é estrutural, não paramétrico:**

Gayed (2021) mostrou que seu filtro de tendência melhora o Sharpe do S&P 500 de 0,32 para 0,61.
Mas o VTSIM (equity global diversificada) já tem Sharpe de 0,61 por conta da diversificação
entre países. Aplicar 2× leverage com filtro binário dobra tanto retorno quanto volatilidade
proporcionalmente → Sharpe fica flat (0,61 → 0,61). Zero melhoria possível.

**Números do backtest (window educacional ~40 anos):**

| métrica | WLDU+Gayed | VTSIM b&h | HAA WINNER |
|---|---|---|---|
| Sharpe | 0,609 | 0,610 | 1,112 |
| CAGR | 12,69% | 9,65% | 14,14% |
| MDD | 44,45% | 58,35% | 20,91% |

Melhora CAGR (+3pp) e MDD (-14pp) vs buy-and-hold simples, mas é dominado pelo HAA em todas
as três dimensões.

**Kill criterion 2 ativado**: MDD=44,45% > 35% (threshold de LETF). O bear market de 2022
foi gradual (rate hikes); o filtro mensal só saiu em março 2022, mas o WLDU a 2× já tinha
absorvido 10-12% em janeiro-fevereiro.

## O que isso significa para o loop

Fechamos a branch "LETF + filtro de tendência binário em equity global". Isso está documentado
como dead-end DE-001 em `DEAD_ENDS.md`. A direção não está morta para equity concentrada
(S&P 500 ou VTISIM com Sharpe base 0,33), apenas para equity global diversificada.

A fila pre-committed estava com 4 hipóteses (iter 005-008). Todas as 4 foram executadas.
**O vencedor da fila é o iter 005 (HAA SmartStack, WINNER 90)**, que continua sendo o
Pareto frontier da busca.

## Próximos passos

O loop entra agora em "exploração livre" pós-fila. Dois candidatos mais promissores:

1. **HAA + sleeve de 5% gold** (iter 009): testar se adicionar GLDSIM fecha o gap de 0,07
   Sharpe até o bestfolio de referência (1,18 vs 1,112 atual)
2. **VAA-G3 SmartStack** (iter 010): substituir o BNDSIM como 4ª ofensiva por equity puro
   — testa se o bond contamination era a única fraqueza do iter 006

## Contexto do projeto

Mandate §1 MAINTENANCE 100% Plano C continua ativo. Os 3 winners encontrados (iters 002, 004,
005) são candidatos, não deployments. Override §7 necessário para qualquer uso real.
