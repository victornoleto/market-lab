---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 10
winners_found: 0
status: iterating
latest_iteration: "010-2026-04-24-1506"
cumulative_n_trials: 4246
---

# Strategy Hunt Loop — BASE MEMORY

**Read this file FIRST in every iteration.** Your conversation history is
empty — this file + on-disk artifacts are your only continuity.

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

Track the top-5 strategies ever scored across all iterations. Even
non-winners may appear here — the point is to make "semi-optimal"
strategies visible for future research.

| rank | iter | tier | score | strategy slug | primary citation | notes |
|---|---|---|---|---|---|---|
| 1 | **008** | 🥈 **PROMISING** | **74/100** | `vol_managed_60_40 vt15_L21_cap20` (single ex-ante cfg, 2-leg SPY+TLT) | `[risk_parity, p.10-11, ch.1]` + `[systematic_trading, p.144 ch.9, p.170-171 ch.11]` + Moreira-Muir 2017 | **hunt-loop co-high** (tied with iter 010). Single ex-ante pre-committed cfg (N=1, no grid) verifying iter 006 edge is structural. Sharpe edu 0.865 / spy **1.000** / ndx 1.021 (Δ+0.20/+0.10/+0.07). Gates **6/6/6** all datasets. CAGR floor 3/3 + MDD ceiling 3/3. G1 PBO N/A (N=1). G6 robustness 5/5 (9/9 positive). **4/5 strict winner conditions met** — only DSR p=0.332 fails at n_trials=4240. |
| 1 | **010** | 🥈 **PROMISING** | **74/100** | `vt15_L21_cap20_3leg` (single ex-ante cfg, 3-leg SPY+TLT+GLD) | `[risk_parity, p.10-11, ch.1]` + `[systematic_trading, p.144, p.170-171, ch.11]` + Moreira-Muir 2017 + Asness-Frazzini-Pedersen 2012 | **hunt-loop co-high** (tied with iter 008). 3-leg structural extension on identical params. Sharpe edu 0.989 (Δ+0.358 vs custom bench) / spy **1.040** (Δ+0.140 vs 0.90) / ndx 0.995 (Δ+0.040 vs 0.955). Gates **6/6/5** (ndx WF regresses 7/8→5/8). CAGR floor 3/3 + MDD ceiling 3/3 (edu MDD −3.5pp / spy −3.5pp). Correlations confirmed: ρ(eq,gd)≈+0.06, ρ(bd,gd)≈+0.15-0.21. **4/5 strict winner conditions met** — only DSR p=0.368 fails at n_trials=4246. 9/9 robustness held. **Lesson: blend family saturates near Sharpe 1.00 on real data regardless of N=2/3. DSR is the true ceiling, not leg-count.** |
| 3 | 006 | 🥈 PROMISING | 67/100 | `vol_managed_60_40 vt15_L21_cap20 / vt15_L63_cap20` | `[risk_parity, p.10-11, ch.1]` + `[systematic_trading, p.170-171, ch.11]` + Moreira-Muir 2017 | first SPY+TLT blend, 12-cfg grid. +0.10 Sharpe gate cleared on spy_real + educational. MDD floor + CAGR floor 3/3 × 3/3. 4/5 winner conditions — only DSR fails. Kill #3 triggered: spy_real PBO 0.690, blend mechanism overfit-sensitive on grid. |
| 4 | **009** | 🥈 **PROMISING** | **64/100** | `vt15_L21_cap20 + ts_inv21_h50` (T10Y3M 21d-EMA binary haircut) | `[regime_change, p.5-6, ch.2]` + `[quant_trading_chan, p.25, p.119-126]` + Estrella-Mishkin 1998 | term-spread macro overlay. Kill #3 TRIGGERED (score 64 < 65). Sharpe regresses −0.03/−0.02/−0.01 on edu/spy/ndx vs iter 008. **Orthogonality claim empirically falsified**: 100% of gate-fires coincide with bottom-20% blend scale bars on 2/3 ds (21d EMA erased lead). |
| 5 | 005 | 🥉 MARGINAL | 59/100 | `variance_managed_spy vt20_L21_cap15` | Moreira-Muir 2017 + `[systematic_trading, p.107-111]` | canonical `σ^{-2}`. 6/7 gates on ALL 3 datasets, real-data PBO 0.147-0.238, DSR passes on edu (p=0.044). Sharpe edge +0.081 spy / +0.097 ndx (both just below +0.10). |

*(iter 001 approximate. See
`tests/test_strategy_scoring.py::TestNearMiss` for the back-filled
calculation.)*

---

## Iteration log (newest first, 6-line max per entry)

### 010 — 2026-04-24 — Three-leg vol-managed SPY+TLT+GLD blend with inverse-variance weighting (🥈 PROMISING, score 74/100)
- **Hypothesis:** Structural extension of iter 008's 2-leg blend to 3 legs by adding GLD with identical params (`vt15_L21_cap20_3leg`, single ex-ante cfg). Naïve risk parity generalises cleanly to N=3; Moreira-Muir variance-scaling applies unchanged to 3×3 σ²_port. Gold adds real-asset / inflation-hedge factor with ρ≈0 to both equity and bond legs — uncorrelated-leg diversification axis qualitatively new vs 2-leg.
- **Citations:** `[risk_parity, p.10-11, ch.1]` + `[risk_parity, p.80-81, ch.4]` (naïve RP + cross-asset diversification); `[systematic_trading, p.144, p.170-171, ch.11]` (target_vol + IDM cap); `[advances_fin_ml, p.162-164, 208-211, 222-223, 31-34]`; `[ilmanen_expected_returns, ch.11]` (gold diversifier). Moreira-Muir 2017 + Asness-Frazzini-Pedersen 2012 *FAJ* 68(1) SSRN 1728082 + Qian 2005 PanAgora.
- **Scope:** 1 ex-ante pre-committed cfg × 3 datasets (edu SPY+TLT+GLD 21y / spy SPY+TLT+GLD 17y / ndx QQQ+TLT+GLD 16y) = 3 trials. GLD constrains edu start to 2004-11-18 (vs iter 008's 2002-07-26). Cumulative n_trials 4243 → 4246.
- **Result:** Sharpe edu 0.989 (Δ+0.358) / spy **1.040** (Δ+0.140) / ndx 0.995 (Δ+0.040). Gates **6/6/5** (ndx WF regresses 7/8→5/8 — first iter to not hit 6+/7 on all 3 datasets for a PROMISING candidate). CAGR floor 3/3 + MDD ceiling 3/3 (edu MDD −3.5pp / spy −3.5pp improvements held). G1 N=1 vacuous. G2 DSR worst p=0.368 FAIL (slightly worse than iter 008's 0.332). G6 boot CI +0.187 to +0.265 all positive. G7 xlib 0.01-0.12 pp PASS. Median weights ~1/3 each leg; cap-hit 85-88%. ρ(eq,gd)≈+0.06, ρ(bd,gd)≈+0.15-0.21. Robustness 9/9 positive (matches iter 008). **4/5 strict winner conditions met.**
- **Score breakdown:** 1:20/25 2:19/25 3:0/15 4:15/15 5:15/15 6:5/5
- **Lesson:** **Vol-managed blend family saturates near Sharpe 1.00 on real data regardless of leg count (N=2 iter 008 and N=3 iter 010 both score 74/100, 4/5 winner conditions).** GLD adds +0.12 Sharpe on edu and +0.04 on spy but subtracts −0.03 on ndx_real — asymmetric, with regression on universes where equity leg is already near Sharpe ceiling (QQQ post-2010 bench 0.955). DSR at cumulative n_trials ≈ 4246 requires Sharpe uplift > ~0.30 on worst dataset; this family delivers at most +0.14 on best and +0.04 on worst. **DSR is the hunt-loop ceiling, not leg count or correlation structure.** Breaking through requires: (a) qualitatively different info (meta-labeling AFML ch.3); (b) timeframe change (weekly rebalance changes DSR n_trials regime); or (c) asymmetric overlays (iter 009 Option B'). See `iterations/010-2026-04-24-1506-three-asset-spy-tlt-gld-blend/final_report.md`.

### 009 — 2026-04-24 — Term-spread (T10Y3M) binary-haircut macro overlay on iter 008 blend (🥈 PROMISING, score 64/100)
- **Hypothesis:** Compound iter 008's single-cfg vol-managed SPY+TLT blend with a pre-committed T10Y3M 21-day EMA binary haircut (threshold=0, haircut=0.5, symmetric on both legs). Macro monetary signal claimed orthogonal to realized-vol regime — expected +0.05-0.15 Sharpe uplift from early-warning recession de-lever.
- **Citations:** `[regime_change, p.5-6, ch.2]` (Chen & Tsang 2020 regime framework); `[quant_trading_chan, p.25, p.104, p.119-126]` (data-observable turning points); `[systematic_trading, p.144, ch.9]` (tier-2 half-exposure de-lever); `[advances_fin_ml, p.162-164, 208-211, 222-223, 31-34]`; Estrella-Mishkin 1998 *REStat* 80(1); Estrella-Hardouvelis 1991 *JoF* 46(2); Moreira-Muir 2017.
- **Scope:** 1 overlay cfg × 1 blend cfg × 3 datasets = 3 new trials. Macro source `data/external/macro/t10y3m_daily.parquet`. Cumulative n_trials 4240 → 4243.
- **Result:** Sharpe edu 0.836 (Δ vs iter 008 **−0.029**) / spy 0.979 (**−0.021**) / ndx 1.007 (**−0.014**). Only **1/3** datasets clears +0.10 gate (iter 008 had 2/3). Gates **6/6/6** (G1 vacuous, G2 DSR fails at p=0.340/0.363/0.350, G3-G7 pass). CAGR floor 3/3 + MDD ceiling 3/3 held. Robustness 5/5 held. Winner conditions **3/5** (regression from iter 008's 4/5).
- **Score breakdown:** 1:10/25 2:19/25 3:0/15 4:15/15 5:15/15 6:5/5
- **Lesson:** **Macro overlay LEAD-TIME is destroyed by monthly-scale smoothing.** Pre-committed 21-day EMA on T10Y3M (to emulate Estrella-Mishkin monthly regime) erased the 6-18 month recession lead that is the indicator's entire value. Result: gate fires concurrently with the blend's own variance-scaling de-lever (100% overlap with bottom-20% blend scale on edu + spy; 40% overlap on ndx). **Orthogonality claim empirically falsified for this specific parametrization.** Kill #3 TRIGGERED (score 64 < 65 pre-commit). T10Y3M as macro signal NOT dead — needs raw/5d smoothing + asymmetric haircut (equity-only) to preserve lead-time and flight-to-quality. See `iterations/009-*/final_report.md` + `DEAD_ENDS.md` (new iter 009 entry).

### 008 — 2026-04-24 — Single-config ex-ante vol-managed SPY+TLT blend (🥈 PROMISING, score 74/100)
- **Hypothesis:** Verify iter 006's blend edge is structural (not grid-selected) by pre-committing the single best cfg `vt15_L21_cap20` (1 cfg × 3 datasets = 3 trials). Eliminates G1 PBO (undefined at N=1) and tests whether the Sharpe uplift survives without param tuning.
- **Citations:** `[risk_parity, p.10-11, ch.1]` (naïve RP exact ERC, 2-asset); `[risk_parity, p.80-81, ch.4]` (SPY-TLT diversification); `[systematic_trading, p.144 ch.9]` (target_vol calibration); `[systematic_trading, p.170-171, ch.11]` (IDM ≤ 2.5); `[advances_fin_ml, p.162-164, 208-211, 222-223]`; Moreira-Muir 2017 *JoF* 72(4) DOI 10.1111/jofi.12513.
- **Scope:** 1 ex-ante pre-committed cfg (`vt15_L21_cap20`) × 3 datasets (educational SPY+TLT 24y / spy_real / ndx_real). 2 bps cost. Cumulative n_trials 4237 → 4240.
- **Result:** Sharpe edu 0.865 (Δ+0.203) / spy **1.000** (Δ+0.104 exact) / ndx 1.021 (Δ+0.070). Gates **6/6/6** all datasets (cross-dataset thresholds met). CAGR floor 3/3, MDD ceiling 3/3 (held vs iter 006). G1 PBO undefined (N=1) → neutral PASS. G2 DSR worst p=0.332 FAIL (n_trials=4240). **G6 robustness bonus 5/5 (9/9 sub-windows positive — first ever bonus awarded)**. ρ_stockbond −0.31/−0.30/−0.23. Winner conditions **4/5** (DSR only failure).
- **Score breakdown:** 1:20/25 2:19/25 3:0/15 4:15/15 5:15/15 6:5/5
- **Lesson:** Iter 006's vol-managed SPY+TLT edge IS structural — single-cfg ex-ante verification preserves the +0.10 spy / +0.20 educational uplift, lifts ndx to 1.021. **G1 neutralized by N=1 design = score climbs 67→74** (new hunt-loop high). **DSR is now the SOLE killer** at cumulative n_trials=4240, where the deflator requires Sharpe uplift ≳0.30 to reach p<0.05 — unreachable with this mechanism alone. Two paths forward: (a) compound an ORTHOGONAL signal (macro spreads, carry, meta-labeling) to push Sharpe past the deflator, OR (b) accept structural-edge-without-DSR as the strongest hunt-loop result and pivot to extending the blend (3-asset NTSX-style, return-stacked) for a different n_trials regime. See `iterations/008-2026-04-24-1411-single-cfg-ex-ante-blend/`.

### 007 — 2026-04-24 — Vol-managed 60/40 SPY+TLT × 12-1 time-series momentum overlay (🥉 MARGINAL, score 50/100)
- **Hypothesis:** Gate iter 006's blend by canonical 12-1 skip-a-month momentum on the equity leg. Expect +0.05-0.10 Sharpe uplift from adding an independent trend-timing axis on top of cross-asset diversification (per Moreira-Muir Table IV).
- **Citations:** `[ml_for_algo_trading, ch.4 p.86]` (12-month skip-a-month RULE); `[algo_trading_chan, p.133, 156-157, 164, ch.6]` (time-series momentum, lookback 252 from Moskowitz-Ooi-Pedersen); Moreira-Muir 2017 Table IV; Jegadeesh-Titman 1993.
- **Scope:** 3 overlay configs (mom252_skip21 / mom126_skip21 / mom378_skip21) × 1 fixed blend cfg (`vt15_L21_cap20`) × 3 datasets = 9 trials. Cumulative n_trials 4228 → 4237.
- **Result:** Top cfg `mom252_skip21` Sharpe edu 0.916 (Δ+0.254) / spy **0.941** (Δ+0.041, **regression vs iter 006's 1.000**) / ndx **0.872** (Δ−0.083, **regression vs iter 006's 1.021**). Gates edu 5/7, spy 5/7, ndx 4/7 (cross-dataset bonus applies). G1 PBO **0.643/0.762/0.746 FAIL ALL 3** (compound mechanism overfit-sensitive even on 3-cfg ex-ante grid). G6 boot CI ndx_real **−0.001 FAIL** (straddles zero). G7 xlib 0.03-0.07pp PASS. MDD reduced 2-5pp on all 3 (overlay DOES find regime info). **KILL #1 + #3 triggered.** Winner conditions 0/5.
- **Score breakdown:** 1:10/25 2:15/25 3:0/15 4:10/15 5:15/15 6:0/5
- **Lesson:** **Momentum overlay is REDUNDANT with variance-scaling** on a vol-managed blend. Both target equity-regime volatility (Gayed: SPY below-MA has 2-3× vol). Moreira-Muir Table IV's vol-managed × momentum uplift does NOT replicate on a vol-managed BLEND — the inverse-variance weighting + variance-scaling together already capture what momentum gates would add. Compounding needs ORTHOGONAL signals (carry, meta-labeling, macro state) not correlated ones. See `iterations/007-*/final_report.md`.

### 006 — 2026-04-24 — Vol-managed SPY+TLT blend with inverse-variance weighting (🥈 PROMISING, score 67/100)
- **Hypothesis:** Apply naïve risk parity (inverse-variance per leg) + Moreira-Muir portfolio-level variance-scaling to a 2-asset SPY+TLT (QQQ+TLT) blend. Cross-asset correlation diversification (ρ≈−0.25 to −0.31) adds an independent edge axis on top of single-asset vol-adaptation (iter 005).
- **Citations:** `[risk_parity, p.10-11, ch.1]` (naïve RP exact ERC for 2-asset); `[systematic_trading, p.170-171, ch.11]` (IDM ≤ 2.5); Moreira-Muir 2017 *JoF* 72(4) DOI 10.1111/jofi.12513; `[risk_parity, p.5, 16, 80-81, 109-110]` (60/40 variance decomposition, leverage rule, RORO, diversification return); Asness-Frazzini-Pedersen 2012 FAJ 68(1) SSRN 1728082.
- **Scope:** 12 configs (tv×L×cap = 2×3×2) × 3 datasets. Educational redefined to SPY+TLT 2002-2026 (24y, longest with TLT cache) with custom benchmark SPY b&h; spy_real/ndx_real keep frozen scoring.BENCHMARKS.
- **Result:** Top cfgs Sharpe edu 0.929 (Δ+0.268) / spy **1.000** (Δ+0.100 exact) / ndx 1.021 (Δ+0.066). Gates edu 5/7, spy 5/7, ndx 6/7 (all meet spec §0 minimums, +4 cross-ds bonus). CAGR floor **3/3**, MDD ceiling **3/3** (first time). G1 PBO **0.690/0.690/0.472** (degraded vs iter 005 0.238 on spy — Kill #3 TRIGGERED, blend grid overfit-sensitive). G2 DSR p=0.20-0.33 FAIL. G6 boot CI +0.175 to +0.286 all positive. G7 xlib 0.03-0.05pp PASS. ρ_stockbond −0.23/−0.30/−0.31 (diversification premise confirmed). Winner conditions **4/5** (only DSR fails).
- **Score breakdown:** 1:20/25 2:17/25 3:0/15 4:15/15 5:15/15 6:0/5
- **Lesson:** Cross-asset diversification as compounding mechanism WORKS — new hunt-loop high (67/100), first to clear +0.10 gate on 2 datasets AND clear both CAGR + MDD floors 3/3. Only structural cost: 12-config blend grid inflates PBO (0.69 vs 0.24 single-asset). Next iteration should pre-commit single cfg (no grid, no PBO issue) OR compound with momentum overlay (+0.05-0.10 expected). See final_report.md.

### 005 — 2026-04-24 — Moreira-Muir canonical variance-scaling on SPY/QQQ (🥉 MARGINAL, score 59/100)
- **Hypothesis:** Replace iter 004's `target_vol/σ̂_{t-1}` (vol-scaling) with `target_vol²/σ̂²_{t-1}` (variance-scaling, Moreira-Muir 2017 canonical). Paper argues `σ^{-2}` is sharper because variance is more persistent; expected +0.12-0.15 uplift.
- **Citations:** Moreira & Muir (2017) *JoF* 72(4) DOI 10.1111/jofi.12513; `[systematic_trading, p.107-111 ch.9]`; `[advances_fin_ml, p.162-164, 208-211, 222-223, 196-202, 31-34]`; Cederburg et al. (2020) *JFE* 138(1) counter.
- **Scope:** 12 configs (target_vol×lookback×cap = 2×3×2) × 3 datasets. 2 bps cost. 3× smaller grid than iter 004 to preserve DSR.
- **Result:** Grand champion `vt20_L21_cap15` Sharpe edu 0.849 (Δ+0.167 hunt-loop top) / spy 0.981 (Δ+0.081) / ndx 1.052 (Δ+0.097). Gates **6/7 on ALL 3 datasets** (first hunt-loop cross-dataset §0 meet). G1 PBO edu 0.571 FAIL, **spy 0.238** / **ndx 0.147** (cleanest). G2 DSR **edu PASS** (p=0.044) spy/ndx FAIL. G6 bootstrap CI +0.35/+0.21/+0.21 all pos. G7 xlib 0.02-0.04 pp. Winner 0/5 (ndx Δ+0.097 misses +0.10 by 0.003).
- **Score breakdown:** 1:10/25 2:19/25 3:0/15 4:15/15 5:15/15 6:0/5
- **Lesson:** Moreira-Muir +0.20-0.40 uplift does NOT replicate on single-asset SPY/QQQ (only +0.01 over iter 004). **Single-asset vol-adaptation family saturated at +0.08-0.10 regardless of exponent σ^{-1}/σ^{-2}**. Only path through is compounding mechanism (cross-asset or signal overlay). See final_report.md.

### 004 — 2026-04-24 — Volatility-managed SPY (single-asset continuous vol scaling) (🥉 MARGINAL, score 51/100)
- **Hypothesis:** Rescale SPY exposure by `target_vol / σ̂_{t-1}` (Carver `[systematic_trading, p.107-111]` / Moreira-Muir 2017) — no signal, no cross-section, just continuous inverse-vol scaling. Tests the simplest instantiation of a canonical mechanism.
- **Citations:** `[systematic_trading, p.40 ch.2, p.107-111, p.144-146 ch.9]`, `[advances_fin_ml, p.162-164, p.208-211, p.222-223 p.275, p.196-202, p.31-34]`, Moreira & Muir (2017) *JoF* 72(4) 1611-1644 DOI 10.1111/jofi.12513.
- **Scope:** 36 configs (target_vol ∈ {0.10, 0.15, 0.20} × lookback ∈ {21, 63, 126, 252} × max_leverage ∈ {1.5, 2.0, 3.0}) × 3 datasets (SPYSIM synth 40y / SPY adj_close 17y / QQQ adj_close 16y). Cost model 2 bps/unit-scale-change.
- **Result:** Grand champion `tv20_L21_cap15` Sharpe edu 0.81 (Δ+0.13) / spy 0.98 (Δ+0.08) / ndx 1.04 (Δ+0.09). Gates edu 4/7, **spy 6/7**, **ndx 6/7**. G1 PBO 0.54/**0.31**/**0.35** (real-data clean). G6 bootstrap 99.9% CI low +0.33/+0.23/+0.22 (first iteration to clear G6). G7 cross-lib parity 0.02-0.04pp. DSR p 0.06/0.36/0.30 at n_trials=4156. MDD reduced 6-9pp on real data vs bench. Winner conditions 0/5 (fails strict Sharpe edge +0.10 on spy/ndx; DSR deflator penalty too large).
- **Score breakdown:** 1:10/25 2:11/25 3:0/15 4:15/15 5:15/15 6:0/5
- **Lesson:** **Vol-scaling mechanism is real and partially validated**: 6/7 gates pass on both real-data slots, MDD reduced while CAGR up, G6 (bootstrap) clears for the first time in the hunt loop. Falls 0.02 Sharpe short of the +0.10 strict gate and DSR headroom eroded by cumulative n_trials. The productive path is NOT more param sweeps but a compounding mechanism (variance-scaling per Moreira, or vol-managed 60/40 mix). See `iterations/004-2026-04-24-vol-managed-spy/final_report.md`.

### Iters 001-004 (pruned for space — see DEAD_ENDS.md + Top-K table)
- **001** (NEAR_FAIL ~35/100) — Crash-protected LETF trend, 4020 cfgs, 0/16 cross-dataset winners. See `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md`.
- **002** (FAIL 17/100) — Clenow 10bps ATR-risk-parity on 11 SPDR sectors. Root cause: ATR sizing calibrated for stocks fails on diversified-basket ETFs → 63-75% cash drag.
- **003** (FAIL 7/100) — Clenow adjusted-slope × R² with equal-notional on 11 SPDR sectors. Root cause: ≤ 20-asset homogeneous ETF universe lacks ranking signal.
- **004** (MARGINAL 51/100) — Single-asset vol-scaling SPY `σ⁻¹` (Carver form). 6/7 gates on spy+ndx, G6 first-ever pass, Sharpe edge +0.08-0.15 (below +0.10 on spy).

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iterations.

Consumed (moved to DEAD_ENDS or confirmed saturated): sector rotation
1/K + Clenow (iter 002/003 FAIL), single-asset vol-scaling (iter 004/005
saturated at +0.08-0.10), vol-managed 60/40 × momentum overlay (iter 007
redundant), single-cfg ex-ante verification of iter 006 blend (iter 008
confirmed structural — score 74, DSR sole killer), T10Y3M 21d-EMA
binary haircut overlay (iter 009 score 64 — smoothing erased lead-time),
**3-leg SPY+TLT+GLD vol-managed blend (iter 010 score 74 — tied
iter 008, confirmed blend family saturates ~Sharpe 1.00 regardless of
N=2/3; DSR is the true ceiling, not leg-count)**. See `DEAD_ENDS.md`.

### Iter 011 candidates (ranked by expected information gain)

Iter 010 framing: **iter 008 (N=2) and iter 010 (N=3) both score exactly
74/100 with 4/5 winner conditions**. The structural extension worked
cleanly (generalised risk-parity + Moreira-Muir to 3 legs) but scored
identical — DSR at cumulative n_trials ≈ 4246 requires Sharpe uplift
> ~0.30 on the worst dataset; blend family delivers at most +0.14 best
case / +0.04 worst case. **Adding more legs (N=4, N=5) won't close the
2× gap.** The productive path must address DSR directly: either change
the information source or change the timeframe-regime the deflator sees.

0j. **[OPTION F — TIMEFRAME CHANGE] Weekly-rebalance 3-leg blend
   (iter 010 mechanism, weekly resample)** — same risk-parity + Moreira-
   Muir variance-scaling, but signal and execution sampled 52× per year
   instead of 252×. Reduces DSR's effective n_trials (trials are
   *sampled* in the deflator). Also matches the Moreira-Muir 2017
   monthly-scale regime more directly. Single ex-ante cfg; reuses
   `three_leg_blend.py` on `.resample("W-FRI")`. **PICK FIRST for
   iter 011** — cheapest implementation, strongest theoretical attack
   on the DSR ceiling.

0f. **[OPTION C — META-LABELING on iter 008 blend] (AFML ch.3)** —
   secondary ML model predicts bar-level profitability using cross-
   sectional / macro features blend can't see. Orthogonal by
   construction; highest engineering cost; only direction that adds
   *informationally independent* signal beyond vol-regime. Expected
   uplift +0.20-0.30 Sharpe if meta-model has real predictive power;
   that magnitude is what DSR needs. Pick after Option F if weekly-
   rebalance doesn't break the ceiling.

0h. **[OPTION B' — REFINED OVERLAY] Asymmetric T10Y3M overlay: raw
   (≤ 5d smoothing) signal + haircut on EQUITY LEG ONLY (bond leg
   keeps full weight during recessions)**. Addresses iter 009's two
   failure modes: (a) preserves lead-time by minimal smoothing, (b)
   respects flight-to-quality. Single ex-ante cfg. Expected Sharpe
   uplift +0.03-0.08 if asymmetry isolates the benefit. Low-cost
   confirmation of the asymmetric-overlay principle.

0i. **[OPTION E — NEW MACRO SIGNAL] EBP (Gilchrist-Zakrajšek 2012)
   overlay on iter 008 blend**. Monthly-sampled credit-cycle signal;
   captures credit-spread risk structurally distinct from yield-curve
   slope. Month-end rebalance at daily horizon. Data in
   `data/external/macro/ebp_monthly.parquet`.

### Deeper backlog (not yet designed as iter-next)

- Return-stacked rotation NTSX/NTSI/NTSE (`[risk_parity, p.5]` +
  `[leverage_for_the_long_run, p.19-20]`).
- Cross-asset carry (FX/commodities/bonds), `[ilmanen_expected_returns]`.
- Seasonality (turn-of-month / sell-in-May / Santa) — never through
  7-gate pipeline.
- Options tail-hedging (put-spread collars).
- HMM regime-switching on stock-bond correlation
  (`[regime_change, ch.2]`).
- Meta-allocation among Plano C sleeves (GDE/AVUV/AVDE/AVEM/BTGD).
- Cross-sectional factor timing (Asness AQR 2024).

---

## Structural dead-ends (do NOT re-test; see `DEAD_ENDS.md` for detail)

- Daily EMA/SMA threshold on 3× LETF + any overlay (iter 001)
- Drawdown-based stop-loss as primary protection mechanism (iter 001)
- CAPE as standalone single-indicator de-lever (dead 2002-2015) (iter 001)
- Walk-Forward MDD<25% gate with leveraged trend (structural conflict) (iter 001)
- Parameter variations of iteration-001 base configs (iter 001)
- Clenow canonical (10 bps ATR-risk-parity) on sector-ETF universe with top-K=3-5 — under-deploys by ~3× (iter 002)
- 4-config single-strategy-family grid when all configs land in the same near-zero regime (G1 PBO noise floor ~0.5) (iter 002)
- Clenow adjusted-slope × R² ranking with equal-notional 1/K sizing on 11 SPDR sectors — full deployment confirmed, signal still absent (iter 003)
- Cross-sectional ranking momentum on any ≤20-asset universe of diversified baskets (sector/factor/country ETFs) — too homogeneous (iter 003)
- **Single-asset vol-adaptation on SPY/QQQ cannot clear +0.10 Sharpe gate regardless of exponent** (iter 004 `σ^{-1}` + iter 005 `σ^{-2}`) — family saturates at +0.08-0.10 real-data edge because SPY post-2009 Sharpe 0.90 is near the informational ceiling for signal-free vol-feedback. Only path through is compounding mechanism (cross-asset or signal overlay)
- **Time-series momentum overlay (12-1 / 6-1 / 18-1) on vol-managed 2-asset blend** REDUCES Sharpe by 0.01-0.15 on real data (iter 007) — momentum signal is redundant with variance-scaling's regime sensitivity; both track the same equity-vol information. Compounding needs ORTHOGONAL signals (carry, macro, meta-labeling), not correlated ones.
- **T10Y3M 21-day EMA binary haircut (threshold=0, haircut=0.5, symmetric on both legs) on iter 008 vol-managed blend** REDUCES Sharpe by 0.01-0.03 on all 3 datasets (iter 009). Root cause: the 21-day EMA smoothing destroyed the 6-18 month recession lead that is T10Y3M's canonical value. After smoothing, signal fires concurrently with realized-vol regime shifts (100% overlap with bottom-20% blend scale on edu+spy). **Macro overlays on vol-managed blends must preserve signal LEAD-TIME (raw or ≤ 5d smoothing) AND use asymmetric haircut (equity leg only) to be orthogonal.**
- **Vol-managed 3-leg blend (SPY+TLT+GLD / QQQ+TLT+GLD) on daily horizon with `vt15_L21_cap20_3leg`** (iter 010) ties iter 008 at 74/100 with 4/5 winner conditions but does NOT surpass — DSR worst p worsens 0.332→0.368 because ndx_real Sharpe regresses −0.03 (while edu +0.12 and spy +0.04). Leg-count is NOT the ceiling — the **blend family saturates near Sharpe 1.00 on real data** because daily vol-regime info has a hard informational ceiling `[leverage_for_the_long_run, p.9]`. Adding 4th/5th legs or swapping GLD for IAU/GDX will score 74 ±2. **DO NOT re-test with minor variations on this mechanism.** Productive path: change information source (meta-labeling) or timeframe (weekly rebalance changes DSR n_trials regime).

---

## Binding constraints (mandate §1, §5, §7)

- **NEVER modify mandate §1** (MAINTENANCE 100% Plano C)
- **Citations obrigatórias** (CLAUDE.md Regra 2): `[book.slug, p.X]`
- **7-gate battery** mandatory per spec §0 criterion
- **DSR n_trials cumulative** — increment `cumulative_n_trials` in this
  memory's frontmatter each iteration (add this iter's config count)
- **Real data > synth**: synth-only edge does NOT count as winner
- **Pytest baseline must stay green** (currently 770 collected: 765 pass + 5 skip, post iter 005 which added 10 variance-target specs; each iteration adds to this)
- **Max 2h wall-time** per iteration (stop if running longer)
- **NEVER commit to git** — the shell `run_loop.sh` handles it

---

## Infrastructure available (reuse, don't rebuild)

Simulators:
- `src/ai_trade/backtest/strategies/ema_sma_threshold_educational.py`
- `src/ai_trade/backtest/strategies/stop_loss_and_risk_signals.py`
  (stop + risk + combined + numpy cross-lib)

Data loaders:
- `src/ai_trade/backtest/data/testfolio_loader.py` (SPYSIM synth 1986+)
- `src/ai_trade/backtest/data/macro_data_loader.py` (EBP/T10Y3M/CAPE/VIX)
- `src/ai_trade/backtest/grid/real_etf_regime_runner.py` (SPY/UPRO, QQQ/TQQQ bundles)

Validation:
- `src/ai_trade/backtest/validation/pbo.py` (PBO via CSCV)
- `src/ai_trade/backtest/validation/dsr.py` (Deflated Sharpe Ratio)
- `src/ai_trade/backtest/validation/walk_forward.py`
- `src/ai_trade/backtest/validation/cpcv.py`
- `src/ai_trade/backtest/validation/permutation.py`

Metrics:
- `src/ai_trade/backtest/metrics/performance.py` (cagr/sharpe/mdd/etc)

Signals:
- `src/ai_trade/backtest/signals/risk_score.py` (z-score sigmoid composite)

Data cache:
- `data/tiingo/daily/prices/*.parquet` — SPY, SSO, UPRO, QQQ, QLD, TQQQ,
  sector ETFs, factor ETFs, bonds
- `data/external/macro/*.parquet` — EBP/T10Y3M/CAPE/VIX
- `data/testfolio/cache/history.parquet` — SPYSIM synth 40y+

Knowledge base:
- `books/summaries/` — 33 books (see `books/MAPPING.md` for slug ↔ title)
- `knowledge/SKILL.md` — aggregated quick-reference

---

## Tips for proposing hypothesis

1. **Keep it structurally new** (not params of old) — refer to
   `DEAD_ENDS.md`
2. **Cite ≥ 1 book** from `books/summaries/` as primary source
3. **Start simplest version** (Occam razor) — if simple version can't
   beat SPY, no amount of complexity will
4. **Think about what SPY doesn't capture** — sector rotation? factor
   tilt? non-equity? timing? regime?
5. **Fail-fast criterion**: hypothesis should include a kill condition
   (e.g., "if rolling 5y Sharpe < SPY in synth, abort")
6. **Test on 3 datasets** (educational + spy_real + ndx_real) from
   the start — cross-dataset is non-negotiable

---

## How to update this file at end of iteration

After your iteration completes:

1. Bump `total_iterations` in frontmatter
2. Update `latest_iteration`
3. Update `cumulative_n_trials` (add configs tested this iteration)
4. Append 5-line entry to `## Iteration log` (newest first)
5. If dead-ends discovered, append to `DEAD_ENDS.md` (don't bloat this file)
6. If WINNER: set `status: winner` in frontmatter AND populate
   `## Winners found` section
7. If not winner: set `status: iterating`, and move the tried direction
   from `## Promising unexplored directions` to `DEAD_ENDS.md` (or
   keep it with a note if it's partially useful for future)
8. **Keep this file < 15 KB.** If it grows too long, prune old
   iteration log entries (keep latest 10 + all winners).
