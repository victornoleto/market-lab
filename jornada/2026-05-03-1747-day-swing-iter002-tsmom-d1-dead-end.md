# Day/swing iter 002 — TSMOM D1 simples falhou nos gates robustos

Rodei a iteracao 002 em `studies/day_swing_strategy_hunt/iterations/002-tsmom-d1-minimal/`, seguindo pre-registro antes do teste. A regra foi Time-Series Momentum D1 long/flat nos 10 simbolos do universo inicial, com lookbacks congelados 20, 60 e 120 barras.

O ponto estimado pareceu bom, mas nao passou pelos gates que protegem contra overfit. O melhor lookback por Sharpe base foi 60 barras: 13.35% CAGR, Sharpe 0.988 e MDD -24.58%, batendo buy-and-hold e random-entry em Sharpe. Mesmo assim, a selecao entre lookbacks falhou PBO: 0.557, acima do limite 0.5. O OOS 2024+ tambem nao passou bootstrap severo: o ponto estimado foi positivo, mas o CI 99.9% low ficou negativo em -10.64% anualizado.

Verdict: `dead-end` para a grade TSMOM D1 minima 20/60/120. Nao ha winner, nao ha paper/live, e nao vamos tentar salvar ajustando threshold/lookback depois de ver resultado. Capital segue 100% Plano C; Plano A continua DORMANT.

Proximo passo sugerido: mudar de familia para Volatility Breakout H4 com canais Donchian/ATR pre-registrados, em vez de otimizar em cima da falha D1.
