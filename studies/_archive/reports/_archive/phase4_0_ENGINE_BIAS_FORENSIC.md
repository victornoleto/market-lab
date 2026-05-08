# ⚠️ ENGINE BIAS FORENSIC NOTICE

**Added:** 2026-04-22
**Applies to:** all files in this directory (specifically
`index_cfd_validation/`)
**Fix commit:** `7b90a8f` (`fix(backtest): shift weight×return alignment to remove lookahead bias`)

---

Reports in this directory were produced by a version of the simulation
engine that contained a **look-ahead bias** (fixed 2026-04-22, commit
`7b90a8f`). The Phase 4.0 Index CFD validation re-ran the V2-L2 Gayed
winner against SPX TR + QQQ adj_close + GLD adj_close using the
Pepperstone Index CFD cost model (commission=0, spread=5bps half,
swap=−0.008%). Because it reused the same engine
(`src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py:462`)
with the bug at `new_w[bar_i] × ret[bar_i]`, the reported Index CFD
improvements (OOS Sharpe 2.400, CAGR 85.76%, MDD −21.51%) are
**inflated by the same look-ahead mechanism**.

**Reported CAGR/Sharpe values in this directory OVERSTATE the honest
strategy performance.** The Phase 4.0 Index CFD story (10/10 gates
PASS, $1k threshold unlocked) does NOT survive the honest engine.

## What this means operationally

- The $1k threshold decision based on these numbers must be
  re-evaluated. The **commission-zero Razor Index** finding (204 bps
  cumulative savings) is still factually correct — that was derived
  from the cTrader rate-card pull, not from the buggy simulator.
  What is NOT correct is the claim that the strategy produces
  Sharpe 2.4 / CAGR 85% under Index CFD costs.
- Under the honest engine, V2-L2 Gayed (regardless of share CFD vs
  Index CFD pricing) fails the 13-gate winner definition. See
  `reports/phase_3_5f/honest_revalidation/v2_l2_gayed_cfd/AGGREGATE.md`.
- The live threading model and cost-model infrastructure built in
  Phase 4.0 (cTrader Open API integration, rate-card puller, lot
  minimums analysis) remains valid and reusable — it was not
  affected by the bug.

## Read also

- `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`
- `jornada/2026-04-22-engine-lookahead-bug.md`
- `jornada/2026-04-22-plano-a-honest-revalidation.md`
- `reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md`
- `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md`

This directory is preserved intact as a **forensic record** of how
the bias manifested in the Index CFD validation context. It is NOT
a canonical source of truth about V2-L2's Index CFD performance.
