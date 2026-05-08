# Decoder fingerprint — system 11305553

Generated: 2026-05-03T19:07:12

## Sanity (martingale + lot dynamics)

- n_trades: **575**, deposits: 5
- pairs: {'AUDCAD': 406, 'NZDCAD': 114, 'AUDNZD': 55}
- actions: {'Buy': 472, 'Sell': 103}
- date range: 2025-01-14 02:34:43+00:00 → 2026-04-17 09:12:57+00:00
- max gap days: 13.0
- lot p50/p95/p99/max: 0.05 / 0.11 / 0.40 / 1.32
- lot p95/p50 ratio: 2.20
- martingale flag: **FAIL (martingale-like dynamics)**, steps=30, max_streak=1
- k1 flags: ['30 doubling-after-loss trades (>5% of total)', 'per-month max/median P95 = 30.75 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 7.64 / 124.69 / 2175.20

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 15:00 — 59 trades
  - 09:00 — 52 trades
  - 17:00 — 40 trades
  - 16:00 — 32 trades
  - 04:00 — 31 trades

Top entry hour:5min (UTC):
  - 15:30 — 38 trades
  - 09:35 — 19 trades
  - 00:15 — 16 trades
  - 17:00 — 14 trades
  - 16:45 — 12 trades

Exit kind distribution:
  - manual_or_time: 575

Direction by pair (Buy %):
  - AUDCAD: total=406, buy_pct=90.1%
  - AUDNZD: total=55, buy_pct=52.7%
  - NZDCAD: total=114, buy_pct=67.5%

Direction by hour (Buy %, top 5 by activity):
  - hour=15: total=59, buy_pct=96.6%
  - hour=09: total=52, buy_pct=94.2%
  - hour=17: total=40, buy_pct=85.0%
  - hour=16: total=32, buy_pct=84.4%
  - hour=04: total=31, buy_pct=71.0%

## Feature extraction

- trades processed: 461
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | baseline | Always-Buy (y_buy mean = 0.8568); Always-Sell = 0.1432 | 0.857 | — | 1.00 | — |
| 2 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.81, ret_10_H1=0.11, ret_1_H1=0.07, ret_1_H4=0.00  \|--- bb_pos_20_2_... | 0.792 | 0.129 | 1.00 | — |
| 3 | univariate | dow > 0 ⇒ Buy | 0.746 | — | 0.85 | 0.000 |
| 4 | ripper | RIPPER ruleset: [[close_vs_session_open_M1=-1.0^prior_bar_sign_H1=1.0^prior_bar_sign_M5=-1.0] V [ret_3_H1=0.00093-0.0018] V [re... | 0.553 | 0.090 | 1.00 | — |
| 5 | univariate | ret_10_H1 > 0.001293 ⇒ Sell | 0.852 | — | 0.20 | 0.000 |
| 6 | univariate | bb_pos_20_2_H1 > 0.4594 ⇒ Sell | 0.848 | — | 0.20 | 0.000 |
| 7 | univariate | ret_3_H4 > 0.001443 ⇒ Sell | 0.848 | — | 0.20 | 0.000 |
| 8 | univariate | ema_dist_20_H1 > 0.6952 ⇒ Sell | 0.844 | — | 0.20 | 0.000 |
| 9 | univariate | ema_dist_20_M15 > 0.5867 ⇒ Sell | 0.805 | — | 0.20 | 0.000 |
| 10 | univariate | bb_pos_20_2_M15 > 0.3888 ⇒ Sell | 0.787 | — | 0.20 | 0.000 |

### TREE full output (rank 2)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.81, ret_10_H1=0.11, ret_1_H1=0.07, ret_1_H4=0.00

|--- bb_pos_20_2_H1 <= 0.40
|   |--- ret_1_H1 <= -0.00
|   |   |--- class: 1
|   |--- ret_1_H1 >  -0.00
|   |   |--- bb_pos_20_2_H1 <= -0.00
|   |   |   |--- ret_1_H4 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_1_H4 >  0.00
|   |   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_H1 >  -0.00
|   |   |   |--- class: 1
|--- bb_pos_20_2_H1 >  0.40
|   |--- ret_10_H1 <= 0.00
|   |   |--- class: 1
|   |--- ret_10_H1 >  0.00
|   |   |--- class: 0

```

### RIPPER full output (rank 4)
```
RIPPER ruleset:
[[close_vs_session_open_M1=-1.0^prior_bar_sign_H1=1.0^prior_bar_sign_M5=-1.0] V [ret_3_H1=0.00093-0.0018] V [ret_1_H1=-0.00072--0.00042] V [ret_3_H1=0.00054-0.00093]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
