# Trading and Exchanges: Market Microstructure for Practitioners

## Metadata
- **Autor:** Larry Harris (Fred V. Keenan Chair in Finance, Marshall School of Business, University of Southern California) [p.i]
- **Ano:** 2002 [p.i]
- **Editora:** Oxford University Press [p.i]
- **Páginas:** ~113 (PDF draft; livro publicado tem ~640 páginas) [metadata]
- **ISBN:** N/A — cópia usada é Draft: March 1, 2002 / March 5, 2002, pré-publicação [p.i]
- **Foco principal:** Microestrutura de mercado — quem negocia, como as regras de troca (rules) moldam liquidez, custos de transação, volatilidade e lucros, e por que certas estratégias ganham/perdem num jogo de soma-zero.

## 1. Tese Central

Mercados são problemas de busca bilateral: compradores buscam vendedores e vice-versa; a estrutura de mercado (trading rules, sistemas de informação) determina custos de busca, poder informacional entre tipos de traders e, consequentemente, liquidez, transparência de preços, volatilidade e lucros [ch.1, p.1-3; ch.19, p.75-76]. Harris enquadra trading como um **jogo de soma-zero** medido relativo à média de mercado: ganhos de um lado = perdas do outro; "informed traders can only profit to the extent that less informed traders are willing to lose to them" [p.4, Key Recurrent Themes, p.6]. A implicação prática dominante: uninformed traders perdem *porque* negociam — limitar trading é a única defesa racional [ch.14, p.59].

Os cinco objetivos do livro [p.1-2]: entender origens de (1) liquidez, (2) transaction costs, (3) preços informativos, (4) volatility, (5) trading profits — e como market structure afeta cada um.

## 2. Conceitos-Chave

- **Liquidity** — habilidade de negociar tamanho grande rapidamente a baixo custo quando se quer [p.75]. Resultado de busca bilateral com múltiplas dimensões: immediacy, depth, width, resiliency [ch.19, p.75-76].
- **Immediacy** — dimensão de liquidez: capacidade de negociar *agora*; o preço da immediacy é o bid/ask spread [p.27, p.59].
- **Bid/Ask Spread (inside spread / touch)** — diferença entre best ask e best bid; preço pago por impatient traders por immediacy [p.28, p.59].
- **BBO / NBBO** — Best Bid and Offer / National Best Bid and Offer (melhor preço nos EUA) [p.28].
- **Standing/Open orders** — ordens limitadas abertas que *oferecem* liquidez; market orders *tomam* liquidez [p.28].
- **Order-driven market** — usa order-precedence rules (price priority + time precedence ou public-order precedence) e trade-pricing rules para casar ordens [p.32].
- **Quote-driven (dealer) market** — dealers cotam bid/ask e negociam com clientes [p.29-30].
- **Price priority** — regra primária em oral auctions: traders com melhores preços têm precedência [p.33].
- **Time precedence** — regra secundária: quem *primeiro* melhora o preço fica com prioridade naquele nível [p.33]. Só é significativa se o tick não for muito pequeno [p.34].
- **Tick / minimum price increment** — menor incremento com que se pode melhorar preço; tick muito pequeno enfraquece time-precedence rule; tick muito grande desincentiva price improvement [p.34].
- **Fundamental value vs. market value** — valor intrínseco vs. preço de mercado; noise = diferença entre eles [p.46].
- **Random walk** — mudanças de preço em mercado eficiente são imprevisíveis porque refletem só informação nova [p.47, p.79].
- **Informed traders** — value traders, news traders, technical information-oriented traders, arbitrageurs; fazem preços informativos ao trade on fundamentals [p.46].
- **Order anticipators (parasitic)** — front-runners, sentiment-oriented technical traders, squeezers; lucram prevendo outras ordens, sem tornar preços mais informativos [p.49].
- **Bluffers / price manipulators** — tentam enganar outros por rumor ou wash trades ("paint the tape") para mover preços [p.52].
- **Momentum traders** — compram após alta, vendem após queda; especialmente vulneráveis a bluffs [p.54].
- **Dealers** — passive traders que vendem immediacy; ganham bid/ask spread; perdem para informed traders [ch.13, p.56-58].
- **Adverse selection spread component** — parcela do spread que compensa dealer por perdas a well-informed traders [p.61].
- **Transaction cost spread component (transitory)** — parcela do spread que cobre custos operacionais + lucro normal; causa bid/ask bounce [p.61].
- **Bid/ask bounce** — oscilação minor entre bid e ask conforme order flow alterna; volatilidade transitória [p.61].
- **Value traders** — "ultimate liquidity suppliers"; negociam quando preço diverge de fundamental value [ch.16, p.65-67].
- **Winner's curse** — ganhar um leilão e depois perceber que pagou demais / vendeu barato demais; risco central do value trader [p.65].
- **Arbitrageurs** — trade on relative values; hedge portfolio com legs long+short; lucram com price convergence [ch.17, p.68-70].
- **Basis / arbitrage spread / arbitrage bounds** — basis = diferença de preços entre legs; fair value = basis "correto"; arbitrage spread = basis − fair-value-basis; arbitrageurs trade quando basis sai dos bounds [p.70].
- **Block trade** — ordem grande demais para fillar em mecânica normal; tipicamente >¼ do volume médio diário (NYSE: ≥10.000 ações) [p.62].
- **Latent demand / responsive traders** — willing to trade if asked, sem ordens no book; block brokers os descobrem via telefone [p.63].
- **Fundamental volatility** — mudanças de preço por mudanças em valor fundamental (unpredictable in efficient markets) [p.78-79].
- **Transitory volatility** — volatilidade causada por trading de uninformed traders; reversível; regulators podem afetá-la [p.78, p.74 epilogue].
- **Implementation shortfall / transaction cost measurement** — diferença entre trade price e benchmark price, multiplicado pelo size + sign [p.83-84].
- **Explicit / Implicit / Missed-trade-opportunity costs** — três componentes de transaction cost [p.82].
- **Zero-sum game** — accounting gains de um lado = accounting losses do outro [p.6, p.1].
- **Order flow externality** — traders que postam limit orders dão opções gratuitas para outros; attracts and binds traders to markets because traders want free trading options [p.15].
- **Front running (legal vs. illegal)** — ilegal se quebra confidencialidade de brokerage; legal se inferido por observação pública [p.50-51].
- **Realized spread** — diff entre prices em que dealer *efetivamente* comprou e vendeu (pode ser menor ou negativo vs. quoted spread por adverse selection) [p.58].

## 3. Fórmulas / Equações

**Transaction cost estimado vs. benchmark price** [p.83-84]

Para uma compra:
$$\text{EstimatedCost} = \text{TradeSize} \times (\text{TradePrice} - \text{BenchmarkPrice})$$

Para uma venda:
$$\text{EstimatedCost} = \text{TradeSize} \times (\text{BenchmarkPrice} - \text{TradePrice})$$

Ou, de forma unificada usando TradeSign (+1 compra, −1 venda):
$$\text{EstimatedCost} = \text{TradeSize} \times \text{TradeSign} \times (\text{TradePrice} - \text{BenchmarkPrice})$$

- Soma dos custos estimados entre todas as partes de um trade = 0 (zero-sum) [p.83].
- Traders que *demandam* liquidez pagam cost > 0; traders que *oferecem* têm cost < 0 [p.83].

**Desired position proportional to mispricing** [p.48, box "An Algebraic Illustration"]

$$D_i = a \cdot (f_i - P)$$

- $f_i = V + e_i$ = forecast do trader $i$, com $e_i$ error term (mean 0, unbiased) [p.48]
- $V$ = fundamental value verdadeiro
- $P$ = market price
- $a$ = constant of proportionality
- Implicação: traders com forecast > price querem long; < price querem short. Agregação de forecasts pelo mercado produz preço mais preciso que qualquer forecast individual [p.48].

**Realized spread (exemplo narrativo, não fórmula rotulada)** [p.58]

$$\text{RealizedSpread} = \text{AvgSellPrice} - \text{AvgBuyPrice}$$

- No exemplo de Dell: quoted spread = 0.3; após adverse-selection downward move, roundtrip de 35.0 buy → 34.9 sell ⇒ realized = −0.1 [p.58].

**Unilateral search stopping rule** [p.76]

Continuar busca enquanto:
$$E[\text{benefit of next inquiry}] > E[\text{cost of next inquiry}]$$

- Exemplo numérico: benefit = (improvement provável) × (prob de achar melhor) = 10 × 0.25 = $2.50; custo = 5 min × ($30/hr) = $2.50 ⇒ stop [p.77].

N/A para modelos formais de Kyle/Glosten-Milgrom — Harris escolhe prosa com equação mínima ("I fully explain all essential concepts in the main text" [p.1-1]).

## 4. Algoritmos e Pseudocódigo

**Oral auction — fluxo de negociação em open outcry** [ch.6, p.32-34]

```
enquanto mercado aberto:
    trader grita bid/offer (open-outcry rule)  [p.32]
    se outro trader aceita:
        trade ocorre ao preço gritado
        buyer: "take it"; seller: "sold"        [p.32]
    regras de precedência:
        1) price priority (melhor preço vence)   [p.33]
        2) time precedence (primeiro a improve)  [p.33]
           — mantida repetindo o quote; "quote good only as long as the breath is warm" [p.33]
    para tomar precedência sem time, deve
      melhorar preço em >= tick (leapfrog)       [p.33-34]
```

**Bluff — long-side bluff scheme (Bill/BNB example)** [ch.12, p.52-54]

```
Fase 1 (accumulation, dias 1-40):
    usar limit orders para comprar devagar, deixando
    mercado vir; 200.000 shares @ avg 6.00       [p.52]

Fase 2 (promotion, dia 31+):
    postar em múltiplos fóruns com usernames
    diferentes; projeções otimistas baseadas em
    10-Q/10-K reais para aumentar credibilidade  [p.52]

Fase 3 (trigger):
    esperar catalyst (press release ambíguo)
    submeter market orders divididos em múltiplos
    brokers simultaneamente para causar price jump [p.53]

Fase 4 (distribution):
    vender devagar em alta; momentum traders
    are particularly susceptible to bluffs; momentum traders primarily buy stock from the bluffer [p.54]
```

— Harris descreve ambos finais: sucesso (momentum traders se iludem) e falha (value traders calam o bluff). Lição: uninformed momentum traders são as vítimas previsíveis.

**Value-trader liquidity provision loop** [ch.16, p.65-67]

```
para cada instrumento em watchlist:
    V_i = estimate_fundamental_value(instrument)  [p.65]
    P_i = current_market_price
    se |P_i - V_i| > outside_spread / 2:
        se P_i < V_i:   BUY  (uninformed selling pressure drove price down) [p.66]
        se P_i > V_i:   SELL
    mitigar:
        - adverse selection risk (news traders mais informados) [p.67]
        - winner's curse (value misestimated)                    [p.67]
    NÃO postar quotes (não dar free options à market)            [p.67]
```

**Order-submission decision (market vs. limit)** [ch.18, p.71-73]

```
INPUT: bid/ask spread s, urgency u, view_on_value v
if v == "no opinion":
    if s small:  use MARKET orders (cheap immediacy)         [p.72]
    if s large:  use LIMIT orders   (offer liquidity)         [p.72]
if v != "no opinion":
    comparar trade_price esperado vs. fundamental_value
    usar MARKET se pode fillar melhor que v
    caso contrário LIMIT
para LARGE orders:                                            [p.71]
    decidir: shop vs. hide; one broker vs. many; split over time
    risco exposure ⇒ front-runners e quote-matchers
```

## 5. Regras de Trading Explícitas

- **REGRA [p.59]**: Submeta market orders quando o bid/ask spread é *estreito* e limit orders quando é *largo* — a menos que você tenha opinião de valor (então inverta se o preço tiver corrido a seu favor) [p.72].
- **REGRA [p.59]**: Antes de decidir market vs. limit, confronte o spread atual com o spread *típico* do instrumento; só assim se sabe se immediacy está cara ou barata [p.59].
- **REGRA [p.72]**: Large traders devem decidir **antes** de exposure: shop vs. hide, single broker vs. múltiplos, split over time vs. all-at-once; display é a decisão crítica do buy-side [p.71].
- **REGRA [p.50]**: Brokers devem "shop the block" apenas com traders prováveis de pegar o outro lado; exposição ampla atrai front-runners [p.50-51].
- **REGRA [p.33]**: Para ganhar time-precedence em oral auction é preciso *ser o primeiro a improve* o best bid/offer em pelo menos um tick; enquanto você mantém o preço, ninguém pode tradear na sua frente naquele nível [p.33].
- **NUNCA [p.59]**: "Uninformed traders lose simply because they trade. If you are an uninformed trader and do not want to lose, you should minimize your trading." — a lição mais importante do livro, auto-declarada pelo autor [p.59].
- **NUNCA [p.52]**: Oferecer liquidez (limit orders, dealing) sem entender adverse selection — você estará dando opções de trading gratuitas a quem sabe mais que você [p.5, p.59].
- **NUNCA [p.54]**: Ser um momentum trader cego após um price jump com volume — você é alvo preferencial de bluffers e order anticipators [p.54].
- **REGRA [p.65]**: Value traders não devem revelar preços de reserva (outside spread) via cotação pública; isso vaza suas estimativas de valor [p.67].
- **REGRA [p.68]**: Arbitrageurs só devem colocar a operação quando o basis sair das *arbitrage bounds* (fair value ± custos de carry + margin of safety) [p.70].
- **REGRA [p.71]**: Se limit order não executa e o mercado se move contra você, prepare-se para pagar preços inferiores — traders que *precisam* fillar devem aceitar o risco via market orders ou limit prices próximos ao mercado [p.72-73].
- **REGRA [p.49]**: Em mercados com time precedence, order anticipators precisam melhorar preço em >= 1 tick para tradear à frente; portanto tick size determina rentabilidade de front-running [p.49].

## 6. Pitfalls e Anti-patterns

- [p.59] "Uninformed traders lose whether they submit limit or market orders. They lose simply because they trade" — o pior pitfall é achar que trading é de graça se você escolher o tipo de ordem certo.
- [p.46-48] Acreditar-se informed sem sê-lo: "most traders who believe that they are informed traders do not trade profitably because they are not truly well informed" [p.46]. Teste: você tem informação que outros não têm, *ou* você processa informação pública melhor que a média?
- [p.54] Momentum trading após catalysts com volume pode ser compra na cúspide de um bluff; "they are particularly susceptible to bluffs" [p.54].
- [p.49-51] Revelar ordens grandes a brokers desatentos → legal front-running por observadores experientes (Rifka vs. Jon example) [p.51].
- [p.67] Value traders que postam seu outside spread publicamente dão free options aos informed — seu outside spread deve ficar privado [p.67].
- [p.70] Arbitrage "livre de risco" não existe: há basis risk / residual risk mesmo após cancelamento de fatores comuns — specific factors afetam legs de forma diferente [p.70].
- [ch.22, p.85-87] Confundir skill com luck em performance evaluation; managers skilled podem ter retornos ruins em períodos adversos, e managers fracos podem parecer bons em bull markets [p.86-87]. "Failures to understand these issues probably account for more trading losses than any other mistakes traders make" [p.86].
- [p.86] Sample-selection bias ao avaliar track records pode distorcer expectativas — fund managers sobreviventes não são amostra representativa.
- [p.54-55] Ignorar que "timing is everything" mesmo com direção correta: "If they initially have no positions, and they sell short too soon, they initially will lose on their short positions. If they cannot finance their losses, their brokers will force them to buy to cover" [p.107].
- [p.65] Winner's curse: ganhar auction/trade *é informação negativa* — significa que sua avaliação foi a mais otimista (ou pessimista se short) do pool, aumentando probabilidade de erro [p.65, p.67].
- [p.59] Dealers que não ajustam spread para adverse selection vão à falência — ninguém consegue perder dinheiro para informed traders indefinidamente [p.61].
- [ch.11, p.49] Large traders que não dividem ordens ou não escondem exposure pagam o custo inteiro do price impact + uma taxa ao front-runner que os copia [p.49-50].
- [p.105-107] Bubbles: momentum traders + leveraged buyers + order anticipators aceleram desvios; quando crash ocorre, margin calls + stop-loss orders amplificam a queda [p.105-107].

## 7. Parâmetros Sensíveis

- **Tick size / minimum price increment** [p.34]: Harris justifica economicamente — tick muito pequeno enfraquece time precedence (reduz incentivo a improve preços); tick muito grande desincentiva price improvement por custo incremental. Não é curve-fit; é decisão de design de mercado com trade-off. "Exchanges and regulators pay close attention to it" [p.34].
- **Block-trade threshold (NYSE: 10.000 shares)** [p.62]: Harris critica o limiar fixo — "Block trading statistics would be more useful if block trades were classified by whether they exceed some fraction of average daily volume rather than by whether they exceed some fixed size" [p.63]. Sugestão: ≥¼ do ADV do papel.
- **Spread components (transaction-cost vs. adverse-selection)** [p.61]: estimação exige métodos econométricos (não especifica fórmula fechada no draft visto); valores dependem do regime de informação assimétrica.
- **Hedge ratios (arbitrage)** [p.70]: "Traders choose their hedge ratios to minimize the total risk of the portfolio" — Harris não prescreve método específico (OLS? regime-switching?), apenas diz que o numerator é o instrument com maior carga no common risk factor [p.70].
- **Arbitrage bounds** [p.70]: fair value ± custos de carry. Harris enfatiza que fair values "are not common knowledge" e precisam ser estimados [p.70] — parâmetro genuinamente proprietário, não otimizável em backtest genérico.
- **Limit-order limit price** [p.73]: decisão de onde colocar depende de "execution probability vs. execution price tradeoff". Harris aponta para econometric models vendidos por vendors, mas não dá fórmula [p.73].
- **Buy-side display decisions (whole vs. split, one broker vs. many)** [p.71]: parameter space enorme, depende de urgência, tamanho relativo ao ADV, e presença de parasitic traders. "Display decisions are the most important trading decisions that large buy side traders make" [p.71].

## 8. Citações Literais Importantes

> "The most important lesson you may learn from this book appears in this chapter. You will learn why uninformed traders lose to well-informed traders whether they submit limit orders or market orders. Uninformed traders lose simply because they trade. If you are an uninformed trader and do not want to lose, you should minimize your trading." — [p.59]

> "Trading is a zero-sum game when gains and losses are measured relative to the market average. In a zero-sum game, someone can win only if somebody else loses. On average, well-informed speculators and bluffers win, and poorly informed traders and foolish traders lose. Informed traders can only profit to the extent that less informed traders are willing to lose to them." — [p.4]

> "A quote is good only as long as the breath is warm." — [p.33] (máxima dos oral auctions; precedência se mantém repetindo o quote continuamente)

> "Most principles of market microstructure somehow involve properties of zero-sum games." — [p.v, Acknowledgements] (Harris atribuindo a lição a Jack Treynor)

> "As a rule, you cannot manage what you cannot measure." — [p.76, Part VI intro]

> "Failures to understand these issues [sample selection bias, skill vs. luck] probably account for more trading losses than any other mistakes traders make." — [p.86]

## 9. Conexões com Outros Livros Desta Base

- **Transaction-cost measurement e implementation shortfall** em `trading_exchanges.md` (ch.21) estende conceito de execution cost tratado também em `systematic_trading.md` — Carver aborda costs como restrição de turnover.
- **Adverse selection / toxic order flow** (Harris ch.13-14) ressoa com o tratamento de microstructure noise e informed trading em `advances_fin_ml.md` (López de Prado, Cap. sobre Triple Barrier / market microstructure).
- **Zero-sum framing e edge requirement** alinham com `evidence_based_ta.md` (Aronson) — onde data-mining bias é a contrapartida estatística do princípio "informed traders só lucram se uninformed aceitam perder".
- **Volatility fundamental vs. transitória** (Harris ch.20) conecta com `regime_change.md` — identificação de regimes distintos em vez de tratar série como estacionária.
- **Performance evaluation / skill vs. luck** (Harris ch.22) alinha com `ml_for_asset_managers.md` (López de Prado) e `advances_fin_ml.md` — uso de Deflated Sharpe Ratio e PBO precisamente para discriminar skill de sorte.
- **Order anticipators / front running** (Harris ch.11) — conceito ausente em livros de technical analysis da base; relevante para `systematic_trading.md` ao desenhar execução slow-signal que evita signal leakage.
- N/A para fórmulas específicas de options pricing, Kelly sizing (ver `leverage_space.md`) ou filtros de sinal DSP (ver `rocket_science.md`, `cybernetic_analysis.md`) — Harris é macro/institucional, não micro/quantitativo.
