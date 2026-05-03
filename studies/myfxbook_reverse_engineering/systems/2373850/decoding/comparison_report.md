# Decoding comparison report — system `2373850`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.55)
- Direction executor: `univariate_rank1`
- Features used: ['dow']
- Entry hours UTC: [13]
- Pairs: ['EURUSD', 'USDCHF']
- Max holding hours: 168.0

## Decoding fidelity score: **0.2967** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.1672 | 0.0418 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-41.75) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.8953 | 0.1791 |
| hold_similarity | 0.15 | 0.1431 | 0.0215 |
| count_ratio_proximity | 0.15 | 0.3117 (ratio=0.2164) | 0.0468 |
| pnl_correlation_pos | 0.10 | 0.0767 (raw=0.0767) | 0.0077 |

## Comparison details

- n_real: 1691
- n_synthetic: 366
- n_matched (±5min): 172
- entry_timing_precision: 0.4699
- entry_timing_recall: 0.1017
- entry_timing_f1: 0.1672
- direction_acc_at_matched: 0.8953
- hold_KS_stat: 0.8569
- hold_similarity: 0.1431
- count_ratio: 0.2164
- pnl_correlation: 0.0767

### Baseline comparison

- always_buy combined-hit rate: 0.071
- hour_majority combined-hit rate: 0.5086
- pair_hour_majority combined-hit rate: 0.5086
- max_baseline: 0.5086
- synthetic combined-hit rate: 0.0911
- lift_vs_baseline_pp: -41.75

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).