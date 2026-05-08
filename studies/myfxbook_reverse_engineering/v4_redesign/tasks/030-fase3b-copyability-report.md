# Task 030 — Fase 3b copyability report

**Phase:** 3b | **Effort:** 1 sessao | **Depends on:** 029-fase3b-copyability-score

## Goal

Documentar o resultado da task 029 (`TOO_MANY_PASS_REQUIRES_REPORT_REVIEW`) sem
tomar decisao automatica de shortlist/monitor. O report deve explicar os 4 PASS,
o risco de selecionar top-N entre 21 EAs e as opcoes de governanca para o usuario.

## Inputs

- `_diagnostics/COPYABILITY_SCOREBOARD.json`
- `_diagnostics/COPYABILITY_SCOREBOARD.md`
- `v4_redesign/FILTER_COPY_PLAN.md`
- `iterations/029-fase3b-copyability-score/SUMMARY.md`
- `iterations/029-fase3b-copyability-score/RESULTS.json`

## Output principal

`studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_REVIEW.md`

Secoes obrigatorias:

1. **Verdict:** `TOO_MANY_PASS_REQUIRES_HUMAN_GOVERNANCE`.
2. **Resumo dos 4 PASS:** `system_id`, `copyability_score`, principais pontos fortes e caveats.
3. **Risco de selecao:** explicar multiple-testing/data-mining por escolher top-N entre 21.
4. **Concentracao e operacional:** simbolos dominantes, Real/Demo, frequencia, custo/slippage.
5. **Opcoes de governanca:** encerrar v4, criar desempate pre-registrado, ou monitor diagnostico read-only futuro.
6. **Guardrails:** sem paper/live, sem AutoTrade real, sem Plano A reativado, sem threshold change.

## Updates obrigatorios

- Criar `iterations/030-fase3b-copyability-report/PRE_REG.md`.
- Criar `iterations/030-fase3b-copyability-report/RESULTS.json`.
- Criar `iterations/030-fase3b-copyability-report/SUMMARY.md`.
- Criar `iterations/030-fase3b-copyability-report/run.log`.
- Atualizar `PROGRESS.md`.
- Atualizar `next_prompt.md` para STOP/decisao humana.
- Atualizar jornada.

## Citacoes obrigatorias

- MCPT no track record: `[evidence_based_ta, p.325-328]`.
- PSR em serie unica de EA: `[advances_fin_ml, p.260-263]`.
- DSR/multiple testing em selecao top-N: `[advances_fin_ml, p.273-275]`.
- Custos/slippage em copia de estrategia curta: `[systematic_trading, p.182-197]`.
- Data-mining na selecao de sistemas: `[evidence_based_ta, p.247-260]`.

## Verificacao

```bash
test -f studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_REVIEW.md
uv run python - <<'PY'
import json
from pathlib import Path
json.loads(Path('studies/myfxbook_reverse_engineering/v4_redesign/iterations/030-fase3b-copyability-report/RESULTS.json').read_text())
PY
```

## Aceite

- [ ] Report existe e contem as 6 secoes obrigatorias.
- [ ] Report nao escolhe top-3 automaticamente.
- [ ] Report nao inicia monitor/cron/paper/live/AutoTrade.
- [ ] `next_prompt.md` para em decisao humana.

## Kill-switches

- Tentativa de desempatar os 4 PASS sem nova regra pre-registrada -> FAILED.
- Tentativa de iniciar monitor/copy/paper/live -> FAILED.
