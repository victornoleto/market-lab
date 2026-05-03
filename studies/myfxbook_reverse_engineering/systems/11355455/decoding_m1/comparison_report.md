# Decoding comparison report — system `11355455`

- Family (Stage 2): **H1_MOMENTUM_GOLD**  (confidence 0.7)
- Direction executor: `yaml_literal`
- Features used: ['bb_pos_20_2_H1']
- Entry hours UTC: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
- Pairs: ['XAUUSD']
- Max holding hours: 0.5

## Decoding fidelity score: **0.2153** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0176 | 0.0044 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-19.07) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.9265 | 0.1853 |
| hold_similarity | 0.15 | 0.004 | 0.0006 |
| count_ratio_proximity | 0.15 | 0.1669 (ratio=31.822) | 0.0250 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 236
- n_synthetic: 7510
- n_matched (±5min): 68
- entry_timing_precision: 0.0091
- entry_timing_recall: 0.2881
- entry_timing_f1: 0.0176
- direction_acc_at_matched: 0.9265
- hold_KS_stat: 0.996
- hold_similarity: 0.004
- count_ratio: 31.822
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.4237
- hour_majority combined-hit rate: 0.4576
- pair_hour_majority combined-hit rate: 0.4576
- max_baseline: 0.4576
- synthetic combined-hit rate: 0.2669
- lift_vs_baseline_pp: -19.07

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).