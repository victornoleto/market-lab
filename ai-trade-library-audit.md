# AI-Trade — Auditoria da Knowledge Base (22 + 9 = 31 livros)

## 1. Mapa de Cobertura Temática

| Área | Livros que cobrem | Profundidade |
|---|---|---|
| **ML financeiro / feature engineering / validação (CPCV, purging)** | #1 López de Prado (AFML) ★★★, #2 López de Prado (ML Asset Mgrs) ★★, #3 Jansen (ML Algo Trading) ★★★ | **Excelente** — AFML é a referência definitiva em triple barrier, meta-labeling, purged k-fold, CPCV. Jansen complementa com pipelines end-to-end em Python. |
| **DSP / análise de ciclos / filtros** | #12 Ehlers (Cybernetic Analysis) ★★★, #14 Ehlers (Cycle Analytics) ★★★, #15 Ehlers (Rocket Science) ★★★ | **Excelente** — três livros do Ehlers = cobertura completa de MESA, filtros adaptativos, Hilbert Transform, indicadores DSP. |
| **Money management / position sizing / Kelly** | #16 Vince (Math of Money Mgmt) ★★★, #17 Vince (Leverage Space) ★★★ | **Muito bom** — Vince é a referência canônica em optimal-f, Kelly generalizado, drawdown control. |
| **Trend following / momentum / rotation** | #7 Carver (Systematic Trading) ★★, #8 Clenow (Trading Evolved) ★★★, #9 Clenow (Stocks on the Move) ★★★, #20 Universal Trend Tactics ★ | **Muito bom** — Clenow cobre trend following com código, Carver adiciona framework de portfolio. |
| **Evidence-based / statistical testing / overfit control** | #4 Aronson (Evidence-Based TA) ★★★, #5 Masters (Stat. Sound Indicators) ★★, #6 Masters (Testing & Tuning) ★★★ | **Muito bom** — Aronson é o gold standard em bootstrap, White's Reality Check, data-mining bias. Masters complementa com permutation testing prático. |
| **Sistemas de trading genéricos / enciclopédia** | #10 Kaufman (Trading Systems & Methods) ★★★, #11 Bulkowski (patterns) ★★ | **Bom** — Kaufman é a enciclopédia mais completa do mercado. Bulkowski é referência em padrões gráficos com estatísticas. |
| **Regime detection / HMM / change-point** | #18 Regime Change ★★, #19 Peterson (Trading on Sentiment) ★ | **Parcial** — #18 cobre o tema diretamente, mas falta rigor acadêmico em HMM/Bayesian switching. |
| **Behavioral / sentiment / alternative data** | #19 Peterson (Trading on Sentiment) ★★ | **Básico** — Peterson cobre sentiment scoring, mas não aprofunda NLP moderno, alt-data pipelines, nem satellite/web-scraping. |
| **Math / DSP / numerical methods (suporte)** | #21 Brunton/Kutz (Data-Driven Science) ★★★, #22 Numerical Recipes ★★★ | **Excelente como suporte** — DMD, SVD, Sparse Sensing (Brunton) + referência numérica completa (NR). |
| **Cybernetic trading (neural nets clássicas)** | #13 Ruggiero (Cybernetic Trading) ★ | **Datado** — foco em redes neurais dos anos 90, útil mais como contexto histórico. |
| **Microestrutura de mercado / execução / slippage** | — | **❌ AUSENTE** → ✅ Harris (draft) |
| **Options / volatility surface / Greeks** | — | **❌ AUSENTE** → ✅ Sinclair |
| **Risk parity / portfolio construction formal** | Carver (#7) toca superficialmente | **⚠️ FRACO** → ✅ Qian |
| **Econometria de séries temporais financeiras (GARCH, cointegração, state-space)** | — | **❌ AUSENTE** → ✅ Tsay 3e + Hamilton |
| **Walk-forward analysis / backtesting rigoroso** | Masters (#6) cobre parcialmente, AFML (#1) traz CPCV | **⚠️ PARCIAL** → ✅ Pardo |
| **Mean reversion / pairs / stat-arb** | — | **❌ AUSENTE** → ✅ Chan (Algo Trading) |
| **Volatility modeling (realized, implied, GARCH)** | — | **❌ AUSENTE** → ✅ Tsay 3e + Sinclair |

---

## 2. Lacunas Críticas Identificadas

### 🔴 Lacunas MUST-HAVE (impactam diretamente a robustez do sistema)

**L1 — Microestrutura de mercado e execução**
Sem entender order flow, bid-ask dynamics e transaction costs, qualquer backtest é ilusório. Especialmente crítico em FX via MT5/XM onde o spread e slippage são reais.

**L2 — Econometria de séries temporais financeiras**
Faltam modelos GARCH, EGARCH, cointegração formal (Johansen), state-space models, Kalman filter aplicado a finanças. Esses são os building blocks para modelar volatilidade e detectar regimes de forma estatisticamente rigorosa.

**L3 — Walk-forward analysis e backtesting formal**
Masters (#6) e AFML (#1) cobrem pedaços, mas falta o tratamento completo: walk-forward optimization, Monte Carlo validation, robustness profiling. Pardo é o framework canônico.

**L4 — Mean reversion / pairs trading / stat-arb**
A biblioteca é forte em trend/momentum mas não tem nenhum livro dedicado a mean reversion. Chan (Algorithmic Trading) é a referência prática com código.

### 🟡 Lacunas NICE-TO-HAVE (expandem o arsenal)

**L5 — Volatility trading / options**
Mesmo sem operar opções diretamente, entender a volatility surface, variance premium e vol forecasting é essencial para regime detection e risk management.

**L6 — Portfolio construction formal / risk parity**
Carver (#7) é bom como framework prático, mas falta a fundamentação quantitativa: mean-variance, Black-Litterman, risk parity, hierarchical risk parity (HRP) do López de Prado.

**L7 — Forex-specific microstructure**
A maioria dos livros é equity-centric. Para FX via MT5, entender liquidity provision, quote-driven markets e carry/momentum em currencies tem nuances próprias.

---

## 3. Lista Priorizada de Recomendações (9 títulos adquiridos)

### 🏆 #1 — MUST-HAVE

**Ernest P. Chan — *Algorithmic Trading: Winning Strategies and Their Rationale***
- **Ano/Ed:** 2013, Wiley, 1ª edição
- **Lacuna:** L4 (mean reversion / stat-arb) + complementa L3 (backtesting prático)
- **Por que é canônico:** Chan é um dos practitioners mais citados em QuantStackExchange e blogs quant. Cobre mean reversion (ADF, Hurst, cointegração, Kalman filter), momentum, e Kelly prático com código MATLAB/Python adaptável. Citado extensivamente por López de Prado e Jansen.
- **Nível:** Intermediário
- **Sobreposição:** Alguma com Jansen (#3) em conceitos gerais, mas Chan é muito mais profundo em stat-arb e pairs trading especificamente. Vale a pena.
- **Link:** [Amazon](https://www.amazon.com/Algorithmic-Trading-Winning-Strategies-Rationale/dp/1118460146)

---

### 🏆 #2 — MUST-HAVE

**Ruey S. Tsay — *Analysis of Financial Time Series*, 3ª edição**
- **Ano/Ed:** 2010, Wiley, 3ª edição
- **Lacuna:** L2 (econometria de séries temporais — GARCH, cointegração, state-space, VaR)
- **Por que é canônico:** Tsay é professor na Chicago Booth, Fellow da ASA e IMS. O livro é o textbook padrão em programas de mestrado/doutorado em finanças quantitativas. Cobre GARCH/EGARCH, volatilidade estocástica, modelos multivariados, MCMC, Kalman filter — tudo com dados reais e código R.
- **Nível:** Intermediário-avançado (requer base em estatística)
- **Sobreposição:** Quase nenhuma — os livros que você tem não cobrem econometria financeira formal. Brunton/Kutz (#21) é DSP/dinâmica, não econometria.
- **Link:** [Wiley](https://www.wiley.com/en-us/Analysis+of+Financial+Time+Series,+3rd+Edition-p-9780470414354) · [Amazon](https://www.amazon.com/Analysis-Financial-Time-Ruey-Tsay/dp/0470414359)

---

### 🏆 #3 — MUST-HAVE

**Robert Pardo — *The Evaluation and Optimization of Trading Strategies*, 2ª edição**
- **Ano/Ed:** 2008, Wiley
- **Lacuna:** L3 (walk-forward analysis, robustness profiling, overfit detection)
- **Por que é canônico:** Pardo literalmente inventou o termo "Walk-Forward Analysis". A 1ª edição (1992, *Design, Testing, and Optimization of Trading Systems*) é um marco no campo. Perry Kaufman (autor do seu #10) escreveu o endorsement. Goldman Sachs e Daiwa são clientes de consultoria de Pardo. Amplamente citado em fóruns como Elite Trader e Wilmott.
- **Nível:** Intermediário
- **Sobreposição:** Complementa Masters (#6) que foca em permutation testing. Pardo foca em walk-forward optimization e profiling — peças diferentes do puzzle anti-overfit.
- **Link:** [Amazon](https://www.amazon.com/Evaluation-Optimization-Trading-Strategies/dp/0470128011) · [Wiley](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119196969)

---

### 🏆 #4 — MUST-HAVE

**Larry Harris — *Trading and Exchanges: Market Microstructure for Practitioners***
- **Ano/Ed:** 2003, Oxford University Press
- **Arquivo:** `trading-and-exchanges-market-microstructure-for-practitioners` (2.551 KB) — ⚠️ versão draft pré-publicação (Mar 2002). Conteúdo substantivo idêntico à edição final; edição publicada não foi encontrada em PDF texto.
- **Lacuna:** L1 (microestrutura de mercado, execução, transaction costs)
- **Por que é canônico:** Harris foi Chief Economist da SEC e ocupa a cátedra Fred V. Keenan na USC. O *Journal of Investment Management* considera o livro indispensável. É o textbook padrão de microestrutura em MBA/MFE programs. Cobre order types, bid-ask spread economics, market maker behavior, transaction cost analysis — tudo que você precisa para modelar slippage realista no MT5.
- **Nível:** Intermediário (escrito em prosa acessível, pouca matemática pesada)
- **Sobreposição:** Zero com sua biblioteca atual. Nenhum dos 22 livros cobre microestrutura.
- **Link:** [Oxford UP](https://global.oup.com/academic/product/trading-and-exchanges-9780195144703) · [Amazon](https://www.amazon.com/Trading-Exchanges-Market-Microstructure-Practitioners/dp/0195144708)

---

### 🥈 #5 — ALTAMENTE RECOMENDADO

**Ernest P. Chan — *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*, 2ª edição**
- **Ano/Ed:** 2021, Wiley, 2ª edição
- **Lacuna:** Complementa L4 + L6 (frameworks de trading end-to-end, regime-aware optimization, factor models)
- **Por que é canônico:** A 2ª edição (2021) inclui material atualizado sobre ML aplicado, regime shifts, e capital allocation — mais moderno que a 1ª edição de 2009. Amplamente recomendado no QuantStart como primeiro livro para quant retail.
- **Nível:** Intro-intermediário
- **Sobreposição:** Alguma com Chan #1 acima e Jansen (#3). A 2ª edição traz regime change e ML que justificam a aquisição mesmo tendo o #1.
- **Link:** [Amazon](https://www.amazon.com/Quantitative-Trading-Build-Algorithmic-Business/dp/1119800064)

---

### 🥈 #6 — ALTAMENTE RECOMENDADO

**Euan Sinclair — *Volatility Trading*, 2ª edição**
- **Ano/Ed:** 2013, Wiley, 2ª edição
- **Lacuna:** L5 (volatility modeling, variance premium, vol forecasting)
- **Por que é canônico:** Sinclair tem PhD em física (Bristol) e 15+ anos como options trader profissional na Bluefin Trading. O livro é considerado o tratamento mais prático de volatility trading disponível, elogiado por Jesper Andreasen (Danske Markets) e Steve Crutchfield (NYSE Euronext). Cobre realized vs implied vol, Kelly sizing para opções, e vol surface dynamics.
- **Nível:** Intermediário
- **Sobreposição:** Complementa Vince (#16/#17) na parte de sizing, mas o foco em volatilidade é completamente novo para sua biblioteca.
- **Link:** [Wiley](https://www.wiley.com/en-us/Volatility+Trading,+++Website,+2nd+Edition-p-9781118416723) · [Amazon](https://www.amazon.com/Volatility-Trading-Website-Euan-Sinclair/dp/1118347137)

---

### ~~#7 — REMOVIDO~~

**Barry Johnson — *Algorithmic Trading and DMA: An Introduction to Direct Market Access Trading Strategies***
- **Status:** ❌ **NÃO ADQUIRIDO** — único PDF encontrado era scan de imagens (não-OCR), inviável para ingestão na knowledge base sem pipeline de OCR pesada.
- **Ano/Ed:** 2010, 4Myeloma Press
- **Lacuna:** L1 + L7 (execution algorithms, DMA, market impact modeling)
- **Decisão:** Desconsiderado. Harris (#4) já cobre a fundamentação conceitual de microestrutura. Os tópicos específicos de execution algorithms (VWAP, TWAP, implementation shortfall) são menos críticos para swing trading FX via MT5 do que seriam para equities em DMA institucional. Se necessário no futuro, pode ser complementado com papers avulsos do SSRN.

---

### 🥉 #8 — NICE-TO-HAVE

**Marcos López de Prado — papers sobre HRP (Hierarchical Risk Parity)**
- **Título alternativo concreto:** Edward Qian — *Risk Parity Fundamentals*
- **Ano/Ed:** 2016, CRC Press
- **Lacuna:** L6 (portfolio construction / risk parity formal)
- **Por que é canônico:** Qian é Managing Director na PanAgora Asset Management e o nome mais associado ao conceito de risk parity na indústria. O livro formaliza risk budgeting, equal risk contribution, e portfolio construction sem depender de estimativas de retorno esperado.
- **Nível:** Intermediário-avançado
- **Sobreposição:** Carver (#7) toca no tema pragmaticamente, mas Qian é o tratamento matemático formal.
- **Link:** [Amazon](https://www.amazon.com/Risk-Parity-Fundamentals-Edward-Qian/dp/1498738796)

---

### 🥉 #9 — NICE-TO-HAVE

**Stefan Jansen — considerar complementar com Hamilton — *Time Series Analysis***
- **Título:** James D. Hamilton — *Time Series Analysis*
- **Ano/Ed:** 1994, Princeton University Press
- **Lacuna:** L2 complementar (HMM, state-space, regime switching — o capítulo 22 de Hamilton é *a* referência para Markov switching models)
- **Por que é canônico:** Hamilton é o criador do Markov-Switching model (Hamilton, 1989) que é o paper seminal em regime detection econométrico. O livro tem 800+ páginas e é o textbook mais citado em econometria de séries temporais (17.000+ citações no Google Scholar).
- **Nível:** Avançado (pesado em matemática)
- **Sobreposição:** Complementa Tsay (#2 acima) — Tsay é mais aplicado/finança, Hamilton é mais teórico/econométrico. Se tiver que escolher um, Tsay é mais prático para trading.
- **Link:** [Princeton UP](https://press.princeton.edu/books/hardcover/9780691042893/time-series-analysis) · [Amazon](https://www.amazon.com/Time-Analysis-James-Douglas-Hamilton/dp/0691042896)

---

### 🥉 #10 — NICE-TO-HAVE

**Ernest P. Chan — *Machine Trading: Deploying Computer Algorithms to Conquer the Markets***
- **Ano/Ed:** 2017, Wiley
- **Lacuna:** Complementa L3 + L4 (execução automatizada, factor models, intraday momentum, ML aplicado a regime detection)
- **Por que é canônico:** Terceiro livro da trilogia do Chan, foca em deployment real: automação, factor models, e mean reversion/momentum com ML. Menos citado que os dois primeiros, mas traz tópicos práticos como Bayesian optimization de parâmetros e risk indicators.
- **Nível:** Intermediário
- **Sobreposição:** Significativa com Chan #1 e #2 acima — se já comprar os dois primeiros, este é incremental.
- **Link:** [Amazon](https://www.amazon.com/Machine-Trading-Deploying-Computer-Algorithms/dp/1119219604)

---

## 4. Resumo Visual de Prioridades

| # | Livro | Arquivo | Lacuna | Status |
|---|---|---|---|---|
| 🏆 1 | Chan — *Algorithmic Trading* | `Algorithmic Trading - Winning Strategies and Their Rationale 2013` (9.0 MB) | Mean reversion / stat-arb | ✅ |
| 🏆 2 | Tsay — *Analysis of Financial Time Series* 3e | `Analysis of Financial Time Series Third Edition By Ruey S.Tsay` (7.2 MB) | GARCH / econometria / vol | ✅ |
| 🏆 3 | Pardo — *Evaluation & Optimization* | `the-evaluation-and-optimization-of-trading-strategies` (3.3 MB) | Walk-forward / anti-overfit | ✅ |
| 🏆 4 | Harris — *Trading and Exchanges* | `trading-and-exchanges-market-microstructure-for-practitioners` (2.5 MB) | Microestrutura / slippage | ✅ (draft) |
| 🥈 5 | Chan — *Quantitative Trading* 2e | `Quantitative Trading How to Build Your Own Algorithmic Trading Business` (3.6 MB) | Framework end-to-end | ✅ |
| 🥈 6 | Sinclair — *Volatility Trading* | `Volatility Trading, + Website-Wiley (2013)` (3.3 MB) | Vol modeling / options | ✅ |
| ~~7~~ | ~~Johnson — *Algo Trading & DMA*~~ | — | ~~Execution algorithms~~ | ❌ Removido |
| 🥉 8 | Qian — *Risk Parity Fundamentals* | `Risk_Parity_Fundamentals` (6.2 MB) | Portfolio construction | ✅ |
| 🥉 9 | Hamilton — *Time Series Analysis* | `Hamilton Time Series Analysis` (13.3 MB) | HMM / regime switching | ✅ |
| 🥉 10 | Chan — *Machine Trading* | `Machine Trading_ Deploying Computer Algorithms to Conquer The Markets (Ernest Chan 2017)` (1.4 MB) | Deployment / ML prático | ✅ |

---

## 5. Nota sobre a Estratégia de Leitura

Dado o framework anti-overfit de 7 camadas do projeto, a ordem de absorção sugerida é:

1. **Primeiro: Chan (Algorithmic Trading)** — abre o arsenal de mean reversion que a biblioteca não tem, com código prático imediato
2. **Segundo: Pardo** — fecha o gap de walk-forward antes de você começar a codificar backtests na Fase 1
3. **Terceiro: Harris** — calibra as premissas de transaction cost e slippage no MT5/XM antes de qualquer simulação ser confiável
4. **Quarto: Tsay** — fundamenta econometricamente os modelos de volatilidade e regime que vão alimentar as estratégias

Os livros 5-10 podem ser absorvidos em paralelo conforme a necessidade surgir durante o desenvolvimento.

---

## 6. Notas de Aquisição

- **9 de 10 livros adquiridos** em PDF texto (ingestão direta na knowledge base)
- **1 removido** (Johnson — *Algo Trading & DMA*): único PDF disponível era scan de imagens, inviável sem OCR. Lacuna de execution algorithms é secundária para swing trading FX e pode ser coberta com papers avulsos se necessário.
- **Harris** adquirido na versão draft (Mar 2002), conteúdo equivalente à edição publicada (Oxford, 2003). Citações devem referenciar a edição publicada.
- **Total final da knowledge base: 22 originais + 9 novos = 31 livros**

---

## 7. Fontes de Dados para Backtest (FX via MT5)

### Princípio central

Dados ruins invalidam qualquer backtest, independente da sofisticação do framework. Para FX, o problema é agravado pelo fato de ser um mercado descentralizado — não existe um "preço oficial", cada dealer tem seu próprio feed, e o "volume" reportado no MT5 é tick volume do broker, não volume real interbancário.

### Tiers de fontes de dados

**Tier 1 — MT5/XM (gratuito, já disponível)**

O próprio MetaTrader5 fornece dados históricos via `copy_rates_from` na API Python. Vantagem: reflete exatamente os spreads e condições do broker onde as trades serão executadas. Desvantagens: profundidade histórica limitada (geralmente 2-5 anos dependendo do timeframe), dados de dealer (não interbancários), e tick volume não representa volume real. Para swing trading em 1H/4H/Daily, é aceitável como ponto de partida — mas não como única fonte.

**Tier 2 — Fontes gratuitas de qualidade razoável**

| Fonte | Dados | Histórico | Observações |
|---|---|---|---|
| **Dukascopy** (JForex) | Tick + 1min | 2003+ | Considerado superior ao FXCM pela comunidade quant. Boa qualidade. |
| **Histdata.com** | Tick + 1min | 2000+ | Fonte gratuita mais usada por quant retail. Feed FXCM/Gain Capital (viés de dealer). |
| **OANDA API** | Candlestick (REST) | Variável | API limpa e bem documentada. Histórico razoável. |
| **TrueFX** | Tick interbancário | Variável | Dados interbancários reais para histórico mais antigo (gratuito); real-time é pago. |

**Tier 3 — Fontes pagas / institucionais**

Refinitiv (ex-Thomson Reuters), Bloomberg, TickData. Qualidade institucional, mas custo incompatível com capital de $1.000. Overkill para a Fase 0/1 do projeto.

### Estratégia recomendada: validação em duas camadas

1. **Desenvolvimento e validação das estratégias:** usar dados do Dukascopy ou Histdata — maior profundidade histórica, mais dados para cross-validation e walk-forward (Pardo).
2. **Validação final pré-live:** rodar o backtest nos dados do próprio MT5/XM — reflete as condições reais do broker onde a execução vai acontecer, incluindo spreads, gaps e peculiaridades.

Essa abordagem de duas fontes independentes funciona como **check de robustez**: se a estratégia funciona nos dados Dukascopy mas não nos dados XM (ou vice-versa), é um sinal de fragilidade e dependência do feed específico.

### Cuidados críticos (fundamentados na knowledge base)

| Cuidado | Livro de referência | Conceito |
|---|---|---|
| Pré-processamento e stacionariedade dos dados | Tsay (*Analysis of Financial Time Series*) | Testes de raiz unitária, diferenciação, transformações |
| Estrutura de janelas treino/validação/teste | Pardo (*Evaluation & Optimization*) | Walk-forward analysis, robustness profiling |
| Premissas de slippage e transaction costs | Harris (*Trading and Exchanges*) | Bid-ask spread economics, market maker behavior |
| Purging e embargo em cross-validation temporal | López de Prado (*AFML*, #1) | Purged k-fold, CPCV, prevenção de leakage |
| Custos de carry (swap overnight) | Chan (*Algorithmic Trading*) | Impact de financing costs em holding periods |

### Regra inviolável

**Nunca confiar em uma única fonte de dados, e sempre incluir custos de transação realistas (spread + swap + slippage) no backtest. Um backtest sem custos é ficção.**
