# Iteration 055 — Final Report

## Verdict

🥈 **PROMISING** (score 73/100, winner_conditions_met=false, **0/6 kills
fired** but score regression vs iter 039 confirms broader-region VRP
basket adds NET NEGATIVE on this rubric).

Cross-region 5-leg VRP basket (SPY+QQQ+IWM+EFA+EEM at 1/5 each,
harvest_notional=1.0) underperforms iter 039's 3-leg US-only basket on
score (73 vs 76, −3 pts) — the diversification benefit on post-GFC
windows (spy_real Sharpe +0.11, ndx_real Sharpe +0.04 vs iter 039) is
overwhelmed by the educational long-window Sharpe drop (1.14 → 1.07,
−0.07) caused by EM volatility asymmetry not captured by the static
VXEEM/VIX = 1.30 proxy ratio. Net DSR penalty at cumulative_n_trials=4325
costs 5 score points (worst-p moves from 0.075 → 0.130 bucket: 10 pts
→ 5 pts), only partially offset by +2 gate pts (spy 6/7 → 7/7).

## Headline metrics (top candidate `vrp_basket_eq5_5_10_1m_5regions`)

| dataset | Sharpe (vs frozen bench Δ) | CAGR (vs floor) | MDD (vs ceil) | gates | DSR p |
|---|---|---|---|---|---|
| educational | 1.072 (Δ +0.392 vs 0.68) | 4.74% (FAIL ≥ 9.18%) | 16.18% (PASS ≤ 60.14%) | 6/7 | 0.130 |
| spy_real    | 1.402 (Δ +0.502 vs 0.90) | 5.38% (FAIL ≥ 11.98%) | 5.99% (PASS ≤ 38.70%) | 7/7 | 0.025 |
| ndx_real    | 1.598 (Δ +0.643 vs 0.955) | 6.20% (FAIL ≥ 15.35%) | 4.70% (PASS ≤ 40.12%) | 7/7 | 0.004 |

Δ vs iter 039 (3-leg US-only baseline, score 76):

| dataset | Sharpe Δ | CAGR Δ | MDD Δ | DSR p Δ |
|---|---|---|---|---|
| educational | **−0.068** ⚠️ | −0.04 pp | +1.86 pp | **+0.055** ⚠️ |
| spy_real    | **+0.115** ✅ | +0.16 pp | −1.07 pp | **−0.036** ✅ |
| ndx_real    | **+0.037** ✅ | −0.15 pp | −2.13 pp | **−0.002** ✅ |

The asymmetry is clear: cross-region diversification helps modern
windows (post-2009 spy, post-2010 ndx) and hurts long-history windows
(2006+ educational, which includes EM-stress 2007-2008 + 2010-2011 EU
sovereign + 2015 China + 2020 COVID).

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | 3/3 datasets beat bench + 0.10 (Δ +0.39/+0.50/+0.64; same as iter 039) |
| 2 Gates | **23** | 25 | edu 6/7 (5pts) + spy 7/7 (7pts) + ndx 7/7 (7pts) + cross-bonus +4 = 23. iter 039 was 21 (spy was 6/7). |
| 3 DSR | **5** | 15 | worst p=0.130 (educational) → 0.10 < p < 0.20 bucket = 5 pts. **REGRESSION vs iter 039's 10 pts (worst-p 0.075).** |
| 4 CAGR floor | **0** | 15 | 0/3 datasets pass 0.8×bench (CAGR 4.7-6.2% vs floors 9.18/11.98/15.35%). **Structural T-bill collateral cap, identical to iter 039.** |
| 5 MDD ceiling | **15** | 15 | 3/3 PASS (max MDD 16.18% on edu, well under 60.14% ceiling) |
| 6 Robustness | **5** | 5 | 9/9 sub-windows Sharpe > 0 |
| **total** | **73** | **100+5** | tier: 🥈 **PROMISING** |

iter 039 score breakdown for comparison: 25 + 21 + 10 + 0 + 15 + 5 = 76.

Net delta: gates +2, DSR −5, others identical → **−3 pts**.

## Kill-criteria status

All 6 pre-committed kills documented in `hypothesis.md`:

- **Kill A (basket-corrupts-Sharpe by ≥ 0.10 on ≥ 2 datasets)**:
  ❌ NOT FIRED. edu Δ −0.068 (sub-threshold), spy Δ +0.115 IMPROVES,
  ndx Δ +0.037 IMPROVES. Only 1 dataset shows degradation, by less
  than 0.10.
- **Kill B (DSR-no-improvement: edu p > 0.075 AND ndx p > 0.0059)**:
  ❌ NOT FIRED. edu fires (0.130 > 0.075) but ndx improves (0.0042 <
  0.0059). AND requires both; only one of two firing.
- **Kill C (MDD > 35% any dataset)**: ❌ NOT FIRED. Max MDD 16.18%
  (educational), well under 35% threshold.
- **Kill D (G7 cross-lib > 3pp)**: ❌ NOT FIRED. All 3 datasets at
  0.0000pp (perfect parity, 9th consecutive iter at 0.0000pp on G7).
- **Kill E (score-regression: score < 73)**: ❌ NOT FIRED — just
  barely. Score = 73 exactly equals the kill threshold; strict less-than
  test passes. **The score is on the boundary — this is a marginal
  PROMISING outcome.**
- **Kill F (sub-window-collapse < 6/9)**: ❌ NOT FIRED. 9/9 sub-windows
  Sharpe > 0.

**0/6 kills fired**, but the iteration is materially below the predicted
range (76-81). The DSR regression is the diagnostic killer — Sharpe
edge and gates both PASS or improve, but the long-history Sharpe drop
(edu 1.14 → 1.07) costs DSR points that no other criterion can recover.

## Configuration tested

Single pre-committed cfg (`vrp_basket_eq5_5_10_1m_5regions`):
- Tickers: SPY + QQQ + IWM + EFA + EEM
- Weights: equal 1/5 each
- IV scales: SPY 1.0 / QQQ 1.10 / IWM 1.25 / EFA 1.05 / EEM 1.30
- Strikes: 5/10 % OTM (k_long=0.95, k_short=0.90)
- DTE: 21 days, monthly roll
- Cost: 5 bps per leg per roll
- harvest_notional = 1.0 (preserved from iter 026/039)
- rf = 2% on T-bill collateral
- Cross-lib G7: pandas vs numpy ΔCAGR = 0.0000 pp on all 3 datasets

## Gate detail (educational — only failing dataset)

| gate | result | pass? |
|---|---|---|
| G1 PBO | N=1 → undefined; vacuous PASS | ✅ |
| G2 DSR | p=0.1301 with n_trials=4325 (would PASS at n_trials < ~1500; cumulative penalty drives FAIL) | ❌ |
| G3 WF | 8/8 windows positive Sharpe + MDD < 25% | ✅ |
| G4 OOS | OOS Sharpe = +1.492 (last 30%) | ✅ |
| G5 FWD | Post-2020 Sharpe = +1.293 | ✅ |
| G6 Boot | 99.9% CI low = +0.385 | ✅ |
| G7 Xlib | ΔCAGR 0.0000 pp | ✅ |

Spy_real and ndx_real both clear 7/7 (DSR PASSES at 0.025 and 0.004
respectively).

## What worked / what didn't

**Worked**:
- **Engine + cross-lib parity**: pandas vs numpy 0.0000 pp ΔCAGR on
  all 3 datasets, validating the 5-leg generalization of iter 039's
  pricer (`[advances_fin_ml, p.31-34]`).
- **Post-GFC Sharpe improvement (spy_real)**: 1.40 vs iter 039's 1.29
  — a +0.11 Sharpe improvement, validating the cross-region
  diversification thesis on the modern regime. EFA + EEM legs added
  net positive in this window.
- **MDD all under 17%**: even with 5 legs and 2008 + 2020 + 2022 in
  the educational window, max MDD is 16.18% (educational). The
  5-leg basket diversifies tail-events as predicted.
- **Sub-window robustness**: 9/9 sub-windows Sharpe > 0; the
  diversification keeps Sharpe positive in every 1/3 epoch.
- **TDD**: 5 unit tests (shape, single-asset reduction, cross-lib
  parity, sign-flip identity, negative-weight rejection) all pass —
  basket implementation is correctly generic over leg count.

**Didn't work — the failure mode**:
- **Educational Sharpe REGRESSED 1.14 → 1.07 (−0.068)**. The 2006-2009
  segment (EM-stress 2007-2008 financial + EM-shock 2010-2011) damages
  the EFA + EEM legs disproportionally. CBOE's actual VXEEM data
  (post-2008) shows the EEM/SPY implied-vol ratio drifts in the
  1.20-1.50 range with notable spikes beyond 1.50 during EM crises;
  our static 1.30 multiplier under-prices EEM's tail risk and
  overstates harvest. EFA's 1.05 multiplier may also under-price
  developed-international spillover risk during US-led sell-offs.
- **DSR penalty kicks in hard at cumulative_n_trials=4325**. The edu
  Sharpe drop from 1.14 → 1.07 moves DSR p-value from 0.075 (10 pts)
  to 0.130 (5 pts). At 4325 cumulative trials, even small Sharpe
  drops have outsized DSR penalty (de Prado's deflation formula
  `[advances_fin_ml, p.222-223]` applies a stricter Bonferroni-style
  penalty per trial).
- **CAGR floor remains structural**: T-bill-collateralized VRP harvest
  caps CAGR at ~5-6%/yr, regardless of leg count. The 5-leg basket's
  CAGR is 4.74/5.38/6.20% — essentially identical to iter 039's
  5.09/5.22/6.35%. Neither passes any of the 9.18 / 11.98 / 15.35%
  floor thresholds. **This confirms the BASE_MEMORY claim: "VRP-
  harvester family 76 ceiling … structural to T-bill collateral".**
- **Net diversification effect is asymmetric across regimes**. Cross-
  region helps post-GFC equity-stress events (EAFE/EM uncorrelated
  with US) but hurts long-history because the IV scaling proxies
  cannot capture EM tail asymmetry pre-VXEEM-publication-era (CBOE
  VXEEM only began publishing late 2007; for our 2006-2007 segment we
  effectively use the post-2008 ratio retroactively, which is
  conservative on calm periods but not crisis-conservative).

## Main lesson (for future iterations)

**Cross-region VRP basket adds NET NEGATIVE on this rubric** — the
post-GFC Sharpe improvement (+0.11 on spy, +0.04 on ndx) does not
compensate for the long-history Sharpe regression (−0.07 on educational)
once the cumulative_n_trials DSR penalty is applied. The 3-leg US-only
basket (iter 039) is **Pareto-optimal** within the broader VRP basket
family on this loop's rubric, and iter 055 closes the cross-region
extension axis.

The deeper structural lesson, contributing to a recurring closure pattern
across iters 026 / 027 / 028 / 029 / 030 / 031 / 039 / 040 / 055:

- **VRP family ceiling = 76 STRONG (iter 039)**, identical to BASE_MEMORY's
  prior diagnosis but now with 9 iterations supporting it.
- The CAGR floor structural cap at ~5-6% per year is **invariant to
  basket composition** — adding 2 more cross-region legs does not raise
  the harvest yield, only redistributes σ. This is a direct consequence
  of T-bill being the collateral asset; any T-bill-collateralized
  short-vol overlay at harvest_notional = 1.0 caps at this CAGR
  regardless of leg diversity.
- Path to break the 76 ceiling in the VRP family is structurally
  blocked unless EITHER (a) the collateral is replaced with an
  equity-rich asset (already tried in iter 032 — corrupts via ρ_SPY ≈
  0.97 absorption), OR (b) `harvest_notional > 1` (iter 027 closure —
  rf-bonus diluted by leverage), OR (c) a cross-region IV signal is
  used per leg (no per-leg IV proxy is available in cache for EFA/EEM
  pre-2008; cannot test in the loop's data layer).

**Implication for hunt loop**: the broader-region VRP path predicted
in BASE_MEMORY (#1 candidate, predicted 76-80) **delivered 73 PROMISING**
— at the low end of expectations. This is the second confirmation
(after iter 040's vol-target on iter 039 → 69) that iter 039 is the
local maximum within the VRP family. **Family is now formally closed
at score 76 ceiling, with iter 055 as the cross-region extension
falsification**.

## Structural dead-ends discovered

Add to `DEAD_ENDS.md`:

- **Cross-region VRP basket (SPY+QQQ+IWM+EFA+EEM at 1/5 each, harvest_
  notional=1.0)** — score 73 PROMISING, materially worse than iter
  039's 76 STRONG (3-leg US-only). The cross-region diversification
  benefit on post-2009 windows (Sharpe +0.04 to +0.11) is overwhelmed
  by the educational long-window Sharpe regression (−0.068) and the
  associated DSR penalty (worst-p 0.075 → 0.130) at
  cumulative_n_trials = 4325. **Don't re-test broader-region VRP
  baskets at any equal-weight composition — the static VXEEM / VIX =
  1.30 proxy is unable to capture EM tail volatility asymmetry
  pre-2008**.

- **VRP-harvester family (026/031/039/040/055) closure confirmed
  at score 76 ceiling**: T-bill-collateralized short-put-credit-
  spread harvest at harvest_notional = 1.0 caps CAGR at ~5-6%/yr
  regardless of basket composition (3-leg US-only iter 039: 5.09%/
  5.22%/6.35%; 5-leg cross-region iter 055: 4.74%/5.38%/6.20%). All
  three CAGR floor thresholds (9.18% / 11.98% / 15.35%) are
  structurally unreachable in this family. The family is now
  Pareto-saturated at iter 039 (best score 76).

## Citations used

- `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP
  diversification (primary).
- `[volatility_trading, ch.3, p.41, p.217]` — Sinclair (2013) VRP
  mechanics + capped tail.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- `[advances_fin_ml, p.31-34]` — cross-library parity G7.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1, vacuous for N=1).
- Bondarenko, O. (2014). "Why Are Put Options So Expensive?"
  *Quarterly Journal of Finance* 4(3) 1450015.
- Carr, P. & Wu, L. (2009). "Variance Risk Premia."
  *Review of Financial Studies* 22(3) 1311-1341.
- Driessen, J., Maenhout, P. & Vilkov, G. (2009). "The Price of
  Correlation Risk: Evidence from Equity Options."
  *Journal of Finance* 64(4) 1377-1406.
- Bakshi, G. & Madan, D. (2006). "A theory of volatility spreads."
  *Journal of Financial Economics* 81(2) 471-518.
- Asness, C. S., Moskowitz, T. J. & Pedersen, L. H. (2013). "Value and
  Momentum Everywhere." *Journal of Finance* 68(3) 929-985.
- Israelov, R. & Klein, M. (2016). "Risk and Return of Equity Index
  Collar Strategies." AQR working paper, SSRN 2784825.

## Next iteration suggestions

The iter 055 result + the broader BASE_MEMORY closures (037+026/041+026
/037+046/041+039/iter-046-axes/iter-039-vol-target/iter-054 cross-
sectional/iter-055 broader-VRP) point to the loop having exhausted the
**multi-leg static-overlay** family at the iter 046 STRONG-85 ceiling
and the **VRP-overlay** family at iter 039 STRONG-76 ceiling. Path
forward needs to shift away from these pattern families.

Iter 056 candidates (priority order):

1. **(RECOMMENDED) Levered iter 046 (1.2× / 1.3× simple notional)** —
   the sole untested axis on iter 046 (already closed: weight sweep
   047 / output gate 048 / +gold-TSM 049+050 / multi-feature regime
   044). iter 046 has MDD 18/15/15 — at 1.3× simple leverage, MDD
   becomes 23/20/20 (still well under MDD ceilings 60/38/40). At 1.3×,
   expected CAGR moves 9.16/9.45/9.76 → 11.6/12.0/12.3 (lift edu by
   −0.6 vs floor 9.18 = MISS, lift spy 12.0 vs floor 11.98 ≈ EQUAL,
   lift ndx 12.3 vs floor 15.35 = MISS). May lift CAGR floor to 1/3 or
   2/3 datasets, gaining +5 to +10 score points → 90-95 candidate
   range. Distinct from iter 027 (which closed harvest_notional > 1
   on T-bill VRP — different leverage mechanism applied to equity-
   rich iter 046 50/50). Citations: `[advances_fin_ml, p.31-34]` +
   `[risk_parity, ch.5]` + `[stocks_on_the_move]`. ~30-45 min impl
   (single cfg, reuse iter 046 stream-multiply).

2. **Asness-Moskowitz-Pedersen (2013) global value-momentum
   overlay** — long-only top-K composite of equity/bond/commodity ETFs
   with global value (CAPE-style) + momentum signals. Distinct from
   iter 023's TSM 3-ETF (closed: HOP needs 67 markets) and iter 054's
   single-stock cross-sectional (closed: data layer). Uses ETF
   universe (8-10 macro sleeves) but with composite signal designed
   for ≤ 12 assets per AMP 2013 §III. ~90 min impl. Citation:
   AMP 2013 + `[stocks_on_the_move]`.

3. **Plano C sleeve evaluation as baseline documentation** —
   factor-tilted ETFs (GDE/AVUV/AVDE/AVEM/BTGD per
   `portfolio-aposentadoria.md`). Inception dates 2018-2024 problematic
   for 17y windows; need FF93 long-format proxies for educational. As
   a "mandate-aligned baseline benchmark" iteration even a PROMISING
   tier (~65-70 predicted) is informative. Citation:
   `[fact_based_investing]` + Fama-French 1993.
