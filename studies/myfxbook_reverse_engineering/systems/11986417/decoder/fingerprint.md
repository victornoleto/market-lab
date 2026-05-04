# Decoder fingerprint — system 11986417

Generated: 2026-05-03T21:10:32
⚠ Sampled run: only the most-recent 120 trades were used (full = 399)

## Sanity (martingale + lot dynamics)

- n_trades: **399**, deposits: 0
- pairs: {'XAUUSD': 399}
- actions: {'Buy': 237, 'Sell': 162}
- date range: 2026-04-14 17:19:58+00:00 → 2026-05-01 22:43:23+00:00
- max gap days: 2.1
- lot p50/p95/p99/max: 4794.87 / 4871.28 / 4880.17 / 4882.76
- lot p95/p50 ratio: 1.02
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.02 / 0.17 / 1.08

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 04:00 — 54 trades
  - 17:00 — 49 trades
  - 16:00 — 42 trades
  - 18:00 — 35 trades
  - 15:00 — 34 trades

Top entry hour:5min (UTC):
  - 17:40 — 16 trades
  - 15:50 — 15 trades
  - 04:30 — 13 trades
  - 04:20 — 12 trades
  - 05:00 — 7 trades

Exit kind distribution:
  - manual_or_time: 399

Direction by pair (Buy %):
  - XAUUSD: total=399, buy_pct=59.4%

Direction by hour (Buy %, top 5 by activity):
  - hour=04: total=54, buy_pct=64.8%
  - hour=17: total=49, buy_pct=55.1%
  - hour=16: total=42, buy_pct=83.3%
  - hour=18: total=35, buy_pct=91.4%
  - hour=15: total=34, buy_pct=79.4%

## Feature extraction

- trades processed: 120
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_3_H4=1.00  \|--- ret_3_H4 <= -0.00 \|   \|--- class: 0 \|--- ret_3_H4 >  -0.00 \|... | 0.583 | 0.046 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.4167); Always-Sell = 0.5833 | 0.583 | — | 1.00 | — |
| 3 | univariate | ret_3_H1 > -0.00415 ⇒ Sell | 0.642 | — | 0.79 | 0.641 |
| 4 | univariate | range_norm_H1 > 0.5505 ⇒ Sell | 0.625 | — | 0.79 | 1.000 |
| 5 | univariate | ema_dist_20_M5 > -1.078 ⇒ Sell | 0.617 | — | 0.80 | 1.000 |
| 6 | ripper | RIPPER ruleset: [[close_vs_session_open_H4=1.0^prior_bar_sign_H1=-1.0^prior_bar_sign_M15=1.0]] | 0.523 | 0.020 | 1.00 | — |
| 7 | univariate | bb_pos_20_2_M5 > -0.3838 ⇒ Sell | 0.617 | — | 0.70 | 1.000 |
| 8 | univariate | ret_1_M1 > -8.624e-05 ⇒ Sell | 0.617 | — | 0.60 | 1.000 |
| 9 | univariate | ret_3_H4 > 0.0002507 ⇒ Buy | 0.642 | — | 0.39 | 0.641 |
| 10 | univariate | close_vs_session_open_H4 > 0 ⇒ Buy | 0.613 | — | 0.40 | 1.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_3_H4=1.00

|--- ret_3_H4 <= -0.00
|   |--- class: 0
|--- ret_3_H4 >  -0.00
|   |--- class: 1

```

### RIPPER full output (rank 6)
```
RIPPER ruleset:
[[close_vs_session_open_H4=1.0^prior_bar_sign_H1=-1.0^prior_bar_sign_M15=1.0]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
