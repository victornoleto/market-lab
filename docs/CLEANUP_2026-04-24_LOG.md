# Cleanup Log — 2026-04-24

Audit trail do cleanup agressivo que reduziu o repo ao mínimo preservando
100% do material Plano C + core engine. Executado em 8 commits isolados,
recuperável via tag `pre-cleanup-2026-04-24`.

Plan file: `/home/victor/.claude/plans/sharded-wondering-spindle.md`

---

## Baseline (pre-cleanup)

- **Tests**: 1168 coletados
- **Repo size** (excl .venv, .git): 1.4G
- **Top-level dirs impactadas**:
  - jornada/ : ~51 MD files + 13 date-dirs (histórico)
  - reports/ : 23 subpastas, 44M
  - scripts/ : 99 .py/.sh top-level + 5 subdirs
  - specs/ : 12 MDs root + 1 _archive
  - docs/ : 5 MDs root + 8 subpastas
  - ops/ : 75 files (standalone CLI platform)
  - src/market_lab/backtest/strategies/ : 40 files
  - tests/ : 83 test files (~1168 tests)

---

## Final state (post-cleanup)

- **Tests**: 704 coletados, 699 passed + 5 skipped, **0 failed** ✅
- **Repo size**: 1.4G (data/ 631M + books/ 483M dominam — não tocadas)
- **Active dirs**:
  - jornada/ : 13 MD files (4 Plano C + 2 studies + 4 arquiteturais + 2
    summaries + README + 1 data-pipeline) + 13 date-dirs preservadas
  - reports/ : 6 subpastas (Plano C + 4 forensic) + _dormant_summary.md + _archive/
  - scripts/ : 15 top-level + data_sprint/
  - specs/ : 1 active + _archive/ (12 files)
  - docs/ : 4 MDs root + 7 subpastas (2 ativos overrides + 6 infra + _archive/)
  - ops/ : REMOVIDO
  - src/market_lab/backtest/strategies/ : 5 files (base + 4 studies modules)
  - tests/ : 49 test files

---

## Commits por etapa

| # | Commit | Subject |
|---|--------|---------|
| 1 | c781c28 | `remove ops/ — substituída por app/ GUI, zero imports externos` |
| 2 | 0eacae1 | `remove temp.txt + prints/ screenshots` |
| 3 | 24743d0 | `consolidate 15+ dormant report dirs → reports/_dormant_summary.md` |
| 4 | b73d6a9 | `consolidate 38 dormant jornadas → _archive/DORMANT_HUNTS.md + rewrite README` |
| 5 | 10246a5 | `remove ~85 dormant scripts (Plano A + iter_v2 + Bollinger + ETF rotation + Phase 3.5/3.6/3.7/3.8/4.0/d_mvp/e_mvp)` |
| 6 | 095e60a | `archive 11 dormant specs → specs/_archive/` |
| 7 | 88581fe | `consolidate dormant docs → _archive/DORMANT_STRATEGIES_SPEC.md` |
| 8+9 | 5bc4f29 | `remove 31 dormant strategies + 10 infra modules + 33 dormant tests` |
| 10 | (este arquivo) | `add CLEANUP_2026-04-24_LOG.md audit trail` |

---

## Detalhamento por área

### Etapa 1 — ops/ (39 files)

Standalone CLI platform pra Plano B swing (DARF calc, FIFO, tax models
monthly_6015 + annual_14754). Zero imports em src/, scripts/, tests/,
app/, studies/ (grep confirmado). Substituída pela GUI em `app/`.

**Removido**: `ops/` inteiro (39 files, ~284KB).

### Etapa 2 — Root litter

**Removido**:
- `temp.txt` (271B, reading-instructions stale de 2026-04-15)
- `prints/*.png` (7 PNGs untracked, setup initial)

### Etapa 3 — reports/ (~27MB liberados)

**Preservado** (6 subpastas, integral):
- `portfolio_aposentadoria_v2/` (8.9M) — Plano C master
- `phase3_5a_v2/` (6.8M) — Plano A V2 forensic (lookahead fix)
- `phase3_5b/` (4.2M) — Plano B canonical reference
- `phase_3_5c/cross_lib/` (3.3M sem `results/`) — cross-lib infra ATIVA (tests/cross_lib/)
- `phase_3_5e/` (820K) — Plano B 7-family continuation
- `phase_3_5f/` (900K) — Plano A V2 honest re-validation

**Removido + consolidado em `_archive/`**:
- `phase_3_5c/results/` (6.8M — stage_1/stage_2 outputs)
- `phase_3_5d/`, `phase_3_6/`, `phase_3_7/`, `phase_3_8/`, `phase_d_mvp/`,
  `phase_e_mvp/`, `phase4_0/`, `bollinger_mr_*/` (4 dirs),
  `regime_decomp_phase_b/`, `etf_rotation_mc_bootstrap/`,
  `b2_benchmark/`, `spec-judges/`, `assets/`, `__pycache__/`
- 13 smoke JSON root-level + `cost_ablation_phase_b.txt`

**Criado**: `reports/_dormant_summary.md` (overview) + `reports/_archive/`
com 7 arquivos-chave (BREADTH_NO_WINNER + ESCALATION_PENDING + FORENSIC).

### Etapa 4 — jornada/ (~400 linhas README + 39 MDs)

**Preservado** (13 files top-level):
- 4 Plano C entries (0500, 1500, 2300, 2359 de 2026-04-23)
- 2 studies sessão (1003 de Apr 23 + 0030 de Apr 24) — **HANDS-OFF** preservados
- 4 arquiteturais (engine-lookahead-bias, engine-lookahead-bug,
  cagr-mdd-tier-framework, data-pipeline-tiingo-first)
- 2 summaries (0700 overnight + 0756 maintenance-mode)
- 1 README.md (reescrito — 580L → 186L)

**Removido**: 39 jornadas DORMANT (Phase 3.5e c01-c06, Phase 3.6 A-K 10
famílias, Phase 3.7-3 H1-H3 8 literário, Phase 3.8-1 B1-B5, Phase D-MVP,
Phase E-MVP, Plano A V2 revalidation).

**Criado**: `jornada/_archive/DORMANT_HUNTS.md` (170L, tabelas
verdict-por-phase + pointers pros BREADTH_NO_WINNER em
`reports/_archive/`).

### Etapa 5 — scripts/ (85 scripts removidos)

**Preservado** (15 top-level + `data_sprint/`):
- Data pipeline: tiingo_bulk_download, tiingo_backup, run_tiingo_migrate,
  clean_intraday_orphans, extract_testfolio_json
- Knowledge base: build_page_index, build_skill, compress_pdfs,
  extract_pdfs, rename_books, validate_summary, check_citations
- Self-improvement: self_improve_loop, smoke_fanout_protocol,
  aggregate_judges

**Removido**:
- 3 Plano A V2 scripts, 6 iter_v2_l*, 4 cTrader OAuth utils
- 11 Bollinger MR, 5 ETF rotation legacy, 3 A3 portfolio leads
- 11 phase_b analysis, 4 plano_b extended, 5 phase3_5b task runners
- 3 phase3_5f revalidation, 22 phase3_6 A-K runners + cross_lib
- 3 phase4_0 CFD gates, 2 tiingo smoke, 1 validate_phase3_winners
- 1 robustness_testfolio
- Subdirs: phase3_7, phase3_8, phase_d_mvp, phase_e_mvp, __pycache__

### Etapa 6 — specs/ (11 archived)

**Preservado** (1 active): `specs/self_improve_fanout_mode.md`

**Moved to `_archive/`** (preserved navigable, not deleted):
- backtest_phase2.md, backtest_phase2_5_ehlers.md (Conclusion fechada)
- phase_3_5a_v2, phase_3_5b_*, phase_3_5d, phase_3_5e (Plano A/B DORMANT)
- phase_4_0_index_cfd_validation, phase_4_paper_trading (pausado)
- post-winners-cleanup (histórico)
- strategy_d_br_ranking (preservado pra reativação futura do Plano D)

### Etapa 7 — docs/ (~6150 linhas consolidadas)

**Preservado** (7 áreas):
- `investment-mandate.md`, `CURRENT_STATE.md`, `tiingo_ablation_rationale.md`,
  `POST_reddit.md`
- `reference/`, `self_improvement/`, `superpowers/` (subpastas infra)
- `mandate_overrides/` com 2 active: `2026-04-23-consolidate-plano-c-final.md`
  (signed load-bearing) + `2026-04-24-crash-protected-letf-open.md`
  (sessão studies paralela — untouched)

**Removido** (git rm):
- `docs/strategies/` (4 MDs, 1613L): Plano A V2-L2 + Plano B 3-leg +
  Pauchlyova static + Pepperstone rate card
- `docs/plans/` (8 MDs, 3020L): engine fix + phase 3.6/3.7/3.8/3.9 hunt
  prompts
- `docs/research/` (2 MDs, 1288L): phase 3.7-1 literature sprint + 3.7-2
  data sprint
- `docs/phase3_winners_allocation.md` (229L): Phase 3 winners retracted

**Moved to `_archive/`**:
- `mandate_overrides/2026-04-22-strategy-d-open.md`
- `mandate_overrides/2026-04-23-strategy-e-multimarket.md`

**Criado**: `docs/_archive/DORMANT_STRATEGIES_SPEC.md` (120L overview).

### Etapa 8+9 — src/market_lab + tests/ (31 strategies + 10 infra + 33 tests)

**Preservado strategies** (5 files):
- `base.py`, `__init__.py`, `ema_sma_threshold_educational.py`,
  `stop_loss_and_risk_signals.py`, `stop_loss_and_risk_signals_numpy.py`
  (últimos 3 são sessão studies untracked, HANDS-OFF)

**Removido strategies** (31):
- Phase 3.6 A-K × 10, Phase 3.7 H1/H2/H3 × 8, Phase 3.8 B1-B5 × 5
- Legacy: afml_tb_meta, bollinger_mr, donchian_breakout, etf_rotation,
  kalman_pair_cointegration, plano_a_leveraged_rotation, ranking_br,
  regime_filtered, session_based, tsmom, tsmom_multi_asset

**Removido infra** (10):
- `grid/`: letf_rotation_grid, portfolio_3leg, portfolio_combiner,
  tsmom_a3b, strategy_benchmark
- `metrics/`: rolling_correlation, slippage_sensitivity, allocation_comparison

**Restaurados** (cascata de dependência da sessão studies):
- `src/market_lab/backtest/grid/bollinger_mr_config.py`
- `src/market_lab/backtest/grid/letf_rotation_b1c.py`
- `src/market_lab/backtest/strategies/letf_rotation.py`
(imported por `studies/ema_sma_threshold_grid.py` via
`studies/ema_sma_threshold_educational/` — ver diff vs tag).

**Removido tests** (33 files): todos os correspondentes às strategies +
infra deletadas (test_letf_rotation*, test_phase3_7_*, test_phase3_8_*,
test_phase_d_mvp_orchestrator, test_plano_a_*, test_portfolio_3leg,
test_portfolio_combiner, test_ranking_br, test_regime_filtered,
test_rolling_correlation, test_slippage_sensitivity, test_tsmom*,
test_bollinger_mr, test_donchian_breakout, test_etf_rotation,
test_kalman_pair_cointegration, test_session_based,
test_allocation_comparison, test_get_trades_hooks,
test_strategy_benchmark, test_phase3_7_data_integrity).

**Atualizado**: `strategies/__init__.py` — removidas referências a
BollingerMR + ETFRotation (já deletadas).

---

## Verification

✅ **Tests baseline**: 699 passed + 5 skipped = 704 tests, **0 failed**
✅ **No broken imports**: `pytest --collect-only` sem erros
✅ **Studies intactos**: `git diff pre-cleanup-2026-04-24 -- studies/` vazio
✅ **App intacto**: `git diff pre-cleanup-2026-04-24 -- app/` vazio
✅ **Plano C integral**: `portfolio-aposentadoria.md` + `reports/portfolio_aposentadoria_v2/` preservados
✅ **Tag recuperação**: `git tag | grep pre-cleanup-2026-04-24` retorna match
✅ **Commits isolados**: 8 chore(cleanup) commits, revertíveis individualmente

---

## Resumo numérico

| Antes | Depois | Redução |
|-------|--------|---------|
| 51 jornadas raiz | 13 | -75% |
| 23 subpastas reports | 6 + `_archive/` (7 files) | -65% |
| 99 scripts root | 15 | -85% |
| 12 specs root | 1 active + 12 em `_archive/` | -92% top-level |
| 14 docs DORMANT (5921L) | 1 consolidated (120L) | -98% |
| 75 arquivos ops/ | 0 | -100% |
| 40 strategy modules | 5 (incl. 3 studies) | -88% |
| 83 test files | 49 | -41% |
| 8 root litter files | 0 | -100% |
| **1168 tests** | **704 tests, 699 passed** | **-40% tests, 0 regressão** |

---

## Recovery cheatsheet

```bash
# Estado pré-cleanup é a tag `pre-cleanup-2026-04-24`.

# Recuperar 1 arquivo específico:
git checkout pre-cleanup-2026-04-24 -- <path>

# Ver conteúdo sem checkout:
git show pre-cleanup-2026-04-24:<path>

# Listar tudo que existia:
git ls-tree -r --name-only pre-cleanup-2026-04-24 | less

# Reverter 1 commit específico (cirúrgico):
git revert <sha>

# Reverter TUDO (voltar pro estado pré-cleanup):
git reset --hard pre-cleanup-2026-04-24  # DESTRUTIVO — use com cuidado
```

---

## Sign-off

- [x] Executor (Claude) — todas as etapas concluídas; verification passou
- [ ] User — revisar este log antes de eventual push do main upstream
