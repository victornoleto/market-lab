# Evidence-Based Technical Analysis: Applying the Scientific Method and Statistical Inference to Trading Signals

## Metadata
- **Autor:** David R. Aronson [p.7, p.15]
- **Ano:** 2007 [p.8]
- **Editora:** John Wiley & Sons (Wiley Trading series) [p.6, p.8]
- **Páginas:** 544
- **ISBN:** 978-0-470-00874-4 / 0-470-00874-1 [p.8]
- **Foco principal:** Transformar análise técnica numa ciência observacional rigorosa usando o método científico, inferência estatística e testes robustos contra o viés do data-mining (White's Reality Check e Monte Carlo Permutation).

## 1. Tese Central

TA deve evoluir de uma folk-art baseada em fé para uma ciência observacional rigorosa — "Evidence-Based Technical Analysis" (EBTA). A tese é dupla [Introduction, p.1-7]: (1) a TA subjetiva (chart patterns desenhados à mão, Elliott Wave, Gann, etc.) é "worse than wrong — it is meaningless" [p.5] porque não produz afirmações falsificáveis; (2) a TA objetiva é passível de ser avaliada cientificamente, mas seus resultados históricos são sistematicamente positivamente enviesados pelo data-mining bias [p.1], exigindo testes estatísticos especializados como White's Reality Check e Monte Carlo Permutation [p.239-243; p.325-328] para serem confiáveis.

O livro é dividido em duas partes [p.11]: Parte I (fundamentos metodológicos, psicológicos, filosóficos e estatísticos — capítulos 1-7); Parte II (case study: back-test de 6.402 regras binárias long/short no S&P 500 durante 25 anos — capítulos 8-9).

## 2. Conceitos-Chave

- **EBTA (Evidence-Based Technical Analysis)** — TA restrita a métodos objetivos cujos resultados são avaliados com inferência estatística que controla data-mining bias [p.6-7, p.162-163].
- **Subjective vs. Objective TA** — Subjetiva não pode ser reduzida a algoritmo computerizável e backtestável; objetiva sim [p.5-6, p.16-17].
- **Cognitive content / discernible-difference test** — Uma proposição só pode ser candidata a crença se se sua verdade vs. falsidade produzir diferença observável [p.2-3].
- **Knowledge = justified true belief** — Para ser conhecimento, uma afirmação precisa ser verdadeira e justificada por inferência sólida a partir de evidência [p.4].
- **Binary reversal rule** — Regra que produz sempre +1 (long) ou -1 (short), invertendo de uma para outra em sinais [p.17, p.33].
- **Position bias** — Tendência de uma regra passar mais tempo em um estado (long ou short) devido à assimetria entre suas condições de entrada [p.23-27].
- **Detrending** — Subtrair do retorno diário do mercado o retorno médio diário do período de back-test, criando série com tendência zero. Necessário para eliminar efeito conjugado de position bias × market trend [p.27-28, p.29-30].
- **Look-ahead bias** — Uso de informação no back-test que não estava disponível no momento da decisão (ex.: usar close como sinal e executar ao mesmo close) [p.29-30].
- **Data-mining bias** — Viés positivo sistemático na performance observada da melhor regra quando várias são testadas; a performance observada supera a performance esperada [p.271, p.287].
- **Multiple Comparison Procedure (MCP)** — Paradigma de data mining: testar muitas soluções candidatas e selecionar a melhor por um figure of merit [p.264-265].
- **Channel Breakout Operator (CBO)** — Operador trend-following: sinal long quando série supera o máximo dos últimos n-períodos; short quando fura o mínimo [p.397].
- **Channel Normalization (CN) / Stochastics** — Operador detrending que escala a série de 0-100 conforme posição no range dos últimos n períodos; serve como high-pass filter [p.401-403].
- **Reasoning by representativeness / sample size neglect** — Heurística psicológica que faz o analista perceber padrões em amostras pequenas de dados aleatórios ("crime of small numbers") [p.88-96, p.113].
- **Overconfidence bias** — Tendência documentada de humanos superestimarem a precisão de seu próprio conhecimento/habilidade [p.45-47].
- **Configural thinking** — Tipo de raciocínio que exige integrar múltiplas variáveis simultaneamente — mente humana limitada a ~3 fatores [p.42-44].
- **Null hypothesis (Ho) em rule testing** — A regra não tem predictive power; retorno esperado = 0 em dados detrended [p.166-167, p.182].
- **Sampling distribution** — Distribuição de probabilidade do test statistic (ex.: retorno médio) sob a hipótese nula [p.167-168].
- **Noise rule** — Regra cujos sinais +1/-1 são aleatoriamente pareados com retornos do mercado; usada como benchmark pelo Monte Carlo Permutation [p.239-240].

## 3. Fórmulas / Equações

**Expected Return of a binary reversal rule (no-predictive-power baseline)** [p.26-28]

$$ER = [p(L) \times ADC] - [p(S) \times ADC]$$

- $p(L)$ = proporção do tempo long [p.26]
- $p(S)$ = $1 - p(L)$ [p.26]
- $ADC$ = average daily change of market traded [p.26]
- Implicação: se $ADC = 0$ (mercado detrended), $ER = 0$ qualquer que seja o position bias [p.28].

**Detrending (conversão para log returns) — rule daily return** [p.29-30]

$$\text{Rule daily return} = POS_0 \times \left[ \log\!\left(\frac{O_{+2}}{O_{+1}}\right) - ALR \right]$$

- $POS_0$ = +1 ou -1 na close do dia 0 [p.29]
- $O_{+1}$, $O_{+2}$ = opens dos dias 1 e 2 (evita look-ahead bias; executa no open seguinte ao sinal) [p.29-30]
- $ALR$ = average log return over back-test period [p.30]

**Sample Mean (ponto estimador do retorno esperado)** [p.260]

$$\bar{X} = \frac{\sum_{i=1}^{n} X_i}{n}$$

**Confidence Interval via Bootstrap Percentile Method** [p.250]

$$x = \frac{100 - \text{Confidence Interval Desired}}{2}$$

- Remover os x% superiores e x% inferiores da distribuição bootstrap dos means para obter os bounds [p.250].

**Moving Average Operator** [p.415]

$$MA_t = \frac{\sum_{i=1}^{n} P_{t-i+1}}{n}$$

- Lag de um simple MA = $(n-1)/2$; lag de linear-weighted MA = $(n-1)/3$ [p.400].

**Linear Weighted Moving Average (LMA)** [p.400]

$$WMA_t = \frac{\sum_{i=1}^{n} (n - i + 1) \cdot P_{t-i+1}}{\sum_{i=1}^{n} i}$$

**Channel Normalization Operator (Stochastics)** [p.402]

$$CN_t = \left[ \frac{S_t - S_{\min,n}}{S_{\max,n} - S_{\min,n}} \right] \times 100$$

- $S_t$ = valor da série no tempo t; $S_{\min,n}$ e $S_{\max,n}$ = mínimo e máximo dos últimos n dias [p.402].

**Cumulative Advance-Decline Ratio (CADR)** [p.414]

$$CADR_t = CADR_{t-1} + ADR_t, \quad ADR_t = \frac{adv_t - dec_t}{adv_t + dec_t + unch_t}$$

**Cumulative Net Volume Ratio (CNVR)** [p.415]

$$NVR_t = \frac{upvol_t - dnvol_t}{upvol_t + dnvol_t + unchvol_t}$$

**Divergence Indicator (double channel normalization)** [p.453]

$$DI = CN\left[\, CN(S_1, n) - CN(S_{\&P500}, n),\ 10n \,\right]$$

- Dupla CN necessária porque séries companheiras têm graus distintos de co-movimento com o S&P 500 [p.452-454].

**Artificial Trading Rule Expected Return (usado nos experimentos de data-mining bias)** [p.307-308]

$$ER = ppm \times 3.97 - (1 - ppm) \times 3.97$$

- $ppm$ = probability of profitable month; 3.97% = mean absolute monthly return do S&P 500 de Aug/1928–Apr/2003 [p.308].

**Linear combining rule (complex rule via soma ponderada)** [p.468-469]

$$Y = a_0 + \sum_{i=1}^{k} a_i \cdot r_i$$

- $r_i$ = output da regra i; $a_i$ = peso; $Y$ = output da regra complexa linear [p.469].

**Markowitz/Xu Data-Mining Correction** [p.324]

$$H' = R + B(H - R)$$

- $H'$ = expected return corrigido da melhor regra [p.324]
- $R$ = retorno médio de todas as regras testadas [p.324]
- $H$ = retorno observado da melhor regra [p.324]
- $B \in [0,1]$ = shrinkage factor (menor B = mais shrinkage) [p.324].

## 4. Algoritmos e Pseudocódigo

**White's Reality Check (WRC) — Bootstrap for best-of-N rules** [p.341-343]

```
Input: daily returns of all N rules over T days
Step 1: For each rule i, subtract its mean daily return from every daily return.
        (Centers each rule at zero — imposes Ho: expected return = 0.)
Step 2: Sample T day-indices with replacement (Bootstrap Theorem requires n_resamples = n_obs).
Step 3: For each rule i, compute mean of its centered returns at the resampled indices.
Step 4: Let M = max of these N means. M is one observation of the sampling distribution.
Step 5: Repeat steps 2-4 >= 500-2000 times (case study used 1,999 replications [p.442]).
Step 6: p-value = fraction of M values >= observed mean return of best rule.
Reject Ho if p-value < 0.05.
```

**Monte Carlo Permutation Method (MCP) — Masters/Aronson** [p.255-256, p.341-344]

```
Input: time series of +1/-1 output values for all N rules;
       detrended one-day-forward market returns (length T).
Step 1: Scramble (permute WITHOUT replacement) the T market returns.
        IMPORTANT: use the SAME permutation for all N rules
        (preserves correlation structure among rules).
Step 2: For each rule, multiply its rule output values by the scrambled returns,
        compute the mean → N mean returns per permutation.
Step 3: Take the maximum of those N means → one value for sampling distribution.
Step 4: Repeat steps 1-3 >= 500 times (case study: 1,999).
Step 5: p-value = fraction of maxima >= observed best-rule return.
Notes:
- MCP tests: "all rules pair outputs with returns at random" (not "expected return = 0") [p.343].
- MCP CANNOT produce confidence intervals (no population parameter) [p.265-266].
- MCP handles negative-expected-return rules better than original WRC [p.345-346].
```

**Walk-Forward Testing with 3-segment fold** [p.339, p.473-474]

```
window = [train_set | test_set | validation_set]
for each fold (walking forward in time):
    inner_loop (parameter_search):
        for each parameter combination at fixed complexity:
            fit on train, evaluate on test
    outer_loop (complexity_search):
        repeat inner_loop at increasing complexity levels
        pick best (param, complexity) on test performance
    evaluate chosen rule on validation_set  # unbiased out-of-sample estimate
    slide window forward (no overlap between validation segments across folds)
```

**Head & Shoulders objectification (Chang & Osler, adopted in chapter 3)** [p.151-160]

```
# Step 1 [p.154]: Detect peaks/troughs via zigzag (Alexander) filter with threshold = k * V
#   where V = stddev(daily % change over last 100 days),
#   k ∈ {1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0}.  (10 scales)
# Step 2 [p.155]: Identify 5 pivots A, B, C, D, E (3 peaks, 2 troughs) with C > A and C > E.
# Step 3 [p.155]: Prior-trend rule — left shoulder A > prior peak; left trough B > prior trough.
# Step 4 [p.155-156]: Vertical symmetry — A > Y and E > X; B < Y and D < X
#   where X = midpoint(AB), Y = midpoint(DE).  (excludes steep necklines)
# Step 5 [p.156-157]: Horizontal symmetry — distance(C to nearest shoulder) ≤ 2.5 x distance to other shoulder.
# Step 6 [p.158]: Completion rule — time from E to neckline penetration < time from A to E.
# Step 7 [p.159-160]: To avoid look-ahead bias, entry occurs AFTER zigzag confirms right shoulder,
#   not when prices first touch the neckline.
```

**Case Study Rule-Naming Scheme** [p.419-429]

```
Trend rules:         TT-<input_series>-<lookback>        traditional (+1 when uptrend)
                     TI-<input_series>-<lookback>        inverse (-1 when uptrend)
                     lookbacks ∈ {3,5,8,12,18,27,41,61,91,137,205}  # ~1.5x spacing
                     11 lookbacks × 39 series × 2 (T/I) = 858 rules
Extreme/Transition:  E-<type>-<input>-<displacement>-<CN_lookback>
                     types: 1..12 (combinations of 4 threshold events)
                     displacement ∈ {10, 20}; CN_lookback ∈ {15, 30, 60}
                     12 × 39 × 2 × 3 = 2,808 rules
Divergence:          D-<type>-<companion>-<displacement>-<CN_lookback>
                     same 12 types applied to double-CN divergence indicator
                     12 × 38 × 2 × 3 = 2,736 rules
Total: 6,402 rules [p.405; p.457]
```

## 5. Regras de Trading Explícitas

- **REGRA [p.23]**: Avaliar uma regra APENAS contra um benchmark relevante. Benchmark adotado pelo livro: retorno de uma regra sem poder preditivo (placebo). Um retorno de 10% é insuficiente ou superior dependendo do que outras regras atingiram.
- **REGRA [p.27-28]**: Detrendar a série do mercado traded ANTES de calcular retornos diários da regra. Subtrair o retorno médio diário do período de back-test. Elimina o efeito combinado de position bias × market trend.
- **REGRA [p.29-30]**: Usar log returns, não percentagens. Sinais gerados na close do dia 0 são executados no open do dia +1; o retorno do dia é $\log(O_{+2}/O_{+1})$ (evita look-ahead bias).
- **REGRA [p.183-185]**: Partir da hipótese nula de que toda regra é inútil (expected return = 0). Só rejeitar Ho se o retorno backtested cair na cauda direita da sampling distribution (p-value < 0.05 neste livro [p.410]).
- **REGRA [p.281, p.345]**: NUNCA usar p-values de single-rule back test para avaliar a melhor regra de um data-mining run. Só são válidos tests que incorporam data-mining bias — WRC ou MCP.
- **REGRA [p.407]**: Se múltiplas regras forem testadas (qualquer data mining), guardar as séries diárias completas de returns (para WRC) e/ou os output values +1/-1 de TODAS as regras (para MCP). Sem isto, significance testing rigoroso é impossível.
- **REGRA [p.407-408]**: Não usar regras vindas de prior research de outros sem conhecer quantas regras aquele autor testou ("data-snooping bias"). Preferir construir o rule universe por enumeração combinatória de parâmetros definidos a priori.
- **REGRA [p.46-47]**: Para dados reportados com lag ou sujeitos a revisão (ex.: mutual fund cash, stats econômicas), lagar os sinais apropriadamente. Case study evitou o problema usando apenas dados sem lag/revisão.
- **REGRA [p.149-150]**: Para analistas subjetivos, emitir apenas forecasts falsificáveis. Três formas: (1) definir ponto futuro de avaliação; (2) definir máximo movimento adverso antes de declarar errado; (3) predizer magnitude X favorável antes de Y desfavorável.
- **NUNCA [p.43-44]**: Combinar mentalmente mais de 3 indicadores de forma configural (não-linear). Mente humana limitada a 3 fatores configural; 5 indicadores geram 2^5 = 32 configurações distintas impossíveis de integrar intuitivamente.
- **NUNCA [p.107-113]**: Concluir que um chart é não-aleatório por inspeção visual. Random walks produzem head-and-shoulders, double tops e trends indistinguíveis de "autênticos"; expert chartists não conseguem distinguir [Introduction, p.8; p.37-38].
- **NUNCA [p.291]**: Otimizar parâmetros com poucas observações. A magnitude do data-mining bias cresce dramaticamente com sample size pequeno — ex.: best-of-1,024 rules com 10 obs → bias ~84% anual; com 1,000 obs → bias ~12% anual [p.315, Figure 6.33].
- **REGRA [p.473]**: Se for permitir otimização de complexidade (rule induction, neural nets), usar 3 data segments — train / test / validation — não apenas 2. Only validation gives unbiased out-of-sample estimate.

## 6. Pitfalls e Anti-patterns

- [p.283-287] **Seleção da melhor regra sem ajustar para data-mining bias** — a performance observada da melhor de N regras sobrestima sistematicamente a expected performance. Ignorar isto é o clássico "fool's gold" da TA objetiva.
- [p.289-291] **Cinco fatores que inflam data-mining bias**: (1) mais regras testadas → mais bias; (2) menos observações no performance statistic → mais bias; (3) menor correlação entre rule returns → mais bias; (4) presença de outliers positivos → mais bias; (5) menor variação de expected returns entre as regras → mais bias.
- [p.149-151] **Forecasts não-falsificáveis** ("estou bullish") não passam no discernible-difference test. Equivalem a astrologia.
- **Faith-based subjective TA** [p.5-6] (Elliott Wave, Gann, Magic T's, classic hand-drawn chart patterns) é "not even wrong" porque não gera previsões testáveis.
- [p.333] **Argumento "TA reflete todas as informações" como justificativa de TA** contém contradição lógica — é a mesma premissa da EMH, que nega eficácia de TA [p.333].
- [p.58, p.71-78] **Confirmation bias, self-attribution bias, hindsight bias** — analistas reinterpretam sinais errados como exceções e atribuem sucesso a skill, falhas a azar. Combater com journal diário com forecasts falsificáveis registrados ex-ante [p.53, experiência pessoal do autor em Spear Leeds].
- [p.88-96] **Illusion of trends & patterns in random data** (Reasoning by Representativeness + Law of Large Numbers violation). Small-samples neglect → gambler's fallacy e clustering illusion.
- [p.273-280] **Comparar performance in-sample vs. out-of-sample** como único remédio. A partir do momento em que dados out-of-sample são usados uma vez, perdem virgindade; a alocação arbitrária train/test é subjetiva.
- [p.29-30] **Look-ahead bias** — usar close como input E como execution price (na mesma barra) inflaciona returns.
- [p.23-28] **Position bias × market trend** cria aparência de predictive power em regras inúteis. Um long-biased rule em mercado de alta gera lucro sem qualquer skill.
- [p.406] **Data-snooping bias (prior-research-snooping)** — testar regras de outros autores sem conhecer quantas regras eles testaram torna impossível avaliar significância corretamente.
- [p.450] **Only long/short reversal rules** — assume mercado sempre ineficiente. Rules long/short/neutral (tri-state) ou long/neutral são mais realistas — restrição do case study foi limitação acknowledged.
- [p.287-288, p.473] **Overfitting por complexidade excessiva** — qualquer rule pode ser fitted perfeitamente ao passado com complexidade suficiente; performance out-of-sample será desastrosa.
- [p.407-408] **Complex rules não foram testadas no case study**; estudo maior (Hsu/Kuan, 39,832 rules) encontrou que 82% das 229 regras estatisticamente significativas eram complexas — mas nenhuma significativa em S&P 500 nem DJIA [p.450].

## 7. Parâmetros Sensíveis

- **CBO lookback span {3, 5, 8, 12, 18, 27, 41, 61, 91, 137, 205 dias}** [p.398]: escolhidos para estarem separados por multiplicador ~1.5. Valores escolhidos "without optimization on the basis of intuition" [p.429] — explicitamente não curve-fit.
- **Threshold displacement {10, 20} em E-rules** [p.429]: upper threshold = 50+d, lower = 50-d. Escolhidos intuitivamente; não otimizados.
- **CN lookback {15, 30, 60 dias}** [p.429]: três escalas para capturar extremes e divergences. Não otimizados.
- **Smoothing LMA = 4 dias** [p.437]: fixo para todos os E-rules — justificado como reduzir chattering de sinais sem lag excessivo (LMA lag = (4-1)/3 = 1 dia).
- **Second-level CN lookback = 10x first level** em divergence indicator [p.454]: "assumido que 10x é suficiente para estabelecer fluctuation range" — escolha conservadora, não otimizada.
- **MA 200d como regime filter** — não endosso direto no livro; Aronson NÃO propõe número mágico. Em vez disso, MLM Index usa MA 12-meses como trend benchmark em 25 commodities [p.398].
- **MLM Index = 12-month MA cross em 25 commodities** [p.398]: usa MA 12-meses ("extremamente simplista") aplicada ao nearby futures — justificado economicamente como risk premium de serviço a hedgers [p.380-384], não como curve-fit.
- **Bootstrap/MC replications = 1,999** [p.442]: aumentar suavizaria distribuição mas não alteraria conclusão.
- **Significance level α = 0.05** [p.410]: threshold padrão; resultado do case study seria 15%+ return para significance, 17%+ para p<0.001 [p.459].
- **Case study back-test period: Nov 1, 1980 – Jul 1, 2005 (~6,800 days)** [p.257, p.405, p.409]: justificado pragmaticamente, não testado por robustness.
- **Trading costs foram ignorados no case study** [p.47]: decisão explícita — objetivo era encontrar predictive power, não sistemas tradáveis. Para deployment real, costs devem ser incluídos.

## 8. Citações Literais Importantes

> "Although the scientific method is not guaranteed to extract gold from the mountains of market data, an unscientific approach is almost certain to produce fool's gold." — [p.1]

> "Subjective TA is not even wrong. It is worse than wrong. Statements that can be qualified as wrong (untrue) at least convey cognitive content that can be tested. The propositions of subjective TA offer no such thing." — [p.6-7]

> "It's not so much the things we don't know that get us into trouble as the things we know that just ain't so." — Artemus Ward, quoted by Aronson [p.36]

> "Technical analysts, including myself, know a lot of stuff that isn't so, and believe a lot of weird things." — [p.9-10]

> "There is no such thing as 'approximately random.' Either a rule has predictive power or it does not. Past performance can fool us. Historical success is a necessary but not a sufficient condition for concluding that a method has predictive power and, therefore, is likely to be profitable in the future." — [p.6, paraphrased closely]

> "With respect to the second objective, no rules with statistically significant returns were found. Specifically, none of the 6,402 rules had a back-tested mean return that was high enough to warrant a rejection of the null hypothesis, at a significance level of 0.05." — [p.457]

> "Had I used an ordinary significance test, which pays no attention to data-mining bias, the mean return of the best rule would have appeared to be highly significant (a p-value of 0.0005)." — [p.459]

## 9. Conexões com Outros Livros Desta Base

N/A — Primeiro livro processado neste pipeline; cross-refs serão adicionadas em passes subsequentes. Tópicos naturais de cross-reference futura (quando livros correspondentes forem processados):
- **Data-mining bias, combinatorial backtesting, multiple-testing correction** → *Advances in Financial Machine Learning* (López de Prado), que define Deflated Sharpe Ratio e CPCV para o mesmo problema.
- **Monte Carlo / Bootstrap em trading** → *Permutation and Randomization Tests for Trading System Development* ou *Statistically Sound Machine Learning for Algorithmic Trading* (Masters, que de fato inventou a versão MCP aqui usada [p.ix, p.239-240]).
- **Kelly sizing, behavior bias** → *Mathematics of Money Management* (Vince), *Thinking, Fast and Slow* (Kahneman) — este último subjacente ao cap. 2 de Aronson.
- **Trend-following risk premium / MLM Index** → *Following the Trend* (Clenow), *Trend Following* (Covel).
- **Behavioral finance models (BSV, DHS, HS)** [p.331-380] → *Inefficient Markets* (Shleifer), *Irrational Exuberance* (Shiller).
