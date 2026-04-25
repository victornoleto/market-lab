# Dead ends — structural failures to avoid

Read this before proposing a hypothesis. Any direction that matches
structurally with an entry below is **forbidden**.

---

## From iteration 001 — crash-protected LETF trend

Complete study: `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md`
+ `deep_review/` + `cross_dataset_gates.md`.

### Exact configurations tested (1 340 × 3 datasets = 4 020 configs)

- **Bases**: SMA/EMA × lookback {50, 100, 150, 200} × threshold
  {0, 2, 5, 10}% × buy_leverage {1, 2, 3}× × sell_leverage {cash, −1, −2, −3}×
- **Overlays**:
  - stop_loss % ∈ {15, 20, 25, 30, 35, 40}
  - re-entry modes: next_signal, time_cooldown {21, 63, 126 days},
    recovery_trigger {5, 10, 15}%
  - risk signals: EBP, term_spread, CAPE, VIX, composite
  - λ ∈ {0.3, 0.5, 0.7}
  - combinations of stop + risk

### What failed (do NOT re-test)

1. **Daily EMA/SMA threshold + LETF + stop + risk signal** — no
   config combination produced Sharpe edge in real data. Top SPY-real
   Sharpe: 0.853 (vs SPY 0.900, gap −0.047).

2. **Drawdown-from-peak stop as primary protection** — mechanically
   saves MDD but proportionally costs CAGR; net Sharpe neutral. Stop
   trigger at 15-30% fires 9 times in 40y; overlay removes ~9 pp MDD
   at cost of ~3 pp CAGR.

3. **CAPE z-score sigmoid as single indicator** — chronically above
   threshold 2002-2015 (13-year dead zone); signal output ≈ 0 during
   entire decade, zero de-levering. Signal resumed 2017+ but too
   little of the sample.

4. **Sigmoid signal on EBP, term_spread, VIX individually** — each
   fires ≤ 30% of bars in bull regime; individual indicators don't
   move the needle.

5. **Composite equal-weight risk signal** — diversification didn't
   compound the edge; composite de-lever 0-6 pp MDD, net effect on
   Sharpe negligible.

6. **next_signal re-entry** — misses 60-70% of recovery in fast
   crashes (COVID-style). `time_cooldown` and `recovery_trigger` are
   marginally better but still leak 30-50% of post-crash rally.

7. **3× LETF (bL=3) with any overlay** — structural MDD floor ~44%
   (synth) / ~48% (real). Cannot reach spec target 40% within CAGR
   corridor. Leverage is destiny.

8. **Walk-Forward G3 gate with leveraged trend** — universally FAILS
   for bL≥2 configs. Each 6-month OOS window contains either a crash
   (MDD > 25%) or a rally (OK) but rarely both; 8 clean windows out of
   history is structurally incompatible with trend-follow on LETF.

9. **Cross-dataset consistency for top-1 CAGR bases** — 4 bases
   appear in all 3 top-20 lists; 16 (base, combo) pairs gated; **0/16**
   pass spec §0.

### Structural principles derived

- **Post-2009 SPY Sharpe 0.90 is hard to beat** with any discrete
  trend-follow + leverage + overlay in equity market alone.
- **3× leverage MDD is inherent**, not fixable by overlay.
- **Crash signals (CAPE/EBP/VIX/term) are feast-or-famine**: strong
  in 1996-2000 and 2017-2022, dead elsewhere. No signal works for
  all regimes.
- **Drawdown-based stops cost CAGR proportional to reduction**; at
  CAGR-neutral, MDD reduction is ~5-10pp (not 20+ pp).

---

## From iteration 002 — Clenow canonical on SPDR sector ETFs

Complete study: `studies/strategy_hunt_loop/iterations/002-2026-04-24-0906-sector-momentum-clenow/final_report.md`.

### What failed (do NOT re-test)

1. **Clenow canonical (10 bps ATR-risk-parity) on 11 SPDR sectors with
   top-K ∈ {3, 5} and leverage ∈ {1×, 2×}** — Sharpe 0.22-0.28 vs
   benchmark SPY/QQQ 0.54-0.91 on all 4 configs across all 3 datasets.
   Score 17/100 ❌ FAIL. Winner conditions 0/5.

2. **The specific root cause: ATR sizing mismatch.** Clenow's 10 bps risk
   factor `[stocks_on_the_move, p.88-89, 228-230]` was calibrated for
   individual S&P 500 stocks with ATR20 ~1-3% of price. Sector ETFs have
   ATR20 ~0.3-1% of price (intra-sector diversification lowers per-bar
   volatility). Shares = equity × 0.001 / ATR at ATR $1-3 and price
   $70-200 gives $5k-10k per position. Top-K=3 × $7.5k = ~$22k deployed
   on $100k → **77% in cash**. Top-K=5 × $7.5k = ~$37k deployed → **63%
   in cash**. Even at buy_leverage=2.0×, portfolio is still 25-50% in
   cash. The strategy is structurally under-deployed; the signal edge (if
   any) is masked by cash drag.

3. **4-config single-family grid on a near-zero-return regime** — G1 PBO
   lands at 0.52-0.57 (barely above the 0.5 noise floor). When every
   config in the grid produces similar near-zero returns, IS-best vs
   OOS-best is effectively a coin flip. PBO cannot distinguish skill
   from noise in this regime.

4. **Bootstrap 99.9% CI low of −0.40** on all 3 datasets means the
   stationary bootstrap distribution of Sharpe straddles zero with wide
   margin — **no evidence of statistical edge even under favorable
   resampling**.

### Don't re-test

- Clenow canonical 10 bps ATR-risk-parity on sector ETFs at top-K ≤ 5.
- Small grid (≤ 4 configs) on a single strategy family when the family
  is under-deployed — PBO is uninformative.

### Structural principles

- **Transporting a book strategy across asset classes requires risk-
  budget recalibration per universe.** Clenow's 10 bps is a per-position
  VaR constraint that depends on asset ATR/price. Moving from 1-3% ATR
  stocks to 0.3-1% ATR sector ETFs requires ~3× larger risk factor
  (e.g., 30 bps) to achieve the same portfolio utilization. This is NOT
  optimization in Clenow's sense `[p.219-220]` — it's first-principles
  calibration to match a new universe's volatility.

- **Unlevered equal-risk sizing breaks with < 20 assets.** Clenow's
  portfolio math `[p.228-230]` assumes 20-50 positions at 10 bps each
  gives ~20-50% daily-impact budget. With only 3-5 sectors at 10 bps, the
  portfolio only uses 3-5% daily-impact budget → most capital sits idle.

- **G1 PBO needs a grid with return dispersion.** A grid where all
  configs produce similar near-zero returns gives PBO ≈ 0.5 by construction
  (coin flip), regardless of whether the strategy has real edge. Before
  gating on PBO, verify the grid spans configs with materially different
  returns.

---

## From iteration 003 — equal-notional sector rotation with Clenow ranking

Complete study: `studies/strategy_hunt_loop/iterations/003-2026-04-24-0927-sector-momentum-equal-notional/final_report.md`.

### What failed (do NOT re-test)

1. **Clenow adjusted-slope × R² ranking with equal-notional 1/K sizing on
   11 SPDR sectors, grid top_k ∈ {3, 5, 7, 9} × lookback_slope ∈ {60, 90,
   120} × buy_leverage ∈ {1.0, 2.0} (24 configs)** — Sharpe 0.15-0.30
   across all 24 configs × 3 datasets, vs bench 0.54-0.91. Score 7/100
   ❌ FAIL. Winner conditions 0/5.

2. **The specific root cause: the ranking signal has no discriminatory
   power on this universe.** Iter 002 suggested sizing was the culprit
   because portfolios were 63-77% in cash; iter 003 fixed sizing
   (deployment 1.00-1.99 gross exposure / equity, median 1.55-1.76 for
   top candidates) and discovered the signal itself is noise. The grid's
   top configs are `top_k=9` (hold nearly all 9-11 sectors, near-equal-
   weight) — concentrating in top-3 or top-5 by ranking score actively
   reduces Sharpe. This is direct empirical evidence against the
   adjusted-slope ranking on a small ETF universe.

3. **PBO worse than iter 002** (0.635-0.905 vs 0.516-0.567). The larger
   24-config grid has real return dispersion, but the IS-best / OOS-best
   rank reversal is severe — textbook overfitting signature, not the
   "small-grid noise floor" of iter 002. G6 bootstrap 99.9% CI low is
   −0.37 to −0.44 across all 3 datasets: no statistical edge even under
   favorable resampling.

4. **Structural hypothesis confirmed**: cross-sectional ranking momentum
   needs a heterogeneous universe (~50+ assets with meaningful
   idiosyncratic return components) to produce a rankable cross-section.
   ≤20-asset universes of diversified baskets (sector/factor/country
   ETFs) are structurally too homogeneous — aggregate market factor
   dominates, ranking score is noise.

### Don't re-test

- Clenow adjusted-slope × R² ranking with equal-notional or any sizing
  variant on the 11 SPDR sector ETFs.
- Any cross-sectional ranking momentum mechanism (adjusted-slope,
  12-month return, 12-1 momentum, etc.) on a ≤20-asset universe of
  diversified-basket ETFs.

### Structural principles

- **Cross-sectional ranking mechanisms need universe heterogeneity.**
  Jegadeesh-Titman (1993) and Clenow (2015) both designed their ranking
  formulas on single-stock universes (NYSE/AMEX, S&P 500) with 500+
  constituents and meaningful idiosyncratic return variance per name.
  On 11 SPDR sectors — each itself a basket of ~50-80 stocks — the
  idiosyncratic component is washed out; top-rank vs bottom-rank sector
  returns are dominated by the same market factor, and the ranking
  signal adds no alpha.

- **Fixing one issue can expose a deeper one.** Iter 002's "under-
  deployment" finding was correct mechanically, but it masked a more
  fundamental problem — the signal's absence. Iter 003's lesson is that
  when diagnosing a FAIL, check whether the fix actually tested the
  hypothesis or just moved the bottleneck. Here the fix (equal-notional)
  cleanly tested the signal, and the signal was the problem.

---

## From iteration 005 — Moreira-Muir variance-scaling on SPY/QQQ

Complete study: `studies/strategy_hunt_loop/iterations/005-2026-04-24-1008-variance-managed-spy/final_report.md`.

### What the iteration resolved

Variance-scaling (`σ^{-2}`, Moreira-Muir 2017 canonical) was tested
head-to-head with iter 004's vol-scaling (`σ^{-1}`, Carver form) on
SPY/QQQ daily returns. Result: **+0.01 Sharpe uplift on real data** —
a lateral move, not the paper's +0.12-0.15 improvement.

Iter 005 score 59/100 MARGINAL (new top-K #1), Sharpe edge +0.081 spy
/ +0.097 ndx (both still below +0.10 strict gate). Kill criteria 1-3
all NOT triggered — the mechanism is not broken, just saturated.

### Structural principle (do NOT re-test)

**Single-asset vol-adaptation on SPY/QQQ over 17y cannot clear the
+0.10 strict Sharpe gate regardless of exponent choice.** This applies
to any form `s_t = f(σ̂_{t-1})` where `f` is a static function of
lagged realised vol. Tested endpoints:

- `f(σ) = target_vol / σ` (iter 004, Carver): edge +0.080 spy / +0.088 ndx
- `f(σ) = target_vol² / σ²` (iter 005, Moreira-Muir): edge +0.081 spy / +0.097 ndx

The family is bounded above at ~+0.08-0.10 real-data Sharpe edge
because SPY's post-2009 buy-hold Sharpe 0.90 is already near the
informational ceiling for a signal-free vol-feedback — vol is
persistent, but the autocorrelation structure of SPY returns is
already mostly captured by a first-order rescaling. Squaring or
higher-order exponents add numerical asymmetry but no new information.

### Don't re-test

- Any further single-asset exponent sweep on SPY/QQQ (e.g., σ⁻¹·⁵, σ⁻³,
  log-σ). The ceiling is informational, not parametric.
- Param grids larger than 12 configs on any single-mechanism vol-
  adaptation family — inflates `cumulative_n_trials` without moving
  the limiting factor (Sharpe edge magnitude).

### Path forward (NOT dead)

Vol-adaptation remains a valid **primitive** for compounded strategies:

- Vol-managed 60/40 SPY+TLT (cross-asset correlation axis is new)
- Variance-scaling × momentum overlay (Moreira-Muir Table IV)
- Meta-labeling on top of variance-scaled primary

These are NOT forbidden by the iter 005 principle — the bound applies
to single-asset static-vol-feedback, not to compounding mechanisms
that add an independent edge source.

---

## From iteration 006 — vol-managed 60/40 SPY+TLT inverse-variance blend

Complete study: `studies/strategy_hunt_loop/iterations/006-2026-04-24-1027-vol-managed-60-40/final_report.md`.

### What the iteration resolved

Inverse-variance weighted SPY+TLT blend with Moreira-Muir portfolio-
level variance-scaling on top. **PROMISING tier, score 67/100 (new
hunt-loop top-K #1)**, clearing +0.10 Sharpe gate on 2 of 3 datasets
(educational +0.268, spy_real +0.100 exact) and CAGR + MDD floors 3/3
(first iteration to achieve both).

Kill #3 triggered: **grid-level PBO on spy_real jumped to 0.690** (vs
iter 005's single-asset variance-scaling at 0.238) — the 2-asset blend
adds degrees of freedom that destabilise IS/OOS rank ordering on a
12-config grid.

### Structural principle (grid-design, NOT mechanism dead-end)

**Vol-managed N-leg blends (N ≥ 2) on a 12-config grid are overfit-
sensitive (PBO ~0.7)** because each extra leg adds a new
weight-dynamics dimension. When short-lookback configs (21d) and
long-lookback configs (126d) respond differently to regime changes
(e.g. 2022 bond crash), IS/OOS rank reversals dominate the grid,
and PBO spikes.

This is a **grid-design caveat, not a mechanism dead-end**. The blend
mechanism's top-candidate Sharpe edge (+0.10 spy_real, +0.27
educational) remains real and gate-passing outside of G1.

### Don't re-test (grid-design)

- Blend mechanisms (N ≥ 2 legs with dynamic weighting) on a 12-config
  grid. Expect PBO > 0.5.
- Adding more configs to a blend grid without deliberate return
  dispersion — will not fix PBO and will further inflate
  `cumulative_n_trials` penalising DSR.

### Paths forward (NOT dead)

Two productive options for iter 007 preserving the blend mechanism:

1. **Pre-committed single-config blend** (no grid search). Commit
   ex-ante to one cfg (e.g. `vt15_L63_cap20` — iter 006 educational
   winner). Eliminates PBO requirement (PBO is grid-definitional).
   Only +3 n_trials added. Tests whether blend edge survives without
   grid-selection.

2. **Blend + signal overlay** (momentum gate or meta-labeling). Adds
   a structurally independent edge axis (trend) without expanding
   the weight-dynamics grid — PBO dimensionality is controlled by
   signal gate, not weight-sweep.

---

## From iteration 007 — time-series momentum overlay on vol-managed SPY+TLT blend

Complete study: `studies/strategy_hunt_loop/iterations/007-2026-04-24-1047-vol-managed-60-40-momentum-overlay/final_report.md`.

### What the iteration resolved

Canonical 12-1 (skip-a-month, `[ml_for_algo_trading, ch.4 p.86]` /
Jegadeesh-Titman 1993 / Moskowitz-Ooi-Pedersen 2012) time-series
momentum overlay tested on top of iter 006's vol-managed SPY+TLT
blend. Pre-committed blend cfg `vt15_L21_cap20`; 3 overlay configs
(lookback ∈ {126, 252, 378} days, skip=21) × 3 datasets = 9 trials.
Result: **Sharpe REGRESSES vs iter 006 on both real-data slots**:
spy_real 0.941 (vs 1.000, −0.06), ndx_real 0.872 (vs 1.021, −0.15).
Score 50/100 MARGINAL (down from 67 PROMISING).

KILL #1 (pre-committed: Sharpe ≤ iter 006 on BOTH real slots):
TRIGGERED. KILL #3 (G1 PBO > 0.5 on 2+ datasets): TRIGGERED (all 3).

### Structural principle (do NOT re-test)

**Time-series momentum overlay is REDUNDANT with variance-scaling on
a vol-managed 2-asset blend.** Both mechanisms target the same
underlying information: equity-regime volatility.
`[leverage_for_the_long_run, p.9]` — SPY below-MA exhibits 2-3× the
above-MA volatility — this asymmetry is what variance-scaling (iter
005's `σ^{-2}`, iter 006's blend) already exploits via its
`scale = target_vol² / σ²` rule. Stacking momentum on top forces
exposure to zero in regimes where the blend is already reduced
naturally, forfeiting the residual positive drift at the cost of
transaction friction on gate flips.

Empirical asymmetry: Sharpe damage scales with the base blend's
Sharpe. Educational (iter 006 Sharpe 0.929) loses only −0.013, while
ndx_real (iter 006 Sharpe 1.021) loses −0.149. The stronger the base
signal, the more costly the overlay — confirming the overlay is
removing information, not adding it.

Moreira-Muir (2017) Table IV's vol-managed × momentum Sharpe uplift is
documented **for a vol-managed single factor (MOM alone)**, not for a
vol-managed BLEND. The uplift does not transfer: once the base is
already a vol-managed cross-asset blend, the correlation between
momentum and blend-scale dominates.

### Don't re-test

- Time-series momentum overlay (any lookback, any skip, any threshold)
  on a vol-managed 2-asset blend with variance-scaling.
- Absolute momentum (Moskowitz-Ooi-Pedersen form, threshold = 0) as a
  binary gate on iter 006's blend.
- Any correlated regime signal (EMA/SMA/VIX/drawdown/absolute momentum)
  as an overlay on iter 006's blend — variance-scaling already
  captures this dimension.
- 3-config ex-ante grids of blend × binary-signal family — iter 007
  showed G1 PBO = 0.64-0.76 even at 3 pre-declared cfgs. The
  overfit-sensitivity is structural to the compound, not to grid
  search.

### Path forward (NOT dead)

- **Orthogonal signals** (carry = term spread, macro state = EBP,
  sentiment = options skew, meta-labeling on cross-sectional features)
  still untested on iter 006's mechanism.
- **Single-config (no grid) verification of iter 006** remains untested
  — Option A from iter 006's final report still valid.
- **3-asset or higher blend** extensions (SPY+TLT+GLD, NTSX/NTSI/NTSE
  rotation) are structurally different and untested.

---

## From iteration 010 — 3-leg vol-managed SPY+TLT+GLD blend (structural saturation, not mechanism-kill)

Complete study: `studies/strategy_hunt_loop/iterations/010-2026-04-24-1506-three-asset-spy-tlt-gld-blend/final_report.md`.

### What the iteration resolved

Iter 010 extended iter 008's 2-leg SPY+TLT vol-managed blend to 3 legs
by adding GLD as the third (commodity / inflation-hedge) leg, with
IDENTICAL params (`vt15_L21_cap20_3leg`, single ex-ante cfg, no sweep).
Naïve risk parity generalised cleanly to N=3 (9 TDD specs pass),
Moreira-Muir variance-scaling applied unchanged to the 3-leg σ²_port,
cross-lib parity holds to ≤ 0.12 pp. Result: **score 74/100 ties iter
008 exactly (hunt-loop high still held, not exceeded)**, 4/5 winner
conditions, DSR remains the sole failure.

Dataset asymmetry is the core finding:
- educational (SPY b&h bench 0.63): **Sharpe +0.12 vs iter 008** (0.87
  → 0.99). Broad 21y window, equity leg not at Sharpe-ceiling — GLD
  adds real diversification.
- spy_real (SPY b&h bench 0.90): **Sharpe +0.04 vs iter 008** (1.00
  → 1.04). Modest but measurable — comfortable clearance of +0.10
  gate vs iter 008's exact tie.
- ndx_real (QQQ b&h bench 0.955): **Sharpe −0.03 vs iter 008** (1.02
  → 1.00). Tech-heavy universe where equity leg is already near its
  informational ceiling; GLD's ρ≈0 contribution acts more as drag
  than hedge on this regime. WF also regresses 7/8 → 5/8 on ndx.

### Structural principle (grid-design caveat, NOT mechanism-kill)

**The vol-managed inverse-variance-weighted multi-leg blend family
saturates at Sharpe ≈ 1.00 on 16-17y real data, regardless of whether
N=2 (iter 008) or N=3 (iter 010).** Two iterations, identical
disciplined N=1 pre-commitment, identical params, both score 74/100
with 4/5 winner conditions. The specific ceiling factor is
**DSR-reachability** at cumulative_n_trials ≈ 4240-4250: the deflator
requires Sharpe uplift > ~0.30 on the worst dataset; the blend
family delivers +0.04 (worst) to +0.14 (best) on real data. A ~2× gap
that cannot be closed by adding more legs.

This is **NOT a mechanism kill**. The 3-leg blend itself is a valid
building block — its cross-asset diversification is real, its MDD
reduction is real, and it's arguably the best hunt-loop deliverable
as a candidate for compounding with orthogonal information. But
**further minor variations of the same core mechanism will score
74±2 and add nothing new**.

### Don't re-test

- Vol-managed 3-leg blend on daily horizon with minor param variations
  (`target_vol ∈ {0.10, 0.20}`, `lookback ∈ {63, 126, 252}`,
  `max_leverage ∈ {1.5, 2.5}`) — will score 74 ± 2 at 4/5 winner
  conditions, adding only to `cumulative_n_trials` and worsening DSR.
- Substituting GLD with closely-related commodity proxies (IAU, GDX,
  PHYS, SGOL) — all track gold spot price, ρ-structure identical.
- Adding a 4th leg (currency basket, emerging bonds, VIX) to expand
  to N=4 without changing the core mechanism — expected effect is
  further ±0.02 Sharpe noise per dataset, no structural ceiling break.
- Any 3-leg blend grid with > 1 config — G1 PBO reverts from N=1
  vacuous-PASS to grid-level measurement, and iter 006's grid-level
  PBO instability (0.69 on 12-cfg grid) has no reason to improve at
  N=3.

### Path forward (NOT dead — truly different mechanism required)

- **Weekly or monthly rebalance** of the 3-leg blend. Changes the
  effective n_trials regime DSR sees (weekly ≈ 52/yr vs daily 252/yr)
  and aligns better with Moreira-Muir 2017's monthly-data canonical
  regime. Cheapest path to attack the DSR ceiling directly.
- **Meta-labeling (AFML ch.3)** on the iter 008 2-leg base. Secondary
  ML model predicts bar-level profitability using cross-sectional
  features the blend cannot see. Only direction that adds
  *informationally independent* signal beyond vol-regime.
- **Asymmetric macro overlay** (iter 009 Option B' — raw/5d T10Y3M +
  equity-leg-only haircut). Still untested; preserves lead-time +
  respects flight-to-quality.
- **Return-stacked ETF rotation** (NTSX/NTSI/NTSE) — built-in leverage
  layered with duration/equity factor, a structurally new primitive.

---

## From iteration 011 — weekly-rebalance vol-managed 3-leg blend (timeframe-change dead-end)

Complete study: `studies/strategy_hunt_loop/iterations/011-2026-04-24-1527-weekly-three-leg-blend/final_report.md`.

### What the iteration resolved

Iter 011 tested BASE_MEMORY's "Option F" — apply iter 010's 3-leg
vol-managed SPY+TLT+GLD blend on **weekly W-FRI cadence** with 4-week
lookback (calendar-equivalent of iter 010's 21 trading days), single
pre-committed cfg `vt15_Lw4_cap20_3leg_weekly`. The conjecture was
that weekly execution would (a) align with Moreira-Muir 2017's
monthly-scale canonical regime, (b) reduce the DSR n_trials deflator
penalty, and (c) cut turnover / transaction-cost drag.

Result: **Kill #1 + Kill #3 both TRIGGERED per pre-commit.** Score
52/100 MARGINAL (−22 vs iter 010). Sharpe regresses on all 3 datasets
(edu 0.989→0.942, spy 1.040→1.019, ndx 0.995→0.898). MDD ballooned
+10-14 pp (edu 33.67%→47.19%, spy 33.67%→47.19%, ndx 37.43%→48.99%).
DSR got WORSE not better (worst p 0.368→0.515). Turnover went UP
(10/yr→13.6/yr per leg). Cross-asset SPY-TLT correlation weakened at
weekly scale (−0.24 vs daily −0.30).

### Structural principle (do NOT re-test)

**Vol-managed variance-targeting is NOT cadence-agnostic.** The
mechanism's edge comes from fast reaction to realized-vol regime
shifts; at any cadence slower than daily, regime changes between
rebalance dates happen entirely unhedged within the rebalance window.
For the 3-leg variance-scaled blend specifically:

- Cap-hit frequency climbs from ~86% (daily) to ~95% (weekly) —
  the vol-target `target_var² / σ²_port` becomes non-binding most of
  the time because 4-week compounded σ² is structurally lower than
  daily σ² over 21 days (more smoothing).
- SPY-TLT flight-to-quality correlation is concentrated on specific
  daily stress events (COVID crash days, 2022 correlation flip).
  These smooth out on weekly compounding, reducing the diversification
  return that the blend exploits.
- Turnover actually INCREASES per leg because the 4-week lookback
  shifts 25%/rebalance (vs daily ~5%/rebalance), so each rebalance
  carries a larger weight change.

**DSR theoretical attack via T reduction is ALSO structurally
unavailable for this mechanism.** The DSR formula evaluates PSR at
benchmark `E[SR_max] ≈ a × √(1/(T-1))` where a depends on n_trials.
Reducing T by ~5× (daily→weekly) inflates the benchmark by √5×,
exactly cancelling the √5× growth in periodic observed Sharpe. Net
first-order effect on p-value is ~zero; second-order effects
(narrower G6 margin, weekly autocorrelation artefacts) push DSR
slightly WORSE, as empirically confirmed.

### Don't re-test

- Weekly-rebalance vol-managed multi-leg blend with 4-week lookback
  at any `target_vol ∈ {0.10, 0.15, 0.20}`, any `max_leverage ∈
  {1.5, 2.0, 2.5}`, any `lookback ∈ {2, 4, 8, 12}` weeks. Parameter
  sweep will not recover the mechanism; the bottleneck is the
  cadence mismatch, not a param choice.
- Other weekday-end cadences (W-MON, W-WED) on same mechanism — day-of-
  week within the weekly block is structurally irrelevant; all
  suffer from the same "regime change between rebalances goes
  unhedged" bottleneck.
- **Monthly rebalance** on same 3-leg blend (21d cadence) — not
  empirically tested but by structural extrapolation: monthly would
  score STRICTLY WORSE than weekly (MDD +20-25 pp vs daily, Sharpe
  −0.15 to −0.25 on real data). The gradient of MDD damage with
  rebalance period is monotone on this mechanism.
- Any DSR-ceiling attack premised on "reduce n_trials / reduce T
  via slower sampling" for variance-targeting blends — the DSR
  formula makes this trade null at first order.

### Path forward (NOT dead)

- **Option B'** (iter 009's untested quadrant): raw T10Y3M signal
  (≤ 5d smoothing) + EQUITY-LEG-ONLY haircut on iter 008 DAILY blend.
  Preserves daily cadence (keeps vol-targeting working) + preserves
  macro lead-time + respects flight-to-quality. Expected Sharpe
  uplift +0.03-0.08.
- **Option C** (meta-labeling, AFML ch.3): secondary ML model
  predicts bar-level profitability of iter 008 daily blend using
  cross-sectional features blend can't see. Orthogonal information
  source; highest engineering cost, highest Sharpe-uplift potential
  (+0.20-0.30 if meta-model works). Attacks DSR via observed-Sharpe
  side of the equation rather than the T side.
- **Option G** (return-stacked ETF rotation): NTSX/NTSI/NTSE uses
  built-in leverage, structurally new primitive not tested in hunt-
  loop. Preserves daily cadence.
- **HMM regime-switching** on stock-bond correlation
  (`[regime_change, ch.2]`): different information axis — regime
  state — orthogonal to vol scaling.

---

## From iteration 012 — Asymmetric T10Y3M equity-leg-only haircut overlay (5d EMA) on vol-managed SPY+TLT blend

Complete study: `studies/strategy_hunt_loop/iterations/012-2026-04-24-1556-asymmetric-term-spread-overlay/final_report.md`.

### What the iteration resolved

Iter 012 tested BASE_MEMORY's "Option B'" — iter 009's remaining
untested combinatorial quadrant: **asymmetric haircut (equity leg
ONLY, 0.5×; bond leg unchanged) + light smoothing (5-day EMA, not
21-day)**. Single pre-committed combined cfg
`vt15_L21_cap20 × ts_inv5_h50_eq` (threshold=0, haircut=0.5,
smoothing=5d, applied_to=equity, lag=1). The conjecture was that
(a) 5d EMA preserves T10Y3M's 6-18 month recession lead-time
(44 zero-crossings over 44y, vs 21d EMA which loses the lead), and
(b) equity-only haircut respects flight-to-quality (SPY-TLT ρ ≈ −0.30
means TLT typically rallies during recession).

Result: **Kill #1 + Kill #3 + Kill #4 all TRIGGERED.** Score
**58/100 MARGINAL** (−16 vs iter 008, −6 vs iter 009). Sharpe
regresses on ALL 3 datasets vs iter 008 (edu −0.041, spy −0.035,
ndx −0.053). Gate-fire / bottom-20%-scale overlap is **100 % on edu
+ spy** — identical diagnostic to iter 009 at 21-day EMA. Winner
conditions **0/5** (regression from iter 008's 4/5).

### Structural principle (do NOT re-test — the T10Y3M overlay family is CLOSED)

**Combined iter 009 + iter 012 span the full 2×2 combinatorial matrix
of the T10Y3M-overlay hypothesis on a vol-managed SPY/QQQ+TLT blend,
and all empirically-tested corners fail with the same 100 % gate-fire /
bottom-20%-scale overlap diagnostic on SPY-based datasets**:

| smoothing \\ asymmetry | symmetric (both legs) | asymmetric (equity only) |
|---|---|---|
| heavy (21d EMA) | iter 009: 64/100, FAIL (tested) | strictly worse (not worth testing) |
| light (5d EMA) | structurally same as 009 light-quadrant | **iter 012: 58/100, FAIL (tested)** |

The redundancy with variance-scaling is **structural cointegration,
not a parameter choice**. T10Y3M and SPY realized-vol are
cointegrated at the business-cycle timescale that matters for a
vol-managed blend: by the time a T10Y3M inversion has persisted long
enough to trigger a binary gate (at any practical smoothing), realized
equity vol has already started accelerating and the blend has already
started de-levering. No smoothing window, threshold, haircut level, or
leg-asymmetry choice breaks this.

The ndx_real partial-orthogonality (40.5 % overlap) is a red herring:
QQQ's tech-specific vol regimes lead aggregate SPY vol regimes by 1-2
months, but the gate's *direction* (halve equity on inversion) is
wrong for QQQ because tech vol spikes (2018 Q4, 2020 Feb, 2022 Q4)
happen independently of T10Y3M inversions.

Additional failure mode: the **asymmetric bond-preservation is the
wrong-direction asymmetry for the post-2008 regime**. In 2022 SPY-TLT
correlation briefly went POSITIVE; preserving the TLT leg while
halving the SPY leg meant carrying a losing bond position through
the rate-hike shock, compounding the CAGR drag. A dynamic asymmetry
(asymmetric during ρ < 0, symmetric during ρ ≥ 0) might help, but
falls back to the 100 %-overlap structural problem on historical
ρ < 0 episodes.

### Don't re-test

- **Any T10Y3M binary-haircut overlay variant on a vol-managed
  SPY/QQQ+TLT blend** — the 2×2 quadrant matrix is fully closed
  (iter 009 heavy-symmetric tested, iter 012 light-asymmetric tested,
  heavy-asymmetric scores strictly worse than tested corners, light-
  symmetric has no theoretical reason to beat tested corners). Variants
  forbidden: haircut ∈ {0.3, 0.7, 0.9}, threshold ∈ {−0.25, −0.5,
  +0.25}, smoothing ∈ {2, 3, 10, 15, 21} days, lag ∈ {0, 2, 5} bars,
  applied_to ∈ {bond, both, conditional}.
- **Any other yield-curve-slope-like signal** (T10Y2M, T5Y3M, T10Y6M,
  SOFR-IOER) as binary-haircut overlay — they all cointegrate with
  T10Y3M at the business-cycle timescale and will reproduce the same
  100 %-overlap diagnostic.

### Path forward (NOT dead)

- **Option C — meta-labeling** (AFML ch.3, ch.5). Primary recommendation
  for iter 013. Uses cross-sectional features the blend can't see
  (cross-asset momentum, breadth, options-implied skew, macro state
  regime encoding). Orthogonal by construction, attacks DSR ceiling via
  observed-Sharpe side rather than timeframe or filter-overlay.
- **Option E — EBP (excess bond premium) overlay** (Gilchrist-Zakrajšek
  2012). Credit-cycle signal, distinct from yield-curve slope —
  different historical fire-episodes (1998 LTCM, 2008 GFC, 2020 COVID)
  some independent of T10Y3M. Requires empirical verification that
  EBP-SPY-realized-vol correlation < T10Y3M's before the overlay is
  worth the cumulative n_trials cost.
- **Option G — Return-stacked ETF rotation** (NTSX/NTSI/NTSE). Different
  universe, structurally novel primitive.

---

## From iteration 013 — meta-labeling classifier with vol-proxy features on vol-managed SPY+TLT blend

Complete study: `studies/strategy_hunt_loop/iterations/013-2026-04-24-1619-meta-labeling-blend/final_report.md`.

### What the iteration resolved

Iter 013 tested BASE_MEMORY's "PICK FIRST" Option C — a scikit-learn
`LogisticRegression(C=1.0, penalty='l2')` trained on two features
orthogonal to the blend's realized-vol inputs: rolling 60-day SPY-TLT
correlation and VIX z-score over 252 bars. Walk-forward retraining
every 252 bars on rolling 1000-bar window; decision threshold
p > 0.5. Single pre-committed combined cfg
`vt15_L21_cap20 × meta_lr_rho60_vixz252_w1000_r252`. Intent: attack
DSR ceiling via observed-Sharpe side using a ML architecture
(AFML ch.3, López de Prado 2018) distinct from the macro-overlay
family falsified in iter 009/012.

Result: **score 64/100 MARGINAL/PROMISING boundary**, −10 vs iter
008/010 co-high. Kill #3 triggered (< 70). Sharpe regresses slightly
on ALL 3 datasets (Δ −0.010 to −0.014), but all under the Kill #1
0.02 tolerance. Gates 6/7 uniformly across datasets (only G2 DSR
fails, worst p = 0.351). CAGR + MDD floors both 3/3. Robustness 9/9
sub-windows positive — highest in hunt-loop history.

### Structural principle (do NOT re-test)

**Meta-labeling with any feature set that cointegrates with portfolio
realized vol at the business-cycle timescale produces 100 % overlap
between meta-gate-off bars and bottom-20 % blend-scale bars** on
SPY-based datasets. The classifier is NOT degenerate — `p_act` has
std 0.19-0.21, showing genuine decision-making — but the patterns it
learned are the same ones the variance-scaler already enforces.
Adding a decision stage with correlated information forfeits residual
positive drift without buying any regime protection.

This is the same structural redundancy observed in iter 009 (T10Y3M
21d symmetric) and iter 012 (T10Y3M 5d asymmetric). **Three distinct
"regime overlay / meta-model" approaches (macro-binary-symmetric,
macro-binary-asymmetric, ML-classifier-continuous) now all show
identical 100 %-overlap failure on edu + spy_real.** The common
failure mode is that **any slow-moving regime proxy cointegrates with
realized portfolio vol at the business-cycle scales that drive the
blend's own de-lever**, whether that proxy is yield-curve slope,
cross-asset correlation, VIX level, or a classifier trained on them.

Empirical evidence: iter 013 gate fires at 10.1 % / 6.3 % / 3.2 %
(edu/spy/ndx) with 100 % / 100 % / 62.5 % bottom-20 %-scale overlap;
iter 009 fires at 16.3 % / 17.8 % / 18.5 % with 100 % / 100 % / 40 %;
iter 012 fires at 15.2 % / 17.1 % / 12.9 % with 100 % / 100 % /
40.5 %. Different fire-rates, same structural overlap.

### Don't re-test

- **Meta-labeling classifiers (logistic regression, random forest,
  gradient boosting, simple MLP) on a vol-managed SPY/QQQ+TLT blend
  using any subset of the following features**: SPY-TLT rolling
  correlation (any window 21-252 bars), VIX level or z-score (any
  normalisation window), realized volatility of either leg (any
  lookback), SMA/EMA/momentum of either leg, yield-curve-slope
  signals (T10Y3M, T10Y2M, etc.), SPY-VIX spread. Every one of these
  cointegrates with σ²_port at the business-cycle scale.
- **Retrain-cadence or window-size variations** (train 500/2000
  bars, retrain quarterly/monthly) on the same feature set — the
  cointegration is structural, not parametric; smaller windows make
  the classifier noisier without adding orthogonal information.
- **Decision-threshold sweep** (p > 0.4, p > 0.6) on iter 013's
  feature set — still the same signal source, just different
  fire-rate.
- **Non-linear classifiers with identical features** (random forest,
  GBM, XGBoost, neural net) — a more expressive model cannot
  manufacture orthogonality from correlated features; it just
  overfits harder on the training set, which DSR then penalises.

### Path forward (NOT dead)

- **Option E (EBP credit-cycle overlay)** remains valid IFF
  pre-validation shows EBP's 60-day rolling correlation with
  σ²_port(iter 008) stays < 0.30 on > 80 % of bars. 1998 LTCM, 2008
  GFC, 2020 COVID fire-episodes are partially independent of
  rates-term-structure, so this is plausible — but not guaranteed.
  Pre-screen BEFORE committing DSR budget.
- **Option G (return-stacked ETF rotation)** remains valid. Different
  universe (NTSX/NTSI/NTSE or synthetic proxies), different primitive
  (built-in futures-stacking leverage).
- **Option H (meta-labeling with empirically-screened orthogonal
  features)** remains valid. Same architecture as iter 013, but
  reject any feature whose |ρ(feature, σ²_port)| > 0.30 on > 20 %
  of bars BEFORE training. Candidate features to screen: HYG/LQD
  credit spread ratio, VIX term-structure slope (VIX3M/VIX if
  available), cross-sectional breadth (% components above 200d MA),
  FX carry basket. Only features passing the screen advance to
  full-iter test.

---

## From iteration 009 — T10Y3M binary-haircut overlay on vol-managed SPY+TLT blend

Complete study: `studies/strategy_hunt_loop/iterations/009-2026-04-24-1447-term-spread-overlay-blend/final_report.md`.

### What the iteration resolved

Canonical 10Y-3M Treasury term-spread (Estrella-Mishkin 1998 / Estrella-
Hardouvelis 1991) tested as a binary-haircut macro overlay on iter
008's single-cfg vol-managed SPY+TLT blend (`vt15_L21_cap20`). Single
pre-committed overlay cfg `ts_inv21_h50`: threshold=0.0 (classical
inversion), haircut=0.5 (Carver tier-2 half-exposure), smoothing=21-day
EMA (monthly emulation of Estrella-Mishkin's data frequency), lag=1
bar (no look-ahead). Result: **Sharpe regresses** on all 3 datasets
(edu −0.029, spy −0.021, ndx −0.014); score **74 → 64** (Kill #3
TRIGGERED at pre-commit < 65 threshold). Winner conditions **4/5 → 3/5**.

KILL #3 (score < 65) TRIGGERED. KILL #1 (Sharpe regression > 0.05) did
NOT trigger — the regression is bounded but systematic.

### Structural principle (do NOT re-test)

**Macro leading-indicator overlays on vol-managed blends must preserve
the signal's LEAD-TIME property.** T10Y3M is canonically a 6-18 month
recession leading indicator. The 21-day EMA smoothing pre-committed
for iter 009 (to emulate Estrella-Mishkin's monthly-data regime)
**erased the lead**: the smoothed series inverts within 1-2 months of
rising realized vol, which variance-scaling (σ²_port) is already
reacting to. Diagnostic: **100% of gate-fire bars coincide with
bottom-20% blend scale bars on educational + spy_real**; 40% overlap
on ndx_real. The overlay adds no early-warning information, only
duplicates the blend's own de-lever magnitude.

Empirical asymmetry: Sharpe damage is proportional to the gate
fire-rate (edu 16.3% fires → Δ−0.029; spy 17.8% → Δ−0.021; ndx 18.5%
→ Δ−0.014). CAGR drag is ~1.5-1.9 pp per dataset — cost of halving
exposure on bars with positive drift exceeds the benefit of halving
on bars with negative drift.

Additional failure mode: **symmetric haircut** (applied to BOTH legs
in equal proportion) forfeits the bond leg's flight-to-quality rally
during recessions. SPY-TLT correlation ≈ −0.30 means the bond leg
typically appreciates when equity falls; halving the bond leg during
inversion compounds the CAGR drag.

### Don't re-test

- T10Y3M binary-haircut overlay with threshold=0, haircut=0.5, and
  smoothing ≥ 21 days on any vol-managed 2-asset blend. Variants with
  slightly different thresholds / haircuts / smoothing windows in the
  same family share the dead-end (1-signal-1-threshold-1-haircut with
  monthly-scale smoothing is the killer configuration).
- EMA-smoothed macro leading indicators (CAPE, EBP, T10Y3M, VIX) at
  smoothing windows ≥ 21 days as overlays on a vol-managed portfolio
  base — the smoothing destroys the lead-time that makes these
  signals valuable and the signal becomes redundant with the blend's
  own variance-scaling.
- Symmetric haircut (same factor on equity AND bond legs) during
  recession regimes on a 2-asset stock-bond blend — forfeits bond-leg
  flight-to-quality benefit.

### Path forward (NOT dead)

- **Asymmetric T10Y3M overlay**: raw (or ≤ 5-day smoothed) signal +
  haircut on EQUITY LEG ONLY. Preserves lead-time AND respects flight-
  to-quality. Untested.
- **EBP (excess bond premium, Gilchrist-Zakrajšek 2012) overlay**:
  credit-cycle signal structurally distinct from yield-curve slope.
  Monthly data → held constant within month, applied at daily rebalance.
- **3-asset blend extension (SPY+TLT+GLD)**: structural extension
  rather than overlay; different asset structure = different
  diversification axis. Most likely path to break the
  redundancy-with-variance-scaling ceiling.
- **Meta-labeling on iter 008 blend** (AFML ch.3): secondary ML model
  predicts bar-level profitability using cross-sectional + macro
  features. Orthogonal by construction.

---

## Structural dead-end categories

Any new hypothesis that falls into one of these is automatically
rejected — require qualitatively different mechanism:

- [ ] Daily timeframe + leveraged ETF + discrete stop
- [ ] Single-indicator de-lever on CAPE / EBP / VIX / term spread
- [ ] Equal-weight composite of the above 4 indicators
- [ ] SMA/EMA crossover filter on SPY with leverage
- [ ] Drawdown-based stop-loss as the primary risk control
- [ ] Parameter variations of (lookback, threshold, buy_L, sell_L,
      stop%, re-entry_param, λ) on any of the above
- [ ] Clenow canonical 10 bps ATR-risk-parity on sector-ETF universe
      with top-K ≤ 5 (iter 002 — capital under-deployed by ~3×)
- [ ] Small grids (≤ 4 configs) of a single strategy family where every
      config lives in the same near-zero-return regime (G1 PBO = 0.5
      noise floor, uninformative)
- [ ] Clenow adjusted-slope × R² ranking with equal-notional 1/K sizing
      on 11 SPDR sectors (iter 003 — signal absent, deployment fix does
      not resurrect it)
- [ ] Cross-sectional ranking momentum on any ≤20-asset ETF universe of
      diversified baskets (iter 003 — universe too homogeneous, aggregate
      market factor dominates idiosyncratic ranking signal)
- [ ] Single-asset vol-adaptation on SPY/QQQ with any static `f(σ̂_{t-1})`
      exponent choice (iter 004 σ⁻¹ + iter 005 σ⁻² — family saturates at
      +0.08-0.10 real-data Sharpe edge; only compounding mechanisms through)
- [ ] Vol-managed N-leg blends (N ≥ 2 with dynamic weights) on a 12-config
      grid — iter 006 PBO 0.69 on spy_real (vs 0.24 single-asset). Grid-
      design caveat, mechanism itself remains valid under single-cfg or
      signal-overlay approaches.
- [ ] Time-series momentum overlay (any lookback/skip/threshold) on a
      vol-managed 2-asset blend with variance-scaling (iter 007) —
      momentum signal is redundant with variance-scaling's regime
      sensitivity; both track same equity-vol information. Compounding
      needs orthogonal signals (carry, macro, meta-labeling).
- [ ] 3-config ex-ante grids of blend × binary-signal family — iter 007
      showed G1 PBO = 0.64-0.76 even at 3 pre-declared cfgs. Overfit-
      sensitivity is structural to the compound, not to grid search.
- [ ] Monthly-smoothed (EMA ≥ 21 days) macro leading indicator binary
      haircut as overlay on vol-managed 2-asset blend (iter 009) — the
      smoothing erases the lead-time that makes the signal valuable;
      signal fires concurrently with blend's own variance-scaling
      de-lever (100% bottom-20% scale overlap on edu + spy). Score
      regresses 74 → 64, Kill #3 TRIGGERED. Symmetric haircut on both
      legs additionally forfeits bond-leg flight-to-quality.
- [ ] **T10Y3M (or any yield-curve-slope) binary-haircut overlay on
      vol-managed SPY/QQQ+TLT blend at ANY smoothing window + ANY leg
      asymmetry combination** (iter 012, combined with iter 009). The
      2×2 matrix {heavy/light smoothing × symmetric/asymmetric} is
      fully closed: light+asymmetric (5d EMA, equity-only) scored 58
      with the SAME 100% gate-fire/bottom-20%-scale overlap on edu+spy
      as iter 009's heavy+symmetric 64. Redundancy is structural
      cointegration of T10Y3M with SPY realized-vol at the
      business-cycle timescale, not a parameter choice. Kill #1 + #3
      + #4 all triggered. **Productive direction**: orthogonal
      information (meta-labeling AFML ch.3 / EBP credit-cycle signal /
      return-stacked ETF rotation) — NOT yield-curve derivatives.
- [ ] Weekly-rebalance (or slower) cadence for vol-managed variance-
      targeting multi-leg blend (iter 011) — vol-targeting mechanism
      requires DAILY cadence to react to intra-window regime shifts.
      MDD ballooned +10-14 pp vs daily counterpart, cap-hit
      frequency 86%→95% (target no longer binding), DSR got WORSE
      (0.368→0.515), turnover UP, cross-asset correlation WEAKER.
      Score 74 → 52, Kill #1 + #3 TRIGGERED. **DSR-ceiling attacks
      via timeframe change are structurally unavailable** for this
      mechanism — the DSR formula's T reduction exactly cancels the
      periodic-Sharpe growth at first order. Also applies by
      extension to monthly cadence (not tested but structurally
      worse). Path forward: Option B' asymmetric overlay + Option C
      meta-labeling, both on daily cadence.
- [ ] **Meta-labeling classifier (LR/RF/GBM/etc.) with any vol-proxy
      feature set on a vol-managed SPY/QQQ+TLT blend** (iter 013).
      Features cointegrated with σ²_port at business-cycle scale:
      SPY-TLT rolling correlation (any window), VIX level or
      z-score, realized volatility of either leg, SMA/EMA/momentum
      of either leg, yield-curve slope, SPY-VIX spread. Classifier
      is NOT degenerate (p_act std 0.19-0.21) but learns redundant
      de-lever rule. Score 74 → 64 with 100% gate-fire/bottom-
      20%-scale overlap on edu+spy. **Three regime overlay/meta-
      model approaches now all closed with same diagnostic (iter
      009 symmetric T10Y3M, iter 012 asymmetric T10Y3M, iter 013
      LR meta)** — vol-proxy signals cannot break 74/100 ceiling
      regardless of implementation. Kill #3 TRIGGERED. Path forward:
      Option E (EBP with pre-validation), Option G (return-stacked),
      Option H (meta-labeling with EMPIRICALLY pre-screened features
      where |ρ(feature, σ²_port)| < 0.30 on > 80% of bars).
- [ ] **EBP (Gilchrist-Zakrajšek 2012) credit-cycle binary-haircut
      overlay on vol-managed SPY+TLT (or SPY+TLT+GLD) blend at ANY
      threshold/z-window/smoothing/lag choice** (iter 014 —
      pre-validation screen rejects all 3 datasets; 60d rolling
      |ρ(EBP_z, σ²_port)| > 0.30 on 68-71 % of bars, mean |ρ| ≈ 0.47,
      max 0.96). GZ2012's decomposition strips expected-default risk
      but the residual still cointegrates with blend realised variance
      at 60-day business-cycle scale. Kill #PV TRIGGERED before any
      backtest — no DSR trial committed. Also applies to HYG/LQD
      ratio and any other credit-spread-derivative signal on this
      mechanism. **Fourth consecutive overlay failure on iter 008
      blend (009/012/013/014) — overlay family CLOSED on this
      mechanism**; mechanism change required. The **pre-validation
      screen methodology (60d |ρ(feature, σ²_port)| > 0.30 exceed
      fraction > 20% → abort)** introduced in iter 014 is now
      MANDATORY for any future overlay/meta-label proposal on a
      vol-managed blend.
- [ ] **Cross-sectional top-K momentum rotation on ≤ 3-region equity
      universe (US/INTL/EM, any of SPY/QQQ × EFA/VEA/IEFA ×
      EEM/VWO/IEMG) with iter 016's fixed-ratio × vol-target
      primitive, at ANY lookback ∈ {63, 126, 189, 252, 378} days,
      ANY skip ∈ {0, 5, 10, 21, 42}, ANY top-K ∈ {1, 2, 3}, ANY
      rebalance cadence ∈ {daily, weekly, monthly, quarterly}**
      (iter 017). Actively HURTS vs always-US base (Δ Sharpe 3/3
      regress −0.18/−0.32; score 79 → 52; 4/5 winner → 3/5). The
      period-matched regional Sharpe differential on 2006-2026
      (US 0.63-0.95 vs EFA 0.36-0.48 vs EEM 0.34-0.42) exceeds any
      plausible uplift from catching regional-leadership
      transitions — 22-42 % of months spent in EFA/EEM eats the
      differential without recapturing it via rare leadership
      windows. Extends iter 003 dead-end from homogeneous sector
      ETFs to regional equity ETFs. Variants closed: Clenow
      adjusted-slope × R² ranking on same 3-region universe;
      absolute-momentum filter variant; adding a 4th
      regional-equity ETF (total-US / frontier) while keeping the
      same mechanism — all inherit the Sharpe-differential trap.
      Kill #1 + #2 + #3 triggered. **Path forward requires a
      DIFFERENT information source** — cross-sectional valuation
      (mean-reverting, not trend-following), cross-asset-class
      rotation (classes not nested within single equity risk
      premium factor), or structurally convex primitives like
      options tail-hedge.

---

## From iteration 014 — EBP credit-cycle binary haircut overlay, rejected by pre-validation screen

Complete study: `studies/strategy_hunt_loop/iterations/014-2026-04-24-1642-ebp-credit-overlay-blend/final_report.md`.

### What the iteration resolved

Iter 014 tested BASE_MEMORY's "Option E" — a binary-haircut overlay on
iter 008's `vt15_L21_cap20` blend driven by the **Gilchrist-Zakrajšek
(2012) Excess Bond Premium (EBP)** signal. EBP is the residual of
corporate bond spreads AFTER stripping expected-default variation; the
hypothesis was that this decomposition would produce a credit-risk-
premium signal partially orthogonal to realised equity volatility,
allowing the overlay to add information iter 013's vol-proxy features
could not.

Iter 014 also introduced a novel pre-commit methodology: a **mandatory
pre-validation screen** that measures 60-day rolling
|ρ(EBP_z_252, σ²_port(blend))| across each dataset and aborts the
iteration BEFORE running any backtest if the fraction of windows with
|ρ| > 0.30 exceeds 20 % on ANY dataset. The screen is the primary
defense against re-opening the cointegration failure mode that killed
iter 009 (T10Y3M 21d symmetric), iter 012 (T10Y3M 5d asymmetric) and
iter 013 (LR meta with ρ_60 + VIX_z_252).

Result: **pre-validation screen FAILS decisively on all 3 datasets**:

| dataset | exceed_frac | max |ρ| | mean |ρ| |
|---|---|---|---|
| educational | **0.684** | 0.958 | 0.469 |
| spy_real    | **0.691** | 0.958 | 0.472 |
| ndx_real    | **0.706** | 0.942 | 0.482 |

All three datasets show ~3.4× overshoot of the 20 % abort threshold,
mean |ρ| ≈ 0.47 (1.5× the 0.30 threshold), max touching 0.96. **Kill
#PV triggered → abort iteration before full backtest, no DSR trial
committed (cumulative_n_trials unchanged at 4255).** Score 0/100 FAIL.

### Structural principle (do NOT re-test)

**EBP (Gilchrist-Zakrajšek 2012 residual) is empirically cointegrated
with blend σ²_port at the 60-day business-cycle timescale on all 3
datasets.** The GZ2012 decomposition that strips expected-default
variation from corporate bond spreads still leaves a residual that
swings WITH equity-vol regimes at the 60-day scale. The credit cycle
and equity-vol cycle are measurably co-moving at this observation
window.

More broadly: **any "regime" signal on the vol-managed SPY+TLT blend
cointegrates with σ²_port at business-cycle scales** — this is a
property of the portfolio's own response function. The blend self-
adjusts on the same macro-risk gradient that drives yield-curve
slopes, cross-asset correlation, VIX, and now credit-risk-premium
residual. Four independent attempts (iter 009, 012, 013, 014) now
document this structural pattern.

### Don't re-test

- **EBP overlay on vol-managed SPY+TLT (or SPY+TLT+GLD) blend at any
  threshold, z-score window, smoothing, or lag choice** — pre-val
  result is structural, not parametric. Variants forbidden:
  threshold ∈ {0.5, 1.5, 2.0}, z-window ∈ {63, 126, 504},
  applied_to ∈ {both, bond-only, conditional}, lag ∈ {0, 2, 5}.
- **Any other credit-cycle / credit-spread signal as a binary-
  haircut or meta-label overlay** on a vol-managed stock-bond blend
  at 60-day observation scale: HYG/LQD ratio, AAA spread,
  BBB spread, distance-to-default indices, dealer-inventory
  proxies — all are observationally cointegrated with σ²_port
  at the relevant business-cycle window.
- **Bigger ensemble of macro features (EBP + T10Y3M + VIX + SPY-TLT
  correlation + ρ_HY)** as meta-label inputs — each individual
  feature is cointegrated with σ²_port; a weighted combination only
  inherits the same cointegration.
- **Running any new overlay or meta-label on iter 008/010 blend
  without first running the 60-day |ρ(feature, σ²_port)| > 0.30
  pre-validation screen**. The pre-commit methodology is now
  mandatory for all such proposals.

### Path forward (NOT dead — but requires MECHANISM change)

The overlay family on the vol-managed SPY+TLT blend is structurally
closed. Further progress requires a primitive that doesn't have a
σ²_port-like self-adjustment response:

- **Return-stacked ETF rotation (NTSX/NTSI/NTSE)** — built-in futures-
  stacking primitive, structurally distinct from iter 008's explicit
  vol-scaling + risk-parity weighting.
- **Cross-sectional signals on heterogeneous universes** — factor
  ETFs (MTUM, QUAL, VLUE, USMV, SIZE, SPMO) have genuine ranking
  structure (unlike sector ETFs killed by iter 003).
- **Options-implied regime signals on plain single-asset SPY** — no
  σ²_port axis means no cointegration to worry about; VIX3M/VIX
  slope or put-call skew tested as regime conditioning.

---

## From iteration 017 — 12-1 top-1 regional rotation (cross-sectional, ≤3 regions) on iter 016 base

Complete study: `studies/strategy_hunt_loop/iterations/017-2026-04-24-1750-regional-rotation-stack-vm/final_report.md`.

### What the iteration resolved

Iter 017 tested BASE_MEMORY's PRIMARY iter-017 rec — "Option R" —
extending iter 016's fixed-ratio × vol-target primitive
(`ntsx_vm_vt15_L21_cap20`) to a 3-region cross-sectional rotation.
Universe: {US (SPY on edu/spy, QQQ on ndx), Developed ex-US (EFA),
Emerging (EEM)}, each stacked with IEF via iter 016's 0.6/0.4 ratio ×
vt15/L21/cap20 vol-target engine. Selection rule: top-1 by 12-1
skip-a-month momentum (`p[t-21]/p[t-252] - 1`), re-ranked monthly
(21 bars). Single pre-committed cfg; iter 016 mechanism applied on
the selected region's (equity, IEF) pair within each 21-bar hold
window. 2 bps/leg running cost + 2 bps one-off switch cost on
equity-leg transitions.

Result: **score 52/100 MARGINAL** (−27 vs iter 016's 79). Three
pre-committed kill criteria TRIGGERED: Kill #1 (Sharpe regress > 0.03
vs iter 016 on ≥ 2 ds — actually 3/3 regress: edu Δ −0.225, spy
Δ −0.319, ndx Δ −0.176), Kill #2 (winner conditions dropped 4/5 →
3/5 — Sharpe axis lost all 3 datasets), Kill #3 (score < 72 — 52 is
decisively below). Kill #4 (MDD regress > 5pp) and Kill #5 (turnover
> 15/yr) NOT triggered.

Sharpe vs frozen benchmarks: edu 0.758 (+0.078), spy 0.819 (−0.081),
ndx 1.019 (+0.064). 0/3 datasets clear the +0.10 Sharpe-edge winner
gate (iter 016 was 3/3 clear by +0.24-0.30 margin).

### Structural principle (do NOT re-test)

**Cross-sectional top-K momentum rotation on ≤ 3-region equity
universes fails when one region has a structurally higher period
Sharpe than the others in the sample window.** The failure mode is
not "momentum signal noise" — the selector correctly concentrated on
US 58-78 % of months. It's that the remaining 22-42 % spent in EFA
or EEM generates decisive drag because their period Sharpes are
materially lower. Empirical numbers:

| region | 2006-2026 Sharpe | 2010-2026 Sharpe |
|---|---|---|
| SPY | 0.63 | 0.90 |
| QQQ | — | 0.95 |
| EFA | 0.36 | 0.48 |
| EEM | 0.34 | 0.42 |

12-1 momentum selected EFA/EEM frequently enough (22-42 % of months
on educational + spy_real) that the portfolio ate the
period-matched Sharpe differential without recapturing it via
regional-leadership transitions (2003-2007 EM commodities is BEFORE
our window, 2014-2017 / 2022 non-US windows are too brief to
dominate the full 17-20y signal average).

Cross-asset correlations on the IEF-aligned window are high (US-INTL
0.76-0.88, US-EM 0.73-0.82, INTL-EM 0.85-0.87), confirming the
iter 003 structural lesson ("cross-sectional ranking momentum needs
universe heterogeneity") extends from homogeneous sector ETFs
(ρ ≈ 0.7-0.9) to regional equity ETFs (ρ ≈ 0.73-0.88) when a
single region dominates the sample Sharpe.

Additional failure mode: **DSR p-values REGRESSED sharply vs iter 016**
(0.226/0.163/0.132 → 0.625/0.651/0.378). The rotation added noise
without adding observed Sharpe, so the signal-to-deflator ratio
worsened markedly — three new trials (n_trials 4261 → 4264) were a
minor deflator change; the dominant effect was observed-Sharpe
regression.

### Don't re-test

- Any top-K ∈ {1, 2, 3} cross-sectional momentum rotation on
  {US, Developed ex-US (EFA / IEFA / VEA), Emerging (EEM / IEMG /
  VWO)} ± iter 016's primitive with ANY lookback ∈ {63, 126, 189,
  252, 378} days, ANY skip ∈ {0, 5, 10, 21, 42}, ANY rebalance
  cadence ∈ {daily, weekly, monthly, quarterly}. The killer is the
  dominant-region Sharpe-differential structure on THIS sample
  window, not the parameter choice.
- Clenow adjusted-slope × R² ranking on the same 3-region universe
  — same structural failure mode, just with a different ranking
  score. Regional Sharpe differential eats the selector edge.
- Absolute-momentum FILTER variant ("long the winning region only if
  its 12-1 > 0, else cash or bond-only") — same 3-region universe,
  same dominant-US structure, just adds binary gate redundant with
  iter 016's vol-target (iter 007 lesson applies).
- Adding a 4th region (e.g. VTI = total-US, SPEM, FM = frontier) to
  the rotation universe while keeping the same 12-1 + top-K=1-2
  mechanism — expected effect is dilution of US concentration
  (mechanically worse, not better, given the Sharpe-gap structure).

### Path forward (NOT dead — strictly different mechanism)

The only remaining untested primitives that are structurally
orthogonal to iter 017's failed mechanism AND iter 009/012/013/014
overlay failures AND iter 007 TSMOM redundancy:

- **Put-spread collar tail-hedge** on iter 016's equity leg (bond
  leg unchanged). Options P&L is a CONVEX function of underlying,
  cannot cointegrate linearly with σ²_port at business-cycle scale.
  Adds skewness-capture axis. Requires options-chain data
  ingestion from CBOE PPUT/CLL indices.
- **Funding-cost-modeled iter 016 replay**: subtract realistic
  `0.5 × DGS3MO` from iter 016 net returns. Zero new trials; a
  deployability validation rather than a hunt-loop iteration.
- **Cross-sectional VALUATION rotation** (CAPE or P/B spread between
  regions) — different information source than momentum, no
  Sharpe-differential trap because valuation is mean-reverting not
  trend-following. Would NOT re-open the iter 017 dead-end because
  the SIGNAL is structurally different. Requires CAPE/P-B data
  ingestion.
- **Cross-asset-class rotation** (equities vs bonds vs FX vs
  commodities) — the Sharpe-differential argument that killed iter
  017 doesn't apply because the classes aren't nested within a
  single equity risk premium factor.

---

## From iteration 019 — HMM stock-bond correlation regime rotation on iter 016 base (pre-val abort)

Complete study:
`studies/strategy_hunt_loop/iterations/019-2026-04-24-1833-hmm-stock-bond-regime/final_report.md`.

### What failed (do NOT re-test)

1. **Any regime signal derived from ρ_stock_bond (60d rolling
   correlation between SPY/QQQ and IEF) applied as an overlay to a
   vol-managed 2-leg stack** — abort triggered on pre-val screen
   (iter 014 pattern). Per-dataset rolling 60-bar |corr(binary_state,
   σ²_port_iter016)| exceed-fraction: **64.6% / 66.5% / 48.8%** vs
   20% ceiling — 2.4-3.3× over. Continuous ρ_60 vs σ²_port exceed-
   fraction: 64.5% / 64.7% / 66.7% — uniformly ~3.2× over.

2. **The specific root cause is ALGEBRAIC, not empirical.** σ²_port
   for a 2-leg blend is
   σ²_port = w_eq²·σ²_eq + w_bd²·σ²_bd + **2·w_eq·w_bd·ρ·σ_eq·σ_bd**,
   which contains ρ as a multiplicative factor in the cross-term.
   Any measurable function of ρ (threshold, HMM state, clustering,
   GMM posterior, sign indicator) is cointegrated with σ²_port by
   construction. The cointegration does NOT depend on choice of
   threshold, number of HMM states, discretization method, or
   feature-smoothing kernel — it is a consequence of the portfolio-
   variance identity itself.

3. **HMM discretization does NOT rescue the cointegration.** Iter
   014 had left the HMM case open as "binary state ∈ {0, 1} might
   break the cointegration sufficiently". Iter 019's pre-val answers
   NO: the binary-threshold state (conservative upper bound on any
   HMM-smoothed state) fails by the same margin as continuous ρ.
   HMM forward-backward is a smoothing operator on ρ; it cannot
   contain more orthogonalization information than the raw ρ.

### Don't re-test

- **2-state Gaussian HMM** on ρ_60d with state-conditional
  {0.6/0.4 ↔ 0.3/0.7} ratio rotation on iter 016 base (iter 019
  configuration).
- **Any n-state HMM** (n ∈ {2, 3, 4, 5}) on any ρ-based feature
  (ρ_20, ρ_60, ρ_120, EWMA ρ, DCC-GARCH-modeled ρ) applied as
  overlay on iter 008 / iter 010 / iter 015 / iter 016 — same
  algebraic cointegration applies.
- **Regime classifier** via k-means, Gaussian mixture, agglomerative
  clustering, or spectral clustering on ρ features, applied to
  vol-managed 2-leg stack ratio rotation.
- **Threshold overlays** on ρ (single threshold, percentile bands,
  volatility-scaled thresholds, regime-stable thresholds, etc.) on
  any vol-managed 2-leg stack.
- **Any overlay mechanism whose primary feature is a measurable
  function of (σ_eq, σ_bd, ρ)** — the three ingredients of σ²_port
  by identity. This includes: VIX z-score (σ_eq proxy), MOVE index
  (σ_bd proxy), realized-vol regimes on either leg, vol-of-vol
  signals, correlation skewness signals, correlation dispersion, etc.

### Structural principles

- **Vol-managed portfolio scaling signals are feature-exhaustive for
  their ingredient features.** Any overlay drawn from the ingredient
  set (σ_eq, σ_bd, ρ) is structurally redundant — the variance-
  target already optimally scales based on these. Adding a regime-
  overlay based on any of them is zero-information-gain AT BEST,
  noise-introduction AT WORST.
- **Discretization is not orthogonalization.** A binary/categorical
  partition of a cointegrated continuous signal inherits the
  cointegration. To escape σ²_port cointegration, the overlay
  feature must be drawn from information NOT representable as a
  function of (σ_eq, σ_bd, ρ). Examples of structurally-escaping
  features: options-implied skewness, options-implied kurtosis,
  convex payoffs from options positions (Carr-Madan static
  replication), cross-asset carry spreads (FX/commodities/bonds
  decoupled from the blend's equity-bond axis), fundamental
  valuation spreads (CAPE differential, earnings yield spread).
- **Pre-val screen is mandatory for ANY proposed overlay on
  vol-managed stacks.** Iter 014 (EBP credit), iter 019 (ρ_60 HMM):
  two out of two pre-val tests failed, protecting 2-4h of wasted
  implementation each. The screen should now be considered the
  standard first step of any overlay iteration, not an optional
  sanity check.

---

## Things that might still work (in principle)

These are NOT dead-ends, just untested:

- Weekly/monthly timeframe (not daily)
- Cross-sectional VALUATION (not momentum) rotation
- Cross-ASSET-CLASS rotation (equity vs bonds vs FX vs commodities)
- Factor rotation (value/momentum/quality/low-vol dynamic weights)
- Options overlay (put spreads as tail insurance) — structurally
  convex, orthogonal to linear overlay failures. **Now the ONLY
  remaining structurally orthogonal primitive after iter 019 closed
  ρ-derived overlays algebraically.**
- Funding-cost-modeled replay of iter 016 for deployability check
  — ✅ done in iter 018, validated
- ML-based meta-labeling with EMPIRICALLY pre-screened orthogonal
  features (iter 014 pre-val screen mandatory) — must use features
  structurally disjoint from (σ_eq, σ_bd, ρ) per iter 019's finding
- ~~Regime-switching HMM on correlation or macro state (iter 014
  predicts pre-val likely fails; run screen first)~~ — **✗ CLOSED
  by iter 019** on correlation variant; macro-state HMM would need
  features structurally orthogonal to (σ_eq, σ_bd, ρ)
- ~~Convex options overlays (put-spread, protective put, collar) on
  vol-managed 2-leg stacks~~ — **✗ CLOSED by iter 020** (long-gamma
  redundant with vol-target's variance response; short-vol harvest
  still open)
- Seasonality-based entries/exits
- Dynamic vol-targeting (Carver) without any leverage

The `## Promising unexplored directions` section of `BASE_MEMORY.md`
prioritizes these.

---

## From iteration 020 — monthly-rolled put-spread tail hedge on iter 016 equity leg

Complete study:
`studies/strategy_hunt_loop/iterations/020-2026-04-24-1850-put-spread-tail-hedge/final_report.md`.

### What failed (do NOT re-test)

1. **Long 5% OTM / short 10% OTM monthly-rolled put spread on iter
   016 equity leg (`ntsx_vm_vt15_L21_cap20_pp5_10_1m`).** Single
   pre-committed cfg: 21-DTE expiry, monthly roll, BS-priced with VIX
   as IV (iv_scale 1.0 for SPY, 1.1 for QQQ as VXN proxy), 5 bps per
   roll transaction cost, hedge_notional_ratio=1.0. Result: Sharpe
   regress **−0.076 / −0.077 / −0.044** vs iter 016 on edu/spy/ndx
   (Kill #1 triggered, 2 of 3 ds clear); MDD WORSE by **+5.68 /
   +3.23 / +4.61 pp** on all 3 ds (Kill #2 triggered, 0/3 improve);
   hedge P&L annualised **−3.03% / −3.00% / −4.13%**, hedge Sharpe
   −0.73 / −0.78 / −0.93, only 28-30% of bars positive; worst DSR
   p=0.340 (deteriorated from iter 016's 0.226). Score 79/100 by
   rubric (ties top-K) but STRICTLY DOMINATED by iter 016 on every
   meaningful axis.

2. **The specific root cause: structural REDUNDANCY between long-gamma
   hedge and vol-target scaling on the same σ² process.** Carr-Madan
   (1999) orthogonality — "options P&L is convex, cannot be
   reconstructed from σ² alone" — is an information-theoretic
   statement that holds STATICALLY but does NOT deliver value in a
   dynamic σ-feedback system. iter 016's vol-target already responds
   to σ²_{t-1} by de-levering; both mechanisms fire on the same
   trigger event (S_t drops sharply ↔ σ²_t spikes), so they duplicate
   crash protection at double the cost rather than compounding it.
   Additional mechanism-level drivers:
   - The hedge's persistent theta drag during calm regimes inflates
     drawdown windows (calm periods of ~3%/yr drag cause slow
     equity curve decay → deeper peak-to-trough excursions before
     the next peak is reached).
   - At scale ~1.9× (cap-hit 76-89% of bars on iter 016 base), the
     effective hedge drag is scale × hedge_cost ≈ 5-8%/yr in
     portfolio-level terms.
   - VIX-as-IV pricing matches empirical put-spread CBOE indices
     (PPUT/CLL history) to within ~50 bps/yr drag — the implementation
     is faithful, not an artefact of bad pricing.

### Don't re-test

- Monthly-rolled 5/10 OTM put-spread (or any OTM long/short put
  spread wider-than-cost) on iter 016 / 015 / 008 / 010 base. The
  spread-family closure applies to any bounded-payoff long-gamma
  structure.
- Pure protective put (long only, no short leg) on the same base —
  would have HIGHER drag than the spread tested here (which was the
  best-case); closed by strict dominance.
- Collar (long put + short call) on the same base — the short-call
  leg caps upside and adds its own drag in bull regimes; the long-put
  drag is what iter 020 measured; net result would be worse Sharpe
  (calls cap upside) with the same MDD problem.
- Any grid variant (strike pct × DTE × roll frequency × IV scaling)
  of the long-gamma family on a vol-managed 2-leg stack — changing
  parameters within the family cannot break the structural redundancy
  with vol-target.
- Quarterly (63-DTE) or weekly (5-DTE) rolled long-put or long
  put-spread on iter 016 base — different roll cadence moves drag
  magnitude but not the redundancy mechanism.
- Applying overlay to bond leg (long IEF puts) — same σ²_bd
  redundancy applies; bond vol drives pos_bd scaling already.

### Don't re-test on other bases UNLESS the base is NOT vol-managed

- Long-gamma overlay on iter 015 (static NTSX, no vol-target) —
  might work because the base has no σ² feedback, so overlay and
  base are genuinely orthogonal. Expected score: 75-80 with genuine
  MDD reduction. But base scored 77 alone → overlay would need to
  be >+2 score additive to be interesting; drag cost may cancel.
  Low-priority vs Option V/W/X.

### Structural principles

- **In a dynamic σ-feedback system (vol-target, vol-managed, risk-
  parity-DCC), any overlay whose expected P&L is monotone in σ² is
  structurally REDUNDANT with the base.** The base has already
  extracted the conditional-mean information from σ²; the overlay
  adds only conditional higher-moment information (skew, kurtosis)
  at a cost that exceeds the value of those higher moments on broad
  equity indices (where higher moments are already small per
  Israelov 2017 AQR).
- **Rubric-score 79 in a "STRONG" tier can mask strict domination.**
  The hunt-loop score measures edge vs SPY, not incremental value vs
  the parent strategy. Kill criteria (pre-committed, base-relative)
  are the only guard against "inherited edge" scoring artefacts.
  Future iterations building on existing top-K members MUST declare
  base-relative kills, not just absolute ones.
- **Carr-Madan orthogonality ≠ additive value.** The theorem says
  options are in principle INDEPENDENT of variance; it does NOT say
  they add value to a system already acting on variance. Orthogonality
  of FEATURES is necessary but not sufficient for orthogonality of
  IMPROVEMENTS. This is the iter 019 algebraic cointegration argument
  applied one level up: iter 019 showed algebraic redundancy of ρ-
  derived signals with σ²_port; iter 020 shows functional redundancy
  of long-gamma hedges with σ²-responsive base.

### Paths forward (NOT dead)

1. **Variance premium HARVEST (short-vol, opposite sign)** — fires on
   opposite event (low realized-vs-implied differential, not σ² spike).
   Does NOT cointegrate with vol-target because the vol-target
   de-levers DURING σ² spikes while short-vol PROFITS from σ² decay
   AFTER spikes subside. Primary iter 021 candidate. See BASE_MEMORY
   Option V.
2. **Cross-asset carry** — linear P&L from term-structure / interest-
   rate differentials, structurally disjoint from both σ² and
   long-gamma. Secondary iter 021 candidate. See BASE_MEMORY Option W.
3. **Expanded stack with uncorrelated third leg** (DBMF trend, long-
   vol ETF controlled allocation) — changes the σ² ingredient set
   rather than overlaying on it. Tertiary iter 021 candidate. See
   BASE_MEMORY Option X.

---

## From iteration 021 — short-credit-spread VRP harvest (iter 020 sign-flipped) on iter 016 equity leg

Complete study:
`studies/strategy_hunt_loop/iterations/021-2026-04-24-1916-short-credit-spread-vrp/final_report.md`.

### What happened (closes a family, does NOT abandon the parent)

1. **Short 5/10 % OTM monthly-rolled put credit spread on iter 016
   equity leg (`ntsx_vm_vt15_L21_cap20_scs5_10_1m`).** Single
   pre-committed cfg: SELL the exact spread iter 020 BOUGHT, every
   other parameter identical (21-DTE, monthly roll, BS-priced with
   VIX as IV, iv_scale 1.0 SPY / 1.1 QQQ, 5 bps per roll,
   harvest_notional_ratio = 1.0). Result: Sharpe Δ vs iter 016
   **+0.009 / −0.002 / −0.042** (Kill #2 "Δ ≤ 0 on ≥ 2 of 3 ds"
   triggered by tiny margins on spy+ndx); MDD **UNIFORMLY IMPROVED
   −1.95 / −1.01 / −2.85 pp** on all 3 ds (opposite of iter 020's
   +3-6 pp regression); overlay annualised **+2.95 % / +2.94 % /
   +4.10 %** (VRP materialises, matches Bondarenko 2014 empirical
   prior); overlay standalone Sharpe +0.73 / +0.78 / +0.93; DSR
   worst p = **0.2171** (marginally improves iter 016's 0.226 but
   still above the 0.20 scoring tier); G3 WF 7/8/8/8/8/8;
   robustness 9/9 sub-windows positive. Score **79/100 STRONG**
   (ties iter 016 and iter 018 at top-K #1).

2. **The specific structural finding: Sharpe-level symmetry under the
   sign flip.** Iter 020 PAID the variance-risk premium and iter 021
   COLLECTS it, but BOTH tie Sharpe at the vol-managed-stack ceiling
   of ~1.14-1.19 (spy). The vol-target's `σ²_port[t-1] → scale[t]`
   feedback loop absorbs the overlay's variance contribution at the
   next bar, so whatever CAGR the overlay injects or removes, `σ`
   compensates — the portfolio's risk-adjusted return is pinned by
   construction. This is a **portfolio-construction ceiling**, not a
   mechanism limit; changing the sign, strike, or DTE of the overlay
   cannot break it.

3. **The MDD asymmetry is REAL and not noise.** Short theta INCOME
   during calm regimes elevates intermediate peaks, reducing the
   denominator of peak-to-trough drawdown; the capped tail loss
   (credit spread caps at (K_long − K_short)/S_entry ≈ 5 %) prevents
   crash-bar runaway. Conversely, long theta PAYMENT flattens peaks
   and extends drawdown windows — iter 020's +3-6 pp MDD regression.
   So iter 021 is a legitimate **MDD-improving ceteris-paribus
   variant of iter 016**: risk reduction at Sharpe parity. If
   deployment ever targets MDD-at-Sharpe-parity, iter 021 is the cfg.

### Don't re-test

- **Any fixed-sign European options overlay at 5/10 % OTM × 21-DTE on
  a vol-managed 2-leg stack** — both signs now empirically tested and
  both tied at the Sharpe ceiling. Parameter sweeps within this
  family (strike ±2%, DTE 14-28 days, roll frequency) will not break
  the absorption property.
- **Short bare uncapped naked put on iter 016 equity leg at 5 % OTM
  × 21-DTE × full notional** — structurally similar theta source but
  with uncapped tail risk; the crash-bar loss is asymmetric in a way
  the credit spread isn't, and the Sharpe absorption still holds for
  the theta portion. Would likely yield worse MDD than iter 021 at
  similar Sharpe; not worth the tail risk.
- **Stacking both long AND short spread overlays (iter 020 + iter 021
  combined) on iter 016** — the two overlays would exactly cancel
  overlay P&L stream (same strikes, opposite sides) up to transaction
  cost, leaving just 2× the cost drag. Pure destruction of value;
  obvious but do not attempt.
- **Changing the base from iter 016 to iter 015 (static NTSX)**
  without vol-target — MAY work because iter 015 has no σ²_port
  feedback to absorb the overlay. Same caveat as iter 020 paths-
  forward #1: promising but low-priority vs Option X/W/Y from
  BASE_MEMORY. If attempted, score hurdle is +3 over iter 015's 77.

### Don't re-test on other bases UNLESS

- Iter 015 (static NTSX, no vol-target) — short-vol overlay might
  compound genuinely since no σ² feedback is present. Low-priority
  relative to Option X/W/Y because even a +0.10 Sharpe gain on iter
  015's 1.04-1.06 spy-real Sharpe reaches 1.14-1.16 — same ceiling
  iter 016 already hits. Marginal improvement at best.

### Structural principles

- **Vol-target is an ABSORBING operator on equity-leg variance
  contributions.** Any overlay on r_eq that adds a stream `x_t` with
  non-trivial σ²_x gets folded into `σ²_port[t-1]` by the next bar,
  causing the scale `min(target_vol² / σ²_port, cap)` to compensate
  so that portfolio realised-variance stays pinned to target. CAGR
  shifts (up for short-theta, down for long-theta) but Sharpe is
  held constant by construction. This is the **variance-target
  absorption lemma** and applies to any Moreira-Muir-style
  mechanism.
- **Bilateral closure from a single test on each side.** Iter 020
  tested the long side and found drag; iter 021 tested the short
  side and found the Sharpe ceiling. Together these two tests close
  an entire 2-dimensional family (sign × magnitude) — no additional
  parameter sweep is informative under the absorption lemma.
- **Rubric score 79 "STRONG" is a base-absolute metric and can
  coexist with a triggered base-relative Kill.** Iter 021's score
  ties top-K because it inherits iter 016's edge vs SPY; the Kill
  criterion (base-relative Sharpe delta) correctly flags that no
  progress was made toward the DSR-clearance goal. **Future
  iterations MUST pre-commit base-relative kills**, not just
  absolute ones, when building on an existing top-K member.
- **MDD structure is NOT absorbed by vol-target in the same way as
  Sharpe.** The scale operator equalises realised-variance at the
  portfolio level, but drawdown is a PATH-DEPENDENT functional of
  the return stream. Theta income during calm periods provides a
  positive drift that elevates intermediate peaks → lower peak-to-
  trough; theta payment does the opposite. This is a second-order
  effect invisible to the Sharpe gate but material at the
  deployment level.

### Paths forward (NOT dead — inherited from iter 020 + refined)

1. **Option X (3rd uncorrelated leg)** — PROMOTED to primary after
   iter 021. Adds a third σ² ingredient (DBMF trend / commodity
   basket / VIX carry via ETF) with volatility dynamics disjoint
   from SPY realised variance; does not live on the equity leg so
   escapes the absorption lemma. BASE_MEMORY Option X. Expected
   Sharpe hurdle +0.05 over iter 016.
2. **Option W (cross-asset carry)** — secondary. Linear P&L from
   rate/curve differentials is disjoint from all σ² axes and from
   long/short-gamma. Data availability is the primary gate. BASE_MEMORY
   Option W.
3. **Option Y (VX futures roll)** — tertiary. Direct VRP instrument
   on a DIFFERENT underlying (VIX futures ≠ SPY), bypasses the
   equity-overlay absorption. Requires external CBOE/CME data.
   BASE_MEMORY Option Y.
4. **DO NOT pursue further options-on-equity-leg iterations at these
   strikes/DTE** — absorption lemma makes parameter sweeps
   uninformative.

---

## From iteration 022 — TOM seasonality eq_weight modulator on iter 016 base

Complete study: `studies/strategy_hunt_loop/iterations/022-2026-04-24-1942-tom-seasonality-overlay/final_report.md`.

### What failed (do NOT re-test)

1. **Calendar-driven eq:bd weight modulator on vol-managed 2-leg stack**
   (iter 016 base). Cfg `ntsx_vm_vt15_L21_cap20_tom_b90_m50`:
   eq_weight = 0.9 on TOM window (last 3 + first 3 business days of
   each calendar month) / 0.5 mid-month; bd_weight mirrors (0.1 TOM,
   0.5 mid). Sharpe regresses uniformly vs iter 016 by −0.218 / −0.256
   / −0.209 across educational / spy_real / ndx_real — the largest
   iter-to-iter-016 Sharpe drop in the hunt-loop. DSR worst p=0.587
   (vs iter 016's 0.226 — got WORSE). MDD regresses on 2/3 datasets
   (+6.2 pp spy, +7.3 pp ndx). Kills #2, #3, #4 all triggered.

2. **The specific root cause: σ²_port is quadratic in w_eq.** When the
   modulator swings w_eq by Δw = 0.4 (from 0.5 to 0.9), σ²_port
   triples on the boosted bars (since σ_eq ≈ 3.5× σ_bd for
   SPY/QQQ+IEF). Vol-target's scale[t] = target_vol² / σ²_port[t-1]
   compensates by cutting scale by a factor of 3×, so the net equity
   position on TOM days is roughly equal to iter 016's 0.6 constant
   position. The raw TOM-day premium (+1-3 bps/d on all 3 datasets;
   Kill #1 passed cleanly) gets compressed to ~0.6 bps/d net, then
   erased by the turnover cost of switching weights at every TOM
   boundary (~30 bps/day net position change).

3. **Secondary damage from mid-month bond overshoot.** During
   non-TOM bars (~72% of the sample), w_bd = 0.5 instead of iter 016's
   0.4. In the post-2009 zero-rate regime, bonds underperformed
   equity by ~4-6 %/yr, so over-allocating to bonds on most bars
   costs ~40-60 bps/yr in CAGR regardless of TOM premium capture.

4. **The TOM premium IS real** on all 3 datasets (Kill #1 passed):
   Δ mean +1.14 to +2.64 bps/day; TOM-day Sharpe 0.91 / 1.05 / 1.20 vs
   mid-month 0.53 / 0.84 / 0.86. The failure is PORTFOLIO-LEVEL
   absorption, not signal-level absence. Post-overlay TOM-state net
   Sharpe INVERTS on 2/3 datasets (TOM net Sharpe < mid net Sharpe) —
   the vol-target feedback actively negates the premium at the
   aggregate-return level.

### Don't re-test

- TOM, holiday, day-of-week, week-of-month, month-of-year, or
  earnings-calendar weight modulators with Δw ≥ 0.2 swing on any
  vol-managed 2-leg stack (iter 008, iter 016, iter 018, iter 021
  bases). All will fail by the same σ² ∝ w² geometric mechanism.
- Smaller swing magnitudes (Δw = 0.1-0.2) on the same vol-managed
  2-leg base. Will reduce the Sharpe regression magnitude but still
  produce negative net edge vs iter 016 — the scale-compensation ÷
  quadratic-penalty ratio is strictly less than 1 for any Δw > 0.

### Structural principles

- **σ²_port feedback absorbs any time-varying per-leg weight schedule
  on a 2-leg vol-managed stack, regardless of the signal source**
  (variance overlays iter 020/021; ρ-regime overlays iter 019; calendar
  modulators iter 022). The lemma is geometric (quadratic variance
  penalty on w_eq) not signal-specific.

- **Kill #1 (mechanism present in raw data) passing is necessary but
  NOT sufficient for strategy success.** Even a strong raw conditional
  drift signal can be erased at the portfolio-construction level by
  variance-target feedback. Future iterations testing a new signal
  class should ALSO verify that the portfolio construction doesn't
  absorb the premium — e.g. by checking post-overlay TOM-state Sharpe
  vs mid-state Sharpe separation.

- **Bypassing absorption requires a portfolio-GEOMETRY change, not a
  signal change.** Candidates: binary entry/exit rotations (zero
  variance on out-of-market bars); stacks with variance-disjoint legs
  (managed-futures 3rd leg; FX carry); rotations on non-equity
  underlyings (VX futures roll). All remaining undefeated directions
  in BASE_MEMORY ({Option X, W, Y, Z}) change the geometry.

### Next direction after this failure

See BASE_MEMORY "Iter 023 candidates" — Option X (3rd uncorrelated
leg, probably synth managed-futures on TLT trend) is PRIMARY; Option
Z (seasonality as BINARY rotation, not weight modulator) is secondary
and can reuse iter 022's TOM flag logic.

---

## From iteration 023 — TSM-primary on 3-asset ETF basket with per-asset vol-target

Complete study: `studies/strategy_hunt_loop/iterations/023-2026-04-24-2007-time-series-trend-3etf/final_report.md`.

### What failed (do NOT re-test)

1. **Time-series trend-following (252-day lookback, 21-day skip,
   Moskowitz-Ooi-Pedersen 2012 canonical) on a 3-asset ETF basket
   {SPY/QQQ, TLT, GLD} with per-asset vol-targeting (10% per leg) and
   2.0× total leverage cap, as the PRIMARY portfolio mechanism (no
   blend overlay, no static base)** — Sharpe 0.55/0.55/0.61 vs
   benchmarks 0.68/0.90/0.955 on educational/spy/ndx (Δ −0.13/−0.35/
   −0.34 vs custom; Δ −0.43/−0.59/−0.58 vs iter 016). Score 28/100
   📉 NEAR_FAIL. Winner conditions 0/5. **Largest cross-dataset
   Sharpe regression in the entire hunt loop** (~2× iter 022's
   previous worst).

2. **The specific root cause: turnover cost dominates basket
   diversification.** Turnover was ~35/yr per leg × 3 legs × 2 bps
   per unit Δposition = ~2.1%/yr cost drag. iter 016's blend has
   ~6/yr × 2 legs × 2 bps = ~0.024%/yr. The two-orders-of-magnitude
   higher cost dominates the alpha that the small basket can
   theoretically deliver. Hurst-Ooi-Pedersen 2017's documented +1.0
   Sharpe for TSM was achieved on **67 markets globally**; with N=3
   effectively independent (correlations −0.31 to +0.21), the
   theoretical upper bound is sqrt(3)/sqrt(67) ≈ 21% of the documented
   edge — and even that small bound is dwarfed by the cost drag.

3. **Per-asset vol-target IS structurally different from σ²_port
   (kill #B and #C clear), but the geometry change does not translate
   to alpha at this scale.** Mechanically the strategy short bonds
   ~43-45% of bars (capturing the 2022 bond crash directionally),
   leverage cap binds only 67-75% of bars (not pinned), and the basket
   correlations are textbook (eq-bond −0.30, eq-gold +0.06, bond-gold
   +0.18). So the iter 023 hypothesis "per-asset vol-target escapes
   σ²_port absorption" is **mechanically validated but empirically
   refuted** — the geometry change happens, but the cost ceiling
   prevents any uplift.

4. **DSR p worst-ever**: 0.926 on spy_real, vs iter 021's 0.217 best.
   G6 bootstrap CI low is **negative** on all 3 datasets (−0.16 / −0.25
   / −0.24) — the realized Sharpe is statistically indistinguishable
   from a noise null. CAGR floor fails on 3/3 datasets (8% / 8% / 9%
   vs benchmark 11% / 15% / 19%).

### Don't re-test

- TSM (any lookback in {3-24 months}, any skip in {0-2 months}) on any
  ≤ 4-asset broad-asset-class ETF basket {equity, bond, gold,
  commodity} as the **primary** portfolio mechanism.
- Per-asset vol-targeting in {5%, 10%, 15%} per leg with leverage cap
  in {1.5×, 2.0×, 2.5×} on the same small-basket TSM construction.
- TSM with daily rebalance on small ETF baskets — turnover dominates.
  Weekly rebalance on TSM is also expected to fail (see iter 011 weekly
  blend lesson — daily required for vol-managed primitives, but a
  TSM-primary weekly grid is a separate untested point if anyone is
  curious).

### Don't close (path remains open)

- TSM with **slow signals + exit thresholds** to suppress turnover —
  EWMAC 64/256 (`[systematic_trading, p.118-119, ch.7] + p.282-284`)
  with hold-period constraints could drop turnover to ~5-8/yr/leg.
  Worth ONE iteration to verify whether iter 023's bottleneck was
  lookback-speed or basket-size; if slow signals also fail, the
  TSM-primary family is fully closed.
- TSM on **larger universes** (≥ 20 markets) — would require external
  data outside Tiingo cache (futures, currencies). Out of scope for
  this hunt loop given cache constraints.
- Cross-asset **carry** as primary mechanism (linear in yield
  differentials, ~3-6/yr turnover, uncorrelated with TSM per
  Asness-Moskowitz-Pedersen 2013 "Value and Momentum Everywhere"
  *JF* 68(3)).
- VRP-portfolio as primary mechanism (short puts/spreads + cash
  collateral + Tbill, premium ~3-4%/yr per Bondarenko 2014, monthly
  rebalance ~12/yr).

### Structural principles

- **Carver's Law of Active Management binds tightly on small N.** The
  Sharpe formula `SR ∝ sqrt(N_independent_bets × IR)` is not a soft
  rule of thumb; it is the operational ceiling. Going from 1 asset
  to 3 multiplies the diversification factor by sqrt(3) ≈ 1.73; going
  from 1 to 67 (Hurst-Ooi-Pedersen 2017) multiplies by sqrt(67) ≈
  8.19. The empirical TSM Sharpe edge scales with this factor.
  Plan for the basket size BEFORE picking the mechanism.

- **Cost analysis is a pre-commitment, not a post-hoc diagnostic.**
  Multiplying expected turnover × per-trade cost gives the
  cost-floor a strategy must clear. For a 35/yr/leg × 2 bps × 3 legs
  setup, that's 2.1%/yr the strategy must beat just to break even;
  with SPY annualised return ~14% post-2009, that's 15% of total
  return given up to costs. Any iteration whose pre-cost backtest
  Sharpe is +0.10 over benchmark but has ≥ 30/yr/leg turnover should
  be flagged as cost-dominated before running.

- **"Geometry change" is necessary but NOT sufficient for escaping
  iter 016 saturation.** iter 023 verified that breaking σ²_port
  feedback is achievable (per-asset vol-target works mechanically),
  but the alpha did not appear because a different binding constraint
  (cost vs basket-size diversification) became active. Forward
  iterations should map the binding constraint of each new geometry
  change BEFORE committing to implement it. The remaining "Option C
  / Z / V" candidates each have different binding constraints
  (carry: data narrowness; slow-EWMAC: same-basket diagnosis; VRP-
  primary: tail risk).

### Next direction after this failure

See BASE_MEMORY "Iter 024 candidates" — Option C (cross-asset carry
as primary) is PRIMARY post-iter-023; Option Z (slow EWMAC variants
to diagnose iter 023's lookback-speed contribution) is secondary and
cheap; Option V (VRP-primary portfolio) is tertiary.

---

## From iteration 025 — Slow-EWMAC trend on 6-asset long-only basket

Complete study: `studies/strategy_hunt_loop/iterations/025-2026-04-24-2059-slow-ewmac-multi-asset/final_report.md`.

### What failed (do NOT re-test)

1. **Slow-EWMAC trend (32:128 + 64:256 with FDM=1.10) + Carver no-trade
   buffer (10%) + portfolio-level vol-target (4%/asset) + long-only on a
   6-asset broad-asset-class ETF basket (SPY/QQQ + TLT + IEF + GLD + EFA
   + EEM)** — Sharpe 0.766/0.815/0.828 vs benchmarks 0.68/0.90/0.955;
   2/3 datasets REGRESS clearly (Δ frozen −0.085 spy_real, −0.127
   ndx_real). CAGR collapses to 9.13/9.97/10.20% vs 11.47/14.97/19.18%
   benchmark. Score 39/100 ❌ NEAR_FAIL. Winner conditions 0/5.

2. **The specific root cause: long-only constraint truncates trend
   premium asymmetrically.** Trend strategies harvest premium from BOTH
   directional legs (long-up + short-down). With long-only, the
   short-leg premium is forfeit entirely — the strategy goes flat on
   negative trends. Hurst-Ooi-Pedersen 2017 attribution suggests this
   loses ~50% of trend Sharpe. Combined with the 6-asset basket being
   too narrow for full diversification (Carver's FDM = 3.2 needs 10
   uncorrelated forecasts; at ρ ≈ 0.3 cross-asset correlation, effective
   N ≈ 4 vs the 67-market basket Hurst-Ooi-Pedersen used for SR ≈ 1.0),
   the realized Sharpe plateau is ~0.80 — well below post-GFC SPY/QQQ.

3. **MDD reduction is dramatic (17.3% on all 3 datasets vs benchmarks
   33-55%) but doesn't compensate.** The strategy is a defensive equity
   surrogate, not a Sharpe-edge candidate. Long-only multi-asset trend
   produces a low-leverage (gross 1.27 mean) low-vol portfolio that
   trades MDD reduction for CAGR loss — not what's needed to beat SPY 1×.

4. **Engine cleanest in hunt loop, but mechanism cannot escape the
   benchmark.** G3 walk-forward 7-8/8 on all datasets (best-ever WF);
   G6 bootstrap CI low > 0 on 3/3 (joins iter 016/021/024); G7 cross-lib
   parity 0.003-0.06 pp (cleanest engine ever in hunt loop). Robustness
   9/9 sub-windows positive (ties iter 013/024 record). Turnover
   1.56-1.61 / yr / leg — 22× lower than iter 023's 35/yr/leg. The
   mechanism IS doing what it's supposed to; it just doesn't beat
   post-2009 US equity beta.

### Don't re-test

- Slow-EWMAC (32:128 + 64:256 with FDM=1.10) on 6-asset broad-asset-class
  long-only ETF basket (SPY/QQQ + TLT + IEF + GLD + EFA + EEM) with
  portfolio-level vol-target and Carver no-trade buffer.
- Any further parameter sweep on this exact framework — the failure is
  structural (long-only + 6-asset diversification limit), not parametric.
  Variations of `target_vol_per_asset`, `no_trade_buffer_pct`, or
  `max_per_asset_leverage` would land at the same ~0.80 Sharpe plateau.
- Similar slow-trend frameworks on equivalent-narrow ETF baskets
  (5-7 assets, single asset class per leg, long-only): the same
  mechanism applies.

### Structural principles

- **Long-only constraint sacrifices ~50% of trend premium on directional
  strategies.** When a downtrend asset is forced to flat instead of
  short, the period's gain is set to zero rather than positive (from
  short PnL). On a 6-asset basket where ~30% of bars have at least one
  asset in negative trend, this aggregates to a meaningful Sharpe gap
  vs the long-short variant. Trend strategies that cannot short
  structurally cannot beat market beta in high-beta regimes (post-GFC
  US equity).

- **6-asset retail ETF basket cannot replicate Hurst-Ooi-Pedersen 67-
  market futures trend edge.** The diversification benefit scales with
  the effective independent count (N_eff ≈ N / (1 + (N-1)·ρ)). For a
  6-asset multi-asset-class basket at typical cross-correlation 0.3,
  N_eff ≈ 2.5 — far below the 50+ effective markets that produce
  +1.0 Sharpe in centennial trend studies. **Trend strategies on retail
  ETFs require either (a) a larger basket via fractional/levered
  futures access, (b) factor-rotation within asset class to amplify
  signal, OR (c) accept a lower Sharpe ceiling than the 1.0 referenced
  in literature.**

- **Engine cleanliness is necessary but not sufficient for beating the
  benchmark.** Iter 025 has the cleanest engine in the hunt loop on
  every diagnostic axis (G3, G6, G7, robustness) and still fails. This
  validates the discipline of the hunt loop's gates: a strategy can
  pass 6/7 gates uniformly, deliver 9/9 robustness, and have <0.06 pp
  cross-lib parity, and still not beat the benchmark Sharpe. The
  benchmark itself is the binding constraint, not the gate battery.

- **MDD-reduction is a separable axis from Sharpe-edge.** Iter 025's
  17% MDD vs benchmarks' 33-55% is a real, valuable property —
  but on the hunt loop's Sharpe-edge primary metric, it doesn't help.
  This suggests a SECONDARY axis worth tracking: "MDD-edge tier" for
  defensive strategies. Iter 025 would tier as 🥇 STRONG by MDD edge
  alone, even though it's NEAR_FAIL by Sharpe edge. Future iterations
  could be stratified by primary axis — Sharpe vs MDD vs CAGR.

### Next direction after this failure

See BASE_MEMORY "Iter 026 candidates":

- **Option V (VRP-primary)** — strongest candidate to break DSR ceiling
  at n=4278; +3-4%/yr Bondarenko premium with retail short-put / Tbill
  collateral structure.
- **Option LS (Long-SHORT slow-EWMAC)** — same mechanism as iter 025
  with shorts allowed; could recover the ~50% lost premium and lift
  Sharpe from 0.80 to ~1.05+.
- **Option C (EWMAC + Carry combo)** — 4 forecasts at FDM ≈ 1.5-1.8
  could lift Sharpe by +0.15-0.20 via signal diversification.

---

## From iteration 027 — Levered VRP-primary (`harvest_notional=3.5`)

Complete study: `studies/strategy_hunt_loop/iterations/027-2026-04-24-2144-levered-vrp-primary/final_report.md`.

### What the iteration resolved

Iter 027 tested whether linearly leveraging iter 026's VRP harvester
from `harvest_notional=1.0` to `3.5` would clear the structural CAGR
floor (iter 026 0/3 → projected 3/3) while preserving Sharpe edge and
DSR significance under the (theoretical) leverage-neutrality
assumption. Single pre-committed cfg `vrp_primary_h3_5_5_10_1m`,
n_trials 4279→4280.

Result: **PROMISING tier 74/100, 4/5 winner conditions** (DSR sole
gap, same as iter 026), **score regression 76→74**. CAGR floor cleared
3/3 datasets (11.43%/12.05%/16.82%) — the hypothesis-specific gain
was confirmed. But Sharpe regressed 0.31-0.37 across all 3 datasets
(edu 1.13→0.80, spy 1.28→0.91, ndx 1.37→1.06), violating Kill A's
≤0.05 tolerance, and DSR p collapsed (0.083→0.517 edu, 0.070→0.464
spy, 0.038→0.281 ndx). Sharpe edge gate misses on spy_real (+0.014 <
+0.10).

### Structural principle (do NOT re-test)

**Linear leverage on a constant-rf-collateral + harvest strategy is
NOT total-return-Sharpe-neutral.** Total-return Sharpe converges
toward `overlay_sharpe` as `harvest_notional → ∞`. Algebraic detail:

    Sharpe(r, N) = (rf_d + N × mean_h) / (N × σ_h) × √252
                = overlay_sharpe + rf_d / (N × σ_h) × √252

The first term is leverage-invariant; the second term is inversely
proportional to N (the rf bonus is diluted by leverage). At iter 026
N=1, the rf bonus added ~0.46 Sharpe to the educational dataset
(0.669 + 0.46 = 1.13). At iter 027 N=3.5, the rf bonus is diluted to
~0.13 (0.669 + 0.13 = 0.80). Same math holds across all 3 datasets
with consistent direction.

The TDD test `test_iter027_sharpe_invariant_under_leverage` correctly
verified that EXCESS-return Sharpe (after rf subtraction) IS leverage-
invariant. But the hunt-loop scoring uses TOTAL-return Sharpe (full
series, no rf subtraction), so the dilution bites in production
metrics.

### Don't re-test

- Higher `harvest_notional` (≥ 4.0) on the iter 026 base — would
  further dilute Sharpe; CAGR marginal benefit on already-cleared
  floors; MDD risk on educational; DSR worsens.
- Linear leverage on any constant-rf-collateral + harvest strategy
  expecting to preserve total-return Sharpe — same dilution applies
  structurally to carry, FX-basis, futures-basis variants where the
  collateral earns a fixed return and the harvest scales linearly.
- Tweaking iter 027's parameters (different N, slightly different
  strikes/DTE) to "rescue" — the rf-dilution boundary is structural.

### Structural principles

- **Total-return Sharpe ≠ excess-return Sharpe** when the strategy
  contains constant-yield components. Theory papers (Asness-Frazzini-
  Pedersen 2012's levered-low-vol argument) typically frame Sharpe in
  excess-return form, which IS leverage-invariant. Production scoring
  often uses total returns (no rf subtraction in `_sharpe()`), which
  has the rf-dilution effect under leverage. **Always check which
  Sharpe form your benchmark + scoring use** before pre-committing
  to leverage as a Sharpe-preserving operation.

- **Path to clear CAGR floor without losing Sharpe edge requires
  scaling the rf-yield component too.** Equivalently: the strategy
  must lever the harvest WITHOUT diluting the rf bonus. This needs
  margin-financing modeling (where margin posted reduces rf-earning
  capital — but realistic margin requirements are < 100%, so partial
  rf can be retained) OR a different mechanism architecture
  (compounding harvest at variable notional, or a multi-leg structure
  where multiple constant-yield components co-scale).

- **The +0.38-0.45 Sharpe edge of iter 026 was N=1-specific.** The
  intrinsic harvest skill (`overlay_sharpe`) is 0.67/0.77/0.93 — that
  is the asymptotic ceiling of any leveraged version. To produce a
  WINNER from this primitive, future iterations must lift
  `overlay_sharpe` itself: VIX filter (V-3), strike refinement (V-5),
  or composing with orthogonal return source (V-4 VRP+carry).

### Path forward (NOT dead — overlay_sharpe-lifting paths)

- **VIX-regime filter on iter 026 base** (V-3) — **TESTED iter 028 →
  CONSTANT-THRESHOLD VERSION CLOSED**; regime-aware variants still open.
- **VRP + Carry composite** (V-4). Adds non-equity-correlated return
  stream from iter 024 carry; composite σ² should drop modestly while
  total mean grows.
- **Strike refinement** (V-5). 5/15% wider OR 3/7% closer-to-ATM
  affects per-trade harvest geometry; pre-commit one variant.

---

## From iteration 028 — constant VIX<35 filter on iter 026 (V-3)

### What failed

- Pre-committed cfg `vrp_filtered_vix35_h1_5_10_1m`: iter 026 base +
  constant Sinclair p.217 `VIX<35` entry gate (at every natural roll
  bar, open only when raw VIX[i] < 35; otherwise hold T-bills until
  next eligible roll).
- **Kill A TRIGGERED** — Sharpe regressed > 0.05 vs iter 026 on 2/3
  datasets (spy −0.10, ndx −0.07). Educational *improved* (+0.13
  Sharpe, first-ever 7/7 gates + first-ever DSR pass p=0.029 on the
  longest 5100-bar window).
- Score 71 PROMISING (down from iter 026's 76). Drop entirely from
  DSR worst-p criterion: educational improved p (0.083 → 0.029), but
  spy/ndx worsened p (0.070 → 0.136 and 0.038 → 0.064); the score
  uses worst-p, which tracks the regression.
- Underlying mechanism: the filter's sign depends on **vol-regime
  persistence**, not absolute level. **Sustained** regimes
  (2008-Q4, VIX 50-80 for weeks) produce breach-prone rolls → filter
  skip is correct. **Transient spikes** (2020-Q1, 2022, 2024;
  VIX > 35 for days) resolve without breach within 21-DTE → the
  unfiltered iter 026 captures the IV mean-reversion premium; iter
  028's skip forgoes that premium. Post-GFC datasets contain mostly
  transient spikes, inverting the rule's empirical sign.

### Don't re-test

- **Any other constant VIX threshold (25, 30, 40, 50) on iter 026 base
  without regime-persistence conditioning.** The dimension that breaks
  is persistence, not level. Other constant levels will behave the
  same way on post-GFC data (transient spikes will be skipped either
  way; the level just tunes the frequency).
- **Combining iter 028's VIX filter with iter 027's leverage.** The
  leverage channel (rf-dilution) and filter channel (overlay_sharpe)
  are orthogonal, but combining them compounds damage on spy/ndx.
- **Symmetric two-sided VIX gates** (e.g. "only when VIX in [15, 35]")
  on iter 026 — the low-VIX tail of any such gate is a no-op on this
  sample (most bars have VIX < 35), so the test reduces to iter 028.

### Structural principles

- **Sinclair's pre-2010 rules are not universally transportable to
  post-GFC data.** The 2008-Q4 regime that p.217 implicitly addresses
  (sustained high-vol) is rare in 2010-2026; most post-GFC high-VIX
  events are mean-reverting spikes. Absolute-level VIX rules therefore
  have **regime-dependent sign** — they lift on samples containing
  sustained vol regimes and hurt on samples without.
- **Educational DSR floor of 0.083 is NOT a noise ceiling** — it
  dropped to 0.029 under the right filter (even an imperfect one).
  Multi-dataset DSR discrepancies are information about **regime
  composition**, not irreducible statistical barriers.
- **Path forward is regime-aware gates**, not constant thresholds.
  Specifically: conditions that distinguish *persistent* vol regimes
  from *transient* spikes.

### Path forward (NOT dead — regime-aware gate paths)

- ~~**R-1 VIX-persistence gate**~~ — TESTED in iter 029, **partial closure**.
  Configuration `vix_threshold=35, persistence_days=3` on iter 026
  base scored **71/100** (ties iter 028; Kill A triggered). DSR
  worst-p improved 27 % (0.136 → 0.100) but missed the 10-pt threshold
  by 0.0003 (would have been 76 STRONG). Closes that exact cfg only.
  See "From iteration 029" below for what it does NOT close.
- **R-2 VIX z-score gate** (filter when `(VIX − VIX_60d_mean) /
  VIX_60d_std > 2`). Relative-shock conditioning. **Now strongest
  candidate for WINNER post-iter-029** (orthogonal to absolute level
  AND persistence; should correctly classify 2011 Eurozone gradual
  buildups as benign while still catching GFC + 2020-Q1).
- **R-3 VIX > VXV term-structure gate** (`[volatility_trading, p.218]`).
  Front-month backwardation as sustained-stress signal.
- **R-1 + R-2 composite gate** (persistence AND z-score both fire).
  More selective; should reduce false positives on transient-but-
  clustered events.

---

## From iteration 029 — VIX-persistence VRP-primary (R-1)

Complete study: `studies/strategy_hunt_loop/iterations/029-2026-04-24-2236-vix-persistence-vrp-primary/final_report.md`.

### What failed (do NOT re-test exactly)

1. **`vrp_persistence_v35d3_h1_5_10_1m`** — single pre-committed cfg
   adding `persistence_days=3` to iter 028's `vix_threshold=35`. Score
   71/100 (ties iter 028); Kill A triggered (spy −0.052 vs iter 026,
   ndx −0.067). DSR worst-p 0.1002 (0.0003 above the 10-point award
   threshold). Educational reached new DSR record p=0.0251 (best ever
   on the longest 5100-bar window) but the score does not reflect this
   improvement because criterion 3 uses worst-p across datasets and
   spy_real fractionally missed the second tier.

2. **The structural finding is dataset-asymmetric**: the 3 hunt-loop
   datasets have qualitatively different high-VIX-event regime
   structures. educational (GFC-inclusive) is dominated by deeply-
   persistent vol; spy_real (post-GFC) is mixed transient/persistent
   (3/6 of iter 028's triggers were transient and correctly let
   through by R-1, but the other 3 are real persistent clusters);
   ndx_real (post-GFC tech) is all-clustered (4/4 of iter 028's
   triggers were already 3+ day persistent → R-1 = iter 028 here,
   contributing zero refinement). A single constant-parameter
   persistence gate cannot simultaneously optimize all 3 datasets.

### Don't re-test

- The exact cfg `vrp_persistence_v35d3_h1_5_10_1m` (already tested,
  PROMISING 71).
- Variations of `persistence_days` ∈ {3} × `vix_threshold` ∈ {35} on
  iter 026 base — single value in each dimension, no point sweeping.
- Combining iter 029 R-1 with iter 027 leverage — leverage channel
  (rf-dilution) is orthogonal but compounds spy/ndx Sharpe damage.

### What this DOES NOT close

- **Longer persistence horizons** (`persistence_days = 5, 7, 10`)
  with the same vix_threshold=35 — may reduce false positives on
  spy_real but the dataset-structure asymmetry still binds. Best-case
  educational unchanged or slight regression; spy maybe +0.01-0.03;
  ndx unchanged. Likely score 71-74 PROMISING.
- **Different threshold + persistence combinations**
  (`vix_threshold ∈ {30, 40}` × `persistence_days ∈ {3, 5}`).
  Bondarenko 2014 §3 implies level alone isn't the discriminator;
  these are likely also-ran refinements.
- **Orthogonal regime axes** (R-2 z-score; R-3 term-structure;
  realised-vol z) — the iter 029 dataset-structure finding suggests
  these are the *real* paths forward.
- **Composite gates** (persistence AND z-score, both must fire to
  skip; persistence AND term-structure backwardation).
- **Conditional strike adjustment** (V-5/V-6 — widen strikes during
  persistent high-VIX rather than skipping outright; capture some
  premium decay with reduced tail risk).
- **iter 026 unfiltered base** at N=1.0 — still STRONG #5 at score 76
  (the actual baseline being refined).

### Structural principles

- **The 3 hunt-loop datasets have different regime-structure
  signatures for high-VIX events**: GFC-inclusive samples are
  dominated by deeply-persistent (weeks at VIX > 50) vol regimes;
  post-GFC broad-market samples are mixed (some 1-2 day spikes that
  mean-revert profitably + some 3+ day clusters that breach); post-
  GFC tech samples have all-clustered high-VIX events (no transient
  triggers to begin with). A single constant-parameter regime gate
  optimizes at most 1-2 of the 3 datasets simultaneously.
- **DSR worst-p threshold is knife-edge categorical**: criterion 3
  awards 5 pts at p < 0.20, 10 pts at p < 0.10, 15 pts at p < 0.05.
  An iteration that improves p from 0.136 to 0.1002 (a 27 % relative
  improvement, materially closer to gates) gets the same 5 pts as if
  it had not improved at all. Future iterations should target
  worst-p < 0.10 or < 0.05 specifically, not just "improve DSR
  marginally".
- **Reducing-to-parent tests (TDD)** are critical for engine
  correctness. Iter 029's TDD spec includes
  `test_persistence_off_at_high_threshold_matches_iter026` (vacuous
  gate → iter 026) and `test_persistence_days_1_matches_iter028`
  (persistence horizon = 1 → iter 028); both passed at 1e-12. This
  pattern should be standard for any iteration that adds parameters
  to a parent engine.

---

## From iteration 030 — VIX z-score VRP-primary (R-2)

Complete study: `studies/strategy_hunt_loop/iterations/030-2026-04-24-2259-vix-zscore-vrp-primary/final_report.md`.

### What failed (do NOT re-test exactly)

1. **`vrp_z_z2_h1_5_10_1m`** — single pre-committed cfg with
   `z_window=60, z_threshold=2.0` z-score gate on iter 026 base.
   Score 71/100 PROMISING (ties iter 028/029); Kill A clean 2.6×
   threshold on ndx (Sharpe −0.131 vs iter 026); Kill B on
   educational (Sharpe −0.121 vs iter 028, below the −0.10 floor).
   spy_real cleared 7/7 gates AND DSR p=0.0345 (1st sub-0.05 spy
   DSR ever) — a genuine record — but the per-dataset trade-offs
   prevent winner status.

2. **THE STRUCTURAL CLOSURE — single-axis VIX-gate family on iter
   026 base**: three successive iterations (028 level / 029 level +
   persistence / 030 z-score) testing three orthogonal single-axis
   gates **all converge on score 71/100**, each producing sub-0.05
   DSR on a *different* dataset:

   | iter | gate | best DSR (ds) | regression cost |
   |---|---|---|---|
   | 028 | level (VIX < 35) | edu 0.029 | spy −0.10 / ndx −0.07 (Kill A) |
   | 029 | level + 3-day persistence | edu 0.025 | spy −0.05 / ndx −0.07 (Kill A 2bp) |
   | 030 | z-score (60d, 2σ) | **spy 0.035** | edu −0.13 / ndx −0.13 (Kill A+B) |

   No single-parameter, single-axis VIX gate can simultaneously
   optimize all 3 hunt-loop datasets because each dataset has a
   fundamentally different high-VIX regime structure (educational
   deeply-persistent GFC; spy_real innovation-shock-dominated
   post-GFC; ndx_real relatively-quiet post-GFC). The DSR record
   rotates by iteration — never simultaneously across datasets.

### Don't re-test

- The exact cfg `vrp_z_z2_h1_5_10_1m` (already tested, PROMISING 71).
- **Single-axis VIX-gate parameter sweeps** within
  {level threshold, persistence days, z-score threshold + window}
  on iter 026 base. Likely to produce another 71-tied result; the
  dataset-asymmetry binding dominates parameter choice within the
  family.
- **R-1+R-2 OR-composite** (skip if EITHER fires) — would aggregate
  the weaknesses (over-filter ndx; let edu sustained through);
  strictly worse than either alone.
- Combining iter 027 leverage with any single-axis or composite
  variant — the rf-dilution channel compounds spy/ndx Sharpe damage.

### What this DOES NOT close

- **R-1+R-2 AND-composite** (persistence AND z-score, BOTH must fire
  to skip) — the *intersection* should be very selective, only the
  genuinely worst regimes (GFC initial ramp where both fire;
  Mar-2020 where both fire). Strongest remaining VIX-gate
  candidate.
- **R-3 VIX > VXV term-structure gate** — qualitatively different
  signal source (market-derived expectation curve, not historical
  VIX distribution). VXV starts 2007.
- **Multi-feature learned regime classifiers** with non-VIX
  features (yield-curve regimes, macro indicators, options-skew
  z-score). Genuinely orthogonal axes.
- **Asset-conditional gates** (different threshold per dataset) —
  only acceptable with purged-CV calibration to avoid per-asset
  overfitting.
- **iter 026 unfiltered base at N=1.0** — still STRONG #5 at score 76
  (the actual baseline being refined).

### Structural principles

- **Single-axis VIX gates on VRP-primary cap at score 71/100**:
  three successive single-axis attempts converge at the same score
  with rotating DSR records. The single-axis family is exhausted on
  iter 026 base.
- **DSR worst-p must be < 0.05 simultaneously across all 3 datasets
  for criterion 3 to award full 15 pts**: the loop has now
  produced sub-0.05 DSR on each individual dataset (iter 026 ndx,
  iter 028/029 edu, iter 030 spy) but never simultaneously. The
  next breakthrough requires a gate axis that benefits all 3
  datasets, not just one — composite intersection or
  qualitatively different signal.
- **Z-score gates have an inherent regime-absorption blind spot**:
  60d rolling mean catches up to a sustained spike within ~3 months,
  after which the gate stops firing even though the underlying
  regime remains genuinely stressed. This makes z-score
  fundamentally unsuitable for *sustained* regime detection on its
  own. The level component (iter 028) is the proper signal for
  sustained regimes; z-score is the proper signal for *innovation*
  events. The two are complementary, not substitutes — motivating
  the AND-composite as iter 031's strongest path.
- **Reducing-to-parent tests (TDD) remain critical**: iter 030's
  TDD spec includes `test_zscore_threshold_inf_matches_iter026`
  (vacuous gate → iter 026 to 1e-12) and the precomputed-z-series
  architecture means any future iteration can swap in different
  signals (term structure, MOVE z, realised-vol z) without touching
  the state machine.

---

## From iteration 031 — VIX AND-composite (R-1 ∧ R-2) on iter 026 base

### What failed (partial closure: scored 76 STRONG, ties iter 026 ceiling)

- Specific cfg `vrp_and_v3p35_z2_h1_5_10_1m`: AND-composite (`VIX>=35` for 3 days AND `z(VIX,60)>=2`) on iter 026 base scores **76/100 STRONG, all 6 pre-committed kills CLEAN**. **First-ever iteration with all 3 datasets simultaneously below DSR p=0.10** (edu 0.054 / spy 0.070 / ndx 0.050) and ndx 7/7 + DSR PASS preserved (third sub-0.05 PASS ever, p=0.0499). Composite is **vacuous on spy_real** by construction (0 fires across 17y of post-2009 bars where the intersection is structurally empty: spy never had VIX≥35 for 3 days AND z≥2 simultaneously); fires exactly 4 times across 60y of cross-dataset bars (2008-10-03 GFC initial ramp + 2020-03-11 + 2011-08-12 US debt downgrade + 2020-03-19).
- Score TIES iter 026 at 76 (not a strict improvement) because the scoring rubric awards worst-p buckets, not DSR distribution tightness. Worst-p = spy 0.0699 (in [0.05, 0.10] bucket → 10 DSR pts, same as iter 026's worst-p 0.0828 in same bucket). Cross-dataset DSR distribution is *qualitatively* better but rubric blind to it.
- All 5 strict winner conditions check: 1=PASS (3/3 datasets beat bench+0.10 Sharpe); 2=PASS (cross-dataset gates met); 3=FAIL (worst-p 0.0699 > 0.05); 4=FAIL (CAGR floor 0/3, all ~5%/yr vs floors 9-15%); 5=PASS (MDD ceiling 3/3). Final winner_conditions_met=False, score=76 STRONG.

### Don't re-test

- Specific cfg `vrp_and_v3p35_z2_h1_5_10_1m` (closed at score 76; ties iter 026 ceiling).
- AND-composite at any other parameter triple `(vix_threshold, persistence_days, z_threshold)` on iter 026 base where `harvest_notional=1.0` — won't break the 76 ceiling because criterion 4 (CAGR floor 0/15) is structural to the T-bill-collateral architecture, regardless of gate parameters.
- AND-composite param sweeps (`vix_threshold ∈ {30, 35, 40}` × `persistence_days ∈ {3, 5}` × `z_threshold ∈ {1.5, 2.0, 2.5}` × `z_window ∈ {30, 60, 120}`) — would inflate PBO grid-level beyond iter 026's 0.69 floor (iter 006 killed exactly by this); even if a sweep finds a slightly better point, it cannot break the 76 ceiling without addressing the CAGR criterion.
- OR-composite of R-1 and R-2 — strictly worse than either alone (aggregates iter 028's edu over-fire and iter 030's ndx over-fire).
- AND-composite + linear leverage (iter 027 + iter 031) — rf-dilution channel kills the gain (iter 027 already showed this at 74); leverage is NOT the CAGR mechanism.

### Open paths (NOT closed by iter 031)

- **R-3 VIX > VXV term-structure gate** — qualitatively different signal source (market-derived expectation curve, not historical VIX distribution). VXV/VIX3M starts late 2007 → educational shortened to ~18y. `[volatility_trading, p.218, p.229]` (IVTS) + Carr-Wu 2009 §III. Cleanest sustained-vs-transient signal in the literature; iter 031's confirmation of the 76 ceiling promotes this from #2 to #1.
- **Multi-asset composition: iter 015 base + iter 031 VRP+composite overlay** — apply the iter 031 composite-gated VRP overlay onto iter 015's NTSX-style 0.9 SPY + 0.6 IEF static stack. Bond leg adds CAGR (criterion 4 was 0/15 on iter 031); static-vs-vol-target architecture validated at iter 015 STRONG 77. Combining iter 015 base + iter 031 overlay is the most direct path to breaking the 76 ceiling specifically by gaining CAGR floor points while preserving DSR distribution.
- **R-1+R-2+R-3 triple AND-composite** — three-axis intersection. Probably empty on most datasets but might informatively shift fire dates.
- **Composite gates with non-VIX features** (yield-curve regime, MOVE z-score, EBP credit cycle, EPU index) — qualitatively different signal sources.

### Structural principles

- **iter 026 single-asset VRP-primary family with literature-anchored 4-axis VIX gates is at score-rubric ceiling 76**: 5 iters total (026/028/029/030/031) span the full 4-axis exploration (no gate / level / level+persistence / z-score / level∧persistence∧z). All 5 capped at 76 (iter 026 + 031) or 71 (iter 028/029/030); none has broken the ceiling because criterion 4 (CAGR floor 0/15) is structural to harvest_notional=1.0 on T-bill collateral. Future iterations on this base will not exceed 76 without a CAGR mechanism.
- **AND-composite is the structurally cleanest gate within the iter 026 family**: it is the FIRST iteration ever to keep all 3 DSR p-values < 0.10 simultaneously. The score rubric doesn't reward this distribution-tightening property, but for any future "winner-conds-met"-aware analysis, the AND-composite cfg is the cleanest baseline.
- **Composite intersections are dramatically more selective than either single axis**: iter 030 z-only fires 19/17/16 rolls; iter 028 level-only fires 11/6/4 rolls; AND-composite fires 2/0/2 rolls — strictly more permissive than either alone, by ~10-20× reduction. The intersection cleanly maps to "literature-flagged regimes only" (Sinclair p.217-218 + Bondarenko 2014 §3 explicitly call out level AND persistence as joint warning signs).
- **Spy_real post-2009 has zero days where R-1 and R-2 agree**: for any winner that needs to clear strict winner conditions on spy_real, the composite axis provides no leverage over no-filter (composite vacuous on spy by construction). The spy gain in iter 030 came from R-2 alone catching VIX<35 innovation shocks; that gain is *unavailable* to any AND-composite that requires R-1 to fire. Spy DSR can only improve through (a) R-2 alone (iter 030 cfg, but Kill A on ndx), (b) a different signal axis (R-3, MOVE, etc.), or (c) a multi-asset architecture that adds Sharpe via an orthogonal sleeve.
- **Reducing-to-parent TDD tests scale to compositional gates**: iter 031's TDD specs include `test_andcomp_inf_vix_matches_iter026` (R-1 vacuous → iter 026 to 1e-12) AND `test_andcomp_inf_z_matches_iter026` (R-2 vacuous → iter 026 to 1e-12). Both pass. The pattern generalizes — any composite gate's TDD must include reduction tests for each axis individually, ensuring no axis introduces hidden state changes.

---

## How to add to this file

At end of each iteration that FAILED, append a section:

```markdown
## From iteration NNN — <short hypothesis>

### What failed
- (5-line summary)

### Don't re-test
- (exact patterns to avoid)

### Structural principles
- (1-2 lessons learned)
```

If the failure is a minor variation of an earlier dead-end, just
append a bullet to the relevant section instead of a full section.
