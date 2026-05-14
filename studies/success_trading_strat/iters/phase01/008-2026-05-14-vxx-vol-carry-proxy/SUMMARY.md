# SUMMARY — 008 VXX volatility-carry proxy

## Verdict

`fail`. The `VXX` volatility-carry proxy produced an economically decent SPY
filter, but failed the promotion stack: IS MCPT, WF MCPT, PBO and DSR all blocked
promotion.

## What Was Tested

Four pre-registered long-only configs used trailing negative `VXX` returns as a
risk-on filter into `SPY` or `QQQ`, otherwise `SHV`. Signals were shifted one bar
to avoid same-close lookahead `[quant_trading_chan, p.51]`. Best config:
`vxx_neg21_spy`.

## Benchmark Comparison

- Best `vxx_neg21_spy`: CAGR 9.86%, Sharpe 0.935, MDD -29.54%.
- Same-asset `SPY` buy-and-hold: CAGR 14.74%, Sharpe 0.910, MDD -33.70%.
- The strategy improved Sharpe and drawdown modestly, but materially lagged SPY
  CAGR/terminal wealth.

## Gates

- IS MCPT: fail, `p=0.145` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.10` with 100 reps and 10 WF windows.
- PBO: fail, `0.686 >= 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.0554` using cumulative `n_trials=20`
  `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 9/10 positive.
- OOS: pass, final 20% return +50.85%.
- FWD stress: pass, last 63 trading days +13.97%.
- Bootstrap: pass, 99.9% mean daily CI low `+0.0000665`.
- Cross-lib: pass, NumPy CAGR delta 0.00pp.

## Lessons

`VXX` data made the volatility-carry proxy testable, but the edge is not robust
under permutation or CSCV. The result looks like a risk-filter that trades off
return for drawdown, not a validated standalone strategy. Because PBO and MCPT
failed, local tuning of VXX lookbacks should stop without a new mechanism
`[testing_tuning, p.327-335]`.

## Next Step

Pivot away from simple trailing-volatility-ETP decay filters. A conservative next
iteration should test a different mechanism with confirmed data, such as a
multi-asset EWMAC forecast family using Carver's fixed EWMAC variants rather than
optimizing VXX thresholds `[systematic_trading, p.118-119]`.
