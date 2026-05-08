# Algorithmic Trading: Winning Strategies and Their Rationale

## Metadata
- **Author:** Ernest P. Chan [p.i, cover]
- **Year:** 2013 [cover]
- **Publisher:** John Wiley & Sons (Wiley Trading series) [p.iv]
- **Pages:** 225 [p.iv]
- **ISBN:** 978-1-118-46014-6 [p.iv]
- **Main focus:** Strategies for mean reversion and momentum trading across stocks, ETFs, currencies, and futures, grounded in economic rationale and backed by statistical tests and Kelly-based risk management. [p.xi, preface]

## 1. Core Thesis
Chan argues that profitable algorithmic trading strategies must be grounded in a fundamental understanding of *why* a market inefficiency exists — not discovered via exhaustive data-mining of technical indicators [p.xi, preface]. The book's unifying thesis is that simple, linear models exploiting identifiable market inefficiencies are superior to complex nonlinear models, because complexity invites data-snooping bias while linearity yields parsimony and interpretability [p.5-6, ch.1].

A second pillar is the scientific method applied to trading: form a hypothesis about the source of a market inefficiency, build the simplest model that captures it, validate with out-of-sample data, and diagnose failures by looking for regime changes rather than blindly adding parameters [p.188, conclusion]. Chan explicitly warns that "true out-of-sample testing cannot really begin until a strategy is published and cast in stone" [p.3, ch.1], because any re-optimization on a supposedly held-out dataset turns it into in-sample data.

The book covers two broad strategy families — mean reversion and momentum — each with distinct risk-return signatures: mean-reverting strategies have capped upside but potentially unbounded drawdown, while momentum strategies have limited downside (via natural stop loss) but unlimited upside, making them complementary in a diversified portfolio [p.153-154, ch.6].

## 2. Main Concepts
- **Look-ahead bias** — using future information (e.g., intraday high/low before bar close) to generate a backtest signal; a programming error that inflates returns [p.4, ch.1]
- **Data-snooping bias** — overfitting a model to random historical patterns via too many free parameters or complex trading rules; minimized by keeping models as simple and linear as possible [p.5, ch.1]
- **Survivorship bias** — using stock databases that exclude delisted companies; especially dangerous for long-only mean-reversion strategies [p.9, ch.1]
- **Primary vs. consolidated stock prices** — MOC/MOO orders execute on the primary exchange (NYSE, Arca, Nasdaq), not at the consolidated tape price; using consolidated prices inflates mean-reversion backtest performance [p.10-11, ch.1]
- **Regime shift** — structural market changes (decimalization April 9, 2001; 2008 financial crisis; Regulation NMS July 2007; uptick rule changes 2007/2010) that invalidate backtests done on prior data [p.24-25, ch.1]
- **Stationarity** — a price series whose variance grows slower than a geometric random walk; described by the Ornstein-Uhlenbeck process; prerequisite for mean-reversion trading [p.41, ch.2]
- **Cointegration** — multiple non-stationary price series that can be combined into a stationary portfolio; the basis for pairs trading; tested via CADF or Johansen tests [p.51, ch.2]
- **Half-life of mean reversion** — the time for a price series to decay halfway toward its mean; derived from the $\lambda$ coefficient in the ADF regression: $\text{half-life} = -\log(2)/\lambda$; sets the natural lookback for moving averages [p.47-48, ch.2]
- **Roll return** — the component of a futures contract's total return arising from convergence toward spot price as expiration approaches; distinct from spot return; can dominate total return [p.115-116, ch.5]
- **Backwardation** — near-contract prices exceed far-contract prices; produces positive roll returns [p.116, ch.5]
- **Contango** — far-contract prices exceed near-contract prices; produces negative roll returns; VX (VIX future) in contango about three-fourths of the time with average annualized roll return of −50% [p.122, ch.5]
- **Time series momentum** — past returns of a single instrument are positively correlated with future returns [p.133, ch.6]
- **Cross-sectional momentum** — an instrument outperforming its peers continues to outperform [p.133-134, ch.6]
- **Post-earnings announcement drift (PEAD)** — stock prices continue drifting in the direction of the earnings surprise for some period after the announcement; known since 1968 and still measurable as recently as 2011 [p.158, ch.7]
- **Leveraged ETF rebalancing momentum** — daily rebalancing to maintain constant leverage necessitates buying when the index rises and selling when it falls, generating near-close momentum in underlying stocks [p.163-164, ch.7]
- **Kelly formula** — determines the optimal leverage maximizing long-run compounded growth rate; also provides an optimal capital allocation formula across multiple strategies [p.172, ch.8]
- **Constant Proportion Portfolio Insurance (CPPI)** — sets aside a fraction D of capital for active trading with Kelly leverage, guaranteeing a maximum drawdown of −D while maximizing compounded growth [p.180-181, ch.8]
- **Crack spread** — portfolio of long three CL (crude oil) contracts, short two RB (gasoline) contracts, short one HO (heating oil) contract; NYMEX offers this as a ready-made basket with lower margin requirements [p.128, ch.5]

## 3. Formulas / Equations
**ADF Test Linear Model** [p.42-44, ch.2]

$$\Delta y(t) = \lambda y(t-1) + \mu + \beta t + \alpha_1 \Delta y(t-1) + \ldots + \alpha_k \Delta y(t-k) + \epsilon_t \tag{2.1}$$

- $\lambda$: mean-reversion coefficient (must be negative and significantly different from zero to confirm mean reversion) [p.42, ch.2]
- Test statistic: $\lambda / SE(\lambda)$, compared against Dickey-Fuller critical values [p.42-43, ch.2]
- In MATLAB: use `adf` from spatial-econometrics.com `jplv7` package with lag $k=1$ [p.43, ch.2]
- USD.CAD example: test statistic −1.84 vs. critical value −2.594 at 90% → cannot reject random walk [p.44, ch.2]

**Ornstein-Uhlenbeck Process** [p.47, ch.2]

$$dy(t) = (\lambda y(t-1) + \mu)dt + d\epsilon \tag{2.5}$$

$$E(y(t)) = y_0 \exp(\lambda t) - \frac{\mu}{\lambda}(1 - \exp(\lambda t)) \tag{2.6}$$

- Half-life: $\text{half-life} = -\log(2)/\lambda$ [p.47, ch.2]
- USD.CAD half-life: approximately 115 days [p.48, ch.2]
- In code: `halflife = -log(2)/regress_results.beta(1)` where regression is $\Delta y$ on $y_{t-1}$ [p.47-48, ch.2]

**Hurst Exponent** [p.44-46, ch.2]

$$\langle |z(t+\tau) - z(t)|^2 \rangle \sim \tau^{2H} \tag{2.4}$$

- $H = 0.5$: geometric random walk; $H < 0.5$: mean-reverting; $H > 0.5$: trending [p.44-45, ch.2]
- USD.CAD estimated $H = 0.49$, indicating weakly mean-reverting [p.46, ch.2]

**Johansen Test Vector Form** [p.55, ch.2]

$$\Delta Y(t) = \Lambda Y(t-1) + M + A_1 \Delta Y(t-1) + \ldots + A_k \Delta Y(t-k) + \epsilon_t \tag{2.7}$$

- Rank $r$ of $\Lambda$ = number of independent cointegrating relationships [p.55, ch.2]
- Eigenvectors of $\Lambda$ give the hedge ratios for forming a stationary portfolio [p.55, ch.2]

**Z-Score Factor Normalization** [p.6-7, ch.1]

$$z(i) = \frac{f(i) - \text{mean}(f)}{\text{std}(f)} \tag{1.1}$$

**Equal-Weight Factor Combination (Predicted Return)** [p.6-7, ch.1]

$$R = \text{mean}(R) + \text{std}(R) \cdot \frac{\sum_i \text{sign}(i) \cdot z(i)}{n} \tag{1.2}$$

- sign(i) = historical correlation sign between factor $f(i)$ and return $R$ [p.6-7, ch.1]
- "Formulas that assign equal weights to all the predictors are often superior, because they are not affected by accidents of sampling" — Kahneman 2011 [p.7, ch.1]

**Rank-Based Factor Combination** [p.7, ch.1]

$$\text{rank}_s = \sum_i \text{sign}(i) \cdot \text{rank}_s(i) \tag{1.3}$$

- Greenblatt's "magic formula" (return on capital + earnings yield): APR 30.8% (1988–2004) vs. 12.4% for S&P 500 [p.7, ch.1]

**Futures Price Model** [p.118, ch.5]

$$F(t, T) = c \, e^{\alpha t} \exp(\gamma(t - T)) \tag{5.9}$$

- $\alpha$ = annualized spot return; $\gamma$ = annualized roll return; $T$ = expiration date [p.118, ch.5]
- Total return = $\alpha + \gamma$; roll return = $\gamma$; spot return = $\alpha$ [p.118, ch.5]
- Used to estimate $\gamma$ via linear regression on the forward curve (5 nearest contracts) at each date [p.120, ch.5]

**Annualized Average Roll Returns (from regression)** [p.122, ch.5]:
- BR (CME): spot −2.7%, roll +10.8% [p.122, ch.5]
- C (CBOT): spot +2.8%, roll −12.8% [p.122, ch.5]
- CL (NYMEX): spot +7.3%, roll −7.1% [p.122, ch.5]
- HG (CME): spot +5.0%, roll +7.7% [p.122, ch.5]
- TU (CBOT): spot −0.0%, roll +3.2% [p.122, ch.5]

**Calendar Spread Log Market Value** [p.123, ch.5]

$$\text{spread} = \gamma(T_1 - T_2), \quad T_2 > T_1 \tag{derived from 5.9}$$

- CL 12-month calendar spread: stationary (ADF 99%), half-life 36 days [p.123, ch.5]

**Currency Return Formula** [p.110, ch.5]

$$r_i(t+1) = \frac{y_{i,U}(t+1) - y_{i,U}(t)}{y_{i,U}(t)} \tag{5.2}$$

**Excess Return with Rollover Interest** [p.114, ch.5]

$$r(t+1) = \{\log(y_{B.Q}(t+1)) - \log(y_{B.Q}(t)) + \log(1+i_B(t)) - \log(1+i_Q(t))\} \tag{5.6}$$

**Kalman Filter Measurement Equation** [p.76, ch.3]

$$y(t) = x(t)\beta(t) + \epsilon(t), \quad V_\epsilon = \text{variance of measurement error} \tag{3.5}$$

$$\beta(t) = \beta(t-1) + \omega(t-1), \quad V_\omega = \frac{\delta}{1-\delta} I \tag{3.6}$$

- $\delta = 0.0001$ recommended (with hindsight); $V_\epsilon = 0.001$ [p.79, ch.3]
- State update: $\hat{\beta}(t|t) = \hat{\beta}(t|t-1) + K(t) \cdot e(t)$, where $K(t) = R(t|t-1) \cdot x(t) / Q(t)$ [p.79, ch.3]

**Kelly Formula — Single Strategy** [p.172, ch.8]

$$f = \frac{m}{s^2} \tag{8.1}$$

- $m$ = mean excess return; $s^2$ = variance of excess returns [p.172, ch.8]
- Use as upper bound; half-Kelly is the prudent standard for deployment [p.172, ch.8]

**Kelly Formula — Multi-Strategy Allocation** [p.173, ch.8]

$$F = C^{-1} M \tag{8.2}$$

- $C$ = covariance matrix of strategy returns; $M$ = vector of mean excess returns [p.173, ch.8]
- $F$ = vector of optimal leverages per strategy [p.173, ch.8]

**Compounded Growth Rate** [p.175, ch.8]

$$g(f) = \langle \log(1 + fR) \rangle \tag{8.5}$$

- Under Gaussian: $g(f) = fm - f^2 s^2/2$; maximize to recover Equation 8.1 [p.175, ch.8]
- Non-Gaussian: use Monte Carlo with Pearson system simulation [p.175-176, ch.8]

**Hypothesis Testing Critical Values for Daily Sharpe** [p.17, ch.1]

Test statistic: $\sqrt{n} \times \text{daily Sharpe ratio}$

| p-value | Critical value |
|---------|---------------|
| 0.10    | 1.282         |
| 0.05    | 1.645         |
| 0.01    | 2.326         |
| 0.001   | 3.091         |

Source: Berntson (2002) [p.17, ch.1].

**Scaling-In Transition Probability** [p.73-74, ch.3]

$$\hat{p} = \frac{F - L_1}{F - L_2}$$

- If $p < \hat{p}$: all-in at $L_1$ is most profitable; if $p > \hat{p}$: all-in at $L_2$ is most profitable; averaging-in is never optimal in backtest (Schoenberg and Corwin 2010) [p.73-74, ch.3]

## 4. Algorithms and Pseudocode
**Buy-on-Gap (Intraday Mean Reversion)** [p.94, ch.4]

```
Input: daily op, lo, cl arrays for SPX stocks
Parameters: topN=10, entryZscore=1, lookback=20

For each day t:
  stdretC2C90d = 90-day moving std of daily close-to-close returns (lagged 1)
  buyPrice = prior_day_low × (1 - entryZscore × stdretC2C90d)
  retGap = (today_open - prior_day_low) / prior_day_low
  ma = 20-day moving average of closes (lagged 1)

  Select stocks where:
    today_open < buyPrice  (gapped down > 1 std dev from prior low)
    today_open > ma         (price above 20-day MA — momentum filter)
  
  Sort by retGap ascending; buy top N (lowest return) stocks at open
  Exit all positions at market close

Return: open-to-close P&L / topN
```

Result: APR 8.7%, Sharpe 1.5 (May 11, 2006–April 24, 2012) [p.94-95, ch.4]

**TU Time Series Momentum Strategy** [p.156-157, ch.6]

```
Input: daily closing prices cl for TU futures
Parameters: lookback=250, holddays=25

For each day t:
  longs[t] = (cl[t] > cl[t - lookback])
  shorts[t] = (cl[t] < cl[t - lookback])

pos = zero array
For h = 0 to holddays-1:
  pos += shift(longs, h)
  pos -= shift(shorts, h)

daily_return = shift(pos, 1) × (cl - shift(cl,1)) / shift(cl,1) / holddays
```

Result: APR 1.7%, Sharpe 1.04, max DD −2.5% (Jun 2004–May 2012) [p.157-158, ch.6]

**Bollinger Band Pairs Strategy** [p.71-73, ch.3]

```
Input: spread = yport (computed from hedge ratio × prices)
Parameters: lookback, entryZscore=1, exitZscore=0

zScore = (yport - movingAvg(yport, lookback)) / movingStd(yport, lookback)

longsEntry  = zScore < -entryZscore
longsExit   = zScore >= -exitZscore
shortsEntry = zScore > entryZscore
shortsExit  = zScore <= exitZscore

numUnitsLong[longsEntry] = 1; numUnitsLong[longsExit] = 0
numUnitsShort[shortsEntry] = -1; numUnitsShort[shortsExit] = 0
Fill missing values forward (carry last position)

numUnits = numUnitsLong + numUnitsShort
positions = numUnits × hedgeRatio × prices
```

Result on GLD-USO: APR 17.8%, Sharpe 0.96 [p.73, ch.3]

**Monte Carlo Leverage Optimization** [p.174-176, ch.8]

```
Input: historical daily returns ret
1. Compute first four moments: mean, std, skewness, kurtosis
2. Generate 100,000 simulated returns using Pearson system (pearsrnd)
3. Define growth rate: g(f) = sum(log(1 + f × ret_sim)) / length(ret_sim)
4. Numerically maximize g(f) over f in [0, f_max] using fminbnd
5. Output: optimal leverage f_opt (compare with Kelly = mean/var)
```

Applied to Example 5.1 strategy: Kelly f = 18.4; Monte Carlo optimal f ≈ 19 [p.176-177, ch.8]

**Post-Earnings Announcement Drift (PEAD)** [p.161, ch.7]

```
Input: op, cl (T×N arrays), earnann (T×N logical: true if earnings before open)
Parameters: lookback=90, threshold=0.5, maxPositions=30

retC2O = (op - lag(cl, 1)) / lag(cl, 1)
stdC2O = 90-day moving std of retC2O

positions = 0
positions[retC2O >= 0.5 × stdC2O AND earnann] = 1   (long)
positions[retC2O <= -0.5 × stdC2O AND earnann] = -1  (short)

daily_return = sum(positions × (cl - op) / op, axis=stocks) / 30
```

Result: APR 6.7%, Sharpe 1.5 (Jan 3, 2011–April 24, 2012); leverage 4× → ~27% annualized [p.161-162, ch.7]

## 5. Explicit Trading Rules
- **RULE [p.20-21, ch.1]**: Perform walk-forward test as the final out-of-sample validation. Live trading with minimal leverage is preferred over paper trading — it tests execution details paper trading misses. Most traders would be happy with live Sharpe ratio > half of backtest value.

- **RULE [p.47, ch.2]**: Set the lookback for moving average and standard deviation in a mean-reversion strategy to a small multiple of the half-life of mean reversion. This avoids brute-force parameter optimization and provides economic justification for the parameter.

- **RULE [p.54, ch.2]**: When using CADF, try both orderings of dependent/independent variable and use the one that gives the most negative t-statistic and the economically sensible hedge ratio.

- **RULE [p.65-66, ch.3]**: Use price spreads when you want a fixed number of shares per trade; use log price spreads when you want fixed capital weights (requires constant rebalancing). Use ratios (price1/price2) when the pair is not truly cointegrated — especially for currencies.

- **RULE [p.95, ch.4]**: Apply a momentum filter (price above long-term moving average) as a gate on a mean-reversion entry signal. Drops caused by negative news are less likely to revert than those caused by liquidity demands [p.95, ch.4].

- **RULE [p.94, ch.4]**: Buy-on-gap rules: (1) select stocks where return from prior day's low to today's open is below −1 standard deviation (90-day close-to-close std); (2) restrict to stocks with open above 20-day MA; (3) buy the 10 stocks with the lowest gap returns; (4) liquidate all positions at market close.

- **RULE [p.116-117, ch.5]**: Use settlement prices (not last-traded prices) for futures spread backtesting — they are contemporaneous. For intermarket spreads across different exchanges, obtain synchronized intraday bid-ask data.

- **RULE [p.31-32, ch.1]**: For futures continuous contracts: use additive (price) back-adjustment for spread-signal strategies; use multiplicative (return) back-adjustment for ratio-signal strategies. You cannot have both P&L and return correct simultaneously with a continuous contract series.

- **RULE [p.139-140, ch.6]**: For roll-return persistence momentum in futures, use the sign of roll return as a signal rather than lagged total return. On TU with 3% annualized threshold: APR 2.5%, Sharpe 2.1.

- **RULE [p.163-164, ch.7]**: Leveraged ETF near-close momentum: enter long in a leveraged ETF if the return from previous close to 15 minutes before close exceeds +2%; enter short if below −2%; exit at market close. APR 15%, Sharpe 1.8 on DRN [p.163-164, ch.7].

- **RULE [p.172, ch.8]**: Use Kelly leverage $f = m/s^2$ as an *upper bound*, not as the leverage to deploy. Given estimation errors and non-Gaussian returns, half-Kelly is the standard prudent choice.

- **RULE [p.172-173, ch.8]**: When facing a broker-imposed maximum leverage much lower than Kelly, it is often optimal to allocate all buying power to the strategy with the highest growth rate rather than scaling all strategies proportionally.

- **RULE [p.180-181, ch.8]**: CPPI: trade only fraction D of total equity (Kelly leverage on that sub-account), keeping 1−D in cash. Reset sub-account equity to D × total at each new high watermark. Growth rate CPPI ≈ half-Kelly alternative (0.002484 vs. 0.002525 per day), but max drawdown limited to −D by design [p.181, ch.8].

- **NEVER [p.183-184, ch.8]**: Do not impose stop losses on mean-reversion strategies at levels that would be triggered during backtest — they always lower backtest performance. Set stop loss above the maximum intraday backtest drawdown to protect against regime change without degrading the backtested model.

## 6. Pitfalls and Anti-patterns
- **[p.xi-xii, preface]** The example strategies deliberately omit transaction costs and sometimes use in-sample data for both parameter optimization and performance measurement. They are "prototype strategies" meant to illustrate techniques, not ready-to-trade systems.

- **[p.3, ch.1]** Backtests done before a regime shift are worthless for predicting post-shift performance. Key shifts: decimalization (April 9, 2001), Reg NMS (July 2007), 2008 financial crisis, uptick rule changes (2007, 2010).

- **[p.5, ch.1]** No matter how carefully data-snooping bias is avoided, it "will somehow creep into your model." Walk-forward testing is the only true safeguard. Re-optimizing on "out-of-sample" data converts it to in-sample data.

- **[p.23-24, ch.1]** Backtesting high-frequency strategies is fundamentally problematic: profitability depends on order types, execution method, and reactions of other market participants — a "Heisenberg uncertainty principle" is at work. Be very skeptical of any HFT backtest.

- **[p.27-28, ch.1]** Using consolidated stock prices (instead of primary exchange prices) inflates mean-reversion backtest performance because outlier prices on secondary exchanges revert to auction prices on the primary exchange. For MOC/MOO strategies, use primary exchange historical data only.

- **[p.88-89, ch.4]** Stock pairs trading has become very difficult: stocks rarely remain cointegrated out-of-sample because corporate fundamentals change rapidly. Large losses from pairs that "go bad" overwhelm gains from good pairs.

- **[p.90, ch.4]** NBBO bid-ask sizes for stocks are extremely small (100 shares for AAPL is not unusual), making backtests using quote prices unrealistic for any meaningful size.

- **[p.126, ch.5]** VX futures do not conform to the standard futures price model (Equation 5.9) because VIX is not a traded underlying asset — log futures prices of VX do not fall on a straight line as a function of time-to-maturity.

- **[p.118-119, ch.5]** Roll returns can silently destroy seemingly attractive arbitrage strategies. "Not understanding this subtlety cost me more than $100,000 in trading loss, and ruined my first year (2006) as an independent trader." Verify that cointegration is between an ETF and the spot price, not the futures price.

- **[p.151, ch.6]** Momentum strategies tend to perform miserably for several years after a financial crisis ("momentum crashes"). After the 1929 crash, a representative momentum strategy did not return to its high watermark for more than 30 years. S&P DTI had a drawdown of −25.9% from December 5, 2008.

- **[p.153, ch.6]** Duration of momentum effects gets progressively shorter as more traders learn about them. Price momentum from earnings announcements used to last several days; as of writing, it lasts barely until the market closes.

- **[p.184, ch.8]** Stop losses are useless when markets are closed (overnight gap risk) or when market makers withdraw liquidity simultaneously (flash crash May 6, 2010: Accenture sell stop executed at $0.01 due to "stub quotes").

- **[p.9, ch.1]** Survivorship bias is more dangerous to long-only mean-reversion stock strategies than to momentum strategies. It inflates long-only returns (buys survivors that were cheap) while deflating momentum short returns (excludes failed companies).

- **[p.23, ch.1]** Always choose the appropriate benchmark: a long-only strategy must be compared to buy-and-hold return (information ratio), not the Sharpe ratio alone. Example: a long-only crude oil strategy returning 20% in 2007 underperformed simple buy-and-hold (47%) despite Sharpe 1.5.

## 7. Sensitive Parameters
- **ADF lag k** [p.43, ch.2]: Start with $k=0$, but setting $k=1$ often allows rejecting the null hypothesis because price changes have serial correlations. The value is not optimized but guided by testing. Economic justification: allows the test to account for autocorrelated residuals.

- **Half-life as lookback** [p.47, ch.2]: Set moving average and standard deviation lookback to the half-life (or a small multiple). Economic justification: the half-life is the natural time scale of mean reversion derived from the data, not fitted to backtest performance. Avoids brute-force optimization.

- **Bollinger band entryZscore / exitZscore** [p.71-72, ch.3]: These are free parameters to be optimized in a training set. Chan uses entryZscore=1, exitZscore=0 in examples but acknowledges these require optimization. Curve-fit risk: medium (2 parameters, linked by economic logic of entry/exit).

- **Kalman filter delta (δ)** [p.79, ch.3]: Controls how rapidly the hedge ratio is allowed to change; $\delta = 0.0001$ chosen with hindsight. Chan acknowledges this is optimized in-sample. Curve-fit risk: high (single parameter, sensitive, no strong economic prior). Typical range: 0.00001–0.01.

- **Kalman filter Ve** [p.79, ch.3]: Measurement noise variance = 0.001 chosen with hindsight. Same concern as δ. Can alternatively be estimated via autocovariance least squares (Rajamani and Rawlings 2007/2009).

- **Futures momentum lookback and holddays** [p.158, ch.6]: Justified economically by the persistence of roll return signs (Table 5.1 shows roll returns persist over long periods). However, specific values (TU: 250d/25d; BR: 100d/10d; HG: 40d/40d) are empirically optimized. Curve-fit risk: medium-high (only a few combinations tested, limited trade count).

- **Roll return threshold for TU momentum (3% annualized)** [p.140, ch.6]: Generates Sharpe 2.1 vs. Sharpe 1.04 with sign-only signal. Author acknowledges this is selected with hindsight. Economic justification: provides a buffer against noise in the roll return estimate.

- **Buy-on-gap entryZscore=1 and lookback=90** [p.94, ch.4]: Standard deviation lookback of 90 days is not optimized; 20-day MA for momentum filter is also conventional. Economic justification: 90 days covers a calendar quarter of close-to-close volatility; 20 days is a standard short-term trend gauge.

- **Cross-sectional momentum lookback=252, holddays=25** [p.164, ch.6]: Based on Moskowitz, Yao, and Pedersen (2012); the 12-month lookback has academic support across many asset classes. Curve-fit risk: low (published, replicated across many markets).

## 8. Key Literal Quotes
> "Backtesting a published strategy allows you to conduct true out-of-sample testing in the period following publication. [...] true out-of-sample testing cannot really begin until a strategy is published and cast in stone." — [p.3, ch.1]

> "There is a general approach to trading strategy construction that can minimize data-snooping bias: make the model as simple as possible, with as few parameters as possible." — [p.5, ch.1]

> "In the end, though, no matter how carefully you have tried to prevent data-snooping bias in your testing process, it will somehow creep into your model. So we must perform a walk-forward test as a final, true out-of-sample test." — [p.8, ch.1]

> "Roll returns can be a curse on many seemingly attractive strategies based on knowledge or intuition informed by the underlying spot price. [...] Not understanding this subtlety cost me more than $100,000 in trading loss, and ruined my first year (2006) as an independent trader." — [p.119, ch.5]

> "Instead of recipes, what I hope to convey is the deeper reasons, the basic principles, why certain strategies should work and why others shouldn't." — [p.187, conclusion]

> "experts are uniformly inferior to algorithms in every domain that has a significant degree of uncertainty or unpredictability, ranging from deciding winners of football games to predicting longevity of cancer patients. One can hope that the financial market is no exception to this rule." — [p.189, conclusion]

> "formulas that assign equal weights to all the predictors are often superior, because they are not affected by accidents of sampling" — Kahneman (2011), cited at [p.7, ch.1]

## 9. Cross-references to Other Books in This Knowledge Base
- Kelly formula ($f = m/s^2$) and optimal capital allocation across strategies are treated in greater mathematical depth in `math_money_mgmt.md` and `leverage_space.md`. Chan's treatment [p.172-173, ch.8] is a practical introduction; those books provide the full derivation and extensions to non-Gaussian cases.

- ADF test, Hurst exponent, and stationarity concepts connect to the time series econometrics treatment in `fin_time_series_tsay.md` and `time_series_hamilton.md`, which provide the full distributional theory behind the critical values Chan applies here.

- The Kalman filter as a dynamic hedge ratio estimator [p.75-80, ch.3] connects to signal processing and Bayesian filtering methods; `ml_for_algo_trading.md` and `advances_fin_ml.md` extend these ideas to ML-based state estimation.

- Walk-forward testing and purged cross-validation extend the out-of-sample validation methodology Chan advocates here [p.3-8, ch.1]; `advances_fin_ml.md` covers CPCV and purging/embargo techniques that improve on the simple walk-forward approach.

- The news sentiment momentum section [p.148-149, ch.6] connects directly to `sentiment_analysis_handbook.md`, which covers elementized newsfeeds, NLP-based sentiment scoring, and the academic literature on PEAD at greater depth.

- Cross-sectional momentum and factor models [p.147-148, ch.6] are treated more extensively in `systematic_trading.md` (Carver), which provides a complete framework for combining multiple momentum factors with correlation-based position sizing.
