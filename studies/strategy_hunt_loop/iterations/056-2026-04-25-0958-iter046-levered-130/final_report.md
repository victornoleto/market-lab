# Iteration 056 — Final Report

## Verdict

🥈 **PROMISING (score 74/100, winner_conditions_met=False, 2/6 kills fired
[B+D] → hypothesis FALSIFIED)**

External 1.3× leverage on the iter 046 TOP-K champion converts unused
MDD slack into +1.6pp CAGR but pays a measured −0.11 Sharpe drag from
the 3.5% retail borrow spread, which **breaks DSR on all 3 datasets**
(0.041 → 0.10) and erodes the c2/c3 gate scoring more than the c4
CAGR-floor gain compensates. Score regress 85 → 74; iter 046 retains
TOP-K #1.

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen / Δ046) | CAGR (Δ floor) | MDD (Δ ceiling) | gates | DSR p |
|---|---|---|---|---|---|
| educational | 1.097 (+0.42 / −0.11) | 10.79% (+1.61pp vs 9.18) | 23.37% (under 60.14) | 6/7 | 0.1023 ❌ |
| spy_real    | 1.210 (+0.31 / −0.11) | 11.20% (−0.78pp vs 11.98) | 20.20% (under 38.70) | 6/7 | 0.1004 ❌ |
| ndx_real    | 1.267 (+0.31 / −0.11) | 11.61% (−3.74pp vs 15.35) | 19.40% (under 40.12) | 6/7 | 0.0783 ❌ |

G1 PBO vacuous (N=1). G2 DSR FAIL × 3. G3 WF 8/8 × 3. G4 OOS Sharpe
+1.11 to +1.19 × 3. G5 FWD post-2020 +1.13 to +1.21 × 3. G6 bootstrap
99.9% CI low +0.39 to +0.42 × 3. G7 cross-lib 0.0000 pp × 3.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 25 | 25 | 3/3 datasets beat bench+0.10 (full +5 cross-bonus) |
| 2 Gates | 19 | 25 | 6+6+6 per ds (5+5+5 = 15) + cross-ds bonus 4 = 19; G2 FAIL ×3 cost 9 pts vs iter 046's 25/25 |
| 3 DSR | 5 | 15 | worst-p = 0.1023 (edu); 0.05 < p < 0.20 → 5pts (vs iter 046's 15) |
| 4 CAGR floor | 5 | 15 | edu PASS (10.79 > 9.18); spy/ndx FAIL (under floor); 1/3 PASS = 5pts |
| 5 MDD ceiling | 15 | 15 | 3/3 well under (23/20/19 vs 60/38/40) |
| 6 Robustness | 5 | 5 | 9/9 sub-windows positive; Sharpes +1.00 to +1.50 |
| **total** | **74** | **100+5** | tier: 🥈 **PROMISING** |

## Configuration tested

```python
CFG = {
    "cfg_id": "iter046_levered_130_borrow_350bps",
    "lev": 1.3,
    "borrow_rate_annual": 0.035,  # T-bill 2% + IBKR Pro Tier 1 spread 1.5%
    # iter 046 sub-strategy params verbatim:
    "w_041": 0.5, "w_039": 0.5,
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},
    "vix_threshold": 20.0,
    "cost_bps_per_leg": 0.0002,
    "rf": 0.02,
    "harvest_notional": 1.0,
    "weights_039": {"SPY": 1/3, "QQQ": 1/3, "IWM": 1/3},
    "iv_scales": {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
    "k_long_pct": 0.95, "k_short_pct": 0.90,
    "dte_days": 21, "cost_bps_per_roll": 5.0,
}
# Total exposure: 1.3 × iter 046 ≈ 1.95× max equity (1.3 × 1.5 calm
# regime). Borrow rate 3.5% = T-bill 2% + IBKR Pro Tier 1 spread 1.5%
# (public schedule 2025-04). NOT optimized — pre-committed to a
# realistic retail-broker rate.
```

Pre-committed kill criteria, evaluated:

| kill | observable | fired? | actual |
|---|---|---|---|
| A Sharpe regress vs iter046 −0.15 | 0/3 below | ✓ clean | max delta −0.114 |
| **B Score < iter 046 (85)** | **🔥 FIRED** | **74 < 85** | iter 046 Pareto-opt confirmed |
| C MDD breach > bench+5pp | 0/3 breach | ✓ clean | 23/20/19 vs 60/38/40 |
| **D DSR worst-p ≥ 0.05** | **🔥 FIRED** | **0.10 > 0.05** | trial penalty + spread drag |
| E G7 cross-lib > 3pp | 0pp | ✓ clean | numpy/pandas parity exact |
| F edu CAGR < 9.18% | 10.79 PASS | ✓ clean | leverage gain net positive |

2 kills fired (B + D) → hypothesis FALSIFIED per the pre-committed rule.

## What worked / what didn't

**What worked**

- Mechanics are clean: G7 0.0000 pp × 3 (numpy/pandas parity exact), G3
  WF 8/8 × 3, G4 OOS positive × 3, G5 FWD positive × 3, G6 bootstrap
  positive × 3. The leverage transform `r_lev = lev × r − (lev−1) ×
  daily_borrow` is correct and verified by 12 TDD specs (Sharpe
  preservation under pure leverage; spread drag formula; daily
  compounding identity for the borrow rate).
- CAGR axis improved as predicted: edu went from 9.16% (0.02pp short of
  the 9.18% floor) to 10.79% (1.61pp clear). +5pts on c4. The
  hypothesis on "convert MDD slack into CAGR" is mechanically validated
  on the edu dataset.
- MDD scaled near-linearly with leverage (1.3× → ~1.30 × MDD): all 3
  datasets remain well under their +5pp ceilings. No path-dependent tail
  amplification.
- All 3 datasets retain Sharpe edge ≥ +0.30 vs frozen benchmarks (c1
  full 25 pts).

**What didn't work**

- **DSR collapse**: worst-p jumped from 0.0416 (iter 046, n=4311) to
  0.1023 (iter 056, n=4326). This is the **dominant cause** of the
  score regress (−10pts on c3). The cause: Sharpe drag from the 3.5%
  borrow spread is **larger than the analytic prediction in
  `hypothesis.md`**. Predicted Sharpe drag was ~0.058 (computed
  per-bar without the √252 annualization factor); actual drag is
  ~0.105 across all 3 datasets, matching the corrected formula
  `Sharpe_drag = √252 × (lev−1) × daily_borrow / (lev × σ_daily)`.
- **Gate G2 collapse**: with DSR p > 0.05 on all 3, G2 fails on all 3,
  costing 6pts on c2 (25 → 19) — combined with c3's −10pts, that's
  −16pts purely from DSR. The c4 gain of +5pts cannot offset this.
- **CAGR floor still failing 2/3**: spy 11.20% vs floor 11.98% (0.78pp
  short); ndx 11.61% vs floor 15.35% (3.74pp short). Even with 1.3×,
  ndx is **far** below floor — the iter 046 base CAGR ceiling at 1.0×
  was 9.76%, and pure leverage at realistic borrow can't bridge a
  5.6pp gap on ndx. To close it would require ~1.8× leverage, but
  Sharpe drag at 1.8× would be ~0.18 (DSR p worst would push past 0.20).

**Why the analytic prediction missed**

The hypothesis `Sharpe_drag = (lev-1) × spread / (lev × σ_annual)` is
**dimensionally wrong**. Sharpe is `√252 × μ_daily / σ_daily`, but the
borrow drag subtracts a **daily** amount per bar; the per-bar drag
divided by daily σ then multiplied by √252 gives the annualized
Sharpe drag — a factor of √252 ≈ 15.87 that the hypothesis omitted.
This iteration's negative result calibrates the team's mental model
for future leverage-axis hypotheses.

## Main lesson (for future iterations)

**External leverage on a low-vol composition (σ ≈ 5.5–6%) can never
clear DSR at retail borrow rates.** The Sharpe drag from realistic
borrow spreads (~1.5pp over T-bill) at 1.3× leverage is ~0.10–0.11
across all 3 datasets — large enough to push DSR worst-p from 0.04 to
0.10 with ~15 additional trials. This **closes the leverage axis on
any iter 046-derivative strategy at retail borrow rates**: the
strategy's edge (c1 + c5 + c6) survives, but the gates that depend on
Sharpe (c2 G2 + c3 DSR) collapse. Iter 046's score 85 is the **Pareto
ceiling for the iter 041+iter 039 composition family**.

The CAGR-floor gap on ndx (5.6pp at 1.0× leverage) is structurally
unbridgeable by any pure-leverage operation — the iter 046 base needs
**Sharpe enhancement** (not risk amplification) to reach WINNER. Future
iterations must seek a different anchor or an additional uncorrelated
return stream.

## Structural dead-ends discovered

**Pure external leverage on iter 046 (any retail borrow rate ≥ 3%)** is
a closed axis:

- At 1.0× → score 85 (iter 046 baseline)
- At 1.3× → score 74 (iter 056, this iter): −11pts. CAGR +1.6pp on
  edu; DSR collapses on all 3 (+0.06pp on worst-p).
- At 1.5× extrapolated → estimated score ≈ 65 PROMISING (Sharpe drag
  ~0.18, DSR p worst > 0.20 likely).
- At 1.7× extrapolated → estimated score ≈ 55 MARGINAL (Sharpe drag
  ~0.25; could pass spy/ndx CAGR floors but DSR fully gone).

The only leverage rate that doesn't break DSR is 1.0× = iter 046
itself. **Add to DEAD_ENDS.md.**

## Citations used

- `[risk_parity, ch.5]` — iter 046 base architecture inherited verbatim.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials`
  4325 → 4326. The DSR formula's sensitivity to small Sharpe changes
  near n_trials > 4000 is what caught the leverage transform here.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate (G6).
- `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP
  (iter 039 component, inherited via iter 046).
- `[advances_fin_ml, p.162-164]` — no-lookahead lag (iter 041
  component, inherited via iter 046).
- Frazzini-Pedersen (2014), JFE 111(1) 1-25, DOI 10.1016/j.jfineco.2013.10.005 —
  borrow frictions on levered low-vol strategies. **Vindicated empirically
  by this iteration**: realistic broker spreads (1.5pp over T-bill)
  collapse DSR even at modest 1.3× leverage on low-vol composites.
- Whaley (2009), JPM 35(3) 98-105, DOI 10.3905/JPM.2009.35.3.098 —
  VIX as ex-ante risk regime indicator (iter 041 component).
- Markowitz (1952), JoF 7(1) 77-91 — convex combination basis.
- IBKR Pro Tier 1 margin schedule (public, 2025-04) — 3.5% effective
  borrow rate at 2025 yields. Pre-committed.

## Next iteration suggestions

The leverage axis on iter 046 is closed; the next iteration must seek
**Sharpe enhancement** rather than risk amplification. Three
structurally distinct directions:

1. **Add a third uncorrelated return stream to iter 046 (out-of-family,
   targeting corr<0.4 with both r_041 and r_039)** — same mechanism as
   iter 045/046 but at the next composition layer. Candidates: trend on
   FX carry (G10 majors), CTA momentum on liquid futures, time-series
   momentum on commodity rolls. The DSR penalty bound at corr=0.40
   would predict an additional ~30% reduction in worst-p (0.04 → 0.028)
   with minimal Sharpe change. Score predicted 88-92 — potentially
   crosses 90 threshold. Cite `[risk_parity, ch.5]` + new source for
   the third leg.

2. **Alternate iter 041 regime architecture using TERM-spread (T10Y3M)
   instead of VIX-binary** — iter 044 closed *2-feature* composite, but
   single-feature **term-spread regime** (cite `[advances_fin_ml,
   ch.17-18]` + Estrella-Mishkin 1998 NBER 6649) is structurally
   distinct. Term spread is forward-looking (~12mo lead-time) where
   VIX is contemporaneous. If T10Y3M-based iter 041 has corr < 0.85
   with iter 039, the composition mechanism applies and we get a fresh
   84-ceiling family. Predicted 76-84.

3. **Alternative iter 039 instrument: variance swap on broader index
   (e.g., 5y vol-target + harvest VRP from VIX/RVX/VXEEM blended)** —
   close to iter 055 but with **separately optimized** per-region
   weights rather than equal-weight. iter 055 closed equal-weight at
   73 due to EM tail asymmetry; an asymmetric weight (e.g., 0.5 SPY +
   0.3 QQQ + 0.2 IWM, 0% EFA/EEM) might preserve iter 039's edge with
   broader exposure. Predicted 75-82.

**Strict avoidance**: any external leverage on iter 046 at any
borrow rate (closed by this iter); any axis already closed in
DEAD_ENDS.md from iters 044/047-050; any iter 037/041 anchor saved-
stream-pair (Pareto exhausted at 85 by iters 045/046/051/053).
