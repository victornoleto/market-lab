# ⚠️ ENGINE BIAS FORENSIC NOTICE

**Added:** 2026-04-22
**Applies to:** all files in this directory
**Fix commit:** `7b90a8f` (`fix(backtest): shift weight×return alignment to remove lookahead bias`)

---

Reports in this directory were produced by a version of the simulation
engine that contained a **look-ahead bias** (fixed 2026-04-22, commit
`7b90a8f`). The engine used `new_w[bar_i] × ret[bar_i]` instead of the
correct `prev_w[bar_i] × ret[bar_i]` in the return compounding line of
`src/market_lab/backtest/strategies/plano_a_leveraged_rotation.py:462`.
Because the regime signal at bar `i` was computed from `close[i]` and
the return at bar `i` was also computed from `close[i]`, the simulator
effectively got to see the day's close before sizing into it.

**Reported CAGR/Sharpe values in this directory OVERSTATE the honest
strategy performance.** Specifically:

| Metric (OOS 2018-2023) | As-reported here (buggy) | Honest (post-fix) |
|---|---:|---:|
| Sharpe | 2.284 | ~0.56 |
| CAGR | 79.14% | 12.58% (raw) / 14.29% (adj) |
| MaxDD | −21.02% | ~−37% |

**Do not cite these numbers as truth.**

For context and honest re-validation, see:

- `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`
- `jornada/2026-04-22-engine-lookahead-bug.md`
- `reports/phase_3_5f/honest_revalidation/v2_l2_gayed_cfd/AGGREGATE.md`
- `reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md`

This directory is preserved intact as a **forensic record** of how
the bias manifested. It is NOT a canonical source of truth about the
V2-L2 strategy's performance.
