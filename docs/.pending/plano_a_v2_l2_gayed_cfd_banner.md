# DRAFT — pending user review

**Target file:** `docs/strategies/plano_a_v2_l2_gayed_cfd.md`
**Status:** NOT YET MERGED. This is a staged banner awaiting user
approval of the Phase 3.5f outcome.

Merge instructions: insert the banner block below at the **top** of
the target file (just under the H1 title, above any existing
frontmatter or body text). The existing body of the strategy doc
should be preserved as `§9 Historical (buggy-engine) record` per
mandate traceability.

---

## Draft banner block

```markdown
> # ⚠️ REJECTED — look-ahead bias in prior engine
>
> **Status update 2026-04-22:** this strategy has been **re-classified
> from "winner" to "rejected"** under the honest simulation engine.
>
> **What changed.** On 2026-04-22 a look-ahead bias was found in the
> Plano A engine (`src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py:462`),
> where the weight×return alignment was `new_w[bar_i] × ret[bar_i]`
> instead of the correct `prev_w[bar_i] × ret[bar_i]`. The bug gave
> the simulator perfect foresight of each day's close before sizing
> into it. Fix shipped in commit `7b90a8f`; 4 surgical tests in
> `tests/test_plano_a_lookahead_bias.py` discriminate the buggy vs
> honest convention by hand-verifiable numbers. `[advances_fin_ml, p.31-34]`
>
> **Impact on this strategy (honest numbers, OOS 2018-2023):**
>
> | Metric | Buggy (as-published) | Honest (post-fix) |
> |---|---:|---:|
> | Sharpe OOS | 2.284 | ~0.56 |
> | CAGR OOS | 79.14% | 12.58% (raw close) / 14.29% (adj close TR) |
> | MaxDD OOS | −21.02% | ~−37% |
> | Bootstrap 99.9% CI low | 0.962 | <0 (fails gate) |
>
> The strategy **fails gate 1 (bootstrap CI > 0), gate 2 (OOS
> Sharpe ≥ 2.0), gate 3 (OOS CAGR ≥ 30% OR CDI floor), and gate 4
> (OOS MDD ≥ −25%)** under the honest engine. Per mandate §2.5 (zero
> bypass), it is not promotable.
>
> **What stays true.** The underlying Gayed regime-rotation thesis
> `[leverage_for_the_long_run, p.11-14]` still carries modest edge
> at ~14%/yr CAGR — comparable to the CDI BR floor for an
> unleveraged version, but the leveraged (L=2×) form used here pays
> disproportionate drawdown (−37% vs −21% baseline) for no
> incremental CAGR above CDI.
>
> **Next steps (user-decided 2026-04-2X).** See
> `jornada/2026-04-23-0700-overnight-summary.md §"Decisão que você
> precisa tomar"` for the 4 options (V3 / Phase-6 Gayed 1× fallback
> / abandon / freeze + Plano B). The user selected **<option>**; see
> `docs/investment-mandate.md §7` (row dated 2026-04-22) for the
> decision record.
>
> **Historical record.** Original buggy-engine results are preserved
> verbatim in `§9` below and in
> `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/` (now flagged
> via `ENGINE_BIAS_FORENSIC.md`). Do not cite the buggy numbers as
> truth.
>
> **Read also:**
> - `reports/phase_3_5f/honest_revalidation/v2_l2_gayed_cfd/AGGREGATE.md`
> - `reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md`
> - `jornada/2026-04-22-engine-lookahead-bug.md`
> - `jornada/2026-04-22-plano-a-honest-revalidation.md`
```

---

## Notes for the merge operation

1. The banner uses the blockquote style (`>`) to visually separate it
   from the rest of the doc body. This matches the pattern used in
   other strategy docs that carry status markers.
2. Replace `<option>` in the banner with the letter the user
   selects (A / B / C / D).
3. The existing body of the strategy doc should move to §9 as a
   historical record. Do not delete the buggy-era text — it is
   forensic evidence of how the bias manifested.
4. Add a "Last reviewed: 2026-04-22" line under the H1 in the same
   commit.

---

## Citations

- `[advances_fin_ml, p.31-34]` — look-ahead bias definition.
- `[leverage_for_the_long_run, Gayed, p.11-14]` — regime rotation
  thesis (still valid).
- `[advances_fin_ml, p.196-202]` — DSR + bootstrap CI (gate 1).
- Mandate §2 (CDI floor) + §2.5 (zero bypass).
