# Plano de execução do 5R-1-hardening — companion ao `hardening.md`

**Status**: AGUARDANDO INÍCIO DE WAVE A — sessão atual encerra após escrever este doc; nova sessão executa Wave A.
**Origem**: parecer adversarial cruzado (Opus 4.7 + GPT-5.5) consolidado em `5R-1-hardening.md`.
**Decisões D1–D4 do usuário**: resolvidas em 2026-05-02 (transcritas na §4 abaixo).

---

## 1. Cabeçalho

Este documento operacionaliza o checklist de `5R-1-hardening.md`. Ele:

- Valida o diagnóstico contra o estado real do repositório (§2).
- Registra findings revisados encontrados durante a validação (§3).
- Documenta as decisões D1–D4 do usuário, que resolvem ambiguidades do checklist original (§4).
- Estrutura o trabalho em 4 waves com esforço estimado, paralelismo via subagentes e dependências (§5).
- Lista citações obrigatórias (Regra 2 CLAUDE.md) que ancoram cada decisão técnica (§6).

`hardening.md` permanece o documento normativo (5 bloqueantes + 2 secundários + ponto narrativo). Este plano é a tradução em sequência executável.

---

## 2. Validação contra repo (snapshot 2026-05-02 pós-Wave 1+2+3 do 5R-0)

| # | Item | Diagnóstico diz | Repo confirma | Notas |
|---|---|---|---|---|
| 1 | CHANGELOG sem hashes/diffs | ✅ | **CONFIRMADO** | Zero linhas com SHA/hash/diff em `frozen_rules/CHANGELOG.md`. Só tabela textual de mudanças. |
| 2 | Monolito 1286 linhas, sem testes | ✅ | **CONFIRMADO + pior** | 1295 linhas (não 1286). Inexiste `tests/` no estudo. Smoke = manual via `python -c`. |
| 3 | Sem enum fechado de `family` | ✅ | **CONFIRMADO** | Zero `Literal[...]` / `Enum` em `shared/decoder_*.py`. Taxonomia só vive em prompt markdown do agent decoder. |
| 4 | Comparator só ±5min match | ⚠ | **PARCIAL** | Já tem `always_buy`, `hour_majority`, `pair_hour_majority`. **Falta**: `always_sell`, `random frequency-matched`, `permutação temporal`. |
| 5 | 6541963 com label ad-hoc | ✅ | **CONFIRMADO** | `family: H1_MOMENTUM_GOLD` no frozen_rule v2. Backup v1 era `FACTOR_SCALPING`. |

---

## 3. Findings revisados (descobertos durante validação, atualizam o `hardening.md`)

- **Smoke pós-vetorização em 10224499 = 7.8s** (não 38min). O 38min do parecer adversarial se referia ao run anterior (per-anchor `compute_entry_features`). Após reescrita do feature extractor com pré-load M5 + resample vetorial + `merge_asof` por timeframe, smoke single-system completo (rule load → window 119k bars → features → backtest com debouncing → comparator → score) roda em ~8s. O ponto secundário §6 do `hardening.md` (`--limit`/timeout/métricas) continua válido para batch 52, mas a urgência cai.
- **Comparator já tem 3 baselines** (`always_buy`, `hour_majority`, `pair_hour_majority`); **falta**: `always_sell`, `random frequency-matched`, `permutação temporal`. O bloqueante §3 do `hardening.md` deve cobrir só o delta, não rebuild from scratch.
- **`replicator.py` = 1295 linhas; estudo sem diretório `tests/`**. Bloqueante §2 do `hardening.md` exige tanto fatiamento quanto cobertura unitária — duas ações distintas.
- **`ROADMAP.md` ainda lista par diagnóstico ativo** (`2373850→11171596`). Narrativa dessincronizada com o estado de evaporação OOS. Wave A item 1 corrige (na próxima sessão, com jornada-entry junta).
- **Cabeçalho do `frozen_rules/CHANGELOG.md`** menciona "operação autorizada" mas não registra `chmod u+w` / timestamp / motivo da quebra do read-only. Wave A item 4 corrige.

---

## 4. Decisões D1–D4 do usuário (transcrição íntegra, 2026-05-02)

> **D1 — H1_MOMENTUM_GOLD: ACEITAR como família nova** (override do critério §1 do `hardening.md`, que exigia ≥2 systems + citação).
> Justificativa do usuário: a família tem coerência mecânica suficiente (Gold + H1 + momentum) e vale registrar como tentativa explícita; se não aparecer 2º system em rodadas futuras, re-avalia. Consequências:
> - `6541963` mantém `family="H1_MOMENTUM_GOLD"` no frozen_rule v2 (não remapear).
> - Wave B item 2 (enum em `shared/decoder_taxonomy.py`) inclui `H1_MOMENTUM_GOLD` na lista oficial.
> - Atualizar §1 do `hardening.md`: critério de nova família vira "≥1 system + citação OU aprovação explícita do usuário com justificativa registrada". ✅ aplicado neste turno.
> - Adicionar nota neste plano flagando que `H1_MOMENTUM_GOLD` é "família provisória, n=1, revisar em ronda futura". ✅ aplicado neste turno.

> **D2 — APROVADO.** Enum mantém 9 famílias originais + `H1_MOMENTUM_GOLD` = 10. Famílias vazias pós-Opus (`NY_SESSION_REVERSAL`, `FACTOR_SCALPING`) ficam na enum como finding sobre vendor library.

> **D3 — APROVADO com ajuste:** pool de sampling = 5 random dos **15 systems não-rechecados** (7 PARTIAL + 8 DECODED), seed fixa para reprodutibilidade. NOT_DECODED excluído (lá Opus seria first-decode, não re-decode — teste diferente).

> **D4 — APROVADO.** 5 subagents Opus paralelos, custo $2-3.

### Consequências consolidadas para o plano

- Wave B item 3 (remap `H1_MOMENTUM_GOLD`) **REMOVIDO** do plano — D1 mudou. Agora vira "incluir `H1_MOMENTUM_GOLD` no enum" dentro do Wave B item 2.
- Wave A item 8 (Stage 1 sample test) usa pool de 15 systems (7 PARTIAL + 8 DECODED não-rechecados), seed fixa.
- Wave B item 2 produz enum com 10 entries, incluindo as duas vazias (`NY_SESSION_REVERSAL`, `FACTOR_SCALPING`) e `H1_MOMENTUM_GOLD` provisório.

---

## 4.5. Decisões D5-D7 + Wave A.5 (2026-05-02 pós-alarme do Stage 1 sample test)

Stage 1 sample test (Wave A item 8) disparou reclass 3/5 = 60% > threshold 30%. Apenas
fechar enum (Wave B) sozinho era insuficiente. Usuário consolidou decisões D5-D7
2026-05-02 + ordem de execução com Wave A.5 inserida entre Wave A e Wave B-original.

### D5 — `NEWS_RELEASE_MOMENTUM`: APROVADO COMO PROVISÓRIO

Evidência: n=1 (`1612420`, "Happy News" v1.4.1, 788 trades). 45% trades em bucket 15:30 UTC + ret_3_H4 momentum-following + p50=0.01h confirmado pós-R4.
Critério provisório: clock-anchored ≥1 bucket horário com >30% trades + name-flag NEWS/HF News + sign momentum-following.
Citação: Aronson `[evidence_based_ta, p.247-260]` event windows + small-sample bias.
Revisão: se R1 não trouxer 2º system, downgrade para `UNCAT + reason_code="taxonomy_gap"`.

### D6 — `SWING_TREND_MOMENTUM`: APROVADO COMO PROVISÓRIO

Nomenclatura: `SWING_TREND_MOMENTUM` em vez de `SWING_H4_TREND` (H4 é feature/timeframe, não essência da família).
Evidência: n=1 (`8577442`, Happy Way FM, 934 trades). p50=213.99h ~9d (confirmado pós-R4), top hour só 11.9%, sem clock anchor, H4 EMA-distance domina tree.
Critério provisório: mediana hold >72h + top hour <15% + H4/D1 trend/momentum features dominam tree.
Citação: Pardo `[testing_tuning, ch. swing-trade systems]` + Clenow `[stocks_on_the_move]` swing/trend momentum.
Revisão: idem D5.

### D7 — `H1_MOMENTUM_GOLD`: MANTER COMO PROVISÓRIO

Já registrado em §1 do `hardening.md`. Entra no enum v2 com `provisional=True` (não oficial pleno). Critério/review_gate explícitos. Frozen rule v2 mantém `family="H1_MOMENTUM_GOLD"` (sem remap).

### Regra UNCAT reason_code obrigatório (decisão usuário 2026-05-02)

`UNCATEGORIZED` é classe legítima quando evidência é insuficiente, mas não é bucket-de-fuga.
Toda atribuição UNCAT exige `reason_code ∈ {underpowered, degenerate, hold_mismatch, mixed_strategy, taxonomy_gap, insufficient_evidence}`.
Detalhes em `hardening.md` §1.
Ranking não penaliza UNCAT automaticamente; score 5R-3 manda.

### R4 — Stage 1 hold-extraction fix (✅ done 2026-05-02)

Causa raiz: parsing posicional de `duration` em `shared/parser.py:128` quebrava em layouts não-FX
(crypto/CFD sem coluna `pips` → `text(10)` lia `pct` como duration → all-NaN).

Impacto pré: 31 systems fully-NaN, 2 mixed. Pós: **0/52**.

Fix: `duration_sec` autoritativa via `(closetime_ms - opentime_ms)/1000`. `duration_sec_text`
preservada para audit/compat. 52 parquets backed up em `data/trades/_pre_R4_2026-05-02/` com
SHA-256 manifest pré+pós.

Fingerprints: **patch cirúrgico** (re-render só da linha `hold p50/p95/max`),
**NÃO re-execução integral do Stage 1**. Features OHLC-based em `candidates.json` e
`signal_rule.md` preservadas (independem de duration). Re-execução completa fica como
opção futura se algum consumidor downstream depender de outros campos derivados de duration_sec.

Validação empírica do alarme do sample test: ground truth pós-R4 confirma reclass do Opus em 4/4 casos checados (8577442 swing 9d, 1612420 news 36s, 10192401 BTC scalp, 10475089 Tokyo swing 2.8d).

Artifacts: `_diagnostics/R4_summary.md`, `R4_migration_manifest.json`, `R4_fingerprint_patch_log.md`.

### R1 — Re-decode integral (próxima execução agendada após Wave B item 2)

Pool: 30 systems não-rechecados pelo 5R-0 (23 DECODED + 7 PARTIAL). NOT_DECODED excluído.
Custo aceito: $15-25 (não fazer parcial — deixaria 7 PARTIAL suspeitos e geraria retrabalho).
Estrutura: 6 waves × 5 subagents Opus paralelos.
Prompt usa enum v2 oficial; nenhum label fora da enum aceito como `family`. Labels emergentes
vão para `candidate_new_family: str | None`. Para UNCAT, exige `reason_code` (regra acima).
Output: `frozen_rules/<id>.md` v3 com backup `_pre_R1_2026-05-02/`. Nova entrada CHANGELOG seguindo padrão SHA + diff do Item 4.
Reportar: tabela final reclass, taxa por família, taxa UNCAT por reason_code, suporte das 3 famílias provisórias.

### Pause gates pós-R1 (antes de Wave C/D)

Definidos pelo usuário:
- Se R1 revelar nova família com n≥2 → escalar antes de aceitar no enum.
- Se taxa de reclass >50% → pausar imediato e escalar.
- Se família provisória permanecer n=1 → manter `provisional=True` e decidir depois (fica, generaliza ou vira UNCAT/taxonomy_gap).

Wave C/D continuam blocked até revisão humana pós-R1.

---

## 5. Plano em 5 waves (revisado pós-D5-D7 + R4)

### Wave A — paralelo, sem dependências (~1.5h wallclock) ✅ DONE 2026-05-02

| Item | Esforço ativo | Subagente | Dependências | Status |
|---|---|---|---|---|
| **1** Narrativa: `ROADMAP.md` + `jornada/` entry | 30min | direto | nenhuma | ✅ done — `jornada/2026-05-02-1630-myfxbook-reeng-6R-pair-evaporated.md` |
| **4** CHANGELOG SHA + diff links + chmod log | 30min | direto | nenhuma | ✅ done — `frozen_rules/CHANGELOG.md` seção "Auditoria criptográfica" |
| **8** Stage 1 sample test (5 random) | 30min wallclock + ~$2-3 | 5 subagents Opus paralelos | nenhuma | ✅ done — **alarme disparado 60% reclass**. `_diagnostics/stage1_sample_test/SUMMARY.md` |
| **9** `--limit`/timeout/token-log | 30min | direto | nenhuma | ✅ done — `scripts/run_replicator_batch.py` + `shared/run_overnight_validation.py` |

### Wave A.5 — pós-alarme (intercalada após decisões D5-D7 do usuário 2026-05-02)

| Item | Esforço | Status | Detalhes |
|---|---|---|---|
| **R4** Stage 1 hold-extraction NaN fix | ~30min | ✅ done | Root cause = parsing posicional `duration` quebra em layouts não-FX. Fix: `duration_sec` autoritativa via timestamps. 31 fully-NaN + 2 mixed → 0/52 NaN. **Patch cirúrgico em fingerprints, NÃO re-execução integral do Stage 1**. Detalhes em `_diagnostics/R4_summary.md`. |
| **R1** Re-decode integral 30 systems com Opus | ~3-4h wallclock + ~$15-25 | pendente após Wave B item 2 | 6 waves × 5 subagents Opus paralelos. Pool: 23 DECODED + 7 PARTIAL não-rechecados. Usa enum v2 + UNCAT reason_code obrigatório. Output: `frozen_rules/` v3 + backup `_pre_R1_2026-05-02/` + entry CHANGELOG. **Pause gates** (escalar): n≥2 nova família, reclass >50%, provisória permanece n=1. |

### Wave B — sequencial após Wave A.5 R4 (~1.5h, expandido por D5-D7)

| Item | Esforço | Detalhes |
|---|---|---|
| **2** Enum fechado + provisórias + UNCAT reason_code em `shared/decoder_taxonomy.py` | 1.5h | `Literal[...]` com **9 originais + 3 provisórias** (`H1_MOMENTUM_GOLD`, `NEWS_RELEASE_MOMENTUM`, `SWING_TREND_MOMENTUM`, todas com `provisional=True` + `criteria` + `review_gate` em docstring referenciando `hardening.md` §1). Schema `Family` com campos `name: Literal[...]`, `provisional: bool`, `n_supporting_systems: int`, `criteria: str`. UNCAT exige `reason_code: Literal[...]` obrigatório. `candidate_new_family: str \| None` mantido para emergentes. Validar `frozen_rules/<id>.md` contra enum (script de check). Atualizar prompt do agent decoder (`.claude/agents/decoder.md`) com mesma lista + reason_code rule. Famílias vazias `NY_SESSION_REVERSAL` e `FACTOR_SCALPING` permanecem na enum como finding sobre vendor library. |
| ~~**3** Remap H1_MOMENTUM_GOLD~~ | — | **REMOVIDO por D1**. Mesclado em item 2. |

### Wave C — sequencial após B (~3-4h)

| Item | Esforço | Detalhes |
|---|---|---|
| **5** Fatiar `replicator.py` em 5 módulos | 2-3h | `parser.py` (frozen rule loading + cascade), `executor.py` (rule executors univariate/tree/ripper/yaml), `backtest.py` (entry/exit/PnL), `comparator.py` (match + métricas), `score.py` (formula 6 termos). API pública estável. `replicator.py` vira fachada fina re-exportando. |
| **7** Baselines no comparator (delta) | 1h | Adicionar `always_sell`, `random_frequency_matched` (mesma freq de fires/dia), `permutation_test` (embaralhar timestamps). Reportar lift vs cada baseline separado. NÃO refazer os 3 que já existem. |

### Wave D — após C (~2.5h)

| Item | Esforço | Detalhes |
|---|---|---|
| **6** Testes unitários por componente (pytest fixtures) | 2h | Fixtures pequenas (50 bars, 5 trades) por módulo. Cobrir parsers (univariate/tree/ripper/yaml), executor edge-cases (NaN features, missing column), backtest debouncing, comparator NaN handling, score formula NaN→0 + clip. |
| **10** `hold_unknown=True` → ranking secundário | 30min | Marcador no `decoding_score.json`. Ranking principal exclui `hold_unknown`; ranking secundário "incomplete extraction" lista esses systems separadamente. |

### Resumo de esforço e wallclock (revisado pós-D5-D7 + R4)

| Wave | Itens | Esforço ativo | Wallclock estimado | Status |
|---|---|---:|---:|---|
| A | 1, 4, 8, 9 | ~2h | ~1.5h | ✅ done 2026-05-02 |
| A.5 | R4 + R1 | R4 ~30min, R1 ~3-4h + ~$15-25 | R4 ~30min, R1 ~3-4h | R4 ✅ done; R1 pendente após Wave B item 2 |
| B | 2 (expandido com 3 provisórias + UNCAT reason_code) | ~1.5h | ~1.5h | bloqueia C; pré-requisito de R1 |
| C | 5, 7 | ~3-4h | ~3-4h | bloqueada até Wave B + R1 fecharem |
| D | 6, 10 | ~2.5h | ~2h | bloqueada até Wave C |
| **Total** | — | **~13-15h ativo + tokens R1** | **~10-12h em waves disciplinadas** | — |

Só após Wave D inteira **+ R1 sem trigger de pause gate**: liberar 5R-2/5R-3
(que já estão bloqueados no checklist mestre).

**Pause gates pós-R1** (definidos em §4.5): se R1 disparar, escalar antes de Wave C.

---

## 6. Citações (Regra 2 CLAUDE.md)

Cada decisão técnica deste plano cita um livro do knowledge base. Quando aplicado em código, a citação migra para docstring/comentário do PR.

- **Baselines no comparator (Wave C item 7)**: López de Prado [advances_fin_ml, p.196-211] (DSR/PBO + bootstrap) e Aronson [evidence_based_ta, p.247-260] (data-mining bias / surrogate data testing) ancoram a exigência de baselines `random frequency-matched` + `permutação temporal`.
- **Taxonomia fechada (Wave B item 2)**: López de Prado [advances_fin_ml, ch.3] (label consistency) e [ml_for_algo_trading] (supervised classification needs closed label space) justificam o enum.
- **`NEWS_RELEASE_MOMENTUM` provisional (D5)**: Aronson [evidence_based_ta, p.247-260] event windows + small-sample bias.
- **`SWING_TREND_MOMENTUM` provisional (D6)**: Pardo [testing_tuning, ch. swing-trade systems] + Clenow [stocks_on_the_move] swing/trend momentum cross-section.
- **`H1_MOMENTUM_GOLD` provisional (D7)**: Carver [systematic_trading] + Aronson [evidence_based_ta] cross-section momentum em commodity FX.
- **CHANGELOG auditável (Wave A item 4)**: Pardo [testing_tuning] (reproducibility como pré-requisito de inferência válida).
- **Testes unitários por componente (Wave D item 6)**: López de Prado [advances_fin_ml, ch.13] (research code as production code; falsifiability via tests).
- **Stage 1 sample test (Wave A item 8)**: Aronson [evidence_based_ta, p.281, p.291] (small-sample bias e necessidade de cross-validation aleatória contra confirmação seletiva).
- **R4 hold-extraction fix (Wave A.5)**: Pardo [testing_tuning] (reproducibilidade — não-NaN é pré-requisito de qualquer inferência sobre family vs hold) + Aronson [evidence_based_ta, p.281] (small-sample bias com NaN como input zera evidência sobre hold).
- **R1 re-decode integral (Wave A.5)**: Aronson [evidence_based_ta, p.281, p.291] (random sampling contra confirmação seletiva) + López de Prado [advances_fin_ml, ch.7] (purged k-fold OOS independente).
- **`hold_unknown` segregado (Wave D item 10)**: Pardo [testing_tuning] (incomplete data quarantine — não misturar com sample limpa).

---

## 7. Status

**WAVE A ✅ DONE + WAVE A.5 R4 ✅ DONE (2026-05-02). Próximo: Wave B item 2 (enum + provisórias + UNCAT reason_code), depois R1.**

Sessão atual:
1. ✅ Wave A 4 itens completos (narrativa, CHANGELOG, sample test, runners hardened).
2. ✅ Wave A.5 R4 (Stage 1 hold-extraction NaN fix; 31+2 → 0/52, par 6R intacto, patch cirúrgico não-Stage1-rerun).
3. ✅ Step 2 docs update (este arquivo + `hardening.md` §1 reescrita com D5/D6/D7 + UNCAT reason_code + R4 detail).
4. → **Próximo**: Wave B item 2 — `shared/decoder_taxonomy.py` com enum 9+3 provisórias + UNCAT reason_code obrigatório + refatorar `decoder_*.py` + atualizar prompt do agent decoder.
5. → Em seguida: R1 — re-decode integral 30 systems com Opus em 6 waves × 5 paralelos.
6. → Pause gates pós-R1 antes de Wave C/D.

Nada em `shared/replicator.py` (Wave C item 5), comparator delta (Wave C item 7), tests (Wave D item 6), ou batch 5R-2/5R-3 até Wave D fechar **+ R1 sem trigger de pause gate**.

Audit trail: este arquivo + `hardening.md` + `R4_summary.md` + `stage1_sample_test/SUMMARY.md` formam o contrato auditável das decisões 5R-1-hardening 2026-05-02.
