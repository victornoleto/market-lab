# Trading Systems and Methods (5th Edition)

## Metadata
- **Autor:** Perry J. Kaufman [p.?]
- **Ano:** 2013 (5th ed.) [p.?]
- **Editora:** John Wiley & Sons [p.?]
- **Páginas:** ~1,170 (printed; 1232 PDF pages incl. frontmatter/appendices) [p.?]
- **ISBN:** 978-1-118-04356-1 [p.?]
- **Foco principal:** Encyclopedic reference on systematic/algorithmic trading — methodology, indicators, system construction, testing, risk, and portfolio allocation. [p.?]

## 1. Tese Central

Technical analysis is the systematic, clear-rule evaluation of price, volume, breadth, and open interest for the purpose of price forecasting [p.1]. Successful systematic trading rests on three co-equal pillars: (1) building strategies on sound fundamental or price premises — not on patterns discovered through unconstrained optimization [p.939]; (2) testing with enough representative data (bull, bear, sideways, price shocks) and with rigorous in-sample/out-of-sample discipline such that four-or-fewer-parameter strategies survive [p.939]; and (3) controlling risk through volatility-normalized position sizing, portfolio diversification across uncorrelated strategies, and capped leverage [p.1085-1091].

Kaufman's recurring empirical finding ties the three together: the suitability of a strategy depends on market noise [ch.1, p.13]. Low-noise markets (short-rates, long-rate bonds) favor trend-following; high-noise markets (equity indices) favor mean-reversion. This forces honest strategy-market matching and is measured via the Efficiency Ratio (ER), which is also the engine of KAMA [ch.17, p.780-781].

## 2. Conceitos-Chave

- **Technical analysis (redefined)** — systematic evaluation of price, volume, breadth, and open interest with clear and complete rules [p.1].
- **Efficiency Ratio (fractal efficiency)** — noise measurement; ER=1 when prices move uniformly in one direction, ER=0 for zero net change across wide swings [p.10-11, p.781].
- **Fat tail** — price data shows runs longer than normal distribution predicts; non-Gaussian, non-symmetric [p.7, p.35].
- **In-sample vs. out-of-sample data** — all testing overfits; reserve unseen data for validation. Once used, out-of-sample is "contaminated" and cannot be reused [p.27, p.917].
- **Sample error** — $1/\sqrt{N}$. 4 trades = 50% error; 400 trades = 5% error [p.28].
- **Kurtosis > 7-8 on daily returns** — overfitting flag [p.43].
- **Swing filter** — minimum price reversal for a new swing; absolute or percentage-of-price (more robust) [p.165, p.168].
- **Pivot Point (N-day)** — center point of N-day window; 5-day pivot has 3-day lag [p.172].
- **Price shock / episodic pattern** — unpredictable moves followed by volatility decay; cannot be forecast. Critical for test-design honesty [p.132-133].
- **Point-and-figure** — event-driven (no time factor), reversal only on minimum box movement; 3-box reversal traditional [p.175-178].
- **Donchian's 20/40 Breakout** — basis of the Turtle method [p.353].
- **Bollinger Bands** — 20-day MA ± 2σ of closing prices (same 20 days). 2σ ≈ 87% confidence in skewed distributions [p.323-324].
- **MACD (Appel)** — difference of two EMAs (12/26) with 9-day signal line [p.382].
- **RSI (Wilder)** — oscillator 0-100 from ratio of average up moves to average down moves; 14-day default = one-half of a natural 1-month cycle [p.386].
- **Stochastic (Lane)** — relative position of close in n-day H/L range [p.392].
- **ADX (Wilder Directional Movement)** — byproduct of directional movement; trend-strength indicator. Cross-referenced to Ch 23 [p.387 (mentioned), not deeply covered in Ch 9].
- **KAMA (Kaufman Adaptive Moving Average)** — exponential smoothing with smoothing constant varying by ER² [p.780-782].
- **VIDYA (Chande)** — smoothing varied by short-SD / long-SD ratio of closing prices [p.784-785].
- **MAMA/FAMA (Ehlers MESA Adaptive)** — phase-rate-of-change based adaptive smoothing [p.786].
- **Cointegration** — test of long-term co-movement; foundation of pairs trading. Stronger than correlation [p.583].
- **Commitment of Traders Report (COT)** — commercials usually right; small-lot traders peak bullish near tops [p.639-640].
- **Fibonacci retracements** — 0.618 (and 0.500 by convention); 1.618 extensions. Kaufman notes 0.382, the complement of 0.618, is not strictly a Fibonacci ratio [p.649-651].
- **Elliott Wave Principle** — 5-wave impulse + 3-wave correction; designed for broad indexes, not individual stocks [p.652].
- **Turn-of-month / Holiday / Hirsch Strategies** — calendar effects (buy Nov 1, sell Apr 30; buy 2 days before holiday) [p.479-481].
- **On-Balance Volume (OBV, Granville)** — cumulative volume weighted by price direction [p.537].
- **Market Profile (Steidlmayer)** — TPO distribution; value area = 70% of TPOs around mode [p.826].
- **Kelly Betting System** — optimal log-growth position sizing [p.1090].
- **Optimal f (Vince)** — fraction of capital per trade maximizing geometric mean growth [p.1090].
- **Calmar Ratio** — AROR / max drawdown [p.1037].
- **Sortino Ratio** — AROR / downside deviation [p.1038].
- **Ulcer Index** — RMS of equity drawdowns below new-high [p.1038].
- **Survivorship bias** — hedge fund benchmarks omit funds that blew up [p.941].
- **Three tail-risk-avoidance rules** — be out of market, cap leverage, use uncorrelated strategies [p.1085].

## 3. Fórmulas / Equações

**Efficiency Ratio** [p.10-11, p.781]:
$$ER_t = \frac{|P_t - P_{t-n}|}{\sum_{i=t-n+1}^{t} |P_i - P_{i-1}|}$$

**Price Density** [p.12]:
$$PD = \frac{\sum (\text{High}_i - \text{Low}_i)}{\max(\text{High}, n) - \min(\text{Low}, n)}$$

**Weighted average (time interval)** [p.30]:
$$W = \frac{\sum a_i d_i}{\sum d_i}$$

**Geometric mean** [p.31]: $G = (a_1 \cdot a_2 \cdots a_n)^{1/n}$.

**Variance** [p.38]: $\text{Var} = \frac{\sum (p_i - \bar{P})^2}{n - 1}$.

**Standard deviation** [p.38]: $\sigma = \sqrt{\frac{\sum (p_i - \bar{P})^2}{n}}$ (population; Excel `Stdevp`). 1σ = 68%, 2σ = 95.5%, 3σ = 99.7%.

**Skewness** [p.39]: $S = \frac{\sum (p_i - \bar{P})^3}{(n-1)\sigma^3}$; shorthand: $S = 3(\text{Mean} - \text{Median})/\sigma$.

**Kurtosis** [p.42]: $K = \frac{\sum (p_i - \bar{P})^4}{(n-1)\sigma^4}$; excess = $K - 3$.

**Durbin-Watson** [p.43-44]: $d = \sum (e_i - e_{i-1})^2 / \sum e_i^2$. d=2: no autocorrelation; d<2: positive; d>2: negative.

**t-statistic** [p.47]: $t = \frac{\text{avg}}{\text{SD}} \sqrt{n}$; df = n − 1.

**NAV chain** [p.49]: $\text{NAV}_t = \text{NAV}_{t-1} (1 + r_t)$; $\text{NAV}_0 = 100$.

**Annualization** [p.53]: multiply daily SD by $\sqrt{252}$; monthly $\sqrt{12}$.

**Information Ratio** [p.58]: annualized return / annualized SD of returns.

**Sharpe Ratio** [p.58]: (annualized return − risk-free) / annualized SD.

**Treynor Ratio** [p.58]: (annualized return − risk-free) / portfolio beta.

**Calmar Ratio** [p.1037]: $\text{Calmar} = AROR / \text{max drawdown}$.

**Sortino Ratio** [p.1038]: $SR = (AROR - MAR)/\sigma_{PE-E}$; denominator is SD of (peak equity − current equity).

**Ulcer Index** [p.1038]: $UI = \sqrt{\frac{\sum D_i^2}{n}}$ where $D_i$ = highest equity to date − current equity.

**Simple moving average** [p.284]: $MA_t = \sum_{i=t-n+1}^t p_i / n$.

**SMA rolling update** [p.285]: $MA_t = MA_{t-1} + (p_t - p_{t-n})/n$.

**Average-off (end-drop smoothing)** [p.287]: $\text{AvgOff}_t = \frac{(n-1) \text{AvgOff}_{t-1} + p_t}{n}$.

**Pivot-Point MA (11-bar)** [p.290]:
$$PPMA_t(11) = \frac{-3 p_{t-10} - 2 p_{t-9} - p_{t-8} + 0 p_{t-7} + p_{t-6} + 2 p_{t-5} + 3 p_{t-4} + 4 p_{t-3} + 5 p_{t-2} + 6 p_{t-1} + 7 p_t}{22}$$
General: $PPMA_t(n) = \frac{2}{n(n+1)} \sum_{i=1}^{n} (3i - n - 1) P_{t-n+i}$.

**Exponential smoothing** [p.294]: $E_t = E_{t-1} + a(p_t - E_{t-1})$; initialize $E_1 = p_1$.

**Smoothing-constant ↔ days (Hutson)** [p.295]: $c = 2/(n+1)$.

**Hull Moving Average** [p.286]:
```
WAVG1 = WAVG(close, p)
WAVG2 = WAVG(close, int(p/2))
HMA   = WAVG(2*WAVG2 - WAVG1, int(sqrt(p)))
```

**TRIX** [p.334]:
- $E1_t = E1_{t-1} + s(\ln p_t - E1_{t-1})$ [p.334]
- $E2_t = E2_{t-1} + s(E1_t - E2_{t-1})$ [p.334]
- $E3_t = E3_{t-1} + s(E2_t - E1_{t-1})$ [p.334]
- $TRIX = (E3_t - E3_{t-1}) \times 10000$; recommended $n = 6$, so $s = 2/7$. [p.334]

**KAMA (Kaufman Adaptive Moving Average)** [p.780-781]:
- $KAMA_t = KAMA_{t-1} + sc_t (p_t - KAMA_{t-1})$ [p.780-781]
- $sc_t = [ER_t (\text{fastest} - \text{slowest}) + \text{slowest}]^2$ [p.780-781]
- fastest = $2/(2+1) = 0.6667$; slowest = $2/(30+1) = 0.0645$ [p.780-781]
- ER lookback default = 10 days; slow-end equivalent = 900-period when ER = 0. [p.780-781]
- TradeStation code [p.781]:
  ```
  KAMA = KAMA[1] + ((absvalue(C-C[10])/summation(absvalue(C-C[1]),10)*0.6022)+0.0645)^2 * (C-KAMA[1])
  ```

**VIDYA (Chande)** [p.785]:
- $VIDYA_t = k s C_t + (1 - ks) VIDYA_{t-1}$ [p.785]
- $s$ = 0.20 (9-day base EMA constant) [p.785]
- $k = \text{stdev}(C, n) / \text{stdev}(C, m)$, default n=9, m=30. [p.785]

**Fractal Dimension (Ehlers FRAMA)** [p.784]: $D = \log(N_2/N_1)/\log(s_1/s_2)$.

**MAMA/FAMA (Ehlers MESA Adaptive)** [p.786]:
- $sc = \text{fast\_limit} / \text{phase\_rate\_of\_change}$; clamped to [0.05, 0.50]. [p.786]
- FAMA uses MAMA with smoothing constant × 0.5. [p.786]

**Wilder Swing Index** [p.193]:
$$SI_t = 50 \times \frac{(C_t - C_{t-1}) + 0.5(C_t - O_t) + 0.25(C_{t-1} - O_{t-1})}{TR_t} \times \frac{K}{M}$$
K = larger of $|H_t - C_{t-1}|$, $|L_t - C_{t-1}|$; M = limit move (100); TR_t via one of 3 sub-formulas.

**True Range** [p.107]: largest of $|H_t - C_{t-1}|$, $|L_t - C_{t-1}|$, $H_t - L_t$.

**Accumulated Swing Index** [p.194]: $ASI_t = ASI_{t-1} + SI_t$.

**Bollinger Bands** [p.323]: $MA_{20}(C) \pm 2\sigma(C, 20)$.

**Modified Bollinger (McNicholl)** [p.325-326]:
- $M_t = \alpha C_t + (1-\alpha) M_{t-1}$; $U_t = \alpha M_t + (1-\alpha) U_{t-1}$ [p.325-326]
- $D_t = ((2-\alpha)M_t - U_t)/(1-\alpha)$ [p.325-326]
- $m_t = \alpha|C_t - D_t| + (1-\alpha) m_{t-1}$; $u_t = \alpha m_t + (1-\alpha) u_{t-1}$ [p.325-326]
- $d_t = ((2-\alpha)m_t - u_t)/(1-\alpha)$ [p.325-326]
- $BU_t = D_t + f d_t$; $BL_t = D_t - f d_t$. Default $\alpha = 0.15$, $f = 2.5$. [p.325-326]

**Volatility System (Bookstaber)** [p.333]:
- $V_t = (1/n) \sum TR_i$ [p.333]
- Sell if close drops by more than $k \cdot V_{t-1}$; Buy reverse. $k \approx 3$. [p.333]

**CCI (Commodity Channel Index)** [p.172]:
- $ADP_t = (H_t + L_t + C_t)/3$; n-day average. [p.172]
- $AvgDev_t$ = n-day average of $|H_i + L_i + C_i - ADP_t|$. [p.172]
- $CCI_t = \frac{(H_t + L_t + C_t)/3 - ADP_t}{0.015 \times AvgDev_t}$. [p.172]

**MACD** [p.382]: MACD = EMA(close,12) − EMA(close,26); Signal = EMA(MACD, 9). Histogram = MACD − Signal.

**RSI (Wilder)** [p.386]:
$$RSI = 100 - \frac{100}{1 + RS}, \quad RS = AU/AD$$
- $AU_t = AU_{t-1} - AU_{t-1}/14 + \max(p_t - p_{t-1}, 0)$ [p.386]
- $AD_t = AD_{t-1} - AD_{t-1}/14 + \max(p_{t-1} - p_t, 0)$ [p.386]

**Stochastic (Lane)** [p.392]:
- Raw $\%K_t = 100 \times (C_t - L_t(n))/R_t(n)$ [p.392]
- $\%D$ (also %K-slow) = 3-day average of raw %K [p.392]
- %D-slow = 3-day average of %D [p.392]

**CMO (Chande)** [p.388]: $CMO = 100 \times (S_u - S_d)/(S_u + S_d)$.

**On-Balance Volume** [p.537]: $OBV_t = OBV_{t-1} + \text{sign}(C_t - C_{t-1}) V_t$.

**Money Flow Index** [p.540]: typical price × volume accumulation separated by up/down days → RSI-style ratio.

**Volume Accumulator (Chaikin)** [p.540]: $VA_t = VA_{t-1} + ((C_t - L_t)/(H_t - L_t) - 0.5) \times 2 V_t$.

**Accumulation Distribution** [p.541]: $AD_t = AD_{t-1} + (C_t - O_t)/(H_t - L_t) \times V_t$.

**Intraday Intensity** [p.541]: $II_t = II_{t-1} + ((C_t - L_t) - (H_t - C_t))/(H_t - L_t) \times V_t$.

**McClellan Oscillator** [p.549]:
- $NA_t$ = Advances − Declines [p.549]
- $E1_t$ = 0.10 EMA of $NA$; $E2_t$ = 0.05 EMA of $NA$ [p.549]
- Oscillator = $E1_t - E2_t$. [p.549]

**Advance-Decline Index** [p.548]: $ADI_t = ADI_{t-1} + (\text{Advances}_t - \text{Declines}_t)$.

**Pairs Trading Stress Indicator (Kaufman)** [p.585]: stochastic of the difference of two leg stochastics; entry when > 95 or < 5.

**Pivot Points (intraday)** [p.667]:
- $P = (H + L + C)/3$ [p.667]
- $R_1 = 2P - L$; $S_1 = 2P - H$ [p.667]
- $R_2 = (P - S_1) + R_1$; $S_2 = P - (R_1 - S_1)$ [p.667]

**Force Index (Elder)** [p.836]: $FI_t = V_t (C_t - C_{t-1})$; 2-day EMA smoothing (const 0.333).

**Elder-Ray** [p.837]: Bull Power = $H_t - EMA_{13}$; Bear Power = $L_t - EMA_{13}$.

**COT Index (Briese)** [p.639]:
$$\text{COT Index}_t = 100 \times \frac{NL_t - \min(NL, n)}{\max(NL, n) - \min(NL, n)}$$
n = 1.5 to 4 years; essentially a stochastic of net long positions.

**Kelly growth function** [p.1090]:
$$G(f) = P \ln(1 + Bf) + (1-P)\ln(1-f)$$

**Kelly closed form** [p.1090]:
$$f = \frac{p(PLR + 1) - 1}{PLR}$$
Example [p.1091]: $p = 0.5$, PLR = 2 → $f = 0.25$.

**Optimal f (Vince)** [p.1090]:
$$\text{optimal } f = \arg\max_{f \in [0.01, 1]} \left( \prod_{i=1}^{n} \left(1 + \frac{R_i}{-\text{Largest loss}} f \right) \right)^{1/n}$$

**Markowitz approximation / optimal leverage** [p.1092]:
- Expected leveraged log return $= M \mu - \frac{1}{2} M^2 \sigma^2$ [p.1092]
- Optimal leverage $M^* = \mu/\sigma^2$ [p.1092]

**Portfolio expected return** [p.1088]: $E(R) = \sum w_i E(R_i)$, $\sum w_i = 1$.

**Portfolio variance** [p.1088]: $\sigma^2_R = \sum w_i^2 \sigma_i^2 + \sum\sum_{i\ne j} w_i w_j \text{cov}_{ij}$ where $\text{cov}_{ij} = \text{corr}_{ij} \sigma_i \sigma_j$.

## 4. Algoritmos e Pseudocódigo

**KAMA (Kaufman Adaptive Moving Average)** [p.780-781]:
```
Input: close series, ER_period=10, fast=2, slow=30
fastest = 2/(fast+1)   # = 0.6667
slowest = 2/(slow+1)   # = 0.0645
for t in range(ER_period, len(close)):
    numer = abs(close[t] - close[t - ER_period])
    denom = sum(abs(close[i] - close[i-1]) for i in t-ER_period+1..t)
    ER    = numer / denom
    sc    = (ER * (fastest - slowest) + slowest) ** 2
    KAMA[t] = KAMA[t-1] + sc * (close[t] - KAMA[t-1])
```

**Channel Breakout with regression** [p.167-169]:
```
1. Select data from last swing high/low (use swing program or pivot points) [p.167-169]
2. X = [1, 2, ..., n]; Y = closes of same length. [p.167-169]
3. Run linear regression -> slope a, intercept b. [p.167-169]
4. BL = distance from regression line to lowest low below line;
   BU = distance from regression line to highest high above line. [p.167-169]
5. Projected upper channel band at n+1 = a*X + b + BU + a [p.167-169]
   Projected lower channel band at n+1 = a*X + b - BU + a
6. Signal: close breaks projected band opposite to slope direction -> trend change. [p.167-169]
```

**Donchian 20/40 Breakout (Turtles foundation)** [p.353]:
```
Buy when today's high > max(high, 40 days)
Sell short when today's low < min(low, 40 days)
Exit long when today's low < min(low, 20 days)
Exit short when today's high > max(high, 20 days)
```

**DeMark Sequential Setup + Countdown** [ch.4, p.173-175]:
```
SETUP:
  9 consecutive closes < close 4 bars ago
INTERSECTION (validation):
  Day 8 or later high >= low of 3 or more days earlier
COUNTDOWN:
  Count days where close < close 2 days ago (not necessarily consecutive)
  When count reaches 13 -> BUY, unless invalidated by:
    - Close exceeds highest intraday high during setup [ch.4, p.173-175]
    - Sell setup occurs (9 consec up closes vs. 4 back) [ch.4, p.173-175]
    - Another buy setup occurs before countdown completes (recycle) [ch.4, p.173-175]
ENTRY: close of signal day, OR close > close 4 days ago, OR close > high 2 days earlier
EXIT stop:
  True range of lowest-range day during setup+countdown
  subtracted from low of that day
```

**Swing Filter Chart Construction** [p.165]:
```
1. Choose swing filter (% or absolute value). [p.165]
2. Begin: current bar high = swing high, low = swing low; assume upswing. [p.165]
3. For each new bar:
   IF in upswing:
     IF high > current swing high: extend upswing to new high.
     ELSE IF (swing high - current low) >= swing filter:
        start new downswing column from swing high to current low.
   ELSE (downswing):
     IF low < current swing low: extend downswing to new low.
     ELSE IF (current high - swing low) >= swing filter:
        start new upswing column.
```

**Step-Forward (Walk-Forward) Testing** [p.918]:
```
1. Total period = e.g. 20 years. [p.918]
2. In-sample window = e.g. 2 years (or 5y if long-term bias). [p.918]
3. Start at earliest data:
   - Optimize parameters on in-sample window. [p.918]
   - Apply best parameters to NEXT 6 months (OOS). [p.918]
   - Accumulate OOS returns. [p.918]
4. Roll forward 6 months; repeat step 3. [p.918]
5. Final performance = accumulated OOS stream. [p.918]
6. NEVER iterate design after seeing OOS results -> feedback = overfit. [p.918]
```

**Pairs Trading via Stress Indicator** [p.584-585]:
```
Inputs: two legs A, B; n = 14
Compute 14-day raw stochastic for A (S1) and B (S2)
D_t   = S1 - S2
Stress_t = 100 * (D_t - min(D, n)) / (max(D, n) - min(D, n))
ENTRY:
  Stress > 95 -> short A, long B
  Stress < 5  -> long A, short B
POSITION SIZING (equal dollar-risk via ATR) [p.586]:
  For each leg, compute ATR20_dollars.
  Size = FIXED_INVESTMENT / ATR20_dollars.
  Example: $5 stock, ATR=$0.25 -> 4000 shares; $25 stock, ATR=$1 -> 1000 shares.
EXIT:
  Stress returns near center.
```

**Kelly / Optimal f Search** [p.1090]:
```
Input: trade returns R_1..R_n; largest_loss (positive value)
best_f  = 0
best_G  = -inf
for f in 0.01..1.0 step 0.01:
  G = geometric_mean( (1 + R_i / -largest_loss * f) for i in 1..n )
  if G > best_G: best_G = G; best_f = f
return best_f
```

**Triple Screen (Elder)** [p.835-838]:
```
Screen 1 (Long-term trend direction):
  Compute weekly MACD histogram (13-week EMA).
  Direction = sign(MACD_week_t - MACD_week_{t-1})

Screen 2 (Intermediate timing oscillator):
  Option A: Force Index = Volume * (Close - PrevClose), 2-day EMA.
    Buy setup: 2-day FI below centerline AND not below multi-week low.
  Option B: Stochastic_14 below 30.
  Option C: Elder-Ray; Bear Power < 0 AND rising (not positive).

Screen 3 (Fast entry):
  Buy-stop just above previous day's high on 60-min bars.

Stop-loss (long):
  Initial: below low of entry day OR previous day's low, whichever lower.
  Move to break-even ASAP.
  Trail to protect 50% of peak profit.
```

**Portfolio Allocation via Excel Solver (Markowitz mean-variance)** [p.1109-1110]:
```
1. Load monthly % returns for assets A1..An. [p.1109-1110]
2. Compute: monthly means, standard deviations, pairwise correlations. [p.1109-1110]
3. Decision variables: allocation weights w_1..w_n. [p.1109-1110]
4. Objective: maximize portfolio return / standard deviation ratio,
   using the full covariance (variance + pairwise correlation terms). [p.1109-1110]
5. Constraints: sum w_i = 1; each w_i >= 0 (or a specified minimum). [p.1109-1110]
6. Solver -> optimal weights on efficient frontier. [p.1109-1110]
```
(Kaufman's Ch 24 later contrasts this traditional mean-variance approach with his GASP Genetic Algorithm Solution to Portfolios, arguing mean-variance breaks when strategy returns include many zero-days from being out of the market.)

## 5. Regras de Trading Explícitas

**Market selection by noise**:
- **REGRA [p.13]**: Low-noise markets (short-rates, long-maturity bonds, USD crossrates, energy, metals) -> trend-following.
- **REGRA [p.13]**: High-noise markets (equity indices) -> mean-reverting / countertrend.
- **REGRA [p.13-14]**: Long-term traders use low-frequency (weekly/monthly) + long-term trends. Short-term traders use high-frequency + mean-reverting.

**Swing / Event-Driven Trend Rules**:
- **REGRA [p.168]**: Conservative swing entry -- buy when current upswing high exceeds previous upswing high; sell short when current downswing low falls below previous downswing low.
- **REGRA [p.191]** (Livermore): Enter only in direction of major trend (higher highs+higher lows, or lower lows+lower highs); add each penetration confirmation; stop-loss at penetration beyond prior pivot.
- **REGRA [p.172]** (Keltner Minor Trend): Buy when daily trades above most recent high; stay long until trades below most recent low. Always reverse.
- **REGRA [p.195]** (Wilder Swing Index): Long when ASI_t > HSP_{t-2}; short when ASI_t < LSP_{t-2}; SAR at most recent opposite swing point.

**Point-and-Figure**:
- **REGRA [p.199]**: Buy when X one box above highest X of last X column. Sell when O below lowest O of last O column.
- **REGRA [p.201]**: Filter signals with 45-degree trendlines -- only take longs when 45-degree trendline up, shorts when down.

**Moving-average and trend systems**:
- **REGRA [p.285]**: Use MA length < half the cycle period to preserve cycle visibility.
- **REGRA [p.285]**: Match MA period to trading horizon -- 63-day = quarterly; 252-day = annual; 200-day = stock-market macro benchmark.
- **REGRA [p.352-353]** (Donchian 5/20): Buy if not long AND $C_t > MA5_{t-1} + ATR_{t-1}$ AND $C_t > MA20_{t-1} + ATR_{t-1}$. Exit long if either MA band violated.
- **REGRA [p.353]**: Position Size = Investment / (ATR * Big Point Value).
- **REGRA [p.353]** (Donchian 20/40 = Turtle basis): Buy when high > max high 40 days; exit long when low < min low 20 days.
- **REGRA [p.354]**: Golden Cross (50 crosses above 200) -- buy SPY; when 50 crosses below 200 (Death Cross) -> short/flat. Yielded 66.7% return over 1999-2010 vs. passive -7.8%.
- **REGRA [p.355]** (Woodshedder ROC): Buy when 5-day ROC below 252-day ROC for 2 consecutive days; exit long when 5-day > 252-day for 2 consecutive days.
- **REGRA [p.326-327]** (Bollinger reversal): Buy on close > upper band; short on close < lower band. Exit at center trendline -> cuts order size 50%.
- **REGRA [p.333]** (Volatility System): $V_t = \frac{1}{n}\sum TR_i$; sell if close drops by $k \cdot V_{t-1}$ (k approx 3).

**Oscillators / Momentum**:
- **REGRA [p.383]** (MACD): Buy when MACD crosses up through signal; require MACD to have first penetrated opposite threshold (e.g. +/-2.00) to filter whipsaws.
- **REGRA [p.386-387]** (RSI): Wilder 70/30 overbought/oversold; per Aan (1985) [p.387-388] prefer 80/20 (1.5 sigma).
- **REGRA [p.388]**: For sustained moves of 14+ days, RSI stays saturated -- do not fade blindly.
- **REGRA [p.392]** (Stochastic): Buy when %D below 20 and cross back up; sell when %D above 80 and cross back down. Always confirm with longer-term trend direction.
- **REGRA [p.640]** (Ruggiero COT): Buy when COT Index Commercials [lag 1+ week] > trigger AND COT Index Small Traders < trigger. Commercials' actions lead.
- **REGRA [p.640]**: Exit mean-reverting trade at neutral (50), not opposite extreme.

**KAMA (trading)**:
- **REGRA [p.783]**: Trade KAMA via trendline direction -- buy when it turns up, sell when it turns down.
- **REGRA [p.783]**: Keep ER period <= 14 days (default 10); leave slowest = 30 fixed; raise fastest from 2 to reduce sensitivity; use small threshold filter (~0.1 SD of trendline changes) to prevent false flips.

**Risk Control**:
- **REGRA [p.53]**: Target volatility for book default = 12% annualized.
- **REGRA [p.1037]**: Initial stop below low of entry day OR previous day's low, whichever is lower. Move to break-even ASAP; trail to protect 50% of peak profit.
- **REGRA [p.1057-1059]**: Size position inversely proportional to ATR for equal-risk allocation across markets.
- **REGRA [p.1091]**: Use optimal f as UPPER BOUND; never size larger, or if you get average results you can expect to go broke eventually.
- **REGRA [p.1091]**: Simpler alternative -- trade constant position size with reserve large enough to absorb extreme moves.
- **REGRA [p.942]**: Investor capitalization = 3 * maximum drawdown.
- **REGRA [p.942]**: Require >= 400 trades to reduce sample error to ~5%.

**Seasonal / Calendar**:
- **REGRA [p.480]** (Holiday -- Kaeppel): Buy on close 3 days before an exchange holiday; sell on close 2 days later.
- **REGRA [p.480]** (Hirsch): Buy first trading day of November; sell last trading day of April.
- **REGRA [p.482]** (McGinley January): If first 5 trading days of January are up >= 4%, year has always been up. Buy, hold full year.
- **REGRA [p.480]** (Month-End): Buy last (or 2nd-to-last) day of month; sell 4th trading day of next month.

**Day Trading**:
- **REGRA [p.741]**: Prefer mean-reverting day strategies -- passive entry orders have near-zero slippage and may earn liquidity rebate.
- **REGRA [p.740]**: Favor markets with highest volume AND highest volatility simultaneously.

**NUNCA**:
- **NUNCA [p.1091]** (Elder): Never average down. Never meet margin calls. Liquidate worst position first.
- **NUNCA [p.27]**: Never reuse out-of-sample data after the first validation run -- feedback contaminates.
- **NUNCA [p.919]**: Never iterate step-forward test design after seeing results -- recreates overfitting.
- **NUNCA [p.941]**: Never change test ranges after tests started -- prevents data-snooping bias.

## 6. Pitfalls e Anti-patterns

- [p.27] "All testing is overfitting the data." In-sample/out-of-sample discipline is mandatory; OOS can only be used once.
- [p.43] Kurtosis on daily returns > 7-8 -> "it begins to look as though the trading method is overfitted."
- [p.132-133] Backtesting over periods with price shocks (2001, 2008) produces apparent predictive power -- your system may "profit" from events it never could have forecast in real time.
- [p.172] CCI and SD-channel overbought conditions can persist for weeks during strong trends. Mechanical OB/OS fading "gives frequent small profits and an occasional very large loss."
- [p.170] Event-driven systems (swing, point-and-figure) have higher per-trade risk than time-based systems -- entry-to-reversal distance can run large before a signal fires.
- [p.290] Pivot-point MA with negative weights can put trendline out of phase with price in short intervals -- best for long-term cyclic markets only.
- [p.326-327] Bollinger bands "bulge" after volatility spikes and narrow slowly. Modified Bollinger (McNicholl) does not remove the bulge but corrects it faster.
- [p.329] Delayed entries (next-day open) improve price 75% of the time but cost overall profits -- fast breakouts that never retrace are missed.
- [p.387-388] Wilder's default 70/30 RSI thresholds = only 0.675 sigma of RSI distribution -- too tight. Prefer 80/20 (~1.5 sigma).
- [p.381] Mean-reversion against a strong trend: "the trend is not your friend if it fights with your mean-reversion."
- [p.541] PVT and % volume indicators fail on back-adjusted futures (prices can go negative).
- [p.584] Pairs trading is mean-reverting -- hold few days only; longer holds let trend component dominate.
- [p.585-586] Even closely linked pairs diverge on idiosyncratic events (Barrick Gold earnings miss). Pairs do NOT eliminate idiosyncratic risk.
- [p.652] Elliott Wave designed for broad indexes -- "Elliott never intended to apply his principle to individual stocks."
- [p.743] Economic report releases (FOMC, Chicago PMI, API/AGA) cause fillable-price gaps. Directional day trading suffers 10-20% unables during news periods.
- [p.783] Exponential smoothing flips direction when price penetrates -- tiny smoothing constants in KAMA produce false flips without a trend-change filter.
- [p.802] 2008 crude oil 140% annualized vol was artifact of lagging 20-day SD, not real risk.
- [p.914] Back-adjusted futures can go negative -> percentage-based stops and percentage volatility calcs break.
- [p.914] Back-adjusted split-adjusted stocks: 1990 $50 stock with 2x splits becomes $12.50 -- loses volatility characteristics.
- [p.916] Monte Carlo random rearrangement of data destroys bull->bear transitions -> abandoned by practitioners.
- [p.919] Step-forward short-interval bias: 2-year in-sample favors fast trend models; use 5-year in-sample for long-term strategies.
- [p.938] Bull-market-biased parameters: "The mistake is extrapolating probable future performance on the basis of an isolated and well-chosen example from the past." -- Schwager.
- [p.939] "Discovering a price pattern or cycle through optimization may seem to be a revelation, but it is more likely to be an illusion."
- [p.939] Best systems use 4 or fewer parameters. More is worse.
- [p.941] Survivorship bias -- hedge fund benchmarks omit funds that blew up.
- [p.941] Asymmetric return fallacy -- -50% then +50% = -25% net.
- [p.1038] Historic max drawdown is a lower bound -- "future always brings larger drawdowns."
- [p.1109] Globalization has increased correlations -- past patterns of returns unlikely to represent all future patterns (implicit critique of stationary-correlation assumptions in classic MPT).
- [p.1109] "Globalization has increased correlations... past patterns of returns are not likely to represent all of the patterns that will be seen in the near future."
- [p.1091] If you trade above optimal f and get average results, you eventually go broke. If below, risk drops arithmetically while profits drop geometrically.
- [p.1091] Theory of Runs (Ch 22): 100 trades expect 1 run of 6. Sequential losing runs of 4-5 are not pathological -- plan for them.

## 7. Parâmetros Sensíveis

**Justified by fundamentals / structural reasons**:
- **14-day RSI** [p.386]: Wilder's 14 = one-half of a natural 1-month cycle. Economic justification is a monthly cycle in human behavior; Kaufman notes 14 "may not be" the true half-cycle for every market.
- **20-day Bollinger, 2 sigma** [p.323-324]: "If it's not 20-day and 2 sigma, it's not a Bollinger band" -- established convention; 2 sigma approx 87% coverage in skewed distributions.
- **50/200 Golden Cross** [p.354]: Quarterly (63-day) and annual (252-day) would be purer economic choices; 50/200 survives by convention and avoids major bear markets.
- **KAMA 10-day ER lookback** [p.783]: "matches rare 10-consecutive-direction runs" -- ER > 10 just scales smaller.
- **12% target volatility** [p.53]: Kaufman's "modest risk level"; conservative benchmark for all book examples.
- **3x max drawdown capitalization** [p.942]: Industry standard investor cushion.
- **63 days = quarterly, 252 days = annual** [p.285]: Natural calendar periods tied to fiscal-quarter rebalancing behavior.

**Curve-fit risk high**:
- **Elliott Wave counting** [p.652]: Visual ambiguity; different practitioners produce different wave counts on same chart. Non-falsifiable.
- **Specific Fibonacci retracement targets (0.382, 0.618)** [p.651-652]: "Self-fulfilling" -- many traders act at these levels; not a cause-effect relationship. (Kaufman explicitly notes that 0.382, the complement of 0.618, is not strictly a Fibonacci ratio.)
- **MACD 12/26/9** [p.382]: Default but not optimal for most markets. Test 19/39 for NASDAQ per Appel.
- **Turtle 20/40** [p.353]: Has survived multiple decades in published form but has been heavily over-emulated -- edge likely decayed post-publication.
- **COT Index lag 1-several weeks** [p.640]: Depends on market; requires recalibration per asset.

## 8. Citações Literais Importantes

> "The market reflects all the jobber knows about the condition of the textile trade; all the banker knows about the money market... the market reduces to a bloodless verdict all knowledge bearing on finance, both domestic and foreign." -- Charles Dow, cited [p.4-5]

> "Most men make money in their own business and lose it in some other fellow's." -- Richard Wyckoff, cited [p.5]

> "Discovering a price pattern or cycle through optimization may seem to be a revelation, but it is more likely to be an illusion. By testing enough patterns, it is statistically probable that one of them will seem to fit. Without a fundamental reason for the existence of that pattern, it is not safe to use it." -- [p.939]

> "It must be based on a sound premise. Each rule and formula must capitalize on a real fundamental or price phenomenon." -- [p.939]

> "The mistake is extrapolating probable future performance on the basis of an isolated and well-chosen example from the past." -- Jack Schwager, cited [p.938]

> "The most serious concern about step-forward testing is feedback." -- [p.919]

> "If you invest less than the optimal amount, then your risk decreases arithmetically, but your profits decrease geometrically, which is another bad scenario." -- [p.1091]

> "Globalization has increased the correlations, and the past patterns of returns are not likely to represent all of the patterns that will be seen in the near future." -- [p.1109]

> "To be uncertain is to be uncomfortable, but to be certain is to be ridiculous." -- Chinese proverb, cited [p.44]

## 9. Conexões com Outros Livros Desta Base

- **Optimization / Overfit** (Ch 21) connects with López de Prado's CPCV and 7-layer anti-overfit framework in `advances_fin_ml.md`. Kaufman arrives at "4 parameters or fewer" [p.939] via Futures Truth empirical evidence; López de Prado derives similar parsimony via Sharpe-deflation math.
- **Parsimony in trend systems** connects with `systematic_trading.md#design-principles` (Carver), who also advocates <= 4 parameters and explicit economic justification. [p.?]
- **Kelly / Optimal f** connects with `math_money_mgmt.md` (Vince's own book) and `leverage_space.md`. Kaufman presents Kelly / optimal f as an upper bound [p.1091] -- same conclusion as other money-management texts.
- **Cycle analysis / MESA / Fisher / Hilbert transforms** connects with `rocket_science.md` (Ehlers' own book), `cycle_analytics.md`, and `cybernetic_analysis.md` -- Ehlers is cited for FRAMA, MAMA, Hilbert transform [p.786].
- **Market Profile / TPO / Steidlmayer** [Ch 18, p.798-800] -- standalone in this base. [p.?]
- **Stochastic arbitrage, pairs, cointegration** [Ch 13] connects with `algo_trading_chan.md`, `quant_trading_chan.md`, and `machine_trading.md` (Chan's work on Engle-Granger cointegration tests). [p.?]
- **VIX as contrarian indicator** [Ch 20, p.866-867] connects with `volatility_trading.md` and `sentiment_analysis_handbook.md`. [p.?]
- **Mean-variance / MPT** [Ch 24] connects with `risk_parity.md` (equal-risk weighting alternative to MPT) and `eval_opt_strategies.md`. [p.?]
- **Candlestick / Bulkowski chart pattern rankings** [Ch 4, p.178-179] connects with `tech_analysis_patterns.md`. [p.?]
- **Elliott Wave / Fibonacci** connects with `universal_trend_tactics.md` and `cybernetic_trading.md` if they cover Wave Principle. [p.?]
