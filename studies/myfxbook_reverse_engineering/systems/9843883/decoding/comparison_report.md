# Decoding comparison report — system `9843883`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.5)
- Direction executor: `univariate_rank1`
- Features used: ['ret_3_M5']
- Entry hours UTC: [13]
- Pairs: ['EURUSD', 'USDCHF']
- Max holding hours: 168.0

## Decoding fidelity score: **0.2275** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.1517 | 0.0379 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-22.67) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.567 | 0.1134 |
| hold_similarity | 0.15 | 0.1945 | 0.0292 |
| count_ratio_proximity | 0.15 | 0.2653 (ratio=0.1467) | 0.0398 |
| pnl_correlation_pos | 0.10 | 0.0723 (raw=0.0723) | 0.0072 |

## Comparison details

- n_real: 2576
- n_synthetic: 378
- n_matched (±5min): 224
- entry_timing_precision: 0.5926
- entry_timing_recall: 0.087
- entry_timing_f1: 0.1517
- direction_acc_at_matched: 0.567
- hold_KS_stat: 0.8055
- hold_similarity: 0.1945
- count_ratio: 0.1467
- pnl_correlation: 0.0723

### Baseline comparison

- always_buy combined-hit rate: 0.21
- hour_majority combined-hit rate: 0.276
- pair_hour_majority combined-hit rate: 0.276
- max_baseline: 0.276
- synthetic combined-hit rate: 0.0493
- lift_vs_baseline_pp: -22.67

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).