---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 46
winners_found: 0
status: iterating
latest_iteration: "046-2026-04-25-0553"
cumulative_n_trials: 4311
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

### 046 — 2026-04-25 — iter039-overlay-on-iter041 (🥇 STRONG, 85/100, **0/6 KILLS, NEW TOP-K #1**)
- **Hypothesis & Cfg:** Transplant iter 045's out-of-family composition onto iter 041 (TOP-K #1=84) instead of iter 037. Single pre-committed cfg `iter039_on_iter041_50_50` (verbatim 041 calm/stress weights {0.70/0.40/0.40}↔{0.30/0.55/0.55} threshold 20.0; verbatim 039 1/3 SPY+QQQ+IWM 5/10 put cs T-bill); cumulative_n_trials 4310→**4311**. `[risk_parity, ch.5]` + `[volatility_trading, p.218]` + `[advances_fin_ml, ch.17-18, p.31-34, p.162-164, p.222-223]` + Whaley 2009, Bondarenko 2014, Carr-Wu 2009, DMV 2009, Erb-Harvey 2006, AMP 2013, Markowitz 1952.
- **Result:** Sharpe edu/spy/ndx **1.20/1.32/1.38** (Δ frozen +0.52/+0.42/+0.43; **Δ045 +0.10/+0.04/+0.06 strict-dominates 045**), gates **7/7/7 (1st EVER 7/7×3)**, DSR p=**0.0414/0.0416/0.0311 (1st EVER sub-0.05×3)** (n=4311; 041's 0.168→0.041 = 75% reduction), CAGR 9.16/9.45/9.76% (0/3 frozen — edu by 0.02pp razor-thin), MDD **17.97/15.22/14.57%** (Δ045 −4.6/−1.0/−0.8pp), G7 **0.0000pp on 3/3**, **corr(041,039)=0.403/0.425/0.413** (LOWER than 045's 0.58 — regime tilt counter-cyclically decorrelates with VRP), WF 8/8 on 3/3, robust 9/9, winner 4/5; score 1:25 2:**25** 3:**15** 4:**0** 5:15 6:5 = **85** (custom-bench 90).
- **Lesson:** Out-of-family composition score advantage scales **inversely with corr** (037+039 ρ=0.58→DSR 0.096→81; 041+039 ρ=0.41→DSR 0.041→**85**). Strict-dominates 041 AND 045 on Sharpe/MDD/gates/DSR/robustness; only CAGR floor (0/15) blocks WINNER. Break-90 path: weight asymmetry (0.65-0.7 → CAGR ↑) OR 3-leg + positive-CAGR factor-timing. iter 047 PICK: 3-cfg weight sweep. See `iterations/046-*/`.

### 045 — 2026-04-25 — iter039-overlay-on-iter037 (🥇 STRONG, 81/100)
- **Result:** 50/50 iter 037+039. Sharpe edu/spy/ndx 1.10/1.28/1.33 (Δ frozen +0.42/+0.38/+0.37), gates 6/6/7, DSR p=0.0962/0.0572/0.0495 (n=4310; iter 037's 0.222 → 0.096 = 57% reduction), CAGR 9.7/10.4/10.6% (edu ✓; spy/ndx fail), MDD 22.6/16.3/15.4%, G7 0.0000pp on 3/3, corr(037,039)=0.587/0.582/0.569, WF 8/8 on 3/3, robust 9/9, winner 3/5; score 1:25 2:21 3:10 4:5 5:15 6:5 = **81**.
- **Lesson:** Out-of-family composition at moderate corr (ρ≈0.58) structurally compounds DSR — convex combo + ρ ∈ [0.4, 0.7] + both components STRONG-tier = recipe; CAGR floor (T-bill collateral cap) is the binding constraint. iter 046 transplanted to iter 041 base improved further. See `iterations/045-*/`.

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

Consumed/closed: 002-005/007/009-014/017/019-036/**037**-**046**. iter 042+043+044 close 3 axes of iter 041 gate enrichment. iter 045 OPENED out-of-family composition (corr 0.58 → DSR 0.222→0.096; 81). **iter 046 transplanted onto iter 041 base → corr 0.41 → DSR 0.041 → 85 NEW TOP-K #1**, strict-dominating iter 041+045 on Sharpe/MDD/gates/DSR/robustness; CAGR floor 0/15 is sole 5-pt blocker to 90+ WINNER tier.

### Iter 047 candidates (iter 046 = 85 NEW #1; CAGR floor 0/15 sole blocker)

- **Weight sweep on iter 046 base (RECOMMENDED #1)**: pre-committed 3-cfg `(w_041 ∈ {0.5, 0.65, 0.8})` Bonferroni-adjusted PBO. Higher iter 041 weight recovers CAGR at potential DSR cost. iter 046's edu CAGR fails frozen floor by 0.02pp; spy/ndx by 2.5/5.6pp. Single-axis path to break 85. ~2h.
- **3-leg iter 041 + iter 039 + factor-timing** (MTUM/QUAL/USMV 12-1 mom): 1/3 each; positive-CAGR 3rd uncorrelated stream lifts combined CAGR over floor; risk corr 041×factor > 0.5. ~4h.
- **iter 046 + cross-asset carry leg** (replace 039 with commodity term-structure or FX carry, AMP 2013): carry CAGR 8-12% lifts combined CAGR; risk: FX 2020+ only (parked). ~5h.
- **iter 046 × OUTPUT-leverage gate**: VIX<20 → 1.4× iter 046; ≥20 → 1.0×. Modulates combined stream (NOT inputs); iter 044 closed INPUT gate-enrichment but output-gate is distinct. ~3h.
- **ML meta-label on iter 046** `[advances_fin_ml, ch.3]`: binary open/skip on (VIX, VXN, RVX, T10Y3M, EBP); non-linear vs 044's additive composite. ~4h.

DEAD-LETTER: **HMM-2 multi-feature regime** (044 closure unless non-VIX/non-T10Y3M features); **FX carry** (Tiingo 2020+ only, 6y insufficient).

NOT recommended: weight/single-asset perturbations of 037/041, σ⁻¹/σ⁻²/term-spread/MOVE/EBP gates on 037/041, 4-5-leg basket, VIX/DTE/strike sweeps on basket, MM σ⁻² on short-vol (040), Kelly-fraction sizing, gate enrichment on iter 041 (042/043/044), composition with corr > 0.85 (iter 032).

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
- **Out-of-family composition VINDICATED 2× (iter 045 score 81 → iter 046 score 85 NEW TOP-K #1)**: 50/50 convex combo of static/regime stack + iter 039 VRP basket strict-dominates standalone. **Score advantage scales inversely with corr**: 037+039 (corr 0.58) → DSR 0.096 → 81; **041+039 (corr 0.41) → DSR 0.041 → 85**. iter 046 is **1st EVER 7/7 gates × 3 datasets + DSR sub-0.05 × 3**. Mechanism: regime tilt counter-cyclically decorrelates with VRP cycle. **OPEN**: weight asymmetry on iter 046 (CAGR↑ Pareto), 3-leg + factor-timing (lifts CAGR), output-leverage gate, ML meta-label. **CLOSED**: composition at corr > 0.85 (iter 032 0.97), additive overlay (032), gate-enrichment on inputs (042/043/044). CAGR-floor (0/15 iter 046) is single 5pt blocker to WINNER tier.

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
