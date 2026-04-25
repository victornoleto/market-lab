---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 37
winners_found: 0
status: iterating
latest_iteration: "037-2026-04-25-0224"
cumulative_n_trials: 4300
---

# Strategy Hunt Loop — BASE MEMORY

**Read this file FIRST in every iteration.** Your conversation history
is empty — this file + on-disk artifacts are your only continuity.
Process rules + iteration template + how to update this file at end of
iteration: see `PROMPT.md`. Available infrastructure (simulators, data
loaders, validation, metrics, signals, data cache): see
`INFRASTRUCTURE.md`.

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

None yet. When found, append:

```yaml
winner:
  iteration: NNN
  hypothesis: "<one-line hypothesis>"
  config: "<cfg_id>"
  score: 100  # 90+ AND winner_conditions_met=True
  datasets_passing:
    - spy_real: {sharpe: X, cagr: Y%, mdd: Z%, gates: N/7}
    - ndx_real: {...}
    - educational: {...}
  citation_primary: "[book.slug, p.X]"
  iteration_dir: "iterations/NNN-YYYY-MM-DD-HHMM-slug/"
```

---

## Top-K strategies ranked (best of all iterations, by score)

| rank | iter | tier | score | strategy slug | primary citation | headline |
|---|---|---|---|---|---|---|
| **1** | **037** | 🥇 STRONG | **79** | `ntsx_3leg_preserved_60_45_45_spy_ief_gld` (0.6 SPY+0.45 IEF+0.45 GLD, 1.5×) | `[risk_parity, ch.5]` + AMP 2013 | 1st plain static-stack at 79; **breaks 77 ceiling**; 4/5 winner; Sharpe +0.30/+0.25/+0.22; DSR 0.222 sole fail |
| **1** | **016** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20` (60:40 × MM vol-target) | `[risk_parity, p.10-11]` + MM 2017 | 4/5 winner; Sharpe +0.24-0.30; DSR 0.226 sole fail |
| **1** | **018** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20_funded` (016 + r_Tbill drag) | `[risk_parity, p.80-84]` | edges survive funding cost (−93 to −148 bps/yr); ties 016 |
| **1** | **021** | 🥇 STRONG | **79** | `ntsx_vm_..._scs5_10_1m` (016 + short put-spread VRP) | `[volatility_trading, ch.3]` | Sharpe-neutral; MDD −1 to −3pp; DSR p=0.217 record |
| **5** | **035** | 🥇 STRONG | **77** | `static_stack_90_60_spy_gld` (static 0.9 SPY + 0.6 GLD) | `[risk_parity, ch.5]` + Erb-Harvey 2006 + AMP 2013 | TIES 015 ceiling from gold-not-bond axis; Δ015 +0.094/+0.026/+0.040 Sharpe; best static DSR ever (0.344) |
| 5 | 015 | 🥇 STRONG | 77 | `ntsx_synth_90_60_daily` (static 0.9 SPY + 0.6 IEF) | `[risk_parity, p.5]` + AFP 2012 | 4/5 winner; 1st escape σ²_port cointegration |
| **7** | **031** | 🥇 STRONG | **76** | `vrp_and_v3p35_z2_h1_5_10_1m` (R-1 ∧ R-2 AND-VIX gate) | `[volatility_trading, p.217-218]` | 1st all-3 DSR<0.10 (0.054/0.070/0.050); ndx 7/7+DSR preserved |
| **7** | **026** | 🥇 STRONG | **76** | `vrp_primary_h1_5_10_1m` (T-bill + short SPY put cs) | `[volatility_trading, ch.3, p.41]` | 1st DSR PASS (ndx 0.038); 1st 7/7 gates; Sharpe Δ +0.38-0.45 |

*(iter 001 ~35/100 approximate; back-fill in `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iteration in full 6-field format; older entries compressed to
3 lines (Result + Lesson + iter-dir pointer) once the file approaches
the 18 KB ceiling. Full hypothesis, citations, scope and score
breakdown for compressed iters are recoverable from
`iterations/NNN-*/hypothesis.md` + `verdict.json` + `final_report.md`.

### 037 — 2026-04-25 — ntsx-3leg-preserved-lev (🥇 STRONG, 79/100, 1/7 KILLS — Kill C only)
- **Hypothesis:** Redistribute weights from iter 036's 0.9/0.6/0.3 (1.8×) to **0.6 SPY + 0.45 IEF + 0.45 GLD = 1.5× lev** — preserves iter 015 leverage budget while adding 3rd leg via 33% equity-cut.
- **Citations:** `[risk_parity, ch.5]` + `[risk_parity, p.5, p.10-11, ch.1]` (AFP 2012) + AMP 2013 (JF 68(3) DOI 10.1111/jofi.12021) + `[leverage_for_the_long_run, p.19-20]` + Erb-Harvey 2006 + KMPV 2018 + Ilmanen 2011.
- **Scope:** 1 cfg, 3 datasets (edu SPY+IEF+GLD 21y, spy_real 17y, ndx_real 16y); GLD-aligned windows from iter 035/036.
- **Result:** Sharpe edu/spy/ndx **0.983/1.154/1.174** (Δ frozen **+0.303/+0.254/+0.219** — largest static-stack edge ever; Δ015 +0.199/+0.110/+0.110 ALL 3; Δ036 +0.062/+0.007/+0.020 strict-dominates 036), gates 6/6/6, DSR p=**0.222**/0.144/0.146 (n=4300, beats iter 036's 0.311 by −29% — Kill C just above 0.20), CAGR 14.16/15.53/17.76% (3/3 clear), MDD **33.33/25.24/32.28%** (**1st plain static-stack with 3/3 MDD clean**, margins 22/8/3pp), G7 max 0.134pp, winner 4/5 (only DSR), robust 9/9; **score 1:25 2:19 3:0 4:15 5:15 6:5 = 79**.
- **Lesson:** **Static-stack 77 ceiling BROKEN at 79 STRONG** (ties top-K #1 016/018/021) — first plain static-stack at 79 without overlays. AMP 2013 orthogonality DOES survive 33% equity-cut; diversifier-sleeve variance reduction (0.45/0.45 IEF/GLD vs 0.6 single) outweighs equity drag. **Static-stack now DSR-bound at 79** (not leverage-bound) — clearing DSR p<0.05 needs Sharpe ~1.30+ cross-ds, mechanically lev>2.0× MDD breach OR non-static. See `iterations/037-*/`.

### Iters 015-036 (compressed 1-line; full detail in `iterations/NNN-*/`)

- **036** (🥈 72, 1/6 KILLS — C only, 3-leg additive @ 1.8×) `ntsx_3leg_add_90_60_30_spy_ief_gld`: Sharpe 0.921/1.147/1.154 (Δ015 +0.138/+0.103/+0.090; Δ035 +0.044/+0.077/+0.051 — 1st empirical proof 3rd leg adds Sharpe), DSR 0.311/0.151/0.164 (n=4297), MDD 42.83/32.41/**41.53%** ndx breach +1.41pp; G7 max 0.142pp; score 1:25 2:17 3:0 4:15 5:10 6:5 = **72**. PRINCIPLE: 3-leg @ 1.8× extracts +0.05 Sharpe but +0.30 lev breaks ndx MDD → net 72. Subsumed by iter 037 (preserved-lev variant strict-dominates on Sharpe + MDD + DSR).

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

Consumed/closed: 002-005/007/009-014/017/019-036/**037** (iter 037 STRONG 79 — 0.6 SPY+0.45 IEF+0.45 GLD @ 1.5× **broke 77 ceiling**; 4/5 winner conds, only DSR fails 0.222; first plain static-stack at 79 ties top-K #1; first 3-leg with 3/3 MDD clean. Corrected characterization: **static-stack DSR-bound at 79 absolute** at preserved 1.5× lev). Top-K #1 quartet 016/018/021/037 at 79.

### Iter 038 candidates (static-stack ceiling re-characterized as DSR-bound at 79; pivot to non-static OR VRP basket; 4-leg static = marginal)

- **HMM regime-aware lev scaling on iter 037 base (RECOMMENDED)**: keep 0.6/0.45/0.45 weights, lever 1.7× in low-vol regime (VIX < 20 or z < 0) and 1.0× in high-vol regime. **Highest-yield remaining test** — direct DSR-bottleneck attack via regime-conditional lev. Predicted: Sharpe ~1.20-1.30 + ndx MDD ≤ 35% → DSR worst-p clears 0.10 (10pts on criterion 3) and possibly 0.05 (15pts → 89-94 score = STRONG/WINNER candidate). `[advances_fin_ml, ch.17-18]`. ~2-4h.
- **C-VRP basket extension**: iter 026 architecture (T-bill + short equity put credit spread) on basket SPY+QQQ+IWM at 1/3 notional each. Iter 026 ndx unique 7/7+DSR PASS; basket may break SPY-edu DSR bottleneck while preserving ndx PASS. ~60-90 min. `[volatility_trading, p.218]` + AMP 2013.
- **4-leg lev-preserved static**: e.g., `0.45 SPY + 0.30 IEF + 0.30 GLD + 0.45 DBC` (commodity broad) or VNQ — at total lev 1.50×. Tests if 79 ceiling extends to 4 legs. Predicted marginal (035→036 = +0.05; 036→037 = +0.06; next ~+0.02-0.03). Likely 79-81, NOT a winner break. ~30 min. `[risk_parity, ch.5]` + AMP 2013.
- **Non-static (other)** (Sharpe ≥ 1.30): ML meta-label `[advances_fin_ml, ch.3]`, CS factor timing 5+ ETFs. Credible DSR PASS path at n ≥ 4300. ~2-4h.

DEAD-LETTER **F-FX FX carry**: **DATA-BLOCKED** (audusd/usdjpy span 2020+ only, 6y insufficient). Parked.

NOT recommended (032/033/034/035/036/**037** confirm): single-asset diversifier substitutions on 2-leg, 3-leg additive at >1.5× lev, AND minor weight perturbations of iter 037's 0.6/0.45/0.45 (e.g., 0.5/0.5/0.5 or 0.7/0.4/0.4 will land within ±2pts of 79). Architecture characterized; further weight sweeps within static-stack family = noise. Includes DBC/GSG/USO single-leg subst, VNQ single-leg subst, EMB, ZROZ/EDV.

### Deeper backlog

- Plano C sleeve meta-allocation (GDE/AVUV/AVDE/AVEM/BTGD).
- Cross-sectional factor timing (≥10 factor ETFs, close to iter 003 floor).
- Carry + value composite (Asness-Moskowitz-Pedersen 2013) — orthogonal axes may break iter 024's saturation.
- VRP on broader index (RUT, EFA) — universe extension of iter 026.

---

## Structural dead-ends (1-line summaries; full text in `DEAD_ENDS.md`)

- Iter 001-014 family (compressed): daily EMA/SMA × LETF + any overlay; drawdown-stops primary; CAPE/EBP/VIX standalone single-indicator; Clenow ATR on sector ETFs top-K≤5; Clenow adj-slope × R² on ≤20-asset homogeneous baskets; single-asset σ⁻¹/σ⁻² SPY/QQQ; TSM 12-1/6-1/18-1 overlay on vol-managed blend; T10Y3M 21d/5d EMA haircut on iter 008; weekly/monthly rebalance for vol-managed blend; meta-LR ρ+VIX_z; EBP credit overlay; pre-val screen mandatory.
- Iter 017/019/020/021 (compressed): 12-1 top-K=1 rotation on ≤3 regions; ρ stock-bond overlay (ρ in σ²_port cross-term cointegrates → closes VIX/MOVE/realized-vol overlays by analogy); options-on-equity-leg 5/10%OTM×21DTE either sign on vol-managed 2-leg stack — σ²_port absorbs; Sharpe tied; MDD asymmetric (short −1-3pp / long +3-6pp). Does NOT close bare puts/ATM straddles/different DTE on STATIC base (see iter 032).
- Iter 022-025 (compressed): calendar TOM eq:bd modulator on vol-managed stack (σ²_port quadratic in w_eq); TSM-PRIMARY ≤4-asset per-asset vol-target (turnover dominates sqrt(N) diversification); bond-curve carry-as-ALLOCATION 2-bond static stack (saturates iter 015 plateau); slow-EWMAC long-only 6-asset basket (long-only sacrifices 50% trend premium; 6 too narrow vs HOP 67). Open: cross-asset carry, ≥20-asset, long-SHORT EWMAC, EWMAC+Carry, VRP-primary, carry+value.
- **Tightening iter 026**: vol-target wrapper ABSORBS short-vol overlays (Sharpe-neutral); stand-alone harvest on T-bill collateral delivers +0.38-0.45 Sharpe alpha 3/3 (STRONG 76).
- **Tightening iter 027**: linear leverage on T-bill+harvest is NOT total-Sharpe-neutral (rf-bonus dilutes); N=3.5 total Sharpe→overlay_sharpe; closes leverage-only path.
- **Tightening iter 028-031** (single-axis VIX-gate family on iter 026 base): constant `VIX<35` (028 lifts edu Kill A 2/3), `level+3d-persistence` (029 ties 71 +0.0003 of 10pt threshold), `z(60,2)` regime-relative (030 1st spy 7/7+DSR PASS but Kill A+B), AND-composite R-1∧R-2 (031 ties 76 ceiling, 1st all-3 DSR<0.10 but criterion-4 CAGR 0/15 structural). All 5 iters capped at 76/71 by harvest_notional=1.0 T-bill architecture. Single-axis family CLOSED. Open: R-3 VXV term-structure, multi-asset, non-VIX gates.
- **iter 032-036 (superseded by 037)**: 032/033/034/036 hit 72; 035 hit 77; iter 037 strict-dominates 036 on Sharpe+MDD+DSR. Closed: single-asset diversifier substitutions on 2-leg + 3-leg additive at >1.5× lev.
- **iter 037 (static-stack DSR-bound at 79 absolute ceiling)**: 0.6 SPY + 0.45 IEF + 0.45 GLD @ 1.5× → Sharpe 0.98/1.15/1.17 (largest static-stack edge ever +0.30/+0.25/+0.22), 3/3 MDD clean (1st plain static-stack), DSR worst-p 0.222 (beats 036's 0.311 by −29%). Score 79 STRONG ties top-K #1 016/018/021. **Breaks 77 ceiling.** 4/5 winner conds (DSR fails). Closes: minor weight perturbations of 0.6/0.45/0.45 (±2pts of 79). **Static-stack now DSR-bound at 79** — clearing p<0.05 needs Sharpe ~1.30+ (lev>2.0× MDD breach OR non-static). Open: HMM regime on iter 037 base, cross-asset VRP basket, 4-leg lev-preserved (marginal).

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
