# PRE_REG — Task 003: cpcv-pbo

**Criado ANTES de codar logica.** Contrato congelado da task.

## Identificacao

- **Task ID:** 003-cpcv-pbo
- **Fase:** 1
- **Sessao:** 2026-05-04
- **Citacao em TASKS.md:**
  > "Implementar `shared/cpcv.py` com CSCV (Combinatorial Symmetric Cross
  > Validation) e PBO (Probability of Backtest Overfitting). `[advances_fin_ml,
  > p.208-222]`. Substitui WF8 simples como gate. Testes unitarios contra exemplo
  > numerico do livro."
- **Esclarecimento (DEAD_ENDS.md):** PBO **complementa** WF, nao substitui.
  PBO mede sorte na selecao entre N candidates; WF mede generalizacao temporal
  de UMA regra. Ambos hard gates em §2.4.
- **Spec detalhado:** `tasks/003-cpcv-pbo.md`

## Escopo (minimo)

Implementar duas funcoes em `shared/cpcv.py`:

1. `cscv_pbo(metric_matrix, n_groups=16, metric="sharpe") -> CPCVResult`
   — algoritmo numerico generico (matrix in / dataclass out), agnostico de domain.
2. `build_metric_matrix_from_candidates(candidates, trades, ohlc, n_groups=16)
   -> pd.DataFrame` — adapter myfxbook que monta `(n_groups, N)` Sharpe-per-rule.

Cobrir com 7 testes unitarios em `tests/myfxbook_pipeline/test_cpcv.py`.

NAO mexer em outros modulos. NAO refatorar gates.py (e a task 004). NAO rodar
em sistema real (deixar para 006/007).

## Inputs esperados

- Para `cscv_pbo`: `pd.DataFrame` shape `(T, N)` com retornos/Sharpes per
  sub-periodo per estrategia. Em testes, matrizes sinteticas montadas inline.
- Para o helper: `list[dict]` de candidates (schema do `decoder_candidates.py`),
  `pd.DataFrame` de trades com colunas `pips`, `is_trade`, `open_dt_utc`. Para
  smoke test, mini-suite sintetica.

## Outputs esperados

### Codigo

- `studies/myfxbook_reverse_engineering/shared/cpcv.py` — preenche skeleton 001.
  - `@dataclass(frozen=True) CPCVResult` com 9 campos:
    `n_groups, n_test, n_paths, pbo, pbo_ci_low_99, pbo_ci_high_99,
    median_oos_rank_of_best_is, n_strategies, n_periods`.
  - `cscv_pbo(metric_matrix, n_groups=16, metric="sharpe") -> CPCVResult`
  - `build_metric_matrix_from_candidates(candidates, trades, ohlc=None,
    n_groups=16, metric="sharpe") -> pd.DataFrame`
  - Helpers privados conforme necessario (`_logit_for_path`, etc).

- `tests/myfxbook_pipeline/test_cpcv.py` — preenche skeleton:
  1. `test_constant_edge_low_pbo` — matriz onde estrategia A tem Sharpe alto
     consistente em todos sub-periodos; outras com Sharpe ~0 → PBO < 0.2.
  2. `test_pure_noise_pbo_around_half` — matriz aleatoria iid → PBO em
     [0.30, 0.70].
  3. `test_adversarial_overfit_high_pbo` — matriz onde a "best in-sample"
     rotaciona entre sub-periodos → PBO > 0.7.
  4. `test_npaths_too_small_raises` — S=4 com S/2=2 dá `n_paths=C(4,2)/2=3`
     que ainda funciona; usar S=2 → ValueError com mensagem clara.
  5. `test_purging_no_period_reuse` — verifica que cada path tem
     `train_idx ∩ test_idx == ∅` (CSCV nao reutiliza submatrizes).
  6. `test_determinism` — mesma matriz → mesmo PBO (e mesmo CI bootstrap com
     mesma seed).
  7. `test_build_metric_matrix_smoke` — 3 candidates dummy + ~80 trades
     sinteticos + n_groups=4 → shape `(4, 3)`.

### Iteracao

- `iterations/003-cpcv-pbo/PRE_REG.md` (este arquivo)
- `iterations/003-cpcv-pbo/run.log` (saida pytest)
- `iterations/003-cpcv-pbo/RESULTS.json` (parseable)
- `iterations/003-cpcv-pbo/SUMMARY.md` (humano)

## Citacoes obrigatorias

| Decisao | Citacao |
|---|---|
| CSCV / PBO algoritmo geral | `[advances_fin_ml, p.208-222]` (Lopez de Prado, AFML cap. 14) |
| PBO < 0.5 hard gate | `[advances_fin_ml, p.211]` |
| PBO complementa WF (nao substitui) | DEAD_ENDS.md "PBO substituindo WF8 (rejeitado)" |
| Sharpe per-trade no helper | `[evidence_based_ta, p.325-328]` (signal/noise sample-level) |
| Bootstrap CI 99% | `[testing_tuning, p.310-322]` (resampling para CI) |

## Decision rules (frozen)

- `pbo < 0.5` = passa hard gate (mandate §2.4)
- `pbo >= 0.5` = rejeita ("mais provavel sorte que edge real")
- `pbo` retorna `NaN` quando S < 4 ou n_paths < 2 → kill-switch numerico

## Detalhes de implementacao decididos

- **n_paths = C(S, S/2) / 2 paths simetricos** (paper Bailey/Lopez 2014).
  Enumerar via `combinations(range(S), S/2)` mantendo apenas splits onde `0 ∈ J`
  (representante canonico do par {J, J^complement}). Documentado em docstring.
- **Logit:** `lambda_c = log(w_c / (1 - w_c))` onde
  `w_c = rank_oos_of_best_in / (N + 1)`. Usa `scipy.stats.rankdata(method="average")`
  (rank 1 = pior, N = melhor).
- **PBO = fracao de paths com `lambda_c <= 0`.**
- **CI 99% bootstrap:** 1000 resamples dos indicadores `(logits <= 0)`,
  quantis 0.005 e 0.995. Seed fixa (`20260504`) para determinismo.
- **median_oos_rank_of_best_is:** mediana do rank OOS da melhor IS — diagnostico.
  Esperado ~N/2 quando ha sorte, > N/2 quando ha edge real.
- **rebinning de matrix:** v1 nao faz rebinning. Se `T != n_groups`, usa S = T
  (ignora `n_groups` exceto como dica para o helper).
- **S impar:** dropa ultima linha, S = S - 1 com warning.
- **S < 4:** ValueError ("CSCV exige S >= 4").
- **Helper:** assume cada candidate tem `extra["predicted_mask"]` (bool array).
  Se ausente, retorna NaN para aquele candidate (smoke test pode injetar masks).
  Sub-periodos sao bins temporais iguais por `open_dt_utc`. Sub-periodo com
  < 2 trades → NaN para todos os candidates (Sharpe indefinido).

## Criterios de aceite (verificaveis)

1. `cscv_pbo(constant_edge_matrix)` retorna `pbo < 0.2`.
2. `cscv_pbo(noise_matrix)` retorna `0.30 <= pbo <= 0.70`.
3. `cscv_pbo(adversarial_overfit_matrix)` retorna `pbo > 0.7`.
4. `cscv_pbo(matrix_S_lt_4)` raises `ValueError`.
5. CSCV nao reutiliza periodos: para todos os paths, `set(train) & set(test) == set()`.
6. Determinismo: 2 chamadas seguidas com mesma seed/matrix → mesmo `pbo` e
   `pbo_ci_low_99/high_99`.
7. `build_metric_matrix_from_candidates(3 dummy candidates, ~80 trades, n_groups=4)`
   retorna DataFrame de shape `(4, 3)`.
8. Baseline 768 testes (pre-existentes) nao regride. 3 falhas pre-existentes
   em `test_macro_data_loader.py` ignoradas (heranca da 001/002).

## Kill-switches (a task FALHA se ocorrer)

- Test 1 (constant edge) retorna PBO > 0.4 → bug na construcao de paths
- Test 3 (adversarial overfit) retorna PBO < 0.5 → bug no logit/ranking
- Test 5 falha → CSCV bugada (purging quebrado)
- Determinismo falha → bug em rng/seed

## Allow-list de paths tocados

- `studies/myfxbook_reverse_engineering/shared/cpcv.py` (preenche)
- `tests/myfxbook_pipeline/test_cpcv.py` (preenche)
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/003-cpcv-pbo/**`
- `studies/myfxbook_reverse_engineering/v4_redesign/PROGRESS.md` (linha 003)
- `studies/myfxbook_reverse_engineering/v4_redesign/next_prompt.md` (rewrite)

NADA fora dessa lista. Frozen rules e outras hunts intocadas.
