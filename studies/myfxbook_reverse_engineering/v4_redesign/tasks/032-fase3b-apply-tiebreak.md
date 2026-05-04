# Task 032 — Fase 3b apply tiebreak

**Phase:** 3b | **Effort:** 1 sessao | **Depends on:** 031-fase3b-tiebreak-pre-reg

## Goal

Aplicar exatamente a regra lexicografica pre-registrada em `TIEBREAK_PLAN.md` aos
4 sistemas PASS (`8577442`, `1152318`, `10067081`, `10062918`). Esta task so
produz uma ordem diagnostica e shortlist de ate 3; nao inicia monitor, paper/live,
AutoTrade real ou qualquer acao operacional.

## Inputs

- `v4_redesign/TIEBREAK_PLAN.md`
- `_diagnostics/COPYABILITY_SCOREBOARD.json`
- `_diagnostics/COPYABILITY_REVIEW.md`

## Output principal

- `studies/myfxbook_reverse_engineering/_diagnostics/TIEBREAK_RESULT.json`
- `studies/myfxbook_reverse_engineering/_diagnostics/TIEBREAK_RESULT.md`

Campos obrigatorios:

- `universe`: exatamente os 4 IDs travados.
- `ordered_systems`: lista completa ordenada pela chave do plano.
- `diagnostic_shortlist`: primeiros 3 sistemas, se a regra aplicar sem BLOCKED.
- `tiebreak_key`: campos calculados por system.
- `status`: `DONE` ou `BLOCKED`.
- `notes`: guardrails e proibicoes operacionais.

## Regras

- Nao alterar `TIEBREAK_PLAN.md`.
- Nao buscar novos dados, novos trades, broker/API ou AutoTrade.
- Nao alterar gates/pesos/thresholds de task 029.
- Se qualquer campo exigido estiver ausente/nulo/invalido, marcar `BLOCKED`.
- Shortlist e diagnostica; nao e recomendacao operacional.

## Citacoes obrigatorias

- Multiple-testing/DSR: `[advances_fin_ml, p.273-275]`.
- Data-mining: `[evidence_based_ta, p.247-260]`.
- Custos/slippage: `[systematic_trading, p.182-197]`.
- MCPT/PSR como evidencia limitada: `[evidence_based_ta, p.325-328]` `[advances_fin_ml, p.260-263]`.

## Verificacao

```bash
uv run python - <<'PY'
import json
from pathlib import Path
p = Path('studies/myfxbook_reverse_engineering/_diagnostics/TIEBREAK_RESULT.json')
d = json.loads(p.read_text())
assert d['universe'] == ['8577442', '1152318', '10067081', '10062918']
assert len(d['ordered_systems']) == 4
assert len(d['diagnostic_shortlist']) <= 3
print(d['status'], d['diagnostic_shortlist'])
PY
```

## Aceite

- [ ] JSON parseavel com os 4 IDs e ordem completa.
- [ ] MD explica a ordem e caveats.
- [ ] Shortlist tem ate 3 sistemas.
- [ ] Sem monitor/cron/paper/live/AutoTrade.
- [ ] `next_prompt.md` para em decisao humana.

## Kill-switches

- Universo diferente dos 4 IDs -> BLOCKED.
- Campo essencial ausente/nulo/invalido -> BLOCKED.
- Tentativa de mudar regra ou thresholds -> FAILED.
- Tentativa de iniciar monitor ou operacionalizar -> FAILED.
