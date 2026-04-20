# Ops Platform — Plano B (MVP) — Design Spec

> **Status:** Draft — aguardando review do usuário antes de virar plan.
> **Data:** 2026-04-20.
> **Escopo:** MVP operacional para controlar trades, DARFs e benchmarks
> do Plano B, com schema multi-account pronto para Plano A (futuro) e
> Plano C. Path tag: `[SWING BROKER]` (Plano B Inter Global).
> **Fora de escopo:** integração automática com Inter API, execução
> automática de ordens, UI web, Plano A features específicas (margin,
> swap, leverage). Todas essas são Phase 5+.

---

## 1. Motivação

Com Plano B autorizado pra deploy (winner Portfolio 3-leg EW SSO+QLD+UGL,
Sharpe 2.108 / CAGR 25.56%, `reports/phase3_5b/PRODUCTION.md`) e Plano A
com winner próprio (Gayed EMA100/L2/off-GLD,
`docs/strategies/plano_a_v2_l2_gayed_cfd.md`), falta um sistema
operacional pra:

- Registrar cada trade executado manualmente no Inter Global (Plano B) ou
  cTrader (Plano A futuro).
- Calcular DARFs com precisão fiscal, respeitando carryforward de
  prejuízo (Lei 11033/2004 regime antigo) ou apuração anual unificada
  (Lei 14.754/2023 regime atual).
- Rastrear dividendos de ETFs externos (SSO/QLD/UGL) com PTAX correto.
- Comparar performance real contra SP500 (em BRL), IBOV, IPCA e SELIC.
- Servir de fonte de verdade fiscal — a Receita não aceita informe do
  broker como única evidência (Lei 14.754, Art. 4°); investidor precisa
  manter registro próprio. Investment Mandate §4.7.2:
  > "Inter fornece Informe de Rendimentos Global Account mas com
  > histórico documentado de atrasos/indisponibilidade. Responsabilidade
  > do investidor: manter planilha própria."

## 2. Requisitos (locked nas Q1-Q6 do brainstorm)

### Q1 — Escopo multi-account desde dia 1

Schema tem `broker`, `account_id`, `strategy`, `instrument_domicile` em
todo trade. Plano A e Plano C entram adicionando linhas, zero migration.

### Q2 — FX tracking via BCB SGS série 1 (PTAX venda)

Auto-fetch no trade entry com fallback manual via `--ptax 5.1234`.
Cache persistente (`fx_cache.csv`). Feriado/fim-de-semana: usa PTAX do
último dia útil anterior (convenção Receita).

### Q3 — Flat CSV files

`ops/data/*.csv` com `# schema_version: N` na primeira linha. Atomic
writes via write-to-tmp + rename. Flock single-writer. Volume esperado
~500 trades em 10 anos.

### Q4 — Loss carryforward completo

Carryforward de prejuízo modelado. Streams separadas por regime:

- **Monthly 6015 (legacy):** swing e daytrade em streams independentes.
- **Annual 14754 (atual):** stream unificada `rendimentos` (ganho de
  capital + dividendos) com carryforward ilimitado entre anos
  (Art. 3°, §5).

### Q5 — Dividend tracking sem auto-Carnê-Leão

Schema `dividends.csv` registra bruto + withholding IRS + PTAX. Sistema
alerta no `add` mas não calcula alíquota progressiva (dependente da
renda total do usuário — fica com contador/Excel próprio). No regime
Lei 14.754, dividendos entram automaticamente no cálculo anual.

### Q6 — Benchmarks hybrid (quick + full)

- `ops status` — tabela compacta CLI.
- `ops benchmark report` — markdown + CSV + PNG opcional.
- Fontes: SPY USD (Tiingo cache existente) × PTAX para S&P500 em BRL;
  IVVB11.SA (yfinance) para S&P500 em BRL com hedge parcial real do
  investidor BR; ^BVSP (yfinance) para IBOV; BCB SGS 433 para IPCA
  mensal; BCB SGS 11 para SELIC diária acumulada; BCB SGS 1178 para
  SELIC meta.
- Todos os equity curves reindexados a base 100 no `inception_date`
  (primeira compra de cada strategy).

### Regime fiscal — α: dois plugins

Lei 14.754/2023 criou regime anual para aplicações no exterior (default
desde 2024-01-01), mas project docs citam regime mensal DARF 6015. Como
Inter Global pode emitir informe em qualquer um dos dois modelos,
MVP implementa **ambos** como plugins:

- `ops/core/tax/regime_monthly_6015.py`
- `ops/core/tax/regime_annual_14754.py`

Flag `--regime` no CLI + default configurável em `config.yaml`. Usuário
confirma com contador/Inter antes do primeiro DARF real; antes disso,
roda os dois em `preview` e compara.

## 3. Arquitetura

**Layout:** split `core` (business logic pura, testável sem I/O) +
`cli` (typer wrapper fino).

```
ops/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── models.py               # dataclasses: Trade, Dividend, DarfEvent, ...
│   ├── storage.py              # CSV read/write atomic + schema check + lock
│   ├── fx.py                   # BCB SGS série 1 client + cache
│   ├── tax/
│   │   ├── __init__.py         # factory get_regime(name)
│   │   ├── base.py             # ABC TaxRegime
│   │   ├── regime_monthly_6015.py
│   │   └── regime_annual_14754.py
│   ├── positions.py            # FIFO lot matching, current positions
│   ├── benchmarks.py           # fetchers + equity curve normalizer
│   └── reports.py              # markdown + chart renderers
├── cli/
│   ├── __init__.py
│   ├── main.py                 # typer app `ops`
│   ├── trade.py                # ops trade add/list/show/delete/edit
│   ├── dividend.py             # ops dividend add/list
│   ├── darf.py                 # ops darf preview/close/list/show/paid/carryforward
│   ├── benchmark.py            # ops benchmark fetch/report/compare
│   ├── signal.py               # ops signal check/history
│   ├── status.py               # ops status
│   └── export.py               # ops export trades/darf-year/backup
├── data/                       # GITIGNORED
│   ├── .gitkeep
│   ├── .lock
│   ├── trades.csv
│   ├── dividends.csv
│   ├── fx_cache.csv
│   ├── benchmarks_cache.csv
│   ├── darf_history.csv
│   └── carryforward.csv
├── tests/
│   ├── fixtures/
│   │   └── example_plano_b_2026/
│   ├── test_storage.py
│   ├── test_fx.py
│   ├── test_positions.py
│   ├── test_benchmarks.py
│   ├── test_reports.py
│   ├── test_tax/
│   │   ├── test_regime_monthly_6015.py
│   │   └── test_regime_annual_14754.py
│   ├── cli/
│   │   ├── test_smoke_trade.py
│   │   ├── test_smoke_darf.py
│   │   └── test_smoke_benchmark.py
│   ├── test_e2e_plano_b_workflow.py
│   └── test_bcb_live.py        # marked live_api, roda só manual
└── README.md
```

**Dependências externas** (adicionar em `pyproject.toml` como extra
`ops`):

- `typer` — CLI
- `pandas` — CSV + time series
- `requests` — BCB SGS + yfinance fallback HTTP
- `yfinance` — IBOV, IVVB11
- `matplotlib` — chart opcional
- `holidays` — feriados BR
- `cryptography` — encrypted backup
- Reusa: `src/ai_trade/backtest/data/tiingo_cache` (SPY), constantes
  fiscais do Investment Mandate.

## 4. Data model (schemas CSV)

Todos os CSVs:
- Primeira linha: `# schema_version: 1`.
- Segunda linha: header com nomes de coluna.
- Encoding UTF-8.
- Decimal via ponto, 8 casas em cálculos intermediários, 2 casas no
  render final com `ROUND_HALF_UP` (ou `ROUND_UP` para tax due —
  conservador).

### 4.1 trades.csv

| Coluna | Tipo | Enum / Validação | Nota |
|---|---|---|---|
| `trade_id` | str | formato `T-YYYYMMDD-NNN` | único |
| `date` | ISO date | | data de execução |
| `broker` | str | `inter_global`, `pepperstone`, `xp`, `nuinvest`, `manual` | |
| `account_id` | str | identificador estável do broker | |
| `strategy` | str | `plano_a`, `plano_b`, `plano_c`, `manual` | `manual` = trades fora dos 3 planos (ex: VOO pessoal), não entra em report de strategy |
| `ticker` | str | símbolo | |
| `instrument_type` | str | `etf`, `stock`, `fii`, `bdr`, `cfd`, `cash` | |
| `instrument_domicile` | str | `us`, `br`, `other` | dita regime aplicável |
| `side` | str | `buy`, `sell` | |
| `qty` | Decimal | > 0 | fracionárias suportadas |
| `price_native` | Decimal | > 0 | no mercado nativo |
| `currency` | str | ISO 4217 (`USD`, `BRL`) | |
| `fees_native` | Decimal | ≥ 0 | Inter = 0 |
| `ptax_venda` | Decimal | > 0 | `1.0` se BRL |
| `cost_basis_brl` | Decimal | ≥ 0 | só para buy; computed |
| `gross_brl` | Decimal | ≥ 0 | só para sell; computed |
| `realized_gain_brl` | Decimal | | só para sell; pode ser < 0 |
| `trade_type` | str | `swing`, `daytrade` | só importa regime mensal |
| `notes` | str | | livre |

**Lot matching FIFO** dentro de `(broker, account_id, ticker)` conforme
IN RFB 1.585/2015, Art. 58.

**Soft delete:** campo implícito `deleted` via notes tag
`[DELETED:YYYY-MM-DD]`; linha permanece pra audit trail fiscal.

### 4.2 dividends.csv

| Coluna | Tipo | Nota |
|---|---|---|
| `dividend_id` | str | `D-YYYYMMDD-NNN` |
| `payment_date` | ISO date | quando virou available |
| `broker` | str | |
| `account_id` | str | |
| `ticker` | str | |
| `gross_usd` | Decimal | bruto distribuído |
| `withheld_us_tax_usd` | Decimal | 30% retenção IRS (padrão BR sem treaty) |
| `net_usd` | Decimal | = gross - withheld |
| `ptax_venda` | Decimal | PTAX da payment_date |
| `gross_brl` | Decimal | computed |
| `withheld_us_tax_brl` | Decimal | computed |
| `net_brl` | Decimal | computed |
| `notes` | str | |

### 4.3 fx_cache.csv

| Coluna | Tipo | Nota |
|---|---|---|
| `date` | ISO date | PK |
| `ptax_venda` | Decimal | R$/USD |
| `source` | str | `bcb_sgs_1`, `manual` |
| `fetched_at` | ISO datetime | UTC |

### 4.4 benchmarks_cache.csv — long format

| Coluna | Tipo | Nota |
|---|---|---|
| `date` | ISO date | |
| `series_id` | str | `spy_usd`, `ivvb11_brl`, `ibov_brl`, `ipca_pct_monthly`, `selic_daily_pct`, `selic_meta_annual` |
| `value` | Decimal | |
| `source` | str | `tiingo`, `bcb_sgs_1/11/433/1178`, `yfinance`, `computed` |
| `fetched_at` | ISO datetime | |

`spy_brl_derived` computado on-the-fly (`spy_usd × ptax`) — não
armazenado.

### 4.5 darf_history.csv — append-only

| Coluna | Tipo | Nota |
|---|---|---|
| `darf_id` | str | `DARF-M-YYYYMM` monthly, `DARF-A-YYYY` annual |
| `regime` | str | `monthly_6015`, `annual_14754` |
| `period_start` | ISO date | |
| `period_end` | ISO date | |
| `due_date` | ISO date | último útil mês seguinte / 2027-04-30 |
| `code` | str | regime-specific; ver nota abaixo |
| `stream` | str | `swing`, `daytrade`, `rendimentos` |
| `gross_gain_brl` | Decimal | antes carryforward |
| `dividends_brl` | Decimal | 0 em monthly, soma em annual |
| `loss_offset_brl` | Decimal | consumido do carryforward |
| `net_taxable_brl` | Decimal | = gross_gain + dividends - loss_offset |
| `tax_rate_applied` | Decimal | 0.15 |
| `tax_due_brl` | Decimal | arredondado pra cima |
| `paid_at` | ISO date | opcional |
| `paid_proof_path` | str | opcional |
| `notes` | str | |

### 4.6 carryforward.csv

| Coluna | Tipo | Nota |
|---|---|---|
| `regime` | str | |
| `stream` | str | |
| `period` | str | `YYYY-MM` monthly, `YYYY` annual |
| `balance_in` | Decimal | ≥ 0 |
| `accrued_this_period` | Decimal | ≥ 0 |
| `consumed_this_period` | Decimal | ≥ 0 |
| `balance_out` | Decimal | ≥ 0 |

Invariante: `balance_out = balance_in + accrued - consumed ≥ 0`.

**Nota sobre `code`:** O campo aceita string livre porque os códigos
variam com o regime e com a interpretação da Receita/contador:

- `monthly_6015` default → `"6015"` (renda variável, swing) ou
  `"8523"` (day-trade).
- `annual_14754` default → `"0211"` (cota única IRPF anual) — mas o
  recolhimento real flui pelo IRPF do ano seguinte, sem DARF próprio
  obrigatório exceto se o investidor optar por antecipar. Valor também
  aceito: `"4600"` (código legacy ganho de capital moeda estrangeira)
  quando Inter emitir informe no formato antigo. Usuário confirma com
  contador antes do primeiro DARF real.

### 4.7 config.yaml

```yaml
schema_version: 1
default_regime: annual_14754       # ou monthly_6015
default_broker: inter_global
default_strategy: plano_b
default_account_id: inter_global_PLACEHOLDER
inception_date: null                # setado no primeiro trade por strategy
benchmarks:
  enabled: [spy_usd, ivvb11_brl, ibov_brl, ipca_pct_monthly, selic_daily_pct]
fx:
  cache_ttl_days: 365
bcb_api:
  base_url: https://api.bcb.gov.br/dados/serie
  timeout_sec: 10
tiingo:
  use_existing_cache: true
```

## 5. CLI surface

Entry point `ops` (installed via `pyproject.toml` script). Typer app
com 7 grupos:

| Grupo | Comandos principais |
|---|---|
| global | `ops init`, `ops config show/set`, `ops status`, `ops version` |
| trade | `add`, `list`, `show`, `delete`, `edit` |
| dividend | `add`, `list` |
| darf | `preview`, `close`, `list`, `show`, `paid`, `carryforward`, `recompute` |
| benchmark | `fetch`, `report`, `compare` |
| signal | `check`, `history` |
| export | `trades`, `darf-year`, `backup` |

Total ~25 subcomandos. Todos com `--help` gerado pelo typer.

## 6. Error handling

**Fiscal (zero-tolerance):** fail-loud em qualquer ambiguidade.
Exemplos críticos:

- Sell sem qty FIFO suficiente → abort.
- PTAX ausente + BCB API down + sem `--ptax` manual → abort.
- DARF close rodado 2x pro mesmo período → abort, exige `darf recompute
  --confirm`.
- Trade delete em trade dentro de DARF fechado → abort, exige
  `darf unfile --confirm` primeiro.
- Schema version mismatch → abort até migration rodar.

**Operacional (tolerante):** warn + continue onde recuperável.
Exemplos:

- Benchmark fetch parcial falho → continua os que deram certo.
- Tiingo cache miss em data isolada → pula ponto no curve.
- Config file ausente → auto-cria default + warn.
- `.lock` de PID morto → remove + continua.

**Precisão:** `Decimal` (contexto 28 dígitos) em finance; float só em
stats (Sharpe, retornos). Render final `.quantize(Decimal("0.01"))`
com `ROUND_HALF_UP` geral, `ROUND_UP` em tax due.

**Calendário:** lib `holidays` (feriados BR bancários) para
`due_date` e fallback PTAX. Timezone `America/Sao_Paulo` pra dates
operacionais; UTC pra timestamps.

**Segurança:**

- `ops/data/**` em `.gitignore`.
- Pre-commit hook rejeita commit que staged qualquer `ops/data/*.csv`.
- `ops export backup --password` usa AES-256 (PBKDF2) via
  `cryptography` lib.
- Logs estruturados em `ops/data/.log`; nunca dumpa valores BRL de
  trades individuais.

## 7. Testing strategy

Baseline: **pytest 796+ do projeto preservado intocado.** Nova suite
`ops/tests/` adicionada ao collect.

| Camada | Cobertura | Técnica |
|---|---|---|
| Unit core | 80%+ geral | pytest + fixtures |
| Golden fiscal | `tax/` 95%+ | `fixtures/example_plano_b_2026/` + hardcoded DARFs esperados |
| CLI smoke | 60%+ | `typer.testing.CliRunner` em tmp dir |
| E2E | 1 full workflow | `requests_mock` stubando BCB; ~2s |
| Property-based | opcional Phase 2 | `hypothesis` para FIFO invariants |
| Live API | manual only | `@pytest.mark.live_api` contra BCB real |

**Zero network em pytest** — tudo mocked. `test_bcb_live.py` roda só
com `pytest -m live_api`.

## 8. README do `ops/` (obrigatório no delivery)

Documenta consolidado:

- Q1-Q6 (decisões com racional).
- Os dois regimes fiscais com diferenças + quando usar cada um.
- Workflow típico Plano B (init → primeira compra → signal check diário
  → rebalance → DARF mensal/anual).
- Fontes dos benchmarks + onde ver PTAX histórica.
- Como fazer backup criptografado.
- Como adicionar Plano A/C futuramente (o que mudar).
- DARF codes explicados (6015, 4600, 0190).
- Citações da legislação (Lei 11033/2004, Lei 14.754/2023,
  IN RFB 1.585/2015).

Esse README é **artefato de entrega** — tão crítico quanto o código.

## 9. Plano de entrega sugerido (pra virar plan)

Particionável em ~8-10 commits, cada um com tests passing:

1. **Scaffolding + storage + models** (CSV schemas + atomic writes +
   lock + models).
2. **FX module + BCB SGS client** (cache + manual override + feriados).
3. **Tax regime monthly_6015** (carryforward swing/daytrade + DARF).
4. **Tax regime annual_14754** (carryforward anual unificado +
   dividendos no bucket).
5. **Positions + FIFO lot matching** (positions module completo).
6. **CLI scaffolding + trade group** (add, list, show, delete, edit).
7. **CLI dividend + darf groups** (preview, close, paid, carryforward).
8. **Benchmarks fetchers** (Tiingo reuse + BCB SGS 433/11/1178 +
   yfinance IBOV/IVVB11).
9. **CLI benchmark + status groups** (report, compare, status).
10. **CLI signal + export + config + init** (signal check Plano B,
    export backup encrypted, init wizard, config get/set).
11. **README + golden fixture completa + e2e test**.

Commits 1-5 são backend-only (testes unit); 6-11 integram CLI. Cada
commit mantém pytest baseline verde (≥ 796 atual + ops/tests/ novos).

**Split opcional em duas tranches** se o usuário preferir entregar em
duas pulls menores:

- **MVP-1 (commits 1-7):** core + trade/dividend/darf. Já permite
  registrar trades, calcular DARFs nos dois regimes, rastrear
  dividendos. Plano B operacional fiscalmente.
- **MVP-2 (commits 8-11):** benchmarks + signal + status + export +
  README completo. Polish operacional e visibilidade vs mercado.

Padrão recomendado: **tranche única** — MVP-2 sem status/benchmark
descaracteriza a plataforma como sistema de acompanhamento. Mas split
é opção válida se prazo apertar.

## 10. Riscos e decisões deferidas

**Risco 1 — regime fiscal errado.** Mitigação: α dois regimes
plugáveis. Usuário confirma com Inter/contador nos primeiros 3 meses
paper/small money antes do primeiro DARF real.

**Risco 2 — PTAX fetch unreliable.** Mitigação: cache permanente +
fallback manual `--ptax`. BCB SGS historicamente 99.9% uptime.

**Risco 3 — tamanho do CSV grande no futuro.** Mitigação: YAGNI.
500 trades em 10 anos é trivial. Se 10k+, migration pra SQLite é
script de 20 LoC.

**Risco 4 — Inter mudar regime no meio do caminho.** Mitigação: todos
DARFs no history registram `regime` explicitamente. `ops darf
recompute --regime=annual_14754 --since 2026-01-01 --confirm` permite
reprocessar tudo.

**Deferido pra Phase 5+:**

- Integração automática Inter API (se existir eventualmente).
- UI web (FastAPI + HTMX + SQLite).
- Plano A features: margin, swap diário, leverage tracker, CFD P&L
  daily mark-to-market.
- Plano C: portfolio tracker factor-based.
- Tax doc generation PDF (usa sicalcnet só pra DARF real; pro IRPF
  completo o user usa o programa da Receita).

## 11. Citações

- Lei 11033/2004 — regime mensal pré-2024 de renda variável.
- Lei 14.754/2023 — regime anual de rendimentos no exterior (vigente).
- IN RFB 1.585/2015, Art. 58 — FIFO lot matching.
- `docs/investment-mandate.md` §4.7.2 — regra fiscal base Plano B.
- `reports/phase3_5b/PRODUCTION.md` §2, §5.1, §7 — Inter Global
  operational notes, T+1.
- `reports/phase3_5b/variants/rebalance_modes/implementation_notes.md`
  §7 — limitations modeladas.
- `jornada/2026-04-19/09-t+1-settlement-caveat-plano-b.md` — caveat
  T+1 registrado.
- `books/summaries/advances_fin_ml.md, p.275-278` — institutional
  rebalance drift-triggered rules (fundamenta threshold 10pp).

---

**Fim do design spec.** Próximo passo: user review + transição pra
`superpowers:writing-plans` para gerar plano de implementação commit
por commit.
