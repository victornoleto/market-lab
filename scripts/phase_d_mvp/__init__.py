"""Phase D-MVP — Strategy D OHLCV-only grid (Leads D1 + D4).

Entry points:

* ``download_ibrx100.py`` — fetch OHLCV for the IBrX-100 proxy via yfinance
  ``.SA`` suffix. One-shot; cached to ``.cache/yfinance/``.
* ``run_single.py`` — backtest a single D1/D4 config over IS/OOS/FWD splits.
* ``orchestrator.py`` — iterate the full grid (24 D1 + 18 D4 = 42 configs),
  compute PBO + DSR deflator, write ``reports/phase_d_mvp/SUMMARY.md``,
  flag early-abort when no config clears PBO < 0.5 AND DSR p < 0.1.

See ``specs/strategy_d_br_ranking.md`` Fase D-MVP and the plan at
``/home/victor/.claude/plans/zazzy-booping-oasis.md``.
"""
