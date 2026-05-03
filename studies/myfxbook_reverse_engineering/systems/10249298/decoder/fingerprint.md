# Decoder fingerprint — system 10249298

Generated: 2026-05-02T01:42:01

## Sanity (martingale + lot dynamics)

- n_trades: **280**, deposits: 2
- pairs: {'EURUSD': 280}
- actions: {'Buy': 152, 'Sell': 128}
- date range: 2022-04-19 15:08:05+00:00 → 2026-04-29 21:45:21+00:00
- max gap days: 57.4
- lot p50/p95/p99/max: 1.08 / 1.17 / 1.19 / 1.20
- lot p95/p50 ratio: 1.08
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 130.51 / 1460.70 / 2835.51

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 20:00 — 80 trades
  - 16:00 — 60 trades
  - 12:00 — 53 trades
  - 00:00 — 40 trades
  - 04:00 — 26 trades

Top entry hour:5min (UTC):
  - 20:00 — 80 trades
  - 16:00 — 60 trades
  - 12:00 — 53 trades
  - 00:00 — 40 trades
  - 04:00 — 26 trades

Exit kind distribution:
  - manual_or_time: 280

Direction by pair (Buy %):
  - EURUSD: total=280, buy_pct=54.3%

Direction by hour (Buy %, top 5 by activity):
  - hour=20: total=80, buy_pct=62.5%
  - hour=16: total=60, buy_pct=50.0%
  - hour=12: total=53, buy_pct=54.7%
  - hour=00: total=40, buy_pct=57.5%
  - hour=04: total=26, buy_pct=42.3%

## Feature extraction

- trades processed: 280
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: ret_10_H1=0.54, atr_ratio_M1=0.25, ema_dist_20_H1=0.21  \|--- ret_10_H1 <= 0.00 \|   ... | 0.596 | 0.112 | 1.00 | — |
| 2 | baseline | Always-Buy (y_buy mean = 0.5429); Always-Sell = 0.4571 | 0.543 | — | 1.00 | — |
| 3 | univariate | ema_dist_20_H1 > -1.755 ⇒ Buy | 0.593 | — | 0.80 | 0.580 |
| 4 | univariate | ret_1_H4 > -0.001375 ⇒ Buy | 0.593 | — | 0.80 | 0.580 |
| 5 | ripper | RIPPER ruleset: [[close_vs_session_open_H4=1.0^prior_bar_sign_H4=1.0^ret_1_M1=2.6e-05-5.5e-05] V [dow=0^ret_1_M5=>0.00043] V [r... | 0.521 | 0.121 | 1.00 | — |
| 6 | univariate | ret_10_H4 > -0.009079 ⇒ Buy | 0.579 | — | 0.80 | 1.000 |
| 7 | univariate | ema_dist_20_H4 > -1.527 ⇒ Buy | 0.607 | — | 0.70 | 0.104 |
| 8 | univariate | bb_pos_20_2_H4 > -0.7492 ⇒ Buy | 0.607 | — | 0.70 | 0.104 |
| 9 | univariate | ret_3_H4 > -0.001013 ⇒ Buy | 0.636 | — | 0.60 | 0.002 |
| 10 | univariate | bb_pos_20_2_H1 > -0.2312 ⇒ Buy | 0.600 | — | 0.60 | 0.252 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: ret_10_H1=0.54, atr_ratio_M1=0.25, ema_dist_20_H1=0.21

|--- ret_10_H1 <= 0.00
|   |--- atr_ratio_M1 <= 0.08
|   |   |--- class: 1
|   |--- atr_ratio_M1 >  0.08
|   |   |--- class: 0
|--- ret_10_H1 >  0.00
|   |--- ema_dist_20_H1 <= 1.45
|   |   |--- class: 1
|   |--- ema_dist_20_H1 >  1.45
|   |   |--- class: 1

```

### RIPPER full output (rank 5)
```
RIPPER ruleset:
[[close_vs_session_open_H4=1.0^prior_bar_sign_H4=1.0^ret_1_M1=2.6e-05-5.5e-05] V [dow=0^ret_1_M5=>0.00043] V [ret_3_H4=0.0022-0.0038^ret_10_H1=0.0024-0.0035]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
