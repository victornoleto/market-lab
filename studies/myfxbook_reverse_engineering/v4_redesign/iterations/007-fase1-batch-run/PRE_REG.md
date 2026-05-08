# PRE_REG — 007-fase1-batch-run

## ID e Nome

- Task: `007-fase1-batch-run`
- Nome: Fase 1 batch run nos systems disponiveis
- Inicio pre-registrado UTC: `2026-05-04T10:20:47Z`

## Fonte da Task

- `TASKS.md`: `007-fase1-batch-run`, Phase 1, depends_on `[006]`, goal de rodar batch com flags Fase 1 em 30 R1 v3 + 22 NOT_DECODED e gerar tabela de sobreviventes.
- `tasks/007-fase1-batch-run.md`: comando via `run_replicator_batch`, flags `--enable-pre-screen --enable-adversarial`, summary `batch_summary_fase1.json`, aceite com pre-screen por system e survivors `N<=10`.

## Escopo Minimo

- Rodar a Fase 1 em batch nos system IDs numericos disponiveis em `studies/myfxbook_reverse_engineering/systems/` usando `--enable-pre-screen` e `--enable-adversarial`.
- Preservar o contrato da task: sem alterar thresholds depois de ver resultado, sem paper/live, sem tocar `frozen_rules/`, `docs/investment-mandate.md`, `data/trades/`, `data/ohlc/`, `data/tiingo/` ou outras hunts.
- Consolidar uma tabela parseavel de sobreviventes com `pre_screen_decision`, metricas do pre-screen, adversarial AUC e `mandate_24` quando o pipeline conseguir gerar synthetic.
- Se algum system nao puder rodar por ausencia de cache/Stage 1, registrar explicitamente em `run.log`, `RESULTS.json` e `SUMMARY.md`; nao inventar dados e nao fazer cherry-pick.

## Inputs Esperados

- `studies/myfxbook_reverse_engineering/systems/<id>/` para system IDs numericos disponiveis.
- `studies/myfxbook_reverse_engineering/scripts/run_replicator_batch.py`.
- `studies/myfxbook_reverse_engineering/workbench/pipeline.py` com flags da task 006.
- Modulos Fase 1 ja implementados: `shared/pre_decode_screen.py`, `shared/adversarial_validator.py`, `shared/gates.py`, `shared/cpcv.py`.

## Outputs Esperados

- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/007-fase1-batch-run/PRE_REG.md`.
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/007-fase1-batch-run/run.log`.
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/007-fase1-batch-run/RESULTS.json`.
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/007-fase1-batch-run/SUMMARY.md`.
- `studies/myfxbook_reverse_engineering/_diagnostics/batch_summary_fase1.json`.
- Se o batch usar output por system: `studies/myfxbook_reverse_engineering/systems/<id>/decoding_v4_fase1/pipeline_summary.json` quando Stage 1/backtest permitirem.
- `PROGRESS.md` atualizado para `007`.
- `next_prompt.md` reescrito para `008-fase1-document` se 007 passar.

## Citacoes de Livro

- MCPT no pre-screen da track record do EA: `[evidence_based_ta, p.325-328]`.
- Validador adversarial real-vs-synthetic via classificador e feature importance: `[advances_fin_ml, ch.5]`.
- DSR hard gate no `mandate_24`: `[advances_fin_ml, p.273-275]`.
- PBO/CSCV ausente ou opcional nesta fase, documentado sem otimizar apos resultado: `[advances_fin_ml, p.208-222]`.

## Criterio de Aceite

- `batch_summary_fase1.json` existe e e JSON parseavel.
- `RESULTS.json` existe, e JSON parseavel, e lista systems tentados, systems completados, failures/blockers e survivors.
- Survivors sao definidos antes do resultado como systems com `pre_screen_decision == "GO"`; quando disponivel, a tabela tambem mostra `adversarial_auc` e `mandate_24_pass`.
- Se `n_survivors <= 10`, a task pode ser `DONE`; se `n_survivors > 10`, registrar como falha de calibragem conforme kill-switch.
- `run.log` contem os comandos de verificacao e a saida suficiente para auditoria.

## Kill-switches

- Batch exceder 4h de wall-clock: parar limpo e marcar `BLOCKED` ou dividir em lote menor apenas se ainda respeitar uma task por sessao.
- Pre-screen falhar em todos os systems: investigar bug provavel antes de marcar `DONE`.
- Pre-screen passar em 30+ systems: marcar `FAILED` por thresholds frouxos demais, sem recalibrar na sessao.
- Necessidade de modificar paths proibidos: marcar `BLOCKED` e pedir intervencao humana.
