# 2026-04-15 (noite, final) — Pivô: intraday short-hold + `tiingo_service` lazy-cache

**Gatilho:** conversa pós-F3.D sobre tempo real de trade. Checando os
trades persistidos dos 9 portfolios (`grid_portfolio_20260415-1541`):

- **Clenow:** duração mediana 56-63 dias, média 65-74, máximo 287-378.
- **Ehlers BP Swing:** mediana 1-22 dias, mas média inflada (129-146
  dias) por posições presas por até 4 anos em trends sem hit de stop.

Isso é **fundamentalmente incompatível** com o objetivo do projeto:
operar CFDs na Pepperstone, que cobra swap/overnight diário. Mesmo
ignorando swap por ora no backtest, a *seleção* de estratégias tem
que respeitar "curto e pontual" desde já, senão estamos otimizando a
coisa errada.

**Duas decisões derivadas:**

1. **`tiingo_service` (lazy-cache) substitui o bulk diário.** Camada
   nova que, em vez de pre-baixar todos os tickers numa única shot,
   memoiza chamadas por `(endpoint, params)`: se o dado já existe em
   `data/cache/`, retorna; senão, requisita, persiste, retorna. Isso:
   (a) permite intraday (endpoints Tiingo IEX 1min/5m/1h) sem bulk
   prévio; (b) ainda funciona pra daily quando necessário; (c) o
   `TiingoStorage`/`manifest.json` atual vira um caso especial dessa
   camada, não o protocolo primário.
2. **Catálogo de estratégias re-prioritizado em torno de short-hold.**
   Clenow sai do caminho de produção (fica como histórico). Entram:
   Chan mean-reversion/pairs `[algo_trading_chan]`, Ehlers BP em 1h
   (mesma lógica, timeframe novo), volatility breakouts `[volatility_
   trading, Sinclair]`. AFML sofisticado — antes priorizado como
   "caminho B" — fica deferred pra entrar depois como filtro
   secundário sobre uma estratégia intraday que mostre edge.

**O que NÃO muda:**
- F3.D sub-result (diversificação resolve WF) continua valioso. O
  pacote `src/ai_trade/backtest/portfolio/` é timeframe-agnostic —
  será reusado pra combinar estratégias intraday.
- Gates anti-overfit (CPCV/PBO/DSR/WF) continuam os mesmos — o que
  muda é o que alimenta eles.
- Regra da citação `[book.slug, p.X]` continua inviolável.
- Stage 1 (edge em dados limpos) vs Stage 2 (custos Pepperstone reais)
  continua como estruturado no ROADMAP §"Two-stage backtest".

**Arquivos afetados nesse commit:**
- `JORNADA.md` (seções "Onde estamos hoje" + "O que vem a seguir" +
  este changelog).
- `ROADMAP.md` §"Current status" + §"Next steps" (pivô documentado).

**Próximo passo concreto** (pra nova sessão): brainstorming do
`tiingo_service` — design da chave de cache, relação com
`TiingoStorage` existente, migração dos backtests existentes.
