# Iteration 003 — Connors RSI(2)<5 MR with SMA(200) trend-regime filter

## Hypothesis

Add a single regime gate (`close > SMA(200)`) to the iter 001 mean-reversion
entry so the strategy fires **only when gold is in an established uptrend**.
The exit rule (close > SMA(5)) is unchanged. Long-only, binary {0, 1}.
Connors himself documents this fix for short-term MR systems on assets
that have persistent trends — `[short_term_trading_strategies, p.105-118]`.

The hypothesis is that GS-1 (iter 001's failure) is rescuable BY ADDING
A REGIME GATE rather than abandoning the MR family entirely. If true,
this is the cheapest path to a positive Sharpe stream that can later
be combined (per IC-7) with a fundamentally different stream (macro,
VIX, calendar). If false, the MR family on single-asset gold is
**structurally dead** even with Connors' published fix → close it
permanently and pivot to fundamentally-different signal sources.

## Primary citation

`[short_term_trading_strategies, p.105-118]` — Connors' "trend filter"
chapter explicitly recommends the SMA(200) gate for RSI(2)<5 MR systems
on commodity-like instruments where pure MR fails. This is the
canonical published fix; not a custom variation.

## Additional citations

- `[short_term_trading_strategies, p.74-86]` — base RSI(2)<5 entry rule
  (carried forward from iter 001 unchanged)
- `[trading_systems_methods, p.301-310]` — Kaufman on regime-conditional
  MR ("MR works in mean-reverting regimes only")
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (this iter increments to 3)
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
- DEAD_ENDS GS-3 escape hatch #1 — explicit recommendation in
  `studies/gold_swing_loop/DEAD_ENDS.md` line 195-197

## Edge source

XAUUSD buy-hold captures 100% of bull-trend bars + 100% of bear-trend
bars (long-only equity drift). Pure RSI(2)<5 (iter 001) bought oversold
dips in BOTH regimes — but only ~40% were rescued by the next bar
because in downtrends the dip kept going. SMA(200) gate filters out
the downtrend dip-buys (which destroy capital on continuation moves)
while preserving the uptrend dip-buys (which mean-revert back to the
prior high quickly). **Edge = avoiding the asymmetric tail loss
on downtrend MR entries.**

## Datasets

All 3 datasets used (cross-dataset replication is non-negotiable):

- **gld_long** (GLD daily 21.4y, 2004-2026) — most informative;
  contains both 2008 GFC, 2011 ATH, 2013-2018 stagnation
  (where SMA(200) gate is OFF most of the time), and 2019-2026 revival
- **xauusd_real** (XAUUSD daily 6.3y, 2020-2026) — bull-only window;
  SMA(200) gate is ON ~85% of bars; expected lift small
- **xauusd_intraday** (XAUUSD 1h 6.3y, daily-resampled) — same
  underlying, daily-resampled to match dimensions

## Timeframes used

`["1d"]` — daily-only. xauusd_intraday is daily-resampled from 1h
(same convention as iter 001 + iter 002). No fine-TF needed; SMA(200)
is a daily indicator by construction.

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A only).

**Rationale for skipping Track B (Inter ETF):** GS-2 cliff (DEAD_ENDS
lines 205-227) — iter 001 ran ~135 trades/yr on the unfiltered version.
Adding the SMA(200) gate cuts entries in regions where the gate is OFF
(estimated ~30-40% of bars on gld_long), so this iter's turnover
projects to ~80-95 trades/yr. Still ~5-6× above the 15 trades/yr
break-even cliff for Inter's 100 bps FX RT. Track B remains
INELIGIBLE — same structural cost cliff applies. We DO compute and
report Track B metrics for completeness but treat them as confirmation
of GS-2, not a separate hypothesis.

## Hold-time profile

- Expected mean hold: **~3-5 trading days** (RSI(2) bounces are short;
  SMA(200) gate doesn't change exit timing — same SMA(5) exit as iter 001).
- Intraday-only: NO. Multi-day holds incur swap drag (−1 bps/night ×
  mean-hold 4d × 80 trades/yr = ~3.2 bps/yr drag — small).
- Mean hold expected ≤ 5 days → hold-time gate should PASS.
  **NOT swing-extended** by construction.

## Kill criteria (pre-committed)

This iteration is **falsified** (and GS-1 closed permanently) if BOTH
of the following hold at end of STAGE 4:

1. Sharpe lift on Track A < 0.10 over iter 001 on **all 3 datasets**
   (i.e., the regime gate provides no material lift). Iter 001's net
   Sharpes were +0.04 / −0.23 / −0.20; this iter must reach
   ≥ +0.14 / ≥ −0.13 / ≥ −0.10 on at least 1 dataset to claim
   "the regime gate worked."
2. Kill criterion #1 fires on ≥ 2/3 datasets simultaneously
   (cross-dataset confirmation of structural failure).

If kill criterion fires:
- Add **GS-4** to DEAD_ENDS: "MR-on-gold is structurally dead even
  with Connors' published SMA(200) fix; pivot to fundamentally
  different signal families (macro, VIX, calendar)"
- Promote VIX flight-to-quality (#4) or DXY z-score (#2) to top of
  candidate list for iter 004

If kill criterion does NOT fire (i.e., ≥ 1 dataset shows ≥ 0.10 lift):
- Track candidate in BASE_MEMORY top-K
- If full WINNER conditions met: halt loop
- If PROMISING/STRONG but not WINNER: queue for IC-7 composition with
  a complementary stream when available

## Pre-validation screen

**Skipped (not applicable).** IC-6 is for OVERLAYS that may correlate
with the base position. Here, SMA(200) is a **gate FILTER on the entry
condition** (not an additive overlay) — its purpose IS to be
correlated with the long-bias regime; that's the entire mechanism.
Architecturally distinct from IC-6's "overlay correlated with base
sizing" failure mode.

What we DO check at runtime as a sanity proxy:
- Trade count vs iter 001 — should drop by ~30-40% if gate is doing
  anything useful
- % of bars where SMA(200) gate is ON across each dataset (sanity
  check on regime distribution)

## Cost model

**Track A (Pepperstone)** — same as iter 001:
- 8 bps spread round-trip per turn
- −1 bps/night swap on long holds (mean ~4 nights × 80 trades/yr ≈ 320
  bps/yr swap drag)
- weekend Friday → Monday = 3× swap (informational; counted in metrics)
- intraday_close=False (multi-day holds normal for swing MR)

**Track B (Inter)** — reported for completeness but FX cost cliff
(GS-2) makes it structurally negative regardless of strategy edge.

## Expected budget

- Configs to test: **1** (single pre-committed config, IC-8 compliant)
- Wall-time: ~2-3 minutes (signal computation O(N), gates O(N))
- Files to create:
  - `hypothesis.md` (this file)
  - `test_rsi2_sma200_signal.py` (TDD; verifies gate behaves correctly)
  - `run_backtest.py` (mostly cloned from iter 001; signal API extended)
  - `results.json` + `verdict.json` + `final_report.md`

## Implementation plan

1. Write `test_rsi2_sma200_signal.py` (TDD-first) — 4-5 unit tests:
   - Gate filters out entries when close < SMA(200)
   - Gate allows entries when close > SMA(200)
   - SMA(200) NaN early bars → no entries (no look-ahead via min_periods)
   - Backward compat: `sma_trend_period=None` reproduces iter 001 signal
   - Exit rule unchanged (still close > SMA(5))
2. Extend `connors_rsi2_signal` in iter 003's `run_backtest.py` to
   take optional `sma_trend_period: int | None = 200`. When set,
   the entry condition gains `& (close > SMA(sma_trend_period))`.
   When None, behaves exactly like iter 001's signal.
3. `run_backtest.py` mostly cloned from iter 001:
   - CFG_ID = `"connors_rsi2_sma200_filter"`
   - CUMULATIVE_N_TRIALS = **3** (iter 001=1 + iter 002=1 + iter 003=1)
   - Track A primary; Track B reported with GS-2 caveat
   - Same 7-gate battery, same scoring helper, same hold-time gate
4. Run; produce `results.json`, `verdict.json`, `final_report.md`
5. Update BASE_MEMORY: iter log entry, top-K rank, frontmatter
   counters; auto-prune if > 18 KB
6. If kill criterion fires: append **GS-4** to DEAD_ENDS
