# SUMMARY — 005-carver-ewmac-trend

## Verdict

`fail`. The non-LRS Carver EWMAC trend-following control did not beat SPY
buy-and-hold and failed multiple hard gates. Capital remains 100% Plano C; this
has no deployment implication.

## What Was Tested

Two pre-fixed EWMAC variants over the common `SPYSIM`/`UPROSIM`/`CASHX`
long-history window, 1986-01-03 to 2026-04-17:

- `ewmac_16_64_upro_cash`: Carver EWMAC 16/64, scalar 3.75, cap +/-20.
- `ewmac_32_128_upro_cash`: Carver EWMAC 32/128, scalar 2.65, cap +/-20.

Positive forecast strength was mapped to next-day `UPROSIM` weight
`max(forecast, 0) / 20`; the remainder stayed in `CASHX`. Negative forecasts
were cash-only. Forecasts used 25-day price-point volatility and were shifted one
trading day before use `[systematic_trading, p.155-157]`,
`[systematic_trading, p.282-285]`, `[advances_fin_ml, p.31-34]`.

## Comparison With SPY

Same-window SPY benchmark:

- CAGR: 11.47%.
- MDD: -55.14%.
- Sharpe: 0.682.
- Terminal equity: 79.86x.

Best config: `ewmac_32_128_upro_cash`.

- CAGR: 8.98%.
- MDD: -39.48%.
- Sharpe: 0.500.
- Terminal equity: 31.88x, or 0.40x SPY.
- Rolling CAGR win rates vs SPY: 3y 34.36%, 5y 38.57%, 10y 26.14%.

## Gates

- Economic gate: fail, CAGR and terminal equity both below SPY.
- PBO: pass, `0.000 < 0.5`, but explicitly unstable with only two configs
  `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.05867` with cumulative `n_trials=10`; required `<0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: fail, 3/8 windows beat SPY; required 6/8
  `[testing_tuning, ch.12]`.
- OOS final 25%: fail, candidate CAGR 13.52% vs SPY 15.32%.
- FWD final 3y: fail, candidate CAGR 18.59% vs SPY 21.45%.
- Bootstrap 99.9% daily excess-return CI: fail, low `-10.50%` annualized.
- Cross-lib parity: pass. Vectorized and explicit loop CAGR matched exactly.

## Lessons

- A simple long-only/cash EWMAC overlay reduced drawdown versus SPY but gave up
  too much equity exposure in long bull regimes.
- The longer 32/128 variant was less bad than 16/64, but still did not clear the
  first economic requirement.
- More local EWMAC speed tuning is disfavored; it would be a threshold grid around
  a failed single-index trend family without a distinct mechanism
  `[systematic_trading, p.60]`.
- Conservative ambiguity handling: public docs were not updated because
  `docs/CURRENT_STATE.md` and `docs/PROJECT_HISTORY.md` already have pre-existing
  unstaged modifications not made in this iteration. The required v2 artifacts
  plus `MEMORY.md` were updated instead.

## Next Step

Try a distinct mechanism rather than another single-index EWMAC/LRS timing rule.
A conservative next candidate is a pre-fixed dual-momentum or time-series
momentum control that explicitly compares SPY/QQQ or SPY/bonds before leverage,
with `n_trials <= 2` and the same long-history SPY benchmark.
