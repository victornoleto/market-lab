# Day/swing iter 006 — Crypto Momentum Vol Throttle falhou bootstrap OOS

Testei a Familia E em `studies/day_swing_strategy_hunt/iterations/006-crypto-momentum-vol-throttle-diagnostic/` como diagnostico BTCUSD/ETHUSD-only. O pre-registro congelou D1, momentum 60 dias e throttle por percentil de volatilidade realizada 20d para reduzir exposicao em regimes extremos `[volatility_trading, ch.2]`.

O resultado pontual foi forte: 33.02% CAGR, Sharpe 1.016 e MDD -54.73% no custo base; custo stress ainda ficou positivo em 26.60% CAGR e Sharpe 0.868. Mesmo assim, o verdict e `dead-end`: o bootstrap OOS 99.9% low ficou negativo (-19.66% anualizado), e crypto-only nunca pode virar winner sozinho.

Capital segue 100% Plano C; Plano A segue DORMANT. Nao houve paper/live, nem ajuste de thresholds depois do resultado.
