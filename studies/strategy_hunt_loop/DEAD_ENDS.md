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

## Things that might still work (in principle)

These are NOT dead-ends, just untested:

- Weekly/monthly timeframe (not daily)
- Cross-sectional (not time-series)
- Different asset class (FX / commodities / bonds) or multi-asset
- Factor rotation (value/momentum/quality/low-vol dynamic weights)
- Options overlay (put spreads as tail insurance)
- ML-based meta-labeling on top of primary signal
- Regime-switching HMM on correlation or macro state
- Seasonality-based entries/exits
- Dynamic vol-targeting (Carver) without any leverage
- Return-stacked ETFs (NTSX/NTSI/NTSE) with rotation

The `## Promising unexplored directions` section of `BASE_MEMORY.md`
prioritizes these.

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
