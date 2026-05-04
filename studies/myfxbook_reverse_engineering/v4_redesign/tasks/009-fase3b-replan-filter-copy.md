# Task 009 — Replanejar Fase 3b filter-and-copy

**Phase:** 3b | **Effort:** 1 sessao | **Depends on:** 008

## Goal

Criar um contrato explicito para pivotar para filter-and-copy apos a Fase 1 STOP.
A Fase 2A/decode-self fica bloqueada porque `n_fase2_eligible_survivors=0`; os 21
`pre_screen_go_systems` sao usados apenas como universo audit-only para avaliar
copiabilidade externa.

## Contexto obrigatório

- Fase 1 report: `_diagnostics/PIPELINE_V4_FASE1_REPORT.md`.
- Batch: `iterations/007-fase1-batch-run/RESULTS.json`.
- Task 008: `iterations/008-fase1-document/SUMMARY.md`.

## Output principal

`studies/myfxbook_reverse_engineering/v4_redesign/FILTER_COPY_PLAN.md`

Conteudo obrigatorio:

1. **Escopo:** filter-and-copy e pesquisa diagnostica, nao reverse engineering e
   nao paper/live.
2. **Universo:** os 21 `pre_screen_go_systems`, marcados como audit-only.
3. **Gates de copiabilidade:** Real vs Demo warning/label, K1 sanity, MCPT/PSR,
   concentration, estabilidade mensal, drawdown recente, trade frequency,
   slippage/cost sensitivity e dependencia de martingale/grid.
4. **Ranking inicial:** especificar formula pre-registrada para `copyability_score`
   sem otimizar pesos apos resultado.
5. **Kill-switches:** se todos falham gates de copiabilidade, encerrar v4; se 1-3
   passam, gerar shortlist diagnostica; nunca promover para live sem nova decisao.
6. **Proximas tasks:** substituir/contornar 025-027 com uma sequencia pequena para
   scoring, report e eventual monitor diagnostico.

## Citacoes obrigatorias

- MCPT no track record: `[evidence_based_ta, p.325-328]`.
- PSR em serie unica de EA: `[advances_fin_ml, p.260-263]`.
- DSR/multiple testing se ranking gerar selecao entre sistemas: `[advances_fin_ml, p.273-275]`.
- Custos/slippage em estrategia curta/copied: `[systematic_trading, p.182-197]`.
- Overfitting/data-mining em selecao de sistemas: `[evidence_based_ta, p.247-260]`.

## Updates obrigatorios

- Criar `iterations/009-fase3b-replan-filter-copy/PRE_REG.md`.
- Criar `iterations/009-fase3b-replan-filter-copy/RESULTS.json`.
- Criar `iterations/009-fase3b-replan-filter-copy/SUMMARY.md`.
- Criar `iterations/009-fase3b-replan-filter-copy/run.log` com verificacoes.
- Atualizar `PROGRESS.md`.
- Atualizar `next_prompt.md` para a proxima task do pivot ou STOP.
- Atualizar `jornada/README.md` e criar entrada de jornada.

## Verificacao

```bash
test -f studies/myfxbook_reverse_engineering/v4_redesign/FILTER_COPY_PLAN.md
uv run python - <<'PY'
import json
from pathlib import Path
json.loads(Path('studies/myfxbook_reverse_engineering/v4_redesign/iterations/009-fase3b-replan-filter-copy/RESULTS.json').read_text())
PY
```

## Aceite

- [ ] `FILTER_COPY_PLAN.md` existe e contem as 6 secoes obrigatorias.
- [ ] Plano preserva sem paper/live e sem `frozen_rules/`.
- [ ] Universo inicial e exatamente os 21 `pre_screen_go_systems`.
- [ ] `copyability_score` e pre-registrado antes de qualquer ranking novo.
- [ ] `next_prompt.md` aponta para task de scoring ou STOP.

## Kill-switches

- Necessidade de AutoTrade real/API live para avaliar copiabilidade -> BLOCKED.
- Necessidade de alterar `frozen_rules/` ou `docs/investment-mandate.md` -> BLOCKED.
- Tentacao de relaxar Fase 1 thresholds para salvar decode-self -> FAILED.
