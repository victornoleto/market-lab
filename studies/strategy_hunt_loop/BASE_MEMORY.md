---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 48
winners_found: 0
status: iterating
latest_iteration: "048-2026-04-25-0644"
cumulative_n_trials: 4315
---

# Strategy Hunt Loop — BASE MEMORY

**Read FIRST every iteration.** Conversation history is empty; this file + `iterations/NNN-*/` are continuity. Process: `PROMPT.md`. Infra: `INFRASTRUCTURE.md`.

---

## Mission

Find ONE trading strategy that:

1. **Beats SPY 1x buy-hold Sharpe by ≥ 0.10** on real data
2. **Passes the 7-gate battery** per `WINNER_CRITERIA.md` cross-dataset
3. **Is not a minor variation** of a known dead-end

Winner criteria live in `studies/strategy_hunt_loop/WINNER_CRITERIA.md`.
Dead ends that must NOT be re-tried live in
`studies/strategy_hunt_loop/DEAD_ENDS.md`.

**Hard context**: project is in mandate §1 **MAINTENANCE 100% Plano C**.
Even if this loop finds a winner, deployment requires a separate signed
override per mandate §7. Loop produces CANDIDATES, not live positions.

---

## Winners found

None yet. When found, append yaml block with iteration/hypothesis/config/score/datasets_passing/citation_primary/iteration_dir (template in `PROMPT.md`).

---

## Top-K ranked (best across all iters, by score)

| rank | iter | tier | score | strategy slug | primary citation | headline |
|---|---|---|---|---|---|---|
| **1** | **046** | 🥇 STRONG | **85** | `iter039_on_iter041_50_50` | `[risk_parity, ch.5]` + Whaley 2009 + Sinclair 2013 | **NEW #1**; iter 041+039 50/50 corr 0.41; **1st EVER 7/7×3 gates + DSR sub-0.05×3** (0.041/0.042/0.031); 0/6 kills; strict-dominates 041+045 on Sharpe/MDD/gates/DSR; CAGR 0/15 sole gap to 90 |
| **2** | **041** | 🥇 STRONG | **84** | `regime_weights_vix_lt20_70_40_40_ge20_30_55_55` | `[risk_parity, ch.5]` + Whaley 2009 | 1st 84; DSR 0.222→0.168 escape; 4/5 winner; 042/043/044 all REGRESS (gate-mod axis closed); base-substituted into iter 046 |
| **3** | **045** | 🥇 STRONG | **81** | `iter039_on_iter037_50_50` | `[risk_parity, ch.5]` + Sinclair 2013 | out-of-family 50/50 037+039; corr 0.58 vindicates compounding; DSR 0.222→**0.096**; ndx 7/7 + DSR sub-0.05; **0/6 kills**; superseded by iter 046 |
| **4** | **038** | 🥇 STRONG | **79** | `regime_lev_vix_lt20_lo10_hi17` | `[advances_fin_ml, ch.17-18]` + MM 2017 | VIX-gated 1.7/1.0× on 037; MDD −4/−8pp; DSR 0.204 |
| **4** | **037** | 🥇 STRONG | **79** | `ntsx_3leg_preserved_60_45_45_spy_ief_gld` | `[risk_parity, ch.5]` + AMP 2013 | 1st plain static-stack 79; Sharpe +0.30/+0.25/+0.22 |
| **4** | **016** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20` | `[risk_parity, p.10-11]` + MM 2017 | 60:40 × MM vol-target; Sharpe +0.24-0.30; DSR 0.226 |
| **4** | **018** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20_funded` | `[risk_parity, p.80-84]` | 016 + funding cost (−93 to −148 bps/yr); ties 016 |
| **4** | **021** | 🥇 STRONG | **79** | `ntsx_vm_..._scs5_10_1m` | `[volatility_trading, ch.3]` | 016 + short put-cs; MDD −1/−3pp; DSR 0.217 |
| **4** | **043** | 🥇 STRONG | **79** | `hysteretic_vix_low18_high22_w70_40_40_30_55_55` | `[advances_fin_ml, ch.17-18]` + Hamilton 1989 | Schmitt 041w; RT/yr 2.5 = halved; falsifies path-variance |
| **10** | **035** | 🥇 STRONG | **77** | `static_stack_90_60_spy_gld` | `[risk_parity, ch.5]` + Erb-Harvey 2006 | gold-not-bond axis; best static DSR (0.344) |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 048 — 2026-04-25 — iter046-output-lev-gate (🥇 STRONG, 83/100, **3/6 KILLS, output-leverage axis CLOSED, REGRESSION vs 85**)
- **Result:** Single cfg `iter046_lev_calm14_stress10_vix20` (1.4× when VIX[t-1]<20; 1.0× otherwise) on iter 046 OUTPUT stream. cumulative_n_trials 4314→4315. Sharpe edu/spy/ndx 1.20/1.29/1.34 (Δ frozen +0.52/+0.39/+0.39; Δ046 **−0.0015/−0.0333/−0.0374** — slight regress on all 3); gates 7/6/7 (spy G2 fails); DSR p=0.0427/0.0557/0.0438 (edu 0.0414→0.0427 deflator step; spy 0.0416→**0.0557** crosses raw α; n=4315); CAGR 10.91/11.22/11.65% (Δ046 +1.75/+1.76/+1.89pp — ALL <2pp Kill F threshold; edu PASS floor, spy/ndx FAIL → 1/3 +5 vs iter 046's 0/3); MDD 18.48/17.72/17.00%; G7 0.0000pp on 3/3; calm_frac 65-71%; robust 9/9; winner 3/5. Score 1:25 2:23 3:10 4:5 5:15 6:5 = **83**. Kills B+D+F fired; A/C/E clean.
- **Lesson:** **Output-side regime leverage on iter 046 = OUTPUT-LEVEL ANALOG of iter 044's INPUT-gate closure.** Re-using same VIX<20 classifier at input + output double-counts the signal; sub-multiplicative compounding eats ~30% of linear envelope. **3 modulation mechanisms now closed (044 input + 047 weight + 048 output)** — all trade variance×return and all fail to break 85. Path to 90 must be ADDITIVE (new uncorrelated stream), not MODULATIVE. iter 049: single-stock momentum on Tiingo 1695-ticker universe (data available; escapes iter 003 ≤20-asset closure) RECOMMENDED; MTUM/QUAL/USMV NOT in cache. See `iterations/048-*/`.

### 047 — 2026-04-25 — iter046-weight-sweep-3cfg (🥇 STRONG, 79/100, **2/6 KILLS, weight axis CLOSED**)
- **Result:** 3-cfg pre-committed sweep `w_041 ∈ {0.50, 0.65, 0.80}` on iter 046; cumulative_n_trials 4311→4314. Best=50/50; Sharpe edu/spy/ndx 1.20/1.32/1.38, DSR raw worst-p 0.042/0.074/0.133 (all 3 cfgs FAIL Bonferroni α'=0.0167), CAGR 9.16/9.45/9.76% (best cfg 0/3 floors; 65/35 + 80/20 each 1/3 edu only); PBO=0.000 on 3/3, G7=0.0000pp; score 1:25 2:19(BF cost) 3:15 4:0 5:15 6:5 = 79 frozen / 84 custom; winner=False. Kills A+B fired.
- **Lesson:** iter 046's 50/50 IS score-function Pareto-optimum; weight asymmetry trades DSR Δ−10 faster than CAGR Δ+5; Bonferroni N=3 cost (6pp gates) > dispersion gain. Ndx CAGR 15.35% structurally unreachable from iter 041 composites (cap 12.97%). See `iterations/047-*/`.

### 046 — 2026-04-25 — iter039-overlay-on-iter041 (🥇 STRONG, 85/100, **TOP-K #1**, 0/6 KILLS)
- **Result:** 50/50 convex combo iter 041 + iter 039. Sharpe edu/spy/ndx 1.20/1.32/1.38 (Δ frozen +0.52/+0.42/+0.43; strict-dominates 045 +0.10/+0.04/+0.06), gates 7/7/7 (1st EVER 7/7×3), DSR p=0.0414/0.0416/0.0311 (1st EVER sub-0.05×3) (n=4311), CAGR 9.16/9.45/9.76% (0/3 frozen — edu by 0.02pp razor-thin), MDD 17.97/15.22/14.57%, G7 0.0000pp, corr(041,039) 0.403/0.425/0.413, WF 8/8×3, robust 9/9, winner 4/5; score 1:25 2:25 3:15 4:0 5:15 6:5 = 85.
- **Lesson:** Out-of-family composition score advantage scales **inversely with corr** (037+039 ρ=0.58→DSR 0.096→81; 041+039 ρ=0.41→DSR 0.041→85). 5-pt gap to WINNER tier is entirely on CAGR-floor (0/15). See `iterations/046-*/`.

### 045 — 2026-04-25 — iter039-overlay-on-iter037 (🥇 STRONG, 81/100)
- **Result:** 50/50 iter 037 + iter 039. Sharpe edu/spy/ndx 1.10/1.28/1.33, DSR 0.0962/0.0572/0.0495, CAGR 9.7/10.4/10.6%, MDD 22.6/16.3/15.4%, corr 0.587, gates 6/6/7, robust 9/9, winner 3/5; score 1:25 2:21 3:10 4:5 5:15 6:5 = 81.
- **Lesson:** Out-of-family composition at moderate corr (ρ≈0.58) compounds DSR; iter 046 (ρ=0.41 base) improved to 85. See `iterations/045-*/`.

### Iters 015-044 (compressed 1-line; full detail in `iterations/NNN-*/`)
- **044** (🥈 74, multifeature-regime-vix-t10y3m) score 1:25 2:19 3:**0** 4:10 5:15 6:5 = 74; DSR 0.240 worst-p DEEPEST 041-perturb. PRINCIPLE: 2-feat composite over-classifies stress + T10Y3M dilutes VIX; 041's 84-ceiling LOCAL PLATEAU; **045+ MUST go OUT-OF-FAMILY** (vindicated by 045/046).
- **043** (🥇 79, hysteretic-vix-regime-weights) DSR worst-p REGRESS 0.168→0.189 (Kill B); MDD best static-stack ever; PRINCIPLE: halving regime crossings introduces regime-lag variance > path-variance gain; localizes 84-ceiling on gate-timing axis.
- **042** (🥈 74, combined-regime-lev-weights) DSR REGRESS 0.168→0.216, MDD deepest-ever; PRINCIPLE: amplifying lev asymmetry adds path variance > mean return; "compose × leverage compound DSR" FALSIFIED.
- **041** (🥇 **84 prior TOP-K #1**, regime-weights-vix, 1/6 KILLS) Sharpe 1.03/1.13/1.16, DSR 0.168/0.167/0.156 (**1st static-stack escape** from 037's 0.222), MDD 27.6/24.6/30.8%; calm 0.70/0.40/0.40 (1.50×) vs stress 0.30/0.55/0.55 (1.40×). PRINCIPLE: composition shift adds DSR power; 84 ceiling held 6 iters until iter 046 transplanted into composition with iter 039 → 85.
- **040** (🥈 69, vrp-basket-vol-target) MM σ⁻² on 039: ALL DEGRADE; PRINCIPLE: σ⁻² ABSORBS short-vol harvest. Closes MM σ⁻² on short-vol.
- **039** (🥇 76, basket 3etf 1/3-eq, 0/6 KILLS) Sharpe 1.14/1.29/1.56, DSR 0.075/0.061/**0.006** ndx loop-record, MDD 14/7/7%; PRINCIPLE: cross-asset VRP basket; VRP family ceiling 76 (CAGR 0/15 + edu DSR > 0.05 structural to T-bill collateral). Closes 4/5-leg, VIX gates on basket, asymmetric weights, DTE/strike sweeps. **Used as iter 045/046 component**.
- **038** (🥇 79, regime-lev-vix) DSR 0.204 best static-stack > 0.20, MDD Δ037 −8/−4/−4pp; PRINCIPLE: binary VIX-gate MDD-additive + Sharpe-neutral + DSR-marginal.
- **037** (🥇 79, 3-leg preserved-lev) Sharpe 0.98/1.15/1.17, DSR 0.222, MDD 33/25/32%; PRINCIPLE: Static-stack 77→79 broken; AMP 2013 orthogonality. **Used as iter 045 component**.
- **036** (🥈 72) 3-leg additive 1.8×; +0.30 lev breaks ndx MDD; subsumed by 037.
- **035** (🥇 77) GLD substitution on 015; 77 ceiling asset-class-agnostic; edge was DIVERSIFICATION not bond-carry.
- **034** (🥈 72) 3-leg bond-carry sleeve; subsumed by 035.
- **033** (🥈 72) IEF→TLT swap; bond-duration is CAGR-MDD trade-off NOT Sharpe lever.
- **032** (🥈 72) Layered iter 015 + iter 031 VRP; corr_SPY=+0.97 put-spread amplifies eq DD; **anchor for iter 045/046 corr<0.85 kill F**.
- **031** (🥇 76) AND-composite R-1∧R-2 on iter 026; 1st all-3 DSR<0.10; CAGR floor structural to harvest_notional=1.0.
- **030** (🥈 71) Z-score VIX gate on 026; spy passes but edu/ndx fail. Closes z-score gates.
- **029** (🥈 71) Persistence VIX gate on 028; edu DSR 0.0251 record but worst-p 0.1003.
- **028** (🥈 71) Constant `VIX<35` filter on 026; closes constant-threshold gates.
- **027** (🥈 74) N=3.5 levered iter 026; rf-bonus diluted by leverage.
- **026** (🥇 76) Stand-alone VRP T-bill + SPY 5/10 put cs; ndx 1st 7/7 + 1st DSR PASS.
- **025** (📉 39) Slow-EWMAC long-only 6-asset; long-only sacrifices 50% trend premium.
- **024** (🥈 72) Bond-curve carry static stack; DSR worst 0.586 binds.
- **023** (📉 28) TSM 3-ETF vol-target; turnover dominates √3; HOP needs 67 markets.
- **022** (🥉 54) TOM eq:bd modulator; σ²_port quadratic absorbs calendar premium.
- **021** (🥇 79) Short put-cs VRP overlay on 016; DSR 0.217.
- **020** (🥇 79) Monthly put-spread tail hedge; long-gamma REDUNDANT with vol-target.
- **019** (❌ 0) HMM stock-bond ρ; pre-val rejects 3/3.
- **018** (🥇 79) Funding-cost 016 replay; 100bps ≈ −0.07 Sharpe.
- **017** (🥉 52) 12-1 regional rotation N=3; US Sharpe dominance.
- **016** (🥇 79) Static 60:40 × MM vol-target; fixed × vol-target ADDITIVE.
- **015** (🥇 77) Static synthetic NTSX 90/60 SPY+IEF; 1st iter clearing +0.10 cross-ds.

### Iters 005-014 (compressed 1-line; full detail in `iterations/NNN-*/`)

- **014** (❌ FAIL 0, Kill #PV) — EBP credit overlay on iter 008; pre-val rejects 3/3 (exceed 0.68-0.71); overlay family CLOSED on iter 008 blend.
- **013** (🥈 64, Kill #3) — LR meta-label ρ_60+vix_z on iter 008: Sharpe regress; vol-proxy meta REDUNDANT with variance-scaling.
- **012** (🥉 58, Kill #1+#3+#4) — 5d EMA asymmetric T10Y3M haircut iter 008: 100% overlap edu+spy; T10Y3M 2×2 family CLOSED.
- **011** (🥉 52, Kill #1+#3) — Weekly 3-leg blend: Sharpe regress 3/3, MDD +10-14pp; vol-targeting REQUIRES daily cadence.
- **010** (🥈 74) — 3-leg SPY+TLT+GLD daily: ties iter 008 at 74, 4/5 winner; blend family saturates Sharpe ~1.00 regardless of N=2 or 3.
- **009** (🥈 64, Kill #3) — 21d EMA symmetric T10Y3M haircut iter 008: 100% overlap at bottom-20%; smoothing destroys lead-time.
- **008** (🥈 74) — Single-cfg ex-ante vol-managed SPY+TLT `vt15_L21_cap20`: Sharpe 0.87/1.00/1.02, DSR p=0.332, 4/5 winner; iter 006's edge IS structural.
- **007** (🥉 50, Kill #1+#3) — 12-1 momentum overlay iter 006: Sharpe regress 2/3; momentum REDUNDANT with variance-scaling.
- **006** (🥈 67, Kill #3) — 12-cfg vol-managed SPY+TLT grid: first +0.10 Sharpe gate cross-ds; killed G1 PBO 0.69 (grid inflates).
- **005** (🥉 59) — Moreira-Muir σ⁻² single-asset SPY/QQQ: first DSR edu PASS; single-asset vol-adapt saturates +0.08-0.10.

### Iters 001-004 (compressed; full detail in iter dirs)

- **001** (NEAR_FAIL ~35) — Crash-protected LETF trend, 4020 cfgs, 0/16 cross-ds winners. See `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md`.
- **002** (FAIL 17) — Clenow 10bps ATR-risk-parity on 11 SPDR sectors → 63-75% cash drag (ATR sized for stocks).
- **003** (FAIL 7) — Clenow adjusted-slope × R² equal-notional on 11 sectors; ≤20-asset homogeneous ETF universe lacks ranking signal.
- **004** (MARGINAL 51) — Single-asset vol-scaling SPY σ⁻¹ (Carver). 6/7 gates spy+ndx, G6 first-ever pass, MDD −6/−9pp; Sharpe edge +0.08-0.15 (below +0.10 spy).

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iterations.

Consumed/closed: 002-005/007/009-014/017/019-036/**037**-**048**. iter 042+043+044 close 3 axes of iter 041 gate enrichment. iter 045 OPENED out-of-family composition (corr 0.58 → DSR 0.222→0.096; 81). iter 046 transplanted onto iter 041 base → corr 0.41 → DSR 0.041 → **85 TOP-K #1**. iter 047 closed weight asymmetry (50/50 IS Pareto-optimum; Bonferroni N=3 cost > grid gain). **iter 048 closed output-side regime leverage gating** (binary VIX<20 → 1.4× output multiplier on iter 046 stream): score 83 < iter 046's 85, **REGRESSION; output is OUTPUT-LEVEL ANALOG of iter 044's INPUT-gate closure** — re-using the same regime classifier at both input and output layers double-counts. **3 distinct modulation mechanisms now CLOSED on iter 046**: input gate (044), weight asymmetry (047), output leverage (048). **Path to 90 must be ADDITIVE** (new uncorrelated stream), not MODULATIVE.

### Iter 049 candidates (iter 046 = 85 TOP-K #1; ALL 3 modulation axes CLOSED by 044/047/048)

- **iter 046 + single-stock momentum on Tiingo 1695-ticker universe (RECOMMENDED #1)** — 1/3 / 1/3 / 1/3 iter 041 + iter 039 + Clenow-style 12-1 momentum on top 50-100 single-stock universe. Universe heterogeneity escapes iter 003's ≤20-asset closure. Data fully available. Risk: turnover cost. ~5-6h.
- **3-leg 041 + 039 + factor-timing (#2, BLOCKED by data)** (MTUM/QUAL/USMV 12-1 mom): MTUM/QUAL/USMV NOT in Tiingo cache (verified 2026-04-25). Either bulk-fetch first, or substitute factor proxies (SPYG/SPYV style/value? — also need to verify cache). ~5-6h including data prep.
- **ML meta-label on iter 046 (#3)** `[advances_fin_ml, ch.3]`: binary open/skip CLASSIFIER on (VIX, T10Y3M, EBP, rolling iter 046 Sharpe). NOT a regime leverage gate (closed by iter 048); a binary include/exclude with logistic regression. ~4h.
- **iter 046 + commodity term-structure carry (#4, data-uncertain)**: DBC/USO/UNG/SPGSCI 3-month roll yield. Need Tiingo manifest review for commodity ETFs. ~4h.

DEAD-LETTER: HMM-2 (044 closure), FX carry (Tiingo 2020+), **weight asymmetry on 046 (047)**, **output-leverage gate on 046 (048)**.

NOT recommended: perturbations of 037/041/046, σ⁻¹/σ⁻²/term-spread/MOVE/EBP gates on 037/041, 4-5-leg basket within iter 046 family, VIX/DTE/strike sweeps, MM σ⁻² on short-vol (040), Kelly-fraction, gate-enrichment on 041 (042/043/044), corr>0.85 (032), N>1 cfg in iter 046 family (047 BF closure), **any regime-classifier MODULATION on iter 046 (044/047/048 closures together — input + weight + output all dominated)**.

### Deeper backlog

- Plano C sleeve meta-allocation (GDE/AVUV/AVDE/AVEM/BTGD).
- Carry + value composite AMP 2013 — orthogonal axes vs iter 024's saturation.
- VRP on broader index (RUT, EFA) — universe extension of iter 026.

---

## Structural dead-ends (1-line summaries; full text in `DEAD_ENDS.md`)

- **Iter 001-014**: daily EMA/SMA × LETF; drawdown-stops; CAPE/EBP/VIX standalone; Clenow ATR/adj-slope ≤20-asset; single-asset σ⁻¹/σ⁻²; TSM overlay; T10Y3M EMA haircut; weekly/monthly cadence; meta-LR; EBP credit.
- **Iter 017/019-021**: 12-1 top-K=1 ≤3 regions; ρ stock-bond overlay; options-on-equity-leg on vol-managed stack (σ²_port absorbs).
- **Iter 022-025**: TOM modulator; TSM-PRIMARY ≤4-asset; bond-curve carry-as-ALLOCATION; slow-EWMAC long-only 6-asset.
- **VRP-harvester family 76 ceiling (026/031/039/040)**: 4/5-leg, basket VIX gates, asymmetric weights, DTE/strike sweeps, MM σ⁻², Kelly. CAGR floor 0/15 + edu DSR > 0.05 structural to T-bill collateral. Open: ML meta-label, positive-CAGR base.
- **Static-stack 84-STRONG ceiling (iter 041) = LOCAL DSR PLATEAU across 3 axes (042 amp / 043 freq / 044 input)** all regress DSR. **iter 046 broke 84 at 85 via out-of-family composition** with iter 039 (NOT gate enrichment). Gate-modification axis CLOSED.
- **Out-of-family composition VINDICATED 2× (iter 045 81 → iter 046 85 TOP-K #1)**: 50/50 convex combo strict-dominates standalone; **score scales inversely with corr** (037+039 ρ=0.58→DSR 0.096; 041+039 ρ=0.41→DSR 0.041). iter 046 = 1st EVER 7/7×3 + DSR sub-0.05×3. **OPEN**: 3-leg + factor-timing (BLOCKED by data), ML meta-label, single-stock momentum on Tiingo universe. **CLOSED on iter 046**: corr>0.85 (032), additive overlay (032), input gate-enrichment (042/043/044), **weight asymmetry (iter 047 closure: 50/50 IS score-function Pareto-optimum)**, **output-leverage regime gating (iter 048 closure: re-using same classifier at input + output double-counts; OUTPUT-LEVEL ANALOG of iter 044)**.
- **iter 047 closure**: pre-committing >1 cfg in iter 046 family costs 6pp gates (Bonferroni α'=0.0167 fails even at raw p=0.04). iter 046-base research must keep N=1 OR earn ≥6pp to amortize BF cost. **Ndx CAGR 15.35% structurally unreachable from iter 041 composites** (cap 12.97%) — must accept ndx 0/15 OR swap base.
- **iter 048 closure**: output-side binary VIX-regime leverage gate (calm 1.4× / stress 1.0×) on iter 046 stream is REDUNDANT with iter 041's input regime gate. **3 modulation mechanisms now closed on iter 046**: input gate (044), weight asymmetry (047), output leverage (048). All 3 trade the same conserved quantity (variance × return) and all 3 fail to break 85. **Path to 90 must be ADDITIVE** (new uncorrelated stream — single-stock momentum on Tiingo 1695-ticker universe is the recommended next direction since data is fully available and universe heterogeneity escapes iter 003's ≤20-asset closure).

---

## Binding constraints (mandate §1, §5, §7)

- **NEVER modify mandate §1** (MAINTENANCE 100% Plano C)
- **Citations obrigatórias** (CLAUDE.md Regra 2): `[book.slug, p.X]`
- **7-gate battery** mandatory per spec §0 criterion
- **DSR n_trials cumulative** — increment `cumulative_n_trials` in this memory's frontmatter each iteration (add this iter's config count)
- **Real data > synth**: synth-only edge does NOT count as winner
- **Pytest baseline must stay green** — never reduce passing count (~796 collected post-iter-011, varies as iters add specs)
- **Max 2 h wall-time** per iteration
- **NEVER commit to git** — the shell `run_loop.sh` handles it
