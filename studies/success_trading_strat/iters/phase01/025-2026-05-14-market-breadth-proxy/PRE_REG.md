# PRE_REG — 025 market breadth proxy

## Hypothesis

Market breadth should provide a different information source from the prior price,
volume, VIX, yield, seasonality and crypto families. A broad advance/decline-style
proxy measures whether many liquid constituents confirm index strength, rather
than relying on the index price alone `[trading_systems_methods, p.548-549]`.
Because this uses a current large-cap proxy list rather than point-in-time index
membership, any passing result is capped at `promising_not_validated`; survivorship
bias blocks a `winner` claim `[trading_systems_methods, p.941]`.

## Data And Window

- Local Tiingo daily adjusted close cache under `data/tiingo/daily/prices/`.
- Risk assets: `SPY`, `QQQ`; defensive sleeve: `SHV`.
- Breadth proxy universe: current large liquid US equities hardcoded in
  `run_iter025.py`, requiring at least 20 available names.
- Window: common daily history from 2010-01-01 through the latest common date.
- Signals are lagged one bar before trading to avoid same-close lookahead
  `[trading_systems_methods, p.27]`.

## Exact Configs

1. `spy_breadth_sma63_gt55`: hold `SPY` when at least 55% of proxy constituents
   close above their 63-day SMA; otherwise hold `SHV` `[trading_systems_methods,
   p.285]`.
2. `qqq_breadth_sma63_gt55`: same rule on `QQQ`.
3. `spy_breadth_sma126_gt55`: hold `SPY` when at least 55% of constituents close
   above their 126-day SMA `[trading_systems_methods, p.285]`.
4. `qqq_breadth_sma126_gt55`: same rule on `QQQ`.

## Benchmark

Each config must beat same-window buy-and-hold of its own risk asset on Sharpe.
CAGR and MDD are reported as warning/tier diagnostics, not hard blocks per mandate.

## Planned Gates

- Data freshness: latest common date >= 2026-03-31.
- Economic Sharpe vs same-asset buy-and-hold.
- IS MCPT with 200 permutations, pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` over the four configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward positive windows: at least 6, or all windows if fewer than 8
  `[testing_tuning, p.148-150]`.
- Single-block OOS final 20% positive `[advances_fin_ml, p.196-202]`.
- Latest 63-observation FWD stress positive `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% mean daily CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib NumPy/pandas CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If fewer than 20 breadth names are available, close `data_blocked`.
- If data are stale, no promotional status is allowed.
- If any PBO/DSR/MCPT hard gate fails, close `fail` and do not tune breadth
  thresholds or SMA lengths locally `[testing_tuning, p.327-335]`.
- Even if all numeric gates pass, survivorship bias from current constituent
  selection prevents `winner=true`; record at most `promising_not_validated`.

## Trial Accounting

- `cumulative_n_trials` before: 84.
- `n_trials` planned: 4.
- `cumulative_n_trials` after: 88.
