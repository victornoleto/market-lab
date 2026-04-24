---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 14
winners_found: 0
status: iterating
latest_iteration: "014-2026-04-24-1642"
cumulative_n_trials: 4255
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
| 1 | **008** | 🥈 PROMISING | **74** | `vt15_L21_cap20` (2-leg SPY+TLT, single ex-ante) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | hunt-loop co-high; 6/6/6 gates; 4/5 winner; DSR p=0.332 only fail |
| 1 | **010** | 🥈 PROMISING | **74** | `vt15_L21_cap20_3leg` (3-leg SPY+TLT+GLD) | `[risk_parity, p.10-11]` + Asness-Frazzini-Pedersen 2012 | ties iter 008 → blend family ceiling |
| 3 | 006 | 🥈 PROMISING | 67 | `vt15_L21_cap20` (12-cfg grid) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | first blend; killed by grid PBO 0.690 |
| 4 | 009 | 🥈 PROMISING | 64 | `vt15_L21_cap20 + ts_inv21_h50` | `[regime_change, p.5-6]` + Estrella-Mishkin 1998 | 21d EMA erased T10Y3M lead-time; 100% overlap |
| 4 | 013 | 🥈 PROMISING | **64** | `vt15_L21_cap20 + meta_lr_rho60_vixz252` | `[advances_fin_ml, ch.3]` + López de Prado 2018 | LR meta vol-proxy features redundant with vol-scaling |

*(iter 001 ~35/100 approximate; back-fill in `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iteration in full 6-field format; older entries compressed to
3 lines (Result + Lesson + iter-dir pointer) once the file approaches
the 18 KB ceiling. Full hypothesis, citations, scope and score
breakdown for compressed iters are recoverable from
`iterations/NNN-*/hypothesis.md` + `verdict.json` + `final_report.md`.

### 014 — 2026-04-24 — EBP (GZ2012) credit-cycle overlay on iter 008 blend — **pre-val screen FAIL** (❌ FAIL, 0/100, Kill #PV, 0 DSR committed)
- **Result:** Pre-validation screen (novel methodology: 60d rolling |ρ(EBP_z, realised σ²_port)| > 0.30 exceed frac > 20% → abort) FAILs all 3 ds — exceed_frac edu/spy/ndx **0.684/0.691/0.706** (3.4× over cap), max|ρ| 0.96/0.96/0.94, mean|ρ| 0.47/0.47/0.48. No backtest run; cumulative_n_trials unchanged 4255. Pytest baseline 823→832 (+9 TDD specs). Score 0/25 0/25 0/15 0/15 0/15 0/5 (nothing measured — pre-val abort precedes gates).
- **Lesson:** EBP's GZ2012 residual does NOT decouple from blend σ²_port at 60d scale — fourth consecutive overlay failure on iter 008's blend (009 T10Y3M sym, 012 T10Y3M asym, 013 LR meta, 014 EBP credit) with same cointegration diagnostic. **Overlay family on this mechanism is CLOSED.** Pre-val gate is now mandatory on future overlay/meta-label proposals. Next iter must change MECHANISM: Option G (return-stacked ETF), cross-sectional factor momentum, or options-skew on plain SPY. See `iterations/014-2026-04-24-1642-ebp-credit-overlay-blend/`.

### 013 — 2026-04-24 — Meta-labeling LR classifier w/ ρ+VIX features on iter 008 blend (🥈 PROMISING, 64/100, Kill #3)
- **Result:** Sharpe edu/spy/ndx 0.853/0.990/1.007 (Δ vs iter 008 −0.012/−0.010/−0.014; 1/3 clears gate), gates 6/7×3, DSR p=0.351 (n=4255), overlap-bottom-20% 100%/100%/62.5% (same as 009/012), p_act std 0.19-0.21, winner 1/5; score 1:10 2:19 3:0 4:15 5:15 6:5.
- **Lesson:** Meta-labeling with vol-proxy features (ρ_60, vix_z) on vol-managed SPY+TLT blend is REDUNDANT with variance-scaling. Three regime-overlay/meta-model approaches (009/012/013) all closed with identical 100%-overlap. See `iterations/013-2026-04-24-1619-meta-labeling-blend/`.

### 012 — 2026-04-24 — Asymmetric T10Y3M equity-leg-only haircut (5d EMA) on iter 008 blend (🥉 MARGINAL, 58/100)
- **Result:** Sharpe edu/spy/ndx 0.824/0.965/0.968 (Δ vs iter 008 −0.041/−0.035/−0.053; only 1/3 clears +0.10 gate), gates 6/7 × 3 ds, DSR worst p=0.410 (n=4252), overlap-bottom-20% 100% edu+spy (same diagnostic as iter 009), winner 0/5; score 1:10 2:19 3:0 4:15 5:10 6:4.
- **Lesson:** **T10Y3M overlay family CLOSED — iter 009 (21d symmetric) + iter 012 (5d asymmetric) span the full 2×2 smoothing × asymmetry matrix, all corners show 100% overlap with variance-scaling de-lever on SPY-based datasets.** Structural cointegration, not parametric. Also in 2022 ρ(SPY,TLT)>0 regime, asymmetric bond-preservation is wrong direction. See `iterations/012-2026-04-24-1556-asymmetric-term-spread-overlay/`.

### 011 — 2026-04-24 — Weekly 3-leg blend (🥉 MARGINAL, 52/100, Kill #1+#3)
- **Result:** Sharpe edu/spy/ndx 0.942/1.019/0.898 (Δ weekly-bench +0.277/+0.087/−0.109; only 1/3 clears gate), gates 5/6/5, DSR worst p=0.515 (n=4249 — REGRESSES vs iter 010 daily 0.368), MDD 47/47/49% (+10-14pp vs iter 010), cap-hit 86%→95%, turnover UP 10/yr→13.6/yr per leg, winner 3/5; score 1:10 2:17 3:0 4:15 5:5 6:5.
- **Lesson:** Vol-managed variance-targeting REQUIRES daily cadence. DSR theoretical attack via T reduction cancels periodic-Sharpe growth at first order; second-order terms make DSR WORSE. **DSR-ceiling attacks via timeframe change are STRUCTURALLY UNAVAILABLE for this mechanism.** See `iterations/011-2026-04-24-1527-weekly-three-leg-blend/`.

### 010 — 2026-04-24 — 3-leg SPY+TLT+GLD vol-managed blend daily (🥈 PROMISING, 74/100)
- **Result:** Sharpe edu/spy/ndx 0.989/1.040/0.995 (Δ+0.358/+0.140/+0.040); gates 6/6/5; DSR worst p=0.368 (n=4246); CAGR+MDD floor 3/3; winner 4/5; score 1:20 2:19 3:0 4:15 5:15 6:5.
- **Lesson:** Vol-managed blend family saturates ~Sharpe 1.00 regardless of leg count (N=2 iter 008 = N=3 iter 010 = 74/100). GLD adds +0.12 edu / +0.04 spy / −0.03 ndx. **Leg-count NOT the ceiling — DSR at cumulative n_trials is.** See `iterations/010-2026-04-24-1506-three-asset-spy-tlt-gld-blend/`.

### 009 — 2026-04-24 — T10Y3M 21d-EMA symmetric haircut overlay on iter 008 blend (🥈 PROMISING, 64/100, Kill #3)
- **Result:** Sharpe edu/spy/ndx 0.836/0.979/1.007 (Δ−0.029/−0.021/−0.014 vs iter 008); only 1/3 clears +0.10 gate; gates 6/6/6; DSR worst p=0.36; winner 3/5; score 1:10 2:19 3:0 4:15 5:15 6:5.
- **Lesson:** 21d EMA smoothing ERASED T10Y3M's 6-18m lead-time → gate fires concurrently with blend's vol-de-lever (100% overlap bottom-20% scale on edu+spy; 40% ndx). SUBSEQUENTLY iter 012 tested raw/5d+asymmetric — SAME 100% overlap → T10Y3M overlay family CLOSED. See `iterations/009-*/`.

### 008 — 2026-04-24 — Single-cfg ex-ante vol-managed SPY+TLT blend (🥈 PROMISING, 74/100)
- **Result:** Sharpe edu/spy/ndx 0.865/1.000/1.021 (Δ+0.203/+0.104/+0.070); gates 6/6/6 all ds (cross-ds bonus); DSR worst p=0.332 (n=4240); G1 N=1 vacuous PASS; G6 robustness 9/9; ρ_stockbond −0.31/−0.30/−0.23; winner 4/5; score 1:20 2:19 3:0 4:15 5:15 6:5.
- **Lesson:** Iter 006's blend edge IS structural (not grid-selected); G1 neutralized by N=1 design lifts score 67→74 (new high). **DSR is now SOLE killer** — requires Sharpe uplift ≳0.30 to clear, unreachable from this mechanism alone. See `iterations/008-2026-04-24-1411-single-cfg-ex-ante-blend/`.

### 007 — 2026-04-24 — Vol-managed blend × 12-1 momentum overlay (🥉 MARGINAL, 50/100, Kill #1 + #3)
- **Result:** Top cfg `mom252_skip21` Sharpe edu/spy/ndx 0.916/0.941/0.872 (Δ+0.254/+0.041/−0.083 — REGRESS vs iter 006 on real data); gates edu/spy/ndx 5/5/4; G1 PBO 0.643/0.762/0.746 FAIL all 3 (compound mechanism overfit-sensitive even on 3-cfg ex-ante grid); G6 ndx CI −0.001 FAIL; G7 0.03-0.07pp; MDD reduced 2-5pp (overlay finds regime info but CAGR drop > MDD gain); winner 0/5; score 1:10/25 2:15/25 3:0/15 4:10/15 5:15/15 6:0/5.
- **Lesson:** **Momentum overlay REDUNDANT with variance-scaling on a vol-managed blend** — both target equity-vol regime (Gayed: SPY below-MA has 2-3× vol). Moreira-Muir Table IV's vol-managed × momentum uplift does NOT replicate on a vol-managed BLEND (inverse-variance weighting + variance-scaling already capture momentum's signal). Compounding needs ORTHOGONAL signals (carry, macro, meta-labeling), not correlated. See `iterations/007-*/`.

### 006 — 2026-04-24 — Vol-managed SPY+TLT blend, 12-cfg grid (🥈 PROMISING, 67/100, Kill #3)
- **Result:** Top cfgs Sharpe edu/spy/ndx 0.929/1.000/1.021 (Δ+0.268/+0.100/+0.066); gates 5/5/6 (all meet §0 minimums + cross-ds bonus); CAGR + MDD floor 3/3 (first time); G1 PBO 0.690/0.690/0.472 FAIL (12-cfg grid inflates PBO vs iter 005's 0.238 single-asset); G2 DSR p=0.20-0.33 FAIL; G6 +0.175 to +0.286 all positive; G7 0.03-0.05pp; ρ_stockbond −0.23/−0.30/−0.31 (diversification premise confirmed); winner 4/5; score 1:20/25 2:17/25 3:0/15 4:15/15 5:15/15 6:0/5.
- **Lesson:** Cross-asset diversification as compounding mechanism WORKS — first +0.10 gate clear on 2 ds AND first 3/3 × 3/3 on CAGR + MDD floors. Structural cost: 12-cfg grid inflates PBO. Next: pre-commit single cfg (no grid, no PBO issue) OR compound with momentum overlay. See `iterations/006-*/`.

### 005 — 2026-04-24 — Moreira-Muir σ⁻² variance-scaling on SPY/QQQ (🥉 MARGINAL, 59/100)
- **Result:** Top cfg `vt20_L21_cap15` Sharpe edu/spy/ndx 0.849/0.981/1.052 (Δ+0.167/+0.081/+0.097); gates **6/7 on ALL 3 ds** (first hunt-loop cross-ds §0 meet); G1 PBO edu 0.571 FAIL, spy 0.238 / ndx 0.147 (cleanest); G2 DSR **edu PASS p=0.044** (first DSR-clear); G6 +0.35/+0.21/+0.21; G7 0.02-0.04pp; winner 0/5 (ndx Δ+0.097 misses +0.10 by 0.003); score 1:10/25 2:19/25 3:0/15 4:15/15 5:15/15 6:0/5.
- **Lesson:** Moreira-Muir +0.20-0.40 uplift does NOT replicate on single-asset SPY/QQQ (only +0.01 over iter 004). **Single-asset vol-adaptation family saturated at +0.08-0.10 regardless of exponent σ⁻¹/σ⁻².** Only path through is compounding mechanism (cross-asset or signal overlay). See `iterations/005-*/`.

### Iters 001-004 (compressed; full detail in iter dirs)

- **001** (NEAR_FAIL ~35) — Crash-protected LETF trend, 4020 cfgs, 0/16 cross-ds winners. See `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md`.
- **002** (FAIL 17) — Clenow 10bps ATR-risk-parity on 11 SPDR sectors → 63-75% cash drag (ATR sized for stocks).
- **003** (FAIL 7) — Clenow adjusted-slope × R² equal-notional on 11 sectors; ≤20-asset homogeneous ETF universe lacks ranking signal.
- **004** (MARGINAL 51) — Single-asset vol-scaling SPY σ⁻¹ (Carver). 6/7 gates spy+ndx, G6 first-ever pass, MDD −6/−9pp; Sharpe edge +0.08-0.15 (below +0.10 spy).

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iterations.

Consumed (DEAD_ENDS or saturated): sector rotation 1/K + Clenow (002/003), single-asset vol-scaling (004/005), momentum overlay on vol-managed blend (007 redundant), iter 006 single-cfg verification (008 confirmed structural), T10Y3M overlay entire 2×2 quadrant FALSIFIED (009 symmetric+21d heavy + 012 asymmetric+5d light), 3-leg blend daily (010 ties iter 008 — blend family ceiling), weekly-rebalance blend (011 — daily cadence required), **Option C vol-proxy meta-labeling (iter 013)**, **Option E EBP credit-cycle overlay (iter 014 — pre-val rejected, |ρ|>0.3 on 68-71% bars)**.

### Iter 015 candidates (ranked by structural novelty)

**Framing:** 4 consecutive overlays on iter 008 blend failed with same cointegration diagnostic (009/012/013/014). Overlay family CLOSED — iter 015 must change MECHANISM, not decorate iter 008 again. Novel methodology from iter 014: **pre-validation screen (60d |ρ(feature, σ²_port)| > 0.30 exceed > 20% → abort)** — mandatory for any future overlay/meta-label on a vol-managed blend.

0k. **[OPTION G — RETURN-STACKED ETF ROTATION]** — PRIMARY rec. NTSX/NTSI/NTSE (90% equity + 60% UST futures stacked). New primitive vs iter 008's explicit vol-scaling. `[risk_parity, p.5]` + `[leverage_for_the_long_run, p.19-20]`. NTSX launched 2018-08; NTSI/NTSE 2021-02 — synthetic proxies (90% SPY/EFA/EEM + 60% IEF) for pre-2021.

0m. **[CROSS-SECTIONAL FACTOR MOMENTUM]** — skip 2-leg universe. MTUM/QUAL/VLUE/USMV/SIZE/SPMO (heterogeneous factor tilts, NOT sector ETFs — iter 003 killed those on homogeneity). 12-1 ranking momentum across factors. Cross-sectional axis, not time-series. `[ml_for_algo_trading, ch.4]` + `[advances_fin_ml, ch.7]`.

0n. **[OPTIONS SKEW / VIX TERM SIGNAL ON PLAIN SPY]** — single-asset primary (no blend → no σ²_port cointegration). VIX/VIX3M ratio or put-call skew on plain SPY daily. `[volatility_trading, ch.4-5]`. Tests options-implied axis (iter 013 flagged as potentially orthogonal).

0l. **[OPTION H — META-LABELING WITH PRE-SCREENED FEATURES]** — deprioritised vs G/cross-sec. Given iter 014 killed EBP, credit-adjacent features likely also fail pre-val; features must come from genuinely different axis (cross-sectional, options-implied).

### Deeper backlog (not yet designed as iter-next)

- Cross-asset carry (FX / commodities / bonds), `[ilmanen_expected_returns]`.
- Seasonality (turn-of-month / sell-in-May / Santa) — never through 7-gate pipeline.
- Options tail-hedging (put-spread collars).
- HMM regime-switching on stock-bond correlation (`[regime_change, ch.2]`).
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
- 3-leg SPY+TLT+GLD daily on `vt15_L21_cap20_3leg` — ties iter 008 at 74/100, blend family ceiling (iter 010); DO NOT re-test minor variations
- Weekly-rebalance 3-leg blend (W-FRI, 4w lookback) — vol-managed REQUIRES daily cadence; MDD +10-14 pp, DSR WORSE, turnover UP (iter 011); DO NOT re-test other weekly params or monthly cadence
- T10Y3M asymmetric equity-leg-only haircut, 5d EMA on iter 008 blend — SAME 100% gate-fire/bottom-20%-scale overlap as iter 009 symmetric 21d (iter 012); **2×2 quadrant (smoothing × asymmetry) fully closed**; redundancy is structural cointegration, not parametric; DO NOT re-test any T10Y3M overlay variant on this mechanism
- Meta-labeling LR with ρ_stockbond + VIX_z on iter 008 blend — 100% bottom-20% overlap edu+spy same as iter 009/012 (iter 013); vol-proxy features cointegrate with σ²_port at business-cycle scale
- EBP (GZ2012 residual) credit-cycle binary haircut overlay on iter 008 blend — pre-val screen rejects all 3 ds (iter 014): 60d rolling |ρ(EBP_z, σ²_port)| > 0.30 on 68-71% of bars (mean≈0.47, max 0.96). **Fourth overlay failure on iter 008 blend (009 T10Y3M sym / 012 T10Y3M asym / 013 LR meta / 014 EBP) — overlay family CLOSED; pre-validation gate mandatory for any future overlay/meta-label on vol-managed blend.**

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
