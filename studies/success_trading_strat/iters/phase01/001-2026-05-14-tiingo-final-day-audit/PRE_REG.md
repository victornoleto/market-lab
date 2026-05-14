# PRE_REG — 001 Tiingo Final-Day Audit

## Hypothesis

Infrastructure-only: before strategy research, preserve the widest feasible local
Tiingo dataset and document coverage gaps. This prevents later strategy claims
from being based on unknown data ranges, stale caches or implicit window choice
`[advances_fin_ml, p.196-202]`, `[testing_tuning, p.143-144]`.

## Data

- Local cache: `data/tiingo/manifest.json` and parquet files under
  `data/tiingo/{daily,1hour}/prices/`.
- Freshness target for critical daily tickers: at least `2026-05-08`.
- Final-day network downloads targeted `2026-05-14` where Tiingo served data.

## Planned Actions

1. Audit critical coverage via `studies/success_trading_strat/scripts/audit_tiingo_coverage.py`.
2. Refresh/download priority buckets:
   - `etf` daily, including broad, LETF, semis/AI and crypto-linked ETFs;
   - `crypto` daily;
   - `forex` daily;
   - `ndx100` daily;
   - `spx500` daily best effort.
3. Create compressed backup of `data/tiingo/`.
4. Re-run coverage audit.

## Gates

- Strategy gates are not applicable because no strategy is tested.
- Data gate: critical missing ticker count should be zero after refresh, or the
  gap is explicitly documented.

## Trial Accounting

- `cumulative_n_trials` before: `0`.
- Strategy configs tested: `0`.
- `cumulative_n_trials` after: `0`.

## Kill Rules

- If Tiingo auth fails, stop and mark `data_blocked`.
- If downloads partially fail, preserve all successful data and record the
  failure count; do not claim complete coverage.
