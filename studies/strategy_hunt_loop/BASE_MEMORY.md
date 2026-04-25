---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 25
winners_found: 0
status: iterating
latest_iteration: "025-2026-04-24-2059"
cumulative_n_trials: 4278
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
| 5 | 008 | 🥈 PROMISING | 74 | `vt15_L21_cap20` (2-leg SPY+TLT vol-mgmt) | `[risk_parity, p.10-11]` + Moreira-Muir 2017 | 4/5 winner; vol-managed reference baseline |

*(iter 001 ~35/100 approximate; back-fill in `tests/test_strategy_scoring.py::TestNearMiss`.)*

---

## Iteration log (newest first)

Latest iteration in full 6-field format; older entries compressed to
3 lines (Result + Lesson + iter-dir pointer) once the file approaches
the 18 KB ceiling. Full hypothesis, citations, scope and score
breakdown for compressed iters are recoverable from
`iterations/NNN-*/hypothesis.md` + `verdict.json` + `final_report.md`.

### 025 — 2026-04-24 — Slow-EWMAC (32:128+64:256 FDM=1.10) + Carver no-trade buffer + portfolio vol-target on 6-asset long-only basket SPY+TLT+IEF+GLD+EFA+EEM (📉 NEAR_FAIL 39/100, Kill #A)
- **Result:** Sharpe 0.766/0.815/0.828 (Δ frozen +0.086/−0.085/−0.127 — 0/3 +0.10 gate, 2/3 REGRESS post-GFC), CAGR 9.13/9.97/10.20% (floor 0/3), MDD 17.3% on all 3 (vs bench 55/34/35; dramatic 16-38pp improvement, MDD ceiling 3/3), gates 6/6/6 (G2 DSR fail p=0.62/0.62/0.63), G3 WF 7/8+8/8+8/8 (best-ever), G6 3/3 PASS (joins iter 016/021/024), G7 xlib 0.003-0.06pp (cleanest engine ever), turnover 1.56-1.61/yr/leg (22× lower than iter 023), buffer ratio 0.726-0.730, robustness 9/9 (ties iter 013/024); n_trials 4277→4278; Kill A triggered (Sharpe Δ vs iter 015 −0.02/−0.23/−0.24); score 1:0 2:19 3:0 4:0 5:15 6:5 = 39.
- **Lesson:** Slow-EWMAC + FDM + buffer fixes iter 023's turnover (1.6/yr vs 35/yr; engine cleanest ever) but cannot beat post-GFC SPY/QQQ on Sharpe. Long-only sacrifices ~50% trend premium; 6-asset too narrow vs Hurst-Ooi-Pedersen 67-market for SR≈1.0. Dramatic MDD reduction (17% vs 33-55%) — defensive equity surrogate at Sharpe cost. Tightens iter 023 boundary: slow-signals + FDM + buffer + portfolio-vol on 6-asset long-only basket = closed. Open: long-short variant, ≥20-asset, EWMAC+Carry combo, VRP-primary. See `iterations/025-2026-04-24-2059-slow-ewmac-multi-asset/`.

### 024 — 2026-04-24 — Bond-carry duration timing TLT↔SHV (🥈 PROMISING 72/100, 4/5 winner cond)
- **Result:** Sharpe 0.787/1.054/1.060 (Δ frozen +0.107/+0.154/+0.105 — 3/3 +0.10 gate; Δ iter 015 +0.003/+0.009/−0.003 tied; Δ iter 016 −0.20/−0.09/−0.13), CAGR 12.5/15.7/19.4% floor 3/3, MDD 42.6/34.0/42.7% (ndx +7.5pp), gates 5/6/6, DSR worst p=0.586, winner 4/5; turnover 0.4/yr; robustness 9/9 record; n_trials 4276→4277; score 1:25 2:17 3:0 4:15 5:10 6:5 = 72.
- **Lesson:** Carry-as-ALLOCATION distinct from carry-as-HAIRCUT — no σ²_port absorption. 3/3 Sharpe edge BUT on 2-bond universe (TLT vs SHV) ties iter 015 static-IEF baseline because alpha from regime switching ≈ TLT vol cost in steep regimes (~70% bars). DSR ceiling at n=4277 binds even for novel 3/3-edge mechanisms. See `iterations/024-2026-04-24-2033-bond-carry-duration-timing/`.

### 023 — 2026-04-24 — TSM 3-asset SPY+TLT+GLD per-asset vol-target (📉 NEAR_FAIL 28/100, biggest regression)
- **Result:** Sharpe 0.554/0.552/0.610 (Δ frozen −0.126/−0.348/−0.345; **Δ iter 016 −0.427/−0.588/−0.576 — largest ever**), CAGR 8/8/9% floor fails 3/3, MDD 48/48/36% spy +14.5pp, gates 5/5/4, DSR worst-ever p=0.926, n_trials 4273→4276, winner 0/5; geometry change mechanical (Kill B+C clear) but cost > premium; score 1:0 2:15 3:0 4:0 5:10 6:3 = 28.
- **Lesson:** TSM-primary on ≤4-asset ETF basket cannot beat SPY/QQQ — turnover ~35/yr/leg × 2 bps (2.1%/yr drag) dominates sqrt(3) basket diversification (Carver LoAM); Hurst-Ooi-Pedersen 2017's +1.0 Sharpe required 67 markets. Closes TSM-primary on broad-asset-class small baskets; does NOT close slow-EWMAC, ≥20-market baskets, carry-primary, VRP-primary. See `iterations/023-2026-04-24-2007-time-series-trend-3etf/`.

### Iters 015-022 (compressed 2-line; full detail in `iterations/NNN-*/`)

- **022** (🥉 54, Kill #4) TOM seasonality eq:bd modulator 0.9↔0.5: Sharpe 0.76/0.89/0.98 (Δ016 −0.22/−0.26/−0.21), MDD +2.7/+6.2/+7.3pp; σ²_port quadratic in w_eq absorbs calendar premium; closes calendar-modulated eq:bd family.
- **021** (🥇 79, top-K #1) Short put-credit-spread VRP overlay on iter 016: Sharpe 0.99/1.14/1.14, MDD −1.95/−1.01/−2.85pp uniform improvement, DSR p=0.217 (n=4270 record), +2.95-4.10%/yr Bondarenko; vol-target absorbs equity-leg options either sign; closes 5/10%OTM×21DTE bilaterally.
- **020** (🥇 79, dominated) Monthly put-spread tail hedge: Sharpe Δ016 −0.08/−0.08/−0.04, MDD +3-6pp WORSE 3/3, theta drag −3 to −4%/yr; long-gamma overlays REDUNDANT with vol-target variance-scaling.
- **019** (❌ 0, Kill #PV) HMM stock-bond ρ regime: pre-val rejects 3/3 (exceed 0.65-0.67); σ²_port contains ρ as cross-term → any f(ρ) cointegrated; closes ρ/VIX/MOVE/realized-vol overlays.
- **018** (🥇 79, top-K #1) Funding-cost iter 016 replay: drag 148/114/93 bps/yr; Sharpe Δ016 −0.09/−0.08/−0.05; each 100bps drag ≈ −0.07 Sharpe; iter 016 post-cost validated; DSR sole barrier.
- **017** (🥉 52) 12-1 regional rotation N=3 on iter 016: Sharpe Δ016 −0.23/−0.32/−0.18; period US Sharpe 0.63-0.95 vs EFA/EEM 0.33-0.48; closes top-K∈{1,2} on ≤3-region universes.
- **016** (🥇 79, top-K #1) Static 60:40 × Moreira-Muir vol-target hybrid: Sharpe 0.98/1.14/1.19 (Δ frozen +0.30/+0.24/+0.24; +0.12-0.17 vs iter 008), DSR p=0.226 (n=4261, BEST), winner 4/5; fixed-ratio × vol-target ADDITIVE not redundant.
- **015** (🥇 77, 4/5 winner) Static synthetic NTSX 90/60 SPY+IEF: Sharpe Δ frozen +0.10/+0.14/+0.11 — 1st iter clearing +0.10 cross-ds; DSR p=0.548; static breaks σ²_port cointegration; DSR universal ceiling.

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

Consumed/closed: 002/003/004/005/007/009/010/011/012/013/014/017/019/020/021/022/023/024/025. Top-K #1 still iter 016/018/021 triple-tied at 79.

### Iter 026 candidates (post-iter-025)

0v. **Option V — VRP-primary portfolio** (short puts/spreads + Tbill collateral). +3-4%/yr (Bondarenko 2014); strongest candidate to break DSR at n=4278. `[volatility_trading, ch.3]`.
0ls. **Option LS — Long-SHORT slow-EWMAC** — same as iter 025 + short positions; recovers ~50% trend premium iter 025 sacrificed. ETF borrow ~30-50 bps/yr.
0c. **Option C — EWMAC + Carry combo on 6 assets** — Carver's negative-skew complement; FDM 1.10→1.5-1.8 with 4 forecasts → +0.15-0.20 Sharpe potential.
0w. **Option W — Wider-universe carry** — iter 024 extended to 3+ duration buckets OR cross-asset (FX UUP, commodity DBC).
0t. **Option T — pre-registered minimal-trial replay of iter 016** (n_trials=1, PSR clears) — §7 override artifact.

### Deeper backlog

- Plano C sleeve meta-allocation (GDE/AVUV/AVDE/AVEM/BTGD).
- Cross-sectional factor timing (≥10 factor ETFs, close to iter 003 floor).
- Carry + value composite (Asness-Moskowitz-Pedersen 2013) — orthogonal axes may break iter 024's saturation.

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
- EBP (GZ2012) credit-cycle overlay on iter 008 — pre-val rejects all 3 ds; overlay family CLOSED; pre-val screen mandatory (iter 014)
- 12-1 top-K=1 rotation on ≤3-region equity universe (iter 016 base) — period Sharpe differential exceeds uplift; closes top-K∈{1,2} × any lookback on N≤3 regional universes (iter 017)
- Stock-bond correlation ρ regime overlay on vol-managed stack — ρ enters σ²_port as cross-term, any f(ρ) cointegrated; closes VIX/MOVE/realized-vol overlays by analogy (iter 019)
- Options-on-equity-leg 5/10%OTM×21DTE either sign on vol-managed 2-leg stack — σ²_port absorbs variance; Sharpe tied. MDD asymmetric (short −1-3pp, long +3-6pp). Does NOT close bare short puts/ATM straddles/different DTE (iter 020/021)
- Calendar-driven eq:bd weight modulator on vol-managed 2-leg stack (TOM/holiday/DoW) — σ²_port quadratic in w_eq; scale compensates → premium compressed; Sharpe −0.21 to −0.26 vs iter 016. Does NOT close binary entry/exit, cross-sectional ranking (iter 022)
- TSM (any lookback/skip) as PRIMARY mechanism on ≤4-asset broad-asset-class ETF basket per-asset vol-target — turnover ~35/yr/leg dominates sqrt(3) diversification; Sharpe regress 0.43-0.59 vs iter 016 (largest ever). Does NOT close slow-EWMAC, ≥20-market baskets, carry-primary, VRP-primary (iter 023)
- Bond-curve carry-as-ALLOCATION on 2-bond universe (TLT↔SHV via T10Y3M ramp) in static 0.9/0.6 stack — novel mechanism (NOT in iter 009/012/013 haircut family), 3/3 Sharpe edge cross-ds, but saturates at iter 015 static-IEF plateau (Δ +0.003/+0.009/−0.003); DSR worst p=0.586 (n=4277). Tightens T10Y3M boundary (closed as scaler, NOT as allocation switch). Does NOT close cross-asset carry, ≥3 duration buckets, carry+value (iter 024)
- Slow-EWMAC trend (32:128 + 64:256, FDM=1.10, Carver no-trade buffer 10%) with portfolio-level vol-target on 6-asset broad-asset-class long-only ETF basket (SPY/QQQ + TLT + IEF + GLD + EFA + EEM) — fixes iter 023's turnover (1.6/yr/leg vs 35/yr; engine cleanest ever, G3 7-8/8, G6 3/3, G7 < 0.06 pp), but Sharpe 0.77/0.82/0.83 vs SPY/QQQ 0.68/0.90/0.96 → 2/3 regress on real data (Δ frozen +0.086/−0.085/−0.127). MDD dramatically improved (17% vs 33-55%). Long-only constraint sacrifices ~50% of trend premium; 6-asset too narrow vs Hurst-Ooi-Pedersen 67-market for SR≈1.0. Does NOT close long-short slow-EWMAC, ≥20-asset trend, EWMAC+Carry combo, VRP-primary (iter 025)

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
