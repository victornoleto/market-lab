# `tiingo_service` — Lazy-Cache com Eixo de Frequência (Daily + 1h Intraday)

**Data:** 2026-04-15
**Fase:** Post-pivot intraday short-hold (entre Phase 2.5 e Phase 3)
**Autor:** Claude Code (brainstorming guiado)
**Status:** design aprovado, aguardando plan de implementação
**Skill usada:** `superpowers:brainstorming`

---

## 1. Contexto

### 1.1 Gatilho do pivô

Os 5 ciclos Phase 2.5 (Clenow, Ehlers BP Swing, Run 4 Step 1 AFML simples,
F3.C long-history Ehlers, F3.D portfolio combinado) rodaram todos em bars
**diários**. A análise dos trades persistidos em
`grid_portfolio_20260415-1541` mostrou durações médias fundamentalmente
incompatíveis com o objetivo do projeto (CFDs Pepperstone com swap
overnight):

- **Clenow**: mediana 56-63 dias, máximo 287-378.
- **Ehlers BP Swing**: mediana 1-22 dias, mas posições presas por até 4 anos.

A decisão do pivô 2026-04-15 noite, registrada em `ROADMAP.md §"PIVOT"` e
`JORNADA.md §"Pivô: intraday short-hold"`, é:

1. Catálogo de estratégias re-prioritizado em torno de **short-hold intraday**
   (Chan mean-reversion, Ehlers BP em 1h, volatility breakouts).
2. Motor de dados migra de **bulk download eager** para **lazy-cache com
   eixo de frequência**, destravando os endpoints Tiingo IEX (1h, e em
   versões futuras 5m/1min) sem precisar pre-baixar.

Este spec entrega o item (2). O item (1) virá em specs separados, um por
estratégia, após este infra estar verde.

### 1.2 Gap atual

O código em `src/ai_trade/backtest/data/{tiingo_source,tiingo_storage}.py`
**já** implementa o contrato storage-first lazy-cache para daily:

```python
# tiingo_source.py:205
if self.storage.has(ticker, start, end):
    return self.storage.read(ticker, start, end)
df = self._http_fetch(ticker, start, end, asset_class)
if df.empty: return df
self.storage.write(ticker, df, asset_class=asset_class)
return self.storage.read(ticker, start, end)
```

O que falta para destravar intraday são quatro gaps pontuais:

1. **Eixo `frequency` no storage** — hoje layout é `{ticker}.parquet` único;
   precisa virar `{freq}/{ticker}.parquet` + manifest nested.
2. **Roteamento HTTP** — `_build_url`/`_build_params` hard-codam endpoints
   daily; precisam aceitar `frequency` e dispatchar para `/iex/` (equity
   intraday) ou adicionar `resampleFreq` (crypto/fx intraday).
3. **Coverage slack consciente de frequência** — o slack atual de 7 dias
   funciona para daily mas é inadequado para 1h (pode mascarar gaps
   significativos).
4. **Whitelist de freq/asset_class** — sem guardrails, um typo
   (`frequency="1h"` vs `"1hour"`) ou call-site mal-informado gasta API
   quota em endpoint inválido.

### 1.3 Hipótese de sucesso v1 (condicionada ao Smoke #1 retention)

**Pré-condição inviolável:** antes do refactor, o Smoke #1 retention probe
(§6.1 passo 1) mede a janela real de retention IEX. O spec é executável
em v1 se retention confirmada **≥ 6 meses** em 1h para os 3 asset
classes (threshold derivado de Chan buy-on-gap ≥ 4.5m + Ehlers 1h ≥ 3-4m
— detalhes em §6.2). Entre 3-6 meses = escalar decisão ao usuário (v1
viável para Chan buy-on-gap + Ehlers, mas cointegration pairs com CPCV
N=6 precisa ~33 meses e fica deferred para v2/v3). < 3 meses, o
paradigma **"lazy-cache reativo"** é errado — o spec volta ao brainstorm
(possibilidades: `scheduled daily-append` via cron, pré-compra de bulk
intraday enquanto subscrição ativa, ou troca de fonte).

**Nota sobre retention real:** docs públicos indicam retention rolling
de ~2000 bars = ~83 dias em 1h (§5.2). Se confirmado no smoke, o
Cenário B de §6.3 (re-brainstorm) é o desfecho esperado — e este spec
então serve como **infra-pronta** para o pivot para `scheduled
daily-append` (reusa 100% do código de migração + storage + source
refatorados).

Assumindo retention compatível, o trabalho está entregue quando:

- `TiingoSource.fetch("SPY", date(2023,1,1), date(2026,4,15), frequency="1hour")`
  baixa bars IEX, persiste em `data/tiingo/1hour/prices/SPY.parquet`,
  segunda chamada hita cache sem HTTP.
- Equivalente verde para `BTCUSD` (crypto 1h) e `EURUSD` (forex 1h).
- **Série retornada é split/dividend-ajustada** (via `splitFactor`/`divCash`
  do daily cache em pós-processamento — ver §3.3 + §5.6).
- Call-sites existentes (daily) continuam funcionando sem edit — `frequency`
  tem default `"daily"`.
- 377 testes atuais seguem verdes + ~25 testes novos (freq routing,
  whitelist, migração, slack per-(asset_class, freq), split adjustment,
  pgrep guard, rollback simulation).
- Migração do bulk existente (1660 tickers daily, ~145 MB) é idempotente,
  reversível via `mv`, **roda com backup automático opt-out** e **bloqueia
  se o bulk Tiingo estiver em execução** (`pgrep -f tiingo_bulk_download`).
- Cancelamento da subscrição Tiingo passa a ser opção segura **para
  daily somente** — intraday requer API viva por causa da janela rolling
  de retention (ver §5.2 + §6.5).

### 1.4 Instrumentação de holding period (downstream requirement)

O pivô 2026-04-15 foi gatilhado por **não medir duração real de trades**
(Clenow mediana 56-63d; Ehlers BP Swing outliers até 4 anos). Esta infra
é neutra quanto a holding period — responsabilidade é das estratégias
consumidoras — mas o spec documenta aqui o **padrão obrigatório** para
evitar repetir o erro em resolução maior:

- `src/ai_trade/backtest/engine/portfolio.py:61-62` **já persiste**
  `entry_time`/`exit_time` como `pd.Timestamp`. Quando bars são 1h, o
  diff dá minutos-horas. A infra de medição existe; falta apenas o
  gate.
- **Regra de catálogo pós-pivô:** todo diagnostic de estratégia intraday
  DEVE reportar `median_hold_hours` e `max_hold_hours` no `diagnostic.md`
  do run.
- **Alerta:** `median_hold > 48h` em estratégia declarada "short-hold"
  sinaliza violação do pivô. Base econômica: `[systematic_trading,
  Carver, p.185-188, ch.12]` — standardised cost (SR units) vs turnover:
  custo anual em SR = cost × annual_turnover; gate p.187-188 "aceite
  novo instrumento apenas se annual cost ≤ 0.13 SR/year (systems
  traders)". Short-hold com swap overnight Pepperstone viola este gate
  trivialmente se mediana > 48h. Warning explícito no diagnostic.
- **Gate de descarte (futuro):** `median_hold > 72h` em 1h = candidato
  a DESCARTE antes mesmo de rodar DSR/PBO (economia de compute +
  proteção contra repetir o erro do pivô).

Este requisito **não é enforçado neste spec** (é infra de dados, não
de estratégia) mas é listado aqui porque o spec de cada estratégia
intraday futura vai referenciar este parágrafo.

---

## 2. Arquitetura

### 2.1 Estratégia de entrega — refactor in place

`TiingoSource` e `TiingoStorage` são refatorados em place (não criamos um
módulo paralelo). Raciocínio explorado nos trade-offs durante o
brainstorming:

| Opção | Por que rejeitada |
|---|---|
| Módulo paralelo `tiingo_service.py` novo | Duplicaria auth, URL construction, 404 handling, env-file reader. Dois code paths = mais superfície de teste + risco de drift. |
| Layered façade (service wraps source) | Indirection extra. Três módulos a raciocinar em vez de dois. |
| **Refactor in place (escolhido)** | Zero duplicação; módulo já é 90% do que precisamos; o único gap semântico é o eixo `frequency`. TDD-first protege o baseline de 377 testes. |

### 2.2 Escopo v1 — 1h only + whitelist

`frequency ∈ {"daily", "1hour"}` em v1. Qualquer outro valor (`"5min"`,
`"1min"`, `"15min"`) levanta `NotImplementedError` com mensagem apontando
para follow-up plan.

Raciocínio: a incerteza de primeira ordem é "esta subscrição Tiingo
retorna bars IEX de fato, e qual a janela de retention real" — e não
"suportamos 1h, 5m ou 1min". Um MVP 1h-only resolve a primeira incerteza
com 2 fixtures de parquet e dá base para Chan pairs / Ehlers 1h. Adicionar
5m/1min depois é um plan de 1 linha no whitelist + fixtures novas.

Adicionalmente: a entrada em `JORNADA.md §"Últimos detalhes"` nota que a
subscrição Tiingo será cancelada após este infra estar verde — logo v1
precisa de "apenas o suficiente" para validar intraday e baixar dados de
referência antes do cancelamento.

### 2.3 Layout físico + manifest — α (freq-at-top-level)

```
data/tiingo/
├── manifest.json              # unified, nested
├── daily/
│   ├── prices/
│   │   ├── AAPL.parquet
│   │   └── ...                # 1660 tickers existentes, movidos pela migração
│   └── meta/
│       └── AAPL.json
└── 1hour/
    ├── prices/
    │   ├── SPY.parquet
    │   └── ...
    └── meta/
        └── SPY.json
```

**Manifest schema (v2 — nested):**

```json
{
  "AAPL": {
    "daily": {
      "first_dt": "1990-01-02T00:00:00",
      "last_dt":  "2026-04-14T00:00:00",
      "n_bars":   9150,
      "asset_class": "equity",
      "fetched_at":  "2026-04-14T22:05:00"
    },
    "1hour": {
      "first_dt": "2024-04-15T13:30:00",
      "last_dt":  "2026-04-14T20:00:00",
      "n_bars":   3400,
      "asset_class": "equity",
      "fetched_at":  "2026-04-15T11:00:00"
    }
  },
  ...
}
```

Nota: `first_dt`/`last_dt` são **ISO-datetime tz-naive** em v2 (não
`date` como em v1), consistente com o pipeline — `_normalize` já produz
`DatetimeIndex` tz-naive. Migração preserva semântica daily via sufixo
`T00:00:00` (midnight no dia registrado).

Alternativas exploradas e rejeitadas:

| Layout | Por que rejeitado |
|---|---|
| `{ticker}_{freq}.parquet` (flat com sufixo) | Quebra tab-completion, conflita dois eixos em uma string, dificulta globbing. |
| Multi-index interno num único parquet por ticker | Write amplification em freqs grandes (1min tem ~400× mais bars que daily). |
| Per-freq manifest separado | Perde a invariante "single source of truth" sem ganho compensatório. |
| `{prices,meta}/{freq}/{ticker}` (freq sob prices) | Mesmo conteúdo, nesting levemente pior para blast-radius de `rm`. |

Escolhido α porque:
1. `rm -rf data/tiingo/1hour/` blast-radius isolado (intraday churn
   mais que daily; queremos opcionalidade de reset).
2. `has()` continua O(1) (single manifest read + nested dict lookup).
3. Migração é `mv prices → daily/prices` + rewrite de chaves (mecânico).
4. Parquets de diferentes freqs têm schemas idênticos (OHLCV 6-col), não
   há nada especial que justifique flatten.

### 2.4 Cache key + coverage — slack per-(asset_class, frequency)

- **Identidade do slot no manifest**: `(ticker, frequency)`.
- **Range de cobertura**: comparado via `first_dt`/`last_dt` datetime
  (**tz-naive**, consistente com a convenção já presente no pipeline —
  `_normalize` faz `dt.tz_localize(None)`).
- **Slack por (asset_class, frequency) — não uniforme:** já em v1
  (estrutural, não edge case — crypto 24/7 vs equity RTH vs forex
  weekend-close são propriedades do pivô, não detalhes).

```python
_COVERAGE_SLACK: dict[tuple[str, str], timedelta] = {
    # Daily (preserva comportamento atual — 7 dias cobre fim-de-ano/feriados)
    ("equity", "daily"):  timedelta(days=7),
    ("etf",    "daily"):  timedelta(days=7),
    ("index",  "daily"):  timedelta(days=7),
    ("crypto", "daily"):  timedelta(days=2),   # 24/7 — weekend/holiday não cria gap
    ("forex",  "daily"):  timedelta(days=4),   # fecha sex 22h UTC → dom 22h UTC
    # 1 hour
    ("equity", "1hour"):  timedelta(hours=12), # RTH 09:30-16:00 ET + pre/post market mínimo
    ("etf",    "1hour"):  timedelta(hours=12),
    ("crypto", "1hour"):  timedelta(hours=6),  # 24/7 → gap estrutural menor
    ("forex",  "1hour"):  timedelta(hours=48), # weekend de 2 dias calendário
}
```

**Assinatura pública:** `has(ticker, start, end, frequency)` aceita
`start: date | datetime, end: date | datetime` já em v1 (5m/1min futuros
precisam de precisão sub-day; `isinstance` check interno é ~3 linhas).
Inputs `date` são promovidos a datetime via
`datetime.combine(d, datetime.min.time())`. Call-sites existentes que
passam `date` continuam funcionando.

`has(ticker, start, end, freq)` retorna `True` iff:

```
slack = _COVERAGE_SLACK[(manifest[ticker][freq].asset_class, freq)]
manifest[ticker][freq].first_dt <= to_datetime(start) + slack
AND
manifest[ticker][freq].last_dt + slack >= to_datetime(end)
```

Raciocínio dos slacks:

- **equity/etf 1h = 12h:** um dia de trading RTH tem 6.5 bars; 12h cobre
  o "pediu 2026-01-05 00:00 mas dados começam 09:30 pelo market open"
  sem mascarar gaps estruturais maiores.
- **crypto 1h = 6h:** 24/7 não tem market open — 6h cobre pequenas
  interrupções de feed/manutenção Tiingo sem esconder disponibilidade
  real.
- **forex 1h = 48h:** fecha sex 22h UTC → dom 22h UTC, então 2 dias
  calendário é o gap estrutural que um request cross-weekend cruza.
- **daily mantém 7d** para equity/etf/index (retrocompat com os 1660
  tickers já em disco); crypto=2d e forex=4d são mais apertados porque
  mercado não tem o mesmo calendário de feriados.

Citação: slack numérico é decisão empírica de engenharia — **não há
livro que recomende "X horas" para cache coverage**; o que os livros de
microstructure cobrem é estrutura de precedência e tick size
(`[trading_exchanges, Harris, p.33-34]` — price priority + time
precedence; **não** session taxonomy). A intuição de market hours aqui é
conhecimento operacional (equity RTH 09:30-16:00 ET, forex 24/5 Sydney-NY,
crypto 24/7) e não tem âncora em livro específico do knowledge base.
Documentado como decisão de engenharia, não como citação falsa.

### 2.5 Partial-fetch semantics — grava returned + requested range

**Contexto obrigatório:** a aplicabilidade desta seção depende do verdict
do Smoke #1 retention (§6.1 passo 1). Documentação pública Tiingo IEX
([riingo](https://business-science.github.io/riingo/reference/riingo_iex_prices.html),
[tiingo-python #117](https://github.com/hydrosquall/tiingo-python),
[QuantStart](https://www.quantstart.com/articles/evaluating-data-coverage-with-tiingo/))
indica retention **rolling de ~2000 data points na frequência pedida** —
~83 dias em 1h. Se Smoke #1 confirmar isso, a política descrita abaixo
aplica-se ao cenário "retention curta" (wide requests sempre retornam
~janela_atual); se retention for efetivamente longa (≥ 6 meses), a
política ainda é válida mas o caso patológico é raro.

Se user pede `[2020-01-01, 2026-04-15]` em 1h e a API retorna só
`[2026-01-22, 2026-04-15]` (retention rolling 83d):

- `manifest[ticker]["1hour"].first_dt = "2026-01-22T..."` (o que veio).
- `manifest[ticker]["1hour"].requested_start = "2020-01-01T00:00:00"`
  (o que foi pedido — **adicionado em v1**, não v2).
- `manifest[ticker]["1hour"].requested_end   = "2026-04-15T00:00:00"`.
- **Política de `has()`:** compara `start`/`end` com o `first_dt`/`last_dt`
  retornado (não o requested). Repeat wide request idêntico re-fetcha —
  **mas o Warning em log avisa** "requested range coincide com o anterior
  e retention é curta; considere ajustar start".
- Chamadas mais estreitas dentro da retention real servem do cache sem
  HTTP (via `first_dt`/`last_dt`).

**Por que gravar `requested_range` em v1 e não v2:** no cenário de
retention curta (preocupação principal do Smoke #1), cada repeat wide
request sempre retorna "~hoje-retention, hoje" — não adiciona história.
Sem `requested_range`, não há como detectar que o padrão está acontecendo.
Custo: 2 campos por entry de manifest, ~5 linhas de código. Benefício:
evidência empírica de redundância + possibilidade de warning.

**Custo de re-fetch bounded:** 1 chamada HTTP por repeat wide request,
dentro do rate limit Tiingo paid (~5000/h).

### 2.6 Matriz de endpoints v1

**⚠️ Esta tabela é premissa, não fato confirmado — depende do Smoke #1
(§6.1).** Se smoke falhar em algum asset_class × freq, esta tabela + §2.7
são revistas antes do refactor.

| asset_class | frequency | URL | params extras |
|---|---|---|---|
| equity/etf/index | daily | `/tiingo/daily/{ticker}/prices` | — |
| equity/etf | 1hour | `/iex/{ticker}/prices` | `resampleFreq=1hour` |
| crypto | daily | `/tiingo/crypto/prices` | `tickers=X, resampleFreq=1day` |
| crypto | 1hour | `/tiingo/crypto/prices` | `tickers=X, resampleFreq=1hour` |
| forex | daily | `/tiingo/fx/{ticker}/prices` | — |
| forex | 1hour | `/tiingo/fx/{ticker}/prices` | `resampleFreq=1hour` |
| index | 1hour | **`NotImplementedError`** | IEX não cobre índices diretamente; usar ETF proxy (SPY, QQQ). |

**Citação da URL:**
- Tiingo docs: [tiingo.com/documentation/iex](https://www.tiingo.com/documentation/iex),
  [tiingo.com/documentation/end-of-day](https://www.tiingo.com/documentation/end-of-day).
- Endpoint shape validado por terceiros:
  [riingo reference](https://business-science.github.io/riingo/reference/riingo_iex_prices.html),
  [tiingo-python #117](https://github.com/hydrosquall/tiingo-python/issues/117).

**Nota sobre IEX como venue específico (não consolidated tape):** IEX é
uma exchange individual, não o consolidated-price feed (SIP). Chan
`[algo_trading_chan, p.10-11, ch.1]` observa que estratégias
mean-reversion intraday são sensíveis a essa distinção — backtests em
consolidated-tape prices podem inflacionar retornos de estratégias que
na vida real executam no venue primário. Usar dados IEX em v1 é
compatível com o padrão de execução Pepperstone cTrader (CFD derivado
de venue, não tape). Documentar para evitar surpresa futura.

**Bar timestamp convention:** Tiingo retorna datetime alinhado ao
**início** do bar (bar de `2026-01-15 14:00` = período `[14:00, 15:00)`).
Documentar para evitar look-ahead bias em triple-barrier labeling +
roofing filters `[algo_trading_chan, p.4, ch.1]`.

### 2.7 Componentes (diagrama)

```
src/ai_trade/backtest/data/
├── tiingo_source.py            [REFATORADO]
│     fetch(ticker, start, end, asset_class="equity",
│           frequency="daily") → DataFrame
│     - _build_url(ticker, asset_class, frequency)    [+ eixo freq]
│     - _build_params(..., frequency)                 [+ resampleFreq]
│     - _WHITELIST: {(equity/etf, daily|1hour),
│                    (index, daily),
│                    (crypto, daily|1hour),
│                    (forex, daily|1hour)}
│
├── tiingo_storage.py           [REFATORADO]
│     TiingoStorage(root=Path("data/tiingo"))
│     - has(ticker, start, end, frequency)            [+ kwarg, aceita date|datetime]
│     - read(ticker, start, end, frequency)           [+ kwarg]
│     - write(ticker, df, asset_class, frequency)     [+ kwarg]
│     - _COVERAGE_SLACK: dict[(asset_class, freq), timedelta]  [per-AC]
│     - manifest.json: nested {ticker: {freq: {range, requested_range}}}
│     - layout: root/{freq}/{prices,meta}/{ticker}
│
└── tiingo_migrate.py           [NOVO]
      migrate_to_freq_layout(root, *, dry_run=False)
      - detecta layout velho (prices/ direto sob root)
      - move {prices,meta} → daily/{prices,meta}
      - re-escreve manifest: achatado → nested sob "daily"
      - converte first_date/last_date → first_dt/last_dt (ISO datetime)
      - idempotente (re-run = no-op)
```

Chamadores existentes (grids Clenow/Ehlers, scripts de bulk) **não
mudam** — `frequency="daily"` default preserva comportamento.

---

## 3. Arquivos + Testes

### 3.1 Arquivos

| Path | Mudança | Linhas est. |
|---|---|---|
| `src/ai_trade/backtest/data/tiingo_source.py` | +`frequency` kwarg + dispatch por (asset_class, freq) + whitelist + `resampleFreq` + **split adjust via daily cache** (§3.3) + `NotImplementedError` path | +180 / -10 |
| `src/ai_trade/backtest/data/tiingo_storage.py` | `has/read/write` recebem `frequency`; manifest nested + `requested_range` v1; slack **per-(asset_class, freq)**; `date | datetime` no `has()`; lockfile detection | +120 / -30 |
| `src/ai_trade/backtest/data/tiingo_migrate.py` | **NOVO** — `migrate_to_freq_layout` idempotente + pgrep guard + backup auto + lockfile | ~180 |
| `scripts/tiingo_smoke_intraday.py` | **NOVO** — retention probe: SPY/BTCUSD/EURUSD 1h; mede `observed_retention_bars/days` | ~120 |
| `scripts/run_tiingo_migrate.py` | **NOVO** — CLI: `--dry-run`, `--root`, `--force-ignore-running`, `--skip-backup` | ~60 |
| `tests/test_tiingo_source.py` | +routing, whitelist, fixtures intraday, **split adjust integration** (com daily cache pré-populado) | +320 |
| `tests/test_tiingo_storage.py` | +nested manifest, freq kwarg, slack per-(AC, freq), multi-freq, date|datetime, requested_range | +260 |
| `tests/test_tiingo_migrate.py` | **NOVO** — detect layout, dry-run, migração real, idempotência, pgrep guard, backup auto, rollback sim, lockfile | ~260 |
| `pyproject.toml` | Nenhuma mudança — sem dependências novas (verificado: `pyarrow` já presente handle intraday tz-naive) | — |

### 3.2 Baseline de testes

377 (`pytest -q` atual) → **~405** pós-entrega (~28 novos: ~11 migrate,
~9 storage, ~8 source, somando guards + slack per-AC + split adjust).
Meta 100% verde, **não quebrar baseline** `[.claude/CLAUDE.md §"Convenções
de código"]`.

### 3.3 Ajuste de splits/dividendos em IEX intraday (decisão v1 consciente)

**Problema:** Tiingo IEX retorna preços **sem ajuste** de split/dividendo
(confirmado por docs públicos e por evidência direta do projeto — o
commit `5ca9410` documenta que ler `close` não-ajustado em daily inflou
artificialmente o Sharpe do SPY de 0.31 para 0.806 quando foi corrigido
para `adj_close`). O mesmo erro re-introduzido em intraday enviesa
estratégias short-hold **silenciosamente** — um split 2:1 num ticker
como NVDA mid-janela vira crash artificial de 50% num oscilador Ehlers
BP ou num sinal de Chan mean-reversion 1h.

**Decisão v1 (upgradada de "caveat v1.1" para requisito crítico após
revisão dos juízes; fórmula corrigida após 2ª rodada adversarial):**

1. IEX retorna `{open, high, low, close, volume}` sem `adjClose`.
2. `TiingoSource.fetch(ticker, ..., frequency="1hour")` **aplica ajuste
   em pós-processamento reusando o módulo existente
   `src/ai_trade/backtest/data/adjust.py`** (entregue pelo commit
   `5ca9410` — mesmo módulo que corrigiu o bug daily que triplicou o
   Sharpe do SPY). A função `adjust_ohlc(df)` usa o **approach ratio**:

   ```
   ratio     = adj_close_daily / close_daily    # == 1 quando sem div/split
   open, high, low, close_adj = (o, h, l, c) × ratio
   adj_close_final = close_adj                  # preserva total-return
   ```

   Fórmula consistente com `[quant_trading_chan, p.37]` — o multiplier de
   Chan é `(Close(T-1) − d) / Close(T-1)` aplicado a todas as prices
   anteriores a T; Chan explicita "do not subtract $d$, to preserve
   returns" — a subtração fica **dentro** do multiplier, não é um passo
   separado. O approach ratio de `adjust.py` é matematicamente
   equivalente (Tiingo daily já entrega `adj_close` com multiplier
   acumulado pelo provider; derivar ratio = `adj_close/close` e aplicar
   ao intraday respeita a regra de preservar returns).

3. **Para IEX intraday:** o ratio é derivado por **dia de calendário** do
   daily cache e aplicado às bars intraday do mesmo dia:

   ```
   Para cada dia D no range pedido:
       ratio_D = daily_cache[ticker].loc[D, "adj_close"]
              / daily_cache[ticker].loc[D, "close"]
       intraday_bars[data == D] × ratio_D
   ```

4. **Pré-condição:** o ticker tem que estar no daily cache com
   `adj_close` populado (Tiingo daily entrega isso por default — ver
   `tiingo_source.py:_normalize`). Se não tiver (ex.: `BTCUSD` crypto —
   não aplica splits em crypto; `EURUSD` forex — mesmo), `adj_close :=
   close` é **a decisão certa** (ratio = 1.0 por construção).

5. **Se é equity/etf e o daily cache não tem o ticker:**
   `NotImplementedError` com mensagem clara — **não** fallback silencioso
   para `close`. Mensagem: "baixe o daily primeiro para obter
   `adj_close`, ou pré-autorize via flag `--skip-adjust` se você sabe o
   que está fazendo."

**Citações (regra 2 — obrigatório neste ponto sensível):**

- `[quant_trading_chan, p.37]` — fórmula canônica do multiplier: preserva
  returns embutindo a subtração do dividendo **dentro** do multiplier,
  nunca como termo separado.
- `[trading_systems_methods, Kaufman, p.914]` — "back-adjusted
  split-adjusted stocks perdem características de volatilidade;
  estratégias percentage-based ou vol-based quebram em série
  não-ajustada".
- `[ml_for_algo_trading, ch.2, p.35-40]` — dollar bars e price-level
  adjustment para splits.
- `[advances_fin_ml, López de Prado, p.57-63, ch.2]` — data structures
  para ML financeiro (dollar bars p.57-59, tick-imbalance bars p.59-62,
  volume-run bars p.62-63).
- `[ml_for_algo_trading, ch.8, p.223-224]` — look-ahead bias de
  retroactive splits.

**Baseline comparison caveat:** os 5 ciclos Phase 2.5 anteriores usaram
preços ajustados (daily `adjClose`). Pivô para intraday ajustado via
pós-processamento preserva apples-to-apples — não se compara com `close`
raw intraday.

### 3.4 Fixtures (HTTP mocked via `MagicMock`, padrão existente)

- **IEX 1h sample** (5-10 linhas): shape real Tiingo IEX — datetime com
  timestamp intradia alinhado ao início do bar, OHLCV, **sem `adjClose`**.
  Teste de ajuste usa sample daily com `splitFactor`/`divCash` + sample
  intraday raw, verifica que o `adj_close` final é consistente com
  multiplier do daily.
- **Crypto 1h sample**: wrappado em `[{"ticker": "btcusd", "priceData":
  [...]}]`, mesma forma de unwrap do daily crypto. `adj_close := close`
  é correto (crypto não tem splits).
- **Forex 1h sample**: similar ao daily fx; `volume` pode vir 0.0 ou
  ausente — default 0.0 no `_normalize`. `adj_close := close` (forex
  também não tem splits).

Live validation de URL/payload shape fica em `scripts/tiingo_smoke_intraday.py`,
**não em pytest**. Mesmo padrão do `scripts/tiingo_smoke.py` existente.

### 3.5 Interface do `migrate_to_freq_layout`

```python
@dataclass
class MigrationReport:
    moved_parquets: int          # 0 em dry-run (nenhum arquivo movido de fato)
    moved_meta_files: int        # idem
    rekeyed_tickers: int         # 0 em dry-run
    elapsed_seconds: float
    dry_run: bool
    # Lista legível de ops, sempre populada (em dry-run é o que seria feito;
    # em execução real é o que foi feito). Ex.:
    # ["check: pgrep -f tiingo_bulk_download → clean",
    #  "backup: cp -r data/tiingo data/tiingo_premigrate_<ts>",
    #  "mv prices/AAPL.parquet → daily/prices/AAPL.parquet",
    #  "rekey manifest[AAPL] → manifest[AAPL][daily]",
    #  ...]
    operations: list[str]

def migrate_to_freq_layout(
    root: Path,
    *,
    dry_run: bool = False,
    force_ignore_running: bool = False,
    skip_backup: bool = False,
) -> MigrationReport:
    """Migrate `root/prices/*.parquet` → `root/daily/prices/*.parquet`,
    rewrite manifest nested by frequency.

    Guards (v1, pós revisão dos juízes):

    1. **pgrep guard (default ON):** if `pgrep -f tiingo_bulk_download`
       finds an active process, abort with clear error. User MUST stop
       the bulk download before migrating. Override via
       `force_ignore_running=True` (explicit opt-in — dangerous).
    2. **Backup automático (default ON):** runs `scripts/tiingo_backup.py`
       as first mutating step (creates `data/tiingo_premigrate_<ts>.tar.gz`
       or similar). User opts OUT via `skip_backup=True` (e.g., already
       has external backup).
    3. **Idempotency:** if `root/daily/prices/` already exists, returns
       a report with 0 ops and layout unchanged. Safe to call multiple
       times.

    Raises if `root/prices/` exists but `root/manifest.json` is missing
    or corrupt — bail before moving files.

    Rollback: restore backup created in step 2, or manually:
        mv root/daily/prices/* root/prices/
        mv root/daily/meta/*   root/meta/
        # + restaurar manifest.json do backup
    """
```

---

## 4. Migração do bulk existente

**Situação atual:** `data/tiingo/prices/*.parquet` (1660 arquivos, ~145
MB) + `data/tiingo/meta/*.json` + `data/tiingo/manifest.json` com chaves
raiz `= ticker`.

**Após migração:**
- `data/tiingo/daily/prices/*.parquet`
- `data/tiingo/daily/meta/*.json`
- `data/tiingo/manifest.json` nested: `{ticker: {daily: {first_dt, last_dt, ...}}}`.

### 4.1 Fluxo

```
def migrate_to_freq_layout(root, *, dry_run=False,
                           force_ignore_running=False,
                           skip_backup=False):
    1. GUARD: pgrep -f tiingo_bulk_download.
       - Se ativo E force_ignore_running=False → raise RuntimeError
         com mensagem: "Bulk Tiingo em execução (PID <N>); pare-o
         antes de migrar OU passe --force-ignore-running (risco:
         split-brain de arquivos)."
       - Se ativo E force_ignore_running=True → log Warning e prossegue.
    2. Se root/daily/prices/ já existe → no-op idempotente, retorna
       report vazio com operations=["layout já migrado"].
    3. Se root/prices/ ausente → no-op (root vazio / novo).
    4. Carregar manifest. Se corrompido → raise antes de mover arquivos.
    5. Planejar ops (lista de strings, sempre populada):
       - [guard] "pgrep tiingo_bulk_download → clean"
       - [backup] Se skip_backup=False:
           "backup: tar czf data/tiingo_premigrate_<ts>.tar.gz data/tiingo/"
           (usa scripts/tiingo_backup.py se existir e é compatível;
           senão, tar direto)
       - [fs] mkdir -p root/daily/prices/ e root/daily/meta/
       - [fs] Para cada parquet em root/prices/: mv para daily/prices/
       - [fs] Para cada json em root/meta/: mv para daily/meta/
       - [fs] rmdir root/prices/ e root/meta/ (após moves)
       - [manifest] Para cada ticker em manifest:
           new_entry = wrap_under_daily_and_rename_date_to_dt(old_entry)
       - [manifest] Persistir novo manifest POR ÚLTIMO (point-of-no-return
         tardio — se crash aqui, arquivos movidos + manifest velho =
         recovery manual mas possível).
    6. Se dry_run: imprime plan, retorna report com operations=<plan>,
       moved_*=0, rekeyed_tickers=0, não executa.
    7. Senão: executa cada op em ordem. Log append em logs/tiingo.log:
         [HH:MM:SS] migrate: <op>
    8. Retorna report com contadores preenchidos.
```

**Lockfile (mitigação de consumer concorrente durante migração):**
escrever `root/.migration.lock` no passo 5 antes de qualquer `mv`; o
`TiingoStorage.__post_init__` pode detectar este arquivo e raise
`RuntimeError("migração em andamento; aguarde")` em vez de carregar
manifest inconsistente. Lockfile é removido no passo 7 após persistir
manifest novo. Se o migrate crash no meio, lockfile persiste e
sinaliza necessidade de rollback.

### 4.2 Esquema de conversão do manifest

```
old:  {"AAPL": {"first_date": "1990-01-02", "last_date": "2026-04-14",
                "n_bars": 9150, "asset_class": "equity",
                "fetched_at": "2026-04-14T22:05:00"}}

new:  {"AAPL": {"daily": {"first_dt": "1990-01-02T00:00:00",
                          "last_dt":  "2026-04-14T00:00:00",
                          "n_bars":   9150,
                          "asset_class": "equity",
                          "fetched_at":  "2026-04-14T22:05:00"}}}
```

### 4.3 Invocação

- **Manual, opt-in.** Nunca auto no `TiingoStorage.__init__` — queremos
  ver o dry-run antes de mover arquivos.
- **Guards obrigatórios antes de invocar:**
  1. Parar o bulk Tiingo (`pgrep -f tiingo_bulk_download` deve estar
     clean). Script aborta se não estiver, salvo `--force-ignore-running`.
  2. Backup automático roda por default (opt-out via `--skip-backup`).
- Workflow:
  ```
  # 1. Parar bulk se ainda rodando (MEMORY indica que pode estar ativo)
  pkill -f tiingo_bulk_download || true

  # 2. Inspecionar plan
  uv run python scripts/run_tiingo_migrate.py --dry-run

  # 3. Executar (backup automático roda primeiro)
  uv run python scripts/run_tiingo_migrate.py
  ```
- Log em `logs/tiingo.log` (append-only, padrão do projeto
  `[memory: unified log preference]`).

### 4.4 Rollback

**Backup é automático** no script (§3.5 + §4.3): antes de qualquer `mv`,
`run_tiingo_migrate.py` executa `scripts/tiingo_backup.py` (ou `tar czf`
equivalente) criando `data/tiingo_premigrate_<ts>.tar.gz`. Opt-out
explícito via `--skip-backup`.

**Restore via backup automático:**

```bash
# Se o backup automático rodou (default):
tar xzf data/tiingo_premigrate_<ts>.tar.gz -C /tmp/
rm -rf data/tiingo
mv /tmp/data/tiingo data/tiingo
```

**Rollback manual (se `--skip-backup` foi usado e precisa reverter):**

```bash
mv data/tiingo/daily/prices/* data/tiingo/prices/
mv data/tiingo/daily/meta/*   data/tiingo/meta/
# + restaurar manifest.json de um git commit anterior
rm -f data/tiingo/.migration.lock  # se o crash deixou lockfile
```

**Lockfile é sinalizador:** `data/tiingo/.migration.lock` presente =
migração crashou no meio. `TiingoStorage.__post_init__` detecta e raise
`RuntimeError("migração incompleta; execute rollback")` para impedir
uso da instância em estado inconsistente.

---

## 5. Caveats Conhecidos

| # | Caveat | Mitigação |
|---|---|---|
| 5.1 | **URL IEX exata não verificada contra live API.** Docs públicos indicam `/iex/{ticker}/prices` mas pode variar por plano. | **Primeiro passo do plan (Smoke #1)** é `scripts/tiingo_smoke_intraday.py` — se der erro 404 ou shape diferente, parar e revisar spec antes de refactorar. Ver §6.2 para o critério go/no-go quantitativo. |
| 5.2 | **Janela IEX retention — medida empiricamente em 2026-04-15 (Smoke #1 executado).** Docs públicos ([riingo](https://business-science.github.io/riingo/reference/riingo_iex_prices.html), [tiingo-python #117](https://github.com/hydrosquall/tiingo-python/issues/117), [QuantStart](https://www.quantstart.com/articles/evaluating-data-coverage-with-tiingo/)) afirmavam retention rolling de ~2000 bars = ~83 dias em 1h. **Refutado parcialmente** pela subscrição paid do projeto: SPY equity IEX retornou **1825 dias (5 anos)** / 7824 bars (4.3 bars/dia útil, bate com 6.5h RTH). Crypto (btcusd) mostrou **208 dias** / 5001 bars (cap em ~5000 bars × 24/7 — este sim rolling). Forex (eurusd) mostrou **416 dias** / 6948 bars. **Implicação:** paradigma "lazy-cache reativo" é **viável** para a subscrição atual em todas as 3 asset classes. O cap em ~5000 bars para crypto é a limitação real mais apertada, mas ainda ≥ threshold 180d. | **Smoke #1 PASS** (§6.1 passo 1, §6.2 critério). Pior caso 208d ≥ 180d = PROCEED Cenário A. Gate recalibrado por caso de uso (§6.2): ≥ 6 meses em todos 3 asset classes foi atingido com folga em equity (5 anos) e forex (13.7m); crypto fica apertado (6.9m) mas suficiente para Chan buy-on-gap + Ehlers 1h. Log: `logs/tiingo.log` 2026-04-15 17:47. |
| 5.3 | **Partial returns marcados no manifest já em v1** (`requested_range`) — decisão upgradada pós revisão dos juízes. | Custo ~5 linhas; dá evidência empírica de redundância + Warning em repeat wide request. Substitui a política YAGNI v1 original. |
| 5.4 | **Rate limit Tiingo (~5000/h paid)** não enforçado client-side. | Não crítico para v1 (universo pequeno, cache agressivo). Adicionar throttle se smoke/backtest bater limite. |
| 5.5 | **Migração transacional parcial.** Se `mv` funciona mas `manifest.json` write falha, ficamos com arquivos em dois lugares + manifest velho. | Lockfile `data/tiingo/.migration.lock` (§4.1) sinaliza estado inconsistente; `TiingoStorage.__post_init__` raise se ver lockfile. Backup automático opt-out (§4.3) garante restore baseline. Teste `test_migration_rollback_restores_layout` simula falha transacional via monkeypatch em `_save_manifest`. |
| 5.6 | **IEX sem `adjClose` — handled em v1 via post-processing com daily cache** (decisão §3.3, upgradada de caveat para requisito). | `TiingoSource.fetch(frequency="1hour")` aplica `splitFactor`/`divCash` do daily cache. Se ticker equity/etf não está no daily cache → `NotImplementedError` (não fallback silencioso). Crypto/forex: `adj_close := close` é correto (não há splits). |
| 5.7 | **Baseline comparison — daily adj vs intraday adj.** Os 5 ciclos Phase 2.5 usaram `adjClose` do daily. v1 intraday aplica adjust via `splitFactor`/`divCash` do mesmo daily cache — **mantém apples-to-apples**. | Documentado em §3.3. Teste de integração verifica que adj_close_intraday é consistente com adj_close_daily nas bars diárias do mesmo dia (tolerance de rounding). |
| 5.8 | **Write amplification em 1min (v2).** 1min cross-classes em 10a = ~1-5M bars/ticker. Em ~48B/row = 50-250MB/parquet; universo de 1660 tickers = ~200-400 GB. | v1 layout `{freq}/prices/{ticker}.parquet` funciona fine em 1h. Para v2 quando 5m/1min entrarem, layout evolui para `{freq}/prices/{ticker}/{year}.parquet` (partition por ano). Documentado em §6.4 Fora de Escopo + §6.6 Unblock Path. |
| 5.9 | **Mudança de default para `frequency="daily"`**. Se um call-site futuro esquecer de passar `frequency=` e o ticker só tiver bars 1h no cache, `has()` retorna False e re-fetcha daily desnecessariamente. | Default seguro (daily é o que o código atual assume implicitamente). Documentar no docstring que `frequency` é kwarg explícito para intraday. |

---

## 6. Plano de Execução

### 6.1 Ordem dos passos (TDD-first)

1. **Smoke #1 — RETENTION PROBE (gate de DESIGN, não só de execução).**
   `scripts/tiingo_smoke_intraday.py` roda contra subscrição Tiingo viva:

   ```
   Para cada (ticker, asset_class) em [("SPY","equity"),
                                       ("BTCUSD","crypto"),
                                       ("EURUSD","forex")]:
       pede startDate = hoje - 5 anos, endDate = hoje, resampleFreq=1hour
       mede: observed_first_dt, observed_last_dt,
             observed_retention_bars = len(response),
             observed_retention_days = (last_dt - first_dt).days
   Log em logs/tiingo.log:
       tiingo-smoke-1 <ticker> retention=<days>d bars=<N>
   ```

   **Gate quantitativo (detalhado em §6.2):** retention observada ≥ 12
   meses em 1h para os 3 asset classes = PROCEED; senão = BLOCK, voltar
   ao brainstorm (scheduled daily-append, pré-compra bulk intraday, ou
   outra fonte). Este passo NÃO toca storage/source — é probe isolado
   (~40 linhas reusando `scripts/tiingo_smoke.py`).

2. **Migração (TDD)** — `tests/test_tiingo_migrate.py` primeiro:
   - `test_detects_old_layout_and_plans_moves`
   - `test_dry_run_does_not_write`
   - `test_real_migration_moves_files_and_rekeys_manifest`
   - `test_idempotent_on_already_migrated_root`
   - `test_raises_on_corrupt_manifest`
   - `test_preserves_datetime_semantics_daily_at_midnight`
   - `test_pgrep_guard_blocks_when_bulk_running` (simula via monkeypatch)
   - `test_force_ignore_running_bypasses_guard_with_warning`
   - `test_backup_automatico_cria_tar_gz_e_opt_out_via_skip_backup`
   - `test_migration_rollback_restores_layout` (simula falha em
     `_save_manifest` via monkeypatch; verifica lockfile + recovery)
   - `test_lockfile_blocks_concurrent_storage_init`

   Então implementar `tiingo_migrate.py`. Rodar dry-run em `data/tiingo/`
   real → inspecionar plan → rodar real (backup automático é o primeiro
   passo; pgrep guard bloqueia se bulk ativo).

3. **TiingoStorage refactor (TDD)** — expandir `test_tiingo_storage.py`:
   - `test_has_with_frequency_kwarg`
   - `test_manifest_nested_schema`
   - `test_slack_per_asset_class_and_freq` (equity/crypto/forex × daily/1h)
   - `test_multi_freq_same_ticker_isolated`
   - `test_write_creates_freq_subdir`
   - `test_read_from_specific_freq`
   - `test_has_accepts_date_or_datetime` (backwards-compat + sub-day)
   - `test_manifest_includes_requested_range_v1`
   - `test_warning_on_repeat_wide_request`

   Refatorar `tiingo_storage.py` para passar.

4. **TiingoSource refactor (TDD)** — expandir `test_tiingo_source.py`:
   - `test_routes_equity_1h_to_iex_endpoint`
   - `test_routes_crypto_1h_with_resample_param`
   - `test_routes_forex_1h_with_resample_param`
   - `test_rejects_frequency_not_in_whitelist`
   - `test_rejects_index_1h_with_etf_hint`
   - `test_rejects_5min_with_plan_pointer`
   - `test_iex_payload_normalizes_without_adjclose`
   - `test_iex_applies_split_adjust_from_daily_cache` (**crítico** —
     verifica multiplier do daily aplicado ao intraday)
   - `test_iex_raises_notimplemented_if_equity_not_in_daily_cache`
   - `test_crypto_and_forex_use_close_as_adj_close_no_split`

   Refatorar `tiingo_source.py` para passar.

5. **Integração end-to-end** — test que roda
   `TiingoSource.fetch("SPY", start, end, frequency="1hour")` com HTTP
   mocked + daily cache pré-populado com `splitFactor`, verifica
   persistência em `data/tiingo/1hour/prices/SPY.parquet` **com
   `adj_close` ajustado**, segunda chamada hita cache sem HTTP.

6. **Baseline verde** — `uv run pytest -q` → ~405/405 verdes.

7. **Smoke #2 — end-to-end** — re-rodar `tiingo_smoke_intraday.py`, mas
   agora routando pelo código refatorado (não mais standalone). Gate:
   mesmo shape e range de Smoke #1, + `adj_close` presente e consistente
   com daily `adj_close` em bars diárias correspondentes (tolerance
   rounding).

8. **Docs + commit** — entrada em `JORNADA.md` (linguagem humana, regra
   inviolável), update em `ROADMAP.md §"Current status"`. **Commit split
   em 3** (facilita revisão + reverts isolados):
   - `feat(data): add frequency axis to tiingo storage + migrate script`
   - `feat(data): route tiingo source to IEX for 1h intraday with split adjust`
   - `feat(data): smoke intraday probe + unblock path docs`

### 6.2 Gate go/no-go

| Checkpoint | Critério pass (quantitativo) |
|---|---|
| **Smoke #1 RETENTION (gate de DESIGN — recalibrado por caso de uso)** | Threshold derivado do menor caso de uso viável no catálogo intraday pós-pivô: **Chan buy-on-gap** `[algo_trading_chan, p.94, ch.4]` opera com mean-reversion intraday e precisa ≥ 4.5 meses para calibrar; **Ehlers BP 1h** precisa ~40 bars de warmup + 2× o ciclo dominante ≈ 3-4 meses úteis. Portanto: **retention ≥ 6 meses (≈ 180 dias de trading)** em 1h para SPY, BTCUSD, EURUSD = PROCEED. Entre 3-6 meses = escalar ao usuário (v1 viável para Chan buy-on-gap + Ehlers, **mas cointegration pairs com CPCV N=6 precisa ~33 meses e fica deferred para v2/v3**). < 3 meses = BLOCK, voltar ao brainstorm. **Nota dado a retention pública Tiingo IEX (~2000 bars = ~83 dias em 1h):** o Cenário B de §6.3 é o default esperado. O spec mantém v1 como "infra + scheduled daily-append eventual" (§6.4 deferred) em vez de assumir janela longa. |
| Smoke #1 URL probe | 3 tickers retornam ≥1 bar com shape canonical (`open, high, low, close, volume` + datetime intraday alinhado ao início do bar) |
| Migration pgrep guard | `pgrep -f tiingo_bulk_download` retorna clean antes do script prosseguir |
| Migration backup auto | `data/tiingo_premigrate_<ts>.tar.gz` criado antes de qualquer `mv` |
| Migration dry-run | Plan mostra 1660 parquet moves + manifest rewrite, zero erros |
| Migration real | `data/tiingo/daily/` existe, `data/tiingo/prices/` removido, lockfile removido, random sample read de 10 parquets OK |
| Migration rollback test | Falha simulada em `_save_manifest` → lockfile persiste, arquivos recoveráveis, teste verde |
| Post-refactor tests | ~405/405 verdes (`uv run pytest -q`) |
| Split adjust (integração) | `adj_close` intraday = `close` × multiplier derivado do daily cache (tolerance 1e-6) em bars correspondentes |
| Smoke #2 (e2e) | Mesmo output de Smoke #1 via código novo + `adj_close` ≠ `close` em tickers com split no range |

Qualquer FAIL de checkpoint → postmortem + revisão de spec antes de
seguir. O **Smoke #1 retention** é o único checkpoint capaz de mandar
o spec de volta ao brainstorm antes do refactor começar — todos os
outros são corrigíveis durante a sessão.

### 6.3 Tempo estimado

**Cenário A — Smoke #1 retention ≥ 6 meses (spec executável conforme
descrito, com cointegration pairs possivelmente deferred):**

- Smoke #1 retention probe + URL verification: ~45 min
- Migração (testes + impl + dry-run + real + rollback test): ~120 min
- Storage refactor (testes + impl + slack per-AC): ~120 min
- Source refactor (testes + impl + split adjust logic): ~150 min
- Integração + baseline verde: ~45 min
- Smoke #2 + docs + commits (3 splits): ~45 min
- **Total: ~8-9h de sessão** (maior que v0 do spec por causa de split
  adjust + slack per-AC + guards extras).

**Cenário B — Smoke #1 retention < 3 meses (spec bloqueado):**

- Smoke #1 retention probe: ~30 min
- Escrever postmortem + pivot decision em `JORNADA.md`: ~30 min
- Re-brainstorm (scheduled daily-append ou pivot para outra fonte):
  sessão nova — ~2h antes de começar qualquer impl.
- **Total v1 abortado: ~1h** + nova rodada de brainstorming.

### 6.4 Fora de escopo (explícito)

Itens **intencionalmente** não incluídos em v1, deferidos:

- **Frequências 5m, 15m, 1min** — v1 whitelist aceita só `{daily, 1hour}`;
  outras levantam `NotImplementedError` apontando §6.6 (unblock path).
- **`index` asset class intraday** — `NotImplementedError` com mensagem
  "use ETF proxy (SPY, QQQ, DIA, IWM)".
- **Partition-by-year no parquet** (para 5m/1min futuro) — v1 layout
  `{freq}/prices/{ticker}.parquet` funciona fine em 1h (bars esparsos).
  Quando 5m/1min entrarem em v2, layout evolui para
  `{freq}/prices/{ticker}/{year}.parquet` para evitar write amplification
  (50-250 MB/parquet em 1min × 1660 tickers = 200-400 GB num arquivo).
- **Bar-count-aware coverage** (Q4-D) — requer `pandas_market_calendars`;
  slack datetime per-(asset_class, freq) resolve 95% dos casos.
- **Auto-migration on `TiingoStorage.__init__`** — nunca automático; sempre
  opt-in via `scripts/run_tiingo_migrate.py`.
- **Rate-limit throttling client-side** — v1 sem throttle; adicionar só se
  smoke/backtest bater limite Tiingo (5000/h paid).
- **Retention probing contínuo** (monitorar janela IEX ao longo do tempo) —
  v1 mede no Smoke #1 e grava; re-probing periódico fica em v2.
- **Scheduled daily-append cron** — se Smoke #1 retornar retention curta,
  este vira o caminho primário mas é spec separado (brainstorm +
  writing-plans próprios). Não faz parte de v1.
- **Strategies intraday (Chan pairs, Ehlers 1h, vol breakouts)** —
  consumidores deste infra; cada um tem spec próprio após `tiingo_service`
  verde.
- **Enforcement de holding-period gate** — §1.4 documenta o requisito mas
  quem enforça é a estratégia consumidora (infra é neutra).
- **Dollar/tick-imbalance bars** `[advances_fin_ml, p.59-62]` — time bars
  (1h) são subótimos para ML pipelines segundo AFML ch.2, mas v1 usa time
  bars por compatibilidade com o engine atual. Trade-off documentado aqui;
  dollar bars virariam spec próprio.

### 6.5 Próximos passos pós-entrega

1. Verdict documentado em `JORNADA.md` changelog (linguagem humana).
2. `ROADMAP.md §"Current status"` atualizado (`tiingo_service ✅`,
   próximo: catálogo intraday começando por Chan pairs).
3. Primeiro consumo real: um spec novo para Chan mean-reversion pairs
   em 1h (`docs/superpowers/specs/YYYY-MM-DD-chan-pairs-1h-design.md`),
   que exercita `tiingo_service` com frequency="1hour" em universo de
   stocks. O spec da estratégia referencia §1.4 deste doc para reportar
   `median_hold_hours` no diagnostic.
4. **Cancelamento da subscrição Tiingo — safe só para daily.** Dado o
   verdict do Smoke #1 retention:
   - Se retention ≥ 6 meses: intraday pode rodar offline após uma
     passada inicial de download por ticker × freq.
   - Se retention < 6 meses (inclui o caso esperado ~83 dias rolling):
     subscrição **não pode** ser cancelada enquanto intraday for parte
     do catálogo — cada backtest que precise de histórico além da janela
     atual requer API viva. **Decisão financeira (~$30-50/mês) deve ser
     escalada ao usuário**, não assumida. ROADMAP §"Next steps" item 5
     precisa ser atualizado para refletir essa condicionalidade.
   Bulk daily já em disco fica invariavelmente protegido (offline
   forever pós-migração).

5. **Bônus para Phase 4 (paper trading cTrader):** `ProtoOAGetTrendbarsReq`
   do [cTrader Open API](https://help.ctrader.com/open-api/symbol-data/)
   também retorna preço raw sem adjust. O módulo `adjust.py` +
   integração com daily cache entregue neste spec vira **ASSET
   reutilizável** para cTrader, não dívida técnica. Em Phase 4, o
   adaptador cTrader pode aplicar o mesmo ratio derivado do daily cache
   Tiingo já em disco (não dependemos de a cTrader fornecer `adj_close`).

### 6.6 Unblock path — adicionar nova frequência (ex.: 5m, 15m, 1min)

Quando uma estratégia futura precisar de `frequency="5min"` ou similar,
o spec prevê 3 passos (< 30 min cada):

1. **Adicionar entrada no `_WHITELIST`** de `tiingo_source.py`:
   ```python
   _WHITELIST_FREQUENCIES.add("5min")
   _WHITELIST_AC_FREQ.add(("equity", "5min"))  # + outras linhas
   ```

2. **Adicionar slack em `_COVERAGE_SLACK`** de `tiingo_storage.py`:
   ```python
   ("equity", "5min"): timedelta(hours=2),
   ("crypto", "5min"): timedelta(hours=1),
   # ...
   ```
   Regra prática: slack < 2 × bar_size para não mascarar gaps.

3. **Adicionar fixture + teste** em `tests/test_tiingo_source.py`:
   - Sample payload IEX 5min (5-10 linhas).
   - Teste `test_routes_equity_5min_to_iex_endpoint`.
   - Teste de retention no Smoke #1 para a nova freq.

4. **Considerar layout partition-by-year** se a nova freq é 1min (ver
   §5.8). Não trivial — requer novo spec próprio se for o caso.

Se retention em 5m for ≤ 10 dias (previsível segundo §5.2) e estratégias
precisarem de histórico longo, passo 5 (extra): planejar
`scheduled daily-append` como acréscimo ao pipeline (spec separado).

---

## 7. Referências

### 7.1 Livros / fontes externas

**Tiingo API (docs + validação por terceiros):**

| Fonte | URL | Uso |
|---|---|---|
| Tiingo IEX docs | [tiingo.com/documentation/iex](https://www.tiingo.com/documentation/iex) | URL `/iex/{ticker}/prices`, `resampleFreq` param |
| Tiingo EOD docs | [tiingo.com/documentation/end-of-day](https://www.tiingo.com/documentation/end-of-day) | `adjClose`/`divCash`/`splitFactor` em daily; CRSP adjustment methodology |
| riingo R wrapper reference | [business-science.github.io/riingo](https://business-science.github.io/riingo/reference/riingo_iex_prices.html) | Confirma retention rolling ~2000 bars em IEX |
| tiingo-python issue #117 | [github.com/hydrosquall/tiingo-python](https://github.com/hydrosquall/tiingo-python/issues/117) | Shape do endpoint `/iex/` com `resampleFreq` |
| QuantStart Tiingo review | [quantstart.com/articles/evaluating-data-coverage-with-tiingo](https://www.quantstart.com/articles/evaluating-data-coverage-with-tiingo/) | Retention + histórico IEX 1min desde 2016 |
| PortfolioOptimizer blog | [portfoliooptimizer.io/blog/selecting-a-stock-market-data-web-api-not-so-simple/](https://portfoliooptimizer.io/blog/selecting-a-stock-market-data-web-api-not-so-simple/) | Confirma IEX intraday NÃO é split/div adjusted (motiva §3.3) |

**Livros do knowledge base citados em decisões técnicas:**

| Slug | Uso |
|---|---|
| `[quant_trading_chan, p.37]` | Fórmula canônica split/dividend multiplier — aplicada em §3.3 (adjust IEX via daily cache). |
| `[trading_systems_methods, Kaufman, p.914]` | "Split-adjusted stocks lose volatility characteristics" — motiva a decisão v1 de ajustar intraday (§3.3). |
| `[ml_for_algo_trading, ch.2, p.35-40]` | Dollar bars + price-level adjustment para splits; fundamenta §3.3. |
| `[ml_for_algo_trading, ch.8, p.223-224]` | Look-ahead bias de retroactive splits; fundamenta necessidade de ajuste antecipado. |
| `[advances_fin_ml, López de Prado, p.57-63, ch.2]` | Data structures para ML financeiro (dollar bars p.57-59, tick-imbalance bars p.59-62, volume-run bars p.62-63); referenciado em §3.3. |
| `[advances_fin_ml, p.59-62]` | Tick-imbalance bars especificamente — trade-off time bars vs TIBs documentado em §6.4. |
| `[algo_trading_chan, p.4, ch.1]` | Look-ahead bias em bar-timestamp open vs close — motiva §2.6 alinhamento. |
| `[algo_trading_chan, p.10-11, ch.1]` | Primary (IEX) vs consolidated (SIP) price — documentado em §2.6 nota. |
| `[systematic_trading, Carver, p.185-188, ch.12]` | Standardised cost (SR units) vs turnover + gate "annual cost ≤ 0.13 SR/year" — motiva §1.4 (holding-period instrumentation: mediana > 48h em short-hold viola o gate de Carver). |
| `[trading_exchanges, Harris, p.33-34]` | Price priority + time precedence + tick size (microstructure de auções). **Não** session taxonomy — §2.4 documenta slack per-asset-class como decisão de engenharia sem âncora forçada. |

### 7.2 Artefatos do projeto

| Path | Uso |
|---|---|
| `.claude/CLAUDE.md` | Convenções: TDD-first, não quebrar baseline 377 testes, citação inviolável, log unificado, Conventional Commits. |
| `ROADMAP.md §"PIVOT"` + §"Next steps (post-pivot)" | Motivação e posição deste item 1 no backlog. |
| `JORNADA.md §"Pivô: intraday short-hold + tiingo_service lazy-cache"` | Narrativa humana do gatilho do pivô. |
| `docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md` | Template de spec (shape das seções 1-8). |
| `src/ai_trade/backtest/data/tiingo_source.py` | Módulo refatorado. Contém já o lazy-cache contract para daily. |
| `src/ai_trade/backtest/data/tiingo_storage.py` | Módulo refatorado. Layout atual `{prices,meta}/{ticker}` vira `{freq}/{prices,meta}/{ticker}`. |
| `tests/test_tiingo_source.py` | Pattern mock HTTP + `tmp_path` + inline payload samples. |
| `tests/test_tiingo_storage.py` | Pattern parquet fixtures + manifest roundtrip. |
| `scripts/tiingo_smoke.py` | Pattern de smoke script daily; `tiingo_smoke_intraday.py` espelha. |
| `logs/tiingo.log` | Log unificado append-only para progresso da migração e smokes. |

---

## 8. Status

**v1 — Design aprovado em 2026-04-15 (tarde) pelo usuário** (seções 1-6
revisadas em chat via `superpowers:brainstorming`).

**v2 — Design revisado em 2026-04-15 (noite) após `/judge-spec`
adversarial multi-juiz.** Veredito inicial dos juízes: **BLOCK**
(2 BLOCK + 1 PROCEED-WITH-CHANGES). Mudanças materiais aplicadas:

1. **§1.3 + §5.2 + §6.1 passo 1 + §6.2** — Smoke #1 promovido a gate de
   DESIGN com critério quantitativo (retention ≥ 12 meses). Retention
   IEX corrigida de "~2a" para "~2000 bars rolling = ~83 dias em 1h",
   com URLs.
2. **§3.3 (nova)** — `adj_close := close` movido de caveat v1.1 para
   decisão v1 consciente: aplicar `splitFactor`/`divCash` do daily cache
   ao IEX intraday em pós-processamento. `NotImplementedError` explícito
   se equity não está no daily cache. Adiciona 5 citações que faltavam.
3. **§1.4 (nova)** — Holding-period instrumentation: `median_hold_hours`/
   `max_hold_hours` obrigatórios em diagnostic de toda estratégia
   intraday futura (gate para evitar repetir pivô em resolução maior).
4. **§2.4** — Slack upgrade de `{daily: 7d, 1hour: 1d}` para per-
   `(asset_class, freq)` — crypto 24/7, forex weekend-close, equity
   RTH tratados estruturalmente, não como edge case.
5. **§2.5** — `requested_range` tracking no manifest em v1, não v2
   (dado retention curta, custo de não trackear é maior).
6. **§2.4** — `has()` aceita `date | datetime` em v1 (não post-v1).
7. **§2.6** — Bar timestamp convention + IEX primary-vs-consolidated
   documentados com citações.
8. **§3.5 + §4** — Migração ganha `pgrep` guard (bloqueia se bulk
   ativo) + backup automático opt-out + lockfile + teste de rollback.
9. **§6.1 passo 8** — Commit single virou split em 3 (storage + source
   + smoke/docs).
10. **§6.5 item 4** — Cancelamento de subscrição Tiingo explicitamente
    safe só para daily (intraday requer API viva se retention curta).
11. **§6.6 (nova)** — Unblock path documentado para adicionar 5m/15m/1min
    em < 30 min cada.
12. **§7.1** — URLs concretas para todas as fontes Tiingo + docs
    terceiros + 10 citações novas de livros do knowledge base.

**Relatórios dos juízes (v1 → v2):**
`reports/spec-judges/2026-04-15-tiingo-service-lazy-cache-design-20260415-170020/`
(methodology.md, domain.md, strategic.md, arbiter.md).

---

**v3 — Design revisado em 2026-04-15 (noite, 2ª rodada) após segundo
`/judge-spec`.** Veredito: **PROCEED-WITH-CHANGES** (3/3 juízes
unânimes, sem 🔴, upgrade significativo vs v1). 5 correções cirúrgicas
aplicadas:

1. **§3.3 fórmula corrigida.** v2 usava
   `cumprod(splitFactor) − cumsum(divCash × splitFactor)` — **subtração
   separada de dividendo, que `[quant_trading_chan, p.37]` explicitamente
   veda**. v3 reusa `src/ai_trade/backtest/data/adjust.py` existente
   (approach ratio `adj_close_daily / close_daily`, derivado
   por-dia-de-calendário e aplicado às bars intraday do mesmo dia).
   Matematicamente equivalente a Chan p.37 (subtração acontece **dentro**
   do multiplier, não como termo separado).
2. **§6.2 gate recalibrado.** v2 exigia `retention ≥ 365d` — **impossível
   em 1h** dado retention pública ~83 dias (§5.2), criando contradição
   interna. v3 threshold = `≥ 6 meses` derivado do menor caso de uso
   viável (Chan buy-on-gap 4.5m + Ehlers 1h 3-4m). Entre 3-6m = escalar
   ao usuário (cointegration pairs com CPCV N=6 precisa ~33m e fica
   deferred). §1.3 Cenário B (brainstorm `scheduled daily-append`) agora
   admitido como desfecho **esperado**, não exceção.
3. **3 citações corrigidas (violação Regra 2):**
   - `[advances_fin_ml, ch.3]` → `[advances_fin_ml, p.57-63, ch.2]`
     (data structures).
   - `[trading_exchanges, Harris, p.33-34]` em §2.4 removido como âncora
     de session taxonomy — Harris p.33-34 é price priority + time
     precedence, **não** sessões. Slack documentado como decisão de
     engenharia sem âncora forçada.
   - `[systematic_trading, Carver, p.32-35]` → `[systematic_trading,
     Carver, p.185-188, ch.12]` (cost/turnover, não skew).
4. **§6.5 item 5 novo — bônus cTrader.** `ProtoOAGetTrendbarsReq` do
   cTrader Open API também retorna raw. O módulo `adjust.py` +
   integração com daily cache vira **asset reutilizável** para Phase 4
   paper trading, não dívida técnica.
5. **§2.7 diagrama atualizado.** `_COVERAGE_SLACK_BY_FREQ` (v1 format)
   → `_COVERAGE_SLACK: dict[(asset_class, freq), timedelta]` + menção a
   `requested_range` no manifest.

**Relatórios dos juízes (v2 → v3):**
`reports/spec-judges/2026-04-15-tiingo-service-lazy-cache-design-v2-20260415-172540/`.

---

**v3.1 — Smoke #1 empírico executado em 2026-04-15 17:47
(`scripts/tiingo_smoke_intraday.py`).** Veredito: **PASS (Cenário A)**.

Retention observada na subscrição paid do projeto:

| Ticker | Asset | Bars | Retention | vs threshold 180d |
|---|---|---|---|---|
| SPY | equity IEX | 7824 | 1825d (5 anos) | ✅✅✅ (~10×) |
| btcusd | crypto | 5001 | 208d | ✅ (apertado) |
| eurusd | forex | 6948 | 416d | ✅ (~2.3×) |

**Pior caso 208d ≥ 180d threshold = PROCEED Cenário A.**

Descobertas empíricas importantes:

- **Equity IEX superou docs públicos em ~22×** (1825d real vs 83d
  documentado). A limitação rolling de "~2000 bars" parece aplicar a
  tiers gratuitos ou tickers menos líquidos — não à subscrição paid em
  SPY.
- **Crypto tem cap real em ~5000 bars** (24/7 × 1h × 208d ≈ 5001).
  Este é o binding constraint real do caso de uso — ainda suficiente
  para Chan buy-on-gap (4.5m) e Ehlers 1h (3-4m), mas **cointegration
  pairs com CPCV N=6 (~33m necessários) permanece deferred** para v2
  com scheduled daily-append para crypto.
- **Forex oferece janela confortável** (416d calendário incluindo
  weekends sem bars).

Log auditável em `logs/tiingo.log` linha 2026-04-15 17:47.

**Próximo passo:** spec pronto para `superpowers:writing-plans`
(produzir plan de implementação seguindo padrão
`docs/superpowers/plans/2026-04-15-f3d-portfolio-clenow-ehlers.md`).
