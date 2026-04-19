# 2026-04-15 (noite, pós-pivô) — `tiingo_service` lazy-cache entregue ✅

**Gatilho:** item 1 do backlog pós-pivô de horas antes. Ver spec v3.1 em
`docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md`
(2 rodadas `/judge-spec` adversarial + Smoke #1 empírico antes de
commitar implementação).

**O que foi entregue:**

- **Storage refactor** — `TiingoStorage` agora nested por frequency; slack
  per-`(asset_class, freq)` (crypto 24/7 não compartilha slack com equity
  RTH); `has()` aceita `date|datetime`; manifest grava `requested_range`
  em v1; lockfile protege contra migração parcial concorrente.
- **Migração executada** — 1675 tickers daily movidos para
  `data/tiingo/daily/prices/` com backup automático em
  `data/tiingo_premigrate_20260415-181358.tar.gz` (149 MB). pgrep guard
  contra bulk ativo.
- **Source refactor** — `TiingoSource.fetch()` aceita `frequency`;
  rotea equity/etf 1h para `/iex/`; crypto/forex 1h usam `resampleFreq=1hour`;
  aplica split/dividend adjust em IEX via ratio derivado do daily cache
  (reusa pattern do `adjust.py`); `NotImplementedError` explícito se equity
  sem daily cache ou frequency fora do whitelist v1 (`{daily, 1hour}`).
- **Smoke #1 empírico (gate de design)** — SPY 5a ✅ · btcusd 208d ✅ ·
  eurusd 416d ✅. Threshold ≥ 6m PASS para os 3 tickers.
  Log em `logs/tiingo.log`.
- **Smoke #2 e2e** — 3 tickers via código refatorado, persistem em
  `data/tiingo/1hour/prices/`, cache hit na segunda chamada.

**Baseline:** 377 → **405 testes verdes**. Não quebrado.

**O que destrava:** catálogo de estratégias intraday do ROADMAP §"Next
steps" item 2 — Chan mean-reversion pairs, Ehlers BP 1h, volatility
breakouts. Cada uma terá spec próprio seguindo mesmo padrão F3.D.

**Caveat residual:** cancelamento da subscrição Tiingo passa a ser safe
APENAS para daily. Intraday requer API viva por causa da janela rolling
de retention (crypto ~208 dias; SPY paid-tier superou docs públicos em
~22× mas ainda rolling). Ver spec §6.5 item 4.

**Arquivos gerados:**
- `reports/spec-judges/2026-04-15-tiingo-service-lazy-cache-design-*/`
  (4 juízes × 2 rodadas = 8 relatórios + 2 árbitros).
- `docs/superpowers/plans/2026-04-15-tiingo-service-lazy-cache.md`
  (plan executado).
- Commits: storage+migrate (commit #1), source+adjust (commit #2),
  smoke+docs (commit #3).
