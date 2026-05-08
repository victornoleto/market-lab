# Decoder fingerprint — system 10281851

Generated: 2026-05-02T02:00:29

## Sanity (martingale + lot dynamics)

- n_trades: **652**, deposits: 1
- pairs: {'XAUUSD': 652}
- actions: {'Buy': 356, 'Sell': 296}
- date range: 2023-02-14 15:32:48+00:00 → 2026-04-30 11:04:07+00:00
- max gap days: 8.3
- lot p50/p95/p99/max: 2407.18 / 4737.54 / 5188.79 / 5393.37
- lot p95/p50 ratio: 1.97
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.00 / 0.19 / 5.22

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 16:00 — 94 trades
  - 15:00 — 84 trades
  - 17:00 — 61 trades
  - 10:00 — 51 trades
  - 09:00 — 46 trades

Top entry hour:5min (UTC):
  - 15:30 — 24 trades
  - 17:00 — 17 trades
  - 16:35 — 17 trades
  - 16:45 — 16 trades
  - 15:20 — 11 trades

Exit kind distribution:
  - manual_or_time: 652

Direction by pair (Buy %):
  - XAUUSD: total=652, buy_pct=54.6%

Direction by hour (Buy %, top 5 by activity):
  - hour=16: total=94, buy_pct=55.3%
  - hour=15: total=84, buy_pct=59.5%
  - hour=17: total=61, buy_pct=47.5%
  - hour=10: total=51, buy_pct=54.9%
  - hour=09: total=46, buy_pct=67.4%

## Feature extraction

- trades processed: 652
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.74, ret_3_H1=0.18, ema_dist_20_H1=0.07, ret_10_H4=0.01  \|--- bb_pos... | 0.850 | 0.053 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_H1=1.0^ema_dist_20_H4=>2.39] V [close_vs_session_open_M15=1.0^ema_dist_20_H4=1.79-2.39]... | 0.838 | 0.052 | 1.00 | — |
| 3 | univariate | bb_pos_20_2_H1 > -0.2467 ⇒ Buy | 0.867 | — | 0.60 | 0.000 |
| 4 | univariate | ema_dist_20_H1 > -0.3093 ⇒ Buy | 0.863 | — | 0.60 | 0.000 |
| 5 | univariate | ret_10_H1 > -0.0008431 ⇒ Buy | 0.839 | — | 0.60 | 0.000 |
| 6 | univariate | ema_dist_20_H4 > -0.2166 ⇒ Buy | 0.796 | — | 0.60 | 0.000 |
| 7 | univariate | ret_3_H4 > 0.0003424 ⇒ Buy | 0.825 | — | 0.50 | 0.000 |
| 8 | univariate | ret_10_H4 > 0.0009794 ⇒ Buy | 0.816 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.08559 ⇒ Buy | 0.794 | — | 0.50 | 0.000 |
| 10 | baseline | Always-Buy (y_buy mean = 0.5460); Always-Sell = 0.4540 | 0.546 | — | 1.00 | — |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.74, ret_3_H1=0.18, ema_dist_20_H1=0.07, ret_10_H4=0.01

|--- bb_pos_20_2_H1 <= -0.24
|   |--- ret_3_H1 <= -0.00
|   |   |--- class: 0
|   |--- ret_3_H1 >  -0.00
|   |   |--- ret_3_H1 <= -0.00
|   |   |   |--- class: 0
|   |   |--- ret_3_H1 >  -0.00
|   |   |   |--- class: 0
|--- bb_pos_20_2_H1 >  -0.24
|   |--- ema_dist_20_H1 <= 0.67
|   |   |--- ret_3_H1 <= 0.00
|   |   |   |--- class: 1
|   |   |--- ret_3_H1 >  0.00
|   |   |   |--- class: 0
|   |--- ema_dist_20_H1 >  0.67
|   |   |--- ret_10_H4 <= 0.00
|   |   |   |--- class: 1
|   |   |--- ret_10_H4 >  0.00
|   |   |   |--- ret_3_H1 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_3_H1 >  0.00
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_H1=1.0^ema_dist_20_H4=>2.39] V [close_vs_session_open_M15=1.0^ema_dist_20_H4=1.79-2.39] V [close_vs_session_open_M15=1.0^ret_10_H4=0.0042-0.0074] V [close_vs_session_open_M1=1.0^bb_pos_20_2_H1=0.74-0.92^prior_bar_sign_H1=-1.0] V [close_vs_session_open_H1=1.0^prior_bar_sign_H1=-1.0^prior_bar_sign_M15=-1.0] V [ema_dist_20_H1=2.01-2.65] V [ema_dist_20_H1=1.41-2.01^ret_10_H1=0.004-0.0059] V [bb_pos_20_2_H1=0.18-0.47^prior_bar_sign_H1=-1.0] V [ema_dist_20_H4=1.17-1.79^hour_utc=<8.0] V [bb_pos_20_2_H1=-0.23-0.18^close_vs_session_open_H1=-1.0] V [ema_dist_20_H1=>2.65] V [ema_dist_20_H1=0.8-1.41^bb_pos_20_2_H4=0.39-0.65] V [ema_dist_20_H1=1.41-2.01] V [ret_10_H1=>0.0084] V [bb_pos_20_2_H1=-0.23-0.18^prior_bar_sign_H1=-1.0]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
