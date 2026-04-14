# Handbook of Sentiment Analysis in Finance

## Metadata
- **Autor:** Gautam Mitra and Xiang Yu (Editors) [p.2]
- **Ano:** 2016 [ch.1, preface reference to "last 5 years" since 2011 Handbook, p.20]
- **Editora:** OptiRisk Systems Ltd / Albury Books (compiled at OptiRisk, London) [p.23]
- **Páginas:** 893
- **ISBN:** N/A — not present in extracted frontmatter
- **Foco principal:** Survey/handbook of how textual sentiment metadata (news, social media, search) is extracted and applied across asset classes and trading horizons.

## 1. Tese Central

Sentiment metadata (SMD) — derived from newswires, social media, microblogs, and online search — adds measurable predictive value to financial models **on top of** market data, but adds nothing on its own; the value emerges when SMD is combined with traditional market inputs to enhance predictive models, regime detection, ex-ante decision models, and ex-post risk control [ch.1, p.42, p.50-51]. The book extends the earlier *Handbook of News Analytics in Finance* (2011) by incorporating NLP, social media, online search as sources, and by widening coverage to bonds, FX, commodities in addition to equities [p.20-22].

A second tethering claim: sentiment analysis operates at the interface of EMH and behavioural finance — the existence of exploitable sentiment signals constitutes evidence of "market anomalies" caused by behavioural biases (over/under reaction, prospect theory) rather than full informational efficiency [p.50].

## 2. Conceitos-Chave

- **Sentiment score** — a real number in a fixed range (e.g. 0–100 or −1..+1) summarising the positive/negative polarity of a news item; the midpoint represents neutral sentiment which is NOT discarded because it contributes to newsflow [p.44-45].
- **Sentiment Metadata (SMD)** — structured tagged record produced from unstructured text: timings, entity tags, relevance, novelty, sentiment score; meant for machine consumption in financial models [p.55].
- **Newsflow** — volume of news items arriving per time bucket; shown to affect asset behaviour independently of sentiment polarity [p.45, p.52].
- **Impact measure** — distinct from sentiment score; quantifies how news sentiment affects asset price, volatility and liquidity over time, combining exponential decay with accumulation [p.52-53].
- **Curated vs un-curated information** — curated = newswires with editorial oversight, macro announcements, company filings; un-curated = microblogs (Twitter), Google/Wikipedia search data [p.20].
- **Synchronous vs asynchronous news** — macro announcements are scheduled (synchronous) with known timing but unknown polarity; general news is asynchronous (both timing and polarity unknown) [p.54].
- **Relevance score** — how much a story is about a given entity; 0.33 ≈ 3 firms mentioned; practitioners filter with relevance ≥ 0.75 [p.705 / ch.20].
- **Novelty score** — measures uniqueness vs prior articles in last 12–24h; novelty = 1 indicates a similar story existed in last 24h; practitioners filter with novelty ≤ 1 [p.705 / ch.20].
- **Tone of the article** — RNSE produces three probabilities (positive, negative, neutral) summing to 1 [p.704].
- **Bag-of-Words** — document-term matrix of word frequencies, used by Tetlock et al. (2008); simplest technique, still dominant despite limitations [p.47].
- **General Inquirer (GI) / Harvard Dictionary** — 77-category word-sentiment dictionary from psychology; Loughran & McDonald (2011) found ~3/4 of its "negative" words are not actually negative in a financial context [p.47].
- **Loughran-McDonald (LM) dictionary** — finance-specific positive/negative wordlist built from 10-K filings; now de-facto standard in finance textual analysis [p.64, p.361].
- **Complexity / Fog Index** — Li (2010) weighted function of avg sentence length and complex words; proxy for 10-K obfuscation, negatively correlated with future stock returns [p.362].
- **Abnormal tone** — residual of regressing EPR tone on earnings surprise; isolates soft-information signal after removing correlation with hard earnings beat/miss [p.369].
- **Information share (Hasbrouck 1995)** — relative contribution of a venue (e.g. options-implied price) to eventual price discovery; internally consistent alternative to lead-lag [p.699].
- **Sentiment reversal / regime detection** — sentiment metadata improves regime-switching models by identifying shifts in market conditions [p.61].

## 3. Fórmulas / Equações

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

## 4. Algoritmos e Pseudocódigo

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

## 5. Regras de Trading Explícitas

- **REGRA [p.705]**: Filtre notícias antes de qualquer modelo: `relevance >= 0.75` AND `novelty <= 1`. Menor que isso = story é peripheral (firma só mencionada) ou stale (repete história das últimas 24h).
- **REGRA [p.372]**: Estratégia Macquarie EPR — go LONG on (positive earnings surprise) AND (positive abnormal tone); go SHORT on the mirror; rebalance quarterly; hold day 2 to day 60.
- **REGRA [p.362-363]**: 10-K complexity signal — SHORT high-complexity names (top quintile), especially for short-horizon sleeves. Only HIGH complexity underperforms; low-complexity names don't over-perform symmetrically.
- **REGRA [p.52]**: News impact decays to zero within 2–5 days on price/beta (Patton & Verardo 2012) and ≈ 7 days on volatility (Mitra et al. 2009). Do NOT treat a news event as permanently informative.
- **REGRA [p.53]**: Accumulate positive and negative impact streams SEPARATELY. Never net positive against negative sentiment — exact cancellation would hide true newsflow intensity.
- **REGRA [p.44-45]**: Do NOT discard neutral-sentiment items: they contribute to newsflow, which itself has predictive content for volatility/beta.
- **REGRA [p.64]**: Use the Loughran-McDonald finance dictionary instead of the Harvard General Inquirer for financial text — ~75% of Harvard "negative" words are not actually negative in finance context [p.47, p.361].
- **REGRA [p.698, ch.20]**: Monitor OPTIONS volume as a leading indicator: options volume rises ≈ 7× (vs ~17% in equities) in the hour BEFORE firm-specific news on Dow 30 names, signalling informed trading.
- **NUNCA [p.45]**: Extrair sentiment de somente uma fonte (ex.: apenas Twitter) para decisões de trading — Derwent Capital's Twitter-only hedge fund closed within 12 months of launch [p.42].

## 6. Pitfalls e Anti-patterns

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

## 7. Parâmetros Sensíveis

- **Decay half-life / horizon of news impact** [p.52]: 2–5 days (price, beta) per Patton & Verardo 2012 [p.52]; up to 7 days (volatility) per Mitra, Mitra & diBartolomeo 2009 [p.52]. Economically justified by trader attention span and story supersession, not curve-fit [p.52].
- **Relevance filter = 0.75**: [p.705] corresponds to a story where the firm is the clear subject (not one of ~3 firms equally mentioned at 0.33).
- **Novelty filter = 1 (max)**: [p.705] one similar story in last 24h is the cap; corresponds to 12-hour rolling window used by RNSE engine [p.705].
- **Holding window day 2 to day 60**: [p.369] Macquarie avoids t=0 / t=1 to remove announcement-day microstructure effects; 60 trading days ≈ one quarter = rebalance cadence.
- **Bayes classifier accuracy ceiling**: 60–70% vs human agreement 82–92% [p.51-52]. The gap justifies ongoing research into SVMs and deep models; it also means accuracy < 70% is the realistic baseline for any new classifier — beware papers claiming 90%+.
- **Bag-of-words text window**: early research limited to ≈ 50 words per piece [p.46]. Short windows are arbitrary — justification is operational, not economic.
- **Options-to-equity volume ratio around news**: options +700% vs equity +17% in hour before news (Dow 30) [p.698]. Parameter that can be monitored as a live signal, not one to optimise.
- **Unconditional vs conditional information share**: 14% vs 27% (options on news days) [p.698]. Calibration targets for options-based news models.
- **Effect size (Garcia 2013)**: −9 bps per 1σ pessimism [p.65]. Signal is small — execution costs must be ≪ 9 bps for the edge to survive.

## 8. Citações Literais Importantes

> "A salient aspect of using the sentiment meta data (SMD) is that just on its own the SMD does not improve the analytics application in finance… adding SMD as an additional information source to market data definitely achieves enhancements of predictive financial analytics models." — [p.42]

> "Derwent Capital used only Twitter data to make investment decisions; within 12 months of its launch the fund closed." — [p.42]

> "Loughran and McDonald (2011) found that three-quarters of words identified as negative in the Harvard Dictionary are not typically considered negative in a financial context." — [p.47]

> "With human scoring reaching average agreement levels of 82-92%, the hunt for better classifiers continues." — [p.52]

> "A research finding is less likely to be true … when there is greater flexibility in designs, definitions, outcomes, and analytical modes; when there is greater financial and other interest and prejudice; and when more teams are involved in a scientific field in chase of statistical significance." — Ioannidis (2005), quoted at [p.66]

> "We find that the trading volume in the options market, indicated by the number of contracts, increases by a factor of nearly 7 an hour before the news arrives, whereas the volume in the equity market … increases by merely 17%." — [p.698]

## 9. Conexões com Outros Livros Desta Base

- **Loughran-McDonald finance dictionary** [p.361, p.64] — same LM wordlist discussed as the de-facto standard in textual finance; any sibling book covering financial NLP should be cross-referenced. N/A for confirmed cross-refs — other summaries not inspected in this pass.
- **Regime detection via sentiment** [p.61] — connects to any regime-switching / HMM treatment in the base. Explicit cross-ref N/A in this pass.
- **Overfitting / false-positive discipline** [p.66-68, Ioannidis + Black critique] — same anti-overfit ethos as `advances_fin_ml.md` / `stat_sound_indicators.md` / `eval_opt_strategies.md` would treat; N/A for literal citation until those summaries are re-read.
- **Options information share around news** [p.698, ch.20] — touches on price-discovery literature present in `trading_exchanges.md` and HFT literature; explicit cross-ref N/A in this pass.
- Otherwise **N/A — cross-refs to other summaries deferred to a later consolidation pass** [ch.1].
