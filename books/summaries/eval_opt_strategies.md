# The Evaluation and Optimization of Trading Strategies (Second Edition)

## Metadata
- **Autor:** Robert Pardo [cover, p.ii]
- **Ano:** 2008 [p.ix]
- **Editora:** John Wiley & Sons (Wiley Trading series) [p.ii, p.iv]
- **Páginas:** 367 (PDF); printed ~310 pages of body [metadata]
- **ISBN:** 978-0-470-12801-5 (cloth) [p.ix]
- **Foco principal:** Método sistemático de projetar, testar e otimizar estratégias de trading usando Walk-Forward Analysis (WFA) como defesa central contra overfitting.

## 1. Tese Central

A tese central de Pardo é que a otimização e o overfitting NÃO são sinônimos: "Optimization refers to the process whereby a trading strategy is tested and refined so as to produce the best possible real-time trading profits... Overfitting... is optimization that has gone bad. Overfitting, then, is incorrect testing." [p.7, ch.1]. Optimização feita corretamente é essencial; o que causa fracasso é violação de princípios estatísticos. O método que Pardo criou e defende como "the only 99 percent foolproof method of optimizing a trading strategy" é o **Walk-Forward Analysis** — juiz exclusivamente no desempenho out-of-sample [p.1, Introduction; p.237, ch.11]. O livro argumenta que uma estratégia só deve ir a produção depois de passar pelos 8 estágios do ciclo de desenvolvimento científico (formulação → especificação → teste preliminar → otimização multimercado/multiperíodo → WFA → trading → monitoramento → refinamento) [p.43-55, ch.3].

## 2. Conceitos-Chave

- **Trading Strategy (systematic)** — conjunto de regras objetivas, formalizadas, externas ao julgamento humano, que disparam entradas/saídas/risco [p.11-12, ch.1; p.73, ch.5].
- **Three Principal Components** — toda estratégia tem: (1) entry/exit, (2) risk management, (3) position sizing [p.74, ch.5].
- **Optimization** — "To make the best or most effective use of" — identificação empírica, por simulação histórica, do conjunto de parâmetros mais robusto [p.51, ch.3; p.211, ch.10].
- **Overfitting** — "Fit to an unwanted or excessive degree"; otimização que identifica parâmetros que lucram in-sample mas perdem out-of-sample [p.282, ch.13].
- **Walk-Forward Analysis (WFA)** — sequência de walk-forwards individuais (otimização in-sample + trading out-of-sample adjacente) rolando por todo o histórico [p.237, 248-251, ch.11].
- **Walk-Forward Efficiency (WFE)** — razão entre lucro anualizado out-of-sample e lucro anualizado in-sample; mede qualidade da otimização [p.238-239, 260, ch.11].
- **Optimization Profile** — conjunto de todas as simulações de uma otimização, analisado para (1) % de parameter sets lucrativos, (2) distribuição de performance, (3) shape (smoothness vs. spikiness) [p.226-227, ch.10].
- **Robust Strategy** — "able to withstand or overcome adverse conditions"; performa em amplo range de parameter sets, em todos os tipos de mercado, em vários períodos, em múltiplos mercados [p.225-226, ch.10].
- **Objective Function (search function / fitness function)** — algoritmo que rankeia e seleciona o top parameter set (net profit, PROM, CECPP, Sharpe, etc.) [p.180, 201, ch.9].
- **Perfect Profit (PP)** — soma de todos os swings possíveis (buy every bottom, sell every top); benchmark teórico [p.273, ch.12].
- **Model Efficiency (ME)** — `Net Profit / Perfect Profit`; ≥5% é considerado very good [p.274, ch.12].
- **Pessimistic Return on Margin (PROM)** — métrica conservadora que ajusta wins por `-√N_wins` e losses por `+√N_losses` [p.205-207, ch.9].
- **Required Capital (RC)** — capital necessário: margin + MDD × safety factor [p.83, ch.5; p.270-272, ch.12].
- **Strategy Stop-Loss (SSL)** — limiar de abandono baseado em múltiplo de MDD [p.305-307, ch.14].
- **Theory of Relevant Data** — dados mais recentes/similares às condições atuais de mercado têm mais valor que "mais dados sempre é melhor" [p.243-244, ch.11].
- **Four Major Market Types** — (1) Bullish, (2) Bearish, (3) Congested, (4) Cyclic — histórico deve conter pelo menos um de cada [p.221, ch.10].
- **Degrees of Freedom** — cada data point é 1 DoF; rules e dados consumidos por indicadores reduzem DoF. Mínimo: reter ≥90% [p.292-295, ch.13].

## 3. Fórmulas / Equações

**Strategy Stop (risk de estratégia)** [p.83, ch.5]

$$\text{Strategy Stop} = \text{MDD} \times \text{Safety Factor}$$

Exemplo: MDD=$40k, SF=1.5 → Stop=$60k.

**Required Capital (versão conservadora)** [p.83-84, ch.5; p.271, ch.12]

$$RC = \text{Margin} + (\text{MDD} \times \text{Safety Factor})$$

Variante conservadora (dupla drawdown): $RC = \text{Margin} + 2 \times (\text{MDD} \times SF)$. Para MDD=$40k, margin=$15k, SF=1.5 → $RC = 15k + 2 \times (40k \times 1.5) = \$135k$.

**Risk-Adjusted Return (RAR), anualizada** [p.272-273, ch.12]

$$RAR_{annual} = \frac{\text{Annualized Profit}}{\text{Margin} + \text{Risk}}$$

Onde Risk costuma ser $MDD \times 2$. Exemplo livro: AP=$25k, Margin=$10k, Risk=$40k → RAR = 50%.

**Reward-to-Risk Ratio (RRR)** [p.273, ch.12]

$$RRR = \frac{\text{Net Profit}}{\text{Maximum Drawdown}}$$

Anualizado. Regra: RRR ≥ 3 é desejável.

**Model Efficiency (ME)** [p.274, ch.12]

$$ME = \frac{\text{Net Profit}}{\text{Perfect Profit}} \times 100\%$$

ME ≥ 5% = muito boa estratégia. Perfect Profit = soma absoluta de todos os swings peak-to-valley.

**Walk-Forward Efficiency (WFE)** [p.238, 260, ch.11]

$$WFE = \frac{\text{Annualized Walk-Forward P\&L}}{\text{Annualized Optimization P\&L}}$$

Regra: WFE ≥ 50–60% indica estratégia robusta; WFE ≤ 25% indica overfitting ou estratégia ruim [p.239, ch.11].

**Pessimistic Return on Margin (PROM)** [p.205-206, ch.9]

$$PROM = \frac{[AW \times (N_W - \sqrt{N_W})] - [AL \times (N_L + \sqrt{N_L})]}{\text{Margin}}$$

- $AW$ = average win, $AL$ = average loss [p.205-206, ch.9]
- $N_W$ = number of wins, $N_L$ = number of losses [p.205-206, ch.9]
- Ajuste pelo erro-padrão penaliza pequenas amostras (ex.: 9 trades → 33% penalty via √9/9) [p.207, ch.9].

**Correlation Equity Curve vs. Perfect Profit (CECPP)** [p.204-205, ch.9]

$$\rho_{CECPP} = \frac{\sum_i (x_i - \bar{x})(y_i - \bar{y})}{(n-1) \cdot SD_x \cdot SD_y}$$

- $x$ = Perfect Profit (cumulativo); $y$ = Equity Curve [p.204-205, ch.9]
- Range [-1, +1]; valores próximos a +1 indicam estratégia captura oportunidade de mercado [p.205, ch.9].

**Standard Error (sample size sensitivity)** [p.295, ch.13]

$$SE\% = \frac{1}{\sqrt{N_{trades}}}$$

N=10 → 31.6%; N=100 → 10%; N=1000 → 3%. Mínimo prático: 30–50 trades.

**Degrees of Freedom check** [p.292-294, ch.13]

$$DoF_{remaining}\% = \frac{N_{data\_points} - N_{consumed\_by\_indicators\_and\_rules}}{N_{data\_points}}$$

Regra: manter ≥ 90% de DoF livres.

**Volatility-based Risk Stop (exemplo)** [p.81-82, ch.5]

$$\text{Stop}_{long} = \text{Entry} - k \times \overline{\text{Range}}_{n}$$

Ex.: k=1, average true/daily range 3d = 5.55 pts → stop 5.55 pts abaixo da entrada.

## 4. Algoritmos e Pseudocódigo

**Algoritmo 1: The 8-Step Trading Strategy Development Process** [p.43-55, ch.3]

```
1. Conceptualize and formulate the strategy (hypothesis).
2. Specify rules in computer-testable form (script).
3. Preliminary testing (verify script == concept; rough P/L on
   small basket of markets and time periods).
4. Optimize: multimarket, multiperiod optimization.
5. Validate with Walk-Forward Analysis (WFA).
6. Trade in real time (take every signal).
7. Monitor real-time performance vs. evaluation profile.
8. Refine/evolve; re-run entire cycle on changes.
```

**Algoritmo 2: Single Walk-Forward (WF)** [p.247-248, ch.11]

```
Input: strategy, parameter scan ranges, objective_fn,
       opt_window_size, walk_forward_window_size, history
Step 1 (Optimization):
    run grid/directed search over parameter space on
      history[t_start : t_start + opt_window_size]
    rank by objective_fn
    top_params = best according to objective_fn
Step 2 (Out-of-sample trade):
    simulate strategy with top_params on
      history[t_start + opt_window_size :
              t_start + opt_window_size + walk_forward_window_size]
    record OOS P&L, drawdown, WFE = OOS_annual / IS_annual
Output: top_params, IS_stats, OOS_stats, WFE
```

**Algoritmo 3: Full Walk-Forward Analysis (WFA)** [p.249-251, ch.11]

```
Input: strategy, scan_ranges, objective_fn,
       opt_window, wf_window, step_window, full_history
walk_forwards = []
t = full_history.start
while (t + opt_window + wf_window) <= full_history.end:
    top_params, is_stats, oos_stats, wfe = single_WF(
        history[t : t + opt_window + wf_window],
        opt_window, wf_window, scan_ranges, objective_fn)
    walk_forwards.append((top_params, is_stats, oos_stats, wfe))
    t += step_window

# Reduce:
aggregate_wf_pnl = sum(w.oos_stats.pnl for w in walk_forwards)
pct_profitable_wfs = count(w.oos_stats.pnl > 0) / len(walk_forwards)
avg_WFE = mean(w.wfe for w in walk_forwards)
# Robustness criteria:
#   - majority of WFs profitable
#   - avg WFE >= 50-60% (Pardo target)
#   - small std deviation of WFE
Output: aggregate summary, per-WF table
# Typical sizing: opt_window 3-6yr slow strat, 1-2yr fast;
# wf_window = 25-35% of opt_window [p.249]
```

**Algoritmo 4: Multimarket/Multiperiod Optimization** [p.223-225, ch.10]

```
for each market in diversified_basket (≥ 10 markets):
    for each period in disjoint_time_samples (e.g., 5 × 2-year):
        run_optimization(strategy, market, period, scan_ranges)
        record optimization_profile
# Total scans example (10 markets × 5 periods × 96 param sets)
# = 4,800 simulations [p.225]
# Decision:
#   Excellent & consistent → go to WFA
#   Marginal → proceed with caution
#   Poor majority → abandon
```

**Algoritmo 5: Genetic Algorithm for parameter search** [p.195-197, ch.9]

```
1. Random initial population of parameter sets.
2. Selection: copy pairs proportional to fitness (objective_fn).
3. Crossover: swap parameter slices between pairs.
4. Mutation: randomly replace some params (low rate).
5. Repeat until convergence (no improvement) or max generations.
# GA typically evaluates only 5-10% of full space.
```

**Algoritmo 6: PROM calculation** [p.205-207, ch.9]

```
adj_wins   = N_W - sqrt(N_W)
adj_losses = N_L + sqrt(N_L)
AAGP = (Gross_Profit / N_W) * adj_wins
AAGL = (Gross_Loss / N_L) * adj_losses
PROM = (AAGP - AAGL) / Margin
# Variants (more stringent):
#   PROM - biggest_win
#   PROM - biggest_winning_run
```

## 5. Regras de Trading Explícitas

- **REGRA [p.3, Intro]**: Nunca operar uma estratégia optimizável sem Walk-Forward Analysis. "The only model that I trust that does not use WFA is the model that requires no optimization."
- **REGRA [p.53, ch.3]**: Após passar em WFA, tome TODOS os sinais gerados; "Trading strategies work. System traders do not." — Larry Williams, citado por Pardo.
- **REGRA [p.74, ch.5]**: Toda estratégia deve ter três componentes explícitos: entry/exit, risk management, position sizing.
- **REGRA [p.80, ch.5]**: Risk stop deve ser entrada COM a posição (at inception) e mantido como GTC até a saída.
- **REGRA [p.83, ch.5]**: Required Capital mínimo = Margin + MDD × Safety Factor (SF=1.5 mínimo; 3× recomendado para conservadorismo).
- **REGRA [p.217, ch.10]**: Minimize o número de parâmetros otimizáveis. Quanto mais parâmetros, maior a probabilidade de overfit.
- **REGRA [p.220, ch.10]**: Amostra histórica deve conter pelo menos 30 trades (ideal 50+); idealmente pelo menos um caso de cada um dos 4 market types (Bullish, Bearish, Congested, Cyclic).
- **REGRA [p.239, ch.11]**: WFE ≥ 50–60% = robusto. WFE ≤ 25% = overfit ou estratégia ruim; rejeitar ou revisar.
- **REGRA [p.248, ch.11]**: Janela WF típica = 25–35% da janela de otimização.
- **REGRA [p.249, ch.11]**: Estratégia rápida → opt_window 1–2 anos; estratégia lenta → opt_window 3–6 anos.
- **REGRA [p.244, ch.11]**: WFA ideal cobre 10–20 anos, gerando 10–20+ walk-forwards individuais.
- **REGRA [p.249, ch.11]**: Modelo otimizado em 2 anos de dados tem shelf life de 3–6 meses; em 5 anos, 1–2 anos. Re-otimize DISCIPLINADAMENTE no fim de cada walk-forward window, "whether or not the strategist thinks it needs it or not" [p.254].
- **REGRA [p.273, ch.12]**: Annualized RRR should be three or better (≥ 3).
- **REGRA [p.274, ch.12]**: Model Efficiency ≥ 5% é considerada muito boa.
- **REGRA [p.294-295, ch.13]**: Manter ≥ 90% de degrees of freedom livres após consumo por indicadores e overhead de startup.
- **REGRA [p.297, ch.13]**: Step size do scan deve ser proporcional à magnitude do parâmetro. Ex.: MA curta 2–14 step 1 OK; MA longa 20–200 step 1 é overscanning (use step 5–10).
- **REGRA [p.297, ch.13]**: Optimization profile é "robusto" se ≥ 40% dos parameter sets são proﬁtáveis.
- **REGRA [p.305-307, ch.14]**: Estabeleça um Strategy Stop-Loss ANTES de iniciar real-time. Quando atingido, pare de operar ou reduza exposição (free-fall check).
- **NUNCA [p.202, ch.9]**: Usar Net Profit como única objective function — ignora risco, distribuição, validade estatística.
- **NUNCA [p.284-286, ch.13]**: Adicionar regras/parâmetros baseado em hindsight sem re-testar em ampla gama de períodos e mercados.
- **NUNCA [p.296-298, ch.13]** (Big Fish in Small Pond): Confiar em estratégia cujo lucro se concentra em 1–2 trades grandes dentro de amostra pequena.
- **NUNCA [p.220, ch.10]**: Operar com trade sample < 30 (ideal 50+).

## 6. Pitfalls e Anti-patterns

- **Overfitting (5 causas principais)** [p.291-292, ch.13]:
  1. Insufficient degrees of freedom.
  2. Inadequate data and trade sample.
  3. Incorrect optimization methods (overparameterization, overscanning).
  4. A big win in a small trade sample ("big fish in small pond").
  5. Absence of a Walk-Forward Analysis.
- [p.217, ch.10] **Overparameterization** — 5 parâmetros com 10 candidatos cada = 100,000 simulações; risco altíssimo de overfit. Use o menor nº possível.
- [p.218-219, ch.10] **Overscanning** (step size muito pequeno) infla artificialmente o % de simulações lucrativas, enganando a métrica de robustez.
- [p.283-285, ch.13] **Abuse of hindsight** — adicionar viés bullish após observar bull market; adicionar stop pós-fato porque "evitaria aquele big loss". Ambos destruíram estratégias sem re-teste.
- [p.286-289, ch.13] **Overfit forecasting model** — statistician adicionando variáveis até curva encostar em cada twist do histórico; zero poder preditivo real.
- [p.293-294, ch.13] **Startup overhead** — MA de 50d em amostra de 100d consome 50% dos dados antes do primeiro trade; inaceitável.
- [p.326, ch.13] **Bias de scan pela estratégia** — parâmetros muito longos consomem mais DoF, gerando amostra menor → bias a favor de parâmetros curtos na otimização.
- [p.78-79, ch.5] **Filter creep** — adicionar múltiplos filtros aumenta complexidade e probabilidade de overfit ("different filter for every bar" = modelo absurdamente overfit com lucro simulado irreal e fracasso real-time).
- [p.46-47, ch.3] **Black-box empirical strategies** (neural nets, ML opaco) — descritos como "the ultimate curve-fitting technology" (uso comum; Pardo relutante em aplicá-los sem WFA rigorosa).
- [p.202, ch.9] **Single-criterion evaluation** (ex.: só Net Profit) — ignora risco, distribuição, statistical validity; promove overfitting.
- [p.311-312, ch.14] **Abandonar estratégia por 3 trades ruins** — sem um "falling apart" precisamente definido pré-trade, o trader fica sem âncora psicológica.
- [p.311-312, ch.14] **Euforia em run-up** — ganhos maiores que os esperados são também sinal de desvio; volatilidade crescente = próximos drawdowns maiores.
- [p.200, ch.9] **Spiky optimization space** — picos isolados de performance cercados de parameter sets ruins; provável artefato estatístico, não robustez genuína.
- [p.267-268, ch.12] **MDD histórico subestimado** — se simulação foi em baixa volatilidade, real-time em alta vol produzirá drawdowns maiores; subcapitalização = risco de ruína.
- [p.272, ch.12] **Undercapitalization** — "one of the most common causes of trading failure".

## 7. Parâmetros Sensíveis

- **Optimization window size** [p.249, ch.11]: Pardo diz NÃO é arbitrário — é EMPIRICAMENTE determinado pela WFA. "The size of the estimation or optimization window and the size of the out-of-sample or walk-forward window are simply two more variables in the trading strategy" [p.220, ch.10]. Start: 1–2 anos para estratégias rápidas; 3–6 anos para lentas.
- **Walk-forward window size** [p.249, ch.11]: 25–35% da opt window. Empírico.
- **Safety Factor para Required Capital** [p.83, ch.5]: Pardo usa 1.5 como padrão; 3 para conservadorismo. Justificativa: statistical margin of error na medição de MDD (MDD é um estimador instável).
- **Minimum trade sample** [p.220, ch.10; p.295, ch.13]: 30 trades tradicional; 50+ ideal; justificativa matemática via SE = 1/√N.
- **Degrees of freedom mínimo** [p.294, ch.13]: 90% remanescentes após indicadores. Statistical rule, não arbitrário.
- **Percentage of profitable parameter sets** [p.297, ch.13]: ≥ 40% = optimization robusta. Justificativa: limite estatístico — menos que isso pode ser chance.
- **Optimization scan step size** [p.252, ch.10]: Manter step proporcional em % (não absoluto). Ex.: MA 20 step 1 (5% change) ≈ MA 100 step 5 (5% change). Evita artificial inflation de counts.
- **MDD multiplier para Strategy Stop-Loss** [p.305-307, ch.14]: 2–3x MDD histórico. Justificativa: real-time volatility > backtest.
- **Objective function selection** [p.201-209, ch.9]: Net Profit sozinho é ruim (motivo: ignora risco e sample). PROM é conservador e recomendado. Pardo usa PROM ou combinações com floors/ceilings [p.208-209].

## 8. Citações Literais Importantes

> "Walk-Forward Analysis (WFA) [is] the only 99 percent foolproof method of optimizing a trading strategy. The only model that I trust that does not use WFA is the model that requires no optimization." — [p.1, Introduction]

> "Optimization refers to the process whereby a trading strategy is tested and refined so as to produce the best possible real-time trading profits. Optimization then is testing done correctly. Overfitting, which no sane strategist ever does intentionally, is optimization that has gone bad. Overfitting, then, is incorrect testing." — [p.7, ch.1]

> "Trading strategies work. System traders do not." — Larry Williams, quoted by Pardo [p.53, ch.3]

> "With enough variables, a curve can be fit perfectly to any time series. Will this perfectly fit curve, though have any predictive value? Probably not — too many constraints, too few data, and not enough testing make for a bad model." — [p.287, ch.13]

> "A walk-forward is a two-step process. The trading strategy is first optimized on a historical sample. It is then traded on a new and unseen historical sample. This process is also known as out-of-sample testing or double-blind testing." — [p.247, ch.11]

> "Research has clearly demonstrated that robust trading strategies have WFEs greater than 50 or 60 percent and in the case of extremely robust strategies, even higher." — [p.239, ch.11]

> "Overfitting is optimization performed incorrectly. More specifically, the overfitting or overoptimizing of a trading strategy is the identification of parameters that produce good trading performance on in-sample price history but produce poor trading performance on out-of-sample price history." — [p.282-283, ch.13]

## 9. Conexões com Outros Livros Desta Base

- **Walk-Forward Analysis** [p.237, ch.11] também tratada em `testing_tuning.md` (Masters, "Testing and Tuning Market Trading Systems") — Masters formaliza WFA com bootstrap e Monte Carlo permutation tests; Pardo é a fonte histórica original do termo (1991 DTOTS) e foca em workflow prático. Leitura complementar: WFE de Pardo + permutation p-values de Masters.
- **Out-of-sample / CPCV** em `advances_fin_ml.md` (López de Prado) — López de Prado evolui o conceito de WFA para Combinatorial Purged Cross-Validation (CPCV) com purging e embargo; mesma preocupação filosófica de Pardo mas com formalização probabilística e correção para data leakage via labels sobrepostos. Pardo [p.237] e López de Prado convergem em: "performance on out-of-sample is the only trustworthy evaluator".
- **Parcimônia de parâmetros** em `systematic_trading.md` (Carver) — Carver propõe 3–4 parâmetros max via design bottom-up; Pardo [p.217] chega à mesma conclusão por caminho estatístico (DoF + overfit risk).
- **Overfitting / data snooping bias** em `evidence_based_ta.md` (Aronson) — Aronson formaliza "data mining bias" com testes Monte Carlo; complementa a descrição qualitativa de Pardo sobre as cinco causas de overfit [p.291].
- **Position sizing / Optimal f** em `leverage_space.md` (Vince) — Pardo [p.75, ch.5] diz "many professional trading strategists believe that the sizing principle is more important than the trading strategy itself" mas não desenvolve; Vince e Carver (systematic_trading) fazem o tratamento matemático.
- **MDD-based sizing** [p.271, ch.12] em `risk_parity.md` e `volatility_trading.md` — Pardo usa MDD × safety factor como base; risk_parity aborda volatility-targeting como alternativa forward-looking.
- **Perfect Profit / Model Efficiency** [p.273-274, ch.12] — conceito original de Pardo (DTOTS 1991); não vi replicação direta em outros summaries desta base. Possível análogo: "benchmark alpha" em ml_for_asset_managers, mas diferente na definição.
- **Objective function selection (PROM)** [p.205-209, ch.9] — não tratado igualmente em outros livros; Pardo inventou PROM e é a fonte canônica.
