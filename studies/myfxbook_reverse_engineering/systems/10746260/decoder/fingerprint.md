# Decoder fingerprint — system 10746260

Generated: 2026-05-02T02:47:59

## Sanity (martingale + lot dynamics)

- n_trades: **636**, deposits: 1
- pairs: {'GBPUSD': 202, 'USDJPY': 168, 'EURUSD': 148, 'AUDUSD': 118}
- actions: {'Sell': 319, 'Buy': 317}
- date range: 2023-05-31 04:30:04+00:00 → 2024-06-19 09:00:15+00:00
- max gap days: 12.3
- lot p50/p95/p99/max: 1.25 / 151.43 / 156.81 / 157.95
- lot p95/p50 ratio: 121.36
- martingale flag: **FAIL (martingale-like dynamics)**, steps=0, max_streak=0
- k1 flags: ['per-month max/median P95 = 128.08 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 0.00 / 0.14 / 4.00

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 15:00 — 345 trades
  - 17:00 — 151 trades
  - 09:00 — 36 trades
  - 16:00 — 35 trades
  - 10:00 — 22 trades

Top entry hour:5min (UTC):
  - 15:30 — 308 trades
  - 17:00 — 151 trades
  - 09:00 — 36 trades
  - 16:45 — 33 trades
  - 15:15 — 32 trades

Exit kind distribution:
  - manual_or_time: 636

Direction by pair (Buy %):
  - AUDUSD: total=118, buy_pct=50.8%
  - EURUSD: total=148, buy_pct=45.9%
  - GBPUSD: total=202, buy_pct=50.0%
  - USDJPY: total=168, buy_pct=52.4%

Direction by hour (Buy %, top 5 by activity):
  - hour=15: total=345, buy_pct=48.4%
  - hour=17: total=151, buy_pct=55.0%
  - hour=09: total=36, buy_pct=50.0%
  - hour=16: total=35, buy_pct=51.4%
  - hour=10: total=22, buy_pct=27.3%

## Feature extraction

- trades processed: 636
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_M15=0.52, ret_10_M5=0.12, ret_1_H1=0.09, hour_utc=0.09, ema_dist_20_H1=0.... | 0.604 | 0.084 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_H4=1.0^ret_3_H4=>0.0066^prior_bar_sign_M5=1.0] V [close_vs_session_open_H4=1.0^hour_utc... | 0.545 | 0.037 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.4984); Always-Sell = 0.5016 | 0.502 | — | 1.00 | — |
| 4 | univariate | ema_dist_20_M15 > 0.02487 ⇒ Buy | 0.662 | — | 0.50 | 0.000 |
| 5 | univariate | bb_pos_20_2_M15 > 0.004137 ⇒ Buy | 0.659 | — | 0.50 | 0.000 |
| 6 | univariate | ret_3_H4 > 0.0002648 ⇒ Buy | 0.642 | — | 0.50 | 0.000 |
| 7 | univariate | close_vs_session_open_H4 > -1 ⇒ Buy | 0.622 | — | 0.52 | 0.000 |
| 8 | univariate | ema_dist_20_H4 > 0.003686 ⇒ Buy | 0.634 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.01914 ⇒ Buy | 0.623 | — | 0.50 | 0.000 |
| 10 | univariate | ret_3_H1 > 1.378e-05 ⇒ Buy | 0.618 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_M15=0.52, ret_10_M5=0.12, ret_1_H1=0.09, hour_utc=0.09, ema_dist_20_H1=0.09

|--- bb_pos_20_2_M15 <= 0.07
|   |--- ema_dist_20_H1 <= -2.44
|   |   |--- class: 0
|   |--- ema_dist_20_H1 >  -2.44
|   |   |--- ret_10_M5 <= 0.00
|   |   |   |--- hour_utc <= 16.50
|   |   |   |   |--- class: 0
|   |   |   |--- hour_utc >  16.50
|   |   |   |   |--- class: 1
|   |   |--- ret_10_M5 >  0.00
|   |   |   |--- class: 0
|--- bb_pos_20_2_M15 >  0.07
|   |--- ret_1_H1 <= 0.00
|   |   |--- ret_1_M5 <= 0.00
|   |   |   |--- bb_pos_20_2_M15 <= 0.50
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_M15 >  0.50
|   |   |   |   |--- class: 1
|   |   |--- ret_1_M5 >  0.00
|   |   |   |--- range_norm_M1 <= 0.95
|   |   |   |   |--- class: 1
|   |   |   |--- range_norm_M1 >  0.95
|   |   |   |   |--- class: 1
|   |--- ret_1_H1 >  0.00
|   |   |--- class: 0

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_H4=1.0^ret_3_H4=>0.0066^prior_bar_sign_M5=1.0] V [close_vs_session_open_H4=1.0^hour_utc=15.0-17.0^prior_bar_sign_H4=-1.0^prior_bar_sign_H1=-1.0] V [bb_pos_20_2_M15=0.22-0.41^atr_ratio_M1=0.14-0.16]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
