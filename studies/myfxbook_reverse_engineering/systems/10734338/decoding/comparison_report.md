# Decoding comparison report — system `10734338`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.5)
- Direction executor: `yaml_literal`
- Features used: ['bb_pos_20_2_H1']
- Entry hours UTC: [15, 16, 17, 18]
- Pairs: ['BTCUSD']
- Max holding hours: 2.0

## Decoding fidelity score: **0.2385** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0197 | 0.0049 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-19.97) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.8636 | 0.1727 |
| hold_similarity | 0.15 | 0.0023 | 0.0003 |
| count_ratio_proximity | 0.15 | 0.4033 (ratio=2.7885) | 0.0605 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 591
- n_synthetic: 1648
- n_matched (±5min): 22
- entry_timing_precision: 0.0133
- entry_timing_recall: 0.0372
- entry_timing_f1: 0.0197
- direction_acc_at_matched: 0.8636
- hold_KS_stat: 0.9977
- hold_similarity: 0.0023
- count_ratio: 2.7885
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.2284
- hour_majority combined-hit rate: 0.2318
- pair_hour_majority combined-hit rate: 0.2318
- max_baseline: 0.2318
- synthetic combined-hit rate: 0.0321
- lift_vs_baseline_pp: -19.97

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: PASS
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).