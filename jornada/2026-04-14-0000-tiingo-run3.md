# 2026-04-14 — Implementação Tiingo + Phase 2.5 Run 3

**Contexto:** no início do dia, yfinance era a fonte única. Problema: 19%
de survivorship bias residual mesmo usando constituintes SPX ponto-
no-tempo do Wikipedia. Decisão: migrar pra Tiingo Power ($10/mês) que
serve dados survivorship-free via API.

**O que aconteceu:**
- Implementada a camada Tiingo (`src/ai_trade/backtest/data/tiingo_source.py`
  + `tiingo_storage.py`). Design "storage-first": todos os dados baixam
  pra disco em parquet; backtests consultam o disco, zero chamada HTTP
  em warm-run.
- Bug de dados crus vs ajustados descoberto e corrigido no commit
  `5ca9410`: estratégias liam `close` em vez de `adj_close`. Splits
  disparavam o filtro de gap 15% do Clenow; dividendos poluíam o
  oscilador do Ehlers. **Sharpe do SPY subiu de 0.31 pra 0.806** só com
  essa correção.
- **Run 3 executado em 3 experimentos:** Ehlers SPY 2015-2023
  (PBO=0.496 passa, DSR 0/24 falha), Ehlers multi-asset 16 ativos
  2005-2023 (0/16 passa tudo), Clenow SPX Tiingo 506 tickers (PBO=0.603
  fail, DSR 0/30 fail).
- Bulk background do Tiingo disparado às 22:05 (1678 tickers).

**Verdict:** PBO fica no limiar mas DSR cataclísmico em toda a linha.
Edge real mas insuficiente vs N de trials. Direção pra Run 4 decidida:
AFML meta-labeling.
