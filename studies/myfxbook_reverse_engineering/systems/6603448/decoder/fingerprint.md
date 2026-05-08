# Decoder fingerprint — system 6603448

Generated: 2026-05-02T07:36:15

## Sanity (martingale + lot dynamics)

- n_trades: **920**, deposits: 1
- pairs: {'AUDUSD': 401, 'USDCHF': 331, 'EURCHF': 188}
- actions: {'Sell': 471, 'Buy': 449}
- date range: 2020-07-27 14:58:10+00:00 → 2021-06-11 20:08:14+00:00
- max gap days: 6.5
- lot p50/p95/p99/max: 0.01 / 0.03 / 0.05 / 0.06
- lot p95/p50 ratio: 3.00
- martingale flag: **FAIL (martingale-like dynamics)**, steps=8, max_streak=1
- k1 flags: ['per-month max/median P95 = 4.35 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 65.84 / 2035.14 / 2712.18

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 17:00 — 92 trades
  - 10:00 — 88 trades
  - 16:00 — 78 trades
  - 15:00 — 66 trades
  - 11:00 — 59 trades

Top entry hour:5min (UTC):
  - 17:55 — 23 trades
  - 10:00 — 14 trades
  - 10:40 — 14 trades
  - 10:05 — 13 trades
  - 17:30 — 13 trades

Exit kind distribution:
  - manual_or_time: 920

Direction by pair (Buy %):
  - AUDUSD: total=401, buy_pct=51.9%
  - EURCHF: total=188, buy_pct=47.3%
  - USDCHF: total=331, buy_pct=45.9%

Direction by hour (Buy %, top 5 by activity):
  - hour=17: total=92, buy_pct=51.1%
  - hour=10: total=88, buy_pct=46.6%
  - hour=16: total=78, buy_pct=43.6%
  - hour=15: total=66, buy_pct=48.5%
  - hour=11: total=59, buy_pct=55.9%

## Feature extraction

- trades processed: 920
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | ripper | RIPPER ruleset: [[prior_bar_sign_M1=-1.0]] | 0.514 | 0.023 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.4880); Always-Sell = 0.5120 | 0.512 | — | 1.00 | — |
| 3 | tree | DecisionTree(max_depth=4) — top features: atr_ratio_M5=0.34, range_norm_M15=0.21, ret_3_M15=0.17, range_norm_M1=0.15, ret_1_M1=... | 0.482 | 0.025 | 1.00 | — |
| 4 | univariate | ret_1_M15 > -0.0003592 ⇒ Sell | 0.521 | — | 0.80 | 1.000 |
| 5 | univariate | hour_utc > 8 ⇒ Sell | 0.518 | — | 0.79 | 1.000 |
| 6 | univariate | ret_3_H1 > -0.0007627 ⇒ Sell | 0.526 | — | 0.70 | 1.000 |
| 7 | univariate | ret_10_M5 > -0.0004042 ⇒ Sell | 0.520 | — | 0.70 | 1.000 |
| 8 | univariate | atr_ratio_M15 > 0.5515 ⇒ Sell | 0.523 | — | 0.60 | 1.000 |
| 9 | univariate | bb_pos_20_2_H4 > -0.3431 ⇒ Buy | 0.520 | — | 0.60 | 1.000 |
| 10 | univariate | prior_bar_sign_M1 > -1 ⇒ Sell | 0.523 | — | 0.54 | 1.000 |

### RIPPER full output (rank 1)
```
RIPPER ruleset:
[[prior_bar_sign_M1=-1.0]]
```

### TREE full output (rank 3)
```
DecisionTree(max_depth=4) — top features: atr_ratio_M5=0.34, range_norm_M15=0.21, ret_3_M15=0.17, range_norm_M1=0.15, ret_1_M1=0.13

|--- atr_ratio_M5 <= 0.14
|   |--- class: 0
|--- atr_ratio_M5 >  0.14
|   |--- atr_ratio_M5 <= 0.23
|   |   |--- range_norm_M15 <= 0.79
|   |   |   |--- ret_1_M1 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_1_M1 >  0.00
|   |   |   |   |--- class: 0
|   |   |--- range_norm_M15 >  0.79
|   |   |   |--- class: 1
|   |--- atr_ratio_M5 >  0.23
|   |   |--- range_norm_M1 <= 1.50
|   |   |   |--- ret_3_M15 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_3_M15 >  0.00
|   |   |   |   |--- class: 0
|   |   |--- range_norm_M1 >  1.50
|   |   |   |--- class: 0

```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
