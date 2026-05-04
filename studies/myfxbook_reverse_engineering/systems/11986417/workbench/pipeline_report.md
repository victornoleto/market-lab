# MyFxBook workbench — system `11986417`

Generated: 2026-05-04T00:32:22+00:00

Research-only. No paper/live, no `frozen_rules/` modification, no strategy decision.

## Selected Pattern

- Miner: `tree`
- Candidate match_rate_cv: `0.5833333333333333`
- Candidate coverage: `1.0`
- Rule text: `DecisionTree(max_depth=4) — top features: ret_3_H4=1.00`
- Executor: `tree_rank1`
- Features used: `['ret_3_H4']`
- Entry hours UTC: `[9, 15, 18]`
- Pairs: `['XAUUSD']`
- Max holding hours: `1.00`

## Score A — Backtest Fidelity

- Fidelity score: **0.1481** (`NONE`)
- n_real: `4899`
- n_synthetic: `186`
- n_matched within ±5min: `39`
- entry_timing_f1: `0.0153`
- direction_acc_at_matched: `0.5897`
- count_ratio: `0.038`
- lift_vs_baseline_pp: `-2.16`

## Score B — Decoded Strategy Efficacy

- Efficacy score: **0.0250** (`NONE`)
- synthetic trades: `186`
- total net pips: `-14448.9`
- avg net pips/trade: `-77.6823`
- daily Sharpe: `-1.2617`
- full bootstrap 99.9% low: `-7.7488`
- OOS Sharpe: `-0.0613`
- OOS bootstrap 99.9% low: `None`
- profit factor: `0.8812`
- WF positive: `2/8`
- max drawdown pips: `26961.4`

## Caveats

- auto_rule is an ephemeral candidate derived from Stage 1; it is not promoted to frozen_rules/.
- fidelity_score measures replication of public MyFxBook entries from OHLC-derived rules, not economic edge.
- efficacy_score measures the decoded synthetic stream after simple cost overlay; it is not a mandate PASS.

Method citations: candidate mining/no-lookahead `[advances_fin_ml, ch.5, ch.7]`; baseline controls `[evidence_based_ta, p.247-260]`; cost overlay `[systematic_trading, p.182-197]`; bootstrap/DSR inference `[advances_fin_ml, p.196-211]`.
