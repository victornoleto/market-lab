# PRE_REG — Task 001: Skeleton Setup

**Criado ANTES de qualquer codigo.** Este e o contrato da task.

## Identificacao

- **Task ID:** 001-skeleton-setup
- **Fase:** 1
- **Sessao:** 2026-05-03
- **Citacao em TASKS.md:** "Criar arquivos vazios de modulos novos [...] com docstrings e citacoes; criar diretorios de testes. Sem logica ainda. Garantir baseline 461 testes ainda passa."
- **Spec detalhado:** `tasks/001-skeleton-setup.md`

## Escopo (minimo)

Criar arquivos de modulos Python vazios (apenas docstrings + TODO) e placeholders de testes (skipped).
**Nenhuma logica de negocio sera implementada nesta task.**

## Inputs esperados

- `studies/myfxbook_reverse_engineering/shared/` — diretorio ja existente com modulos v3
- `tests/` — diretorio de testes existente com baseline 461 testes

## Outputs esperados

### Modulos (12 arquivos)

| Arquivo | Citacao principal |
|---|---|
| `shared/pre_decode_screen.py` | `[evidence_based_ta, p.325-328]` (MCPT), `[advances_fin_ml, p.260-263]` (PSR) |
| `shared/cpcv.py` | `[advances_fin_ml, p.208-222]` |
| `shared/adversarial_validator.py` | `[advances_fin_ml, ch.5]` |
| `shared/news_calendar.py` | `[evidence_based_ta, ch.7]` |
| `shared/cross_asset_features.py` | `[volatility_trading, p.173-177]` |
| `shared/meta_labeler.py` | `[advances_fin_ml, p.84-89]` |
| `shared/lightgbm_miner.py` | `[advances_fin_ml, ch.5]` |
| `shared/transformer_encoder.py` | `[advances_fin_ml, ch.5, ch.7]` |
| `shared/hmm_regime_mixture.py` | `[machine_trading, ch.4]` |
| `shared/out_of_domain_transfer.py` | `[testing_tuning, p.148-162]` |
| `shared/signal_score_consolidated.py` | `[advances_fin_ml, p.196-211]` |
| `shared/forward_monitor.py` | `[advances_fin_ml, ch.14]` |

### Testes (8 arquivos)

- `tests/myfxbook_pipeline/__init__.py`
- `tests/myfxbook_pipeline/test_pre_decode_screen.py`
- `tests/myfxbook_pipeline/test_cpcv.py`
- `tests/myfxbook_pipeline/test_adversarial_validator.py`
- `tests/myfxbook_pipeline/test_news_calendar.py`
- `tests/myfxbook_pipeline/test_cross_asset_features.py`
- `tests/myfxbook_pipeline/test_meta_labeler.py`
- `tests/myfxbook_pipeline/test_lightgbm_miner.py`

### Diretorio de iteracao

- `iterations/001-skeleton-setup/` (este diretorio)
- `iterations/001-skeleton-setup/PRE_REG.md` (este arquivo)
- `iterations/001-skeleton-setup/run.log`
- `iterations/001-skeleton-setup/RESULTS.json`
- `iterations/001-skeleton-setup/SUMMARY.md`

## Criterios de aceite (verificaveis)

1. 12 arquivos `shared/*.py` criados — cada um com docstring contendo citacao correta
2. 8 arquivos `tests/myfxbook_pipeline/` criados — cada test_*.py com `@pytest.mark.skip`
3. `uv run pytest tests/ -x -q` continua passando com baseline 461+ (novos testes marcados skip)
4. Nenhum modulo v3 existente foi modificado

## Citacoes tecnicas

- CPCV/PBO: `[advances_fin_ml, p.208-222]` — combinatorial purged CV para medir overfit
- PSR (pre-screen): `[advances_fin_ml, p.260-263]` — probabilistic Sharpe ratio para track record unica
- MCPT: `[evidence_based_ta, p.325-328]` — Monte Carlo permutation test para estrategia
- Meta-labeling: `[advances_fin_ml, p.84-89]` — primary + secondary classifier
- LightGBM purged-CV: `[advances_fin_ml, ch.5]` — feature importance com purge+embargo
- HAR-RV regime: `[volatility_trading, p.173-177]` — realized vol bucketing
- HMM regime: `[machine_trading, ch.4]` — hidden Markov model para regime detection
- Out-of-domain WF: `[testing_tuning, p.148-162]` — walk-forward com purge+embargo
- Signal consolidation: `[advances_fin_ml, p.196-211]` — betting sizing e scoring
- Forward monitor: `[advances_fin_ml, ch.14]` — forward testing framework

## Kill-switches

- Qualquer quebra nos 461 testes baseline → reverter novos arquivos, marcar FAILED
- Nome de modulo duplicado em `shared/` → renomear antes de criar
- Import circular detectado → isolar em modulo separado antes de prosseguir
