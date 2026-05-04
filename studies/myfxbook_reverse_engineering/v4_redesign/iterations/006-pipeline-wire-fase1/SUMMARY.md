# SUMMARY — 006-pipeline-wire-fase1

## Verdict

DONE.

## O que foi feito

- `workbench/pipeline.py` ganhou flags opt-in `--enable-pre-screen`, `--abort-on-pre-screen-stop`, `--enable-adversarial`, alias `--system-id` e `--out-dir` para smoke isolado.
- `--enable-pre-screen` roda `pre_decode_screen.screen_system()` antes do Stage 1/backtest, escreve `pre_decode_screen.json` no `out_dir` e, por default, segue o pipeline com warning se `decision != "GO"`. Com `--abort-on-pre-screen-stop`, encerra cedo sem synthetic.
- `--enable-adversarial` chama `adversarial_validate(real_trades, synthetic_trades)` apos `run_backtest()` e adiciona `adversarial_auc`, CI 95%, contagens, top-5 features e notes ao `pipeline_summary.json`.
- Quando alguma flag Fase 1 esta ativa e synthetic existe, o pipeline chama `gates.compute_gates(...).passes_mandate_24()` e expõe `mandate_24_pass` / `mandate_24_failed`; `pbo` e `wf_purged` ficam implicitamente opcionais nesta fase.
- Sem flags, o schema legado do `pipeline_summary.json` foi preservado: nenhum campo `pre_screen_*`, `adversarial_*` ou `mandate_24_*` aparece.
- Adicionados 3 testes unitarios em `tests/myfxbook_pipeline/test_pipeline_v4_wiring.py` para alias CLI, fallback adversarial nao-fatal e wiring do veredito agregado.

## Smoke 1407880

- Com flags: `uv run python studies/myfxbook_reverse_engineering/workbench/pipeline.py --system-id 1407880 --enable-pre-screen --enable-adversarial --out-dir /tmp/v4_smoke_1407880`.
- `pre_decode_screen.json` existe e traz `decision=GO`, `is_live=false`, note Demo warning-only.
- `pipeline_summary.json` contem todos os novos campos.
- `adversarial_auc=1.0`, dentro de `[0, 1]`; top features: `entry_price_normalized`, `lots`, `duration_sec`, `pips`, `hour_utc`.
- `mandate_24_pass=false`; failed gates: `sharpe_bootstrap_ci_low_999`, `oos_bootstrap_ci_low_999`, `dsr_p`.
- Sem flags: `/tmp/v4_smoke_1407880_legacy/pipeline_summary.json` preservou o schema pre-006.

## Citacoes usadas

- Pre-screen MCPT: `[evidence_based_ta, p.325-328]`.
- Adversarial validator real-vs-synthetic AUC: `[advances_fin_ml, ch.5]`.
- DSR hard gate via `passes_mandate_24()`: `[advances_fin_ml, p.273-275]`.
- PBO opcional via `cpcv_result` em fases posteriores: `[advances_fin_ml, p.208-222]`.
- Bootstrap CI usado pelos gates sinteticos: `[advances_fin_ml, p.196-211]`.

## Verificacao

- `uv run pytest tests/myfxbook_pipeline/test_pipeline_v4_wiring.py -q`: 3 passed.
- `uv run pytest tests/myfxbook_pipeline -q`: 36 passed, 4 skipped.
- `uv run pytest -q`: 799 passed, 14 skipped, 3 failed preexistentes em `tests/test_macro_data_loader.py` por caches macro ausentes (`ebp_monthly.parquet`, `t10y3m_daily.parquet`, `cape_monthly.parquet`).

## Caveats / decisoes nao-obvias

- `mandate_24_*` só é anexado quando flags Fase 1 estão ativas para preservar o schema legado exigido pelo smoke sem flags.
- Erro adversarial ou synthetic vazio vira campos `null` + `adversarial_notes`, conforme kill-switch da task; no smoke obrigatório isso nao ocorreu.
- `scripts/run_replicator_batch.py` nao foi alterado porque o driver atual nao chama `workbench.pipeline.run_pipeline(...)`; callers existentes continuam sem mudanca. A task 007 pode usar a CLI nova do `workbench/pipeline.py` ou detalhar um batch wrapper especifico sem mexer no fluxo R1 legado.

## Licao para a proxima task

Task 007 deve rodar batch Fase 1 usando as flags novas e coletar `pre_screen_decision`, `adversarial_auc` e `mandate_24_pass` por system. System `1407880` demonstrou que Demo continua warning-only e que AUC adversarial pode denunciar decode trivially distinguishable mesmo quando pre-screen da track record passa.
