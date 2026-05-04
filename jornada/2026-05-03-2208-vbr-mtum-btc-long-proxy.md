# VBRSIM/MTUMSIM long proxy para satellite

Rodei o iter 055 para remover a limitacao do FMTM. Usei 10% VBRSIM como proxy
SCV, 10% MTUMSIM como proxy momentum (SPMO+FMTM) e 5% BTCSIM quando BTC entra. Fiz dois
testes: 2010+ limitado por BTC e 2000+ sem BTC.

Com BTC desde 2010, B4+BTC5 continuou sendo melhor por Sharpe: 23.18% CAGR /
-27.26% MDD / Sharpe 1.472. A melhor variante moderada por CAGR,
`proxy_sat_from_zroz_ntsx`, fez 24.40% / -29.90% / 1.412. Ou seja, compra
+1.22pp CAGR, mas perde MDD e Sharpe.

Sem BTC desde 2000, B4 base venceu por Sharpe/MDD: 12.27% / -29.02% / 0.881. Os
satellites VBRSIM/MTUMSIM elevaram um pouco o CAGR em alguns casos, mas com MDD
na faixa -35% a -43% e Sharpe menor.

Conclusao: a cesta fator/crypto pode ser uma preferencia agressiva para buscar
CAGR, mas nao e melhoria core sobre B4+BTC5. Se for usada, o formato menos ruim
continua sendo preservar RSST e financiar de NTSX+ZROZ, nao zerar ZROZ.
