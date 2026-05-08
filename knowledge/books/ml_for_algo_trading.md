# Machine Learning for Algorithmic Trading (Second Edition)

## Metadata
- **Author:** Stefan Jansen [p.i, cover]
- **Year:** 2020 [preface, p.xv]
- **Publisher:** Packt Publishing [p.iii]
- **Pages:** 821 (PDF) / ~770 printed [metadata]
- **ISBN:** 978-1-83921-771-5 [p.xxi]
- **Main focus:** End-to-end ML4T workflow — sourcing data, engineering alpha factors, training/tuning supervised & unsupervised models, deep learning and reinforcement learning agents, and backtesting with Zipline/backtrader [preface p.xiii-xx].

## 1. Core Thesis
ML for trading is not a standalone exercise but an integrated workflow: **source → features → model → portfolio → backtest** [preface p.xiii-xiv; ch.1 p.13]. The book's recurring claim is that ML adds value to *multiple* steps of strategy design, but requires careful domain expertise and anti-overfit discipline because (a) financial data has low signal-to-noise ratio, (b) competitive markets make factor alpha decay — published anomalies lose ~25% excess return from discovery to publication and >50% after publication [ch.1 p.15-16], and (c) backtest overfitting from multiple testing is the field's dominant pitfall [ch.8 p.227; ch.23 p.718].

The practical synthesis: the **Fundamental Law of Active Management** frames skill (information coefficient) × breadth (independent bets) as the route to a positive information ratio [ch.5 p.124], while López de Prado's purged CV, embargoing, deflated Sharpe, and combinatorial walk-forward address the overfitting problem [ch.6 p.169; ch.8 p.227].

## 2. Main Concepts
- **Alpha factor** — transformation of raw market/fundamental/alternative data that outputs a single predictive value per asset at each evaluation time [ch.4 p.82]. 250+ published factors as of 2015, growing ~40/year [ch.4 p.83].
- **Information Coefficient (IC)** — Spearman rank correlation between factor predictions and forward returns; values of 0.05–0.15 allow significant outperformance with sufficient breadth [ch.4 p.115-116; ch.5 p.124].
- **Information Ratio (IR)** — alpha ÷ tracking error; Fundamental Law approximates IR ≈ IC × √breadth [ch.5 p.124].
- **Sharpe Ratio (SR)** — expected excess return / std of excess return; convert frequencies by multiplying by √(ratio of periods). For non-IID returns, Lo's adjustment applies [ch.5 p.123].
- **Deflated Sharpe Ratio** — adjusts SR for multiple testing, non-normal returns, and short samples [ch.8 p.227].
- **Look-ahead bias** — using information before it was historically available; most insidious source is restated fundamentals [ch.8 p.223-224].
- **Survivorship bias** — backtesting on universe of currently-active tickers only [ch.8 p.224].
- **Point-in-time (PIT) data** — data reflecting only what was known at that timestamp; non-negotiable for valid backtests [ch.1 p.13; ch.8 p.223-224].
- **Purging / Embargoing** — remove training samples whose evaluation window overlaps a validation sample (purge) and those immediately following a test period (embargo) [ch.6 p.169].
- **Combinatorial Purged CV (CPCV)** — compute all train/test combinations over N groups with purge+embargo to generate many historical paths [ch.6 p.169].
- **Factor decay** — published factors' excess returns drop ~25% discovery→publication, >50% post-publication [ch.1 p.15-16].
- **Stationarity** — constant mean/variance/autocorrelation over time; required by ARIMA/VAR; achieved via differencing and log-transform [ch.9 p.260-262].
- **Cointegration** — linear combination of non-stationary series is stationary → basis for pairs trading [ch.9 p.277-280].
- **GARCH(p,q)** — ARMA(p,q) model of the error variance; for volatility forecasting [ch.9 p.275].
- **Bagging (bootstrap aggregation)** — reduce variance by averaging predictions of models trained on bootstrap samples; core of random forests [ch.11 p.327-328].
- **Boosting** — sequentially train weak learners on residuals of prior models [ch.12 p.369-371].
- **SHAP values** — game-theoretic attribution of predictions to features; central for interpreting gradient boosting models [ch.1 p.17; ch.23 p.719].
- **Markov Decision Process (MDP)** — mathematical framing for RL: states, actions, rewards, transition probabilities, discount factor γ<1 [ch.22 p.685].
- **Tick / time / volume / dollar bars** — alternative aggregations of raw trade data; dollar bars adjust for price level changes (stock splits, large moves) and produce more normally distributed returns than time bars [ch.2 p.35-40].
- **Nasdaq ITCH / TotalView** — exchange-native direct market-data protocol allowing full order-book reconstruction; ITCH v5.0 declares 20+ message types [ch.2 p.27-35].
- **Alternative-data 3 V's** — Volume, Velocity, Variety; key differentiators vs. traditional sources [ch.3 p.60-61].
- **Alt-data evaluation criteria (4)** — signal content (alpha), data quality, latency, legal/reputational risk (GDPR) [ch.3 p.65-69].
- **Eigenportfolios** — normalized principal components of the return covariance matrix used as portfolio weights; PC1 typically mirrors "the market" [ch.13 p.425].
- **Hierarchical Risk Parity (HRP)** — Prado (2016) method that clusters the correlation matrix and allocates weights top-down using recursive inverse-variance bisection [ch.13 p.434-435].
- **Bayesian Sharpe ratio** — models returns as Student-t (fat tails) with prior on mean/std/ν via PyMC3; yields a full posterior distribution of SR, not a point estimate [ch.10 p.317-319].
- **Gaussian-random-walk coefficients** — Bayesian rolling regression: α_t ~ N(α_{t-1}, σ²) and β_t ~ N(β_{t-1}, σ²) produce a time-varying hedge ratio for pairs trading [ch.10 p.320-321].
- **LDA (Latent Dirichlet Allocation)** — hierarchical Bayesian generative topic model; documents are Dirichlet mixtures of topics, topics are Dirichlet mixtures of words [ch.15 p.471-473].
- **Topic coherence (UMass/UCI)** — metrics that score LDA topic semantic quality based on word co-occurrence probabilities; values closer to zero imply higher coherence [ch.15 p.474].
- **word2vec (CBOW vs skip-gram)** — shallow NN learning dense (typically 300-d) word embeddings; CBOW trains faster on frequent words, skip-gram works better with small datasets and rare words [ch.16 p.485].
- **Negative sampling (NEG)** — approximation to softmax that trains word2vec 45× faster than hierarchical softmax with similar convergence [ch.16 p.486].
- **doc2vec (DBOW / DM)** — extends word2vec to produce embeddings for entire documents/paragraphs [ch.16 p.503].
- **BERT / attention / transformers** — bidirectional pretraining with 12–24 attention layers replaces recurrence; fine-tuned for downstream NLP tasks (e.g., sentiment) [ch.16 p.513-515].
- **CNN convolutional layer** — applies learnable filters (kernels) via sliding dot product; three stages: convolution → detector (non-linearity) → pooling (downsampling) [ch.18 p.555-557].
- **CNN-TA (Sezer & Ozbayoglu 2018)** — encodes 15 technical indicators × 15 lookback intervals into a 15×15 "image" classified by a CNN as buy/hold/sell; tested on Dow 30 + 9 ETFs 2007-2017 [ch.18 p.595-596].
- **LSTM / GRU** — gated RNN units designed to mitigate vanishing gradients and retain long-range memory [ch.19 p.591-592].
- **Conditional autoencoder (Gu-Kelly-Xiu 2020)** — left FFNN maps P asset characteristics → K factor loadings (β); right AE maps returns → K latent factors; product predicts next-period returns [ch.20 p.658-660].
- **TimeGAN (Yoon et al. 2019)** — combines 4 networks (embedder, recovery, generator, discriminator) + supervisor and a moment-matching loss to generate synthetic multivariate financial time series [ch.21 p.668-670].

## 3. Formulas / Equations
**Sharpe Ratio** [ch.5 p.123]

$$\text{SR} \equiv \frac{\mu(R^e)}{\sigma(R^e)}, \quad R^e = R - R_f$$

Frequency adjustment: monthly→annual multiply by $\sqrt{12}$; daily→monthly by $\sqrt{21}$ [ch.5 p.123].

**Information Ratio and Fundamental Law** [ch.5 p.124]

$$\text{IR} = \frac{\text{Alpha}}{\text{Tracking Error}} \approx \text{IC} \cdot \sqrt{\text{breadth}}$$

**Kelly Criterion (binary bets)** [ch.5 p.133]

$$f^* = \frac{bp + p - 1}{b} = \frac{bp - q}{b}$$

Where $b$ = payout odds, $p$ = probability of win, $q = 1-p$. Many investors use **Half-Kelly** to reduce volatility [ch.5 p.133].

**Multi-asset Kelly (Chan 2008)** [ch.5 p.133]

$$\mathbf{f}^* = \Sigma^{-1} \boldsymbol{\mu}$$

Equivalent to the (potentially levered) maximum-Sharpe portfolio from mean-variance optimization [ch.5 p.133].

**CAPM** [ch.7 p.188]

$$E[r_i] = \alpha_i + r_f + \beta_i(E[r_m] - r_f)$$

**Fama–French 5-factor** uses Mkt-RF, SMB (size), HML (value), RMW (profitability), CMA (investment) [ch.7 p.190-191].

**RSI** [ch.4 p.86]

$$\text{RSI} = 100 - \frac{100}{1 + \overline{\Delta p_{up}} / \overline{\Delta p_{down}}}$$

Default lookback 14 periods; >70 overbought, <30 oversold [ch.4 p.86].

**Ridge / Lasso regularization** [ch.7 p.195]

Ridge: $\min \|y - X\beta\|_2^2 + \lambda \|\beta\|_2^2$ and Lasso: $\min \|y - X\beta\|_2^2 + \lambda \|\beta\|_1$. λ chosen via cross-validation; Lasso can drive coefficients to exactly zero (sparse selection) [ch.7 p.195].

**ARIMA(p, d, q)** combines AR(p), d differencing steps, and MA(q). Requires stationarity; SARIMAX extends with seasonal + exogenous terms [ch.9 p.266-271].

**ARCH(p)** [ch.9 p.272]

$$\text{var}(x_t) = \sigma_t^2 = \omega + \sum_{i=1}^p \alpha_i \epsilon_{t-i}^2$$

**GARCH(p, q)** extends ARCH with ARMA structure on variance [ch.9 p.273]. Workflow: fit ARMA to mean; test residuals for ARCH effects via ACF/PACF of squared residuals; jointly estimate mean+volatility; diagnose [ch.9 p.274].

**Bayes' theorem (posterior)** [ch.10 p.297]

$$P(\theta | X) = \frac{P(X | \theta) \, P(\theta)}{P(X)}$$

Posterior = prior × likelihood / evidence; the evidence is often intractable, motivating MAP, MCMC (e.g., NUTS), or variational inference (ADVI) approximations [ch.10 p.298-305].

**Bayesian rolling regression (pairs hedge ratio)** [ch.10 p.320-321]

$$\alpha_t \sim \mathcal{N}(\alpha_{t-1}, \sigma_\alpha^2), \quad \beta_t \sim \mathcal{N}(\beta_{t-1}, \sigma_\beta^2)$$

Implemented in PyMC3 as `pm.GaussianRandomWalk`; trained via NUTS with target_accept=0.9 for difficult posteriors [ch.10 p.321].

**LDAvis relevance** [ch.15 p.476]

$$r(w, t | \lambda) = \lambda \log p(w|t) + (1-\lambda) \log \frac{p(w|t)}{p(w)}$$

User studies recommend λ = 0.6 for most plausible topic interpretations [ch.15 p.476].

**Perplexity (LDA)** [ch.15 p.474]

$$2^{H(p)} = 2^{-\sum_w p(w) \log_2 p(w)}$$

Lower is better; used together with UMass/UCI coherence [ch.15 p.474].

**Bellman Equation (RL)** [ch.22 p.686]

$$v_\pi(s) = \mathbb{E}_\pi[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t=s]$$

Figure 22.2 illustrates the recursive relationship. For continuing (non-episodic) tasks the discount factor γ must be strictly < 1 to avoid infinite returns [ch.22 p.685-686].

## 4. Algorithms and Pseudocode
**ML4T Workflow** [preface p.xiii; ch.1 p.12-15; ch.6 p.153]

Step A — Frame problem: define target metric (return forecast, direction, class) [ch.6 p.155].
Step B — Source data: market + fundamental + alternative, PIT-correct [ch.1 p.13].
Step C — Engineer features (alpha factors): momentum, value, quality, volatility [ch.4 p.82-93].
Step D — Train/tune ML model with cross-validation respecting time-series order [ch.6 p.167-169].
Step E — Translate predictions → portfolio weights (sizing, risk constraints) [ch.5 p.126-135].
Step F — Backtest with Zipline/backtrader; track risk metrics mark-to-market [ch.8 p.223-230].
Step G — Evaluate via Sharpe / IR / deflated SR / pyfolio tearsheet [ch.5 p.123; ch.8 p.227].
Step H — Paper-trade, then live, with continuous monitoring for factor decay [ch.23 p.719].

**TimeSeriesSplit walk-forward CV** [ch.6 p.167-168]

```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(X):
    # train_set strictly precedes test_set
    # optional max_train_size for rolling (vs expanding) window
    ...
```

**Purged / Embargoed / Combinatorial CV** [ch.6 p.169]

```
Input: dataset D, n_splits, n_test_splits, purge_window, embargo_pct
for each combination C of n_test_splits groups from N:
    train_set = D \ C
    purged = remove_overlapping(train_set, C, purge_window)
    embargoed = apply_embargo(purged, embargo_pct)
    model = train(embargoed)
    scores.append(evaluate(model, C))
return distribution(scores)
```

**Nasdaq ITCH order-book reconstruction** [ch.2 p.28-35]

```
Parse ITCH v5.0 binary feed using message-type specs
For each message:
    if message adds / replaces / cancels an order:
        update in-memory order book (by price level)
    elif message is an execution:
        record trade
Persist state iteratively to HDF5 (9 GB typical single-day)
```

Output: full limit-order-book snapshot per ticker, aggregate trades → tick/time/volume/**dollar bars** [ch.2 p.35-40].

**AlgoSeek minute-bar pipeline** [ch.2 p.41-43]

Load 1-min CSV zips → convert to daily `.parquet` → combine → HDF5 (53.8M records / 3.2 GB covering 5y × 100 tickers in the sample) [ch.2 p.42-43]. Bars include NBBO-based OHLC, VWAP, bid/ask, dark-pool volume, up/down-tick counts.

**EDGAR XBRL PIT-correct fundamentals** [ch.2 p.52-56]

Download SEC Financial-Statement-and-Notes (FSN) quarterly ZIPs → parse SUB, TAG, NUM, DIM tables → by CIK retrieve filings → adjust pre-split EPS (e.g. Apple pre-2014-06-04 ÷ 7) → rolling 4-quarter TTM EPS → join with adjusted prices to compute trailing P/E [ch.2 p.55-56].

**Web-scraping alt-data with Selenium + Splash** [ch.3 p.73-78]

Use `requests + BeautifulSoup` for static HTML; headless Firefox via Selenium to execute JavaScript; Scrapy + Splash for scalable crawling. Demonstrated to build a 10,000-restaurant OpenTable NYC booking dataset and to scrape earnings-call transcripts from SeekingAlpha [ch.3 p.72-79].

**Volatility Model (GARCH) Build Procedure** [ch.9 p.274]

Step A — Fit ARMA(p, q) to returns; inspect ACF/PACF to choose p, q [ch.9 p.274].
Step B — Test residuals for ARCH effects via ACF/PACF of squared residuals [ch.9 p.274].
Step C — If significant, jointly fit mean + GARCH(p, q); evaluate AIC/BIC [ch.9 p.274].
Step D — Validate: standardized residuals should look like white noise [ch.9 p.274].
Step E — Out-of-sample: rolling 10-year window, 1-step forecast, minimize RMSE vs realized squared deviations (example: GARCH(2,2) on NASDAQ) [ch.9 p.275-276].

**Pairs Trading via Cointegration** [ch.9 p.280-283]

Step A — Select candidate pairs by sector, fundamentals, or broad universe [ch.9 p.282].
Step B — Test each pair for cointegration via Engle-Granger two-step OR Johansen procedure [ch.9 p.281-282].
Step C — Keep pairs with stable, high-variance spreads for more trading opportunities [ch.9 p.283].
Step D — Model the spread as mean-reverting, e.g., Ornstein-Uhlenbeck [ch.9 p.283].
Step E — Entry when spread deviation exceeds threshold (e.g., 2σ); exit on return to mean [ch.9 p.283].

**Bayesian Sharpe Ratio (PyMC3)** [ch.10 p.317-318]

```python
with pm.Model() as sharpe_model:
    mean = pm.Normal('mean', mu=mean_prior, sd=std_prior)
    std  = pm.Uniform('std', lower=std_low, upper=std_high)
    nu   = pm.Exponential('nu_minus_two', 1/29) + 2   # t dof => fat tails
    returns = pm.StudentT('returns', nu=nu, mu=mean, sd=std, observed=data)
    sharpe = mean / std * np.sqrt(252)
    pm.Deterministic('sharpe', sharpe)
    trace = pm.sample(draws=25000, chains=4)   # NUTS
```

Produces full posterior of SR — enables effect-size comparison of two return series [ch.10 p.318-319].

**Hierarchical Risk Parity (HRP) — Prado 2016** [ch.13 p.434-435]

```
1. Compute asset-return correlation ρ; distance d = sqrt(0.5*(1 - ρ))
2. Hierarchical clustering on d (e.g., single linkage) → linkage_matrix
3. Quasi-diagonalize covariance by the cluster order
4. Recursive bisection:
    for each pair of sub-clusters (c0, c1):
        v0 = inverse-variance weighted variance of c0
        v1 = inverse-variance weighted variance of c1
        weights[c0] *= 1 - v0/(v0+v1)
        weights[c1] *= v0/(v0+v1)
```

Benchmarked against Mean-Variance (MV) and Equal-Weight (EW) on a Zipline ML strategy: Sharpe MV = 1.16, EW = 1.01, HRP = 0.83 — but HRP uses no return forecasts and is more robust to estimation error [ch.13 p.438].

**Factor Research (Zipline + Alphalens)** [ch.4 p.107-118]

```python
class MeanReversion(CustomFactor):
    inputs = [Returns(window_length=MONTH)]
    window_length = YEAR
    def compute(self, today, assets, out, monthly_returns):
        df = pd.DataFrame(monthly_returns)
        out[:] = df.iloc[-1].sub(df.mean()).div(df.std())

alphalens_data = get_clean_factor_and_forward_returns(
    factor=factor_data, prices=prices,
    periods=(5, 10, 21, 42), quantiles=5)
```

Outputs include mean-return-by-quantile, IC time series, and factor turnover [ch.4 p.112-118].

**LightGBM training recipe** [ch.12 p.390-400]

Use leaf-wise growth (not depth-wise) for faster convergence at higher overfit risk [ch.12 p.397]. Control `num_leaves` plus `max_depth` carefully [ch.12 p.398]. Use early_stopping on a held-out validation set — never the test set — and limit the number of trials to avoid validation-set overfitting [ch.12 p.373]. GOSS (gradient-based one-side sampling) provides speed on large datasets [ch.12 p.399]. Exclusive Feature Bundling reduces sparse-feature dimensionality [ch.12 p.399]. Apply SHAP values for interpreting predictions [ch.12 p.394].

**LDA topic modeling (Gensim)** [ch.15 p.476-478]

```python
from gensim.models import LdaModel
lda = LdaModel(corpus=train_corpus, num_topics=15, id2word=id2word,
               passes=25, alpha='symmetric')
lda.top_topics(corpus=train_corpus, coherence='u_mass')
```

On 700 earnings-call transcripts (22,582 statements, 1,529-word vocab) a 15-topic model surfaced themes such as clinical trials (topic 5), China/tariffs (topic 9), and tech issues (topic 11) [ch.15 p.479]. Coherence degrades after 25–30 topics and perplexity rises in parallel [ch.15 p.480].

**word2vec for SEC 10-Ks (Gensim skip-gram)** [ch.16 p.501-502]

```python
model = Word2Vec(sentences,
                 sg=1,            # 1=skip-gram, 0=CBOW
                 hs=0,            # 0=negative sampling, 1=hierarchical softmax
                 size=300,        # embedding dim
                 window=3,        # context window
                 min_count=50,
                 negative=10,
                 alpha=0.025, min_alpha=0.0001)
```

Corpus: 22,000 10-K filings 2013–2016 (6,500 companies); 11,000 filings label-joined with 1-month post-filing returns [ch.16 p.499-500]. Sweep results: skip-gram > CBOW; negative sampling > hierarchical softmax; context window < 5 degrades; larger vectors help — size=600 achieves best analogy accuracy at 38.5% [ch.16 p.502].

**CNN-TA time-series-as-image** [ch.18 p.595-596]

```
For each trading day:
    Compute 15 technical indicators (RSI, MACD, Bollinger, ...) × 15 lookback intervals
    Arrange as 15×15 grid, ordered by hierarchical clustering of mutual information
    Feed to CNN classifier → {buy, hold, sell}
```

Replicates Sezer & Ozbayoglu (2018) on Dow 30 + 9 most-traded ETFs, 2007–2017 [ch.18 p.595].

**Stacked LSTM for weekly stock-return classification** [ch.19 p.605-609]

```
Inputs: 52 weeks of lagged weekly returns + one-hot month + ticker embedding
Architecture: LSTM(25, dropout=0.2, return_sequences=True)
           → LSTM(10, dropout=0.2)
           → concat with ticker_embedding + month dummies
           → Dense → sigmoid
Data: ~2,500 tickers with complete history
```

Test AUC = 0.6816, test accuracy ≈ 58%, IC (prediction vs actual weekly return) = 0.32; top-vs-bottom quintile weekly spread ≈ 20 bps [ch.19 p.609].

**Conditional Autoencoder for asset pricing (GKX 2020)** [ch.20 p.658-662]

```
LEFT branch (beta network):
  Input: N stocks × P characteristics   → FFNN with hidden layer
                                        → output K factor loadings per stock (beta)
RIGHT branch (factor network):
  Input: individual stock returns       → autoencoder → K latent factors
OUTPUT:
  predicted return_{i,t} = dot(beta_i, factor_t)
Loss: MSE on reconstructed returns
```

Produces significant quintile-portfolio spread and positive long-short cumulative return on an unseen period [ch.20 p.671-672].

**TimeGAN (Yoon et al. 2019)** [ch.21 p.668-670, 676-678]

```
Components:
  embedder  : real   X → latent H        (autoencoder half 1)
  recovery  : latent H → reconstructed X (autoencoder half 2)
  generator : noise Z → latent H_hat
  discriminator: latent H/H_hat → real/fake
  supervisor: enforces stepwise transition dynamics in latent space
Training phases:
  1) embedder + recovery reconstruction loss
  2) supervised loss (next-latent-state prediction)
  3) joint adversarial + supervised + moment-matching loss
Evaluation:
  - PCA & t-SNE visualization for diversity
  - Discriminative score (test-set classifier real-vs-synthetic) for fidelity
  - TSTR (Train-on-Synthetic, Test-on-Real) sequence-prediction error for usefulness
```

Demonstrated on 15 years of Google OHLCV (6 features, 24 timesteps) [ch.21 p.668].

**Deep Q-Learning Trading Agent** [ch.22 p.679-681]

Define environment via OpenAI Gym with state = features (prices, technicals, position), actions = {buy, hold, sell}, reward = incremental PnL (optionally risk-adjusted) [ch.22 p.681-682]. Build deep Q-network approximating Q(s, a) [ch.22 p.680]. Train with experience replay plus target network [ch.22 p.680]. Use epsilon-greedy exploration decaying over training [ch.22 p.680]. Backtest on unseen period before deploying [ch.22 p.680; ch.23 p.719].

## 5. Explicit Trading Rules
- **RULE [ch.1 p.13; ch.8 p.223-224]**: Use ONLY point-in-time (PIT) data; synchronize reported financials with actual publication dates (e.g., EPS quarterly vs. prices daily). Failure produces positive backtests that collapse in live trading.
- **RULE [ch.2 p.55]**: When joining fundamentals with adjusted prices, back-adjust pre-split EPS by the split ratio (e.g., Apple pre-2014-06-04 EPS ÷ 7); use 4-quarter rolling sums for TTM metrics.
- **RULE [ch.2 p.39]**: Prefer **dollar bars** (or volume bars) over time bars in backtests; tick-return normality tests fail at vanishingly small p-values, and dollar bars remain comparable across splits and price-regime changes.
- **RULE [ch.3 p.66-67]**: Score every alternative dataset on (1) signal content / alpha, (2) data quality (gaps, biases), (3) latency between event and delivery, (4) legal/reputational risk including GDPR. Skip datasets that fail any dimension.
- **RULE [ch.3 p.66]**: Prefer alt-data whose signals show low (< 5%) correlation with traditional risk premia (value, momentum, quality); they add diversification value even when standalone Sharpe is weak.
- **RULE [ch.8 p.224]**: Include delisted/bankrupt/acquired tickers in backtest universe. Excluding them is survivorship bias and inflates results.
- **RULE [ch.5 p.133]**: Use fractional Kelly (typically Half-Kelly) for position sizing. Full Kelly is optimal only with perfect parameter knowledge; real estimates have noise.
- **RULE [ch.4 p.86]**: For momentum, use 12-month return EXCLUDING the most recent month (skip-a-month) to avoid short-term reversal contamination.
- **RULE [ch.5 p.124]**: Target IC of 0.05–0.15 combined with high breadth. A single high-IC signal with low breadth underperforms many weak uncorrelated signals.
- **RULE [ch.6 p.167-169]**: Use `TimeSeriesSplit` (walk-forward), not random K-fold, for time-series data. For overlapping labels, add purging + embargoing.
- **RULE [ch.8 p.227]**: Report the number of trials run during strategy search; adjust Sharpe via the deflated SR formula before concluding.
- **RULE [ch.8 p.227]**: 2 years of daily data supports conclusions about at most ~7 strategy variants; 5 years supports ~45. Running more trials without more data equals overfitting.
- **RULE [ch.9 p.274]**: For volatility models, jointly estimate mean + GARCH structure rather than sequentially — sequential estimation understates uncertainty.
- **RULE [ch.10 p.318-319]**: Compare strategies via posterior distribution of the **difference** in Sharpe ratios (Bayesian SR), not point-estimate Sharpe differences; it gives a probability that one strategy is truly superior.
- **RULE [ch.11 p.327-334]**: For random-forest trading models, control `max_depth`, `min_samples_split`, `min_samples_leaf`. Default trees overfit financial data.
- **RULE [ch.12 p.373]**: When using early stopping with gradient boosting or deep networks, keep a separate hold-out test set; never use the test set as the stopping-criterion validation set or you leak information.
- **RULE [ch.12 p.373]**: Even with a proper validation set, running a large number of early-stopped trials overfits to the validation set itself — keep trial counts modest.
- **RULE [ch.13 p.438]**: HRP typically underperforms MV in Sharpe (0.83 vs 1.16 in the book's ML benchmark) but is robust to correlation-matrix estimation error; prefer HRP when return forecasts are unreliable.
- **RULE [ch.17 p.514-515]**: Neural networks require combined regularization (L1/L2 + dropout + early stopping) — deep models overfit low-signal financial data easily.
- **RULE [ch.15 p.476]**: When interpreting LDA topics with pyLDAvis, set relevance λ ≈ 0.6 (user-study optimum); stop increasing topic count when coherence plateaus (typically 25–30 for financial news).
- **RULE [ch.16 p.502]**: For word2vec on financial corpora, use skip-gram + negative sampling, `min_count ≥ 50`, window ≥ 5, and embedding size 300–600; CBOW and hierarchical softmax underperform.
- **RULE [ch.23 p.719]**: Before going live, always run paper-trading in a staged manner. Never go straight from backtest to capital deployment.
- **NEVER [ch.8 p.225-226]**: Backtest trades executing at the close-price of the same bar that generated the signal. Use next-bar open (or intraday with latency).
- **NEVER [ch.23 p.716]**: Design strategies by "letting the data speak" (pure data mining). Prioritize economically-motivated hypotheses; test a limited set.

## 6. Pitfalls and Anti-patterns
- [ch.8 p.223-224] **Look-ahead bias** from restated fundamentals, retroactive splits, incorrect EPS/price alignment.
- [ch.8 p.224] **Survivorship bias** — only using currently-tradable universe.
- [ch.8 p.225] **Outlier mis-treatment** — winsorizing extreme values that are actually realistic market events.
- [ch.8 p.225] **Unrepresentative sample period** — training set may lack important market-regime aspects (e.g. volatility or volume regimes) or include too few/too many extreme events; mitigate by covering multiple regimes or augmenting with synthetic data.
- [ch.8 p.225-226] **Ignoring transaction costs and slippage** — small per-trade costs compound and kill high-turnover strategies.
- [ch.8 p.226] **Short-sale / leverage assumptions** not available in reality (borrow constraints, margin).
- [ch.8 p.226] **Mis-timing signals vs. execution** — using close-price signals executed at close (impossible live).
- [ch.8 p.226-227] **Multiple-testing / p-hacking**: selecting among many variants on same data inflates best-variant Sharpe.
- [ch.8 p.227] **Ignoring backtest overfitting** inherited from prior knowledge of what worked in others' published research.
- [ch.6 p.167] **IID assumption violation** — applying standard K-fold to serially-correlated financial data leaks future into past.
- [ch.6 p.169] **Overlapping labels** (e.g., 5-day returns with daily observations) create train-test contamination unless purged.
- [ch.11 p.334] **Not tuning tree hyperparameters** — default decision trees overfit tabular financial data.
- [ch.12 p.373] **Early stopping using the test set** leaks test information into training decisions; use a separate validation set.
- [ch.12 p.373] **Running thousands of early-stopped trials** on the same validation set overfits to *that* validation set even though the test set is held out; the effective number of independent experiments is far smaller than the trial count.
- [ch.13 p.413] **Applying PCA to fat-tailed return data** — PCA assumes normality and will underweight higher-order moments; consider robust / non-linear alternatives (ICA, autoencoders).
- [ch.16 p.499-500] **Using generic pretrained vectors (GloVe-Wikipedia) on domain-specific financial text** — domain vocabulary (e.g. SEC 10-K terms) is under-represented; train custom embeddings on a financial corpus.
- [ch.23 p.716] **Torturing the data** — "if you torture the data long enough, it will confess" (López de Prado critique).
- [ch.23 p.720] **Treating DL/ensemble as black box** — absent SHAP/interpretability, can't distinguish spurious vs. economic signal.

## 7. Sensitive Parameters
- **Momentum lookback: 12 months minus last month** — [ch.4 p.86] justified economically by behavioral underreaction and positive feedback between economy and risk assets; skipping the last month avoids short-term reversal. NOT curve-fit; standard in academic literature (Jegadeesh & Titman 1993).
- **RSI timeperiod = 14** — [ch.4 p.86] tradition/arbitrary; reasonable values 10–20 perform equivalently. Low curve-fit risk if not optimized.
- **Bollinger timeperiod = 21 (approx. 1 month of trading days), 2σ bands** — [ch.4 p.99] derived from Bollinger's original rules, motivated by normal-distribution 2σ containment.
- **TrainSize = 10 years for GARCH rolling window** [ch.9 p.275] — economic justification: enough data to cover multiple volatility regimes.
- **GARCH(2,2) on NASDAQ daily** — [ch.9 p.276] chosen via grid search on p, q ∈ {1..4}, minimizing out-of-sample RMSE. Report all trials considered.
- **LDA topic count for financial news/earnings calls: 15–25** — [ch.15 p.480] coherence drops and perplexity rises beyond 25–30 topics on the earnings-call corpus (22k statements, 1.5k-word vocab).
- **pyLDAvis relevance λ = 0.6** — [ch.15 p.476] user-study optimum for plausible topic interpretations.
- **word2vec embedding size = 300–600; window = 3–5; min_count = 50; negative = 10** — [ch.16 p.502] empirical grid-search winners on 22k SEC 10-K corpus; size=600 gave best analogy accuracy at 38.5%.
- **Stacked-LSTM: LSTM(25) → LSTM(10), dropout = 0.2** — [ch.19 p.606-607] for 52-week input, 2,500-ticker panel; achieves test AUC 0.6816 and IC 0.32.
- **LightGBM `num_leaves`** — [ch.12 p.398] the most sensitive hyperparameter because leaf-wise growth can explode complexity; authors warn it requires "extra caution".
- **Learning rate (boosting / DL)** — [ch.12 p.388; ch.17 p.538] low LR (e.g. 0.01) with many estimators and early stopping beats high LR with few estimators; less variance.
- **Dropout probability 0.2–0.5 in NNs** [ch.17 p.515-520] — standard range; tune via validation.
- **Discount factor γ (RL)** — [ch.22 p.685] must be strictly <1 to avoid infinite rewards in continuing tasks (specific numeric conventions such as 0.95–0.99 are not stated by the author; source only mandates γ<1).

## 8. Key Literal Quotes
> "The use of powerful models with a high capacity to learn patterns requires particular care to avoid overfitting when the signal-to-noise ratio is as low as is often the case with financial data. Furthermore, the competitive nature of trading implies that patterns evolve quickly as signals decay." — [ch.23 p.713]

> "Two years of daily backtesting data does not support conclusions about more than seven strategies. 5 years of data expands this number to 45 strategy variations." — [ch.8 p.227]

> "The excess returns from new anomalies have been shown to drop by a quarter from discovery to publication, and by over 50 percent after publication due to competition and crowding." — [ch.1 p.15-16]

> "If you torture the data long enough, it will confess." — [ch.23 p.716]

> "ML algorithms trained on distorted historical data will almost certainly fail during live trading." — [ch.1 p.13]

> "An IC of 0.05 or even 0.1 allows for significant outperformance if there are sufficient opportunities to apply this forecasting skill, as the fundamental law of active management will illustrate." — [ch.4 p.116]

> "Keep in mind that using early stopping with the same validation set for a large number of trials will also lead to overfitting, but just for the particular validation set rather than the training set. It is best to avoid running a large number of experiments when developing a trading strategy as the risk of false discoveries increases significantly." — [ch.12 p.373]

## 9. Cross-references to Other Books in This Knowledge Base
- **CPCV, purging, embargoing, deflated Sharpe** — explicitly credited to López de Prado 2018 [ch.6 p.169; ch.8 p.227]; this book provides the hands-on Python implementation complementing López de Prado's theory.
- **Kelly criterion / Half-Kelly** — also treated in `math_money_mgmt.md` (Vince) and `leverage_space.md` with multi-asset extensions [ch.5 p.133].
- **Stat-sound indicators, walk-forward** — `stat_sound_indicators.md` and `testing_tuning.md` cover similar anti-overfit methodology for classical TA [ch.6 p.169].
- **Time-series / GARCH / cointegration** — deeper mathematical treatment in `fin_time_series_tsay.md` and `time_series_hamilton.md` [ch.9 p.260-283].
- **Pairs trading / cointegration / Bayesian rolling regression** — Chan's `algo_trading_chan.md` and `quant_trading_chan.md` cover the same Engle-Granger + Johansen workflow with additional practical detail; this book adds the PyMC3 Gaussian-random-walk Bayesian formulation [ch.9 p.280-283; ch.10 p.320-321].
- **Risk parity / HRP** — overlaps with `risk_parity.md`; HRP comparison to MV and EW in a live ML pipeline is unique to this book [ch.13 p.434-438].
- **Momentum factor, trend following** — `stocks_on_the_move.md` (Clenow) and `universal_trend_tactics.md` provide complementary discretionary/systematic treatments [ch.4 p.84-86].
- **Alpha factor library** — the 100+ factors in the Appendix overlap with the multi-hundred-factor libraries in `trading_systems_methods.md` (Kaufman) [Appendix p.754-781].
- **Linear factor models (Fama-French)** — also referenced in `eval_opt_strategies.md` [ch.7 p.188-191].
- **Sentiment / NLP for trading** — complements `sentiment_analysis_handbook.md`; this book adds an end-to-end NLP stack (spaCy, TF-IDF+NB, LDA, word2vec, doc2vec, BERT) with concrete financial datasets (BBC news, Yelp, earnings calls, SEC 10-Ks) [ch.14-16].
- **Big-data / alt-data infrastructure** — the ITCH / AlgoSeek / EDGAR pipelines complement `big_data_ml_quant.md` [ch.2 p.27-56; ch.3 p.59-80].
