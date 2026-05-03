# Decoding comparison report — system `9375654`

- Family (Stage 2): **OVERLAP_NY_LONDON_RANGE**  (confidence 0.55)
- Direction executor: `tree_rank1`
- Features used: ['bb_pos_20_2_H1', 'ema_dist_20_H1', 'ema_dist_20_M5', 'ret_10_H1', 'ret_3_H1', 'ret_3_M15']
- Entry hours UTC: [13, 14, 15, 16, 17]
- Pairs: ['XAUUSD']
- Max holding hours: 4.0

## Decoding fidelity score: **0.1798** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0195 | 0.0049 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-24.7) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.5484 | 0.1097 |
| hold_similarity | 0.15 | 0.0011 | 0.0002 |
| count_ratio_proximity | 0.15 | 0.4338 (ratio=2.471) | 0.0651 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 915
- n_synthetic: 2261
- n_matched (±5min): 31
- entry_timing_precision: 0.0137
- entry_timing_recall: 0.0339
- entry_timing_f1: 0.0195
- direction_acc_at_matched: 0.5484
- hold_KS_stat: 0.9989
- hold_similarity: 0.0011
- count_ratio: 2.471
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.2492
- hour_majority combined-hit rate: 0.2656
- pair_hour_majority combined-hit rate: 0.2656
- max_baseline: 0.2656
- synthetic combined-hit rate: 0.0186
- lift_vs_baseline_pp: -24.7

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: PASS
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).