# Kalman pairs SPY-IWM 1h: segundo PASS no cofre (mas mais fraco)

**Data:** 2026-04-16 00:45
**Contexto:** Iter 12 do loop de self-improvement — lead #1 da fila.

## O que foi feito

Implementei a variante **adaptiva** do par trader do Chan [algo_trading_chan,
p.76-80, ch.3]: ao invés de um β fixo estimado por OLS numa janela de
treino (como o `ChanBollingerPairsStrategy` faz), o hedge ratio
`[α_t, β_t]` evolui a cada barra via Kalman filter:

- Estado `x_t = [α_t, β_t]`, transição `x_t = x_{t-1} + w_t`,
  `w_t ~ N(0, Q)` com `Q = δ·I` (δ = ruído de processo).
- Observação `y_t = [1, x_obs_t] · x_t + ν_t`, `ν_t ~ N(0, R)`.
- Sinal de entrada: **inovação padronizada** `z_t = e_t / √S_t`.

Grid parsimonioso (N=4 para não degradar DSR):
- `δ ∈ (1e-5, 1e-4)`
- `entry_z ∈ (1.0, 1.5)`

## Resultado — 2° Winner do cofre

**SPY-IWM 1h, 2021-2025:**

| Gate | Valor | Verdict |
|---|---|---|
| PBO | 0.433 | ✅ < 0.5 |
| DSR (best cfg) | p=0.0136 | ✅ < 0.05 |
| Walk-forward | 7/8 windows profitable | ✅ ≥ 6/8 |

**Best config #1:** δ=1e-5, entry_z=1.5.

- Sharpe anual: **0.550**
- CAGR: 0.41%
- MaxDD: 2.17%
- 249 pair trades em ~5 anos
- WR=68.3%, PF=1.88
- **Hold mediano = 5h, p90=25h** → dentro do gate de swap Pepperstone.

## Interpretação

✅ **Passa todos os 3 gates** — a segunda estratégia no cofre. [SHORT-HOLD CFD]
compatível: mediana < 1 dia.

⚠️ **Sharpe é MUITO menor** que o Bollinger MR (0.55 vs 1.314). O Bollinger
continua sendo o candidato principal pra deploy. Esse Kalman é útil por
**diversificação**: família diferente (spread par vs single-asset MR),
pode ser combinado em portfolio.

⚠️ **CAGR baixo (0.41%/ano)** — o spread SPY-IWM é estreito, MaxDD 2.17%
indica que a estratégia está sub-alavancada. Poderia aumentar
`risk_pct_of_equity` além dos 95% canônicos, mas isso introduziria outro
grau de liberdade pro grid e potencialmente degradaria os gates.

⚠️ **Diferença vs Chan canônico:** Chan p.76 usa o par oil ETFs (EWA/EWC).
Usei SPY-IWM porque: (i) Tiingo 1h disponível pra ambos; (ii) ambos
ETFs líquidos; (iii) economicamente relacionados via beta-to-market mas
com premium small-cap. β médio convergiu perto de 0.4 (IWM ≈ 40% da
variação de SPY).

## Comparação com o Chan canônico (static OLS)

Esse teste também valida indiretamente por que o `ChanBollingerPairsStrategy`
**GLD-SLV** falhou (lead deprecated): não era só o par — o ajuste adaptivo
faz a diferença. Kalman permite que β se ajuste a regime-changes (ex.:
2022 com subida de juros quebrou várias cointegracções estáticas).

## Próximos passos

- **Não** aumenta o best_verdict (Bollinger mantém Sharpe 1.314 > 0.55).
- **Incrementa** o contador de cofre: 2/10 winners.
- **Próximo lead:** Bollinger MR 1h BTCUSD — mercado 24/7, microestrutura
  diferente, mesma família da winner #1.
- **Ideia futura:** combinar Bollinger MR SPY (winner #1) + Kalman pairs
  SPY-IWM em portfolio — baixa correlação esperada (MR single-asset vs
  spread relative-value).

## Commits / arquivos

- `src/ai_trade/backtest/strategies/kalman_pairs.py` (329 linhas)
- `src/ai_trade/backtest/grid/kalman_pairs_config.py`
- `tests/test_kalman_pairs.py` (9 tests)
- `scripts/run_grid_kalman_pairs.py`
- Report: `reports/grid_kalman_pairs_20260416-0041/summary.md`

501 tests green (492 antes + 9 Kalman). Não quebrou baseline.
