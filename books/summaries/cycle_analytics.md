# Cycle Analytics for Traders

## Metadata
- **Author:** John F. Ehlers [p.iv]
- **Year:** 2013
- **Publisher:** John Wiley & Sons
- **Pages:** 252
- **ISBN:** 978-1-118-72851-2
- **Main focus:** Digital signal processing (DSP) techniques adapted from electrical engineering to extract cyclic structure from market data and build adaptive, low-lag trading indicators.

## 1. Core Thesis
Market data possesses measurable cyclic structure arising from the constrained random walk physics of trader behavior, and digital signal processing (DSP) techniques developed in electrical engineering can be adapted to extract this structure and create superior trading indicators [ch.6, p.71-74]. The central argument is that thinking of prices in the *frequency domain* — not just the time domain — reveals which indicator parameters are appropriate and why, replacing arbitrary fixed lookback periods with adaptive ones tuned to the measured dominant cycle [p.xi-xii].

A key empirical obstacle is *Spectral Dilation*: market data's spectral power density is proportional to $1/F^\alpha$, meaning longer cycles have proportionally larger amplitude swings. Traditional indicators embed this distortion without compensation, producing erroneous overbought/oversold signals during trends. Ehlers argues that a *roofing filter* (two-pole high-pass filter + SuperSmoother) must precede any indicator computation to create a zero-mean, Spectral-Dilation-corrected data stream [p.77-89, ch.7]. The book's second thesis is that market cycles are *evanescent* — they come and go — and therefore the *autocorrelation periodogram* is the preferred spectral estimator because it has the least latency, requires no Spectral Dilation compensation, and automatically estimates cyclic power as a function of time [p.102-103, ch.8].

## 2. Main Concepts
- **Transfer Response** — The ratio Output/Input that completely describes any linear filter. Written as a ratio of two polynomials in the Z-transform domain; the only thing differentiating filters is coefficient selection [p.1-2, ch.1].

- **Nonrecursive (FIR) Filter** — Output depends only on input samples; also called finite impulse response, moving average, tapped delay line. Lag = $(N-1)/2$ bars for symmetric coefficients, constant at all frequencies [p.3-4, ch.1].

- **Recursive (IIR) Filter** — Output depends on previous output values; also called EMA, infinite impulse response, autoregressive. The EMA is the fundamental recursive filter: $\text{EMA} = \alpha \cdot \text{Input} + (1-\alpha) \cdot \text{EMA}[1]$; lag = $(1/\alpha) - 1$ bars [p.9-10, p.35, ch.1-2].

- **SMA lag** — An N-length SMA has lag exactly $(N-1)/2$ bars. The critical period (−3 dB) of an SMA is approximately twice its length [p.16-17, ch.2].

- **SuperSmoother filter** — A modified two-pole Butterworth filter with a two-element moving average in the numerator, creating a zero in the transfer response at the Nyquist frequency. Delivers approximately 1.5 bars maximum lag for a 10-bar cutoff period and attenuates aliasing noise at 12 dB per octave [p.32-36, ch.3].

- **Spectral Dilation** — Market data's spectral power density is proportional to $1/F^\alpha$; longer cycle periods have correspondingly larger amplitude swings. Virtually ignored in all conventional indicators; responsible for erroneous overbought/oversold readings during trends [p.77-78, p.88, ch.7].

- **Roofing Filter** — Serial combination of a two-pole high-pass filter and a SuperSmoother. In descriptive text (p.77) the example uses a 48-bar HP cutoff and 10-bar SuperSmoother cutoff, passing cyclic components between approximately 10 and 48 bars; establishes a near-zero mean; eliminates Spectral Dilation effects before indicator computation. Note: Code Listing 7-3 (the generalized indicator implementation) uses `HPPeriod(80)` and `LPPeriod(40)` as its default inputs — the text notes these are set "rather arbitrarily" as an example [p.77-82, ch.7].

- **Decycler** — A filter created by subtracting a single-pole high-pass filter output from the input, leaving only low-frequency trend components by cancellation. Functions as a one-pole low-pass filter with exceptionally low lag; serves as an instantaneous trend line [p.39-42, ch.4].

- **Decycler Oscillator** — Difference of two **two-pole** high-pass filters (using $K=0.707$ in the angle, per the unified filter theory table) at different cutoff periods; displays the trend as an oscillator; zero crossings signal trend transitions. Each HP filter uses the `.707` factor, making both filters two-pole — in contrast to the basic Decycler which uses a single-pole HP (no `.707`) [p.43-45, ch.4].

- **Band-Pass Filter (BPF)** — Simultaneously a detrender and a smoother. When precisely tuned to the dominant cycle, produces output with *zero lag*. Selectivity measured by Q = center_period / bandwidth [p.47-51, ch.5].

- **Automatic Gain Control (AGC)** — Fast attack–slow decay amplitude normalizer. Decay factor $K = 0.991$ chosen to produce 1.5 dB gain slope across the 10–48 bar trading band. Normalizes band-pass or other indicator output to swing between −1 and +1 [p.54-55, ch.5].

- **Hurst Coefficient** — Measures long-memory structure: $H = 2 - D$ (fractal dimension); $H > 0.5$ indicates trend mode; $H < 0.5$ indicates cycle mode; $H = 0.5$ is a random walk. Has *no direct predictive value* for trading [p.65-68, p.74-75, ch.6].

- **Autocorrelation Periodogram** — Combines Pearson autocorrelation at lags 0–48 with a discrete Fourier transform (DFT inner loop over N=3..48) to estimate the market spectrum. Preferred over DFT and comb-filter methods because of lowest latency and no need for Spectral Dilation compensation [p.102-106, ch.8].

- **Dominant Cycle** — The cycle period with the highest spectral power, extracted from the autocorrelation periodogram using a center-of-gravity (CG) algorithm: $\text{DC} = \sum(\text{Period} \cdot \text{Pwr}) / \sum(\text{Pwr})$ for periods where Pwr $\geq 0.5$ [p.103-104, ch.8].

- **Fisher Transform** — Converts a zero-mean indicator bounded between −1 and +1 to an approximately normal (Gaussian) distribution; output expressed in standard deviations [p.195-197, ch.15].

- **Inverse Fisher Transform** — Acts as a soft limiter; compresses large absolute values toward ±1, removing extraneous squiggles [p.198-200, ch.15].

- **Hilbert Transformer (modified)** — Creates an analytic signal (real + imaginary quadrature components) from price data using one-bar difference for phase quadrature and AGC for amplitude. Classic FIR version has 11-bar lag, unusable for trading [p.175-186, ch.14].

- **SwamiCharts** — Heat map display of an indicator computed over a range of lookback periods (5–48 bars), providing statistical context for indicator signals [p.203-216, ch.16].

- **Even Better Sinewave Indicator** — Roofing filter variant using a single-pole high-pass filter to equalize the spectrum and retain trend components. Wave amplitude is normalized to the square root of average power; swings between −1 and +1. Hold long when near +1, short when near −1. Default duration input = 40 bars [p.159-163, ch.12].

## 3. Formulas / Equations
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

## 4. Algorithms and Pseudocode
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

## 5. Explicit Trading Rules
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

## 6. Pitfalls and Anti-patterns
- **[p.xi-xii]**: Cycles cannot be the basis of trades all the time. When cyclic swings are swamped by trends, using cycle tools is "folly." The framework explicitly requires identifying the market mode first.

- **[p.74-75, ch.6]**: The Hurst coefficient has *no direct predictive value* and no direct trading usefulness. Its result changes dramatically depending on input length (30 bars vs. 200 bars on the same price series give opposite conclusions).

- **[p.186, ch.14]**: Using the Hilbert transformer to compute the dominant cycle is explicitly warned against: "do not use the code for trading." The autocorrelation periodogram is the vastly superior alternative. Sample-to-sample noise swamps the phase-rate-change computation, making the resulting dominant cycle calculations "basically worthless."

- **[p.115, ch.9]**: Applying the DFT directly to market data disregards three theoretical requirements (stationarity, infinite data, integer cycle count in the window). It produces usable results only through mathematical concessions.

- **[p.218, ch.17]**: Optimization "is anything but optimum and can lull you into a false sense of confidence in your prospective strategy." Out-of-sample validation without re-optimizing is essential.

- **[p.39-42, ch.4]**: A decycler uses only a one-pole filter and has inferior filtering capability compared to the SuperSmoother. Do not use it to remove aliasing noise; use it only as an instantaneous trend line with a large cutoff period.

- **[p.23, ch.2]**: Weighted Moving Averages (WMAs) "have little or no redeeming virtue" — they have poorer attenuation than SMAs and more lag than EMAs in the passband.

- **[p.82, ch.7]**: The roofing filter indicator alone gives "excellent guidance for discretionary trading, but additional rules would be required to create a good mechanical trading system."

- **[p.219-220, ch.17]**: Using oscillator confirmation (waiting to cross *above* 20% to buy) produces a deeply negative equity curve (approximately −$50,000 on S&P Futures over 10 years, 2003–2013). Computational lag causes entries approximately 8 bars late on a 10-bar cycle.

## 7. Sensitive Parameters
- **SuperSmoother cutoff period = 10 bars** [p.36, ch.3]: Ehlers does not optimize this value; it is chosen on signal processing grounds — short enough to eliminate aliasing noise from cycles below 10 bars (Nyquist-induced), long enough to preserve 10-bar and longer cycle content. The book recommends universally applying this value without asset-specific tuning.

- **Roofing filter HP cutoff: 48 bars (conceptual default) vs. HPPeriod=80 (Code Listing 7-3 default)** [p.77-82, ch.7]: The descriptive text in Ch.7 uses 48 bars as the HP cutoff example, capturing the tradeable 10–48 bar band. Code Listing 7-3 (the generalized indicator) defaults to HPPeriod=80 and LPPeriod=40 — Ehlers notes these are set "rather arbitrarily" in the example [p.82, ch.7]. The 48-bar value is hardcoded (not an optimized parameter) in the conceptual examples (Code Listings 7-1, 7-2, 7-4, 7-5); the Code Listing 7-3 defaults are illustrative, not prescriptive.

- **Autocorrelation periodogram: AvgLength default = 3 bars; lag range = 0–48 (Pearson), DFT inner loop N = 3–48** [p.103-106, ch.8]: Code Listing 8-3 declares `AvgLength(3)` as its default. The line `If AvgLength = 0 Then M = Lag` is a fallback for when the input is explicitly set to zero (as in the aurora indicator, Code Listing 8-2, which uses `AvgLength(0)` as its default). The DFT summation begins at N=3 to avoid trivial autocorrelations of the shortest lags. Maximum lag of 48 matches the roofing filter upper cutoff. Fixed on signal-processing grounds, not in-sample optimization.

- **AGC decay constant K = 0.991** [p.54-55, ch.5]: Derived analytically to produce 1.5 dB gain slope across the 10–48 bar band. Not curve-fit; derived from the desired gain characteristic equation. Note: the autocorrelation periodogram (Code Listing 8-3) uses a separate MaxPwr decay of `.995` for its normalization block [p.106, ch.8] — distinct from this AGC constant.

- **Band-pass bandwidth = 30%** [p.53, ch.5]: Ehlers recommends 30% as a practical compromise. Narrower bandwidth (high Q) causes more ringing; wider bandwidth reduces cycle isolation. "Using a band-pass filter having a 30 percent pass band is a relatively good compromise between selectivity and transient responsiveness for most trading applications" is explicitly stated as the practical recommendation, not an optimized figure.

- **Adaptive BPF tuned to 0.9 × DC** [p.152-153, ch.11]: The 10% reduction from the measured dominant cycle is analytically derived to produce approximately 60 degrees of phase lead. Not an in-sample-optimized coefficient.

- **Even Better Sinewave duration parameter default = 40 bars** [p.161, ch.12]: The default Duration input is 40 bars, corresponding to a maximum trend trade duration of approximately two months. The book demonstrates a second example at Duration=20 bars. Ehlers notes that decreasing Duration increases sensitivity to shorter wavelengths and that "some care should be taken when shortening the duration input." No sensitivity-stable range (e.g., 4–12 bars) is identified in the text; the parameter directly controls the high-pass filter critical period and should be adjusted to fit trading style, not optimized numerically.

- **30-trades-per-parameter rule** [p.218, ch.17]: Ehlers explicitly states this as the minimum sample size for statistical confidence in any single parameter. This is a practitioner heuristic, not derived from a specific distribution assumption, but it aligns with statistical power considerations.

## 8. Key Literal Quotes
> "It is important to remember that no filter is predictive — filter responses are computed on the basis of historical data samples." — [p.1, ch.1]

> "Minimizing lag in trading filters is almost more important than the smoothing that is realized by using the filter. Therefore, filters used for trading best use a relatively small amount of input data and should not be complex." — [p.2, ch.1]

> "I urge readers to universally adapt the SuperSmoother filter set to a cutoff period of 10 bars or so on all data to attenuate aliasing noise." — [p.36, ch.3]

> "Spectral Dilation is inherently part of market data, arising from the fractal nature of the data. That is, longer cycle periods necessarily have correspondingly larger amplitude swings." — [p.88, ch.7]

> "The autocorrelation periodogram has the least latency of all market data spectral estimates." — [p.113, ch.8]

> "Market cycles are evanescent—they come and go and change their periodicity over time." — [p.109, ch.8]

> "Trading systems should be simple to avoid curve fitting to the data set on which the system is developed." — [p.217, ch.17]

> "I can assure you that the process [of optimization] is anything but optimum and can lull you into a false sense of confidence in your prospective strategy." — [p.218, ch.17]

> "There is one unmistakable psychological signal to exit a trade. That is, if you even think about hoping a trade will turn around and move in your favor, then exit the trade immediately. Hope has a negative value in trading." — [p.224, ch.17]

## 9. Cross-references to Other Books in This Knowledge Base
- **`rocket_science.md`** — Ehlers's direct predecessor book (2001). The Even Better Sinewave Indicator evolved from the original Sinewave Indicator first introduced in 1996 and developed further there [p.164, ch.12]. The MESA algorithm originates in *Rocket Science for Traders*. The current book extends the DSP framework to autocorrelation-based spectral analysis not present in the earlier work. Both books share the roofing filter concept and use of SuperSmoother as a universal noise reducer.

- **`cybernetic_analysis.md`** — Ehlers's intermediate book (*Cybernetic Analysis for Stocks and Futures*). The current book supersedes many of its spectral analysis techniques, replacing earlier dominant cycle methods with the autocorrelation periodogram. Adaptive indicators in Chapter 11 are extensions of the cybernetic framework. Both books share the foundational DSP vocabulary (HP filters, IIR/FIR distinction, lag minimization). The Even Better Sinewave Indicator represents a further evolution of the Sinewave Indicator approach used in both prior books.

- **`stat_sound_indicators.md`** — Related in statistical methodology. Both books use Pearson correlation and normalization frameworks; the autocorrelation periodogram (Chapter 8) applies Pearson correlation as its first stage [p.102-103, ch.8]. Both emphasize that overbought/oversold indicator interpretations are statistical rather than deterministic [p.14, ch.1].

- **`trading_systems_methods.md`** — Referenced directly: Kaufman's KAMA (adaptive moving average) is cited in Chapter 11 [p.135, ch.11] as a volatility-reactive adaptive filter, contrasted with Ehlers's cycle-period-adaptive approach.

- **`quant_trading_chan.md`** — Shares emphasis on statistical significance in backtesting and overfitting risk. Both require out-of-sample validation without re-optimizing. Ehlers's 30-trades-per-parameter rule [p.218, ch.17] parallels Chan's backtesting rigor.

- **`new_tech_trader.md`** — N/A: This slug does not exist in the current knowledge base. Chande and Kroll are referenced in Chapter 11 as the origin of VIDYA, but no corresponding summary file exists and no cross-reference can be established.
