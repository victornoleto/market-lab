# Analysis of Financial Time Series, Third Edition

## Metadata
- **Autor:** Ruey S. Tsay [p.i, cover]
- **Ano:** 2010 [p.iv]
- **Editora:** John Wiley & Sons, Inc., Hoboken, New Jersey
- **Páginas:** 677 (body) + frontmatter; 714 PDF pages total
- **ISBN:** 978-0-470-41435-4 [p.iv, N/A for exact location but on copyright page]
- **Foco principal:** Applied, empirical treatment of financial time series — volatility (GARCH family, SV), nonlinear (TAR/MSA), high-frequency microstructure, extreme-value VaR, multivariate VAR/cointegration, multivariate volatility (DCC/BEKK), state-space/Kalman, MCMC — aimed at practitioners of risk management and quant finance.

## 1. Tese Central

Tsay's organizing claim is that *financial time series differs fundamentally from generic time series because its "signal" is uncertainty itself* — volatility is unobservable, tails are heavy, serial dependence shows up mostly in squared/absolute returns, and microstructure contaminates naive variance estimates [ch.1, p.1-2; ch.3.1, p.109-110]. The book therefore devotes more than half its volume to methods that model second-moment and tail behaviour: ARCH/GARCH/EGARCH/TGARCH/SV for conditional variance [ch.3, p.109-155], extreme-value theory and POT for VaR [ch.7, p.325-415], and multivariate volatility with time-varying correlations for portfolio risk [ch.10, p.505-568]. A secondary thesis: high-frequency transactional data requires its own apparatus (duration models, microstructure corrections, realized volatility) [ch.5, p.231-286], and long-run cross-asset relations are best handled by cointegration and error-correction models, with pairs trading as the canonical financial application [ch.8.6-8.8, p.428-455].

## 2. Conceitos-Chave

- **Simple net return** — $R_t = P_t/P_{t-1} - 1$ [p.3, ch.1.1, eq.1.2].
- **Log return (continuously compounded)** — $r_t = \ln(1+R_t) = p_t - p_{t-1}$; multiperiod log returns simply sum: $r_t[k] = r_t + r_{t-1} + \cdots + r_{t-k+1}$ [p.5, eq.1.6].
- **Excess return** — $Z_t = R_t - R_{0t}$, $z_t = r_t - r_{0t}$ where 0 subscript is risk-free [p.6, eq.1.7].
- **Volatility clustering** — large |return| followed by large |return|; rationale for ARCH [p.110, ch.3.1].
- **Leverage effect** — asymmetric volatility response to negative vs positive shocks; motivates EGARCH/TGARCH [p.110, ch.3.1].
- **ARCH effect** — serial correlation in $a_t^2$; tested via Ljung–Box on $\{a_t^2\}$ or Engle's LM test [p.114-115, ch.3.3.1].
- **Conditional heteroskedasticity (structural)** — $r_t = \mu_t + a_t$, $\mu_t = E(r_t|F_{t-1})$, $\sigma_t^2 = \text{Var}(r_t|F_{t-1})$ [p.111-112, eq.3.2-3.3].
- **Realized volatility** — $RV_t = \sum_{i=1}^n r_{t,i}^2$ from $n$ intraday returns; quadratic variation estimate of daily variance [p.162, eq. without number in §3.15.1].
- **Tail index / shape parameter** — $\xi$ of GEV distribution; invariant under time aggregation [p.344-345, §7.5.1].
- **Value at Risk (VaR)** — $(1-p)$-quantile of loss distribution over horizon $\ell$: $p = \Pr[L(\ell) \geq \text{VaR}]$ [p.327, eq.7.1].
- **Expected Shortfall (ES / CVaR)** — $E[L | L > \text{VaR}]$; subadditive, unlike VaR [p.329, §7.1 remark; p.332-333, §7.2.3].
- **Cointegration** — $x_t$ is $k$-dim I(1) but $\beta' x_t$ is stationary for some $\beta$ [p.428-430, §8.6].
- **Error-correction model (ECM)** — $\Delta x_t = \alpha(\beta' x_{t-1} - \mu_w) + \sum \Gamma_i \Delta x_{t-i} + \epsilon_t$; $\beta' x_{t-1}$ is the error-correction term [p.432-433, eq.8.33-8.36].
- **Spread (pairs trading)** — $w_t = p_{1t} - \gamma p_{2t}$, stationary and mean-reverting when the two log-price series cointegrate [p.447, §8.8.1, eq.8.45].
- **Dynamic Conditional Correlation (DCC)** — parsimonious parameterization where conditional covariance $\Sigma_t = D_t \rho_t D_t$ with $\rho_t$ evolving via 2 scalars $\theta_1, \theta_2$ [p.531-532, §10.4.3].
- **ACD (autoregressive conditional duration)** — volatility-style model for inter-trade time gaps in high-frequency data [p.256-266, ch.5.5, referenced in TOC].
- **Stochastic Volatility (SV)** model — volatility has its own innovation $v_t$ beyond the return shock [p.153-154, §3.12, eq.3.40].

## 3. Fórmulas / Equações

**ARCH(m)** [p.115-116, §3.4, eq.3.5]

$$a_t = \sigma_t \epsilon_t, \qquad \sigma_t^2 = \alpha_0 + \sum_{i=1}^{m} \alpha_i a_{t-i}^2$$

with $\alpha_0>0, \alpha_i\geq 0$, and $\{\epsilon_t\}$ iid mean 0 variance 1 (Gaussian, standardized-t, or GED).

**GARCH(m,s)** — Bollerslev (1986) [p.131-132, §3.5, eq.3.14]

$$\sigma_t^2 = \alpha_0 + \sum_{i=1}^{m}\alpha_i a_{t-i}^2 + \sum_{j=1}^{s}\beta_j \sigma_{t-j}^2$$

**GARCH(1,1) stationary** [p.132, eq.3.16]

$$\sigma_t^2 = \alpha_0 + \alpha_1 a_{t-1}^2 + \beta_1 \sigma_{t-1}^2, \quad 0\le\alpha_1,\beta_1\le1, \ \alpha_1+\beta_1 < 1$$

Unconditional variance: $E(a_t^2) = \alpha_0 / (1 - \alpha_1 - \beta_1)$ [p.132]. $\ell$-step-ahead forecast converges to it: $\sigma_h^2(\ell) \to \alpha_0/(1-\alpha_1-\beta_1)$ as $\ell\to\infty$ [p.133, eq.3.17]. Empirical example: S&P 500 monthly excess returns fit GARCH(1,1) with $\sigma_t^2 = 0.000086 + 0.1216 a_{t-1}^2 + 0.8511 \sigma_{t-1}^2$ [p.137, eq.3.19].

**IGARCH(1,1)** [p.141-143, §3.6] — when $\alpha_1 + \beta_1 = 1$. Special case (random-walk IGARCH, $\alpha_0 = 0$) is the RiskMetrics model:

$$\sigma_t^2 = \alpha \sigma_{t-1}^2 + (1-\alpha) a_{t-1}^2, \quad \alpha \in (0.9, 1), \text{ typical } 0.94$$

[p.329, eq.7.2].

**GARCH-M** [p.143, §3.7] — risk premium enters the mean equation:

$$r_t = \mu + c \sigma_t^2 + a_t, \qquad a_t = \sigma_t \epsilon_t, \quad \sigma_t^2 = \alpha_0 + \alpha_1 a_{t-1}^2 + \beta_1 \sigma_{t-1}^2$$

**EGARCH(m,s)** — Nelson (1991) [p.144-145, §3.8, eq.3.25, 3.28]

$$\ln(\sigma_t^2) = \alpha_0 + \sum_{i=1}^s \alpha_i \frac{|a_{t-i}| + \gamma_i a_{t-i}}{\sigma_{t-i}} + \sum_{j=1}^m \beta_j \ln(\sigma_{t-j}^2)$$

Leverage effect: $\gamma_i < 0$ expected. IBM example: $\ln\sigma_t^2 = -0.557 + 0.220|a_{t-1}| - 0.264 a_{t-1}/\sigma_{t-1} + 0.929\ln\sigma_{t-1}^2$ [p.147, eq.3.32]. Volatility ratio for $\pm 2$ sigma shocks: negative/positive ≈ 1.374 (IBM, 37.4% asymmetry) [p.146].

**TGARCH / GJR model** [p.149-150, §3.9, eq.3.34]

$$\sigma_t^2 = \alpha_0 + \sum_{i=1}^s (\alpha_i + \gamma_i N_{t-i}) a_{t-i}^2 + \sum_{j=1}^m \beta_j \sigma_{t-j}^2$$

where $N_{t-i} = 1$ if $a_{t-i} < 0$, else 0. IBM example: $\sigma_t^2 = 3.45\times10^{-4} + (0.0658 + 0.0843 N_{t-1})a_{t-1}^2 + 0.8182 \sigma_{t-1}^2$ [p.149, eq.3.35].

**Stochastic Volatility model** [p.153-154, §3.12, eq.3.40]

$$a_t = \sigma_t \epsilon_t, \qquad (1 - \alpha_1 B - \cdots - \alpha_m B^m)\ln(\sigma_t^2) = \alpha_0 + v_t$$

with $\epsilon_t \sim N(0,1)$, $v_t \sim N(0,\sigma_v^2)$, independent.

**Long-Memory SV (LMSV)** [p.154, §3.13, eq.3.41]

$$\sigma_t = \sigma\exp(u_t/2), \quad (1-B)^d u_t = \eta_t, \quad 0 < d < 0.5$$

**Parkinson (1980) range-based variance** [p.163, §3.15.2]

$$\hat\sigma^2_{2,t} = \frac{(H_t - L_t)^2}{4\ln 2} \approx 0.3607(H_t - L_t)^2$$

**Garman–Klass (1980) O/H/L/C estimator** [p.163, §3.15.2]

$$\hat\sigma^2_{5,t} \approx 0.5(H_t - L_t)^2 - 0.386(C_t - O_t)^2$$

Efficiency relative to close-to-close: approximately 7.4× [p.164].

**Yang–Zhang (2000) drift-independent estimator** [p.163-164, §3.15.2]

$$\hat\sigma^2_{yz} = \hat\sigma^2_o + k \hat\sigma^2_c + (1-k)\hat\sigma^2_{rs}$$

**Realized Volatility** [p.162, §3.15.1]

$$RV_t = \sum_{i=1}^n r_{t,i}^2$$

Recommended intraday interval: 4–15 minutes for heavily-traded U.S. assets [p.162]. $\ln(RV_t)$ often fits Gaussian ARIMA(0,1,q) [p.162].

**Generalized Extreme Value (GEV) distribution** [p.343, §7.5.1, eq.7.16]

$$F_*(x) = \begin{cases} \exp\big[-(1 + \xi x)^{-1/\xi}\big] & \xi \ne 0 \\ \exp[-\exp(-x)] & \xi = 0 \end{cases}$$

- $\xi = 0$: Gumbel (thin tails).
- $\xi > 0$: Fréchet — includes Student-$t$ and stable. **Relevant for financial returns** [p.344].
- $\xi < 0$: Weibull (finite).

**Generalized Pareto Distribution (GPD)** — excess over threshold $\eta$ [p.360-361, §7.7.1, eq.7.31]

$$G_{\xi,\psi}(x) = \begin{cases} 1 - \big(1 + \xi x/\psi(\eta)\big)^{-1/\xi} & \xi \ne 0 \\ 1 - \exp[-x/\psi(\eta)] & \xi = 0 \end{cases}$$

Mean excess function (linear in threshold under GPD) [p.361, §7.7.2]:

$$e(\eta) = E[r - \eta | r > \eta] = \frac{\psi(\eta_0) + \xi(\eta - \eta_0)}{1 - \xi}$$

**RiskMetrics VaR** [p.330, §7.2] — under IGARCH(1,1) with zero mean and Gaussian innovations:

- 1-day 5%: $\text{VaR} = 1.65\,\sigma_{t+1}$
- 1-day 1%: $\text{VaR} = 2.326\,\sigma_{t+1}$
- $k$-day: $\text{VaR}(k) = \sqrt{k}\cdot \text{VaR}$ ("square-root-of-time rule")

**Expected Shortfall under Gaussian** [p.333, §7.2.3]

$$\text{ES}_q = \frac{f(\text{VaR}_q)}{p}\sigma_t$$

where $f$ is standard normal pdf, $q = 1 - p$.

**Multi-position VaR** [p.332, §7.2.2]

$$\text{VaR} = \sqrt{\sum_{i=1}^m \text{VaR}_i^2 + 2\sum_{i<j} \rho_{ij}\,\text{VaR}_i\,\text{VaR}_j}$$

**BEKK multivariate GARCH** [p.513-514, §10.2.2, eq.10.6]

$$\Sigma_t = A A' + \sum_{i=1}^m A_i(a_{t-i}a_{t-i}')A_i' + \sum_{j=1}^s B_j \Sigma_{t-j} B_j'$$

Guarantees $\Sigma_t$ positive-definite. Parameter count: $k^2(m+s) + k(k+1)/2$ — explodes with dimension [p.513].

**Engle (2002) DCC** [p.531-532, §10.4.3]

$$\rho_t = J_t Q_t J_t, \qquad Q_t = (1-\theta_1-\theta_2)\bar Q + \theta_1 \epsilon_{t-1}\epsilon_{t-1}' + \theta_2 Q_{t-1}$$

with $\theta_1,\theta_2\ge 0$, $\theta_1+\theta_2 < 1$, $\epsilon_{it}=a_{it}/\sqrt{\sigma_{ii,t}}$, $\bar Q$ unconditional covariance of $\epsilon_t$, $J_t = \text{diag}(q_{ii,t}^{-1/2})$.

**Pairs-trading error-correction** [p.447, §8.8.1, eq.8.45]

$$\begin{pmatrix} r_{1t} \\ r_{2t}\end{pmatrix} = \begin{pmatrix}\alpha_1\\\alpha_2\end{pmatrix}(w_{t-1}-\mu_w) + \begin{pmatrix}\epsilon_{1t}\\\epsilon_{2t}\end{pmatrix}, \qquad w_t = p_{1t} - \gamma p_{2t}$$

with $\alpha_1, \alpha_2$ of opposite signs (mean-reversion). BHP/VALE empirical: $\hat\gamma = 0.718$, $\sigma_w = 0.044$, $\mu_w = 1.81$ [p.450-452].

**Markov Switching (MSA) model** — Hamilton (1989) [p.186-187, §4.1.4, eq.4.18]

$$x_t = \begin{cases} c_1 + \sum_{i=1}^p \phi_{1,i} x_{t-i} + a_{1t} & s_t = 1 \\ c_2 + \sum_{i=1}^p \phi_{2,i} x_{t-i} + a_{2t} & s_t = 2 \end{cases}$$

with transition probabilities $P(s_t=2|s_{t-1}=1) = w_1$, $P(s_t=1|s_{t-1}=2) = w_2$. Expected duration in state $i$ is $1/w_i$ [p.187].

**SETAR(k,p) model** — Tong (1978, 1990) [p.180, §4.1.2, eq.4.9]

$$x_t = \phi_0^{(j)} + \phi_1^{(j)} x_{t-1} + \cdots + \phi_p^{(j)} x_{t-p} + a_t^{(j)}, \quad \text{if } \gamma_{j-1} \le x_{t-d} < \gamma_j$$

Ergodicity for 2-regime AR(1): $\phi_1^{(1)} < 1$, $\phi_1^{(2)} < 1$, $\phi_1^{(1)}\phi_1^{(2)} < 1$ [p.179].

## 4. Algoritmos e Pseudocódigo

**ARCH-effect test (build volatility model)** [p.113-115, §3.3]

```
# Step 1: specify mean equation (often ARMA(p,q) or just demean)
mu_hat = fit_mean(r_t)
a_t = r_t - mu_hat

# Step 2: test for ARCH
LjungBox(a_t^2, lag=m)          # McLeod-Li
EngleLM(a_t, lag=m)             # LM: regress a_t^2 on a_{t-1}^2,...,a_{t-m}^2

# Step 3: if significant, jointly estimate mean + GARCH(p,q)
model = fit_garch(r_t, mean_order=(p_m,q_m), vol_order=(p,q))

# Step 4: diagnose on standardized residuals
stdres = model.a / model.sigma
LjungBox(stdres, lag=12)         # for mean misspec
LjungBox(stdres^2, lag=12)       # for vol misspec
```

**GARCH(1,1) 1-step and multistep forecast** [p.133, §3.5, eq.3.17]

```
sigma2_h1 = alpha0 + alpha1*a_h^2 + beta1*sigma_h^2
for l in 2, 3, ...:
    sigma2_hl = alpha0 + (alpha1 + beta1) * sigma2_h(l-1)
# limit -> alpha0 / (1 - alpha1 - beta1)
```

**RiskMetrics VaR (EWMA IGARCH with alpha ≈ 0.94)** [p.328-331, §7.2]

```
alpha = 0.94
sigma2_t = alpha * sigma2_{t-1} + (1 - alpha) * r_{t-1}^2
VaR_1day_5pct  = 1.65 * sqrt(sigma2_{t+1}) * Position
VaR_kday_5pct  = 1.65 * sqrt(k * sigma2_{t+1}) * Position    # sqrt-t rule
VaR_1day_1pct  = 2.326 * sqrt(sigma2_{t+1}) * Position
ES_1day_5pct   = (phi(1.65) / 0.05) * sqrt(sigma2_{t+1}) * Position
```

**Peaks-Over-Threshold (POT) for VaR** [p.359-365, §7.7]

```
# Pick threshold eta (~5% of observations as exceedances)
# Rule of thumb: stable return series -> 2.5%; volatile -> up to 10%
eta = choose_threshold(returns)        # inspect mean-excess plot for linearity
exceedances = {r_t - eta : r_t > eta}

# Fit GPD by MLE
xi_hat, psi_hat = fit_GPD(exceedances)

# Quantile (VaR)
N_eta = len(exceedances); T = len(returns)
p_star = small_tail_prob        # e.g. 0.01
VaR = eta + (psi_hat / xi_hat) * ((T/N_eta * p_star)^(-xi_hat) - 1)
```

**Pairs trading (cointegration-based)** [p.446-453, §8.8]

```
# 1. SELECT CANDIDATES: same risk factors / same sector (APT rationale)
# 2. TEST COINTEGRATION of log prices
p1 = log(Price1); p2 = log(Price2)
# regression method
beta0, gamma, resid = OLS(p1 ~ p2)
# verify residuals stationary: AR(2) fit or ADF test
ADF_stat, p_val = adf_test(resid)
assert p_val < 0.05, "not cointegrated"

# 3. ECM via Johansen (more formal)
VECM = fit_VECM(xt = [p1, p2], trend='rc')
# extract gamma_hat, mu_w, alpha_1, alpha_2 with alpha_1*alpha_2 < 0

# 4. SPREAD & TRADING BANDS
w_t = p1_t - gamma_hat * p2_t
sigma_w = std(w_t); mu_w = mean(w_t)
Delta = choose_delta(sigma_w)   # e.g. 1 sigma (~0.045 for BHP/VALE example)
assert 2*Delta > eta_cost, "not profitable after costs"

# 5. EXECUTE
if w_t == mu_w - Delta:
    buy(1 share Stock1); short(gamma_hat shares Stock2)
elif w_t == mu_w + Delta:
    short(1 share Stock1); buy(gamma_hat shares Stock2)
# Unwind when w_t crosses mu_w (shorter holding) or opposite boundary
```

**DCC (Engle) estimation** [p.531-532, §10.4.3]

```
# Stage 1: univariate GARCH on each series => D_t diagonal of sigma_i,t
# Stage 2: standardize eps_it = a_it / sigma_it
# Estimate Q_bar = sample_cov(eps)
# Estimate (theta1, theta2) by QMLE on correlation equation:
Q_t = (1 - theta1 - theta2) * Q_bar + theta1 * eps_{t-1} eps_{t-1}' + theta2 * Q_{t-1}
J_t = diag(Q_t)^{-1/2}
rho_t = J_t * Q_t * J_t
Sigma_t = D_t * rho_t * D_t
```

## 5. Regras de Trading Explícitas

- **REGRA [p.115, §3.3]**: Before modeling volatility, remove the sample mean if statistically different from zero; test BOTH the residual series AND its square via Ljung–Box / Engle LM. No ARCH effect → no GARCH model.
- **REGRA [p.132, eq.3.16]**: GARCH(1,1) parameters must satisfy $\alpha_1 + \beta_1 < 1$ for covariance-stationarity. If estimation returns $\alpha_1 + \beta_1 \ge 0.97$, you have IGARCH — shocks to variance are permanent, forecast horizon matters. Tsay explicitly flags IGARCH as common: S&P 500 fit gives 0.9727 [p.137].
- **REGRA [p.330]**: Under RiskMetrics (IGARCH, mean 0, Gaussian), $k$-day VaR = $\sqrt{k} \times$ 1-day VaR. This rule FAILS if mean ≠ 0 or volatility is not random-walk IGARCH [p.331-332, §7.2.1].
- **REGRA [p.333, §7.2.1]**: Square-root-of-time rule is invalid when $\mu \ne 0$: correct $k$-period 95% quantile is $k\mu + 1.65\sqrt{k}\sigma_{t+1}$, not $\sqrt{k}(1.65\sigma_{t+1})$.
- **REGRA [p.360, §7.7]**: For POT / GPD-based VaR, choose threshold $\eta$ so exceedances ≈ 5% of sample. For stable series, $\eta = 2.5\%$; for volatile (dot-com-like) returns, up to 10%.
- **REGRA [p.389, §7.7.2]**: Use the mean-excess plot $e_T(\eta)$ vs $\eta$; pick $\eta_0$ at the lower bound of the linear region (GPD is valid only where the plot is linear).
- **REGRA [p.449, §8.8.2]**: Pairs trade only if $2\Delta > \eta_{\text{cost}}$ where $\Delta$ is the target deviation and $\eta_{\text{cost}}$ is the round-trip cost (commissions + bid-ask). Otherwise the strategy is EV-negative.
- **REGRA [p.449, eq.8.45]**: Enter pairs trade only when the two ECM loadings have opposite signs ($\alpha_1 \alpha_2 < 0$) — this is the empirical signature of mean-reversion toward the cointegration equilibrium. BHP/VALE: $\alpha_1 = -0.067$, $\alpha_2 = +0.026$ [p.451].
- **REGRA [p.452]**: Common practical choice for $\Delta$ = one standard deviation of the spread $\sigma_w$ (BHP/VALE: 0.045). Under Gaussian assumption, $P(|w_t - \mu_w| > \sigma_w) \approx 30\%$, ensuring sufficient trade frequency.
- **REGRA [ch.3.15.1, p.162]**: When building daily realized volatility, use 4–15-minute returns (not 1-minute) to avoid microstructure bias from bid-ask bounce. Overnight return must be added for stocks (not ignored); for indices / FX it is less critical.
- **NUNCA [p.331]**: Trust RiskMetrics VaR on heavy-tailed returns — the normality assumption systematically underestimates VaR for stocks. Use Student-$t$ innovations or EVT/POT instead.
- **NUNCA [p.360, §7.7]**: Use "block maxima" extreme-value with a fixed block length $n$ when $n$ is arbitrary. Prefer POT/GPD; it is threshold-based and uses more data.
- **REGRA [p.146-147]**: Expect $\gamma_i < 0$ in EGARCH (leverage effect). If estimate is positive, reconsider model or data issues. IBM: $\gamma = -0.264$, $t=-2.09$, significant at 5% [p.147].

## 6. Pitfalls e Anti-patterns

- [p.110-111, ch.3.1] **Implied volatility ≠ statistical volatility.** Implied vol (from Black-Scholes) is systematically higher than GARCH estimates; don't mix them.
- [p.112, ch.3.1] **Volatility is unobservable** — you cannot directly "validate" a GARCH forecast against a single realized return. Use proxies (squared return, realized variance) and understand they are noisy.
- [p.131, §3.5] **Higher-order GARCH(p,q) with p,q > 1 rarely improves fit.** Only lower-order models (1,1), (2,1), (1,2) are used in practice.
- [p.134-135] **GARCH tails are too thin under Gaussian innovations** for high-frequency returns. Must use Student-$t$ or GED for honest tail representation.
- [p.144, §3.8] **Sign of leverage coefficient matters.** In EGARCH the weighted innovation $g(\epsilon_t) = \theta\epsilon_t + \gamma(|\epsilon_t|-E|\epsilon_t|)$ requires $\theta < 0$ for negative returns to increase volatility. Check sign; positive $\theta$ is a red flag.
- [p.331, §7.2.1] **Normality assumption + IGARCH-with-zero-mean gives the clean √t rule.** If you relax either, the √t rule BREAKS and you need to recompute — see eq on p.332 with extra $k\mu$ term.
- [p.328, §7.2 remark] **VaR is NOT subadditive.** Merging portfolios can increase VaR. Use Expected Shortfall (CVaR) if you need subadditivity [p.329].
- [p.327, §7.1] **VaR ignores tail shape past the quantile.** Two assets with same VaR can have very different losses beyond it. Expected Shortfall fixes this.
- [ch.5.1-5.2, p.231-255] **Nonsynchronous trading induces spurious lag-1 correlation** in observed returns (up to substantial negative autocorrelation when $\mu\ne0$). Do NOT interpret that as predictability.
- [p.287-289, §5.2] **Bid-ask bounce induces negative lag-1 autocorrelation** in transaction prices even in a random walk. Do not model this as predictable signal. Use mid-quote or trade-direction-filtered series.
- [p.162, §3.15.1] **Too-high intraday frequency (1-minute) biases realized volatility upward** due to bid-ask bounce. Use 4–15 minutes.
- [p.162] **Ignoring overnight return underestimates daily volatility for stocks.** Can be ignored for indices and FX.
- [p.514, §10.2.2] **BEKK(1,1) parameter count is $k^2(m+s) + k(k+1)/2$** — for $k=10$ this is already >100 parameters. Most estimates will be insignificant. Prefer DCC for $k > 3$.
- [p.436, §8.6] **Cointegration tests are fragile** — Tsay explicitly writes: "While I have some misgivings on the practical value of cointegration tests, the idea of cointegration is highly relevant in financial study." Tests ignore parameter uncertainty in the error-correction term. Use the idea, but stress-test statistical significance.
- [p.361, §7.7.1] **VaR from POT depends on threshold $\eta$**; different thresholds → different tail index $\xi$. Sensitivity analysis is mandatory.

## 7. Parâmetros Sensíveis

- **RiskMetrics decay $\alpha \approx 0.94$** [p.329, §7.2]. Tsay attributes this to J. P. Morgan/Longerstaey & More (1995); justification is empirical for daily equity/FX, not theoretical. Typical range $(0.9, 1)$. Not optimized per asset in original RiskMetrics — treat as anchored prior, not free parameter.
- **GARCH lag orders (p,q)** [p.131, §3.5]. Tsay's practical rule: use only GARCH(1,1), (2,1), (1,2). Anything larger is overfit-prone. GARCH(1,1) is almost always chosen; justification is parsimony + empirical consensus.
- **POT threshold $\eta$** [p.360, §7.7]. Not statistically determined — depends on institutional risk tolerance and on sample volatility. Tsay recommends ~5% of observations as exceedances; stable series $\eta=2.5\%$, volatile $\eta$ up to 10%. Sensitivity: VaR estimate is "not sensitive to choice of $\eta$" for IBM [p.360].
- **Realized Volatility sampling interval** [p.162, §3.15.1]. 4–15 minutes for US heavily-traded assets. Below 4 min: microstructure bias. Above 15 min: waste of data. Not a curve-fit parameter — driven by microstructure physics of the specific market.
- **Pairs-trading target deviation $\Delta$** [p.452-453, §8.8.3]. Tsay uses $\Delta \approx \sigma_w$ (one standard deviation of spread). Under Gaussian, $P(|w-\mu_w|>\sigma_w) \approx 30\%$ — enough trade frequency without being too frequent. Must satisfy $2\Delta > \eta_{\text{cost}}$.
- **ARCH-test lag $m$** [p.114-115]. Tsay uses $m=12$ for monthly data. Not optimized — choose to span at least one seasonal cycle.
- **DCC $\theta_1, \theta_2$** [p.531-532]. Constrained $\theta_1+\theta_2<1$ for stationarity. Scalar across all pairs — acknowledged limitation [p.531]: "all the conditional correlations have the same dynamics. This might be hard to justify in real applications, especially when the dimension $k$ is large."
- **EWMA vs IGARCH** [p.329]. RiskMetrics is IGARCH(1,1) with $\alpha_0=0, \alpha_1+\beta_1=1, \mu=0$. These are THREE restrictions — each is falsifiable. The $\mu=0$ assumption is the one most often violated for stocks [p.331].
- **Markov-switching expected duration** $1/w_i$ [p.187, §4.1.4]. McCulloch-Tsay GNP example: $1/w_1 = 1/0.118 \approx 8.5$ quarters (expansion), $1/w_2 = 1/0.286 \approx 3.5$ quarters (contraction). Driven by data, not chosen ex-ante.

## 8. Citações Literais Importantes

> "A special feature of stock volatility is that it is not directly observable." — [p.110, §3.1]

> "While I have some misgivings on the practical value of cointegration tests, the idea of cointegration is highly relevant in financial study." — [p.436, §8.6]

> "The normality assumption used often results in underestimation of VaR. Other approaches to VaR calculation avoid making such an assumption." — [p.331, §7.2.1]

> "An obvious drawback of the prior two models is that $\theta_1$ and $\theta_2$ are scalar so that all the conditional correlations have the same dynamics. This might be hard to justify in real applications, especially when the dimension $k$ is large." — [p.531, §10.4.3]

> "Pairs trading involves selling the higher priced stock and buying the lower priced stock with the hope that the mispricing will correct itself in the future. Note that the true prices of the two stocks are not important. … What is important is that the observed prices be the same." — [p.446, §8.8]

> "The problem of choosing an optimal time interval for constructing realized volatility has attracted much research lately. For heavily traded assets in the United States, a time interval of 4–15 minutes is often used." — [p.162, §3.15.1]

## 9. Conexões com Outros Livros Desta Base

- **Overlap with `time_series_hamilton.md` (major)**: Both cover ARMA, unit roots, cointegration, VAR, Kalman filter, GARCH, Markov switching. Hamilton is the theoretical/proof-oriented treatment (Wold, MLE asymptotics, spectral analysis); Tsay is the empirical/financial-application treatment. Use Hamilton for "why" and Tsay for "how to estimate on real data."
- **GARCH family**: Hamilton ch.21 covers ARCH/GARCH briefly; Tsay ch.3 is the canonical financial treatment (IGARCH, EGARCH, TGARCH, SV, LMSV). **Novelty in Tsay**: full EGARCH derivation with leverage asymmetry [p.144-146], TGARCH/GJR [p.149-150], realized volatility + O/H/L/C estimators [p.162-164] — not in Hamilton.
- **Cointegration & pairs trading**: Hamilton ch.19 treats cointegration theory; Tsay ch.8.8 gives the explicit pairs-trading ECM recipe with BHP/VALE worked example [p.446-455]. Also in `algo_trading_chan.md` and `quant_trading_chan.md` which provide complementary practical strategies — Chan emphasizes half-life and z-score entry rules, Tsay emphasizes the statistical test chain (cointegration → ECM → threshold).
- **VaR & Expected Shortfall**: Tsay ch.7 is the most thorough EVT/POT treatment in this knowledge base. Complements `volatility_trading.md` (Sinclair) which gives options-trading angle on volatility forecasting. `ml_for_asset_managers.md` (López de Prado) treats extreme risk via simulation/synthetic data rather than EVT.
- **Regime switching**: MSA model [p.186-187] is the same Hamilton (1989) two-state model covered deeper in `time_series_hamilton.md` ch.22. Also referenced in `regime_change.md` for practical regime-detection trading rules.
- **Realized volatility / range estimators**: Parkinson, Garman–Klass, Yang–Zhang [p.163-164] — also discussed with trading applications in `volatility_trading.md` and `cycle_analytics.md`.
- **DCC/BEKK multivariate volatility**: unique to Tsay in this base. No direct overlap with other summaries; use as the reference for portfolio-level volatility forecasting.
- **Nonlinearity (TAR/SETAR, STAR, neural nets)**: Tsay ch.4 is the canonical reference. Complements `big_data_ml_quant.md` and `data_driven_science.md` on neural networks, but Tsay gives the econometric testing procedure (linearity tests, Tsay 1989 threshold test) absent from ML-flavored books.
