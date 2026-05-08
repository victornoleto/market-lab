# Decoder fingerprint — system 1152318

Generated: 2026-05-02T04:17:50

## Sanity (martingale + lot dynamics)

- n_trades: **1637**, deposits: 2
- pairs: {'AUDUSD': 887, 'EURCHF': 750}
- actions: {'Buy': 820, 'Sell': 817}
- date range: 2015-01-05 15:06:00+00:00 → 2021-06-01 02:31:00+00:00
- max gap days: 70.5
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.01 / 0.01
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 118.38 / 872.01 / 2087.33

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 03:00 — 151 trades
  - 09:00 — 128 trades
  - 04:00 — 123 trades
  - 17:00 — 118 trades
  - 10:00 — 112 trades

Top entry hour:5min (UTC):
  - 04:30 — 25 trades
  - 17:55 — 19 trades
  - 03:05 — 18 trades
  - 03:30 — 18 trades
  - 02:30 — 17 trades

Exit kind distribution:
  - manual_or_time: 1637

Direction by pair (Buy %):
  - AUDUSD: total=887, buy_pct=47.8%
  - EURCHF: total=750, buy_pct=52.8%

Direction by hour (Buy %, top 5 by activity):
  - hour=03: total=151, buy_pct=47.0%
  - hour=09: total=128, buy_pct=45.3%
  - hour=04: total=123, buy_pct=48.0%
  - hour=17: total=118, buy_pct=64.4%
  - hour=10: total=112, buy_pct=46.4%

## Feature extraction

- trades processed: 1637
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ema_dist_20_H1=0.62, ema_dist_20_H4=0.14, ret_1_H1=0.10, bb_pos_20_2_H1=0.05, ret_1_H... | 0.739 | 0.063 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M15=-1.0^ema_dist_20_H1=<-1.91^bb_pos_20_2_M15=-0.76--0.56] V [close_vs_session_open_M1... | 0.660 | 0.039 | 1.00 | — |
| 3 | univariate | ema_dist_20_H1 > 0.02548 ⇒ Sell | 0.744 | — | 0.50 | 0.000 |
| 4 | univariate | bb_pos_20_2_H4 > 0.02092 ⇒ Sell | 0.739 | — | 0.50 | 0.000 |
| 5 | univariate | ema_dist_20_H4 > 0.02856 ⇒ Sell | 0.738 | — | 0.50 | 0.000 |
| 6 | univariate | ret_10_H1 > -1.419e-05 ⇒ Sell | 0.737 | — | 0.50 | 0.000 |
| 7 | univariate | bb_pos_20_2_H1 > -0.007585 ⇒ Sell | 0.737 | — | 0.50 | 0.000 |
| 8 | univariate | ret_3_H4 > 0 ⇒ Sell | 0.711 | — | 0.50 | 0.000 |
| 9 | baseline | Always-Buy (y_buy mean = 0.5009); Always-Sell = 0.4991 | 0.501 | — | 1.00 | — |
| 10 | univariate | ret_10_H4 > 6.357e-05 ⇒ Sell | 0.703 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ema_dist_20_H1=0.62, ema_dist_20_H4=0.14, ret_1_H1=0.10, bb_pos_20_2_H1=0.05, ret_1_H4=0.03

|--- ema_dist_20_H1 <= 0.22
|   |--- ema_dist_20_H4 <= -0.26
|   |   |--- ret_1_H1 <= -0.00
|   |   |   |--- ret_10_H1 <= -0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_10_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |   |--- ret_1_H1 >  -0.00
|   |   |   |--- ema_dist_20_H1 <= -0.34
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_H1 >  -0.34
|   |   |   |   |--- class: 1
|   |--- ema_dist_20_H4 >  -0.26
|   |   |--- ret_1_H4 <= -0.00
|   |   |   |--- bb_pos_20_2_H1 <= -0.37
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_H1 >  -0.37
|   |   |   |   |--- class: 0
|   |   |--- ret_1_H4 >  -0.00
|   |   |   |--- ret_1_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_1_H1 >  -0.00
|   |   |   |   |--- class: 1
|--- ema_dist_20_H1 >  0.22
|   |--- ema_dist_20_H4 <= 0.39
|   |   |--- atr_ratio_M15 <= 0.58
|   |   |   |--- ret_1_H1 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_1_H1 >  0.00
|   |   |   |   |--- class: 0
|   |   |--- atr_ratio_M15 >  0.58
|   |   |   |--- class: 1
|   |--- ema_dist_20_H4 >  0.39
|   |   |--- bb_pos_20_2_H1 <= 0.39
|   |   |   |--- ret_1_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_1_H1 >  -0.00
|   |   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_H1 >  0.39
|   |   |   |--- bb_pos_20_2_M15 <= 0.10
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_M15 >  0.10
|   |   |   |   |--- class: 0

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M15=-1.0^ema_dist_20_H1=<-1.91^bb_pos_20_2_M15=-0.76--0.56] V [close_vs_session_open_M15=-1.0^bb_pos_20_2_H1=-0.94--0.71] V [close_vs_session_open_M15=-1.0^bb_pos_20_2_H1=-0.71--0.5] V [close_vs_session_open_M1=-1.0^bb_pos_20_2_H1=<-0.94^ret_1_H4=-0.0025--0.0015] V [ema_dist_20_H4=-1.88--1.32^prior_bar_sign_H1=1.0^prior_bar_sign_M15=-1.0] V [ema_dist_20_H1=-0.83--0.38^prior_bar_sign_H1=1.0^prior_bar_sign_M5=1.0] V [close_vs_session_open_M5=-1.0^bb_pos_20_2_H1=<-0.94^atr_ratio_M1=0.14-0.16] V [ema_dist_20_H4=<-1.88^prior_bar_sign_H1=1.0^close_vs_session_open_M1=1.0] V [ret_10_H1=-0.0036--0.0022^close_vs_session_open_M5=1.0^prior_bar_sign_M15=-1.0] V [ema_dist_20_H1=-0.38-0.018^prior_bar_sign_H1=1.0^close_vs_session_open_M1=1.0] V [bb_pos_20_2_M15=-0.56--0.37^prior_bar_sign_M5=-1.0] V [bb_pos_20_2_H4=-0.49--0.25^ret_3_H4=-0.00073-0.0] V [ema_dist_20_H4=<-1.88^ema_dist_20_H1=<-1.91] V [ema_dist_20_H4=-1.88--1.32] V [ema_dist_20_M15=-0.31-0.015^atr_ratio_H4=1.56-1.71] V [bb_pos_20_2_M5=0.6-0.81^ema_dist_20_H4=-1.32--0.8]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
