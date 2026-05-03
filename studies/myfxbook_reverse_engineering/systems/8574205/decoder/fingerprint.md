# Decoder fingerprint — system 8574205

Generated: 2026-05-02T09:08:58

## Sanity (martingale + lot dynamics)

- n_trades: **3994**, deposits: 2
- pairs: {'EURJPY': 1550, 'USDJPY': 1163, 'EURUSD': 555, 'NZDUSD': 368, 'AUDUSD': 358}
- actions: {'Buy': 2139, 'Sell': 1855}
- date range: 2021-09-03 16:00:01+00:00 → 2026-05-01 17:21:35+00:00
- max gap days: 16.7
- lot p50/p95/p99/max: 0.02 / 0.02 / 0.02 / 0.02
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=1, max_streak=1
- hold p50/p95/max (h): 27.83 / 1526.99 / 11903.94

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 18:00 — 313 trades
  - 16:00 — 307 trades
  - 19:00 — 273 trades
  - 17:00 — 261 trades
  - 04:00 — 225 trades

Top entry hour:5min (UTC):
  - 16:00 — 307 trades
  - 18:00 — 306 trades
  - 19:00 — 273 trades
  - 17:00 — 257 trades
  - 04:00 — 225 trades

Exit kind distribution:
  - manual_or_time: 3994

Direction by pair (Buy %):
  - AUDUSD: total=358, buy_pct=58.1%
  - EURJPY: total=1550, buy_pct=48.4%
  - EURUSD: total=555, buy_pct=48.1%
  - NZDUSD: total=368, buy_pct=72.0%
  - USDJPY: total=1163, buy_pct=55.8%

Direction by hour (Buy %, top 5 by activity):
  - hour=18: total=313, buy_pct=52.7%
  - hour=16: total=307, buy_pct=51.8%
  - hour=19: total=273, buy_pct=50.2%
  - hour=17: total=261, buy_pct=51.3%
  - hour=04: total=225, buy_pct=56.0%

## Feature extraction

- trades processed: 3994
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | baseline | Always-Buy (y_buy mean = 0.5356); Always-Sell = 0.4644 | 0.536 | — | 1.00 | — |
| 2 | tree | DecisionTree(max_depth=4) — top features: ret_10_H4=0.25, bb_pos_20_2_H4=0.24, atr_ratio_M15=0.15, ema_dist_20_H4=0.11, ret_10_... | 0.515 | 0.030 | 1.00 | — |
| 3 | univariate | bb_pos_20_2_H1 > -0.7377 ⇒ Buy | 0.549 | — | 0.80 | 0.000 |
| 4 | univariate | ema_dist_20_H1 > -1.738 ⇒ Buy | 0.548 | — | 0.80 | 0.000 |
| 5 | univariate | ret_10_H1 > -0.005032 ⇒ Buy | 0.547 | — | 0.80 | 0.000 |
| 6 | univariate | bb_pos_20_2_H4 > -0.8347 ⇒ Buy | 0.543 | — | 0.80 | 0.000 |
| 7 | univariate | ret_3_H4 > -0.00512 ⇒ Buy | 0.541 | — | 0.80 | 0.000 |
| 8 | ripper | RIPPER ruleset: [[ret_10_H4=>0.013^dow=2^bb_pos_20_2_H4=>1.08]] | 0.479 | 0.052 | 1.00 | — |
| 9 | univariate | atr_ratio_H4 > 1.573 ⇒ Buy | 0.534 | — | 0.80 | 0.006 |
| 10 | univariate | ema_dist_20_M15 > -1.128 ⇒ Buy | 0.533 | — | 0.80 | 0.010 |

### TREE full output (rank 2)
```
DecisionTree(max_depth=4) — top features: ret_10_H4=0.25, bb_pos_20_2_H4=0.24, atr_ratio_M15=0.15, ema_dist_20_H4=0.11, ret_10_H1=0.10

|--- ret_10_H4 <= 0.01
|   |--- bb_pos_20_2_H4 <= -1.29
|   |   |--- ret_10_H4 <= -0.01
|   |   |   |--- class: 0
|   |   |--- ret_10_H4 >  -0.01
|   |   |   |--- class: 0
|   |--- bb_pos_20_2_H4 >  -1.29
|   |   |--- ema_dist_20_H4 <= -2.23
|   |   |   |--- bb_pos_20_2_H4 <= -1.16
|   |   |   |   |--- class: 0
|   |   |   |--- bb_pos_20_2_H4 >  -1.16
|   |   |   |   |--- class: 1
|   |   |--- ema_dist_20_H4 >  -2.23
|   |   |   |--- ret_10_H1 <= 0.01
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H1 >  0.01
|   |   |   |   |--- class: 1
|--- ret_10_H4 >  0.01
|   |--- atr_ratio_M15 <= 0.39
|   |   |--- bb_pos_20_2_H4 <= 0.84
|   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_H4 >  0.84
|   |   |   |--- ret_10_H1 <= 0.01
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H1 >  0.01
|   |   |   |   |--- class: 0
|   |--- atr_ratio_M15 >  0.39
|   |   |--- hour_utc <= 3.50
|   |   |   |--- class: 0
|   |   |--- hour_utc >  3.50
|   |   |   |--- bb_pos_20_2_M1 <= 0.60
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_M1 >  0.60
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 8)
```
RIPPER ruleset:
[[ret_10_H4=>0.013^dow=2^bb_pos_20_2_H4=>1.08]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
