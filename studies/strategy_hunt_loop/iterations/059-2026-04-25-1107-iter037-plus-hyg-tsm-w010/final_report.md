# Iteration 059 — Final Report

## Verdict

🥇 **STRONG** — score **79/100** (frozen) / **79/100** (custom-bench),
**winner_conditions_met=False** (DSR worst-p 0.2675 ≥ 0.05 cutoff),
**1/7 kills fired** (kill B — DSR didn't improve vs iter 037 baseline).

This iteration tested **direction #1 from BASE_MEMORY**: pair the
proven HYG_TSM 3rd stream (iter 058's vindication) with a higher-CAGR
anchor (iter 037, CAGR 14-18%) instead of iter 046 (CAGR 9-10%) to
unlock the CAGR floor 0/15 gap that pinned iter 058 at 85. The CAGR
floor unlock **succeeded fully (15/15, 3/3 datasets)** — but DSR did
NOT clear because iter 037's standalone Sharpe (~0.96-1.17 on the
HYG-windowed range) is already too close to the Markowitz-predicted
combined Sharpe to leave headroom for a deflated p-value < 0.05 at
n_trials=4329. The iter 037 anchor's CAGR advantage **cannot
substitute for the higher Sharpe of iter 046's anchor when the binding
constraint is DSR**.

The result has 3 noteworthy structural findings:

- **CAGR floor unlock works as predicted**: combined CAGR 13.04% /
  14.47% / 16.50% on edu/spy/ndx, **all 3/3 above the 0.8×bench floor**
  (9.18% / 11.98% / 15.35%). Iter 058 had **0/3** on this metric
  (CAGR 8.69 / 9.01 / 9.27% all below floors). The +5-7 pp CAGR
  cushion in iter 037 vs iter 046 absorbs the 0.4-1.1 pp HYG drag
  comfortably.
- **MDD ceiling 3/3 + Sharpe edge 3/3 retained**: combined MDD
  30.71 / 22.93 / 29.33% all under bench+5pp; Sharpe edge vs frozen
  +0.30 / +0.27 / +0.23 (all ≥ +0.10). Iter 037's MDD cushion (vs
  bench) is preserved by HYG addition.
- **DSR still 0/15**: edu p=0.2675, spy p=0.1279, ndx p=0.1381. The
  Markowitz-predicted Sharpe lift from HYG_TSM on iter 037 is only
  +0.02 cross-dataset (vs iter 058's +0.02 on iter 046), but iter
  037's lower starting Sharpe (~0.96-1.17) means combined Sharpe
  ~0.98-1.18 cannot overcome the DSR penalty at n_trials=4329 — exactly
  what iter 037's verdict.json's lesson predicted ("**static-stack is
  DSR-bound at 79 absolute ceiling**, achievable at preserved 1.5×
  leverage with 3 orthogonal diversifier legs"). Adding a 3rd-stream
  TSM at w=0.10 does NOT change that DSR-binding characterization.

This closes a key cell in the path-to-WINNER landscape: the
**saved-stream-pair Pareto exhausted at 85 STRONG (iter 058 + iter
046)** stands; substituting iter 037 for iter 046 gives back exactly
iter 037's score (79) because the +1 score from added Sharpe edge is
offset by the 0/15 DSR-bucket loss vs iter 046's 15/15 DSR. **The path
to WINNER is NOT through anchor substitution at fixed Markowitz
weights** — it requires a base anchor with **simultaneously** Sharpe ≥
1.20 (DSR-clearing) AND CAGR ≥ 12% (floor-clearing) on real data, a
combination none of the 0-58 anchors achieves before HYG addition.

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen, Δ037) | CAGR (Δ037) | MDD (Δ037) | DSR p | gates |
|---|---|---|---|---|---|
| educational | 0.9814 (+0.3014, **−0.0013**) | 13.04% (**−1.11pp**) | 30.71% (**−2.62pp** ✓) | **0.2675** ✗ | **6/7** |
| spy_real    | 1.1732 (+0.2732, **+0.0195**) | 14.47% (**−1.06pp**) | 22.93% (**−2.31pp** ✓) | **0.1279** ✗ | **6/7** |
| ndx_real    | 1.1830 (+0.2280, **+0.0093**) | 16.50% (**−1.26pp**) | 29.33% (**−2.95pp** ✓) | **0.1381** ✗ | **6/7** |

Standalone HYG_TSM metrics on each dataset (for comparison): Sharpe
0.872 / 0.990 / 0.996, CAGR 5.08 / 4.92 / 4.79%, MDD 17.64 / 6.72 /
6.72%, pct_long 73.6 / 76.2 / 75.6% (HYG_TSM engine vendored verbatim
from iter 058; G7 cross-lib parity 0.0000 pp on all 3 datasets, same
as iter 058).

Standalone iter 037 stream on the windowed (HYG-aligned) range:
Sharpe 0.9594 / 1.1545 / 1.1665, CAGR 13.86 / 15.50 / 17.77%, MDD
33.33 / 25.24 / 32.28%. The educational stream is windowed from
2007-04-12 → 2026-04-15 (~4787 bars vs original 5101) by the inner-
join with HYG; spy_real and ndx_real already start post-HYG-inception
so are unaffected. The educational windowed Sharpe drops 0.023 (0.96
vs 0.98 on the full range) because the 2006-2007 portion of iter
037's stream had a slightly higher Sharpe than the 2007-2026 portion.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | All 3 datasets beat frozen bench by ≥ 0.10 (Δ +0.30 / +0.27 / +0.23) |
| 2 Gates | **19** | 25 | 6/7 each (G1 PBO N=1 vacuous PASS, G2 DSR FAIL all 3) + cross-ds bonus +4 = 19/25 |
| 3 DSR | **0** | 15 | Worst-p 0.2675 (edu) ≥ 0.20 → bucket 0; n_trials=4329 |
| 4 CAGR floor | **15** | 15 | All 3 ≥ 0.8×bench (13.04 / 14.47 / 16.50% vs 9.18 / 11.98 / 15.35%) |
| 5 MDD ceiling | **15** | 15 | All 3 ≤ bench+5pp; **lower than iter 037 by 2.3-3.0 pp on each** (HYG defensive) |
| 6 Robustness | **5** | 5 | 9/9 sub-windows positive (edu 0.80/1.10/1.18, spy 1.31/1.15/1.09, ndx 1.18/1.35/1.07) |
| **total** | **79** | **100+5** | tier: **STRONG** |

Custom-bench score: **79/100** (using HYG-aligned 2007+ benchmarks
where edu SPY Sharpe drops to 0.628 and CAGR to 10.81%; the looser
floor doesn't change the score because the CAGR floor is already 15/15
on frozen, and DSR/Sharpe/Gates aren't sensitive to the bench window).

Strict winner conditions: **4/5 met** — same as iter 037:
1. Sharpe edge ≥ +0.10 on ≥ 2 ds: ✓ (3/3)
2. Gates cross-ds (edu ≥5, spy/ndx ≥4): ✓ (6/6/6)
3. DSR p < 0.05 (worst): ✗ (0.2675)
4. CAGR ≥ 0.8×bench on ≥ 2 ds: ✓ (3/3)
5. MDD ≤ bench+5pp on ≥ 2 ds: ✓ (3/3)

Only **DSR fails** the strict 0.05 threshold (same blocker as iter 037
standalone). Score 79 + winner_conds=False → **STRONG** (≥ 75, < 90).

## Configuration tested

```python
CFG = {
    "cfg_id": "iter037_plus_hyg_tsm_w010_lookback90",
    "w_037": 0.9,                       # iter 037 anchor (3-leg static stack)
    "w_hyg": 0.1,                       # HYG TSM long-only
    "hyg_ticker": "HYG",
    "lookback": 90,                     # boolean trend on trailing 90d return
    "rf": 0.02,
    "cost_bps": 5.0,
}
```

Effective top-level weights: 0.54 SPY + 0.405 IEF + 0.405 GLD + 0.10
HYG_TSM (iter 037's 0.60/0.45/0.45 scaled by 0.9). Total 1.45×
notional. All hyperparameters pre-committed; no grid sweep.
cumulative_n_trials advance: 4328 → **4329** (+1).

## Pre-committed kills

| # | kill | fired? | observation |
|---|---|---|---|
| A | Sharpe regress vs iter 037 by ≥ 0.10 on ≥ 2 datasets | ✓ clean | edu Δ −0.0013 (within noise), spy Δ +0.0195, ndx Δ +0.0093; 0/3 datasets dropped 0.10+ |
| B | DSR worst-p ≥ iter 037's 0.222 baseline | **❌ FIRED** | edu p 0.2675 ≥ 0.222 (the HYG-windowed edu stream lost the high-Sharpe 2006-2007 portion of iter 037, raising worst-p) |
| C | Score < iter 037's 79 (anchor baseline) | ✓ clean | 79 ≥ 79 (matched, did not regress) |
| D | Markowitz residual ≥ 0.05 on ≥ 2 datasets | ✓ clean | residuals −0.0000 / +0.0000 / +0.0000 (perfect closed-form, like iter 058) |
| E | G7 cross-lib > 3 pp | ✓ clean | 0.0000 pp on all 3 datasets (HYG_TSM engine identical to iter 058) |
| F | corr(r_hyg, r_037) > 0.85 | ✓ clean | avg 0.416 (max 0.444); HYG is genuinely diversifying — corr LOWER than iter 058's 0.443 because iter 037's smaller equity weight (0.6 vs 0.81 effective in iter 046) lowers eq-credit corr |
| G | CAGR floor regress on ≥ 2 datasets | ✓ clean | 0/3 datasets failed floor; **the structural CAGR-floor-unlock thesis VINDICATED** |

**1/7 kills fired** ⇒ hypothesis substantially supported (well below
4/7 falsification threshold). Kill B firing is a **windowing artefact**,
not a structural failure: the HYG-aligned edu range (2007-04-12 →
2026-04-15) loses the high-Sharpe 2006 portion of iter 037, pushing
edu standalone Sharpe from 0.98 (full range) to 0.96 (windowed),
which in turn raises edu DSR worst-p from iter 037's 0.222 (full
range) to 0.2675 (windowed). The combined Sharpe (0.98) is essentially
identical to the bare iter 037 windowed Sharpe (0.96) plus a tiny
HYG_TSM lift (~+0.02), so the DSR rise is driven by the windowing
loss, not by a genuine HYG-related regression. spy_real and ndx_real
DSR worst-p (0.128 / 0.138) are LOWER than iter 037's full-range
worst-p (0.222), confirming HYG_TSM is mildly DSR-positive on the
common windows; only edu shows the windowing artefact.

## What worked / what didn't

**Worked**:

- **CAGR floor unlock VINDICATED** (the headline finding). The
  hypothesis predicted that pairing iter 037's higher-CAGR anchor
  with HYG_TSM at w=0.10 would clear the CAGR floor 3/3 — confirmed
  with 3.6-7.4 pp slack on each dataset (vs iter 058's 0/3 with
  0.5-6.1 pp slack below floor). **This closes the structural
  question raised by iter 058**: can the CAGR floor be unlocked
  without sacrificing Sharpe edge or MDD ceiling? The answer is YES
  on iter 037 anchor at w=0.10 HYG_TSM, but the score impact is
  neutral because DSR remained the binding constraint.
- **Sharpe edge 25/25, MDD ceiling 15/15, robustness 5/5 retained**:
  the new Pareto-positive elements iter 058 introduced (Sharpe up
  vs iter 046, MDD down) survive the anchor substitution — combined
  Sharpe is +0.01-0.02 above iter 037 on spy/ndx (within noise on
  edu due to windowing loss) and combined MDD is 2.3-3.0 pp BELOW
  iter 037 on each dataset.
- **Markowitz residual = 0.0000 cross-dataset**: the closed-form
  composition is exact (same as iter 058). At 4787-bar samples and
  fixed weights, the empirical Sharpe identity holds to 4 decimal
  places. This vindicates the iter-058 finding that "Markowitz
  closed-form is empirically exact at this scale."
- **G7 cross-lib parity 0.0000 pp on all 3 datasets**: the HYG_TSM
  engine vendored from iter 058 preserves its parity invariant; no
  drift from re-vendoring or path changes.
- **Engine + tests**: 15/15 TDD tests pass in 0.34s. Baseline pytest
  preserved (existing 92 collection errors are pre-iter-058,
  unaffected).
- **Kill F clean at avg corr 0.416** (lower than iter 058's 0.443):
  iter 037's lower equity weight (0.6 SPY vs iter 046's effective
  0.81 SPY through iter 041's 0.7-eq leg) reduces equity-credit
  correlation, **strengthening the diversification quality of HYG
  on the iter 037 anchor over its quality on iter 046** — but
  insufficient to compensate for the lower base Sharpe.

**Didn't**:

- **DSR 0/15 (binding ceiling reaffirmed)**. The +0.02 Sharpe lift
  from HYG_TSM on iter 037 is the same magnitude as on iter 046 (per
  iter 058 results), but iter 037's lower base Sharpe means the
  combined Sharpe (0.98-1.18) is 0.20-0.22 below iter 046's combined
  (1.20-1.40). At n_trials=4329, that Sharpe gap translates to
  worst-p 0.27 vs 0.05 — a multiple-of-5 gap that single-stream
  additions at w=0.10 cannot bridge. **The iter 037 anchor IS
  DSR-bound at 79 regardless of HYG addition** (the structural
  characterization in iter 037's verdict.json's lesson holds
  verbatim).
- **Score 79 = no improvement on iter 037 standalone**. The +1 from
  Sharpe edge bucket (criterion 1: 25 vs iter 037's 25 — both at
  max, no change) plus CAGR floor (15 vs 15 — both at max) is
  exactly offset by no-change on DSR (0 vs 0) and gates (19 vs 19 —
  both 6/7 each). The net Δ vs iter 037 standalone is **0** points.
  The MDD reduction (2-3 pp) and Sharpe lift (+0.01-0.02) are
  Pareto-positive but live BELOW the bucket boundaries (5-pt MDD
  ceiling pass already maxed at 15/15; Sharpe edge bucket already
  maxed at 25/25).
- **Score 79 < iter 058's 85**: the saved-stream-pair Pareto ceiling
  at 85 (iter 058 = iter 046+HYG, iter 046 itself) is **NOT broken**
  by iter 037 substitution. The ANCHOR substitution path is closed
  for THIS w_HYG=0.10 cell. Higher w_HYG would add more CAGR drag
  AND more DSR penalty — not a net positive direction.

## Main lesson (for future iterations)

**Anchor substitution at fixed w=0.10 HYG_TSM trades CAGR-floor for
DSR-pass: iter 037 anchor unlocks CAGR floor 3/3 (vs iter 058's 0/3)
but loses iter 058's DSR pass (15/15→0/15), netting the same 79 STRONG
as bare iter 037.** The two anchors (iter 037 and iter 046+HYG = iter
058) trace **two non-dominating Pareto points** on the CAGR-vs-DSR
frontier at 79-85 STRONG; neither dominates the other on score because
each maxes one constraint that the other fails.

The path to WINNER (90+) requires breaking the CAGR-DSR dual constraint
**simultaneously**, which is **structurally impossible** at fixed
w_HYG = 0.10 because:

- The CAGR-clearing anchors in our library (iter 037, iter 015, iter
  035) all have base Sharpe ≤ 1.17 → combined Sharpe ≤ 1.19 at
  w_HYG=0.10 → DSR worst-p ≥ 0.13 at n_trials=4329 → DSR bucket ≤ 5.
- The DSR-clearing anchors (iter 046 = 1.20-1.38 Sharpe combined =
  iter 058) all have base CAGR ≤ 9.76% → combined CAGR ≤ 9.27% →
  CAGR floor 0/3 → criterion 4 = 0/15.

Therefore the saved-stream-pair Pareto ceiling at 79-85 STRONG cannot
be broken on existing anchors with HYG_TSM. To score 90+, **a NEW
base anchor with simultaneously Sharpe ≥ 1.20 AND CAGR ≥ 12% on real
data** is required before any 3rd-stream addition. None of iters 0-58
delivers this combination.

The likely **viable directions** for iter 060+:

1. **Levered iter 058 at 1.2-1.3× external borrow** (analog of iter
   056 on iter 046, but on the iter-058 saved stream which already
   passes DSR). The CAGR is the binding axis; if external lev at
   3.5% borrow lifts iter 058 CAGR from 9.0/9.0/9.3% to 11.5-12% on
   each dataset, criterion 4 jumps from 0 to 15, and iter 058's
   85 → 100 (capped). Risk: borrow drag may eat the Sharpe edge (iter
   056 closure pattern). **Predicted 80-95 if borrow ≤ 3%.**
2. **Equity-overweight iter 037 + HYG_TSM** at higher equity weight
   (0.75/0.40/0.40 SPY/IEF/GLD with same HYG addition). Trades MDD
   for Sharpe: may push standalone Sharpe to 1.10-1.20 on edu (which
   would push DSR to ~0.10-0.15, criterion 3 bucket = 5-10), while
   preserving CAGR floor (already comfortable). Predicted 84-89.
3. **A non-HYG, non-iter-046, non-iter-037 anchor** — e.g., a
   regime-aware leverage scaling strategy applied to iter 015's
   saved stream (iter 037's lesson recommended this as direction
   #1). Predicted breaks this Pareto if Sharpe ≥ 1.20 AND CAGR ≥
   12%, with HYG_TSM addition as a refinement step.

## Structural dead-ends discovered

- **iter 059 (🥇 STRONG 79, 1/7 KILLS — kill B only) — iter 037 +
  HYG_TSM at w=0.10**: iter 037 standalone CAGR floor advantage
  (15/15 vs iter 058's 0/15) is offset 1:1 by DSR penalty (0/15 vs
  iter 058's 15/15). **Net score 79 = iter 037 standalone 79**. The
  saved-stream-pair Pareto ceiling at **79 (CAGR-clearing branch) /
  85 (DSR-clearing branch)** is now characterized; neither branch
  dominates the other on total score, both are **non-WINNER** at
  fixed w_HYG=0.10. **Closes** the iter-037-as-anchor cell for
  HYG_TSM at this weight.

- **CAGR-DSR dual constraint structural finding**: at n_trials=4329
  and w_HYG=0.10, **no anchor in the iter 0-58 library delivers
  simultaneously CAGR ≥ 0.8×bench (3 datasets) AND DSR p < 0.05**.
  This is a fundamental ceiling on the saved-stream-pair Pareto and
  must be broken by either external leverage (iter 060 candidate
  direction #1) or a new base anchor with Sharpe ≥ 1.20 AND CAGR ≥
  12%.

## Citations used

- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen 2012 multi-leg
  risk-parity decomposition (iter 037 anchor architecture, preserved
  verbatim via iter 037's saved stream).
- `[risk_parity, p.5, p.10-11, ch.1]` — AFP 2012 SSRN 1728082, static-
  stack mechanism (iter 037 base).
- `[leverage_for_the_long_run, p.19-20]` — Hsiao & Williams 2017,
  *J. Index Investing*. 1.5× optimal-leverage zone for 3-asset base
  (iter 037).
- `[systematic_trading]` (Carver) — single-asset boolean TSM (HYG_TSM
  engine vendored from iter 058).
- `[stocks_on_the_move, p.76-77]` — Clenow boolean trend on log price.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (4329).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (numpy ref
  vendored from iter 058, 0.0000 pp parity preserved).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- `[advances_fin_ml, ch.17-18]` — regime detection (forward-looking
  for iter 060+ regime-aware leverage direction).
- Asvanunt, A. & Richardson, S. 2017, "The Credit Risk Premium",
  JPM 43(2), DOI 10.3905/jpm.2017.43.2.090 — credit risk premium
  quantification, trend filter for stress avoidance.
- Markowitz (1952), JoF 7(1) 77-91 — convex combination Sharpe
  identity (closed-form residual = 0.0000).
- Asness, C., Moskowitz, T. & Pedersen, L. 2013, "Value and Momentum
  Everywhere", JoF 68(3) 929-985, DOI 10.1111/jofi.12021 — credit
  TSM positive Sharpe Table III.
- Moskowitz, Ooi & Pedersen 2012, JFE 104(2) 228-250,
  DOI 10.1016/j.jfineco.2011.11.003 — TSM canonical reference.
- Erb, C.B. & Harvey, C.R. 2006, "The Strategic and Tactical Value
  of Commodity Futures", FAJ 62(2) 69-97 — gold-as-diversifier
  (preserved through iter 037 anchor).
- Koijen, Moskowitz, Pedersen, Vrugt 2018, "Carry", JFE 127(2)
  197-225 — gold spot-forward basis ≈ 0; bond term-premium
  decomposition (iter 037 anchor).

## Next iteration suggestions

iter 059 closes the iter-037-as-anchor question for HYG_TSM at w=0.10
constructively (CAGR floor unlocked, MDD lower, Sharpe lift, DSR
unchanged). The next binding constraint is the CAGR-DSR dual
characterized in the Main Lesson. Three structurally distinct
directions point at it, ordered by expected information yield:

1. **Levered iter 058 at 1.2-1.3× external borrow (RECOMMENDED for
   iter 060)**: applies iter 056's pattern (external lev at 3.5%
   borrow on iter 046) to the iter 058 saved stream. iter 058's
   combined CAGR 9.07-9.27% × 1.25 ≈ 11.3-11.6% — pushes 1-2
   datasets across the CAGR floor while preserving Sharpe (DSR-
   clearing) profile. **Predicted: 78-92.** If borrow ≤ 3% and
   Sharpe survives at iter 058 levels, this becomes a path to
   WINNER. Cite Hsiao-Williams 2017 + iter 056 closure pattern.

2. **Equity-overweight iter 037 (0.75/0.40/0.40) + HYG_TSM**: trades
   MDD for Sharpe on the iter 037 anchor. Predicted: standalone
   Sharpe 1.05-1.20 (vs iter 037's 0.98-1.17), DSR worst-p
   ~0.13-0.18 (criterion 3 = 5-10 pts), CAGR floor preserved (3/3),
   MDD borderline (edu likely > 30%, but spy/ndx OK). Score
   predicted 82-87 — **breaks iter 058's CAGR-floor gap by
   structural Sharpe boost**, but doesn't WIN unless DSR clears
   0.05.

3. **Regime-aware leverage scaling on iter 015 base**: iter 037's
   verdict.json explicitly recommended this for iter 038 but the
   loop pivoted to direction 2 instead. Re-visit per
   `[advances_fin_ml, ch.17-18]`: VIX-z-score 2-state HMM, lever
   1.7× in calm regime (z<0), 1.0× in stress (z>0). Iter 015's base
   Sharpe was 0.78 standalone (iter 015 frozen), 0.78×1.7 = 1.33 in
   calm regime, 1.33×0.65 (calm fraction) + 0.78×0.35 = 1.13
   blended. Predicted: Sharpe ~1.10-1.30, CAGR ~13-17%, MDD ~25-30%
   — clears all 5 strict winner conditions if DSR threshold hits.
   Predicted: 80-95 (path-to-WINNER).

**Recommended pick for iter 060**: **direction #1 (levered iter 058)**
because it directly attacks the only remaining binding constraint
(CAGR floor on iter 058) on the existing top-K #1, with minimal new
infrastructure (vendored borrow-cost model from iter 056). If borrow
drag eats the Sharpe edge as in iter 056, iter 061 should pivot to
direction #2 (equity-overweight iter 037 + HYG_TSM); direction #3
(regime-aware leverage) is the deeper-backlog candidate when the
score plateau is confirmed at 85.
