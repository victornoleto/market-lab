# Decoder fingerprint — system 10251631

Generated: 2026-05-02T01:52:15

## Sanity (martingale + lot dynamics)

- n_trades: **461**, deposits: 5
- pairs: {'XAUUSD': 461}
- actions: {'Buy': 232, 'Sell': 229}
- date range: 2022-03-21 11:36:54+00:00 → 2024-08-07 02:32:52+00:00
- max gap days: 14.9
- lot p50/p95/p99/max: 1929.19 / 2358.54 / 2421.97 / 2467.76
- lot p95/p50 ratio: 1.22
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.15 / 13.62 / 160.87

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 03:00 — 115 trades
  - 04:00 — 80 trades
  - 02:00 — 52 trades
  - 01:00 — 50 trades
  - 06:00 — 36 trades

Top entry hour:5min (UTC):
  - 04:00 — 20 trades
  - 01:00 — 19 trades
  - 03:05 — 16 trades
  - 03:00 — 15 trades
  - 03:10 — 13 trades

Exit kind distribution:
  - manual_or_time: 461

Direction by pair (Buy %):
  - XAUUSD: total=461, buy_pct=50.3%

Direction by hour (Buy %, top 5 by activity):
  - hour=03: total=115, buy_pct=50.4%
  - hour=04: total=80, buy_pct=48.8%
  - hour=02: total=52, buy_pct=44.2%
  - hour=01: total=50, buy_pct=52.0%
  - hour=06: total=36, buy_pct=44.4%

## Feature extraction

- trades processed: 461
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: close_vs_session_open_H4=0.37, ret_10_M1=0.15, bb_pos_20_2_H4=0.13, bb_pos_20_2_M15=0... | 0.531 | 0.056 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_H4=-1.0^prior_bar_sign_M5=-1.0^prior_bar_sign_M1=1.0^prior_bar_sign_M15=-1.0^ret_1_M1=7... | 0.513 | 0.020 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.5033); Always-Sell = 0.4967 | 0.503 | — | 1.00 | — |
| 4 | univariate | bb_pos_20_2_H1 > -0.3392 ⇒ Sell | 0.573 | — | 0.70 | 0.536 |
| 5 | univariate | ret_1_H4 > -0.0003973 ⇒ Sell | 0.586 | — | 0.60 | 0.070 |
| 6 | univariate | ema_dist_20_M15 > -0.2308 ⇒ Sell | 0.585 | — | 0.60 | 0.080 |
| 7 | univariate | ema_dist_20_H1 > -0.2956 ⇒ Sell | 0.581 | — | 0.60 | 0.143 |
| 8 | univariate | close_vs_session_open_H4 > -1 ⇒ Sell | 0.612 | — | 0.54 | 0.000 |
| 9 | univariate | close_vs_session_open_M15 > -1 ⇒ Sell | 0.585 | — | 0.56 | 0.083 |
| 10 | univariate | close_vs_session_open_M1 > -1 ⇒ Sell | 0.586 | — | 0.55 | 0.070 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: close_vs_session_open_H4=0.37, ret_10_M1=0.15, bb_pos_20_2_H4=0.13, bb_pos_20_2_M15=0.13, atr_ratio_H4=0.12

|--- close_vs_session_open_H4 <= -0.50
|   |--- bb_pos_20_2_M15 <= 0.05
|   |   |--- bb_pos_20_2_H4 <= -0.00
|   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_H4 >  -0.00
|   |   |   |--- class: 1
|   |--- bb_pos_20_2_M15 >  0.05
|   |   |--- class: 0
|--- close_vs_session_open_H4 >  -0.50
|   |--- ret_10_M1 <= -0.00
|   |   |--- class: 0
|   |--- ret_10_M1 >  -0.00
|   |   |--- atr_ratio_M1 <= 0.10
|   |   |   |--- atr_ratio_H4 <= 2.01
|   |   |   |   |--- class: 0
|   |   |   |--- atr_ratio_H4 >  2.01
|   |   |   |   |--- class: 0
|   |   |--- atr_ratio_M1 >  0.10
|   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_H4=-1.0^prior_bar_sign_M5=-1.0^prior_bar_sign_M1=1.0^prior_bar_sign_M15=-1.0^ret_1_M1=7.6e-05-0.00013] V [close_vs_session_open_H4=-1.0^ret_1_M15=0.00015-0.0003]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
