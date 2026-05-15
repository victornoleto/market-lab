# SUMMARY - Phase 3 Iteration 006

## Verdict

`economic_beater_not_validated`. No winner, no deploy implication, mandate remains 100% Plano C.

## Tested

Six pre-registered high-beta relative-rotation configs over `QQQ`, `SMH`, `SOXX` and `XLK`: top-1/top-2 by 63d or 126d momentum, plus 126d momentum divided by 63d realized volatility. The mechanism stays fully invested in the strongest high-beta sleeves rather than rotating to cash `[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`.

Physical daily-file audit confirmed `QQQ`, `SMH`, `SOXX`, `XLK`, `SPY` and `SHV` parquets exist through 2026-05-13 with usable close columns.

## Benchmark Comparison

Best config by pre-registered Sharpe selection: `top2_m63`.

- Strategy: CAGR `15.98%`, terminal wealth `37.92x`, Sharpe `0.680`, MDD `-59.48%`.
- Primary equal-weight `QQQ/SMH/SOXX/XLK` buy-and-hold: CAGR `15.50%`, terminal wealth `34.28x`, Sharpe `0.672`, MDD `-59.35%`.
- `SPY` opportunity benchmark: CAGR `10.19%`, terminal wealth `10.79x`.
- Best single sleeve context, `SMH` buy-and-hold: CAGR `17.06%`, terminal wealth `47.63x`.

The Phase 3 economic gate passed versus the primary equal-weight opportunity basket and `SPY`, but the margin was small and did not beat the best single sleeve.

## Gates

- IS MCPT: fail, `p=0.055` vs required `<=0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.850` vs required `<=0.05` `[testing_tuning, p.318-320]`.
- PBO: pass, `0.345 < 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.2983` with cumulative `n_trials=252` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, `19/21` positive.
- OOS and FWD 63d: pass.
- Bootstrap: pass, 99.9% mean daily CI low `0.000107`.
- Cross-lib/vector parity: pass.

## Lessons

High-beta rotation is economically closer to a useful mechanism than the pure defensive filters, but the edge over equal-weight buy-and-hold is too small and fails MCPT/DSR. The high annual turnover (`16.05`) also makes the gross no-tax/no-cost result optimistic.

## Next Step

Pivot to the next Phase 3 recommended branch: crypto/equity rotation over confirmed `BTCUSD`/`ETHUSD`/`QQQ`/`GLD`, or drawdown-adaptive sizing on a high-beta universe. Do not locally tune the `top2_m63` lookback/top-k choice without a new mechanism `[testing_tuning, p.327-335]`.
