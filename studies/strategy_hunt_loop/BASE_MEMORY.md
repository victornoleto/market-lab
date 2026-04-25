---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 33
winners_found: 0
status: iterating
latest_iteration: "033-2026-04-25-0056"
cumulative_n_trials: 4288
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
| **1** | **016** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20` (60:40 static × MM vol-target) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | 4/5 winner; Sharpe +0.24-0.30; DSR p=0.226 sole fail |
| **1** | **018** | 🥇 STRONG | **79** | `ntsx_vm_vt15_L21_cap20_funded` (016 + r_Tbill drag) | `[risk_parity, p.80-84]` + NTSX prospectus | edges survive funding cost (−93 to −148 bps/yr); ties 016 |
| **1** | **021** | 🥇 STRONG | **79** | `ntsx_vm_..._scs5_10_1m` (016 + short OTM put-spread VRP) | `[volatility_trading, ch.3]` + Bondarenko 2014 | Sharpe-neutral but MDD −1 to −3pp; DSR p=0.217 record |
| 4 | 015 | 🥇 STRONG | 77 | `ntsx_synth_90_60_daily` (static 0.9 SPY + 0.6 IEF) | `[risk_parity, p.5]` + Asness-Frazzini-Pedersen 2012 | 4/5 winner; 1st mech to escape σ²_port cointegration |
| **5** | **031** | 🥇 STRONG | **76** | `vrp_and_v3p35_z2_h1_5_10_1m` (iter 026 + R-1 ∧ R-2 AND-composite VIX gate) | `[volatility_trading, p.217-218]` + Bondarenko 2014 §3 | **1st-ever all-3 DSR < 0.10** (edu 0.054 / spy 0.070 / ndx 0.050); composite vacuous on spy preserves iter 026 exactly; ndx 7/7 + DSR PASS preserved |
| **5** | **026** | 🥇 STRONG | **76** | `vrp_primary_h1_5_10_1m` (T-bill + short SPY 5/10% put credit spread) | `[volatility_trading, ch.3, p.41, p.217]` + Bondarenko 2014 | **1st DSR PASS ever** (ndx p=0.038); **1st 7/7 gates ever** (ndx); Sharpe Δ +0.38-0.45 cross-ds |

*(iter 001 ~35/100 approximate; back-fill in `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iteration in full 6-field format; older entries compressed to
3 lines (Result + Lesson + iter-dir pointer) once the file approaches
the 18 KB ceiling. Full hypothesis, citations, scope and score
breakdown for compressed iters are recoverable from
`iterations/NNN-*/hypothesis.md` + `verdict.json` + `final_report.md`.

### 033 — 2026-04-25 — ntsx-tlt-long-duration (🥈 PROMISING, 72/100, 1/6 KILLS — Kill C only)
- **Hypothesis:** swap iter 015 bond leg IEF (7-10y) → TLT (20-30y) at preserved 0.9/0.6 NTSX weights; pure single-mech duration tilt, no overlay, no timing. Test KMPV 2018 long-end term premium thesis.
- **Citations:** `[risk_parity, p.5, p.10-11, ch.1, ch.5]` + `[leverage_for_the_long_run, p.19-20]` + AFP 2012 + KMPV 2018 + Cochrane-Piazzesi 2005 + Ilmanen 2011 ch.6-7 + NTSX prospectus.
- **Scope:** 1 cfg × 3 ds → +3 trials (4285→4288). cfg `ntsx_synth_90_60_spy_tlt`. Datasets edu 2002-2026 (24y, +4y vs iter 015), spy 2009-2026, ndx 2010-2026.
- **Result:** Sharpe edu/spy/ndx 0.850/1.037/1.065 (Δ frozen +0.170/+0.137/+0.110 — 3/3 clear; **Δ015 +0.067/−0.007/+0.001 — Sharpe TIED on real data**), gates 5/6/6, DSR p=**0.313**/0.277/0.266 (n=4288, all 3 fail Kill C 0.20), MDD 42.60%/38.47%/**47.04%** ndx breach +6.93pp, robustness 9/9, winner=3/5; ρ(eq,bd) −0.31/−0.30/−0.23. G7 max 1.00pp 3/3.
- **Score breakdown:** 1:25/25 2:17/25 3:0/15 4:15/15 5:10/15 6:5/5 = **72** — 5 below iter 015 ceiling 77, score-tied with iter 032 from different mechanism path.
- **Lesson:** **Bond-duration is CAGR-MDD trade-off NOT Sharpe lever** on fixed-weight static stacks at preserved leg notional — variance scales with duration² (~7% IEF vol → ~14% TLT) and offsets ~+1.5%/y carry premium gain along Sharpe curve. iter 015 plateau at 77 resilient: iter 032 (composition) + iter 033 (duration) both score 72 from different paths. **DSR binding on static-stack family at n_trials ≥ 4288 with Sharpe ≤ 1.10**. Future winners: bond carry SLEEVE (zero-net-notional, preserves variance), FX/commodity carry (distribution-orthogonal), cross-asset VRP IWM, or non-static architecture Sharpe ≥ 1.30 cross-ds. See `iterations/033-2026-04-25-0056-ntsx-tlt-long-duration/`.

### Iters 015-032 (compressed 1-line; full detail in `iterations/NNN-*/`)

- **032** (🥈 72, 3/6 KILLS, layered composition) NTSX 0.9 SPY + 0.6 IEF + iter 031 AND-composite VRP on equity notional (`ntsx_vrp_and_v3p35_z2_eq09_bd06_h1`): Sharpe 0.81/1.04/1.08, DSR p=**0.502**/0.281/0.254, MDD 52.86%/35.63%/**44.38%** ndx breach; score 1:25 2:17 3:**0** 4:**15** 5:10 6:5 = **72**. corr_SPY=+0.97 — put-spread amplifies equity drawdowns. **NEW PRINCIPLE**: DSR penalty on composed strategy dominated by COMPOSITE distribution higher moments, NOT layer DSRs. Closes iter 015 + iter 026/031 overlay path.

- **031** (🥇 76, top-K #5 tied, ALL 6 KILLS CLEAN, **1st-ever all-3 DSR < 0.10**) AND-composite R-1∧R-2 on iter 026 base (`vrp_and_v3p35_z2_h1_5_10_1m`): Sharpe 1.19/1.28/1.33, gates 6/6/7, DSR p=0.054/0.070/0.050 (n=4284, 3rd sub-0.05 ndx, 1st all-3<0.10); ties iter 026 ceiling because rubric awards worst-p bucket not distribution tightness. AND-intersection fires 4× across 60y (Sep-Oct 2008 + Mar-2020 + 2011-08-12); vacuous on spy by construction. CLOSURE: 5 iters on iter 026 base capped at 76; criterion-4 CAGR floor 0/15 structural to harvest_notional=1.0 — gain requires CAGR mechanism or R-3 term-structure.

- **030** (🥈 71, Kill A+B) Z-score gate (`z_window=60, z_threshold=2.0`) on iter 026: spy 1st-ever 7/7 + DSR p=0.0345 PASS, but edu Kill B (z misses sustained Q4-2008) and ndx Kill A 2.6× (z over-filters tech mini-spikes); 3 successive single-axis iters (028/029/030) all converge at 71, each w/ sub-0.05 DSR on different dataset.

- **029** (🥈 71, Kill A 2bp) Level + 3-day persistence on iter 028: edu DSR record p=0.0251 (best edu ever), spy partial recovery (+0.048 vs iter 028), ndx unchanged (already all-clustered). Worst-p 0.100 missed 10-pt threshold by 0.0003. Closes specific cfg; structural finding 3 datasets have qualitatively different regime structures.
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

Consumed/closed: 002/003/004/005/007/009/010/011/012/013/014/017/019/020/021/022/023/024/025/026/027/028/029/030/031/032/**033** (iter 033 PROMISING 72 — bond-duration tilt is CAGR-MDD trade-off NOT Sharpe lever; iter 015 plateau at 77 resilient to bond-axis variations; both iter 032 composition and iter 033 duration substitution score 72 from different mechanism paths). Top-K #1 still iter 016/018/021 triple-tied at 79.

### Iter 034 candidates (post-iter-033 — non-static-stack OR variance-neutral CAGR mechanism)

- **B-Sleeve Bond carry SLEEVE (STRONGEST)**. Zero-net-notional duration spread on iter 015 base: `0.9 SPY + (0.6 - α) IEF + α TLT` for α ∈ {0.1, 0.2, 0.3}. Spread vol (TLT-IEF) is much smaller than TLT vol alone (~6-8% vs ~14%); preserves iter 015 Sharpe AND adds carry premium. Directly addresses iter 033's variance offset. `[risk_parity, ch.5]` + KMPV 2018.
- **C-VRP Cross-asset VRP IWM**. iter 015 base + iter 031 AND-composite put-spread on **IWM** (Russell 2000) instead of SPY. Small-cap stress decorrelated from large-cap (2022 IWM −36% vs SPY −25%) — composite corr_SPY drops below iter 032's 0.97. `[volatility_trading, p.218]` + AMP 2013.
- **F-FX FX carry overlay** on iter 015 base. Long AUDUSD short USDJPY — most distribution-orthogonal to equity beta. FX carry has its OWN crash pattern. Lustig-Verdelhan 2007; Burnside 2011.
- **Non-static architecture** Sharpe ≥ 1.30 cross-ds: only path to clear DSR at n_trials ≥ 4288 per iter 033 lesson. Open: ML meta-label, regime-aware, cross-sectional factor timing.

NOT recommended (per iter 032+033): bond-axis variations on iter 015 stack — plateau 77 resilient. TLT at higher weight (worsens MDD); iter 032/033 param sweeps (inflates PBO).

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
- **iter 032/033 (PROMISING 72 from different paths)**: layered composition (`ntsx_vrp_and_v3p35_z2_eq09_bd06_h1`) and bond-duration substitution (`ntsx_synth_90_60_spy_tlt`) both reach 72 with identical breakdown (1:25 2:17 3:0 4:15 5:10 6:5) — iter 015 plateau at 77 resilient. iter 032: composite higher-moment penalty (corr_SPY=+0.97, DSR worst-p 0.50). iter 033: variance scales with duration² offsetting carry along Sharpe curve (bond vol 7%→14%, Sharpe Δ vs iter 015 ≈ 0). **DSR binding on static-stack family at n_trials ≥ 4288 with Sharpe ≤ 1.10**. Closes (a) iter 015 + iter 026/031 overlay path (any harvest_notional), (b) bond-axis substitution at preserved 0.9/0.6 weights. Open: bond carry SLEEVE (zero-net-notional duration spread), FX/commodity carry (distribution-orthogonal), cross-asset VRP IWM/EFA, non-static architecture Sharpe ≥ 1.30 cross-ds.

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
