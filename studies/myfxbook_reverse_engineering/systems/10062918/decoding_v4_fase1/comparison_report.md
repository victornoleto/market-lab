# Decoding comparison report — system `10062918`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.5)
- Direction executor: `yaml_literal`
- Features used: ['ema_dist_20_H4']
- Entry hours UTC: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
- Pairs: ['AUDUSD', 'EURCHF']
- Max holding hours: 960.0

## Decoding fidelity score: **0.0398** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0 | 0.0000 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-62.93) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.0 | 0.0000 |
| hold_similarity | 0.15 | 0.0506 | 0.0076 |
| count_ratio_proximity | 0.15 | 0.2148 (ratio=0.0793) | 0.0322 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 731
- n_synthetic: 58
- n_matched (±5min): 0
- entry_timing_precision: 0.0
- entry_timing_recall: 0.0
- entry_timing_f1: 0.0
- direction_acc_at_matched: nan
- hold_KS_stat: 0.9494
- hold_similarity: 0.0506
- count_ratio: 0.0793
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.4884
- hour_majority combined-hit rate: 0.5937
- pair_hour_majority combined-hit rate: 0.6293
- max_baseline: 0.6293
- synthetic combined-hit rate: 0.0
- lift_vs_baseline_pp: -62.93

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).