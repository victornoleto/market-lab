# Task 004 — gates.py refactor (DSR hard, PBO entry)

**Phase:** 1 | **Effort:** 1-2 sessoes | **Depends on:** 003

## Goal

Promover DSR de informativo para hard gate em `shared/gates.py`. Adicionar PBO
via `cpcv.py` (task 003) como gate. Manter CAGR/MDD warning-only conforme
mandate §2.2/§2.3. Atualizar testes existentes.

## Mudancas em gates.py

### Antes (estado atual)
- `dsr_p` reportado em GateStats (informativo, nao bloqueia)
- `walk_forward_positive` simples (8 splits contiguos sem purge)
- Sem PBO

### Depois
- `dsr_p < 0.05` → hard gate, bloqueia se falhar
- `pbo < 0.50` → hard gate via `cscv_pbo()` de task 003
- `walk_forward_positive` → renomeado `wf_simple_positive`, mantido informativo
- Novo `wf_purged_positive` opcional para sessoes que tiverem dados embargados
- Pass/fail compostos em `GateStats.passes_mandate_24()` retornando bool

## Interface

```python
@dataclass(frozen=True)
class GateStats:
    sharpe: float
    sharpe_bootstrap_ci_low_999: float | None
    oos_sharpe: float
    oos_bootstrap_ci_low_999: float | None
    dsr_p: float | None  # NOVO: bloqueante se < 0.05
    pbo: float | None  # NOVO: bloqueante se < 0.50
    wf_simple_positive: int
    wf_simple_total: int
    cagr: float | None  # warning-only tier
    max_drawdown: float | None  # warning-only tier
    
    def passes_mandate_24(self) -> tuple[bool, list[str]]:
        """Retorna (passes_all, list_of_failed_gate_names)."""
        ...
```

## Hard gates §2.4 (apos refactor)

| Gate | Threshold | Source |
|---|---|---|
| Sharpe bootstrap CI 99.9% low | > 0 | `[advances_fin_ml, p.196-211]` |
| OOS bootstrap CI 99.9% low | > 0 | mesmo |
| DSR p | < 0.05 | `[advances_fin_ml, p.273-275]` |
| PBO | < 0.50 | `[advances_fin_ml, p.208-222]` |
| WF purgado | ≥ 6/8 (quando aplicavel) | `[testing_tuning, p.148-162]` |

## Warning-only tiers (mandate §2.2/§2.3)

CAGR e Max Drawdown ficam em `GateStats` apenas para reporting. Tabela de tiers
fica em `docs/investment-mandate.md` §2.

## Testes a atualizar

- `tests/test_gates.py` (existente) — atualizar para validar:
  - DSR p < 0.05 → passes
  - DSR p >= 0.05 → fails com `dsr_p` em failed_gate_names
  - PBO < 0.50 → passes
  - PBO >= 0.50 → fails
  - Combinacoes parciais (Sharpe ok mas DSR fail → fails total)
- Adicionar `tests/myfxbook_pipeline/test_gates_v4.py` com cenarios novos.

## Files to modify

- `shared/gates.py` — refactor existente
- `tests/test_gates.py` — atualizar testes
- `tests/myfxbook_pipeline/test_gates_v4.py` — testes novos

## Verificacao

```bash
# Testes especificos
uv run pytest tests/test_gates.py tests/myfxbook_pipeline/test_gates_v4.py -v

# Baseline 461 nao quebra
uv run pytest tests/ -q
```

## Aceite

- [ ] `GateStats.passes_mandate_24()` implementado
- [ ] DSR p<0.05 bloqueia
- [ ] PBO<0.50 bloqueia
- [ ] CAGR/MDD warning-only preservados
- [ ] Testes atualizados passam
- [ ] Baseline 461 testes preservado

## Kill-switches

- Quebra em testes existentes que dependem do nome `walk_forward_positive` →
  manter nome legado como property apontando para `wf_simple_positive`
- Tests do projeto inteiro passam de 461 → numero menor → regressao, fix antes
  de marcar DONE
