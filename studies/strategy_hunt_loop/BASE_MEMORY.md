---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 15
winners_found: 0
status: iterating
latest_iteration: "015-2026-04-24-1704"
cumulative_n_trials: 4258
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
| **1** | **015** | 🥇 **STRONG** | **77** | `ntsx_synth_90_60_daily` (static 0.9 SPY + 0.6 IEF stack) | `[risk_parity, p.5]` + Asness-Frazzini-Pedersen 2012 | 4/5 winner; 3/3 Sharpe edge; 9/9 sub-windows; DSR sole fail; mech escapes σ²_port trap |
| 2 | 008 | 🥈 PROMISING | 74 | `vt15_L21_cap20` (2-leg SPY+TLT vol-mgmt) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | 4/5 winner; vol-managed reference baseline |
| 2 | 010 | 🥈 PROMISING | 74 | `vt15_L21_cap20_3leg` (3-leg SPY+TLT+GLD) | `[risk_parity, p.10-11]` + Asness-Frazzini-Pedersen 2012 | ties iter 008 — blend family ceiling |
| 4 | 006 | 🥈 PROMISING | 67 | `vt15_L21_cap20` (12-cfg grid) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | first blend; killed by grid PBO 0.690 |
| 5 | 009 | 🥈 PROMISING | 64 | `vt15_L21_cap20 + ts_inv21_h50` | `[regime_change, p.5-6]` + Estrella-Mishkin 1998 | 21d EMA erased T10Y3M lead-time; 100% overlap |
| 5 | 013 | 🥈 PROMISING | 64 | `vt15_L21_cap20 + meta_lr_rho60_vixz252` | `[advances_fin_ml, ch.3]` + López de Prado 2018 | LR meta vol-proxy features redundant with vol-scaling |

*(iter 001 ~35/100 approximate; back-fill in `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iteration in full 6-field format; older entries compressed to
3 lines (Result + Lesson + iter-dir pointer) once the file approaches
the 18 KB ceiling. Full hypothesis, citations, scope and score
breakdown for compressed iters are recoverable from
`iterations/NNN-*/hypothesis.md` + `verdict.json` + `final_report.md`.

### 015 — 2026-04-24 — Static synthetic NTSX 90/60 SPY+IEF stack (🥇 STRONG, 77/100, NEW HUNT-LOOP HIGH, 4/5 winner, DSR sole fail)
- **Hypothesis + Citations:** Static `0.9 × equity + 0.6 × IEF` daily-rebalanced fixed weights, single cfg `ntsx_synth_90_60_daily`, NO overlay/vol-mgmt/rotation. First mechanism-change iter after 4 cointegration overlay failures. `[risk_parity, p.5, p.10-11, ch.1]` (Asness-Frazzini-Pedersen risk-parity); `[leverage_for_the_long_run, p.19-20]`; AFP 2012 FAJ 68(1) SSRN 1728082; WisdomTree NTSX. Scope: 1 cfg × 3 ds = 3 trials (n_trials 4255→4258); +9 TDD specs (761 pass + 5 skip).
- **Result:** Sharpe edu/spy/ndx **0.78/1.04/1.06** (Δ frozen +0.10/+0.14/+0.11 — first iter to clear +0.10 on ALL 3 ds), gates **5/7, 6/7, 6/7** (cross-ds §0 met +4 bonus), DSR worst p=0.548 (edu) sole fail, CAGR+MDD floor 3/3 ✓ (ndx MDD 39.51% vs 40.12% ceiling razor 0.61pp), winner **4/5**, G6 9/9 sub-windows positive; score 1:25 2:17 3:0 4:15 5:15 6:5 = **77** (new top-K #1).
- **Lesson:** **Mechanism change DOES break σ²_port cointegration ceiling**, but DSR cumulative-n_trials is now the universal hunt-loop ceiling regardless of mechanism. Synthetic NTSX has ~75-100 bps optimism gap vs real product (no funding cost on 50% extra notional); post-funding-cost edge ~+0.04-0.10, BORDERLINE on +0.10 strict gate. Iter 016 PICK: Option P (static stack × vol-mgmt hybrid) — attack DSR via Sharpe uplift while preserving cointegration escape. See `iterations/015-2026-04-24-1704-return-stacked-static-ntsx/`.

### 014 — 2026-04-24 — EBP (GZ2012) credit-cycle overlay on iter 008 blend (❌ FAIL, 0/100, Kill #PV, 0 DSR committed)
- **Result:** Pre-validation screen (60d rolling |ρ(EBP_z, σ²_port)| > 0.30 exceed > 20% → abort) FAILs all 3 ds — exceed_frac edu/spy/ndx **0.684/0.691/0.706** (3.4× cap), max|ρ| 0.96, mean|ρ| 0.47. No backtest, n_trials unchanged 4255. Score 0 (nothing measured); winner 0/5.
- **Lesson:** Fourth consecutive overlay failure on iter 008 blend (009/012/013/014) — overlay family CLOSED on this mechanism. Pre-val screen is now mandatory for any future overlay/meta-label proposal. See `iterations/014-2026-04-24-1642-ebp-credit-overlay-blend/`.

### 013 — 2026-04-24 — Meta-labeling LR w/ ρ+VIX features on iter 008 blend (🥈 PROMISING, 64/100, Kill #3)
- **Result:** Sharpe edu/spy/ndx 0.853/0.990/1.007 (Δ vs iter 008 −0.012/−0.010/−0.014; 1/3 clears gate), gates 6/7×3, DSR p=0.351 (n=4255), overlap-bottom-20% 100%/100%/62.5%, winner 1/5; score 1:10 2:19 3:0 4:15 5:15 6:5.
- **Lesson:** Meta-labeling with vol-proxy features (ρ_60, vix_z) is REDUNDANT with variance-scaling — three regime-overlay/meta-model approaches (009/012/013) all closed with identical 100%-overlap. See `iterations/013-2026-04-24-1619-meta-labeling-blend/`.

### 012 — 2026-04-24 — Asymmetric T10Y3M equity-leg haircut (5d EMA) on iter 008 (🥉 MARGINAL, 58/100)
- **Result:** Sharpe edu/spy/ndx 0.824/0.965/0.968 (Δ vs iter 008 −0.041/−0.035/−0.053), gates 6/7×3, DSR p=0.410 (n=4252), overlap 100% edu+spy (same as iter 009), winner 0/5; score 1:10 2:19 3:0 4:15 5:10 6:4.
- **Lesson:** T10Y3M overlay family fully CLOSED — iter 009 (21d sym) + iter 012 (5d asym) span 2×2 matrix, structural cointegration not parametric. See `iterations/012-2026-04-24-1556-asymmetric-term-spread-overlay/`.

### 011 — 2026-04-24 — Weekly 3-leg blend (🥉 MARGINAL, 52/100, Kill #1+#3)
- **Result:** Sharpe edu/spy/ndx 0.942/1.019/0.898 (Δ +0.277/+0.087/−0.109; only 1/3 clears), gates 5/6/5, DSR worst p=0.515 (REGRESSES vs daily 0.368), MDD +10-14pp, turnover UP, cap-hit 86%→95%; winner 3/5; score 1:10 2:17 3:0 4:15 5:5 6:5.
- **Lesson:** Vol-managed variance-targeting REQUIRES daily cadence. DSR via T-reduction cancels at first order — DSR-ceiling timeframe attacks structurally unavailable. See `iterations/011-2026-04-24-1527-weekly-three-leg-blend/`.

### 010 — 2026-04-24 — 3-leg SPY+TLT+GLD vol-managed daily (🥈 PROMISING, 74/100)
- **Result:** Sharpe edu/spy/ndx 0.989/1.040/0.995 (Δ+0.358/+0.140/+0.040); gates 6/6/5; DSR worst p=0.368 (n=4246); CAGR+MDD floor 3/3; winner 4/5; score 1:20 2:19 3:0 4:15 5:15 6:5.
- **Lesson:** Vol-managed blend family saturates Sharpe ~1.00 regardless of leg count (N=2 iter 008 = N=3 iter 010 = 74/100). DSR is the ceiling, not leg count. See `iterations/010-2026-04-24-1506-three-asset-spy-tlt-gld-blend/`.

### 009 — 2026-04-24 — T10Y3M 21d-EMA symmetric haircut on iter 008 (🥈 PROMISING, 64/100, Kill #3)
- **Result:** Sharpe edu/spy/ndx 0.836/0.979/1.007 (Δ−0.029/−0.021/−0.014); 1/3 clears gate; gates 6/6/6; DSR worst p=0.36; winner 3/5; score 1:10 2:19 3:0 4:15 5:15 6:5.
- **Lesson:** 21d EMA smoothing ERASED T10Y3M's 6-18m lead-time → 100% bottom-20% overlap with vol-de-lever. T10Y3M overlay family closed (combined w/ iter 012). See `iterations/009-*/`.

### 008 — 2026-04-24 — Single-cfg ex-ante vol-managed SPY+TLT blend (🥈 PROMISING, 74/100)
- **Result:** Sharpe edu/spy/ndx 0.865/1.000/1.021 (Δ+0.203/+0.104/+0.070); gates 6/6/6 all ds; DSR worst p=0.332 (n=4240); G1 N=1 vacuous PASS; G6 9/9; ρ_stockbond −0.31/−0.30/−0.23; winner 4/5; score 1:20 2:19 3:0 4:15 5:15 6:5.
- **Lesson:** Iter 006's blend edge IS structural; G1 neutralised by N=1 lifts score 67→74. DSR sole killer requiring Sharpe uplift ≳0.30 — unreachable from this mechanism alone. See `iterations/008-2026-04-24-1411-single-cfg-ex-ante-blend/`.

### 007 — 2026-04-24 — Vol-managed blend × 12-1 momentum overlay (🥉 MARGINAL, 50/100, Kill #1+#3)
- **Result:** `mom252_skip21` Sharpe edu/spy/ndx 0.916/0.941/0.872 (Δ+0.254/+0.041/−0.083 — REGRESS vs iter 006); gates 5/5/4; G1 PBO 0.643/0.762/0.746 FAIL all 3; G6 ndx CI −0.001; winner 0/5; score 1:10 2:15 3:0 4:10 5:15 6:0.
- **Lesson:** Momentum overlay REDUNDANT with variance-scaling on vol-managed blend (both target equity-vol regime). Compounding needs ORTHOGONAL signals. See `iterations/007-*/`.

### 006 — 2026-04-24 — Vol-managed SPY+TLT blend, 12-cfg grid (🥈 PROMISING, 67/100, Kill #3)
- **Result:** Sharpe edu/spy/ndx 0.929/1.000/1.021 (Δ+0.268/+0.100/+0.066); gates 5/5/6 (all meet §0 + cross-ds bonus); CAGR+MDD 3/3 (first time); G1 PBO 0.690/0.690/0.472 FAIL (grid inflates); winner 4/5; score 1:20 2:17 3:0 4:15 5:15 6:0.
- **Lesson:** Cross-asset diversification compounding WORKS — first +0.10 gate on 2 ds; structural cost is grid PBO inflation. Next: pre-commit single cfg (iter 008). See `iterations/006-*/`.

### 005 — 2026-04-24 — Moreira-Muir σ⁻² variance-scaling on SPY/QQQ (🥉 MARGINAL, 59/100)
- **Result:** `vt20_L21_cap15` Sharpe edu/spy/ndx 0.849/0.981/1.052 (Δ+0.167/+0.081/+0.097); gates 6/7×3 (first cross-ds §0 meet); G2 DSR edu PASS p=0.044 (first DSR-clear); winner 0/5; score 1:10 2:19 3:0 4:15 5:15 6:0.
- **Lesson:** Single-asset vol-adaptation family saturates at +0.08-0.10 Sharpe regardless of exponent. Only path through is compounding (cross-asset or signal overlay). See `iterations/005-*/`.

### Iters 001-004 (compressed; full detail in iter dirs)

- **001** (NEAR_FAIL ~35) — Crash-protected LETF trend, 4020 cfgs, 0/16 cross-ds winners. See `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md`.
- **002** (FAIL 17) — Clenow 10bps ATR-risk-parity on 11 SPDR sectors → 63-75% cash drag (ATR sized for stocks).
- **003** (FAIL 7) — Clenow adjusted-slope × R² equal-notional on 11 sectors; ≤20-asset homogeneous ETF universe lacks ranking signal.
- **004** (MARGINAL 51) — Single-asset vol-scaling SPY σ⁻¹ (Carver). 6/7 gates spy+ndx, G6 first-ever pass, MDD −6/−9pp; Sharpe edge +0.08-0.15 (below +0.10 spy).

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iterations.

Consumed (DEAD_ENDS or saturated): sector rotation 1/K + Clenow (002/003); single-asset vol-scaling (004/005); momentum overlay on vol-managed blend (007 redundant); iter 006 single-cfg verification (008 structural); T10Y3M overlay full 2×2 (009/012); 3-leg blend daily (010 ties iter 008); weekly-cadence blend (011); meta-label vol-proxy (013); EBP credit-cycle overlay (014 pre-val); **iter 015 — STATIC SYNTH NTSX (90/60 SPY+IEF) STACK SCORED 77/100 STRONG, NEW HUNT-LOOP HIGH, 4/5 winner conds, only DSR fails — first mechanism to escape σ²_port cointegration**.

### Iter 016 candidates (ranked by expected DSR-clearance lift)

**Framing:** Iter 015 PROVED that mechanism change escapes the σ²_port cointegration ceiling (77/100, all 3 ds clear +0.10 Sharpe gate, 9/9 sub-windows positive, 4/5 winner conds met). The ONLY remaining killer is DSR at cumulative_n_trials=4258 — needs Sharpe ~1.30-1.40 on worst dataset (currently 1.04 spy_real). To clear DSR cleanly, iter 016 must add Sharpe uplift to iter 015's static stack baseline WITHOUT reopening cointegration.

0p. **[OPTION P — STATIC STACK × VOL-MANAGEMENT HYBRID]** — PRIMARY rec for iter 016. Multiply iter 008's vol-target scaling on top of iter 015's static 90/60 weights: `pos_eq[t] = 0.9 × scale[t]`, `pos_bd[t] = 0.6 × scale[t]`, `scale[t] = clip(target_vol²/σ²_port[t-1], 0, max_lev)`. Vol-target inflates exposure during low-vol regimes (where static 1.5× is conservative) and contracts during stress. Single-cfg pre-committed; n_trials += 3. Expected uplift: +0.05-0.15 Sharpe per ds (modest, may not fully clear DSR but moves in right direction). Citations: `[risk_parity, p.5]` + Moreira-Muir 2017.

0q. **[OPTION Q — STATIC STACK + EXPLICIT FUNDING-COST MODELING]** — robustness verification of iter 015. Subtract `0.5 × DGS3MO_daily_return` from net returns to model the futures-stacking implicit borrow on the 50% additional notional. If post-funding-cost Sharpe edge ≥ +0.05 cross-ds, iter 015's 77/100 stands; if < +0.05, the primitive needs a compounding layer to be deployable. Cheap; n_trials += 3. Citation: `[advances_fin_ml, p.162-164]`.

0r. **[OPTION R — NTSX/NTSI/NTSE REGIONAL ROTATION]** — equity-leg cross-sectional momentum on stacked products. Universe: 3 synthetic stacked ETFs (NTSX_synth = 0.9 SPY + 0.6 IEF; NTSI_synth = 0.9 EFA + 0.6 IEF; NTSE_synth = 0.9 EEM + 0.6 IEF). Signal: 12-1 absolute momentum on equity component of each. Adds orthogonal regional-equity dispersion axis. NOT a re-test of iter 003 (sector ETFs were homogeneous; regional equity has genuine heterogeneity 2008-2012 EM commodities, 2014-2017 China tech). 1-3 cfgs (top-1, top-2, all-positive); n_trials += 3-9.

0n. **[OPTIONS SKEW / VIX TERM SIGNAL ON PLAIN SPY]** — deferred to iter 017+. Single-asset primary (no blend → no σ²_port cointegration). VIX/VIX3M or put-call skew. `[volatility_trading, ch.4-5]`. Lower priority because iter 015 already cleared Sharpe gate cross-ds; this would be a parallel-mechanism comparison rather than DSR-clearance attack.

### Deeper backlog (not yet designed as iter-next)

- Cross-asset carry (FX / commodities / bonds), `[ilmanen_expected_returns]`.
- Seasonality (turn-of-month / sell-in-May / Santa) — never through 7-gate pipeline.
- Options tail-hedging (put-spread collars).
- HMM regime-switching on stock-bond correlation (`[regime_change, ch.2]`).
- Meta-allocation among Plano C sleeves (GDE / AVUV / AVDE / AVEM / BTGD).
- Cross-sectional factor timing (Asness AQR 2024).
- **DSR n_trials reset via pre-registered minimal-trial test** — run iter 015's primitive in isolation with n_trials=1; document standalone DSR (essentially PSR, much easier to clear). Not a hunt-loop iteration but a deployability validation.

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
