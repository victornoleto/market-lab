# ROADMAP — MyFxBook Reverse-Engineering Study

> Objetivo: para cada um dos 52 systems do vendor HappyForex, decodificar o algoritmo,
> rodar backtest, comparar contra trades reais, e atribuir um score 0-1 de fidelidade
> de decodificação. Score, sanity, e edge econômico são dimensões **ortogonais**.
>
> **Capital remains 100% Plano C** durante e após estudo.
> **Sign-off explícito do usuário** entre fases.

---

## 🔄 Pivô 2026-05-02 (current)

Após 7 turnos de chat adversarial Opus↔GPT (`adversarial_chat/001..007`) + sessão de execução parcial:

**Mudança de escopo**: ao invés de filtrar para "top-10 DECODED" e testar só esses, **todos os 52 systems** entram no pipeline de decode-and-score. Score 0-1 + sanity + edge são dimensões separadas.

**Renomeação semântica**: o que era HIGH/MEDIUM/LOW (decodabilidade condicional ao timestamp real) já virou `DECODED/PARTIAL_DECODED/NOT_DECODED` no `OVERNIGHT_VALIDATION_REPORT`. **Esse score atual NÃO é o score de fidelidade** — é o score do proxy antigo. O novo score (Phase 5R abaixo) substitui.

**Próxima sessão**: ideal com **Opus** (modelo, não a janela de contexto). Razões em "Recomendação de modelo" abaixo.

---

## Princípios operacionais

1. **Gate-driven progression**: cada phase tem critério explícito de "go" ou "stop"
2. **Cheap kills first**: phases iniciais (catalog, sanity) são baratas e eliminam Folclore antes de gastar OHLC + replicator
3. **Citação obrigatória**: todo memo cita livro do knowledge base
4. **Idempotência**: scripts re-rodáveis sem stress (cache OHLC, parquets)
5. **Sem refactor amplo da app principal** — só `studies/` e refs read-only
6. **NEW**: três dimensões ortogonais — fidelidade de decodificação ≠ sanity ≠ edge econômico. Não misturar em um único score "tradeable".

---

## Status atual (2026-05-03)

**Atualizacao 2026-05-03**: R1 promoveu 30 rules para `frozen_rules/` v3 com
taxonomy strict 30/30. Por aprovacao condicionada do usuario, 5R-1 rodou apenas
como fase deterministica de `replicator/comparator/score` nesses 30 systems.
Outputs: `systems/<id>/decoding/*`, `_diagnostics/batch_summary.json`,
`_diagnostics/5R1_DETERMINISTIC_RUN.md`. Nenhum system atingiu
`fidelity_score >= 0.60` (2 LOW, 28 NONE), mas **nao ha ranking final nem decisao
de estrategia**: pause gates de R1 (`NEWS_RELEASE_MOMENTUM` n=1 e 13/30
`needs_m1_review`) seguem bloqueantes. Capital continua 100% Plano C; Plano A
DORMANT.

| Phase | Status | Output |
|---|---|---|
| 0 — infra | ✅ done 2026-05-01 | `shared/*` |
| 1 — catalog scrape | ✅ done 2026-05-01 | catalog parqueteado |
| 2 — per-system trade scrape | ✅ done 2026-05-01 | 52 systems × `data/trades/<id>/trades.parquet` |
| 3 — sanity + EDA | ✅ done overnight 2026-05-02 | per-system fingerprint + `_diagnostics/sanity_flags.json` |
| 4 — OHLC infra | ✅ done | `data/ohlc/<pair>/M5/<YYYY-MM>.parquet` cache |
| **5R — decode-and-score (NEW)** | 🟡 5R-1 deterministic run done for 30 R1 v3; ranking final blocked by pause gates | `systems/<id>/decoding/*` + `_diagnostics/batch_summary.json` |
| 6R — frozen-rule cross-system | ⏳ pending; escopo reduzido a par primário sobrevivente | `frozen_rule_test.md` |
| 7R — decisão Stage 3 | ⏳ pending | `jornada/` final + Stage 3 spec OR closure |
| 8 — Stage 3 proper (gates §2.4) | ⏳ condicional a 7R | `stage_3_<id>_*.md` |
| 9 — paper trading | ⏳ condicional a 8 | `PAPER_TRADING_VERDICT.md` |

Phases 0-4 preservadas em formato histórico abaixo.

---

## Phase 5R — Decode-and-Score (NEW, próxima sessão)

**Goal**: para cada um dos 52 systems, decodificar o algoritmo, rodar backtest contra OHLC Dukascopy, comparar synthetic vs real, e produzir score 0-1 de fidelidade de decodificação.

**Inputs read-only**:
- `frozen_rules/<id>.md` (12 já congeladas; precisa expandir para 52 — ver task 5R-0)
- `systems/<id>/decoder/candidates.json`
- `systems/<id>/decoder/fingerprint.md`
- `data/trades/<id>/trades.parquet`
- `data/ohlc/<pair>/M5/<YYYY-MM>.parquet`

**Outputs por system**:
- `systems/<id>/decoding/synthetic_trades.parquet` — backtest output
- `systems/<id>/decoding/comparison_report.md` — synthetic vs real
- `systems/<id>/decoding/decoding_score.json` — score breakdown 0-1

**Cross-system output**:
- `ranking/DECODING_FIDELITY_RANKING.md` — todos 52, sort por score, com sanity flag em coluna separada

### Tasks

**5R-0 — Pré-rodada Opus Stage 2 re-decode (recomendado, condicional a usuário ter Opus)**
- [ ] Re-rodar `/decode-system <id>` com **Opus** nos 52 systems (especialmente os 14 UNCATEGORIZED + os com sanity flag suspeito de família — e.g., `11171596` NY_SESSION_REVERSAL com p95=561h)
- [ ] Custo estimado: $15-25 total
- [ ] Output: 52 × `signal_rule.md` atualizados → re-copiar para `frozen_rules/`
- [ ] Justificativa: Sonnet errou várias famílias contra dados óbvios (família swing classificada como intraday). Opus aceita instruções de sanity-check família vs hold distribution.
- **Skip se**: usuário não tiver acesso Opus na sessão. Pipeline 5R-1+ funciona com regras Sonnet, só com fidelidade menor.

**5R-1 — Reescrever `replicator.py` (drop "lite")**
- [ ] Mover `shared/replicator_lite.py` → `shared/replicator.py` (rewrite, não remendar)
- [ ] Rule executor que suporta:
  - `tree` rules (parsear sklearn ASCII tree → executor)
  - `ripper` rulesets (parsear notação `[cond1^cond2] V [cond3]` → executor)
  - `univariate` (já implementado)
  - `multi-clause YAML` (parsear `direction:` literal do `signal_rule.md` em estilo Python)
- [ ] Backtest engine que simula entry + exit + PnL:
  - Entry: candidate (pair, t) onde rule fires
  - Exit: `max_holding_hours` do `frozen_rules/<id>.md`, ou EXIT rule se especificada
  - PnL: usando OHLC[pair][exit_t].close vs OHLC[pair][entry_t].open (sem custos — Stage 3 modela custos)
  - Output: `synthetic_trades.parquet` com schema compatível com `data/trades/<id>/trades.parquet`
- [ ] Citações obrigatórias (CLAUDE.md Regra 2):
  - `[advances_fin_ml, ch.5]` para feature importance
  - `[evidence_based_ta, p.367-380]` para session/hour FX
  - `[testing_tuning_pardo]` para walk-forward (downstream Stage 3)
- [ ] Manter pré-registro: spec `specs/replicator_lite_pre_reg.md` continua válido para a parte de "case-control entry detection"; criar `specs/replicator_full_addendum.md` com adições de exit + PnL + score formula

**5R-2 — Comparator synthetic vs real**
- [ ] Para cada (system, pair):
  - Match synthetic trades vs real trades por timestamp ±5min + symbol + direction
  - Compute hit-rate (synthetic that match real entry), precision (real that match synthetic), recall
  - Compute hold duration distribution similarity (KS test)
  - Compute PnL distribution similarity (Pearson correlation on matched + KS on unmatched)
  - Compute count ratio: `n_synthetic / n_real`
- [ ] Per-pair + agregado por system

**5R-3 — Score 0-1 de fidelidade de decodificação**

Fórmula proposta (`specs/decoding_score_formula.md` deve formalizar antes de codar):

```
fidelity_score = 0.30 × entry_timing_f1                  # combined precision/recall ±5min
              + 0.25 × direction_accuracy_at_matched     # Buy/Sell correto entre matched
              + 0.20 × hold_similarity                   # 1 - KS_stat das distribuições de hold
              + 0.15 × count_ratio_proximity             # 1 se ratio ∈ [0.5, 2.0], scaled fora
              + 0.10 × pnl_correlation                   # Pearson PnL synthetic vs real matched
clamp [0, 1]
```

Bandas (calibrar após primeira rodada):
- **0.80+** — algoritmo recuperado com alta fidelidade. Candidato natural para Stage 3 se sanity OK.
- **0.60-0.80** — decodificação parcial. Investigar com Opus re-review (se ainda não feito) ou aceitar como "approximate" e ir para Stage 3 com asterisco.
- **0.40-0.60** — fraca. Algoritmo provavelmente usa features fora do feature pack atual (DXY, news, intermarket). Não vale Stage 3.
- **<0.40** — não decodificado. Algoritmo não recuperável de OHLC público sozinho.

**5R-4 — Cross-system ranking + visualização**
- [ ] `ranking/DECODING_FIDELITY_RANKING.md`:
  - Sort por `fidelity_score` desc
  - Colunas: `system_id, name, family, fidelity_score, score_band, sanity_flag, n_trades, account, broker`
  - Disclaimer literal no topo: "score mede capacidade de reproduzir os trades reais via algoritmo recuperado de OHLC público; sanity é dimensão ortogonal; edge econômico requer Stage 3"
- [ ] Plot: scatter `fidelity_score × n_trades` colorido por sanity flag

**Exit criteria 5R**:
- 52 systems com `decoding_score.json`
- Ranking publicado
- ≥ 1 system com `fidelity_score ≥ 0.60` (mínimo para Phase 6R fazer sentido)

**Kill-switch 5R**: se 0 systems atingem `fidelity_score ≥ 0.60`, encerrar como "decodificação não foi possível com pipeline atual". Pular 6R/7R, ir direto para `jornada/` final.

---

## Phase 6R — Frozen-rule cross-system (atualizada após 5R-0 Opus re-decode)

**Goal**: validar OOS que regras congeladas em system OLD reproduzem trades em system NEW da mesma família.

**Estado dos pares pós-5R-0 (Wave 1+2+3 Opus, 2026-05-02)**:
- **Primário (decisivo) — SOBREVIVE**: `1407880` (OLD HMH v2.3.1, 3304 trades, blackout 2021) → `10224499` (HMH FM REAL, 221 trades, fresh). Ambos confirmados `LATE_NY_BREAKOUT` por Opus (1407880 conf 0.62, 10224499 conf 0.72). Wave 1 retirou `11206045` da família (re-classificado por Opus como Tokyo Open, não NY breakout) → família mais limpa.
- **Diagnóstico — EVAPOROU**: `2373850` (OLD Algorithm PRO, 1691) → `11171596` (Algorithm PRO FM, 1083). **Ambos UNCATEGORIZED** após Opus re-decode (eram família-divergent em v1; viraram duplo-UNCAT em v2). Vira **caso negativo sobre vendor library HappyForex**, não diagnóstico-de-coisa-nenhuma. Detalhe em `frozen_rules/CHANGELOG.md` v2 + jornada `2026-05-02-*-myfxbook-6R-pair-evaporated.md`.

**Implicação de escopo**: Phase 6R protocol roda **apenas no par primário sobrevivente**. Par diagnóstico fica como finding sobre o vendor (skewed momentum/breakout, sem reversal genuíno + fragilidade de classificação Sonnet em swing-as-intraday).

**Protocolo**: ajustar regra (entry + direction) **só** em OLD com purged k-fold; testar congelada em NEW (sem re-fit, sem peek).

**Thresholds par primário** (consenso 005/006):
| Banda | Critério |
|---|---|
| Strong pass | hit_rate ±5min ≥ 50% AND direction_accuracy ≥ 60% |
| Weak pass | hit_rate ±15min ≥ 50% AND direction_accuracy ≥ 58% |
| Borderline | 40% ≤ hit_rate ±15min < 50% OR 55% ≤ direction_accuracy < 58% |
| Fail | hit_rate ±15min < 40% OR direction_accuracy < 55% |

**Output**: `frozen_rule_test.md` com decomposição de falha (algoritmo mudou / regime mudou / sem replicabilidade) se Fail.

**Exit criteria 6R**: par primário em Strong/Weak Pass → 7R prossegue para Stage 3. Borderline → Stage 3 com asterisco. Fail → Stage 3 abortado.

---

## Phase 7R — Decisão Stage 3 + jornada final

**Matriz de decisão**:

| Phase 5R top scores | Phase 6R par primário | Ação |
|---|---|---|
| ≥1 system com score ≥0.80 AND sanity OK | Strong/Weak Pass | Spec separado `specs/stage_3_proper.md` para top 1-3 systems Pass. Phase 8 ativa. |
| ≥1 system score ≥0.80 AND sanity OK | Borderline | Stage 3 só para system(s) Phase 5R Pass, com asterisco metodológico. |
| ≥1 system score ≥0.80 AND sanity fail | qualquer | Memo "academic only — algoritmo decodificado mas system não tradeable". Sem Stage 3. |
| Nenhum score ≥0.60 | qualquer | Encerrar. `jornada/` final como "decodificação não recuperável de OHLC público". |
| Score moderado AND par primário Fail | — | Encerrar. Decodificação parcial sem confirmação OOS — não justifica Stage 3. |

**Output**: única `jornada/2026-05-XX-XXXX-myfxbook-reeng-decode-score-{result}.md` cobrindo Phases 5R-7R.

---

## Recomendação de modelo (Sonnet vs Opus)

**Sonnet (atual)** — funciona para:
- Implementação mecânica de Python (replicator, comparator, scorer)
- Iteração de código com testes

**Opus (recomendado)** — necessário para:
- **5R-0 re-decode Stage 2**: Sonnet errou ≥3 famílias contra dados óbvios (e.g., 11171596 classificado intraday mas com p95_hold=561h). Opus aceita "antes de classificar família, valide consistência da hipótese contra hold distribution e gap distribution".
- **Adversarial review da score formula**: a fórmula proposta pesa 5 dimensões. Opus questiona se 0.30×timing_f1 está bem calibrado, se a banda 0.80 está honesta, se algum termo é redundante. Sonnet aceita demais.
- **Code architecture review do replicator**: invariantes sutis (no look-ahead, candidate window not optimized post-hoc, frozen rule não re-minerada). Opus pega bugs aqui.

**Custo**:
- 5R-0 Opus re-decode 52 systems × ~$0.30-0.50/system = **$15-25**
- Sessão de código: dentro do plano Max, sem custo marginal por token

**Decisão recomendada**: rodar próxima sessão com Opus. Se orçamento apertado, pular 5R-0 (re-decode) e usar regras Sonnet existentes — fidelity score vai ser menor mas o pipeline funciona.

---

## Estimativa de tempo (próxima sessão)

| Task | Tempo Sonnet | Tempo Opus |
|---|---:|---:|
| 5R-0 Stage 2 re-decode 52 systems com Opus | N/A | 4-6h (depende de Opus throughput) |
| 5R-1 reescrever `replicator.py` | 4-5h | 3h |
| 5R-2 comparator synthetic vs real | 2h | 1.5h |
| 5R-3 score formula + spec | 1h | 0.5h |
| 5R-4 ranking + plot | 1h | 0.5h |
| 5R smoke test em 1 system + bug fix | 1-2h | 1h |
| 5R batch run 52 systems (compute) | 1-2h wallclock (paralelizável) | mesmo |
| 6R frozen-rule cross-system | 1h | 0.5h |
| 7R decisão + jornada final | 0.5h | 0.5h |
| **Total ativo** | **~12-15h** | **~10-13h** com Opus 5R-0 incluído |

Realista: 2 sessões. Sessão 1 = 5R-0 (se Opus) + 5R-1 + smoke test. Sessão 2 = 5R-2/3/4 + 6R + 7R.

---

## Kill-switches globais (atualizados)

- **K-1**: Phase 5R 0 systems com `fidelity_score ≥ 0.60` → encerra estudo como "não decodificável".
- **K-2**: Phase 6R par primário Fail → Stage 3 abortado mesmo se 5R Pass; documentar como "decodificação dentro do system, não OOS".
- **K-3**: Phase 7R 0 candidatos a Stage 3 → estudo encerra com publicação dos achados (algoritmos decodificados, mesmo sem edge testado).
- **K-4**: Stage 3 (Phase 8) hard-block FAIL em algum gate §2.4 (PBO, DSR, WF, OOS bootstrap, cross-lib) → Folclore + memo.

---

## Compliance com mandate market-lab

- Plano A está **DORMANT** (mandate §1, §7) desde 2026-04-23.
- Phases 5R-7R são **research-only**, sem capital allocation.
- Pass em 5R+6R **não autoriza** reativação de Plano A — apenas Stage 3 proper (Phase 8).
- Stage 3 herda gates §2.4 hard-block (PBO<0.5, DSR p<0.05, WF≥6/8, OOS bootstrap 99.9% CI > 0, cross-lib ±3pp).
- Sanity flag (DD<30%, p95_hold<168h, max_gap<30d) bloqueia paper trading mesmo se Stage 3 passar.

---

## Decisões pendentes do usuário

1. **Opus para 5R-0 re-decode**: confirmar se vai trocar conta para usar Opus. Se sim, rodar 5R-0 antes de 5R-1. Se não, pular 5R-0.
2. **Score formula final** (5R-3): pesos 0.30/0.25/0.20/0.15/0.10 são heurísticos; usuário pode ajustar antes de batch run.
3. **Bandas de fidelidade** (0.80/0.60/0.40): calibrar após ver distribuição empírica nos 52 systems.
4. **Stage 3 spec**: redigir só após 7R aprovar.

---

## Histórico — Phases 0-4 (done)

Preservadas para contexto. Não re-executar.

### Phase 0 — Infra (done 2026-05-01)
Scripts em `shared/` parametrizados por `system_id`. 109/109 smoke checks PASS contra prototype `1407880`.

### Phase 1 — Catalog scrape (done 2026-05-01)
60 systems scrapeados. Filtragem TIER aplicada → 52 systems entram no pipeline.

### Phase 2 — Per-system trade scrape (done 2026-05-01)
52 systems × `data/trades/<id>/trades.parquet`. Sample size 100-4000 trades.

### Phase 3 — Sanity + EDA (done overnight 2026-05-02)
Per-system `fingerprint.md` + `signal_rule.md` (Sonnet) + reliability proxy. Output em `OVERNIGHT_VALIDATION_REPORT.md`.

**Resultado**: 23 DECODED + 7 PARTIAL + 22 NOT_DECODED. Apenas 4/10 top DECODED passam sanity (DD<30, p95<168h, gap<30d). Reliability proxy revelado como "decodabilidade condicional" no chat adversarial — não confunde com fidelidade nem edge.

### Phase 4 — OHLC infra (done)
`data/ohlc/<pair>/M5/<YYYY-MM>.parquet` cache. 8623 parquets, ~10 GB. FX majors + XAU + BTC.

### Phases 5-7 (originais, superseded)
Phases 5-7 originais (direction extraction + gates §2.4 + ranking) **substituídos** por 5R-7R com nova estrutura ortogonal (fidelidade ≠ sanity ≠ edge). Razão: chat adversarial 2026-05-02 mostrou que misturar dimensões em score único leva a marketing teatral ("HIGH" não significa tradeable).

---

## Atualizações ROADMAP

Conforme phases avançam:
- Marcar checkboxes nesta página
- Adicionar `jornada/YYYY-MM-DD-HHmm-slug.md` por phase completada (CLAUDE.md Regra 1)
- Update `ranking/DECODING_FIDELITY_RANKING.md` ao final de cada batch run
