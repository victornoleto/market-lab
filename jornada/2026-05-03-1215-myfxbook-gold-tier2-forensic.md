# MyFxBook reverse-engineering — Tier 2 Gold forense fecha over-fire

Rodei o Tier 2 opcional no backtest derivado das regras Gold para responder se o resultado negativo era apenas efeito de over-fire. O teste reduziu cada stream sintetico para `k = n_real_trades` sem alterar `frozen_rules/`.

O seletor minimamente honesto (`uniform_time_k_n_real`, sem PnL futuro) falhou nos 7 systems no cenario M5 + 45p: todos tiveram Sharpe negativo, bootstrap full low negativo e OOS bootstrap low negativo. O oracle ex-post (`oracle_best_net_pips_k_n_real_nontradeable`) passou em varios, mas ele escolhe os melhores trades olhando o PnL futuro; portanto so mostra que havia bons trades dentro do over-fire, nao uma regra executavel.

Conclusao: reduzir a frequencia para casar `n_real` nao salva as regras Gold de forma tradeavel. HappyForex segue como nao decodificavel e sem robustez economica derivada. Capital segue 100% Plano C; Plano A DORMANT.
