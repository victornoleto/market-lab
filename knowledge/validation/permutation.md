# Permutation & Monte Carlo Tests

Testes de permutação para validar que edge é estatisticamente significativo (não sorte).

## Sources

- [`books/advances_fin_ml.md`](../books/advances_fin_ml.md)
- [`books/testing_tuning.md`](../books/testing_tuning.md)
- [`books/stat_sound_indicators.md`](../books/stat_sound_indicators.md)
- [`books/evidence_based_ta.md`](../books/evidence_based_ta.md)

## From `books/advances_fin_ml.md`

### Regras de Trading Explícitas

- **REGRA [p.71-72]**: Apply the CUSUM filter to price series before applying triple-barrier labeling. Sampling at every tick creates serially correlated, non-IID labels. The CUSUM filter triggers observations only when cumulative price change exceeds $\pm h$, dramatically reducing label overlap.

- **REGRA [p.78-80]**: Use the triple-barrier method with dynamically computed barriers (ATR-based or volatility-based), not fixed-price barriers. This ensures the barrier width adapts to the market regime and is not dominated by the vertical barrier.

- **REGRA [p.84-89]**: Separate the side prediction task from the sizing task using meta-labeling. Build a primary model for direction (recall-optimized), then a secondary model to learn when to trust it (precision-optimized). Do not conflate the two tasks.

- **REGRA [p.98-99, p.103-106]**: Weight training samples by $\tilde{u}_i \cdot d_i$ where $\tilde{u}_i$ is average uniqueness and $d_i$ is a time-decay weight. Never train a financial ML model on equal-weighted overlapping labels — this artificially inflates effective sample size.

- **REGRA [p.121-125]**: Apply FFD with the minimum $d^*$ that passes the ADF stationarity test. For E-mini S&P 500, this is approximately $d^* \approx 0.35$ [p.126-127], retaining 99.5% correlation with the original price series. Do not blindly apply $d=1$ (first difference) which destroys memory.

- **REGRA [p.149-154]**: Always use Purged K-Fold CV with embargo for financial ML. Embargo of $h \approx 0.01T$ prevents performance inflation from serial correlation not covered by purging alone.

- **REGRA [p.160-167]**: Use all three feature importance methods (MDI, MDA, SFI) and report only features ranked important by at least two methods. MDI is biased toward high-cardinality features; SFI ignores substitution effects. Their overlap is the reliable signal.

- **REGRA [p.167]**: Use weighted Kendall's $\tau$ to assess concordance between MDI feature importance rankings and their associated PCA eigenvalue rankings (not MDI vs MDA). The book's E-mini example gives $\tau = 0.8133$ between MDI importances and inverse PCA rankings [p.167]. A high $\tau$ confirms that PCA-identified features and ML-identified features agree on relative importance.

- **REGRA [p.192-196]**: Use bet sizing (continuous position in $(-1,1)$) rather than binary signals. Discretize to $\{-1, -0.5, 0, +0.5, +1\}$ if necessary for execution, but avoid all-or-nothing signals that maximize turnover.

- **REGRA [p.208-211]**: Estimate PBO via CSCV before finalizing any strategy. A PBO > 0.5 means the strategy is more likely overfit than valid. Do not deploy until PBO is demonstrably below 0.5.

- **REGRA [p.219-222]**: Use CPCV (not simple walk-forward) to generate a full distribution of $\phi[N,k]$ backtest paths. Report the distribution of Sharpe ratios, not just the mean. Strategies with high variance across paths have uncertain real-world performance.

- **REGRA [p.276]**: Before declaring a strategy live-tradeable, verify it passes the DSR threshold. A single Sharpe ratio, however large, is uninformative without correction for the number of configurations tested.

- **REGRA [p.302-308]**: For portfolio construction, prefer HRP over Markowitz/CLA. HRP's Monte Carlo result shows $\sigma^2_{\text{HRP}} = 0.0671$ vs $\sigma^2_{\text{CLA}} = 0.1157$ vs $\sigma^2_{\text{IVP}} = 0.0928$ out-of-sample [p.313].

- **REGRA [p.383-384]**: Monitor VPIN as an intraday risk indicator. VPIN spiked anomalously before the 2010 Flash Crash, providing early warning. Treat a VPIN CDF > 0.99 as a signal to reduce exposure or widen spreads [p.448-449].

### Fórmulas / Equações

**Tick imbalance bar (TIB) threshold** [p.59-62]

The bar is formed when the cumulative signed tick imbalance exceeds:

$$|\theta_T| \geq E_0[T] \cdot |2 E_0[b_t] - 1|$$

where $\theta_T = \sum_{t=1}^{T} b_t$, $b_t \in \{-1, +1\}$ is the tick rule sign, $E_0[T]$ is the expected bar length, and $E_0[b_t]$ is the expected fraction of buys.

---

**Fractional differencing weights** [p.116-118]

$$\tilde{x}_t = \sum_{k=0}^{\infty} \omega_k x_{t-k}, \quad \omega_k = \frac{\prod_{i=0}^{k-1}(d-i)}{k!}$$

For $d=1$ this is standard differencing; for $d=0$ the series is unchanged.

---

**FFD weight recurrence** [p.121-123]

$$\omega_k = -\omega_{k-1} \cdot \frac{d - k + 1}{k}$$

Truncated when $|\omega_k| < \varepsilon$ (threshold, e.g., $10^{-5}$).

---

**Average uniqueness of label $i$** [p.98-99]

$$\bar{u}_i = \frac{1}{t_{i,1} - t_{i,0}} \sum_{t=t_{i,0}}^{t_{i,1}} \frac{1}{c_t}$$

where $c_t$ is the number of concurrent labels active at time $t$.

---

**Bagging variance reduction** [p.135-136]

For a base estimator with variance $\sigma^2$ and pairwise correlation $\rho$ among $N$ learners:

$$\sigma^2_{\text{bag}} = \rho \sigma^2 + \frac{1-\rho}{N} \sigma^2$$

As $N \to \infty$, $\sigma^2_{\text{bag}} \to \rho \sigma^2$. Reducing $\rho$ (diversity) is more powerful than adding learners.

---

**Bet sizing from predicted probability** [p.192]

The Sharpe ratio of the opportunity is estimated as $z$, and the bet size $m$ is derived as:

$$z = \frac{p - 0.5}{\sigma_p}, \quad m = 2Z[z] - 1$$

where $p$ is the predicted probability, $\sigma_p$ is the cross-sectional standard deviation of predicted probabilities, $Z[\cdot]$ is the CDF of the standard Gaussian, and $m \in [-1, 1]$. The quantity $z$ is the estimated Sharpe ratio of the opportunity; $m = 2Z[z] - 1$ maps it to a signed bet size [p.192].

---

**Number of CPCV train/test splits and backtest paths** [p.219-220]

Number of train/test splits (combinations):

$$\binom{N}{k}$$

Number of distinct backtest paths:

$$\phi[N, k] = \binom{N}{k} \cdot \frac{k}{N}$$

where $N$ is the number of groups and $k$ is the number of test groups per combination. Example: $N=6, k=2$ yields $\binom{6}{2} = 15$ splits and $\phi[6,2] = 5$ backtest paths [p.219-220]. Each group belongs to the same number of testing sets (5 for this example), so the tested groups are uniformly distributed across all $N$ groups.

---

**Expected maximum Sharpe ratio under $N$ trials** [p.222-223]

$$E[\hat{SR}_{\max}] \approx (1 - \gamma) Z^{-1}\!\left[1 - \frac{1}{N}\right] + \gamma Z^{-1}\!\left[1 - \frac{1}{N e}\right]$$

where $\gamma \approx 0.5772$ is the Euler-Mascheroni constant and $Z^{-1}$ is the inverse of the standard normal CDF.

---

**Sharpe ratio (annualized)** [p.273]

$$\hat{SR} = \frac{\hat{\mu} - r_f}{\hat{\sigma}}$$

where $\hat{\mu}$ is mean periodic return, $r_f$ is risk-free rate, $\hat{\sigma}$ is standard deviation of periodic returns.

---

**Probabilistic Sharpe Ratio (PSR)** [p.273-274]

$$PSR[\widehat{SR}^*] = Z\!\left[\frac{(\hat{SR} - \widehat{SR}^*)\sqrt{T-1}}{\sqrt{1 - \hat{\gamma}_3 \hat{SR} + \frac{\hat{\gamma}_4 - 1}{4}\hat{SR}^2}}\right]$$

where $\hat{\gamma}_3$ is skewness and $\hat{\gamma}_4$ is kurtosis of the return series, $T$ is the track record length, and $\widehat{SR}^*$ is the benchmark Sharpe ratio.

---

**Deflated Sharpe Ratio (DSR)** [p.275]

$$DSR[\widehat{SR}^*] = PSR\!\left[\widehat{SR}^* = E[\widehat{SR}_{\max}]\right]$$

where $E[\widehat{SR}_{\max}]$ is the expected maximum Sharpe ratio under the number of trials performed.

---

**Strategy failure probability (symmetric payoff)** [p.285-286]

$$\theta[p, n] = \frac{(2p-1)\sqrt{n}}{2\sqrt{p(1-p)}}$$

where $p$ is the win probability and $n$ is the number of bets. This is the Sharpe ratio for a symmetric binary-payout strategy.

---

**HRP: distance metric from correlation matrix** [p.302-304]

$$d_{i,j} = \sqrt{\frac{1}{2}(1 - \rho_{i,j})}$$

Satisfies the triangle inequality; used as input to single-linkage hierarchical clustering.

---

**HRP: recursive bisection allocation** [p.307-308]

For cluster $C$ split into sub-clusters $C_1$ and $C_2$:

$$\alpha_1 = 1 - \frac{\tilde{V}_1}{\tilde{V}_1 + \tilde{V}_2}, \quad \alpha_2 = 1 - \alpha_1$$

where $\tilde{V}_j = w_j^T \Sigma_j w_j$ is the variance of the naïve (IVP) allocation within sub-cluster $j$.

---

**Roll spread estimator** [p.372-373]

$$c = \sqrt{-\text{Cov}(\Delta p_t, \Delta p_{t-1})}$$

where $\Delta p_t$ is the tick-to-tick price change and $c$ is the effective half-spread.

---

**Kyle's lambda** [p.377-378]

$$\Delta p_t = \lambda \sum_i b_i v_i + \varepsilon_t$$

where $b_i \in \{-1, +1\}$ is the trade sign, $v_i$ is the trade volume, and $\lambda$ is estimated by OLS.

---

**Amihud's lambda** [p.379-380]

$$\lambda_{\text{Amihud}} = E\!\left[\frac{|r_t|}{V_t}\right]$$

where $r_t$ is the daily log-return and $V_t$ is daily dollar volume.

---

**Shannon entropy (plug-in estimator)** [p.349-351]

$$H[X] = -\sum_{x \in \mathcal{X}} p(x) \log_2 p(x)$$

Estimated by replacing $p(x)$ with observed frequencies.

---

**SADF test statistic** [p.336-340]

$$SADF(t_0) = \sup_{t_1 \in [t_0, t_0 + \delta]} ADF_{t_0, t_1}$$

where $ADF_{t_0, t_1}$ is the ADF statistic on the sub-period $[t_0, t_1]$. Computational complexity is $O(T^3)$ for the full SADF series [p.338-339].

---

**CUSUM filter (event-based sampling, Ch.2)** [p.71-72]

The symmetric CUSUM filter accumulates deviations from a running expected value. A bar is sampled whenever $S_t \geq h$, at which point $S_t$ is reset to zero:

$$S_t = \max(0,\; S_{t-1} + y_t - E_{t-1}[y_t])$$

with the symmetric extension triggering on run-ups or run-downs. The only user-set parameter is the threshold $h$ (the filter size). No parameter $k$ appears in the Ch.2 CUSUM filter [p.71-72]. (Note: a separate `k` parameter appears in the Ch.17 Brown-Durbin-Evans CUSUM structural break test [p.333-334], where it denotes the number of regression features — a different context entirely.)

### Algoritmos e Pseudocódigo

**Triple-barrier labeling** [p.78-80, ch.3]

```
Input: price series p, profit_taker multiplier pt, stop_loss multiplier sl,
       max_holding_period t1, volatility estimate sigma

For each event (t0, side):
    upper_barrier = p[t0] * (1 + pt * sigma)
    lower_barrier = p[t0] * (1 - sl * sigma)
    expiry         = t0 + t1

    t_touch = argmin{t > t0 : p[t] >= upper_barrier
                            or p[t] <= lower_barrier
                            or t >= expiry}

    if   p[t_touch] >= upper_barrier: label = +1
    elif p[t_touch] <= lower_barrier: label = -1
    else:                              label =  0  # expiry
```

---

**Meta-labeling pipeline** [p.84-89, ch.3]

```
Step 1 (primary model):
    Train model M1 on features F to predict SIDE in {-1, +1}
    Threshold by F1 maximization on validation set

Step 2 (meta-labeling):
    Let S = predicted side from M1 (keep only non-zero predictions)
    Binary target: y_meta = 1 if M1 was correct, 0 otherwise
    Train binary classifier M2 on (F union {S}) -> y_meta
    Output: probability p_meta from M2

Step 3 (sizing):
    bet_size = p_meta * side  # size in (-1, +1)
```

---

**Sequential bootstrap** [p.101-106, ch.4]

```
Input: indicator matrix Phi (T x N), where Phi[t,i]=1 if label i active at t

Initialize: drawn = []

While len(drawn) < N_bootstrap:
    for each label i not yet in drawn:
        c_t = count of already-drawn labels active at each t in label_i's range
        u_i = mean(1 / (c_t + 1)) over t in label_i's range
    weights = u_i / sum(u_i)
    draw next sample proportionally to weights
    append to drawn

Return: drawn
```

---

**FFD implementation** [p.124-125, ch.5]

```python
def getWeights_FFD(d, thres):
    w, k = [1.], 1
    while True:
        w_ = -w[-1]/k*(d-k+1)
        if abs(w_) < thres: break
        w.append(w_)
        k += 1
    w = np.array(w[::-1]).reshape(-1,1)
    return w

def fracDiff_FFD(series, d, thres=1e-5):
    w = getWeights_FFD(d, thres)
    width = len(w)-1
    df = {}
    for name in series.columns:
        seriesF = series[[name]].fillna(method='ffill').dropna()
        df_ = pd.Series()
        for iloc1 in range(width, seriesF.shape[0]):
            loc0, loc1 = seriesF.index[iloc1-width], seriesF.index[iloc1]
            if not np.isfinite(series.loc[loc1,name]): continue
            df_[loc1] = np.dot(w.T, seriesF.loc[loc0:loc1])[0,0]
        df[name] = df_.copy(deep=True)
    df = pd.concat(df, axis=1)
    return df
```

---

**Purged K-Fold cross-validation** [p.149-154, ch.7]

```
Input: dataset with (t0, t1) label pairs, K folds, embargo_pct h

Partition observations into K groups by t0 (chronological)

for k in 1..K:
    test_set    = group k
    test_range  = [min(t0 in k), max(t1 in k)]
    purge_end   = test_range.end + h * total_span
    train_set   = {i : t1_i < test_range.start
                      or t0_i > purge_end}
    model       = fit(train_set)
    score_k     = evaluate(model, test_set)

return mean(scores), std(scores)
```

---

**CPCV backtest paths** [p.219-222, ch.12]

```
Input: dataset split into N groups, choose k groups as test per combination

paths = []
for each C in combinations(N_groups, k):
    test_data  = concatenate groups in C
    train_data = all groups not in C, purged and embargoed
    model      = fit(train_data)
    pnl        = evaluate(model, test_data)
    paths.append(pnl)

# C(N,k) total splits; phi[N,k] = C(N,k) * k/N distinct backtest paths
# Example: N=6, k=2 -> C(6,2)=15 splits, phi[6,2]=5 paths
report: distribution(paths), Sharpe(paths), PBO estimate
```

---

**HRP algorithm** [p.302-308, ch.16]

```
Input: T x N return matrix R

Step 1 — Clustering:
    corr = R.corr()
    dist[i,j] = sqrt(0.5 * (1 - corr[i,j]))
    linkage = single_linkage_clustering(dist)
    sort_idx = quasi_diagonalize(linkage)

Step 2 — Quasi-diagonalization:
    Reorder corr and cov by sort_idx so similar assets are adjacent

Step 3 — Recursive bisection:
    weights = {i: 1.0 for i in all assets}
    cluster_list = [sorted_asset_list]
    while cluster_list not empty:
        C = cluster_list.pop()
        split C into left half C1 and right half C2
        var1 = IVP_variance(C1)   # inverse variance portfolio
        var2 = IVP_variance(C2)
        alpha1 = 1 - var1 / (var1 + var2)
        for i in C1: weights[i] *= alpha1
        for i in C2: weights[i] *= (1 - alpha1)
        if len(C1) > 1: cluster_list.append(C1)
        if len(C2) > 1: cluster_list.append(C2)

Return: weights  # sum to 1, no matrix inversion required
```

---

**mpPandasObj multiprocessing engine** [p.404-405, ch.20]

```python
def mpPandasObj(func, pdObj, numThreads=24, mpBatches=1, linMols=True, **kargs):
    """Parallelize jobs, return a DataFrame or Series"""
    if linMols:
        parts = linParts(len(pdObj[1]), numThreads * mpBatches)
    else:
        parts = nestedParts(len(pdObj[1]), numThreads * mpBatches)
    jobs = []
    for i in range(1, len(parts)):
        job = {pdObj[0]: pdObj[1][parts[i-1]:parts[i]], 'func': func}
        job.update(kargs)
        jobs.append(job)
    if numThreads == 1:
        out = processJobs_(jobs)
    else:
        out = processJobs(jobs, numThreads=numThreads)
    if isinstance(out[0], pd.DataFrame):   df0 = pd.DataFrame()
    elif isinstance(out[0], pd.Series):    df0 = pd.Series()
    else: return out
    for i in out: df0 = df0.append(i)
    return df0.sort_index()
```

---

**O-U process calibration for synthetic backtesting** [p.229-232, ch.13]

```
Input: price series p (log-prices)

Step 1: Fit O-U model
    dp_t = theta*(mu - p_{t-1})*dt + sigma*dW_t
    Estimate theta, mu, sigma via OLS on: p_t = a + b*p_{t-1} + epsilon
    theta = -log(b)/dt
    mu    = a / (1 - b)
    sigma_ou = std(epsilon) / sqrt((1 - b^2) / (2*theta))

Step 2: Generate synthetic price paths
    Simulate N paths of length T using calibrated (theta, mu, sigma_ou)

Step 3: Apply trading rule on each path, compute SR per path

Step 4: Report SR distribution; test if real SR is in top tail
```

### Pitfalls e Anti-patterns

- **[p.29, p.39-40]** The Sisyphus paradigm — solo researcher who loops backtest until satisfied — is the root cause of most quantitative failure. It is structurally equivalent to p-hacking. The fix is a team-based pipeline with audited steps.

- **[p.148-149]** Standard K-fold CV on financial data inflates performance because: (1) training and test sets overlap in time; (2) labels for correlated periods leak across folds. López de Prado describes the inflation mechanism qualitatively; no numerical Sharpe-inflation multiplier is given in the source.

- **[p.76-77]** Fixed-time horizon labeling (e.g., "return over next 20 days") fails to account for path-dependency. A trade that hits a stop-loss on day 5 but recovers to positive by day 20 is mislabeled as successful.

- **[p.39-40]** Table 1.2 lists 10 common pitfalls in Financial ML: (1) The Sisyphus paradigm [epistemological]; (2) Research through backtesting [epistemological]; (3) Chronological sampling [data processing]; (4) Integer differentiation [data processing]; (5) Fixed-time horizon labeling [classification]; (6) Learning side and size simultaneously [classification]; (7) Weighting of non-IID samples [classification]; (8) Cross-validation leakage [evaluation]; (9) Walk-forward (historical) backtesting [evaluation]; (10) Backtest overfitting [evaluation].

- **[p.134-140]** Random forests are vulnerable to spurious feature importance when features are correlated. MDI and MDA give different rankings for correlated features; SFI resolves ambiguity by training on each feature independently.

- **[p.204-207]** The seven deadly sins of quantitative investing (Luo et al. [2014], cited and discussed by López de Prado): (1) Survivorship bias; (2) Look-ahead bias; (3) Storytelling; (4) Data mining and data snooping; (5) Transaction costs; (6) Outliers; (7) Shorting — taking a short position on cash products requires finding a lender, and the cost of lending and the amount available is generally unknown [p.204]. The CSCV/PBO framework specifically quantifies the data mining sin.

- **[p.217-218]** Walk-forward backtesting with a single train-test split produces a single Sharpe ratio that has high variance and is insufficient for inferring future performance. The correct approach is CPCV to obtain a distribution.

- **[p.298-299]** Markowitz's curse: with $N$ assets, the number of parameters in $\Sigma$ grows as $O(N^2)$ while sample size typically grows as $O(N)$, making the estimated inverse highly unstable. Adding more assets makes the problem worse, not better.

- **[p.338-339]** SADF's computational complexity is $O(T^3)$. Running it naively on tick data is impractical. Use the recursive formulation and parallelize using atoms/molecules pattern from Ch.20.

- **[p.388-389]** Using price-level data directly as ML features produces non-stationary inputs whose correlations are spurious. Use FFD with minimum $d^*$ to preserve memory while achieving stationarity.

- **[p.29]** Researchers who add complexity to survive the backtest (adding parameters, changing lookback windows, switching instruments) are unknowingly inflating the multiple-testing bias. Every additional configuration tested increases the effective null hypothesis count.

- **[p.144]** Boosting is more prone to overfitting in finance than bagging because it explicitly targets the residuals of prior models; in a noisy financial environment, it will target noise. Prefer bagging (random forests) over gradient boosting for financial ML unless the dataset is large and low-noise.

---

## From `books/testing_tuning.md`

### Regras de Trading Explícitas

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

### Fórmulas / Equações

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

### Algoritmos e Pseudocódigo

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

### Pitfalls e Anti-patterns

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

## From `books/stat_sound_indicators.md`

### Regras de Trading Explícitas

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

### Fórmulas / Equações

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

### Algoritmos e Pseudocódigo

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

### Pitfalls e Anti-patterns

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

---

## From `books/evidence_based_ta.md`

### Regras de Trading Explícitas

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

### Fórmulas / Equações

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

### Algoritmos e Pseudocódigo

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

### Pitfalls e Anti-patterns

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

---

## Companion C++ Code (reference implementations)

These are reference C++ implementations from Timothy Masters' companion code.
Use as authoritative pseudocode when porting to Python in Phases 4/5.

- [`books/code/masters-testing-tuning/MCPT_BARS/MCPT_BARS.CPP`](../../books/code/masters-testing-tuning/MCPT_BARS/MCPT_BARS.CPP)
- [`books/code/masters-testing-tuning/MCPT_TRN/MCPT_TRN.CPP`](../../books/code/masters-testing-tuning/MCPT_TRN/MCPT_TRN.CPP)
- [`books/code/masters-assessing/BOOT_P_1.CPP`](../../books/code/masters-assessing/BOOT_P_1.CPP)
- [`books/code/masters-assessing/BOOT_P_2.CPP`](../../books/code/masters-assessing/BOOT_P_2.CPP)
