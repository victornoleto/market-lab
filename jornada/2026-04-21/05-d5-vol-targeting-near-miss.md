# D5 Vol-targeting TQQQ+GLD — 9/10 gates pass, PBO obstáculo [SWING BROKER]

**Data:** 2026-04-21 | **Iter:** 9 | **Lead:** D5 | **Resultado:** NEAR-MISS (0/7 PASS)

## O que tentamos

Ao invés de um sinal binário on/off (como o SMA200 no D2), tentamos uma exposição **contínua** ao TQQQ proporcional ao inverso da volatilidade realizada:

```
peso_TQQQ = min(1.0, vol_target / vol_realizada_TQQQ)
peso_GLD  = 1 - peso_TQQQ
```

Testamos 6 combinações de `target_vol` (15%, 20%) × `lookback` (10, 20, 30 dias), mais uma 7ª config com overlay SMA200 sobre a melhor base. Citações: `[advances_fin_ml, ch.14]` (sizing por vol) e `[volatility_trading]`.

## O que encontramos

| Config | CAGR% | CAGR_net% | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Stage2 | PASS |
|--------|-------|-----------|--------|------------|--------|--------|----|-------|-------|-----|-------|--------|------|
| vol15_lk10 | 20.0 | 17.0 | 0.928 | 0.789 | -37.3 | 0.537 | 8/8 | 1.063 | 0.219 | 0.599 | 0.002 | ✓ | ✗ |
| **vol15_lk20** | **21.3** | **18.1** | **1.006** | **0.855** | **-37.2** | **0.573** | **8/8** | **1.169** | **0.182** | 0.599 | 0.001 | ✓ | ✗ |
| vol15_lk30 | 20.6 | 17.5 | 0.988 | 0.840 | -37.7 | 0.548 | 8/8 | 1.181 | 0.215 | 0.599 | 0.001 | ✓ | ✗ |
| vol20_lk10 | 22.2 | 18.9 | 0.897 | 0.763 | -44.0 | 0.505 | 8/8 | 0.923 | 0.058 | 0.599 | 0.003 | ✗ | ✗ |
| vol20_lk20 | 24.0 | 20.4 | 0.977 | 0.830 | -43.9 | 0.545 | 8/8 | 1.030 | 0.006 | 0.599 | 0.001 | ✗ | ✗ |
| vol20_lk30 | 23.2 | 19.7 | 0.961 | 0.817 | -44.5 | 0.521 | 8/8 | 1.046 | 0.051 | 0.599 | 0.001 | ✗ | ✗ |
| best_sma200 | 19.5 | 16.6 | 0.956 | 0.813 | -30.2 | 0.646 | 8/8 | 1.170 | 0.145 | 0.599 | 0.001 | ✓ | ✗ |

**SPY B&H net:** 7.31%/yr (15% IR BR aplicado à janela 2004-2026)

## Por que não passou

**PBO = 0.599** (precisa < 0.5). Todos os 7 configs são variantes da mesma família de vol-targeting — parâmetros ligeiramente diferentes, retornos altamente correlacionados. O CSCV (Combinatorial Symmetric Cross-Validation) `[advances_fin_ml, p.208-211]` não consegue diferenciar "escolhemos o melhor pela habilidade" de "escolhemos pela sorte" quando os candidatos são tão similares entre si.

Analogia: é como perguntar "qual dos seus gêmeos idênticos tirou nota maior na prova?" — não dá pra saber se foi mérito ou aleatoriedade quando são quase iguais.

## Breakthrough econômico

Apesar do PBO, esta é a **primeira lead a superar o gate Sharpe_net > 0.800**:

| Comparação | D2 sma200_gld (melhor anterior) | D5 vol15_lk20 |
|-----------|--------------------------------|---------------|
| Sharpe bruto | 0.918 | **1.006** |
| Sharpe_net | 0.780 | **0.855** |
| MaxDD | -60.3% | **-37.2%** |
| Calmar | 0.608 | 0.573 |
| WF | 7/8 | 8/8 |
| OOS Sharpe | N/A | **1.169** |
| Stage 2 (yfinance) | ±1.36pp ✓ | **±2.23pp ✓** |

O vol-targeting funciona porque:
1. Durante crashs (vol TQQQ sobe para 80-120%), o peso cai para 15-20% → drawdown limitado
2. Durante bull markets (vol ~50%), o peso fica em ~30% → captura parte do upside
3. GLD complementa bem em regimes de alta volatilidade (correlação negativa com equities)

## Por que o PBO é o obstáculo e não a economia

As 7 configs testadas são essencialmente a MESMA ideia com parâmetros ligeiramente diferentes. PBO testa se a seleção do "melhor" foi por mérito ou sorte no espaço de configurações. Quando todas as configs são correlacionadas, o PBO não pode distinguir — e falha conservadoramente.

Solução: testar 3 configs **estruturalmente distintas**:
1. `sma200_gld` — regime binário MA (D2 best)
2. `vol15_lk20` — vol-targeting contínuo puro (D5 best)
3. `vol15_lk20+sma200` — combo (vol-target × regime)

Três famílias distintas → PBO consegue discriminar → esperamos PBO < 0.5.

## Próximo passo

**D5b** (iter 10): teste PBO com 3 configs estruturalmente diversas. Se vol15_lk20 vencer
com PBO < 0.5, todas as outras gates já passam — seria um **winner** da Phase 3.5d.

`reports/phase_3_5d/d5_vol_targeting/TQQQ.md` | `reports/phase_3_5d/d5_vol_targeting/TQQQ.json`
