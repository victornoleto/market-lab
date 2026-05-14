# SUMMARY — 013 crypto Donchian trend

## Verdict

`fail`. The BTC/ETH Donchian breakout pivot produced strong economic and
statistical diagnostics, but it failed two hard gates: walk-forward positives and
latest 63-observation FWD stress. No winner claim.

## What Was Tested

Four pre-registered Donchian breakout configs on `BTCUSD` and `ETHUSD`, with
lookbacks 20 and 55 and `SHV` as defensive sleeve. Signals were lagged one bar;
the mechanism follows the crypto trend-following thesis rather than another VIX
local stress `[paper.zarattini_2025_crypto_trends, §methodology]`,
`[testing_tuning, p.327-335]`.

## Benchmark Comparison

- Best `eth_don20`: CAGR 66.12%, Sharpe 1.364, MDD -35.51%.
- ETH buy-and-hold same window: CAGR 95.20%, Sharpe 1.160, MDD -92.94%.
- BTC/ETH equal-weight buy-and-hold same window: CAGR 99.17%, Sharpe 1.318, MDD -84.97%.
- The strategy improved Sharpe and drawdown versus same-asset ETH buy-and-hold,
  but gave up substantial CAGR in a very strong crypto sample.

## Gates

- Data freshness: pass, common cache ended 2026-05-13.
- Economic Sharpe vs same-asset buy-and-hold: pass, 1.364 > 1.160.
- IS MCPT: pass, `p=0.000` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: pass, `p=0.050` with 100 reps and 6 WF windows.
- PBO: pass, `0.286 < 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.00364` using cumulative `n_trials=40` `[advances_fin_ml, p.222-223]`.
- WF windows: fail, 5/6 positive versus the pre-registered 6-positive requirement.
- OOS: pass, final 20% return +45.43%.
- FWD stress: fail, latest 63 observations -6.85%.
- Bootstrap: pass, 99.9% mean daily CI low `+0.000590`.
- Cross-lib: pass, NumPy CAGR delta 0.00pp.

## Lessons

Donchian crypto trend is materially more promising than most prior pivots on
PBO/DSR/MCPT, but it still breaks the hard rule that recent forward stress must
be positive. The strategy also trades off huge buy-and-hold CAGR for drawdown
control, so it is a risk-management lead, not an obvious superior return engine.

## Next Step

Do not locally tune BTC/ETH Donchian lookbacks. If continuing crypto, use a new
economic hypothesis such as broader liquid-coin rotation or volatility sizing,
and only if the data-source caveat is resolved or explicitly treated as
research-only `[paper.zarattini_2025_crypto_trends, §applicability-to-market-lab]`.
