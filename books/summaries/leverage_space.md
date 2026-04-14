# The Leverage Space Trading Model: Reconciling Portfolio Management Strategies and Economic Theory

## Metadata
- **Autor:** Ralph Vince [p.iii, p.xi]
- **Ano:** 2009 [p.iv]
- **Editora:** John Wiley & Sons, Inc., Hoboken, New Jersey (Wiley Trading series) [p.iv]
- **Páginas:** ~206 (print body numbered to ~190) [metadata]
- **ISBN:** 978-0-470-45595-1 (cloth) [p.iv]
- **Foco principal:** A framework (not merely a portfolio model) for position sizing in N+1-dimensional "leverage space", where optimal f is generalized to multiple simultaneous scenario-based components, risk is defined as drawdown (not variance), and migration functions maximize probability of profit rather than geometric growth.

## 1. Tese Central

Every trader, on every trade, occupies an *ineluctable* coordinate `f` between 0 and 1 on a geometric-growth curve — "whether they acknowledge it or not" — and the dynamics of that curve (peak, points of inflection, the point beyond which TWR<1 and ruin is certain) dictate outcomes more than signal selection or timing [ch.1-3, p.7-57]. For N simultaneous components, this curve becomes an N+1–dimensional surface in "leverage space", parameterized only by joint scenario probabilities — NOT by correlation coefficients, which fail precisely on the fat-tail days when you need them most [ch.4, p.61-72]. Risk is redefined as probability of drawdown RD(b), not variance in returns [ch.5, p.89-120]. In Part III, Vince pivots: the goal is rarely growth-optimality; portfolio managers and their clients want *probability of profit at a horizon*, which is accomplished via a small-Martingale migration function through the leverage-space terrain, consistent with Prospect Theory [ch.6-7, p.141-167].

## 2. Conceitos-Chave

- **Optimal f** — the fixed fraction of stake (0 ≤ f ≤ 1) that maximizes geometric mean HPR; bounded by dividing the per-unit biggest loss into f$ [p.16-18, ch.1]
- **f$** — dollar amount capitalizing each unit: `f$ = |BiggestLoss| / f` [p.18, eq.1.09]
- **HPR(f), TWR(f), GHPR(f)** — Holding Period Return, Terminal Wealth Relative (product of HPRs), Geometric mean HPR (nth root of TWR) [p.16-17, eqs.1.06-1.08]
- **Scenario spectrum** — a binned discrete distribution of outcomes (Ai) with probabilities (Pi) for one tradable; replaces Normal assumption [p.24, ch.2]
- **Biggest Loss (BL/W)** — worst perceived per-unit loss; used solely to bound f between 0 and 1. It does NOT affect the number of units optimally traded [p.25, Table 2.1]
- **Leverage Space** — the N+1–dimensional surface (f1…fN axes + GHPR altitude) where every N-component portfolio has an ineluctable location [p.65-67, ch.4]
- **Market system** — a given approach applied to a given market; one component in a portfolio [p.5]
- **Two facets of leverage** — (1) static cash-vs-position ratio, (2) schedule of adding/trimming as equity fluctuates. Both collapse into the single number f [p.43-44, Fig.3.9]
- **Point of inflection** — dTWR(f)/df sign-change points; left-of-peak inflection marks fastest marginal growth but migrates toward the peak as q→∞ [p.41-42]
- **Point of certain ruin** — the f value (always <1) beyond the peak where GHPR<1, even in a cash account [p.43, Fig.3.8]
- **AHPR(f), SDHPR(f), VHPR(f)** — arithmetic mean, std-dev, and variance of HPRs [p.49-51]
- **EGM(f)** — estimated geometric mean = √(AHPR² − SDHPR²) [p.51, eq.3.10]
- **Fundamental Equation of Trading** — `TWR(f) = (AHPR² − SDHPR²)^(q/2)` [p.54, eq.3.11b]
- **RR(b) — Risk of Ruin** — probability of hitting lower absorbing barrier b × initial stake [p.94-99, ch.5]
- **RD(b) — Risk of Drawdown** — probability of a (1−b) regression from equity high; far more germane than RR in practice [p.105-106, eq.5.03a]
- **Joint-scenarios table** — the only input needed for multi-component Leverage Space; replaces pairwise correlation [p.63-66]
- **Migration function** — the path an investor traces through leverage space as equity fluctuates. Every position-sizing rule ("1% rule", half-Kelly, MPT) is implicitly one [p.149-151, ch.6]
- **Probability of Profit PP(r)** — probability that TWR after q periods ≥ 1+r; the new criterion Vince adopts in Part III [p.165-166, eqs.7.05-7.06]
- **Martingale exponents z−, z+** — the two levers (for under-water and above-water equity states) that govern the small-Martingale migration function in Ch.7 [p.161-164, eqs.7.01-7.03]

## 3. Fórmulas / Equações

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

## 4. Algoritmos e Pseudocódigo

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

## 5. Regras de Trading Explícitas

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

## 6. Pitfalls e Anti-patterns

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

## 7. Parâmetros Sensíveis

- **BiggestLoss (W, BL)** — [p.25-26, Table 2.1] Vince explicitly shows that varying BiggestLoss from −0.6 to −29 changes only the reported optimal *f* fraction (0.15 → 7.25); the resulting *f$* and therefore *actual unit count* stay identical. This is an economic/invariance property, not curve-fit: the parameter's job is only to bound f in [0,1]. Choose the worst perceived loss you can budget for.
- **Number of bins per scenario spectrum** — [p.79] NOT required to be equal across spectrums; equispaced binning not required either. "Fewer scenarios = quicker calculation but greater information loss" [p.87]. Vince uses 5 bins on 13 monthly data points in the worked three-system example — a pragmatic not optimized choice.
- **Drawdown threshold b** — [p.96-99] Judgement call. b=0.6 (tolerate 40% drawdown) is used in all Ch.5 worked examples; no claim that 0.6 is optimal — it is an illustration. Practitioner should match b to capital-permanence requirements.
- **Horizon q for PP(r) optimization** — [p.165] Must be specified in advance. A wider q generally lowers permissible f aggression for a given PP target.
- **Martingale exponents z−, z+** — [p.162-163] Vince demonstrates (z−=−0.7, z+=−0.3) as a "typical" example but does not claim these are universally optimal. Optimize per strategy / client profile. Values z− < −1 are forbidden (eq.7.01); z = 0 reduces to constant-fractional-of-equity sizing (no Martingale at all).
- **f_1…f_N initial values in Martingale migration** — [p.165] must be jointly optimized with (z−, z+) since (7.03) depends on *initial* f_k as anchor.

## 8. Citações Literais Importantes

> "Everyone, on every trade, on every opportunity involving risk, has an f value whether they acknowledge it or not." — [p.21]

> "You are not borrowing any money to do this… It is, in effect, a cash account, no margin is even being used; it is a wildly favorable game, and yet, you go broke with a probability that approaches certainty as you continue to play." — [p.43]

> "Using correlation is dangerous as it fails us during those critical periods when we are counting on it the most. Using correlation as an important input to an allocation model will cause us to be badly misled." — [p.65]

> "Clearly, Mathematical Expectation, a cornerstone of gambling theory, of money management as well as Economic Theory, must be utilized with the lens of a given horizon, a given lifespan." — [p.4]

> "In other words, the peak in leverage space, juxtaposed to risk (drawdown) is not our criterion. Instead, we seek to create a function to migrate through leverage space in a manner that satisfies our criterion." — [p.150]

> "The Kelly criterion is never the point that maximizes the growth of capital, except in the abstract case of an infinite number of plays… To trade at the optimal f point, in other words, to satisfy the Kelly criterion… does not maximize the growth of capital, and will always be suboptimal." — [p.37-38 footnote]

## 9. Conexões com Outros Livros Desta Base

- **Kelly / half-Kelly dilution** is also treated in `systematic_trading.md` (Carver) — Carver recommends *half-Kelly* explicitly (`vol target = 0.5 × realistic Sharpe`), whereas Vince [p.44, p.150] argues half-Kelly is an arbitrary heuristic that ignores the migration of mathematically significant points. These summaries genuinely disagree; the divergence is a design decision worth flagging in the ai-trade Phase-0 anti-overfit review.
- **Drawdown as the real risk metric** (not variance) matches Carver's preference for caring about actual drawdown equity curves over Sharpe-style variance penalties (`systematic_trading.md` §Half-Kelly / §Volatility target). [p.44, p.150]
- **Scenario-based (empirical, non-parametric) return modeling** in Ch.4 parallels the empirical-distribution emphasis of `evidence_based_ta.md` (Aronson) and `ml_for_asset_managers.md` (López de Prado), though Vince's joint-scenarios table is a more aggressive non-parametric construction than they discuss. [p.44, p.150]
- **Fat-tail / correlation-breakdown warning** [p.65] cross-references the rolling-correlation instability themes in `regime_change.md` (regime-conditional statistics) — different language, same empirical fact.
- **Fundamental Equation of Trading** `TWR = (AHPR² − SDHPR²)^(q/2)` [p.54] is the geometric-growth counterpart to the Sharpe/Law-of-Active-Management identity in `systematic_trading.md` (SR ∝ √N). Both say that reducing dispersion and increasing independent bet count dominate mean-return chasing.
- No direct cross-ref in this knowledge base for Vince's Ch.7 small-Martingale probability-of-profit optimization — it is a Vince-unique contribution. [p.54]
