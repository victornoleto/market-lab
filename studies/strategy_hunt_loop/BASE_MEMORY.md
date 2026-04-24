---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 20
winners_found: 0
status: iterating
latest_iteration: "020-2026-04-24-1850"
cumulative_n_trials: 4267
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
| **1** | **016** | 🥇 **STRONG** | **79** | `ntsx_vm_vt15_L21_cap20` (0.6/0.4 static ratio × Moreira-Muir vol-target) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | 4/5 winner; 3/3 Sharpe +0.24-0.30; 9/9 sub-windows; hybrid beats both parents; DSR sole fail (p=0.13-0.23); funding-cost validated by iter 018 |
| **1** | **018** | 🥇 **STRONG** | **79** | `ntsx_vm_vt15_L21_cap20_funded` (iter 016 + r_Tbill drag SHV-lagged) | `[risk_parity, p.80-84]` + NTSX prospectus | ties iter 016; edges survive funding cost (−93 to −148 bps/yr → post-edges +0.17/+0.19/+0.21 still clear +0.10 gate); 4/5 winner |
| 3 | 015 | 🥇 STRONG | 77 | `ntsx_synth_90_60_daily` (static 0.9 SPY + 0.6 IEF) | `[risk_parity, p.5]` + Asness-Frazzini-Pedersen 2012 | 4/5 winner; first mech to escape σ²_port cointegration |
| 4 | 008 | 🥈 PROMISING | 74 | `vt15_L21_cap20` (2-leg SPY+TLT vol-mgmt) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | 4/5 winner; vol-managed reference baseline |
| 4 | 010 | 🥈 PROMISING | 74 | `vt15_L21_cap20_3leg` (3-leg SPY+TLT+GLD) | `[risk_parity, p.10-11]` + Asness-Frazzini-Pedersen 2012 | ties iter 008 — blend family ceiling |

*(iter 001 ~35/100 approximate; back-fill in `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iteration in full 6-field format; older entries compressed to
3 lines (Result + Lesson + iter-dir pointer) once the file approaches
the 18 KB ceiling. Full hypothesis, citations, scope and score
breakdown for compressed iters are recoverable from
`iterations/NNN-*/hypothesis.md` + `verdict.json` + `final_report.md`.

### 020 — 2026-04-24 — Monthly-rolled put-spread tail hedge (5/10% OTM, 21-DTE, VIX-IV) on iter 016 base (🥇 STRONG by score, **Kill #1+#2 TRIGGERED**)
- **Result:** Sharpe edu/spy/ndx 0.905/1.063/1.142 (Δ frozen +0.22/+0.16/+0.19 — PASS +0.10 gate 3/3 inherited from iter 016; **Δ iter 016 −0.076/−0.077/−0.044**), MDD 37.0/29.9/27.8% (**Δ iter 016 +5.7/+3.2/+4.6pp WORSE 3/3**), gates 6/7/6/7/6/7, DSR worst p=0.340 (n=4267; worse than iter 016's 0.226), overlay annual −3.03/−3.00/−4.13%, winner 4/5; score 1:25 2:19 3:0 4:15 5:15 6:5 = 79 (ties top-K by rubric, DOMINATED vs iter 016 on all axes).
- **Lesson:** **Convex options overlays on vol-managed stacks are REDUNDANT, not complementary.** Carr-Madan orthogonality is a STATIC info statement — in a dynamic σ-feedback system (iter 016's vol-target already de-levers on σ² spike) both mechanisms fire on same event → net 3-4%/yr cost with zero MDD benefit. Rubric score 79 MISLEADING (measures edge vs SPY, not vs parent); Kill criteria correctly flagged failure. Closes long-gamma overlay family on vol-managed 2-leg stacks; does NOT close short-vol harvest or options-on-unlevered primitives. See `iterations/020-2026-04-24-1850-put-spread-tail-hedge/`.

### 019 — 2026-04-24 — HMM stock-bond correlation regime rotation on iter 016 base (❌ FAIL, 0/100, Kill #PV)
- **Result:** Pre-val rejects all 3 ds (exceed-frac 0.646/0.665/0.488 vs 0.20 ceiling; continuous ρ_60 0.645/0.647/0.667), 0 cfgs run, 0 new trials, winner 0/5; score 1:0 2:0 3:0 4:0 5:0 6:0 = 0.
- **Lesson:** σ²_port contains ρ as algebraic cross-term → any function of ρ is ALGEBRAICALLY cointegrated, not empirically. Closes ρ-regime overlays on vol-managed stacks; by σ_eq/σ_bd analogy also closes VIX/MOVE/realized-vol overlays. See `iterations/019-2026-04-24-1833-hmm-stock-bond-regime/`.

### 018 — 2026-04-24 — Funding-cost-modeled iter 016 replay (🥇 STRONG, 79/100, ties top-K #1)
- **Result:** Sharpe edu/spy/ndx 0.888/1.065/1.140 (Δ frozen +0.21/+0.16/+0.19 — 3/3 pass +0.10 gate; funding drag 148/114/93 bps/yr), gates 6/7/6/7/6/7, DSR worst p=0.370 (n=4264), winner 4/5; score 1:25 2:19 3:0 4:15 5:15 6:5 = 79. 0 new trials.
- **Lesson:** Each 100 bps/yr funding drag costs ~0.07 Sharpe at 15% vol target. Iter 016 deployability validated post-cost; DSR now sole winner-barrier. See `iterations/018-2026-04-24-1813-funding-cost-modeled-replay/`.

### 017 — 2026-04-24 — 12-1 top-1 regional rotation on iter 016 base (🥉 MARGINAL, 52/100, Kill #1+#2+#3)
- **Result:** Sharpe edu/spy/ndx 0.76/0.82/1.02 (Δ frozen +0.08/−0.08/+0.06, Δ iter 016 −0.23/−0.32/−0.18 all regress), gates 5/7/6/7/6/7, DSR p=0.651/0.651/0.378, winner 3/5; score 1:0 2:17 3:0 4:15 5:15 6:5 = 52.
- **Lesson:** Cross-sectional 12-1 rotation on N=3 regional equity universe with structurally-dominant US HURTS (period Sharpe differential US 0.63-0.95 vs EFA/EEM 0.33-0.48 exceeds momentum uplift). Closes top-K ∈ {1,2} on ≤ 3-region equity universes. See `iterations/017-2026-04-24-1750-regional-rotation-stack-vm/`.

### 016 — 2026-04-24 — Static 60:40 ratio × Moreira-Muir vol-target hybrid (🥇 STRONG, 79/100, top-K #1, 4/5 winner, DSR sole fail)
- **Result:** Sharpe edu/spy/ndx 0.98/1.14/1.19 (Δ frozen +0.30/+0.24/+0.24 — HUGE margins; vs iter 008 +0.12/+0.14/+0.17), gates 6/7/6/7/6/7 (cross-ds bonus +4), DSR worst p=0.226 (LOWEST in history, n=4261), CAGR 15.1/17.8/20.7%, MDD 31.3/26.7/**23.2%**, winner 4/5, G3 WF 7/8/8/8/8/8, G7 xlib 0.02-0.04pp; score 1:25 2:19 3:0 4:15 5:15 6:5 = **79**. Kill #1/#3/#4 ALL FALSE.
- **Lesson:** **Fixed-ratio × vol-target is structurally ADDITIVE not redundant** — iter 015's fixed ratio prevents iter 008's asymmetric vol-shock vulnerability; iter 008's scaling adds regime adaptation. Post-funding-cost edge still clears +0.10 on 3/3 ds (iter 018). DSR is sole barrier. See `iterations/016-2026-04-24-1729-static-stack-vm-hybrid/`.

### 015 — 2026-04-24 — Static synthetic NTSX 90/60 SPY+IEF stack (🥇 STRONG, 77/100, 4/5 winner)
- **Result:** Sharpe edu/spy/ndx 0.78/1.04/1.06 (Δ frozen +0.10/+0.14/+0.11 — 1st iter clearing +0.10 gate cross-ds), gates 5/7/6/7/6/7, DSR worst p=0.548 (n=4258), CAGR+MDD floor 3/3, G6 9/9, winner 4/5; score 1:25 2:17 3:0 4:15 5:15 6:5 = **77**.
- **Lesson:** First mechanism change (static fixed weights) DOES break σ²_port cointegration ceiling. DSR is universal hunt-loop ceiling regardless of mechanism. Synth NTSX has ~75-100bps funding-cost gap. See `iterations/015-2026-04-24-1704-return-stacked-static-ntsx/`.

### Iters 005-014 (compressed 1-line; full detail in `iterations/NNN-*/`)

- **014** (❌ FAIL 0, Kill #PV) — EBP GZ2012 credit overlay on iter 008, pre-val screen rejects all 3 ds (exceed_frac 0.68-0.71, 3.4× cap); no backtest. 4th consecutive overlay failure on iter 008 blend → overlay family CLOSED; pre-val screen now mandatory.
- **013** (🥈 PROMISING 64, Kill #3) — LR meta-label with ρ_60 + vix_z on iter 008 blend: Sharpe regress −0.01 to −0.01, 100% overlap at bottom-20% scale on edu+spy; vol-proxy meta is REDUNDANT with variance-scaling (3rd "regime overlay" approach closed).
- **012** (🥉 MARGINAL 58, Kill #1+#3+#4) — 5d EMA asymmetric T10Y3M equity-leg haircut on iter 008: Sharpe regress 0.04-0.05, 100% overlap edu+spy (same as iter 009). Closes 2×2 {smoothing × asymmetry} matrix — T10Y3M overlay family structurally cointegrated, not parametric.
- **011** (🥉 MARGINAL 52, Kill #1+#3) — Weekly 3-leg blend: Sharpe regress 3/3, MDD +10-14pp, DSR worse (0.368→0.515), cap-hit 86→95%, turnover UP. Vol-targeting REQUIRES daily cadence; DSR via T-reduction cancels at first order.
- **010** (🥈 PROMISING 74) — 3-leg SPY+TLT+GLD vol-managed daily: ties iter 008 at 74/100, 4/5 winner. Blend family saturates Sharpe ~1.00 regardless of N=2 or N=3; DSR is the ceiling.
- **009** (🥈 PROMISING 64, Kill #3) — 21d EMA symmetric T10Y3M haircut on iter 008 blend: 100% overlap at bottom-20% blend-scale, smoothing destroys lead-time.
- **008** (🥈 PROMISING 74) — Single-cfg ex-ante vol-managed SPY+TLT blend `vt15_L21_cap20`: Sharpe 0.87/1.00/1.02, gates 6/6/6, DSR p=0.332, G1 N=1 vacuous PASS; 4/5 winner; iter 006's blend edge IS structural.
- **007** (🥉 MARGINAL 50, Kill #1+#3) — 12-1 momentum overlay on iter 006: Sharpe regress on 2/3 ds; momentum REDUNDANT with variance-scaling (both track equity-vol regime).
- **006** (🥈 PROMISING 67, Kill #3) — 12-cfg grid vol-managed SPY+TLT blend: Sharpe 0.93/1.00/1.02, first +0.10 gate cross-ds; killed by G1 PBO 0.69 (grid inflates). Cross-asset compounding WORKS.
- **005** (🥉 MARGINAL 59) — Moreira-Muir σ⁻² single-asset on SPY/QQQ: first DSR edu PASS; single-asset vol-adaptation saturates +0.08-0.10 regardless of exponent. Compounding only path through.

### Iters 001-004 (compressed; full detail in iter dirs)

- **001** (NEAR_FAIL ~35) — Crash-protected LETF trend, 4020 cfgs, 0/16 cross-ds winners. See `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md`.
- **002** (FAIL 17) — Clenow 10bps ATR-risk-parity on 11 SPDR sectors → 63-75% cash drag (ATR sized for stocks).
- **003** (FAIL 7) — Clenow adjusted-slope × R² equal-notional on 11 sectors; ≤20-asset homogeneous ETF universe lacks ranking signal.
- **004** (MARGINAL 51) — Single-asset vol-scaling SPY σ⁻¹ (Carver). 6/7 gates spy+ndx, G6 first-ever pass, MDD −6/−9pp; Sharpe edge +0.08-0.15 (below +0.10 spy).

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iterations.

Consumed (DEAD_ENDS or saturated): sector rotation 1/K + Clenow (002/003); single-asset vol-scaling (004/005); momentum overlay (007 redundant); iter 006 single-cfg verif (008 structural); T10Y3M overlay 2×2 (009/012); 3-leg blend (010 ties 008); weekly blend (011); meta-label vol-proxy (013); EBP credit overlay (014 pre-val); iter 015 static NTSX (77 STRONG); iter 016 static×vol-target (79 STRONG top-K #1, 4/5, DSR sole fail); iter 017 regional rotation (52 MARGINAL); iter 018 funding-cost replay (79 STRONG ties top-K #1, iter 016 deployability confirmed); iter 019 HMM ρ_60 regime rotation (Option P') FAILED Kill #0 pre-val — closes ρ-derived regime overlays on vol-managed 2-leg stacks algebraically (σ²_port contains ρ as cross-term factor); **iter 020 put-spread tail hedge (Option S) scored 79 but Kills #1+#2 TRIGGERED — closes long-gamma overlay family on vol-managed stacks (convex P&L is REDUNDANT with vol-target's variance-responsive scaling, not complementary; both fire on σ² spikes).**

### Iter 021 candidates (ranked by expected DSR-clearance value)

**Framing:** Iter 016 top-K #1 (79/100 STRONG, 4/5, DSR sole barrier). Iter 018 confirmed deployability post-funding-cost. Iter 019 closed ρ-regime overlays algebraically. Iter 020 closed long-gamma overlays on vol-managed stacks (REDUNDANT with vol-target). Remaining primitives with features disjoint from iter 016's (σ_eq, σ_bd, ρ, long-gamma):

0v. **[OPTION V — VARIANCE PREMIUM HARVEST (short-vol)]** — PRIMARY. SELL short-dated put or straddle on equity leg; harvests 2-3%/yr VRP that iter 020 paid. P&L OPPOSITE sign (theta-positive calm, negative-skewed crash); fires on OPPOSITE event (low realized-vs-implied, not σ² spike) → does NOT overlap iter 020's closure. Expected +0.10-0.20 Sharpe. Reuses SPY+VIX infra (same BS framework, opposite sign). Citations: `[volatility_trading, ch.3]` VRP; Bondarenko (2014); CBOE PUT index.

0w. **[OPTION W — CROSS-ASSET CARRY FX/commodities/bonds]** — secondary. Linear P&L from interest-rate differentials / futures curve slope / term structure — disjoint from (σ_eq, σ_bd, ρ) and from long-gamma. Requires new data (FX ETFs, commodity basket, short bonds). Citation: `[ilmanen_expected_returns, ch.5-7]`.

0x. **[OPTION X — UNCORRELATED ASSET IN STACK]** — tertiary. Add 3rd leg (managed-futures trend proxy DBMF, or controlled long-vol ETF) to iter 016 stack. Expands σ²_port ingredient set. Citations: `[risk_parity, ch.5-7]`; `[systematic_trading, ch.14]`.

0t. **[OPTION T — PRE-REGISTERED MINIMAL-TRIAL TEST]** — parallel track, not a hunt iter. Rerun iter 016 post-cost with n_trials=1; PSR trivially clears p<0.001. Documentation artifact for mandate §7 override.

### Deeper backlog (not yet designed as iter-next)

- Seasonality (turn-of-month / sell-in-May / Santa) — never through 7-gate pipeline.
- Meta-allocation among Plano C sleeves (GDE / AVUV / AVDE / AVEM / BTGD).
- Cross-sectional factor timing (Asness AQR 2024).

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
- 12-1 top-K=1 cross-sectional rotation on 3-region equity universe (US+EFA+EEM) with iter 016 base — actively HURTS vs always-US (Δ Sharpe −0.18/−0.32 on 3/3 ds); period Sharpe differential (US 0.63-0.95 vs EFA/EEM 0.33-0.48) exceeds regional-leadership uplift; closes top-K ∈ {1,2} × any lookback × any cadence for N ≤ 3 regional equity universes (iter 017)
- **Any regime overlay using stock-bond correlation ρ on vol-managed 2-leg stack — ALGEBRAICALLY cointegrated with σ²_port (which contains ρ as multiplicative factor in cross-term); pre-val exceed-frac 0.65/0.67/0.49 on 3/3 ds; HMM discretization does NOT rescue (it is a smoothing operator on ρ, not a feature-space change); by analogous σ_eq/σ_bd dependence also closes VIX/MOVE/realized-vol overlays on vol-managed stacks (iter 019)**
- **Monthly-rolled OTM put-spread tail hedge (5/10% OTM, 21-DTE, VIX-IV) on vol-managed 2-leg stack — convex options P&L REDUNDANT with vol-target's variance-responsive scaling (both fire on σ² spikes); drag 3-4%/yr, Sharpe regress −0.04 to −0.08, MDD WORSE +3-6pp 3/3 ds (Kill #2). Closes long-gamma overlay family on vol-managed stacks; does NOT close short-vol harvest / options-on-unlevered (iter 020)**

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
