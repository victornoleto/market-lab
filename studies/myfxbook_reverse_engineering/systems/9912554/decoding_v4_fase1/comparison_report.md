# Decoding comparison report — system `9912554`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.3)
- Direction executor: `yaml_literal`
- Features used: ['ret_10_H1']
- Entry hours UTC: [12, 13, 14, 15, 16, 17, 18, 19, 20]
- Pairs: ['EURGBP']
- Max holding hours: 4930.81

## Decoding fidelity score: **0.0246** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0 | 0.0000 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-53.4) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.0 | 0.0000 |
| hold_similarity | 0.15 | 0.0 | 0.0000 |
| count_ratio_proximity | 0.15 | 0.1639 (ratio=0.0291) | 0.0246 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 103
- n_synthetic: 3
- n_matched (±5min): 0
- entry_timing_precision: 0.0
- entry_timing_recall: 0.0
- entry_timing_f1: 0.0
- direction_acc_at_matched: nan
- hold_KS_stat: nan
- hold_similarity: nan
- count_ratio: 0.0291
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.534
- hour_majority combined-hit rate: 0.534
- pair_hour_majority combined-hit rate: 0.534
- max_baseline: 0.534
- synthetic combined-hit rate: 0.0
- lift_vs_baseline_pp: -53.4

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).