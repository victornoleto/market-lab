---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 45
winners_found: 0
status: iterating
latest_iteration: "045-2026-04-25-0528"
cumulative_n_trials: 4310
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
| **1** | **041** | 🥇 STRONG | **84** | `regime_weights_vix_lt20_70_40_40_ge20_30_55_55` | `[risk_parity, ch.5]` + Whaley 2009 | **TOP**; 1st 84; DSR 0.222→0.168 escape; 4/5 winner; 042/043/044 all REGRESS (gate-mod axis closed) |
| **2** | **045** | 🥇 STRONG | **81** | `iter039_on_iter037_50_50` | `[risk_parity, ch.5]` + Sinclair 2013 | **NEW #2**; out-of-family 50/50 037+039; corr 0.58 vindicates compounding; DSR 0.222→**0.096** (best stack family); ndx 7/7 + DSR sub-0.05; **0/6 kills**; CAGR 5/15 sole gap to 90 |
| **3** | **038** | 🥇 STRONG | **79** | `regime_lev_vix_lt20_lo10_hi17` | `[advances_fin_ml, ch.17-18]` + MM 2017 | VIX-gated 1.7/1.0× on 037; MDD −4/−8pp; DSR 0.204 |
| **3** | **037** | 🥇 STRONG | **79** | `ntsx_3leg_preserved_60_45_45_spy_ief_gld` | `[risk_parity, ch.5]` + AMP 2013 | 1st plain static-stack 79; Sharpe +0.30/+0.25/+0.22 |
| **3** | **016** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20` | `[risk_parity, p.10-11]` + MM 2017 | 60:40 × MM vol-target; Sharpe +0.24-0.30; DSR 0.226 |
| **3** | **018** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20_funded` | `[risk_parity, p.80-84]` | 016 + funding cost (−93 to −148 bps/yr); ties 016 |
| **3** | **021** | 🥇 STRONG | **79** | `ntsx_vm_..._scs5_10_1m` | `[volatility_trading, ch.3]` | 016 + short put-cs; MDD −1/−3pp; DSR 0.217 |
| **3** | **043** | 🥇 STRONG | **79** | `hysteretic_vix_low18_high22_w70_40_40_30_55_55` | `[advances_fin_ml, ch.17-18]` + Hamilton 1989 | Schmitt 041w; RT/yr 2.5 = halved; falsifies path-variance |
| **9** | **035** | 🥇 STRONG | **77** | `static_stack_90_60_spy_gld` | `[risk_parity, ch.5]` + Erb-Harvey 2006 | gold-not-bond axis; best static DSR (0.344) |
| 9 | 015 | 🥇 STRONG | 77 | `ntsx_synth_90_60_daily` | `[risk_parity, p.5]` + AFP 2012 | 1st escape σ²_port cointegration |
| **11** | **039** | 🥇 STRONG | **76** | `vrp_basket_eq3_5_10_1m` | `[volatility_trading, p.218]` + Bondarenko 2014 | T-bill + 1/3 SPY+QQQ+IWM put cs; loop-record DSR ndx 0.006 |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 045 — 2026-04-25 — iter039-overlay-on-iter037 (🥇 STRONG, 81/100, **0/6 KILLS, NEW TOP-K #2**)
- **Result:** 50/50 convex combo iter 037 stack (0.6 SPY + 0.45 IEF + 0.45 GLD) + iter 039 VRP basket (T-bill + 1/3 SPY+QQQ+IWM 5/10 put cs). Sharpe edu/spy/ndx **1.10/1.28/1.33** (Δ frozen +0.42/+0.38/+0.37; **Δ041 +0.08/+0.15/+0.16 strict-dominates 041**), gates 6/6/**7** (1st 7/7 ndx on stack family), DSR p=**0.096/0.057/0.0495** (n=4310; **best worst-p of stack family**: 037's 0.222 → **0.096 = 57% reduction**; ndx PASSES sub-0.05), CAGR 9.7/10.4/10.6% (edu ✓; spy/ndx fail by 1.54/4.72pp — 50% T-bill caps), MDD 22.6/**16.3/15.4%** (Δ041 −5/−8/−15pp), G7 **0.0000pp on 3/3**, **corr(037,039)=0.587/0.582/0.569** (orthogonality vindicated; iter 032's 0.97 NOT re-triggered), WF 8/8 on 3/3, robust 9/9, winner 3/5; score 1:25 2:21 3:10 4:**5** 5:15 6:5 = **81**. `[risk_parity, ch.5]` + `[volatility_trading, p.218]` Sinclair 2013 + Markowitz 1952. Cfg `iter039_on_iter037_50_50`.
- **Lesson:** Out-of-family composition at moderate corr (ρ≈0.58, < Kill F 0.85) **structurally compounds DSR** — iter 037's 0.222 → 0.096 on same architecture. iter 045 strict-dominates iter 041 on Sharpe/MDD/DSR/gates/robustness; 3-pt gap to 84 is **entirely on CAGR axis** (5/15 vs 15/15) — T-bill collateral caps combined CAGR at ~10%. **Recipe validated**: convex combo + ρ ∈ [0.4, 0.7] + both components STRONG-tier. iter 046 PICK: weight sweep (CAGR↑ vs DSR trade-off, 3-4 cfg pre-committed grid) — single-axis path to break 84. See `iterations/045-*/`.

### Iters 015-044 (compressed 1-line; full detail in `iterations/NNN-*/`)
- **044** (🥈 74, multifeature-regime-vix-t10y3m, 3/6 KILLS — DEEPEST DSR REGRESS on 041 weights) Sharpe 0.97/1.10/1.10 (Δ041 −0.06/−0.04/−0.07 Kill A 2/3), gates 6/6/6, DSR p=**0.240**/0.205/0.229 (n=4309; worst-p 0.168→**0.240 +0.072 DEEPEST** 041-perturb), CAGR ndx <floor 0.66pp, MDD Δ041 +2-7pp (clean), G7 0.123pp, robust 9/9, winner 3/5; score 1:25 2:19 3:**0** 4:10 5:15 6:5 = **74**. PRINCIPLE: 2-feat composite over-classifies stress (52% vs 41's 64-67%) + T10Y3M noise dilutes VIX precision; 041's 84-ceiling LOCAL PLATEAU across 3 orthogonal axes (042 amp / 043 freq / 044 input). 045+ MUST go OUT-OF-FAMILY.
- **043** (🥇 79, hysteretic-vix-regime-weights, 2/6 KILLS) Sharpe 1.03/1.12/1.13 Δ041 +0.01/−0.01/−0.03 (Kill A clean), DSR 0.161/0.179/**0.189** worst-p REGRESS 0.168→0.189 (Kill B fires); MDD 25.68/**22.92**/27.75% Δ041 −1.92/−1.73/−3.09pp (best static-stack MDD ever, Kill C clean), ndx CAGR <floor 0.30pp, score **79** (Kill D fires −5). RT/yr 2.5 = halved (Kill F clean). PRINCIPLE: halving regime crossings introduces *regime-lag variance* (delayed band transitions) that dominates path-variance gain; with iter 042 jointly localizes 84-ceiling on gate-timing axis (amplitude + frequency).
- **042** (🥈 74, combined-regime-lev-weights, 2/6 KILLS) Sharpe 1.02/1.09/1.13 Δ041 ≈ −0/−0.04/−0.04, DSR 0.175/**0.216**/0.196 REGRESS worst-p 0.168→0.216, MDD 22.21/22.21/28.85% deepest-ever, ndx CAGR <floor, G7 1.0pp, score 74. PRINCIPLE: amplifying asymmetry (lev range 0.10→0.70) adds path variance > mean return → DSR worse; "compose × leverage compound DSR" FALSIFIED.
- **041** (🥇 84 TOP-K #1, regime-weights-vix, 1/6 KILLS) Sharpe 1.03/1.13/1.16 Δ037 +0.04/−0.02/−0.01, DSR 0.168/0.167/0.156 **1st static-stack 0/15→5/15 escape** from 037's 0.222, MDD 27.6/24.6/30.8% Δ037 ALL improve, G7 0.124pp, score **84** (broke 79 ceiling held 6 iters). Cfg calm 0.70/0.40/0.40 (1.50×) vs stress 0.30/0.55/0.55 (1.40×). PRINCIPLE: composition shift adds DSR power independent of scale shift; but iter 042+043 falsify both gate-timing perturbations.
- **040** (🥈 69, vrp-basket-vol-target) MM σ⁻² wrapper on 039: Sharpe 1.04/1.21/1.31 Δ039 ALL DEGRADE, DSR worse, score 69. PRINCIPLE: σ⁻² ABSORBS short-vol harvest (premium = f(IV) → σ⁻² removes exposure when E[harvest] peaks). Closes MM σ⁻² on short-vol.
- **039** (🥇 76, basket 3etf 1/3-eq, 0/6 KILLS) Sharpe 1.14/1.29/1.56 (Δ frozen +0.46/+0.39/+0.61; Δ026 +0.01/+0.01/+0.19), gates 6/6/7, DSR p=0.075/0.061/**0.006** (loop-record ndx sub-0.01, 6.4× tighter than 026), MDD 14/7/7%, G7 0.0000pp, robust 9/9; score 1:25 2:21 3:10 4:0 5:15 6:5 = **76**. PRINCIPLE: cross-asset VRP basket TRIPLE-DOMINATES iter 026 operationally but score-ties at 76 — VRP family ceiling structurally CAGR-floor 0/15 + edu DSR > 0.05 (T-bill + GFC cluster ρ→1). Closes 4/5-leg, VIX gates on basket, asymmetric weights, DTE/strike sweeps.
- **038** (🥇 79, regime-lev-vix) Sharpe 0.998/1.105/1.149 (Δ037 +0.02/−0.05/−0.03), DSR 0.204 (best static-stack > 0.20), MDD 25/22/29% (Δ037 −8/−4/−4pp best of any STRONG), G7 0.087pp, lev avg 1.46-1.49; score 1:25 2:19 3:0 4:15 5:15 6:5 = **79**. PRINCIPLE: static-stack DSR-bound at 79; binary VIX-gate MDD-additive + Sharpe-neutral + DSR-marginal. Two-axis: DSR-bound + MDD freely optimizable.

- **037** (🥇 79, 3-leg preserved-lev) Sharpe 0.98/1.15/1.17 (Δ015 +0.20/+0.11/+0.11), DSR 0.222 (best static-stack until 038), MDD 33/25/32% (1st 3/3 clean), G7 max 0.134pp; score 1:25 2:19 3:0 4:15 5:15 6:5 = **79**. PRINCIPLE: Static-stack 77 ceiling BROKEN at 79; AMP 2013 orthogonality survives 33% equity cut. DSR-bound at 79; ties top-K #1.
- **036** (🥈 72, 3-leg additive 1.8×) Sharpe 0.92/1.15/1.15, DSR 0.311, MDD ndx 41.53% breach +1.41pp; score 72. PRINCIPLE: +0.30 lev breaks ndx MDD → net 72. Subsumed by 037 strict-dominates.

- **035** (🥇 77, GLD substitution) Sharpe 0.877/1.070/1.103 (Δ015 +0.094/+0.026/+0.040), DSR 0.344/0.236/0.219, MDD 3/3 clean; score 1:25 2:17 3:0 4:15 5:15 6:5 = **77**. PRINCIPLE: 77 ceiling asset-class-agnostic; iter 015 edge was DIVERSIFICATION not bond-carry.
- **034** (🥈 72, 3-leg bond-carry sleeve) Sharpe 0.795/1.058/1.075 (Δ015 +0.011/+0.014/+0.012), DSR 0.529/0.250/0.253, MDD ndx 42.11% breach; score 72. PRINCIPLE: subsumed by 035 — 77 ceiling architecture-bound, not bond-specific.
- **033** (🥈 72, IEF→TLT swap 0.9/0.6) Sharpe 0.85/1.04/1.06, DSR 0.31/0.28/0.27, MDD ndx 47% breach; score 72. PRINCIPLE: bond-duration is CAGR-MDD trade-off NOT Sharpe lever (variance scales with duration², cancels carry).
- **032** (🥈 72, layered iter 015 + iter 031 VRP) Sharpe 0.81/1.04/1.08, DSR 0.50/0.28/0.25, MDD ndx 44% breach (corr_SPY=+0.97 put-spread amplifies eq DD); score 72. PRINCIPLE: composed-strategy DSR penalty dominated by COMPOSITE higher moments, not layer DSRs.
- **031** (🥇 76, top-K #5 tied, ALL 6 CLEAN, 1st all-3 DSR<0.10) AND-composite R-1∧R-2 on iter 026: Sharpe 1.19/1.28/1.33, DSR 0.054/0.070/0.050. CLOSURE: 5 iters on iter 026 base capped at 76; CAGR floor structural to harvest_notional=1.0.

- **030** (🥈 71, Kill A+B) Z-score gate (z_60d, 2σ) on iter 026: spy 7/7 + DSR 0.0345 PASS but edu Kill B + ndx Kill A 2.6×.
- **029** (🥈 71, Kill A 2bp) Level + 3d persistence on iter 028: edu DSR 0.0251 record, worst-p 0.100 missed by 0.0003.
- **028** (🥈 71) Constant `VIX<35` filter on iter 026: edu 1st-ever 7/7 + DSR p=0.029 but spy/ndx regress; closes constant-threshold.
- **027** (🥈 74) Levered (N=3.5) iter 026: CAGR 3/3 ✓ but Sharpe regress + DSR collapse; rf-bonus diluted by leverage.
- **026** (🥇 76, top-K #5) Stand-alone VRP harvest T-bill + short SPY 5/10% put cs: Sharpe 1.13/1.28/1.37, ndx 1st 7/7 + 1st DSR PASS (p=0.038).
- **025** (📉 39) Slow-EWMAC long-only 6-asset basket: long-only sacrifices 50% trend premium.
- **024** (🥈 72) Bond-curve carry-as-ALLOCATION static stack: 3/3 Sharpe edge but DSR worst 0.586 binds.
- **023** (📉 28) TSM-primary 3-ETF per-asset vol-target: turnover dominates sqrt(3) diversification; HOP needs 67 markets.
- **022** (🥉 54) TOM eq:bd modulator: σ²_port quadratic absorbs calendar premium.
- **021** (🥇 79, top-K #1) Short put-cs VRP overlay on 016: MDD −1.95/−1.01/−2.85pp, DSR 0.217.
- **020** (🥇 79) Monthly put-spread tail hedge: long-gamma overlays REDUNDANT with vol-target.
- **019** (❌ 0) HMM stock-bond ρ: pre-val rejects 3/3.
- **018** (🥇 79, top-K #1) Funding-cost 016 replay: each 100bps ≈ −0.07 Sharpe.
- **017** (🥉 52) 12-1 regional rotation N=3: period US Sharpe dominance.
- **016** (🥇 79, top-K #1) Static 60:40 × Moreira-Muir vol-target: Sharpe 0.98/1.14/1.19; fixed × vol-target ADDITIVE.
- **015** (🥇 77) Static synthetic NTSX 90/60 SPY+IEF: 1st iter clearing +0.10 cross-ds.

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

Consumed/closed: 002-005/007/009-014/017/019-036/**037**-**045**. iter 042+043+044 jointly close 3 axes of iter 041 gate enrichment (amplitude/frequency/input — all regress DSR). iter 045 OPENS out-of-family composition (corr 0.58 → DSR 0.222→0.096; score 81 NEW #2). TOP-K #1 unchanged 041 at 84; iter 045 strict-dominates 041 on Sharpe/MDD/DSR/gates/robustness but trails 3pts on CAGR axis only.

### Iter 046 candidates (iter 045 vindicated out-of-family at 81 STRONG; CAGR floor sole 3-pt blocker to break 84)

- **Weight sweep on iter 045 base (RECOMMENDED #1)**: pre-committed 3-4 point grid for `(w_037, w_039)` ∈ {(0.4, 0.6), (0.5, 0.5), (0.6, 0.4), (0.7, 0.3)}. Higher iter 037 weight recovers CAGR at potential DSR cost; explicitly tests CAGR-vs-DSR efficient frontier between two STRONG strategies. Use Bonferroni adjustment on PBO to avoid grid overfit. iter 045's CAGR floor (5/15) is the SINGLE-AXIS blocker between 81 and 90+ (WINNER) — direct attack. ~2h.
- **Layer iter 039 on iter 041 (TOP-K #1) instead of iter 037**: untested combination of regime-conditioning + VRP harvest. iter 041 has higher Sharpe than iter 037 → combined Sharpe ceiling is higher than iter 045. Risk: iter 041's gate may interact destructively with iter 039's VRP cycle (iter 044 closure on gate input perturbation does NOT directly apply since this is gate ENRICHMENT via outside stream, not gate input modification). ~3h.
- **3-leg composition** (iter 037 + iter 039 + factor-timing): add MTUM/QUAL/USMV 12-1 momentum as third return-stream at 1/3 each. Tests whether the corr<0.85 mechanism extends to a 3rd source (AMP 2013 cross-sectional). ~4h.
- **ML meta-label on iter 045 base** `[advances_fin_ml, ch.3]`: binary open/skip classifier on iter 045's combined returns using (VIX, VXN, RVX, T10Y3M, EBP). Could lift iter 045's Sharpe in stress regimes without changing the structural composition. iter 044 closed ADDITIVE composites; non-linear classifier on combined output is functionally distinct. ~4h.
- **Cross-sectional factor timing standalone ≥10 factor ETFs** (out-of-family alternative): MTUM/QUAL/USMV/SIZE/VLUE/SPLV; 12-1 mom + value AMP 2013. Sidesteps 84-plateau entirely with new return architecture. Useful as fallback if weight sweep on iter 045 fails. ~3h.

DEAD-LETTER **HMM-2 multi-feature regime**: iter 044 closes the multi-feature instantaneous-gate direction (worst-p 0.240 vs 041's 0.168). HMM with state-persistence might recover SOME of the loss but iter 043 hysteresis closure suggests state-persistence costs Sharpe. SKIP unless using non-VIX/non-T10Y3M features.

DEAD-LETTER **FX carry**: Tiingo FX 2020+ only (6y insufficient). Parked.

NOT recommended: weight/single-asset perturbations of 037, σ⁻¹/σ⁻²/term-spread/MOVE/EBP gates on 037, 4-5-leg basket, VIX/asymmetric/DTE/strike sweeps on basket, MM σ⁻² on short-vol (040), Kelly-fraction sizing, **gate enrichment on iter 041** any axis (042/043/044 close amplitude/frequency/input).

### Deeper backlog

- Plano C sleeve meta-allocation (GDE/AVUV/AVDE/AVEM/BTGD).
- Carry + value composite AMP 2013 — orthogonal axes vs iter 024's saturation.
- VRP on broader index (RUT, EFA) — universe extension of iter 026.

---

## Structural dead-ends (1-line summaries; full text in `DEAD_ENDS.md`)

- **Iter 001-014**: daily EMA/SMA × LETF + overlay; drawdown-stops; CAPE/EBP/VIX standalone; Clenow ATR/adj-slope ≤20-asset; single-asset σ⁻¹/σ⁻²; TSM 12-1/6-1/18-1 overlay; T10Y3M 21d/5d EMA haircut; weekly/monthly cadence for vol-managed; meta-LR ρ+VIX_z; EBP credit.
- **Iter 017/019-021**: 12-1 top-K=1 rotation on ≤3 regions; ρ stock-bond overlay (closes VIX/MOVE/realized-vol overlays); options-on-equity-leg 5/10%OTM×21DTE on vol-managed stack (σ²_port absorbs). Open: bare puts / ATM straddles / different DTE on STATIC base.
- **Iter 022-025**: TOM eq:bd modulator (σ²_port quadratic); TSM-PRIMARY ≤4-asset per-asset vol-target (turnover dominates √N); bond-curve carry-as-ALLOCATION 2-bond static; slow-EWMAC long-only 6-asset basket. Open: cross-asset carry, ≥20-asset, long-SHORT EWMAC, carry+value.
- **VRP-harvester family ceiling 76 STRONG across 4 attacks (026/031/039/040)**: T-bill +0.38-0.45 Sharpe (026); linear-lev rf-dilutes (027); VIX-gates cap 76/71 (028-031); basket ties 76 (039); MM σ⁻² wrapper regresses to 69 (040). CAGR floor 0/15 + edu DSR > 0.05 structural to T-bill collateral. Closes 4/5-leg, basket VIX gates, asymmetric weights, DTE/strike sweeps, MM σ⁻², Kelly sizing. Open break-76: ML meta-label, positive-CAGR base, cross-sectional factor timing.
- **Static-stack 84-STRONG ceiling (iter 041) = LOCAL DSR PLATEAU across 3 axes.** 041 binary VIX@20 → DSR 0.168 score **84**; 042 amplitude (compound 041w×038lev) → 0.216 −10; 043 frequency (hysteretic [18,22]) → 0.189 −5; 044 input (composite VIX+T10Y3M) → 0.240 −10 DEEPEST. Any structural gate enrichment regresses DSR 4-7pp via different mechanisms; 041's binary-VIX-20 IS local optimum on plateau. Closed: 037-weight perturb, compound, hysteretic [18,22], 2-feat equal-weight τ=0. Open break-84: out-of-family return-stream (✓ iter 045 vindicated at 81 with corr 0.58, DSR 0.096), ML meta-label, different gate ASSET (CDS/gold-ratio/DXY) — gate-modification axis CLOSED.
- **Out-of-family composition VINDICATED (iter 045, score 81 NEW #2)**: iter 037 + iter 039 50/50 convex combo at corr 0.58 strict-dominates iter 041 on Sharpe/MDD/DSR/gates/robustness. **DSR worst-p 0.222 → 0.096 (57% reduction)** on same architecture; ndx_real PASSES sub-0.05 with 7/7 gates. CAGR floor (5/15) is sole 3-pt blocker to 84. **OPEN**: weight sweep (CAGR↑ vs DSR↑ trade-off), iter 039 layered on iter 041 (higher Sharpe ceiling), 3-leg composition with factor-timing. **CLOSED for this family**: composition at corr > 0.85 (iter 032 0.97 failure), additive overlay (iter 032), composing two strategies with single-asset components (use baskets for diversification).

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
