# Phase 3.5f — Engine lookahead fix + Plano A honest winner hunt

**Created:** 2026-04-22
**Plan author:** assistant (session finishing 2026-04-22)
**Executing session:** TBD (user will launch fresh Claude Code session)
**Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422` (ALREADY CREATED, clean)
**Baseline pytest:** 914 tests green at plan creation time

---

## 0. TL;DR — what this plan does

This plan re-establishes truth in the Plano A (short-hold CFD Pepperstone)
leg of the ai-trade project after a **look-ahead bias** was discovered in
the simulation engine on 2026-04-22. The bug silently inflated backtest
returns for every regime-rotation strategy that used the shared
simulator, potentially making `gayed_ema100_L2_off_gld` (the V2-L2
winner) an artifact, and potentially hiding a real winner among the five
V2 "DEAD" leads that were rejected.

**Mission — single objective:** find a **stable, honest, winning
strategy** for Plano A under the corrected engine. "Winner" is defined
rigorously in §6. If no winner survives honest validation, escalate to
the user.

**Hard constraints:** Plano A only. Plano B stand-by. Plano C untouched.
`docs/self_improvement/memory.md`, `trial_count.json`, and
`reports/phase_3_5e/*` stay frozen (forensic preservation of the
paused Plano B search). Baseline pytest must be green after every
commit.

---

## 1. What happened — context for the executing session

### 1.1 The original state at session start (for reference)

On 2026-04-19, a "winner" was confirmed for Plano A:
`gayed_ema100_L2_off_gld` — Gayed regime rotation
`[leverage_for_the_long_run, Gayed, p.11-14]` transported to Pepperstone
Razor CFD, signal EMA-100 on SPY, leverage 2×, risk-on = 50% SPY + 50%
QQQ, risk-off = 100% GLD, daily close rebalance. Reported metrics
(frozen in `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld.json`):

| Split | Sharpe | CAGR | MaxDD |
|---|---:|---:|---:|
| IS (2001-05-14 → 2017-12-31) | 1.856 | 53.42% | −22.67% |
| OOS (2018-01-01 → 2023-12-31) | 2.284 | 79.14% | −21.02% |
| FWD (2024-01-01 → 2026-04-14) | 1.821 | 59.28% | −17.35% |

All 13 V2 gates pass (PBO 0.103, DSR p 0.000288, WF 8/8 @ DD 22.7%,
bootstrap 99.9% CI low 0.962). Baseline doc:
`docs/strategies/plano_a_v2_l2_gayed_cfd.md`.

### 1.2 The bug discovered on 2026-04-22

While doing cross-lib validation (bt / vectorbt / backtrader) for
Plano A as Task #5 of this session, the canonical engine
`simulate_plano_a_rotation` in
`src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py`
disagreed with all three independent libraries by a factor of ~5× in
OOS CAGR (canonical 92% vs libs 21%, cost=0/swap=0 isolation).

Isolation test: same weights matrix fed to a numpy dot-product
reference, vectorbt, and backtrader — all three agreed at CAGR
~15-21%, while canonical alone gave CAGR 71% over 2001-2026. The
difference was traced to a **timing convention bug** in the return
calculation:

```python
# File: src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py
# Lines ~406-466 (see git blame for exact span)
for bar_i, ts in enumerate(common_idx):
    new_w = np.zeros(len(cols), dtype=float)
    for k, t in enumerate(config.risk_on_tickers):
        state = regime_df.iloc[bar_i][t]       # signal at close[bar_i]
        if state == "ON":
            new_w[k] = L * budget_per_asset     # today's weight
        else:
            new_w[-1] += budget_per_asset

    # ... cost/switch bookkeeping ...

    per_asset = ret_vals[bar_i]                 # today's return = close[i] / close[i-1] - 1
    on_ret = np.sum(new_w[:n_assets] * per_asset)  # w_i × r_i  ← LOOK-AHEAD
```

**Why this is look-ahead:** the regime signal at bar `i` is computed from
`close[i]` (via `px > EMA(close)_i`). The return at bar `i` is also
computed from `close[i]` (via `pct_change`). Multiplying `w_i × r_i`
means "use knowledge that close[i] was X to decide the weight at bar i,
then reward that weight with the gain caused by close[i] being X."
Classic Oracle bet.

**Correct convention:** `w_{i-1} × r_i` (the previous-close decision
earns today's return) OR equivalently `w_i × r_{i+1}` (today's decision
earns tomorrow's return). Both are equivalent under weekday-only daily
rebalance.

### 1.3 Numerical proof of the bug (verified this session)

Running canonical (cost=0, swap=0) vs numpy reference on the SAME
weights matrix over 2001-05 → 2026-04:

| Method | Equity 2026-04 | CAGR |
|---|---:|---:|
| Canonical `w_i × r_i` | 660,440× | 71.16% |
| Numpy `w_{i-1} × r_i` (shift) | 34.8× | 15.29% |
| bt-adapter-equivalent | 34.8× | 15.29% |
| vectorbt-adapter-equivalent | 34.8× | 15.29% |
| backtrader-adapter-equivalent | 34.8× | 15.29% |

Three independent libraries and a hand-written numpy reference all agree
on the shift convention. Canonical is alone with the no-shift math. The
difference at OOS-split level:

| | Canonical (buggy) | Honest (shift) |
|---|---:|---:|
| OOS Sharpe (gross, cost=0) | 2.528 | 0.810 |
| OOS CAGR (gross, cost=0) | 91.95% | 20.79% |

After cost+swap is reintroduced (~0.4%/yr drag on the leveraged leg),
the **honest V2-L2 OOS CAGR is projected to be ~15-18%** vs the
baseline 79%. Below CDI BR floor (~13-14%/yr per
`docs/investment-mandate.md §2`) for a leveraged strategy → **not a
winner under the honest engine**.

### 1.4 Known implicated code (preliminary — F1 will inventory fully)

At a minimum, the following engines share the same `w_i × r_i` pattern
based on preliminary grep:

- `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py`
  (Plano A V2-L2 winner)
- `src/ai_trade/backtest/strategies/letf_rotation.py` (Plano B V4
  rejected / Plano B search universe)

Phase 3.5c cross-lib validation of Plano B V4 showed the same divergence
pattern (canonical 37.9% vs libs 11.6%) but was at the time misdiagnosed
as a "synthetic LETF data source" issue. **It was the engine bug all
along.** See `jornada/2026-04-20/03-phase-3-5c-cross-lib-exposed-baseline-mismatch.md`.

---

## 2. Hard constraints (READ THIS FIRST)

Violation = PR rejected. No exceptions.

### 2.1 Scope

- **Plano A only.** All re-validation work targets Plano A V2 leads. No
  Plano B revalidation. No Plano C work.
- **No self-improve loop.** Do NOT run `scripts/self_improve_loop.sh`.
  This is manual validation work.
- **No Phase 3.5e continuation.** The Plano B breadth-hunt grid
  (c06-c12) is explicitly paused. Do NOT run any new Phase 3.5e iters.
- **No new strategy families.** Only re-validate the 6 leads from Phase
  3.5a-V2 (`V2-L1` TSMOM, `V2-L2` Gayed, `V2-L3` AFML meta-label,
  `V2-L4` Carver RP, `V2-L5` Kalman pairs, `V2-L6` vol-breakout).

### 2.2 Files that are FROZEN (do not touch)

- `docs/self_improvement/memory.md` — Plano B search state (preserved
  for later resumption).
- `docs/self_improvement/trial_count.json` — Plano B PBO accounting
  (preserved).
- `reports/phase_3_5e/*` — Plano B breadth-hunt reports (preserved).
- `reports/phase_3_5b/*` — Plano B V4 winner reports (historical).
- `reports/phase_3_5d/*` — Plano B 3× LETF reports (historical).
- `reports/phase_3_5a_v2/v2_l2_gayed_transported_cfd/` — Plano A V2-L2
  winner reports with BUGGY numbers (historical forensic record).

### 2.3 Files that MUST be updated during F4

- `docs/strategies/plano_a_v2_l2_gayed_cfd.md` — status marker +
  corrected numbers OR "rejected" banner.
- `docs/investment-mandate.md §7` — new entry registering bug,
  fix, and decision review.
- `docs/CURRENT_STATE.md` — if it exists and references V2-L2 or
  Phase 4.0 numbers.
- `jornada/README.md` — index + "Onde estamos hoje" section.

### 2.4 Engineering discipline

- **Pytest baseline stays green after every commit.** Current: 914 tests.
  F2 fix WILL break tests that assert biased numbers — update those
  tests in the SAME commit as the fix. Never ship a commit that leaves
  pytest red.
- **Citation rule (CLAUDE.md Regra 2):** every technical decision cites
  `[book.slug, p.X]` or `[book.slug, ch.Y]`. Not optional.
- **Conventional Commits:** `fix:`, `feat:`, `docs:`, `test:`, `chore:`.
- **No force push to main.** Stay on branch
  `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`.
- **Preserve forensic reports.** All new re-validations write to NEW
  paths under `reports/phase_3_5f/honest_*/...`. Never overwrite the
  historical buggy reports.

### 2.5 Escalation triggers (STOP and ask user)

- F0 tests do NOT confirm the bug as described. Stop, report, do not
  proceed to F2.
- F2 fix breaks > 20% of existing tests (suggests deep dependency on
  buggy numbers). Stop and reassess scope.
- F3 re-validation finds that ALL 6 V2 leads FAIL honest gates (no
  Plano A winner exists). Stop, escalate to user for next-step decision
  (V3 / abandon Plano A / other).
- F3 re-validation produces a new winner different from V2-L2
  (e.g., V2-L4 Carver RP passes honest). Stop before promoting — the
  user wants to review before any auto-promotion.
- Any cost, swap, or regime-filter modification needed to make a
  borderline strategy pass gates. This is mandate §2.5 "zero bypass"
  territory.

---

## 3. Required reading for the executing session

Read in this order **before** writing any code. Total ~30 min.

1. `jornada/README.md` — current state summary.
2. `jornada/2026-04-21-1700-session-summary-phase-3-5e-batch1.md` —
   most recent session summary before this plan.
3. **This document (the plan).**
4. `docs/investment-mandate.md` §1-3, §5, §7 — strategy rules.
5. `docs/strategies/plano_a_v2_l2_gayed_cfd.md` — current (buggy)
   strategy doc.
6. `jornada/2026-04-19/07-phase3.5a-v2-summary-WINNER-FOUND.md` —
   the original V2-L2 claim.
7. `jornada/2026-04-20/03-phase-3-5c-cross-lib-exposed-baseline-mismatch.md`
   — the Phase 3.5c finding that in hindsight foreshadowed this bug.
8. `specs/phase_3_5a_v2.md` — V2 contract + 13 gates definition.
9. `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` —
   the engine to fix.
10. `src/ai_trade/backtest/strategies/letf_rotation.py` — other engine
    suspected of the same bug.
11. `reports/phase_3_5f/v2_l2_gayed_redo/report.md` +
    `reports/phase_3_5f/v2_l2_gayed_redo/cross_lib_report.md` —
    the evidence trail from this plan's creation session.
12. `scripts/run_phase3_5f_stage_a.py` +
    `scripts/run_phase3_5f_cross_lib.py` — existing runners, reusable.

---

## 4. Execution plan — 5 phases

Each phase ends with a hard **GATE**. Do not proceed past a gate
without passing the check or escalating.

### F0 — Confirmation cirúrgica do bug

**Objective:** prove or refute the lookahead bug with ≥ 3 surgical
unit tests whose expected output a third party can verify by hand.

**Deliverables:**

`tests/test_plano_a_lookahead_bias.py` with at least:

#### Test 1 — Flat-price series with forced regime flips
Build a SPY series where `close[i]` is constant = 100 for `i < 200`,
then jumps to 105 at `i = 200`, constant again at 105 for `i ≥ 200`.
QQQ series the same. GLD series constant 100 throughout. EMA100 warms
up around bar 100-150; at bar 200, SPY will cross above EMA → regime ON.

Expected under honest convention (shift): the +5% jump at bar 200 is
earned by the OFF weight (since signal flipped AT close of bar 200;
position change applies from bar 201 onward). Portfolio return at bar
200 = 0 (off-leg GLD flat) or GLD daily return (≈0 by construction).
Returns from bar 201 onward = 2× ×0 = 0 (price constant again).
Expected cumulative return ≈ 0%.

Expected under canonical (no-shift): the +5% jump at bar 200 is earned
by the ON weight (2× SPY and 2× QQQ both capturing +5% via look-ahead).
Portfolio return at bar 200 ≈ 2 × 0.5 × 0.05 + 2 × 0.5 × 0.05 = 0.10
(10%). Cumulative return ≈ +10%.

Assertion: `simulate_plano_a_rotation(...).daily_returns.sum() > 0.05`
would CONFIRM the bug (sum ≥ 0.10 expected). If the engine passes and
returns ~0, the bug is NOT present.

#### Test 2 — Single flip captures next-day return only
Build a series with known daily returns `r` such that signal flips ON
at close of bar 100 exactly. Inject a +3% return at bar 100 and +1% at
bar 101.

Expected honest: bar 100 pnl = w_{99}×r_{100} = 0×0.03 = 0 (still OFF
through bar 100); bar 101 pnl = w_{100}×r_{101} = 1×0.01 = 0.01 (ON
from bar 101 onward).

Expected canonical: bar 100 pnl = w_{100}×r_{100} = 1×0.03 = 0.03 (ON
weight times jump that triggered ON). Bar 101 pnl = 0.01.

Assertion: engine pnl at bar 100 must be 0 ± ε. If 0.03, bug confirmed.

#### Test 3 — Symmetric regime flipper → should render ~zero net
Mirror-symmetric series where regime flips every N bars. Under honest
alignment, wins and losses wash. Under canonical, wins cluster on
flip days.

Assertion: cumulative return over N × 10 bars is within ±2× the sum
of noise. Under canonical, cumulative >> 2× noise.

#### Test 4 — Determinístico against bt + vectorbt
Build a 200-bar series with pre-specified regime series. Feed same
inputs to `simulate_plano_a_rotation`, a bt adapter, and a vectorbt
adapter. Assert all three agree within 1e-6 on every daily return.

**Gate:** all 4 tests return the expected HONEST values from a patched
engine (F2 will do the patching; in F0 we ONLY write the tests —
they are expected to FAIL against the current engine). If the tests
don't discriminate (pass on current + patched), redesign them until
they do. Run the tests against the UNPATCHED engine to confirm they
fail in the expected direction.

**Also in F0:** Read `specs/phase_3_5a_v2.md` cover to cover searching
for any documentation of the `w_i × r_i` convention as intentional.
Grep git log for `"lookahead"`, `"shift"`, `"alignment"`, `"execution
timing"`. Record findings in
`docs/superpowers/findings/2026-04-22-engine-lookahead-confirmation.md`.

**Commit:** `test: add surgical lookahead-bias tests for plano_a engine`

**Deliverable path:**
- `tests/test_plano_a_lookahead_bias.py` (new)
- `docs/superpowers/findings/2026-04-22-engine-lookahead-confirmation.md` (new)

**If F0 confirms bug:** proceed to F1. **If F0 refutes bug (tests don't
fail against current engine as expected):** STOP, escalate, do not
proceed to F2. The user may have been misinformed by this plan.

---

### F1 — Scope mapping (inventário do raio do problema)

**Objective:** find every code path, report, and doc affected by the
lookahead bug. No guessing; grep-driven.

**Steps:**

1. Grep for every strategy file in `src/ai_trade/backtest/strategies/`
   that has the pattern `for bar_i` (or equivalent loop) with
   `np.sum(new_w[:n_assets] * per_asset)` or similar `w_i × r_i`
   compounding. List in doc.

2. Grep for every simulator/runner that imports these engines:
   - `grep -rln "simulate_plano_a_rotation\|simulate_letf_rotation" src/ scripts/ reports/`
   - Catalog by lead/phase.

3. Inventory reports affected:
   - `reports/phase3_5a_v2/*` — Plano A V2 (6 leads)
   - `reports/phase4_0/*` — Index CFD validation
   - `reports/phase_3_5b/*` — Plano B V4
   - `reports/phase_3_5c/*` — cross-lib (adapters are CLEAN; canonical
     runs were BUGGY — note this distinction)
   - `reports/phase_3_5d/*` — Plano B 3× LETF search
   - `reports/phase_3_5e/*` — Plano B breadth hunt

4. Inventory tests that assert specific biased numbers:
   - `grep -rln "sharpe.*2\.28\|cagr.*79\|79\.14\|2\.285" tests/`
   - `grep -rln "sharpe.*2\.25\|cagr.*37" tests/` (Plano B V4 historical)

**Deliverable:**
`docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md` with:

| Strategy module | Has bug? | Used by | Reports affected | Tests affected |
|---|:---:|---|---|---|
| `plano_a_leveraged_rotation.py` | YES | V2-L2 Gayed + Phase 4.0 | phase3_5a_v2/v2_l2_*, phase4_0/* | test_plano_a_leveraged_rotation.py |
| `letf_rotation.py` | ? (verify) | Plano B V4, 3.5d, 3.5e | phase_3_5b/*, phase_3_5d/*, phase_3_5e/* | test_letf_rotation.py |
| `tsmom.py` | ? (verify) | V2-L1 | phase3_5a_v2/v2_l1_* | ? |
| `afml_meta_label.py` | ? (verify) | V2-L3 | phase3_5a_v2/v2_l3_* | ? |
| `carver_rp.py` | ? (verify) | V2-L4 | phase3_5a_v2/v2_l4_* | ? |
| `equity_pairs.py` | ? (verify) | V2-L5 | phase3_5a_v2/v2_l5_* | ? |
| `vol_breakout.py` | ? (verify) | V2-L6 | phase3_5a_v2/v2_l6_* | ? |
| `portfolio_3leg.py` | ? | Plano B 3-leg | phase_3_5b/3_leg_* | ? |

**Gate:** inventory document committed. User reviews before F2.

**Commit:** `docs: map scope of engine lookahead bias`

---

### F2 — Fix + regression tests

**Objective:** patch every engine with the bug, update tests that
assert biased numbers to assert honest numbers, keep pytest green.

**Principle:** single logical fix per file, cleanly separable in git
diff. No opportunistic refactors.

**Steps:**

1. For each file in F1 inventory with `YES` bug:
   - Locate the return-compounding line.
   - Replace `new_w[bar_i] * ret[bar_i]` with `prev_weights[bar_i] * ret[bar_i]`.
   - Or equivalently: compute `prev_weights[bar_i] = weights.shift(1).fillna(0)[bar_i]`.
   - Ensure cost/swap/switch accounting remains consistent (switches
     are still detected from prev_w vs new_w comparison — this logic
     is about weight decisions at decision-close, unchanged).
   - The FIRST bar's return is 0 (no prior weight to apply).

2. Update `tests/test_plano_a_leveraged_rotation.py`:
   - `test_leverage_applied_when_risk_on`: after shift, steady-drift
     mean daily return ≈ 0.002 still holds (steady state). Keep.
   - `test_off_regime_tlt_contributes_to_return`: off-regime drift
     attribution unchanged under shift (similar reasoning). Keep.
   - Add assertions that the F0 surgical tests now PASS.

3. Update any other tests that asserted specific CAGR/Sharpe:
   - `tests/test_letf_rotation.py` — rerun with shift; update expected
     numbers where they were biased. Document the old → new delta in
     commit body.
   - Same for other strategies found in F1.

4. Run full pytest. Target: 914 (or more if F0 added tests) all green.

5. Run `scripts/run_phase3_5f_stage_a.py` and
   `scripts/run_phase3_5f_cross_lib.py` again — expect canonical to now
   match libs within ±0.5pp CAGR. This is the de facto regression
   test for the fix.

**Deliverables:**
- Patched `src/ai_trade/backtest/strategies/*.py`
- Updated `tests/test_*.py`
- Updated `reports/phase_3_5f/v2_l2_gayed_redo/*` (new run with honest
  engine confirming cross-lib concordance)
- Pytest proof: `logs/phase3_5f_f2_pytest.log`

**Gate:** pytest green, cross-lib concordance confirmed on V2-L2 config.
User reviews diff before F3.

**Commit:** `fix(backtest): shift weight×return alignment to remove lookahead bias`

---

### F3 — Plano A honest winner hunt

**Objective:** determine if any of the 6 Plano A V2 leads passes the
13 V2 gates + cross-lib + Stage-2 concordance under the honest engine.

**Priority order (highest re-eval probability first):**

1. **V2-L2 Gayed `gayed_ema100_L2_off_gld`** — was the winner. Most
   likely to degrade below gates under honest math (projected OOS Sharpe
   ~0.7-1.0). If it survives, Plano A survives with reduced numbers.

2. **V2-L4 Carver RP blend** — was DEAD because "blend dilui L2 alpha
   79% → 16%". If L2's honest alpha is 15%, the blend may end up
   comparable to or better than L2 alone. Worth re-evaluating.

3. **V2-L1 TSMOM monthly** — was DEAD by swap drag over long holds
   (40-160d). Lookahead bias contributes a constant inflation per flip,
   but flips are MUCH rarer here. May reveal a modest honest edge that
   was masked by the cost story. Likely still DEAD.

4. **V2-L3 AFML meta-label** — was DEAD by meta-labeling being a filter
   not an edge, with residual CAGR 2.5% below costs. Honest numbers
   even lower. Expected still DEAD.

5. **V2-L5 Kalman pairs** — was DEAD by zero ADF-cointegration pairs
   found. This is a structural, pre-engine failure. Honest vs buggy
   math doesn't change "no pairs found". Confirmed still DEAD.

6. **V2-L6 vol-breakout Donchian** — was DEAD with 12/12 OOS Sharpe
   NEGATIVE. Removing lookahead bias typically makes negatives MORE
   negative, not positive. Confirmed still DEAD.

**For each re-evaluated lead:**

1. Locate the iter runner (e.g. `scripts/iter_v2_l2_run_config.py` for
   V2-L2). Verify it's picking up the F2-patched engine.
2. Run all configs in the lead's registry over IS/OOS/FWD splits.
3. Apply all 13 V2 gates from `specs/phase_3_5a_v2.md §gates`:
   - PBO < 0.5 (if grid ≥ 5 configs)
   - DSR p < 0.05 (if grid ≥ 5 configs)
   - Bootstrap 99.9% CI low > 0 (single-config fallback)
   - OOS Sharpe ≥ 2.0
   - OOS CAGR ≥ 30%
   - OOS MaxDD ≥ -25%
   - FWD Sharpe > 0
   - WF 6/8 profitable, max window DD ≤ 25%
   - Median hold ≥ 3 days
   - IR vs SPY ≥ 0.5
   - (remaining 3 gates per spec)
4. Cross-lib concordance: ≥ 2/3 of {bt, vectorbt, backtrader} within
   ±3pp CAGR of canonical.
5. Stage-2 data concordance: Tiingo `adj_close` + testfolio
   `SPYSIM/QQQSIM/GLDSIM` within ±1pp CAGR on OOS/FWD (IS can diverge
   due to pre-2004 GLD caveat).
6. Write `reports/phase_3_5f/honest_revalidation/<lead>/AGGREGATE.md`
   with PASS/FAIL verdict.

**Stopping rule within F3:** as soon as the **first lead passes all
gates**, STOP and escalate to user for winner confirmation review. Do
NOT continue auto-evaluating remaining leads without user go-ahead.

**Deliverables per lead:**
- `reports/phase_3_5f/honest_revalidation/v2_l<N>_<lead>/AGGREGATE.md`
- Daily returns parquets per config
- Summary JSON with metrics
- Gate checklist

**Gate at end of F3:**

Three outcomes possible:

- **(a) V2-L2 passes honest:** Plano A winner confirmed with corrected
  numbers. Proceed to F4 documentation. Prepare for Phase 4 paper
  trading path.
- **(b) Different lead passes honest:** new winner promoted. User
  reviews before F4 documentation. May require spec update.
- **(c) All 6 leads fail honest:** Plano A has NO known winner. Stop
  F3. Escalate to user with these explicit options:
  - **V3 framework:** design a new 7th lead family (not repeating any
    of the 6 tested). Requires new spec.
  - **Phase-6 fallback:** use honest Gayed 1× (unleveraged) as Plano A
    proxy — passes gates at ~11%/yr CAGR but below CDI. Accept as
    "passive-like active" with no real alpha.
  - **Abandon Plano A:** per mandate §7 V2 binding rule ("if V2
    produces 0 PASS → abandon permanently"). Reallocate bucket A
    capital to Plano C per mandate §4.7. No V3.
  - **Wait and retry:** freeze Plano A, revisit Plano B grid completion
    (Phase 3.5e c06-c12) with honest engine — maybe the 7 untested
    Plano B families reveal a cross-strategy winner. THIS IS OUT OF
    SCOPE unless user lifts the Plano B stand-by.

**Critical:** do NOT auto-promote any winner. Every candidate passes
through user review before mandate §7 gets a new entry.

---

### F4 — Documentation, mandate update, forensic closure

**Objective:** produce the auditable record of what happened. Update
living docs so the next session is not confused about canonical
numbers.

**Deliverables:**

1. `jornada/2026-04-22-engine-lookahead-bug.md` — the
   narrative-in-human-language of what went wrong and how it was
   caught. Include analogy (coin flip after seeing result). Reference
   the 4 surgical tests.

2. `jornada/2026-04-22-plano-a-honest-revalidation.md` — results
   of F3. Per-lead PASS/FAIL, new winner (if any), honest metrics
   replacing buggy baseline.

3. `docs/strategies/plano_a_v2_l2_gayed_cfd.md` — header banner:
   - If V2-L2 passes honest: "HONEST NUMBERS (post 2026-04-22 fix):
     Sharpe X.XX / CAGR YY% / MDD -ZZ%. Original buggy numbers preserved
     at §9 for history."
   - If V2-L2 fails honest: "REJECTED: look-ahead bias in prior
     engine. See jornada/2026-04-22-*. New winner: [name] OR no winner
     (Plano A abandoned per mandate §7)."

4. `docs/investment-mandate.md §7` — NEW entry:
   | 2026-04-22 | Engine lookahead bias discovered + fixed. V2-L2 [surveillance / rejected / confirmed]. Phase 3.5b-d-e Plano B reports marked as BIASED FORENSIC. [winner status]. | Shift-convention enforcement. `[advances_fin_ml, p.31-34]` | <commit hash> |

5. `docs/CURRENT_STATE.md` — update top-level "current winner" line if
   it exists.

6. `docs/superpowers/findings/2026-04-22-engine-lookahead-*.md` —
   technical deep-dive for future agents.

7. `jornada/README.md` — update "Onde estamos hoje" and "O que vem a
   seguir" sections.

8. Add `ENGINE_BIAS_FORENSIC.md` README inside each affected historical
   report directory (NOT modifying the JSON/MD contents, just adding a
   banner file):
   - `reports/phase3_5a_v2/ENGINE_BIAS_FORENSIC.md`
   - `reports/phase4_0/ENGINE_BIAS_FORENSIC.md`
   - `reports/phase_3_5b/ENGINE_BIAS_FORENSIC.md`
   - `reports/phase_3_5c/ENGINE_BIAS_FORENSIC.md`
   - `reports/phase_3_5d/ENGINE_BIAS_FORENSIC.md`
   - `reports/phase_3_5e/ENGINE_BIAS_FORENSIC.md`
   
   Each banner: "Reports in this directory were produced by a version
   of the simulation engine that contained a look-ahead bias (fixed
   2026-04-22, commit <hash>). Reported CAGR/Sharpe values OVERSTATE
   the honest strategy performance. Do not cite these numbers as
   truth. See docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md
   and jornada/2026-04-22-engine-lookahead-bug.md for context."

**Gate:** pytest green, all docs linted (no broken links), user reads
docs and approves language.

**Commit chain:**
- `test: surgical lookahead tests (F0)`
- `docs: scope of engine lookahead bias (F1)`
- `fix(backtest): remove lookahead bias from return compounding (F2)`
- `test: update affected tests with honest expected values (F2 continuation)`
- `feat(backtest): honest re-validation of Plano A V2 leads (F3)`
- `docs: record engine bias fix + plano A re-validation verdict (F4)`

---

## 5. Operational details

### 5.1 Running things

- Python: `.venv/bin/python`
- Pytest: `.venv/bin/pytest -q`
- Branch: `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422` (already
  checked out). DO NOT merge to main until all phases pass.

### 5.2 Existing helpers to reuse

- `scripts/run_phase3_5f_stage_a.py` — ready to re-run V2-L2 after F2
  fix. Compares Tiingo raw close / Tiingo adj_close / testfolio SIM.
- `scripts/run_phase3_5f_cross_lib.py` — bt/vectorbt/backtrader engine
  replication test. After fix, canonical should match libs.
- `scripts/iter_v2_l2_run_config.py` — canonical V2-L2 runner. After
  F2 fix, will produce honest numbers to a new directory.
- `src/ai_trade/backtest/data/testfolio_loader.py` — for Stage-2 TR
  data.
- `src/ai_trade/backtest/grid/letf_rotation_b1c.py` —
  `bootstrap_sharpe_ci`, `walk_forward_verdict_from_returns`,
  `compute_split_metrics` all reusable.
- `reports/phase_3_5c/cross_lib/adapters/` — bt, vectorbt, backtrader
  adapters (already honest/shift-aware per Phase 3.5c evidence).

### 5.3 Data paths (for reference)

- Tiingo daily prices: `data/tiingo/daily/prices/{TICKER}.parquet`
  (columns: open, high, low, close, adj_close, volume).
- Testfolio cache: `data/testfolio/cache/history.parquet` (columns:
  SPYSIM, QQQSIM, GLDSIM, SSOSIM, QLDSIM, UPROSIM, TQQQSIM, UGLSIM,
  ZROZSIM). 1986-01-02 → 2026-04-17.
- Reference prices (cross-lib long format):
  `reports/phase_3_5c/cross_lib/data/reference_prices.parquet`
  (columns: date, ticker, open, high, low, close, volume).

### 5.4 Windows (V2 canonical — do not change)

- IS: 2001-05-14 → 2017-12-31
- OOS: 2018-01-01 → 2023-12-31
- FWD: 2024-01-01 → 2026-04-14

### 5.5 Winner definition (single source of truth for F3)

A "winner" for Plano A must satisfy ALL of the following under the
**honest (post-F2) engine** with cost + swap + slippage applied:

1. **Bootstrap 99.9% CI lower bound > 0** on OOS Sharpe AND full-period
   Sharpe. `[advances_fin_ml, p.196-202]`
2. **OOS Sharpe ≥ 2.0** (can be relaxed to ≥ 1.5 with user approval if
   border-passing).
3. **OOS CAGR ≥ 30%** net of costs (mandate §2 Plano A target).
   Relaxation to ≥ CDI BR (~13%) requires explicit user sign-off per
   mandate §2.
4. **OOS MaxDD ≥ −25%** (mandate §5 binding cap, no relaxation).
5. **FWD Sharpe > 0** on 2024-2026 (forward stress).
6. **Walk-forward 8 windows: ≥ 6/8 profitable, max window DD ≤ 25%**.
7. **Median hold ≥ 3 trading days** (spec §1, avoid HF contamination).
8. **IR vs SPY ≥ 0.5** on OOS.
9. **Cross-lib concordance ≥ 2/3** of {bt, vectorbt, backtrader} within
   ±3pp CAGR of canonical on OOS.
10. **Stage-2 data concordance** Tiingo `adj_close` vs testfolio SIM
    within ±1pp CAGR on OOS + FWD.
11. (If grid ≥ 5 configs) **PBO < 0.5** via CSCV 10-block.
    `[advances_fin_ml, p.208-211]`
12. (If grid ≥ 5 configs) **DSR p-value < 0.05** on winner OOS Sharpe.
    `[advances_fin_ml, p.196-202]`
13. **Cost sensitivity:** multiplying cost bps × 2 still produces OOS
    Sharpe > 1.0. Robust to Pepperstone rate-card variance.

Any candidate missing ANY of these 13 conditions is NOT a winner. Zero
bypass. `docs/investment-mandate.md §2.5`.

---

## 6. The mission — single-sentence

**Find a Plano A strategy that survives all 13 gates in §5.5 under
the honest (post-2026-04-22-fix) simulation engine.** If none exists,
escalate to user with the three options in F3 gate (c).

---

## 7. Final notes for the executing session

- You are picking up work from session 2026-04-22. Your context at start
  is empty — read §3 Required Reading FIRST.
- This is manual validation work. Do NOT trigger `self_improve_loop.sh`.
- User prefers terse updates + clear escalation at each F-gate.
- If you hit an unknown situation (test fails unexpectedly, numerical
  artifact, unclear convention), ESCALATE rather than improvise. The
  user has been burned by autonomous decisions before (see V1 "abandon
  Plano A" decision corrected by user intervention —
  `jornada/2026-04-18/23-phase3.5a-v2-WINNER-humana.md`).
- Every decision cites `[book.slug, p.X]` per CLAUDE.md Regra 2.
- Every jornada entry follows `jornada/README.md` format.
- Every commit follows Conventional Commits.
- The final `jornada/2026-04-22-plano-a-honest-revalidation.md` is the
  outcome document that matters most — write it as if the user has no
  memory of prior conversations.

---

## 8. Citations

- Look-ahead bias detection + two-stage replication protocol:
  `[advances_fin_ml, p.31-34]`.
- PBO CSCV: `[advances_fin_ml, p.208-211]`.
- DSR / bootstrap: `[advances_fin_ml, p.196-202]`.
- Walk-forward 6/8 gate: `[advances_fin_ml, ch.11]`.
- Gayed regime rotation (V2-L2 thesis source):
  `[leverage_for_the_long_run, Gayed, p.11-14, p.16-17, p.21]`.
- Carver retail cost model + hold discipline:
  `[systematic_trading, p.185-188]`.
- Kelly f/2 leverage cap + ruin: `[math_money_mgmt, Vince]`,
  `[leverage_space, Vince]`.

---

**End of plan.**
