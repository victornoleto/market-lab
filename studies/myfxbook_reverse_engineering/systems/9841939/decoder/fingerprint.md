# Decoder fingerprint — system 9841939

Generated: 2026-05-02T11:06:46

## Sanity (martingale + lot dynamics)

- n_trades: **4000**, deposits: 0
- pairs: {'EURCHF': 4000}
- actions: {'Sell': 2017, 'Buy': 1983}
- date range: 2025-04-10 03:28:43+00:00 → 2026-05-01 09:51:51+00:00
- max gap days: 3.7
- lot p50/p95/p99/max: 0.93 / 0.94 / 0.94 / 0.95
- lot p95/p50 ratio: 1.01
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 22.09 / 726.25 / 1481.47

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 17:00 — 413 trades
  - 10:00 — 341 trades
  - 15:00 — 311 trades
  - 00:00 — 291 trades
  - 11:00 — 268 trades

Top entry hour:5min (UTC):
  - 00:00 — 108 trades
  - 17:55 — 72 trades
  - 00:05 — 65 trades
  - 01:00 — 60 trades
  - 17:05 — 49 trades

Exit kind distribution:
  - manual_or_time: 4000

Direction by pair (Buy %):
  - EURCHF: total=4000, buy_pct=49.6%

Direction by hour (Buy %, top 5 by activity):
  - hour=17: total=413, buy_pct=49.4%
  - hour=10: total=341, buy_pct=50.7%
  - hour=15: total=311, buy_pct=48.9%
  - hour=00: total=291, buy_pct=50.9%
  - hour=11: total=268, buy_pct=48.5%

## Feature extraction

- trades processed: 4000
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | ripper | RIPPER ruleset: [[ema_dist_20_M1=0.3-0.66^prior_bar_sign_M15=1.0^ret_3_M5=6.5e-05-0.00015^atr_ratio_M1=0.074-0.087]] | 0.506 | 0.008 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.4958); Always-Sell = 0.5042 | 0.504 | — | 1.00 | — |
| 3 | tree | DecisionTree(max_depth=4) — top features: ret_1_M1=0.28, ret_1_M5=0.13, ret_3_M1=0.13, ret_3_H4=0.10, ema_dist_20_M1=0.07  \|--... | 0.496 | 0.017 | 1.00 | — |
| 4 | univariate | range_norm_M1 > 0.6222 ⇒ Sell | 0.511 | — | 0.80 | 1.000 |
| 5 | univariate | ret_10_M1 > -0.0001392 ⇒ Buy | 0.505 | — | 0.70 | 1.000 |
| 6 | univariate | hour_utc > 10 ⇒ Sell | 0.505 | — | 0.64 | 1.000 |
| 7 | univariate | ret_3_M1 > -3.234e-05 ⇒ Buy | 0.510 | — | 0.60 | 1.000 |
| 8 | univariate | ret_10_M5 > -0.0001499 ⇒ Buy | 0.506 | — | 0.60 | 1.000 |
| 9 | univariate | prior_bar_sign_M1 > -1 ⇒ Buy | 0.508 | — | 0.53 | 1.000 |
| 10 | univariate | ret_3_H1 > -1.092e-05 ⇒ Buy | 0.505 | — | 0.50 | 1.000 |

### RIPPER full output (rank 1)
```
RIPPER ruleset:
[[ema_dist_20_M1=0.3-0.66^prior_bar_sign_M15=1.0^ret_3_M5=6.5e-05-0.00015^atr_ratio_M1=0.074-0.087]]
```

### TREE full output (rank 3)
```
DecisionTree(max_depth=4) — top features: ret_1_M1=0.28, ret_1_M5=0.13, ret_3_M1=0.13, ret_3_H4=0.10, ema_dist_20_M1=0.07

|--- ret_1_M1 <= 0.00
|   |--- ret_1_M5 <= 0.00
|   |   |--- range_norm_M1 <= 0.64
|   |   |   |--- ret_1_H4 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_1_H4 >  -0.00
|   |   |   |   |--- class: 1
|   |   |--- range_norm_M1 >  0.64
|   |   |   |--- ret_10_H4 <= -0.01
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H4 >  -0.01
|   |   |   |   |--- class: 0
|   |--- ret_1_M5 >  0.00
|   |   |--- ret_1_M1 <= -0.00
|   |   |   |--- class: 0
|   |   |--- ret_1_M1 >  -0.00
|   |   |   |--- ema_dist_20_M1 <= 0.68
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_M1 >  0.68
|   |   |   |   |--- class: 0
|--- ret_1_M1 >  0.00
|   |--- ret_3_M1 <= 0.00
|   |   |--- range_norm_M15 <= 0.96
|   |   |   |--- class: 1
|   |   |--- range_norm_M15 >  0.96
|   |   |   |--- class: 0
|   |--- ret_3_M1 >  0.00
|   |   |--- ret_3_H4 <= 0.00
|   |   |   |--- ret_3_H1 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_3_H1 >  0.00
|   |   |   |   |--- class: 1
|   |   |--- ret_3_H4 >  0.00
|   |   |   |--- class: 0

```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
