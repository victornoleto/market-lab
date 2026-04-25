---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 40
winners_found: 0
status: iterating
latest_iteration: "040-2026-04-25-0338"
cumulative_n_trials: 4305
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

## Top-K strategies ranked (best of all iterations, by score)

| rank | iter | tier | score | strategy slug | primary citation | headline |
|---|---|---|---|---|---|---|
| **1** | **038** | 🥇 STRONG | **79** | `regime_lev_vix_lt20_lo10_hi17` (VIX-gated 1.7/1.0× on iter 037) | `[advances_fin_ml, ch.17-18]` + MM 2017 | Ties 79; MDD −4/−8pp vs 037 best of STRONG; DSR 0.204 best ever; MM uplift NOT on diversified |
| **1** | **037** | 🥇 STRONG | **79** | `ntsx_3leg_preserved_60_45_45_spy_ief_gld` (0.6 SPY+0.45 IEF+0.45 GLD, 1.5×) | `[risk_parity, ch.5]` + AMP 2013 | 1st plain static-stack at 79; **breaks 77 ceiling**; 4/5 winner; Sharpe +0.30/+0.25/+0.22; DSR 0.222 sole fail |
| **1** | **016** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20` (60:40 × MM vol-target) | `[risk_parity, p.10-11]` + MM 2017 | 4/5 winner; Sharpe +0.24-0.30; DSR 0.226 sole fail |
| **1** | **018** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20_funded` (016 + r_Tbill drag) | `[risk_parity, p.80-84]` | edges survive funding cost (−93 to −148 bps/yr); ties 016 |
| **1** | **021** | 🥇 STRONG | **79** | `ntsx_vm_..._scs5_10_1m` (016 + short put-spread VRP) | `[volatility_trading, ch.3]` | Sharpe-neutral; MDD −1 to −3pp; DSR p=0.217 record |
| **6** | **035** | 🥇 STRONG | **77** | `static_stack_90_60_spy_gld` (static 0.9 SPY + 0.6 GLD) | `[risk_parity, ch.5]` + Erb-Harvey 2006 + AMP 2013 | TIES 015 ceiling from gold-not-bond axis; Δ015 +0.094/+0.026/+0.040 Sharpe; best static DSR ever (0.344) |
| 6 | 015 | 🥇 STRONG | 77 | `ntsx_synth_90_60_daily` (static 0.9 SPY + 0.6 IEF) | `[risk_parity, p.5]` + AFP 2012 | 4/5 winner; 1st escape σ²_port cointegration |
| **8** | **039** | 🥇 STRONG | **76** | `vrp_basket_eq3_5_10_1m` (T-bill + 1/3 SPY+QQQ+IWM short put cs) | `[volatility_trading, p.218]` + Bondarenko 2014 + DMV 2009 | **Loop-record Sharpe (ndx 1.561) + DSR (ndx 0.006); 3/3 Sharpe edge ≥+0.10; 9/9 robust; G7 0.0000pp** |
| **8** | **031** | 🥇 STRONG | **76** | `vrp_and_v3p35_z2_h1_5_10_1m` (R-1 ∧ R-2 AND-VIX gate) | `[volatility_trading, p.217-218]` | 1st all-3 DSR<0.10 (0.054/0.070/0.050); ndx 7/7+DSR preserved |
| **8** | **026** | 🥇 STRONG | **76** | `vrp_primary_h1_5_10_1m` (T-bill + short SPY put cs) | `[volatility_trading, ch.3, p.41]` | 1st DSR PASS (ndx 0.038); 1st 7/7 gates; Sharpe Δ +0.38-0.45 |

*(iter 001 ~35/100; see `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iter in 6-field format; older entries compressed once file > 18 KB. Full detail recoverable from `iterations/NNN-*/`.

### 040 — 2026-04-25 — vrp-basket-vol-target (🥈 PROMISING, 69/100, 3/6 KILLS — Hypothesis FALSIFIED)
- **Hypothesis & Citations:** Moreira-Muir 2017 σ⁻²-target wrapper on iter 039 basket overlay (target_vol=0.05, lookback=21d, max_lev=2.0×). Inherits iter 039 cfg verbatim; ONLY new dim is dynamic notional scaling. `[volatility_trading, p.218]` + MM 2017 JoF 72(4) 1611-1644; `[systematic_trading, p.170-171]` (IDM≤2.5). 1 cfg, 3 datasets pre-committed.
- **Result:** Sharpe edu/spy/ndx **1.036/1.213/1.308** (Δ frozen +0.36/+0.31/+0.35; Δ039 **−0.104/−0.075/−0.253**), gates 6/6/6, DSR p=**0.168/0.112/0.070** (n=4305; Δ039 +0.094/+0.051/+0.064 ALL DEGRADE), CAGR 5.48/6.40/6.77%, MDD **9.04/8.94/6.42%** (edu −5.3pp), G7 max **0.0000pp**, robust **9/9**, winner 3/5; score 1:25 2:19 3:5 4:0 5:15 6:5 = **69**.
- **Lesson:** MM 2017 σ⁻² wrapper **ABSORBS** basket VRP harvest — short-vol mean scales POSITIVELY with IV (put-spread premium = f(IV)), so σ⁻² removes exposure when E[harvest] is largest → Sharpe ↓. Cleanest absorption test (NO equity stack, rules out σ²_port). VRP family 76 ceiling confirmed across 4 attacks (026/031/039/040). Closes any constant-window MM σ⁻² scaling + Kelly-fraction sizing. Open: ML meta-label on basket (RECOMMENDED iter 041), positive-CAGR base, cross-sectional factor timing. See `iterations/040-*/`.

### Iters 015-039 (compressed 1-line; full detail in `iterations/NNN-*/`)
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

Consumed/closed: 002-005/007/009-014/017/019-036/**037**/**038**/**039**/**040** (iter 040 MM-vol-target wrapper on iter 039 basket FAILED — 69/100, hypothesis falsified, 3/6 kills fired; Sharpe Δ039 −0.10/−0.07/−0.25, DSR worst-p degrades 0.075→0.168, score regression −7. Confirms VRP family 76 ceiling across 4 attacks: 026/031/039/040). Top-K #1 quintet 016/018/021/037/038 at 79; top-K #5 trio 026/031/039 at 76.

### Iter 041 candidates (VRP fam 76 across 4 attacks; static-stack 79 across 037+038)

- **ML meta-label on iter 039 basket (RECOMMENDED)**: binary open/skip classifier orthogonal to notional scaling. Features: VIX/VXN/RVX/VVIX/T10Y3M/EBP/realized-vol/skew. AFML ch.3 meta-labelling — changes SUPPORT of harvest distribution, not sizing (iter 040 closed sizing axis). ~3-4h. `[advances_fin_ml, ch.3]`.
- **Iter 039 basket overlay on iter 037 static-stack base**: replace T-bill collateral with 0.6 SPY + 0.45 IEF + 0.45 GLD. 3-leg basket has 3× smaller per-leg σ²_port absorption than iter 032's 1-leg; if sub-linear, may push 79→82-85. Risk: re-trigger iter 032 closure. ~2h.
- **Cross-sectional factor timing ≥10 factor ETFs** (out-of-family): MTUM/QUAL/USMV/SIZE/VLUE/SPLV; 12-1 momentum + value composite (AMP 2013). ≥10 assets exits iter 003's ≤20-asset floor. ~3h.
- **Regime-conditional WEIGHTS on iter 037 base**: VIX<20 → (0.70, 0.40, 0.40); VIX≥20 → (0.30, 0.55, 0.55). Modulates weights not leverage. Predicted 81-83 STRONG. ~2h.

DEAD-LETTER **F-FX FX carry**: DATA-BLOCKED (Tiingo FX span 2020+ only, 6y insufficient). Parked.

NOT recommended (032-040 confirm — predicted ≤+0.02 Sharpe / −0.005 DSR or strict regression): single-asset diversifier subst on 2/3-leg, weight perturbations of 0.6/0.45/0.45, σ⁻¹/σ⁻²/other-VIX/z-VIX/term-spread/MOVE/EBP gates on 037, 4-leg/5-leg basket, VIX gates on basket, asymmetric basket weights, DTE/strike sweeps, **any constant-window MM-style σ⁻² scaling on short-vol overlays (iter 040 closes), Kelly-fraction harvest sizing (predicted same absorption mechanism)**.

### Deeper backlog

- Plano C sleeve meta-allocation (GDE/AVUV/AVDE/AVEM/BTGD).
- Cross-sectional factor timing (≥10 factor ETFs, close to iter 003 floor).
- Carry + value composite (Asness-Moskowitz-Pedersen 2013) — orthogonal axes may break iter 024's saturation.
- VRP on broader index (RUT, EFA) — universe extension of iter 026.

---

## Structural dead-ends (1-line summaries; full text in `DEAD_ENDS.md`)

- **Iter 001-014**: daily EMA/SMA × LETF + any overlay; drawdown-stops primary; CAPE/EBP/VIX standalone; Clenow ATR/adj-slope on ≤20-asset homogeneous; single-asset σ⁻¹/σ⁻²; TSM 12-1/6-1/18-1 overlay on vol-managed blend; T10Y3M 21d/5d EMA haircut on iter 008; weekly/monthly cadence for vol-managed; meta-LR ρ+VIX_z; EBP credit; pre-val mandatory.
- **Iter 017/019-021**: 12-1 top-K=1 rotation on ≤3 regions; ρ stock-bond overlay (closes VIX/MOVE/realized-vol overlays by σ²_port cointegration analogy); options-on-equity-leg 5/10%OTM×21DTE either sign on vol-managed 2-leg stack (σ²_port absorbs Sharpe; MDD asymmetric short −1-3pp / long +3-6pp). Open: bare puts / ATM straddles / different DTE on STATIC base.
- **Iter 022-025**: TOM eq:bd modulator (σ²_port quadratic); TSM-PRIMARY ≤4-asset per-asset vol-target (turnover dominates √N); bond-curve carry-as-ALLOCATION 2-bond static (saturates iter 015 plateau); slow-EWMAC long-only 6-asset basket (long-only sacrifices 50% trend; 6 too narrow vs HOP 67). Open: cross-asset carry, ≥20-asset, long-SHORT EWMAC, carry+value.
- **VRP-harvester family ceiling 76 STRONG across 4 attacks: 026/031/039/040**: T-bill harvest delivers +0.38-0.45 Sharpe (026); linear-lev rf-dilutes (027); VIX-gates cap 76/71 (028/029/030/031); basket SPY+QQQ+IWM ties 76 (039); MM-vol-target wrapper on basket strictly regresses to 69 (040 — short-vol mean scales with IV → σ⁻² removes exposure when E[harvest] is largest → variance ↓, mean ↓ MORE → Sharpe ↓; cleanest test, no σ²_port explanation). CAGR floor 0/15 + edu DSR > 0.05 structural to T-bill collateral. Closes 4/5-leg, basket VIX gates, asymmetric weights, DTE/strike sweeps, **any constant-window MM σ⁻² scaling, predicted Kelly-fraction sizing**. Open break-76: ML meta-label on basket (RECOMMENDED iter 041), positive-CAGR base-layer, cross-sectional factor timing.
- **Static-stack family ceiling 79 STRONG across 037 (preserved-lev) + 038 (regime-gated-lev)**: 032/033/034/036 hit 72; 035 hit 77; 037 = 0.6/0.45/0.45 SPY+IEF+GLD @ 1.5× → Sharpe 0.98/1.15/1.17, DSR 0.222, MDD 33/25/32%; 038 = VIX-regime-gated 1.7↔1.0× (avg 1.46-1.49) → Sharpe 0.998/1.10/1.15, DSR 0.204 (best static-stack ever), MDD 25/22/29% (−4 to −8pp vs 037, two-axis: DSR-bound + MDD freely optimizable). MM 2017 +0.20-0.30 uplift doesn't replicate on diversified base. Closes weight perturbations, binary-VIX, σ⁻¹/σ⁻², z-VIX, term-spread/MOVE/EBP gates on 037. Open break-79 in-family: regime-conditional WEIGHTS not LEVERAGE; out-of-family: vol-target on basket.

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
