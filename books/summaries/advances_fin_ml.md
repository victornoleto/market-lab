# Advances in Financial Machine Learning

## Metadata
- **Author:** Marcos López de Prado [p.i]
- **Year:** 2018
- **Publisher:** John Wiley & Sons
- **Pages:** 489
- **ISBN:** 978-1-119-48208-6
- **Main focus:** A rigorous ML methodology for financial research — from data structures and feature engineering through model selection, backtesting, and high-performance implementation — designed to replace the ad-hoc Sisyphus paradigm with a robust, team-based production pipeline.

## 1. Core Thesis
The book argues that the overwhelming majority of quantitative failures stem not from bad ideas but from a flawed research paradigm: individual analysts who code → backtest → iterate until Sharpe looks good. López de Prado calls this the **Sisyphus paradigm** and shows it structurally guarantees overfitting [p.29]. The alternative is a **meta-strategy paradigm** — a division-of-labor production pipeline in which data curators, feature analysts, strategists, backtesters, deployment engineers, and portfolio oversight each perform specialized, verifiable work, making the process auditable and reproducible [p.30, p.32-35].

The unifying technical claim is that financial ML requires domain-adapted methodology at every step: standard bar construction produces data with unwanted statistical properties; standard cross-validation is invalid on serially correlated labels; standard Sharpe-based selection is biased by multiple testing; standard portfolio optimization is ill-conditioned. Each chapter introduces a principled, often novel solution. The three Laws of Backtesting summarize the epistemological core: Law 1 (Snippet 8.1, [p.159]) — "Backtesting is not a research tool. Feature importance is."; Law 2 (Snippet 11.1, [p.207]) — "Backtesting while researching is like drinking and driving. Do not research under the influence of a backtest."; Law 3 (Snippet 14.5, [p.276]) — "Every backtest result must be reported in conjunction with all the trials involved in its production. Absent that information, it is impossible to assess the backtest's 'false discovery' probability."

## 2. Main Concepts
- **Sisyphus paradigm** — solo analyst who codes, backtests, and iterates until results look acceptable; structurally guarantees overfitting [p.29]
- **Meta-strategy paradigm** — team-based production chain with specialized roles; separates research from validation [p.29-30]
- **Financial data types** — fundamental (economic data), market (prices/volumes), analytics (estimates), alternative (non-standard sources); each with distinct stale-data and look-ahead risks [p.52]
- **Dollar bars** — observations formed when a fixed dollar amount $x$ changes hands; normalizes for changing trading intensity better than time or tick bars [p.57-59]
- **Tick-imbalance bars (TIBs)** — bars formed when signed tick imbalance exceeds a threshold $E_0[T]$; generate a new bar at the moment informed trading is detected [p.59-62]
- **Volume-run bars (VRBs)** — bars formed when buy or sell volume in a single direction exceeds an expected threshold; most sensitive to directional institutional flow [p.62-63]
- **ETF trick** — technique to stitch together futures roll series into a continuous series using price ratios of spot and front contracts; preserves PnL computability [p.64-66]
- **CUSUM filter** — event-based sampling method that triggers observation only when cumulative log-return deviates by $\pm h$ from running high/low; prevents triple-barrier labeling from being swamped by noise [p.71-72]
- **Triple-barrier method** — labeling scheme with upper profit-taking barrier, lower stop-loss barrier, and vertical time expiration; label is the first barrier touched [p.78-80]
- **Meta-labeling** — secondary binary classifier placed on top of a primary side-prediction model; learns when the primary model is correct and scales bet size accordingly [p.84-89]
- **Average uniqueness** — fraction of label $i$'s interval that is not overlapped by other labels; quantifies degree of non-IID-ness for sample weighting [p.98-99]
- **Sequential bootstrap** — bootstrap procedure that draws samples with probability inversely proportional to the average uniqueness of the already-drawn set; produces near-IID training samples from overlapping labels [p.101-106]
- **Fractional differentiation (fracdiff / FFD)** — applies a fractional-order differencing operator $d \in (0,1)$ instead of integer differencing; achieves stationarity while retaining maximum historical memory [p.116-121]
- **Fixed-width window fractional differentiation (FFD)** — truncated version of fracdiff that drops weights below threshold $\varepsilon$; yields a stationary and memory-preserving series suitable for ML [p.121-125]
- **Purged K-Fold CV** — cross-validation that removes training observations whose outcomes overlap with the test period; prevents look-ahead leakage [p.149-151]
- **Embargo** — additional buffer of $h \approx 0.01T$ observations removed after the purged boundary to absorb serial correlation not captured by purging [p.152]
- **Mean Decrease Impurity (MDI)** — in-bag feature importance measure based on weighted average impurity reduction across all splits; fast but biased toward high-cardinality features [p.160-161]
- **Mean Decrease Accuracy (MDA)** — out-of-bag feature importance measured by performance drop after column permutation; unbiased but slower [p.161-162]
- **Single Feature Importance (SFI)** — OOS importance measured by training a separate model on each feature individually; most conservative, avoids substitution effects [p.163-164]
- **Bet sizing** — mapping predicted probability $p$ to a position size in $[-1, 1]$ via a monotone transformation; avoids binary all-in/all-out signals [p.192-193]
- **CSCV (Combinatorial Symmetric Cross-Validation)** — method to estimate the Probability of Backtest Overfitting (PBO) by generating all possible 50/50 train-test splits of the backtest period [p.208-211]
- **CPCV (Combinatorial Purged Cross-Validation)** — generalization of purged K-fold that forms $\phi[N,k]$ distinct backtest paths by choosing all possible combinations of $k$ test groups from $N$ total splits [p.219-222]
- **Probabilistic Sharpe Ratio (PSR)** — Sharpe ratio adjusted for estimation uncertainty, non-normality of returns, and length of track record [p.273-274]
- **Deflated Sharpe Ratio (DSR)** — PSR further adjusted for the number of trials (strategy configurations) tested; answers "is this SR significant given how many strategies I tried?" [p.275]
- **Hierarchical Risk Parity (HRP)** — portfolio construction method using hierarchical clustering and recursive bisection; does not require matrix inversion and outperforms Markowitz under estimation error [p.302-308]
- **Structural break tests (SADF)** — Supremum Augmented Dickey-Fuller test for detecting explosive price behavior (bubbles) by running a sequence of backward-expanding ADF tests [p.336-340]
- **Shannon entropy** — information-theoretic measure of market efficiency; lower entropy signals exploitable predictability [p.349-351]
- **Lempel-Ziv entropy estimator** — non-parametric estimator of the entropy rate of a binary/quantile-encoded price series; preferred over plug-in when distribution is unknown [p.352-357]
- **VPIN (Volume-synchronized Probability of Informed Trading)** — measure of order flow toxicity computed using volume bars; shown to spike before the 2010 Flash Crash [p.364-365, p.383-384]
- **Kyle's lambda** — price impact coefficient from regression of price change on signed order flow; measures per-unit cost of informed trading [p.377-378]
- **Markowitz's curse** — instability of optimized portfolio weights under estimation error; condition number of the covariance matrix grows rapidly with $N$ [p.298-299]
- **Atoms and molecules** — decomposition of parallel jobs: atoms are indivisible tasks; molecules are subsets of atoms assigned to a single CPU core [p.399]
- **Quantum annealing for portfolio optimization** — discretizing the dynamic trading trajectory problem into a combinatorial integer program soluble by a quantum annealer [p.420-421]

## 3. Formulas / Equations
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

## 4. Algorithms and Pseudocode
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

## 5. Explicit Trading Rules
- **RULE [p.71-72]**: Apply the CUSUM filter to price series before applying triple-barrier labeling. Sampling at every tick creates serially correlated, non-IID labels. The CUSUM filter triggers observations only when cumulative price change exceeds $\pm h$, dramatically reducing label overlap.

- **RULE [p.78-80]**: Use the triple-barrier method with dynamically computed barriers (ATR-based or volatility-based), not fixed-price barriers. This ensures the barrier width adapts to the market regime and is not dominated by the vertical barrier.

- **RULE [p.84-89]**: Separate the side prediction task from the sizing task using meta-labeling. Build a primary model for direction (recall-optimized), then a secondary model to learn when to trust it (precision-optimized). Do not conflate the two tasks.

- **RULE [p.98-99, p.103-106]**: Weight training samples by $\tilde{u}_i \cdot d_i$ where $\tilde{u}_i$ is average uniqueness and $d_i$ is a time-decay weight. Never train a financial ML model on equal-weighted overlapping labels — this artificially inflates effective sample size.

- **RULE [p.121-125]**: Apply FFD with the minimum $d^*$ that passes the ADF stationarity test. For E-mini S&P 500, this is approximately $d^* \approx 0.35$ [p.126-127], retaining 99.5% correlation with the original price series. Do not blindly apply $d=1$ (first difference) which destroys memory.

- **RULE [p.149-154]**: Always use Purged K-Fold CV with embargo for financial ML. Embargo of $h \approx 0.01T$ prevents performance inflation from serial correlation not covered by purging alone.

- **RULE [p.160-167]**: Use all three feature importance methods (MDI, MDA, SFI) and report only features ranked important by at least two methods. MDI is biased toward high-cardinality features; SFI ignores substitution effects. Their overlap is the reliable signal.

- **RULE [p.167]**: Use weighted Kendall's $\tau$ to assess concordance between MDI feature importance rankings and their associated PCA eigenvalue rankings (not MDI vs MDA). The book's E-mini example gives $\tau = 0.8133$ between MDI importances and inverse PCA rankings [p.167]. A high $\tau$ confirms that PCA-identified features and ML-identified features agree on relative importance.

- **RULE [p.192-196]**: Use bet sizing (continuous position in $(-1,1)$) rather than binary signals. Discretize to $\{-1, -0.5, 0, +0.5, +1\}$ if necessary for execution, but avoid all-or-nothing signals that maximize turnover.

- **RULE [p.208-211]**: Estimate PBO via CSCV before finalizing any strategy. A PBO > 0.5 means the strategy is more likely overfit than valid. Do not deploy until PBO is demonstrably below 0.5.

- **RULE [p.219-222]**: Use CPCV (not simple walk-forward) to generate a full distribution of $\phi[N,k]$ backtest paths. Report the distribution of Sharpe ratios, not just the mean. Strategies with high variance across paths have uncertain real-world performance.

- **RULE [p.276]**: Before declaring a strategy live-tradeable, verify it passes the DSR threshold. A single Sharpe ratio, however large, is uninformative without correction for the number of configurations tested.

- **RULE [p.302-308]**: For portfolio construction, prefer HRP over Markowitz/CLA. HRP's Monte Carlo result shows $\sigma^2_{\text{HRP}} = 0.0671$ vs $\sigma^2_{\text{CLA}} = 0.1157$ vs $\sigma^2_{\text{IVP}} = 0.0928$ out-of-sample [p.313].

- **RULE [p.383-384]**: Monitor VPIN as an intraday risk indicator. VPIN spiked anomalously before the 2010 Flash Crash, providing early warning. Treat a VPIN CDF > 0.99 as a signal to reduce exposure or widen spreads [p.448-449].

## 6. Pitfalls and Anti-patterns
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

## 7. Sensitive Parameters
- **CUSUM threshold $h$** [p.71-72]: Author recommends setting $h$ equal to the daily volatility estimate (rolling standard deviation). This makes the filter volatility-adaptive and ensures approximately constant sampling rate across regimes. Not curve-fit — grounded in units of returns.

- **Triple-barrier barrier multipliers** [p.78-80]: Author uses equal-width barriers (1:1 profit-taking to stop-loss) as the default, with multipliers of 1×-2× the volatility estimate. Asymmetric ratios require separate economic justification.

- **Embargo fraction $h$** [p.152]: Author recommends $h \approx 0.01T$ where $T$ is the span of the training set. Rule of thumb, not optimized. Rationale: typical serial correlation in financial features decays within 1% of the sample span.

- **Fractional differentiation order $d^*$** [p.126-127]: Selected as the minimum $d$ that passes the ADF stationarity test at 95% confidence. For E-mini S&P 500, $d^* \approx 0.35$. For 87 liquid futures, all achieved stationarity with $d < 0.6$ [p.128]. Data-driven but economically grounded (preserve maximum memory).

- **FFD truncation threshold $\varepsilon$** [p.121-123]: Author uses $\varepsilon = 10^{-5}$. Controls the width of the fixed window. Increasing $\varepsilon$ increases stationarity but loses more memory. Precision parameter, not a tuning parameter.

- **Random forest number of trees** [p.139-141]: Author recommends starting large (hundreds) and stopping when OOB error stabilizes. Not tuned — increasing $N_\text{trees}$ never hurts, only adds computational cost.

- **HRP clustering linkage** [p.302-304]: Author uses single-linkage. Justification: single-linkage produces compact clusters that minimize within-cluster variance. Monte Carlo experiment did not compare other linkage methods.

- **VPIN parameters** [p.448-449]: LBNL calibration across 100 futures contracts (reducing false positive rate from 20% to 7%): median pricing, 200 buckets/day, 30 bars/bucket, support window = 1 day, event duration = 0.1 day, Student-$t$ bulk volume classification ($\nu = 0.1$), threshold CDF = 0.99. Population-level parameters, not per-instrument fits.

- **Number of CPCV splits $N$ and $k$** [p.219-220]: Author does not specify a universal rule. More splits produce more paths but reduce training set size. Example from book: $N=6, k=2$ produces $\binom{6}{2} = 15$ train/test splits and $\phi[6,2] = 5$ backtest paths — not 15 paths. The 15 is the number of splits; the 5 is the number of paths (each group belongs to 5 testing sets).

- **PSR benchmark $\widehat{SR}^*$** [p.273-274]: Author recommends setting $\widehat{SR}^* = 0$ (test against noise) or $\widehat{SR}^* = SR_{\text{benchmark}}$ (test against passive strategy). Must be declared before looking at results.

## 8. Key Literal Quotes
> "Backtesting is not a research tool. Feature importance is." — Marcos López de Prado, Snippet 8.1 (Marcos' First Law of Backtesting) [p.159]

> "Backtesting while researching is like drinking and driving. Do not research under the influence of a backtest." — Marcos López de Prado, Snippet 11.1 (Marcos' Second Law of Backtesting) [p.207]

> "Every backtest result must be reported in conjunction with all the trials involved in its production. Absent that information, it is impossible to assess the backtest's 'false discovery' probability." — Marcos López de Prado, Snippet 14.5 (Marcos' Third Law of Backtesting) [p.276]

> "In contrast, a backtest is not a research tool. It provides us with very little insight into the reason why a particular strategy would have made money." — [p.205]

> "The purpose of a backtest is to discard bad models, not to improve them. Adjusting your model based on the backtest results is a waste of time ... and it's dangerous." — [p.206]

## 9. Cross-references to Other Books in This Knowledge Base
- The **Kelly criterion and fractional Kelly sizing** discussed in `math_money_mgmt.md` connects to López de Prado's bet-sizing via predicted probability in ch.10 [p.192-196] — both derive position size from an edge estimate, but AFML conditions edge on ML probability rather than historical win rate.

- **Feature importance and overfitting diagnostics** connect to `ml_for_algo_trading.md` — that book applies MDI/MDA in practice; AFML provides the theoretical derivation of why MDI is biased and when SFI is preferred [p.160-164].

- The **HRP portfolio construction** in ch.16 [p.298-313] can be compared to `risk_parity.md` — AFML derives HRP from first principles of hierarchical clustering; the risk parity book focuses on equal risk contribution without the ML framing.

- **Structural breaks and regime detection** in ch.17 (SADF) [p.336-340] connects to `regime_change.md` — AFML provides the statistical test for explosive behavior; the regime change book provides the broader framework for acting on regime signals in a portfolio.

- **VPIN as microstructure early-warning** in ch.18-19 [p.364-365, p.383-384] connects to `trading_exchanges.md` — that book provides the market microstructure theory underlying order flow toxicity; AFML provides the operational formula and empirical calibration.
