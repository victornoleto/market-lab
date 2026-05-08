# Decoder fingerprint — system 1612420

Generated: 2026-05-02T05:08:48

## Sanity (martingale + lot dynamics)

- n_trades: **788**, deposits: 68
- pairs: {'EURUSD': 272, 'GBPUSD': 227, 'AUDUSD': 165, 'USDJPY': 124}
- actions: {'Buy': 398, 'Sell': 390}
- date range: 2016-02-25 15:30:03+00:00 → 2021-06-10 15:40:55+00:00
- max gap days: 34.8
- lot p50/p95/p99/max: 3.48 / 5.38 / 5.79 / 6.27
- lot p95/p50 ratio: 1.54
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.01 / 0.46 / 5.83

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 15:00 — 405 trades
  - 17:00 — 107 trades
  - 11:00 — 76 trades
  - 04:00 — 36 trades
  - 14:00 — 31 trades

Top entry hour:5min (UTC):
  - 15:30 — 356 trades
  - 17:00 — 95 trades
  - 11:30 — 72 trades
  - 04:30 — 36 trades
  - 02:30 — 31 trades

Exit kind distribution:
  - manual_or_time: 788

Direction by pair (Buy %):
  - AUDUSD: total=165, buy_pct=55.8%
  - EURUSD: total=272, buy_pct=47.4%
  - GBPUSD: total=227, buy_pct=51.1%
  - USDJPY: total=124, buy_pct=49.2%

Direction by hour (Buy %, top 5 by activity):
  - hour=15: total=405, buy_pct=50.4%
  - hour=17: total=107, buy_pct=45.8%
  - hour=11: total=76, buy_pct=47.4%
  - hour=04: total=36, buy_pct=50.0%
  - hour=14: total=31, buy_pct=48.4%

## Feature extraction

- trades processed: 788
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_3_H4=0.52, ret_10_M5=0.09, range_norm_M1=0.08, ema_dist_20_H1=0.08, ema_dist_20_M... | 0.649 | 0.012 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M5=1.0^ema_dist_20_H1=>2.27^pair_cluster_dispersion=0.00057-0.00068] V [close_vs_sessio... | 0.523 | 0.039 | 1.00 | — |
| 3 | univariate | ret_3_H4 > -0.0008685 ⇒ Buy | 0.666 | — | 0.60 | 0.000 |
| 4 | baseline | Always-Buy (y_buy mean = 0.5051); Always-Sell = 0.4949 | 0.505 | — | 1.00 | — |
| 5 | univariate | ema_dist_20_M15 > -0.3183 ⇒ Buy | 0.631 | — | 0.60 | 0.000 |
| 6 | univariate | ema_dist_20_H4 > -0.2576 ⇒ Buy | 0.626 | — | 0.60 | 0.000 |
| 7 | univariate | ret_10_H4 > -0.00124 ⇒ Buy | 0.613 | — | 0.60 | 0.000 |
| 8 | univariate | bb_pos_20_2_H1 > 0.08711 ⇒ Buy | 0.670 | — | 0.50 | 0.000 |
| 9 | univariate | ret_10_H1 > 0.0001868 ⇒ Buy | 0.662 | — | 0.50 | 0.000 |
| 10 | univariate | ema_dist_20_H1 > 0.08383 ⇒ Buy | 0.662 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_3_H4=0.52, ret_10_M5=0.09, range_norm_M1=0.08, ema_dist_20_H1=0.08, ema_dist_20_M15=0.07

|--- ret_3_H4 <= -0.00
|   |--- ema_dist_20_H1 <= -2.82
|   |   |--- class: 0
|   |--- ema_dist_20_H1 >  -2.82
|   |   |--- range_norm_M1 <= 0.81
|   |   |   |--- range_norm_M1 <= 0.67
|   |   |   |   |--- class: 0
|   |   |   |--- range_norm_M1 >  0.67
|   |   |   |   |--- class: 1
|   |   |--- range_norm_M1 >  0.81
|   |   |   |--- range_norm_H4 <= 1.30
|   |   |   |   |--- class: 0
|   |   |   |--- range_norm_H4 >  1.30
|   |   |   |   |--- class: 0
|--- ret_3_H4 >  -0.00
|   |--- ret_10_M5 <= 0.00
|   |   |--- ema_dist_20_M15 <= 1.10
|   |   |   |--- bb_pos_20_2_M5 <= 0.23
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_M5 >  0.23
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_M15 >  1.10
|   |   |   |--- range_norm_H1 <= 0.95
|   |   |   |   |--- class: 1
|   |   |   |--- range_norm_H1 >  0.95
|   |   |   |   |--- class: 1
|   |--- ret_10_M5 >  0.00
|   |   |--- class: 0

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M5=1.0^ema_dist_20_H1=>2.27^pair_cluster_dispersion=0.00057-0.00068] V [close_vs_session_open_M5=1.0^ema_dist_20_M15=>1.79^ret_3_H4=>0.0055] V [bb_pos_20_2_M1=-0.23--0.01^ret_1_M5=0.00017-0.00027] V [dow=4^prior_bar_sign_M15=1.0^ret_3_M1=0.00011-0.0002] V [prior_bar_sign_H4=1.0^dow=4^ret_3_H4=0.0035-0.0055] V [ret_10_M15=-0.002--0.0012^ret_10_M5=-0.00055--0.00028]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
