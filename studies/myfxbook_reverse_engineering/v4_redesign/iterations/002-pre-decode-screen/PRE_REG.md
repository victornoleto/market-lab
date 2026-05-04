# PRE_REG — Task 002: pre_decode_screen

**Criado ANTES de qualquer codigo de logica.** Contrato congelado da task.

## Identificacao

- **Task ID:** 002-pre-decode-screen
- **Fase:** 1
- **Sessao:** 2026-05-04
- **Citacao em TASKS.md (`tasks/002-pre-decode-screen.md`):**
  > "Implementar pre-filtro que rejeita EAs sem edge real ANTES de gastar
  > compute decodando. 5 gates encapsulados: K1 sanity (martingale), MCPT,
  > PSR p<0.05, concentration top-5%, is_live (warning-only)."
- **Spec detalhado:** `tasks/002-pre-decode-screen.md`

## Escopo (minimo)

Implementar `studies/myfxbook_reverse_engineering/shared/pre_decode_screen.py`
com 5 gates exatamente como definidos no spec; nao adicionar gates novos, nao
mudar thresholds, nao refatorar `sanity.py` existente. Cobrir com 5 testes
unitarios contra goldens.

## Inputs esperados

- `data/trades/<system_id>/trades.parquet` — output do `parser.parse_*`
  (cols: `is_trade`, `pips`, `lots`, `open_dt_utc`, `close_dt_utc`, `symbol`, `action`)
- `systems/<system_id>/system_info.json` — dict com `account.account_type`
  (`"Real"` | `"Demo"`)

Sistemas usados como golden:
- `10281851` (Real, gain +3,376%, MDD 11.7%, 652 trades, OVERLAP_NY_LONDON_RANGE) → GO
- `11504701` (Real, MARTINGALE_GRID, sanity FAIL detectado em reliability_score.json) → STOP
- `1407880` (Demo, 3304 trades, LATE_NY_BREAKOUT, sanity OK) → GO com is_live=False

## Outputs esperados

### Codigo

- `studies/myfxbook_reverse_engineering/shared/pre_decode_screen.py` — modulo
  preenchido com:
  - `@dataclass(frozen=True) PreScreenResult`
  - `screen_system(system_id, *, n_permutations=2000, seed=20260503) -> PreScreenResult`
  - `screen_batch(system_ids) -> list[PreScreenResult]`
  - helpers privados: `_load_trades`, `_load_account_type`, `_mcpt_p_value`,
    `_psr_p_value`, `_concentration_top5`, `_sharpe_annualized_per_trade`
  - `write_pre_screen_json(result, *, output_path=None) -> Path` — serializa
    `pre_decode_screen.json`

- `tests/myfxbook_pipeline/test_pre_decode_screen.py` — 5 testes:
  1. `test_golden_pass_real` — system 10281851 retorna `decision="GO"`,
     `is_live=True`, `k1_sanity_pass=True`
  2. `test_golden_stop_martingale` — system 11504701 retorna `decision="STOP"`
     com `k1_sanity_pass=False`
  3. `test_golden_demo_warning_only` — system 1407880 retorna `is_live=False`
     com `decision="GO"` (demo flag NAO bloqueia)
  4. `test_concentration_high_synthetic` — DataFrame sintetico onde top-5%
     trades = 80% PnL → STOP por `concentration_top5 > 0.50`
  5. `test_mcpt_determinism` — mesma seed produz mesmo p-value

### Iteracao

- `iterations/002-pre-decode-screen/PRE_REG.md` (este arquivo)
- `iterations/002-pre-decode-screen/run.log`
- `iterations/002-pre-decode-screen/RESULTS.json`
- `iterations/002-pre-decode-screen/SUMMARY.md`

## Citacoes obrigatorias (Regra 2)

| Decisao | Citacao |
|---|---|
| K1 sanity (martingale signature, reuso de `sanity.py`) | `[advances_fin_ml, ch.13]` (overbetting/martingale) |
| MCPT (sign-flip permutation, n=2000) | `[evidence_based_ta, p.325-328]`, `[testing_tuning, p.310-322]` |
| PSR (track record do EA, M=1, sr_benchmark=0) | `[advances_fin_ml, p.260-263]` |
| Concentration test (top-5% PnL contribution) | `[machine_trading, p.13-14]` (Calmar fragilidade) |
| `is_live` warning-only (nao bloqueia) | mandate §3 + `DEAD_ENDS.md` "is_live como hard gate (rejeitado)" |
| Sign-flip Sharpe permutation (vs sample-with-replacement) | `[evidence_based_ta, p.325-328]` |

NAO usar DSR aqui: DSR pressupoe selecao ex-post entre M tentativas;
track record do EA e serie unica do vendor (M=1). DSR reaparece em Fase 3a
apos LightGBM mining (`[advances_fin_ml, p.273-275]`). Veja
`DEAD_ENDS.md` -> "DSR com M=1".

## Decision rules (frozen no spec)

`decision="GO"` requer **TODOS** os 4 gates duros:

1. `k1_sanity_pass == True`
2. `mcpt_p < 0.05`
3. `psr_p < 0.05`
4. `concentration_top5 < 0.50`

`is_live` registrado em notes mas **nao afeta decision**.

## Detalhes de implementacao decididos

- **Serie de retornos para MCPT/PSR/Sharpe/concentration:** usar coluna `pips`
  do trades.parquet. Razao: `profit` esta majoritariamente `None` em sistemas
  HappyForex (verificado empiricamente em 10281851 e 1407880); `pips` e o
  campo numerico denso disponivel. Trades com `pips==0` (entradas pendentes)
  sao mantidos para preservar tamanho amostral T do PSR.
- **Sharpe annualization:** Sharpe per-trade × sqrt(N_trades_per_year).
  Como o cadencia varia, usar versao **per-trade** sem anualizacao para o
  MCPT (porque permutacao preserva N) e per-trade para o PSR (sr_benchmark=0
  e invariante a anualizacao). Documentar em docstring.
- **MCPT sign-flip:** preserva distribuicao marginal (heavy-tail), destroi
  sequencia. Citado em `[evidence_based_ta, p.325-328]`. n_permutations=2000
  default; seed=20260503.
- **PSR formula:**
  ```
  z = (SR - SR_b) * sqrt(T - 1) / sqrt(1 - skew*SR + (kurt-1)/4 * SR^2)
  p = 1 - Phi(z)
  ```
  com `kurt = scipy.stats.kurtosis(returns, fisher=False)` (kurtosis
  nao-Fisher, i.e. 3 para gaussiana — match com formula de AFML p.262).
- **Concentration top-5%:** `top5_abs_sum / abs(total_pnl)` onde `top5_abs_sum`
  e a soma dos 5% trades com maior `abs(pips)`. Threshold 0.50.
- **`is_live`:** parser do `system_info.json["account"]["account_type"]` —
  `"Real" -> True`, `"Demo" -> False`.

## Criterios de aceite (verificaveis)

1. `screen_system("10281851")` retorna `decision="GO"`, `k1_sanity_pass=True`,
   `is_live=True`, `mcpt_p < 0.05`, `psr_p < 0.05`, `concentration_top5 < 0.50`
2. `screen_system("11504701")` retorna `decision="STOP"` por
   `k1_sanity_pass=False` (martingale)
3. `screen_system("1407880")` retorna `is_live=False` mas `decision="GO"`
   (demo nao bloqueia)
4. 5 testes unitarios passam em < 30 s
5. Baseline 763 testes nao regride (testes pre-existentes mantidos)
6. `pre_decode_screen.json` schema documentado em docstring + exemplo serializado

## Kill-switches (a task FALHA se ocorrerem)

- MCPT p-value > 0.05 em 10281851 (gain +3,376%, MDD 11.7%, n=652) →
  bug provavel no calculo, investigar antes de DONE
- PSR p-value retorna NaN para input valido → bug numerico
- 11504701 retorna `decision="GO"` → bug critico no K1 wiring (deveria FAIL
  imediato por `k1_sanity_pass=False`)
- Quebra de qualquer teste pre-existente em `tests/` → reverter

## Allow-list de paths tocados

- `studies/myfxbook_reverse_engineering/shared/pre_decode_screen.py` (preenche)
- `tests/myfxbook_pipeline/test_pre_decode_screen.py` (preenche)
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/002-pre-decode-screen/**`
- `studies/myfxbook_reverse_engineering/v4_redesign/PROGRESS.md` (linha 002)
- `studies/myfxbook_reverse_engineering/v4_redesign/next_prompt.md` (rewrite)
- `jornada/2026-05-04-HHMM-myfxbook-v4-task-002.md` (entry de progresso) — opcional, conta como progresso

NADA fora dessa lista. Frozen rules e outras hunts intocadas.
