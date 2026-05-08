# Decoder fingerprint — system 8577442

Generated: 2026-05-02T09:55:33

## Sanity (martingale + lot dynamics)

- n_trades: **934**, deposits: 1
- pairs: {'USDCAD': 311, 'AUDUSD': 201, 'AUDCAD': 149, 'CADCHF': 138, 'AUDCHF': 135}
- actions: {'Buy': 511, 'Sell': 423}
- date range: 2021-06-21 16:20:47+00:00 → 2026-04-27 15:17:32+00:00
- max gap days: 74.5
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.01 / 0.01
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 213.99 / 2052.79 / 5209.24

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 17:00 — 111 trades
  - 15:00 — 87 trades
  - 16:00 — 85 trades
  - 10:00 — 67 trades
  - 04:00 — 45 trades

Top entry hour:5min (UTC):
  - 15:30 — 26 trades
  - 17:00 — 19 trades
  - 00:00 — 16 trades
  - 16:45 — 16 trades
  - 17:05 — 15 trades

Exit kind distribution:
  - manual_or_time: 934

Direction by pair (Buy %):
  - AUDCAD: total=149, buy_pct=51.0%
  - AUDCHF: total=135, buy_pct=65.9%
  - AUDUSD: total=201, buy_pct=61.2%
  - CADCHF: total=138, buy_pct=44.2%
  - USDCAD: total=311, buy_pct=52.1%

Direction by hour (Buy %, top 5 by activity):
  - hour=17: total=111, buy_pct=60.4%
  - hour=15: total=87, buy_pct=49.4%
  - hour=16: total=85, buy_pct=49.4%
  - hour=10: total=67, buy_pct=52.2%
  - hour=04: total=45, buy_pct=62.2%

## Feature extraction

- trades processed: 934
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.60, ret_10_H1=0.16, ret_10_H4=0.08, ret_10_M5=0.05, ret_10_M1=0.05  ... | 0.619 | 0.034 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.5471); Always-Sell = 0.4529 | 0.547 | — | 1.00 | — |
| 3 | univariate | ret_1_M5 > -0.0002452 ⇒ Buy | 0.559 | — | 0.80 | 0.097 |
| 4 | univariate | ema_dist_20_M1 > -1.234 ⇒ Buy | 0.550 | — | 0.80 | 0.630 |
| 5 | ripper | RIPPER ruleset: [[ret_10_H4=<-0.013] V [ret_1_M15=-0.0007--0.00044]] | 0.491 | 0.031 | 1.00 | — |
| 6 | univariate | ret_1_M1 > -7.161e-05 ⇒ Buy | 0.560 | — | 0.70 | 0.075 |
| 7 | univariate | bb_pos_20_2_H4 > -0.522 ⇒ Sell | 0.586 | — | 0.60 | 0.000 |
| 8 | univariate | ret_10_H4 > -0.0009182 ⇒ Sell | 0.585 | — | 0.50 | 0.000 |
| 9 | univariate | ema_dist_20_H4 > -0.2121 ⇒ Sell | 0.582 | — | 0.50 | 0.000 |
| 10 | univariate | ret_3_H1 > 0.0009061 ⇒ Sell | 0.547 | — | 0.30 | 1.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.60, ret_10_H1=0.16, ret_10_H4=0.08, ret_10_M5=0.05, ret_10_M1=0.05

|--- ema_dist_20_H4 <= -1.75
|   |--- ret_10_M1 <= 0.00
|   |   |--- ret_10_M5 <= -0.00
|   |   |   |--- class: 1
|   |   |--- ret_10_M5 >  -0.00
|   |   |   |--- class: 1
|   |--- ret_10_M1 >  0.00
|   |   |--- class: 1
|--- ema_dist_20_H4 >  -1.75
|   |--- ret_10_H1 <= 0.00
|   |   |--- ema_dist_20_H4 <= -0.60
|   |   |   |--- ret_10_H4 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H4 >  -0.00
|   |   |   |   |--- class: 1
|   |   |--- ema_dist_20_H4 >  -0.60
|   |   |   |--- ret_10_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |--- ret_10_H1 >  0.00
|   |   |--- ema_dist_20_H4 <= 0.72
|   |   |   |--- class: 1
|   |   |--- ema_dist_20_H4 >  0.72
|   |   |   |--- dow <= 2.50
|   |   |   |   |--- class: 0
|   |   |   |--- dow >  2.50
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 5)
```
RIPPER ruleset:
[[ret_10_H4=<-0.013] V [ret_1_M15=-0.0007--0.00044]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
