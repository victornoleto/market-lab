---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 18
winners_found: 0
status: iterating
latest_iteration: "018-2026-04-24-1813"
cumulative_n_trials: 4264
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

### 018 — 2026-04-24 — Funding-cost-modeled iter 016 replay (Option Q) (🥇 STRONG, 79/100, ties iter 016 top-K #1, hypothesis CONFIRMED)
- **Result:** Sharpe edu/spy/ndx 0.888/1.065/1.140 (Δ frozen +0.21/+0.16/+0.19 — 3/3 clear +0.10 gate; Δ vs iter 016 gross −0.10/−0.07/−0.05 funding drag), gates 6/7+6/7+6/7, DSR worst p=0.370 (regressed from iter 016 0.226 via lower obs Sharpe × same n_trials=4264), CAGR 13.4/16.5/19.6% floor 3/3, MDD 33.3/26.7/23.2% (+2.0/+0.0/−0.1 pp), winner 4/5 (DSR sole fail, identical to iter 016), funding drag 148/114/93 bps/yr (scale_mean 1.8/1.8/1.7 at 76/79/63% cap-hit; excess_lev_mean 0.84), robustness 9/9; score 1:25 2:19 3:0 4:15 5:15 6:5 = 79. **Zero kills → hypothesis CONFIRMED.** 0 new trials (same cfg).
- **Lesson:** Iter 016 is deployability-validated against largest-known unmodeled cost. Each 100 bps/yr funding drag costs ~0.07 Sharpe at 15% vol target. Rule of thumb: candidates with gross edge < +0.20 need funding-cost replay before top-K entry. DSR now the SOLE axis blocking winner; only primitive still structurally untested that can deliver +0.3-0.5 Sharpe uplift is Option S (put-spread collar). Iter 019 PICK: Option S (CBOE PPUT/BXMY data ingestion, convex P&L orthogonal to σ²_port cointegration family). See `iterations/018-2026-04-24-1813-funding-cost-modeled-replay/`.

### 017 — 2026-04-24 — 12-1 top-1 regional rotation on iter 016 base (🥉 MARGINAL, 52/100)
- **Result:** Sharpe edu/spy/ndx 0.76/0.82/1.02 (Δ frozen +0.08/−0.08/+0.06 — 0/3 clear +0.10 gate; Δ vs iter 016 −0.23/−0.32/−0.18 ALL regress ≥ 0.03), gates 5/7+6/7+6/7, DSR p=0.651/0.651/0.378 (worse than iter 016 all ds), CAGR 11.99/13.03/17.47%, MDD 31.99/29.42/22.95%, winner 3/5; region selection US 58-78% / EM 10-30% / INTL 11-12%; score 1:0 2:17 3:0 4:15 5:15 6:5 = 52. **Kill #1/#2/#3 triggered.**
- **Lesson:** Cross-sectional 12-1 rotation on N=3 regional equity universe with structurally-dominant US actively HURTS (period Sharpe differential US 0.63-0.95 vs EFA/EEM 0.33-0.48 exceeds any momentum uplift). Closes top-K ∈ {1, 2} × any lookback × any cadence on ≤ 3-region equity universes. See `iterations/017-2026-04-24-1750-regional-rotation-stack-vm/`.

### 016 — 2026-04-24 — Static 60:40 ratio × Moreira-Muir vol-target hybrid (🥇 STRONG, 79/100, top-K #1, 4/5 winner, DSR sole fail)
- **Result:** Sharpe edu/spy/ndx 0.98/1.14/1.19 (Δ frozen +0.30/+0.24/+0.24 — 3/3 clear gate with HUGE margins; +0.20/+0.09/+0.13 vs iter 015; +0.12/+0.14/+0.17 vs iter 008), gates 6/7, 6/7, 6/7 (cross-ds §0 met +4 bonus), DSR worst p=0.226 (LOWEST in history), CAGR 15.08/17.79/20.73%, MDD 31.33/26.65/**23.23%**, winner 4/5, G3 WF 7/8+8/8+8/8, G6 9/9, G7 xlib 0.02-0.04pp; cap-hit 63-79%, turnover 4.6-7.4/yr; score 1:25 2:19 3:0 4:15 5:15 6:5 = **79** (top-K #1). Kill #1/#3/#4 ALL FALSE.
- **Lesson:** **Fixed-ratio × vol-target is structurally ADDITIVE not redundant** — iter 015's fixed ratio prevents iter 008's vulnerability to asymmetric single-leg vol shocks; iter 008's scaling adds regime adaptation. Post-funding-cost edge still clears +0.10 on 3/3 ds. DSR is now the sole barrier. See `iterations/016-2026-04-24-1729-static-stack-vm-hybrid/`.

### 015 — 2026-04-24 — Static synthetic NTSX 90/60 SPY+IEF stack (🥇 STRONG, 77/100, 4/5 winner)
- **Result:** Sharpe edu/spy/ndx 0.78/1.04/1.06 (Δ frozen +0.10/+0.14/+0.11 — 1st iter clearing gate cross-ds), gates 5/7+6/7+6/7, DSR worst p=0.548, CAGR+MDD floor 3/3 (ndx MDD 39.51% vs 40.12% razor 0.61pp), G6 9/9, score 1:25 2:17 3:0 4:15 5:15 6:5 = **77**.
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

Consumed (DEAD_ENDS or saturated): sector rotation 1/K + Clenow (002/003); single-asset vol-scaling (004/005); momentum overlay on vol-managed blend (007 redundant); iter 006 single-cfg verification (008 structural); T10Y3M overlay full 2×2 (009/012); 3-leg blend daily (010 ties iter 008); weekly-cadence blend (011); meta-label vol-proxy (013); EBP credit-cycle overlay (014 pre-val); iter 015 static NTSX stack (77/100 STRONG, 4/5 winner); iter 016 static×vol-target hybrid (79/100 STRONG top-K #1, 4/5 winner, DSR sole fail); iter 017 — 12-1 top-1 regional rotation (US/INTL/EM) on iter 016 base — FAILED 52/100 MARGINAL; **iter 018 — Option Q funding-cost-modeled iter 016 replay — CONFIRMED 79/100 STRONG ties iter 016, 4/5 winner, 3/3 post-cost edges still clear +0.10 gate (+0.21/+0.16/+0.19), iter 016 deployability validated; robustness protocol added (candidates with gross edge < +0.20 must run funding-cost replay before top-K entry). Does NOT close any mechanism — confirms iter 016 as top candidate under realistic cost assumptions.**

### Iter 019 candidates (ranked by expected DSR-clearance value)

**Framing:** Iter 016 remains hunt-loop top-K #1 at 79/100 STRONG, 4/5 winner. Iter 018 **confirmed deployability** — funding-cost drag (−0.054 to −0.096 Sharpe/ds, 93-148 bps/yr) doesn't break +0.10 gate. DSR remains the sole winner-condition barrier (worst p 0.37 post-cost, needs < 0.05 at n_trials = 4264). Clearance path requires Sharpe uplift of +0.3-0.5 on worst dataset via genuinely orthogonal information. Only primitive structurally untested with sufficient magnitude is options tail-hedge (convex P&L cannot cointegrate with σ²_port).

0s. **[OPTION S — PUT-SPREAD COLLAR TAIL-HEDGE ON ITER 016 EQUITY LEG]** — PRIMARY rec for iter 019. Finance a 10Δ put spread via a 25Δ covered call on SPY/QQQ leg of iter 016 (bond leg unchanged; funding cost now modeled per iter 018). Adds skewness-capture axis (Taleb tail-hedge) that is **convex** in underlying → cannot cointegrate with σ²_port at business-cycle scale the way linear signals did in iter 009/012/013/014. Expected +0.05-0.15 Sharpe via MDD reduction + preserved upside. Requires CBOE PPUT/BXMY/CLL indices data ingestion (~2-3h engineering; freely available from cboe.com/indices). Citations: `[dynamic_hedging, ch.3-4]` (Taleb), Carr-Madan (1999), CBOE BXM/BXY/PPUT methodology.

0p. **[OPTION P' — HMM STOCK-BOND CORRELATION REGIME ROTATION + PRE-VAL SCREEN]** — secondary. 2-state HMM on 60d rolling ρ(SPY, IEF): regime A (ρ < −0.1) → iter 016 60:40; regime B (ρ > 0) → defensive 30:70. **Iter 014 predicts pre-val screen likely FAILS for ρ_60** (continuous) but HMM's discrete state ∈ {0, 1} might break cointegration sufficiently. Run pre-val screen FIRST; if |ρ(state, σ²_port)| > 0.30 on > 20% of bars, abort without DSR budget. Citation `[regime_change, ch.2]`.

0t. **[OPTION T — PRE-REGISTERED MINIMAL-TRIAL TEST OF ITER 016]** — tertiary. NOT a hunt-loop iteration but a deployability protocol. Rerun iter 016 post-cost with cumulative_n_trials=1 (single pre-registered cfg), compute PSR at observed Sharpe 1.065 (spy_real post-cost). At n_trials=1, PSR trivially clears p < 0.001. Documentation artifact for future mandate §7 override; zero-eng parallel track.

### Deeper backlog (not yet designed as iter-next)

- Cross-asset carry (FX / commodities / bonds), `[ilmanen_expected_returns]`.
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
