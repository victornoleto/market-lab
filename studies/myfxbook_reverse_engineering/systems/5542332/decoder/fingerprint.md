# Decoder fingerprint — system 5542332

Generated: 2026-05-02T07:11:04

## Sanity (martingale + lot dynamics)

- n_trades: **3995**, deposits: 5
- pairs: {'GBPUSD': 1592, 'USDCAD': 836, 'EURUSD': 600, 'USDJPY': 415, 'EURGBP': 213, 'EURCHF': 144, 'USDCHF': 102, 'AUDUSD': 93}
- actions: {'Sell': 2098, 'Buy': 1897}
- date range: 2019-12-16 14:49:02+00:00 → 2021-06-16 10:05:43+00:00
- max gap days: 3.9
- lot p50/p95/p99/max: 0.10 / 0.10 / 0.10 / 0.10
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 4.29 / 351.00 / 10452.57

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 17:00 — 399 trades
  - 16:00 — 353 trades
  - 10:00 — 339 trades
  - 15:00 — 276 trades
  - 11:00 — 266 trades

Top entry hour:5min (UTC):
  - 17:55 — 55 trades
  - 18:30 — 45 trades
  - 17:50 — 44 trades
  - 00:05 — 43 trades
  - 17:20 — 41 trades

Exit kind distribution:
  - manual_or_time: 3995

Direction by pair (Buy %):
  - AUDUSD: total=93, buy_pct=52.7%
  - EURCHF: total=144, buy_pct=10.4%
  - EURGBP: total=213, buy_pct=49.3%
  - EURUSD: total=600, buy_pct=50.2%
  - GBPUSD: total=1592, buy_pct=44.7%
  - USDCAD: total=836, buy_pct=48.0%
  - USDCHF: total=102, buy_pct=84.3%
  - USDJPY: total=415, buy_pct=55.2%

Direction by hour (Buy %, top 5 by activity):
  - hour=17: total=399, buy_pct=45.4%
  - hour=16: total=353, buy_pct=43.3%
  - hour=10: total=339, buy_pct=49.0%
  - hour=15: total=276, buy_pct=49.3%
  - hour=11: total=266, buy_pct=43.6%

## Feature extraction

- trades processed: 3995
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | baseline | Always-Buy (y_buy mean = 0.4748); Always-Sell = 0.5252 | 0.525 | — | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M5=1.0^ema_dist_20_H4=0.45-0.82^ret_1_H1=0.00019-0.00041] V [ema_dist_20_H4=0.45-0.82^r... | 0.521 | 0.055 | 1.00 | — |
| 3 | tree | DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.31, ret_3_H4=0.24, bb_pos_20_2_H4=0.18, ret_10_H4=0.09, ret_1_H4=0.0... | 0.499 | 0.035 | 1.00 | — |
| 4 | univariate | bb_pos_20_2_M5 > -0.5969 ⇒ Sell | 0.531 | — | 0.80 | 0.021 |
| 5 | univariate | ret_1_M5 > -0.0002083 ⇒ Sell | 0.528 | — | 0.80 | 0.123 |
| 6 | univariate | ema_dist_20_M5 > -1.064 ⇒ Sell | 0.527 | — | 0.80 | 0.197 |
| 7 | univariate | ema_dist_20_H4 > -1.117 ⇒ Sell | 0.527 | — | 0.80 | 0.221 |
| 8 | univariate | ret_3_M5 > -0.0003304 ⇒ Sell | 0.524 | — | 0.80 | 0.595 |
| 9 | univariate | dollar_index_proxy > -1 ⇒ Sell | 0.525 | — | 0.80 | 0.481 |
| 10 | univariate | bb_pos_20_2_H4 > -0.6659 ⇒ Sell | 0.523 | — | 0.80 | 1.000 |

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M5=1.0^ema_dist_20_H4=0.45-0.82^ret_1_H1=0.00019-0.00041] V [ema_dist_20_H4=0.45-0.82^ret_1_H4=8.5e-05-0.00045]]
```

### TREE full output (rank 3)
```
DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.31, ret_3_H4=0.24, bb_pos_20_2_H4=0.18, ret_10_H4=0.09, ret_1_H4=0.07

|--- ema_dist_20_H4 <= 1.95
|   |--- ret_3_H4 <= -0.00
|   |   |--- ema_dist_20_H4 <= -1.14
|   |   |   |--- ret_10_H4 <= -0.01
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H4 >  -0.01
|   |   |   |   |--- class: 1
|   |   |--- ema_dist_20_H4 >  -1.14
|   |   |   |--- ret_1_H4 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_1_H4 >  0.00
|   |   |   |   |--- class: 0
|   |--- ret_3_H4 >  -0.00
|   |   |--- ema_dist_20_H4 <= 1.21
|   |   |   |--- bb_pos_20_2_H4 <= 0.46
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_H4 >  0.46
|   |   |   |   |--- class: 1
|   |   |--- ema_dist_20_H4 >  1.21
|   |   |   |--- bb_pos_20_2_H4 <= 1.04
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_H4 >  1.04
|   |   |   |   |--- class: 1
|--- ema_dist_20_H4 >  1.95
|   |--- ret_3_H4 <= 0.00
|   |   |--- ret_3_H4 <= 0.00
|   |   |   |--- class: 0
|   |   |--- ret_3_H4 >  0.00
|   |   |   |--- atr_ratio_M1 <= 0.10
|   |   |   |   |--- class: 0
|   |   |   |--- atr_ratio_M1 >  0.10
|   |   |   |   |--- class: 0
|   |--- ret_3_H4 >  0.00
|   |   |--- ema_dist_20_M1 <= 1.22
|   |   |   |--- ret_10_H1 <= 0.01
|   |   |   |   |--- class: 1
|   |   |   |--- ret_10_H1 >  0.01
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_M1 >  1.22
|   |   |   |--- class: 1

```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
