# SPMO rigorous validation nao virou gate-passed winner

Rodei o iter 053 em
`studies/spy_beater_hunt/iterations/053-2026-05-03-spmo-rigorous-validation/`
para testar de forma mais dura o candidato 25% NTSX / 25% GDE / 25% RSST /
15% ZROZ / 5% BTC / 5% SPMO.

Na janela live disponivel para o sleeve, 2022-03-17 -> 2026-05-01, ele melhorou
B4+BTC5 de 12.28% CAGR / -25.98% MDD / Sharpe raw 0.782 para 14.23% / -25.15%
/ 0.872. No split 70/30 tambem manteve CAGR melhor no OOS, mas com drawdown
ligeiramente pior no OOS. O bootstrap em blocos deu excesso medio anual de
+1.66pp e probabilidade de excesso positivo de 99.52%, mas o CI 99.9% low ficou
negativo (-0.26pp).

Conclusao honesta: SPMO e promissor e fica como high-priority research
candidate, mas nao substitui o B4+BTC5 como winner formal. Falha promocao porque
a janela real e curta e o bootstrap 99.9% nao passa o hard standard do projeto.
