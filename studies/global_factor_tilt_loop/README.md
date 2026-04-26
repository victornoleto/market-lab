# Global Factor-Tilt Loop — STUDY PREPARATION

**Status**: PREPARATION ONLY. Not yet activated. Will run AFTER
`gold_swing_loop` completes.

**Mission**: Find ONE strategy that gives **global equity exposure**
(US + ex-US developed + emerging) and beats **VT 1x buy-and-hold** in
risk-adjusted terms (Sharpe) on real data, ideally also in raw return
(CAGR).

This is a **bifurcation** of `studies/strategy_hunt_loop/` — the
hypothesis-search infrastructure is reusable, only the universe and
benchmark change.

---

## Why a separate study (vs continuing strategy_hunt_loop)?

`strategy_hunt_loop` tested edge against SPY (US-only) and QQQ
(US-tech). Most winners (iter 035, 016, 006, 074, 079) **dominate SPY
because they add asset diversification on top of US equity** —
bonds, gold, vol-target overlay. They are not "edge over global
equity"; they're "edge over US-only".

A US-resident investor going *globally diversified* would naturally use
**VT** (Vanguard Total World) or equivalent as the passive baseline.
That bench is harder to beat because:

1. VT is already 60% US + 40% international — the gain from adding
   ex-US is gone.
2. VT's natural Sharpe is *lower* than SPY (~0.55 vs 0.90 in 17y) but
   so is its CAGR — the bar shifts proportionally.
3. The candidate strategies need a DIFFERENT kind of edge: factor
   tilts, regional rotation, currency hedge, etc.

So: separate loop, separate winner conditions, separate dead-ends.

---

## Benchmark hierarchy (TBD — confirm before launch)

| dataset | candidate benchmark | notes |
|---|---|---|
| primary | **VT 1x b&h** | Vanguard Total World (1x cap-weighted) |
| secondary | **VTI + VXUS 60/40** | proxy if VT history limited (VT only has ~17y) |
| long-window | **SPYSIM × 0.6 + EFASIM × 0.4** synthetic | needs EFA/EFASIM availability check |

**Critical gap**: `data/testfolio/cache/history.parquet` covers SPYSIM,
QQQSIM, GLDSIM, ZROZSIM (40y) but NOT EFASIM/VXUSSIM. Long-window
validation for global strategies will be **incomplete** unless we
either (a) source EFASIM separately or (b) accept 17-year window only.

---

## Candidate universe (Avantis-tilted, factor-aware)

User explicit ask: use **AVNM** (Avantis All Intl Markets Equity, ETF)
for ex-US exposure instead of plain VXUS — Avantis tilts to small-cap
value within int'l developed + emerging.

Tickers to validate (Inter Internacional availability check **TBD**):

| ticker | role | strategy hypothesis |
|---|---|---|
| **VT** | benchmark | passive global cap-weighted |
| **VTI / SPY** | US core | base US equity sleeve |
| **AVUV** | US small-cap value | Avantis US factor tilt |
| **AVDV** | int'l developed small-value | Avantis ex-US factor |
| **AVEM** | emerging factor | Avantis EM tilt |
| **AVNM** | int'l multi-factor (small + value) | broader Avantis ex-US (alternative to AVDV/AVEM split) |
| **VXUS** | int'l cap-weighted | passive ex-US (comparison only) |
| **VWO** | EM cap-weighted | passive EM (comparison only) |
| **TLT / IEF / ZROZ** | bond defensive sleeve | per strategy_hunt_loop top-K |
| **GLD** | gold sleeve | cross-asset diversifier |

Open questions for Stage 1 (research, not implementation):

- AVNM history: started ~2022, may not give clean 5-year backtest.
  Substitute: `AVDV + AVEM` blend.
- AVUV started 2019 → 7y history.
- AVDV started 2018 → 8y.
- AVEM started 2019 → 7y.
- VT started 2008-06 → 17y.
- For 17y backtest: VT + AVUV (since 2019) + AVDV (since 2018) +
  AVEM (since 2019) + bond/gold legs. Joined-window is ~7y from 2019
  → very short for strict statistical claims.

---

## Hypothesis menu (curated, based on academic literature)

These are STARTING points for the loop's Stage 1 hypothesis selection.
The loop may invent variants or find new directions.

### Tier 1: established factor literature

1. **Static return-stack: VT + AVUV + AVDV/AVEM + bonds + gold**.
   `[risk_parity, ch.5]` extended globally. Direct port of
   `strategy_hunt_loop` iter 035 to global universe.
   Priors: should beat VT in CAGR (small-value premium ≈ +2-4%/yr per
   Fama-French 1993, Asness 1997+) and Sharpe (correlation
   diversification).

2. **AVNM-only static stack**. Single-ticker bet on Avantis' ex-US
   factor implementation. Simpler than (1) but heavier concentration.
   `[smart_beta_etfs]` if available.

3. **Vol-managed VT + bonds/gold mix**. Direct port of iter 016
   (vol-target overlay) to global universe. `[systematic_trading,
   ch.11]` + Moreira-Muir 2017.

4. **VT vs `VTI+VXUS 60/40` allocation rotation**. When US
   outperforms by N pp on rolling 12m → tilt to VTI; when ex-US
   outperforms → tilt to VXUS. Cross-region momentum.
   `[stocks_on_the_move, p.21-30]` adapted to regions.

### Tier 2: regional + style rotation

5. **Top-K country rotation** (Faber 2007 style on country ETFs).
   Universe: SPY, EWJ (Japan), EWG (Germany), EZU (Eurozone),
   EWU (UK), MCHI (China), EWZ (Brazil), INDA (India). Pick top-K
   by 12m momentum.

6. **Factor sleeve rotation within global**: rotate across MTUM/VLUE/
   QUAL/SIZE per region by relative momentum. AQR-style factor timing.

### Tier 3: explicit currency / hedge layer

7. **VT + currency hedge overlay** (DBV / FXE). Hedge USD/EUR/JPY
   exposure when carry signal flips. `[ilmanen_expected_returns,
   ch.fx-carry]`.

8. **VT + EM commodity exposure** (DBA, DBC, GLD). Adds inflation
   hedge orthogonal to equity beta.

---

## What's reusable from `strategy_hunt_loop`

**Reuse directly** (no edits):
- `scoring.py` — same 0-100 rubric (parameterize benchmarks)
- `plot_helper.py` — same plot generator (parameterize benchmarks)
- `cross_lib_validator.py` — light cross-lib metric validation
- `long_window_validator.py` — pattern, with new strategies
- `rescore_v2.py` — relaxed DSR convention
- `WINNER_AND_RANKING.md` — strict criteria (only benchmark numbers
  change)
- `run_loop.sh` — shell orchestrator (CHANGE the path)

**Reuse with substitution** (parameterize):
- `BENCHMARKS` dict in `scoring.py` → swap to VT/VTI+VXUS/etc.
- `BENCH_PARQUETS` in `plot_helper.py` → add `vt_real`, `intl_real`.

**New for this loop**:
- `BENCHMARKS.json` (this loop's specific bench numbers, computed once
  upfront from VT.parquet)
- New universe filter in iter scaffolding
- DEAD_ENDS.md starts empty (different mechanism family from US-only
  loop)
- BASE_MEMORY.md starts fresh

---

## Pre-launch checklist (do these before activating loop)

- [ ] **Confirm tickers at Inter Internacional**: AVNM, AVUV, AVDV,
      AVEM, VT, VTI, VXUS, VWO, EWJ/EWG/EZU/EWU/MCHI/EWZ/INDA, TLT,
      IEF, ZROZ, GLD. Some may require IBKR.
- [ ] **Cache prices via Tiingo** for all confirmed tickers. Run
      `scripts/tiingo_bulk_pull.py` with the new ticker list.
- [ ] **Compute VT benchmark numbers** for `scoring.BENCHMARKS_GLOBAL`:
      VT Sharpe / CAGR / MDD on 17y window.
- [ ] **Decide benchmark hierarchy**: only-VT, only-VTI+VXUS-blend,
      or both? Affects `winner_conditions_met` definition.
- [ ] **Long-window data sourcing**: check if Avantis or another
      vendor publishes synth small-value backtests pre-2010. If not,
      accept 7-17y window.
- [ ] **Update PROMPT.md** for this loop: replace "SPY 1x buy-hold"
      bench with "VT 1x buy-hold"; replace dataset slugs (`spy_real`,
      `ndx_real`, `educational`) with new global slugs.
- [ ] **Decide MAX_ITER + ITER_TIMEOUT** for the new run.

---

## Files to create when activating

```
studies/global_factor_tilt_loop/
├── README.md                        ← this file
├── PROMPT.md                        ← copy + adapt from strategy_hunt_loop
├── BASE_MEMORY.md                   ← fresh, frontmatter only
├── DEAD_ENDS.md                     ← empty initially
├── WINNER_AND_RANKING.md            ← copy + adapt benchmark table
├── scoring.py                       ← copy + swap BENCHMARKS
├── plot_helper.py                   ← copy + swap BENCH_PARQUETS
├── cross_lib_validator.py           ← copy verbatim
├── long_window_validator.py         ← copy + new strategies
├── rescore_v2.py                    ← copy verbatim
├── run_loop.sh                      ← copy + change LOOP_DIR
├── INFRASTRUCTURE.md                ← copy + augment ticker list
└── iterations/                      ← empty
```

When activating, the first action is: **copy these files from
`studies/strategy_hunt_loop/`, run the pre-launch checklist, then
launch.**

---

## Branching strategy

Suggested: `global-factor-tilt/iter-NNN-NNN` branches off main, same
pattern as `strategy-hunt-relaxed/iter-075-100`. Keep this loop's work
isolated from gold_swing_loop and strategy_hunt_loop.

---

*Created 2026-04-26 in preparation. Awaiting gold_swing_loop completion
before activation.*
