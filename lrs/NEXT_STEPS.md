# NEXT_STEPS - LRS Restart

Este arquivo e o handoff operacional para uma nova sessao limpa de contexto. Leia
este documento antes de continuar a evolucao da estrategia em `lrs/`.

## Leitura Obrigatoria

1. `docs/PUBLIC_SUMMARY.md`.
2. `docs/CURRENT_STATE.md`.
3. `README.md`.
4. `docs/PROJECT_HISTORY.md`.
5. `docs/investment-mandate.md`.
6. `lrs/SPEC.md`.
7. `lrs/MEMORY.md`.
8. Este arquivo.
9. Ultimo report: `lrs/phases/phase02_target_leverage_vol/REPORT.md`.

## Contexto Fixo

- O repositorio segue em maintenance mode. Nada em `lrs/` autoriza deploy, paper
  trade ou mudanca de mandato.
- `lrs/` e um restart local e research-only da familia Gayed/LRS.
- Regra base: `underlying.shift(1) > SMA200.shift(1)` entra em risco-on
  alavancado; caso contrario usa sleeve defensiva `[leverage_for_the_long_run,
  p.13]`.
- A SMA deve ser interpretada como proxy simples de regime de volatilidade e
  downside, nao como otimizador magico de retorno `[leverage_for_the_long_run,
  p.7-8]`.
- Alta volatilidade degrada a composicao de portfolios alavancados; por isso a
  Phase 2 testou filtros simples de volatilidade realizada
  `[leverage_for_the_long_run, p.4-7]`.
- Qualquer escolha nova de indicador, parametro, gate ou estrategia precisa citar
  livro no formato `[book.slug, p.X]` ou `[book.slug, ch.Y]`.
- Overfit gates continuam diagnosticos durante a evolucao local, mas qualquer
  promocao futura exigiria os gates do mandate: PBO, DSR, WF, OOS, FWD stress,
  bootstrap e cross-lib `[advances_fin_ml, p.208-211]`, `[advances_fin_ml,
  p.222-223]`.

## Estado Atual

### Phase 0 - Baseline Gayed

- Arquivo: `lrs/phases/phase00_gayed_baseline/REPORT.md`.
- Testou 24 linhas: SPY/QQQ 2x/3x x lag `n=0..5`.
- Risk-off: `CASHX`.
- Top score: `SPY_3x`, lag `2`, after-tax CAGR `16.91%`, MDD `-88.33%`, Calmar
  `0.191`.
- Melhor QQQ: `QQQ_3x`, lag `0`, after-tax CAGR `21.34%`, MDD `-91.97%`.
- Leitura: retorno existe, mas drawdown e ruin-tier.

### Phase 1 - Risk-Off Alternatives

- Arquivo: `lrs/phases/phase01_risk_off/REPORT.md`.
- Testou 264 linhas: 4 branches x 11 risk-off sleeves x lag `n=0..5`.
- Top score: `SPY_2x`, risk-off `40 ZROZ / 40 GLD / 20 IEF`, lag `5`, after-tax
  CAGR `15.23%`, MDD `-41.34%`, Calmar `0.368`.
- `34` linhas bateram underlying after-tax com MDD `<=50%`; todas SPY 2x.
- Melhor SPY 3x ainda warning-tier: MDD `-61.04%`.
- QQQ 2x/3x ainda ruin-tier nessa superficie.
- Leitura: risk-off importa muito; antes de indicadores amplos, mexer em
  exposicao/alavancagem e volatilidade.

### Phase 2 - Target Leverage And Volatility Throttle

- Arquivo: `lrs/phases/phase02_target_leverage_vol/REPORT.md`.
- CSV: `lrs/results/phase02_target_leverage_vol.csv`.
- Plots: `lrs/phases/phase02_target_leverage_vol/plots/`.
- Testou 2,400 linhas: SPY/QQQ x 8 target leverages x 5 risk-off sleeves x 5
  vol filters x lag `n=0..5`.
- Top score geral: `SPY` L`2.00`, risk-off `50 ZROZ / 25 GLD / 25 CASH`,
  `RV21 <= 30%`, lag `3`, after-tax CAGR `15.44%`, MDD `-39.28%`, Calmar
  `0.393`, terminal `12.28x` vs SPY after-tax.
- Melhor QQQ: L`1.75`, risk-off `40 ZROZ / 40 GLD / 20 IEF`, `RV63 <= 40%`,
  lag `0`, after-tax CAGR `19.46%`, MDD `-42.58%`, Calmar `0.457`, terminal
  `5.82x` vs QQQ after-tax.
- `875` practical-pass rows: MDD `>= -50%` e outperformance after-tax contra o
  underlying.
- `394` preferred rows: MDD `>= -40%`.
- `303` QQQ practical-pass rows.
- Leitura: geometria de exposicao resolveu parte relevante do drawdown antes de
  adicionar indicadores.

### Phase 3A - Sparse Risk-On Confirmation Vote (CONCLUIDA 2026-06-07)

- Arquivo: `lrs/phases/phase03_sparse_risk_on_vote/REPORT.md`.
- CSV: `lrs/results/phase03_sparse_risk_on_vote.csv`. Helpers novos:
  `lrs/lib/indicators.py`. Testes: `tests/test_lrs_phase03.py`.
- Testou 324 linhas: SPY/QQQ x 3 bases por branch (top Phase 2 + 2 vizinhos de
  1 alavanca) x 9 filtros (`none` + Clenow/ROC/histerese/ADX x 2 variantes) x
  lag `0..5`. Cada linha faz AND de no maximo UM filtro sobre o sinal base.
  Scoring Phase 2 mantido verbatim.
- Resultado NEGATIVO: top geral e o controle `none` (`SPY spy_top` L`2.00` lag
  `3`, after-tax CAGR `15.44%`, MDD `-39.28%`) — reproduz a Phase 2 exatamente
  (sanity check, diff `0`). Nenhum filtro bate `none` em nenhuma branch.
  Clenow/ROC/ADX divergem mas reduzem CAGR. ADX e proxy close-only degradado
  (sem OHLC no cache).
- Insight estrutural: histerese SMA como AND-gate e IDENTICA a `none` em 36/36
  configs — so testavel substituindo o gate SMA, nao fazendo AND.
- Leitura: complexidade de filtro risk-on nao se justifica; geometria de
  exposicao da Phase 2 e o driver real `[trading_systems_methods, p.939]`,
  `[advances_fin_ml, p.208-211]`.

## Regras Para Continuar

- Nao declarar winner, paper-trade candidate ou deploy candidate sem rodar os
  gates formais do mandate.
- Nao fazer grid amplo de indicadores tecnicos combinados sem pre-registro. Isso
  aumenta risco de overfit `[trading_systems_methods, p.939]`,
  `[advances_fin_ml, p.208-211]`.
- Preferir mudancas pequenas e estruturais: uma familia de mecanismo por fase.
- Manter execucao semanal e lag `n=0..5` ate haver razao documentada para mudar.
- Durante lag `n>0`, manter `CASHX` antes de entrar na nova sleeve.
- Usar sempre `AnnualDarfEngine` para modelo tributario BR de ETFs estrangeiros.
- Gerar plots em toda fase.
- Atualizar `lrs/MEMORY.md` apos cada phase executada.
- Atualizar `docs/CURRENT_STATE.md` e, se a conclusao mudar a narrativa publica,
  `docs/PROJECT_HISTORY.md`.
- Nao tocar nas mudancas nao relacionadas em `studies/return_stacked_core/...`
  salvo pedido explicito do usuario.

## Proximo Trabalho Recomendado

### Phase 3A - Small Risk-On Vote Sobre A Geometria Phase 2 (CONCLUIDA)

> CONCLUIDA em 2026-06-07. Resultado negativo: nenhum filtro de confirmacao bate
> o controle `none` (ver "Estado Atual" acima e o REPORT). Proximo trabalho real
> abaixo passa a ser Phase 3A-2 (histerese como substituta do gate SMA) ou a
> Phase 4 de validacao diagnostica. A descricao original e mantida abaixo como
> referencia de design.

Objetivo: verificar se poucos filtros risk-on, estruturalmente distintos,
melhoram a fronteira sem abrir um grid enorme.

Base inicial sugerida:

- SPY base: L`2.00`, risk-off `50 ZROZ / 25 GLD / 25 CASH`, `RV21 <= 30%`, lag
  sweep `0..5`.
- QQQ base: L`1.75`, risk-off `40 ZROZ / 40 GLD / 20 IEF`, `RV63 <= 40%`, lag
  sweep `0..5`.
- Tambem testar vizinhancas proximas de Phase 2, nao so o top exato, para evitar
  fragilidade de ponto unico.

Familias candidatas, uma por vez:

- Trend hysteresis: entrada acima de SMA200, saida abaixo de SMA200 com banda
  pequena ou MA secundaria. Precisa citar fonte antes de implementar.
- Trend quality: slope de regressao ajustado por R2, inspirado em Clenow
  `[stocks_on_the_move, p.66-67]`.
- Momentum/streak quality: ROC ou momentum simples, mantendo a familia pequena
  `[stocks_on_the_move, p.60]`.
- Trend strength: ADX como confirmacao, se usado, citar a fonte do indicador
  antes de rodar.
- Volatility refinement: comparar RV21/RV63 thresholds proximos, mas evitar
  transformar isso em busca fina demais.

Formato recomendado:

- Criar `lrs/phases/phase03_sparse_risk_on_vote/`.
- Criar `README.md` e `run.py`.
- Limitar a combinatoria. Exemplo aceitavel: 2 branches x 3-5 bases x 3-5 filtros
  x 6 lags.
- Reportar sempre top geral, top por branch, pass counts, preferred counts,
  rolling hit rates, terminal vs underlying, terminal vs target-leverage B&H,
  turnover e tax paid.
- Incluir plots: top SPY, top QQQ, frontier, sensitivity por filtro.

Itens a verificar nessa fase:

- Se o filtro melhora MDD sem matar CAGR/terminal.
- Se o ganho aparece em SPY e QQQ ou e apenas branch-specific.
- Se o lag vencedor e robusto ou depende de um `n` especifico.
- Se `none` continua tao bom quanto filtros novos; se sim, nao adicionar
  complexidade.
- Se turnover e imposto aumentam demais.
- Se rolling 10y/15y/20y hit rates pioram apesar do top full-period melhorar.

### Phase 3B - Bear-Market Sleeve Separada

Objetivo: testar se uma sleeve bear/inversa reduz drawdown residual sem explodir
whipsaw e short-convexity risk.

So fazer depois de confirmar se Phase 3A nao resolve o drawdown, ou se o usuario
priorizar drawdown sobre simplicidade.

Prerequisitos:

- Verificar se existem series inverse/synthetic no cache. Procurar por `SH`,
  `SDS`, `SPXU`, `PSQ`, `QID`, `SQQQ`, ou sintaxe Testfol.io `?L=-1/-2/-3`.
- Se nao houver dados, documentar bloqueio ou criar fetch/synthetic separado.
- Capar exposicao inversa; nao assumir que bear-market sleeve pode ser 3x full
  size por padrao.

Itens a verificar:

- Melhora de MDD absoluto.
- Piora de CAGR/terminal por whipsaw.
- Piora de rolling 10y/15y hit rates.
- Sensibilidade extrema a crash regimes especificos.
- Turnover e imposto.
- Se a sleeve inversa so funciona com parametros pos-hoc de 2008/2020, descartar.

### Phase 4 - Validacao Diagnostica

Nao e promocao; e diagnostico para saber se a familia merece continuar.

Itens minimos:

- Walk-forward por blocos longos.
- PBO/CPCV do pequeno painel testado.
- DSR com `n_trials` honesto do restart e das fases relacionadas
  `[advances_fin_ml, p.196-202]`.
- Single-block OOS recente.
- FWD stress recente.
- Bootstrap 99.9% CI.
- Cross-lib ou pelo menos numpy/reference-vs-current engine para a familia final.

Se qualquer gate falhar, registrar como diagnostico, nao como winner.

## Perguntas Em Aberto

- O objetivo primario da proxima fase e maximizar CAGR com MDD `<=50%` ou buscar
  MDD `<=40%` mesmo sacrificando retorno?
- QQQ deve ser tratado como branch separada com parametros proprios ou precisa
  compartilhar a mesma gramatica SPY/QQQ com poucos parametros distintos?
- A proxima fase deve priorizar simplicidade operacional ou frontier economica?
- A estrategia deve evitar qualquer sleeve que dependa de sintetico Testfol.io
  dificil de executar em broker real?
- O limite pratico de turnover anual ainda e aceitavel para DARF/controle manual?

## Comandos Uteis

```bash
uv run pytest tests/test_lrs_phase00.py
uv run python -m lrs.phases.phase02_target_leverage_vol.run
```

Para uma nova fase, depois de implementar:

```bash
uv run pytest tests/test_lrs_phase00.py
uv run python -m lrs.phases.phase03_sparse_risk_on_vote.run
```

## Arquivos-Chave

- `lrs/lib/backtest.py`: helpers comuns de sinal, pesos semanais, simulacao com
  imposto, metricas e estatisticas relativas.
- `lrs/phases/phase00_gayed_baseline/run.py`: baseline Gayed original.
- `lrs/phases/phase01_risk_off/run.py`: sweep de risk-off.
- `lrs/phases/phase02_target_leverage_vol/run.py`: target leverage e vol
  throttle.
- `tests/test_lrs_phase00.py`: testes focados dos helpers LRS.
- `data/testfolio/cache/history.parquet`: cache local usado pelas fases.

## Checklist Antes De Encerrar Qualquer Nova Sessao

- Rodou a phase nova com timeout adequado?
- Gerou `REPORT.md`, CSV em `lrs/results/` e plots?
- Atualizou `lrs/MEMORY.md`?
- Atualizou docs publicos se o estado publico mudou?
- Rodou `uv run pytest tests/test_lrs_phase00.py`?
- Conferiu `git status --short` e separou mudancas relacionadas das nao
  relacionadas?
- Registrou explicitamente que nao houve deploy, paper-trade label ou mandate
  change?
