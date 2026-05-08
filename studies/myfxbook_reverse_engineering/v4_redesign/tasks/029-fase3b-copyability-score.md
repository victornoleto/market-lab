# Task 029 — Fase 3b copyability score

**Phase:** 3b | **Effort:** 1-2 sessoes | **Depends on:** 009-fase3b-replan-filter-copy

## Goal

Implementar scoring offline dos 21 `pre_screen_go_systems` usando exatamente o
contrato pre-registrado em `FILTER_COPY_PLAN.md`. Esta task avalia copiabilidade
diagnostica, nao reverse engineering, nao paper/live e nao AutoTrade real.

## Inputs

- `studies/myfxbook_reverse_engineering/v4_redesign/FILTER_COPY_PLAN.md`.
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/007-fase1-batch-run/RESULTS.json`.
- `studies/myfxbook_reverse_engineering/_diagnostics/batch_summary_fase1.json`.
- `studies/myfxbook_reverse_engineering/systems/<id>/decoding_v4_fase1/pre_decode_screen.json` quando existir.
- `studies/myfxbook_reverse_engineering/data/trades/<id>/trades.parquet` ou cache legado ja usado pelo batch.

## Output principal

- `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_SCOREBOARD.json`
- `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_SCOREBOARD.md`

Campos obrigatorios por system:

- `system_id`
- `copyability_status`: `PASS` ou `STOP`
- `failed_copyability_gates`
- `copyability_score`: numero apenas para `PASS`, `null` para `STOP`
- componentes do score definidos em `FILTER_COPY_PLAN.md`
- `ranking_selection_warning`

## Regras de implementacao

- Usar exatamente os 21 IDs travados no plano.
- Aplicar primeiro os gates bloqueantes do plano.
- Calcular `copyability_score` somente para quem passar todos os gates.
- Nao alterar pesos/thresholds apos observar resultados.
- Nao tocar `frozen_rules/`, `docs/investment-mandate.md` ou dados congelados.

## Citacoes obrigatorias

- MCPT no track record: `[evidence_based_ta, p.325-328]`.
- PSR em serie unica de EA: `[advances_fin_ml, p.260-263]`.
- DSR/multiple testing em selecao top-N: `[advances_fin_ml, p.273-275]`.
- Custos/slippage em copia de estrategia curta: `[systematic_trading, p.182-197]`.
- Data-mining na selecao de sistemas: `[evidence_based_ta, p.247-260]`.

## Verificacao

```bash
uv run python - <<'PY'
import json
from pathlib import Path
p = Path('studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_SCOREBOARD.json')
d = json.loads(p.read_text())
assert len(d['systems']) == 21
print(d['summary'])
PY
```

## Aceite

- [ ] Scoreboard JSON parseavel com 21 systems.
- [ ] Scoreboard MD com tabela e conclusao.
- [ ] Nenhum sistema fora dos 21 IDs audit-only foi avaliado.
- [ ] `copyability_score` so existe para `PASS`.
- [ ] Se todos STOP, `next_prompt.md` aponta report/encerramento, nao relaxa thresholds.
- [ ] Se 1-3 PASS, `next_prompt.md` aponta task de report diagnostico, sem paper/live.

## Kill-switches

- Todos falham gates de copiabilidade -> registrar STOP limpo, nao relaxar.
- Alguma metrica exigir credencial, AutoTrade real ou ordem -> BLOCKED.
- Necessidade de alterar paths proibidos -> BLOCKED.
