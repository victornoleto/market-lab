# PRE_REG — Task 005: adversarial-validator

**Criado ANTES de codar logica.** Contrato congelado da task.

## Identificacao

- **Task ID:** 005-adversarial-validator
- **Fase:** 1
- **Sessao:** 2026-05-04
- **Citacao em TASKS.md:**
  > "`shared/adversarial_validator.py` — LightGBM binario real-vs-synthetic
  > classifier, AUC como metrica de identificabilidade. Sanity tests: copia
  > exata → AUC≈0.5; ruido puro → AUC>0.9. `[advances_fin_ml, ch.5]` para
  > feature importance."
- **Spec detalhado:** `tasks/005-adversarial-validator.md`
- **Depende de:** task 001 DONE (skeleton + extra `myfxbook_decoder` no
  `pyproject.toml`).

## Escopo (minimo)

1. Adicionar `lightgbm>=4.0` ao extra `myfxbook_decoder` em `pyproject.toml`
   e atualizar `uv.lock` via `uv add --optional myfxbook_decoder lightgbm` ou
   comando equivalente. Decisao pre-registrada no SPEC.md secao "Decisoes
   travadas apos review GPT-5.5". `uv.lock` e permitido porque `uv` sincroniza
   o lockfile com `pyproject.toml`.
2. Implementar `shared/adversarial_validator.py` com:
   - `AdversarialResult` dataclass frozen (campos do spec).
   - Funcao publica `adversarial_validate(real_trades, synthetic_trades, *,
     cv_folds=5, seed=20260503) -> AdversarialResult`.
   - Feature builder trade-level (`hour_utc`, `dow`, `pair_idx`,
     `direction_idx`, `lots`, `duration_sec`, `pips`, `mfe_pips`, `mae_pips`,
     `entry_price_normalized`).
   - Paired stratified group k-fold CV (`StratifiedGroupKFold`) agrupando linhas
     por hash de features identicas; preserva duplicatas real/synthetic no
     mesmo fold e mantem balanceamento aproximado de classes. AUC media nos
     folds + bootstrap CI 95% sobre os AUCs dos folds.
   - Feature importance (LightGBM `gain`) top-10 ordenado.
   - Determinismo: mesmas entradas + seed → mesmo AUC `±0.01`.
3. Adicionar 5 sanity tests em
   `tests/myfxbook_pipeline/test_adversarial_validator.py`:
   - Copia exata: `synthetic = real.copy()` → `0.45 ≤ AUC ≤ 0.55`.
   - Sub-amostra: `synthetic = real.sample(0.5, seed)` → `0.45 ≤ AUC ≤ 0.55`.
   - Ruido puro: features sinteticas i.i.d. → `AUC > 0.85`.
   - Shift de hora: `synthetic = real`, `hour_utc += 6` → `AUC > 0.70`.
   - Determinismo: mesma entrada + seed → mesmo AUC `±0.01`.

## Inputs esperados

- DataFrames `real_trades` e `synthetic_trades` com colunas comuns:
  - `open_dt_utc` (datetime UTC) → fonte de `hour_utc`, `dow`.
  - `symbol` (str) → fonte de `pair_idx`.
  - `action` (`Buy`/`Sell`) → fonte de `direction_idx` (`Buy=0`, `Sell=1`).
  - `lots` (float).
  - `duration_sec` (float).
  - `pips` (float).
  - `open_price` (float) → fonte de `entry_price_normalized`.
- Colunas opcionais: `mfe_pips`, `mae_pips` (preenche `NaN` quando ausentes;
  LightGBM aceita missing nativamente).

## Outputs esperados

### Codigo

- `pyproject.toml` — extra `myfxbook_decoder` ganha `lightgbm>=4.0`.
- `uv.lock` — atualizado pelo `uv` para travar a dependencia LightGBM.
- `studies/myfxbook_reverse_engineering/shared/adversarial_validator.py` —
  modulo completo com:
  - imports limitados a `numpy`, `pandas`, `sklearn`, `lightgbm`, stdlib.
  - `AdversarialResult` dataclass frozen.
  - `_build_features(real, synthetic)` puro (nao escreve nada).
  - `adversarial_validate()` publica.
  - docstrings com citacoes em todas as decisoes.
- `tests/myfxbook_pipeline/test_adversarial_validator.py` — substitui
  placeholder por 5 sanity tests + 1 fixture compartilhada.

### Iteracao

- `iterations/005-adversarial-validator/PRE_REG.md` (este arquivo).
- `iterations/005-adversarial-validator/run.log` (saida pytest).
- `iterations/005-adversarial-validator/RESULTS.json`.
- `iterations/005-adversarial-validator/SUMMARY.md`.

## Citacoes obrigatorias

| Decisao | Citacao |
|---|---|
| LightGBM real-vs-synthetic AUC como metrica de identificabilidade | `[advances_fin_ml, ch.5]` |
| Paired stratified group k-fold + risk de overfitting em ML | `[testing_tuning, ch.7]` |
| Bootstrap CI sobre AUCs nos folds | `[advances_fin_ml, p.196-211]` |
| Feature importance via LightGBM gain | `[advances_fin_ml, ch.5]` |

## Decision rules (frozen)

- LightGBM hyperparams default conservadores (anti-overfit, sample pequeno):
  - `n_estimators=200`, `learning_rate=0.05`, `num_leaves=31`,
    `min_child_samples=10`, `feature_fraction=0.9`, `bagging_fraction=0.9`,
    `bagging_freq=5`, `objective='binary'`, `metric='auc'`,
    `verbosity=-1`, `random_state=seed`.
  - Citacao: `[testing_tuning, ch.7]` — capacity baixa em sample pequeno.
- CV: `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)` com
  `groups=hash(features)`. Agrupa duplicatas exatas para impedir leakage no
  teste `synthetic = real.copy()` e estratifica por `label` para proteger contra
  imbalance bias.
- AUC reportado: media simples dos folds (`np.mean`).
- CI 95%: bootstrap nao-parametrico de 1000 reamostragens com reposicao sobre
  os AUCs dos folds, percentis 2.5/97.5. Seed dedicado `seed + 1`.
- Sample tamanhos pequenos (n<60 total) → emite warning em `notes`,
  mas nao falha; AUC ainda computavel.
- Determinismo: `random_state=seed` em LightGBM e em StratifiedGroupKFold;
  `np.random.default_rng(seed + 1)` para bootstrap. Mesma entrada → mesmo
  resultado bit-a-bit (`±1e-12`); spec exige tolerancia `±0.01`.

## Backward-compat preservada

- Modulo `adversarial_validator` ja existe como stub (vazio com docstring).
  Substituicao limpa, sem call sites externos atuais.
- Testes existentes em `test_adversarial_validator.py` sao um placeholder
  `@pytest.mark.skip`. Reemplace por 5 testes reais.
- Demais modulos (`gates.py`, `cpcv.py`, `pre_decode_screen.py`) inalterados.

## Criterios de aceite (verificaveis)

1. `tests/myfxbook_pipeline/test_adversarial_validator.py` adicionado, 5
   sanity tests, todos passam.
2. Baseline 790 testes pre-existentes nao regride (3 falhas pre-existentes
   em `test_macro_data_loader.py` toleradas — heranca da 001-004).
3. `import lightgbm` funciona apos `uv pip install -e '.[myfxbook_decoder]'`.
4. `adversarial_validate()` retorna `AdversarialResult` com todos os campos
   preenchidos (auc, ci_low_95, ci_high_95, n_real, n_synthetic, n_features,
   feature_importance dict tamanho ≤ 10, notes list).
5. Top-10 feature_importance ordenado decrescente por gain.
6. Determinismo confirmado em sanity test 5.

## Kill-switches (a task FALHA se ocorrer)

- AUC > 0.55 em test 1 (copia exata) → bug semantico, fix antes de DONE.
- LightGBM ImportError apos `uv pip install -e '.[myfxbook_decoder]'`.
- Sanity test 4 (shift hour) AUC < 0.70 → feature `hour_utc` nao chega ao
  modelo, fix.
- Numero de testes < 790 ou nova falha em modulo nao tocado → regressao.

## Allow-list de paths tocados

- `pyproject.toml` (extra `myfxbook_decoder` ganha `lightgbm>=4.0`).
- `uv.lock` (lockfile sincronizado com `pyproject.toml`).
- `studies/myfxbook_reverse_engineering/shared/adversarial_validator.py`.
- `tests/myfxbook_pipeline/test_adversarial_validator.py`.
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/005-adversarial-validator/**`.
- `studies/myfxbook_reverse_engineering/v4_redesign/PROGRESS.md` (linha 005).
- `studies/myfxbook_reverse_engineering/v4_redesign/next_prompt.md` (rewrite).
- `jornada/2026-05-04-XXXX-myfxbook-v4-task-005-*.md` (entrada nova).
- `jornada/README.md` (lista atualizada).

NADA fora dessa lista. `frozen_rules/`, `docs/investment-mandate.md`,
`shared/replicator.py`, `shared/gates.py` nao tocados.
