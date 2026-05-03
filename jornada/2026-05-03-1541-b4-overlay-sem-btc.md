# Overlay B4 sem BTC testado em janela longa

Removi BTC para tirar a restricao de inicio em 2010 e rodei o iter 049 em
`spy_beater_hunt`: B4 sem BTC com overlay restrito de regime. Para manter o
proxy RSST corrigido em janela longa, usei `DBMFSIM?FB=KMLMSIM` como fallback
antes do inicio nativo de DBMF, preservando a estrutura `SPY + 70% DBMF + 30%
KMLM - cash` quando DBMF existe.

Resultado principal em 1987-12-31 a 2026-05-01: B4 estatico fez 12.51% CAGR /
-29.81% MDD / Sharpe 0.894. O melhor overlay restrito
`overlay_200d_12mdd_10pp` fez 13.05% CAGR / -26.65% MDD / Sharpe 0.933. Isso e
um sinal promissor: melhora retorno, drawdown e Sharpe na mesma simulacao.

Ainda nao e aprovacao live automatica. O fallback estende a historia, mas nao e
historico puro de DBMF antes de 2000; e o overlay ainda precisa de checks estilo
gate/OOS antes de virar regra operacional. Mesmo assim, a tese de overlay
restrito ficou mais forte do que o solver livre do iter 043, que tinha piorado
Sharpe por overfit/corner solutions.
