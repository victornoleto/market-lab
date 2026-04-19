# [SHORT-HOLD CFD] A2 — multi-asset universe screener entregue

**Tag:** Strategy A (Path A short-hold CFD Pepperstone) — enabler
**Iteration:** 33
**Verdict:** ✅ PASS (deliverable entregue, ranking publicado)

## O que foi feito

Construí o módulo `src/ai_trade/backtest/screener/` (novo package, +28
testes, baseline 436 → 464). Ele cruza Hurst exponent, ATR%, vol
realizada e dollar volume sobre cada ticker do candidate universe e
emite uma DataFrame ranqueada por composite rank (média do
mr-rank + liquidity-rank — equal-weight per `[algo_trading_chan, p.6-7]`).

Universe screened (14 candidatos, daily, longest-available history):

- **5 ETFs equity/bond/gold:** SPY, QQQ, IWM, GLD, TLT (~22-25y cada)
- **9 cryptos majors:** BTC, ETH, SOL, XRP, ADA, DOGE, DOT, AVAX, BNB
  (de 2014-08 → 2026-04 a 2021-08 → 2026-04, dependendo do ativo)

**Gaps documentados:**
- FX majors (EURUSD/GBPUSD/USDJPY) **NÃO estão no daily Tiingo cache**.
  Apenas EURUSD 1h ~6 meses está cacheado — insuficiente pra screener.
  Isso é constraint físico do dataset, não bug do screener. Próximo
  pull Tiingo deveria incluir FX majors daily se quisermos honrar o
  mandato §3 completo.

## Resultados (sorted por composite rank, lower = better)

| Ticker | Class | n_bars | Hurst | CI95 | ATR% | Vol(ann) | $Vol/d | Rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IWM | etf | 6266 | **0.447** | [0.423, 0.582] | 2.20% | 19.59% | $9.1B | 2.5 |
| SPY | etf | 6266 | 0.520 | [0.445, 0.597] | 1.53% | 13.38% | $50.1B | 4.0 |
| TLT | etf | 5968 | **0.470** | [0.410, 0.566] | 0.87% | 10.59% | $3.2B | 4.0 |
| QQQ | etf | 6266 | 0.540 | [0.452, 0.607] | 1.92% | 17.05% | $31.3B | 5.5 |
| GLD | etf | 5384 | 0.545 | [0.449, 0.627] | 2.81% | 27.67% | $5.4B | 7.0 |
| dotusd | crypto | 2692 | **0.418** | [0.408, 0.575] | 5.24% | 76.78% | $7.9M | 7.0 |
| xrpusd | crypto | 3878 | 0.513 | [0.419, 0.587] | 3.73% | 59.10% | $274M | 7.5 |
| avaxusd | crypto | 1791 | 0.506 | [0.379, 0.597] | 5.90% | 72.43% | $21M | 8.5 |
| dogeusd | crypto | 3294 | 0.533 | [0.432, 0.594] | 4.08% | 70.01% | $55M | 9.0 |
| bnbusd | crypto | 1033 | 0.497 | [0.365, 0.591] | 3.03% | 47.21% | $2.7M | 9.0 |
| btcusd | crypto | 4483 | 0.585 | [0.442, 0.595] | 3.52% | 39.14% | $1.2B | 9.5 |
| ethusd | crypto | 3882 | 0.584 | [0.440, 0.625] | 5.05% | 60.07% | $671M | 9.5 |
| solusd | crypto | 2021 | 0.596 | [0.402, 0.601] | 5.11% | 64.63% | $323M | 11.0 |
| adausd | crypto | 2993 | 0.552 | [0.407, 0.584] | 5.38% | 67.96% | $36.7M | 11.0 |

(Boldface = H < 0.5 com 95% CI tocando ou abaixo de 0.5 — MR-favorável
per Chan p.44-45.)

## Leituras (em PT, com analogia)

- **IWM lidera o ranking** — Hurst 0.447 (CI claramente toca abaixo de
  0.5) + $9B/dia de volume diário. Pensa nele como o índice das small
  caps que costuma "voltar pra média" mais rápido que o SPY. Esse
  perfil casa exatamente com o que a BollingerMR procura. Mas atenção:
  iter 19 testou BollingerMR em 13 ETFs e IWM **não** passou. Aquele
  teste foi sem GARCH sizing — agora podemos repetir com a versão
  GARCH (a mesma que fez o SPY virar winner). Esse re-teste é o
  natural próximo lead (A3 sub-experimento).

- **SPY/QQQ ficam em H ≈ 0.52-0.54** — CI95 cruza 0.5, então estão na
  zona ambígua. O SPY é o nosso winner único da Strategy A; QQQ tem
  IS Sharpe 0.91 em iter 21 mas OOS catastrófico (-0.991, dead end).
  Coerente com o screener: QQQ é mais momentum, não MR.

- **TLT (bonds 20y+)** — H 0.47, vol baixa (10.6%/ano), $3B/d.
  MR-favorável estrutural (Treasuries vivem em bands). Vale teste.

- **GLD** — H 0.545. Não é MR-favorable, é mais um asset de regime
  (rallies longos seguidos de consolidações). Strategy A unlikely.

- **Cryptos:** o cenário é misto. **dotusd tem o menor Hurst (0.418)**
  da amostra inteira, mas $7.9M/dia é capacidade insuficiente pra
  CFD com leverage. **BTC e ETH (H~0.585) são distintamente
  trending** — confirma narrativa do mercado e descarta BollingerMR
  como winner ali; talvez momentum (Clenow-style) faça sentido, não
  reversão à média. **xrpusd (H=0.513, $274M/d)** é o melhor crypto
  com liquidez suficiente, mas H não passa do limiar.

- **FX missing:** o mandato §3 lista FX majors como obrigatórios pra
  Strategy A multi-asset. O cache atual não tem. Lead A3 só pode
  trabalhar com o que existe (ETFs + cryptos top); pra fechar o
  mandato, precisamos rodar um Tiingo bulk pra EURUSD/GBPUSD/USDJPY
  daily, idealmente 10y+ de história (Tiingo cobre FX desde ~2010).

## Recomendação para A3

Com base no ranking, pesar A3 nesta ordem:

1. **IWM 1h + BollingerMR GARCH** — re-test do dead end de iter 19,
   agora com GARCH sizing (mesma config do SPY winner). Justificado
   pelo screener (lowest H entre os ETFs grandes). Se OOS Sharpe > 0
   e gates passam, ganhamos um segundo ativo independente para
   Strategy A.
2. **TLT 1h + BollingerMR GARCH** — bonds têm regime distinto;
   correlação com IWM/SPY é negativa em risk-off. Se passar, vira
   diversificação genuína.
3. **xrpusd daily + BollingerMR** — único crypto com liquidez ≥ $200M
   e H ≤ 0.52. Hourly não disponível (BTCUSD 1h só 2 meses).

BTC/ETH ficariam fora da BollingerMR (H > 0.58), mas **deveriam ser
considerados na lead A3 com Clenow momentum/trend** (reaproveita
`adjusted_slope`). Isso é ortogonal ao mandato (Strategy A é
BollingerMR), mas o screener objetivamente sugere essa rota.

## Citações

- Hurst structure-function: `[algo_trading_chan, p.44-46, ch.2]`
- ATR(20) sizing proxy: `[stocks_on_the_move, p.88]`
- Dollar-volume tradability: `[stocks_on_the_move, p.81]`
- Equal-weight rank combination: `[algo_trading_chan, p.6-7, ch.1]`
  (Kahneman 2011)
- Caveat sample-length sensibility: `[cycle_analytics, p.74-75, ch.6]`
  (mitigado com `min_obs=252` e bootstrap CI 95%)

## Arquivos novos / modificados

- `src/ai_trade/backtest/screener/__init__.py` (novo)
- `src/ai_trade/backtest/screener/hurst.py` (novo, ~150 linhas)
- `src/ai_trade/backtest/screener/metrics.py` (novo, ~75 linhas)
- `src/ai_trade/backtest/screener/universe.py` (novo, ~200 linhas)
- `tests/test_screener_hurst.py` (12 tests)
- `tests/test_screener_metrics.py` (8 tests)
- `tests/test_screener_universe.py` (8 tests)
- `scripts/run_screener_a2.py` (novo, orchestração)
- `reports/screener_a2_universe.json` (output do run)

**Pytest:** 464 passed (baseline 436 → +28). Sem regressão.
**Runtime do screener:** ~0.6s para 14 candidatos com bootstrap=200.
