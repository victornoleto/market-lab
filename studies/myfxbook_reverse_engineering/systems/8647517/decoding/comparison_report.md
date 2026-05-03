# Decoding comparison report — system `8647517`

- Family (Stage 2): **H1_MOMENTUM_GOLD**  (confidence 0.65)
- Direction executor: `yaml_literal`
- Features used: ['bb_pos_20_2_H1']
- Entry hours UTC: [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
- Pairs: ['XAUUSD']
- Max holding hours: 0.5

## Decoding fidelity score: **0.2141** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0232 | 0.0058 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-18.07) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.8878 | 0.1776 |
| hold_similarity | 0.15 | 0.0269 | 0.0040 |
| count_ratio_proximity | 0.15 | 0.178 (ratio=24.5459) | 0.0267 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 1024
- n_synthetic: 25135
- n_matched (±5min): 303
- entry_timing_precision: 0.0121
- entry_timing_recall: 0.2959
- entry_timing_f1: 0.0232
- direction_acc_at_matched: 0.8878
- hold_KS_stat: 0.9731
- hold_similarity: 0.0269
- count_ratio: 24.5459
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.418
- hour_majority combined-hit rate: 0.4434
- pair_hour_majority combined-hit rate: 0.4434
- max_baseline: 0.4434
- synthetic combined-hit rate: 0.2627
- lift_vs_baseline_pp: -18.07

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).