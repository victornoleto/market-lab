# Decoding comparison report — system `11171596`

- Family (Stage 2): **UNCATEGORIZED**  (confidence 0.45)
- Direction executor: `univariate_rank1`
- Features used: ['dow']
- Entry hours UTC: [13]
- Pairs: ['EURUSD', 'USDCHF']
- Max holding hours: 24.0

## Decoding fidelity score: **0.4816** (LOW)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.4497 | 0.1124 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-25.67) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.7283 | 0.1457 |
| hold_similarity | 0.15 | 0.4903 | 0.0735 |
| count_ratio_proximity | 0.15 | 1.0 (ratio=0.7535) | 0.1500 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 1083
- n_synthetic: 816
- n_matched (±5min): 427
- entry_timing_precision: 0.5233
- entry_timing_recall: 0.3943
- entry_timing_f1: 0.4497
- direction_acc_at_matched: 0.7283
- hold_KS_stat: 0.5097
- hold_similarity: 0.4903
- count_ratio: 0.7535
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.0
- hour_majority combined-hit rate: 0.5439
- pair_hour_majority combined-hit rate: 0.5439
- max_baseline: 0.5439
- synthetic combined-hit rate: 0.2872
- lift_vs_baseline_pp: -25.67

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: PASS
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).