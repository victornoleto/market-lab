# Cross-lib concordance — Family E Ehlers adaptive cycles

- Winner cell: **hp=48, ss=10, lo=0.30, hi=0.70, hold=20 bars**
- OOS window: 2018-01-01 → 2023-12-31
- Canonical OOS CAGR: **-9.950%**
- Hand-rolled (pure-pandas) OOS CAGR: **-9.950%**
- |Δ|: **0.000pp** (tolerance ≤ 3pp)
- Gate 9 verdict: **PASS**

## Notes

Two independent implementations of the Ehlers-cycles portfolio:

1. Canonical: `simulate_ehlers_cycles` — DSP primitives (roofing
   filter, autocorrelation periodogram DC, adaptive RSI) combined
   with in-simulator per-asset state machine and equal-weight
   allocation.
2. Hand-rolled: re-uses `compute_signal_per_asset` (so the DSP
   primitives are identical) but rebuilds the portfolio layer
   from scratch with explicit pandas operations (state/N_on,
   shift-by-one alignment, spread/swap accounting).

Both include frictions (Pepperstone 0.05% spread, 0.03%/night
swap). Any difference isolates portfolio-wiring bugs — the DSP
signal itself is shared.

vectorbt / bt / backtrader ports were NOT produced because:

- Those libraries do not expose Ehlers DSP primitives (Hilbert
  Transformer, autocorrelation periodogram, two-pole roofing
  filter, SuperSmoother). Porting would require implementing
  them inside the library's custom-indicator API — the result
  would be a copy of our own primitives with a thin wrapper,
  not an independent implementation.
- The OOS verdict is FAIL on multiple binding gates; additional
  library ports cannot rescue a family with no edge under any
  clean implementation.

## Citations

- Lookahead audit: `[advances_fin_ml, p.31-34]`.
- Ehlers DSP primitives: `[cycle_analytics, p.77-137]`.
