# Engine look-ahead bias — F0 surgical confirmation (2026-04-22)

**Phase:** 3.5f §F0
**Plan:** `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`
**Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`
**Status:** **BUG CONFIRMED.** Proceed to F1 (scope inventory).

---

## 1. What F0 set out to prove

Hypothesis (from plan §1.2): the canonical simulator
`src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` at
`simulate_plano_a_rotation` multiplies the weight decision at bar `i`
by the return from `close[i-1] → close[i]` on the SAME bar. Because
the regime signal at bar `i` is computed from `close[i]` (via
`px > EMA(close)_i` etc.), the product `w_i × r_i` is an oracle bet —
the weight "knows" the return that just happened.

Honest convention: `w_{i-1} × r_i` (or equivalently `w_i × r_{i+1}`).

---

## 2. Prior-art grep — was this convention documented anywhere?

### 2.1 `git log --all --oneline | grep -iE 'lookahead|look-ahead|shift|alignment'`

```
7c280a2 docs: map scope of engine lookahead bias
e910919 test(phase-3.5c): bt adapter contract + signal alignment
```

`7c280a2` is the F1 scope-map doc already written during the plan
authoring session (lives at HEAD). `e910919` is the Phase 3.5c bt
adapter contract test, where the shift convention was written correctly
on the library-adapter side (which is exactly why the canonical engine
stood out as the outlier in Phase 3.5c cross-lib).

**No commit, anywhere in history, documents `w_i × r_i` as an intentional
choice.** There is zero prior paper trail treating the canonical
convention as deliberate. The nearest prior mention of the problem is
the speculative `specs/phase_3_5b_winners_validation.md` line 26:

> validar que não há bug de look-ahead, bar-alignment, etc.

That was a generic validation checklist item, not a proof.

### 2.2 `grep -rnE 'lookahead|look-ahead' specs/`

```
specs/phase_4_0_index_cfd_validation.md:267:| NDX TR loader introduzir
  lookahead bug | Média (20%) | Validate via unit test: reconstructed
  NDX close matches QQQ up to dividend, ex-div dates match published
  NDX calendar |
specs/phase_3_5b_winners_validation.md:26: validar que não há bug de
  look-ahead, bar-alignment, etc.
specs/phase_3_5b_winners_validation.md:39: quebrar (p.ex. winner revela
  look-ahead bias), é melhor descobrir
```

All three are *risk callouts*, not specifications of intended timing
behaviour. The canonical engine was simply never held against a
surgical weight-vs-return alignment test until now.

### 2.3 `grep -rnE 'shift|alignment' specs/backtest_phase2*.md specs/phase_3_5a_v2.md`

```
specs/backtest_phase2.md:152: (paid data / universe shift / pivot)...
specs/backtest_phase2.md:262: Universe shift (Nasdaq100 instead of SPX500)...
specs/backtest_phase2.md:346: shifted landscape
specs/backtest_phase2_5_ehlers.md:551: shifted landscape
```

All four hits are about **universe shifts / landscape shifts**, not
weight-vs-return timing shifts. No spec defines the canonical engine
convention.

**Conclusion of §2:** the specs do NOT sanction `w_i × r_i`. The bug
is a silent implementation drift, not a documented modelling choice.
This matches plan §1.2's framing ("classic Oracle bet").

---

## 3. Pytest evidence — the 4 surgical tests all FAIL as expected

File: `tests/test_plano_a_lookahead_bias.py` (new, this commit).
Command: `.venv/bin/pytest tests/test_plano_a_lookahead_bias.py -v`.

Summary (verbatim):

```
tests/test_plano_a_lookahead_bias.py::test_flat_then_jump_flat_no_lookahead_captures_zero_pnl FAILED [ 25%]
tests/test_plano_a_lookahead_bias.py::test_single_flip_captures_only_next_day_return FAILED [ 50%]
tests/test_plano_a_lookahead_bias.py::test_symmetric_flipper_washes_to_near_zero_under_honest FAILED [ 75%]
tests/test_plano_a_lookahead_bias.py::test_canonical_matches_bt_vectorbt_within_1e6 FAILED [100%]
========================= 4 failed, 1 warning in 2.43s =========================
```

Per-test assertion output (verbatim):

```
E AssertionError: Engine captured the +5% jump on the same bar the
  regime flipped ON — this is look-ahead. Cumulative daily_returns =
  0.1000; expected ≤ 0.01 under honest w_{i-1} × r_i convention.
E assert 0.10000000000000009 <= 0.01
```

```
E AssertionError: Engine earned 0.0300 on the SAME bar the regime
  flipped ON (bar 250, +3% same-day move). Honest convention pays this
  return to the PREVIOUS weight (OFF → 0). Look-ahead bias.
E assert 0.030000000000000027 < 0.005
```

```
E AssertionError: Symmetric regime-flipper path produced a large
  POSITIVE cumulative return (0.8083) under the engine. The path is
  mean-reverting by construction; a positive drift is only possible if
  the engine's ON weights are capturing the same-bar up-move that
  triggered the ON decision — look-ahead.
E assert 0.8083061180762081 < 0.05
```

```
E AssertionError: Canonical engine daily returns disagree with
  bt/vectorbt/numpy references by up to 3.506096e-02 (tolerance 1e-6).
  Three independent compounding paths agree on w_{i-1} × r_i;
  canonical alone uses w_i × r_i → look-ahead bias.
E assert 0.035060956208306626 < 1e-06
```

Each failure is numerically consistent with the exact bug arithmetic
predicted in plan §1.3 (e.g. Test 1 buggy cumulative = `2 legs × L=2
× budget=0.5 × jump=0.05 = +0.10` ✓; Test 2 flip-bar pnl =
`L=1 × budget=1 × jump=0.03 = 0.03` ✓). The four tests discriminate
unambiguously between the canonical and honest conventions — there is
no parameter setting under which `w_i × r_i` can produce these honest
expected values.

---

## 4. Conclusion — bug confirmed

**The look-ahead bias described in plan §1.2 is PRESENT in
`src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` at
line 462** (inside the per-bar loop spanning lines 406-466):

```python
# Line 406:  for bar_i, ts in enumerate(common_idx):
# Line 409:      new_w = np.zeros(len(cols), dtype=float)
# Line 411:          state = regime_df.iloc[bar_i][t]     # signal @ close[i]
# Line 413:              new_w[k] = L * budget_per_asset  # weight @ close[i]
# Line 459-462:
#     per_asset = np.where(np.isnan(ret_vals[bar_i]), 0.0, ret_vals[bar_i])
#     on_ret = float(np.sum(new_w[:n_assets] * per_asset))  # ← LOOK-AHEAD
# Line 463-464:
#     off_r = off_vals[bar_i] ...
#     off_ret = float(new_w[-1] * off_r)                    # ← same issue off-leg
```

The `new_w` vector, freshly computed at bar `i` from information
contained in `close[i]`, is multiplied by `per_asset = ret[bar_i] =
close[bar_i] / close[bar_i - 1] - 1` — a return that also embeds
`close[i]`. This rewards the weight decision with the same close-to-
close move that triggered it.

Correct convention (to be applied in F2): replace `new_w` with
`prev_weights` in both the `on_ret` and `off_ret` computations, or
equivalently compute returns from `weights.shift(1) × returns`. Under
that convention all four tests in `tests/test_plano_a_lookahead_bias.py`
will pass; three independent libraries (`bt`, `vectorbt`, `backtrader`)
plus a hand-written numpy reference have already confirmed the shift
convention during Phase 3.5c cross-lib validation (see Phase 3.5c bt
adapter commit `e910919`).

**No escalation trigger fired.** F0's confirmation matches plan §1.2-1.3
exactly. Proceed to F1 (already committed at `7c280a2` — "docs: map
scope of engine lookahead bias") → then F2 (the fix).

---

## 5. Citations

* Look-ahead bias detection + two-stage replication protocol:
  `[advances_fin_ml, p.31-34]`.
* Weight alignment / signal timing in walk-forward backtests:
  `[advances_fin_ml, ch.11]`.
* Gayed regime rotation (V2-L2 thesis):
  `[leverage_for_the_long_run, p.11-14, p.16-17, p.21]`.
