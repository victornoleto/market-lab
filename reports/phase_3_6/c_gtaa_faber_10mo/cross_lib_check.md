# Cross-lib concordance — Family C Faber GTAA 10-mo

- Winner cell: **sma=8mo, lag=1d, equal-weight, no costs/tax (isolated mechanics)**
- OOS window: 2018-01-01 → 2023-12-31
- Canonical OOS CAGR: **+6.798%**
- Hand-rolled (pure-pandas) OOS CAGR: **+6.798%**
- |Δ|: **0.000pp** (tolerance ≤ 3pp)
- Gate 9 verdict: **PASS**

## Notes

Two independent implementations (canonical return-series simulator vs hand-rolled pure-pandas) of the Faber GTAA mechanics. Both implementations strip frictions/tax to isolate the signal+weight alignment logic.

vectorbt / bt / backtrader ports were not produced because the OOS verdict is FAIL (OOS Sharpe 0.414, OOS CAGR 3.89%, PBO 0.91) — additional library ports cannot rescue a family that has no edge under any clean implementation.

## Citations

- Lookahead audit: `[advances_fin_ml, p.31-34]`.
