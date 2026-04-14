# Regime Detection

HMM e outros métodos para identificar bull/bear/sideways e trocar estratégia dinamicamente.

## Sources

- [`books/regime_change.md`](../books/regime_change.md)
- [`books/sentiment_analysis_handbook.md`](../books/sentiment_analysis_handbook.md)
- [`books/data_driven_science.md`](../books/data_driven_science.md)

## From `books/regime_change.md`

### Regras de Trading Explícitas

- **REGRA [p.82, ch.6]**: Under normal regime, enter contrarian when |TMV| reaches 2: short in uptrend (TMV ≥ 2), long in downtrend (TMV ≤ -2). Rationale: mean reversion is observed in normal market regimes.

- **REGRA [p.83, ch.6]**: Under abnormal regime, JC1 switches to trend-following on the same |TMV| ≥ 2 trigger. Rationale: in abnormal regimes, margin calls cascade and drive the prevailing trend further.

- **REGRA [p.82, ch.6]**: Close position at the next DC Confirmation (DCC) point under both normal and abnormal regimes.

- **REGRA [p.82–83, ch.6]**: Close ALL open positions immediately when a regime change is detected by the Bayes tracker. This is the primary stop-loss mechanism and the source of drawdown reduction.

- **REGRA [p.83, ch.6]** (JC2 — more conservative): Hold NO positions during abnormal regime; wait for return to normal regime before re-entering.

- **REGRA [p.71, ch.5]**: Use B-Strict rule: only conclude Regime 2 if $p(C_2|x) > p(C_1|x)$ AND $p(C_2|x) > 0.8$. Reduces false alarms from 52 to 10 across DJIA/FTSE/S&P 500 test period [p.76, ch.5].

- **REGRA [p.58, ch.4]**: If the current market is moving away from the normal regime cluster in the T-TMV indicator space, consider closing positions or switching strategy.

- **NUNCA [p.77, ch.5]**: Treat regime tracking output as a forecast of future prices — the method is purely data-led and tells only the current regime state. "No forecasting is attempted."

---

### Fórmulas / Equações

**DC Event Condition** [p.10, ch.2 eq. 2.1]

$$\frac{|P_t - P_{EXT}|}{P_{EXT}} \geq \theta$$

- $P_t$ = current price; $P_{EXT}$ = price at last extreme point; $\theta$ = threshold [p.10, ch.2]

---

**Total Price Movement (TMV)** [p.42, ch.4 eq. 4.1]

$$TMV = \frac{|P_s - P_e|/P_s}{\theta}$$

- $P_s$ = price at trend start (extreme point); $P_e$ = price at trend end (next extreme point); $\theta$ = threshold [p.42, ch.4]

---

**Time-Adjusted Return (R)** [p.43, ch.4 eq. 4.2]

$$R = \frac{|TMV| \times \theta}{T}$$

- $T$ = time elapsed between successive extreme points [p.42, ch.4]
- Higher R indicates larger price change in less time — proxy for volatility intensity under DC [p.43, ch.4]

---

**TMV indicator (alternative form with extreme points)** [p.12, ch.2 eq. 2.2]

$$TMV_{EXT}(n) = \frac{P_{EXT}(n) - P_{EXT}(n-1)}{P_{EXT}(n-1) \times \theta}$$

where $P_{EXT}(n)$ is the price at the $n$-th extreme point.

---

**Log-transformed DC indicator (HMM input)** [p.27, ch.3 eq. 3.1]

$$LR[t] := \log(R[t])$$

Applied before feeding R into HMM to address right-skew in R distributions.

---

**Realised Volatility (time-series benchmark)** [p.27, ch.3 eq. 3.2]

$$RV(t) = \sum_{i=1}^{n} r_t^2(i)$$

- $r_t(i)$ = 5-minute log return at interval $i$; $n$ = number of 5-minute intervals in one trading day [p.27, ch.3]
- Used as the time-series counterpart to R for head-to-head regime detection comparison in Chapter 3 [p.27, ch.3].

---

**HMM Markov Assumption** [p.15, ch.2 eq. 2.5]

$$P(q_i = a \mid q_1 \ldots q_{i-1}) = P(q_i = a \mid q_{i-1})$$

The current hidden state depends only on the immediately preceding state.

---

**Naive Bayes Posterior** [p.18, ch.2 eq. 2.6–2.7; also p.63, ch.5 eq. 5.1]

$$p(C_k | x) = \frac{p(C_k) \cdot p(x | C_k)}{p(x)}$$

where $x = (TMV_i, T_i)$, $C_k \in \{C_1 = \text{Normal}, C_2 = \text{Abnormal}\}$

---

**Conditional independence of features** [p.64, ch.5 eq. 5.2]

$$p(x | C_k) = p(x_1 | C_k) \cdot p(x_2 | C_k)$$

where $x_1 = TMV$, $x_2 = T$ — "naive" assumption of independence.

---

**Gaussian emission density** [p.64, ch.5 eq. 5.3]

$$p(x | C_k) = \frac{1}{\sqrt{2\pi\sigma_k^2}} \exp\!\left(-\frac{(x - \mu_k)^2}{2\sigma_k^2}\right)$$

$\mu_k$ and $\sigma_k$ are estimated from training data for each regime $k$.

---

**Marginal probability** [p.64, ch.5 eq. 5.5]

$$p(x) = p(x|C_1)\,p(C_1) + p(x|C_2)\,p(C_2)$$

---

**B-Simple decision rule** [p.70, ch.5 eq. 5.6]

$$\text{choose } C_1 \text{ if } p(C_1|x) > p(C_2|x); \quad \text{choose } C_2 \text{ if } p(C_2|x) > p(C_1|x)$$

---

**B-Strict decision rule** [p.71, ch.5 eq. 5.7]

$$\text{choose } C_2 \text{ if } p(C_2|x) > p(C_1|x) \text{ AND } p(C_2|x) > \text{threshold}_2$$

- $\text{threshold}_2 = 0.8$ in empirical experiments [p.71, ch.5]
- B-Simple is a special case of B-Strict with $\text{threshold}_2 = 0.5$ [p.71, ch.5]

---

**Min-Max normalisation (comparing T and TMV across markets)** [p.45, ch.4 eq. 4.3]

$$x' = \frac{x - \min(x)}{\max(x) - \min(x)}$$

Applied so that regimes from markets with different absolute TMV/T scales can be positioned in the same indicator space.

---

### Algoritmos e Pseudocódigo

**Algorithm 1 — Naive Bayes Classifier training and testing** [p.65, ch.5]

```
Training Phase
  Input:  Training data (x, C) where x = (TMV, T) pairs, C in {C1, C2}
  Output: Parameters of the model
  1. Calculate prior probability of class: p(C_k)
  2. Calculate mean mu_k and std sigma_k of features per class
  3. Estimate Gaussian distribution p(x|C_k) for each class
  4. Calculate marginal p(x) = sum_k [ p(x|C_k) * p(C_k) ]

Testing Phase
  Input:  New observation v
  Output: p(C_k | x = v)
  1. For each class k: plug v into Gaussian(mu_k, sigma_k)
  2. Calculate p(x = v | C_k)
  3. Calculate p(C_k | x = v) = p(C_k) * p(x=v|C_k) / p(x)
```

---

**DC-based Regime Detection Pipeline (Chapter 3)** [p.25–28, ch.3]

```
Input:  Price series (second-by-second), threshold theta = 0.004 (0.4%)
Step 1: Summarise data into DC trends (uptrends, downtrends) using theta
Step 2: For each completed DC trend:
          compute TMV, T
          compute R = |TMV| * theta / T
Step 3: Log-transform: LR[t] = log(R[t])
Step 4: Fit 2-state HMM with Gaussian emissions to LR series
          (depmixS4 in R; EM algorithm)
Step 5: Decode hidden state of each trend -> Regime 1 or Regime 2
          Regime 1: lower R (normal, less volatile)
          Regime 2: higher R (abnormal, more volatile)
Output: Regime label per DC trend
Parallel:
  Extract 5-minute returns from same raw data
  Compute daily realised volatility RV = sum(r_t^2)
  Fit separate 2-state HMM on RV
  Compare regime periods from both approaches
```

---

**Regime Classification in T-TMV Indicator Space (Chapter 4)** [p.44–55, ch.4]

```
For each dataset (10 markets x 10 thresholds, thresholds in 0.1%-1.0%):
  1. Summarise into DC trends using each threshold
  2. Compute TMV, T, R per trend
  3. Run 2-state HMM on R -> label each trend Regime1/Regime2
  4. Compute average TMV and average T per regime period
  5. Apply min-max normalisation (eq. 4.3) per dataset

Plot each (regime period, dataset, threshold) as point in
normalised (mean_T, mean_TMV) indicator space.

Expected outcome:
  Regime 1 points cluster in one region (higher T, lower TMV)
  Regime 2 points cluster in another region (lower T, higher TMV)
  -> higher TMV/T ratio = higher volatility
  -> separation holds across asset types, times, and thresholds
```

---

**JC1 — Regime-switching DC contrarian/trend-follower** [p.82–83, ch.6]

```
Under Normal Regime (mean reversion assumed):
  Rule 1:  In uptrend,   when TMV >=  2: open SHORT position
  Rule 2:  In downtrend, when TMV <= -2: open LONG position
  Rule 3:  When next DC Confirmation (DCC) point confirmed: CLOSE
  Rule 4:  When regime change to Abnormal detected: CLOSE

Under Abnormal Regime (momentum/margin cascades assumed):
  Rule 1a: In uptrend,   when TMV >=  2: open LONG (trend-follow)
  Rule 2a: In downtrend, when TMV <= -2: open SHORT (trend-follow)
  Rule 3a: When next DCC point confirmed: CLOSE
  Rule 4a: When regime change back to Normal detected: CLOSE
```

---

**JC2 — Regime-gated DC contrarian (preferred for drawdown reduction)** [p.83–84, ch.6]

```
Under Normal Regime:
  Rule 1: In uptrend,   when TMV >=  2: open SHORT
  Rule 2: In downtrend, when TMV <= -2: open LONG
  Rule 3: When regime change to Abnormal detected: CLOSE position
Under Abnormal Regime: NO TRADES (sit out)
Resume trading when Normal regime is restored.
```

---

**CT1 — Baseline contrarian (no regime information)** [p.84, ch.6]

```
Rule 1: In uptrend,   when TMV >=  2: open SHORT
Rule 2: In downtrend, when TMV <= -2: open LONG
Rule 3: When next DCC point confirmed: CLOSE
(No regime awareness — used as benchmark for JC1/JC2)
```

---

### Pitfalls e Anti-patterns

- [p.94, ch.7] Using only time-series analysis for regime detection — this misses intra-day regime changes that DC captures (e.g., the 14 July 2016 EUR-GBP regime change linked to Theresa May becoming PM was not detected under time series) [p.29, ch.3].

- [p.1, ch.1; p.94, ch.7] Assuming fixed-interval sampling captures all significant market shifts — in 24h FX markets, important events occur within intervals and are diluted in daily closes.

- [p.88–89, ch.6] Expecting JC1/JC2 to beat the control CT1 in total wealth — they do NOT. JC1 and JC2 are consistently inferior to CT1 in profitability across all 3 indices × 3 trading thresholds (with one exception: FTSE 100 at threshold 0.006). The advantage is exclusively in **maximum drawdown reduction**.

- [p.92, ch.6] Treating JC1/JC2 as production-ready strategies — the authors explicitly call them "naïve/primitive" and "proof of concept." The regime tracking information is proposed as an add-on to more sophisticated algorithms like the Alpha Engine.

- [p.73, ch.5] Expecting B-Simple to generate persistent regime signals — the rule generates repeated intermittent alarms because it uses only the current (TMV, T) reading without Markov memory. Traders should react on the first alarm, not wait for persistence.

- [p.55–57, ch.4] Assuming results are threshold-independent everywhere — in some markets (FX, Chinese stocks) regime positions in indicator space shift with θ; in others (stock indices, oil) they do not. The **separability** between Regime 1 and Regime 2 holds across thresholds, but absolute positions may vary.

- [p.76, ch.5] Expecting zero-lag detection — typical delays in tracking experiments range from +9 days behind to -6 days ahead; the average is early or on-time but perfect synchrony is not guaranteed.

- [p.25, ch.3] Using a 2-state HMM for long time horizons — only justified for short periods like the 2-month Brexit window. For multi-year analysis, more states may be needed and model selection criteria (BIC/AIC) should be applied.

- [p.203, ch.4 — implicit in methodology] Min-max normalisation using the full dataset's range leaks future information in production: max/min of TMV and T are only known at end of sample. Authors do not address this look-ahead issue explicitly.

---

---

## From `books/sentiment_analysis_handbook.md`

### Regras de Trading Explícitas

- **REGRA [p.705]**: Filtre notícias antes de qualquer modelo: `relevance >= 0.75` AND `novelty <= 1`. Menor que isso = story é peripheral (firma só mencionada) ou stale (repete história das últimas 24h).
- **REGRA [p.372]**: Estratégia Macquarie EPR — go LONG on (positive earnings surprise) AND (positive abnormal tone); go SHORT on the mirror; rebalance quarterly; hold day 2 to day 60.
- **REGRA [p.362-363]**: 10-K complexity signal — SHORT high-complexity names (top quintile), especially for short-horizon sleeves. Only HIGH complexity underperforms; low-complexity names don't over-perform symmetrically.
- **REGRA [p.52]**: News impact decays to zero within 2–5 days on price/beta (Patton & Verardo 2012) and ≈ 7 days on volatility (Mitra et al. 2009). Do NOT treat a news event as permanently informative.
- **REGRA [p.53]**: Accumulate positive and negative impact streams SEPARATELY. Never net positive against negative sentiment — exact cancellation would hide true newsflow intensity.
- **REGRA [p.44-45]**: Do NOT discard neutral-sentiment items: they contribute to newsflow, which itself has predictive content for volatility/beta.
- **REGRA [p.64]**: Use the Loughran-McDonald finance dictionary instead of the Harvard General Inquirer for financial text — ~75% of Harvard "negative" words are not actually negative in finance context [p.47, p.361].
- **REGRA [p.698, ch.20]**: Monitor OPTIONS volume as a leading indicator: options volume rises ≈ 7× (vs ~17% in equities) in the hour BEFORE firm-specific news on Dow 30 names, signalling informed trading.
- **NUNCA [p.45]**: Extrair sentiment de somente uma fonte (ex.: apenas Twitter) para decisões de trading — Derwent Capital's Twitter-only hedge fund closed within 12 months of launch [p.42].

### Fórmulas / Equações

**Tone probability decomposition (Thomson Reuters RNSE)** [p.704]

$$p_{\text{pos}} + p_{\text{neg}} + p_{\text{neu}} = 1$$

Each firm in a multi-firm article receives its own triplet based on the words used to describe that firm [p.704].

**Filter thresholds used by practitioners (Sinha & Dong, ch.20)** [p.705]

$$\text{relevance} \ge 0.75 \quad \text{AND} \quad \text{novelty} \le 1$$

Justification: relevance ≥ 0.75 keeps stories where firm is the focus (not mentioned in passing); novelty ≤ 1 filters stale repeats within last 24h.

**Impact measure (conceptual formulation)** [p.52-53]

Positive and negative sentiments accumulated separately to avoid cancellation:

$$\text{Impact}^{+}(t) = \sum_{i: s_i > 0} s_i \cdot e^{-\lambda (t - t_i)}$$

$$\text{Impact}^{-}(t) = \sum_{i: s_i < 0} s_i \cdot e^{-\lambda (t - t_i)}$$

where $s_i$ is the sentiment score of news item $i$ arriving at $t_i$, and $\lambda$ controls decay. Empirically, decay observed in the range of 2–5 days (Patton & Verardo 2012) up to 7 days (Mitra, Mitra & diBartolomeo 2009) [p.52]. The exact equation form is described verbally; this is a reconstruction of the described "exponential decay + accumulation" procedure [p.53].

**Residual complexity signal (Brar, De Rossi, Kalamkar — Macquarie)** [p.362]

$$\text{Complexity}_{i,t} = f(\text{word count}, \text{words/sentence}, \text{complex words/sentence})$$

$$\text{Signal}_{i,t} = \text{Complexity}_{i,t} - \hat{\alpha} - \hat{\beta}_1 \text{Size}_{i,t} - \hat{\beta}_2 \text{AssetGrowth}_{i,t} - \sum_s \hat{\gamma}_s \text{Sector}_s$$

Residual after stripping size, asset growth and sector effects; used as cross-sectional signal [p.362].

**Abnormal tone (Macquarie EPR strategy)** [p.369]

$$\text{Tone}_{i,t} = \alpha + \beta \cdot \text{EarnSurprise}_{i,t} + \varepsilon_{i,t}$$

$$\text{AbnormalTone}_{i,t} = \hat{\varepsilon}_{i,t}$$

Residual = soft-information signal orthogonal to hard earnings surprise [p.369].

**Garcia (2013) empirical effect size** [p.65]

A one standard-deviation increase in media pessimism ⇒ ≈ **−9 bps** stock return next day, over 80 years of NYT financial articles (~27,500 trading days); effect concentrated in recessions, Mondays, and day after holidays (~1/3 of sample) [p.65].

### Algoritmos e Pseudocódigo

**Sentiment classification pipeline (general, per ch.1.2 and ch.9)** [p.47-48]

```
Input: news story text T
Step 1 — Preprocess: [p.47]
   tokenise and apply document-term matrices (Bag-of-Words) [p.47]
   handle negation (Das & Chen 2007 negation tagging) [p.47]
   optionally keep bigrams / n-grams [p.64]
Step 2 — Score: [p.47-48]
   Option A (lexicon / Bag-of-Words):
     count positive / negative words using LM dictionary [p.361]
     tone = (pos - neg) / total
   Option B (Bayes / SVM):
     train on human-labelled corpus [p.48]
     assign P(class | words); pick argmax class [p.48]
   Option C (Machine learning / NLP):
     sentence-level classification preserving syntax [p.47]
Step 3 — Aggregate at document level: [p.374]
     doc_tone = (#pos_sentences - #neg_sentences) / total_sentences  [p.374]
Step 4 — Tag output with: timestamp, entity_id, relevance, novelty, tone [p.55]
Step 5 — Filter for downstream: relevance >= 0.75 AND novelty <= 1  [p.705]
```

**Macquarie "abnormal tone + earnings surprise" trading strategy** [p.372]

```
Each quarter, for each stock i:
  Step 1 — Observe reported EPS vs consensus -> EarnSurprise_i [p.367]
  Step 2 — Extract tone from Earnings Press Release (EPR) via bag-of-words / LM dict [p.369]
  Step 3 — Regress tone on EarnSurprise across cross-section [p.369]
     -> AbnormalTone_i = residual
  Step 4 — Form portfolio: [p.372]
       LONG  if EarnSurprise > 0 AND AbnormalTone > 0
       SHORT if EarnSurprise < 0 AND AbnormalTone < 0
  Step 5 — Hold 3 months (day 2 to day 60 to avoid announcement-day effects) [p.369]
  Step 6 — Rebalance quarterly [p.372]
Observed: improves raw and risk-adjusted returns in US large-caps [p.372]
```

**Impact-measure aggregation (exponential decay + accumulation)** [p.53]

```
for each asset a at time t:
  Impact_pos(a, t) = 0
  Impact_neg(a, t) = 0
  for each news item i relevant to a with timestamp t_i < t:
    s_i = sentiment_score(i)
    decay = exp(-lambda * (t - t_i))
    if s_i > 0:
      Impact_pos(a, t) += s_i * decay
    elif s_i < 0:
      Impact_neg(a, t) += s_i * decay
  # keep positive and negative sums SEPARATE — do not net them
  return Impact_pos, Impact_neg
```
Rationale: exact cancellation would misrepresent the situation as "no news" [p.53].

**Information-share via Hasbrouck (1995) for options vs equity** [p.699]

```
Given (Hasbrouck information share inputs) [p.699]:
  option-implied stock price series from ATM call/put [p.699]
  actual stock price series [p.699]
  5-minute intervals covering 200 min before, 400 min after news [p.699]
Steps:
  Step 1 — Map news arrival to 5-min interval [p.705]
  Step 2 — Build VECM on the two price series [p.699]
  Step 3 — Compute Hasbrouck information share of option-implied price [p.699]
Conditional result: IS rises from 14% (unconditional) to 27% around news [p.698]
```

### Pitfalls e Anti-patterns

- **[p.64] Large K → spurious results.** Text data has as many covariates as words in the language (×n-grams). Probability of spurious patterns grows with K. Nyman et al. (2014) cited as warning.
- **[p.65] Large N ≠ precision.** Garcia (2013) had 27,500 trading days but the full effect was concentrated in only ~1/3 of observations (recessions, Mondays, day-after-holidays). Sample size gives illusion of robustness.
- **[p.65-66] Small T (time) is the real bottleneck.** Financial crises are rare; predicting them with textual data runs into the same small-T problem as regime models.
- **[p.66] Survivorship bias in text.** US went from 1,800 daily newspapers (1940) to 1,382 (2013). Cross-section of text today ≠ cross-section in the past — using current media footprint to infer old readership patterns is misleading.
- **[p.66] Words change meaning.** "Awful" was positive until mid-20th century. Historical lexicon-based scores can silently drift.
- **[p.47] Naïve bag-of-words mis-handles negation and context.** "The figure is not encouraging" can be scored positive. Must apply negation tagging (Das & Chen 2007) or move to sentence-level models.
- **[p.64] Ex-ante dictionary selection creates hidden bias.** Even "fix" of using LM (built from 10-Ks) may not generalise to earnings transcripts, social media, or analyst notes. Hanley & Hoberg (2010) use alternative dictionaries — indication the field is not settled.
- **[p.66-67] Ioannidis (2005) conditions for false-positive research are ALL satisfied for textual finance**: small effect size, flexibility in design, many teams chasing significance, financial incentives. Expect high false-positive rate in published sentiment-alpha claims.
- **[p.67-68] Data-mining culture clash.** Finance traditionally distrusts data mining (Black 1993) while ML embraces it (Hand 2001); naïve textual-finance work imports ML tools without the finance discipline of out-of-sample testing.
- **[p.42] Derwent Capital's Twitter-only hedge fund** — single-source sentiment fund shut down within 12 months. Single-source alpha claims are fragile.
- **[p.362] Complexity signal: only the SHORT side works.** Cross-sectional asymmetry means long-only investors cannot fully exploit; real backtest must be long/short or short-only.
- **[p.374] Subjective ex-ante word-list** contaminates out-of-sample evaluation (Li 2010 critique).

---

## From `books/data_driven_science.md`

### Regras de Trading Explícitas

N/A — This chapter is a pedagogical treatment of Reinforcement Learning for general dynamical systems, control, robotics, and board/video games. It does NOT discuss trading, asset pricing, portfolio optimization, execution, or any financial-market application. No trading rule ("if X then Y") is stated anywhere in the extracted pages. Applying RL to trading would require additional domain knowledge (reward function design, state/action spaces for markets, transaction costs, non-stationarity) that is not covered here. For explicit trading rules see `systematic_trading.md` or `evidence_based_ta.md`.

### Fórmulas / Equações

**Policy as conditional probability** [p.3, eq.11.1]

$$\pi(s, a) = \Pr(a = a \mid s = s)$$

**Markov transition and reward** [p.4, eq.11.3-11.4]

$$P(s', s, a) = \Pr(s_{k+1} = s' \mid s_k = s, a_k = a)$$
$$R(s', s, a) = \Pr(r_{k+1} \mid s_{k+1} = s', s_k = s, a_k = a)$$

**Markov process as linear map** [p.5, eq.11.6]

$$s' = T s$$

- $T$ = stochastic transition matrix; each column sums to 1.

**Value function (discounted future reward)** [p.6, eq.11.8-11.9]

$$V^{\pi}(s) = \mathbb{E}\left( \sum_{k} \gamma^k r_k \mid s_0 = s \right)$$

$$V(s) = \max_{\pi} \mathbb{E}\left( \sum_{k=0}^{\infty} \gamma^k r_k \mid s_0 = s \right)$$

- $\gamma$ = discount factor ∈ (0,1); "future rewards are discounted, reflecting the economic principle that current rewards are more valuable than future rewards" [p.6].

**Bellman equation** [p.6, eq.11.11]

$$V(s) = \max_{\pi} \mathbb{E}\bigl( r_0 + \gamma V(s') \bigr)$$

$$\pi = \arg\max_{\pi} \mathbb{E}\bigl( r_0 + \gamma V(s') \bigr)$$

**Policy iteration update** [p.13, eq.11.13b-11.14]

$$V^{\pi}(s) = \sum_{s'} P(s' \mid s, \pi(s))\bigl( R(s', s, \pi(s)) + \gamma V^{\pi}(s') \bigr)$$

$$\pi(s) = \arg\max_{a \in A} \mathbb{E}\bigl( R(s', s, a) + \gamma V^{\pi}(s') \bigr)$$

**Value iteration update** [p.13, eq.11.15]

$$V(s) = \max_{a} \sum_{s'} P(s' \mid s, a)\bigl( R(s', s, a) + \gamma V(s') \bigr)$$

**Quality function** [p.14, eq.11.17]

$$Q(s, a) = \sum_{s'} P(s' \mid s, a)\bigl( R(s', s, a) + \gamma V(s') \bigr)$$

$$\pi(s, a) = \arg\max_{a} Q(s, a), \qquad V(s) = \max_{a} Q(s, a)$$

**Monte Carlo cumulative reward and V update** [p.15, eq.11.19-11.20]

$$R_{\Sigma} = \sum_{k=1}^{n} \gamma^k r_k$$

$$V^{\text{new}}(s_k) = V^{\text{old}}(s_k) + \frac{1}{n}\bigl( R_{\Sigma} - V^{\text{old}}(s_k) \bigr)$$

**Monte Carlo Q update with learning rate α** [p.16, eq.11.22]

$$Q^{\text{new}}(s_k, a_k) = Q^{\text{old}}(s_k, a_k) + \alpha\bigl( R_{\Sigma} - Q^{\text{old}}(s_k, a_k) \bigr)$$

- $\alpha \in [0, 1]$. "Larger learning rates α > 1/n will favor more recent experience" [p.16].

**TD(0) update** [p.17, eq.11.24]

$$V^{\text{new}}(s_k) = V^{\text{old}}(s_k) + \alpha\bigl( \underbrace{r_k + \gamma V^{\text{old}}(s_{k+1})}_{\text{TD target}} - V^{\text{old}}(s_k) \bigr)$$

**TD(n) n-step target** [p.17, eq.11.26b]

$$R^{(n)}_{\Sigma} = \sum_{j=0}^{n} \gamma^j r_{k+j} + \gamma^{n+1} V(s_{k+n+1})$$

**TD-λ target** [p.18, eq.11.27, Sutton 1988]

$$R^{\lambda}_{\Sigma} = (1 - \lambda) \sum_{n=1}^{\infty} \lambda^{n-1} R^{(n)}_{\Sigma}$$

**SARSA(0) update (on-policy TD for Q)** [p.19, eq.11.29]

$$Q^{\text{new}}(s_k, a_k) = Q^{\text{old}}(s_k, a_k) + \alpha\bigl( r_k + \gamma Q^{\text{old}}(s_{k+1}, a_{k+1}) - Q^{\text{old}}(s_k, a_k) \bigr)$$

**Q-learning update (off-policy TD for Q)** [p.19, eq.11.32]

$$Q^{\text{new}}(s_k, a_k) = Q^{\text{old}}(s_k, a_k) + \alpha\bigl( r_k + \gamma \max_{a} Q(s_{k+1}, a) - Q^{\text{old}}(s_k, a_k) \bigr)$$

**Policy gradient (log-likelihood trick)** [p.21, eq.11.34d]

$$\nabla_{\theta} R_{\Sigma, \theta} = \mathbb{E}\bigl( Q(s, a)\, \nabla_{\theta} \log \pi_{\theta}(s, a) \bigr)$$

**Policy parameter update** [p.21, eq.11.35]

$$\theta_{\text{new}} = \theta_{\text{old}} + \alpha \nabla_{\theta} R_{\Sigma, \theta}$$

**Deep Q Network loss** [p.24, eq.11.38]

$$L = \mathbb{E}\left[ \bigl( r_k + \gamma \max_{a} Q(s_{k+1}, a_{k+1}, \theta) - Q(s_k, a_k, \theta) \bigr)^2 \right]$$

**Dueling DQN decomposition** [p.24, eq.11.39]

$$Q(s, a, \theta) = V(s, \theta_1) + A(s, a, \theta_2)$$

**Advantage Actor-Critic (A2C) update** [p.25, eq.11.41]

$$\theta_{k+1} = \theta_k + \alpha \nabla_{\theta}\bigl( \log \pi(s_k, a_k, \theta)\, Q(s_k, a_k, \theta_2) \bigr)$$

**Nonlinear dynamics / cost functional (optimal control)** [p.32, eq.11.42-11.43]

$$\frac{d}{dt} x = f(x(t), u(t), t)$$

$$J(x(t), u(t), t_0, t_f) = Q(x(t_f), t_f) + \int_{t_0}^{t_f} L(x(\tau), u(\tau))\, d\tau$$

**Hamilton-Jacobi-Bellman (HJB) equation** [p.33, eq.11.45]

$$-\frac{\partial V}{\partial t} = \min_{u(t)}\left( \left(\frac{\partial V}{\partial x}\right)^T f(x(t), u(t)) + L(x(t), u(t)) \right)$$

- V(x,t,t_f) is the value function / "cost-to-go" assuming optimal control [p.33].
- LQR Riccati equation is a special case of the HJB equation [p.34].

**Discrete-time Bellman** [p.35, eq.11.55]

$$V(x) = \min_{u}\bigl( L(x, u) + V(F(x, u)) \bigr)$$

$$\pi(x) = \arg\min_{u}\bigl( L(x, u) + V(F(x, u)) \bigr)$$

### Algoritmos e Pseudocódigo

**Policy Iteration** [p.12-13, §policy iteration]

```
Input: MDP (S, A, P, R), discount γ, tolerance tol
[1] Initialize policy π arbitrarily.
[2] Repeat:
   a. Policy evaluation: iterate V^π(s) = Σ_s' P(s'|s, π(s)) [R(s',s,π(s)) + γ V^π(s')]
      for all s ∈ S until V converges.
   b. Policy improvement: for all s ∈ S,
         π(s) ← argmax_{a ∈ A} E(R(s',s,a) + γ V^π(s'))
   c. If π and V both changed less than tol, break.
[3] Return (π, V).
# Note: "expensive and prone to finding local minima" [p.13].
```

**Value Iteration** [p.13, eq.11.15-11.16]

```
Input: MDP, γ, tol
[1] Initialize V(s) ← 0 (or random) for all s ∈ S.
[2] Repeat:
   For all s ∈ S:
      V(s) ← max_a Σ_s' P(s'|s,a) [R(s',s,a) + γ V(s')]
[3] Until max_s |V_new(s) - V_old(s)| < tol.
[4] Extract policy: π(s,a) = argmax_a Σ_s' P(s'|s,a) [R(s',s,a) + γ V(s')]
# "Value iteration typically requires fewer steps per iteration; policy iteration
#  often converges in fewer iterations" [p.14].
```

**Monte Carlo Q-learning (episodic)** [p.15-16, eq.11.19-11.22]

```
Input: episode horizon n, γ, learning rate α
[1] Initialize Q(s,a) arbitrarily for all (s,a).
[2] For each episode:
   a. Run policy π (ε-greedy over current Q) for n steps;
      record trajectory (s_1,a_1,r_1,...,s_n,a_n,r_n).
   b. Compute R_Σ = Σ_{k=1}^n γ^k r_k
   c. For each visited (s_k, a_k):
         Q(s_k, a_k) ← Q(s_k, a_k) + α [R_Σ - Q(s_k, a_k)]
[3] Return Q.
```

**Q-Learning (off-policy TD)** [p.19, eq.11.32; §11.3]

```
Input: learning rate α, discount γ, exploration ε
[1] Initialize Q(s,a) for all (s,a).
[2] For each episode:
   Observe initial state s.
   While not terminal:
      a. With prob. 1−ε: a ← argmax_a Q(s,a); else a ← random.   # ε-greedy [p.20]
      b. Take action a, observe reward r and next state s'.
      c. Q(s,a) ← Q(s,a) + α [ r + γ max_a' Q(s', a') − Q(s,a) ]
      d. s ← s'
[3] Typically: anneal ε toward 0 over training [p.21].
```

**SARSA (on-policy TD)** [p.18-19, eq.11.29]

```
Initialize Q(s,a); choose s; a ← ε-greedy(Q, s).
While not terminal:
   Take action a, observe r, s'.
   a' ← ε-greedy(Q, s').
   Q(s,a) ← Q(s,a) + α [ r + γ Q(s', a') − Q(s,a) ]     # uses ACTUAL next action
   s ← s';  a ← a'.
```

**Deep Q Network (DQN) with experience replay** [p.23-24, eq.11.38, ref. 519]

```
Input: replay buffer D, batch size B, target-update period τ
[1] Initialize Q-net Q_θ, target net Q_{θ^-} with θ^- ← θ.
[2] For each episode / step:
   a. Act ε-greedily from Q_θ; observe (s, a, r, s'); store in D.
   b. Sample batch of B transitions from D (optionally prioritized by TD error [p.24]).
   c. For each sample: y = r + γ max_a' Q_{θ^-}(s', a')
   d. Loss L = (1/B) Σ [ y − Q_θ(s,a) ]^2    # eq. 11.38
   e. SGD step on θ.
   f. Every τ steps: θ^- ← θ.    # double-DQN stability [p.24]
```

**REINFORCE-style Policy Gradient** [p.21-22, eq.11.34-11.35]

```
Input: parameterized policy π_θ, learning rate α
[1] Sample trajectory τ = (s_1,a_1,r_1,...,s_T,a_T,r_T) under π_θ.
[2] For each step k: compute return G_k = Σ_{j≥k} γ^{j-k} r_j   (or advantage Q(s_k,a_k))
[3] Gradient estimate: ĝ = Σ_k G_k · ∇_θ log π_θ(s_k,a_k)
[4] θ ← θ + α · ĝ
# Variants: natural policy gradients [p.22, ref. 377]; REINFORCE [p.22, ref. 770]
```

**Advantage Actor-Critic (A2C)** [p.25, eq.11.41]

```
Initialize actor π_θ (deep policy net) and critic Q_{θ₂} (DDQN).
Loop:
   a. Actor draws action a ~ π_θ(s).
   b. Observe (r, s').
   c. Critic TD update on Q_{θ₂}.
   d. Actor update: θ ← θ + α ∇_θ[ log π_θ(s,a) · Q_{θ₂}(s,a) ]
```

### Pitfalls e Anti-patterns

- **Curse of dimensionality in dynamic programming** [p.11-12]: "For even moderately large problems, [Bellman backup] suffers from the curse of dimensionality, and approximate solution methods must be employed" [p.12]. Chess has combinatorially large state spaces (Shannon number ≈ 10^120 [p.25]) that make tabular Q infeasible.
- **Policy iteration is expensive and prone to local minima** [p.13]: "This procedure is both expensive and prone to finding local minima. It also resembles the alternating descent method."
- **Monte Carlo learning is sample-inefficient for sparse rewards** [p.15]: "For this reason, Monte Carlo learning is typically quite sample inefficient, especially for problems with sparse rewards."
- **Off-policy Monte Carlo methods** [p.16]: "In general, they are quite inefficient or unfeasible."
- **TD learning introduces bias** [p.18, §bias-variance tradeoff]: "The sampled TD target is a biased estimate, because it uses sub-optimal actions and the current imperfect estimate of the value function."
- **Q-learning vs. SARSA safety tradeoff** [p.19]: "In safety-critical applications, such as self-driving cars or other applications where there can be catastrophic failure, SARSA will typically learn less optimal solutions, but with a better safety margin, since it is maximizing on-policy rewards." Q-learning "will learn a more optimal solution faster than SARSA, but with more variance in the solution."
- **Reward shaping ceiling** [p.26]: Reward shaping "is not a viable strategy for a generalized artificial intelligence agent capable of learning multiple games or tasks. In addition, reward shaping generally limits the upper end of the agent's performance to that of the human expert."
- **Curiosity reward fails in stochastic/chaotic environments** [p.27]: "A naive novelty reward would constantly provide positive incentive to explore these regions, since the forward model will not improve." Remedy: predicate novelty on predictability via latent autoencoder features [p.27, ref. 562].
- **RL is expensive and potentially unsafe** [p.6-7]: "Reinforcement learning may be very expensive to train, and it might not be the right strategy for problems where testing a policy is expensive or potentially unsafe. Similarly, in many cases, there are simpler control strategies than RL, such as LQR or MPC; when these approaches are effective, they are often preferable" [p.7].
- **RL assumptions may not hold** [p.7]: "Many real world applications do not satisfy [MDP] assumptions. For example, the dynamics may depend on the state history or on hidden or latent variables. Similarly, the evolution dynamics may be entirely deterministic, yet chaotic."
- **Credit assignment problem** [p.7]: Six decades old, still unsolved in general. Sparse/delayed rewards make it computationally intractable to know which action sequence caused the eventual reward.
- **HJB curse of dimensionality** [p.34-35]: "A nonlinear control problem with a three-dimensional state vector x ∈ R^3 will result in a three-dimensional PDE. Thus, optimal nonlinear control based on the HJB equation typically suffers from the curse of dimensionality."
- **Double-DQN target-network instability** [p.24]: "It may be necessary to fix the target network for multiple training iterations of the prediction network before updating to improve stability and convergence" [ref. 264].

---
