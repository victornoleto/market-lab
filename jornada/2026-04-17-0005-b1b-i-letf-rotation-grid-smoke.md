# B1b-i — Grid runner LETF rotation + smoke run (16 configs, SPY proxy)

**Tag:** [SWING BROKER] | **Phase 3 lead:** B1b-i | **Status:** DONE
(infra) — não é verdict; gates pendentes.

## O que foi feito

Iteration 30 entregou a infra-estrutura do grid para a **LETF rotation**
(Gayed LRS, Strategy B / Path B swing broker BR):

1. `src/ai_trade/backtest/grid/letf_rotation_grid.py` — expande eixos
   (filter × lookback × band × leverage × gold_weight), roda cada
   config em cada split, coleta métricas por célula (Sharpe, CAGR,
   MaxDD, switches, custos, taxa).
2. `scripts/run_grid_letf_rotation.py` — CLI que carrega SPY (proxy
   SPX TR) e opcionalmente GLD do cache Tiingo, expande o grid
   (smoke 16 ou full 360), e escreve JSON report.
3. `tests/test_letf_rotation_grid.py` — 15 testes unitários cobrindo
   expansão de grid, slicing, validação de inputs, round-trip dict.

Pytest total: **411 passed** (baseline 345 mantido; +15 desta iter,
+51 acumulados desde início Phase 3).

## Smoke signal (NÃO é winner)

Grid 16 configs × 3 splits sobre SPY daily 2005-2026, custos 15 bps
round-trip + taxa BR 15% + expense ratio 1%:

```
Top 5 por OOS Sharpe:
filter lb  band  lev gw  IS    OOS    Stress  OOS_CAGR  OOS_MDD  n_sw
EMA   125 0.00  3x  0   1.691 1.942  1.785   66.9%    -26.0%   62
EMA   125 0.00  2x  0   1.646 1.885  1.730   40.5%    -18.5%   62
SMA   125 0.00  3x  0   1.704 1.830  1.729   60.8%    -26.0%   72
SMA   125 0.00  2x  0   1.657 1.770  1.676   37.0%    -18.5%   72
EMA   200 0.00  3x  0   1.519 1.360  1.498   44.3%    -28.9%   31
```

Sharpes consistentes ≥1.3 em todos os 3 splits. Lookback 125 domina
lookback 200, band 0% domina 5%, EMA ≥ SMA. Alinhado
qualitativamente com `[leverage_for_the_long_run, p.14, Table 6]`
(todos os MAs 10-200 têm Sharpe positivo; curtos ligeiramente melhor).

## Caveats (por que NÃO é winner ainda)

1. **Splits são de conveniência**, não canônicos. Mandate pede IS
   1970-2000 / OOS 2001-2015 / Stress 2016-2026; o Tiingo cache só
   começa em 2001-05-14. Este smoke usou IS 2005-2013 / OOS
   2014-2019 / Stress 2020-2026 — janela pós-GFC, viés pro-bull
   market.
2. **SPY é proxy do SPX TR**, não o SPX TR oficial. Dividendos estão
   incluídos (`adj_close`), mas pré-2001 não existe.
3. **Gates não foram rodados.** PBO precisa de CPCV (Lead B1c), DSR
   precisa de PSR com trial-adjusted benchmark, WF precisa de walk-
   forward rolante. Sem esses 3, "Sharpe alto" não vale verdict.
4. **Gold não incluído** no smoke. Configs com `gold_weight > 0`
   só rodam com GLD (2004+); ativar via `--include-gold` no próximo
   iter.

## Custos reais modelados

Por switch ON↔OFF: 15 bps (10 comm + 5 spread) + se saída ON→OFF com
ganho, 15% BR IR sobre o ganho realizado. Expense ratio 1%/252 por
dia em ON. Cash rate 0% (Gayed canonical, `[p.21]`). Sem swap (Path B
é swing broker, não CFD).

## Decisões técnicas novas

- Grid runner próprio (não reusa `GridRunner` generic) porque LRS é
  return-series simulator, não bar-engine. Design alinhado com B1a
  [p.13, p.21].
- Eixos `GridAxes` frozen dataclass — smoke (16) vs full (360) é só
  passar axes diferentes, mesmo pipeline.
- 360 configs do mandate = 2×4×3×3×5. Smoke 16 = 2×2×2×2×1.

## Próximo (B1b-ii)

Adicionar loader SPX TR pré-2001 via Shiller ou Ken French (daily
factor CRSP-weighted com dividendos reinvestidos). Re-rodar grid 360
com splits canônicos Gayed 1970-2000 / 2001-2015 / 2016-2026. Depois
B1c = CPCV + PBO + stationary block bootstrap + veredito PASS/FAIL.

## Artefatos

- `reports/letf_rotation_grid_smoke.json` (16 trials, 48 cells)
- 3 arquivos de código novos (grid module + CLI + tests)

## Citações

- `[leverage_for_the_long_run, p.13]` — LRS signal SMA 200, above→ON.
- `[leverage_for_the_long_run, p.14, Table 6]` — todos MAs 10-200
  positivos; alinha com smoke (lb 125 ≥ 200).
- `[leverage_for_the_long_run, p.17, Table 8]` — leverage 1.25/2/3
  todos testados no paper.
- `[leverage_for_the_long_run, p.21]` — ETF implementation usa cash.
- `[advances_fin_ml, p.208-211]` — split-leakage: splits mutuamente
  exclusivos são condição necessária pra PBO válido (rodará em B1c).
