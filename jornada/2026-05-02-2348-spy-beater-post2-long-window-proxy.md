# spy_beater_hunt — Post 2 volta para proxy RSST long-window

O draft do Post 2 foi ajustado para usar `RSST = SPY + KMLM - cash` como metodologia principal. A razão é prática: `DBMFSIM` começa em 2000 e reduz a amostra para ~26 anos; `KMLMSIM` permite manter a janela longa 1987-12-30 → 2026-04-29, que captura mais regimes úteis para o estudo `[risk_parity, ch.5, p.10]` `[ilmanen_expected_returns, ch.19]`.

Decisão narrativa: o proxy `SPY + 70% DBMF + 30% KMLM - cash` fica como caveat/sensitivity final, não como tabela principal. Ele provavelmente acompanha o RSST real melhor, mas sacrifica 12+ anos de histórico. O post agora diz explicitamente que a aproximação KMLM-only não é reconstrução perfeita de RSST e que os números podem mudar na versão 70/30.

Os quatro gráficos principais foram regenerados para refletir a metodologia long-window:

- `testfolio_01_equity.png`
- `testfolio_02_drawdown.png`
- `testfolio_03_scatter.png`
- `testfolio_04_rolling_grid.png`

Novo script reproduzível: `studies/spy_beater_hunt/iterations/044-2026-05-01-iter038-rebaseline-monthly-ers-terminal-darf/plot_post2_long_window_charts.py`.

Capital segue 100% Plano C, sem deploy.
