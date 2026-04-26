# Iteration 014 — TIPS DFII10 macro stream (long XAU when 10y real rate is falling)

## Hypothesis

Gold's primary fundamental driver is the **10-year TIPS yield (DFII10)** —
the real rate. When real rates fall, gold's opportunity cost (the
risk-free real return foregone by holding a non-yielding asset) drops,
and gold is in its bull regime. When real rates rise, gold structurally
underperforms even amid nominal-yield drama.

**Signal (single pre-committed cfg per IC-8):**

> Long XAU on day `t` if `DFII10[t] < DFII10[t - 60 trading days]`
> (10y TIPS yield is *falling* on a 60-day rolling window).
> Flat otherwise.

Daily decision, daily rebalance. Long-only — short side has been
historically dangerous on gold (iter 002 closure GS-3) and the macro
mechanism is asymmetric (real-rate spikes do happen but mean-revert
quickly; falling-rate regimes persist).

## Primary citation

`[trading_systems_methods, p.13]` — Kaufman: low-noise markets (metals,
long-maturity bonds) favor trend-following, with real-rate moves the
underlying low-noise driver. The 60-day window matches Kaufman's
quarterly horizon (`p.285`) for macro-regime classification.

## Additional citations

- `[trading_systems_methods, p.285]` — 252-day MA = annual macro benchmark; the 60-day window picks a quarterly subset for swing horizon.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 14` (13 prior iters + this one).
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline (Pepperstone Track A 8 bps RT + −1 bps/night swap).
- Web — Erb & Harvey (2013) *"The Golden Dilemma"* (Financial Analysts Journal 69:4) — empirical study of gold's relationship to real interest rates over 1975-2012; finds inverse correlation with real-rate level.
- Web — Bauer & Mertens (2018) "Information shocks and Treasury rates" (FRBSF Working Paper) — TIPS-implied real-rate dynamics drive cross-asset reactions.

## Edge source

XAUUSD buy-hold doesn't distinguish between real-rate-falling regimes
(gold's bull regime) and real-rate-rising regimes (gold's bear regime).
A single binary regime gate based on DFII10 momentum should capture
~50-70% of buy-hold's positive months while filtering out ~70%+ of
the negative drift periods. Net Sharpe should rise via the same
mechanism as iter 011 (vol-regime gate) but on a fundamentally
different family — macro/real-rates instead of price-action volatility.

The crucial structural difference vs iter 010-013:

- iter 010-013 use price-derived signals (`σ`, `SMA`, `RSI`); they all
  share the same family ceiling on gld_long because the deficit lives
  in 2008-2009 GFC + 2018-2019 sideways + 2022 inversion regimes that
  price-derived signals struggle to bridge.
- DFII10 is **exogenous** to gold's price action; it should *correlate
  by ~0* with iter 011's σ_60<σ_252 gate over rolling windows. This is
  the **family orthogonality** GS-12 boundary requires for IC-7
  composition uplift in iter 015+.

## Datasets

- **gld_long** (GLD daily, 21.4 y; 2004-11-18 → 2026-04-15): full window for the 21-y context check. DFII10 covers from 2003-01-02 → so all gld_long bars have a valid DFII10 reading.
- **xauusd_real** (XAUUSD daily, 6.3 y; 2020-01-02 → 2026-04-17): the cost-realistic actual instrument; recent regime (post-COVID, post-Fed-hiking).
- **xauusd_intraday** (XAUUSD 1h, 6.3 y; same window): macro signal is daily-resampled (DFII10 is published daily); intraday backtest uses the same daily flag forward-filled across the day's hourly bars.

## Timeframes used

- **1d** for signal (DFII10 published once per business day at FRED close)
- **1d** for execution on gld_long and xauusd_real
- **1h** forward-filled daily flag for xauusd_intraday (same propagation pattern as iter 011 / 012 / 013)

## Broker tracks targeted

- **`broker_track: pepperstone_cfd`** (Track A only).
- Track B (Inter ETF, GLD long) is also long-only and would work in principle, but per BASE_MEMORY closure GS-2 the FX-cliff at high turnover is destructive; this iter focuses on Track A. If the strategy delivers a STRONG on Track A, iter 015 could add Track B reporting.
- Cost model: 8 bps spread RT + −1 bps/night swap (long position) — strategy holds long for full duration of falling-rate regimes (mean hold 2-3 months expected → 60-90 nights × −1 bps = −60 to −90 bps drag per trade).

## Hold-time profile (HARD GATE)

- **Expected mean hold: ~30-90 trading days** — real-rate cycles run quarterly; the 60-day momentum filter will produce mean-hold ~40-60 days based on prior cycle data (DFII10 has ~3-4 inflection points/year empirically).
- **Strategy is SWING-EXTENDED** — hold > 5 trading days. **Max tier: STRONG (no WINNER).**
- Justification for swing-extended: the macro/real-rate cycle operates at quarterly+ horizons; reducing hold below 5 days would force trading on noise, defeating the macro premise.
- Same swing-extended bucket as iter 011 (51d), iter 012 (43d), iter 013 (22d) — this iter is targeted at the same structural slot but in a fundamentally different family.

## Kill criteria (pre-committed)

If ANY of the following at end of Stage 3, the hypothesis is falsified:

1. **Signal has no real edge**: `p_active` (fraction of bars with long signal) > 90% or < 10% on any dataset (means the signal is binary-degenerate, i.e. always on or always off — would not be a regime gate).
2. **Sharpe regression vs iter 011**: gld_long Sharpe < 0.30 (iter 011's standalone gld_long Sharpe was +0.481; if the macro stream cannot reach 60% of that, the family hypothesis is broken).
3. **Cross-dataset divergence**: xauusd_real Sharpe Δ vs benchmark < 0.0 AND xauusd_intraday Sharpe Δ < 0.0 (means the macro signal works only on the long window via curve-fitting to 2008-2014 era).
4. **n_trades collapse**: gld_long n_trades < 5 (means the regime persists too long; not actually a "swing" candidate even at swing-extended tier).

## Pre-validation screen

This is a **standalone strategy**, not an overlay. IC-6 (correlation
pre-check vs base position) does not apply directly. However, I will
report the per-dataset signal statistics (`p_active`, mean signal
duration, n_regime_changes) before running the full backtest, and
abort if any kill criterion #1 or #4 fires.

## Cost model

**Track A (Pepperstone CFD)**:
- Spread: 8 bps round-trip per trade
- Swap (long): −1 bps/night (3× on Friday close for weekend)
- Slippage on stops: 5 bps (no stops in this strategy — swing-style with regime exit)

A typical trade holds ~60 calendar days = ~42 trading nights = ~−42 bps
swap drag, plus 8 bps spread = ~50 bps cost per trade. With ~5 trades/yr,
annualized cost ~250 bps/yr. Compares against expected gross gold return
in falling-rate regimes (estimated ~25-40%/yr from anecdotal regime
data) — should net positive comfortably.

## Expected budget

- Configs to test: **1** (pre-committed per IC-8 — single threshold, single window)
- Wall-time: ~30-60 min (FRED fetch ~30s + 3-dataset backtest + gate battery)
- Files to create:
  - `data/external/macro/dfii10_daily.parquet` — fetched FRED data
  - `scripts/data_sprint/ingest_dfii10_fred.py` — ingester (mirrors `ingest_vix_fred.py`)
  - `src/ai_trade/backtest/strategies/macro_dfii10_gold.py` — strategy module
  - `tests/test_macro_dfii10_gold.py` — TDD tests
  - `iterations/014-*/run_backtest.py` — driver script
  - `iterations/014-*/results.json` — per-dataset metrics
  - `iterations/014-*/verdict.json` — score result
  - `iterations/014-*/final_report.md` — Stage 5

## Implementation plan

1. **Fetch DFII10 from FRED**: adapt `ingest_vix_fred.py` for `series_id=DFII10`. Cache to `data/external/macro/dfii10_daily.parquet`. Verify date range covers 2003-01-02 → 2026-04-17+.
2. **Build signal vector**: `signal[t] = 1 if DFII10[t] < DFII10[t-60bd] else 0`. Forward-fill to align with each dataset's index.
3. **TDD test**: write `tests/test_macro_dfii10_gold.py` with synthetic DFII10 series → expected signal vector. Confirm 60-day-shift logic.
4. **Backtest on 3 datasets**: each dataset gets the daily signal forward-filled to the dataset's bar frequency. Compute net returns with Pepperstone Track A cost model. Save `results.json` with `index/net_returns/positions/n_trades/per_trade_attribution` per dataset.
5. **7-gate battery**: PBO (CSCV with 60d folds), DSR (n_trials=14), WF 8-window, OOS 70/30, FWD post-2022, Bootstrap 99.9%, Cross-lib (numpy reference for the 60d-shift signal computation).
6. **Score via `scoring.py`**: hold-time gate checked separately (will fail; expected swing-extended cap at STRONG).
7. **Final report + verdict.json + BASE_MEMORY/DEAD_ENDS update**.

## Distinct vs prior iters (structural novelty check)

- **iter 001-002** (RSI MR / Donchian TF): single-mech price-action — different family.
- **iter 003** (RSI(2) + SMA(200) filter): MR + trend filter — different family.
- **iter 004** (VIX recovery): equity-vol overlay — different signal (VIX is volatility-derived; DFII10 is macro fundamental).
- **iter 005** (DXY z-score): FX overlay — different signal, but adjacent family (cross-asset macro). Iter 005 was inverted on gld_long. Not a structural repeat.
- **iter 006** (pre-FOMC drift): calendar event — different family.
- **iter 007** (z-MR 1h): MR — different family.
- **iter 008-009** (XAU/XAG): cross-pair — different family.
- **iter 010-013** (vol-regime σ_60/σ_252 + filters): price-action vol family — exactly what this iter pivots away from.

DFII10 is **not a price-derived signal at all** — it's the 10y TIPS
yield, computed from off-the-run inflation-protected Treasury bond
prices (different security class, different curve segment). No prior
iter has used a Treasury-yield input.

## Inheritance from BASE_MEMORY

- BASE_MEMORY direction #1 (PROMOTED): TIPS DFII10 macro stream — this iter executes that.
- iter 013 final_report.md "Next iteration suggestions" priority 1 — pursued.
- IC-7 path consideration: if this iter's gld_long Sharpe ≥ 0.55 standalone AND DSR p < 0.10, it unlocks 2-stream IC-7 composition with iter 011/013 as second base in iter 015+. The 2-stream Markowitz at ρ ≈ 0 (different family) should compound DSR p < 0.05 on gld_long.
- IC-8 honored: single pre-committed cfg, no grid sweep on macro window.
