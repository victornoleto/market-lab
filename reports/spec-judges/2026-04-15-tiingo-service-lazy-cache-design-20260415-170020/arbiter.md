# Árbitro — Veredito Consolidado

**Spec:** `docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md`
**Data:** 2026-04-15 17:30
**Veredito final:** **BLOCK**

## Tabela de vereditos por juiz

| Juiz | Veredito | 🔴 crít. | 🟠 alta | 🟡 méd. | 🟢 baixa |
|---|---|---|---|---|---|
| Methodology | BLOCK | 1 | 4 | 4 | 3 |
| Domain | BLOCK | 2 | 3 | 4 | 3 |
| Strategic | PROCEED-WITH-CHANGES | 0 | 3 | 3 | 2 |

## Resumo executivo

Dois dos três juízes emitem **BLOCK** e ambos convergem em duas falhas materiais
que atacam a proposta de valor central do spec — não são detalhes de polimento.
A primeira é a **premissa de retention IEX "tipicamente 2 anos" em §5.2**
contradita por documentação pública (riingo docs, tiingo-python issue #117,
QuantStart) que indica retention rolling de ~2000 pontos (~83 dias em 1h).
Se confirmado, o paradigma "lazy-cache reativo" é o errado — o design correto
seria `scheduled daily-append` (cron que acumula a janela por adição incremental).
A segunda é a decisão **`adj_close := close` em §3.3/§5.6** que re-introduz
exatamente o bug do commit `5ca9410` (Sharpe SPY 0.31 → 0.806 quando corrigido
para adj_close em daily) na camada intraday, **sem citação** das 3 fontes que o
knowledge base já contém (`[quant_trading_chan, p.37]`,
`[trading_systems_methods, p.914]`, `[ml_for_algo_trading, ch.2 p.35-40]`) —
violação direta da Regra 2 inviolável do projeto. O juiz Strategic não
bloqueia porque foca em "fidelidade ao pivô" (infra é neutra), mas levanta 3
dívidas técnicas convergentes com os outros juízes.

**Desbloqueio é mecânico, não redesign completo**: smoke de retention antes do
refactor, mover adj_close de caveat para decisão v1 consciente com citação,
slack per-(asset_class, freq). Mas essas mudanças precisam estar no spec
**antes** do plan ser executado — não como "caveat para v1.1" ou "YAGNI".

## Preocupações consolidadas (deduplicadas, ordenadas por criticidade)

### 🔴 Críticas

1. **Retention IEX factualmente errada em §5.2 — premissa do design está
   invertida** [Methodology 🔴 + Domain 🔴 + Strategic 🟠]
   - Spec afirma "tipicamente 2a em paid tier" sem citação; 3 fontes públicas
     convergentes (`riingo docs`, `tiingo-python #117`, QuantStart) indicam
     "últimos 2000 ticks na frequência pedida" — ~83 dias em 1h.
   - Se confirmado, o cache lazy-reativo captura apenas a janela pedida pelo
     smoke; qualquer backtest posterior com janela mais ampla **sempre**
     retorna `has()=False`. O design correto seria `scheduled append-daily`
     (acumular histórico por iteração), não reativo.
   - Invalida a hipótese §1.3 "cancelar subscrição Tiingo depois" para
     intraday — cada janela nova de backtest requer API.
   - Invalida a partial-fetch semantics §2.5 ("se pedir [2020,2026] e voltar
     [2024,2026]") porque com retention 83d o retorno é sempre "[hoje-83d, hoje]".
   - Smoke #1 em §6.1 é posicionado como gate de execução; os três juízes
     concordam que precisa ser **gate de DESIGN** com critério quantitativo
     explícito ("se retention < X meses → parar e revisar spec").

2. **`adj_close := close` (§3.3, §5.6) re-introduz o bug do commit `5ca9410`
   em intraday** [Domain 🔴 + Methodology 🟡]
   - Commit `5ca9410` documenta que ler `close` não-ajustado inflou Sharpe do
     SPY daily de 0.31 para 0.806 quando foi corrigido para `adj_close`.
   - Spec aceita silenciosamente o mesmo erro em intraday com fallback
     `adj_close := close`. Mitigação "v1.1 emitir warning" é tardia demais:
     v1 já produzirá verdicts de estratégia estatisticamente enviesados
     (splits em NVDA-class tickers mid-window = crash artificial de 50% em
     oscillator Ehlers/Chan).
   - **Viola Regra 2 do CLAUDE.md**: a decisão está apresentada sem citação,
     apesar de 3 fontes diretamente aplicáveis existirem no knowledge base:
     - `[quant_trading_chan, p.37]` — fórmula split/dividend multiplier.
     - `[trading_systems_methods, p.914]` — "split-adjusted stocks lose
       volatility characteristics".
     - `[ml_for_algo_trading, ch.2 p.35-40]` — "dollar bars adjust for price
       level changes (stock splits)".
   - **Solução tecnicamente viável no v1**: o projeto já tem `splitFactor` e
     `divCash` no daily cache (via commit `5ca9410`) — aplicar em
     pós-processamento ao IEX 1h é computacionalmente simples.

### 🟠 Altas

3. **Slack uniforme `_COVERAGE_SLACK_BY_FREQ = {1hour: 1d}` ignora asset
   class** [Methodology 🟠 + Strategic 🟠]
   - Equity regular-hours (6.5 bars/d), crypto 24/7 (24 bars/d), forex
     weekend-close (24/5 Sydney→NY) têm gaps estruturais diferentes — não
     são edge cases, são propriedades do pivô que já foi escolhido (Q6-C:
     todos 3 asset classes em 1h).
   - Caveat §5.7 admite o problema e defere para v2 sem gatilho de observação
     (nada mede "quando isso vai me morder").
   - Ambos juízes propõem a mesma solução: `_COVERAGE_SLACK: dict[tuple[str,
     str], timedelta]` já no v1 (custo: ~5 linhas + 2 testes).

4. **Conflito direto com bulk Tiingo em progresso (MEMORY.md)** [Methodology 🟠]
   - MEMORY `project_tiingo_bulk_in_progress` explicita: "check pgrep +
     manifest before doing anything Tiingo-related" — 1678 tickers ainda
     baixando desde 2026-04-14 22:05.
   - §4 descreve migração via `mv` sem lock, sem checagem de processo ativo.
     Se migrate roda com bulk ainda escrevendo em `data/tiingo/prices/`,
     bulk continua escrevendo no caminho velho **depois** da migração —
     split brain inevitável.
   - Solução: primeira linha de `migrate_to_freq_layout` verificar
     ausência de `pgrep -f tiingo_bulk_download` ou exigir flag
     `--force-ignore-running`.

5. **Rollback não automatizado, não testado, executado pela primeira vez em
   prod se der problema** [Methodology 🟠 + Strategic 🟡]
   - §4.4 diz `cp -r data/tiingo data/tiingo_premigrate_<ts>` é "sugestão
     via docstring". `scripts/tiingo_backup.py` já existe no repo mas não
     é integrado. Nenhum teste exerce o rollback em §6.1.
   - Ambos juízes propõem integração opt-out: backup automático no
     `run_tiingo_migrate.py`, flag `--skip-backup` só se usuário já tem
     externo. Strategic cita existência de `scripts/tiingo_backup.py`.

6. **Partial-fetch re-fetch redundante sem tracking no v1** [Methodology 🟠]
   - §2.5 descreve que wide requests repetidas re-hitam a API a cada call.
     Em retention 83d (preocupação #1), cada re-fetch **sempre** retorna
     "hoje-2000 bars" — não adiciona história, apenas consome rate-limit.
   - `requested_range` marcado como v2 "se > 10% redundância" — sem
     tracking nenhum, não há como medir 10%.
   - Solução proposta: adicionar `requested_range: [first, last]` no manifest
     v1 (custo: 2 campos) + Warning em re-fetch idêntico.

7. **Instrumentação de holding period ausente do spec** [Strategic 🟠]
   - Pivô JORNADA foi gatilhado por Clenow mediana 56d + Ehlers até 4a. Se
     a próxima estratégia 1h segurar 10 dias e ninguém medir, repetimos o
     erro em resolução maior.
   - `engine/portfolio.py:61-62` já persiste `entry_time`/`exit_time` como
     `pd.Timestamp` — a infra de medição **existe**, só não está conectada
     a gate de seleção.
   - Solução: §1.4 nova declarando que estratégias consumindo `1hour`
     DEVEM reportar `median_hold_hours` / `max_hold_hours`. Citação
     `[systematic_trading, p.32-35]`.

8. **Decisões sem citação em violação da Regra 2** [Domain 🟠]
   - `§7.1` marca `[advances_fin_ml, López de Prado]` como **N/A** —
     incorreto: AFML ch.3 cobre adjust-for-splits (dollar bars) e ch.8
     p.223-224 cobre look-ahead bias de retroactive splits. Citações
     diretamente aplicáveis.
   - `§2.4` slack 1d sem justificativa documentada de microstructure.
   - `§5.6` fallback adj_close sem as 3 citações do knowledge base
     listadas na preocupação #2.

### 🟡 Médias

9. **Write amplification em 1min no layout α não validada** [Methodology 🟡]
   - §2.3 rejeita multi-index por write amplification mas layout α escolhido
     sofre o mesmo problema em 1min (~200MB/ticker/2a × 1660 tickers = 300+
     GB). Nenhuma linha do spec afirma aceitável nem propõe partition por
     ano para v2.

10. **Assinatura `has(start: date, end: date)` limita intraday granular**
    [Methodology 🟡]
    - 5m/1min intraday cross-dia não se expressa em `date`. "Extensão
      trivial pós-v1" não é trivial quando call-sites já usam `date`.
      Solução: aceitar `date | datetime` com runtime `isinstance` já no v1.

11. **Convenção de bar timestamp (open vs close) não documentada** [Domain 🟡]
    - §3.3 menciona "datetime com timestamp intradia" sem explicitar
      alinhamento. `[algo_trading_chan, p.4 ch.1]` alerta que ambiguidade
      aqui afeta triple-barrier labels e roofing filter.

12. **Crypto retention não verificado no smoke** [Domain 🟡]
    - Spec assume que `/tiingo/crypto/prices?resampleFreq=1hour` tem
      mesma limitação ou não. Smoke #1 deve incluir probe crypto
      explícito, não só SPY.

13. **Baseline daily adj vs intraday raw invalida comparação** [Domain 🟡]
    - 5 ciclos diários falhados usaram adjClose (yfinance/Tiingo daily).
      Pivô para intraday raw (`adj_close := close`) quebra a comparação
      baseline — não é apples-to-apples.

14. **Migração escreve manifest por último mas não lida com consumer
    concorrente** [Strategic 🟡]
    - Outro processo abrindo `TiingoStorage` durante migração carrega
      manifest velho e procura arquivos que já se moveram → `FileNotFoundError`
      silencioso. Solução: lockfile `data/tiingo/.migration.lock`.

15. **§2.6 tabela posicionada antes do smoke #1 que é gate go/no-go**
    [Strategic 🟡]
    - Se smoke falha, §2.6 e §2.7 precisam ser replan inteiro.

16. **`pyproject.toml "nenhuma mudança"` não verificado contra engine parquet**
    [Methodology 🟡]
    - `pyarrow` vs `fastparquet` têm comportamentos diferentes em índices
      tz-naive datetime sub-day. Sem verificação, afirmação é presumida.

### 🟢 Baixas

17. **Commit único grande** [Methodology 🟢] — quebrar em 3 commits
    (storage / source / migration).
18. **Estimativa 6-7h assume smoke pass** [Methodology 🟢] — falha no smoke
    volta para brainstorm.
19. **`[Tiingo API docs]` sem URL** [Methodology 🟢 + Domain 🟢] — viola
    Regra 2.
20. **`NotImplementedError` para 5m/1min sem "unblock path" documentado**
    [Strategic 🟢] — §6.6 curta com 3 passos.
21. **Primary vs consolidated exchange (IEX)** [Domain 🟢] — citação
    `[algo_trading_chan, p.10-11]` merece 1 linha em §2.6.
22. **`[advances_fin_ml, p.59-62]` time bars vs dollar/tick-imbalance bars**
    [Domain 🟢] — reconhecer trade-off, aceitar para MVP.

## Contradições entre juízes

**Nenhuma contradição material detectada — juízes convergem.**

O veredito divergente (Methodology BLOCK, Domain BLOCK, Strategic
PROCEED-WITH-CHANGES) não é contradição: todos os três juízes levantam as
mesmas preocupações com classificações de criticidade diferentes por lentes
distintas. Methodology e Domain chegam a BLOCK porque classificam a retention
IEX como 🔴 (premissa factual errada); Strategic chega a PROCEED-WITH-CHANGES
porque avalia infra sob a lente "impede o pivô?" (resposta: não) e classifica
o mesmo item como 🟠 (ajuste pré-plan, não impeditivo de design).

**A regra do árbitro em `.claude/agents/spec-judge-arbiter.md §"Regra de
decisão"` é explícita:** qualquer juiz BLOCK OU qualquer 🔴 ⇒ veredito final
BLOCK, independente de soma. Não há cancelamento por contagem — unanimidade
técnica em questões críticas é o gate.

## Razões de bloqueio

Este veredito **não** é "mais trabalho antes de começar"; é "duas premissas
materiais do design precisam ser resolvidas antes que o refactor não sirva
o pivô".

O que o usuário precisa decidir / executar antes de desbloquear:

1. **Executar smoke de retention probe isolado** (sem tocar storage):
   requisitar `/iex/SPY/prices?startDate=2020-01-01&resampleFreq=1hour` e
   medir `first_dt` do que volta. Aplicar o mesmo para `/tiingo/crypto/prices`
   com BTCUSD e `/tiingo/fx/prices` com EURUSD. Output: tabela com
   `observed_retention_bars`, `first_dt`, `last_dt` por endpoint.

2. **Decidir paradigma com base no resultado**:
   - Se retention ≥ 12 meses em 1h para os 3 asset classes → spec atual
     sobrevive com mudanças incrementais (items 3-8 das 🟠).
   - Se retention < 12 meses → **não é lazy-cache reativo**; correto seria
     `scheduled daily-append` (cron diário que anexa N dias, acumula
     histórico por adição) OU decidir trocar fonte para intraday. Spec
     precisa ser re-escrito antes de qualquer refactor.

3. **Reclassificar `adj_close` para decisão v1 consciente** (mover de §5.6
   caveat para §3.3 decisão com citação):
   - Aplicar `splitFactor`/`divCash` do daily cache ao IEX intraday em
     pós-processamento.
   - Se ticker não está no daily cache (ex.: crypto BTCUSD), `NotImplementedError`
     com mensagem clara, não fallback silencioso para `close`.
   - Adicionar citações `[quant_trading_chan, p.37]`,
     `[trading_systems_methods, p.914]`, `[ml_for_algo_trading, ch.2 p.35-40]`,
     `[ml_for_algo_trading, ch.8 p.223-224]`.

4. **Resolver conflito com bulk em execução** antes da migração:
   - `pgrep -f tiingo_bulk_download` check na primeira linha de
     `migrate_to_freq_layout`.
   - Integração com `scripts/tiingo_backup.py` já existente (opt-out,
     não opt-in).
   - Test `test_migration_rollback_restores_layout` novo em §6.1.

Caminhos alternativos sugeridos pelos juízes:
- **Methodology**: promover Smoke #1 a gate de design com critério
  quantitativo explícito em §6.2. Se retention < 12 meses, voltar ao
  brainstorm e considerar scheduled-append.
- **Domain**: gate quantitativo no smoke (retention < 250 bars ~10d ⇒ BLOCK).
  `adj_close` como decisão v1 com splitFactor/divCash do daily cache.
- **Strategic**: condicionar §2.5 ao verdict do smoke; opções: (a) downgrade
  para retention real, (b) trocar fonte, (c) pré-comprar bulk intraday
  enquanto subscrição Tiingo ativa.

## Relatórios individuais

- Engenharia: `reports/spec-judges/2026-04-15-tiingo-service-lazy-cache-design-20260415-170020/methodology.md`
- Domínio:    `reports/spec-judges/2026-04-15-tiingo-service-lazy-cache-design-20260415-170020/domain.md`
- Estratégia: `reports/spec-judges/2026-04-15-tiingo-service-lazy-cache-design-20260415-170020/strategic.md`

## Veredito final

**BLOCK.**

A regra do árbitro é clara: qualquer juiz BLOCK OU qualquer 🔴 força BLOCK,
e aqui temos 2 BLOCKs + 3 🔴 convergentes. O desbloqueio **não é redesign
completo** — é resolver 2 questões antes do plan:

1. **Retention IEX real** via smoke isolado (sem refactor) + atualizar
   hipótese de sucesso v1 + promover Smoke #1 a gate de design com
   critério quantitativo em §6.2.
2. **`adj_close := close` reclassificado para decisão v1 com citação** e
   implementação via `splitFactor`/`divCash` do daily cache (já disponível
   pós commit `5ca9410`).

Adicionalmente, aplicar as 5 ações 🟠 restantes antes do plan (slack
per-(asset_class, freq); guard de bulk em execução; backup automático
opt-out; `requested_range` no manifest v1; instrumentação holding period
como §1.4 nova). Todos são mecânicos, custo ~50-80 linhas de edit no spec
+ 2h de trabalho empírico (smoke retention probe + atualização do spec).

**Próximo passo para o usuário**: rodar o smoke retention probe manualmente
(pode ser script de ~40 linhas reusando `scripts/tiingo_smoke.py` como
base), trazer o output, e decidir entre (a) manter o paradigma lazy-cache
com retention confirmada e aplicar as mudanças 🟠, ou (b) abrir novo
brainstorm para `scheduled-append` se retention < 12 meses. Só depois
re-submeter o spec para `/judge-spec`.
