# V2-L2 Gayed CFD — honest re-validation under fixed engine

**Lead:** V2-L2 Gayed transported CFD (Plano A short-hold Pepperstone Razor)
**Config:** `gayed_ema100_L2_off_gld`
  (regime EMA-100 on SPY, risk-on = 50% SPY + 50% QQQ, risk-off = 100% GLD,
  leverage L=2, daily close rebalance, long-only, broker model
  `pepperstone_razor_cfd`)
**Re-validation date:** 2026-04-22
**Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`
**Engine-fix commit:** `7b90a8f` — `fix(backtest): shift weight×return
  alignment to remove lookahead bias`
**Plan reference:** `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`
  §F3 (honest winner hunt) + §5.5 (13-gate definitions)
**Scope of this file:** pure aggregation of artifacts produced in F2. **No
  new simulations are run here.** All numbers come from the F2 outputs
  listed in §6 (Data lineage) below.

---

## 1. One-liner verdict

**FAIL.** Under the honest post-`7b90a8f` engine, `gayed_ema100_L2_off_gld`
collapses from the baseline 79% OOS CAGR / Sharpe 2.28 claim to roughly
13-14% CAGR / Sharpe 0.6 with a −37% MaxDD. The strategy fails the Plano
A hard target (CAGR ≥ 30%, mandate §2) and fails the binding MaxDD cap
(≥ −25%, mandate §5). Even on the user-accepted CDI soft-floor
(≈ 13%/yr), the strict Tiingo-raw variant (12.58%) sits *below* the floor
and the total-return variants (14.23-14.29%) only clear the soft-floor by
a fraction of a percentage point — well inside bootstrap noise
(99.9% CI OOS Sharpe low = −0.64 to −0.68, i.e. statistically
indistinguishable from zero). Gates 2, 4, 5, 6, 8, and the bootstrap
lower-bound test (gate 1) all **FAIL** outright. The original 79% OOS
CAGR was a look-ahead artifact from the `w_i × r_i` timing convention
identified in commit `7b90a8f`. **V2-L2 is rejected as the Plano A
winner.**

---

## 2. Side-by-side comparison — buggy baseline vs honest re-validation

Baseline ("Buggy") = `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld.json`
(iter 27, produced 2026-04-18T17:56:52Z, frozen for forensic record).

Honest A.1 (Tiingo raw close, same cost model as baseline) =
`reports/phase_3_5f/v2_l2_gayed_redo/summary.json → stage_a1_tiingo_close`.

Honest A.1b (Tiingo `adj_close`, TR variant) and Honest A.2
(testfolio `SPYSIM/QQQSIM/GLDSIM` TR) shown for context per §F3 step 5
(Stage-2 data concordance).

### 2.1 IS split (2001-05-14 → 2017-12-31)

| Metric | Buggy baseline | Honest A.1 raw | Honest A.1b adj | Honest A.2 SIM |
|---|---:|---:|---:|---:|
| Sharpe | 1.856 | 0.282 | 0.402 | 0.430 |
| CAGR | 53.42% | 3.99% | 7.25% | 8.12% |
| MaxDD | −22.67% | −59.06% | −58.52% | −56.63% |

### 2.2 OOS split (2018-01-01 → 2023-12-31) — **primary decision window**

| Metric | Buggy baseline | Honest A.1 raw | Honest A.1b adj | Honest A.2 SIM |
|---|---:|---:|---:|---:|
| Sharpe | **2.284** | **0.559** | **0.609** | **0.607** |
| CAGR | **79.14%** | **12.58%** | **14.29%** | **14.23%** |
| MaxDD | **−21.02%** | **−38.82%** | **−36.21%** | **−36.90%** |

Delta buggy → honest A.1 raw: **ΔSharpe −1.725, ΔCAGR −66.56pp**. This
is the core forensic finding.

### 2.3 FWD split (2024-01-01 → 2026-04-14) — forward stress

| Metric | Buggy baseline | Honest A.1 raw | Honest A.1b adj | Honest A.2 SIM |
|---|---:|---:|---:|---:|
| Sharpe | 1.821 | 0.806 | 0.860 | 0.865 |
| CAGR | 59.28% | 20.27% | 22.10% | 22.27% |
| MaxDD | −17.35% | −29.52% | −28.42% | −28.39% |

### 2.4 Aux metrics

| Metric | Buggy baseline | Honest A.1 raw |
|---|---:|---:|
| WF 8-window profitable ratio | 1.000 | 0.750 |
| WF max window DD | 22.7% | 47.8% |
| Bootstrap 99.9% CI full Sharpe low | 0.962 | −0.243 |
| Bootstrap 99.9% CI OOS Sharpe low | n/a (not computed) | −0.643 |
| Median hold (days) | 6.0 | 6.0 |
| Total regime switches | 616 | 616 |
| Cum transaction cost (%) | 1.258 | 1.258 |
| Cum swap cost (%) | −0.449 | −0.450 |

Interpretation: switch schedule and cost model are untouched by the
engine fix — the delta is 100% attributable to the
`w_i × r_i` → `w_{i-1} × r_i` correction.

---

## 3. 13-gate checklist per §5.5

Primary column is **A.1 (Tiingo raw close, baseline cost model)** because
that is the variant that exactly replicates the buggy baseline setup,
only with honest timing. A.1b / A.2 shown in parentheses where the
verdict could in principle change.

| # | Gate (§5.5) | Threshold | A.1 value | Verdict |
|---|---|---|---|---|
| 1 | Bootstrap 99.9% CI low > 0 on OOS Sharpe AND full-period Sharpe [advances_fin_ml, p.196-202] | > 0 | OOS low = **−0.643**; full low = **−0.243** | **FAIL** |
| 2 | OOS Sharpe ≥ 2.0 | ≥ 2.0 | **0.559** (A.1b 0.609 / A.2 0.607) | **FAIL** |
| 3 | OOS CAGR ≥ 30% net (soft-floor CDI ≈ 13% requires explicit user sign-off) | ≥ 30% strict | **12.58%** (A.1b 14.29% / A.2 14.23%) | **FAIL strict**; A.1 FAIL even on 13% CDI soft-floor; A.1b/A.2 only PARTIAL on soft-floor (margin within bootstrap noise) |
| 4 | OOS MaxDD ≥ −25% (mandate §5, binding, no relaxation) | ≥ −25% | **−38.82%** (A.1b −36.21% / A.2 −36.90%) | **FAIL** |
| 5 | FWD Sharpe > 0 | > 0 | **0.806** | PASS |
| 6 | Walk-forward 8 windows: ≥ 6/8 profitable AND max window DD ≤ 25% | both | profitable 0.750 ✅, max DD **47.8%** ❌ | **FAIL** (DD sub-gate) |
| 7 | Median hold ≥ 3 trading days | ≥ 3d | **6.0d** | PASS |
| 8 | IR vs SPY ≥ 0.5 on OOS | ≥ 0.5 | **needs re-run under honest engine** — not computed by `scripts/run_phase3_5f_stage_a.py`. Expected FAIL: SPY OOS CAGR ≈ 12-13% (buy-hold) vs honest strategy OOS CAGR 12.58%, i.e. leveraged Gayed delivers ~zero active return over SPY with materially higher DD — IR is almost certainly below 0.5 and likely negative. | **TBD / expected FAIL** |
| 9 | Cross-lib concordance ≥ 2/3 within ±3pp CAGR on OOS | ≥ 2/3 | canonical 20.79% = numpy 20.79% = vectorbt 20.79% = backtrader 20.79%; bt errored on pre-existing data NaN unrelated to the fix | **PASS** (2/3 — vectorbt, backtrader; bt error isolated and documented) |
| 10 | Stage-2 data concordance Tiingo adj_close vs testfolio SIM ≤ 1pp OOS+FWD | ≤ 1pp | OOS ΔCAGR 0.06pp; FWD ΔCAGR 0.17pp | **PASS** |
| 11 | PBO < 0.5 via CSCV 10-block (if grid ≥ 5 configs) [advances_fin_ml, p.208-211] | < 0.5 | V2-L2 grid in `reports/phase_3_5f/v2_l2_gayed_redo/` has 27 configs → grid-level gate applies; PBO NOT recomputed under honest engine in F2 Stage-A run | **needs grid-level re-run under honest engine** |
| 12 | DSR p-value < 0.05 on winner OOS Sharpe (if grid ≥ 5 configs) [advances_fin_ml, p.196-202] | p < 0.05 | not recomputed; but given honest OOS Sharpe 0.559 vs buggy 2.284, DSR under 27-trial grid is very unlikely to survive | **needs grid-level re-run under honest engine; expected FAIL** |
| 13 | Cost-sensitivity — cost bps × 2 still OOS Sharpe > 1.0 | OOS Sharpe > 1.0 at 2× | not computed in F2 Stage-A; base case honest OOS Sharpe is already **0.559** < 1.0, so doubling costs cannot satisfy the gate | **FAIL by inspection (base < 1.0)** |

### Summary tally

| Count | Gates |
|---|---|
| **PASS (4)** | 5, 7, 9, 10 |
| **PARTIAL / soft-floor only (1)** | 3 (A.1b/A.2 clear CDI floor marginally; A.1 fails even soft-floor) |
| **FAIL outright (6)** | 1, 2, 4, 6, 8 (expected), 13 |
| **TBD — needs grid-level re-run under honest engine (2)** | 11, 12 (both expected FAIL given the 4× OOS-Sharpe collapse) |

**Aggregate:** 4 PASS / 1 PARTIAL / 6 FAIL / 2 TBD-likely-FAIL. The §5.5
"zero bypass" clause requires ALL 13 gates to pass. V2-L2 misses by a
wide margin on the hardest gates (2, 4, 6) and has no path to repair
within the existing config family.

---

## 4. Interpretation

The original `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/` report
claimed **OOS Sharpe 2.285, CAGR 79.14%, MaxDD −21.02%** and was
promoted to Plano A winner on 2026-04-19. Under the honest engine patch
`7b90a8f` (which shifts the return-compounding alignment from `w_i × r_i`
to `w_{i-1} × r_i`, removing the same-bar lookahead — see
`[advances_fin_ml, p.31-34]` on timing-convention audits for
backtests), the OOS figures collapse to **Sharpe 0.559, CAGR 12.58%,
MaxDD −38.82%**. The 66.56pp CAGR gap is the magnitude of the
look-ahead inflation this config was capturing on regime-flip days.

The honest numbers fall:
- **Below Plano A CAGR target** (≥ 30%, `docs/investment-mandate.md §2`).
- **Below the CDI-BR soft-floor** (~13%) on Tiingo raw close; borderline
  (~14.2%) on the TR variants, with a 99.9% bootstrap CI on OOS Sharpe
  of [−0.64, +2.17], i.e. the edge is statistically indistinguishable
  from zero.
- **Outside the binding MaxDD cap** (≥ −25%, mandate §5) by ~12pp.
- **Below the Sharpe gate** (≥ 2.0 target / ≥ 1.5 with user approval)
  by a factor of ~3.5×.

Walk-forward also degrades: 1.000 → 0.750 profitable-ratio (still clears
6/8 ≥ 0.75), but **max window DD blows from 22.7% to 47.8%** — more
than double the gate cap. This is the canonical signature of a strategy
whose apparent stability was manufactured by the look-ahead. Once the
oracle bar is removed, regime transitions produce true whipsaw losses
and the leveraged leg amplifies them.

The thesis itself (Gayed, EMA regime rotation,
`[leverage_for_the_long_run, Gayed, p.11-14]`) remains sound as a
framework. What fails here is the **2× leveraged CFD transport of that
signal onto SPY+QQQ+GLD with daily close rebalance under the Pepperstone
Razor cost model**. An unleveraged (L=1) version of the same signal
would be expected to survive as a low-alpha passive-like variant, but
that is out of scope for Plano A (which mandates leveraged short-hold
CFD exposure per mandate §2). No config tweak inside the existing V2-L2
grid (lookback, off-regime asset, lower leverage) saves this — all 27
configs used the same timing-biased engine, and the §F3 re-run shows
that after the fix the winner config itself falls well short. The
broader grid revalidation under gates 11/12 (§F3 follow-up) is expected
to confirm this pattern across all 27 configs.

**Decision:** V2-L2 is rejected as Plano A winner. Per the §F3 priority
queue, the next candidate to re-evaluate under the honest engine is
V2-L4 Carver RP blend (was DEAD because "blend diluted L2 alpha 79% →
16%"; if L2's honest alpha is 15%, the blend may end up comparable or
better). Escalation to user happens at the end of F3, not here.

---

## 5. Audit note: why A.1 vs A.1b vs A.2 is not a gate-saving argument

The Tiingo `adj_close` (A.1b) and testfolio SIM (A.2) variants deliver
OOS CAGR 14.29% / 14.23% — roughly 1.7pp above the Tiingo raw-close
(A.1) result of 12.58%. That delta is dividend pass-through: raw-close
treats ex-div price drops as losses, while TR variants don't. Under a
proper share-CFD model with dividend cash adjustment, the TR numbers
are the more honest accounting.

However:
- The **Sharpe** in A.1b/A.2 (0.609 / 0.607) is still ~3.3× below the
  gate-2 minimum of 2.0.
- The **MaxDD** in A.1b/A.2 (−36.2% / −36.9%) is still ~11-12pp beyond
  the gate-4 binding cap of −25%.
- The **bootstrap 99.9% CI** on OOS Sharpe remains non-positive at its
  lower bound ([−0.68, +2.17] for A.1b).

So the TR upgrade does not rescue V2-L2 even under the most
favourable dividend-accounting assumption. The failure is structural,
not accounting.

---

## 6. Data lineage

All inputs to this aggregate are F0-F2 artifacts. No new simulations
triggered by this file.

**Primary honest numbers:**
- `reports/phase_3_5f/v2_l2_gayed_redo/summary.json` — stage-A three-variant
  concordance (A.1 / A.1b / A.2), bootstrap, walk-forward, gate verdicts.
- `reports/phase_3_5f/v2_l2_gayed_redo/report.md` — human-readable stage-A
  report with concordance matrix.
- `reports/phase_3_5f/v2_l2_gayed_redo/cross_lib_summary.json` — gross-returns
  cross-lib check (canonical vs numpy_ref vs vectorbt vs backtrader; bt
  errored on pre-existing GLD-NaN).
- `reports/phase_3_5f/v2_l2_gayed_redo/cross_lib_report.md` — human-readable
  cross-lib report.
- `reports/phase_3_5f/v2_l2_gayed_redo/stage_a1_tiingo_close_daily_returns.parquet`
- `reports/phase_3_5f/v2_l2_gayed_redo/stage_a1b_tiingo_adj_close_daily_returns.parquet`
- `reports/phase_3_5f/v2_l2_gayed_redo/stage_a2_testfolio_daily_returns.parquet`

**F2 execution logs:**
- `logs/phase3_5f_f2_stage_a.log` — stage-A re-run.
- `logs/phase3_5f_f2_cross_lib.log` — cross-lib re-run.
- `logs/phase3_5f_f2_pytest.log` — regression pytest after the fix.

**Engine fix commit:**
- `7b90a8f` — `fix(backtest): shift weight×return alignment to remove
  lookahead bias` (patches `src/market_lab/backtest/strategies/plano_a_leveraged_rotation.py`
  and the other engines identified in F1 inventory).

**Buggy baseline (preserved, do not edit — forensic record):**
- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld.json`
- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld.md`
- Full grid (27 configs) in the same directory, all inflated by the
  same lookahead bias.

**Supporting references:**
- `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`
  (plan, §F3 + §5.5)
- `jornada/2026-04-22-2212-engine-lookahead-bias-descoberto.md` (original
  bug-discovery narrative)
- `specs/phase_3_5a_v2.md` (V2 gate contract)

---

## 7. Citations

- Look-ahead detection and two-stage replication protocol:
  `[advances_fin_ml, p.31-34]`.
- PBO CSCV method (gate 11): `[advances_fin_ml, p.208-211]`.
- DSR + bootstrap 99.9% CI (gates 1, 12): `[advances_fin_ml, p.196-202]`.
- Walk-forward 6/8 + max-DD gate (gate 6): `[advances_fin_ml, ch.11]`.
- Original Gayed regime-rotation thesis:
  `[leverage_for_the_long_run, Gayed, p.11-14]` (EMA signal),
  `[leverage_for_the_long_run, Gayed, p.16-17]` (leverage sizing rationale),
  `[leverage_for_the_long_run, Gayed, p.21]` (risk-off asset choice).
- Carver retail cost model + hold discipline (cost model used in
  A.1/A.1b/A.2): `[systematic_trading, p.185-188]`.
- Kelly f/2 leverage cap + ruin considerations for L=2 choice:
  `[math_money_mgmt, Vince]`, `[leverage_space, Vince]`.

---

**End of aggregate. Verdict: FAIL. Next F3 candidate: V2-L4 Carver RP.**
