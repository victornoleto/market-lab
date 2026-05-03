# Decoder fingerprint — system 8599269

Generated: 2026-05-02T10:09:40

## Sanity (martingale + lot dynamics)

- n_trades: **1123**, deposits: 3
- pairs: {'AUDUSD': 1123}
- actions: {'Buy': 571, 'Sell': 552}
- date range: 2021-06-18 13:32:41+00:00 → 2026-04-29 21:44:22+00:00
- max gap days: 44.7
- lot p50/p95/p99/max: 0.01 / 0.02 / 0.05 / 0.11
- lot p95/p50 ratio: 2.00
- martingale flag: **FAIL (martingale-like dynamics)**, steps=1, max_streak=1
- k1 flags: ['per-month max/median P95 = 5.00 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 16.99 / 566.80 / 2383.72

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 18:00 — 91 trades
  - 17:00 — 87 trades
  - 19:00 — 80 trades
  - 16:00 — 78 trades
  - 11:00 — 64 trades

Top entry hour:5min (UTC):
  - 18:00 — 91 trades
  - 17:00 — 87 trades
  - 19:00 — 80 trades
  - 16:00 — 78 trades
  - 11:00 — 64 trades

Exit kind distribution:
  - manual_or_time: 1123

Direction by pair (Buy %):
  - AUDUSD: total=1123, buy_pct=50.8%

Direction by hour (Buy %, top 5 by activity):
  - hour=18: total=91, buy_pct=54.9%
  - hour=17: total=87, buy_pct=57.5%
  - hour=19: total=80, buy_pct=45.0%
  - hour=16: total=78, buy_pct=55.1%
  - hour=11: total=64, buy_pct=37.5%

## Feature extraction

- trades processed: 1123
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.52, range_norm_M15=0.11, atr_ratio_M15=0.11, ema_dist_20_M1=0.08, at... | 0.546 | 0.045 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.5085); Always-Sell = 0.4915 | 0.508 | — | 1.00 | — |
| 3 | ripper | RIPPER ruleset: [[close_vs_session_open_H4=1.0^bb_pos_20_2_H1=>0.92]] | 0.500 | 0.101 | 1.00 | — |
| 4 | univariate | bb_pos_20_2_M15 > -0.1466 ⇒ Buy | 0.593 | — | 0.60 | 0.000 |
| 5 | univariate | ema_dist_20_M15 > -0.3227 ⇒ Buy | 0.588 | — | 0.60 | 0.000 |
| 6 | univariate | bb_pos_20_2_H1 > -0.02433 ⇒ Buy | 0.599 | — | 0.50 | 0.000 |
| 7 | univariate | ema_dist_20_H1 > -0.009202 ⇒ Buy | 0.598 | — | 0.50 | 0.000 |
| 8 | univariate | ret_3_H4 > 6.887e-05 ⇒ Buy | 0.598 | — | 0.50 | 0.000 |
| 9 | univariate | close_vs_session_open_M15 > -1 ⇒ Buy | 0.565 | — | 0.53 | 0.005 |
| 10 | univariate | bb_pos_20_2_H4 > -0.1315 ⇒ Buy | 0.580 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.52, range_norm_M15=0.11, atr_ratio_M15=0.11, ema_dist_20_M1=0.08, atr_ratio_M5=0.06

|--- bb_pos_20_2_H1 <= 0.68
|   |--- bb_pos_20_2_H1 <= -0.66
|   |   |--- range_norm_M15 <= 0.84
|   |   |   |--- range_norm_H4 <= 1.04
|   |   |   |   |--- class: 0
|   |   |   |--- range_norm_H4 >  1.04
|   |   |   |   |--- class: 0
|   |   |--- range_norm_M15 >  0.84
|   |   |   |--- atr_ratio_M15 <= 0.55
|   |   |   |   |--- class: 1
|   |   |   |--- atr_ratio_M15 >  0.55
|   |   |   |   |--- class: 0
|   |--- bb_pos_20_2_H1 >  -0.66
|   |   |--- ema_dist_20_M1 <= 1.29
|   |   |   |--- atr_ratio_M5 <= 0.29
|   |   |   |   |--- class: 1
|   |   |   |--- atr_ratio_M5 >  0.29
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_M1 >  1.29
|   |   |   |--- class: 0
|--- bb_pos_20_2_H1 >  0.68
|   |--- atr_ratio_M15 <= 0.56
|   |   |--- ema_dist_20_M5 <= 0.54
|   |   |   |--- class: 0
|   |   |--- ema_dist_20_M5 >  0.54
|   |   |   |--- class: 1
|   |--- atr_ratio_M15 >  0.56
|   |   |--- ret_10_M5 <= 0.00
|   |   |   |--- class: 1
|   |   |--- ret_10_M5 >  0.00
|   |   |   |--- class: 1

```

### RIPPER full output (rank 3)
```
RIPPER ruleset:
[[close_vs_session_open_H4=1.0^bb_pos_20_2_H1=>0.92]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
