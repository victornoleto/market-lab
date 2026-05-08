# The Evaluation and Optimization of Trading Strategies (Second Edition)

## Metadata
- **Author:** Robert Pardo [cover, p.ii]
- **Year:** 2008 [p.ix]
- **Publisher:** John Wiley & Sons (Wiley Trading series) [p.ii, p.iv]
- **Pages:** 367 (PDF); printed ~310 pages of body [metadata]
- **ISBN:** 978-0-470-12801-5 (cloth) [p.ix]
- **Primary focus:** Systematic method for designing, testing, and optimizing trading strategies using Walk-Forward Analysis (WFA) as the central defense against overfitting.

## 1. Core Thesis
Pardo's core thesis is that optimization and overfitting are NOT synonyms: "Optimization refers to the process whereby a trading strategy is tested and refined so as to produce the best possible real-time trading profits... Overfitting... is optimization that has gone bad. Overfitting, then, is incorrect testing." [p.7, ch.1]. Optimization done correctly is essential; what causes failure is violating statistical principles. The method Pardo invented and champions as "the only 99 percent foolproof method of optimizing a trading strategy" is **Walk-Forward Analysis** — judged exclusively on out-of-sample performance [p.1, Introduction; p.237, ch.11]. The book argues that a strategy should only go to production after passing the 8 stages of the scientific development cycle (formulation → specification → preliminary testing → multimarket/multiperiod optimization → WFA → trading → monitoring → refinement) [p.43-55, ch.3].

## 2. Main Concepts
- **Trading Strategy (systematic)** — set of objective, formalized rules, external to human judgement, that trigger entries/exits/risk [p.11-12, ch.1; p.73, ch.5].
- **Three Principal Components** — every strategy has: (1) entry/exit, (2) risk management, (3) position sizing [p.74, ch.5].
- **Optimization** — "To make the best or most effective use of" — empirical identification, via historical simulation, of the most robust parameter set [p.51, ch.3; p.211, ch.10].
- **Overfitting** — "Fit to an unwanted or excessive degree"; optimization that identifies parameters that profit in-sample but lose out-of-sample [p.282, ch.13].
- **Walk-Forward Analysis (WFA)** — sequence of individual walk-forwards (in-sample optimization + adjacent out-of-sample trading) rolling over the entire history [p.237, 248-251, ch.11].
- **Walk-Forward Efficiency (WFE)** — ratio of annualized out-of-sample profit to annualized in-sample profit; measures optimization quality [p.238-239, 260, ch.11].
- **Optimization Profile** — set of all simulations of an optimization, analyzed for (1) % of profitable parameter sets, (2) distribution of performance, (3) shape (smoothness vs. spikiness) [p.226-227, ch.10].
- **Robust Strategy** — "able to withstand or overcome adverse conditions"; performs over a wide range of parameter sets, across all market types, over multiple periods, across multiple markets [p.225-226, ch.10].
- **Objective Function (search function / fitness function)** — algorithm that ranks and selects the top parameter set (net profit, PROM, CECPP, Sharpe, etc.) [p.180, 201, ch.9].
- **Perfect Profit (PP)** — sum of all possible swings (buy every bottom, sell every top); theoretical benchmark [p.273, ch.12].
- **Model Efficiency (ME)** — `Net Profit / Perfect Profit`; ≥ 5% is considered very good [p.274, ch.12].
- **Pessimistic Return on Margin (PROM)** — conservative metric that adjusts wins by `-√N_wins` and losses by `+√N_losses` [p.205-207, ch.9].
- **Required Capital (RC)** — capital required: margin + MDD x safety factor [p.83, ch.5; p.270-272, ch.12].
- **Strategy Stop-Loss (SSL)** — abandonment threshold based on a multiple of MDD [p.305-307, ch.14].
- **Theory of Relevant Data** — more recent/similar-to-current market data is more valuable than "more data is always better" [p.243-244, ch.11].
- **Four Major Market Types** — (1) Bullish, (2) Bearish, (3) Congested, (4) Cyclic — the history must contain at least one of each [p.221, ch.10].
- **Degrees of Freedom** — each data point is 1 DoF; rules and data consumed by indicators reduce DoF. Minimum: retain ≥ 90% [p.292-295, ch.13].

## 3. Formulas / Equations
**Strategy Stop (strategy risk)** [p.83, ch.5]

$$\text{Strategy Stop} = \text{MDD} \times \text{Safety Factor}$$

Example: MDD=$40k, SF=1.5 → Stop=$60k.

**Required Capital (conservative version)** [p.83-84, ch.5; p.271, ch.12]

$$RC = \text{Margin} + (\text{MDD} \times \text{Safety Factor})$$

Conservative variant (double drawdown): $RC = \text{Margin} + 2 \times (\text{MDD} \times SF)$. For MDD=$40k, margin=$15k, SF=1.5 → $RC = 15k + 2 \times (40k \times 1.5) = \$135k$.

**Risk-Adjusted Return (RAR), annualized** [p.272-273, ch.12]

$$RAR_{annual} = \frac{\text{Annualized Profit}}{\text{Margin} + \text{Risk}}$$

Where Risk is usually $MDD \times 2$. Book example: AP=$25k, Margin=$10k, Risk=$40k → RAR = 50%.

**Reward-to-Risk Ratio (RRR)** [p.273, ch.12]

$$RRR = \frac{\text{Net Profit}}{\text{Maximum Drawdown}}$$

Annualized. Rule: RRR ≥ 3 is desirable.

**Model Efficiency (ME)** [p.274, ch.12]

$$ME = \frac{\text{Net Profit}}{\text{Perfect Profit}} \times 100\%$$

ME ≥ 5% = very good strategy. Perfect Profit = absolute sum of all peak-to-valley swings.

**Walk-Forward Efficiency (WFE)** [p.238, 260, ch.11]

$$WFE = \frac{\text{Annualized Walk-Forward P\&L}}{\text{Annualized Optimization P\&L}}$$

Rule: WFE ≥ 50–60% indicates a robust strategy; WFE ≤ 25% indicates overfitting or a poor strategy [p.239, ch.11].

**Pessimistic Return on Margin (PROM)** [p.205-206, ch.9]

$$PROM = \frac{[AW \times (N_W - \sqrt{N_W})] - [AL \times (N_L + \sqrt{N_L})]}{\text{Margin}}$$

- $AW$ = average win, $AL$ = average loss [p.205-206, ch.9]
- $N_W$ = number of wins, $N_L$ = number of losses [p.205-206, ch.9]
- The standard-error adjustment penalizes small samples (e.g., 9 trades → 33% penalty via √9/9) [p.207, ch.9].

**Correlation Equity Curve vs. Perfect Profit (CECPP)** [p.204-205, ch.9]

$$\rho_{CECPP} = \frac{\sum_i (x_i - \bar{x})(y_i - \bar{y})}{(n-1) \cdot SD_x \cdot SD_y}$$

- $x$ = Perfect Profit (cumulative); $y$ = Equity Curve [p.204-205, ch.9]
- Range [-1, +1]; values close to +1 indicate the strategy captures market opportunity [p.205, ch.9].

**Standard Error (sample size sensitivity)** [p.295, ch.13]

$$SE\% = \frac{1}{\sqrt{N_{trades}}}$$

N=10 → 31.6%; N=100 → 10%; N=1000 → 3%. Practical minimum: 30–50 trades.

**Degrees of Freedom check** [p.292-294, ch.13]

$$DoF_{remaining}\% = \frac{N_{data\_points} - N_{consumed\_by\_indicators\_and\_rules}}{N_{data\_points}}$$

Rule: keep ≥ 90% of DoF free.

**Volatility-based Risk Stop (example)** [p.81-82, ch.5]

$$\text{Stop}_{long} = \text{Entry} - k \times \overline{\text{Range}}_{n}$$

Example: k=1, average true/daily range over 3d = 5.55 pts → stop 5.55 pts below entry.

## 4. Algorithms and Pseudocode
**Algorithm 1: The 8-Step Trading Strategy Development Process** [p.43-55, ch.3]

```
1. Conceptualize and formulate the strategy (hypothesis).
2. Specify rules in computer-testable form (script).
3. Preliminary testing (verify script == concept; rough P/L on
   small basket of markets and time periods).
4. Optimize: multimarket, multiperiod optimization.
5. Validate with Walk-Forward Analysis (WFA).
6. Trade in real time (take every signal).
7. Monitor real-time performance vs. evaluation profile.
8. Refine/evolve; re-run entire cycle on changes.
```

**Algorithm 2: Single Walk-Forward (WF)** [p.247-248, ch.11]

```
Input: strategy, parameter scan ranges, objective_fn,
       opt_window_size, walk_forward_window_size, history
Step 1 (Optimization):
    run grid/directed search over parameter space on
      history[t_start : t_start + opt_window_size]
    rank by objective_fn
    top_params = best according to objective_fn
Step 2 (Out-of-sample trade):
    simulate strategy with top_params on
      history[t_start + opt_window_size :
              t_start + opt_window_size + walk_forward_window_size]
    record OOS P&L, drawdown, WFE = OOS_annual / IS_annual
Output: top_params, IS_stats, OOS_stats, WFE
```

**Algorithm 3: Full Walk-Forward Analysis (WFA)** [p.249-251, ch.11]

```
Input: strategy, scan_ranges, objective_fn,
       opt_window, wf_window, step_window, full_history
walk_forwards = []
t = full_history.start
while (t + opt_window + wf_window) <= full_history.end:
    top_params, is_stats, oos_stats, wfe = single_WF(
        history[t : t + opt_window + wf_window],
        opt_window, wf_window, scan_ranges, objective_fn)
    walk_forwards.append((top_params, is_stats, oos_stats, wfe))
    t += step_window

# Reduce:
aggregate_wf_pnl = sum(w.oos_stats.pnl for w in walk_forwards)
pct_profitable_wfs = count(w.oos_stats.pnl > 0) / len(walk_forwards)
avg_WFE = mean(w.wfe for w in walk_forwards)
# Robustness criteria:
#   - majority of WFs profitable
#   - avg WFE >= 50-60% (Pardo target)
#   - small std deviation of WFE
Output: aggregate summary, per-WF table
# Typical sizing: opt_window 3-6yr slow strat, 1-2yr fast;
# wf_window = 25-35% of opt_window [p.249]
```

**Algorithm 4: Multimarket/Multiperiod Optimization** [p.223-225, ch.10]

```
for each market in diversified_basket (≥ 10 markets):
    for each period in disjoint_time_samples (e.g., 5 × 2-year):
        run_optimization(strategy, market, period, scan_ranges)
        record optimization_profile
# Total scans example (10 markets × 5 periods × 96 param sets)
# = 4,800 simulations [p.225]
# Decision:
#   Excellent & consistent → go to WFA
#   Marginal → proceed with caution
#   Poor majority → abandon
```

**Algorithm 5: Genetic Algorithm for parameter search** [p.195-197, ch.9]

```
1. Random initial population of parameter sets.
2. Selection: copy pairs proportional to fitness (objective_fn).
3. Crossover: swap parameter slices between pairs.
4. Mutation: randomly replace some params (low rate).
5. Repeat until convergence (no improvement) or max generations.
# GA typically evaluates only 5-10% of full space.
```

**Algorithm 6: PROM calculation** [p.205-207, ch.9]

```
adj_wins   = N_W - sqrt(N_W)
adj_losses = N_L + sqrt(N_L)
AAGP = (Gross_Profit / N_W) * adj_wins
AAGL = (Gross_Loss / N_L) * adj_losses
PROM = (AAGP - AAGL) / Margin
# Variants (more stringent):
#   PROM - biggest_win
#   PROM - biggest_winning_run
```

## 5. Explicit Trading Rules
- **RULE [p.3, Intro]**: Never run an optimizable strategy without Walk-Forward Analysis. "The only model that I trust that does not use WFA is the model that requires no optimization."
- **RULE [p.53, ch.3]**: After a strategy passes WFA, take ALL signals it generates; "Trading strategies work. System traders do not." — Larry Williams, quoted by Pardo.
- **RULE [p.74, ch.5]**: Every strategy must have three explicit components: entry/exit, risk management, position sizing.
- **RULE [p.80, ch.5]**: The risk stop must be entered WITH the position (at inception) and kept GTC until exit.
- **RULE [p.83, ch.5]**: Minimum Required Capital = Margin + MDD x Safety Factor (SF=1.5 minimum; 3x recommended for conservatism).
- **RULE [p.217, ch.10]**: Minimize the number of optimizable parameters. The more parameters, the higher the probability of overfit.
- **RULE [p.220, ch.10]**: The historical sample must contain at least 30 trades (ideally 50+); ideally at least one instance of each of the 4 market types (Bullish, Bearish, Congested, Cyclic).
- **RULE [p.239, ch.11]**: WFE ≥ 50–60% = robust. WFE ≤ 25% = overfit or poor strategy; reject or revise.
- **RULE [p.248, ch.11]**: Typical WF window = 25–35% of the optimization window.
- **RULE [p.249, ch.11]**: Fast strategy → opt_window 1–2 years; slow strategy → opt_window 3–6 years.
- **RULE [p.244, ch.11]**: An ideal WFA covers 10–20 years, generating 10–20+ individual walk-forwards.
- **RULE [p.249, ch.11]**: A model optimized over 2 years of data has a shelf life of 3–6 months; over 5 years, 1–2 years. Re-optimize DISCIPLINED at the end of each walk-forward window, "whether or not the strategist thinks it needs it or not" [p.254].
- **RULE [p.273, ch.12]**: Annualized RRR should be three or better (≥ 3).
- **RULE [p.274, ch.12]**: Model Efficiency ≥ 5% is considered very good.
- **RULE [p.294-295, ch.13]**: Keep ≥ 90% of degrees of freedom free after consumption by indicators and startup overhead.
- **RULE [p.297, ch.13]**: Scan step size must be proportional to the magnitude of the parameter. Example: short MA 2–14 step 1 OK; long MA 20–200 step 1 is overscanning (use step 5–10).
- **RULE [p.297, ch.13]**: An optimization profile is "robust" if ≥ 40% of parameter sets are profitable.
- **RULE [p.305-307, ch.14]**: Establish a Strategy Stop-Loss BEFORE going live. When hit, stop trading or reduce exposure (free-fall check).
- **NEVER [p.202, ch.9]**: Use Net Profit as the sole objective function — it ignores risk, distribution, and statistical validity.
- **NEVER [p.284-286, ch.13]**: Add rules/parameters based on hindsight without re-testing over a wide range of periods and markets.
- **NEVER [p.296-298, ch.13]** (Big Fish in Small Pond): Trust a strategy whose profit concentrates in 1–2 large trades within a small sample.
- **NEVER [p.220, ch.10]**: Operate with a trade sample < 30 (ideal 50+).

## 6. Pitfalls and Anti-patterns
- **Overfitting (5 main causes)** [p.291-292, ch.13]:
  1. Insufficient degrees of freedom.
  2. Inadequate data and trade sample.
  3. Incorrect optimization methods (overparameterization, overscanning).
  4. A big win in a small trade sample ("big fish in small pond").
  5. Absence of a Walk-Forward Analysis.
- [p.217, ch.10] **Overparameterization** — 5 parameters with 10 candidates each = 100,000 simulations; very high overfit risk. Use the fewest possible.
- [p.218-219, ch.10] **Overscanning** (too small a step size) artificially inflates the % of profitable simulations, misleading the robustness metric.
- [p.283-285, ch.13] **Abuse of hindsight** — adding a bullish bias after observing a bull market; adding a stop after the fact because "it would have avoided that big loss". Both destroyed strategies without re-testing.
- [p.286-289, ch.13] **Overfit forecasting model** — the statistician adding variables until the curve touches every twist in history; zero real predictive power.
- [p.293-294, ch.13] **Startup overhead** — a 50d MA on a 100d sample consumes 50% of the data before the first trade; unacceptable.
- [p.326, ch.13] **Strategy scan bias** — longer parameters consume more DoF, generating a smaller sample → bias in favor of short parameters in the optimization.
- [p.78-79, ch.5] **Filter creep** — adding multiple filters increases complexity and the probability of overfit ("a different filter for every bar" = absurdly overfit model with unreal simulated profit and real-time failure).
- [p.46-47, ch.3] **Black-box empirical strategies** (neural nets, opaque ML) — described as "the ultimate curve-fitting technology" (common usage; Pardo reluctant to apply them without rigorous WFA).
- [p.202, ch.9] **Single-criterion evaluation** (e.g., Net Profit only) — ignores risk, distribution, statistical validity; promotes overfitting.
- [p.311-312, ch.14] **Abandoning a strategy after 3 bad trades** — without a precisely defined pre-trade "falling apart" criterion, the trader is left without psychological anchor.
- [p.311-312, ch.14] **Run-up euphoria** — gains larger than expected are also a deviation signal; rising volatility = larger next drawdowns.
- [p.200, ch.9] **Spiky optimization space** — isolated performance peaks surrounded by bad parameter sets; likely a statistical artifact, not genuine robustness.
- [p.267-268, ch.12] **Underestimated historical MDD** — if the simulation was in low volatility, real-time in high vol will produce larger drawdowns; undercapitalization = risk of ruin.
- [p.272, ch.12] **Undercapitalization** — "one of the most common causes of trading failure".

## 7. Sensitive Parameters
- **Optimization window size** [p.249, ch.11]: Pardo says it is NOT arbitrary — it is EMPIRICALLY determined by WFA. "The size of the estimation or optimization window and the size of the out-of-sample or walk-forward window are simply two more variables in the trading strategy" [p.220, ch.10]. Start: 1–2 years for fast strategies; 3–6 years for slow ones.
- **Walk-forward window size** [p.249, ch.11]: 25–35% of the opt window. Empirical.
- **Safety Factor for Required Capital** [p.83, ch.5]: Pardo uses 1.5 as default; 3 for conservatism. Justification: statistical margin of error in the MDD measurement (MDD is an unstable estimator).
- **Minimum trade sample** [p.220, ch.10; p.295, ch.13]: 30 trades traditional; 50+ ideal; mathematical justification via SE = 1/√N.
- **Minimum degrees of freedom** [p.294, ch.13]: 90% remaining after indicators. Statistical rule, not arbitrary.
- **Percentage of profitable parameter sets** [p.297, ch.13]: ≥ 40% = robust optimization. Justification: statistical floor — below that could be chance.
- **Optimization scan step size** [p.252, ch.10]: Keep step proportional in % (not absolute). Example: MA 20 step 1 (5% change) ≈ MA 100 step 5 (5% change). Avoids artificial count inflation.
- **MDD multiplier for Strategy Stop-Loss** [p.305-307, ch.14]: 2–3x historical MDD. Justification: real-time volatility > backtest.
- **Objective function selection** [p.201-209, ch.9]: Net Profit alone is bad (reason: ignores risk and sample). PROM is conservative and recommended. Pardo uses PROM or combinations with floors/ceilings [p.208-209].

## 8. Key Literal Quotes
> "Walk-Forward Analysis (WFA) [is] the only 99 percent foolproof method of optimizing a trading strategy. The only model that I trust that does not use WFA is the model that requires no optimization." — [p.1, Introduction]

> "Optimization refers to the process whereby a trading strategy is tested and refined so as to produce the best possible real-time trading profits. Optimization then is testing done correctly. Overfitting, which no sane strategist ever does intentionally, is optimization that has gone bad. Overfitting, then, is incorrect testing." — [p.7, ch.1]

> "Trading strategies work. System traders do not." — Larry Williams, quoted by Pardo [p.53, ch.3]

> "With enough variables, a curve can be fit perfectly to any time series. Will this perfectly fit curve, though have any predictive value? Probably not — too many constraints, too few data, and not enough testing make for a bad model." — [p.287, ch.13]

> "A walk-forward is a two-step process. The trading strategy is first optimized on a historical sample. It is then traded on a new and unseen historical sample. This process is also known as out-of-sample testing or double-blind testing." — [p.247, ch.11]

> "Research has clearly demonstrated that robust trading strategies have WFEs greater than 50 or 60 percent and in the case of extremely robust strategies, even higher." — [p.239, ch.11]

> "Overfitting is optimization performed incorrectly. More specifically, the overfitting or overoptimizing of a trading strategy is the identification of parameters that produce good trading performance on in-sample price history but produce poor trading performance on out-of-sample price history." — [p.282-283, ch.13]

## 9. Cross-references to Other Books in This Knowledge Base
- **Walk-Forward Analysis** [p.237, ch.11] is also treated in `testing_tuning.md` (Masters, "Testing and Tuning Market Trading Systems") — Masters formalizes WFA with bootstrap and Monte Carlo permutation tests; Pardo is the original historical source of the term (1991 DTOTS) and focuses on practical workflow. Complementary reading: Pardo's WFE + Masters's permutation p-values.
- **Out-of-sample / CPCV** in `advances_fin_ml.md` (López de Prado) — López de Prado evolves the WFA concept into Combinatorial Purged Cross-Validation (CPCV) with purging and embargo; the same philosophical concern as Pardo but with probabilistic formalization and correction for data leakage via overlapping labels. Pardo [p.237] and López de Prado converge on: "performance on out-of-sample is the only trustworthy evaluator".
- **Parameter parsimony** in `systematic_trading.md` (Carver) — Carver proposes 3–4 max parameters via bottom-up design; Pardo [p.217] reaches the same conclusion via a statistical path (DoF + overfit risk).
- **Overfitting / data snooping bias** in `evidence_based_ta.md` (Aronson) — Aronson formalizes "data mining bias" with Monte Carlo tests; complements Pardo's qualitative description of the five causes of overfit [p.291].
- **Position sizing / Optimal f** in `leverage_space.md` (Vince) — Pardo [p.75, ch.5] says "many professional trading strategists believe that the sizing principle is more important than the trading strategy itself" but does not develop it; Vince and Carver (systematic_trading) provide the mathematical treatment.
- **MDD-based sizing** [p.271, ch.12] in `risk_parity.md` and `volatility_trading.md` — Pardo uses MDD x safety factor as a base; risk_parity treats volatility-targeting as a forward-looking alternative.
- **Perfect Profit / Model Efficiency** [p.273-274, ch.12] — original Pardo concept (DTOTS 1991); I have not seen direct replication in other summaries in this knowledge base. Possible analog: "benchmark alpha" in ml_for_asset_managers, but different in definition.
- **Objective function selection (PROM)** [p.205-209, ch.9] — not equally addressed in other books; Pardo invented PROM and is the canonical source.
