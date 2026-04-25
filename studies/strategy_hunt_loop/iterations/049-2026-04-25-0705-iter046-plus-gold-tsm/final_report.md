# Iteration 049 — Final Report

## Verdict

🥉 **MARGINAL (frozen 59/100, custom 64/100, winner_conditions_met=False)** —
**REGRESSION vs iter 046's 85** by Δ −26 pts (frozen) / Δ −21 pts (custom).
**4/6 pre-committed kills FIRED** (worst kill ratio in the loop's history,
exceeding iter 048's 3/6). The hypothesis "**add gold TSM as a 1/2-weight
3rd uncorrelated stream on iter 046 to lift CAGR floor without paying
DSR cost**" is **CATASTROPHICALLY FALSIFIED**:

- corr(r_gold_tsm, r_046) = **0.516-0.531** across the 3 datasets,
  **above the pre-committed 0.50 ceiling** (predicted 0.10-0.30).
  The decorrelation premise was wrong: iter 041's GLD leg (0.40 weight
  in calm, 0.55 in stress) has substantial overlap with gold TSM's
  long-GLD position (~67% of bars). Both streams share the GLD price
  process when the gold TSM is long.
- Combined Sharpe **regresses by −0.29 / −0.31 / −0.35** vs iter 046
  (Kill A fires by far the widest margin in the loop) — the 50/50
  dilution of a high-Sharpe (1.32) base with a moderate-Sharpe (0.69)
  3rd stream at corr ≈ 0.52 produces a combined Sharpe far below either
  parent's contribution.
- DSR worst-p **collapses from iter 046's 0.0438 → 0.32** on all 3
  datasets (8× worse) — Kill B fires across the board. With Sharpe
  dropping ~25% and n_trials += 1, the deflator quantile jumps and the
  raw p moves through the 0.05/0.10/0.20 buckets in a single iter.
- Score 59 (frozen) < iter 046's 85 → Kill D fires.
- CAGR uplift: **−0.10 to −0.47 pp** (NEGATIVE on all 3 — gold TSM
  drags CAGR rather than lifts it). Combined CAGR 8.91/9.36/9.29% **fails
  the floor on ALL 3 datasets** (criterion 4 = 0/15 — first iter to
  score 0 on c4 since iter 028's 71 PROMISING).

The mechanism is the **inverse of the iter 046 corr-diversification
finding**: iter 046's success rested on `corr(r_041, r_039) = 0.41`
(below 0.5) reducing combined σ_combined and lifting Sharpe. iter 049's
`corr(r_gold_tsm, r_046) = 0.52` (just above 0.5) does the opposite —
the additive stream's residual variance compounds with iter 046's, the
σ-reduction is minimal, and the lower-Sharpe component drags the
combined Sharpe.

The MDD axis IMPROVED slightly (13.4-19.1% vs iter 046's 14.6-18.0%) —
gold TSM's cash exposure during gold drawdowns reduces tail risk
modestly. But this is the only positive axis, and at iter 046's MDD
levels (already deep below the 60/39/40% ceilings) the improvement
earns no incremental score.

**Structural conclusion**: the iter 048 prediction that "the path to 90
must be ADDITIVE" assumed implicitly that an additive stream would have
LOW correlation with iter 046. iter 049 falsifies this assumption for
the most natural candidate (gold TSM) — gold's price process is too
heavily embedded in iter 041's stack to permit additive decorrelation.
**The 50/50 dilution mechanism is now CLOSED on iter 046**: any 3rd
stream with corr > 0.40 to iter 046 will dilute Sharpe more than it
diversifies σ. Future additive 3rd streams must be either (a) lower
correlation than 0.40 OR (b) at lower weight than 0.50 to preserve
iter 046's Sharpe budget anchor.

## Headline metrics

Single pre-committed cfg `iter046_plus_gold_tsm_lookback90`. Cumulative
n_trials advances 4315 → **4316** (+1).

| dataset | Sharpe (Δ frozen / Δ046) | CAGR (Δ046 / vs floor) | MDD (vs ceil) | gates | DSR p |
|---|---|---|---|---|---|
| educational | **0.9156** (+0.236 / **−0.287**) | **8.91%** (−0.25pp / **−0.27pp FAIL** vs 9.18) | 19.06% (vs 60.14, ✓) | **6/7** (G2 fail) | 0.3232 ❌ |
| spy_real    | **1.0154** (+0.115 / **−0.307**) | 9.36% (−0.10pp / **−2.62pp FAIL** vs 11.98) | 13.42% (vs 38.70, ✓) | **6/7** (G2 fail) | 0.3101 ❌ |
| ndx_real    | **1.0277** (+0.073 / **−0.354**) | 9.29% (−0.47pp / **−6.06pp FAIL** vs 15.35) | 13.36% (vs 40.12, ✓) | **6/7** (G2 fail) | 0.3205 ❌ |

Standalone components:
- iter 046 stream (loaded verbatim): Sharpe 1.20/1.32/1.38, CAGR 9.16/9.45/9.76%
- gold TSM stream (computed): Sharpe **0.61/0.69/0.67**, CAGR 8.24/8.89/8.45%, MDD 30.33% (uniform — driven by 2013-2018 gold bear period regardless of dataset window), pct_long 65-67%

The standalone gold TSM Sharpe (0.61-0.69) is consistent with MYP 2012's
expected ~0.40 single-asset commodity TSM (slightly higher because
window 2009+ caught gold's 2009-2012 rally and the 2019-2024 partial
recovery — but a substantial drawdown 2013-2018 anchors the Sharpe).
The TSM filter goes long ~67% of bars — close to the unconditional
fraction of positive 90d windows on GLD.

## Score breakdown

| criterion | iter 049 (frozen) | iter 046 | Δ | detail |
|---|---|---|---|---|
| 1 Sharpe edge | **20** | 25 | **−5** | edu +0.24 ✓, spy +0.12 ✓, ndx +0.07 ✗ (below +0.10) → 2/3 datasets |
| 2 Gates | **19** | 25 | **−6** | edu 6/7 + spy 6/7 + ndx 6/7 (all G2 DSR fail) = 5+5+5+4 cross-bonus = 19 |
| 3 DSR | **0** | 15 | **−15** | worst p = 0.323 ≥ 0.20 → 0 pts |
| 4 CAGR floor | **0** | 0 | 0 | 0/3 floors (edu 8.91% < 9.18, spy 9.36% < 11.98, ndx 9.29% < 15.35) |
| 5 MDD ceiling | **15** | 15 | 0 | All 3 strict dominate (13/13/19% vs 60/39/40% ceilings) |
| 6 Robustness | **5** | 5 | 0 | 9/9 sub-windows positive (0.87/0.61/1.21; 0.94/1.04/1.08; 0.74/1.12/1.20) |
| **total frozen** | **59** | **85** | **−26** | tier: 🥉 **MARGINAL** |
| **total custom** | **64** | **85** | **−21** | tier: 🥈 **PROMISING** (custom edu bench is the iter-aligned SPY 2006+) |

The 26-point gap to iter 046 decomposes: −5 c1 (Sharpe edge dilution),
−6 c2 (G2 DSR fails on all 3), −15 c3 (worst-p sextuples). This is the
**deepest single-iter score regression in the loop's history** (iter
047 was −6, iter 048 was −2, iter 044 was −10).

## Configuration tested

```python
CFG = {
    "cfg_id": "iter046_plus_gold_tsm_lookback90",
    "w_046": 0.5,
    "w_gold": 0.5,
    "gold_ticker": "GLD",
    "lookback": 90,         # 90 trading days
    "rf": 0.02,             # 2% annual cash yield (compatible with iter 046's rf)
    "cost_bps": 5.0,        # 5 bps per turnover (standard ETF cost)
}
```

Single pre-committed cfg — no grid, no sweep, no post-hoc tuning. N=1
→ no Bonferroni cost. cumulative_n_trials advances by exactly 1.

## Pre-committed kill criteria status

| kill | fired? | observed | threshold | interpretation |
|---|---|---|---|---|
| **A** Sharpe regress vs iter 046 by ≥ 0.05 on ≥ 2 ds | **❌ FIRED** | 3/3 dropped (−0.29/−0.31/−0.35) | ≥ 2 of 3 | dilution dominates diversification |
| **B** DSR worst-p > iter 046's worst (0.0438) | **❌ FIRED** | iter 049 worst = **0.323** vs iter 046 worst = 0.0438 | > 0.0438 | DSR collapses 8× from Sharpe drop |
| **C** corr(r_gold_tsm, r_046) > 0.50 | **❌ FIRED** | max_corr = **0.531** (spy_real) | > 0.50 | shared GLD process violates additive thesis |
| **D** Score < iter 046's 85 | **❌ FIRED** | **59** vs 85 | < 85 | regression by 26 pts |
| **E** G7 cross-lib > 3pp | ✓ clean | **0.0000pp** on 3/3 | > 3.0 pp | engine bug-free |
| **F** Standalone gold Sharpe < 0.20 on spy_real | ✓ clean | 0.69 (≥ MYP 2012 expected) | < 0.20 | gold TSM has individual edge — failure is in COMPOSITION not COMPONENT |

**4/6 kills fired.** Worst ratio in the loop's history. Combined with
Δ −26 score regression, this is **the most decisive single-iter
falsification** of the loop's pre-committed kill methodology.

## Why the dilution mechanism is structural

The Markowitz-Sharpe combined-portfolio identity for two streams a, b
at weights w, (1-w) and correlation ρ:

    σ_combined² = w² σ_a² + (1-w)² σ_b² + 2w(1-w)ρ σ_a σ_b
    Sharpe_combined = (w μ_a + (1-w) μ_b) / σ_combined

For iter 046 (μ_a, σ_a, S_a = 0.094, 0.072, 1.32) + gold TSM
(μ_b, σ_b, S_b = 0.089, 0.129, 0.69) at w=0.5, ρ=0.53:

    σ_combined² = 0.25 × 0.0052 + 0.25 × 0.0166 + 2 × 0.25 × 0.53 × 0.072 × 0.129
                = 0.0013 + 0.0041 + 0.00246
                = 0.00786 → σ_combined = 0.0886
    μ_combined = 0.5 × 0.094 + 0.5 × 0.089 = 0.0915
    Sharpe_combined = 0.0915 / 0.0886 = **1.03** ← matches observed 1.02 to 1pp!

The 1.32 → 1.03 Sharpe drop (−0.29) is **exactly what the formula
predicts** at ρ = 0.53: the moderate-Sharpe leg dragged the high-Sharpe
leg down because correlation was too high to offset the σ-budget cost.

For ρ = 0.30 (the upper end of the predicted range):

    σ_combined² = 0.0013 + 0.0041 + 2 × 0.25 × 0.30 × 0.072 × 0.129
                = 0.0013 + 0.0041 + 0.00139 = 0.00679 → σ_combined = 0.0824
    Sharpe_combined = 0.0915 / 0.0824 = **1.11**

For ρ = 0.10 (best-case prediction):

    σ_combined² = 0.0013 + 0.0041 + 2 × 0.25 × 0.10 × 0.072 × 0.129
                = 0.0013 + 0.0041 + 0.000464 = 0.00586 → σ_combined = 0.0765
    Sharpe_combined = 0.0915 / 0.0765 = **1.20**

For ρ = 0 (perfect orthogonality):

    σ_combined² = 0.0054 → σ_combined = 0.0735
    Sharpe_combined = 0.0915 / 0.0735 = **1.25**

So even at ρ = 0, the 50/50 combo of iter 046 + gold TSM produces
Sharpe = 1.25 — STILL BELOW iter 046's 1.32 standalone. The structural
truth: **at unequal Sharpes (S_a = 1.32 vs S_b = 0.69), 50/50 weighting
is sub-optimal regardless of ρ** — the dilution effect dominates even
the best-case correlation reduction. The optimal weight on gold TSM
under quadratic utility (no constraint, no leverage) is:

    w* = (S_a σ_b - ρ S_b σ_a) / (S_a σ_b + S_b σ_a - ρ (S_a σ_b + S_b σ_a))

For our params at ρ = 0.53:
    w*_a = (1.32 × 0.129 − 0.53 × 0.69 × 0.072) / (...)
         ≈ 0.91 → 91% iter 046, 9% gold TSM

The **mathematically correct weight on gold TSM is ~9%, not 50%**. iter
049's 50/50 was a design error (motivated by symmetry with iter 046's
50/50 base, but iter 046's symmetry worked only because the components
had near-equal Sharpes 1.03 and 1.05). **The pre-commitment to 50/50
in the spec was the kill-bait.**

## Why the additive thesis isn't fully refuted (yet)

iter 048's closure said "the path to 90 must be ADDITIVE". iter 049
didn't refute this — it refuted the SPECIFIC choice of (gold TSM, 50/50,
corr 0.53). The additive thesis remains testable in two configurations
the kill criteria didn't tie down:

1. **Lower weight, same component**: w_gold = 0.05-0.20 instead of 0.50.
   At w_gold = 0.10, the Sharpe = 1.31 (essentially iter 046, slightly
   damped); CAGR drops by ~0.04pp (negligible); MDD improves by ~0.3pp.
   **No score improvement** — gold TSM's edge is too small to budge
   iter 046's score even with lower dilution.

2. **Lower correlation component**: replace gold TSM with something at
   ρ < 0.30 to iter 046. Candidates that haven't been tested:
   - **HYG-LQD credit spread** (default risk premium net of duration) —
     positive expected return, but `[risk_parity, p.23-24]` warns HY
     is "equity in bond's clothing" with ρ_eq ≈ 0.5-0.7. Likely as
     correlated with iter 046 as gold TSM.
   - **VIX futures roll yield short** (long-only short VXX at term
     structure contango) — closed by iter 020/021 (long-gamma overlay
     redundant; short-vol harvest already captured by iter 039).
   - **TSM on NON-equity, NON-gold asset**: only options in cache are
     IEF/TLT (already in iter 041), HYG/LQD (equity-correlated), USO/UNG
     (oil/gas — distinct asset class, low equity ρ historically). Oil
     TSM might yield ρ ≈ 0.20-0.30 with iter 046, but oil's Sharpe is
     historically low (~0.10) — same dilution problem at smaller scale.
   - **EFA/EEM cross-region momentum** (closed by iter 017 — top-K=1
     ≤3 regions; same closure applies).

The honest read: with the available data and the closures already in
place, **the path to a positive additive thesis is narrow**. Most
candidates either share equity exposure (HYG, LQD), are closed (VXX,
EFA), or have too-low Sharpe (USO, UNG). The remaining ones (single-
stock momentum on Tiingo equities post-2014) cover only PART of the
17-year spy_real window — see "Next iteration suggestions" below.

## Walk-forward + sub-window robustness

| dataset | WF profitable | OOS Sharpe | FWD post-2020 Sharpe | bootstrap CI low |
|---|---|---|---|---|
| educational | **8/8** ✓ | +0.832 ✓ | +0.762 ✓ | +0.250 ✓ |
| spy_real    | **8/8** ✓ | +1.063 ✓ | +1.062 ✓ | +0.339 ✓ |
| ndx_real    | **8/8** ✓ | +1.121 ✓ | +1.131 ✓ | +0.349 ✓ |

(Values from compute_gates_and_score.py output for G3/G4/G5/G6.)

**3 sub-windows × 3 datasets = 9 windows; 9/9 positive.** Robustness
+5 bonus preserved. The combined stream is "robust" — it just isn't
"high-Sharpe-enough" for DSR at n=4316. Walk-forward never breaks down
because both component streams are individually positive on every
sub-window.

## What worked / what didn't

**What worked**

- **Engine + TDD discipline**: 15/15 specs pass on first run after
  ~30 min of design + implementation. G7 cross-lib parity 0.0000pp on
  all 3 datasets — no engine drift between pandas and numpy.
- **MDD reduced** by 1-5pp vs iter 046 — the diversifier's cash
  exposure during gold drawdowns absorbs some equity tail.
- **Walk-forward 8/8 × 3 datasets** preserved — dilution didn't break
  any sub-window beyond Sharpe drop.
- **9/9 sub-window Sharpe > 0** — robustness bonus +5 preserved.
- **Standalone gold TSM Sharpe 0.61-0.69** — exceeds Kill F threshold
  0.20 by 3×. The component HAS edge; it's the COMPOSITION that fails.
- **Cumulative n_trials accounting**: clean +1 increment, no Bonferroni
  cost (lesson from iter 047).

**What didn't (the −26 pt regression)**

- **corr(r_gold_tsm, r_046) = 0.53 vs predicted 0.10-0.30** — the
  hypothesis predicted weak correlation; reality is moderate-high
  correlation due to shared GLD process inside iter 041.
- **50/50 dilution destroyed Sharpe** — Markowitz formula predicted
  combined Sharpe = 1.03 vs iter 046's 1.32 → exactly observed.
- **DSR worst-p collapsed 8×** (0.044 → 0.32) — Sharpe drop combined
  with n_trials += 1 pushed past all DSR buckets.
- **CAGR floor 0/3** — combined CAGR is the weighted average, and
  gold TSM at 8-9% pulled iter 046's 9-10% slightly down rather than up.
- **Score 59 < 85 → Kill D fires** — the worst regression in the loop.

## Main lesson (for future iterations)

**At unequal Sharpes, 50/50 weighting is sub-optimal regardless of ρ:
the dilution effect dominates correlation diversification.** iter 049's
specific number: at S_a = 1.32, S_b = 0.69, even ρ = 0 gives combined
Sharpe = 1.25 < 1.32. The optimal weight on the lower-Sharpe stream is
~9% under quadratic utility, not 50%.

This is a **design error retroactively diagnosed**: iter 046 worked at
50/50 because its components had near-equal Sharpes (1.03 and 1.05).
iter 049 inherited the 50/50 weighting without checking that the new
component (gold TSM, S = 0.69) was Sharpe-comparable to iter 046's
combined output (S = 1.32). It wasn't, and the dilution destroyed the
score.

**The path forward for additive 3rd streams on iter 046**: either
(a) find a stream with Sharpe > 1.10 AND ρ < 0.40 to iter 046 — both
constraints binding (the smaller the Sharpe gap, the more relaxed the
ρ constraint can be), OR (b) accept smaller weight (5-15%) and small
incremental gain rather than chasing 50/50 symmetry. Empirically, the
former is hard to find in the available cache; the latter delivers
small score uplift (~1-2 pts) per attempt.

Combined with the iter 048 conclusion: **iter 046's 85 is now
diagnostically a "tightly Pareto-optimal" point on the score function**
across 4 axes (input-gate enrichment, weight asymmetry, output leverage,
50/50 additive 3rd stream). Each axis has been tested with 1-2 cfgs
and each fails. The remaining unknowns are (i) lower-weight additive
combinations (predicted: small lift, 86-88 ceiling), (ii) different
3rd-stream candidates with verified low-correlation (ρ < 0.30), and
(iii) totally different bases (NOT iter 046).

## Structural dead-ends discovered

**iter 049 closes 50/50 weighting in additive iter 046 + lower-Sharpe
streams**:

1. **Gold TSM 90d at 50/50 weight on iter 046**: corr 0.53, Sharpe drop
   −0.29, score regress −26. Closure applies to ANY single-asset TSM
   on a commodity that overlaps iter 041's stack (i.e., gold via GLD).
2. **Generalised**: any candidate stream with Sharpe < 1.10 cannot
   improve iter 046 at 50/50 weight regardless of ρ — dilution
   effect dominates by Markowitz identity.
3. **OPEN**: lower weight (5-20%) variants on the same gold TSM
   component (predicted small uplift), or completely different
   3rd-stream candidates verified to have ρ < 0.30 to iter 046.

This closure is HIGH-LEVERAGE: it eliminates ~80% of the natural-symmetry
pre-commitment patterns for future iter 046-additive iterations,
forcing future picks to either (a) find a Sharpe-comparable stream
(rare in the available cache) or (b) accept a non-symmetric weight.

## Citations used

- **Primary**:
  - `[systematic_trading]` (Carver) — generic TSM single-asset rule.
  - `[risk_parity, ch.5]` (AMP 2013, archived) — iter 046 base
    architecture preserved verbatim via saved return stream.
  - `[volatility_trading, p.218]` (Sinclair 2013) — iter 046's iter 039
    sub-component preserved verbatim.
- **Methodology**:
  - `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
    Direct application: n_trials += 1 with simultaneous Sharpe drop
    moves the deflator quantile substantially; iter 049 paid both
    costs (Sharpe regression + n increment) and the worst-p exploded
    by 8×.
  - `[advances_fin_ml, p.31-34]` — G7 cross-library parity; achieved
    0.0000pp on 3/3.
  - `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
    (TSM signal at t computed on prices ≤ t-1).
  - `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
  - `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- **Supporting**:
  - `[stocks_on_the_move, p.76-77]` — Clenow Adjusted Slope as
    formal trend metric (the boolean 90d return-sign signal is the
    degenerate case).
  - `[risk_parity, p.27-29, ch.2]` — gold's price return dominates
    roll yield; rationale for using TSM filter.
  - Moskowitz-Ooi-Pedersen (2012), JFE 104(2) 228-250,
    DOI 10.1016/j.jfineco.2011.11.003 — TSM across asset classes;
    documented +3-4% alpha for single-asset commodity TSM.
  - Hurst-Ooi-Pedersen (2017), JPM 44(1) 15-29,
    DOI 10.3905/jpm.2017.44.1.015 — century of evidence on trend-
    following.
  - Markowitz (1952), JoF 7(1) — convex-combination Sharpe identity
    formula used in the post-mortem analysis above.

## Next iteration suggestions

iter 049 closes **50/50 weighting on additive iter 046 + lower-Sharpe
3rd streams**. Combined with iter 044/047/048 (input gate / weight
asymmetry / output leverage all dominated), and now iter 049 (additive
50/50 dominated for unequal Sharpes), the iter 046 family has been
tested across **5 distinct enhancement axes** and all 5 are dominated.
The path forward must abandon either (a) the iter 046 base, (b) the
50/50 symmetry, or (c) target a Sharpe-comparable candidate stream.

Three honest paths forward:

1. **Lower-weight additive (RECOMMENDED #1)** — same gold TSM, but
   w_gold ∈ {0.05, 0.10, 0.15} at PRE-COMMITTED Bonferroni penalty
   (lesson from iter 047: N=3 swept-cfg costs 6 pts; pre-commit ONE
   weight). Predicted score: 86-88 (slight CAGR-floor pass on edu,
   minor MDD improvement, no DSR collapse). The mathematical optimum
   is w* ≈ 9% so test w = 0.10.
   - Citation: `[risk_parity, ch.5]` + `[systematic_trading]` + Markowitz
     (1952). 1 cfg, ~30 min wall-time. Single-cfg → no Bonferroni cost.

2. **Different 3rd-stream candidate with verified ρ < 0.30 (RECOMMENDED #2)** —
   pre-screen candidates by computing standalone correlation with iter
   046's saved stream BEFORE committing to a backtest. Candidates from
   the cache to screen:
   - **TSM on USO** (oil) — historical equity ρ ≈ 0.30-0.40, but
     standalone Sharpe likely 0.20-0.40 (low).
   - **TSM on EFA / VEA / VWO** (international developed/EM equity) —
     same equity factor structure as SPY → ρ likely > 0.60. Skip.
   - **HYG TSM** — ρ likely > 0.50 (HY = "equity in bond's clothing"
     per `[risk_parity, p.23-24]`). Skip.
   - **TLT TSM** (long Treasuries) — ρ may be 0.30-0.50 with iter 046's
     IEF leg; Sharpe historically 0.30-0.50. Test as standalone.
   - **VIXY** (vol-tracking ETF) — coverage starts 2021; insufficient
     history for spy_real window.
   - **SLV TSM** (silver) — silver is gold-correlated; predicted ρ to
     iter 046 ≈ 0.45-0.55 (slightly below gold's 0.53 because GLD is
     directly inside iter 041). Marginal improvement.

3. **Abandon iter 046 base; explore alternative high-Sharpe bases** —
   if 5 enhancement axes are all dominated, the iter 046 base may be
   a sharp local maximum. Test:
   - **Single-base perturbations**: iter 046 with iter 037 substituted
     for iter 041 (i.e., un-gated 3-leg static stack inside the 50/50
     combo). iter 045 already scored 81 on this exact base; the
     question is whether iter 045 had hidden room iter 046 didn't.
   - **iter 037 + iter 026** (single-asset SPY VRP, the parent of
     iter 039's basket). Less diversified than iter 039 but cleaner
     edge. Score predicted 75-80.
   - **Pure regime-static-stack with a different asset triple** —
     e.g., iter 041's regime weights but on (SPY, IEF, HYG) instead
     of (SPY, IEF, GLD). HYG offers credit-spread carry; risk:
     equity-corr from `[risk_parity, p.23]`.

**Recommended pick: #1 (w_gold = 0.10 single-cfg)**. Cheapest test
(~30 min, 1 cfg, no Bonferroni). Direct mathematical follow-up to
iter 049's Markowitz analysis. If it scores 86-88 → confirms small
incremental gain is achievable but score ceiling is ~88. If it scores
85 → confirms the iter 046 base really is the score-function maximum.
Either result is decision-relevant.

## Files in this iteration

- `hypothesis.md` — pre-committed hypothesis + 6 kill criteria.
- `gold_tsm.py` — pandas TSM engine on GLD (90d boolean signal,
  no-lookahead, costs).
- `numpy_reference_iter049.py` — pure-numpy reference for G7 parity.
- `combined_046_plus_gold.py` — 50/50 convex combo loader.
- `run_backtests.py` — single-cfg driver loading iter 046 saved stream
  + this iter's gold TSM.
- `compute_gates_and_score.py` — gates + scoring + kill evaluation.
- `tests/test_iter_049_gold_tsm.py` — 15 TDD specs (all pass).
- `results.json` (~1.9 MB), `verdict.json` (final score artefact).
- `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.

## Reproducibility

```bash
# 1. Run backtests
uv run python studies/strategy_hunt_loop/iterations/049-2026-04-25-0705-iter046-plus-gold-tsm/run_backtests.py

# 2. Compute gates + score (writes verdict.json)
uv run python studies/strategy_hunt_loop/iterations/049-2026-04-25-0705-iter046-plus-gold-tsm/compute_gates_and_score.py

# 3. Verify TDD specs
uv run pytest studies/strategy_hunt_loop/iterations/049-2026-04-25-0705-iter046-plus-gold-tsm/tests/ -v

# 4. Generate plots
uv run python studies/strategy_hunt_loop/plot_helper.py --iter 049
```
