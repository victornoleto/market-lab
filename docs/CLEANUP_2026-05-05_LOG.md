# CLEANUP 2026-05-05 — Audit Log

**Executor:** Claude Code (sessão única)
**User:** Victor Noleto
**Plan file:** `/home/victor/.claude/plans/snuggly-drifting-cascade.md`
**Recovery tag:** `pre-cleanup-2026-05-05`
**Playbook:** `docs/CLEANUP.md` (run anterior: `docs/CLEANUP_2026-04-24_LOG.md`)

---

## Sumário executivo

Cleanup agressivo focado em `studies/` após confirmação de hunt closures recentes (myfxbook v4 em 2026-05-04, spy_beater em 2026-04-30). Recuperação total: **2.3 GB** (~43%). Zero regressão de testes (813 colhidos, 798 passed, 17 skipped, 3 failures **pré-existentes** confirmadas via checkout da tag).

| Área | Antes | Depois | Δ |
|---|---:|---:|---:|
| Total repo (excl .venv/.git) | 5.3 GB | 3.0 GB | **−2.3 GB** |
| `studies/` | 3.2 GB | 854 MB | **−2.4 GB** |
| `studies/myfxbook_reverse_engineering/` | 2.3 GB | 55 MB | **−2.25 GB** |
| `studies/spy_beater_hunt/` | 530 MB | 477 MB | −53 MB |
| `docs/` | 18 MB | 18 MB | 0 (movido p/ _archive) |
| `logs/` | 18 MB | 6 MB | −12 MB (tarballed) |
| Top-level cruft | ~810 KB | 0 | −810 KB |
| Pycache scattered | ~5 MB | 0 | −5 MB |

---

## Decisões alinhadas com o user (AskUserQuestion 2026-05-05)

| Tópico | Escolha autorizada |
|---|---|
| myfxbook 2.3GB | Agressivo: deletar OHLC + trades, manter verdict + decoding_v4_fase1 |
| spy_beater iters 001-039 | Deletar `testfolio_data/`, manter SUMMARY + verdict |
| Meta-state docs | Refresh CLAUDE.md, ROADMAP.md, CURRENT_STATE.md (+README) |

---

## Tabela de commits

| # | Etapa | SHA | Subject |
|---|---|---|---|
| 1 | Etapa 1 — cruft trivial + pycache | `efbd829` | chore(cleanup): remove root cruft + pycache |
| 2 | Etapa 2 — myfxbook bulk | (sem commit — untracked/gitignored) | OHLC 1.8GB + trades 406MB + 2 candidate_window.parquet |
| 3 | Etapa 3 — spy_beater testfolio_data | `3345dec` | chore(cleanup): drop spy_beater iter 039 testfolio_data |
| 4 | Etapa 4 — docs/reference → archive | `cbd4f34` | chore(cleanup): archive docs/reference into docs/_archive/reference_backups (17MB) |
| 5 | Etapa 5 — logs/ rotation | (sem commit — gitignored) | tarball `logs/_archived_hunt_logs.tar.gz` (2.6MB) |
| 6 | Etapa 6 — reports/__pycache__ + cross_lib check | (sem commit — untracked) | rm pycache; cross_lib coleta 40 tests OK |
| 7 | Etapa 7 — meta-state refresh | `010243f` | chore(cleanup): refresh meta-state docs to 2026-05-05 |
| 8 | Etapa 8 — validação | (sem commit) | pytest 813 collected; HANDS-OFF zero diff |
| 9 | Etapa 9 — este LOG | (a seguir) | chore(cleanup): add CLEANUP_2026-05-05_LOG.md |
| 10 | Etapa 10 — jornada/ entry | (a seguir) | docs(jornada): cleanup 2026-05-05 entry |

---

## Etapa 1 — Cruft trivial

### REMOVED (tracked → git rm)
- `happyforex-landing.png` (788 KB) — órfão da hunt myfxbook v1
- `AGENTS.md` (593 B) — residual da bestfolio-hunt phase
- `market-lab-library-audit.md` (20 KB) — audit pré-Phase 3.5; preservado em git history

### REMOVED (untracked → rm)
- `.codex` (0 B) — marker stale
- 21 dirs `__pycache__/` espalhadas (excl `.venv/`, `app/`)
- 358 arquivos `*.pyc`

---

## Etapa 2 — myfxbook reverse engineering bulk

Hunt CLOSED 2026-05-04 com veredito `CLOSED_NO_OPERABLE_EDGE` (`_diagnostics/PIPELINE_V4_CLOSURE.md`).

### REMOVED (untracked — gitignored sob `studies/*/data/`)
- `studies/myfxbook_reverse_engineering/data/ohlc/` (1.8 GB Dukascopy 1m parquets, 10.786 arquivos)
- `studies/myfxbook_reverse_engineering/data/trades/` (406 MB trades parquets per-system)
- `studies/myfxbook_reverse_engineering/systems/1407880/workbench/candidate_window.parquet` (42 MB)
- `studies/myfxbook_reverse_engineering/systems/9526428/workbench/candidate_window.parquet` (61 MB)

### PRESERVED
- `_diagnostics/` (verdict canônico)
- `frozen_rules/` (1.4 MB — regras pré-registradas)
- `v4_redesign/` (772 KB — design docs)
- `data/catalog/` (1.7 MB — catalog metadata)
- `systems/*/decoding_v4_fase1/` (resultados Fase 1, base do verdict)
- `systems/*/{system_info.json,signal_rule.md,validation_report.md,reliability_score.json}`
- `shared/`, `workbench/`, `scripts/` (Python modules — importados por `tests/myfxbook_pipeline/`)
- `ROADMAP.md`, `README.md`

### Verificação de import-graph antes do delete
- grep cascata em `src/ tests/ scripts/` — zero referências às paths `data/ohlc` ou `data/trades`
- Tests em `tests/myfxbook_pipeline/test_pre_decode_screen.py` usam `@pytest.mark.skipif(not _golden_available(...))` — skipam graciosamente quando dados ausentes

### Recuperação
Re-fetch via `studies/myfxbook_reverse_engineering/shared/{ohlc_dukascopy.py,fetcher.py,parser.py}` se reativar (lento). Plano A continua DORMANT — reativação exige literatura/regime novos.

---

## Etapa 3 — spy_beater testfolio_data

Hunt CLOSED 2026-04-30 com **B4 Conservative** (25 NTSX / 25 GDE / 25 RSST / 25 ZROZ, Sharpe 0.745 net) declared deploy-ready.

### REMOVED (tracked — git rm)
- `studies/spy_beater_hunt/iterations/039-2026-04-30-reddit-comparison-spy-lrs-vs-static-stack/testfolio_data/` (52.6 MB, 4 backtest JSONs)

### Achado vs estimativa
Auditoria estimou ~300 MB em iters 001-039. Realidade: iters 001-038 nunca tiveram `testfolio_data/` (já minimal: 3-6 MB cada, só `results.json` + plots). Apenas iter 039 (post-closure reddit comparison) tinha `testfolio_data/`.

### PRESERVED (iters 001-038)
- `SUMMARY.md`, `final_report.md`, `hypothesis.md`, `results.json`, `verdict.json`, plots — intactos.

### PRESERVED (iters 040-055)
- Inteiros — post-closure RSST-corrected validation, methodologically canonical.

---

## Etapa 4 — docs/reference → archive

### MOVED (git mv)
- `docs/reference/letf_rotation_reddit_analysis.md` (12 KB)
- `docs/reference/letf_rotation_reddit_post.pdf` (4.6 MB)
- `docs/reference/letf_rotation_testfol_payload.json` (4 KB)
- `docs/reference/testfolio_letf_spy_ema_125_response.json` (12 MB)
→ `docs/_archive/reference_backups/`

Verificação: zero referências cruzadas (`grep -rn docs/reference docs/ src/ tests/ scripts/ studies/`).

---

## Etapa 5 — logs/ rotation

Tudo em `logs/` é gitignored (zero tracked).

### ARCHIVED → tarball
`logs/_archived_hunt_logs.tar.gz` (2.6 MB) contém:
- `bestfolio_hunt_loop/` (14 MB) — Phase 3.8 closed sem winner
- `myfxbook_v4_redesign/` (436 KB)
- `strategy_hunt_loop/` (536 KB)
- `day_swing_strategy_hunt/` (104 KB)
- `global_factor_tilt_loop/` (88 KB)
- `spy_beater_hunt/` (60 KB)
- `long_term_portfolio/` (48 KB)
- `gold_swing_loop/` (8 KB)

### PRESERVED
- `logs/self_improve/` (1.2 MB) — loop ativo
- `logs/grid.log`, `logs/tiingo.log` — unified logs ativos
- `logs/grid_latest_status.md`
- Logs root-level com nomes de phases concluídas (deixados intactos para preservar trail forense; podem ser limpos manualmente se necessário)

---

## Etapa 6 — reports/__pycache__ + cross_lib check

### REMOVED (untracked)
- `reports/__pycache__/`
- `reports/phase_3_5c/__pycache__/`
- `reports/phase_3_5c/cross_lib/__pycache__/`
- `reports/portfolio_aposentadoria_v2/scripts/__pycache__/`

### Validação
`.venv/bin/pytest tests/cross_lib/ --collect-only -q` → **40 tests collected, 0 erros de import** ✓.

---

## Etapa 7 — meta-state refresh

### EDITED
- **`CLAUDE.md`**: pytest baseline `461` → **`813`**; quick-refs aponta `docs/CURRENT_STATE.md` + `CLEANUP.md` em vez de path stale do plan-file.
- **`ROADMAP.md`**: banner no topo apontando `docs/CURRENT_STATE.md` como state-of-now (ROADMAP fica como histórico técnico das fases 0-3.8).
- **`docs/CURRENT_STATE.md`**: rewrite total snapshot 2026-05-05. MAINTENANCE MODE 100% Plano C; status atualizado de cada subdir em `studies/` (myfxbook CLOSED, spy_beater B4 deploy-ready, long_term BLOCKED, factor_tilt FROZEN, day_swing bootstrap); pytest baseline 813; pointers para CLEANUP_2026-04-24/2026-05-05_LOG.md.
- **`README.md`**: status table compacta 3.6/3.7/3.8 em 1 linha; current reality bloco refletindo MAINTENANCE MODE.

---

## Etapa 8 — Validação final (Verification Matrix)

| Check | Comando | Resultado | OK? |
|---|---|---|---|
| Tests baseline mantido | `pytest --collect-only -q` | 813 collected | ✅ |
| Tests run | `pytest --tb=no -q` | 798 passed, 17 skipped, **3 failed (PRE-EXISTING)** | ⚠️ |
| HANDS-OFF `app/` zero diff | `git diff pre-cleanup-2026-05-05 -- app/` | 0 lines | ✅ |
| HANDS-OFF `books/` zero diff | idem | 0 lines | ✅ |
| HANDS-OFF `data/` zero diff | idem | 0 lines | ✅ |
| HANDS-OFF `knowledge/` zero diff | idem | 0 lines | ✅ |
| HANDS-OFF `studies/_shared/` zero diff | idem | 0 lines | ✅ |
| HANDS-OFF `studies/_archive/` zero diff | idem | 0 lines | ✅ |
| HANDS-OFF `studies/long_term_portfolio/` zero diff | idem | 0 lines | ✅ |
| HANDS-OFF `studies/global_factor_tilt_loop/` zero diff | idem | 0 lines | ✅ |
| HANDS-OFF `studies/day_swing_strategy_hunt/` zero diff | idem | 0 lines | ✅ |
| Plano C zero diff | `git diff pre-cleanup-2026-05-05 -- portfolio-aposentadoria.md reports/portfolio_aposentadoria_v2/ docs/investment-mandate.md docs/mandate_overrides/` | 0 lines | ✅ |
| Cross-lib coleta | `pytest tests/cross_lib/ --collect-only -q` | 40 collected | ✅ |
| Recovery tag exists | `git tag \| grep pre-cleanup-2026-05-05` | presente | ✅ |
| Tamanho reduziu | `du -sh .` | 5.3 GB → 3.0 GB | ✅ |

### 3 failures pré-existentes — NÃO causadas por cleanup

`tests/test_macro_data_loader.py::TestLoaderSmoke::*`:
- `test_ebp_monthly_loads_with_expected_columns`
- `test_term_spread_daily_loads`
- `test_cape_monthly_loads`

**Causa raiz:** `data/external/macro/{ebp_monthly,t10y3m_daily,cape_monthly}.parquet` ausentes (cache nunca foi commitado; tag também tem dir vazio).

**Verificação:** rodei `git checkout pre-cleanup-2026-05-05 -- tests/test_macro_data_loader.py src/market_lab/backtest/data/macro_data_loader.py && pytest tests/test_macro_data_loader.py` — mesmo 3 falhas. Cleanup neutro.

**Recomendação separada:** rodar fetch dos 3 caches FRED/Shiller (não é escopo deste cleanup).

---

## Recovery cheatsheet

```bash
# Restaurar arquivo individual
git checkout pre-cleanup-2026-05-05 -- <path>

# Restaurar comparações detalhadas (ler antes de restaurar)
git show pre-cleanup-2026-05-05:<path>

# Reverter um commit específico (cirúrgico)
git revert efbd829   # cruft + pycache
git revert 3345dec   # spy_beater iter 039
git revert cbd4f34   # docs/reference move
git revert 010243f   # meta-state refresh

# ⚠️ DESTRUTIVO — voltar tudo (avisar user antes)
git reset --hard pre-cleanup-2026-05-05
```

### Re-fetch myfxbook bulk se reativar
```bash
cd studies/myfxbook_reverse_engineering
# 1. OHLC Dukascopy
.venv/bin/python shared/ohlc_dukascopy.py --pairs <list> --start 2020 --end 2025
# 2. Trades parquets (cookies em .env)
.venv/bin/python shared/fetcher.py --system-id <id>
.venv/bin/python shared/parser.py --system-id <id>
```

---

## Sign-off

- [ ] User reviewed final state
- [ ] User accepts 3 pre-existing test failures (separate from cleanup)
- [ ] LOG approved
