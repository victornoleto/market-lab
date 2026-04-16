# Stress-test Bollinger MR winners no forward-window 2026-Q1

> ⚠️ **RETRACTED 2026-04-16 12:45.** Cache 1h continha placeholder bars
> em US holidays (Q1-2026 inclui MLK Day, Presidents' Day, Good Friday).
> XLK/SPY/XLE Sharpes Q1-26 reportados (2.341 / 2.585 / 1.879) eram
> dominados por trades fake nesses dias. EEM demoção stand-alone permanece
> (EEM real edge ainda fraco). Veja
> [2026-04-16-1245-data-bug-winners-retracted.md](2026-04-16-1245-data-bug-winners-retracted.md).

**Data:** 2026-04-16, iter 16 do self-improvement loop.
**Motivação (lead #8 da memória):** validar os 4 winners Bollinger MR 1h
num período futuro (2026-Q1) que ficou fora tanto do grid (2021-2024)
quanto do OOS já rodado (2025). Serve como filtro adicional antes de
carimbar a família como "production-grade".

## Protocolo

- Script: `scripts/run_oos_bollinger_mr.py`.
- Config congelado: `window=20, std=1.5, stop=0.02, max_hold=24`.
- Janela OOS: **2026-01-01 → 2026-04-15** (444 barras 1h, ~3.5 meses).
- Comparação: mesmo config rodado em 2021-2024 (train) como baseline.
- Critério simples (complementa os 3 gates do framework): Sharpe > 0.5,
  profitable, MaxDD > -25%.

## Resultado por símbolo

| Símbolo | Train Sharpe | Q1 Sharpe | Decay | WR | Trades | Veredito |
|---------|-------------:|----------:|------:|---:|-------:|---------|
| XLK     | 1.893        | **2.341** | +23.7% | 76.5% | 17 | ★ PASS |
| SPY     | 1.293        | **2.585** | +99.9% | 73.3% | 15 | ★ PASS |
| XLE     | 1.584        | **1.879** | +18.7% | 75.0% | 8  | ★ PASS |
| EEM     | 1.311        | **-0.991**| -175.6%| 55.6%| 9  | ✗ FAIL |

## Interpretação

**Três winners resistem ao forward-test e fica ainda melhor:** XLK, SPY e
XLE apresentam Sharpes 2026-Q1 *acima* do treino — win-rate sobe, MaxDD
cai. Consistência impressionante pro mesmo config em 3 ETFs de perfis
diferentes (tech, índice amplo, energia).

**EEM quebra com sinal inequívoco:** Sharpe passa de +1.311 (train) e
+1.198 (OOS 2025) para **-0.991** em Q1 2026. Win-rate cai de 65.8% →
55.6%. Profit factor vira contra. Mesmo com n=9 trades pequeno, o
direcional é claro e sai fora da banda ruidosa.

**Padrão déjà-vu do Kalman Pairs (iter 13):** passa os 3 gates, passa o
hold-out 2025, mas quebra num período mais novo. Reforça a regra
adicionada após iter 13: **três gates + hold-out 2025 ainda são
necessários mas não suficientes**. Stress-test forward-window vira mais
uma peneira obrigatória.

**Hipótese sobre EEM:** emerging markets podem estar em regime novo em
2026 Q1 (dólar, política monetária global, eventos geopolíticos).
Mean-reversion em ETF de emergentes depende de mercado "ranging";
se 2026-Q1 entrou em trend ou voltou agressiva, a estratégia machuca.
Requer investigação dedicada se EEM for reativado algum dia.

## Caveat de sample size

444 barras ≈ 3.5 meses, 8-17 trades por símbolo. Poder estatístico
baixo pra Sharpe sozinho. Mas:
- Os 3 que passaram passaram com folga e WR alto.
- EEM falhou com WR abaixo de 60% e Sharpe -1.0 — isso é distingui de
  ruído mesmo com n=9.
- Decisão: tratar EEM como **"watch / demoted"**, não como "definitivamente
  quebrado". Revalidar quando 2026-Q2 fechar.

## Mudanças de estado

- **Winner count:** 4/10 → **3/10** (EEM demovido).
- **Production-grade portfolio (Bollinger MR 1h w=20/std=1.5/stop=0.02/max_hold=24):**
  - XLK (tech)
  - SPY (S&P500 amplo)
  - XLE (energia)
- **Lead #8 consumido** (stress-test XLK cumprido; expandiu natural pro
  resto da família).

## Citações

- Config parameters: `[algo_trading_chan, p.28-30, ch.2]`.
- Walk-forward / OOS protocol: `[advances_fin_ml, p.208-211, ch.12]`.
- Hold-out discipline (single-block): `[evidence_based_ta, p.239-244, ch.7]`.
