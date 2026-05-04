# Day/swing iter 005 — Gold Regime Split falhou

Rodei a iteracao 005 em `studies/day_swing_strategy_hunt/iterations/005-gold-regime-split-diagnostic/` como diagnostico XAUUSD-only. O pre-registro travou que Gold sozinho nunca poderia virar winner; qualquer resultado positivo teria sido apenas sinal para uma iteracao multi-asset futura `[trading_systems_methods, p.13-14]`.

A regra minima usou D1 para reduzir peso de custo `[systematic_trading, p.182-197]`: tendencia por SMA100/retorno 100 barras, regime por percentil de ATR(14)/close em 252 barras, modo trend acima de p60 e modo range abaixo de p40. A janela XAUUSD D1 da Dukascopy passou auditoria: 2593 barras de 2018-01-01 a 2026-05-01.

Resultado: `dead-end`. A estrategia teve -6.18% CAGR, Sharpe -0.442 e MDD -51.14% no custo base; no bloco OOS 2024+ ficou em -5.92% CAGR; sob custo stress caiu para -11.48% CAGR. Bootstrap full e OOS 99.9% tiveram lows negativos `[advances_fin_ml, p.31-34]`.

Comparada aos controles da iteracao 001, perdeu para buy-and-hold XAUUSD, always-flat, uniform-frequency e random-entry `[evidence_based_ta, p.247-260]`. Nao ha winner, nao ha paper/live, e nao vale tentar salvar ajustando SMA, ATR, percentis ou bandas depois de ver o resultado.

Capital segue 100% Plano C; Plano A segue DORMANT.
