# Machine Trading: Deploying Computer Algorithms to Conquer the Markets

## Metadata
- **Autor:** Ernest P. Chan [copyright p.6]
- **Ano:** 2017 [p.6]
- **Editora:** John Wiley & Sons, Inc. [p.6]
- **Páginas:** 267 (PDF), printed body ends around p.242
- **ISBN:** 978-1-119-21960-6 (Hardcover) [p.6]; 978-1-119-21967-5 (ePDF); 978-1-119-21965-1 (ePub)
- **Foco principal:** Third book in Chan's trilogy; applies factor models, time-series techniques, AI/ML, options, intraday microstructure and bitcoin strategies with MATLAB examples.

## 1. Tese Central

Chan's thesis in this volume [Preface, p.ix-xii] is that quantitative traders should augment classical hypothesis-driven strategy development with data-driven techniques (factor models, state-space models, and ML), but constantly guard against overfitting because "financial data are not only quite limited (unless we use tick data), they are also not very stationary in the statistical sense. That is, the probability distribution of returns does not stay constant forever. If we just turn our machine learning algorithms loose on these data, it is very easy to come up with trading rules that worked extremely well in certain past periods, but fail terribly going forward" [p.83-84, ch.4]. The book is a continuation of *Quantitative Trading* (Chan 2009) and *Algorithmic Trading* (Chan 2013), covering topics omitted there: factor models, time-series (ARIMA/VAR/SSM), AI techniques with overfit reduction, options strategies, intraday microstructure, and bitcoins [Preface, p.ix-x].

Recurring principle: "in trading, complexity doesn't pay" [p.115, ch.4 summary] — start with the simplest technique (stepwise regression) and only escalate (neural nets, deep SVM kernels) if simpler approaches fail.

## 2. Conceitos-Chave

- **CAGR (Compound Annual Growth Rate)** — return assuming constant leverage, profits re-compounded; contrasts with average annualized return [p.12]
- **Calmar ratio** — CAGR divided by absolute value of the max drawdown over the most recent **three years**; preferred by Chan over MAR (which uses entire-history max DD) [p.13-14]. Chan trades strategies with backtest Calmar ≥ 1 [p.14]
- **Kelly optimal leverage** — mean of excess returns / variance of excess returns [p.13]; equivalently, for a portfolio: $F^* = C^{-1}M$ [p.19-20]
- **Tangency portfolio / Markowitz efficient frontier** — portfolio maximizing Sharpe ratio; same solution as Kelly (up to leverage normalization) [p.18-20]
- **Minimum variance portfolio / risk parity** — allocations that avoid reliance on return forecasts; allocate capital inversely to volatility for risk parity [p.22]
- **Time-series factor** — varies in time, same value across stocks (e.g., market return, HML, SMB, UMD/WML) [p.29-30]
- **Cross-sectional factor loading** — varies across stocks, observable fundamentally (e.g., P/E, ROE, BM) [p.33]
- **Fama-French factors** — market excess return, HML, SMB; Chan shows they fail to predict next-day SPX stock returns out-of-sample [p.31-32]
- **Implied Vol / Skew / Kurt (option-implied moments)** — Vol = (CIV(0.5)+PIV(-0.5))/2; Skew = CIV(0.25)-PIV(-0.25); Kurt = CIV(0.25)+PIV(-0.25)-CIV(0.5)-PIV(-0.5), all with 30-day tenor [p.41-42]
- **Put-call deviation VS** — weighted open-interest avg of (IV_call - IV_put) across strikes/expirations; positive values predict positive stock returns [p.45-46]
- **Volatility smirk / skew** — OTM-put IV minus ATM-call IV; high skew predicts negative future returns [p.46]
- **Short Interest Ratio (SIR) vs Days-To-Cover (DTC)** — DTC = shares shorted / avg daily volume; DTC is a better return predictor than SIR [p.48]
- **Statistical factors via PCA** — diagonalize returns covariance; eigenvectors become factor loadings [p.49-50]
- **AR(p), ARMA(p,q), ARIMA(p,d,q)** — linear time-series models; coefficients fit by maximum-likelihood; p and q selected by BIC [p.60-65]
- **VAR(p) / VEC(q)** — multivariate autoregressive and error-correction forms; VEC lets you model ΔY with both ΔY and Y as regressors [p.67-69]
- **State Space Model (SSM) / Kalman filter** — hidden state x(t) = A·x(t-1)+B·u(t); observables y(t) = C·x(t)+D·ε(t) [p.71]
- **Stepwise regression** — linear regression with automatic feature selection via AIC/BIC/SSE [p.87]
- **Regression tree / Classification tree** — hierarchical splits minimizing variance (regression) or Gini Diversity Index (classification) [p.89-91, p.98]
- **Cross-validation / Bagging / Random Subspace / Random Forest / Boosting** — overfit-reduction ensemble techniques [p.85, p.92-97]
- **Gini's Diversity Index (GDI)** — $1 - p_+^2 - p_-^2$ for binary classification [p.98]
- **Support Vector Machine (SVM)** — hyperplane separating classes, maximizing margin; kernel functions for nonlinearity [p.99-101]
- **Hidden Markov Model (HMM)** — unsupervised learning with transition matrix T and emission matrix E; trained via EM algorithm [p.101-104]
- **Feed-forward Neural Network** — linear combinations of sigmoids $S(x)=1/(1+e^{-x})$ [p.105-106]
- **Data normalization for ML aggregation** — divide each stock's predictors and response by its return volatility so data from different stocks can be pooled [p.109-110]
- **Delta-neutral options strategies** — portfolios with zero aggregate delta; intended to isolate volatility/theta exposure [p.119-120]
- **Gamma scalping** — long straddle hedging a mean-reversion strategy on the underlying; path-dependent profit from oscillation around strike [p.137-140]
- **Dispersion trading** — short index options vs long single-name options; bet on correlation [p.156-157, ch.5]
- **GARCH(p,q)** — conditional variance model [p.126-127]
- **Bollinger Band mean-reversion** — buy when price < MA − k·MSTD, sell when > MA + k·MSTD [p.204-205, ch.7]
- **Order flow** — signed transaction volume (+s for buy market orders, -s for sell market orders) [p.186]
- **Toxic flow / Adverse selection** — order flow generated by highly informed traders that penalizes passive liquidity providers [p.177-178, p.696-697 endnotes]
- **VPIN (Bulk Volume Classification)** — Easley, Lopez de Prado, O'Hara (2015) technique to infer order flow using price change + volume per bar [p.186, ch.6]
- **NBBO / Order Protection Rule (Reg NMS Rule 611)** — market orders must route to exchange with best displayed quote [p.164]
- **Hide-and-Light / ISO order types** — specialized limit order modifiers used by HFTs to secure queue priority and rebates [p.164-165]
- **Primary-exchange auction price vs consolidated close** — backtests using SIP-consolidated close can inflate mean-reversion PnL by ~8bps white noise [Box 6.2, p.183]

## 3. Fórmulas / Equações

**Kelly optimal leverage (single strategy)** [p.13]

$$\text{Optimal leverage} = \frac{\text{Mean of Excess Returns}}{\text{Variance of Excess Returns}}$$

Chan warns this is typically too aggressive in practice due to fat tails; a one-day -20% shock (Black Monday 1987) would wipe out equity at Kelly=5 [p.13].

**Kelly optimal portfolio allocation** [p.19-20]

$$F^* = C^{-1} M$$

Where $C$ is the covariance matrix of returns and $M$ is the column vector of expected returns. This allocation simultaneously maximizes compound growth rate and Sharpe ratio (up to a leverage constant) [p.19-20, Box 1.3].

**Mean log-return vs net-return relation (Ito's Lemma limit)** [p.15, eq. 1.1]

$$\mu \approx m - \frac{s^2}{2}$$

**Max compound growth rate in terms of Sharpe** [p.20]

$$\text{Max compound growth} = \frac{S^{*2}}{2}$$

**Markowitz quadratic programming problem** [Box 1.2, p.17-18]

$$\min F^T C F \quad \text{subject to } F \geq 0 \text{ and } F^T M = m$$

**Factor model (descriptive / explanatory)** [eq. 2.1, p.29]

$$R(t,s) - r_F = \alpha(t,s) + \beta_1(s) \cdot F_1(t) + \beta_2(s) \cdot F_2(t) + \cdots + \varepsilon(t,s)$$

**Factor model (predictive — time t+1)** [eq. 2.2, p.30]

$$R(t+1,s) - r_F = \alpha(s) + \beta_1(s) \cdot F_1(t) + \beta_2(s) \cdot F_2(t) + \cdots + \varepsilon(t,s)$$

**ROE factor (Chattopadhyay/Lyle/Wang two-factor model)** [p.37]

$$ROE(i,s) = 1 + X(i,s) / Book(i-1, s)$$

The two-factor model uses $\log(ROE)$ and $\log(BM)$ as loadings [p.37-38].

**Implied moments for long-short portfolio** [p.42]

$$\text{Vol} = \frac{CIV(0.5) + PIV(-0.5)}{2}$$
$$\text{Skew} = CIV(0.25) - PIV(-0.25)$$
$$\text{Kurt} = CIV(0.25) + PIV(-0.25) - CIV(0.5) - PIV(-0.5)$$

All with 30-day tenor [p.41-42].

**Put-call volatility deviation factor VS** [p.45-46]

$$VS(t,s) = \sum_j w_j(t,s) \left[ IV^{call}_j(t,s) - IV^{put}_j(t,s) \right]$$

Where $w_j$ is avg open interest for the j-th option pair. Long top-quintile / short bottom-quintile weekly yields unlevered CAGR ~12.4% in-sample [p.46].

**AR(p) model** [eq. 3.2, p.60]

$$Y(t) = \mu + \phi_1 Y(t-1) + \phi_2 Y(t-2) + \cdots + \phi_p Y(t-p) + \varepsilon(t)$$

Weakly stationary iff $|\phi|<1$ in AR(1) [p.60]. BIC minimization selects p.

**ARMA(p,q) model** [eq. 3.3, p.63]

$$Y(t) = \mu + \sum_{i=1}^p \phi_i Y(t-i) + \varepsilon(t) + \sum_{j=1}^q \theta_j \varepsilon(t-j)$$

**VEC(q) model (vector error correction)** [eq. 3.5, p.69]

$$\Delta Y(t) = M + C Y(t-1) + A_1 \Delta Y(t-1) + \cdots + A_k \Delta Y(t-k) + \varepsilon(t)$$

C is the error-correction matrix; its eigenvalues link to the Johansen cointegration test [p.70].

**State Space Model** [eq. 3.6-3.7, p.71]

$$x(t) = A(t) \cdot x(t-1) + B(t) \cdot u(t)$$
$$y(t) = C(t) \cdot x(t) + D(t) \cdot \varepsilon(t)$$

**Sector-neutral VAR allocation** [eq. 3.4, p.69]

$$w_i = \frac{r_i - \langle r \rangle}{\sum_j |r_j - \langle r \rangle|}$$

**Gini's Diversity Index (classification tree split criterion)** [p.98]

$$GDI = 1 - p_+^2 - p_-^2$$

**Sigmoid activation (neural network)** [p.105]

$$S(x) = \frac{1}{1 + e^{-x}}$$

**GARCH(p,q) model** [eq. 5.1, p.126]

$$r_t = \sigma_t \epsilon_t, \quad \sigma_t^2 = \omega + \sum_{i=1}^p \alpha_i \sigma_{t-i}^2 + \sum_{i=1}^q \beta_i r_{t-i}^2$$

Chan reports sign-of-vol-change accuracy of 66% on SPY, 67% USO, 59% GLD, 60% AAPL, 62% EURUSD [p.127].

## 4. Algoritmos e Pseudocódigo

**BIC-based model selection (AR/ARMA)** [p.61, ch.3]

```
for p in 1..MAX_P:
  for q in 1..MAX_Q:
    model = arima(p, 0, q)
    logL = estimate(model, trainset)
    LOGL[p,q] = logL
    PQ[p,q]  = p + q
# bic penalizes n_params via +1 for constant
[_, bic] = aicbic(flatten(LOGL), flatten(PQ)+1, len(trainset))
(p*, q*) = argmin(bic)
```

**Regression tree stopping rules** [p.89]

```
split(node):
  if no_variance_reduction(node): return
  if size(node) < MinParentSize: return
  if any_child(node).size < MinLeafSize: return
  if total_splits >= MaxNumSplits: return
  pick predictor and threshold minimizing child-variance sum
  recurse on children
```

**Cross-validation for overfit-reduction** [p.92]

```
divide trainset into K subsets
for i in 1..K:
  model_i = train(trainset \ subset_i)
  loss_i  = evaluate(model_i, subset_i)
pick model with min loss
```

**Bagging (bootstrap aggregation)** [p.93-94]

```
for k in 1..K:
  bag_k = sample trainset of size N WITH REPLACEMENT
  model_k = train(bag_k)
  oob_k   = trainset \ bag_k  # out-of-bag points
prediction = average(model_k.predict(x) for k in 1..K)
```

**Boosting (LSBoost gradient descent for regression trees)** [p.96-97]

```
residual = y
for m in 1..M:
  tree_m = train(X, residual)
  pred_m = tree_m.predict(X)
  residual = residual - pred_m
final = sum(pred_m for m in 1..M)  # or weighted
```

**HMM next-day emission prediction** [p.104]

```
pstates[1..t] = hmmdecode(observations[1..t], T, E)
pstates[t+1] = T' @ pstates[t]
pemis[t+1]   = E' @ pstates[t+1]
```

**Data normalization for ML aggregation across stocks** [p.109-110]

```
for each stock s:
  ret1_N[s] = ret1[s] / vol1[s]
  ret2_N[s] = ret2[s] / vol1[s]
  ...
  retFut1_N[s] = retFut1[s] / vol1[s]
X = reshape(ret1_N, ret2_N, ... to one long column per feature)
Y = reshape(retFut1_N)
train one model on all stocks' aggregated data
```

**Order-book reconstruction from ITCH-like messages** [Example 6.2, p.178-181]

```
initialize buyOrderBook, sellOrderBook (binary search trees)
for each event in chronological order:
  if WORKING_CONFIRMED:
    insert(price, size) into matching tree
    update best_bid / best_ask if improved
  elif CANCEL_CONFIRMED or (PARTIAL_)FILL_CONFIRMED:
    locate order; decrement size or delete
    if deleted order was the best, pop next-best from tree
```

**Bulk Volume Classification (VPIN) for order flow** [ch.6, p.186, Box 6.4]

```
# reference: Easley, Lopez de Prado, O'Hara (2015)
per bar (equal-volume buckets):
  use sign(price_change) weighted by standardized return
  to split bar volume into buy-initiated vs sell-initiated fractions
order_flow = buy_vol - sell_vol
```

## 5. Regras de Trading Explícitas

- **REGRA [p.14]**: trade strategies with backtest **Calmar ratio ≥ 1** (CAGR / |3-year max DD|).
- **REGRA [p.13]**: "lower the leverage until you are comfortable with the maximum drawdown in the backtest over a period that includes several financial crises." Kelly optimal leverage is typically too aggressive.
- **REGRA [p.12]**: in backtests, set **leverage = 1**; measure returns as P&L divided by gross market value.
- **REGRA [p.60-61, ch.3]**: test on **midprices** (not trade prices) to avoid phantom mean-reversion from bid-ask bounce.
- **REGRA [p.115]**: "start with the simplest technique (such as stepwise regression) and proceed to the most complicated (such as neural network) if the simpler techniques do not yield good performance. In trading, complexity doesn't pay."
- **REGRA [p.86-87, ch.4]**: always split data into train/test halves; never use the entire set for fitting.
- **REGRA [p.93, ch.4]**: when using cross-validation on ~1,000-row financial datasets, prefer **K=5** over K=10 (small out-of-sample folds yield large statistical errors).
- **REGRA [p.94, ch.4]**: for bagging on limited financial data, avoid large K (e.g., K>5-10); averaging many bags converges to same overfit as single full-data model.
- **REGRA [p.108, ch.4]**: for a feed-forward NN on small financial data (SPY, ~1000 rows × 4 features) use only **one hidden layer with one neuron**; more layers/neurons degrade OOS.
- **REGRA [p.109-110]**: when aggregating stocks for ML, **normalize predictors AND response by volatility** first (dividing by recent vol); omission drops Sharpe from 0.9 to -0.4.
- **REGRA [p.14, Chan 2013 convention]**: fix Calmar-ratio DD window to **most recent 3 years** to avoid dependence on backtest length.
- **REGRA [p.197-198, ch.5 options]**: prefer **delta-neutral** options strategies; if you want delta exposure, trade the underlying (lower transaction cost).
- **REGRA [ch.6, p.183, Box 6.2]**: when backtesting open/close stock strategies, use **primary-exchange auction prices**, not SIP-consolidated open/close; the ~8bps white-noise difference can inflate mean-reversion PnL fictitiously.
- **REGRA [p.159-160, ch.6]**: for intraday strategies use **compiled languages (C++, C#, Java)**, not scripting (MATLAB/R/Python), due to ~10x latency difference.
- **REGRA [p.161, ch.6]**: reduce all three latencies: order-submission, order-status, market-data. Rent VPS at Equinix NY4 or NJ1 colocated with broker; use direct exchange feeds where budget allows.
- **REGRA [p.183, ch.6]**: to avoid slippage/market-impact blow-up, order size must respect NBBO size (AAPL's is typically only ~189 shares).
- **REGRA [p.12 Chan 2013 + p.202, ch.7]**: for bitcoin trading, remember ~45% of exchanges fail due to thefts/hacks — credit risk, not just market risk.
- **REGRA [p.12, p.196]**: to avoid catastrophic leverage loss (e.g., CHF flash 2015), trade via **limited-liability vehicle** (LLC, S-corp, LP) not personal name.
- **REGRA [p.3-4, ch.1]**: use **survivorship-bias-free data** (CRSP, CSI delisted, Bloomberg) — ordinary Yahoo/Quandl default daily stock series will embed survivorship bias.
- **NUNCA [p.13]**: use naive Kelly leverage on financial assets — Gaussian assumption breaks under tail events.
- **NUNCA [p.22]**: target equal **volatility** per asset in a risk-parity portfolio without considering that "volatility isn't what we should be afraid of — tail risk is." Target equal **max drawdown** instead.
- **NUNCA [p.108, ch.4]**: use large numbers of hidden layers and neurons for small financial datasets — overfitting dominates.
- **NUNCA [p.97, ch.4]**: rely on boosting to fight overfitting — Chan shows boosting increases trainset Sharpe dramatically while test-set Sharpe stays insignificant.

## 6. Pitfalls e Anti-patterns

- **[p.32, Example 2.1]** Fama-French factors fit in-sample with CAGR 242% / Sharpe 3.7 but produce NEGATIVE OOS returns — classic overfit of explanatory factors used as predictors.
- **[p.37, Example 2.2]** Throwing all 112 fundamental factors blindly yields in-sample $R^2 = 0.96$ and CAGR 48%, but NEGATIVE test-set CAGR. Using only 27 size-independent factors yields 12% OOS CAGR.
- **[p.43, Example 2.4]** Out-of-sample results do NOT replicate for published strategies (Bali 2015 obtained 9.68% CAGR on all optionable stocks; Chan reports ~0% on SPX subset) — small/restricted universes kill many factor strategies.
- **[p.47-49, ch.2]** Published return-predicting factors decay over time (SIR, Ibbotson liquidity, put-call VS all diminished in recent years). **[p.48]** DTC factor-loading sign reversed since 2012.
- **[p.76-79, ch.3 SSM]** Overfitting by Kalman-filter strategies: training-set cumulative return > 250% but test-set nearly flat on EWC-EWA pair; regime change and over-estimation of B covariance.
- **[p.91-92, ch.4]** Using every leaf of a regression tree for prediction boosted in-sample CAGR to 73% but dropped OOS to -7.2% — overfit.
- **[p.97, ch.4 boosting]** Figure 4.7 shows Sharpe on train rising to 8 while test Sharpe remains near zero — boosting does NOT mitigate overfitting for financial data.
- **[p.108, ch.4]** Increasing NN layers/neurons increases in-sample but degrades OOS (Tables 4.1, 4.2).
- **[p.133, ch.5]** Short straddle strategy backtest is "very flimsy evidence" — only one year of data.
- **[p.159-160, ch.6]** Intraday strategy with holding minutes can become impossible at scale: ES NBBO is only ~$30M per touch, AAPL only 189 shares.
- **[p.183, ch.6, Box 6.2]** 8bps white-noise difference between consolidated and primary-exchange close creates "significant but fictitious excess return" for mean-reversion strategies.
- **[p.184, ch.6]** Algoseek / CQG datasets miss trade ticks — backtests using them silently lose end-of-day auction prices.
- **[p.109, ch.4]** Training ML on ~1,000 rows × 4 columns is inadequate; typical ML problems have millions of rows × hundreds of predictors.
- **[Preface, p.xi]** "Most, if not all, the strategies I describe contain hidden biases in one way or another, waiting for you to unearth and eliminate." Every strategy in the book is prototype, NOT production-ready.
- **[p.181-182, ch.6 dark pools]** Dark pools can be toxic: informed traders quote-ping on primary exchange to drive midprice, then execute in dark pool against stale resting orders. Even IEX-style speed-bump pools don't fully eliminate this.
- **[p.125-128, ch.5 vol prediction]** Being able to predict direction of realized-vol change doesn't yield profits on VXX/XIV — VXX has negative theta and reflects a rolling options portfolio, not pure implied vol.

## 7. Parâmetros Sensíveis

- **Calmar ratio lookback = 3 years** [p.14]: economic justification, normalizes max DD across backtest lengths. Not curve-fit.
- **K=5 for K-fold CV on 1000-row financial data** [p.93]: not curve-fit — justified by trade-off between train size and OOS statistical robustness.
- **MinLeafSize=100 in regression tree on SPY** [p.90]: chosen "to avoid overfitting"; Chan explicitly states smaller values hurt OOS.
- **Options tenor = 30 days for implied-moment factors** [p.42, p.43]: published convention; Chan cites Sinclair (2016) that the IV-delta ratio is "independent of tenor", so not a sensitive tuning parameter.
- **Moneyness ranges (OTM put 0.8-0.95, ATM call 0.95-1.05)** [p.46-47]: published convention from Zhang/Zhao/Xing (2008).
- **Top-30%/30%/30% triple sort for Bali-Hu-Murray** [p.42]: published convention; out-of-sample on SPX stocks yields ~0% CAGR (the factor was overfit to broader universe).
- **1% grid for Gamma scalping entries** [p.139]: Chan flags this as a parameter "to be optimized" — NOT economically justified. Curve-fit risk.
- **N=1 contract hedge for gamma scalping** [p.139]: "arbitrarily chosen"; negative PnL — Chan explicitly treats as free parameter.
- **5% OTM strangle width for hedging CL** [p.140]: economically justified (caps CL loss at 4%); not curve-fit.
- **Weekly trade window Thursday-Friday for gamma scalping CL** [p.138]: partially economically justified (avoids weekend theta, NOPA/API release days).
- **Entry at 9:00 ET day after Weekly Petroleum Status Report** [p.133-135]: seasonal economic event, not curve-fit.
- **VAR lag p=1 for industry-group cointegrating stocks** [p.67]: selected by BIC; "this is a typical result for most industry groups" — justified, not arbitrary.
- **holdingDays = 63 (quarterly) for fundamental cross-section** [p.35, p.113]: justified by quarterly earnings cycle; not curve-fit.
- **NN retraining ensemble = 100 networks** [p.107]: justified by need to escape random-init local minima; Chan invites readers to run more.
- **Kelly fractional leverage = Chan explicitly recommends LESS than full Kelly** [p.13]: economically justified.
- **Calmar ratio target for 1-factor ROE small-caps = 0.97** [p.141, example 5.1 XIV/SPY Kalman]: reported, not parameter.

## 8. Citações Literais Importantes

> "If we just turn our machine learning algorithms loose on these data, it is very easy to come up with trading rules that worked extremely well in certain past periods, but fail terribly going forward." — [p.83-84, ch.4]

> "Start with the simplest technique (such as stepwise regression) and proceed to the most complicated (such as neural network) if the simpler techniques do not yield good performance. In trading, complexity doesn't pay." — [p.115, ch.4]

> "Most, if not all, the strategies I describe contain hidden biases in one way or another, waiting for you to unearth and eliminate." — [Preface, p.xi]

> "Volatility isn't what we should be afraid of — tail risk is." — [p.22, ch.1]

> "Nobody should trade someone else's strategies without a thorough, independent backtest, removing all likely sources of biases and data errors, and adding various variations for improvement." — [Preface, p.xi]

> "I have found that Kelly's leverage is typically too high to be of practical use." — [p.13, ch.1]

## 9. Conexões com Outros Livros Desta Base

- **Kelly leverage and portfolio optimization** — core formula $F^* = C^{-1}M$ [p.19-20] is also treated in `leverage_space.md` (Ralph Vince, with 2D drawdown-geometric-mean surface) and `quant_trading_chan.md` (Chan's own introduction to Kelly in book 1).
- **CPCV and purging techniques for overfit reduction** — Chan's K-fold CV treatment [p.92-94] is less rigorous than the Combinatorial Purged CV and Deflated Sharpe described in `advances_fin_ml.md#cpcv`. Use López de Prado for leakage control.
- **Kalman filter / state-space models** — SSM treatment [ch.3, p.71-79] extends Chan (2013) and complements `time_series_hamilton.md` (which gives the theoretical derivation of the Kalman recursions) and `rocket_science.md` / `cybernetic_analysis.md` (Ehlers uses similar linear adaptive filters for DSP-style indicators).
- **ARIMA/ARMA/VAR** — `time_series_hamilton.md` gives the rigorous derivations; Chan here focuses on practical MATLAB econometric toolbox calls.
- **Factor models (Fama-French, HML, SMB)** — also discussed in `ml_for_asset_managers.md` (López de Prado) and `evidence_based_ta.md` (Aronson on data-snooping bias in factor research).
- **Mean-reversion on pairs (EWA/EWC)** — same pair used in `quant_trading_chan.md` and Chan (2013); Kalman variation here refines hedge-ratio estimation.
- **Overfitting framework and in-sample vs OOS** — central theme aligns with `evidence_based_ta.md` (Aronson: "no rule works unless replicated OOS") and `advances_fin_ml.md` (López de Prado: backtest overfitting is the primary risk).
- **Volatility prediction (GARCH)** — applicable methodology in `time_series_hamilton.md` (theoretical) and `regime_change.md` (regime-switching extensions beyond GARCH).
- **Risk parity and minimum variance portfolio** — also treated in `systematic_trading.md` (Carver) with different parameterization.
- **Machine learning general framework** — significantly overlaps with `ml_for_asset_managers.md` (López de Prado); Chan is more MATLAB-how-to, López de Prado more theoretical and production-grade.
- **Microstructure / order flow / VPIN** — `trading_exchanges.md` (Harris) is the canonical reference for market microstructure; Chan summarizes key issues (order types, hide-and-light, ISO, Reg NMS Rule 611) at a more trader-practical level.
- Cross-ref to Chan's own book 2 (`algo_trading_chan`) — not yet in this knowledge base; Chan repeatedly references Chan (2013) for Kalman pairs, cointegration, Johansen test, and survivorship-bias handling.
