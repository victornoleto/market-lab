# MyFxBook workbench — system `11305553`

Generated: 2026-05-03T22:14:35+00:00

Research-only. No paper/live, no `frozen_rules/` modification, no strategy decision.

## Selected Pattern

- Miner: `univariate`
- Candidate match_rate_cv: `0.7462039045553145`
- Candidate coverage: `0.8459869848156182`
- Rule text: `dow > 0 ⇒ Buy`
- Executor: `univariate_rank1`
- Features used: `['dow']`
- Entry hours UTC: `[9, 15, 17]`
- Pairs: `['AUDCAD', 'AUDNZD', 'NZDCAD']`
- Max holding hours: `51.00`

## Score A — Backtest Fidelity

- Fidelity score: **0.3009** (`NONE`)
- n_real: `575`
- n_synthetic: `262`
- n_matched within ±5min: `1`
- entry_timing_f1: `0.0024`
- direction_acc_at_matched: `1.0`
- count_ratio: `0.4557`
- lift_vs_baseline_pp: `-16.0`

## Score B — Decoded Strategy Efficacy

- Efficacy score: **0.0125** (`NONE`)
- synthetic trades: `262`
- total net pips: `-3321.8`
- avg net pips/trade: `-12.6786`
- daily Sharpe: `-4.4525`
- full bootstrap 99.9% low: `-8.0987`
- OOS Sharpe: `-9.4659`
- OOS bootstrap 99.9% low: `None`
- profit factor: `0.4964`
- WF positive: `1/8`
- max drawdown pips: `3718.3`

## Caveats

- auto_rule is an ephemeral candidate derived from Stage 1; it is not promoted to frozen_rules/.
- fidelity_score measures replication of public MyFxBook entries from OHLC-derived rules, not economic edge.
- efficacy_score measures the decoded synthetic stream after simple cost overlay; it is not a mandate PASS.

Method citations: candidate mining/no-lookahead `[advances_fin_ml, ch.5, ch.7]`; baseline controls `[evidence_based_ta, p.247-260]`; cost overlay `[systematic_trading, p.182-197]`; bootstrap/DSR inference `[advances_fin_ml, p.196-211]`.
