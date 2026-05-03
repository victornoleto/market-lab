# Decoding comparison report — system `10563761`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.62)
- Direction executor: `yaml_literal`
- Features used: ['bb_pos_20_2_H1']
- Entry hours UTC: [15, 16, 17, 18, 19, 20]
- Pairs: ['BTCUSD']
- Max holding hours: 1.5

## Decoding fidelity score: **0.2173** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0218 | 0.0054 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-25.0) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.8438 | 0.1688 |
| hold_similarity | 0.15 | 0.0036 | 0.0005 |
| count_ratio_proximity | 0.15 | 0.284 (ratio=5.7408) | 0.0426 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 436
- n_synthetic: 2503
- n_matched (±5min): 32
- entry_timing_precision: 0.0128
- entry_timing_recall: 0.0734
- entry_timing_f1: 0.0218
- direction_acc_at_matched: 0.8438
- hold_KS_stat: 0.9964
- hold_similarity: 0.0036
- count_ratio: 5.7408
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.3028
- hour_majority combined-hit rate: 0.3119
- pair_hour_majority combined-hit rate: 0.3119
- max_baseline: 0.3119
- synthetic combined-hit rate: 0.0619
- lift_vs_baseline_pp: -25.0

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).