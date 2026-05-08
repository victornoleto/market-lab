# Public Summary

`market-lab` is a deterministic research codebase for systematic trading and
portfolio backtesting. It combines a Python backtest engine, validation tools,
market-data adapters, and documented research studies.

## Current Status

The project is in maintenance mode. The active-trading research tracks did not
produce a strategy that cleared the full validation stack, so no live trading
deployment is authorized by this repository.

The useful output is the research infrastructure:

- event-driven and vectorized backtest components;
- data adapters for public/research market data sources;
- validation tools for PBO, DSR, walk-forward, bootstrap and cross-library checks;
- reproducible study folders with hypotheses, scripts, results and conclusions;
- a book-citation discipline for strategy, indicator and gate decisions.

## What This Repository Is Not

- It is not financial advice.
- It is not a live-trading system ready for capital allocation.
- It does not include private credentials, broker accounts, raw copyrighted PDFs,
  personal portfolio projections, or local data caches.

## Main Lessons

- Many plausible strategies fail after multiple-testing correction and honest
  out-of-sample validation.
- CAGR and drawdown alone are insufficient for promotion; statistical robustness
  gates are mandatory.
- Reproducible research benefits from keeping hypotheses, code and verdicts
  together inside each study directory.

See `docs/PROJECT_HISTORY.md` for the historical timeline and `README.md` for
setup and repository structure.
