# Lead V2-L5 — Equity pairs cointegration daily (aggregate)

**Phase:** phase3_5a_v2 | **Lead:** V2-L5 | **Status:** DEAD END (0/6 PASS)
**Period:** 2001-05-14 → 2026-04-14 (per-pair, daily Tiingo cache)
**Tested:** 6 pairs × 1 config = 6 runs
**Aggregation iter:** 66

## Summary

V2-L5 testou 6 pares de ETFs líquidos US (setor/índice,
commodity/metal, crédito/duration, ações/bonds) como candidatos a
pairs-trading market-neutral via cointegração Engle-Granger + Kalman
dynamic β + bandas 2σ / exit 0σ / stop 4σ / hold cap 30d, custos
Pepperstone Razor CFD. **Nenhum par passou no gate de cointegração
(ADF p ≤ 0.05)**, portanto nenhum gerou trade e nenhum passou os 5
gates do framework V2. Verdict: **DEAD END**.

A interpretação é consistente com a literatura: em ETFs com grande
volume institucional e arbitragem profissional, qualquer spread
mean-reverting é anulado rapidamente; os spreads observados aqui são
**integrados de ordem 1** (random walks correlacionados),
não estacionários `[algo_trading_chan, p.42-54]`, `[machine_trading_chan, ch.3]`.
A mesma refutação foi feita por Chan (2013) com os mesmos pares
setoriais. O par mais próximo do limite foi **XLF/HYG** (p=0.0746),
mas o β OLS de 2.67 é economicamente anômalo (financial sector ETF
não "segue" high-yield bonds com duplo de sensibilidade) e o ciclo
Fed 2022-2024 (hikes) quebrou paridade (HYG ↓ por duration vs XLF ↑
por NIM expansion). Nenhum par é estruturalmente cointegrado para
todo o histórico disponível.

Esse resultado **confirma V1-T3 (Kalman pair-trade FX 1h)** e
**restringe o espaço de Plano A** a edges de momentum/rotação,
não de relative-value. O universo Pepperstone CFD é blue-chip
global (SPY, QQQ, GLD, SLV, BTC, ETH, majors FX) — não contém
os pares structural/micro-cap onde pairs-trading retém edge
`[algo_trading_chan, p.46]`.

## Cross-ticker table

| Pair    | Window (y) | Bars | ADF stat | ADF p  | OLS β   | Kalman β | Cointegrated | Trades | PASS |
|---------|------------|------|----------|--------|---------|----------|--------------|--------|------|
| GLD_SLV | 20.0       | 5021 | -2.239   | 0.192  | 0.898   | 0.485    | NO           | 0      | NO   |
| QQQ_XLK | 22.6       | 5698 | -1.237   | 0.658  | 1.014   | 0.945    | NO           | 0      | NO   |
| SPY_IWM | 24.9       | 6266 | -2.504   | 0.115  | 1.121   | 0.802    | NO           | 0      | NO   |
| TLT_IEF | 12.3       | 3088 | +0.819   | 0.992  | 1.675   | 1.671    | NO           | 0      | NO   |
| XLE_USO | 20.0       | 5034 | -1.546   | 0.511  | -0.137  | 0.536    | NO           | 0      | NO   |
| XLF_HYG | 12.3       | 3088 | -2.697   | 0.0746 | 2.666   | 1.563    | NO (closest) | 0      | NO   |

Todos os 6 pares falham `oos_sharpe_gt_0`, `fwd_sharpe_gt_0`,
`wf_pass`, `median_hold_ge_3d`, `oos_cagr_ge_30pct`,
`oos_sharpe_ge_2` por ausência de trades (0-trade produz métricas
0.0 em toda janela). Apenas `oos_maxdd_le_25pct` passa
trivialmente. Subset gates: 1/7 em todos.

### Diagnóstico por par

- **GLD_SLV (p=0.192):** clássico "ouro-prata" — correlação alta (ρ > 0.7) mas não cointegrado; silver carrega componente industrial que rompe paridade em ciclos de manufacturing `[algo_trading_chan, p.45]`.
- **QQQ_XLK (p=0.658):** setorial vs. índice — MAG7 concentração pós-2021 dominated o QQQ, quebrando a paridade construída quando XLK era ~25% do QQQ.
- **SPY_IWM (p=0.115):** large-cap vs. small-cap — Russell 2000 descolou pós-2021 por rate sensitivity + small-cap unprofitability.
- **TLT_IEF (p=0.992):** long-duration vs. intermediate-duration Treasuries — rates zero-bound 2014-2021 + Fed hiking 2022-2024 + cuts 2024 introduziram non-stationarity estrutural; β 1.67 consistente com convexity mas spread não-reverte em ciclo completo.
- **XLE_USO (p=0.511):** energy sector vs. oil futures — β OLS -0.137 economicamente absurdo; USO sofre contango drag (roll perdido em futuros) enquanto XLE reflete spot + upstream equity — decoupling estrutural.
- **XLF_HYG (p=0.0746):** financial sector vs. high-yield bonds — closest to threshold mas β 2.67 anômalo; credit-spread sensitivity compartilhada quebrada por rate-duration opposta em 2022-2024.

## Consequência para Plano A V2

- V2-L5 vai para `## Dead ends` em `docs/self_improvement/memory.md`.
- Winner Plano A permanece `gayed_ema100_L2_off_gld` standalone (iter 43 V2-L2 AGGREGATOR PASS — Sharpe OOS 2.285, CAGR 79.14%, MDD -21.02%, median hold 6d).
- `winners_short_hold:` lista 2 entradas — nenhuma alteração desta iter.
- Stop rule do V2 não dispara: já há 1 PASS, restam L6 (vol breakout multi-asset daily) + L7 (verdict final).
- Próxima iter (67) = **V2-L6 bootstrap** (vol breakout — lookback {20, 50, 100} × exit {trailing ATR 3×, opposite channel} × direction {long-only, long/short} = 12 configs × índices+commodities+FI).

## Citations

- `[algo_trading_chan, p.42-54]` — pairs trading em ETFs maduros: edge arbitragem institucional.
- `[machine_trading_chan, ch.3]` — Kalman filter para β dinâmico em pair-trading; ETFs líquidos = casos negativos.
- `[advances_fin_ml, ch.7]` — non-stationarity em séries financeiras; testes ADF requerem amostra suficiente e estacionariedade estrutural.
- `[systematic_trading, p.185-188]` — retail CFD: spread+commission dominantes, trades infrequentes toleradas só se edge claro.

## Links

- Per-ticker reports: `reports/phase3_5a_v2/v2_l5_equity_pairs/*.md`
- Registry: `reports/phase3_5a_v2/v2_l5_equity_pairs/registry.json`
- Jornada: `jornada/2026-04-19-0310-phase3.5a-v2-L5-equity-pairs-DEAD.md`
