# MyFxBook workbench — system `1407880`

Generated: 2026-05-03T21:55:54+00:00

Research-only. No paper/live, no `frozen_rules/` modification, no strategy decision.

## Selected Pattern

- Miner: `tree`
- Candidate match_rate_cv: `0.64`
- Candidate coverage: `1.0`
- Rule text: `DecisionTree(max_depth=4) — top features: bb_pos_20_2_M15=0.62, bb_pos_20_2_M5=0.26, range_norm_H1=0.12`
- Executor: `tree_rank1`
- Features used: `['bb_pos_20_2_M15', 'bb_pos_20_2_M5', 'range_norm_H1']`
- Entry hours UTC: `[0, 1, 23]`
- Pairs: `['EURCHF', 'EURGBP', 'EURUSD', 'GBPUSD', 'USDCAD', 'USDCHF']`
- Max holding hours: `2.06`

## Score A — Backtest Fidelity

- Fidelity score: **0.2249** (`NONE`)
- n_real: `3304`
- n_synthetic: `24720`
- n_matched within ±5min: `549`
- entry_timing_f1: `0.0392`
- direction_acc_at_matched: `0.7158`
- count_ratio: `7.4818`
- lift_vs_baseline_pp: `-43.49`

## Score B — Decoded Strategy Efficacy

- Efficacy score: **0.0000** (`NONE`)
- synthetic trades: `24720`
- total net pips: `-28962.46`
- avg net pips/trade: `-1.1716`
- daily Sharpe: `-4.5965`
- full bootstrap 99.9% low: `-6.5404`
- OOS Sharpe: `-4.6757`
- OOS bootstrap 99.9% low: `-7.1777`
- profit factor: `0.7047`
- WF positive: `0/8`
- max drawdown pips: `28961.36`

## Caveats

- auto_rule is an ephemeral candidate derived from Stage 1; it is not promoted to frozen_rules/.
- fidelity_score measures replication of public MyFxBook entries from OHLC-derived rules, not economic edge.
- efficacy_score measures the decoded synthetic stream after simple cost overlay; it is not a mandate PASS.

Method citations: candidate mining/no-lookahead `[advances_fin_ml, ch.5, ch.7]`; baseline controls `[evidence_based_ta, p.247-260]`; cost overlay `[systematic_trading, p.182-197]`; bootstrap/DSR inference `[advances_fin_ml, p.196-211]`.
