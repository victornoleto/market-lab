# spy_beater: SPMO/FMTM momentum sleeve revisado

Revisei a ideia de adicionar momentum/SCV ao B4/BTC5 depois da popularidade de
SPMO e FMTM. Criei o iter 052 em
`studies/spy_beater_hunt/iterations/052-2026-05-03-momentum-scv-sleeves/`.

O resultado separa bem qualidade de evidência:

- SPMO live foi realmente bom desde 2015: 18.49% CAGR / -30.94% MDD / Sharpe
  0.848 contra SPY 14.72% / -33.70% / 0.740 e SSO 22.79% / -59.34% / 0.696.
- FMTM foi ainda melhor desde 2025-03, mas a janela no testfol.io e so 1.11
  ano; fica em watchlist, nao em deploy.
- MTUMSIM em janela longa 1994+ confirma momentum como fator, mas com drawdown
  parecido com SPY: 13.35% / -56.10% / 0.602 contra SPYSIM 10.96% / -55.20% /
  0.517.

No nosso portfolio, o melhor candidato pequeno foi SPMO financiado de ZROZ. Em
B4+BTC5, a variante `B4_btc5_spmo5_from_zroz` melhorou a janela 2022+ de 12.28%
/ -25.98% / 0.531 para 14.23% / -25.15% / 0.625. Ainda nao e gate-equivalent:
a janela e curta e nao substitui PBO/DSR/WF/bootstrap.

Leitura pratica: nao trocar o winner agora, mas manter como proxima hipotese
pre-registravel: 25% NTSX / 25% GDE / 25% RSST / 15% ZROZ / 5% BTC / 5% SPMO.
