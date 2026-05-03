# Decoder fingerprint — system 2123808

Generated: 2026-05-02T05:56:39

## Sanity (martingale + lot dynamics)

- n_trades: **856**, deposits: 3
- pairs: {'USDCAD': 256, 'AUDCHF': 181, 'AUDCAD': 142, 'CADCHF': 139, 'AUDUSD': 138}
- actions: {'Buy': 464, 'Sell': 392}
- date range: 2017-05-16 11:52:46+00:00 → 2021-06-15 14:30:55+00:00
- max gap days: 28.7
- lot p50/p95/p99/max: 0.06 / 0.06 / 0.06 / 0.06
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 168.71 / 1914.06 / 9947.83

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 17:00 — 101 trades
  - 15:00 — 70 trades
  - 16:00 — 66 trades
  - 03:00 — 48 trades
  - 13:00 — 42 trades

Top entry hour:5min (UTC):
  - 15:30 — 25 trades
  - 17:00 — 20 trades
  - 00:05 — 16 trades
  - 17:55 — 13 trades
  - 17:50 — 12 trades

Exit kind distribution:
  - manual_or_time: 856

Direction by pair (Buy %):
  - AUDCAD: total=142, buy_pct=53.5%
  - AUDCHF: total=181, buy_pct=58.6%
  - AUDUSD: total=138, buy_pct=57.2%
  - CADCHF: total=139, buy_pct=49.6%
  - USDCAD: total=256, buy_pct=52.3%

Direction by hour (Buy %, top 5 by activity):
  - hour=17: total=101, buy_pct=53.5%
  - hour=15: total=70, buy_pct=57.1%
  - hour=16: total=66, buy_pct=43.9%
  - hour=03: total=48, buy_pct=62.5%
  - hour=13: total=42, buy_pct=52.4%

## Feature extraction

- trades processed: 856
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_10_H4=0.27, bb_pos_20_2_H4=0.22, bb_pos_20_2_M15=0.18, bb_pos_20_2_M5=0.13, atr_r... | 0.556 | 0.053 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.5421); Always-Sell = 0.4579 | 0.542 | — | 1.00 | — |
| 3 | univariate | dow > 0 ⇒ Buy | 0.550 | — | 0.84 | 0.991 |
| 4 | univariate | pair_cluster_dispersion > 0.0003105 ⇒ Buy | 0.547 | — | 0.80 | 1.000 |
| 5 | ripper | RIPPER ruleset: [[ret_10_H4=<-0.014^ret_1_M15=<-0.0007]] | 0.485 | 0.043 | 1.00 | — |
| 6 | univariate | range_norm_M15 > 0.5973 ⇒ Buy | 0.554 | — | 0.70 | 0.498 |
| 7 | univariate | atr_ratio_H4 > 1.933 ⇒ Sell | 0.556 | — | 0.40 | 0.314 |
| 8 | univariate | ret_10_H4 > 0.004779 ⇒ Sell | 0.583 | — | 0.30 | 0.000 |
| 9 | univariate | ema_dist_20_H4 > 1.196 ⇒ Sell | 0.576 | — | 0.30 | 0.003 |
| 10 | univariate | ret_1_H4 > 0.001024 ⇒ Sell | 0.546 | — | 0.30 | 1.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_10_H4=0.27, bb_pos_20_2_H4=0.22, bb_pos_20_2_M15=0.18, bb_pos_20_2_M5=0.13, atr_ratio_M5=0.12

|--- ret_10_H4 <= -0.01
|   |--- bb_pos_20_2_H4 <= -1.08
|   |   |--- class: 1
|   |--- bb_pos_20_2_H4 >  -1.08
|   |   |--- class: 1
|--- ret_10_H4 >  -0.01
|   |--- bb_pos_20_2_H4 <= 0.90
|   |   |--- bb_pos_20_2_M15 <= -0.01
|   |   |   |--- bb_pos_20_2_M5 <= -0.83
|   |   |   |   |--- class: 1
|   |   |   |--- bb_pos_20_2_M5 >  -0.83
|   |   |   |   |--- class: 0
|   |   |--- bb_pos_20_2_M15 >  -0.01
|   |   |   |--- atr_ratio_M5 <= 0.28
|   |   |   |   |--- class: 1
|   |   |   |--- atr_ratio_M5 >  0.28
|   |   |   |   |--- class: 1
|   |--- bb_pos_20_2_H4 >  0.90
|   |   |--- atr_ratio_M1 <= 0.09
|   |   |   |--- class: 1
|   |   |--- atr_ratio_M1 >  0.09
|   |   |   |--- class: 0

```

### RIPPER full output (rank 5)
```
RIPPER ruleset:
[[ret_10_H4=<-0.014^ret_1_M15=<-0.0007]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
