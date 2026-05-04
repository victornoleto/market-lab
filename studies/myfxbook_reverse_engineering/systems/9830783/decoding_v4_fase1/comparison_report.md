# Decoding comparison report — system `9830783`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.3)
- Direction executor: `univariate_rank1`
- Features used: ['bb_pos_20_2_M15']
- Entry hours UTC: [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
- Pairs: ['USDCAD', 'GBPCHF', 'EURCHF', 'AUDNZD']
- Max holding hours: 720.0

## Decoding fidelity score: **0.1347** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0048 | 0.0012 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-35.1) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.5 | 0.1000 |
| hold_similarity | 0.15 | 0.0453 | 0.0068 |
| count_ratio_proximity | 0.15 | 0.1783 (ratio=0.041) | 0.0267 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 4000
- n_synthetic: 164
- n_matched (±5min): 10
- entry_timing_precision: 0.061
- entry_timing_recall: 0.0025
- entry_timing_f1: 0.0048
- direction_acc_at_matched: 0.5
- hold_KS_stat: 0.9547
- hold_similarity: 0.0453
- count_ratio: 0.041
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.3123
- hour_majority combined-hit rate: 0.3432
- pair_hour_majority combined-hit rate: 0.3522
- max_baseline: 0.3522
- synthetic combined-hit rate: 0.0013
- lift_vs_baseline_pp: -35.1

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).