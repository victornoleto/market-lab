# Decoder fingerprint — system 1407880

Generated: 2026-05-01T20:07:58
⚠ Sampled run: only the most-recent 300 trades were used (full = 3304)

## Sanity (martingale + lot dynamics)

- n_trades: **3304**, deposits: 95
- pairs: {'GBPUSD': 898, 'USDCAD': 807, 'EURUSD': 703, 'EURCHF': 370, 'USDCHF': 287, 'EURGBP': 239}
- actions: {'Sell': 1712, 'Buy': 1592}
- date range: 2013-09-02 00:00:00+00:00 → 2021-06-16 00:46:00+00:00
- max gap days: 33.9
- lot p50/p95/p99/max: 3.76 / 15.16 / 16.64 / 17.05
- lot p95/p50 ratio: 4.03
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.98 / 3.15 / 8.60

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 00:00 — 1680 trades
  - 23:00 — 1375 trades
  - 01:00 — 248 trades
  - 22:00 — 1 trades
  - 04:00 — 0 trades

Top entry hour:5min (UTC):
  - 00:00 — 415 trades
  - 23:00 — 401 trades
  - 00:05 — 350 trades
  - 23:55 — 205 trades
  - 00:15 — 135 trades

Exit kind distribution:
  - manual_or_time: 3304

Direction by pair (Buy %):
  - EURCHF: total=370, buy_pct=43.8%
  - EURGBP: total=239, buy_pct=44.8%
  - EURUSD: total=703, buy_pct=52.5%
  - GBPUSD: total=898, buy_pct=51.4%
  - USDCAD: total=807, buy_pct=47.0%
  - USDCHF: total=287, buy_pct=39.4%

Direction by hour (Buy %, top 5 by activity):
  - hour=00: total=1680, buy_pct=48.6%
  - hour=23: total=1375, buy_pct=51.1%
  - hour=01: total=248, buy_pct=29.4%
  - hour=22: total=1, buy_pct=100.0%

## Feature extraction

- trades processed: 300
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_M15=0.62, bb_pos_20_2_M5=0.26, range_norm_H1=0.12  \|--- bb_pos_20_2_M15 ... | 0.640 | 0.054 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: None | 0.613 | 0.043 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.4700); Always-Sell = 0.5300 | 0.530 | — | 1.00 | — |
| 4 | univariate | ret_3_H4 > -0.001989 ⇒ Sell | 0.580 | — | 0.80 | 1.000 |
| 5 | univariate | range_norm_H1 > 0.4015 ⇒ Sell | 0.553 | — | 0.80 | 1.000 |
| 6 | univariate | ret_3_H1 > -0.0001123 ⇒ Sell | 0.630 | — | 0.60 | 0.002 |
| 7 | univariate | ret_10_M15 > -5.925e-05 ⇒ Sell | 0.623 | — | 0.60 | 0.006 |
| 8 | univariate | bb_pos_20_2_M15 > 0.1951 ⇒ Sell | 0.663 | — | 0.50 | 0.000 |
| 9 | univariate | range_norm_M15 > 0.6738 ⇒ Sell | 0.557 | — | 0.70 | 1.000 |
| 10 | univariate | ema_dist_20_M15 > 0.1582 ⇒ Sell | 0.643 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_M15=0.62, bb_pos_20_2_M5=0.26, range_norm_H1=0.12

|--- bb_pos_20_2_M15 <= 0.15
|   |--- range_norm_H1 <= 0.72
|   |   |--- class: 1
|   |--- range_norm_H1 >  0.72
|   |   |--- class: 0
|--- bb_pos_20_2_M15 >  0.15
|   |--- bb_pos_20_2_M5 <= 0.55
|   |   |--- class: 0
|   |--- bb_pos_20_2_M5 >  0.55
|   |   |--- class: 0

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
None
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
