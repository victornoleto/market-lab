# Day/swing iter 004 — Carry/Trend FX bloqueado por dados

Resultado: `inconclusive`. A Familia C Carry/Trend FX nao foi backtestada porque o pre-registro exigia dados confiaveis de rates/carry para EUR, GBP, USD, JPY, CHF, CAD, AUD e NZD antes do teste, e o repo nao tinha essa fonte documentada.

Isto e uma parada conservadora, nao uma rejeicao economica da tese. Sem uma matriz historica de juros/carry por moeda, usar spot FX, retorno passado ou PnL futuro como substituto viraria proxy improvisado e violaria o protocolo `[quant_trading_chan, ch.6]`.

Capital segue 100% Plano C; Plano A segue DORMANT. Nao houve paper/live, winner, PBO, bootstrap ou estrategia rodada.
