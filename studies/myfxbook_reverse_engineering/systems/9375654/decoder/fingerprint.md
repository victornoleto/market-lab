# Decoder fingerprint — system 9375654

Generated: 2026-05-02T10:25:06

## Sanity (martingale + lot dynamics)

- n_trades: **915**, deposits: 21
- pairs: {'XAUUSD': 915}
- actions: {'Buy': 485, 'Sell': 430}
- date range: 2021-11-22 08:51:45+00:00 → 2026-04-30 11:04:07+00:00
- max gap days: 8.3
- lot p50/p95/p99/max: 2020.30 / 4603.91 / 5145.58 / 5393.58
- lot p95/p50 ratio: 2.28
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.00 / 0.11 / 2.14

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 15:00 — 126 trades
  - 16:00 — 123 trades
  - 17:00 — 86 trades
  - 10:00 — 72 trades
  - 09:00 — 63 trades

Top entry hour:5min (UTC):
  - 15:30 — 42 trades
  - 16:35 — 23 trades
  - 17:00 — 22 trades
  - 16:45 — 21 trades
  - 16:30 — 15 trades

Exit kind distribution:
  - manual_or_time: 915

Direction by pair (Buy %):
  - XAUUSD: total=915, buy_pct=53.0%

Direction by hour (Buy %, top 5 by activity):
  - hour=15: total=126, buy_pct=57.9%
  - hour=16: total=123, buy_pct=57.7%
  - hour=17: total=86, buy_pct=47.7%
  - hour=10: total=72, buy_pct=50.0%
  - hour=11: total=63, buy_pct=44.4%

## Feature extraction

- trades processed: 915
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.75, ret_3_H1=0.13, ema_dist_20_H1=0.06, ret_10_H1=0.05, ema_dist_20_... | 0.867 | 0.040 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M15=1.0^ret_10_H1=>0.0084] V [close_vs_session_open_H1=1.0^ret_10_H1=0.0058-0.0084^bb_p... | 0.825 | 0.039 | 1.00 | — |
| 3 | univariate | ret_10_H1 > -0.00125 ⇒ Buy | 0.827 | — | 0.60 | 0.000 |
| 4 | univariate | bb_pos_20_2_H1 > 0.1209 ⇒ Buy | 0.860 | — | 0.50 | 0.000 |
| 5 | univariate | ema_dist_20_H1 > 0.2216 ⇒ Buy | 0.851 | — | 0.50 | 0.000 |
| 6 | univariate | ret_3_H4 > 0.0002302 ⇒ Buy | 0.816 | — | 0.50 | 0.000 |
| 7 | univariate | ret_10_H4 > 0.000986 ⇒ Buy | 0.812 | — | 0.50 | 0.000 |
| 8 | univariate | ema_dist_20_H4 > 0.2346 ⇒ Buy | 0.805 | — | 0.50 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.0973 ⇒ Buy | 0.805 | — | 0.50 | 0.000 |
| 10 | univariate | close_vs_session_open_H1 > -1 ⇒ Buy | 0.718 | — | 0.55 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.75, ret_3_H1=0.13, ema_dist_20_H1=0.06, ret_10_H1=0.05, ema_dist_20_M5=0.01

|--- bb_pos_20_2_H1 <= -0.16
|   |--- ret_3_H1 <= -0.00
|   |   |--- ret_10_H1 <= -0.01
|   |   |   |--- class: 0
|   |   |--- ret_10_H1 >  -0.01
|   |   |   |--- class: 1
|   |--- ret_3_H1 >  -0.00
|   |   |--- ret_10_H1 <= -0.00
|   |   |   |--- ret_3_M15 <= 0.00
|   |   |   |   |--- class: 0
|   |   |   |--- ret_3_M15 >  0.00
|   |   |   |   |--- class: 0
|   |   |--- ret_10_H1 >  -0.00
|   |   |   |--- class: 0
|--- bb_pos_20_2_H1 >  -0.16
|   |--- ema_dist_20_H1 <= 0.63
|   |   |--- ret_3_H1 <= -0.00
|   |   |   |--- class: 1
|   |   |--- ret_3_H1 >  -0.00
|   |   |   |--- class: 0
|   |--- ema_dist_20_H1 >  0.63
|   |   |--- ret_3_H1 <= 0.01
|   |   |   |--- ema_dist_20_M5 <= 1.63
|   |   |   |   |--- class: 1
|   |   |   |--- ema_dist_20_M5 >  1.63
|   |   |   |   |--- class: 1
|   |   |--- ret_3_H1 >  0.01
|   |   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M15=1.0^ret_10_H1=>0.0084] V [close_vs_session_open_H1=1.0^ret_10_H1=0.0058-0.0084^bb_pos_20_2_H1=0.93-1.09] V [close_vs_session_open_M1=1.0^ret_3_H4=0.0039-0.006] V [close_vs_session_open_M1=1.0^ret_3_H4=0.0021-0.0039^prior_bar_sign_M15=-1.0] V [close_vs_session_open_M5=1.0^ret_3_H4=0.006-0.01^ema_dist_20_H1=1.9-2.54] V [close_vs_session_open_M15=1.0^ret_10_H1=0.0017-0.0038^prior_bar_sign_H1=-1.0] V [close_vs_session_open_H1=1.0^ema_dist_20_H4=>2.25] V [bb_pos_20_2_H1=0.12-0.45^close_vs_session_open_H1=-1.0] V [close_vs_session_open_H1=1.0^ema_dist_20_H4=1.14-1.73] V [bb_pos_20_2_H1=0.45-0.73^prior_bar_sign_H1=-1.0] V [hour_utc=13.0-15.0^bb_pos_20_2_H1=-0.29-0.12^close_vs_session_open_H4=-1.0] V [close_vs_session_open_H4=1.0^ema_dist_20_H1=0.75-1.32] V [ema_dist_20_H4=1.73-2.25^close_vs_session_open_M1=-1.0] V [bb_pos_20_2_H4=0.64-0.83] V [ema_dist_20_M15=1.35-1.85^ema_dist_20_M5=0.75-1.12] V [bb_pos_20_2_H4=0.83-1.05] V [ret_10_M5=-0.0022--0.0012^range_norm_H4=>2.26] V [ema_dist_20_H4=-0.68--0.27^range_norm_H4=1.46-1.72]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
