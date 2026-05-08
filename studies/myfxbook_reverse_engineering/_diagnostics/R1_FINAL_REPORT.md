# R1 Final Report — frozen_rules v3

Data: 2026-05-03

Escopo: 30 systems re-decodificados no R1 = 23 `DECODED` + 7 `PARTIAL_DECODED` do OVR antigo. Os 22 `NOT_DECODED` continuam fora do R1, mas permanecem no universo total de 52 systems e devem aparecer como `NOT_DECODED`/nao-recuperaveis em rankings futuros.

Este relatório documenta decodabilidade semântica, nao deployabilidade. Capital segue 100% Plano C; Plano A permanece DORMANT.

Citação metodológica: congelar a taxonomia antes de replicacao evita mudar labels depois de olhar resultados; a proxima etapa ainda precisa testar replicabilidade fora do timestamp real, sob risco de overfitting/data-mining bias `[advances_fin_ml, p.208-211]`.

## Auditoria R1

| Item | Resultado |
|---|---|
| Manifest lido | `_diagnostics/R1_pre_manifest.json` |
| Pool manifest | 30 |
| `status.tsv` | 25 linhas, incompleto |
| Omissos em `status.tsv` | `10067081, 10192401, 10249298, 10251631, 10475089` |
| SHA atual vs pre-R1 | 30/30 mudaram |
| Strict validation dos `systems/<id>/signal_rule.md` | 30/30 `DONE_VALID` |
| Promocao para `frozen_rules/` | 30/30 promovidos |
| Strict validation pos-promocao | PASS=30 WARN=0 FAIL=0 |
| chmod pos-promocao | 30/30 frozen rules em `444` |
| Backup pre-v3 | `frozen_rules/_pre_v3_R1_2026-05-03T0000Z/` |

## Tabela Final

| system_id | family pre-R1 | family pos-R1 | confidence | reason_code | candidate_new_family | reclass | needs_m1_review |
|---|---|---:|---:|---|---|---|---|
| 10062918 | UNCATEGORIZED | UNCATEGORIZED | 0.50 | taxonomy_gap | SWING_MR_MA_FADE | no | no |
| 10067081 | UNCATEGORIZED | UNCATEGORIZED | 0.55 | mixed_strategy |  | no | no |
| 10192401 | FACTOR_SCALPING | UNCATEGORIZED | 0.55 | taxonomy_gap | BTC_NY_HOURS_BB_TREND | yes | no |
| 10224499 | LATE_NY_BREAKOUT | LATE_NY_BREAKOUT | 0.72 |  |  | no | no |
| 10249298 | UNCATEGORIZED | SWING_TREND_MOMENTUM | 0.58 |  |  | yes | no |
| 10251631 | FACTOR_SCALPING | UNCATEGORIZED | 0.32 | taxonomy_gap | ASIAN_PRELONDON_GOLD_MR_H4 | yes | no |
| 10281851 | UNCATEGORIZED | H1_MOMENTUM_GOLD | 0.60 |  |  | yes | yes |
| 10475089 | UNCATEGORIZED | UNCATEGORIZED | 0.42 | taxonomy_gap | TOKYO_OPEN_SWING | no | no |
| 10563761 | FACTOR_SCALPING | UNCATEGORIZED | 0.62 | taxonomy_gap | H1_MOMENTUM_BTC | yes | yes |
| 10734338 | FACTOR_SCALPING | UNCATEGORIZED | 0.50 | taxonomy_gap | CRYPTO_INTRADAY_MOMENTUM | yes | yes |
| 11155858 | UNCATEGORIZED | UNCATEGORIZED | 0.30 | degenerate |  | no | no |
| 11171596 | UNCATEGORIZED | UNCATEGORIZED | 0.45 | taxonomy_gap | PAIR_HEDGED_DAILY_FX_SHORT | no | no |
| 11206045 | UNCATEGORIZED | UNCATEGORIZED | 0.38 | taxonomy_gap | TOKYO_OPEN_JPY_SWING | no | yes |
| 11207608 | OVERLAP_NY_LONDON_RANGE | H1_MOMENTUM_GOLD | 0.65 |  |  | yes | yes |
| 11355455 | FACTOR_SCALPING | H1_MOMENTUM_GOLD | 0.70 |  |  | yes | yes |
| 1152318 | UNCATEGORIZED | UNCATEGORIZED | 0.55 | taxonomy_gap | SWING_FX_MEAN_REVERSION | no | no |
| 11628637 | UNCATEGORIZED | UNCATEGORIZED | 0.55 | taxonomy_gap | H1_MOMENTUM_CRYPTO | no | yes |
| 1407880 | LATE_NY_BREAKOUT | LATE_NY_BREAKOUT | 0.75 |  |  | no | no |
| 1603276 | LONDON_OPEN_MOMENTUM | UNCATEGORIZED | 0.45 | taxonomy_gap | INTRADAY_TREND_SCALP | yes | yes |
| 1612420 | OVERLAP_NY_LONDON_RANGE | NEWS_RELEASE_MOMENTUM | 0.60 |  |  | yes | yes |
| 2373850 | UNCATEGORIZED | UNCATEGORIZED | 0.55 | degenerate |  | no | no |
| 2421356 | UNCATEGORIZED | H1_MOMENTUM_GOLD | 0.60 |  |  | yes | yes |
| 6541963 | H1_MOMENTUM_GOLD | H1_MOMENTUM_GOLD | 0.60 |  |  | no | yes |
| 8577442 | OVERLAP_NY_LONDON_RANGE | SWING_TREND_MOMENTUM | 0.60 |  |  | yes | no |
| 8647517 | UNCATEGORIZED | H1_MOMENTUM_GOLD | 0.65 |  |  | yes | yes |
| 9375654 | OVERLAP_NY_LONDON_RANGE | OVERLAP_NY_LONDON_RANGE | 0.55 |  |  | no | yes |
| 9830783 | OVERLAP_NY_LONDON_RANGE | UNCATEGORIZED | 0.30 | hold_mismatch |  | yes | no |
| 9841939 | FACTOR_SCALPING | UNCATEGORIZED | 0.65 | degenerate |  | yes | no |
| 9843883 | UNCATEGORIZED | UNCATEGORIZED | 0.50 | hold_mismatch |  | no | no |
| 9912554 | UNCATEGORIZED | UNCATEGORIZED | 0.30 | insufficient_evidence |  | no | no |

## Reclassificacao

| Base | Reclass | Taxa |
|---|---:|---:|
| frozen v2 conhecido | 4/15 | 26.7% |
| tabela pre-R1 signal -> pos-R1 frozen | 15/30 | 50.0% |

O gate especificado e `reclass >50%`; portanto 15/30 nao dispara por estar exatamente em 50.0%.

## Contagem Por Familia

| Familia | Count |
|---|---:|
| UNCATEGORIZED | 18 |
| H1_MOMENTUM_GOLD | 6 |
| LATE_NY_BREAKOUT | 2 |
| SWING_TREND_MOMENTUM | 2 |
| NEWS_RELEASE_MOMENTUM | 1 |
| OVERLAP_NY_LONDON_RANGE | 1 |

## UNCATEGORIZED Por reason_code

| reason_code | Count |
|---|---:|
| taxonomy_gap | 11 |
| degenerate | 3 |
| hold_mismatch | 2 |
| mixed_strategy | 1 |
| insufficient_evidence | 1 |

## candidate_new_family

Nenhum `candidate_new_family` repetiu com `n>=2`.

| candidate_new_family | Count |
|---|---:|
| ASIAN_PRELONDON_GOLD_MR_H4 | 1 |
| BTC_NY_HOURS_BB_TREND | 1 |
| CRYPTO_INTRADAY_MOMENTUM | 1 |
| H1_MOMENTUM_BTC | 1 |
| H1_MOMENTUM_CRYPTO | 1 |
| INTRADAY_TREND_SCALP | 1 |
| PAIR_HEDGED_DAILY_FX_SHORT | 1 |
| SWING_FX_MEAN_REVERSION | 1 |
| SWING_MR_MA_FADE | 1 |
| TOKYO_OPEN_JPY_SWING | 1 |
| TOKYO_OPEN_SWING | 1 |

## Familias Provisorias

| Familia provisoria | Suporte R1 v3 | Gate |
|---|---:|---|
| H1_MOMENTUM_GOLD | 6 | PASS: deixou de ser n=1 |
| NEWS_RELEASE_MOMENTUM | 1 | PAUSE: permanece n=1 |
| SWING_TREND_MOMENTUM | 2 | PASS: deixou de ser n=1 |

## needs_m1_review

Marcados: 13/30.

`10281851, 10563761, 10734338, 11206045, 11207608, 11355455, 11628637, 1603276, 1612420, 2421356, 6541963, 8647517, 9375654`

Interpretação: M5 continua timeframe base. Estes systems precisam de review M1 quando p50_hold <5min, news/event, ou timing sub-M5 aparece na regra. News systems devem ser replicados primeiro por evidencia clock/OHLC, sem assumir calendario economico ou IA live.

## Pause Gates

| Gate | Resultado | Estado |
|---|---|---|
| reclass >50% | 15/30 = 50.0%; frozen-v2-known 4/15 = 26.7% | PASS |
| candidate_new_family n>=2 | 0 candidates repetidos | PASS |
| label fora enum | 0 | PASS |
| UNCAT sem reason_code | 0 | PASS |
| taxonomy_gap sem candidate_new_family | 0 | PASS |
| familia provisoria ainda n=1 | `NEWS_RELEASE_MOMENTUM` = 1 | PAUSE |
| muitos needs_m1_review | 13/30 | PAUSE |
| qualquer falha strict | 0 | PASS |

Conclusao: contrato semantico v3 esta limpo e promovido. Existem dois pause gates metodologicos antes de seguir automaticamente: `NEWS_RELEASE_MOMENTUM` continua n=1 e `needs_m1_review` e alto. Nao iniciar Wave C/D nem 5R-1/5R-2 sem aprovacao explicita.
