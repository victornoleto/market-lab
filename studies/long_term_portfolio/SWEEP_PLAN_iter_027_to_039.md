---
status: PROPOSED
created: 2026-04-29
mission: Produce SEVEN retirement portfolio finalists (US/Global × Stacking/Factor/Hybrid + Stacked-MF wildcard), MF sleeve sensitivity test, and comparative report scoring all for 20-30y deploy
phase_1_iters: 6  # 027-032, single-axis isolation
phase_2_iters: 6  # 033-038, finalist construction (F1 = iter 023 baseline, no new iter)
phase_3_iters: 1  # 039, MF sleeve sensitivity on chosen winner
expected_total_runtime: ~19.5h
baseline: iter 023 (NTSX+GDE+KMLM+TLT 25/25/35/15)
expected_decision_at_end: SEVEN portfolios + MF sleeve recommendation + multi-criteria scoring report + final pick
---

# Sweep Plan — Iter 027 to 039 (Seven-Portfolio Finalist Matrix)

## Mission

Test three distinct portfolio design philosophies — **capital efficiency
stacking** (NTSX/NTSD/GDE), **factor risk premia** (AVUV/AVDV/AVEM/SPMO/
IDMO), and **stacked-MF** (RSST/RSBT family) — across two geographic
scopes (US-only and Global), producing **seven finalist portfolios**:

|                          | **US-only** | **Global** |
|--------------------------|-------------|------------|
| **Stacking only**        | F1          | F4         |
| **Factor tilts only**    | F2          | F5         |
| **Hybrid (Stack+Factor)**| F3          | F6         |
| **Stacked-MF wildcard**  | F7          | (deferred — RSIT not launched) |

After finalist construction, test **MF sleeve sensitivity** on the
chosen winner (KMLM vs DBMF vs split) to inform deploy choice. Final
output: comparative report scoring all seven on multi-criteria for
20-30y retirement deploy + MF sleeve recommendation.

## Design philosophy definitions

- **Stacking ETFs** = leveraged ETFs combining multiple exposures via
  futures/derivatives in one ticker (NTSX, NTSD, GDE, RSSB, NTSI/NTSE).
  Goal: more notional per dollar invested.
- **Factor tilt ETFs** = ETFs tilting equity toward empirical factors
  (AVUV, AVDV, AVEM, SPMO, IDMO). Goal: capture factor risk premia at
  1× notional.
- **Stacked-MF ETFs** = leveraged ETFs combining equity + managed-futures
  (RSST = S&P + MF, RSIT pending = Intl + MF). Goal: equity exposure +
  crisis-alpha diversifier in one ticker.
- **Diversifier ETFs (used in all)**: KMLM (managed futures), TLT (long
  Treasury), GLDSIM (gold). Used in any philosophy as alternative
  asset-class diversifiers.

## Baseline (iter 023)

**Composition**: 25% NTSX + 25% GDE + 35% KMLM + 15% TLT  
**Sharpe** (lh_56y / vt_real / ndx_real): **1.189 / 1.004 / 1.135**  
**CAGR**: 11.50% / 10.13% / 10.62%  
**MDD**: 21.13% / 17.40% / 11.76%  

iter 023 is **F1 directly** (US stacking-only) — no new iter needed.
Citation: `[risk_parity, ch.5, p.10]` Carlson all-weather levered.

---

## Phase 1 — Single-axis isolation (6 iters: 027-032, ~9h)

Each iter adds ONE sleeve to iter 023 base, sweeps 4 weights
(5/10/15/20%), tests if sleeve adds Sharpe vs iter 023. Phase 2
finalists use Phase 1 winners.

| iter | sleeve | category | substitution source |
|---|---|---|---|
| 027 | NTSD | Global stacking | from NTSX |
| 028 | AVUV | US factor (size+value+profit) | balanced from NTSX+KMLM |
| 029 | AVDV | Global factor | balanced from NTSX+KMLM |
| 030 | SPMO synth | US momentum factor | balanced from NTSX+KMLM |
| 031 | IDMO synth | Global momentum factor | balanced from NTSX+KMLM |
| 032 | AVEM | Global EM factor | balanced from NTSX+KMLM |

**Sleeve winner criteria**: best config beats iter 023 mean Sharpe
across 3 datasets AND passes 7-gate battery on ≥2/3 datasets AND DSR
p<0.05 cumulative.

(Per-iter details — configs, synth formulas, citations — same as prior
spec versions. Synth formulas consolidated below.)

---

## Phase 2 — Seven finalist constructions (6 NEW iters: 033-038, ~9h)

### F1 — US Stacking-only = iter 023 (NO NEW ITER)

Composition: **25% NTSX + 25% GDE + 35% KMLM + 15% TLT** (4 ETFs)

### iter 033 — F2: US Factor-tilts-only (6 ETFs, no leverage)

Equity via VTI vanilla + AVUV/SPMO factor tilts. Diversifiers: KMLM,
TLT, GLDSIM.

| config | VTISIM | AVUV | SPMO | KMLM | TLTSIM | GLDSIM |
|---|---:|---:|---:|---:|---:|---:|
| f2_balanced | 35% | 15% | 10% | 20% | 10% | 10% |
| f2_factor_heavy | 25% | 25% | 15% | 15% | 10% | 10% |
| f2_avuv_heavy | 30% | 25% | 5% | 20% | 10% | 10% |
| f2_spmo_heavy | 30% | 10% | 20% | 20% | 10% | 10% |

### iter 034 — F3: US Hybrid (Stacking + Factor)

iter 023 base + AVUV/SPMO winners.

| config | NTSX | GDE | KMLM | TLT | AVUV | SPMO |
|---|---:|---:|---:|---:|---:|---:|
| f3_balanced | 18% | 25% | 27% | 15% | 7.5% | 7.5% |
| f3_avuv_heavy | 17% | 25% | 28% | 15% | 10% | 5% |
| f3_spmo_heavy | 17% | 25% | 28% | 15% | 5% | 10% |
| f3_factor_15 | 15% | 25% | 25% | 15% | 10% | 10% |

ETF count: 6. Notional: ~135%.

### iter 035 — F4: Global Stacking-only

iter 023 base + NTSD geographic stack (depends on NTSD winning iter 027).

| config | NTSX | NTSD | GDE | KMLM | TLT |
|---|---:|---:|---:|---:|---:|
| f4_lite | 20% | 5% | 25% | 35% | 15% |
| f4_mod | 15% | 10% | 25% | 35% | 15% |
| f4_med | 12% | 15% | 25% | 33% | 15% |
| f4_heavy | 10% | 20% | 25% | 30% | 15% |

ETF count: 5. Notional: ~140%.

### iter 036 — F5: Global Factor-tilts-only

Pure factor portfolio with global factor tilts. No stacking.

| config | VTISIM | VEASIM | VWOSIM | AVUV | AVDV | AVEM | SPMO | IDMO | KMLM | TLT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| f5_lite | 25% | 12% | 5% | 10% | 8% | 5% | 8% | 5% | 15% | 7% |
| f5_factor_balanced | 18% | 10% | 4% | 12% | 10% | 6% | 10% | 6% | 18% | 6% |
| f5_factor_max | 12% | 8% | 3% | 15% | 12% | 8% | 12% | 8% | 16% | 6% |
| f5_no_momentum | 25% | 12% | 5% | 18% | 12% | 8% | 0% | 0% | 15% | 5% |

ETF count: 8-10. **Worst simplicity score in matrix.** Notional: 100%.

### iter 037 — F6: Global Hybrid (Stacking + Factor + Geographic)

iter 023 + NTSD + factor sleeves from each region.

| config | NTSX | NTSD | GDE | KMLM | TLT | AVUV | AVDV | AVEM | SPMO | IDMO |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| f6_lite | 15% | 8% | 22% | 28% | 12% | 5% | 4% | 2% | 2% | 2% |
| f6_balanced | 12% | 10% | 20% | 25% | 10% | 6% | 5% | 3% | 5% | 4% |
| f6_factor_heavy | 10% | 10% | 18% | 22% | 10% | 8% | 6% | 4% | 7% | 5% |
| f6_intl_heavy | 12% | 15% | 18% | 22% | 10% | 5% | 7% | 4% | 4% | 3% |

ETF count: 10. **Highest complexity in matrix.** Notional: ~150%.

### iter 038 — F7: US Stacked-MF wildcard (NEW)

**Hypothesis**: RSST stacks 100% S&P + 100% trend MF in one ticker.
Tests "stacked-MF philosophy" — an alternative to separate equity+MF
allocation, where the MF sleeve is bundled with equity. KMLM kept as
additional MF diversifier (since RSST uses Newfound/ReSolve trend, not
KFA MLM Index — diversifies engine risk).

| config | NTSX | RSST_synth | GDE | KMLM | TLT |
|---|---:|---:|---:|---:|---:|
| f7_lite | 25% | 15% | 25% | 20% | 15% |
| f7_balanced | 15% | 30% | 25% | 15% | 15% |
| f7_rsst_heavy | 10% | 40% | 25% | 10% | 15% |
| f7_pure_stack | 0% | 50% | 25% | 10% | 15% |

**Synth RSST** (INCOMPLETE):  
`RSST_daily_return = SPYSIM_daily_return + KMLMSIM_daily_return − (60bps/y ÷ 252)`  
Caveat: real RSST uses Newfound/ReSolve trend MF (not KFA MLM Index).
Engine differs from KMLM. Long-history backtest using KMLMSIM proxy
will track RSST imperfectly. Real RSST inception 2023-09 (~2.5y track
record). Flag INCOMPLETE.

ETF count: 5 (or 4 if NTSX=0). Notional: ~150-160% depending on config.
Double-dipping concern: RSST and KMLM both expose to MF — by design, to
test if engine diversification adds value or is redundant.

Citations: `[risk_parity, ch.5]` Carlson cap-efficient stacking +
ReSolve/Newfound Return Stacked methodology docs (2023).

**Note on Global Stacked-MF**: would use RSIT (Intl + MF stacked), but
RSIT launches ~mai/2026 (post-spec), and RSIT_synth has too much
assumption stacking. F7 stays US-only; Global Stacked-MF is **deferred
future work**.

---

## Phase 2 fallback rules

**If a sleeve fails Phase 1**, the finalist using it adapts:
- F2 fails (no AVUV, no SPMO): skip iter 033; F2 = "factor-only US not viable"
- F3 partial (only AVUV or SPMO wins): iter 034 with single-sleeve
- F4 fails (no NTSD): skip iter 035; F4 = "global stacking not viable"
  (consistent with iter 014/015 closures)
- F5 fails (no factor sleeves win): skip iter 036; F5 = "global factor-only not viable"
- F6 partial: iter 037 with whatever sleeves won
- F7 KILL #5 (no-free-lunch RSST synth): if RSST synth standalone Sharpe
  > KMLM standalone × 1.5 (i.e., synth inflates due to embedded equity
  beta), invalidate and rerun with cleaner formula

If F2-F7 all fail: report concludes "iter 023 (F1) is the deploy
recommendation".

---

## Phase 3 — MF sleeve sensitivity (1 NEW iter: 039, ~1.5h)

**Trigger**: Phase 2 complete, comparative report draft identifies
WINNER finalist (highest multi-criteria score).

### iter 039 — MF sleeve sensitivity on winner

Replace winner's MF sleeve with each candidate, hold all other weights
constant. Tests deploy-readiness of MF choice.

| config | MF sleeve replaces KMLM with | rationale |
|---|---|---|
| mf_kmlm (baseline) | KMLMSIM | published index, transparent rules |
| mf_dbmf | DBMFSIM | 5× AUM, replicates SG CTA Index, more reliable |
| mf_split | 50% KMLMSIM + 50% DBMFSIM | engine + AUM diversification within sleeve |
| mf_cta_proxy | KMLMSIM scaled to estimated CTA Simplify exposure (proxy with caveat) | multi-strategy, lower TER (0.75% vs 0.92%) |

**Caveats**:
- DBMFSIM 26y window vs KMLMSIM 38y → comparison runs on 26y intersection
- CTA Simplify proxy uses KMLMSIM with vol scaling (no honest synth) — flag INCOMPLETE
- All configs use winner finalist's other weights unchanged

**Output**: iter 039 verdict declares the recommended MF sleeve. Phase 4
report includes "Recommended MF sleeve" section.

---

## Phase 4 — Comparative Report (FINAL_REPORT_seven_portfolios.md)

### Multi-criteria scoring rubric (0-100 per finalist)

| criterion | weight | how scored |
|---|---:|---|
| **C1 Risk-adjusted return** | 25 | mean(gross_Sharpe) across 3 datasets, normalized vs iter 023 (1.109) and SPY (0.827) |
| **C2 CAGR** | 12 | mean CAGR vs SPY benchmark |
| **C3 MDD safety** | 13 | mean MDD reduction vs SPY |
| **C4 Simplicity** | 15 | inverse of ETF count; 4=100, 5=90, 6=80, 7=70, 8=60, 9=50, 10=40 |
| **C5 Expense (TER)** | 10 | weighted-avg TER; <0.40%=100, 0.40-0.60%=85, 0.60-0.80%=70, 0.80-1.00%=55, >1.00%=40 |
| **C6 Regime robustness** | 10 | rolling 5y % positive Sharpe |
| **C7 Deploy ease (Inter)** | 15 | hard gate: any ETF unavailable on Inter Internacional → C7=0; else AUM-based |

Weights sum: 100. Higher = more important for 20-30y retirement.

### Comparative table (7 finalists side-by-side)

```
| metric                    | F1 US-Stk | F2 US-Fct | F3 US-Hyb | F4 Gl-Stk | F5 Gl-Fct | F6 Gl-Hyb | F7 US-StkMF |
| ETF count                 | 4         | 6         | 6         | 5         | 8-10      | 10        | 4-5         |
| Notional total            | 132%      | 100%      | 135%      | 140%      | 100%      | 150%      | 150-160%    |
| Sharpe lh_56y             | 1.189     | ?         | ?         | ?         | ?         | ?         | ?           |
| ...                       | ...       | ...       | ...       | ...       | ...       | ...       | ...         |
| Multi-criteria score      | X/100     | ?         | ?         | ?         | ?         | ?         | ?           |
```

### Cross-cutting analysis

1. **Stacking vs Factor vs Stacked-MF**: which philosophy wins? F1+F4
   vs F2+F5 vs F7.
2. **US vs Global**: F1+F2+F3+F7 (US) vs F4+F5+F6 (Global).
3. **Hybrid premium**: does F3/F6 beat pure philosophies?
4. **Regime regret analysis**: 1980s-style intl-led vs 2010s-style US-led.

### Recommendation section

1. Which finalist scores highest? (with MF sleeve from iter 039)
2. Should you deploy highest scorer or runner-up if Sharpe gap < 0.05
   and simplicity gap > 15pts?
3. Regret-minimizing choice if regime is uncertain?
4. Mandate §7 override request draft for chosen finalist + MF sleeve.

---

## Synth formulas reference (consolidated)

| ticker | synth | caveat |
|---|---|---|
| **NTSX** | `0.90 × SPYSIM + 0.60 × IEFSIM − 0.50 × CASHX` | validated 2026-04-26 |
| **NTSD** | `0.90 × SPYSIM + 0.60 × VEASIM − 75bps/y` | INCOMPLETE — active mgmt unmodeled |
| **GDE** | `GDESIM` (testfolio direct) | direct |
| **KMLM** | `KMLMSIM` (testfolio direct) | direct, 38y |
| **DBMF** | `DBMFSIM` (testfolio direct) | direct, 26y (1999+) |
| **TLT** | `TLTSIM` (testfolio direct) | direct |
| **GLD** | `GLDSIM` (testfolio direct) | direct |
| **VTI** | `VTISIM` (testfolio direct) | direct, 99y |
| **VEA** | `VEASIM` (testfolio direct) | direct, 56y |
| **VWO** | `VWOSIM` (testfolio direct) | direct, 32y (1994+) |
| **AVUV** | `VBRSIM + 75bps/y tilt premium` | INCOMPLETE — proxy index |
| **AVDV** | `VSSSIM + 100bps/y tilt premium` | INCOMPLETE |
| **AVEM** | `VWOSIM + 125bps/y tilt premium` | INCOMPLETE — VWOSIM 1994+ bottleneck |
| **SPMO** | `SPYSIM + 0.60 × UMD_KF − 35bps/y` | INCOMPLETE — UMD academic capture |
| **IDMO** | `VEASIM + 0.60 × UMD_KF − 60bps/y` | INCOMPLETE — US UMD proxy for intl |
| **RSST** | `SPYSIM + KMLMSIM − 60bps/y` | INCOMPLETE — engine differs (ReSolve ≠ MLM Index) |
| **CTA Simplify proxy** | `KMLMSIM scaled` | INCOMPLETE — KMLMSIM is single-strategy, CTA is multi |

UMD_KF source: `data/ken_french/F-F_Momentum_Factor_daily.csv`.

---

## Pre-committed KILL conditions (anti-overfit)

- **KILL #1 (no-positive-config)**: best Phase 1 config doesn't beat
  iter 023 on ≥1/3 datasets → sleeve closed.
- **KILL #2 (monotonic regression)**: Sharpe monotonically decreases
  with sleeve weight → sleeve subordinate, closed.
- **KILL #3 (no-free-lunch synth)**: SPMO/IDMO/AVEM synth standalone
  Sharpe > 1.5 → broken, fix and rerun.
- **KILL #4 (Phase 2 frankenstein degradation)**: Phase 2 best combo
  Sharpe < mean of contributing single-axis winners → fall back.
- **KILL #5 (RSST stacked synth check)**: RSST_synth standalone Sharpe >
  1.5 (absolute cap, matches KILL #3) → synth has bug (double leverage,
  leakage). Original `(s1+s2) × 0.7` threshold revised post-implementation:
  SPY/KMLM correlation is -0.19, so equal-weight stacking legitimately
  produces Sharpe ~0.97 by mean-variance math (consistent with ReSolve
  published RSST live Sharpe since 2023 inception) — not a free lunch.

---

## Risks / caveats

### Synth assumption stacking
SPMO/IDMO embed 2 layers (beta + UMD scale). AVEM stacks 3 layers
(VWOSIM + 125bps + EM data quality). RSST embeds 2 layers (SPY beta +
KMLM as MF proxy with engine mismatch). Phase 1/2 results from synth-
heavy sleeves should be interpreted conservatively.

### DSR cumulative inflation
Pre-sweep n_trials = 94. Phase 1 adds 6×4 = 24 → 118. Phase 2 adds 6×4
= 24 → 142. Phase 3 adds 4 → 146. p-value bar tightens accordingly.

### Window bottleneck (AVEM, DBMF, RSST)
- VWOSIM starts 1994-05-04 → AVEM (iter 032, F5, F6) lh_56y limited to 32y
- DBMFSIM starts 1999-12-31 → iter 039 mf_dbmf comparison limited to 26y
- RSST_synth uses KMLMSIM (1987+) and SPYSIM (1986+) → 38y window
- All effective windows documented in respective iter reports

### Geographic + philosophy regime confounding
F1-F3 over-fit 2010-2024 US-equity dominance. F4-F6 may win in intl-led
regime. F7 stacked-MF is regime-agnostic in theory but engine-specific
(ReSolve trend) in practice. Phase 4 regime regret analysis addresses.

### Deploy ease HARD GATE
ETFs to verify on Inter Internacional: NTSX, NTSD, GDE, KMLM, DBMF, TLT,
GLD, VTI, VEA, VWO, AVUV, AVDV, AVEM, SPMO, IDMO, RSST. If any missing,
finalists using it score C7=0.

### Engine diversity in stacked-MF
F7 uses RSST (ReSolve trend) + KMLM (KFA MLM trend). Both are trend-
following but different engines. Real correlation likely 0.6-0.8 — not
fully diversified. Consider DBMF as third engine if F7 wins.

### Model artifact risk (recall iter 022)
KILL #3 + KILL #5 enforced strictly for synth iters.

---

## Citations

- `[risk_parity, ch.5, p.10]` Carlson — cap-efficient stacking
- `[risk_parity, ch.2, p.37-41]` — Fama-French factor framework
- `[stocks_on_the_move, p.21-30]` Clenow — momentum premium
- `[ilmanen_expected_returns, ch.19]` — intl + EM diversification
- `[advances_fin_ml, p.208-211]` PBO via CSCV
- `[advances_fin_ml, p.222-223]` DSR
- `[advances_fin_ml, p.196-202]` bootstrap CI
- `[advances_fin_ml, p.31-34]` cross-lib + factor framework
- WisdomTree NTSD prospectus 2026-03-19
- Frazzini-Israel-Moskowitz 2018 — UMD long-only capture rate
- Jegadeesh-Titman 1993 — cross-sectional momentum
- ReSolve/Newfound Return Stacked methodology (2023) — RSST/RSBT/RSIT
  conceptual framework

---

## Execution plan (high-level)

1. User reviews this spec (this checkpoint).
2. After approval: invoke `superpowers:writing-plans` skill to produce
   detailed step-by-step implementation plan covering:
   - Inter Internacional pre-check (16 ETFs availability)
   - Synth function implementations (NTSD, AVUV, AVDV, AVEM, SPMO,
     IDMO, RSST, CTA proxy)
   - Iter 027-032 Phase 1 scaffolding + execution
   - Phase 1 → Phase 2 selection automation
   - Iter 033-038 Phase 2 finalist construction
   - Iter 039 Phase 3 MF sleeve sensitivity
   - FINAL_REPORT_seven_portfolios.md production
3. Phase 1 execution: 6 iters sequentially, ~9h.
4. Phase 2 execution: 6 iters sequentially, ~9h.
5. Phase 3 execution: 1 iter, ~1.5h.
6. Phase 4 comparative report: ~2h analysis.
7. User reviews report + chooses ONE finalist + MF sleeve + decides on
   mandate §7 override request.

---

## Conclusion

Sweep produces seven finalist portfolios across 3 design philosophies
(stacking, factor, stacked-MF) × 2 geographic scopes (US, Global), tests
MF sleeve sensitivity on the winner, and produces multi-criteria scoring
report for 20-30y retirement deploy. Either pure philosophy (F1/F4
stacking, F2/F5 factor, F7 stacked-MF) wins on simplicity, or hybrid
(F3/F6) wins on diversification — outcome is data-driven, with explicit
regime regret analysis and deploy-ready MF sleeve recommendation.
