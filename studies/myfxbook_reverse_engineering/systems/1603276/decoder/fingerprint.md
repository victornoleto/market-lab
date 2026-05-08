# Decoder fingerprint — system 1603276

Generated: 2026-05-02T04:37:05

## Sanity (martingale + lot dynamics)

- n_trades: **594**, deposits: 277
- pairs: {'EURUSD': 404, 'GBPUSD': 104, 'USDJPY': 70, 'XAUUSD': 16}
- actions: {'Buy': 314, 'Sell': 280}
- date range: 2016-01-25 09:30:45+00:00 → 2017-09-07 10:46:12+00:00
- max gap days: 9.1
- lot p50/p95/p99/max: 0.31 / 0.40 / 0.41 / 0.41
- lot p95/p50 ratio: 1.29
- martingale flag: **PASS (no martingale)**, steps=1, max_streak=1
- hold p50/p95/max (h): 0.00 / 0.06 / 1.06

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 10:00 — 72 trades
  - 15:00 — 69 trades
  - 09:00 — 57 trades
  - 17:00 — 56 trades
  - 11:00 — 47 trades

Top entry hour:5min (UTC):
  - 15:30 — 31 trades
  - 17:00 — 15 trades
  - 10:05 — 11 trades
  - 16:10 — 10 trades
  - 21:00 — 10 trades

Exit kind distribution:
  - manual_or_time: 594

Direction by pair (Buy %):
  - EURUSD: total=404, buy_pct=53.5%
  - GBPUSD: total=104, buy_pct=51.0%
  - USDJPY: total=70, buy_pct=47.1%
  - XAUUSD: total=16, buy_pct=75.0%

Direction by hour (Buy %, top 5 by activity):
  - hour=10: total=72, buy_pct=47.2%
  - hour=15: total=69, buy_pct=56.5%
  - hour=09: total=57, buy_pct=49.1%
  - hour=17: total=56, buy_pct=55.4%
  - hour=16: total=47, buy_pct=53.2%

## Feature extraction

- trades processed: 594
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ema_dist_20_H1=0.71, ret_10_H1=0.16, ret_3_H1=0.06, ret_10_H4=0.04, bb_pos_20_2_M5=0.... | 0.827 | 0.018 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_H1=1.0^bb_pos_20_2_H4=0.8-1.1] V [close_vs_session_open_M5=1.0^ret_3_H4=0.004-0.0062] V... | 0.742 | 0.039 | 1.00 | — |
| 3 | univariate | ema_dist_20_H1 > -0.3842 ⇒ Buy | 0.835 | — | 0.60 | 0.000 |
| 4 | univariate | bb_pos_20_2_H1 > -0.3283 ⇒ Buy | 0.825 | — | 0.60 | 0.000 |
| 5 | univariate | ret_10_H1 > -0.0007909 ⇒ Buy | 0.805 | — | 0.60 | 0.000 |
| 6 | univariate | ret_3_H4 > -0.0007716 ⇒ Buy | 0.785 | — | 0.60 | 0.000 |
| 7 | univariate | ema_dist_20_H4 > -0.3376 ⇒ Buy | 0.781 | — | 0.60 | 0.000 |
| 8 | univariate | ret_10_H4 > 0.0002989 ⇒ Buy | 0.810 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.05935 ⇒ Buy | 0.786 | — | 0.50 | 0.000 |
| 10 | univariate | ema_dist_20_M15 > -0.2664 ⇒ Buy | 0.700 | — | 0.60 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ema_dist_20_H1=0.71, ret_10_H1=0.16, ret_3_H1=0.06, ret_10_H4=0.04, bb_pos_20_2_M5=0.01

|--- ema_dist_20_H1 <= -0.27
|   |--- ret_10_H4 <= -0.00
|   |   |--- range_norm_H4 <= 1.41
|   |   |   |--- range_norm_H4 <= 0.83
|   |   |   |   |--- class: 0
|   |   |   |--- range_norm_H4 >  0.83
|   |   |   |   |--- class: 0
|   |   |--- range_norm_H4 >  1.41
|   |   |   |--- class: 0
|   |--- ret_10_H4 >  -0.00
|   |   |--- class: 0
|--- ema_dist_20_H1 >  -0.27
|   |--- ret_3_H1 <= 0.00
|   |   |--- atr_ratio_M15 <= 0.76
|   |   |   |--- ret_3_M15 <= -0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_3_M15 >  -0.00
|   |   |   |   |--- class: 1
|   |   |--- atr_ratio_M15 >  0.76
|   |   |   |--- class: 1
|   |--- ret_3_H1 >  0.00
|   |   |--- ret_10_H1 <= 0.00
|   |   |   |--- class: 0
|   |   |--- ret_10_H1 >  0.00
|   |   |   |--- bb_pos_20_2_M5 <= 0.43
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_M5 >  0.43
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_H1=1.0^bb_pos_20_2_H4=0.8-1.1] V [close_vs_session_open_M5=1.0^ret_3_H4=0.004-0.0062] V [close_vs_session_open_M1=1.0^ema_dist_20_H1=>2.64] V [bb_pos_20_2_H4=0.59-0.8^prior_bar_sign_H1=-1.0^prior_bar_sign_H4=-1.0] V [ret_10_H1=0.0038-0.0055^dollar_index_proxy=-0.3333333333333333] V [bb_pos_20_2_H4=0.32-0.59^prior_bar_sign_H4=-1.0] V [bb_pos_20_2_H1=0.72-0.91] V [bb_pos_20_2_H1=0.15-0.47^prior_bar_sign_H4=-1.0] V [close_vs_session_open_M1=1.0^bb_pos_20_2_H1=0.47-0.72^prior_bar_sign_H1=-1.0] V [bb_pos_20_2_H4=0.59-0.8] V [bb_pos_20_2_H4=>1.1^prior_bar_sign_M1=-1.0] V [bb_pos_20_2_H1=0.91-1.11^prior_bar_sign_M1=1.0] V [ema_dist_20_H1=-0.38-0.18^ret_3_H1=-0.00098--0.00047] V [close_vs_session_open_M1=1.0^hour_utc=17.0-19.0] V [range_norm_H4=>2.45^ret_10_H4=-0.0014-0.00026] V [bb_pos_20_2_H1=-0.33-0.15^prior_bar_sign_H1=-1.0^prior_bar_sign_H4=-1.0] V [ret_10_H4=0.00026-0.0019^atr_ratio_H4=1.71-1.81] V [ema_dist_20_H4=0.97-1.69^bb_pos_20_2_M15=-0.72--0.5] V [atr_ratio_M5=0.43-0.5^bb_pos_20_2_M15=>0.7]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
