# US ETFs 13612 Staggered Screen

Status: research-only FAIL. No deployment, paper-trade label or mandate change.

This folder contains the focused US ETF 13612 evidence. The implementation
remains in the shared study runners `../../run.py` and `../../run_etf_staggered.py`;
this directory keeps ETF-universe outputs together.

## Scope

- Universe: curated current US liquid ETF list via yfinance (`us_etfs`).
- Source: yfinance current universe, therefore `promotion_eligible=false` until
  PIT/delisted validation exists `[advances_fin_ml, p.208-211]`.
- Staggered hypothesis start: `2000-01-01`.
- Top-N: `3,5,10`.
- Rebalance frequencies: `3,6,12` months.
- Offset policy: all offsets are equal-capital sleeves; no best-offset selection.
- Mechanisms: raw 13612 equal-weight and raw 13612 inverse-vol weights
  `[stocks_on_the_move, p.60]`, `[stocks_on_the_move, p.98-99]`,
  `[systematic_trading, p.137-148]`.
- Ranking metric: after-tax returns under Brazil's annual 15% realized-gain
  approximation.

## Command

```bash
uv run python studies/momentum_13612_universes/run_etf_staggered.py --allow-biased-yfinance --max-us-etfs 9999 --top-n 3,5,10 --rebalance-months 3,6,12 --start 2000-01-01 --max-finalists 12
```

## Verdict

Best after-tax Sharpe row:

- `mom13612_us_etfs_raw_inverse_vol_top10_reb3_staggered`
- CAGR `10.15%`
- MDD `-30.24%`
- Sharpe `0.683`
- PBO all `0.663`

Conclusion: screen-only FAIL. Staggering removed best-offset timing luck, and the
ETF edge became marginal versus SPY while still carrying meaningful drawdown.

## Files

- `REPORT_ETF_STAGGERED.md`: full ETF staggered report.
- `results/staggered_etf_results.csv`: all 18 staggered rows.
- `results/staggered_etf_results.json`: JSON copy of all rows.
- `results/staggered_etf_pbo.json`: PBO summary.
- `results/staggered_etf_finalists.csv`: diagnostic finalists.
- `plots/etf_staggered/`: aggregate plots and finalist plots.
- `plots/base/`: ETF plots from the initial base `us_all` run.
