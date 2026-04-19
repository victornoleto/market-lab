# [SHORT-HOLD CFD] Phase 3.5a — T4 Session-based FX: 0/6 PASS, DEAD

**Data:** 2026-04-18 ~15:00 BRT
**Path:** A (Pepperstone CFD, short-hold ≤ 5 dias)
**Phase:** 3.5a — investigação Plano A
**Verdict:** DEAD END. 4º lead consecutivo sem winner em FX 1h.

---

## TL;DR

Sweep T4 fan-out fechou: 6 FX majors (EURUSD, GBPUSD, EURGBP, USDCAD,
USDJPY, AUDUSD) × 3 estratégias de sessão (London ORB on Asian range;
NY-close MR; Asian-range fade on NY range) em 1h sobre janela Tiingo
2020-01-06 → 2026-04-14 (~6.3 anos). **Zero tickers passaram os 5
gates** (PBO/DSR/WF/OOS/FWD + hold ≤ 5 d).

Padrão por família:

- **London ORB** (trend/breakout): catastrófico e uniforme. OOS
  Sharpe −3.13 (USDJPY) a −9.31 (EURGBP), CAGR −21% a −31%, MDD
  −40% a −54%, **470–575 trades/ano**. Não é hold-time — é trade
  **count**: cada round-trip come ≥5–7 bps de spread + commission +
  fill, e o alpha bruto por trade não supera esse piso.
- **NY-close MR** (banda 0.2×24h-range): degenerado. Gera **0–9
  trades OOS em 2 anos** no universo inteiro. Os dois Sharpes OOS
  "positivos" — AUDUSD +0.75 (1 trade) e USDJPY +0.27 (3 trades)
  — são ruído puro: amostra pequena demais para DSR, WF indecidível,
  e FWD vem com 0 trades nos dois.
- **Asian-range fade** (fade da range NY na janela asiática): todo
  mundo negativo. OOS Sharpe −2.93 a −4.95, CAGR −5% a −13%, 210–405
  trades. Hold mediano 0.29 d, então o custo relativo por trade é
  pior ainda do que o ORB.

## Cross-ticker (best config por ticker, todos fail)

| Ticker | Best config    | Sharpe OOS | CAGR OOS % | MDD OOS % | Trades | Hold (d) | PASS |
|--------|----------------|-----------:|-----------:|----------:|-------:|---------:|:----:|
| AUDUSD | ny_close_mr_1h |      +0.75 |      +0.21 |     −0.13 |      1 |     0.46 |  ✗   |
| USDJPY | ny_close_mr_1h |      +0.27 |      +0.18 |     −0.75 |      3 |     0.46 |  ✗   |
| EURGBP | ny_close_mr_1h |       0.00 |       0.00 |      0.00 |      0 |     0.00 |  ✗   |
| USDCAD | ny_close_mr_1h |      −0.50 |      −0.28 |     −0.98 |      9 |     0.46 |  ✗   |
| GBPUSD | ny_close_mr_1h |      −0.74 |      −0.18 |     −0.50 |      2 |     0.33 |  ✗   |
| EURUSD | ny_close_mr_1h |      −0.83 |      −0.10 |     −0.24 |      2 |     0.46 |  ✗   |

Detalhes completos em `reports/phase3_5a/t4_session_based_fx/AGGREGATE.md`
e nos 6 `<ticker>.md` / `.json` por ticker.

## Diagnóstico

A tese de "sessões deixam skew exploitable" tem assinatura no retorno
bruto, mas o **gross edge por trade (~3–8 bps) fica abaixo da friction
Razor (~5–10 bps round-trip)**. Qualquer configuração que reduza
trade count o bastante para escapar da friction (banda mais estreita
ou stop-loss mais apertado) degenera em 0–9 trades/ano — sem robustez
estatística. Qualquer configuração que produza amostra passa a ser
dominada pelo custo.

T4 junta T1 (BollingerMR 0/36), T2 (Donchian 0/12) e T3 (pairs
statarb 0/6) como **4º lead consecutivo sem winner em FX 1h**. 72
runs (36 + 12 + 6 + 18) em 4 famílias distintas, todos cost-eaten.

Lição recorrente: **FX 1h com Razor-tier não é onde vive o edge do
Plano A**. Próximas tentativas precisam ou (a) mudar frequência
(recusada pelo mandate — only `1hour`/`daily` no Tiingo whitelist),
ou (b) mudar universo (índices/commodities/crypto), ou (c) mudar
estrutura (regime filter para comprimir trade count sem perder
amostra).

## Citações

- `[quant_trading_chan, p.43-53, ch.2-3]` — parsimônia FX intraday;
  limite de quão estreita uma banda de sessão pode ser antes de o
  Sharpe perder significado.
- `[trading_systems_methods, p.353]` — base Donchian/breakout.
- `[trading_systems_methods, p.326-329]` — mecânica de range-fade.
- `[volatility_trading]` — ATR filter + Chandelier exit.
- `[systematic_trading, p.185-188]` — disciplina de hold-time
  (respeitada aqui ≤ 24 h intra-sessão).
- `[advances_fin_ml, ch.7]` — PBO cross-config por ticker.

## Próximo passo

**Lead T5** (regime-filter hybrid) — sobrepor VIX/DXY filter sobre
BollingerMR SPY 1h existente; hipótese: filtragem reduz trade count
sem matar amostra (não é "banda mais estreita" — é "menos
oportunidades mas cada uma melhor"). Se T5 também falhar, ir direto
para T6 (rebalance da meta Plano A com override §7 do mandate — o
projeto pode precisar aceitar que Plano A não supera Plano B sob
custos Pepperstone reais).

## Pointers

- Registry: `reports/phase3_5a/t4_session_based_fx/registry.json`
- Aggregate: `reports/phase3_5a/t4_session_based_fx/AGGREGATE.md`
- Per-ticker MDs: `reports/phase3_5a/t4_session_based_fx/*.md`
- Iter counter: 32 (6 sweep iters 26–31 + aggregator 32)
- Pytest baseline: 757 passed (sem regressão, zero código tocado)
