# PIPELINE_V4_FASE1_REPORT

## Verdict

Fase 1 = **STOP para Fase 2A**.

O batch operacional avaliou `55` systems: `21` passaram o pre-screen, `27` pararam no pre-screen e `7` falharam por `frozen_rules/<id>.md` ausente. Os `21` `pre_screen_go_systems` sao evidencia audit-only; a lista downstream `fase2_eligible_survivors` usa o contrato corrigido `pre_screen_decision=GO AND adversarial_auc<0.65 AND mandate_24_pass=true` e ficou vazia.

Nao iniciar automaticamente tasks `009-013`. A proxima acao precisa de decisao humana: pivot para Fase 3b/filter-and-copy com novo contrato, ou encerramento do pipeline v4.

## Section 1 — Pre-screen Results

Tabela gerada dos `pre_decode_screen.json` existentes sob `systems/*/decoding_v4_fase1/`. O spec historico citava 52 rows, mas o batch corrigido da task 007 processou 55 system IDs disponiveis; este report documenta os 55 artefatos reais.

| system_id | mcpt_p | psr_p | concentration_top5 | is_live | decision | notes |
|---|---:|---:|---:|---|---|---|
| 10062918 | 0.0005 | 4.263e-14 | 0.189393 | true | GO |  |
| 10067081 | 0.0005 | 0 | 0.329706 | true | GO |  |
| 10192401 | 0.113943 | 0.117267 | 0.199196 | true | STOP | MCPT p=0.1139 >= 0.05; PSR p=0.1173 >= 0.05 |
| 10224499 | 1 | 1 | 0.390752 | true | STOP | MCPT p=1.0000 >= 0.05; PSR p=1.0000 >= 0.05 |
| 10249298 | 0.0005 | 5.998e-08 | 0.354265 | true | GO |  |
| 10251631 | 0.104948 | 0.124633 | 0.743115 | true | STOP | MCPT p=0.1049 >= 0.05; PSR p=0.1246 >= 0.05; concentration top-5%=0.743 >= 0.5 |
| 10281851 | 0.0005 | 0 | 0.444248 | true | GO |  |
| 10475089 | 0.10095 | 0.040294 | 0.403485 | true | STOP | MCPT p=0.1009 >= 0.05 |
| 10563761 | 0.011494 | 0.014401 | 0.226691 | true | GO |  |
| 10585558 | 0.0005 | 0 | 0.440793 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 126.41 (> 3.0) — within-month doubling |
| 10716398 | 0.0005 | 0 | 0.353107 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 139.40 (> 3.0) — within-month doubling |
| 10734338 | 0.0005 | 6.695e-14 | 0.270414 | false | GO | is_live=False (account_type='Demo'); warning-only, does not block |
| 10746260 | 0.0005 | 5.344e-08 | 0.317136 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 128.08 (> 3.0) — within-month doubling |
| 10814265 | 0.010495 | 0.014354 | 0.280073 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 125.92 (> 3.0) — within-month doubling |
| 10878805 | 0.0005 | 0.003124 | 0.539532 | true | STOP | concentration top-5%=0.540 >= 0.5 |
| 10970107 | 0.0005 | 0 | 0.376369 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 127.98 (> 3.0) — within-month doubling |
| 11155858 | 0.0005 | 5.097e-07 | 0.41349 | true | GO |  |
| 11171596 | 0.053473 | 0.047768 | 0.27761 | true | STOP | MCPT p=0.0535 >= 0.05 |
| 11206045 | 0.0005 | 5.195e-06 | 0.315704 | true | GO |  |
| 11207608 | 0.021989 | 0.027931 | 0.254078 | true | GO |  |
| 11305553 | 0.0005 | 2.036e-05 | 0.216322 | true | STOP | K1 sanity FAIL: 30 doubling-after-loss trades (>5% of total); per-month max/median P95 = 30.75 (> 3.0) — within-month doubling |
| 11355455 | 0.0005 | 2.331e-15 | 0.501711 | true | STOP | concentration top-5%=0.502 >= 0.5 |
| 11504701 | 0.0005 | 2.104e-10 | 0.531069 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 119.47 (> 3.0) — within-month doubling; concentration top-5%=0.531 >= 0.5 |
| 1152318 | 0.0005 | 7.019e-07 | 0.229744 | true | GO |  |
| 11628637 | 0.0005 | 8.316e-05 | 0.231207 | true | GO |  |
| 11986417 | 0.0005 | 2.585e-13 | 0.637575 | true | STOP | concentration top-5%=0.638 >= 0.5 |
| 1407880 | 0.0005 | 0 | 0.065335 | false | GO | is_live=False (account_type='Demo'); warning-only, does not block |
| 1603276 | 0.0005 | 0 | 0.759384 | true | STOP | concentration top-5%=0.759 >= 0.5 |
| 1612420 | 0.0005 | 0 | 0.313411 | false | GO | is_live=False (account_type='Demo'); warning-only, does not block |
| 2123808 | 0.0005 | 7.224e-08 | 0.262265 | true | GO |  |
| 2373850 | 0.102449 | 0.089897 | 0.346947 | true | STOP | MCPT p=0.1024 >= 0.05; PSR p=0.0899 >= 0.05 |
| 2421356 | 0.0005 | 0 | 0.115297 | false | GO | is_live=False (account_type='Demo'); warning-only, does not block |
| 2483126 | 0.0005 | 0 | 0.268291 | true | GO |  |
| 3568877 | 0.0005 | 0 | 0.340511 | true | GO |  |
| 5542332 | 0.0005 | 0 | 0.284293 | true | GO |  |
| 612872 | 0.012494 | 0.015723 | 0.29097 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 32.90 (> 3.0) — within-month doubling |
| 6541963 | 0.0005 | 0 | 0.108395 | false | GO | is_live=False (account_type='Demo'); warning-only, does not block |
| 6603448 | 0.0005 | 9.314e-07 | 0.314027 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 4.35 (> 3.0) — within-month doubling |
| 7603723 | 0.0005 | 2.581e-13 | 0.319107 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 5.10 (> 3.0) — within-month doubling |
| 7942220 | 0.0005 | 3.236e-11 | 0.330665 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 5.95 (> 3.0) — within-month doubling |
| 8286716 | 0.0005 | 0 | 0.198723 | true | GO |  |
| 8397136 | 0.267866 | 0.249921 | 0.241284 | true | STOP | MCPT p=0.2679 >= 0.05; PSR p=0.2499 >= 0.05 |
| 8574205 | 0.0005 | 0 | 0.348885 | true | GO |  |
| 8577442 | 0.0005 | 4.219e-15 | 0.186321 | true | GO |  |
| 8577996 | 0.0005 | 0 | 0.271025 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 4.10 (> 3.0) — within-month doubling |
| 8599269 | 0.025987 | 0.030183 | 0.288425 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 5.00 (> 3.0) — within-month doubling |
| 8599392 | 0.0005 | 0 | 0.363931 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 209.40 (> 3.0) — within-month doubling |
| 8647517 | 0.0005 | 0 | 0.393545 | true | GO |  |
| 9375654 | 0.0005 | 2.220e-16 | 0.37296 | true | GO |  |
| 9526428 | 0.0005 | 0 | 0.205089 | true | GO |  |
| 9607500 | 0.033983 | 0.038084 | 0.345977 | true | STOP | K1 sanity FAIL: per-month max/median P95 = 144.59 (> 3.0) — within-month doubling |
| 9830783 | 0.0005 | 0.000889 | 0.378216 | true | GO |  |
| 9841939 | 0.0005 | 0 | 0.237498 | true | GO |  |
| 9843883 | 0.050975 | 0.052542 | 0.322342 | true | STOP | MCPT p=0.0510 >= 0.05; PSR p=0.0525 >= 0.05 |
| 9912554 | 0.0005 | 6.894e-06 | 0.287379 | true | GO |  |

## Section 2 — Pre-screen GO vs Fase2-eligible Survivors

`pre_screen_go_systems` audit-only: `21`. Eles passaram MCPT/PSR/concentration no track record do EA `[evidence_based_ta, p.325-328]`, mas isso nao basta para Fase 2 se o decode sintetico e distinguivel do real ou se falha `mandate_24`.

| rank_psr | system_id | psr_p | mcpt_p | concentration_top5 | is_live | adversarial_auc | mandate_24_pass | mandate_24_failed |
|---:|---|---:|---:|---:|---|---:|---|---|
| 1 | 10067081 | 0 | 0.0005 | 0.329706 | true | null | null |  |
| 2 | 10281851 | 0 | 0.0005 | 0.444248 | true | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999 |
| 3 | 1407880 | 0 | 0.0005 | 0.065335 | false | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999, dsr_p |
| 4 | 1612420 | 0 | 0.0005 | 0.313411 | false | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999, dsr_p |
| 5 | 2421356 | 0 | 0.0005 | 0.115297 | false | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999 |
| 6 | 6541963 | 0 | 0.0005 | 0.108395 | false | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999 |
| 7 | 8647517 | 0 | 0.0005 | 0.393545 | true | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999 |
| 8 | 9841939 | 0 | 0.0005 | 0.237498 | true | null | null |  |
| 9 | 9375654 | 2.220e-16 | 0.0005 | 0.37296 | true | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999 |
| 10 | 8577442 | 4.219e-15 | 0.0005 | 0.186321 | true | null | null |  |
| 11 | 10062918 | 4.263e-14 | 0.0005 | 0.189393 | true | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999, dsr_p |
| 12 | 10734338 | 6.695e-14 | 0.0005 | 0.270414 | false | 0.999995 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999 |
| 13 | 10249298 | 5.998e-08 | 0.0005 | 0.354265 | true | null | null |  |
| 14 | 11155858 | 5.097e-07 | 0.0005 | 0.41349 | true | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999 |
| 15 | 1152318 | 7.019e-07 | 0.0005 | 0.229744 | true | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999, dsr_p |
| 16 | 11206045 | 5.195e-06 | 0.0005 | 0.315704 | true | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999, dsr_p |
| 17 | 9912554 | 6.894e-06 | 0.0005 | 0.287379 | true | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999, dsr_p |
| 18 | 11628637 | 8.316e-05 | 0.0005 | 0.231207 | true | 0.999755 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999 |
| 19 | 9830783 | 0.000889 | 0.0005 | 0.378216 | true | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999, dsr_p |
| 20 | 10563761 | 0.014401 | 0.011494 | 0.226691 | true | 0.999991 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999 |
| 21 | 11207608 | 0.027931 | 0.021989 | 0.254078 | true | 1 | false | sharpe_bootstrap_ci_low_999, oos_bootstrap_ci_low_999, dsr_p |

Lista downstream:

- `fase2_eligible_survivors = []`
- `survivors = []`
- `n_fase2_eligible_survivors = 0`

Definicao downstream congelada apos correcao humana: `pre_screen_decision=GO AND adversarial_auc<0.65 AND mandate_24_pass=true`. O threshold adversarial mede identificabilidade real-vs-synthetic `[advances_fin_ml, ch.5]`; `mandate_24_pass=true` exige hard gates/DSR `[advances_fin_ml, p.273-275]`. PBO/CSCV fica opcional/ausente nesta fase porque ainda nao houve selecao entre multiplos candidatos minerados `[advances_fin_ml, p.208-222]`.

## Section 3 — Comparacao Baseline vs Fase 1

| Metric | Count |
|---|---:|
| Systems no universo operacional do batch | 55 |
| Systems que passavam para decode antes da Fase 1 | 55 |
| Systems com pre-screen GO | 21 |
| Systems com PRE_SCREEN_STOP | 27 |
| Systems failed por `frozen_rules/<id>.md` ausente | 7 |
| GO com `adversarial_auc < 0.65` | 0 |
| GO com `mandate_24_pass=true` | 0 |
| Fase 2 eligible survivors | 0 |

Top razoes de STOP no pre-screen:

| reason | count |
|---|---:|
| `k1_sanity_fail` | 15 |
| `mcpt_p_high` | 8 |
| `concentration_high` | 6 |
| `psr_p_high` | 6 |

Entre os GO com AUC calculavel, `adversarial_auc` ficou entre `0.999755` e `1`; portanto nenhum synthetic ficou abaixo de `0.65`. Isso indica que os trades sinteticos continuam trivialmente distinguiveis dos reais pelo discriminador LightGBM `[advances_fin_ml, ch.5]`.

## Section 4 — Decisao Fase 1 → Fase 2

**Decision Gate Fase 1: STOP.**

Razao: `N == 0` em `fase2_eligible_survivors`. O pre-screen encontrou 21 EAs com track record estatisticamente aceitavel para auditoria, mas nenhum satisfaz simultaneamente `adversarial_auc<0.65` e `mandate_24_pass=true`. Avancar para Fase 2A com N=0 violaria o contrato da Fase 1 e transformaria tasks 009-013 em especulacao sem universo valido.

Pedido de decisao humana: escolher entre pivot para Fase 3b/filter-and-copy com novo contrato explicito, ou encerrar o pipeline v4. Enquanto isso, Plano A segue DORMANT, capital 100% Plano C, sem paper/live e sem alterar `frozen_rules/`.

## Section 5 — Citacoes

- MCPT no pre-screen do track record do EA: `[evidence_based_ta, p.325-328]`.
- PSR no pre-screen do track record do EA: `[advances_fin_ml, p.260-263]`.
- Adversarial real-vs-synthetic AUC como medida de identificabilidade do synthetic: `[advances_fin_ml, ch.5]`.
- DSR hard gate via `mandate_24` no synthetic: `[advances_fin_ml, p.273-275]`.
- PBO/CSCV opcional/ausente na Fase 1 porque ainda nao ha mining de multiplos candidatos Fase 2B: `[advances_fin_ml, p.208-222]`.
- Walk-forward purgado permanece parte dos hard gates quando aplicavel downstream: `[testing_tuning, p.148-162]`.
