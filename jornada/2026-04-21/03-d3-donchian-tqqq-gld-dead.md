# D3 Donchian Breakout TQQQ+GLD — Dead End (iter 7) [SWING BROKER]

**Data:** 2026-04-21 00:37

**Resultado:** 0/4 PASS

---

## O que foi testado

D3 testou uma abordagem completamente diferente da D2: em vez de um filtro de regime por média móvel,
usamos o clássico **Canal de Donchian** como sinal de entrada e saída.

A lógica é simples: comprar TQQQ quando o preço rompe para cima o máximo dos últimos N pregões;
vender para GLD quando o preço cai abaixo do mínimo dos últimos M pregões. A posição persiste
entre os sinais — uma espécie de "segue o momentum".

Testamos 4 pares de lookback: (20/10), (40/20), (60/30), (80/40).
Janela: 2004-11-18 → 2026-04-15 (21.4 anos, a mais longa disponível para TQQQ+GLD).

Citações: `[trading_systems_methods, p.353]` (Donchian), `[stocks_on_the_move, p.81]` (momentum timing).

---

## Resultados

| Config | CAGR líq% | Sharpe bruto | Sharpe líq | MaxDD% | Calmar | WF |
|--------|-----------|--------------|------------|--------|--------|----|
| dc20_10 | 20.3% | 0.795 | 0.676 | -47.2% | 0.507 | 7/8 |
| dc40_20 | 19.1% | 0.759 | 0.646 | -42.6% | 0.527 | 7/8 |
| dc60_30 | 11.8% | 0.542 | 0.461 | -54.8% | 0.253 | 8/8 |
| dc80_40 | 14.6% | 0.613 | 0.521 | -53.7% | 0.319 | 8/8 |

PBO = 0.107 (passa com folga). SPY líquido = 7.31% nesta janela (todos os configs vencem).

---

## Por que não passou

O gate mais restritivo é o **Sharpe líquido > 0.800**. O melhor config (dc20_10) tem Sharpe bruto 0.795 →
líquido 0.676. Para passar o gate, precisaríamos de Sharpe bruto ≥ 0.941.

O Donchian reduz bem o MaxDD: dc20_10 tem -47.2% vs -81.7% do TQQQ buy-hold. Mas corta demais o CAGR
(23.9% bruto vs 41.1% buy-hold) para gerar Sharpe suficiente. O SMA200 da D2 tinha Sharpe bruto 0.918 —
o Donchian ficou 0.795, ainda pior.

A raiz do problema é a mesma da D2: o imposto de 15% IR BR (Plano B) exige Sharpe bruto muito alto.
Um sistema que troca frequentemente ou que fica fora do mercado por muito tempo paga esse custo.
O dc20_10 ficou 48% do tempo no mercado — a metade do tempo em GLD, perdendo o rally do TQQQ.

---

## O que aprendemos

1. **Donchian < SMA200 em Sharpe bruto** nesta configuração (0.795 vs 0.918). A média móvel de longo prazo
   filtra o regime com maior precisão.
2. **Janela longa (21.4 anos) inclui a crise de 2008** onde TQQQ sintético teria sofrido muito. O Donchian
   saiu do mercado parte do tempo, mas o impacto na crise não foi suficiente para compensar o custo de oportunidade.
3. **O gargalo permanece**: gross Sharpe ≥ 0.941 é a barreira que nenhuma estratégia até agora alcançou.
   A D2 chegou mais perto (0.918).

---

## Próximo passo

D4 — Dual Momentum (Antonacci): sinal de 12 meses de momentum absoluto sobre TQQQ vs GLD.
Mensal ao invés de diário. Citação: `[antonacci_dual_momentum]`.
A hipótese é que um lookback mais longo pode capturar regimes multi-mensais e produzir Sharpe maior.
