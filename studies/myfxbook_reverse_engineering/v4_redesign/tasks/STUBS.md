# Tasks 009-028 — STUBS

Specs detalhados das tasks da Fase 2 e Fase 3 sao **postponed**: cada sessao que
completa uma task e responsavel por detalhar a NEXT (ou a NEXT+1 quando ha
paralelismo), gravando em `tasks/NNN-slug.md` antes de encerrar a sessao.

Razao: o N≤10 universo de Fase 2 sai apenas da Fase 1 (task 008). Os specs
das tasks 009-014 dependem desse universo (quais pairs, quais hours_utc, qual
volume de tick data).

## Resumo (de TASKS.md)

| ID | Phase | Goal (resumo) |
|---|---|---|
| 009-news-calendar | 2A | `shared/news_calendar.py`: Forex Factory CSV ingest, features news-aware |
| 010-cross-asset-features | 2A | `shared/cross_asset_features.py`: DXY/VIX/etc via Tiingo |
| 011-tick-volume-features | 2A | Estender `ohlc_dukascopy.py` para ticks; features tick_count/imbalance |
| 012-realized-vol-regime | 2A | HAR-RV bucket em decoder_features.py |
| 013-decoder-features-wire-2a | 2A | Wire A1-A4 em compute_entry_features() |
| 014-fase2a-batch-run | 2A | Batch nos N≤10 com features novas |
| 015-lightgbm-miner | 2B | `shared/lightgbm_miner.py`: substitui univariate+tree+RIPPER |
| 016-meta-labeler | 2B | `shared/meta_labeler.py`: primary side + secondary take |
| 017-replicator-wire-2b | 2B | Wire LightGBM + meta-labeling em replicator.py |
| 018-fase2b-batch-run | 2B | Batch nos N≤10 com Trilha A+B completa |
| 019-decision-gate-fase2-fase3 | 2B | DECISION GATE; aloca Fase 3a vs 3b prioridade |
| 020-transformer-encoder | 3a | `shared/transformer_encoder.py`: pequeno encoder |
| 021-hmm-regime-mixture | 3a | `shared/hmm_regime_mixture.py`: 3 regimes |
| 022-out-of-domain-transfer | 3a | `shared/out_of_domain_transfer.py`: EUR train, JPY test |
| 023-cross-lib-validator | 3a | Estender existente; ±3pp em vectorbt+backtrader |
| 024-fase3a-document | 3a | Tabela best-decoded-rule por system |
| 025-signal-score-consolidated | 3b | `shared/signal_score_consolidated.py`: ranking |
| 026-forward-monitor-setup | 3b | `shared/forward_monitor.py`: cron weekly + diff |
| 027-fase3b-document | 3b | Setup do monitor + racional do top-3 |
| 028-pipeline-v4-final-report | final | `_diagnostics/PIPELINE_V4_FINAL.md` |

## Como detalhar uma task STUB

Quando voce (sessao Claude Code) completar a task NNN e a proxima e STUB:

1. Ler o resumo desta task em STUBS.md ou TASKS.md
2. Ler outputs da task NNN (em iterations/NNN/) para informar decisoes
3. Criar `tasks/<NNN+1>-slug.md` seguindo o template das tasks 001-008
4. Conteudo minimo:
   - Goal claro
   - Files to create/modify
   - Interface (signatures, dataclasses)
   - Testes obrigatorios
   - Verificacao (comandos exatos)
   - Aceite (checklist)
   - Kill-switches
   - Citacoes obrigatorias
5. Atualizar `next_prompt.md` apontando para a task recem-detalhada

Nao detalhar mais de 2 tasks de uma vez. YAGNI.

## Citacoes guia (por task)

Para evitar guess, cada task usa estas citacoes core:

- 009 news_calendar — `[evidence_based_ta, ch.7]`
- 010 cross_asset — `[volatility_trading, p.173-177]`, `[trading_systems_methods, p.1024]`
- 011 tick_volume — `[advances_fin_ml, ch.2]`
- 012 realized_vol — `[volatility_trading, p.173-177]`
- 013 decoder wire — sem citacao nova
- 014 batch run — `[advances_fin_ml, p.196-211]` (gates)
- 015 lightgbm — `[advances_fin_ml, ch.5]`
- 016 meta_label — `[advances_fin_ml, p.84-89]`
- 017 replicator wire — sem citacao nova
- 018 batch run — `[advances_fin_ml, p.196-211]`
- 019 decision gate — sem citacao nova
- 020 transformer — `[advances_fin_ml, ch.5, ch.7]`
- 021 hmm — `[machine_trading, ch.4]`
- 022 OOD transfer — `[testing_tuning, p.148-162]`
- 023 cross-lib — `[systematic_trading, ch.4]` (engine equivalence)
- 024 doc — sem citacao nova
- 025 signal score — `[advances_fin_ml, p.196-211]`
- 026 forward monitor — `[advances_fin_ml, ch.14]`
- 027 doc — sem citacao nova
- 028 final report — sem citacao nova
