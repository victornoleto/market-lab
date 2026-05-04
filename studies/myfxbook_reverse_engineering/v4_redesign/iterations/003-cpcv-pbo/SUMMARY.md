# SUMMARY — Task 003: cpcv-pbo

**Verdict: DONE**

## O que foi feito

Implementado `shared/cpcv.py` com:

- `@dataclass(frozen=True) CPCVResult` (9 campos: n_groups, n_test, n_paths,
  pbo, pbo_ci_low_99, pbo_ci_high_99, median_oos_rank_of_best_is,
  n_strategies, n_periods).
- `cscv_pbo(metric_matrix, n_groups=16, metric="sharpe") -> CPCVResult` —
  algoritmo numerico generico seguindo Bailey/Lopez 2014 §2.2 / `[advances_fin_ml,
  p.208-222]`. **Corrigido apos review GPT-5.5:** enumera todos os
  `C(S, S/2)` splits. `J train / J^c test` e `J^c train / J test` nao sao
  duplicatas porque podem escolher estrategias best-in-sample diferentes. Para
  cada path, logit
  `lambda = log(w/(1-w))` onde `w = rank_oos_of_best_in / (N+1)`. PBO =
  fracao de `lambda <= 0`.
- `build_metric_matrix_from_candidates(candidates, trades, ohlc, n_groups=16,
  metric="sharpe") -> pd.DataFrame` — adapter myfxbook que monta matriz
  `(n_groups, N)` a partir de candidates (com `extra["predicted_mask"]`)
  aplicados ao `trades.parquet` em bins temporais iguais.
- Suporte a 3 metricas: `sharpe`, `total_pnl`, `calmar`. Sharpe per-trade
  sem anualizacao (apropriado para cross-comparacao entre rules na mesma
  janela).
- CI 99% bootstrap (n=1000) com seed determinista.
- Gate exposto: `cpcv.PBO_THRESHOLD = 0.50` (mandate §2.4 hard gate).

8 testes unitarios em `tests/myfxbook_pipeline/test_cpcv.py` cobrem os 3
cenarios sinteticos canonicos + edge cases. Todos passam em ~3.3 s.

## Resultados nos 3 cenarios sinteticos (S=16, N=10/16)

| Cenario | N | PBO | CI 99% | median_oos_rank | Verdict |
|---|---:|---:|---|---:|---|
| **Constant edge** (strat 0 dominante consistente) | 10 | 0.000 | (0.000, 0.000) | 10.0 | **PASS** — best-in-train ranqueia top OOS sempre |
| **Pure noise** (iid N(0,1)) | 10 | **0.447** | (0.435, 0.457) | 6.0 | **DIAGNOSTIC** — ruido iid fica perto de 0.5 e pode cair de qualquer lado com uma seed |
| **Adversarial overfit** (spike rotativo i,i) | 16 | 1.000 | (1.000, 1.000) | 2.0 | **FAIL** — PBO=1; sempre escolhe a strat com 1 spike, OOS colapsa |

`n_paths = C(16, 8) = 12870` em todos os cenarios.

Comportamento esperado: gate `PBO < 0.5` libera edge constante e bloqueia
overfit rotativo. Ruido iid e diagnostico de calibragem, nao fixture de gate,
porque uma seed finita pode cair ligeiramente abaixo ou acima de 0.5.

## Citacoes usadas

- `[advances_fin_ml, p.208-222]` — CSCV/PBO algoritmo (Lopez de Prado, AFML
  cap. 14, baseado em Bailey & Lopez 2014)
- `[advances_fin_ml, p.211]` — gate `PBO < 0.5` ("mais provavel sorte que
  edge real")
- `[evidence_based_ta, p.325-328]` — Sharpe per-trade no helper (signal/noise
  como insumo do PBO)
- `[testing_tuning, p.310-322]` — bootstrap quantile CI
- DEAD_ENDS.md "PBO substituindo WF8 (rejeitado)" — escopo: complementa, nao
  substitui WF

## Caveats / decisoes nao-obvias

- **Correção GPT-5.5 — n_paths = C(S, S/2), nao C(S, S/2)/2.** A implementacao
  inicial usava representantes canonicos com `0 in train`, mas isso estava
  conceitualmente errado para PBO: os dois sentidos do split podem escolher
  estrategias best-in-sample diferentes. Para S=16, o correto e 12870 paths.
  Foi adicionado teste de regressao `test_complementary_splits_are_kept`.
- **Empate em `argmax`:** `np.argmax` retorna o primeiro indice em caso de
  empate. Para os cenarios reais (Sharpes contínuos) isso e raro; em testes
  sinteticos com "spike+ruido pequeno", empate nao acontece.
- **`scipy.stats.rankdata(method="average")`** lida com empates dando o rank
  medio; e a convencao do paper.
- **`build_metric_matrix_from_candidates` assume `extra["predicted_mask"]`.**
  Os candidates atuais (univariate/tree/RIPPER em `decoder_candidates.py`)
  NAO armazenam o mask — apenas `rule_text` (string). A task 015 (LightGBM
  miner) e/ou um refactor de `decoder_candidates.py` precisara persistir o
  mask. Para v1, a task 003 entrega o adapter pronto e o smoke test com
  masks injetados. Quem usar em producao (006, 015) anexa `predicted_mask`
  ao construir a `list[dict]`.
- **Sub-periodo com std=0** (ex.: candidate que skipa tudo, retornos = 0)
  retorna NaN para Sharpe — comportamento intencional, o PBO downstream
  precisa filtrar candidates com NaN.
- **CSCV exige `T >= 4`.** Para EAs com track curto (< 4 trimestres), retornar
  NaN com warning e responsabilidade do helper, nao do `cscv_pbo` direto.
  Atualmente o helper avalia mesmo com poucos trades (NaN nas linhas).

## Validacao baseline

- Testes do task: **8/8 passam** em 6.76 s apos correcao GPT-5.5.
- Baseline `tests/` excluindo `test_macro_data_loader.py` (3 fails
  pre-existentes herdadas de 001/002): **770 passed / 15 skipped / 0 failed**
  em 12.63 s.
- `test_macro_data_loader.py`: 5 passed / 3 failed (mesmas 3 falhas
  pre-existentes; `ebp_monthly.parquet` ausente no working tree).
- Sem regressao: zero novas falhas.

## Licao para a proxima task

- **CPCVResult e contrato downstream.** Tasks 004 (gates refactor) e 015
  (LightGBM miner) devem importar `CPCVResult` e `cscv_pbo` diretamente.
- **Task 004 deve adicionar PBO ao `gates.py`** chamando
  `cscv_pbo(build_metric_matrix_from_candidates(...))`. O `extra["predicted_mask"]`
  precisa ser persistido pelo miner — pode envolver patch em
  `decoder_candidates.py` na task 004 ou 015.
- **PBO != WF.** Mandate §2.4 exige AMBOS. Task 004 deve enforcar PBO < 0.5
  E WF >= 6/8 como gates independentes.
- **Bootstrap CI 99% e diagnostico, nao gate.** O gate e PBO ponto < 0.5.
  CI ajuda a interpretar incerteza amostral (se o CI cruza 0.5, decisao
  fragil — flagger no relatorio).

## Proxima task elegivel

- **004-gates-dsr-hard** (depend_on=003 ✓): refactor `gates.py` para promover
  DSR de informativo para hard gate + adicionar PBO via `cpcv.cscv_pbo`.
- **005-adversarial-validator** (depend_on=001 ✓): rodavel em paralelo, mas
  recomendo 004 primeiro — destrava 006/007/008.

A 004 esta com spec completo em `tasks/004-gates-dsr-hard.md` (nao precisa
detalhar STUB).
