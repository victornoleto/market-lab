# Iteration 021 — DCOT money-manager net-long z-score (contrarian, post-2006)

## Hypothesis

Replace iter 018's legacy-COT commercials bucket with the **disaggregated
COT (DCOT) money-manager bucket**, which isolates pure speculative flow
from producer hedging. Compute the rolling 156-week z-score of money-
manager net longs (`m_money_positions_long_all − m_money_positions_short_all`),
lag 1 week (next Tuesday close on Friday's report), and apply contrarian
gating: **enter LONG when z < −1.0σ** (MM speculators positioned
extreme-bearish → contrarian buy), exit when z > 0 (positioning
normalized) or after `max_hold_days = 30`. Long-only, single-asset, on
gold spot.

This is the natural mirror of iter 018: iter 018 went long when
commercials z (i.e., `NL_comm − NL_small`) was extreme-positive, on the
theory that commercials lead. Money-manager bucket is the speculative-
side mirror of that signal — same `[trading_systems_methods, p.640]`
hedging-pressure tradition, but with the cleaner post-2006 disaggregated
bucket that excludes producer hedging entirely.

## Primary citation

`[trading_systems_methods, p.640]` — Kaufman: COT positioning extremes
as contrarian signal; "money manager" bucket on the disaggregated
report isolates speculator flow with less producer noise than the
legacy non-commercial bucket.

## Additional citations

- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials=21`
  (this iter increments by 1 vs iter 020's 20).
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest (Pepperstone
  CFD, 8 bps RT spread + −1 bps/calendar-night swap on long).
- de Roon, Nijman, Veld (2000) *J Finance* — "Hedging Pressure Effects
  in Futures Markets": z-score positioning theoretical anchor.
- Web: CFTC DCOT methodology docs
  (https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm)
  — DCOT introduced 2006-09-04 (verified empirically: gold series
  earliest row 2006-06-13).

## Edge source

Legacy non-commercials = money-managers + other-reportables, but
producer hedging contaminates the *commercial* bucket on the same
report. DCOT money-manager isolates the speculator wing only — if the
contrarian-positioning edge exists on gold, the MM bucket should
expose it more cleanly (less producer-hedging noise) than iter 018's
`NL_comm − NL_small` proxy. Standalone XAUUSD/GLD buy-hold misses this
because it has no positioning information; speculators-extreme-bearish
historically marks gold troughs (e.g., 2015 Q4, 2018 Q3) when MM net
longs collapse.

## Datasets

- **Primary: `gld_long`** sliced 2009-06-09 → 2026-04-15 (after 156w
  z-score warmup from DCOT 2006-06-13 start; ~16.85y, ~4 240 daily bars).
  Larger sample than xauusd_real and richer regime coverage (2009 GFC
  recovery, 2011 peak, 2013-2018 slow-bleed, 2019+ revival, 2020 COVID
  rally, 2022 rate-hike cycle).
- **Corroborating: `xauusd_real`** 2020-01-02 → 2026-04-17 (6.29y daily;
  DCOT z-score is fully warmed by then since DCOT data starts 13.5
  years earlier).

## Timeframes used

`1d` only (daily price + weekly DCOT forward-filled to daily index).

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A1).

- Track A (Pepperstone CFD): long-only signal works, no swap penalty
  beyond standard model. Reported as primary track.
- Track B (Inter ETF): long-only naturally fits, but DARF 15% drag
  + 100 bps FX RT not modeled — defer to post-winner cleanup if iter
  reaches WINNER tier.

## Hold-time profile

- Expected mean hold: 25-30 calendar days (similar to iter 018's 28.4d
  on gld_long), bounded by `max_hold_days = 30`.
- Bucket declared: **`medium_swing`** (10-30 days).
- NOT intraday-only; swap drag −1 bps/calendar-night on long is part
  of the cost model and is netted out in the reported Sharpe.

## Kill criteria (pre-committed)

If any of the following holds at end of Stage 3, this hypothesis is
falsified regardless of secondary metrics:

1. **No standalone edge**: gld_long net Sharpe < +0.20 (cost-net) over
   the post-warmup primary slice → MM bucket has no contrarian edge on
   gold; closes DCOT MM contrarian path.
2. **DSR no-progress**: gld_long primary DSR p-value > 0.30 at
   `n_trials=21` → no improvement vs iter 020's combined 0.36; closes
   single-stream DCOT MM path on gold.
3. **Not IC-7-eligible**: static daily ρ vs iter 003 RSI(2)+SMA(200)
   MR ≥ +0.50 on primary OR rolling-60d ρ exceedance fraction
   (|ρ| > 0.30) ≥ 20% on primary → fails IC-6 pre-val for any future
   IC-7 composition with iter 003.

Each kill is recorded explicitly in the final report. A "structural
new-mode close" (3 kills firing simultaneously) escalates to GS-21
closure of the entire DCOT MM contrarian family.

## Pre-validation screen (mandatory IC-6 measurement, not a kill on its own)

Compute static ρ and rolling-60d ρ exceedance vs iter 003 / iter 011 /
iter 015 / iter 017 / iter 018 on both gld_long and xauusd_real
(consistent daily granularity). This is data for future IC-7
candidacy — kill #3 only fires on iter 003 since that is the
canonical RSI MR base.

This iter is **not** a composition/overlay (it is a STANDALONE single-
mechanism test), so iter 003 ρ does NOT need to clear IC-7 thresholds
for this iter to score; the diagnostic is for downstream planning.

## Cost model

**Track A (Pepperstone XAUUSD CFD)**:
- Spread 8 bps round-trip (4 bps in + 4 bps out)
- Swap on long: −1 bps per calendar night (3× on Friday)
- No commission; no slippage modeled separately for daily-bar entries

For ~25-day mean hold: ~24 nights × −1 bps = −24 bps swap drag per
trade in addition to 8 bps spread RT → ~32 bps total cost per trade.
With ~12-15 trades/year (similar to iter 018), annual cost drag ~
4-5%. Required gross signal Sh > +0.4 to net positive at this drag
rate. (For comparison, iter 018's standalone Sh was +0.352 net
gld_long; cost recovery is in the right ballpark.)

## Expected budget

- Configs to test: **1** (IC-8: single pre-committed cfg, no grid)
- Wall-time: ~15-20 min (DCOT fetch + backtest + 7 gates + 5 ρ pairs)
- Files to create:
  - `fetch_dcot.py` — adapted from iter 017's `fetch_cftc.py` with
    DCOT endpoint + MM columns
  - `data/external/macro/cftc_dcot_gold_weekly.parquet` — cached fetch
    output (committed via shell loop)
  - `run_backtest.py` — adapted from iter 018's `run_backtest.py`,
    swapping `NL_diff` for `MM_NL` and inverting signal direction
  - `test_dcot.py` — TDD tests for `mm_net_long`, `zscore_signal_short`,
    DCOT loader (4-6 tests)
  - `results.json`, `verdict.json`, `final_report.md`

## Implementation plan

1. **Stage 3a (data infra)**: write `fetch_dcot.py`, fetch CFTC DCOT
   gold series (Socrata 72hh-3qpy, code 088691), keep `report_date`,
   `m_money_positions_long_all`, `m_money_positions_short_all`,
   `open_interest_all`. Cache to `data/external/macro/cftc_dcot_gold_weekly.parquet`.
   Verify ~1030 weekly rows from 2006-06-13 → 2026-04-21.
2. **Stage 3b (backtest)**: adapt `run_backtest.py` from iter 018:
   - Load DCOT, compute `MM_NL = mm_long − mm_short`
   - Rolling 156w z-score on `MM_NL`
   - Lag 1 week, forward-fill to daily index
   - Long when z < −1.0σ, exit when z > 0 OR `max_hold_days >= 30`
   - Apply Pepperstone cost model (8 bps spread + −1 bps/night swap)
   - Slice gld_long to post-warmup start (~2009-06-09 = first day with
     valid 156w z); xauusd_real already starts after warmup
3. **Stage 3c (gates + diagnostics)**: 7-gate battery (G1 PBO=True
   convention, G2 DSR p, G3 WF 8-window, G4 OOS 70/30, G5 FWD 2022+,
   G6 bootstrap 99.9% CI low, G7 cross-lib hand-rolled numpy).
   Correlation diagnostic vs iter 003/011/015/017/018 (daily granularity).
4. **Stage 3d (TDD)**: 5 tests in `test_dcot.py` exercising the new
   helpers: MM net-long compute, z-score sign-flip, signal state-machine
   (entry/exit/timeout), DCOT loader missing-column tolerance, cost
   model swap-on-long.
5. **Stage 4**: `score_strategy_v2(declared_primary='gld_long',
   declared_corroborating=['xauusd_real'], cumulative_n_trials=21)`
   + hold-time gate (compute mean_hold_days, check ∈ [10, 30]).
6. **Stage 5**: `final_report.md`, `verdict.json`, BASE_MEMORY +
   DEAD_ENDS update. Auto-prune BASE_MEMORY to <18KB.
