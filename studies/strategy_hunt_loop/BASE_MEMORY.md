---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 36
winners_found: 0
status: iterating
latest_iteration: "036-2026-04-25-0206"
cumulative_n_trials: 4297
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
| **1** | **016** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20` (60:40 × MM vol-target) | `[risk_parity, p.10-11]` + MM 2017 | 4/5 winner; Sharpe +0.24-0.30; DSR 0.226 sole fail |
| **1** | **018** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20_funded` (016 + r_Tbill drag) | `[risk_parity, p.80-84]` | edges survive funding cost (−93 to −148 bps/yr); ties 016 |
| **1** | **021** | 🥇 STRONG | **79** | `ntsx_vm_..._scs5_10_1m` (016 + short put-spread VRP) | `[volatility_trading, ch.3]` | Sharpe-neutral; MDD −1 to −3pp; DSR p=0.217 record |
| **4** | **035** | 🥇 STRONG | **77** | `static_stack_90_60_spy_gld` (static 0.9 SPY + 0.6 GLD) | `[risk_parity, ch.5]` + Erb-Harvey 2006 + AMP 2013 | TIES 015 ceiling from gold-not-bond axis; Δ015 +0.094/+0.026/+0.040 Sharpe; best static DSR ever (0.344) |
| 4 | 015 | 🥇 STRONG | 77 | `ntsx_synth_90_60_daily` (static 0.9 SPY + 0.6 IEF) | `[risk_parity, p.5]` + AFP 2012 | 4/5 winner; 1st escape σ²_port cointegration |
| **6** | **031** | 🥇 STRONG | **76** | `vrp_and_v3p35_z2_h1_5_10_1m` (R-1 ∧ R-2 AND-VIX gate) | `[volatility_trading, p.217-218]` | 1st all-3 DSR<0.10 (0.054/0.070/0.050); ndx 7/7+DSR preserved |
| **6** | **026** | 🥇 STRONG | **76** | `vrp_primary_h1_5_10_1m` (T-bill + short SPY put cs) | `[volatility_trading, ch.3, p.41]` | 1st DSR PASS (ndx 0.038); 1st 7/7 gates; Sharpe Δ +0.38-0.45 |

*(iter 001 ~35/100 approximate; back-fill in `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iteration in full 6-field format; older entries compressed to
3 lines (Result + Lesson + iter-dir pointer) once the file approaches
the 18 KB ceiling. Full hypothesis, citations, scope and score
breakdown for compressed iters are recoverable from
`iterations/NNN-*/hypothesis.md` + `verdict.json` + `final_report.md`.

### 036 — 2026-04-25 — ntsx-3leg-additive-spy-ief-gld (🥈 PROMISING, 72/100, 1/6 KILLS — Kill C only)
- **Result:** Sharpe edu/spy/ndx 0.921/1.147/1.154 (Δ frozen +0.241/+0.247/+0.199 ALL 3 ≥ +0.10; Δ015 +0.138/+0.103/+0.090; **Δ035 +0.044/+0.077/+0.051 — 1st empirical proof 3rd leg adds Sharpe**), gates 5/6/6, DSR p=**0.311**/0.151/0.164 (n=4297, **lowest static-stack worst-p ever** vs 015's 0.548, 035's 0.344 — Kill C); MDD 42.83/32.41/**41.53%** (ndx breach +1.41pp), winner=4/5; G7 max 0.142pp; robust 9/9; score 1:25 2:17 3:0 4:15 **5:10** 6:5 = **72**.
- **Lesson:** **77 ceiling TRIPLE-CONFIRMED**: asset-agnostic (035) + 2-leg-saturated (015) + leverage-bound (036). 3-leg additive @ 1.8× extracts +0.05 Sharpe (AMP 2013 orthogonality real) BUT +0.30 lev breaks ndx MDD → net 72. **Static-stack ≤1.8× exhausted at 77.** Open: lev-preserved 3-leg (0.6/0.45/0.45 = 1.5×), HMM regime, VRP basket. See `iterations/036-2026-04-25-0206-ntsx-3leg-additive-spy-ief-gld/`.

### Iters 015-035 (compressed 1-line; full detail in `iterations/NNN-*/`)

- **035** (🥇 77, 1/6 KILLS — Kill C only, GLD substitution) `static_stack_90_60_spy_gld`: Sharpe 0.877/1.070/1.103 (Δ015 +0.094/+0.026/+0.040 POSITIVE 3/3), DSR 0.344/0.236/0.219 (n=4294, edu −0.205 absolute vs iter 015), MDD 48.67%/32.44%/36.95% 3/3 clean; G7 max 0.188pp; score 1:25 2:17 3:0 4:15 5:15 6:5 = **77**. PRINCIPLE: 77 ceiling asset-class-agnostic; gold and IEF extract same Sharpe on 90/60 1.5× base → iter 015's edge was DIVERSIFICATION-driven not bond-carry. Closes single-asset diversifier substitution.

- **034** (🥈 72, 1/6 KILLS — C only, 3-leg bond-carry sleeve) zero-net-notional duration spread on iter 015 (`ntsx_synth_90_spy_40_ief_20_tlt`): Sharpe 0.795/1.058/1.075 (Δ015 +0.011/+0.014/+0.012 POSITIVE 3/3 but small), DSR 0.529/0.250/0.253 (n=4291, all 3 fail Kill C), MDD ndx 42.11% breach +1.99pp; G7 max 0.087pp; score 1:25 2:17 3:0 4:15 5:10 6:5 = **72**. PRINCIPLE: third bond-axis path tying iter 032/033 at 72 — bond-axis CLOSED. iter 035 GLD substitution result re-classifies this lesson: 77 ceiling is architecture-bound, not bond-specific.

- **033** (🥈 72, 1/6 KILLS — C only, duration substitution) full IEF→TLT swap at 0.9/0.6 (`ntsx_synth_90_60_spy_tlt`): Sharpe 0.85/1.04/1.06, DSR 0.31/0.28/0.27, MDD 43%/38%/**47%** ndx breach; score 1:25 2:17 3:0 4:15 5:10 6:5 = **72**. Δ015 +0.067/−0.007/+0.001 — Sharpe TIED real data (edu uplift = 4y extra window). PRINCIPLE: bond-duration is CAGR-MDD trade-off NOT Sharpe lever (variance scales with duration², cancels carry premium).

- **032** (🥈 72, 3/6 KILLS, layered composition) iter 015 + iter 031 AND-VRP on equity (`ntsx_vrp_and_v3p35_z2_eq09_bd06_h1`): Sharpe 0.81/1.04/1.08, DSR 0.50/0.28/0.25, MDD 53%/36%/**44%** ndx breach; corr_SPY=+0.97 (put-spread amplifies equity DD). PRINCIPLE: DSR penalty on composed strategy dominated by COMPOSITE higher moments, NOT layer DSRs. Closes iter 015 + iter 026/031 overlay path.

- **031** (🥇 76, top-K #5 tied, ALL 6 CLEAN, 1st all-3 DSR<0.10) AND-composite R-1∧R-2 on iter 026 (`vrp_and_v3p35_z2_h1_5_10_1m`): Sharpe 1.19/1.28/1.33, gates 6/6/7, DSR 0.054/0.070/0.050; AND-intersection fires 4× across 60y, vacuous on spy. Ties iter 026 (rubric awards worst-p bucket). CLOSURE: 5 iters on iter 026 base capped at 76; CAGR floor 0/15 structural to harvest_notional=1.0.

- **030** (🥈 71, Kill A+B) Z-score gate (z_60d, 2σ) on iter 026: spy 1st 7/7 + DSR 0.0345 PASS, but edu Kill B + ndx Kill A 2.6×; 3 single-axis iters (028/029/030) converge at 71.

- **029** (🥈 71, Kill A 2bp) Level + 3d persistence on iter 028: edu DSR record 0.0251, ndx unchanged. Worst-p 0.100 missed 10pt threshold by 0.0003.
- **028** (🥈 71, Kill A) Constant `VIX<35` filter on iter 026: edu 1st-ever 7/7 + DSR p=0.029 record, but spy/ndx regress (transient spikes); closes constant-threshold path, opens regime-aware gates.
- **027** (🥈 74, Kill A) Levered (N=3.5) iter 026: CAGR floor 3/3 ✓ but Sharpe regress 3/3 + DSR collapse; rf-bonus diluted by leverage; iter 026 edge is N=1-specific.
- **026** (🥇 76, top-K #5) Stand-alone VRP harvest on T-bill (short SPY 5/10% put credit spread): Sharpe 1.13/1.28/1.37, ndx 1st 7/7 + 1st DSR PASS ever (p=0.038); strongest cross-ds Sharpe edge in loop.
- **025** (📉 39) Slow-EWMAC FDM=1.10 buffer 10% on 6-asset basket: long-only sacrifices ~50% trend premium; closes long-only ≤6-asset.
- **024** (🥈 72) Bond-curve carry-as-ALLOCATION (T10Y3M ramp) in static stack: 3/3 Sharpe edge but DSR worst 0.586 binds; saturates iter 015 plateau.
- **023** (📉 28) TSM-primary 3-ETF (SPY+TLT+GLD) per-asset vol-target: turnover ~35/yr/leg dominates sqrt(3) diversification; HOP 2017 needs 67 markets.
- **022** (🥉 54) TOM eq:bd modulator: σ²_port quadratic in w_eq absorbs calendar premium.
- **021** (🥇 79, top-K #1) Short put-credit-spread VRP overlay on iter 016: uniform MDD improvement −1.95/−1.01/−2.85pp, DSR p=0.217.
- **020** (🥇 79) Monthly put-spread tail hedge: Δ016 −0.08/−0.08/−0.04; long-gamma overlays REDUNDANT with vol-target.
- **019** (❌ 0) HMM stock-bond ρ: pre-val rejects 3/3; closes ρ/VIX/MOVE/realized-vol overlays.
- **018** (🥇 79, top-K #1) Funding-cost iter 016 replay: each 100bps drag ≈ −0.07 Sharpe.
- **017** (🥉 52) 12-1 regional rotation N=3: period US Sharpe dominance → closes top-K∈{1,2} on ≤3 regions.
- **016** (🥇 79, top-K #1) Static 60:40 × Moreira-Muir vol-target: Sharpe 0.98/1.14/1.19; fixed × vol-target ADDITIVE.
- **015** (🥇 77) Static synthetic NTSX 90/60 SPY+IEF: 1st iter clearing +0.10 cross-ds; static breaks σ²_port cointegration.

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

Consumed/closed: 002-005/007/009-014/017/019-035/**036** (iter 036 PROMISING 72 — 3-leg additive SPY+IEF+GLD at 1.8× lev demonstrated Sharpe IS extracted by 3rd leg (+0.05 over iter 035 across all 3 ds, 1st empirical proof) but +0.30 leverage breaks ndx MDD ceiling, netting 72. **77 ceiling NOW TRIPLE-CONFIRMED**: asset-class-agnostic (035) + 2-leg-saturated (015) + leverage-bound (036). Static-stack family within ≤1.8× exhausted at 77 absolute. Closes 3-leg additive at >1.5× lev). Top-K #1 still iter 016/018/021 triple-tied at 79.

### Iter 037 candidates (static-stack ≤1.8× exhausted at 77; pivot to lev-preserved 3-leg, non-static, OR cross-asset VRP)

- **G-3LEG-PRESERVED lev-preserved 3-leg (RECOMMENDED)**: `0.6 SPY + 0.45 IEF + 0.45 GLD = 1.5× lev` — 3 orthogonal diversifiers AT iter 015 lev. Pre-committed: Sharpe ≥ +0.10 cross-ds AND ndx MDD ≤ 40% = 1st 80+ break; <+0.10 on ≥2 ds closes static-stack at ≤1.5×. ~30 min, minimal cfg change. **Single most informative remaining cheap test.** `[risk_parity, ch.5]` + AMP 2013.
- **HMM regime-aware lev scaling on iter 015**: VIX level/z 2-state HMM; lev 1.5× low-vol / 1.0× high-vol. Predicted: breaks 77 on MDD axis. `[advances_fin_ml, ch.17-18]`. ~2-4h.
- **C-VRP IWM**: iter 026 arch on IWM (Russell 2000) put cs. Iter 026 ndx 7/7+DSR PASS → IWM may break SPY edu DSR bottleneck. ~60-90 min. `[volatility_trading, p.218]` + AMP 2013.
- **Non-static (other)** (Sharpe ≥ 1.30): ML meta-label `[advances_fin_ml, ch.3]`, CS factor timing 5+ ETFs. Only credible DSR PASS path at n ≥ 4297. ~2-4h.

DEAD-LETTER **F-FX FX carry**: **DATA-BLOCKED** (audusd/usdjpy span 2020+ only, 6y insufficient). Parked.

NOT recommended (032/033/034/035/**036** confirm): single-asset diversifier substitutions on 2-leg AND 3-leg additive at >1.5× — IEF/GLD substs (035) AND 3-leg @ 1.8× (036) bounded at 72-77. Includes DBC/GSG/USO, VNQ, EMB, ZROZ/EDV.

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
- **iter 032/033/034/035/036 (static-stack ceiling 72-77, 5 paths — TRIPLE-CONFIRMED)**: 032/033/034/036 hit 72 (1:25 2:17 3:0 4:15 **5:10** 6:5); **035 GLD subst hits 77** (5:15) — only diff: ndx MDD clean. **77 ceiling is simultaneously asset-agnostic (035), 2-leg-saturated (015), AND leverage-bound (036, 3-leg @ 1.8× breaks ndx MDD)**. 036 NULL on Kill A proved 3rd leg DOES add +0.05 Sharpe (AMP 2013 orthogonality empirical), but +0.30 lev breaks tail. Best DSR ever = **036 edu p=0.311** (−0.237 vs 015). **Closes all single-asset diversifier substitutions on 2-leg AND 3-leg additive at >1.5× lev**. Open: lev-preserved 3-leg (0.6/0.45/0.45 = 1.5×), HMM regime, cross-asset VRP basket.

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
