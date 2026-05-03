# Decoder fingerprint — system 9830783

Generated: 2026-05-02T11:00:16

## Sanity (martingale + lot dynamics)

- n_trades: **4000**, deposits: 0
- pairs: {'USDCAD': 1369, 'GBPCHF': 1353, 'EURCHF': 733, 'AUDNZD': 496, 'CADCHF': 49}
- actions: {'Sell': 2105, 'Buy': 1895}
- date range: 2022-10-03 15:00:00+00:00 → 2026-05-01 15:21:04+00:00
- max gap days: 10.9
- lot p50/p95/p99/max: 1.12 / 1.38 / 1.39 / 1.48
- lot p95/p50 ratio: 1.23
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 16.22 / 675.62 / 25617.65

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 18:00 — 395 trades
  - 17:00 — 329 trades
  - 19:00 — 325 trades
  - 11:00 — 322 trades
  - 12:00 — 254 trades

Top entry hour:5min (UTC):
  - 18:00 — 395 trades
  - 17:00 — 329 trades
  - 19:00 — 325 trades
  - 11:00 — 321 trades
  - 16:00 — 252 trades

Exit kind distribution:
  - manual_or_time: 4000

Direction by pair (Buy %):
  - AUDNZD: total=496, buy_pct=48.2%
  - CADCHF: total=49, buy_pct=71.4%
  - EURCHF: total=733, buy_pct=48.0%
  - GBPCHF: total=1353, buy_pct=46.3%
  - USDCAD: total=1369, buy_pct=46.9%

Direction by hour (Buy %, top 5 by activity):
  - hour=18: total=395, buy_pct=45.1%
  - hour=17: total=329, buy_pct=49.8%
  - hour=19: total=325, buy_pct=45.5%
  - hour=11: total=322, buy_pct=45.3%
  - hour=12: total=254, buy_pct=48.0%

## Feature extraction

- trades processed: 4000
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | ripper | RIPPER ruleset: [[ema_dist_20_H1=>2.29^ret_10_H4=>0.0073^prior_bar_sign_H1=-1.0] V [ema_dist_20_H1=>2.29^hour_utc=14.0-16.0] V ... | 0.535 | 0.031 | 1.00 | — |
| 2 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.28, ret_10_H4=0.17, ema_dist_20_H1=0.14, bb_pos_20_2_H4=0.11, atr_ra... | 0.527 | 0.021 | 1.00 | — |
| 3 | baseline | Always-Buy (y_buy mean = 0.4738); Always-Sell = 0.5262 | 0.526 | — | 1.00 | — |
| 4 | univariate | bb_pos_20_2_M15 > 0.02078 ⇒ Buy | 0.553 | — | 0.50 | 0.000 |
| 5 | univariate | ema_dist_20_M15 > 0.355 ⇒ Buy | 0.550 | — | 0.40 | 0.000 |
| 6 | univariate | ret_3_H1 > 0.0003844 ⇒ Buy | 0.547 | — | 0.40 | 0.000 |
| 7 | univariate | ret_10_H4 > 0.001379 ⇒ Buy | 0.542 | — | 0.40 | 0.000 |
| 8 | univariate | ret_10_H1 > 0.002011 ⇒ Buy | 0.560 | — | 0.30 | 0.000 |
| 9 | univariate | ret_3_H4 > 0.001997 ⇒ Buy | 0.559 | — | 0.30 | 0.000 |
| 10 | univariate | ret_10_M15 > 0.0006196 ⇒ Buy | 0.538 | — | 0.30 | 0.000 |

### RIPPER full output (rank 1)
```
RIPPER ruleset:
[[ema_dist_20_H1=>2.29^ret_10_H4=>0.0073^prior_bar_sign_H1=-1.0] V [ema_dist_20_H1=>2.29^hour_utc=14.0-16.0] V [close_vs_session_open_M15=1.0^bb_pos_20_2_M5=-0.22--0.0051^ema_dist_20_M15=0.72-1.15]]
```

### TREE full output (rank 2)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.28, ret_10_H4=0.17, ema_dist_20_H1=0.14, bb_pos_20_2_H4=0.11, atr_ratio_M15=0.10

|--- bb_pos_20_2_H1 <= 0.77
|   |--- ret_10_H4 <= -0.02
|   |   |--- class: 1
|   |--- ret_10_H4 >  -0.02
|   |   |--- ema_dist_20_H1 <= -2.09
|   |   |   |--- ret_10_H4 <= -0.01
|   |   |   |   |--- class: 0
|   |   |   |--- ret_10_H4 >  -0.01
|   |   |   |   |--- class: 0
|   |   |--- ema_dist_20_H1 >  -2.09
|   |   |   |--- ema_dist_20_H4 <= -1.64
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_H4 >  -1.64
|   |   |   |   |--- class: 0
|--- bb_pos_20_2_H1 >  0.77
|   |--- atr_ratio_M15 <= 0.78
|   |   |--- bb_pos_20_2_H4 <= 0.85
|   |   |   |--- atr_ratio_H4 <= 1.63
|   |   |   |   |--- class: 1
|   |   |   |--- atr_ratio_H4 >  1.63
|   |   |   |   |--- class: 0
|   |   |--- bb_pos_20_2_H4 >  0.85
|   |   |   |--- ret_1_H4 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_1_H4 >  0.00
|   |   |   |   |--- class: 0
|   |--- atr_ratio_M15 >  0.78
|   |   |--- bb_pos_20_2_H4 <= 0.81
|   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_H4 >  0.81
|   |   |   |--- class: 1

```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
