# Iteration 005 — DXY z-score down-cross + 5-day fixed hold (fundamentals macro overlay on gold)

## Hypothesis

When the dollar (DXY proxy) is *unusually weak relative to its recent
60-day distribution* AND has *just crossed* into that unusually-weak
state from above (z down-cross through −1.0), gold's expected forward
return over the next 5 trading days is positive and meaningfully higher
than the unconditional buy-hold mean. This is the **fundamentals-macro
overlay** complement to iter 004's stress-driven cross-asset overlay
(VIX recovery): both are cross-asset, but the signal source is
qualitatively different — iter 004 read RISK-OFF flows (equity stress
spilling into safe-haven gold), iter 005 reads CARRY/CURRENCY-DRIVER
flows (USD weakness mechanically lifting gold via the inverse
USD-priced-commodity relationship).

The strategy enters long gold when the DXY z-score down-crosses through
−1, holds for fixed 5 trading days (HARD GATE pass by construction),
then enforces a 5-day cooldown before next eligibility. Long-only,
binary {0, 1}, no leverage, no stops. Single pre-committed config per
IC-8.

## Primary citation

`[ilmanen_expected_returns, ch.10]` — Ilmanen documents gold's expected
return decomposition: inflation hedge (~50%), USD hedge (~30%), real-
yield hedge (~20%); USD weakness is among the two most-cited
fundamental drivers of gold's risk premium. The "USD-weak / DXY z<−1"
state is exactly the regime where Ilmanen flags expected gold return
as elevated.

## Additional citations

- `[trading_systems_methods, p.301-310]` — Kaufman regime-conditional
  entry methodology (event-driven trigger + fixed hold pattern reused
  from iter 004's framing, applied to a different signal source).
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- `[short_term_trading_strategies, p.105-118]` — Connors regime-filter
  pattern (analogous: "only enter long when regime favors long");
  here regime = USD weakness rather than gold uptrend.
- Web: Bauer, M. D., & Mertens, T. M. (2018). "Information in the Yield
  Curve about Future Recessions." FRBSF Economic Letter 2018-19; and
  Erb, C. B., & Harvey, C. R. (2013). "The Golden Dilemma." *Financial
  Analysts Journal* 69(4), 10-42 — empirical decomposition of gold
  returns showing DXY weakening explains ~30-40% of monthly gold
  variance over the 1975-2012 sample.

## Edge source

XAUUSD buy-hold is unconditionally long gold across all USD regimes,
including the regimes where USD strength mechanically suppresses gold
returns. By being long ONLY when USD has just crossed into unusually-
weak territory (and accepting being flat the rest of the time), the
strategy concentrates exposure on the empirically high-conditional-
return state. The edge is regime-conditional: trade frequency × per-
trade lift > buy-hold mean × time-in-market only if the conditional
lift is large enough to offset the lower coverage. iter 004 attempted
this same logic on a stress signal (VIX) and failed cross-dataset; the
hypothesis here is that a fundamentals signal will be more regime-
robust because it reads gold's primary mechanical driver directly.

## Datasets

- **gld_long** (GLD daily, 21.4 y, 2004-11-18 → 2026-04-15) — long-
  history validation; needs ≥ ~30 trigger events for reasonable
  statistical power; mixed regimes (GFC, 2011 peak, 2013-18 stagnation,
  2019-25 revival).
- **xauusd_real** (XAUUSD daily, 6.3 y, 2020-01-02 → 2026-04-17) —
  short-history corroboration on the actual instrument; the cross-
  dataset robustness check that iter 004 *failed*. If iter 005 also
  fails here, that closes "any cross-asset overlay framing" on Tiingo's
  current XAUUSD coverage.
- **xauusd_intraday** (XAUUSD 1h, 6.3 y, same calendar) — daily-
  resampled; same signal frequency as `xauusd_real`. Included for
  formal cross-dataset gate consistency; signal is daily-bar so the
  intraday TF doesn't add structural information here.

## Timeframes used

`["1d"]` — daily-bar signal on all three datasets (the 1h dataset is
daily-resampled, mirroring iter 003's and iter 004's pattern). No fine-
TF (30m/15m/1m) data needed; cTrader fetch deferred.

## Broker tracks targeted

`broker_track: "both"` (primary `pepperstone_cfd`, secondary
`inter_etf`). Will report metrics for both. Track-B viability depends
on trigger frequency: if mean turnover ≤ 12 trades/yr (per GS-2 cliff),
Track B is viable; ≥ 25 trades/yr forces Track-A only. iter 004
recorded ~4 trades/yr on a similar event-trigger framework, so
**4-12 trades/yr is the expected range** — squarely Track-B viable
unless the entry threshold proves too loose.

## Hold-time profile (HARD GATE)

- Expected mean hold: **exactly 5 trading days** (by construction)
- Intraday-only: NO; multi-day swing → swap accrues on Track A
  (5 nights × −1 bps = −5 bps per trade swap drag, plus weekend 3×
  multiplier when Friday-close hold occurs; cost model handles this
  per `cost_models.py`).
- Swing-extended tag: NO; mean hold is exactly 5 d → within HARD GATE.

## Kill criteria (pre-committed)

If at end of testing **AT LEAST 2 of 3 datasets** show **negative
Track-A Sharpe** AND **at most 1 dataset** shows positive Track-A
Sharpe, mark FAIL with structural verdict: "fundamentals macro
overlay (DXY) is regime-fragile on Tiingo's coverage; same closure
pattern as iter 004's stress overlay (GS-4); generalize to GS-5
'cross-asset overlays as PRIMARY gold-entry triggers fail on short
data, regardless of stress-vs-fundamental signal source.'"

If exactly 1 dataset shows negative Sharpe but the other 2 are positive
and gates pass, mark PROMISING / MARGINAL — partial robustness, candidate
for IC-7 composition.

If all 3 datasets show positive Track-A Sharpe AND ≥ 2 beat benchmark
+0.10 AND DSR p < 0.05 with cumulative n_trials = 5, then WINNER tier
is achievable (subject to other gates).

## Pre-validation screen (mandatory; IC-6 spirit)

iter 005 is a STANDALONE strategy (signal generates entries, not an
overlay onto another strategy), so the strict IC-6 cointegration check
doesn't apply. The relevant pre-val is: **does the trigger event have
positive forward 5-d gold return predictive power on the long-history
dataset?**

```
1. Load GLD daily (gld_long); load usdcad/usdchf/usdjpy daily.
2. Align indices (inner-join on common business days).
3. DXY_proxy = (log(usdcad) + log(usdchf) + log(usdjpy)) / 3
4. z = (DXY_proxy - rolling_mean(60)) / rolling_std(60)
5. Identify trigger events: bars where z[t] < -1.0 AND z[t-1] >= -1.0.
6. For each trigger, compute forward 5-d gold log-return:
   r_5d = log(close[t+5] / close[t]).
7. Compute t-stat of r_5d distribution: t = mean / (std / sqrt(N)).
8. Compute hit-rate: fraction of triggers where r_5d > 0.
```

**Abort iter** if any of:
- N events < 20 in the 21-y gld_long window (insufficient statistical
  power; the thresholding is too tight or the cross is too rare)
- t-stat < 0.5 (no meaningful directional forward edge)
- hit-rate < 0.50 (worse than coin-flip)

**Continue iter** if all three thresholds clear.

This pre-val takes ~30 s and saves a wasted DSR trial if the signal
has no raw predictive power.

## Cost model (per track)

**Track A (Pepperstone XAUUSD CFD)**: spread 8 bps round-trip + swap
−1 bps × 5 nights/trade = ~−13 bps per trade in expected drag (more if
Friday-close hold incurs weekend 3× multiplier). At ~6 trades/yr, that's
~−78 bps/yr cost drag — small relative to the gold buy-hold ~7-13%
CAGR but enough to flip a marginal raw edge to net-negative if the
trigger is poorly aligned. `cost_models.apply_pepperstone_costs(...,
intraday_close=False)` handles this.

**Track B (Inter Internacional GLD ETF)**: 100 bps FX RT per trade ×
~6 trades/yr = ~−60 bps/yr FX drag, PLUS DARF 15% on positive monthly
net profits (asymmetric — losing months don't refund). DARF eats ~10-
15% of pre-tax CAGR. Reported but not the primary track. ETF EER
(40 bps/yr GLD or 25 bps/yr IAU) is netted from price; not added.

## Expected budget

- Configs to test: **1** (per IC-8: pre-committed, single cfg, no
  parameter sweep). Adding any sweep (z threshold ∈ {−0.75, −1.0,
  −1.25, −1.5}, hold ∈ {3, 5, 7, 10}, cooldown ∈ {3, 5, 10}) would
  drain DSR cumulative trial count by 6-12 additional trials in one
  iter — negative-EV per IC-8.
- Wall-time: ~30-60 minutes (single backtest × 3 datasets × 7 gates +
  bootstrap 2000-sample × 3 datasets).
- Files to create:
  - `iterations/005-*/hypothesis.md` (this file)
  - `iterations/005-*/run_backtest.py` (single script; reuses
    `cost_models.py`, `datasets.py`, `scoring.py` from loop level)
  - `iterations/005-*/test_dxy_signal.py` (TDD: 3-5 unit tests for
    DXY proxy construction, z-score computation, down-cross detection,
    and hold/cooldown state machine)
  - `iterations/005-*/results.json` (per-dataset metrics, gates,
    returns_series for plotting + IC-7 cross-iter correlation)
  - `iterations/005-*/verdict.json` (score + winner check + dual-track
    metrics)
  - `iterations/005-*/final_report.md` (Stage 5 deliverable)

## Implementation plan

1. **TDD**: write `test_dxy_signal.py` with 3-5 tests covering
   - DXY proxy = (log(usdcad)+log(usdchf)+log(usdjpy))/3 on a synthetic
     3-bar fixture (verify formula)
   - z-score uses 60-bar rolling mean/std (NaN warmup; first valid bar
     at index 60)
   - Down-cross detection: z[t] < −1 AND z[t−1] >= −1 fires exactly
     once at the cross bar, no repeats while z stays below
   - 5-day fixed hold + 5-day cooldown state machine: trigger at t →
     position[t..t+4] = 1, position[t+5..t+9] = 0 (cooldown), eligible
     again at t+10
   - GS-2 cliff sanity: assert n_trades_per_year ≤ 12 on at least one
     dataset (Track-B viability claim)

2. **Implementation** (`run_backtest.py`):
   - Load gold dataset (gld_long / xauusd_real / xauusd_intraday;
     resample 1h → daily for the intraday case, mirroring iter 003)
   - Load 3 FX series (usdcad / usdchf / usdjpy) from
     `data/tiingo/daily/prices/`
   - Inner-join on common business days; build DXY_proxy + z-score
   - Generate position series via down-cross + 5-day hold + 5-day
     cooldown state machine
   - Apply cost models (Track A and Track B); compute metrics; run
     7-gate battery; score
   - Compute kill-criterion check (≥ 2 datasets with negative Sharpe)
   - Save `results.json` (with `_returns_series` for IC-7 cross-iter
     corr) + `verdict.json`

3. **Stage 4 — score** via `score_strategy(metrics, gates,
   cumulative_n_trials=5)`. Note: `cumulative_n_trials` increments
   from 4 → 5 (iters 001+002+003+004+005 = 5 single-cfg attempts).

4. **Stage 5 — final_report.md** with full transparency: pre-val
   t-stat / hit-rate, Track-A and Track-B per-dataset metrics, gate
   table, score breakdown, what worked / what didn't, structural
   lesson, IC-7 composition prep (correlation of iter 005 PnL vs iter
   003 MR PnL on common bars; whether composition is unblocked).
