# Advances in Financial Machine Learning

## Metadata
- **Autor:** Marcos López de Prado [p.7]
- **Ano:** 2018 [p.8]
- **Editora:** John Wiley & Sons, Inc., Hoboken, New Jersey [p.8]
- **Páginas:** 489 (PDF)
- **ISBN:** 978-1-119-48208-6 (Hardcover); 978-1-119-48211-6 (ePDF); 978-1-119-48210-9 (ePub) [p.8]
- **Foco principal:** ML aplicado a finanças como disciplina distinta, com foco em pipeline industrial: estrutura de dados, rotulagem, cross-validation robusta, backtesting e evitando overfitting.

## 1. Tese Central

Financial ML is a subject in its own right, distinct from standard ML [p.27, ch.1]. Off-the-shelf ML imported from Silicon Valley or academia applied to financial time series will fail because of non-IID observations, low signal-to-noise ratio, and rampant backtest overfitting [p.27-28]. The book argues for the **meta-strategy paradigm** — running research as a factory with specialized stations (data curators, feature analysts, strategists, backtesters, deployment, portfolio oversight) rather than having individual PhDs chase "magical formula" individual strategies (the "Sisyphus Paradigm") [p.28-35, ch.1].

A unifying theme: **"Backtesting is not a research tool. Feature importance is."** — Marcos' First Law of Backtesting [p.159, Snippet 8.1]. The book provides mathematical and computational techniques (purging, embargoing, CPCV, fractional differentiation, meta-labeling, HRP) designed to survive the realities of financial data.

## 2. Conceitos-Chave

- **Meta-Strategy Paradigm** — factory-like organization of quant research; specialization across stations yields discoveries at predictable rate [p.29-34, ch.1].
- **Information-Driven Bars (TIB, VIB, DIB, TRB, VRB, DRB)** — sample bars when tick/volume/dollar imbalances or runs exceed expectations; produce more IID-like observations than time bars [p.59-63, ch.2].
- **Dollar Bars** — sampling every time a predefined market value has been exchanged; robust to share-count changes from corporate actions [p.57-59, ch.2].
- **ETF Trick** — transforms a multi-product series (e.g., futures roll, basket of securities) into a single $1-invested non-expiring cash-product time series [p.64-66, ch.2].
- **CUSUM Filter (symmetric)** — event-based sampler that triggers when cumulative run-ups or run-downs exceed threshold h; avoids flaws of Bollinger-band-like triggers [p.71-73, ch.2].
- **Triple-Barrier Method** — labels observation by whichever of three barriers (profit-taking horizontal, stop-loss horizontal, time-expiration vertical) is touched first; path-dependent and volatility-adjusted [p.78-81, ch.3].
- **Meta-Labeling** — secondary ML model that learns the **size** of a bet given a primary model that sets the **side**; increases F1, limits overfitting to "direction" [p.84-88, ch.3].
- **Average Uniqueness** — for each label, the reciprocal of the harmonic mean of concurrent labels over its lifespan; used to down-weight redundant overlapping outcomes [p.99-100, ch.4].
- **Sequential Bootstrap** — sampling with replacement where draw probabilities decrease with overlap with prior draws; produces samples closer to IID than standard bootstrap [p.101-106, ch.4].
- **Fractional Differentiation (FFD)** — non-integer differencing that makes a series stationary while preserving maximum memory [p.116-126, ch.5].
- **Purging** — removing training observations whose labels overlap in time with the testing labels (prevents leakage) [p.150, ch.7].
- **Embargo** — removing training observations immediately after the test set to kill residual serial-correlation leakage [p.152, ch.7].
- **Purged K-Fold CV** — k-fold CV with purging+embargoing; the standard the book promotes for finance [p.150-154, ch.7].
- **MDI, MDA, SFI** — Mean Decrease Impurity (IS, tree-based), Mean Decrease Accuracy (OOS, permutation), Single Feature Importance (OOS, per-feature) [p.158-164, ch.8].
- **Combinatorial Purged Cross-Validation (CPCV)** — generates φ[N,k] backtest paths by combining k-sized testing groups drawn from N partitions; produces a distribution of Sharpe ratios instead of one [p.219-223, ch.12].
- **Probability of Backtest Overfitting (PBO)** via CSCV — combinatorially symmetric CV that estimates the probability an IS-optimal strategy underperforms OOS [p.208-210, ch.11].
- **Probabilistic Sharpe Ratio (PSR)** — probability that the true SR exceeds a user-defined threshold given observed SR, T, skew, kurtosis [p.273, ch.14].
- **Deflated Sharpe Ratio (DSR)** — PSR where the benchmark SR\* is set from the expected maximum across N trials, correcting for multiple testing / selection bias [p.274-275, ch.14].
- **Hierarchical Risk Parity (HRP)** — tree-clustering + recursive bisection portfolio construction that does not require covariance inversion; robust vs. Markowitz CLA [p.297-299, ch.16].
- **Kyle's λ, Amihud's λ, Hasbrouck's λ** — microstructure measures of price impact / illiquidity [p.351-355, ch.19].
- **VPIN** — Volume-Synchronized Probability of Informed Trading [p.358-360, ch.19].

## 3. Fórmulas / Equações

**Dollar Value of $1 invested — ETF Trick** [p.65, ch.2]

$$K_t = K_{t-1} + \sum_{i=1}^{I} h_{i,t} \cdot \delta_{i,t}$$

with $K_0 = 1$, $h_{i,t}$ = holdings of instrument $i$ and $\delta_{i,t}$ = change in market value; dividends embedded in $K_t$ to prevent negative prices [p.65].

**Fractional Differentiation — Weight Iteration** [p.117, ch.5]

$$\omega_k = -\omega_{k-1} \frac{d-k+1}{k}, \quad \omega_0 = 1$$

Apply via dot-product: $\tilde{X}_t = \sum_{k=0}^{\infty} \omega_k X_{t-k}$ [p.117]. In the FFD (fixed-width window) variant, truncate when $|\omega_k| < \tau$ (e.g., $\tau = 10^{-5}$) [p.124, Snippet 5.3].

**Purged K-Fold — Overlap Conditions** [p.150, ch.7]

Labels $Y_i = f[[t_{i,0}, t_{i,1}]]$ and $Y_j = f[[t_{j,0}, t_{j,1}]]$ overlap iff any of the three is true [p.150]:

1. $t_{j,0} \le t_{i,0} \le t_{j,1}$
2. $t_{j,0} \le t_{i,1} \le t_{j,1}$
3. $t_{i,0} \le t_{j,0} \le t_{j,1} \le t_{i,1}$

Embargo: extend test label to $Y_j = f[[t_{j,0}, t_{j,1} + h]]$ with typically $h \approx 0.01 T$ [p.152].

**CPCV — Number of Paths** [p.219, ch.12]

$$\varphi[N, k] = \frac{k}{N} \binom{N}{k}$$

Number of train/test splits: $\binom{N}{k}$. For $k=2$: $\varphi[N,2] = N-1$ paths [p.220].

**Variance of CPCV Sample Mean** [p.222, ch.12]

$$\sigma^2[\bar{y}_i] = \frac{\sigma_i^2}{\varphi} + \frac{\varphi - 1}{\varphi} \bar{\rho}\, \sigma_i^2$$

where $\bar{\rho}$ is the average off-diagonal correlation among paths. Lower $\bar{\rho}$ → lower variance → fewer false discoveries than WF/CV [p.222-223].

**Expected Maximum SR under H0 (used by DSR)** [p.222, ch.12; p.275, ch.14]

$$E[\max_n \{\hat{SR}_n\}] \approx \sqrt{V[\hat{SR}_n]} \left( (1-\gamma) Z^{-1}\!\left[1 - \frac{1}{N}\right] + \gamma\, Z^{-1}\!\left[1 - \frac{1}{N e}\right]\right)$$

with $\gamma \approx 0.5772156649$ (Euler-Mascheroni), $Z^{-1}$ inverse CDF of standard normal, $N$ number of independent trials [p.222, p.275].

**Probabilistic Sharpe Ratio (PSR)** [p.273, ch.14]

$$\widehat{PSR}(SR^*) = Z\!\left[\frac{(\hat{SR} - SR^*)\sqrt{T-1}}{\sqrt{1 - \hat{\gamma}_3 \hat{SR} + \frac{\hat{\gamma}_4 - 1}{4}\hat{SR}^2}}\right]$$

where $\hat{\gamma}_3$ = skewness, $\hat{\gamma}_4$ = kurtosis of returns; $\hat{SR}$ in original (non-annualized) frequency; $T$ = number of returns [p.273-274]. Should exceed 0.95 at 5% significance level [p.276].

**Annualized Sharpe — Symmetric Binary Strategy** [p.285, ch.15]

$$\theta[p, n] = \frac{2p - 1}{\sqrt{4 p (1-p)}} \sqrt{n}$$

$p$ = precision, $n$ = bets per year. For $p = 0.55$ you need $n = 396$ bets/year for SR = 2 [p.286].

**Annualized Sharpe — Asymmetric Payouts** [p.287, ch.15]

$$\theta[p, n, \pi_-, \pi_+] = \frac{(\pi_+ - \pi_-) p + \pi_-}{(\pi_+ - \pi_-) \sqrt{p(1-p)}} \sqrt{n}$$

Example: $n = 260, \pi_- = -0.01, \pi_+ = 0.005, p = 0.7$ → $\theta = 1.173$; tiny move to $p = 0.72$ → $\theta = 2$, showing extreme sensitivity [p.288].

**Bet Size from Predicted Probability** [p.192, ch.10]

For binary outcome:

$$z = \frac{p - 0.5}{\sqrt{p(1-p)}}, \qquad m = 2 Z[z] - 1$$

with $m \in [-1, 1]$, $Z[\cdot]$ standard normal CDF [p.192].

**Size Discretization** [p.195, ch.10]

$$m^* = \text{round}(m/d) \cdot d, \quad d \in (0, 1]$$

to prevent overtrading / jitter [p.195].

**Expected Max from IID Normal (for DSR derivation)** [p.221-222, ch.12]

$$E[\max_i x_i] \approx (1-\gamma)\, Z^{-1}[1 - 1/I] + \gamma\, Z^{-1}[1 - 1/(I e)]$$

with $\gamma \approx 0.5772156649$ [p.222].

## 4. Algoritmos e Pseudocódigo

**Symmetric CUSUM Filter** [p.71-72, Snippet 2.4, ch.2]

```
init S_pos = 0, S_neg = 0, events = []
for t = 1..T:
    y_t = diff or log-diff
    S_pos = max(0, S_pos + y_t)
    S_neg = min(0, S_neg + y_t)
    if S_neg < -h:  S_neg = 0; events.append(t)
    elif S_pos > h: S_pos = 0; events.append(t)
return events
```

**Triple-Barrier Labeling** [p.79-83, Snippet 3.2-3.5, ch.3]

```
for each event i at t_{i,0}:
    upper = price[t_{i,0}] * (1 + ptSl[0] * trgt[i])
    lower = price[t_{i,0}] * (1 - ptSl[1] * trgt[i])
    t_vertical = t_{i,0} + numDays_bars
    t_first_touch = earliest(
        first_t where price >= upper,
        first_t where price <= lower,
        t_vertical
    )
    label = sign(ret over [t_{i,0}, t_first_touch])  # or 0 at vertical
```
Barrier configurations [p.79-80]: `[1,1,1]` standard; `[0,1,1]` stop-only; `[0,0,1]` fixed-horizon; `[0,0,0]` illogical (no label).

**FFD — Fixed-Width Window Fracdiff** [p.124-125, Snippet 5.3, ch.5]

```python
def getWeights_FFD(d, thres):
    w, k = [1.], 1
    while True:
        w_ = -w[-1]/k*(d-k+1)
        if abs(w_) < thres: break
        w.append(w_); k += 1
    return np.array(w[::-1]).reshape(-1, 1)

def fracDiff_FFD(series, d, thres=1e-5):
    w = getWeights_FFD(d, thres); width = len(w)-1
    for each col:
        for iloc in range(width, len(series)):
            df_[loc] = np.dot(w.T, series[loc-width : loc])
    return df
```

**Finding d\* (minimum d for stationarity)** [p.125-126, ch.5]

```
for d in [0, 0.1, 0.2, ..., 1.0]:
    X_d = FFD(X, d, thres=1e-5)
    stat = ADF(X_d)
    if stat < critical_5pct:
        d_star = d; break
use X_{d_star} as feature
```
Example: on E-mini S&P 500 log-prices, $d^* \approx 0.35$ achieves ADF significance while preserving correlation 0.995 with original series [p.126].

**Sequential Bootstrap** [p.101-103, Snippets 4.3-4.5, ch.4]

```
given indicator matrix I[t, i] (which bars influence label i):
phi = []  # selected draws
for draw = 1..I:
    for each j in 1..I:
        u_avg[j] = avg over t in [t_{j,0},t_{j,1}] of:
                   1 / (c_t + 1) where c_t = sum of I[t, k] for k in phi
        delta[j] = u_avg[j] / sum(u_avg)
    pick j according to delta; append to phi
return phi
```

**Purged K-Fold CV** [p.150-154, Snippets 7.1-7.3, ch.7]

```
for fold = 1..k:
    test = fold_indices[fold]
    train = all \ test
    # purge
    for i in train:
        if [t_{i,0}, t_{i,1}] overlaps any [t_{j,0}, t_{j,1}] in test:
            drop i from train
    # embargo
    embargo_len = ceil(0.01 * T)
    drop from train any i where t_{i,0} in [max(test.t1), max(test.t1)+embargo_len]
    fit(train); score(test)
```

**MDA — Mean Decrease Accuracy** [p.161-162, Snippet 8.3, ch.8]

```
fit classifier with Purged K-Fold CV -> baseline_score
for each feature f:
    for each CV split:
        X_test_perm = copy(X_test); shuffle column f of X_test_perm
        score_perm = score(model, X_test_perm)
    MDA[f] = (baseline_score - score_perm) / max_possible_score
```

**CPCV Algorithm** [p.220-221, ch.12]

```
1. Partition T observations into N non-shuffled groups
2. Enumerate all C(N, k) train/test splits
3. For each split: apply purging + embargo (Ch.7) on train
4. Fit classifier on each train set; produce forecasts on corresponding test set
5. Reassemble φ[N,k] = (k/N) * C(N,k) backtest paths
6. Compute distribution of Sharpe ratios across paths
rule of thumb: for target φ paths, pick N = φ+1, k = 2
```

**CSCV — Probability of Backtest Overfitting** [p.208-209, ch.11]

```
M: T x N matrix of PnLs (N trials, T aggregated periods)
Partition M into S even submatrices by rows
For each combination c of S/2 submatrices forming train J (complement = test J_bar):
    R = perf_stats on columns of J
    n_star = argmax R
    R_bar = perf_stats on columns of J_bar
    rank omega_c = relative rank of R_bar[n_star] in R_bar
    logit lambda_c = log(omega_c / (1 - omega_c))
PBO = P(lambda <= 0) = frequency of IS-winner that underperforms OOS median
```

**Optimal Trading Rule on O-U Process** [p.230-232, ch.13]

```
1. Estimate {sigma, phi} from historical data via OLS on:
   Delta P_t = (1 - phi) * (E[P] - P_{t-1}) + sigma * eps_t
2. Construct mesh of (stop_loss, profit_take) pairs, e.g. 20x20
3. Simulate 100,000 synthetic O-U paths using estimated params
4. For each mesh node apply profit_take / stop_loss / maxHP barriers
5. Pick (sl*, pt*) maximizing Sharpe over synthetic sample
half-life: tau = -log(2) / log(phi)  =>  phi = 2^{-1/tau}
```

**Strategy Risk — Probability of Failure** [p.293, ch.15]

```
pi_plus = mean of positive outcomes
pi_minus = mean of negative outcomes
n = bets per year
bootstrap i = 1..I:
    draw floor(n*k) with replacement (k years)  # e.g., k=2
    p_i = proportion of positives in draw
fit KDE on {p_i}
p_theta_star = precision implied by target Sharpe theta*
P[failure] = P(p < p_theta_star)  # CDF from KDE
reject strategy if P[failure] > 0.05
```

## 5. Regras de Trading Explícitas

- **REGRA [p.55, ch.2]**: Prefer **dollar bars** over time bars for sampling; they are robust to corporate actions (splits, issuance, buybacks) and closer to IID-Gaussian.
- **REGRA [p.57, ch.2]**: Prefer **volume bars / dollar bars** over time bars because time bars oversample low-activity periods and undersample high-activity periods, and exhibit serial correlation + heteroscedasticity.
- **REGRA [p.71-72, ch.2]**: Trigger events for model inference via **CUSUM filter** rather than Bollinger bands — CUSUM requires a full run of magnitude $h$, avoiding the hovering-triggers flaw.
- **REGRA [p.77, ch.3]**: Never use a fixed-time horizon with a fixed threshold $\tau$ on time bars for labeling; use a volatility-scaled threshold (rolling EWM std) or switch to volume/dollar bars.
- **REGRA [p.78-80, ch.3]**: Use **Triple-Barrier Method** [1,1,1] (profit-take + stop-loss + vertical time barrier) for labeling — path-dependent and volatility-adjusted.
- **REGRA [p.87-88, ch.3]**: Apply **meta-labeling** whenever you have a primary model for side: train a secondary ML to decide size/pass only. Limits overfitting and improves F1.
- **REGRA [p.101, ch.4]**: When bagging with overlapping labels, set `max_samples = out['tW'].mean()` (average uniqueness) in sklearn `BaggingClassifier` to prevent oversampling redundant observations.
- **REGRA [p.125-126, ch.5]**: For every non-stationary feature, compute $d^*$ = minimum fractional differentiation order that passes ADF at 95%; use FFD($d^*$) as feature. Goal: stationarity with maximum memory.
- **NUNCA [p.140, ch.6]**: Trust out-of-bag accuracy from Random Forest in financial applications — it is inflated because of non-IID overlapping samples. Use Purged K-Fold CV instead.
- **REGRA [p.140, ch.6]**: Prefer bagging over boosting in finance — bagging attacks overfitting (the main enemy in low-SNR data); boosting attacks bias and increases overfitting risk.
- **REGRA [p.150-152, ch.7]**: Every CV in finance MUST use **Purging + Embargo** (~1% of T). Plain K-Fold leaks information through serial correlation and label overlap.
- **NUNCA [p.155, ch.7]**: Use `sklearn.cross_val_score` directly — has known bugs (sample-weights not forwarded to scoring). Use the `cvScore` function in Snippet 7.4 instead.
- **NUNCA [p.156, ch.7]**: Shuffle before K-Fold in financial datasets — shuffling guarantees leakage because serially correlated neighbors end up in both splits.
- **REGRA [p.159, ch.8]**: **"Backtesting is not a research tool. Feature importance is."** (First Law of Backtesting). Complete feature importance analysis before running any backtest.
- **REGRA [p.160-164, ch.8]**: Always cross-check feature importance with PCA ranking. A strong Kendall's tau between MDI/MDA rank and PCA eigenvalue rank is evidence the signal is not overfit.
- **REGRA [p.194, ch.10]**: Derive bet size from predicted probability: $m = 2 Z[z] - 1$ with $z = (p - 0.5)/\sqrt{p(1-p)}$; then average active bets; then discretize with step $d$ (e.g., 0.1) to prevent over-trading.
- **NUNCA [p.204, ch.11]**: Use backtest as a research tool. **"Researching and backtesting is like drinking and driving. Do not research under the influence of a backtest."** (Second Law of Backtesting) [p.206].
- **REGRA [p.206-207, ch.11]**: Develop models for **whole asset classes**, not individual securities; apply bagging; don't backtest until all research is complete; record every backtest (for DSR / PBO).
- **REGRA [p.220-222, ch.12]**: Prefer **CPCV** over Walk-Forward and plain CV. Target $\varphi \ge 100$ paths; set $N = \varphi + 1, k = 2$.
- **REGRA [p.276, ch.14]**: Reject strategies with DSR < 0.95 or PSR < 0.95 at 5% significance. Always report PSR and DSR alongside the raw Sharpe.
- **REGRA [p.276, ch.14]**: **"Every backtest result must be reported in conjunction with all the trials involved in its production."** (Third Law of Backtesting). Absent that info, false-discovery probability cannot be assessed.
- **REGRA [p.293, ch.15]**: Reject a strategy if $P[p < p_{\theta^*}] > 0.05$ — probability of strategy failure above 5% is too risky even for low-volatility portfolios.
- **REGRA [p.297-299]**: Use **HRP** (Hierarchical Risk Parity) for allocating capital across strategies/assets instead of Markowitz CLA; HRP doesn't require covariance inversion, delivers lower OOS variance even vs. minimum-variance optimizers.

## 6. Pitfalls e Anti-patterns

- [p.53, ch.2] Using **backfilled / reinstated** fundamental data (Bloomberg style) with the final-reported value aligned to the original release date — this is look-ahead bias. Always check release timestamps.
- [p.55-57, ch.2] Sampling at **fixed time intervals** ("time bars") because it oversamples dead hours, undersamples active hours, and produces heteroscedastic returns.
- [p.77, ch.3] Using a **fixed threshold $\tau$** for labeling without volatility scaling — produces almost all 0-labels in quiet regimes and all 1-labels in storms.
- [p.97, ch.4] Assuming **labels are IID** when they overlap in time — break the foundational assumption of most ML algorithms. Overlapping → redundancy → in-bag leakage → inflated OOB accuracy.
- [p.100, ch.4] **Dropping overlapping outcomes** as a fix — extreme info loss. Use weights or sequential bootstrap instead.
- [p.115-116, ch.5] **Integer differentiation** (log-returns) wipes out long memory — correlation between original series and returns ≈ 0.03 for E-mini [p.126]. Use FFD($d^*$).
- [p.140, ch.6] Trusting Random Forest **out-of-bag accuracy** in finance — inflated by redundant samples.
- [p.140, ch.6] Using **boosting** in finance when the primary concern is overfitting (low SNR data). Boosting reduces bias at cost of overfitting.
- [p.148-149, ch.7] Using **plain K-Fold / `cross_val_score`** on financial data — leakage is guaranteed because of serial correlation and label overlap.
- [p.155, ch.7] Known **sklearn bugs**: scoring functions don't know `classes_`; `cross_val_score` doesn't pass sample_weight to log_loss. Roll your own (Snippet 7.4).
- [p.158, ch.8] Running **data → ML → backtest → repeat** until "nice-looking backtest" appears. ~20 iterations suffice to fabricate a 5%-significant false discovery [p.158].
- [p.160, ch.8] **MDI**: penalizes correlated / substitute features by dilution; features with more categories are favored (Strobl et al. [2007] bias).
- [p.161, ch.8] **MDA** also suffers substitution effects: shuffling one of two identical features leaves predictive power intact via the other.
- [p.204, ch.11] Luo et al.'s **"Seven Sins"** [p.204]: (1) survivorship bias, (2) look-ahead bias, (3) storytelling, (4) data mining/snooping, (5) transaction cost underestimation, (6) outlier dependence, (7) shorting (ignoring availability and cost of lending).
- [p.204-205, ch.11] Even a **"flawless" backtest** from an experienced researcher is likely wrong, because experience means having run thousands of prior backtests on the same data (selection bias).
- [p.206, ch.11] **Adjusting the model based on backtest results** — this is overfitting by definition. The purpose of a backtest is to discard bad models, not to improve them.
- [p.217, ch.12] **Walk-forward backtests** test a single historical path and are easy to overfit; their main argument ("predicting the past biases up") is weak because walk-backward backtests frequently underperform walk-forward on the same data.
- [p.222, ch.12] **Ignoring the number of trials $N$** when reporting Sharpe — FWER, FDR, and PBO cannot be computed; maximum SR under H0 grows with $\sqrt{\ln N}$ (eq. p.222).
- [p.228-229, ch.13] **Calibrating trading rules by brute force** over historical data — with two free parameters $(\bar{\pi}, \underline{\pi})$ overfit is almost inevitable when returns have serial dependence. Use synthetic data via O-U fit instead.
- [p.292-293, ch.15] **Confusing portfolio risk with strategy risk**. A low-volatility portfolio can hide a fragile strategy where a 3% drop in precision ($p = 0.70 \to 0.67$) wipes out all profits.
- [p.298-299, ch.16] **Markowitz's curse**: as correlations grow (more diversification needed), the covariance condition number explodes, making inverse matrix unstable; estimation errors dominate diversification gains. Even **equal-weight outperforms mean-variance OOS** [De Miguel et al. 2009, cited p.299].

## 7. Parâmetros Sensíveis

- **FFD threshold $\tau$**: [p.125] recommended $\tau = 10^{-5}$. Determines cut-off for dropping small weights. Small changes don't meaningfully alter $d^*$; low curve-fit risk.
- **FFD order $d$**: [p.125-126] should be selected as the **minimum** $d$ such that ADF(FFD series) < 5% critical value. For E-mini S&P 500, $d^* \approx 0.35$ [p.126]. Economically justified — it's the smallest differentiation preserving memory.
- **Embargo fraction**: [p.152] typically $h \approx 0.01 T$ — economically justified as "slightly more than max label horizon"; not optimized.
- **Triple-barrier `ptSl`**: [p.79] the ratio of profit-taking to stop-loss multipliers. Sensitive. Author recommends symmetric `[1,1]` when learning side, asymmetric for meta-labeling [p.84].
- **`max_samples` in bagging**: [p.101] should be set to average uniqueness `out['tW'].mean()`, not 1.0. Economically derived, not tuned.
- **Bet discretization $d$**: [p.195] recommended 0.1-0.2. Trade-off between responsiveness and turnover.
- **Number of CPCV paths $\varphi$**: [p.220] rule of thumb $N = \varphi + 1, k = 2$. For 1000 paths, $N = 1001$ groups [ex.12.4, p.224].
- **Target Sharpe $\theta^*$ for PSR/DSR**: [p.276] PSR/DSR > 0.95 at 5% significance. Not a free tuning knob; this is the statistical threshold.
- **Number of trials $N$ for DSR**: [p.275] cannot be invented; must be counted honestly across the research pipeline. López de Prado [2018] provides estimation method [p.275].
- **Maximum holding period `maxHP`**: [p.231, ch.13] example uses 100 observations. Analogous to the vertical barrier; should be justified by strategy horizon, not tuned on backtest.

## 8. Citações Literais Importantes

> "Backtesting is not a research tool. Feature importance is." — Marcos López de Prado, Advances in Financial Machine Learning (2018) [p.159, Snippet 8.1, Marcos' First Law of Backtesting]

> "Backtesting while researching is like drinking and driving. Do not research under the influence of a backtest." — [p.206, Snippet 11.1, Marcos' Second Law of Backtesting]

> "Every backtest result must be reported in conjunction with all the trials involved in its production. Absent that information, it is impossible to assess the backtest's 'false discovery' probability." — [p.275, Snippet 14.5, Marcos' Third Law of Backtesting]

> "It takes almost as much effort to produce one true investment strategy as to produce a hundred, and the complexities are overwhelming…" — [p.29, ch.1, meta-strategy paradigm]

> "The maddening thing about backtesting is that, the better you become at it, the more likely false discoveries will pop up." — [p.205, ch.11]

> "Finance is not a plug-and-play subject as it relates to ML applications. Anyone who tells you otherwise will waste your time and money." — [p.97, ch.4]

> "Overfitting is unethical. It leads to promising outcomes that cannot be delivered. When done knowingly, overfitting is outright scientific fraud." — [p.38, ch.1]

## 9. Conexões com Outros Livros Desta Base

- **Purged K-Fold CV, CPCV, PBO, DSR, HRP** — all are deepened (with matrix-denoising extensions) in `ml_for_asset_managers.md` (same author; 2020 follow-up focused on asset management specifically).
- **Fractional differentiation / stationarity with memory** — covered in `ml_for_asset_managers.md` as well (López de Prado's later treatment).
- **Parsimony / overfitting avoidance via few tunables** — thematic overlap with `systematic_trading.md#design-principles` (Carver reaches similar conclusions via "no optimization, use economic priors" route) although Carver does not use purging/embargoing specifically.
- **Kelly / bet sizing from predicted probability** — `systematic_trading.md` discusses Kelly fractional sizing in a discretionary framework; López de Prado's `m = 2Z[z] - 1` formulation [p.192, ch.10] is complementary but driven by ML probabilities rather than forecast strength.
- Other cross-refs (e.g., microstructure, entropy features) — N/A in current knowledge base; will be added as more books are processed.
