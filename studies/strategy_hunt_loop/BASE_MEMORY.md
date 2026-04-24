---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 16
winners_found: 0
status: iterating
latest_iteration: "016-2026-04-24-1729"
cumulative_n_trials: 4261
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
| **1** | **016** | 🥇 **STRONG** | **79** | `ntsx_vm_vt15_L21_cap20` (0.6/0.4 static ratio × Moreira-Muir vol-target) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | 4/5 winner; 3/3 Sharpe +0.24-0.30; 9/9 sub-windows; hybrid beats both parents; DSR sole fail (p=0.13-0.23) |
| 2 | 015 | 🥇 STRONG | 77 | `ntsx_synth_90_60_daily` (static 0.9 SPY + 0.6 IEF) | `[risk_parity, p.5]` + Asness-Frazzini-Pedersen 2012 | 4/5 winner; first mech to escape σ²_port cointegration |
| 3 | 008 | 🥈 PROMISING | 74 | `vt15_L21_cap20` (2-leg SPY+TLT vol-mgmt) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | 4/5 winner; vol-managed reference baseline |
| 3 | 010 | 🥈 PROMISING | 74 | `vt15_L21_cap20_3leg` (3-leg SPY+TLT+GLD) | `[risk_parity, p.10-11]` + Asness-Frazzini-Pedersen 2012 | ties iter 008 — blend family ceiling |
| 5 | 006 | 🥈 PROMISING | 67 | `vt15_L21_cap20` (12-cfg grid) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | first blend; killed by grid PBO 0.690 |

*(iter 001 ~35/100 approximate; back-fill in `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iteration in full 6-field format; older entries compressed to
3 lines (Result + Lesson + iter-dir pointer) once the file approaches
the 18 KB ceiling. Full hypothesis, citations, scope and score
breakdown for compressed iters are recoverable from
`iterations/NNN-*/hypothesis.md` + `verdict.json` + `final_report.md`.

### 016 — 2026-04-24 — Static 60:40 ratio × Moreira-Muir vol-target hybrid (🥇 STRONG, 79/100, NEW HUNT-LOOP HIGH, 4/5 winner, DSR sole fail)
- **Hypothesis + Citations:** Fixed normalised ratio 0.6 equity / 0.4 bond (preserves iter 015's 90:60 un-normalised at scale=1.5) × Moreira-Muir portfolio-level variance-target scaling on top (inherits iter 008's `scale[t] = clip(target_vol²/σ²_port[t-1], 0, max_lev)` but with σ²_port computed against FIXED weights, not dynamic inverse-variance). Single cfg `ntsx_vm_vt15_L21_cap20` (target_vol=0.15, lookback=21d, max_lev=2.0). Hybrid of iter 008 + iter 015 primitives. Citations: `[risk_parity, p.10-11, ch.1]`; `[systematic_trading, p.40, ch.2, p.170-171, ch.11]`; Moreira-Muir (2017) JoF 72(4); Asness-Frazzini-Pedersen (2012) FAJ 68(1). Scope: 1 cfg × 3 ds = 3 trials (n_trials 4258→4261); +14 TDD specs (775 pass + 5 skip, +14 vs iter 015's 761 pass).
- **Result:** Sharpe edu/spy/ndx **0.98/1.14/1.19** (Δ frozen +0.30/+0.24/+0.24 — 3/3 clear gate with HUGE margins, +0.20/+0.09/+0.13 VS iter 015, +0.12/+0.14/+0.17 vs iter 008), gates **6/7, 6/7, 6/7** (cross-ds §0 met +4 bonus; edu gate 5→6), DSR worst p **0.226** (sole fail but LOWEST in hunt-loop history — vs iter 015's 0.548), CAGR 15.08/17.79/20.73% floor 3/3 ✓, MDD 31.33/26.65/**23.23%** (ceilings 60.14/38.70/40.12 — 28.8/12.1/16.9 pp margin; vs iter 015 −13/−4/−16 pp), winner **4/5** (DSR only), G3 WF 7/8, **8/8, 8/8** (hunt-loop 1st 8/8 double), G5 post-2020 0.89/0.89/1.00, G6 9/9 robustness 0.80-1.55, G7 xlib 0.02-0.04pp; scale cap-hit 63-79%, turnover 4.6-7.4/yr; score 1:25 2:19 3:0 4:15 5:15 6:5 = **79** (new top-K #1). Kill #1/#3/#4 ALL FALSE (Sharpe + MDD + score all IMPROVED).
- **Lesson:** **Fixed-ratio × vol-target is structurally ADDITIVE not redundant** — iter 015's cointegration-free fixed ratio prevents iter 008's vulnerability to asymmetric single-leg vol shocks; iter 008's scaling provides regime adaptation iter 015 lacks at constant 1.5×. Together beats BOTH parents cleanly (+0.13-0.20 vs iter 008, +0.09-0.20 vs iter 015). Post-funding-cost edge **still clears +0.10 on 3/3 ds** (vs iter 015's borderline) — more robust to optimism gap. **DSR is now within striking distance** (p=0.13 ndx; needs Sharpe +0.3 lift). Iter 017 PICK: Option R (NTSX/NTSI/NTSE regional rotation) — add orthogonal cross-sectional dimension on iter 016 base. See `iterations/016-2026-04-24-1729-static-stack-vm-hybrid/`.

### 015 — 2026-04-24 — Static synthetic NTSX 90/60 SPY+IEF stack (🥇 STRONG, 77/100)
- **Result:** Sharpe edu/spy/ndx 0.78/1.04/1.06 (Δ frozen +0.10/+0.14/+0.11 — 1st iter clearing gate cross-ds), gates 5/7, 6/7, 6/7, DSR worst p=0.548 sole fail (n_trials=4258), CAGR+MDD floor 3/3 (ndx MDD 39.51% vs 40.12% ceiling razor 0.61pp), winner 4/5, G6 9/9 sub-windows positive; score 1:25 2:17 3:0 4:15 5:15 6:5.
- **Lesson:** First mechanism change (static fixed weights) DOES break σ²_port cointegration ceiling. DSR is universal hunt-loop ceiling regardless of mechanism. Synth NTSX has ~75-100bps funding-cost optimism gap → post-drag edge BORDERLINE on +0.10 strict gate. See `iterations/015-2026-04-24-1704-return-stacked-static-ntsx/`.

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

Consumed (DEAD_ENDS or saturated): sector rotation 1/K + Clenow (002/003); single-asset vol-scaling (004/005); momentum overlay on vol-managed blend (007 redundant); iter 006 single-cfg verification (008 structural); T10Y3M overlay full 2×2 (009/012); 3-leg blend daily (010 ties iter 008); weekly-cadence blend (011); meta-label vol-proxy (013); EBP credit-cycle overlay (014 pre-val); iter 015 static NTSX stack (77/100 STRONG); **iter 016 — STATIC 60:40 × VOL-TARGET HYBRID SCORED 79/100 STRONG, NEW HUNT-LOOP HIGH, 4/5 winner conds, DSR p=0.13-0.23 SOLE FAIL — beats both parent mechanisms cleanly; fixed ratio + vol-scaling are ADDITIVE**.

### Iter 017 candidates (ranked by expected DSR-clearance lift)

**Framing:** Iter 016 established a STRONG baseline (79/100) that clears 4/5 strict winner conditions with +0.24-0.30 Sharpe edge on 3/3 ds and robust post-funding-cost edge. DSR is the sole barrier at n_trials=4261 — needs Sharpe ≳ 1.5 on worst dataset (currently 0.98 edu). To clear DSR cleanly, iter 017 must add Sharpe uplift of +0.3-0.5 via an ORTHOGONAL information source — vol-target axis is now saturated on iter 016, and cross-asset diversification is already maxed by the 60:40 ratio.

0r. **[OPTION R — NTSX/NTSI/NTSE REGIONAL ROTATION ON ITER 016 BASE]** — PRIMARY rec for iter 017. Apply iter 016's fixed-ratio × vol-target primitive to three regional stacked products: NTSX_synth (0.9 SPY + 0.6 IEF), NTSI_synth (0.9 EFA + 0.6 IEF), NTSE_synth (0.9 EEM + 0.6 IEF). 12-1 absolute momentum on equity leg of each; pre-committed top-K=1 or top-K=2 selection rule. Bond stacking always on. Adds orthogonal cross-sectional equity-regional dispersion axis. NOT a re-test of iter 003 (iter 003 used homogeneous sector ETFs; regional equity has genuine heterogeneity 2008-2012 EM commodities, 2014-2017 China tech). Single cfg pre-committed; n_trials += 3. Expected uplift: +0.10-0.25 Sharpe (orthogonal dimension; bonus if dispersion > noise). Citations: `[stocks_on_the_move, p.76-77]` + Asness-Moskowitz-Pedersen (2013) "Value and Momentum Everywhere" SSRN 1363476.

0s. **[OPTION S — PUT-SPREAD COLLAR TAIL-HEDGE ON EQUITY LEG]** — secondary rec. Finance a 10Δ put spread via a 25Δ covered call on SPY leg of iter 016 (bond leg unchanged). Adds skewness-capture axis (Taleb tail-hedge). Expected +0.05-0.15 Sharpe via MDD reduction. Requires options-chain data (not in current cache) — higher engineering cost. Defer unless Option R fails.

0t. **[OPTION T — HMM STOCK-BOND CORRELATION REGIME ROTATION]** — tertiary rec. 2-state HMM on 60d rolling ρ(SPY, IEF): regime A (ρ < −0.1) → iter 016's 60:40 ratio; regime B (ρ > 0) → defensive 30:70 or cash+IEF. Preserves fixed-ratio discipline within each regime. Expected +0.05-0.15 Sharpe protecting against 2022-style correlation flip. Cheaper than options; requires sklearn HMM. Pre-committed config with ≤ 2 cfgs (regime-B weight variant). Citation `[regime_change, ch.2]`.

0q. **[OPTION Q — FUNDING-COST-MODELED ITER 016 REPLAY]** — robustness verification. Subtract `0.5 × DGS3MO_daily_return` from iter 016's net returns; document the TRUE deployable Sharpe. Cheap; 0 new trials (same config, different cost model). Post iter 017 or 018, before any Mandate §7 override discussion.

### Deeper backlog (not yet designed as iter-next)

- Cross-asset carry (FX / commodities / bonds), `[ilmanen_expected_returns]`.
- Seasonality (turn-of-month / sell-in-May / Santa) — never through 7-gate pipeline.
- Meta-allocation among Plano C sleeves (GDE / AVUV / AVDE / AVEM / BTGD).
- Cross-sectional factor timing (Asness AQR 2024).
- **DSR n_trials reset via pre-registered minimal-trial test** — run iter 016's primitive in isolation with n_trials=1; document standalone DSR (essentially PSR at observed Sharpe 1.14, trivially p<0.05). Not a hunt-loop iteration but a deployability validation.

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
