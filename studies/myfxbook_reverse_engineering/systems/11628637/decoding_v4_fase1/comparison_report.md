# Decoding comparison report — system `11628637`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.55)
- Direction executor: `yaml_literal`
- Features used: ['ema_dist_20_H1']
- Entry hours UTC: [15, 16, 17, 18, 19]
- Pairs: ['BTCUSD']
- Max holding hours: 2.5

## Decoding fidelity score: **0.2378** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0165 | 0.0041 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-27.16) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.8571 | 0.1714 |
| hold_similarity | 0.15 | 0.0 | 0.0000 |
| count_ratio_proximity | 0.15 | 0.4147 (ratio=2.6595) | 0.0622 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 232
- n_synthetic: 617
- n_matched (±5min): 7
- entry_timing_precision: 0.0113
- entry_timing_recall: 0.0302
- entry_timing_f1: 0.0165
- direction_acc_at_matched: 0.8571
- hold_KS_stat: 1.0
- hold_similarity: 0.0
- count_ratio: 2.6595
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.2543
- hour_majority combined-hit rate: 0.2974
- pair_hour_majority combined-hit rate: 0.2974
- max_baseline: 0.2974
- synthetic combined-hit rate: 0.0259
- lift_vs_baseline_pp: -27.16

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: PASS
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).