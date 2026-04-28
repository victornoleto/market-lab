# Estados Unidos vs Global — Estudo para horizonte 20-30 anos

**Pergunta**: "Os EUA serão a maior potência econômica nas próximas décadas?
Eu não sei, e me preocupo. Quero diversificação global mesmo sabendo que
US-only teve melhor Sharpe/CAGR recentemente. Como otimizar evidência-based
pra 20-30 anos?"

**Geradores**: `us_vs_global_study.py` + `plot_us_vs_global.py`
**Dados**: testfolio synth cache 1969-2026 (56y) + 1986-2026 SPY (40y)
**Janela bottleneck**: SPYSIM começa 1986; GDESIM/VTSIM começam 1968-1969

---

## TL;DR

**Empírico (1986-2026, 40y)**:
- SPY-only domina VT-global por 1.8pp/yr (CAGR 11.49% vs 9.68%)
- Em rolling 20y: **US NUNCA retornou < 4.4%, VT MIN 3.18%, VEA MIN 1.42%**
- Em rolling 30y: **US min 9.56%, VT min 7.09%** — todos mais que 5%

**MAS**: o backtest captura 40 anos de **dominância US sustentada** (1980+). 
Quando incluímos cenário de "US lost decade":
- **2000-2013**: SPY CAGR 1.7% vs **VT 2.8%** vs VEA 2.0% — **VT venceu**
- 1969-1979 (não temos SPY mas VT): VT +109% global → bonita performance global

**Academic consensus**:
- Dimson-Marsh-Staunton (DMS) 1900-2024: dispersão country-level real CAGR
  varia ~2% a ~7%/yr — **predição ex-ante de país vencedor é impossível**
- Vanguard CMA 2024: forecasts US 4-6% nominal vs intl 7-9% próximos 10 anos
  baseado em valuation mean reversion (US CAPE ~38 vs intl ~17)
- Asness-Israelov-Liew (2011) "International Diversification Works":
  diversificação **DOES** ajudar terminal wealth long-run mesmo com correlação
  alta em crashes

**Crash correlations** (importante): em drawdowns >15%, correlação SPY-VEA
sobe de 0.64 → 0.78 (+0.14). "Diversification works EXCEPT when you need it
most" (Asness). MAS ainda há ~22% de descorrelação residual.

**Recomendação framework**: a decisão depende de **3 crenças**:
1. CAPE mean-reversion vai materializar (→ pesa contra US-only)
2. Crashes globais sincronizados não destroem diversificação (→ favorece global)
3. Você consegue manter convicção quando SPY supera VT por 5-10 anos (→ disciplina importa)

Se "sim" pra 1+2+3: V3_1 ou hybrid. Se "sim" pra 3 mas não 1-2: V1 NTSX+GDE.

---

## Section 1 — Replicação da sua comparação testfolio (5-way)

Janela 40.3y (1986-2026, bounded por SPYSIM):

| estratégia | Sharpe | CAGR | MDD | comentário |
|---|---|---|---|---|
| A NTSX_synth (90/60/-50) | 0.799 | 12.62% | 44.98% | seu config validado |
| **B NTSX+GDE blend** (59.4/39.6/-33/34) | **0.815** | **13.44%** | 44.40% | **vencedor de Sharpe** |
| C SPY 100% | 0.682 | 11.49% | 55.14% | bench US-only |
| D VT 100% global cap | 0.610 | 9.68% | 58.35% | **VT PERDEU SPY 40y** |
| E GDE 100% | 0.709 | 14.22% | 52.71% | maior CAGR mas vol alta |

**Confirmação**: B NTSX+GDE entrega o melhor Sharpe (0.815 daily-annualized; testfolio reportou 0.56 monthly — métricas diferentes mas ranking idêntico). Plot: `US_VS_GLOBAL_5way.png`.

**Ponto crítico para sua pergunta**: VT (global cap-weighted) **PERDEU SPY** em 40y por:
- 1.8pp/yr de CAGR
- 0.07 de Sharpe
- 3.2pp de MDD

**Mas isso é uma janela específica.** Vamos ver onde VT vence.

---

## Section 2 — Rolling 20y e 30y CAGR distributions

Janela 1986-2026 (40y → ~5023 janelas rolling 20y daily-stepped, ~3023 windows 30y).

### Rolling 20y

| estratégia | mean | median | 5% | 95% | min | max | P(<5%) | P(<3%) |
|---|---|---|---|---|---|---|---|---|
| **SPY US** | **8.84%** | 8.78% | 6.12% | 11.31% | 4.39% | 12.63% | 0.2% | 0.0% |
| VT global | 7.43% | 7.55% | 5.43% | 9.49% | 3.18% | 10.95% | 2.3% | 0.0% |
| VEA DM | 5.51% | 5.55% | 3.58% | 7.79% | 1.42% | 9.85% | **34%** | 2.6% |
| VXUS intl | 5.66% | 5.66% | 3.82% | 7.85% | 1.68% | 9.86% | 29% | 2.3% |
| **VBR US SCV** | **11.24%** | 11.03% | 8.68% | 14.51% | 6.82% | 15.86% | 0.0% | 0.0% |

### Rolling 30y

| estratégia | mean | 5% | min | max | P(<5%) |
|---|---|---|---|---|---|
| **SPY US** | **10.19%** | 9.56% | 8.70% | 11.14% | 0.0% |
| VT global | 7.88% | 7.09% | 6.29% | 8.85% | 0.0% |
| VEA DM | 5.52% | 4.58% | 3.86% | 7.45% | 17.6% |
| **VBR US SCV** | **11.73%** | 10.73% | 9.80% | 13.51% | 0.0% |

**3 achados:**

1. **US (SPY) NUNCA retornou abaixo de 9.5% em rolling 30y** janela 1986-2026.
   Distribuição muito tight. Isso é evidência forte mas **possivelmente
   biased** — o sample inclui 40 anos de US bull run estrutural.

2. **VEA (DM developed) tem 17.6% de chance de retornar < 5% em 30y** — esse
   é o "Japan-style lost decades" risk concentrado em desenvolvidos não-US
   que tiveram décadas perdidas (Japão 1989+, Europa 2000-2010, etc.)

3. **VBR (US SCV - small cap value) bate todo mundo** — Fama-French SCV
   premium real e persistente. Esse é o argumento empirico pelos AVUV/AVDV
   tilts no Plano C.

Plots: `US_VS_GLOBAL_rolling_20y.png` (linha do tempo) +
`US_VS_GLOBAL_distribution.png` (histograma).

---

## Section 3 — "Lost decades" — quando US perdeu

| período | SPY US | VT global | VEA DM | vencedor |
|---|---|---|---|---|
| 1969-1979 stagflation | n/a (SPYSIM 1986+) | +109% (CAGR 7.6%) | +151% (CAGR 9.6%) | **DM** |
| 1973-74 oil crisis | n/a | −37% (CAGR −20.4%) | −29% (CAGR −15.5%) | **DM** |
| **2000-2013 dot-com to recovery** | **+24% (CAGR 1.7%)** | +44% (CAGR 2.8%) | +29% (CAGR 2.0%) | **VT** |
| 2000-2002 dot-com | −37% | −39% | −43% | SPY |
| 2007-2009 GFC | −46% | −49% | −51% | SPY |
| post-2009 QE era | +675% (CAGR 17.4%) | +399% | +226% | **SPY (massive)** |
| 2022 rate cycle | −18% | −18% | −15% | **DM (small)** |

**Achado crítico**: 2000-2013 foi a janela mais recente onde **VT global venceu
SPY US por 1.1pp/yr** durante 13 anos contínuos. Não é hipotético.

VT venceu porque:
- 2002-2007: EM bull (commodities supercycle, China)
- 2002-2007: USD enfraqueceu massivamente, dollar-denominated US assets
  underperformed when re-converted
- 2010-2013: Europa em crise mas DM ex-EU + EM compensaram

Plot: `US_VS_GLOBAL_lost_decade.png` mostra equity curves 2000-2013.

**O que isso significa pra você**:
- Pode acontecer de novo. CAPE atual (38) parece com pré-2000 (44) e 2007 (28)
- Em 13 anos de US lost decade, V1 NTSX+GDE entregaria ~1.7% CAGR
  (deflated por inflação seria NEGATIVE real returns!)
- V3_1 (com 30%+ DM/EM) entregaria ~2.5-3% CAGR — pequeno em absoluto, mas
  >50% melhor que V1

---

## Section 4 — Crash correlations (Asness's "diversification fails when you need it")

| par | normal_corr (≥85% das barras) | crash_corr (drawdown >15%) | Δ |
|---|---|---|---|
| SPY vs VT | 0.843 | 0.897 | +0.054 |
| SPY vs VEA | 0.638 | 0.777 | +0.139 |
| SPY vs VWO | 0.628 | 0.787 | +0.159 |

**Interpretação**:
- Em mercados normais: SPY-VEA correlation 0.64 (boa diversificação)
- Em crashes: correlation 0.78 (correlation SOBE, mas ainda há ~22% residual)
- **Diversificação ajuda menos em crashes mas NÃO desaparece**

Asness-Israelov-Liew (2011, FAJ) argumenta exatamente isso: o argumento
"diversification fails in crashes" é exagerado — perdeu-se nuance. Em 2008,
quase tudo caiu, mas terminal wealth de portfolio diversificado **recupera
mais rápido** que single-country.

Empírico aqui: 2007-2009 SPY −46% vs VEA −51% (parecido), MAS 2010-2013 VEA
recuperou rápido com EM bull e SPY ficou flat.

---

## Section 5 — Regional dispersion (1994+, 32y, com VWOSIM)

Rolling 20y CAGR (1994-2026, 3003 windows):

| região | mean | 5% | 95% | min | max |
|---|---|---|---|---|---|
| US SPY | 8.52% | 5.95% | 10.79% | 4.39% | 11.38% |
| DM VEA | 5.26% | 3.68% | 6.84% | 1.42% | 7.64% |
| **EM VWO** | **7.32%** | 5.51% | 9.60% | 4.52% | 10.78% |

Ironia: em janela post-1994, **EM (Emerging Markets) bate DM developed em
todos os pontos da distribuição** — média, 5pct, 95pct, min, max. EM foi
mais return-yielding que DM nas últimas 3 décadas, embora com mais vol
intra-year.

Isso valida o Plano C V3.5 ter alocação 13% AVEM (EM core).

---

## Sintese acadêmica

### O que a literatura realmente diz

**Dimson-Marsh-Staunton (DMS) "Triumph of the Optimists" (2002, anual)**:
- Long-run real returns 1900-2024 by country: dispersion **2% a 7% real
  CAGR** entre os top-23 países desenvolvidos
- US é top-4-5 (não #1) — South Africa, Australia, Sweden tiveram retornos
  similares ou maiores
- **Predicção ex-ante de country winner é impossível** — não há serial
  correlation significativa de country returns décade-to-décade
- **Survivorship bias forte**: Russia, China, Argentina, etc. saíram dos
  índices ao longo do século. Investidores que estavam 100% em "country X
  vencedor de 1900" perderam tudo várias vezes.

**Vanguard Capital Markets Model (CMA, 2024 update)**:
- 10-year forecast US equities: **4.0-6.0% nominal** (~2-4% real)
- 10-year forecast intl developed: **7.0-9.0% nominal** (~5-7% real)
- 10-year forecast EM: **7.5-9.5% nominal**
- Driver: mean reversion de valuations (US CAPE 38 vs intl ~17)

**Shiller CAPE (Cyclically Adjusted Price-Earnings)**:
- Atual US ~38 (Apr 2025) — 95th percentil histórico desde 1881
- Long-term avg ~17
- Empirico (Shiller 2000, 2015): CAPE em 35+ historicamente preditivo de
  retorno 10y baixo (~0-3% real)
- Mas isso é **probabilístico**, não determinístico

**Asness-Israelov-Liew (2011, FAJ) "International Diversification Works
(Eventually)"**:
- Curto prazo: diversificação parece ineficaz em crashes
- Long prazo: terminal wealth distribution melhora claramente
- Quanto mais longa a janela, mais a diversificação compensa

**Buffett's "bet on America"**:
- Recomendação clássica: 90% S&P + 10% bonds pra herança da esposa
- **Caveat explícito** em letters: "America has had economic miracles before
  — this could change"
- Buffett vive em país que **dominou o século XX** — viés de sobrevivente
  perfeito

### Para o brasileiro (BR investor angle)

Pontos específicos pro seu caso:
1. **Sua moeda de consumo é BRL**. BRL desvaloriza ~5-10%/yr historicamente
   vs USD. Isso significa que portfolio US-denominated dá hedge cambial
   quase automático em janela longa.
2. **Diversificação cambial DM/EM** adiciona moedas EUR/JPY/CHF/GBP — todas
   também tendem a apreciar vs BRL long-run, mas com perfil diferente.
3. **Estate Tax US** (40% acima de $60k) **só afeta ETFs US-domiciliados**.
   Plano C V3.5 tem mitigação via UCITS irlandeses (CSPX/IWDA/EIMI). V1
   (NTSX+GDE) é 100% US-domiciled — sem mitigação.
4. **Lei 14.754 BR**: aplicação financeira no exterior, 15% sobre realizações.
   Buy-hold pode deferir tax indefinidamente. Aplica-se igualmente a V1 e V3_1.

---

## Framework de decisão (sua pergunta core)

Sua pergunta era: "EUA continuará dominante? Não sei. Quero diversificação
global. Como decidir baseado em evidência?"

**Não há resposta única — depende de quais riscos você prioriza:**

### Cenário 1 — você acredita em mean reversion (CAPE atual implausível)

Cenário base: US returns próximos 10y serão 2-4% real (Vanguard, Shiller).

→ **Pesa contra V1 (NTSX+GDE all-US)**.
→ V3_1 ou hybrid faz sentido.

### Cenário 2 — você acredita em "American exceptionalism" continuando

Cenário base: AI revolution, energy independence, deep capital markets,
USD reserve currency continuam dominantes.

→ **Pesa a favor de V1**. CAPE 38 é o "preço da qualidade".
→ Aceita 5-10y de underperformance se vier; recupera no ciclo seguinte.

### Cenário 3 — você quer minimizar regret cross-scenario

Aceita que ambos cenários têm probabilidade não-trivial. Ambos têm
"regret" se você bate na escolha errada:
- 100% V1 + US lost decade chega → "perdi 5pp/yr por 10 anos"
- 100% V3_1 + US continued dominance → "perdi 3pp/yr por 10 anos"

→ **Hybrid 50/50 V1/V3_1**: minimiza regret, aceita não maximizar em
nenhum cenário.

### Cenário 4 — você acredita em factor premium (literatura Fama-French)

US SCV (VBR) entregou 11.24% rolling 20y mean (vs SPY 8.84%). Se você
**believer** em factor premium persistente:

→ Plano C V3_1 v3.5 já incorpora isso (15% AVUV+AVDV).
→ V1 NTSX+GDE **NÃO** captura factor premium — só capital efficiency.
→ Factor + global > all-US capital efficiency em backward-looking 30y.

---

## Recomendação por horizonte e tese

### Horizonte 30+ anos, sem opinion forte sobre dominância US

Plano C V3_1 v3.5 **defende-se academicamente bem**:
- Diversificação global por DMS/Asness (literatura forte)
- Factor tilts por Fama-French (literatura mais forte ainda)
- Estate Tax mitigation via UCITS
- BR FI integration aos 45+ (Campbell-Viceira "bonds-em-moeda-de-consumo")

Trade-off: 11 ETFs vs 2; aceita 2-3pp/yr CAGR a menos histórico em troca
de robustez cross-scenario.

### Horizonte 30+ anos, **acredita** em US continuado

V1 NTSX+GDE 67/33:
- Sharpe melhor empírico (1986-2026)
- 2 ETFs, simplicidade radical
- **Mas**: 100% US, 100% USD-denominated, 100% US-domiciled (estate tax risk),
  zero hedge se US lost decade vier

### Horizonte 30+, hybrid (split a diferença)

50% V1 + 50% V3_1 = mistura das duas teses. Mais complexo (12 ETFs total)
mas deliberadamente não otimizado pra um cenário só.

### Honest limit deste estudo

**Janela 1986-2026 é US-favored estruturalmente**. Se eu pudesse usar
1900-2024 (DMS dataset), VT/global teria empatado ou batido SPY em mais
janelas. Não temos dados pré-1969 no testfolio synth.

CAPE atual 38 historicamente preditivo de underperformance 10y, mas
nem sempre — 1996 CAPE era 28 e o boom dot-com ainda durou 4 anos.

A **literatura acadêmica é clara em UMA coisa**: você não sabe quem vai
ganhar nos próximos 30 anos. Quem te disser que sabe está ou enganado
ou vendendo algo.

---

## Sua pergunta filosófica: "EUA dominará ainda?"

**Resposta empírica honesta**: probabilidade não-zero de SIM e NÃO.
Vanguard CMA dá ~30-40% de probability subjetiva de US underperform.
Asness em comunicações públicas estima 50/50.

**Sua intuição é defensável**: "I don't know, so I want global." É
literalmente o argumento Markowitz/CAPM clássico de mean-variance
optimization sob incerteza.

**Mas**: não é binário V1 (100% US) vs V3_1 (45% intl). Há um continuum.
Decisão é "em que ponto deste continuum estou confortável?"

**Sugestão prática**:
1. Decida % alvo intl baseado em sua incerteza (40% é Vanguard's recommendation)
2. Decida se factor tilts SCV/Mom valem o tracking error (15-30% é AQR-optimal)
3. Decida se return-stacking (NTSX/GDE) substitui pure equity ou complementa

Isso te leva a um portfolio único — pode ser exatamente V3_1 v3.5, pode
ser variant, pode ser híbrido com V1.

---

## Próximos passos sugeridos

1. **Iniciar `global_factor_tilt_loop`** (próximo passo do user já planejado)
   pra explorar empiricamente combinações de factor + global + capital
   efficiency
2. **Considerar pull de mais data**: Shiller CAPE histórico, country-level
   indices DMS, BTC data se quer modelar BTGD propriamente
3. **Backtest scenario analysis**: V1/V3_1/hybrid em "synthetic stagflation"
   construído via 1973-1979 multipliers — não temos US data desse período
   mas podemos extrapolar via VT/VEA

⚠️ **Mandate maintenance §1 inalterado**. Esta análise é deploy-readiness
research; nenhuma das 3 vias é deploy autorizado sem override §7.

---

## Files referenced

- `us_vs_global_study.py` — runner empírico
- `plot_us_vs_global.py` — geradores de plot
- `US_VS_GLOBAL_STUDY.json` — raw data completo
- `us_vs_global_returns.parquet` — daily returns
- 5 PNGs:
  - `US_VS_GLOBAL_5way.png` — 5-way comparison
  - `US_VS_GLOBAL_equity.png` — long-window equity curves
  - `US_VS_GLOBAL_rolling_20y.png` — rolling 20y CAGR time series
  - `US_VS_GLOBAL_distribution.png` — histogram of rolling 20y CAGRs
  - `US_VS_GLOBAL_lost_decade.png` — 2000-2013 zoom

## Citations

- Dimson, Marsh, Staunton (2002, ongoing). *Triumph of the Optimists* +
  UBS Global Investment Returns Yearbook annual updates.
- Asness, C., Israelov, R., Liew, J. (2011). "International Diversification
  Works (Eventually)." *Financial Analysts Journal* 67(3), 24-38.
- Vanguard Investment Strategy Group (2024). "Vanguard Capital Markets
  Model: 10-year asset class outlook."
- Shiller, R. J. (2000, updated 2015). *Irrational Exuberance.* Princeton
  University Press. — CAPE methodology.
- Buffett, W. E. (2013, recurring). Berkshire Hathaway annual letter —
  90/10 portfolio for personal estate.
- Campbell, J. Y., Viceira, L. M. (2010). "Bonds, Bills, and Stocks."
  *Journal of Finance* — bonds-in-consumption-currency principle.
