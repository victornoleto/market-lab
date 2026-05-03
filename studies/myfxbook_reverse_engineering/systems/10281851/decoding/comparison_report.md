# Decoding comparison report — system `10281851`

- Family (Stage 2): **H1_MOMENTUM_GOLD**  (confidence 0.6)
- Direction executor: `yaml_literal`
- Features used: ['bb_pos_20_2_H1']
- Entry hours UTC: [9, 10, 11, 12, 13, 14, 15, 16, 17]
- Pairs: ['XAUUSD']
- Max holding hours: 5.5

## Decoding fidelity score: **0.2518** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0113 | 0.0028 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-40.03) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.9231 | 0.1846 |
| hold_similarity | 0.15 | 0.0015 | 0.0002 |
| count_ratio_proximity | 0.15 | 0.4273 (ratio=2.5322) | 0.0641 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 652
- n_synthetic: 1651
- n_matched (±5min): 13
- entry_timing_precision: 0.0079
- entry_timing_recall: 0.0199
- entry_timing_f1: 0.0113
- direction_acc_at_matched: 0.9231
- hold_KS_stat: 0.9985
- hold_similarity: 0.0015
- count_ratio: 2.5322
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.4034
- hour_majority combined-hit rate: 0.4187
- pair_hour_majority combined-hit rate: 0.4187
- max_baseline: 0.4187
- synthetic combined-hit rate: 0.0184
- lift_vs_baseline_pp: -40.03

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: PASS
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).