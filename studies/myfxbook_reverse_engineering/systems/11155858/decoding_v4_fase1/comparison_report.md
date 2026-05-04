# Decoding comparison report — system `11155858`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.3)
- Direction executor: `tree_rank1`
- Features used: ['ret_1_H4']
- Entry hours UTC: [12, 13, 14, 15, 16, 17, 18, 19, 20]
- Pairs: ['EURGBP']
- Max holding hours: 120.0

## Decoding fidelity score: **0.4004** (LOW)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.066 | 0.0165 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-63.45) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.8 | 0.1600 |
| hold_similarity | 0.15 | 0.4924 | 0.0739 |
| count_ratio_proximity | 0.15 | 1.0 (ratio=0.5381) | 0.1500 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 197
- n_synthetic: 106
- n_matched (±5min): 10
- entry_timing_precision: 0.0943
- entry_timing_recall: 0.0508
- entry_timing_f1: 0.066
- direction_acc_at_matched: 0.8
- hold_KS_stat: 0.5076
- hold_similarity: 0.4924
- count_ratio: 0.5381
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.6701
- hour_majority combined-hit rate: 0.6751
- pair_hour_majority combined-hit rate: 0.6751
- max_baseline: 0.6751
- synthetic combined-hit rate: 0.0406
- lift_vs_baseline_pp: -63.45

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: PASS
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).