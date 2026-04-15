# Rocket Science for Traders: Digital Signal Processing Applications

## Metadata
- **Author:** John F. Ehlers [cover, p.iv]
- **Year:** 2001 [copyright page, p.iv]
- **Publisher:** John Wiley & Sons, Inc., New York [p.iv]
- **Pages:** 265 (PDF); ~245 numbered in the body + front/backmatter [metadata]
- **ISBN:** 0-471-40567-1 [p.iv]
- **Main focus:** Introduction of Digital Signal Processing (DSP) to trading — use of the Hilbert Transform, Homodyne Discriminator, FIR/IIR filters, Ehlers filters, and cycle measurement to build minimum-lag indicators and systems adaptive to the market's dominant cycle.

## 1. Core Thesis
Ehlers argues that available trading software has not evolved alongside hardware — most indicators are primitive calculations that could be done with pencil and paper [Preface, p.vii]. The solution is to import DSP from the engineering domains (geophysics, electronics) into trading: treat price as a sampled signal that can be decomposed into two orthogonal components derived from the Drunkard's Walk — Trend Mode (solution of the Diffusion Equation) and Cycle Mode (solution of the Telegrapher's Equation) [ch.2, p.11-14]. The theoretical pair enables a trading system that switches rules according to the identified market mode.

The operational thesis: using the amplitude-corrected Hilbert Transform to extract Inphase and Quadrature components, and the Homodyne Discriminator to measure the dominant cycle in real time, one can build (a) a Signal-to-Noise Ratio, (b) the Sinewave Indicator (anticipates turning points by 1/16 of a cycle), (c) an Instantaneous Trendline with half-cycle lag, and (d) automatic mode identification — combined in the SineTrend Automatic System [Preface, p.vii-ix; ch.12, p.119-129].

## 2. Main Concepts
- **Trend Mode** — mode derived from the Diffusion Equation (symmetric Drunkard's Walk p=½); traders ask "will it go up or down?"; use moving averages [p.11-14]
- **Cycle Mode** — mode derived from the Telegrapher's Equation (Drunkard's Walk with persistence); traders ask "will the trend continue?"; use oscillators [p.11-14]
- **Drunkard's Walk (constrained Random Walk)** — base 1-D model with regular steps; in the persistence-p version, produces harmonic motion [p.10-11]
- **Nyquist criterion** — requires ≥2 samples/cycle; in trading the absolute minimum cycle is 2 bars, practical 5-8 bars [p.3-4]
- **Aliasing** — distortion from sampling at less than 2x/cycle; data must be smoothed before any operation to avoid high-frequency fold-back [p.4]
- **Decibels (dB)** — logarithmic unit; +3 dB = 2x power, −3 dB = half (cutoff frequency); amplitude 0.7 is half-power [p.5-6]
- **Analytic signal** — real waveform familiar to the trader, with no imaginary values; positive frequencies only (or negative only) [p.53]
- **Inphase / Quadrature (I, Q)** — orthogonal components (cosine and sine) obtained via the Hilbert Transform; Quadrature = 90° shift [p.54]
- **Hilbert Transform** — converts an analytic signal into a complex signal; shifts all positive frequencies by −90° and negative by +90° [p.54-55]
- **Homodyne Discriminator** — preferred algorithm for measuring the dominant cycle period, used throughout the book [Preface, p.viii; ch.7 referenced]
- **Phasor / phase angle** — rotational vector representation of the cycle; phasor amplitude = √(I²+Q²), angle = arctan(Q/I) [p.47, p.79]
- **Signal-to-Noise Ratio (SNR)** — ratio (signal power)/(noise power) in dB; noise defined as the average bar range (EMA α=0.1) [p.79-80]
- **Sinewave Indicator** — plot of sin(DCPhase) and sin(DCPhase+45°); crosses 22.5° before the turning point; does not generate whipsaws in Trend Mode [p.99-100]
- **Instantaneous Trendline (ITrend)** — SMA over the measured dominant cycle period; fully cancels the cyclic component [p.23, p.107]
- **LeadSine** — second line of the Sinewave Indicator, advanced by 45° [p.99-100]
- **Dominant Cycle Phase (DCPhase)** — heterodyne price with the dominant cycle and compute arctan(Imag/Real) — produces lag-free phase [p.95-96]
- **Ehlers filter** — nonlinear FIR filter whose coefficients are a function of a statistic (e.g., momentum²); detects edges/shifts [ch.18, p.185-188]
- **Order Statistic filter** — filter class based on ranking (not time); e.g., Median filter [p.186]
- **Market mode overriding rule** — if |SmoothPrice − Trendline|/Trendline ≥ 1.5%, force Trend Mode [p.114]
- **CycPart multiplier** — period multiplier for the Instantaneous Trendline SMA; optimized values 1.15 (T-Bonds) / 1.10 (Swiss Franc) [p.125, p.128]

## 3. Formulas / Equations
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

## 4. Algorithms and Pseudocode
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

## 5. Explicit Trading Rules
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

## 6. Pitfalls and Anti-patterns
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

## 7. Sensitive Parameters
- **Hilbert Transformer truncation n=3 (4-tap)** [p.56-57]: economic choice to minimize lag to 3 bars; coefficients 0.0962 / 0.5769 derived by trial-and-error to flatten amplitude response. Justification = frequency-domain shape, NOT P&L optimization → low curve-fit risk.
- **Amplitude correction (0.075·Period[1] + 0.54)** [p.58]: derived from measurement at 11dB @ 40-bar and 6.2dB @ 20-bar → linear fit. Mathematical, not tuned against market data.
- **Period clamps [6, 50]** [p.82]: 6 for practical Nyquist; 50 because above that the system loses responsiveness. Theoretical choice.
- **Rate-of-change clamp [0.67×, 1.5×]** [p.82]: limits spurious bar-to-bar "jumps". Preserves measurement continuity.
- **EMA α=0.2 in post-discriminator smoothing** [p.82]: 9-bar-equivalent lag; not optimized, "range tends not to change much".
- **Enhanced SNR amplitude coefficients 0.1759 / 0.4607** [p.88-89]: straight-line fit derived from a chirp (10-40 bars). Mathematical derivation, not curve-fit.
- **Phase wraparound at 315° (not 360°)** [p.96]: cosmetic choice — "more pleasing display" — does not affect signals.
- **Sinewave +45° lead** [p.99-100]: produces a crossover 22.5° before the turning point = 1/16 of the cycle. Pure mathematical derivation.
- **Trend-Mode override threshold 1.5%** [p.114]: PRAGMATIC parameter (Ehlers admits: "pragmatic observation, not theoretical"). **Curve-fit RISK** — may be asset-specific.
- **CycPart=1.15 (T-Bonds) / 1.10 (Swiss Franc)** [p.125, p.128]: **POST-HOC OPTIMIZED**. Ehlers argues low curve-fit risk due to high trade-to-parameter ratio (191-460 trades / 2 params over ~16 years). Still an optimized parameter — must pass CPCV.
- **Money-management stop $1,100 / $2,200** [p.125, p.128]: also optimized — asset-specific. High curve-fit risk if extrapolated.
- **Ehlers filter Length=15** [p.188]: "an example"; can be adapted to the dominant cycle. Not optimized.

## 8. Key Literal Quotes
> "Most of the trading tools available today are neither different nor more complex than the simple pencil-and-paper calculations that can be achieved through the use of mechanical adding machines." — [p.vii]

> "Momentum can never lead the event. Momentum is always more disjoint (i.e., noisier) than the original function." — [p.34]

> "Cycle Mode trading should be avoided when the SNR is below 6 dB." — [p.93]

> "A Trend Mode is declared if the 4-bar WMA is separated from the Instantaneous Trendline by more than 1.5 percent." — [p.118]

> "Since the Cycle Mode exists for the smallest fraction of time and since most traders make the most money following a trend rather than a cycle, it is best to assume that the market is in a Trend Mode unless some very specific criteria are met." — [p.113]

> "Market data tend to be nonstationary much of the time. Therefore, adaptive technique or nonlinear data processing is required for maximum effectiveness." — [p.195]

## 9. Cross-references to Other Books in This Knowledge Base
- The Hilbert Transform, Instantaneous Trendline, and Sinewave Indicator are also treated (more maturely and with refined parameters) in `cybernetic_analysis.md` — the 2004 book is a continuation/evolution of this one. See `cybernetic_analysis.md#3-formulas--equations` (truncated 4-tap Hilbert) and `cybernetic_analysis.md#sinewave-indicator-noncausal`. This `rocket_science.md` contains the original DERIVATION and the philosophical justification (Drunkard's Walk → Diffusion vs Telegrapher's Equation) that the later book simply assumes.
- The Trend/Cycle Mode duality is presented here as a consequence of two distinct PDEs [p.11-14]; in `cybernetic_analysis.md#2-conceitos-chave` the pair is reformulated as "Instantaneous Trendline + Cyber Cycle" (sum = unity in the frequency domain) — same concept, different derivation.
- Ehlers Filters (ch.18) are introduced FIRST here [p.185-195]; expanded in `cybernetic_analysis.md` (whether they appear there explicitly was not reviewed — N/A at this point).
- Curve-fit risk on the optimized CycPart and money-management stop [p.125] should be run through the CPCV/WFO framework described in `advances_fin_ml.md` and the parsimony principle (≤4 params) of `systematic_trading.md`.
- The SNR indicator [ch.8] is conceptually close to the "tradeable regimes" analysis in `regime_change.md` — both seek to filter out periods with insufficient signal — but the mechanisms differ (DSP vs HMM/statistical).
- FFT issues [Preface p.ix, ch.19 referenced] contrast with the time-series treatment in `time_series_hamilton.md` (classical ARIMA/spectral analysis); Ehlers argues for Maximum Entropy / Homodyne over direct Fourier.
