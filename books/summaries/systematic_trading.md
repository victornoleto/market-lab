# Systematic Trading: A unique new method for designing trading and investing systems

## Metadata
- **Author:** Robert Carver [p.2 (frontmatter)]
- **Year:** 2015
- **Publisher:** Harriman House Ltd
- **Pages:** 326
- **ISBN:** 9780857194459 (hardback); 9780857195005 (eBook) [p.5 (copyright page)]
- **Main focus:** A modular, volatility-standardised framework for designing systematic trading and investing systems for futures, ETFs and spread bets, covering forecasting, position sizing, portfolio construction and cost control.

---

## 1. Core Thesis
The book's central thesis is that the most important source of underperformance — for amateurs and professionals alike — is not a failure to find better trading rules, but a failure to design the surrounding system correctly: wrong position sizing, overtrading, and over-fitting kill more accounts than bad forecasts do [ch.1, p.7].

Carver's solution is a modular, volatility-standardised framework that separates (i) the trading rule/forecast, (ii) the volatility target, and (iii) the position sizing arithmetic. Because all three layers are volatility-standardised, the same framework works for any rule, any instrument and any account size. The book is structured around three archetypal users: the *asset allocating investor* (static portfolio, no forecasts, ETFs), the *semi-automatic trader* (discretionary forecasts within a systematic risk framework, spread bets), and the *staunch systems trader* (fully systematic rules, futures) — all sharing the same core pipeline [p.9–11 (preface)].

---

## 2. Main Concepts
- **Volatility standardisation** — Adjusting the returns (and forecasts) of different assets so they have the same expected risk (daily standard deviation). The single most powerful technique in the framework, enabling the same trading rule to be applied generically across all instruments [p.40 (ch.2)].
- **Forecast** — A scaled number, positive meaning buy and negative meaning sell, proportional to the expected risk-adjusted return (i.e., the expected Sharpe ratio). Expected average absolute value is **10**; hard-capped at **±20** [p.112–114 (ch.7)].
- **Combined forecast** — A weighted average of individual rule forecasts using *forecast weights*, then multiplied by a *forecast diversification multiplier* (FDM) to restore the expected absolute value to 10, and then capped at ±20 [p.129–133 (ch.8)].
- **Volatility target (percentage)** — The desired annualised standard deviation of portfolio returns as a percentage of trading capital. Set once using the Half-Kelly criterion and not changed except downward when truly intolerable losses occur [p.137–148 (ch.9)].
- **Volatility scalar** — The number of instrument blocks to hold if the entire capital is invested in one instrument with a constant forecast of +10. Equal to the daily cash volatility target divided by the instrument value volatility [p.159 (ch.10)].
- **Subsystem position** — How many blocks to hold given the current forecast: `volatility_scalar × forecast / 10` [p.160 (ch.10)].
- **Instrument weight** — The fraction of total trading capital allocated to each instrument's trading subsystem. Found via handcrafting or bootstrapping [p.167–168 (ch.11)].
- **Instrument diversification multiplier (IDM)** — Correction factor applied to all portfolio positions to compensate for the risk reduction from holding imperfectly correlated instruments. Maximum recommended value: **2.5** [p.170–171 (ch.11)].
- **Position inertia** — Not trading when the rounded target position is within 10% of the current position. Significantly reduces turnover and costs without affecting pre-cost performance [p.174 (ch.11)].
- **Turnover** — Number of round trips (buy + sell of one average-sized position) per year. The key speed metric for cost management [p.185 (ch.12)].
- **Standardised cost (SR units)** — Round-trip cost as a fraction of annualised SR: `(2 × cost_per_block) ÷ (16 × instrument_currency_volatility)`. Enables cost comparison across instruments regardless of price level [p.182 (ch.12)].
- **Law of Active Management** — SR of a strategy is proportional to the square root of the number of independent bets per year, implying diversification across instruments is the best source of additional return [p.42 (ch.2)].
- **EWMAC rule** — Exponentially Weighted Moving Average Crossover: buy when the fast EWMA is above the slow EWMA, with the crossover volatility-standardised and scaled to an average absolute forecast of 10. Six variants: 2:8, 4:16, 8:32, 16:64, 32:128, 64:256 [p.118–119 (ch.7), p.282–284 (appendix B)].
- **Carry rule** — Buys assets with high expected carry (yield minus funding cost) and sells those with negative carry; negative-skew complement to EWMAC. For futures: annualised carry = (current contract price − nearer contract price) / distance in years [p.119 (ch.7), p.285–287 (appendix B)].
- **Handcrafting** — A simple, pencil-and-paper portfolio optimisation method that groups correlated assets hierarchically and assigns weights from a look-up table, bypassing the instability of classic Markowitz optimisation [p.78–85 (ch.4)].
- **Bootstrapping** — Averaging many optimisations over different data windows to produce stable, non-extreme portfolio weights. The gold standard for weight estimation when code is available [p.75–77 (ch.4)].
- **Skew** — Positive-skew strategies (trend following) have frequent small losses and occasional large gains; negative-skew strategies (carry, market making) have frequent small gains and occasional catastrophic losses. Skew must be understood before setting volatility targets [p.32–35 (ch.2)].
- **Overconfidence / meddling** — The main enemy of systematic trading. Humans override systems precisely when the system should be trusted most [p.17–18 (ch.1)].
- **Ideas first vs. data first** — Generating a hypothesis before looking at data (ideas first) is safer against over-fitting than mining data for patterns (data first) [p.26–27 (ch.2)].

---

## 3. Formulas / Equations
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

## 4. Algorithms and Pseudocode
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

## 5. Explicit Trading Rules
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

## 6. Pitfalls and Anti-patterns
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

## 7. Sensitive Parameters
- **Volatility look-back: 25 business days (default)** [p.155–157, ch.10]: 25-day simple moving average of daily returns. Trade-off between responsiveness and stability, equivalent to 36-day EWMA half-life. Justified economically, not optimised in backtest.
- **ETF / asset allocator look-back: 20 weeks** [p.196–197, ch.12]: Table 36 shows turnover drops from 1.6 to 0.4 round trips/year vs 25-day look-back. Chosen to reduce turnover-driven costs, not for performance.
- **Forecast cap: ±20** [p.114, ch.7]: Forecasts beyond ±20 add little information and increase turnover and risk unnecessarily. Not data-mined.
- **IDM maximum: 2.5** [p.170–171, ch.11]: Conservative cap to guard against optimism in assumed pairwise correlations. Justified as a conservative bound, not fitted.
- **EWMAC look-back ratio: 4:1 (fast:slow)** [p.284, appendix B]: Fixed ratio selected on artificial data (not real data) to avoid overfitting. Performance was flat between ratios 2:1 and 6:1, so 4:1 was chosen. Confirmed reasonable on real data ex post.
- **EWMAC look-back pairs: 2:8, 4:16, 8:32, 16:64, 32:128, 64:256** [p.284, appendix B]: Adjacent pairs have correlation 0.90 (Table 57); adding intermediate values would give correlations > 0.95 and add no independent information. Beyond 64:256, holding periods become excessively long.
- **Carry forecast scalar: 30** [p.288, appendix B]: Derived from data across a large number of markets and asset classes, not optimised on any single instrument or period.
- **Semi-automatic stop-loss X = 4** [p.212, ch.13]: Chosen to give average holding period of 6.5 weeks and turnover ≈ 8 round trips/year. Not selected by performance — chosen by desired turnover profile.
- **Position inertia threshold: 10%** [p.174, ch.11]: Informal heuristic, not optimised. Justified as "too small a trade to be worth the transaction cost".
- **SR_realistic cap: 1.0 (staunch systems traders), 0.5 (semi-automatic traders)** [p.146, ch.9]: Conservative ceilings from experience. Staunch systems traders: any back-tested SR > 1.0 is treated as evidence of overfitting or look-ahead bias. Semi-automatic traders: SR of 0.5 is described as "the maximum safe achievable level" [p.146 (ch.9)].
- **FDM maximum: 2.5** [p.133, ch.8]: Same conservative cap as IDM — guards against over-estimation of forecast independence.

---

## 8. Key Literal Quotes
> "I call this process of interference by our internal monologue meddling. Meddling is due to the biggest cognitive bias of all: overconfidence." — [p.17 (ch.1)]

> "I also believe finding the best trading rules is less important than designing your trading system in the correct way. In particular you need to avoid the serious crime of over-fitting." — [p.48 (ch.2)]

> "The best systematic traders will be diligent when creating their systems, but lazy when running them. Put the hard work into designing a safe system that you are comfortable with and then do not change it." — [p.260 (epilogue)]

> "Diversification is the investor's best friend. But it's pointless diversifying if you then allow one part of your system to dominate your returns." — [p.130 (ch.8)]

> "Use Half-Kelly: your maximum percentage volatility target should be half what you pessimistically expect your Sharpe ratio to be." — [p.260 (epilogue)]

---

## 9. Cross-references to Other Books in This Knowledge Base
N/A — This summary was produced as the primary detailed extraction of this book. Cross-references to other summaries in this knowledge base will be validated and added in subsequent passes.

Connections anticipated for future validation:
- Kelly criterion / position sizing: connects to `math_money_mgmt.md` (Ralph Vince).
- Trend following (EWMAC): connects to `trading_evolved.md` and `stocks_on_the_move.md` (Clenow).
- Portfolio optimisation (bootstrapping vs. Markowitz): connects to `ml_for_algo_trading.md`.
- Carry rule across asset classes: connects to `risk_parity.md`.
- Systematic trading rules design: connects to `trading_systems_methods.md` (Perry Kaufman).
