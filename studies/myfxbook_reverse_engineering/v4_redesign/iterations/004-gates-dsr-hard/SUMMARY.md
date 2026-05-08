# SUMMARY — Task 004: gates-dsr-hard

**Verdict:** ✅ DONE

## O que foi feito

Refatorei `studies/myfxbook_reverse_engineering/shared/gates.py` para ancorar o
contrato `passes_mandate_24() -> tuple[bool, list[str]]` em `GateStats` e
absorver os 5 hard gates do mandate §2.4:

| Gate | Threshold | Source |
|---|---|---|
| `sharpe_bootstrap_ci_low_999 > 0` | full sample | `[advances_fin_ml, p.196-211]` |
| `oos_bootstrap_ci_low_999 > 0` | OOS block | `[advances_fin_ml, p.196-211]` |
| `dsr_p < 0.05` (hard) | full | `[advances_fin_ml, p.273-275]` |
| `pbo < 0.50` | candidato matrix | `[advances_fin_ml, p.208-222]` |
| `wf_purged_n_positive >= 6` | quando aplicavel | `[testing_tuning, p.148-162]` |

CAGR e Max Drawdown viram **campos warning-only** em `GateStats`
(`[mandate §2.2/§2.3]`) — nunca aparecem em `failed_gate_names`.

`compute_gates()` ganhou kwargs opcionais (`cpcv_result`, `wf_purged`, `cagr`,
`max_drawdown`) para receber insumos da Fase 2B (LightGBM mining + WF purgado
embargado). Default `None` = sem mining ainda; gate "PBO" e "WF purgado" ficam
opcionais e nao bloqueiam quando ausentes — coerente com Fase 1 onde o
universo N de candidate rules ainda nao foi gerado.

Backward-compat: callsites existentes (`shared/_smoke_test.py`,
`data/trades/11504701/_convert_and_pipeline.py`) chamam
`compute_gates(df, system_id)` sem kwargs novos e continuam recebendo a
mesma estrutura `GateStats` com os campos legados (`gate2_pass`,
`gate3_pass`, `gate4_pass`, `gate6_pass`, `n_wf_positive`, `full`, `oos`,
`walkforward`, `sharpe_optimistic`).

`format_gates_report()` foi estendido para imprimir as secoes "PBO — CSCV",
"WF purgado", "Tiers warning-only" e o veredito agregado de
`passes_mandate_24()` (apenas quando os campos relevantes estao populados).

Adicionei 14 testes unitarios em `tests/myfxbook_pipeline/test_gates_v4.py`
cobrindo:
1. DSR < 0.05 → passes
2. DSR >= 0.05 → falha com `dsr_p` em failed
3. PBO < 0.50 → passes
4. PBO >= 0.50 → falha com `pbo` em failed
5. Combinacao parcial (Sharpe ok + DSR fail → fail total)
6. CAGR / MDD altos NAO bloqueiam (warning-only)
7. WF purgado None NAO bloqueia (opcional)
8. WF purgado < 6 → falha
9. OOS ausente → falha
10. Sharpe bootstrap CI low <= 0 → falha
11. `compute_gates()` backward-compat sem kwargs novos
12. `compute_gates()` com `cpcv_result` popula `pbo`
13. Assinatura `passes_mandate_24() -> (bool, list[str])` validada
14. Constantes do modulo (`DSR_HARD_THRESHOLD`, `PBO_THRESHOLD`,
    `WF_PURGED_MIN_POSITIVE`) auditaveis

## Citacoes usadas

- `[advances_fin_ml, p.273-275]` — DSR hard gate (Bailey & Lopez 2014).
- `[advances_fin_ml, p.196-211]` — Sharpe bootstrap CI 99.9% gate.
- `[advances_fin_ml, p.208-222]` — PBO via CSCV.
- `[testing_tuning, p.148-162]` — WF purgado >= 6/8.
- `docs/investment-mandate.md §2.2/§2.3` — CAGR/MDD warning-only.
- `DEAD_ENDS.md` — PBO complementa WF (nao substitui).

## Caveats / decisoes nao-obvias

- **`tests/test_gates.py` nao existe** no repo — referencia incorreta no spec
  e no `next_prompt.md`. O unico arquivo `test_grid_gates.py` (`src/market_lab/
  backtest/grid/gates.py`) e modulo distinto do Plano A DORMANT e continua
  passando sem mudanca. Optei por criar somente `tests/myfxbook_pipeline/
  test_gates_v4.py` — mesmo padrao de outras tasks v4 (`test_cpcv.py`,
  `test_pre_decode_screen.py`).
- **PBO opcional em `passes_mandate_24()`**: `pbo=None` nao bloqueia. Razao:
  Fase 1 ainda nao gerou universo de candidate rules; PBO so faz sentido
  apos LightGBM mining (Fase 2B, task 015). Forcar bloqueio aqui criaria
  falsos negativos em todos os EAs antes do mining. Spec da task explicita
  "(quando aplicavel)" para WF purgado; aplico mesma logica para PBO. `pbo`
  fornecido com valor numerico continua bloqueando (>=0.50).
- **DSR hard sem `pbo` no caminho legado**: o campo `gate2_pass` ja era
  `dsr_p < 0.05` no codigo pre-task-004. A "promocao" e semantica:
  agora `passes_mandate_24()` agrega DSR como bloqueio formal junto com os
  demais §2.4 gates. Comportamento legado preservado.
- **CAGR / MDD são `Optional[float]`** em `GateStats`. Tiers warning-only
  exibidos no report quando fornecidos pelo caller; nunca afetam
  `passes_mandate_24()`. Manter em `GateStats` em vez de criar dataclass
  separado simplifica contrato downstream (Fase 2B, decision gate).
- Backward-compat preservada: `_make_stats(...)` em testes e
  `compute_gates(...)` chamadas sem kwargs novos retornam estrutura
  identica a antes (campos novos = `None`).

## Licao para a proxima task

A proxima task elegivel e **006-pipeline-wire-fase1** (depends:
002 ✓ + 003 ✓ + 004 ✓ + 005 PENDING). Como 005 (`adversarial-validator`)
ainda esta PENDING e nao tem dependencia em 003/004, podera ser executada em
paralelo ou em sessao subsequente. 006 espera ambas DONE.

Ordem recomendada para o loop:
- Sessao seguinte: **005-adversarial-validator** (dispara 006).
- Depois: **006-pipeline-wire-fase1** (wire `pre_decode_screen` +
  `adversarial_validator` + `passes_mandate_24` em `workbench/pipeline.py`).

Para 006 wire, o uso natural do gate sera:
```python
stats = compute_gates(trades, sid, cpcv_result=cpcv, wf_purged=(wf_pos, 8))
mandate_pass, failed = stats.passes_mandate_24()
```

## Run summary

- `pytest tests/myfxbook_pipeline/test_gates_v4.py`: 14/14 passed em 0.87s.
- `pytest tests/`: 790 passed, 15 skipped, 3 failed (pre-existing) em 17.4s.
  Sem regressao.
- `tests/test_grid_gates.py` (modulo distinto Plano A DORMANT) inalterado:
  passa.
- Smoke import `gates.compute_gates(df, sid)` produz `GateStats` com
  legado-compativel + `passes_mandate_24()` retornando `(bool, list[str])`.
