# Decoder fingerprint — system 9607500

Generated: 2026-05-02T10:36:35

## Sanity (martingale + lot dynamics)

- n_trades: **1942**, deposits: 1
- pairs: {'GBPUSD': 604, 'EURUSD': 561, 'USDJPY': 486, 'GBPJPY': 200, 'EURJPY': 91}
- actions: {'Buy': 1033, 'Sell': 909}
- date range: 2022-05-02 21:32:46+00:00 → 2026-05-01 09:52:47+00:00
- max gap days: 8.4
- lot p50/p95/p99/max: 1.29 / 166.72 / 184.05 / 188.29
- lot p95/p50 ratio: 128.87
- martingale flag: **FAIL (martingale-like dynamics)**, steps=0, max_streak=0
- k1 flags: ['per-month max/median P95 = 144.59 (> 3.0) — within-month doubling']
- hold p50/p95/max (h): 0.14 / 2.92 / 86.99

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 10:00 — 229 trades
  - 15:00 — 224 trades
  - 09:00 — 220 trades
  - 11:00 — 181 trades
  - 16:00 — 178 trades

Top entry hour:5min (UTC):
  - 15:30 — 97 trades
  - 17:00 — 50 trades
  - 09:00 — 37 trades
  - 10:00 — 33 trades
  - 11:00 — 28 trades

Exit kind distribution:
  - manual_or_time: 1942

Direction by pair (Buy %):
  - EURJPY: total=91, buy_pct=62.6%
  - EURUSD: total=561, buy_pct=52.0%
  - GBPJPY: total=200, buy_pct=50.5%
  - GBPUSD: total=604, buy_pct=49.7%
  - USDJPY: total=486, buy_pct=58.2%

Direction by hour (Buy %, top 5 by activity):
  - hour=10: total=229, buy_pct=47.6%
  - hour=15: total=224, buy_pct=49.6%
  - hour=09: total=220, buy_pct=51.8%
  - hour=11: total=181, buy_pct=55.8%
  - hour=16: total=178, buy_pct=44.9%

## Feature extraction

- trades processed: 1942
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_10_H4=0.86, ret_10_H1=0.09, ret_3_H1=0.04, atr_ratio_M15=0.01, ema_dist_20_H4=0.0... | 0.905 | 0.031 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M15=1.0^bb_pos_20_2_H4=0.84-1.09] V [close_vs_session_open_M1=1.0^bb_pos_20_2_H4=>1.09^... | 0.893 | 0.027 | 1.00 | — |
| 3 | univariate | ret_10_H4 > 0.0002851 ⇒ Buy | 0.899 | — | 0.50 | 0.000 |
| 4 | univariate | bb_pos_20_2_H4 > 0.07142 ⇒ Buy | 0.891 | — | 0.50 | 0.000 |
| 5 | univariate | ema_dist_20_H4 > 0.1682 ⇒ Buy | 0.878 | — | 0.50 | 0.000 |
| 6 | univariate | ema_dist_20_H1 > 0.1495 ⇒ Buy | 0.870 | — | 0.50 | 0.000 |
| 7 | univariate | ret_10_H1 > 0.000249 ⇒ Buy | 0.867 | — | 0.50 | 0.000 |
| 8 | univariate | bb_pos_20_2_H1 > 0.1463 ⇒ Buy | 0.860 | — | 0.50 | 0.000 |
| 9 | univariate | ret_3_H4 > 0.0002573 ⇒ Buy | 0.855 | — | 0.50 | 0.000 |
| 10 | univariate | ema_dist_20_M15 > -0.2885 ⇒ Buy | 0.715 | — | 0.60 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_10_H4=0.86, ret_10_H1=0.09, ret_3_H1=0.04, atr_ratio_M15=0.01, ema_dist_20_H4=0.00

|--- ret_10_H4 <= -0.00
|   |--- ret_10_H1 <= -0.00
|   |   |--- atr_ratio_M15 <= 0.85
|   |   |   |--- ema_dist_20_H4 <= -0.79
|   |   |   |   |--- class: 0
|   |   |   |--- ema_dist_20_H4 >  -0.79
|   |   |   |   |--- class: 0
|   |   |--- atr_ratio_M15 >  0.85
|   |   |   |--- ret_3_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_3_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |--- ret_10_H1 >  -0.00
|   |   |--- ret_3_H1 <= 0.00
|   |   |   |--- class: 1
|   |   |--- ret_3_H1 >  0.00
|   |   |   |--- class: 0
|--- ret_10_H4 >  -0.00
|   |--- ret_10_H1 <= -0.00
|   |   |--- class: 0
|   |--- ret_10_H1 >  -0.00
|   |   |--- atr_ratio_M15 <= 0.84
|   |   |   |--- ret_10_H4 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_10_H4 >  0.00
|   |   |   |   |--- class: 1
|   |   |--- atr_ratio_M15 >  0.84
|   |   |   |--- ret_10_H4 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_10_H4 >  0.00
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M15=1.0^bb_pos_20_2_H4=0.84-1.09] V [close_vs_session_open_M1=1.0^bb_pos_20_2_H4=>1.09^ema_dist_20_H1=>2.61] V [bb_pos_20_2_H4=0.43-0.67^prior_bar_sign_H4=-1.0] V [bb_pos_20_2_H4=0.67-0.84^prior_bar_sign_H4=-1.0] V [close_vs_session_open_H4=1.0^bb_pos_20_2_H4=0.67-0.84] V [bb_pos_20_2_H4=0.071-0.43^prior_bar_sign_H4=-1.0] V [bb_pos_20_2_H4=>1.09^ema_dist_20_H1=1.92-2.61] V [bb_pos_20_2_H4=0.43-0.67^ret_1_H4=0.00013-0.00057] V [bb_pos_20_2_H4=0.43-0.67^ret_1_H4=0.00057-0.0012] V [ema_dist_20_H1=1.29-1.92^prior_bar_sign_M15=-1.0] V [bb_pos_20_2_H4=0.84-1.09] V [bb_pos_20_2_H4=-0.32-0.071^prior_bar_sign_H1=-1.0^ret_3_H4=0.00026-0.0015] V [close_vs_session_open_M15=1.0^bb_pos_20_2_H4=>1.09] V [ret_10_H4=0.00029-0.0021^prior_bar_sign_M15=-1.0] V [ret_10_H1=0.0025-0.004] V [ret_10_H1=0.004-0.0062] V [ret_10_H1=>0.0062] V [ema_dist_20_H1=0.15-0.8^prior_bar_sign_H1=-1.0^is_first_min_of_hour=0^bb_pos_20_2_H1=0.15-0.51] V [ema_dist_20_H1=0.8-1.29^bb_pos_20_2_H1=0.51-0.74] V [range_norm_H4=>2.24^ret_1_M1=>0.00018^ret_3_M5=>0.0007] V [ret_10_H4=0.0021-0.0039^ret_1_H1=0.0-0.00026] V [ret_10_H1=0.00025-0.0013^atr_ratio_M5=0.28-0.31^close_vs_session_open_H1=0.0] V [ret_10_H1=0.0013-0.0025^dow=0] V [ema_dist_20_H4=-0.4-0.17^ema_dist_20_M5=-1.12--0.68^prior_bar_sign_M5=1.0] V [bb_pos_20_2_M5=-0.19-0.012^dow=1^close_vs_session_open_H1=1.0] V [bb_pos_20_2_M15=<-0.73^bb_pos_20_2_H4=-0.61--0.32^ret_1_H4=-0.0034--0.0018] V [ret_1_M1=-2.8e-05-0.0^ema_dist_20_H1=0.15-0.8^atr_ratio_M1=<0.072] V [range_norm_H4=>2.24^ret_3_M5=-0.00012-0.0^bb_pos_20_2_M15=<-0.73] V [bb_pos_20_2_H1=-0.32-0.15^ema_dist_20_M15=-1.14--0.69^is_first_5min_of_hour=0] V [dollar_index_proxy=1.0^ret_1_M15=0.00025-0.00043^is_first_min_of_hour=1] V [atr_ratio_M15=>0.89^ret_3_H1=<-0.003^range_norm_M5=0.81-0.89^hour_utc=13.0-15.0] V [atr_ratio_M15=0.81-0.89^ret_3_H4=-0.001-0.00026^dow=3]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
