# Decoding comparison report — system `10475089`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.42)
- Direction executor: `univariate_rank1`
- Features used: ['ret_1_M1']
- Entry hours UTC: [0]
- Pairs: ['GBPJPY']
- Max holding hours: 627.89

## Decoding fidelity score: **0.0000** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0 | 0.0000 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-59.83) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.0 | 0.0000 |
| hold_similarity | 0.15 | 0.0 | 0.0000 |
| count_ratio_proximity | 0.15 | 0.0 (ratio=0.0) | 0.0000 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 117
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

- always_buy combined-hit rate: 0.5983
- hour_majority combined-hit rate: 0.5983
- pair_hour_majority combined-hit rate: 0.5983
- max_baseline: 0.5983
- synthetic combined-hit rate: 0.0
- lift_vs_baseline_pp: -59.83

## Smoke invariants

- I1_schema: FAIL
- I2_count_ratio: FAIL
- I3_entry_hours: FAIL
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).