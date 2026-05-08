# Decoder fingerprint — system 10067081

Generated: 2026-05-02T01:06:44

## Sanity (martingale + lot dynamics)

- n_trades: **4000**, deposits: 0
- pairs: {'USDJPY': 1661, 'GBPUSD': 963, 'USDCAD': 475, 'AUDUSD': 339, 'EURGBP': 303, 'EURCHF': 259}
- actions: {'Buy': 2063, 'Sell': 1937}
- date range: 2024-10-08 06:05:00+00:00 → 2026-04-30 22:10:51+00:00
- max gap days: 2.5
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.01 / 0.01
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 3.00 / 213.72 / 4449.09

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 03:00 — 465 trades
  - 10:00 — 276 trades
  - 17:00 — 275 trades
  - 18:00 — 254 trades
  - 15:00 — 235 trades

Top entry hour:5min (UTC):
  - 03:00 — 227 trades
  - 02:00 — 95 trades
  - 15:35 — 47 trades
  - 18:35 — 43 trades
  - 19:35 — 43 trades

Exit kind distribution:
  - manual_or_time: 4000

Direction by pair (Buy %):
  - AUDUSD: total=339, buy_pct=59.9%
  - EURCHF: total=259, buy_pct=57.5%
  - EURGBP: total=303, buy_pct=62.0%
  - GBPUSD: total=963, buy_pct=50.5%
  - USDCAD: total=475, buy_pct=48.8%
  - USDJPY: total=1661, buy_pct=48.5%

Direction by hour (Buy %, top 5 by activity):
  - hour=03: total=465, buy_pct=48.6%
  - hour=10: total=276, buy_pct=44.9%
  - hour=17: total=275, buy_pct=53.1%
  - hour=18: total=254, buy_pct=55.5%
  - hour=15: total=235, buy_pct=58.7%

## Feature extraction

- trades processed: 4000
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_3_H4=0.24, bb_pos_20_2_H1=0.17, bb_pos_20_2_H4=0.13, ema_dist_20_H4=0.12, ema_dis... | 0.562 | 0.031 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.5158); Always-Sell = 0.4842 | 0.516 | — | 1.00 | — |
| 3 | univariate | ema_dist_20_M15 > -1.027 ⇒ Buy | 0.560 | — | 0.80 | 0.000 |
| 4 | ripper | RIPPER ruleset: [[close_vs_session_open_H1=1.0^ret_10_H1=>0.0054^dow=3^ret_10_M15=>0.0021]] | 0.488 | 0.055 | 1.00 | — |
| 5 | univariate | bb_pos_20_2_H4 > -0.7121 ⇒ Buy | 0.543 | — | 0.80 | 0.000 |
| 6 | univariate | bb_pos_20_2_H1 > -0.4675 ⇒ Buy | 0.564 | — | 0.70 | 0.000 |
| 7 | univariate | ret_10_H1 > -0.001588 ⇒ Buy | 0.557 | — | 0.70 | 0.000 |
| 8 | univariate | ret_3_H4 > -0.001744 ⇒ Buy | 0.556 | — | 0.70 | 0.000 |
| 9 | univariate | bb_pos_20_2_M15 > -0.1508 ⇒ Buy | 0.565 | — | 0.60 | 0.000 |
| 10 | univariate | ema_dist_20_H1 > -0.3612 ⇒ Buy | 0.557 | — | 0.60 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_3_H4=0.24, bb_pos_20_2_H1=0.17, bb_pos_20_2_H4=0.13, ema_dist_20_H4=0.12, ema_dist_20_H1=0.07

|--- ret_3_H4 <= 0.00
|   |--- bb_pos_20_2_H1 <= -1.06
|   |   |--- ret_1_H1 <= -0.00
|   |   |   |--- class: 0
|   |   |--- ret_1_H1 >  -0.00
|   |   |   |--- range_norm_M1 <= 0.96
|   |   |   |   |--- class: 0
|   |   |   |--- range_norm_M1 >  0.96
|   |   |   |   |--- class: 0
|   |--- bb_pos_20_2_H1 >  -1.06
|   |   |--- ema_dist_20_H4 <= 1.84
|   |   |   |--- bb_pos_20_2_M15 <= 0.07
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_M15 >  0.07
|   |   |   |   |--- class: 1
|   |   |--- ema_dist_20_H4 >  1.84
|   |   |   |--- range_norm_H1 <= 0.83
|   |   |   |   |--- class: 0
|   |   |   |--- range_norm_H1 >  0.83
|   |   |   |   |--- class: 0
|--- ret_3_H4 >  0.00
|   |--- ret_10_H4 <= 0.01
|   |   |--- pair_cluster_dispersion <= 0.00
|   |   |   |--- bb_pos_20_2_H1 <= 0.54
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_H1 >  0.54
|   |   |   |   |--- class: 1
|   |   |--- pair_cluster_dispersion >  0.00
|   |   |   |--- atr_ratio_M15 <= 0.67
|   |   |   |   |--- class: 1
|   |   |   |--- atr_ratio_M15 >  0.67
|   |   |   |   |--- class: 1
|   |--- ret_10_H4 >  0.01
|   |   |--- bb_pos_20_2_H4 <= 1.13
|   |   |   |--- ema_dist_20_H1 <= 2.05
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_H1 >  2.05
|   |   |   |   |--- class: 0
|   |   |--- bb_pos_20_2_H4 >  1.13
|   |   |   |--- ema_dist_20_H4 <= 2.79
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_H4 >  2.79
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 4)
```
RIPPER ruleset:
[[close_vs_session_open_H1=1.0^ret_10_H1=>0.0054^dow=3^ret_10_M15=>0.0021]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
