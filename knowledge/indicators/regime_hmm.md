# Hidden Markov Models for Regime

HMM como classificador de regime (bull, bear, high-vol, low-vol).

## Sources

- [`books/regime_change.md`](../books/regime_change.md)
- [`books/data_driven_science.md`](../books/data_driven_science.md)
- [`books/ml_for_algo_trading.md`](../books/ml_for_algo_trading.md)

## From `books/regime_change.md`

### Regras de Trading Explícitas

- **REGRA [p.82, ch.6]**: Under normal regime, enter contrarian when |TMV| reaches 2: short in uptrend (TMV ≥ 2), long in downtrend (TMV ≤ -2). Rationale: mean reversion is observed in normal market regimes.

- **REGRA [p.83, ch.6]**: Under abnormal regime, JC1 switches to trend-following on the same |TMV| ≥ 2 trigger. Rationale: in abnormal regimes, margin calls cascade and drive the prevailing trend further.

- **REGRA [p.82, ch.6]**: Close position at the next DC Confirmation (DCC) point under both normal and abnormal regimes.

- **REGRA [p.82–83, ch.6]**: Close ALL open positions immediately when a regime change is detected by the Bayes tracker. This is the primary stop-loss mechanism and the source of drawdown reduction.

- **REGRA [p.83, ch.6]** (JC2 — more conservative): Hold NO positions during abnormal regime; wait for return to normal regime before re-entering.

- **REGRA [p.71, ch.5]**: Use B-Strict rule: only conclude Regime 2 if $p(C_2|x) > p(C_1|x)$ AND $p(C_2|x) > 0.8$. Reduces false alarms from 52 to 10 across DJIA/FTSE/S&P 500 test period [p.76, ch.5].

- **REGRA [p.58, ch.4]**: If the current market is moving away from the normal regime cluster in the T-TMV indicator space, consider closing positions or switching strategy.

- **NUNCA [p.77, ch.5]**: Treat regime tracking output as a forecast of future prices — the method is purely data-led and tells only the current regime state. "No forecasting is attempted."

---

### Fórmulas / Equações

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

### Algoritmos e Pseudocódigo

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

### Pitfalls e Anti-patterns

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

---

## From `books/data_driven_science.md`

### Regras de Trading Explícitas

N/A — This chapter is a pedagogical treatment of Reinforcement Learning for general dynamical systems, control, robotics, and board/video games. It does NOT discuss trading, asset pricing, portfolio optimization, execution, or any financial-market application. No trading rule ("if X then Y") is stated anywhere in the extracted pages. Applying RL to trading would require additional domain knowledge (reward function design, state/action spaces for markets, transaction costs, non-stationarity) that is not covered here. For explicit trading rules see `systematic_trading.md` or `evidence_based_ta.md`.

### Fórmulas / Equações

**Policy as conditional probability** [p.3, eq.11.1]

$$\pi(s, a) = \Pr(a = a \mid s = s)$$

**Markov transition and reward** [p.4, eq.11.3-11.4]

$$P(s', s, a) = \Pr(s_{k+1} = s' \mid s_k = s, a_k = a)$$
$$R(s', s, a) = \Pr(r_{k+1} \mid s_{k+1} = s', s_k = s, a_k = a)$$

**Markov process as linear map** [p.5, eq.11.6]

$$s' = T s$$

- $T$ = stochastic transition matrix; each column sums to 1.

**Value function (discounted future reward)** [p.6, eq.11.8-11.9]

$$V^{\pi}(s) = \mathbb{E}\left( \sum_{k} \gamma^k r_k \mid s_0 = s \right)$$

$$V(s) = \max_{\pi} \mathbb{E}\left( \sum_{k=0}^{\infty} \gamma^k r_k \mid s_0 = s \right)$$

- $\gamma$ = discount factor ∈ (0,1); "future rewards are discounted, reflecting the economic principle that current rewards are more valuable than future rewards" [p.6].

**Bellman equation** [p.6, eq.11.11]

$$V(s) = \max_{\pi} \mathbb{E}\bigl( r_0 + \gamma V(s') \bigr)$$

$$\pi = \arg\max_{\pi} \mathbb{E}\bigl( r_0 + \gamma V(s') \bigr)$$

**Policy iteration update** [p.13, eq.11.13b-11.14]

$$V^{\pi}(s) = \sum_{s'} P(s' \mid s, \pi(s))\bigl( R(s', s, \pi(s)) + \gamma V^{\pi}(s') \bigr)$$

$$\pi(s) = \arg\max_{a \in A} \mathbb{E}\bigl( R(s', s, a) + \gamma V^{\pi}(s') \bigr)$$

**Value iteration update** [p.13, eq.11.15]

$$V(s) = \max_{a} \sum_{s'} P(s' \mid s, a)\bigl( R(s', s, a) + \gamma V(s') \bigr)$$

**Quality function** [p.14, eq.11.17]

$$Q(s, a) = \sum_{s'} P(s' \mid s, a)\bigl( R(s', s, a) + \gamma V(s') \bigr)$$

$$\pi(s, a) = \arg\max_{a} Q(s, a), \qquad V(s) = \max_{a} Q(s, a)$$

**Monte Carlo cumulative reward and V update** [p.15, eq.11.19-11.20]

$$R_{\Sigma} = \sum_{k=1}^{n} \gamma^k r_k$$

$$V^{\text{new}}(s_k) = V^{\text{old}}(s_k) + \frac{1}{n}\bigl( R_{\Sigma} - V^{\text{old}}(s_k) \bigr)$$

**Monte Carlo Q update with learning rate α** [p.16, eq.11.22]

$$Q^{\text{new}}(s_k, a_k) = Q^{\text{old}}(s_k, a_k) + \alpha\bigl( R_{\Sigma} - Q^{\text{old}}(s_k, a_k) \bigr)$$

- $\alpha \in [0, 1]$. "Larger learning rates α > 1/n will favor more recent experience" [p.16].

**TD(0) update** [p.17, eq.11.24]

$$V^{\text{new}}(s_k) = V^{\text{old}}(s_k) + \alpha\bigl( \underbrace{r_k + \gamma V^{\text{old}}(s_{k+1})}_{\text{TD target}} - V^{\text{old}}(s_k) \bigr)$$

**TD(n) n-step target** [p.17, eq.11.26b]

$$R^{(n)}_{\Sigma} = \sum_{j=0}^{n} \gamma^j r_{k+j} + \gamma^{n+1} V(s_{k+n+1})$$

**TD-λ target** [p.18, eq.11.27, Sutton 1988]

$$R^{\lambda}_{\Sigma} = (1 - \lambda) \sum_{n=1}^{\infty} \lambda^{n-1} R^{(n)}_{\Sigma}$$

**SARSA(0) update (on-policy TD for Q)** [p.19, eq.11.29]

$$Q^{\text{new}}(s_k, a_k) = Q^{\text{old}}(s_k, a_k) + \alpha\bigl( r_k + \gamma Q^{\text{old}}(s_{k+1}, a_{k+1}) - Q^{\text{old}}(s_k, a_k) \bigr)$$

**Q-learning update (off-policy TD for Q)** [p.19, eq.11.32]

$$Q^{\text{new}}(s_k, a_k) = Q^{\text{old}}(s_k, a_k) + \alpha\bigl( r_k + \gamma \max_{a} Q(s_{k+1}, a) - Q^{\text{old}}(s_k, a_k) \bigr)$$

**Policy gradient (log-likelihood trick)** [p.21, eq.11.34d]

$$\nabla_{\theta} R_{\Sigma, \theta} = \mathbb{E}\bigl( Q(s, a)\, \nabla_{\theta} \log \pi_{\theta}(s, a) \bigr)$$

**Policy parameter update** [p.21, eq.11.35]

$$\theta_{\text{new}} = \theta_{\text{old}} + \alpha \nabla_{\theta} R_{\Sigma, \theta}$$

**Deep Q Network loss** [p.24, eq.11.38]

$$L = \mathbb{E}\left[ \bigl( r_k + \gamma \max_{a} Q(s_{k+1}, a_{k+1}, \theta) - Q(s_k, a_k, \theta) \bigr)^2 \right]$$

**Dueling DQN decomposition** [p.24, eq.11.39]

$$Q(s, a, \theta) = V(s, \theta_1) + A(s, a, \theta_2)$$

**Advantage Actor-Critic (A2C) update** [p.25, eq.11.41]

$$\theta_{k+1} = \theta_k + \alpha \nabla_{\theta}\bigl( \log \pi(s_k, a_k, \theta)\, Q(s_k, a_k, \theta_2) \bigr)$$

**Nonlinear dynamics / cost functional (optimal control)** [p.32, eq.11.42-11.43]

$$\frac{d}{dt} x = f(x(t), u(t), t)$$

$$J(x(t), u(t), t_0, t_f) = Q(x(t_f), t_f) + \int_{t_0}^{t_f} L(x(\tau), u(\tau))\, d\tau$$

**Hamilton-Jacobi-Bellman (HJB) equation** [p.33, eq.11.45]

$$-\frac{\partial V}{\partial t} = \min_{u(t)}\left( \left(\frac{\partial V}{\partial x}\right)^T f(x(t), u(t)) + L(x(t), u(t)) \right)$$

- V(x,t,t_f) is the value function / "cost-to-go" assuming optimal control [p.33].
- LQR Riccati equation is a special case of the HJB equation [p.34].

**Discrete-time Bellman** [p.35, eq.11.55]

$$V(x) = \min_{u}\bigl( L(x, u) + V(F(x, u)) \bigr)$$

$$\pi(x) = \arg\min_{u}\bigl( L(x, u) + V(F(x, u)) \bigr)$$

### Algoritmos e Pseudocódigo

**Policy Iteration** [p.12-13, §policy iteration]

```
Input: MDP (S, A, P, R), discount γ, tolerance tol
[1] Initialize policy π arbitrarily.
[2] Repeat:
   a. Policy evaluation: iterate V^π(s) = Σ_s' P(s'|s, π(s)) [R(s',s,π(s)) + γ V^π(s')]
      for all s ∈ S until V converges.
   b. Policy improvement: for all s ∈ S,
         π(s) ← argmax_{a ∈ A} E(R(s',s,a) + γ V^π(s'))
   c. If π and V both changed less than tol, break.
[3] Return (π, V).
# Note: "expensive and prone to finding local minima" [p.13].
```

**Value Iteration** [p.13, eq.11.15-11.16]

```
Input: MDP, γ, tol
[1] Initialize V(s) ← 0 (or random) for all s ∈ S.
[2] Repeat:
   For all s ∈ S:
      V(s) ← max_a Σ_s' P(s'|s,a) [R(s',s,a) + γ V(s')]
[3] Until max_s |V_new(s) - V_old(s)| < tol.
[4] Extract policy: π(s,a) = argmax_a Σ_s' P(s'|s,a) [R(s',s,a) + γ V(s')]
# "Value iteration typically requires fewer steps per iteration; policy iteration
#  often converges in fewer iterations" [p.14].
```

**Monte Carlo Q-learning (episodic)** [p.15-16, eq.11.19-11.22]

```
Input: episode horizon n, γ, learning rate α
[1] Initialize Q(s,a) arbitrarily for all (s,a).
[2] For each episode:
   a. Run policy π (ε-greedy over current Q) for n steps;
      record trajectory (s_1,a_1,r_1,...,s_n,a_n,r_n).
   b. Compute R_Σ = Σ_{k=1}^n γ^k r_k
   c. For each visited (s_k, a_k):
         Q(s_k, a_k) ← Q(s_k, a_k) + α [R_Σ - Q(s_k, a_k)]
[3] Return Q.
```

**Q-Learning (off-policy TD)** [p.19, eq.11.32; §11.3]

```
Input: learning rate α, discount γ, exploration ε
[1] Initialize Q(s,a) for all (s,a).
[2] For each episode:
   Observe initial state s.
   While not terminal:
      a. With prob. 1−ε: a ← argmax_a Q(s,a); else a ← random.   # ε-greedy [p.20]
      b. Take action a, observe reward r and next state s'.
      c. Q(s,a) ← Q(s,a) + α [ r + γ max_a' Q(s', a') − Q(s,a) ]
      d. s ← s'
[3] Typically: anneal ε toward 0 over training [p.21].
```

**SARSA (on-policy TD)** [p.18-19, eq.11.29]

```
Initialize Q(s,a); choose s; a ← ε-greedy(Q, s).
While not terminal:
   Take action a, observe r, s'.
   a' ← ε-greedy(Q, s').
   Q(s,a) ← Q(s,a) + α [ r + γ Q(s', a') − Q(s,a) ]     # uses ACTUAL next action
   s ← s';  a ← a'.
```

**Deep Q Network (DQN) with experience replay** [p.23-24, eq.11.38, ref. 519]

```
Input: replay buffer D, batch size B, target-update period τ
[1] Initialize Q-net Q_θ, target net Q_{θ^-} with θ^- ← θ.
[2] For each episode / step:
   a. Act ε-greedily from Q_θ; observe (s, a, r, s'); store in D.
   b. Sample batch of B transitions from D (optionally prioritized by TD error [p.24]).
   c. For each sample: y = r + γ max_a' Q_{θ^-}(s', a')
   d. Loss L = (1/B) Σ [ y − Q_θ(s,a) ]^2    # eq. 11.38
   e. SGD step on θ.
   f. Every τ steps: θ^- ← θ.    # double-DQN stability [p.24]
```

**REINFORCE-style Policy Gradient** [p.21-22, eq.11.34-11.35]

```
Input: parameterized policy π_θ, learning rate α
[1] Sample trajectory τ = (s_1,a_1,r_1,...,s_T,a_T,r_T) under π_θ.
[2] For each step k: compute return G_k = Σ_{j≥k} γ^{j-k} r_j   (or advantage Q(s_k,a_k))
[3] Gradient estimate: ĝ = Σ_k G_k · ∇_θ log π_θ(s_k,a_k)
[4] θ ← θ + α · ĝ
# Variants: natural policy gradients [p.22, ref. 377]; REINFORCE [p.22, ref. 770]
```

**Advantage Actor-Critic (A2C)** [p.25, eq.11.41]

```
Initialize actor π_θ (deep policy net) and critic Q_{θ₂} (DDQN).
Loop:
   a. Actor draws action a ~ π_θ(s).
   b. Observe (r, s').
   c. Critic TD update on Q_{θ₂}.
   d. Actor update: θ ← θ + α ∇_θ[ log π_θ(s,a) · Q_{θ₂}(s,a) ]
```

### Pitfalls e Anti-patterns

- **Curse of dimensionality in dynamic programming** [p.11-12]: "For even moderately large problems, [Bellman backup] suffers from the curse of dimensionality, and approximate solution methods must be employed" [p.12]. Chess has combinatorially large state spaces (Shannon number ≈ 10^120 [p.25]) that make tabular Q infeasible.
- **Policy iteration is expensive and prone to local minima** [p.13]: "This procedure is both expensive and prone to finding local minima. It also resembles the alternating descent method."
- **Monte Carlo learning is sample-inefficient for sparse rewards** [p.15]: "For this reason, Monte Carlo learning is typically quite sample inefficient, especially for problems with sparse rewards."
- **Off-policy Monte Carlo methods** [p.16]: "In general, they are quite inefficient or unfeasible."
- **TD learning introduces bias** [p.18, §bias-variance tradeoff]: "The sampled TD target is a biased estimate, because it uses sub-optimal actions and the current imperfect estimate of the value function."
- **Q-learning vs. SARSA safety tradeoff** [p.19]: "In safety-critical applications, such as self-driving cars or other applications where there can be catastrophic failure, SARSA will typically learn less optimal solutions, but with a better safety margin, since it is maximizing on-policy rewards." Q-learning "will learn a more optimal solution faster than SARSA, but with more variance in the solution."
- **Reward shaping ceiling** [p.26]: Reward shaping "is not a viable strategy for a generalized artificial intelligence agent capable of learning multiple games or tasks. In addition, reward shaping generally limits the upper end of the agent's performance to that of the human expert."
- **Curiosity reward fails in stochastic/chaotic environments** [p.27]: "A naive novelty reward would constantly provide positive incentive to explore these regions, since the forward model will not improve." Remedy: predicate novelty on predictability via latent autoencoder features [p.27, ref. 562].
- **RL is expensive and potentially unsafe** [p.6-7]: "Reinforcement learning may be very expensive to train, and it might not be the right strategy for problems where testing a policy is expensive or potentially unsafe. Similarly, in many cases, there are simpler control strategies than RL, such as LQR or MPC; when these approaches are effective, they are often preferable" [p.7].
- **RL assumptions may not hold** [p.7]: "Many real world applications do not satisfy [MDP] assumptions. For example, the dynamics may depend on the state history or on hidden or latent variables. Similarly, the evolution dynamics may be entirely deterministic, yet chaotic."
- **Credit assignment problem** [p.7]: Six decades old, still unsolved in general. Sparse/delayed rewards make it computationally intractable to know which action sequence caused the eventual reward.
- **HJB curse of dimensionality** [p.34-35]: "A nonlinear control problem with a three-dimensional state vector x ∈ R^3 will result in a three-dimensional PDE. Thus, optimal nonlinear control based on the HJB equation typically suffers from the curse of dimensionality."
- **Double-DQN target-network instability** [p.24]: "It may be necessary to fix the target network for multiple training iterations of the prediction network before updating to improve stability and convergence" [ref. 264].

---

## From `books/ml_for_algo_trading.md`

### Regras de Trading Explícitas

- **REGRA [ch.1 p.13; ch.8 p.223-224]**: Use ONLY point-in-time (PIT) data; synchronize reported financials with actual publication dates (e.g., EPS quarterly vs. prices daily). Failure produces positive backtests that collapse in live trading.
- **REGRA [ch.2 p.55]**: When joining fundamentals with adjusted prices, back-adjust pre-split EPS by the split ratio (e.g., Apple pre-2014-06-04 EPS ÷ 7); use 4-quarter rolling sums for TTM metrics.
- **REGRA [ch.2 p.39]**: Prefer **dollar bars** (or volume bars) over time bars in backtests; tick-return normality tests fail at vanishingly small p-values, and dollar bars remain comparable across splits and price-regime changes.
- **REGRA [ch.3 p.66-67]**: Score every alternative dataset on (1) signal content / alpha, (2) data quality (gaps, biases), (3) latency between event and delivery, (4) legal/reputational risk including GDPR. Skip datasets that fail any dimension.
- **REGRA [ch.3 p.66]**: Prefer alt-data whose signals show low (< 5%) correlation with traditional risk premia (value, momentum, quality); they add diversification value even when standalone Sharpe is weak.
- **REGRA [ch.8 p.224]**: Include delisted/bankrupt/acquired tickers in backtest universe. Excluding them is survivorship bias and inflates results.
- **REGRA [ch.5 p.133]**: Use fractional Kelly (typically Half-Kelly) for position sizing. Full Kelly is optimal only with perfect parameter knowledge; real estimates have noise.
- **REGRA [ch.4 p.86]**: For momentum, use 12-month return EXCLUDING the most recent month (skip-a-month) to avoid short-term reversal contamination.
- **REGRA [ch.5 p.124]**: Target IC of 0.05–0.15 combined with high breadth. A single high-IC signal with low breadth underperforms many weak uncorrelated signals.
- **REGRA [ch.6 p.167-169]**: Use `TimeSeriesSplit` (walk-forward), not random K-fold, for time-series data. For overlapping labels, add purging + embargoing.
- **REGRA [ch.8 p.227]**: Report the number of trials run during strategy search; adjust Sharpe via the deflated SR formula before concluding.
- **REGRA [ch.8 p.227]**: 2 years of daily data supports conclusions about at most ~7 strategy variants; 5 years supports ~45. Running more trials without more data equals overfitting.
- **REGRA [ch.9 p.274]**: For volatility models, jointly estimate mean + GARCH structure rather than sequentially — sequential estimation understates uncertainty.
- **REGRA [ch.10 p.318-319]**: Compare strategies via posterior distribution of the **difference** in Sharpe ratios (Bayesian SR), not point-estimate Sharpe differences; it gives a probability that one strategy is truly superior.
- **REGRA [ch.11 p.327-334]**: For random-forest trading models, control `max_depth`, `min_samples_split`, `min_samples_leaf`. Default trees overfit financial data.
- **REGRA [ch.12 p.373]**: When using early stopping with gradient boosting or deep networks, keep a separate hold-out test set; never use the test set as the stopping-criterion validation set or you leak information.
- **REGRA [ch.12 p.373]**: Even with a proper validation set, running a large number of early-stopped trials overfits to the validation set itself — keep trial counts modest.
- **REGRA [ch.13 p.438]**: HRP typically underperforms MV in Sharpe (0.83 vs 1.16 in the book's ML benchmark) but is robust to correlation-matrix estimation error; prefer HRP when return forecasts are unreliable.
- **REGRA [ch.17 p.514-515]**: Neural networks require combined regularization (L1/L2 + dropout + early stopping) — deep models overfit low-signal financial data easily.
- **REGRA [ch.15 p.476]**: When interpreting LDA topics with pyLDAvis, set relevance λ ≈ 0.6 (user-study optimum); stop increasing topic count when coherence plateaus (typically 25–30 for financial news).
- **REGRA [ch.16 p.502]**: For word2vec on financial corpora, use skip-gram + negative sampling, `min_count ≥ 50`, window ≥ 5, and embedding size 300–600; CBOW and hierarchical softmax underperform.
- **REGRA [ch.23 p.719]**: Before going live, always run paper-trading in a staged manner. Never go straight from backtest to capital deployment.
- **NUNCA [ch.8 p.225-226]**: Backtest trades executing at the close-price of the same bar that generated the signal. Use next-bar open (or intraday with latency).
- **NUNCA [ch.23 p.716]**: Design strategies by "letting the data speak" (pure data mining). Prioritize economically-motivated hypotheses; test a limited set.

### Fórmulas / Equações

**Sharpe Ratio** [ch.5 p.123]

$$\text{SR} \equiv \frac{\mu(R^e)}{\sigma(R^e)}, \quad R^e = R - R_f$$

Frequency adjustment: monthly→annual multiply by $\sqrt{12}$; daily→monthly by $\sqrt{21}$ [ch.5 p.123].

**Information Ratio and Fundamental Law** [ch.5 p.124]

$$\text{IR} = \frac{\text{Alpha}}{\text{Tracking Error}} \approx \text{IC} \cdot \sqrt{\text{breadth}}$$

**Kelly Criterion (binary bets)** [ch.5 p.133]

$$f^* = \frac{bp + p - 1}{b} = \frac{bp - q}{b}$$

Where $b$ = payout odds, $p$ = probability of win, $q = 1-p$. Many investors use **Half-Kelly** to reduce volatility [ch.5 p.133].

**Multi-asset Kelly (Chan 2008)** [ch.5 p.133]

$$\mathbf{f}^* = \Sigma^{-1} \boldsymbol{\mu}$$

Equivalent to the (potentially levered) maximum-Sharpe portfolio from mean-variance optimization [ch.5 p.133].

**CAPM** [ch.7 p.188]

$$E[r_i] = \alpha_i + r_f + \beta_i(E[r_m] - r_f)$$

**Fama–French 5-factor** uses Mkt-RF, SMB (size), HML (value), RMW (profitability), CMA (investment) [ch.7 p.190-191].

**RSI** [ch.4 p.86]

$$\text{RSI} = 100 - \frac{100}{1 + \overline{\Delta p_{up}} / \overline{\Delta p_{down}}}$$

Default lookback 14 periods; >70 overbought, <30 oversold [ch.4 p.86].

**Ridge / Lasso regularization** [ch.7 p.195]

Ridge: $\min \|y - X\beta\|_2^2 + \lambda \|\beta\|_2^2$ and Lasso: $\min \|y - X\beta\|_2^2 + \lambda \|\beta\|_1$. λ chosen via cross-validation; Lasso can drive coefficients to exactly zero (sparse selection) [ch.7 p.195].

**ARIMA(p, d, q)** combines AR(p), d differencing steps, and MA(q). Requires stationarity; SARIMAX extends with seasonal + exogenous terms [ch.9 p.266-271].

**ARCH(p)** [ch.9 p.272]

$$\text{var}(x_t) = \sigma_t^2 = \omega + \sum_{i=1}^p \alpha_i \epsilon_{t-i}^2$$

**GARCH(p, q)** extends ARCH with ARMA structure on variance [ch.9 p.273]. Workflow: fit ARMA to mean; test residuals for ARCH effects via ACF/PACF of squared residuals; jointly estimate mean+volatility; diagnose [ch.9 p.274].

**Bayes' theorem (posterior)** [ch.10 p.297]

$$P(\theta | X) = \frac{P(X | \theta) \, P(\theta)}{P(X)}$$

Posterior = prior × likelihood / evidence; the evidence is often intractable, motivating MAP, MCMC (e.g., NUTS), or variational inference (ADVI) approximations [ch.10 p.298-305].

**Bayesian rolling regression (pairs hedge ratio)** [ch.10 p.320-321]

$$\alpha_t \sim \mathcal{N}(\alpha_{t-1}, \sigma_\alpha^2), \quad \beta_t \sim \mathcal{N}(\beta_{t-1}, \sigma_\beta^2)$$

Implemented in PyMC3 as `pm.GaussianRandomWalk`; trained via NUTS with target_accept=0.9 for difficult posteriors [ch.10 p.321].

**LDAvis relevance** [ch.15 p.476]

$$r(w, t | \lambda) = \lambda \log p(w|t) + (1-\lambda) \log \frac{p(w|t)}{p(w)}$$

User studies recommend λ = 0.6 for most plausible topic interpretations [ch.15 p.476].

**Perplexity (LDA)** [ch.15 p.474]

$$2^{H(p)} = 2^{-\sum_w p(w) \log_2 p(w)}$$

Lower is better; used together with UMass/UCI coherence [ch.15 p.474].

**Bellman Equation (RL)** [ch.22 p.686]

$$v_\pi(s) = \mathbb{E}_\pi[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t=s]$$

Figure 22.2 illustrates the recursive relationship. For continuing (non-episodic) tasks the discount factor γ must be strictly < 1 to avoid infinite returns [ch.22 p.685-686].

### Algoritmos e Pseudocódigo

**ML4T Workflow** [preface p.xiii; ch.1 p.12-15; ch.6 p.153]

Step A — Frame problem: define target metric (return forecast, direction, class) [ch.6 p.155].
Step B — Source data: market + fundamental + alternative, PIT-correct [ch.1 p.13].
Step C — Engineer features (alpha factors): momentum, value, quality, volatility [ch.4 p.82-93].
Step D — Train/tune ML model with cross-validation respecting time-series order [ch.6 p.167-169].
Step E — Translate predictions → portfolio weights (sizing, risk constraints) [ch.5 p.126-135].
Step F — Backtest with Zipline/backtrader; track risk metrics mark-to-market [ch.8 p.223-230].
Step G — Evaluate via Sharpe / IR / deflated SR / pyfolio tearsheet [ch.5 p.123; ch.8 p.227].
Step H — Paper-trade, then live, with continuous monitoring for factor decay [ch.23 p.719].

**TimeSeriesSplit walk-forward CV** [ch.6 p.167-168]

```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(X):
    # train_set strictly precedes test_set
    # optional max_train_size for rolling (vs expanding) window
    ...
```

**Purged / Embargoed / Combinatorial CV** [ch.6 p.169]

```
Input: dataset D, n_splits, n_test_splits, purge_window, embargo_pct
for each combination C of n_test_splits groups from N:
    train_set = D \ C
    purged = remove_overlapping(train_set, C, purge_window)
    embargoed = apply_embargo(purged, embargo_pct)
    model = train(embargoed)
    scores.append(evaluate(model, C))
return distribution(scores)
```

**Nasdaq ITCH order-book reconstruction** [ch.2 p.28-35]

```
Parse ITCH v5.0 binary feed using message-type specs
For each message:
    if message adds / replaces / cancels an order:
        update in-memory order book (by price level)
    elif message is an execution:
        record trade
Persist state iteratively to HDF5 (9 GB typical single-day)
```

Output: full limit-order-book snapshot per ticker, aggregate trades → tick/time/volume/**dollar bars** [ch.2 p.35-40].

**AlgoSeek minute-bar pipeline** [ch.2 p.41-43]

Load 1-min CSV zips → convert to daily `.parquet` → combine → HDF5 (53.8M records / 3.2 GB covering 5y × 100 tickers in the sample) [ch.2 p.42-43]. Bars include NBBO-based OHLC, VWAP, bid/ask, dark-pool volume, up/down-tick counts.

**EDGAR XBRL PIT-correct fundamentals** [ch.2 p.52-56]

Download SEC Financial-Statement-and-Notes (FSN) quarterly ZIPs → parse SUB, TAG, NUM, DIM tables → by CIK retrieve filings → adjust pre-split EPS (e.g. Apple pre-2014-06-04 ÷ 7) → rolling 4-quarter TTM EPS → join with adjusted prices to compute trailing P/E [ch.2 p.55-56].

**Web-scraping alt-data with Selenium + Splash** [ch.3 p.73-78]

Use `requests + BeautifulSoup` for static HTML; headless Firefox via Selenium to execute JavaScript; Scrapy + Splash for scalable crawling. Demonstrated to build a 10,000-restaurant OpenTable NYC booking dataset and to scrape earnings-call transcripts from SeekingAlpha [ch.3 p.72-79].

**Volatility Model (GARCH) Build Procedure** [ch.9 p.274]

Step A — Fit ARMA(p, q) to returns; inspect ACF/PACF to choose p, q [ch.9 p.274].
Step B — Test residuals for ARCH effects via ACF/PACF of squared residuals [ch.9 p.274].
Step C — If significant, jointly fit mean + GARCH(p, q); evaluate AIC/BIC [ch.9 p.274].
Step D — Validate: standardized residuals should look like white noise [ch.9 p.274].
Step E — Out-of-sample: rolling 10-year window, 1-step forecast, minimize RMSE vs realized squared deviations (example: GARCH(2,2) on NASDAQ) [ch.9 p.275-276].

**Pairs Trading via Cointegration** [ch.9 p.280-283]

Step A — Select candidate pairs by sector, fundamentals, or broad universe [ch.9 p.282].
Step B — Test each pair for cointegration via Engle-Granger two-step OR Johansen procedure [ch.9 p.281-282].
Step C — Keep pairs with stable, high-variance spreads for more trading opportunities [ch.9 p.283].
Step D — Model the spread as mean-reverting, e.g., Ornstein-Uhlenbeck [ch.9 p.283].
Step E — Entry when spread deviation exceeds threshold (e.g., 2σ); exit on return to mean [ch.9 p.283].

**Bayesian Sharpe Ratio (PyMC3)** [ch.10 p.317-318]

```python
with pm.Model() as sharpe_model:
    mean = pm.Normal('mean', mu=mean_prior, sd=std_prior)
    std  = pm.Uniform('std', lower=std_low, upper=std_high)
    nu   = pm.Exponential('nu_minus_two', 1/29) + 2   # t dof => fat tails
    returns = pm.StudentT('returns', nu=nu, mu=mean, sd=std, observed=data)
    sharpe = mean / std * np.sqrt(252)
    pm.Deterministic('sharpe', sharpe)
    trace = pm.sample(draws=25000, chains=4)   # NUTS
```

Produces full posterior of SR — enables effect-size comparison of two return series [ch.10 p.318-319].

**Hierarchical Risk Parity (HRP) — Prado 2016** [ch.13 p.434-435]

```
1. Compute asset-return correlation ρ; distance d = sqrt(0.5*(1 - ρ))
2. Hierarchical clustering on d (e.g., single linkage) → linkage_matrix
3. Quasi-diagonalize covariance by the cluster order
4. Recursive bisection:
    for each pair of sub-clusters (c0, c1):
        v0 = inverse-variance weighted variance of c0
        v1 = inverse-variance weighted variance of c1
        weights[c0] *= 1 - v0/(v0+v1)
        weights[c1] *= v0/(v0+v1)
```

Benchmarked against Mean-Variance (MV) and Equal-Weight (EW) on a Zipline ML strategy: Sharpe MV = 1.16, EW = 1.01, HRP = 0.83 — but HRP uses no return forecasts and is more robust to estimation error [ch.13 p.438].

**Factor Research (Zipline + Alphalens)** [ch.4 p.107-118]

```python
class MeanReversion(CustomFactor):
    inputs = [Returns(window_length=MONTH)]
    window_length = YEAR
    def compute(self, today, assets, out, monthly_returns):
        df = pd.DataFrame(monthly_returns)
        out[:] = df.iloc[-1].sub(df.mean()).div(df.std())

alphalens_data = get_clean_factor_and_forward_returns(
    factor=factor_data, prices=prices,
    periods=(5, 10, 21, 42), quantiles=5)
```

Outputs include mean-return-by-quantile, IC time series, and factor turnover [ch.4 p.112-118].

**LightGBM training recipe** [ch.12 p.390-400]

Use leaf-wise growth (not depth-wise) for faster convergence at higher overfit risk [ch.12 p.397]. Control `num_leaves` plus `max_depth` carefully [ch.12 p.398]. Use early_stopping on a held-out validation set — never the test set — and limit the number of trials to avoid validation-set overfitting [ch.12 p.373]. GOSS (gradient-based one-side sampling) provides speed on large datasets [ch.12 p.399]. Exclusive Feature Bundling reduces sparse-feature dimensionality [ch.12 p.399]. Apply SHAP values for interpreting predictions [ch.12 p.394].

**LDA topic modeling (Gensim)** [ch.15 p.476-478]

```python
from gensim.models import LdaModel
lda = LdaModel(corpus=train_corpus, num_topics=15, id2word=id2word,
               passes=25, alpha='symmetric')
lda.top_topics(corpus=train_corpus, coherence='u_mass')
```

On 700 earnings-call transcripts (22,582 statements, 1,529-word vocab) a 15-topic model surfaced themes such as clinical trials (topic 5), China/tariffs (topic 9), and tech issues (topic 11) [ch.15 p.479]. Coherence degrades after 25–30 topics and perplexity rises in parallel [ch.15 p.480].

**word2vec for SEC 10-Ks (Gensim skip-gram)** [ch.16 p.501-502]

```python
model = Word2Vec(sentences,
                 sg=1,            # 1=skip-gram, 0=CBOW
                 hs=0,            # 0=negative sampling, 1=hierarchical softmax
                 size=300,        # embedding dim
                 window=3,        # context window
                 min_count=50,
                 negative=10,
                 alpha=0.025, min_alpha=0.0001)
```

Corpus: 22,000 10-K filings 2013–2016 (6,500 companies); 11,000 filings label-joined with 1-month post-filing returns [ch.16 p.499-500]. Sweep results: skip-gram > CBOW; negative sampling > hierarchical softmax; context window < 5 degrades; larger vectors help — size=600 achieves best analogy accuracy at 38.5% [ch.16 p.502].

**CNN-TA time-series-as-image** [ch.18 p.595-596]

```
For each trading day:
    Compute 15 technical indicators (RSI, MACD, Bollinger, ...) × 15 lookback intervals
    Arrange as 15×15 grid, ordered by hierarchical clustering of mutual information
    Feed to CNN classifier → {buy, hold, sell}
```

Replicates Sezer & Ozbayoglu (2018) on Dow 30 + 9 most-traded ETFs, 2007–2017 [ch.18 p.595].

**Stacked LSTM for weekly stock-return classification** [ch.19 p.605-609]

```
Inputs: 52 weeks of lagged weekly returns + one-hot month + ticker embedding
Architecture: LSTM(25, dropout=0.2, return_sequences=True)
           → LSTM(10, dropout=0.2)
           → concat with ticker_embedding + month dummies
           → Dense → sigmoid
Data: ~2,500 tickers with complete history
```

Test AUC = 0.6816, test accuracy ≈ 58%, IC (prediction vs actual weekly return) = 0.32; top-vs-bottom quintile weekly spread ≈ 20 bps [ch.19 p.609].

**Conditional Autoencoder for asset pricing (GKX 2020)** [ch.20 p.658-662]

```
LEFT branch (beta network):
  Input: N stocks × P characteristics   → FFNN with hidden layer
                                        → output K factor loadings per stock (beta)
RIGHT branch (factor network):
  Input: individual stock returns       → autoencoder → K latent factors
OUTPUT:
  predicted return_{i,t} = dot(beta_i, factor_t)
Loss: MSE on reconstructed returns
```

Produces significant quintile-portfolio spread and positive long-short cumulative return on an unseen period [ch.20 p.671-672].

**TimeGAN (Yoon et al. 2019)** [ch.21 p.668-670, 676-678]

```
Components:
  embedder  : real   X → latent H        (autoencoder half 1)
  recovery  : latent H → reconstructed X (autoencoder half 2)
  generator : noise Z → latent H_hat
  discriminator: latent H/H_hat → real/fake
  supervisor: enforces stepwise transition dynamics in latent space
Training phases:
  1) embedder + recovery reconstruction loss
  2) supervised loss (next-latent-state prediction)
  3) joint adversarial + supervised + moment-matching loss
Evaluation:
  - PCA & t-SNE visualization for diversity
  - Discriminative score (test-set classifier real-vs-synthetic) for fidelity
  - TSTR (Train-on-Synthetic, Test-on-Real) sequence-prediction error for usefulness
```

Demonstrated on 15 years of Google OHLCV (6 features, 24 timesteps) [ch.21 p.668].

**Deep Q-Learning Trading Agent** [ch.22 p.679-681]

Define environment via OpenAI Gym with state = features (prices, technicals, position), actions = {buy, hold, sell}, reward = incremental PnL (optionally risk-adjusted) [ch.22 p.681-682]. Build deep Q-network approximating Q(s, a) [ch.22 p.680]. Train with experience replay plus target network [ch.22 p.680]. Use epsilon-greedy exploration decaying over training [ch.22 p.680]. Backtest on unseen period before deploying [ch.22 p.680; ch.23 p.719].

### Pitfalls e Anti-patterns

- [ch.8 p.223-224] **Look-ahead bias** from restated fundamentals, retroactive splits, incorrect EPS/price alignment.
- [ch.8 p.224] **Survivorship bias** — only using currently-tradable universe.
- [ch.8 p.225] **Outlier mis-treatment** — winsorizing extreme values that are actually realistic market events.
- [ch.8 p.225] **Unrepresentative sample period** — training set may lack important market-regime aspects (e.g. volatility or volume regimes) or include too few/too many extreme events; mitigate by covering multiple regimes or augmenting with synthetic data.
- [ch.8 p.225-226] **Ignoring transaction costs and slippage** — small per-trade costs compound and kill high-turnover strategies.
- [ch.8 p.226] **Short-sale / leverage assumptions** not available in reality (borrow constraints, margin).
- [ch.8 p.226] **Mis-timing signals vs. execution** — using close-price signals executed at close (impossible live).
- [ch.8 p.226-227] **Multiple-testing / p-hacking**: selecting among many variants on same data inflates best-variant Sharpe.
- [ch.8 p.227] **Ignoring backtest overfitting** inherited from prior knowledge of what worked in others' published research.
- [ch.6 p.167] **IID assumption violation** — applying standard K-fold to serially-correlated financial data leaks future into past.
- [ch.6 p.169] **Overlapping labels** (e.g., 5-day returns with daily observations) create train-test contamination unless purged.
- [ch.11 p.334] **Not tuning tree hyperparameters** — default decision trees overfit tabular financial data.
- [ch.12 p.373] **Early stopping using the test set** leaks test information into training decisions; use a separate validation set.
- [ch.12 p.373] **Running thousands of early-stopped trials** on the same validation set overfits to *that* validation set even though the test set is held out; the effective number of independent experiments is far smaller than the trial count.
- [ch.13 p.413] **Applying PCA to fat-tailed return data** — PCA assumes normality and will underweight higher-order moments; consider robust / non-linear alternatives (ICA, autoencoders).
- [ch.16 p.499-500] **Using generic pretrained vectors (GloVe-Wikipedia) on domain-specific financial text** — domain vocabulary (e.g. SEC 10-K terms) is under-represented; train custom embeddings on a financial corpus.
- [ch.23 p.716] **Torturing the data** — "if you torture the data long enough, it will confess" (López de Prado critique).
- [ch.23 p.720] **Treating DL/ensemble as black box** — absent SHAP/interpretability, can't distinguish spurious vs. economic signal.

---
