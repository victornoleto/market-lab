# Technical Analysis for Algorithmic Pattern Recognition

## Metadata
- **Authors:** Prodromos E. Tsinaslanidis, Achilleas D. Zapranis [p.i, cover]
- **Year:** 2016
- **Publisher:** Springer International Publishing Switzerland [p.i]
- **Pages:** 213 (PDF); ~204 printed
- **ISBN:** 978-3-319-23635-3 (print); 978-3-319-23636-0 (eBook) [p.i]
- **Primary focus:** Rule-based algorithmic recognition of classical technical patterns (horizontal, zigzag, circular) with rigorous statistical assessment (t-tests, Bernoulli trials, bootstrap with GARCH-m/E-GARCH null models).

## 1. Core Thesis
The authors argue that the technical-pattern analysis literature suffers from critical problems: descriptive and theoretical approaches instead of quantitative ones, illustrations only of "best-case" examples, inherent subjectivity in visual identification, and cognitive biases (clustering illusion) [Preface, p.vii-viii]. The book proposes systematic treatment via rule-based recognition mechanisms (algorithmic and therefore non-subjective) and a robust statistical framework (parametric tests + bootstrap with GARCH null models) to evaluate whether patterns generate abnormal returns [p.2, ch.1; p.25-26]. **The authors' empirical conclusion**: "overall TA does not generate systematically, statistically significant abnormal returns" [p.2]. The book's strongest result: the Head-and-Shoulders pattern can be identified in 21.77% (normal) and 22.94% (inverse) of simulated series under pure GBM — so it appears in pure randomness [p.93, ch.5].

## 2. Main Concepts
- **Weak-form EMH** — current prices reflect all information contained in historical prices; in the limit, this invalidates prediction based on TA [p.4-5, ch.1]
- **Random Walk RW1/RW2/RW3** — three hierarchical versions (IID / INID / uncorrelated but dependent); RW2 is the usual one in finance because it allows conditional heteroskedasticity [p.7-8]
- **Self-fulfilling prophecy vs. self-destructive** — two opposing theses on how collective technician beliefs affect prices [p.20-21, §1.5.2]
- **Clustering illusion** — cognitive bias that makes humans perceive patterns where none exist; explains the irrational persistence of TA [p.21, §1.6]
- **Regional local (peak/trough)** — an observation that is a maximum (minimum) within a 2w+1 window centered on it; the basis for all pattern recognition [p.32, ch.2]
- **Perceptually Important Points (PIPs)** — alternative method of identifying salient points via maximum distance (ED, PD, or VD) to adjacent PIPs [p.33-36, §2.3.2]
- **HSAR (Horizontal Support/Resistance)** — horizontal price zone where clustering of locals forms a support/resistance band, not a single level [p.61-63, ch.4]
- **Bounce frequency** — ratio of bounces/hits; measures an HSAR's reversal strength [p.66]
- **Trading Range Breakout (TRB)** — simple SAR version: min/max of the last w bars [p.61, §4.2.4]
- **Fibonacci retracement levels** — 0%, 23.6%, 38.2%, 50%, 61.8%, 100%, 161.8%, 261.8%, 423.6% [p.59, §4.2.1]
- **Neckline (HS pattern)** — line connecting the two intervening troughs; acts as support before penetration and resistance afterward [p.57, ch.4; p.87, ch.5]
- **Geometric Brownian Motion (discrete)** — $\Delta P/P = \mu\Delta t + \sigma\varepsilon\sqrt{\Delta t}$, used as the null simulation model [p.92, eq.5.14]
- **Savitzky-Golay smoothing** — local polynomial filter; preprocessing step to estimate derivatives before DDTW [p.200, eq.9.10]
- **DTW / DDTW / Subsequence DDTW** — Dynamic Time Warping and variants to align series of different lengths; DDTW uses local derivatives (robust to different price levels) [ch.9, p.193-202]
- **GARCH-m and E-GARCH null models** — bootstrap null models that capture leptokurtosis, autocorrelation, and conditional heteroskedasticity [ch.8, p.161]
- **Joint hypothesis problem** — when testing excess returns you must choose an asset-pricing model (CAPM, APT); both have limitations; the authors prefer raw returns [p.164, ch.8]
- **"Trader's remorse"** — after SAR penetration, prices return to the level that reverses roles (S→R or R→S) [p.62, ch.4]
- **Whipsaw** — rapid reversals in opposite directions over the same moving average, generating high costs [p.149, ch.7]

## 3. Formulas / Equations
**Regional peak/trough (rolling window)** [p.32, eq.2.1-2.2]

$$\text{Local Peak if } p_t > \max\{p_{[t-w:t-1]}\} \;\&\; p_t > \max\{p_{[t+1:t+w]}\}$$

$$\text{Local Trough if } p_t < \min\{p_{[t-w:t-1]}\} \;\&\; p_t < \min\{p_{[t+1:t+w]}\}$$

**Perpendicular distance for PIP** [p.34, eq.2.4]

$$d_P(x_i; x_t, x_{t+T}) = \frac{|s \cdot i + c - p_i|}{\sqrt{s^2 + 1}}$$

where $s=(p_{t+T}-p_t)/T$, $c=p_t - t(p_{t+T}-p_t)/T$.

**HSAR bin number (logarithmic spacing)** [p.63, eq.4.13]

$$n = \frac{\ln(L_2^*/L_1^*)}{\ln(1+x)}$$

where $L_1^* = \min(L)(1+x/2)$, $L_2^* = \max(L)(1+x/2)$, $x$ = desired percentage per bin.

**TRB levels** [p.61, eq.4.4-4.5]

$$\text{Support}_t = \min\{p_{t-1}, \dots, p_{t-w}\}, \quad \text{Resistance}_t = \max\{p_{t-1}, \dots, p_{t-w}\}$$

**HS tops — 5 conditions (Osler & Chang 1995, adopted by Lucke 2003)** [p.87-88, ch.5, eq.5.1-5.7]

- C1 (head higher) [p.87, eq.5.1]: $P_2 > \max(P_1, P_3)$
- C3 (balance) [p.88, eq.5.4]: $P_1 \geq 0.5(P_3+T_2)$ & $P_3 \geq 0.5(P_1+T_1)$
- C4 (symmetry) [p.88, eq.5.5]: $t_{P_2}-t_{P_1} < 2.5(t_{P_3}-t_{P_2})$ & $t_{P_3}-t_{P_2} < 2.5(t_{P_2}-t_{P_1})$
- C5a (neckline penetration) [p.88, eq.5.6]: $B < \frac{T_2-T_1}{t_{T_2}-t_{T_1}}(t_B-t_{T_1})+T_1$
- C5b (timing) [p.88, eq.5.7]: $t_B < t_{P_3}+(t_{P_3}-t_{P_1})$

**DT balance & depth** [p.97, eq.5.27, 5.29]

$$|P_1-P_2|/\min(P_1,P_2) \leq 0.04, \quad (T_1-P_1)/P_1 \leq -0.1$$

(i.e. 4% lateral tolerance, 10% minimum pullback between tops; values from Bulkowski 2000)

**Rounding Bottom — radius of the circumscribed circle** [p.129, eq.6.1]

$$R_1 = \frac{a}{2\sin(A)}$$

**RB depth** [p.132, eq.6.5]

$$\text{Depth} = \frac{P_{\max}-P_{\min}}{P_{\min}}$$

**RB fit** [p.132, eq.6.4]

$$\text{Fit} = \frac{\text{obs within bounds}}{\text{total obs}}$$

Default thresholds: bounds = 0.3, $t_{\text{width}}=15$, $t_{\text{fit}}=0.9$ [Table 6.2, p.134]

**Geometric Brownian Motion (discrete)** [p.92, eq.5.14]

$$\frac{\Delta P}{P} = \mu \Delta t + \sigma \varepsilon \sqrt{\Delta t}, \quad \varepsilon \sim N(0,1)$$

**SMA** [p.148, eq.7.1]

$$\text{SMA}_t|w = \frac{P_t + P_{t-1} + \dots + P_{t-w+1}}{w}$$

**EMA** [p.150, eq.7.4]

$$\text{EMA}_{t|w,\lambda} = (1-\lambda)\text{EMA}_{t-1|w,\lambda} + \lambda P_t, \quad \lambda^* = \frac{2}{w+1}$$

**MACD & signal line** [p.152, eq.7.7-7.8]

$$\text{MACD}_{t|w_S,w_L,\lambda} = \text{EMA}_{t|w_S,\lambda} - \text{EMA}_{t|w_L,\lambda}$$

$$\text{SL}_{t|w_{sig},\lambda} = \text{EMA}^{\{\text{MACD}_t\}}_{t|w_{sig},\lambda}$$

Typical params: $w_L=26, w_S=12, w_{sig}=9$ (Murphy 1999) [p.151]

**RSI** [p.153, eq.7.12-7.13]

$$\text{RS}_{t|w} = \frac{\sum_{i=t-w+1}^{t} \Delta P_i^+}{\sum_{i=t-w+1}^{t} \Delta P_i^-}, \quad \text{RSI}_{t|w} = 100 - \frac{100}{1+\text{RS}_{t|w}}$$

Default: $w=14$, upper level 70, lower level 30 [p.153]

**Bollinger Bands** [p.154, eq.7.15-7.16]

$$\text{BB}^{up}_{t|w,k} = \text{SMA}_{t|w} + k\sigma_{t|w}, \quad \text{BB}^{low}_{t|w,k} = \text{SMA}_{t|w} - k\sigma_{t|w}$$

Default: $w=20, k=2$.

**Momentum / ROC** [p.156-157, eq.7.18, 7.21]

$$\text{MOM}_{t|w} = P_t - P_{t-w}, \quad \text{ROC}_{t|w} = 100(P_t/P_{t-w} - 1)$$

Default $w=12$.

**Bootstrap / Bernoulli trial z-stat** [p.48, ch.3]

$$z = \frac{x - pN}{\sqrt{Np(1-p)}}$$

where $x$ = number of successes (e.g., estimated bounce > artificial), $p=0.5$ (fair), $N$ = trials.

**DTW accumulated cost recursion** [p.195, eq.9.3]

$$\tilde{d}(n,m) = d(n,m) + \min\{\tilde{d}(n-1,m), \tilde{d}(n,m-1), \tilde{d}(n-1,m-1)\}$$

**Forecast-accuracy metrics (MSE, RMSE, NRMSE, NPRMSE, MAE, MAPE, Theil U1, U2)** [p.49-51, ch.3, eq.3.6-3.13] — all standard and defined in the text.

**POCID / IPOCID / POS** (directional accuracy) [p.52, eq.3.14-3.17]

## 4. Algorithms and Pseudocode
**RW() — identify regional locals** [p.32, ch.2, Appendix 1]

```
Input: ys (price vector), w (half-window), pflag
Output: Peaks (m×2), Bottoms (k×2)  # y-coord, x-coord
for t in [w+1 : len(ys)-w]:
    if ys[t] > max(ys[t-w:t-1]) and ys[t] > max(ys[t+1:t+w]):
        append (ys[t], t) to Peaks
    if ys[t] < min(ys[t-w:t-1]) and ys[t] < min(ys[t+1:t+w]):
        append (ys[t], t) to Bottoms
```

**PIPs() — Perceptually Important Points** [p.33-36, ch.2]

```
Input: price series P of length L, number K of PIPs, distance d in {ED, PD, VD}
PIPs = [(1, P[1]), (L, P[L])]
while len(PIPs) < K:
    for each intermediate point i between adjacent PIPs:
        compute d(P[i], adjacent PIPs)
    add point with max distance to PIPs
    sort PIPs by x-coord
return PIPs
```

**HSAR() — identification of horizontal S/R zones** [p.62-63, ch.4]

```
(1) Call RW(ys, w) -> regional locals L = [l1..lk]
(2) Define bins logarithmically: n = ln(L2*/L1*) / ln(1+x)
(3) Round n -> actual bin count n_hat; recompute x_hat = (L2*/L1*)^(1/n_hat) - 1
(4) Bucket locals into bins; bin is HSAR if frequency >= 2
(5) Daily identification: HSARsim uses only past data up to t-1 (500-day warmup)
```

**HS() identification — diagonal check of 7x7 criteria matrix** [p.88-89, Table 5.1]

```
For each 7-tuple (P0, T0, P1, T1, P2, T2, P3) of alternating locals:
    build 7x5 binary matrix M
    M[i,j] = 1 if local i satisfies condition j (among 5 HS conditions)
    confirm pattern if diagonal of 1's exists (all 5 conditions met)
```

**RBottoms() — circle-based saucer detection** [p.131-132, ch.6]

```
Input: ys, w (RW), Bounds %, tWidth, tFit
(1) Find short-term peaks with RW(ys, w)
(2) For each peak P1, scan forward for first P2 >= P1
(3) Require a local trough T1 between them
(4) Scale data 1:2 (depth:width)
(5) Build isosceles triangle ABC (A,C at avg y of P1,P2; B at x-midpoint, y of T1)
(6) Compute radius R1 of circumscribed circle
(7) Draw homocentric circles R2 = (1-Bounds)R1, R3 = (1+Bounds)R1
(8) Count prices within [R2, R3] band; Fit = count / width
(9) Confirm if width >= tWidth and Fit >= tFit
```

**Bootstrap methodology (null model assessment)** [p.48-49, ch.3; p.161, ch.8]

```
(1) Apply rule g() on actual series -> observed statistic theta_hat
(2) Fit null model (GARCH-m or E-GARCH) to actual returns
(3) Verify residuals are IID (else discard model)
(4) Resample residuals with replacement; simulate N series using fitted coefficients
(5) Apply g() to each simulated series -> distribution {theta*_1,...,theta*_N}
(6) Simulated p-value = fraction of theta*_i >= theta_hat
(7) Rule significant at alpha if p-value <= alpha
```

**Subsequence DDTW** [p.196-200, ch.9]

```
Input: query Q (length N), longer Y (length M), threshold tau, rolling window omega
(1) Smooth Y via Savitzky-Golay (ws=21, cubic)
(2) Compute first derivatives: y'_m = [(y_hat_m - y_hat_{m-1}) + (y_hat_{m+1} - y_hat_{m-1})/2] / 2
(3) Standardize to zero-mean, unit-sd
(4) Build cost matrix D[n,m] = |Q[n] - Y[m]|
(5) Relax boundary: D_tilde[1,m] = D[1,m] for all m in [1:M]
(6) Fill D_tilde via recursion (eq.9.3)
(7) Identify local minima of D_tilde[N,:] using RW with window omega
(8) Set B* = {b where D_tilde[N,b] < tau}
(9) Backtrack each b* to starting point a*
```

## 5. Explicit Trading Rules
- **RULE [p.57, ch.4]**: In HSARz, if price hits and returns from the same side → bounce (trend-reversal signal); if it penetrates → failure (trend-continuation signal). Go long on bounce-from-support, short on bounce-from-resistance. TR2 inverts: long after resistance breach.
- **RULE [p.66, ch.4]**: Trade signal with 1-day lag after confirmation (avoids non-synchronous trading); close after fixed holding periods HPs = {1:1:20} days or HPm = {22:2:40} days.
- **RULE [p.106, ch.5 — HS tops closure]**: Short on the neckline penetration; close when (1) price reaches target = neckline − head_height (case 1), OR (2) time exceeds shoulder width (case 2), OR (3) price rises above the neckline for $t_n$ consecutive days or causes loss >= $t_{sl}$ (case 3). The authors use $t_n=2$, $t_{sl}=-0.04$ [p.109-110, Tables 5.4-5.5].
- **RULE [p.95, ch.5 — DT balance]**: Tolerance between the two tops ≤ 4%; minimum pullback ≥ 10% (Bulkowski 2000).
- **RULE [p.134, ch.6 — RB params]**: Bounds=0.3, min width=15, min fit=0.9, w=10.
- **RULE [p.148, ch.7 — SMA]**: Go long when $P_t > \text{SMA}$ & $P_{t-1} < \text{SMA}$; short on the inverse.
- **RULE [p.153, ch.7 — RSI]**: Buy when RSI crosses the lower (30) from below; sell when it crosses the upper (70) from above (Wilder 1978).
- **RULE [p.153, ch.7 — BB]**: Buy if price exits through BB_upper OR crosses BB_lower from below; sell on the inverse (Leung & Chong 2003; Lim et al. 2013).
- **RULE [p.105, ch.5 — choice of w]**: Choose w in RW() for zigzag patterns based on expected mean duration: HS -> w=7, TT/TB -> 15, DT/DB -> 15, Flags -> 3, Pennants -> 2, Wedges -> 7 (via GBM simulation matching the median local-to-local spacing) [Table 5.2, p.104].
- **NEVER [p.65, ch.4]**: Use "estimated" HSARs with future data for backtesting — that is look-ahead bias. Use HSARsim() with a warmup of ~500 days and recompute daily using only data up to t-1.
- **PREFER [p.172, ch.8]**: Short holding periods. TA performs best at HP=1 day; increasing HP degrades performance.
- **RULE [p.164, ch.8]**: Use raw logarithmic returns (not excess returns) for short-term testing — avoids the joint hypothesis problem with CAPM/APT.

## 6. Pitfalls and Anti-patterns
- **[p.93, ch.5] HS can be identified in 21.77% / 22.94% of simulated GBM series** — "if GBM is considered an accurate representation of the price stock generating mechanism then the HS pattern has no predictive power at all" [p.11, ch.1]. Clustering illusion explains the persistence of the belief.
- **[p.190, ch.8] Parameter optimization was deliberately NOT performed in the book** — "parameters' values used in defining each trading rule were the most commonly used in the literature" to avoid data-snooping. Readers should NOT optimize parameters in-sample and report results as if they were out-of-sample.
- **[p.18, §1.5.3] Overfitting via backtesting**: in-sample optimal rules capture both signal and noise; noise does not repeat out-of-sample → performance degrades. A validation set is mandatory.
- **[p.66, ch.4] Look-ahead bias** in classical HSAR: any method using future locals to define a current level is invalid. Use rolling/expanding window with $t-1$ information only.
- **[p.13, p.68, p.190] "Self-destructive" TA**: rules that were publicly effective tend to disappear (Sullivan et al. 1999; Olson 2004; Zapranis & Tsinaslanidis 2012b).
- **[p.168-169, Table 8.5] Low-frequency patterns generate few signals**: although patterns have larger absolute returns than indicators, they produce few signals — pulling average returns toward the unconditional mean. Do not generalize from a single effective pattern.
- **[p.190, ch.8] Transaction costs NOT included** — "transaction costs were not considered in this study, which would exacerbate even further the predictive performance of TA".
- **[p.190, ch.8] Volume confirmation NOT included** — difficult to embed in simulated bootstrap, but TA assumes volume confirms the signal.
- **[p.21, §1.6] Clustering illusion**: humans see patterns in random sequences (De Bondt 1998; Gilovich 1993).
- **[p.22, §1.6] Overconfidence + self-attribution + hindsight bias + confirmation bias + neglect of probability** — all justify traders' irrational perseverance in TA.
- **[p.165, ch.8] Distributional assumptions of ordinary t-tests are violated** in financial series (leptokurtosis, autocorrelation, conditional heteroskedasticity) → use bootstrap with a GARCH null model.
- **[p.158, ch.7 "Whipsaw"]**: in volatile markets with a sensitive MA, long/short signals oscillate at the same level, generating transaction losses. Use filters (time, price-percentage) or MAC.
- **[p.109, ch.5] In zigzag patterns, f3 >= f1 > f2 is the empirical pattern** — i.e., stop-loss (case 3) triggers MORE frequently than the price target (case 1) or neutral expiration (case 2). TA fails more often than it succeeds.
- **[p.188-189, ch.8] The AR(1) null model failed the IID test** on real series — do not use a null model without checking residual independence.
- **[p.201-202, ch.9] DDTW is computationally expensive** — hard to combine with bootstrap, which is already heavy.
- **[p.202, ch.9] Pathological alignment in DTW**: the optimal path can deviate strongly from the diagonal; use a Sakoe-Chiba band or Itakura parallelogram as global constraint.

## 7. Sensitive Parameters
- **Rolling window w in RW()** [p.104-105, Table 5.2]: chosen via GBM simulation with 100 combinations of (mu, sigma), finding w whose median local-to-local spacing matches the average pattern duration reported in the literature. Economic justification: captures the theoretical average duration reported by Bulkowski/Pring/Murphy. **NOT optimized in backtest**.
- **HSAR bin percent x=3% (empirical results), 5% (example)** [p.68, p.63]: logarithmic value keeps percentage distance constant between bins. x=3% and w=50 used in the empirical results.
- **RB thresholds Bounds=0.3, tWidth=15, tFit=0.9** [p.134]: width=15 comes from Pring (2002) "as little as 3 weeks". Bounds and fit are arbitrary but justified as conservative.
- **HS 2.5x symmetry ratio** [p.88]: comes directly from Osler & Chang (1995); not optimized. The authors apply it as-is.
- **DT/DB 4% balance, 10% depth** [p.97]: from Bulkowski (2000). The authors acknowledge "maximum price variations of 3% and 4% for DT and DB respectively" in the original Bulkowski.
- **RSI(14)**: [p.153] Wilder (1978) tradition; the authors simply use it.
- **MACD (12, 26, 9)** [p.151]: "technicians usually set $w_L=26, w_S=12, w_{signal}=9$" (Murphy 1999) — pure convention.
- **BB (20, 2)** [p.154]: "common length of time span used is 20 days". Pure tradition.
- **MOM w=12, ROC w=12** [p.156-157]: "setting w with 12 is a common choice among technicians" (Rosillo et al. 2013).
- **Stop-loss thresholds $t_n=2$, $t_{sl}=-0.04$** [p.109, Table 5.4]: chosen as representative; the authors present figures with sensitivity (Fig 5.16) showing how variation changes relative frequencies and mean returns — this is parameter exploration, not optimization.
- **SMA long-term w=200** [p.163, ch.8, Table 8.2]: "long term" benchmark. Medium w=50, short w=10.
- **Holding period HP**: tested for multiple values; Fig 8.1 shows HP=1 gives best performance [p.171-172].

## 8. Key Literal Quotes
> "Our empirical evidences suggest that overall TA does not generate systematically, statistically significant abnormal returns." — [p.2, ch.1]

> "The HS pattern is successfully identified in random price series and this indicates that it is possible the pattern to be identified in real price series too. The main conclusion is that if the geometric Brownian motion is considered an accurate representation of the price stock generating mechanism then the HS pattern has no predictive power at all." — [p.11, ch.1]

> "...the usual method of graphing stock prices gives a picture of successive levels rather than of changes, and levels can give an artificial appearance of pattern or trend. A second is that chance behavior itself produces patterns that invite spurious interpretations." — Roberts (1959), cited [p.93, ch.5]

> "Support and resistance are not individual price points, but rather thick bands of molasses that slow or even stop price movement." — Bulkowski (2002), cited [p.61-62, ch.4]

> "After taking trading costs into account, none of the thirty-two patterns showed any evidence of profitable forecasting ability in either [bullish or bearish] direction... Moreover, the most bullish results tended to be generated by those patterns which are classified as bearish in the standard textbooks on charting, and vice versa." — Levy (1971, p.318), cited [p.14, Table 1.1]

## 9. Cross-references to Other Books in This Knowledge Base
- **Skepticism about classical TA** [p.2, ch.1]: `algo_trading_chan.md` and `quant_trading_chan.md` (Chan) empirically document strategies with marginal performance — aligned with this book's central conclusion. Both emphasize out-of-sample validation.
- **Regional peaks / pattern recognition via PIPs** [ch.2, p.32-36]: partially overlaps with swing-point detection techniques in `cycle_analytics.md` and `rocket_science.md` (Ehlers). Ehlers uses DSP filters and the Hilbert transform; Tsinaslanidis uses discrete RW + PIPs.
- **Bootstrap methodology with GARCH null model** [ch.8, p.161, p.173-189]: similar methodology discussed in `ml_for_algo_trading.md` (Lopez de Prado) under a different name (Monte Carlo / purged cross-validation).
- **GBM as null model for price series** [ch.5, p.92, eq.5.14]: also in `fin_time_series_tsay.md` (ARIMA/GARCH models) and `time_series_hamilton.md`.
- **Technical indicators (SMA, EMA, MACD, RSI, BB, MOM, ROC)** [ch.7, p.147-159]: standard definitions aligned with `cybernetic_analysis.md` and `quant_trading_chan.md`.
- **Head-and-Shoulders in GBM noise (clustering illusion)** [p.93, ch.5; p.21, §1.6]: reinforces the warning in `systematic_trading.md` (Carver) about cherry-picking and confirmation bias, and aligns with the market-lab project's anti-overfit framework.
- **Overfitting warning via in-sample vs. out-of-sample** [p.18, §1.5.3]: present in `ml_for_algo_trading.md` and `testing_tuning.md`; chapter 1.5.3 here is introductory compared with Lopez de Prado's treatment.
