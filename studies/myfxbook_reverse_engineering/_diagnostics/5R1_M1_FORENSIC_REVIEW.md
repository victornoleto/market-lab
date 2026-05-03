# 5R-1 M1 Forensic Review

Data: 2026-05-03

Escopo aprovado pelo usuario: ultimo teste forense M1 apenas nos 13 systems R1 v3 marcados `needs_m1_review`.

Este arquivo nao e ranking final. E uma comparacao auditavel M5 vs M1 para verificar se granularidade sub-M5 recupera a decodificacao operacional. Score continua medindo fidelidade de regra congelada contra trades reais, nao edge economico; qualquer inferencia de estrategia exigiria validacao anti-overfit posterior `[advances_fin_ml, p.196-211]`.

## Guardrails

| Guardrail | Estado |
|---|---|
| Ranking final permitido | `false` |
| Decisao estrategica permitida | `false` |
| Capital | 100% Plano C |
| Plano A | DORMANT |
| 6R / Stage 3 / paper trading | Nao iniciado |
| Frozen rules | Nao alteradas |
| Outputs M5 `systems/<id>/decoding/` | Preservados |
| Outputs M1 | `systems/<id>/decoding_m1/` |

Pause gates preservados:

| Gate | Estado |
|---|---|
| `NEWS_RELEASE_MOMENTUM` n=1 | Bloqueante para ranking final |
| `needs_m1_review` 13/30 | Este review testou os 13; nao libera ranking final sozinho |

## Implementacao

Mudanca minima aplicada:

- `scripts/run_replicator_batch.py`: adiciona `--freq M1/M5`, `--output-dir-name` e `--summary-name`.
- `shared/replicator.py`: parametriza frequencia-base da candidate window, preload/leitura de OHLC e backtest; default permanece `M5`.
- `M1` usa janela candidata de 1 minuto e OHLC/cache `data/ohlc/<pair>/M1/`; `M5` permanece default para a rodada original.

## Comandos

Validacao estatica:

```bash
uv run python -m py_compile studies/myfxbook_reverse_engineering/scripts/run_replicator_batch.py studies/myfxbook_reverse_engineering/shared/replicator.py
```

Smoke M1 isolado:

```bash
uv run python -m studies.myfxbook_reverse_engineering.scripts.run_replicator_batch --only 10281851 --freq M1 --output-dir-name decoding_m1_smoke --summary-name batch_summary_decoding_m1_smoke.json --force --timeout-per-system 180
```

Batch forense M1:

```bash
uv run python -m studies.myfxbook_reverse_engineering.scripts.run_replicator_batch --only 10281851 10563761 10734338 11206045 11207608 11355455 11628637 1603276 1612420 2421356 6541963 8647517 9375654 --freq M1 --output-dir-name decoding_m1 --summary-name batch_summary_decoding_m1.json --force --timeout-per-system 900
```

## Resultado Do Batch M1

Fonte parseable: `_diagnostics/batch_summary_decoding_m1.json`.

| Metrica | Valor |
|---|---:|
| Systems no escopo | 13 |
| Passed | 13 |
| Failed | 0 |
| Skipped | 0 |
| Wallclock | 785.5 s |
| `fidelity_score >= 0.60` | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| NONE | 13 |
| Melhor M1 `fidelity_score` | 0.3589 |

## Comparacao M5 vs M1

Ordem da tabela segue a lista `needs_m1_review`; nao e ranking final.

| system_id | M5 score | M1 score | delta | M5 band | M1 band | M5 f1 | M1 f1 | M5 dir | M1 dir | M5 n_real | M1 n_real | M5 n_synth | M1 n_synth | M5 n_match | M1 n_match | M5 ratio | M1 ratio |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10281851 | 0.2518 | 0.2518 | +0.0000 | NONE | NONE | 0.0113 | 0.0113 | 0.9231 | 0.9231 | 652 | 652 | 1651 | 1651 | 13 | 13 | 2.5322 | 2.5322 |
| 10563761 | 0.2108 | 0.2173 | +0.0065 | NONE | NONE | 0.0218 | 0.0218 | 0.8125 | 0.8438 | 436 | 436 | 2497 | 2503 | 32 | 32 | 5.7271 | 5.7408 |
| 10734338 | 0.2385 | 0.2385 | +0.0000 | NONE | NONE | 0.0197 | 0.0197 | 0.8636 | 0.8636 | 591 | 591 | 1648 | 1648 | 22 | 22 | 2.7885 | 2.7885 |
| 11206045 | 0.2992 | 0.2992 | +0.0000 | NONE | NONE | 0.0067 | 0.0067 | 1.0000 | 1.0000 | 212 | 212 | 87 | 87 | 1 | 1 | 0.4104 | 0.4104 |
| 11207608 | 0.2095 | 0.2128 | +0.0033 | NONE | NONE | 0.0212 | 0.0182 | 0.8987 | 0.9138 | 202 | 202 | 7257 | 6186 | 79 | 58 | 35.9257 | 30.6238 |
| 11355455 | 0.2152 | 0.2153 | +0.0001 | NONE | NONE | 0.0179 | 0.0176 | 0.9275 | 0.9265 | 236 | 236 | 7486 | 7510 | 69 | 68 | 31.7203 | 31.8220 |
| 11628637 | 0.2378 | 0.2379 | +0.0001 | NONE | NONE | 0.0165 | 0.0165 | 0.8571 | 0.8571 | 232 | 232 | 617 | 618 | 7 | 7 | 2.6595 | 2.6638 |
| 1603276 | 0.1993 | 0.2146 | +0.0153 | NONE | NONE | 0.0113 | 0.0106 | 0.8202 | 0.8690 | 594 | 594 | 15192 | 15191 | 89 | 84 | 25.5758 | 25.5741 |
| 1612420 | 0.0456 | 0.0425 | -0.0031 | NONE | NONE | 0.0000 | 0.0000 | NaN | NaN | 788 | 788 | 4525 | 5488 | 0 | 0 | 5.7424 | 6.9645 |
| 2421356 | 0.3589 | 0.3589 | +0.0000 | NONE | NONE | 0.0107 | 0.0107 | 0.8947 | 0.8947 | 1763 | 1763 | 1773 | 1773 | 19 | 19 | 1.0057 | 1.0057 |
| 6541963 | 0.2212 | 0.2198 | -0.0014 | NONE | NONE | 0.0282 | 0.0281 | 0.8195 | 0.8195 | 2213 | 2213 | 16625 | 16707 | 266 | 266 | 7.5124 | 7.5495 |
| 8647517 | 0.2141 | 0.2135 | -0.0006 | NONE | NONE | 0.0232 | 0.0231 | 0.8878 | 0.8812 | 1024 | 1024 | 25135 | 25265 | 303 | 303 | 24.5459 | 24.6729 |
| 9375654 | 0.1798 | 0.1733 | -0.0065 | NONE | NONE | 0.0195 | 0.0195 | 0.5484 | 0.5161 | 915 | 915 | 2261 | 2261 | 31 | 31 | 2.4710 | 2.4710 |

Resumo da comparacao:

| Item | Count |
|---|---:|
| M1 melhorou score vs M5 | 5 |
| M1 piorou score vs M5 | 4 |
| M1 empatou no score arredondado | 4 |
| Mudancas de banda | 0 |
| M1 `fidelity_score >= 0.60` | 0 |

## Leitura Forense

- M1 nao recuperou timing operacional: `entry_timing_f1` continuou muito baixo em todos os 13 cases, com maximo 0.0281.
- M1 nao mudou a conclusao de banda: todos os 13 permanecem `NONE`.
- As pequenas melhorias vieram de direcao ou contagem em poucos systems, nao de match de entrada substantivo.
- O caso `1612420` (`NEWS_RELEASE_MOMENTUM`) continuou com `n_matched=0`; M1 publico sem calendario/evento nao recuperou o padrao.
- Over-fire segue material em varios H1_MOMENTUM_GOLD (`count_ratio` > 20 em `11207608`, `11355455`, `8647517`), sinalizando que a regra recuperada dispara muito mais que o EA real.

## Conclusao Provisoria

Nenhum dos 13 M1 atingiu `fidelity_score >= 0.60`. Combinado com a rodada M5 dos 30 R1 v3, a conclusao provisoria e: **decodificacao operacional nao recuperavel com OHLC publico M5/M1 pelo pipeline atual**.

Isto nao prova que as regras absorvidas nao tenham valor economico como ideias derivadas; prova apenas que o pipeline atual nao reproduz os trades reais do EA original com fidelidade suficiente.

## Plano Opcional — Derived Strategy Backtest

Se o estudo continuar, o caminho correto nao e 6R/Stage 3 do reverse engineering original. E criar uma trilha separada `derived_strategy_backtest` com pre-registro proprio:

1. Congelar um subconjunto pequeno de regras derivadas como hipoteses independentes, sem alegar equivalencia ao EA original.
2. Rodar backtest economico com custos, spread, slippage, sizing fixo e sem calibrar threshold pos-resultado.
3. Aplicar gates anti-overfit do mandato: PBO, DSR, walk-forward, OOS single-block e bootstrap; estes gates sao necessarios porque regras mineradas em historico de vendor tem risco alto de data-mining bias `[advances_fin_ml, p.208-211]`.
4. Reportar como estudo de estrategia derivada, nao como reverse engineering do EA HappyForex.
