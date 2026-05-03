# Decoder fingerprint — system 2421356

Generated: 2026-05-02T06:27:09

## Sanity (martingale + lot dynamics)

- n_trades: **1763**, deposits: 1
- pairs: {'XAUUSD': 1762, 'SUMMAR': 1}
- actions: {'Buy': 919, 'Sell': 844}
- date range: 2017-09-04 09:22:13+00:00 → 2026-04-30 11:04:08+00:00
- max gap days: 63.9
- lot p50/p95/p99/max: 0.62 / 11.57 / 24.73 / 35.89
- lot p95/p50 ratio: 18.65
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.00 / 0.32 / 12.69

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 15:00 — 233 trades
  - 16:00 — 223 trades
  - 10:00 — 165 trades
  - 17:00 — 156 trades
  - 09:00 — 135 trades

Top entry hour:5min (UTC):
  - 15:30 — 69 trades
  - 17:00 — 40 trades
  - 16:35 — 34 trades
  - 16:45 — 29 trades
  - 16:30 — 28 trades

Exit kind distribution:
  - manual_or_time: 1763

Direction by pair (Buy %):
  - SUMMAR: total=1, buy_pct=100.0%
  - XAUUSD: total=1762, buy_pct=52.1%

Direction by hour (Buy %, top 5 by activity):
  - hour=15: total=233, buy_pct=55.8%
  - hour=16: total=223, buy_pct=55.6%
  - hour=10: total=165, buy_pct=46.1%
  - hour=17: total=156, buy_pct=50.0%
  - hour=09: total=135, buy_pct=58.5%

## Feature extraction

- trades processed: 1762
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.73, ret_3_H1=0.12, ema_dist_20_H1=0.05, ret_10_H1=0.04, ret_10_H4=0.... | 0.875 | 0.016 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_H1=1.0^ret_10_H1=>0.0079^ret_3_H4=>0.0089] V [close_vs_session_open_H1=1.0^bb_pos_20_2_... | 0.840 | 0.029 | 1.00 | — |
| 3 | univariate | ret_10_H1 > -0.001261 ⇒ Buy | 0.825 | — | 0.60 | 0.000 |
| 4 | univariate | bb_pos_20_2_H1 > 0.07135 ⇒ Buy | 0.853 | — | 0.50 | 0.000 |
| 5 | univariate | ema_dist_20_H1 > 0.1122 ⇒ Buy | 0.850 | — | 0.50 | 0.000 |
| 6 | univariate | ret_10_H4 > 0.0008085 ⇒ Buy | 0.812 | — | 0.50 | 0.000 |
| 7 | univariate | ema_dist_20_H4 > 0.1852 ⇒ Buy | 0.810 | — | 0.50 | 0.000 |
| 8 | univariate | ret_3_H4 > 0.0001024 ⇒ Buy | 0.806 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.0627 ⇒ Buy | 0.804 | — | 0.50 | 0.000 |
| 10 | univariate | ema_dist_20_M15 > 0.07806 ⇒ Buy | 0.744 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.73, ret_3_H1=0.12, ema_dist_20_H1=0.05, ret_10_H1=0.04, ret_10_H4=0.03

|--- bb_pos_20_2_H1 <= -0.09
|   |--- ret_10_H4 <= 0.00
|   |   |--- ret_3_H1 <= -0.00
|   |   |   |--- ret_10_H1 <= -0.01
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H1 >  -0.01
|   |   |   |   |--- class: 1
|   |   |--- ret_3_H1 >  -0.00
|   |   |   |--- ret_10_H1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H1 >  -0.00
|   |   |   |   |--- class: 0
|   |--- ret_10_H4 >  0.00
|   |   |--- class: 0
|--- bb_pos_20_2_H1 >  -0.09
|   |--- ema_dist_20_H1 <= 0.76
|   |   |--- ret_3_H1 <= 0.00
|   |   |   |--- ema_dist_20_M15 <= 0.25
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_M15 >  0.25
|   |   |   |   |--- class: 1
|   |   |--- ret_3_H1 >  0.00
|   |   |   |--- ret_10_M5 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_M5 >  0.00
|   |   |   |   |--- class: 0
|   |--- ema_dist_20_H1 >  0.76
|   |   |--- ema_dist_20_M5 <= 2.25
|   |   |   |--- range_norm_H4 <= 1.52
|   |   |   |   |--- class: 1
|   |   |   |--- range_norm_H4 >  1.52
|   |   |   |   |--- class: 1
|   |   |--- ema_dist_20_M5 >  2.25
|   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_H1=1.0^ret_10_H1=>0.0079^ret_3_H4=>0.0089] V [close_vs_session_open_H1=1.0^bb_pos_20_2_H4=0.79-1.03^ret_1_H4=0.0018-0.0031] V [close_vs_session_open_H1=1.0^ret_10_H1=0.005-0.0079^ret_3_H1=0.0018-0.003] V [close_vs_session_open_M1=1.0^ret_10_H1=0.0032-0.005^ret_3_H1=0.0018-0.003] V [close_vs_session_open_M1=1.0^ret_3_H4=0.0054-0.0089^prior_bar_sign_H1=-1.0] V [close_vs_session_open_M1=1.0^ret_10_H1=0.0032-0.005^ret_3_H4=0.0033-0.0054^prior_bar_sign_H1=-1.0] V [close_vs_session_open_M1=1.0^ema_dist_20_H1=1.81-2.49^bb_pos_20_2_H1=0.91-1.09] V [ret_10_H1=0.0016-0.0032^prior_bar_sign_H1=-1.0^prior_bar_sign_H4=-1.0] V [close_vs_session_open_H1=1.0^bb_pos_20_2_H1=0.44-0.71^ema_dist_20_M15=0.081-0.44] V [close_vs_session_open_M5=1.0^ema_dist_20_H1=1.26-1.81^atr_ratio_M1=0.094-0.11] V [ret_10_H4=>0.014^close_vs_session_open_H4=1.0] V [bb_pos_20_2_H4=0.35-0.61^prior_bar_sign_H4=-1.0] V [close_vs_session_open_H1=1.0^ret_10_H4=0.0059-0.0092^close_vs_session_open_M1=1.0] V [ema_dist_20_H1=0.69-1.26] V [ema_dist_20_H1=1.81-2.49^close_vs_session_open_M1=-1.0] V [ema_dist_20_H1=1.26-1.81^prior_bar_sign_M15=-1.0^close_vs_session_open_M5=-1.0] V [close_vs_session_open_M5=1.0^ema_dist_20_H1=1.26-1.81^atr_ratio_M1=0.13-0.15] V [bb_pos_20_2_H1=0.076-0.44^prior_bar_sign_H4=-1.0^ret_3_H1=-0.0027--0.0014] V [close_vs_session_open_M5=1.0^bb_pos_20_2_H1=>1.09^dow=1] V [ema_dist_20_H1=0.12-0.69^ret_3_H1=-0.0014--0.00055] V [ema_dist_20_H1=>2.49] V [ema_dist_20_H1=1.26-1.81^hour_utc=<8.0] V [ema_dist_20_H1=0.12-0.69^close_vs_session_open_H1=-1.0] V [bb_pos_20_2_H1=-0.34-0.076^prior_bar_sign_H4=-1.0^prior_bar_sign_H1=-1.0] V [close_vs_session_open_M1=1.0^ema_dist_20_H1=1.81-2.49] V [ema_dist_20_H1=1.26-1.81^ema_dist_20_M1=1.22-1.8] V [ret_3_H1=<-0.0047^range_norm_H4=>2.24^ret_10_H1=-0.0049--0.003] V [ret_10_M15=<-0.0043^ret_10_H4=0.00083-0.003] V [ema_dist_20_H1=1.26-1.81^bb_pos_20_2_H1=0.91-1.09] V [ret_10_M15=-0.0043--0.0024^bb_pos_20_2_H1=-0.34-0.076] V [bb_pos_20_2_M15=<-0.75^ema_dist_20_H1=-1.56--1.03^range_norm_M15=>1.42] V [atr_ratio_H4=1.75-1.88^ema_dist_20_H1=0.12-0.69] V [ret_10_M5=<-0.002^atr_ratio_M15=0.74-0.8^ret_10_M1=-0.00032--0.00017] V [ret_10_H4=0.0059-0.0092^ret_10_M15=-0.0043--0.0024]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
