# MyFxBook v4 task 005 — adversarial validator real-vs-synthetic pronto

**2026-05-04 05:55 UTC.** Fechei a quinta task da Fase 1 do redesign do
pipeline myfxbook v4. O modulo
`studies/myfxbook_reverse_engineering/shared/adversarial_validator.py` recebe
duas tabelas de trades — uma real (do MyFxBook) e uma sintetica (gerada pelo
replicator a partir de uma regra decodificada) — e devolve uma AUC out-of-fold
medindo o quanto um classificador LightGBM consegue distinguir uma da outra.

## Por que isso importa

A AUC funciona como **termometro de identificabilidade do decode**. A ideia,
emprestada de adversarial validation [advances_fin_ml, ch.5]:

| AUC observada | Interpretacao |
|---|---|
| ~ 0.50 | Sintetico indistinguivel do real → decode capturou a distribuicao do EA |
| > 0.65 | Modelo de geracao errado → overfire, taxonomia incorreta, features faltando |
| > 0.85 | Sintetico claramente diferente → regra nao replica o EA |

E um dos gates do **Decision Gate Fase 2 → 3** (semana 6 do cronograma):
SPEC.md exige `adversarial_auc < 0.65 em ≥ 3 systems` para liberar a trilha
3a (decode-self) como prioridade. Acima disso, prioridade vira 3b
(filter-and-copy via myfxbook AutoTrade).

## Features Fase 1 (MVP, trade-level)

10 features computadas para real e synthetic, mesma logica em ambos:
`hour_utc`, `dow`, `pair_idx`, `direction_idx`, `lots`, `duration_sec`,
`pips`, `mfe_pips`, `mae_pips`, `entry_price_normalized` (normalizada por
mediana de `open_price` por par no pool).

Window-level (RSI, BB position, ATR, news, cross-asset) entram na Fase 2A
com as features ricas (tasks 009-012).

## Sanity tests (5/5 PASS)

Todos passam com hyperparams LightGBM conservadores (n_estimators=200,
num_leaves=31, learning_rate=0.05):

| # | Cenario | Esperado | Obtido |
|---|---|---|---|
| 1 | `synthetic = real.copy()` | AUC ~0.5 | **0.500** ✅ |
| 2 | Synthetic com features i.i.d. | AUC > 0.85 | **1.000** ✅ |
| 3 | `synthetic = real.sample(0.5)` | AUC ~0.5 | **0.503** ✅ |
| 4 | Hour shift +6h | AUC > 0.70 | **1.000** ✅ |
| 5 | Determinismo (seed) | delta ≤ 0.01 | **0.000** ✅ |

Test 4 confirma `hour_utc` como top-1 em feature_importance — modelo isola
corretamente a feature separadora.

## Achado nao-obvio: paired-kfold

Inicialmente usei `sklearn.model_selection.StratifiedKFold(shuffle=True,
random_state=seed)`. Resultado catastrofico no test 1 (synth=real.copy()):
**AUC = 0.027**, nao 0.5. O classificador estava prevendo INVERTIDO de forma
sistematica.

Diagnostico empirico:

1. StratifiedKFold permuta as duas classes **independentemente**. Trade #i
   em real (label=0, indice 0..199) e seu clone em synthetic (label=1,
   indice 200..399) caem em folds diferentes — um vai treino, o outro
   validacao.
2. As 10 features incluem variaveis ID-like (`lots`, `duration_sec`, `pips`
   sao floats unicos por trade). LightGBM com 31 num_leaves x 200 estimators
   memoriza "esses 160 lots especificos sao label=0; aqueles outros 160 sao
   label=1".
3. Na validacao (40 trades de cada classe, copias dos vistos no treino MAS
   com label oposto), o modelo prediz invertido → AUC ≈ 0.

Solucao: `_paired_kfold_indices(X, n_splits, seed)` agrupa rows por hash de
feature row (NaN → sentinel determinístico). Hashes identicos viajam juntos
para o mesmo fold via permutacao seeded. Quando `synth = real`, todos os
pares vao juntos → cada fold de validacao tem rows com X identico em ambas
classes → modelo nao tem como prever direcao → AUC ≈ 0.5. Quando synthetic
e genuinamente diferente (testes 2 e 4), cada hash e unico → comportamento
equivale a KFold randomizado.

Decisao registrada em
`studies/myfxbook_reverse_engineering/v4_redesign/DEAD_ENDS.md`
("StratifiedKFold em adversarial validator com possivel overlap").

## LightGBM como dependencia opcional

`pyproject.toml` agora carrega `lightgbm>=4.0` no extra `myfxbook_decoder`
(decisao pre-registrada em SPEC.md). Instalei via:

```bash
uv pip install -e '.[myfxbook_decoder]'
```

→ `lightgbm 4.6.0`. Smoke import OK; baseline 795 pass / 14 skip / 3 falhas
pre-existentes em `test_macro_data_loader.py` (toleradas — heranca pre-001).

`sklearn` (cross_val_score, roc_auc_score) ja vem do core.

## Onde estamos

Fase 1 do redesign: **5/8 DONE**. Falta:

- 006-pipeline-wire-fase1 (proxima sessao) — wire pre_decode_screen +
  adversarial_validator + passes_mandate_24 em workbench/pipeline.py
- 007-fase1-batch-run — rodar batch nos 30 systems R1 v3 + 22 NOT_DECODED
- 008-fase1-document — _diagnostics/PIPELINE_V4_FASE1_REPORT.md, decisao
  GO/STOP para Fase 2 e lista N≤10 sobreviventes

Plano C (passive factor-tilted) inalterado. Plano A continua DORMANT.

Detalhes tecnicos em
`studies/myfxbook_reverse_engineering/v4_redesign/iterations/005-adversarial-validator/SUMMARY.md`.
