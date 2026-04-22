# Cross-lib concordance — Family F vol-target managed futures basket

- Winner cell: **EWMAC 16:64, vol_target=15%, rebal=10d**
- OOS window: 2018-01-01 → 2023-12-31
- Canonical OOS CAGR: **-0.137%**
- Hand-rolled (pure-pandas) OOS CAGR: **-0.137%**
- |Δ|: **0.000pp** (tolerance ≤ 3pp)
- Gate 9 verdict: **PASS**

## Notes

Two independent implementations of the Family F portfolio layer:

1. Canonical: `simulate_vol_target_mf` — vectorized numpy per-bar
   loop with in-simulator inertia + cadence + gross-leverage cap
   + swap/spread/commission decomposition.
2. Hand-rolled: re-uses `compute_ewmac_forecast` (so the Carver
   EWMAC primitive is identical) but rebuilds σ-EWMA, target
   sizing, cadence loop, and cost decomposition from scratch using
   pure-pandas ops.

Both implementations apply the Pepperstone Razor cost model (plan
§3.1): per-ticker spread, 3.5e-5 round-trip commission, 0.03%/night
swap on long notional. Any non-trivial Δ isolates portfolio-wiring
bugs (not signal bugs).

vectorbt / bt / backtrader ports were NOT produced because:

- Those libraries do not expose a primitive for Carver vol-target
  sizing with IDM (instrument diversification multiplier) and
  position inertia. Porting would require implementing the full
  pipeline inside the library's custom-indicator API — yielding a
  copy of our own code with a thin wrapper, not an independent
  implementation.
- The OOS verdict is FAIL on 12 binding gates (swap drag dominates:
  311% cumulative swap cost over 25 years at 2.22× average gross
  leverage). Additional library ports cannot rescue a family where
  the gross-return Sharpe is 0.60 pre-cost and the cost model
  erases it.

## Citations

- Lookahead audit: `[advances_fin_ml, p.31-34]`.
- Carver EWMAC + vol-target primitives: `[systematic_trading,
  p.282-285, p.159-173]`.
