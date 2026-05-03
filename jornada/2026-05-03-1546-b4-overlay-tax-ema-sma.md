# Overlay B4 com DARF e SMA/EMA

Rodei o iter 050 para responder duas duvidas antes de considerar overlay live:
quanto a DARF anual sobre vendas come da vantagem, e se o sinal depende apenas
do 200d SMA popular. Usei B4 sem BTC, janela 1987-12-31 a 2026-05-01, RSST com
`DBMFSIM?FB=KMLMSIM`, e imposto anual de 15% sobre ganhos realizados por
rebalance mensal. A linha static tambem foi forcada a rebalance mensal para ser
comparavel em tax lots; na vida real, static via aportes pode diferir e adiar
mais imposto.

Resultado: o melhor overlay pos-imposto foi `overlay_sma150_12mdd_10pp`, com
12.35% CAGR liquido / -28.00% MDD / Sharpe 0.901. O B4 estatico forçado mensal
ficou em 12.18% / -30.88% / 0.880. A vantagem liquida existe, mas e pequena:
aprox. +0.17pp CAGR, +2.9pp MDD e +0.021 Sharpe. Em bruto, a vantagem era maior,
mostrando que DARF recorrente realmente importa.

Sobre o 200d: nao foi o unico vencedor. SMA 126/150/180/200/210/252 e EMA
126/150/180/200/210/252 ficaram em faixa proxima; SMA 150d foi melhor, SMA 126d
quase empatou, e EMA 150d tambem ficou acima do 200d. Isso reduz a suspeita de
que o resultado seja apenas crowding do 200d, mas ainda exige checks OOS/gates
antes de virar regra live.
