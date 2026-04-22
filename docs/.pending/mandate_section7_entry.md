# DRAFT — pending user review

**Target file:** `docs/investment-mandate.md` §7 (Decision History)
**Status:** NOT YET MERGED. This is a staged entry awaiting user
approval of the Phase 3.5f outcome and the chosen next-step option
(A/B/C/D — see `jornada/2026-04-23-0700-overnight-summary.md §6`).

Merge instructions: once the user selects an option, append the row
below to the `§7 Decision History` table in `docs/investment-mandate.md`.
Replace `<verdict>` with the verdict chosen and `<commit hash>` with
the F4-closing commit hash.

---

## Draft row to insert

| Date | Decision | Rationale | Citation | Commit |
|---|---|---|---|---|
| 2026-04-22 | **Engine look-ahead bias discovered and fixed.** `plano_a_leveraged_rotation.py:462` was doing `new_w[bar_i] × ret[bar_i]` instead of `prev_w[bar_i] × ret[bar_i]`. Three independent libraries (bt, vectorbt, backtrader) + numpy reference all agreed on the shift convention; canonical engine was alone. Shift applied in commit `7b90a8f`. Surgical tests (4) in `tests/test_plano_a_lookahead_bias.py`. Scope audit in `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md` confirmed the bug was isolated to **one file, one line** — `letf_rotation.py` (Plano B) and all other V2 engines were clean. V2-L2 Gayed **rejected** under honest engine (honest OOS Sharpe 0.56 / CAGR 14% / MDD −37% vs baseline 2.28 / 79% / −21%). All 6 Plano A V2 leads FAIL honest gates. Phase 3.5b/3.5c/3.5d/3.5e Plano B reports **preserved as clean canonical** (engines never touched the bug). Reports `phase3_5a_v2/v2_l2_*` + `phase3_5a_v2/v2_l4_*` (partial, 4.8% weight) + `phase4_0/*` marked with `ENGINE_BIAS_FORENSIC.md` banners. **Plano A: no honest winner. User decision: <A = design V3 / B = Gayed 1× fallback / C = abandon per `project_plano_a_v2_last_attempt` / D = freeze Plano A, resume Plano B c06-c12>.** | Look-ahead convention enforcement + cross-lib independent replication. `[advances_fin_ml, p.31-34]` | `<commit hash of F4 closing commit>` |

---

## Notes for the merge operation

1. The V2-L2 header banner (`docs/.pending/plano_a_v2_l2_gayed_cfd_banner.md`)
   should be merged in the same commit as this §7 entry, so the mandate
   row and the strategy doc tell the same story.
2. The row text above is deliberately dense (one cell, multiple
   sentences) to match the existing §7 format. If future agents find
   this hard to scan, extract detail into a dedicated subsection
   below §7 and leave a short pointer in the table row.
3. If the user selects Option A (V3) or D (Plano B resume), the
   mandate may also need a new §3 entry capturing the revised strategy
   allocation. That would be a separate follow-up.

---

## Citations

- `[advances_fin_ml, p.31-34]` — look-ahead bias detection and
  two-stage replication protocol (the canonical reference for the
  bug class).
- Mandate §2.5 (zero bypass) — why we do not soft-gate the 6 failing
  leads through.
- Mandate §4.7 (abandonment allocation rule) — relevant if Option C
  is selected.
