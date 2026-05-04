# Task 001 — Skeleton Setup

**Phase:** 1 | **Effort:** 1 sessao | **Depends on:** -

## Goal

Criar arquivos vazios dos modulos novos previstos no SPEC.md, com docstrings
contendo intencao + citacoes + interface esperada (sem logica). Garantir que
baseline 461 testes ainda passa ao final.

## Files to create (vazios + docstring)

```
studies/myfxbook_reverse_engineering/shared/pre_decode_screen.py
studies/myfxbook_reverse_engineering/shared/cpcv.py
studies/myfxbook_reverse_engineering/shared/adversarial_validator.py
studies/myfxbook_reverse_engineering/shared/news_calendar.py
studies/myfxbook_reverse_engineering/shared/cross_asset_features.py
studies/myfxbook_reverse_engineering/shared/meta_labeler.py
studies/myfxbook_reverse_engineering/shared/lightgbm_miner.py
studies/myfxbook_reverse_engineering/shared/transformer_encoder.py
studies/myfxbook_reverse_engineering/shared/hmm_regime_mixture.py
studies/myfxbook_reverse_engineering/shared/out_of_domain_transfer.py
studies/myfxbook_reverse_engineering/shared/signal_score_consolidated.py
studies/myfxbook_reverse_engineering/shared/forward_monitor.py

tests/myfxbook_pipeline/__init__.py  (apenas se nao existir)
tests/myfxbook_pipeline/test_pre_decode_screen.py
tests/myfxbook_pipeline/test_cpcv.py
tests/myfxbook_pipeline/test_adversarial_validator.py
tests/myfxbook_pipeline/test_news_calendar.py
tests/myfxbook_pipeline/test_cross_asset_features.py
tests/myfxbook_pipeline/test_meta_labeler.py
tests/myfxbook_pipeline/test_lightgbm_miner.py
```

## Conteudo de cada arquivo `shared/<modulo>.py`

```python
"""<title> — Pipeline v4 Redesign module.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: <NNN-slug> em studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md

Citations:
- <book.slug, p.X> — <razao>
"""
from __future__ import annotations

# TODO(NNN-slug): implementar conforme tasks/NNN-slug.md
```

## Conteudo de cada arquivo `tests/myfxbook_pipeline/test_*.py`

```python
"""Tests for shared.<modulo>. Detalhado quando o modulo for implementado."""
import pytest


@pytest.mark.skip(reason="Pending implementation in v4 task NNN-slug")
def test_placeholder():
    pass
```

## Verificacao

```bash
uv run pytest tests/ -x --collect-only | tail -30
uv run pytest tests/ -x -q 2>&1 | tail -10
```

Esperado:
- Coleta inclui novos test_*.py com testes skipped
- Baseline 461 testes ainda passa (461 passed, ou 461 passed + N skipped)

## Aceite

- [ ] 12 arquivos `shared/<modulo>.py` criados com docstrings + TODO
- [ ] 7+ arquivos `tests/myfxbook_pipeline/test_*.py` com placeholder skip
- [ ] `pytest tests/ -x` continua passando (baseline preservado)
- [ ] `iterations/001-skeleton-setup/RESULTS.json` registra files_created
- [ ] `next_prompt.md` aponta para task 002

## Citacoes obrigatorias

Os docstrings dos modulos devem citar pelo menos a referencia da intencao:

- `pre_decode_screen.py` → `[evidence_based_ta, p.325-328]` (MCPT), `[advances_fin_ml, p.260-263]` (PSR — NAO p.273-275 que e DSR)
- `cpcv.py` → `[advances_fin_ml, p.208-222]`
- `adversarial_validator.py` → `[advances_fin_ml, ch.5]`
- `meta_labeler.py` → `[advances_fin_ml, p.84-89]`
- `lightgbm_miner.py` → `[advances_fin_ml, ch.5]`
- `transformer_encoder.py` → `[advances_fin_ml, ch.5, ch.7]`
- `hmm_regime_mixture.py` → `[machine_trading, ch.4]`
- `news_calendar.py` → `[evidence_based_ta, ch.7]` (news effects)
- `cross_asset_features.py` → `[volatility_trading, p.173-177]`
- `out_of_domain_transfer.py` → `[testing_tuning, p.148-162]`
- `signal_score_consolidated.py` → `[advances_fin_ml, p.196-211]`
- `forward_monitor.py` → `[advances_fin_ml, ch.14]` (forward testing)

## Kill-switches

- Quebra do baseline 461 testes → reverter, marcar FAILED
- Module com nome duplicado em `shared/` → renomear conforme TASKS.md
