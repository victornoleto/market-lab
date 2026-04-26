# Iteration 006 — Pre-FOMC drift T-2 to T+1 on gold (calendar-event signal, leverages gld_long 21.4y)

## Hypothesis

Gold's expected return is non-zero and positive over the four-trading-
day window centred on a scheduled FOMC announcement (entry at close of
T-2, exit at close of T+1, where T is the announcement date). The
hypothesis ports Lucca-Moench 2015's empirical pre-FOMC drift finding
(~+49 bps cumulative SPX return in the 24 hours before the announcement,
1994-2011) to gold and extends it by symmetric post-announcement window
to capture the typical FOMC reflex (rate-cut priors → gold rallies on
weaker USD).

The strategy is event-driven, **purely date-based** (no price-conditional
gate, no regime filter), single-cfg per IC-8. Position is binary {0, 1},
long-only, no leverage, no stops. Entry at close T-2; flat at close T+1.

This is the FIRST iter of the loop with a signal whose long-history
applicability extends back to the **earliest** edge of `gld_long`
(2004-11): scheduled FOMC dates have been published continuously since
1981, so all 21.4 y of GLD data carry a usable signal. iter 006 is
explicitly designed to dodge **GS-5** (Tiingo FX cache 2020+ window)
and **GS-4** (cross-asset stress signals regime-fragile on 2020+).

## Primary citation

`[trading_systems_methods, p.479]` — Kaufman documents the FOMC
calendar effect within his calendar-strategies chapter and recommends
the "trade through FOMC announcement" framework as a regime-conditional
overlay for any asset whose price is sensitive to monetary-policy
expectations. Gold is the canonical such asset (rate-sensitive carry
cost via real yields; flow-sensitive on USD direction).

## Additional citations

- Lucca, D. O. & Moench, E. (2015). "The Pre-FOMC Announcement Drift."
  *Journal of Finance* 70(1), 329-371. The seminal paper documenting the
  cumulative ~+49 bps drift in the S&P 500 over the 24 h pre-announcement
  window across 1994-2011 (157 events). Mechanisms proposed: information
  leakage, risk-on positioning, time-varying risk premium.
- `[ilmanen_expected_returns, ch.10]` — gold expected-return decomposition
  (USD hedge ~30%, real-yield hedge ~20%): both channels are activated
  by FOMC announcements, motivating a non-zero pre-FOMC drift on gold.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 6`.
- DEAD_ENDS GS-4 / GS-5 escape hatches — `studies/gold_swing_loop/DEAD_ENDS.md`.
- Web (cross-check): Federal Reserve Bank of New York, "Pre-FOMC
  Announcement Drift" Liberty Street Economics post (2013), reproducing
  Lucca-Moench finding on out-of-sample 2011-2013 extension.

## Edge source

XAUUSD buy-hold is unconditionally long gold across all calendar regimes.
Pre-FOMC drift, if it exists on gold, is a **time-localized risk premium
concentrated in 4 trading days × 8 events/year = 32 bars/year of total
position time** (~12.7% time in market). For the strategy to beat
buy-hold's Sharpe, the per-event drift must be sufficiently positive
relative to the unconditional gold return, AND the time-out-of-market
must shed the drawdowns that buy-hold absorbs (most of gold's MDD comes
in non-FOMC weeks: 2013 spring crash, 2015 USD spike, 2018 Q4, 2022
stagflation flip-flop).

The mechanical channel: FOMC announcements → reset in rate expectations
→ shift in real yields → gold price reaction. If markets systematically
PRICE-IN dovish surprises in the days running up to the announcement
(by analogy with SPX pre-FOMC drift), gold rallies pre-announcement
and continues post-announcement on the rate-cut confirmation.

If the channel is **purely equity-specific** (Lucca-Moench drift driven
by equity risk-on flow, with no commodity spillover), then gold's
pre-FOMC return distribution is centred at zero or even negative, and
the strategy fails immediately. **This is the structural risk** — the
same risk that classifies this hypothesis as MARGINAL conviction.

## Datasets

- **gld_long** (GLD daily, 21.4 y, 2004-11-18 → 2026-04-15) — primary
  validation. ~22 y × 8 FOMCs = ~170 events. Gold buy-hold Sharpe 0.68
  (measured iter 001). Long-history mixed regimes (GFC, 2011 peak,
  2013-18 stagnation, 2019-25 revival, COVID, stagflation, all-time-
  high cycle).
- **xauusd_real** (XAUUSD daily, 6.3 y, 2020-01-02 → 2026-04-17) —
  cross-dataset robustness. ~50 events. Gold buy-hold Sharpe 1.04.
  Same window where iter 004 (VIX) and iter 005 (DXY) failed.
- **xauusd_intraday** (XAUUSD 1h, 6.3 y, daily-resampled to match 1d
  signal) — formal cross-dataset gate consistency.

The 3-way replication is the critical robustness test: a true pre-FOMC
drift effect should appear on BOTH the long-history GLD ETF AND the
short-history XAUUSD spot, because the mechanism is calendar-driven,
not regime-driven.

## Timeframes used

`["1d"]` — daily-bar signal on all three datasets. The `xauusd_intraday`
1h bars are resampled to daily, mirroring iters 003-005. No fine-TF
(30m/15m/1m) data needed; cTrader fetch deferred.

## Broker tracks targeted

`broker_track: "both"` (primary `pepperstone_cfd`, secondary
`inter_etf`). Per GS-2 cliff (≥15 trades/yr → Track-B unviable),
**8 events/yr × 1 trade/event = 8 trades/yr is well below the cliff** →
Track B is fully viable. Will report per-track metrics. Track B will
incur DARF on positive months and 100 bps FX RT × 8/yr = 80 bps/yr
FX drag, which is small relative to gold buy-hold ~11-13% CAGR.

## Hold-time profile (HARD GATE)

- **Expected mean hold: 4 trading days exactly** (by construction:
  position[T-2..T+1] = 1, position[T+2..] = 0). Within HARD GATE (≤5).
- **Intraday-only**: NO; multi-day swing → Track A swap accrues
  (3 nights × −1 bps = −3 bps per trade, plus weekend 3× multiplier
  if Friday-close hold occurs; cost model handles this).
- **Swing-extended tag**: NO.

## Kill criteria (pre-committed)

If the **pre-validation screen** on gld_long shows any of:

- `n_events < 50` (insufficient statistical power across 21.4 y),
- `t-stat < 0.5` (no meaningful directional pre-FOMC drift on gold),
- `hit-rate < 0.50` (drift direction is worse than coin-flip),

then **abort iter** with structural verdict: "Lucca-Moench's pre-FOMC
drift is equity-specific; does NOT generalize to gold." Add **GS-6**
to DEAD_ENDS: "calendar-event signals from equity literature (pre-FOMC
drift, monthly TOM) do not port directly to gold; gold's reaction to
calendar events is dominated by USD-direction conditioning."

If pre-val passes but full-backtest **kill criterion** fires (≥ 2 of 3
datasets show negative Track-A Sharpe AND ≤ 1 dataset shows positive
Track-A Sharpe), mark FAIL with structural verdict: "pre-FOMC drift
is regime-dependent on gold (works on long-history but not on 2020+
regime), same closure pattern as GS-4 / GS-5."

If exactly 1 dataset shows negative Sharpe and the other 2 are positive
+ gates pass, mark PROMISING / MARGINAL — partial robustness, candidate
for IC-7 composition with iter 003 MR base.

If all 3 datasets show positive Track-A Sharpe AND ≥ 2 beat benchmark
+0.10 AND DSR p < 0.05 with cumulative `n_trials = 6`, then WINNER
tier is achievable (subject to other gates).

## Pre-validation screen (mandatory; IC-6 spirit)

iter 006 is a STANDALONE event-driven strategy (signal generates entries
from a calendar list, not an overlay onto another strategy), so the
strict IC-6 cointegration check doesn't apply. The relevant pre-val is:
**does the pre-FOMC window have positive forward gold return predictive
power on the long-history dataset?**

```
1. Load GLD daily (gld_long).
2. Load FOMC scheduled meeting dates 2004-2026 (hardcoded; verified).
3. For each FOMC date in [2004-11-18, 2026-04-15]:
   - Find T0 = announcement date in trading calendar (skip if not in
     dataset; FOMC dates are weekdays so usually direct match).
   - Find T-2 = 2 trading days before T0.
   - Find T+1 = 1 trading day after T0.
   - Compute log-return r = log(close[T+1] / close[T-2])  (4-day return).
4. Compute t-stat of r distribution: t = mean / (std / sqrt(N)).
5. Compute hit-rate: fraction of events where r > 0.
6. Compute mean cumulative log-return.
```

**Abort iter** if any of:
- N events < 50 in the 21-y gld_long window
- t-stat < 0.5 (no meaningful directional forward edge)
- hit-rate < 0.50 (worse than coin-flip)

**Continue iter** if all three thresholds clear.

This pre-val takes ~10 s and saves a wasted DSR trial if the signal
has no raw predictive power.

## Cost model (per track)

**Track A (Pepperstone XAUUSD CFD)**: spread 8 bps round-trip + swap
−1 bps × 3 nights/trade = ~−11 bps per trade in expected drag (more
if Friday-close hold incurs weekend 3× multiplier — most FOMC
announcements are Wed; T+1 = Thu, so weekend multiplier doesn't fire
for the typical announcement). At ~8 trades/yr, that's ~−88 bps/yr
cost drag — small relative to gold buy-hold ~11-13% CAGR.

**Track B (Inter Internacional GLD ETF)**: 100 bps FX RT per trade ×
~8 trades/yr = ~−80 bps/yr FX drag, PLUS DARF 15% on positive monthly
net profits (asymmetric — losing months don't refund). DARF eats ~10-
15% of pre-tax CAGR. Reported but not the primary track.

## Expected budget

- Configs to test: **1** (per IC-8: pre-committed, single cfg, no
  parameter sweep on hold_window, lookahead, etc.).
- Wall-time: ~30-60 minutes (single backtest × 3 datasets × 7 gates +
  bootstrap 2000-sample × 3 datasets).
- Files to create:
  - `iterations/006-*/hypothesis.md` (this file)
  - `iterations/006-*/run_backtest.py` (single script; reuses
    `cost_models.py`, `datasets.py`, `scoring.py` from loop level)
  - `iterations/006-*/test_pre_fomc_signal.py` (TDD: 3-5 unit tests
    for FOMC date parsing, T-2/T+1 trading-day arithmetic, position
    state machine, mean-hold = 4)
  - `iterations/006-*/results.json` (per-dataset metrics, gates,
    returns_series for plotting + IC-7 cross-iter correlation)
  - `iterations/006-*/verdict.json` (score + winner check + dual-track
    metrics)
  - `iterations/006-*/final_report.md` (Stage 5 deliverable)

## Implementation plan

1. **TDD**: write `test_pre_fomc_signal.py` with 3-5 tests covering
   - FOMC date list integrity (~170 events for 2004-2026, no
     duplicates, all weekdays, monotonically increasing)
   - Trading-day arithmetic: given a FOMC date and a sorted trading-
     calendar index, T-2 should return the index 2 positions before
     and T+1 should return the index 1 position after; both should
     return None if out of range
   - Position state machine: a single FOMC event should produce
     position == 1.0 at exactly 4 consecutive bars [T-2, T-1, T, T+1]
     and 0.0 elsewhere
   - Mean hold computation: with 8 events/yr × 22 years and
     non-overlapping windows, mean_hold should equal 4.0
   - Edge cases: FOMC date outside dataset window → no position
     contribution; consecutive FOMCs within 4 trading days → overlap
     handling (in practice doesn't occur — FOMCs are 6+ weeks apart)

2. **Implementation** (`run_backtest.py`):
   - Hardcoded FOMC announcement-date list 2004-2026 (~170 dates)
   - Pre-val on gld_long: compute T-2 → T+1 log-return per event,
     t-stat, hit-rate; abort if any threshold fails
   - Per dataset (gld_long / xauusd_real / xauusd_intraday daily-
     resample): generate position series via FOMC-date matching +
     T-2/T+1 trading-day indexing
   - Apply Track A and Track B cost models; compute metrics + 7-gate
     battery; score
   - Compute IC-7 cross-iter correlation with iter 003 MR base
   - Save results.json + verdict.json

3. **Stage 4 — score** via `score_strategy(metrics, gates,
   cumulative_n_trials=6)`. Note: `cumulative_n_trials` increments
   from 5 → 6 (iters 001+002+003+004+005+006 = 6 single-cfg attempts).

4. **Stage 5 — final_report.md** with full transparency: pre-val
   t-stat / hit-rate / mean cumulative log-return, Track-A and Track-B
   per-dataset metrics, gate table, score breakdown, what worked /
   what didn't, structural lesson, IC-7 composition prep (correlation
   of iter 006 PnL vs iter 003 MR PnL on common bars; whether
   composition is unblocked).
