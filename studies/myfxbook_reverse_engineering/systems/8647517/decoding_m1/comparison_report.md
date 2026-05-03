# Decoding comparison report — system `8647517`

- Family (Stage 2): **H1_MOMENTUM_GOLD**  (confidence 0.65)
- Direction executor: `yaml_literal`
- Features used: ['bb_pos_20_2_H1']
- Entry hours UTC: [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
- Pairs: ['XAUUSD']
- Max holding hours: 0.5

## Decoding fidelity score: **0.2135** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0231 | 0.0058 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-18.36) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.8812 | 0.1762 |
| hold_similarity | 0.15 | 0.032 | 0.0048 |
| count_ratio_proximity | 0.15 | 0.1778 (ratio=24.6729) | 0.0267 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 1024
- n_synthetic: 25265
- n_matched (±5min): 303
- entry_timing_precision: 0.012
- entry_timing_recall: 0.2959
- entry_timing_f1: 0.0231
- direction_acc_at_matched: 0.8812
- hold_KS_stat: 0.968
- hold_similarity: 0.032
- count_ratio: 24.6729
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.4189
- hour_majority combined-hit rate: 0.4443
- pair_hour_majority combined-hit rate: 0.4443
- max_baseline: 0.4443
- synthetic combined-hit rate: 0.2607
- lift_vs_baseline_pp: -18.36

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).