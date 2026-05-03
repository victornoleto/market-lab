# Decoder fingerprint — system 2373850

Generated: 2026-05-02T06:10:40

## Sanity (martingale + lot dynamics)

- n_trades: **1691**, deposits: 1
- pairs: {'EURUSD': 848, 'USDCHF': 843}
- actions: {'Sell': 1487, 'Buy': 204}
- date range: 2017-11-27 23:25:24+00:00 → 2021-06-01 12:29:55+00:00
- max gap days: 221.1
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.01 / 0.01
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 25.43 / 507.54 / 1864.34

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 13:00 — 990 trades
  - 16:00 — 80 trades
  - 14:00 — 76 trades
  - 17:00 — 74 trades
  - 15:00 — 68 trades

Top entry hour:5min (UTC):
  - 13:00 — 874 trades
  - 17:55 — 24 trades
  - 13:30 — 16 trades
  - 13:05 — 16 trades
  - 16:30 — 14 trades

Exit kind distribution:
  - manual_or_time: 1691

Direction by pair (Buy %):
  - EURUSD: total=848, buy_pct=12.0%
  - USDCHF: total=843, buy_pct=12.1%

Direction by hour (Buy %, top 5 by activity):
  - hour=13: total=990, buy_pct=12.1%
  - hour=16: total=80, buy_pct=5.0%
  - hour=14: total=76, buy_pct=10.5%
  - hour=17: total=74, buy_pct=2.7%
  - hour=15: total=68, buy_pct=11.8%

## Feature extraction

- trades processed: 1691
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | baseline | Always-Buy (y_buy mean = 0.1206); Always-Sell = 0.8794 | 0.879 | — | 1.00 | — |
| 2 | tree | DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.34, hour_utc=0.18, bb_pos_20_2_H4=0.12, range_norm_H4=0.11, bb_pos_2... | 0.871 | 0.237 | 1.00 | — |
| 3 | ripper | RIPPER ruleset: [[ema_dist_20_H4=>1.69^range_norm_H4=1.04-1.17^range_norm_M1=>1.88] V [hour_utc=<11.0^ema_dist_20_H1=>1.94^ema_... | 0.868 | 0.235 | 1.00 | — |
| 4 | univariate | dow > 0 ⇒ Sell | 0.747 | — | 0.81 | 0.000 |
| 5 | univariate | ema_dist_20_H4 > 1.059 ⇒ Buy | 0.760 | — | 0.20 | 0.000 |
| 6 | univariate | ret_10_H1 > 0.00201 ⇒ Buy | 0.754 | — | 0.20 | 0.000 |
| 7 | univariate | ret_10_H4 > 0.003726 ⇒ Buy | 0.753 | — | 0.20 | 0.000 |
| 8 | univariate | ret_3_H4 > 0.00218 ⇒ Buy | 0.750 | — | 0.20 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.6107 ⇒ Buy | 0.748 | — | 0.20 | 0.000 |
| 10 | univariate | ema_dist_20_H1 > 1.194 ⇒ Buy | 0.747 | — | 0.20 | 0.000 |

### TREE full output (rank 2)
```
DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.34, hour_utc=0.18, bb_pos_20_2_H4=0.12, range_norm_H4=0.11, bb_pos_20_2_M5=0.07

|--- ema_dist_20_H4 <= 0.74
|   |--- ema_dist_20_H4 <= -0.94
|   |   |--- atr_ratio_M15 <= 0.60
|   |   |   |--- is_first_min_of_hour <= 0.50
|   |   |   |   |--- class: 0
|   |   |   |--- is_first_min_of_hour >  0.50
|   |   |   |   |--- class: 0
|   |   |--- atr_ratio_M15 >  0.60
|   |   |   |--- ret_1_M1 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_1_M1 >  0.00
|   |   |   |   |--- class: 0
|   |--- ema_dist_20_H4 >  -0.94
|   |   |--- range_norm_M1 <= 1.87
|   |   |   |--- bb_pos_20_2_M5 <= -0.61
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_M5 >  -0.61
|   |   |   |   |--- class: 0
|   |   |--- range_norm_M1 >  1.87
|   |   |   |--- class: 0
|--- ema_dist_20_H4 >  0.74
|   |--- hour_utc <= 12.50
|   |   |--- class: 0
|   |--- hour_utc >  12.50
|   |   |--- range_norm_H4 <= 1.58
|   |   |   |--- bb_pos_20_2_H4 <= 0.55
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_H4 >  0.55
|   |   |   |   |--- class: 0
|   |   |--- range_norm_H4 >  1.58
|   |   |   |--- atr_ratio_M5 <= 0.42
|   |   |   |   |--- class: 0
|   |   |   |--- atr_ratio_M5 >  0.42
|   |   |   |   |--- class: 0

```

### RIPPER full output (rank 3)
```
RIPPER ruleset:
[[ema_dist_20_H4=>1.69^range_norm_H4=1.04-1.17^range_norm_M1=>1.88] V [hour_utc=<11.0^ema_dist_20_H1=>1.94^ema_dist_20_H4=>1.69^dollar_index_proxy=1.0] V [atr_ratio_M15=0.58-0.61^ret_10_H1=0.002-0.0035^dollar_index_proxy=1.0] V [ret_3_H4=0.0022-0.0036^ret_10_M1=-9e-05--8.6e-06^close_vs_session_open_M1=-1.0] V [range_norm_H1=1.26-1.39^ema_dist_20_H1=1.19-1.94^bb_pos_20_2_H1=0.49-0.74] V [atr_ratio_M1=0.13-0.14^ret_10_H4=0.0037-0.0062^prior_bar_sign_M15=-1.0] V [range_norm_M5=1.39-1.62^ret_3_M15=-0.00038--0.00016^atr_ratio_H4=2.02-2.12]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
