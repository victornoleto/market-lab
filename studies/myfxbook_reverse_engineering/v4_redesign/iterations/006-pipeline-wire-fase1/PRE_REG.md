# PRE_REG — 006-pipeline-wire-fase1

## ID

- Task: `006-pipeline-wire-fase1`
- Phase: 1
- Depends: `002-pre-decode-screen`, `003-cpcv-pbo`, `004-gates-dsr-hard`, `005-adversarial-validator`

## Spec Citations

- `TASKS.md` linhas 66-74: conectar `pre_decode_screen` e `adversarial_validator` em `workbench/pipeline.py` como flags opt-in; smoke em system `1407880`; backward-compat sem flags.
- `tasks/006-pipeline-wire-fase1.md`: adicionar flags de Fase 1, manter pipeline antigo intacto, expor fields adversariais e veredito agregado de gates quando disponivel.

## Escopo Minimo

- Adicionar aliases CLI `--system-id` e `--account-oid`, preservando `--account-oid` como compat legado.
- Adicionar `--out-dir` opcional para smoke isolado sem sobrescrever `systems/<id>/workbench`.
- Adicionar `--enable-pre-screen` e `--abort-on-pre-screen-stop`.
- Rodar `pre_decode_screen.screen_system(system_id)` antes de Stage 1/mining quando habilitado; escrever `pre_decode_screen.json` em `out_dir`; se `decision != "GO"` e abort flag ativa, encerrar cedo sem synthetic.
- Adicionar `--enable-adversarial`; apos `run_backtest()`, chamar `adversarial_validate(real_trades, synthetic_trades)` e incluir campos `adversarial_*` no `pipeline_summary.json`.
- Computar `gates.compute_gates(synthetic_trades, system_id, n_bootstrap=5000)` quando houver synthetic e expor `mandate_24_pass` e `mandate_24_failed`; `pbo` e `wf_purged` permanecem `None` nesta Fase 1.
- Propagar flags em `scripts/run_replicator_batch.py` apenas se houver chamada direta ao workbench; se o batch atual usa `shared.replicator.run_one_full`, preservar compat e nao reescrever o fluxo R1 antigo.

## Inputs Esperados

- `data/trades/1407880/trades.parquet`
- `systems/1407880/system_info.json`
- `systems/1407880/decoder/candidates.json` ou Stage 1 capaz de gerar candidatos.
- OHLC cache usado pelo `OhlcLoader` para o backtest existente.
- Modulos existentes:
  - `studies/myfxbook_reverse_engineering/shared/pre_decode_screen.py`
  - `studies/myfxbook_reverse_engineering/shared/adversarial_validator.py`
  - `studies/myfxbook_reverse_engineering/shared/gates.py`

## Outputs Esperados

- `/tmp/v4_smoke_1407880/pipeline_summary.json`
- `/tmp/v4_smoke_1407880/pre_decode_screen.json`
- `/tmp/v4_smoke_1407880/synthetic_trades.parquet` quando o pipeline segue apos pre-screen.
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/006-pipeline-wire-fase1/run.log`
- `RESULTS.json`, `SUMMARY.md`, `PROGRESS.md`, `next_prompt.md`, jornada entry.

## Citacoes Tecnicas

- Pre-screen MCPT: `[evidence_based_ta, p.325-328]`.
- Adversarial real-vs-synthetic AUC e feature importance: `[advances_fin_ml, ch.5]`.
- DSR como hard gate via `passes_mandate_24()`: `[advances_fin_ml, p.273-275]`.
- PBO opcional via `cpcv_result` quando disponivel: `[advances_fin_ml, p.208-222]`.
- Bootstrap CI usado pelo gate sintentico: `[advances_fin_ml, p.196-211]`.

## Criterios de Aceite

- Com `--enable-pre-screen --enable-adversarial --out-dir /tmp/v4_smoke_1407880`, system `1407880` gera `pre_decode_screen.json` e `pipeline_summary.json` com campos novos.
- `adversarial_auc` e numerico em `[0, 1]` ou `null` apenas se synthetic vazio/erro documentado; para o smoke exigido deve ser numerico.
- Sem flags, `pipeline_summary.json` preserva o schema pre-006: nenhum campo `pre_screen_*`, `adversarial_*`, `mandate_24_*` e artifacts/caveats legados preservados.
- `tests/myfxbook_pipeline/` continua sem novas falhas; as 3 falhas conhecidas em `test_macro_data_loader.py` sao externas ao escopo.
- `scripts/run_replicator_batch.py` continua funcional sem novos argumentos obrigatorios.

## Kill-Switches

- Se pre-screen falhar por falta de dados cacheados, marcar task `BLOCKED` sem workaround que viole allow-list.
- Se adversarial quebrar por synthetic vazio, registrar fields `null` + note; se o smoke 1407880 nao produzir synthetic numerico, task `FAILED/BLOCKED` conforme causa.
- Se backward-compat sem flags alterar schema legado, corrigir antes de marcar `DONE`.
- Nao otimizar thresholds, nao usar PnL futuro/oracle, nao tocar `frozen_rules/` ou `docs/investment-mandate.md`, nao fazer commit/push.
