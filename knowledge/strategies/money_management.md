# Money Management & Position Sizing

Kelly, fractional Kelly, optimal f, risk of ruin — sizing sob incerteza.

## Sources

- [`books/math_money_mgmt.md`](../books/math_money_mgmt.md)
- [`books/leverage_space.md`](../books/leverage_space.md)
- [`books/systematic_trading.md`](../books/systematic_trading.md)

## From `books/math_money_mgmt.md`

### Regras de Trading Explícitas

- **REGRA [p.13]**: Never use money management to salvage a system with negative mathematical expectation. Money management only amplifies what is already there — positive or negative.

- **REGRA [p.17]**: Always use the biggest historical loss (not average loss) as the denominator in HPR calculations. Using average loss underestimates real risk.

- **REGRA [p.16]**: Do NOT equate optimal f with Kelly Criterion unless the trading system has exactly two outcomes of fixed sizes (pure Bernoulli).

- **REGRA [p.16]**: Do not use Kelly Criterion on systems with variable win/loss sizes. Produces incorrect f values and can lead to ruin.

- **REGRA [p.34]**: Expect the **longest** drawdown to occupy 35-55% of trading life at optimal f. The arc sine laws apply to duration of drawdown, not its depth. This is a mathematical consequence, not a tail risk.

- **REGRA [p.26, ch.2]**: Do NOT switch to fixed-fraction trading until equity surpasses the Threshold to Geometric (T). Below T, constant-contract trading has a higher expected outcome.

- **REGRA [p.44-48, ch.3]**: When using parametric optimal f with the Normal distribution, use at minimum M = 100 discrete points to discretize the distribution.

- **REGRA [p.76-80, ch.6]**: Compute optimal f for each market system individually first, then construct the portfolio using those HPR streams. Do NOT optimize portfolio weights and f simultaneously.

- **REGRA [p.82-84, ch.7]**: Use unconstrained portfolio weights (sum > 1 is allowed and expected). The constraint sum(w) = 1 artificially limits growth.

- **REGRA [p.89-93, ch.8]**: Prefer dynamic fractional f over static fractional f. Dynamic is asymptotically superior: it compounds the active portion at full optimal f while inactive equity provides a floor.

- **REGRA [p.96-97, ch.8]**: Before trading an unconstrained portfolio, compute margin upper limit U via Eq. (8.08). Set maximum active equity percentage to min(U, 1.0).

- **REGRA [p.97, ch.8]**: When a component's portfolio weight exceeds 1.0, set the active equity upper limit to 1 / (highest weighting) to prevent a single worst-case loss from wiping the account.

- **REGRA [p.97-98, ch.8]**: When managing a rotating portfolio, always recalculate the unconstrained geometric optimal portfolio after each composition change. Keep the inactive equity dollar amount constant.

- **NUNCA [p.16]**: Do not use the Kelly Criterion on trading systems with variable win/loss sizes.

- **NUNCA [p.24]**: Do not use the Fundamental Equation of Trading as a real-time trading signal. Use it only for scenario analysis and only when distribution is stationary.

---

### Fórmulas / Equações

**HPR (Holding Period Return)** [p.16, ch.1; eq.1.11]

$$HPR_i = 1 + f \cdot \left(\frac{-\text{Trade}_i}{\text{BiggestLoss}}\right)$$

- $f$ = fraction of equity risked (0 to 1) [p.16, ch.1]
- $\text{Trade}_i$ = P&L of trade $i$ (negative for losses) [p.16, ch.1]
- $\text{BiggestLoss}$ = largest single-trade loss (negative number) [p.16, ch.1]

---

**Terminal Wealth Relative (TWR)** [p.14, ch.1; eq.1.04]

$$TWR = \prod_{i=1}^{N} HPR_i$$

---

**Geometric Mean (G)** [p.14-15, ch.1; eq.1.05]

$$G = TWR^{1/N}$$

---

**Geometric Average Trade (GAT)** [p.17-18, ch.1; eq.1.14]

$$GAT = (G - 1) \cdot \frac{BiggestLoss}{-f}$$

- $G - 1$ = Geometric mean minus 1 (e.g., if G = 1.017238 then $G - 1$ = 0.017238) [p.18, ch.1]
- $f$ = Optimal fixed fraction [p.18, ch.1]
- $BiggestLoss$ = always a negative number [p.18, ch.1]

Example from the text: G = 1.017238, BiggestLoss = -$8,000, f = .31.
GAT = (1.017238 - 1) * ($8,000 / .31) = 0.017238 * $25,806.45 = $444.85 [p.18, ch.1].

Interpretation: average dollar profit per contract per trade under optimal-f reinvestment.

---

**Kelly Criterion (Bernoulli processes only)** [p.16, ch.1; eq.1.10c]

$$f^* = P - \frac{Q}{B}$$

- $B$ = payoff ratio = avg\_win / avg\_loss [p.16, ch.1]
- $P$ = historical win probability [p.16, ch.1]
- $Q = 1 - P$ [p.16, ch.1]
- **Warning**: valid only when all wins are the same size and all losses are the same size (Bernoulli). Do NOT use for variable-payoff trading systems [p.16, ch.1].

---

**Estimated Geometric Mean (EGM) — Pythagorean Relationship** [p.21, ch.1; eq.1.16a]

$$EGM = \sqrt{A^2 - SD^2}$$

- $A$ = arithmetic mean of HPRs [p.21, ch.1]
- $SD$ = standard deviation of HPRs [p.21, ch.1]

The Pythagorean form (eq.1.28) derived at [p.24, ch.1]:

$$A^2 = G^2 + SD^2$$

where A is the hypotenuse and G is the leg to maximize. Any increase in SD requires a proportional increase in A to preserve the same G [p.24, ch.1].

---

**Fundamental Equation of Trading** [p.24, ch.1; eq.1.19c]

$$\widehat{TWR} = (A^2 - SD^2)^{N/2}$$

- $A$ = arithmetic mean HPR
- $SD$ = population standard deviation of HPRs
- $N$ = number of trades

This equation is labeled "the fundamental equation for trading" at [p.24, ch.1]. Note: the intermediate form eq.(1.19a) appears at [p.23] and the final simplification to eq.(1.19c) is derived at [p.24].

---

**Normal Distribution CDF approximation** [p.38-40, ch.3]

$$N(Z) = 1 - N'(Z) \cdot \left(1.330274429 Y^5 - 1.821255978 Y^4 + 1.781477937 Y^3 - 0.356563782 Y^2 + 0.319381530 Y\right)$$

where:
- $Y = \frac{1}{1 + 0.2316419 |Z|}$ [p.38, ch.3]
- $N'(Z) = 0.398942 \cdot e^{-Z^2/2}$ [p.38, ch.3]

---

**Lognormal conversion** [p.41-42, ch.3]

To use lognormal math, convert price ratios (HPRs) to natural logarithms [p.42, ch.3]:

$$x_{ln} = \ln\!\left(\frac{P_t}{P_{t-1}}\right)$$

where $P_t / P_{t-1}$ is the price ratio (HPR) for the period. The converted values $x_{ln}$ are Normally distributed if the raw price changes were Lognormally distributed. Apply all Normal distribution math to $x_{ln}$ values [p.42, ch.3].

---

**Geometric Optimal Portfolio Condition** [p.82-84, ch.7]

$$A_{portfolio} - SD_{portfolio}^2 = 1$$

The arithmetic mean HPR minus the variance in HPRs equals 1 at the geometric optimal portfolio [p.83, ch.7].

---

**Hedge Ratio — Dynamic Fractional f** [p.94-95, ch.8; Eq. 8.04a]

$$H = \frac{f \cdot A}{E}$$

- $H$ = hedge ratio [p.94, ch.8]
- $f$ = optimal f (0 to 1) [p.94, ch.8]
- $A$ = active equity [p.94, ch.8]
- $E$ = total equity [p.94, ch.8]

---

**Hedge Ratio — Static Fractional f** [p.95, ch.8; Eq. 8.04b]

$$H = f \cdot FRAC$$

- $FRAC$ = the fraction of optimal f being used [p.95, ch.8]

---

**Aggregate f for a multi-system portfolio** [p.95, ch.8; Eq. 8.05]

$$f = \sum_{i=1}^{N} f_i \cdot W_i$$

- $W_i$ = weighting of the $i$th market system [p.95, ch.8]
- $f_i$ = optimal f of the $i$th system [p.95, ch.8]

---

**Margin Upper Limit for Unconstrained Portfolio** [p.96-97, ch.8; Eq. 8.08]

$$U = \frac{\sum_{i=1}^{N} f_i\$}{\left(\sum_{i=1}^{N} margin_i\$\right) \cdot N}$$

- $U$ = maximum fraction of active equity without triggering a margin call (cap at 1.0) [p.96, ch.8]
- $f_i\$$ = optimal f in dollars for the $i$th system [p.96, ch.8]
- $margin_i\$$ = initial margin requirement of the $i$th system [p.96, ch.8]

---

**Portfolio Variance to Option Volatility** [p.95, ch.8; Eq. 8.07]

$$OV = \sqrt{V} \cdot ACTV \cdot \sqrt{YEARDAYS}$$

- $OV$ = annualized volatility input for option pricing [p.95, ch.8]
- $V$ = portfolio variance [p.95, ch.8]
- $ACTV$ = current active equity fraction [p.95, ch.8]
- $YEARDAYS$ = trading days in a year (typically 251) [p.95, ch.8]

---

**Chi-Square Statistic with Yates' correction** [p.100, Appendix A; Eq. A.02]

$$\chi^2 = \sum_{i=1}^{N} \frac{(|O_i - E_i| - 0.5)^2}{E_i}$$

Used when expected values $E_i$ are non-integers [p.100, Appendix A].

---

**Binomial Distribution PMF** [p.101-102, Appendix B; Eq. B.07]

$$N'(X) = \frac{N!}{X!(N-X)!} \cdot P^X \cdot Q^{N-X}$$

---

### Algoritmos e Pseudocódigo

**Algorithm: Empirical Optimal f Search** [p.16-17, ch.1]

```python
# Input: trades = list of N P&L values
# Output: optimal_f, max_TWR
biggest_loss = min(trades)
max_TWR = 0
optimal_f = 0
for f in [i/100 for i in range(1, 101)]:
    TWR = 1.0
    valid = True
    for trade in trades:
        HPR = 1 + f * (-trade / biggest_loss)
        if HPR <= 0:
            valid = False
            break
        TWR *= HPR
    if valid and TWR > max_TWR:
        max_TWR = TWR
        optimal_f = f
return optimal_f, max_TWR
```

---

**Algorithm: Parametric Optimal f (Normal Distribution)** [p.40-44, ch.3]

```python
# Input: mean_trade, sd_trade, biggest_loss, M=100 discrete points
# Step 1: Generate M equally-spaced CDF points
for j in range(1, M+1):
    Z_j = InverseNormal((j - 0.5) / M)   # Newton-Raphson on N(Z) eq
    x_j = mean_trade + Z_j * sd_trade

# Step 2: Search for optimal f
max_TWR = 0
optimal_f = 0
for f in [i/100 for i in range(1, 101)]:
    TWR = 1.0
    valid = True
    for x in x_points:
        HPR = 1 + f * (-x / abs(biggest_loss))
        if HPR <= 0:
            valid = False; break
        TWR *= HPR
    if valid and TWR > max_TWR:
        max_TWR = TWR
        optimal_f = f
return optimal_f
```

---

**Algorithm: Runs Test for Trade Independence** [p.10, ch.1; eq.1.01]

```python
# Input: sequence of N trades (sign = win/loss)
# Output: Z statistic (|Z| > 1.96 -> dependent at 95% confidence)
# eq.(1.01): Z = (N*(R-0.5)-X) / sqrt((X*(X-N))/(N-1))
R = count_runs(trades)           # number of consecutive same-sign sequences
n1 = sum(1 for t in trades if t > 0)
n2 = sum(1 for t in trades if t < 0)
N = n1 + n2
X = 2 * n1 * n2
Z = (N * (R - 0.5) - X) / sqrt((X * (X - N)) / (N - 1))
```

---

**Algorithm: Geometric Optimal Portfolio Construction** [p.76-80, ch.6]

```
Input: N market systems with daily equity change series
Output: optimal weights W[i]

For each system i, compute individual optimal_f_i empirically.        [p.76, ch.6]
Convert daily equity changes to HPR series under optimal_f_i.         [p.77, ch.6]
Compute pairwise linear correlation matrix of HPR series.              [p.78, ch.6]
Grid-search or QP-optimize unconstrained weight vector W
  to maximize EGM_portfolio = sqrt(A_p^2 - SD_p^2)
  subject to: W[i] >= 0 for all i (no shorting systems).
  Optimum at slope-1 line intersecting AHPR frontier: A_p - SD_p^2 = 1.  [p.83, ch.7]
Return optimal W and the corresponding f_dollar per system
  (individual market system's optimal f$ divided by its portfolio weighting). [p.96, ch.8]
```

---

**Algorithm: Dynamic Fractional f (Split-Equity) Strategy** [p.89-93, ch.8]

```
Input: total_equity, initial_active_pct (e.g. 0.20), f_dollar per system
Output: contracts per system

active_equity = total_equity * initial_active_pct
inactive_equity = total_equity - active_equity  # held constant in dollars

for each system i:
    contracts_i = floor(active_equity / f_dollar_i)

# Reallocation: triggered periodically or by investor utility threshold
# Reset: recalculate active_equity = total_equity * initial_active_pct
#        inactive_equity = total_equity - active_equity
```

---

### Pitfalls e Anti-patterns

- **[p.13]** Attempting to use money management on a system with negative expectation. No position sizing technique converts a losing strategy into a winner.

- **[p.17, ch.1]** Confusing optimal f with the fraction of account equity to invest. Optimal f is the fraction used to compute position size (contracts = equity / f$), not a direct equity percentage.

- **[p.16, ch.1]** Applying Kelly Criterion to systems with non-fixed payoffs. Variable P&L requires the empirical optimal f search.

- **[p.34, ch.2]** Abandoning optimal f during a large drawdown. Arc Sine Laws show the longest drawdown occupies 35-55% of trading life at optimal f. Quitting locks in the loss.

- **[p.?]** Over-relying on EGM when the distribution of returns is not stationary. EGM assumes stable A and SD over time. N/A — no specific page verified for this warning; p.37 contains only skewness/kurtosis definitions and does not discuss EGM limitations.

- **[p.44-48, ch.3]** Using too few discrete data points (M < 30) when computing parametric optimal f. Smooths tails and biases f upward toward ruin.

- **[p.74-76, ch.6]** Using classical Markowitz efficient frontier with constrained weights for a trading portfolio. Ignores geometric growth objective.

- **[p.82-84, ch.7]** Constraining portfolio weights to sum to 1. Systematically leaves geometric growth on the table.

- **[p.95-96, ch.8]** Using portfolio insurance as the primary reallocation method. Requires continuous reallocation, undermining dynamic fractional f asymptotic advantage.

- **[p.97, ch.8]** Adding too many market systems. Because of simultaneous outcomes and margin constraints, 3 systems at full optimal f typically beats 300 systems at diluted f.

- **[p.97-98, ch.8]** Applying optimal f derived from a pre-filtered trade series to a post-filtered series. Always recalculate f on the actual traded series.

- **[p.10-12, ch.1]** Assuming trade independence without testing. Positive autocorrelation and negative autocorrelation both change the appropriate f.

---

---

## From `books/leverage_space.md`

### Regras de Trading Explícitas

- **REGRA [p.15-18, eqs.1.06-1.10]:** Position-size via `Number of Units = Equity / f$` where `f$ = |BiggestLoss| / f_optimal`. Do NOT size by margin — margin "has nothing to do with the optimal amount to finance a trade by" [p.19].
- **REGRA [p.25]:** The chosen BiggestLoss parameter only *bounds f between 0 and 1*; it does NOT change the optimal number of units (Table 2.1). You can use an arbitrary worst case if true worst case is unknown, as long as you are consistent.
- **REGRA [p.63, ch.4]:** For multi-component portfolios, do NOT use pairwise correlation as an input. Instead, bin empirical history into a joint-scenarios table of combinations with probabilities — that is the only input the Leverage Space Model requires.
- **NUNCA [p.43, Fig.3.8]:** Operate to the right of the peak of the f curve. Even in a cash account with no borrowing, there is a point (f > peak) where GHPR<1 and ruin is certain with probability → 1 as q → ∞. In the 2:1 coin toss that point is f = 0.5 (one bet per $2 in stake).
- **NUNCA [p.44, p.150]:** Use ad-hoc heuristics like "half Kelly" or "never risk more than 1% / 2%" as primary position-sizing rules. They are arbitrary stationary points that do not migrate with holding-period count; the nature of the curve renders them incorrect.
- **NUNCA [p.65]:** Rely on low historical correlation to size multiple simultaneous positions. Vince's empirical finding: crude-gold r = 0.18 all-days → 0.61 on crude 3σ days; Ford-Pfizer r = 0.15 all-days → 0.75 on S&P 500 3σ days. Correlation fails precisely when needed.
- **REGRA [p.89, ch.5]:** Remove from the N+1-dimensional surface all coordinates where the expected drawdown RD(b) violates your constraint (GHPR at those points is set to 0). Operate only on the remaining terrain.
- **REGRA [p.92]:** When the drawdown-admissible terrain has multiple equal-altitude optima, pick the coordinate with the smallest `sum(f_i)` — closer to origin means smaller minimum expected drawdown among ties.
- **REGRA [p.33-37, Ch.3]:** When you can know your horizon q, the growth-maximizing f is *slightly greater* than the asymptotic optimal f, and converges to optimal f from above as q → ∞ (e.g., for the 2:1 coin toss: q=1→f=1.0, q=2→0.5, q=3→0.37868, q=8→0.2871, q=∞→0.25). In practice, trading at asymptotic optimal f is always slightly sub-optimal — this is acceptable.
- **REGRA [p.157-167, ch.7]:** If your criterion is *probability of profit at horizon* rather than growth, use two Martingale exponents (z−, z+) in eq.7.03. z+ in (−0.5, 0] for above-start equity (take profit more slowly), z− < −0.5 for below-start (press harder). Optimize (z−, z+, f_1…f_N) to maximize PP(r) subject to RD(b) ≤ constraint.
- **REGRA [p.69]:** If trading in integer units (one contract, one lot) constrains you below the continuous optimum (e.g., 21 bets instead of 21.85), always *round down*, never up — rounding up places you to the right of the peak on some axis.

### Fórmulas / Equações

**Mathematical Expectation (ME) / scenario expected value** [p.2, Introduction]

$$ME = \sum_{i=1}^{n} (P_i \cdot A_i)$$

**Kelly optimal f (2-outcome, unequal payoffs)** — Thorp form, via Vince [p.12, eq.1.04]

$$f = \frac{(B+1)P - 1}{B}$$

- B = ratio amount-won / amount-lost on losing bet; P = prob. of win. [p.12, eq.1.04]
- Yields f = 0.25 for the 2:1 coin toss (P=0.5, B=2). [p.12, eq.1.04]
- Valid ONLY when all wins are the same size and all losses are the same size [p.13].

**HPR(f) for a trade stream (Vince 1990)** [p.16, eq.1.06]

$$HPR(f)_i = 1 + f \cdot \frac{-\text{trade}_i}{\text{BiggestLoss}}$$

**TWR and GHPR from a trade stream** [p.17, eqs.1.07-1.08]

$$TWR(f) = \prod_{i=1}^{n}\left(1 + f \cdot \frac{-\text{trade}_i}{\text{BiggestLoss}}\right) \qquad GHPR(f) = TWR(f)^{1/n}$$

**HPR(f) for a scenario spectrum (generalization)** [p.47, eq.3.02]

$$HPR(f)_i = \left(1 + A_i \cdot \frac{-f}{W}\right)^{P_i}$$

- W = worst outcome across the n scenarios (a negative number) [p.47, eq.3.02]
- A_i = outcome of scenario i; P_i = its probability [p.47, eq.3.02]

**GHPR for N simultaneous scenario spectrums (THE central Leverage-Space equation)** [p.71, eqs.4.01-4.02a]

$$HPR(f_1 \ldots f_N)_k = 1 + \sum_{i=1}^{N}\left(f_i \cdot \frac{-PL_{k,i}}{BL_i}\right)$$

$$GHPR(f_1 \ldots f_N) = \prod_{k=1}^{n} HPR(f_1 \ldots f_N)_k^{\text{prob}_k}$$

- k indexes joint-scenario rows (n = ∏ #scenarios_i across N spectrums) [p.71, eqs.4.01-4.02a]
- PL_{k,i} = profit/loss of component i in joint-scenario k [p.71, eqs.4.01-4.02a]
- BL_i = worst scenario outcome for component i [p.71, eqs.4.01-4.02a]
- prob_k = joint probability of combination k [p.71, eqs.4.01-4.02a]
- Maximize over (f_1…f_N) to find the optimal-f set; no correlation coefficients appear. [p.71, eqs.4.01-4.02a]

**Pythagorean relation of AHPR, SDHPR, EGM** [p.52, eq.3.10b]

$$AHPR(f)^2 = EGM(f)^2 + SDHPR(f)^2$$

- Reducing SDHPR improves EGM equivalently to the same-sized increase in AHPR. [p.52, eq.3.10b]

**Fundamental Equation of Trading** [p.54, eq.3.11b]

$$TWR(f) \approx \left(AHPR(f)^2 - SDHPR(f)^2\right)^{q/2}$$

- If AHPR(f) ≤ 1, no q can rescue it — eventual ruin. [p.54, eq.3.11b]

**Time to reach a TWR goal** [p.57, eq.3.14]

$$q = \frac{\ln(TWR(f))}{\ln(GHPR(f))}$$

**Classical Risk of Ruin (Feller)** [p.94-95, eq.5.01]

$$RR = \frac{\left(\frac{1-p}{p}\right)^u - \left(\frac{1-p}{p}\right)^z}{\left(\frac{1-p}{p}\right)^u - 1} \qquad (\text{if } p \neq 1-p)$$

- z = initial capital, u = combined capital (target + initial), p = win prob. [p.94-95, eq.5.01]
- If p = 1−p: `RR = 1 − z/u` [eq.5.01a]. [p.94-95, eq.5.01]

**β indicator — ruin check for a single HPR(f) permutation** [p.98, eq.5.03]

$$\beta = \text{int}\!\left(\frac{\sum_{i=1}^{q}\left[\left(\prod_{t=0}^{i-1} HPR(f)_t\right) \cdot HPR(f)_i - b\right]}{\sum_{i=1}^{q}\left|\left(\prod_{t=0}^{i-1} HPR(f)_t\right) \cdot HPR(f)_i - b\right|}\right)$$

- β = 1 means no ruin; β = 0 means ruin occurred somewhere in the permutation. [p.98, eq.5.03]
- Variant 5.03a (drawdown): replace the running product with `min(1.0, running product)` so the barrier floats with each new equity high [p.106].

**Risk of Ruin / Drawdown over all permutations** [p.99, eq.5.05]

$$RR(b, q) = 1 - \frac{\sum_{k=1}^{n^q} \beta_k}{n^q}$$

- Taken over all n^q permutations of n HPR(f)s sequenced q-deep. [p.99, eq.5.05]
- Asymptotes as q → ∞ to a finite horizontal value (e.g., 0.48406 for the 2:1 coin toss at f=0.25, b=0.6) [p.102-103, Table 5.3].

**Small-Martingale capitalization (Ch.7 migration function)** [p.161, eq.7.03]

$$f\$_{k,i} = \frac{BL_k / -f_k}{\left(\frac{acctEQ_0}{acctEQ_{i-1}}\right)^{\frac{1}{1+z} - 1}}$$

- −1 < z ≤ 0 (z− for equity below start, z+ for above). [p.161, eq.7.03]
- z = 0 → constant f$ per unit (units scale with equity). [p.161, eq.7.03]
- z = −0.5 → constant number of units regardless of equity. [p.161, eq.7.03]
- z < −0.5 → Martingale effect (bet more as equity falls). [p.161, eq.7.03]
- Figure 7.3 example uses z− = −0.7, z+ = −0.3 [p.163].

**Number of units to trade at period i, component k** [p.164, eq.7.04]

$$U_{k,i} = \frac{acctEQ_{i-1}}{f\$_{k,i}}$$

**Probability-of-Profit acceptance criterion** [p.166, eq.7.06]

$$TWR(f_1 \ldots f_N) - 1 \geq r \;\Rightarrow\; \text{branch is "profitable"}$$

- Maximize the fraction of q-deep permutation branches satisfying (7.06) over (z−, z+, f_1…f_N) subject to an RD(b) constraint. [p.166, eq.7.06]

### Algoritmos e Pseudocódigo

**Optimal-f for a single scenario spectrum** [ch.3, p.47-48]

```
Input: scenarios [(A_i, P_i), ...], W = min(A_i)
function GHPR(f):
    return product_i of (1 + A_i * (-f) / W)^P_i
optimal_f = argmax over f in (0, 1] of GHPR(f)   # 1D search
```

**Leverage-Space multi-component optimization** [ch.4, p.77-87]

```
Input: N scenario spectrums, joint-probability table rows k=1..n
       each row has (PL_{k,1}..PL_{k,N}, prob_k); BL_i per component
function GHPR(f_1..f_N):
    prod = 1
    for k in 1..n:
        HPR_k = 1 + sum_i f_i * (-PL_{k,i}) / BL_i
        prod *= HPR_k ** prob_k
    return prod
(f_1..f_N)* = argmax GHPR        # via genetic algorithm or equivalent [p.84]
# Rows with 0 empirical prob can be dropped to reduce n (125 → 12 in the Vince worked example [p.84])
```

**Risk-of-Ruin / Drawdown by full permutation enumeration** [ch.5, p.99-109]

```
Input: HPR_1..HPR_n (for N>1, one composite HPR per joint scenario via eq.5.06);
       barrier b; horizon q; mode in {RUIN, DRAWDOWN}
count_surviving = 0
for each permutation of length q drawn from {HPR_1..HPR_n} with replacement:  # n^q total
    running = 1.0
    ruined = False
    for hpr in permutation:
        if mode == DRAWDOWN and running > 1.0: running = 1.0   # floating high-water
        running *= hpr
        if running <= b: ruined = True; break
    if not ruined: count_surviving += 1
RX(b, q) = 1 - count_surviving / n^q
# Asymptotes as q grows; start the analysis at q=1 to resolve the asymptote [p.103]
```

Vince supplies bare-bones Java reference code reproducing this loop for one or more scenario spectrums, with a `usedrawdowninsteadofruin` flag [p.106-110]. The inner kernel is eq.5.03a, not a closed-form.

**Small-Martingale probability-of-profit search (Ch.7)** [p.165-167]

```
Input: N components' scenario spectrums; horizon q; target return r;
       drawdown constraint (b, maxProbRD)
function PP(z_minus, z_plus, f_1..f_N):
    profitable_branches = 0; total = n^q
    for each branch (sequence of q joint-scenario draws):
        acctEQ = acctEQ_0
        for period i in 1..q:
            for component k in 1..N:
                choose z = z_minus if acctEQ < acctEQ_0 else z_plus
                f$_{k,i} = (BL_k / -f_k) / (acctEQ_0 / acctEQ) ** (1/(1+z) - 1)
                U_{k,i} = acctEQ / f$_{k,i}
            acctEQ += sum_k U_{k,i} * outcome_{k,i}   # eq.7.07
        if acctEQ / acctEQ_0 - 1 >= r: profitable_branches += 1
    return profitable_branches / total
(z-*, z+*, f_1..f_N*) = argmax PP  subject to RD(b) <= maxProbRD
```

### Pitfalls e Anti-patterns

- [p.43, Fig.3.8] Believing a "cash account, no margin" is safe. Even with zero borrowing, every market system has an f > peak where GHPR < 1 and ruin is certain. Leverage is fundamentally the f value, not the borrow ratio.
- [p.44-45, p.150] Using "half-Kelly" as a safety dilution. It is a stationary heuristic oblivious to the migration of inflection points toward the peak as q grows. The claim that "half Kelly gives ¾ of the return with much less volatility" is "patently false" [p.44].
- [p.61-62, ch.4] Using Modern Portfolio Theory / mean-variance: four failure modes — assumes normality (fails on fat tails), uses variance-as-risk instead of drawdown, ignores leverage, and relies on correlation which fails on tail-event days.
- [p.65] Overallocating when pairwise correlation between components looks low on *all days* — correlations spike on big-move days. Build joint-scenarios tables from empirical data instead.
- [p.68] Being optimal on 99 of 100 component axes yet far-off on a single axis, so the GHPR drops below 1 and the whole portfolio loses money. One wrong quantity on one axis can negate N winning propositions [p.149].
- [p.92-93] Tucking "deeply toward 0…0" on all axes as a conservative safety play. You decrease returns geometrically while decreasing drawdowns only arithmetically; ignorance of the curve's shape leads to the mistaken belief that going from 1% to 2% "just doubles" drawdowns.
- [p.69-70] Using margin requirements to determine position size. They have no relationship to optimal f$.
- [p.49-51] Using the arithmetic mean HPR as the base of `(1+r)^q` for compounded growth. This is only correct when SDHPR=0. In trading, always use GHPR; the arithmetic mean materially overstates compound growth.
- [p.2-3] Evaluating a strategy by Mathematical Expectation alone, without a horizon lens. A positive-ME lottery can have 99.74% of players losing everything over their realistic horizon; a negative-ME insurance game is rational for finite-lifespan agents. "Mathematical Expectation must be utilized with the lens of a given horizon, a given lifespan" [p.4].
- [p.103] Forgetting to treat ruin/drawdown analysis as order-dependent. Permutations must all be enumerated (n^q); unlike optimal-f calculation, order matters for ruin metrics.
- [p.156-157, ch.6] Confusing *portfolio model* with *framework*. The static portfolio-model mindset (MPT, CAPM, half-Kelly) is obsolete; Leverage Space is a framework inside which migration functions realize specific criteria.

---

## From `books/systematic_trading.md`

### Regras de Trading Explícitas

- **REGRA [p.160, ch.10]**: Subsystem position = (volatility_scalar × forecast) / 10. Apply to every instrument, every day.
- **REGRA [p.173, ch.11]**: Portfolio position = subsystem_position × instrument_weight × IDM. IDM must never exceed 2.5 [p.170–171 (ch.11)].
- **REGRA [p.174, ch.11]**: Apply position inertia — do not trade if the rounded target position is within 10% of the current held position.
- **REGRA [p.133, ch.8]**: Cap combined forecast at ±20 after applying FDM. Never allow a combined forecast above +20 or below −20.
- **REGRA [p.144, ch.9]**: Set percentage volatility target = SR_realistic / 2 (Half-Kelly). For negative-skew strategies: SR_realistic / 4 [p.146 (ch.9)].
- **REGRA [p.146, ch.9]**: SR_realistic must be capped at 1.0 for staunch systems traders, regardless of how good the back-test looks. For semi-automatic traders, the maximum safe achievable SR is 0.5, so the volatility target must not exceed 25% [p.146 (ch.9)].
- **REGRA [p.187–188, p.196, ch.12]**: Accept a new instrument only if its annual cost ≤ 0.13 SR/year (systems traders, p.187–188) or ≤ 0.08 SR/year (asset allocators and semi-auto traders, p.196).
- **REGRA [p.212, ch.13]**: Semi-automatic stop loss uses X = 4 sigma_price_points from tracking extreme. On trigger: close the position only (no automatic reversal). Never modify the forecast after entering a trade [p.222 (ch.13)].
- **REGRA [p.222, ch.13]**: Do NOT use profit targets for semi-automatic trading — no consistent evidence they improve performance.
- **REGRA [p.122, ch.7]**: Prune any two trading rule variations with correlation > 0.95 — they add no independent information.
- **REGRA [p.116, ch.7]**: Asset allocating investor always uses forecast = +10 (constant buy). Never short via this archetype.
- **REGRA [p.201–202, ch.12]**: If maximum portfolio position < 4 blocks for any instrument at maximum forecast: increase instrument weight, reduce portfolio size, or remove the instrument.
- **REGRA [p.196–197, ch.12]**: Use 20-week volatility look-back for asset allocators (instead of 25-day) to reduce volatility-estimate-driven turnover.

---

### Fórmulas / Equações

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

### Algoritmos e Pseudocódigo

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

### Pitfalls e Anti-patterns

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
