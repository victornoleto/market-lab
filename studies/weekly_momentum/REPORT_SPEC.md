# Weekly Momentum Report Spec

Every run writes a deterministic report bundle under:

```text
studies/weekly_momentum/results/{variation}/{config_slug}/
```

Required files:

- `config.json`: exact strategy parameters.
- `metrics.csv`: metric table with `strategy` and `spy` columns.
- `metrics.json`: machine-readable run summary.
- `equity.csv`: strategy equity curve.
- `returns.csv`: strategy daily returns.
- `weights.csv`: daily portfolio weights.
- `trades.csv`: buy/sell event log.
- `benchmark_spy.csv`: aligned SPY buy-and-hold benchmark.
- `report.md`: human-readable deterministic report.
- `plots/equity_vs_spy.png`: strategy vs SPY equity.
- `plots/drawdown_vs_spy.png`: strategy vs SPY drawdown.
- `plots/relative_to_spy.png`: strategy equity divided by SPY equity.
- `plots/rolling_252d_sharpe.png`: rolling 252-trading-day Sharpe comparison.
- `plots/rolling_windows_1_3_5_10y.png`: 2×2 panel with 1/3/5/10-year rolling CAGR vs SPY and strategy CAGR edge shading.

`report.md` must include these sections:

- `Strategy`: universe, signal, execution timing, holdings, benchmark.
- `Strategy`: universe, signal, execution timing, holdings, absolute-momentum filter, market regime filter, benchmark.
- `Result Summary`: date range, asset count, headline CAGR/MDD/Sharpe and terminal relative wealth.
- `Metrics`: table comparing strategy against SPY.
- `Plots`: embedded links to all required plots, including rolling 1/3/5/10-year windows.
- `Trades`: event count and recent trade table.
- `Caveats`: survivorship, daily close-to-close proxy, missing costs/taxes/slippage, top-1 path risk.
- `Review Notes`: deterministic placeholder for manual or AI-assisted interpretation outside runtime.

Runtime LLM calls are intentionally excluded. Repository convention keeps LLM/AI
analysis outside deterministic Python scripts.
