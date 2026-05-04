# TASKS — Pipeline v4 Redesign (28 tasks ordenadas)

Lista frozen das tasks. Alteracoes exigem decisao do usuario registrada em
`jornada/`. **Status mutavel vai em `PROGRESS.md`** (este arquivo nao guarda
status).

Convencoes:
- ID: `NNN-slug` (3 digitos, ordem de execucao)
- `depends_on`: lista de task IDs que devem estar `DONE` antes
- `phase`: 1 / 2A / 2B / 3a / 3b / final
- `effort`: estimativa em sessoes (uma sessao = 1-3h de relogio)

---

## Fase 1 — Tighten the diagnostic loop (semanas 1-2)

### 001-skeleton-setup
- Phase: 1
- Effort: 1
- depends_on: []
- Goal: Criar arquivos vazios de modulos novos (pre_decode_screen.py, cpcv.py,
  adversarial_validator.py, news_calendar.py, cross_asset_features.py,
  meta_labeler.py, etc) com docstrings e citacoes; criar diretorios de testes.
  Sem logica ainda. Garantir baseline 461 testes ainda passa.

### 002-pre-decode-screen
- Phase: 1
- Effort: 2-3
- depends_on: [001]
- Goal: Implementar `shared/pre_decode_screen.py` com 5 gates:
  - K1 sanity (martingale signature; reusa `sanity.py` existente)
  - MCPT na track record do EA `[evidence_based_ta, p.325-328]`
  - PSR p<0.05 na track record `[advances_fin_ml, p.260-263]`
  - Concentration test (top-5% trades vs total PnL)
  - Live-vs-demo flag — **warning-only**, nao bloqueia
  Output: `pre_decode_screen.json` por system com pass/fail.
  Testes unitarios contra golden EAs (10281851 PASS Real, 11504701 STOP martingale, 1407880 demo flag).

### 003-cpcv-pbo
- Phase: 1
- Effort: 2
- depends_on: [001]
- Goal: Implementar `shared/cpcv.py` com CSCV (Combinatorial Symmetric Cross
  Validation) e PBO (Probability of Backtest Overfitting). `[advances_fin_ml,
  p.208-222]`. Complementa WF8/purged-WF: PBO mede sorte na selecao entre
  candidatos; WF mede generalizacao temporal de uma regra. Testes unitarios
  contra cenarios sinteticos canonicos.

### 004-gates-dsr-hard
- Phase: 1
- Effort: 1-2
- depends_on: [003]
- Goal: Refatorar `shared/gates.py` — promover DSR de informativo para hard gate
  (p<0.05 bloqueia). Adicionar PBO via cpcv.py como gate. Manter CAGR/MDD
  warning-only conforme mandate §2.2/§2.3. Atualizar testes existentes.

### 005-adversarial-validator
- Phase: 1
- Effort: 2
- depends_on: [001]
- Goal: `shared/adversarial_validator.py` — LightGBM binario real-vs-synthetic
  classifier, AUC como metrica de identificabilidade. Sanity tests: copia exata
  → AUC≈0.5; ruido puro → AUC>0.9. `[advances_fin_ml, ch.5]` para feature
  importance.

### 006-pipeline-wire-fase1
- Phase: 1
- Effort: 2
- depends_on: [002, 003, 004, 005]
- Goal: Wire `pre_decode_screen` e `adversarial_validator` em
  `workbench/pipeline.py` como flags `--enable-pre-screen --enable-adversarial`.
  Smoke test em system 1407880. Garantir que pipeline antigo continua rodando
  sem flags (backward-compat).

### 007-fase1-batch-run
- Phase: 1
- Effort: 1 (ou 2 dependendo do compute)
- depends_on: [006]
- Goal: Rodar `run_replicator_batch` com flags Fase 1 em todos os 30 systems R1
  v3 e os 22 NOT_DECODED restantes. Output: tabela "EAs sobreviventes" (max 10)
  em `iterations/007-fase1-batch-run/RESULTS.json`. Comparar baseline pre-Fase 1
  vs pos-Fase 1.

### 008-fase1-document
- Phase: 1
- Effort: 1
- depends_on: [007]
- Goal: Escrever `_diagnostics/PIPELINE_V4_FASE1_REPORT.md` consolidando os 30+22
  resultados, lista N≤10 sobreviventes, decisao GO/STOP para Fase 2. Atualizar
  jornada com entry "Fase 1 concluida".

---

## Fase 2A — Inputs ricos (semanas 3-4)

### 009-news-calendar
- Phase: 2A
- Effort: 2
- depends_on: [008]
- Goal: `shared/news_calendar.py` — ingest Forex Factory CSV (free dump). Output
  features `is_news_window_5min`, `news_impact (low/med/high)`,
  `minutes_to_next_high_impact`. Cache em `data/news/forex_factory_*.parquet`.
  Cita `[evidence_based_ta, ch.7]` para news effects.

### 010-cross-asset-features
- Phase: 2A
- Effort: 2
- depends_on: [008]
- Goal: `shared/cross_asset_features.py` — DXY proxy (UUP), VIX, gold/silver
  ratio (XAU/XAG), BTC dominance, US10Y, breakeven inflation. Source via cache
  Tiingo `data/tiingo/`. Output features alinhadas a candidate_window.

### 011-tick-volume-features
- Phase: 2A
- Effort: 3
- depends_on: [008]
- Goal: Estender `shared/ohlc_dukascopy.py` para ingerir Dukascopy ticks (free).
  Cache em `data/ticks/<pair>/<YYYY-MM>/`. Output features `tick_count_5min`,
  `up_tick_ratio`, `aggressive_buy_ratio`. Cita `[advances_fin_ml, ch.2]` para
  tick bars.

### 012-realized-vol-regime
- Phase: 2A
- Effort: 1-2
- depends_on: [010]
- Goal: Adicionar `realized_vol_regime` em `decoder_features.py` — HAR-RV bucket
  (low/normal/high) per pair. `[volatility_trading, p.173-177]`.

### 013-decoder-features-wire-2a
- Phase: 2A
- Effort: 1
- depends_on: [009, 010, 011, 012]
- Goal: Wire features A1-A4 em `decoder_features.py.compute_entry_features()`.
  Garantir backward-compat (features novas opt-in via flag).

### 014-fase2a-batch-run
- Phase: 2A
- Effort: 1
- depends_on: [013]
- Goal: Rodar replicator nos N≤10 sobreviventes com features A1-A4 ativas.
  Comparar `adversarial_auc` baseline vs novo, F1 timing baseline vs novo.

---

## Fase 2B — Metodologia (semanas 5-6)

### 015-lightgbm-miner
- Phase: 2B
- Effort: 2-3
- depends_on: [014]
- Goal: `shared/lightgbm_miner.py` — substituir univariate+tree+RIPPER por
  LightGBM purged-CV + permutation importance + monotonic constraints. Manter
  miners antigos como baseline para comparacao em `decoder_candidates.py`.
  `[advances_fin_ml, ch.5]`.

### 016-meta-labeler
- Phase: 2B
- Effort: 3
- depends_on: [015]
- Goal: `shared/meta_labeler.py` — primary classifier (Buy/Sell/None) sobre
  janela bruta; secondary classifier (take/skip) apenas nos pontos do primary.
  `[advances_fin_ml, p.84-89]`. Output: `meta_labeled_synthetic_trades.parquet`.

### 017-replicator-wire-2b
- Phase: 2B
- Effort: 2
- depends_on: [016]
- Goal: Wire LightGBM miner + meta-labeling em `replicator.py`. Adicionar
  `meta_label_auc`, `timing_f1_post_meta` em `pipeline_summary.json`. Smoke
  test em 1407880.

### 018-fase2b-batch-run
- Phase: 2B
- Effort: 1
- depends_on: [017]
- Goal: Rodar replicator nos N≤10 com Trilha A+B completa.

### 019-decision-gate-fase2-fase3
- Phase: 2B
- Effort: 1
- depends_on: [018]
- Goal: **DECISION GATE.** Avaliar se F1 timing > 0.30 em ≥3 systems E
  adversarial AUC < 0.65 E §2.4 gates passam. Output:
  `iterations/019-decision-gate/DECISION.md` com veredito (Fase 3a prioridade ou
  Fase 3b prioridade), tabela de evidencia, recomendacao de proximos tickets.
  Atualizar jornada.

---

## Fase 3a — Decode-self path (semanas 7-10)

### 020-transformer-encoder
- Phase: 3a
- Effort: 4-5
- depends_on: [019]
- Goal: `shared/transformer_encoder.py` — Transformer encoder pequeno (4 layers,
  64 dim) sobre janela [-200, 0] bars. Head linear → P(real entry no bar atual).
  Treino purged k-fold + embargo. Comparar contra LightGBM. Se Transformer
  >+0.1 AUC mantém; senão descarta YAGNI. `[advances_fin_ml, ch.5, ch.7]`.

### 021-hmm-regime-mixture
- Phase: 3a
- Effort: 3
- depends_on: [019]
- Goal: `shared/hmm_regime_mixture.py` — HMM 3-estados (trend/MR/quiet) sobre
  trade history. Classifica cada trade real em regime; treina rules separadas
  por regime; combina com gating. Aplicar em EAs com `taxonomy_gap`.
  `[machine_trading, ch.4]`.

### 022-out-of-domain-transfer
- Phase: 3a
- Effort: 2
- depends_on: [020]
- Goal: `shared/out_of_domain_transfer.py` — train EUR pairs, test JPY pairs.
  Edge real transfere; sobreajuste nao. Output: `transfer_score` em
  `pipeline_summary.json`. Gate Sharpe OOS ≥ 50% Sharpe in-domain.

### 023-cross-lib-validator
- Phase: 3a
- Effort: 2
- depends_on: [022]
- Goal: Estender `studies/global_factor_tilt_loop/cross_lib_validator.py` (ja
  existente) para a engine atual; reimplementar mesma regra em vectorbt e
  backtrader; CAGR ±3pp. STUB — detalhar quando chegar.

### 024-fase3a-document
- Phase: 3a
- Effort: 1
- depends_on: [023]
- Goal: Documentar Fase 3a com tabela best-decoded-rule por system.

---

## Fase 3b — Filter-and-copy path (semanas 7-8 + monitor 60d)

### 025-signal-score-consolidated
- Phase: 3b
- Effort: 2
- depends_on: [019]
- Goal: `shared/signal_score_consolidated.py` — combinacao ponderada de PBO,
  DSR, MCPT, adversarial_auc, concentration. Output: `signal_quality_score`
  por system; ranking top-3 EAs.

### 026-forward-monitor-setup
- Phase: 3b
- Effort: 2
- depends_on: [025]
- Goal: `shared/forward_monitor.py` — agendamento weekly de
  `download_data.scrape_one_system` para os top-3 EAs; diff dos novos trades
  contra ultimos. Cron via `cron/myfxbook_weekly.cron` ou `loop.sh` separado.

### 027-fase3b-document
- Phase: 3b
- Effort: 1
- depends_on: [026]
- Goal: Documentar Fase 3b com setup do monitor e racional do top-3. Forward
  monitor 60d roda em background; nao bloqueia tasks subsequentes.

---

## Final (semanas 11-12)

### 028-pipeline-v4-final-report
- Phase: final
- Effort: 1-2
- depends_on: [024, 027]
- Goal: `_diagnostics/PIPELINE_V4_FINAL.md` — consolidar Fase 3a (decode-self) e
  Fase 3b (filter-and-copy), apresentar verdict e opcoes para o usuario:
  - Plano A reativacao (mandate §7) se decode passou criterio final?
  - Filter-and-copy via myfxbook AutoTrade?
  - Encerrar definitivamente?

---

## Mapa de dependencias (resumo)

```
001 → 002, 003, 005
003 → 004
{002, 003, 004, 005} → 006 → 007 → 008
008 → {009, 010, 011}
{009, 010} → 012
{009..012} → 013 → 014
014 → 015 → 016 → 017 → 018 → 019
019 → {020, 021, 025}
020 → 022 → 023 → 024
025 → 026 → 027
{024, 027} → 028
```

## Tarefas STUB que precisam detalhamento on-demand

- 023 (cross-lib): detalhar quando chegar (depende da forma final da regra)
- 026 (forward monitor): detalhar formato de notificacao/alerta quando chegar

Outras tasks tem spec detalhado em `tasks/NNN-slug.md` (Fase 1) ou serao
detalhadas pela sessao que executa a anterior (Fase 2 e 3).
