---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 29
winners_found: 0
status: iterating
latest_iteration: "029-2026-04-24-2236"
cumulative_n_trials: 4282
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
| **5** | **026** | 🥇 STRONG | **76** | `vrp_primary_h1_5_10_1m` (T-bill + short SPY 5/10% put credit spread) | `[volatility_trading, ch.3, p.41, p.217]` + Bondarenko 2014 | **1st DSR PASS ever** (ndx p=0.038); **1st 7/7 gates ever** (ndx); Sharpe Δ +0.38-0.45 cross-ds |
| 6 | 008 | 🥈 PROMISING | 74 | `vt15_L21_cap20` (2-leg SPY+TLT vol-mgmt) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | 4/5 winner; vol-managed reference baseline |

*(iter 001 ~35/100 approximate; back-fill in `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iteration in full 6-field format; older entries compressed to
3 lines (Result + Lesson + iter-dir pointer) once the file approaches
the 18 KB ceiling. Full hypothesis, citations, scope and score
breakdown for compressed iters are recoverable from
`iterations/NNN-*/hypothesis.md` + `verdict.json` + `final_report.md`.

### 029 — 2026-04-24 — vix-persistence-vrp-primary (🥈 PROMISING, 71/100, **Kill A TRIGGERED, score-tied iter 028**)
- **Hypothesis:** R-1 VIX-persistence gate (skip open only if VIX≥35 for 3 consecutive days) — refinement of iter 028, anchored to Sinclair p.218 sustained-vs-transient + Bondarenko 2014 §3.
- **Citations:** `[volatility_trading, p.217-218, ch.3, p.41]`, Bondarenko (2014) QJF 4(3) §3, Carr-Wu (2009) RFS 22(3), Whaley (2009) JPM 35(3).
- **Scope:** 1 cfg `vrp_persistence_v35d3_h1_5_10_1m`, 3 datasets, n_trials 4281→4282.
- **Result:** Sharpe edu/spy/ndx 1.2735/1.2295/1.3005 (Δ frozen +0.594/+0.330/+0.346 — 3/3 +0.10 gate; Δ iter026 **+0.140/−0.052/−0.067** Kill A — spy 2bp over threshold; Δ iter028 **+0.014/+0.048/+0.000** partial recovery), gates **7/6/6**, DSR p=**0.0251**/0.1002/0.0640 (n=4282, **NEW edu DSR record**; spy 0.136→0.100 improved 27% but missed 0.10 threshold by 0.0003), CAGR 5.11/4.71/5.90% floor 0/3 N=1 ceiling, MDD 6.63/6.35/8.18% ceiling 3/3, G7 0.0000 pp, persistence-skipped 10/3/4 vs iter 028 level-only 11/6/4, robustness 9/9, winner=4/5; score 1:25 2:21 3:5 4:0 5:15 6:5 = 71.
- **Score breakdown:** 1:25/25 2:21/25 3:5/15 4:0/15 5:15/15 6:5/5 = 71/100+5
- **Lesson:** Persistence-gate refines iter 028 in correct direction (DSR worst-p 0.136→0.100, edu DSR record 0.025) but ties score 71 (missed 10-pt threshold by 0.0003) + Kill A still triggers. **NEW STRUCTURAL FINDING**: 3 datasets have qualitatively different high-VIX regime structures — edu deeply-persistent GFC, spy mixed transient/persistent (3/6 transient), ndx all-clustered (4/4 persistent → R-1=iter 028). Single constant-parameter persistence gate cannot optimize all 3; need orthogonal axis. Closes specific cfg; opens R-2 z-score + R-3 term-structure + composite gates. See `iterations/029-2026-04-24-2236-vix-persistence-vrp-primary/`.

### 028 — 2026-04-24 — vix-filter-vrp-primary (🥈 PROMISING, 71/100, Kill A)
- **Result:** Sharpe edu/spy/ndx 1.260/1.181/1.301 (Δ frozen +0.580/+0.281/+0.345; Δ iter026 +0.126/−0.101/−0.067 Kill A 2/3), gates 7/6/6 (1st-ever 7/7 educational), DSR p=0.0287/0.1364/0.0640 (n=4281, 1st-ever sub-0.05 DSR on educational), winner=4/5; score 1:25 2:21 3:5 4:0 5:15 6:5 = 71.
- **Lesson:** Sinclair p.217 constant `VIX<35` is regime-conditional — lifts GFC-inclusive samples but regresses post-GFC. Asymmetry is persistence, not level. Closes constant-threshold path; opens regime-aware gates. See `iterations/028-2026-04-24-2207-vix-filter-vrp-primary/`.

### Iters 015-028 (compressed 1-line; full detail in `iterations/NNN-*/`)

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

Consumed/closed: 002/003/004/005/007/009/010/011/012/013/014/017/019/020/021/022/023/024/025/026/027/028/029 (iter 029 PROMISING 71, constant-persistence-threshold cfg closed; partial validation reveals dataset-structure asymmetry — single-parameter gate cannot optimize all 3 datasets). Top-K #1 still iter 016/018/021 triple-tied at 79.

### Iter 030 candidates (post-iter-029 — orthogonal regime axes; need WORST-p < 0.05 cross-ds)

- **R-2 VIX z-score gate** (filter when `(VIX[i] - VIX_60d_mean[i]) / VIX_60d_std[i] > 2`). **STRONGEST candidate — best path to WINNER.** Conditions on *relative shock*, orthogonal to both absolute level AND persistence; should correctly classify 2011 Eurozone gradual buildups (low z) as benign while still catching GFC + Mar-2020 (high z). Citations `[volatility_trading, p.218]` + Whaley (2009) JPM 35(3).
- **R-3 VIX term-structure gate** (filter when VIX > VXV — front-month backwardation). Self-conditioning on actual market expectation; arguably cleanest "sustained-stress vs transient" signal. `[volatility_trading, p.218]` + Carr-Wu 2009. Caveat: VXV data starts 2007; may shorten educational window.
- **R-1' Longer persistence horizons** (`persistence_days = 5, 7, 10` × `vix_threshold = 30, 35, 40`). NOT recommended standalone — same regime-structure issue, expected ties or marginal improvements.
- **R-1+R-2 composite** (persistence AND z-score both fire). More selective; should reduce false-positive filtering on transient-but-clustered events.
- **V-4 VRP+Carry composite** (0.5 × iter 026 + 0.5 × iter 024). Carry uncorrelated → composite σ² drops; adds CAGR from carry leg (could lift criterion 4 from 0/15 → 5/15).
- **V-5 Strike refinement** (5/15% wider OR 3/7% closer-to-ATM). Affects overlay_sharpe non-trivially.
- **V-6 Conditional strike adjustment**: widen strikes during persistent high-VIX rather than skipping outright; capture some premium decay with lower tail risk.
- **LS Long-short slow-EWMAC** (iter 025 + shorts; recovers ~50% trend premium).
- **C EWMAC+Carry combo** on 6 assets (Carver negative-skew complement; FDM 1.10→1.5-1.8).
- **W Wider-universe carry** (iter 024 + 3+ duration buckets OR cross-asset FX/commodity).

### Deeper backlog

- Plano C sleeve meta-allocation (GDE/AVUV/AVDE/AVEM/BTGD).
- Cross-sectional factor timing (≥10 factor ETFs, close to iter 003 floor).
- Carry + value composite (Asness-Moskowitz-Pedersen 2013) — orthogonal axes may break iter 024's saturation.
- VRP on broader index (RUT, EFA) — universe extension of iter 026.

---

## Structural dead-ends (1-line summaries; full text in `DEAD_ENDS.md`)

- Iter 001 family: daily EMA/SMA on 3× LETF + any overlay; drawdown-based stop-loss primary; CAPE standalone de-lever; WF MDD<25% gate with leveraged trend; param variations of base cfgs — all structurally closed.
- Clenow 10bps ATR-risk-parity on sector-ETF universe top-K=3-5 — under-deploys ~3× (iter 002); 4-cfg single-family grid near-zero → G1 PBO noise floor ~0.5.
- Clenow adjusted-slope × R² equal-notional on 11 SPDR sectors — signal absent (iter 003); cross-sectional momentum on ≤20-asset homogeneous baskets (sector/factor/country ETFs) closed.
- Single-asset vol-adaptation σ⁻¹/σ⁻² on SPY/QQQ — family saturates +0.08-0.10 (iter 004 + 005)
- TSM 12-1/6-1/18-1 overlay on vol-managed blend — REDUNDANT with variance-scaling (iter 007).
- T10Y3M 21d-EMA symmetric haircut on iter 008 — smoothing destroys lead-time (iter 009); T10Y3M asymmetric 5d EMA haircut — 100% overlap iter 009, 2×2 matrix closed (iter 012).
- 3-leg SPY+TLT+GLD daily `vt15_L21_cap20_3leg` — ties iter 008 at 74, blend-family ceiling (iter 010).
- Weekly/monthly rebalance for vol-managed multi-leg blend — daily cadence required; MDD +10-14pp (iter 011).
- Meta-labeling LR with ρ + VIX_z on iter 008 — vol-proxy features cointegrate with σ²_port (iter 013).
- EBP credit-cycle overlay on iter 008 — pre-val rejects 3/3; pre-val screen mandatory (iter 014).
- 12-1 top-K=1 rotation on ≤3-region universe — period Sharpe differential exceeds uplift (iter 017).
- ρ stock-bond regime overlay on vol-managed stack — ρ in σ²_port cross-term → any f(ρ) cointegrates; closes VIX/MOVE/realized-vol overlays by analogy (iter 019).
- Options-on-equity-leg 5/10%OTM×21DTE either sign on vol-managed 2-leg stack — σ²_port absorbs; Sharpe tied; MDD asymmetric (short −1-3pp, long +3-6pp). Does NOT close bare short puts/ATM straddles/different DTE (iter 020/021).
- Calendar-driven eq:bd weight modulator on vol-managed stack (TOM/holiday/DoW) — σ²_port quadratic in w_eq compresses premium; Sharpe −0.21 to −0.26 vs iter 016 (iter 022).
- TSM-PRIMARY on ≤4-asset broad-class ETF basket per-asset vol-target — turnover ~35/yr/leg dominates sqrt(3) diversification (iter 023). Open: slow-EWMAC, ≥20-market, carry/VRP-primary.
- Bond-curve carry-as-ALLOCATION on 2-bond universe (T10Y3M ramp) in static 0.9/0.6 stack — saturates at iter 015 static-IEF plateau; DSR worst p=0.586 (iter 024). Open: cross-asset carry, ≥3 duration buckets, carry+value.
- Slow-EWMAC long-only (FDM=1.10, buffer 10%) on 6-asset broad-class basket — engine cleanest ever but Sharpe 0.77/0.82/0.83 regresses 2/3 vs SPY/QQQ; long-only sacrifices ~50% trend premium; 6-asset too narrow vs Hurst-Ooi-Pedersen 67-market (iter 025). Open: long-SHORT, ≥20-asset, EWMAC+Carry, VRP-primary.
- **Tightening iter 026**: vol-target wrapper ABSORBS short-vol overlays (Sharpe-neutral); stand-alone harvest on T-bill collateral delivers +0.38-0.45 Sharpe alpha 3/3 (STRONG 76).
- **Tightening iter 027**: linear leverage on T-bill+harvest is NOT total-Sharpe-neutral (rf-bonus dilutes); N=3.5 total Sharpe→overlay_sharpe; closes leverage-only path.
- **Tightening iter 028**: constant `VIX<35` entry filter on iter 026 base is regime-conditional; lifts educational (GFC-inclusive → 1st-ever 7/7 + DSR p=0.029) but regresses spy/ndx (post-GFC transient spikes) → Kill A 2/3; closes constant-threshold V-3, opens regime-aware gates (R-1 persistence/R-2 z-score/R-3 term-structure). Does NOT close iter 026 at N=1.
- **Tightening iter 029**: `vix_threshold=35, persistence_days=3` partially refines iter 028 (DSR worst 0.136→0.100, edu record 0.0251) but ties score 71 (missed 10-pt threshold by 0.0003) + Kill A. NEW finding: 3 datasets have qualitatively different high-VIX structures (edu deeply-persistent GFC; spy mixed; ndx all-clustered → R-1=iter 028). Single constant gate cannot optimize all 3. Closes that cfg; opens R-2 z-score, R-3 term-structure, composite gates.

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
