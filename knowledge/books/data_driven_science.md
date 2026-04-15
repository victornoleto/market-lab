# Data-Driven Science & Engineering: Machine Learning, Dynamical Systems, and Control

## Metadata
- **Author:** Steven L. Brunton (Mechanical Engineering, University of Washington) & J. Nathan Kutz (Applied Mathematics, University of Washington) [p.1 title page of extract]
- **Year:** 2021 (second edition / 2021 copyright notice on every page footer) [p.2, p.3, and throughout — "Copyright © 2021 Brunton & Kutz, Cambridge University Press"]
- **Publisher:** Cambridge University Press [p.2 footer]
- **Pages:** The extracted PDF contains Chapter 11 (pp.499-535) plus the opening of the bibliography (pp.663-664). Full book N/A — only this chapter was delivered to the pipeline.
- **ISBN:** N/A — not present in the extracted pages (title page p.1 of PDF only shows title/authors).
- **Main focus:** Reinforcement learning (RL) as the intersection of control theory and machine learning — model-based (policy/value iteration, HJB), model-free (Q-learning, SARSA, TD), policy gradients, and deep RL (DQN, DDQN, A2C) — with a physical-systems/control bent rather than finance.

> **Extraction scope notice:** The PDF delivered to this pipeline contains ONLY Chapter 11 (Reinforcement Learning) — printed pages 499-535 — plus the opening bibliography pages 663-664. The other 10 chapters of the book (SVD, Fourier/Wavelet transforms, Sparsity & Compressed Sensing, Regression, Data-Driven Dynamical Systems, Koopman, SINDy, Neural Networks, Control Theory, Dimensionality Reduction, etc.) are NOT in the source file and are not summarized here. Any claims made about those chapters would be fabrication. **Page citations below use PDF-page indices [p.1-76] of the extracted file** (which corresponds to printed pages 499-535 of the full book; offset = printed − 498). This matches the `[PAGE N]` markers in `books/extracted/data_driven_science/_full.txt` and what the deterministic citation checker validates against.

## 1. Core Thesis
Reinforcement learning is a biologically-inspired third branch of machine learning (alongside supervised and unsupervised learning) in which an agent learns control policies through trial-and-error interaction with an environment, sensing states, taking actions, and receiving sparse/delayed rewards [p.2, ch.11]. The entire chapter is organized around a unifying optimization framework: learn either the policy π(s,a), the value function V(s), or the quality function Q(s,a), all of which satisfy Bellman's recursive equation of optimality [p.6, eq.11.11]. The "major dichotomies" that structure the field are model-based vs. model-free, gradient-based vs. gradient-free, and on-policy vs. off-policy [p.10, Fig.11.3]. RL connects mathematically to optimal nonlinear control via the Hamilton-Jacobi-Bellman (HJB) equation, the continuous-time generalization of Bellman's principle [p.32, §11.6].

## 2. Main Concepts
- **Agent / Environment / State / Action / Reward / Policy** — canonical RL five-tuple. Agent observes state s ∈ S, takes action a ∈ A via policy π, receives reward r [p.3, Fig.11.1].
- **Policy π(s,a)** — probability distribution Pr(a=a | s=s); may be a lookup table (discrete) or a parameterized approximator π(s, a, θ) such as a deep neural network ("deep policy network") [p.3-4, eq.11.1-11.2].
- **Markov Decision Process (MDP)** — tuple (S, A, R) with transition P(s', s, a) = Pr(s_{k+1}=s' | s_k=s, a_k=a) and reward function R; defining property is that future depends only on current state, not history [p.4-5, eq.11.3-11.4].
- **Transition matrix T** — stochastic matrix (columns sum to 1) representing Markov process; s' = Ts; steady state μ is the eigenvector of T at eigenvalue 1 [p.5, eq.11.6].
- **Value function V^π(s)** — expected discounted cumulative future reward from state s under policy π [p.6, eq.11.8].
- **Bellman equation / principle of optimality** — V(s) = max_π E(r₀ + γV(s')); a multi-step optimal policy must be locally optimal at every sub-sequence [p.6, eq.11.11; p.11, §dynamic programming].
- **Discount factor γ** — reflects economic principle that current rewards are more valuable than future ones [p.6].
- **Quality function Q(s,a)** — E(R(s',s,a) + γV(s')); encodes joint desirability of (state, action); policy and value may both be extracted from Q [p.14, eq.11.17-11.18].
- **Model-based vs. model-free RL** — model-based uses known/learned P and R (policy iteration, value iteration); model-free learns directly from experience (Q-learning, SARSA) [p.10, Fig.11.3; p.14, §11.3].
- **On-policy vs. off-policy** — on-policy (SARSA) updates using actions actually taken by current policy; off-policy (Q-learning) updates using optimal action regardless of action taken [p.18-19].
- **Monte Carlo learning** — episodic; uses full-episode cumulative reward R_Σ to update V or Q with credit shared equally among visited states [p.15, eq.11.19-11.22].
- **Temporal Difference (TD) learning** — bootstrapped sample-based updates using one-step-ahead estimates; continuous (non-episodic); lower variance but biased due to bootstrapping [p.16-17, eq.11.23-11.24].
- **TD target / TD error** — TD target = r_k + γV(s_{k+1}); TD error = TD target − V_old(s_k) [p.17, eq.11.24].
- **TD(n)** — n-step look-ahead TD target; in the limit of a full episode, TD(n) → Monte Carlo [p.17-18, eq.11.26].
- **TD-λ** — Sutton (1988); weighted average of all TD(n) targets with geometric weight λ^(n−1) [p.18, eq.11.27].
- **SARSA (State-Action-Reward-State-Action)** — on-policy TD for Q; uses Q(s_{k+1}, a_{k+1}) with a_{k+1} from current policy [p.18-19, eq.11.29].
- **Q-learning** — off-policy TD for Q; uses max_a Q(s_{k+1}, a) for the TD target [p.19, eq.11.32].
- **ε-greedy exploration** — take current optimal action with prob. 1−ε, random action with prob. ε; ε typically annealed from 1 downward [p.20-21].
- **Experience replay** — store past (s,a,r,s') transitions and re-train on them; only possible because Q-learning is off-policy [p.20, §experience replay].
- **Prioritized experience replay** — weight past experiences by magnitude of TD error [p.24].
- **Credit assignment problem** — Minsky-coined challenge of identifying which action sequence was responsible for a sparse/delayed reward [p.7].
- **Bias-variance tradeoff (in RL)** — Monte Carlo = no bias / high variance; TD = lower variance / introduced bias via bootstrapping [p.18].
- **Deep Q Network (DQN)** — CNN approximator for Q, introduced by Mnih et al. (Nature 2015) for Atari games [p.24, ref. 519].
- **Double DQN** — separate target and prediction networks to reduce bias early in training [p.24, ref. 742].
- **Dueling Deep Q Network (DDQN)** — splits Q(s,a,θ) = V(s,θ₁) + A(s,a,θ₂) where A is "advantage function" [p.24, eq.11.39].
- **Policy gradient** — directly optimizes parameters θ of π_θ via gradient ascent on expected cumulative reward; REINFORCE algorithm and natural policy gradients [p.21-22, eq.11.33-11.35].
- **Advantage Actor-Critic (A2C)** — actor is a deep policy net; critic is a DDQN [p.25, eq.11.41].
- **Reward shaping** — designing proxy intermediate rewards to densify sparse signals; e.g., point values per chess piece [p.25-26].
- **Hindsight experience replay (HER)** — reinterpret failed trials as successes at a *different* task; densifies reward and enables learning whole families of tasks [p.26, ref. 22, 438].
- **Curiosity-driven exploration** — augments reward with novelty signal based on forward-model prediction error (Intrinsic Curiosity Module, ICM) [p.26-27, ref. 562].
- **Hamilton-Jacobi-Bellman (HJB) equation** — PDE generalization of the Bellman equation to continuous-time nonlinear optimal control [p.33, eq.11.45].
- **Cost-to-go** — control-theory name for the value function: integrated remaining cost from state x(t) under optimal control until t_f [p.33].

## 3. Formulas / Equations
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

## 4. Algorithms and Pseudocode
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

## 5. Explicit Trading Rules
N/A — This chapter is a pedagogical treatment of Reinforcement Learning for general dynamical systems, control, robotics, and board/video games. It does NOT discuss trading, asset pricing, portfolio optimization, execution, or any financial-market application. No trading rule ("if X then Y") is stated anywhere in the extracted pages. Applying RL to trading would require additional domain knowledge (reward function design, state/action spaces for markets, transaction costs, non-stationarity) that is not covered here. For explicit trading rules see `systematic_trading.md` or `evidence_based_ta.md`.

## 6. Pitfalls and Anti-patterns
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

## 7. Sensitive Parameters
- **Discount factor γ** [p.6, eq.11.8]: economic-principle justification — "current rewards are more valuable than future rewards." No numeric recommendation; treated as problem-specific.
- **Learning rate α ∈ [0, 1]** [p.16, eq.11.22]: used in MC, TD, SARSA, Q-learning updates. Explicit author comment: "Larger learning rates α > 1/n will favor more recent experience" [p.16]. Set per task; no universal optimum given.
- **Exploration ε ∈ [0, 1]** in ε-greedy [p.20-21]: "Typically, the value of ε will be initialized to a large value, often ε = 1. Throughout the course of training, ε decays so that as the Q function improves, the agent increasingly takes the current optimal action. This is closely related to simulated annealing from optimization" [p.21]. Explicit schedule guidance: anneal from 1 toward 0.
- **TD-λ weight λ ∈ [0, 1]** [p.18, eq.11.27]: interpolates between TD(0) (λ=0) and Monte Carlo (λ=1). No numeric recommendation; used in Tesauro's 1995 backgammon demo [ref. 712].
- **Target-network update period τ (DQN)** [p.24]: "It may be necessary to fix the target network for multiple training iterations of the prediction network before updating to improve stability and convergence" [ref. 264]. No specific τ recommended.
- **Replay buffer / prioritization weights** [p.24]: weight by TD-error magnitude; "prioritized experience replay" [ref. 642]. No specific weighting formula given in the extract.
- **n in TD(n) / SARSA(n)** [p.17-18]: controls bias-variance tradeoff. As n → ∞ (full episode), TD(n) → Monte Carlo (high variance, no bias). As n = 0, lowest variance, highest bias. No numeric recommendation.
- **Neural-network architecture parameters for DQN** [p.23, Fig.11.5]: convolutional layers + fully-connected layers used in Mnih et al. 2015 [ref. 519]. Exact layer sizes N/A — not in extract; see original Mnih et al. paper.

## 8. Key Literal Quotes
> "In reinforcement learning, an agent senses the state of its environment and learns take appropriate actions to optimize future rewards. The ultimate goal in RL is to learn an effective control strategy or set of actions through positive or negative reinforcement." — [p.2]

> "This expression, known as Bellman's equation, is a statement of Bellman's principle of optimality, and it is a central result that underpins modern RL." — [p.6]

> "One of the central challenges of reinforcement learning is that rewards are often extremely rare and may be significantly delayed from a sequence of good control actions. This challenge leads to the so-called credit assignment problem, coined by Minsky [514] to describe the challenge of knowing what action sequence was responsible for the reward ultimately received. These sparse and delayed rewards have been a central challenge in RL for six decades, and they are still a focus of research today." — [p.7]

> "Reinforcement learning is, therefore, well-suited for situations where some combination of the following are true: evaluating a policy is inexpensive, as in board games; there are sufficient resources to perform a near brute-force optimization, as in evolutionary optimization; no other control strategy works." — [p.7]

> "Generally, Q-learning will learn a more optimal solution faster than SARSA, but with more variance in the solution. However, SARSA will typically yield more cumulative rewards during the training process, since it is on-policy. In safety critical applications, such as self-driving cars or other applications where there can be catastrophic failure, SARSA will typically learn less optimal solutions, but with a better safety margin, since it is maximizing on-policy rewards." — [p.19]

> "Reward shaping is quite common and can be very effective. However, these rewards require expert human guidance to design, and this requires customized effort for each new task. Thus, reward shaping is not a viable strategy for a generalized artificial intelligence agent capable of learning multiple games or tasks. In addition, reward shaping generally limits the upper end of the agent's performance to that of the human expert." — [p.26]

## 9. Cross-references to Other Books in This Knowledge Base
- **Bellman equation & dynamic programming**: mentioned but not developed in any of the previously-processed trading/quant books. Closest conceptual neighbor is the optimal-control background assumed in `advances_fin_ml.md` (López de Prado uses cross-validation / purged splits but does not treat RL).
- **Bias-variance tradeoff** [p.18]: same concept discussed in `ml_for_asset_managers.md#generalization-error` as the root cause of overfitting in financial ML — Brunton & Kutz treat it from the TD-vs-Monte-Carlo angle [p.18]; López de Prado treats it from the number-of-trials / Deflated Sharpe angle.
- **Curse of dimensionality** [p.11, p.35]: the motivation for approximate methods (neural nets, Koopman, SINDy) — same theme appears implicitly in the parsimony / parameter-budget discussions of `systematic_trading.md` (Carver) and in López de Prado's anti-backtest-overfit framework in `advances_fin_ml.md` and `ml_for_asset_managers.md`.
- **Markov Decision Process / Markov assumption**: related to the Markov properties of time series in `time_series_hamilton.md` (Hamilton treats ARMA/VAR/state-space with MDP-compatible Markov assumption, though not in RL language).
- **Trading applications**: no direct cross-reference possible — this chapter does not treat finance. RL applications to portfolio construction / execution are NOT covered in this extract and not covered in `evidence_based_ta.md` either; would require additional books (Ritter / Moody & Saffell / Deng et al.) not yet in this knowledge base.
- **Overall**: this chapter stands alone in the current knowledge base as the authoritative treatment of RL primitives (MDP, Bellman, Q-learning, policy gradient, DQN, HJB). No redundant material in the other five summaries. Useful as a reference when/if Phase 3+ of the trading system explores RL-based position sizing or execution-agent learning.
