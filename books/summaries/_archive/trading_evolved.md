# Trading Evolved — Anyone can Build Killer Trading Strategies in Python

> **Page convention**: this summary cites using the `[PAGE N]` marker numbers from the extracted text (PDF 1-indexed), which is the only reliable numbering visible in `_full.txt` — the book does not print page numbers as plain text. The `check_citations.py` validator applies an offset automatically if detected.

## Metadata
- **Author:** Andreas F. Clenow [p.3]
- **Year:** 2019 [p.3]
- **Publisher:** Self-published / Equilateral Capital Management GmbH, Zurich [p.3]
- **Pages:** 467 (PDF)
- **ISBN:** 9781091983786 [p.4]
- **Main focus:** Teaches construction, backtesting, and analysis of quantitative trading strategies in Python (Zipline + PyFolio), with real models for ETFs, equities (momentum), and futures (trend, counter-trend, curve, time-return).

## 1. Core Thesis
Systematic trading is the use of computers to model, test, and implement mathematical trading rules. The book's goal is to make quantitative backtesting accessible to anyone with moderate background, using Python (Zipline, Pandas, PyFolio) as the tool, and demonstrating real trading models (not "magic systems") as the pedagogical vehicle. The scientific approach requires formulating hypotheses, testing with a skeptical mindset (default: reject), and prioritizing **simplicity** over curve-fitted complexity [p.21-23, p.27-30]. The central message is that the models shown "are teaching tools, not production grade models" — the reader should replicate, understand, modify, and only then build their own model [p.15, p.312, p.349].

## 2. Main Concepts
- **Systematic trading** — use of computers to model, test, and implement mathematical trading rules; removes the emotional component and enables idea validation [p.21, p.24].
- **Model Purpose / "raison d'être"** — every model needs a specific purpose (the market phenomenon it exploits), not just "make money"; purpose-less models are "accidental models" — almost certain overfit [p.27-28].
- **Accidental model** — a model created by testing indicators until positive returns are found; backtest looks good but has no predictive value [p.27-28].
- **Financial Risk** — defined as "potential value variation per unit of time" — volatility over time, not "how much I lose if my stop triggers" [p.37].
- **Mark-to-Market** — position/portfolio valuation always at current market price; "playing with the house's money" is a fallacy [p.39-40].
- **Risk per Trade (fallacy)** — retail idea that risk = stop distance × position; Clenow rejects this: two portfolios with the same "risk per trade" can have 2× different real risk if notional sizes differ [p.42-43].
- **Sharpe Ratio** — (annualized return − risk-free) / annualized standard deviation; values >1 are rare; strategies with Sharpe 3-5 typically carry "negative skew" (small wins, rare catastrophic loss) [p.45-46].
- **Investment Universe** — set of eligible markets; selection is critical and the main source of survivorship bias in equities [p.32-33, p.192].
- **Survivorship bias** — using an index's current constituents to simulate the past; fix: use the index's historical composition (joiners/leavers) [p.192, p.197-198].
- **Rebalancing** — position-size adjustments to maintain the target risk level as volatility/portfolio change; not a change of opinion, it is maintenance [p.35-36].
- **Momentum (Clenow score)** — annualized exponential-regression slope × R² (coefficient of determination); penalizes volatile/jumpy stocks [p.200, p.203-205].
- **Volatility Parity / Inverse Volatility sizing** — allocate positions so each contributes roughly equal risk; more volatile = lower weight [p.206-207, p.293].
- **Trend filter (index-level SMA)** — e.g., prohibit long when S&P 500 < SMA(200); criticized as potential curve-fitting when used to "explain" 2008/2020 [p.211-212].
- **Std-dev-based trailing stop** — exit when position drops N × std_dev from the peak; normalizes across markets [p.267-268].
- **ETF (good/bad/worst)** — good: passive low-cost trackers (SPY); bad: commodity ETNs (term-structure drag, counterparty risk); worst: leveraged/inverse (daily rebalance → volatility decay) [p.166-178].
- **Contango / Backwardation** — contango term structure has embedded bearish bias; backwardation has bullish bias [p.327-329].
- **Carry / Cost of Carry** — price difference between contracts, annualized; can be the sole signal source for "curve trading" [p.326, p.329].
- **Continuation** — synthetic continuous futures series, stitched via rolls; used only for signal calculation, not for trading [p.270, p.294].
- **Point Value (big point value)** — multiplier that converts a price move into $ P&L per contract [p.237-238].
- **Random portfolio benchmark ("Mr. Bubbles")** — random selection of 50 stocks from the S&P 500, rebalanced monthly, tends to beat the index long-term — the index is a poorly designed systematic strategy, not an "average" [p.370-372].

## 3. Formulas / Equations
**Momentum Score (Clenow)** [p.200, p.204-205]

$$\text{momentum\_score} = \left[\left(e^{\text{slope}}\right)^{252} - 1\right] \times 100 \times R^2$$

- $\text{slope}$ = slope of the linear regression of $\ln(\text{price})$ vs. time
- $R^2$ = coefficient of determination of the same regression (0 to 1)
- 252 = trading days/year (annualization)
- Use: stock ranking for momentum portfolios; built-in penalty for volatile stocks (low R²)
- Default window used in the book: 125 days [p.209]
- Minimum threshold used: 40 [p.211]

**Sharpe Ratio** [p.45-46]

$$SR = \frac{R_{\text{ann}} - R_f}{\sigma_{\text{ann}}}$$

- $R_{\text{ann}}$ = annualized strategy return
- $R_f$ = risk-free rate (Clenow recommends daily yields of short treasuries; retail can use 0 to compare strategies with each other) [p.46]
- $\sigma_{\text{ann}}$ = annualized standard deviation of returns
- Sharpe > 1 is rare; 0.7-0.8 can be "highly successful"; Sharpe 3-5 usually = dangerous negative skew [p.46]

**Position Size (Volatility Parity Futures)** [p.263]

$$\text{contracts} = \frac{\text{portfolio\_value} \times \text{risk\_factor}}{\sigma_{\text{price}} \times \text{point\_value}}$$

- $\text{risk\_factor}$ = target basis points of daily variation per position (e.g., 0.002 = 20 bps = 0.2% target daily impact) [p.263]
- $\sigma_{\text{price}}$ = 40-day std-dev of daily price differences (price changes, not returns) [p.262]
- $\text{point\_value}$ = contract big point value
- Result rounded down to int

**Volatility / Std-Dev of Price Changes (40 days)** [p.262-263]

```python
std_dev = df.close.diff()[-40:].std()
```

**Volatility para Equities (pct change)** [p.208]

```python
def volatility(ts):
    return ts.pct_change().rolling(vola_window).std().iloc[-1]
```

- `vola_window` = 20 days in the Momentum model [p.214]

**Normalized pullback (Counter-Trend)** [p.314-315]

$$\text{pullback} = \frac{\text{close}_t - \max(\text{close}_{t-20:t})}{\sigma_{40d}}$$

- Enter long if $\text{pullback} < -3$ (i.e., 3 std-dev below the 20d high) in a bull-market regime [p.314-315, p.321]

**Cost of Carry (Curve Trading)** [p.329-330]

$$\text{annualized\_carry} = \left(\frac{P_{\text{near}}}{P_{\text{far}}}\right)^{365/\Delta\text{days}} - 1$$

- Book example: SH9 at 907.50, SK9 at 921.50, expiry 61 days later → implied loss 1.52% over 61d = −8.75% annualized (contango) [p.329]
- Used as the sole input for trade selection in the "Trading the Curve" model [p.326]

**Trend Filter (Dual EMA)** [p.264-265]

- Bull: $\text{EMA}_{40} > \text{EMA}_{80}$
- Bear: $\text{EMA}_{40} < \text{EMA}_{80}$
- Used in the Core Trend Model and the Counter-Trend [p.265, p.312]

## 4. Algorithms and Pseudocode
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

## 5. Explicit Trading Rules
- **RULE [p.21-22]**: Before going systematic, **formulate your hypothesis as firm, testable rules**; if you cannot, the idea was not a complete model.
- **RULE [p.23]**: The default approach to backtesting is **skeptical** — look for reasons to **reject** the rule, not to accept it (confirmation bias is inevitable if you seek validation).
- **RULE [p.27-28]**: Every model must have a **specific purpose** (market phenomenon + target return profile); "make money" is not a purpose.
- **RULE [p.29]**: Use **as few rules and variations as possible**. Complexity must justify its existence economically — improving the backtest is not enough.
- **RULE [p.30]**: Every rule added must have a **real market explanation**, not just a historical-metric improvement.
- **RULE [p.32]**: Use part of the time series for fitting and part for out-of-sample testing. Never test on the same data you fit.
- **RULE [p.33]**: Prefer **portfolios** (multiple markets) over single-market strategies; single-market = zero diversification.
- **RULE [p.192, p.198]**: For equities, **use historical index membership** (not current constituents) to avoid survivorship bias.
- **RULE [p.193-194]**: When dealing with equities, **adjust for dividends** (total return series or cash dividend accounting); ignoring them = substantial multi-year distortion.
- **RULE [p.207]**: Use **volatility-parity position sizing** (inverse-volatility weighting) to give each position an "equal vote".
- **RULE [p.197]**: **S&P 500 momentum model** — trade only monthly, top 30 stocks by momentum score (125d window), buy if momentum > 40, inverse-vol weighting, volatility = 20d std-dev of returns.
- **RULE [p.261]**: Futures models must **check entry/exit signals AND rolls daily**; trades execute the day after the signal (close).
- **RULE [p.263]**: For futures, size each position to impact ~0.2% daily portfolio var (risk_factor = 20 bps) as the initial benchmark.
- **RULE [p.267-268]**: Trend trailing stop for futures = 3× std-dev of price changes (40d) from the position's peak reading. Implies ~0.6% portfolio giveback per position.
- **RULE [p.314-315]**: Counter-trend in bull — enter long if EMA40>EMA80 AND pullback < −3 std-dev from the 20d high; exit in 20 days OR on trend reversal.
- **RULE [p.349-352]**: **Combine multiple uncorrelated models** as portfolio components — book example: 5 equal-weighted models produced Sharpe 1.24 vs. best individual 0.84, drawdown −17% vs. individual −25% to −40%.
- **NEVER [p.30]**: Run an optimizer to find "best" parameters; use **reasonable variations** to test stability, not optimal values.
- **NEVER [p.41-42]**: Use pyramiding ("playing with house's money"); it violates mark-to-market and is based on a gambling fallacy.
- **NEVER [p.43]**: Define risk as "risk per trade" based on stop distance; this ignores that risk is potential variation per unit of time.
- **NEVER [p.44]**: Target triple-digit yearly returns — mathematically unviable long-term ("probability of ruin approaches 1").
- **NEVER [p.176]**: Hold leveraged/inverse ETFs beyond one day — daily rebalance creates volatility decay, loss even in sideways or bear markets.
- **NEVER [p.26]**: Leave an algo trading unsupervised; even when automated it needs constant monitoring.
- **NEVER [p.179-180]**: Assume you can short small ETFs in a backtest — borrow liquidity is limited and shares can be recalled at the worst moment.

## 6. Pitfalls and Anti-patterns
- [p.27-28] **Accidental models** — combining indicators randomly and tuning until the backtest looks good. No predictive value; a model without "raison d'être" is nearly guaranteed curve fit.
- [p.30] **Multi-parameter optimization** → "optimizers will tell you what the perfect parameters WAS for the past" — no predictive value.
- [p.31] **Ad-hoc filters to avoid bad years** (e.g., "filter that avoids 2008") — looks like backtest improvement but is overfit; had the model been developed earlier, the filter would not exist.
- [p.41-42] **Position-size pyramiding** — increasing position after a gain; "past trades lack magical ability to impact the future" — it is a gambling fallacy.
- [p.43] **"Risk per trade" based on stop distance** — wrong definition of risk; two portfolios with the same "risk per trade" can have very different real risk.
- [p.44-45] **Targeting triple-digit returns** — mathematically impossible long-term; realistic expectation = <15% p.a. for skilled traders.
- [p.175-176] **Leveraged/Inverse ETFs held >1 day** — daily rebalance causes volatility decay; even in a bear market of the underlying, an inverse ETF can lose.
- [p.179-180] **Assuming shorting ETFs is free** in the backtester — locate, funding rate, and recall risk destroy the edge in practice.
- [p.192] **Using current index constituents** to simulate the past — massive survivorship bias (would you have picked Enron and Lehman 10 years ago? But you pick Apple because you know it went up).
- [p.193] **Ignoring dividends** in equity backtests — significant multi-year impact.
- [p.211-212] **Long-SMA-based trend filter (e.g., 200d)** — may be **severe curve fitting** from hindsight knowledge of 2008; "we already know from experience that using such a long term trend filter will greatly mitigate damage from the two major bear markets of our generation. The question is of course if that has any predictive value in terms of avoiding the next" [p.212].
- [p.257] **Inability to explain a strategy simply** — red flag: "if you are unable to explain the idea behind your trading strategy in a simple, brief and understandable manner, then there is a clear risk that you have overcomplicated and over fitted rules".
- [p.26] **Automation without supervision** — "computers are only as smart as the person programming it, and usually not even that smart".
- [p.259-260] **Faking capital with futures** (trading a $100k portfolio as if it were $1M via margin) — a 10% drawdown wipes you out.
- [p.349-350] **Comparing models only by annual return** — ignores drawdown, Sharpe, correlation with existing portfolio; "a model with low expected return but low/negative correlation can greatly help overall portfolio".
- [p.370-372] **Comparing your strategy only against the S&P 500** — a random ("chimp with darts") selection of 50 stocks beats the index long-term. "The index is a completely different systematic trading strategy. And a poorly designed one at that" [p.371].
- [p.369] **Investing in active mutual funds** — ~80% fail to beat the benchmark in any 3-5 year period (SPIVA reports).
- [p.168] **Using ETNs as ETFs** — ETN = structured debt, counterparty risk; if the issuer goes bust, cash is lost (remember 2008).
- [p.321] **Expected: symmetric long/short design** — "bullish trends and bearish trends tend to behave quite differently and may require different parameter sets"; symmetry is simplification, not feature.

## 7. Sensitive Parameters
- **Momentum window = 125 days** [p.209, p.214] — "meant to roughly represent half a year". Clenow explicitly admits: "I deliberately chose middle of the road kind of settings. I pick them more or less at random, from a set of reasonable values" [p.210]. NOT optimized.
- **Minimum momentum = 40** [p.211] — arbitrary threshold. Clenow: "This fairly arbitrary number, is to ensure that we are not buying flat or negative stocks". Note: depends on window — shorter windows produce more extreme scores, so the threshold must scale [p.211].
- **Portfolio size = 30 stocks** [p.210] — economic rationale: "10 stocks = too high single-stock risk; too many = quality suffers and monitoring overhead". Not backtest-optimized.
- **Vola window = 20 days** (equities) [p.214] — "reasonable", industry standard.
- **Vola window = 40 days** (futures, std-dev of price changes) [p.262] — "roughly measures the past two months' volatility. Feel free to experiment".
- **Trend filter EMAs = 40/80 days** [p.265] — "these numbers are reasonable, as are many others. Feel free to try other combinations". Clenow: chosen for exposure symmetry, not for the best backtest.
- **Breakout window = 50 days** (Core Trend) [p.266] — arbitrary.
- **Stop = 3× std-dev** [p.267] — economic rationale: with risk_factor=0.2%, a 3σ stop loses ~0.6% of the portfolio per position, which is "acceptable giveback".
- **Risk factor = 20 bps (0.002) daily** [p.263] — main risk tuning knob; "reasonable" default that can be scaled to the mandate.
- **Days to hold = 20** (Counter-Trend) [p.315] — "approximately one month"; Clenow admits it is "wonky stop logic" in the demo [p.321].
- **Dip buy = −3 std-dev** (Counter-Trend) [p.315] — symmetric to the Trend stop to explain the dynamics; not optimized.
- **S&P 500 index trend filter (200d)** [p.211-212] — Clenow explicitly does NOT use it in the book's momentum model, suspected of retrospective curve fit.
- **Commission = 0.1% per $** (equity) [p.215]; **$0.85/contract + $1.5 exchange fee** (futures) [p.268-269] — realistic for a low-cost broker.
- **Slippage = VolumeShareSlippage, limit 2.5% of daily volume, impact 5%** (equity) [p.215]; **VolatilityVolumeShare limit 30%** (futures) [p.269].

## 8. Key Literal Quotes
> "The point of my books, all of my books, is to make a seemingly complex subject accessible." — [p.13]

> "Your default way of thinking should be to find ways to reject the rules. To show that they fail to add value and should be discarded." — [p.23]

> "Complexity [is] something inherently bad, something which needs to justify its existence. Any complexity you want to add to your model needs to have a clear and meaningful benefit." — [p.29]

> "Optimizers will tell you what the perfect parameters was for the past. They will also con you into a false sense of security, and make you believe that they have any sort of predictive value. Which they don't." — [p.30-31]

> "Financial risk is about potential value variation per unit of time." — [p.37]

> "Anyone aiming at achieving triple digit yearly returns will, with mathematical certainty, lose all of their money if they remain at the table. In such a game, the longer you play, the more your probability of ruin approaches 1." — [p.45]

> "If you are unable to explain the idea behind your trading strategy in a simple, brief and understandable manner, then there is a clear risk that you have overcomplicated and over fitted rules to match data, and that there is little to no predictive value." — [p.257]

> "The index is a completely different systematic trading strategy. And a poorly designed one at that." — [p.371]

> "Never forget that the interesting money in this business is made from trading other people's money." — [p.355]

## 9. Cross-references to Other Books in This Knowledge Base
- The **Momentum model (equity, S&P 500)** is an evolved version (with Python + Zipline code) of the model from `stocks_on_the_move.md` — same author Clenow; Clenow explicitly references the earlier book [p.196, p.199]. Here the implementation is quantitative with survivorship-bias handling via a CSV of historical index composition.
- The **Core Trend Model (futures)** is a Python reimplementation of the model presented in Clenow, *Following the Trend* (2013) [p.255-258]. No summary of that earlier book exists in this knowledge base.
- **`systematic_trading.md` (Rob Carver)** is explicitly referenced as a deeper theoretical complement — "a deep dive into systematic trading, you should look at something like the aptly named Systematic Trading (Carver, 2015)" [p.18]; Carver is also co-author of guest chapter 22 in *Trading Evolved* [p.385]. Connection: Carver advocates similar parsimony and position sizing; independent convergence on risk budgeting and the importance of skepticism against optimization.
- **Volatility parity / inverse-volatility sizing** [p.206-207, p.263] also central in `systematic_trading.md` — same concept, similar notation.
- **Counter-trend / mean reversion in bull markets** [p.310-315] complements the approach of `algo_trading_chan.md` and `machine_trading.md` (Ernest Chan) on mean-reversion; Clenow focuses on diversified futures, Chan on equity pairs.
- **Curve/carry trading** [p.326-330] treats a topic absent from other books in this knowledge base — section 18 is an original contribution.
- **Anti-optimization skepticism** [p.30-31, p.257] resonates strongly with `advances_fin_ml.md` (López de Prado — "backtest overfitting is the most pressing issue") and `evidence_based_ta.md` (Aronson — data-mining bias). Clenow reaches the same conclusion without a formal statistical framework, via empirical principle alone.
- **ETF pitfalls (leveraged/inverse daily rebalance decay)** [p.172-176] is a practical treatment that complements `volatility_trading.md` (Sinclair) on derivatives product structuring.
- **Random portfolio benchmark ("Mr. Bubbles")** [p.367-372] aligns with the discussion in `evidence_based_ta.md` on statistical significance against passive/random benchmarks.
