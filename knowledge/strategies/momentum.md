# Momentum Strategies

Trend-following and cross-sectional momentum, with regime filter.

## Sources

- [`books/systematic_trading.md`](../books/systematic_trading.md)
- [`books/stocks_on_the_move.md`](../books/stocks_on_the_move.md)

## Pending sources (not yet absorbed)

- `books/trading_evolved.md` — missing (absorb with `/absorb-book trading_evolved`)
- `books/universal_trend_tactics.md` — missing (absorb with `/absorb-book universal_trend_tactics`)

## From `books/systematic_trading.md`

### Explicit Trading Rules

- **RULE [p.160, ch.10]**: Subsystem position = (volatility_scalar × forecast) / 10. Apply to every instrument, every day.
- **RULE [p.173, ch.11]**: Portfolio position = subsystem_position × instrument_weight × IDM. IDM must never exceed 2.5 [p.170–171 (ch.11)].
- **RULE [p.174, ch.11]**: Apply position inertia — do not trade if the rounded target position is within 10% of the current held position.
- **RULE [p.133, ch.8]**: Cap combined forecast at ±20 after applying FDM. Never allow a combined forecast above +20 or below −20.
- **RULE [p.144, ch.9]**: Set percentage volatility target = SR_realistic / 2 (Half-Kelly). For negative-skew strategies: SR_realistic / 4 [p.146 (ch.9)].
- **RULE [p.146, ch.9]**: SR_realistic must be capped at 1.0 for staunch systems traders, regardless of how good the back-test looks. For semi-automatic traders, the maximum safe achievable SR is 0.5, so the volatility target must not exceed 25% [p.146 (ch.9)].
- **RULE [p.187–188, p.196, ch.12]**: Accept a new instrument only if its annual cost ≤ 0.13 SR/year (systems traders, p.187–188) or ≤ 0.08 SR/year (asset allocators and semi-auto traders, p.196).
- **RULE [p.212, ch.13]**: Semi-automatic stop loss uses X = 4 sigma_price_points from tracking extreme. On trigger: close the position only (no automatic reversal). Never modify the forecast after entering a trade [p.222 (ch.13)].
- **RULE [p.222, ch.13]**: Do NOT use profit targets for semi-automatic trading — no consistent evidence they improve performance.
- **RULE [p.122, ch.7]**: Prune any two trading rule variations with correlation > 0.95 — they add no independent information.
- **RULE [p.116, ch.7]**: Asset allocating investor always uses forecast = +10 (constant buy). Never short via this archetype.
- **RULE [p.201–202, ch.12]**: If maximum portfolio position < 4 blocks for any instrument at maximum forecast: increase instrument weight, reduce portfolio size, or remove the instrument.
- **RULE [p.196–197, ch.12]**: Use 20-week volatility look-back for asset allocators (instead of 25-day) to reduce volatility-estimate-driven turnover.

---

### Formulas / Equations

**Annualising volatility** [p.21 (ch.1)]

Daily to annual: multiply by $\sqrt{256} = 16$.

$$\sigma_{annual} = 16 \times \sigma_{daily}$$

**Sharpe Ratio (annualised)** [p.32 (ch.2)]

$$SR_{ann} = 16 \times \frac{\mu_{daily}}{\sigma_{daily}}$$

**Half-Kelly volatility target** [p.144 (ch.9)]

Optimal percentage volatility target equals the realistic annualised Sharpe ratio. In practice use Half-Kelly:

$$\sigma_{target}^{Half\text{-}Kelly} = \frac{SR_{realistic}}{2}$$

For negative-skew strategies, halve again: $\sigma_{target} = SR_{realistic} / 4$ [p.146 (ch.9)].

**Volatility scalar** [p.159 (ch.10)]

$$\text{Volatility scalar} = \frac{\text{Daily cash volatility target}}{\text{Instrument value volatility}}$$

$$\text{Instrument value volatility} = \text{Block value} \times \text{Price volatility (\%)} \times \text{FX rate}$$

**Subsystem position** [p.160, 163 (ch.10)]

$$\text{Subsystem position} = \frac{\text{Volatility scalar} \times \text{Forecast}}{10}$$

**Portfolio instrument position** [p.173 (ch.11)]

$$\text{Portfolio position} = \text{Subsystem position} \times \text{Instrument weight} \times \text{IDM}$$

where IDM is the instrument diversification multiplier (maximum 2.5 per [p.170–171 (ch.11)]).

**Standardised cost (SR units per round trip)** [p.182 (ch.12)]

$$\text{Standardised cost} = \frac{2 \times C}{16 \times ICV}$$

where $C$ is the total cost per block in instrument currency, and $ICV$ is the daily instrument currency volatility ($ICV = \text{Block value} \times \text{Price volatility}$).

**Annual cost in SR units** [p.185 (ch.12)]

$$\text{Annual cost (SR)} = \text{Standardised cost} \times \text{Annual turnover}$$

Speed limits: $\leq 0.13$ SR/year for systems traders [p.187–188 (ch.12)]; $\leq 0.08$ SR/year for asset allocators and semi-auto traders [p.196 (ch.12)].

**EWMAC decay parameter** [p.283 (appendix B)]

$$A = \frac{2}{L + 1}$$

Recursive EWMA formula [p.283 (appendix B)]:

$$E_t = A \times P_t + (1-A) \times E_{t-1}$$

Volatility-adjusted EWMAC forecast [p.283–284 (appendix B)]:

$$\text{Raw crossover} = E_{fast} - E_{slow}$$

$$\text{Forecast} = \text{scalar} \times \frac{E_{fast} - E_{slow}}{\sigma_{price\text{-}points}}$$

Capped at $[-20, +20]$. Forecast scalars from Table 49 [p.285 (appendix B)]:

- EWMAC 2,8: scalar = 10.6 [p.285 (appendix B)]
- EWMAC 4,16: scalar = 7.5 [p.285 (appendix B)]
- EWMAC 8,32: scalar = 5.3 [p.285 (appendix B)]
- EWMAC 16,64: scalar = 3.75 [p.285 (appendix B)]
- EWMAC 32,128: scalar = 2.65 [p.285 (appendix B)]
- EWMAC 64,256: scalar = 1.87 [p.285 (appendix B)]

**Carry forecast calculation** [p.288 (appendix B)]

$$\text{Raw carry} = \frac{\text{Net expected return in price units}}{\text{Annualised} \, \sigma_{price\text{-}points}}$$

$$\text{Forecast} = 30 \times \text{Raw carry}$$

Carry forecast scalar is **30**; the raw carry is effectively an annualised Sharpe ratio [p.288 (appendix B)].

**Achievable SR benchmarks** [p.46–47 (ch.2)]

- Single equity long only: SR ≈ 0.15 [p.46 (ch.2)]
- Equity index (S&P 500): SR ≈ 0.20 [p.46 (ch.2)]
- Multi-country equities: SR ≈ 0.25 [p.46 (ch.2)]
- Multi-asset static portfolio: SR ≈ 0.40, maximum for asset allocators [p.46 (ch.2)]
- Single futures instrument with EWMAC: SR ≈ 0.40 [p.47 (ch.2)]
- Highly diversified systems trader (maximum realistic): SR ≈ 1.0 [p.47 (ch.2)]

**Forecast diversification multiplier (FDM) look-up values** [p.131, table 18 (ch.8)]

- 2 uncorrelated forecasts ($\rho$=0): FDM = 1.41 [p.131 (ch.8)]
- 2 forecasts at $\rho$=0.5: FDM = 1.15 [p.131 (ch.8)]
- 4 uncorrelated forecasts ($\rho$=0): FDM = 2.0 [p.131 (ch.8)]
- 10 uncorrelated forecasts ($\rho$=0): FDM = 3.2, capped in practice at 2.5 [p.131–133 (ch.8)]

---

### Algorithms and Pseudocode

**Full modular framework pipeline** [p.98–100 (ch.5)]

```python
# Stage A: Instruments [ch.6]
# Select tradeable instruments (futures, ETFs, spread bets)
# Exclude: pegged currencies, very low volatility, too large for account
# Require >= 4 blocks at maximum forecast 20

# Stage B: Forecasts per instrument-rule variation [ch.7]
# raw = signal() e.g. EWMAC crossover or carry
# vol_adj = raw / sigma_price_points
# forecast = scalar * vol_adj
# capped_forecast = clip(forecast, -20, +20)  # expected abs value = 10

# Stage C: Combined Forecast per instrument [ch.8]
# combined_raw = sum(weight_i * forecast_i for each rule i)
# combined = combined_raw * FDM
# combined_capped = clip(combined, -20, +20)

# Stage D: Volatility Targeting [ch.9]
# SR_realistic cap: 1.0 (staunch systems) / 0.5 (semi-auto) per [p.146, ch.9];
# starting assumption for semi-auto = 0.20 per Carver. No explicit formula given.
# sigma_target_pct = SR_realistic / 2  # Half-Kelly
# daily_cash_target = capital * sigma_target_pct / 16

# Stage E: Position Sizing [ch.10]
# ICV = block_value * price_vol_pct * fx_rate
# volatility_scalar = daily_cash_target / ICV
# subsystem_position = volatility_scalar * combined_capped / 10

# Stage F: Portfolio Positions [ch.11]
# portfolio_position = subsystem_position * instrument_weight * IDM
# rounded = round(portfolio_position)
# if abs(rounded - current) >= 0.1 * abs(rounded): trade to rounded
```

**EWMAC rule computation** [p.282–285 (appendix B)]

```python
# Input: price series P, Lfast, Lslow (e.g. 2 and 8)
# sigma_price_points = daily std dev of price changes (not %)

Afast = 2 / (Lfast + 1)   # decay param for fast EWMA
Aslow = 2 / (Lslow + 1)   # decay param for slow EWMA

Efast = P[0]; Eslow = P[0]
for t in range(1, N):
    Efast = Afast * P[t] + (1 - Afast) * Efast
    Eslow = Aslow * P[t] + (1 - Aslow) * Eslow

raw_crossover = Efast - Eslow
vol_adj = raw_crossover / sigma_price_points
forecast = scalar * vol_adj
capped_forecast = max(-20, min(20, forecast))
```

**Handcrafting portfolio weights** [p.78–85 (ch.4)]

```
Step A: Group instruments by correlation
        (same sector > same country > same asset class)
Step B: For each small group, look up equal-risk weights from Table 8
        based on average pairwise correlation
Step C: For groups-of-groups, apply Table 8 again at next level
Step D: Final weight = product of weights at each hierarchy level
Step E: Optional SR adjustment via Table 12
        (only if >10 years data; do NOT adjust if <10 years data)
```

**Semi-automatic trader stop-loss rule** [p.212 (ch.13)]

```
Parameters: X=4 (sigma multiplier from tracking extreme)
            sigma_price_points = daily std dev in price units

tracking_extreme = entry_price  # highest (long) or lowest (short) since entry

each bar:
    if long:
        tracking_extreme = max(tracking_extreme, current_price)
        stop_level = tracking_extreme - X * sigma_price_points
        if current_price <= stop_level: CLOSE POSITION
    if short:
        tracking_extreme = min(tracking_extreme, current_price)
        stop_level = tracking_extreme + X * sigma_price_points
        if current_price >= stop_level: CLOSE POSITION
```

NOTE: The action on stop trigger is to CLOSE the position only [p.212 (ch.13)]. Automatic reversal (exit long and enter short, or vice versa) belongs to the "A-and-B" mechanical system described in appendix B [p.281–282 (appendix B)], which Carver explicitly does NOT recommend for real trading.

---

### Pitfalls and Anti-patterns

- **[p.60, p.68–70, ch.3]**: Testing > 5 rule variations per idea with < 10 years of data almost guarantees selecting spurious rules. Table 4 (printed p.60): 50 rules, 5 years data → required SR threshold of 1.5 to keep false-positive rate below 5%; p.68–70 discusses the implications.
- **[p.58–59, ch.3]**: Selecting the best of 90 "early loss taker" system variations (stop-loss B and profit-target A parameters) on 1-year rolling windows gave SR = 0.07 (worse than random). Using all 90 equally weighted gave SR = 0.33. Over-selection destroys performance.
- **[p.47, ch.2]**: Negative-skew strategies appear to have very high Sharpe ratios until catastrophic loss. An imaginary strategy returning 100%/65% alternating had SR = 4.6 pre-blowup; even after losing 100% in year 21, the 21-year SR was still 1.7 — masking extreme negative skew. The SR of LTCM (which blew up in 1998) was also around 4.6 pre-blowup [p.47 (ch.2)].
- **[p.142–143, ch.9]**: Extreme leverage with low-volatility instruments is lethal. At the start of the day of the January 2015 CHF appreciation, "the natural risk of holding a position in EUR/CHF was tiny, at around 1% a year" [p.142 (ch.9)]. Achieving a 50% annualised volatility target would have required 50× leverage (50%/1%=50×). Only those with leverage of 7× or less survived the day, implying a maximum achievable 7% volatility target [p.143 (ch.9)].
- **[p.55, ch.3]**: "Ideas first" is also vulnerable to over-fitting via look-ahead bias — only rules already known to work in the literature are tested, which is implicit selection.
- **[p.72–77, ch.4]**: Single-period Markowitz optimisation produces extreme, unstable weights. In a NASDAQ/S&P/Bond example, NASDAQ was allocated 0% in-sample. Bootstrapping and handcrafting both produced near-equal, sensible weights.
- **[p.17–18, ch.1]**: Overriding the system during drawdown (meddling) is the most destructive behaviour. Humans take losses personally and intervene precisely when the system should be trusted most.
- **[p.85, ch.4]**: In-sample single-period Markowitz SR = 0.84 versus rolling OOS = 0.30 — in-sample optimisation tripled apparent performance through data mining.
- **[p.170, ch.11]**: Correlation instability: in a crisis, correlations jump higher, reducing diversification benefit and potentially inflating position sizes calculated under low-correlation assumptions.
- **[p.146, ch.9]**: Never use a back-tested SR above 1.0 (staunch systems traders) or 0.5 (semi-automatic traders) to set your volatility target, even if the back-test shows higher numbers.

---

---

## From `books/stocks_on_the_move.md`

### Explicit Trading Rules

- **RULE [p.98]**: Only trade on Wednesdays. All calculations use daily data, but decisions happen once per week. The day of the week is arbitrary — pick any day.
- **RULE [p.98]**: Rank S&P 500 stocks by (annualized 90-day exponential regression slope) x R^2.
- **RULE [p.98]**: Disqualify any stock trading below its 100-day moving average.
- **RULE [p.98]**: Disqualify any stock with a single-day move > 15% in the past 90 days.
- **RULE [p.98-99]**: Open new positions ONLY if the S&P 500 Index is above its 200-day moving average. If below, do not buy; hold existing positions (slow scale-out as they fall out of the ranking).
- **RULE [p.98]**: Position size = `AccountValue x 0.001 / ATR20`. Target daily impact per stock = 10 bps.
- **RULE [p.99]**: Build the initial portfolio by buying top-ranked non-disqualified stocks until cash runs out.
- **RULE [p.99, p.110]**: Every Wednesday — sell holdings that (a) rank outside the top 20% (e.g. rank > 100 in S&P 500), (b) dropped below the 100d MA, (c) had a >15% gap, or (d) left the index.
- **RULE [p.99]**: Every second Wednesday — recalculate target position sizes using current ATR and current account value; adjust if deviation is significant.
- **RULE [p.94]**: Do NOT use stop-losses. Exit is governed purely by ranking deterioration, trend breach, gap, or index exit.
- **RULE [p.96]**: Do NOT use trailing stops. They keep stale underperformers and lock in sideways drifters.
- **NEVER [p.94-95]**: Do not sell a holding just because the index drops below the 200d MA — only stop adding new positions. Existing holdings exit on their own criteria.
- **NEVER [p.68]**: Do not rank stocks by a single simple measure like "% above 200d MA" — it ignores volatility and rewards single-day jumps (e.g. takeovers) [p.68-69].
- **NEVER [p.83-85]**: Do not use equal-cash weighting. It tilts the portfolio toward the most volatile names.

### Formulas / Equations

**Annualized Exponential Regression Slope** [p.70-72, p.77]

Given a series of closing prices $P_t$ over $N = 90$ trading days, compute the linear regression slope $m$ of $\ln(P_t)$ vs. $t$:

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

### Algorithms and Pseudocode

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

### Pitfalls and Anti-patterns

- [p.219-220] **Do not optimize parameters.** "Optimizations are evil and out to kill you." Clenow states he picked all numbers (200d, 100d, 90d, 15%, 10bps) without optimization; a result like "237-day MA is optimal" is curve-fit and has no predictive value.
- [p.82, p.104] **Do not buy stocks with large recent gaps (>15% in past 90d).** These are usually takeover announcements, not genuine momentum — the stock is dead money afterwards.
- [p.238-239] **Survivorship bias kills simulations.** Using current S&P 500 constituents for a 10-year backtest creates fake outperformance because current members are selected BECAUSE they rose. You MUST use point-in-time membership and include delisted stocks.
- [p.239] **Missing cash dividends makes total returns meaningless over time.** Handle via dividend factors or as cash injections.
- [p.239-240] **Single-strategy single-instrument backtesting software is useless.** It must handle full portfolio semantics (multiple positions, rebalancing, cross-sectional ranking).
- [p.91-92] **Volatility is non-stationary.** A position sized once and left alone drifts to random risk — ATR doubling (e.g. Monster, Aug 2014) doubles your risk allocation if you do not rebalance.
- [p.63-65] **Do not hold momentum stocks through a bear market.** Correlations go to 1, diversification is illusory, and the momentum effect breaks down.
- [p.67-69] **Do not pick stocks by visual chart inspection or familiarity.** Discretionary pattern-matching is inconsistent day-to-day.
- [p.229-230] **Do not hold fewer than 10 stocks.** Event risk (single-stock shock) dominates; "element of luck becomes too large."
- [p.231] **Do not hold 40+ stocks (too broad).** Simulations worsen, it becomes impractical at low capital, and you lose the rebalance effect.

---
