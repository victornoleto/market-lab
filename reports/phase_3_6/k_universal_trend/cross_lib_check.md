# Cross-lib concordance — Family K Universal Trend Tactics

- Winner cell: **Donchian-50, ATR(14)×3.0, risk 0.5%/leg, 1d cadence**
- OOS window: 2018-01-01 → 2023-12-31
- Canonical OOS CAGR: **+1.878%**
- Hand-rolled (pure-pandas) OOS CAGR: **+1.878%**
- |Δ|: **0.000pp** (tolerance ≤ 3pp)
- Gate 9 verdict: **PASS**

## Notes

Two independent implementations of the Family K portfolio layer:

1. Canonical: `simulate_universal_trend` — vectorized numpy per-bar
   loop with in-simulator entry / ATR-trail exit / gross cap +
   swap/spread/commission decomposition.
2. Hand-rolled: re-uses `compute_atr_wilder` (so the ATR primitive
   is identical) but rebuilds Donchian-channel detection, trail-
   stop state machine, and cost decomposition with explicit pandas
   operations.

Both implementations apply the Pepperstone Razor cost model (plan
§3.1): per-ticker spread, 3.5e-5 round-trip commission, 0.03%/night
swap on long notional. Any non-trivial Δ isolates portfolio-wiring
bugs (not signal bugs).

vectorbt / bt / backtrader ports were NOT produced because:

- Those libraries do not expose primitives for ATR-distance
  trailing stops with risk-fraction position sizing on a multi-
  asset basket. Porting would re-implement the pipeline inside
  the library's custom-indicator API — yielding a copy of our own
  code with a thin wrapper, not independent verification.
- The OOS verdict is FAIL on 10 binding gates — additional
  library ports cannot rescue a family where the basket of
  Donchian breakouts produces only Sharpe ≈ 0.39 / CAGR ≈ 1.9%
  OOS after Pepperstone retail costs.

## Citations

- Lookahead audit: `[advances_fin_ml, p.31-34]`.
- Penfold Donchian + ATR trail primitives: `[universal_trend_
  tactics, p.295-299, p.338-343]`.
