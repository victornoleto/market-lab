# Cybernetic Analysis for Stocks and Futures: Cutting-Edge DSP Technology to Improve Your Trading

## Metadata
- **Author:** John F. Ehlers [cover, p.i]
- **Year:** 2004 [copyright page, p.iv]
- **Publisher:** John Wiley & Sons, Inc., Hoboken, New Jersey [p.iv]
- **Pages:** 274 (PDF) / body numbered ~246 printed pages [metadata]
- **ISBN:** 0-471-46307-8 [p.iv]
- **Main focus:** Application of Digital Signal Processing (DSP) techniques — Fisher transform, Hilbert transform, IIR/Butterworth filters, Laguerre polynomials — to build trading indicators and systems with near-zero lag and adaptive to the market's dominant cycle.

## 1. Core Thesis
Ehlers argues that conventional technical analysis is crippled by two fallacies: (1) the assumption that prices have a Gaussian PDF, which invalidates any indicator based on standard deviations (Bollinger Bands, CCI, z-scores) [ch.1, p.1-2]; and (2) the use of primitive filters (SMA, EMA) whose lag, proportional to length, destroys any useful signal. The solution is to treat price as a signal composed of a trend component (low frequency) plus a cyclic component (high frequency), decompose it via DSP filters, measure the dominant cycle in real time with the Hilbert transform, and adapt indicator length to the measured cycle [Introduction, p.xi-xiii; ch.2, p.11-19].

The operational thesis: a complementary pair "Instantaneous Trendline + Cyber Cycle" is mathematically dual (sum = unity in the frequency domain) and both have zero low-frequency lag. This allows oscillators to be overlaid on price exactly as moving averages were used before, unifying trend and cycle analysis [ch.2, p.15-19; ch.4, p.36].

## 2. Main Concepts
- **Gaussian PDF fallacy** — prices almost never have a normal distribution; real PDFs (e.g., T-Bond futures 1988-2003) look more like those of a cyclic signal than a bell curve [p.5-6]
- **Fisher Transform** — nonlinear transformation that converts any PDF to approximately Gaussian, enabling "razor-sharp" entry/exit signals [p.3-4]
- **Trend Mode vs Cycle Mode** — mutually exclusive modes defined by frequency content; trend = low lag, cycle = high lag [p.11]
- **Instantaneous Trendline (ITrend)** — second-order low-pass filter with **zero lag** at low frequency, obtained by subtracting the high-pass response from unity [p.16-17]
- **Cyber Cycle** — second-order Gaussian high-pass filter (α=0.07), cyclic component complementary to ITrend [p.15, p.33]
- **Dominant Cycle** — the single tradeable cycle predominant in the data set, measured via the Hilbert transform discriminator [p.108]
- **Hilbert Transform (truncated 4-tap)** — decomposes the analytic signal into InPhase and Quadrature components, allowing phase and cycle period measurement within ~4 samples [p.109]
- **Phasor / DeltaPhase** — rotational vector representation of the cycle; phase difference between successive samples yields the period measure (2π/ΔΦ) [p.108, p.117]
- **Center of Gravity (CG)** — balance point of prices within a FIR window; moves opposite to price swings → zero-lag oscillator [p.47-48]
- **Relative Vigor Index (RVI)** — ratio (Close−Open) / (High−Low), smoothed by a 4-bar symmetric FIR; prices close above the open in up-markets [p.55-57]
- **Stochasticization** — apply the Stochastic function to an indicator to normalize it to the range [0,1]; cancels lag via numerator/denominator ratio [p.67-68]
- **Fisherization** — apply Fisher transform after stochasticizing → sharp binary crossover signals [p.73]
- **Adaptive indicators** — adjust length (via α=2/(Period+1)) to the measured Dominant Cycle; turns a good indicator into an excellent one [ch.10, p.123-124]
- **Sinewave Indicator (noncausal)** — synthesizes the dominant cycle as a pure sine, advances phase by 45° → anticipates turning points by 1/16 of the cycle [p.151-152]
- **Super Smoother / Butterworth digital filter** — 2- or 3-pole filters with configurable cutoff period, nearly flat passband response [ch.13, p.191-192]
- **Regularized filter (Satchwell)** — EMA + curvature penalty term; requires λ = exp(0.16/α) to avoid frequency amplification [p.188]
- **Laguerre filter / transform** — "time-warp": substitutes unit delays by all-pass networks with damping γ; enables strong smoothing with little data [ch.14, p.215-216]
- **Leading indicator (causal)** — adds (price − EMA) to the price → lead = EMA lag; incurs mandatory noise gain [p.231-232]
- **Profit Factor** — ratio Gross Winnings / Gross Losses; together with % winners, sufficient to simulate a Monte Carlo equity curve [p.228]

## 3. Formulas / Equations
**Fisher Transform** [p.3, Eq. 1.2]

$$y = 0.5 \cdot \ln\!\left(\frac{1+x}{1-x}\right)$$

- $x$ = input constrained to $-1 < x < 1$ (otherwise the equation "blows up")
- $y$ = output with approximately Gaussian PDF
- In the implementation the author uses $y = 0.25 \cdot \ln((1+v)/(1-v)) + 0.5 \cdot y[1]$ (smoothing EMA α=0.5) [p.7]

**EMA transfer response (Z-transform)** [p.12, Eq. 2.2]

$$H(z) = \frac{\alpha}{1-(1-\alpha)Z^{-1}}$$

**EMA α ↔ SMA length equivalence** [p.13, Eq. 2.4]

$$\alpha = \frac{2}{\text{Length}+1}$$

**Second-order Gaussian High-Pass Filter (Cyber Cycle base)** [p.15, Eq. 2.7]

$$HPF_t = (1-\tfrac{\alpha}{2})^2 (P_t - 2P_{t-1} + P_{t-2}) + 2(1-\alpha)HPF_{t-1} - (1-\alpha)^2 HPF_{t-2}$$

**Instantaneous Trendline** [p.16, Eq. 2.9]

$$IT_t = (\alpha - \tfrac{\alpha^2}{4})P_t + \tfrac{\alpha^2}{2}P_{t-1} - (\alpha - \tfrac{3\alpha^2}{4})P_{t-2} + 2(1-\alpha)IT_{t-1} - (1-\alpha)^2 IT_{t-2}$$

- Default α=0.07 (≈ 28-bar equivalent) [p.24]
- Initialization: for the first 7 bars, $IT = (P + 2P[1] + P[2])/4$ [p.24]

**Trigger (2-bar leading momentum of ITrend)** [p.24]

$$\text{Trigger}_t = 2 IT_t - IT_{t-2}$$

**4-bar FIR symmetric smoother** [p.33, Eq. 4.1]

$$\text{Smooth}_t = (P_t + 2P_{t-1} + 2P_{t-2} + P_{t-3}) / 6$$

- Constant lag of 1.5 bars at all frequencies.

**Cyber Cycle (applied to Smooth)** [p.34]

$$\text{Cycle}_t = (1-\tfrac{\alpha}{2})^2 (S_t - 2S_{t-1} + S_{t-2}) + 2(1-\alpha)\text{Cycle}_{t-1} - (1-\alpha)^2 \text{Cycle}_{t-2}$$

**Hilbert Transform Quadrature (4-tap truncated)** [p.109, Eq. 9.1]

$$Q_t = (0.0962\, C_t + 0.5769\, C_{t-2} - 0.5769\, C_{t-4} - 0.0962\, C_{t-6}) \cdot (0.5 + 0.08 \cdot InstPeriod_{t-1})$$

$$I_t = C_{t-3}$$

- The factor (0.5 + 0.08·InstPeriod) is an amplitude compensation dependent on the measured period [p.110].

**DeltaPhase (via arctangent subtraction identity)** [p.117, Eq. 9.3]

$$\Delta\Phi_t = \frac{I_t/Q_t - I_{t-1}/Q_{t-1}}{1 + I_t I_{t-1}/(Q_t Q_{t-1})}$$

- Bounds: $0.1 \le \Delta\Phi \le 1.1$ radians (avoids periods <6 bars and >63 bars) [p.117]

**Dominant Cycle period** [p.117-118]

$$DC = \frac{2\pi}{\text{Median}(\Delta\Phi, 5)} + 0.5$$

$$\text{InstPeriod}_t = 0.33 \cdot DC + 0.67 \cdot \text{InstPeriod}_{t-1}$$

$$\text{Period}_t = 0.15 \cdot \text{InstPeriod}_t + 0.85 \cdot \text{Period}_{t-1}$$

**Center of Gravity oscillator** [p.48, Eq. 5.2]

$$CG_t = -\frac{\sum_{i=0}^{N-1} (i+1) \cdot P_{t-i}}{\sum_{i=0}^{N-1} P_{t-i}} + \frac{N+1}{2}$$

- Optimal length = half the Dominant Cycle [p.53]

**Relative Vigor Index** [p.55, Eq. 6.1]

$$RVI = \frac{\text{Close} - \text{Open}}{\text{High} - \text{Low}}$$

- Numerator (Close-Open) and denominator (High-Low) are independently smoothed by a four-bar symmetrical FIR filter before being summed (default Length=8 bars); lag cancels in the ratio [p.56-57]

**Sinewave / LeadSine synthesis** [p.155, ch.11]

$$\text{RealPart} = \sum_{i=0}^{DCPeriod-1} \sin(360° \cdot i / DCPeriod) \cdot \text{Cycle}_{t-i}$$

$$\text{ImagPart} = \sum_{i=0}^{DCPeriod-1} \cos(360° \cdot i / DCPeriod) \cdot \text{Cycle}_{t-i}$$

$$DCPhase = \arctan(\text{RealPart} / \text{ImagPart}) + 90° \;[+180° \text{ if ImagPart}<0]$$

$$\text{Sine} = \sin(DCPhase) \qquad \text{LeadSine} = \sin(DCPhase + 45°)$$

**Three-pole Super Smoother (Butterworth)** [p.191-192, Eq. 13.10]

$$a = e^{-\pi/\text{Cutoff}}, \quad b = 2a\cos(1.738 \cdot 180°/\text{Cutoff}), \quad c = a^2$$

$$\text{Butter}_t = \frac{(1-b+c)(1-c)}{8}(P_t + 3P_{t-1} + 3P_{t-3} + P_{t-4}) + (b+c)\text{Butter}_{t-1} - (c+bc)\text{Butter}_{t-2} + c^2 \text{Butter}_{t-3}$$

**Regularized filter optimal lambda** [p.188, Eq. 13.6]

$$\lambda = \exp(0.16/\alpha)$$

- E.g., α=0.33 → λ=1.624 (nearly flat response up to 0.05 cycles/day) [p.188]

**Iterative SMA** [p.242, Eq. 17.5]

$$SMA_t = \frac{P_t - P_{t-N} + SMA_{t-1}}{N+1}$$

## 4. Algorithms and Pseudocode
**Fisher Transform Indicator** [p.7, Figure 1.7, EasyLanguage]

```
Inputs: Price = (H+L)/2; Len = 10
MaxH = Highest(Price, Len)
MinL = Lowest(Price, Len)
Value1 = 0.5 * 2 * ((Price - MinL)/(MaxH - MinL) - 0.5) + 0.5 * Value1[1]
If Value1 > 0.9999 then Value1 = 0.9999
If Value1 < -0.9999 then Value1 = -0.9999
Fish = 0.25 * Log((1 + Value1)/(1 - Value1)) + 0.5 * Fish[1]
Plot Fish, Fish[1]   # crossover identifies turning points
```

**Cyber Cycle Trading Strategy (contrarian with half-cycle delay)** [p.38, Figure 4.6]

```
Inputs: Price=(H+L)/2, alpha=0.07, Lag=9
Smooth = (P + 2*P[1] + 2*P[2] + P[3]) / 6
Cycle  = (1 - alpha/2)^2 * (Smooth - 2*Smooth[1] + Smooth[2])
       + 2*(1-alpha)*Cycle[1] - (1-alpha)^2 * Cycle[2]
If currentbar < 7 then Cycle = (P - 2*P[1] + P[2]) / 4
alpha2 = 1 / (Lag + 1)
Signal = alpha2 * Cycle + (1 - alpha2) * Signal[1]
If Signal crosses UNDER Signal[1] then Buy next bar on open      # contrarian
If Signal crosses OVER  Signal[1] then Sell Short next bar on open
If Long  and OpenPnL < 0 and BarsSinceEntry > 8 then exit this bar
If Short and OpenPnL < 0 and BarsSinceEntry > 8 then cover this bar
```

**Dominant Cycle measurement via Hilbert discriminator** [p.111, Figure 9.4]

```
Smooth = (P + 2P[1] + 2P[2] + P[3]) / 6
Cycle  = (1-alpha/2)^2 * (Smooth - 2*Smooth[1] + Smooth[2])
       + 2*(1-alpha)*Cycle[1] - (1-alpha)^2 * Cycle[2]
Q1 = (0.0962*Cycle + 0.5769*Cycle[2] - 0.5769*Cycle[4] - 0.0962*Cycle[6])
   * (0.5 + 0.08 * InstPeriod[1])
I1 = Cycle[3]
If Q1 != 0 and Q1[1] != 0:
    DeltaPhase = (I1/Q1 - I1[1]/Q1[1]) / (1 + I1*I1[1]/(Q1*Q1[1]))
DeltaPhase = clip(DeltaPhase, 0.1, 1.1)
MedianDelta = Median(DeltaPhase, 5)
DC = 6.28318 / MedianDelta + 0.5         (fallback 15 if MedianDelta == 0)
InstPeriod = 0.33*DC         + 0.67*InstPeriod[1]
Period     = 0.15*InstPeriod + 0.85*Period[1]
```

**Instantaneous Trendline Trading Strategy (trend-following)** [p.26, Figure 3.6]

```
Inputs: alpha=0.07, RngFrac=0.35, RevPct=1.015
ITrend = (alpha - alpha^2/4)*P + 0.5*alpha^2*P[1]
       - (alpha - 0.75*alpha^2)*P[2]
       + 2*(1-alpha)*ITrend[1] - (1-alpha)^2 * ITrend[2]
Trigger = 2*ITrend - ITrend[2]
If Trigger crosses OVER ITrend:
    Buy next bar at Close - RngFrac*(High-Low) LIMIT
If Trigger crosses UNDER ITrend:
    SellShort next bar at Close + RngFrac*(High-Low) LIMIT
If Long  and Close < EntryPrice/RevPct : reverse to Short on open
If Short and Close > EntryPrice*RevPct : reverse to Long  on open
# $2,500 money-management stop added externally [p.26]
```

**Sinewave Indicator** [p.154, Figure 11.2]

```
# ... compute DC period as above ...
DCPeriod = IntPortion(0.15*InstPeriod + 0.85*Period[1])
RealPart = 0; ImagPart = 0
for i in 0 .. DCPeriod-1:
    RealPart += Sin(360*i/DCPeriod) * Cycle[i]
    ImagPart += Cos(360*i/DCPeriod) * Cycle[i]
if |ImagPart| > 0.001: DCPhase = ArcTan(RealPart/ImagPart)
else:                  DCPhase = 90 * Sign(RealPart)
DCPhase += 90
if ImagPart < 0: DCPhase += 180
if DCPhase > 315: DCPhase -= 360
Plot Sin(DCPhase), Sin(DCPhase + 45)   # LeadSine leads Sine by 1/16 cycle
```

**Laguerre Filter (4-element, γ=0.8)** [p.216, Figure 14.5]

```
L0 = (1-gamma)*Price + gamma*L0[1]
L1 = -gamma*L0 + L0[1] + gamma*L1[1]
L2 = -gamma*L1 + L1[1] + gamma*L2[1]
L3 = -gamma*L2 + L2[1] + gamma*L3[1]
Filt = (L0 + 2*L1 + 2*L2 + L3) / 6
```

**Monte Carlo equity-growth simulator (Excel)** [p.228-229]

```
Inputs: percent_winners (cell A2, default 45), profit_factor (cell B2, default 1.5)
for row in 3 .. 500:
    r = RAND()                               # uniform [0,1]
    trade_pnl = profit_factor if r < percent_winners/100 else -1
    equity[row] = equity[row-1] + trade_pnl
plot equity (line chart)
# Press F9 to re-randomize; repeat until distribution of outcomes is visualised
```

## 5. Explicit Trading Rules
- **RULE [p.4-5]** (Fisher Transform usage): after normalizing prices to the range [-1,+1] over a 10-bar window and applying the Fisher transform, crossovers between Fish and Fish[1] identify cyclic turning points with essentially zero lag.
- **RULE [p.23-24]** (ITrend trend strategy): Long when Trigger crosses above ITrend; Short when it crosses below. Entry **always via limit order** at Close ± 35% of the bar's range (RngFrac=0.35).
- **RULE [p.25]** (ITrend reversal protection): If the position is losing more than 1.5% (RevPct=1.015), reverse to the opposite side at the next bar's open — "major losses are avoided by recognizing when a trade is on the wrong side."
- **RULE [p.26]** ($2,500 money-management stop): for currency futures, an additional $2,500 stop independent of the technical rule.
- **NEVER [p.24]**: use stop orders or market orders as primary entry — limit orders capture slippage as profit rather than as cost.
- **RULE [p.35-36]** (Cyber Cycle strategy, contrarian): because total lag (1.5 smooth + ~0.5 cycle + 1 trigger + 1 execution = 4 bars) makes the signal "exactly wrong" on an 8-bar cycle, **use the inverted signal** with an additional-lag EMA. Cross-under ⇒ Buy; cross-over ⇒ Sell Short.
- **RULE [p.38]** (Cyber Cycle escape): if the trade still has an open loss after 8 bars, exit immediately (reverse).
- **RULE [p.57]** (RVI): indicator is cycle-mode only; buy when RVI crosses above Trigger (RVI[1]), sell when it crosses below.
- **RULE [p.152-153]** (Sinewave): LeadSine-crosses-above-Sine = entry ~1/16 cycle before top/bottom; **do NOT trade** when the lines do not have a clear sinusoidal shape (signals Trend Mode — natural whipsaw filter).
- **RULE [p.221-223]** (Laguerre RSI): buy when RSI crosses above 20%, sell when it crosses below 80%.
- **RULE [p.123-124]** (Adaptive indicators): whenever possible, replace fixed length with the measured Dominant Cycle, via $\alpha_1 = 2/(\text{Period}+1)$.
- **NEVER [p.1-2]**: attribute statistical meaning to ±1σ / ±2σ bands over price data assuming a Normal PDF — the assumption is demonstrably false on Treasury Bond futures over 15 years (1988-2003).
- **NEVER [p.189, p.210]**: use filters of order higher than 2 (without strong justification) for Gaussian, or higher than 3 for Butterworth — ringing and lag grow more than the attenuation benefit.

## 6. Pitfalls and Anti-patterns
- [p.1-2] **Gaussian PDF assumption**: CCI, Bollinger Bands, and any indicator with a "sigma boundary" are built on a false premise. The real price PDF looks more like a sinewave than a bell curve.
- [p.188] **Regularized filter with arbitrary λ**: λ=10 with α=0.33 amplifies 33-bar cycles by +6 dB (the exact opposite of the desired smoothing). Always use $\lambda = e^{0.16/\alpha}$.
- [p.15, p.19] **Higher-order Gaussian filters have transient "bell-ringing"**: "the ringing is more a function of the bell itself rather than a filtered response of a driving force" — avoid order > 2.
- [p.36] **Trading cycles directly produces systematically delayed signals**: cumulative lag of smooth + cycle + trigger + execution = ~4 bars, which for an 8-bar cycle completely inverts the signal.
- [p.51, p.53] **Wrong CG length destroys the indicator**: if window = full dominant cycle, the CG sits static in the middle (half the data pulls right, half pulls left). Always use ~ ½ of the Dominant Cycle.
- [p.152] **Sinewave in Trend Mode**: during a trend, phase does not advance and the lines do not cross — **this is a feature, not a bug**. Forcing sinewave signals in a trend generates fabricated whipsaws.
- [p.227-229] **A single equity curve is misleading**: the same combination {% winners=45, PF=1.5} produces dramatically different curves on each Monte Carlo run. A vendor showing one curve without Profit Factor and % winners is hiding information.
- [p.232-233] **Leading indicators carry mandatory noise gain**: there is no causal filter that anticipates transients without amplifying noise — "you cannot get something for nothing; there is no magic predictor" [p.234].
- [p.26, p.32] **False robustness from many parameters**: Ehlers defends his Instantaneous Trend Strategy by saying it is "highly unlikely that the strategy has been curve fitted" because it has **few independent parameters** and a large number of trades over 25 years — the contrapositive being the pitfall.
- [p.220] **RSI = 14 is arbitrary**: "When Welles Wilder first introduced the RSI, I was curious as to why he selected 14 bars" — motivation for adaptive indicators over traditional constants.
- [p.117-118] **DeltaPhase can go to zero or negative** due to noise / quadrant ambiguity → requires clipping to [0.1, 1.1] rad + a 5-sample median filter before use.
- [p.119] **FFT is unsuitable for markets**: cannot simultaneously satisfy stationarity constraints and produce sufficient resolution; requires 16 full cycles for measurement resolution comparable to the Hilbert discriminator.

## 7. Sensitive Parameters
- **α = 0.07 (Cyber Cycle / ITrend default)** [p.24, p.34]: equivalent to ~28-bar SMA via α=2/(L+1). Ehlers uses this value in **every** indicator in the book; it is not optimized per market — it is a design choice that isolates the ~40+ bar band as trend and <40 bars as cycle. Low curve-fit risk.
- **RngFrac = 0.35 (limit order offset)** [p.24, p.26]: "optimizable parameter"; author states it is the only parameter tuned via backtest, the rest being fixed by design.
- **RevPct = 1.015 (reversal threshold)** [p.25]: "relatively robust number"; 1.5% by design (not optimized).
- **BarsSinceEntry > 8 (Cyber Cycle escape)** [p.38]: chosen as a "typical half cycle" to allow natural reversal; derived from the 16-bar dominant cycle assumption.
- **Hilbert truncation = 4 taps** [p.109]: truncates the infinite series; the amplitude feedback correction $(0.5 + 0.08 \cdot InstPeriod_{t-1})$ is empirical but explicitly justified as superior to the trigonometric identity $\sin^2+\cos^2=1$ in the presence of noise [p.117].
- **Smoothing EMA on measurement** [p.118]: α=0.33 (InstPeriod) and α=0.15 (Period) — derived from the requirement "full cycle measurement in one cycle of 20-bar signal starting from 0".
- **DeltaPhase clips [0.1, 1.1] rad** [p.117]: mathematical justification — corresponds to cycles between 6 and 63 bars (2π/0.1 and 2π/1.1). Not a curve-fit; it is a physical bound.
- **γ (Laguerre damping) ∈ [0.6, 0.8]** [p.215]: low parsimony — the author shows curves for both and leaves the choice to the reader. Default in code = 0.8 [p.216].
- **Cutoff period (Super Smoother)** [p.191-192]: Table 13.2 lists coefficients for cutoffs of 10, 15, 20, 25, 30 bars; should be selected by timeframe, not optimized in backtest.
- **Fisher normalization window = 10 bars** [p.7]: arbitrary; EasyLanguage `Len` input.
- **RVI summation length = 8 bars** [p.57]: "nominal value ... approximately half the period of most cycles of interest" — economic, not statistical, justification.

## 8. Key Literal Quotes
> "Prices almost never have a Gaussian, or Normal, probability distribution. Statistical measures based on Gaussian probability distributions, such as standard deviations, are in error because the probability distribution assumption underlying the calculation is in error." — [p.10]

> "The Instantaneous Trendline has zero lag. That's right—zero lag!" — [p.17]

> "All indicators have lag ... No indicator can precede an event from which it is derived." — [p.36, p.46]

> "Curve fitting is a weakness of many technical analysis trading strategies." — [p.26, p.32]

> "That's the law of physics—you cannot get something for nothing. Causal filters can have a predictive capability over some portion of the frequency response, but not at all frequencies. There is no magic predictor." — [p.234]

> "Profit Factor and Percentage Winners of a trading system are all you need to create a Monte Carlo equity curve of that system. A real equity curve is only one of the possibilities that can be produced by a Monte Carlo equity curve." — [p.230]

## 9. Cross-references to Other Books in This Knowledge Base
- **Parameter parsimony** — Ehlers argues "few independent parameters + many trades over long span ⇒ not curve-fit" [p.26], aligned with Carver's principle in `systematic_trading.md#design-principles` of avoiding overfitting via robust defaults and handcrafted weights. Both reach the same conclusion by different routes (engineering vs. Bayesian prior).
- **Monte Carlo for system evaluation** [p.227-230] — simulation via {% winners, profit factor} complements, but is much simpler than, the CPCV/walk-forward framework in `advances_fin_ml.md`. Ehlers provides a minimal parameterized simulator; López de Prado provides the theory of robust backtesting.
- **Critique of the Gaussian PDF** [ch.1, p.1-10] — connects to the empirical discussion of fat-tailed distributions in `evidence_based_ta.md`; Ehlers proposes the Fisher transform as a *workaround* to reuse Normal-based tools.
- **Cycle-based filters vs. ML features** — the zero-lag oscillators (Cyber Cycle, CG, RVI, adaptive versions) are direct candidates for numerical features in models from `ml_for_asset_managers.md` and `advances_fin_ml.md`; particularly the Dominant Cycle period as a macro-regime feature.
- **Time series theory** — Ehlers's Z-transform analysis [ch.2, p.12-16] and lag/response derivations are rigorously the apparatus of `time_series_hamilton.md` ch. 3 (linear filters, ARMA as transfer-function filters). Ehlers applies DSP where Hamilton applies econometrics; the same mathematical formalism.
