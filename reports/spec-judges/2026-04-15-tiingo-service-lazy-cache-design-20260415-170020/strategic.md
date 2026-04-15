# Juiz Adversarial — Fidelidade Estratégica

**Spec:** `docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md`
**Data:** 2026-04-15 17:15
**Veredito:** PROCEED-WITH-CHANGES

## Resumo executivo

O spec é genuinamente alinhado com o pivô: refactor in place do `tiingo_source`/
`tiingo_storage` para aceitar `frequency=1hour`, com layout `{freq}/prices/{ticker}.parquet`
e manifest nested. A decisão de v1 ficar em `{daily, 1hour}` é defensável como MVP.
**Mas há cinco riscos que empurram o projeto para perto da fronteira entre "habilita
intraday" e "esconde dívida técnica contra minutos-horas"**: (i) ausência total de
instrumentação de *holding period* no próprio spec — viabilizar bars ≠ medir duração
de trade; (ii) slack `_COVERAGE_SLACK_BY_FREQ = {1hour: 1d}` único para equity/crypto/
forex (crypto 24/7 vs equity regular hours coexistem no mesmo dict); (iii) suposição
`§2.5` de "retention tipicamente 2a" não é confirmada — fontes externas indicam janela
IEX rolling de 2000 bars (~83 dias em 1h); (iv) migração automática sem backup
automático é point-of-no-return na prática; (v) `NotImplementedError` para 5m/1min
é guardrail útil mas a "próxima estratégia" pode precisar 5m imediatamente, e o spec
não tem seção de "como desbloquear em 1 dia".

## Alinhamento com o pivô

| Aspecto | Spec respeita? | Evidência |
|---|---|---|
| Habilita/preserva intraday | **Sim** | §1.3, §2.6: `frequency="1hour"` dispara para IEX/resampleFreq; layout `{freq}/prices/{ticker}.parquet` isola paths; `tiingo_source.py:82` já produz `DatetimeIndex` tz-naive (minute-granular quando bars são intraday). |
| Não gera swap risk adicional | **Sim (infra neutra)** | Infra não seleciona estratégia nem altera holding period. Os trades continuam abertos pela estratégia consumidora. |
| Permite medir holding period | **Parcial** | `engine/portfolio.py:61-62` JÁ tem `entry_time`/`exit_time` como `pd.Timestamp` → quando bars são 1h o diff dá minutes. **Mas o spec não menciona isso, nem propõe gate de duração** (ex.: "rejeita configs com mediana > 3 dias"). Ver 🔴 #1. |
| Compatível com cTrader future | **Sim** | Schema OHLCV 6-col é o mesmo do `ProtoOAGetTrendbarsReq`. `frequency` como eixo do storage encaixa direto em `M1/M5/H1/D1` do cTrader Open API (§Phase 1 ROADMAP). |
| Gates anti-overfit intocados | **Sim** | Infra não toca CPCV/PBO/DSR/WF. N_trials determinado pelas estratégias consumidoras. |

## Preferências recentes do usuário que este spec respeita/viola

O usuário reafirmou nos **últimos turnos**:

1. **Preocupação com swap Pepperstone** → spec é infra, não carrega swap por si só, **mas também não equipa o projeto com ferramentas para detectar violação**. Um Chan pairs em 1h que segurar posição por 10 dias passa silencioso se ninguém mede hold duration. O `engine/portfolio.py` tem os timestamps; o spec deveria citar isso e adicionar assert/metrica no pipeline de report. **Respeita parcialmente**.
2. **Escolheu Q6-C (todos 3 asset classes em 1h)** → spec entrega: equity via IEX, crypto via `/tiingo/crypto/` + `resampleFreq=1hour`, forex via `/tiingo/fx/` (§2.6). **Respeita**.
3. **"Infra destrava intraday SEM criar atrito futuro"** → *parcialmente viola*: o `_COVERAGE_SLACK_BY_FREQ` único sem eixo de asset_class é um futuro bug sutil para crypto 24/7 (§5.7 admite o caveat mas não mitiga) e a ausência de estratégia de backup para migração é atrito de ops (§4.4 manda copiar à mão antes).

## Preocupações

### 🔴 Críticas (bloqueiam — spec empurra o projeto para trás)

Nenhuma crítica bloqueante **neste escopo de infra**. A infra é neutra em relação à fronteira do pivô. As preocupações são altas/médias, não bloqueantes.

### 🟠 Altas (dívida técnica significativa)

1. **Spec é silencioso sobre instrumentação de holding period** (§1.3, §6.4). O gatilho do pivô (JORNADA 2026-04-15 noite) foi exatamente detectar que Clenow mediana 56d e Ehlers até 4a. Se a próxima estratégia 1h mantiver posição 10 dias e ninguém medir, repetimos o mesmo erro em resolução maior. **O spec deveria citar** que `engine/portfolio.py:61-62` já persiste `entry_time`/`exit_time` como `pd.Timestamp` e **propor um gate explícito** (ex.: "qualquer estratégia consumindo `frequency="1hour"` DEVE reportar `median_hold_hours` e `max_hold_hours` no diagnostic, com threshold de alerta"). Sem isso, este infra vira ponte neutra quando poderia ser ponte com guard-rail. `[systematic_trading, p.32-35]` — skew de custo vs frequência deveria motivar esse instrumento.

2. **Suposição de retention IEX "tipicamente 2 anos" não confirmada (§2.5, §5.2).** Busca externa encontrou duas leituras conflitantes: "2000 ticks rolling = ~83 dias em 1h" vs "IEX 1min desde 2017" ([Tiingo IEX docs](https://www.tiingo.com/documentation/iex)). Para paid tier, a janela real precisa de probe. O spec **corretamente** elege smoke como primeiro passo, mas a §2.5 arquiteta partial-fetch semantics ("se pedir [2020,2026] e voltar [2024,2026]") que só faz sentido em cenário "retention > 1a". Se o smoke voltar 83 dias de retention, o partial-fetch é irrelevante e o spec precisa revisão antes do refactor. **Recomendação:** condicionar §2.5 ao verdict do smoke #1, colocando §2.5 como "se retention ≥ 1 ano, este é o policy; senão, entrar no branch de `short_window_policy` TBD". Ou: documentar que retention < 1a é blocker para usar Tiingo em 1h e precisa pivotar para outra fonte.

3. **`_COVERAGE_SLACK_BY_FREQ = {1hour: 1d}` unified across asset classes** (§2.4, caveat §5.7). Crypto é 24/7, equity é 6.5h/dia × 5d. Um slack de 1 dia de calendário em crypto é ~24 bars "buffer" (aceitável); em equity é ~6.5 bars (também aceitável); **mas em forex intraday** (24h/5d, Sydney→NY) a semana tem gap estruturalmente. §5.7 admite mas deixa para "v2 se houver problema". Com o pivô, isso é estrutural, não edge case. **Recomendação:** mudar para `_COVERAGE_SLACK_BY_FREQ_AND_CLASS: dict[tuple[str, str], timedelta]` agora. Custo: 5 linhas de código, 2 testes a mais. Benefício: não acumular dívida em camada que o usuário já identificou.

### 🟡 Médias (risco gerenciável)

4. **Migração "opt-in" mas sem `tiingo_backup.py` integrado** (§4.3, §4.4). O script `scripts/tiingo_backup.py` já existe no repo. A doc da §4.4 diz "sugestão: `cp -r data/tiingo ...`" — mas esse é um `cp` manual sem checksum, mesmo tendo um script oficial de backup. **Recomendação:** `scripts/run_tiingo_migrate.py` deve rodar `tiingo_backup.py` como primeiro passo opt-out (flag `--skip-backup`), não opt-in. Operações sobre 1660 arquivos sem backup automático são o clássico "vai dar certo, até não dar".

5. **Migração escreve manifest "por último"** (§4.1 passo 7) — boa prática, mas o spec não descreve o **estado intermediário observável** por um consumer externo que abra a instância DURANTE a migração. Se outro processo faz `TiingoStorage(root=data/tiingo)` enquanto o script está movendo arquivos, o `__post_init__` carrega manifest velho, mas os arquivos já se moveram → `read()` levanta `FileNotFoundError` silenciosamente. **Recomendação:** adicionar test `test_migration_is_not_interruptible_safe` e documentar que o user DEVE parar processos consumidores antes. Alternativa: lockfile `data/tiingo/.migration.lock`.

6. **1h para equity via `/iex/` URL não verificada (§5.1)** é caveat conhecido e mitigado pelo smoke #1 como gate go/no-go. **Mas §2.6 mostra que o spec já assume essa URL em muitos lugares** (§2.6 tabela, §2.7 diagrama de componentes). Se smoke #1 falhar, trabalho de refactor já descrito vira "replanejar §2.6 + refazer §2.7 + refazer plan". Isso é honesto na §6.1 ("se 404 → parar e revisar"), só que a §2.6 está posicionada ANTES do smoke na ordem de leitura. **Recomendação:** mover tabela §2.6 explicitamente depois de smoke #1 no plan de execução ou adicionar um disclaimer inline.

### 🟢 Baixas (observação de futuro)

7. **Layout `{freq}/prices/{ticker}.parquet` para 1min** — dimensionamento (§2.3 rejeita multi-index por write amplification): 1 ticker 10 anos 1min = ~1M bars; 24/7 (crypto) = ~5M bars. Em ~48B/row isso é 50-250MB por parquet **em um único arquivo**. Não trivial, mas funciona — `pd.read_parquet` é rápido, slicing via `pd.DatetimeIndex` é O(log n). Sub-options para o futuro (se 5m/1min entrarem): partition por ano (`{freq}/prices/{ticker}/{year}.parquet`), formato delta-lake. Não precisa resolver agora.

8. **`NotImplementedError` para 5m/15m/1min é guardrail forte, mas não tem "unblock path" documentado** (§6.4). Se amanhã o Chan pairs precisar de 5m (Chan recomenda `[algo_trading_chan, p.94]` mean-reversion com "gap open to mid-morning" em escala de minutos), o spec diz "whitelist de 1 linha + fixtures". OK, mas isso deveria ser uma seção "§6.6 — Como adicionar frequência nova em 30 min" para não virar obstáculo psicológico para o próximo engenheiro. **Recomendação:** adicionar checklist curto (3 passos) em §6.4.

## Pontos fortes (estratégia)

1. **Refactor in place** (§2.1) evita criar módulo paralelo `tiingo_service.py` que duplicaria auth + 404 handling — escolha arquitetural correta sob a lente de "não criar dívida para fases futuras (Phase 4 paper → Phase 5 live)".

2. **Frequency como eixo first-class** no layout (`{freq}/prices`) casa 1-para-1 com `ProtoOAGetTrendbarsReq` timeframes (M1/M5/H1/D1) do cTrader Open API. Quando Phase 4 for ligar cTrader demo, a mesma abstração serve.

3. **Migração opt-in + dry-run** (§4.3, §6.1 passo 2) respeita política do projeto (scripts longos + log unificado `[memory: unified_log]`).

4. **Spec cita fontes do projeto coerentemente** (§7.2) — CLAUDE.md, JORNADA.md, ROADMAP.md. Regra 2 respeitada na letra, mesmo para infra (`§7.1` marca `advances_fin_ml` como N/A para infra sem gate estatístico, o que é honesto).

5. **v1 escopo 1h-only é disciplina MVP.** Evita tentação de resolver 5m/1min em mesma iteração e acoplar risk (fixtures novos, retention probing, edge cases de weekends em FX).

## Sugestões concretas

1. **§1.3 + §6.2 — Adicionar critério de holding period.** Nova seção §1.4 "Instrumentação de holding period (downstream requirement)": "O `engine/portfolio.py:61-62` já persiste `entry_time`/`exit_time` como `pd.Timestamp`. Este infra é NEUTRO quanto a holding period — responsabilidade das estratégias consumidoras. Padrão do projeto pós-pivô: todo diagnostic de estratégia intraday reporta `median_hold_hours`, `max_hold_hours`, com alerta `[systematic_trading, p.32-35]` se `median_hold > 48h`. Gate futuro: configs com `median_hold > 72h` em intraday são candidatas a DESCARTE antes mesmo de rodar DSR/PBO (economia de compute)." **Motivação:** garantir que o próximo spec de estratégia não "esquece" o pivô.

2. **§2.5 + §5.2 — Tornar retention explicitamente condicional.** Reescrever §2.5 como: "Se smoke #1 confirma retention ≥ 1 ano: aplicar política descrita abaixo. Se retention < 1 ano (rolling 2000 bars): revisitar spec antes de prosseguir — partial-fetch e backtest de 2015-2023 ficam inviáveis e precisamos decidir: (a) downgrade para retention real, (b) trocar fonte, (c) pré-comprar bulk intraday enquanto a subscrição Tiingo está ativa." **Motivação:** pivô exige dados intraday com runway suficiente para CPCV/PBO com N_trials razoável.

3. **§2.4 + §5.7 — Slack per-(asset_class, freq) agora.** Mudar `_COVERAGE_SLACK_BY_FREQ: dict[str, timedelta]` para `_COVERAGE_SLACK: dict[tuple[str, str], timedelta]` com entradas:
   - `(equity, 1hour): 1 day` (regular hours + weekend)
   - `(etf, 1hour): 1 day`
   - `(crypto, 1hour): 6 hours` (24/7 → weekend nem existe)
   - `(forex, 1hour): 2 days` (fecha fim-de-semana sex 22h UTC → dom 22h UTC, Pepperstone spec)
   - Daily: mantém 7 days para todos.

   **Motivação:** crypto 24/7 e forex weekend-close são propriedades estruturais do pivô, não edge cases.

4. **§4.3 — Backup automático opt-out, não opt-in.** Mudar `scripts/run_tiingo_migrate.py` para rodar `python scripts/tiingo_backup.py` como primeiro passo; expor flag `--skip-backup` para o caso em que o usuário já tem backup externo. **Motivação:** ops sobre 1660 arquivos.

5. **§6.4 — Adicionar mini-checklist "§6.6 Unblock intraday < 1h freq".** 3 passos concretos:
   - Adicionar entrada no `_WHITELIST` de `tiingo_source.py`
   - Adicionar fixture 5-linha no `tests/test_tiingo_source.py`
   - Confirmar `_COVERAGE_SLACK` para nova freq (menor que bars × slack anterior)

   **Motivação:** `NotImplementedError` vira muro se o unblock não está documentado em passos explícitos.

## Evidência consultada

### Artefatos do projeto

- `JORNADA.md §"Pivô: intraday short-hold"` (L177-228): gatilho do pivô = Clenow mediana 56d + Ehlers até 4a. Confirma que "medir holding period" é o problema matricial.
- `ROADMAP.md §"Current status"` (L25-40): pivô documentado; `tiingo_service` é o item 1 do backlog pós-pivô.
- `src/ai_trade/backtest/engine/portfolio.py:61-62,74,111,151-152,159`: `entry_time` / `exit_time` já como `pd.Timestamp` — a infra DE MEDIÇÃO de hold period existe, só não está conectada ao gate de seleção.
- `src/ai_trade/backtest/data/tiingo_source.py:72,82`: `_normalize` faz `pd.to_datetime(...).dt.tz_localize(None)` e usa `adjClose` com default para `close` — confirma que datetime granularity existe no pipeline (minute-level quando bars forem intraday) e que IEX sem `adjClose` cai para `close` (caveat §5.6 do spec).
- `src/ai_trade/backtest/data/tiingo_storage.py:95-111`: `_COVERAGE_SLACK = timedelta(days=7)` global — confirma o gap que o spec corrige, mas a proposta `{daily:7d, 1hour:1d}` ainda não cobre asset_class.
- `data/tiingo/manifest.json:1-60`: schema atual achatado `{ticker: {first_date, last_date, n_bars, asset_class}}` → confirma que a migração descrita em §4 é mecânica como spec descreve.
- `scripts/tiingo_backup.py` existe (listado em `ls scripts/tiingo*`) — reforça que o spec deveria integrar ao invés de sugerir `cp -r`.

### Fontes externas

- [Pepperstone Pricing — swap/overnight](https://pepperstone.com/en/ways-to-trade/pricing/) — confirma "5pm New York time server rollover" (22:00 GMT / 21:00 DST) e fórmula diária com 2.5% admin fee em índices/shares. "5pm NY" é o cutoff que toda posição multi-day cruza → CFD swap é real, não hipótese. Confirma a urgência do pivô.
- [bestbrokers.com Pepperstone review 2026](https://www.bestbrokers.com/reviews/pepperstone/spreads-fees-and-commissions/) — swap charges "use market closing price, trade size, fixed rate 2.5%". Long paga, short recebe.
- [Tiingo IEX API Documentation](https://www.tiingo.com/documentation/iex) — busca Google: feed "returns the most recent 2000 ticks of data at the specified frequency, and you cannot request data older than today's date minus 2000 data points". Para 1h isso é ~83 dias. **Esta é a tensão direta com §2.5 do spec que assume "tipicamente 2 anos".**
- [Tiingo IEX 1min desde 2017](https://www.tiingo.com/blog/iex-cloud-alternatives/) — conflito aparente: 1min data volta a 2017. Resolução TBD pelo smoke #1 do spec. Suporta a recomendação #2 (condicionar §2.5 ao verdict do smoke).

## Veredito

**PROCEED-WITH-CHANGES**

**Regra aplicada:**
- Zero 🔴 críticas bloqueantes. Infra é genuinamente neutra ao pivô.
- 3 🟠 altas remediáveis ANTES do plan (gate #2 migration bloqueante até smoke, holding-period hook, per-(class,freq) slack).
- Alinhamento com o pivô é positivo na intenção e na maior parte da execução; mas "habilitar intraday" não é automaticamente "medir/filtrar holding period", e três das preocupações são sobre essa confusão.

**Principal vetor estratégico:** o spec deveria incluir **uma cláusula explícita** (nova §1.4 ou §2.8) declarando que o ônus de medir/reportar `median_hold_hours` é das estratégias consumidoras, com referência aos campos `entry_time`/`exit_time` que já existem no `engine/portfolio.py`. Sem isso, corremos risco de repetir em 1h o erro que motivou o pivô em daily — edge existe, mas hold duration violation passa silencioso em diagnostic pós-run.
