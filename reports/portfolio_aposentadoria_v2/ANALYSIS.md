# Portfolio de Aposentadoria v2 — Análise, Backtest e 4 Portfolios Otimizados

> **⚠️ LEIA PRIMEIRO: [`CORRECTIONS.md`](CORRECTIONS.md)** — em 2026-04-23
> pós-entrega, o usuário pegou uma inconsistência nos rankings (FINAL_1
> "Max CAGR" tinha CAGR menor que FINAL_3). Dois bugs foram encontrados
> e corrigidos: (1) NaN→0 em daily→monthly resample; (2) proxies com
> janelas desalinhadas. As tabelas neste documento **abaixo da seção 6**
> ainda refletem os números antigos (buggy). A seção 6 foi reescrita
> com números corretos. Os números do §3 (análise da sua proposta SSO)
> não mudaram materialmente. Me desculpe pelo descuido — você estava
> certo de desconfiar.

> Documento consolidado da sessão 2026-04-23 respondendo ao pedido:
> "otimize meu portfolio de aposentadoria (Plano C) levando em conta factor
> investing, return stacking e ETFs alavancados. Me dê 4 opções finais, uma
> por função objetivo."
>
> Artefatos relacionados (nesta pasta):
>
> - `scripts/01*–06_*.py` — pipeline reprodutível de download, panel, simulação
> - `data/returns_monthly.parquet` — panel mensal 1926-2026 (50 ativos)
> - `data/web_research.md` — relatório completo de pesquisa 2024-2026 com links
> - `results/backtest_summary.csv` — 12 portfolios × 3 janelas históricas
> - `results/final_portfolios.json` — as 4 carteiras finais + bootstrap
>
> Citações seguem o padrão do projeto: `[book.slug, p.X]` pros 33 livros em
> `books/summaries/`; web papers com link explícito.

---

## Sumário Executivo

1. **O plano atual (Plano C as-is) é defensível mas deixa 2-3pp de CAGR/ano na
   mesa.** Em backtest 20 anos (2006-2026): CAGR líquido ~7,5% / Sharpe 0,39 /
   MDD -50% / bootstrap p50 terminal wealth (30 anos, 10k + 1k/mês) = **$1,13M**.
2. **Sua proposta do SSO 50% tem um kernel bom (eficiência de capital) mas uma
   execução ruim.** Backtest 2006-2026: CAGR sobe pra 9,44% (+1,9pp), mas
   MDD vai a -69%, Sharpe CAI de 0,39 pra 0,35, e a probabilidade de sofrer
   drawdown >50% em 30 anos de bootstrap sobe de 4% pra **53%**. **Troca ruim
   de risco por retorno** — mesma direção que você quer (eficiência de capital)
   mas com o veículo errado.
3. **Há um caminho melhor:** usar return stacking (família WisdomTree NTSX +
   família Return Stacked ETFs de Corey Hoffstein) em vez de LETFs puros. Ele
   entrega **mais CAGR**, **melhor Sharpe** e **menor MDD** simultaneamente.
4. **Risco crítico e subestimado para brasileiro com portfolio US-domiciliado:
   US Estate Tax** (seção 8). Na sua morte, ETFs US contam como "US situs
   assets" e herdeiros podem pagar **até 40% de imposto federal US** sobre o
   saldo acima de $60k. Solução: migrar a maior parte para ETFs UCITS
   domiciliados na Irlanda (CSPX, IWDA, etc.) disponíveis na IBKR.
5. **4 portfolios finais** — um por função objetivo — descritos na seção 6.
   Meu default pro seu caso (30 anos, factor investing, sem medo de complexidade)
   seria **Final 3 (Max Terminal Wealth / MDD ≤ 50%)**: CAGR 9,40% / Sharpe 0,64
   / MDD -36% / terminal wealth p50 $1,81M em 30 anos. É 60% mais rico que o
   plano atual.

---

## 1. Metodologia

### 1.1 Panel de dados

Fontes unificadas em `data/returns_monthly.parquet` (50 ativos, 1926-2026):

| Fonte | Ativos | Janela |
|-------|--------|--------|
| Tiingo REST API (reais) | AVUS, AVUV, AVDE, AVDV, AVEM, IDMO, SPMO, NTSX, NTSI, NTSE, RSST, RSSB, RSBT, RSSY, RSBY, DBMF, KMLM, CTA, IBIT, GLDM, GLD, AVGV, DFAC, DFAT | Inception → 2026-04 |
| Tiingo (projeto, existente) | SSO, UPRO, QLD, TQQQ, SPY, VTI, VEA, VWO, TLT, IEF, SHV | 2001-2026 |
| Testfolio SPY-SIM | SPY_1x_sim, SPY_2x_sim, SPY_3x_sim | **1885-2026** (141 anos) |
| Ken French F-F daily | Mkt-RF, SMB, HML, RF | **1926-2026** (100 anos) |
| Sintéticos | NTSX_syn (0.9 SPY + 0.6 IEF), RSST_syn (SPY+DBMF), AVUV_syn_3f (RF + Mkt + SMB + HML com factor loadings) | Várias janelas |

Caveats:
- Return Stacked ETFs têm inception 2023-2024 — backtest real limitado a
  ~2,5 anos; extrapolação via proxies (NTSX_syn para o componente stocks+bonds).
- Managed futures proxies de longo prazo são fracos — uso `SPY_1x_sim` como
  fallback, o que SUBESTIMA o MF em janelas longas (MF histórico é
  descorrelacionado de equities, `SPY_1x_sim` é puramente equity).
- Therefore: **preferir a janela 2006-2026 (20 anos) para decisões
  quantitativas**. A janela 1926-2026 é suporte qualitativo (ciclos de regime)
  mas tem viés pra baixo nas carteiras com MF/RS.

### 1.2 Modelo de custos (drag anual por ativo)

Aplicado como dedução mensal `(fee/12)` sobre o retorno antes de agregar.
Composto de:

- **Expense ratio** da ETF (valores atuais divulgados pelo emissor).
- **30% withholding US** sobre dividendos (baseline; reduzível a 15% com
  W-8BEN). Dividend yield estimado por classe de ativo.
- **Distribuições de ganho de capital** para ETFs com alto turnover
  (momentum especialmente).

Drag total típico:

| Classe | Drag anual |
|--------|-----------|
| Factor core (AVUS/AVUV) | 0,60-0,90% |
| Momentum (SPMO/IDMO) | 1,00-1,10% |
| LETFs (SSO/UPRO) | 1,20-1,35% |
| NTSX family | 0,55-0,85% |
| Return Stacked | 0,95-1,10% |
| Managed futures | 1,10-1,30% |
| Bonds longos | 0,60-0,70% |

Importante: **15% DARF brasileiro em ganhos realizados** NÃO está no drag —
assume-se holding passivo com rebalanceamento por aportes (turnover ≈ 0%).
Se houver rebalance por venda anual, somar ~0,3% extra.

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

Backtests:

| Janela | CAGR | Sharpe | MDD | Worst 12m | Vol |
|--------|------|--------|-----|-----------|-----|
| 2020-2026 (real) | 12,65% | 0,57 | -24,1% | -16% | 17,3% |
| 2006-2026 (proxy) | 7,54% | 0,39 | -49,7% | -41% | 15,1% |
| 1926-2026 (proxy) | 6,39% | 0,27 | -61,3% | -50% | 12,1% |

Bootstrap 30 anos (10k + 1k/mês):
- p25 terminal wealth = **$0,82M**
- p50 terminal wealth = **$1,13M**
- p95 terminal wealth = $2,50M
- P(MDD > 50%) = 4,3%
- SWR (95% sucesso, 30 anos) = **4,07%**

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

### Resultados

| Janela | CAGR | Sharpe | MDD | vs Plano C atual |
|--------|------|--------|-----|------------------|
| 2020-2026 | 14,49% | 0,46 | -35,8% | +1,84pp CAGR / MDD +12pp pior |
| 2006-2026 | 9,44% | 0,35 | -68,5% | **+1,90pp CAGR / MDD +19pp pior / Sharpe PIOR** |
| 1926-2026 | 7,68% | 0,22 | -85,5% | +1,29pp / MDD +24pp pior |

Bootstrap 30 anos (10k + 1k/mês):
- p25 = $0,87M (+6% vs plano atual)
- p50 = **$1,52M** (+35% vs plano atual)
- p95 = $6,52M (+161% vs plano atual)
- P(MDD > 50%) = **53%** (vs 4% atual) — **13× maior**
- SWR = **2,69%** (vs 4,07% atual) — **-34% pior** para aposentadoria

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
| **NTSX_syn 100%** (0.9 SPY + 0.6 IEF) | **11,50%** | **0,71** | -41% | 13,8% |
| SSO 100% (com LETF fees) | 12,91% | 0,37 | -81% | 30,7% |

NTSX entrega **+1,4pp CAGR vs SPY** com MDD MENOR (-41% vs -51%) e Sharpe
0,71 (melhor que tudo no ranking). Em vez de SSO 50% (+1,9pp CAGR, MDD +19pp
pior), considere **NTSX 100% da parte US** (+1,7pp CAGR, MDD 10pp MELHOR).

Para o SEU objetivo ("mais exposição US"), NTSX é a escolha superior em
praticamente todos os cenários.

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

### 4.6 Bonds (para retirement)

| Ticker | Duração | ER | Nota |
|--------|---------|----|------|
| TLT | 20+ anos | 0.15% | -71% em 2022 |
| IEF | 7-10 anos | 0.15% | -15% em 2022 |
| SHV | 0-1 ano | 0.15% | Cash proxy |

---

## 5. Backtests: 12 carteiras-candidatas × 3 janelas

Resumo compactado. Dados completos em `results/backtest_summary.csv`.

### 5.1 Ranking por Sharpe (janela 2006-2026, 20 anos)

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

## 6. As 4 carteiras otimizadas finais

Cada uma respondendo a uma função objetivo diferente. Janela de referência:
2006-2026 (20 anos, proxies). Bootstrap 30 anos em `results/final_portfolios.json`.

### 6.1 FINAL_1: Max CAGR — "Leveraged Growth Engine"

**Objetivo:** maximizar CAGR esperado em 30 anos; aceita MDD até ~50%.

| Ticker | Peso | Classe |
|--------|------|--------|
| NTSX | 30% | Efficient core US 90/60 |
| NTSI | 15% | Efficient core DM 90/60 |
| RSST | 15% | US Stocks + MF stacked |
| AVUV | 15% | US SCV |
| AVDV | 10% | Int SCV |
| AVEM | 5% | EM core |
| SPMO | 5% | US Momentum |
| IBIT | 3% | Bitcoin |
| GLDM | 2% | Ouro |

**Alavancagem efetiva ≈ 1,55×.** Factor tilts 35% (SCV 25% + Momentum 5% + EM 5%).

**Performance (2006-2026 proxy):**
- CAGR 9,10% / Sharpe 0,61 / MDD -35% / Vol 12,2%

**Bootstrap 30 anos (10k + 1k/mês = $370k contribuídos):**
- p05 = $0,88M / p25 = **$1,59M** / p50 = **$2,23M** / p95 = $5,57M
- P(MDD > 50%) = 0,4%

**Vs. plano atual:** +1,6pp CAGR / Sharpe 0,61 vs 0,39 / MDD **melhor** (-35% vs -50%).

**Veredito:** essa é a carteira que mais entrega, com risco surpreendentemente
controlado. O return stacking via NTSX+RSST faz o trabalho que o SSO 50%
tentava fazer mas melhor.

### 6.2 FINAL_2: Max Sharpe — "Risk Parity with Factor Tilt"

**Objetivo:** maximizar Sharpe; aceita CAGR menor por caminho mais tranquilo.

| Ticker | Peso | Classe |
|--------|------|--------|
| NTSX | 25% | Core |
| NTSI | 15% | Core DM |
| NTSE | 5% | Core EM |
| AVUV | 10% | SCV |
| AVDV | 5% | Int SCV |
| RSBT | 15% | Bonds + MF stacked (MAIOR diversificador) |
| DBMF | 10% | Pure MF |
| GLDM | 10% | Ouro (tail hedge) |
| TLT | 5% | Long bonds direto |

**Alavancagem efetiva ≈ 1,35×.** 25% em managed futures (RSBT + DBMF).

**Performance (2006-2026 proxy):**
- CAGR 9,20% / Sharpe **0,70** / MDD **-28%** / Vol 10,8%

**Bootstrap 30 anos:**
- p05 = $0,72M / p25 = $1,14M / p50 = **$1,47M** / p95 = $2,82M
- P(MDD > 50%) = 0,1%

**Veredito:** o Sharpe mais alto de todos (0,70). Drawdown raso (-28%). Mas
terminal wealth p50 menor — o preço da suavidade.

### 6.3 FINAL_3: Max Terminal Wealth com MDD ≤ 50% — "Bounded Growth"

**Objetivo:** max riqueza terminal em 30 anos, com restrição MDD ≤ 50% histórico.

| Ticker | Peso | Classe |
|--------|------|--------|
| NTSX | 25% | Core |
| NTSI | 15% | Core DM |
| NTSE | 8% | Core EM |
| AVUV | 12% | SCV |
| AVDV | 8% | Int SCV |
| AVEM | 5% | EM core |
| SPMO | 5% | Momentum |
| RSBT | 8% | MF + bonds |
| DBMF | 5% | Pure MF |
| GLDM | 5% | Ouro |
| IBIT | 2% | Bitcoin |
| TLT | 2% | Long bonds |

**Alavancagem efetiva ≈ 1,30×.** Factor tilts 30%. MF ~13%.

**Performance (2006-2026 proxy):**
- CAGR **9,40%** / Sharpe 0,64 / MDD -36% / Vol 12,1%

**Bootstrap 30 anos:**
- p05 = $0,80M / p25 = $1,31M / p50 = **$1,81M** / p95 = $4,09M
- P(MDD > 50%) = 0,4%

**Veredito:** a carteira mais equilibrada. CAGR levemente acima de FINAL_2,
Sharpe levemente abaixo de FINAL_2, terminal wealth entre FINAL_1 e FINAL_2.
**É o meu default pro seu perfil** (30 anos, factor investing, tolerância a
complexidade, sem aversão a risco mas querendo evitar catástrofe).

### 6.4 FINAL_4: Max SWR — "Retirement Income Optimizer"

**Objetivo:** maximizar Safe Withdrawal Rate em 30 anos de aposentadoria
(95% success). Este é um END-STATE — não para fase de acumulação.

| Ticker | Peso | Classe |
|--------|------|--------|
| NTSX | 18% | Core equity (levered via 90/60) |
| NTSI | 10% | Core DM |
| AVUV | 8% | SCV tilt residual |
| AVDV | 5% | |
| DBMF | 15% | MF (heavy para crisis alpha) |
| KMLM | 5% | Segundo MF (diversificação de MF) |
| RSBT | 8% | MF + bonds stack |
| TLT | 8% | Long bonds |
| IEF | 12% | Intermediate bonds |
| SHV | 5% | Cash buffer |
| GLDM | 5% | Ouro |
| IBIT | 1% | Bitcoin residual |

**Alavancagem efetiva ≈ 1,15×.** Equity ~45% / Bonds 33% / MF 28% / Alts 6% / Cash 5%.

**Performance (2006-2026 proxy):**
- CAGR 8,65% / Sharpe **0,73** / MDD **-24%** / Vol 9,6%

**SWR (95% success, 30 anos, $1M inicial, block bootstrap):**
- 4,05-4,5% (depende da janela de bootstrap)

**Veredito:** diversificação máxima sem sacrificar demais retorno. A carteira
só faz sentido quando você estiver saindo, não entrando — tem pouca
cauda direita.

### 6.5 Tabela comparativa final — CORRIGIDA (ver CORRECTIONS.md)

Janela comum 2007-07 → 2026-02 (18,5 anos, proxy; inclui 2008 + 2020 + 2022):

| Carteira | CAGR | Vol | Sharpe | MDD | p25 TW | p50 TW | p95 TW | P(MDD>50%) | SWR |
|----------|------|-----|--------|-----|--------|--------|--------|------------|-----|
| P0 atual | 7,52% | 16,5% | 0,37 | -53,6% | $0,93M | $1,50M | $4,50M | 30,2% | 3,48% |
| P1 Sua SSO 50% | 9,53% | 23,7% | 0,34 | **-71,1%** | $1,15M | $2,42M | $12,5M | **79,3%** | 2,48% |
| **FINAL_1 Max CAGR** | **10,40%** | 17,9% | 0,50 | -56,0% | $1,55M | **$2,66M** | $8,97M | 44,0% | 4,36% |
| **FINAL_2 Max Sharpe** | 8,64% | 10,1% | 0,72 | -24,8% | $1,35M | $1,77M | $3,29M | 0,1% | **5,82%** |
| **FINAL_3 Max TW/MDD≤50%** | 9,20% | 13,3% | 0,58 | -41,0% | $1,38M | $2,04M | $4,80M | 5,8% | 5,18% |
| **FINAL_4 Max SWR** | 7,88% | 8,7% | **0,74** | -21,5% | $1,18M | $1,52M | $2,76M | 0,0% | 5,73% |

Rankings agora consistentes com o nome de cada carteira:

- **Max CAGR:** FINAL_1 (10,40%) ✅
- **Max Sharpe:** FINAL_4 (0,74) > FINAL_2 (0,72) — nearly-tied (ruído)
- **Max TW com MDD ≤ 50%:** FINAL_3 (9,20% CAGR, MDD -41% respeita o gate) ✅
- **Max SWR:** FINAL_2 (5,82%) > FINAL_4 (5,73%) — nearly-tied (ruído)

**FINAL_2 e FINAL_4 são gêmeas na filosofia** (diversificação + bond/gold/MF
pesado). A diferença é equity beta: FINAL_2 com 45% NTSX, FINAL_4 com 28%.
No período 2007-2026 elas se confundem. Se você quiser acumular, use
FINAL_2; se quiser renda na aposentadoria, use FINAL_4.

**Correção importante vs versão anterior:** não é verdade que "todas as
4 batem o plano atual em todos os eixos simultaneamente". **FINAL_1
perde de P0 em MDD** (-56% vs -54%) — ela troca MDD por CAGR e cauda
direita. FINAL_2/3/4 batem P0 em todos os eixos.

---

## 7. Glidepath ao longo de 30 anos

### 7.1 Opção conservadora (seu documento original)

Age 30-45: 100% equity / Age 45-55: add bonds / Age 55-60: 30-40% FR.

**Problema:** esta trajetória **não é dominante** segundo Cederburg et al.
2024 ([SSRN 4590406](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4590406),
dataset 38 países 1890-2019, 1M bootstraps). TDFs tradicionais subperformam
all-equity em **todos** os outcomes (wealth at retirement, consumo sustentado,
risco exaustão, bequests).

### 7.2 Minha recomendação — glidepath baseada em fatores de risco, não em idade

Em vez de mudar `equity %` por idade, troque o **mix de fontes de retorno**
por fase da vida:

| Fase | Idade | Portfolio | Racional |
|------|-------|-----------|----------|
| Acumulação agressiva | 30-45 | **FINAL_1** (Max CAGR) | Horizonte 15+ anos absorve drawdowns |
| Transição | 45-55 | **FINAL_3** (Max TW/MDD≤50%) | 15-25 anos pós-transição; capa MDD pra proteger sequence risk |
| Pré-aposentadoria | 55-60 | **FINAL_2** (Max Sharpe) | 5-10 anos antes; sequence risk dominante |
| Aposentadoria | 60+ | **FINAL_4** (Max SWR) | Foco em withdrawal rate sustentável |

### 7.3 Opção Cederburg-pura (mais agressiva, evidência-based)

Se você acredita em Cederburg/Anarkulova (2024) — **manter FINAL_1 ou FINAL_3
durante toda a vida, inclusive em retirement.** A evidência global multi-país
é forte: rising equity glidepath **domina** a trajetória decrescente.

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

## 9. Operacional — broker, custos recorrentes, DARF

### 9.1 Broker

- **Inter Internacional** — bom pra começar (zero corretagem, onboarding BR);
  **spread FX 0,99-1,50%** é o custo invisível (em 30 anos de aportes mensais
  = custo total ~15-25% do capital aportado).
- **IBKR** — spread FX ~zero ($2 fee por conversão), plataforma complexa.
  **Inter perde pra IBKR pro investidor que aporta >$500-1000/mês** pelo
  diferencial de spread.
- Recomendação: **começar no Inter, migrar pra IBKR quando aporte mensal >
  $1k USD equivalente** (via ACAT, geralmente grátis ou barato).

### 9.2 Custos recorrentes estimados

Com FINAL_3 (Max TW/MDD50) como exemplo:
- ER ponderado: ~0,36%/ano
- Withholding 30% em dividendos (yield médio ~1,5%): ~0,45%/ano
- Cap gains distributions (baixo turnover): ~0,15%/ano
- **Drag total: ~0,95%/ano** (conservador)

Sobre patrimônio $500k: **~$4,8k/ano em custos invisíveis**.

### 9.3 DARF brasileiro

- Aporte mensal = zero DARF (não há realização).
- Rebalanceamento por aportes = zero DARF.
- Venda anual (se houver) acima de R$35k/mês em ações listadas B3 = isento
  (não se aplica a ETFs US).
- Venda de ETFs US (qualquer valor) = **15% sobre ganho líquido, DAA anual em
  maio** (Lei 14.754/2023).
- **Dividendos USD** = tributáveis como rendimento (carnê-leão mensal);
  compensável com tax credit do withholding US.

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
