# Quantitative Trading: How to Build Your Own Algorithmic Trading Business

## Metadata
- **Author:** Ernest P. Chan [p.i, cover]
- **Year:** 2009 [p.iv]
- **Publisher:** John Wiley & Sons (Wiley Trading series) [p.iv]
- **Pages:** 204 (printed: ~181 pages of content + appendix/index)
- **ISBN:** 978-0-470-28488-9 (cloth) [p.iv]
- **Primary focus:** Practical guide for the independent trader to build a statistical arbitrage business (stocks, futures, FX) with modest capital.

## 1. Core Thesis
"Make everything as simple as possible. But not simpler." — Einstein, quoted by Chan [p.3]. Chan's core thesis is that independent traders, operating from home with $50k-$100k, can outperform institutional hedge funds by exploiting *low capacity strategies* that are economically unviable for large funds [ch.8, p.158]. The key is not advanced math (neural networks, stochastic calculus) but (1) structural simplicity of strategies, (2) discipline in the backtest framework to avoid biases, and (3) use of the Kelly formula for sizing and capital allocation across multiple strategies [ch.6, p.95-96].

Chan argues that statistical arbitrage — trading simple stocks, futures, and FX — does not require a PhD; it requires parsimony (≤5 parameters), data free of survivorship bias whenever possible, and emotional management of drawdowns [ch.2-3, ch.6].

## 2. Main Concepts
- **Statistical arbitrage** — quantitative trading of simple instruments (stocks, futures, currencies), distinct from complex derivatives [p.2]
- **Sharpe ratio** — Chan's primary metric for comparing strategies; ratio of mean excess return to the standard deviation of excess returns [p.18, p.43]
- **Information ratio** — version of Sharpe using a market benchmark (index) instead of the risk-free rate; appropriate for long-only strategies [p.18]
- **Drawdown / Maximum drawdown / Maximum drawdown duration** — difference between current equity and the high watermark; largest peak-to-trough fall; longest period to recover losses [p.21, p.43]
- **High watermark** — global maximum of the equity curve up to time t [p.21]
- **Survivorship bias** — databases that omit delisted/bankrupt firms, artificially inflating backtests of "buy on the cheap" strategies [p.14, p.24, p.40-42]
- **Look-ahead bias** — using information available only in the future (e.g., "buy within 1% of the day's low") to generate signals [p.51]
- **Data-snooping bias** — parameter overfit to historical noise; worse the more parameters you have [p.25, p.52-53]
- **Regime shift** — structural change in markets (decimalization, repeal of the short-sale rule, subprime crisis) that invalidates old series [p.25, p.104]
- **Mean-reverting vs. momentum regime** — two basic categories of profitable strategies; random-walking prices are not tradable [p.116]
- **Cointegration** — linear combination of two non-stationary series that produces a stationary I(0) series; basis of pair trading [p.126-127]
- **Kelly formula (continuous finance)** — optimal fraction of equity per strategy to maximize long-term compounded growth [p.97]
- **Half-Kelly** — using half of the Kelly leverage for safety against estimation errors and fat tails [p.98, p.105]
- **Capacity** — amount of equity a strategy can absorb without degrading returns; the niche of the independent trader is low-capacity strategies [p.27, p.158]
- **Fama-French 3-Factor model** — stock return as a function of beta, market cap, and book-to-price ratio [p.134]
- **Factor exposure / factor return / specific return** — X (sensitivities), b (common drivers), u (specific noise) in the APT R = Xb + u [p.133-134]
- **Ornstein-Uhlenbeck formula** — continuous mean-reversion model used to compute optimal half-life [p.140-141]
- **PEAD (Post-Earnings Announcement Drift)** — momentum strategy: buy stocks whose earnings surprise positively, short those that disappoint [p.118]

## 3. Formulas / Equations
**Sharpe Ratio (Chan's convention)** [p.43-44]

$$\text{Annualized Sharpe Ratio} = \sqrt{N_T} \cdot \frac{\overline{R - r_F}}{\sigma_{R}}$$

Where $N_T$ is the number of trading periods per year; for NYSE intraday $N_T = 252 \times 6.5 = 1638$, NOT $252 \times 24$ [p.45]. For dollar-neutral (self-financing) strategies, do NOT subtract $r_F$: the margin balance earns interest close to $r_F$, cancelling it out [p.43-44]. For long-only day-trading without overnight holding, also do NOT subtract $r_F$ (no financing cost) [p.44]. Rules of thumb: Sharpe < 1 = not stand-alone; Sharpe ≥ 2 = profitable almost every month; Sharpe ≥ 3 = profitable almost every day [p.43].

**Information Ratio** [p.18]

$$\text{Information Ratio} = \frac{\overline{R_{portfolio} - R_{benchmark}}}{\sigma(R_{portfolio} - R_{benchmark})}$$

**Compounded, Levered Growth Rate (Gaussian process)** [p.112]

$$g(f) = r + fm - \frac{s^2 f^2}{2}$$

Where $f$ is leverage, $r$ is the risk-free rate, $m$ is the simple mean of one-period excess return, $s$ is the std of uncompounded returns [p.112]. Special case: for a pure random walk ($m=0, f=1$), $g = -s^2/2 < 0$ — risk reduces the growth rate even with zero drift [p.97].

**Kelly Formula — single strategy (Gaussian)** [p.97, p.113]

$$f^* = \frac{m}{s^2}$$

Derivation [p.113]: take the first derivative of the Gaussian growth rate with respect to leverage $f$ and set it to zero, $dg/df = m - s^2 f = 0$; solving gives the optimal Kelly leverage $f^* = m/s^2$.

**Kelly Formula — multi-strategy (matrix form, Thorp 1997)** [p.96]

$$F^* = C^{-1} M$$

Where $F^*$ is the column vector of optimal allocations $(f_1^*, \ldots, f_n^*)^T$, $C$ is the covariance matrix of returns ($C_{ij}$ = cov($R_i, R_j$)), and $M = (m_1, \ldots, m_n)^T$ is the vector of mean excess returns [p.96]. Returns are one-period, simple (uncompounded), UNLEVERED [p.96-97]. If strategies are independent, $C$ is diagonal and $f_i = m_i / s_i^2$ [p.97].

**Maximum Compounded Growth Rate (Kelly-optimal portfolio)** [p.98, p.102]

$$g(F^*) = r + \frac{F^{*T} C F^*}{2} = r + \frac{S^2}{2}$$

Where $S = \sqrt{F^{*T} C F^*}$ is the Sharpe ratio of the Kelly-optimal portfolio [p.98, p.102]. **This formula is central**: long-term growth is proportional to **Sharpe ratio squared**, not to mean return [p.154].

**Leverage restriction under Regulation T** [p.98]

$$f_i^{restricted} = f_i \cdot \frac{l}{|f_1| + |f_2| + \cdots + |f_n|}$$

Where $l$ = 2 (overnight) or 4 (intraday) [p.98].

**APT / Factor Model** [p.133-134]

$$R = Xb + u$$

Where $R$ is an N×1 vector of excess returns, $X$ is the matrix of factor exposures (loadings), $b$ is the vector of factor returns, and $u$ is the vector of specific returns (assumed uncorrelated across stocks) [p.133-134].

**Ornstein-Uhlenbeck — mean reversion half-life** [p.140-141]

$$dz(t) = -\theta(z(t) - \mu) dt + dW$$

Half-life:

$$\text{half-life} = \frac{\ln(2)}{\theta}$$

Estimate $\theta$ via linear regression of $dz$ on $(z - \bar{z})$ [p.141]. In the GLD-GDX example: half-life ≈ 10 days [p.141-142].

**Split/dividend adjustment multiplier** [p.37]

For an N-to-1 split with ex-date T: multiply pre-T prices by $1/N$.
For a dividend $d$ with ex-date T:

$$\text{multiplier} = \frac{Close(T-1) - d}{Close(T-1)}$$

Apply the multiplier to all prices before T (do not subtract $d$, to preserve returns) [p.37].

**Position sizing by market cap — fourth root rule** [p.88]

Chan recommends scaling capital per stock proportional to $\text{MarketCap}^{1/4}$ to keep the max/min weight ratio below ~10 and preserve the diversification benefit [p.88].

## 4. Algorithms and Pseudocode
**Kelly Optimal Allocation** [p.100-102, Example 6.3]

```
Input: daily returns matrix ret (T x N strategies), risk_free_rate r
    excessRet = ret - r/252
    M = 252 * mean(excessRet, axis=0)       # annualized mean excess returns
    C = 252 * cov(excessRet)                # annualized covariance matrix
    F_star = inv(C) * M                     # Kelly optimal leverages
    g = r + F_star.T @ C @ F_star / 2       # max compounded growth
    S = sqrt(F_star.T @ C @ F_star)         # portfolio Sharpe
    # Rebalance daily: position_size_i = F_star_i * current_equity
```

**Maximum Drawdown Calculation** [p.48-49, Example 3.5]

```
function calculateMaxDD(cumret):
    highwatermark = zeros(length(cumret))
    drawdown     = zeros(length(cumret))
    drawdownduration = zeros(length(cumret))
    for t from 2 to length(cumret):
        highwatermark[t] = max(highwatermark[t-1], cumret[t])
        drawdown[t] = (1 + highwatermark[t]) / (1 + cumret[t]) - 1
        if drawdown[t] == 0:
            drawdownduration[t] = 0
        else:
            drawdownduration[t] = drawdownduration[t-1] + 1
    return max(drawdown), max(drawdownduration)
```

**Look-Ahead Bias Check (Chan's truncation procedure)** [p.51-52, Example 3.6]

```
Step A. Run full backtest on historical data D ending at date T. Save positions to file A.
Step B. Truncate D: remove last N days (N in 10..100). New last date = T-N.
Step C. Re-run backtest on truncated data. Save positions to file B.
Step D. Truncate file A to also end at T-N.
Step E. If positions in A != B anywhere:
            program has look-ahead bias.
            Typical cause: using future data to compute signals on past days.
```

**Pair-Trading with Cointegration (GLD/GDX style)** [p.56-59, Example 3.6]

```
Training:
    Run CADF (cointegrating augmented Dickey-Fuller) test on two price series.
    Null rejected at 95%+ => cointegrated.
    hedge_ratio = OLS slope: price1 = beta * price2 + residual
    spread = price1 - hedge_ratio * price2
    spread_mean, spread_std computed on training set only

Trading:
    zscore_t = (spread_t - spread_mean) / spread_std
    Entry long spread:    zscore <= -2  -> long price1, short hedge_ratio*price2
    Entry short spread:   zscore >= +2  -> short price1, long  hedge_ratio*price2
    Exit when |zscore| <= 1
    Alternative exit (Example 7.5): exit after half-life = ln(2)/theta bars
```

**PCA Factor Model for Cross-Sectional Strategy** [p.137-138, Example 7.4]

```
lookback = 252; numFactors = 5; topN = 50
for each day t > lookback:
    R = dailyret[t-lookback+1 : t, :]        # (days x stocks), exclude NaN stocks
    R_demean = R - mean(R, axis=0)
    covR = cov(R_demean)
    (eigvals, eigvecs) = eig(covR)
    X = eigvecs[:, -numFactors:]             # top-N eigenvectors as factor loadings
    b = OLS(R[end,:], X)                     # latest factor returns
    R_expected = mean(R, axis=0) + X @ b     # assume factor returns have momentum
    long_topN_highest(R_expected)
    short_topN_lowest(R_expected)
# Chan reports this produced -1.81 annualized in backtest;
# assumption of factor-return momentum may be wrong for small-caps. [p.138]
```

**January Effect (mean-reverting on small-cap losers)** [p.144-146, Example 7.6]

```
For each year y:
    annret_y = (close[last_day_Dec_y] - close[last_day_Dec_{y-1}]) / close[last_day_Dec_{y-1}]
    Sort stocks by annret_y ascending.
    topN = round(n_stocks / 10)   # decile
    longs  = bottom decile (worst 10% of prior year)
    shorts = top decile    (best 10% of prior year)
    Hold from close of last trading day of December
       to close of last trading day of January.
    Subtract 2 * 5bp transaction costs (round-trip).
```

**Ornstein-Uhlenbeck Half-Life Estimation** [p.141-142, Example 7.5]

```
prevz = lag(z, 1)
dz = z - prevz
# Regress dz ~ (prevz - mean(prevz))
theta = OLS(dz, prevz - mean(prevz)).beta
halflife = -ln(2) / theta     # negative theta means mean-reverting
```

## 5. Explicit Trading Rules
- **RULE [p.43]**: Reject stand-alone strategies with Sharpe ratio < 1. Sharpe ≥ 2 is a realistic floor for a profit-center.
- **RULE [p.53, p.74]**: Never use more than **5 parameters** in a model (including entry/exit thresholds, holding period, lookback). Rule-of-thumb: you need ≥ 252 x (n_params) data points.
- **RULE [p.53]**: Split data into training set and test set, roughly equal (or at least 1/3 test set). The test set is SACRED — do NOT adjust parameters on it [p.60].
- **RULE [p.98, p.105]**: Use **half-Kelly** by default (or less) due to fat tails and estimation error in $m, s$. Full Kelly is fragile.
- **RULE [p.105-106]**: Final leverage = min(half-Kelly, max_tolerable_drawdown / worst_historical_one-period_loss).
- **RULE [p.103]**: Rebalance positions per Kelly at least once at the end of each trading day. After a loss, reduce position size; after a gain, increase it.
- **RULE [p.103]**: Lookback for estimating Kelly's $M$ and $C$ is ~6 months for strategies with a 1-day holding period.
- **RULE [p.87]**: An individual order should not exceed **1% of the average daily volume** of the asset (reduces market impact).
- **RULE [p.87]**: Avoid stocks priced < $5 (commission as % rises, percentage bid-ask spread rises).
- **RULE [p.88]**: Scale capital per stock proportional to $\text{MarketCap}^{1/4}$, not linearly (preserves diversification).
- **RULE [p.51, p.74]**: Always use **lagged data** (prior day's close) to generate signals, unless the strategy enters exactly at the close.
- **RULE [p.142-143]**: A stop loss is appropriate for momentum strategies (trending regime). A stop loss is **harmful** for mean-reversion strategies — in mean-reverting, you exit at the worst moment.
- **RULE [p.143]**: For mean-reversion, exit via (a) mean target price ($\mu$ of OU), (b) half-life of $\ln(2)/\theta$, or (c) the opposite of the new entry signal.
- **RULE [p.97]**: Returns used as Kelly inputs must be **one-period, simple (uncompounded), unlevered**.
- **RULE [p.43-44]**: For dollar-neutral portfolios and long-only strategies without overnight holdings, do NOT subtract the risk-free rate in the Sharpe calculation (financing cost is ~zero).
- **NEVER [p.106]**: Rely on stop losses to prevent catastrophes — in gap events fills happen well below the stop, realizing the loss rather than avoiding it.
- **NEVER [p.103]**: Fail to recompute $F^*$ daily after equity changes; Kelly is not set-and-forget.
- **NEVER [p.52]**: Optimize parameters on the test set after already calibrating on the training set. This turns the test set into a training set and reintroduces data-snooping bias.
- **NEVER [p.110]**: Modify a strategy immediately after a large loss ("representativeness bias"). Always backtest the modification over a long period.

## 6. Pitfalls and Anti-patterns
- **[p.14, p.24, p.40-42] Survivorship bias**: backtesting on a database without delisted stocks artificially inflates "buy cheap" / "buy losers" strategies. Chan's numerical example: a portfolio selected in 2001 returned **-42% real** vs. **+388% fictitious** when delisted stocks were omitted [Example 3.3, p.41-42].
- **[p.51] Look-ahead bias**: using the "day's high" or a regression fit on the full dataset to generate signals within the period. Easier to detect in Excel (WYSIWYG) than in MATLAB/Python. Chan recommends the truncation test (see Algorithm in section 4).
- **[p.25, p.52-53] Data-snooping bias**: any model with > ~5 parameters fit to < 5 years of daily data will fit noise. AI/neural networks with "many parameters" **consistently failed** in Chan's direct experience [sidebar p.26-27].
- **[p.45] Transaction cost underestimation**: a Bollinger-band ES strategy with Sharpe = 3 (no costs) becomes Sharpe = **-3** with just 1 bp of cost per trade [p.45].
- **[p.42] Noisy high/low data**: intraday high/low prices have far more noise than open/close; backtests that assume fills at limit prices below the day's high are overly optimistic [p.42].
- **[p.25, p.104] Regime shifts**: data from more than 10 years ago can be useless due to structural changes (decimalization 2003, uptick-rule repeal 2007, subprime). Financial series are **non-stationary** [p.25].
- **[p.111-112] Overleveraging after initial success** (greed): Chan confesses to having lost $1M+ by adding $100M to a strategy with only 6 months of track record. "It is a hitherto superbly performing model that is at the greatest risk of huge loss due to overconfidence and overleverage."
- **[p.106, p.143] Stop loss in mean-reverting regime**: "exiting at the worst possible time."
- **[p.108-109] Status quo bias / endowment effect**: holding losers too long even without mean-reverting justification; exiting winners too early due to loss aversion.
- **[p.109] Representativeness bias**: changing parameters immediately after a large loss. "No system can avoid all the market vagaries that can result in losses."
- **[p.110] Despair (prolonged drawdown) + greed (after big wins)** → overleveraging in both directions. Long-Term Capital Management 2000 and Amaranth Advisors 2006 are textbook cases [p.110].
- **[p.123-126] AI / machine learning overfit**: Alphacet Discovery with perceptron returned 37.93% on a 6-month backtest in GS — Chan warns that the short period and multiple models tried still carry data-snooping, even in a moving-window framework.
- **[p.139] Factor models with fundamental factors**: assume "investors persist in using the same metric to value companies" — severe drawdown when the valuation regime changes (e.g., growth-vs-value in 2007).
- **[p.88] Linear scaling by market cap**: produces weight ratios > 10,000x, destroying diversification. Use fourth-root scaling.

## 7. Sensitive Parameters
- **Kelly leverage $f^* = m/s^2$** [p.98, p.105]: Chan recommends **half** the value (half-Kelly) in production. Economic justification: fat tails + estimation error. NOT curve-fit.
- **Kelly lookback for estimating $m, s$** [p.103]: ~6 months for 1-day holding. Justification: balance between responsiveness to regime shifts and statistical stability. Low-sensitivity parameter — do not optimize in the backtest.
- **Maximum of 5 parameters per model** [p.53]: Chan's rule-of-thumb based on experience, not formal theory. Relationship to sample size: 252 x n_params.
- **Mean-reversion half-life = $\ln(2)/\theta$** [p.141]: parameter *derived* from OU, not optimized. Robust because it uses the full series, not just trades.
- **Entry/exit thresholds in pair trading (GLD/GDX)** [p.58-59]: Chan tested ±2 std entry / ±1 std exit → train Sharpe 2.3, test 1.5; and ±1 std entry / ±0.5 std exit → train Sharpe 2.9, test 2.1. Moderate sensitivity — economically equivalent values work.
- **Lookback=252 days, numFactors=5, topN=50 in the PCA factor model** [p.137]: parameters set arbitrarily by Chan; he admits the backtest is negative, suggesting the model structure is wrong, not the parameters.
- **Transaction cost assumption of 5 bps per trade (one-way)** [p.45, p.63]: institutional standard for S&P 500. ES (E-mini S&P 500 futures): ~1 bp [p.45]. Economically justified by the average bid-ask spread + commission.
- **Risk-free rate 4% p.a.** [p.45]: reflected the 3-month T-bill yield in 2008. Not optimized.
- **Sharpe rules of thumb vs. holding frequency** [p.43]: Sharpe ≥ 2 = profitable almost every month; Sharpe ≥ 3 = profitable almost every day. Derived from the law of large numbers, not curve-fit.

## 8. Key Literal Quotes
> "As Einstein said: 'Make everything as simple as possible.' But not simpler." — [p.3]

> "Finance is famously nonstationary... it is possible to incorporate such regime shifts into a sophisticated 'super'-model, but it is much simpler if we just demand that our model deliver good performance on recent data." — [p.25]

> "The take-away lesson here is that risk always decreases long-term growth rate—hence the importance of risk management!" — [p.98]

> "It is a hitherto superbly performing model that is at the greatest risk of huge loss due to overconfidence and overleverage." — [p.111-112]

> "When a catastrophic event occurs, securities prices will drop discontinuously, so the stop loss orders to exit the positions will only be filled at prices much worse than those before the event. So, by exiting the positions, we are actually realizing the catastrophic loss and not avoiding it." — [p.106]

> "With many parameters, we can for sure capture small patterns that no human can see. But do these patterns persist? Or are they random noises that will never replay again?" — [p.26]

> "The ultimate risk management mind-set is very simple: Do not succumb to either despair or greed." — [p.112]

## 9. Cross-references to Other Books in This Knowledge Base
- **Kelly formula & leverage-space** [p.96-98]: `leverage_space.md` (Vince) covers the same ground with more mathematical depth; Chan uses the continuous Gaussian version (Thorp 1997), Vince uses discrete Kelly and TWR. Chan's "half-Kelly" recommendation is consistent with Vince's warning about the sensitivity of optimal f.
- **Parameter parsimony (≤5)** [p.53]: same conclusion in `systematic_trading.md` (Carver, ~3-4 params) and `evidence_based_ta.md` (Aronson, multiple-testing penalty). Independent convergence.
- **Survivorship bias and data-snooping** [p.40-42, p.52-53]: `advances_fin_ml.md` (López de Prado) formalizes the problem with CPCV and DSR (Deflated Sharpe Ratio); Chan is less rigorous but reaches the same practical warnings.
- **Mean-reversion, cointegration, Ornstein-Uhlenbeck** [p.126-142]: `time_series_hamilton.md` covers ADF/cointegration formally. Chan uses CADF via the spatial-econometrics toolbox [p.128-129] as a practical application.
- **Regime detection** [p.119-126]: `regime_change.md` and `ml_for_asset_managers.md` cover HMM / structural breaks — Chan is skeptical of Markov regime-switching ("useless for actual trading purposes because of constant transition probabilities", [p.121]) but open to data-mining turning points.
- **Momentum strategies** [p.116-119]: `stocks_on_the_move.md` (Clenow) is a specific cross-sectional momentum implementation that fits the class Chan describes.
- **Chan trilogy** [cover]: this is the first book. `algo_trading_chan.md` (2013) and `machine_trading.md` (2017) are not yet processed — they will be added in subsequent passes for expanded cross-refs.
