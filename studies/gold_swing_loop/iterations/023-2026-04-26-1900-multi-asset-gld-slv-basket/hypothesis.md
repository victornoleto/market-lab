# Iteration 023 — Multi-asset gold_complex (60% GLD + 40% SLV) RSI(2)<5 + SMA(200) basket

## Hypothesis

Apply iter 003's already-validated single-asset RSI(2)<5 + SMA(200)
trend-filter mean-reversion signal **independently to gold and silver
ETFs**, and aggregate at fixed weights **60% gold + 40% silver**.
Hypothesis: a precious-metals basket (XAU + XAG correlated yet
distinct) gives the same MR signal a less-correlated position vector
vs gold's macro-stress clock (which trapped iters 011/014/015/022 at
ρ ≥ +0.50 vs the vol-regime base) AND lifts the standalone Sharpe by
adding diversification across two assets that share the same MR
mechanism but differ in idiosyncratic supply/demand cycles.

**Why this is structurally novel** vs the 22 prior iters: every iter
016-022 used `universe = single_xau`. This is the first iter to use
the relaxation-rule freedom `universe = gold_complex` granted on
2026-04-26. Sister loop's 54+ iter empirical record: every loop winner
was multi-asset. The 7 NEAR_FAIL band iters (016-022) all hit the
single-asset Sharpe ceiling ≈ +0.55 (per GS-13/14/15/22). The basket
position vector is structurally distinct — driven by independent
RSI(2) firings on two correlated-but-not-identical price series.

## Primary citation

`[risk_parity, ch.7]` — Multi-asset basket weighting; precious metals
sub-portfolio as a defensive risk-tilt component. Static-weight
60/40 is the baseline before any inverse-vol or risk-parity dynamic
weighting iteration.

## Additional citations

- `[short_term_trading_strategies, p.105-118]` — Connors RSI(2)<5
  + SMA(200) trend filter (the per-asset signal generator; identical
  to iter 003's validated implementation)
- `[ilmanen_expected_returns, ch.10]` — Precious metals as a
  diversification asset class; gold + silver as a sub-basket
- `[trading_systems_methods, p.301-310]` — Kaufman regime-conditional
  MR (silver MR works when gold MR works, gated by SMA(200))
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (this iter increments to 23)
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
  (per-asset spread + swap)
- DEAD_ENDS GS-22 closure logic — option-implied vol family closed;
  multi-asset extension is the next genuinely structurally different
  direction per BASE_MEMORY priority 3

## Edge source

The single-asset XAU buy-hold benchmarks each capture 100% of gold's
drift; iter 003's RSI(2)+SMA(200) on XAU alone trails by Δ −0.38 to
−0.86 Sharpe (`GS-3 escape, partial vindication`). What iter 003
misses: silver-specific MR opportunities. Silver has higher vol
(σ ≈ 25% vs gold's 15%) and a more pronounced MR profile (industrial
demand cycles + precious-metals safe-haven flows), but silver MR
fires on partially-different days than gold MR (correlation of daily
returns ~0.70-0.80, not 1.0). A basket of independent RSI(2) signals
captures more of the MR opportunity per year while diversifying
asset-specific volatility.

**Edge = adding silver's MR opportunities to gold's, while keeping
each asset's per-trade signal cost-controlled** (8 bps RT for gold
leg, 20 bps RT for silver leg, no XAG leg trades when silver SMA(200)
is below price).

## Datasets

- **Primary: `gld_slv_basket_long`** — synthetic basket of GLD daily
  (60% weight) + SLV daily (40% weight), continuous-rebalance,
  2006-04-28 → 2026-04-15 (19.97 y). Earliest joint window starts
  when SLV launched (2006-04-28). Covers 2008 GFC + 2011 silver squeeze
  + 2013-2018 stagnation + 2020 COVID + 2024 ATH cycle. Best long-history
  test of multi-asset MR.
- **Corroborating: `xau_xag_basket`** — XAUUSD spot (60%) + XAGUSD spot
  (40%) basket, daily, 2020-01-02 → 2026-04-17 (6.29 y). Real Pepperstone-
  tradable instruments.
- (Iter 003's `xauusd_intraday` 1h variant skipped — basket signal is
  daily-resampled by construction.)

## Timeframes used

`["1d"]` — daily-only. Both legs use same SMA(200) trend filter and
same 2-day RSI windows.

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A only).

**Per-leg cost model**:
- **Gold leg**: 8 bps RT spread (Pepperstone XAUUSD Razor),
  −1 bps/night swap on long, weekend 3× swap.
- **Silver leg**: **20 bps RT spread** (Pepperstone XAGUSD spread is
  ~2.5× wider than XAU; conservative), −1 bps/night swap, weekend 3×.
- Long-only per asset → no short-side complications.

**Track B (Inter ETF) skipped** — same GS-2 cliff as iter 003 (~80
trades/yr per leg × 2 legs = 160 trades/yr × 100 bps FX RT ≈ 16% pa
drag, structurally negative).

## Hold-time profile (declared bucket)

- **Declared track**: `short_swing` (mean hold 2-10 trading days)
- Iter 003's per-asset mean hold was ~3-5 days; basket aggregate
  expected ~3-5 days as well (signals are independent per asset; weighted
  position changes faster than single-asset position).
- Bucket gate: PASS expected.
- Mismatch (e.g., observed mean hold > 10 days) → tier downgraded
  to NEAR_FAIL regardless of score.

## Pre-validation screen (mandatory per IC-6 for compositions)

This iter is BOTH a per-asset signal application AND a 2-stream
weighted aggregation. IC-6 mandatory check on the AGGREGATED basket
position vector vs:

1. **iter 003 (single-asset RSI(2)+SMA200 on gold)**: rolling-60d
   |ρ| measured on PRIMARY. Expectation: ρ_gld_basket vs ρ_gld_single
   should be HIGH (~0.85-0.95) because gold leg is 60% of basket and
   uses identical signal. **If ρ > 0.95**, the silver leg adds
   essentially zero structural diversification → basket reduces to
   "iter 003 with extra cost drag" → kill.
2. **iter 011 (vol_regime_inverse σ_60<σ_252)**: rolling-60d |ρ| on
   PRIMARY. This is the macro-stress-clock test that closed iters
   014/015/022. Expectation: ρ < 0.30 (basket should NOT ride the
   gold-vol-regime macro clock, since RSI MR is price-momentum-
   driven not vol-driven).

Pre-val computed at runtime; both iter 003 and iter 011 net return
series available from prior iters' `results.json["returns_series"]`.

## Kill criteria (pre-committed)

This iteration is **falsified** if ANY of the following fire at end
of STAGE 4:

1. **Standalone Sh on PRIMARY < +0.30** — basket fails to even match
   iter 003's single-asset Sh on gld_long (+0.30). Multi-asset adds
   no edge.
2. **Sh lift over iter 003 on PRIMARY < +0.05** — basket Sharpe is
   essentially the same as single-asset; silver leg contributes
   nothing or slightly dilutes (cost-of-trading > MR edge).
3. **IC-6: rolling-60d |ρ| vs iter 003 > 95% on PRIMARY** — silver
   leg adds essentially zero structural diversification.
4. **G6 bootstrap 99.9% CI low ≤ 0 on PRIMARY** — fragility check.

If kills fire: add **GS-23** to DEAD_ENDS closing
"60/40 GLD+SLV basket extension of iter 003 RSI MR" path. Does NOT
close: alternate basket weights (40/60, 50/50, inverse-vol),
alternate signal (e.g., breakout instead of MR), miner-inclusive
basket (GDX/GDXJ — requires Tiingo fetch), GDX as IC-7 secondary.

If NO kills fire AND score ≥ 60 PROMISING: queue as base for IC-7
composition with the strongest orthogonal stream available (probably
iter 014 macro-DFII10 or iter 018 COT z-score).

## Cost model (Track A per-leg)

```python
# Gold leg
br_gold = apply_pepperstone_costs(
    gross_returns=gld_pct_change,
    position=signal_gld * 0.60,  # 60% capital allocation
    spread_rt_bps=8.0, swap_long_bps=-1.0, swap_short_bps=0.3,
)
# Silver leg
br_silver = apply_pepperstone_costs(
    gross_returns=slv_pct_change,
    position=signal_slv * 0.40,  # 40% capital allocation
    spread_rt_bps=20.0,  # XAG wider spread
    swap_long_bps=-1.0, swap_short_bps=0.3,
)
# Portfolio PnL = sum of per-leg net PnL
basket_net_pnl = br_gold.net_pnl + br_silver.net_pnl
```

Mean-hold ~4d × 80-100 trades/yr per leg × 2 legs ≈ 160 trades/yr;
expected per-asset annual cost: gold ~80 × 8 + 320 swap = 960 bps/yr
pre-MR-edge; silver ~80 × 20 + 320 swap = 1920 bps/yr pre-MR-edge.
Higher cost vs iter 003 by silver-leg's wider spread × turnover.

## Expected budget

- Configs to test: **1** (single pre-committed basket weight 60/40,
  IC-8 compliant, no grid-sweep)
- Wall-time: ~3-5 minutes (signal O(N) per asset × 2 + portfolio
  aggregation + 7-gate battery)
- Files to create:
  - `hypothesis.md` (this file)
  - `test_basket_signal.py` (TDD; per-asset signal correctness +
    weighted aggregation + cost per-leg parity)
  - `run_backtest.py` (reuses iter 003's signal helper; adds basket
    aggregation + per-leg cost call)
  - `results.json` + `verdict.json` + `final_report.md`

## Implementation plan

1. **TDD first** — write `test_basket_signal.py` (~5-6 tests):
   - Per-asset signal `connors_rsi2_signal_with_trend_filter` from
     iter 003 reused unchanged (verify by importing).
   - Basket position aggregation: `pos_basket = w_gold * sig_gold +
     w_silver * sig_silver` produces ∈ [0, 1].
   - Cost model applied per leg (not on portfolio sum) — verify
     spread costs computed against per-leg `position.diff()`, not
     aggregate.
   - Benchmark = `0.60 * GLD_returns + 0.40 * SLV_returns`
     continuous-rebalance.
   - IC-6 correlation diagnostic helper computes rolling-60d ρ
     against another series and returns exceed-fraction.
2. **Compute new benchmarks** — for primary (`gld_slv_basket_long`)
   and corroborating (`xau_xag_basket`), measure Sharpe / CAGR / MDD
   on 60/40 buy-hold. Pass these via `score_strategy_v2(benchmarks=...)`.
3. **Run backtest** — both datasets, single config, 7-gate battery
   per dataset. IC-6 pre-val measured at runtime against iter 003
   and iter 011 net-return series (load from prior `results.json`).
4. **Score with `score_strategy_v2`** (rules_version: 2026-04-26-r1)
   declared_primary=`gld_slv_basket_long`, declared_corroborating=
   `[xau_xag_basket]`. Threshold defaults to 4 for new datasets.
5. **Report** — final_report.md, verdict.json, append iter log entry
   to BASE_MEMORY, structural-dead-end if kills fire, auto-prune
   BASE_MEMORY if > 18 KB.
