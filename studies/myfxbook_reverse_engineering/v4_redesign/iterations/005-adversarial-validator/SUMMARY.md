# SUMMARY — Task 005: adversarial-validator

**Verdict:** ✅ DONE

## O que foi feito

Implementei `studies/myfxbook_reverse_engineering/shared/adversarial_validator.py`
com classificador binario LightGBM real-vs-synthetic. Interface congelada:

```python
@dataclass(frozen=True)
class AdversarialResult:
    auc: float                     # mean dos folds (out-of-fold)
    auc_ci_low_95: float           # bootstrap 1000x sobre AUCs dos folds
    auc_ci_high_95: float
    n_real: int
    n_synthetic: int
    n_features: int
    feature_importance: dict[str, float]   # top-10 LightGBM gain
    notes: list[str]                       # warnings nao-fatais

def adversarial_validate(real_trades, synthetic_trades, *, cv_folds=5, seed=20260503) -> AdversarialResult
```

Features trade-level Fase 1 (10): `hour_utc`, `dow`, `pair_idx`,
`direction_idx`, `lots`, `duration_sec`, `pips`, `mfe_pips`, `mae_pips`,
`entry_price_normalized` (normalizada por mediana de `open_price` por par no
pool real ∪ synthetic). Window-level entra na Fase 2A.

LightGBM hyperparams conservadores (anti-overfit em sample pequeno):
`num_leaves=31`, `n_estimators=200`, `learning_rate=0.05`,
`min_child_samples=10`, `bagging_fraction=0.9`, `bagging_freq=5`,
`feature_fraction=0.9`, `deterministic=True`, `force_row_wise=True`.

Adicionei `lightgbm>=4.0` ao extra `myfxbook_decoder` em `pyproject.toml` e
instalei via `uv pip install -e '.[myfxbook_decoder]'` (lightgbm 4.6.0).

5 sanity tests em `tests/myfxbook_pipeline/test_adversarial_validator.py`,
todos passam:

| # | Cenario | AUC esperado | AUC obtido | Pass? |
|---|---|---|---|---|
| 1 | `synthetic = real.copy()` | `[0.45, 0.55]` | 0.500 | ✅ |
| 2 | Synthetic com features i.i.d. | `> 0.85` | 1.000 | ✅ |
| 3 | `synthetic = real.sample(0.5)` | `[0.45, 0.55]` | 0.503 | ✅ |
| 4 | `synthetic = real`, `hour += 6` | `> 0.70` | 1.000 | ✅ |
| 5 | Determinismo (mesma entrada+seed) | `delta ≤ 0.01` | 0.000 | ✅ |

Test 4 confirma `hour_utc` como top-1 em feature_importance — modelo
identifica corretamente a feature separadora `[advances_fin_ml, ch.5]`.

## Citacoes usadas

- `[advances_fin_ml, ch.5]` — LightGBM + feature importance + adversarial
  AUC como metrica de identificabilidade.
- `[testing_tuning, ch.7]` — risco de overfitting em ML; capacity
  conservadora em sample pequeno.
- `[advances_fin_ml, p.196-211]` — bootstrap CI sobre AUCs dos folds.

## Caveats / decisoes nao-obvias

### Paired stratified group k-fold CV (substituiu StratifiedKFold)

**Problema descoberto durante implementacao:** com `synthetic = real.copy()`
byte-a-byte, `StratifiedKFold(shuffle=True, random_state=seed)` aplica
permutacoes INDEPENDENTES nas duas classes. Resultado: trade #i (label=0,
em real) e seu clone trade #i+200 (label=1, em synthetic) caem em folds
diferentes (um vai treino, outro validacao). LightGBM com features
ID-like (lots, pips, duration uniformemente distribuidos) memoriza
"esses 160 lots especificos sao label=0; aqueles 160 outros sao label=1"
e prediz INVERTIDO na validacao → AUC ≈ 0.027, nao 0.5.

**Diagnostico empirico:** com 200 hashes unicos no pool e StratifiedKFold,
treino tem ~80 hashes com so label=0 + ~80 hashes com so label=1 + ~80
hashes com ambos labels. Modelo aprende "X em S0 → 0; X em S1 → 1" e
extrapola na validacao prevendo label oposto ao verdadeiro
(porque val_class0 ⊂ S1 com alta prob).

**Solucao final apos validacao GPT-5.5:** `_paired_stratified_kfold_indices(X, y,
n_splits, seed)` agrupa rows por hash de feature row (NaN → sentinel) e passa
esses hashes como `groups` para `StratifiedGroupKFold`. Hashes identicos viajam
juntos para o mesmo fold, e os folds preservam balanceamento aproximado de
labels. Isso evita leakage sem abrir mao da estratificacao exigida para AUC.

- Quando `synth = real.copy()` (todos os hashes pareados): cada fold
  tem rows de ambas classes, modelo treina com balance per-X → predicao
  ≈ 0.5 → AUC ≈ 0.5.
- Quando synth tem features genuinamente diferentes (testes 2 e 4): cada
  hash e unico → comportamento se aproxima de StratifiedKFold randomizado
  seeded.

**Teste de regressao adicionado:**
`test_paired_stratified_splitter_keeps_duplicates_together_and_balanced` valida
que duplicatas exatas ficam juntas e que cada validation fold contem as duas
classes em balanceamento 1:1 no caso `synthetic = real.copy()`.

**Decisao registrada em DEAD_ENDS.md** ("StratifiedKFold em adversarial
com possivel overlap real/synth").

### LightGBM determinismo

`deterministic=True, force_row_wise=True` + `random_state=seed+fold_idx`
+ `feature_fraction=0.9, bagging_fraction=0.9, bagging_freq=5` → mesmo
input → mesmo output bit-a-bit (delta = 0.0 medido empiricamente, bem
abaixo da margem `±0.01` exigida pelo spec).

### Sample size guard

`LOW_SAMPLE_THRESHOLD = 60` (real + synthetic combinados). Abaixo disso,
emite warning em `notes` mas nao falha. CV reduz `n_splits` para
`min(cv_folds, min_class_count)` quando classe minoritaria e menor que
folds solicitados — registra reducao em `notes`.

### Bootstrap CI 95%

1000 reamostragens com reposicao sobre os AUCs dos folds, percentis 2.5/97.5.
Seed = `seed + 1` para nao colidir com seeds dos folds (`seed + fold_idx`).
`[advances_fin_ml, p.196-211]`.

## Run summary

- `pytest tests/myfxbook_pipeline/test_adversarial_validator.py -v`:
  6/6 passed apos correcao GPT-5.5.
- `pytest tests/`: 795 passed, 14 skipped, 3 failed (pre-existing) em 22.4s.
  Sem regressao (790 → 795 = +5 tests novos).
- 3 falhas pre-existentes em `tests/test_macro_data_loader.py` toleradas
  per task spec ("3 em test_macro_data_loader.py sao pre-existentes").
- LightGBM 4.6.0 instalado via `uv pip install -e '.[myfxbook_decoder]'`.

## Licao para a proxima task

A proxima task elegivel e **006-pipeline-wire-fase1** (depends:
002 ✓ + 003 ✓ + 004 ✓ + 005 ✓). Wire `pre_decode_screen` +
`adversarial_validator` + `passes_mandate_24` em `workbench/pipeline.py`
como flags `--enable-pre-screen --enable-adversarial`. Smoke test em
system 1407880. Garantir backward-compat (pipeline sem flags continua
rodando como antes).

Para 006, uso natural sera:

```python
from studies.myfxbook_reverse_engineering.shared.adversarial_validator import adversarial_validate

if args.enable_adversarial:
    adv = adversarial_validate(real_trades, synthetic_trades, seed=seed)
    summary["adversarial_auc"] = adv.auc
    summary["adversarial_ci"] = (adv.auc_ci_low_95, adv.auc_ci_high_95)
    summary["adversarial_top_features"] = list(adv.feature_importance.keys())[:5]
```

E aceitar gate decision-time (Fase 2 → 3): `adv.auc < 0.65` no
`019-decision-gate-fase2-fase3` (SPEC.md secao "Decision Gate Fase 2 → 3").
