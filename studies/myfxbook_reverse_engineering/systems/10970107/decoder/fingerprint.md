# Decoder fingerprint — system 10970107

Generated: 2026-05-02T02:56:57

## Sanity (martingale + lot dynamics)

- n_trades: **835**, deposits: 1
- pairs: {'USDJPY': 271, 'GBPUSD': 240, 'EURUSD': 198, 'AUDUSD': 126}
- actions: {'Sell': 419, 'Buy': 416}
- date range: 2024-02-29 15:30:04+00:00 → 2026-01-30 15:49:42+00:00
- max gap days: 14.5
- lot p50/p95/p99/max: 1.28 / 156.33 / 158.81 / 161.60
- lot p95/p50 ratio: 121.97
- martingale flag: **FAIL (martingale-like dynamics)**, steps=0, max_streak=0
- k1 flags: ['per-month max/median P95 = 127.98 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 0.00 / 0.13 / 16.12

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 15:00 — 461 trades
  - 17:00 — 179 trades
  - 16:00 — 49 trades
  - 09:00 — 39 trades
  - 10:00 — 28 trades

Top entry hour:5min (UTC):
  - 15:30 — 421 trades
  - 17:00 — 179 trades
  - 16:45 — 49 trades
  - 09:00 — 39 trades
  - 15:15 — 38 trades

Exit kind distribution:
  - manual_or_time: 835

Direction by pair (Buy %):
  - AUDUSD: total=126, buy_pct=60.3%
  - EURUSD: total=198, buy_pct=51.5%
  - GBPUSD: total=240, buy_pct=48.8%
  - USDJPY: total=271, buy_pct=44.6%

Direction by hour (Buy %, top 5 by activity):
  - hour=15: total=461, buy_pct=51.4%
  - hour=17: total=179, buy_pct=48.0%
  - hour=16: total=49, buy_pct=46.9%
  - hour=09: total=39, buy_pct=43.6%
  - hour=10: total=28, buy_pct=42.9%

## Feature extraction

- trades processed: 835
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ema_dist_20_H1=0.48, ema_dist_20_M15=0.14, bb_pos_20_2_M5=0.11, ret_3_M15=0.08, ret_1... | 0.649 | 0.044 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_H4=1.0^prior_bar_sign_H1=-1.0^is_first_min_of_hour=1^dollar_index_proxy=1.0^hour_utc=15... | 0.562 | 0.039 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.4982); Always-Sell = 0.5018 | 0.502 | — | 1.00 | — |
| 4 | univariate | bb_pos_20_2_M15 > -0.2336 ⇒ Buy | 0.611 | — | 0.60 | 0.000 |
| 5 | univariate | ema_dist_20_M15 > -0.3604 ⇒ Buy | 0.606 | — | 0.60 | 0.000 |
| 6 | univariate | ema_dist_20_H1 > -0.02232 ⇒ Buy | 0.654 | — | 0.50 | 0.000 |
| 7 | univariate | ret_10_H1 > -0.000106 ⇒ Buy | 0.651 | — | 0.50 | 0.000 |
| 8 | univariate | bb_pos_20_2_H1 > -0.02139 ⇒ Buy | 0.649 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.03558 ⇒ Buy | 0.644 | — | 0.50 | 0.000 |
| 10 | univariate | ema_dist_20_H4 > -0.008453 ⇒ Buy | 0.642 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ema_dist_20_H1=0.48, ema_dist_20_M15=0.14, bb_pos_20_2_M5=0.11, ret_3_M15=0.08, ret_1_H1=0.06

|--- ema_dist_20_H1 <= -0.39
|   |--- ret_3_M15 <= 0.00
|   |   |--- ema_dist_20_H1 <= -1.15
|   |   |   |--- range_norm_H4 <= 1.52
|   |   |   |   |--- class: 0
|   |   |   |--- range_norm_H4 >  1.52
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_H1 >  -1.15
|   |   |   |--- class: 1
|   |--- ret_3_M15 >  0.00
|   |   |--- bb_pos_20_2_M15 <= -0.24
|   |   |   |--- class: 0
|   |   |--- bb_pos_20_2_M15 >  -0.24
|   |   |   |--- class: 0
|--- ema_dist_20_H1 >  -0.39
|   |--- bb_pos_20_2_M5 <= -0.33
|   |   |--- ret_10_M15 <= -0.00
|   |   |   |--- class: 1
|   |   |--- ret_10_M15 >  -0.00
|   |   |   |--- class: 1
|   |--- bb_pos_20_2_M5 >  -0.33
|   |   |--- ema_dist_20_M15 <= 1.30
|   |   |   |--- ret_1_H1 <= -0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_1_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_M15 >  1.30
|   |   |   |--- bb_pos_20_2_M15 <= 0.73
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_M15 >  0.73
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_H4=1.0^prior_bar_sign_H1=-1.0^is_first_min_of_hour=1^dollar_index_proxy=1.0^hour_utc=15.8-17.0] V [close_vs_session_open_H4=1.0^ema_dist_20_M15=>1.6] V [prior_bar_sign_H1=-1.0^bb_pos_20_2_H1=0.32-0.62] V [prior_bar_sign_H4=1.0^hour_utc=10.0-15.0^close_vs_session_open_M1=-1.0] V [prior_bar_sign_H1=-1.0^ret_3_H4=0.0034-0.0057] V [ema_dist_20_H4=0.42-0.86^bb_pos_20_2_H4=0.036-0.29] V [bb_pos_20_2_M5=-0.62--0.43^bb_pos_20_2_H1=-0.32--0.021]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
