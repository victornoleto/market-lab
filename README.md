# market-lab

Deterministic research toolkit for systematic-trading and portfolio backtests.
The repository contains a Python backtest engine, validation utilities and
reproducible study folders. It is a research lab, not a live-trading product or
financial advice.

## Status

The project is in maintenance mode. Active strategy research did not produce a
candidate that cleared the full robustness stack, so no live deployment is
authorized by this repository.

Recent research consolidated `35% GDE / 40% RSST / 25% ZROZ`
(`GDESIM/RSSTSIM/ZROZSIM`) as the no-margin B4-v2 research core, then closed that
package as documentation/robustness work. The active follow-on study is
`studies/spy_sso_upro_replacement/`, a static-first SPY replacement search that
pivoted to explicit target leverage and benchmark-relative equity dominance after
static near-misses failed strict rolling robustness. The practical after-tax rerun
excludes daily updates, models annual Brazilian DARF with `AnnualDarfEngine`, and
currently finds 3 monthly active risk-on/off dominance passes and 0 static passes;
the lead is `SMA300 L2.75 off 60 ZROZ / 40 GLD monthly`. This remains
research-only and does not authorize capital allocation `[testing_tuning,
p.327-335]`, `[advances_fin_ml, p.208-211]`, `[leverage_for_the_long_run, p.13]`.

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
