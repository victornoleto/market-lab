# A1 [SHORT-HOLD CFD] — Leverage sweep BollingerMR SPY 1h: L=2 único GO, mas abaixo do CDI

**Data:** 2026-04-16 23:10  
**Iteração:** 28 (Phase 3, Lead A1)  
**Status:** PARTIAL-GO — um nível de leverage passou os gates, mas CAGR < 15% CDI.

## O que eu fiz

Rodei o BollingerMR canônico (window=20, σ=2.0, stop_pct=2%, max_hold=24 bars)
em SPY 1h **na janela mais longa do manifest** (2019-08-26 → 2026-04-14,
10 002 barras, ~5,67 anos) com `risk_pct_of_equity ∈ {0.95, 2.0, 5.0, 10.0, 20.0}`
simulando a friction Pepperstone (half-spread $0.02 ≈ 0.4 bps) e
conferindo margem-call via intra-bar scan (bar.low para long, bar.high
para short) + prob-of-ruin via stationary block bootstrap (10k paths,
block 5, horizon = n_trades).

**Gate A1 definido:** final_equity > baseline (L=0.95) **E** max DD ≥ -50 %
**E** prob-of-ruin bootstrap < 5 % **E** sem intra-bar ruin.

## Resultado (tabela fiel à saída do script)

| L     | Sharpe | CAGR     | MaxDD     | FinEq    | Worst IB eq | IB ruin | PoR     | Kelly f* | Verdict |
|-------|-------:|---------:|----------:|---------:|------------:|:-------:|--------:|---------:|:-------:|
| 0.95  | 0.588  | 5.49 %   | -17.16 %  | $1 354   | $951        | no      | 0 %     | 1.000    | NO-GO (baseline) |
| 2.00  | 0.592  | 10.76 %  | -34.11 %  | $1 785   | $895        | no      | 0 %     | 1.000    | **GO**  |
| 5.00  | 0.603  | 19.77 %  | **-69.84 %** | $2 781 | $731       | no      | 0 %     | 0.406    | NO-GO (DD) |
| 10.00 | 0.624  | 9.34 %   | -94.98 %  | $1 659   | $462        | no      | **99.79 %** | 0.035 | NO-GO (PoR) |
| 20.00 | 0.676  | -77.20 % | -100.00 % | $0       | **-$1**    | **YES** | 75.44 % | 0.000    | NO-GO (ruína) |

## Diagnóstico

- **L=2 é o único gate-passing**. Duplicou o CAGR vs 1x (10.76 % vs 5.49 %)
  sem estourar DD ou probabilidade de ruína. Sharpe praticamente igual
  — confirmação de que leverage não cria edge, só escala.
- **L=5 bate a meta CAGR (19.77 %)** mas custa 70 % de DD. Fura o gate
  de preservação de capital. Em live, um 70 % DD quase certamente causa
  deleveraging compulsório antes de recuperar.
- **L=10 colapsa via volatility drag** — FinEq $1 659 é menor que L=5 com
  mais risco. Sharpe sobe (ilusão do numerador médio × σ baixo em path
  sobrevivente), PoR bootstrap 99.79 % diz que quase todo caminho
  possível quebra o floor $0.
- **L=20 ruína real intra-barra** no dia 2020-03-12 (COVID crash): bar.low
  dispara equity < 0 antes do próximo mark-to-close.

## Kelly cross-check

- Kelly binomial da série de trades: `f* = p/L - q/W = 1.000` (clamped).
  Isso acontece porque per-trade returns são pequenos (~0.5 %) com win
  rate > 50 %, então a fórmula dá f* > 1 e saturamos no cap.
- Mapeamento f/2 → L via `f/2 / stop_pct = 0.5 / 0.02 = 25x` é
  **enganoso** — assume distribuição binomial com independência, mas
  BollingerMR tem fat-left-tail via gaps através do stop.
- Empiricamente, o **L ótimo ajustado por gates é L=2**, não o Kelly
  ingênuo. Isso é consistente com `[leverage_space, Vince]`: cada
  estratégia tem f* empírico abaixo do Kelly teórico quando a
  distribuição de retornos é non-normal.

## Verdict Lead A1

**PARTIAL-GO.**

- Leverage 2x **passa todos os gates** mas produz CAGR 10.76 % < meta
  CDI 13–14 % / ano. Fora do mandato de investimento para Strategy A.
- Leverage ≥ 5 bate o CAGR mas fura DD ou PoR. Inviável em live.
- **Conclusão estratégica:** SPY-only BollingerMR não chega ao target
  da Strategy A via leverage sozinha. Precisa de **diversificação
  multi-asset (Lead A2)** pra combinar edges correlacionados baixo e
  elevar o Sharpe ao nível onde L=2–3 entrega 15 %+ CAGR dentro do
  budget de DD.

## Citations

- BollingerMR canônico: `[algo_trading_chan, p.28-30, ch.2]`,
  `[machine_trading, p.204-205, ch.7]`.
- Gate de DD ≤ 50 % como proxy de capital preservation: convenção do
  mandate `[docs/investment-mandate.md §1–5]`.
- Leverage space e curva de ruína: `[leverage_space, Vince]`.
- Kelly binomial pra sizing: `[math_money_mgmt, Vince]`.
- Gayed leverage-preservation floor: `[leverage_for_the_long_run, p.7]`.

## Próximos passos

1. **A1 concluído** — leverage sweep feito, L=2 registrado como o
   único gate-passing. Seguir para B1 (LETF rotation do zero) conforme
   ordem fixa Phase 3.
2. **A2 depois de B1**: multi-asset screener (SPY/QQQ/GLD/BTC/ETH/FX)
   é a peça que pode destravar CAGR ≥ 15 % com L=2 via correlação baixa.
3. Não consumir iters adicionais em SPY-only otimização (marginal).

## Files

- `src/ai_trade/backtest/helpers/leverage.py` (novo) — Kelly, intra-bar
  ruin scan, bootstrap PoR.
- `scripts/run_leverage_sweep_bollinger_mr.py` (novo).
- `tests/test_helpers_leverage.py` (novo, 15 testes).
- `reports/leverage_sweep_A1_spy_1h.json` (artefato).
- Pytest baseline: **360 passed** (345 pré + 15 novos, nenhuma regressão).
