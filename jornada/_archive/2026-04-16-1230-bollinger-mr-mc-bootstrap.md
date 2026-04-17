# MC bootstrap dos winners — bandas honestas em torno do Sharpe

> ⚠️ **RETRACTED 2026-04-16 12:45.** As CIs aqui foram computadas em
> trade returns de cache contaminada. As bandas de Sharpe/CAGR/MaxDD
> portanto são em torno de pontos artificiais. A infra de bootstrap
> (`stationary_bootstrap_trades`) e o módulo de teste permanecem válidos
> e reusáveis — só o exercício específico de SPY/XLK/XLE 2025-2026Q1
> precisa re-rodar com dados limpos depois que algum strategy passe o
> gate. Veja [2026-04-16-1245-data-bug-winners-retracted.md](2026-04-16-1245-data-bug-winners-retracted.md).


**Verdict resumido:** ✅ Os 3 winners passam o critério "lower bound do
Sharpe OOS CI95 > 0", mas **com folga muito desigual**. XLK é o mais
robusto (lower bound 0.601), SPY o mais frágil (0.031, basicamente
encostado em zero), XLE no meio (0.239). O ponto-estimativa do report
único masking essa heterogeneidade.

---

## Por que rodamos isto

Task 1A do plan `2026-04-16-winners-deep-validation.md`. Os reports
anteriores (iter 5/15/16 da self-improve loop) entregam um único
número — Sharpe = X — mas não dizem **com que confiança esse X reflete
edge real vs sorte da janela amostrada**. Stationary bootstrap dá uma
distribuição empírica dessa estatística, e dela um CI 95%.

Critério de "edge real": lower bound do CI > 0 (ainda não-deflado por
DSR — esse é o gate seguinte; se nem o pre-deflation passa, parar).

## O que foi feito

1. Adicionei `--emit-trades` ao `scripts/run_oos_bollinger_mr.py` —
   escreve CSV `period,symbol,side,volume,entry_time,exit_time,entry_price,exit_price,pnl`.
2. Implementei `src/ai_trade/backtest/validation/bootstrap.py` —
   `stationary_bootstrap_trades(...)` Politis-Romano (geometric block
   length, mean=5). 12 testes unitários cobrindo IID extremo
   (block=1), block longo (preserva ordem), unbiased mean, edge cases
   (empty/non-1d/single-trade).
3. Criei `scripts/run_mc_bootstrap_bollinger_mr.py` — lê CSVs, computa
   Sharpe/CAGR/MaxDD por resample (n=10000, seed=42), produz
   `*_ci.json`, `summary.md`, histogramas.
4. Rodei OOS contínuo `2025-01-01 → 2026-04-15` (15 meses) para SPY,
   XLK, XLE — train (2021-2024) emitido na mesma rodada para baseline.

**Decisão de modelagem:** bootstrap em **per-trade returns** baseados
em preço (`(exit-entry)/entry`, signed por side), não em PnL bruto.
Razão: o strategy compounds equity 800× ao longo de 4 anos com
`risk_pct=0.95`, o que faz cada PnL absoluto depender do equity
acumulado. Bootstrap de PnL como se fosse IID em dólares produziu CIs
de drawdown impossíveis (-4120%). Returns price-based são
equity-history-independent. Sharpe é leverage-invariant (risk_pct
cancela em mean/std); CAGR/MaxDD compoundam ao risk_pct correto.

## Resultados (95% CI por bootstrap, n=10000)

### OOS contínuo 2025-01-01 → 2026-04-15

| Ticker | N | Years | Sharpe (point) | Sharpe CI95 | CAGR (point) | CAGR CI95 | MaxDD (point) | MaxDD CI95 |
|---|---|---|---|---|---|---|---|---|
| SPY | 59 | 1.26 | 1.404 | **[0.031, 3.280]** | 16.74% | [-0.36%, 36.02%] | -11.16% | [-15.47%, -2.53%] |
| XLK | 59 | 1.24 | 1.586 | **[0.601, 2.345]** | 400.54% | [7.41%, 2602.08%] | -13.40% | [-20.99%, -4.96%] |
| XLE | 50 | 1.21 | 1.075 | **[0.239, 2.897]** | 106.99% | [2.44%, 568.84%] | -10.41% | [-18.27%, -3.04%] |

### Train 2021-2024 baseline

| Ticker | N | Years | Sharpe (point) | Sharpe CI95 | CAGR (point) | CAGR CI95 | MaxDD (point) | MaxDD CI95 |
|---|---|---|---|---|---|---|---|---|
| SPY | 158 | 3.95 | 1.310 | [0.489, 2.206] | 14.67% | [5.02%, 24.80%] | -12.18% | [-17.22%, -4.44%] |
| XLK | 173 | 3.95 | 1.858 | [1.313, 2.350] | 793.60% | [207.27%, 2838.48%] | -13.85% | [-18.35%, -6.22%] |
| XLE | 165 | 3.92 | 1.547 | [1.026, 1.990] | 469.11% | [118.21%, 1524.90%] | -16.16% | [-30.67%, -11.07%] |

## O que isso muda na narrativa

1. **Ordem de robustez:** XLK > XLE > SPY (oposto do que a tabela de
   point estimates sugere — SPY iter 5+16 vinha sendo "winner #2" mas é
   o mais frágil em CI). XLK é não só o melhor ponto-estimativa mas
   também o com lower bound mais alto. Foi o vencedor por mérito.
2. **SPY OOS é frágil estatisticamente.** Lower bound 0.031 quer dizer
   que se o "verdadeiro" edge SPY fosse Sharpe ~0.0, o que observamos
   teria probabilidade ~2.5% sob bootstrap. Não é zero, mas é o gate
   mínimo. Se DSR aplicar deflation, SPY pode falhar.
3. **CAGR ranges são gigantes.** XLK train CAGR CI [207%, 2838%] não é
   "estratégia ruim" — é o efeito de comporção a 95% do equity em
   ~170 trades alavancados. **Confirma a intuição do user de que
   risk_pct=0.95 é absurdo para live.** É exatamente isto que o Task
   1C vai dimensionar: que CAGR (e MaxDD) realista a 0.20-0.50 entrega.
4. **Train tem CI mais apertado que OOS** — e isso é simplesmente
   tamanho de amostra. SPY train n=158 vs OOS n=59 ⇒ raiz(158/59) ≈ 1.6×
   CI mais apertado no train. Não tem nada a ver com edge — é
   estatística básica. Aviso para não subestimar incerteza só porque
   "o histórico é grande".
5. **MaxDD é a métrica mais robusta.** Bandas relativamente apertadas
   em todos os 6 cenários (train+OOS × 3 tickers), entre -3% e -30%.
   Nada "blow-up implícito" no bootstrap.

## Citações

- `[advances_fin_ml, p.196-202, ch.11]` — bootstrap CI para Sharpe;
  por que single-point Sharpe é insuficiente quando há autocorrelação.
- Politis & Romano (1994) "The stationary bootstrap" — Journal of the
  American Statistical Association, 89(428): 1303-1313 — algoritmo
  fonte. Não está no knowledge base como livro absorvido; AFML cita.

## Arquivos

- `src/ai_trade/backtest/validation/bootstrap.py` — Politis-Romano
- `scripts/run_oos_bollinger_mr.py` — `+--emit-trades --trades-out`
- `scripts/run_mc_bootstrap_bollinger_mr.py` — bootstrap + report
- `tests/test_bootstrap.py` — 12 testes
- `reports/bollinger_mr_trades/{SPY,XLK,XLE}_2025-01-01_2026-04-15.csv`
- `reports/bollinger_mr_mc_bootstrap/{spy,xlk,xle}_ci.json`
- `reports/bollinger_mr_mc_bootstrap/summary.md`
- `reports/bollinger_mr_mc_bootstrap/assets/sharpe_hist_{spy,xlk,xle}.png`

## Próximos passos

Plan original: 1A → 1B (overlap) → 1D (regime) → 1E (long-history) →
1C (sizing) → ... → 1G (verdict).

A descoberta de que SPY OOS lower bound é 0.031 não muda a ordem mas
**aumenta a importância do Task 1B (overlap)**: se SPY/XLK/XLE são
correlacionados (porventura SPY leva XLK leva XLE no mesmo dia),
"3 winners" pode ser na prática 1.5 winners. E como SPY é o mais
frágil, eliminá-lo não muda muito se XLK transporta o edge.

Total tests: **501 → 515 verdes** (+12 bootstrap, +2 do fix do audit
do commit anterior).
