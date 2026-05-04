# Decoding comparison report — system `1152318`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.55)
- Direction executor: `yaml_literal`
- Features used: ['ema_dist_20_H1']
- Entry hours UTC: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
- Pairs: ['AUDUSD', 'EURCHF']
- Max holding hours: 168.0

## Decoding fidelity score: **0.1202** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0 | 0.0000 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-58.64) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.0 | 0.0000 |
| hold_similarity | 0.15 | 0.3653 | 0.0548 |
| count_ratio_proximity | 0.15 | 0.4361 (ratio=0.4081) | 0.0654 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 1637
- n_synthetic: 668
- n_matched (±5min): 0
- entry_timing_precision: 0.0
- entry_timing_recall: 0.0
- entry_timing_f1: 0.0
- direction_acc_at_matched: nan
- hold_KS_stat: 0.6347
- hold_similarity: 0.3653
- count_ratio: 0.4081
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.5009
- hour_majority combined-hit rate: 0.5718
- pair_hour_majority combined-hit rate: 0.5864
- max_baseline: 0.5864
- synthetic combined-hit rate: 0.0
- lift_vs_baseline_pp: -58.64

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).