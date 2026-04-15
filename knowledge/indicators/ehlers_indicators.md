# Ehlers Indicators (DSP)

MAMA, Cyber Cycle, Fisher Transform, Hilbert Transform — all grounded in DSP.

## Sources

- [`books/rocket_science.md`](../books/rocket_science.md)
- [`books/cybernetic_analysis.md`](../books/cybernetic_analysis.md)
- [`books/cycle_analytics.md`](../books/cycle_analytics.md)

## From `books/rocket_science.md`

### Explicit Trading Rules

- **RULE [p.114]**: Assume Trend Mode by default; Cycle Mode requires specific criteria (two conditions only).
- **RULE [p.114]**: Cycle Mode is active for a half-dominant-cycle after the Sinewave/LeadSine lines cross.
- **RULE [p.114]**: Cycle Mode if the phase rate of change is between 0.67× and 1.5× the dominant rate (360/Period).
- **RULE [p.114]**: Override → Trend Mode when |SmoothPrice − Trendline|/Trendline ≥ 1.5% (price "widely separated").
- **RULE [p.122]**: In Trend Mode, buy when SmoothPrice crosses above Trendline; sell when it crosses below.
- **RULE [p.123]**: In Cycle Mode, buy when LeadSine crosses above Sine; sell when it crosses below.
- **RULE [p.108]**: A trend is "in force" if SmoothPrice has not crossed the Instantaneous Trendline in the last half-dominant-cycle.
- **RULE [p.108]**: Trend is declared early if SmoothPrice has not crossed in the last quarter-cycle and does not appear to return.
- **RULE [p.108]**: Trend has ended when SmoothPrice crosses the Instantaneous Trendline again.
- **RULE [p.93]**: Avoid Cycle Mode trading when SNR < 6 dB — below this the signal is less than 2× noise and profit becomes a crapshoot.
- **RULE [p.82-83]**: Clamp Period to [6, 50] bars; also limit the bar-to-bar rate of change to [0.67×, 1.5×] to stabilize the measurement.
- **RULE [p.125]**: On T-Bonds (1984-2000), CycPart=1.15 and a $1,100 money-management stop optimize SineTrend (profit $113k, 44.5% win, DD $8,137).
- **RULE [p.128]**: On Swiss Franc (1975-2000), CycPart=1.10 and a $2,200 stop — avg_win/avg_loss ratio = 1.56:1.
- **NEVER [p.3-4]**: Trade cycle periods < 2 bars (Nyquist) or in practice < 5-8 bars — aliasing makes it unworkable.
- **NEVER [p.4]**: Operate on non-smoothed data — high-frequency aliasing contaminates all downstream analysis.
- **NEVER [Preface p.ix]**: Use FFT to measure market spectra — ch.19 is dedicated to explaining why FFT is unsuitable for trading.

### Formulas / Equations

**SMA lag** [p.18-19, ch.3]

$$\text{Lag}_{SMA} = \frac{n - 1}{2}$$

**SMA frequency response** [p.24]

$$\text{SMA}(P) = \frac{\sin(\pi W / P)}{\pi W / P}$$

- $W$ = window width; $P$ = cycle period; nulls when $W/P$ is integer

**WMA lag (center of gravity of triangle)** [p.27]

$$\text{Lag}_{WMA} = \frac{n - 1}{3}$$

**EMA alpha → lag** [p.29]

$$\alpha = \frac{1}{L + 1}, \quad \alpha = \frac{2}{n + 1} \text{ (equivalent to n-bar SMA)}$$

**EMA cutoff period** [p.30, proved in ch.13]

$$P = \frac{-2\pi}{\ln(1 - \alpha)} \approx \frac{4\pi}{\alpha(2 + \alpha)}$$

**Momentum derivative identity (cycle lead of 90°)** [p.36]

$$\frac{d}{dt}\sin(\omega t) = \omega \cos(\omega t)$$

**3-bar detrend filter (odd-order, rejects 2-bar cycle)** [p.37]


$$MO = 0.5 \cdot P - 0.5 \cdot P[2]$$

**5-bar symmetric high-pass filter (detrender)** [p.38]

$$MO = 0.0909 P + 0.4545 P[1] - 0.4545 P[3] - 0.0909 P[4]$$

**Phase lag of symmetric high-pass filter** [p.39]

$$\phi_{lag} = \frac{360 \cdot 3}{\text{Period}} - 90^{\circ}$$

— zero-lag cycle period = 12 bars.

**Improved Hilbert Transformer (4-tap truncated, trial/error tuned)** [p.57]

$$Q = 0.0962 P + 0.5769 P[2] - 0.5769 P[4] - 0.0962 P[6]$$

Lag = 3 bars.

**Amplitude correction for truncated Hilbert Transformer** [p.58]

$$A_{corr} = 0.075 \cdot \text{Period}[1] + 0.54$$

**Euler's identity (basis of DSP complex frequency)** [p.46, ch.5]

$$e^{j\theta} = \cos\theta + j\sin\theta$$

**Phase lag of Inphase/Quadrature after Hilbert Transform** [p.60]

$$\phi_{lag} = \frac{360 \cdot 7}{\text{Period}} - 90^{\circ}$$

— zero-lag @ 28-bar dominant cycle.

**SNR in decibels** [p.82]

$$\text{SNR} = 10 \log_{10}\left(\frac{I_1^2 + Q_1^2}{\text{Range}^2}\right) + 6 \text{ dB}$$

— +6 dB bias compensates for the definition of "0 dB SNR = signal amp = half the daily range".

**Enhanced SNR amplitude correction terms** (derived from chirp 10-40 bar) [p.88-89]

$$Q_3 = 0.5(\text{Smooth} - \text{Smooth}[2]) \cdot (0.1759 \cdot \text{SmoothPeriod} + 0.4607)$$

$$I_3 = \frac{\pi}{2} \cdot \frac{1}{N/2}\sum_{k=0}^{N/2-1} Q_3[k]$$

(the 1.57 ≈ π/2 compensates the half-cycle moving average amplitude)

**Ehlers filter (general form)** [p.188]

$$y = \frac{\sum_{i=1}^{n} c_i \cdot x_i}{\sum_{i=1}^{n} c_i}$$

where $c_i$ is a statistic (absolute momentum, squared distance, SNR, volume, etc.) ordered over the window.

**Distance-coefficient Ehlers filter** [p.193]

$$c_i = \sum_{k=1}^{n-1} (P_i - P_{i+k})^2$$

(coefficient = squared "distance" across the window → nonlinear edge-detecting response)

### Algorithms and Pseudocode

**Hilbert Transform + Homodyne Discriminator (cycle period)** [ch.6, p.59; ch.8 p.82-83, EasyLanguage]

```
{Smoothing}
Smooth = (4*Price + 3*Price[1] + 2*Price[2] + Price[3]) / 10
{Detrend via amplitude-corrected Hilbert Transformer}
Detrender = (0.0962*Smooth + 0.5769*Smooth[2] - 0.5769*Smooth[4] - 0.0962*Smooth[6])
            * (0.075*Period[1] + 0.54)
{Inphase / Quadrature}
Q1 = (0.0962*Detrender + 0.5769*Detrender[2] - 0.5769*Detrender[4]
      - 0.0962*Detrender[6]) * (0.075*Period[1] + 0.54)
I1 = Detrender[3]
{Advance phase by 90°}
jI = HilbertOf(I1) * amplitude_correction
jQ = HilbertOf(Q1) * amplitude_correction
{Phasor addition for 3-bar averaging}
I2 = I1 - jQ
Q2 = Q1 + jI
{EMA smoothing before discriminator}
I2 = 0.2*I2 + 0.8*I2[1]
Q2 = 0.2*Q2 + 0.8*Q2[1]
{Homodyne Discriminator}
Re = I2*I2[1] + Q2*Q2[1]
Im = I2*Q2[1] - Q2*I2[1]
Re = 0.2*Re + 0.8*Re[1]
Im = 0.2*Im + 0.8*Im[1]
If Im<>0 and Re<>0 then Period = 360 / ArcTangent(Im/Re)
{Clamp rates of change}
If Period > 1.5*Period[1] then Period = 1.5*Period[1]
If Period < 0.67*Period[1] then Period = 0.67*Period[1]
{Clamp absolute range}
If Period < 6 then Period = 6
If Period > 50 then Period = 50
Period = 0.2*Period + 0.8*Period[1]
SmoothPeriod = 0.33*Period + 0.67*SmoothPeriod[1]
```

**Dominant Cycle Phase via heterodyne** [ch.9, p.97-99]

```
DCPeriod = IntPortion(SmoothPeriod + 0.5)
RealPart = 0
ImagPart = 0
For count = 0 to DCPeriod - 1:
    RealPart += Cos(360*count/DCPeriod) * SmoothPrice[count]
    ImagPart += Sin(360*count/DCPeriod) * SmoothPrice[count]
DCPhase = Arctangent(ImagPart/RealPart) + 90
{Compensate 1-bar WMA smoothing lag}
DCPhase += 360 / SmoothPeriod
If ImagPart < 0 then DCPhase += 180
If DCPhase > 315 then DCPhase -= 360   {wraparound at 315}
```

**Sinewave Indicator** [ch.9, p.101-103]

```
Sine     = Sin(DCPhase)
LeadSine = Sin(DCPhase + 45)
{Buy when LeadSine crosses over Sine; Sell when crosses under}
```

**Instantaneous Trendline** [ch.10, p.109]

```
ITrend = 0
For count = 0 to DCPeriod - 1:
    ITrend += Price[count]
ITrend = ITrend / DCPeriod
{Smooth with 4-bar WMA}
Trendline = (4*ITrend + 3*ITrend[1] + 2*ITrend[2] + ITrend[3]) / 10
SmoothPrice = (4*Price + 3*Price[1] + 2*Price[2] + Price[3]) / 10
```

**Market Mode Identification** [ch.11, p.114-117]

```
Trend = 1   {assume Trend Mode}
{Reset days in trend on Sinewave crossing}
If Sin(DCPhase) crosses Sin(DCPhase+45) then:
    DaysInTrend = 0
    Trend = 0
DaysInTrend += 1
{Cycle Mode for half dominant cycle after crossing}
If DaysInTrend < 0.5*SmoothPeriod then Trend = 0
{Cycle Mode if phase rate of change is within ±50% of dominant}
If (DCPhase - DCPhase[1]) > 0.67*360/SmoothPeriod AND
   (DCPhase - DCPhase[1]) < 1.5*360/SmoothPeriod then Trend = 0
{Override: Trend Mode if prices far from Trendline}
If |SmoothPrice - Trendline| / Trendline >= 0.015 then Trend = 1
```

**SineTrend Automatic Trading System** [ch.12, p.122-123]

```
If Trend = 1 (Trend Mode):
    {Entry on transition from cycle to trend}
    If Trend[1] = 0:
        If MarketPosition = -1 AND Smooth >= Trendline then buy
        If MarketPosition = +1 AND SmoothPrice < Trendline then sell
    {Regular trend signals}
    If SmoothPrice crosses over Trendline then buy
    If SmoothPrice crosses under Trendline then sell
If Trend = 0 (Cycle Mode):
    If LeadSine crosses over Sine then buy
    If LeadSine crosses under Sine then sell
```

**Ehlers Filter (distance coefficients)** [ch.18, p.193]

```
For count = 0 to Length - 1:
    Distance2[count] = 0
    For LookBack = 1 to Length - 1:
        Distance2[count] += (Price[count] - Price[count+LookBack])^2
    Coef[count] = Distance2[count]
Num = 0; SumCoef = 0
For count = 0 to Length - 1:
    Num += Coef[count] * Price[count]
    SumCoef += Coef[count]
Filt = Num / SumCoef
```

### Pitfalls and Anti-patterns

- [p.17] Moving averages induce lag that is "almost always a bad characteristic"; smoothing is always a trade-off against lag.
- [p.20] Too-wide SMA window: "sluggish" — useful only for the longest trends. Too-narrow window: whipsaws from inadequate smoothing.
- [p.28-29] Common EMA programming error: assigning α=0.2 and (1-α)=0.9 (does not sum to 1) → recursion diverges / blows up. Always use α as a global variable and write the EMA as a function of α.
- [p.33] Momentum NEVER leads the event on real price action — the 90° anticipation is an illusion that ONLY exists if price is a pure sine wave (Cycle Mode).
- [p.33] Momentum is always noisier/more discontinuous than the original function (successive derivatives increase disjointedness).
- [p.35] Momentum-based anticipation depends on FIRST identifying the market mode — in Trend Mode, assigning predictive capability to momentum is an error.
- [p.37-39] "More of a good thing" does not work: increasing the high-pass filter length beyond ~5 bars adds lag that destroys any phase lead.
- [p.58] An ideal Hilbert Transformer requires coefficients from −∞ to +∞; in practice it must be severely truncated. Non-truncated Hilbert lag at a 40-bar cycle = 21 bars, unworkable.
- [p.82] Primary SNR has 10-bar lag; Alternate SNR adds 7.5 bars of lag (total 17.5) — "unthinkable for practical trading". Use Enhanced SNR (4-bar lag).
- [Preface p.ix] FFT is an unsuitable tool for trading because it ignores mathematical constraints (short data window, non-stationarity).
- [p.95] Phase computed directly from the Hilbert Transform is unusable: 7-bar lag is a "substantial portion of most tradable cycles" and the measurement is noisy.
- [p.125] Caveat: the change to CycPart + money-management stop is presented as "not curve fitting" because tested over 16 years — but it is clearly a post-hoc optimization of 2 parameters. The trade-to-parameter ratio is cited as justification.
- [p.124] Trend-Mode-only performance (no Cycle) is "simply awful" (negative avg trade) — the system relies heavily on Cycle trades → risk if regime changes.
- [p.185] Linear filters (SMA/EMA) are OPTIMAL only for slowly-varying stationary signals + high-freq noise — market data is neither; requires nonlinear.
- [p.194-195] Increasing coefficient nonlinearity (cube, Gaussian) degenerates the Ehlers filter into something indistinguishable from a median filter (loses gray-area resolution).
- [p.117] Trying to automate mode decision "often leads to great deal of chatter and rapid back-and-forth switching" — which is why Trend is the default.

---

## From `books/cybernetic_analysis.md`

### Explicit Trading Rules

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

### Formulas / Equations

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

### Algorithms and Pseudocode

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

### Pitfalls and Anti-patterns

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

---

## From `books/cycle_analytics.md`

### Explicit Trading Rules

- **RULE [p.36, ch.3]**: Apply a SuperSmoother filter with a cutoff period of 10 bars universally to all price data before any indicator computation. The SuperSmoother attenuates aliasing noise at 12 dB per octave; aliasing noise grows at 6 dB per octave, so the net effect is effective noise gating.

- **RULE [p.88-89, ch.7]**: Precede every technical indicator with a roofing filter (two-pole HP + SuperSmoother). Without this, conventional indicators produce erroneous signals during trending markets due to Spectral Dilation. The text example uses 48-bar HP and 10-bar SuperSmoother; Code Listing 7-3 implements the generalized indicator with defaults HPPeriod=80 and LPPeriod=40 [p.81-82, ch.7].

- **RULE [p.137, ch.11]**: Set the Adaptive RSI lookback to half the measured dominant cycle. At this setting, the RSI reaches 0 or 1 only when prices complete a genuine cyclic swing.

- **RULE [p.142, ch.11]**: Set the Adaptive Stochastic lookback to the *full* measured dominant cycle period to guarantee that both highest and lowest closes are included in the range.

- **RULE [p.152-153, ch.11]**: Tune the Adaptive Band-Pass Filter to 90% of the dominant cycle period to obtain approximately 60 degrees of phase lead. Buy/sell signals trigger when indicator and trigger lines cross outside the ±0.7 reference lines.

- **RULE [p.220-221, ch.17]**: For oscillator-based swing trading, anticipate rather than confirm turning points. Generate long entry when oscillator crosses *below* the lower threshold (e.g., 20%), short entry when crosses *above* the upper threshold (e.g., 80%). Recovers approximately 4 bars of lag vs. the confirmation rule.

- **RULE [p.222-223, ch.17]**: For band-pass swing trading, use the cosine-wave leading signal. Buy when Cosine crosses over its 1-bar delayed version; sell when crosses under. Produces a quarter-cycle phase lead.

- **RULE [p.224-225, ch.17]**: Safety valve exit: if long and price closes below a SuperSmoother-smoothed lower channel, exit immediately. If trade is not profitable within half the expected trade duration, exit. "If you even think about hoping a trade will turn around, exit the trade immediately."

- **RULE [p.225-226, ch.17]**: Stop-loss: use only as a guard against extreme losses. A simple percentage of entry price (2–5% for stocks) is sufficient. Do not build stop-loss logic into the core strategy signal.

- **NEVER [p.218, ch.17]**: Do not optimize strategy parameters without requiring at least 30 trades per parameter. Apply sensitivity analysis: if the performance surface does not form a gentle hill across a range of parameter values, the strategy is not robust.

### Formulas / Equations

**Unified two-pole filter coefficient (eq. 1-15)** [p.11-12, ch.1]

$$\alpha = \frac{\cos(K \cdot 360°/\text{Period}) + \sin(K \cdot 360°/\text{Period}) - 1}{\cos(K \cdot 360°/\text{Period})}$$

- $K = 1.0$ for single-pole filters
- $K = 0.707$ for two-pole high-pass filters
- $K = 1.414$ for two-pole low-pass (Butterworth) filters

**General two-pole IIR form (eq. 1-14)** [p.11, ch.1]

$$\text{Output} = b_0 \cdot \text{Input} + b_1 \cdot \text{Input}[1] + b_2 \cdot \text{Input}[2] - a_1 \cdot \text{Output}[1] - a_2 \cdot \text{Output}[2]$$

**EMA lag formula (alpha calculation)** [p.19, ch.2]

$$\text{Lag} = \frac{1}{\alpha} - 1 \quad \text{where } \alpha = \frac{2}{N+1}$$

**Band-Pass Filter output (eq. 5-2)** [p.48, ch.5]

$$\text{BP} = 0.5(1-\sigma)(\text{Input} - \text{Input}[2]) + \lambda(1+\sigma)\cdot\text{BP}[1] - \sigma\cdot\text{BP}[2]$$

- $\lambda = \cos(360°/\text{Period})$
- $\sigma$, $\gamma$ are bandwidth parameters from eq. 5-1

**AGC decay factor derivation** [p.54-55, ch.5]

$$K = 0.991 \implies \text{decays approx. 1.5 dB across 10–48 bar trading band}$$

**Hurst Coefficient** [p.65-67, ch.6]

$$H = 2 - D \quad \text{where } D = \text{fractal dimension}$$

- $H > 0.5$: trend (persistence); $H = 0.5$: random walk; $H < 0.5$: cycle (antipersistence)

**Fisher Transform** [p.196-197, ch.15]

$$\text{Output} = 0.5 \cdot \ln\!\left(\frac{1 + \text{Input}}{1 - \text{Input}}\right)$$

**Inverse Fisher Transform** [p.198-200, ch.15]

$$\text{Output} = \frac{e^{2K \cdot \text{Input}} - 1}{e^{2K \cdot \text{Input}} + 1}$$

**Dominant Cycle (center-of-gravity)** [p.103-104, ch.8]

$$\text{DC} = \frac{\sum_{P=10}^{48} P \cdot \text{Pwr}(P)}{\sum_{P=10}^{48} \text{Pwr}(P)} \quad \text{for } \text{Pwr}(P) \geq 0.5$$

**Cosine-wave leading signal** [p.222-223, ch.17]

$$\text{Cosine} = \frac{\text{Period}}{2\pi} \cdot (\text{BP} - \text{BP}[1])$$

Produces a quarter-cycle phase lead relative to the band-pass filter.

### Algorithms and Pseudocode

**SuperSmoother Filter (eq. 3-3)** [p.33, ch.3]

```easylanguage
a = exp(-1.414 * 3.14159 / Period)
b = 2 * a * Cos(1.414 * 180 / Period)
c2 = b
c3 = -a * a
c1 = 1 - c2 - c3
Output = c1 * (Input + Input[1]) / 2 + c2 * Output[1] + c3 * Output[2]
```

Note: Eq. 3-1 (p.32) is the two-pole modified Butterworth filter (denominator only, no two-element MA numerator). Ch.3 contains no Code Listings — only numbered equations (3-1, 3-2, 3-3).

**Roofing Filter Indicator — Two-Pole HP + SuperSmoother (Code Listing 7-3)** [p.81-82, ch.7]

```easylanguage
// Inputs: HPPeriod(80), LPPeriod(40)  ← defaults in code
// (Text example in Ch.7 uses 48-bar HP and 10-bar SuperSmoother to explain
//  the concept; Code Listing 7-3 uses the generalized inputs below.)
alpha1 = (Cosine(.707*360 / HPPeriod) + Sine(.707*360 / HPPeriod) - 1) /
          Cosine(.707*360 / HPPeriod)
HP = (1 - alpha1/2)*(1 - alpha1/2)*(Close - 2*Close[1] + Close[2])
     + 2*(1 - alpha1)*HP[1] - (1 - alpha1)*(1 - alpha1)*HP[2]
// Smooth with SuperSmoother at LPPeriod
a1 = expvalue(-1.414*3.14159 / LPPeriod)
b1 = 2*a1*Cosine(1.414*180 / LPPeriod)
c2 = b1; c3 = -a1*a1; c1 = 1 - c2 - c3
Filt = c1*(HP + HP[1]) / 2 + c2*Filt[1] + c3*Filt[2]
```

Note: Code Listing 7-1 [p.78, ch.7] is a simpler single-pole HP version (no `.707` factor) hardcoded to 48-bar HP and 10-bar SuperSmoother, used only as the initial explanatory example. Code Listing 7-3 implements the two-pole HP with generalized inputs (defaults HPPeriod=80, LPPeriod=40), which is the preferred formulation.

**Decycler (Code Listing 4-1)** [p.40-42, ch.4]

```easylanguage
// Inputs: Cutoff(60)
// Single-pole HP — no .707 factor
alpha1 = (Cosine(360 / Cutoff) + Sine(360 / Cutoff) - 1) / Cosine(360 / Cutoff)
Decycle = (alpha1 / 2)*(Close + Close[1]) + (1 - alpha1)*Decycle[1]
```

**Decycler Oscillator (Code Listing 4-2)** [p.43-45, ch.4]

```easylanguage
// Inputs: HPPeriod1(30), HPPeriod2(60)
// Both HP filters use .707 factor → two-pole HP (K=0.707 per unified filter theory)
alpha1 = (Cosine(.707*360 / HPPeriod1) + Sine(.707*360 / HPPeriod1) - 1) /
          Cosine(.707*360 / HPPeriod1)
alpha2 = (Cosine(.707*360 / HPPeriod2) + Sine(.707*360 / HPPeriod2) - 1) /
          Cosine(.707*360 / HPPeriod2)
HP1 = (1 - alpha1/2)*(1 - alpha1/2)*(Close - 2*Close[1] + Close[2])
      + 2*(1 - alpha1)*HP1[1] - (1 - alpha1)*(1 - alpha1)*HP1[2]
HP2 = (1 - alpha2/2)*(1 - alpha2/2)*(Close - 2*Close[1] + Close[2])
      + 2*(1 - alpha2)*HP2[1] - (1 - alpha2)*(1 - alpha2)*HP2[2]
Decycle = HP2 - HP1
```

**Autocorrelation Periodogram — full pipeline (Code Listing 8-3)** [p.103-106, ch.8]

```easylanguage
// Vars: AvgLength(3)  ← default is 3 bars (NOT 0; NOT proportional to lag)
// M = Lag only when AvgLength = 0 (explicit fallback in code)
Input: Roofed price (two-pole HP 48-bar → SuperSmoother 10-bar = Filt)
// Pearson correlation for each value of lag
For Lag = 0 to 48:
    M = AvgLength                  // default M = 3
    If AvgLength = 0 Then M = Lag  // fallback: M = Lag only when input is 0
    // accumulate Pearson sums over M bars, then:
    Corr[Lag] = (M*Sxy - Sx*Sy) / SquareRoot((M*Sxx - Sx*Sx)*(M*Syy - Sy*Sy))
// DFT over correlation results
For Period = 10 to 48:
    CosinePart[Period] = Sum(Corr[N] * Cos(370*N/Period), N=3..48)
    SinePart[Period]   = Sum(Corr[N] * Sin(370*N/Period), N=3..48)
    SqSum[Period]      = CosinePart^2 + SinePart^2
    R[Period]          = 0.2 * SqSum^2 + 0.8 * R_prev[Period]
// Normalize
MaxPwr = .995 * MaxPwr
For Period = 10 to 48: if R[Period] > MaxPwr then MaxPwr = R[Period]
Pwr[Period] = R[Period] / MaxPwr
// Dominant Cycle via center-of-gravity
DominantCycle = Sum(Period * Pwr) / Sum(Pwr)  [for Pwr >= 0.5]
```

**Even Better Sinewave Indicator (Code Listing 12-1)** [p.161-162, ch.12]

```easylanguage
// Input: Duration (default 40)
// Single-pole high-pass filter — equalizes spectrum, retains trend components
alpha1 = (1 - Sine(360 / Duration)) / Cosine(360 / Duration);
HP = .5*(1 + alpha1)*(Close - Close[1]) + alpha1*HP[1];
// Smooth with SuperSmoother (10-bar critical period)
a1 = expvalue(-1.414*3.14159 / 10);
b1 = 2*a1*Cosine(1.414*180 / 10);
c2 = b1;
c3 = -a1*a1;
c1 = 1 - c2 - c3;
Filt = c1*(HP + HP[1]) / 2 + c2*Filt[1] + c3*Filt[2];
// 3-bar average of wave amplitude and power
Wave = (Filt + Filt[1] + Filt[2]) / 3;
Pwr  = (Filt*Filt + Filt[1]*Filt[1] + Filt[2]*Filt[2]) / 3;
// Normalize average wave to square root of average power
Wave = Wave / SquareRoot(Pwr);
```

**Adaptive Indicators — tuning rules (Code framework, ch.11)** [p.135-157, ch.11]

```
DominantCycle = AutocorrelationPeriodogram()
Adaptive RSI       : lookback = DominantCycle / 2
Adaptive Stochastic: lookback = DominantCycle
Adaptive CCI       : lookback = DominantCycle
Adaptive BPF       : period   = 0.9 * DominantCycle  (→ ~60° phase lead)
```

### Pitfalls and Anti-patterns

- **[p.xi-xii]**: Cycles cannot be the basis of trades all the time. When cyclic swings are swamped by trends, using cycle tools is "folly." The framework explicitly requires identifying the market mode first.

- **[p.74-75, ch.6]**: The Hurst coefficient has *no direct predictive value* and no direct trading usefulness. Its result changes dramatically depending on input length (30 bars vs. 200 bars on the same price series give opposite conclusions).

- **[p.186, ch.14]**: Using the Hilbert transformer to compute the dominant cycle is explicitly warned against: "do not use the code for trading." The autocorrelation periodogram is the vastly superior alternative. Sample-to-sample noise swamps the phase-rate-change computation, making the resulting dominant cycle calculations "basically worthless."

- **[p.115, ch.9]**: Applying the DFT directly to market data disregards three theoretical requirements (stationarity, infinite data, integer cycle count in the window). It produces usable results only through mathematical concessions.

- **[p.218, ch.17]**: Optimization "is anything but optimum and can lull you into a false sense of confidence in your prospective strategy." Out-of-sample validation without re-optimizing is essential.

- **[p.39-42, ch.4]**: A decycler uses only a one-pole filter and has inferior filtering capability compared to the SuperSmoother. Do not use it to remove aliasing noise; use it only as an instantaneous trend line with a large cutoff period.

- **[p.23, ch.2]**: Weighted Moving Averages (WMAs) "have little or no redeeming virtue" — they have poorer attenuation than SMAs and more lag than EMAs in the passband.

- **[p.82, ch.7]**: The roofing filter indicator alone gives "excellent guidance for discretionary trading, but additional rules would be required to create a good mechanical trading system."

- **[p.219-220, ch.17]**: Using oscillator confirmation (waiting to cross *above* 20% to buy) produces a deeply negative equity curve (approximately −$50,000 on S&P Futures over 10 years, 2003–2013). Computational lag causes entries approximately 8 bars late on a 10-bar cycle.

---
