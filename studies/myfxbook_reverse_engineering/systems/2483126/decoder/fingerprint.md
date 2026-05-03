# Decoder fingerprint — system 2483126

Generated: 2026-05-02T06:50:09

## Sanity (martingale + lot dynamics)

- n_trades: **1910**, deposits: 2
- pairs: {'EURJPY': 576, 'AUDUSD': 364, 'USDJPY': 347, 'NZDUSD': 343, 'EURUSD': 280}
- actions: {'Buy': 1069, 'Sell': 841}
- date range: 2018-03-12 00:05:02+00:00 → 2021-06-16 21:01:13+00:00
- max gap days: 26.8
- lot p50/p95/p99/max: 0.02 / 0.02 / 0.02 / 0.02
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=1, max_streak=1
- hold p50/p95/max (h): 68.68 / 1822.51 / 6199.90

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 18:00 — 160 trades
  - 19:00 — 152 trades
  - 17:00 — 138 trades
  - 16:00 — 107 trades
  - 12:00 — 104 trades

Top entry hour:5min (UTC):
  - 18:00 — 157 trades
  - 19:00 — 149 trades
  - 17:00 — 133 trades
  - 16:00 — 106 trades
  - 12:00 — 103 trades

Exit kind distribution:
  - manual_or_time: 1910

Direction by pair (Buy %):
  - AUDUSD: total=364, buy_pct=58.5%
  - EURJPY: total=576, buy_pct=58.2%
  - EURUSD: total=280, buy_pct=55.4%
  - NZDUSD: total=343, buy_pct=50.1%
  - USDJPY: total=347, buy_pct=55.9%

Direction by hour (Buy %, top 5 by activity):
  - hour=18: total=160, buy_pct=51.9%
  - hour=19: total=152, buy_pct=65.1%
  - hour=17: total=138, buy_pct=54.3%
  - hour=16: total=107, buy_pct=48.6%
  - hour=12: total=104, buy_pct=45.2%

## Feature extraction

- trades processed: 1910
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | baseline | Always-Buy (y_buy mean = 0.5597); Always-Sell = 0.4403 | 0.560 | — | 1.00 | — |
| 2 | univariate | ret_1_M5 > -0.0002731 ⇒ Buy | 0.555 | — | 0.80 | 0.000 |
| 3 | univariate | bb_pos_20_2_M5 > -0.6276 ⇒ Buy | 0.555 | — | 0.80 | 0.000 |
| 4 | univariate | dow > 0 ⇒ Buy | 0.551 | — | 0.81 | 0.003 |
| 5 | univariate | ema_dist_20_M5 > -1.142 ⇒ Buy | 0.550 | — | 0.80 | 0.003 |
| 6 | univariate | atr_ratio_M15 > 0.4036 ⇒ Buy | 0.550 | — | 0.80 | 0.003 |
| 7 | tree | DecisionTree(max_depth=4) — top features: atr_ratio_H4=0.21, range_norm_M15=0.15, ret_3_H4=0.15, range_norm_H1=0.15, pair_clust... | 0.466 | 0.120 | 1.00 | — |
| 8 | ripper | RIPPER ruleset: [[atr_ratio_H4=<1.46^ema_dist_20_H4=<-2.62]] | 0.451 | 0.146 | 1.00 | — |
| 9 | univariate | ret_10_M15 > 0.0007604 ⇒ Sell | 0.550 | — | 0.30 | 0.004 |
| 10 | univariate | range_norm_M15 > 1.064 ⇒ Sell | 0.548 | — | 0.30 | 0.009 |

### TREE full output (rank 7)
```
DecisionTree(max_depth=4) — top features: atr_ratio_H4=0.21, range_norm_M15=0.15, ret_3_H4=0.15, range_norm_H1=0.15, pair_cluster_dispersion=0.14

|--- atr_ratio_H4 <= 1.51
|   |--- ret_3_H4 <= 0.00
|   |   |--- ret_10_M15 <= -0.00
|   |   |   |--- class: 1
|   |   |--- ret_10_M15 >  -0.00
|   |   |   |--- close_vs_session_open_M1 <= -0.50
|   |   |   |   |--- class: 1
|   |   |   |--- close_vs_session_open_M1 >  -0.50
|   |   |   |   |--- class: 1
|   |--- ret_3_H4 >  0.00
|   |   |--- class: 0
|--- atr_ratio_H4 >  1.51
|   |--- range_norm_H1 <= 1.79
|   |   |--- pair_cluster_dispersion <= 0.00
|   |   |   |--- ret_3_M1 <= -0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_3_M1 >  -0.00
|   |   |   |   |--- class: 1
|   |   |--- pair_cluster_dispersion >  0.00
|   |   |   |--- range_norm_M15 <= 0.77
|   |   |   |   |--- class: 1
|   |   |   |--- range_norm_M15 >  0.77
|   |   |   |   |--- class: 0
|   |--- range_norm_H1 >  1.79
|   |   |--- class: 1

```

### RIPPER full output (rank 8)
```
RIPPER ruleset:
[[atr_ratio_H4=<1.46^ema_dist_20_H4=<-2.62]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
