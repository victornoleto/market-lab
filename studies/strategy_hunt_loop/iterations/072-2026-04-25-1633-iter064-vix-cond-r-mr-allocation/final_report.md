# Iteration 072 — Final Report

## Verdict

🥇 **STRONG** — score **85/100** (1 step BELOW the joint TOP-K #1 4-way tie
of iter 064/069/070/071 at 90), **winner_conditions_met=False** (4/5 strict
— Sharpe edge ✓, gates cross-ds ✓, DSR ✓, MDD ceiling ✓; CAGR floor ✗ 0/3
this iter), **6/10 kills fired (A primary; B+C+D+E+I diagnostic)**.

This iteration tests the iter 071 final report's recommended direction #1:
**hierarchical regime-conditional allocation of the validated calm-aggressive
r_mr stream**. The structural hypothesis was that VIX-binary regime
conditioning (calm-only activation) would amplify r_mr's calm-Sharpe
contribution (0.82-0.93 cross 3 ds, vindicated in iter 071 KILL D) while
avoiding the stress-regime CAGR dilution — breaking iter 071's KILL A
(Δ064 Sharpe < +0.02 on ≥ 2 ds).

```
gate_stress[t] = (VIX[t-1] >= 20)                           # Whaley 2009 median
w_mr[t]    = w_mr_calm if not gate_stress[t] else w_mr_stress
w_046[t]   = (1 - w_mr[t]) * 0.90                           # iter 064 9:1 base
w_qqqt[t]  = (1 - w_mr[t]) * 0.10
cost[t]    = 5bp · |Δw_mr|                                  # flip cost
r_072[t]   = w_046·r_046 + w_qqqt·r_qqqt + w_mr·r_mr - cost
```

**Engine integrity perfect**: 16/16 TDD tests pass (weight invariants,
Σw≡1, no-peek shift(1) on VIX, regime-conditional flip cost, w_mr_stress=0
collapse to iter 064 base, w_mr_calm=w_mr_stress collapse to iter 071
static, cross-lib parity). G7 cross-lib **0.0000 pp on all 4 cfgs × 3
datasets** (max ret diff = 0.0). Σw deviation from 1.0 < 1e-12 every bar.

**Key empirical findings**:

1. **KILL A FIRES — regime-conditioning DOES NOT clear iter 071's threshold.**
   Best cfg (calm010_stress005) Δ064 Sharpe is +0.013/+0.019/+0.016 — same
   marginal magnitude as iter 071 (+0.016/+0.018/+0.015), still under +0.02
   on 3/3 datasets.
2. **KILL C FIRES — regime-conditioning is no better than static.** Best cfg
   Δ071_th10w005 Sharpe is −0.004/+0.001/+0.001 — essentially zero on all
   3 ds. Dynamic VIX-conditional allocation provides ZERO incremental
   benefit over iter 071's uniform static blend.
3. **KILL E FIRES — regime mechanism is structurally INVERTED at portfolio
   level.** r_072 calm_S/stress_S < 1.0 on 3/3 (calm 1.04-1.08 vs stress
   1.82-1.97) — the composition is still defensively biased. The same
   pattern holds for r_064 (calm 1.04-1.07 vs stress 1.48-1.95) — proving
   that **iter 064 base is itself calm-defensive at the bar level**.
4. **Structural diagnosis**: Up-weighting r_mr in CALM regime concentrates
   exposure in the iter 064 base's LOWEST conditional-Sharpe segment.
   r_mr's calm-Sharpe (0.82-0.93) is INSUFFICIENT to compensate for
   reducing iter 064 base weight from 1.0 to 0.85-0.90 in calm — where
   iter 064 has Sharpe 1.04-1.07. Net effect: zero amplification.
5. **KILL B FIRES — CAGR drops below 9.18% unlock floor on best cfg
   (9.08% edu)**. The regime-conditioning's selective r_mr exposure
   (mean_w_mr ≈ 0.084) costs the composition ~0.10pp edu CAGR vs iter
   071 (9.27% → 9.08%) — just enough to lose the iter 064 unlock and
   drop CAGR floor 1/3 → 0/3 → score 90 → 85.
6. **All 7/7 gates pass × 3 datasets for ALL 4 cfgs** (engine perfect:
   PBO 0.03/0.23/0.32, DSR p < 0.05 worst, robustness 9/9, G7 0.0pp).
7. **Score 85 STRONG ties iter 058 (#5 in TOP-K).** Falls 5 points below
   the joint TOP-K #1 of iter 064/069/070/071 (each at 90) — the regression
   is entirely on criterion 4 (CAGR floor).

## Headline metrics (best cfg `iter064_vix_cond_calm010_stress005`)

| dataset | Sharpe (Δ frozen / Δ064 / Δ071) | CAGR (Δ064 / Δ071) | MDD (Δ064 / Δ071) | DSR p | gates |
|---|---|---|---|---|---|
| educational | **1.2300** (+0.5500 / **+0.0125** / **−0.0040**) | 9.08% (−0.40pp / −0.18pp) | 16.33% (−0.94pp / −0.08pp) | **0.0323** | **7/7** |
| spy_real | **1.3502** (+0.4502 / **+0.0189** / **+0.0011**) | 9.57% (−0.40pp / −0.19pp) | 14.34% (−0.99pp / −0.33pp) | **0.0333** | **7/7** |
| ndx_real | **1.3912** (+0.4362 / **+0.0158** / **+0.0011**) | 9.72% (−0.45pp / −0.21pp) | 13.77% (−0.97pp / −0.34pp) | **0.0291** | **7/7** |

vs iter 064 (1.2175/1.3312/1.3755 Sharpe; 9.49/9.97/10.17% CAGR; 17.27/15.33/14.74% MDD): same ~0.015-0.019 Sharpe lift as iter 071 + tighter MDD (−0.94 to −0.99pp) — but CAGR drops further (−0.40 to −0.45pp vs iter 064's reduction of −0.21 to −0.24pp in iter 071). The regime-conditioning trades CAGR for marginal MDD tightening, no net Sharpe gain.

vs iter 071 (1.2339/1.3491/1.3901 Sharpe; 9.27/9.76/9.93% CAGR; 16.41/14.67/14.11% MDD): essentially identical — Δ Sharpe ranges from −0.0040 to +0.0011 (within noise), Δ CAGR −0.18 to −0.21pp, Δ MDD −0.08 to −0.34pp. The composition is **bit-identical to iter 071's static blend at portfolio level** (corr ≈ 0.998-0.999) with marginal CAGR cost.

**Per-dataset gate detail** (G1234567):

| dataset | G1 | G2 | G3 | G4 | G5 | G6 | G7 | total |
|---|---|---|---|---|---|---|---|---|
| edu | ✓ PBO=0.03 | ✓ p=0.032 | ✓ 8/8 | ✓ S>0 | ✓ S>0 | ✓ ci_low=0.524 | ✓ 0pp | **7/7** |
| spy | ✓ PBO=0.23 | ✓ p=0.033 | ✓ ≥6/8 | ✓ S>0 | ✓ S>0 | ✓ ci_low=0.580 | ✓ 0pp | **7/7** |
| ndx | ✓ PBO=0.32 | ✓ p=0.029 | ✓ ≥6/8 | ✓ S>0 | ✓ S>0 | ✓ ci_low=0.493 | ✓ 0pp | **7/7** |

7/7 × 3 with PBO < 0.5 on all and DSR < 0.05 at cumulative_n_trials = 4348.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | 3/3 datasets ≥ frozen + 0.10 (edu +0.55 / spy +0.45 / ndx +0.44) |
| 2 Gates | **25** | 25 | edu 7/7 → 7pts; spy 7/7 → 7pts; ndx 7/7 → 7pts; cross-ds met → +4 = 25 |
| 3 DSR | **15** | 15 | Worst-p 0.0333 (spy) < 0.05 → full 15 pts; cumulative n_trials = 4348 |
| 4 CAGR floor | **0** | 15 | 0/3 datasets pass: edu 9.08% < 9.18% ✗; spy 9.57% < 11.98% ✗; ndx 9.72% < 15.35% ✗ |
| 5 MDD ceiling | **15** | 15 | All 3 well under bench+5pp; 22-26pp slack each |
| 6 Robustness | **5** | 5 | 9/9 sub-windows positive (Sharpe 1.13-1.59 across all 9) |
| **total** | **85** | **100+5** | tier: **STRONG** (5 below joint TOP-K #1 of 90) |

Strict winner conditions: **4/5 met** —
1. Sharpe edge ≥ +0.10 on ≥ 2 ds: ✓ (3/3 vs frozen)
2. Gates cross-ds (edu ≥5, spy/ndx ≥4): ✓ (7/7/7)
3. DSR p < 0.05 (worst): ✓ (0.0333 spy)
4. CAGR ≥ 0.8×bench on ≥ 2 ds: ✗ (0/3 — edu drops below 9.18%)
5. MDD ≤ bench+5pp on ≥ 2 ds: ✓ (3/3)

The 90 → 85 regression is **entirely on criterion 4** — edu CAGR drops 19bps (9.27% in iter 071 → 9.08% in iter 072) and crosses the 9.18% iter 064 unlock threshold. The other 5 criteria match iter 071 exactly.

## Per-cfg sensitivity sweep (4 cfgs)

| cfg_id | (w_calm, w_stress) | mean_w_mr | Sharpe edu/spy/ndx | Δ064 (best ds) | edu CAGR | score | kills | tier |
|---|---|---|---|---|---|---|---|---|
| `calm010_stress000` | (0.10, 0.00) | 0.068 | 1.210/1.333/1.378 | +0.002 spy | 9.10% | 85 | 6/10 | STRONG |
| `calm015_stress000` | (0.15, 0.00) | 0.103 | 1.204/1.332/1.377 | +0.001 ndx | 8.91% | 85 | 6/10 | STRONG |
| **`calm010_stress005`** | **(0.10, 0.05)** | **0.084** | **1.230/1.350/1.391** | **+0.019 spy** | **9.08%** | **85** | **6/10** | **STRONG** |
| `calm020_stress000` | (0.20, 0.00) | 0.131 | 1.196/1.329/1.374 | −0.002 spy | 8.71% | 85 | 6/10 | STRONG |

**Sensitivity findings**:

- **All 4 cfgs score 85** — the regime-conditional allocation axis has zero
  effective sensitivity at this composition. The Pareto front (score)
  is FLAT.
- **cfg3 (calm010_stress005) is best** by composite (highest min-Sharpe).
  Notably, this cfg has the SMALLEST regime-conditioning effect (mean_w_mr
  varies least from iter 071's static 0.05): w varies from 0.10 (calm) to
  0.05 (stress) — barely a 2× swing. This is mechanistically closest to
  iter 071 and produces nearly identical metrics (corr 0.998-0.999).
- **More aggressive regime-conditioning loses CAGR linearly**: cfg4
  (calm020_stress000) drops edu CAGR to 8.71% (47bps below floor) — pure
  cost without compensating Sharpe lift. The marginal r_mr exposure beyond
  ~0.05 effective weight produces no incremental benefit because iter 064
  base's calm-conditional Sharpe is already low.
- **0/4 cfgs clear KILL A** (Δ064 ≥ +0.02 on ≥ 2 ds). Best result is cfg3
  spy +0.019 (singleton, just under threshold).

## Pre-committed kills evaluation

Best cfg `calm010_stress005`:

| # | kill | fired? | observation |
|---|---|---|---|
| **A** | **Δ064 Sharpe < +0.02 on ≥ 2 ds** | **❌ FIRED** | +0.013/+0.019/+0.016 — 3/3 below threshold |
| **B** | **edu CAGR < 9.18% (064 unlock)** | **❌ FIRED** | 9.08% — 10bps below floor |
| **C** | **Δ071_th10w005 Sharpe < +0.005 on ≥ 2 ds** | **❌ FIRED** | −0.004/+0.001/+0.001 — 3/3 below |
| **D** | **corr(072, 064_static) > 0.99 on ≥ 2 ds** | **❌ FIRED** | 0.998/0.998/0.998 — 3/3 above |
| **E** | **r_072 calm_S/stress_S < 1.3 on ≥ 2 ds** | **❌ FIRED** | 0.56/0.57/0.58 — 3/3 INVERTED (calm < stress) |
| F | PBO grid-level > 0.5 on any ds | ✓ clean | max 0.32 (ndx) — well under |
| G | DSR worst p > 0.05 | ✓ clean | 0.033 spy — well under |
| H | G7 cross-lib > 0.5 pp | ✓ clean | max 0.0000 pp — engine perfect |
| **I** | **r_mr cond ratio < 1.5 on ≥ 2 ds** | **❌ FIRED** | 1.21/1.25/1.14 — 3/3 below (calm-aggressive but mild) |
| J | Score < 75 | ✓ clean | 85 — well above STRONG threshold |

**6/10 kills fire** — A primary (regime-conditioning fails to clear iter
071's threshold); B secondary (CAGR floor lost on best cfg); C+D+E+I are
diagnostic confirmations of structural inertness.

**The KILL E inversion is the single most informative finding**:
r_072 has calm-Sharpe FAR LOWER than stress-Sharpe (ratio ≈ 0.56-0.58 < 1).
This is the structural OPPOSITE of the hypothesis. iter 064 base is
itself calm-DEFENSIVE — and the composition inherits this bias. r_mr's
calm-aggression is too small (cond ratio 1.14-1.25 across 3 ds) to flip
the portfolio's regime profile.

## What worked / what didn't

**Worked**:

- **Engine integrity perfect**: 16/16 TDD tests pass; all weight invariants
  hold (Σw ≡ 1.0 to 1e-12); strict no-peek shift(1) on VIX confirmed; cost
  accounting linear in cost_bps; w_mr_stress=0 cleanly collapses to iter
  064 base on stress bars; w_mr_calm=w_mr_stress cleanly recovers iter 071
  static; G7 cross-lib 0.0000 pp on all 4 cfgs × 3 datasets.
- **All 7/7 gates pass × 3 datasets for ALL 4 cfgs**: PBO 0.03-0.32 (well
  under 0.5); DSR < 0.05 worst on all cfgs (4348 cumulative n_trials);
  WF 8/8 windows profitable on edu, ≥6/8 on spy/ndx; bootstrap CI low
  > 0.49 on all cfgs.
- **Robustness 9/9 positive sub-windows** (Sharpe 1.13-1.59 across) —
  same cleanliness as iter 071 baseline.
- **MDD strictly tightens vs iter 064 on 3/3 (best cfg)**: −0.94 to −0.99pp.
  The regime-conditioning provides marginal MDD benefit (selectively
  exiting r_mr in stress), but it's small.
- **Score 85 STRONG remains in TOP-5** (ties iter 058 at #5 ranking).

**Didn't**:

- **KILL A FIRES**: Sharpe lift vs iter 064 is +0.013-0.019 — 3/3 below
  the +0.02 threshold. Same magnitude as iter 071 — no lift from regime-
  conditioning.
- **KILL C FIRES**: Sharpe lift vs iter 071's static is essentially zero
  (−0.004 to +0.001) on 3/3. Dynamic VIX-conditional allocation provides
  ZERO incremental benefit over iter 071's uniform static at the same
  effective average w.
- **KILL E FIRES — mechanism falsified**: r_072 calm_S/stress_S < 1.0 on
  3/3, INVERTED from the hypothesis. iter 064 base is calm-defensive
  (calm_S 1.04-1.07 vs stress_S 1.48-1.95 — KILL E equivalent for
  r_064: also < 1.0 on 3/3). The composition cannot be made calm-
  aggressive at the portfolio level by adding a small calm-aggressive
  3rd stream.
- **KILL B FIRES**: edu CAGR drops to 9.08% (10bps below 9.18% floor)
  — losing the iter 064 unlock. The regime-conditioning's selective
  r_mr exposure costs ~19bps edu CAGR vs iter 071's static (9.27% →
  9.08%), enough to drop CAGR floor pass rate 1/3 → 0/3 → score 90 → 85.
- **KILL D FIRES**: corr(072, 064_static) > 0.998 on 3/3 — the regime-
  conditional weighting at small w_mr makes the composition structurally
  inert at portfolio level.
- **Winner conditions still 4/5** — same as iter 064/069/070/071. The
  CAGR-floor failure mode is now WORSE (0/3 vs 1/3 in iter 071/064).

## Main lesson (for future iterations)

**iter 072 = STRUCTURAL CLOSURE of "regime-conditional 3rd-stream allocation
on iter 064 base" → score 85 STRONG (drop from 90 ceiling)**.

This is the **5th iteration to confirm the 90 ceiling under iter 064 base
across fundamentally different mechanisms**:

| iter | mechanism | regime classifier | Δ064 Sharpe | edu CAGR | score |
|---|---|---|---|---|---|
| 064 | (baseline) | none | baseline | 9.49% | 90 |
| 068 | inner-w binary VIX (orig dir) | equity-vol binary | −0.04/−0.05/−0.05 | 9.53% | 79 |
| 069 | inner-w binary VIX (reverse) | equity-vol binary | −0.005/−0.010/−0.020 | 9.36% | 90 |
| 070 | inner-w continuous T10Y3M | macro/forward continuous | −0.003/−0.011/−0.018 | 9.69% | 90 |
| 071-th10w005 | static 3rd stream (SPY MR) | none (orthogonal) | +0.016/+0.018/+0.015 | 9.27% | 90 |
| 072-cs010s005 | regime-cond 3rd stream | binary VIX on 3rd-stream weight | +0.013/+0.019/+0.016 | 9.08% | **85** |

**Key structural finding (newly revealed by iter 072 KILL E inversion)**:
**iter 064 base is calm-defensive at the bar level** (r_064 calm_S 1.04-1.07
vs stress_S 1.48-1.95 — calm_S/stress_S < 1 on 3/3). This means:

1. **Adding a calm-aggressive complement amplifies the WRONG segment**.
   Up-weighting r_mr in calm regime concentrates exposure in iter 064's
   lowest-conditional-Sharpe portion. The marginal Sharpe from r_mr's
   calm 0.82 is OFFSET by reducing iter 064's base weight from 1.0 →
   0.85-0.90 in calm — where iter 064 has Sharpe 1.04-1.07.
2. **Static blends (iter 071) work BETTER than regime-conditional blends
   (iter 072)**: a uniform small w_mr captures iter 064's strong stress-
   Sharpe (1.95) AND r_mr's calm-Sharpe (0.82) simultaneously, both
   contributing positive Sharpe to their respective regimes. Dynamic
   regime-conditioning can only DEACTIVATE r_mr in stress (saving ~5bps
   stress Sharpe) at the cost of activating it MORE in calm — the wrong
   trade given iter 064's calm-weak base.
3. **KILL I clean across iter 071/072 confirms r_mr is genuinely calm-
   aggressive (calm_S 1.21-1.26× stress_S)**, but the magnitude is too
   small to flip the composition's regime profile.

**Implications for iter 073+**:

1. **The 90 ceiling is now confirmed across 5 fundamentally different
   structural mechanisms on iter 064 base** — regime reweighting (068/069),
   continuous regime (070), static 3rd stream (071), regime-conditional
   3rd stream (072). KILL E's inversion proves the ceiling is **anchored
   in iter 064 base's calm-defensive bar-level distribution**, not in
   the choice of structural ingredient.
2. **Direction #2 from iter 071 final (fresh higher-CAGR anchor, NOT iter
   046 family) is now the ONLY remaining structural lever**. All 5 axes
   on iter 064 base are now closed at 90 ceiling.
3. **Calm-aggressive complement composition strategy: the right move is
   NOT to add a small calm-aggressive stream to iter 064 (proven inert).
   The right move is to find a base anchor that is itself calm-aggressive
   (or neutral)** — then iter 071's r_mr stream composes additively
   rather than redundantly.
4. **Hierarchical/multi-signal regime models on iter 064 are exhausted** —
   binary VIX, continuous T10Y3M, static 3rd stream, regime-conditional
   3rd stream all saturate at 90 (or regress, as in iter 072 to 85).
   The only lever that works is changing the base.

## Structural dead-ends discovered

iter 072 closes the **VIX-binary regime-conditional 3rd-stream allocation
axis on iter 064 base**:

- **iter 072 (🥇 STRONG 85, 6/10 KILLS — A primary; B+C+D+E+I diagnostic) —
  VIX-binary regime-conditional r_mr allocation on iter 064 base + iter 071
  validated r_mr (4 cfgs sweep: w_calm ∈ {0.10, 0.15, 0.20}, w_stress ∈
  {0.00, 0.05})**: 7/7 gates × 3 ds; PBO 0.03-0.32 (3/3 < 0.5); DSR < 0.05
  × 3 (cumulative n_trials = 4348); robustness 9/9; engine perfect (16/16
  TDD, G7 0.0pp). Sharpe lift vs iter 064 is +0.013-0.019 on 3/3 (KILL A);
  vs iter 071 static is −0.004 to +0.001 on 3/3 (KILL C). Best cfg edu
  CAGR 9.08% < 9.18% iter 064 unlock floor (KILL B). corr(072, 064) >
  0.998 on 3/3 (KILL D). r_072 calm_S/stress_S < 1.0 on 3/3 (KILL E
  INVERTED — iter 064 base is itself calm-defensive). r_mr cond ratio
  1.14-1.25 (KILL I — calm-aggressive but mild magnitude).

  **Closes the regime-conditional-3rd-stream axis on iter 064 base at
  85 STRONG ceiling** (regression from 90 due to CAGR floor loss). The
  composition's CAGR ceiling (anchored in iter 046 + r_qqqt) is BELOW
  iter 071 because regime-conditioning de-allocates r_mr in ~30% of
  bars without offsetting Sharpe gain.

What is **OPEN** for iter 073+ (NOT consumed by iter 072):

- **Fresh higher-CAGR anchor (NOT iter 046 family)** — the ONLY remaining
  structural lever after 5 axes closed on iter 064 base. Candidates:
  cross-asset Hurst-regime trend; credit-spread regime as primary signal;
  single-asset levered base with embedded calm-aggressive + defensive
  components; multi-asset risk-parity at higher vol target. Cost: ~3-5+
  iterations to build the new anchor before composing.
- **Plano C sleeve meta-allocation** (≤ 70 ceiling).
- **CRSP / Norgate cross-sectional momentum** (data budget).
- **Forward 5-day Sharpe meta-label on iter 064** (still open from iter
  067 final report; cadence-orthogonal but expected ≤ 85).

What is **CLOSED** by iter 072 (in addition to all prior closures):

- **VIX-binary regime-conditional 3rd-stream allocation on iter 064 base**
  (4 cfgs sweep: w_calm × w_stress): structurally falsifies the calm-
  aggressive amplification hypothesis. The mechanism is INVERTED at
  portfolio level (KILL E < 1.0 on 3/3) because iter 064 base is itself
  calm-defensive. Closes the 5th and final regime-allocation axis on
  iter 064 base at 85-90 ceiling.

## Citations used

- `[algo_trading_chan, p.95, p.153-154, ch.6]` — Chan: momentum filter on
  MR + MR/momentum complementarity in regime-based portfolio allocation.
  Primary citation for the hierarchical regime allocation hypothesis.
- Whaley, R. E. (2009). "Understanding the VIX." *Journal of Portfolio
  Management*, 35(3): 98-105. DOI 10.3905/JPM.2009.35.3.098 — VIX
  threshold = 20 long-run median.
- Bekaert, G., & Hoerova, M. (2014). *Journal of Econometrics*, 183(2):
  181-192. SSRN 2294327 — VIX as risk-aversion + uncertainty proxy.
- Connors, L., & Alvarez, C. (2009). *Short Term Trading Strategies That
  Work*. ISBN 978-0-9755513-2-7 — RSI(2) + VIX timing rule.
- Lo, A. W., & MacKinlay, A. C. (1988). *Review of Financial Studies*,
  1(1): 41-66. DOI 10.1093/rfs/1.1.41 — short-horizon mean-reversion.
- Moskowitz, T., Ooi, Y. H., & Pedersen, L. H. (2012). *JFE*, 104(2):
  228-250. DOI 10.1016/j.jfineco.2011.11.003 — TSM regime conditionality.
- `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base
  preserved verbatim (saved return stream).
- Faber (2007), SSRN 962461 + `[stocks_on_the_move, p.21-30]` — Faber
  QQQ-200d-trend preserved verbatim (computed via iter 064's qqq_trend).
- `[advances_fin_ml, ch.17-18]` — regime detection / structural breaks.
- `[advances_fin_ml, p.162-164]` — strict shift(1) on VIX (no peek).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 4348.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (0.0000 pp).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV gate G1.
- `[systematic_trading, ch.11]` — Carver IDM ≤ 2.5 (Σw ≡ 1.0).
- iter 064/071 final reports — TOP-K #1 baseline + validated r_mr stream.
- iter 069 / vix_inner_weight.py — engine pattern for VIX-binary
  regime-conditional weighting (re-applied to 3-leg).

## Next iteration suggestions

iter 072 closes the regime-conditional-3rd-stream-allocation axis on
iter 064 base at 85 STRONG (regression from 90 → 85). The 90 ceiling
is now CONFIRMED across 5 fundamentally different mechanisms on iter
064 base. Three structurally distinct directions for iter 073, ranked
by expected information per cost:

1. **Fresh higher-CAGR anchor (NOT iter 046 family) — RECOMMENDED.**
   ONLY remaining structural lever. The 5-iter pattern (064/068/069/
   070/071/072) provably proves the iter 064 base anchor is the binding
   constraint, NOT mechanism choice. Candidate primitives:
   - **(a) NTSX / risk-parity-equity at higher vol target**: 90/60
     leveraged stack, vol target 14% (vs iter 046's ~9%). Citations:
     Asvanunt-Richardson 2017, NTSX whitepaper.
   - **(b) Volatility-targeted SPY+TLT at HIGHER target with TSM
     overlay**: combine iter 016 base (vol-managed 60/40 SPY+TLT MM
     scaling) + iter 024 TSM filter — but at higher leverage cap 1.5×
     (instead of 1.0× cap currently used). Citations: Moreira-Muir 2017,
     Asness-Moskowitz-Pedersen 2013.
   - **(c) Multi-asset Hurst-regime trend follower**: 5-asset basket
     (SPY, TLT, GLD, USO, DBC) with Hurst-exponent regime classifier.
     Citations: Mandelbrot 1971, Peters 1991, Lo-MacKinlay 1988.
   Predicted **70-95**, high variance; cost ~3-5 iterations to build
   the new anchor before composing iter 071's r_mr.
2. **Forward 5-day Sharpe meta-label on iter 064** (still open from
   iter 067 final report). Different cadence than bar-level regime
   classifier; ~120 flips/yr at weekly horizon. Predicted **65-85**,
   high variance. Cost ~75-90 min. Lower priority — same iter 064 base
   constraint.
3. **Plano C sleeve meta-allocation** (≤ 70 ceiling). Lowest priority
   — ceiling is below STRONG threshold.

**Recommended pick for iter 073**: **direction #1 sub-option (b)** —
volatility-targeted SPY+TLT at HIGHER target with TSM overlay. Reuses
iter 016/024 infrastructure (lowest implementation cost), tests a
fundamentally NEW base composition, and is small enough to compose
with iter 071's r_mr in iter 074 if direction #1 succeeds. The
hypothesis: a higher-vol-target base will have a non-defensive
calm/stress profile, allowing r_mr's calm-aggression to compose
additively rather than redundantly.

iter 064 stays at **TOP-K #1 (joint with iter 069, iter 070, iter 071)**
with score 90 STRONG, 4/5 winner conditions, 0/7 kills. iter 072 enters
TOP-5 at #5 with score 85 STRONG, 4/5 winner conditions, 6/10 kills —
ties iter 058 (also 85 STRONG, displaced when iter 064 took #1 in the
4-way tie).
