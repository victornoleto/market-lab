# Iteration 013 — iter 011 (σ_60<σ_252) AND close > SMA(200) regime gate

## Hypothesis

Iter 011's inverse vol-regime gate (`σ_60d < σ_252d` long-only) achieved
+Sharpe-edge bench-beat 2/3 ds (xauusd_real Δ +0.38, xauusd_intraday Δ
+0.49) but **failed on gld_long** (Sharpe +0.48 vs bench +0.68; DSR p=0.275
> 0.05). The structural diagnosis (DEAD_ENDS GS-11 + iter 011 final report):
the gld_long 21.4y window contains ~5 years (≈2013-2018) of low-vol
bear-stagnation where σ_60<σ_252 fires (because volatility IS compressed)
but gold drifts DOWN. Iter 011 cannot tell low-vol-bull from low-vol-bear.

This iteration adds **one** parameter — Connors' canonical trend gate
`close > SMA(200)` — to filter out exactly that regime: bars where
volatility is compressed AND price is below its 200-day average (i.e.,
low-vol bear-drift). Position becomes:

```
position[t] = 1 iff (σ_60[t-1] < σ_252[t-1]) AND (close[t-1] > SMA_200[t-1])
            = 0 otherwise
```

(All inputs lagged 1 bar; look-ahead-free.)

**Expected effect on gld_long**: removes ~30-40% of currently-on bars
(the 2013-2018 stagnation patch). Active period shrinks from ~50% to
~30%. Mean active drift improves (positive bias from removed losing-bars),
lifting Sharpe through the n_trials=13 deflator. Target Sharpe ≥ 0.65
to clear DSR p<0.05.

**Expected effect on xauusd_real / xauusd_intraday**: minimal. The 6.3y
window (2020-2026) has only one major drawdown (2022 H1) and gold has
mostly trended up, so SMA(200) gate eliminates few bars and doesn't
materially change the +Sharpe edge already won.

## Primary citation

`[short_term_trading_strategies, p.106]` — Connors' "use SMA(200) as a
trend-regime gate" — explicitly cited in DEAD_ENDS GS-3 escape hatch #1
and BASE_MEMORY direction #1 (PROMOTED priority for iter 013 after
iter 012 closed IC-7 path GS-12).

## Additional citations

- `[volatility_trading, p.58-59]` (Sinclair) — vol cone framework; iter 011 base.
- `[trading_systems_methods, p.13-14]` (Kaufman) — metals = low-noise → trending; iter 011 directional rationale.
- `[trading_systems_methods, p.301-310]` (Kaufman) — regime-conditional rules; SMA(200) as "macro-trend filter".
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 13`.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest; reuse iter 011's cost-included net returns infrastructure.
- DEAD_ENDS GS-11 / GS-12 — iter 011 closes σ_60<σ_252 STANDALONE; iter 012 closes IC-7(003+011) Markowitz; this iter pursues the orthogonal "single-stream gld_long bear-regime fix" path explicitly preserved as "Does NOT close" item #1 in GS-11.

## Edge source

Gold buy-hold (and iter 011 standalone) cannot distinguish low-vol-bull
from low-vol-bear regimes — both fire the σ ratio. SMA(200) provides
that distinction at zero data cost (already in cache; one extra rolling
mean). The 2013-2018 gld_long bear-leak is **the only structural
weakness** keeping iter 011 from passing 5/5 winner conditions on
non-hold-time axes.

## Datasets

All 3 mandatory:

- **gld_long** (GLD daily ~21.4y, 5384 bars): primary test bed — the
  weakness we're trying to fix lives here. SMA(200) needs ~252 bars of
  warmup (= already accommodated by iter 011's σ_252 warmup).
- **xauusd_real** (XAUUSD daily 6.3y, 1700 bars): regression check —
  must NOT degrade Sharpe edge by > 0.30. The 2020-2026 window has
  short SMA(200) warmup penalty (first ~year unavailable).
- **xauusd_intraday** (XAUUSD 1h, 32195 bars, 6.3y): regression check —
  same pattern as xauusd_real but 1h-resolution; SMA(200) computed on
  daily-resampled close, propagated to 1h bars (look-ahead-free, mirror
  iter 011's `build_intraday_position`).

## Timeframes used

`1d / 4h / 1h` (1d for gld_long + xauusd_real signal; 1h for
xauusd_intraday execution with daily-resampled signal). No fine-TF
fetch needed; iter 001's data infra fully sufficient. **No deferred TFs.**

## Broker tracks targeted

`broker_track: "both"` — same dual-track shape as iter 011.

- **Track A (Pepperstone CFD)**: 8 bps spread RT + −1 bps/night swap; long-only via flag=1; intraday viable.
- **Track B (Inter ETF GLD)**: 100 bps FX RT + 15% DARF; long-only daily-only; `xauusd_intraday` skipped on B per T+1.

Track A is primary for winner verdict.

## Hold-time profile (HARD GATE)

- Expected mean hold: ~30-50 trading days (similar to iter 011 — slow
  regime indicator). The SMA(200) gate is even slower than σ_60/σ_252,
  so episode lengths may *increase* slightly but flip count stays low.
- Intraday-only: **NO** — multi-day swing (σ_60 + SMA(200) are slow).
- **Hold gate will FAIL** (mean > 5d). Tier ceiling = STRONG with
  "swing-extended" tag (same as iter 011). Acceptable per BASE_MEMORY:
  "If gld_long DSR<0.05 standalone → all 5 winner conditions except
  hold-time clear → STRONG with swing-extended tag."

## Kill criteria (pre-committed)

Iter is FAILED / regression if ANY:

1. **gld_long Sharpe drops below iter 011 standalone (+0.48)** — the
   SMA(200) gate is supposed to *raise* gld_long Sharpe by removing
   bear-leak; if it drops below baseline, the diagnostic is wrong and
   we close this path. (Gentle threshold: tolerate +0.05 noise; abort
   if Sharpe < 0.43.)
2. **xauusd_real Sharpe drops by > 0.30 vs iter 011 (+1.42 → < +1.12)** —
   regression on a working dataset. Means SMA(200) on the 2020-2026
   window is over-gating.
3. **gld_long active fraction drops below 10%** — over-filtering;
   strategy becomes mostly cash. Iter 011 had p_active ≈ 50%; expect
   ~30% post-filter; abort if < 10%.
4. **All 3 datasets fail pre-val gate** — same pre-val structure as
   iter 011 (p_active ∈ [0.10, 0.70] — relaxed lower bound vs iter 011's
   0.15 because we expect SMA(200) to reduce p_active legitimately;
   μ_active > 0; n_flips/yr ≤ 8; cost drag < 0.5 × active drift).
   AUTO-ABORT.

## Pre-validation screen

Single-stream additive (not overlay) → IC-6 ρ-screen NOT applicable.
Pre-val is the cost-aware screen (same shape as iter 011 with the
relaxed p_active lower bound noted in kill criterion #4).

## Cost model (per track)

**Track A (Pepperstone)**: spread 8 bps RT + swap −1 bps/night long
+ 0.3 bps/night short (irrelevant for long-only). Multi-day hold ⇒
swap drag accumulates linearly with mean_hold_days × 1 bps. At ~40-day
hold, swap drag ≈ 40 bps/trade vs ~80 bps/trade gross drift required.
Reuse `cost_models.apply_pepperstone_costs` from iter 011.

**Track B (Inter)**: FX 100 bps RT + 15% DARF. Same as iter 011's
`apply_inter_costs_with_darf`.

Both already validated against iter 011's working pipeline; no new
cost code.

## Expected budget

- Configs to test: **1** (single pre-committed cfg per IC-8). No grid.
  Defaults: window_short=60, window_long=252, sma_trend=200. All three
  are canonical (Sinclair cone, Connors).
- Wall-time: ~3-5 minutes (same as iter 011; just one extra rolling mean
  + element-wise AND).
- Files to create: `run_backtest.py`, `test_volregime_sma200_signal.py`,
  `pre_val.json`, `results.json`, `verdict.json`, `final_report.md`.

## Implementation plan

1. Write TDD test file `test_volregime_sma200_signal.py` covering:
   (a) `vol_regime_inverse_with_sma200_flag` returns 0 in warmup,
   (b) flag=1 only when both σ inverse AND price>SMA(200),
   (c) cross-lib parity for SMA(200) (numpy rolling mean reference),
   (d) reduces or matches iter 011's flag (subset relation: new flag → old flag),
   (e) hand-rolled gld_long sanity (constructed series with known regime crossings).
2. Implement `vol_regime_inverse_with_sma200_flag` and
   `vol_regime_inverse_with_sma200_position` in `run_backtest.py`,
   reusing iter 011's `realized_vol`. Re-export iter 011's flag for
   the subset test.
3. Reuse iter 011's `run_one_dataset`, `run_walk_forward`, `run_bootstrap`,
   `cross_lib_gross_check`, pre-val structure unchanged. Update
   `CUMULATIVE_N_TRIALS = 13` and `CFG_ID = vol_regime_inverse_sma200_long_only`.
4. Run pre-val on all 3 datasets; if 0/3 pass auto-abort.
5. Run full 3-dataset backtest; save `results.json` + `verdict.json`.
6. Compute score via `scoring.score_strategy(metrics, gates, 13)`.
7. Compare iter 011 vs iter 013 standalone metrics in final report.
8. Determine tier:
   - If gld_long DSR p<0.05 + winner_conditions_met (4/5 non-hold) →
     STRONG (with swing-extended tag) at 75+ score.
   - If gld_long DSR p remains > 0.05 but lifted significantly → MARGINAL
     with documentation of the structural ceiling.
   - If kill criterion fires → FAIL with regression closure note.
9. Update BASE_MEMORY iter log + DEAD_ENDS (new GS-13 if structural).
