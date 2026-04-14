# Statistically Sound Machine Learning for Algorithmic Trading of Financial Instruments: Developing Predictive-Model-Based Trading Systems Using TSSB

## Extraction Scope Notice

This book's PDF pagination aligns such that the printed page number visible at the bottom of each text page equals `[PAGE N] - 16` for chapters (the first 16 PDF pages are unnumbered front matter: title, bio, TOC). Verified by cross-reference: the chapter "Introduction" starts at printed page 1 = `[PAGE 17]`, and the author's own in-text cross-reference "See Page 185 for the definition of profit factor" (seen at printed page 4 = `[PAGE 20]`) resolves to `[PAGE 201]` of the extraction, which in this book displays the printed number `185`. Therefore, all `[p.X]` citations in this summary refer to the **printed page number** (the one the author himself uses when cross-referencing). When a citation says `[p.96]`, the extracted text will show the content under `[PAGE 112]`. The TSSB program referenced throughout is Aronson & Masters' "Trading System Synthesis and Boosting" software, whose syntax conventions dominate the book. File names use the filename slug `stat_sound_indicators` despite the full title being mostly authored by Aronson — see Metadata.

## Metadata
- **Autor:** David Aronson (primary author), with Timothy Masters, Ph.D. (Technical Advisor) [p.i, p.iii — [PAGE 1], [PAGE 3]]
- **Ano:** 2013 [p.ii — [PAGE 2]]
- **Editora:** Self-published / CreateSpace (the companion Masters volume "Assessing and Improving Prediction and Classification" is published by CreateSpace 2013 [p.iii]); ISBN registry implies CreateSpace/Amazon.
- **Edition:** 1.20 [p.i]
- **Páginas:** 519 (PDF) / ~503 printed content pages (p.1-503) [metadata.json]
- **ISBN:** 978-1-4895-0771-6 [p.ii]
- **Foco principal:** [p.1-4] Design and statistical validation of market-prediction indicators and predictive models in the TSSB program. The book is simultaneously (a) a taxonomy of statistically sound indicators (trend, volatility, volume, entropy, wavelets, FTI, Mahalanobis, absorption ratio) and (b) a rigorous pipeline (MCPT, permutation training, walkforward, OOS portfolios) for isolating genuine Skill from Trend and Bias components of backtest returns.
- **TSSB download (at time of writing):** http://tssbsoftware.com/ [p.ii]
- **Note on title attribution:** [p.iii] This is Aronson's third book (after 2007 *Evidence-Based Technical Analysis*), produced jointly with Masters. Whereas *Evidence-Based TA* is pure theory and *Testing and Tuning* (Masters 2018) is pure C++ methodology, this volume is the practitioner's manual that bridges the two via the TSSB software.

## 1. Tese Central

The central claim is stated on [PAGE 17] (printed p.1) and reinforced at [p.43 — [PAGE 59]]: **"Intelligently designed automated trading systems can and often do outperform human-driven systems"** [p.1], but only when (i) indicators and targets are statistically sound (stationary, low-redundancy, high-entropy), (ii) model selection is protected against selection bias by Monte-Carlo Permutation Tests, and (iii) the total apparent return of any trained system is decomposed into Skill + Trend + Bias so that only the Skill component is claimed as edge. Aronson frames the entire TSSB program as the operational answer to the question posed in *Evidence-Based TA*: "how do we data-mine without being fooled by data-mining bias?" The answer he operationalizes is a two-part pipeline: indicator purification (PURIFY transform, cross-market normalization, pooled variables, historical adjustment) followed by TRAIN PERMUTED, which shuffles the underlying market bar-changes and retrains the entire system hundreds of times in order to read out Bias directly as an estimate rather than a hand-waved correction [ch. "Permutation Training", p.299-310].

Aronson's working principle, stated at [p.1] and reiterated across chapters: "Intelligent modeling software can discover patterns that are so complex or buried under random noise that no human could ever see them" [p.2] — but this discovery *requires* statistical infrastructure, not just computation. Indicator selection without MCPT "can be severe, causing worthless predictors to be selected" [p.170].

## 2. Conceitos-Chave

- **Indicator** — variable that looks strictly backwards in time; must be computable in realtime at every bar from available history [p.3].
- **Target (dependent variable)** — variable that looks strictly forward in time; known only for historical bars and never for the current trading bar [p.3].
- **Threshold-based trade decision** — "If prediction ≥ long threshold, go long; if prediction ≤ short threshold, go short." TSSB auto-chooses thresholds by maximizing long-PF and short-PF separately subject to a min-trade-count constraint [p.4].
- **MIN CRITERION FRACTION** — lower bound on the fraction of bars that must generate a trade at the chosen threshold. Prevents the degenerate "one lucky trade" optimum [p.4, p.189].
- **Profit Factor** — sum of positive trade returns divided by absolute value of sum of negative returns. The default training criterion in TSSB [p.185].
- **Buy-and-hold PF / Sell-short-and-hold PF** — naive baseline PFs used as denominators to compute the **Improvement Ratio** = Outer long-only PF / Buy-and-hold PF [p.1064-1065 — printed p.X visible in the trade-sim output at [PAGE 300-305]].
- **Dual-thresholded outer PF** — PF that counts both long and short signals together, measured at the chosen thresholds. Master metric of a dual-direction system [p.1051-based descriptions, visible in output].
- **Stationarity (practical definition)** — "roughly speaking, stationarity means that the statistical properties of an indicator do not change over time" [p.87]. Masters' thesis that induced stationarity is mandatory for models is adopted wholesale here.
- **CENTER / SCALE / NORMALIZE (historical adjustment)** — operators that subtract historical median, divide by historical IQR, or both, using a user-specified lookback [p.87-89].
- **Cross-market normalization** — for each bar, rank indicator values across all markets in the universe and return (percentile − 50), giving a value in [-50, 50]. Requires minimum fraction of markets (e.g., 0.6) to be present [p.92].
- **Pooled Variable** — aggregate of an indicator across markets using MEDIAN, IQRANGE, SCALED MEDIAN, SKEWNESS, KURTOSIS, or CLUMP60 [p.93-94]. CLUMP60 measures conformity: if ≥60% of markets share the indicator's sign, returns the 40th percentile (positive side) or 60th percentile (negative side); otherwise zero [p.94].
- **CLOSE TO CLOSE variable** — 100 × log(close_t / close_{t-1}). Too nonstationary for prediction models, but the canonical input for Mahalanobis Distance and Absorption Ratio [p.108].
- **Mahalanobis Distance (turbulence indicator)** — multivariate distance of a vector of simultaneous market changes from its historical mean, using historical covariance, following Kritzman & Li ("Skulls, Financial Turbulence, and Risk Management", *Financial Analysts Journal* 66, Sep/Oct 2010) [p.96].
- **Absorption Ratio** — fraction of total cross-market covariance variance contained in the largest k eigenvalues; Kritzman et al. use 0.2 (20% of eigenvalues). Measures coherence/herding in the market [p.97].
- **Absorption Shift** — (short-MA of Absorption Ratio − long-MA), scaled by the long-period std of the absorption ratio [p.97].
- **LINEAR PER ATR / QUADRATIC PER ATR / CUBIC PER ATR** — Legendre polynomial coefficients (linear, quadratic, cubic) fitted to log(mean(O,H,L,C)) over HistLength, divided by ATR over ATRlength. The three coefficients capture price velocity, acceleration, and change-in-acceleration independently (orthogonality property) [p.99-100].
- **PRICE ENTROPY / VOLUME ENTROPY (WordLength)** — binary entropy of up/down patterns over contiguous WordLength bars, in a window of 10 × 2^WordLength bars [p.133].
- **PRICE MUTUAL INFORMATION (WordLength)** — mutual information between the current bar's binary change and the WordLength prior binary changes; window is 10 × 2^(WordLength+1) bars [p.133].
- **Morlet wavelet (REAL / IMAG / DIFF / PRODUCT)** — wavelet family that perfectly attains the Heisenberg uncertainty limit (best simultaneous localization in time and period) but is highly redundant. Lag is exactly 2 × Period. Minimum period is 2 bars (Nyquist) [p.135, p.137].
- **Daubechies wavelet (MEAN / MIN / MAX / STD / ENERGY / NL ENERGY / CURVE)** — non-redundant wavelet family at the opposite end of the continuum from Morlet; superior when spanning a full price series with few indicators but with poor time/period localization. HistLength must be a power of two, Level ∈ {1,2,3,4}, and 2^(Level+1) ≤ HistLength. Li, Shi & Li recommend HistLength ≈ 3× prediction horizon and Level=2 [p.141].
- **Follow-Through Index (FTI)** — Khalsa's measure: mean length of "legitimate" (non-noise) filtered price legs divided by channel width around filtered prices. Large FTI = strong follow-through (tradable trend); small FTI = noisy, mean-reverting [p.143-147].
- **FTI Channel Width** — measure of noise: pair of boundaries around the lowpass-filtered price series that enclose most (not necessarily all) observed deviations in the channel [p.147].
- **Channel Width Ratio (major/minor)** — ratio of minor-trend channel width to major-trend channel width; used as a state indicator [p.148-149].
- **Zero-lag lowpass filter (Khalsa)** — a filter using half of the full filter shape at the most recent data point (plus progressively more of the filter going back), trading frequency response for zero lag. Critical for FTI [p.146].
- **Chi-square test (predictor screening)** — partitions one predictor and one target into bins, computes χ², contingency coefficient, and Cramer's V; solo p-value (independent-test) plus optional unbiased p-value via MCPT [p.162-166].
- **Cramer's V** — superior nominal correlation coefficient ranging 0-1; used as the default sorting key for predictor screening [p.164].
- **Nonredundant predictor screening** — stepwise selection that picks the indicator maximizing **Uncertainty Reduction** (information-theoretic one-sided proportional measure), then picks the next indicator that adds the most predictive power *beyond* those already chosen [p.167-170]. The three measures it reports:
  - **100 × V** (Cramer's V) — symmetric, not proportional [p.168].
  - **100 × Lambda** — one-sided, proportional, but based on the heaviest-populated cells only [p.168].
  - **100 × UReduc (Uncertainty Reduction)** — one-sided, proportional, uses all cells. "The author considers this excellent" [p.168].
- **Inclusion p-value vs. Group p-value** — MCPT-based; inclusion-p tests the marginal contribution of the newly added predictor to the set, group-p tests the joint power of the entire set so far [p.168-169].
- **Selection bias** — "when we choose one or more trained models from among a group of competitors … some of the models will have been lucky … their luck, by definition, will not hold up in the future" [p.306].
- **Training bias** — the inflation of apparent performance caused by the model tuning itself to inauthentic patterns (noise) during training [p.302]. Quantified by TRAIN PERMUTED.
- **Components of Performance (Aronson decomposition)** — *Total = Skill + Trend + Bias* [p.302, Eq. 9]. Only *Skill* survives permutation.
- **Trend component** — return attributable to long/short imbalance in the presence of market drift; preserved under shuffling of bar-changes [p.303, Eq. 11-12].
- **Bias component** — return attributable to memorization of training noise; equal (on average) to the mean permuted return minus the Trend component [p.304, Eq. 13].
- **Benchmarked return (pure Skill)** — UnbiasedReturn − Trend = estimated true Skill [p.304, Eq. 15; sample output at p.305].
- **PURIFY transform** — linear-model-based subtraction of a predictable component of an indicator (the "pollutant", predicted by functions of a separately specified purifier series) so that the residual is the purified indicator. Aronson credits this method for his "Pure VIX" [p.iii, p.353-359].
- **Oracle (TSSB)** — weighted combiner of component models; the weights depend on a gate variable, so specialist models can be activated by regime (e.g., volatility) [p.253-262].
- **PRESCREEN vs. TRIGGER (regime specialization)** — two mechanisms: PRESCREEN trains each component model on its own regime subset but reports across all cases via an oracle combination; TRIGGER filters the entire dataset to one regime and trains/tests within [p.280-295].
- **IS vs. OOS Portfolio** — IS (in-sample) selects component models using training-set performance; OOS uses walkforward OOS performance. IS is dangerous because over-powerful models are preferentially picked on their overfit [p.306].
- **Pure VIX** — Aronson's applied case of PURIFY: VIX purified of its predictable component due to market price, leaving the residual "pure" volatility signal [p.iii, demonstrated at p.350-352].

## 3. Fórmulas / Equações

**Aronson Decomposition of Trading System Performance** [p.302, Eq. 9]

$$\text{Total Return} = \text{Skill} + \text{Trend} + \text{Bias}$$

Where:
- Skill = ability of the system to exploit authentic, repeatable market patterns [p.302].
- Trend = return attributable to long/short position imbalance × market long-term drift [p.302].
- Bias = return attributable to training exploiting inauthentic (noise) patterns [p.302].

**Expected return from a permuted (Skill-less) market** [p.303, Eq. 10]

$$\mathbb{E}[\text{Return}_{\text{permuted}}] = \text{Trend} + \text{Bias}$$

**Expected return from an unbalanced random long/short system (Trend component)** [p.303-304, Eq. 11-12]

$$\text{Trend} = \frac{\text{BarsLong} - \text{BarsShort}}{\text{TotalBars}} \cdot \sum_{i} \text{Target}_i$$

- $\text{BarsLong}, \text{BarsShort}$ = number of bars on which the system holds long vs. short positions [p.303].
- $\sum \text{Target}_i$ = sum of the target variable over the evaluation set (positive = uptrending market, negative = downtrending) [p.303].

**Estimated Training Bias (averaged across ≥100 permutation replications)** [p.304, Eq. 13]

$$\widehat{\text{Bias}} = \frac{1}{N_{\text{reps}}} \sum_{k=1}^{N_{\text{reps}}} \left( \text{Return}_k^{\text{permuted}} - \text{Trend}_k^{\text{permuted}} \right)$$

**Unbiased Return (= Skill + Trend)** [p.304, Eq. 14]

$$\text{UnbiasedReturn} = \text{Return}_{\text{original}} - \widehat{\text{Bias}}$$

**Benchmarked Return (pure Skill)** [p.304, Eq. 15]

$$\text{BenchmarkedReturn} = \text{UnbiasedReturn} - \text{Trend}_{\text{original}}$$

Sample audit-log output for this decomposition is shown on [p.305]:

```
Net profit factor p = 0.0600 return p = 0.0400
Training bias = 52.3346 (67.1255 permuted return minus 14.7909 permuted benchmark)
Unbiased return = 55.4320 (107.7665 original return minus 52.3346 training bias = skill + trend)
Benchmarked return = 39.8372 (55.4320 unbiased return minus 15.5947 original benchmark = skill)
```

**Monte-Carlo Permutation Test p-value** [p.301, unnumbered]

If among $N_{\text{reps}}$ training runs (one unpermuted, rest permuted), $k$ of the permuted runs achieve performance ≥ the unpermuted result, then

$$p = \frac{k + 1}{N_{\text{reps}}}$$

**Gietzen Reactivity Indicator** [p.105-106, Eq. 3-6]

Aspect ratio:
$$\text{AspectRatio} = \frac{\text{Range} / \text{SmoothedRange}}{\text{Volume} / \text{SmoothedVolume}}$$

Price change:
$$M = \text{Price}_0 - \text{Price}_{\text{HistLength}}$$

Raw reactivity:
$$\text{RawReactivity} = M \times \text{AspectRatio}$$

Reactivity:
$$\text{Reactivity} = \text{RawReactivity} / \text{SmoothedRange}$$

Smoothing constant for exponential MA equivalent to n-day simple MA: $\alpha = 2/(n+1)$ [p.106]. Khalsa uses smoothing ≈ 4 × trading cycle length.

**NEXT DAY LOG RATIO target** [p.156, Eq. 7]

$$\text{NextDayLogRatio} = 25000 \cdot \log\left(\frac{O_{+2}}{O_{+1}}\right)$$

- $O_{+1}, O_{+2}$ = opens of next and following bars. Normalization 250×100 gives approximate annualized percent for day bars [p.156].

**NEXT DAY ATR RETURN target** [p.157, Eq. 8]

$$\text{NextDayATRReturn} = \frac{O_{+2} - O_{+1}}{\text{ATR}(\text{Distance})}$$

- If Distance = 0, denominator is 1 (raw point return). ATR-normalization is "especially useful in multiple-market applications … it does an excellent job of ensuring conformity across markets" [p.157].

**HIT OR MISS target (Up, Down, Cutoff, ATRdist)** [p.158]

Returns +Up if the price moves up at least Up × ATR before moving down Down × ATR during the next Cutoff bars, −Down if the opposite, otherwise price-change ÷ ATR. Its two key properties: (1) "mimics real-life trading using limit and stop orders"; (2) "its distribution cannot have outliers" [p.158].

**Scaling transform (nonlinear compression to [-50, 50])** [p.88, Eq. 2]

Applied after centering and/or scaling by IQR to compress outliers and fix range; Φ is the standard normal CDF, F25/F50/F75 are historical 25th/50th/75th percentiles of the indicator. Form is proprietary to TSSB but the design goal is explicit: range-fix + outlier-compress while preserving monotonicity.

## 4. Algoritmos e Pseudocódigo

**Nonredundant Predictor Screening (stepwise with MCPT)** [p.167-170, 173-178]

```
Input:
  predictors P[1..M], target T
  Nbins_pred, Nbins_target (or tail_frac if TAILS)
  Nreps for MCPT
  max_keep (default 8)

Output:
  ordered list of selected predictors with (Cramer's V, Lambda, UReduc, Inc_pval, Grp_pval)

Step 1: For each predictor p in P:
     partition p into Nbins_pred equal-count bins (or 2 tail bins)
     partition T into Nbins_target bins (equal, or split-at-zero)
     build contingency table C(p, T)
     compute V(p), Lambda(p), UReduc(p)
     base_score(p) = UReduc(p)   # default criterion

Step 2: Pick best = argmax base_score(p); selected = {best}

Step 3: For step k = 2 .. max_keep:
     for each remaining candidate p:
         build joint contingency over (selected + [p]) × T
         compute incremental UReduc(selected, p) = UReduc(selected+{p}) - UReduc(selected)
     if all incremental contributions ≈ 0 or mean-cell-count < 5:
         emit warning "results below this line are suspect due to small mean cell count"
     p_k = argmax incremental UReduc
     append p_k to selected

Step 4: MCPT loop (if MCPT=Nreps appended):
     for rep = 1..Nreps-1:
         shuffle T (random permutation of target over cases)
         run steps 1-3 recording max incremental UReduc per step
     for each selected predictor p_k:
         Inc_pval(p_k) = (# reps where permuted incremental ≥ real incremental + 1) / Nreps
         Grp_pval(p_k) = (# reps where permuted cumulative UReduc of best-k ≥ real cum UReduc of selected[1..k] + 1) / Nreps

Step 5: Return selected[] sorted in selection order.
```

**TRAIN PERMUTED (MCPT of the entire training factory)** [p.299-306]

```
Input:
  dataset D (raw market bar-changes for each market)
  trading system definition S (indicators, targets, models, oracles, portfolios)
  Nreps (typically 100-1000)

Output:
  p-values for profit factor and total return
  Training Bias estimate, Unbiased Return, Benchmarked Return (Skill)

Preconditions:
  No READ DATABASE / APPEND DATABASE (system must recompute indicators from raw markets)
  REMOVE ZERO VOLUME must be set before READ MARKET HISTORIES

Step 1: Train system S on the ORIGINAL markets:
     compute all indicators and targets
     train all models, oracles
     record Return_original, PF_original, BarsLong_orig, BarsShort_orig, SumTargets_orig
     Trend_orig = ((BarsLong_orig - BarsShort_orig) / TotalBars) * SumTargets_orig

Step 2: Repeat Nreps - 1 times:
     permute: shuffle the sequence of bar-to-bar changes within each market independently
              (preserves the marginal distribution of bar changes)
     from permuted bar changes, rebuild market prices (cumulative)
     recompute all indicators and targets
     retrain all models and oracles (full TSSB training run)
     record Return_k, PF_k, BarsLong_k, BarsShort_k, SumTargets_k
     Trend_k = ((BarsLong_k - BarsShort_k) / TotalBars) * SumTargets_k

Step 3: p_return = (1 + #{k : Return_k >= Return_orig}) / Nreps
   p_PF = (1 + #{k : PF_k >= PF_original}) / Nreps

Step 4: Bias_est = mean over k of (Return_k - Trend_k)

Step 5: UnbiasedReturn = Return_orig - Bias_est        # = Skill + Trend
   BenchmarkedReturn = UnbiasedReturn - Trend_orig # = Skill

Step 6: Emit histogram of permuted performance with original marked as a vertical bar
   (Figure 16, p.301).
```

**FTI (Follow-Through Index) computation for one bar** [p.147]

```
Input:
  BlockSize, HalfLength, Period (with rules: HalfLength >= Period/2,
  BlockSize - HalfLength >= 20 recommended, >= 2 required)

Step 1: Apply Khalsa's zero-lag lowpass filter of specified Period to log(close)
   over the HalfLength ... BlockSize-1 window behind current bar.
Step 2: Partition the filtered-price series in the channel (= BlockSize - HalfLength
   most recent bars, the HalfLength oldest are "used up" by the filter)
   into up-legs and down-legs.
Step 3: Determine a noise threshold from the leg-length distribution;
   discard legs shorter than threshold. Compute mean length of legitimate legs.
Step 4: For each bar in the channel, compute |log_price - filtered_log_price|.
   Define channel_width as a quantile of that absolute-deviation distribution.
Step 5: FTI = mean_legitimate_leg_length / channel_width.
```

**Absorption Ratio (Kritzman et al.)** [p.97]

```
Input: per-market CLOSE TO CLOSE series; lookback window W; eigen-fraction f (0.2 per Kritzman)
Preconditions: valid data for ALL markets on EVERY bar in W

Step 1: Build M×W matrix of bar-to-bar log returns across markets in window.
Step 2: Σ = sample covariance matrix across markets (M×M).
Step 3: Eigendecompose Σ, sort eigenvalues λ₁ ≥ λ₂ ≥ ... ≥ λ_M.
Step 4: k = round(f * M)
Step 5: AbsorptionRatio = (λ₁ + ... + λ_k) / (λ₁ + ... + λ_M)
Step 6: If short_MA and long_MA lookbacks are both nonzero:
     AbsorptionShift = (short_MA(AR) - long_MA(AR)) / std_long(AR)
```

**Khalsa zero-lag lowpass filter design principle** [p.146]

```
For the current bar:  use only HALF of the full symmetric filter shape
                      (the "past" half; there is no future data)
For bar lagged by h <= HalfLength:  use half + h coefficients
For bars lagged h >= HalfLength:    use the full symmetric filter (zero lag in its own region)

Property: zero lag for the most recent points at the cost of degraded frequency
response (high-frequency noise leaks through) near the current bar.
```

**PURIFY transform (indicator noise removal)** [p.353-359]

```
Input:
  purified series X (indicator to clean)
  purifier series Y (hypothesized pollution source; e.g., market close, VIX)
  predictor families F ⊂ {TREND, ACCELERATION, ABS_VOLATILITY, VALUE, ...}
  lookbacks L = (L1, L2, ...)
  N_predictors ∈ {1, 2}

Step 1: For each (family, lookback) pair, compute a candidate predictor function of Y.
Step 2: For each single predictor (if N_predictors=1) or every pair (if N_predictors=2):
     fit linear regression X ≈ a + b1 * f1(Y) + (b2 * f2(Y))
     score by R² or similar
Step 3: Select the best-fit linear model M*.
Step 4: For each bar t, purified_X(t) = X(t) - M*(Y)(t)
```

## 5. Regras de Trading Explícitas

- **REGRA [p.4]**: "Predictions of large magnitude are more likely to signal profitable market moves than predictions of small magnitude." Use threshold-based trade conversion: long if prediction ≥ upper threshold, short if ≤ lower threshold.
- **REGRA [p.4, p.189]**: Always specify a `MIN CRITERION FRACTION` (minimum fraction of bars that trade) when letting TSSB auto-optimize thresholds. Without it, the optimizer may converge on a single lucky trade.
- **REGRA [p.87]**: When an indicator's absolute level is meaningful but secular drift ruins stationarity, apply `CENTER <lookback>`. When volatility varies across epochs, apply `SCALE <lookback>`. When both matter, apply `NORMALIZE <lookback>`. Use median/IQR rather than mean/std because of outlier robustness [p.87-88].
- **REGRA [p.92]**: In multi-market systems, add `! <min_fraction>` (e.g., `! 0.6`) to require at least 60% of markets be present before computing the cross-market rank; otherwise the rank is meaningless.
- **REGRA [p.94]**: Use `CLUMP60` pooling when the question is "are markets moving together?" It returns 0 in a mixed regime and a signed measure of conformity otherwise.
- **REGRA [p.98]**: For Absorption Ratio computation, keep `CLEAN RAW DATA` threshold as small as possible (0.4 or less) — a single cleaned bar in any market anywhere in the lookback voids the computation for the current bar.
- **REGRA [p.108]**: Never use `CLOSE TO CLOSE` as a direct predictor in a prediction model — it is extremely unstable, nonstationary, and has poor cross-market conformity. Use it only as input to Mahalanobis Distance or Absorption Ratio [p.108].
- **REGRA [p.135-137]**: Prefer Morlet wavelets over Daubechies for financial applications: Morlet has best time-period localization, which is what traders need. Daubechies has zero redundancy but terrible localization — use only when maximal compression of a full time series is the goal.
- **REGRA [p.137]**: Budget Morlet wavelet indicators parsimoniously — they are "seriously redundant." Using many Morlet wavelets as predictors will create massive overfitting via the curse of dimensionality.
- **REGRA [p.141]**: For Daubechies wavelet indicators, set HistLength ≈ 3 × prediction horizon and Level = 2 (Li, Shi & Li recommendation). HistLength must be a power of two; 2^(Level+1) ≤ HistLength.
- **REGRA [p.144-145]**: FTI parameter choice order: (1) pick Period from the trading cycle; (2) set HalfLength somewhat greater than Period/2; (3) set BlockSize = 2 × HalfLength, increasing if channel length < 20, decreasing if channel length > 20 and long-history memory is undesired.
- **REGRA [p.156-157]**: For targets, prefer `NEXT DAY ATR RETURN` (or its multi-bar variant `SUBSEQUENT DAY ATR RETURN`) over raw log-ratio in multi-market settings — ATR-normalization equalizes across markets so high-volatility markets do not dominate training.
- **REGRA [p.158]**: Use `HIT OR MISS` target whenever the real trading plan includes stops and profit targets — it mimics order execution and its distribution has no outliers, which helps training.
- **REGRA [p.170, p.172]**: When ranking predictors with Nonredundant Predictor Screening, always append `MCPT = Nreps` (≥100, preferably 1000). The solo p-value grossly underestimates the true p-value because selection bias is ignored.
- **REGRA [p.170]**: When using `TAILS`, keep tail fraction ≥ 0.05 and typically 0.10 — smaller fractions cause mean cell count to plummet, rendering tests unreliable. "Keeping more than ten percent of each tail usually results in significant loss of predictive power. The majority of predictive power in most indicators lies in the most extreme values" [p.166].
- **REGRA [p.168, p.175]**: Use **Uncertainty Reduction** as the default selection criterion, not Cramer's V or Lambda. UReduc is one-sided, proportional, and uses all cells. TSSB hard-codes it as default "because it is an excellent choice" [p.169].
- **REGRA [p.175]**: When the printed output contains the line `"Results below this line are suspect due to small mean cell count"`, do not trust any p-values or measures printed below that line.
- **REGRA [p.178]**: When indicator tail-only screening disagrees with full-distribution screening on predictor ordering, trust the tails-only ordering for model-based trading systems — the tails usually carry more of the actionable signal.
- **REGRA [p.280, p.290]**: Prefer PRESCREEN over TRIGGER when you have strong a-priori belief that a particular regime split is appropriate; the PRESCREEN+oracle combination gives higher net OOS PF because it lets models vote jointly over all regimes rather than dropping entire regimes [p.294-295, empirical comparison].
- **REGRA [p.306]**: Never use `IS` (in-sample) portfolios in production — they select preferentially over-powerful overfitted component models. Use only `OOS` portfolios, which require WALK FORWARD.
- **REGRA [p.44-45] (paraphrasing from context)**: The `PROFIT FACTOR` criterion has good generalizability; other performance statistics (e.g., model R² or ROC area) do not translate well to financial performance [p.44].
- **NUNCA [p.299, p.306]**: Do not mix TRAIN PERMUTED with APPEND DATABASE or precomputed indicator databases — permutation requires the system to be able to *recompute* indicators and targets from raw permuted bar changes. A precomputed database cannot be shuffled at the bar level.
- **NUNCA [p.307]**: Do not interpret a low IS-portfolio p-value from TRAIN PERMUTED as evidence of edge — it detects training bias but not OOS-specific selection bias. Only WALK FORWARD on OOS portfolios gives the honest answer.
- **NUNCA [p.175]**: Do not compare p-values to 0.05 as if that alone validates an indicator — "if the null hypothesis is true, you will still obtain a p-value less than 0.1 ten percent of the time, and a p-value less than 0.01 one percent of the time" [p.174].

## 6. Pitfalls e Anti-patterns

- [p.137, p.152] **Over-using redundant wavelet families**: a battery of Morlet wavelets at neighboring periods conveys nearly the same information repeatedly, driving overfitting via the curse of dimensionality. Use at most a small handful across well-separated periods, or switch to Daubechies when many scales are needed.
- [p.148] **Trusting automated FTI period selection**: `FTI MINOR`, `FTI MAJOR`, and related auto-period variants are "highly unstable and of limited utility"; the chosen period can jump by large amounts from one bar to the next, producing non-stationary indicator behavior. Prefer `FTI FTI` with a fixed user-specified period.
- [p.162] **Using many predictor bins with little data**: chi-square and related contingency tests degrade catastrophically when mean cells per bin drop below ~5. Always watch the mean-cell-count column in TSSB output; ignore everything below the "results below this line are suspect" warning.
- [p.163, p.164] **Reading the solo p-value as if it were unbiased**: the solo p-value does not account for the multiple comparisons inherent in scanning many candidate predictors. Selection bias alone can reduce the true significance by orders of magnitude [p.170: "selection bias … can be severe, causing worthless predictors to be selected"].
- [p.170, p.174] **Forgetting serial correlation in the target**: if the target looks ahead more than one bar, the computed MCPT p-values are biased downward. For multi-bar-ahead targets, treat p-values as lower bounds only [repeated at p.170, p.172, p.175].
- [p.174, p.177] **Adding "helpful" predictors at high step-numbers**: even a random, worthless candidate — when optimally selected from a pool of remainders — can noticeably improve UReduc of the kept set, yet have inclusion p ≈ 1.0. This is selection bias masquerading as synergy. Read the inclusion p-values, not only UReduc [concrete example at p.177: REACT_20 raised UReduc from 3.06 to 4.36 while having p = 0.723].
- [p.299-300] **Walkforward discards the majority of history**: only OOS-pooled data can answer the p-value question via bootstrap, and walkforward training folds grow slowly. This is a real cost, which is why Aronson complements walkforward with TRAIN PERMUTED — but TRAIN PERMUTED is 100×-1000× slower per design pass.
- [p.302] **Confusing the two core questions**: Q1 ("probability a worthless system produced this apparent performance") and Q2 ("expected future performance") are "different, largely unrelated questions, and a responsible developer will require a satisfactory answer to both of them." A small p-value does not imply good expected return, and vice-versa.
- [p.304] **Treating Trend as Skill**: if a market has a secular drift and your training allows long/short imbalance, the training optimizer will exploit the drift (because it is present in the permuted markets too). Without Benchmarked Return = UnbiasedReturn − Trend, you will falsely claim drift-capture as genuine edge.
- [p.306-307] **Using IS portfolios with heterogeneous model power**: if one candidate model is much more expressive than the rest, its IS-performance will always look best because of overfit, and an IS-portfolio selection will always pick it. The permutation test will catch this (large training bias detected) but the damage to portfolio composition is already done.
- [p.306] **Putting MCPT on OOS Portfolios via TRAIN PERMUTED**: it does not work. OOS portfolios require WALK FORWARD, and as of this book edition TSSB had no permutation variant of walkforward portfolio selection.
- [p.ii] **Skimming the book before using TSSB**: Aronson explicitly warns "If the reader just skims through the entire text, hoping to gain an idea of how to use the TSSB program, the reader will be hopelessly dismayed by the vast complexity of options. The correct approach is to begin with the first, very simple example and implement it" [p.ii]. The knowledge compounds example by example.
- [p.44, paraphrased from context]: Using model-performance metrics (MSE, R², ROC area) to judge a trading system is misleading — "a shockingly low relationship" exists between R² and profit factor across real systems. Train with PROFIT FACTOR criterion, not MSE.
- [p.98] **Universe-composition bias in Absorption Ratio**: many current S&P 100 components did not exist years ago, so the first usable date is the birth date of the youngest market. This can silently truncate training sets by years. Check market start/end dates before computing ratios.
- [p.107 context] **Treating CLOSE TO CLOSE as a tradable indicator**: raw bar-to-bar log returns are extremely noisy with wide distributional variation across markets. Using them as direct model inputs yields unstable, non-conforming features — use them only through aggregation (Mahalanobis, Absorption).

## 7. Parâmetros Sensíveis

- **MCPT replications (`MCPT = Nreps`)** [p.170, p.172]: the smallest achievable p-value is 1/Nreps. Aronson: "If this is done, at least 100 replications should be used, and 1000 is not unreasonable." Trading off test precision against runtime — 1000 is the defensible default for production; 100 for exploratory work. Economic justification: MCPT precision, not curve-fit.
- **Maximum predictors in Nonredundant Screening (default 8)** [p.169]: "Nearly always more than enough, as cell count reduction will render the tests meaningless before even 8 are reached." Hard-coded in script mode; only overridable via the menu. Economic justification: practical cell-count limits, not curve-fit.
- **MIN CRITERION FRACTION (e.g., 0.1)** [p.4, p.189]: minimum fraction of bars that must produce a trade. A floor against degenerate solutions. Default of 0.1 is a deliberate compromise between statistical reliability (more trades) and edge concentration (fewer, better trades). Example scripts throughout the book use 0.1.
- **Tail fraction for TAILS option (0.05 or 0.10)** [p.166, p.182]: default "typical" values, justified by the universal finding that predictive power concentrates in indicator tails. Smaller than 0.05 wrecks cell counts; larger than 0.10 dilutes power.
- **Centering/Scaling lookback (example: 100 for trend centered, 200 for other)** [p.87, p.89]: "As long as the historical lookback period for the adjustment is made long relative to the frequency of trading signals, important information is almost never lost, and the improvement in stationarity can be enormous" [p.87]. Rule: lookback >> signal frequency. Author's figures show 100-200 bars working well for day bars [p.89]; no specific optimization.
- **ATR lookback (250)** [p.99, p.157, and throughout examples]: 250 trading days ≈ one year. Canonical choice for ATR normalization across the book. Economic justification: a full business cycle, institutional rebalancing cadence.
- **LINEAR PER ATR history length (50)** [p.99]: author's example uses 50 bars for the fit, 250 for ATR. 50 bars ≈ 2.5 months. Not presented as optimized — a reasonable horizon choice.
- **Chi-square bins (2-3 for target, 2-3 for predictor)** [p.162, p.166, p.176]: "In most cases this is the best choice, with three bins used. Three equal-count bins split the target into 'big win', 'big loss', and 'fairly inconsequential'." Economic meaning for three target bins. Two bins is the default for predictors when keeping all cases; tails-only uses exactly two (top/bottom).
- **FTI Period range (5 to 65 days)** [p.145]: "Khalsa processes day bars, and he uses periods ranging from 5 days up to 65 days in his demonstrations." Range is empirically chosen from Khalsa's work.
- **Absorption Ratio eigenvalue fraction (0.2)** [p.97]: "Kritzman et al use 0.2." Paper-motivated, not backtested.
- **Mahalanobis lookback (250)** [p.96]: "approximately one year" for daily data, per Kritzman & Li. Paper-motivated.
- **Daubechies Level = 2, HistLength ≈ 3 × horizon** [p.141]: Li, Shi & Li recommendation. "The user may wish to do his/her own experiments to choose optimal values."
- **MAX STEPWISE (1 to 4 predictors)** [p.307 example]: examples show 1-2 for conservative models and 4 as deliberately excessive ("almost certainly excessive … a strong model"). Higher stepwise counts encode higher overfit risk that TRAIN PERMUTED will then quantify.
- **TSSB compressions to [-50, 50]** [p.88-89]: nearly all TSSB indicators are passed through a final nonlinear squashing function to a fixed range. The author explicitly notes that because of this, MINUS INDEX differences may not equal exact raw differences — transformations happen after the arithmetic [p.85].

## 8. Citações Literais Importantes

> "Intelligent modeling software can discover patterns that are so complex or buried under random noise that no human could ever see them." — [p.2]

> "Predictions of large magnitude are more likely to signal profitable market moves than predictions of small magnitude." — [p.4]

> "Stationarity, roughly speaking, means that the statistical properties of an indicator do not change over time." — [p.87]

> "The basic reason is that such adjustment is an excellent way of forcing a great degree of stationarity on the indicator. In most cases, stationarity improves the accuracy of predictive models." — [p.87]

> "When you test many predictors and repeatedly look for the best to add, lucky predictors will be favored. This is called selection bias, and it can be severe, causing worthless predictors to be selected." — [p.170]

> "If the null hypothesis is true, one will still obtain a p-value less than 0.1 ten percent of the time, and a p-value less than 0.01 one percent of the time." — [p.174]

> "These are different, largely unrelated questions, and a responsible developer will require a satisfactory answer to both of them before signing off on real-life trading." — [p.299]

> "No matter how 'good' a trading system may be, it will be worthless when presented with random market data! Some of these shuffled market histories will allow the trained trading systems to be lucky, and others will not." — [p.300]

> "Selection bias … occurs when we choose one or more trained models from among a group of competitors. Bias occurs in the selection process because some of the models will have been lucky while others will have been unlucky. Those models that were lucky will be more likely to be selected than those that were unlucky, yet their luck, by definition, will not hold up in the future." — [p.306]

> "If the reader just skims through the entire text, hoping to gain an idea of how to use the TSSB program, the reader will be hopelessly dismayed by the vast complexity of options." — [p.ii]

## 9. Conexões com Outros Livros Desta Base

This is the third Masters/Aronson volume in the base. Cross-references are deliberate and non-redundant — this book is the *applied manual* that overlaps least with the other two on methodology and most on *concrete indicator definitions*.

- **Evidence-Based Technical Analysis** (`evidence_based_ta.md`) [p.ii; ch. Introduction] — Aronson 2007 is the **theoretical foundation** for the entire statistical worldview here. Data-mining bias [`evidence_based_ta.md#data-mining-bias`], Monte Carlo Permutation Method [`evidence_based_ta.md#monte-carlo-permutation`], detrending [`evidence_based_ta.md#detrending`], and the position-bias / Binary Reversal Rule concept are all presupposed in this 2013 volume. The MCPT and TRAIN PERMUTED mechanisms here are direct operationalizations of the Reality Check / Monte Carlo Permutation methods introduced in Chapter 6-7 of the 2007 book. Channel Breakout Operator (CBO) and Channel Normalization (CN) from the 2007 case study [`evidence_based_ta.md#channel-breakout-operator`] reappear here as parametrizable TSSB indicators (`N DAY HIGH`, `N DAY LOW`, `STOCHASTIC K/D`).
- **Testing and Tuning Market Trading Systems** (`testing_tuning.md`) — Masters 2018 is the **C++ algorithmic counterpart**. The stationarity induction stack there [`testing_tuning.md`, ch.2-3] — subtract moving median, divide by IQR, final nonlinear squash — is the same stack exposed here under TSSB's `CENTER`/`SCALE`/`NORMALIZE` commands [p.87-89]. Masters' relative entropy gate (require H(X)/log(K) ≥ 0.5 for any candidate indicator) [`testing_tuning.md` ch.2] corresponds to the `PRICE ENTROPY`/`VOLUME ENTROPY` family here [p.132-134], though this book does not impose Masters' 0.5 floor explicitly. Masters' nested-walkforward MCPT of training processes and model factories [`testing_tuning.md` ch.7] is the predecessor idea of TRAIN PERMUTED [p.299]. The PURIFY transform [p.353-359] is a production form of Masters' indicator-purification discussion.
- **Advances in Financial Machine Learning** (`advances_fin_ml.md`) [p.299-306] — López de Prado's book shares the concern over selection bias and purged/embargoed cross-validation. The `TRAIN PERMUTED` mechanism here is analogous to López de Prado's MCPT-of-training but with a different permutation model (bar-change shuffle vs. label shuffle).
- **Machine Learning for Asset Managers** (`ml_for_asset_managers.md`) — López de Prado 2020's eigendecomposition-based coherence measures closely parallel the Absorption Ratio [p.97] here, both drawing on the Kritzman et al. 2010 paper.
- **Cycle Analytics for Traders / Rocket Science for Traders / Cybernetic Analysis / Cybernetic Trading** (`cycle_analytics.md`, `rocket_science.md`, `cybernetic_analysis.md`, `cybernetic_trading.md`) — Ehlers' work on bandpass/lowpass filters for cycle extraction is conceptually adjacent to Khalsa's FTI zero-lag filter [p.146] and the Morlet wavelet family [p.135-140]; but where Ehlers emphasizes cycle detection for timing, Aronson/Masters emphasize filter output as *predictor features*, not as trade signals directly.
- **Evaluating and Optimizing Trading Strategies** (`eval_opt_strategies.md`) — Pardo's walkforward methodology is a practical companion to the walkforward + permutation mechanism here. The PRESCREEN/TRIGGER distinction [p.280-295] for regime specialization has no direct analog in Pardo and is a novel contribution.
- **Systematic Trading** (`systematic_trading.md`) — Carver's emphasis on parsimony (3-4 parameter budget) aligns with this book's stepwise predictor cap of 8 [p.169] and the repeated warning at p.169-175 that later predictors improve apparent performance via selection bias, not genuine Skill.

Non-connections (explicit N/A): trilogia-Masters cross-refs for book-specific material on classification methodology (`testing_tuning.md`), BCa bootstrap and Student-t bounds (`testing_tuning.md`), and regularized-elastic-net optimization (`testing_tuning.md`, ch.3) — none of that methodology appears in *this* volume. This book's novel contributions are: (1) the concrete TSSB indicator taxonomy (FTI, Morlet/Daubechies, entropy/MI, Mahalanobis, Absorption Ratio, Reactivity, etc.); (2) the PURIFY transform operationalizing "Pure VIX"; (3) Oracle-based regime specialization (PRESCREEN + HONOR PRESCREEN vs. TRIGGER); (4) the explicit Total = Skill + Trend + Bias decomposition with closed-form estimators from permutation output.
