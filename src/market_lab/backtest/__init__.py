"""market_lab.backtest — backtest engine, data sources, validation, metrics.

The architectural principle is source-agnostic testing: research data adapters
and execution/calibration data can vary while the engine contract stays stable.

Phase 2 scope:
    data/       — fetch + normalize OHLCV from external sources
    (later)
    engine/     — portfolio accounting, execution simulator
    validation/ — CPCV, PBO, DSR, walk-forward (ported from AFML)
    metrics/    — Sharpe, Sortino, max DD, CAGR
    strategies/ — Clenow (first replication target), AFML meta-label, ...
"""
