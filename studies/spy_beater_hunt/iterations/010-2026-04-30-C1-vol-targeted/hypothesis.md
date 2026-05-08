# spy_beater_hunt iter 010 — Hypothesis — `C1-vol-targeted`

**Slug**: `C1-vol-targeted`
**Cumulative n_trials**: 32 (prior iters 001-009) → **35** (this iter adds 3)
**Target_total_iterations**: 50

---

## Pivot rationale

After iter 009 (`B2-hfea-kmlm`), all leveraged-barbell architectures
(B1 HFEA classical, B2 HFEA + KMLM crisis-alpha) are CLOSED via
KILL #24 + KILL #27 — both fail the spy_beater MDD bar (mean
67-72% on B1; 61-62% on B2 across the 15-25% KMLM dose). The
A2 TQQQ-track family is saturated at score 67 (iter 006/007),
and A1/A3 SPY-track is saturated at score 60-66 (iter 001-005).

Per iter 009 final_report.md "Where the score-90 path goes from
here", **C1 vol-targeted** is the only remaining Tier 1-2
architecture not yet tested. Its lever is **state-dependent
leverage scaling** (Carver canonical: `weight_t = target_vol /
realised_vol_t`), which is structurally distinct from:

- Static-weight barbells (B1, B2): fixed leverage regardless of regime
- Trend-following regime gates (A1, A2, A3): binary on/off per 200d SMA

This different control geometry **may unlock the 67-score ceiling**
because vol-targeting is **structurally conservative in stress**:
when realised vol spikes (2008 GFC ~50%, 2020 COVID ~45%, 2022
inflation ~25%), the weight on the leveraged underlying **drops
proportionally**, providing automatic defensive de-risking that
static barbells lack and trend gates only achieve via lagged signal.

If C1 also caps near 67, the architectural ceiling is confirmed
empirically across all four major control families (static-weight,
trend-gate, vol-target, dose-response on crisis-alpha) and the
**spy_beater rubric is architecturally unreachable** within the
2-dataset gross-of-tax framework — IMPOSSIBILITY_RESULT triggers
iter 011+ fallback.

---

## Hypothesis

### Primary: H₁

**At least one of the 3 vol-target configs clears all 3 strict bars**
on the (lh_56y, spy_real) framework: CAGR ≥ 11.21%, MDD ≤ 55.17%,
gates ≥ 5/5 cross-met. Most defensive variant `c1_vt20_sso` is the
strongest candidate to clear MDD bar; most aggressive `c1_vt25_upro`
is the strongest CAGR candidate.

### Secondary: H₂

**Vol-targeting lifts mean Sharpe vs static barbells**. Iter 008
b1 HFEA Sharpe mean 0.74; iter 009 b2 HFEA+KMLM 0.77; iter 006
a6 TQQQ-track 0.76. Carver canonical `[systematic_trading, ch.10]`
predicts vol-targeting captures Sharpe by reducing the long-tail
dispersion of returns — strategy with mean Sharpe 0.85+ becomes
plausible, lifting score on criterion 5 (currently 2 pts at mean
Sharpe ~0.77 in anchor 0.5-2.0).

### Tertiary: H₃

**Target_vol dose-response is monotonic positive on CAGR** through
the tested 20→22→25% range. Higher target_vol means higher mean
weight on underlying (e.g., target 25% / 3× UPRO factor / SPY
realised vol 16% → mean weight ~0.52 → 1.56× SPY effective
exposure), which translates to higher CAGR with non-linear MDD
penalty. Inflection point unknown.

---

## Configs

3 configs, all use:
- `signal_ticker`: SPYSIM (vol estimate from raw SPY returns)
- `vol_window`: 60 trading days
- `vol_lag_days`: 1 (T+1, no peek-ahead)
- `weight_min`: 0.0
- `weight_max`: 1.0
- `cash_weights`: {IEFSIM: 1.0}

| name | target_vol | underlying | factor | mean weight (~16% SPY vol) | mean SPY-equiv exposure |
|------|-----------:|------------|-------:|---------------------------:|------------------------:|
| `c1_vt20_sso` | 20% | SSOSIM | 2 | 0.625 | ~1.25× |
| `c1_vt22_upro` | 22% | UPROSIM | 3 | 0.458 | ~1.375× |
| `c1_vt25_upro` | 25% | UPROSIM | 3 | 0.521 | ~1.56× |

Naming convention: `c{iter-letter}_vt{target_vol_pct}_{underlying-suffix}`.

Mathematical intuition: SPY long-run annualized vol ≈ 16%. Target
above 16% means the strategy is on average more than 1× SPY
exposed (CAGR > SPY in mean-vol regimes). When realised vol spikes
to 30-50% (stress), weights collapse, cutting drawdowns
automatically.

---

## Pre-committed KILL conditions

KILL conditions are evaluated AFTER metrics are computed. If any
fires, that **direction** is closed for the rest of the hunt.

### KILL #30 — Vol-target Sharpe < a1_lrs_split baseline (0.66)

**Condition**: best vol-target config Sharpe (mean across datasets)
< 0.66 (iter 001 a1_lrs_split baseline).
**Implication**: vol-targeting adds noise without informational
edge over Gayed regime gating; the realised-vol signal is too
backward-looking to time leverage usefully.
**Direction effect**: C1 vol-targeted CLOSED → IMPOSSIBILITY_RESULT
trigger.

### KILL #31 — Most conservative variant fails MDD bar

**Condition**: `c1_vt20_sso` (most defensive, 1.25× SPY effective)
spy_real MDD > 55% bar.
**Implication**: vol-targeting CANNOT clear MDD bar even at
conservative target_vol; the realised-vol signal lags fast
crashes (60d window misses March 2020 / Sep 2008 inflection by
weeks).
**Direction effect**: C1 vol-targeted CLOSED at conservative end
→ no path forward in this architecture.

### KILL #32 — Sharpe regression with target_vol dose

**Condition**: monotonic NEGATIVE Sharpe through 20→22→25% target on
**both** datasets, i.e., `c1_vt20_sso` Sharpe > `c1_vt22_upro` Sharpe
> `c1_vt25_upro` Sharpe in lh_56y AND spy_real.
**Implication**: high-target dose breaks the strategy — leverage is
too high vs realised-vol estimate's accuracy at fast inflection
points; SSO @ 20% is the structural sweet spot.
**Direction effect**: dose-response CLOSED at upper end; subsequent
iters could explore lower targets (15-18%) but expected CAGR drag
makes this subordinate to Tier 1 candidates.

---

## Expected outcomes

**Best case** (H₁ confirmed): one config clears all 3 bars with
score 65-75. Most likely candidate: `c1_vt22_upro` (mid-target,
mid-leverage) — CAGR ~14-15%, MDD ~40-50%, Sharpe ~0.80-0.85.
Score budget: CAGR 21-25 + MDD 8-12 + Gates 11-13 + DSR 10 +
Sharpe 2-3 + Robustness 10 = 62-72. **Beats incumbent 67**.

**Likely case** (H₁ partial): all 3 configs PASS bars 3/3 but
score caps at 65-70 — TIE iter 006/007 closest-to-winner but not
exceed. Confirms architectural ceiling at 67. Direction CLOSED
empirically.

**Worst case** (KILL #30 OR #31 fires): vol-targeting structurally
inferior to trend-gating in this dataset framework. Direction
CLOSED. Hunt pivots to IMPOSSIBILITY_RESULT (iter 011 wraps up).

---

## INCOMPLETE flags (pre-iter)

- **Vol estimate window**: 60d realised vol on SPY signal is the
  standard but not the only choice. EWMA with span 30-60 (Carver
  default) might be more responsive; we chose simple rolling for
  consistency with iter 001's gate window simplicity. Sensitivity
  to this not tested in iter 010.
- **Underlying factor approximation**: SSO factor=2.0, UPRO factor=3.0
  are nominal LETF leverage factors. Real LETFs have daily-reset
  decay (~0.5-1.5%/y for SSO, 1.5-3.0%/y for UPRO) which means
  effective factor over multi-month windows is slightly less than
  nominal. Our synth captures decay (UPROSIM in cache) but the
  vol-target weight formula uses nominal factor for translation.
  Net effect: actual SPY-equivalent exposure is 5-10% lower than
  computed from `target / (factor × realised_vol)`.
- **2008 GFC stress**: lh_56y captures 2008 fully via SPYSIM synth
  (1986+); spy_real Tiingo 2003+ also captures it via real SPY.
  Both datasets test the GFC-specific failure mode for vol-target
  (60d window lagging the Sep 2008 inflection by ~1 month).
- **Cumulative n_trials growth**: cumulative 35 with 3 configs.
  DSR penalty grows ln(n)/√n; at n=35, threshold sharpens by
  ~3% vs n=32. Worst-case still passes p<0.05 with current
  Sharpe headroom.
- **PBO N=3 warning expected**: CSCV statistically unstable at
  N<4. PBO 0.85-0.95 expected; informative only here. Cumulative
  cross-iter grid carries the anti-overfit weight.

---

## Citations

- `[systematic_trading, ch.10]` Carver — vol-targeting canonical:
  `position_size = target_vol / realised_vol`. Validated in
  hedge fund / commodity / FX context; under-tested on equity
  LETFs in 1986+ regime.
- `[advances_fin_ml, p.31-34]` factor framework — vol as a state
  variable distinct from trend signal; vol-target captures the
  vol-of-vol factor that Gayed gate does not.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials=35;
  threshold p < 0.05 with growing penalty.
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking —
  vol-target on leveraged underlying achieves stacking-equivalent
  effective exposure via dynamic weight rather than static
  unhedged notional.
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LETF decay
  rationale — informs underlying choice (SSO vs UPRO) and decay
  cost expectation in mean-leverage scenarios.
- HFEA Bogleheads 2019 + iter 008/009 falsification — leveraged-
  barbell structurally subordinate; vol-target may be the
  surviving Tier 1-2 architecture.
