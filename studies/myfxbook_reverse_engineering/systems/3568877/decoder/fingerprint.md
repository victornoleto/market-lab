# Decoder fingerprint — system 3568877

Generated: 2026-05-02T07:02:14

## Sanity (martingale + lot dynamics)

- n_trades: **3998**, deposits: 2
- pairs: {'GBPUSD': 1059, 'USDCAD': 867, 'EURGBP': 686, 'USDJPY': 462, 'EURCHF': 338, 'EURUSD': 239, 'EURJPY': 183, 'USDCHF': 113, 'AUDUSD': 51}
- actions: {'Buy': 2026, 'Sell': 1972}
- date range: 2020-03-10 10:40:02+00:00 → 2021-06-16 22:56:23+00:00
- max gap days: 3.6
- lot p50/p95/p99/max: 0.02 / 0.02 / 0.02 / 0.02
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=1, max_streak=1
- hold p50/p95/max (h): 3.15 / 303.83 / 7415.95

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 03:00 — 331 trades
  - 10:00 — 326 trades
  - 17:00 — 308 trades
  - 18:00 — 294 trades
  - 16:00 — 285 trades

Top entry hour:5min (UTC):
  - 03:00 — 164 trades
  - 02:00 — 111 trades
  - 18:00 — 54 trades
  - 18:35 — 53 trades
  - 20:05 — 40 trades

Exit kind distribution:
  - manual_or_time: 3998

Direction by pair (Buy %):
  - AUDUSD: total=51, buy_pct=13.7%
  - EURCHF: total=338, buy_pct=55.6%
  - EURGBP: total=686, buy_pct=48.7%
  - EURJPY: total=183, buy_pct=58.5%
  - EURUSD: total=239, buy_pct=41.8%
  - GBPUSD: total=1059, buy_pct=35.8%
  - USDCAD: total=867, buy_pct=65.9%
  - USDCHF: total=113, buy_pct=50.4%
  - USDJPY: total=462, buy_pct=61.3%

Direction by hour (Buy %, top 5 by activity):
  - hour=03: total=331, buy_pct=51.7%
  - hour=10: total=326, buy_pct=50.0%
  - hour=17: total=308, buy_pct=51.3%
  - hour=18: total=294, buy_pct=56.1%
  - hour=16: total=285, buy_pct=49.5%

## Feature extraction

- trades processed: 3998
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.29, ret_10_H1=0.14, pair_cluster_dispersion=0.13, ret_3_H4=0.12, atr... | 0.524 | 0.017 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.5068); Always-Sell = 0.4932 | 0.507 | — | 1.00 | — |
| 3 | ripper | RIPPER ruleset: [[close_vs_session_open_H1=1.0^ret_3_H4=>0.0064^ret_10_H4=0.0061-0.0097] V [atr_ratio_M5=<0.16^bb_pos_20_2_H1=-... | 0.504 | 0.046 | 1.00 | — |
| 4 | univariate | bb_pos_20_2_H1 > -0.5348 ⇒ Buy | 0.544 | — | 0.70 | 0.000 |
| 5 | univariate | ret_3_H4 > -0.001184 ⇒ Buy | 0.546 | — | 0.60 | 0.000 |
| 6 | univariate | ema_dist_20_H1 > -0.4477 ⇒ Buy | 0.536 | — | 0.60 | 0.002 |
| 7 | univariate | bb_pos_20_2_M5 > 0.002064 ⇒ Sell | 0.531 | — | 0.50 | 0.026 |
| 8 | univariate | pair_cluster_dispersion > 0.0007558 ⇒ Sell | 0.527 | — | 0.50 | 0.236 |
| 9 | univariate | bb_pos_20_2_M15 > -0.005716 ⇒ Buy | 0.525 | — | 0.50 | 0.456 |
| 10 | univariate | ret_10_H1 > 0.001077 ⇒ Buy | 0.547 | — | 0.40 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.29, ret_10_H1=0.14, pair_cluster_dispersion=0.13, ret_3_H4=0.12, atr_ratio_M15=0.10

|--- ret_10_H1 <= 0.00
|   |--- atr_ratio_M15 <= 0.52
|   |   |--- ema_dist_20_H4 <= 0.17
|   |   |   |--- ema_dist_20_H4 <= -1.97
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_H4 >  -1.97
|   |   |   |   |--- class: 1
|   |   |--- ema_dist_20_H4 >  0.17
|   |   |   |--- pair_cluster_dispersion <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- pair_cluster_dispersion >  0.00
|   |   |   |   |--- class: 1
|   |--- atr_ratio_M15 >  0.52
|   |   |--- ret_3_H4 <= -0.00
|   |   |   |--- ema_dist_20_H4 <= -1.18
|   |   |   |   |--- class: 0
|   |   |   |--- ema_dist_20_H4 >  -1.18
|   |   |   |   |--- class: 0
|   |   |--- ret_3_H4 >  -0.00
|   |   |   |--- ema_dist_20_M15 <= -0.76
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_M15 >  -0.76
|   |   |   |   |--- class: 0
|--- ret_10_H1 >  0.00
|   |--- range_norm_H4 <= 1.41
|   |   |--- pair_cluster_dispersion <= 0.00
|   |   |   |--- ema_dist_20_H4 <= 0.76
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_H4 >  0.76
|   |   |   |   |--- class: 1
|   |   |--- pair_cluster_dispersion >  0.00
|   |   |   |--- ret_10_H1 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H1 >  0.00
|   |   |   |   |--- class: 0
|   |--- range_norm_H4 >  1.41
|   |   |--- ret_3_H4 <= 0.00
|   |   |   |--- bb_pos_20_2_H4 <= 0.43
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_H4 >  0.43
|   |   |   |   |--- class: 0
|   |   |--- ret_3_H4 >  0.00
|   |   |   |--- ret_1_H4 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_1_H4 >  0.00
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 3)
```
RIPPER ruleset:
[[close_vs_session_open_H1=1.0^ret_3_H4=>0.0064^ret_10_H4=0.0061-0.0097] V [atr_ratio_M5=<0.16^bb_pos_20_2_H1=-0.54--0.32^bb_pos_20_2_H4=-0.98--0.73] V [close_vs_session_open_H4=1.0^dollar_index_proxy=>0.67^bb_pos_20_2_H1=>0.94^ret_3_H4=>0.0064] V [atr_ratio_M1=<0.056^ema_dist_20_H4=-0.81--0.37^atr_ratio_H4=<1.46] V [range_norm_H4=1.5-1.82^dow=2^close_vs_session_open_M1=-1.0^ret_1_H4=<-0.0033] V [ret_10_H4=-0.0059--0.0037^atr_ratio_M1=<0.056] V [range_norm_H4=1.5-1.82^ema_dist_20_H1=>2.17^dow=1]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
