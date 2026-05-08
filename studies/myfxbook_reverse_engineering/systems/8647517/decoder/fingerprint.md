# Decoder fingerprint — system 8647517

Generated: 2026-05-02T10:20:14

## Sanity (martingale + lot dynamics)

- n_trades: **1024**, deposits: 1
- pairs: {'XAUUSD': 1024}
- actions: {'Buy': 544, 'Sell': 480}
- date range: 2021-06-15 17:19:27+00:00 → 2026-04-30 11:04:07+00:00
- max gap days: 8.3
- lot p50/p95/p99/max: 1977.38 / 4468.64 / 5140.86 / 5393.42
- lot p95/p50 ratio: 2.26
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.00 / 0.25 / 5.18

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 15:00 — 143 trades
  - 16:00 — 137 trades
  - 17:00 — 94 trades
  - 10:00 — 86 trades
  - 11:00 — 73 trades

Top entry hour:5min (UTC):
  - 15:30 — 44 trades
  - 17:00 — 25 trades
  - 16:35 — 24 trades
  - 16:45 — 23 trades
  - 21:00 — 18 trades

Exit kind distribution:
  - manual_or_time: 1024

Direction by pair (Buy %):
  - XAUUSD: total=1024, buy_pct=53.1%

Direction by hour (Buy %, top 5 by activity):
  - hour=15: total=143, buy_pct=59.4%
  - hour=16: total=137, buy_pct=55.5%
  - hour=17: total=94, buy_pct=46.8%
  - hour=10: total=86, buy_pct=51.2%
  - hour=11: total=73, buy_pct=41.1%

## Feature extraction

- trades processed: 1024
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.78, ret_10_H1=0.06, ret_10_H4=0.06, ret_10_M15=0.05, ret_3_H1=0.03  ... | 0.871 | 0.041 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M15=1.0^ema_dist_20_H4=>2.22] V [close_vs_session_open_M15=1.0^bb_pos_20_2_H1=0.92-1.09... | 0.809 | 0.046 | 1.00 | — |
| 3 | univariate | ema_dist_20_H1 > -0.3576 ⇒ Buy | 0.848 | — | 0.60 | 0.000 |
| 4 | univariate | ret_10_H1 > -0.001147 ⇒ Buy | 0.832 | — | 0.60 | 0.000 |
| 5 | univariate | bb_pos_20_2_H1 > 0.1347 ⇒ Buy | 0.854 | — | 0.50 | 0.000 |
| 6 | univariate | ret_3_H4 > 0.0002174 ⇒ Buy | 0.812 | — | 0.50 | 0.000 |
| 7 | univariate | ret_10_H4 > 0.0009834 ⇒ Buy | 0.811 | — | 0.50 | 0.000 |
| 8 | univariate | ema_dist_20_H4 > 0.2303 ⇒ Buy | 0.797 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.1024 ⇒ Buy | 0.797 | — | 0.50 | 0.000 |
| 10 | baseline | Always-Buy (y_buy mean = 0.5312); Always-Sell = 0.4688 | 0.531 | — | 1.00 | — |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.78, ret_10_H1=0.06, ret_10_H4=0.06, ret_10_M15=0.05, ret_3_H1=0.03

|--- bb_pos_20_2_H1 <= -0.10
|   |--- ret_3_H1 <= -0.00
|   |   |--- ret_10_H1 <= -0.01
|   |   |   |--- ret_10_H4 <= -0.01
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H4 >  -0.01
|   |   |   |   |--- class: 0
|   |   |--- ret_10_H1 >  -0.01
|   |   |   |--- class: 1
|   |--- ret_3_H1 >  -0.00
|   |   |--- ret_10_H1 <= -0.00
|   |   |   |--- ret_10_H4 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H4 >  -0.00
|   |   |   |   |--- class: 0
|   |   |--- ret_10_H1 >  -0.00
|   |   |   |--- class: 0
|--- bb_pos_20_2_H1 >  -0.10
|   |--- ret_10_H4 <= 0.00
|   |   |--- ret_10_M15 <= 0.00
|   |   |   |--- class: 1
|   |   |--- ret_10_M15 >  0.00
|   |   |   |--- class: 0
|   |--- ret_10_H4 >  0.00
|   |   |--- ret_3_H1 <= 0.00
|   |   |   |--- ret_10_M5 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_10_M5 >  0.00
|   |   |   |   |--- class: 1
|   |   |--- ret_3_H1 >  0.00
|   |   |   |--- ema_dist_20_H1 <= 1.64
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_H1 >  1.64
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M15=1.0^ema_dist_20_H4=>2.22] V [close_vs_session_open_M15=1.0^bb_pos_20_2_H1=0.92-1.09] V [close_vs_session_open_M1=1.0^ema_dist_20_H1=0.76-1.29^prior_bar_sign_H1=-1.0] V [close_vs_session_open_H1=1.0^prior_bar_sign_H1=-1.0^ema_dist_20_H1=1.29-1.88] V [close_vs_session_open_H1=1.0^bb_pos_20_2_H4=0.4-0.63] V [close_vs_session_open_H1=1.0^ema_dist_20_H1=1.88-2.55] V [bb_pos_20_2_H1=0.16-0.45^prior_bar_sign_H1=-1.0^is_first_min_of_hour=0] V [ema_dist_20_H1=>2.55] V [bb_pos_20_2_H1=0.72-0.92^ema_dist_20_H1=1.29-1.88] V [bb_pos_20_2_H1=0.45-0.72^prior_bar_sign_M15=-1.0] V [ema_dist_20_H1=-0.33-0.25^ret_10_M15=-0.0025--0.0013] V [ema_dist_20_H1=1.88-2.55] V [ema_dist_20_H1=0.76-1.29^close_vs_session_open_H1=-1.0] V [bb_pos_20_2_H1=-0.28-0.16^close_vs_session_open_H1=-1.0^prior_bar_sign_H4=-1.0^prior_bar_sign_H1=-1.0] V [bb_pos_20_2_H4=0.63-0.83^ret_3_M5=0.00068-0.0012] V [ema_dist_20_H1=0.25-0.76^range_norm_H4=0.64-0.78] V [ret_3_H1=-0.0048--0.0028^bb_pos_20_2_H1=-0.63--0.28^prior_bar_sign_M5=-1.0] V [bb_pos_20_2_M1=-0.038-0.19^bb_pos_20_2_M15=<-0.74] V [bb_pos_20_2_H1=-0.28-0.16^ret_10_M15=-0.0047--0.0025] V [ret_10_H1=0.0017-0.0037^ema_dist_20_M15=1.33-1.85] V [atr_ratio_H4=<1.48^range_norm_M1=0.92-1.01] V [ema_dist_20_M15=0.096-0.49^range_norm_M15=0.54-0.61] V [ret_3_H1=<-0.0048^ret_3_H4=-0.0034--0.0014] V [ret_10_H1=-0.0011-0.00043^ret_3_M1=-0.0002--0.0001]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
