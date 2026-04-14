# Testing and Tuning Market Trading Systems: Algorithms in C++

## Extraction Scope Notice

This book's PDF uses a single continuous page numbering sequence: the `[PAGE N]` markers in the extracted text align with the printed page numbers referenced by the author himself (e.g., the author's in-text reference "the progressive walkforward algorithm given on page 142" lands exactly at `[PAGE 142]` in the extraction, which contains the walkforward training-bias program). Therefore every `[p.X]` citation below refers directly to the `[PAGE X]` marker = printed page X. Chapter 1 (Introduction) begins at p.11; TOC/frontmatter occupies p.1-10. Range `[p.X-Y]` = PAGE X through PAGE Y. `[ch.N]` is used when the concept spans the entire chapter.

## Metadata
- **Autor:** Timothy Masters [p.2, p.9]
- **Ano:** 2018 [p.3]
- **Editora:** Apress (distributed by Springer) [p.3, p.4]
- **Páginas:** 353 (PDF); printed content pp.1-348 [metadata.json]
- **ISBN:** 978-1-4842-4172-1 (print), 978-1-4842-4173-8 (electronic) [p.3]
- **Foco principal:** Rigorous statistical methodology for evaluating, validating, and bounding the future performance of automated market trading systems, with emphasis on avoiding overfitting and future leak.

## 1. Tese Central

A trading system backtest is not a research tool — it is a tool for measuring the *risk of overfitting* and the probability that apparent in-sample edge will survive into live trading. The central thesis of the book, restated in many forms, is that seemingly small methodological errors (future leak through lookback/lookahead overlap, selection bias across competing systems, unregularized predictor sets, bootstrap confidence intervals on ratio statistics, cross-validation on nonstationary series) *systematically* inflate reported performance and destroy capital in production. The entire book is organized as a pipeline of defenses: pre-optimization (stationarity induction, indicator entropy), optimization (regularized linear models, differential evolution), post-optimization (cheap bias estimates, parameter-sensitivity curves), unbiased trade simulation (walkforward, nested walkforward), trade analysis (Student-t and BCa bounds on mean return, bootstrapped drawdown quantiles), and finally permutation testing (MCPT of training processes and model factories). [ch.1, p.11-19; ch.7, p.310-312]

Masters' operating principle, stated explicitly: "the strength of your indicators is vastly more important than the strength of the predictive model that uses them to signal trades. Some of the best, most stable and profitable trading systems I've seen over the years use a simple linear or nearly linear model with high-quality indicators as inputs." [p.43]

## 2. Conceitos-Chave

- **Future leak** — illegal leakage of future knowledge into a testing procedure; produces optimistic performance estimates. Masters stresses it is "far deadlier than you imagine": a nearly-random system with a 1% edge can produce a respectable-looking equity curve. [p.17]
- **Percent-wins fallacy** — $E[\text{return}] = W \cdot p - L \cdot q$; win-rate and payoff are inseparable. A 9/10 win-rate system on a random walk with 1:9 payoff has zero expectation. [p.18-19]
- **Stationarity (practical)** — "the degree to which a time series' statistical properties remain constant over time"; markets are inherently nonstationary; traditional statistical tests for nonstationarity are pointless (they always reject). The relevant question is: can we induce stationarity in the indicator? [p.20-21]
- **Location-stationarity oscillation** — compute indicator relative to a lagged version of itself (current − value at lag = lookback), or as short-lookback minus long-lookback. Trades information about absolute level for dramatic stationarity gain. [p.26-27]
- **Extreme stationarity induction** — subtract moving-window mean (or median); divide by moving-window std (or IQR); short window → extreme stationarity but destroys absolute-level info. [p.28]
- **Relative (proportional) entropy** — $H(X)/\log(K)$; ranges 0-1. Masters requires ≥ 0.5, preferably higher, for any candidate indicator. Computed by equal-range binning of indicator history. [p.30-31]
- **Monotonic tail-only cleaning** — identify the narrowest-range sorted window containing (1 − 2·tail_frac) of cases; compress values outside it with an exponential of a scaled delta; preserves monotonicity, restores entropy without destroying information. [p.38-40]
- **Regularized (elastic-net) linear model** — linear regression with combined L1/L2 penalty governed by (α, λ); α=0 is ridge, α=1 is lasso, intermediate gives "elastic net." Trains via coordinate descent with soft-thresholding. [p.45-47]
- **Differential Evolution (DE)** — genetic-style optimizer; compromise between hill-climbing speed and global-search robustness; Masters' preferred optimizer for both algorithmic and model-based systems. [p.85-88]
- **StocBias (cheap training bias)** — intercept the initial (random) DE population; track each candidate's bar-by-bar returns; the best IS minus matching OOS return approximates training bias essentially for free. [p.105-107]
- **Parameter sensitivity curves** — plots of performance as each parameter is perturbed around its optimum; smooth curves = robust, narrow peaks or multi-peak structure = luck/overfitting. Presented as "minimal due diligence" for any developer. [p.126-127]
- **Selection bias** — the moment you pick the best of several OOS performances, that winner's OOS score becomes biased upward; only a fresh held-out set restores unbiasedness. [p.143-144]
- **Walkforward analysis** — rolling IS-train / adjacent-OOS-test windows; simulates real-time updating. [p.148-149]
- **Guard buffer / purge** — when lookback > 1 or lookahead > 1 in the model-building dataset, remove `min(lookback, lookahead) − 1` cases from the end of the training set (or, for CV, from both the start and end where training touches OOS). [p.149-150, p.161-162]
- **CSCV (Computationally Symmetric Cross-Validation)** — Bailey et al.'s 2015 construction to equalize train/test set sizes; useful when per-fold Sharpe/profit-factor are needed. [p.182]
- **Nested walkforward** — outer walkforward wrapping an inner walkforward (or inner CV); necessary whenever a selector chooses between competing systems based on their OOS performance. [p.196-197]
- **Profit factor** — sum of wins ÷ sum of losses. Favored by Masters but fragile as a ratio statistic under bootstrap. [p.218, p.263]
- **BCa bootstrap** — "bias-corrected and accelerated" bootstrap; Masters' recommended tool for bounding the true mean of future returns. [p.246-247]
- **Drawdown bounding** — drawdowns measure *across* trades, not per-trade; intuitive reasoning fails; requires specialized bootstrap on quantiles with ~1e8 iterations for accuracy. [p.287-291, p.306-307]
- **MCPT (Monte Carlo Permutation Test)** — null hypothesis: market changes are unordered (no exploitable structure). Permute price-changes (not prices) to destroy patterns while preserving the marginal distribution; re-run the full training/testing pipeline; p-value = fraction of permuted runs that match or beat the unpermuted performance. [p.310-319]
- **Skill / TrainingBias / Trend partitioning** — MCPT-based decomposition of total IS return into learned skill, patterns learned in-sample that will not repeat (TrainingBias), and market long-bias contribution (Trend). [p.321-322]

## 3. Fórmulas / Equações

**Equation 1-1 — Expected return of a trade** [p.18]

$$E[R] = W \cdot p - L \cdot q$$

- $W$ = amount won per win, $L$ = amount lost per loss
- $p$ = probability of winning, $q = 1 - p$
- Masters' takeaway: "win/loss sizes and probabilities are inextricably related." [p.19]

**Log returns for trade accounting** [p.14-15]

$$r_t = \log(P_{\text{exit}}) - \log(P_{\text{entry}})$$

Required throughout the book because percent changes are asymmetric: +10% then −10% is not zero.

**Equation 2-1 — Shannon entropy (nats)** [p.29]

$$H(X) = -\sum_{x \in \chi} p(x) \log p(x)$$

Maximum is $\log(K)$ where $K$ = number of possible values; **relative entropy** = $H(X) / \log(K)$. Masters' acceptance threshold: relative entropy ≥ 0.5 (serious concern below 0.1). [p.30-31, p.34]

**Equation 2-2, 2-3 — Tail-taming transforms** [p.35]

$$\tanh(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}}$$
$$\text{logistic}(x) = \frac{1}{1 + e^{-x}}$$

Subtract 0.5 after logistic to center at zero. Prescale input appropriately. [p.35]

**Equation 3-1, 3-2, 3-3 — Regularized linear model** [p.45-46]

$$\hat{y}_i = \beta_0 + x_i^\top \beta$$

Loss with elastic-net penalty:

$$L(\beta_0, \beta) = \frac{1}{2N}\sum_{i=1}^N (y_i - \beta_0 - x_i^\top \beta)^2 + \lambda P_\alpha(\beta)$$

$$P_\alpha(\beta) = \tfrac{1}{2}(1-\alpha)\|\beta\|_2^2 + \alpha \|\beta\|_1$$

- $\alpha = 0$ → ridge; $\alpha = 1$ → lasso; $0 < \alpha < 1$ → elastic net.
- With standardized predictors/target, $\beta_0 = 0$ and can be dropped. [p.45-46]
- Lasso ($\alpha = 1$) is numerically unstable under perfectly correlated predictors: "set α to a value very close to one but not quite there." [p.47]

**Equations 3-4 to 3-7 — Coordinate-descent beta update with soft-thresholding** [p.48-49]

Residual: $r_i = y_i - \sum_{k \ne j} x_{ik} \beta_k$

Argument: $a_j = \frac{1}{N}\sum_i x_{ij} r_i$

Soft-threshold: $S(a, \gamma) = \text{sign}(a) \cdot \max(|a| - \gamma, 0)$

Update: $\beta_j \leftarrow \frac{S(a_j, \lambda \alpha)}{1 + \lambda(1-\alpha)}$

(With standardized $x_j$: $\sum_i x_{ij}^2 = N$.) Guaranteed to converge because the loss is convex with a unique global minimum. [p.48]

**Equations 3-8, 3-9 — Differential case weighting variant** [p.49]

Using case weights $w_i$ summing to 1, the argument and update generalize; reduces to 3-5/3-7 when all $w_i = 1/N$.

**Equations 3-10 to 3-15 — Covariance-updates formulation** [p.49-50]

Enables $O(K)$ per-iteration work instead of $O(N)$ when $N \gg K$ (the common trading case), via precomputing $X_{\text{inner}}$ and $Y_{\text{inner}}$ once. [p.49-50]

**Student's-t lower bound on mean return** [p.244-245]

$$\text{LB} = \bar{r} - \frac{s}{\sqrt{n}} \cdot t^{-1}_{n-1}(1 - \alpha)$$

C++ literal from book:

```c
lower_bound = mean - stddev / sqrt((double) n) *
              inverse_t_CDF ( n - 1 , 0.95 ) ;
```

Relatively robust to moderate non-normality but fragile under heavy tails or extreme skew. [p.244-245]

## 4. Algoritmos e Pseudocódigo

**STATN — nonstationarity gap analysis** [p.22-26]

```
Inputs: lookback, fractile, version, filename (OHLC)
1. For each bar, compute Trend = least-squares slope over lookback bars
                         Volatility = ATR over lookback bars
2. If version == 1: subtract lagged indicator (lag = lookback)
   If version > 1:  subtract long-lookback version (lookback * version)
3. Sort indicator values; find quantile at specified fractile
4. Walk indicator array; each time it flips above/below the quantile,
   bin the count of consecutive bars on the same side into
   { 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, >512 }
5. Print bin counts for trend and volatility tables
```
Interpretation: heavy counts in 256/512/>512 bins = severe nonstationarity (slow wandering). [p.22-27]

**clean_tails — monotonic tail-only cleaning** [p.38-40]

```c
// Preserve interior (1 - 2*tail_frac) fraction unchanged.
// Find narrowest sorted window of that coverage.
// Beyond [minval, maxval] of that window, apply
//   new = minval - limit*(1 - exp(scale*(minval-raw))), left tail
//   new = maxval + limit*(1 - exp(scale*(raw-maxval))), right tail
// limit = (maxval - minval)*(1 - cover)
// scale = -1 / (maxval - minval)
```
Monotonic; preserves order; dramatically improves entropy on heavy-tailed indicators. [p.39-40]

**CoordinateDescent training with lambda path** [p.65-66, p.78-82]

```
1. Standardize predictors (zero mean, unit variance); standardize target.
2. Precompute X_inner (K x K), Y_inner (K), XSSvec (K) once.
3. Start at lambda_max large enough to force all β to zero.
4. For each lambda on a descending log-spaced path:
     a. Initialize from previous lambda's solution (warm start).
     b. Repeat until converged:
          For each j in 1..K:
             β_j ← S(a_j, λα) / (1 + λ(1-α))  // Eq 3-7 / 3-10
5. Each lambda produces an explained-variance curve and a count of
   nonzero β; plot/return these.
```

**cv_train — k-fold CV for lambda selection** [p.82]

```
for each fold f:
   train on cases outside f using full lambda path  (lambda_train)
   for each trial lambda: record OOS explained-variance on fold f
Pool OOS explained-variance across folds for each lambda.
Return lambda with best pooled OOS performance.
```

**Differential Evolution (DE) — DIFF_EV.CPP** [p.85-91]

```
Initialize: generate popsize random individuals (parameter vectors).
            Use overinit > popsize trials, keep top popsize by criterion.
            Optionally pass each trial's bar returns to StocBias (training-bias estimator).
Loop until max_bad_gen generations without improvement:
    For each individual i:
        pick three distinct individuals a, b, c != i
        trial = a + mutate_dev * (b - c)                  // differential mutation
        crossover trial with i at rate = pcross            // [p.89]
        if criterion(trial) > criterion(i): replace i
Return best individual.
```

**StocBias cheap training-bias estimator** [p.105-110]

```
At construction: allocate IS_best[nreturns], OOS[nreturns].  // [p.108]
During initial random population generation only (collect = True):
    For each candidate whose bar-by-bar returns[] come in:   // [p.109]
        total = sum(returns[0..nreturns-1])
        For each bar i:
            this_x = returns[i]
            IS_best[i] = total - this_x   // IS = sum of all bars except bar i
            OOS[i]     = this_x           // OOS = bar i's own return
            (update only if total - this_x > IS_best[i] on subsequent calls)
compute():                                                    // [p.110]
    *IS_return = sum(IS_best[0..nreturns-1])
    *OOS_return = sum(OOS[0..nreturns-1])
    *IS_return /= (nreturns - 1)   // each IS_best[i] is sum of nreturns-1 returns
    // OOS_return is NOT divided — raw sum
    *bias = *IS_return - *OOS_return
```
The leave-one-out trick creates a quick OOS proxy without retraining. [p.108-110]

**Walkforward (basic)** [p.148-149]

```
set IS_start = 0; IS_len = window; OOS_len = step
while IS_start + IS_len + OOS_len <= n:
   train on bars [IS_start .. IS_start + IS_len)
   apply trained system to bars [IS_start + IS_len .. IS_start + IS_len + OOS_len)
   append OOS returns to pool
   IS_start += OOS_len
Pool all OOS returns → final performance estimate.
```
Requires `min(lookback, lookahead) - 1` guard buffer at the train/test boundary when indicators look back multiple bars and target looks ahead multiple bars. [p.149-150, p.171]

**Nested Walkforward** [p.196-199]

```
Inputs: n_cases, prices, n_competitors, IS_n, OOS1_n
         OOS1 [n_competitors x n_cases]
         OOS2 [n_cases]
IS_start     = 0
OOS1_start   = IS_n
OOS1_end     = IS_n
OOS2_start   = IS_n + OOS1_n
OOS2_end     = IS_n + OOS1_n
while OOS2_end < n_cases:
   # 1. Each competitor makes a trade decision for bar OOS1_end
   #    using training window [IS_start .. OOS1_end); store its
   #    realised OOS return in OOS1[c, OOS1_end].
   # 2. Once OOS1_end - OOS1_start >= OOS1_n:
   #      Use OOS1 returns in [OOS1_start, OOS1_end) to score
   #      each competitor; pick the best subset.
   #      The realised return of the picked subset on bar
   #      OOS2_end goes into OOS2[OOS2_end].
   #      advance OOS1_start
   OOS1_end  += 1
   OOS2_end  += 1
   IS_start  += 1     # slide training window forward
Return OOS2[OOS2_start .. OOS2_end).
```
Required whenever you are *selecting among* systems; otherwise selection bias contaminates OOS. [p.196-199, p.201-202]

**BCa bootstrap confidence bound for mean return** [p.246-250]

```
1. Compute θ̂ = mean(returns).
2. For b = 1..B (B >= 2000): draw with replacement a sample same size as returns;
   record θ*_b = mean of that sample.
3. Bias correction:   z0 = Φ⁻¹( #{θ*_b < θ̂} / B )
4. Acceleration (via jackknife θ_(i)):
      a = Σ(θ̄_. - θ_(i))³ / (6 * [ Σ(θ̄_. - θ_(i))² ]^{3/2})
5. For desired level α, adjust quantiles:
      α_lo = Φ( z0 + (z0 + z_α )    / (1 - a(z0 + z_α )) )
      α_hi = Φ( z0 + (z0 + z_{1-α}) / (1 - a(z0 + z_{1-α})) )
6. Lower bound = α_lo quantile of { θ*_b }.
```
Handles mean returns and most well-behaved statistics, but **fails for ratio measures** (Sharpe, profit factor) whose denominator can collapse. [p.246-250, p.263]

**DRAWDOWN — bootstrap drawdown quantile bounds** [p.292, p.306-307]

```
Inputs: OOS returns (length n), n_trades (horizon for drawdown), nboot, quantiles q1..q4.
For b = 1..nboot:
   sample with replacement n_trades returns from full OOS pool
   build equity curve, compute max drawdown of that sample
   record
For each quantile q: report q-quantile of the nboot drawdown values.
```
Note n_trades is typically ~252 (1 year of daily bars); bootstrap sample == horizon, not == n. [p.306-307]

**MCPT — basic permutation test** [p.318-319]

```
for irep in 0..nreps-1:
   if irep > 0: shuffle price-changes within OOS region
   compute performance (OOS for fully-specified system; IS for training-process test; pooled OOS for model-factory test)
   if irep == 0:
       original_performance = performance; count = 1
   else:
       if performance >= original_performance: count += 1
p_value = count / nreps
```
Reject null (market is unordered noise) when p_value small. Applications: [p.312] fully-specified system, [p.314] training process (overfitting detector), [p.315-316] model factory. [p.310-319]

**MCPT — selection-bias-aware (best-of-many)** [p.319-320]

```
For each competitor c, compute its unpermuted performance.
For irep in 1..nreps-1:
   shuffle the shared driver series ONCE
   for each competitor c:  recompute performance under this shuffle
   record max performance across c
For each individual competitor c: p_value_c = fraction of reps with perf_c >= original_c.
Selection-bias-adjusted best p_value:
   p_best = fraction of reps whose max-across-c >= original best performance.
```
The *second* p-value is the one that matters. [p.319-320]

**Simple-market permutation** [p.327-328]

```
changes = diff(log_prices)         // preserves ups/downs magnitude
permute `changes` within OOS region
reconstruct log_prices via cumulative sum starting from original start price
// End price equals original end price because changes is only reshuffled
```

**Multi-market synchronised permutation** [p.334-335]

```
Align calendars so every date has a bar in every market (drop incomplete dates).
Draw ONE permutation σ of indices inside OOS region.
Apply σ identically to each market's change-vector and reconstruct.
```
Required to preserve cross-market correlation. [p.334-335]

## 5. Regras de Trading Explícitas

- **REGRA [p.14-15]:** Always work with log-prices and compute trade returns as differences of logs. Never use raw percent returns in statistical evaluations — asymmetry of +x%/−x% accumulates into a bogus positive expectation.
- **REGRA [p.17]:** Design the testing pipeline to eliminate *every* trace of future leak, including "innocuous" overlaps. A 1% edge produces a respectable equity curve; any leak is amplified.
- **REGRA [p.21, p.27-28]:** Before training any model, visually study each indicator's time-series plot. If its central tendency wanders for months/years, either oscillate (lagged difference), normalize with a moving window, or reject the indicator.
- **REGRA [p.30-31]:** Screen every candidate indicator for relative entropy ≥ 0.5 (hard concern at < 0.1). If low, revise the computation or apply a monotonic transform (tanh / logistic / log / tail cleaning).
- **REGRA [p.43]:** Start with a regularized linear model. Graduate to nonlinear only if a clear, validated advantage emerges.
- **REGRA [p.47]:** Never run a pure lasso (α = 1) on data that might contain near-perfect predictor collinearity. Use α just below 1 for stability.
- **REGRA [p.125-127]:** After optimization, plot parameter sensitivity curves around the optimum. Smooth decline = robust; narrow peak or multi-peak = overfit / lucky. Reject narrow-peak systems.
- **REGRA [p.143-144]:** After choosing among multiple competing systems based on OOS performance, the chosen OOS score is biased. You must hold out an additional fresh period for the final estimate, or use selection-bias MCPT [p.319-320].
- **REGRA [p.149-150, p.171]:** In walkforward or CV, remove `min(lookback, lookahead) − 1` cases as a guard buffer between train and test. For CV, remove the buffer on *both* sides of each test block.
- **REGRA [p.170-171]:** Do not use cross-validation for time-series trading-system performance estimation in general. Walkforward mimics real life; CV leaks nonstationarity and is pessimistically biased on smaller training sets. Narrow exceptions: optimizing model complexity or selecting predictors, where CV-inside-walkforward is reasonable. [p.211-212]
- **REGRA [p.196-199]:** Whenever a selector picks from competing systems on OOS returns, use nested walkforward so the selector's own decisions are evaluated on untouched outer-OOS data.
- **REGRA [p.244-245]:** For bounds on mean future returns with near-normal returns, use Student-t one-sided lower bound at the desired confidence. Beware heavy tails.
- **REGRA [p.246-247]:** With non-normal or uncertain distributions, use BCa bootstrap, not pivot or percentile methods. BCa is the single most important bounding tool for the true mean of returns.
- **REGRA [p.263-264]:** Never bootstrap the raw Sharpe ratio or raw profit factor. Bootstrap log(profit factor) instead; treat raw Sharpe bounds with "considerable caution."
- **REGRA [p.291]:** To bound future drawdowns, use the drawdown-specific bootstrap (sample of size = drawdown-horizon = typically 252, from the full OOS pool); expect millions of iterations; never use drawdown bounds inside training loops unless you apply the faster approximation on p.264.
- **REGRA [p.318, p.286]:** Run an MCPT on the *entire training process* (not just a final system). A good unpermuted result should sit in the extreme right tail of the permuted performance distribution (p < 0.05, ideally much smaller).
- **REGRA [p.319-320]:** When comparing several trading-system candidates, the decision-relevant p-value is the *best-of-many* selection-bias-adjusted MCPT p-value, not the per-system p-value.
- **REGRA [p.327-328]:** Permute *log-price changes*, not prices. Keep the first price fixed. Keep the shuffle inside the OOS region.
- **REGRA [p.334-335]:** For multi-market systems, use a single shared permutation across all markets to preserve cross-correlation; drop dates with any missing market.
- **NUNCA [p.16-17]:** Override the trading system based on gut feel. "Forget automated trading if you don't have the guts to believe in it."
- **NUNCA [p.34]:** Truncate (clip) outliers — truncation is non-monotonic and destroys information. Use tail cleaning (exp compression) instead.

## 6. Pitfalls e Anti-patterns

- [p.17] Casual developers claim "small" future leaks don't matter. They do. Treat any leak as catastrophic.
- [p.18-19] Bragging about how often a trading system wins is meaningless without the size of wins and losses — win/loss sizes and probabilities are inextricably related via Equation 1-1.
- [p.21] Do not run classical stationarity tests on markets — they always reject; time wasted.
- [p.27-28] Heavy counts in the > 256 / > 512 bins of STATN = slow wandering = a system built on this indicator will have long dormant or losing periods.
- [p.33-34] Outliers drag linear boundaries in their direction and break most trainers; low-entropy bimodal distributions also break models without outliers being present.
- [p.34] Dividing by a small denominator in an indicator formula is "thin ice" — outliers inevitable.
- [p.44-48] Too many predictors → overfit. Stepwise selection has all-or-nothing hysteresis: excluded variables never return. Regularized models gradually include/exclude, often finding better subsets.
- [p.46-47] Ordinary OLS with highly correlated predictors blows coefficients up to ±∞ and cancels them; ridge / elastic-net cure this.
- [p.85-87] Pure hill-climbers get stuck in local optima; pure GA is slow. DE is Masters' preferred compromise.
- [p.121, p.140-145] **Training bias** — IS performance always overstates future performance when parameters were optimized on IS data. You must measure it (StocBias cheap estimate or nested-WF honest estimate).
- [p.143-145] **Selection bias** — choosing the best of several OOS performances converts *all* winner-OOS scores into biased estimates. A common and lethal mistake.
- [p.150, p.172] Hidden IS/OOS overlap from lookback > 1 and lookahead > 1 is "more dangerous than you may think"; silently inflates performance.
- [p.170-171] Cross-validation on nonstationary time series leaks future volatility/regime information into training; CV "does not reflect real life."
- [p.171] "All else being equal, cross validation will slightly underestimate the performance that will be obtained when we finally train using the entire dataset" — **pessimistic** bias on its own, but combined with nonstationarity it can flip to optimistic.
- [p.218-220, p.263-264] Bootstrap confidence bounds on Sharpe ratio or profit factor often fail because these statistics have exploding variance when the denominator gets small.
- [p.285-291] Intuitive reasoning about drawdown is typically wrong. Bounding mean drawdown ≠ bounding next drawdown; individual drawdowns can be much worse than average.
- [p.292] Drawdown computations require ≈ 1e8 iterations for accuracy; even then results may be inexact.
- [p.314] "I have often seen people develop systems that look back optimizable parameters"... overfitting is caused by systems that are *too powerful*, not too weak — MCPT of the training process is the defense.
- [p.321-322] Do not confuse total in-sample return with skill. MCPT partitions return into three components: **Skill** (legitimate learned patterns likely to continue), **TrainingBias** (noise patterns learned in-sample that will not repeat), and **Trend** (long-bias contribution from a trending market); high "Trend" component means your system is mostly just long-biased.

## 7. Parâmetros Sensíveis

- **Relative entropy threshold = 0.5 (serious concern at < 0.1)** [p.31] — heuristic but pragmatic; Masters admits "this threshold is highly arbitrary." Not curve-fit (chosen from information theory, not optimization).
- **Elastic-net α** [p.47] — justified economically: α = 0 (ridge) spreads weights across correlated indicators; α = 1 (lasso) picks one; intermediate is a design choice, not an optimization target. Set α < 1 (e.g., 0.95) to avoid numerical instability with near-collinear predictors.
- **λ (regularization strength)** [p.65-66, p.82] — *should* be chosen by k-fold CV on pooled OOS explained variance. Not hand-tuned.
- **Entropy binning (nbins)** [p.41] — "around 20 or so bins is good" for market histories of several thousand bars. "If varying the number of bins by a small amount produces large changes in computed entropy, there's something fishy" — sensitivity check built in.
- **Tail fraction for clean_tails (0.01–0.10)** [p.38] — small; otherwise the "cleaning" distorts the useful body.
- **DE population size, overinit, mutate_dev, pcross, max_bad_gen** [p.85-91] — Masters shows the interface but does not publish "golden" values; he notes overinit (initial random pool > popsize) is key for the StocBias bias-estimate quality [p.106]. pcross (crossover probability) should "usually be small, perhaps 0.1 to 0.5 at most" [p.89].
- **Walkforward IS window size** [p.170-171] — Masters explicitly recommends matching the IS window to the size you will retrain with in production; do **not** chase larger IS windows chasing CV-like efficiency, because nonstationarity across regimes becomes a bigger problem than data scarcity.
- **Guard buffer = min(lookback, lookahead) − 1** [p.149-150] — derived analytically from overlap structure, **not** a hyperparameter.
- **Drawdown horizon n_trades = 252** [p.306-307] — Masters uses one trading year as default, noting this is configurable. Economic justification: annual performance reviews.
- **MCPT nreps** [p.338] — "hundreds or thousands"; the p-value resolution is limited by nreps.

## 8. Citações Literais Importantes

> "Future leak is far deadlier than you imagine. Take it seriously." — [p.17]

> "If someone brags about how often their trading system wins, ask them about the size of their wins and losses. And if they brag about how huge their wins are compared to their losses, ask them how often they win. Neither exists in isolation." — [p.19]

> "If I could leave readers of this book with only one thought, it would be this: the strength of your indicators is vastly more important than the strength of the predictive model that uses them to signal trades." — [p.43]

> "Cross validation is highly suspect compared to walkforward analysis when it comes to simulating real life. ... I cannot recommend cross validation analysis in trading system development, except in the most unusual special situations." — [p.170-171]

> "The problem in which permutation testing is valuable is the opposite of weakness: your system is too powerful at detecting predictive patterns. The term commonly employed for this situation is overfitting. When your system has too many optimizable parameters, it will tend to see random noise as predictive patterns and learn these patterns along with any legitimate patterns that might be present." — [p.314]

## 9. Conexões com Outros Livros Desta Base

- **`evidence_based_ta.md` (Aronson)** — same author-school (Masters wrote EBTA's statistical appendix style companion earlier); MCPT methodology in this book extends and operationalizes the Monte Carlo permutation test framework Aronson uses to evaluate rule-based systems; both books share the "specification-destroying shuffle" philosophy. [p.310-319 here vs. Aronson's MCPT chapters]
- **`advances_fin_ml.md` (López de Prado)** — López de Prado's CPCV (Combinatorial Purged Cross-Validation) solves the same purge/embargo concern that Masters addresses with the `min(lookback, lookahead) - 1` guard buffer [p.149-150, p.162, p.171]. Masters arrives at the buffer analytically for WF and CV; LdP formalizes purge+embargo for combinatorial CV. CSCV here [p.182] traces to Bailey et al. 2015, the same paper LdP cites for DSR (Deflated Sharpe Ratio).
- **`stat_sound_indicators.md`** — N/A — summary not present in current base (file not in books/summaries/). Revisit when processed; entropy-based indicator screening [p.30-31, p.34-37] and tail-cleaning [p.38-40] should cross-reference directly.
- **`systematic_trading.md` (Carver)** — parameter parsimony agreement: Carver's argument for 3-4 parameters max on economic grounds parallels Masters' regularization [p.44-48] and sensitivity-curve [p.125-127] arguments that reach the same conclusion statistically. Both reject curve-fit optimization.
- **`ml_for_asset_managers.md` (López de Prado)** — same anti-overfit spirit; MCPT of the training process [p.314-319] is methodologically akin to LdP's backtest-overfitting probability via CSCV.
- **`leverage_space.md` / `volatility_trading.md`** — N/A for direct content overlap; Masters does not discuss leverage/position-sizing optimization.
- **`time_series_hamilton.md`** — shares classical statistical machinery (Student-t, bootstrap), but Masters operationalizes for trading with much more skepticism about parametric assumptions; Hamilton supplies the theory Masters applies.
- **`machine_trading.md` (Chan)** — Chan recommends walkforward as well; Masters' nested walkforward [p.196-199] is stricter when a selector exists.
