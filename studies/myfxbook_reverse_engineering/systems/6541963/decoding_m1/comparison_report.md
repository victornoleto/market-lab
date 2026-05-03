# Decoding comparison report — system `6541963`

- Family (Stage 2): **H1_MOMENTUM_GOLD**  (confidence 0.6)
- Direction executor: `yaml_literal`
- Features used: ['ret_10_H1']
- Entry hours UTC: [9, 10, 11, 12, 13, 14, 15, 16, 17]
- Pairs: ['XAUUSD']
- Max holding hours: 1.0

## Decoding fidelity score: **0.2198** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0281 | 0.0070 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-28.15) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.8195 | 0.1639 |
| hold_similarity | 0.15 | 0.0203 | 0.0030 |
| count_ratio_proximity | 0.15 | 0.2553 (ratio=7.5495) | 0.0383 |
| pnl_correlation_pos | 0.10 | 0.0748 (raw=0.0748) | 0.0075 |

## Comparison details

- n_real: 2213
- n_synthetic: 16707
- n_matched (±5min): 266
- entry_timing_precision: 0.0159
- entry_timing_recall: 0.1202
- entry_timing_f1: 0.0281
- direction_acc_at_matched: 0.8195
- hold_KS_stat: 0.9797
- hold_similarity: 0.0203
- count_ratio: 7.5495
- pnl_correlation: 0.0748

### Baseline comparison

- always_buy combined-hit rate: 0.3714
- hour_majority combined-hit rate: 0.38
- pair_hour_majority combined-hit rate: 0.38
- max_baseline: 0.38
- synthetic combined-hit rate: 0.0985
- lift_vs_baseline_pp: -28.15

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).