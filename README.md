# market-lab

Deterministic research toolkit for systematic-trading and portfolio backtests.
The repository contains a Python backtest engine, validation utilities and
reproducible study folders. It is a research lab, not a live-trading product or
financial advice.

## Status

The project is in maintenance mode. Active strategy research did not produce a
candidate that cleared the full robustness stack, so no live deployment is
authorized by this repository.

Recent research consolidated `studies/return_stacked_core/` as the canonical
Return-Stacked Core (RSC) folder. The anchor is RSC-US
`35% GDE / 40% RSST / 25% ZROZ` (`GDESIM/RSSTSIM/ZROZSIM`), with a documented
RSC-Global diversification branch. It remains documentation/robustness work, not
deployment authorization. The active follow-on study is
`studies/spy_sso_upro_replacement/`, a static-first SPY replacement search that
pivoted to explicit target leverage and benchmark-relative equity dominance after
static near-misses failed strict rolling robustness. The practical after-tax rerun
excludes daily updates, models annual Brazilian DARF with `AnnualDarfEngine`, and
currently finds 3 monthly active risk-on/off dominance passes and 0 static passes;
the lead is `SMA300 L2.75 off 60 ZROZ / 40 GLD monthly`. This remains
research-only and does not authorize capital allocation `[testing_tuning,
p.327-335]`, `[advances_fin_ml, p.208-211]`, `[leverage_for_the_long_run, p.13]`.

A new root-level `lrs/` restart opened on 2026-06-07 to study the Gayed/SMA LRS
line again from first principles. It is research-only and not deployment
authorization. Phase 2 now varies target leverage and realized-volatility
throttles after the SMA200 weekly baseline and risk-off sweep. Current top score:
`SPY` L`2.00`, risk-off `50 ZROZ / 25 GLD / 25 CASH`, `RV21 <= 30%`, lag `3`,
after-tax CAGR `15.44%`, MDD `-39.28%`. Best QQQ: L`1.75`, risk-off
`40 ZROZ / 40 GLD / 20 IEF`, `RV63 <= 40%`, lag `0`, after-tax CAGR `19.46%`,
MDD `-42.58%` `[leverage_for_the_long_run, p.4-7]`, `[systematic_trading,
p.137-148]`.

See:

- `docs/PUBLIC_SUMMARY.md` for the public-facing summary;
- `docs/PROJECT_HISTORY.md` for the condensed project timeline;
- `docs/CURRENT_STATE.md` for the latest technical snapshot;
- `docs/investment-mandate.md` for validation and governance rules.
- `studies/SUMMARY.md` for the compact ledger of tested strategies, metrics,
  verdicts and cleanup-preservation rules.

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
