# Decoder fingerprint — system 11355455

Generated: 2026-05-02T03:26:45

## Sanity (martingale + lot dynamics)

- n_trades: **236**, deposits: 1
- pairs: {'XAUUSD': 233, 'ARCHIV': 3}
- actions: {'Buy': 127, 'Sell': 109}
- date range: 2024-12-31 23:59:59+00:00 → 2026-04-30 11:04:37+00:00
- max gap days: 7.9
- lot p50/p95/p99/max: 3392.41 / 5122.17 / 5293.85 / 5595.01
- lot p95/p50 ratio: 1.51
- martingale flag: **PASS (no martingale)**, steps=0, max_streak=0
- hold p50/p95/max (h): 0.00 / 0.03 / 0.33

## EDA (timing / exit / direction)

Top entry hours (UTC):
  - 16:00 — 31 trades
  - 17:00 — 26 trades
  - 15:00 — 20 trades
  - 08:00 — 18 trades
  - 18:00 — 17 trades

Top entry hour:5min (UTC):
  - 16:35 — 6 trades
  - 17:00 — 6 trades
  - 16:45 — 5 trades
  - 08:45 — 5 trades
  - 15:35 — 5 trades

Exit kind distribution:
  - manual_or_time: 236

Direction by pair (Buy %):
  - ARCHIV: total=3, buy_pct=100.0%
  - XAUUSD: total=233, buy_pct=53.2%

Direction by hour (Buy %, top 5 by activity):
  - hour=16: total=31, buy_pct=45.2%
  - hour=17: total=26, buy_pct=53.8%
  - hour=15: total=20, buy_pct=55.0%
  - hour=08: total=18, buy_pct=44.4%
  - hour=18: total=17, buy_pct=58.8%

## Feature extraction

- trades processed: 233
- feature columns: 56
- skipped (no OHLC at anchor): 0
- skipped (insufficient lookback history): 0

## Top candidate direction rules

| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |
|---:|---|---|---:|---:|---:|---:|
| 1 | tree | DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.97, ret_1_M15=0.03  \|--- bb_pos_20_2_H1 <= -0.19 \|   \|--- class: ... | 0.923 | 0.029 | 1.00 | — |
| 2 | ripper | RIPPER ruleset: [[close_vs_session_open_M1=1.0^ema_dist_20_H1=>2.63] V [close_vs_session_open_M1=1.0^bb_pos_20_2_H1=0.51-0.73] ... | 0.825 | 0.036 | 1.00 | — |
| 3 | univariate | ema_dist_20_H1 > -0.2642 ⇒ Buy | 0.906 | — | 0.60 | 0.000 |
| 4 | univariate | bb_pos_20_2_H1 > -0.285 ⇒ Buy | 0.906 | — | 0.60 | 0.000 |
| 5 | univariate | ema_dist_20_H4 > -0.01851 ⇒ Buy | 0.828 | — | 0.59 | 0.000 |
| 6 | univariate | ret_10_H1 > 0.0004136 ⇒ Buy | 0.880 | — | 0.50 | 0.000 |
| 7 | univariate | ret_3_H4 > 0.0005338 ⇒ Buy | 0.845 | — | 0.50 | 0.000 |
| 8 | univariate | close_vs_session_open_H1 > -1 ⇒ Buy | 0.773 | — | 0.58 | 0.000 |
| 9 | univariate | bb_pos_20_2_H4 > 0.1478 ⇒ Buy | 0.820 | — | 0.50 | 0.000 |
| 10 | univariate | close_vs_session_open_M1 > -1 ⇒ Buy | 0.777 | — | 0.54 | 0.000 |

### TREE full output (rank 1)
```
DecisionTree(max_depth=4) — top features: bb_pos_20_2_H1=0.97, ret_1_M15=0.03

|--- bb_pos_20_2_H1 <= -0.19
|   |--- class: 0
|--- bb_pos_20_2_H1 >  -0.19
|   |--- ret_1_M15 <= 0.00
|   |   |--- class: 1
|   |--- ret_1_M15 >  0.00
|   |   |--- class: 1

```

### RIPPER full output (rank 2)
```
RIPPER ruleset:
[[close_vs_session_open_M1=1.0^ema_dist_20_H1=>2.63] V [close_vs_session_open_M1=1.0^bb_pos_20_2_H1=0.51-0.73] V [close_vs_session_open_M1=1.0^bb_pos_20_2_H1=0.73-0.96] V [close_vs_session_open_M1=1.0^ret_10_H1=0.0053-0.0071] V [bb_pos_20_2_H1=0.18-0.51] V [ret_10_H4=0.013-0.023] V [ema_dist_20_H1=2.06-2.63] V [ema_dist_20_H1=-0.2-0.23^prior_bar_sign_H4=-1.0]]
```

## Notes for Stage 2 (LLM family naming)

Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table above to identify the strategy family. Cross-check candidates with the literature: [evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`.
