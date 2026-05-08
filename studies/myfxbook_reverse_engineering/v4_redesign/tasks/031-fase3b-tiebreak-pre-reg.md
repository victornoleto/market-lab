# Task 031 — Fase 3b tiebreak pre-reg

**Phase:** 3b | **Effort:** 1 sessao | **Depends on:** 030-fase3b-copyability-report

## Goal

Pre-registrar uma regra de desempate para os 4 sistemas `PASS` da task 029 antes
de aplica-la. Esta task nao executa desempate, nao escolhe top-3, nao inicia
monitor e nao altera thresholds/pesos da task 029.

## Inputs

- `_diagnostics/COPYABILITY_REVIEW.md`
- `_diagnostics/COPYABILITY_SCOREBOARD.json`
- `v4_redesign/FILTER_COPY_PLAN.md`
- `iterations/030-fase3b-copyability-report/SUMMARY.md`

## Output principal

`studies/myfxbook_reverse_engineering/v4_redesign/TIEBREAK_PLAN.md`

Secoes obrigatorias:

1. **Escopo:** desempate diagnostico, nao deploy.
2. **Universo travado:** exatamente os 4 PASS (`8577442`, `1152318`, `10067081`, `10062918`).
3. **Regra de desempate:** criterios em ordem lexicografica ou score secundario,
   usando apenas campos ja existentes no scoreboard/review.
4. **Justificativa:** reduzir data-mining/multiple-testing sem olhar novo resultado.
5. **Kill-switches:** se regra depender de dado novo, PnL futuro, broker/API,
   AutoTrade, ou threshold change, marcar BLOCKED/FAILED.
6. **Proxima task:** aplicar o desempate em uma task separada, se autorizado.

## Restricoes

- Nao aplicar o desempate nesta task.
- Nao escolher top-3 automaticamente.
- Nao alterar gates/pesos de `FILTER_COPY_PLAN.md` ou task 029.
- Nao iniciar monitor/cron, paper/live, AutoTrade real ou broker integration.
- Nao tratar qualquer PASS como recomendacao operacional.

## Citacoes obrigatorias

- Multiple testing / DSR em selecao top-N: `[advances_fin_ml, p.273-275]`.
- Data-mining em selecao de sistemas: `[evidence_based_ta, p.247-260]`.
- Custos/slippage para desempate operacional: `[systematic_trading, p.182-197]`.
- MCPT/PSR como evidencia limitada de track record: `[evidence_based_ta, p.325-328]` `[advances_fin_ml, p.260-263]`.

## Verificacao

```bash
test -f studies/myfxbook_reverse_engineering/v4_redesign/TIEBREAK_PLAN.md
uv run python - <<'PY'
import json
from pathlib import Path
json.loads(Path('studies/myfxbook_reverse_engineering/v4_redesign/iterations/031-fase3b-tiebreak-pre-reg/RESULTS.json').read_text())
PY
```

## Aceite

- [ ] `TIEBREAK_PLAN.md` existe e contem as 6 secoes obrigatorias.
- [ ] Plano nao aplica desempate nem escolhe top-3.
- [ ] Plano preserva sem paper/live, sem AutoTrade real e sem monitor.
- [ ] `next_prompt.md` aponta para task futura de aplicacao ou STOP.

## Kill-switches

- Regra proposta requer dado novo nao pre-registrado -> BLOCKED.
- Regra muda thresholds/pesos da task 029 -> FAILED.
- Regra tenta promover operacionalmente qualquer EA -> FAILED.
