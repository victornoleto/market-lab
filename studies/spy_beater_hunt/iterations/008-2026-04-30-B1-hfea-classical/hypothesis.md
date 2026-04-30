# spy_beater_hunt iter 008 — Hypothesis — `B1-hfea-classical`

**Slug**: `B1-hfea-classical`
**Created**: 2026-04-30
**Cumulative n_trials**: prior 26 + 3 this iter = **29**
**Continuation rationale**: per iter 007 final_report "Suggested iter 008",
the A2 TQQQ-track is **structurally saturated near 67** within the
CAGR-anchored rubric (KMLM/TLT extensions trade CAGR ↔ MDD at ~1:1
within integer-pt scoring; Sharpe lift gets penalized by anchor range).
To break past 75, this iter pivots to a **different return/risk geometry**:
the HFEA leveraged barbell (UPRO + TMF). Pre-2022 backtests claim
~22% CAGR + ~30% MDD; the 2022 inflation regime is the known
falsifiability test (TMF −70% same year as UPRO −50%).

This is the **first non-LRS direction** in spy_beater_hunt — it has no
regime gate, just static rebalanced weights. If B1 caps near ~75 too,
iter 009 pivots to **C1 vol-targeted** (different geometry again).

---

## Hypothesis

**H₁ (HFEA classical clears the 3 strict bars)**: `b1_classic_5545`
(55% UPRO + 45% TMF) achieves mean CAGR ≥ 11.21% AND mean MDD ≤ 55.17%
AND ≥ 5/5 cross-met gates across `(lh_56y, spy_real)`. Pre-2022
backtests show CAGR ~22% / MDD ~30% in clean regimes; the long-history
windows here include 2022's HFEA stress (TMF −70% / UPRO −50% concurrent)
which deepens MDD considerably but should not break the strict bars
on a 40y mean basis since pre-2022 alpha was material.

**H₂ (UPRO-weight monotonic dose-response)**: Pushing UPRO from 50% → 55%
→ 60% (with TMF complement 50% → 45% → 40%) lifts CAGR monotonically
AND raises MDD monotonically. The 50/50 variant tests whether
TMF-heavy is too 2022-fragile; the 60/40 modern variant tests
whether reducing TMF lifts CAGR enough to clear the 13.80% Bogleheads
target. We expect the dose-response to be roughly linear in clean
regimes (correlation matters less when both legs are lev'd).

**H₃ (binding constraint is post-2022 spy_real MDD)**: spy_real has the
2022 inflation drawdown explicitly; lh_56y has the 1994 bond bear and
the 2008 GFC equity tail. The driving constraint should be spy_real
MDD post-2022, not lh_56y. If true, future B2 variants (HFEA + KMLM
crisis-alpha) become the natural extension.

Citation: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed
documents leveraged-barbell logic but warns LETF decay during
sideways/bear markets compounds; HFEA Bogleheads 2019 thread for
canonical 55/45 weighting; `[risk_parity, ch.5, p.10]` Carlson on
capital-efficient stacking — UPRO + TMF is the leveraged extension
of the classic 60/40, and `[advances_fin_ml, p.31-34]` factor
framework — leveraged duration is a distinct factor exposure
(rates-falling beta) versus the equity-momentum bias of A1-A3 LRS
strategies.

---

## Configs (3, naming `b1_*`)

### 1. `b1_classic_5545` — canonical Bogleheads HFEA (55/45)

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.55,
    "TMFSIM": 0.45
  }
}
```

Tests: H₁, H₂. Canonical HFEA per Bogleheads 2019. 55% × 3× SPY +
45% × 3× LTT = 165% equity + 135% duration notional.

### 2. `b1_modern_6040` — modern HFEA (60/40, equity-tilted)

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.60,
    "TMFSIM": 0.40
  }
}
```

Tests: H₂ extension. Equity-tilted variant; reduces TMF exposure
which is 2022's worst leg. Should produce higher CAGR + higher MDD
than 5545 (linear interpolation between UPRO standalone and 5050).

### 3. `b1_balanced_5050` — balanced HFEA (50/50, duration-tilted)

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.50,
    "TMFSIM": 0.50
  }
}
```

Tests: H₂. More TMF exposure — historically lower MDD pre-2022
(more uncorrelated stack) but worst-case in 2022. Useful for
mapping the dose-response curve at 5pp spacing around the canonical
55/45 anchor.

---

## Pre-committed KILL conditions

KILL numbering continues from #23 (last used in iter 007). New: #24, #25, #26.

### KILL #6 (standing — CAGR floor)

If best config across the iter has CAGR mean < 11.21% (the spy_beater
bar), the strategy class is structurally subordinate to SPY buy-hold.
Direction CLOSED.

**Citation**: `WINNER_AND_RANKING.md` Bar 1.

### KILL #24 — HFEA 2022-stress MDD blow-up

If `b1_classic_5545` MDD on **spy_real** > 65%, the 2022 inflation
regime breaks the leveraged-barbell thesis structurally. Direction
B1 CLOSED at canonical weights; iter 009 pivots to **B2 HFEA + KMLM
crisis-alpha** (the literature-aware response to the 2022 weakness)
or **C1 vol-targeted** (different geometry).

**Rationale**: Bogleheads simulator + multiple academic post-mortems
agree that HFEA's worst 12-month period was 2022 (TMF down ~−70% with
UPRO concurrently down ~−50%, peak-to-trough combined ~60-65%).
A measured MDD > 65% on spy_real suggests the synth captures
this regime correctly and the drawdown is structural — gate G3
(walk-forward MDD < 25% per window) is also likely to fail.

### KILL #25 — TMFSIM synth no-free-lunch (standalone Sharpe out of [0, 1.0])

If TMFSIM standalone Sharpe (post-1986) is < 0 OR > 1.0, the synth
is broken. The synth must capture realistic 3× LTT behaviour: positive
nominal return over 40+ years (interest rate cycle compensation), but
substantially worse Sharpe than the 1× TLT (because the 3× decay is
real and 2022 was catastrophic).

**Verified pre-iter** (smoke check): TMF 1986+ standalone Sharpe ≈ 0.49
(passes [0, 1.0] band). KILL #25 not expected to fire.

**Rationale**: `[advances_fin_ml, p.31-34]` no-free-lunch — synthetic
LETFs at 3× leverage with daily reset must show Sharpe degradation
versus their 1× underlying due to vol drag. A standalone Sharpe > 1.0
on a 3× LETF is a synth bug (not realistic) and would invalidate
the iter.

### KILL #26 — HFEA dose-response non-monotonic AND inflection at 55/45

If `b1_modern_6040` Sharpe < `b1_classic_5545` Sharpe AND
`b1_balanced_5050` Sharpe < `b1_classic_5545` Sharpe on BOTH datasets,
the HFEA dose-response inflects at 55/45 (canonical is locally
optimal). Sub-direction B1 ceiling is the canonical config; future
iters should pivot to B2 (add crisis-alpha) rather than re-sweep
UPRO weight.

**Rationale**: classic Bogleheads claim is that 55/45 is the
risk-parity optimum at the leveraged barbell — both legs contribute
similar dollar volatility. If both 50/50 (more TMF) AND 60/40 (more
UPRO) fall below 55/45 on Sharpe, the rubric structurally caps B1
at canonical, supporting the documented HFEA literature claim.

---

## Expected outcomes

| config             | expected CAGR mean | expected MDD mean | expected Sharpe |
|--------------------|-------------------:|------------------:|----------------:|
| b1_classic_5545    | 14-18%             | 45-58%            | 0.55-0.75       |
| b1_modern_6040     | 16-20%             | 50-62%            | 0.55-0.72       |
| b1_balanced_5050   | 12-16%             | 42-55%            | 0.55-0.78       |

**Score outlook** (selected ≈ b1_classic_5545 if H₂ holds at 55/45):
- 1. CAGR 30 × clamp((0.16 − 0.05)/0.15, 0, 1) ≈ 22 pts (similar to iter 007)
- 2. MDD 20 × clamp((0.50 − 0.50)/0.40, 0, 1) ≈ 0-5 pts (HFEA's known weakness)
- 3. Gates likely 10-13 pts (G3 walk-forward MDD<25% probably fails for HFEA in 2022 window)
- 4. DSR n=29 worst p estimated < 0.01 → 10 pts
- 5. Sharpe ≈ 0.65 → 1-2 pts
- 6. Robustness ≈ 6-8 pts (HFEA pre-2022 strong; 2022 single-window erodes 5y pass-rate materially)
- 7. Extra 0
- **Total expected**: ~50-65

**Score-90 path**: structurally improbable in this iter. HFEA's
known fingerprint is high CAGR, high MDD — perfect inverse of
spy_beater's CAGR/MDD-balanced rubric. Best-case ~65-70 (similar
to current closest-to-winner iter 006 at 67); worst-case ~45-55
(KILL #24 fires + structural fail).

This iter's value is **diagnostic**: it maps the leveraged-barbell
geometry against the rubric, sets up B2 (HFEA + KMLM) and C1
(vol-target) directions for iter 009-010, and either confirms or
falsifies the Bogleheads 55/45 risk-parity claim within our anti-overfit
gate framework.

---

## INCOMPLETE flags

1. **TMFSIM synth approximation**: real TMF (Direxion Daily 20+ Year
   Treasury Bull 3×) has variable daily-reset decay depending on
   realised vol. Our synth uses constant 1.5%/y annualised decay
   (`tmf_synth_returns_from_cache`). In high-vol regimes (2022 had
   TLT vol ~22% annualised vs typical 12-15%) real decay is closer
   to 3-5%/y; our synth understates the 2022 drag. The MDD measurement
   on spy_real may underestimate true 2022 HFEA pain by 5-10pp.

2. **TLT cache pre-1980 backfill**: TLTSIM cache starts 1962 but the
   1962-1986 bars are testfolio's index synth (LTT yield curve
   reconstruction). Within `lh_56y` (1986+), this backfill is
   irrelevant. Within potential extensions to longer windows it
   matters — out of scope this iter.

3. **UPROSIM cache pre-2009**: real UPRO (ProShares UltraPro S&P 500)
   inception 2009-06; pre-2009 is testfolio's SPY × 3 with daily
   reset decay synth. The 2008 GFC stress test on lh_56y is fully
   synthetic — no real 3× LETF traded the actual GFC.

4. **No transaction costs / no quarterly rebalance friction**: HFEA
   classical assumes quarterly rebalance per Bogleheads thread; we
   use daily rebalance (instantaneous). Rebalance-tax drag on real
   HFEA is small (~0.1-0.3%/y) but real-world 4× annual rebalance
   has spread + slippage cost.

5. **PBO at N=3 (warning emitted)**: CSCV statistically unstable
   below N=4. PBO informative-only at this iter level; cumulative
   n_trials=29 cross-iter grid carries the anti-overfit weight
   (DSR worst p target < 0.05).

6. **2022 stress regime is the falsifiability test**: spy_real
   contains 2022 explicitly (Tiingo daily 2003+); lh_56y synth also
   captures it. If KILL #24 fires (MDD > 65% on spy_real), B1 is
   architecturally subordinate to LRS-style regime-gated strategies.

---

## Next-iter sketch (depending on outcome)

- **If `b1_classic_5545` scores ≥ 67 (matches or beats iter 006/007 closest)**:
  iter 009 extends with **B2 HFEA + KMLM crisis-alpha** (50% UPRO +
  35% TMF + 15% KMLM) to test whether MF-on-top hedges 2022 without
  CAGR drag.
- **If KILL #24 fires (HFEA blow-up on spy_real)**: iter 009 pivots
  directly to **C1 vol-targeted** (1.5× SPY when 60d vol < 15%, else
  0.5× → IEF). Different geometry: dynamic leverage, no TMF.
- **If KILL #26 fires (HFEA monotonic regression at 55/45)**: future
  B-direction iters lock 55/45 as canonical anchor; pivot to B2
  variants (add KMLM/TLT crisis-alpha) without re-sweeping UPRO weight.
- **If all 3 configs FAIL strict bars (CAGR mean OR MDD mean fails)**:
  B1 direction CLOSED entirely; iter 009 pivots to **C1 vol-targeted**
  or **D1 concentrated growth + monthly momentum gate**.
- **If `b1_classic_5545` scores 70+ AND winner_conditions_met TRUE**:
  iter 009 sensitivity sweep around 55/45 (add 52/48 + 58/42 + KMLM
  variants).

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — LETF decay
  rationale; even with regime gate, leveraged duration is fragile in
  rising-rate regimes (2022).
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking;
  HFEA is the leveraged extension of stacking to 3× via UPRO+TMF.
- HFEA Bogleheads 2019 — canonical 55/45 weighting; documented stress
  test in 2022 inflation regime.
- `[advances_fin_ml, p.31-34]` factor framework — leveraged duration
  (TMF) is a distinct factor exposure (rates-falling beta) vs. equity
  momentum (UPRO).
- `[advances_fin_ml, p.222-223]` DSR with cumulative n_trials=29.
- `[advances_fin_ml, p.208-211]` PBO via CSCV (informative at N=3).
- `[advances_fin_ml, p.196-202]` bootstrap CI 99.9% low > 0.
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha — flagged as
  natural extension to B1 if iter 008 shows 2022 is the binding
  constraint (sets up B2 in iter 009).
- studies/long_term_portfolio/synths.py `tmf_synth_returns` —
  3× TLT − 1.5%/y daily-reset decay (validated by 3 existing tests,
  standalone Sharpe 1986+ ≈ 0.49, passes KILL #25 [0, 1.0] band).
