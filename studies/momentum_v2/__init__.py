"""momentum_v2 — consolidated cross-sectional momentum study.

Merges the proven engine of two earlier studies into one universe-organized
package:

* **ranking / diagnostics** from ``studies/momentum_13612_universes`` —
  rolling relative-equity dominance, moving-average overlays, staggered
  offsets, crisis-window drawdowns, the broad -> evolution -> validate funnel;
* **data / validation foundation** from ``studies/momentum`` — the shared
  :class:`market_lab.backtest.data.PostgresSource`, survivorship filters,
  YAML config, and the hard validation gates.

All results are research-only / ``promotion_eligible=false``: even with the
Postgres universe plus filters, the yfinance feed never captured most fully
delisted names, so survivorship bias remains ``[advances_fin_ml, p.208-211]``.
"""
