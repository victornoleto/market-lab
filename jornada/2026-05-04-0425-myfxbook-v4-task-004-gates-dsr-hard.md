# MyFxBook v4 task 004 — DSR e PBO viram hard gates no veredito agregado

**2026-05-04** — Task 004-gates-dsr-hard do redesign do pipeline myfxbook
refatorou `studies/myfxbook_reverse_engineering/shared/gates.py` para
formalizar o veredito agregado dos hard gates §2.4 do mandate. Antes da
task, `gates.py` ja calculava `dsr_p` e `gate2_pass` mas o "K4 verdict"
existente misturava Gate 2/3/4/6 em uma lista informacional sem PBO e sem
contrato programatico. Agora `GateStats` tem o metodo
`passes_mandate_24() -> tuple[bool, list[str]]` que retorna o veredito
unico e a lista de gates que falharam por nome.

## O que mudou

`passes_mandate_24()` avalia cinco hard gates:

| Gate | Threshold | Source |
|---|---|---|
| `sharpe_bootstrap_ci_low_999` | `> 0` | `[advances_fin_ml, p.196-211]` |
| `oos_bootstrap_ci_low_999` | `> 0` | idem |
| `dsr_p` | `< 0.05` | `[advances_fin_ml, p.273-275]` |
| `pbo` | `< 0.50` | `[advances_fin_ml, p.208-222]` |
| `wf_purged_positive` | `>= 6` quando aplicavel | `[testing_tuning, p.148-162]` |

CAGR e Max Drawdown viram campos warning-only em `GateStats`
(`[mandate §2.2/§2.3]`) — nunca aparecem em `failed_gate_names`. WF simples
de 8 blocks contiguos (`gate3_pass`) continua presente como diagnostico
informacional, mas NAO substitui o WF purgado que sera usado pos-task-006.

`compute_gates()` ganhou kwargs opcionais (`cpcv_result`, `wf_purged`,
`cagr`, `max_drawdown`) para receber insumos da Fase 2B (LightGBM mining +
WF purgado embargado). Sem estes insumos, `pbo` e `wf_purged_*` ficam
`None` e o gate fica opcional — coerente com Fase 1, onde o universo de N
candidate rules ainda nao foi gerado.

## Backward-compat preservada

Callsites existentes (`shared/_smoke_test.py`, `data/trades/<id>/_convert_
and_pipeline.py`) chamam `compute_gates(df, system_id)` sem kwargs novos e
continuam recebendo a mesma estrutura legada (`gate2_pass`, `gate3_pass`,
`gate4_pass`, `gate6_pass`, `n_wf_positive`, `full`, `oos`,
`walkforward`, `sharpe_optimistic`). Smoke test confirmado — Sharpe e DSR
batem com numeros pre-refactor.

`tests/test_grid_gates.py` (modulo distinto Plano A DORMANT em
`src/ai_trade/backtest/grid/gates.py`) inalterado e passando.

## Validacao com 14 testes unitarios

`tests/myfxbook_pipeline/test_gates_v4.py` cobre:
- DSR < 0.05 passa; DSR >= 0.05 falha com `dsr_p` em failed
- PBO < 0.50 passa; PBO >= 0.50 falha com `pbo` em failed
- Combinacao parcial (Sharpe ok + DSR fail -> fail total)
- CAGR / MDD altos NAO bloqueiam (warning-only)
- WF purgado None NAO bloqueia (opcional Fase 1)
- WF purgado < 6 falha
- OOS ausente bloqueia
- Sharpe bootstrap CI low <= 0 bloqueia
- `compute_gates()` backward-compat sem kwargs novos
- `compute_gates()` com `cpcv_result` popula `pbo`
- Assinatura `passes_mandate_24() -> (bool, list[str])` validada
- Constantes do modulo (`DSR_HARD_THRESHOLD`, `PBO_THRESHOLD`,
  `WF_PURGED_MIN_POSITIVE`) auditaveis

Baseline ampliado: 790 pass / 15 skip / 3 pre-existing fails (test_macro_
data_loader.py — heranca das tasks 001/002/003). Sem regressao.

## Por que isso importa

Antes desta task o "K4 verdict" do `gates.py` era informativo. O contrato
`passes_mandate_24() -> (bool, list[str])` permite que a Fase 1 batch run
(task 007) e o decision gate Fase 2->3 (task 019) consultem um veredito
booleano unico com lista programatica de gates falhos — sem precisar
parsear strings ou checar 4-5 campos individuais. PBO entra no fluxo
oficial: quando o LightGBM miner (task 015) gerar N candidate rules, basta
passar o `CPCVResult` para `compute_gates(..., cpcv_result=...)` e o PBO
vira gate ativo.

## Estado do redesign

- Fase 1 (semanas 1-2): 4 de 8 tasks DONE (001 skeleton, 002 pre-decode-
  screen, 003 cpcv-pbo, 004 gates-dsr-hard).
- Restam 4 tasks: 005 adversarial-validator (proxima sessao), 006 pipeline-
  wire-fase1, 007 fase1-batch-run, 008 fase1-document.
- Plano A continua DORMANT, frozen rules intocadas, capital 100% Plano C.
- Sem paper/live, sem commit/push.

Detalhe tecnico em
`studies/myfxbook_reverse_engineering/v4_redesign/iterations/004-gates-dsr-hard/SUMMARY.md`.
