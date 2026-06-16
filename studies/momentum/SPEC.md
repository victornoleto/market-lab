# Momentum Study Spec

Status: research-only scaffold, initiated 2026-06-16. No deployment,
paper-trade label or mandate change.

## Objective

Use the local yfinance Postgres cache to test long-horizon momentum mechanisms
across US, BR, ETF and crypto universes. The local database removes repeated
network fetches and makes broad discovery grids feasible, but it does not remove
current-universe and delisted-symbol bias `[advances_fin_ml, p.208-211]`.

## Design Principles

1. Data comes from `yf_tickers` and `yf_daily_prices` only.
2. Filters and grids are YAML-configured, not hardcoded.
3. Every extra degree of freedom is counted as a trial `[advances_fin_ml, p.273-275]`.
4. Broad screen results are diagnostic; promotion requires PIT/delisted/corporate-action audit.
5. We evaluate mechanism families, not only the top in-sample row.

## Base Universes

| Universe | Definition |
|---|---|
| `us_stocks` | `country='us' AND asset_class='stock'` |
| `us_etfs` | `country='us' AND asset_class='etf'` |
| `us_mixed` | US stocks + ETFs |
| `br_stocks` | `country='br' AND asset_class='stock'` |
| `br_etfs` | `country='br' AND asset_class='etf'` |
| `br_mixed` | BR stocks + ETFs |
| `crypto` | `asset_class='crypto'` |
| `global_mixed` | all active stocks, ETFs and crypto |

## Filters

Default filters are defined in `config/default.yaml` and can be overridden by
asset class / country. They cover minimum history, price, median dollar volume,
observations per year and stale-data limits.

## Signals

- 13612U cross-sectional momentum `[stocks_on_the_move, p.60]`.
- 12-1 momentum.
- 3/6/12 momentum.
- Clenow trend slope × R² `[stocks_on_the_move, p.70-77, p.98]`.
- Vol-adjusted momentum and inverse-vol weighting `[systematic_trading, p.137-148]`.
- Momentum + low-vol composite.

## Validation Diagnostics

- PBO over the declared matrix `[advances_fin_ml, p.208-211]`.
- DSR with honest `n_trials` `[advances_fin_ml, p.273-275]`.
- Walk-forward positive windows `[testing_tuning, p.318-320]`.
- OOS final 30% and post-2020 FWD stress `[testing_tuning, p.327-335]`.
- Stationary block bootstrap low Sharpe confidence.
- Rolling 3/5/10/15-year minima.
- Vectorized-vs-holdings loop agreement to catch look-ahead `[advances_fin_ml, p.31-34]`.

## Outputs

- `DATA_AUDIT.md`
- `REPORT.md`
- `results/broad_results.csv`
- `results/broad_results.json`
- `results/broad_pbo.json`
