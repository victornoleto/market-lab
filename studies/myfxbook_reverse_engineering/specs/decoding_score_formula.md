# Spec — Decoding fidelity score 0-1 (Phase 5R-3)

**Status**: pré-registrada (frozen) em 2026-05-02 antes da implementação. Mudanças posteriores
invalidam scores já computados e exigem re-batch de todos os 52 systems.

**Origem**: `ROADMAP.md` Phase 5R-3 + autorização do usuário 2026-05-02 para incluir lift_vs_baseline
term + count_ratio_proximity formula explícita + NaN→0 convention.

---

## 1. Objetivo

Atribuir um score `[0, 1]` por system que mede **quão fielmente a regra Stage 2 (frozen_rules)
recupera os trades reais** quando aplicada como backtest sobre OHLC público (Dukascopy).

Score é uma das **três dimensões ortogonais** do estudo:

1. **Fidelidade de decodificação** (este score).
2. **Sanity / tradeable state** (`_diagnostics/sanity_flags.json`, flag DD<30%/p95<168h/gap<30d).
3. **Edge econômico** (Stage 3 proper, gates §2.4 PBO/DSR/WF/OOS bootstrap/cross-lib).

Score alto **não** implica edge nem tradeable. Disclaimer obrigatório no `DECODING_FIDELITY_RANKING.md`.

---

## 2. Inputs

Para cada system `i`, computar over `(pair, t)` no candidate window `W_i`
(definido em `specs/replicator_lite_pre_reg.md` §4.1):

| Termo | Origem | Range |
|---|---|---|
| `entry_timing_f1` | comparator §4.4 spec pre-reg | [0, 1] |
| `direction_acc_at_matched` | comparator | [0, 1], NaN se n_matched=0 |
| `hold_similarity` | `1 - KS_stat(synthetic_holds, real_holds)` | [0, 1], NaN se n<5 em qualquer lado |
| `count_ratio` | `n_synthetic / n_real` | (0, ∞), NaN se n_real=0 |
| `pnl_correlation` | Pearson PnL synthetic-vs-real em matched | [-1, 1], NaN se n_matched<5 |
| `lift_vs_baseline_pp` | `combined_hit_rate - max_baseline_hit_rate` (já em §4.5 pre-reg) | (-∞, ∞), em pp |

---

## 3. Fórmula final

```
fidelity_score = 0.25 × entry_timing_f1
              + 0.15 × baseline_lift_normalized
              + 0.20 × direction_acc_at_matched
              + 0.15 × hold_similarity
              + 0.15 × count_ratio_proximity
              + 0.10 × pnl_correlation_pos
clip([0, 1])
```

Pesos somam 1.00. Cada termo é mapeado para `[0, 1]` (ver §3.1-3.6) antes de combinar.

### 3.1 `entry_timing_f1` — peso 0.25

F1 padrão sobre matched `(synthetic ∩ real)` com tolerância ±5min e symbol-match.
Já em [0, 1]. NaN não ocorre se `n_synthetic > 0` (P=0/0=0 por convenção sklearn).
Se `n_synthetic=0`, F1 = 0 (regra que nunca dispara não tem timing).

Citação: F1 é métrica padrão para classificação binária com classe positiva rara
[evidence_based_ta, p.196-200] (precision-recall tradeoff em rule mining).

### 3.2 `baseline_lift_normalized` — peso 0.15 (NEW)

```
baseline_lift_normalized = clip(lift_vs_baseline_pp / 20, 0, 1)
```

System que bate o melhor baseline (always-buy / hour-majority / pair-hour-majority) em
**+20pp combined-hit-rate** ganha o termo cheio. +0pp ou negativo ganha 0.

**Justificativa**: sem este termo, uma regra trivial (e.g., always-buy à top-3 hour) atinge
F1≈0.6 + dir_acc=1.0 + hold_sim≈1.0 + count_ratio≈1.0 → score ~0.85, mas o "algoritmo
recuperado" não tem edge informacional sobre baseline. Aronson [evidence_based_ta, p.247-260]
trata explicitamente "data-mining bias" e a necessidade de comparar contra benchmark trivial
para distinguir regra real de coincidência.

Threshold de +20pp é heurístico. Calibrar pós-batch se distribuição empírica sugerir.

### 3.3 `direction_acc_at_matched` — peso 0.20

Acurácia Buy/Sell entre as `n_matched` entradas que coincidem ±5min.
Range [0, 1]. Convenção NaN: se `n_matched < 1`, termo = 0 (sem evidência → penaliza).
Se `n_matched ∈ [1, 4]`, termo é mantido mas marcado `low_confidence_dir=True` no JSON.

Citação: direction predictability é a primeira camada da hipótese de decodabilidade
[chan_quant_trading, ch.3] (mean reversion vs momentum direction).

### 3.4 `hold_similarity` — peso 0.15

```
hold_similarity = 1 - KS_stat(synthetic_holds_hours, real_holds_hours)
```

Two-sample Kolmogorov-Smirnov sobre durações de hold (em horas). Range [0, 1].
NaN quando `min(n_synthetic, n_real) < 5` → termo = 0.

**Por que KS, não Wasserstein**: KS é invariante a outliers de cauda (distribuições
de hold em FX têm caudas longas — trades stop-out vs target take-profit), enquanto
Wasserstein sobre-pesaria a cauda. Pardo [testing_tuning] usa distribution overlap
como sanity check de simulator vs live.

### 3.5 `count_ratio_proximity` — peso 0.15

```
def count_ratio_proximity(r):
    if r is NaN or r <= 0:
        return 0.0
    if 0.5 <= r <= 2.0:
        return 1.0
    return 1.0 / (1.0 + abs(math.log2(r)))
```

`r = n_synthetic / n_real`. Banda [0.5, 2.0] = pleno match (conta dentro de fator 2x).
Fora: decaimento simétrico log2 — `r=4` (over-fires 4x) → 0.33; `r=0.25` (under-fires 4x) → 0.33;
`r=8` ou `1/8` → 0.20; `r=16` ou `1/16` → 0.17.

Simetria em log-space é apropriada porque count_ratio é multiplicativo (a "metade" de erro
4x e 1/4x é a mesma magnitude direcional). Aronson [evidence_based_ta, p.367-380] discute
out-of-sample frequency-of-fire como signal de over-fitting quando `r >> 1`.

### 3.6 `pnl_correlation_pos` — peso 0.10

```
pnl_correlation_pos = clip(pearson(pnl_synthetic_matched, pnl_real_matched), 0, 1)
```

Pearson sobre PnL nas matched entries (synthetic PnL via OHLC sem custos vs real PnL
do trades.parquet). Negativo → 0 (anti-correlação não vale crédito). NaN se `n_matched < 5` → 0.

**Limitação conhecida**: PnL synthetic é sem custos; PnL real inclui spread/swap/commission.
Por isso peso baixo (0.10) e clip a 0. Stage 3 proper substitui esse termo por full cost model.
Mantido aqui como sanity check fraco (sinal positivo se sim, descarta se não).

Citação: Carver [systematic_trading, ch.4] discute equity-curve correlation entre paper e live
como diagnóstico de model drift; aplicável análogo synthetic vs real.

---

## 4. NaN convention (global)

Qualquer termo individual com NaN → **substituir por 0** antes de combinar.
Não renormalizar pesos (renormalização esconderia falta de evidência).

Sistema com `n_real_trades < 50`: marcar `low_n_flag=True` no JSON, mas computar score normalmente.
Sistema com `n_synthetic = 0` (regra nunca dispara): score = 0 trivialmente
(F1=0, lift=0, dir_acc=0 NaN→0, hold_sim=NaN→0, count_ratio=0, pnl_corr=NaN→0).

---

## 5. Bandas de fidelidade (heurísticas iniciais)

| Banda | Range | Interpretação |
|---|---|---|
| **HIGH** | `[0.80, 1.00]` | algoritmo recuperado com alta fidelidade. Candidato natural a 6R + Stage 3 (se sanity OK). |
| **MEDIUM** | `[0.60, 0.80)` | decodificação parcial. Investigar por system; pode ser feature pack incompleto. |
| **LOW** | `[0.40, 0.60)` | fraca. Algoritmo provavelmente usa features fora do feature pack atual (DXY, news, intermarket). Não justifica Stage 3. |
| **NONE** | `[0.00, 0.40)` | não decodificado. Algoritmo não recuperável de OHLC público sozinho. |

**Calibração pós-batch**: ajustar thresholds só se a distribuição empírica nos 52 systems
mostrar bimodalidade clara em outro ponto. Ajuste é mecânico (bandas), não da fórmula —
fórmula fica congelada.

---

## 6. Output `decoding_score.json` schema

```json
{
  "system_id": "10224499",
  "family_stage2": "LATE_NY_BREAKOUT",
  "model_used_stage2": "opus-4.7",
  "fidelity_score": 0.732,
  "score_band": "MEDIUM",
  "terms": {
    "entry_timing_f1": 0.612,
    "baseline_lift_normalized": 0.450,
    "lift_vs_baseline_pp": 9.0,
    "direction_acc_at_matched": 0.871,
    "hold_similarity": 0.682,
    "count_ratio_proximity": 1.000,
    "count_ratio": 1.32,
    "pnl_correlation_pos": 0.234,
    "pnl_correlation_raw": 0.234
  },
  "diagnostics": {
    "n_real": 221,
    "n_synthetic": 292,
    "n_matched": 87,
    "low_n_flag": false,
    "low_confidence_dir": false,
    "rule_executor": "tree_rank1"
  },
  "sanity_flag_orthogonal": {
    "tradeable_sanity_pass": false,
    "dd": 52.89,
    "p95_hold_h": 5.03,
    "max_gap_d": 41.05
  }
}
```

`sanity_flag_orthogonal` é repetido aqui por conveniência mas não entra no score —
preserva ortogonalidade.

---

## 7. Compliance / kill-switch

- Plano A DORMANT (mandate §1, §7). Score é research-only, sem capital.
- Citações obrigatórias preservadas (Regra 2 CLAUDE.md): `[advances_fin_ml ch.5]`,
  `[evidence_based_ta p.196-200, p.247-260, p.367-380]`, `[chan_quant_trading ch.3]`,
  `[testing_tuning]`, `[systematic_trading ch.4]`.
- Kill-switch 5R: se 0 systems atingem `fidelity_score ≥ 0.60`, encerra estudo
  como "decodificação não recuperável de OHLC público com pipeline atual" (ROADMAP linha 140).

---

## 8. Versão

`v1.0` — 2026-05-02. Frozen.
