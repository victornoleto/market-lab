# D4 — Absolute Momentum (Antonacci) — TQQQ+GLD — DEAD END [SWING BROKER]

**Data:** 2026-04-21 | **Iter:** 8 | **Veredicto:** DEAD END (0/6 PASS)

## O que testamos

Implementamos o filtro de **absolute momentum** de Antonacci
`[antonacci_dual_momentum, p.62]`: no fim de cada mês, se o retorno
acumulado dos últimos N meses do ticker de sinal (QQQ ou TQQQ) for
positivo, ficamos em TQQQ; caso contrário, vamos para GLD.

6 configurações: 3 lookbacks (6, 9, 12 meses) × 2 tickers de sinal
(QQQ, TQQQ). Janela 2004-11-18 → 2026-04-15 (21.4 anos).

## Resultados

| Config     | LB   | Sinal | CAGR_net% | Sharpe_net | MaxDD%  | Calmar | WF  | PBO   | PASS |
|------------|------|-------|-----------|------------|---------|--------|-----|-------|------|
| mom12_qqq  | 12mo | QQQ   | 20.0%     | 0.565      | -69.9%  | 0.337  | 8/8 | 0.778 | ✗    |
| mom12_tqqq | 12mo | TQQQ  | 17.4%     | 0.532      | -79.3%  | 0.259  | 8/8 | 0.778 | ✗    |
| mom9_qqq   | 9mo  | QQQ   | 18.3%     | 0.545      | -69.9%  | 0.309  | 8/8 | 0.778 | ✗    |

SPY B&H net: 7.31% (batido por todas as configs). Gates que falham:
**PBO=0.778** (seleção de hiperparâmetro flagrada), **Sharpe_net < 0.800**,
**Calmar < 0.500**.

## Por que falhou

Duas razões fundamentais:

1. **Rebalanceamento mensal não protege intra-mês.** Em crashes violentos
   (março 2020, 2022), o TQQQ despenca -60-80% em semanas, mas o sinal
   mensal ainda marca "positivo" no último mês anterior. O MaxDD fica em
   -69.9% mesmo com o filtro — quase igual ao buy-and-hold de TQQQ.

2. **Sharpe inferior ao SMA200 diário.** O melhor resultado aqui foi
   Sharpe_net=0.565 vs D2 SMA200 best de 0.780. O SMA200 reage mais rápido
   a quebras de tendência porque é calculado diariamente; o momentum mensal
   é mais lento.

## Comparação com D2 (SMA200)

| Lead | Melhor config      | Sharpe | Sharpe_net | MaxDD  | Calmar |
|------|--------------------|--------|------------|--------|--------|
| D2   | TQQQ sma200_gld    | 0.918  | 0.780      | -60.3% | 0.608  |
| D4   | mom12_qqq          | 0.665  | 0.565      | -69.9% | 0.337  |

D4 é claramente inferior ao SMA200 em todas as métricas relevantes.

## Diagnóstico e próximo passo

A hipótese "momentum mensal captura regimes melhor que SMA200" foi
**refutada**. SMA200 diário permanece o melhor filtro encontrado até agora.

O gap até o gate de Sharpe_net=0.800 permanece: D2 estava a 0.020
(0.780 vs 0.800). Em vez de trocar o sinal, a abordagem D5 vai **combinar**
o SMA200 com **volatility targeting** (escalar a exposição ao TQQQ em vez de
on/off binário), que pode reduzir o MaxDD e melhorar o Calmar sem sacrificar
o Sharpe.

**Próximo:** D5 — Volatility Targeting `[advances_fin_ml, ch.14]`.

## Links

- Report: `reports/phase_3_5d/d4_dual_momentum_antonacci/TQQQ.md`
- JSON: `reports/phase_3_5d/d4_dual_momentum_antonacci/TQQQ.json`
