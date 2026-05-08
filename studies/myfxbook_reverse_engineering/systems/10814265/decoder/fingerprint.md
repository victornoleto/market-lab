# Decoder fingerprint — system 10814265

Generated: 2026-05-02T02:52:41

## Sanity (martingale + lot dynamics)

- n_trades: **957**, deposits: 1
- pairs: {'GBPUSD': 353, 'EURUSD': 333, 'USDJPY': 271}
- actions: {'Buy': 509, 'Sell': 448}
- date range: 2022-12-05 17:00:02+00:00 → 2025-04-04 13:44:52+00:00
- max gap days: 8.4
- lot p50/p95/p99/max: 1.26 / 153.94 / 158.13 / 161.74
- lot p95/p50 ratio: 122.40
- martingale flag: **FAIL (martingale-like dynamics)**, steps=0, max_streak=0
- k1 flags: ['per-month max/median P95 = 125.92 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 0.27 / 4.39 / 86.91

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 15:00 — 119 trades
  - 10:00 — 118 trades
  - 09:00 — 106 trades
  - 17:00 — 94 trades
  - 16:00 — 87 trades

Top entry hour:5min (UTC):
  - 15:30 — 51 trades
  - 17:00 — 30 trades
  - 10:00 — 20 trades
  - 09:00 — 19 trades
  - 10:30 — 16 trades

Exit kind distribution:
  - manual_or_time: 957

Direction by pair (Buy %):
  - EURUSD: total=333, buy_pct=52.9%
  - GBPUSD: total=353, buy_pct=50.7%
  - USDJPY: total=271, buy_pct=56.8%

Direction by hour (Buy %, top 5 by activity):
  - hour=15: total=119, buy_pct=53.8%
  - hour=10: total=118, buy_pct=47.5%
  - hour=09: total=106, buy_pct=50.9%
  - hour=17: total=94, buy_pct=53.2%
  - hour=16: total=87, buy_pct=51.7%

## Feature extraction

- trades processed: 957
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | ripper | RIPPER ruleset: [[close_vs_session_open_H1=1.0^ema_dist_20_H1=>2.62] V [close_vs_session_open_H4=1.0^ema_dist_20_H1=1.9-2.62] V... | 0.913 | 0.026 | 1.00 | — |
| 2 | tree | DecisionTree(max_depth=4) — top features: ret_10_H4=0.91, ret_10_H1=0.05, ema_dist_20_H1=0.02, ret_3_H1=0.01, bb_pos_20_2_M15=0... | 0.908 | 0.024 | 1.00 | — |
| 3 | univariate | ema_dist_20_H4 > -0.3778 ⇒ Buy | 0.882 | — | 0.60 | 0.000 |
| 4 | univariate | ret_10_H1 > -0.0008005 ⇒ Buy | 0.878 | — | 0.60 | 0.000 |
| 5 | univariate | ema_dist_20_H1 > -0.447 ⇒ Buy | 0.874 | — | 0.60 | 0.000 |
| 6 | univariate | bb_pos_20_2_H1 > -0.3031 ⇒ Buy | 0.861 | — | 0.60 | 0.000 |
| 7 | univariate | ret_10_H4 > 0.0004234 ⇒ Buy | 0.901 | — | 0.50 | 0.000 |
| 8 | univariate | bb_pos_20_2_H4 > 0.08878 ⇒ Buy | 0.899 | — | 0.50 | 0.000 |
| 9 | univariate | ret_3_H4 > 0.0002321 ⇒ Buy | 0.853 | — | 0.50 | 0.000 |
| 10 | univariate | ema_dist_20_M15 > -0.3261 ⇒ Buy | 0.719 | — | 0.60 | 0.000 |

### RIPPER full output (rank 1)
```
RIPPER ruleset:
[[close_vs_session_open_H1=1.0^ema_dist_20_H1=>2.62] V [close_vs_session_open_H4=1.0^ema_dist_20_H1=1.9-2.62] V [ema_dist_20_H1=0.74-1.3^bb_pos_20_2_H1=0.49-0.76^prior_bar_sign_M15=-1.0] V [ema_dist_20_H1=1.3-1.9^prior_bar_sign_M15=-1.0] V [ret_10_H1=0.00033-0.0013^prior_bar_sign_H1=-1.0] V [bb_pos_20_2_H4=0.45-0.69] V [bb_pos_20_2_H1=0.76-0.92] V [bb_pos_20_2_H1=0.15-0.49^prior_bar_sign_H1=-1.0] V [ret_10_H4=0.00042-0.002^prior_bar_sign_H4=-1.0] V [ret_10_H4=0.0051-0.0083] V [bb_pos_20_2_H1=0.49-0.76^ema_dist_20_H1=0.74-1.3] V [ret_10_H4=>0.0083] V [ret_10_H4=0.002-0.0036^prior_bar_sign_M1=-1.0] V [ret_10_H4=0.0036-0.0051] V [ret_10_H1=-0.0008-0.00033^ema_dist_20_M5=-1.71--1.13] V [bb_pos_20_2_H4=0.089-0.45^prior_bar_sign_H4=-1.0^prior_bar_sign_M5=-1.0] V [ema_dist_20_H1=1.3-1.9^hour_utc=11.0-13.0] V [ret_10_H4=0.00042-0.002^prior_bar_sign_M15=-1.0] V [ret_3_M15=-0.00019-1.7e-05^bb_pos_20_2_H1=0.15-0.49] V [ret_3_M5=-0.0001--7.9e-06^range_norm_H4=0.81-0.96^ret_1_M5=6.4e-05-0.00014]]
```

### TREE full output (rank 2)
```
DecisionTree(max_depth=4) — top features: ret_10_H4=0.91, ret_10_H1=0.05, ema_dist_20_H1=0.02, ret_3_H1=0.01, bb_pos_20_2_M15=0.01

|--- ret_10_H4 <= -0.00
|   |--- ret_10_H1 <= -0.00
|   |   |--- ema_dist_20_H4 <= -0.91
|   |   |   |--- range_norm_H4 <= 1.90
|   |   |   |   |--- class: 0
|   |   |   |--- range_norm_H4 >  1.90
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_H4 >  -0.91
|   |   |   |--- ret_3_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_3_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |--- ret_10_H1 >  -0.00
|   |   |--- class: 0
|--- ret_10_H4 >  -0.00
|   |--- ema_dist_20_H1 <= 0.39
|   |   |--- class: 1
|   |--- ema_dist_20_H1 >  0.39
|   |   |--- bb_pos_20_2_M15 <= 0.84
|   |   |   |--- range_norm_H4 <= 1.28
|   |   |   |   |--- class: 1
|   |   |   |--- range_norm_H4 >  1.28
|   |   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_M15 >  0.84
|   |   |   |--- class: 1

```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
