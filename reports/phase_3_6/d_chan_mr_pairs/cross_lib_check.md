# Cross-lib concordance — Family D Chan MR pairs (non-Kalman)

- Winner cell: **lookback=126, entry_z=2.0, exit_z=0.0, stop_z=4.0, coint_gate=1.0 (disabled for cross-lib)**
- OOS window: 2018-01-01 → 2023-12-31
- Canonical OOS CAGR: **-1.536%**
- Hand-rolled (pure-numpy) OOS CAGR: **-1.165%**
- |Δ|: **0.371pp** (tolerance ≤ 3pp)
- Gate 9 verdict: **PASS**

## Notes

Two independent implementations of the Chan pairs mechanics:

- **Canonical:** pandas rolling helpers (`.rolling().mean()`, `.rolling().var()`, covariance via `E[xy] - E[x]E[y]`) in `src/ai_trade/backtest/strategies/phase3_6_d_chan_mr_pairs.py`.
- **Hand-rolled:** explicit window slices with numpy mean/var (Bessel-corrected) per bar. No pandas rolling primitives.

The EG cointegration gate is disabled for the comparison (coint_gate=1.0) — we are checking the signal + hedge-ratio + entry/exit + cost engine, not the stat test. That isolates the arithmetic reconciliation from stochastic branches.

vectorbt / bt / backtrader ports were not produced because the OOS verdict is FAIL across every binding edge gate (Sharpe, CAGR, DSR p-value, bootstrap CI, IR vs SPY, cost×2 sensitivity). Additional library ports cannot rescue a family that has no edge under any clean implementation.

## Citations

- Lookahead audit: `[advances_fin_ml, p.31-34]`.
- Chan pairs mechanics: `[algo_trading_chan, p.51-54, p.71-73]`.
