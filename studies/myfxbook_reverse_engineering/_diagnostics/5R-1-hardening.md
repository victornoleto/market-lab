# 5R-1 Hardening — STOP antes de 5R-2/5R-3

**Status**: BLOCKER. Não rodar 5R-2 nem 5R-3 antes de fechar este checklist.
**Origem**: parecer adversarial cruzado (Opus 4.7 + GPT-5.5), 2026-05-02.
**Motivo**: o estado atual produziria ranking com aparência científica e baixo valor probatório.

---

## Contexto (o que aconteceu até agora)

- Phase 5R-0 rodou Opus 4.7 re-decode em 15 systems (3 waves × 5 agents).
- 73% dos labels Sonnet (Stage 2 v1) foram reclassificados pelo Opus.
- `frozen_rules/` foi descongelado (chmod u+w) e versionado para v2.
- Família `FACTOR_SCALPING` colapsou 6→0; `NY_SESSION_REVERSAL` colapsou 2→0.
- Opus inventou label ad-hoc `H1_MOMENTUM_GOLD` fora de qualquer enum.
- Par 6R diagnóstico (`2373850` ↔ `11171596`) virou duplamente `UNCATEGORIZED`.
- `shared/replicator.py` cresceu para ~1286 linhas sem cobertura de teste por componente.
- Smoke test reportou 38min / ~160k tokens; falta `--limit`/timeout/métricas.

## Diagnóstico consolidado

A rodada Opus expôs três fragilidades simultâneas:
1. **Stage 2 (Sonnet)** era instável — 73% reclass não é "vitória do Opus", é "etapa anterior frágil".
2. **Stage 1 (fingerprint)** também é suspeito — colapso `FACTOR_SCALPING` 6→0 sugere viés de feature (alta-freq Gold/BTC ≠ scalping).
3. **Pipeline operacional** (replicator + comparator + frozen_rules) não tem auditoria nem baselines suficientes para sustentar um ranking.

Avançar para 5R-2/5R-3 amplifica os três problemas.

---

## Bloqueantes — fechar TODOS antes de 5R-2

### 1. Taxonomia fechada (família = enum)

- `family` deve ser `Literal[...]` fechado em `shared/decoder_taxonomy.py` (single source of truth) + consumido por `shared/decoder_*.py` e pelo agent prompt do decoder.
- Labels emergentes fora da enum vão para campo separado `candidate_new_family: str | None`, **nunca** substituem o enum oficial. Obrigatório para qualquer label não-enum.
- **`UNCATEGORIZED` é classe legítima**, não bucket-de-fuga (decisão usuário 2026-05-02): toda atribuição UNCAT deve carregar `reason_code` obrigatório, valores aceitos:
  - `underpowered` — n<100 ou cobertura insuficiente para qualquer rule miner;
  - `degenerate` — tree/ripper colapsa para always-Buy/always-Sell baseline;
  - `hold_mismatch` — sanity de família intraday violado por hold distribution real;
  - `mixed_strategy` — múltiplos picos de timing / ≥2 sub-estratégias coexistentes;
  - `taxonomy_gap` — estratégia coerente mas fora das famílias do enum atual (candidata a expansão futura);
  - `insufficient_evidence` — fingerprint+candidates não permitem decisão confiável.
  Ranking não penaliza UNCAT automaticamente; score empírico (5R-3) manda.
- Critério para aceitar nova família:
  **≥1 system + citação em `books/summaries/`** + **aprovação explícita do usuário com justificativa registrada** (decisão 2026-05-02 — relaxa o ≥2 systems original; nova família entra com `provisional=True` e revisada após R1 para confirmar suporte n≥2).

#### Entradas registradas (novas famílias provisórias)

Todas as 3 entries abaixo são **provisórias** (n=1 cada, marcadas `provisional=True` em
`shared/decoder_taxonomy.py`). Revisão obrigatória após R1 (re-decode integral dos 30 não-rechecados):
se nenhum 2º system independente recair na mesma assinatura, reavaliar downgrade para
`UNCATEGORIZED + reason_code="taxonomy_gap" + candidate_new_family="<NAME>"` ou generalização.

- **2026-05-02 — `H1_MOMENTUM_GOLD`** (D7 do usuário). n=1 (system `6541963`, Happy Gold - Tickmill M15, 2213 trades).
  Justificativa: "coerência mecânica suficiente (Gold + H1 + momentum); vale registrar como tentativa explícita".
  Critério de revisão: presença de Gold/XAU + entry-on-H1-momentum + tree balanced + dir_acc>0.7. Frozen rule v2 mantém `family="H1_MOMENTUM_GOLD"` (sem remap).
  Citação: `[carver_systematic_trading]` momentum cross-section + `[machine_trading]` cap.

- **2026-05-02 — `NEWS_RELEASE_MOMENTUM`** (D5 do usuário). n=1 (system `1612420`, OLD Happy News v1.4.1, 788 trades).
  Evidência: name="Happy News" + 45% trades em bucket 15:30 UTC + ret_3_H4 momentum-following + p50=0.01h (~36s) entradas/saídas instantâneas em janela news (confirmado pós-R4).
  Critério provisório: clock-anchored ≥1 bucket horário com >30% trades + name-flag NEWS/HF News + sign momentum-following.
  Revisão: se nenhum 2º system recair nessa assinatura após R1, reavaliar downgrade `UNCAT + reason_code="taxonomy_gap"`.
  Citação: Aronson `[evidence_based_ta, p.247-260]` event windows + small-sample bias.

- **2026-05-02 — `SWING_TREND_MOMENTUM`** (D6 do usuário). n=1 (system `8577442`, Happy Way FM - REAL, 934 trades).
  Nota nomenclatura: usar `SWING_TREND_MOMENTUM` em vez de `SWING_H4_TREND` — H4 é feature/timeframe, não essência da família.
  Evidência: p50=213.99h (~9d, confirmado pós-R4), top hour só 11.9%, sem clock anchor, H4 EMA-distance domina tree.
  Critério provisório: mediana hold >72h + top hour <15% + H4/D1 trend/momentum features dominam tree.
  Revisão: idem (downgrade se R1 não trouxer 2º system).
  Citação: Pardo `[testing_tuning, ch. swing-trade systems]` + Clenow `[stocks_on_the_move]` swing/trend momentum.

#### R4 — Stage 1 hold-extraction NaN fix (2026-05-02)

Pré-requisito empírico para Wave B + R1, executado entre Wave A e Wave B (Wave A.5 no plan §4.5).

- **Root cause**: `shared/parser.py:128` extraía `duration` por posição (`text(10)`) na tabela HTML do MyFxBook. Layouts não-FX (crypto/CFD) omitem a coluna `pips`, deslocando "duration" para a posição que normalmente carrega `pct`. Resultado: parser lia `"0.02%"` como duração → `_parse_duration` retornava `None` → `duration_sec` all-NaN → fingerprint reportava `hold p50/p95/max = nan/nan/nan`.
- **Impacto pré-fix**: 31 systems fully-NaN + 2 mixed; pós-fix: 0/52 NaN.
- **Evidência empírica do alarme do sample test**: `8577442` classificado pelo Sonnet como OVERLAP_NY_LONDON_RANGE (intraday) tinha hold real ~9 dias (p50=213.99h pós-R4) — bug NaN impedia qualquer sanity-check de família vs hold. Reclass do Opus na sample test foi confirmada por ground truth.
- **Par 6R sobrevivente**: intacto (`1407880` p50=0.98h, `10224499` p50=1.74h, ambos LATE_NY_BREAKOUT intraday).
- **Fix**: `duration_sec` autoritativa via `(closetime_ms - opentime_ms)/1000` (sempre presentes nos atributos do `td.symbol`, layout-independente). `duration_sec_text` mantida para audit.
- **Caveat de rastreabilidade**: fingerprints foram **patch cirúrgico** (re-render só da linha `hold p50/p95/max`), **não re-execução integral do Stage 1**. Features OHLC-based em `candidates.json` e `signal_rule.md` foram preservadas (independentes de duration). Re-execução completa do Stage 1 fica como opção futura se algum consumidor downstream depender de outros campos derivados de `duration_sec`.
- **Artifacts**:
  - `_diagnostics/R4_summary.md` — sumário executivo
  - `_diagnostics/R4_migration_manifest.json` — SHA-256 pré+pós manifest dos 52 parquets
  - `_diagnostics/R4_fingerprint_patch_log.md` — log surgical patch fingerprint per system
  - `data/trades/_pre_R4_2026-05-02/<sid>.parquet` × 52 — backup completo

### 2. `replicator.py` testado por componente

Quebrar o monolito de 1286 linhas em módulos com cobertura unitária:

- `parser` — interpreta `signal_rule.md` → AST/dict de regras.
- `executor` — aplica regra em OHLC e gera sinais.
- `backtest` — converte sinais em trades sintéticos com custos.
- `comparator` — alinha trades sintéticos vs MyFxBook reais.
- `score` — agrega métricas em ranking final.

Cada componente precisa de teste com fixture pequena antes de integrar. Sem isso, qualquer bug silencioso contamina o ranking inteiro.

### 3. Comparator com baselines

`match ±5min + symbol + direction` mede coincidência de calendário, não edge. Adicionar baselines obrigatórios:

- **Random rule** com mesma frequência média de sinais.
- **Always-Buy** e **Always-Sell** no mesmo símbolo.
- **Permutação temporal** (embaralhar timestamps de sinais).
- **Frequency-matched random** controlando por hora/símbolo.

Score reportado deve ser **lift sobre baseline**, não match rate absoluto. Sem isso, ranking não é interpretável.

### 4. Auditoria do `frozen_rules/`

`frozen_rules/CHANGELOG.md` precisa de:

- SHA-256 (ou similar) de cada arquivo pré e pós-mudança.
- Diff textual rastreável (ou link para `_backups/.../<id>.md`).
- Operação que descongelou (chmod) registrada com timestamp e justificativa.
- Reversão deve ser determinística a partir do backup.

Sem isso, o "read-only contract" virou "read-only-on-trust" e a Etapa 0 (consenso adversarial 005-007) perde força contratual.

### 5. Reconhecer Stage 1 como suspeito

- Adicionar nota em `ROADMAP.md` e `_diagnostics/`: fingerprint Stage 1 não passou auditoria adversarial.
- Antes de qualquer ranking final, rodar Opus em **amostra cega** (ex: 5 systems aleatórios fora dos 15 já rechecados) e medir taxa de reclass. Se >30%, Stage 1 também precisa de revisão antes de ranking público.

---

## Pontos secundários (não-bloqueantes, mas resolver na mesma fase)

### 6. Smoke test custoso

- Adicionar flag `--limit N` em `run_overnight_validation.py` / replicator.
- Timeout duro por system.
- Logar tokens/tempo por etapa para identificar gargalo.

Não bloqueia 5R-2, mas precisa entrar antes de batch grande.

### 7. `max_holding_hours` default

- Systems com `p95_hold=NaN` viram `hold_unknown=True`.
- **Excluir do ranking principal** (apresentar em ranking secundário "incomplete extraction").
- Não usar default 24h em score, só em sanity report.

---

## Ponto narrativo (precisa entrar em `jornada/`)

A tese original do estudo era "**dois pares 6R replicáveis**" (`1407880↔10224499` + `2373850↔11171596`).

Após Opus re-decode:
- Par primário **SOBREVIVE** (`1407880↔10224499`, ambos `LATE_NY_BREAKOUT`).
- Par diagnóstico **EVAPORA** (`2373850↔11171596`, ambos `UNCATEGORIZED`).

Narrativa atualizada: **"um par principal sobrevivente + um caso negativo sobre vendor library HappyForex"**. Isso precisa aparecer em:
- `ROADMAP.md` (status atualizado da fase 6R).
- `jornada/2026-05-02-*-myfxbook-6R-pair-evaporated.md` (nova entrada).
- `README.md` do estudo (se mencionar 2 pares).

---

## Checklist 5R-1-hardening (ordem revisada 2026-05-02 pós-decisões D1-D7 + R4)

**Wave A** (paralelo, sem dependências):

- [x] **Narrativa** — ROADMAP + jornada par 6R diagnóstico evaporado. Done 2026-05-02 16h30 (`jornada/2026-05-02-1630-myfxbook-reeng-6R-pair-evaporated.md`).
- [x] **CHANGELOG auditável** — SHA + diff em `frozen_rules/CHANGELOG.md` para v1→v2 + chmod log. Done 2026-05-02.
- [x] **Stage 1 sample test** — Opus em 5 systems aleatórios fora dos 15; reclass rate **3/5 = 60% — alarme disparado** (>30%). Done 2026-05-02 (`_diagnostics/stage1_sample_test/SUMMARY.md`).
- [x] **`--limit` + timeout + token-log** — em runners de smoke/overnight. Done 2026-05-02 (`scripts/run_replicator_batch.py` + `shared/run_overnight_validation.py`).

**Wave A.5** (intercalada após decisões D1-D7 do usuário 2026-05-02; pré-requisito empírico para Wave B + R1):

- [x] **R4** — fix Stage 1 hold-extraction NaN (root cause: parsing posicional em layouts não-FX). 31 fully-NaN + 2 mixed → 0/52 NaN. Done 2026-05-02. Detalhe na seção R4 acima + `_diagnostics/R4_summary.md`.
- [ ] **R1** — re-decode integral com Opus dos 30 systems não-rechecados (23 DECODED + 7 PARTIAL), 6 waves × 5 subagents paralelos, custo ~$15-25. Usa enum v2 oficial + fingerprints corrigidos R4. Pendente após Wave B item 2 (precisa do enum disponível).

**Wave B** (sequencial após Wave A.5 R4 fechar; bloqueia até Wave D inteira fechar antes de 5R-2/5R-3):

- [ ] **Taxonomia fechada (enum + provisórias + UNCAT reason_code)** — `shared/decoder_taxonomy.py` single source of truth com 9 famílias originais + 3 provisórias (`H1_MOMENTUM_GOLD`, `NEWS_RELEASE_MOMENTUM`, `SWING_TREND_MOMENTUM`, todas marcadas `provisional=True`). UNCAT exige `reason_code` obrigatório. `candidate_new_family: str | None` mantido para emergentes futuras. Refatorar `shared/decoder_*.py` + prompt do agent decoder para consumir essa fonte única.

**Wave C** (sequencial após Wave B):

- [ ] **Replicator fatiado** — extrair parser/executor/backtest/comparator/score em módulos.
- [ ] **Baselines no comparator (delta only)** — adicionar `always_sell` + `random_frequency_matched` + `permutation_test` (3 já existentes preservados).

**Wave D** (sequencial após Wave C):

- [ ] **Testes unitários** — fixtures pequenas por componente.
- [ ] **`hold_unknown` segregado** — ranking secundário separado (note pós-R4: poucos systems devem cair aqui agora; mecanismo segue válido para casos edge).

Só após Wave D inteira fechar **+ R1 completo**: liberar 5R-2/5R-3.

Audit trail: cada decisão neste checklist citada por `D<N>` no `5R-1-hardening-plan.md` §4 e §4.5.

---

## Referências

- `_diagnostics/opus_redecode_targets.md` — alvos da Phase 5R-0.
- `frozen_rules/CHANGELOG.md` — v2 do batch Opus.
- `adversarial_chat/005-007` — origem do contrato `frozen_rules/`.
- Parecer adversarial cruzado: Opus 4.7 + GPT-5.5 (transcrição na sessão de origem deste documento).
