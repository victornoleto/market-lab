# ⚠️ ENGINE BIAS FORENSIC NOTICE (PARTIAL CONTAMINATION)

**Added:** 2026-04-22
**Applies to:** all files in this directory
**Fix commit:** `7b90a8f` (`fix(backtest): shift weight×return alignment to remove lookahead bias`)

---

Reports in this directory were produced by a simulator stack that
**partially** included the buggy Plano A engine. Specifically, the
L2 Gayed sleeve of the Carver risk-parity blend was computed via
`src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py:462`,
which contained a **look-ahead bias** (fixed 2026-04-22, commit
`7b90a8f`). The L1 (TSMOM) and L3 (AFML) sleeves were computed via
clean engines.

## Contamination was partial — and much smaller than initially expected

The Phase 3.5f plan §F3 item 2 guessed that the L2 sleeve carried
"66-75% of blend weight" and expected the bug to dominate L4's
reported numbers. When the honest re-run was performed, the Carver
risk-parity weight allocation (inverse-IS-volatility) actually
distributed the risk budget as:

| Sleeve | IS σ (ann.) | Implied risk weight |
|---|---:|---:|
| L1 TSMOM | ~8% | 29% |
| L2 Gayed (buggy or honest) | ~35% | **4.8%** |
| L3 AFML | ~4% | 66% |

**The L2 sleeve was only 4.8% of the blend weight, not 66-75%.** The
buggy L2 numbers therefore contributed a much smaller overstatement
to the overall L4 reported metrics than the plan assumed. The blend
was dominated by L3 (which was already CAGR-starved at ~2.5%/yr),
not by the buggy L2.

## Practical guidance

- The L4 verdict of **FAIL** is correct and was correct both under
  buggy and honest engines (the blend never had edge).
- The overstatement magnitude in this directory is smaller than in
  `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/` (where the
  same buggy engine was applied at 100% weight).
- Do not cite CAGR/Sharpe/MDD numbers in this directory as truth.
  Honest replacements are at:
  `reports/phase_3_5f/honest_revalidation/v2_l4_carver_rp/AGGREGATE.md`.

## Read also

- `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`
- `jornada/2026-04-22-engine-lookahead-bug.md`
- `jornada/2026-04-22-plano-a-honest-revalidation.md`
- `reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md`

This directory is preserved intact as a **forensic record**. It is
NOT a canonical source of truth about the V2-L4 blend's performance.
