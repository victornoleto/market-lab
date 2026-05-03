# Decoding comparison report — system `11206045`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.38)
- Direction executor: `yaml_literal`
- Features used: ['ret_10_H4']
- Entry hours UTC: [0]
- Pairs: ['GBPJPY']
- Max holding hours: 168.0

## Decoding fidelity score: **0.2992** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0067 | 0.0017 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-53.77) | 0.0000 |
| direction_acc_at_matched | 0.20 | 1.0 | 0.2000 |
| hold_similarity | 0.15 | 0.2123 | 0.0318 |
| count_ratio_proximity | 0.15 | 0.4377 (ratio=0.4104) | 0.0657 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 212
- n_synthetic: 87
- n_matched (±5min): 1
- entry_timing_precision: 0.0115
- entry_timing_recall: 0.0047
- entry_timing_f1: 0.0067
- direction_acc_at_matched: 1.0
- hold_KS_stat: 0.7877
- hold_similarity: 0.2123
- count_ratio: 0.4104
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.5425
- hour_majority combined-hit rate: 0.5425
- pair_hour_majority combined-hit rate: 0.5425
- max_baseline: 0.5425
- synthetic combined-hit rate: 0.0047
- lift_vs_baseline_pp: -53.77

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).