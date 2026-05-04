"""News calendar features (Forex Factory) — Pipeline v4 Redesign module.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: 009-news-calendar em studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md

Citations:
- [evidence_based_ta, ch.7] — efeitos de news calendar em estrategias de trading;
  impacto de eventos macroeconomicos de alto impacto sobre o timing de entradas.

Trilha A1 do SPEC.md: news calendar (Forex Factory CSV, free).

Interface esperada (task 009):
  load_news_calendar(csv_path: str) -> pd.DataFrame
  compute_news_features(trades: pd.DataFrame, news: pd.DataFrame) -> pd.DataFrame
    -> features: is_news_window_5min, news_impact (low/med/high), minutes_to_next_high_impact

Cache em data/news/forex_factory_*.parquet.
"""
from __future__ import annotations

# TODO(009-news-calendar): implementar conforme tasks/009-news-calendar.md (detalhar on-demand apos task 008)
