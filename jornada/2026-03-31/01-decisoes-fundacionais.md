# ≤ 2026-03-31 — Decisões fundacionais

- Broker escolhido: **Pepperstone via cTrader Open API** (Protobuf/TCP,
  OAuth2). Descartados XM/MT5, Alpaca, OANDA, IBKR.
- Stack: Python 3.12, docker-compose (Postgres + Grafana),
  Twisted-based `ctrader_open_api` SDK oficial.
- Princípio inviolável: trading como problema de estatística + sinal.
  LLM entra como segunda opinião, nunca como raciocinador primário.
