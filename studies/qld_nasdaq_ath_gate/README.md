# QLD Nasdaq ATH Gate

Quick study for the rule:

> The signal line for Nasdaq 100 is 85% of the last 46 weeks all-time high. If
> Nasdaq 100 is above the line, invest in QLD. Otherwise hold cash/T-bills.

Implementation notes:

- Signal proxy: `QQQSIM` long-history Nasdaq-100 proxy from testfol.io.
- Risk-on asset: `QQQSIM?L=2`, resolved through the local testfol.io alias map to `QLDSIM`.
- Comparison leverage: `QQQSIM?L=3`, resolved to `TQQQSIM`.
- Risk-off asset: `CASHX` from testfol.io cache, used as a T-bill/cash proxy.
- Weekly signal uses the last available weekly close, then applies the new
  allocation on the next trading day to avoid same-close look-ahead.
- The fixed 46-week high-watermark band is treated as a trend/risk gate in the
  leveraged rotation family `[leverage_for_the_long_run, p.13, p.21]`.
- Rolling-window diagnostics are included because full-period CAGR can hide
  unstable regimes `[trading_systems_methods, ch.21]`.

Run:

```bash
uv run python studies/qld_nasdaq_ath_gate/run.py
```

Outputs:

```text
studies/qld_nasdaq_ath_gate/results/default/
```

This is a fast diagnostic, not a deployable strategy verdict. Costs, taxes,
slippage and robustness gates are not modeled here. Pre-inception `QQQSIM`,
`QLDSIM` and `TQQQSIM` bars are modelled testfol.io approximations, not directly
tradeable ETF history.
