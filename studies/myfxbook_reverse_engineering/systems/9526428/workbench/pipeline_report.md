# MyFxBook workbench — system `9526428`

Generated: 2026-05-03T22:53:31+00:00

Research-only. No paper/live, no `frozen_rules/` modification, no strategy decision.

## Selected Pattern

- Miner: `univariate`
- Candidate match_rate_cv: `0.945141065830721`
- Candidate coverage: `0.5`
- Rule text: `bb_pos_20_2_H4 > -0.3411 ⇒ Sell`
- Executor: `univariate_rank1`
- Features used: `['bb_pos_20_2_H4']`
- Entry hours UTC: `[8, 12, 16]`
- Pairs: `['AUDCAD', 'AUDCHF', 'AUDNZD', 'AUDUSD', 'EURAUD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURNZD', 'EURUSD', 'GBPUSD', 'NZDCAD', 'NZDCHF', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']`
- Max holding hours: `18.56`

## Score A — Backtest Fidelity

- Fidelity score: **0.2804** (`NONE`)
- n_real: `1437`
- n_synthetic: `13808`
- n_matched within ±5min: `44`
- entry_timing_f1: `0.0058`
- direction_acc_at_matched: `0.9773`
- count_ratio: `9.6089`
- lift_vs_baseline_pp: `-15.1`

## Score B — Decoded Strategy Efficacy

- Efficacy score: **0.0250** (`NONE`)
- synthetic trades: `13808`
- total net pips: `-14864.91`
- avg net pips/trade: `-1.0765`
- daily Sharpe: `-0.8767`
- full bootstrap 99.9% low: `-2.617`
- OOS Sharpe: `-2.7677`
- OOS bootstrap 99.9% low: `-6.7739`
- profit factor: `0.9379`
- WF positive: `2/8`
- max drawdown pips: `15805.81`

## Caveats

- auto_rule is an ephemeral candidate derived from Stage 1; it is not promoted to frozen_rules/.
- fidelity_score measures replication of public MyFxBook entries from OHLC-derived rules, not economic edge.
- efficacy_score measures the decoded synthetic stream after simple cost overlay; it is not a mandate PASS.

Method citations: candidate mining/no-lookahead `[advances_fin_ml, ch.5, ch.7]`; baseline controls `[evidence_based_ta, p.247-260]`; cost overlay `[systematic_trading, p.182-197]`; bootstrap/DSR inference `[advances_fin_ml, p.196-211]`.
