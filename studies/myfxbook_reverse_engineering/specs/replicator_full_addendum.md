# Spec — `replicator.py` full addendum (Phase 5R-1)

**Status**: pré-registrada (frozen) em 2026-05-02. Mudanças posteriores invalidam batch e
exigem re-run dos 52 systems.

**Origem**: addendum a `specs/replicator_lite_pre_reg.md` (que cobre case-control entry detection
no §4). Esta spec adiciona: rule executors completos (tree/RIPPER/YAML além de univariate),
backtest engine (entry → exit → PnL), schema `synthetic_trades.parquet`, e invariantes
anti-lookahead. O pre-reg permanece válido para a parte de entry detection; este addendum o estende
para gerar trades sintéticos comparáveis aos reais.

**Decisão upstream**: drop "lite" do nome — `shared/replicator_lite.py` → `shared/replicator.py`
com rewrite. Skeleton atual (544 linhas) tem boa base de candidate window + univariate executor
+ baselines, mas falta tree/RIPPER/YAML executors e backtest engine completo. Rewrite mantém as
funções utilitárias parseáveis (load_frozen_rule, build_candidate_window, label_entries, baselines).

---

## 1. Inputs (read-only)

Idênticos ao pre-reg §2. Reforço:

- `frozen_rules/<id>.md` é **read-only contract**. Tentar `open(... 'w')` deve raise.
- `systems/<id>/decoder/candidates.json` para extrair o `tree`/`ripper`/`univariate` rank-1.
- `data/ohlc/<pair>/M5/<YYYY-MM>.parquet` cache Dukascopy.

Replicator **não** escreve em `frozen_rules/`, `systems/<id>/decoder/`, `data/trades/`, `data/ohlc/`.
Escreve apenas em `systems/<id>/decoding/*` (subdir nova, separada de `decoder/` Stage 1+2).

---

## 2. Rule executors

A regra do `signal_rule.md` é parseada para uma das 4 formas. Tentar em ordem; primeiro que parsear
ganha (registrar `direction_executor` no output). Em todos os casos, features são computadas
pelo MESMO `shared/decoder_features.py:compute_entry_features()` usado em Stage 1 — sem
re-implementação.

### 2.1 `univariate` (já implementado)

`feat OP threshold ⇒ Direction`. Implementado em `_parse_univariate` do skeleton atual.
Mantido no rewrite.

### 2.2 `tree` (NEW)

Sklearn ASCII tree em `candidates.json[i]['rule_text']`:

```
|--- bb_pos_20_2_M15 <= 0.15
|   |--- ret_10_H1 <= 0.00
|   |   |--- class: 1
|   |--- ret_10_H1 >  0.00
|   |   |--- class: 1
|--- bb_pos_20_2_M15 >  0.15
|   |--- ret_10_M15 <= 0.00
|   |   |--- class: 0
```

Parser produz lista de paths `(conditions, leaf_class)` e mapeia `class:1` → primary_direction
(`Buy` ou `Sell` via inferência: classe majoritária na direção dos trades reais matched no
training do Stage 1; cair de volta a "rank-1 univariate" se ambíguo).

Apenas paths com `<=`, `<`, `>=`, `>` em features numéricas. Categóricas (e.g., `hour_utc == 23`)
ficam para v2 — RIPPER cobre o caso especial.

Implementação: parser linha-a-linha, indent-aware. Output = função
`predict_direction(feats: dict) -> Direction | "NA"` aplicada vetorialmente.

### 2.3 `ripper` (NEW)

Notação `[cond1 ∧ cond2] ∨ [cond3]`:

```
prior_bar_sign_H4 = -1 AND (ret_10_M15 < -0.00092 OR hour_utc == 23) ⇒ Sell
```

Parser:
1. Quebrar em cláusulas separadas por `∨` / `OR` (top-level).
2. Cada cláusula = AND de literals `feat OP value`.
3. Operadores suportados: `<`, `<=`, `>`, `>=`, `==`, `!=`.
4. Direction é `⇒ X` no fim da regra; default da outra direção é o complemento.

Igual ao tree: se parse falha, fallback para univariate rank-1.

### 2.4 `yaml_literal` (NEW — multi-clause)

Quando `signal_rule.md` `direction:` é prosa pseudo-Python:

```
BUY  if bb_pos_20_2_M15 <= 0.15
SELL otherwise
```

Parser linha-a-linha procura `^\s*(BUY|SELL)\s+if\s+(.+)$` e `^\s*(BUY|SELL)\s+otherwise\s*$`.
Múltiplas linhas `if` viram `elif` na ordem. Suporta `AND`/`OR` simples na expressão.

Se parse falha, fallback para tree rank-1 do `candidates.json`. Se tree também falha,
univariate rank-1.

### 2.5 Cascata e `direction_executor` flag

```
parsers = [yaml_literal, tree_rank1, ripper_rank1, univariate_rank1]
for p in parsers:
    if p.try_parse() succeeds:
        return executor with name p.__name__
raise NoParseable(system_id)
```

Output: `direction_executor` ∈ {`yaml_literal`, `tree_rank1`, `ripper_rank1`, `univariate_rank1`}
gravado no `decoding_score.json` para auditoria.

---

## 3. Backtest engine

### 3.1 Entry

Para cada `(pair, t) ∈ W_i` (candidate window do pre-reg §4.1):

1. Computar features OHLC[pair][t-lookback : t-1] via `compute_entry_features()`.
   **Lookback termina em `t-1`** (sem lookahead — não usar OHLC[t]).
2. Aplicar rule executor → `predicted_direction ∈ {Buy, Sell, NA}`.
3. Se `NA` (feature missing por gap OHLC), pular candidato.
4. Senão, gerar trade sintético com:
   - `entry_ts = t` (M5 bar open)
   - `entry_price = OHLC[pair][t].open`
   - `symbol = pair`
   - `action = predicted_direction`
   - `lots = 0.01` (fixed; sizing é Stage 3 territory)

### 3.2 Exit

```
exit_ts = entry_ts + Timedelta(hours=max_holding_hours)
```

`max_holding_hours` vem do YAML front-matter de `frozen_rules/<id>.md`.
Se ausente: default `24` horas (justifica como "intraday" mas marca `default_exit=True`
no diagnostic).

`exit_price = OHLC[pair][exit_ts].open` (sem stop-loss / take-profit no v1; Stage 3 modela).

Ajuste de fim de dataset: se `exit_ts > last_OHLC_ts`, truncar para `last_OHLC_ts` e marcar
`exit_truncated=True`.

### 3.3 PnL

```
pip_value = pip_value_for_pair(pair)  # 0.0001 para FX major; 0.01 para JPY pairs; etc.

if action == "Buy":
    pips = (exit_price - entry_price) / pip_value
else:  # Sell
    pips = (entry_price - exit_price) / pip_value

profit_per_lot_usd = pips * pip_value_usd_per_pip(pair)  # standard convention
profit = profit_per_lot_usd * lots  # = 0.01 lot fixo
```

**Sem custos** no v1 (sem spread, sem swap, sem comissão). Stage 3 proper modela. Esta
escolha está no ROADMAP linha 92 e no espírito do pre-reg.

`pip_value_for_pair` e `pip_value_usd_per_pip` são tabelas estáticas em `shared/pip_table.py`
(criar). FX majors = 0.0001 / $10 per pip per std lot. JPY = 0.01 / $9.30 per pip
(approx; OK porque Pearson de PnL não depende de escala absoluta; só do ranking relativo).

Citação: convenção pip-value padrão de FX [evidence_based_ta, p.367-380] (FX session/contract structure).

### 3.4 Schema `synthetic_trades.parquet`

Compatível com `data/trades/<id>/trades.parquet` (subconjunto de colunas) para o
comparator §4 reaproveitar lógica:

| Coluna | Tipo | Origem |
|---|---|---|
| `record` | str | `f"synth_{system_id}_{pair}_{i}"` |
| `symbol` | str | pair |
| `action` | str | "Buy" / "Sell" |
| `lots` | float64 | 0.01 |
| `open_price` | float64 | OHLC entry open |
| `close_price` | float64 | OHLC exit open |
| `pips` | float64 | computed §3.3 |
| `profit` | float64 | computed §3.3 |
| `open_dt_utc` | datetime64[ns, UTC] | `entry_ts` |
| `close_dt_utc` | datetime64[ns, UTC] | `exit_ts` |
| `duration_sec` | float64 | `(close - open).total_seconds()` |
| `is_trade` | bool | `True` |
| `is_deposit` | bool | `False` |
| `direction_executor` | str | name of rule executor used |
| `exit_truncated` | bool | `True` se exit_ts foi clipped |

`record` tem prefixo `synth_` para impedir confusão com `record` real (que é integer).

### 3.5 Invariantes anti-lookahead (verificadas em smoke test)

1. **No future bar in features**: `compute_entry_features(pair, t)` lê apenas OHLC[pair][< t].
   Verificar via `assert max(feature_window_ts) < t`.
2. **Exit price post-hoc**: `exit_price` lido em `exit_ts` (que pode ser futuro do entry); OK
   porque é a mecânica de holding period — não vaza para a decisão de entry.
3. **Frozen rule não é re-fitada**: assert que `frozen_rules/<id>.md` e
   `systems/<id>/decoder/candidates.json` não foram tocados pós-pre-reg
   (mtime check vs `_diagnostics/freeze_timestamp.txt` — criar nessa rodada).
4. **Candidate window definido pré-execução**: `H_i` (entry hours) congelado em
   `_diagnostics/freeze_window.json` no início do batch e re-checado por system. Recompute
   diferente → raise.

---

## 4. Comparator (5R-2 — overlap com `decoding_score_formula.md`)

Implementado em `shared/comparator.py` (NEW).

Para cada system `i`, par `p`:

```
matches = match_within_5min(synthetic_trades_i_p, real_trades_i_p)
# match: same symbol, |open_dt_utc_diff| <= 5min, direction-agnostic for entry_timing
```

Métricas:

| Métrica | Fórmula | Notes |
|---|---|---|
| `entry_timing_precision` | matches / n_synthetic | NaN-safe: 0/0 → 0 |
| `entry_timing_recall` | matches / n_real | 0/0 → 0 |
| `entry_timing_f1` | 2·P·R/(P+R) | 0 quando P=R=0 |
| `direction_acc_at_matched` | acc(direction) entre matches | NaN se matches=0 |
| `hold_KS_stat` | scipy.stats.ks_2samp(synth_holds, real_holds).statistic | NaN se min<5 |
| `hold_similarity` | `1 - hold_KS_stat` |  |
| `count_ratio` | n_synth / n_real | NaN se n_real=0 |
| `pnl_correlation` | scipy.stats.pearsonr(synth_pnl_matched, real_pnl_matched).statistic | NaN se matches<5 |
| `lift_vs_baseline_pp` | inherited from pre-reg §4.5 | já existe no skeleton |

Per-pair + agregado por system (weighted by `n_real_pair`).

Output: `systems/<id>/decoding/comparison_report.md` (humano) + `comparison_metrics.json` (parseable).

---

## 5. Smoke test obrigatório (5R-1b)

Antes do batch 52: rodar replicator em `10224499` apenas. Validar:

1. **Schema**: `synthetic_trades.parquet` lê via pandas, colunas conforme §3.4.
2. **Sanity counts**: `0.5 ≤ count_ratio ≤ 5.0` (banda ampla; só pega bug grosseiro).
3. **Entry hours coverage**: `synthetic_trades['open_dt_utc'].dt.hour.unique()` ⊆ `entry_hours_utc`
   da regra. Violation = bug.
4. **Direction sanity**: se `entry_timing_f1 > 0.3`, então `direction_acc_at_matched ≥ 0.4`
   (regra Bollinger BB do 10224499 deve ter direção razoável). Violation = bug no executor.
5. **No-lookahead**: rodar com OHLC truncado em `entry_ts - 1 minute` para o feature compute;
   resultado deve ser idêntico ao baseline. Se diferente → lookahead bug.
6. **Frozen integrity**: assert `frozen_rules/10224499.md` mtime == frozen mtime.

Bug-fix antes de escalar. Smoke test produz `_diagnostics/smoke_10224499.md` documentando
PASS/FAIL de cada invariante.

---

## 6. Batch driver

`scripts/run_replicator_batch.py` (NEW):

```
for system_id in all_52_systems:
    try:
        rule = load_frozen_rule(system_id, base_dir)
        window = build_candidate_window(rule, trades_i)
        synth_trades = run_backtest(rule, window, ohlc_loader)
        synth_trades.to_parquet(f"systems/{system_id}/decoding/synthetic_trades.parquet")
        report = comparator.compare(synth_trades, trades_i)
        write_comparison_report(report, f"systems/{system_id}/decoding/")
        score = score_formula.compute(report)
        write_score_json(score, f"systems/{system_id}/decoding/decoding_score.json")
    except Exception as e:
        log_failure(system_id, e)
        continue
```

Falhas individuais → log + continue. Não param o batch. Output `_diagnostics/batch_summary.json`
com `{passed, failed: {id: error}, n_total}`.

---

## 7. Citações obrigatórias (Regra 2 CLAUDE.md)

- `[advances_fin_ml, ch.5]` — feature importance + clustered MDA (já no skeleton)
- `[evidence_based_ta, p.367-380]` — session/hour FX regime + pip convention (já no skeleton)
- `[evidence_based_ta, p.247-260]` — data-mining bias / baseline lift (NEW pra score formula)
- `[chan_quant_trading, ch.3]` — direction predictability (NEW)
- `[testing_tuning]` — KS distribution comparison para sim-vs-live (NEW)
- `[systematic_trading, ch.4]` — equity-curve correlation diagnostic (NEW)
- `[advances_fin_ml, p.196-211]` — DSR/PBO downstream Stage 3 (mantido)

---

## 8. Compliance mandate market-lab

- Plano A DORMANT (mandate §1, §7) continua. Replicator é research-only.
- Pass em 5R **não** autoriza Plano A; apenas Stage 3 proper (Phase 8) que herda gates §2.4.
- Sanity flag (`tradeable_sanity_pass`) é **ortogonal** ao score; não exclui systems do batch
  (consenso `007-opus.md`), mas bloqueia downstream paper trading mesmo se Stage 3 passar.

---

## 9. Versão

`v1.0` — 2026-05-02. Frozen.
