# PRE_REG — 007 volatility carry proxy

## Hypothesis

Short-volatility/carry premia are structurally different from the momentum,
static-vol and RSI families already rejected. Because carry strategies can earn
frequent small gains with crash risk, this iteration only tests a conservative
long-only equity exposure filter: hold `SPY` or `QQQ` when a VIX futures ETN has
negative trailing return, otherwise hold `SHV` `[systematic_trading, p.32-35]`,
`[systematic_trading, p.119]`. The VIX ETN is used as a proxy for volatility
carry/term-structure pressure, not as a traded short leg.

MCPT, walk-forward and best-of-many controls remain mandatory because choosing
the best config from a family creates selection bias `[testing_tuning, p.318-320]`,
`[testing_tuning, p.327-335]`. PBO and DSR are hard blocks
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Data And Window

- Source: local Tiingo daily adjusted close cache under `data/tiingo/daily/prices/`.
- Required tickers: `SPY`, `QQQ`, `SHV`, `VIXY`.
- Window: common adjusted-close history from `2012-01-01` through latest local
  available date.
- Execution timing: signal uses close-to-close trailing return and is lagged one
  bar before portfolio returns are applied to avoid same-close lookahead
  `[quant_trading_chan, p.51]`.

## Exact Configs

1. `vixy_neg21_spy`: if trailing `VIXY` 21-trading-day return is below `0`, hold
   `SPY`; else hold `SHV`.
2. `vixy_neg63_spy`: if trailing `VIXY` 63-trading-day return is below `0`, hold
   `SPY`; else hold `SHV`.
3. `vixy_neg63_qqq`: if trailing `VIXY` 63-trading-day return is below `0`, hold
   `QQQ`; else hold `SHV`.
4. `vixy_neg126_spy`: if trailing `VIXY` 126-trading-day return is below `0`, hold
   `SPY`; else hold `SHV`.

No thresholds, assets or lookbacks may be changed after results are observed.

## Benchmark

- Primary benchmark: same risk asset buy-and-hold on the exact strategy return
  index (`SPY` for SPY configs, `QQQ` for QQQ config).
- Secondary benchmark: `SPY` buy-and-hold on the exact strategy return index.

## Planned Gates

- Economic: best config must beat same-asset buy-and-hold Sharpe and have positive
  CAGR.
- IS MCPT: fixed best config, 200 permutations, pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT: fixed best config, 100 permutations, pass if `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO: 8 blocks over the 4 config return matrix, pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR: pass if `p < 0.05` using `cumulative_n_trials_after=20`
  `[advances_fin_ml, p.222-223]`.
- WF windows: 4y train / 1y test / 1y step; pass if at least 6 positive windows
  out of 8 or more `[testing_tuning, p.148-150]`.
- OOS: final 20% single holdout positive `[advances_fin_ml, p.196-202]`.
- FWD stress: final 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: stationary bootstrap 99.9% daily mean CI low > 0
  `[testing_tuning, p.246-247]`.
- Cross-lib/proxy: independent vectorized recomputation must match primary CAGR
  within +/-3 percentage points `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If required Tiingo files are missing or common history is under 5 years, mark
  `data_blocked` and stop.
- If the family fails MCPT, PBO or DSR, add it to dead ends and do not locally tune
  VIXY lookbacks in the next iteration without a new mechanism.
- If the best config only reduces drawdown but loses Sharpe to same-asset
  buy-and-hold, verdict is `fail` even if statistical gates pass.
- No deploy claim is possible; capital remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials_before=16`.
- `n_trials=4`.
- `cumulative_n_trials_after=20`.
