# PRE_REG - 028 Gayed LETF QQQ rotation

## Hypothesis

Test whether a simple Gayed-style leverage rotation on Nasdaq exposure can clear
the success_trading_strat gates: use `QQQ` as the regime signal, hold `QLD` or
`TQQQ` when `QQQ` is above a lagged moving-average regime filter, otherwise hold
`SHV`. The mechanism is volatility/regime control for leveraged equity exposure,
not a local retune of the prior unlevered `SPY/QQQ` SMA family
`[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.16-17]`.

This is research-only. Capital remains 100% Plano C and no deploy is authorized
`[advances_fin_ml, p.222-223]`.

## Data And Window

- Local Tiingo adjusted daily closes from `data/tiingo/daily/prices/`.
- Required tickers: `QQQ`, `QLD`, `TQQQ`, `SHV`.
- Window: common daily history from `2010-02-12` onward, chosen before testing to
  include real `TQQQ` history and avoid comparing different ETF inception windows.
- Signals are shifted one trading day before execution to avoid same-close
  lookahead `[advances_fin_ml, p.31-34]`.

## Exact Configs

1. `qld_qqq_sma200`: risk asset `QLD`, risk-on if `QQQ > SMA200`.
2. `tqqq_qqq_sma200`: risk asset `TQQQ`, risk-on if `QQQ > SMA200`.
3. `qld_qqq_sma200_rv70`: risk asset `QLD`, risk-on if `QQQ > SMA200` and QQQ
   21d realized volatility is below its trailing 252d 70th percentile.
4. `tqqq_qqq_sma200_rv70`: risk asset `TQQQ`, same volatility filter.

The 200-day moving average is Gayed's canonical regime filter; the 21d/252d/70th
percentile volatility clause is a sparse volatility-control variant, justified by
leverage sensitivity to volatility rather than an open grid
`[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.16-17]`,
`[trading_systems_methods, p.1085-1091]`.

## Benchmark

- Compare each config to same-window buy-and-hold of its risk asset (`QLD` or
  `TQQQ`) on Sharpe, with CAGR/MDD reported as tier context only.

## Planned Gates

- Data freshness: latest common date must be at least `2026-03-31`.
- Economic Sharpe vs same-risk-asset benchmark.
- IS MCPT with 200 permutations, pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO over the 4 config return matrix with 8 blocks, pass `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR using cumulative trials after this iteration (`96`), pass `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward positive windows: at least 6 if there are 8+ windows, otherwise all
  available windows positive `[testing_tuning, p.148-150]`.
- Single-block OOS final 20% return positive `[advances_fin_ml, p.196-202]`.
- Latest 63d FWD stress return positive `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% mean daily CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib numpy/pandas CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If any required local price file is missing or stale, stop as `data_blocked` and
  consume zero trials.
- If PBO, DSR, IS MCPT or WF MCPT fails, verdict cannot be `winner`.
- Do not add MA lengths, volatility thresholds, bands, cash alternatives or QLD/TQQQ
  leverage variants after seeing results `[testing_tuning, p.327-335]`.
- Do not modify `docs/investment-mandate.md`; no commit or push.

## Trial Accounting

- `cumulative_n_trials` before: 92.
- New strategy configs: 4.
- `cumulative_n_trials` after if tested: 96.
