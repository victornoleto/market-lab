# Risk Parity Fundamentals

## Metadata
- **Autor:** Edward E. Qian, PhD, CFA [p.xvii]
- **Ano:** 2016
- **Editora:** CRC Press / Taylor & Francis Group
- **Páginas:** 245
- **ISBN:** 978-1-4987-3880-4 (eBook PDF)
- **Foco principal:** Portfolio construction via balanced risk allocation across equity, interest rate, and inflation risk premiums — the theoretical and practical case for risk parity over traditional 60/40.

---

## 1. Tese Central

The central thesis is that traditional capital-weighted portfolios such as the 60/40 stock/bond allocation are misleadingly named "balanced" — they are in fact severely unbalanced in terms of risk, with 90%–95% of portfolio risk concentrated in equities [p.1–2, ch.1]. True diversification requires allocating risk equally (or proportionally) across independent risk premiums rather than allocating capital. Risk parity achieves this by inverting the process: start with a target risk allocation, derive portfolio weights, and apply leverage to reach the desired return level [p.10, ch.1].

The three primary risk premiums that must be balanced are: equity risk premium (rewarded by business cycle growth), interest rate risk premium (rewarded by lending over long horizons), and inflation risk "premium" (primarily a hedge via commodities and inflation-linked bonds) [p.17–18, ch.2]. A risk parity portfolio is superior precisely because these three premiums have low and sometimes negative correlations — each provides diversification exactly when the others struggle [p.69, ch.4]. The author coined the term "risk parity" in 2005 and launched a live risk parity strategy at PanAgora Asset Management in 2006 [p.xiii–xiv].

---

## 2. Conceitos-Chave

- **Risk contribution (variance decomposition)** — The share of a portfolio's total variance attributable to each component, calculated by assigning the component's variance plus half of its covariances with all other assets [p.3–5, ch.1]. For a 60/40 portfolio with equity vol 15% and bond vol 5%, stocks contribute ~92% of total risk and bonds only ~8% [p.5–6, ch.1].

- **Loss contribution ≈ risk contribution** — Mathematically provable (Qian 2006) that for a large portfolio loss $L$, each component's fractional loss contribution approximately equals its risk contribution: $L_s/L \approx p_s$ [p.7, ch.1]. Empirically confirmed on the 60/40 portfolio (S&P 500 / LT Government Bond), January 1926 – June 2004 [p.8, ch.1].

- **Naïve risk parity** — Weights assets by the inverse of their individual volatilities, ignoring pairwise correlations. Achieves equal risk contribution only when all pairwise correlations are identical. For a 3-asset example, naïve risk parity gives **65% bonds, 22% stocks, 13% commodities** while true ERC parity gives 68% bonds, 18% stocks, 14% commodities [p.11, ch.1].

- **True ERC (Equal Risk Contribution) risk parity** — Finds portfolio weights such that every asset contributes equally to total portfolio variance, fully accounting for the covariance matrix. For N > 2 assets, solved by trial and error or Excel Solver — no closed-form solution exists for the general case [p.10–11, ch.1].

- **ERC portfolio ≠ Risk Parity if assets are misclassified** — Applying ERC to 4 equity asset classes + 5 bond asset classes + 1 commodity (= 10 assets total) produces ~65% equity risk, 20% interest rate risk, 15% inflation risk — resembling a 60/40 portfolio [p.18, ch.2].

- **Three primary risk premiums ("colors")** — Equity risk premium, interest rate risk premium, inflation risk "premium." All other asset class exposures are combinations ("hybrids") of these three primary colors [p.17–18, ch.2].

- **HY bonds as equity in bond's clothing** — After correcting for illiquidity via annual return volatility, HY bonds (1984–2011) have virtually the same excess return (~4.87%), risk (~16.40%), and Sharpe ratio (~0.30) as large-cap equities [p.23–24, ch.2]. HY belongs in the equity risk bucket, not the interest rate bucket [p.25, ch.2].

- **Roll yield (commodities)** — Not a valuation metric analogous to bond yield or dividend yield. Rather, an accounting attribution between futures price change and spot price change. Empirically, price return dominated commodity returns in most decades; roll yield only explained a significant portion in 1991–2000 when prices were stationary [p.27–29, ch.2].

- **Currency risk premium** — Does not exist at a broad level. Currency exposures add substantial volatility with statistically insignificant returns across all base currencies (t-stat of 0.28 for USD investors, [p.37–38, ch.2]). Exception: currency carry trade is a factor premium (long high-yield / short low-yield currencies), highly correlated with equity market returns (correlation ≈ 0.52, [p.41, ch.2]).

- **Forward rates as predictors of future rates** — Forward rates have a persistent upward bias: they predicted rising rates 72% of the time while actual rates rose only 51% of the time over 1952–2013. Overall hit ratio: 39% [p.65–66, ch.3].

- **Bond return volatility = duration × yield volatility** — Duration alone is an incomplete risk measure for bonds. The combined effect of declining duration sensitivity (short-end near ZIRP) and low yield volatility means short-term bonds can have lower effective risk than duration implies [p.51–52, ch.3].

- **Risk-on / Risk-off (RORO)** — Regime where almost all risky assets move together (stocks and commodities correlation reached 0.71 in 2009–2012) while safe assets (USTs) have strongly negative correlation with risky assets (−0.58 to −0.53 in the same period) [p.80–81, ch.4].

- **Diversification return** — Difference between the geometric return of a fixed-weight portfolio and the weighted average of the geometric returns of its components. Always non-negative for long-only unlevered portfolios; can be negative for leveraged/inverse single-asset vehicles [p.109–110, ch.5].

- **Participation ratio (PRD)** — Upside and downside participation ratios of a portfolio relative to a benchmark. Risk parity has low downside participation ratio (similar to defensive strategies) but upside participation ratio close to 1 — unlike defensive strategies [p.103, ch.5].

- **Style analysis (Sharpe 1988/1992)** — Return-based regression of a fund's returns against asset class indices to derive effective style weights and risk allocations. Extended by Qian to leveraged portfolios [p.166–167, ch.7].

---

## 3. Fórmulas / Equações

**Portfolio Variance of Two-Asset Portfolio (e.g. 60/40)** [p.5, ch.1]

$$\sigma^2 = w_s^2 \sigma_s^2 + 2\rho w_s w_b \sigma_s \sigma_b + w_b^2 \sigma_b^2$$

Example: $w_s=0.6$, $w_b=0.4$, $\sigma_s=0.15$, $\sigma_b=0.05$, $\rho=0.2$ gives $\sigma \approx 9.60\%$.

**Variance Contribution of Asset $s$ (two-asset)** [p.5, ch.1]

$$\sigma_s^2 = w_s^2 \sigma_s^2 + \rho \cdot w_s w_b \sigma_s \sigma_b$$

The covariance term is split equally between the two assets.

**Percentage Risk Contribution** [p.5–6, ch.1]

$$p_s = \frac{\sigma_s^2}{\sigma_s^2 + \sigma_b^2}, \quad p_b = \frac{\sigma_b^2}{\sigma_s^2 + \sigma_b^2}$$

For the 60/40 example: $p_s \approx 92\%$, $p_b \approx 8\%$.

**Risk Contribution ≈ Loss Contribution** [p.7, ch.1]

$$\frac{L_s}{L} \approx p_s, \quad \frac{L_b}{L} \approx p_b$$

Valid for both standard deviation and VaR as risk measure (Qian 2006).

**Financial Futures Spot-Forward Parity** [p.28, ch.2]

$$F = S \cdot e^{(r - c)(T - t)}$$

- $S$ = spot price, $F$ = futures price, $r$ = short-term interest rate
- $c$ = dividend yield (equities) or convenience yield (commodities), $T-t$ = time to maturity
- If $r > c$: contango ($F > S$). If $r < c$: backwardation ($F < S$).

**Forward Rate Derivation from Spot Yields** [p.60, ch.3]

$$(1 + y_1)(1 + f_{1,1}) = (1 + y_2)^2$$

Solving for the 1-year forward rate 1 year hence:

$$f_{1,1} = \frac{(1 + y_2)^2}{(1 + y_1)} - 1$$

When the yield curve slopes up ($y_2 > y_1$): always $f_{1,1} > y_2$. Numerical example with $y_1 = 0.10\%$, $y_2 = 0.50\%$: $f_{1,1} = 0.90\%$ [p.60, ch.3].

**Diversification Return (two-asset fixed-weight portfolio)** [p.110, ch.5]

$$e_v = 0.5\left(w_1^2\sigma_1^2 + w_2^2\sigma_2^2 - \sigma_p^2\right) = -0.5 \cdot w_1 w_2 \cdot 2\rho_{12}\sigma_1\sigma_2$$

Equivalently: $e_v = \frac{1}{2}\left(\sum_i w_i \sigma_i^2 - \sigma_p^2\right)$. Always $\geq 0$ for long-only unlevered portfolios.

**Diversification Return for Inverse/Leveraged ETF (single risky asset + cash)** [p.112, ch.5]

$$e_v = 0.5 \cdot (w_1 - 1) \cdot w_1 \cdot \sigma_1^2$$

where $w_1$ is the weight in the risky asset (e.g., $w_1 = -1$ for inverse ETF, $w_1 = 2$ for 2X ETF). For $w_1 \notin [0, 1]$, $(w_1 - 1)w_1 > 0$, making $e_v > 0$... Author states: for inverse ETF ($w_1 = -100\%$): negative diversification return; for 2X ETF ($w_1 = 200\%$): negative diversification return. Annual slippage at 20% underlying vol: −21.3% for −3X ETF, −11.3% for 3X ETF [p.112–113, ch.5]. The formula as extracted from OCR may have sign ambiguity — use the empirical slippage values as ground truth.

---

## 4. Algoritmos e Pseudocódigo

**ERC Portfolio Construction** [p.10–11, ch.1]

```
Input: N assets, volatilities σ_i, correlation matrix ρ_ij

For two assets (exact closed-form solution):
    w_1 = σ_2 / (σ_1 + σ_2)
    w_2 = σ_1 / (σ_1 + σ_2)
    # Inverse vol weighting is exact ERC for two assets regardless of correlation

For N > 2 assets (no closed-form solution — book's prescribed method):
    Use trial and error (small N, e.g. 3 assets) or Excel Solver to find w such that:
        risk_contribution(i) is equal for all i
    where risk_contribution(i) = w_i * (Σ_j ρ_ij σ_i σ_j w_j) / σ_portfolio

Note: The ERC condition (equal risk contribution for all assets) does NOT
have a closed-form expression for the weights when N > 2.
Naïve risk parity (inverse vol only, ignoring correlations) approximates ERC
but is exact only when all pairwise correlations are equal.
```

**Risk Parity Benchmark Portfolio (3-asset, Table 5.1)** [p.122, ch.5]

```
Asset class     Weight    Instrument
Commodities      25%      Futures (GSCI/DJ-UBS)
Equities         33%      Physical (MSCI index)
Government bonds 142%     Futures + physicals (WGBI)
Total leverage:  200%

Cash is divided between:
  - Physical investments for risk premium capture
  - Collateral for derivatives positions
```

**Return-Based Style Analysis for Risk Parity Manager Classification** [p.166–167, ch.7]

```
Input:
  R_manager[t] — monthly returns over 3-year trailing window
  R_index[i,t] — monthly returns for 12 asset class indices
                 (DJUBS, UST, WGBI ex US, MBS, TIPS, Credit,
                  EM Debt, HY, S&P 500, MSCI ex US, R2000, MSCI EM)

Step 1: Constrained regression (long-only leveraged)
  min  Σ_t (R_manager[t] - Σ_i w_i * R_index[i,t])^2
  s.t. w_i >= 0  (no shorting)
       Σ_i w_i can exceed 1.0  (leveraged)

Step 2: Compute leverage = Σ_i w_i  (target: 200%-300%)
        Compute R² (target: >90% for good fit)

Step 3: Map effective weights → risk contributions
  using covariance matrix from long-term (>3 year) history

Step 4: Aggregate risk into three buckets:
  Equity risk:    S&P 500 + MSCI ex US + R2000 + MSCI EM + HY + EM Debt(partial)
  Interest rate:  UST + WGBI ex US + MBS + Credit(partial)
  Inflation:      DJUBS + TIPS

Step 5: Classification
  Balanced risk parity:  each bucket roughly 20%–40%
  Equity-biased (not RP): equity+inflation > 80%  (resembles 60/40)
  Rate-biased (not RP):   interest rate > 60%     (levered bond fund)
```

**Naïve Stop-Loss Test on Asset Classes** [p.181–182, ch.7]

```
Input: monthly return series, threshold T (1-month return standard deviation)
       re-entry: when cumulative return from exit recovers to positive (1/5 of threshold)
       naïve risk parity: equal vol contribution, 200% total leverage
       deleveraging: reduce each investment by 25% (not full exit) when stop-loss triggers

For each asset class / portfolio:
  Track 1-month return
  If 1-month return <= -T: reduce exposure by 25% (go to 75% invested + 25% cash)
  Re-enter (restore full exposure) when 1-month return >= +T/5

Stop-loss has positive investment value if:
  AC(1) > 0 (trending losses)  AND
  Significant negative skewness + high excess kurtosis

Result: commodities (GSCI) benefit from stop-loss due to AC(1) = 0.15 (positive)
        stocks/bonds/risk-parity overall: stop-loss has little or negative value
        (bonds have AC(1) > 0 but also AC(2) < 0, offsetting the benefit)
```

---

## 5. Regras de Trading Explícitas

- **REGRA [p.10, ch.1]**: For a two-asset risk parity portfolio, set weights inversely proportional to volatility. With stocks at 15% vol and bonds at 5% vol (ratio 3:1), the unlevered risk parity portfolio is 25% stocks / 75% bonds.

- **REGRA [p.10, ch.1]**: Apply leverage to the unlevered risk parity portfolio to match a target risk level (e.g., 60/40's ~9.6% volatility). A 25/75 stock/bond portfolio requires ~2:1 leverage → 50% stocks / 150% bonds.

- **REGRA [p.16, ch.1]**: Use risk parity at one of three leverage levels: (1) unleveraged at 4%–5% risk (bond-index substitute); (2) ~2:1 leverage at ~10% risk (balanced portfolio substitute); (3) ~4:1 leverage at ~20% risk (global macro substitute, Sharpe ~1.1 over 1983–2004 backtest).

- **REGRA [p.25, ch.2]**: Classify HY bonds as equity risk, not interest rate risk. Do NOT include HY bonds in the interest rate bucket of a risk parity portfolio — this amounts to doubling equity risk. Exclude HY from core risk parity allocations due to equity exposure and illiquidity.

- **REGRA [p.37–38, ch.2]**: Always hedge currency exposure when investing in foreign equity or bond risk premiums. Currency risk adds volatility without return premium (t-stat ≈ 0.28 for USD investors in unhedged WGBI).

- **REGRA [p.55, ch.3]**: Do NOT use duration alone as the risk measure for bonds. Use return volatility (= duration × yield volatility). In a ZIRP environment, declining yield volatility can more than offset rising duration, resulting in lower effective bond risk.

- **REGRA [p.55–56, ch.3]**: In ZIRP environments where short-end yields are anchored, reduce risk allocation to 2-year and 5-year bonds (low term premium, no equity-hedging benefit). Increase allocation to 10- and 30-year bonds (meaningful yield volatility, negative equity correlation preserved).

- **REGRA [p.66, ch.3]**: Do NOT use forward rates as forecasts of future interest rates. The hit ratio is only 39% (1952–2013). Use current rates as the default expectation; rely on fundamental macroeconomic analysis (growth + inflation) for any active interest rate views.

- **REGRA [p.78, ch.4]**: When inflation is persistently high, dynamically shift risk allocation toward real assets (commodities, inflation-linked bonds) and away from nominal bonds and equities. Dynamic risk allocation would have been especially beneficial in the 1970s.

- **REGRA [p.78, ch.4]**: As a secondary inflation defense, deleverage the portfolio (reduce total risk exposure) when all three risk premiums are simultaneously negative. High cash returns during inflationary regimes partially compensate for the deleveraging.

- **REGRA [p.113, ch.5]**: Do NOT use inverse or leveraged single-asset ETFs as long-term investments. Annual return slippage (negative diversification return) at 20% underlying vol: −21.3% for −3X, −11.3% for 3X, −3.9% for −1X. These are structural costs, not episodic.

- **REGRA [p.180–183, ch.7]**: Stop-loss policies have real investment value for commodities (positive autocorrelation AC(1) = 0.15 and fat tails), but little or negative investment value for stocks, bonds, and diversified risk parity portfolios overall.

- **NUNCA [p.169, ch.7]**: Do not label a portfolio "risk parity" based on leverage and fixed-income notional weight alone. A portfolio with 86%–93% "risk-on" (equity + inflation) allocation is not risk parity — it is a disguised 60/40. The required test: equity risk + interest rate risk + inflation risk each ≈ 20%–40%.

---

## 6. Pitfalls e Anti-patterns

- **[p.18, ch.2]** Applying ERC to an asymmetric set of assets (e.g., four equity asset classes + five bond asset classes including HY/EM + one commodity = 10 assets) produces ~65% equity risk — structurally resembling a 60/40 portfolio. Risk parity requires parity at the level of economic risk dimensions (equity/rates/inflation), not at the level of asset count.

- **[p.11, ch.1]** Naïve risk parity (inverse vol weighting) ignores correlations and is exact only for two-asset portfolios or when all pairwise correlations are equal. For N > 2 assets with unequal correlations, it overweights high-correlation assets relative to the true ERC optimum.

- **[p.23–24, ch.2]** Measuring HY bond risk via annualized monthly volatility (~8.93%) underestimates true risk by nearly 2x due to illiquidity-driven autocorrelation. True risk (annual return volatility) is ~16.40% — equivalent to large-cap equities. Using the wrong risk measure causes inadvertent doubling of equity exposure.

- **[p.27–29, ch.2]** Using roll yield as a long-term valuation indicator or predictor of commodity returns is erroneous. Roll yield explained commodity returns significantly only in 1991–2000 when prices were stationary. In the inflationary 1970s and 2000s, price return dominated while roll yield was largely irrelevant.

- **[p.51, ch.3]** Treating duration as the primary risk measure for bonds leads to incorrectly raising leverage to short-end instruments when short-end yield volatility has collapsed to near-zero (e.g., under ZIRP). Effective bond risk = duration × yield volatility.

- **[p.60–66, ch.3]** Using forward rates as forecasts of future interest rates introduces a persistent upward bias. Forward rates called for rising rates 72% of the time; actual rates rose 51% of the time. The hit ratio was 39% — below random chance.

- **[p.73–74, ch.4]** Constructing "risk parity" portfolios without inflation protection (missing commodities and TIPS) creates systematic vulnerability to inflation shocks. The only scenario where all three risk premiums go negative simultaneously is during high and sustained inflation (1970s), and this requires real assets to hedge.

- **[p.111–113, ch.5]** Daily-rebalanced leveraged/inverse ETFs structurally destroy value long-term via negative diversification return. At 20% underlying index volatility: −21.3%/year slippage for −3X ETF; −11.3% for 3X ETF. Using a −3X ETF when the index returns −5%/year, the ETF likely returns −6.3% (not the expected +15%).

- **[p.169, ch.7]** High leverage ratio is a necessary but not sufficient condition for risk parity. Among seven managers studied, two had 86%–93% growth (equity+inflation) risk concentration despite 188%–225% leverage and large fixed-income notional weights. These portfolios fail the risk parity test because their risk allocation is indistinguishable from 60/40.

- **[p.113, ch.5]** For leveraged multi-asset portfolios, top-level rebalancing is trend-following (buy winners / sell losers) while bottom-level cross-asset rebalancing is contrarian (mean-reverting). The net diversification return can be positive or negative. With negative stock-bond correlation and moderate leverage, diversification return for a leveraged risk parity portfolio can exceed that of a 60/40 portfolio.

---

## 7. Parâmetros Sensíveis

- **Equity volatility: 15%–20% annualized** [p.1, ch.1]: Broad developed market equity indices have volatilities in this range. Used as 15% in most examples. Not optimized — reflects long-run empirical norm; economically justified as the risk compensation for business cycle exposure.

- **Investment-grade bond volatility: ~5% annualized** [p.1, ch.1]: High-quality fixed-income assets exhibit much lower volatilities. Used as 5% in most examples; 3:1 vol ratio vs. equities. Not optimized; economically justified by the lower uncertainty of fixed coupon payments.

- **Benchmark risk parity leverage: ~200%** [p.10, ch.1 and p.181, ch.7]: Unlevered 25/75 stock/bond risk parity portfolio (~4%–5% vol) requires approximately 2:1 leverage to match 60/40's ~10% risk level. Not curve-fitted; derived mechanically from the risk-matching requirement. The 3-asset benchmark (Table 5.1) also uses 200% leverage.

- **Three-asset benchmark weights** [p.122, ch.5 (Table 5.1)]: 25% GSCI (commodities), 33% MSCI (equities), 142% WGBI (bonds), total 200%. Author presents these as a "simple benchmark for risk parity" — reflecting the approximate inverse-vol weighting among three asset classes. Not back-tested to this specific parameterization.

- **Commodity volatility: ~25% annualized** [p.5, ch.1]: Used in the three-asset example. In-sample value for the illustrative example; not tuned. The author notes commodities' correlations with stocks and bonds change sign with the inflation regime.

- **Style analysis look-back window: 3 years monthly** [p.166–167, ch.7]: Chosen because risk parity managers significantly evolved strategies post-2008 GFC; longer history would misrepresent current style. Acknowledged as too short for stable covariance estimation — author uses a longer history for the separate risk decomposition step.

- **Risk parity Sharpe ratios (backtest, 1983–2004)** [p.13–15, ch.1]: Unlevered ERC (23/77 stock/bond): Sharpe 0.87 vs. 0.67 for 60/40 vs. 0.55 for Russell 1000 (Table 1.6, p.13). Levered to stocks' risk level (~280% leverage): average return 13.2% vs. 8.3% for Russell 1000, same 15.1% vol (Table 1.8, p.15). These are in-sample results on a single period, not out-of-sample validation.

---

## 8. Citações Literais Importantes

> "The innovation and defining characteristic of risk parity lies in its active use of risk contribution as the underlying criterion to construct portfolios, rather than as a limited and often passive tool for risk monitoring." — [p.3, ch.1]

> "Risk contributions to portfolio risk are directly linked to return contributions to portfolio returns from underlying assets." — [p.6, ch.1]

> "Both theoretical proof and empirical evidence show that risk contribution has a sound economic interpretation — either as average return contribution for a mean-variance optimal portfolio or as expected contribution to potential large losses of any portfolio." — [p.9, ch.1]

> "HY bonds are equity in bond's clothing." — [p.25, ch.2]

> "The roll yield is important only if the price change is small compared to the roll yield." — [p.27, ch.2]

> "Risk parity, a term I christened in 2005, originated as a quantitative approach for asset allocation." — [p.xiii, Preface]

---

## 9. Conexões com Outros Livros Desta Base

N/A — This is among the first books processed; cross-references will be added in subsequent passes after other summaries in this knowledge base are verified. Likely connections based on content overlap (not yet verified against other summaries):

- ERC/risk-budgeting portfolio construction: potentially related to `ml_for_algo_trading.md` (portfolio construction chapters) and `trading_evolved.md` (risk-based allocation).
- Critique of mean-variance optimization (sensitivity to inputs, concentrated outputs): likely shared theme in `systematic_trading.md` and other quant portfolio books in this base.
- Stop-loss analysis and behavioral bias (Prospect Theory, Kahneman-Tversky): potentially in `adaptive_markets.md`.
- Commodity futures roll yield decomposition: potentially in commodity-focused books in this base.
