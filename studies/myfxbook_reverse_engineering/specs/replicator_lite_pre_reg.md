# Replicator-lite — Pré-registro (Etapa 1 + Etapa 2)

**Status**: pré-registrado (frozen) em 2026-05-02 antes da implementação. Mudanças posteriores requerem novo round adversarial e invalidam métricas já computadas.

**Origem**: consenso fechado em `adversarial_chat/001..007-*.md`. Esta spec é a versão executável da "Lista consensuada finalíssima" de `005-opus.md` + `006-gpt.md` sign-off + `007-opus.md` micro-ajuste sanity-flags.

---

## 1. Objetivo

Medir **replicabilidade** (não decodabilidade nem edge econômico) das `frozen_rules/<id>.md` produzidas pelo Stage 2 contra os trades reais dos systems HappyForex, usando case-control entry detection com baselines triviais.

Pass em Etapa 1 + Etapa 2 autoriza apenas **Stage 3 proper** (PnL replicator com gates §2.4) — **não** autoriza paper trading, sizing real, ou qualquer alocação de capital. Todos os outputs carregam disclaimer literal.

---

## 2. Inputs (read-only)

| Arquivo | Conteúdo | Uso |
|---|---|---|
| `frozen_rules/<id>.md` | YAML front-matter Stage 2 + narrativa | source-of-truth da regra |
| `systems/<id>/decoder/candidates.json` | top-10 candidates (tree/ripper/univariate) | direction executor (ver §4.3) |
| `systems/<id>/decoder/fingerprint.md` | top-3 hours, pairs, EDA | candidate window definition |
| `data/trades/<id>/trades.parquet` | trades reais com `open_dt_utc` (real UTC, validado em `_diagnostics/broker_time_check.md`) | events ground truth |
| `data/ohlc/<pair>/M5/<YYYY-MM>.parquet` | Dukascopy M5 bars real UTC | candidate window bars |

Replicator-lite **não pode escrever em** `frozen_rules/`, `systems/<id>/decoder/`, `data/trades/`, `data/ohlc/`. Tentativa de re-mineração ou re-fit invalida o pré-registro.

---

## 3. Universo

**Etapa 1**: top-10 DECODED de `ranking/OVERNIGHT_VALIDATION_REPORT.md` pós-relabel, ordenados por reliability:

| # | system_id | family | n | acct | flag |
|---:|---|---|---:|---|---|
| 1 | 10224499 | LATE_NY_BREAKOUT | 221 | Real | `low_n=False`, sanity DD-fail |
| 2 | 11171596 | NY_SESSION_REVERSAL | 1083 | Real | sanity OK |
| 3 | 11155858 | FACTOR_SCALPING | 197 | Real | `low_n=True`, sanity DD-fail |
| 4 | 8647517 | FACTOR_SCALPING | 1024 | Real | sanity OK |
| 5 | 2421356 | FACTOR_SCALPING | 1763 | Demo | sanity OK |
| 6 | 10281851 | OVERLAP_NY_LONDON_RANGE | 652 | Real | sanity OK |
| 7 | 9912554 | OVERLAP_NY_LONDON_RANGE | 103 | Real | `low_n=True`, sanity DD-fail |
| 8 | 11207608 | FACTOR_SCALPING | 202 | Real | sanity DD-fail |
| 9 | 11628637 | FACTOR_SCALPING | 232 | Real | sanity OK |
| 10 | 9375654 | NY_SESSION_REVERSAL | 915 | Real | sanity OK |

Sanity flags são informativos (não excluem do teste — ver `007-opus.md` micro-ajuste).

**Etapa 2 par primário** (decisivo): `1407880` → `10224499` (mesma família LATE_NY_BREAKOUT).
**Etapa 2 par diagnóstico** (não decisivo): `2373850` → `11171596` (famílias divergem).

---

## 4. Procedimento Etapa 1 (replicator-lite case-control)

### 4.1 Candidate window por system

Para cada system `i`:

```
W_i = { (pair p, bar M5 t) :
        p ∈ pairs_i (do trades.parquet, distintos)
        AND hour(t) ∈ H_i
        AND t ∈ [first_trade_date_i, last_trade_date_i]
        AND OHLC[p][t] existe (Dukascopy)
}
```

Onde `H_i` é definido **antes de medir métricas** por uma das duas regras (em ordem de preferência):

1. Se `frozen_rules/<id>.md` declara `entry_window_utc: [HH:MM, HH:MM]`, expandir para conjunto de horas inteiras (ex: `["22:00", "00:59"]` → `H_i = {22, 23, 0}`).
2. Senão, top-3 hours de `fingerprint.md` "Top entry hours (UTC)".

`H_i` é congelado antes da execução. **Não retunar** se métricas ruins.

### 4.2 Ground-truth labels

Para cada `(p, t) ∈ W_i`:

```
y_entry(p, t)  = 1 se ∃ trade real em system i com symbol=p e open_dt_utc ∈ [t, t+5min)
               = 0 caso contrário

y_direction(p, t) = 'Buy' / 'Sell' / 'NA' (NA quando y_entry=0)
```

### 4.3 Direction rule executor (v1)

A regra de direção é executada usando **o candidate citado como primary pela `signal_rule.md`** em `frozen_rules/<id>.md`:

- Se signal_rule cita explicitamente um candidate rank do `candidates.json` (e.g., "rank 1 tree"), usar essa regra.
- Se signal_rule cita feature + threshold (e.g., `bb_pos_20_2_M15 <= 0.15 → BUY; else SELL`), parsear como single-feature rule.
- Se signal_rule é multi-clause (e.g., 4 condições aninhadas no `direction:`), usar o **tree rank-1** do candidates.json (estruturado, parseável).
- Se nenhum dos acima, usar **univariate rank-1** do candidates.json (sempre parseável: `feat OP threshold ⇒ Direction`).

Para cada `(p, t) ∈ W_i`, computar `pred_direction(p, t)` aplicando a regra contra features extraídas de OHLC[p][t-lookback : t]. Features computadas EXATAMENTE como em `shared/decoder_features.py` (mesmo código, sem re-implementação).

**Flag de transparência**: se a regra usada não for a YAML literal, marcar `direction_executor='top1_univariate'` ou `direction_executor='tree_rank1'` no output.

### 4.4 Métricas (por system × por par + agregadas)

Para cada system `i`, par `p` (e agregado ponderado por `n_trades_pair`):

| Métrica | Fórmula |
|---|---|
| `n_window_bars` | \|W_i ∩ {par=p}\| |
| `n_actual_entries` | Σ y_entry |
| `n_predicted_entries` | Σ 𝟙(rule fires) |
| `predicted_actual_ratio` | n_predicted / max(n_actual, 1) |
| `entry_precision` | TP / (TP + FP) — TP=rule-fires AND real entry within ±5min |
| `entry_recall` | TP / (TP + FN) — FN=real entry mas rule não dispara |
| `entry_f1` | 2·P·R / (P+R) |
| `fp_per_day` | FP / (n_days no window) |
| `direction_accuracy_on_predicted` | acertos de Buy/Sell entre TPs |
| `direction_acc_ci95` | Wilson 95% CI binomial |
| `combined_hit` | TP AND symbol-match AND direction-match | **métrica primária** |
| `combined_hit_ci95` | Wilson 95% CI |
| `lift_vs_baseline` | (combined_hit_rate - max_baseline_hit_rate) em pp |

### 4.5 Baselines triviais (mandatórios)

Os três rodam no MESMO `W_i`:

1. **always-buy-by-pair**: `pred_direction = 'Buy'` em todo `(p, t)`. Entry sempre dispara.
2. **hour-majority**: `pred_direction = direção majoritária no histórico do system para hour(t)`. Entry sempre dispara.
3. **pair-hour-majority**: `pred_direction = direção majoritária para (pair, hour) específica`. Entry sempre dispara.

`max_baseline_hit_rate = max(combined_hit_rate dos 3)`.

### 4.6 Thresholds (consenso 005/006)

| Banda | Critério |
|---|---|
| **Fail** | `lift_vs_baseline ≤ +5pp` **OU** `predicted_actual_ratio > 3.0` |
| **Borderline** | `+5pp < lift_vs_baseline < +10pp` |
| **Pass** | `lift_vs_baseline ≥ +10pp` **AND** `predicted_actual_ratio ≤ 3.0` **AND** combined-hit CI95 lower > max_baseline_hit_rate |

A condição "CI95 lower > max_baseline_hit_rate" garante que o lift é estatisticamente material, não amostral.

### 4.7 Saídas

`replicator_lite_results.csv` com 1 linha por `(system, pair_or_aggregate)`:

```
system_id, pair, family, n_trades_pair, n_window_bars,
entry_precision, entry_recall, entry_f1, fp_per_day,
predicted_actual_ratio, direction_accuracy, direction_acc_ci95_low, direction_acc_ci95_high,
combined_hit_rate, combined_hit_ci95_low, combined_hit_ci95_high,
baseline_always_buy, baseline_hour_majority, baseline_pair_hour_majority,
max_baseline, lift_vs_baseline_pp, banda, low_n_flag, sanity_flag, direction_executor
```

`replicator_lite_memo.md`: 1 parágrafo por system com decisão (Pass/Borderline/Fail) e razão.

### 4.8 Kill-switch

Se 0 systems atingirem `Pass` no agregado: estudo encerra como "decodabilidade encontrada, replicabilidade não demonstrada". Sem Etapa 2, sem Stage 3, sem Opus, sem paper. `jornada/` entry final cobre isso.

---

## 5. Procedimento Etapa 2 (frozen-rule cross-system)

### 5.1 Par primário: 1407880 (OLD HMH v2.3.1) → 10224499 (HMH FM REAL)

**Ajuste no OLD** (`1407880`):
- Usar `frozen_rules/1407880.md` (regra Stage 2) como fonte; **sem re-mining**.
- Se a regra precisar de threshold ajustado às features de 1407880, usar purged k-fold **só** em 1407880 (5 folds, embargo=5 trades) — replica o que Stage 1 já fez. **Apenas** o threshold pode ser fitado dentro do range já existente em `candidates.json` rank-1; nenhum feature novo, nenhum miner novo.

**Teste no NEW** (`10224499`):
- Aplicar regra congelada do OLD diretamente nas features de 10224499.
- Sem peek nas features de 10224499 durante o ajuste.
- Sem re-fit, sem re-tuning.

**Métricas**:
- `hit_rate_pm1min`, `hit_rate_pm5min`, `hit_rate_pm15min` com Wilson CI95.
- `direction_accuracy_at_hit` com Wilson CI95.
- `n_predicted_NEW`, `n_actual_NEW`, ratio.

### 5.2 Thresholds par primário (consenso 005/006)

| Banda | Critério |
|---|---|
| **Strong pass** | `hit_rate_pm5min ≥ 50%` **AND** `direction_accuracy ≥ 60%` |
| **Weak pass** | `hit_rate_pm15min ≥ 50%` **AND** `direction_accuracy ≥ 58%` |
| **Borderline** | `40% ≤ hit_rate_pm15min < 50%` **OU** `55% ≤ direction_accuracy < 58%` |
| **Fail** | `hit_rate_pm15min < 40%` **OU** `direction_accuracy < 55%` |

### 5.3 Decomposição de falha (obrigatória se Fail)

Se par primário Fail, decompor em 3 hipóteses concorrentes:

1. **Algoritmo mudou**: contar fração de features do OLD que ainda são distribucionalmente similares no NEW (KS test por feature, p<0.05 → distrib mudou).
2. **Regime mudou**: comparar volatilidade realizada (ATR percentile) entre janelas OLD e NEW para o mesmo par-hora.
3. **Sem replicabilidade**: residual após excluir 1 e 2.

Reportar fração atribuída a cada hipótese.

### 5.4 Par diagnóstico: 2373850 → 11171596

Mesmo protocolo, sem decomposição de falha obrigatória. Famílias já divergem (UNCATEGORIZED vs NY_SESSION_REVERSAL); resultado é informativo, não decisivo.

### 5.5 Saída

`frozen_rule_test.md` com:
- Resultado par primário (banda + métricas + CI).
- Resultado par diagnóstico.
- Decomposição de falha (se aplicável).
- Recomendação de próxima etapa (Stage 3 sim/não).

---

## 6. Procedimento Etapa 3 (decisão)

| Cenário | Ação |
|---|---|
| Etapa 1 Pass ≥ 1 system AND Etapa 2 par primário Strong/Weak Pass | Stage 3 proper apenas para top 1-3 systems Pass. Spec separado. |
| Etapa 1 Pass ≥ 1 system AND Etapa 2 par primário Borderline | Stage 3 apenas para system(s) Etapa 1 Pass, com asterisco metodológico. |
| Etapa 1 Pass = 0 OU Etapa 2 par primário Fail | Encerrar estudo. Documentar como "decodabilidade demonstrada, replicabilidade não". Sem Stage 3, sem Opus, sem paper. |

Output: única `jornada/2026-05-XX-XXXX-myfxbook-reverse-eng-replicabilidade-{result}.md` cobrindo Etapas 0-3.

---

## 7. Defer absoluto (não fazer agora)

- Path B Opus re-review (~$10).
- Path C Stage 3 proper (1-2 dias).
- RuleFit / Bayesian Rule Lists / Optimal Sparse Decision Trees.
- White's Reality Check / SPA test.
- Features novas (DXY, Asian range, news flags, broker server-time variants).
- Agregação Happy Gold cohort (8 systems pooled).

Qualquer um desses, se desejado depois, requer novo round adversarial.

---

## 8. Compliance com mandate ai-trade

- Plano A está DORMANT (mandate §1, §7). Replicator-lite é **research-only**, sem capital allocation.
- Citações obrigatórias preservadas no `signal_rule.md` original (Aronson, López de Prado, Chan, Carver) — replicator-lite não cita nada novo, apenas opera sobre as regras citadas.
- Pass em Etapa 1+2 NÃO autoriza reativação de Plano A — apenas Stage 3 proper.
- Stage 3, se rodar, herda gates §2.4 hard-block (PBO<0.5, DSR p<0.05, WF≥6/8, OOS bootstrap 99.9% CI > 0, cross-lib ±3pp).

---

## 9. Checklist de execução

- [x] Diagnóstico broker server-time (`_diagnostics/broker_time_check.md`) — PASS
- [x] `frozen_rules/` populada (12 regras, read-only)
- [x] Spec pré-registrada (este arquivo)
- [ ] Etapa 0 — relabel + sanity flags em `OVERNIGHT_VALIDATION_REPORT.md`
- [ ] Etapa 1 — `replicator_lite.py` + `replicator_lite_results.csv` + memo
- [ ] Etapa 2 — `frozen_rule_test.md`
- [ ] Etapa 3 — decisão + única `jornada/` entry
