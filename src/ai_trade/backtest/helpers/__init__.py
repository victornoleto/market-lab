"""Pure-function helpers shared across strategies (no strategy state).

Modules here hold deterministic calculations referenced from multiple
strategy files (or kept around for Phase 3 leads after a strategy is
retired). Only side-effect-free utilities live here — anything that
needs a Portfolio, Bar, or Order goes back into ``strategies/``.
"""
