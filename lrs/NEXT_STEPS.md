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
9. `lrs/TOP20_BY_CAGR.md`.
10. Ultimo report: `lrs/phases/phase05_rsc_overlay_proxy/REPORT.md`.

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

### Phase 3A-2, 3C e 4 - Regime/Lookback/Gates (CONCLUIDAS 2026-06-07)

- Arquivos: `lrs/phases/phase03b_regime_signals/REPORT.md`,
  `lrs/phases/phase03c_lookback_study/REPORT.md`,
  `lrs/phases/phase04_validation_gates/REPORT.md`.
- Phase 3A-2 testou formas de regime substituindo SMA200; nenhuma bate SMA200 em
  SPY e QQQ. EMA200 e QQQ-only near-tie, mas piora MDD.
- Phase 3C respondeu "por que 200?": 200 e uma janela fixa adequada dentro da
  regiao `~175-225`, mas nao e platao robusto amplo nem ancorada em persistencia;
  adaptativo piora liquido de turnover.
- Phase 4 rodou gates do mandate sobre 6 bases SMA200: **0/6 passam**. Gate
  vinculante = walk-forward; QQQ tambem falha PBO/DSR. LRS standalone encerrado
  como research-only negativo `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.273-275]`.

### Phase 5 - RSC Overlay Rebuilt-Sleeve Diagnostic (CONCLUIDA 2026-06-08/09)

- Arquivo: `lrs/phases/phase05_rsc_overlay_proxy/REPORT.md`.
- CSV: `lrs/results/phase05_rsc_overlay_proxy.csv`.
- Plots: `lrs/phases/phase05_rsc_overlay_proxy/plots/`.
- Testes: `tests/test_lrs_phase05.py`.
- Objetivo: testar se LRS/T3d faz sentido como satelite pequeno sobre RSC-US
  `35/40/25`, usando metricas de underwater/recovery e drawdown relativo.
- Fonte RSC: matriz local
  `studies/return_stacked_core/us_core/series/return_stacked_core_sleeve_returns.parquet`
  com `GDESIM`, `RSSTSIM`, `ZROZSIM` e sleeves auxiliares. `RSSTSIM` = `SPYSIM +
  0.70*DBMFSIM + 0.30*KMLMSIM - (CASHX + 0.0200/252)`, equivalente local ao
  payload `100% SPY + 70% DBMF + 30% KMLM - 100% CASHX?E=-2`; proxy documentado,
  nao backfill de ETF live
  `[risk_parity, p.80-81]`, `[systematic_trading, p.185-188]`.
- Resultado: `0/9` overlays passam o screen rebuilt-sleeve estrito. Maior CAGR de
  overlay: `70% RSC / 30% T3d-K2`, CAGR `14.24%`, MDD `-48.65%`, Calmar `0.293`,
  vs RSC reconstruido CAGR `12.40%`, MDD `-30.76%`, Calmar `0.403`.
- Top-20 independente de drawdown: `lrs/TOP20_BY_CAGR.md` e
  `lrs/results/top20_by_cagr.csv` ranqueiam `4183` rows por CAGR desc. Top row:
  `QQQ L3.00 / ZROZ / RV63<=40% / lag5`, CAGR `25.84%`, MDD `-71.05%`.
- Leitura: nao ha overlay strict com o RSST proxy revisado. A proxima acao depende
  de escolha explicita do usuario sobre qual row/lead quer seguir; depois disso,
  tax/friction account-level + gates honestos continuam obrigatorios
  `[testing_tuning, p.327-335]`, `[systematic_trading, p.185-188]`,
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
- A matriz RSC-US core ja foi exportada; nao chamar `RSSTSIM` de ETF live nem
  afirmar match exato com a curva RSC salva antiga. O proxy atual começa em 2000
  por causa de `DBMFSIM`.

### Phase 6 Round - 6C/6B/6D/6A (CONCLUIDA 2026-06-09)

- Pergunta do usuario: "existe estrategia LRS que valha ceder parte de um
  portfolio 100% static?" Decisoes: benchmarks RSC-US + SSO B&H + SPY B&H,
  teto MDD `-50%`, 4 frentes aprovadas. Ordem de execucao: 6C -> 6B -> 6D -> 6A.
- **6C forense WF (+0 trials):** 84 janelas persistidas
  (`lrs/results/phase06c_wf_forensics.csv`). Headline pre-registrado (>=2/3 das
  falhas em `bull_low`): NO (48,5%), mas 90,9% das falhas sao bull;
  `bear_high` beat 100% (+154pp medio), `bear_mid` 0% (whipsaw alavancado).
  Edge concentrado em crise profunda.
- **6B vol-targeting continuo (+72 -> 3948):** SPY FAIL (WF 12/17 = baseline);
  QQQ SUCCESS diagnostico (sigma 40%/RV21/lag1: WF 7/11 vs 6/11, CAGR 19,14%,
  MDD -42,18%). Vira satelite na 6A.
- **6D sleeve inversa (+36 -> 3984):** FAIL nas duas branches; todo `f` piora
  CAGR e MDD. Sanity f=0 reproduz Phase 4 (~5.6e-17).
- **6A fronteira after-tax (+21 -> 4005), REVISADA 2026-06-09:** correcao do
  usuario - core static rebalanceia via aportes, sem DARF intermediario; DARF
  so na liquidacao final. Satelites LRS mantem DARF anual (giro semanal vende
  de verdade). Janela 2000+. Benchmarks: RSC `11,74% / -30,76% / Calmar 0,382`;
  SSO B&H `9,01% / -88,27%`; SPY B&H `7,81% / -55,14%`. **18/18 mixes passam o
  teto -50%; 13 batem o RSC em CAGR E Calmar.** Top Calmar:
  `mix_lrs_spy_headline_20` (12,12%, MDD -25,18%, Calmar 0,481). Maior CAGR
  unified: `mix_lrs_qqq_voltarget_30` (12,83%, -27,67%).
- **6A Part 2 - simulacao de aportes (+0 trials):** 10k inicial + 1k/mes,
  comprando so o componente mais abaixo do target (minimo de ordens), sem
  vendas, DARF final por componente gross. **Todos os 18 mixes batem 100% RSC
  em IRR** (RSC 13,72%, terminal $2,96M em $326k aportados).
  `mix_lrs_qqq_voltarget_30`: IRR 15,21% ($3,87M) com path MDD -28,4% ~= RSC.
  `mix_t3d_k2_saved_30` topa IRR (17,66%, $6,0M) mas path MDD -50,3%. SSO B&H:
  IRR 15,81% mas path MDD -80,8% (ruin). CSVs:
  `lrs/results/phase06a_aftertax_frontier.csv` e
  `lrs/results/phase06a_contribution_sim.csv`.

### Phase 7 Round - 7A/7B/7C/7D/7E/7F (CONCLUIDA 2026-06-09)

- Pergunta do usuario: "encontrar estrategia LETF que SUPERE a LRS 200d SMA";
  criterio pre-registrado da rodada = WF beats vs controle pareado (o gate
  vinculante), nao CAGR. Usuario aprovou todas as frentes + a excecao de
  citacao do gate macro (fonte blog). Ledger de trials: 4005 -> **4377**.
- **7A ensemble multi-lookback fracionario (+72):** SPY SUCCESS
  (`spy_alt_off / narrow {150,175,200,225} / lag 2`: WF **13/17 = 76,5%** vs
  12/17 - primeira linha do restart no nivel do G3; CAGR 14,49%, MDD -43,16%);
  QQQ FAIL (7/11 empate).
- **7B portfolio EW de rotacoes multi-asset (+72):** FAIL 0/3 (EW5 WF 9/11
  empata a melhor leg ex-post; MDD -53%). Diversificacao aparece no MDD, nao
  no WF.
- **7C macro gate GTT/UNRATE (+72):** FAIL 0/2 pelo criterio de MDD, com o
  maior lift de WF do restart (SPY 14/17, QQQ 10/11; CAGR > headline; zero
  rows com MDD >= -50%). Ingest novo `scripts/data_sprint/ingest_unrate_fred.py`
  + `UNRATE_LAG_TD = 25` em `macro_data_loader`. EXCEPTION de citacao
  documentada no README da fase.
- **7D vol-targeting quadratico sigma^2/RV^2 (+72):** QQQ SUCCESS
  (σ40/RV21/lag2: WF 8/11 vs 7/11, CAGR 19,53% > headline, MDD -42,63%);
  SPY FAIL (12/17 empate).
- **7E risk-off managed futures (+60, low-power 2000+):** SPY weak SUCCESS
  (100% DBMF: WF 5/6 vs 4/6, MDD -31,6% vs -39,3%); QQQ FAIL. So 6 janelas.
- **7F composicao 7A x 7D (+24, parametros congelados):** FAIL 0/2 - os
  mecanismos nao se somam (SPY 12/17 vs 13; QQQ 6/11 vs 8).

### Phase 8 - Suite Final de Gates (CONCLUIDA 2026-06-10; FAIL 0/2)

- Usuario escolheu os dois sobreviventes naturais. Suite SS5 completa com
  `n_trials = 4377`, PBO matrix = grid da familia por branch (36 configs
  cada), +0 trials. Sanity: rows da Phase 7 reproduzidas (~1e-17).
- **`spy_7a_ensemble`: 6/7.** G3 walk-forward PASSA pela primeira vez no
  restart (13/17). FAIL apenas no G2 DSR: p `0.052` vs `0.05` - margem 0.002,
  e o ledger exclui letf-lab (p honesto seria maior). "Quase la" nao passa.
- **`qqq_7d_quadratic`: 4/7.** FAIL G1 PBO (0.651), G2 DSR (p 0.138), G3 WF
  (8/11) - exatamente o prior registrado.
- Regra pre-registrada aplicada: ambos re-fechados, sem re-runs nem ajuste de
  threshold. Linha LRS volta para a prateleira.

### Phases 9, 10 e Consolidacao Final (CONCLUIDAS 2026-06-10)

- **Phase 9 (teto 3x, +48 -> 4425):** SPY lead return-first
  (`L_max 2.50/sigma40/RV21/lag3`: 16,81% / -47,47%, WF 12/17); QQQ FAIL
  (zero rows no teto -50%). Escalar pinado no cap ~99% dos dias - o ganho vem
  da alavancagem, nao do sizing.
- **Phase 10 (buy-the-dip ladder, +144 -> 4569):** FAIL 0/2 - o negativo mais
  limpo do restart. Zero rows entre 144 seguram MDD >= -50% (8 ruinas
  totais); a tese Gayed sobrevive a propria inversao.
- **Consolidacao final:** `lrs/REPORT.md` (gerado por `lrs/final_report.py`)
  + 10 plots em `lrs/plots/` - relatorio definitivo do estudo com finalistas,
  fichas operacionais e lente de aportes. ESTUDO ENCERRADO.

## Proximo Trabalho Recomendado Atual

**O estudo LRS esta ENCERRADO (2026-06-10).** Relatorio definitivo:
`lrs/REPORT.md`. A linha standalone/satelite LRS esta RE-FECHADA apos a
Phase 8 (0/2 na suite completa; vinculante agora = DSR no SPY, PBO/DSR/WF no
QQQ). O que resta de honesto:

1. Nao reabrir a familia sem literatura ou regime genuinamente novos - o
   resultado da linha inteira e: a geometria de timing e real, mas o edge e
   pequeno demais para sobreviver ao accounting honesto de multiplos testes
   (`n_trials = 4377`) `[advances_fin_ml, p.273-275]`.
2. Pendencia que continua valida: escolha de mix da 6A (decision table
   static x satelite) - decisao do usuario, fora do escopo de gates desta
   linha.
3. Leads fracos arquivados para eventual pre-registro futuro: 7E KMLM-only de
   janela longa (1988+); 7C macro gate como redutor de alavancagem (nao como
   switch binario) se um dia houver fonte citavel para a regra de MDD.
4. Nao reabrir grid amplo; nao adicionar familias novas de mecanismo sem
   pre-registro.

## Historico De Trabalho Recomendado Anterior (Phase 6A)

A Phase 6A entrega a tabela de decisao que a pergunta do usuario pedia
(`lrs/phases/phase06a_aftertax_frontier/REPORT.md`). A ordem honesta era:

1. Usuario escolher UM mix da tabela rankeada da 6A (ex.: 75/25 RSC x SPY
   headline, ou 70/30 RSC x QQQ vol-target), ou declarar que nenhum compensa.
2. Pre-registrar a fase de validacao desse mix unico: rodar a suite completa de
   gates do mandate (PBO/DSR/WF/OOS/FWD/bootstrap/xlib) sobre o MIX (nao sobre o
   satelite isolado), com `n_trials >= 4005` cobrindo toda a linhagem.
3. Se (e somente se) os gates passarem, levar ao processo de decisao do mandate
   (SS7 overrides). Sem isso, a 6A fica como diagnostico/decision-table.
4. Nao reabrir grid amplo; nao adicionar familias novas de mecanismo sem
   pre-registro (6B/6D ja cobriram as duas candidatas remanescentes; 6D FAIL).

## Historico De Trabalho Recomendado Anterior

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
