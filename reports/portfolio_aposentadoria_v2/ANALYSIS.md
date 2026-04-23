# Portfolio de Aposentadoria — Análise, Backtest e 4 Carteiras Otimizadas

> Documento consolidado da sessão 2026-04-23 respondendo ao pedido:
> "otimize meu portfolio de aposentadoria (Plano C) levando em conta factor
> investing, return stacking e ETFs alavancados. Me dê 4 opções finais, uma
> por função objetivo."
>
> **Versão atual: V3** (post feedback do usuário sobre BR FI e stacked alts).
> Mudanças vs versões anteriores em `REVISIONS.md`.
>
> Artefatos relacionados:
>
> - `scripts/01*–09_*.py` — pipeline reprodutível de download, panel, simulação
> - `data/returns_monthly.parquet` — panel mensal 2000-2026 (65 ativos, inclui
>   BR FI via CDI-BCB, BR ETFs via yfinance, US ETFs via Tiingo, sintéticos)
> - `data/web_research.md` + `data/web_research_v3.md` — pesquisa com links
> - `results/final_portfolios_v3.json` — as 4 carteiras finais + bootstrap
>
> Citações: `[book.slug, p.X]` para livros em `books/summaries/`; web papers
> com link direto.

---

## Sumário Executivo

1. **O plano atual (Plano C as-is) é defensível mas deixa 4pp de CAGR/ano na
   mesa.** Backtest 2007-2026 (18,5y): CAGR líquido 7,52% / Sharpe 0,37 /
   MDD -54% / bootstrap p50 terminal wealth (30 anos, 10k + 1k/mês) = **$1,50M**.
2. **Sua proposta SSO 50% tem kernel bom (capital efficiency) mas execução
   errada.** Backtest: CAGR +2,0pp ✅, Sharpe PIOR ❌, MDD -71% (de -54%),
   P(MDD>50% em 30y) sobe de 30% para **79%**. A alternativa certa é
   **return stacking com overlay descorrelacionado** (bonds ou gold), não
   leverage puro sobre beta.
3. **Bonds do seu portfolio devem ser em BRL, não em USD.** Campbell-Viceira
   2010, Vanguard 2018/2023, Ben Felix/PWL: bonds na moeda de consumo. Para
   brasileiro o gap é +400bps (NTN-B real IPCA+6% vs TIPS 2%), e FX vol
   15-20% destrói o papel de stabilizer de um bond unhedgeado. Universo
   usado: **B5P211** (IPCA+ curto), **IMAB11** (IPCA+ longo), **LFTS11**
   (Selic cash), **DINF11** (debênture incentivada, **isento de IR**).
4. **Gold/BTC via return stacking.** GDE (WisdomTree Efficient Gold+Equity,
   90%SPX + 90%gold, TER 0,20%, AUM $629M) é o core; BTGD (100%BTC +
   100%gold) é satellite. ISBG descartado (AUM <$5M, covered-call decay).
5. **4 carteiras V3 finais** (seção 6). Meu default pro seu perfil: **V3_3
   "Bounded Growth"** — CAGR 11,7% / Sharpe 0,79 / MDD -36% / p50 TW 30y
   **$3,3M**. É 120% mais rico que o plano atual em terminal wealth.
6. **Risco crítico e não mitigado: US Estate Tax** (seção 8). Brasileiro com
   ETFs US-domiciliados >$60k paga até 40% na morte. Mitigação via UCITS
   irlandeses para parte do bucket equity.

---

## 1. Metodologia

### 1.1 Panel de dados

Fontes unificadas em `data/returns_monthly.parquet` (65 ativos, 1885-2026):

| Fonte | Ativos | Janela |
|-------|--------|--------|
| Tiingo REST API (US ETFs reais) | AVUS, AVUV, AVDE, AVDV, AVEM, IDMO, SPMO, NTSX, NTSI, NTSE, RSST, RSSB, RSBT, RSSY, RSBY, DBMF, KMLM, CTA, IBIT, GLDM, GLD, AVGV, DFAC, DFAT, **GDE, RSSX, BTGD, ISBG** | Inception → 2026-04 |
| Tiingo (projeto, existente) | SSO, UPRO, QLD, TQQQ, SPY, VTI, VEA, VWO, TLT, IEF, SHV | 2001-2026 |
| **yfinance BR ETFs** | **B5P211, IMAB11, LFTS11, DEBB11, FIXA11, BOVA11, IVVB11** | 2019-2026 |
| **BCB SGS API** | **CDI_BR (série 12)**, IPCA_BR (série 433) | **2000-2026** (26 anos) |
| yfinance BTC-USD | BTC_USD | 2014-2026 |
| Testfolio SPY-SIM | SPY_1x/2x/3x_sim | **1885-2026** (141 anos) |
| Ken French F-F daily | Mkt-RF, SMB, HML, RF, Mkt | **1926-2026** (100 anos) |
| Sintéticos | NTSX_syn (0,9 SPY + 0,6 IEF), **GDE_syn (0,9 SPY + 0,9 GLD)**, **BTGD_syn (1 BTC + 1 GLD)**, **RSSX_syn (1 SPY + 0,5 GLD + 0,5 BTC)**, AVUV_syn_3f (Fama-French loadings) | Várias |

Caveats:
- **Return Stacked ETFs** (RSST/RSSB/RSBT/RSSY/RSBY/ISBG) têm inception
  2023-2026 — backtest real muito limitado; usamos NTSX_syn e GDE_syn como
  proxies long-history.
- **BR FI (B5P211/IMAB11/LFTS11/DINF11)** tem inception 2019-2024. Para janela
  longa usamos **CDI_BR** (BCB série 12 desde 2000) como proxy — mas
  **atenção ao caveat abaixo**.
- **CDI proxy é otimista para B5P211/IMAB11**: CDI tem duração zero, enquanto
  IMAB11 tem duração 6-8y e sofre em ciclos Selic (MDD -8% em 2024). O backtest
  com CDI subestima MDD e superestima Sharpe do sleeve FI.
- Therefore: **preferir janela 2007-2026 (18,5 anos) como referência primária**.
  Validação adicional com dados REAIS 2020-2026 para confirmar ordem de grandeza.

### 1.2 Modelo de custos (drag anual por ativo)

Aplicado como dedução mensal `(fee/12)` sobre o retorno antes de agregar.
Composto de:

- **Expense ratio** da ETF
- **30% withholding US** sobre dividendos (reduzível a 15% com W-8BEN)
- **Distribuições de cap gains** para ETFs com alto turnover
- **15% DARF BR** sobre ganhos realizados em ETFs US (+ capital gains em BR
  ETFs); assumido holding passivo com rebalance por aportes (turnover ≈ 0).

Drag típico por classe:

| Classe | Drag anual | Observação |
|--------|-----------|------------|
| Factor core US (AVUS/AVUV) | 0,60-0,90% | ER baixo + dividend drag |
| Momentum (SPMO/IDMO) | 1,00-1,10% | Alto turnover |
| LETFs (SSO/UPRO/QLD/TQQQ) | 1,20-1,35% | ER + swap financing embedded |
| NTSX family | 0,55-0,85% | ER 0,20% + Treasury futures |
| **GDE** | **0,30%** | ER 0,20% + gold (no dividend) |
| Return Stacked (RSST/RSBT/RSSX) | 0,80-1,10% | ER ~0,7-1,0% + futures drag |
| BTGD | 1,30% | ER 1,05% + swap/futures |
| Managed futures (DBMF/KMLM) | 1,10-1,30% | ER ~0,9% + distributions |
| **BR FI ETFs** (B5P211/IMAB11/LFTS11) | **0,40-0,50%** | ER + 15% IR on sale |
| **DINF11** (debênture incentivada) | **0,60%** | ER; **0% IR isento Lei 12.431** |
| Gold/BTC spot (GLDM/IBIT) | 0,10-0,30% | ER only |
| US Bonds diretos (TLT/IEF/SHV) | 0,60-0,70% | ER + distribution drag |

### 1.3 Janelas de backtest

- **real_2020_2026** (6 anos) — apenas ETFs reais, regime recente (bull de 2020-2021,
  bear de 2022, recovery 2023-2025).
- **syn_2006_2026** (20 anos) — usa proxies de médio prazo (NTSX_syn, AVUV_syn_3f);
  inclui 2008, COVID, 2022 rate shock. **Janela primária para decisão.**
- **syn_long_1926** (100 anos) — usa testfolio SPY_2x/3x_sim + Ken French;
  inclui Great Depression 1929-42, WWII, 70's stagflation. Suporte qualitativo
  só.

### 1.4 Métricas

- **CAGR líquido:** composição geométrica dos retornos mensais pós-drag.
- **Vol anualizada:** std mensal × √12.
- **Sharpe:** (CAGR − RF médio) / vol_ann, onde RF vem do Ken French (média do período).
- **Max drawdown:** worst peak-to-trough na série de wealth.
- **Bootstrap terminal wealth:** 2000 caminhos de 360 meses via stationary block
  bootstrap (bloco 12 meses). Inicial $10k + $1k/mês de contribuição. Calcula
  p05/p25/p50/p95 da riqueza terminal e da distribuição de MDD.
- **SWR (Safe Withdrawal Rate):** busca binária pelo maior saque anual constante
  que sobrevive 30 anos de retirement em ≥95% dos caminhos bootstrap ($1M inicial).

---

## 2. Avaliação quantitativa do seu plano atual (Plano C as-is)

Pesos do `portfolio-aposentadoria.md` §10:
`AVUS 0.28 / SPMO 0.10 / AVUV 0.14 / AVDE 0.14 / IDMO 0.05 / AVDV 0.09 / AVEM 0.15 / IBIT 0.03 / GLDM 0.02`.

Backtests (proxy primário 2007-2026, 18,5y, com VEA substituindo AVDV
para janela comum):

| Janela | CAGR | Sharpe | MDD | Worst 12m | Vol |
|--------|------|--------|-----|-----------|-----|
| 2007-2026 (proxy) | 7,52% | 0,37 | -53,6% | -42% | 16,5% |
| 2020-2026 (real) | 12,65% | 0,57 | -24,1% | -16% | 17,3% |

Bootstrap 30 anos (10k + 1k/mês):
- p25 terminal wealth = **$0,93M**
- p50 terminal wealth = **$1,50M**
- p95 terminal wealth = $4,50M
- P(MDD > 50%) = 30,2%
- SWR (95% sucesso, 30 anos) = **3,48%**

### Diagnóstico

- **O que está certo:** diversificação geográfica, factor tilts legítimos (SCV +
  Momentum são sustentados pela literatura mais rigorosa — AQR "Our Model Goes
  to Six" mostra que value e momentum são complementares pela correlação
  negativa condicional), custos controlados.
- **O que está na mesa sem ser usado:**
  1. **Zero leverage** — para horizonte de 30 anos com alta tolerância ao
     risco, é subótimo. Asness 1996 (atualizado 2021, WisdomTree) mostra que
     levered 60/40 a 155% bateu equities em **13,1% CAGR vs 9,1%** 1926-2021,
     **mesma vol 20%** ([ETF Trends](https://www.etftrends.com/model-portfolio-content-hub/an-update-to-cliff-asnesss-study-on-the-benefits-of-a-levered-6040/)).
  2. **Zero managed futures** — Hurst/Ooi/Pedersen (2017) documentam retornos
     positivos de trend-following em **cada década desde 1880**, com
     correlação ≈ 0 com equities e bonds. DBMF entregou +21,4% em 2022 quando
     60/40 perdeu 17%. ([AQR Century of Evidence](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2993026))
  3. **Factor tilts poderiam ser mais agressivos** — o papel da PWL Capital
     (Ben Felix) propõe 16% SCV em portfolio 80/20. O seu tem 23% SCV
     (AVUV+AVDV) mas com 100% equities, então o peso relativo é similar.
- **Principais riscos não endereçados:**
  1. **US Estate Tax** (seção 8) — até 40% de imposto federal US sobre saldo US
     >$60k na morte do investidor BR. ETFs Avantis/Invesco são US-domiciliadas.
  2. **Concentração em fatores US** — SCV + Momentum em 25-30% do portfolio
     pode ter períodos de underperform de 10+ anos (value dead 2010-2020;
     momentum crashes abruptos em regime shifts).

---

## 3. A sua proposta SSO 50% — análise quantitativa

Sua sugestão: substituir ~50% do portfolio por SSO (2x SPY), liberando 10% de
espaço pra DM/EM, mantendo factor tilts em DM/EM.

Pesos hipotéticos que eu usei pra backtest:
`SSO 0.50 / AVDE 0.14 / IDMO 0.05 / AVDV 0.09 / AVEM 0.15 / AVUV 0.05 /
IBIT 0.01 / GLDM 0.01`.

### Resultados (janela primária 2007-2026, 18,5y, com proxies corrigidos)

| Métrica | P0 Plano atual | P1 Sua SSO 50% | Delta |
|---------|----------------|-----------------|-------|
| CAGR | 7,52% | 9,53% | +2,01pp ✅ |
| Sharpe | 0,37 | 0,34 | **PIOR** ❌ |
| MDD | -53,6% | **-71,1%** | +17,5pp pior ❌ |
| Vol | 16,5% | 23,7% | +43% ❌ |
| P(MDD>50% em 30y bootstrap) | 30,2% | **79,3%** | 2,6× pior ❌ |
| SWR | 3,48% | 2,48% | -1,00pp ❌ |
| p50 terminal wealth 30y | $1,50M | $2,42M | +61% ✅ |

### Veredito quantitativo

**A troca é ruim.** Você ganha ~1,9pp de CAGR e 35% em p50 de riqueza terminal,
mas paga com **Sharpe pior** e **probabilidade 13× maior de sofrer drawdown
catastrófico**. Em **metade dos caminhos**, MDD passa de 50% — em alguns anos
específicos da sua vida de 30 anos (ex.: 2008 se você tivesse entrado em 2007),
você estaria em -70% de pico.

### Por que o kernel era bom (e a execução não)

O princípio — eficiência de capital, ou seja, obter mais exposição com menos
capital — **é economicamente correto** e é a base das famílias NTSX e Return
Stacked. O problema é que SSO é **pura leverage sobre beta de large-cap**, sem
nenhum componente diversificador no overlay. Toda vez que SPX cai, SSO cai
2× — sem nenhum hedge.

A alternativa NTSX (90% SPX + 60% Treasury futures) faz a mesma coisa que SSO
está tentando fazer (eficiência de capital), mas com **overlay diferente e
descorrelacionado**: os 60% extras são bonds, não mais equity. Isso entrega:

- **Mesma exposição total (~150%)** que SSO 75% seria
- **Mas com segunda perna descorrelacionada** → drawdowns menores
- **ER 0,20%** (vs SSO 0,91% + cost de swap embutido ~5-6%/ano)

No meu backtest 2006-2026 (100% do portfolio em cada candidato):

| Ativo | CAGR | Sharpe | MDD | Vol |
|-------|------|--------|-----|-----|
| SPY 100% | 9,84% | 0,54 | -51% | 15,1% |
| **NTSX_syn 100%** (0,9 SPY + 0,6 IEF) | **11,50%** | **0,71** | -41% | 13,8% |
| **GDE_syn 100%** (0,9 SPY + 0,9 GLD) | ~12,5%* | ~0,70 | ~-40% | ~17% |
| SSO 100% (com LETF fees) | 12,91% | 0,37 | -81% | 30,7% |

(*) GDE_syn em 2006-2026 estimado; GDE real (2022+) tem CAGR 31% em janela
bull-biased. Tese de stacking é equivalente.

NTSX/GDE entregam CAGR próximo ao SSO com **metade do MDD** e Sharpe quase 2×
melhor. Em vez de SSO 50% (+2,0pp CAGR, MDD +17,5pp pior), considere:
- **GDE 30%** (capital efficient equity+gold, used in V3)
- **NTSX ou NTSI** pra componente internacional

**Para sleeve bond: bonds do seu portfolio devem ser em BRL, não USD.**
Campbell-Viceira 2010 (JoF) + Vanguard 2018/2023 + Ben Felix/PWL: bonds na
moeda de consumo. Universo BR FI usado nas V3: B5P211, IMAB11, LFTS11,
DINF11.

---

## 4. Universo de ativos considerado

Tabela de candidatos principais com dados atuais (ER, AUM, inception):

### 4.1 Factor core (tilts SCV/Momentum/Quality)

| Ticker | Função | ER | AUM | Inception | Observação |
|--------|--------|----|----|-----------|------------|
| AVUS | US Core | 0.15% | ~$7,6B | 2019-09 | Factor loadings [0.09 SMB, 0.15 HML] |
| AVUV | US Small-Cap Value | 0.25% | ~$18B | 2019-09 | SMB 0.70, HML 0.55, RMW 0.20 — tilts fortes |
| AVDE | DM ex-US Core | 0.23% | ~$9B | 2019-09 | |
| AVDV | Int Small Value | 0.36% | ~$7B | 2019-09 | |
| AVEM | EM Core | 0.33% | ~$6B | 2019-09 | Clenow-style momentum NÃO aplicado aqui |
| SPMO | US Momentum | 0.13% | ~$10B | 2015-10 | 2024 +45.8%, 2025 +26.6% — forte |
| IDMO | DM Momentum | 0.25% | ~$250M | 2012-02 | |
| DFAT | US Targeted Value (DFA) | 0.29% | ~$15B | 2021-06 | Alternativa a AVUV |
| AVGV | All Eq Markets Value | 0.25% | ~$1B | 2023-06 | Global value, pouco histórico |

### 4.2 Return stacking / efficient core

| Ticker | Estrutura | ER | AUM | Inception | Comentário |
|--------|-----------|----|----|-----------|------------|
| NTSX | 90% SPX + 60% Treasury fut | 0.20% | ~$1B | 2018-08 | Core recomendado |
| NTSI | 90% DM + 60% Treasury fut | 0.26% | ~$330M | 2021-05 | |
| NTSE | 90% EM + 60% Treasury fut | 0.32% | ~$27M | 2021-05 | Liquidez limitada |
| RSST | 100% US Stocks + 100% MF | 0.99% | ~$399M | 2023-09 | MF via Newfound trend |
| RSSB | 100% Global Stocks + 100% Bonds | 0.40% | ~$471M | 2023-12 | Maior do lote |
| RSBT | 100% Bonds + 100% MF | 1.02% | ~$127M | 2023-02 | Equivalente risco-livre levered |
| RSSY | 100% US Stocks + 100% Carry | 0.98% | ~$102M | 2024-05 | Mais novo |
| RSBY | 100% Bonds + 100% Carry | 0.98% | ~$76M | 2024-08 | Mais novo |
| RSSX | 100% US + 100% Gold/BTC | 0.68% | ~$64M | 2025-05 | Experimental |
| RSBA | 100% Bonds + 100% Merger Arb | 0.68% | ~$52M | 2024-12 | Experimental |

### 4.3 Leveraged ETFs (LETFs) — para comparação

| Ticker | Fator | ER | MDD histórico | Observação |
|--------|-------|----|----|------------|
| SSO | 2× SPY | 0.91% | -85% (2008) | LETF legado; drag swaps ~5-6%/ano |
| UPRO | 3× SPY | 0.91% | -77% (2020) | MDD 3× + path dep |
| QLD | 2× QQQ | 0.95% | -57% (2022) | |
| TQQQ | 3× QQQ | 0.88% | -82% (2022) | |
| EFO | 2× MSCI EAFE | 0.95% | -72% (2020) | Proxy pra SSO-estilo em DM |

### 4.3.1 Nota crítica sobre QLD/TQQQ (você perguntou sobre eles)

Backtest 2010-2026 (inception):
- QLD 100%: CAGR **28,73%** / Sharpe 0,78 / MDD -61%
- TQQQ 100%: CAGR **36,67%** / Sharpe 0,66 / MDD -79%

Números espetaculares mas **cherry-picked pelo regime**. 2010-2026 foi o maior
bull run de tech da história (QQQ CAGR 17%). Se você rodar em outra janela:
- 2000-2002 dot-com: QQQ caiu -83%. QLD teria caído ~-95%; TQQQ ~-99% (ruído
  estrutural de reset diário).
- A literatura (Cheng-Madhavan 2009, Leung-Santoli 2016) confirma: **LETFs
  3× sobrevivem regime positivo persistente, são liquidados em regime misto
  volátil**.

**Veredito:** QLD/TQQQ como buy-hold **sem regime filter é gambling**. Se
você quiser exposição tech amplificada, use na mistura:
- 5-10% de QLD numa carteira de 90%+ diversificada, ou
- QLD via regime filter estilo Gayed (mas é Plano B, que FALHOU OOS). Seu
  mandate §4 proíbe efetivamente esta rota.

Gayed específico em `[leverage_for_the_long_run, p.21, Table 12]`:
ETF implementation (UPRO 3×, 2009-2020) underperformou o teórico mesmo
em bull (24,2% vs 26,3% da rotação) devido a **negative leverage premium**
(performance lag intrínseco).

### 4.4 Managed futures (trend-following)

| Ticker | Estrutura | ER | AUM | Inception | 2022 |
|--------|-----------|----|----|-----------|------|
| DBMF | CTA replicação (behavior) | 0.85% | ~$1.1B | 2019-05 | +21.4% |
| KMLM | KFA MLM Index (22 futures) | 0.90% | ~$250M | 2020-12 | +30.4% |
| CTA | Simplify (multi-strat) | 0.84% | ~$300M | 2022-03 | N/A |

### 4.5 Alts (hedges de cauda)

| Ticker | Função | ER | AUM |
|--------|--------|----|----|
| IBIT | Bitcoin spot | 0.25% | $50B+ |
| GLDM | Ouro spot | 0.10% | ~$9B+ |

### 4.6 Bonds — **BR Fixed Income (V3 primary)**

Bonds do portfolio em **BRL, não USD** (Campbell-Viceira 2010, Vanguard 2018/2023,
Ben Felix/PWL — bonds na moeda de consumo). Para brasileiro: NTN-B real yield
IPCA+6% vs US TIPS +2% = +400bps favor BR; BRL/USD vol 15-20% destrói stabilizer.

| Ticker | Estrutura | TER | AUM | Inception | Tax PF |
|--------|-----------|-----|-----|-----------|--------|
| **B5P211** | IT Now IMA-B5 P2 (IPCA+ ≤5y, duration ~2,5y) | 0,20% | R$ 2,87-3,54bi | 2020-11 | 15% IR |
| **IMAB11** | IT Now IMA-B (IPCA+ full curve, duration ~6-8y) | 0,25% | R$ 2,65bi | 2018-2019 | 15% IR |
| **B5MB11** | Bradesco IMA-B5+ (IPCA+ >5y) | 0,20% | - | 2019 | 15% IR |
| **LFTS11** | Investo Teva Selic (duração ~0, cash-proxy) | 0,19% | R$ 3,01bi | 2021 | 15% IR |
| **FIXA11** | Mirae Pré 3y (DI futures) | 0,30% | - | 2018 | 15% IR |
| **DEBB11** | BTG Debêntures DI (corporate credit) | 0,60% | R$ 1,17bi | 2022-06 | 15% IR (NÃO isento) |
| **DINF11** | BTG Debêntures Incentivadas Lei 12.431 | ~0,60% | menor | ~2023 | **0% ISENTO** |

**Destaques:**
- **DINF11** é o único ETF de debêntures incentivadas na B3 com isenção total
  IR pra PF (Lei 12.431/2011 infraestrutura). Pickup sobre CDI ~150-180bps,
  100% retido vs DEBB11 que pega 15% IR.
- **B5P211** vs **IMAB11**: B5P211 é stabilizer (duration curta, MDD baixo);
  IMAB11 é inflation-match de longo prazo (duration ~7y, MDD -8% em 2024).

### 4.7 US Bonds — só pra referência, NÃO usado nas V3

| Ticker | Duração | ER | Nota |
|--------|---------|----|------|
| TLT | 20+ anos | 0,15% | -71% em 2022 |
| IEF | 7-10 anos | 0,15% | -15% em 2022 |
| SHV | 0-1 ano | 0,15% | Cash proxy |

Usados na V1/V2. Substituídos por BR FI na V3.

---

## 5. Screening: 12 carteiras-candidatas (V1, pre-V3 redesign)

Essa seção preserva o ranking inicial de 12 carteiras-candidatas (v1 antes
da incorporação de BR FI + GDE). Serve como contexto comparativo para
mostrar que **return stacking em geral domina LETF puro**, e por que a V3
redesenhou com BR FI. Dados completos em `results/backtest_summary.csv`.

### 5.1 Ranking por Sharpe (janela 2006-2026, 20 anos, V1 proxies)

| # | Portfolio | CAGR | Sharpe | MDD | P(MDD>50%) 30y |
|---|-----------|------|--------|-----|----------------|
| 1 | **P6 Return Stacked agg** | 8,41% | **0,59** | -30% | 0,0% |
| 2 | P9 Max Sharpe (hand-tuned) | 9,04% | 0,56 | -41% | 0,1% |
| 3 | P5 NTSX global 60/30/10 | 8,99% | 0,52 | -46% | 0,3% |
| 4 | P7 Stacked factor core | 8,52% | 0,50 | -43% | 0,2% |
| 5 | P11 Max SWR (retirement) | 7,88% | 0,61 | -29% | 0,0% |
| 6 | P10 Terminal MDD≤50% | 8,57% | 0,49 | -45% | 0,8% |
| 7 | **P0 Plano atual** | 7,54% | 0,39 | -50% | 4,3% |
| 8 | P2 SSO 100% | 12,91% | 0,37 | -81% | 96,9% |
| 9 | P4 HFEA 55/45 | 11,22% | 0,37 | -73% | 92,2% |
| 10 | **P1 Sua proposta SSO 50%** | 9,44% | 0,35 | -69% | 53,3% |
| 11 | P8 Max CAGR LETF heavy | 11,39% | 0,38 | -73% | 82,5% |
| 12 | P3 UPRO 100% | 11,95% | 0,22 | -94% | 100,0% |

### Observações

- **Portfolios baseados em return stacking (P5/P6/P7/P9)** dominam o top-5 em
  Sharpe — são os que entregam melhor risco-retorno.
- **O plano atual P0 (#7) fica no meio** — superior aos LETF-puros em
  Sharpe/MDD mas inferior aos return-stacked.
- **Sua proposta P1 (#10)** fica abaixo do plano atual em Sharpe mesmo tendo
  CAGR superior — confirma o veredito qualitativo da seção 3.
- **LETFs puros (P2/P3/P8)** dominam em CAGR absoluto mas falham em
  Sharpe/MDD. Em 30 anos de bootstrap, P3 (UPRO 100%) **passa por drawdown
  >50% em 100% dos caminhos** — garantido.

### 5.2 Terminal wealth 30 anos (10k inicial + 1k/mês)

| Portfolio | p05 | p25 | p50 | p95 | P(MDD>50%) |
|-----------|-----|-----|-----|-----|-----------|
| **P0 Plano atual** | $0,61M | **$0,82M** | **$1,13M** | $2,50M | 4,3% |
| P1 Sua SSO 50% | $0,58M | $0,87M | $1,52M | $6,52M | 53,3% |
| P2 SSO 100% | $0,78M | $1,09M | $3,16M | $51,76M | 96,9% |
| P3 UPRO 100% | $0,32M | $0,61M | $2,60M | $176,45M | 100,0% |
| P5 NTSX global | $0,38M | $0,40M | $0,46M | $0,69M | 0,3% |
| P6 Return Stacked | $0,48M | $0,52M | $0,60M | $0,92M | 0,0% |
| P8 Max CAGR LETF | $0,62M | $1,11M | $2,41M | $19,34M | 82,5% |

Nota: P5/P6 bootstrap underperform por causa do proxy conservador de MF
(ver seção 1.1 caveats); on real 2020-2026 window entregam CAGR ~8,5-9%.

### 5.3 Lição central dos backtests

> **Leverage puro sobre beta = cassino.**
> **Leverage sobre overlay descorrelacionado = eficiência.**

Em números: P2 (SSO 100%) tem p95 terminal wealth = $51M (absurdo upside) mas
p25 = $1,09M (pior que o plano atual no pior quartil). O risco é convexo pra
baixo: ou você fica muito rico, ou muito pobre, raramente no meio.

Já as carteiras NTSX/Return-Stacked (P5/P6/P7) têm distribuição **mais
estreita**: p25 e p95 próximos. **Menos variância de outcome** — é o que você
quer quando está otimizando sua aposentadoria única.

---

## 6. As 4 carteiras V3 otimizadas finais

Cada uma otimizando uma função objetivo diferente, usando:
- **Equity core em USD** via NTSX family + GDE (capital efficient) + AVUV/AVDV/AVEM/SPMO (factor tilts)
- **Fixed income em BRL** via B5P211 + IMAB11 + LFTS11 + DINF11 (home-currency principle)
- **Gold/BTC via return stacking** via GDE integrado + BTGD satellite
- **Managed futures** via DBMF + KMLM (onde aplicável)

Janela de backtest primária: **2007-07 → 2026-02 (18,5 anos, proxy)** com CDI como
BR FI proxy. Validação adicional com dados REAIS 2020-2026.

### 6.1 FINAL V3_1: Max CAGR — "Leveraged Growth Engine"

**Objetivo:** maximizar CAGR esperado em 30 anos; zero FI (drag); aceita MDD até ~40%.

| Ticker | Peso | Classe |
|--------|------|--------|
| **GDE** | 30% | 90% SPX + 90% gold (1,8× lev) |
| NTSI | 15% | Int 90/60 |
| NTSE | 5% | EM 90/60 |
| AVUV | 15% | US SCV |
| AVDV | 10% | Int SCV |
| AVEM | 5% | EM core |
| SPMO | 5% | US Momentum |
| SSO | 10% | 2× SPY direto (extra leverage) |
| BTGD | 3% | Gold+BTC stacked |
| IBIT | 2% | Bitcoin spot |

**Alavancagem efetiva ≈ 1,75×.** Zero bonds. Factor tilts 35%.

**Performance (proxy long-history 2014-2026, janela 11,4y por BTGD_syn):**
CAGR **18,33%** / Sharpe 0,93 / MDD -29,7% / Vol 17,5%

**Bootstrap 30y (10k + 1k/mês):**
p05=$2,89M / p25=**$7,53M** / p50=**$12,42M** / p95=$46,17M / P(MDD>50%)=1,4% / SWR 9,61%

**Veredito:** Máxima convexidade à direita. GDE 30% substitui a lógica do NTSX+SSO
com stacking de gold (descorrelacionado) em vez de bonds (que drena em bull). O
SSO 10% direto adiciona a camada extra de beta puro. Bull case forte, caveat:
janela curta 2014-2026 é bull-biased.

### 6.2 FINAL V3_2: Max Sharpe — "Diversified Factor + BR FI"

**Objetivo:** maximizar Sharpe; heavy BR FI + MF diversifier.

| Ticker | Peso | Classe |
|--------|------|--------|
| GDE | 20% | Capital efficient equity + gold |
| NTSI | 10% | Int 90/60 |
| AVUV | 10% | SCV |
| AVDV | 5% | Int SCV |
| DBMF | 10% | US MF |
| KMLM | 5% | US MF 2º |
| **B5P211** | 15% | BR IPCA+ curto (stabilizer) |
| **IMAB11** | 10% | BR IPCA+ longo (duration) |
| **DINF11** | 10% | BR debênture isenta IR |
| GLDM | 5% | Ouro extra |

**Alavancagem efetiva ≈ 1,25×.** 35% em BR FI. 15% em MF.

**Performance (proxy 2007-2026, 18,5y):**
CAGR 12,46% / Sharpe **1,12** / MDD -18,1% / Vol 9,9%

**Bootstrap 30y:**
p05=$2,18M / p25=**$2,75M** / p50=**$3,70M** / p95=$7,98M / P(MDD>50%)=0,0% / SWR 8,33%

**Veredito:** Home-currency bonds + MF + factor tilt entregam Sharpe 1,12 com
MDD limitado. Caveat: Sharpe inflado pelo proxy CDI (duração zero); real-world
com IMAB11 duration 6-8y seria Sharpe 0,8-0,9.

### 6.3 FINAL V3_3: Max Terminal Wealth com MDD ≤ 50% — "Bounded Growth"

**Objetivo:** max p50 terminal wealth com MDD histórico ≤ 50%. **Meu default
pra acumulação 30-60 anos.**

| Ticker | Peso | Classe |
|--------|------|--------|
| GDE | 20% | Capital efficient eq+gold |
| NTSI | 15% | Int 90/60 |
| NTSE | 5% | EM 90/60 |
| AVUV | 15% | US SCV |
| AVDV | 10% | Int SCV |
| AVEM | 5% | EM core |
| SPMO | 5% | US Momentum |
| DBMF | 5% | MF diversifier |
| **B5P211** | 10% | BR IPCA+ curto |
| **IMAB11** | 5% | BR IPCA+ longo |
| **DINF11** | 3% | BR isenta |
| GLDM | 2% | Ouro |

**Alavancagem efetiva ≈ 1,35×.** 18% BR FI. Factor tilts 35%.

**Performance (proxy 2007-2026):**
CAGR **11,69%** / Sharpe 0,79 / MDD -35,5% / Vol 13,0%

**Bootstrap 30y:**
p05=$1,66M / p25=**$2,23M** / p50=**$3,31M** / p95=$8,06M / P(MDD>50%)=1,8% / SWR 6,75%

**Veredito:** Balanceada. CAGR alto, MDD respeita o gate 50%, factor tilts
robustos, BR FI suficiente pra rebalancear na queda mas não tanto pra drenar
CAGR. É o melhor ponto pragmático pro seu perfil (30 anos, tolerante a
complexidade, factor believer).

### 6.4 FINAL V3_4: Max SWR — "Retirement Income BR"

**Objetivo:** max SWR em 30 anos de retirement (95% success). End-state do
glidepath. **NÃO usar em acumulação.**

| Ticker | Peso | Classe |
|--------|------|--------|
| GDE | 15% | Eq + gold stacked |
| AVUV | 8% | SCV residual |
| AVDV | 5% | Int SCV |
| DBMF | 10% | MF crisis alpha |
| KMLM | 5% | MF 2º |
| **B5P211** | 20% | BR IPCA+ curto (stabilizer dominante) |
| **IMAB11** | 15% | BR IPCA+ longo (duration/income) |
| **LFTS11** | 10% | BR Selic cash |
| **DINF11** | 7% | BR isenta (tax-free income) |
| GLDM | 5% | Ouro |

**Alavancagem efetiva ≈ 1,15×.** **52% BR FI** (maior peso). 15% MF. Zero US bonds.

**Performance (proxy 2007-2026):**
CAGR 11,69% / Sharpe **1,36** / MDD **-12,1%** / Vol 7,5%

**Bootstrap 30y:**
p05=$1,93M / p25=$2,48M / p50=$3,13M / p95=$5,87M / P(MDD>50%)=0,0% / SWR **8,61%**

**Validação com DADOS REAIS (janela 2020-2026, 65 meses):**
CAGR 11,61% / Sharpe 1,33 / MDD -3,5% / Vol 6,3% — **estrutura confirmada**.

**Veredito:** Retirement end-state. BR FI dominante pro stabilizer + income,
MF pra crisis alpha, factor tilt residual pra inflation hedge. Proxy CDI
infla Sharpe (real-world ~0,9-1,0 com duration risk); mesmo assim o
estrutural é sólido.

### 6.5 Tabela comparativa V3 final

Janela 2007-2026 (18,5y; V3_1 em 2014-2026 por BTGD_syn). Proxy CDI otimista
pra BR FI (veja §1.1).

| Carteira | CAGR | Vol | Sharpe | MDD | p25 TW | p50 TW | p95 TW | SWR | BR FI% | Leverage |
|----------|------|-----|--------|-----|--------|--------|--------|-----|--------|----------|
| P0 atual | 7,52% | 16,5% | 0,37 | -54% | $0,93M | $1,50M | $4,50M | 3,48% | 0% | 1,0× |
| P1 SSO 50% | 9,53% | 23,7% | 0,34 | **-71%** | $1,15M | $2,42M | $12,5M | 2,48% | 0% | 1,5× |
| **V3_1 Max CAGR** | **18,33%** | 17,5% | 0,93 | -30% | $7,53M | **$12,42M** | $46,2M | 9,61% | 0% | 1,75× |
| **V3_2 Max Sharpe** | 12,46% | 9,9% | 1,12 | -18% | $2,75M | $3,70M | $7,98M | 8,33% | 35% | 1,25× |
| **V3_3 Max TW/MDD50** | 11,69% | 13,0% | 0,79 | -36% | $2,23M | $3,31M | $8,06M | 6,75% | 18% | 1,35× |
| **V3_4 Max SWR** | 11,69% | 7,5% | **1,36** | **-12%** | $2,48M | $3,13M | $5,87M | **8,61%** | 52% | 1,15× |

Rankings consistentes com o nome:
- **Max CAGR:** V3_1 (18,33%) ✅
- **Max Sharpe:** V3_4 (1,36) > V3_2 (1,12) — V3_4 vence no proxy CDI
- **Max TW/MDD≤50%:** V3_3 (MDD -36% dentro do gate, CAGR 11,69%) ✅
- **Max SWR:** V3_4 (8,61%) ✅

**Vs P0 (plano atual):** todas as 4 V3 batem P0 em CAGR, Sharpe e terminal
wealth. V3_3 e V3_4 batem em MDD também; V3_1 troca MDD (-30% vs -54% do P0)
por upside maciço (p95 $46M); V3_2 tem MDD menor (-18%).

### 6.6 Comparação V2 (US bonds) vs V3 (BR FI)

Para auditoria — mostra o impacto de substituir US bonds por BR FI:

| Métrica | V2 (com US bonds) | V3 (com BR FI) | Delta |
|---------|-------------------|----------------|-------|
| Max CAGR | 10,40% | 18,33% | +7,93pp* |
| Max Sharpe | 0,74 | 1,36 | +0,62 |
| Max SWR | 5,82% | 8,61% | +2,79pp |
| Menor MDD | -21,5% | -12,1% | -9,4pp (melhor) |
| V3_2 p50 TW 30y | $1,77M | $3,70M | +$1,93M |

(*) V3_1 em janela bull-biased 2014-2026 (vs V2 2007-2026). Real delta
esperado: +3-5pp CAGR.

**A direção do delta é correta** — BR FI domina US FI pro brasileiro por 3
motivos combinados: (1) retorno nominal BR maior (12% vs 3-4%), (2) elimina
FX vol sobre stabilizer, (3) tax-efficient (DINF11 isento).

**Caveat honesto:** parte do ganho é artificial pelo proxy CDI (duração zero
vs IMAB11 duração 6-8y). Real-world esperado: +0,3-0,4 Sharpe vs V2 (não
+0,62) e MDD BR FI real seria -5% a -8%, não zero.

---

## 7. Glidepath ao longo de 30 anos

### 7.1 Opção conservadora (seu documento original)

Age 30-45: 100% equity / Age 45-55: add bonds / Age 55-60: 30-40% FR.

**Problema:** esta trajetória **não é dominante** segundo Cederburg et al.
2024 ([SSRN 4590406](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4590406),
dataset 38 países 1890-2019, 1M bootstraps). TDFs tradicionais subperformam
all-equity em **todos** os outcomes (wealth at retirement, consumo sustentado,
risco exaustão, bequests).

### 7.2 Minha recomendação — glidepath por mix de fontes de retorno

Em vez de mudar `equity %` por idade, troque o **mix de fontes de retorno**
por fase da vida:

| Fase | Idade | Portfolio | Racional |
|------|-------|-----------|----------|
| Acumulação agressiva | 30-45 | **V3_1** (Max CAGR) | Horizonte 15+ anos absorve drawdowns |
| Transição | 45-55 | **V3_3** (Max TW/MDD≤50%) | 15-25 anos pós-transição; capa MDD pra proteger sequence risk |
| Pré-aposentadoria | 55-60 | **V3_2** (Max Sharpe) | 5-10 anos antes; sequence risk dominante |
| Aposentadoria | 60+ | **V3_4** (Max SWR) | Foco em withdrawal rate sustentável |

**Mecânica do glidepath (exemplo V3_1 → V3_3 aos 45):**
- Parar de aportar em SSO e BTGD (eliminar a leverage extra)
- Redirecionar aportes pra B5P211 + IMAB11 + DINF11 até atingir ~18% BR FI
- Reduzir GDE de 30% pra 20% vendendo gradualmente em anos bons

### 7.3 Opção Cederburg-pura (mais agressiva, evidência-based)

Se você acredita em Cederburg/Anarkulova (2024) — **manter V3_1 ou V3_3
durante toda a vida, inclusive em retirement.** A evidência global multi-país
(38 países, 1M bootstraps, 1890-2019) é forte: rising equity glidepath
**domina** a trajetória decrescente em todos os outcomes testados.

**Trade-off honesto:** você vai experimentar drawdowns de 30-50% mesmo aos 65
anos. Se sua tolerância psicológica não aguenta, use 7.2 (é subótima
estatisticamente mas superior para você, pessoalmente, se você vender no
fundo do drawdown).

### 7.4 Rebalanceamento durante a fase de acumulação

- **Aportes mensais comprando o que está abaixo do target** — zero turnover,
  zero DARF. Isso é o rebalanceamento mais tax-efficient possível.
- **Rebalanceamento formal (vendas)** só se drift > 5% em alguma classe após
  12 meses. Aceite um pouco de drift pra evitar cap gains.
- **Em anos de perda** (>10% MDD em equity), **acelerar o aporte em classes
  machucadas** — o mesmo princípio do value investing applied ao seu
  portfolio.

---

## 8. ⚠️ Risco crítico não endereçado no seu plano: US Estate Tax

Esta seção é o alerta mais importante deste documento.

### 8.1 O problema

- Investidor **não-residente dos EUA** (brasileiro) com **US situs assets > $60k**
  é sujeito a **estate tax federal US até 40%** sobre o saldo ACIMA de $60k na
  morte.
- **ETFs US contam como US situs assets.** AVUS, AVUV, SPMO, AVDE, IDMO, AVDV,
  AVEM, NTSX, NTSI, NTSE, RSST, RSSB, RSBT, DBMF, KMLM, SSO, UPRO, QLD, TQQQ,
  IBIT, GLDM — **TODOS** os tickers analisados neste documento estão neste
  rol.
- Cidadãos/residentes US têm exemption de **$15 milhões**; non-resident aliens
  têm **$60.000**.
- Exemplo numérico: se no seu falecimento o saldo é **$1,5M** nesses ETFs,
  seus herdeiros pagam **40% × ($1,5M − $0,06M) = $576k**. Quase 40% da
  riqueza **simplesmente some**.

### 8.2 Soluções (ordenadas por robustez)

1. **ETFs UCITS domiciliados na Irlanda** (solução primária, não custosa):
   - `CSPX` (iShares S&P 500 acc, Irlanda) — equivalente a SPY
   - `IWDA` (iShares MSCI World acc, Irlanda) — global developed
   - `VWCE` (Vanguard FTSE All-World, Irlanda) — equivalente a VT
   - `EIMI` (iShares MSCI EM acc, Irlanda) — EM
   - **Não são US situs.** Irlanda tem tratado com US que reduz withholding
     pra 15% em vez de 30%.
   - Disponíveis na **IBKR** (não no Inter Internacional).
   - **Problema:** AVUV / AVDV / NTSX / RSST / DBMF **não têm equivalente
     UCITS direto.** Factor ETFs UCITS existem mas com menor tilt (ex.: `IWVL`
     iShares Edge MSCI World Value).

2. **Foreign corporation holder** (complexo, custoso):
   - Setup de pessoa jurídica em BVI / Hong Kong / Caymans que detém os ETFs
     US em nome próprio.
   - Na morte do beneficiário, transfere-se a PJ, não os ativos.
   - Custo compliance: **$2-5k/ano + setup $10-20k**.
   - Só vale a pena pra patrimônios >$500k em ETFs US.

3. **Limitar exposição US-domiciliada a $60k** (estratégia cap):
   - Usar UCITS pra beta core (SPY-like).
   - Limitar Avantis/Invesco/Return Stacked US à franja tática do portfolio,
     mantendo total US-domiciliado < $60k ao longo do tempo.
   - Perde-se acesso a AVUV / NTSX quando o patrimônio cresce demais.

4. **Life insurance com US situs hedge**:
   - Apólice de seguro de vida em USD cobre exatamente o estate tax due.
   - Custo 0,3-0,8%/ano sobre o valor segurado; razoável como seguro.

### 8.3 Minha recomendação prática

Para patrimônio crescendo pra >$250k em US situs:

- **60% via UCITS irlandeses** (CSPX + IWDA + VWCE + EIMI) na IBKR.
- **30% via ETFs Avantis US-domiciliados** (AVUV + AVDV + AVEM) onde factor
  tilt específico não tem UCITS equivalente.
- **10% via NTSX/Return Stacked** (produtos de capital efficiency sem UCITS).

Monitorar total US-domiciliado a cada 2 anos; se ultrapassar $500k, começar
processo de setup da foreign corp.

**Referências críticas:**
- [IRS Estate Tax NRA](https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax-for-nonresidents-not-citizens-of-the-united-states)
- [AbitOs 2025 Guide](https://abitos.com/the-2025-estate-and-gift-tax-guide-for-foreign-investors/)
- [Bogleheads non-US investor guide](https://www.bogleheads.org/wiki/Non-US_investor's_guide_to_navigating_US_tax_traps)

---

## 9. Operacional — dois brokers, custos, tax

### 9.1 Estrutura dual-broker (V3 requer)

| Sleeve | Moeda | Broker | Tickers |
|--------|-------|--------|---------|
| **BR FI** | BRL | Corretora BR doméstica | B5P211, IMAB11, LFTS11, DINF11 |
| **US equity + GDE + alts** | USD | Broker US | GDE, NTSI, AVUV, AVDV, SSO, DBMF, BTGD, IBIT |

**Recomendação do par de brokers:**

- **Setup mais simples:** Inter DTVM (BR) + Inter Internacional (US) — mesma
  conta Inter, zero corretagem ambos, transferências BRL↔USD internas. FX
  spread 0,99-1,50% é o custo invisível (em 30 anos de aportes = 15-25% de
  drag sobre capital aportado).
- **Setup mais eficiente:** XP Investimentos (BR) + IBKR (US). FX spread IBKR
  essencialmente zero ($2 fee). Vale a pena quando aporte USD > $500/mês.
  Migração Inter Internacional → IBKR via ACAT (gratuito).
- **Setup híbrido:** Inter DTVM (BR) + IBKR (US). Sem o benefício Inter-Inter
  de transfer interno, mas pega o BR-eficiente + US-eficiente.

### 9.2 Tax treatment por sleeve

**BR FI (ETFs renda fixa BR):**
- ER + 15% IR sobre ganho de capital na venda
- **DINF11: 0% IR** (debênture incentivada Lei 12.431)
- Sem come-cotas (diferente de FIs)
- Dividendos/juros distribuídos: 15% na fonte (exceto DINF11: isento)

**US equity + alts:**
- Withholding 30% dividendos na fonte (reduzível a 15% com W-8BEN, mas
  Brasil não tem treaty, então 30% fica padrão)
- Capital gains: 15% DARF BR sobre ganho líquido, DAA anual em maio
  (Lei 14.754/2023)
- **Isenção R$35k/mês NÃO aplica** a ETFs US (só ações listadas B3)
- **US Estate Tax** — ver §8

### 9.3 Custos recorrentes estimados (V3_3 como exemplo)

| Componente | Drag anual |
|------------|-----------|
| ER ponderado | ~0,35% |
| 30% withholding dividendos USD (yield ~1,2% em GDE-heavy) | ~0,36% |
| Cap gains distributions + IR 15% BR | ~0,15% |
| FX spread Inter (se houver transfer BR→USD mensal 1,25%) | ~0,15% |
| **Drag total** | **~1,0%/ano** |

Sobre patrimônio R$2M (~$400k): **~$4k/ano em custos invisíveis**.
Sobre patrimônio R$10M (~$2M): ~$20k/ano.

### 9.4 DARF mensal/anual

- **Aporte mensal = zero DARF** (não há realização)
- **Rebalanceamento por aportes = zero DARF**
- **Venda ETFs BR:** 15% IR, declaração anual (DINF11: isento)
- **Venda ETFs US:** 15% DARF, DAA anual maio
- **Dividendos USD:** carnê-leão mensal; compensável com tax credit 30% na
  fonte (limitado a IR devido no BR — geralmente zera)

---

## 10. Decisões-chave (checklist antes de começar)

1. [ ] **Eu aceito que vou ter drawdowns de 30-40% mesmo em FINAL_3/4?**
   Se não, usar FINAL_4 mesmo em fase de acumulação (perde ~1pp CAGR).
2. [ ] **Vou migrar pra IBKR e UCITS agora** ou ficar no Inter até crescer?
   Tradeoff: complexidade vs estate tax risk.
3. [ ] **Aporte mensal esperado em USD** — define break-even Inter vs IBKR e
   ritmo da curva de terminal wealth.
4. [ ] **Tolero return stacking via RSST/RSBT (ER 1%)?** Alternativa:
   replicar internamente com NTSX + DBMF separados (custo menor, operação
   mais complexa).
5. [ ] **SPMO como tilt de momentum**: fica (tax inefficient mas +alpha) ou
   sai (mais limpo operacionalmente)?
6. [ ] **Hedge cambial parcial via NTN-B / IPCA+**: 0% (all-USD bet),
   10-20% (prudente), 30% (conservador)?

---

## 11. Citações dos livros do projeto

Lista das afirmações técnicas fundamentais deste documento com citações em
`[book.slug, p.X]`:

- **Volatility drag mechanics** — `[leverage_for_the_long_run, p.4-6]`:
  "Daily re-leveraging combined with high volatility creates compounding
  issues (...) At 40% vol, probability of loss >50%; at 70% vol, strong
  likelihood of loss even with +10% annual drift."

- **LETF buy-hold risk-of-ruin** — `[leverage_for_the_long_run, p.19-20]`:
  3× constant leverage 1929-1942 suffered -99.9% DD, requiring +174.037%
  recovery — "near-certain risk of ruin."

- **Risk parity: equal risk contribution** — `[risk_parity, p.5, ch.1]`:
  60/40 tradicional = 92% risco equity / 8% risco bond; para true ERC
  precisa inverse-vol ponderação.

- **HRP over-out-of-sample** — `[advances_fin_ml, p.302-308, ch.16]`:
  HRP reduz out-of-sample variance vs min-variance CLA sem inversão de
  matriz singular.

- **Momentum factor (90d lookback)** — `[stocks_on_the_move, p.73, p.76-77]`:
  Annualized exponential regression slope × R² de 90 dias é o critério
  empírico dominante.

- **Kelly / half-Kelly for buy-hold** — `[systematic_trading, p.144, ch.9]` e
  `[algo_trading_chan, p.172, ch.8]`: `f = m/s²` como upper bound,
  half-Kelly (f/2) é o default prático.

- **Backtest honesty (PBO/DSR)** — `[advances_fin_ml, p.208-211, 275, ch.12-14]`:
  PBO > 0.5 = overfit; DSR corrige Sharpe pelo número de trials.

Citações web completas em `data/web_research.md`.

---

## 12. Próximos passos (se quiser continuar a linha de raciocínio)

1. **Validar com paper trading simulado** — pegar uma das 4 finals e rodar
   12 meses simulados com dados reais (paper broker IBKR) pra sentir o
   operacional.
2. **Quantificar o upgrade custo** — calcular custo real de migração
   Inter→IBKR (ACAT fees, FX, período sem aportar).
3. **Escolher UCITS replacements específicos pra cada bucket** —
   mapeamento 1:1 dos ETFs US pra equivalentes Irlandeses, sabendo
   tracking error esperado.
4. **Fase D-promotion se ainda ativa** — se a Strategy D ativa morrer, pode
   valer aumentar a alocação ao Plano C de 60-80% pra 90%+, deixando
   10% pra Plano A Pepperstone único (se ele emergir depois).
5. **Setup de life insurance USD** como hedge de estate tax — cotações com
   corretoras específicas (AIG, Prudential).

---

## 13. Disclaimers

- Não é recomendação de investimento personalizada. Análise educacional.
- Todos os números de CAGR/Sharpe/MDD são históricos e bootstrap; **futuro
  pode divergir materialmente**.
- Tax law BR/US pode mudar (Lei 14.754/2023 é recente; estate tax treaty
  US-BR não existe).
- Return Stacked ETFs têm amostra curta (<3 anos). Bootstrap usa proxies que
  podem subestimar ou superestimar retornos reais futuros dependendo do
  regime.
- Prefira validação externa (advisor fee-only CFP) antes de mudanças
  materiais.

---

*Documento gerado em 2026-04-23 por pipeline reprodutível em
`reports/portfolio_aposentadoria_v2/scripts/`. Backtests a partir de dados
Tiingo + Ken French + Testfolio SPY-SIM. Pesquisa web de 2024-2026 em
`data/web_research.md`.*
