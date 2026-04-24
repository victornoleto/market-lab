---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 23
winners_found: 0
status: iterating
latest_iteration: "023-2026-04-24-2007"
cumulative_n_trials: 4276
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
| **1** | **016** | 🥇 **STRONG** | **79** | `ntsx_vm_vt15_L21_cap20` (0.6/0.4 static ratio × Moreira-Muir vol-target) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | 4/5 winner; Sharpe +0.24-0.30; DSR sole fail (p=0.226); funding-cost validated by iter 018; MDD-improved variant in iter 021 |
| **1** | **018** | 🥇 **STRONG** | **79** | `ntsx_vm_vt15_L21_cap20_funded` (iter 016 + r_Tbill SHV drag) | `[risk_parity, p.80-84]` + NTSX prospectus | edges survive funding cost (−93 to −148 bps/yr); 4/5 winner; ties iter 016 |
| **1** | **021** | 🥇 **STRONG** | **79** | `ntsx_vm_vt15_L21_cap20_scs5_10_1m` (iter 016 + short 5/10% OTM put-credit-spread VRP harvest) | `[volatility_trading, ch.3]` + Bondarenko 2014 | ties iter 016 at score; Sharpe-neutral (Δ +0.01/−0.00/−0.04) but **MDD uniformly improves −1 to −3pp**; VRP realises +2.9-4.1%/yr as predicted; DSR p=0.217 lowest ever (still sub-tier) |
| 4 | 015 | 🥇 STRONG | 77 | `ntsx_synth_90_60_daily` (static 0.9 SPY + 0.6 IEF) | `[risk_parity, p.5]` + Asness-Frazzini-Pedersen 2012 | 4/5 winner; first mech to escape σ²_port cointegration |
| 5 | 008 | 🥈 PROMISING | 74 | `vt15_L21_cap20` (2-leg SPY+TLT vol-mgmt) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | 4/5 winner; vol-managed reference baseline |

*(iter 001 ~35/100 approximate; back-fill in `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iteration in full 6-field format; older entries compressed to
3 lines (Result + Lesson + iter-dir pointer) once the file approaches
the 18 KB ceiling. Full hypothesis, citations, scope and score
breakdown for compressed iters are recoverable from
`iterations/NNN-*/hypothesis.md` + `verdict.json` + `final_report.md`.

### 023 — 2026-04-24 — Time-series trend 3-asset SPY+TLT+GLD per-asset vol-target (📉 NEAR_FAIL 28/100, biggest hunt-loop regression)
- **Result:** Sharpe 0.554/0.552/0.610 (Δ frozen −0.126/−0.348/−0.345, 0/3 beat bench; **Δ iter 016 −0.427/−0.588/−0.576 uniform — largest ever**), CAGR 8/8/9% floor fails 3/3, MDD 48/48/36% spy +14.5pp, gates 5/5/4 (G2 DSR fail p=0.89/0.93/0.90; G6 boot CI neg 3/3; G3 WF fail ndx 4/8), DSR worst-ever p=0.926, n_trials 4273→4276, winner 0/5; cap_hit 67-75% (Kill C clear), short fracs 9-18% eq / 38-45% TLT / 33-39% GLD (Kill B clear, geometry change happens mechanically); score 1:0 2:15 3:0 4:0 5:10 6:3 = 28.
- **Lesson:** TSM-primary on ≤4-asset ETF basket cannot beat SPY/QQQ — turnover ~35/yr/leg × 2 bps cost (2.1%/yr drag) dominates sqrt(3)≈1.7× basket diversification (Carver Law of Active Management); Hurst-Ooi-Pedersen 2017's documented +1.0 Sharpe required 67 markets. Per-asset vol-target IS structurally different from σ²_port but cost > premium at this scale. Closes TSM-primary on broad-asset-class small baskets. Does NOT close slow-EWMAC + exit thresholds, ≥20-market external baskets, carry-primary, VRP-primary. See `iterations/023-2026-04-24-2007-time-series-trend-3etf/`.

### 022 — 2026-04-24 — TOM seasonality eq_weight modulator 0.9↔0.5 (🥉 MARGINAL 54/100)
- **Result:** Sharpe 0.763/0.885/0.977 (Δ frozen +0.08/−0.01/+0.02; **Δ iter 016 −0.218/−0.256/−0.209 uniform regression**), MDD 34.0/32.8/30.6% (+2.7/+6.2/+7.3pp vs 016, Kill #4 2/3), gates 6/6/6, DSR p=0.587/0.513/0.396 worst (Kill #3); raw TOM premium present (Kill #1 clear) but post-overlay inverts on 2/3 ds.
- **Lesson:** σ²_port absorption generalises from variance to calendar-driven weight modulators (σ² quadratic in w_eq, swing 0.5↔0.9 triples σ² → scale÷3 → premium compressed). Closes calendar-modulated eq:bd weight family (TOM/holiday/DoW/MoY/earnings predicted identical). See `iterations/022-2026-04-24-1942-tom-seasonality-overlay/`.

### 021 — 2026-04-24 — Short put credit spread VRP (🥇 STRONG 79/100, ties top-K #1)
- **Result:** Sharpe 0.990/1.138/1.144 (Δ iter 016 +0.009/−0.002/−0.042 Kill #2), MDD 29.4/25.6/20.4% (Δ iter 016 −1.95/−1.01/−2.85pp uniform improvement), gates 6/7, DSR p=0.217 (n=4270 lowest-ever), overlay +2.95-4.10%/yr Bondarenko-matching, winner 4/5; score 1:25 2:19 3:0 4:15 5:15 6:5 = 79.
- **Lesson:** Vol-target absorbs equity-leg options either sign; MDD asymmetric (short −1-3pp, long +3-6pp). Closes options-on-equity-leg family at 5/10%OTM×21DTE bilaterally. See `iterations/021-2026-04-24-1916-short-credit-spread-vrp/`.

### 020 — 2026-04-24 — Monthly put-spread tail hedge (🥇 STRONG 79, Kill #1+#2, dominated vs iter 016)
- **Result:** Sharpe 0.905/1.063/1.142 (Δ iter 016 −0.08/−0.08/−0.04), MDD 37.0/29.9/27.8% (+3-6pp WORSE 3/3), gates 6/7, DSR p=0.340, overlay −3 to −4%/yr theta drag, winner 4/5; score 1:25 2:19 3:0 4:15 5:15 6:5 = 79.
- **Lesson:** Long-gamma overlays redundant with vol-target's variance-responsive scaling. Closes long-gamma overlay family on vol-managed 2-leg stacks. See `iterations/020-2026-04-24-1850-put-spread-tail-hedge/`.

### 019 — 2026-04-24 — HMM stock-bond correlation regime (❌ FAIL 0/100, Kill #PV)
- **Result:** Pre-val rejects all 3 ds (exceed-frac 0.65/0.67/0.49 vs 0.20 ceiling); 0 cfgs run, winner 0/5; score 0.
- **Lesson:** σ²_port contains ρ as algebraic cross-term → any function of ρ cointegrated. Closes ρ-regime overlays; by σ_eq/σ_bd analogy also VIX/MOVE/realized-vol overlays. See `iterations/019-2026-04-24-1833-hmm-stock-bond-regime/`.

### 018 — 2026-04-24 — Funding-cost-modeled iter 016 replay (🥇 STRONG 79/100, ties top-K #1)
- **Result:** Sharpe 0.888/1.065/1.140 (Δ iter 016 −0.09/−0.08/−0.05 post-funding; funding drag 148/114/93 bps/yr), gates 6/7, DSR p=0.370, winner 4/5; score 1:25 2:19 3:0 4:15 5:15 6:5 = 79. 0 new trials.
- **Lesson:** Each 100 bps/yr funding drag ~0.07 Sharpe at 15% vol target. Iter 016 deployability validated post-cost; DSR sole barrier. See `iterations/018-2026-04-24-1813-funding-cost-modeled-replay/`.

### 017 — 2026-04-24 — 12-1 top-1 regional rotation on iter 016 (🥉 MARGINAL 52/100, Kill #1+#2+#3)
- **Result:** Sharpe 0.76/0.82/1.02 (Δ iter 016 −0.23/−0.32/−0.18 all regress), gates 5/7/6/7/6/7, DSR p=0.651/0.651/0.378, winner 3/5; score 1:0 2:17 3:0 4:15 5:15 6:5 = 52.
- **Lesson:** Cross-sectional 12-1 rotation on N=3 regions w/ structurally-dominant US hurts (period Sharpe US 0.63-0.95 vs EFA/EEM 0.33-0.48). Closes top-K∈{1,2} on ≤3-region equity universes. See `iterations/017-2026-04-24-1750-regional-rotation-stack-vm/`.

### 016 — 2026-04-24 — Static 60:40 × Moreira-Muir vol-target hybrid (🥇 STRONG 79/100, top-K #1)
- **Result:** Sharpe 0.98/1.14/1.19 (Δ frozen +0.30/+0.24/+0.24; vs iter 008 +0.12/+0.14/+0.17), gates 6/7 (xds +4), DSR p=0.226 (n=4261), CAGR 15.1/17.8/20.7%, MDD 31.3/26.7/23.2%, winner 4/5; score 1:25 2:19 3:0 4:15 5:15 6:5 = 79.
- **Lesson:** Fixed-ratio × vol-target is structurally ADDITIVE not redundant — iter 015 ratio prevents iter 008 vol-shock; iter 008 scaling adds regime adaptation. DSR sole barrier. See `iterations/016-2026-04-24-1729-static-stack-vm-hybrid/`.

### 015 — 2026-04-24 — Static synthetic NTSX 90/60 SPY+IEF (🥇 STRONG 77/100, 4/5 winner)
- **Result:** Sharpe 0.78/1.04/1.06 (Δ frozen +0.10/+0.14/+0.11 — 1st iter clearing +0.10 cross-ds), gates 5/7/6/7/6/7, DSR p=0.548, winner 4/5; score 1:25 2:17 3:0 4:15 5:15 6:5 = 77.
- **Lesson:** Static fixed weights DOES break σ²_port cointegration ceiling. DSR is universal hunt-loop ceiling. Synth NTSX ~75-100bps funding-cost gap. See `iterations/015-2026-04-24-1704-return-stacked-static-ntsx/`.

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

Consumed/closed: sector rotation (002/003); single-asset vol-scaling (004/005); momentum overlay on blend (007); T10Y3M 2×2 (009/012); 3-leg static blend (010); weekly blend (011); meta-label vol-proxy (013); EBP credit overlay (014); regional rotation (017); HMM ρ regime (019); long-gamma put-spread (020); short-gamma credit-spread VRP overlay (021); calendar-modulated weight (022); **TSM-primary on small basket per-asset vol-target (023 — 28/100, biggest regression).** Top-K #1 still iter 016/018/021 triple-tied at 79.

### Iter 024 candidates (post-iter-023)

0c. **Option C — Cross-asset CARRY as primary** — PRIMARY POST-023. Linear in yield differentials (Asness-Moskowitz-Pedersen 2013), uncorrelated w/ TSM, low turnover ~3-6/yr. Bond-curve carry synthesisable from TLT-vs-IEF/SHY price ratio. `[ilmanen_expected_returns, ch.5-7]`.
0z. **Option Z — Slow EWMAC 64/256 + exit thresholds** — secondary; diagnoses if iter 023 bottleneck was speed or basket size. Turnover ~5-8/yr/leg. `[systematic_trading, p.118-119, ch.7]`.
0v. **Option V — VRP-primary portfolio** (short puts/spreads + cash collateral + Tbill). Premium ~3-4%/yr (Bondarenko 2014); turnover ~12/yr; tail-risk concern. `[volatility_trading, ch.3]`.
0t. **Option T — pre-registered minimal-trial replay of iter 016** (n_trials=1, PSR clears) — §7 override artifact.

### Deeper backlog

- Calendar effects family closed (iter 022).
- Plano C sleeve meta-allocation (GDE/AVUV/AVDE/AVEM/BTGD).
- Cross-sectional factor timing (likely ≥10 factor ETFs needed, close to iter 003 floor).

---

## Structural dead-ends (1-line summaries; full text in `DEAD_ENDS.md`)

- Daily EMA/SMA threshold on 3× LETF + any overlay (iter 001)
- Drawdown-based stop-loss as primary protection (iter 001)
- CAPE as standalone single-indicator de-lever 2002-2015 (iter 001)
- WF MDD<25% gate with leveraged trend — structural conflict (iter 001)
- Param variations of iter 001 base configs (iter 001)
- Clenow 10bps ATR-risk-parity on sector-ETF universe top-K=3-5 — under-deploys ~3× (iter 002)
- 4-cfg single-family grid when all configs land near-zero (G1 PBO noise floor ~0.5, iter 002)
- Clenow adjusted-slope × R² equal-notional on 11 SPDR sectors — full deployment, signal absent (iter 003)
- Cross-sectional ranking momentum on ≤20-asset homogeneous baskets (sector / factor / country ETFs, iter 003)
- Single-asset vol-adaptation σ⁻¹/σ⁻² on SPY/QQQ — family saturates +0.08-0.10 (iter 004 + 005)
- Time-series momentum overlay (12-1 / 6-1 / 18-1) on vol-managed blend — REDUNDANT with variance-scaling (iter 007)
- T10Y3M 21d-EMA binary haircut symmetric on iter 008 blend — smoothing destroys lead-time (iter 009)
- 3-leg SPY+TLT+GLD daily on `vt15_L21_cap20_3leg` — ties iter 008 at 74/100, blend family ceiling (iter 010)
- Weekly/monthly rebalance for vol-managed multi-leg blend — daily cadence required; MDD +10-14pp, DSR worse (iter 011)
- T10Y3M asymmetric equity-leg haircut 5d EMA on iter 008 — 100% overlap as iter 009; 2×2 matrix fully closed (iter 012)
- Meta-labeling LR with ρ_stockbond + VIX_z on iter 008 — vol-proxy features cointegrate with σ²_port at business cycle (iter 013)
- EBP (GZ2012) credit-cycle overlay on iter 008 — pre-val rejects all 3 ds (60d |ρ|>0.3 on 68-71% bars); 4th overlay failure on iter 008 blend; **overlay family CLOSED on this mechanism; pre-val screen mandatory for any future overlay** (iter 014)
- 12-1 top-K=1 cross-sectional rotation on ≤3-region equity universe with iter 016 base — period Sharpe differential (US 0.63-0.95 vs EFA/EEM 0.33-0.48) exceeds uplift; closes top-K∈{1,2} × any lookback on N≤3 regional universes (iter 017)
- Any regime overlay using stock-bond correlation ρ on vol-managed 2-leg stack — ρ enters σ²_port as cross-term, any f(ρ) is algebraically cointegrated; HMM discretization doesn't rescue; by σ_eq/σ_bd analogy also closes VIX/MOVE/realized-vol overlays (iter 019)
- Options-on-equity-leg 5/10%OTM×21DTE either sign on vol-managed 2-leg stack — σ²_port→scale absorbs variance; Sharpe tied regardless of sign (iter 020 long Δ−0.04 to −0.08; iter 021 short Δ+0.01/−0.00/−0.04). MDD asymmetric (short −1 to −3pp, long +3 to +6pp). Does NOT close bare short puts/ATM straddles/different DTE/VX futures roll (iter 020/021)
- Calendar-driven eq:bd weight modulator on vol-managed 2-leg stack (TOM/holiday/DoW/MoY) — σ²_port QUADRATIC in w_eq; swing 0.5↔0.9 triples σ² on flagged days, scale compensates 3×; premium compressed + mid-month w_bd overshoot → Sharpe uniformly −0.21 to −0.26 vs iter 016. Raw TOM premium IS present but absorbed. Does NOT close binary entry/exit, variance-disjoint legs, cross-sectional ranking (iter 022)
- TSM (any lookback {3-24m}/skip {0-2m}) as PRIMARY mechanism on ≤4-asset broad-asset-class ETF basket with per-asset vol-target — turnover ~35/yr/leg × 2 bps cost > sqrt(3)~1.7× diversification; geometry change happens (kill #B+C clear) but cost > premium. Sharpe regress 0.43-0.59 vs iter 016 (biggest ever). Does NOT close slow-EWMAC + exit thresholds, ≥20-market baskets, carry-primary, VRP-primary (iter 023)

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
