# Decoding comparison report — system `10192401`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.55)
- Direction executor: `yaml_literal`
- Features used: ['bb_pos_20_2_H1']
- Entry hours UTC: [15, 16, 17, 18]
- Pairs: ['BTCUSD']
- Max holding hours: 4.5

## Decoding fidelity score: **0.3589** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0058 | 0.0014 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-22.86) | 0.0000 |
| direction_acc_at_matched | 0.20 | 1.0 | 0.2000 |
| hold_similarity | 0.15 | 0.05 | 0.0075 |
| count_ratio_proximity | 0.15 | 1.0 (ratio=1.4619) | 0.1500 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 420
- n_synthetic: 614
- n_matched (±5min): 3
- entry_timing_precision: 0.0049
- entry_timing_recall: 0.0071
- entry_timing_f1: 0.0058
- direction_acc_at_matched: 1.0
- hold_KS_stat: 0.95
- hold_similarity: 0.05
- count_ratio: 1.4619
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.2024
- hour_majority combined-hit rate: 0.2357
- pair_hour_majority combined-hit rate: 0.2357
- max_baseline: 0.2357
- synthetic combined-hit rate: 0.0071
- lift_vs_baseline_pp: -22.86

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: PASS
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).