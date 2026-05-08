# Decoder fingerprint — system 10734338

Generated: 2026-05-02T02:44:32

## Sanity (martingale + lot dynamics)

- n_trades: **591**, deposits: 1
- pairs: {'BTCUSD': 591}
- actions: {'Buy': 317, 'Sell': 274}
- date range: 2024-01-26 11:42:12+00:00 → 2026-05-01 15:33:53+00:00
- max gap days: 6.5
- lot p50/p95/p99/max: 84407.66 / 116251.50 / 120927.35 / 125785.00
- lot p95/p50 ratio: 1.38
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.01 / 0.26 / 2.04

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 17:00 — 91 trades
  - 16:00 — 86 trades
  - 18:00 — 44 trades
  - 15:00 — 42 trades
  - 10:00 — 41 trades

Top entry hour:5min (UTC):
  - 16:40 — 17 trades
  - 15:30 — 15 trades
  - 16:45 — 14 trades
  - 17:10 — 13 trades
  - 16:50 — 11 trades

Exit kind distribution:
  - manual_or_time: 591

Direction by pair (Buy %):
  - BTCUSD: total=591, buy_pct=53.6%

Direction by hour (Buy %, top 5 by activity):
  - hour=17: total=91, buy_pct=50.5%
  - hour=16: total=86, buy_pct=50.0%
  - hour=18: total=44, buy_pct=47.7%
  - hour=15: total=42, buy_pct=59.5%
  - hour=10: total=41, buy_pct=53.7%

## Feature extraction

- trades processed: 591
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.85, ema_dist_20_H1=0.11, range_norm_H4=0.03, ema_dist_20_H4=0.01, re... | 0.860 | 0.023 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M5=1.0^ret_10_H1=0.016-0.027] V [close_vs_session_open_M1=1.0^ret_10_H1=>0.027] V [clos... | 0.837 | 0.027 | 1.00 | — |
| 3 | univariate | ret_10_H1 > -0.004215 ⇒ Buy | 0.853 | — | 0.60 | 0.000 |
| 4 | univariate | bb_pos_20_2_H4 > -0.1852 ⇒ Buy | 0.839 | — | 0.60 | 0.000 |
| 5 | univariate | ema_dist_20_H4 > -0.2796 ⇒ Buy | 0.836 | — | 0.60 | 0.000 |
| 6 | univariate | bb_pos_20_2_H1 > 0.1203 ⇒ Buy | 0.868 | — | 0.50 | 0.000 |
| 7 | univariate | ema_dist_20_H1 > 0.301 ⇒ Buy | 0.861 | — | 0.50 | 0.000 |
| 8 | univariate | ret_10_H4 > 0.002441 ⇒ Buy | 0.810 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_M15 > -0.144 ⇒ Buy | 0.738 | — | 0.60 | 0.000 |
| 10 | univariate | ret_3_H4 > 0.001415 ⇒ Buy | 0.807 | — | 0.50 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.85, ema_dist_20_H1=0.11, range_norm_H4=0.03, ema_dist_20_H4=0.01, ret_1_M15=0.00

|--- bb_pos_20_2_H1 <= -0.29
|   |--- range_norm_H4 <= 1.91
|   |   |--- ema_dist_20_H4 <= -0.37
|   |   |   |--- class: 0
|   |   |--- ema_dist_20_H4 >  -0.37
|   |   |   |--- class: 0
|   |--- range_norm_H4 >  1.91
|   |   |--- class: 0
|--- bb_pos_20_2_H1 >  -0.29
|   |--- ema_dist_20_H1 <= 0.55
|   |   |--- class: 1
|   |--- ema_dist_20_H1 >  0.55
|   |   |--- ema_dist_20_H1 <= 1.12
|   |   |   |--- class: 1
|   |   |--- ema_dist_20_H1 >  1.12
|   |   |   |--- ret_1_M15 <= 0.00
|   |   |   |   |--- class: 1
|   |   |   |--- ret_1_M15 >  0.00
|   |   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M5=1.0^ret_10_H1=0.016-0.027] V [close_vs_session_open_M1=1.0^ret_10_H1=>0.027] V [close_vs_session_open_M5=1.0^ret_10_H1=0.01-0.016^prior_bar_sign_M1=-1.0] V [close_vs_session_open_M5=1.0^ret_10_H1=0.01-0.016] V [ema_dist_20_H1=0.77-1.29] V [ret_10_H1=0.00077-0.005^prior_bar_sign_H4=-1.0] V [ema_dist_20_H1=0.31-0.77^prior_bar_sign_H1=-1.0] V [ema_dist_20_H1=-0.45-0.31^prior_bar_sign_H1=-1.0] V [ret_3_H4=0.01-0.017] V [ema_dist_20_H4=1.04-1.55] V [ema_dist_20_H4=0.11-0.57^prior_bar_sign_H4=-1.0] V [ema_dist_20_H1=1.29-1.73] V [ema_dist_20_H4=>2.13] V [ema_dist_20_H4=1.55-2.13]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
