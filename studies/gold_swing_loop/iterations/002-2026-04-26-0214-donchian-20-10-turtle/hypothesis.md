# Iteration 002 — Donchian-20/10 channel breakout (Turtle System 2 lite) on gold

## Hypothesis

Replace iter 001's mean-reversion entry (Connors RSI(2)<5) with a
**momentum-breakout entry** (Donchian-20 channel break) and replace
the SMA(5) exit with a **channel exit** (Donchian-10 opposite-side
break). On gold's persistent-trend regime profile, momentum entries
should ride the trend instead of fighting pullbacks; opposite-channel
exit lets winners run until trend reverses, instead of being chopped
off by an SMA cross at the first bounce.

In symbolic form:

* **Long entry**: when flat AND `close[t] >= rolling_max(close, 20)[t]`.
* **Short entry** (Track A only): when flat AND `close[t] <= rolling_min(close, 20)[t]`.
* **Exit long**: when long AND `close[t] <= rolling_min(close, 10)[t-1]`.
  *(Note: the `t-1` shift on the exit channel prevents look-ahead and
  ensures the exit channel is computed BEFORE the current bar.)*
* **Exit short** (Track A only): when short AND `close[t] >= rolling_max(close, 10)[t-1]`.

No leverage. Position sizing binary {−1, 0, +1} on Track A; {0, +1} on Track B.

## Primary citation

`[trend_following, Covel]` — channel-breakout philosophy ("the trend is
your friend; cut losses, let winners run") with Donchian as the
canonical implementation. Faith's *Way of the Turtle* (1983 Dennis-Eckhardt
Turtle program, "System 2") used 55-day entry / 20-day exit; the
20/10 variant is the standardized fast-Turtle for shorter time-frames.

## Additional citations

* `[stocks_on_the_move, p.81]` — Clenow's relative-strength regression
  uses an analogous channel-break logic (90-day lookback equivalents);
  endorses momentum entries with volatility-aware exits on commodities/equities.
* `[trading_systems_methods, Kaufman, ch.20]` — channel-breakout systems
  with adaptive lookbacks; documents the "20/10" as a shorter-cycle
  Turtle variant.
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest validation
  (Pepperstone CFD model is mandatory).
* `[advances_fin_ml, p.222-223]` — DSR / PSR with cumulative n_trials.

## Edge source

Gold exhibits persistent multi-month trends (2008-2011 +260%, 2018-2024
+95%, 2022-2024 +30%). XAUUSD buy-hold captures these trends but pays
~22-46% MDD during the inevitable counter-rallies. Donchian-20/10
breakout aims to:

1. **Enter** only after momentum is confirmed (close at a new 20-day
   high), avoiding the chop in range-bound regimes.
2. **Exit** when the dominant trend pauses (close at a new 10-day low),
   preserving capital during corrections.
3. Capture Sharpe uplift via lower MDD (sit out the worst counter-rallies)
   without sacrificing too much CAGR.

The structurally **OPPOSITE** family from GS-1: where MR fades pullbacks,
Donchian rides confirmations. Both can fail (gold has neither pure trends
nor pure mean-reversion in all regimes), but they fail in DIFFERENT ways
and at DIFFERENT times — so a positive result here would close the
question of which family fits gold day/swing.

## Datasets

* **gld_long** (GLD daily, 21.4y): primary test. Mixed regime
  (2008 bull, 2011-2018 chop, 2018+ second bull) — discriminates
  trend-follow's regime sensitivity.
* **xauusd_real** (XAUUSD daily, 6.3y): bull-only regime since 2020.
  Should be the "easy" dataset for a trend-follower; if it FAILS here,
  the family is structurally dead.
* **xauusd_intraday** (XAUUSD 1h, 6.3y, daily-resampled): same as
  xauusd_real but using the 1h dataset's daily-resample. Confirms the
  result is not an artifact of the daily-spot data quirks.

## Timeframes used

`[1d]` only — Donchian-20/10 is a daily-bar strategy. The
`xauusd_intraday` dataset is resampled 1h → 1d (last close per UTC day,
matching iter 001's protocol via `resample_1h_to_daily`). Sub-1h
timeframes (30m/15m/1m) **are NOT used** — no need for cTrader API fetch.

## Broker tracks targeted

`broker_track: "both"`.

* **Track A — Pepperstone CFD**: BIDIRECTIONAL (long+short). Holds 20-30 days
  on average → multi-night swap accrues. Cost model: spread 8 bps RT +
  swap −1 bps/night long, +0.3 bps/night short, 3× weekend multiplier.
* **Track B — Inter ETF (GLD)**: LONG-ONLY (drops short signals to flat).
  Daily settlement; no intraday round-trips. Cost: 100 bps FX RT +
  DARF 15% on positive monthly net profit. **Caveat (GS-2)**: expected
  ~10-20 trades/yr on this strategy → marginal Track-B viability
  (FX cost ≈ 100-200 bps/yr drag). Will report both, but primary is Track A.

## Hold-time profile (HARD GATE)

* Expected mean hold: **~20-30 trading days** (Donchian-20/10 design).
* Intraday-only (swap-free): NO — multi-night swing.
* **Swing-extended tag**: yes. This iteration **CANNOT** declare WINNER
  even at score ≥ 90 because mean hold > 5 days. Maximum tier achievable
  is **STRONG (75-89)**. Justification per loop spec: closing the
  trend-follow direction question (entry vs exit defect in GS-1) is
  high-information at this stage; a positive STRONG result would inform
  iter 003+ to test compressed-hold variants (3-day drift, EMA fast cross)
  that ARE winner-eligible.

## Kill criterion (pre-committed)

If `Sharpe_strategy_net_of_costs < Sharpe_buy_hold − 0.05` on **≥ 2 of 3**
datasets, the hypothesis is falsified — trend-follow entries do NOT
help gold day/swing (closes the broad trend-follow family for this
loop). Tier downgrades to FAIL or NEAR_FAIL regardless of secondary
metrics.

This mirrors iter 001's kill criterion symmetrically. Negative kill
result → pivot to direction #2 (MR with 200d-SMA trend filter,
Connors' own fix) or #3 (macro-overlay DXY z-score) per BASE_MEMORY.

## Pre-validation screen (IC-6)

**Not applicable** — Donchian-20/10 is a standalone single-mechanism
strategy, not an overlay or composition. The IC-6 mandate
(`exceed_frac(|ρ| > 0.30) > 20% → abort`) requires a base position to
correlate against; this iter has no base. IC-6 will apply when iter 003+
tests compositions (Markowitz combo per IC-7).

## Cost model (per track)

### Track A (Pepperstone CFD)

* Spread: 8 bps round-trip (4 bps per side, applied on `|position.diff()|`)
* Swap long: −1 bps/night per +1.0 long unit
* Swap short: +0.3 bps/night per −1.0 short unit
* Weekend multiplier: 3× swap on Friday-close hold (Mon bar charged)
* Slippage on stops: not modeled (Donchian uses close-based trigger,
  not stop-loss orders, so slip is implicit in the close-vs-trigger gap)
* Intraday-close: `False` (multi-night swing)

Expected drag: at ~10 trades/yr × (8 bps spread + ~22 nights × 1 bps swap)
= ~302 bps/yr ≈ 3% CAGR drag. Manageable on a +13% benchmark.

### Track B (Inter ETF)

* FX RT: 100 bps per round-trip (50 bps per side)
* DARF: 15% × max(0, sum_monthly_pretax_net) — applied to last bar of month
* No swap (ETF), no brokerage (Inter zero-fee)
* GLD ETF expense ratio (40 bps/yr) already netted in NAV — informational

Expected drag: at ~10 trades/yr × 100 bps FX = ~1 000 bps/yr = ~10% CAGR
drag. Plus DARF ~1.5%/yr on a +13% gross. Total ~11.5% drag — KILLS
buy-hold edge unless gross alpha is +15-20%/yr, which is unlikely from
a single-mechanism trend-follower.

Per GS-2 dead-end rule: Track-B verdict will likely be NEAR_FAIL/FAIL;
report for completeness but Track A is the primary scoring track.

## Expected budget

* **Configs to test**: 1 (Donchian-20/10 only — no parameter sweep per IC-8).
  Increments `cumulative_n_trials` from 1 → 2.
* **Wall-time**: ~3-5 minutes (3 datasets × Donchian computation + gate suite).
* **Files to create** (this iter directory):
  - `hypothesis.md` (this file)
  - `run_backtest.py` (adapted from iter 001)
  - `donchian_signal.py` (helper module — small, may inline in run_backtest.py)
  - `results.json` (per-dataset metrics + gate outcomes + returns series)
  - `verdict.json` (score_strategy() output + winner conditions)
  - `final_report.md` (Stage 5)

## Implementation plan

1. **Adapt run_backtest.py** from iter 001 — replace `connors_rsi2_signal`
   with `donchian_breakout_signal(df, entry_lookback=20, exit_lookback=10,
   long_only=False)`. Reuse `wilder_rsi`-style structure (state machine
   with anti-look-ahead via `t-1` shifting on exit channel).
2. **Track A**: bidirectional position (`+1`, `0`, `−1`).
3. **Track B**: same signal, but clip to `max(position, 0)` — drops shorts
   to flat; long-only enforced by `apply_inter_costs_with_darf`.
4. **Gates** per dataset (G1 PBO degenerate single-cfg pass, G2 PSR/DSR,
   G3 walk-forward 8 windows, G4 OOS 70/30, G5 FWD post-2022, G6
   bootstrap 99.9% CI, G7 cross-lib ±3 pp CAGR via numpy reference).
5. **Scoring** via `scoring.score_strategy()` with cumulative_n_trials=2
   (iter 001's 1 + this iter's 1).
6. **Hold-time gate** computed and reported separately; expected FAIL
   (mean > 5 days), tier capped at STRONG.
7. **Cross-lib G7** mandatory: hand-rolled numpy reference of Donchian
   logic to confirm pandas computation matches within ±3 pp CAGR.

## Pre-commit notes

* Single config — no grid sweep on `entry_lookback ∈ {15, 20, 25}` or
  `exit_lookback ∈ {5, 10, 15}`. Per IC-8: pre-commit the canonical
  20/10 variant; if it fails, pivot family rather than tune.
* Kill criterion is observable BEFORE running the gate suite (just need
  Sharpe_net comparison) — use this to short-circuit if necessary,
  saving DSR trial budget on a kill.
