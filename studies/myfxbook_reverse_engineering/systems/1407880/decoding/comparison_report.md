# Decoding comparison report — system `1407880`

- Family (Stage 2): **LATE_NY_BREAKOUT**  (confidence 0.75)
- Direction executor: `tree_rank1`
- Features used: ['bb_pos_20_2_M15', 'bb_pos_20_2_M5', 'range_norm_H1']
- Entry hours UTC: [0, 1, 22, 23]
- Pairs: ['GBPUSD', 'USDCAD', 'EURUSD', 'EURCHF', 'USDCHF', 'EURGBP']
- Max holding hours: 4.0

## Decoding fidelity score: **0.0550** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0 | 0.0000 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-55.42) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.0 | 0.0000 |
| hold_similarity | 0.15 | 0.0221 | 0.0033 |
| count_ratio_proximity | 0.15 | 0.3443 (ratio=3.7427) | 0.0516 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 3304
- n_synthetic: 12366
- n_matched (±5min): 0
- entry_timing_precision: 0.0
- entry_timing_recall: 0.0
- entry_timing_f1: 0.0
- direction_acc_at_matched: nan
- hold_KS_stat: 0.9779
- hold_similarity: 0.0221
- count_ratio: 3.7427
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.4818
- hour_majority combined-hit rate: 0.5272
- pair_hour_majority combined-hit rate: 0.5542
- max_baseline: 0.5542
- synthetic combined-hit rate: 0.0
- lift_vs_baseline_pp: -55.42

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: PASS
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).