# Quantitative Trading: How to Build Your Own Algorithmic Trading Business

## Metadata
- **Autor:** Ernest P. Chan [p.i, capa]
- **Ano:** 2009 [p.iv]
- **Editora:** John Wiley & Sons (Wiley Trading series) [p.iv]
- **Páginas:** 204 (printed: ~181 páginas de conteúdo + appendix/index)
- **ISBN:** 978-0-470-28488-9 (cloth) [p.iv]
- **Foco principal:** Guia prático para o trader independente construir um negócio de statistical arbitrage (stocks, futures, FX) com capital modesto.

## 1. Tese Central

"Make everything as simple as possible. But not simpler." — Einstein, citado por Chan [p.3]. A tese central de Chan é que traders independentes, operando de casa com $50k-$100k, podem superar hedge funds institucionais ao explorar estratégias de *baixa capacidade* (low capacity strategies) que são economicamente inviáveis para fundos grandes [ch.8, p.158]. A chave não está em matemática avançada (neural networks, stochastic calculus) mas em (1) simplicidade estrutural das estratégias, (2) disciplina no framework de backtest para evitar viéses, e (3) uso do Kelly formula para sizing e alocação de capital entre múltiplas estratégias [ch.6, p.95-96].

Chan argumenta que statistical arbitrage — operando stocks, futures e FX simples — não requer PhD; requer parcimônia (≤5 parâmetros), dados sem survivorship bias sempre que possível, e gestão emocional de drawdowns [ch.2-3, ch.6].

## 2. Conceitos-Chave

- **Statistical arbitrage** — trading quantitativo de instrumentos simples (stocks, futures, currencies), distinto de derivativos complexos [p.2]
- **Sharpe ratio** — métrica principal de Chan para comparar estratégias; razão entre retorno excedente médio e desvio-padrão dos retornos excedentes [p.18, p.43]
- **Information ratio** — versão do Sharpe usando um benchmark de mercado (índice) em vez da taxa livre de risco; apropriado para estratégias long-only [p.18]
- **Drawdown / Maximum drawdown / Maximum drawdown duration** — diferença entre equity atual e high watermark; maior queda peak-to-trough; maior período para recuperar losses [p.21, p.43]
- **High watermark** — máximo global da equity curve até o tempo t [p.21]
- **Survivorship bias** — databases que omitem empresas delistadas/bancarrotas, inflando artificialmente o backtest de estratégias "buy on the cheap" [p.14, p.24, p.40-42]
- **Look-ahead bias** — usar informação disponível somente no futuro (ex: "comprar dentro de 1% da mínima do dia") para gerar sinais [p.51]
- **Data-snooping bias** — overfit de parâmetros a ruído histórico; pior quanto mais parâmetros [p.25, p.52-53]
- **Regime shift** — mudança estrutural nos mercados (decimalização, revogação do short-sale rule, crise subprime) que invalida séries antigas [p.25, p.104]
- **Mean-reverting vs momentum regime** — duas categorias básicas de estratégias lucrativas; preços random-walking não são tradáveis [p.116]
- **Cointegration** — combinação linear de duas séries não-estacionárias que produz uma série estacionária I(0); base de pair trading [p.126-127]
- **Kelly formula (continuous finance)** — fração ótima de equity por estratégia para maximizar long-term compounded growth [p.97]
- **Half-Kelly** — usar metade da alavancagem Kelly para segurança contra erros de estimação e fat tails [p.98, p.105]
- **Capacity** — quantidade de equity que uma estratégia pode absorver sem degradar retornos; niche do trader independente são estratégias de baixa capacidade [p.27, p.158]
- **Fama-French 3-Factor model** — retorno de stock como função de beta, market cap, book-to-price ratio [p.134]
- **Factor exposure / factor return / specific return** — X (sensibilidades), b (drivers comuns), u (ruído específico) no APT R = Xb + u [p.133-134]
- **Ornstein-Uhlenbeck formula** — modelo contínuo de mean reversion usado para calcular half-life ótimo [p.140-141]
- **PEAD (Post-Earnings Announcement Drift)** — estratégia momentum: comprar stocks cujo earnings surpreende, shortar os que decepcionam [p.118]

## 3. Fórmulas / Equações

**Sharpe Ratio (Chan's convention)** [p.43-44]

$$\text{Annualized Sharpe Ratio} = \sqrt{N_T} \cdot \frac{\overline{R - r_F}}{\sigma_{R}}$$

Onde $N_T$ é o número de períodos de trading por ano; para NYSE intraday $N_T = 252 \times 6.5 = 1638$, NÃO $252 \times 24$ [p.45]. Para estratégias dollar-neutral (self-financing), NÃO subtrair $r_F$: a margin balance rende crédito próximo de $r_F$, cancelando [p.43-44]. Para long-only day-trading sem holding overnight, também NÃO subtrair $r_F$ (sem financing cost) [p.44]. Regras de bolso: Sharpe < 1 = não stand-alone; Sharpe ≥ 2 = lucrativo quase todo mês; Sharpe ≥ 3 = lucrativo quase todo dia [p.43].

**Information Ratio** [p.18]

$$\text{Information Ratio} = \frac{\overline{R_{portfolio} - R_{benchmark}}}{\sigma(R_{portfolio} - R_{benchmark})}$$

**Compounded, Levered Growth Rate (Gaussian process)** [p.112]

$$g(f) = r + fm - \frac{s^2 f^2}{2}$$

Onde $f$ é leverage, $r$ é risk-free rate, $m$ é média simples de um-período excess return, $s$ é std dos uncompounded returns [p.112]. Caso especial: para random walk puro ($m=0, f=1$), $g = -s^2/2 < 0$ — risco diminui growth rate mesmo com drift zero [p.97].

**Kelly Formula — one strategy (Gaussian)** [p.97, p.113]

$$f^* = \frac{m}{s^2}$$

Derivation [p.113]: take the first derivative of the Gaussian growth rate with respect to leverage $f$ and set it to zero, $dg/df = m - s^2 f = 0$; solving gives the optimal Kelly leverage $f^* = m/s^2$.

**Kelly Formula — multi-strategy (matrix form, Thorp 1997)** [p.96]

$$F^* = C^{-1} M$$

Onde $F^*$ é vetor coluna de alocações ótimas $(f_1^*, \ldots, f_n^*)^T$, $C$ é matriz de covariância dos retornos ($C_{ij}$ = cov($R_i, R_j$)), e $M = (m_1, \ldots, m_n)^T$ é vetor de mean excess returns [p.96]. Retornos são one-period, simple (uncompounded), UNLEVERED [p.96-97]. Se estratégias independentes, $C$ é diagonal e $f_i = m_i / s_i^2$ [p.97].

**Maximum Compounded Growth Rate (Kelly-optimal portfolio)** [p.98, p.102]

$$g(F^*) = r + \frac{F^{*T} C F^*}{2} = r + \frac{S^2}{2}$$

Onde $S = \sqrt{F^{*T} C F^*}$ é o Sharpe ratio do portfolio Kelly-ótimo [p.98, p.102]. **Esta fórmula é central**: long-term growth é proporcional a **Sharpe ratio ao quadrado**, não ao retorno médio [p.154].

**Leverage restriction sob Regulation T** [p.98]

$$f_i^{restricted} = f_i \cdot \frac{l}{|f_1| + |f_2| + \cdots + |f_n|}$$

Onde $l$ = 2 (overnight) ou 4 (intraday) [p.98].

**APT / Factor Model** [p.133-134]

$$R = Xb + u$$

Onde $R$ é vetor N×1 de excess returns, $X$ é matriz de factor exposures (loadings), $b$ é vetor de factor returns, e $u$ é vetor de specific returns (assumido uncorrelated cross-stocks) [p.133-134].

**Ornstein-Uhlenbeck — mean reversion half-life** [p.140-141]

$$dz(t) = -\theta(z(t) - \mu) dt + dW$$

Half-life:

$$\text{half-life} = \frac{\ln(2)}{\theta}$$

Estimar $\theta$ via regressão linear de $dz$ contra $(z - \bar{z})$ [p.141]. No exemplo GLD-GDX: half-life ≈ 10 dias [p.141-142].

**Split/dividend adjustment multiplier** [p.37]

Para split N-to-1 com ex-date T: multiplicar preços pré-T por $1/N$.
Para dividendo $d$ com ex-date T:

$$\text{multiplier} = \frac{Close(T-1) - d}{Close(T-1)}$$

Aplicar multiplicador a todos os preços anteriores a T (não subtrair $d$, para preservar returns) [p.37].

**Position sizing por market cap — fourth root rule** [p.88]

Chan recomenda scaling de capital por stock proporcional a $\text{MarketCap}^{1/4}$ para manter ratio max/min de weights abaixo de ~10 e preservar benefício de diversificação [p.88].

## 4. Algoritmos e Pseudocódigo

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

## 5. Regras de Trading Explícitas

- **REGRA [p.43]**: Rejeitar estratégia stand-alone com Sharpe ratio < 1. Sharpe ≥ 2 é piso realista para profit-center.
- **REGRA [p.53, p.74]**: Nunca usar mais de **5 parâmetros** em um modelo (incluindo entry/exit thresholds, holding period, lookback). Rule-of-thumb: precisa de ≥ 252 × (n_parâmetros) data points.
- **REGRA [p.53]**: Dividir dados em training set e test set, roughly equal (ou mínimo 1/3 test set). Test set é SAGRADO — NÃO ajustar parâmetros nele [p.60].
- **REGRA [p.98, p.105]**: Usar **half-Kelly** por default (ou menos) devido a fat tails e erro de estimação em $m, s$. Full Kelly é frágil.
- **REGRA [p.105-106]**: Leverage final = min(half-Kelly, max_tolerable_drawdown / worst_historical_one-period_loss).
- **REGRA [p.103]**: Rebalancear posições conforme Kelly pelo menos uma vez ao fim de cada trading day. Após perda, reduzir position size; após ganho, aumentar.
- **REGRA [p.103]**: Lookback para estimar $M$ e $C$ do Kelly é ~6 meses para estratégias com holding de 1 dia.
- **REGRA [p.87]**: Ordem individual não deve exceder **1% do average daily volume** do ativo (reduz market impact).
- **REGRA [p.87]**: Evitar stocks com preço < $5 (comissão em % aumenta, bid-ask spread percentual aumenta).
- **REGRA [p.88]**: Escalar capital por stock proporcional a $\text{MarketCap}^{1/4}$, não linearmente (preserva diversificação).
- **REGRA [p.51, p.74]**: Sempre usar **dados laggados** (close do dia anterior) para gerar sinais, a menos que a estratégia entre exatamente no close.
- **REGRA [p.142-143]**: Stop loss é apropriado para momentum strategies (regime trending). Stop loss é **prejudicial** para mean-reversion strategies — em mean-reverting, você exita no pior momento.
- **REGRA [p.143]**: Para mean-reversion, exit via (a) mean target price ($\mu$ do OU), (b) half-life de $\ln(2)/\theta$, ou (c) oposição do novo entry signal.
- **REGRA [p.97]**: Returns para input no Kelly devem ser **one-period, simple (uncompounded), unlevered**.
- **REGRA [p.43-44]**: Para portfolios dollar-neutral e estratégias long-only sem overnight, NÃO subtrair risk-free rate no cálculo do Sharpe (financing cost é ~zero).
- **NUNCA [p.106]**: Confiar em stop loss para prevenir catástrofes — em gap events os fills acontecem muito abaixo do stop, realizando a perda em vez de evitá-la.
- **NUNCA [p.103]**: Deixar de recalcular $F^*$ diariamente após mudanças de equity; Kelly não é set-and-forget.
- **NUNCA [p.52]**: Otimizar parâmetros no test set após já ter calibrado no training set. Isso transforma test set em training set e reintroduz data-snooping bias.
- **NUNCA [p.110]**: Modificar estratégia imediatamente após uma grande perda ("representativeness bias"). Sempre backtestar a modificação em período longo.

## 6. Pitfalls e Anti-patterns

- **[p.14, p.24, p.40-42] Survivorship bias**: backtest em database sem stocks delistadas infla artificialmente estratégias "buy cheap" / "buy losers". Exemplo numérico de Chan: portfolio selecionado em 2001 retornou **-42% real** vs **+388% fictício** quando delisted stocks foram omitidas [Example 3.3, p.41-42].
- **[p.51] Look-ahead bias**: usar "day's high" ou regressão ajustada no dataset inteiro para gerar sinais dentro do período. Mais fácil de detectar em Excel (WYSIWYG) que em MATLAB/Python. Chan recomenda truncation test (ver Algoritmo em seção 4).
- **[p.25, p.52-53] Data-snooping bias**: qualquer modelo com > ~5 parâmetros sobre < 5 anos de daily data vai fitar ruído. AI/neural networks com "many parameters" **falharam consistentemente** na experiência direta de Chan [sidebar p.26-27].
- **[p.45] Transaction cost underestimation**: estratégia Bollinger-band em ES com Sharpe = 3 sem custos vira Sharpe = **-3** com apenas 1 bp de custo por trade [p.45].
- **[p.42] Dados high/low ruidosos**: preços high/low intraday têm muito mais ruído que open/close; backtests que assumem fills em limit prices abaixo da high do dia são superotimistas [p.42].
- **[p.25, p.104] Regime shifts**: dados de > 10 anos atrás podem ser inúteis devido a mudanças estruturais (decimalização 2003, revogação do uptick rule 2007, subprime). Séries financeiras são **não-estacionárias** [p.25].
- **[p.111-112] Overleveraging após sucesso inicial** (greed): Chan confessa ter perdido $1M+ adicionando $100M a estratégia com apenas 6 meses de track record. "It is a hitherto superbly performing model that is at the greatest risk of huge loss due to overconfidence and overleverage".
- **[p.106, p.143] Stop loss em regime mean-reverting**: "exiting at the worst possible time".
- **[p.108-109] Status quo bias / endowment effect**: segurar perdedoras por muito tempo mesmo sem justificativa mean-reverting; exitar vencedoras cedo demais por loss aversion.
- **[p.109] Representativeness bias**: alterar parâmetros imediatamente após grande perda. "No system can avoid all the market vagaries that can result in losses".
- **[p.110] Despair (drawdown prolongado) + greed (after big wins)** → overleveraging em ambas direções. Long-Term Capital Management 2000 e Amaranth Advisors 2006 são casos-texto [p.110].
- **[p.123-126] AI / machine learning overfit**: Alphacet Discovery com perceptron rendeu 37.93% backtest de 6 meses em GS — Chan alerta que período curto e múltiplos modelos tentados ainda carregam data-snooping, mesmo em framework com moving window.
- **[p.139] Factor models com fatores fundamentais**: assumem que "investors persist in using the same metric to value companies" — drawdown severo quando valuation regime muda (ex: growth-vs-value em 2007).
- **[p.88] Scaling linear por market cap**: produz weight ratio > 10000×, destruindo diversificação. Use fourth-root scaling.

## 7. Parâmetros Sensíveis

- **Kelly leverage $f^* = m/s^2$** [p.98, p.105]: Chan recomenda **metade** do valor (half-Kelly) em produção. Justificativa econômica: fat tails + erro de estimação. NÃO é curve-fit.
- **Kelly lookback para estimar $m, s$** [p.103]: ~6 meses para holding de 1 dia. Justificativa: balance entre responsividade a regime shifts e estabilidade estatística. Parâmetro com baixa sensibilidade — não otimizar no backtest.
- **Máximo de 5 parâmetros por modelo** [p.53]: rule-of-thumb de Chan baseado em experiência, não em teoria formal. Relação com sample size: 252 × n_params.
- **Half-life de mean reversion = $\ln(2)/\theta$** [p.141]: parâmetro *derivado* do OU, não otimizado. Robusto porque usa toda a série, não apenas os trades.
- **Thresholds de entry/exit em pair trading (GLD/GDX)** [p.58-59]: Chan testou ±2 std entry / ±1 std exit → Sharpe train 2.3, test 1.5; e ±1 std entry / ±0.5 std exit → Sharpe train 2.9, test 2.1. Sensibilidade moderada — valores equivalentes economicamente funcionam.
- **Lookback=252 dias, numFactors=5, topN=50 no PCA factor model** [p.137]: parâmetros arbitrários por Chan; ele admite que backtest é negativo, sugerindo que a estrutura do modelo está errada, não os parâmetros.
- **Transaction cost assumption de 5 bps por trade (one-way)** [p.45, p.63]: padrão institucional para S&P 500. ES (E-mini S&P 500 futures): ~1 bp [p.45]. Justificado economicamente pela média bid-ask spread + commission.
- **Risk-free rate 4% a.a.** [p.45]: refletia 3-month T-bill yield em 2008. Não otimizado.
- **Regras de bolso Sharpe vs holding frequency** [p.43]: Sharpe ≥ 2 = quase todo mês lucrativo; Sharpe ≥ 3 = quase todo dia. Derivado do law of large numbers, não curve-fit.

## 8. Citações Literais Importantes

> "As Einstein said: 'Make everything as simple as possible.' But not simpler." — [p.3]

> "Finance is famously nonstationary... it is possible to incorporate such regime shifts into a sophisticated 'super'-model, but it is much simpler if we just demand that our model deliver good performance on recent data." — [p.25]

> "The take-away lesson here is that risk always decreases long-term growth rate—hence the importance of risk management!" — [p.98]

> "It is a hitherto superbly performing model that is at the greatest risk of huge loss due to overconfidence and overleverage." — [p.111-112]

> "When a catastrophic event occurs, securities prices will drop discontinuously, so the stop loss orders to exit the positions will only be filled at prices much worse than those before the event. So, by exiting the positions, we are actually realizing the catastrophic loss and not avoiding it." — [p.106]

> "With many parameters, we can for sure capture small patterns that no human can see. But do these patterns persist? Or are they random noises that will never replay again?" — [p.26]

> "The ultimate risk management mind-set is very simple: Do not succumb to either despair or greed." — [p.112]

## 9. Conexões com Outros Livros Desta Base

- **Kelly formula & leverage-space** [p.96-98]: `leverage_space.md` (Vince) explora o mesmo terreno com mais profundidade matemática; Chan usa a versão Gaussian contínua (Thorp 1997), Vince usa Kelly discreto e TWR. A recomendação "half-Kelly" de Chan é consistente com o aviso de Vince sobre sensibilidade do optimal f.
- **Parcimônia de parâmetros (≤5)** [p.53]: mesma conclusão em `systematic_trading.md` (Carver, ~3-4 params) e `evidence_based_ta.md` (Aronson, multiple-testing penalty). Convergência independente.
- **Survivorship bias e data-snooping** [p.40-42, p.52-53]: `advances_fin_ml.md` (López de Prado) formaliza o problema com CPCV e DSR (Deflated Sharpe Ratio); Chan é menos rigoroso mas chega às mesmas advertências práticas.
- **Mean-reversion, cointegration, Ornstein-Uhlenbeck** [p.126-142]: `time_series_hamilton.md` trata ADF/cointegration formalmente. Chan usa CADF via spatial-econometrics toolbox [p.128-129] como aplicação prática.
- **Regime detection** [p.119-126]: `regime_change.md` e `ml_for_asset_managers.md` cobrem HMM / structural breaks — Chan é cético sobre Markov regime-switching ("useless for actual trading purposes because of constant transition probabilities", [p.121]) mas aberto a data-mining de turning points.
- **Momentum strategies** [p.116-119]: `stocks_on_the_move.md` (Clenow) é uma implementação específica de momentum cross-sectional que cabe na classe descrita por Chan.
- **Trilogia Chan** [capa]: este é o primeiro livro. `algo_trading_chan.md` (2013) e `machine_trading.md` (2017) ainda não processados — serão adicionados em passes subsequentes para expansão de cross-refs.
