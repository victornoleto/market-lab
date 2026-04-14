# ai-trade — Systematic Swing-Trading para Pepperstone CFD

Sistema automatizado de trading sistemático para **CFDs Pepperstone via cTrader
Open API**, fundamentado em **33 livros de trading quantitativo/ML absorvidos**
como uma Claude Skill (knowledge base citável). Todo código é determinístico e
toda decisão remete a `[livro.slug, p.X]`.

**Regra de ouro:** nenhuma afirmação, estratégia, parâmetro ou gate sem
referência ao livro. Alucinação destrói o valor da knowledge base — e, em
live, destrói capital.

---

## Status

| Fase | Escopo | Estado |
|---|---|---|
| 0 | Knowledge base — 33 livros → summaries validados | ✅ Concluída |
| 0.5 | `build_skill.py` + gate de sanidade da skill | ✅ Concluída |
| 1 | Infra Pepperstone/cTrader + Postgres/Grafana | 🔄 Scaffold (aguarda aprovação Spotware para OAuth) |
| 2 | Backtest Module — engine + validation + métricas + Clenow replication | ✅ Concluída |
| 2.5 | Strategy Engine (Universe Selector + candidatas fundamentadas) | ⏳ |
| 3 | Backtest rigoroso (grid de parâmetros + gates CPCV/PBO/DSR em produção) | ⏳ |
| 4 | Paper trading (conta demo cTrader) | ⏳ |
| 5 | Live trading ($1000 inicial) | ⏳ |
| 6 | Monitoring + governança | ⏳ |
| 7 | Scaling | ⏳ |

Detalhes por fase em [`ROADMAP.md`](ROADMAP.md). Plano geral do sistema em
[`TRADING_SYSTEM_PLAN.md`](TRADING_SYSTEM_PLAN.md).

---

## Arquitetura em alto nível

```
         Phase 0 — knowledge base (concluída)              Phase 1+ — runtime (parcial)

books/raw/    ─▶ summaries/    ─▶ knowledge/               cTrader Open API ◀──▶ src/ai_trade/
(33 PDFs)        (33 MD, 9 sec)    SKILL.md                (Protobuf/OAuth2)      (Python/Twisted)
                                   + books/                                             │
                                   + strategies/                                        ▼
                                   + indicators/                                  Postgres + Grafana
                                   + validation/                                  (docker-compose)
```

- Python NÃO usa nenhum LLM SDK. Toda inteligência LLM roda dentro do
  **Claude Code CLI** (subagentes + slash commands).
- Scripts em `scripts/` e módulos em `src/ai_trade/` são determinísticos.

---

## Estrutura do repositório

```
ai-trade/
├── books/                           # Knowledge base bruta (Fase 0)
│   ├── raw/                         # 33 PDFs com slugs canônicos
│   ├── summaries/                   # 1 MD validado por livro
│   ├── code/                        # Código C++ complementar (Timothy Masters)
│   ├── MAPPING.md                   # Inventário "nome original → slug"
│   └── README.md                    # Catálogo + qualidade + pipeline de absorção
├── knowledge/                       # Claude Skill agregada (Fase 0.5)
│   ├── SKILL.md                     # Entry point + inviolable rules
│   ├── books/                       # Per-book summaries (cópia validada)
│   ├── strategies/                  # Agregações temáticas (momentum, cycles, ...)
│   ├── indicators/                  # Ehlers DSP, momentum, HMM
│   └── validation/                  # CPCV, permutation, DSR, walk-forward
├── src/ai_trade/                    # Runtime Python (Fase 1+)
│   ├── __init__.py
│   ├── config.py                    # Typed config (pydantic-settings)
│   └── backtest/                    # Fase 2 — módulo de backtest (173 tests)
│       ├── data/                    #   yfinance + Wikipedia SPX point-in-time
│       ├── engine/                  #   portfolio + execução CFD-aware + runner
│       ├── validation/              #   CPCV / PBO / DSR / walk-forward / MCPT
│       ├── metrics/                 #   Sharpe/Sortino/Calmar + report MD+PNG
│       └── strategies/              #   base + Clenow momentum replication
├── scripts/                         # Utilitários determinísticos (sem LLM)
│   ├── extract_pdfs.py              # PDF → texto + capítulos + metadata
│   ├── validate_summary.py          # Gate estrutural de summaries
│   ├── check_citations.py           # Verifica offset PDF↔printed + citações
│   ├── build_page_index.py          # Gera _page_index.json por livro
│   ├── aggregate_judges.py          # Agrega juízes adversariais (Layer-3)
│   ├── build_skill.py               # Summaries → knowledge/
│   ├── compress_pdfs.py             # Ghostscript compressor (reversível)
│   ├── rename_books.py              # Normaliza slugs em books/raw/
│   ├── ctrader_oauth_bootstrap.py   # OAuth2 one-time bootstrap (browser local)
│   └── run_clenow_replication.py    # CLI de replicação Clenow momentum (Fase 2)
├── db/
│   └── init.sql                     # Schemas Postgres: market_data, trades, ...
├── docker-compose.yml               # Postgres 16 + Grafana 11
├── .env.example                     # Template de credenciais/tokens
├── pyproject.toml                   # Deps + hatch config
├── ROADMAP.md                       # Mapa de fases
├── TRADING_SYSTEM_PLAN.md           # Plano geral com justificativa por decisão
└── README.md                        # este arquivo
```

---

## Requisitos

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recomendado) ou `pip`
- Docker + Docker Compose (para Postgres/Grafana locais)
- Claude Code CLI (para expandir a knowledge base ou re-absorver livros via
  `/absorb-book`; não é necessário para o runtime da Fase 1+)

---

## Setup

### Python

```bash
uv sync
# ou: python -m venv .venv && .venv/bin/pip install -e .
```

### Infra local (Postgres + Grafana)

```bash
docker compose up -d postgres grafana
docker compose exec postgres psql -U ai_trade -d ai_trade -c "\dn"
# deve listar: market_data, trades, features, logs, backtest_runs
```

**Portas:**
- Postgres: `localhost:5435` (mapeia → container 5432; `5432` local fica para o Postgres nativo, se houver)
- Grafana: `http://localhost:3000` (login `admin` / `ai_trade`)

Parar sem apagar dados: `docker compose down`. Zerar tudo: `docker compose down -v`.

### cTrader OAuth (one-time, após aprovação Spotware do app)

```bash
cp .env.example .env
# preencha CTRADER_CLIENT_ID e CTRADER_CLIENT_SECRET (do portal Spotware)
python scripts/ctrader_oauth_bootstrap.py
# abre browser → consent screen → captura refresh_token → escreve no .env
```

O app precisa estar aprovado pela Spotware (manual, horas a dias após submissão
em `openapi.ctrader.com`). Enquanto não aprovado, o bootstrap falha com
*"OA client is not in active state"*.

---

## Como rodar um backtest

Fase 2 entregou o módulo completo de backtest em `src/ai_trade/backtest/`:
engine (portfolio + execução CFD-aware + runner bar-by-bar), validation
framework (CPCV / PBO / DSR / walk-forward / MCPT), métricas (Sharpe /
Sortino / Calmar / CAGR / max DD / VaR) e gerador de report em markdown +
PNG. Replicação de referência: Andreas Clenow `stocks_on_the_move` no
universo SPX 500 point-in-time (yfinance + Wikipedia scrape).

```bash
.venv/bin/python scripts/run_clenow_replication.py \
    --start 2023-07-01 \
    --end 2023-12-31 \
    --cash 100000 \
    --output-dir reports/
```

Saídas:
- `reports/clenow_momentum_<YYYYMMDD-HHMM>.md` — relatório estruturado com
  disclaimer obrigatório de survivorship bias, métricas anualizadas,
  walk-forward summary e lista de trades (top winners/losers)
- `reports/assets/*.png` — equity curve + underwater drawdown (2 painéis,
  backend Agg headless)

Componentes (cobertos por 173 testes com verificação numérica contra os
livros-fonte):
- `backtest/engine/` — `portfolio.py` / `execution.py` / `runner.py`
- `backtest/validation/` — `cpcv.py` / `pbo.py` / `dsr.py` /
  `walk_forward.py` / `permutation.py`
- `backtest/metrics/` — `performance.py` / `report.py`
- `backtest/strategies/` — `base.py` / `clenow_momentum.py`

Notas da replicação (performance vs livro, limitações, decisões de design):
[`reports/clenow_replication_notes.md`](reports/clenow_replication_notes.md).
Spec executável da Fase 2 com campo Conclusão por task:
[`specs/backtest_phase2.md`](specs/backtest_phase2.md).

**Gate crítico:** todo report gerado de fonte `yfinance`/`wikipedia` inclui
disclaimer de survivorship bias obrigatório (inviolable rule do ROADMAP).
Migração para fonte paga (Tiingo/EOD/Norgate) é decisão adiada até a
primeira estratégia sobreviver a um grid com PBO < 0.5 e DSR p-value < 0.05
— ver [`specs/backtest_phase2.md`](specs/backtest_phase2.md#reavaliação-pós-fase-2-decisões-adiadas-do-roadmap).

---

## Como rodar o grid (Fase 2.5/3)

Módulo `src/ai_trade/backtest/grid/` estende a Fase 2 com infraestrutura
para rodar um grid de configurações de estratégia com gates anti-overfit
ativos (PBO / DSR / walk-forward). Um novo CLI orquestra fetch + grid
paralelo (joblib) + walk-forward + gate evaluation + report/diagnóstico:

```bash
.venv/bin/python scripts/run_grid_clenow.py \
    --start 2015-01-01 --end 2023-12-31 \
    --cash 100000 --output-dir reports/ \
    --n-jobs 4
```

Acompanhar execução em tempo real (log unificado — um único `tail -f`
para qualquer run, presente ou futura):

```bash
tail -f logs/grid.log
cat logs/grid_latest_status.md  # snapshot high-level da última run
```

**Saídas:**
- `reports/grid_<YYYYMMDD-HHMM>/summary.md` (se gates passam) OU
  `diagnostic.md` (se falham) — incluem disclaimer de survivorship
- `reports/grid_<YYYYMMDD-HHMM>/assets/heatmap_sharpe.png` — Sharpe por
  `(lookback_regression × top_pct)` agregado por `max(risk_factor)`
- `.cache/grid_runs/<run_id>/trial_*/` — checkpoints per-trial (parquet
  + JSON, humano-inspecionáveis, resume-friendly)
- `.cache/grid_runs/<run_id>/trials.jsonl` — machine-readable por trial

**Execução 1 (2026-04-14):** gates falham marginalmente — PBO=0.524,
DSR 0/30, WF 4/30. Best config #15 (lookback=90, top=20%, risk=0.2%)
com Sharpe 0.58, CAGR 8.87%, DD 20%, WF 6/8. Clenow em yfinance SPX
2015-2023 não demonstra edge estatístico após correção para múltiplas
hipóteses. Fork de decisão aberto: paid-data ablation vs pivot vs
universe shift — ver `specs/backtest_phase2.md` §"Fase 2.5/3 —
Execução 1" para análise completa.

---

## Livros

**33 livros absorvidos** como Claude Skill (Fase 0 concluída). Importância por
livro (⭐⭐⭐ crítico, ⭐⭐ importante, ⭐ complementar) e qualidade de absorção
(🌟 perfeita, ✅ boa, ⚠️ borderline) estão no catálogo completo em
[`books/README.md`](books/README.md#catálogo-dos-livros-3333-absorvidos).

**Inventário canônico** (slug → título/autor/ano): [`books/MAPPING.md`](books/MAPPING.md).

Para re-absorver um livro ou adicionar novo:

```
# dentro do Claude Code
/absorb-book <slug>
```

Pipeline completo documentado em [`books/README.md#pipeline`](books/README.md#pipeline-como-reproduzir--re-absorver).

---

## Conceitos-chave de anti-overfit (CPCV / PBO / DSR)

Três testes do López de Prado (`advances_fin_ml`) que funcionam como **gates
obrigatórios** de qualquer backtest neste projeto. Aparecem nas inviolable
rules #3-5 de `knowledge/SKILL.md` e serão portados para
`src/ai_trade/backtest/validation/` nas Fases 2/3. Juntos, fecham o cerco
contra "estratégia com Sharpe alto que morre em live":

- **CPCV** → você tem uma *distribuição* honesta de performance, não um ponto.
- **PBO** → você sabe se o *processo de seleção* está viciado.
- **DSR** → você sabe se o Sharpe observado sobrevive ao teste de múltiplas hipóteses.

**Nenhum está em lib aberta mantida** (mlfinlab tinha, virou comercial).
Implementação será custom porém direta — referência cruzada em
`knowledge/validation/cpcv.md`, `knowledge/validation/deflated_sharpe.md` e
`knowledge/validation/permutation.md`.

### CPCV — Combinatorial Purged Cross-Validation

**O quê:** validação cruzada adaptada para séries temporais financeiras.

**Por que importa:** k-fold padrão **vaza informação** em séries temporais —
features de treino e teste se sobrepõem no tempo. Sharpe parece bom; em
produção colapsa.

**Três componentes:**
1. **Purged**: remove amostras de treino cujos rótulos se sobrepõem ao período de teste.
2. **Embargo**: insere um *buffer* após cada bloco de teste (serial correlation não respeita fronteiras de fold).
3. **Combinatorial**: em vez de K folds → K test sets, gera C(K, N) combinações. K=10 com N=2 = 45 caminhos. Você passa a ter uma **distribuição** de Sharpes, não um número isolado.

**Saída útil:** *"em 45 simulações, Sharpe foi 1.2 ± 0.4 — pior caso 0.3"*.
Muito mais honesto que *"Sharpe = 1.5 no backtest"*.

Ref: `advances_fin_ml.md`, ch.7 `[p.104-117]`.

### PBO — Probability of Backtest Overfitting

**O quê:** probabilidade de que o **processo de seleção da estratégia**
(escolher a que teve melhor in-sample) produza uma que perde out-of-sample.

**Como calcula:** embaralha várias partições IS/OOS. Para cada partição, pega
a estratégia com melhor Sharpe IS e vê se ela ficou acima ou abaixo da
mediana OOS. Se **frequentemente** fica abaixo da mediana → seu processo de
backtest está viciado.

**Gate prático (inviolable rule #3):** PBO > 0.5 ⇒ **descartar**. Sua
"estratégia vencedora" tem mais chance de ser overfit que válida.

**Intuição:** se você testa 100 combinações de parâmetros, alguma vai ter
Sharpe 2 **por puro azar**. PBO quantifica esse risco.

Ref: `advances_fin_ml.md`, ch.11 `[p.208-211]`. Implementação de referência:
`books/code/masters-testing-tuning/CSCV_MKT/CSCV.CPP` (C++ do Masters).

### DSR — Deflated Sharpe Ratio

**O quê:** Sharpe "desinflado" pelo número de estratégias testadas.

**Por que importa:** se você tentou **1 estratégia** e obteve Sharpe 2, é
impressionante. Se tentou **1000 estratégias** e a melhor teve Sharpe 2, é
esperado **por puro acaso** — a cauda da distribuição de Sharpes em N
tentativas concentra valores altos.

**Fórmula (alto nível):** deflaciona o Sharpe observado por:
- N (número de tentativas)
- skewness e kurtosis dos retornos
- tamanho da amostra
- variância cross-sectional dos Sharpes testados

Gera um p-value: *"dado que testei N estratégias, qual a probabilidade desse
SR ser > 0 de verdade?"*

**Gate prático (inviolable rule #4):** reporta DSR sempre que N > 1. Nunca
cite Sharpe cru num PR sem o DSR ao lado.

Ref: `advances_fin_ml.md`, ch.14 `[p.261-270]`.

---

## Universo Clenow e survivorship bias

Conceito complementar aos 3 acima — ataca a mesma doença (backtest mentiroso)
por outro ângulo: os **dados**, não os testes estatísticos.

### O que é o "universo Clenow"

A estratégia momentum de Andreas Clenow (`stocks_on_the_move`) opera sobre
**SPX 500**, reranqueando semanalmente. Mas "SPX 500" **depende da data
histórica sendo simulada** — não é a lista atual.

Entre 2005 e 2026, dezenas de empresas entraram no índice (NVDA em 2001, TSLA
em 2020) e saíram (Lehman Brothers, Enron pré-colapso, Washington Mutual,
General Motors 2009, Sears, etc.). Backtest que usa a lista **atual** do SPX
500 está testando numa realidade que nunca existiu.

### Survivorship bias

Erro sistemático de backtest causado por usar **apenas os sobreviventes
atuais** no lugar dos constituintes históricos.

Testar momentum 2000-2020 com a lista SPX atual é trapacear: você retirou
todas as empresas que quebraram, foram rebaixadas ou fundiram. O backtest
mostra Sharpe alto porque a amostra já está **filtrada pelos vencedores**.
Equivale a entrevistar bilionários sobre "as regras do sucesso" — o sampling
é viciado por construção.

Clenow é explícito sobre o tamanho do efeito `[stocks_on_the_move, p.238-239]`:

> *"Survivorship bias kills simulations. Using current S&P 500 constituents
> for a 10-year backtest creates fake outperformance because current members
> are selected BECAUSE they rose. You MUST use point-in-time membership and
> include delisted stocks."*

### Solução correta

**Point-in-time constituents + delisted stocks.** Fontes:
- **Norgate Data** (~US$85/mo) — fonte recomendada pelo próprio Clenow
- **EOD Historical Data** (~US$20/mo) — survivorship-free daily
- **Tiingo** (plano pago ~US$10/mo) — acessível
- **CRSP** — padrão-ouro acadêmico, mas licença cara
- **Wikipedia scrape** — brittle mas grátis; é onde vamos começar

### Como tratamos nesta fase

Fase inicial do backtest usa `yfinance` + Wikipedia scrape (grátis, bias
residual). **Cada relatório de backtest documenta explicitamente o caveat** —
resultados são otimistas até migrar para fonte paga. Quando a primeira
estratégia passar pelos gates CPCV/PBO/DSR, aí o investimento em dados
survivorship-free se justifica.

Ver [`ROADMAP.md`](ROADMAP.md) seção "Backtest em duas etapas" para como o
universo (e os dados) evoluem entre pesquisa e calibração Pepperstone.

---

## Referências

- **Roadmap / estado das fases:** [`ROADMAP.md`](ROADMAP.md)
- **Plano geral com justificativa por decisão:** [`TRADING_SYSTEM_PLAN.md`](TRADING_SYSTEM_PLAN.md)
- **Catálogo dos livros + pipeline de absorção:** [`books/README.md`](books/README.md)
- **Claude Skill gerada:** [`knowledge/SKILL.md`](knowledge/SKILL.md)
- **Plano ativo (Fase 0):** `/home/victor/.claude/plans/synthetic-snuggling-wren.md`
