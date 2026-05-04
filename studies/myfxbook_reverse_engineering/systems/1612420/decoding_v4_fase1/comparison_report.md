# Decoding comparison report — system `1612420`

- Family (Stage 2): **NEWS_RELEASE_MOMENTUM**  (confidence 0.6)
- Direction executor: `yaml_literal`
- Features used: ['ret_3_H4']
- Entry hours UTC: [15]
- Pairs: ['EURUSD', 'GBPUSD', 'AUDUSD', 'USDJPY']
- Max holding hours: 1.0

## Decoding fidelity score: **0.0425** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0 | 0.0000 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-25.13) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.0 | 0.0000 |
| hold_similarity | 0.15 | 0.0203 | 0.0030 |
| count_ratio_proximity | 0.15 | 0.2632 (ratio=6.9645) | 0.0395 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 788
- n_synthetic: 5488
- n_matched (±5min): 0
- entry_timing_precision: 0.0
- entry_timing_recall: 0.0
- entry_timing_f1: 0.0
- direction_acc_at_matched: nan
- hold_KS_stat: 0.9797
- hold_similarity: 0.0203
- count_ratio: 6.9645
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.2398
- hour_majority combined-hit rate: 0.2398
- pair_hour_majority combined-hit rate: 0.2513
- max_baseline: 0.2513
- synthetic combined-hit rate: 0.0
- lift_vs_baseline_pp: -25.13

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).