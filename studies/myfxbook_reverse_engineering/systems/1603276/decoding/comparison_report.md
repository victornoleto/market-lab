# Decoding comparison report — system `1603276`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.45)
- Direction executor: `yaml_literal`
- Features used: ['ema_dist_20_H1']
- Entry hours UTC: [9, 10, 11, 12, 13, 14, 15, 16, 17]
- Pairs: ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
- Max holding hours: 1.1

## Decoding fidelity score: **0.1993** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0113 | 0.0028 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-31.65) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.8202 | 0.1640 |
| hold_similarity | 0.15 | 0.0032 | 0.0005 |
| count_ratio_proximity | 0.15 | 0.1762 (ratio=25.5758) | 0.0264 |
| pnl_correlation_pos | 0.10 | 0.0549 (raw=0.0549) | 0.0055 |

## Comparison details

- n_real: 594
- n_synthetic: 15192
- n_matched (±5min): 89
- entry_timing_precision: 0.0059
- entry_timing_recall: 0.1498
- entry_timing_f1: 0.0113
- direction_acc_at_matched: 0.8202
- hold_KS_stat: 0.9968
- hold_similarity: 0.0032
- count_ratio: 25.5758
- pnl_correlation: 0.0549

### Baseline comparison

- always_buy combined-hit rate: 0.3754
- hour_majority combined-hit rate: 0.3973
- pair_hour_majority combined-hit rate: 0.4394
- max_baseline: 0.4394
- synthetic combined-hit rate: 0.1229
- lift_vs_baseline_pp: -31.65

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).