# Iteration 022 — GVZ implied-vol regime gate, contrarian long-on-low-IV

## Hypothesis

Buy gold (long-only) when the CBOE Gold ETF Volatility Index (GVZ) is at
an exceptionally low z-score (z < −1.0σ over a 252-day rolling window),
exit when z reverts to normal (z > 0) or after `max_hold_days = 30`. The
edge thesis: when the option market is pricing implied vol at multi-year
lows, the variance-risk-premium argument predicts a high probability of
upward IV mean-reversion, and on gold IV expansions historically coincide
with bullish price moves (stress-driven flight-to-quality, real-rate
compressions). Long-only contrarian — sell IV-cheapness, ride the
expansion.

## Primary citation

`[volatility_trading, p.32-37]` — Sinclair: implied-vol indices reflect
option-writer risk premia; low IV often precedes vol expansions
(variance-risk-premium framework). The contrarian "buy when IV cheap"
trade is formalized as the typical short-vega seller's exit signal —
in our setup, mirrored to the underlying spot side of the same trade.

## Additional citations

- `[trading_systems_methods, p.13-14]` — Kaufman: "vol regime" as a
  primary regime classifier; cheap vol = complacency window often
  preceding a regime change.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 22`.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest (apply
  Pepperstone Track A: 8 bps RT spread + −1 bps/night swap on long).
- Web: CBOE GVZ methodology white paper —
  https://www.cboe.com/us/indices/dashboard/gvz/ — GVZ is computed using
  the same 30-day model-free implied-vol formula as VIX, applied to GLD
  options. Series available on FRED as `GVZCLS` (2008-06-03 → present).
- Bollerslev, Tauchen, Zhou (2009) RFS — "Expected stock returns and
  variance risk premia". Variance-risk-premium-as-predictor framework
  for equity; the gold-IV variant we test here is the analogous
  trade.

## Edge source (one sentence)

GLD/XAUUSD buy-hold misses the contrarian asymmetry: when GVZ collapses
to multi-year low z-scores, the option market is implicitly forecasting
range-bound gold, but the variance-risk-premium predicts an asymmetric
upside in both vol AND price as the regime transitions to stress
(real-rate easing, FX dislocations, geopolitical risk-off).

## Datasets

- **gld_long (PRIMARY)** — GLD daily 2004-11-18 → 2026-04-15 (21.4y, 5384 bars).
  Sliced from **2009-06-04** (1 yr after GVZ inception 2008-06-03 to allow
  the 252-day z-score window to mature). Effective primary window
  ≈ 16.86y / 4 244 bars. Strict gate threshold: ≥ 5/7.
- **xauusd_real (CORROBORATING)** — XAUUSD spot daily 2020-01-02 →
  2026-04-17 (6.29y, 1700 bars). Already inside the GVZ-mature regime
  (GVZ has been live > 11 yr by 2020). Relaxed corroborating gate:
  G6 bootstrap CI low > 0 + G2 DSR p < 0.20.
- xauusd_intraday (NOT used) — GVZ is a daily series; intraday signals
  derived from a daily indicator add no information at sub-day granularity.

## Timeframes used

`1d` only. (GVZ is published as a single daily close; sub-daily granularity
not available without paid data.)

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A). Strategy is long-only with
multi-week holds (medium_swing); both Track A (Pepperstone CFD,
swap-bearing) and Track B (Inter ETF, DARF-bearing) would be deployable
in principle. We declare Track A as primary because:
- swap drag is well-modeled (1 bps/calendar-night per long lot)
- long-only nature is fine for both tracks (no short-side dropped)
- Track A cost path matches mandate §1's "Plano A reactivation research"
  framing
- Track B's DARF would only make returns worse — running it later is a
  follow-up exercise once Track A passes / fails.

## Hold-time profile (HARD-GATE-LIKE)

- Expected mean hold: ~15-25 trading days (z-score state-machine with
  exit at z > 0 and 30-day cap → typical position lasts 2-6 weeks).
- Intraday-only: NO.
- Track: `medium_swing` (hold-time bucket bounds: 10 ≤ mean ≤ 30 days).
- If observed mean hold lands < 10d, declared bucket mismatch ⇒ tier
  downgraded to NEAR_FAIL (process bug, not strategy failure).
- If observed mean > 30d, mismatch in the opposite direction.

## Pre-committed kill criteria

If ANY of the following is true at end of Stage 3, the iteration is
declared FAIL regardless of secondary metrics:

1. **Standalone primary Sharpe < +0.20** (gld_long, post-cost). At
   this threshold the strategy has no meaningful edge over the
   benchmark — DSR-deflator at `n_trials = 22` requires ~0.65+ for
   significance, so anything < 0.20 is dead on arrival.
2. **Primary DSR p-value > 0.30**. Standalone Sharpe high enough to
   evade kill #1 but DSR-deflated p > 0.30 means the result is
   indistinguishable from spurious selection at our cumulative trial
   count.
3. **IC-6 rolling-60d ρ vs iter 011 (vol_regime_inverse) > 30% on
   PRIMARY**. GVZ implied vol and σ_60/σ_252 ratio are both vol-regime
   signals; if rolling-correlation exceeds 30% on the primary dataset,
   GVZ is a re-skin of iter 011 (already MARGINAL/50) and deserves no
   incremental DSR budget. Per IC-6 closure (sister loop iter 007/010).
4. **Primary G6 bootstrap 99.9% CI low ≤ 0**. Any positive Sharpe
   that doesn't survive 1000-bootstrap CI at 99.9% lower bound is
   noise.

## Pre-validation screen (mandatory IC-6 per sister loop closure)

This is an overlay of an EXOGENOUS daily vol indicator on gold spot —
qualifies as overlay-style candidate. Per IC-6:

1. Build the GVZ z-signal-derived position vector on gld_long.
2. Compare it to iter 011's `vol_regime_inverse` position vector
   (loaded from `iterations/011-*/results.json`).
3. Compute static Pearson ρ and rolling-60d ρ on net-return space.
4. If `exceed_frac(|ρ_rolling| > 0.30) > 20%` on PRIMARY → ABORT iter
   immediately and log GS-22 as "GVZ-z is realized-vol-regime
   re-skin".
5. Also report ρ vs iter 003 (orthogonality target for any future IC-7
   composition) — not a kill, just diagnostic.

## Cost model (Track A = Pepperstone CFD)

```
gross_returns_daily = pct_change(close)  # gld_long or xauusd_real
half_spread = 8 bps / 2 = 4 bps (entry + exit each)
swap_per_calendar_night = 1 bps × calendar_nights_held × position
net_returns = gross_returns × position
              − entry_cost (when position changes 0→1)
              − exit_cost (when position changes 1→0; charged at last bar if still long)
              − swap_per_night × prior_position
```

(Identical to iter 018/021 helper to ensure cross-iter comparability.)

For an average ~20-day hold, cost ≈ 8 bps spread + 20×1 bps swap = 28
bps round-trip. With ~15-20 trades/year, annual cost drag ≈ 4.2-5.6%
notional. Strategy must overcome this from gold-rally capture.

## Expected budget

- Configs to test: **1** (per IC-8 single-cfg-per-iter rule; relaxing
  this would re-pollute DSR cumulative count after sister loop's
  control work).
- Wall-time: ~15-30 min (1 cfg × 2 datasets × 7-gate battery + IC-6).
- Files to create:
  - `fetch_gvz.py` — already created
  - `run_backtest.py` — main pipeline (clone of iter 021 with GVZ
    signal swapped in)
  - `test_gvz.py` — TDD tests for GVZ z-score signal generation
  - `score_and_verdict.py` — scoring + verdict.json writer
  - `results.json` — full per-dataset metrics + correlation diagnostics
  - `verdict.json` — score_strategy_v2 result + hold-time gate
  - `final_report.md` — verdict + lessons + dead-end (if any)

## Implementation plan

1. ✅ `fetch_gvz.py` — pulls FRED `GVZCLS`, caches
   `data/external/macro/gvzcls_daily.parquet`. Done.
2. **TDD**: `test_gvz.py` covers
   - rolling z-score numerical correctness on synthetic series
   - `gvz_zscore_signal_long_when_z_below()` state-machine entry/exit
   - position-vector lookahead-free property (today's signal uses
     yesterday's GVZ — `lag_days=1`)
   - cost-model parity vs iter 018/021 helper
3. **`run_backtest.py`** — clone iter 021 structure:
   - load GVZ + GLD + XAU
   - generate position vector via GVZ-z state machine
   - apply Track A cost model
   - 7 gates + DSR + bootstrap + walk-forward + cross-lib
   - IC-6 correlation diagnostic vs iter 003 / 011 / 015 / 018 / 020
4. **`score_and_verdict.py`** — call `score_strategy_v2`, hold-time
   check, write `verdict.json`.
5. **`final_report.md`** — verdict + lessons.
6. **Update `BASE_MEMORY.md`** — bump `total_iterations=22`,
   `cumulative_n_trials=22`, log entry, top-K, dead-ends.

## Pre-committed configuration

```python
CFG = {
    "cfg_id": "gvz_zscore_long_zentry_neg1_zexit_zero_window252d_lag1d_max30d",
    "z_entry_below": -1.0,
    "z_exit_above": 0.0,
    "window_days": 252,
    "lag_days": 1,
    "max_hold_days": 30,
    "spread_bps_rt": 8.0,
    "swap_bps_per_calendar_night": 1.0,
    "track": "pepperstone_cfd",
    "universe": "single_xau",
    "hold_time_track": "medium_swing",
    "declared_primary": "gld_long",
    "declared_corroborating": ["xauusd_real"],
    "primary_slice_start": "2009-06-04",  # 252-day warmup from GVZ inception
}
CUM_N_TRIALS = 22
```
