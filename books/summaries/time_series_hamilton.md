# Time Series Analysis

## Metadata
- **Autor:** James D. Hamilton [p.iii, cover]
- **Ano:** 1994 [p.iv]
- **Editora:** Princeton University Press, Princeton, New Jersey [p.iv]
- **Páginas:** 799 (numbered body) + frontmatter; 814 PDF pages total
- **ISBN:** 0-691-04289-6 [p.iv]
- **Foco principal:** Unified graduate-level treatment of time-series econometrics — ARMA, VAR, Kalman, GMM, unit roots, cointegration, GARCH, regime switching — with full asymptotic theory.

## 1. Tese Central

Every dynamic econometric model must be analyzed both as a computational device (how to estimate and forecast) and as a statistical object (what the sampling distribution of its estimates looks like). Hamilton argues [ch.1, p.1; preface] that the practical researcher needs BOTH the Kalman/state-space machinery for handling latent states and the asymptotic theory (functional CLT, Brownian motion functionals) for unit-root and cointegration inference, because naive application of Gaussian-OLS distribution theory to I(1) regressors produces invalid inference — spurious regressions, wrong critical values [ch.17, p.487-488; ch.18, p.557-561]. The book is organized to build from deterministic difference equations (Ch 1-2) through stationary ARMA (Ch 3-6) and asymptotic theory (Ch 7-8) to the nonstationary / cointegration / regime-switching extensions (Ch 15-22) needed for real financial and macro data.

## 2. Conceitos-Chave

- **Covariance stationarity** — first two moments independent of t [p.45]
- **White noise** — zero-mean, constant variance, uncorrelated over time [p.47]
- **MA(q) process** — $y_t = \mu + \varepsilon_t + \theta_1\varepsilon_{t-1} + \cdots + \theta_q\varepsilon_{t-q}$ [p.50, eq 3.3.8]
- **AR(p) covariance-stationarity** — roots of $1 - \phi_1 z - \cdots - \phi_p z^p = 0$ outside unit circle [p.58]
- **Wold representation** — any covariance-stationary purely non-deterministic process has MA(∞) form with square-summable coefficients; ε_t white noise uncorrelated with own past [p.109, Prop 4.1]
- **Autocovariance-generating function** — $g_Y(z) = \sum \gamma_j z^j$ [p.62]
- **Population spectrum** — $s_Y(\omega) = (2\pi)^{-1} \sum \gamma_j e^{-i\omega j}$ [p.153, eq 6.1.2]
- **VAR(p)** — vector generalization: each variable on own lags + lags of others [p.257]
- **Granger causality** — y fails to Granger-cause x if lagged y does not improve forecast of x beyond lagged x alone [p.303]
- **Impulse-response function** — $\Psi_s$ row i col j = $\partial y_{i,t+s}/\partial \varepsilon_{j,t}$ [p.319]
- **Orthogonalized IRF (Cholesky)** — depends on variable ordering [p.322]
- **Variance decomposition** — attributes s-step forecast MSE to each orthogonalized innovation [p.323]
- **State-space representation** — state eq ξ_{t+1} = Fξ_t + v_{t+1}; observation eq y_t = A'x_t + H'ξ_t + w_t [p.372]
- **Kalman filter** — recursive linear-projection algorithm for unobserved state [p.377]
- **Kalman smoother** — full-sample backward pass yielding ξ̂_{t|T} [p.394]
- **GMM** — estimator minimizing quadratic form in moment conditions E[h(θ; y_t)] = 0 [p.409]
- **Unit root** — y_t = y_{t−1} + u_t; non-stationary; superconsistent rate T for OLS p̂ [p.475, p.488]
- **Brownian motion W(·)** — continuous-time limit of random walk; W(0)=0, independent Gaussian increments [p.478]
- **Functional CLT** — (√T/σ) X_T(·) ⇒ W(·) where X_T is partial-sum process [p.480]
- **Dickey-Fuller test** — ρ-test T(p̂−1) or t-test; nonstandard distributions [p.490]
- **Phillips-Perron test** — DF adjusted non-parametrically for serial correlation [p.509]
- **Augmented Dickey-Fuller (ADF)** — add lagged Δy to absorb serial correlation [p.527]
- **Spurious regression** — OLS of independent I(1) series yields diverging t-statistics [p.557]
- **Cointegration** — individual components I(1), linear combination I(0) [p.571]
- **Error-correction model (ECM / VECM)** — differenced VAR plus lagged deviations from equilibrium [p.580]
- **Granger representation theorem** — Φ(1) = BA' connects cointegration to ECM form [p.582]
- **Engle-Granger two-step** — OLS cointegrating regression then ADF on residuals [p.591-592]
- **Johansen FIML** — reduced-rank regression for VECM; trace and max-eigenvalue tests [p.635]
- **ARCH(m)** — $h_t = \zeta + \alpha_1 u_{t-1}^2 + \cdots$, Engle (1982) [p.658]
- **GARCH(r,m)** — $h_t$ also depends on lagged h's, Bollerslev (1986); equivalent ARMA form for $u_t^2$ [p.665]
- **IGARCH** — Σδ+Σα = 1; non-stationary variance [p.667]
- **EGARCH** — Nelson (1991); log h_t captures leverage effect λ < 0 [p.668]
- **ARCH-M** — conditional variance enters mean equation (risk-return trade-off) [p.667]
- **GJR-GARCH (threshold)** — indicator-based asymmetric GARCH [p.669]
- **Markov chain** — P{s_t = j | s_{t−1}} = p_{ij} transition matrix [p.678]
- **Ergodic probabilities π** — eigenvector of P for unit eigenvalue, normalized 1'π=1 [p.681]
- **Hamilton filter** — iterative optimal inference on hidden regime state [p.692]
- **Kim smoother** — backward pass for smoothed regime probabilities [p.694]

## 3. Fórmulas / Equações

### Stationary ARMA

**AR(1) autocovariance** [p.53, eq 3.4.5]
$$\gamma_j = \phi^j \sigma^2 / (1 - \phi^2)$$

**Yule-Walker equations** [p.59, eq 3.4.37]
$$\rho_j = \phi_1 \rho_{j-1} + \phi_2 \rho_{j-2} + \cdots + \phi_p \rho_{j-p}, \quad j = 1, 2, \ldots$$

**Autocovariance-generating function for MA(q)** [p.62, eq 3.6.3]
$$g_Y(z) = \sigma^2 \theta(z) \theta(z^{-1})$$

**Wold representation (Prop 4.1)** [p.109, eq 4.8.2]
$$Y_t = \sum_{j=0}^{\infty} \psi_j \varepsilon_{t-j} + \kappa_t, \quad \psi_0 = 1, \; \sum \psi_j^2 < \infty$$

**Wiener-Kolmogorov s-step forecast (MA(∞) form)** [p.77, eq 4.2.4 and 4.2.6]
$$\hat y_{t+s|t} = \mu + \psi_s \varepsilon_t + \psi_{s+1} \varepsilon_{t-1} + \cdots, \quad \text{MSE} = \sigma^2 (1 + \psi_1^2 + \cdots + \psi_{s-1}^2)$$

**Population spectrum of ARMA** [p.155-156]
$$s_Y(\omega) = \frac{\sigma^2}{2\pi} \frac{|1 + \theta_1 e^{-i\omega} + \cdots|^2}{|1 - \phi_1 e^{-i\omega} - \cdots|^2}$$

### Regression & Asymptotics

**OLS asymptotic distribution (iid)** [p.210, eq 8.2.8]
$$\sqrt{T}(\hat\beta - \beta) \xrightarrow{L} N(0, \sigma^2 Q^{-1}), \quad Q = E(x_t x_t')$$

**Newey-West HAC covariance** [p.281, eq 10.5.15]
$$\hat S_T = \hat\Gamma_0 + \sum_{j=1}^q [1 - j/(q+1)](\hat\Gamma_j + \hat\Gamma_j')$$

### Vector Autoregressions (VAR)

**VAR(p)** [p.257, eq 10.1.4]
$$y_t = c + \Phi_1 y_{t-1} + \cdots + \Phi_p y_{t-p} + \varepsilon_t, \quad E(\varepsilon_t\varepsilon_t') = \Omega$$

**Stationarity condition** [p.259, eq 10.1.13]
$$|I_n - \Phi_1 z - \Phi_2 z^2 - \cdots - \Phi_p z^p| = 0 \text{ — all roots outside unit circle}$$

**Closed-form for Σ = Var(ξ) via vec** [p.265, eq 10.2.18]
$$\text{vec}(\Sigma) = [I_{r^2} - (F \otimes F)]^{-1} \text{vec}(Q)$$

**Autocovariance recursion** [p.265, eq 10.2.22]
$$\Gamma_j = \Phi_1 \Gamma_{j-1} + \cdots + \Phi_p \Gamma_{j-p}, \quad j \geq p$$

**Vector MA(∞) coefficient recursion** [p.260, eq 10.1.19]
$$\Psi_s = \Phi_1 \Psi_{s-1} + \cdots + \Phi_p \Psi_{s-p}, \quad \Psi_0 = I_n, \quad \Psi_s = 0 \text{ for } s<0$$

**Autocovariance-generating function (vector)** [p.267, eq 10.3.7]
$$G_y(z) = \Psi(z) \Omega [\Psi(z^{-1})]'$$

**VAR MLE = OLS equation-by-equation** [p.293, eq 11.1.11]
$$\hat\Pi' = \left[\sum y_t x_t'\right]\left[\sum x_t x_t'\right]^{-1}$$

**VAR log-likelihood** [p.292, eq 11.1.10]
$$\mathcal{L}(\theta) = -(Tn/2)\log(2\pi) + (T/2)\log|\Omega^{-1}| - \tfrac{1}{2}\sum_t (y_t - \Pi'x_t)'\Omega^{-1}(y_t - \Pi'x_t)$$

**MLE of Ω** [p.295, eq 11.1.27]
$$\hat\Omega = (1/T) \sum_t \hat\varepsilon_t \hat\varepsilon_t'$$

**LR test for VAR lag order** [p.297, eq 11.1.33]
$$2(\mathcal{L}_1^* - \mathcal{L}_0^*) = T\{\log|\hat\Omega_0| - \log|\hat\Omega_1|\} \sim \chi^2(n^2(p_1 - p_0))$$

**Sims small-sample correction** [p.297, eq 11.1.34]
$$(T - k)\{\log|\hat\Omega_0| - \log|\hat\Omega_1|\}, \quad k = 1 + np_1$$

**Asymptotic distribution of VAR coefficients** [p.298, Prop 11.1]
$$\sqrt{T}(\hat\pi_T - \pi) \xrightarrow{L} N(0, \Omega \otimes Q^{-1})$$

**Wald test for linear restrictions Rπ = r** [p.299, eq 11.1.38]
$$\chi^2(m) = T(R\hat\pi - r)'[R(\hat\Omega \otimes \hat Q^{-1})R']^{-1}(R\hat\pi - r)$$

**Granger-causality F-test** [p.305, eq 11.2.9-10]
$$S_1 = \frac{(RSS_0 - RSS_1)/p}{RSS_1/(T - 2p - 1)} \sim F(p, T-2p-1), \quad S_2 = T(RSS_0 - RSS_1)/RSS_1 \sim \chi^2(p)$$

**Block-exogeneity LR test** [p.312, eq 11.3.23]
$$T\{\log|\hat\Omega_{11}(0)| - \log|\hat\Omega_{11}|\} \sim \chi^2(n_1 n_2 p)$$

**Cholesky decomposition** [p.322, eq 11.4.21]
$$\Omega = PP' = AD^{1/2} D^{1/2} A'$$

**MSE of s-step forecast** [p.323, eq 11.5.2]
$$\text{MSE}(\hat y_{t+s|t}) = \Omega + \Psi_1 \Omega \Psi_1' + \cdots + \Psi_{s-1} \Omega \Psi_{s-1}'$$

**Variance decomposition** [p.323, eq 11.5.6]
$$\text{MSE} = \sum_{j=1}^n \text{Var}(u_{jt})\, [a_j a_j' + \Psi_1 a_j a_j' \Psi_1' + \cdots]$$

### Kalman Filter

**State-space form** [p.372, eq 13.1.1-2]
$$\xi_{t+1} = F \xi_t + v_{t+1}, \quad y_t = A'x_t + H'\xi_t + w_t$$

**Filter update** [p.380, eq 13.2.15-16]
$$\hat\xi_{t|t} = \hat\xi_{t|t-1} + P_{t|t-1} H (H' P_{t|t-1} H + R)^{-1} (y_t - A'x_t - H'\hat\xi_{t|t-1})$$
$$P_{t|t} = P_{t|t-1} - P_{t|t-1} H (H' P_{t|t-1} H + R)^{-1} H' P_{t|t-1}$$

**Forecast recursion** [p.380, eq 13.2.20-22]
$$\hat\xi_{t+1|t} = F \hat\xi_{t|t-1} + K_t (y_t - A'x_t - H'\hat\xi_{t|t-1})$$
$$K_t = F P_{t|t-1} H (H' P_{t|t-1} H + R)^{-1}$$
$$P_{t+1|t} = F [P_{t|t-1} - P_{t|t-1} H (H' P_{t|t-1} H + R)^{-1} H' P_{t|t-1}] F' + Q$$

**s-step-ahead state forecast** [p.384, eq 13.3.25, 27]
$$\hat\xi_{t+s|t} = F^s \hat\xi_{t|t}, \quad P_{t+s|t} = F^s P_{t|t} (F')^s + F^{s-1} Q (F')^{s-1} + \cdots + Q$$

**Kalman log-likelihood** [p.385, eq 13.4.1-2]
$$f(y_t | \cdot) = (2\pi)^{-n/2} |H'P_{t|t-1}H + R|^{-1/2} \exp\left\{-\tfrac{1}{2}(y_t - A'x_t - H'\hat\xi_{t|t-1})'(H'P_{t|t-1}H+R)^{-1}(\cdot)\right\}$$
$$\mathcal{L}(\theta) = \sum_{t=1}^T \log f(y_t | x_t, \mathcal{Y}_{t-1}; \theta)$$

**Steady-state Riccati equation** [p.390, eq 13.5.3]
$$P = F [P - PH(H'PH + R)^{-1} H'P] F' + Q$$

**Kalman smoother** [p.395-397, eq 13.6.11, 16, 20]
$$J_t = P_{t|t} F' P_{t+1|t}^{-1}, \quad \hat\xi_{t|T} = \hat\xi_{t|t} + J_t(\hat\xi_{t+1|T} - \hat\xi_{t+1|t})$$
$$P_{t|T} = P_{t|t} + J_t (P_{t+1|T} - P_{t+1|t}) J_t'$$

### GMM

**GMM objective** [p.412, eq 14.1.11]
$$Q(\theta) = [g(\theta; \mathcal{Y}_T)]' W_T [g(\theta; \mathcal{Y}_T)], \quad g = T^{-1}\sum h(\theta; y_t)$$

**Optimal weighting matrix W = S⁻¹** [p.412, eq 14.1.14]
$$S = \sum_{v=-\infty}^\infty E[h(\theta_0; y_t) h(\theta_0; y_{t-v})']$$

**GMM asymptotic distribution** [p.414-415, eq 14.1.24-25]
$$\sqrt{T}(\hat\theta - \theta_0) \xrightarrow{L} N(0, (D'S^{-1}D)^{-1}), \quad D = E[\partial h/\partial \theta']$$

**Hansen J-test** [p.414-415, eq 14.1.27]
$$J_T = T \cdot Q(\hat\theta_T) \xrightarrow{L} \chi^2(r - a)$$

### Unit Roots

**Random walk** [p.475-476, eq 17.1.1, 17.1.7]
$$y_t = p y_{t-1} + u_t, \; y_0 = 0; \text{ if } p=1: y_t = \sum_{s=1}^t u_s \sim N(0, \sigma^2 t)$$

**Stationary distribution of OLS p** [p.475, eq 17.1.3]
$$\sqrt{T}(\hat p_T - p) \xrightarrow{L} N(0, 1 - p^2)$$

**Dickey-Fuller distribution (Case 1)** [p.488, eq 17.4.7]
$$T(\hat p_T - 1) \xrightarrow{L} \frac{(1/2)\{[W(1)]^2 - 1\}}{\int_0^1 [W(r)]^2 dr}$$

**DF t-statistic (Case 1)** [p.489, eq 17.4.12]
$$t_T \xrightarrow{L} \frac{(1/2)\{[W(1)]^2 - 1\}}{\{\int_0^1 [W(r)]^2 dr\}^{1/2}}$$

**ADF ρ-test** [p.523, formula unlabeled near eq 17.7.34]
$$\frac{T(\hat p_T - 1)}{1 - \hat\zeta_1 - \cdots - \hat\zeta_{p-1}} \xrightarrow{L} \frac{(1/2)\{[W(1)]^2 - 1\} - W(1)\int W(r) dr}{\int [W(r)]^2 dr - [\int W(r) dr]^2}$$

**Phillips-Perron Z_ρ** [p.514, Table 17.2]
$$Z_\rho = T(\hat p_T - 1) - \tfrac{1}{2}(T^2 \hat\sigma_{\hat p}^2 / s_T^2)(\hat\lambda_T^2 - \hat\gamma_{0,T})$$

**Phillips-Perron Z_t** [p.514, Table 17.2]
$$Z_t = (\hat\gamma_0/\hat\lambda^2)^{1/2} (\hat p_T - 1)/\hat\sigma_{\hat p} - \tfrac{1}{2}(\hat\lambda^2 - \hat\gamma_0)(1/\hat\lambda)\{T \hat\sigma_{\hat p}/s_T\}$$

**Newey-West long-run variance estimate** [p.510, eq 17.6.16]
$$\hat\lambda^2 = \hat\gamma_0 + 2 \sum_{j=1}^q [1 - j/(q+1)] \hat\gamma_j$$

### Cointegration

**Error-correction model** [p.580, eq 19.1.42]
$$\Delta y_t = \zeta_1 \Delta y_{t-1} + \cdots + \zeta_{p-1} \Delta y_{t-p+1} + \alpha - B z_{t-1} + \varepsilon_t, \quad z_{t-1} = A' y_{t-1}$$

**Granger representation theorem** [p.582, Prop 19.1] — if Δy_t is I(0) and y_t has h cointegrating vectors, ∃ (h × n) A' with A'π(1) = 0 such that A'y_t is stationary; and ∃ (n × h) B with Φ(1) = BA'.

**Johansen trace test** [p.645]
$$\text{trace stat}(h) = -T \sum_{i=h+1}^n \log(1 - \hat\lambda_i)$$

**Johansen max-eigenvalue test** [p.645]
$$\text{max stat}(h) = -T \log(1 - \hat\lambda_{h+1})$$

### ARCH/GARCH

**ARCH(m)** [p.659, eq 21.1.9-11]
$$u_t = \sqrt{h_t}\, v_t, \; v_t \sim \text{i.i.d.}(0,1), \quad h_t = \zeta + \alpha_1 u_{t-1}^2 + \cdots + \alpha_m u_{t-m}^2$$

**Stationarity condition** [p.659, eq 21.1.7]
$$\sum_{j=1}^m \alpha_j < 1 \text{ with } \alpha_j \geq 0$$

**Unconditional variance** [p.659, eq 21.1.8]
$$\sigma^2 = \zeta/(1 - \alpha_1 - \cdots - \alpha_m)$$

**GARCH(r,m)** [p.665, eq 21.2.3]
$$h_t = \kappa + \delta_1 h_{t-1} + \cdots + \delta_r h_{t-r} + \alpha_1 u_{t-1}^2 + \cdots + \alpha_m u_{t-m}^2$$

**GARCH as ARMA for u²** [p.665-666, eq 21.2.4]
$$u_t^2 = \kappa + \sum_{j=1}^p (\delta_j + \alpha_j) u_{t-j}^2 + w_t - \sum_{j=1}^r \delta_j w_{t-j}, \quad w_t = u_t^2 - h_t$$

**IGARCH condition** [p.667, eq 21.2.5]
$$\sum_{j=1}^r \delta_j + \sum_{j=1}^m \alpha_j = 1$$

**ARCH-M model** [p.667]
$$y_t = x_t'\beta + \delta h_t + u_t, \quad u_t = \sqrt{h_t}\, v_t$$

**EGARCH** [p.668, eq 21.2.7]
$$\log h_t = \kappa + \sum_{j=1}^r \delta_j \log h_{t-j} + \sum_{j=1}^m \alpha_j\{|v_{t-j}| - E|v_{t-j}| + \lambda v_{t-j}\}$$

**GJR-GARCH (threshold)** [p.669, eq 21.2.10]
$$h_t = \kappa + \delta_1 h_{t-1} + \alpha_1 u_{t-1}^2 + \lambda u_{t-1}^2 I_{t-1}, \quad I_{t-1} = \mathbf{1}[u_{t-1} \geq 0]$$

**Gaussian log-likelihood** [p.660, eq 21.1.20]
$$\mathcal{L}(\theta) = -\tfrac{T}{2}\log(2\pi) - \tfrac{1}{2}\sum_t \log h_t - \tfrac{1}{2}\sum_t (y_t - x_t'\beta)^2 / h_t$$

**Engle ARCH-LM test** [p.664]: regress û² on constant + m lags of û²; T·R² ~ χ²(m) under H₀.

**QMLE sandwich variance** [p.663, eq 21.1.25]
$$\sqrt{T}(\hat\theta - \theta) \xrightarrow{L} N(0, D^{-1} S D^{-1})$$

### Markov Switching

**Transition matrix** [p.679, eq 22.2.3] — (N×N), columns sum to 1 [p.678, eq 22.2.2].

**VAR(1) form of Markov chain** [p.679, eq 22.2.6]
$$\xi_{t+1} = P \xi_t + v_{t+1}$$

**Ergodic probability eigenvector** [p.681, eq 22.2.13]
$$P \pi = \pi, \quad 1'\pi = 1$$

**Closed-form solution for ergodic probabilities** [p.684, eq 22.2.26]
$$\pi = (A'A)^{-1} A' e_{N+1}, \quad A = \begin{bmatrix} I_N - P \\ 1' \end{bmatrix}$$

**Two-state ergodic probability** [p.683]
$$P\{s_t = 1\} = \pi_1 = \frac{1 - p_{22}}{2 - p_{11} - p_{22}}$$

**Long-run limit** [p.681, eq 22.2.14]
$$\lim_{m\to\infty} P^m = \pi \cdot 1'$$

**Hamilton filter update** [p.692, eq 22.4.5]
$$\hat\xi_{t|t} = \frac{\hat\xi_{t|t-1} \odot \eta_t}{1'(\hat\xi_{t|t-1} \odot \eta_t)}$$

**Hamilton filter forecast** [p.692, eq 22.4.6]
$$\hat\xi_{t+1|t} = P \cdot \hat\xi_{t|t}$$

**Log-likelihood via Hamilton filter** [p.692, eq 22.4.7-8]
$$\mathcal{L}(\theta) = \sum_{t=1}^T \log[1'(\hat\xi_{t|t-1} \odot \eta_t)]$$

**Kim smoother** [p.694, eq 22.4.14]
$$\hat\xi_{t|T} = \hat\xi_{t|t} \odot \{P' \cdot [\hat\xi_{t+1|T} (\div) \hat\xi_{t+1|t}]\}$$

**MLE of transition probability** [p.694, Hamilton 1990]
$$\hat p_{ij} = \frac{\sum_{t=2}^T P\{s_t = j, s_{t-1} = i | \mathcal{Y}_T; \theta\}}{\sum_{t=2}^T P\{s_{t-1} = i | \mathcal{Y}_T; \theta\}}$$

## 4. Algoritmos e Pseudocódigo

**Kalman Filter (forward pass)** [ch.13, p.381-384]
```
Input: F, Q, A, H, R; data {y_t, x_t} for t = 1..T
Initialize:
    xi_hat[1|0] = 0                                    # or analyst's best guess
    vec(P[1|0]) = [I - F⊗F]^{-1} vec(Q)                # stationary initialization
For t = 1..T:
    y_hat[t|t-1] = A' x_t + H' xi_hat[t|t-1]
    Sigma_y      = H' P[t|t-1] H + R
    K_t          = F P[t|t-1] H Sigma_y^{-1}
    xi_hat[t+1|t] = F xi_hat[t|t-1] + K_t (y_t - y_hat[t|t-1])
    P[t+1|t]     = F [P[t|t-1] - P[t|t-1] H Sigma_y^{-1} H' P[t|t-1]] F' + Q
    L           += log phi(y_t ; y_hat[t|t-1], Sigma_y)
Return {xi_hat[t|t-1], P[t|t-1], L}
```

**Kalman Smoother (backward pass)** [ch.13, p.395-397]
```
Input: filter outputs {xi_hat[t|t], xi_hat[t+1|t], P[t|t], P[t+1|t]}, matrix F
Initialize: xi_hat[T|T] (from forward pass)
For t = T-1 downto 1:
    J_t        = P[t|t] F' P[t+1|t]^{-1}
    xi_hat[t|T] = xi_hat[t|t] + J_t (xi_hat[t+1|T] - xi_hat[t+1|t])
    P[t|T]     = P[t|t]      + J_t (P[t+1|T] - P[t+1|t]) J_t'
```

**Hamilton Filter (regime switching)** [ch.22, p.692-694]
```
Input: transition matrix P (NxN), conditional densities f(y_t | s_t=j, ...), start xi[1|0]
For t = 1..T:
    eta_t = [f(y_t | s_t=j, x_t, Y_{t-1}; theta) for j = 1..N]   # density vector
    num   = xi_hat[t|t-1] * eta_t                                # Hadamard product
    xi_hat[t|t]   = num / (1' num)
    L            += log(1' num)
    xi_hat[t+1|t] = P * xi_hat[t|t]
Return {xi_hat[t|t], xi_hat[t+1|t], L}
```

**Kim Smoother (regime switching)** [ch.22, p.694]
```
Input: filter outputs, transition matrix P
For t = T-1 downto 1:
    ratio       = xi_hat[t+1|T] / xi_hat[t+1|t]   # element-wise
    xi_hat[t|T] = xi_hat[t|t] * (P' * ratio)     # Hadamard product
```

**Dickey-Fuller Test (Case 2, with constant)** [ch.17, p.490-493]
```
Input: series y_1..y_T
Run OLS: y_t = alpha + rho y_{t-1} + u_t
rho_stat = T * (rho_hat - 1)            # compare to Table B.5 Case 2
t_stat   = (rho_hat - 1) / se(rho_hat)  # compare to Table B.6 Case 2
# 5% critical values (Case 2), Table B.5: T=50 → -13.3; T=100 → -13.7; T=250 → -14.0; T=∞ → -14.1
# Example 17.4 [p.489] uses -13.8 (interpolated for T=168); t-stat 5% ≈ -2.89 (Table B.6 Case 2).
If rho_stat < crit_rho(T) or t_stat < -2.89: reject H0 (unit root)
```

**Augmented Dickey-Fuller (ADF)** [ch.17, p.527]
```
Input: series y_1..y_T, lag order p
Run OLS: y_t = zeta_1 Delta_y_{t-1} + ... + zeta_{p-1} Delta_y_{t-p+1} + alpha + rho y_{t-1} + eps_t
# Two alternative test statistics:
rho_adj = T * (rho_hat - 1) / (1 - zeta_1_hat - ... - zeta_{p-1}_hat)
t_stat  = (rho_hat - 1) / se(rho_hat)  # unchanged critical values, Table B.6 Case 2
F_stat  = (usual F for H0: alpha=0 and rho=1)   # Table B.7 Case 2
```

**Phillips-Perron Test** [ch.17, p.510-514]
```
# Run same regression as DF Case 2: y_t = alpha + rho y_{t-1} + u_t
gamma_hat_j = (1/T) sum_{t=j+1}^T u_t u_{t-j}  for j = 0..q
lambda_sq_hat = gamma_hat_0 + 2 * sum_{j=1}^q [1 - j/(q+1)] * gamma_hat_j   # Newey-West
Z_rho = T*(rho_hat - 1) - 0.5 * (T^2 * se(rho_hat)^2 / s^2) * (lambda_sq_hat - gamma_hat_0)
Z_t   = (gamma_hat_0 / lambda_sq_hat)^0.5 * (rho_hat - 1) / se(rho_hat) \
        - 0.5*(lambda_sq_hat - gamma_hat_0)/lambda_hat * (T * se(rho_hat)/s + lambda_hat)
# Compare to Tables B.5 / B.6 Case 2
```

**GARCH(1,1) MLE (Gaussian)** [ch.21, p.660]
```
Input: data {y_t, x_t}, starting values (beta, kappa, delta, alpha)
For each proposed theta = (beta, kappa, delta, alpha):
    h_0 = Var(OLS residuals)
    For t = 1..T:
        h_t     = kappa + delta * h_{t-1} + alpha * (y_{t-1} - x_{t-1}' beta)^2
        log_L_t = -0.5*log(2*pi) - 0.5*log(h_t) - 0.5*(y_t - x_t' beta)^2 / h_t
    L = sum(log_L_t)
Maximize L s.t. kappa > 0, alpha >= 0, delta >= 0, alpha + delta < 1
Report QMLE sandwich SEs: (D_T)^{-1} S_T (D_T)^{-1} / T     # eq 21.1.25
```

**Johansen Cointegration Test (VECM rank)** [ch.20, p.635-647]
```
Input: (n x 1) vector series y_1..y_T, VECM lag p
# Stage 1: concentrate out short-run dynamics
Regress Delta y_t on (1, Delta y_{t-1}, ..., Delta y_{t-p+1}) -> residuals R0_t
Regress y_{t-1}   on (1, Delta y_{t-1}, ..., Delta y_{t-p+1}) -> residuals R1_t
S00 = (1/T) sum R0_t R0_t'
S01 = (1/T) sum R0_t R1_t'
S10 = S01'
S11 = (1/T) sum R1_t R1_t'
# Stage 2: generalized eigenvalue problem
Solve |lambda * S11 - S10 S00^{-1} S01| = 0
Order eigenvalues lambda_1 >= ... >= lambda_n
trace_stat(h) = -T * sum_{i=h+1}^n log(1 - lambda_i)        # H0: rank <= h
max_stat(h)   = -T * log(1 - lambda_{h+1})                   # H0: rank = h vs rank = h+1
Compare to Osterwald-Lenum (1992) critical values
```

## 5. Regras de Trading Explícitas

This is an econometrics textbook — "rules" are methodological imperatives for valid inference that downstream protect trading:

- **REGRA [p.307-308]**: NEVER interpret Granger-causality as structural causality when forward-looking variables (stock prices, interest rates, FX rates) are involved. Hamilton's stock-price example: prices Granger-cause dividends even though dividends causally determine prices — forward-looking expectations reverse the sign.
- **REGRA [p.527, p.513]**: For ADF test, use UNCHANGED Case-2 t-critical values (−2.89 at 5%) regardless of how many lagged Δy are included. For Phillips-Perron Newey-West lag use $q \approx \lambda T^{1/5}$.
- **REGRA [p.668]**: For equity return volatility modeling, prefer EGARCH(1,1) or GJR-GARCH over plain GARCH(1,1) — the leverage effect (λ < 0) is empirically robust.
- **REGRA [p.666, p.671]**: GARCH(1,1) is typically parsimonious enough for financial returns; higher-order (r, m) rarely improves out-of-sample forecasts. Engle-Hong-Kane-Noh (1991), West-Edison-Cho (1993) confirm.
- **REGRA [p.671]**: Compare ARCH/GARCH specifications out-of-sample via squared-residual loss — Pagan-Schwert (1990) show parametric models (GARCH, EGARCH) beat nonparametric kernels for forecasting despite worse in-sample fit.
- **REGRA [p.561, p.591]**: Do NOT run OLS of one I(1) series on another without first testing for cointegration — spurious regression gives divergent t-statistics.
- **REGRA [p.386]**: For ARMA(p,q) MLE use Kalman filter for EXACT likelihood evaluation (eq 13.4.1-2). Works even when MA part is non-invertible; avoids bias of conditional likelihood.
- **REGRA [p.386, p.389]**: Always parameterize variance-covariance Ω in MLE via its Cholesky factor for numerical stability.
- **NEVER [p.322]**: Report a single orthogonalized IRF without declaring the Cholesky ordering — IRFs depend on ordering, and a theory-free ordering is indefensible.
- **NEVER [p.660]**: Assume fourth moments exist when α₁ < 1 in Gaussian ARCH(1) — need α₁² < 1/4 (equivalently α₁ < 1/2) for 4th moment finiteness — Hamilton [p.660]: "This equation has no real solution for A whenever α₁² ≥ ¼".
- **NEVER [p.659, p.663]**: Report Gaussian MLE standard errors for GARCH without checking whether v_t is actually Gaussian. Financial returns are not. Use QMLE sandwich variance (D⁻¹SD⁻¹).

## 6. Pitfalls e Anti-patterns

- [p.487-488] Under H₀: p = 1, √T(p̂ − 1) → 0 in probability (not a normal distribution). Must scale by T. Applying stationary-AR inference to unit-root data is INVALID.
- [p.516] Phillips-Perron tests have POOR SIZE when the true process has negative MA (θ ≈ −0.8); Schwert (1989), Kim-Schmidt (1990) document false rejections of unit-root null.
- [p.513] No unique rule for Newey-West lag q: too small underestimates long-run variance; too large loses power. Andrews (1991) data-driven rules may help.
- [p.489, Example 17.3] Dickey-Fuller has LOW POWER — with T = 168 quarterly observations cannot distinguish p = 1 from p = 0.95. Need long samples.
- [p.557-561] Granger-Newbold (1974) spurious regression: independent random walks regressed on each other produce "significant" t-statistics by random chance. Test cointegration first.
- [p.322] Orthogonalized IRF depends ENTIRELY on Cholesky ordering — no unique "causal" decomposition without theory.
- [p.387-388] State-space models are generically UNIDENTIFIED without restrictions. Symptom: non-invertible information matrix at optimum. Test local identification via Rothenberg (1971).
- [p.383-384] Kalman filter for MA(1) gives IDENTICAL likelihood for (θ, σ²) and (θ⁻¹, θ²σ²) — invertibility must be imposed exogenously.
- [p.388] Caines (1988) asymptotic consistency of state-space MLE requires (i) identified model, (ii) eigenvalues of F inside unit circle, (iii) x_t asymptotically covariance-stationary full-rank, (iv) θ₀ not on boundary of parameter space.
- [p.665] Nelson-Cao (1992): nonneg α_j, δ_j are SUFFICIENT but not NECESSARY for h_t > 0. Needlessly restricting loses flexibility.
- [p.667] IGARCH (Σδ + Σα = 1) has infinite unconditional variance — forecast MSE diverges at long horizons. Not covariance-stationary.
- [p.660] Gaussian ARCH still produces non-Gaussian unconditional distribution of u_t — fatter-than-Normal tails. Fitting Gaussian v_t leaves kurtosis > 3 in u_t.
- [p.305, p.307-309] Granger-causality tests are highly sensitive to lag length p and to how nonstationarity is treated — Feige-Pearce (1979), Christiano-Ljungqvist (1988), Stock-Watson (1989).
- [p.680, p.684] Reducible or periodic Markov chains lose ergodicity. Check that estimated P̂ has exactly one unit eigenvalue and rest strictly inside unit circle.
- [p.695] Optimal forecast of y in regime-switching model is NONLINEAR in observables even though each regime admits linear representation.
- [p.444] Do NOT difference a TREND-STATIONARY series — the result $\Delta y_t = \delta + (1 - L)\psi(L)\varepsilon_t$ introduces a unit root into the moving average representation, yielding a noninvertible process.
- [p.660] Imposing stationarity (Σα < 1) and nonnegativity (α_j ≥ 0) simultaneously in ARCH estimation is hard — typically use small m or ad-hoc parametric structure.
- [p.689] Mixture-density log-likelihood has singularities (µ_j = y_i with σ²_j → 0 makes L → ∞) and multiple local maxima. Standard practice: ignore the singularity and try again with different starting values.

## 7. Parâmetros Sensíveis

- **Newey-West truncation q** [p.513]: Phillips's result requires $q_T \to \infty$ with $q_T/T^{1/4} \to 0$ (e.g., $q_T = \lambda T^{1/5}$). Under- or over-smoothing both degrade test size/power.
- **VAR lag order p** [p.297]: Sims (T − k) correction reduces small-sample bias. Hamilton's examples use 4 lags for quarterly data; 6-12 for monthly. Economic theory should inform lower bound.
- **GARCH orders (r, m)** [p.666]: Empirical consensus — (1, 1) nearly always adequate for financial returns. Higher-order GARCH rarely improves out-of-sample forecasts [p.671].
- **EGARCH leverage parameter λ** [p.668]: Economically motivated (equity deleveraging amplifies volatility on negative returns). Typically λ ∈ (−1, 0) for stocks — NOT curve-fitted.
- **ARCH-M risk premium δ** [p.667]: Has theoretical support from asset-pricing theory. Often statistically insignificant — weak empirical evidence for strong risk-return linkage.
- **Regime count N in Markov switching** [p.691]: Hamilton's (1989) business-cycle model uses N = 2 (expansion/recession). More regimes invite overfitting and identification issues — keep N small unless theory demands otherwise.
- **Cointegrating rank h** [p.645-647, Tables B.10/B.11]: Tested via Johansen likelihood-ratio statistics — trace test $-T\sum_{i=h+1}^n \log(1-\hat\lambda_i)$ [eq 20.3.4] compared against Case 1-3 sections of Table B.10, and max-eigenvalue $-T\log(1-\hat\lambda_{h+1})$ [eq 20.3.7] compared against Table B.11. Hamilton's Italy/US exchange-rate example [p.647-648] shows the two tests can disagree at adjacent ranks — no default selection rule given in Hamilton.
- **Kalman initial state covariance P_{1|0}** [p.378]: For stationary models, use unconditional variance vec(P_{1|0}) = [I − F⊗F]⁻¹ vec(Q). For nonstationary / unknown initial state, use large diagonal "diffuse" prior.
- **ARCH lag length m** [p.660]: Typically small (1-5) for financial returns. Too large m → nonnegativity constraints bind, likelihood surface becomes degenerate.

## 8. Citações Literais Importantes

> "Granger's reason for proposing this definition was that if an event Y is the cause of another event X, then the event Y should precede the event X. Although one might agree with this position philosophically, there can be serious obstacles to practical implementation of this idea using aggregate time series data" — [p.303]

> "A VAR can be viewed as the reduced form of a general dynamic structural model." — [p.327]

> "The results of any empirical test for Granger causality can be surprisingly sensitive to the choice of lag length (p) or the methods used to deal with potential nonstationarity of the series." — [p.305]

> "In the absence of restrictions on F, Q, A, H, and R, the parameters of the state-space representation are unidentified — more than one set of values for the parameters can give rise to the identical value of the likelihood function, and the data give us no guide for choosing among these." — [p.387]

> "Granger-causality tests for such series may be useful for assessing the efficient markets view or investigating whether markets are concerned with or are able to forecast GNP or inflation, but should not be used to infer a direction of causation." — [p.307]

## 9. Conexões com Outros Livros Desta Base

- **GARCH / VAR overlap with `fin_time_series_tsay.md`** — Tsay (*Analysis of Financial Time Series*, 3rd ed.) covers the same GARCH family (ARCH, GARCH, EGARCH, GJR) and VAR estimation with substantially more applied R-code examples and recent financial applications. Use Tsay for applied implementation and empirical insight, Hamilton for theoretical foundation (asymptotics, proofs, identification theory). Hamilton Ch 21 ≈ Tsay Ch 3; Hamilton Ch 11 ≈ Tsay Ch 8; Hamilton Ch 10 overlaps Tsay's multivariate chapters.
- **Kalman Filter / Numerical methods in `numerical_recipes.md`** — Numerical Recipes gives practical implementations of matrix factorizations (Cholesky, QR, SVD) and numerical optimization (BFGS, Nelder-Mead, Levenberg-Marquardt) needed to turn Hamilton's MLE equations into running code. The steady-state Riccati equation (eq 13.5.3) and nonlinear search algorithms referenced in Hamilton Ch 5 and Ch 21 for ARCH MLE benefit from NR-style solvers; Kalman propagation benefits from NR's numerically stable triangular solves.
- **ML methods on time series in `advances_fin_ml.md`** — López de Prado addresses many of the same concerns as Hamilton (nonstationarity, overfitting on financial data, spurious correlation) but from a machine-learning perspective: fractional differentiation (preserving memory while achieving stationarity) directly responds to Hamilton's Ch 15-17 dilemma between trend-stationary and unit-root treatment. Hamilton Ch 17 unit-root tests are López de Prado's classical benchmark for his fractionally-differentiated stationarity procedure. CPCV / purged cross-validation handle the dependency issues raised by Hamilton's asymptotic theory in a way agnostic to specific parametric models — complementary, not redundant.
