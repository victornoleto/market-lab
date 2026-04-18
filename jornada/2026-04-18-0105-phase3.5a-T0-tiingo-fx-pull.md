# 2026-04-18 0105 — Phase 3.5a Lead T0 [SHORT-HOLD CFD]: Tiingo FX/metals bulk pull

## Verdict
★ DONE — 12 FX tickers baixados daily + 1hour cobrindo 2020-01-01 → 2026-04-17.
Pré-requisito crítico para Leads T1-T5 desbloqueado.

## O que foi feito

**Extensão `scripts/tiingo_bulk_download.py`:**
- Novo arg `--frequency {daily, 1hour}` (default daily). 1hour pula asset_class=index
  automaticamente (Tiingo IEX não cobre índices).
- `FOREX_TICKERS` += `xauusd`, `xagusd` (metais via endpoint FX).
- `run_id` e `summary.json` passam a incluir frequency.

**Fix `src/ai_trade/backtest/data/tiingo_source.py`:**
1. `_build_params(forex, daily)` agora seta `resampleFreq=1day` explícito.
   Sem isso, `/tiingo/fx/<t>/prices` retorna samples irregulares (tick-level),
   não daily. Bug latente que nunca tinha sido exposto — FX nunca foi puxado
   daily até agora.
2. `_http_fetch(forex, 1hour)` agora pagina em chunks de 180 dias. Tiingo FX
   intraday cap-a cada resposta em ~7000 bars (~1 ano 24/5). Sem paginação,
   uma chamada de 6 anos retornava só ~7k bars e silenciosamente parava em
   2021-02-19. Agora emite 13 calls sequenciais por ticker (1s+throttle ~50ms
   ⇒ ~45s por FX 1hour).

**Restrições Tiingo descobertas:**
- FX API exige `startDate >= 2020-01-01` (HTTP 400 pra datas anteriores).
- FX 1hour response cap: ~7000 bars por chamada (motivo de pagination).
- Índices spot (SPX500, NAS100, DE40, UK100, JP225) **não servidos**. Lead T2
  usará ETF proxies já cacheados: SPY/QQQ/DIA. Non-US (DE40/UK100/JP225) fica
  como gap pra broker feed direto em Phase 4.

## Manifest resultante (12 FX tickers)

| ticker  | daily (n_bars) | 1hour (n_bars) | window |
|---------|----------------|----------------|--------|
| eurusd  | 1957           | 38784          | 2020-01-01 → 2026-04-17 |
| gbpusd  | 1957           | 38785          | idem |
| usdjpy  | 1958           | 38820          | idem |
| usdchf  | 1956           | 38719          | idem |
| audusd  | 1957           | 38732          | idem |
| usdcad  | 1957           | 38716          | idem |
| nzdusd  | 1956           | 38706          | idem |
| eurjpy  | 1955           | 38691          | idem |
| eurgbp  | 1953           | 38727          | idem |
| gbpjpy  | 1946           | 38516          | idem |
| xauusd  | 1700           | 32195          | 2020-01-02 → 2026-04-17 |
| xagusd  | 1700           | 32221          | idem |

Smoke check amostral:
- `eurusd 1h`: close [0.95, 1.23], média 1.115 (reasonable pós-2022 crisis + 2023 rebound).
- `xauusd 1h`: [$1519, $5562], média $2397 (matches gold 2020-26 bull run).
- `gbpusd 1h`: [1.04, 1.42] (min coincide com Truss-mini-budget set/2022).

## Constraints de escopo afetados

- **Janela pra FX Leads T1-T4**: 6.3 anos (2020-01 → 2026-04) é o longest disponível via Tiingo
  pago. Inclui COVID crash, 2022 USD-rally/UK-crisis, 2025 dólar-fraco — cobertura regime OK
  mas CURTA comparada com daily SPY/QQQ que temos 25 anos. Precisa levar em conta nos gates
  (WF blocks menores).
- **Citação mandate §3** (Plano A multi-asset obrigatório): universo agora inclui FX majors +
  metais. Índices CFD cobertos via ETFs equity proxies (SPY/QQQ/DIA/IWM 1h já em cache).

## Próximo

Lead T1 — BollingerMR canonical (window=20, σ=2.0) no grid FX daily + 1h (+ metais 1h).
Gate 5-layer + median hold ≤ 5 days. `[bollinger_on_bollinger_bands, p.51-58]`.

## Artefatos

- `scripts/tiingo_bulk_download.py` (modificado — +--frequency, +metais).
- `src/ai_trade/backtest/data/tiingo_source.py` (modificado — resampleFreq forex daily + pagination FX 1h).
- `data/tiingo/bulk_summary_bulk_forex_daily_20260418-0051.json`
- `data/tiingo/bulk_summary_bulk_forex_1hour_20260418-0055.json`
- 12 parquets em `data/tiingo/daily/prices/*.parquet` + 12 em `data/tiingo/1hour/prices/*.parquet`.

Pytest: **709 passed**, baseline preservado.
