# Iteration 025 — Slow-EWMAC trend with forecast diversification on a 6-asset broad-asset-class basket

## Hypothesis

Run a **multi-asset trend-following** strategy on a 6-asset broad-asset-class
basket (SPY, EFA, EEM, TLT, IEF, GLD), using **slow EWMAC signals only**
(32:128 and 64:256 day pairs per Carver appendix B), with two-speed forecast
diversification (FDM ≈ 1.10), per-asset volatility-targeting, and a
**portfolio-level vol-target** of 15%/yr. The goal is to harvest cross-asset
trend premia (Hurst-Ooi-Pedersen 2017 estimate ~+5%/yr Sharpe contribution
from time-series momentum on diversified futures) while sidestepping iter
023's failure mode (turnover ~35/yr/leg from canonical 252/21 fast TSM).

The combined (per-asset, per-speed) forecast is mapped to a position weight
proportional to `forecast_norm × target_vol_per_asset / asset_realized_vol`,
clipped to a per-asset leverage cap of 0.6× (so total gross leverage is
bounded at 6 × 0.6 = 3.6×, but the realized leverage will be much lower
because forecasts and signs vary). Rebalance is daily but trades are
position-sized (no rebalance trade unless |Δposition| > 10% of current
position — Carver p.252 "no-trade buffer"), pushing turnover to ~3-6/yr/leg
per Carver Table 30.

## Primary citation

`[systematic_trading, p.118-119, ch.7]` — EWMAC trend rule with six
canonical speed pairs (2:8, 4:16, 8:32, 16:64, 32:128, 64:256). The
ratio 4:1 fast:slow is fixed on artificial data to avoid overfitting,
performance flat between 2:1 and 6:1 [p.284, app.B].

## Additional citations

- `[systematic_trading, p.131-133, ch.8]` — Forecast diversification
  multiplier (FDM): combining N correlated forecasts requires multiplying
  the weighted sum by FDM to restore E[|combined|] = 10. For 2 forecasts
  at ρ=0.85 (typical EWMAC adjacent-speed correlation), FDM ≈ 1.10.
- `[systematic_trading, p.282-285, app.B]` — EWMAC computation, the
  `2/(L+1)` decay parameters, and the per-speed forecast scalars (32:128
  scalar = 2.65, 64:256 scalar = 1.87).
- `[systematic_trading, p.244-258, ch.15]` — Position trade-band /
  no-trade buffer reduces turnover without sacrificing edge.
- `[risk_parity, p.10-11, ch.1]` — Multi-asset diversification basis;
  per-asset vol-targeting equalizes risk contributions.
- `[advances_fin_ml, p.31-34]` — Cross-library parity discipline (G7).
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag rule (no look-ahead).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- `[stocks_on_the_move, p.229]` — 2 bps/leg cost model (held constant).

Web / academic:

- Hurst, Ooi, Pedersen (2017). "A Century of Evidence on Trend-Following
  Investing." *Journal of Portfolio Management* 44(1), 15-29. — Centennial
  evidence on cross-asset trend, ~+5% Sharpe contribution.
  https://doi.org/10.3905/jpm.2017.44.1.015
- Moskowitz, Ooi, Pedersen (2012). "Time series momentum." *JFE* 104(2),
  228-250. — Reference for the TSM family that iter 023 closed at fast
  speeds; iter 025 tests the slow-speed boundary.
  https://doi.org/10.1016/j.jfineco.2011.11.003

## Edge source

SPY 1× buy-hold has zero exposure to bond/commodity/non-US-equity trend
regimes (e.g., 2008-2009 bond rally with TLT +30%, 2020-2021 gold rally
with GLD +25%, 2022 commodity rally with DBC +30%). A diversified
multi-asset slow-trend portfolio captures persistent cross-asset
directional premia that are uncorrelated with US equity beta, providing
both Sharpe lift (when trends align) and drawdown shelter (when SPY
drawdowns coincide with bond/gold strength).

## Datasets

- **educational** (SPY+TLT+IEF+GLD+EFA+EEM 2007-01-11 → 2026-04-15):
  ~19y intersection-aligned start (matches iter 024 cleanly; IEF inception
  is 2006-01 but we use 2007-01-11 for the SHV-aligned hunt-loop default).
- **spy_real** (SPY+TLT+IEF+GLD+EFA+EEM 2009-06-25 → 2026-04-15):
  17y post-GFC. SPY is benchmark, others are diversifiers.
- **ndx_real** (QQQ+TLT+IEF+GLD+EFA+EEM 2010-02-12 → 2026-04-15):
  16y post-GFC. QQQ replaces SPY as equity leg.

## Kill criteria (pre-committed)

The hypothesis is falsified — and the iteration documented as a structural
dead-end — if ANY of:

1. **Kill A (Sharpe regression vs iter 015):** Sharpe Δ vs iter 015
   (frozen) < −0.03 on ≥ 2/3 datasets. Slow-EWMAC adds nothing over
   static SPY+IEF baseline.
2. **Kill B (turnover trap):** average per-leg turnover > 12/yr on
   ≥ 2/3 datasets. Slow signals AREN'T slow enough; cost drag will
   dominate.
3. **Kill C (MDD blowup):** MDD > benchmark + 5pp on ≥ 2/3 datasets.
   Trend leak through 2008/2022 disasters.
4. **Kill D (no-trade buffer ineffective):** post-buffer turnover > 80%
   of pre-buffer turnover on ≥ 2/3 datasets. The Carver no-trade buffer
   isn't reducing churn meaningfully.

## Expected budget

- **Configs to test: 1** (single pre-committed cfg, no grid, no sweep).
  Cumulative n_trials advance: 4277 → 4278 (+1).
- **Wall-time:** ~15-25 min for backtests + gates.
- **Files to create:**
  - `slow_ewmac_multi_asset.py` — strategy implementation (~200 LOC).
  - `numpy_reference_sema.py` — pure-numpy cross-lib reference (~150 LOC).
  - `run_backtests.py` — 3-dataset runner.
  - `compute_gates_and_score.py` — gate battery + scoring.
  - `tests/test_slow_ewmac_multi_asset.py` — TDD specs (~10 specs).
  - `final_report.md`, `verdict.json`, plots.

## Implementation plan

1. **Write tests first** (`tests/test_slow_ewmac_multi_asset.py`):
   - EWMAC computation matches Carver Table 49 scalars.
   - σ̂_{t-1} lag enforced (no look-ahead).
   - Forecast capping at ±20.
   - FDM applied correctly when combining 2 speeds.
   - Per-asset position sizing scales inversely with realized vol.
   - No-trade buffer reduces turnover without changing held positions.
   - Cost = sum |Δpos_i| × 2 bps.

2. **Implement `slow_ewmac_multi_asset.py`** — pandas-based, ~200 LOC.
   - `compute_ewmac_forecast(prices, Lfast, Lslow, scalar) → forecast in [-20, +20]`
   - `combine_forecasts(f1, f2, fdm=1.10) → combined in [-20, +20]`
   - `position_size(combined, asset_vol, target_vol_per_asset) → weight`
   - `apply_no_trade_buffer(weights, threshold=0.10) → traded_weights`
   - `apply_strategy(prices_df, target_vol, asset_weights, ...) → (net, positions)`

3. **Implement numpy reference** (`numpy_reference_sema.py`) for G7 cross-lib parity.

4. **Run on 3 datasets** via `run_backtests.py`, write `results.json`.

5. **Compute gates and score** via `compute_gates_and_score.py`,
   writing `verdict.json`.

6. **Plot equity curves** via `studies/strategy_hunt_loop/plot_helper.py`.

7. **Final report** documenting verdict, kill-criteria check, and
   structural lessons.

## Pre-committed config

```python
CFG = {
    "cfg_id": "sema_slow_64_256_32_128_6asset_vt15_v1",
    "speeds": [(32, 128), (64, 256)],         # 2 slow speeds
    "speed_scalars": [2.65, 1.87],            # Carver Table 49
    "speed_weights": [0.5, 0.5],              # equal weights
    "fdm": 1.10,                              # 2 forecasts at ρ≈0.85
    "target_vol_pct": 0.15,                   # 15%/yr portfolio
    "asset_weights": [1/6] * 6,               # equal-risk basket
    "asset_vol_span": 36,                     # EWMA vol span (~7w halflife)
    "lag_bars": 1,                            # no look-ahead
    "no_trade_buffer_pct": 0.10,              # 10% threshold
    "rebalance_bars": 1,                      # daily check
    "max_per_asset_leverage": 0.6,            # cap per asset
    "long_only": True,                        # no shorts
    "cost_bps_per_leg": 2.0,                  # 2 bps per |Δposition|
}
```

Long-only constraint: when `forecast_norm < 0`, position is set to 0
(flat), not negative. This matches what's implementable on retail ETFs
without margin shorts.

## Why this is structurally novel vs DEAD_ENDS.md

- **Iter 023 closed:** TSM canonical (252/21) on ≤4-asset basket per-asset
  vol-target. Iter 025 uses **slow EWMAC (32:128 + 64:256)** instead of
  fast TSM, **6 assets** (vs 3), **portfolio-level vol-target** (vs
  per-asset only), **forecast diversification across 2 speeds with FDM**
  (Carver p.131-133, not present in iter 023), and **no-trade buffer**
  (10% trade band, not present in iter 023).
- **Iter 023 dead-end note explicitly states:** "Does NOT close
  slow-EWMAC, ≥20-market baskets, carry-primary, VRP-primary."
- **Iter 010 closed:** 3-leg static blend SPY+TLT+GLD with daily inverse-
  variance allocation. Iter 025 uses **trend-driven directional positions**
  (not inverse-variance), 6 assets (not 3).
- **Iter 011 closed:** weekly cadence on multi-leg blend. Iter 025 uses
  daily forecast computation with no-trade buffer (Carver-canonical) for
  turnover control, NOT cadence reduction.

This is the FIRST iteration testing slow-EWMAC trend on a multi-asset
basket in the hunt loop.
