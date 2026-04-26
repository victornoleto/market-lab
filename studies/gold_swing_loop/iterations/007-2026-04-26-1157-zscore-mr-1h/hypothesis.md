# Iteration 007 — z-score mean-reversion MR on 1h gold (oversold-bounce)

## Hypothesis

Gold bars at z-score(60) < −2 (where z = (close − MA60) / std60) on the
1h timeframe are **temporarily oversold relative to recent realized
volatility**, and revert toward the mean within ~24 hours. Long-only
intraday MR: enter at bar where z < −2 (and not in a position); exit
when z ≥ 0 OR bars-held > 24 (1h dataset) or bars-held > 5 (daily
datasets, where 5 trading days ≈ same temporal scale). Pure
price-action — no macro, no calendar, no FX. Same mechanism applied to
all 3 datasets at TF-natural lookback (60 bars on 1h ≈ 60 hours;
20 bars on daily ≈ 1 calendar month — Chan ch.4 buy-on-gap precedent).

## Primary citation

`[algo_trading_chan, p.71-73, ch.3]` — Bollinger band z-score on a
stationary spread is the canonical price-only MR mechanism (Chan's
GLD-USO pairs example: APR 17.8%, Sharpe 0.96 on a cointegrated pair).
This iter applies the same z-score grammar to a SINGLE asset (gold);
the cointegration assumption is replaced by the empirical observation
that **short-term gold returns are weakly mean-reverting at intraday
horizons** (Chan p.45-46 ch.2 Hurst-exponent diagnostic on USD.CAD
suggests $H \approx 0.49$ for analogous FX/commodity data — to verify
on gold via pre-val).

## Additional citations

- `[algo_trading_chan, p.94-95, ch.4]` — buy-on-gap intraday MR with
  20-day lookback for vol normalization; Chan's RULE [p.95]: apply
  momentum/regime filter on top of MR if needed (deferred — first
  baseline without filter).
- `[algo_trading_chan, p.47, ch.2]` — half-life lookback rule: set
  moving-average lookback to a small multiple of the mean-reversion
  half-life. Pre-val will estimate half-life on z-score series.
- `[trading_systems_methods, Kaufman]` — short-term oversold MR is
  the standard intraday "fade" pattern; gold has well-documented
  pullback-revert behavior intraday.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 7`.

## Edge source

Gold buy-hold captures the asset's persistent ~11%/yr drift. What it
misses: the **intraday vol-normalized pullback**. When z(60h) drops
below −2σ on 1h, gold has just made a sharp short-horizon move down
that is statistically extreme relative to its own recent vol. If price
is stationary at this timescale (Hurst < 0.5 on 1h log-returns, to
confirm pre-val), the bar-level reversion-to-mean dominates the macro
drift — for ~24h. Buy-hold sits through these draws; this strategy
front-runs the bounce. The key empirical question is whether the
pullback-to-mean signal-to-noise ratio is high enough on gold's 1h
data to overcome the 8 bps round-trip Pepperstone cost.

## Datasets

- **gld_long** (GLD daily, 21.4y) — daily-bar version: lookback=20d,
  timeout=5d, z<-2 entry. Mean hold ≤ 5 trading days (HARD GATE
  boundary). Long-history cross-check; **gld_long not directly
  intraday but enables 21y validation of the MR mechanism's stationarity**.
- **xauusd_real** (XAUUSD daily, 6.3y) — daily-bar version: lookback=20d,
  timeout=5d. Direct gold cost-realistic.
- **xauusd_intraday** (XAUUSD 1h, 6.3y, ~32k bars) — **PRIMARY**:
  lookback=60h, timeout=24h. Strategy's natural habitat; sidesteps
  GS-4/5/6 macro-regime trap by operating below the timescale at which
  macro drivers manifest.

## Timeframes used

`["1d", "1h"]` (1d for gld_long + xauusd_real; 1h for xauusd_intraday).
Both available in Tiingo cache. No fine-TF (30m/15m/1m) deferral
needed.

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A). Track B (Inter ETF) will
be reported with **GS-2 cost-cliff caveat** — at est. ~50-100 trades/yr
on 1h, FX RT cost (100 bps × ~75 trades) decimates returns; Track A
is the only viable execution path for an intraday strategy.

## Hold-time profile (HARD GATE)

- **Expected mean hold:**
  - 1h: 12-20 bars (mean) × (252/5119) ≈ 0.6-1.0 trading days
  - daily: 2.5-3.5 bars (mean) ≈ 2.5-3.5 trading days
- **Intraday-only?** No — position can carry overnight (up to 24h on
  1h, up to 5d on daily). Modeled as Track A swap-accruing, with
  swap rate scaled to TF (1 bps/night = (1/24) bps/bar on 1h).
- **Swing-extended risk?** No — both daily configs target ~3 day mean
  hold (well within ≤5d gate); 1h targets ~1 day. Position state
  machine forces exit at the timeout; MDD on extreme-stress windows
  is bounded by the hold-time cap.

## Kill criteria (pre-committed)

**Pre-validation kill** (Stage 3a, before backtest):

If on `xauusd_intraday`, the forward 24-bar log-return after z<-2
entries gives:
- mean fwd_24h log-return < 0 (signal directionally inverted), OR
- t-stat ≤ 0 over n_events ≥ 50

→ AUTO-ABORT (same as iter 005 DXY closure). z-score MR on intraday
gold is structurally inverted; mark GS-7 closure (intraday MR
mechanically fails on gold) and pivot to candidate #13 (realized-vol
regime gate) next iter.

**Backtest kill** (Stage 3b, after backtest):

If full Track-A backtest on `xauusd_intraday` (the strategy's primary
dataset) shows:
- net Sharpe ≤ 0 after Pepperstone costs, OR
- net Sharpe < 0 on ≥ 2 of 3 datasets

→ FAIL (per WINNER_AND_RANKING.md §1: cross-dataset positive Sharpe
required).

## Pre-validation screen (mandatory diagnostic)

Even though IC-6 strictly applies to OVERLAY/COMPOSITION candidates
(this iter is single-mech base), I run a directional pre-val on 1h
to:
1. Confirm signal direction (sign of mean fwd return after entry
   trigger)
2. Estimate event count + statistical power on 1h and daily
3. Compute base/signal correlation with iter 003 MR for IC-7 prep
4. Check ρ(z<-2 entry, vol_position) for IC-1 sanity (must be < 0.85)

This is diagnostic; the strategy is committed regardless (1 cfg, no
sweep per IC-8). Pre-val cost ~10s, vetoes signal-inverted starts.

## Cost model (per track)

**Track A (Pepperstone XAUUSD CFD)**:

- Spread: 8 bps round-trip (per `cost_models.py` PEPPERSTONE_SPREAD_RT_BPS)
- Swap long: −1 bps/night for daily; **−1/24 bps/bar for 1h** (this
  iter uses the per-bar accrual approximation: at 1h granularity, the
  −1 bps/night charge is spread evenly across 24 hourly bars).
  Mathematically equivalent to discrete overnight charge for positions
  held a full 24h; small bias for sub-day holds (under-charges 0.5 bps
  for a 12h hold avg, vs discrete model ~0.5 bps avg). Acceptable.
- Weekend mult: 3.0× on Friday-close holds (only relevant for daily
  positions held over weekend; 1h timeout=24h means no weekend cross
  except for entries Friday afternoon).
- `intraday_close=False` for both TFs (positions carry overnight).

**Track B (Inter ETF)**: GS-2 cost cliff applies (100 bps FX RT × ~75
trades/yr on 1h ≈ 750 bps/yr drag). Reported for completeness; not a
viable deployment path.

## Expected budget

- Configs to test: **1** (pre-committed, no sweep — IC-8 discipline)
- cumulative_n_trials after this iter: **7** (= 6 + 1)
- Wall-time: ~5-8 minutes (1h dataset has 32k bars; bootstrap on 1h
  takes ~1-2 min; rest is fast)
- Files to create: `hypothesis.md`, `run_backtest.py`,
  `test_zscore_mr_signal.py`, `results.json`, `verdict.json`,
  `final_report.md`, `pre_val.json`

## Implementation plan

1. **TDD test** (`test_zscore_mr_signal.py`): verify position state
   machine on a synthetic z-series with known entry/exit triggers.
2. **`run_backtest.py`** scaffold (copy iter 003's structure):
   - `zscore_mr_signal(df, lookback, timeout, z_entry=-2, z_exit=0)` —
     returns position series.
   - `run_pre_val(df, lookback=60, fwd=24)` — measures n_events, mean
     fwd return, t-stat, hit-rate on entry triggers (xauusd_intraday only).
   - `run_one_dataset(name)` — full 7-gate run; per-TF lookback/timeout/ann.
3. **Pre-val** on xauusd_intraday → `pre_val.json`. If killed, write
   minimal `final_report.md` with FAIL + GS-7 closure and stop.
4. **Full backtest** on 3 datasets if pre-val passes.
5. **Score** via `scoring.score_strategy` + hold-time gate per WINNER §6.
6. **Write** `results.json`, `verdict.json`, `final_report.md`.
7. **Update** BASE_MEMORY (iteration log, top-K maybe), DEAD_ENDS if
   structural closure.

## Why this iter is structurally novel

1. **Mechanism family**: pure z-score (price − MA / std) on raw price
   series. Different from:
   - iter 001/003 (Wilder RSI(2) on gain/loss-of-changes — different
     normalization grammar)
   - iter 002 (Donchian breakout — opposite direction, trend not MR)
   - iter 004 (VIX cross-asset — closed by GS-4)
   - iter 005 (DXY cross-asset — closed by GS-5)
   - iter 006 (FOMC calendar — closed by GS-6)

2. **Timeframe**: primary execution on 1h (vs all prior iters on
   daily). Sidesteps the GS-4/5/6 macro-regime non-stationarity wall
   because intraday MR operates below the timescale at which macro
   drivers manifest.

3. **Exit mechanic**: hard time-based timeout vs SMA-cross (iter 001/
   003) or fixed N-day hold (iter 002/004/005/006). Time-stop discipline
   matches Chan's RULE [p.183-184, ch.8] (`NEVER impose stop losses
   that fire in backtest`) — z-score timeout is symmetric and
   regime-stationary.

## Known risks (to watch in results)

1. **Anti-pattern from DEAD_ENDS** (`Daily mean-reversion on gold
   trend regimes`): pure MR loses ~50% premium during gold's 2001-
   2011 and 2018-2024 strong uptrends. Test will reveal if this
   applies at 1h timescale (likely less severe — intraday vol cycles
   are stationary even in trending macro regimes).

2. **GS-3 trap**: single-mech standalone on gold is dominated by
   buy-hold drift. Iter 003's MR-with-SMA200 already established this
   for daily. The 1h variant might escape if the per-trade edge × turnover
   compounds to ≥ buy-hold drift, but this is empirical.

3. **Cost-cliff at high turnover** (similar mechanism to GS-6): on
   1h, expected ~75 trades/yr × 8 bps = 600 bps/yr just on spread.
   If gross edge per trade is < 8 bps, net is negative regardless.
   Pre-val will surface mean edge magnitude.

4. **Spread asymmetry on 1h**: Pepperstone Razor's published 1.4 bps/leg
   is an average across day; off-hours spreads can be 5-10 bps/leg.
   The 8 bps RT modeled is conservative for liquid hours but optimistic
   for late Asia / post-NY-close hours. Future iter may stratify by
   session if results are borderline.
