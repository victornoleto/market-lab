# Technical Analysis for Algorithmic Pattern Recognition

## Metadata
- **Autor:** Prodromos E. Tsinaslanidis, Achilleas D. Zapranis [p.i, cover]
- **Ano:** 2016
- **Editora:** Springer International Publishing Switzerland [p.i]
- **Páginas:** 213 (PDF); ~204 printed
- **ISBN:** 978-3-319-23635-3 (print); 978-3-319-23636-0 (eBook) [p.i]
- **Foco principal:** Rule-based algorithmic recognition of classical technical patterns (horizontal, zigzag, circular) with rigorous statistical assessment (t-tests, Bernoulli trials, bootstrap with GARCH-m/E-GARCH null models).

## 1. Tese Central

Os autores sustentam que a bibliografia sobre análise técnica de padrões sofre de problemas críticos: abordagens descritivas e teóricas em vez de quantitativas, ilustrações apenas de casos "ótimos", subjetividade inerente na identificação visual e vieses cognitivos (clustering illusion) [Preface, p.vii-viii]. O livro propõe tratamento sistemático via mecanismos de reconhecimento rule-based (algorítmicos e, portanto, não subjetivos) e um framework estatístico robusto (testes paramétricos + bootstrap com modelos nulos GARCH) para avaliar se padrões geram retornos anormais [p.2, ch.1; p.25-26]. **Conclusão empírica dos autores**: "overall TA does not generate systematically, statistically significant abnormal returns" [p.2]. O resultado mais forte do livro: o padrão Head-and-Shoulders pode ser identificado em 21.77% (normal) e 22.94% (inversa) das séries simuladas com GBM puro — logo aparece em pura aleatoriedade [p.93, ch.5].

## 2. Conceitos-Chave

- **Weak-form EMH** — preços atuais refletem toda a informação contida em preços históricos; invalida a predição baseada em TA no limite [p.4-5, ch.1]
- **Random Walk RW1/RW2/RW3** — três versões hierárquicas (IID / INID / uncorrelated but dependent); RW2 é o usual em finanças pois permite heteroskedasticidade condicional [p.7-8]
- **Self-fulfilling prophecy vs self-destructive** — duas teses opostas sobre como crenças coletivas dos técnicos afetam preços [p.20-21, §1.5.2]
- **Clustering illusion** — viés cognitivo que faz humanos perceberem padrões onde não existem; explica persistência irracional da TA [p.21, §1.6]
- **Regional local (peak/trough)** — observação que é máxima (mínima) numa janela de 2w+1 centrada nela; base de todo reconhecimento de padrões [p.32, ch.2]
- **Perceptually Important Points (PIPs)** — método alternativo de identificar pontos salientes via distância máxima (ED, PD ou VD) a PIPs adjacentes [p.33-36, §2.3.2]
- **HSAR (Horizontal Support/Resistance)** — zona horizontal de preços onde clustering de locals forma banda de suporte/resistência, não nível único [p.61-63, ch.4]
- **Bounce frequency** — razão bounces/hits; mede poder de reversão de um HSAR [p.66]
- **Trading Range Breakout (TRB)** — versão simples de SAR: mín/máx das últimas w barras [p.61, §4.2.4]
- **Fibonacci retracement levels** — 0%, 23.6%, 38.2%, 50%, 61.8%, 100%, 161.8%, 261.8%, 423.6% [p.59, §4.2.1]
- **Neckline (HS pattern)** — linha conectando os dois troughs intervenientes; age como suporte antes da penetração e resistência depois [p.57, ch.4; p.87, ch.5]
- **Geometric Brownian Motion (discrete)** — $\Delta P/P = \mu\Delta t + \sigma\varepsilon\sqrt{\Delta t}$, usado como null model para simulação [p.92, eq.5.14]
- **Savitzky-Golay smoothing** — filtro polinomial local; pré-processamento para estimar derivadas antes de DDTW [p.200, eq.9.10]
- **DTW / DDTW / Subsequence DDTW** — Dynamic Time Warping e variantes para alinhar séries de comprimentos diferentes; DDTW usa derivadas locais (robustas a níveis de preço distintos) [ch.9, p.193-202]
- **GARCH-m e E-GARCH null models** — modelos nulos bootstrap que capturam leptocurtose, autocorrelação e heteroskedasticidade condicional [ch.8, p.161]
- **Joint hypothesis problem** — ao testar retornos excessivos é preciso escolher um modelo de asset pricing (CAPM, APT); ambos com limitações; os autores preferem raw returns [p.164, ch.8]
- **"Trader's remorse"** — após penetração de SAR, preços retornam ao nível que inverte papel (S→R ou R→S) [p.62, ch.4]
- **Whipsaw** — reversões rápidas em direções opostas sobre a mesma média móvel, geram custos altos [p.149, ch.7]

## 3. Fórmulas / Equações

**Regional peak/trough (rolling window)** [p.32, eq.2.1-2.2]

$$\text{Local Peak if } p_t > \max\{p_{[t-w:t-1]}\} \;\&\; p_t > \max\{p_{[t+1:t+w]}\}$$

$$\text{Local Trough if } p_t < \min\{p_{[t-w:t-1]}\} \;\&\; p_t < \min\{p_{[t+1:t+w]}\}$$

**Perpendicular distance para PIP** [p.34, eq.2.4]

$$d_P(x_i; x_t, x_{t+T}) = \frac{|s \cdot i + c - p_i|}{\sqrt{s^2 + 1}}$$

onde $s=(p_{t+T}-p_t)/T$, $c=p_t - t(p_{t+T}-p_t)/T$.

**HSAR bin number (logarithmic spacing)** [p.63, eq.4.13]

$$n = \frac{\ln(L_2^*/L_1^*)}{\ln(1+x)}$$

onde $L_1^* = \min(L)(1+x/2)$, $L_2^* = \max(L)(1+x/2)$, $x$ = percentual desejado por bin.

**TRB levels** [p.61, eq.4.4-4.5]

$$\text{Support}_t = \min\{p_{t-1}, \dots, p_{t-w}\}, \quad \text{Resistance}_t = \max\{p_{t-1}, \dots, p_{t-w}\}$$

**HS tops — 5 condições (Osler & Chang 1995, adotadas por Lucke 2003)** [p.87-88, ch.5, eq.5.1-5.7]

- C1 (head higher) [p.87, eq.5.1]: $P_2 > \max(P_1, P_3)$
- C3 (balance) [p.88, eq.5.4]: $P_1 \geq 0.5(P_3+T_2)$ & $P_3 \geq 0.5(P_1+T_1)$
- C4 (symmetry) [p.88, eq.5.5]: $t_{P_2}-t_{P_1} < 2.5(t_{P_3}-t_{P_2})$ & $t_{P_3}-t_{P_2} < 2.5(t_{P_2}-t_{P_1})$
- C5a (neckline penetration) [p.88, eq.5.6]: $B < \frac{T_2-T_1}{t_{T_2}-t_{T_1}}(t_B-t_{T_1})+T_1$
- C5b (timing) [p.88, eq.5.7]: $t_B < t_{P_3}+(t_{P_3}-t_{P_1})$

**DT balance & depth** [p.97, eq.5.27, 5.29]

$$|P_1-P_2|/\min(P_1,P_2) \leq 0.04, \quad (T_1-P_1)/P_1 \leq -0.1$$

(i.e. 4% tolerância lateral, 10% de recuo mínimo entre topos; valores de Bulkowski 2000)

**Rounding Bottom — radius do círculo circunscrito** [p.129, eq.6.1]

$$R_1 = \frac{a}{2\sin(A)}$$

**RB depth** [p.132, eq.6.5]

$$\text{Depth} = \frac{P_{\max}-P_{\min}}{P_{\min}}$$

**RB fit** [p.132, eq.6.4]

$$\text{Fit} = \frac{\text{obs within bounds}}{\text{total obs}}$$

Default thresholds: bounds = 0.3, $t_{\text{width}}=15$, $t_{\text{fit}}=0.9$ [Table 6.2, p.134]

**Geometric Brownian Motion (discrete)** [p.92, eq.5.14]

$$\frac{\Delta P}{P} = \mu \Delta t + \sigma \varepsilon \sqrt{\Delta t}, \quad \varepsilon \sim N(0,1)$$

**SMA** [p.148, eq.7.1]

$$\text{SMA}_t|w = \frac{P_t + P_{t-1} + \dots + P_{t-w+1}}{w}$$

**EMA** [p.150, eq.7.4]

$$\text{EMA}_{t|w,\lambda} = (1-\lambda)\text{EMA}_{t-1|w,\lambda} + \lambda P_t, \quad \lambda^* = \frac{2}{w+1}$$

**MACD & signal line** [p.152, eq.7.7-7.8]

$$\text{MACD}_{t|w_S,w_L,\lambda} = \text{EMA}_{t|w_S,\lambda} - \text{EMA}_{t|w_L,\lambda}$$

$$\text{SL}_{t|w_{sig},\lambda} = \text{EMA}^{\{\text{MACD}_t\}}_{t|w_{sig},\lambda}$$

Typical params: $w_L=26, w_S=12, w_{sig}=9$ (Murphy 1999) [p.151]

**RSI** [p.153, eq.7.12-7.13]

$$\text{RS}_{t|w} = \frac{\sum_{i=t-w+1}^{t} \Delta P_i^+}{\sum_{i=t-w+1}^{t} \Delta P_i^-}, \quad \text{RSI}_{t|w} = 100 - \frac{100}{1+\text{RS}_{t|w}}$$

Default: $w=14$, upper level 70, lower level 30 [p.153]

**Bollinger Bands** [p.154, eq.7.15-7.16]

$$\text{BB}^{up}_{t|w,k} = \text{SMA}_{t|w} + k\sigma_{t|w}, \quad \text{BB}^{low}_{t|w,k} = \text{SMA}_{t|w} - k\sigma_{t|w}$$

Default: $w=20, k=2$.

**Momentum / ROC** [p.156-157, eq.7.18, 7.21]

$$\text{MOM}_{t|w} = P_t - P_{t-w}, \quad \text{ROC}_{t|w} = 100(P_t/P_{t-w} - 1)$$

Default $w=12$.

**Bootstrap / Bernoulli trial z-stat** [p.48, ch.3]

$$z = \frac{x - pN}{\sqrt{Np(1-p)}}$$

onde $x$ = número de sucessos (ex: estimated bounce > artificial), $p=0.5$ (fair), $N$ = trials.

**DTW accumulated cost recursion** [p.195, eq.9.3]

$$\tilde{d}(n,m) = d(n,m) + \min\{\tilde{d}(n-1,m), \tilde{d}(n,m-1), \tilde{d}(n-1,m-1)\}$$

**Forecast-accuracy metrics (MSE, RMSE, NRMSE, NPRMSE, MAE, MAPE, Theil U1, U2)** [p.49-51, ch.3, eq.3.6-3.13] — todas padrão e definidas no texto.

**POCID / IPOCID / POS** (directional accuracy) [p.52, eq.3.14-3.17]

## 4. Algoritmos e Pseudocódigo

**RW() — identificar regional locals** [p.32, ch.2, Appendix 1]

```
Input: ys (price vector), w (half-window), pflag
Output: Peaks (m×2), Bottoms (k×2)  # y-coord, x-coord
for t in [w+1 : len(ys)-w]:
    if ys[t] > max(ys[t-w:t-1]) and ys[t] > max(ys[t+1:t+w]):
        append (ys[t], t) to Peaks
    if ys[t] < min(ys[t-w:t-1]) and ys[t] < min(ys[t+1:t+w]):
        append (ys[t], t) to Bottoms
```

**PIPs() — Perceptually Important Points** [p.33-36, ch.2]

```
Input: price series P of length L, number K of PIPs, distance d in {ED, PD, VD}
PIPs = [(1, P[1]), (L, P[L])]
while len(PIPs) < K:
    for each intermediate point i between adjacent PIPs:
        compute d(P[i], adjacent PIPs)
    add point with max distance to PIPs
    sort PIPs by x-coord
return PIPs
```

**HSAR() — identification of horizontal S/R zones** [p.62-63, ch.4]

```
(1) Call RW(ys, w) -> regional locals L = [l1..lk]
(2) Define bins logarithmically: n = ln(L2*/L1*) / ln(1+x)
(3) Round n -> actual bin count n_hat; recompute x_hat = (L2*/L1*)^(1/n_hat) - 1
(4) Bucket locals into bins; bin is HSAR if frequency >= 2
(5) Daily identification: HSARsim uses only past data up to t-1 (500-day warmup)
```

**HS() identification — diagonal check of 7x7 criteria matrix** [p.88-89, Table 5.1]

```
For each 7-tuple (P0, T0, P1, T1, P2, T2, P3) of alternating locals:
    build 7x5 binary matrix M
    M[i,j] = 1 if local i satisfies condition j (among 5 HS conditions)
    confirm pattern if diagonal of 1's exists (all 5 conditions met)
```

**RBottoms() — circle-based saucer detection** [p.131-132, ch.6]

```
Input: ys, w (RW), Bounds %, tWidth, tFit
(1) Find short-term peaks with RW(ys, w)
(2) For each peak P1, scan forward for first P2 >= P1
(3) Require a local trough T1 between them
(4) Scale data 1:2 (depth:width)
(5) Build isosceles triangle ABC (A,C at avg y of P1,P2; B at x-midpoint, y of T1)
(6) Compute radius R1 of circumscribed circle
(7) Draw homocentric circles R2 = (1-Bounds)R1, R3 = (1+Bounds)R1
(8) Count prices within [R2, R3] band; Fit = count / width
(9) Confirm if width >= tWidth and Fit >= tFit
```

**Bootstrap methodology (null model assessment)** [p.48-49, ch.3; p.161, ch.8]

```
(1) Apply rule g() on actual series -> observed statistic theta_hat
(2) Fit null model (GARCH-m or E-GARCH) to actual returns
(3) Verify residuals are IID (else discard model)
(4) Resample residuals with replacement; simulate N series using fitted coefficients
(5) Apply g() to each simulated series -> distribution {theta*_1,...,theta*_N}
(6) Simulated p-value = fraction of theta*_i >= theta_hat
(7) Rule significant at alpha if p-value <= alpha
```

**Subsequence DDTW** [p.196-200, ch.9]

```
Input: query Q (length N), longer Y (length M), threshold tau, rolling window omega
(1) Smooth Y via Savitzky-Golay (ws=21, cubic)
(2) Compute first derivatives: y'_m = [(y_hat_m - y_hat_{m-1}) + (y_hat_{m+1} - y_hat_{m-1})/2] / 2
(3) Standardize to zero-mean, unit-sd
(4) Build cost matrix D[n,m] = |Q[n] - Y[m]|
(5) Relax boundary: D_tilde[1,m] = D[1,m] for all m in [1:M]
(6) Fill D_tilde via recursion (eq.9.3)
(7) Identify local minima of D_tilde[N,:] using RW with window omega
(8) Set B* = {b where D_tilde[N,b] < tau}
(9) Backtrack each b* to starting point a*
```

## 5. Regras de Trading Explícitas

- **REGRA [p.57, ch.4]**: Em HSARz, se preço bate e retorna do mesmo lado → bounce (trend reversal signal); se penetra → failure (trend continuation signal). Long em bounce-de-support, short em bounce-de-resistance. TR2 inverte: long após breach de resistance.
- **REGRA [p.66, ch.4]**: Sinal de trade com 1 dia de lag após a confirmação (evita non-synchronous trading); fechamento após holding periods fixos HPs = {1:1:20} dias ou HPm = {22:2:40} dias.
- **REGRA [p.106, ch.5 — HS tops closure]**: Short na penetração da neckline; fecha quando (1) preço atinge target = neckline - head_height (case 1), OU (2) tempo excede shoulder-width (case 2), OU (3) preço sobe acima da neckline por $t_n$ dias consecutivos ou causa perda >= $t_{sl}$ (case 3). Autores usam $t_n=2$, $t_{sl}=-0.04$ [p.109-110, Tables 5.4-5.5].
- **REGRA [p.95, ch.5 — DT balance]**: Tolerância entre dois tops <= 4%; recuo mínimo >= 10% (Bulkowski 2000).
- **REGRA [p.134, ch.6 — RB params]**: Bounds=0.3, min width=15, min fit=0.9, w=10.
- **REGRA [p.148, ch.7 — SMA]**: Long quando $P_t > \text{SMA}$ & $P_{t-1} < \text{SMA}$; short no inverso.
- **REGRA [p.153, ch.7 — RSI]**: Buy quando RSI cruza lower (30) de baixo; sell quando cruza upper (70) de cima (Wilder 1978).
- **REGRA [p.153, ch.7 — BB]**: Buy se preço sai pelo BB_upper OU cruza BB_lower de baixo; sell no inverso (Leung & Chong 2003; Lim et al. 2013).
- **REGRA [p.105, ch.5 — choice of w]**: Escolher w em RW() para zigzag patterns baseado em duração média esperada: HS -> w=7, TT/TB -> 15, DT/DB -> 15, Flags -> 3, Pennants -> 2, Wedges -> 7 (via simulação GBM matching mediana de espaçamento entre locals) [Table 5.2, p.104].
- **NUNCA [p.65, ch.4]**: Usar HSARs "estimados" com dados futuros para backtesting — é look-ahead bias. Use HSARsim() com warmup de ~500 dias e recompute a cada dia só com dados até t-1.
- **PREFIRA [p.172, ch.8]**: Holding periods curtos. TA performa melhor em HP=1 dia; aumentando HP degrada a performance.
- **REGRA [p.164, ch.8]**: Usar raw logarithmic returns (não excess returns) para short-term testing — evita joint hypothesis problem com CAPM/APT.

## 6. Pitfalls e Anti-patterns

- **[p.93, ch.5] HS pode ser identificado em 21.77% / 22.94% das séries GBM simuladas** — "if GBM is considered an accurate representation of the price stock generating mechanism then the HS pattern has no predictive power at all" [p.11, ch.1]. Clustering illusion explica persistência da crença.
- **[p.190, ch.8] Parameter optimization NÃO foi feita no livro deliberadamente** — "parameters' values used in defining each trading rule were the most commonly used in the literature" para evitar data-snooping. Readers devem NÃO otimizar parâmetros em in-sample e relatar resultados como se fossem out-of-sample.
- **[p.18, §1.5.3] Overfitting via backtesting**: rules ótimas in-sample capturam tanto sinal quanto ruído; ruído não se repete out-of-sample → performance degrada. Validation set obrigatório.
- **[p.66, ch.4] Look-ahead bias** em HSAR clássico: qualquer método que use locals futuros para definir um nível corrente é inválido. Use rolling/expanding window apenas com informação $t-1$.
- **[p.13, p.68, p.190] "Self-destructive" TA**: regras que já foram publicamente eficazes tendem a desaparecer (Sullivan et al. 1999; Olson 2004; Zapranis & Tsinaslanidis 2012b).
- **[p.168-169, Table 8.5] Low-frequency patterns geram poucos sinais**: embora patterns tenham retornos absolutos maiores que indicators, produzem poucos sinais — empurra retornos médios para a média incondicional. Não generalizar de um único pattern eficaz.
- **[p.190, ch.8] Transaction costs NÃO incluídos** — "transaction costs were not considered in this study, which would exacerbate even further the predictive performance of TA".
- **[p.190, ch.8] Volume confirmation NÃO incluída** — difícil embutir em bootstrap simulado, mas TA assume que volume confirma sinal.
- **[p.21, §1.6] Clustering illusion**: humanos veem padrões em sequências aleatórias (De Bondt 1998; Gilovich 1993).
- **[p.22, §1.6] Overconfidence + self-attribution + hindsight bias + confirmation bias + neglect of probability** — todos justificam a perseverança irracional de traders em TA.
- **[p.165, ch.8] Distributional assumptions de t-tests ordinários são violadas** em séries financeiras (leptocurtose, autocorrelação, heteroskedasticidade condicional) → use bootstrap com GARCH null model.
- **[p.158, ch.7 "Whipsaw"]**: em mercados voláteis com MA sensível, long/short signals oscilam no mesmo nível, gerando perdas de transação. Use filtros (time, price-percentage) ou MAC.
- **[p.109, ch.5] Em zigzag patterns, f3 >= f1 > f2 é o padrão empírico** — ou seja, stop-loss (case 3) dispara MAIS frequentemente que o price target (case 1) ou expiração neutra (case 2). TA falha mais vezes do que acerta.
- **[p.188-189, ch.8] AR(1) null model falhou no teste IID** em séries reais — não use modelo nulo sem checar independência dos resíduos.
- **[p.201-202, ch.9] DDTW é computacionalmente caro** — complicado combinar com bootstrap que já é pesado.
- **[p.202, ch.9] Pathological alignment em DTW**: caminho ótimo pode deviar fortemente da diagonal; use Sakoe-Chiba band ou Itakura parallelogram como constraint global.

## 7. Parâmetros Sensíveis

- **Rolling window w em RW()** [p.104-105, Table 5.2]: escolhido via simulação GBM com 100 combinações de (mu, sigma), encontrando w cuja mediana de espaçamento entre locals bate com duração média do pattern na literatura. Justificativa econômica: captura a duração teórica média reportada por Bulkowski/Pring/Murphy. **NÃO é otimizado em backtest**.
- **HSAR bin percent x=3% (empirical results), 5% (example)** [p.68, p.63]: valor logarítmico mantém distância percentual constante entre bins. x=3% e w=50 usados nos empirical results.
- **RB thresholds Bounds=0.3, tWidth=15, tFit=0.9** [p.134]: width=15 vem de Pring (2002) "as little as 3 weeks". Bounds e fit são arbitrários mas justificados como conservadores.
- **HS 2.5x symmetry ratio** [p.88]: vem diretamente de Osler & Chang (1995); não otimizado. Autores aplicam como-é.
- **DT/DB 4% balance, 10% depth** [p.97]: vêm de Bulkowski (2000). Autores admitem "maximum price variations of 3% and 4% for DT and DB respectively" no Bulkowski original.
- **RSI(14)**: [p.153] tradição de Wilder (1978); autores apenas usam.
- **MACD (12, 26, 9)** [p.151]: "technicians usually set $w_L=26, w_S=12, w_{signal}=9$" (Murphy 1999) — pura convenção.
- **BB (20, 2)** [p.154]: "common length of time span used is 20 days". Pura tradição.
- **MOM w=12, ROC w=12** [p.156-157]: "setting w with 12 is a common choice among technicians" (Rosillo et al. 2013).
- **Stop-loss thresholds $t_n=2$, $t_{sl}=-0.04$** [p.109, Table 5.4]: escolhidos como representativos; autores apresentam figuras com sensibilidade (Fig 5.16) mostrando como variação muda frequências relativas e retornos médios — é exploração paramétrica, não otimização.
- **SMA long-term w=200** [p.163, ch.8, Table 8.2]: "long term" benchmark. Medium w=50, short w=10.
- **Holding period HP**: testado para múltiplos valores; Fig 8.1 mostra que HP=1 dá melhor performance [p.171-172].

## 8. Citações Literais Importantes

> "Our empirical evidences suggest that overall TA does not generate systematically, statistically significant abnormal returns." — [p.2, ch.1]

> "The HS pattern is successfully identified in random price series and this indicates that it is possible the pattern to be identified in real price series too. The main conclusion is that if the geometric Brownian motion is considered an accurate representation of the price stock generating mechanism then the HS pattern has no predictive power at all." — [p.11, ch.1]

> "...the usual method of graphing stock prices gives a picture of successive levels rather than of changes, and levels can give an artificial appearance of pattern or trend. A second is that chance behavior itself produces patterns that invite spurious interpretations." — Roberts (1959), cited [p.93, ch.5]

> "Support and resistance are not individual price points, but rather thick bands of molasses that slow or even stop price movement." — Bulkowski (2002), cited [p.61-62, ch.4]

> "After taking trading costs into account, none of the thirty-two patterns showed any evidence of profitable forecasting ability in either [bullish or bearish] direction... Moreover, the most bullish results tended to be generated by those patterns which are classified as bearish in the standard textbooks on charting, and vice versa." — Levy (1971, p.318), cited [p.14, Table 1.1]

## 9. Conexões com Outros Livros Desta Base

- **Ceticismo sobre TA clássica** [p.2, ch.1]: `algo_trading_chan.md` e `quant_trading_chan.md` (Chan) documentam empiricamente estratégias com performance marginal — alinhado com a conclusão central deste livro. Ambos enfatizam validação out-of-sample.
- **Regional peaks / pattern recognition via PIPs** [ch.2, p.32-36]: sobrepõe parcialmente com técnicas de swing-point detection em `cycle_analytics.md` e `rocket_science.md` (Ehlers). Ehlers usa DSP filters e Hilbert transform; Tsinaslanidis usa RW + PIPs discretos.
- **Bootstrap methodology com GARCH null model** [ch.8, p.161, p.173-189]: metodologia similar discutida em `ml_for_algo_trading.md` (Lopez de Prado) sob outro nome (Monte Carlo / purged cross-validation).
- **GBM como null model de séries de preço** [ch.5, p.92, eq.5.14]: também em `fin_time_series_tsay.md` (modelos ARIMA/GARCH) e `time_series_hamilton.md`.
- **Technical indicators (SMA, EMA, MACD, RSI, BB, MOM, ROC)** [ch.7, p.147-159]: definições padrão alinhadas com `cybernetic_analysis.md` e `quant_trading_chan.md`.
- **Head-and-Shoulders in GBM noise (clustering illusion)** [p.93, ch.5; p.21, §1.6]: reforça alerta de `systematic_trading.md` (Carver) sobre cherry-picking e confirmation bias, e alinha com framework anti-overfit do projeto ai-trade.
- **Overfitting warning via in-sample vs out-of-sample** [p.18, §1.5.3]: presente em `ml_for_algo_trading.md` e `testing_tuning.md`; o capítulo 1.5.3 aqui é introdutório em comparação com o tratamento de Lopez de Prado.
