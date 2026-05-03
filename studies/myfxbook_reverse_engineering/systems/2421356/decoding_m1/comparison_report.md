# Decoding comparison report — system `2421356`

- Family (Stage 2): **H1_MOMENTUM_GOLD**  (confidence 0.6)
- Direction executor: `yaml_literal`
- Features used: ['bb_pos_20_2_H1']
- Entry hours UTC: [9, 10, 11, 12, 13, 14, 15, 16, 17]
- Pairs: ['XAUUSD']
- Max holding hours: 24.0 (default fallback)

## Decoding fidelity score: **0.3589** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0107 | 0.0027 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-39.31) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.8947 | 0.1789 |
| hold_similarity | 0.15 | 0.0 | 0.0000 |
| count_ratio_proximity | 0.15 | 1.0 (ratio=1.0057) | 0.1500 |
| pnl_correlation_pos | 0.10 | 0.2732 (raw=0.2732) | 0.0273 |

## Comparison details

- n_real: 1763
- n_synthetic: 1773
- n_matched (±5min): 19
- entry_timing_precision: 0.0107
- entry_timing_recall: 0.0108
- entry_timing_f1: 0.0107
- direction_acc_at_matched: 0.8947
- hold_KS_stat: 1.0
- hold_similarity: 0.0
- count_ratio: 1.0057
- pnl_correlation: 0.2732

### Baseline comparison

- always_buy combined-hit rate: 0.3857
- hour_majority combined-hit rate: 0.4027
- pair_hour_majority combined-hit rate: 0.4027
- max_baseline: 0.4027
- synthetic combined-hit rate: 0.0096
- lift_vs_baseline_pp: -39.31

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: PASS
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).