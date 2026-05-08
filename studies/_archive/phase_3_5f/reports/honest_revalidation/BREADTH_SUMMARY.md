# Phase 3.5f — Honest Revalidation Breadth Summary

**Date:** 2026-04-22
**Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`
**F2 engine-fix commit:** `7b90a8f` (`fix(backtest): shift weight×return alignment to remove lookahead bias`)
**Purpose:** Synthesize honest-engine re-validation verdicts across all 6 Plano A V2 leads so the user can choose a next-step path without having to read the 6 per-lead AGGREGATE files.
**Path tag:** [SHORT-HOLD CFD]

---

## 0. TL;DR

Under the honest engine (`prev_w × r_i` shift, post-F2), **none of the 6
Plano A V2 lead families passes the 13-gate winner definition**
(`docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md
§5.5`). The previous "winner" V2-L2 Gayed loses ~65pp of its reported
OOS CAGR (79.14% → ~14% honest); the five other leads were already DEAD
and stay DEAD (L1/L3/L5/L6 were on clean engines; L4 partial
contamination was only 4.8% blend weight, immaterial).

**Mission outcome:** F3 gate (c) fires — Plano A has no honest winner.
User must decide between four options (see §6 below).

---

## 1. Context (for future agents)

On 2026-04-22, a **look-ahead bias** was discovered in
`src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py:462`:
the return-compounding line used `new_w[bar_i] * ret[bar_i]` (weight
at bar `i` times return at bar `i`) instead of the correct
`prev_w[bar_i] * ret[bar_i]` (yesterday's decision earns today's
move). Because the regime signal at bar `i` is computed from
`close[i]` and the return at bar `i` is also computed from `close[i]`,
the buggy form gave the simulator perfect foresight of each day's
close before sizing into it. `[advances_fin_ml, p.31-34]`

Numerical magnitude on V2-L2 `gayed_ema100_L2_off_gld` over 2001-05 →
2026-04:

| Method | Equity 2026-04 | CAGR |
|---|---:|---:|
| Canonical `w_i × r_i` (buggy) | 660,440× | 71.16% |
| Numpy `w_{i-1} × r_i` (shift) | 34.8× | 15.29% |
| bt adapter | 34.8× | 15.29% |
| vectorbt adapter | 34.8× | 15.29% |
| backtrader adapter | 34.8× | 15.29% |

Three independent libraries + a numpy reference all agree on the
shift convention. The bug was isolated to **one file, one line**
(see §1.2 below).

### 1.1 Scope of contamination (F1 finding — narrower than expected)

Plan §1.4 suspected `letf_rotation.py` was also buggy (based on a
surface grep). F1 reread the files and confirmed it is NOT: the
`w_i × r_i` anti-pattern only exists in
`plano_a_leveraged_rotation.py`. Consequently:

- **Tainted** (needs forensic banners):
  1. `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/` — direct bug exposure.
  2. `reports/phase3_5a_v2/v2_l4_carver_risk_parity/` — partial
     (L2 sleeve was only **4.8% of blend weight**, not 66-75% as the
     plan had guessed; magnitude is minor).
  3. `reports/phase4_0/index_cfd_validation/` — used the buggy canonical
     for Index CFD validation.

- **Clean, preserved as-is** (no banners): phase_3_5b, phase_3_5c,
  phase_3_5d, phase_3_5e. Their engines were never exposed to the
  buggy line. (Plano B `letf_rotation.py` uses a different numeric
  path and was verified clean.)

- **Flagged independently** (no fresh banner needed):
  `reports/phase_3_5c/cross_lib/canonical_baseline/` already carried
  a "divergent" verdict at the time; it is cross-referenced in the
  scope doc instead.

Full file-by-file audit:
`docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md`.

### 1.2 The surgical tests

Four tests in `tests/test_plano_a_lookahead_bias.py` discriminate the
buggy vs honest convention by hand-verifiable numbers (flat-price
jump, single-flip isolation, symmetric flipper, and cross-lib
concordance within 1e-6). All 4 failed against the pre-F2 engine and
pass against the post-F2 engine. Pytest baseline is **918 green**
(914 pre-F0 + 4 new).

---

## 2. Top-line verdict table (all 6 V2 leads, honest engine)

| Lead | Module | Engine status (F1) | Honest OOS Sharpe | Honest OOS CAGR | Honest OOS MDD | Verdict |
|---|---|---|---:|---:|---:|---|
| V2-L1 TSMOM | `tsmom_multi_asset.py` | CLEAN (never buggy) | −0.21 | −0.49% | −10.24% | FAIL |
| V2-L2 Gayed | `plano_a_leveraged_rotation.py` | BUGGY → F2 fixed | 0.56 | 12.58% (raw) / 14.29% (adj) | −37% | FAIL |
| V2-L3 AFML | `afml_tb_meta.py` | CLEAN | 1.21 | 2.50% | −0.76% | FAIL |
| V2-L4 Carver RP | (blend uses L1+L2+L3) | L2 sleeve was buggy → fixed | 0.62 | 4.99% | −12.77% | FAIL |
| V2-L5 Kalman | `kalman_pair_cointegration.py` | CLEAN | — | — | — | FAIL (structural: 0 cointegrated pairs) |
| V2-L6 vol-breakout | `donchian_breakout.py` | CLEAN | −0.22 to −0.73 (12/12 neg) | — | — | FAIL |

Sources (individual AGGREGATE files):

- `reports/phase_3_5f/honest_revalidation/v2_l1_tsmom/AGGREGATE.md`
- `reports/phase_3_5f/honest_revalidation/v2_l2_gayed_cfd/AGGREGATE.md`
- `reports/phase_3_5f/honest_revalidation/v2_l3_afml/AGGREGATE.md`
- `reports/phase_3_5f/honest_revalidation/v2_l4_carver_rp/AGGREGATE.md`
- `reports/phase_3_5f/honest_revalidation/v2_l5_kalman/AGGREGATE.md`
- `reports/phase_3_5f/honest_revalidation/v2_l6_vol_breakout/AGGREGATE.md`

---

## 3. Gate-by-gate matrix (13 gates × 6 leads)

Gates per plan §5.5. Cells: `Y` = pass, `N` = fail, `—` = not applicable
(structural failure upstream of the gate). "Best config" per lead used
to evaluate gates (for L3 = XLF; for L2 = `gayed_ema100_L2_off_gld`
honest; for L4 = the full blend; others see per-lead AGGREGATE).

| # | Gate | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Bootstrap 99.9% CI lower bound > 0 (OOS + full) | N | N | N | N | — | N |
| 2 | OOS Sharpe ≥ 2.0 | N | N | N | N | — | N |
| 3 | OOS CAGR ≥ 30% (soft-floor CDI ~13%) | N | N (borderline ~14%) | N | N | — | N |
| 4 | OOS MaxDD ≥ −25% | Y | N (−37%) | Y | Y | — | Y/N (mixed) |
| 5 | FWD Sharpe > 0 | N | mixed | N | N | — | Y (12/12 FWD pos by coincidence) |
| 6 | Walk-forward 6/8 profitable, max window DD ≤ 25% | N | N | N | N | — | N |
| 7 | Median hold ≥ 3 trading days | Y | Y (6d) | Y (~7d) | Y | — | Y |
| 8 | IR vs SPY ≥ 0.5 on OOS | N | N | N | N | — | N |
| 9 | Cross-lib concordance ≥ 2/3 within ±3pp CAGR | Y | Y (post-fix 1e-6) | Y | Y | — | Y |
| 10 | Stage-2 data concordance ±1pp CAGR (OOS+FWD) | Y | Y | Y | Y | — | Y |
| 11 | PBO < 0.5 (CSCV) | N | N | — (single config/ticker) | N | — | N |
| 12 | DSR p-value < 0.05 | N | N | — | N | — | N |
| 13 | Cost 2× keeps OOS Sharpe > 1.0 | N | N | N | N | — | N |
| | **Pass count** | 2 | 2 | 3 | 2 | 0 | 3 |

No lead passes **all 13**. No lead passes even **gate set {1, 2, 3, 8}**
(the four most economically load-bearing gates). Structural gates (9,
10) pass broadly because the engine and data pipeline are now
consistent — that is the F2 fix working, not an edge.

---

## 4. Lead-by-lead one-sentence postmortem

- **V2-L1 TSMOM (multi-asset monthly momentum).** FAIL. Engine was
  always clean; OOS Sharpe −0.21 and CAGR −0.49% on the best-Sharpe
  config confirm the original "swap drag kills 40-160d holds"
  diagnosis `[systematic_trading, p.185-188]`.

- **V2-L2 Gayed (EMA-100 regime rotation, L=2).** FAIL. Under the
  honest engine the headline "Sharpe 2.28 / CAGR 79%" collapses to
  Sharpe ~0.56 / CAGR ~14% on OOS with MDD worsening from −21% to
  −37%. The 2× leverage cranks up drawdown without recovering the
  lost CAGR. Below the CDI BR floor (mandate §2) and fails gate 4
  (MDD ≥ −25%). The regime-rotation edge is real but modest — the
  "winner" number was ~65pp of lookahead inflation
  `[leverage_for_the_long_run, Gayed, p.11-14]` for the underlying
  thesis, `[advances_fin_ml, p.31-34]` for the bias that inflated it.

- **V2-L3 AFML triple-barrier meta-label.** FAIL. Engine always
  clean. Best ticker (XLF) OOS Sharpe 1.21 but CAGR only 2.50% — the
  primary EMA-50 cross is too thin for meta-labeling to lift above
  Pepperstone costs `[advances_fin_ml, p.50]`.

- **V2-L4 Carver risk-parity blend (L1+L2+L3).** FAIL. The blend
  hypothesis from the plan ("maybe L2's honest alpha dilutes to
  something survivable") was invalidated by the actual risk weights:
  L3 carries **66%** (low IS vol), L1 carries **29%**, L2 only
  **4.8%**. The L2 contamination footprint on the blend was tiny;
  the blend inherits L3's CAGR-starved profile (4.99% OOS CAGR)
  `[systematic_trading, ch.11]`, `[advances_fin_ml, ch.16]`.

- **V2-L5 Kalman pair cointegration.** FAIL (structural). Zero
  ADF-cointegrated pairs in the ETF universe; no simulation to
  re-run. Engine state is irrelevant to this failure mode.

- **V2-L6 Donchian volatility breakout.** FAIL (reconfirmed).
  12/12 configs produced OOS Sharpe negative on the clean engine;
  honest re-run only widens the loss. `[trend_following_covel, ch.4]`
  — trend-follow needs 30+ instrument universe; 10-ETF basket too
  narrow.

---

## 5. No winner exists

Per plan §6 mission statement, a "winner for Plano A must satisfy
ALL 13 conditions under the honest engine with cost+swap+slippage
applied." Zero leads clear that bar. **F3 gate (c) — no winner — fires.**

Per mandate §2.5 (zero bypass), we do not soft-gate any lead through.
Per `project_plano_a_v2_last_attempt` user-memory ("if Phase 3.5a-V2
fails, abandon Plano A entirely; no V3, focus on refining Plano B
only"), the default path would be abandonment, but the user has
previously corrected that rule (see
`jornada/2026-04-18/23-phase3.5a-v2-WINNER-humana.md`), so the
decision is re-presented here.

---

## 6. Four options (F3 gate (c))

The user chose between these options at the F3/F4 transition. Each is
presented with ~3-line pros/cons and the immediate cost of pursuing it.

### Option A — Design a new V3 family (7th lead)

**Pros.** Preserves Plano A aspiration (5-10%/month leveraged
short-hold CFD per mandate §3). The 6 tested families do not exhaust
the hypothesis space — e.g., vol-surface skew signals, event-study
pre-earnings, cross-asset lead-lag are untested classes.
**Cons.** 4-8 week spec + build + validate cycle. High risk of
another null — the 6 tested were the literature-dense candidates; the
V3 candidate would lean on thinner citations.
**Cost to start.** New spec doc + registry + CPCV plumbing + adapters.
Budget: 1 new scientific citation family + ~15 gate-passing attempts
(Plano A already burned 80+ iters against the 6 families).

### Option B — Phase-6 fallback (Gayed 1× unleveraged)

**Pros.** Numbers-in-hand: honest Gayed 1× is estimated at
~11%/yr CAGR with ~16% MDD, Sharpe ~0.7. Passes MDD gate (4) and
bootstrap (1) but is below CDI BR. Acceptable as "passive-like active"
in bucket A with no real alpha claim.
**Cons.** CAGR below CDI = violates mandate §2 minimum. Plano A
thesis was "aggressive leveraged 5-10%/mo"; unleveraged Gayed is not
that. Amounts to re-labeling Plano A as Plano C with more steps.
**Cost to start.** Days. Re-run Gayed at L=1, document, ship.

### Option C — Abandon Plano A permanently

**Pros.** Honest. Invokes the `project_plano_a_v2_last_attempt` rule
cleanly. Frees bandwidth to finish Plano B grid (Phase 3.5e c06-c12)
and refine Plano C allocation. Removes the permanent temptation to
re-lever a non-edge.
**Cons.** The user explicitly overrode this rule once before (2026-04-18);
overriding it is a live option. Bucket A capital reallocates per
mandate §4.7 (all to Plano C buy-hold).
**Cost to start.** Hours. Update mandate §7 + strategy doc banner
(already staged in `.pending`) + jornada closure entry.

### Option D — Freeze Plano A, finish Plano B (c06-c12) on honest engine

**Pros.** Plano B engine (`letf_rotation.py`) is already clean per F1
audit — no re-validation cost. 7 untested families remain in the
Phase 3.5e registry. A Plano B winner would cover the 20-40% active
bucket per mandate §1, even without a Plano A.
**Cons.** Out-of-scope of this plan (user set Plano B stand-by on
2026-04-22). Requires user lifting the stand-by. Still does not
deliver Plano A's aggressive-leveraged profile.
**Cost to start.** Relaunch `self_improve_loop.sh` on Phase 3.5e c06
onward. 1-2 weeks of iter budget to exhaust the grid.

---

## 7. Pending files awaiting user review

Staged under `docs/.pending/` (outside canonical paths so the user
must explicitly merge them):

- `docs/.pending/mandate_section7_entry.md` — draft `docs/investment-mandate.md §7` row.
- `docs/.pending/plano_a_v2_l2_gayed_cfd_banner.md` — draft banner for the strategy doc.
- `docs/.pending/jornada_readme_update.md` — draft "Onde estamos hoje" + "O que vem a seguir" rewrite.

No canonical doc is modified until the user picks a path from §6.

---

## 8. Citations

- Look-ahead bias detection, shift convention: `[advances_fin_ml, p.31-34]`.
- PBO CSCV gate: `[advances_fin_ml, p.208-211]`.
- DSR / bootstrap CI: `[advances_fin_ml, p.196-202]`.
- Walk-forward 6/8 gate: `[advances_fin_ml, ch.11]`.
- Meta-labeling as precision filter, not edge: `[advances_fin_ml, p.50]`.
- Risk-parity blend caveats: `[systematic_trading, ch.11]`, `[advances_fin_ml, ch.16]`.
- Gayed regime rotation (V2-L2 thesis): `[leverage_for_the_long_run, Gayed, p.11-14, p.16-17, p.21]`.
- Retail CFD cost model: `[systematic_trading, p.185-188]`.
- Trend-follow universe size: `[trend_following_covel, ch.4]`.
- CDI BR floor, mandate §2 + §2.5 (zero bypass).
- Plano A last-attempt rule: `project_plano_a_v2_last_attempt` (user memory).

---

## 9. Provenance

- F0 commit: `2b414d0` — surgical tests added.
- F1 commit: `7c280a2` — scope document.
- F2 commit: `7b90a8f` — engine fix + cross-lib concordance 1e-6.
- F3 commits (6 aggregates): `02fe3ea` (L2), `2947bc4` (L5),
  `1cd3895` (L1), `c1542e5` (L6), `55f7eca` (L4), plus L3 aggregate
  (written alongside the others, same branch).
- F4 commit: this document + jornada entries + banners + .pending
  files (see final commit chain in the executing session report).

---

**End of breadth summary.**
