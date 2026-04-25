# Iteration 038 — Final Report

## Verdict

🥇 **STRONG** (score **79/100**, winner_conditions_met=False, **1/7 KILLS — Kill C only**)

VIX-level regime gating (VIX_{t−1} < 20 → 1.70× total leverage; ≥ 20 →
1.00×) on iter 037's 0.60 SPY + 0.45 IEF + 0.45 GLD base **ties iter
037's score 79 STRONG with strict-MDD-dominant deltas across all three
datasets** but fails to break the static-stack DSR ceiling. Kill C (DSR
worst-p > 0.10) fired alone — the regime gate barely budged DSR
worst-p (iter 037: 0.222 → iter 038: 0.204, improvement 0.018 — still
above the 0.20 partial-credit threshold). All other 6 kills clean,
robustness 9/9, and **MDD improved by −8/−4/−4 pp on edu/spy/ndx vs
iter 037** while leverage averaged 1.46-1.49× (≈ iter 037's 1.50× — pure
regime-timing experiment per Moreira-Muir 2017).

This iteration is the **second consecutive ceiling tie at 79** (iter
037 broke 77→79 via 3-leg preserved-lev architecture; iter 038 ties at
79 via VIX-regime gate on the same 3-leg base). The combined evidence
across iter 037 and iter 038 hardens the diagnosis: **the static-stack
family is DSR-bound at ≈ 79 across leverage modulators that hold
average exposure constant**. Both Sharpe and DSR worst-p are tightly
clustered in the 0.98-1.17 / 0.17-0.22 ranges regardless of the lever
mechanism (preserved 3-leg vs preserved-on-average regime-gated). The
DSR penalty at n_trials = 4303 needs Sharpe ≈ 1.30 cross-dataset —
which neither preserved 3-leg, regime-gated 3-leg, nor incremental
weight perturbations can deliver within the static-stack family.

The MDD improvement is **real and economically meaningful** but the
loop's scoring rubric does not pay for additional MDD margin once the
"≤ benchmark + 5pp" threshold is cleared (iter 037 already maxed
criterion 5 at 15/15). For an investor whose objective includes
absolute drawdown control, iter 038 is **mechanically dominant** over
iter 037; for a pure Sharpe-edge / DSR-strict objective, iter 038 is a
wash.

---

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen) | CAGR (Δ frozen) | MDD (Δ frozen) | gates |
|---|---|---|---|---|
| educational | 0.9975 (+0.318 vs 0.68) | 12.42% (+0.95pp vs 11.47%) | **25.11%** (−30.03pp vs 55.14%) | **6/7** |
| spy_real | 1.1049 (+0.205 vs 0.90) | 13.22% (−1.75pp vs 14.97%) | **21.60%** (−12.10pp vs 33.70%) | **6/7** |
| ndx_real | 1.1490 (+0.194 vs 0.955) | 15.69% (−3.49pp vs 19.18%) | **28.63%** (−6.49pp vs 35.12%) | **6/7** |

| dataset | Δ vs iter 037 (3-leg preserved-lev 1.5×) |
|---|---|
| edu Sharpe | **+0.0148** ✓ (slight uplift) |
| spy Sharpe | **−0.0488** (just shy of −0.05 Kill A threshold) |
| ndx Sharpe | **−0.0247** (mild regression) |
| edu CAGR | **−1.74pp** (lower avg lev 1.46 vs 1.50) |
| spy CAGR | **−2.31pp** |
| ndx CAGR | **−2.07pp** |
| edu MDD | **−8.22pp** ✓ (much better) |
| spy MDD | **−3.64pp** ✓ |
| ndx MDD | **−3.65pp** ✓ |
| edu DSR | **−0.0179** ✓ (small improvement, 0.222 → 0.204) |
| spy DSR | +0.0504 (regression, 0.144 → 0.195) |
| ndx DSR | +0.0249 (regression, 0.146 → 0.171) |

DSR profile is QUALITATIVELY different from iter 037: edu DSR improved
modestly (the regime gate avoids the long 2008 high-vol episode where
iter 037's static stack accumulated drag), while spy/ndx DSR regressed
slightly because Sharpe dropped 0.025-0.049 there and the regime gate
is most active during the 2018-2020-2022 stress window (which post-GFC
samples weight heavily). The worst-p (0.204) is now from spy_real's
0.195 in some sense competing with edu's 0.204; concretely the edu
window contains the longest VIX>20 episode (2008-Q4 to 2009-Q3) where
the gate has the most impact on tail returns. Frozen-benchmark Sharpe
edges remain large: 3/3 datasets ≥ +0.10, criterion 1 maxes at 25/25.

**MDD profile is the cleanest the loop has ever observed for any STRONG
candidate**: 25.11% / 21.60% / 28.63% — better than SPY/QQQ buy-and-hold
on every dataset by 6-30 pp. Tail control is the unambiguous win of
this iteration.

DSR worst-p of 0.2038 is **the second-lowest static-stack DSR
worst-p ever** (after iter 037's 0.222 → iter 038's 0.204):

- iter 015 (2-leg IEF, 1.5×) = 0.548
- iter 035 (2-leg GLD, 1.5×) = 0.344
- iter 036 (3-leg additive 1.8×) = 0.311
- iter 037 (3-leg preserved-lev 1.5×) = **0.222** ← ceiling break
- iter 038 (regime-gated 3-leg 1.46-1.49×) = **0.204** ← marginal advance

The trajectory is asymptotic: 037→038 = −0.018 (8% relative). The
asymptotic limit at this n_trials is around p ≈ 0.18-0.20 for
static-stack-class architectures at Sharpe 0.98-1.20.

---

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | edu/spy/ndx all beat frozen bench by ≥ +0.10 (Δ +0.318/+0.205/+0.194); 3/3 includes the +5 cross-dataset bonus |
| 2 Gates | **19** | 25 | edu 6/7 → 5 pts (5+1); spy 6/7 → 5 pts (4+2); ndx 6/7 → 5 pts (4+2); cross-ds bonus +4 |
| 3 DSR | **0** | 15 | worst-p **0.2038** (educational); spy 0.1949, ndx 0.1707 — all 3 still > 0.05; bucket 0/15 (≥ 0.20). Knife-edge — 0.04 above the partial-credit 0.20 threshold |
| 4 CAGR floor | **15** | 15 | all 3 datasets ≥ 0.8 × frozen CAGR benchmark (12.42/13.22/15.69% all comfortably above 9.18/11.98/15.35%) |
| 5 MDD ceiling | **15** | 15 | edu 25.11% ≤ 60.14% ✓; spy 21.60% ≤ 38.70% ✓; ndx 28.63% ≤ 40.12% ✓ — by largest margin of any iter (35/17/12 pp) |
| 6 Robustness bonus | **5** | 5 | 9/9 sub-windows Sharpe > 0 across 3 datasets |
| **total** | **79** | **100** + 5 | tier: **🥇 STRONG** |

Strict winner conditions: **4/5 met** (same shape as iter 037):

1. Sharpe edge ≥ +0.10 on ≥ 2 ds: ✓ (3/3)
2. Gates cross-ds (edu ≥5, spy/ndx ≥4): ✓ (6/6/6)
3. DSR p < 0.05 (worst): ✗ (0.2038)
4. CAGR ≥ 0.8×bench on ≥ 2 ds: ✓ (3/3)
5. MDD ≤ bench+5pp on ≥ 2 ds: ✓ (3/3)

Only **DSR fails** the strict 0.05 threshold (same as iter 037).
Score 79 + winner_conds=False → **STRONG** (≥ 75, < 90).

Pre-committed kills (iter 038 hypothesis): **1/7 fired** — Kill C (DSR
worst-p > 0.10). Specifically:

- Kill A (Sharpe Δ vs iter 037 < −0.05 on ≥ 2 ds): clean (1/3 below
  threshold — only spy at −0.049, just barely above)
- Kill B (ndx MDD > 35%): clean (28.63% — best ever for static stacks)
- **Kill C (DSR worst-p > 0.10): FIRED** — the iteration's primary
  thesis (regime gate clears DSR threshold) was not delivered. The
  partial-credit threshold (0.20) was missed by 0.04, and the
  strict-winner threshold (0.05) was missed by 0.15.
- Kill D (G7 cross-lib > 3pp): clean (max 0.087pp on ndx)
- Kill E (score < 75): clean (79 — ties iter 037)
- Kill F (robustness < 7/9): clean (9/9, perfect)
- Kill G (regime fraction extreme): clean (0.65/0.68/0.71 low-vol fracs
  — well within 50-85% sanity band)

---

## Configuration tested

Single pre-committed cfg `regime_lev_vix_lt20_lo10_hi17`:

| param | value |
|---|---|
| regime signal | VIX level (1-day lag → ``VIX[t−1]``) |
| threshold | **20.0** (Sinclair p.217 round-number; ≈ historical median + 0.3σ) |
| lev_lo (low-vol regime, VIX < 20) | **1.70** |
| lev_hi (high-vol regime, VIX ≥ 20) | **1.00** |
| base_weights (eq, bd, gld) | (0.60, 0.45, 0.45) — preserved from iter 037 |
| weight scaling | base × lev_regime / 1.50 (iter 037's lev) |
| rebalance | daily (regime checked daily, positions adjust on flip days only) |
| cost_bps_per_leg | 0.0002 (preserves iter 037 cost convention) |
| funding cost | NOT modeled (≈ 50-80 bps drag at avg 1.46-1.49× — same magnitude as iter 037) |

Cross-library parity: ≤ 0.087 pp CAGR delta on all 3 datasets
(threshold 3 pp, max observed in ndx_real). G7 PASS 3/3.

Regime statistics per dataset:

| dataset | low-vol frac (lagged) | avg lev | flips/yr ≈ | turnover/yr |
|---|---|---|---|---|
| educational | 0.653 | 1.457 | 14 | 10.25 |
| spy_real | 0.684 | 1.479 | 16 | 11.29 |
| ndx_real | 0.707 | 1.495 | 16 | 11.47 |

Avg leverage settles at 1.46-1.49 × — within 1 pp of iter 037's 1.50
on all 3 datasets. The regime gate is **leverage-neutral on average**;
any return / risk delta vs iter 037 comes purely from regime-conditional
exposure timing, not from elevated risk-taking.

Leg correlations (preserved from iter 037 since underlying tickers
unchanged): ρ(eq,bd) ≈ −0.20 to −0.30, ρ(eq,gld) ≈ +0.06 to +0.07,
ρ(bd,gld) ≈ +0.21 to +0.28. Average pairwise ρ ≈ −0.04 (orthogonal
diversification structurally identical to iter 037).

---

## What worked / what didn't

**What worked.** The MDD reduction is unambiguous and large: −8.22 pp
on educational (33.33% → 25.11%), −3.64 pp on spy_real (25.24% →
21.60%), and −3.65 pp on ndx_real (32.28% → 28.63%). The regime gate
correctly identifies high-vol episodes (2008-Q4, 2011 Eurozone, 2015
crude crash, 2018-Q4 sell-off, 2020-Q1 COVID, 2022 rate-hike) and
de-levers from 1.5× equivalent to 1.0×, exactly the windows that drive
peak-to-trough drawdowns in iter 037's constant 1.5× exposure. The
9/9 sub-window robustness was preserved — the gate does not introduce
sample-period sensitivity. G7 cross-library parity was clean (0.0087-
0.0872 pp CAGR delta vs pure-numpy reference, all under 1pp). Edu DSR
worst-p improved modestly (0.222 → 0.204).

**What didn't.** The Sharpe uplift predicted by Moreira-Muir 2017 (Table
IV reports +0.20-0.30 unconditional Sharpe uplift for vol-managed
factor portfolios) **did not materialize on this multi-asset stack.**
Sharpe regressed by 0.025-0.049 on spy_real and ndx_real (1.154 →
1.105 spy; 1.174 → 1.149 ndx) and only marginally improved on
educational (+0.015). Three structural reasons explain this:

1. **VIX-binary threshold is much cruder than vol-targeting.** Moreira-
   Muir 2017's σ⁻²-scaling adjusts exposure continuously across the
   full vol distribution; a binary threshold loses information about
   intermediate vol levels (e.g., VIX=18 vs VIX=22 — both close to the
   threshold, treated as polar opposites). Continuous scaling
   (Sinclair iter 005-style σ⁻¹) might recover more of the predicted
   uplift.

2. **Multi-asset stack already includes natural vol-diversification.**
   The 3-leg orthogonality (ρ_avg ≈ −0.04) means the stack's
   conditional vol is dampened across regimes vs a single-asset base.
   Moreira-Muir's +0.20-0.30 uplift was measured on single-asset
   factor portfolios (mkt, smb, hml); on iter 037's already-diversified
   base, the marginal benefit of regime gating is much smaller.

3. **Leverage-neutral on average means no Sharpe lift unless timing is
   aggressive.** With avg lev 1.46-1.49 ≈ iter 037's 1.50, the regime
   gate is purely re-distributing existing exposure. To get a Sharpe
   lift requires the low-vol regime to be Sharpe-significantly higher
   than the high-vol regime AND the gate to switch correctly. On this
   data, the empirical conditional Sharpe gap is ≈ +0.15-0.20 (post-
   2009), not +0.30+, so the average uplift falls short.

DSR worst-p improved only 8% (0.222 → 0.204) — in line with the small
edu Sharpe uplift but well below the 30%+ relative improvement needed
to clear the 0.10 partial-credit threshold (would need worst-p ≈
0.15) or the 0.05 strict threshold (would need ≈ 0.10).

**Key structural finding.** iter 037 + iter 038 together deliver the
**second-tightest empirical characterization of the static-stack family**
in the loop's history (after the iter 015/035 = 77 ceiling
characterization). The new characterization:

> Across both 3-leg-preserved-lev (iter 037) and regime-gated-3-leg
> (iter 038), the static-stack family at avg leverage 1.45-1.50× and
> base weights {0.6 eq, 0.45 bd, 0.45 gld} produces:
>
> - Sharpe in the band [0.98, 1.17] cross-dataset
> - DSR worst-p in the band [0.20, 0.23]
> - Score 79 STRONG (winner_conds 4/5, DSR sole gap)
>
> The mechanism applied to leverage modulation (preserved-3-leg vs
> regime-gated) does NOT shift the score band — only the MDD profile
> shifts (regime-gated wins on tail control by 4-8 pp).

The DSR ceiling within static-stack is **architecture-bound at 79**,
not lever-bound (037) and not regime-bound (038). To break the ceiling
requires either:

- A genuinely different return source (VRP harvest, factor timing, ML
  meta-label) — iter 026 demonstrated VRP single-asset can clear 76;
  cross-asset VRP basket may clear 80+.
- A more sophisticated regime-conditional **weight** mix (not just
  leverage). E.g., shift to GLD/IEF dominance during stress, equity
  dominance during low-vol — this is the proper HMM regime-conditional
  *portfolio* test, not just regime-conditional *leverage*.
- A continuous vol-managed scaling (σ⁻² Moreira-Muir-style) on the
  3-leg base, applied to the *equity leg only* — preserves diversifier
  premia while capturing the SPY-vol-managed Sharpe uplift.

---

## Main lesson (for future iterations)

**Binary VIX-level regime gating on a 3-leg static stack is
leverage-neutral on average AND Sharpe-neutral on net AND
DSR-neutral, but DELIVERS −4 to −8 pp MDD improvement across all 3
datasets — confirming iter 037's "static-stack DSR-bound at 79"
diagnosis with a strictly different lever.** Score 79 STRONG (ties iter
037 and the loop's top-K #1 quartet 016/018/021); 4/5 winner conditions
met (DSR sole gap, same as iter 037); 9/9 robust; G7 clean.

The DSR ceiling at 79 STRONG is now confirmed by **two independent
mechanisms** (preserved 3-leg lev, regime-gated 3-leg) and characterized
across the trajectory:

- iter 015 / iter 035 (77, 2-leg static): Sharpe 0.78-1.10
- iter 036 (72, 3-leg additive 1.8×): Sharpe 0.92-1.15, ndx MDD breach
- iter 037 (79, 3-leg preserved-lev 1.5×): Sharpe 0.98-1.17, MDD clean
- **iter 038 (79, 3-leg regime-gated avg 1.46-1.49×): Sharpe 0.997-1.149,
  MDD massively cleaner** (−4 to −8 pp vs 037 across all ds)

Future iterations breaking 79 within the static-stack family must NOT
attempt:

- Other leverage modulators (continuous σ⁻¹, σ⁻²) — predicted band
  79 ± 2 pts; same DSR ceiling.
- Other VIX threshold values (15, 25, 30) — minor perturbations
  within ±2 pts.
- Other regime indicators (term-spread, EBP, MOVE) on the same
  weight base — same ceiling, different tail profile.

To break 79 within the static-stack family, the **regime must modulate
WEIGHTS, not LEVERAGE** — e.g., shift to bond/gold dominance during
high-vol regimes (this is the proper "regime-conditional risk parity"
test). Outside the static-stack family, the candidate paths remain:

- Cross-asset VRP basket (iter 026 architecture × SPY+QQQ+IWM 1/3 each)
- 4-leg lev-preserved static (incremental, predicted 79-81)
- ML meta-label on iter 037 (AFML ch.3) — orthogonal by construction

The MDD-improvement finding is **economically valuable and operationally
significant**: for any candidate that becomes a Path-B reactivation
candidate (mandate §4 reactivation criteria), iter 038's regime-gated
profile would be strictly preferred over iter 037's at the same Sharpe.
The DSR ceiling does not invalidate this — it just keeps both at the
same score.

---

## Structural dead-ends discovered

**iter 038 (STRONG 79, 1/7 KILLS — Kill C only) — VIX-level binary
regime gating on iter 037's 3-leg static stack**: VIX_{t−1} < 20 →
1.70× lev; ≥ 20 → 1.00× lev; weights = (0.6, 0.45, 0.45) preserved
proportionally. **Ties iter 037 at 79 STRONG** (matches loop top-K #1
quartet 016/018/021/037). Kill C fires alone — DSR worst-p 0.204
(improvement of 0.018 vs iter 037's 0.222, but below the 0.20 partial-
credit threshold). MDD massively improved on all 3 datasets (−4 to −8
pp vs iter 037). 9/9 robust, G7 clean (max 0.087 pp). **Closes**:
binary VIX-level regime gating on a multi-asset static stack at avg
1.45-1.50× lev — does NOT break the static-stack 79 DSR ceiling. The
mechanism is **MDD-additive, Sharpe-neutral, DSR-marginal**.

This finding subsumes iter 037's prior characterization "static-stack
is DSR-bound at 79 absolute ceiling at preserved 1.5× leverage". The
corrected characterization: **static-stack is DSR-bound at 79 across
both preserved-lev AND regime-gated-lev mechanisms holding average
exposure constant**. To break 79 within the static-stack family
requires a regime mechanism that modulates **weights** (eq:bd:gld
ratio), not just total leverage; outside static-stack, a different
return source (VRP basket, factor timing, ML meta-label) is required.

The Kill C-only firing pattern (DSR 0.204 vs 0.10 threshold) confirms
the static-stack family is now characterized as a **two-axis ceiling**:

- DSR axis at 79: requires Sharpe ≈ 1.30+ cross-ds, mechanically
  unavailable within static-stack at avg lev ≤ 1.50× (without MDD
  breach via lev > 2.0×).
- MDD axis: free to optimize without affecting score (iter 038 reduced
  MDD by 4-8 pp vs iter 037 with no score impact). Future static-stack
  iterations should optimize MDD as a tiebreaker.

**Strongly de-prioritized for future iters within static-stack family**:

- Continuous vol-managed scaling (σ⁻², σ⁻¹) on the 3-leg base —
  predicted 79 ± 2 pts; same DSR ceiling (Moreira-Muir +0.20-0.30
  doesn't apply on already-diversified base).
- VIX z-score gating (60d window) — iter 030 closed this on iter 026
  base; predicted same DSR ceiling on iter 037 base.
- Other macro-regime gates (term-spread, MOVE, credit) on iter 037
  base — predicted 79 ± 3 pts.

---

## Citations used

**Primary**: `[advances_fin_ml, ch.17-18]` — regime detection /
Markov-switching state inference. The binary VIX-threshold rule is
the simplest 2-state regime classifier and the deterministic
equivalent of a 2-state Gaussian HMM on VIX log-levels (Hamilton
1989). The chapter's discussion of how regime-conditional
implementations differ from continuous filtering frames why a binary
gate may underperform a continuous filter on already-diversified bases.

**Supporting**:

- **Hamilton (1989)**, *Econometrica* 57(2): 357-384. DOI
  10.2307/1912559. Markov regime-switching econometric foundation.
- **Moreira & Muir (2017)**, *JF* 72(4): 1611-1644. DOI
  10.1111/jofi.12513. Vol-managed-factor unconditional Sharpe uplift
  Table IV — the predicted +0.20-0.30 mechanism that did NOT replicate
  on this multi-asset base.
- **Ang & Bekaert (2002)**, *JFE* 63(3): 443-494. DOI 10.1016/
  S0304-405X(02)00065-2. International regime-switching reference.
- `[volatility_trading, p.217-218]` — Sinclair, *Volatility Trading*
  (2nd ed., Wiley 2013). VIX 20 as the natural vol-regime divider.
- `[risk_parity, ch.5]` + `[risk_parity, p.5, p.10-11, ch.1]` —
  Asness-Frazzini-Pedersen (2012), *FAJ* 68(1): 47-59. SSRN 1728082.
  3-leg static stack base preserved from iter 037.
- `[leverage_for_the_long_run, p.19-20]` — Hsiao-Williams (2017),
  *J. Index Investing*. Preserved-on-average 1.5× lev framework.
- **Erb & Harvey (2006)**, *FAJ* 62(2): 69-97. DOI 10.2469/faj.v62.n2.4084.
  Gold strategic role on a levered base.
- **Asness-Moskowitz-Pedersen (2013)**, *JF* 68(3): 929-985. DOI
  10.1111/jofi.12021. Cross-asset orthogonality.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (G2).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (1-day shift
  on VIX-regime mask).

---

## Next iteration suggestions

The two-axis characterization of the static-stack ceiling (DSR-bound at
79; MDD freely optimizable) shifts iter 039 priority decisively away
from any further static-stack family experiments. Three candidate
directions, ordered by expected information yield:

1. **Cross-asset VRP basket extension (RECOMMENDED — strongest
   credible DSR-PASS path)**: iter 026's single-asset VRP architecture
   (T-bill collateral + short SPY put credit spread, harvest_notional
   = 1.0) extended to a 3-asset basket: 1/3 SPY put-spread + 1/3 QQQ
   put-spread + 1/3 IWM put-spread on T-bill collateral. Iter 026's
   ndx delivered the loop's first 7/7 + DSR PASS (p=0.038); the
   diversified basket may break the SPY-edu-specific DSR bottleneck
   while preserving the ndx PASS. Cross-asset VRP has strong empirical
   support (Bondarenko 2014; Carr-Wu 2009; Bakshi-Madan 2006) and the
   extension is structurally novel vs iter 026/028-031 (single-asset).
   Predicted: Sharpe 1.10-1.30 cross-ds, MDD 5-15 pp (very low),
   credible DSR PASS path. ~60-90 min. `[volatility_trading, p.218]`
   + Asness-Moskowitz-Pedersen 2013.

2. **Regime-conditional WEIGHTS (not just leverage) on iter 037 base**:
   when VIX < 20: (0.70, 0.40, 0.40) — equity tilt; when VIX ≥ 20:
   (0.30, 0.55, 0.55) — defensive tilt. Avg weights still ≈ iter 037's
   (0.60, 0.45, 0.45). This is the proper "regime-conditional risk
   parity" test that iter 038's leverage-only modulator did not
   reach. Predicted: Sharpe potentially +0.10-0.20 vs iter 037 (if
   the equity-tilt-on-low-vol thesis holds), MDD better than iter 037
   (defensive tilt-on-high-vol). May break 79 to 81-83 PROMISING-to-
   STRONG. ~2h. `[risk_parity, ch.5]` + Moreira-Muir 2017.

3. **ML meta-label on iter 037 base** (AFML ch.3): train a binary
   classifier (logistic regression or random forest) to predict
   "trade today / skip today" on iter 037's signal. Features: VIX,
   T10Y3M, EBP, momentum, recent realized vol. Meta-label is
   orthogonal-by-construction to the primary signal. Predicted: more
   variance, less reliable; if it works, could break to 85+. Higher
   risk / higher reward. ~3h. `[advances_fin_ml, ch.3]`.

**Recommended pick for iter 039: Cross-asset VRP basket**. The DSR
ceiling at 79 within static-stack family is now firmly characterized
across two mechanisms (037 + 038); the highest-yield uncharted DSR-
PASS path is cross-asset VRP, which has unique empirical evidence of
DSR PASS at the loop's iter 026 (ndx 7/7 + p=0.038) and natural
extension to a basket. If VRP basket fails, iter 040 should pivot to
regime-conditional weights (option 2) — that path is structurally
novel within the static-stack family and addresses the leverage-only
limitation iter 038 exposed.

The MDD-optimization finding from iter 038 (regime-gating delivers
−4 to −8 pp MDD at zero score cost) is **operationally relevant** for
any future Path B reactivation: even though score-tied with iter 037,
iter 038's regime-gated profile would be the preferred deployment
candidate. This is documented but not actionable until a winner-class
candidate emerges from iter 039+.
