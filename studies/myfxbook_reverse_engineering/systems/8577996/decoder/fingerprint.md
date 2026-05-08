# Decoder fingerprint — system 8577996

Generated: 2026-05-02T10:05:18

## Sanity (martingale + lot dynamics)

- n_trades: **4000**, deposits: 0
- pairs: {'USDCHF': 1560, 'AUDUSD': 1417, 'EURCHF': 1023}
- actions: {'Sell': 2001, 'Buy': 1999}
- date range: 2023-03-10 17:11:50+00:00 → 2026-05-01 17:12:52+00:00
- max gap days: 4.8
- lot p50/p95/p99/max: 0.01 / 0.03 / 0.04 / 0.06
- lot p95/p50 ratio: 3.00
- martingale flag: **FAIL (martingale-like dynamics)**, steps=22, max_streak=1
- k1 flags: ['per-month max/median P95 = 4.10 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 67.43 / 1809.09 / 4370.03

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 17:00 — 473 trades
  - 15:00 — 363 trades
  - 16:00 — 345 trades
  - 10:00 — 312 trades
  - 18:00 — 243 trades

Top entry hour:5min (UTC):
  - 15:30 — 157 trades
  - 17:00 — 70 trades
  - 00:00 — 69 trades
  - 10:30 — 64 trades
  - 17:15 — 48 trades

Exit kind distribution:
  - manual_or_time: 4000

Direction by pair (Buy %):
  - AUDUSD: total=1417, buy_pct=49.8%
  - EURCHF: total=1023, buy_pct=50.3%
  - USDCHF: total=1560, buy_pct=49.9%

Direction by hour (Buy %, top 5 by activity):
  - hour=17: total=473, buy_pct=52.2%
  - hour=15: total=363, buy_pct=50.1%
  - hour=16: total=345, buy_pct=49.3%
  - hour=10: total=312, buy_pct=52.2%
  - hour=18: total=243, buy_pct=49.4%

## Feature extraction

- trades processed: 4000
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_3_H4=0.17, bb_pos_20_2_M5=0.13, ret_10_M1=0.12, range_norm_M15=0.12, ret_1_M5=0.1... | 0.514 | 0.007 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M5=-1.0]] | 0.513 | 0.012 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.4998); Always-Sell = 0.5002 | 0.500 | — | 1.00 | — |
| 4 | univariate | ret_10_H1 > -0.0006821 ⇒ Sell | 0.527 | — | 0.50 | 0.182 |
| 5 | univariate | ret_3_H4 > -0.0006104 ⇒ Sell | 0.526 | — | 0.50 | 0.320 |
| 6 | univariate | ema_dist_20_H1 > -0.3432 ⇒ Sell | 0.524 | — | 0.50 | 0.614 |
| 7 | univariate | bb_pos_20_2_H1 > -0.2151 ⇒ Sell | 0.521 | — | 0.50 | 1.000 |
| 8 | univariate | bb_pos_20_2_H4 > -0.3195 ⇒ Sell | 0.518 | — | 0.50 | 1.000 |
| 9 | univariate | close_vs_session_open_M5 > -1 ⇒ Sell | 0.518 | — | 0.48 | 1.000 |
| 10 | univariate | close_vs_session_open_H4 > -1 ⇒ Sell | 0.517 | — | 0.47 | 1.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_3_H4=0.17, bb_pos_20_2_M5=0.13, ret_10_M1=0.12, range_norm_M15=0.12, ret_1_M5=0.10

|--- ret_3_H4 <= -0.00
|   |--- is_first_min_of_hour <= 0.50
|   |   |--- bb_pos_20_2_M1 <= 0.82
|   |   |   |--- ret_10_M1 <= -0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_10_M1 >  -0.00
|   |   |   |   |--- class: 0
|   |   |--- bb_pos_20_2_M1 >  0.82
|   |   |   |--- ret_1_M5 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_1_M5 >  0.00
|   |   |   |   |--- class: 1
|   |--- is_first_min_of_hour >  0.50
|   |   |--- class: 0
|--- ret_3_H4 >  -0.00
|   |--- range_norm_M15 <= 1.07
|   |   |--- range_norm_M15 <= 0.95
|   |   |   |--- bb_pos_20_2_M5 <= 0.97
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_M5 >  0.97
|   |   |   |   |--- class: 0
|   |   |--- range_norm_M15 >  0.95
|   |   |   |--- ret_1_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_1_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |--- range_norm_M15 >  1.07
|   |   |--- bb_pos_20_2_M5 <= -0.14
|   |   |   |--- dollar_index_proxy <= 0.50
|   |   |   |   |--- class: 1
|   |   |   |--- dollar_index_proxy >  0.50
|   |   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_M5 >  -0.14
|   |   |   |--- ret_1_H1 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_1_H1 >  0.00
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M5=-1.0]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
