# Trading Evolved — Anyone can Build Killer Trading Strategies in Python

> **Convenção de páginas**: este summary cita usando os números dos marcadores `[PAGE N]` do texto extraído (PDF 1-indexed), que é a única numeração confiável visível no `_full.txt` — o livro não imprime números de página em texto plano. O validador `check_citations.py` aplica offset automaticamente se detectar.

## Metadata
- **Autor:** Andreas F. Clenow [p.3]
- **Ano:** 2019 [p.3]
- **Editora:** Self-published / Equilateral Capital Management GmbH, Zurich [p.3]
- **Páginas:** 467 (PDF)
- **ISBN:** 9781091983786 [p.4]
- **Foco principal:** Ensinar construção, backtesting e análise de estratégias quantitativas de trading em Python (Zipline + PyFolio), com modelos reais para ETFs, equities (momentum) e futures (trend, counter-trend, curve, time-return).

## 1. Tese Central

Systematic trading é o uso de computadores para modelar, testar e implementar regras matemáticas de trading. O objetivo do livro é tornar backtesting quantitativo acessível a qualquer pessoa com conhecimento moderado, usando Python (Zipline, Pandas, PyFolio) como ferramenta, e demonstrando modelos de trading reais (não "sistemas mágicos") como veículo pedagógico. A abordagem científica exige formular hipóteses, testar com mentalidade skeptical (default: rejeitar), e priorizar **simplicidade** sobre complexidade curve-fitted [p.21-23, p.27-30]. A mensagem central é que os modelos mostrados "are teaching tools, not production grade models" — o leitor deve replicar, entender, modificar e só então fazer seu próprio modelo [p.15, p.312, p.349].

## 2. Conceitos-Chave

- **Systematic trading** — uso de computadores para modelar, testar e implementar regras matemáticas de trading; remove o componente emocional e permite validação de ideias [p.21, p.24].
- **Model Purpose / "raison d'être"** — todo modelo precisa ter um propósito específico (fenômeno de mercado que explora), não apenas "make money"; modelos sem propósito são "accidental models" — overfit quase certo [p.27-28].
- **Accidental model** — modelo criado testando indicadores até achar retorno positivo; backtest parece bom mas não tem predictive value [p.27-28].
- **Financial Risk** — definido como "potential value variation per unit of time" — volatilidade por tempo, não "quanto perco se meu stop bater" [p.37].
- **Mark-to-Market** — valoração de posição/portfólio sempre pelo preço corrente de mercado; "playing with the house's money" é fallacy [p.39-40].
- **Risk per Trade (fallacy)** — ideia retail de que risco = distância até stop × posição; Clenow rejeita: duas carteiras com mesmo "risk per trade" podem ter risco real 2× diferente se tamanhos notional diferem [p.42-43].
- **Sharpe Ratio** — (retorno anualizado − risk-free) / desvio-padrão anualizado; valores >1 são raros; estratégias com Sharpe 3-5 geralmente têm "negative skew" (pequenas vitórias, raro loss catastrófico) [p.45-46].
- **Investment Universe** — conjunto de markets elegíveis; seleção é crítica e fonte principal de survivorship bias em equities [p.32-33, p.192].
- **Survivorship bias** — usar constituintes atuais de um índice para simular o passado; solução: usar composição histórica do índice (joiners/leavers) [p.192, p.197-198].
- **Rebalancing** — ajustes de tamanho de posição para manter risk level alvo conforme volatilidade/portfolio mudam; não é mudança de opinião, é manutenção [p.35-36].
- **Momentum (Clenow score)** — slope de regressão exponencial anualizado × R² (coeficiente de determinação); punir ações voláteis/jumpy [p.200, p.203-205].
- **Volatility Parity / Inverse Volatility sizing** — alocar posições tal que cada uma contribua risco aproximadamente igual; mais voláteis = peso menor [p.206-207, p.293].
- **Trend filter (index-level SMA)** — ex: proibir long quando S&P 500 < SMA(200); criticado como potencial curve-fitting se usado para "explicar" 2008/2020 [p.211-212].
- **Trailing stop baseado em std-dev** — exit quando position cai N × std_dev do pico; normaliza cross-market [p.267-268].
- **ETF (good/bad/worst)** — good: passive low-cost trackers (SPY); bad: commodity ETNs (term-structure drag, counterparty risk); worst: leveraged/inverse (daily rebalance → volatility decay) [p.166-178].
- **Contango / Backwardation** — term structure em contango tem viés bearish embutido; backwardation tem viés bullish [p.327-329].
- **Carry / Cost of Carry** — diferença de preço entre contratos, anualizada; pode ser única fonte de sinal para "curve trading" [p.326, p.329].
- **Continuation** — série contínua sintética de futures, stitched por rolls; usada só para cálculo de sinais, não para trading [p.270, p.294].
- **Point Value (big point value)** — multiplicador que converte movimento de preço em $ P&L por contrato [p.237-238].
- **Random portfolio benchmark ("Mr. Bubbles")** — seleção aleatória de 50 ações do S&P 500, rebalanceada mensalmente, tende a bater o índice em longo prazo — o índice é um sistema sistemático ruim, não um "average" [p.370-372].

## 3. Fórmulas / Equações

**Momentum Score (Clenow)** [p.200, p.204-205]

$$\text{momentum\_score} = \left[\left(e^{\text{slope}}\right)^{252} - 1\right] \times 100 \times R^2$$

- $\text{slope}$ = coeficiente angular da regressão linear sobre $\ln(\text{preço})$ vs. tempo
- $R^2$ = coeficiente de determinação da mesma regressão (0 a 1)
- 252 = dias úteis/ano (anualização)
- Uso: ranking de ações para portfólio momentum; punição embutida para voláteis (R² baixo)
- Janela padrão usada no livro: 125 dias [p.209]
- Threshold mínimo usado: 40 [p.211]

**Sharpe Ratio** [p.45-46]

$$SR = \frac{R_{\text{ann}} - R_f}{\sigma_{\text{ann}}}$$

- $R_{\text{ann}}$ = retorno anualizado da estratégia
- $R_f$ = risk-free rate (Clenow recomenda yields diários de treasuries curtos; retail pode usar 0 para comparar estratégias entre si) [p.46]
- $\sigma_{\text{ann}}$ = desvio-padrão anualizado dos retornos
- Sharpe > 1 é raro; 0.7-0.8 pode ser "highly successful"; Sharpe 3-5 geralmente = negative skew perigoso [p.46]

**Position Size (Volatility Parity Futures)** [p.263]

$$\text{contracts} = \frac{\text{portfolio\_value} \times \text{risk\_factor}}{\sigma_{\text{price}} \times \text{point\_value}}$$

- $\text{risk\_factor}$ = basis points alvo de variação diária por posição (ex: 0.002 = 20 bps = 0.2% daily impact alvo) [p.263]
- $\sigma_{\text{price}}$ = 40-day std-dev das diferenças diárias de preço (price changes, não returns) [p.262]
- $\text{point\_value}$ = big point value do contrato
- Resultado arredondado para baixo (int)

**Volatility / Std-Dev de Price Changes (40 dias)** [p.262-263]

```python
std_dev = df.close.diff()[-40:].std()
```

**Volatility para Equities (pct change)** [p.208]

```python
def volatility(ts):
    return ts.pct_change().rolling(vola_window).std().iloc[-1]
```

- `vola_window` = 20 dias no modelo Momentum [p.214]

**Pullback normalizado (Counter-Trend)** [p.314-315]

$$\text{pullback} = \frac{\text{close}_t - \max(\text{close}_{t-20:t})}{\sigma_{40d}}$$

- Entry long se $\text{pullback} < -3$ (i.e., 3 std-dev abaixo do high de 20d) em regime de bull market [p.314-315, p.321]

**Cost of Carry (Curve Trading)** [p.329-330]

$$\text{annualized\_carry} = \left(\frac{P_{\text{near}}}{P_{\text{far}}}\right)^{365/\Delta\text{days}} - 1$$

- Exemplo do livro: SH9 a 907.50, SK9 a 921.50, expiry 61 dias depois → perda implícita 1.52% em 61d = −8.75% annualized (contango) [p.329]
- Usado como único input para seleção de trades no modelo "Trading the Curve" [p.326]

**Trend Filter (Dual EMA)** [p.264-265]

- Bull: $\text{EMA}_{40} > \text{EMA}_{80}$
- Bear: $\text{EMA}_{40} < \text{EMA}_{80}$
- Usado no Core Trend Model e no Counter-Trend [p.265, p.312]

## 4. Algoritmos e Pseudocódigo

**Momentum Model (Equity, S&P 500 membership)** [p.197-198, p.222-226]

```
Params: momentum_window=125, minimum_momentum=40, portfolio_size=30, vola_window=20

At each month_start:
    today = current_date
    universe = S&P 500 constituents on `today` (from historical index membership CSV)
    hist = close prices (momentum_window bars) for universe
    ranking = sort_desc(momentum_score(hist[ticker]) for ticker in universe)

    # Sell logic
    for pos in open_positions:
        if pos.ticker not in universe: sell(pos)            # left the index
        elif ranking[pos.ticker] < minimum_momentum: sell(pos)  # momentum decayed

    # Buy logic
    needed = portfolio_size - len(kept_positions)
    buy_list = top(ranking, needed) excluding kept_positions
    new_portfolio = buy_list + kept_positions

    # Inverse-volatility sizing
    vola = volatility(hist[new_portfolio])
    weights = (1/vola) / sum(1/vola)
    for sec in new_portfolio:
        if sec not in kept AND ranking[sec] < minimum_momentum: skip  # cash
        else: order_target_percent(sec, weights[sec])
```

**Core Trend Model (Futures)** [p.258-268]

```
Params: fast_ma=40 (EMA), slow_ma=80 (EMA), breakout=50 (days),
        stop_mult=3 (std-devs), vola_window=40 (days), risk_factor=0.002

Daily:
    for market in universe (~40 US futures):
        std = std(close.diff()[-40:])
        trend_positive = EMA(close, 40) > EMA(close, 80)
        if no position:
            if trend_positive AND close == max(close[-50:]):
                open long, size = (portfolio_value * risk_factor) / (std * point_value)
            elif not trend_positive AND close == min(close[-50:]):
                open short, size symmetric
        else:
            if long AND close <= peak_close - 3*std: close
            if short AND close >= trough_close + 3*std: close
    # Roll logic: if held contract < 5 days to auto_close, roll to most-liquid
```

**Counter-Trend (Futures, mean reversion in bull)** [p.314-315, p.320-321]

```
Params: fast_ma=40, slow_ma=80, high_window=20, dip_buy=-3, days_to_hold=20

Daily per market:
    trend = EMA(close, 40) > EMA(close, 80)
    std = std(close.diff()[-40:])

    if position_open:
        bars_held += 1
        if bars_held >= 20: exit
        elif not trend: exit

    elif trend:
        pullback = (close[-1] - max(close[-20:])) / std
        if pullback < -3:
            open long, size = (pv * 0.0015) / (std * point_value)
```

**Time Return Trend Model** [p.294]

```
Monthly only, per market (continuation):
    if close > close[-252]: signal = long
    elif close < close[-252]: signal = short
    # Also check 126-day (half year) return for agreement
    size by inverse volatility (40-day std)
    no stops, hold until signal flips next month
```

**Curve Trading (Carry Futures)** [p.326-330]

```
No historical data needed. Each rebalance:
    for each commodity future with liquid curve:
        for each contract n, n+1 in chain:
            carry[n] = (P[n] / P[n+1])^(365/days_between) - 1
    rank markets by carry
    long top-carry contracts (out on curve, not front)
    short bottom-carry (deepest contango)
```

**Asset Allocation Model (ETF)** [p.183-185]

```
Fixed weights, monthly rebalance:
  SPY: 0.25, TLT: 0.30, IEF: 0.30, GLD: 0.075, DBC: 0.075

At month_start:
    for sec, target_weight in securities.items():
        if data.can_trade(sec):
            order_target_percent(sec, target_weight)
```

**Survivorship-bias-free universe (pragmatic)** [p.217-219]

```
# CSV with columns: date, comma_separated_tickers
# One row per day the index composition changed
index_members = pd.read_csv('sp500.csv', index_col=0, parse_dates=[0])

def universe_on(today):
    all_prior = index_members.loc[index_members.index < today]
    latest_row = all_prior.iloc[-1, 0]  # last-known composition
    return latest_row.split(',')
```

## 5. Regras de Trading Explícitas

- **REGRA [p.21-22]**: Antes de ir sistemático, **formule sua hipótese em regras firmes e testáveis**; se não consegue, é porque a ideia não era um modelo completo.
- **REGRA [p.23]**: Abordagem default ao backtest é **skeptical** — procure razões para **rejeitar** a regra, não para aceitá-la (confirmação bias é inevitável se você buscar validação).
- **REGRA [p.27-28]**: Todo modelo deve ter um **purpose específico** (fenômeno de mercado + perfil de retorno alvo); "make money" não é purpose.
- **REGRA [p.29]**: Use **quantas menos regras e variações possível**. Complexidade precisa justificar economicamente sua existência — não basta melhorar o backtest.
- **REGRA [p.30]**: Toda regra adicionada precisa ter **explicação real de mercado**, não só melhora de métrica histórica.
- **REGRA [p.32]**: Use parte da série temporal para fitting e parte para testing (out-of-sample). Nunca teste no mesmo dado que ajustou.
- **REGRA [p.33]**: Prefira **portfolios** (múltiplos markets) a single-market strategies; single-market = diversification zero.
- **REGRA [p.192, p.198]**: Para equities, **use historical index membership** (não constituintes atuais) para evitar survivorship bias.
- **REGRA [p.193-194]**: Ao lidar com equities, **corrija por dividendos** (total return series ou cash dividend accounting); ignorar = distorção substancial multi-ano.
- **REGRA [p.207]**: Use **volatility-parity position sizing** (inverse-volatility weighting) para dar "equal vote" a cada posição.
- **REGRA [p.197]**: **Momentum model S&P 500** — trade apenas mensalmente, top 30 ações por momentum score (janela 125d), compre se momentum > 40, inverse-vol weighting, volatility 20d std-dev de retornos.
- **REGRA [p.261]**: Modelos de futures devem **checar diariamente** sinais de entrada/saída E rolls; trades executam no dia seguinte ao sinal (close).
- **REGRA [p.263]**: Para futures, dimensione para cada posição impactar ~0.2% daily var do portfolio (risk_factor = 20 bps) como benchmark inicial.
- **REGRA [p.267-268]**: Trailing stop para trend em futures = 3× std-dev de price changes (40d) do peak reading da posição. Implica giveback ~0.6% do portfolio por posição.
- **REGRA [p.314-315]**: Counter-trend em bull — entrar long se EMA40>EMA80 E pullback < −3 std-dev do máximo 20d; exit em 20 dias OU reversão de trend.
- **REGRA [p.349-352]**: **Combine múltiplos modelos descorrelacionados** como portfolio components — exemplo do livro: 5 modelos equi-ponderados produziram Sharpe 1.24 vs. melhor individual 0.84, drawdown −17% vs. −25% a −40% individuais.
- **NUNCA [p.30]**: Rode um optimizer para encontrar "melhores" parâmetros; use **variações razoáveis** para testar estabilidade, não optimal values.
- **NUNCA [p.41-42]**: Use pyramiding ("playing with house's money"); viola mark-to-market e é baseado em gambling fallacy.
- **NUNCA [p.43]**: Defina risco como "risk per trade" baseado em distância de stop; isso ignora o fato de que risco é variação potencial por unidade de tempo.
- **NUNCA [p.44]**: Mire triple-digit yearly returns — matematicamente inviável em longo prazo ("probability of ruin approaches 1").
- **NUNCA [p.176]**: Mantenha leveraged/inverse ETFs além de um dia — rebalance diário cria volatility decay, perda mesmo em mercado lateral ou bear.
- **NUNCA [p.26]**: Deixe um algo trading unsupervised; mesmo automatizado precisa de monitoramento constante.
- **NUNCA [p.179-180]**: Assuma que pode shortar ETFs pequenos em backtest — liquidez de borrow é limitada e shares podem ser recalled no pior momento.

## 6. Pitfalls e Anti-patterns

- [p.27-28] **Accidental models** — combinar indicadores aleatoriamente e tunar até o backtest ficar bonito. Não tem predictive value; modelo sem "raison d'être" é curve fit quase garantido.
- [p.30] **Optimização de múltiplos parâmetros** → "optimizers will tell you what the perfect parameters WAS for the past" — sem valor preditivo.
- [p.31] **Filters ad-hoc para evitar anos ruins** (ex: "filter que evita 2008") — parece melhorar backtest mas é overfit; se o modelo tivesse sido desenvolvido antes, tal filter não existiria.
- [p.41-42] **Position-size pyramiding** — aumentar posição após ganho; "past trades lack magical ability to impact the future", é gambling fallacy.
- [p.43] **"Risk per trade" baseado em stop distance** — definição errada de risco; duas carteiras com mesmo "risk per trade" podem ter risk real muito diferente.
- [p.44-45] **Mirar triple-digit returns** — matematicamente impossível em longo prazo; expectativa realista = <15% p.a. de traders skilled.
- [p.175-176] **Leveraged/Inverse ETFs held >1 day** — daily rebalance causa volatility decay; mesmo em bear market de underlying, inverse ETF pode perder.
- [p.179-180] **Assumir que short em ETFs é grátis** no backtester — locate, funding rate e recall risk destroem o edge em practice.
- [p.192] **Usar constituintes atuais do índice** para simular o passado — survivorship bias massivo (você escolheria Enron e Lehman 10 anos atrás? Mas escolhe Apple porque sabe que subiu).
- [p.193] **Ignorar dividendos** em equity backtests — impacto significativo multi-ano.
- [p.211-212] **Trend filter baseado em SMA longa (ex: 200d)** — pode ser **severe curve fitting** pelo conhecimento retrospectivo de 2008; "we already know from experience that using such a long term trend filter will greatly mitigate damage from the two major bear markets of our generation. The question is of course if that has any predictive value in terms of avoiding the next" [p.212].
- [p.257] **Inability to explain a strategy simply** — red flag: "if you are unable to explain the idea behind your trading strategy in a simple, brief and understandable manner, then there is a clear risk that you have overcomplicated and over fitted rules".
- [p.26] **Automação sem supervisão** — "computers are only as smart as the person programming it, and usually not even that smart".
- [p.259-260] **Faking capital with futures** (tradar um portfolio de $100k como se fosse $1M usando margem) — 10% drawdown te varre.
- [p.349-350] **Comparar modelos apenas por retorno anual** — ignora drawdown, Sharpe, correlação com portfolio existente; "a model with low expected return but low/negative correlation can greatly help overall portfolio".
- [p.370-372] **Comparar sua estratégia só contra o S&P 500** — uma seleção aleatória ("chimp with darts") de 50 ações bate o índice em longo prazo. "The index is a completely different systematic trading strategy. And a poorly designed one at that" [p.371].
- [p.369] **Investir em mutual funds ativos** — ~80% falham em bater benchmark em qualquer período 3-5 anos (SPIVA reports).
- [p.168] **Usar ETNs como ETFs** — ETN = dívida estruturada, counterparty risk; se o emissor quebra, cash é perdido (lembre 2008).
- [p.321] **Expected: desenho simétrico long/short** — "bullish trends and bearish trends tend to behave quite differently and may require different parameter sets"; simetria é simplificação, não feature.

## 7. Parâmetros Sensíveis

- **Momentum window = 125 dias** [p.209, p.214] — "meant to roughly represent half a year". Clenow admite explicitamente: "I deliberately chose middle of the road kind of settings. I pick them more or less at random, from a set of reasonable values" [p.210]. NÃO é otimizado.
- **Minimum momentum = 40** [p.211] — threshold arbitrário. Clenow: "This fairly arbitrary number, is to ensure that we are not buying flat or negative stocks". Nota: depende da janela — janelas mais curtas produzem scores mais extremos, então o threshold precisa escalar [p.211].
- **Portfolio size = 30 stocks** [p.210] — justificativa econômica: "10 stocks = too high single-stock risk; too many = quality suffers and monitoring overhead". Não é otimizado para backtest.
- **Vola window = 20 dias** (equities) [p.214] — "reasonable", padrão industrial.
- **Vola window = 40 dias** (futures, std-dev de price changes) [p.262] — "roughly measures the past two months' volatility. Feel free to experiment".
- **Trend filter EMAs = 40/80 dias** [p.265] — "these numbers are reasonable, as are many others. Feel free to try other combinations". Clenow: escolheu por simetria de exposição, não por backtest best.
- **Breakout window = 50 dias** (Core Trend) [p.266] — arbitrário.
- **Stop = 3× std-dev** [p.267] — justificativa econômica: com risk_factor=0.2%, um stop 3σ perde ~0.6% do portfolio por posição, o que é "giveback acceptable".
- **Risk factor = 20 bps (0.002) daily** [p.263] — ajustador principal de risco; default "reasonable" que pode ser escalado conforme mandato.
- **Days to hold = 20** (Counter-Trend) [p.315] — "approximately one month"; Clenow admite é "wonky stop logic" em demo [p.321].
- **Dip buy = −3 std-dev** (Counter-Trend) [p.315] — simétrico ao stop do Trend para explicar a dinâmica; não otimizado.
- **S&P 500 index trend filter (200d)** [p.211-212] — Clenow explicitamente NÃO usa no modelo momentum do livro, suspeita de curve fit retrospectivo.
- **Commission = 0.1% por $** (equity) [p.215]; **$0.85/contract + $1.5 exchange fee** (futures) [p.268-269] — realistas para low-cost broker.
- **Slippage = VolumeShareSlippage, limit 2.5% do volume diário, impact 5%** (equity) [p.215]; **VolatilityVolumeShare limit 30%** (futures) [p.269].

## 8. Citações Literais Importantes

> "The point of my books, all of my books, is to make a seemingly complex subject accessible." — [p.13]

> "Your default way of thinking should be to find ways to reject the rules. To show that they fail to add value and should be discarded." — [p.23]

> "Complexity [is] something inherently bad, something which needs to justify its existence. Any complexity you want to add to your model needs to have a clear and meaningful benefit." — [p.29]

> "Optimizers will tell you what the perfect parameters was for the past. They will also con you into a false sense of security, and make you believe that they have any sort of predictive value. Which they don't." — [p.30-31]

> "Financial risk is about potential value variation per unit of time." — [p.37]

> "Anyone aiming at achieving triple digit yearly returns will, with mathematical certainty, lose all of their money if they remain at the table. In such a game, the longer you play, the more your probability of ruin approaches 1." — [p.45]

> "If you are unable to explain the idea behind your trading strategy in a simple, brief and understandable manner, then there is a clear risk that you have overcomplicated and over fitted rules to match data, and that there is little to no predictive value." — [p.257]

> "The index is a completely different systematic trading strategy. And a poorly designed one at that." — [p.371]

> "Never forget that the interesting money in this business is made from trading other people's money." — [p.355]

## 9. Conexões com Outros Livros Desta Base

- **Momentum model (equity, S&P 500)** é versão evoluída (com código Python + Zipline) do modelo de `stocks_on_the_move.md` — mesmo autor Clenow; Clenow explicitamente refere-se ao livro anterior [p.196, p.199]. Aqui a implementação é quantitativa com survivorship-bias handling via CSV de composição histórica do índice.
- **Core Trend Model (futures)** é reimplementação em Python do modelo apresentado em Clenow, *Following the Trend* (2013) [p.255-258]. Não há summary desse livro anterior na base.
- **Systematic_trading.md (Rob Carver)** é referenciado explicitamente como complemento teórico/profundo — "a deep dive into systematic trading, you should look at something like the aptly named Systematic Trading (Carver, 2015)" [p.18]; e Carver é co-autor de guest chapter 22 em *Trading Evolved* [p.385]. Conexão: Carver defende parcimônia e position sizing similar; convergência independente sobre risk budgeting e importância de skepticism contra optimization.
- **Volatility parity / inverse-volatility sizing** [p.206-207, p.263] também central em `systematic_trading.md` — mesmo conceito, notação similar.
- **Counter-trend / mean reversion em bull markets** [p.310-315] complementa a abordagem de `algo_trading_chan.md` e `machine_trading.md` (Ernest Chan) sobre mean-reversion; Clenow foca em futures diversificados, Chan em equity pairs.
- **Curve/carry trading** [p.326-330] trata um tópico ausente dos outros livros da base — seção 18 é aporte original.
- **Skepticism anti-optimização** [p.30-31, p.257] ecoa fortemente com `advances_fin_ml.md` (López de Prado — "backtest overfitting is the most pressing issue") e `evidence_based_ta.md` (Aronson — data-mining bias). Clenow chega à mesma conclusão sem framework estatístico formal, apenas princípio empírico.
- **ETF pitfalls (leveraged/inverse daily rebalance decay)** [p.172-176] é tratamento prático que complementa `volatility_trading.md` (Sinclair) sobre estruturação de produtos derivativos.
- **Random portfolio benchmark ("Mr. Bubbles")** [p.367-372] tem afinidade com a discussão de `evidence_based_ta.md` sobre significância estatística contra benchmarks passivos/random.
