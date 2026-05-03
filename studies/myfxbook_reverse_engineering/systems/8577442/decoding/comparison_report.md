# Decoding comparison report — system `8577442`

- Family (Stage 2): **SWING_TREND_MOMENTUM**  (confidence 0.6)
- Direction executor: `tree_rank1`
- Features used: ['dow', 'ema_dist_20_H4', 'ret_10_H1', 'ret_10_H4', 'ret_10_M1', 'ret_10_M5']
- Entry hours UTC: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
- Pairs: ['USDCAD', 'AUDUSD', 'AUDCAD', 'CADCHF', 'AUDCHF']
- Max holding hours: 240.0

## Decoding fidelity score: **0.0000** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0 | 0.0000 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-63.6) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.0 | 0.0000 |
| hold_similarity | 0.15 | 0.0 | 0.0000 |
| count_ratio_proximity | 0.15 | 0.0 (ratio=0.0) | 0.0000 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 934
- n_synthetic: 0
- n_matched (±5min): 0
- entry_timing_precision: 0.0
- entry_timing_recall: 0.0
- entry_timing_f1: 0.0
- direction_acc_at_matched: nan
- hold_KS_stat: nan
- hold_similarity: nan
- count_ratio: 0.0
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.5471
- hour_majority combined-hit rate: 0.5621
- pair_hour_majority combined-hit rate: 0.636
- max_baseline: 0.636
- synthetic combined-hit rate: 0.0
- lift_vs_baseline_pp: -63.6

## Smoke invariants

- I1_schema: FAIL
- I2_count_ratio: FAIL
- I3_entry_hours: FAIL
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).