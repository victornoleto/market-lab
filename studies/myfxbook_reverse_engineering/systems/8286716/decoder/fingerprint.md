# Decoder fingerprint — system 8286716

Generated: 2026-05-02T08:33:03

## Sanity (martingale + lot dynamics)

- n_trades: **1531**, deposits: 2
- pairs: {'EURCHF': 1531}
- actions: {'Sell': 803, 'Buy': 728}
- date range: 2021-02-25 14:25:57+00:00 → 2021-06-11 20:06:56+00:00
- max gap days: 2.3
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.01 / 0.01
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 14.45 / 283.34 / 504.50

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 10:00 — 183 trades
  - 11:00 — 148 trades
  - 17:00 — 146 trades
  - 12:00 — 130 trades
  - 15:00 — 126 trades

Top entry hour:5min (UTC):
  - 10:55 — 26 trades
  - 11:00 — 24 trades
  - 17:55 — 24 trades
  - 11:10 — 22 trades
  - 11:50 — 21 trades

Exit kind distribution:
  - manual_or_time: 1531

Direction by pair (Buy %):
  - EURCHF: total=1531, buy_pct=47.6%

Direction by hour (Buy %, top 5 by activity):
  - hour=10: total=183, buy_pct=47.5%
  - hour=11: total=148, buy_pct=45.9%
  - hour=17: total=146, buy_pct=46.6%
  - hour=12: total=130, buy_pct=49.2%
  - hour=15: total=126, buy_pct=47.6%

## Feature extraction

- trades processed: 1531
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: range_norm_M1=0.37, ret_10_H4=0.16, ret_3_M5=0.12, ret_3_H1=0.11, ema_dist_20_H4=0.10... | 0.536 | 0.020 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.4755); Always-Sell = 0.5245 | 0.524 | — | 1.00 | — |
| 3 | ripper | RIPPER ruleset: [[close_vs_session_open_M1=1.0^close_vs_session_open_H4=-1.0^ema_dist_20_M1=0.87-1.31^prior_bar_sign_M5=1.0]] | 0.522 | 0.024 | 1.00 | — |
| 4 | univariate | ret_3_H4 > 0.0006273 ⇒ Buy | 0.524 | — | 0.40 | 1.000 |
| 5 | univariate | ema_dist_20_M1 > 0.8662 ⇒ Buy | 0.523 | — | 0.30 | 1.000 |
| 6 | univariate | ret_3_M5 > 0.0001367 ⇒ Buy | 0.522 | — | 0.30 | 1.000 |
| 7 | univariate | ema_dist_20_M15 > 0.5141 ⇒ Buy | 0.522 | — | 0.30 | 1.000 |
| 8 | univariate | bb_pos_20_2_H1 > 0.6234 ⇒ Buy | 0.522 | — | 0.30 | 1.000 |
| 9 | univariate | ret_10_H4 > 0.001466 ⇒ Buy | 0.523 | — | 0.30 | 1.000 |
| 10 | univariate | ret_10_H1 > 0.001713 ⇒ Buy | 0.526 | — | 0.20 | 1.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: range_norm_M1=0.37, ret_10_H4=0.16, ret_3_M5=0.12, ret_3_H1=0.11, ema_dist_20_H4=0.10

|--- ema_dist_20_H4 <= -1.35
|   |--- ret_10_H4 <= -0.00
|   |   |--- class: 0
|   |--- ret_10_H4 >  -0.00
|   |   |--- class: 0
|--- ema_dist_20_H4 >  -1.35
|   |--- range_norm_M1 <= 1.09
|   |   |--- range_norm_M1 <= 0.96
|   |   |   |--- range_norm_M1 <= 0.92
|   |   |   |   |--- class: 0
|   |   |   |--- range_norm_M1 >  0.92
|   |   |   |   |--- class: 0
|   |   |--- range_norm_M1 >  0.96
|   |   |   |--- bb_pos_20_2_M5 <= -0.04
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_M5 >  -0.04
|   |   |   |   |--- class: 1
|   |--- range_norm_M1 >  1.09
|   |   |--- ret_3_M5 <= -0.00
|   |   |   |--- ret_3_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_3_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |   |--- ret_3_M5 >  -0.00
|   |   |   |--- ema_dist_20_M5 <= -0.20
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_M5 >  -0.20
|   |   |   |   |--- class: 0

```

### RIPPER full output (rank 3)
```
RIPPER ruleset:
[[close_vs_session_open_M1=1.0^close_vs_session_open_H4=-1.0^ema_dist_20_M1=0.87-1.31^prior_bar_sign_M5=1.0]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
