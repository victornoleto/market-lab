# Decoding comparison report — system `11207608`

- Family (Stage 2): **H1_MOMENTUM_GOLD**  (confidence 0.65)
- Direction executor: `yaml_literal`
- Features used: ['bb_pos_20_2_H1']
- Entry hours UTC: [8, 9, 10, 11, 12, 13, 14, 15, 16]
- Pairs: ['XAUUSD']
- Max holding hours: 0.4

## Decoding fidelity score: **0.2128** (NONE)

| Term | Weight | Value | Contribution |
|---|---:|---:|---:|
| entry_timing_f1 | 0.25 | 0.0182 | 0.0046 |
| baseline_lift_normalized | 0.15 | 0.0 (lift_pp=-15.35) | 0.0000 |
| direction_acc_at_matched | 0.20 | 0.9138 | 0.1828 |
| hold_similarity | 0.15 | 0.0015 | 0.0002 |
| count_ratio_proximity | 0.15 | 0.1684 (ratio=30.6238) | 0.0253 |
| pnl_correlation_pos | 0.10 | 0.0 (raw=nan) | 0.0000 |

## Comparison details

- n_real: 202
- n_synthetic: 6186
- n_matched (±5min): 58
- entry_timing_precision: 0.0094
- entry_timing_recall: 0.2871
- entry_timing_f1: 0.0182
- direction_acc_at_matched: 0.9138
- hold_KS_stat: 0.9985
- hold_similarity: 0.0015
- count_ratio: 30.6238
- pnl_correlation: nan

### Baseline comparison

- always_buy combined-hit rate: 0.3812
- hour_majority combined-hit rate: 0.4158
- pair_hour_majority combined-hit rate: 0.4158
- max_baseline: 0.4158
- synthetic combined-hit rate: 0.2624
- lift_vs_baseline_pp: -15.35

## Smoke invariants

- I1_schema: PASS
- I2_count_ratio: FAIL
- I3_entry_hours: PASS
- I4_direction_sanity: PASS

---

**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via
regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem
tradeable state (sanity flags ortogonais).