"""ai_trade.backtest — backtest engine, data sources, validation, metrics.

See ROADMAP.md §"Two-stage backtest: research vs. calibration" for the
architectural principle: research uses external survivorship-aware data,
calibration uses cTrader historical; the engine itself is source-agnostic.

Phase 2 scope:
    data/       — fetch + normalize OHLCV from external sources
    (later)
    engine/     — portfolio accounting, execution simulator
    validation/ — CPCV, PBO, DSR, walk-forward (ported from AFML)
    metrics/    — Sharpe, Sortino, max DD, CAGR
    strategies/ — Clenow (first replication target), AFML meta-label, ...
"""
