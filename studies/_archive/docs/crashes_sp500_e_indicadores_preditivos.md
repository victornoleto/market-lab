# Crashes do S&P 500 e Indicadores Preditivos

Síntese consolidada sobre as maiores quedas históricas do mercado acionário americano e o estado da arte em literatura sobre sinais/indicadores de previsão de crashes, com foco em aplicabilidade quantitativa.

---

## Parte 1 — Maiores quedas do S&P 500

Drawdowns pico-ao-vale em termos nominais, ordenados por severidade:

| # | Evento | Período | Drawdown | Duração | Tempo p/ recuperar |
|---|--------|---------|----------|---------|--------------------|
| 1 | Grande Depressão | set/1929 – jun/1932 | ~82-86% | 996 dias | >25 anos |
| 2 | Crise Financeira Global | out/2007 – mar/2009 | ~57% | 407 dias | Até abr/2013 |
| 3 | Dot-Com | mar/2000 – out/2002 | ~49% | 685 dias | ~13 anos |
| 4 | Bear market anos 70 | 1973-74 | ~48% | — | — |
| 5 | Black Monday | 19/out/1987 | -20,47% em 1 dia | 54 dias no total | Jul/1989 |
| 6 | COVID Crash | fev-mar/2020 | -34% | 32 dias (o mais rápido da história) | ~5 meses |
| 7 | Bear market 2022 | 2022 | ~-25% | — | — |

### Fatos estruturais

- Desde 1928, o S&P 500 passou cerca de **40% de todos os dias de pregão em drawdown** em relação a um pico anterior. Drawdown é o estado normal, não a exceção.
- Foram **15 bear markets** (>20%) desde 1928.
- O Black Monday de 1987 foi a maior queda percentual em um único dia, mas o índice **fechou o ano positivo**.
- O COVID Crash foi o bear market mais rápido já registrado.

---

## Parte 2 — Indicadores e papers sobre previsão de crashes

### A) Valuation — Campbell & Shiller / CAPE

**Papers de referência:**
- Campbell & Shiller (1988) — *Stock Prices, Earnings, and Expected Dividends*
- Shiller & Jivraj (2017) — *The Many Colours of CAPE*
- Haghani & White (2024) — P-CAPE (ajusta por payout ratio)

**Fórmula:**
$$CAPE_t = \frac{P_t}{\frac{1}{10}\sum_{i=0}^{9} E_{t-i}^{real}}$$

**Excess CAPE Yield (Shiller, 2020):**
$$ECY_t = \frac{1}{CAPE_t} - r_t^{10y,real}$$

**Equação de forecast:**
$$r_{t \to t+10}^{real} = a + b \cdot \ln(CAPE_t) + \varepsilon_t$$

**Poder preditivo:** log(CAPE) tem correlação > -80% com retornos reais 10-20 anos à frente (base Ibbotson, 90 anos) e -58% na base Shiller de 135 anos.

**Marcos históricos:** CAPE > 25 só ocorreu em três períodos antes de 2010 — 1929, 1999 e 2007 — todos seguidos de grandes quedas.

**Limitação crítica:** NÃO é tool de timing. CAPE ficou > 25 durante quase toda a década de 2010 sem crash. Útil para dimensionamento estratégico e rotação entre regiões, não para entry/exit.

---

### B) Yield Curve — Estrella & Mishkin

**Papers de referência:**
- Estrella & Mishkin (1996) — *The Yield Curve as a Predictor of U.S. Recessions*
- Estrella & Mishkin (1998) — *Predicting U.S. Recessions: Financial Variables as Leading Indicators*
- Wright (2006, Fed) — adiciona fed funds rate
- Hamilton & Kim (2002) — decomposição expectations vs. term premium
- Johansson & Meldrum (2018, Fed) — ACM-adjusted spread

**Modelo probit canônico:**
$$P(R_{t+12} = 1) = \Phi(\alpha + \beta \cdot TS_t)$$

onde $TS_t = y_t^{10y} - y_t^{3m}$, $\beta \approx -0.65$.

**Thresholds de Estrella-Mishkin:**
- Spread ≈ -0.8 p.p. → ~50% probabilidade de recessão
- Spread ≈ -2.4 p.p. → ~90% probabilidade de recessão

**Dados prontos:** NY Fed publica a probabilidade mensal em `newyorkfed.org/research/capital_markets/ycfaq` (CSV livre).

**Falha recente:** A inversão de 2022-2024 sem recessão técnica é o maior desafio empírico do modelo em 50 anos. Hipóteses incluem distorção de term premium por QE/QT, resiliência atípica do consumidor pós-COVID, ou recessão adiada.

**Conclusão prática:** Sinal de prazo longo (12-24 meses de lag), com falso positivo recente. Precisa de **confirmação** por outros indicadores — não usar isolado.

---

### C) Credit Spreads — Excess Bond Premium (Gilchrist & Zakrajšek)

**Paper de referência:** Gilchrist & Zakrajšek (2012) — *Credit Spreads and Business Cycle Fluctuations*, AER 102(4).

Provavelmente o indicador macro mais sólido da literatura pós-2012.

**Construção do GZ Spread (bond a bond):**
$$S_{it}^{GZ} = y_{it}^{corp} - y_{it}^{synth}$$

onde $y_{it}^{synth}$ é o yield de um título sintético livre de risco que **replica exatamente os cash flows** do bond corporativo, descontando pela curva zero-coupon de Treasuries (Gürkaynak, Sack & Wright, 2007). Diferente do BAA-AAA tradicional, evita viés de duration e composição setorial.

**Decomposição em default + EBP:**
$$\ln S_{it}^{GZ} = \beta' \mathbf{DD}_{it} + \gamma' \mathbf{Z}_{it} + \varepsilon_{it}$$

onde $\mathbf{DD}_{it}$ é *distance-to-default* (Merton KMV). O EBP é:

$$EBP_t = \frac{1}{N_t}\sum_{i} \left(S_{it}^{GZ} - \hat{S}_{it}^{GZ}\right)$$

**Insight-chave:** O poder preditivo dos credit spreads para recessões é **inteiramente devido ao EBP**, não ao componente default. Crises vêm de choques na risk-bearing capacity do setor financeiro, não de piora fundamental prévia.

**Modelo probit:**
$$P(NBER_{t+12} = 1) = \Phi(\alpha + \beta_1 \cdot TermSpread_t + \beta_2 \cdot EBP_t)$$

**Dados prontos:** Fed publica série mensal em `federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv`, começando em 1973. Livre, CSV direto.

**Cuidado:** A série tem *vintage issues* — é revisada. Para backtest honesto, use vintages do ALFRED (St. Louis Fed).

**Também relevantes:**
- High Yield Spread: antecipou toda recessão americana desde 1970; abertura de 300 bps da mínima recente = sinal histórico de correção
- TED spread (picos antes de 2008)
- Baa-Aaa spread (Moody's)

---

### D) Volatilidade e opções

**Papers:**
- Bollerslev, Tauchen & Zhou (2009) — *Expected Stock Returns and Variance Risk Premia*

**Indicadores:**
- **VIX** — acima de 30 historicamente = stress; acima de 35 = crisis
- **VIX term structure** — backwardation (VX1 > VX2) tipicamente precede selloffs de 5-10%
- **VVIX** — volatilidade da volatilidade
- **Put/Call ratio** — extremos marcam turning points
- **SKEW index** — probabilidade implícita de eventos de cauda

**Caveats:**
- VIX é **coincidente**, não leading — sobe durante, não antes
- Backwardation dá sinal com lag curto (dias a semanas)

---

### E) LPPLS — Log-Periodic Power Law Singularity (Sornette et al.)

A escola mais "engenheirável" em termos de sinal acionável de preço.

**Papers fundamentais:**
- Johansen, Ledoit & Sornette (1999, 2000) — *Crashes as Critical Points*
- Sornette (2003) — *Why Stock Markets Crash* (livro, Princeton)
- Filimonov & Sornette (2013) — *A Stable and Robust Calibration Scheme of the LPPL*
- Sornette et al. (2015) — *Real-Time Prediction and Post-Mortem Analysis of the Shanghai 2015 Bubble*
- Demos & Sornette (2017), Filimonov et al. (2017) — sloppiness e profile likelihood
- Shu & Zhu (2019) — CMA-ES para calibração

#### E.1 Formulação original (JLS)

$$\ln[p(t)] = A + B(t_c - t)^m + C(t_c - t)^m \cos[\omega \ln(t_c - t) - \phi]$$

Parâmetros:
- $t_c$ = *critical time* (momento esperado do crash)
- $m \in (0, 1)$ = expoente power-law; garante crescimento super-exponencial
- $\omega$ = frequência angular das oscilações log-periódicas
- $\phi$ = fase
- $A, B, C$ = escala

**Interpretação comportamental:** captura positive feedback loop de herding competindo com negative feedback de contrarians.

#### E.2 Calibração Filimonov-Sornette (2013)

Reformula para reduzir de 4 não-lineares ($t_c, m, \omega, \phi$) para 3 ($m, \omega, t_c$), substituindo $C$ e $\phi$ por $C_1 = C\cos\phi$ e $C_2 = C\sin\phi$:

$$\ln p(t) = A + B(t_c-t)^m + C_1(t_c-t)^m\cos[\omega\ln(t_c-t)] + C_2(t_c-t)^m\sin[\omega\ln(t_c-t)]$$

Fixando $(m, \omega, t_c)$, os lineares saem por OLS fechado. Busca no espaço 3D via multi-start ou CMA-ES.

#### E.3 Filter conditions para validar fit

```
m ∈ [0.01, 0.99]
ω ∈ [2, 25]              (Johansen: tipicamente ~6.36)
t_c próximo ao fim da janela
B < 0                    (bolha positiva; B > 0 para anti-bolha)
|C| / |B| < 1            (restrição de hazard rate não-negativo)
Damping: m|B| / (ω|C|) ≥ 1
Oscilações até t_c ≥ 2.5
```

#### E.4 LPPLS Confidence e Trust Indicators

- **Confidence:** fração de janelas (30-750 dias, ~142 janelas) cujas calibrações satisfazem as filter conditions. Valor perto de 1 = padrão robusto a escolha de $\Delta t$.
- **Trust:** bootstrap dos resíduos + verificação de que fração das séries sintéticas ainda satisfaz. Mais conservador.

#### E.5 Implementação prática

Biblioteca Python `lppls` (Boulder-Investment-Technologies):

```python
from lppls import lppls
obs = np.array([time_ordinal, log_price])
model = lppls.LPPLS(observations=obs)
res = model.mp_compute_nested_fits(
    workers=8, window_size=120, smallest_window_size=30,
    outer_increment=1, inner_increment=5, max_searches=25
)
# res é DataFrame com pos_conf, neg_conf por data
```

Custo computacional alto — roda bem em frequência diária/semanal, não em tick.

#### E.6 Track record e críticas

**Chamadas ex-ante:**
- Pico do petróleo (julho/2008)
- Shanghai (agosto/2009)
- Bolha chinesa de 2015

**Críticas:**
- Brée, Challet & Perduboi (2013); Chang & Feigenbaum (2006) — muitos parâmetros "universais" ($\omega \approx 6.36$) foram ajustados post-hoc
- Alta taxa de falso positivo

**Uso correto:** sinal condicional, não gatilho. Confidence alto + EBP subindo + yield curve invertida → de-risk gradual.

---

### F) Early Warning Signals (Critical Slowing Down)

**Base teórica:** Scheffer et al. (2009) — *Early-warning signals for critical transitions*, Nature.

**Matemática:** em sistemas dinâmicos próximos a bifurcação, o autovalor dominante $\lambda \to 0$, e portanto:
- Autocorrelação lag-1: $\rho_1 \to 1$
- Variância: $\text{Var}(x) \to \infty$
- Skewness e kurtosis crescem

**Aplicação a mercados:**
```
AR(1)_t = corr(r[t-w:t], r[t-w-1:t-1])
Var_t   = var(r[t-w:t])
```

Tendência crescente simultânea = early warning.

**Aplicações recentes:**
- Dakos et al. (2012) — mercados têm menos sinais consistentes de CSD que ecologia
- Diks, Hommes & Wang (2019) — CSD apareceu antes de 1987, 2000, 2008, com alta taxa de falso positivo

**Estado da arte — Multiplex Recurrence Networks:**
- Guo et al. (2024, EPJ Data Science) — constroem MRNs a partir de retornos multidimensionais dos constituintes; *average mutual information* entre camadas é EWS promissor
- Conceito: quando a rede de correlações entre stocks se torna muito densa (everything correlates to 1), o sistema está fragilizado

---

### G) Machine Learning

**Papers:**
- Chatzis et al. (2018) — *Forecasting stock market crisis events using deep and statistical ML techniques*, Expert Systems with Applications
- Shankar (2025, SSRN) — *ML-Based Early Warning Signals of Market Crashes from Index Price Data*
- Systemic Risk Radar (2025, arXiv 2512.17185) — framework de grafos multicamadas

**Insight comum:** instabilidade sistêmica aparece na **estrutura do mercado** (correlações, clustering, sincronização setorial) antes dos preços.

---

### H) Microestrutura e sentimento

- Baker & Wurgler (2006, 2007) — índice composto de sentimento
- Margin Debt (NYSE/FINRA) — picos extremos em 1929, 2000, 2007, 2021
- Hindenburg Omen — folclore técnico, sem suporte acadêmico robusto

---

## Parte 3 — Framework de composição (regime-switching)

Dada a disciplina de validação (PBO/DSR/WFA), a abordagem defensável é **sizing dinâmico condicional**, não sinal binário de entry/exit.

### 3.1 Sinal composto

$$Risk_t = w_1 \cdot z(EBP_t) + w_2 \cdot z(-TS_t) + w_3 \cdot LPPLS\_Conf_t + w_4 \cdot z(VIX\_term_t) + w_5 \cdot z(CSD_t)$$

onde $z(\cdot)$ é z-score rolling. Normaliza para $[0, 1]$ via sigmoide.

### 3.2 Mapping para allocation

$$leverage_t = leverage_{base} \cdot (1 - \lambda \cdot Risk_t)$$

Com $\lambda \in [0.5, 0.8]$. **Nunca zera exposição** — apenas reduz. Resolve o problema do "custo de estar fora" (perder os 10-20 melhores dias destrói retorno).

### 3.3 Cuidados de validação

- **Small sample crítico:** 5-8 crashes genuínos em 90+ anos. Qualquer hyperparameter tuning destrói o sinal. Grid mínimo.
- **Look-ahead bias:** usar apenas vintages disponíveis na data (ALFRED para EBP). Valuation (CAPE) tem earnings reportados com lag.
- **PBO (Bailey-López de Prado 2014):** combinar variáveis com **ancoragem teórica independente** — crédito (EBP), macro (TS), microestrutura de preço (LPPLS), valuation (CAPE). Se convergem, risco de fitar ruído cai.
- **Combinatorial Purged Cross-Validation** (López de Prado) em vez de k-fold normal — respeita dependência temporal.
- **Deflated Sharpe Ratio:** sempre reportar. Com 50 experimentos, SR in-sample de 1.5 pode virar DSR de 0.3.

### 3.4 Benchmark correto

Não é buy-and-hold do S&P. É **risk parity simples** ou **60/40 rebalanceado**. Se o regime-switching não bate isso em Sharpe e Max Drawdown simultaneamente em WFA, não adiciona valor.

---

## Parte 4 — Reality check

Três limitações estruturais reconhecidas pela literatura:

1. **Small sample:** ~5-8 crashes genuínos no S&P em 90 anos. Modelos calibrados nisso têm grau de liberdade virtualmente zero.

2. **Ex-ante vs. ex-post:** Sornette acertou chamadas públicas, mas também errou várias. A curva inverteu em 2022 sem produzir recessão clássica. CAPE ficou > 30 por quase toda a década de 2010 sem crash.

3. **Custo de estar fora:** perder os 10-20 melhores dias do mercado destrói retorno. Estratégias "sair em sinal e voltar em sinal" precisam de precisão muito alta para bater buy-and-hold após custos.

**Conclusão:** usar indicadores como *inputs* em sizing dinâmico (regime-switching com risk parity condicional) e não como trigger de zeragem total.

---

## Literatura essencial (ordem de prioridade)

1. **Sornette, D. (2003)** — *Why Stock Markets Crash: Critical Events in Complex Financial Systems*. Princeton. (livro-texto)
2. **Gilchrist & Zakrajšek (2012)** — *Credit Spreads and Business Cycle Fluctuations*, AER 102(4).
3. **Filimonov & Sornette (2013)** — *A Stable and Robust Calibration Scheme of the LPPL*, Physica A.
4. **Campbell & Shiller (1988)** — *Stock Prices, Earnings, and Expected Dividends*, JF.
5. **López de Prado (2018)** — *Advances in Financial Machine Learning*. Capítulos 7, 11, 12 e 14.
6. **Scheffer et al. (2009)** — *Early-warning signals for critical transitions*, Nature.
7. **Bailey, Borwein, López de Prado & Zhu (2014)** — *The Probability of Backtest Overfitting*.
8. **Estrella & Mishkin (1998)** — *Predicting U.S. Recessions: Financial Variables as Leading Indicators*.
9. **Shiller & Jivraj (2017)** — *The Many Colours of CAPE*.
10. **Bollerslev, Tauchen & Zhou (2009)** — *Expected Stock Returns and Variance Risk Premia*.

---

## Fontes de dados (gratuitas e prontas)

| Indicador | Fonte | URL |
|-----------|-------|-----|
| EBP (Excess Bond Premium) | Federal Reserve | `federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv` |
| Yield Curve / Term Spread | FRED | `fred.stlouisfed.org` (séries T10Y3M, T10Y2Y) |
| NY Fed Recession Probability | NY Fed | `newyorkfed.org/research/capital_markets/ycfaq` |
| CAPE / Shiller PE | Multpl | `multpl.com/shiller-pe` |
| Vintages (real-time) | ALFRED | `alfred.stlouisfed.org` |
| VIX | FRED | série `VIXCLS` |

---

## Bibliotecas Python úteis

- **`lppls`** (PyPI) — calibração LPPLS com CMA-ES e Confidence indicator
- **`arch`** — GARCH, EGARCH, modelos de volatilidade
- **`statsmodels`** — probit, VAR, cointegração
- **`mlfinlab`** — implementações dos métodos de López de Prado (CPCV, PBO, DSR)
- **`pandas-datareader`** — acesso ao FRED e outras fontes
