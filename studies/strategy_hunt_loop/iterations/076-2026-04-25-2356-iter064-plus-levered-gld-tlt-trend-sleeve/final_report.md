# Iteration 076 — Final Report

**Date:** 2026-04-25 23:56 → 2026-04-26 00:35
**Hypothesis:** iter 064 + LEVERED GLD/TLT trend sleeve ensemble.
Extend iter 075 by sweeping the sleeve's target_vol up to 0.30 with
leg_cap=3.0 and honest leg-level borrow drag at 4.5%/yr (industry-
standard retail portfolio-margin SOFR + 0.5-1.0% spread). 4 target_vol
× 5 w_sleeve = 20 cfgs.
**cumulative_n_trials after iter 076:** 4462 (was 4402; +60 = 20 cfgs ×
3 ds).

---

## Verdict

🥇 **STRONG** (score **85/100** under v2 native per-iter DSR
convention; `winner_conditions_met=False`, **4/5 strict winner
conditions met**, CAGR floor remains the sole strict failure — same
gap as iter 075).

**Best cfg: `iter076_lev_tv015_w015`** (target_vol=0.15, w_sleeve=0.15,
leg_cap=3.0, borrow_rate=0.045).

The hypothesis was **partially validated and partially falsified**:

- ✅ **KILL A clean — borrow-drag math is correct**: G7 cross-lib
  parity = 0 pp on ALL 20 cfgs × 3 datasets (Δ_max < 1e-9 element-wise).
- ❌ **KILL B FIRED — leverage does NOT lift sleeve CAGR proportionally**:
  At target_vol=0.30 the sleeve gross CAGRs are 5.45 / 3.94 / 2.65% on
  edu / spy / ndx — three of three below the 6% threshold. Compare to
  iter 075's unlevered (tv=0.10) sleeve CAGRs of 3.28 / 2.78 / 2.33%:
  3× nominal leverage produced only 1.7× / 1.4× / 1.1× CAGR scaling
  because borrow drag eats ~50-65% of the additional leverage benefit.
  **Pre-committed math vindicated**.
- ✅ **KILL C clean — combined Sharpe does NOT regress on best cfg**:
  Δ_064 = +0.010 / −0.006 / −0.028 on edu / spy / ndx — all above the
  −0.05 regression threshold. 0/3 datasets cross the threshold; would
  need ≥ 2 to fire.
- ✅ **KILL D clean** — best score 85 ≥ 75.
- ✅ **KILL E clean** — G7 ≤ 3pp on all cfgs (max 0 pp).
- ✅ **KILL F clean** — PBO 0.048 / 0.000 / 0.000 cross-dataset (vs
  iter 075's 0.86 / 0.60 / 0.46). **The wider 4×5 grid solved iter
  075's narrow-grid PBO inflation.**
- ✅ **KILL G clean** — DSR worst-p well below 0.05 (Sharpe 1.32+ over
  4 226 bars with n_trials=20).

**6 of 7 kills clean. Only KILL B fires.** The borrow-drag mechanism
behaves exactly as the pre-committed math predicted: linear-leverage on
a Sharpe-0.5-class strategy at 4.5%/yr borrow eats most of the CAGR
scaling, leaving only a fraction of the gross-of-borrow benefit.

The hypothesis's central question — **"does leverage on the GLD/TLT
trend sleeve solve the joint (low ρ × high CAGR) constraint exposed by
iter 075?"** — is answered: **NO**. At any tested target_vol up to 0.30,
combined CAGR remains 0/3 below the strict-winner floors 9.18 / 11.98 /
15.35%. **Leverage cannot mechanically resolve the CAGR floor on
iter-064-anchored ensembles when the 2nd leg's pre-borrow Sharpe is
~0.5 and borrow is ≥ 2.5%/yr.**

That said, iter 076 **scores +4 vs iter 075** (85 vs 81) because the
wider 4×5 grid lifts G1 PBO from FAIL to PASS on edu/spy and produces
a best cfg with 7/7/7 gates instead of 6/6/7. This is structural
improvement on the gate-pass axis even though the underlying mechanism
question (leverage-as-CAGR-fix) was falsified.

---

## Headline metrics (best cfg `iter076_lev_tv015_w015`)

| dataset | Sharpe (Δ frozen / Δ064) | CAGR (vs floor) | MDD (vs ceiling) | gates | DSR p (v2 n=20) |
|---|---|---|---|---|---|
| educational | **1.2310** (+0.551 / +0.010) | 8.80% (**−0.38 pp** below 9.18%) | 15.74% (−44.4 pp under 60.1%) | 7/7 | 1.31e-5 |
| spy_real    | **1.3253** (+0.425 / −0.006) | 9.10% (**−2.88 pp** below 11.98%) | 13.99% (−24.7 pp under 38.7%) | 7/7 | 1.45e-5 |
| ndx_real    | **1.3523** (+0.397 / −0.028) | 9.15% (**−6.20 pp** below 15.35%) | 13.48% (−26.6 pp under 40.1%) | 7/7 | 1.21e-5 |

Robustness sub-windows (3 datasets × 3 chronological thirds = 9 total):
9/9 positive Sharpe → +5 robustness bonus.

### Strict winner-conditions check (5 conditions per `WINNER_AND_RANKING.md`)

1. **Sharpe edge ≥ +0.10 on ≥ 2 of 3 datasets** ✅ — 3/3 pass (+0.551 / +0.425 / +0.397)
2. **Gate cross-dataset (edu ≥ 5/7, spy/ndx ≥ 4/7)** ✅ — 7/7/7 all clear; cross-ds bonus
3. **DSR worst p < 0.05** ✅ — worst p = 1.45e-5
4. **CAGR ≥ 0.8 × bench on ≥ 2 of 3 datasets** ❌ — 0/3 pass (sleeve still dilutes despite leverage; borrow drag offsets gross-CAGR scaling)
5. **MDD ≤ bench + 5 pp on ≥ 2 of 3 datasets** ✅ — 3/3 pass

**4/5 strict winner conditions met. CAGR floor remains the sole gap
(same as iter 075).**

---

## Score breakdown (best cfg, v2 native convention)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | 3/3 datasets clear bench+0.10 (full + bonus) |
| 2 Gates | **25** | 25 | edu 7/7 (+7) + spy 7/7 (+7) + ndx 7/7 (+7) + cross-ds bonus (+4), capped at 25 |
| 3 DSR | **15** | 15 | worst p = 1.45e-5 with v2 n_trials=20 |
| 4 CAGR floor | **0** | 15 | edu 8.80 < 9.18; spy 9.10 < 11.98; ndx 9.15 < 15.35 — 0/3 pass |
| 5 MDD ceiling | **15** | 15 | all 3 pass with huge margin (5+5+5) |
| 6 Robustness bonus | **5** | 5 | 9/9 sub-windows positive across datasets |
| **total** | **85** | **100+5** | tier: **🥇 STRONG**; CAGR floor sole strict gap |

### Per-cfg score grid (full sweep, v2 native)

| target_vol | w=0.15 | w=0.25 | w=0.35 | w=0.45 | w=0.50 |
|---|---|---|---|---|---|
| **0.15** | **85** | 85 | 85 | 85 | 80 |
| **0.20** | **85** | 85 | 85 | 70 | 63 |
| **0.25** | **85** | 85 | 80 | 61 | 56 |
| **0.30** | **85** | 85 | 70 | 56 | 39 |

**Pattern**: 8 cfgs score 85 — concentrated at low w_sleeve (0.15-0.25)
where the iter 064 base dominates and the sleeve-leverage drag impact
is muted. Score degrades as w_sleeve rises (sleeve drag becomes
material in the linear blend) and as target_vol rises (more
borrow-drag accumulates per leg). The 4×5 grid is **structurally well-
behaved** — score variation has clear monotonic gradients in both
dimensions, consistent with a non-overfit landscape (PBO 0.05 confirms
this empirically).

The "best 85" plateau IS the same plateau as iter 058/072 prior STRONG
ceiling — and falls one tier short of iter 064's TOP-K #1 90.

---

## Kill criteria evaluation (pre-committed)

| Kill | Threshold | Status | Detail |
|---|---|---|---|
| **A** | borrow-drag math wrong (G7 > 1e-3 pp on any cfg) | ✓ clean | 0 pp on all 20 cfgs; pure-numpy reference matches pandas impl 1e-9 |
| **B** | sleeve gross CAGR ≤ 6% at tv=0.30 on ≥ 2 ds | ❌ FIRED | edu 5.45% / spy 3.94% / ndx 2.65%; **all 3 below 6%** — borrow drag eats CAGR scaling |
| **C** | combined Sharpe regress ≥ 0.05 vs iter 064 on ≥ 2 ds | ✓ clean | best cfg Δ +0.010 / −0.006 / −0.028 (none reach −0.05) |
| **D** | best cfg score < 75 (below STRONG) | ✓ clean | 85 ≥ 75 |
| **E** | G7 cross-lib > 3 pp CAGR on any ds | ✓ clean | max 0 pp across 60 dataset×cfg G7 checks |
| **F** | PBO grid-level ≥ 0.5 on ≥ 2 ds | ✓ clean | 0.048 / 0.000 / 0.000 — wide grid solved iter 075's narrow-grid PBO |
| **G** | DSR worst-p ≥ 0.05 (v2 n=20) | ✓ clean | worst p = 1.45e-5 |

**1/7 kills fired (B).** This is informative: borrow-drag at industry-
standard retail rates eats the leverage benefit on a Sharpe-0.5
strategy as the pre-committed math predicted.

---

## What worked / what didn't

**Worked.** The 4×5 grid design fixed the narrow-grid PBO inflation
that bit iter 075 (PBO 0.86 edu → 0.048 edu, a 18× drop). Wider grid
yields a best cfg with **all 7/7 gates passing on all 3 datasets** — a
first for any iter-064-anchored ensemble in the hunt loop. This is
structural improvement on the gate-pass axis, lifting the best cfg
score from 81 (iter 075) to 85 even though the underlying mechanism
hypothesis was falsified.

The borrow-drag implementation is **mathematically clean**: G7 = 0pp
on all 20 cfgs × 3 datasets, all 23 TDD tests pass, and the iter-075
baseline reproduces bit-for-bit at target_vol=0.10 / leg_cap=1.0 /
borrow=0 (test 14). The numpy-pure reference matches pandas impl to
1e-9 element-wise across the entire 4×5 grid (test 8 + test 21).

**Didn't work.** Leverage-as-CAGR-fix on the sleeve **fails by the
exact mechanism predicted in the hypothesis**: the borrow drag at 4.5%/yr
eats most of the CAGR scaling expected from linear leverage. Sleeve
gross CAGR at tv=0.30 is 5.45 / 3.94 / 2.65% — only 1.7× / 1.4× / 1.1×
the iter 075 unlevered CAGRs of 3.28 / 2.78 / 2.33%, well below the 3×
ratio implied by 3× leverage on a Sharpe-preserving primitive. This
matches the leverage-Sharpe identity from
`[leverage_for_the_long_run, ch.5]`:

```
Sharpe_post_borrow ≈ S_pre - (lev - 1) × spread / σ_T × t_in_position
```

For S_pre ≈ 0.50, lev = 2.5, spread = 0.045, σ_T = 0.25,
t_in_position ≈ 0.7:

```
Sharpe_post ≈ 0.50 - (2.5 - 1) × 0.045 / 0.25 × 0.7 ≈ 0.31
```

Empirically observed at tv=0.25: spy_real sleeve Sharpe = 0.337
(predicted 0.31 — within 0.03). At tv=0.30: spy_real sleeve Sharpe =
0.300 (predicted ~0.27 — within 0.03). The math is honest.

The combined CAGR with iter 064 at the highest tested w_sleeve where
combined Sharpe doesn't crater (w=0.15) is best 9.28% spy at tv=0.30 —
still 2.7 pp below the 11.98% spy_real strict-winner floor. **No
combination of (target_vol ∈ [0.15, 0.30], w_sleeve ∈ [0.15, 0.50])
clears the spy_real CAGR floor**, vindicating the hypothesis's
pre-committed prediction.

---

## Main lesson (for future iterations)

**Leverage on a Sharpe-0.5 non-equity sleeve at 4.5% borrow CANNOT
mechanically resolve iter 075's joint constraint** (need ρ < 0.5 vs
iter 064 AND sleeve standalone CAGR ≥ 8-10%). The borrow drag
proportionally reduces the gross-CAGR scaling such that the post-drag
sleeve CAGR plateaus around 4-5% (vs iter 075's 3%) — a 30-60% lift
that is NOT enough to push combined CAGR over the 11.98% spy floor at
any practical w_sleeve.

Iter 076 vindicates the iter 075 lesson's pre-committed math AND
exposes a deeper structural finding: **the iter-064-anchored ensemble
family has hit the 85 STRONG ceiling via gate-pass improvement (PBO,
gate count) without unlocking the CAGR floor** that defines the
remaining 5th winner condition.

**Closes**: levered non-equity Faber-trend single-cap-borrow-charged
sleeve as iter-064 ensemble at score 85 STRONG (matches iter 058 / 072
prior STRONG ceiling).

The lever for 90+→ 95 unlock therefore requires a 2nd leg with
**naturally higher pre-borrow Sharpe** (say 0.7-1.0+) so that
applying any borrow primitive doesn't crater the post-drag risk-
adjusted return below useful thresholds. Candidates with documented
Sharpe ≥ 0.7 standalone:

- **DBMF managed-futures** (SocGen Trend Index ETF; Sharpe 0.5-0.7
  historical, but with the long-term Sharpe LIFT of about +0.2 on a
  60/40 baseline `[advances_fin_ml, ch.20]`)
- **Long-short MTUM-VLUE factor sleeve** (Carhart 1997, AMP 2013;
  Sharpe 0.6-0.8 on dollar-neutral construction)
- **Cross-sectional momentum (Tiingo CRSP)** — blocked on data-quality
  for the hunt loop
- **EM / DM equity rotation w/ trend filter** (VEA/VWO not as a
  standalone 2nd leg but as an iter 064 base-replacement candidate)

iter 077 should be **EITHER** download DBMF/MTUM/VLUE Tiingo data OR
pursue a fundamentally different non-ensemble mechanism (e.g., Hurst-
regime adaptive trend on multi-asset).

---

## Structural dead-ends discovered

**Add to `DEAD_ENDS.md`**:

> **iter 076 (iter 064 + LEVERED GLD/TLT trend sleeve ensemble; 20
> cfgs at target_vol ∈ {0.15, 0.20, 0.25, 0.30} × w_sleeve ∈ {0.15,
> 0.25, 0.35, 0.45, 0.50}, leg_cap=3.0, borrow=4.5%/yr):** 85 STRONG,
> 4/5 strict winner conds met (CAGR floor sole gap; same as iter 075).
> 1/7 kills fired (B — sleeve gross CAGR ≤ 6% at tv=0.30 on 3/3 ds).
> Engine perfect (23/23 TDD, G7=0pp on all 20 cfgs, Markowitz residual
> = 0, robustness 9/9). Best cfg `iter076_lev_tv015_w015` lifts gates
> to 7/7/7 (vs iter 075's 6/6/7) and PBO to 0.05/0/0 (vs iter 075's
> 0.86/0.60/0.46) via wider 4×5 grid. KILL B confirms borrow-drag
> identity from `[leverage_for_the_long_run, ch.5]`: at retail-margin
> 4.5% borrow on a Sharpe-0.5 sleeve, leverage scaling produces only
> 1.7× / 1.4× / 1.1× CAGR lift (vs 3× nominal leverage), yielding
> sleeve CAGR plateau ~4-5% — INSUFFICIENT to push combined CAGR over
> the 11.98% spy_real strict-winner floor at any tested cfg.
> **Closes the iter-064 + leg-levered single-cap-borrow-charged Faber-
> trend non-equity sleeve ensemble axis at 85 STRONG.** The 90 ceiling
> persists across BOTH unlevered (iter 075 = 81) AND levered (iter 076
> = 85) variants of the iter-064-anchored sleeve ensemble family. The
> +4 score lift comes from grid-design improvement (PBO + gate count),
> NOT from the underlying leverage hypothesis. Direction shift implied:
> **90+→95 unlock requires a 2nd leg with naturally higher pre-borrow
> Sharpe (≥ 0.7-1.0)** that survives the leverage-Sharpe identity at
> ≥ 2.5%/yr borrow without cratering. Candidates: DBMF managed-futures
> (Tiingo not cached, ~5y history), long-short MTUM-VLUE factor pair
> (not cached), cross-sectional momentum (CRSP-blocked). All require
> data ops not done in iter 076.

---

## Citations used

### Primary

- `[leverage_for_the_long_run, ch.5]` — Hsiao-Williams (2017) borrow-
  cost primitive at futures-implied vs retail-margin spreads; informs
  the leverage-Sharpe identity that drives iter 076's pre-committed
  KILL B prediction.
- **Faber, M.** (2007). "A Quantitative Approach to Tactical Asset
  Allocation." SSRN 962461 — long-only SMA-200 trend filter on multi-
  asset baskets (sleeve construction core, inherited from iter 075).

### Supporting

- **Frazzini, A., & Pedersen, L. H.** (2014). "Betting Against Beta."
  *Journal of Financial Economics* 111(1), 1-25.
  DOI 10.1016/j.jfineco.2013.10.005 — borrow-frictions on levered low-
  vol strategies; same primitive used in iter 056 (3.5% retail) and
  iter 060 (2.5% futures). Iter 076 applies at the leg-level rather
  than post-stream.
- `[stocks_on_the_move, p.81]` — trend lookback rationale (inherited).
- `[risk_parity, ch.5]` — Asness, Frazzini, Pedersen (2012) FAJ 68(1).
  Risk-parity equal-weighting of GLD+TLT sleeve legs.
- **Erb, C., & Harvey, C.** (2006). "The Strategic and Tactical Value
  of Commodity Returns." *FAJ* 62(2), 69-97. DOI 10.2469/faj.v62.i2.4084.
- **Markowitz, H.** (1952). "Portfolio Selection." *J. Finance* 7(1),
  77-91. DOI 10.1111/j.1540-6261.1952.tb01525.x.
- `[volatility_trading, p.218]` — Sinclair (2013) inverse-vol sizing.
- `[advances_fin_ml, p.222-223]` — DSR with n_trials (per-iter v2).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead).
- **iter 064 saved stream** (anchor; verified iter-064-bit-stable load).

---

## Next iteration suggestions

The iter 076 result establishes the deeper joint-constraint structure:
**90+→95 unlock requires a 2nd leg with naturally high pre-borrow Sharpe
(≥ 0.7-1.0) that survives the borrow-Sharpe identity** — leverage alone
on a Sharpe-0.5 sleeve is insufficient, as iter 076 mechanically proved.
Three structurally distinct iter 077 candidates that target this:

1. **iter 077 — DBMF managed-futures Tiingo download + ensemble** —
   Download DBMF (iMGP DBi Managed Futures, inception 2019-05) into
   `data/tiingo/daily/prices/`. Ensemble with iter 064 at the same
   weight-grid as iter 075. Caveat: only ~6.5y of data → spy_real
   window 2009-06 → 2026-04 forces iter 064 + cash-substitute pre-2019
   for the sleeve, which adds an awkward window asymmetry. Expected
   sleeve Sharpe 0.5-0.7 with ρ ≈ 0.0-0.2; if Sharpe holds the
   hypothesis predicts CAGR ~7-10% — clear boundary case for the
   joint-constraint test. Citations: Asness-Moskowitz-Pedersen (2013)
   JoF 68(3) DOI 10.1111/jofi.12021. **RECOMMENDED #1.**

2. **iter 077 — Long-short MTUM-VLUE factor sleeve Tiingo download** —
   Download MTUM (iShares MSCI USA Momentum, 2013-05) and VLUE (iShares
   MSCI USA Value, 2013-05) — both have 13-year history. Construct
   dollar-neutral long-short pair (Carhart 1997 + AMP 2013). Standalone
   Sharpe 0.4-0.7, ρ ≈ 0.0-0.3 with SPY by construction. If Sharpe ≥
   0.7 holds, this would be a cleanest test of the high-Sharpe-2nd-leg
   hypothesis. Citations: Carhart (1997) JoF 52(1) + AMP (2013).

3. **iter 077 — Multi-asset Hurst-regime adaptive trend** — Pursue
   BASE_MEMORY direction #4: continuous Hurst-exponent-based regime
   detection (Mandelbrot/Peters/Lo-MacKinlay) as a structurally novel
   2nd-leg mechanism that is qualitatively different from binary SMA-
   regime. Higher implementation cost but tests a NEW mechanism class
   (continuous-regime memory-based trend) rather than parameter sweeps
   on saturated mechanisms.

**Ranked recommendation**: #1 (DBMF download) — short data window is
acceptable as a JOINT-constraint test on the post-2019 era; if DBMF
clears the joint constraint cleanly, it provides empirical anchor for
a follow-up with longer-history CTA proxies (e.g., SocGen Trend Index
or constructed CTA proxy). #2 (MTUM-VLUE) has cleaner full-history
test but conditional on dollar-neutral construction holding the
hypothesised ρ ≈ 0. #3 is informationally richest but highest cost.
