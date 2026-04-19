# V2-L1 TSMOM lb=1m: calendário semanal consertado, 2 configs processados — [SHORT-HOLD CFD]

**Fase:** 3.5a-V2 (LAST attempt Plano A) · **Lead:** V2-L1 TSMOM multi-asset daily · **Iter:** 3

## O que aconteceu

Primeira rodada do sweep V2-L1 foi **lookback=1m × vol-target=10%** sobre
um universo de 30 instrumentos (26 ETFs + BTCUSD + 3 pares FX majors).
A primeira execução saiu suspeita: métricas OOS e FWD com Sharpe **zero**
a partir de 2014. Diagnóstico mostrou que o portfólio literalmente
congelava depois daquela data.

Causa raiz: o calendário mestre da simulação era a união dos índices
nativos de todos os 30 ativos. Como o BTCUSD tem barras de fim-de-semana
e os ETFs não, o `shift(lookback_days=21)` em uma série de ETF, calculado
em cima do índice união, "pulava" para uma barra de sábado/domingo com
`NaN` — logo `past_return` virava NaN para todos os 26 ETFs de uma vez,
o sinal TSMOM nunca disparava, e o portfólio ficava flat.

Correção: master calendar agora filtrado para dias úteis
(`idx[idx.dayofweek < 5]`) em `src/ai_trade/backtest/strategies/tsmom_multi_asset.py`.
Retorno do BTCUSD numa segunda agora representa Sex→Seg (convenção
multi-asset daily padrão `[systematic_trading, ch.8-9]`).

Seis testes de regressão novos em `tests/test_tsmom_multi_asset.py`
bloqueiam recorrência (calendar weekday-only, sinal binário em drift
positivo, flat quando `min_active_instruments` não bate, custo de
round-trip proporcional ao delta de peso).

## Desvio de protocolo reconhecido

Fan-out manda **1 work unit por iter**. Iter 3 processou **2** configs:
- `tsmom_lb01m_vt10` — primeira execução bugada gravou artifacts ruins
  e já havia sido removida de `tickers_pending`. Após o fix, re-rodei e
  sobrescrevi os artifacts (mantendo `iter=3` no registry).
- `tsmom_lb01m_vt15` — ao reexecutar o runner normal pós-fix, o script
  leu o registry e pegou o próximo pendente (vt15), processando mais um.

Dois `iter=3` em `tickers_done` ficam registrados como uma anomalia
declarada. Nenhum config perdido; só adiantei 1 unit. Próxima iter
retoma com `tsmom_lb01m_vt20` pelo protocolo normal.

## Verdict per-config

Nenhum dos dois passa os gates de winner V2 — como esperado para
lookback=1m (muito ruidoso para TSMOM mensal, `[trend_following_covel, ch.5-6]`
sugere 3-12m como zona útil).

| Config | IS Sharpe | OOS Sharpe | FWD Sharpe | OOS CAGR | Median hold | Gates pass |
|--------|----------:|-----------:|-----------:|---------:|------------:|:----------:|
| lb01m_vt10 | -0.382 | -1.128 | -1.201 | -2.54% | 41.0d | 2/7 |
| lb01m_vt15 | -0.381 | -1.118 | -1.219 | -3.40% | 41.0d | 2/7 |

Custo de swap (longs equity ≈ 5 bps/dia) dominou: vt10 acumulou
73.8% swap cumulativo em 25 anos, vt15 acumulou 107% — sinal que
lb=1m vira-e-mexe demais, ficando comprado em instrumentos laterais
pagando overnight. Este dado só reforça a tese de que lookbacks curtos
não sobrevivem num CFD com swap ≠ 0.

## Próximo passo

Iter 4 rodará `tsmom_lb01m_vt20`, depois 9 configs restantes dos
blocos 3m/6m/12m. Aggregator (último iter do Lead) aplica PBO + DSR
sobre a matriz completa e escolhe a best config, se houver.

## Arquivos

- Código: `src/ai_trade/backtest/strategies/tsmom_multi_asset.py` (fix weekday)
- Testes: `tests/test_tsmom_multi_asset.py` (+6 tests, baseline 765 → 771)
- Artifacts: `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/tsmom_lb01m_vt10.{md,json}`
- Artifacts: `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/tsmom_lb01m_vt15.{md,json}`
- Registry: `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/registry.json` (2 done, 10 pending)

## Citações

- TSMOM binário long-only + vol-target per-asset: `[systematic_trading, ch.8-9]`.
- Rebalance mensal EOM como convenção CTA: `[trend_following_covel, ch.5-6]`.
- σ̂ defasado para evitar look-ahead: `[advances_fin_ml, p.162-164]`.
- Walk-forward 6/8 + 25% DD cap: `[advances_fin_ml, ch.11]`.
