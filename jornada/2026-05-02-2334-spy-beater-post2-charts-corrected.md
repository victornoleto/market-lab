# spy_beater_hunt — gráficos do Post 2 corrigidos para janela 2000+

Os gráficos principais do draft do Post 2 foram regenerados para ficar consistentes com o iter 045: janela comum 2000-01-03 → 2026-05-01, rebalanceamento mensal, ERs explícitos, sem DARF para static buy-and-hold/lazy-rebal, e proxy `RSST = SPY + 70% DBMF + 30% KMLM - cash`.

Antes, os PNGs ainda refletiam o snapshot visual antigo do Post 1 (1987-2026, proxy `SPY + KMLM`). Isso criava uma inconsistência metodológica com a tabela canônica corrigida. A escolha foi refazer os gráficos, não apenas adicionar caveat, porque o teste live mostrou que o proxy 70/30 acompanha melhor o RSST real e DBMFSIM força a janela 2000+ `[risk_parity, ch.5, p.10]` `[ilmanen_expected_returns, ch.19]`.

Arquivos atualizados:

- `testfolio_01_equity.png`
- `testfolio_02_drawdown.png`
- `testfolio_03_scatter.png`
- `testfolio_04_rolling_grid.png`
- `REDDIT_POST_2_technical.md`

Também foi adicionado `plot_post2_charts.py` no iter 045 para tornar a geração dos gráficos reproduzível. Capital segue 100% Plano C, sem deploy.
