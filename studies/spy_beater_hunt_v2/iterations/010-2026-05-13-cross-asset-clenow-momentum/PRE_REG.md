# PRE_REG — 010-cross-asset-clenow-momentum

## Hypothesis

Cross-asset momentum can improve long-term robustness versus SPY buy-and-hold by
rotating among equity, long-duration Treasuries, gold and managed-futures proxy
assets instead of timing only SPY/QQQ. The ranking signal is Clenow's 90-trading-day
annualized log-price regression slope multiplied by R², which rewards smooth
medium-term momentum and penalizes choppy moves `[stocks_on_the_move, p.75-77]`.
New risk entries are blocked when SPY is below its 200-day SMA, following Clenow's
market regime filter `[stocks_on_the_move, p.66-67]`. Parameter tuning is not
allowed because Clenow explicitly warns against optimized magical numbers
`[stocks_on_the_move, p.219-224]`.

## Data And Window

- Source: `data/testfolio/cache/history.parquet` via existing `load_testfolio_series`.
- Required labels: `SPYSIM`, `ZROZSIM`, `GLDSIM`, `KMLMSIM`, `CASHX`.
- Window: common non-null daily window across all required labels.
- Benchmark: buy-and-hold `SPYSIM` over the identical return index.

## Exact Configs

1. `clenow_xasset_top1_cash`: weekly Wednesday rebalance; rank `SPYSIM`,
   `ZROZSIM`, `GLDSIM`, `KMLMSIM` by 90-day adjusted slope; hold 100% top-ranked
   asset if `SPYSIM > SMA200`, otherwise `CASHX`.
2. `clenow_xasset_top2_invvol_cash`: weekly Wednesday rebalance; same ranking and
   regime filter; hold top 2 assets weighted by inverse 63-day realized volatility,
   otherwise `CASHX`. Inverse-vol risk allocation follows the same risk-not-cash
   sizing principle as Clenow's ATR risk parity `[stocks_on_the_move, p.83-89]`.

No other configs, lookbacks, assets, rebalance days or thresholds may be tested in
this iteration.

## Planned Gates

- Economic: best config CAGR and terminal equity ratio must beat SPY.
- PBO `< 0.5` over the two pre-registered configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6/8 windows beat SPY `[testing_tuning, ch.12]`.
- OOS: final 25% holdout CAGR beats SPY `[advances_fin_ml, p.196-202]`.
- FWD: final 3y CAGR beats SPY `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% CI low of daily excess returns is positive
  `[advances_fin_ml, p.196-202]`.
- Cross-lib: vectorized implementation and explicit loop CAGR differ by <= 3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If required labels are unavailable, return `data_blocked`; do not substitute
  assets after seeing data.
- If the common window starts materially later than 1988 because of `KMLMSIM`, keep
  the same window but record the limitation; do not shorten further.
- If the best config fails any hard gate, verdict is `fail` even if it beats SPY.
- If the result depends only on top1/top2 choice, do not tune top-k or lookbacks in
  this iteration.
- Capital remains 100% Plano C; no deployment authorization.

## Trial Accounting

- `cumulative_n_trials` before: 18.
- `n_trials` in this iteration: 2.
- `cumulative_n_trials` after: 20.
