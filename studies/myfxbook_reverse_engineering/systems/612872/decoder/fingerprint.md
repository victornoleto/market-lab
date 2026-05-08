# Decoder fingerprint — system 612872

Generated: 2026-05-02T07:26:17

## Sanity (martingale + lot dynamics)

- n_trades: **3136**, deposits: 813
- pairs: {'GBPUSD': 2140, 'AUDUSD': 996}
- actions: {'Sell': 1608, 'Buy': 1528}
- date range: 2013-09-06 17:00:00+00:00 → 2021-05-11 04:01:00+00:00
- max gap days: 53.9
- lot p50/p95/p99/max: 0.33 / 1.11 / 3.76 / 19.03
- lot p95/p50 ratio: 3.36
- martingale flag: **FAIL (martingale-like dynamics)**, steps=19, max_streak=1
- k1 flags: ['per-month max/median P95 = 32.90 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 14.97 / 218.79 / 2335.78

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 18:00 — 284 trades
  - 17:00 — 234 trades
  - 16:00 — 226 trades
  - 12:00 — 216 trades
  - 19:00 — 209 trades

Top entry hour:5min (UTC):
  - 18:00 — 279 trades
  - 17:00 — 227 trades
  - 16:00 — 223 trades
  - 12:00 — 214 trades
  - 19:00 — 204 trades

Exit kind distribution:
  - manual_or_time: 3136

Direction by pair (Buy %):
  - AUDUSD: total=996, buy_pct=47.5%
  - GBPUSD: total=2140, buy_pct=49.3%

Direction by hour (Buy %, top 5 by activity):
  - hour=18: total=284, buy_pct=45.8%
  - hour=17: total=234, buy_pct=50.4%
  - hour=16: total=226, buy_pct=45.6%
  - hour=12: total=216, buy_pct=49.1%
  - hour=19: total=209, buy_pct=48.3%

## Feature extraction

- trades processed: 3136
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_3_H4=0.42, is_first_min_of_hour=0.13, range_norm_M1=0.08, ema_dist_20_M15=0.07, h... | 0.544 | 0.039 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[ret_10_H1=0.004-0.0064] V [ret_10_H1=>0.0064]] | 0.535 | 0.080 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.4872); Always-Sell = 0.5128 | 0.513 | — | 1.00 | — |
| 4 | univariate | ema_dist_20_M15 > -0.4008 ⇒ Buy | 0.546 | — | 0.60 | 0.000 |
| 5 | univariate | ema_dist_20_H1 > -0.03441 ⇒ Buy | 0.566 | — | 0.50 | 0.000 |
| 6 | univariate | bb_pos_20_2_H1 > -0.02746 ⇒ Buy | 0.564 | — | 0.50 | 0.000 |
| 7 | univariate | bb_pos_20_2_H4 > -0.03727 ⇒ Buy | 0.563 | — | 0.50 | 0.000 |
| 8 | univariate | close_vs_session_open_H4 > -1 ⇒ Buy | 0.533 | — | 0.52 | 0.071 |
| 9 | univariate | bb_pos_20_2_M15 > -0.02292 ⇒ Buy | 0.532 | — | 0.50 | 0.100 |
| 10 | univariate | ret_10_H1 > 0.001157 ⇒ Buy | 0.573 | — | 0.40 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_3_H4=0.42, is_first_min_of_hour=0.13, range_norm_M1=0.08, ema_dist_20_M15=0.07, hour_utc=0.07

|--- ret_3_H4 <= 0.00
|   |--- is_first_min_of_hour <= 0.50
|   |   |--- class: 1
|   |--- is_first_min_of_hour >  0.50
|   |   |--- atr_ratio_M15 <= 0.31
|   |   |   |--- atr_ratio_H4 <= 1.45
|   |   |   |   |--- class: 1
|   |   |   |--- atr_ratio_H4 >  1.45
|   |   |   |   |--- class: 0
|   |   |--- atr_ratio_M15 >  0.31
|   |   |   |--- bb_pos_20_2_H4 <= -0.89
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_H4 >  -0.89
|   |   |   |   |--- class: 0
|--- ret_3_H4 >  0.00
|   |--- range_norm_M1 <= 2.20
|   |   |--- ret_10_H1 <= 0.00
|   |   |   |--- ema_dist_20_M15 <= 0.37
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_M15 >  0.37
|   |   |   |   |--- class: 0
|   |   |--- ret_10_H1 >  0.00
|   |   |   |--- hour_utc <= 6.50
|   |   |   |   |--- class: 0
|   |   |   |--- hour_utc >  6.50
|   |   |   |   |--- class: 1
|   |--- range_norm_M1 >  2.20
|   |   |--- ret_3_M15 <= -0.00
|   |   |   |--- class: 1
|   |   |--- ret_3_M15 >  -0.00
|   |   |   |--- class: 0

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[ret_10_H1=0.004-0.0064] V [ret_10_H1=>0.0064]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
