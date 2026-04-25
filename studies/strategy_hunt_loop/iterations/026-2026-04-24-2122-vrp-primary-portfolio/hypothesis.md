# Iteration 026 — VRP-primary portfolio (T-bill collateral + short SPY put credit spread)

## Hypothesis

Construct a **stand-alone Volatility Risk Premium (VRP) harvester**: hold
all capital in T-bills earning a constant risk-free rate, and sell a
single 5%/10% OTM put credit spread on SPY (or QQQ for the NDX dataset)
every month at 21-DTE, rolling at expiry. Daily P&L is `rf_daily +
harvest_notional × (−put_spread_daily_return)` with `harvest_notional =
1.0` (one full spread per unit of capital — max single-roll loss capped
at the spread width minus net credit, ~4-4.5% of S_entry).

Unlike iter 020/021, **no equity-leg, no bond-leg, no vol-target
wrapper sits below the overlay** — the strategy IS the harvest. This
makes the realised P&L of the option-pricing block the dominant Sharpe
driver, instead of being absorbed into σ²_port via Moreira-Muir scaling
(the iter 021 dynamic that left it Sharpe-neutral).

## Primary citation

`[volatility_trading, ch.3]` — variance-risk-premium mechanics: implied
volatility consistently exceeds realised volatility on index options
(Sinclair p.40-44 documents historical IV vs RV for SPX); short-vol
positions therefore have **positive expected return ex ante**, which
the seller earns as a premium for bearing the short-gamma tail.

## Additional citations

- `[volatility_trading, p.41]` — "SPX kurtosis 21.3" justifies a
  capped-tail (credit-spread) wrapper instead of a bare short put.
- `[volatility_trading, p.217]` — Sinclair's rule: "Sell index volatility
  (straddles/strangles on QQQ/SPY) when the VIX is below 35. The
  volatility premium is proportionally greater when the implied
  volatility is low. Results are fairly robust with respect to the
  actual VIX level chosen." (Iter 026 V1 omits the VIX filter to keep
  the pre-committed spec minimal; it's a deferred refinement.)
- `[volatility_trading, p.11]` — Black-Scholes pricing identity (IV is
  the σ that makes BS reproduce market price); used in the BS pricer
  inherited from iter 020.
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials`.
- Web/papers:
  - **Bondarenko, O. (2014). "Why Are Put Options So Expensive?"**
    *Quarterly Journal of Finance* 4(3): 1450015. DOI:
    10.1142/S2010139214500153. Documents an empirical VRP of 2-3%/yr
    for SPX put writers 1987-2011 (after risk adjustment), with Sharpe
    ratios ~1.0-1.5 for capped credit-spread structures.
  - **Carr, P. & Wu, L. (2009). "Variance Risk Premiums."** *Review of
    Financial Studies* 22(3): 1311-1341. DOI: 10.1093/rfs/hhn038.
    Decomposition of VRP into instantaneous variance + jump components;
    documents stable cross-asset premium.
  - **Coval, J. & Shumway, T. (2001). "Expected Option Returns."**
    *Journal of Finance* 56(3): 983-1009. Shows OTM index puts are
    priced rich relative to objective probabilities.
  - **Hurst-Ooi-Pedersen (2017)** is referenced in iter 023/025 for
    cross-asset trend; not relevant here.

## Edge source

SPY 1x captures equity beta. VRP-PRIMARY captures the **volatility risk
premium directly**: insurance buyers (institutional hedgers, retail
gamma-buyers) consistently overpay the seller relative to objective
probability of large drawdown. The seller's expected return is **the
risk premium for bearing tail-event tail-loss**, which is **structurally
orthogonal to equity beta** (Carr-Wu 2009 §3.1 documents the
correlation of variance risk to equity is positive but well below 1.0).

## Datasets

- **educational**: SPY + VIX, 2006-01-03 → 2026-04-15 (~20y, ~5050 bars).
  Matches iter 020/021 alignment. Includes 2008 GFC, 2010 flash crash,
  2018 vol blow-up, 2020 COVID, 2022 rate-hike — the four canonical
  short-vol stress events.
- **spy_real**: SPY + VIX, 2009-06-25 → 2026-04-15 (~17y, ~4225 bars).
  Post-GFC, includes 2020 COVID + 2022 rate-hike + 2025 stress.
- **ndx_real**: QQQ + VIX×1.1, 2010-02-12 → 2026-04-15 (~16y, ~4065
  bars). NDX IV runs ~10% above SPX (NDX skew is slightly steeper);
  iv_scale = 1.1 inherited from iter 020/021.

VIX coverage starts 1990-01-02 — adequate for all three windows.

## Kill criteria (pre-committed)

If ANY of the following observable at end of Stage 3, the hypothesis
is falsified regardless of secondary metrics:

- **Kill A — No Sharpe alpha**: candidate Sharpe < benchmark Sharpe on
  ≥ 2/3 datasets. Means VRP harvest with `harvest_notional=1.0` is too
  conservative to compete with US-equity beta post-GFC.
- **Kill B — Catastrophic per-roll loss**: any single 21-day window
  drawdown > 30% of equity. Means the credit-spread structure does NOT
  effectively cap the tail (data alignment / IV-scale bug).
- **Kill C — Equity-beta in disguise**: |corr(daily strategy return,
  daily SPY return)| > 0.7. Means the strategy is essentially long
  SPY at modest beta, not orthogonal VRP harvest. Counter-prediction:
  Carr-Wu 2009 §3.1 estimates VRP-equity ρ ≈ 0.4-0.5 historically.
- **Kill D — Engine dirty**: G7 cross-library CAGR diff > 3 pp on any
  dataset. Means the BS pricing or roll mechanics differ between
  pandas and pure-numpy implementations.

If only Kill A fires (no others), the structural-failure analysis
should still produce useful boundary-tightening (the iter 020/021
overlay tests are tightened by removing the vol-target wrapper).

## Expected budget

- Configs to test: **1** (single pre-committed cfg, no grid).
- Wall-time: ~25-30 minutes (3 datasets × monthly-roll BS pricing on
  ~5000 bars × gate battery).
- New files to create:
  - `vrp_primary.py` — main module
  - `numpy_reference_vrp.py` — pure-numpy parity ref (G7)
  - `run_backtests.py` — runner over 3 datasets
  - `compute_gates_and_score.py` — gate evaluation
  - `tests/test_iter026_vrp_primary.py` — TDD spec
- Reuses:
  - `compute_put_spread_daily_returns` from
    `iterations/020-2026-04-24-1850-put-spread-tail-hedge/put_spread_hedge.py`
    (BS-priced spread overlay, identical to iter 020/021)
  - `data/external/macro/vix_daily.parquet` (VIX 1990+)
  - `data/tiingo/daily/prices/{SPY,QQQ}.parquet`
  - Validation modules per `INFRASTRUCTURE.md`

## Implementation plan

1. **Write TDD spec first** (`tests/test_iter026_vrp_primary.py`):
   - `test_constant_vol_synthetic_returns_to_rf`: with σ_realised = σ_implied
     and OTM strikes, the spread MtM ≈ 0 across the life of the position
     (modulo theta/cost), so `r_strategy ≈ rf_daily`.
   - `test_zero_harvest_returns_pure_rf`: `harvest_notional=0` → daily
     return = `rf_daily` exactly.
   - `test_negative_harvest_raises`: `harvest_notional<0` raises
     ValueError (we are SHORT writers; the sign is internal).
   - `test_short_writer_signs_match_iter_021`: stand-alone harvest
     returns equal `−overlay` to floating-point parity (re-using
     iter 021's overlay flip).
   - `test_pipeline_runs_on_50bar_synthetic`: end-to-end synthetic
     50-bar dataset with constant 20% IV produces a finite Sharpe.
2. **Implement** `vrp_primary.py` — single function
   `compute_vrp_primary_returns` taking (prices, iv_series, **kwargs)
   returning a daily-return Series.
3. **Implement** `numpy_reference_vrp.py` — pure-numpy replica of the
   pipeline (BS pricing, roll mechanics, T-bill drift) for G7 parity.
4. **Run** `run_backtests.py` on 3 datasets; save `results.json` with
   `returns_series` schema for the Stage-5 plot helper.
5. **Compute** gates G1-G7 + score via `studies/strategy_hunt_loop/scoring.py`.
6. **Write** `final_report.md`, `verdict.json`, run plot helper.

## Pre-registration of n_trials advance

`cumulative_n_trials`: 4278 → **4279** (+1 cfg × 1 dataset is the test
unit; per project convention iters with N configs × M datasets advance
by N, so this single-cfg iter adds **+1**).
