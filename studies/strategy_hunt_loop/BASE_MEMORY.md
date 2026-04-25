---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 49
winners_found: 0
status: iterating
latest_iteration: "049-2026-04-25-0705"
cumulative_n_trials: 4316
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
| **1** | **046** | 🥇 STRONG | **85** | `iter039_on_iter041_50_50` | `[risk_parity, ch.5]` + Whaley + Sinclair | TOP-K; corr 0.41; 1st EVER 7/7×3 + DSR sub-0.05×3; 0/6 kills; CAGR 0/15 sole gap to 90 |
| **2** | **041** | 🥇 STRONG | **84** | `regime_weights_vix_lt20_70_40_40_ge20_30_55_55` | `[risk_parity, ch.5]` + Whaley | 1st 84; DSR 0.222→0.168 escape; gate-mod axis closed (042/043/044); used in iter 046 |
| **3** | **045** | 🥇 STRONG | **81** | `iter039_on_iter037_50_50` | `[risk_parity, ch.5]` + Sinclair | out-of-family 50/50 037+039; ρ=0.58; DSR 0.222→0.096; ndx 7/7; 0/6 kills; superseded by 046 |
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

### 049 — 2026-04-25 — iter046-plus-gold-tsm (🥉 MARGINAL, 59/100 frozen / 64 custom, **4/6 KILLS, additive 50/50 axis CLOSED, DEEPEST single-iter regression in loop**)
- **Result:** 50/50 combo iter 046 saved stream + gold TSM 90d (boolean trend on GLD, cash@rf=2%). Sharpe edu/spy/ndx **0.92/1.02/1.03** (Δ046 **−0.287/−0.307/−0.354** — widest 3/3 dropouts in loop), gates 6/6/6 (G2 fails 3/3), DSR p=**0.323/0.310/0.321** (8× iter 046's 0.044, n=4316), **corr(046,gold)=0.528/0.531/0.516** (predicted 0.10-0.30; Kill C fires), CAGR 8.91/9.36/9.29% (0/3 floors), MDD 19/13/13%, G7 0.0000pp, standalone gold S=0.61/0.69/0.67 (matches MYP 2012), robust 9/9, winner 1/5; score 1:20 2:19 3:0 4:0 5:15 6:5 = 59 frozen / 64 custom. Kills A+B+C+D fired (E+F clean).
- **Lesson:** **At unequal Sharpes 50/50 weighting is sub-optimal regardless of ρ — dilution dominates by Markowitz identity.** S_a=1.32+S_b=0.69 even at ρ=0 gives combined Sharpe 1.25 < 1.32; optimum w_gold ≈ 0.09. iter 046's 50/50 worked only because S_041≈S_039≈1.04. **5 axes now closed on iter 046**: input gate (044), weight asymmetry (047), output leverage (048), 50/50 additive lower-Sharpe (049). Iter 050: w_gold=0.10 single cfg (~30 min), OR pre-screen ρ < 0.30 candidate, OR abandon iter 046 base. See `iterations/049-2026-04-25-0705-iter046-plus-gold-tsm/`.

### 048 — 2026-04-25 — iter046-output-lev-gate (🥇 STRONG, 83/100, 3/6 KILLS, output-leverage axis CLOSED)
- **Result:** Sharpe edu/spy/ndx 1.20/1.29/1.34 (Δ frozen +0.52/+0.39/+0.39; Δ046 −0.0015/−0.0333/−0.0374), gates 7/6/7, DSR p=0.0427/0.0557/0.0438 (n=4315), winner=3/5; score 1:25 2:23 3:10 4:5 5:15 6:5 = 83. Kills B+D+F fired.
- **Lesson:** Output-side regime leverage = OUTPUT-LEVEL ANALOG of iter 044's INPUT-gate closure. 3 modulation mechanisms closed (044 input + 047 weight + 048 output) — all trade variance×return. See `iterations/048-*/`.

### 047 — 2026-04-25 — iter046-weight-sweep-3cfg (🥇 STRONG, 79/100, weight axis CLOSED)
- **Result:** 3-cfg sweep w_041 ∈ {0.5,0.65,0.8}, best=50/50 (≡ iter 046). Bonferroni α'=0.0167 destroys G2 (raw 0.042 fails); score 79 frozen/84 custom. Kills A+B fired.
- **Lesson:** iter 046's 50/50 IS the score-function Pareto-optimum; weight asymmetry trades DSR Δ−10 > CAGR Δ+5. Ndx CAGR 15.35% structurally unreachable from iter 041 composites. See `iterations/047-*/`.

### 046 — 2026-04-25 — iter039-overlay-on-iter041 (🥇 STRONG, 85/100, TOP-K #1, 0/6 KILLS)
- **Result:** 50/50 iter 041+iter 039. Sharpe edu/spy/ndx 1.20/1.32/1.38, DSR p=0.0414/0.0416/0.0311 (1st EVER sub-0.05×3, n=4311), gates 7/7/7 (1st EVER), CAGR 9.16/9.45/9.76% (edu razor-thin 0.02pp short of floor), MDD 17.97/15.22/14.57%, corr(041,039)=0.41, WF 8/8×3, winner 4/5; score 1:25 2:25 3:15 4:0 5:15 6:5 = 85.
- **Lesson:** Out-of-family composition score advantage scales inversely with corr (045 ρ=0.58→81; 046 ρ=0.41→85). 5-pt gap to WINNER on CAGR-floor only. See `iterations/046-*/`.

### 045 — 2026-04-25 — iter039-overlay-on-iter037 (🥇 STRONG, 81/100)
- **Result:** 50/50 iter 037+iter 039 (ρ=0.587). Sharpe 1.10/1.28/1.33, DSR 0.0962/0.0572/0.0495 (ndx sub-0.05), CAGR 9.7/10.4/10.6%, MDD 22.6/16.3/15.4%, gates 6/6/7, winner 3/5; score 25/21/10/5/15/5 = 81.
- **Lesson:** Out-of-family composition at moderate corr compounds DSR (037 standalone DSR 0.222→0.096). iter 046 superseded at lower corr. See `iterations/045-*/`.

### Iters 015-044 (compressed 1-line; full detail in `iterations/NNN-*/`)
- **044** (🥈 74, multifeature-regime-vix-t10y3m) score 1:25 2:19 3:**0** 4:10 5:15 6:5 = 74; DSR 0.240 worst-p DEEPEST 041-perturb. PRINCIPLE: 2-feat composite over-classifies stress + T10Y3M dilutes VIX; 041's 84-ceiling LOCAL PLATEAU; **045+ MUST go OUT-OF-FAMILY** (vindicated by 045/046).
- **043** (🥇 79, hysteretic-vix-regime-weights) DSR worst-p REGRESS 0.168→0.189 (Kill B); MDD best static-stack ever; PRINCIPLE: halving regime crossings introduces regime-lag variance > path-variance gain; localizes 84-ceiling on gate-timing axis.
- **042** (🥈 74, combined-regime-lev-weights) DSR REGRESS 0.168→0.216, MDD deepest-ever; PRINCIPLE: amplifying lev asymmetry adds path variance > mean return; "compose × leverage compound DSR" FALSIFIED.
- **041** (🥇 84 prior TOP-K #1, regime-weights-vix) Sharpe 1.03/1.13/1.16, DSR 0.168 (1st static-stack escape from 037's 0.222), calm 0.70/0.40/0.40 (1.50×) / stress 0.30/0.55/0.55 (1.40×). 84 ceiling held until iter 046 → 85.
- **040** (🥈 69, vrp-basket-vol-target) MM σ⁻² on 039: ALL DEGRADE; σ⁻² ABSORBS short-vol harvest.
- **039** (🥇 76, basket 3etf 1/3-eq) Sharpe 1.14/1.29/1.56, DSR 0.075/0.061/0.006 (ndx loop-record), MDD 14/7/7%; VRP family ceiling 76 (CAGR 0/15 structural). **Used as iter 045/046 component**.
- **038** (🥇 79, regime-lev-vix) DSR 0.204 best static-stack > 0.20; binary VIX-gate MDD-additive + Sharpe-neutral.
- **037** (🥇 79, 3-leg preserved-lev) Sharpe 0.98/1.15/1.17, DSR 0.222, MDD 33/25/32%; AMP 2013 orthogonality. **Used as iter 045 component**.
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

Consumed/closed: 002-005/007/009-014/017/019-036/**037**-**049**. iter 044/047/048/049 close 4 axes of iter 046: input gate (044), weight asymmetry (047), output leverage (048), 50/50 additive lower-Sharpe stream (049). Path forward narrowed.

### Iter 050 candidates (iter 046 = 85 TOP-K #1; FOUR axes closed by 044/047/048/049)

- **iter 046 + gold TSM at LOWER WEIGHT (RECOMMENDED #1)** — single cfg `w_gold=0.10` (~Markowitz optimum given S_046=1.32, S_gold=0.69, ρ=0.53). Predicted 86-88 (small CAGR-floor pass on edu, no DSR collapse). Cheap test (~30 min). Direct mathematical follow-up to iter 049's Markowitz post-mortem.
- **iter 046 + verified-low-corr 3rd stream (#2)** — pre-screen ρ to iter 046 saved stream BEFORE backtest commit. Candidates: TSM on USO (oil; ρ predicted 0.30-0.40, Sharpe 0.20-0.40), TSM on TLT (long bonds; ρ ~0.30-0.50 with iter 041 IEF leg), TSM on SLV (silver; ρ~0.45-0.55 — gold-correlated). HYG/EFA/EEM correlated equity-like — skip.
- **iter 037 + iter 026 (single-asset SPY VRP) 50/50 (#3)** — iter 037 standalone score 79; iter 026 score 76 (1st DSR PASS ndx). 50/50 combo at corr likely 0.50-0.60 — same Markowitz dilution risk as iter 049 unless components are Sharpe-comparable (S_037~1.10, S_026~1.27 — fairly similar).
- **iter 046 with iter 037 substituted for iter 041 base (#4)** — collapses to iter 045 base (already scored 81). Useful only as sanity replication.
- **Single-stock momentum on Tiingo equities (DEFERRED, data window limited)** — 1632 equities in cache but ALL start ≥ 2013-01 (none cover 2009-06-25 spy_real start). Verified 2026-04-25.

DEAD-LETTER: HMM-2 (044), FX carry (Tiingo post-2020), weight asymmetry on 046 (047), output-leverage on 046 (048), **50/50 additive lower-Sharpe stream on 046 (049)**, MTUM/QUAL/USMV factor-timing (NOT in cache, verified 2026-04-25).

NOT recommended: perturbations of 037/041/046, σ⁻¹/σ⁻²/term-spread/MOVE/EBP gates on 037/041, 4-5-leg basket within iter 046 family, VIX/DTE/strike sweeps, MM σ⁻² on short-vol (040), Kelly-fraction, gate-enrichment on 041 (042/043/044), corr>0.85 (032), N>1 cfg in iter 046 family (047 BF closure), any regime-classifier MODULATION on iter 046 (044/047/048), **50/50 additive 3rd stream on iter 046 with S_3rd < 1.10 (049 closure: dilution dominates regardless of ρ by Markowitz identity)**.

### Deeper backlog

- Plano C sleeve meta-allocation (GDE/AVUV/AVDE/AVEM/BTGD).
- Carry + value composite AMP 2013 — orthogonal axes vs iter 024's saturation.
- VRP on broader index (RUT, EFA) — universe extension of iter 026.

---

## Structural dead-ends (1-line summaries; full text in `DEAD_ENDS.md`)

- **Iter 001-014**: daily EMA/SMA × LETF; drawdown-stops; CAPE/EBP/VIX standalone; Clenow ATR/adj-slope ≤20-asset; single-asset σ⁻¹/σ⁻²; TSM overlay; T10Y3M EMA haircut; weekly/monthly cadence; meta-LR; EBP credit.
- **Iter 017/019-021**: 12-1 top-K=1 ≤3 regions; ρ stock-bond overlay; options-on-equity-leg on vol-managed stack.
- **Iter 022-025**: TOM modulator; TSM-PRIMARY ≤4-asset; bond-curve carry-as-ALLOCATION; slow-EWMAC long-only 6-asset.
- **VRP-harvester family 76 ceiling (026/031/039/040)**: CAGR floor 0/15 + edu DSR > 0.05 structural to T-bill collateral.
- **Static-stack 84-STRONG ceiling = LOCAL DSR PLATEAU**: iter 042 amp / 043 freq / 044 input all regress DSR.
- **Out-of-family composition VINDICATED**: iter 045 (81, ρ=0.58) → iter 046 (85, ρ=0.41) TOP-K #1; score scales inversely with corr.
- **iter 047 closure**: 50/50 IS Pareto-optimum on iter 046; Bonferroni N=3 cost > grid gain; ndx CAGR 15.35% unreachable from iter 041 composites.
- **iter 048 closure**: output-side regime gate is OUTPUT-LEVEL ANALOG of iter 044's input closure — re-using same VIX classifier double-counts.
- **iter 049 closure**: 50/50 additive 3rd stream on iter 046 with S_3rd < 1.10 fails by Markowitz identity REGARDLESS of ρ — dilution effect dominates correlation diversification. Specifically: gold TSM 90d (S=0.69, ρ=0.53) at w=0.5 produces combined Sharpe 1.03 (formula prediction matches observed 1.02), score 59 MARGINAL — −26 vs iter 046's 85, deepest single-iter regression in loop. **Markowitz optimum w_gold ≈ 0.09**, NOT 0.50. Closure applies to ANY S_3rd < 1.10 stream at 50/50 on iter 046; future picks must use w ≤ 0.20 OR find S_3rd-comparable stream with verified ρ < 0.30 OR abandon iter 046 base. **5 distinct iter 046 enhancement axes now CLOSED** (input/weight/output/additive-50-50/...).

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
