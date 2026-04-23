# Construção de Portfólio para Aposentadoria com Factor Investing

> Documento gerado a partir de uma consultoria sobre construção de portfólio de aposentadoria baseado em ETFs domiciliados nos Estados Unidos, com tilts de fatores fundamentados em pesquisa acadêmica.

> **📋 VERSÃO REVISADA (V3.5, 2026-04-23):** este documento foi consolidado
> original. Após análise completa com backtest + revisão de princípios
> estruturais (bonds em moeda de consumo, stacking com overlay
> descorrelacionado, factor tilts balanceados), o design evolui para o
> que está em **`reports/portfolio_aposentadoria_v2/`**. Ver:
>
> - `reports/portfolio_aposentadoria_v2/TLDR.md` — 2-min read da versão atual
> - `reports/portfolio_aposentadoria_v2/ANALYSIS.md` — análise completa ~900 linhas
> - `reports/portfolio_aposentadoria_v2/REVISIONS.md` — audit trail V1→V3.5
>
> Principais diferenças vs este documento original:
>
> 1. **Bonds em BRL (não em USD)**: adicionados na fase de transição aos 45 anos
>    (B5P211, IMAB11, LFTS11, DINF11) — nunca US Treasuries.
> 2. **Stacked alts** (GDE, BTGD) em vez de standalone (GLDM, IBIT).
> 3. **Fator tilts balanceados 15% SCV + 10% Momentum** (ratio 60/40) em vez de
>    25% SCV + 5% Momentum.
> 4. **Glidepath por fase-da-vida**: V3_1 (30-45) → V3_3 (45-55) → V3_2 (55-60) → V3_4 (60+).
> 5. **US Estate Tax alert crítico** (ETFs US-domiciliados >$60k → até 40% tax
>    para não-residente na morte). Mitigação via UCITS irlandeses.

---

## Sumário

1. [Contexto e Objetivos](#1-contexto-e-objetivos)
2. [Análise: Corretora — Inter vs Interactive Brokers](#2-análise-corretora--inter-vs-interactive-brokers)
3. [Análise: VT vs VTI/VXUS vs VTI/VEA/VWO](#3-análise-vt-vs-vtivxus-vs-vtiveavwo)
4. [Análise: Avantis vs Dimensional — AVUS vs DFUS](#4-análise-avantis-vs-dimensional--avus-vs-dfus)
5. [Análise: Por que Momentum "não funcionou" em Emergentes (EEMO)](#5-análise-por-que-momentum-não-funcionou-em-emergentes-eemo)
6. [Análise: SPMO e IDMO — Momentum em US e Developed ex-US](#6-análise-spmo-e-idmo--momentum-em-us-e-developed-ex-us)
7. [Proporção Sugerida para o Portfólio](#7-proporção-sugerida-para-o-portfólio)
8. [Glidepath: Reduzindo Risco ao Longo do Tempo](#8-glidepath-reduzindo-risco-ao-longo-do-tempo)
9. [BTGD: Bitcoin + Gold em um Único ETF](#9-btgd-bitcoin--gold-em-um-único-etf)
10. [Portfólio Consolidado Sugerido](#10-portfólio-consolidado-sugerido)
11. [Balanceamento entre SCV e Momentum](#11-balanceamento-entre-scv-e-momentum)
12. [Considerações Finais](#12-considerações-finais)

---

## 1. Contexto e Objetivos

### Perfil do Investidor

- **Idade atual:** 30 anos
- **Objetivo de aposentadoria:** 60 anos (horizonte de 30 anos)
- **Nacionalidade:** Brasileiro
- **Corretora considerada:** Inter (principal) / Interactive Brokers (alternativa)
- **Abordagem:** Factor investing baseado em pesquisa acadêmica
- **Veículos:** ETFs domiciliados nos Estados Unidos
- **Tolerância a complexidade:** Alta — interesse genuíno no tema, com planos de canal no YouTube sobre investimentos

### Premissas e Convicções

- **Diversificação global é necessária.** Apesar do desempenho histórico superior dos EUA (VTI: 572,30% vs VXUS: 166,34% acumulado desde 2011), os retornos recentes em 2025 (VTI: 17,10% vs VXUS: 32,35%) reforçam a importância da alocação ex-US diante de mudanças econômicas globais.
- **Factor investing é a abordagem preferida**, com tilts para Small Cap Value (SCV) e Momentum, sustentados por décadas de literatura acadêmica (Fama-French, AQR, Dimensional, etc.).
- **Alocação alternativa em ouro e Bitcoin (~5%)** como hedge e diversificação.
- **O tamanho do aporte é o fator mais determinante**, mas a otimização da carteira é um objetivo pessoal e profissional.

### Dúvidas Centrais

1. Inter ou Interactive Brokers para ETFs americanos?
2. VT vs VTI/VXUS vs VTI/VEA/VWO — qual a melhor estrutura?
3. Avantis ou Dimensional para o core? (AVUS vs DFUS)
4. Por que momentum não funcionou em emergentes (EEMO)?
5. Qual a proporção ideal de SCV e Momentum nos tilts?
6. BTGD (stacked Bitcoin + Gold) vale a pena?
7. Como implementar um glidepath ao longo de 30 anos?

### Portfólio Considerado pelo Investidor

| ETF  | Região / Função                    |
|------|------------------------------------|
| AVUS | US — Core                          |
| SPMO | US — Tilt Momentum                 |
| AVUV | US — Tilt Small Cap Value          |
| AVDE | Developed ex-US — Core             |
| IDMO | Developed ex-US — Tilt Momentum    |
| AVDV | Developed ex-US — Tilt SCV         |
| AVEM | Emergentes — Core                  |

---

## 2. Análise: Corretora — Inter vs Interactive Brokers

Para o caso específico de ETFs domiciliados nos EUA, o **Inter é uma escolha perfeitamente válida**. A IBKR é mais indicada para quem quer acessar não apenas o mercado americano, mas também diversos outros mercados globais, como ETFs domiciliados na Irlanda (UCITS) — o que não é uma necessidade aqui. A grande vantagem da IBKR para europeus é justamente ser o único corretor europeu que facilita o acesso a ETFs americanos através do estatuto de Cliente Profissional Eletivo, contornando a restrição PRIIPs — algo que não se aplica a brasileiros.

Dito isso, a IBKR tem vantagens objetivas:

- **Spreads de câmbio significativamente menores** — a diferença pode ser de 0,5–1,5% por operação versus o Inter, o que ao longo de 30 anos de aportes faz uma diferença considerável.
- Se os aportes mensais forem relevantes (acima de R$ 2–3 mil/mês), a economia no spread pode facilmente justificar a complexidade extra.
- A grande desvantagem é que a plataforma é mais complexa, mas nada que um desenvolvedor não consiga dominar em alguns dias.

### Sugestão Pragmática

Comece pelo Inter para não postergar o início dos investimentos. Se ao longo do tempo os aportes crescerem, migre para a IBKR. O custo de transferência (ACAT) entre corretoras americanas é geralmente gratuito ou barato.

---

## 3. Análise: VT vs VTI/VXUS vs VTI/VEA/VWO

As diferenças são essencialmente de **controle granular** e **custo**:

### VT (Vanguard Total World)

- Simplicidade máxima — um único ETF com ~60% EUA, ~30% developed ex-US e ~10% emergentes, ponderado por market cap.
- **Desvantagem:** sem controle sobre a proporção entre regiões.
- Expense ratio: 0,07% (ligeiramente mais alto que as alternativas combinadas).

### VTI + VXUS

- Controle sobre a proporção US vs ex-US (ex: 50/50 ao invés de 60/40).
- Permite rebalanceamento fiscal mais eficiente (tax-loss harvesting entre os dois).
- Custo combinado mais baixo (~0,04% ponderado).

### VTI + VEA + VWO

- Camada adicional de controle: ajuste separado de developed e emergentes.
- Relevante se emergentes merecem peso acima do market cap.
- Diferença de custo marginal.

### Conclusão

Para o perfil de alguém que gosta do tema e quer otimizar, a separação em pelo menos US/DM/EM faz sentido. Como ETFs da Avantis serão usados como core, essa granularidade já vem naturalmente da seleção de ativos (AVUS / AVDE / AVEM).

---

## 4. Análise: Avantis vs Dimensional — AVUS vs DFUS

### Factor Loadings (Regressão Fama-French)

| ETF  | Rm-Rf | SMB   | HML   | RMW   | CMA   | Descrição                                |
|------|-------|-------|-------|-------|-------|------------------------------------------|
| VTI  | 1.00  | -0.01 | 0.04  | 0.02  | 0.01  | Mercado puro                             |
| DFUS | 1.00  | 0.00  | 0.01  | 0.03  | 0.03  | Muito próximo de VTI, sem tilts reais    |
| AVUS | 1.03  | 0.09  | 0.15  | 0.06  | 0.01  | Tilts significativos para size e value   |
| DCOR | 1.00  | 0.08  | 0.13  | 0.06  | 0.03  | Equivalente DFA do AVUS (US Core Eq. 1)  |

### Distinção-chave

- **DFUS** não tem factor loadings significativos — é essencialmente um substituto do VTI com a vantagem de não seguir um índice (evita front-running).
- **AVUS** tem tilts pronunciados para size, value e profitability.
- **DFAC** (DFA US Core Equity 2) é o mais próximo do AVUS na linha Dimensional, com mais factor tilts que DFUS.

### Sobre as Empresas

- **Avantis** é uma divisão da American Century Investments (fundada em 1958). Abriu em 2019, fundada por ex-funcionários da Dimensional, incluindo Eduardo Repetto (ex co-CEO/CIO da DFA). Atualmente administra 37 fundos com ~$50 bilhões em ativos.
- **Dimensional** existe desde 1981, com ~$539B em AUM. Histórico mais longo e bancada acadêmica mais profunda (laços com University of Chicago, Eugene Fama).

### Diferença Metodológica

Enquanto a Dimensional usa o tradicional **price-to-book**, a Avantis olha o book value menos "intangíveis" (ativos não-físicos como valor de marcas). Isso pode resultar em captura de value premium mais limpa na era moderna, onde intangíveis dominam os balanços.

### Recomendação

**AVUS para o core US.** Tem os tilts integrados desejados, AUM robusto (~$7,6B), e a metodologia é ligeiramente mais moderna.

---

## 5. Análise: Por que Momentum "não funcionou" em Emergentes (EEMO)

### Dados Comparativos (Retornos acumulados desde 2019-09-19)

| ETF  | Tipo           | Retorno Acumulado |
|------|----------------|-------------------|
| VWO  | Core EM        | 74,02%            |
| AVEM | Core EM (tilts)| 109,10%           |
| EEMO | Momentum EM    | 41,21%            |

### Explicações Acadêmicas

1. **Custos de implementação elevados:** Mercados emergentes têm spreads bid-ask maiores, menor liquidez e custos de negociação mais altos. Como momentum requer rebalanceamento mais frequente, esses custos corroem o premium. Assumindo custos de 50 bps (razoável para EM), o retorno de momentum cai drasticamente.

2. **Crashes de momentum assimétricos:** O retorno mensal médio de momentum em estados de queda de mercado (down market states) em EM é de -0,57%, que depois cai para -4,88% quando o mercado melhora. Mercados emergentes experimentam mais estados de queda e recuperações abruptas (crises cambiais, instabilidade política), tornando os crashes de momentum mais frequentes e severos.

3. **Problemas específicos do EEMO:** O ETF gerou retornos negativos em excesso desde 2016, enquanto o fator teórico de momentum long-short em emergentes aumentou quase 100%. Com apenas ~$12M em AUM e volume médio de ~2.500 ações/dia, é um fundo pequeno demais para ser eficiente.

### Conclusão

Evitar momentum em emergentes via ETF. O prêmio teórico existe, mas a implementação via EEMO é péssima. Usar **AVEM como core em EM, sem tilt de momentum**, é a decisão correta.

---

## 6. Análise: SPMO e IDMO — Momentum em US e Developed ex-US

### Dados Comparativos

**US (retornos acumulados desde 2015-10-12):**

| ETF  | Retorno Acumulado |
|------|-------------------|
| VTI  | 288,45%           |
| VOO  | 308,60%           |
| SPMO | 440,51%           |

**Developed ex-US (retornos acumulados desde 2019-09-26):**

| ETF  | Retorno Acumulado |
|------|-------------------|
| VEA  | 105,48%           |
| AVDE | 116,29%           |
| IDMO | 170,15%           |

### Análise

A história é bem diferente de EM. O SPMO (Invesco S&P 500 Momentum) opera em mercado líquido, com custos de implementação baixos, e o momentum premium nos EUA é robusto e bem-documentado. O IDMO segue lógica similar para developed markets.

### Ressalva Importante

Momentum é o fator com **maior turnover** e portanto **menor eficiência fiscal** comparado a value ou profitability. Dividendos de ETFs americanos já sofrem 30% de withholding tax para brasileiros, e momentum ETFs tendem a ter mais distribuições de ganho de capital.

---

## 7. Proporção Sugerida para o Portfólio

### Alocação Geográfica Base (porção em ações)

| Região          | Alocação | Market Cap (~) | Delta    |
|-----------------|----------|----------------|----------|
| EUA             | 55%      | ~60%           | -5%      |
| Developed ex-US | 30%      | ~28%           | +2%      |
| Emergentes      | 15%      | ~12%           | +3%      |

Leve overweight em ex-US, alinhado com a tese de diversificação global.

### Divisão com Tilts por Região

**EUA (55% total):**

| ETF  | Função   | Alocação |
|------|----------|----------|
| AVUS | Core     | 30%      |
| SPMO | Momentum | 10%      |
| AVUV | SCV      | 15%      |

**Developed ex-US (30% total):**

| ETF  | Função   | Alocação |
|------|----------|----------|
| AVDE | Core     | 15%      |
| IDMO | Momentum | 5%       |
| AVDV | SCV      | 10%      |

**Emergentes (15% total):**

| ETF  | Função | Alocação |
|------|--------|----------|
| AVEM | Core   | 15%      |

### Fundamentação para ~25% SCV

- O paper de Ben Felix para a PWL Capital coloca o peso em small stocks em aproximadamente 30% do portfólio modelo.
- Larry Swedroe estima que apenas cerca de 5% dos investidores DIY conseguem manter um tilt de SCV por causa do tracking error.
- Manter SCV em ~25% do equity é um tilt significativo mas não radical.

A pesquisa de Javier Estrada (IESE) demonstra que portfólios com tilts de fatores resultam em benefícios que não podem ser reproduzidos otimizando portfólios de ações/bonds — se um portfólio ações/bonds é otimizado para igualar o retorno de um portfólio com tilts, ele terá maior volatilidade e menor poder de composição.

---

## 8. Glidepath: Reduzindo Risco ao Longo do Tempo

### Fase 1 — Acumulação Agressiva (30–45 anos)

- **100% equities** com os tilts de fator máximos.
- Risco de sequência de retornos não é relevante nessa fase.
- Volatilidade é aliada: mais cotas compradas nas quedas.

### Fase 2 — Transição (45–55 anos)

- Introduzir **renda fixa gradualmente** (~5% ao ano).
- Reduzir proporcionalmente o **momentum** primeiro (mais volátil).
- Manter SCV por mais tempo — o prêmio compensa especialmente em horizontes longos.

### Fase 3 — Pré-aposentadoria (55–60 anos)

- Target de **30–40% renda fixa**.
- Reduzir SCV para ~10–15% do equity.
- **Renda fixa brasileira** (B5P211, LFTB11) como hedge cambial natural, já que as despesas na aposentadoria serão em reais.

### Observação Importante

Como brasileiro, parte significativa do "bond allocation" deveria ser em renda fixa brasileira (Tesouro IPCA+ via B5P211, por exemplo), não em bonds americanos. O risco cambial BRL/USD já é uma aposta implícita da carteira de ações em dólar, e ter renda fixa em reais oferece diversificação genuína.

---

## 9. BTGD: Bitcoin + Gold em um Único ETF

### O que é

O BTGD (STKd 100% Bitcoin & 100% Gold ETF), lançado em outubro de 2024, utiliza contratos futuros e ETPs para empilhar ("stack") 100% de exposição a Bitcoin e 100% a ouro. Com cada dólar investido, o investidor recebe exposição de $2 (alavancado).

### Pontos Positivos

- Correlação entre Bitcoin e ouro nos últimos seis meses é de ~4%, flutuando entre -30% e +40% — o rebalanceamento interno gera um "rebalancing bonus" significativo.
- Tese coerente: ouro (store of value secular, hedge contra inflação) + Bitcoin (store of value digital, adoção crescente).

### Pontos de Atenção

| Aspecto         | BTGD                          | Alternativa (IBIT + GLDM)     |
|-----------------|-------------------------------|-------------------------------|
| Expense Ratio   | 1,05%                         | ~0,20–0,25% (média ponderada) |
| AUM             | ~$94M (pequeno)               | IBIT: $50B+ / GLDM: $9B+     |
| Alavancagem     | Sim (200% exposure)           | Não                           |
| Custos ocultos  | Roll de futuros               | Nenhum                        |
| Controle        | Proporção fixa 50/50          | Ajustável livremente          |

### Recomendação

Para 5% de exposição a ouro/bitcoin, fazer separadamente com **IBIT** (Bitcoin spot, 0,25% ER) + **GLDM** (ouro, 0,10% ER) na proporção desejada (ex: 3% BTC, 2% ouro). Economia de ~0,75% a.a. em fees, sem risco de alavancagem, e com controle sobre a proporção.

---

## 10. Portfólio Consolidado Sugerido

### Alocação Inicial (30 anos, 100% equities + 5% alternatives)

| ETF  | Região / Fator              | Alocação |
|------|-----------------------------|----------|
| AVUS | US Core (tilts integrados)  | 28%      |
| SPMO | US Momentum                 | 10%      |
| AVUV | US Small Cap Value          | 14%      |
| AVDE | DM ex-US Core               | 14%      |
| IDMO | DM ex-US Momentum           | 5%       |
| AVDV | DM ex-US SCV                | 9%       |
| AVEM | EM Core                     | 15%      |
| IBIT | Bitcoin                     | 3%       |
| GLDM | Ouro                        | 2%       |

**Total: 9 ETFs**

### Rebalanceamento

- Com aportes mensais, fazer **rebalanceamento por novos aportes** (comprar o que está mais abaixo do target).
- Rebalanceamento formal (vendas) **uma ou duas vezes por ano**, alinhado com a declaração de IR.

---

## 11. Balanceamento entre SCV e Momentum

### A Pergunta

> Baseado em pesquisa científica, não seria interessante balancear o peso do tilt de SCV e Momentum de forma mais equilibrada?

### A Resposta: Sim — Value e Momentum são o "Casamento Feliz" do Factor Investing

O paper mais relevante é o **"Fact, Fiction, and Momentum Investing"** da AQR (Asness, Frazzini, Israel e Moskowitz):

- Usando dados de Kenneth French para maximizar o Sharpe ratio de um portfólio combinando mercado, size, value e momentum, o **peso ótimo de momentum seria de aproximadamente 38%** do portfólio.
- **Mesmo assumindo retorno esperado de momentum igual a zero**, os benefícios de diversificação ainda justificariam um peso significativo de momentum no portfólio.

### A Correlação Negativa entre Value e Momentum

| Métrica                                      | Valor  |
|----------------------------------------------|--------|
| Correlação HML vs UMD (French, 1927–2013)    | -0,4   |
| Correlação HML vs UMD (Asness & Frazzini)    | -0,7   |

Intuitivamente faz sentido: quando value stocks estão caindo, são justamente as ações "caindo" que momentum está vendendo/evitando, e vice-versa.

### Nuance Importante (Ehsani & Linnainmaa, NBER)

A correlação é condicional ao estado do mercado:

| Cenário                           | Correlação HML vs MOM |
|-----------------------------------|-----------------------|
| Após ano positivo de HML          | +0,22                 |
| Após ano negativo de HML          | -0,57                 |

A diversificação "funciona melhor" exatamente quando value está indo mal — que é quando mais se precisa dela. No entanto, quando um fator se correlaciona negativamente com momentum, tipicamente também é o estado em que o fator não está gerando um prêmio significativo. Os benefícios são reais, mas mais "elusivos" do que a correlação incondicional sugere.

### Alocação Revisada (US como exemplo)

**Antes (menos momentum):**

| ETF  | Alocação |
|------|----------|
| AVUS | 30%      |
| SPMO | 10%      |
| AVUV | 15%      |

**Depois — mais balanceado entre SCV e Momentum:**

| ETF  | Alocação |
|------|----------|
| AVUS | 25%      |
| SPMO | 15%      |
| AVUV | 15%      |

Ou, para quem confia ainda mais na ciência:

| ETF  | Alocação |
|------|----------|
| AVUS | 20%      |
| SPMO | 17%      |
| AVUV | 18%      |

A mesma lógica se aplica ao ex-US developed, balanceando IDMO e AVDV em proporções mais próximas (7–8% cada ao invés de 5%/10%).

### Por que SCV ainda merece um leve edge sobre Momentum na prática

Apesar da teoria sugerir pesos iguais ou até superiores para momentum, na implementação via ETFs long-only:

- **SCV é mais barato** (AVUV: 0,25% vs SPMO: 0,13% — embora SPMO seja mais barato aqui, o turnover implícito é maior)
- **SCV é mais tax-efficient** (menor turnover = menos distribuições de ganho de capital)
- **O prêmio de SCV é mais persistente** em horizontes longos, enquanto momentum pode sofrer crashes abruptos

---

## 12. Considerações Finais

### O que mais importa

O que mais importa é o **tamanho do aporte**. A diferença entre VT puro e um portfólio factor-tilted otimizado pode ser de 0,5–1,5% a.a. em retorno esperado. A diferença entre aportar R$ 2.000/mês vs R$ 5.000/mês é ordens de magnitude maior no resultado final.

### Filosofia do Portfólio

O portfólio montado é:
- **Fundamentado** em décadas de pesquisa acadêmica (Fama-French, AQR, Dimensional/Avantis)
- **Diversificado** por fatores (market, value, size, momentum, profitability) e geografias (US, DM, EM)
- **Implementável** com produtos de alta qualidade e baixo custo relativo
- **Suficientemente complexo** para gerar conteúdo educativo em um canal de YouTube
- **Suficientemente simples** (9 ETFs) para ser gerenciável ao longo de 30 anos

### O Preço a Pagar

O **tracking error é o preço que se paga pelo prêmio de fatores**. Haverá períodos de 3, 5 ou até 10 anos em que SCV subperformará o mercado. A chave é ter convicção baseada em dados para manter o plano.

---

> ⚠️ **Disclaimer:** Este documento não constitui recomendação de investimento personalizada. As análises são de caráter informativo e educacional, baseadas em pesquisa acadêmica e dados públicos. Consulte um profissional financeiro qualificado antes de tomar decisões de investimento.

---

*Documento gerado em 16 de abril de 2026.*
