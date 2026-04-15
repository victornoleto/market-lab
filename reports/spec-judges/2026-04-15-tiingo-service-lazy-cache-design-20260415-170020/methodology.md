# Juiz Adversarial — Engenharia & Metodologia

**Spec:** `docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md`
**Data:** 2026-04-15 17:00
**Veredito:** BLOCK

## Resumo executivo

O spec é estruturalmente bem escrito — TDD-first, escopo explícito,
trade-offs documentados e uma migração idempotente opt-in. A ordem dos
passos respeita "teste → código" e a separação entre refactor de
storage, refactor de source e módulo novo de migração é limpa.

Porém, a decisão central do spec — habilitar intraday com `frequency="1hour"`
via endpoint IEX — se apoia numa **premissa técnica documentalmente
incorreta** sobre retention da API Tiingo. O spec §2.5 e §5.2 afirmam
"tipicamente 2a em paid tier"; a documentação pública Tiingo e múltiplas
fontes independentes confirmam que o endpoint `/iex/{ticker}/prices`
retorna **"os 2000 ticks mais recentes na frequência requisitada"**
(roughly ~83 dias em 1h; ~8 dias em 5m; ~33h em 1min) e **não aceita
`startDate` anterior a hoje − 2000 pontos**. Isso muda radicalmente a
natureza do cache: em vez de "baixou uma vez, cobre dois anos, serve
backtests longos offline", o cache intraday fica sendo "janela rolling
curta que precisa ser re-alimentada continuamente". Sem reconhecer
isso no design, o `has()` e o coverage-slack ficam errados, a decisão
"cancelar a subscrição Tiingo depois" se torna inviável para intraday,
e o Smoke #1 pode "passar" ao baixar 3 tickers recentes e mascarar o
problema. Este é um **BLOCK crítico** até o spec incorporar a retention
real do IEX (ou até a §6.1 Step 1 "live smoke" ser promovida a **gate de
decisão de design, não de execução**, com critério explícito "se retention
< 1 ano, spec é revisado antes de refactor").

Três outros problemas 🟠 somam-se à lente intraday do `--focus`: (a) o
slack de 1d crypto 24/7 é apertado demais (§5.7 admite e passa
buck para v2); (b) o spec menciona 5m/1min apenas como NotImplementedError
sem verificar que o layout α sobrevive ao write-amplification dessas
frequências (parquets 1min podem passar de 400× o tamanho do daily —
o §2.3 menciona isso para descartar multi-index mas não explora o
efeito em 1min no layout escolhido); (c) a migração auto-executa via
`run_tiingo_migrate.py` sem lock de concorrência contra o bulk
(`pgrep` em `tiingo_bulk_download.py` segundo MEMORY.md), o que é
risco real dado que o bulk atual está rodando.

## Preocupações

### 🔴 Críticas (bloqueiam o prosseguimento)

- **[§2.5 + §5.2 + §6.1 Step 1] Retention real do IEX é
  desconhecida/errada no spec, e o smoke não é gate de design.** Fontes
  públicas indicam que o endpoint IEX retorna "últimos 2000 data points
  na frequência requisitada" — ~83 dias em 1h, ~8 em 5m, ~33h em 1min
  ([riingo docs](https://business-science.github.io/riingo/reference/riingo_iex_prices.html),
  [QuantStart](https://www.quantstart.com/articles/evaluating-data-coverage-with-tiingo/)).
  Isso invalida três pilares do design:
    1. A hipótese §5.2 "tipicamente 2a" está factualmente errada segundo
       fontes públicas e não há citação Tiingo direta que a confirme.
    2. O argumento §1.3 "bulk daily + qualquer intraday já baixado ficam
       no disco, subscription cancelável" é inválido para intraday —
       cada vez que o backtest precisa de uma janela nova intraday, a
       API é necessária; o cache não protege contra cancelamento.
    3. Em §6.1 Step 1 ("live smoke" como primeiro passo), o checkpoint
       §6.2 ("3 tickers retornam ≥1 bar cada com shape canonical")
       **não testa retention** — vai passar mesmo com janela de 83 dias
       só, e só depois, no Smoke #2, é que o usuário descobre que os
       backtests longos intraday não têm como existir com os dados
       persistidos hoje.

  **Impacto:** toda a proposta de valor do "lazy-cache intraday" se
  apoia no assumption implícito de que o cache acumula história útil ao
  longo do tempo. Com retention rolling de 83 dias em 1h, o cache
  captura somente a janela que o smoke está pedindo no momento —
  qualquer backtest posterior que pedir janela anterior terá
  `has()=False` permanentemente.

  **Sugestão:** antes de PROCEED, o spec precisa:
    - Reescrever §5.2 com citação Tiingo direta, não "docs públicos
      indicam".
    - Promover o Smoke #1 a **gate de design**: executar uma probe que
      pede `[today-5y, today]` em 1h e mede o que volta. Critério de
      aceite: se retention < 1 ano, **parar** e revisar plan — talvez o
      caminho certo seja um **scheduled daily append** (cron que puxa os
      últimos N dias todo dia, constrói a série histórica por
      acumulação) e não um lazy-cache reativo. Isso muda o design,
      não só um parâmetro.
    - Adicionar à hipótese §1.3 de sucesso v1 um item explícito:
      "retention observada do endpoint IEX é compatível com backtest
      de ≥ N meses em 1h" (onde N é escolhido pelo usuário — Chan
      mean-reversion tipicamente quer 2-3 anos).
    - Reexaminar o plano de cancelamento de subscrição (§6.5 item 4):
      tornar explícito que **cancelamento fecha intraday** e só é
      seguro para daily.

### 🟠 Altas (devem mudar antes de prosseguir)

- **[§2.5 coverage slack partial-fetch] Comportamento documentado é
  patológico e aceito como YAGNI v1.** O spec descreve que wide
  requests repetidas re-hitam a API a cada chamada (`first_dt > start +
  1d ⇒ re-fetch`). Em um grid de backtest com múltiplas estratégias ou
  múltiplas janelas sobrepostas, isso *multiplica* chamadas HTTP
  desnecessárias — e no cenário da preocupação 🔴 (retention 83d),
  **cada re-fetch rebaixa o first_dt ainda mais para "today-2000"**, não
  adicionando história. O `requested_range` é marcado como v2 "se >10%
  redundância", mas sem tracking nenhum, não há nem como *medir* 10%.

  **Sugestão:** adicionar no manifest v2 o campo `requested_range: [first,
  last]` já no v1 (custo mínimo: 2 campos extra) e loggar Warning quando
  re-fetch idêntico acontece. Isso dá evidência empírica antes de decidir
  v2. Custo de implementação: ~10 linhas, cabe no refactor de storage.

- **[§5.7 Crypto 24/7 slack] `_COVERAGE_SLACK_BY_FREQ = {1hour: 1d}`
  único para equity regular-hours + crypto 24/7 é errado no mercado
  intraday real.** Crypto 1h tem 24 bars/dia; equity 1h tem 6.5
  bars/dia (9:30-16:00). Um slack de 1 dia calendário esconde:
  **24 bars faltando em crypto** (um dia inteiro) vs **6-7 bars em
  equity**. A lente do pivô é exatamente short-hold intraday — 24 bars
  de gap em BTCUSD 1h cobre 1 dia de trading e potencialmente uma
  inversão completa de regime. A confissão §5.7 "se observamos edge
  cases reais, override em v2" deixa o bug esperando para ser
  descoberto por um backtest que já rodou errado.

  **Sugestão:** `_COVERAGE_SLACK_BY_FREQ` deve ser keyed por
  `(asset_class, frequency)` já no v1 — ex.:
  `{("equity","1hour"): 1d, ("crypto","1hour"): 2h, ("forex","1hour"): 4h}`.
  Tabela e citação da estrutura regular-hours vs 24/7 já está implícita
  em §2.6 (matriz de endpoints), então a informação existe.

- **[§4 Migração + bulk em progresso] Conflito com o bulk rodando
  (MEMORY.md `project_tiingo_bulk_in_progress`).** O MEMORY do usuário
  explicita: "Tiingo bulk in progress — 1678 tickers downloading to
  data/tiingo/ since 2026-04-14 22:05; check pgrep + manifest before
  doing anything Tiingo-related". A §4 do spec descreve migração
  **mecânica via `mv`** sem lock, sem verificação de processo ativo, e
  sem como lidar com writes concorrentes do bulk durante a migração.
  Se alguém rodar `run_tiingo_migrate.py --dry-run` → inspecionar →
  `run_tiingo_migrate.py` enquanto o bulk ainda estiver ativo, o bulk
  continua escrevendo em `data/tiingo/prices/` (caminho velho) depois
  da migração mover arquivos — resultado: split brain, arquivos em dois
  lugares, manifest inconsistente.

  **Sugestão:** em `migrate_to_freq_layout`, primeiro passo: verificar
  ausência de processos tiingo bulk (ex.: `pgrep -f tiingo_bulk_download`)
  ou requerer flag `--force-ignore-running` explícita. Mesma verificação
  no dry-run, pra não dar falso positivo no plan. Documentar em §4.3
  "Invocação" que migração requer bulk parado.

- **[§5.5 rollback manual] "Backup manual + docstring" não é backup
  automatizável e não há teste de rollback.** O spec diz `cp -r` pré-
  migração é "forte recomendação". Para 145 MB isso é rápido, mas o
  test suite proposto em §6.1 Step 2 **não tem um teste que exerce o
  rollback** (test_real_migration_moves_files_and_rekeys_manifest só
  testa forward). Resultado: se a migração real der problema, o usuário
  executa o procedimento de rollback pela primeira vez **em prod**, sem
  nunca ter sido testado.

  **Sugestão:** adicionar `test_migration_rollback_restores_layout` em
  §6.1 Step 2 — que simula falha transacional (disco cheio ou equivalent
  via monkeypatch do `_save_manifest`), verifica que arquivos não foram
  movidos permanentemente, e que um `restore_pre_migration(root, backup)`
  helper (novo) funciona. Ou, alternativa mais simples: mudar o backup
  de "sugestão via docstring" para "primeira coisa que `run_tiingo_migrate.py`
  faz por padrão" — automatize o backup, mais difícil de esquecer.

### 🟡 Médias (recomendado mudar)

- **[§2.3 layout α + §6.4 "5m/1min deferred"] Write amplification em
  1min não foi verificada no layout escolhido.** O spec menciona 400×
  bars vs daily para rejeitar multi-index, mas o layout α escolhido
  também sofre: um único arquivo `data/tiingo/1min/prices/SPY.parquet`
  de um ticker ativo com 2 anos de dados 1min pode chegar a ~200MB+
  por ticker. Para 1660 tickers isso é 300+ GB. O spec não afirma que
  isso é aceitável ou que haverá particionamento por data em v2 —
  fica latente.

  **Sugestão:** adicionar §2.3 uma linha: "layout α é uniforme em v1
  (daily+1hour); quando 1min/5m entrarem em v2, cada arquivo parquet
  será particionado por ano para evitar write amplification (ex.:
  `1min/prices/SPY/2024.parquet`, `SPY/2025.parquet`)". Isso não muda o
  v1 atual, só registra a decisão antes que o layout α "prenda o projeto
  em 1h" — exatamente uma das preocupações do `--focus`.

- **[§2.4 backwards-compat do `has()`] `start: date, end: date` +
  conversão tz-naive à meia-noite é subtle-buggy para intraday futuro.**
  A assinatura `has(ticker, start: date, end: date, frequency)` promove
  `date` para `datetime at midnight` e compara com `first_dt/last_dt`
  nos manifests. Para 1h isso funciona. Para 5m/1min, um backtest
  cross-dia começando às 09:30 e terminando às 16:00 não pode expressar
  essa granularidade via `date` — ou o call-site passa janelas
  folgadas demais (pedindo dia todo) ou a interface precisa de sobrecarga.
  O spec diz "Aceitar `datetime` diretamente é extensão trivial pós-v1"
  mas isso **não é trivial** quando os call-sites existentes passam
  `date` objects — aceitar ambos tipos é mais bagunça que benefício.

  **Sugestão:** já no v1 mudar a assinatura para `start: date | datetime,
  end: date | datetime`, com runtime `isinstance` check. Zero overhead,
  call-sites existentes continuam funcionando, e estratégias intraday
  futuras não precisam esperar refactor de interface. Custo: 3 linhas a
  mais + 1 teste novo.

- **[§3.1 pyproject.toml "Nenhuma mudança"] Afirmação não-verificada.**
  O spec afirma "sem dependências novas" mas não lista explicitamente o
  que já existe (`pandas`, `requests`, `pyarrow`/`fastparquet`) e se a
  leitura parquet intraday funciona com o engine atual em índices tz-naive
  com datetime. `pd.read_parquet` tem comportamentos diferentes entre
  `pyarrow` e `fastparquet` para índices datetime tz-naive com granularidade
  sub-day. Sem verificar o engine, a afirmação é presumida.

  **Sugestão:** §3.1 ou §6.1 Step 3 deve incluir "verificar engine parquet
  ativo + um test `test_write_intraday_read_roundtrip_preserves_minute_granularity`".

- **[§5.6 IEX sem adjClose] Decisão `adj_close := close` é silenciosa
  para o pipeline downstream.** O adjust_ohlc utility do projeto e o
  Ehlers BP Swing dependem de adj_close para ajustar splits/dividendos.
  Em IEX 1h sem ajuste, um split 2-for-1 num ticker como NVDA mid-window
  vira um crash artificial de 50% no oscilador. §5.6 admite isso mas
  defere o warning para v1.1. **Lente `--focus` do spec é intraday
  short-hold viável**: rodar Ehlers BP 1h numa janela que contém split
  produz resultado estatisticamente enviesado. Se o warning fica em
  v1.1, v1 pode produzir verdicts de estratégia ruins.

  **Sugestão:** minimamente, adicionar ao v1 uma checagem que **emite
  Warning no `fetch()` com frequency=1hour se o ticker teve split no
  manifest daily do mesmo range** — logs + docstring explicitando o
  risco. Se daily não está no cache, apenas Warning genérico "IEX não
  ajusta splits — verifique o ticker manualmente". Custo: ~10 linhas.

### 🟢 Baixas (opcional)

- **[§7.1 referências]** `[Tiingo API docs]` é citação sem URL — viola
  a Regra 2 inviolável do projeto de citação específica. Deve virar
  `[tiingo.com/documentation/iex]` ou similar URL concreta.

- **[§6.1 Step 8 commit message]** "feat(data): tiingo_service lazy-cache
  with 1h intraday support" — esse commit vai acumular refactor de
  storage + source + novo módulo de migração + novo smoke script, é um
  commit grande. Considerar: quebrar em (1) `feat(data): add frequency
  axis to tiingo storage`, (2) `feat(data): route tiingo source to IEX
  for 1h intraday`, (3) `feat(data): tiingo_migrate script for legacy
  layout`. Cada commit é reversível isoladamente.

- **[§6.3] Estimativa 6-7h** assume tudo corre sem smoke falhar. Se a
  preocupação 🔴 sobre retention se materializa no Smoke #1, a sessão
  termina sem refactor e com um novo ciclo de brainstorming — o spec
  deveria dizer isso explicitamente na §6.2.

## Pontos fortes

- **TDD ordering é exemplar** — §6.1 lista testes antes da implementação
  em cada step, nomes de teste são específicos e cobrem happy path +
  error paths + boundaries.
- **Separação de concerns é clara** — storage / source / migration são 3
  módulos distintos, cada um testa um contrato isolado.
- **Backwards-compat para daily** é preservado via `frequency="daily"`
  default. Todos os 7 call-sites em `scripts/` (levantados via Grep:
  `run_clenow_replication`, `run_grid_clenow`, `run_grid_ehlers`,
  `run_grid_ehlers_meta`, `run_ehlers_replication`,
  `run_portfolio_combined`, `tiingo_bulk_download`) continuam
  funcionando sem edit.
- **Migração explicitamente opt-in** — nunca auto no
  `TiingoStorage.__init__`. Decisão correta.
- **Escopo v1 é disciplinado** — whitelist `{daily, 1hour}` evita o
  over-engineering de tentar 5m/1min já v1.
- **§6.4 "Fora de escopo" é extensivo e honesto** — reconhece 8 itens
  deferidos com racional.
- **Trade-offs documentados** — §2.1 (refactor in place), §2.3 (layout
  α vs alternativas), §2.5 (partial-fetch semantics) têm tabelas de
  rejeição explícitas.

## Sugestões concretas

1. **§2.5 + §5.2 + §6.1 Step 1 — Promover Smoke #1 a gate de design.**
   Antes de qualquer refactor, rodar probe que mede retention real do
   `/iex/{ticker}/prices` com `startDate=today-5y`. Critério de aceite
   explícito na §6.2: "retention observada ≥ 12 meses em 1h — caso
   contrário, voltar ao brainstorm e considerar design cron-append
   (scheduled append-daily) em vez de lazy-cache reativo".
   Justificativa: docs públicos ([riingo](https://business-science.github.io/riingo/reference/riingo_iex_prices.html),
   [QuantStart](https://www.quantstart.com/articles/evaluating-data-coverage-with-tiingo/))
   indicam retention de 2000 pontos (~83 dias em 1h); se isso se
   confirmar, o design de cache precisa mudar, não só um parâmetro.

2. **§2.4 — Tornar slack keyed por `(asset_class, frequency)` já no v1.**
   Substituir `_COVERAGE_SLACK_BY_FREQ = {"daily": 7d, "1hour": 1d}`
   por `_COVERAGE_SLACK_BY_AC_FREQ = {("equity","daily"): 7d,
   ("crypto","daily"): 2d, ("equity","1hour"): 12h, ("crypto","1hour"):
   2h, ("forex","1hour"): 4h}`. Justificativa: crypto 24/7 e forex
   24/5 têm gaps estruturalmente diferentes de equity regular-hours; um
   único slack global mascara realidade.

3. **§4.1 — Adicionar guard de concorrência com o bulk.**
   Primeiro passo de `migrate_to_freq_layout`: `if pgrep_bulk_tiingo():
   raise RuntimeError("bulk download ativo; migração bloqueada")`. Ou
   flag opt-in `--force-ignore-running`. Justificativa: o próprio
   MEMORY.md do usuário alerta "check pgrep + manifest before doing
   anything Tiingo-related" — o spec ignora esse estado ativo.

4. **§4 + §6.1 Step 2 — Automatizar backup no script + teste de
   rollback.** Tornar `cp -r data/tiingo data/tiingo_premigrate_<ts>`
   comportamento default de `run_tiingo_migrate.py`, com flag
   `--no-backup` para opt-out consciente. Adicionar teste
   `test_migration_rollback_restores_layout` simulando falha
   transacional via monkeypatch em `_save_manifest`. Justificativa:
   "sugestão via docstring" não é backup; e rollback não testado é
   rollback que funciona pela primeira vez em prod.

5. **§2.5 — Adicionar `requested_range` no manifest v1, não v2.** Custo:
   ~10 linhas, evita re-fetch redundante em wide-request patterns e
   cria evidência empírica antes de decidir v2.
   Justificativa: sem tracking, não há como medir "10% redundância"
   que o spec usa como gatilho de v2.

6. **§2.4 — Aceitar `start|end: date | datetime` já no v1.**
   3 linhas via `isinstance` check. Justificativa: evita refactor de
   interface quando estratégias intraday granulares (5m/1min) vierem,
   e é fielmente backwards-compat com o que existe.

7. **§5.6 — v1 emite Warning de split para IEX 1h.** Cruzar ticker+range
   com manifest daily (splitFactor ≠ 1.0 em alguma row do range ⇒
   warning). Justificativa: sem o warning, backtest 1h em ticker com
   split produz resultado estatisticamente enviesado silenciosamente —
   contradiz a lente `--focus` "viabilizar intraday short-hold".

8. **§7.1 — Converter `[Tiingo API docs]` em URL concreta.**
   `[https://www.tiingo.com/documentation/iex]` ou equivalente.
   Regra 2 inviolável do projeto.

## Evidência externa consultada

### Arquivos do projeto
- `/var/www/pessoal/ai-trade/docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md` — spec em revisão.
- `/var/www/pessoal/ai-trade/.claude/CLAUDE.md` — convenções do projeto (TDD, citação, não-quebrar baseline 377 testes, Conventional Commits).
- `/var/www/pessoal/ai-trade/JORNADA.md` — pivô 2026-04-15 noite, motivação intraday short-hold.
- `/var/www/pessoal/ai-trade/ROADMAP.md` — §"Current status" + §"Next steps", deixa claro que `tiingo_service` é próximo.
- `/var/www/pessoal/ai-trade/src/ai_trade/backtest/data/tiingo_storage.py` — código atual; confirma `_COVERAGE_SLACK=7d` único, layout `{prices,meta}/{ticker}`, chave root do manifest `= ticker`.
- `/var/www/pessoal/ai-trade/src/ai_trade/backtest/data/tiingo_source.py` — `_build_url`/`_build_params` hard-code daily como spec afirma.
- `/var/www/pessoal/ai-trade/tests/test_tiingo_source.py` + `tests/test_tiingo_storage.py` — pattern de mock HTTP + tmp_path + parquet fixtures; spec segue o padrão.
- `/var/www/pessoal/ai-trade/scripts/tiingo_bulk_download.py:254-283` — confirma call-site do bulk usa `storage.has(ticker, args.start, args.end)` sem kwarg `frequency`; backwards-compat do spec é válida.
- `/var/www/pessoal/ai-trade/data/tiingo/manifest.json` — schema velho confirmado: root keys = tickers, `first_date`/`last_date` string ISO `YYYY-MM-DD`, sem nesting por freq.
- `/var/www/pessoal/ai-trade/scripts/tiingo_smoke.py` — spec segue o mesmo padrão (`_BASE = https://api.tiingo.com/tiingo/daily`, load key, 3 probe cases).
- `/home/victor/.claude/projects/-var-www-pessoal-ai-trade/memory/MEMORY.md` — `project_tiingo_bulk_in_progress` é ativo; spec ignora.

### Web
- [riingo_iex_prices — business-science.github.io](https://business-science.github.io/riingo/reference/riingo_iex_prices.html): "returns the most recent 2000 ticks of data at the specified frequency" — contradiz spec §5.2 "tipicamente 2a".
- [QuantStart — Evaluating Data Coverage with Tiingo](https://www.quantstart.com/articles/evaluating-data-coverage-with-tiingo/): mesma limitação 2000 ticks rolling; historical intraday começa em 2016.
- [GitHub tiingo-python issue #117](https://github.com/hydrosquall/tiingo-python/issues/117): URL example `/iex/aapl/prices?startDate=2018-5-22&resampleFreq=5min` — valida formato do endpoint conforme §2.6 do spec.
- [Tiingo IEX docs page](https://www.tiingo.com/documentation/iex): URL existe mas conteúdo retornado via WebFetch é só o header — impede verificação mais profunda sem auth.

## Veredito

**BLOCK**

**Regra aplicada:**
- PROCEED = zero preocupação 🔴 ou 🟠.
- PROCEED-WITH-CHANGES = zero 🔴, pelo menos uma 🟠.
- BLOCK = pelo menos uma 🔴.

Preocupação crítica dominante: a premissa de retention Tiingo IEX "tipicamente 2a"
contradiz documentação pública que indica retention rolling de ~2000 data points
(~83 dias em 1h). Se confirmado no smoke, o design "lazy-cache" não atende o caso
de uso intraday — seria necessário mudar para scheduled-append. O Smoke #1 do §6.1
precisa ser promovido a **gate de decisão de design**, não apenas de execução,
antes que qualquer refactor seja feito.
