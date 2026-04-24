# Iteration 018 — Funding-cost-modeled iter 016 replay (Option Q)

## Hypothesis

Iter 016 (`ntsx_vm_vt15_L21_cap20`, 79/100 STRONG, 4/5 winner conditions,
hunt-loop top-K #1) uses a **synthetic** NTSX-style stack: 0.6 fixed weight
on equity × dynamic scale + 0.4 fixed weight on bond × dynamic scale,
scale ∈ [0, 2.0] via Moreira-Muir variance-target. In reality, a return-
stacked ETF that delivers > 1.0× gross exposure on < 1.0× NAV has to
finance the extra notional via futures rolling or prime-broker credit,
at a cost ≈ `(scale − 1.0) × r_Tbill` per bar. The iter 016 simulator
omits this cost (explicit `funding_cost_modeled: false`).

The hypothesis for iter 018: **the ~0.24-0.30 Sharpe edge that iter 016
displayed over the naïve SPY / QQQ benchmark survives realistic funding-
cost modeling without collapsing below the +0.10 strict winner gate on
a majority of real datasets**. Falsifying this hypothesis would
downgrade iter 016 from "deployable candidate" to "simulator artifact";
confirming it would elevate iter 016 to the only iteration whose Sharpe
edge has been stress-tested against its largest-known unmodeled cost.

This is not a new strategy trial — it is a **cost-model audit of the
hunt-loop top candidate**. `cumulative_n_trials` remains **4264**
(unchanged; same cfg, same weights, same vol-target, same universe).
Only the per-bar P&L stream changes via a deterministic subtraction of
a funding-cost series.

## Primary citation

`[risk_parity, p.80-84, ch.4]` — leverage / margin cost in levered-
portfolio return decomposition; explicit form `r_lev = L · r_asset −
(L − 1) · r_f` for levered exposure.

## Additional citations

- `[systematic_trading, p.170-171, ch.11]` — Carver IDM ≤ 2.5 as a
  "marginal cost of risk" constraint; leverage above 1.0× must earn
  excess return over financing cost.
- `[advances_fin_ml, p.31-34]` — cross-lib / cross-cost-model parity
  discipline; same rule of "isolate one change at a time" applies.
- `[ilmanen_expected_returns, ch.3]` — risk-free rate as the universal
  deflator of any levered return stream.
- **NTSX prospectus (WisdomTree / U.S. Treasury 2% Target Managed
  Duration Index)** — discloses ~0.3-0.9 % annual expense drag on the
  synthetic 90/60 stack, attributable to (a) 0.20 % ER, (b) Treasury-
  futures rolling spread vs cash bonds, (c) financing carry on the
  levered futures leg. The synthetic-ETF replication we simulate in
  iter 016 inherits (b) + (c) exactly.
- Web: Moreira & Muir (2017) "Volatility-Managed Portfolios." *JoF*
  72(4), 1611-1644 — DOI
  [10.1111/jofi.12513](https://doi.org/10.1111/jofi.12513). Iter 016
  vol-target primitive. Their Table IV reports gross Sharpe (no
  funding cost); the paper footnote 11 acknowledges "the results are
  not qualitatively affected by a constant 2 % financing rate
  assumption" — iter 018 tests this empirically for a variable-rate
  environment 2006-2026.
- Web: Willenbrock (2011) "Diversification Return, Portfolio Rebalancing,
  and the Commodity Return Puzzle." *FAJ* 67(4) — SSRN
  [1972085](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1972085).
  Leverage-cost decomposition framework.

## Edge source

iter 016 itself is the candidate. The "edge" iter 018 stress-tests is
the 0.24-0.30 raw Sharpe uplift the synthetic stack shows over SPY/QQQ
buy-hold. iter 018's *own* edge is **honesty**: if the Sharpe edge
holds after subtracting `(scale − 1) × r_Tbill / 252` per bar, iter 016
is deployability-validated; if it collapses, iter 016 is honestly
downgraded.

## Datasets

Unchanged from iter 016 (keeps the comparison pure):

- **educational** (SPY + IEF, 2006-01-03 → 2026-04-15, ~20y "deep"
  sample) — SHV inception is 2007-01-11. For the pre-SHV segment
  (251 bars), we fall back to a **constant daily funding cost = IRX
  approximation 4.75 % / 252 ≈ 1.88 bps**, matching the 2006 Fed Funds
  target midpoint (`[ilmanen_expected_returns, ch.3]` baseline T-bill).
  Reason to test here: 20-year window gives DSR more bars; iter 016's
  edge is Sharpe 0.98 on this window. Funding cost was highest in
  2007-2008 (~5%) and lowest 2010-2015 (~0.1%).
- **spy_real** (SPY + IEF, 2009-06-25 → 2026-04-15, 17 y post-GFC) —
  SHV covers the full window. Iter 016 Sharpe 1.14. Funding rates
  spanned 0.0-5.5 % over the sample (ZIRP 2009-2015, hikes 2015-2019,
  ZIRP again 2020-2022, hikes 2022-2024). This is the dataset where
  funding-cost realism matters most.
- **ndx_real** (QQQ + IEF, 2010-02-12 → 2026-04-15, 16 y tech-heavy) —
  SHV covers the full window. Iter 016 Sharpe 1.19. Same funding
  regime as spy_real; test whether the tech-heavy equity leg's higher
  raw return absorbs the funding cost better than SPY's.

## Kill criteria (pre-committed)

Hypothesis **falsified** if ANY of the following occur:

1. **Post-cost Sharpe edge < +0.10 on ≥ 2 of 3 datasets** (winner
   condition 1 fails majority). Iter 016's gross edges were
   +0.30/+0.24/+0.24; the maximum plausible cost drag on gross Sharpe
   for iter 016's scale-mean ~1.4-1.6 (≈ 0.4-0.6 excess leverage) at
   avg T-bill ~2 % is approximately `0.5 × 0.02 = 1 %` return drag
   ⇒ Sharpe damage ≈ `1 % / portfolio-vol 15 %` ≈ −0.067. A drop of
   > 0.20 would indicate the stack mechanism was largely funding-cost-
   driven illusion.
2. **Post-cost winner conditions collapse to ≤ 2 / 5** (from iter
   016's 4/5). Any single-criterion collapse (Sharpe, CAGR floor,
   MDD ceiling) past the strict gate on majority datasets.
3. **Post-cost score < 60** (dropping iter 016 out of STRONG tier into
   PROMISING or worse; −19 points from 79).

Hypothesis **confirmed (iter 016 deployable)** if ALL three hold:

- Post-cost Sharpe edge ≥ +0.10 on ≥ 2 of 3 datasets
- Post-cost winner conditions ≥ 3 / 5
- Post-cost score ≥ 65 (PROMISING tier minimum); STRONG confirmation
  would require ≥ 75.

## Expected budget

- **Configs tested**: 0 new (same cfg `ntsx_vm_vt15_L21_cap20` under
  a new cost model; `cumulative_n_trials` unchanged at 4264).
- **Wall-time**: ~5 min per dataset × 3 = 15 min backtest + 30 min
  gate compute + 20 min final report. Total ~1 h 15 min (well below
  2 h cap).
- **Files to create**:
  1. `funding_cost_wrapper.py` — pure wrapper around
     `iter 016 / static_stack_vm.apply_static_stack_vol_managed` that
     loads SHV, aligns, subtracts `max(scale[t] − 1, 0) × r_Tbill[t]`
     from net returns per bar. No new simulator; reuse iter 016's
     primitive unchanged.
  2. `numpy_reference_funding.py` — hand-rolled numpy reference for
     the funding-cost subtraction, for G7 cross-lib parity.
  3. `run_backtests.py` — 3-dataset runner, identical to iter 016's
     except it calls the wrapper. Produces `results.json`.
  4. `compute_gates_and_score.py` — 7 gates + score on post-cost
     net returns. Produces `verdict.json`.
  5. `final_report.md` — Stage 5 deliverable.
- **Files NOT to create**: no new simulator module (wrapper only),
  no new TDD spec if the wrapper is trivial enough to verify inline.
  Pytest baseline 844 + 5 stays green.

## Implementation plan

1. **Load SHV** (2007-01-11 → 2026-04-20) from Tiingo cache; compute
   daily simple return on `adj_close`. For bars before SHV inception
   (educational 2006-01-03 → 2007-01-10, 251 bars), pad with constant
   `r_Tbill_daily = 0.0475 / 252 ≈ 1.88e-4` (FRED DGS3MO 2006 mean).
2. **Run iter 016's primitive** unchanged on each of 3 datasets to
   recover `(net, pos_eq, pos_bd, scale)` — the `scale` series is the
   input to the funding-cost calc.
3. **Apply funding-cost subtraction**: per-bar `fc[t] = max(scale[t]
   − 1.0, 0.0) × r_Tbill[t]`. The `max(·, 0)` clause ensures we don't
   *credit* the portfolio when under-levered (conservative; matches
   NTSX prospectus treatment that fees are asymmetric). Store
   `net_post_cost = net − fc`.
4. **Recompute gates** on `net_post_cost`:
   - G1 PBO: N=1 vacuous PASS (same as iter 016).
   - G2 DSR: computed on post-cost Sharpe with cumulative_n_trials =
     4264 (unchanged).
   - G3 Walk-Forward: 8 rolling windows, MDD < 25 % per window on
     post-cost series.
   - G4 OOS 70/30: split, compute OOS Sharpe on post-cost.
   - G5 FWD post-2020: slice post-2020-01-01 bars, Sharpe.
   - G6 Bootstrap 99.9 % CI low: stationary block bootstrap on
     post-cost returns.
   - G7 Cross-lib: pandas engine's post-cost series vs numpy
     reference's post-cost series; ±3 pp CAGR.
5. **Score using `scoring.py`**: call `score_strategy` with the
   post-cost metrics. Compare criterion-by-criterion to iter 016's
   79/100.
6. **Final report**: explicit table of `pre_cost vs post_cost` per
   dataset for Sharpe, CAGR, MDD, DSR p, gates; main lesson one
   paragraph; updates to BASE_MEMORY's deployability notes.

### Key numerical expectations (pre-commit for sanity)

Given iter 016's `scale_mean` roughly 1.35 on edu / 1.60 on spy / 1.70
on ndx (estimated from iter 016 log; to be verified at runtime) and
period-mean T-bill rates of ~2.0 % / 1.5 % / 1.5 %, expected daily-mean
funding cost per bar:

- **educational**: `(1.35 − 1.0) × 0.02 / 252 ≈ 2.78 × 10⁻⁵`
  (2.78 bps/day on notional) → annual drag ≈ 0.7 %.
- **spy_real**:   `(1.60 − 1.0) × 0.015 / 252 ≈ 3.57 × 10⁻⁵`
  (annual drag ≈ 0.9 %).
- **ndx_real**:   `(1.70 − 1.0) × 0.015 / 252 ≈ 4.17 × 10⁻⁵`
  (annual drag ≈ 1.05 %).

Expected Sharpe damage given ~15 % annualised portfolio vol:
~0.7/0.9/1.05 ÷ 15 ≈ **−0.047 / −0.060 / −0.070**.

**Expected post-cost Sharpes**: edu 0.98 − 0.047 ≈ 0.93 (vs bench 0.68,
edge +0.25 ✓); spy 1.14 − 0.060 ≈ 1.08 (vs 0.90, edge +0.18 ✓);
ndx 1.19 − 0.070 ≈ 1.12 (vs 0.955, edge +0.165 ✓). All 3 still clear
+0.10 strict gate under these priors, suggesting hypothesis should
**confirm**. Falsification would require actual drag > 2× pre-commit
estimate — possible if the 2022 rate-hike regime (SHV returns peaking
5 %+) dominates the average in our ~3 high-rate years.

### Why this iteration counts as "structurally novel" per PROMPT hard rule

- **New data input** (SHV → `r_Tbill`) never used in a hunt-loop iteration
  before; the macro cache uses T10Y3M (rate *spread*, not level) and VIX,
  neither of which captures financing cost.
- **New transformation** (per-bar subtraction of levered-cost series) not
  performed by any prior wrapper; iter 016's `net` stream was assumed
  cost-complete, iter 017's was identical.
- **Different outcome semantics**: this iteration cannot "break" iter
  016's mechanism — it can only reveal the mechanism's realistic edge.
  So the kill criteria are calibrated to REALISM thresholds (+0.10
  gate still clearable) rather than MECHANISM thresholds (winner
  conditions 4/5). The dead-end classification this iteration can
  produce is a *deployability* one: "synthetic-NTSX vol-targeted stack
  reproduces only 0.06 Sharpe edge post-funding, below +0.10 gate on
  2/3 datasets ⇒ deploy only via **real** NTSX ETF whose expense ratio
  capture is subsumed in the 0.20 % ER" — this is a distinct failure
  mode from the "mechanism cointegrates" family (iter 009/012/013/014).
