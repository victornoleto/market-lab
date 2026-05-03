# Decoder fingerprint — system 10192401

Generated: 2026-05-02T01:16:50

## Sanity (martingale + lot dynamics)

- n_trades: **420**, deposits: 1
- pairs: {'BTCUSD': 420}
- actions: {'Buy': 220, 'Sell': 200}
- date range: 2022-11-21 21:28:15+00:00 → 2024-08-01 18:17:03+00:00
- max gap days: 6.8
- lot p50/p95/p99/max: 34087.50 / 69526.85 / 71613.35 / 73485.00
- lot p95/p50 ratio: 2.04
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.06 / 4.32 / 86.03

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 17:00 — 57 trades
  - 16:00 — 46 trades
  - 18:00 — 39 trades
  - 15:00 — 34 trades
  - 10:00 — 28 trades

Top entry hour:5min (UTC):
  - 15:30 — 14 trades
  - 17:45 — 11 trades
  - 16:55 — 8 trades
  - 09:45 — 7 trades
  - 18:15 — 7 trades

Exit kind distribution:
  - manual_or_time: 420

Direction by pair (Buy %):
  - BTCUSD: total=420, buy_pct=52.4%

Direction by hour (Buy %, top 5 by activity):
  - hour=17: total=57, buy_pct=40.4%
  - hour=16: total=46, buy_pct=52.2%
  - hour=18: total=39, buy_pct=46.2%
  - hour=15: total=34, buy_pct=58.8%
  - hour=10: total=28, buy_pct=57.1%

## Feature extraction

- trades processed: 420
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.89, ema_dist_20_H4=0.07, bb_pos_20_2_H4=0.04, range_norm_H1=0.00, re... | 0.874 | 0.029 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M1=1.0^prior_bar_sign_H4=1.0^ret_3_H4=>0.028] V [close_vs_session_open_M1=1.0^ret_3_H4=... | 0.824 | 0.038 | 1.00 | — |
| 3 | univariate | ema_dist_20_H4 > -0.2754 ⇒ Buy | 0.833 | — | 0.60 | 0.000 |
| 4 | univariate | bb_pos_20_2_H4 > -0.2196 ⇒ Buy | 0.814 | — | 0.60 | 0.000 |
| 5 | univariate | ema_dist_20_H1 > 0.1038 ⇒ Buy | 0.867 | — | 0.50 | 0.000 |
| 6 | univariate | bb_pos_20_2_H1 > 0.01682 ⇒ Buy | 0.867 | — | 0.50 | 0.000 |
| 7 | univariate | ret_10_H1 > 2.015e-06 ⇒ Buy | 0.848 | — | 0.50 | 0.000 |
| 8 | univariate | ret_3_H4 > 0.0001134 ⇒ Buy | 0.824 | — | 0.50 | 0.000 |
| 9 | univariate | ret_10_H4 > 7.975e-05 ⇒ Buy | 0.790 | — | 0.50 | 0.000 |
| 10 | baseline | Always-Buy (y_buy mean = 0.5238); Always-Sell = 0.4762 | 0.524 | — | 1.00 | — |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.89, ema_dist_20_H4=0.07, bb_pos_20_2_H4=0.04, range_norm_H1=0.00, ret_3_M15=0.00

|--- bb_pos_20_2_H1 <= -0.04
|   |--- ema_dist_20_H4 <= -0.25
|   |   |--- range_norm_H1 <= 1.12
|   |   |   |--- class: 0
|   |   |--- range_norm_H1 >  1.12
|   |   |   |--- class: 0
|   |--- ema_dist_20_H4 >  -0.25
|   |   |--- class: 0
|--- bb_pos_20_2_H1 >  -0.04
|   |--- bb_pos_20_2_H4 <= 0.59
|   |   |--- class: 1
|   |--- bb_pos_20_2_H4 >  0.59
|   |   |--- ret_3_M15 <= 0.00
|   |   |   |--- class: 1
|   |   |--- ret_3_M15 >  0.00
|   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M1=1.0^prior_bar_sign_H4=1.0^ret_3_H4=>0.028] V [close_vs_session_open_M1=1.0^ret_3_H4=0.016-0.028] V [close_vs_session_open_M1=1.0^ret_3_H4=0.01-0.016] V [bb_pos_20_2_H4=0.59-0.83] V [ret_10_M5=<-0.0051^hour_utc=14.0-16.0] V [bb_pos_20_2_H1=0.63-0.9] V [bb_pos_20_2_M5=-0.38--0.12^ret_10_H1=-0.0035--5.1e-05] V [ret_10_H4=7.3e-05-0.0055^prior_bar_sign_M15=1.0] V [bb_pos_20_2_H4=-0.48--0.22^ema_dist_20_M5=-1.64--1.06] V [is_first_5min_of_hour=1^atr_ratio_M15=>0.91] V [ret_3_M5=<-0.0025^ret_10_M1=-0.0014--0.00086]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
