# Rocket Science for Traders: Digital Signal Processing Applications

## Metadata
- **Autor:** John F. Ehlers [cover, p.iv]
- **Ano:** 2001 [copyright page, p.iv]
- **Editora:** John Wiley & Sons, Inc., New York [p.iv]
- **Páginas:** 265 (PDF); ~245 numeradas no corpo + front/backmatter [metadata]
- **ISBN:** 0-471-40567-1 [p.iv]
- **Foco principal:** Introdução do Digital Signal Processing (DSP) ao trading — uso de Hilbert Transform, Homodyne Discriminator, filtros FIR/IIR, Ehlers filters e cycle measurement para construir indicadores com lag mínimo e sistemas adaptativos ao ciclo dominante do mercado.

## 1. Tese Central

Ehlers argumenta que o software de trading disponível não evoluiu junto com o hardware — a maioria dos indicadores são cálculos primitivos que poderiam ser feitos com papel e lápis [Preface, p.vii]. A solução é importar DSP dos domínios de engenharia (geofísica, eletrônica) para trading: tratar preço como um sinal amostrado que pode ser decomposto em duas componentes ortogonais derivadas do Drunkard's Walk — Trend Mode (solução da Diffusion Equation) e Cycle Mode (solução da Telegrapher's Equation) [ch.2, p.11-14]. O par teórico permite construir um sistema de trading que alterna regras segundo o modo de mercado identificado.

A tese operacional: usando o Hilbert Transform amplitude-corrigido para extrair componentes Inphase e Quadrature, e o Homodyne Discriminator para medir o ciclo dominante em tempo real, é possível construir (a) Signal-to-Noise Ratio, (b) Sinewave Indicator (antecipa turning points 1/16 de ciclo), (c) Instantaneous Trendline com lag de meio ciclo, e (d) identificação automática de modo — combinados no SineTrend Automatic System [Preface, p.vii-ix; ch.12, p.119-129].

## 2. Conceitos-Chave

- **Trend Mode** — modo derivado da Diffusion Equation (Drunkard's Walk simétrico p=½); traders perguntam "subirá ou descerá?"; usar moving averages [p.11-14]
- **Cycle Mode** — modo derivado da Telegrapher's Equation (Drunkard's Walk com persistência); traders perguntam "a tendência continuará?"; usar oscilladores [p.11-14]
- **Drunkard's Walk (Random Walk constrained)** — modelo base de 1 dimensão, passos regulares; na versão modificada com persistência p, produz movimento harmônico [p.10-11]
- **Nyquist criterion** — precisa ≥2 samples/ciclo; em trading o ciclo mínimo absoluto é 2 bars, prático 5-8 bars [p.3-4]
- **Aliasing** — distorção por amostrar menos que 2x/ciclo; dados devem ser smoothed antes de qualquer operação para evitar fold-back de altas frequências [p.4]
- **Decibels (dB)** — unidade logarítmica; +3 dB = 2x poder, −3 dB = metade (cutoff frequency); amplitude de 0.7 é half-power [p.5-6]
- **Analytic signal** — waveform real familiar ao trader, sem imaginary values; apenas frequências positivas (ou só negativas) [p.53]
- **Inphase / Quadrature (I, Q)** — componentes ortogonais (cosseno e seno) obtidos via Hilbert Transform; Quadrature = 90° shift [p.54]
- **Hilbert Transform** — converte analytic signal em sinal complexo; shifts todas frequências positivas por −90° e negativas por +90° [p.54-55]
- **Homodyne Discriminator** — algoritmo preferido de medida de período do ciclo dominante, usado em todo o livro [Preface, p.viii; ch.7 referenced]
- **Phasor / phase angle** — representação vetorial rotacional do ciclo; phasor amplitude = √(I²+Q²), ângulo = arctan(Q/I) [p.47, p.79]
- **Signal-to-Noise Ratio (SNR)** — quociente (signal power)/(noise power) em dB; noise definido como range médio dos bars (EMA α=0.1) [p.79-80]
- **Sinewave Indicator** — plotagem de sin(DCPhase) e sin(DCPhase+45°); cruza 22.5° antes do turning point; não gera whipsaw em Trend Mode [p.99-100]
- **Instantaneous Trendline (ITrend)** — SMA sobre período do ciclo dominante medido; cancela completamente a componente cíclica [p.23, p.107]
- **LeadSine** — segunda linha do Sinewave Indicator, 45° adiantada [p.99-100]
- **Dominant Cycle Phase (DCPhase)** — heterodyne preço com ciclo dominante e calcular arctan(Imag/Real) — produz fase sem lag [p.95-96]
- **Ehlers filter** — filtro FIR não-linear onde coeficientes são função de estatística (ex: momentum²); detecta edges/shifts [ch.18, p.185-188]
- **Order Statistic filter** — classe de filtros baseada em ranking (não tempo); ex: Median filter [p.186]
- **Market mode overriding rule** — se |SmoothPrice − Trendline|/Trendline ≥ 1.5%, força Trend Mode [p.114]
- **CycPart multiplier** — multiplicador do período para SMA da Instantaneous Trendline; valor otimizado 1.15 (T-Bonds) / 1.10 (Swiss Franc) [p.125, p.128]

## 3. Fórmulas / Equações

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

## 4. Algoritmos e Pseudocódigo

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

## 5. Regras de Trading Explícitas

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

## 6. Pitfalls e Anti-patterns

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

## 7. Parâmetros Sensíveis

- **Hilbert Transformer truncation n=3 (4-tap)** [p.56-57]: escolha econômica para minimizar lag a 3 bars; coeficientes 0.0962 / 0.5769 derivados por trial-and-error para achatar amplitude response. Justificativa = frequency-domain shape, NÃO optimização sobre P&L → baixo curve-fit risk.
- **Amplitude correction (0.075·Period[1] + 0.54)** [p.58]: derivada de measurement em 11dB @ 40-bar e 6.2dB @ 20-bar → linear fit. Matemática, não tunada contra dados de mercado.
- **Period clamps [6, 50]** [p.82]: 6 por Nyquist prático; 50 porque acima disso o sistema perde responsividade. Escolha teórica.
- **Rate-of-change clamp [0.67×, 1.5×]** [p.82]: limita "jumps" espúrios bar-a-bar. Mantém continuidade de medição.
- **EMA α=0.2 no smoothing pós-discriminador** [p.82]: 9-bar-equivalent lag; não é otimizado, é "range tends not to change much".
- **Enhanced SNR amplitude coefficients 0.1759 / 0.4607** [p.88-89]: straight-line fit derivado de chirp (10-40 bars). Mathematical derivation, não curve-fit.
- **Wraparound de fase em 315° (não 360°)** [p.96]: escolha cosmética — "mais pleasing display" — não afeta sinais.
- **Sinewave +45° lead** [p.99-100]: produz cruzamento 22.5° antes do turning point = 1/16 do ciclo. Derivação matemática pura.
- **Trend-Mode override threshold 1.5%** [p.114]: parâmetro PRAGMÁTICO (admitido por Ehlers: "pragmatic observation, not theoretical"). **RISCO de curve-fit** — pode ser asset-specific.
- **CycPart=1.15 (T-Bonds) / 1.10 (Swiss Franc)** [p.125, p.128]: **AJUSTADO POST-HOC POR OTIMIZAÇÃO**. Ehlers argumenta baixo curve-fit risk por trade-to-parameter ratio alto (191-460 trades / 2 params em ~16 anos). Ainda assim, é parâmetro optimizado — deve passar por CPCV.
- **Money-management stop $1,100 / $2,200** [p.125, p.128]: também otimizado — asset-specific. Alto curve-fit risk se extrapolado.
- **Ehlers filter Length=15** [p.188]: "an example"; pode ser adaptive ao dominant cycle. Não otimizado.

## 8. Citações Literais Importantes

> "Most of the trading tools available today are neither different nor more complex than the simple pencil-and-paper calculations that can be achieved through the use of mechanical adding machines." — [p.vii]

> "Momentum can never lead the event. Momentum is always more disjoint (i.e., noisier) than the original function." — [p.34]

> "Cycle Mode trading should be avoided when the SNR is below 6 dB." — [p.93]

> "A Trend Mode is declared if the 4-bar WMA is separated from the Instantaneous Trendline by more than 1.5 percent." — [p.118]

> "Since the Cycle Mode exists for the smallest fraction of time and since most traders make the most money following a trend rather than a cycle, it is best to assume that the market is in a Trend Mode unless some very specific criteria are met." — [p.113]

> "Market data tend to be nonstationary much of the time. Therefore, adaptive technique or nonlinear data processing is required for maximum effectiveness." — [p.195]

## 9. Conexões com Outros Livros Desta Base

- Hilbert Transform, Instantaneous Trendline, Sinewave Indicator são também tratados (mais maduros e com parâmetros refinados) em `cybernetic_analysis.md` — o livro de 2004 é uma continuação/evolução deste. Ver `cybernetic_analysis.md#3-fórmulas--equações` (truncated 4-tap Hilbert) e `cybernetic_analysis.md#sinewave-indicator-noncausal`. Este `rocket_science.md` contém a DERIVAÇÃO original e a justificativa filosófica (Drunkard's Walk → Diffusion vs Telegrapher's Equation) que o livro posterior apenas assume.
- Trend/Cycle Mode dualidade é apresentada aqui como consequência de duas PDEs distintas [p.11-14]; em `cybernetic_analysis.md#2-conceitos-chave` o par é reformulado como "Instantaneous Trendline + Cyber Cycle" (soma = unidade no domínio frequência) — mesmo conceito, derivação diferente.
- Ehlers Filters (ch.18) são introduzidos PRIMEIRO aqui [p.185-195]; expandidos em `cybernetic_analysis.md` (não revisado se aparecem lá explicitamente — N/A neste ponto).
- Curve-fit risk de CycPart e money-management stop otimizados [p.125] deveria passar pelo framework CPCV/WFO descrito em `advances_fin_ml.md` e pelo princípio de parcimônia (≤4 params) de `systematic_trading.md`.
- SNR indicator [ch.8] é conceitualmente próximo da análise de "tradeable regimes" em `regime_change.md` — ambos buscam filtrar períodos onde signal é insuficiente — mas mecanismos são distintos (DSP vs HMM/statistical).
- Problemas com FFT [Preface p.ix, ch.19 referenced] contrastam com tratamento time-series em `time_series_hamilton.md` (ARIMA/spectral analysis clássico); Ehlers argumenta por Maximum Entropy / Homodyne em vez de Fourier direto.
