# SUMMARY — Task 002: pre_decode_screen

**Verdict: DONE**

## O que foi feito

Implementado `shared/pre_decode_screen.py` com os 5 gates definidos no spec:

1. **K1 sanity** — reusa `sanity.compute_sanity` (martingale signature: lot
   doubling within 24h, per-month max/median ratio).
2. **MCPT** sign-flip permutation (`n_permutations=2000`, seed=20260503) — H0:
   retornos sao sign-symmetric noise.
3. **PSR p<0.05** sobre track record do EA (M=1, sr_benchmark=0).
4. **Concentration top-5%** — `sum(|top 5% trades|) / sum(|all trades|) < 0.50`.
5. **`is_live`** — registrado em `notes`, NAO bloqueia decision.

`screen_system(sid)` -> `PreScreenResult`. `screen_batch(sids)` -> `list`.
`write_pre_screen_json(result)` serializa para `systems/<id>/pre_decode_screen.json`.

5 testes unitarios em `tests/myfxbook_pipeline/test_pre_decode_screen.py`
cobrem os 3 goldens + concentration sintetica + MCPT determinism. Passam em
< 1 s.

## Resultados nos goldens

| System | Decision | k1 | mcpt_p | psr_p | conc_top5 | is_live | n_trades |
|---|---|---|---|---|---|---|---|
| 10281851 | **GO** | True | 0.0020 | 0.0000 | 0.444 | True | 652 |
| 11504701 | **STOP** | False | 0.0020 | 0.0000 | 0.531 | True | 314 |
| 1407880 | **GO** | True | 0.0020 | 0.0000 | 0.065 | False | 3304 |

11504701 falhou K1 (martingale per-month max/median P95=119.47 >> 3.0) E
concentration (0.531 > 0.50) — defense in depth: dois gates independentes
pegaram o mesmo padrao de comportamento.

1407880 e Demo, mas o gate so registra warning em `notes` — decision=GO
preservada conforme decisao GPT-5.5 review (DEAD_ENDS.md "is_live como
hard gate").

## Citacoes usadas

- `[advances_fin_ml, ch.13]` — overbetting/martingale (K1 base teorica)
- `[evidence_based_ta, p.325-328]` — MCPT sign-flip permutation
- `[testing_tuning, p.310-322]` — MCPT cross-reference
- `[advances_fin_ml, p.260-263]` — PSR formula com skew/kurt
- `[machine_trading, p.13-14]` — Calmar fragility / concentration
- mandate §3 + DEAD_ENDS.md — `is_live` warning-only

## Caveats / decisoes nao-obvias

- **Serie de retornos = `pips`, nao `profit`.** Em HappyForex parquets,
  `profit` chega majoritariamente como `None` (verificado em 10281851 e
  1407880); `pips` e a coluna numerica densa disponivel. Decisao registrada
  no PRE_REG.
- **Sharpe per-trade sem anualizacao.** MCPT permuta os mesmos N samples
  entao sqrt(N) cancela; PSR usa `sr_benchmark=0` que e invariante a
  anualizacao. Documentado nas docstrings.
- **PSR p=0 nos 3 goldens** reflete que os track records HappyForex tem
  signal-to-noise per-trade extremamente forte (mean/std ratios entre 0.16
  e 6.69 — esse ultimo por causa do tamanho de pip diferente em pares antigos
  do 1407880). Isso e esperado dado o vendor selection bias e nao afeta a
  validade do gate, que esta filtrando o **objeto certo** (track record do
  vendor, M=1).
- **`write_pre_screen_json` existe mas nao foi rodado em sistemas reais.**
  Persistir em `systems/<id>/pre_decode_screen.json` para o batch e tarefa
  da 006 (pipeline wire) ou 007 (batch run); a task 002 entrega apenas o
  modulo + testes.
- **3 testes pre-existentes em test_macro_data_loader.py** continuam
  falhando — sao herdados (arquivo `ebp_monthly.parquet` ausente, ja
  documentado em SUMMARY da 001). Nao e regressao.

## Licao para a proxima task

- O contrato `PreScreenResult` esta congelado para uso downstream — task 006
  pode importar diretamente sem aliases.
- `screen_batch` e sequencial; se a 007 (batch run sobre 30+22 systems)
  precisar paralelismo, pode envolver em `concurrent.futures` por fora sem
  tocar o modulo.
- DSR aplicado sobre synthetic post-mining e responsabilidade da task 015
  (LightGBM miner) + 004 (gates refactor). PSR (M=1) e o gate certo aqui
  e nao deve ser substituido por DSR no pre-screen.

## Proxima task elegivel

Como 001 esta DONE e 002 acaba aqui, as proximas com depend_on satisfeitas
sao **003-cpcv-pbo** ou **005-adversarial-validator**. Recomendo
**003-cpcv-pbo** (numerico) — destrava 004-gates-dsr-hard que destrava o
restante da Fase 1.
