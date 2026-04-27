# Loop Global Factor Tilt — Fechamento: o híbrido vence tudo

## O que foi feito

O loop `global_factor_tilt_loop` foi encerrado após 12 iterações (10 de busca de estratégia +
2 de análise fiscal). O objetivo era encontrar UMA estratégia globalmente diversificada que
batesse VT buy-and-hold, o Plano C V3_1 v3.5 e o V_HYBRID+MF.

Iter 012 foi a última iteração: um portfólio híbrido 50/50 combinando:
- 50% HAA+Gold (estratégia ativa com canário, iter 009) → DARF mensal
- 50% Plano C V3_1 v3.5 proxy (passivo, factor equity global) → DARF só no resgate terminal

## Resultados do híbrido (líquido de impostos)

| Janela | Sharpe | CAGR | Drawdown máximo |
|---|---|---|---|
| Educacional (30.8y) | **1.021** | **13.38%** | 26.85% |
| VT real (16.8y) | **1.058** | **14.06%** | 19.36% |
| NDX real (15.1y) | **0.972** | **11.84%** | 19.20% |

## A descoberta inesperada

O híbrido não ficou no meio-termo entre HAA e Plano C. Ele **BATEU o HAA puro no Sharpe** em
todos os 3 datasets (+0.03 a +0.12 de diferença).

Motivo: diversificação HAA+PlanC com rebalanceamento anual captura o prêmio de dispersão. O
Plano C (estático, sem canário) tem correlação ~0.75 com o HAA (momentum canário). Quando o HAA
vai para defensivo (bear markets), o Plano C cai menos — mas mais do que o HAA defensivo. O
rebalanceamento anual compra o lado que caiu mais, gerando retorno extra.

Além disso, a metade Plano C difere o DARF para o resgate terminal, que é fiscalmente mais
eficiente do que pagar DARF mensalmente como o HAA puro faz.

## Tabela de decisão — mandato §7

| estratégia | Sharpe | CAGR líquido | MDD | DARF/ano | complexidade |
|---|---|---|---|---|---|
| **50/50 Híbrido** | **1.021** | **13.38%** | 26.85% | ~3 (metade HAA) | MÉDIO |
| 100% HAA+Gold | 0.991 | 12.13% | 21.83% | ~2.5 | ALTO |
| 100% Plano C | 0.631 | 10.31% | 52.43% | 1 (terminal) | ZERO |

O híbrido **domina o HAA puro em Sharpe** e domina o Plano C em tudo exceto complexidade.
O único custo: MDD sobe de 21.8% (HAA) para 26.9% (híbrido), e exige rebalanceamento mensal
na metade HAA.

## O que isso significa para o mandato §7

O usuario tem agora 3 opções concretas com números net-of-tax:

1. **Manter Plano C** (mandato atual §1): CAGR ~10.3%, MDD ~52%, zero complexidade operacional.
   Racional: preservação de energia cognitiva, simplicidade máxima, sem DARF mensal.

2. **Ativar 50/50 Híbrido**: CAGR ~13.4%, MDD ~27%, rebalanceamento mensal na metade HAA.
   Racional: melhor Sharpe que HAA puro, melhor CAGR que Plano C puro, complexidade moderada.

3. **Ativar 100% HAA+Gold**: CAGR ~12.1%, MDD ~22%, rebalanceamento mensal, menor drawdown.
   Racional: máxima proteção de capital, Sharpe alto, mas CAGR abaixo do híbrido.

## Status do loop

12 iterações concluídas. Iterações com score WINNER: 002, 004, 005, 009, 011. Fronteira bruta:
iter 009 (Sharpe 1.120). Fronteira líquida: iter 012 híbrido (Sharpe 1.021). Loop FROZEN.
