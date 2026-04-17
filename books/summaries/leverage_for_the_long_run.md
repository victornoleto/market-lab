# Leverage for the Long Run: A Systematic Approach to Managing Risk and Magnifying Returns in Stocks

## Metadata
- **Autor:** Michael A. Gayed, CFA [p.?] (cover/abstract page, no printed page number)
- **Ano:** 2016 (updated through December 31, 2020)
- **Editora:** Lead-Lag Publishing, LLC
- **Páginas:** 23 (printed); 24 PDF pages
- **ISBN:** N/A — SSRN working paper, no ISBN. Available at https://ssrn.com/abstract=2741701
- **Foco principal:** A systematic Leverage Rotation Strategy (LRS) that employs leveraged S&P 500 exposure when the index is above its Moving Average and rotates to Treasury bills when below, demonstrating superior absolute and risk-adjusted returns vs. buy-and-hold and constant-leverage strategies over 1928–2020.

## 1. Core Thesis

The paper's central thesis is that **volatility is the enemy of leverage, and Moving Averages are an effective systematic signal for identifying low-volatility, high-streak-potential regimes** — precisely the conditions under which daily re-leveraging is beneficial [p.7]. The popular belief that daily-leveraged products decay to zero over time is characterized as a myth: "performance over time has nothing to do with time itself, but rather: 1) the behavior of the underlying asset in its overall trend, 2) the path of daily returns (streaks versus seesawing action), and 3) whether the regime under which leverage is utilized is high or low volatility" [p.7].

The second pillar is that Moving Averages function primarily as **downside protection tools**, not return-enhancement tools in bull markets [p.8]. When employed in a Leverage Rotation framework — leveraged equity above the MA, Treasury bills below — the combined strategy achieves higher absolute returns, better risk-adjusted metrics (Sharpe/Sortino), lower drawdowns, and lower beta than either buy-and-hold or constant-leverage approaches, across all leverage factors (1.25x, 2x, 3x) tested from October 1928 through December 2020 [p.17, Table 8].

## 2. Main Concepts

- **Constant Leverage Trap** — The mathematical destruction of capital that occurs when a daily re-leveraged product seesaws between positive and negative returns at high volatility: after a loss the exposure is reset to a lower asset base (reducing effective exposure ahead of the next gain), and after a gain it is reset to a higher base (increasing exposure ahead of the next loss). Named and cited from Trainor Jr. (2011) [p.4].

- **Leverage Rotation Strategy (LRS)** — Systematic rule: hold leveraged S&P 500 when the index closes above its Moving Average; rotate to Treasury bills when the index closes below. Tested across 1.25x, 2x, and 3x leverage, with 10-, 20-, 50-, 100-, and 200-day MA periods [p.13].

- **Volatility Regime** — Annualized rolling volatility used as a state variable. Below ~40% annualized, daily leveraged products track near their leverage multiple with minimal decay; above 40% (especially above 70%), compounding losses accelerate and positive returning underlying weeks can produce negative leveraged returns [p.5–6].

- **Path Dependency** — The compounded leveraged return depends not just on the final unleveraged return but on the sequence of daily returns. Two paths with identical cumulative returns but different volatility profiles produce materially different leveraged outcomes [p.4–5].

- **Autocorrelation / Streaks** — Above its Moving Average, the S&P 500 exhibits positive autocorrelation (consecutive up-days more likely), which is the precondition for leveraged strategies to perform well; below the MA, alternating seesawing dominates. Behavioral explanation: low volatility → investor underreaction → streaks; high volatility → overreaction → back-and-forth [p.6–7].

- **Moving Average as Volatility Indicator** — The SMA functions primarily as a volatility regime indicator rather than a trend-following signal. When price is above the MA, forward volatility is lower; when below, forward volatility is higher — confirmed across all MA periods (10-day through 200-day) from 1928 [p.9]. S&P 500 trades below its 200-day MA 68.2% of time during recessions vs. only 19.4% during expansions [p.9].

- **Leverage Aversion** — Behavioral and structural bias: institutional constraints (pension funds, mutual funds, endowments cannot use leverage by mandate), margin-call costs, and availability heuristic (extreme loss events recalled first) combine to create a persistent inefficiency [p.2].

- **Risk of Ruin** — Drawdown path where an investor abandons the strategy before recovery. The 3x buy-and-hold fell to -99.9% (April 1942), requiring a 174,037% gain to recover; realistically means permanent loss for any investor who exited [p.19–20].

- **Simple Moving Average (SMA)** — Unweighted mean of the prior n daily closing prices of the total return series (including dividends). The paper limits analysis to SMA only, using daily closing prices of the total return S&P 500 [p.8, footnote 15].

## 3. Formulas / Equations

**Daily Re-Leveraging Compounding — Core Mechanism** [p.4]

The paper describes the constant leverage trap mechanism in prose with supporting tables. The implicit compounding formula for a $L$x daily-leveraged product is:

$$R_{\text{leveraged, cumulative}} = \prod_{t=1}^{T}(1 + L \cdot r_t) - 1$$

where $r_t$ is the daily return of the underlying (S&P 500 total return). This formula drives all empirical tables in the paper.

> "Daily re-leveraging combined with high volatility creates compounding issues, often referred to as the 'constant leverage trap.' When the path of returns is not trending but alternating back and forth between positive and negative returns (seesawing action), the act of re-leveraging is mathematically destructive." — [p.4]

- $L$ = leverage factor (1.25, 2, or 3 in the paper's tests)
- $r_t$ = daily return of underlying S&P 500 total return index
- Key insight: for the same cumulative unleveraged return, lower volatility paths produce higher leveraged cumulative returns.

**Note on closed-form decay formula:** No Perold-Sharpe style closed-form formula appears as a typeset equation in this paper. The paper relies on Monte Carlo simulation (3,000 annual paths per volatility level, 252 trading days, mean 10%) and empirical tables rather than a symbolic expression [p.5, footnote 11].

**Volatility-Leverage Relationship (Monte Carlo)** [p.6]

> "At low volatility levels, the decay is minimal, while at higher volatilities (above 40%), a daily leveraged strategy is very likely to lose over the course of a year." — [p.6]

- Simulation: 3,000 annual return paths per volatility level, 252 trading days, mean return 10%
- Volatility levels tested: 0%, 10%, 40%, 70%, 100% [p.5, footnote 11]
- Below 40% annualized volatility: minimal decay, leveraged strategy likely profitable
- Above 40%: increasing probability of loss; above 70%: strong likelihood of loss even with positive drift

**Growth of $1 — Leveraged Buy and Hold (Oct 1928 – Dec 2020, no leverage cost)** [p.3, Table 1]

> "We observe this in Table 1, where the 3x leveraged cumulative return since 1928 is an astonishing 681 times that of the unleveraged S&P 500." — [p.3]

| Strategy | Growth of $1 | Multiple vs. 1x |
|---|---|---|
| S&P 500 (1x) | $4,059 | 1 |
| S&P 500 1.25x | $19,313 | 5 |
| S&P 500 2x | $591,035 | 146 |
| S&P 500 3x | $2,763,322 | 681 |

**Synthetic Leveraged Return for Pre-ETF Backtests** [p.16, footnotes 22–23]

The paper's methodology for pre-UPRO (pre-2009) simulation:

> "we will assume for the purposes of this section a leverage fee of 1% per year, which approximates the current expense ratio for the largest leveraged ETFs." — [p.16]

Applied daily: $r_{\text{synth},t} = L \times r_{\text{SPX\_TR},t} - \frac{0.01}{252}$ per trading day, using S&P 500 Total Return Index (Gross Dividends) from Bloomberg [p.3, footnote 9]. For post-2021 modeling, substitute 0.0095 for 0.01 (0.95% actual UPRO expense ratio as of 2021 [p.16, footnote 23]).

**LRS Performance Summary — 200-day MA, Oct 1928–Dec 2020** [p.17, Table 8]

> "as compared to a buy and hold of the S&P 500 and leveraged buy and hold, the LRS achieves: 1) improved absolute returns, 2) lower annualized volatility, 3) improved risk-adjusted returns (higher Sharpe/Sortino), 4) lower maximum drawdowns, 5) reduced Beta, and 6) significant positive alpha." — [p.17]

| Metric | S&P 500 | 2x BuyHold | 3x BuyHold | 2x LRS (200d) | 3x LRS (200d) |
|---|---|---|---|---|---|
| Annual Return | 9.4% | 14.3% | 16.2% | 19.0% | 26.7% |
| Annual Volatility | 18.9% | 37.8% | 56.7% | 24.9% | 37.3% |
| Sharpe Ratio | 0.32 | 0.28 | 0.22 | 0.61 | 0.61 |
| Sortino Ratio | 0.57 | 0.65 | 0.71 | 0.99 | 1.05 |
| Max Drawdown | -86.2% | -98.8% | -99.9% | -78.7% | -92.2% |
| Annual Alpha | 0.0% | -1.0% | -1.0% | 11.0% | 17.5% |

**LRS with Actual ETFs (SSO/UPRO), Jul 2009 – Dec 2020** [p.21, Table 12]

> "The performance figures are slightly below the theoretical computed performances using the S&P 500 index total returns, likely due to a negative leverage premium (performance lag) in the leveraged ETFs." — [p.21]

| Metric | S&P 500 | UPRO (3x BH) | UPRO (3x 200d LRS) |
|---|---|---|---|
| Annual Return | 15.3% | 35.4% | 24.2% |
| Annual Volatility | 17.5% | 51.9% | 36.8% |
| Sharpe Ratio | 0.85 | 0.67 | 0.64 |
| Max Drawdown | -33.8% | -76.8% | -51.2% |
| Annual Alpha | 0.0% | -1.6% | 8.0% |

## 4. Algorithms and Pseudocode

**Leverage Rotation Strategy (LRS) — Core Signal Logic** [p.13]

```
Input: S&P 500 total return daily close prices,
       MA_period ∈ {10, 20, 50, 100, 200} days (default 200),
       leverage_factor L ∈ {1.25, 2, 3},
       leverage_fee_annual = 0.01  # 1% per year; or 0.0095 for post-2021

For each trading day t:
    SMA_t = mean(close[t - MA_period + 1 : t])  # simple MA of prior n days

    if close[t] > SMA_t:
        signal = "RISK_ON"
        position = L * r_SPX_TR[t] - (leverage_fee_annual / 252)
    else:
        signal = "RISK_OFF"
        position = r_TBill_3month[t]  # 3-month Treasury bill daily return

    portfolio_return[t] = position

Output: cumulative portfolio return, Sharpe, Sortino, max drawdown, beta, alpha
```

Source: "When the S&P 500 Index closes above its Moving Average, rotate into the S&P 500 and use leverage to magnify returns. When the S&P 500 Index closes below its Moving Average, rotate into Treasury bills to manage risk." [p.13]

**Modern ETF Implementation** [p.21]

```
ETF Implementation of 200-Day LRS:
    Data source: S&P 500 index daily close (total return)
    Signal: if S&P 500 close > SMA(200), RISK_ON; else RISK_OFF
    RISK_ON instruments: SSO (2x S&P 500 ETF) or UPRO (3x S&P 500 ETF)
    RISK_OFF instrument: Cash
      (NOT T-Bill ETF like BIL — paper explicitly uses cash for RISK_OFF)
    Rebalance: Daily check, trade at close on signal change
    Average rotations: ~5 per year for 200-day MA
```

Source: "we hold cash during risk-off periods (and not a T-Bill tracking product, e.g. the 1-3 Month Treasury ETF 'BIL')" [p.21]

**Volatility Regime Check (MA Periods Tested)** [p.14, Table 6]

```
MA_periods = [10, 20, 50, 100, 200]  # all tested, all robust
For each MA_period:
    Run LRS backtest (Oct 1928 – Dec 2020)
    Compute: annual_return, annual_vol, sharpe, sortino, max_dd, beta, alpha, avg_trades/yr
    # Results: all periods generate positive annual alpha (5.2-6.4%) vs unleveraged BH
    # Shortest (10d): 38 avg trades/yr, Sharpe 0.68
    # Longest (200d): 5 avg trades/yr,  Sharpe 0.59 (unleveraged), highest practicality
```

## 5. Explicit Trading Rules

- **RULE [p.13]**: LRS Signal — RISK ON: if S&P 500 daily close > SMA(MA_period), hold leveraged S&P 500 (1.25x, 2x, or 3x daily). RISK OFF: if S&P 500 daily close <= SMA(MA_period), rotate to Treasury bills (theoretical) or cash (ETF implementation).

- **RULE [p.16]**: Use 200-day Moving Average (SMA) as the primary MA period for LRS implementation. Justification: fewest transaction costs (~5 rotations/year), most widely referenced, applicable to both short-term traders and long-term investors.

- **RULE [p.21]**: In ETF implementation, use SSO (2x) or UPRO (3x) as RISK_ON instruments. Hold cash (not BIL or T-bill ETF) during RISK_OFF periods.

- **RULE [p.16, footnote 23]**: Apply a leverage fee (expense ratio) of 1% per year when modeling leveraged positions in backtests. As of 2021 the actual UPRO expense ratio is 0.95%.

- **RULE [p.5–6]**: Leverage is beneficial at volatility regimes below 40% annualized (sweet spot). Above 40%, the constant leverage trap dominates; above 70%, even positive-underlying weeks may produce negative leveraged weeks. The MA signal proxies for this regime.

- **RULE [p.8]**: SMA definition: unweighted mean of prior n daily closing prices of the total return series (inclusive of dividends). Use total return series, not price-only index.

- **RULE [p.14, Table 6]**: All five MA periods (10-, 20-, 50-, 100-, 200-day) generate positive annual alpha (5.2%–6.4%) vs. unleveraged buy-and-hold with Sharpe ratios of 0.58–0.68 vs. 0.32 for buy-and-hold. Shorter MAs: higher absolute return but higher turnover and whipsaw.

- **NEVER [p.20]**: Do not apply constant leverage (leveraged buy-and-hold) without a volatility regime filter. The 3x constant leverage produced drawdowns below -90% from October 1930 to March 1954, in October 2002, and October 2007 to August 2008 — near-certain risk of ruin for any real investor with finite drawdown tolerance.

## 6. Pitfalls and Anti-patterns

- **[p.4]** The "natural decay" myth of daily leveraged products: believing daily re-leveraging inherently destroys capital over time. Over the long run (1928–2020), the 3x daily leveraged S&P 500 generated 681x the unleveraged return with no cost assumption [Table 1]. Decay only occurs in high-volatility, seesawing regimes — it is not a structural property of daily leveraging.

- **[p.7–8, Table 4]** Treating Moving Averages as return-enhancement tools rather than downside-protection tools. In bull markets (1990–1998, 2002–2007, 2009–2018), the 200-day MA rotation strategy consistently underperforms buy-and-hold: e.g., Oct 2002–Oct 2007 the S&P 500 returned 120.6% while the 200-day MA rotation returned only 42.9%.

- **[p.15]** Judging the Moving Average strategy on absolute return alone leads to incorrect rejection. MA rule beats buy-and-hold in absolute return in only 49% of rolling 3-year periods but generates positive alpha in 69% of rolling 3-year periods. The MA's value is risk-adjusted, not absolute.

- **[p.19–20]** Risk of ruin from applying 3x leverage without a rotation filter. An investor in 3x constant-leverage at the September 1929 peak would have seen $10,000 fall to $5.74 by 1942. Recovery required a 174,037% gain and did not complete until January 1960. Any investor who exited before recovery would have suffered near-total permanent loss.

- **[p.4–5, Table 2]** High-volatility seesawing destroys leveraged returns even when the unlevered index finishes positive. In August 8–15, 2011 (annualized volatility >75%), the S&P 500 returned +0.51% but the 2x returned -0.14% and the 3x returned -2.02%.

- **[p.16, Table 7]** Leveraged buy-and-hold (no regime filter) produces negative annual alpha relative to unleveraged: -1.1% for 1.25x, -1.5% for 2x, -2.4% for 3x. Adding leverage without timing destroys risk-adjusted performance even at long horizons.

- **[p.21]** ETF implementation underperforms the theoretical simulation due to a "negative leverage premium (performance lag) in the leveraged ETFs." Model results (Tables 8–10) should be shaded downward for real-world ETF implementation. Example: theoretical 3x LRS 2009–2020 = 26.3% annual return; UPRO-based 3x LRS = 24.2% [p.21, Table 12].

- **[p.6, footnote 11]** The Monte Carlo simulation does not capture empirically observed positive autocorrelation in daily returns (consecutive up-days). Simulated results at low volatility are therefore conservative — actual low-volatility leveraged performance is likely better than the simulated worst case.

## 7. Sensitive Parameters

- **Moving Average Period — 200-day (SMA)** [p.16]: Recommended for LRS implementation. Justification: ~5 rotations/year (lowest transaction costs), most widely referenced in practice, robust across all periods tested. All MA periods (10- through 200-day) show similar Sharpe ratios (0.58–0.68) and positive annual alpha (5.2%–6.4%) [Table 6]. Low curve-fit risk: the paper explicitly states results are "robust to various leverage amounts, Moving Average time periods, and across multiple economic and financial market cycles" [p.1, abstract].

- **MA Periods Tested — 10, 20, 50, 100, 200 days** [p.14, Table 6]: Turnover ranges from 38 trades/year (10-day) to 5 trades/year (200-day). All generate similar risk-adjusted results. Parameter is not optimized for maximum return — any of these periods would be defensible.

- **Leverage Factors — 1.25x, 2x, 3x** [p.17, Table 8]: LRS Sharpe ratios 0.57, 0.61, 0.61 respectively vs. 0.32 for buy-and-hold. Max drawdowns -59.0%, -78.7%, -92.2% for 200-day LRS. Author does not designate an optimal level — choice depends on investor drawdown tolerance and risk of ruin threshold.

- **Leverage Fee / Expense Ratio — 1% per year (0.95% as of 2021)** [p.16, footnotes 22–23]: Applied as daily drag of fee/252 per leveraged day. Not curve-fitted — reflects actual ETF cost structure. Use 0.95% for UPRO in post-2021 models.

- **Volatility Threshold — 40% annualized** [p.5–6]: The boundary between the "sweet spot" (below 40%) and the danger zone (above 40%) for daily leveraged strategies. Derived analytically from Chart 1 (weekly observations of 3x vs. 1x returns across volatility bins) and Monte Carlo simulation. This is not a free parameter in the LRS — the MA signal implicitly serves as the regime gate.

- **Risk-Off Asset — 3-month Treasury bills (theoretical) or Cash (ETF)** [p.13, p.21]: Theoretical tests use T-bill total return data (Ken French library). Modern ETF implementation uses cash. The difference in risk-off yield between T-bills and cash is small in low-rate environments but may be material in high-rate regimes. The paper does not optimize this choice.

## 8. Key Literal Quotes

> "High volatility and seesawing action are the enemies of leverage while low volatility and streaks in performance are its friends." — [p.4]

> "The conclusion here is that the popular belief that leveraging results in decay over time is a myth, as performance over time has nothing to do with time itself, but rather: 1) the behavior of the underlying asset in its overall trend, 2) the path of daily returns (streaks versus seesawing action), and 3) whether the regime under which leverage is utilized is high or low volatility." — [p.7]

> "Viewing the Moving Average as a volatility indicator more so than a trend identifier helps explain how Moving Average strategies can underperform in strong equity bull markets." — [p.11]

> "As Jeremy Siegel notes in 'Stocks for the Long Run,' the 'major gain of the [Moving Average] timing strategy is a reduction in risk.'" — [p.8]

> "The 3x leveraged cumulative return since 1928 is an astonishing 681 times that of the unleveraged S&P 500." — [p.3]

## 9. Cross-references to Other Books in This Knowledge Base

N/A — Cross-references will be added in subsequent passes once other summaries are confirmed processed. Potential topical connections (flagged as unverified):

- Moving Average regime filter (price above/below SMA as risk signal) likely overlaps with trend-following or tactical asset allocation summaries if present in the base.
- The autocorrelation and momentum underpinning (Grinblatt and Moskowitz 2000) referenced here [p.7, footnote 12] connects to momentum literature.
- Risk of ruin and leverage factor selection connect to Kelly criterion and position sizing literature.

All three are flagged as unverified until corresponding summaries are confirmed in the base.
