# Decoder fingerprint — system 6541963

Generated: 2026-05-02T07:31:09

## Sanity (martingale + lot dynamics)

- n_trades: **2213**, deposits: 1
- pairs: {'XAUUSD': 2213}
- actions: {'Buy': 1152, 'Sell': 1061}
- date range: 2019-03-05 17:01:04+00:00 → 2026-04-30 11:04:07+00:00
- max gap days: 63.8
- lot p50/p95/p99/max: 18.65 / 76.74 / 88.86 / 100.00
- lot p95/p50 ratio: 4.11
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.00 / 0.29 / 8.75

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 15:00 — 307 trades
  - 16:00 — 231 trades
  - 09:00 — 190 trades
  - 10:00 — 175 trades
  - 17:00 — 172 trades

Top entry hour:5min (UTC):
  - 15:30 — 67 trades
  - 17:00 — 41 trades
  - 16:35 — 38 trades
  - 15:20 — 35 trades
  - 15:15 — 35 trades

Exit kind distribution:
  - manual_or_time: 2213

Direction by pair (Buy %):
  - XAUUSD: total=2213, buy_pct=52.1%

Direction by hour (Buy %, top 5 by activity):
  - hour=15: total=307, buy_pct=53.1%
  - hour=16: total=231, buy_pct=52.8%
  - hour=09: total=190, buy_pct=54.2%
  - hour=10: total=175, buy_pct=52.6%
  - hour=17: total=172, buy_pct=49.4%

## Feature extraction

- trades processed: 2213
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_10_H1=0.74, ret_3_H1=0.07, bb_pos_20_2_H1=0.05, ema_dist_20_H1=0.04, ret_1_H1=0.0... | 0.844 | 0.026 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M1=1.0^ret_10_H1=>0.0079^bb_pos_20_2_M15=0.46-0.61] V [close_vs_session_open_M5=1.0^bb_... | 0.794 | 0.026 | 1.00 | — |
| 3 | univariate | ret_10_H1 > -0.001083 ⇒ Buy | 0.808 | — | 0.60 | 0.000 |
| 4 | univariate | bb_pos_20_2_H1 > 0.08917 ⇒ Buy | 0.811 | — | 0.50 | 0.000 |
| 5 | univariate | ema_dist_20_H1 > 0.1304 ⇒ Buy | 0.789 | — | 0.50 | 0.000 |
| 6 | univariate | ret_3_H4 > 0.0002174 ⇒ Buy | 0.782 | — | 0.50 | 0.000 |
| 7 | baseline | Always-Buy (y_buy mean = 0.5206); Always-Sell = 0.4794 | 0.521 | — | 1.00 | — |
| 8 | univariate | ema_dist_20_H4 > 0.1744 ⇒ Buy | 0.717 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.06327 ⇒ Buy | 0.707 | — | 0.50 | 0.000 |
| 10 | univariate | ema_dist_20_M15 > 0.03382 ⇒ Buy | 0.703 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_10_H1=0.74, ret_3_H1=0.07, bb_pos_20_2_H1=0.05, ema_dist_20_H1=0.04, ret_1_H1=0.03

|--- ret_10_H1 <= -0.00
|   |--- ret_1_H1 <= -0.00
|   |   |--- ema_dist_20_H1 <= -1.54
|   |   |   |--- bb_pos_20_2_H1 <= -1.28
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_H1 >  -1.28
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_H1 >  -1.54
|   |   |   |--- ret_10_M15 <= -0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_10_M15 >  -0.00
|   |   |   |   |--- class: 0
|   |--- ret_1_H1 >  -0.00
|   |   |--- bb_pos_20_2_H1 <= -0.14
|   |   |   |--- atr_ratio_M15 <= 0.86
|   |   |   |   |--- class: 0
|   |   |   |--- atr_ratio_M15 >  0.86
|   |   |   |   |--- class: 0
|   |   |--- bb_pos_20_2_H1 >  -0.14
|   |   |   |--- class: 0
|--- ret_10_H1 >  -0.00
|   |--- ret_10_H1 <= 0.00
|   |   |--- ret_3_H1 <= 0.00
|   |   |   |--- bb_pos_20_2_H1 <= -0.18
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_H1 >  -0.18
|   |   |   |   |--- class: 1
|   |   |--- ret_3_H1 >  0.00
|   |   |   |--- bb_pos_20_2_H1 <= 0.44
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_H1 >  0.44
|   |   |   |   |--- class: 1
|   |--- ret_10_H1 >  0.00
|   |   |--- range_norm_H4 <= 1.62
|   |   |   |--- ret_1_H1 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_1_H1 >  0.00
|   |   |   |   |--- class: 1
|   |   |--- range_norm_H4 >  1.62
|   |   |   |--- ret_10_H4 <= 0.01
|   |   |   |   |--- class: 1
|   |   |   |--- ret_10_H4 >  0.01
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M1=1.0^ret_10_H1=>0.0079^bb_pos_20_2_M15=0.46-0.61] V [close_vs_session_open_M5=1.0^bb_pos_20_2_H1=0.88-1.09^ema_dist_20_M15=1.27-1.82] V [close_vs_session_open_M1=1.0^bb_pos_20_2_H1=0.38-0.66^prior_bar_sign_H1=-1.0^close_vs_session_open_H1=1.0] V [close_vs_session_open_M1=1.0^ema_dist_20_H1=1.64-2.35^prior_bar_sign_H1=-1.0] V [close_vs_session_open_M1=1.0^ema_dist_20_H1=>2.35^prior_bar_sign_M1=-1.0] V [close_vs_session_open_M15=1.0^ema_dist_20_H1=1.64-2.35^bb_pos_20_2_M15=0.61-0.79] V [bb_pos_20_2_H1=0.66-0.88] V [close_vs_session_open_M1=1.0^ret_10_H1=0.0031-0.0048] V [bb_pos_20_2_H1=0.38-0.66^prior_bar_sign_H4=-1.0] V [bb_pos_20_2_H1=>1.09^dow=1^ema_dist_20_M15=>1.82] V [bb_pos_20_2_H1=0.092-0.38^prior_bar_sign_H4=-1.0^close_vs_session_open_H1=-1.0] V [close_vs_session_open_M5=1.0^ret_10_H1=0.0048-0.0079] V [ret_10_H1=0.0015-0.0031] V [ret_10_H1=>0.0079^close_vs_session_open_M1=-1.0] V [ret_10_H1=0.00025-0.0015^prior_bar_sign_H4=-1.0^bb_pos_20_2_H1=-0.27-0.092] V [ema_dist_20_H1=>2.35^bb_pos_20_2_M15=>0.79^dow=3] V [ret_10_H1=-0.001-0.00025^prior_bar_sign_H4=-1.0^bb_pos_20_2_H1=-0.27-0.092] V [bb_pos_20_2_H1=0.092-0.38^ret_3_H1=-0.00064-0.00011] V [ret_10_H1=0.00025-0.0015^ret_3_H1=-0.0015--0.00064] V [ema_dist_20_H1=>2.35] V [bb_pos_20_2_H1=0.38-0.66^ret_1_H4=0.00089-0.0018^prior_bar_sign_M5=1.0] V [bb_pos_20_2_M15=<-0.76^ret_1_M1=-0.00018--0.00011^ret_10_M5=<-0.0021] V [ema_dist_20_H1=1.64-2.35^bb_pos_20_2_H1=0.88-1.09] V [ret_10_H1=0.00025-0.0015^ret_3_H1=-0.0027--0.0015] V [bb_pos_20_2_H1=0.38-0.66^ret_1_M1=-0.00018--0.00011] V [range_norm_H4=>2.32^bb_pos_20_2_M1=-0.0032-0.22] V [bb_pos_20_2_H1=0.092-0.38^ret_3_M5=-0.00067--0.00037^prior_bar_sign_H4=-1.0]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
