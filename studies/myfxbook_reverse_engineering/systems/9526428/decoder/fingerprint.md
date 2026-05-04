# Decoder fingerprint — system 9526428

Generated: 2026-05-03T19:46:33

## Sanity (martingale + lot dynamics)

- n_trades: **1437**, deposits: 7
- pairs: {'USDJPY': 178, 'EURJPY': 142, 'NZDJPY': 108, 'EURNZD': 107, 'GBPUSD': 107, 'USDCAD': 100, 'EURUSD': 93, 'EURAUD': 91, 'NZDUSD': 80, 'EURCHF': 64, 'AUDUSD': 59, 'AUDNZD': 59, 'NZDCAD': 54, 'AUDCAD': 49, 'AUDCHF': 48, 'NZDCHF': 46, 'EURGBP': 40, 'USDCHF': 12}
- actions: {'Buy': 773, 'Sell': 664}
- date range: 2022-02-02 18:30:30+00:00 → 2026-04-19 21:32:25+00:00
- max gap days: 43.9
- lot p50/p95/p99/max: nan / nan / nan / nan
- lot p95/p50 ratio: inf
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 2.12 / 135.04 / 1716.23

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 16:00 — 184 trades
  - 12:00 — 124 trades
  - 08:00 — 108 trades
  - 14:00 — 95 trades
  - 15:00 — 80 trades

Top entry hour:5min (UTC):
  - 16:00 — 115 trades
  - 12:00 — 67 trades
  - 08:00 — 59 trades
  - 20:00 — 52 trades
  - 04:00 — 48 trades

Exit kind distribution:
  - manual_or_time: 1437

Direction by pair (Buy %):
  - AUDCAD: total=49, buy_pct=55.1%
  - AUDCHF: total=48, buy_pct=41.7%
  - AUDNZD: total=59, buy_pct=59.3%
  - AUDUSD: total=59, buy_pct=47.5%
  - EURAUD: total=91, buy_pct=46.2%
  - EURCHF: total=64, buy_pct=32.8%
  - EURGBP: total=40, buy_pct=52.5%
  - EURJPY: total=142, buy_pct=66.2%
  - EURNZD: total=107, buy_pct=56.1%
  - EURUSD: total=93, buy_pct=55.9%
  - GBPUSD: total=107, buy_pct=51.4%
  - NZDCAD: total=54, buy_pct=53.7%
  - NZDCHF: total=46, buy_pct=32.6%
  - NZDJPY: total=108, buy_pct=63.9%
  - NZDUSD: total=80, buy_pct=31.2%
  - USDCAD: total=100, buy_pct=44.0%
  - USDCHF: total=12, buy_pct=75.0%
  - USDJPY: total=178, buy_pct=71.3%

Direction by hour (Buy %, top 5 by activity):
  - hour=16: total=184, buy_pct=62.5%
  - hour=12: total=124, buy_pct=51.6%
  - hour=08: total=108, buy_pct=56.5%
  - hour=14: total=95, buy_pct=46.3%
  - hour=15: total=80, buy_pct=57.5%

## Feature extraction

- trades processed: 1276
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | ripper | RIPPER ruleset: [[prior_bar_sign_H1=1.0^is_first_5min_of_hour=0^prior_bar_sign_H4=1.0^bb_pos_20_2_H4=-0.59--0.35] V [prior_bar_... | 0.972 | 0.010 | 1.00 | — |
| 2 | tree | DecisionTree(max_depth=4) — top features: ret_10_H4=0.94, range_norm_H4=0.04, ret_3_M15=0.01, bb_pos_20_2_H4=0.00, is_first_min... | 0.940 | 0.032 | 1.00 | — |
| 3 | univariate | bb_pos_20_2_H4 > -0.3411 ⇒ Sell | 0.945 | — | 0.50 | 0.000 |
| 4 | univariate | ret_10_H4 > -0.001614 ⇒ Sell | 0.940 | — | 0.50 | 0.000 |
| 5 | univariate | ema_dist_20_H4 > -0.6115 ⇒ Sell | 0.940 | — | 0.50 | 0.000 |
| 6 | univariate | ema_dist_20_H1 > -0.2343 ⇒ Sell | 0.765 | — | 0.50 | 0.000 |
| 7 | univariate | bb_pos_20_2_M5 > -0.4246 ⇒ Buy | 0.699 | — | 0.59 | 0.000 |
| 8 | baseline | Always-Buy (y_buy mean = 0.5361); Always-Sell = 0.4639 | 0.536 | — | 1.00 | — |
| 9 | univariate | ret_3_H4 > -0.0005609 ⇒ Sell | 0.749 | — | 0.50 | 0.000 |
| 10 | univariate | ret_3_M15 > -1.179e-05 ⇒ Buy | 0.704 | — | 0.50 | 0.000 |

### RIPPER full output (rank 1)
```
RIPPER ruleset:
[[prior_bar_sign_H1=1.0^is_first_5min_of_hour=0^prior_bar_sign_H4=1.0^bb_pos_20_2_H4=-0.59--0.35] V [prior_bar_sign_H1=1.0^bb_pos_20_2_H4=-0.75--0.59] V [bb_pos_20_2_H4=<-1.15] V [bb_pos_20_2_H4=-1.15--0.93] V [bb_pos_20_2_H4=-0.93--0.75^prior_bar_sign_H1=1.0] V [bb_pos_20_2_H4=-0.93--0.75] V [prior_bar_sign_H4=1.0^ema_dist_20_H4=-1.23--0.63] V [prior_bar_sign_H4=1.0^ema_dist_20_H4=-0.63-0.7] V [ema_dist_20_H4=-1.74--1.23] V [bb_pos_20_2_H4=-0.75--0.59] V [ret_1_H4=>0.0045^ema_dist_20_M5=>2.67^dow=1] V [ema_dist_20_H4=-2.07--1.74] V [ret_10_M5=>0.0023^atr_ratio_H4=1.57-1.69^is_first_min_of_hour=0]]
```

### TREE full output (rank 2)
```
DecisionTree(max_depth=4) — top features: ret_10_H4=0.94, range_norm_H4=0.04, ret_3_M15=0.01, bb_pos_20_2_H4=0.00, is_first_min_of_hour=0.00

|--- ret_10_H4 <= 0.00
|   |--- range_norm_H4 <= 2.64
|   |   |--- bb_pos_20_2_H4 <= -0.39
|   |   |   |--- class: 1
|   |   |--- bb_pos_20_2_H4 >  -0.39
|   |   |   |--- class: 1
|   |--- range_norm_H4 >  2.64
|   |   |--- class: 1
|--- ret_10_H4 >  0.00
|   |--- ret_3_M15 <= 0.00
|   |   |--- ret_10_M5 <= -0.00
|   |   |   |--- class: 0
|   |   |--- ret_10_M5 >  -0.00
|   |   |   |--- is_first_min_of_hour <= 0.50
|   |   |   |   |--- class: 0
|   |   |   |--- is_first_min_of_hour >  0.50
|   |   |   |   |--- class: 0
|   |--- ret_3_M15 >  0.00
|   |   |--- class: 0

```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
