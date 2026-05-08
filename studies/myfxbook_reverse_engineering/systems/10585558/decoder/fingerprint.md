# Decoder fingerprint — system 10585558

Generated: 2026-05-02T02:28:52

## Sanity (martingale + lot dynamics)

- n_trades: **1611**, deposits: 1
- pairs: {'GBPUSD': 476, 'USDJPY': 471, 'EURUSD': 372, 'AUDUSD': 292}
- actions: {'Sell': 806, 'Buy': 805}
- date range: 2023-02-16 02:30:04+00:00 → 2026-04-23 11:30:01+00:00
- max gap days: 14.5
- lot p50/p95/p99/max: 1.26 / 154.79 / 158.67 / 161.60
- lot p95/p50 ratio: 123.26
- martingale flag: **FAIL (martingale-like dynamics)**, steps=0, max_streak=0
- k1 flags: ['per-month max/median P95 = 126.41 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 0.00 / 0.12 / 8.94

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 15:00 — 895 trades
  - 17:00 — 347 trades
  - 16:00 — 105 trades
  - 09:00 — 69 trades
  - 10:00 — 50 trades

Top entry hour:5min (UTC):
  - 15:30 — 802 trades
  - 17:00 — 347 trades
  - 16:45 — 102 trades
  - 15:15 — 78 trades
  - 09:00 — 69 trades

Exit kind distribution:
  - manual_or_time: 1611

Direction by pair (Buy %):
  - AUDUSD: total=292, buy_pct=52.1%
  - EURUSD: total=372, buy_pct=49.5%
  - GBPUSD: total=476, buy_pct=51.9%
  - USDJPY: total=471, buy_pct=47.1%

Direction by hour (Buy %, top 5 by activity):
  - hour=15: total=895, buy_pct=50.5%
  - hour=17: total=347, buy_pct=51.6%
  - hour=16: total=105, buy_pct=41.9%
  - hour=09: total=69, buy_pct=53.6%
  - hour=10: total=50, buy_pct=36.0%

## Feature extraction

- trades processed: 1611
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.38, bb_pos_20_2_M15=0.17, bb_pos_20_2_M5=0.13, ema_dist_20_M15=0.09,... | 0.604 | 0.026 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_H4=1.0^ret_3_H4=>0.0059] V [close_vs_session_open_H4=1.0^prior_bar_sign_H1=-1.0^ret_3_H... | 0.537 | 0.037 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.4997); Always-Sell = 0.5003 | 0.500 | — | 1.00 | — |
| 4 | univariate | ema_dist_20_H4 > -0.3786 ⇒ Buy | 0.636 | — | 0.60 | 0.000 |
| 5 | univariate | ema_dist_20_H1 > -0.4832 ⇒ Buy | 0.633 | — | 0.60 | 0.000 |
| 6 | univariate | ret_3_H4 > -0.001223 ⇒ Buy | 0.622 | — | 0.60 | 0.000 |
| 7 | univariate | bb_pos_20_2_M15 > -0.2405 ⇒ Buy | 0.618 | — | 0.60 | 0.000 |
| 8 | univariate | ret_10_H1 > -0.0001267 ⇒ Buy | 0.636 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.01433 ⇒ Buy | 0.624 | — | 0.50 | 0.000 |
| 10 | univariate | ret_10_H4 > 1.838e-05 ⇒ Buy | 0.620 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.38, bb_pos_20_2_M15=0.17, bb_pos_20_2_M5=0.13, ema_dist_20_M15=0.09, ema_dist_20_H1=0.09

|--- ema_dist_20_H4 <= -0.37
|   |--- bb_pos_20_2_M15 <= -0.23
|   |   |--- bb_pos_20_2_M15 <= -0.64
|   |   |   |--- range_norm_H1 <= 1.16
|   |   |   |   |--- class: 1
|   |   |   |--- range_norm_H1 >  1.16
|   |   |   |   |--- class: 0
|   |   |--- bb_pos_20_2_M15 >  -0.64
|   |   |   |--- ema_dist_20_M15 <= -1.08
|   |   |   |   |--- class: 0
|   |   |   |--- ema_dist_20_M15 >  -1.08
|   |   |   |   |--- class: 0
|   |--- bb_pos_20_2_M15 >  -0.23
|   |   |--- bb_pos_20_2_M5 <= 0.31
|   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_M5 >  0.31
|   |   |   |--- atr_ratio_M1 <= 0.12
|   |   |   |   |--- class: 0
|   |   |   |--- atr_ratio_M1 >  0.12
|   |   |   |   |--- class: 0
|--- ema_dist_20_H4 >  -0.37
|   |--- ema_dist_20_H1 <= 1.34
|   |   |--- bb_pos_20_2_M5 <= -0.11
|   |   |   |--- ema_dist_20_M15 <= -1.28
|   |   |   |   |--- class: 0
|   |   |   |--- ema_dist_20_M15 >  -1.28
|   |   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_M5 >  -0.11
|   |   |   |--- ema_dist_20_M1 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ema_dist_20_M1 >  0.00
|   |   |   |   |--- class: 1
|   |--- ema_dist_20_H1 >  1.34
|   |   |--- bb_pos_20_2_M15 <= 0.64
|   |   |   |--- ema_dist_20_M15 <= 1.36
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_M15 >  1.36
|   |   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_M15 >  0.64
|   |   |   |--- ret_3_H4 <= 0.01
|   |   |   |   |--- class: 0
|   |   |   |--- ret_3_H4 >  0.01
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_H4=1.0^ret_3_H4=>0.0059] V [close_vs_session_open_H4=1.0^prior_bar_sign_H1=-1.0^ret_3_H4=0.0036-0.0059] V [prior_bar_sign_H4=1.0^hour_utc=10.0-15.0^close_vs_session_open_H1=-1.0]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
