# Trading and Exchanges: Market Microstructure for Practitioners

## Metadata
- **Author:** Larry Harris (Fred V. Keenan Chair in Finance, Marshall School of Business, University of Southern California) [p.i]
- **Year:** 2002 [p.i]
- **Publisher:** Oxford University Press [p.i]
- **Pages:** ~113 (PDF draft; the published book has ~640 pages) [metadata]
- **ISBN:** N/A — the copy used is a Draft: March 1, 2002 / March 5, 2002, pre-publication [p.i]
- **Primary focus:** Market microstructure — who trades, how exchange rules shape liquidity, transaction costs, volatility, and profits, and why certain strategies win or lose in a zero-sum game.

## 1. Core Thesis
Markets are bilateral search problems: buyers search for sellers and vice versa; market structure (trading rules, information systems) determines search costs, informational power between trader types, and consequently liquidity, price transparency, volatility, and profits [ch.1, p.1-3; ch.19, p.75-76]. Harris frames trading as a **zero-sum game** measured relative to the market average: one side's gains equal the other side's losses; "informed traders can only profit to the extent that less informed traders are willing to lose to them" [p.4, Key Recurrent Themes, p.6]. The dominant practical implication: uninformed traders lose *because* they trade — limiting trading is the only rational defense [ch.14, p.59].

The book's five objectives [p.1-2]: understand the origins of (1) liquidity, (2) transaction costs, (3) informative prices, (4) volatility, (5) trading profits — and how market structure affects each.

## 2. Main Concepts
- **Liquidity** — the ability to trade in large size quickly at low cost when you want to [p.75]. Arises from bilateral search with multiple dimensions: immediacy, depth, width, resiliency [ch.19, p.75-76].
- **Immediacy** — liquidity dimension: the ability to trade *now*; the price of immediacy is the bid/ask spread [p.27, p.59].
- **Bid/Ask Spread (inside spread / touch)** — difference between best ask and best bid; the price impatient traders pay for immediacy [p.28, p.59].
- **BBO / NBBO** — Best Bid and Offer / National Best Bid and Offer (best price in the US) [p.28].
- **Standing/Open orders** — open limit orders that *offer* liquidity; market orders *take* liquidity [p.28].
- **Order-driven market** — uses order-precedence rules (price priority + time precedence or public-order precedence) and trade-pricing rules to match orders [p.32].
- **Quote-driven (dealer) market** — dealers quote bid/ask and trade with clients [p.29-30].
- **Price priority** — primary rule in oral auctions: traders with better prices have precedence [p.33].
- **Time precedence** — secondary rule: whoever *first* improves the price has priority at that level [p.33]. Only meaningful if the tick is not too small [p.34].
- **Tick / minimum price increment** — smallest increment by which price can be improved; a tick that is too small weakens the time-precedence rule; a tick that is too large discourages price improvement [p.34].
- **Fundamental value vs. market value** — intrinsic value vs. market price; noise = difference between them [p.46].
- **Random walk** — price changes in an efficient market are unpredictable because they reflect only new information [p.47, p.79].
- **Informed traders** — value traders, news traders, technical information-oriented traders, arbitrageurs; make prices informative by trading on fundamentals [p.46].
- **Order anticipators (parasitic)** — front-runners, sentiment-oriented technical traders, squeezers; profit by predicting other orders without making prices more informative [p.49].
- **Bluffers / price manipulators** — try to deceive others via rumor or wash trades ("paint the tape") to move prices [p.52].
- **Momentum traders** — buy after a rise, sell after a fall; especially vulnerable to bluffs [p.54].
- **Dealers** — passive traders who sell immediacy; earn the bid/ask spread; lose to informed traders [ch.13, p.56-58].
- **Adverse selection spread component** — portion of the spread that compensates the dealer for losses to well-informed traders [p.61].
- **Transaction cost spread component (transitory)** — portion of the spread that covers operating costs plus normal profit; causes bid/ask bounce [p.61].
- **Bid/ask bounce** — minor oscillation between bid and ask as order flow alternates; transitory volatility [p.61].
- **Value traders** — "ultimate liquidity suppliers"; trade when price diverges from fundamental value [ch.16, p.65-67].
- **Winner's curse** — winning an auction and then realizing you paid too much / sold too cheap; the central risk of the value trader [p.65].
- **Arbitrageurs** — trade on relative values; hedge portfolio with long+short legs; profit from price convergence [ch.17, p.68-70].
- **Basis / arbitrage spread / arbitrage bounds** — basis = price difference between legs; fair value = "correct" basis; arbitrage spread = basis − fair-value-basis; arbitrageurs trade when basis leaves its bounds [p.70].
- **Block trade** — order too large to fill via normal mechanics; typically >1/4 of average daily volume (NYSE: ≥10,000 shares) [p.62].
- **Latent demand / responsive traders** — willing to trade if asked, with no orders on the book; block brokers discover them by phone [p.63].
- **Fundamental volatility** — price changes driven by fundamental value changes (unpredictable in efficient markets) [p.78-79].
- **Transitory volatility** — volatility caused by uninformed-trader trading; reversible; regulators can affect it [p.78, p.74 epilogue].
- **Implementation shortfall / transaction cost measurement** — difference between trade price and benchmark price, multiplied by size + sign [p.83-84].
- **Explicit / Implicit / Missed-trade-opportunity costs** — three components of transaction cost [p.82].
- **Zero-sum game** — accounting gains on one side = accounting losses on the other [p.6, p.1].
- **Order flow externality** — traders who post limit orders give free options to others; this attracts and binds traders to markets because traders want free trading options [p.15].
- **Front running (legal vs. illegal)** — illegal if it breaches brokerage confidentiality; legal if inferred by public observation [p.50-51].
- **Realized spread** — difference between the prices at which the dealer *actually* bought and sold (may be smaller or negative vs. quoted spread due to adverse selection) [p.58].

## 3. Formulas / Equations
**Estimated transaction cost vs. benchmark price** [p.83-84]

For a buy:
$$\text{EstimatedCost} = \text{TradeSize} \times (\text{TradePrice} - \text{BenchmarkPrice})$$

For a sell:
$$\text{EstimatedCost} = \text{TradeSize} \times (\text{BenchmarkPrice} - \text{TradePrice})$$

Or, in unified form using TradeSign (+1 buy, −1 sell):
$$\text{EstimatedCost} = \text{TradeSize} \times \text{TradeSign} \times (\text{TradePrice} - \text{BenchmarkPrice})$$

- Sum of estimated costs across all parties to a trade = 0 (zero-sum) [p.83].
- Traders who *demand* liquidity pay cost > 0; traders who *offer* it have cost < 0 [p.83].

**Desired position proportional to mispricing** [p.48, box "An Algebraic Illustration"]

$$D_i = a \cdot (f_i - P)$$

- $f_i = V + e_i$ = forecast of trader $i$, with $e_i$ error term (mean 0, unbiased) [p.48]
- $V$ = true fundamental value
- $P$ = market price
- $a$ = constant of proportionality
- Implication: traders with forecast > price want long; < price want short. Aggregation of forecasts by the market produces a price more accurate than any individual forecast [p.48].

**Realized spread (narrative example, not a labeled formula)** [p.58]

$$\text{RealizedSpread} = \text{AvgSellPrice} - \text{AvgBuyPrice}$$

- In the Dell example: quoted spread = 0.3; after an adverse-selection downward move, a roundtrip of 35.0 buy → 34.9 sell ⇒ realized = −0.1 [p.58].

**Unilateral search stopping rule** [p.76]

Continue searching while:
$$E[\text{benefit of next inquiry}] > E[\text{cost of next inquiry}]$$

- Numerical example: benefit = (probable improvement) x (prob of finding better) = 10 x 0.25 = $2.50; cost = 5 min x ($30/hr) = $2.50 ⇒ stop [p.77].

N/A for formal Kyle/Glosten-Milgrom models — Harris chooses prose with minimal equations ("I fully explain all essential concepts in the main text" [p.1-1]).

## 4. Algorithms and Pseudocode
**Oral auction — trading flow in open outcry** [ch.6, p.32-34]

```
while market is open:
    trader shouts bid/offer (open-outcry rule)  [p.32]
    if another trader accepts:
        trade occurs at the shouted price
        buyer: "take it"; seller: "sold"        [p.32]
    precedence rules:
        1) price priority (best price wins)     [p.33]
        2) time precedence (first to improve)   [p.33]
           — maintained by repeating the quote; "quote good only as long as the breath is warm" [p.33]
    to take precedence without time, must
      improve price by >= tick (leapfrog)       [p.33-34]
```

**Bluff — long-side bluff scheme (Bill/BNB example)** [ch.12, p.52-54]

```
Phase 1 (accumulation, days 1-40):
    use limit orders to buy slowly, letting
    the market come to you; 200,000 shares @ avg 6.00 [p.52]

Phase 2 (promotion, day 31+):
    post in multiple forums with different
    usernames; optimistic projections based on
    real 10-Q/10-K to boost credibility         [p.52]

Phase 3 (trigger):
    wait for a catalyst (ambiguous press release)
    submit market orders split across multiple
    brokers simultaneously to cause a price jump [p.53]

Phase 4 (distribution):
    sell slowly on the rise; momentum traders
    are particularly susceptible to bluffs; momentum traders primarily buy stock from the bluffer [p.54]
```

— Harris describes both endings: success (momentum traders are fooled) and failure (value traders silence the bluff). Lesson: uninformed momentum traders are the predictable victims.

**Value-trader liquidity provision loop** [ch.16, p.65-67]

```
for each instrument in watchlist:
    V_i = estimate_fundamental_value(instrument)  [p.65]
    P_i = current_market_price
    if |P_i - V_i| > outside_spread / 2:
        if P_i < V_i:   BUY  (uninformed selling pressure drove price down) [p.66]
        if P_i > V_i:   SELL
    mitigate:
        - adverse selection risk (news traders more informed) [p.67]
        - winner's curse (value misestimated)                 [p.67]
    DO NOT post quotes (do not give free options to the market) [p.67]
```

**Order-submission decision (market vs. limit)** [ch.18, p.71-73]

```
INPUT: bid/ask spread s, urgency u, view_on_value v
if v == "no opinion":
    if s small:  use MARKET orders (cheap immediacy)          [p.72]
    if s large:  use LIMIT orders   (offer liquidity)         [p.72]
if v != "no opinion":
    compare expected trade_price vs. fundamental_value
    use MARKET if you can fill better than v
    otherwise LIMIT
for LARGE orders:                                             [p.71]
    decide: shop vs. hide; one broker vs. many; split over time
    exposure risk ⇒ front-runners and quote-matchers
```

## 5. Explicit Trading Rules
- **RULE [p.59]**: Submit market orders when the bid/ask spread is *narrow* and limit orders when it is *wide* — unless you have a view of value (then invert if price has run in your favor) [p.72].
- **RULE [p.59]**: Before deciding market vs. limit, compare the current spread with the instrument's *typical* spread; only then do you know whether immediacy is expensive or cheap [p.59].
- **RULE [p.72]**: Large traders must decide **before** exposure: shop vs. hide, single broker vs. multiple, split over time vs. all-at-once; display is the critical buy-side decision [p.71].
- **RULE [p.50]**: Brokers should "shop the block" only with traders likely to take the other side; broad exposure attracts front-runners [p.50-51].
- **RULE [p.33]**: To gain time precedence in an oral auction you must *be the first to improve* the best bid/offer by at least one tick; while you hold the price, no one can trade ahead of you at that level [p.33].
- **NEVER [p.59]**: "Uninformed traders lose simply because they trade. If you are an uninformed trader and do not want to lose, you should minimize your trading." — the book's single most important lesson, self-declared by the author [p.59].
- **NEVER [p.52]**: Offer liquidity (limit orders, dealing) without understanding adverse selection — you will be giving free trading options to those who know more than you [p.5, p.59].
- **NEVER [p.54]**: Be a blind momentum trader after a price jump with volume — you are a prime target of bluffers and order anticipators [p.54].
- **RULE [p.65]**: Value traders should not reveal reservation prices (outside spread) via public quotes; this leaks their value estimates [p.67].
- **RULE [p.68]**: Arbitrageurs should only put on the trade when the basis leaves the *arbitrage bounds* (fair value ± carry costs + margin of safety) [p.70].
- **RULE [p.71]**: If a limit order does not execute and the market moves against you, be prepared to pay worse prices — traders who *need* to fill must accept the risk via market orders or limit prices close to the market [p.72-73].
- **RULE [p.49]**: In markets with time precedence, order anticipators must improve price by >= 1 tick to trade ahead; tick size therefore determines front-running profitability [p.49].

## 6. Pitfalls and Anti-patterns
- [p.59] "Uninformed traders lose whether they submit limit or market orders. They lose simply because they trade" — the worst pitfall is believing trading is free if you pick the right order type.
- [p.46-48] Believing yourself informed without being so: "most traders who believe that they are informed traders do not trade profitably because they are not truly well informed" [p.46]. Test: do you have information others lack, *or* do you process public information better than average?
- [p.54] Momentum trading after catalysts with volume may be buying at the peak of a bluff; "they are particularly susceptible to bluffs" [p.54].
- [p.49-51] Revealing large orders to inattentive brokers → legal front-running by experienced observers (Rifka vs. Jon example) [p.51].
- [p.67] Value traders who post their outside spread publicly give free options to the informed — your outside spread must stay private [p.67].
- [p.70] "Risk-free" arbitrage does not exist: basis risk / residual risk remains even after common factors cancel — specific factors affect legs differently [p.70].
- [ch.22, p.85-87] Confusing skill with luck in performance evaluation; skilled managers can have poor returns in adverse periods, and weak managers can look good in bull markets [p.86-87]. "Failures to understand these issues probably account for more trading losses than any other mistakes traders make" [p.86].
- [p.86] Sample-selection bias in evaluating track records can distort expectations — surviving fund managers are not a representative sample.
- [p.54-55] Ignoring that "timing is everything" even with the right direction: "If they initially have no positions, and they sell short too soon, they initially will lose on their short positions. If they cannot finance their losses, their brokers will force them to buy to cover" [p.107].
- [p.65] Winner's curse: winning an auction/trade *is negative information* — it means your estimate was the most optimistic (or pessimistic, if short) in the pool, increasing the probability of error [p.65, p.67].
- [p.59] Dealers who fail to adjust spread for adverse selection go bankrupt — no one can lose money to informed traders indefinitely [p.61].
- [ch.11, p.49] Large traders who fail to split orders or hide exposure pay the full price-impact cost plus a fee to the front-runner who copies them [p.49-50].
- [p.105-107] Bubbles: momentum traders + leveraged buyers + order anticipators accelerate deviations; when a crash occurs, margin calls + stop-loss orders amplify the fall [p.105-107].

## 7. Sensitive Parameters
- **Tick size / minimum price increment** [p.34]: Harris justifies this economically — a tick too small weakens time precedence (reduces incentive to improve prices); a tick too large discourages price improvement due to incremental cost. Not curve-fit; it is a market-design decision with a trade-off. "Exchanges and regulators pay close attention to it" [p.34].
- **Block-trade threshold (NYSE: 10,000 shares)** [p.62]: Harris criticizes the fixed threshold — "Block trading statistics would be more useful if block trades were classified by whether they exceed some fraction of average daily volume rather than by whether they exceed some fixed size" [p.63]. Suggestion: >= 1/4 of the instrument's ADV.
- **Spread components (transaction-cost vs. adverse-selection)** [p.61]: estimation requires econometric methods (the draft does not specify a closed-form formula); values depend on the information-asymmetry regime.
- **Hedge ratios (arbitrage)** [p.70]: "Traders choose their hedge ratios to minimize the total risk of the portfolio" — Harris does not prescribe a specific method (OLS? regime-switching?), only that the numerator is the instrument with the largest loading on the common risk factor [p.70].
- **Arbitrage bounds** [p.70]: fair value ± carry costs. Harris emphasizes that fair values "are not common knowledge" and must be estimated [p.70] — genuinely proprietary parameter, not optimizable in a generic backtest.
- **Limit-order limit price** [p.73]: the decision of where to place it depends on "execution probability vs. execution price tradeoff". Harris points to econometric models sold by vendors but does not provide a formula [p.73].
- **Buy-side display decisions (whole vs. split, one broker vs. many)** [p.71]: enormous parameter space, dependent on urgency, size relative to ADV, and presence of parasitic traders. "Display decisions are the most important trading decisions that large buy side traders make" [p.71].

## 8. Key Literal Quotes
> "The most important lesson you may learn from this book appears in this chapter. You will learn why uninformed traders lose to well-informed traders whether they submit limit orders or market orders. Uninformed traders lose simply because they trade. If you are an uninformed trader and do not want to lose, you should minimize your trading." — [p.59]

> "Trading is a zero-sum game when gains and losses are measured relative to the market average. In a zero-sum game, someone can win only if somebody else loses. On average, well-informed speculators and bluffers win, and poorly informed traders and foolish traders lose. Informed traders can only profit to the extent that less informed traders are willing to lose to them." — [p.4]

> "A quote is good only as long as the breath is warm." — [p.33] (maxim of oral auctions; precedence is maintained by repeating the quote continuously)

> "Most principles of market microstructure somehow involve properties of zero-sum games." — [p.v, Acknowledgements] (Harris attributing the lesson to Jack Treynor)

> "As a rule, you cannot manage what you cannot measure." — [p.76, Part VI intro]

> "Failures to understand these issues [sample selection bias, skill vs. luck] probably account for more trading losses than any other mistakes traders make." — [p.86]

## 9. Cross-references to Other Books in This Knowledge Base
- **Transaction-cost measurement and implementation shortfall** in `trading_exchanges.md` (ch.21) extends the execution-cost concept also treated in `systematic_trading.md` — Carver frames costs as a turnover constraint.
- **Adverse selection / toxic order flow** (Harris ch.13-14) resonates with the treatment of microstructure noise and informed trading in `advances_fin_ml.md` (López de Prado, chapter on Triple Barrier / market microstructure).
- **Zero-sum framing and edge requirement** align with `evidence_based_ta.md` (Aronson) — where data-mining bias is the statistical counterpart to the principle "informed traders only profit if uninformed ones agree to lose".
- **Fundamental vs. transitory volatility** (Harris ch.20) connects with `regime_change.md` — identification of distinct regimes rather than treating the series as stationary.
- **Performance evaluation / skill vs. luck** (Harris ch.22) aligns with `ml_for_asset_managers.md` (López de Prado) and `advances_fin_ml.md` — use of Deflated Sharpe Ratio and PBO precisely to discriminate skill from luck.
- **Order anticipators / front running** (Harris ch.11) — concept absent in technical-analysis books in the knowledge base; relevant for `systematic_trading.md` when designing slow-signal execution that avoids signal leakage.
- N/A for specific options-pricing formulas, Kelly sizing (see `leverage_space.md`), or DSP signal filters (see `rocket_science.md`, `cybernetic_analysis.md`) — Harris is macro/institutional, not micro/quantitative.
