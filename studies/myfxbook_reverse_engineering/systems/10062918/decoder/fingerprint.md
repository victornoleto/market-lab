# Decoder fingerprint — system 10062918

Generated: 2026-05-02T00:45:57

## Sanity (martingale + lot dynamics)

- n_trades: **731**, deposits: 1
- pairs: {'AUDUSD': 381, 'EURCHF': 350}
- actions: {'Sell': 374, 'Buy': 357}
- date range: 2022-08-22 16:36:41+00:00 → 2025-11-19 03:05:22+00:00
- max gap days: 75.1
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.01 / 0.01
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 153.95 / 960.45 / 1783.99

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 03:00 — 67 trades
  - 04:00 — 59 trades
  - 09:00 — 58 trades
  - 17:00 — 54 trades
  - 10:00 — 53 trades

Top entry hour:5min (UTC):
  - 15:30 — 13 trades
  - 17:00 — 10 trades
  - 03:50 — 9 trades
  - 10:10 — 9 trades
  - 10:15 — 8 trades

Exit kind distribution:
  - manual_or_time: 731

Direction by pair (Buy %):
  - AUDUSD: total=381, buy_pct=53.8%
  - EURCHF: total=350, buy_pct=43.4%

Direction by hour (Buy %, top 5 by activity):
  - hour=03: total=67, buy_pct=56.7%
  - hour=04: total=59, buy_pct=54.2%
  - hour=09: total=58, buy_pct=31.0%
  - hour=17: total=54, buy_pct=61.1%
  - hour=10: total=53, buy_pct=47.2%

## Feature extraction

- trades processed: 731
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.78, ret_10_H1=0.07, ema_dist_20_H1=0.06, bb_pos_20_2_M5=0.06, ret_1_... | 0.793 | 0.038 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_H1=-1.0^ema_dist_20_H1=-2.04--1.32] V [close_vs_session_open_M1=-1.0^ema_dist_20_H1=<-2... | 0.715 | 0.056 | 1.00 | — |
| 3 | univariate | ema_dist_20_H4 > -0.006575 ⇒ Sell | 0.813 | — | 0.50 | 0.000 |
| 4 | univariate | bb_pos_20_2_H4 > 0.02913 ⇒ Sell | 0.799 | — | 0.50 | 0.000 |
| 5 | univariate | bb_pos_20_2_H1 > 0.04522 ⇒ Sell | 0.777 | — | 0.50 | 0.000 |
| 6 | univariate | ret_10_H4 > -0.000107 ⇒ Sell | 0.777 | — | 0.50 | 0.000 |
| 7 | univariate | ret_10_H1 > 8.982e-05 ⇒ Sell | 0.766 | — | 0.50 | 0.000 |
| 8 | univariate | ret_3_H4 > 2.129e-05 ⇒ Sell | 0.747 | — | 0.50 | 0.000 |
| 9 | univariate | ema_dist_20_M15 > -0.2832 ⇒ Sell | 0.677 | — | 0.60 | 0.000 |
| 10 | univariate | bb_pos_20_2_M15 > -0.172 ⇒ Sell | 0.672 | — | 0.60 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.78, ret_10_H1=0.07, ema_dist_20_H1=0.06, bb_pos_20_2_M5=0.06, ret_1_H1=0.03

|--- ema_dist_20_H4 <= 0.06
|   |--- ret_10_H1 <= -0.00
|   |   |--- ret_1_H1 <= -0.00
|   |   |   |--- class: 1
|   |   |--- ret_1_H1 >  -0.00
|   |   |   |--- range_norm_M1 <= 0.73
|   |   |   |   |--- class: 1
|   |   |   |--- range_norm_M1 >  0.73
|   |   |   |   |--- class: 1
|   |--- ret_10_H1 >  -0.00
|   |   |--- bb_pos_20_2_M5 <= -0.17
|   |   |   |--- class: 0
|   |   |--- bb_pos_20_2_M5 >  -0.17
|   |   |   |--- class: 1
|--- ema_dist_20_H4 >  0.06
|   |--- ema_dist_20_H1 <= 0.43
|   |   |--- class: 0
|   |--- ema_dist_20_H1 >  0.43
|   |   |--- ret_1_H1 <= 0.00
|   |   |   |--- ret_1_H1 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_1_H1 >  0.00
|   |   |   |   |--- class: 0
|   |   |--- ret_1_H1 >  0.00
|   |   |   |--- class: 0

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_H1=-1.0^ema_dist_20_H1=-2.04--1.32] V [close_vs_session_open_M1=-1.0^ema_dist_20_H1=<-2.04] V [ema_dist_20_H1=-1.32--0.79^close_vs_session_open_M1=-1.0^bb_pos_20_2_H1=-0.72--0.49] V [prior_bar_sign_H1=1.0^ema_dist_20_H4=-0.83--0.42^prior_bar_sign_M15=1.0] V [ret_10_H4=-0.0054--0.0033^bb_pos_20_2_H1=-0.49--0.24] V [ema_dist_20_H4=-0.42--0.0051^prior_bar_sign_H1=1.0^prior_bar_sign_M1=1.0] V [ema_dist_20_H4=-1.34--0.83^ret_10_H1=-0.0025--0.0015] V [ema_dist_20_H4=<-1.96] V [ema_dist_20_H4=-1.96--1.34] V [ret_1_H1=>0.0013^ret_10_H4=-0.0017--0.00011] V [ema_dist_20_H4=-1.34--0.83^bb_pos_20_2_M1=0.24-0.45]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
