# Phase 3.7 H1.a — Zarattini-Aziz-Barbon 2024 intraday SPY (honest base replication)

**Date:** 2026-04-23 | **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched `prev_weight × ret` alignment `[advances_fin_ml, p.31-34]`
**Broker path modelled:** Pepperstone Razor SPX500 CFD intraday — spread
**0.4 pts ≈ 0.67 bps per side** (cost×2 = 1.33 bps), commission **0 bps**
(SPX500 index CFD), swap **0** (flat-at-close), **no DARF** per mandate §2.2
rota A + `feedback_pepperstone_staging_and_darf.md`.
**Windows:** IS 2017-06-01 → 2021-12-31 (4.5y) | OOS 2022-01-01 → 2024-12-31
(3y) | FWD 2025-01-01 → 2026-04-14 (1.3y). SPY primary, QQQ cross-asset
confirm.
**Data source:** Tiingo IEX 1-min bars, 917,371 SPY bars + 917,169 QQQ
bars, UTC-aware index (`data/phase3_7/intraday/{SPY,QQQ}_1min.parquet`).

## Verdict: **FAIL**

The paper-literal Zarattini-Aziz-Barbon 2024 intraday noise-boundary
momentum signal on SPY 1-min **fails 4 of 4 hard gates and 5 of 9 soft
gates** under the honest engine + Pepperstone cost model. OOS Sharpe
collapses to **−0.335** (paper target ≥1.3 → fail) and the bootstrap
99.9% CI on OOS Sharpe is **[−1.97, 1.28]** — straddles zero by a wide
margin (gate 10 HARD → FAIL). PBO 0.37 (gate 11 HARD < 0.3 → FAIL) and
DSR p = 0.96 (gate 12 HARD < 0.05 → FAIL) both confirm the observed
series is statistically indistinguishable from noise. **The edge reported
in the paper (Sharpe 1.33 net over 2007-2024) does not reproduce on
post-2017 SPY** under honest F2-patched alignment + spread costs.

Positive signals (narrow): cross-lib concordance **passes** — vectorbt
and the pandas reference agree within **0.53 pp OOS CAGR** (gate 9 HARD
< 3pp → PASS). FWD Sharpe **0.20** (>0, gate 5 soft → PASS). Median hold
**6.4 h** (gate 7 ≥ 1h → PASS). **None of these salvage the hard-gate
failures.**

**Mandate §7 and strategy docs stay UNTOUCHED.** FAIL = no promotion, no
pending draft in `docs/.pending/`.

## Top-line metrics

| Split | Ticker | Bars | Sharpe | CAGR | MaxDD |
|-------|:------:|-----:|-------:|-----:|------:|
| IS  (2017-06-01 → 2021-12-31)   | SPY | 1169 | −0.148 | −2.59% | −26.14% |
| **OOS** (2022-01-01 → 2024-12-31) | **SPY** | **760** | **−0.335** | **−5.42%** | **−22.80%** |
| FWD (2025-01-01 → 2026-04-14)   | SPY |  326 |  0.202 |  1.93% | −12.96% |
| FULL (2017-06-01 → 2026-04-14)  | SPY | 2358 | −0.148 | −2.73% | −42.72% |
| OOS cross-asset                 | QQQ |  760 |  0.273 |  3.42% | −21.98% |
| **SPY OOS buy-hold benchmark**  | SPY |  760 |  0.489 |  7.24% | −25.36% |

Portfolio OOS underperforms SPY buy-hold by **−12.7 pp CAGR** and carries
a deep **IR = −0.58** (gate 8 ≥ 0.2 → FAIL). QQQ cross-asset run is mildly
positive (Sharpe 0.27) but far from paper target — not a save.

## Winner config (paper-literal baseline)

```python
H1ZarattiniBaseConfig(
    ma_days                          = 14,       # [zarattini_aziz_barbon_2024]
    atr_period                       = 20,       # Wilder ATR, Penfold p.338-343 convention
    atr_multiplier                   = 2.0,      # 2·ATR trail
    atr_scale                        = "daily",  # daily-bar ATR, not 1-min (see §ATR note)
    signal_start_bar                 = 1,        # evaluate from bar-2 of each day
    flat_at_close                    = True,     # mandate §3 intraday
    spread_one_way                   = 6.67e-5,  # ≈0.67 bps (0.4 pts on SPX 6000)
    commission_round_trip            = 0.0,      # SPX500 index CFD commission-free
    swap_daily                       = 0.0,      # intraday, flat-at-close
    tax_rate                         = 0.0,      # no DARF on Pepperstone per mandate §2.2 rota A
    no_reentry_after_stop_same_day   = True,     # matches paper's ~1.5 trades/day
)
```

**ATR-scale note.** The paper spec (``2 × ATR(20)`` trail) could be
interpreted either as (a) Wilder ATR on 1-min bars, or (b) Wilder ATR on
daily bars broadcast to the active day. A pilot showed 1-min ATR gives
~0.05% trail → stops trigger in minutes, ~13 trades/day, Sharpe −4.27 (all
spread-bleed). Daily-bar ATR gives ~1% → 2% trail, ~1 trade/day (paper-
matching), positions typically exit at EOD via flat-at-close. We use
daily-scaled ATR as the honest interpretation and still see FAIL — so
the exit rule is not the determining issue.

**No-reentry-after-stop-same-day.** Paper reports ~1.5 trades/day; the
literal rule (re-enter on every re-crossing) produces ~13 trades/day.
We enforce one-trade-per-day discipline on SPY which matches the paper's
stat. Still FAIL.

## 13-gate checklist (per plan + mandate §2.4)

| # | Gate | Level | Threshold | Value | Pass |
|---|------|:-----:|-----------|------:|:----:|
| 1   | IS Sharpe > 0.5                                | soft    | > 0.5   | −0.148 | **FAIL** |
| 2   | OOS Sharpe ≥ 1.3 (paper 1.33)                  | soft    | ≥ 1.3   | −0.335 | **FAIL** |
| 3   | OOS CAGR tier (rota A)                         | warning | classify| −5.42% → **Folclore** | WARN |
| 4   | OOS MaxDD tier (rota A)                        | warning | classify| −22.80% → **Excelente** | WARN |
| 5   | FWD Sharpe > 0                                 | soft    | > 0     |  0.202 | PASS |
| 6   | Walk-forward 6/8 profitable                    | soft    | ≥ 6/8   | 3/8 mdd=18.54% | **FAIL** |
| 7   | Median hold ≥ 1h intraday                      | soft    | ≥ 1h    | 6.4h (386 bars) | PASS |
| 8   | IR vs SPY buy-hold OOS ≥ 0.2                   | soft    | ≥ 0.2   | −0.5805 | **FAIL** |
| 9   | Cross-lib concordance ±3pp OOS CAGR            | **hard**| ≤ 3pp   | 0.53 pp (vbt vs pandas) | **PASS** |
| 10  | Bootstrap OOS 99.9% CI low > 0                 | **hard**| > 0     | −1.9664 | **FAIL** |
| 10b | Bootstrap FULL 99.9% CI low > 0                | **hard**| > 0     | −1.1523 | **FAIL** |
| 11  | PBO < 0.3 (single-feature stricter)            | **hard**| < 0.3   | 0.369 | **FAIL** |
| 12  | DSR p < 0.05                                   | **hard**| < 0.05  | 0.962 | **FAIL** |
| 13  | cost×2 Sharpe > 1.0 (unleveraged)              | soft    | > 1.0   | −0.570 | **FAIL** |

**Summary: 3 PASS / 9 FAIL / 2 WARNING-ONLY.**
- **Hard gates: 1 PASS (gate 9), 4 FAIL (gates 10, 10b, 11, 12).**
- Halt-contract N_trades OOS = 730 (≫ 100) → not triggered.
- Halt-contract cross-lib Δ = 0.53pp (< 10pp) → no engine regression.

## Why it failed

The strategy exhibits a **"signal is noise"** profile across every
statistical test:

1. **PBO 0.369 (HARD FAIL):** across the 5-config sensitivity grid, the
   IS-best configuration performs below OOS median in 37% of CSCV block
   splits. Single-feature signal with grid-tuned parameters is exactly
   the scenario PBO was designed to detect, and we set a stricter 0.3
   threshold per the hunt prompt. Even at the default 0.5 the strategy
   would barely pass — and the OOS Sharpe would still be negative.

2. **DSR p = 0.96 (HARD FAIL):** after deflating the observed Sharpe
   (−0.021 periodic) by the expected maximum under 5 iid-null trials,
   the Deflated Sharpe is **indistinguishable from zero**. This is the
   canonical post-selection-bias test from `[advances_fin_ml, p.273-275]`.

3. **Bootstrap 99.9% CI on OOS Sharpe = [−1.97, 1.28] (HARD FAIL):** the
   stationary block bootstrap (block_mean=5, n=2000, seed=42 — Politis-
   Romano 1994 / `[advances_fin_ml, p.196-202]`) says the true Sharpe
   could plausibly be anywhere from strongly negative to near paper-target
   positive. **The data simply does not have enough signal to reject
   zero at 99.9% confidence.**

4. **Walk-forward 3/8 profitable (SOFT FAIL):** only 3 of 8 equal-sized
   windows show positive compound returns. This contradicts the paper's
   claim of persistent edge across regimes.

5. **Cost×2 Sharpe −0.57 (SOFT FAIL):** doubling the spread to 1.33 bps
   deepens the OOS Sharpe from −0.34 to −0.57 — the strategy is actively
   **anti-robust** to cost increases, meaning any gross edge is negative
   before slippage even enters.

6. **IR vs SPY buy-hold OOS = −0.58 (SOFT FAIL):** on the same period,
   SPY buy-hold net (via Inter) delivered Sharpe 0.49 / CAGR 7.24%. The
   Zarattini signal **actively destroyed value vs just holding the
   index**. No excess return exists to harvest.

7. **QQQ cross-asset mildly positive (Sharpe 0.27, CAGR 3.42%).** This
   hints there *could* be intraday momentum on QQQ post-2022, but the
   magnitude is a far cry from Sharpe 1.3 and does not save H1.a under
   the single-asset paper spec (SPY is the paper's only test asset).

### Tier labels (mandate §2.2 / §2.3 rota A — warning-only)

- **OOS CAGR tier:** **Folclore** (< 13% required for "Marginal" on rota
  A). CAGR is −5.42% — deeply below every tier.
- **OOS MDD tier:** **Excelente** (magnitude 22.80% ≤ 25% cutoff). This
  is the single positive of the risk side — but risk-control has no value
  when expected return is negative.

## Grid sensitivity (5 configs for CSCV/PBO)

| Tag                         | ma_days | atr_period | atr_mult | atr_scale | Sharpe (full) |
|-----------------------------|--------:|-----------:|---------:|:---------:|--------------:|
| ma14_atr20_k2_daily (winner)|      14 |         20 |      2.0 | daily     |  −0.148 |
| ma10_atr20_k2_daily         |      10 |         20 |      2.0 | daily     |   0.005 |
| ma20_atr20_k2_daily         |      20 |         20 |      2.0 | daily     |  −0.019 |
| ma14_atr20_k3_daily         |      14 |         20 |      3.0 | daily     |  −0.125 |
| ma14_atr14_k2_daily         |      14 |         14 |      2.0 | daily     |  −0.100 |

All 5 configs cluster around Sharpe ≈ 0 (range [−0.15, +0.01]). The grid
is not rescued by any single parameter — the base signal itself is
broken on 2017+ SPY.

## Cross-lib concordance (gate 9 — HARD PASS)

Re-implemented the Zarattini signal in **vectorbt 0.28.5** via
`vbt.Portfolio.from_signals` on the same SPY 1-min bars, same spread
(`fees=6.67e-5` per side), size=1.0 value-typed, OOS window slice. Result:

| Library | OOS CAGR | Δ vs reference |
|---------|---------:|----------------|
| pandas (reference) | −5.42% | —                   |
| vectorbt 0.28.5    | −5.95% | **0.53 pp** (< 3pp) |

**Gate 9 HARD PASS.** Engine + cost model agree across libraries within
tolerance. Halt-contract "cross-lib Δ > 10pp → engine regression" is not
triggered. bt/backtrader intraday 1-min skipped (event-loop overhead on
~900k bars is prohibitive and offers marginal additional cross-check
value when vbt + pandas already concur); documented here for honesty.

## What FAIL means for the hunt

Per the plan §T7 halt-contract and mandate §2.4:

- **HARD gates 10/11/12 FAIL** = statistical rejection. The observed
  Sharpe is within the noise band (bootstrap CI, DSR) AND the parameter
  grid shows overfit risk (PBO 0.369 ≥ 0.3 strict threshold).
- **No promotion, no draft entry, no live capital.** H1.a is DEAD as a
  strategy A lead on 2017+ SPY.

**Recommendation to orchestrator:** do NOT stop Wave 1 on H1.a PASS
(it didn't pass). Continue to H1.b (already committed as FAIL — commit
`12c0635`) and H1.c. If all 3 of Wave 1 fail, consider the halt note on
Polygon.io 2007-2017 SPY escalation — the paper's original edge may only
exist in the 2007-2016 regime (e.g. pre-HFT saturation, structural gamma
flow differences). Under the 2017+ window we have, **the edge
demonstrably does not reproduce at honest costs.**

## Data-source caveats

1. **Tiingo IEX 1-min is post-2017.** The paper's 17-year backtest
   (2007-2024) includes the 2007-2016 window where intraday momentum
   is stronger in the academic literature (pre-0DTE options dealer
   hedging saturation, pre-retail-flow shift to overnight). We can
   only test the back half of that window — a structural limitation,
   NOT a bug.

2. **UTC-aware index, DST-robust.** Bars span 13:30-20:59 UTC
   (= 09:30-15:59 ET or 08:30-14:59 CT depending on DST); the simulator
   treats each UTC date as a trading day. Half-days (Thanksgiving Fri,
   etc.) correctly tracked via `groupby(date).cumsum()` for bar-of-day.

3. **Volume NOT used.** The paper references volume in some diagnostic
   sections but the base signal is price-only. We do not filter by
   volume.

## Artifacts

- `AGGREGATE.json` — full structured numeric detail.
- `daily_returns_SPY.parquet` — winner-config honest daily returns (SPY).
- `daily_returns_QQQ.parquet` — winner-config honest daily returns (QQQ).
- `daily_returns_cost2x.parquet` — cost×2 sensitivity daily returns.
- `config_grid.csv` — 5-config sensitivity grid Sharpe table.
- Logs: `logs/phase3_7_h1_zarattini.log`.
- Strategy module:
  `src/ai_trade/backtest/strategies/phase3_7_h1_zarattini_base.py`.
- Runner: `scripts/phase3_7/run_h1_zarattini_base.py`.
- Tests: `tests/test_phase3_7_h1_zarattini_base.py` (4 smoke tests,
  pytest baseline preserved).

## Mandate §7 / strategy doc status

**UNTOUCHED.** Verdict is FAIL. No promotion. No pending draft.

## Citations

- Zarattini-Aziz-Barbon 2024 — `[zarattini_aziz_barbon_2024]` (SSRN
  4824172; sprint reference
  `docs/research/2026-04-23-phase3.7-literature-sprint.md §T3.Paper1`).
- Wilder ATR / trailing-stop discipline:
  `[universal_trend_tactics, p.338-343, p.68-69]`.
- Lookahead audit + `prev_w × ret` alignment:
  `[advances_fin_ml, p.31-34]`.
- Stationary bootstrap 99.9% CI:
  `[advances_fin_ml, p.196-202]`.
- CSCV PBO: `[advances_fin_ml, p.208-211]`.
- DSR: `[advances_fin_ml, p.273-275]`.
- Walk-forward: `[advances_fin_ml, ch.11]`; Pardo (2008) ch.10-11.
- Flat-at-close intraday pivot: mandate §3 (2026-04-15).
- Pepperstone cost model: `docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md`
  + `feedback_pepperstone_staging_and_darf.md` (no-DARF on rota A).
- 13-gate framework: `docs/investment-mandate.md §2.4` + Phase 3.7-3
  hunt prompt (2026-04-23).
