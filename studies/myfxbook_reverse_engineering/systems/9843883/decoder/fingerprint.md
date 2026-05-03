# Decoder fingerprint — system 9843883

Generated: 2026-05-02T11:15:07

## Sanity (martingale + lot dynamics)

- n_trades: **2576**, deposits: 2
- pairs: {'EURUSD': 1288, 'USDCHF': 1288}
- actions: {'Sell': 1485, 'Buy': 1091}
- date range: 2022-09-09 15:59:30+00:00 → 2026-04-28 16:37:51+00:00
- max gap days: 19.9
- lot p50/p95/p99/max: 0.01 / 0.01 / 0.01 / 0.01
- lot p95/p50 ratio: 1.00
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 24.96 / 1014.43 / 10028.84

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 13:00 — 1450 trades
  - 16:00 — 146 trades
  - 17:00 — 140 trades
  - 15:00 — 112 trades
  - 10:00 — 102 trades

Top entry hour:5min (UTC):
  - 13:00 — 1304 trades
  - 13:20 — 28 trades
  - 15:30 — 24 trades
  - 16:25 — 22 trades
  - 10:35 — 20 trades

Exit kind distribution:
  - manual_or_time: 2576

Direction by pair (Buy %):
  - EURUSD: total=1288, buy_pct=42.4%
  - USDCHF: total=1288, buy_pct=42.3%

Direction by hour (Buy %, top 5 by activity):
  - hour=13: total=1450, buy_pct=44.2%
  - hour=16: total=146, buy_pct=34.2%
  - hour=17: total=140, buy_pct=45.7%
  - hour=15: total=112, buy_pct=48.2%
  - hour=10: total=102, buy_pct=37.3%

## Feature extraction

- trades processed: 2576
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | ripper | RIPPER ruleset: [[ret_10_H1=>0.005^is_first_min_of_hour=0^dollar_index_proxy=-1.0^prior_bar_sign_M1=-1.0] V [close_vs_session_o... | 0.589 | 0.252 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.4235); Always-Sell = 0.5765 | 0.576 | — | 1.00 | — |
| 3 | tree | DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.35, ret_10_H1=0.14, range_norm_H4=0.10, ret_3_M5=0.10, ret_1_H4=0.07... | 0.557 | 0.165 | 1.00 | — |
| 4 | univariate | ret_3_M5 > -0.0005059 ⇒ Sell | 0.572 | — | 0.80 | 0.000 |
| 5 | univariate | ret_1_M15 > -0.0005012 ⇒ Sell | 0.571 | — | 0.80 | 0.000 |
| 6 | univariate | ret_1_M5 > -0.0002738 ⇒ Sell | 0.571 | — | 0.80 | 0.000 |
| 7 | univariate | ret_3_M1 > -0.0002115 ⇒ Sell | 0.570 | — | 0.80 | 0.000 |
| 8 | univariate | ret_1_H1 > -0.0009669 ⇒ Sell | 0.569 | — | 0.80 | 0.000 |
| 9 | univariate | ema_dist_20_H4 > 0.8673 ⇒ Buy | 0.582 | — | 0.30 | 0.000 |
| 10 | univariate | bb_pos_20_2_H1 > 0.5584 ⇒ Buy | 0.573 | — | 0.30 | 0.000 |

### RIPPER full output (rank 1)
```
RIPPER ruleset:
[[ret_10_H1=>0.005^is_first_min_of_hour=0^dollar_index_proxy=-1.0^prior_bar_sign_M1=-1.0] V [close_vs_session_open_H4=1.0^ema_dist_20_H4=1.34-2.08^is_first_min_of_hour=0^ret_3_H4=>0.0057^is_first_5min_of_hour=0]]
```

### TREE full output (rank 3)
```
DecisionTree(max_depth=4) — top features: ema_dist_20_H4=0.35, ret_10_H1=0.14, range_norm_H4=0.10, ret_3_M5=0.10, ret_1_H4=0.07

|--- ema_dist_20_H4 <= -0.62
|   |--- ret_3_M5 <= -0.00
|   |   |--- atr_ratio_M5 <= 0.37
|   |   |   |--- class: 1
|   |   |--- atr_ratio_M5 >  0.37
|   |   |   |--- class: 0
|   |--- ret_3_M5 >  -0.00
|   |   |--- ret_1_H4 <= -0.00
|   |   |   |--- range_norm_H1 <= 1.34
|   |   |   |   |--- class: 0
|   |   |   |--- range_norm_H1 >  1.34
|   |   |   |   |--- class: 1
|   |   |--- ret_1_H4 >  -0.00
|   |   |   |--- atr_ratio_M15 <= 0.78
|   |   |   |   |--- class: 0
|   |   |   |--- atr_ratio_M15 >  0.78
|   |   |   |   |--- class: 0
|--- ema_dist_20_H4 >  -0.62
|   |--- ret_10_H1 <= 0.00
|   |   |--- ret_10_M15 <= -0.00
|   |   |   |--- ema_dist_20_H1 <= -0.87
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_H1 >  -0.87
|   |   |   |   |--- class: 1
|   |   |--- ret_10_M15 >  -0.00
|   |   |   |--- ret_3_H4 <= -0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_3_H4 >  -0.00
|   |   |   |   |--- class: 0
|   |--- ret_10_H1 >  0.00
|   |   |--- range_norm_H4 <= 2.18
|   |   |   |--- ema_dist_20_H4 <= 2.12
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_H4 >  2.12
|   |   |   |   |--- class: 1
|   |   |--- range_norm_H4 >  2.18
|   |   |   |--- class: 0

```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
