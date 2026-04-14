# Cycle Detection (DSP-based)

Indicadores de Ehlers baseados em processamento de sinais para detectar ciclos dominantes.

## Sources

- [`books/rocket_science.md`](../books/rocket_science.md)
- [`books/cybernetic_analysis.md`](../books/cybernetic_analysis.md)
- [`books/cycle_analytics.md`](../books/cycle_analytics.md)
- [`books/cybernetic_trading.md`](../books/cybernetic_trading.md)

## From `books/rocket_science.md`

### Regras de Trading Explícitas

- **REGRA [p.114]**: Assuma Trend Mode por padrão; o Cycle Mode exige critérios específicos (two conditions only).
- **REGRA [p.114]**: Cycle Mode está ativo durante half-dominant-cycle após o cruzamento das linhas Sinewave/LeadSine.
- **REGRA [p.114]**: Cycle Mode se phase rate of change estiver entre 0.67× e 1.5× do rate dominante (360/Period).
- **REGRA [p.114]**: Override → Trend Mode quando |SmoothPrice − Trendline|/Trendline ≥ 1.5% (price "widely separated").
- **REGRA [p.122]**: Em Trend Mode, buy quando SmoothPrice cruza acima de Trendline; sell quando cruza abaixo.
- **REGRA [p.123]**: Em Cycle Mode, buy quando LeadSine cruza acima de Sine; sell quando cruza abaixo.
- **REGRA [p.108]**: Um trend está "em força" se o SmoothPrice não cruzou a Instantaneous Trendline no último half-dominant-cycle.
- **REGRA [p.108]**: Trend antecipado declarado se SmoothPrice não cruzou no último quarter-cycle e não aparenta retornar.
- **REGRA [p.108]**: Trend terminou quando SmoothPrice cruza novamente a Instantaneous Trendline.
- **REGRA [p.93]**: Evite Cycle Mode trading quando SNR < 6 dB — abaixo disso o sinal é menor que 2× noise e profit vira crapshoot.
- **REGRA [p.82-83]**: Clampar Period em [6, 50] bars; também limitar rate de mudança a [0.67×, 1.5×] bar-a-bar para estabilizar medição.
- **REGRA [p.125]**: Em T-Bonds (1984-2000), CycPart=1.15 e money-management stop de $1,100 otimizam SineTrend (profit $113k, 44.5% win, DD $8,137).
- **REGRA [p.128]**: Em Swiss Franc (1975-2000), CycPart=1.10 e stop de $2,200 — ratio avg_win/avg_loss = 1.56:1.
- **NUNCA [p.3-4]**: Tradar cycle periods < 2 bars (Nyquist) ou na prática < 5-8 bars — aliasing inviabiliza.
- **NUNCA [p.4]**: Operar sobre dados não-smoothed — alta-frequência aliasing contamina toda análise downstream.
- **NUNCA [Preface p.ix]**: Usar FFT para medir spectra de mercado — ch.19 é dedicado a explicar que FFT é inadequado para trading.

### Fórmulas / Equações

**SMA lag** [p.18-19, ch.3]

$$\text{Lag}_{SMA} = \frac{n - 1}{2}$$

**SMA frequency response** [p.24]

$$\text{SMA}(P) = \frac{\sin(\pi W / P)}{\pi W / P}$$

- $W$ = window width; $P$ = cycle period; nulls quando $W/P$ é inteiro

**WMA lag (center of gravity of triangle)** [p.27]

$$\text{Lag}_{WMA} = \frac{n - 1}{3}$$

**EMA alpha → lag** [p.29]

$$\alpha = \frac{1}{L + 1}, \quad \alpha = \frac{2}{n + 1} \text{ (equivalente a n-bar SMA)}$$

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

— +6 dB bias compensa definição de "0 dB SNR = signal amp = half the daily range".

**Enhanced SNR amplitude correction terms** (derived from chirp 10-40 bar) [p.88-89]

$$Q_3 = 0.5(\text{Smooth} - \text{Smooth}[2]) \cdot (0.1759 \cdot \text{SmoothPeriod} + 0.4607)$$

$$I_3 = \frac{\pi}{2} \cdot \frac{1}{N/2}\sum_{k=0}^{N/2-1} Q_3[k]$$

(o 1.57 ≈ π/2 compensa amplitude do half-cycle moving average)

**Ehlers filter (general form)** [p.188]

$$y = \frac{\sum_{i=1}^{n} c_i \cdot x_i}{\sum_{i=1}^{n} c_i}$$

onde $c_i$ é uma estatística (momentum absoluto, distância², SNR, volume, etc.) ordenada na janela.

**Distance-coefficient Ehlers filter** [p.193]

$$c_i = \sum_{k=1}^{n-1} (P_i - P_{i+k})^2$$

(coeficiente = "distância" quadrática ao longo da janela → resposta não-linear que detecta edges)

### Algoritmos e Pseudocódigo

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

### Pitfalls e Anti-patterns

- [p.17] Moving averages induzem lag que "quase sempre é característica ruim"; smoothing é sempre trade-off contra lag.
- [p.20] Janela muito larga (SMA): "sluggish" — só útil para longest trends. Janela muito estreita: whipsaws por inadequate smoothing.
- [p.28-29] EMA programming error comum: atribuir α=0.2 e (1-α)=0.9 (não somam 1) → recursão diverge / travamento. Sempre use α como variável global, escreva EMA em função de α.
- [p.33] Momentum NUNCA antecipa o evento em uma price action real — a antecipação de 90° é ilusão que SÓ existe se o preço for sine wave puro (Cycle Mode).
- [p.33] Momentum é sempre mais noisy/descontínuo que a função original (successive derivatives aumentam disjointedness).
- [p.35] A antecipação via momentum depende de PRIMEIRO identificar o market mode — em Trend Mode atribuir capacidade preditiva ao momentum é erro.
- [p.37-39] "More of a good thing" não funciona: aumentar comprimento do high-pass filter além de ~5 bars adiciona lag que destrói qualquer phase lead.
- [p.58] Hilbert Transformer ideal exige coeficientes de −∞ a +∞; na prática precisa ser severamente truncado. Lag de um Hilbert não-truncado a 40-bar cycle = 21 bars, inviável.
- [p.82] Primary SNR tem lag de 10 bars; Alternate SNR lag adicional de 7.5 bars (total 17.5) — "unthinkable for practical trading". Use Enhanced SNR (4 bars lag).
- [Preface p.ix] FFT é tool inadequado para trading porque ignora mathematical constraints (short data window, nonstationarity).
- [p.95] Fase calculada diretamente do Hilbert Transform é inutilizável: lag de 7 bars é "substantial portion of most tradable cycles" e medição é ruidosa.
- [p.125] Atenção: a mudança de CycPart + money-management stop é apresentada como "not curve fitting" porque testado em 16 anos — mas é claramente uma otimização pós-hoc de 2 parâmetros. Trade-to-parameter ratio citado como justificativa.
- [p.124] O Trend-Mode-only performance (sem Cycle) é "simply awful" (avg trade negativo) — o sistema depende fortemente das Cycle trades → risco se regime muda.
- [p.185] Linear filters (SMA/EMA) são ÓTIMOS apenas para sinais stationary slowly-varying + high-freq noise — market data não é nenhum dos dois; requer nonlinear.
- [p.194-195] Aumentar nonlinearidade dos coeficientes (cube, Gaussian) faz o Ehlers filter degenerar para algo indistinguível de median filter (perde gray-area resolution).
- [p.117] Trying to automate mode decision "often leads to great deal of chatter and rapid back-and-forth switching" — é por isso que Trend é default.

---

## From `books/cybernetic_analysis.md`

### Regras de Trading Explícitas

- **REGRA [p.4-5]** (Fisher Transform usage): após normalizar preços ao range [-1,+1] numa janela de 10 bars e aplicar Fisher transform, cruzamentos entre Fish e Fish[1] identificam turning points cíclicos com lag essencialmente zero.
- **REGRA [p.23-24]** (ITrend trend strategy): Long quando Trigger cruza acima de ITrend; Short quando cruza abaixo. Entry **sempre via limit order** a Close ± 35% do range do bar (RngFrac=0.35).
- **REGRA [p.25]** (ITrend reversal protection): Se a posição estiver perdendo mais de 1.5% (RevPct=1.015), reverter para o lado oposto no open do próximo bar — "major losses are avoided by recognizing when a trade is on the wrong side."
- **REGRA [p.26]** ($2,500 money-management stop): para currency futures, stop adicional de $2,500 independente da regra técnica.
- **NUNCA [p.24]**: usar stop orders ou market orders como entrada primária — limit orders capturam slippage como profit em vez de como custo.
- **REGRA [p.35-36]** (Cyber Cycle strategy, contrarian): como o lag total (1.5 smooth + ~0.5 cycle + 1 trigger + 1 execução = 4 bars) faz o signal ser "exatamente errado" em um ciclo de 8 bars, **usar o sinal invertido** com um EMA de lag adicional. Cross-under ⇒ Buy; cross-over ⇒ Sell Short.
- **REGRA [p.38]** (Cyber Cycle escape): se após 8 bars na trade ainda tiver open loss, sair imediatamente (reverte).
- **REGRA [p.57]** (RVI): indicador é cycle-mode apenas; comprar quando RVI cruza acima do Trigger (RVI[1]), vender quando cruza abaixo.
- **REGRA [p.152-153]** (Sinewave): cruzamento LeadSine-acima-de-Sine = entry ~1/16 ciclo antes do topo/fundo; **NÃO operar** quando as linhas não têm forma sinusoidal clara (sinaliza Trend Mode — filtro natural de whipsaw).
- **REGRA [p.221-223]** (Laguerre RSI): comprar quando RSI cruza acima de 20%, vender quando cruza abaixo de 80%.
- **REGRA [p.123-124]** (Adaptive indicators): sempre que possível, substituir length fixo pelo Dominant Cycle medido, via $\alpha_1 = 2/(\text{Period}+1)$.
- **NUNCA [p.1-2]**: atribuir significado estatístico a bandas ±1σ / ±2σ sobre price data assumindo Normal PDF — a suposição é comprovadamente falsa em Treasury Bond futures sobre 15 anos (1988-2003).
- **NUNCA [p.189, p.210]**: usar filtros de ordem superior a 2 (sem justificativa forte) para Gaussian, ou superior a 3 para Butterworth — o ringing e o lag crescem mais do que o benefício de atenuação.

### Fórmulas / Equações

**Fisher Transform** [p.3, Eq. 1.2]

$$y = 0.5 \cdot \ln\!\left(\frac{1+x}{1-x}\right)$$

- $x$ = input restrito a $-1 < x < 1$ (senão equação "explode")
- $y$ = output com PDF aproximadamente Gaussiana
- Na implementação, autor usa $y = 0.25 \cdot \ln((1+v)/(1-v)) + 0.5 \cdot y[1]$ (smoothing EMA α=0.5) [p.7]

**EMA transfer response (Z-transform)** [p.12, Eq. 2.2]

$$H(z) = \frac{\alpha}{1-(1-\alpha)Z^{-1}}$$

**EMA α ↔ SMA length equivalence** [p.13, Eq. 2.4]

$$\alpha = \frac{2}{\text{Length}+1}$$

**Second-order Gaussian High-Pass Filter (Cyber Cycle base)** [p.15, Eq. 2.7]

$$HPF_t = (1-\tfrac{\alpha}{2})^2 (P_t - 2P_{t-1} + P_{t-2}) + 2(1-\alpha)HPF_{t-1} - (1-\alpha)^2 HPF_{t-2}$$

**Instantaneous Trendline** [p.16, Eq. 2.9]

$$IT_t = (\alpha - \tfrac{\alpha^2}{4})P_t + \tfrac{\alpha^2}{2}P_{t-1} - (\alpha - \tfrac{3\alpha^2}{4})P_{t-2} + 2(1-\alpha)IT_{t-1} - (1-\alpha)^2 IT_{t-2}$$

- Default α=0.07 (≈ 28-bar equivalent) [p.24]
- Inicialização: for first 7 bars, $IT = (P + 2P[1] + P[2])/4$ [p.24]

**Trigger (2-bar leading momentum of ITrend)** [p.24]

$$\text{Trigger}_t = 2 IT_t - IT_{t-2}$$

**4-bar FIR symmetric smoother** [p.33, Eq. 4.1]

$$\text{Smooth}_t = (P_t + 2P_{t-1} + 2P_{t-2} + P_{t-3}) / 6$$

- Lag constante de 1.5 barras em todas as frequências.

**Cyber Cycle (applied to Smooth)** [p.34]

$$\text{Cycle}_t = (1-\tfrac{\alpha}{2})^2 (S_t - 2S_{t-1} + S_{t-2}) + 2(1-\alpha)\text{Cycle}_{t-1} - (1-\alpha)^2 \text{Cycle}_{t-2}$$

**Hilbert Transform Quadrature (4-tap truncated)** [p.109, Eq. 9.1]

$$Q_t = (0.0962\, C_t + 0.5769\, C_{t-2} - 0.5769\, C_{t-4} - 0.0962\, C_{t-6}) \cdot (0.5 + 0.08 \cdot InstPeriod_{t-1})$$

$$I_t = C_{t-3}$$

- Fator (0.5 + 0.08·InstPeriod) é compensação de amplitude dependente do período medido [p.110].

**DeltaPhase (via arctangent subtraction identity)** [p.117, Eq. 9.3]

$$\Delta\Phi_t = \frac{I_t/Q_t - I_{t-1}/Q_{t-1}}{1 + I_t I_{t-1}/(Q_t Q_{t-1})}$$

- Limites: $0.1 \le \Delta\Phi \le 1.1$ radians (evita períodos <6 bars e >63 bars) [p.117]

**Dominant Cycle period** [p.117-118]

$$DC = \frac{2\pi}{\text{Median}(\Delta\Phi, 5)} + 0.5$$

$$\text{InstPeriod}_t = 0.33 \cdot DC + 0.67 \cdot \text{InstPeriod}_{t-1}$$

$$\text{Period}_t = 0.15 \cdot \text{InstPeriod}_t + 0.85 \cdot \text{Period}_{t-1}$$

**Center of Gravity oscillator** [p.48, Eq. 5.2]

$$CG_t = -\frac{\sum_{i=0}^{N-1} (i+1) \cdot P_{t-i}}{\sum_{i=0}^{N-1} P_{t-i}} + \frac{N+1}{2}$$

- Length ótima = metade do Dominant Cycle [p.53]

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

- Ex: α=0.33 → λ=1.624 (resposta quase plana até 0.05 cycles/day) [p.188]

**Iterative SMA** [p.242, Eq. 17.5]

$$SMA_t = \frac{P_t - P_{t-N} + SMA_{t-1}}{N+1}$$

### Algoritmos e Pseudocódigo

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

### Pitfalls e Anti-patterns

- [p.1-2] **Gaussian PDF assumption**: CCI, Bollinger Bands e qualquer indicador com "sigma boundary" são baseados em premissa falsa. PDF real de preços parece mais com sinewave do que bell curve.
- [p.188] **Regularized filter com λ arbitrário**: λ=10 com α=0.33 amplifica em +6 dB ciclos de 33 bars (faz exatamente o oposto do smoothing desejado). Usar sempre $\lambda = e^{0.16/\alpha}$.
- [p.15, p.19] **Higher-order Gaussian filters têm transient "bell-ringing"**: "the ringing is more a function of the bell itself rather than a filtered response of a driving force" — evitar ordem > 2.
- [p.36] **Trading cycles diretamente gera signals sistematicamente atrasados**: lag cumulativo de smooth + cycle + trigger + execução = ~4 bars, o que para um ciclo de 8 bars inverte totalmente o sinal.
- [p.51, p.53] **CG length errada destrói o indicador**: se window = full dominant cycle, a CG fica estática no meio (metade dos dados puxa p/ direita, metade p/ esquerda). Sempre usar ~ ½ do Dominant Cycle.
- [p.152] **Sinewave em Trend Mode**: quando há tendência, a fase não avança e as linhas não cruzam — **isso é feature, não bug**. Forçar signals de sinewave em trend gera whipsaws fabricados.
- [p.227-229] **Single equity curve é enganoso**: a mesma combinação {% winners=45, PF=1.5} produz curvas dramaticamente diferentes a cada Monte Carlo run. Vendor que mostra uma curva sem Profit Factor e % winners está escondendo informação.
- [p.232-233] **Leading indicators têm noise gain obrigatório**: não existe causal filter que antecipe transients sem amplificar ruído — "you cannot get something for nothing; there is no magic predictor" [p.234].
- [p.26, p.32] **Falsa robustez de muitos parâmetros**: Ehlers defende sua Instantaneous Trend Strategy dizendo "highly unlikely that the strategy has been curve fitted" por ter **poucos parâmetros independentes** e grande número de trades em 25 anos — a contrapositiva sendo o pitfall.
- [p.220] **RSI = 14 é arbitrário**: "When Welles Wilder first introduced the RSI, I was curious as to why he selected 14 bars" — motivação para indicadores adaptativos em vez de constantes tradicionais.
- [p.117-118] **DeltaPhase pode ir a zero ou negativo** por ruído / ambiguidade de quadrante → necessita clip em [0.1, 1.1] rad + median filter de 5 amostras antes de ser usado.
- [p.119] **FFT é inadequado para mercados**: não consegue simultaneamente atender constraint de estacionariedade e produzir resolução suficiente; requer 16 full cycles para medida com resolução comparável ao Hilbert discriminator.

---

## From `books/cycle_analytics.md`

### Regras de Trading Explícitas

- **REGRA [p.36, ch.3]**: Apply a SuperSmoother filter with a cutoff period of 10 bars universally to all price data before any indicator computation. The SuperSmoother attenuates aliasing noise at 12 dB per octave; aliasing noise grows at 6 dB per octave, so the net effect is effective noise gating.

- **REGRA [p.88-89, ch.7]**: Precede every technical indicator with a roofing filter (two-pole HP + SuperSmoother). Without this, conventional indicators produce erroneous signals during trending markets due to Spectral Dilation. The text example uses 48-bar HP and 10-bar SuperSmoother; Code Listing 7-3 implements the generalized indicator with defaults HPPeriod=80 and LPPeriod=40 [p.81-82, ch.7].

- **REGRA [p.137, ch.11]**: Set the Adaptive RSI lookback to half the measured dominant cycle. At this setting, the RSI reaches 0 or 1 only when prices complete a genuine cyclic swing.

- **REGRA [p.142, ch.11]**: Set the Adaptive Stochastic lookback to the *full* measured dominant cycle period to guarantee that both highest and lowest closes are included in the range.

- **REGRA [p.152-153, ch.11]**: Tune the Adaptive Band-Pass Filter to 90% of the dominant cycle period to obtain approximately 60 degrees of phase lead. Buy/sell signals trigger when indicator and trigger lines cross outside the ±0.7 reference lines.

- **REGRA [p.220-221, ch.17]**: For oscillator-based swing trading, anticipate rather than confirm turning points. Generate long entry when oscillator crosses *below* the lower threshold (e.g., 20%), short entry when crosses *above* the upper threshold (e.g., 80%). Recovers approximately 4 bars of lag vs. the confirmation rule.

- **REGRA [p.222-223, ch.17]**: For band-pass swing trading, use the cosine-wave leading signal. Buy when Cosine crosses over its 1-bar delayed version; sell when crosses under. Produces a quarter-cycle phase lead.

- **REGRA [p.224-225, ch.17]**: Safety valve exit: if long and price closes below a SuperSmoother-smoothed lower channel, exit immediately. If trade is not profitable within half the expected trade duration, exit. "If you even think about hoping a trade will turn around, exit the trade immediately."

- **REGRA [p.225-226, ch.17]**: Stop-loss: use only as a guard against extreme losses. A simple percentage of entry price (2–5% for stocks) is sufficient. Do not build stop-loss logic into the core strategy signal.

- **NUNCA [p.218, ch.17]**: Do not optimize strategy parameters without requiring at least 30 trades per parameter. Apply sensitivity analysis: if the performance surface does not form a gentle hill across a range of parameter values, the strategy is not robust.

### Fórmulas / Equações

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

### Algoritmos e Pseudocódigo

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

### Pitfalls e Anti-patterns

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

## From `books/cybernetic_trading.md`

### Regras de Trading Explícitas

- **REGRA [p.13]**: Operar long S&P500 somente quando T-Bonds está acima da média móvel de 26 dias (filtro de regime positive-correlation); fora do mercado caso contrário — fica no mercado 59% do tempo e supera buy-and-hold.
- **REGRA [p.23]**: Intermarket divergence short-term — se T-Bonds[5]−T-Bonds[10] positivo e S&P500−S&P500[5] negativo (ou inverso), entrar na divergência; testar horizonte 10–30 dias.
- **REGRA [p.25, Table 1.6]**: T-Bonds usando Eurodollars — quando T-Bonds fecha abaixo da sua SMA(24) e Eurodollars acima da sua SMA(32), comprar T-Bonds no open; 59% win, avg trade $1,447.
- **REGRA [p.34]**: Day-of-week S&P500 — comprar segunda-feira se T-Bonds acima da SMA(26); $249/trade desde 1982.
- **REGRA [p.40, Table 3.1]**: Usar inflação (ratio CPI/Yield) para prever juros de curto prazo — 86% acerto desde 1971.
- **REGRA [p.48, Table 4.9]**: Só operar breakouts quando ADX(14) > 25 ou ADX subindo de <10 por 3 dos últimos 4; sair do trend quando 5-day diff(ADX) < 0.
- **REGRA [p.53-54]**: Sistema COT — se COT Index Commercials[Lag] > Ctrigger e COT Index Small < Strigger → comprar (Ruggiero recommends Lag=1-3 weeks, Ctrigger=30-55, Strigger=35-50 por mercado).
- **REGRA [p.65]**: Adaptive Channel Breakout — comprar em `Highest(High, DCycle)` onde DCycle vem do MEM com window=30, poles=6; D-Mark, Yen, Swiss Franc: win rate 44-49%, drawdown <$12,500.
- **REGRA [p.66-67]**: Usar Pearson correlation 40-day entre intermarket e traded market com threshold |ρ|>0.5 como filtro on/off — reduz drawdown ~50% e dobra average trade.
- **REGRA [p.105]**: Se PTI > 35 após wave 4 → esperar novo high em wave 5; se PTI < 35 → assumir double top / failed fifth.
- **REGRA [p.115-116]**: Nunca selecionar o set de parâmetros mais lucrativo; escolher aquele cercado por vizinhos com performance similar (flat profit surface).
- **REGRA [p.118-119]**: Distribuição de trades tem que permanecer similar entre dev set e live trading; mudança de distribuição precede a falha de um sistema mesmo que P&L corrente pareça bom.
- **REGRA [p.125]**: Stop trading imediatamente se drawdown live > 150% do dev set OR consecutive losers > 150% do dev set.
- **REGRA [p.134]**: Desenvolver modelos com pelo menos 30 casos por input; >30:1 ratio é mais robusto.
- **NUNCA [p.157]**: Usar profit factor puro como função de fitness em GA — evolui soluções curve-fit de 5 trades.
- **NUNCA [p.60]**: Tentar usar MEM diretamente em dados de preço brutos — precisa detrend (ex.: Butterworth(6) − Butterworth(20)).
- **NUNCA [p.62]**: Usar estocástico/RSI com período fixo — Lane ajusta ao dominant cycle (metade do ciclo).

### Fórmulas / Equações

**COT Index (Briese)** [p.53]

$$\text{COT Index} = 100 \times \frac{\text{Current Net} - \text{Lowest(Net, } N\text{)}}{\text{Highest(Net, } N\text{)} - \text{Lowest(Net, } N\text{)}}$$

- $N$ = 1.5–4 years. Buy when >90 using commercials; sell when <10. [p.53]

**Elliott Wave Oscillator (Tom Joseph)** [p.104]

$$\text{EWO} = \text{Average}\!\left(\tfrac{H+L}{2}, 5\right) - \text{Average}\!\left(\tfrac{H+L}{2}, 35\right)$$

**Inflation / Short-term Yield Oscillator** [p.40, Table 3.1]

$$\text{Ratio} = 1 - \frac{\text{Inflation}}{\text{Yield}}; \quad \text{InflatYieldOsc} = \text{Ratio} - \text{Average(Ratio,20)}$$

Rules: if Ratio < 0.2 or Osc < 0 and Yield > Yield[3 months ago] → rates will rise; if Ratio > 0.3 or Osc > 0.5 and Yield < Yield[3 months ago] → rates will fall.

**Efficiency Indicator (breakout-mode)** [p.49]

$$\text{Eff} = \frac{\text{Close} - \text{Close}[\text{Len}]}{\sum_{i=1}^{\text{Len}} |\text{Close} - \text{Close}[i-1]|}$$

Len=10; breakout mode when Eff ≥ 0.20.

**Pearson's Correlation** [p.58]

$$r = \frac{\sum_i (X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum_i (X_i - \bar{X})^2 \sum_i (Y_i - \bar{Y})^2}}$$

**Z-test for Trading-System Average Trade** [p.57-58]

$$Z = \frac{M - D}{\sqrt{V/N}}$$

- $M$ = sample mean; $D$ = null value; $V$ = variance; $N$ = number of trades. |Z|>2.33 rejects null at 99%. [p.58]

**Chi-square Pattern Significance** [p.58]

$$\chi^2 = \sum_i \frac{(O_i - E_i)^2}{E_i}$$

**Variance / Standard Deviation** [p.57]

$$V = \frac{1}{N}\sum_i (D_i - M)^2; \quad \sigma = \sqrt{V}$$

**Rescaled Range / Hurst Exponent (Peters-simplified)** [p.92-93]

$$N_i = \log\!\left(\tfrac{P_{i+1}}{P_i}\right); \quad X_{k,a} = \sum_{i=1}^{k}(N_{i,a} - \bar{e}_a); \quad R_a = \max_k X_{k,a} - \min_k X_{k,a}$$

$$\frac{R(n)}{S(n)} = C \cdot n^H; \quad D_H = 2 - H$$

**Fuzzy "Tall" Candle Membership** [p.106, Table 14.2]

$$\text{Tall} = \max\!\left(0, \min\!\left(1, \frac{\text{CRange} - \text{OneTrig}}{\text{OneTrig} - \text{ZeroTrig}}\right)\right)$$

where $\text{OneTrig} = \text{Average(CRange,LBack)} \times \text{OneCof}$.

**Forward Percent-K (neural-network target)** [p.124]

$$\text{Forward K} = \frac{\text{Highest(High}_{+N}, N) - \text{Close}}{\text{Highest(High}_{+N}, N) - \text{Lowest(Low}_{+N}, N)}$$

**Standard Error of Trading System** [p.119]

$$\text{Standard Error} = \frac{1}{\sqrt{N}}$$

where $N$ = number of trades. Used to compare development vs. testing set.

**Sharpe Ratio** [p.121]

$$\text{Sharpe} = \frac{R_A - R_F}{S}$$

where $R_A$ = average returns, $R_F$ = risk-free returns, $S$ = stdev of returns.

**Fitness Function (genetic-algorithm example, TSEvolve)** [p.156-157]

$$\text{Fitness} = \text{NetProfit} - 2 \times \text{MaxIDDrawDown}$$

Ruggiero warns against using profit factor alone — it would yield 5-trade curve-fit winners [p.157].

**Alternative Fitness (Net Profit / Drawdown × Win %)** [p.89]

$$\text{Fitness} = \frac{\text{NetProfit}}{\text{Drawdown}} \times \text{Winning\%}$$

### Algoritmos e Pseudocódigo

**Adaptive Channel Breakout (MEM-driven)** [p.65]

```
Input: window=30, poles=6, min_cycle=6, max_cycle=50
DCycle = round(RSMemCycle1_2(close, 6, 50, 30, 6, 0))
if trend_filter == 1:  # RSCycleTrend gate
    Buy  at Highest(High, DCycle) stop
    Sell at Lowest(Low, DCycle) stop
# early-trade tighter stop (seen in later modified version)
if MarketPosition == 1 and BarsSinceEntry < 10:
    ExitLong at Lowest(Low, DCycle/2) stop
if MarketPosition == -1 and BarsSinceEntry < 10:
    ExitShort at Highest(High, DCycle/2) stop
# normal cycle-length stop
ExitLong  at Lowest(Low, DCycle) stop
ExitShort at Highest(High, DCycle) stop
```

**Ruggiero/Barna Seasonal Index** [p.31, Table 2.2]

```
Step 1 — Develop seasonal and update as you walk forward in the data.
Step 2 — For each trading day of year, record next-N-day return and
         percentage of time market moved up vs down.
Step 3 — Multiply the 5-day return by the up-percentage.
Step 4 — Scale the result between -1 and +1 over the whole trading year.
```

**ADX Trend Mode Rules (Ruggiero-modified Wilder)** [p.48, Table 4.9]

```
Rule 1 — if ADX crosses above 25 -> trending
Rule 2 — if ADX crosses below 20 -> consolidating
Rule 3 — if ADX crosses below 45 from above -> consolidating (exhaustion)
Rule 4 — if ADX rises from below 10 on 3 of last 4 days -> trend starting
Rule 5 — rule-4 trend remains until 5-day diff(ADX) < 0
```

**Intermarket Divergence Entry Template** [p.23-24, p.25]

```
# Example: S&P500 using T-Bonds (positively correlated)
if SPX < Average(SPX, LenTr) and TBonds > Average(TBonds, LenInt):
    Buy at open
if SPX > Average(SPX, LenTr) and TBonds < Average(TBonds, LenInt):
    Sell at open
# Strong param pairs (e.g. LenTr=12/16, LenInt=26/30 on S&P500/T-Bonds
# dev set 4/21/82-2/7/96) produced 68-69% win rate [p.25, Table 1.4]
```

**T-Bonds / Eurodollar Divergence System** [p.25]

```
# T-Bonds and Eurodollars are positively correlated
if TBond.close < Avg(TBond.close, LenTB=24) and
   EuroDlr.close > Avg(EuroDlr.close, LenEuro=32):
    Buy TBonds at open
if TBond.close > Avg(TBond.close, LenTB=24) and
   EuroDlr.close < Avg(EuroDlr.close, LenEuro=32):
    Sell TBonds at open
# Result: 59% win, $1,447 avg trade, DD=-$13,331 (1/2/86-2/7/96)
```

**Breakout Mode Index (Raschke-inspired composite)** [p.49-50]

```
# Four confusion/equilibrium components, averaged N days:
comp1 = mom(5), mom(10), mom(20) not all same sign  # confusion
comp2 = (SlowK(9) in 40..60) and (SlowK(14) in 40..60)
comp3 = Volatility(10) == Lowest(Volatility, 20)    # low vol
comp4 = abs(Efficiency(10)) <= 0.20
BreakoutMode = Average(comp1+comp2+comp3+comp4, N)
Enter breakout trade only when BreakoutMode >= 2
```

**Genetic-Algorithm Rule Evolution (TSEvolve)** [p.156-158]

```
Population   = 500
Crossover    = 0.30
Mutation     = 0.30
Chromosome   = 3 genes × 4 elements (rule_id, p1, p2, p3)
Rule IDs 1..14 span momentum thresholds, EMA comparisons, FastD
bands, for Data1 (traded market), Data2, Data3 (intermarkets)
Fitness      = NetProfit - 2 * MaxIDDrawDown
Selection    = roulette wheel weighted by fitness
Crossover    = one-point, two-point, or uniform (p.90-91)
Stop         = after N generations (e.g., 3000)
Post-filter  = human expert rejects statistical artifacts
```

**Scatter-Chart Stop Development** [p.73-75]

```
Step 1 — Simulate system without stops.
Step 2 — Log per-trade: EntryDate, MarketPosition,
         MaxPositionLoss, FinalProfit.
Step 3 — Plot MaxAdverseMovement (X) vs FinalProfit (Y) scatter.
Step 4 — Choose stop level such that only a small fraction of eventual
         winners are cut.
Step 5 — Repeat per-bar (bar 5, bar 10, ...) to build trailing-stop schedule.
Step 6 — For adaptive stop: mean + 1 sigma of adverse movement.
```

**Rough-Sets / Machine Induction for Rule Generation (C4.5-based)** [p.93]

```
# Markets are not Gaussian — rough sets make no distributional assumption
for each rule-candidate in induced decision tree:
    if accuracy(rule) >= 60% on dev set and
       coverage(rule) >= 5% of class cases and
       rule is uniformly distributed across dev data:
        keep rule
    else:
        discard as statistical artifact
```

### Pitfalls e Anti-patterns

- [p.32] **Seasonal reliability**: Day-of-year seasonality com apenas 10-20 ocorrências é quase curve-fit; exigir 80%+ accuracy ou não operar.
- [p.60] Fourier analysis falha em dados financeiros porque requer séries longas e estacionárias; usar MEM (Burg 1967) em vez disso.
- [p.73-74] Usar o otimizador do TradeStation direto para definir stops pode derrubar win rate — analisar scatter charts da adverse movement trade-by-trade.
- [p.77-78] Trading um sistema sem monitorar a equity curve é "como dirigir à noite sem faróis".
- [p.93] Rough sets / machine induction em financial data — markets não são gaussianos; métodos que não assumem distribuição são preferíveis (C4.5 / rough sets).
- [p.111-112] Definir time-frame sem considerar capital: sistema S&P500 overnight com $10,000 é suicídio; preferir T-Bonds.
- [p.111] Usar apenas um bull market nos dados; precisa pelo menos 1 bull + 1 bear em dev e test sets; mínimo 10 anos daily.
- [p.65, p.115] Reversal-stop-and-reverse systems produzem large losers ocasionais; mitigar com target profit ou time-based exit (early-trade tighter stop).
- [p.29] Não usar o par de parâmetros mais "profitable"; o "flatter the profit surface" e "robust" parameters são melhores — mesmo em intermarket, the most profitable set of parameters is surrounded by similarly profitable neighbors.
- [p.121-122] A **distribuição** de trade P&L precede falha do sistema em vários meses; se a forma da curva muda, parar mesmo com P&L ainda positivo.
- [p.125] Aumento de 150% no max drawdown vs dev set = DANGER, parar o sistema.
- [p.125-126] Neural network com life-span curto (semanas) para em padrões transitórios e morre sem aviso por falta de testing set estatisticamente significante.
- [p.144-145] Train a neural network multiple times with different initial weights; if results diverge, the model is not robust (similar results across trainings = reliable network).
- [p.146] Raw output de NN com regras primitivas (long > 0, short < 0) gera drawdown muito alto; sempre usar threshold (ex: ±0.10) e filtro de predictive correlation.
- [p.151] Error function padrão (RMSE) em neural networks produz large losing trades em trading; evoluir pesos via GA com função de fitness customizada é melhor.
- [p.157] Profit factor sozinho como fitness function em GA converge em soluções curve-fit de 5 trades ganhadores — usar `NetProfit − 2×MaxIDDrawDown`.

---
