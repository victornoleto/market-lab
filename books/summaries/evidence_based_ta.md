# Evidence-Based Technical Analysis: Applying the Scientific Method and Statistical Inference to Trading Signals

## Metadata
- **Author:** David R. Aronson [p.7, p.15]
- **Year:** 2007 [p.8]
- **Publisher:** John Wiley & Sons (Wiley Trading series) [p.6, p.8]
- **Pages:** 544
- **ISBN:** 978-0-470-00874-4 / 0-470-00874-1 [p.8]
- **Primary focus:** Turn technical analysis into a rigorous observational science by applying the scientific method, statistical inference, and tests robust against data-mining bias (White's Reality Check and Monte Carlo Permutation).

## 1. Core Thesis
Technical analysis must evolve from a faith-based folk art into a rigorous observational science — "Evidence-Based Technical Analysis" (EBTA). The thesis is twofold [Introduction, p.1-7]: (1) subjective TA (hand-drawn chart patterns, Elliott Wave, Gann, etc.) is "worse than wrong — it is meaningless" [p.5] because it produces no falsifiable claims; (2) objective TA is amenable to scientific evaluation, but its historical results are systematically positively biased by data-mining bias [p.1], requiring specialized statistical tests such as White's Reality Check and Monte Carlo Permutation [p.239-243; p.325-328] to be trustworthy.

The book is divided into two parts [p.11]: Part I (methodological, psychological, philosophical, and statistical foundations — chapters 1-7); Part II (case study: back-test of 6,402 binary long/short rules on the S&P 500 over 25 years — chapters 8-9).

## 2. Main Concepts
- **EBTA (Evidence-Based Technical Analysis)** — TA restricted to objective methods whose results are evaluated with statistical inference that controls for data-mining bias [p.6-7, p.162-163].
- **Subjective vs. Objective TA** — Subjective TA cannot be reduced to a computerizable and backtestable algorithm; objective TA can [p.5-6, p.16-17].
- **Cognitive content / discernible-difference test** — A proposition can be a candidate for belief only if its truth vs. falsity produces an observable difference [p.2-3].
- **Knowledge = justified true belief** — To qualify as knowledge, a claim must be true and justified by sound inference from evidence [p.4].
- **Binary reversal rule** — A rule that always outputs +1 (long) or −1 (short), flipping from one to the other on signals [p.17, p.33].
- **Position bias** — Tendency of a rule to spend more time in one state (long or short) due to asymmetry between its entry conditions [p.23-27].
- **Detrending** — Subtract the average daily return of the back-test period from each daily market return, producing a zero-trend series. Required to eliminate the conjoined effect of position bias x market trend [p.27-28, p.29-30].
- **Look-ahead bias** — Using information in the back-test that was not available at the time of the decision (e.g., using the close as a signal and executing at the same close) [p.29-30].
- **Data-mining bias** — Systematic positive bias in the observed performance of the best rule when several are tested; observed performance exceeds expected performance [p.271, p.287].
- **Multiple Comparison Procedure (MCP)** — Data-mining paradigm: test many candidate solutions and select the best by a figure of merit [p.264-265].
- **Channel Breakout Operator (CBO)** — Trend-following operator: long signal when the series crosses above the maximum of the last n periods; short when it crosses below the minimum [p.397].
- **Channel Normalization (CN) / Stochastics** — Detrending operator that scales the series to 0-100 based on its position in the range of the last n periods; acts as a high-pass filter [p.401-403].
- **Reasoning by representativeness / sample size neglect** — Psychological heuristic that leads the analyst to perceive patterns in small samples of random data ("crime of small numbers") [p.88-96, p.113].
- **Overconfidence bias** — Documented human tendency to overestimate the accuracy of one's own knowledge/skill [p.45-47].
- **Configural thinking** — A mode of reasoning that requires integrating multiple variables simultaneously — the human mind is limited to ~3 factors [p.42-44].
- **Null hypothesis (Ho) in rule testing** — The rule has no predictive power; expected return = 0 on detrended data [p.166-167, p.182].
- **Sampling distribution** — Probability distribution of the test statistic (e.g., mean return) under the null hypothesis [p.167-168].
- **Noise rule** — A rule whose +1/−1 signals are randomly paired with market returns; used as benchmark by Monte Carlo Permutation [p.239-240].

## 3. Formulas / Equations
**Expected Return of a binary reversal rule (no-predictive-power baseline)** [p.26-28]

$$ER = [p(L) \times ADC] - [p(S) \times ADC]$$

- $p(L)$ = proportion of time long [p.26]
- $p(S)$ = $1 - p(L)$ [p.26]
- $ADC$ = average daily change of the traded market [p.26]
- Implication: if $ADC = 0$ (detrended market), $ER = 0$ regardless of position bias [p.28].

**Detrending (log-return conversion) — rule daily return** [p.29-30]

$$\text{Rule daily return} = POS_0 \times \left[ \log\!\left(\frac{O_{+2}}{O_{+1}}\right) - ALR \right]$$

- $POS_0$ = +1 or −1 at the close of day 0 [p.29]
- $O_{+1}$, $O_{+2}$ = opens of days 1 and 2 (avoids look-ahead bias; executes at the open following the signal) [p.29-30]
- $ALR$ = average log return over back-test period [p.30]

**Sample Mean (point estimator of expected return)** [p.260]

$$\bar{X} = \frac{\sum_{i=1}^{n} X_i}{n}$$

**Confidence Interval via Bootstrap Percentile Method** [p.250]

$$x = \frac{100 - \text{Confidence Interval Desired}}{2}$$

- Remove the top x% and bottom x% from the bootstrap distribution of means to obtain the bounds [p.250].

**Moving Average Operator** [p.415]

$$MA_t = \frac{\sum_{i=1}^{n} P_{t-i+1}}{n}$$

- Lag of a simple MA = $(n-1)/2$; lag of a linear-weighted MA = $(n-1)/3$ [p.400].

**Linear Weighted Moving Average (LMA)** [p.400]

$$WMA_t = \frac{\sum_{i=1}^{n} (n - i + 1) \cdot P_{t-i+1}}{\sum_{i=1}^{n} i}$$

**Channel Normalization Operator (Stochastics)** [p.402]

$$CN_t = \left[ \frac{S_t - S_{\min,n}}{S_{\max,n} - S_{\min,n}} \right] \times 100$$

- $S_t$ = value of the series at time t; $S_{\min,n}$ and $S_{\max,n}$ = min and max of the last n days [p.402].

**Cumulative Advance-Decline Ratio (CADR)** [p.414]

$$CADR_t = CADR_{t-1} + ADR_t, \quad ADR_t = \frac{adv_t - dec_t}{adv_t + dec_t + unch_t}$$

**Cumulative Net Volume Ratio (CNVR)** [p.415]

$$NVR_t = \frac{upvol_t - dnvol_t}{upvol_t + dnvol_t + unchvol_t}$$

**Divergence Indicator (double channel normalization)** [p.453]

$$DI = CN\left[\, CN(S_1, n) - CN(S_{\&P500}, n),\ 10n \,\right]$$

- Double CN is required because companion series have different degrees of co-movement with the S&P 500 [p.452-454].

**Artificial Trading Rule Expected Return (used in the data-mining bias experiments)** [p.307-308]

$$ER = ppm \times 3.97 - (1 - ppm) \times 3.97$$

- $ppm$ = probability of profitable month; 3.97% = mean absolute monthly return of the S&P 500 from Aug/1928–Apr/2003 [p.308].

**Linear combining rule (complex rule via weighted sum)** [p.468-469]

$$Y = a_0 + \sum_{i=1}^{k} a_i \cdot r_i$$

- $r_i$ = output of rule i; $a_i$ = weight; $Y$ = output of the linear complex rule [p.469].

**Markowitz/Xu Data-Mining Correction** [p.324]

$$H' = R + B(H - R)$$

- $H'$ = corrected expected return of the best rule [p.324]
- $R$ = mean return of all tested rules [p.324]
- $H$ = observed return of the best rule [p.324]
- $B \in [0,1]$ = shrinkage factor (smaller B = more shrinkage) [p.324].

## 4. Algorithms and Pseudocode
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

## 5. Explicit Trading Rules
- **RULE [p.23]**: Evaluate a rule ONLY against a relevant benchmark. The benchmark adopted by the book is the return of a rule without predictive power (placebo). A 10% return is inadequate or superior depending on what other rules achieved.
- **RULE [p.27-28]**: Detrend the traded market series BEFORE computing daily rule returns. Subtract the mean daily return of the back-test period. This eliminates the combined effect of position bias x market trend.
- **RULE [p.29-30]**: Use log returns, not percentages. Signals generated at the close of day 0 are executed at the open of day +1; the day's return is $\log(O_{+2}/O_{+1})$ (avoids look-ahead bias).
- **RULE [p.183-185]**: Start from the null hypothesis that every rule is useless (expected return = 0). Only reject Ho if the backtested return falls in the right tail of the sampling distribution (p-value < 0.05 in this book [p.410]).
- **RULE [p.281, p.345]**: NEVER use single-rule back test p-values to evaluate the best rule from a data-mining run. Only tests that incorporate data-mining bias are valid — WRC or MCP.
- **RULE [p.407]**: If multiple rules are tested (any data mining), store the full daily return series (for WRC) and/or the +1/−1 output values of ALL rules (for MCP). Without this, rigorous significance testing is impossible.
- **RULE [p.407-408]**: Do not use rules from prior research by others without knowing how many rules that author tested ("data-snooping bias"). Prefer building the rule universe by combinatorial enumeration of parameters defined a priori.
- **RULE [p.46-47]**: For data reported with lag or subject to revision (e.g., mutual fund cash, economic stats), lag the signals appropriately. The case study avoided the problem by using only data without lag/revision.
- **RULE [p.149-150]**: For subjective analysts, issue only falsifiable forecasts. Three forms: (1) define a future evaluation point; (2) define the maximum adverse movement before declaring the forecast wrong; (3) predict a favorable magnitude X before an unfavorable Y.
- **NEVER [p.43-44]**: Mentally combine more than 3 indicators in a configural (non-linear) way. The human mind is limited to 3 configural factors; 5 indicators generate 2^5 = 32 distinct configurations impossible to integrate intuitively.
- **NEVER [p.107-113]**: Conclude that a chart is non-random by visual inspection. Random walks produce head-and-shoulders, double tops, and trends indistinguishable from "authentic" ones; expert chartists cannot tell them apart [Introduction, p.8; p.37-38].
- **NEVER [p.291]**: Optimize parameters with few observations. The magnitude of data-mining bias grows dramatically with small sample size — e.g., best-of-1,024 rules with 10 obs → bias ~84% per year; with 1,000 obs → bias ~12% per year [p.315, Figure 6.33].
- **RULE [p.473]**: If you allow complexity optimization (rule induction, neural nets), use 3 data segments — train / test / validation — not just 2. Only validation gives an unbiased out-of-sample estimate.

## 6. Pitfalls and Anti-patterns
- [p.283-287] **Selecting the best rule without adjusting for data-mining bias** — the observed performance of the best of N rules systematically overestimates expected performance. Ignoring this is the classic "fool's gold" of objective TA.
- [p.289-291] **Five factors that inflate data-mining bias**: (1) more rules tested → more bias; (2) fewer observations in the performance statistic → more bias; (3) lower correlation between rule returns → more bias; (4) presence of positive outliers → more bias; (5) smaller variance of expected returns across rules → more bias.
- [p.149-151] **Non-falsifiable forecasts** ("I am bullish") fail the discernible-difference test. They are equivalent to astrology.
- **Faith-based subjective TA** [p.5-6] (Elliott Wave, Gann, Magic T's, classic hand-drawn chart patterns) is "not even wrong" because it generates no testable predictions.
- [p.333] **The "TA reflects all information" argument as a justification for TA** contains a logical contradiction — it is the same premise as EMH, which denies TA's effectiveness [p.333].
- [p.58, p.71-78] **Confirmation bias, self-attribution bias, hindsight bias** — analysts reinterpret wrong signals as exceptions and attribute success to skill, failures to luck. Combat by keeping a daily journal with falsifiable forecasts recorded ex-ante [p.53, author's personal experience at Spear Leeds].
- [p.88-96] **Illusion of trends & patterns in random data** (Reasoning by Representativeness + Law of Large Numbers violation). Small-sample neglect → gambler's fallacy and clustering illusion.
- [p.273-280] **Comparing in-sample vs. out-of-sample performance** as a sole remedy. Once out-of-sample data is used even once, it loses its virginity; the arbitrary train/test split is subjective.
- [p.29-30] **Look-ahead bias** — using the close as both input AND execution price (on the same bar) inflates returns.
- [p.23-28] **Position bias x market trend** creates apparent predictive power in useless rules. A long-biased rule in a bull market produces profit without any skill.
- [p.406] **Data-snooping bias (prior-research-snooping)** — testing rules from other authors without knowing how many rules they tested makes it impossible to evaluate significance correctly.
- [p.450] **Only long/short reversal rules** — assumes the market is always inefficient. Long/short/neutral (tri-state) or long/neutral rules are more realistic — the restriction of the case study was an acknowledged limitation.
- [p.287-288, p.473] **Overfitting from excessive complexity** — any rule can be fitted perfectly to the past with enough complexity; out-of-sample performance will be disastrous.
- [p.407-408] **Complex rules were not tested in the case study**; a larger study (Hsu/Kuan, 39,832 rules) found that 82% of the 229 statistically significant rules were complex — but none significant on the S&P 500 or DJIA [p.450].

## 7. Sensitive Parameters
- **CBO lookback span {3, 5, 8, 12, 18, 27, 41, 61, 91, 137, 205 days}** [p.398]: chosen to be separated by a ~1.5 multiplier. Values selected "without optimization on the basis of intuition" [p.429] — explicitly not curve-fit.
- **Threshold displacement {10, 20} in E-rules** [p.429]: upper threshold = 50+d, lower = 50-d. Chosen intuitively; not optimized.
- **CN lookback {15, 30, 60 days}** [p.429]: three scales to capture extremes and divergences. Not optimized.
- **Smoothing LMA = 4 days** [p.437]: fixed for all E-rules — justified as reducing signal chattering without excessive lag (LMA lag = (4-1)/3 = 1 day).
- **Second-level CN lookback = 10x first level** in divergence indicator [p.454]: "assumed that 10x is enough to establish the fluctuation range" — a conservative, not optimized, choice.
- **200d MA as regime filter** — not directly endorsed in the book; Aronson does NOT propose a magic number. Instead, the MLM Index uses a 12-month MA as a trend benchmark on 25 commodities [p.398].
- **MLM Index = 12-month MA cross on 25 commodities** [p.398]: uses the 12-month MA ("extremely simplistic") applied to nearby futures — justified economically as risk premium for service to hedgers [p.380-384], not as curve-fit.
- **Bootstrap/MC replications = 1,999** [p.442]: increasing would smooth the distribution but not alter the conclusion.
- **Significance level α = 0.05** [p.410]: standard threshold; the case study would require 15%+ return for significance, 17%+ for p<0.001 [p.459].
- **Case study back-test period: Nov 1, 1980 – Jul 1, 2005 (~6,800 days)** [p.257, p.405, p.409]: pragmatically justified, not tested for robustness.
- **Trading costs were ignored in the case study** [p.47]: explicit decision — the goal was to find predictive power, not tradable systems. For real deployment, costs must be included.

## 8. Key Literal Quotes
> "Although the scientific method is not guaranteed to extract gold from the mountains of market data, an unscientific approach is almost certain to produce fool's gold." — [p.1]

> "Subjective TA is not even wrong. It is worse than wrong. Statements that can be qualified as wrong (untrue) at least convey cognitive content that can be tested. The propositions of subjective TA offer no such thing." — [p.6-7]

> "It's not so much the things we don't know that get us into trouble as the things we know that just ain't so." — Artemus Ward, quoted by Aronson [p.36]

> "Technical analysts, including myself, know a lot of stuff that isn't so, and believe a lot of weird things." — [p.9-10]

> "There is no such thing as 'approximately random.' Either a rule has predictive power or it does not. Past performance can fool us. Historical success is a necessary but not a sufficient condition for concluding that a method has predictive power and, therefore, is likely to be profitable in the future." — [p.6, paraphrased closely]

> "With respect to the second objective, no rules with statistically significant returns were found. Specifically, none of the 6,402 rules had a back-tested mean return that was high enough to warrant a rejection of the null hypothesis, at a significance level of 0.05." — [p.457]

> "Had I used an ordinary significance test, which pays no attention to data-mining bias, the mean return of the best rule would have appeared to be highly significant (a p-value of 0.0005)." — [p.459]

## 9. Cross-references to Other Books in This Knowledge Base
N/A — First book processed in this pipeline; cross-refs will be added in subsequent passes. Natural future cross-reference topics (once the corresponding books are processed):
- **Data-mining bias, combinatorial backtesting, multiple-testing correction** → *Advances in Financial Machine Learning* (López de Prado), which defines the Deflated Sharpe Ratio and CPCV for the same problem.
- **Monte Carlo / Bootstrap in trading** → *Permutation and Randomization Tests for Trading System Development* or *Statistically Sound Machine Learning for Algorithmic Trading* (Masters, who actually invented the MCP variant used here [p.ix, p.239-240]).
- **Kelly sizing, behavior bias** → *Mathematics of Money Management* (Vince), *Thinking, Fast and Slow* (Kahneman) — the latter underpins Aronson's ch.2.
- **Trend-following risk premium / MLM Index** → *Following the Trend* (Clenow), *Trend Following* (Covel).
- **Behavioral finance models (BSV, DHS, HS)** [p.331-380] → *Inefficient Markets* (Shleifer), *Irrational Exuberance* (Shiller).
