# Big Data and Machine Learning in Quantitative Investment

> **Note on page numbering:** citations use the PRINTED page numbers (book body starts at printed p.1 on PDF [PAGE 7]). Offset PDF→printed ≈ −6 for Part I, with chapter headers restarting printed numbering as per TOC ([p.v-vi, PDF PAGES 5-6]). Where I cite `[p.X]`, X is the number printed on the physical page.

## Metadata
- **Autor:** Tony Guida (editor); 13 chapters by different contributors [cover, p.iii]
- **Ano:** 2019 [p.iv]
- **Editora:** John Wiley & Sons, Ltd (Wiley Finance Series) [p.iv]
- **Páginas:** 285 (PDF); ~278 printed + front/back matter
- **ISBN:** 9781119522195 (hardback); 9781119522218 (ePub); 9781119522089 (ePDF) [p.iv]
- **Foco principal:** Survey/edited volume of practitioner chapters applying alternative data, ML, deep learning, and reinforcement learning to systematic investment (equities, macro, commodities).

## 1. Tese Central

Traditional quantitative finance — linear factor models on structured price/fundamentals data — is reaching diminishing returns as classic factors become crowded (as evidenced by the 2007 "Quant Quake" [p.51-52]). The book's shared thesis, distributed across 13 practitioner chapters, is that the next wave of alpha will come from (a) **alternative data** (satellite, web-scraping, social media, email receipts, news sentiment) that captures economic reality at higher frequency than quarterly filings [p.13-16; ch.4, p.51-74]; and (b) **machine learning methods** (gradient boosting, random forests, SVM, LSTM, reinforcement learning) that can model non-linearity, interaction effects, and temporal dependencies that linear factor models miss [p.1-12; ch.7, p.129-148].

However, every contributor emphasises **feature/label engineering and economic framing** over raw algorithmic power: "A substantial portion of research in ML-based financial applications fails because of a lack of economic framing and unrealistic or ill-defined goals" [p.134]. Reinvention, not replication, is required [p.2-4].

## 2. Conceitos-Chave

- **Alternative data** — novel datasets created mostly in the past ~7 years, not historically available to investment world; often a by-product ("exhaust data") of non-financial economic activity [p.13]. Categorised into 20 types (crowd-sourced, satellite, social, web scraping, ESG, sentiment, etc.) [p.16].
- **Exhaust data** — secondary data generated as by-product of a firm's everyday business (e.g. streaming logs, credit-card receipts) that can be monetised to investors [p.81].
- **Quant Quake (Aug 2007)** — 3-day event (7-9 Aug 2007) where market-neutral quants experienced 12-sigma losses; motivated the search for uncrowded alpha sources [p.51-52].
- **Crowded factors vs less-crowded** — earnings yield, 12-mo momentum and 5-day reversal were heavily crowded by 2007; TM1 seasonality, CAM1 option volume, CAM1 skew were less crowded and barely drew down in the Quake [p.52-53, Table 4.1].
- **Diffusion of innovation (Rogers 1962)** — alt-data adoption moving from early adopters (13.5%) into early majority (34%); US leads Europe/Asia [p.14, Fig 2.1].
- **XGBoost (eXtreme Gradient Boosting)** — third-generation boosted trees library used here to predict sector-neutral stock outperformance over 1-yr horizon [p.136, fn.6].
- **ERS (Event Relevance Score)** — 0-100 integer measuring how prominently a news event features in a story, from RavenPack taxonomy (~6800 event categories) [p.169-170, fn.3].
- **Event Similarity Days (ESD)** — days since a similar event was detected in past 365 days; used to filter duplicate news [p.170, fn.2].
- **Markov Decision Process (MDP)** — state space S, action space A, transition probabilities p(s',r | s,a); foundation for RL trading [p.227-228].
- **Value function v_π(s), action-value q_π(s,a)** — expected cumulative discounted reward under policy π starting from state s (and action a) [p.228-229].
- **VNM-rational preferences** — four axioms (completeness, transitivity, continuity, independence of irrelevant alternatives) guaranteeing utility-function representation of preferences (von Neumann-Morgenstern 1945) [p.232].
- **Mean-variance equivalence** — a return distribution is mean-variance equivalent if, for any standard utility u, optimal portfolio = argmax{E[w̃] − (κ/2)V[w̃]}; holds for elliptical distributions (incl. multivariate Student-t) but NOT for lognormal [p.235-240].
- **LSTM (Long Short-Term Memory)** — RNN variant solving vanishing/exploding gradient problems; suitable for financial time series with autocorrelation, volatility clustering, regimes [p.251, p.255].
- **SVM / Structural Risk Minimization (SRM)** — Vapnik-Chervonenkis-based method that minimises generalisation-error bound (not just empirical error), giving fat-margin separators that generalise better than ANN empirical risk minimization [p.213-214].
- **Kernel trick** — map inputs non-linearly into high-dimensional feature space, allowing linear separation there [p.215-216].
- **Sector-neutral outperformance label** — binary: 1 if stock outperforms its sector over 1y, else 0; used as target by Guida-Coqueret XGBoost model [p.135].
- **Walk-forward CV** — estimate model on past N years, predict next year, roll forward; used in both ch.7 and ch.9 to avoid look-ahead bias [p.136; ch.9, p.172-173].

## 3. Fórmulas / Equações

**3.1 Regression-tree split criterion (variance minimization)** [p.130-131]

For variable j and split value s, choose s minimising total intra-cluster variance:

$$V_j^s = \sum_{t=1}^{T} \mathbf{1}_{\{x_{t,k}>s\}}(y_t - \mu_j^+)^2 + \sum_{t=1}^{T} \mathbf{1}_{\{x_{t,k}\leq s\}}(y_t - \mu_j^-)^2$$

where $\mu_j^{\pm}$ are intra-cluster means. For classification trees, replace variance with cross-entropy $-\sum_{k} \pi_k^{s\pm} \log(\pi_k^{s\pm})$ [p.131].

**3.2 XGBoost additive objective (2nd-order Taylor approx.)** [p.133]

$$\tilde{\Lambda}_m = \sum_{j=1}^{J}\left[w_j \sum_{k\in I_j} g_k + \frac{w_j^2}{2}\left(\sum_{k\in I_j} h_k + \lambda\right)\right]$$

with optimal leaf weight:

$$w_j^* = -\frac{\sum_{k\in I_j} g_k}{\sum_{k\in I_j} h_k + \lambda}$$

where $g_k, h_k$ are first/second derivatives of loss L w.r.t. prediction, and λ is L2 regularisation [p.133].

**3.3 Boosting additive update with shrinkage η** [p.133]

$$T_m(x_t) = T_{m-1}(x_t) + \eta\,\gamma_m f_m(x_t)$$

η (learning rate) shrinks each new tree to "leave more room for future trees" [p.133].

**3.4 Bellman equations (MDP, reinforcement learning)** [p.229-230]

Value function recursion:
$$v_\pi(s) = \sum_{a,s',r} \pi(a\mid s)\, p(s',r\mid s,a)\,[r + \gamma v_\pi(s')]$$

Optimal action-value:
$$q^*(s,a) = \sum_{s',r} p(s',r\mid s,a)\left[r + \gamma \max_{a'} q^*(s',a')\right]$$

**3.5 Q-learning update (Watkins 1989)** [p.230, eq. 12.9]

$$Q(S,A) \mathrel{+}= \alpha\,[\underbrace{R + \gamma \max_a Q(S',a) - Q(S,A)}_{\text{TD-error}}]$$

with step-size α ∈ (0,1). Convergence requires $\sum_t \alpha_t = \infty$ and $\sum_t \alpha_t^2 < \infty$ [p.231, eq. 12.10].

**3.6 Mean-variance reward function for RL trading** [p.241, eq. 12.24]

$$R_t := \delta w_t - \frac{k}{2}(\delta w_t - \hat{\mu})^2$$

where $\delta w_t = w_t - w_{t-1}$ is one-period wealth increment and $\hat{\mu}$ estimates $E[\delta w_t]$. Under this choice, maximising cumulative reward ≈ maximising $E[w_T] - (k/2)V[w_T]$ [p.241].

**3.7 Portfolio P&L with slippage and financing costs** [p.242-243, eq. 12.28-12.31]

$$\delta v_t = h_{t-1}\cdot r_t - c_t, \quad c_t = \text{slip}_t + \text{fin}_t$$

with slippage $\text{slip}_t = \delta n_t \cdot (\tilde{p}_t - p_t)$ (effective minus mid price) and fin_t = commissions + financing [p.242-243].

**3.8 Volatility-adjusted log-return (for mixed-vol basket training)** [p.172, eq. 9.1-9.3]

$$r_{t,n} = \ln(p_{t,n}/p_{t-1,n})$$
$$\sigma_{t,n} = \sqrt{m^{-1}\sum_{j=1}^{m}\left(r_{t-j+1,n} - \bar r\right)^2}$$
$$y_{t,n} = \frac{r_{t,n}}{\sigma_{t-1,n}} \times \text{target}$$

With m = 21 trading days, target = $20\%/\sqrt{252}$ annualised [p.172].

**3.9 Elman RNN update** [p.256, eq. 13.1-13.2]

$$h(t) = f\left(W_i^h(x(t)+b_i) + W_h^h(h(t-1)+b_h)\right)$$
$$y(t) = g\left(W_i^o h(t) + b_o\right)$$

**3.10 Loss functions (LSTM training)** [p.258]
- Binary classification (Bernoulli): $L = -\sum_n y_n\log f_n + (1-y_n)\log(1-f_n)$
- Multi-class softmax: $L = -\sum_n\sum_k y_{kn}\log f_k(x_n,\theta)$
- Regression: $L = \frac{1}{2}\sum_n \|f_n(x_n,\theta)-y_n\|^2$

**3.11 Min-max feature normalization (LSTM preprocessing)** [p.271]

$$\Delta x = \frac{x - \min(x)}{\max(x) - \min(x)}$$

scaled to range (a,b), commonly (0,1).

## 4. Algoritmos e Pseudocódigo

**4.1 XGBoost training protocol for sector-neutral equity prediction (Guida-Coqueret)** [p.136-137]

```
Input: monthly panel (T×K), T≈620k (stock,date) instances, K=200 features
Universe: top 3000 US stocks by mkt cap, Dec 1999 - Dec 2017, point-in-time
Label y_i: 1 if stock i outperforms its sector over next 12m, else 0
  - Exclude stocks outside (5th, 95th) percentile of sector returns
  - Process only top/bottom quintile (hierarchical ranking)
  - Sector-neutralize to avoid sector-rotation artefacts

for each month t:
    train_window = [t-24m, t]   # 24-month rolling
    split 80% train / 20% test (test = most recent 20% — NO "testing in the past")
    fit XGBoost(train) with logistic loss + L2 regularization
    tune hyperparams on test slice:
        - eta (learning rate): shrinkage
        - gamma: min split loss
        - max_depth
        - scale_pos_weight
        - lambda (L2)
    predict(t+12m) probability for each stock
    rebalance monthly
```
Result: long-short top-bottom-decile portfolio delivered ~3.1% avg outperformance vs simple multifactor benchmark [p.146].

**4.2 Walk-forward 10-fold CV ensemble (Hafez-Lautizi energy)** [p.172-174]

```
Models: ELNET, KNN, ANN, RF, GBN (5 models)
Features: ERS-weighted event indicators, 110 event categories reduced
          to 34-37 via |corr|>0.5% filter
Target: volatility-adjusted next-day log-return (21d rolling std, 20% ann. target)

for year Y in {2015, 2016, 2017}:
    for run in 1..10:                      # account for model randomness
        train = data[Y-10 : Y-1]
        for model M in [ELNET, KNN, ANN, RF, GBN]:
            best_hp = 10-fold CV over train
            pred[M,Y,run] = M.fit(train,best_hp).predict(Y)
    ensemble_pred[Y] = mean over runs and optionally over models

Portfolio: weights = normalized predicted returns, gross exposure = 1,
           net ∈ [-1, 1]
```
Out-of-sample ensemble IR = 0.65; high-vol regime IR = 1.27; low-vol regime IR = -0.20 [p.170, Table 9.1].

**4.3 Q-learning (Watkins) for trading** [p.230]

```
Initialize Q (|S|×|A|) = 0
Repeat until convergence:
    observe state S
    choose A via exploration/exploitation policy (e.g. ε-greedy over Q)
    take action A, observe reward R, new state S'
    Target = R + γ * max_a Q(S', a)
    Q(S, A) += α * (Target - Q(S, A))
    S = S'
```
For continuous state/action, replace table with function approximator Q(s,a;θ) — DQN, regression trees, or linear [p.231-232].

**4.4 LSTM stock-return prediction setup (Alonso-Batres-Estrada-Moulin)** [p.270-271]
```
Architecture: 1 hidden LSTM layer, 50 hidden units, ReLU activation
Dropout: 0.01
Batch size: 32
Epochs: 400
Optimizer: Adam (lr=0.001, β1=0.9, β2=0.999, ε=1e-9, decay=0)
Loss: MSE (regression)
Input: multivariate — 50 stock returns + S&P500 + oil + gold
Split: 560d train / 83d val / 83d test / 111d live
Portfolio rule:
    at market open: predict R_i for each stock
    if predicted R_i > 0: open long
    if predicted R_i < 0 and long-short: open short; else skip
    at close: flatten all
```
Live HR ~63%, avg daily L/S return 0.27%, long-only portfolio Sharpe ~8, L/S Sharpe ~10 (no transaction costs) [p.271 Table 13.2, p.274].

**4.5 SVM-based GTAA (Guglietta, Ch.11)** — two-step: (1) forecast each asset-class return via SVR with kernel trick; (2) allocate via conditional mean-variance using current macro state [p.212-218]. Uses sparse macro features: RBC survey indicators and realised inflation [p.213].

## 5. Regras de Trading Explícitas

- **REGRA [p.54]**: Diversify alpha sources across uncrowded factors (TM1 seasonality, option volume, skew) because classic factors (E/P, 12-1 momentum, 5d reversal) are now highly crowded and co-crash in liquidations (Quant Quake lesson).
- **REGRA [p.135]**: When framing ML labels for stock selection, (a) sector-neutralize, (b) exclude outliers outside 5th-95th percentile, (c) use only top/bottom quintile as training labels. Ill-framed labels make ML models fail regardless of algorithm strength.
- **REGRA [p.136]**: Use rolling 24-month training window; keep test set as the MOST RECENT 20% of the window — never test on data older than the training slice ("no testing in the past").
- **REGRA [p.137]**: Control XGBoost complexity via learning_rate η (shrinkage), min_split_loss γ, max_depth, and L2 reg λ. Boosted trees overfit easily, so regularisation is "first-order" concern.
- **REGRA [p.172]**: When modelling a basket with heterogeneous volatilities, **volatility-adjust returns before training** (divide by rolling 21-day std, rescale to common target vol 20% ann.) — otherwise high-vol assets dominate the loss and skew the fit.
- **REGRA [p.173]**: Repeat stochastic training (CV splits + stochastic models) ~10 times and ensemble — single-run results are unreliable due to randomness in CV and random forest / ANN init.
- **REGRA [p.174]**: Filter features by |correlation with target| ≥ 0.005 before fitting; drops 37-45% of raw features and improves speed + in-sample robustness.
- **REGRA [p.178]**: Performance is regime-dependent — condition on volatility regime: the ensemble hit 1.27 IR in high-vol and −0.20 in low-vol [Table 9.1]. Consider regime filters before live deployment.
- **REGRA [p.241]**: RL reward function for trading should be $R_t = \delta w_t - (k/2)(\delta w_t - \hat\mu)^2$ — this is the unique(ish) form under which cumulative reward ≈ mean-variance utility.
- **REGRA [p.242-243]**: Always include slippage (effective vs mid price) AND commissions/financing in the RL cost term $c_t$. Ignoring slippage makes the learned policy trade too aggressively.
- **REGRA [p.243]**: Include current holdings + alpha-signal values + order-book micro-state in the state vector `s_t` — "the agent cannot use a signal that isn't in the state."
- **REGRA [p.270-271]**: For LSTM, split chronologically (train → val → test → live), normalize inputs via min-max to (0,1), and use batch sizes ≥ 32 with dropout ≥ 0.01 to prevent overfitting on financial series.
- **REGRA [p.213]**: For GTAA, increase allocation to risky assets in periods of high expected returns, decrease in periods of high realised volatility (Kandel-Stambaugh 1996 shows even weak predictability can generate economic value if market is timed correctly even 1 out of 100 times).
- **NUNCA [p.11]**: Try to time factors using non-linear time-series models — factor returns are smooth with a few catastrophic bumps; using NN to predict those events leverages heavily on non-repeatable tell-tale signs and usually loses to buy-and-hold after costs.
- **NUNCA [p.54]**: Assume your methodology is unique just because your firm built it. The Quake showed supposedly-differentiated market-neutral books were holding identical positions.
- **NUNCA [p.237]**: Use a quadratic "utility" E[w]-κV[w] as if it were a utility function — it's not (not monotone increasing). It is mathematically equivalent only under mean-variance equivalence (elliptical distributions).

## 6. Pitfalls e Anti-patterns

- [p.9-10] **Brute-force ML on fundamentals is suspect**: fundamental data is discrete, highly-managed and reported quarterly; neural nets on monthly fundamental-data will pick up subtle post-reporting price deviations as if they were signals. Ferrari in London traffic.
- [p.11] **Non-linear factor-timing attempts usually lose to buy-and-hold** after costs — factors are engineered to have smooth returns with rare catastrophic bumps; NNs over-index on those bumps.
- [p.48] **Alpha decay is inevitable**: "every new paradigm has a period of alpha where first-mover advantage prevails. Over time this alpha predictably diminishes." Data sources become crowded.
- [p.48] **Crowdsourced AI / Kaggle-for-hedge-funds has overfit-for-purpose risk** [ref TechEmergence 2018].
- [p.53-54] **The "chasm" (Moore 1991)**: moving from early adopter to early-majority phase is where most alt-data users get stuck — 80% of buy-side *wants* alt data but few have made progress.
- [p.54] **Counting Walmart parking-lot cars via satellite is largely hype** — limited genuine scalable alpha.
- [p.125-126] **Email-receipt alt-data has look-ahead bias risk**: seasonal components estimated on full sample leak into out-of-sample for early weeks of each quarter.
- [p.136] **Keep all correlated features; do NOT pre-select by importance** for boosted trees — they handle correlated features natively; pre-selection reduces degrees of freedom the tree needs for regime adaptation.
- [p.137] **XGBoost overfits easily**: require regularisation; "could exhibit poor generalisation behaviour out of sample" if unregularised.
- [p.174] **Curse of dimensionality**: with 110 event categories and limited history, plain OLS is unusable; linear feature-filtering before a non-linear model is a necessary compromise but introduces a linear-filter bias.
- [p.191] **Sentiment analysis overfitting**: "the NLP practitioner lured by attaining improved results and constantly tweaking model parameterization" — standard ML overfit amplified by scoring/labelling degrees of freedom.
- [p.191] **News-volume bias**: top quintile of S&P Large-Cap Europe = 40% of news coverage; bottom quintile = 5%. Large-cap bias leaks into any sentiment backtest.
- [p.193] **Responding rapidly but wrongly is dangerous** — April 2013 fake White House tweet caused mini flash crash; Thomson Reuters rebuked for selling news seconds early to HFT.
- [p.214-215] **Kernel choice is unsolved**: "there is no good method for the choice of kernel function" — biggest practical SVM limitation (Chaudhuri 2014; Burges 1998; Horváth 2003).
- [p.230] **Vanilla Q-learning converges slowly** and requires huge number of time-steps; use function approximators (DQN, regression-tree ensembles) for continuous state/action spaces.
- [p.237] **Mean-variance equivalence fails for lognormal wealth**; don't assume E[w]-κV[w] captures log-utility decisions.
- [p.251] **RNNs suffer vanishing AND exploding gradients** (Graves 2012; Hochreiter-Schmidhuber 1997); LSTM solves both but at cost of many parameters.
- [p.272] **SVM degrades with longer look-back; LSTM stays robust** — but both were tested without transaction costs (explicitly noted as unrealistic in crisis markets).
- [p.274] **"No trading costs have been considered"** in the LSTM experiments reporting Sharpe ≈ 8-10 — be extremely sceptical of costless backtests.

## 7. Parâmetros Sensíveis

- **Learning rate η (XGBoost)** [p.137] — shrinkage prevents overfitting; authors do NOT give a specific recommended value but discuss tuning via CV. Typical Kaggle practice is 0.01-0.1.
- **max_depth (XGBoost)** [p.138] — tested {3, 5, 7} via 5-fold CV. Higher depth → more overfitting; pair with smaller η.
- **Training window = 24 months (XGBoost)** [p.136] — author justifies as "short enough for regime adaptation with high feature count." Economic justification: rapid sector/style rotation; not a fitted hyperparameter.
- **Rolling volatility window m = 21 (Ch.9)** [p.172] — "NOT optimized; provides good tradeoff between stability and variability." Roughly one trading month — economically motivated, low curve-fit risk.
- **Target annualized vol = 20% (Ch.9)** [p.172] — normalisation constant; not a tunable alpha parameter.
- **10 CV runs averaged (Ch.9)** [p.173] — to reduce stochasticity; larger N better but diminishing returns.
- **Feature filter |corr| ≥ 0.005 (Ch.9)** [p.174] — not optimised; reduces features 37-45%; "introduced to remove very infrequent event categories" — economically motivated.
- **Discount factor γ (RL)** [p.228] — must satisfy 0 < γ < 1 for infinite sum convergence. Set γ ≈ 1 if reward function is per-period wealth (Equation 12.23) so cumulative reward ≈ total-period utility [p.241].
- **Step-size α (Q-learning)** [p.231] — must satisfy Robbins-Monro conditions $\sum \alpha_t = \infty$, $\sum \alpha_t^2 < \infty$. Typically α_t → 0 as t grows.
- **LSTM units = 50, layers = 1 (Ch.13)** [p.270] — not justified economically; consistent with Lee-Yoo (2017) 100-unit LSTM [p.252]; authors don't provide sensitivity analysis.
- **LSTM training window = 560 days (~2.3y), epochs = 400 (Ch.13)** [p.270] — not justified; risk of curve-fit high given small sample relative to parameter count.
- **LSTM look-back {1,2,5,10} days tested (Ch.13 baseline)** [p.272, Table 13.3] — LSTM stable across, SVM degrades monotonically with longer look-back (overfitting).

## 8. Citações Literais Importantes

> "A substantial portion of research in ML-based financial applications fails because of a lack of economic framing and unrealistic or ill-defined goals, such as finding the 'best stocks'." — [p.134]

> "It is for scientifically minded researchers to fall in love with a new methodology and spend their time looking for problems to deploy it on. Like wielding your favourite hammer, wandering around the house looking for nails, machine learning can seem like an exciting branch of methodology with no obviously unique application." — [p.11-12]

> "Every new paradigm has a period of alpha where first-mover advantage prevails. Over time this alpha predictably diminishes." — [p.48]

> "A reinforcement learning agent can learn to maximize only the rewards it knows about. If some part of what defines success is missing from the reward function, then the agent you are training will most likely fall behind in exactly that aspect of success." — [p.240]

> "The determination of the value of an item must not be based on the price, but rather on the utility it yields … There is no doubt that a gain of one thousand ducats is more significant to the pauper than to a rich man though both gain the same amount." — Bernoulli (1954), quoted [p.232]

> "Controlling for model complexity is a first order point for boosted trees as they tend to overfit the data and could exhibit poor generalization behaviour out of sample." — [p.137]

## 9. Conexões com Outros Livros Desta Base

- **CPCV / purged CV / overfitting** — López de Prado `advances_fin_ml.md` develops CPCV, purged K-fold, and the PBO framework. This book (Guida ed.) only uses simpler walk-forward + k-fold CV with "test in the most recent 20%" (Ch.7 [p.136]) and 10-fold CV (Ch.9 [p.173]) — weaker anti-overfit machinery than López de Prado. Treat this book's backtests as more optimistic.
- **Boosted trees / XGBoost on equities** — extends `advances_fin_ml.md` (which uses RF more than XGBoost) and `ml_for_asset_managers.md` (which focuses on covariance denoising and NCO). Ch.7 here is the most practical recipe for sector-neutral XGBoost stock selection.
- **Reinforcement learning** — `advances_fin_ml.md` does NOT cover RL in depth; Ritter's Ch.12 here is the canonical introduction for RL-in-trading in this knowledge base. Complements Sutton-Barto references.
- **LSTM / deep learning** — `ml_for_asset_managers.md` (López de Prado) largely avoids deep learning. Ch.13 here is the main LSTM-for-returns reference in the base; read sceptically given no-costs caveat [p.274].
- **Alt data / sentiment / NLP** — complements any news-sentiment material; this book is most comprehensive on the alt-data taxonomy (Ch.2 [p.16]) and legal issues (Ch.5 [p.83-84]) — unique vs. `advances_fin_ml.md`.
- **Feature engineering emphasis** — resonates with `advances_fin_ml.md` Ch.18 "Feature Importance"; both stress economic framing over algorithm sophistication.
- **Crowding / Quant Quake** — Ch.4 [p.51-54] is the most detailed Quant Quake post-mortem in this knowledge base.
- **Mean-variance equivalence** — Ritter's Ch.12 [p.235-240] gives a rigorous treatment going beyond `systematic_trading.md` standard mean-variance material (connects to elliptical-distribution theory).
- N/A for direct overlap with strict anti-overfit framework (7-layer) of `advances_fin_ml.md` — this book is more permissive on CV methodology.
