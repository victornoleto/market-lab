# MyFxBook reverse-engineering — backtest derivado das regras Gold

Após a falha de fidelidade M5/M1, rodei um teste separado de `derived_strategy_backtest` para as regras Gold absorvidas. Este teste pergunta se a logica extraida teria resultado economico proprio; ele nao reabre a tese de reverse engineering do EA original.

Foram testados 7 systems XAUUSD/Gold usando os trades sinteticos ja gerados pelo replicator, com cenarios de custo 0p, 45p e 80p round-trip por trade. No cenario principal M5 + 45p, nenhum system teve bootstrap full e OOS positivos simultaneamente. O melhor H1_MOMENTUM_GOLD foi `10281851`, com Sharpe 0.162, mas bootstrap 99.9% low negativo e OOS bootstrap low negativo.

Conclusao: as regras Gold absorvidas tambem nao apresentam robustez economica simples como estrategia derivada. Capital segue 100% Plano C; Plano A permanece DORMANT. Relatorio: `studies/myfxbook_reverse_engineering/_diagnostics/DERIVED_GOLD_BACKTEST.md`.
