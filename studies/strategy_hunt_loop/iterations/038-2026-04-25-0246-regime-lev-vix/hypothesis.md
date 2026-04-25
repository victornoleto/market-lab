# Iteration 038 — VIX-regime-gated leverage on iter 037's 3-leg static stack

## Hypothesis

Iter 037 is the loop's static-stack ceiling at **STRONG 79** (Sharpe
0.98/1.15/1.17, MDD clear, **DSR worst-p 0.222** — 1pp above the 0.20
Kill-C threshold). The single binding gap to a winner is **DSR**: at
n_trials = 4300, DSR p < 0.05 requires Sharpe ≈ 1.30 cross-dataset.
Static-stack architectures cannot deliver +0.13-0.32 Sharpe at preserved
1.5× without breaching MDD (iter 036 demonstrated: 1.8× breaks ndx MDD).

Moreira & Muir (*JF* 2017, vol. 72(4): 1611-1644, DOI
10.1111/jofi.12513) prove that vol-managed factor portfolios deliver
**unconditional Sharpe uplift of +0.20-0.30 vs the buy-and-hold base**
even when average exposure is held constant — the mechanism is *timing*
(concentrating exposure in low-vol regimes where the Sharpe ratio is
mechanically higher). Their Table IV reports +0.27 unconditional Sharpe
uplift for SPY-vol-managed at near-1× average exposure.

Iter 038 applies a **binary VIX-level regime gate** to iter 037's
0.60 SPY + 0.45 IEF + 0.45 GLD weights:

- **Low-vol regime** (VIX_{t−1} < 20): scale all 3 legs by 1.7/1.5 →
  positions become 0.68 / 0.51 / 0.51, total leverage 1.70×
- **High-vol regime** (VIX_{t−1} ≥ 20): scale all 3 legs by 1.0/1.5 →
  positions become 0.40 / 0.30 / 0.30, total leverage 1.00×

The weight ratios within iter 037's 4:3:3 (eq:bd:gld) are preserved —
this is a pure regime-conditional total-leverage modulation, NOT a
weight-mix change.

**Key sanity check**: VIX<20 fraction is empirically 67-71% across the
3 datasets, so average leverage settles at ≈ 1.47-1.49, **almost
identical to iter 037's 1.50**. Average exposure is held constant; any
Sharpe uplift comes purely from regime timing per Moreira-Muir 2017,
not from increased risk-taking.

## Primary citation

`[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching
state inference; the binary VIX-threshold rule is the simplest
2-state regime classifier and the natural deterministic equivalent of
a 2-state Gaussian HMM on VIX log-levels (Hamilton 1989,
*Econometrica* 57(2): 357-384, DOI 10.2307/1912559; Ang-Bekaert 2002,
*JFE* 63(3): 443-494). The HMM "high-vol" hidden state in standard
fits separates around the VIX 70-75th percentile (≈ 22 historically);
20 is the natural round-number proxy and matches Sinclair's vol-trading
threshold.

## Additional citations

- **Moreira & Muir (2017)**, *JF* 72(4): 1611-1644. DOI
  10.1111/jofi.12513. Vol-managed-factor unconditional Sharpe uplift
  Table IV (the structural mechanism this iteration tests on a
  multi-asset stack).
- `[volatility_trading, p.217-218]` — Sinclair, *Volatility Trading*
  (2nd ed., Wiley 2013). VIX 20 as the natural vol-regime divider.
- `[risk_parity, ch.5]` + `[risk_parity, p.5, p.10-11, ch.1]` —
  Asness-Frazzini-Pedersen (2012), *FAJ* 68(1): 47-59. SSRN 1728082.
  The 3-leg stack base preserved from iter 037.
- `[leverage_for_the_long_run, p.19-20]` — Hsiao-Williams (2017),
  *J. Index Investing*. Leverage on diversified base; 1.7× lo / 1.0×
  hi straddles the 1.5× iter 015/037 sweet spot.
- **Erb & Harvey (2006)**, *FAJ* 62(2): 69-97. DOI 10.2469/faj.v62.n2.4084.
  Gold's strategic role on a levered base (preserved from iter 035/037).
- **Asness-Moskowitz-Pedersen (2013)**, *JF* 68(3): 929-985. DOI
  10.1111/jofi.12021. Cross-asset orthogonality (preserved from iter 037).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (G2).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.

## Edge source

In ONE sentence: SPY buy-and-hold takes constant 1× exposure regardless
of vol regime, missing the Moreira-Muir 2017 result that
unconditional Sharpe rises by +0.20-0.30 when exposure is concentrated
in low-vol regimes — iter 038 captures this by leveraging iter 037's
already-Sharpe-edge-positive 3-leg base 1.7× when VIX < 20 (≈ 67-71% of
bars, close to historical "calm" regime) and de-levering to 1.0× when
VIX ≥ 20 (≈ 30-33% of bars, capturing 2008-Q4, 2020-Q1, 2022).

## Datasets

- **educational** (SPY+IEF+GLD 2004-11-19 → 2026-04-15, GLD-aligned 21y):
  contains the 2008 GFC stress where iter 037's static stack still drew
  down 33% — perfect window to test whether VIX gate avoids the worst
  of the GFC equity leg drag while preserving the bond/gold rally.
- **spy_real** (SPY+IEF+GLD 2009-06-25 → 2026-04-15, post-GFC 17y): the
  loop's frozen-benchmark test. iter 037 hit 1.15 Sharpe; needs +0.15
  to reach the DSR 0.05 threshold.
- **ndx_real** (QQQ+IEF+GLD 2010-02-12 → 2026-04-15, tech-heavy 16y):
  iter 037 hit 1.17 Sharpe with 32% MDD — the gate must not break the
  +0.10 Sharpe edge while reducing tail concentration in the 2022
  rate-spike + tech-selloff dual stress.

## Kill criteria (pre-committed)

A single Kill firing demotes the iteration's interpretation; ≥ 2 firing
forces a structural re-think:

- **Kill A — Sharpe regression vs iter 037**: Sharpe Δ vs iter 037 < −0.05
  on ≥ 2 datasets (regime gate destroys static-stack edge). If fired,
  vol-regime timing on iter 037 base is **not** Sharpe-additive.

- **Kill B — ndx MDD breach**: ndx_real MDD > 35% (regime gate fails
  to protect tail despite having lower hi-regime exposure). The 1.7×
  low-vol weight at 0.68 SPY would amplify intra-regime drawdowns if
  the regime gate fires too late.

- **Kill C — DSR worst-p above 0.10**: the **whole point** of this iter
  is clearing DSR. If worst-p ≥ 0.10 (i.e., does not reach the
  10-pt criterion-3 bucket), the regime gate has not delivered its
  thesis even partially. ≥ 0.20 (no improvement vs iter 037) means
  full failure.

- **Kill D — G7 cross-lib > 3 pp**: engine bug in regime-gated stack
  primitive (must reproduce within numerical tolerance in pure numpy).

- **Kill E — Score < 75**: regression vs iter 037's STRONG 79 baseline.
  At ≥ 2 datasets failing the +0.10 frozen-Sharpe edge, criterion 1
  drops to ≤ 10 pts and total likely falls below 70.

- **Kill F — Robustness < 7/9 sub-windows positive**: regime gate
  introduces sample-period sensitivity; iter 037 had 9/9.

- **Kill G — Regime fraction extreme**: low-vol fraction < 50% or
  > 85% on any dataset, signaling the threshold is mis-calibrated for
  that window. Sanity check, not a strategic kill.

## Expected budget

- Configs to test: **1** (pre-committed binary VIX threshold = 20,
  lev_lo = 1.70, lev_hi = 1.00). NO sweep, NO post-hoc selection. The
  thresholds match Sinclair's published number and the
  iter-037-preserved budget; no degrees of freedom are created.
- Cumulative n_trials advance: 4300 → 4303 (+3, single cfg × 3 datasets).
- Wall-time: ~30-45 min (vendoring iter 037's 3-leg primitive +
  regime mask + cross-lib reference + 6 gates × 3 datasets).
- Files to create:
  - `regime_lev_stack_3leg.py` — pandas engine adding regime mask
  - `numpy_reference_regime_lev_stack_3leg.py` — pure-numpy reference
  - `run_backtests.py` — runner across 3 datasets
  - `compute_gates_and_score.py` — gates + scoring + verdict.json
  - `tests/test_regime_lev_stack.py` — TDD spec for new primitive
  - `results.json`, `verdict.json`, `final_report.md`,
    `plot_vs_benchmark_*.png`

## Implementation plan

1. **TDD-first**: write `tests/test_regime_lev_stack.py` with the
   following invariants:
   - When all bars are low-vol (VIX < 20 always), output equals
     `apply_static_stack_3leg(eq_w=0.68, bd_short_w=0.51, bd_long_w=0.51)`
     within numerical tolerance.
   - When all bars are high-vol (VIX ≥ 20 always), output equals
     `apply_static_stack_3leg(eq_w=0.40, bd_short_w=0.30, bd_long_w=0.30)`.
   - Mixed regime: cost on flip days is non-zero;
     non-flip days within a regime have zero rebalance cost (positions
     are constant within a regime).
   - 1-day signal lag: regime at bar t uses VIX_{t−1}, not VIX_t.
   - Pandas engine and numpy reference produce identical output to
     1e-10.
2. **Implement** `apply_regime_lev_stack_3leg(r_eq, r_bd, r_gld, vix,
   threshold=20.0, lev_lo=1.70, lev_hi=1.00, base_weights=(0.6, 0.45,
   0.45))`. Mechanism:
   - Align the 4 series on the inner-join index of returns ∩ VIX.
   - Compute regime[t] = 1{VIX_{t-1} < threshold}; first bar uses neutral
     scaling (lev = 1.5 / 0.5*(lev_lo+lev_hi)) — to avoid a fictional
     pre-sample regime value (later asserted by test).
   - For each leg: pos[t] = base_w × (lev_lo if regime[t]=1 else lev_hi)
     / (base_weights_sum, here 1.5).
3. **Run on 3 datasets** using iter 037's `load_triple_returns` + a
   VIX loader; align all 4 series.
4. **G7 cross-lib**: numpy reference recomputes net returns; CAGR
   parity ≤ 3 pp.
5. **Score** via `scoring.score_strategy()` + custom edu benchmark
   (matching the GLD-aligned 21y window iter 037 used).
6. **Plot** equity vs SPY/QQQ b&h on spy_real / ndx_real.

The test-first invariants pin the primitive's behavior tightly. The
single pre-committed cfg + n_trials advance of just 3 keeps the DSR
penalty growth minimal — ensuring that *if* Sharpe rises to ≈ 1.30
cross-ds the DSR test will detect the lift.

## Why this is structurally novel vs known dead-ends

- **Iter 028-031 (single-axis VIX gate family CLOSED)** applied VIX
  level / persistence / z-score gates to **iter 026's VRP-primary
  base** (T-bill + short SPY put credit spread). The VRP base has a
  fundamentally different return mechanism (option-premium harvest)
  than iter 037's static-stack (cross-asset risk-parity) — vol gates
  on each base interact with the underlying premium structure in
  qualitatively different ways. The static-stack family has NEVER had
  a VIX regime gate tested.
- **Iter 030 dead-end** specifically closes "single-axis VIX-gate on
  iter 026 base"; iter 037 has a structurally orthogonal premium
  source (multi-asset orthogonality, not VRP).
- The VIX-level threshold of 20 (vs iter 028's 35, iter 029's
  35+persistence, iter 030's z>2σ) targets a different regime
  boundary entirely — iter 028-030 filter the **tail** of vol
  distribution; iter 038 filters the **median** to capture the
  Moreira-Muir Sharpe-uplift mechanism.
- **Iter 022 (calendar TOM modulator)** also tested a regime modulator
  on a vol-managed stack (failed — σ²_port quadratic in w_eq). Iter
  038 differs: (a) regime indicator is exogenous (VIX) not endogenous
  (calendar), (b) base is iter 037 static-stack not vol-managed, (c)
  modulation is on TOTAL leverage not eq:bd ratio.

This iteration tests one structurally new question: does VIX-level
regime timing on a 3-leg static stack at preserved-on-average leverage
deliver Moreira-Muir's Sharpe uplift?
