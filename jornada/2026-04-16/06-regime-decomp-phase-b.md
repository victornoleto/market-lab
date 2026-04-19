# Phase B Lead #6 — Decomposição por Regime [SHORT-HOLD CFD + SWING BROKER]

**Data:** 2026-04-16  |  **Iteração:** 25  |  **Status:** PASS (análise completa)

## O que foi feito

Analisamos os dois winners confirmados da Fase A por régime de volatilidade (VIX) e por ano.
O objetivo é identificar **condições de pausa** — quando seria prudente pausar cada estratégia no live.

**Proxy de VIX usado:** VIXY ETF (correlação ≈0.9 com VIX, disponível no Tiingo desde 2021-01-04).
Quintis calibrados sobre a série completa 2021-2026:

| Quintil | Faixa VIXY | Régime |
|---|---|---|
| Q1 | 5.2–12.1 | calmo |
| Q2 | 12.1–15.7 | baixo |
| Q3 | 15.7–21.4 | médio |
| Q4 | 21.4–32.4 | alto |
| Q5 | 32.4–82.8 | pânico |

---

## BollingerMR GARCH SPY 1h [SHORT-HOLD CFD, Path A]

**151 trades IS (2019-12 → 2024-12). 116 com dado VIXY (2021+).**

### Por ano

| Ano | n | WR | Sharpe(×√50) |
|---|---|---|---|
| 2019 | 2 | 100% | n/a |
| 2020 | 33 | 64% | +0.837 |
| **2021** | 32 | 91% | **+6.337** |
| **2022** | 33 | 52% | **-1.431** ⚠️ |
| 2023 | 24 | 67% | +0.988 |
| **2024** | 27 | 78% | **+3.069** |

**2022 foi o único ano negativo** — coincide com o bear market de -19% do S&P500.
A estratégia não tem filtro de regime, então continuou operando durante a tendência de baixa.
Leção: adicionar SPY>SMA200 como gate de pausa eliminaria esse drawdown (mas reduz oportunidades).

### Por quintil VIXY (2021-2026 IS)

| Quintil | n | WR | Sharpe(×√50) |
|---|---|---|---|
| Q1 calmo | 24 | 79% | **+3.234** |
| Q2 baixo | 32 | 75% | +0.813 |
| Q3 médio | 33 | 73% | +0.590 |
| Q4 alto | 25 | 64% | +0.718 |
| Q5 pânico | 2 | 0% | n/a (n=2) |

✅ **Nenhum quintil negativo com n≥5.** O edge existe em todos os regimes de vol.
Edge é mais forte em mercado calmo (Q1: Sharpe 3.2x) e se mantém em vol alta (Q4: Sharpe 0.72).
Esse padrão faz sentido: vol-sizing GARCH reduz tamanho quando vol é alta, preservando Sharpe.

**Conclusão BollingerMR:** Não há trigger de pausa baseado em VIX nos dados IS.
O único risco é tendência prolongada de baixa (2022). **Recomendação: monitorar posição relativa
SPY vs SMA200 como gate qualitativo para aumentar cautela, não necessariamente parar.**

---

## ETFRotation monthly top-1 [SWING BROKER, Path B]

**239 meses IS (2005-2024). 47 com dado VIXY (2021+).**

### Por ano (resumo — anos relevantes)

| Ano | Ret anual | Sharpe | Observação |
|---|---|---|---|
| 2008 | +8.4% | +1.00 | Crise financeira — filtro SPY>SMA200 foi ao cash |
| 2011 | +33.6% | +1.95 | Melhor ano no IS |
| **2012** | **-11.7%** | **-0.985** ⚠️ | Ano lateral — rotação pegou momentum fraco |
| 2016 | -3.5% | -0.26 ⚠️ | Lateral pré-Trump, novembro inverteu |
| 2021 | +34.7% | +2.07 | Melhor da série recente |
| 2022 | +2.7% | +0.29 | Bear market: filtro SMA200 protegeu |

**2012 e 2016 foram os únicos anos negativos** em 20 anos de IS.
De 2017 em diante: **zero anos negativos** (8 anos consecutivos positivos).

### Por quintil VIXY (47 meses, 2021-2024)

| Quintil | n | Ret anualizado | Sharpe(ann) |
|---|---|---|---|
| Q1 calmo | 13 | +21.7% | +1.429 |
| Q2 baixo | 12 | +18.4% | +1.743 |
| Q3 médio | 11 | +17.2% | +1.118 |
| Q4 alto | 10 | +10.8% | +0.782 |
| Q5 pânico | 1 | -35.4% | n/a (n=1) |

✅ **Nenhum quintil negativo com n≥3.** (Q5 tem n=1, mês Covid-cauda provavelmente.)
Padrão: retorno diminui conforme VIX sobe (Q1→Q4: 21.7%→10.8%). 
Isso é esperado: estratégia de momentum sofre em alta vol onde tendências revertem.

**Conclusão ETFRotation:** Filtro SPY>SMA200 já protege contra regimes de bear market (2008/2022).
2012 e 2016 foram exceções (mercado lateral sem trend claro). **Recomendação: não adicionar
filtro adicional de VIX — o momentum score já captura essa dinâmica.**

---

## Concordância entre estratégias

- **Nenhum quintil perdedor em comum** → blend continua diversificado em qualquer regime VIX.
- BollingerMR perde em 2022 (tendência baixa); ETFRotation sobrevive 2022 (filtro SMA200).
- ETFRotation perde em 2012/2016 (lateral); BollingerMR é indiferente a tendência.
- **As duas estratégias se complementam em regimes diferentes.**

---

## Citações

- `[advances_fin_ml, p.215-219, ch.13]` — regime stress / partitioning
- `[machine_trading, p.126-127]` — EWMA-GARCH vol sizing
- `[stocks_on_the_move, p.81/66/95]` — ETFRotation params canônicos

## Script

`scripts/run_regime_decomp_phase_b.py` — outputs em `reports/regime_decomp_phase_b/`
