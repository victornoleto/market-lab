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
