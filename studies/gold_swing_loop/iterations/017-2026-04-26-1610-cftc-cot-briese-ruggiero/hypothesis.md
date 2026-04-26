# Iteration 017 — Briese COT Index + Ruggiero rule on gold (long-only swing)

## Hypothesis

Gold's **price-discovery imbalance** between hedgers (commercials) and
small-trader speculators is a **stationary positional cycle that does
NOT share the macro/USD/realized-vol clock** that gates iters 003 / 011 /
014 / 015. Specifically:

- **Commercials** (gold producers, refiners, jewelry, central banks)
  are *price-makers* who systematically over-hedge into rallies and
  under-hedge into selloffs (information advantage about real demand).
- **Small traders** (non-reportable, < ~150 contracts) are
  trend-followers / sentiment-driven; they peak bullish near tops and
  bearish near bottoms.

Kaufman (2020), `[trading_systems_methods, p.639-640]`, formalises
the **Briese COT Index** = stochastic oscillator over 156 weeks
(~3 y) of net-long positions, scaled 0-100 per category. Ruggiero's
canonical rule (p.640):

> **Buy when Commercials COT Index (lagged 1+ week) > trigger AND
> Small Traders COT Index < trigger. Commercials' actions lead.**

The strategy goes long XAUUSD when this two-component condition fires
on the most recent CFTC release (lagged 1 week to avoid look-ahead),
holds until Commercials COTI < 50 OR Small COTI > 50 ("exit at neutral",
p.640) OR a 30-trading-day timeout.

## Primary citation

`[trading_systems_methods, p.639-640]` — Briese COT Index formula
(p.639) + Ruggiero rule + neutral-exit rule + lag guidance (p.640).

## Additional citations

- `[trading_systems_methods, p.482]` — "COT Index lag 1-several weeks
  per market; requires recalibration per asset" (Kaufman caveat we
  honour by pre-committing lag = 1 week, not sweeping).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (this iter increments to 17).
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest (every leg
  net of declared cost path).
- de Roon, Nijman, Veld (2000) "Hedging Pressure Effects in Futures
  Markets," *Journal of Finance* 55(3), 1437-1456 — cross-commodity
  evidence that hedger imbalance predicts futures returns.
- Sanders, Boris, Manfredo (2004) "Hedgers, Funds, and Small Speculators
  in the Energy Futures Markets," *Energy Economics* 26(3), 425-445 —
  Briese-style COT Index empirical validation.

## Edge source

Gold buy-hold misses the **mean-reverting positional crowding cycle**:
when small-trader speculators are extremely long AND commercials have
already covered most of their hedges, the market has consumed the
demand impulse and is structurally vulnerable to reversion. Symmetrically,
when commercials reload long hedges (rare — they are normally net short)
while small traders are bearish, real demand is signalling an under-
priced market. Buy-hold treats every day equal; this strategy concentrates
exposure on the ~5-15 % of weeks where the positional spread is at its
historical extreme.

## Datasets

- **gld_long** — PRIMARY. CFTC weekly Gold (code 088691) covers
  1986-01-15 → 2026-04-21 (1 913 records); GLD daily 2004-11-18 →
  2026-04-15 (5 384 bars). Full coverage; the 21.4 y window includes
  3 macro regimes (1986-2000 stagnation, 2001-2011 secular bull,
  2011-2018 stagnation, 2019+ revival).
- **xauusd_real** — CORROBORATING. Same CFTC weekly series joined to
  XAUUSD daily 2020-01-02 → 2026-04-17 (6.3 y).

`xauusd_intraday` and `gold_synth_40y` are **not used**: the signal
operates at weekly cadence; intraday bars would only add noise, and the
synth dataset is still un-built (deferred per BASE_MEMORY).

## Timeframes used

`["weekly_cot", "1d"]` — CFTC release once per week (Tuesday snapshot,
Friday release); position sizing applies on the next daily bar after
the release. No 4 h / 1 h / sub-1 h dependency.

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A only this iter).

- Long-only in this configuration; Track A's short-side and intraday
  are not exploited. Track B (Inter ETF) would also be applicable in
  principle but is **deferred** to a future iter — comparing per-track
  metrics on the same signal multiplies n_trials and per IC-8 we
  pre-commit a single track.

Expected DARF drag if Track B were used: ~10 % of CAGR (≥ 5 positive
months/year × 15 % each). Out of scope this iter.

## Hold-time profile (HARD GATE)

- **Declared track:** `medium_swing` (10 ≤ mean ≤ 30 trading days)
- Expected mean hold: ~15-25 trading days (the 30-day timeout caps
  the long tail; "exit at neutral" averages 3-5 weeks)
- Intraday-only: **N**

The 30-trading-day timeout is necessary to keep observed mean hold
inside the medium_swing 10-30 d band; without it, "exit at neutral"
alone can produce 35-50 d holds in slow regimes (would force a
declared-track mismatch → automatic NEAR_FAIL per scoring spec
§Part 1.6).

## Kill criteria (pre-committed)

If ANY of these happens at end of STAGE 3, hypothesis falsified:

1. **Trade count** — fewer than 10 round-trip trades on `gld_long`.
   The 21.4 y / weekly-signal universe should produce ≥ 25 trades; if
   the canonical Ruggiero thresholds (70 / 30) are too strict to fire
   that many, the strategy is structurally untradable and re-tuning
   thresholds would burn DSR (IC-8).
2. **Primary Sharpe < 0.30** on `gld_long`. Bench is 0.68 ; the +0.10
   edge requires Sharpe ≥ 0.78. If we don't even clear 0.30, the
   signal has no edge and IC-7 composition cannot rescue it
   (combined Sharpe ≤ √(S_A² + S_B²) per IC-3).
3. **Pre-val correlation with iter 003 (RSI(2)+SMA(200) MR) > 0.50**
   on `gld_long`. The whole structural-orthogonality argument for
   COT is that positioning is RESPONSE to macro/price, not on the
   macro clock. If ρ ≥ 0.50, COT is in the same family as iter 015's
   DXY-trend grammar (GS-15 / GS-16) and the IC-7 path is closed
   regardless.

## Pre-validation screen (mandatory for overlays per IC-6)

This is a **standalone** signal (not an overlay/composition with a
pre-existing base position), so the strict overlay-correlation
pre-val is N/A. However, kill criterion #3 is a *forward-looking*
pre-val for the IC-7 path that iter 018+ would build on top.

## Cost model (Track A — Pepperstone CFD)

- **Spread**: 8 bps round-trip per round-trip trade.
- **Swap (long)**: −1 bps per calendar night per lot.
- **Slippage on stops**: not modelled — entries and exits are at
  daily-close on the bar after the signal flip; no stop-loss orders
  this iter.
- **Mean total cost per trade**: spread 8 bps + swap (mean ~21
  trading-day hold × 7/5 calendar inflator × 1 bps/night) ≈ **8 + 29
  = 37 bps round-trip**.

The strategy's mean per-trade gross must clear ≥ 50 bps (1.5 × 37 bps
per IC-6 cost-magnitude rule of thumb) to count as having an edge.

## Expected budget

- **Configs to test:** 1 — Ruggiero canonical (Comm > 70, Small < 30,
  COT Index window = 156 weeks, lag = 1 week, exit at neutral 50 OR
  30-trading-day timeout). Pre-committed; no parameter sweep this iter
  (IC-8).
- **Wall-time:** ~30-45 min — 5 min CFTC fetch + 15 min implementation
  + 15 min backtest on 2 datasets + 10 min gates + report.
- **Files to create:**
  - `studies/gold_swing_loop/iterations/017-*/fetch_cftc.py` —
    one-shot CFTC pull; caches `data/external/macro/cftc_cot_gold_weekly.parquet`
  - `studies/gold_swing_loop/iterations/017-*/run_backtest.py` —
    Briese COT Index + Ruggiero signal + cost-net backtest
  - `studies/gold_swing_loop/iterations/017-*/test_cot.py` — TDD
    unit tests for COT Index formula + signal logic
  - `studies/gold_swing_loop/iterations/017-*/results.json`
  - `studies/gold_swing_loop/iterations/017-*/verdict.json`
  - `studies/gold_swing_loop/iterations/017-*/final_report.md`
  - `data/external/macro/cftc_cot_gold_weekly.parquet` (cache)

## Implementation plan

1. **Fetch** CFTC Legacy Futures-Only weekly reports for
   `cftc_contract_market_code = 088691` (Gold COMEX) via Socrata API
   `https://publicreporting.cftc.gov/resource/6dca-aqww.json` — paginated
   pulls, save raw + minimal parquet (date, comm_long, comm_short,
   nonrept_long, nonrept_short, open_interest_all). Range 1986-01-15 →
   latest. ~1 913 records expected.
2. **Briese COT Index** computation:
   ```
   NL_comm[t]  = comm_positions_long_all[t]  - comm_positions_short_all[t]
   NL_small[t] = nonrept_positions_long_all[t] - nonrept_positions_short_all[t]
   COTI_X[t]   = 100 * (NL_X[t] - min(NL_X, 156w window))
                 / (max(NL_X, 156w) - min(NL_X, 156w))
   ```
   Window = 156 weeks (3 y, midpoint of Kaufman's "1.5-4 y" range).
3. **Signal** (long-only, lag 1 week):
   ```
   long_t = (COTI_comm[w(t) - 1] > 70) AND (COTI_small[w(t) - 1] < 30)
   exit_t = (COTI_comm[w(t) - 1] < 50) OR (COTI_small[w(t) - 1] > 50)
            OR (days_in_position >= 30)
   ```
   `w(t)` = most recent CFTC report week ≤ daily bar `t`'s date − 7
   calendar days (Friday release lag).
4. **Position size**: 1.0 (full notional) when long, 0 otherwise.
   Single-asset, no Kelly/vol-targeting (would be a separate iter +
   another DSR trial; IC-8).
5. **Cost net**: per round-trip trade, deduct 8 bps spread; per long
   night, deduct 1 bps swap (calendar nights, not trading days).
6. **Datasets**:
   - `gld_long` — daily GLD close-to-close returns; 2004-11-18 →
     2026-04-15.
   - `xauusd_real` — daily XAUUSD close-to-close; 2020-01-02 →
     2026-04-17.
7. **Gates** G1-G7: PBO grid-level (single cfg → trivially N/A,
   reported as PASS by absence of grid), DSR p with
   cumulative_n_trials = 17, walk-forward 8 windows, 70/30 OOS,
   FWD post-2022, bootstrap 99.9 % CI, cross-lib numpy reference.
8. **Cross-lib** — numpy-pure reference of one full cycle (signal
   + cost + cumulative return) → ±3 pp CAGR vs primary engine.
9. **Score** via `score_strategy_v2(declared_primary="gld_long",
   declared_corroborating=["xauusd_real"], cumulative_n_trials=17)`.
10. **Hold-time gate** check (compute mean hold from trade list).

## Pre-committed correlation diagnostic (IC-7 prep, not gating)

After main backtest, compute Pearson ρ of (COT-strategy daily returns)
vs (iter 003 RSI(2)+SMA(200) daily returns) and (iter 011 vol-regime
daily returns) on the overlapping window, **at consistent daily
granularity** (per the GS-16 process correction). Report ρ values in
`results.json::correlation_diagnostic`. If primary kill criterion #3
fires (ρ ≥ 0.50 vs iter 003), tier this iter NEAR_FAIL regardless of
score and document the macro-clock confirmation in GS-17.
