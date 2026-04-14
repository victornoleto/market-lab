# Detecting Regime Change in Computational Finance: Data Science, Machine Learning and Algorithmic Trading

## Metadata
- **Autor:** Jun Chen, Edward P K Tsang [p.4]
- **Ano:** 2021 [p.5]
- **Editora:** CRC Press (Taylor & Francis Group) [p.5]
- **Páginas:** 165
- **ISBN:** 978-0-367-53628-2 (hbk) [p.5]
- **Foco principal:** Detecting and tracking regime changes in financial markets using Directional Change (event-based sampling) combined with Hidden Markov Models and Naive Bayes classifiers, as an alternative and complement to time-series analysis.

---

## 1. Tese Central

The book argues that financial market regime changes — significant shifts in the collective trading behaviour of market participants — can be detected, classified, and tracked more effectively by using Directional Change (DC), a data-driven event-based sampling framework, rather than or alongside conventional time series analysis [p.1–3, ch.1]. Rather than sampling prices at fixed time intervals, DC samples only when the market has moved by a pre-defined threshold percentage from its last extreme point, capturing only "significant" price movements and filtering noise [p.8–9, ch.2].

The central operational claim is that DC, combined with Hidden Markov Models (HMM) for retrospective regime detection and Naive Bayes classifiers for real-time tracking, provides a complementary lens to time series: together they give a richer picture of when markets transition between normal (low-volatility) and abnormal (high-volatility) regimes — and that this information can be operationalised to consistently reduce maximum drawdown in algorithmic trading, even if total profitability is not improved by naive implementations [p.89–91, ch.6].

---

## 2. Conceitos-Chave

- **Regime Change (RC)** — a significant change in the collective trading behaviour of market participants, observable through changes in statistical properties of price movements (mean, volatility, correlation); not directly observable, but inferred from price dynamics [p.5–6, ch.2]

- **Directional Change (DC)** — an event-based, data-driven approach to sampling price movements; a price point is recorded only when the market reverses direction by at least a pre-defined threshold θ. Introduced by Guillaume et al. (1997). Known in technical analysis as the "Zigzag indicator" [p.8–9, ch.2]

- **Threshold (θ)** — the percentage price change required to confirm a DC event; defined by the observer. Different thresholds reveal market dynamics at different scales; DC scaling laws hold across thresholds [p.9, ch.2]

- **DC Event** — confirmed when $|P_t - P_{EXT}| / P_{EXT} \geq \theta$, i.e., the price has moved from the last extreme point by at least θ; the extreme point is then retrospectively confirmed [p.10, ch.2]

- **Overshoot (OS) Event** — price movement between one DC confirmation point and the next DC event (continuation of the current trend beyond the initial DC reversal confirmation) [p.10, ch.2]

- **Extreme Point (EXT)** — the peak or trough retrospectively confirmed at each DC event; the anchor for computing DC indicators [p.10, ch.2]

- **Total Price Movement (TMV)** — DC indicator: normalised percentage price change from one extreme to the next; $TMV = \frac{|P_s - P_e|/P_s}{\theta}$ [p.42, ch.4]

- **Time for Completion (T)** — DC indicator: number of time units elapsed between successive extreme points [p.42, ch.4]

- **Time-Adjusted Return (R)** — DC indicator: rate of price change per time unit; $R = \frac{|TMV| \times \theta}{T}$. Primary HMM input for regime detection [p.43, ch.4]

- **Hidden Markov Model (HMM)** — probabilistic model that infers a hidden state sequence (market regimes) from observable sequences (DC indicators). Trained via Expectation-Maximization (Baum-Welch). Used with 2 states throughout the book; implemented via `depmixS4` in R [p.14–17, ch.2]

- **Normal Regime (Regime 1)** — market period with lower volatility; trends present lower TMV/T ratio in normalised indicator space [p.44, ch.4]

- **Abnormal Regime (Regime 2)** — market period with higher volatility; trends complete with larger TMV in shorter T; observed following significant external events (financial crises, political shocks) [p.44–46, ch.4]

- **Naive Bayes Classifier (NBC)** — statistical classifier used for real-time regime tracking; computes posterior regime probability using Bayes' theorem and class-conditional Gaussian distributions; assumes feature independence [p.18–19, ch.2]

- **Scaling Laws** — empirical power-law relationships between DC-derived quantities; Glattfelder et al. (2011) discovered 12 such laws in FX markets, unobservable under conventional time series [p.11, ch.2]

- **B-Simple / B-Strict** — two decision rules combining NBC output for regime classification: B-Simple picks the highest probability regime; B-Strict additionally requires $p(C_2|x) > \text{threshold}_2 = 0.8$ to conclude Regime 2, reducing false alarms [p.70–71, ch.5]

---

## 3. Fórmulas / Equações

**DC Event Condition** [p.10, ch.2 eq. 2.1]

$$\frac{|P_t - P_{EXT}|}{P_{EXT}} \geq \theta$$

- $P_t$ = current price; $P_{EXT}$ = price at last extreme point; $\theta$ = threshold [p.10, ch.2]

---

**Total Price Movement (TMV)** [p.42, ch.4 eq. 4.1]

$$TMV = \frac{|P_s - P_e|/P_s}{\theta}$$

- $P_s$ = price at trend start (extreme point); $P_e$ = price at trend end (next extreme point); $\theta$ = threshold [p.42, ch.4]

---

**Time-Adjusted Return (R)** [p.43, ch.4 eq. 4.2]

$$R = \frac{|TMV| \times \theta}{T}$$

- $T$ = time elapsed between successive extreme points [p.42, ch.4]
- Higher R indicates larger price change in less time — proxy for volatility intensity under DC [p.43, ch.4]

---

**TMV indicator (alternative form with extreme points)** [p.12, ch.2 eq. 2.2]

$$TMV_{EXT}(n) = \frac{P_{EXT}(n) - P_{EXT}(n-1)}{P_{EXT}(n-1) \times \theta}$$

where $P_{EXT}(n)$ is the price at the $n$-th extreme point.

---

**Log-transformed DC indicator (HMM input)** [p.27, ch.3 eq. 3.1]

$$LR[t] := \log(R[t])$$

Applied before feeding R into HMM to address right-skew in R distributions.

---

**Realised Volatility (time-series benchmark)** [p.27, ch.3 eq. 3.2]

$$RV(t) = \sum_{i=1}^{n} r_t^2(i)$$

- $r_t(i)$ = 5-minute log return at interval $i$; $n$ = number of 5-minute intervals in one trading day [p.27, ch.3]
- Used as the time-series counterpart to R for head-to-head regime detection comparison in Chapter 3 [p.27, ch.3].

---

**HMM Markov Assumption** [p.15, ch.2 eq. 2.5]

$$P(q_i = a \mid q_1 \ldots q_{i-1}) = P(q_i = a \mid q_{i-1})$$

The current hidden state depends only on the immediately preceding state.

---

**Naive Bayes Posterior** [p.18, ch.2 eq. 2.6–2.7; also p.63, ch.5 eq. 5.1]

$$p(C_k | x) = \frac{p(C_k) \cdot p(x | C_k)}{p(x)}$$

where $x = (TMV_i, T_i)$, $C_k \in \{C_1 = \text{Normal}, C_2 = \text{Abnormal}\}$

---

**Conditional independence of features** [p.64, ch.5 eq. 5.2]

$$p(x | C_k) = p(x_1 | C_k) \cdot p(x_2 | C_k)$$

where $x_1 = TMV$, $x_2 = T$ — "naive" assumption of independence.

---

**Gaussian emission density** [p.64, ch.5 eq. 5.3]

$$p(x | C_k) = \frac{1}{\sqrt{2\pi\sigma_k^2}} \exp\!\left(-\frac{(x - \mu_k)^2}{2\sigma_k^2}\right)$$

$\mu_k$ and $\sigma_k$ are estimated from training data for each regime $k$.

---

**Marginal probability** [p.64, ch.5 eq. 5.5]

$$p(x) = p(x|C_1)\,p(C_1) + p(x|C_2)\,p(C_2)$$

---

**B-Simple decision rule** [p.70, ch.5 eq. 5.6]

$$\text{choose } C_1 \text{ if } p(C_1|x) > p(C_2|x); \quad \text{choose } C_2 \text{ if } p(C_2|x) > p(C_1|x)$$

---

**B-Strict decision rule** [p.71, ch.5 eq. 5.7]

$$\text{choose } C_2 \text{ if } p(C_2|x) > p(C_1|x) \text{ AND } p(C_2|x) > \text{threshold}_2$$

- $\text{threshold}_2 = 0.8$ in empirical experiments [p.71, ch.5]
- B-Simple is a special case of B-Strict with $\text{threshold}_2 = 0.5$ [p.71, ch.5]

---

**Min-Max normalisation (comparing T and TMV across markets)** [p.45, ch.4 eq. 4.3]

$$x' = \frac{x - \min(x)}{\max(x) - \min(x)}$$

Applied so that regimes from markets with different absolute TMV/T scales can be positioned in the same indicator space.

---

## 4. Algoritmos e Pseudocódigo

**Algorithm 1 — Naive Bayes Classifier training and testing** [p.65, ch.5]

```
Training Phase
  Input:  Training data (x, C) where x = (TMV, T) pairs, C in {C1, C2}
  Output: Parameters of the model
  1. Calculate prior probability of class: p(C_k)
  2. Calculate mean mu_k and std sigma_k of features per class
  3. Estimate Gaussian distribution p(x|C_k) for each class
  4. Calculate marginal p(x) = sum_k [ p(x|C_k) * p(C_k) ]

Testing Phase
  Input:  New observation v
  Output: p(C_k | x = v)
  1. For each class k: plug v into Gaussian(mu_k, sigma_k)
  2. Calculate p(x = v | C_k)
  3. Calculate p(C_k | x = v) = p(C_k) * p(x=v|C_k) / p(x)
```

---

**DC-based Regime Detection Pipeline (Chapter 3)** [p.25–28, ch.3]

```
Input:  Price series (second-by-second), threshold theta = 0.004 (0.4%)
Step 1: Summarise data into DC trends (uptrends, downtrends) using theta
Step 2: For each completed DC trend:
          compute TMV, T
          compute R = |TMV| * theta / T
Step 3: Log-transform: LR[t] = log(R[t])
Step 4: Fit 2-state HMM with Gaussian emissions to LR series
          (depmixS4 in R; EM algorithm)
Step 5: Decode hidden state of each trend -> Regime 1 or Regime 2
          Regime 1: lower R (normal, less volatile)
          Regime 2: higher R (abnormal, more volatile)
Output: Regime label per DC trend
Parallel:
  Extract 5-minute returns from same raw data
  Compute daily realised volatility RV = sum(r_t^2)
  Fit separate 2-state HMM on RV
  Compare regime periods from both approaches
```

---

**Regime Classification in T-TMV Indicator Space (Chapter 4)** [p.44–55, ch.4]

```
For each dataset (10 markets x 10 thresholds, thresholds in 0.1%-1.0%):
  1. Summarise into DC trends using each threshold
  2. Compute TMV, T, R per trend
  3. Run 2-state HMM on R -> label each trend Regime1/Regime2
  4. Compute average TMV and average T per regime period
  5. Apply min-max normalisation (eq. 4.3) per dataset

Plot each (regime period, dataset, threshold) as point in
normalised (mean_T, mean_TMV) indicator space.

Expected outcome:
  Regime 1 points cluster in one region (higher T, lower TMV)
  Regime 2 points cluster in another region (lower T, higher TMV)
  -> higher TMV/T ratio = higher volatility
  -> separation holds across asset types, times, and thresholds
```

---

**JC1 — Regime-switching DC contrarian/trend-follower** [p.82–83, ch.6]

```
Under Normal Regime (mean reversion assumed):
  Rule 1:  In uptrend,   when TMV >=  2: open SHORT position
  Rule 2:  In downtrend, when TMV <= -2: open LONG position
  Rule 3:  When next DC Confirmation (DCC) point confirmed: CLOSE
  Rule 4:  When regime change to Abnormal detected: CLOSE

Under Abnormal Regime (momentum/margin cascades assumed):
  Rule 1a: In uptrend,   when TMV >=  2: open LONG (trend-follow)
  Rule 2a: In downtrend, when TMV <= -2: open SHORT (trend-follow)
  Rule 3a: When next DCC point confirmed: CLOSE
  Rule 4a: When regime change back to Normal detected: CLOSE
```

---

**JC2 — Regime-gated DC contrarian (preferred for drawdown reduction)** [p.83–84, ch.6]

```
Under Normal Regime:
  Rule 1: In uptrend,   when TMV >=  2: open SHORT
  Rule 2: In downtrend, when TMV <= -2: open LONG
  Rule 3: When regime change to Abnormal detected: CLOSE position
Under Abnormal Regime: NO TRADES (sit out)
Resume trading when Normal regime is restored.
```

---

**CT1 — Baseline contrarian (no regime information)** [p.84, ch.6]

```
Rule 1: In uptrend,   when TMV >=  2: open SHORT
Rule 2: In downtrend, when TMV <= -2: open LONG
Rule 3: When next DCC point confirmed: CLOSE
(No regime awareness — used as benchmark for JC1/JC2)
```

---

## 5. Regras de Trading Explícitas

- **REGRA [p.82, ch.6]**: Under normal regime, enter contrarian when |TMV| reaches 2: short in uptrend (TMV ≥ 2), long in downtrend (TMV ≤ -2). Rationale: mean reversion is observed in normal market regimes.

- **REGRA [p.83, ch.6]**: Under abnormal regime, JC1 switches to trend-following on the same |TMV| ≥ 2 trigger. Rationale: in abnormal regimes, margin calls cascade and drive the prevailing trend further.

- **REGRA [p.82, ch.6]**: Close position at the next DC Confirmation (DCC) point under both normal and abnormal regimes.

- **REGRA [p.82–83, ch.6]**: Close ALL open positions immediately when a regime change is detected by the Bayes tracker. This is the primary stop-loss mechanism and the source of drawdown reduction.

- **REGRA [p.83, ch.6]** (JC2 — more conservative): Hold NO positions during abnormal regime; wait for return to normal regime before re-entering.

- **REGRA [p.71, ch.5]**: Use B-Strict rule: only conclude Regime 2 if $p(C_2|x) > p(C_1|x)$ AND $p(C_2|x) > 0.8$. Reduces false alarms from 52 to 10 across DJIA/FTSE/S&P 500 test period [p.76, ch.5].

- **REGRA [p.58, ch.4]**: If the current market is moving away from the normal regime cluster in the T-TMV indicator space, consider closing positions or switching strategy.

- **NUNCA [p.77, ch.5]**: Treat regime tracking output as a forecast of future prices — the method is purely data-led and tells only the current regime state. "No forecasting is attempted."

---

## 6. Pitfalls e Anti-patterns

- [p.94, ch.7] Using only time-series analysis for regime detection — this misses intra-day regime changes that DC captures (e.g., the 14 July 2016 EUR-GBP regime change linked to Theresa May becoming PM was not detected under time series) [p.29, ch.3].

- [p.1, ch.1; p.94, ch.7] Assuming fixed-interval sampling captures all significant market shifts — in 24h FX markets, important events occur within intervals and are diluted in daily closes.

- [p.88–89, ch.6] Expecting JC1/JC2 to beat the control CT1 in total wealth — they do NOT. JC1 and JC2 are consistently inferior to CT1 in profitability across all 3 indices × 3 trading thresholds (with one exception: FTSE 100 at threshold 0.006). The advantage is exclusively in **maximum drawdown reduction**.

- [p.92, ch.6] Treating JC1/JC2 as production-ready strategies — the authors explicitly call them "naïve/primitive" and "proof of concept." The regime tracking information is proposed as an add-on to more sophisticated algorithms like the Alpha Engine.

- [p.73, ch.5] Expecting B-Simple to generate persistent regime signals — the rule generates repeated intermittent alarms because it uses only the current (TMV, T) reading without Markov memory. Traders should react on the first alarm, not wait for persistence.

- [p.55–57, ch.4] Assuming results are threshold-independent everywhere — in some markets (FX, Chinese stocks) regime positions in indicator space shift with θ; in others (stock indices, oil) they do not. The **separability** between Regime 1 and Regime 2 holds across thresholds, but absolute positions may vary.

- [p.76, ch.5] Expecting zero-lag detection — typical delays in tracking experiments range from +9 days behind to -6 days ahead; the average is early or on-time but perfect synchrony is not guaranteed.

- [p.25, ch.3] Using a 2-state HMM for long time horizons — only justified for short periods like the 2-month Brexit window. For multi-year analysis, more states may be needed and model selection criteria (BIC/AIC) should be applied.

- [p.203, ch.4 — implicit in methodology] Min-max normalisation using the full dataset's range leaks future information in production: max/min of TMV and T are only known at end of sample. Authors do not address this look-ahead issue explicitly.

---

## 7. Parâmetros Sensíveis

- **Threshold θ = 0.4%** (Chapter 3, FX second-by-second) [p.25, ch.3]: set "arbitrarily." Justified by DC scaling law from Glattfelder et al. — "the same stylised facts can be observed under different thresholds." Curve-fit risk: low, as scaling invariance is empirically established.

- **Threshold grid 0.1%–1.0%** (Chapter 4, classification) [p.51, ch.4]: ten evenly spaced values used to demonstrate that regime separability holds across thresholds. Good anti-overfit practice — the result (separability) does not depend on any single θ.

- **Threshold θ = 0.3%** (Chapter 5, tracking) [p.65, ch.5]: used for DC summarisation in training data. Not optimised.

- **Regime tracking threshold θ = 0.003** (Chapter 6) [p.85, ch.6]: fixed, consistent with Chapter 5 order of magnitude.

- **Trading thresholds α ∈ {0.03, 0.006, 0.009}** [p.85, ch.6]: three values tested for robustness. All show same qualitative result (JC1/JC2 reduce drawdown vs. CT1), so findings are not threshold-specific.

- **HMM states = 2** [p.25, ch.3; p.47, ch.4]: justified by the binary normal/abnormal taxonomy and short data periods. Not optimised via model selection criteria — acknowledged as a limitation [p.100, ch.7].

- **B-Strict threshold₂ = 0.8** [p.71, ch.5]: defined by the researcher as a "cautious" prior for concluding Regime 2. Not optimised empirically; presented as a tuning knob. Lower values → more alarms; higher → fewer.

- **|TMV| = 2 as entry trigger** [p.81–82, ch.6]: economically justified by Glattfelder et al.'s finding that FX markets change direction on average at TMV = 2 (scaling law, not optimised). Same value used by the Alpha Engine. Low curve-fit risk.

- **Training split 2007–2009 / test 2010–2012** [p.65, ch.5]: fixed single split; no walk-forward or cross-validation applied. Authors acknowledge this is proof-of-concept and that more rigorous validation is future work.

---

## 8. Citações Literais Importantes

> "If no one buys and sells in the market, or the price never changes, whether one takes a daily, hourly or minute approach, time series as a concept does not matter. Time series is only useful if it records price changes. And if that is the case, then why don't we simply record only significant price changes in the market? That is the basic concept behind Directional Change." — [p.20, Preface]

> "Being able to see with two eyes (time series and directional change) is better than seeing with one (time series alone)." — [p.1, ch.1]

> "Regime change presents significant challenges to investors: the performance of their trading strategies generally depends on the market continuing to behave as before. This assumption is especially important for trading algorithms that rely on machine learning. When the collective trading behaviour changes in the market, trading strategies may need to change." — [p.23, ch.3]

> "Both the DC and time series approaches picked up regime changes on the day before the Brexit referendum result was announced on 24 June 2016. Both indicators suggest that traders reacted ahead of the results." — [p.38, ch.3]

> "8 out of 12 alarms are raised ahead of or spot on the actual regime changes. Such results are positive. That means our tracking mechanism is likely to raise the alarm of regime changes in advance." — [p.76, ch.5]

> "Closing one's position when the market changes its regime is an effective stop-loss strategy." — [p.90, ch.6]

> "JC1 and JC2 are primitive trading algorithms. They are useful for proving our point, which is the usefulness of regime tracking information... the low returns of JC1 and JC2 compared to the control algorithm CT1 should not deter researchers from using regime tracking information to improve profitability of more advanced algorithms, such as the Alpha Machine." — [p.92, ch.6]

> "The abnormal regime (more volatile market periods) was more likely to have been triggered by a significant external event, such as the oil crash of 2014–2016, or the global financial crisis of 2007–2008, but then the market always returned to and stayed in normal regimes (less volatile market periods) afterwards." — [p.97, ch.7]

> "No forecasting is attempted. It is up to users to interpret what are the results." — [p.97, ch.7]

---

## 9. Conexões com Outros Livros Desta Base

- **Hamilton's regime-switching model** [p.6–7, ch.2] is the direct precursor to the HMM framework used here. `time_series_hamilton.md` covers the statistical foundations; this book extends it by replacing the time-series observable (returns/volatility) with DC indicator R.

- **Anti-overfit / threshold robustness** [p.56–57, ch.4]: the demonstration that regime separability holds across 10 thresholds (0.1%–1.0%) resonates with the parsimony principle in `systematic_trading.md` — a valid result should be insensitive to parameter choices within an economically reasonable range.

- **Regime-gating as position management** [p.82–83, ch.6] (JC2 closes all positions on regime change): conceptually related to the meta-labeling idea in `ml_for_algo_trading.md` (López de Prado) — ML provides a gate on whether to act, not the entry signal itself. Here the Bayes tracker provides the gate.

- **Walk-forward vs. fixed split**: this book uses a single fixed 2007–2009 train / 2010–2012 test split [p.65, ch.5], lacking walk-forward or CPCV. More rigorous anti-overfit validation is available in `ml_for_algo_trading.md`.

- **TMV = 2 entry trigger** [p.82, ch.6] is derived from Glattfelder et al.'s scaling law — an empirically invariant constant, not an optimised parameter. This pattern (economically justified constants vs. optimised parameters) also appears in `trading_systems_methods.md`.

- N/A for books not yet processed in this pipeline that would require confirmation before citing.
