# Stocks on the Move: Beating the Market with Hedge Fund Momentum Strategies

## Metadata
- **Autor:** Andreas F. Clenow [p.2]
- **Ano:** 2015 [p.3]
- **Editora:** Equilateral Capital Management GmbH (self-published, Zurich) [p.3]
- **Páginas:** 249
- **ISBN:** 1511466146 / 978-1511466141 [p.3-4]
- **Foco principal:** Systematic long-only equity momentum strategy applied to S&P 500 constituents, with volatility-adjusted ranking, ATR risk parity sizing, and a long-term index regime filter.

## 1. Tese Central

"Buy stocks that move up" [p.7] — a stock that has been moving up strongly for a while is likely to continue doing so a little bit longer [p.7]. The book's mission is to present a complete, rule-based set of mechanics to manage a momentum portfolio (ranking, sizing, regime filter, rebalancing, exits) so the concept can be simulated and traded end-to-end [p.7-9]. Clenow argues that traditional trend following (trailing stops on single futures-style signals) does NOT work on individual stocks [p.33], but volatility-adjusted cross-sectional momentum combined with a market regime filter and risk parity sizing beats the S&P 500 Total Return substantially with roughly half the drawdown [p.115, p.218].

## 2. Conceitos-Chave

- **Momentum Effect** — "When a stock has been going up for a while, the likelihood of it continuing up is greater than for it to turn around" [p.58]. Empirically documented since Levy (1967) and Jegadeesh & Titman (1993) [p.60].
- **Market Regime Filter** — Index-level long-term trend filter. Clenow uses S&P 500 vs its 200-day moving average; when index is below, no new buys are allowed [p.66-67].
- **Volatility-Adjusted Momentum (Adjusted Slope)** — Annualized exponential regression slope of 90-day log-price, multiplied by R² (coefficient of determination) to penalize choppy/gappy stocks [p.75-77, p.82].
- **Exponential Regression Slope** — Linear regression on the log of price; slope expressed as a percentage per day, then annualized by compounding over 250 trading days [p.71-72].
- **Coefficient of Determination (R²)** — Measures fit of regression line to price series. Used as the "smoothness" penalty in the ranking [p.74-75].
- **ATR (Average True Range)** — 20-day average of true range; used as volatility proxy for position sizing [p.88].
- **Risk Parity Sizing** — Each position sized so its theoretical daily dollar move equals a target fraction (10 bps) of portfolio equity [p.86-89].
- **Position Rebalancing** — Recalibrate share counts every two weeks so each position still targets 10 bps daily impact under current ATR and equity [p.91-93, p.108-109].
- **Portfolio Rebalancing** — Weekly check: sell holdings that fell out of ranking / below 100d MA / had a >15% gap; refill from the top of the ranking list [p.95-96, p.110-111].
- **Gap Filter** — Any stock with a single move > 15% in the past 90 days is disqualified [p.82, p.98].
- **Trend Filter (per stock)** — Stock must trade above its 100-day moving average to be a buy candidate [p.81-82].
- **Historical Index Membership / Delisting** — Simulations must use point-in-time index constituents and include delisted stocks to avoid survivorship bias [p.107, p.238-239].

## 3. Fórmulas / Equações

**Annualized Exponential Regression Slope** [p.70-72, p.77]

Given a series of closing prices $P_t$ over $N = 90$ trading days, compute the linear regression slope $m$ of $\ln(P_t)$ vs $t$:

$$\text{AnnualizedSlope} = \left( e^{m} \right)^{250} - 1$$

Where $m$ is the daily log-slope. The $-1$ gives it as a percent; Clenow in Excel form computes `=(EXP(SLOPE(LN(prices), days))^250) - 1` [p.77].

**Adjusted Slope (ranking score)** [p.76, p.82]

$$\text{AdjustedSlope} = \text{AnnualizedSlope} \times R^2$$

Where $R^2$ is the coefficient of determination from the same regression (Excel `RSQ()` on the log series) [p.77]. Higher = better momentum with smoother fit.

**ATR-Based Position Sizing (Risk Parity)** [p.88-89, p.98]

$$\text{Shares} = \frac{\text{AccountValue} \times \text{RiskFactor}}{\text{ATR}_{20}}$$

- $\text{RiskFactor} = 0.001$ (10 basis points = target daily dollar impact per stock) [p.88, p.98].
- $\text{ATR}_{20}$ = 20-day Average True Range in price units [p.88].
- Example [p.89]: Account $100,000, Monster Beverage ATR = 3.26 → shares = $100,000 \times 0.001 / 3.26 = 30.67$ → round down to 30 shares.

**True Range (per day)** [p.88]

$$\text{TR}_t = \max\!\left( H_t - L_t,\ |H_t - C_{t-1}|,\ |L_t - C_{t-1}| \right)$$

ATR is the average of TR over N days (Clenow uses N=20) [p.88].

## 4. Algoritmos e Pseudocódigo

**Ranking Algorithm (run every Wednesday)** [p.73-77, p.82, p.98]

```
for each stock S in S&P 500 constituents (point-in-time membership):
    prices = last 90 trading days of S closing prices
    log_prices = ln(prices)
    slope_m = linear_regression_slope(log_prices, t=0..89)
    annualized = (exp(slope_m))^250 - 1
    r_squared = RSQ(log_prices, t)
    adjusted_slope = annualized * r_squared
    
    # Disqualification filters
    if S.close < SMA(S.close, 100):        # trend filter [p.81-82]
        S.disqualified = True
    if max_gap(S, lookback=90) > 0.15:     # gap filter [p.82]
        S.disqualified = True

sort stocks by adjusted_slope DESC
return ranking_table
```

**Complete Trading Strategy (flow, every Wednesday)** [p.98-100, flow chart p.102]

```
# --- Portfolio Rebalance (every Wednesday) ---
update ranking_table

# Sell leg
for each held stock H:
    if rank(H) > top_20%_cutoff OR                # e.g. rank > 100 in S&P 500
       H.close < SMA(H.close, 100) OR             # below 100d MA
       max_gap(H, 90) > 0.15 OR                   # had >15% gap
       H no longer in index:                       # left the index
        SELL H

# Buy leg
if S&P500.close > SMA(S&P500.close, 200):         # regime filter [p.98-99]
    for S in ranking_table (top-down):
        if not_held(S) and not_disqualified(S):
            shares = floor(account_value * 0.001 / S.ATR20)
            BUY shares of S
            if cash_remaining < next_stock_cost: break
# else: do nothing — no new buys in bear regime (slow scale-out) [p.99, p.111]

# --- Position Rebalance (every SECOND Wednesday) ---
for each held stock H:
    target_shares = floor(account_value * 0.001 / H.ATR20)
    if |target_shares - current_shares| > threshold:
        adjust position to target_shares
```

**Random-Portfolio Benchmark ("beat Wall Street with a dice roll")** [p.235-236]

```
monthly:
    liquidate entire portfolio
    pick 50 random stocks from S&P 500 constituents (point-in-time)
    size each via ATR risk parity (same formula as main strategy)
# Result: virtually every random run beats S&P 500 TR over long horizons
# because of risk-parity weighting vs market-cap weighting [p.221-223, p.236]
```

## 5. Regras de Trading Explícitas

- **REGRA [p.98]**: Only trade on Wednesdays. All calculations use daily data, but decisions happen once per week. Day choice is arbitrary — pick any day.
- **REGRA [p.98]**: Rank S&P 500 stocks by (annualized 90-day exponential regression slope) × R².
- **REGRA [p.98]**: Disqualify any stock trading below its 100-day moving average.
- **REGRA [p.98]**: Disqualify any stock with a single-day move > 15% in the past 90 days.
- **REGRA [p.98-99]**: Open new positions ONLY if S&P 500 Index is above its 200-day moving average. If below, do not buy; hold existing positions (slow scale-out as they fall out of ranking).
- **REGRA [p.98]**: Position size = `AccountValue × 0.001 / ATR20`. Target daily impact per stock = 10 bps.
- **REGRA [p.99]**: Build initial portfolio by buying top-ranked non-disqualified stocks until cash runs out.
- **REGRA [p.99, p.110]**: Every Wednesday — sell holdings that (a) rank outside top 20% (e.g. rank > 100 in S&P 500), (b) dropped below 100d MA, (c) had >15% gap, or (d) left the index.
- **REGRA [p.99]**: Every second Wednesday — recalculate target position sizes using current ATR and current account value; adjust if deviation is significant.
- **REGRA [p.94]**: Do NOT use stop-losses. Exit is governed purely by ranking deterioration, trend breach, gap, or index exit.
- **REGRA [p.96]**: Do NOT use trailing stops. They keep stale underperformers and lock in sideways drifters.
- **NUNCA [p.94-95]**: Do not sell a holding just because the index drops below the 200d MA — only stop adding new positions. Existing holdings exit on their own criteria.
- **NUNCA [p.68]**: Do not rank stocks by a single simple measure like "% above 200d MA" — it ignores volatility and rewards single-day jumps (e.g. takeovers) [p.68-69].
- **NUNCA [p.83-85]**: Do not use equal-cash weighting. It tilts the portfolio toward the most volatile names.

## 6. Pitfalls e Anti-patterns

- [p.219-220] **Do not optimize parameters.** "Optimizations are evil and out to kill you." Clenow states he picked all numbers (200d, 100d, 90d, 15%, 10bps) without optimization; a result like "237-day MA is optimal" is curve-fit and has no predictive value.
- [p.82, p.104] **Do not buy stocks with large recent gaps (>15% in past 90d).** These are usually takeover announcements, not genuine momentum — the stock is dead money afterwards.
- [p.238-239] **Survivorship bias kills simulations.** Using current S&P 500 constituents for a 10-year backtest creates fake outperformance because current members are selected BECAUSE they rose. You MUST use point-in-time membership and include delisted stocks.
- [p.239] **Missing cash dividends makes total returns meaningless over time.** Handle via dividend factors or as cash injections.
- [p.239-240] **Single-strategy single-instrument backtesting software is useless.** Must handle full portfolio semantics (multiple positions, rebalancing, cross-sectional ranking).
- [p.91-92] **Volatility is non-stationary.** A position sized once and left alone drifts to random risk — ATR doubling (e.g. Monster Aug 2014) doubles your risk allocation if you don't rebalance.
- [p.63-65] **Do not hold momentum stocks through a bear market.** Correlations go to 1, diversification is illusory, momentum effect breaks down.
- [p.67-69] **Do not pick stocks by visual chart inspection or familiarity.** Discretionary pattern-matching is inconsistent day-to-day.
- [p.229-230] **Do not hold < 10 stocks.** Event risk (single-stock shock) dominates; "element of luck becomes too large."
- [p.231] **Do not hold 40+ stocks (too broad).** Simulations worsen, becomes impractical at low capital, loses the rebalance effect.

## 7. Parâmetros Sensíveis

- **Regression period = 90 trading days** [p.73, p.223-224]. Justification: "medium-term momentum" range. Sanity check on p.224: 60/90/120/240 all produce similar results; "exact number you pick isn't of very high importance."
- **Index regime filter = S&P 500 200d MA** [p.66]. Justification: long-term trend. Clenow explicitly refuses to optimize this [p.219-220]; concept matters, not exact number.
- **Per-stock trend filter = 100d MA** [p.81, p.104]. Justification: "failsafe to avoid some weird situations" where a stock ranks high but is still in a downtrend.
- **Gap threshold = 15% in past 90 days** [p.82]. Justification: filters takeover-driven jumps that corrupt the momentum signal.
- **Risk factor = 10 bps (0.001) per stock** [p.88, p.228-229]. Justification: produces 20-30 stock portfolios (good diversification without fragmentation). Sanity check [p.229-230]: 5bps (40-50 stocks) slightly worse, 50bps (5-6 stocks) better in simulation but too concentrated — "dependency on luck becomes too large."
- **Portfolio rebalance frequency = weekly** [p.99, p.108]. Justification: reduces workload and costs vs daily; captures ranking churn.
- **Position rebalance frequency = every 2 weeks** [p.99, p.108]. Justification: "good compromise" between risk accuracy and trading costs.
- **Top 20% cutoff for holding (rank ≤ 100 on S&P 500)** [p.95, p.110]. Justification: leeway — narrower cutoff would force too much churn.
- **ATR lookback = 20 days** [p.88]. "Matter of preference and purpose and not overwhelmingly important."
- **Trading weekday = Wednesday** [p.98]. Explicitly arbitrary ("Pick a day. It doesn't matter.") [p.99].

## 8. Citações Literais Importantes

> "A stock that has been moving up strongly for a while is likely to continue doing so a little bit longer. That's the core idea. The rest is details." — [p.7]

> "Don't buy stocks in a bear market." — [p.64, restated p.67]

> "When it comes to position size, you need to remember that we're not allocating money. We're allocating risk." — [p.83]

> "Optimizations are evil and out to kill you. Don't trust them." — [p.219]

> "You need to trade a concept, not a magical number." — [p.224]

> "Volatility is the currency that we use to buy performance. What we want to achieve is to pay as little volatility as possible for as much performance as we can get." — [p.69]

## 9. Conexões com Outros Livros Desta Base

- **Regime filter (200d MA on index)** — same concept used as a simple trend / market-state gate; see `regime_change.md` for formal regime-change detection methods (more sophisticated than a single MA cross).
- **Avoid optimization / trade concepts not numbers** — strongly aligned with `systematic_trading.md` (Carver's parsimony principle) and `evidence_based_ta.md` (Aronson on data-mining bias). Clenow's anti-optimization stance at [p.219-220] is a plain-English version of the same warning.
- **ATR-based volatility position sizing** — overlaps with `systematic_trading.md` volatility-targeting framework; Clenow uses per-position ATR sizing, Carver uses portfolio-level vol targeting.
- **Survivorship bias and point-in-time data** [p.238-239] — same warning as `advances_fin_ml.md` on dataset hygiene and as `ml_for_asset_managers.md` on backtest integrity.
- **Cross-sectional momentum ranking** — Jegadeesh & Titman (1993) referenced [p.60]; same empirical anomaly formalized statistically in `evidence_based_ta.md` (momentum as one of the few statistically robust effects).
- **Risk parity beats market-cap weighting** [p.221-223] — empirical observation consistent with factor literature in `ml_for_asset_managers.md`.
