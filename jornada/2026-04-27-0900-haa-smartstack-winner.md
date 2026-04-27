# HAA SmartStack — Nova Fronteira Pareto (Iter 005)

Iteração 005 do Global Factor-Tilt Loop encontrou um novo vencedor — e o melhor até agora.

## O que aconteceu

Testamos a estratégia HAA SmartStack: Hybrid Asset Allocation (Keller & Keuning 2023)
aplicada sobre um universo de ETFs "empilhados" (stacked), com um sleeve fixo de 10%
em futuros gerenciados (KMLM).

A ideia central: um ativo "canário" (mercados emergentes / VWOSIM) decide todo mês se
o portfólio entra em modo ofensivo ou defensivo.

- **Modo ofensivo (canário positivo)**: top-2 ETFs empilhados (cada um com 1.5× de
  notional — ações + bonds juntos num único instrumento), 45% cada + 10% KMLM.
- **Modo defensivo (canário negativo)**: melhor bond/cash defensivo a 90% + 10% KMLM.

O resultado em 31 anos de dados sintéticos (1995–2026):

| | Sharpe | CAGR | MDD |
|---|---|---|---|
| HAA SmartStack | **1.11** | **14.14%** | **20.91%** |
| Plano C V3_1 (referência) | 0.671 | 10.94% | 52.43% |
| V_HYBRID+MF (referência) | 0.743 | 10.91% | 44.71% |
| VT buy-and-hold | 0.55 | 8.64% | 58.35% |

7/7 gates em todos os 3 conjuntos de dados. 26/26 janelas de 5 anos com Sharpe positivo.

## Por que é relevante

A estratégia é melhor em **todas as três dimensões simultaneamente** comparada às três
referências mandatárias — dominância Pareto clara. A diferença mais impressionante é o
MDD: 20.91% vs 52-58% das referências passivas. O mecanismo do canário protege
efetivamente nas crises de 2008, 2020 e 2022.

Em comparação com a referência externa (bestfolio.app HAA SmartStack, Sharpe 1.18),
estamos apenas 0.07 Sharpe abaixo — a arquitetura está validada.

## Status e próximos passos

Mandato §1 MANUTENÇÃO ainda em vigor — este resultado é um candidato a override §7,
não um deploy automático.

Próxima iteração (006): VAA-G4 SmartStack — o mesmo universo empilhado, mas com
sinal de "breadth momentum" em vez de canário único. Testa se a abordagem mais
agressiva do VAA supera o HAA.
