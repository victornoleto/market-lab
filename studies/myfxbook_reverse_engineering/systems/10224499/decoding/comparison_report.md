# Decoding comparison report — system `10224499`

- Family (Stage 2): **LATE_NY_BREAKOUT**  (confidence 0.72)
- Direction executor: `yaml_literal`
- Features used: ['bb_pos_20_2_M15']
- Entry hours UTC: [0, 22, 23]
- Pairs: ['USDCAD', 'EURUSD', 'GBPUSD']
- Max holding hours: 5.0

## Decoding fidelity score: **0.2524** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0039 | 0.0010 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-57.92) | 0.0000 |
| direction_acc_at_matched | 0.20 | 1.0 | 0.2000 |
| hold_similarity | 0.15 | 0.0592 | 0.0089 |
| count_ratio_proximity | 0.15 | 0.2265 (ratio=10.6697) | 0.0340 |
| pnl_correlation_pos | 0.10 | 0.0859 (raw=0.0859) | 0.0086 |

## Comparison details

- n_real: 221
- n_synthetic: 2358
- n_matched (±5min): 5
- entry_timing_precision: 0.0021
- entry_timing_recall: 0.0226
- entry_timing_f1: 0.0039
- direction_acc_at_matched: 1.0
- hold_KS_stat: 0.9408
- hold_similarity: 0.0592
- count_ratio: 10.6697
- pnl_correlation: 0.0859

### Baseline comparison

- always_buy combined-hit rate: 0.4842
- hour_majority combined-hit rate: 0.5385
- pair_hour_majority combined-hit rate: 0.6018
- max_baseline: 0.6018
- synthetic combined-hit rate: 0.0226
- lift_vs_baseline_pp: -57.92

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).