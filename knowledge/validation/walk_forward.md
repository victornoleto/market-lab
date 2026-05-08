# Walk-Forward Analysis

Sliding train/test — simulates real operation with periodic re-optimization.

## Sources

- [`books/testing_tuning.md`](../books/testing_tuning.md)
- [`books/trading_systems_methods.md`](../books/trading_systems_methods.md)

## Pending sources (not yet absorbed)

- `books/stat_sound_indicators.md` — missing (absorb with `/absorb-book stat_sound_indicators`)

## From `books/testing_tuning.md`

### Explicit Trading Rules

- **RULE [p.14-15]:** Always work with log-prices and compute trade returns as differences of logs. Never use raw percent returns in statistical evaluations — asymmetry of +x%/−x% accumulates into a bogus positive expectation.
- **RULE [p.17]:** Design the testing pipeline to eliminate *every* trace of future leak, including "innocuous" overlaps. A 1% edge produces a respectable equity curve; any leak is amplified.
- **RULE [p.21, p.27-28]:** Before training any model, visually study each indicator's time-series plot. If its central tendency wanders for months/years, either oscillate (lagged difference), normalize with a moving window, or reject the indicator.
- **RULE [p.30-31]:** Screen every candidate indicator for relative entropy ≥ 0.5 (hard concern at < 0.1). If low, revise the computation or apply a monotonic transform (tanh / logistic / log / tail cleaning).
- **RULE [p.43]:** Start with a regularized linear model. Graduate to nonlinear only if a clear, validated advantage emerges.
- **RULE [p.47]:** Never run a pure lasso (α = 1) on data that might contain near-perfect predictor collinearity. Use α just below 1 for stability.
- **RULE [p.125-127]:** After optimization, plot parameter sensitivity curves around the optimum. Smooth decline = robust; narrow peak or multi-peak = overfit / lucky. Reject narrow-peak systems.
- **RULE [p.143-144]:** After choosing among multiple competing systems based on OOS performance, the chosen OOS score is biased. You must hold out an additional fresh period for the final estimate, or use selection-bias MCPT [p.319-320].
- **RULE [p.149-150, p.171]:** In walkforward or CV, remove `min(lookback, lookahead) − 1` cases as a guard buffer between train and test. For CV, remove the buffer on *both* sides of each test block.
- **RULE [p.170-171]:** Do not use cross-validation for time-series trading-system performance estimation in general. Walkforward mimics real life; CV leaks nonstationarity and is pessimistically biased on smaller training sets. Narrow exceptions: optimizing model complexity or selecting predictors, where CV-inside-walkforward is reasonable. [p.211-212]
- **RULE [p.196-199]:** Whenever a selector picks from competing systems on OOS returns, use nested walkforward so the selector's own decisions are evaluated on untouched outer-OOS data.
- **RULE [p.244-245]:** For bounds on mean future returns with near-normal returns, use Student-t one-sided lower bound at the desired confidence. Beware heavy tails.
- **RULE [p.246-247]:** With non-normal or uncertain distributions, use BCa bootstrap, not pivot or percentile methods. BCa is the single most important bounding tool for the true mean of returns.
- **RULE [p.263-264]:** Never bootstrap the raw Sharpe ratio or raw profit factor. Bootstrap log(profit factor) instead; treat raw Sharpe bounds with "considerable caution."
- **RULE [p.291]:** To bound future drawdowns, use the drawdown-specific bootstrap (sample of size = drawdown-horizon = typically 252, from the full OOS pool); expect millions of iterations; never use drawdown bounds inside training loops unless you apply the faster approximation on p.264.
- **RULE [p.318, p.286]:** Run an MCPT on the *entire training process* (not just a final system). A good unpermuted result should sit in the extreme right tail of the permuted performance distribution (p < 0.05, ideally much smaller).
- **RULE [p.319-320]:** When comparing several trading-system candidates, the decision-relevant p-value is the *best-of-many* selection-bias-adjusted MCPT p-value, not the per-system p-value.
- **RULE [p.327-328]:** Permute *log-price changes*, not prices. Keep the first price fixed. Keep the shuffle inside the OOS region.
- **RULE [p.334-335]:** For multi-market systems, use a single shared permutation across all markets to preserve cross-correlation; drop dates with any missing market.
- **NEVER [p.16-17]:** Override the trading system based on gut feel. "Forget automated trading if you don't have the guts to believe in it."
- **NEVER [p.34]:** Truncate (clip) outliers — truncation is non-monotonic and destroys information. Use tail cleaning (exp compression) instead.

### Formulas / Equations

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

### Algorithms and Pseudocode

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

### Pitfalls and Anti-patterns

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

---

## From `books/trading_systems_methods.md`

### Explicit Trading Rules

**Market selection by noise**:
- **RULE [p.13]**: Low-noise markets (short-rates, long-maturity bonds, USD crossrates, energy, metals) -> trend-following.
- **RULE [p.13]**: High-noise markets (equity indices) -> mean-reverting / countertrend.
- **RULE [p.13-14]**: Long-term traders use low-frequency (weekly/monthly) + long-term trends. Short-term traders use high-frequency + mean-reverting.

**Swing / Event-Driven Trend Rules**:
- **RULE [p.168]**: Conservative swing entry -- buy when current upswing high exceeds previous upswing high; sell short when current downswing low falls below previous downswing low.
- **RULE [p.191]** (Livermore): Enter only in direction of major trend (higher highs+higher lows, or lower lows+lower highs); add each penetration confirmation; stop-loss at penetration beyond prior pivot.
- **RULE [p.172]** (Keltner Minor Trend): Buy when daily trades above most recent high; stay long until trades below most recent low. Always reverse.
- **RULE [p.195]** (Wilder Swing Index): Long when ASI_t > HSP_{t-2}; short when ASI_t < LSP_{t-2}; SAR at most recent opposite swing point.

**Point-and-Figure**:
- **RULE [p.199]**: Buy when X one box above highest X of last X column. Sell when O below lowest O of last O column.
- **RULE [p.201]**: Filter signals with 45-degree trendlines -- only take longs when 45-degree trendline up, shorts when down.

**Moving-average and trend systems**:
- **RULE [p.285]**: Use MA length < half the cycle period to preserve cycle visibility.
- **RULE [p.285]**: Match MA period to trading horizon -- 63-day = quarterly; 252-day = annual; 200-day = stock-market macro benchmark.
- **RULE [p.352-353]** (Donchian 5/20): Buy if not long AND $C_t > MA5_{t-1} + ATR_{t-1}$ AND $C_t > MA20_{t-1} + ATR_{t-1}$. Exit long if either MA band violated.
- **RULE [p.353]**: Position Size = Investment / (ATR * Big Point Value).
- **RULE [p.353]** (Donchian 20/40 = Turtle basis): Buy when high > max high 40 days; exit long when low < min low 20 days.
- **RULE [p.354]**: Golden Cross (50 crosses above 200) -- buy SPY; when 50 crosses below 200 (Death Cross) -> short/flat. Yielded 66.7% return over 1999-2010 vs. passive -7.8%.
- **RULE [p.355]** (Woodshedder ROC): Buy when 5-day ROC below 252-day ROC for 2 consecutive days; exit long when 5-day > 252-day for 2 consecutive days.
- **RULE [p.326-327]** (Bollinger reversal): Buy on close > upper band; short on close < lower band. Exit at center trendline -> cuts order size 50%.
- **RULE [p.333]** (Volatility System): $V_t = \frac{1}{n}\sum TR_i$; sell if close drops by $k \cdot V_{t-1}$ (k approx 3).

**Oscillators / Momentum**:
- **RULE [p.383]** (MACD): Buy when MACD crosses up through signal; require MACD to have first penetrated opposite threshold (e.g. +/-2.00) to filter whipsaws.
- **RULE [p.386-387]** (RSI): Wilder 70/30 overbought/oversold; per Aan (1985) [p.387-388] prefer 80/20 (1.5 sigma).
- **RULE [p.388]**: For sustained moves of 14+ days, RSI stays saturated -- do not fade blindly.
- **RULE [p.392]** (Stochastic): Buy when %D below 20 and cross back up; sell when %D above 80 and cross back down. Always confirm with longer-term trend direction.
- **RULE [p.640]** (Ruggiero COT): Buy when COT Index Commercials [lag 1+ week] > trigger AND COT Index Small Traders < trigger. Commercials' actions lead.
- **RULE [p.640]**: Exit mean-reverting trade at neutral (50), not opposite extreme.

**KAMA (trading)**:
- **RULE [p.783]**: Trade KAMA via trendline direction -- buy when it turns up, sell when it turns down.
- **RULE [p.783]**: Keep ER period <= 14 days (default 10); leave slowest = 30 fixed; raise fastest from 2 to reduce sensitivity; use small threshold filter (~0.1 SD of trendline changes) to prevent false flips.

**Risk Control**:
- **RULE [p.53]**: Target volatility for book default = 12% annualized.
- **RULE [p.1037]**: Initial stop below low of entry day OR previous day's low, whichever is lower. Move to break-even ASAP; trail to protect 50% of peak profit.
- **RULE [p.1057-1059]**: Size position inversely proportional to ATR for equal-risk allocation across markets.
- **RULE [p.1091]**: Use optimal f as UPPER BOUND; never size larger, or if you get average results you can expect to go broke eventually.
- **RULE [p.1091]**: Simpler alternative -- trade constant position size with reserve large enough to absorb extreme moves.
- **RULE [p.942]**: Investor capitalization = 3 * maximum drawdown.
- **RULE [p.942]**: Require >= 400 trades to reduce sample error to ~5%.

**Seasonal / Calendar**:
- **RULE [p.480]** (Holiday -- Kaeppel): Buy on close 3 days before an exchange holiday; sell on close 2 days later.
- **RULE [p.480]** (Hirsch): Buy first trading day of November; sell last trading day of April.
- **RULE [p.482]** (McGinley January): If first 5 trading days of January are up >= 4%, year has always been up. Buy, hold full year.
- **RULE [p.480]** (Month-End): Buy last (or 2nd-to-last) day of month; sell 4th trading day of next month.

**Day Trading**:
- **RULE [p.741]**: Prefer mean-reverting day strategies -- passive entry orders have near-zero slippage and may earn liquidity rebate.
- **RULE [p.740]**: Favor markets with highest volume AND highest volatility simultaneously.

**NUNCA**:
- **NEVER [p.1091]** (Elder): Never average down. Never meet margin calls. Liquidate worst position first.
- **NEVER [p.27]**: Never reuse out-of-sample data after the first validation run -- feedback contaminates.
- **NEVER [p.919]**: Never iterate step-forward test design after seeing results -- recreates overfitting.
- **NEVER [p.941]**: Never change test ranges after tests started -- prevents data-snooping bias.

### Formulas / Equations

**Efficiency Ratio** [p.10-11, p.781]:
$$ER_t = \frac{|P_t - P_{t-n}|}{\sum_{i=t-n+1}^{t} |P_i - P_{i-1}|}$$

**Price Density** [p.12]:
$$PD = \frac{\sum (\text{High}_i - \text{Low}_i)}{\max(\text{High}, n) - \min(\text{Low}, n)}$$

**Weighted average (time interval)** [p.30]:
$$W = \frac{\sum a_i d_i}{\sum d_i}$$

**Geometric mean** [p.31]: $G = (a_1 \cdot a_2 \cdots a_n)^{1/n}$.

**Variance** [p.38]: $\text{Var} = \frac{\sum (p_i - \bar{P})^2}{n - 1}$.

**Standard deviation** [p.38]: $\sigma = \sqrt{\frac{\sum (p_i - \bar{P})^2}{n}}$ (population; Excel `Stdevp`). 1σ = 68%, 2σ = 95.5%, 3σ = 99.7%.

**Skewness** [p.39]: $S = \frac{\sum (p_i - \bar{P})^3}{(n-1)\sigma^3}$; shorthand: $S = 3(\text{Mean} - \text{Median})/\sigma$.

**Kurtosis** [p.42]: $K = \frac{\sum (p_i - \bar{P})^4}{(n-1)\sigma^4}$; excess = $K - 3$.

**Durbin-Watson** [p.43-44]: $d = \sum (e_i - e_{i-1})^2 / \sum e_i^2$. d=2: no autocorrelation; d<2: positive; d>2: negative.

**t-statistic** [p.47]: $t = \frac{\text{avg}}{\text{SD}} \sqrt{n}$; df = n − 1.

**NAV chain** [p.49]: $\text{NAV}_t = \text{NAV}_{t-1} (1 + r_t)$; $\text{NAV}_0 = 100$.

**Annualization** [p.53]: multiply daily SD by $\sqrt{252}$; monthly $\sqrt{12}$.

**Information Ratio** [p.58]: annualized return / annualized SD of returns.

**Sharpe Ratio** [p.58]: (annualized return − risk-free) / annualized SD.

**Treynor Ratio** [p.58]: (annualized return − risk-free) / portfolio beta.

**Calmar Ratio** [p.1037]: $\text{Calmar} = AROR / \text{max drawdown}$.

**Sortino Ratio** [p.1038]: $SR = (AROR - MAR)/\sigma_{PE-E}$; denominator is SD of (peak equity − current equity).

**Ulcer Index** [p.1038]: $UI = \sqrt{\frac{\sum D_i^2}{n}}$ where $D_i$ = highest equity to date − current equity.

**Simple moving average** [p.284]: $MA_t = \sum_{i=t-n+1}^t p_i / n$.

**SMA rolling update** [p.285]: $MA_t = MA_{t-1} + (p_t - p_{t-n})/n$.

**Average-off (end-drop smoothing)** [p.287]: $\text{AvgOff}_t = \frac{(n-1) \text{AvgOff}_{t-1} + p_t}{n}$.

**Pivot-Point MA (11-bar)** [p.290]:
$$PPMA_t(11) = \frac{-3 p_{t-10} - 2 p_{t-9} - p_{t-8} + 0 p_{t-7} + p_{t-6} + 2 p_{t-5} + 3 p_{t-4} + 4 p_{t-3} + 5 p_{t-2} + 6 p_{t-1} + 7 p_t}{22}$$
General: $PPMA_t(n) = \frac{2}{n(n+1)} \sum_{i=1}^{n} (3i - n - 1) P_{t-n+i}$.

**Exponential smoothing** [p.294]: $E_t = E_{t-1} + a(p_t - E_{t-1})$; initialize $E_1 = p_1$.

**Smoothing-constant ↔ days (Hutson)** [p.295]: $c = 2/(n+1)$.

**Hull Moving Average** [p.286]:
```
WAVG1 = WAVG(close, p)
WAVG2 = WAVG(close, int(p/2))
HMA   = WAVG(2*WAVG2 - WAVG1, int(sqrt(p)))
```

**TRIX** [p.334]:
- $E1_t = E1_{t-1} + s(\ln p_t - E1_{t-1})$ [p.334]
- $E2_t = E2_{t-1} + s(E1_t - E2_{t-1})$ [p.334]
- $E3_t = E3_{t-1} + s(E2_t - E1_{t-1})$ [p.334]
- $TRIX = (E3_t - E3_{t-1}) \times 10000$; recommended $n = 6$, so $s = 2/7$. [p.334]

**KAMA (Kaufman Adaptive Moving Average)** [p.780-781]:
- $KAMA_t = KAMA_{t-1} + sc_t (p_t - KAMA_{t-1})$ [p.780-781]
- $sc_t = [ER_t (\text{fastest} - \text{slowest}) + \text{slowest}]^2$ [p.780-781]
- fastest = $2/(2+1) = 0.6667$; slowest = $2/(30+1) = 0.0645$ [p.780-781]
- ER lookback default = 10 days; slow-end equivalent = 900-period when ER = 0. [p.780-781]
- TradeStation code [p.781]:
  ```
  KAMA = KAMA[1] + ((absvalue(C-C[10])/summation(absvalue(C-C[1]),10)*0.6022)+0.0645)^2 * (C-KAMA[1])
  ```

**VIDYA (Chande)** [p.785]:
- $VIDYA_t = k s C_t + (1 - ks) VIDYA_{t-1}$ [p.785]
- $s$ = 0.20 (9-day base EMA constant) [p.785]
- $k = \text{stdev}(C, n) / \text{stdev}(C, m)$, default n=9, m=30. [p.785]

**Fractal Dimension (Ehlers FRAMA)** [p.784]: $D = \log(N_2/N_1)/\log(s_1/s_2)$.

**MAMA/FAMA (Ehlers MESA Adaptive)** [p.786]:
- $sc = \text{fast\_limit} / \text{phase\_rate\_of\_change}$; clamped to [0.05, 0.50]. [p.786]
- FAMA uses MAMA with smoothing constant × 0.5. [p.786]

**Wilder Swing Index** [p.193]:
$$SI_t = 50 \times \frac{(C_t - C_{t-1}) + 0.5(C_t - O_t) + 0.25(C_{t-1} - O_{t-1})}{TR_t} \times \frac{K}{M}$$
K = larger of $|H_t - C_{t-1}|$, $|L_t - C_{t-1}|$; M = limit move (100); TR_t via one of 3 sub-formulas.

**True Range** [p.107]: largest of $|H_t - C_{t-1}|$, $|L_t - C_{t-1}|$, $H_t - L_t$.

**Accumulated Swing Index** [p.194]: $ASI_t = ASI_{t-1} + SI_t$.

**Bollinger Bands** [p.323]: $MA_{20}(C) \pm 2\sigma(C, 20)$.

**Modified Bollinger (McNicholl)** [p.325-326]:
- $M_t = \alpha C_t + (1-\alpha) M_{t-1}$; $U_t = \alpha M_t + (1-\alpha) U_{t-1}$ [p.325-326]
- $D_t = ((2-\alpha)M_t - U_t)/(1-\alpha)$ [p.325-326]
- $m_t = \alpha|C_t - D_t| + (1-\alpha) m_{t-1}$; $u_t = \alpha m_t + (1-\alpha) u_{t-1}$ [p.325-326]
- $d_t = ((2-\alpha)m_t - u_t)/(1-\alpha)$ [p.325-326]
- $BU_t = D_t + f d_t$; $BL_t = D_t - f d_t$. Default $\alpha = 0.15$, $f = 2.5$. [p.325-326]

**Volatility System (Bookstaber)** [p.333]:
- $V_t = (1/n) \sum TR_i$ [p.333]
- Sell if close drops by more than $k \cdot V_{t-1}$; Buy reverse. $k \approx 3$. [p.333]

**CCI (Commodity Channel Index)** [p.172]:
- $ADP_t = (H_t + L_t + C_t)/3$; n-day average. [p.172]
- $AvgDev_t$ = n-day average of $|H_i + L_i + C_i - ADP_t|$. [p.172]
- $CCI_t = \frac{(H_t + L_t + C_t)/3 - ADP_t}{0.015 \times AvgDev_t}$. [p.172]

**MACD** [p.382]: MACD = EMA(close,12) − EMA(close,26); Signal = EMA(MACD, 9). Histogram = MACD − Signal.

**RSI (Wilder)** [p.386]:
$$RSI = 100 - \frac{100}{1 + RS}, \quad RS = AU/AD$$
- $AU_t = AU_{t-1} - AU_{t-1}/14 + \max(p_t - p_{t-1}, 0)$ [p.386]
- $AD_t = AD_{t-1} - AD_{t-1}/14 + \max(p_{t-1} - p_t, 0)$ [p.386]

**Stochastic (Lane)** [p.392]:
- Raw $\%K_t = 100 \times (C_t - L_t(n))/R_t(n)$ [p.392]
- $\%D$ (also %K-slow) = 3-day average of raw %K [p.392]
- %D-slow = 3-day average of %D [p.392]

**CMO (Chande)** [p.388]: $CMO = 100 \times (S_u - S_d)/(S_u + S_d)$.

**On-Balance Volume** [p.537]: $OBV_t = OBV_{t-1} + \text{sign}(C_t - C_{t-1}) V_t$.

**Money Flow Index** [p.540]: typical price × volume accumulation separated by up/down days → RSI-style ratio.

**Volume Accumulator (Chaikin)** [p.540]: $VA_t = VA_{t-1} + ((C_t - L_t)/(H_t - L_t) - 0.5) \times 2 V_t$.

**Accumulation Distribution** [p.541]: $AD_t = AD_{t-1} + (C_t - O_t)/(H_t - L_t) \times V_t$.

**Intraday Intensity** [p.541]: $II_t = II_{t-1} + ((C_t - L_t) - (H_t - C_t))/(H_t - L_t) \times V_t$.

**McClellan Oscillator** [p.549]:
- $NA_t$ = Advances − Declines [p.549]
- $E1_t$ = 0.10 EMA of $NA$; $E2_t$ = 0.05 EMA of $NA$ [p.549]
- Oscillator = $E1_t - E2_t$. [p.549]

**Advance-Decline Index** [p.548]: $ADI_t = ADI_{t-1} + (\text{Advances}_t - \text{Declines}_t)$.

**Pairs Trading Stress Indicator (Kaufman)** [p.585]: stochastic of the difference of two leg stochastics; entry when > 95 or < 5.

**Pivot Points (intraday)** [p.667]:
- $P = (H + L + C)/3$ [p.667]
- $R_1 = 2P - L$; $S_1 = 2P - H$ [p.667]
- $R_2 = (P - S_1) + R_1$; $S_2 = P - (R_1 - S_1)$ [p.667]

**Force Index (Elder)** [p.836]: $FI_t = V_t (C_t - C_{t-1})$; 2-day EMA smoothing (const 0.333).

**Elder-Ray** [p.837]: Bull Power = $H_t - EMA_{13}$; Bear Power = $L_t - EMA_{13}$.

**COT Index (Briese)** [p.639]:
$$\text{COT Index}_t = 100 \times \frac{NL_t - \min(NL, n)}{\max(NL, n) - \min(NL, n)}$$
n = 1.5 to 4 years; essentially a stochastic of net long positions.

**Kelly growth function** [p.1090]:
$$G(f) = P \ln(1 + Bf) + (1-P)\ln(1-f)$$

**Kelly closed form** [p.1090]:
$$f = \frac{p(PLR + 1) - 1}{PLR}$$
Example [p.1091]: $p = 0.5$, PLR = 2 → $f = 0.25$.

**Optimal f (Vince)** [p.1090]:
$$\text{optimal } f = \arg\max_{f \in [0.01, 1]} \left( \prod_{i=1}^{n} \left(1 + \frac{R_i}{-\text{Largest loss}} f \right) \right)^{1/n}$$

**Markowitz approximation / optimal leverage** [p.1092]:
- Expected leveraged log return $= M \mu - \frac{1}{2} M^2 \sigma^2$ [p.1092]
- Optimal leverage $M^* = \mu/\sigma^2$ [p.1092]

**Portfolio expected return** [p.1088]: $E(R) = \sum w_i E(R_i)$, $\sum w_i = 1$.

**Portfolio variance** [p.1088]: $\sigma^2_R = \sum w_i^2 \sigma_i^2 + \sum\sum_{i\ne j} w_i w_j \text{cov}_{ij}$ where $\text{cov}_{ij} = \text{corr}_{ij} \sigma_i \sigma_j$.

### Algorithms and Pseudocode

**KAMA (Kaufman Adaptive Moving Average)** [p.780-781]:
```
Input: close series, ER_period=10, fast=2, slow=30
fastest = 2/(fast+1)   # = 0.6667
slowest = 2/(slow+1)   # = 0.0645
for t in range(ER_period, len(close)):
    numer = abs(close[t] - close[t - ER_period])
    denom = sum(abs(close[i] - close[i-1]) for i in t-ER_period+1..t)
    ER    = numer / denom
    sc    = (ER * (fastest - slowest) + slowest) ** 2
    KAMA[t] = KAMA[t-1] + sc * (close[t] - KAMA[t-1])
```

**Channel Breakout with regression** [p.167-169]:
```
1. Select data from last swing high/low (use swing program or pivot points) [p.167-169]
2. X = [1, 2, ..., n]; Y = closes of same length. [p.167-169]
3. Run linear regression -> slope a, intercept b. [p.167-169]
4. BL = distance from regression line to lowest low below line;
   BU = distance from regression line to highest high above line. [p.167-169]
5. Projected upper channel band at n+1 = a*X + b + BU + a [p.167-169]
   Projected lower channel band at n+1 = a*X + b - BU + a
6. Signal: close breaks projected band opposite to slope direction -> trend change. [p.167-169]
```

**Donchian 20/40 Breakout (Turtles foundation)** [p.353]:
```
Buy when today's high > max(high, 40 days)
Sell short when today's low < min(low, 40 days)
Exit long when today's low < min(low, 20 days)
Exit short when today's high > max(high, 20 days)
```

**DeMark Sequential Setup + Countdown** [ch.4, p.173-175]:
```
SETUP:
  9 consecutive closes < close 4 bars ago
INTERSECTION (validation):
  Day 8 or later high >= low of 3 or more days earlier
COUNTDOWN:
  Count days where close < close 2 days ago (not necessarily consecutive)
  When count reaches 13 -> BUY, unless invalidated by:
    - Close exceeds highest intraday high during setup [ch.4, p.173-175]
    - Sell setup occurs (9 consec up closes vs. 4 back) [ch.4, p.173-175]
    - Another buy setup occurs before countdown completes (recycle) [ch.4, p.173-175]
ENTRY: close of signal day, OR close > close 4 days ago, OR close > high 2 days earlier
EXIT stop:
  True range of lowest-range day during setup+countdown
  subtracted from low of that day
```

**Swing Filter Chart Construction** [p.165]:
```
1. Choose swing filter (% or absolute value). [p.165]
2. Begin: current bar high = swing high, low = swing low; assume upswing. [p.165]
3. For each new bar:
   IF in upswing:
     IF high > current swing high: extend upswing to new high.
     ELSE IF (swing high - current low) >= swing filter:
        start new downswing column from swing high to current low.
   ELSE (downswing):
     IF low < current swing low: extend downswing to new low.
     ELSE IF (current high - swing low) >= swing filter:
        start new upswing column.
```

**Step-Forward (Walk-Forward) Testing** [p.918]:
```
1. Total period = e.g. 20 years. [p.918]
2. In-sample window = e.g. 2 years (or 5y if long-term bias). [p.918]
3. Start at earliest data:
   - Optimize parameters on in-sample window. [p.918]
   - Apply best parameters to NEXT 6 months (OOS). [p.918]
   - Accumulate OOS returns. [p.918]
4. Roll forward 6 months; repeat step 3. [p.918]
5. Final performance = accumulated OOS stream. [p.918]
6. NEVER iterate design after seeing OOS results -> feedback = overfit. [p.918]
```

**Pairs Trading via Stress Indicator** [p.584-585]:
```
Inputs: two legs A, B; n = 14
Compute 14-day raw stochastic for A (S1) and B (S2)
D_t   = S1 - S2
Stress_t = 100 * (D_t - min(D, n)) / (max(D, n) - min(D, n))
ENTRY:
  Stress > 95 -> short A, long B
  Stress < 5  -> long A, short B
POSITION SIZING (equal dollar-risk via ATR) [p.586]:
  For each leg, compute ATR20_dollars.
  Size = FIXED_INVESTMENT / ATR20_dollars.
  Example: $5 stock, ATR=$0.25 -> 4000 shares; $25 stock, ATR=$1 -> 1000 shares.
EXIT:
  Stress returns near center.
```

**Kelly / Optimal f Search** [p.1090]:
```
Input: trade returns R_1..R_n; largest_loss (positive value)
best_f  = 0
best_G  = -inf
for f in 0.01..1.0 step 0.01:
  G = geometric_mean( (1 + R_i / -largest_loss * f) for i in 1..n )
  if G > best_G: best_G = G; best_f = f
return best_f
```

**Triple Screen (Elder)** [p.835-838]:
```
Screen 1 (Long-term trend direction):
  Compute weekly MACD histogram (13-week EMA).
  Direction = sign(MACD_week_t - MACD_week_{t-1})

Screen 2 (Intermediate timing oscillator):
  Option A: Force Index = Volume * (Close - PrevClose), 2-day EMA.
    Buy setup: 2-day FI below centerline AND not below multi-week low.
  Option B: Stochastic_14 below 30.
  Option C: Elder-Ray; Bear Power < 0 AND rising (not positive).

Screen 3 (Fast entry):
  Buy-stop just above previous day's high on 60-min bars.

Stop-loss (long):
  Initial: below low of entry day OR previous day's low, whichever lower.
  Move to break-even ASAP.
  Trail to protect 50% of peak profit.
```

**Portfolio Allocation via Excel Solver (Markowitz mean-variance)** [p.1109-1110]:
```
1. Load monthly % returns for assets A1..An. [p.1109-1110]
2. Compute: monthly means, standard deviations, pairwise correlations. [p.1109-1110]
3. Decision variables: allocation weights w_1..w_n. [p.1109-1110]
4. Objective: maximize portfolio return / standard deviation ratio,
   using the full covariance (variance + pairwise correlation terms). [p.1109-1110]
5. Constraints: sum w_i = 1; each w_i >= 0 (or a specified minimum). [p.1109-1110]
6. Solver -> optimal weights on efficient frontier. [p.1109-1110]
```
(Kaufman's Ch 24 later contrasts this traditional mean-variance approach with his GASP Genetic Algorithm Solution to Portfolios, arguing mean-variance breaks when strategy returns include many zero-days from being out of the market.)

### Pitfalls and Anti-patterns

- [p.27] "All testing is overfitting the data." In-sample/out-of-sample discipline is mandatory; OOS can only be used once.
- [p.43] Kurtosis on daily returns > 7-8 -> "it begins to look as though the trading method is overfitted."
- [p.132-133] Backtesting over periods with price shocks (2001, 2008) produces apparent predictive power -- your system may "profit" from events it never could have forecast in real time.
- [p.172] CCI and SD-channel overbought conditions can persist for weeks during strong trends. Mechanical OB/OS fading "gives frequent small profits and an occasional very large loss."
- [p.170] Event-driven systems (swing, point-and-figure) have higher per-trade risk than time-based systems -- entry-to-reversal distance can run large before a signal fires.
- [p.290] Pivot-point MA with negative weights can put trendline out of phase with price in short intervals -- best for long-term cyclic markets only.
- [p.326-327] Bollinger bands "bulge" after volatility spikes and narrow slowly. Modified Bollinger (McNicholl) does not remove the bulge but corrects it faster.
- [p.329] Delayed entries (next-day open) improve price 75% of the time but cost overall profits -- fast breakouts that never retrace are missed.
- [p.387-388] Wilder's default 70/30 RSI thresholds = only 0.675 sigma of RSI distribution -- too tight. Prefer 80/20 (~1.5 sigma).
- [p.381] Mean-reversion against a strong trend: "the trend is not your friend if it fights with your mean-reversion."
- [p.541] PVT and % volume indicators fail on back-adjusted futures (prices can go negative).
- [p.584] Pairs trading is mean-reverting -- hold few days only; longer holds let trend component dominate.
- [p.585-586] Even closely linked pairs diverge on idiosyncratic events (Barrick Gold earnings miss). Pairs do NOT eliminate idiosyncratic risk.
- [p.652] Elliott Wave designed for broad indexes -- "Elliott never intended to apply his principle to individual stocks."
- [p.743] Economic report releases (FOMC, Chicago PMI, API/AGA) cause fillable-price gaps. Directional day trading suffers 10-20% unables during news periods.
- [p.783] Exponential smoothing flips direction when price penetrates -- tiny smoothing constants in KAMA produce false flips without a trend-change filter.
- [p.802] 2008 crude oil 140% annualized vol was artifact of lagging 20-day SD, not real risk.
- [p.914] Back-adjusted futures can go negative -> percentage-based stops and percentage volatility calcs break.
- [p.914] Back-adjusted split-adjusted stocks: 1990 $50 stock with 2x splits becomes $12.50 -- loses volatility characteristics.
- [p.916] Monte Carlo random rearrangement of data destroys bull->bear transitions -> abandoned by practitioners.
- [p.919] Step-forward short-interval bias: 2-year in-sample favors fast trend models; use 5-year in-sample for long-term strategies.
- [p.938] Bull-market-biased parameters: "The mistake is extrapolating probable future performance on the basis of an isolated and well-chosen example from the past." -- Schwager.
- [p.939] "Discovering a price pattern or cycle through optimization may seem to be a revelation, but it is more likely to be an illusion."
- [p.939] Best systems use 4 or fewer parameters. More is worse.
- [p.941] Survivorship bias -- hedge fund benchmarks omit funds that blew up.
- [p.941] Asymmetric return fallacy -- -50% then +50% = -25% net.
- [p.1038] Historic max drawdown is a lower bound -- "future always brings larger drawdowns."
- [p.1109] Globalization has increased correlations -- past patterns of returns unlikely to represent all future patterns (implicit critique of stationary-correlation assumptions in classic MPT).
- [p.1109] "Globalization has increased correlations... past patterns of returns are not likely to represent all of the patterns that will be seen in the near future."
- [p.1091] If you trade above optimal f and get average results, you eventually go broke. If below, risk drops arithmetically while profits drop geometrically.
- [p.1091] Theory of Runs (Ch 22): 100 trades expect 1 run of 6. Sequential losing runs of 4-5 are not pathological -- plan for them.

---

## Companion C++ Code (reference implementations)

These are reference C++ implementations from Timothy Masters' companion code.
Use as authoritative pseudocode when porting to Python in Phases 4/5.

- [`books/code/masters-testing-tuning/DRAWDOWN/DRAWDOWN.CPP`](../../books/code/masters-testing-tuning/DRAWDOWN/DRAWDOWN.CPP)
