# market-lab

Deterministic research toolkit for systematic-trading and portfolio backtests.
The repository contains a Python backtest engine, validation utilities and
reproducible study folders. It is a research lab, not a live-trading product or
financial advice.

## Status

The project is in maintenance mode. Active strategy research did not produce a
candidate that cleared the full robustness stack, so no live deployment is
authorized by this repository.

Current discovery work in `studies/static_spy_beater_portfolio/` uses
`35% GDE / 40% RSST / 25% ZROZ` (`GDESIM/RSSTSIM/ZROZSIM`) as its no-margin internal
core benchmark. The study objective is to find static or later tactical portfolios
that beat this core by rolling equity dominance, not by maximum drawdown alone. This
is research-only and does not authorize capital allocation.

See:

- `docs/PUBLIC_SUMMARY.md` for the public-facing summary;
- `docs/PROJECT_HISTORY.md` for the condensed project timeline;
- `docs/CURRENT_STATE.md` for the latest technical snapshot;
- `docs/investment-mandate.md` for validation and governance rules.

## What Is Included

- `src/market_lab/` — Python package with data adapters, backtest engine,
  strategies, metrics, validation and grid tooling.
- `tests/` — core test suite.
- `studies/` — reproducible research studies. Each study should keep its own
  hypotheses, scripts, results and reports together.
- `books/summaries/` and `knowledge/` — derived research notes used for
  citation discipline.
- `scripts/` — deterministic utility scripts.

## What Is Excluded

- raw copyrighted PDFs;
- credentials and local broker/API tokens;
- personal investment projections;
- local market-data caches and generated parquet files;
- local agent session state.

## Setup

Requirements:

- Python 3.11+
- `uv` recommended

```bash
uv sync
```

Run tests:

```bash
uv run pytest
```

## Repository Layout

```text
market-lab/
├── src/market_lab/       # core Python package
├── tests/              # pytest suite
├── scripts/            # deterministic utilities
├── studies/            # research studies and archived studies
├── docs/               # public docs, mandate and project history
├── books/              # summaries and metadata, no raw PDFs
├── knowledge/          # aggregated research notes
├── data/               # manifests/readmes only; generated data is ignored
```

## Validation Philosophy

Strategy promotion requires evidence beyond attractive backtest metrics:

- PBO and CPCV checks;
- Deflated Sharpe Ratio;
- walk-forward validation;
- bootstrap confidence intervals;
- single-block OOS and forward stress windows;
- cross-library agreement.

Every strategy, indicator, parameter and validation gate should cite a source in
the format `[book.slug, p.X]` where applicable.

## License

MIT. See `LICENSE`.
