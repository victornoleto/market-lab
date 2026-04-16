# Cross-asset overlap dos winners — XLK e XLE são quase a mesma aposta

> ⚠️ **RETRACTED 2026-04-16 12:45.** Daily PnL correlations foram
> computadas em trades cuja PnL absoluta era 50-90% fake (placeholder
> bars em US holidays). A correlação entry-time (Jaccard) ainda é válida
> qualitativamente — entries em si estão certas, é só o PnL que está
> contaminado. Mas as conclusões de "XLK-XLE corr 0.83 → 1 edge" e os
> Sharpes daily-aggregated são ambos artefato. O script
> `run_trade_overlap_bollinger_mr.py` permanece válido — re-rodar com
> dados limpos quando algum strategy passar gate. Veja
> [2026-04-16-1245-data-bug-winners-retracted.md](2026-04-16-1245-data-bug-winners-retracted.md).


**Verdict:** Não temos 3 edges independentes — temos **~2**. XLK-XLE
correlação diária de PnL = **0.83** (acima do threshold 0.7 do plan,
que ativa a regra "1 edge × 3 ativos"). SPY corre por outro fator
(corr SPY-XLK = 0.13, SPY-XLE = 0.08 — surpreendentemente baixos).

Equal-weight 3-asset Sharpe = **2.54** vs mean-of-3 = **2.30** — lift
de 10% (vs √3=1.73 teórico se fossem independentes). Modesto.

---

## Por que rodamos

Task 1B do plan. O bootstrap de 1A diz "cada winner individual passa o
gate pre-DSR", mas se SPY/XLK/XLE são facetas correlacionadas do mesmo
sinal, **portfolio diversification é ilusória** — 3 caminhos para o
mesmo blow-up. Critério: pair correlation > 0.7 ⇒ 1 edge×3 ativos.

## Métricas computadas

### Jaccard de entries (granularidade 1h)

| Par | Jaccard |
|---|---|
| SPY-XLK | 0.204 |
| SPY-XLE | 0.069 |
| XLK-XLE | 0.058 |

Interpretação: 0.204 = só 20% das barras-de-entrada de SPY-ou-XLK são
de **ambos**. As estratégias raramente firam no mesmo bar. Para SPY-XLE
e XLK-XLE, ainda menos sobreposição (~6-7%).

Conclusão isolada: pelas entries, não parecem altamente correlacionados.

### Correlação diária de PnL

|  | SPY | XLK | XLE |
|---|---|---|---|
| SPY | 1.000 | 0.128 | 0.076 |
| XLK | 0.128 | 1.000 | **0.825** |
| XLE | 0.076 | 0.825 | 1.000 |

**Três achados:**

1. **XLK-XLE = 0.825 > 0.7** — gatilho "1 edge ×N" ativado. Tech +
   energia compartilham regime macro (risk-on/off, dollar move,
   commodity beta cruza para tech via cap-ex de chip e etc.).
2. **SPY-XLK = 0.128** é baixíssimo, contra-intuitivo — SPY tem
   ~30% peso tech. Provável explicação: o strategy não fira nos
   mesmos dias para SPY vs sectors. Days where SPY trades but XLK
   doesn't ⇒ XLK daily PnL = 0, baixa o ρ.
3. **SPY-XLE = 0.076** é genuinamente baixo — broad market vs
   energy seguem dynamics diferentes (energy tem dependência forte
   em oil que não está no SPX core).

### N efetivo (participation ratio dos eigenvalues)

Eigenvalues de C (3×3): perfeitamente diagonal teria PR=3 (3 fatores
independentes); rank-1 (single common factor) teria PR=1.

**PR observado = 2.04** ⇒ na prática, ~2 dimensões de risco. Bate com
a leitura "SPY é um fator, XLK≈XLE é outro".

### Sharpe per-asset (daily-aggregated, OOS) vs portfolio

| | Sharpe (daily, ann. = √252) |
|---|---|
| SPY | 2.38 |
| XLK | 2.52 |
| XLE | 2.01 |
| **Mean of 3** | **2.30** |
| **Equal-weight portfolio** | **2.54** |

Diversification lift = 2.54 / 2.30 = **1.10**. Vs teórico max √3 =
1.73. Lift muito menor que o ideal, consistente com N_eff ≈ 2.

**Nota sobre Sharpe daily ≠ Sharpe trade-level:** este Sharpe é da
série diária de PnL, anualizado por √252. O bootstrap de 1A usou
Sharpe trade-level (~46 trades/ano, anualizado por √46). Os dois são
métricas válidas mas diferentes — daily Sharpe é maior porque agrega
intra-day vol away. Não há contradição.

## O que isso muda na narrativa

1. **"3 winners" pelo bootstrap → "~2 edges efetivos" pelo overlap.**
   XLK e XLE devem ser tratados como UM produto na construção de
   portfólio. Pegar os dois = alocação concentrada no mesmo fator.
2. **SPY genuinamente diversifica o sector pair.** Embora SPY OOS
   bootstrap (Task 1A) tenha o lower bound mais frágil, ele é
   ortogonal a XLK/XLE — drop SPY perde diversification real, não só
   redundância.
3. **Portfolio sweet spot = SPY + um (XLK OU XLE).** Não os 3 juntos.
   Estima-se Sharpe de portfolio 2-asset ≈ 2.5 (semelhante ao 3-asset
   atual), com 1/3 a menos de complexidade operacional.
4. **Implicação para Task 1G (production-readiness verdict):** não é
   3-asset deploy. Provavelmente 2-asset (SPY + XLK), ou single-asset
   XLK (que tem o melhor bootstrap CI individual) com peso pleno.
5. **Implicação para Task 1H (GARCH-sized variant):** se passar, é
   uma 3ª dimensão que pode reabrir o portfolio para 3 estratégias
   reais (Bollinger SPY + Bollinger XLK + GARCH-Bollinger XLK,
   por exemplo).

## Citações

- `[advances_fin_ml, p.40-44, ch.3]` — purged correlation discipline.
- `[systematic_trading, Carver, p.121-126, ch.7]` (não citado no
  script, mas relevante) — diversification benefits via correlation
  matrix; "uncorrelated >> highly-correlated" para mesmo SR target.

## Arquivos

- `scripts/run_trade_overlap_bollinger_mr.py`
- `reports/bollinger_mr_overlap/summary.md`
- `reports/bollinger_mr_overlap/overlap.json`
- `reports/bollinger_mr_overlap/assets/daily_pnl_corr.png`

## Próximo passo

Plan original: 1B → 1D (regime decomposition). Saber em quais regimes
de VIX cada um dos 3 quebra ajuda a entender SE XLK e XLE quebram em
regimes diferentes (resgatando alguma diversificação) ou no mesmo
regime (confirmando que são 1 fator).

Tests intactos: 515 verdes (script é stand-alone, não muda código
testado).
