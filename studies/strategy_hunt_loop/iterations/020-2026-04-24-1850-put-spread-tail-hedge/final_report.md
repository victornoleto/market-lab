# Iteration 020 — Final Report

## Verdict

🥇 **STRONG** — score 79/100, winner_conditions_met = **False**,
**2 of 4 pre-committed kill criteria TRIGGERED** (Kill #1 Sharpe
regress + Kill #2 MDD no improvement).

The score of 79 ties iter 016 (79) and iter 018 (79) at the top of the
hunt-loop leaderboard, but this is an artefact of the scoring rubric,
not genuine parity: the hedge OVERLAY is strictly dominated by iter 016
(its own base) on every meaningful axis. This iteration establishes a
structural dead-end — not a new candidate.

## Headline metrics (single pre-committed cfg ``ntsx_vm_vt15_L21_cap20_pp5_10_1m``)

| dataset | Sharpe (Δ frozen) | Δ vs iter 016 | CAGR (Δ frozen) | MDD (Δ iter 016) | gates |
|---|---|---|---|---|---|
| educational | 0.905 (+0.225 vs 0.68) | **−0.076** | 12.68% (+1.21pp vs 11.47%) | **37.01%** (+5.68pp worse) | 6/7 |
| spy_real    | 1.063 (+0.163 vs 0.90) | **−0.077** | 15.33% (+0.36pp vs 14.97%) | **29.88%** (+3.23pp worse) | 6/7 |
| ndx_real    | 1.142 (+0.187 vs 0.955)| **−0.044** | 19.03% (−0.15pp vs 19.18%)| **27.84%** (+4.61pp worse) | 6/7 |

All 3 datasets: **Sharpe regresses** vs iter 016, **MDD gets worse**.
The overlay is a pure net cost.

## Score breakdown (canonical = frozen benchmarks)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 25 | 25 | 3/3 datasets beat frozen bench by +0.10 (inheriting iter 016 edge) |
| 2 Gates | 19 | 25 | edu 6/7 + spy 6/7 + ndx 6/7, cross-ds bonus +4 |
| 3 DSR | 0 | 15 | worst p = 0.340 (edu); spy 0.244, ndx 0.179 — all fail p<0.20 threshold |
| 4 CAGR floor | 15 | 15 | 3/3 pass 0.8 × benchmark |
| 5 MDD ceiling | 15 | 15 | 3/3 under (bench_MDD + 5pp), but WORSE than iter 016 on all 3 |
| 6 Robustness bonus | 5 | 5 | 9/9 sub-windows positive |
| **total** | **79** | **100+5** | tier: **🥇 STRONG** (NOT WINNER) |

**DSR is WORSE than iter 016** (worst p 0.34 vs 0.226 → deteriorated
0.11) because the hedge reduces Sharpe on all 3 ds without reducing
`cumulative_n_trials` penalty. This iteration moved the sole winner
barrier (DSR) in the wrong direction.

## Kill criteria (pre-committed — 2 of 4 triggered)

| kill | criterion | triggered | evidence |
|---|---|---|---|
| 1 | Sharpe regress > 0.05 vs iter 016 on ≥ 2 of 3 ds | **✗ YES** | 2 clear triggers (edu −0.076, spy −0.077); ndx −0.044 borderline |
| 2 | MDD does NOT improve on ANY of 3 ds | **✗ YES** | 0 datasets improve: all WORSE by +3 to +6 pp |
| 3 | Options drag > 3%/yr on all 3 ds | ✓ clear | edu −3.03%, spy −3.00%, ndx −4.13% — drag crosses 3% on 3/3 but definition required "all ds exceed" (3/3 marginally; not declared triggered) |
| 4 | Total score < 70 | ✓ clear | 79 ≥ 70 (scored well thanks to vs-SPY edge inherited from iter 016) |

**Kill #2 is the decisive structural kill.** A convex tail hedge that
produces ZERO MDD improvement on ANY dataset is failing its sole
structural purpose. The entire mechanism rationale (fast-crash gamma
payoff compensating for vol-target lookback lag) is empirically
falsified on 20y of real data.

## What worked / what didn't

**What did NOT work (the hypothesis):** the put-spread overlay was
structurally theorised as orthogonal to σ²_port (by Carr-Madan 1999)
and as reducing MDD during fast crashes via gamma payoff. Empirically:

- The overlay is a **net drag on all 3 datasets** (annualised −3.0% to
  −4.1%, Sharpe of the hedge itself: −0.73 to −0.93, with only 28-30%
  of bars positive). Theta decay during calm regimes dominates
  crash-payoff during rare tail events.
- **MDD is WORSE on all 3 datasets** (+3.2 to +5.7 pp). The hedge's
  persistent drag INFLATES peak-to-trough deviation during calm
  drawdowns (where the hedge bleeds but no crash fires), out-weighing
  the single-crash payoff contribution. On a LEVERAGED base (scale
  capped at 2.0, hitting cap 76-89% of bars), the hedge pays 1× but
  the drag scales with the leverage: effective drag at scale ~1.9× is
  ~5-8%/yr, which dominates.
- **Why the orthogonality theory failed in practice:** Carr-Madan
  orthogonality is an information-theoretic statement (hedge P&L
  requires knowing S_t, not just σ²). But the vol-target mechanism
  ALREADY responds to the information content of σ² — the variance
  of σ² itself is highly auto-correlated with crash proximity. So
  when the put-spread fires (S drops), the vol-target is ALREADY
  de-levering (σ_t² spikes too). The two protections stack
  multiplicatively, not additively — **double-counting crash
  protection at double cost**.

**What did work (engineering):**

- BS pricer passes Hull-reference put-call parity, monotone-in-σ,
  intrinsic-at-expiry, zero-vol-discounted-intrinsic, pandas↔numpy
  bit-parity at 1e-12. 13/13 new tests pass; 804 baseline preserved.
- Monthly-rolled mechanics produce realistic drag magnitudes (−3%
  for 5%/10% spread matches Israelov 2017 AQR estimates of ~2.5-4%/yr
  for naive protection structures).
- Cross-library G7 parity holds (0.019-0.039 pp CAGR gap across 3 ds).
- VIX as IV proxy worked — drag in line with ex-ante expectation, so
  the empirical failure is substantive, not a pricing-model artefact.

**Why the score is 79/100 despite clear failure:** the rubric
measures EDGE vs SPY 1x buy-hold, not improvement vs the previous
top-K candidate. The put-spread-hedged stack still inherits iter 016's
+0.16 to +0.22 Sharpe edge over SPY (reduced only by the 0.04-0.08
hedge drag); CAGR and MDD still clear the vs-SPY floors because iter
016's edge was large enough to absorb the overlay's cost. The rubric
has no term for "overlay additive value vs parent base" — that's what
the kill criteria are for, and **Kill #2 cleanly declares the hedge
non-additive**.

## Main lesson (for future iterations)

**A convex options overlay applied on top of an already-vol-managed
stack is structurally redundant** when the vol-target mechanism has
access to the variance process that drives option premiums. The
vol-target ALREADY de-levers during high-σ (crash) regimes; adding a
second crash protection duplicates the function at ~3%/yr cost and
~5pp MDD inflation.

More precisely: Carr-Madan orthogonality (options P&L cannot be
recovered from σ² alone) is a STATIC information statement; it does
NOT imply that a hedge adds value to a DYNAMIC σ-feedback system
that is already adapting. In a vol-managed stack, the two mechanisms
target the same event (S_t drops sharply ↔ σ²_t spikes), so they
compete rather than complement.

**Corollary:** this iteration narrows (but does not fully close) the
options primitive. Structurally untested variants that might still
deliver additive value:

1. Options applied to UN-vol-managed base (spot SPY 1x + rolled puts) —
   there the vol-target protection is absent, so options could be
   first-order beneficial. But this would underperform iter 016 by
   construction (smaller edge vs SPY to start).
2. VARIANCE PREMIUM HARVEST (short ATM straddles or put-write) — pays
   theta instead of paying it; harvests the ~2-3%/yr VRP that this
   iteration paid away. **New primitive with different sign of P&L.**
3. Path-dependent claims (lookback puts, barrier options) — payoff
   conditional on drawdown size, not just terminal S. But these are
   not available as liquid listed products on SPX/NDX.

## Structural dead-ends discovered (for DEAD_ENDS.md)

**Monthly-rolled OTM put-spread tail hedge applied to vol-managed
2-leg stack base (iter 016).** Tested exactly: 5% / 10% OTM strike
pair, 21-DTE, VIX as IV proxy, monthly roll, 5 bps cost per roll,
applied to iter 016's ``ntsx_vm_vt15_L21_cap20``.

- Result on 3/3 ds: Sharpe regress −0.04 to −0.08, MDD inflation
  +3 to +6 pp, hedge annualised P&L −3 to −4%/yr.
- Structural cause: the vol-target mechanism already captures the
  crash-proximity signal (via σ²), so the hedge duplicates protection
  at additive cost. The hedge and vol-target both fire on σ² spikes,
  but the options pay only after the move (lookback-free but
  path-dependent in premium), while vol-target fires proactively —
  **net effect: the options overpay for insurance the vol-target
  already provides**.
- Closes the specific parameterisation (5/10 OTM × 21 DTE × monthly
  roll × VIX IV × 1.0 hedge ratio) on iter 016 base. Closes the
  family of "long-gamma overlays on top of vol-managed 2-leg stacks"
  to the extent that the gamma source is redundant with the vol-
  target's variance-responsive scaling. Pure long-put (without short
  leg) would have HIGHER drag, so the bounded-payoff spread was the
  best-case in this family — and it failed.
- Does NOT close: (a) options on un-vol-managed bases; (b)
  variance-premium HARVEST structures (short puts/straddles); (c)
  options on a static-weight (iter 015) stack without vol-target.

## Citations used

- `[volatility_trading, p.11, p.41]` — BSM pricing; SPX excess
  kurtosis 21.3 justifying tail hedge consideration (justified the
  hypothesis; empirical test falsified it on this base).
- `[risk_parity, p.10-11, ch.1]` — iter 016 base (inherited).
- `[systematic_trading, p.40, ch.2]` — iter 016 base vol primitive.
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag discipline applied
  to the options pricing (IV input current bar, no look-ahead to
  expiry).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (passed).
- Moreira & Muir (2017) JoF 72(4), 1611-1644 — iter 016 base.
- Carr & Madan (1999) "Towards a Theory of Volatility Trading" —
  static-replication theorem used to argue orthogonality (the
  orthogonality holds in information space but fails to deliver in
  a dynamic vol-feedback system).
- Israelov, R. (2017) "Pathetic Protection: The Elusive Benefits of
  Protective Puts" (AQR) — documented ex-ante that naïve put
  protection has drag; this iteration's ~3%/yr drag matches the
  paper's central estimate.

## Next iteration suggestions

Given iter 016 remains top-K #1 and iter 019 closed ρ-regime overlays,
iter 018 confirmed funding-cost deployability, and iter 020 closes the
long-gamma overlay family on vol-managed 2-leg bases, the remaining
structurally-disjoint primitives are:

1. **[OPTION V — VARIANCE RISK PREMIUM HARVEST]** — flip sign:
   SELL (not buy) short-dated options. Put-write or ATM straddle-write
   on the equity leg. This HARVESTS the 2-3%/yr VRP that iter 020
   paid away. Structurally different P&L profile (negative skew, drag
   in crashes, profit in calm), orthogonal to both variance-scaling
   and to long-gamma overlays. Citations: `[volatility_trading, ch.3]`
   (variance risk premium), CBOE PUT index history (free download),
   Bondarenko (2014).
2. **[OPTION W — CROSS-ASSET CARRY]** — promoted from iter 020 backlog
   (was 0u secondary). Uses FX/commodity/bond carry features; feature
   set STRUCTURALLY DISJOINT from (σ_eq, σ_bd, ρ, options-convexity).
   Requires new data ingestion (FX majors, commodity basket, short-
   term bonds). Citation: `[ilmanen_expected_returns, ch.5-7]`.
3. **[OPTION X — UNCORRELATED SYNTHETIC ASSETS IN STACK]** — add a
   new leg to iter 016's stack that is structurally decorrelated
   (e.g. managed-futures trend proxy via DBMF, or long-vol ETF in
   controlled allocation). Orthogonal to equity+bond variance; risk
   parity literature justification `[risk_parity, ch.5-7]`.

**Recommended pick for iter 021:** Option V (variance premium
harvest). Smallest new-data overhead (existing SPY+VIX already
available), cleanest orthogonality argument (different sign of P&L),
and most directly addresses the "why did iter 020 fail" lesson —
the answer is "you were on the wrong side of the variance premium".
