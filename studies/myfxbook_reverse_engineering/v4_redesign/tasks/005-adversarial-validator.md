# Task 005 — adversarial_validator.py

**Phase:** 1 | **Effort:** 2 sessoes | **Depends on:** 001

## Goal

Implementar classificador binario LightGBM real-vs-synthetic. AUC mede
identificabilidade do decode: AUC ~0.5 = synthetic indistinguivel de real
(decode bom); AUC > 0.65 = decode ruim (modelo de geracao errado).

## Interface

```python
# studies/myfxbook_reverse_engineering/shared/adversarial_validator.py

from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class AdversarialResult:
    auc: float
    auc_ci_low_95: float
    auc_ci_high_95: float
    n_real: int
    n_synthetic: int
    n_features: int
    feature_importance: dict[str, float]  # top-10 ordenado
    notes: list[str]

def adversarial_validate(
    real_trades: pd.DataFrame,
    synthetic_trades: pd.DataFrame,
    *,
    cv_folds: int = 5,
    seed: int = 20260503,
) -> AdversarialResult: ...
```

## Features compartilhadas (real e synthetic)

Calcular as mesmas features para ambos os conjuntos:
- Trade-level: `hour_utc`, `dow`, `pair_idx`, `direction_idx`, `lots`,
  `duration_sec`, `pips`, `mfe_pips`, `mae_pips`, `entry_price_normalized`
- Window-level (no momento da entrada): `rsi_14`, `bb_position_20`, `atr_norm_14`,
  `realized_vol_20bar`, `is_news_window`, `cross_asset_dxy_z`, etc.

Para Fase 1 (MVP), usar so trade-level. Window-level entra na Fase 2A apos features
ricas.

## Sanity tests

`tests/myfxbook_pipeline/test_adversarial_validator.py`:

1. **Copia exata:** `synthetic = real.copy()` → AUC ≈ 0.5 (esperado random
   guess). Margem: `0.45 < auc < 0.55`.
2. **Ruido puro:** `synthetic` aleatorio → AUC > 0.85 (separa facilmente).
3. **Sub-amostra:** `synthetic = real.sample(0.5)` → AUC ≈ 0.5 (mesma distrib).
4. **Shift de hour:** `synthetic = real` mas com `hour_utc` deslocado +6h →
   AUC > 0.7 (separa).
5. **Determinismo:** mesma entrada + seed produz mesmo AUC ±0.01.

## CV correto

Importante: usar `train_test_split` ou `cross_val_score` com `stratify=label`
(real=0, synthetic=1) para evitar imbalance bias. Reportar AUC media ±std nos
folds.

## Citacoes

- `[advances_fin_ml, ch.5]` — feature importance + clustered MDA
- `[testing_tuning, ch.7]` — overfitting risks em ML

## Files to modify

- `shared/adversarial_validator.py` (preenche skeleton)
- `tests/myfxbook_pipeline/test_adversarial_validator.py` (preenche skeleton)

## Verificacao

```bash
uv run pytest tests/myfxbook_pipeline/test_adversarial_validator.py -v
```

## Aceite

- [ ] `adversarial_validate()` implementado
- [ ] 5 sanity tests passam
- [ ] Determinismo: mesma seed produz mesmo AUC
- [ ] Top-10 feature_importance presente em output
- [ ] Citacoes em docstring

## Dependencia LightGBM (decidida no SPEC.md, nao mid-loop)

LightGBM entra no extra `myfxbook_decoder` em `pyproject.toml` (junto com
`dukascopy-python>=4.0` e `wittgenstein>=0.3` ja existentes). Adicao:

```toml
myfxbook_decoder = [
    "dukascopy-python>=4.0",
    "wittgenstein>=0.3",
    "lightgbm>=4.0",        # NOVO — task 005, 015 (LightGBM miner)
]
```

Comando para instalar:
```bash
uv pip install -e '.[myfxbook_decoder]'
```

Esta task **deve** atualizar `pyproject.toml` adicionando a linha. Documentar
no SUMMARY.md da iteracao 005.

`sklearn.metrics.roc_auc_score` e `sklearn.model_selection.cross_val_score`
ja sao cobertos por `scikit-learn>=1.4` no core dependencies (verificado).

## Kill-switches

- AUC > 0.55 em test 1 (copia exata) → bug, fix antes de DONE.
- LightGBM import error apos `uv pip install -e '.[myfxbook_decoder]'` →
  versao incompativel; pinar `lightgbm>=4.0,<5.0` se necessario.
