# Day/swing iter 003 — Vol Breakout H4 minimo falhou bootstrap

Rodei a iteracao 003 do `day_swing_strategy_hunt` em `studies/day_swing_strategy_hunt/iterations/003-vol-breakout-h4-minimal/`. A regra testada foi Volatility Breakout H4: canais Donchian 20/55, filtro ATR p50/p70, entrada por rompimento e saida por canal oposto `[trading_systems_methods, ch.14]`.

O melhor ponto estimado foi `donchian55_atrp50`: 8.07% CAGR, Sharpe 0.477 e MDD -31.24%. Ele passou PBO (0.000), ficou positivo sob custo stress e bateu random-entry, mas nao bateu buy-and-hold H4 em Sharpe. Mais importante: bootstrap full 99.9% low ficou negativo (-7.19% anualizado) e OOS 2024+ tambem (-21.86%), entao o verdict e `dead-end` `[advances_fin_ml, p.31-34]`.

Nao ha winner, nao ha paper/live e nenhum resultado single-asset foi aceito como candidato. Capital segue 100% Plano C; Plano A continua DORMANT. A proxima sessao nao deve tentar salvar esta grade ajustando canal/ATR depois do resultado.
