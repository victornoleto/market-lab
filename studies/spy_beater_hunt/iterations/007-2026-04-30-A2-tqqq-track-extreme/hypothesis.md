# spy_beater_hunt iter 007 — Hypothesis — `A2-tqqq-track-extreme`

**Slug**: `A2-tqqq-track-extreme`
**Created**: 2026-04-30
**Cumulative n_trials**: prior 23 + 3 this iter = **26**
**Continuation rationale**: per iter 006 final_report "Suggested iter 007", the
TQQQ-track + KMLM30 + TLT10 (`a6_tqqq_split_kmlm30_tlt10`) became the new
closest-to-winner at score 67. The binding constraint is criterion 2 (MDD),
mean 49.73% driven by lh_56y MDD 62.39% (dot-com synth). Path to score 90
requires +6-13 pts on MDD axis. The iter 005 SPY-track sweep showed Sharpe
rising monotonic positive 0%→40% KMLM with concave dose-response curve —
this iter mirrors that sweep on the TQQQ-track to find the inflection (or
confirm monotonicity through 40%).

---

## Hypothesis

**H₁ (KMLM dose extension)**: Pushing KMLM dose from 30% → 35% → 40% on the
TQQQ-track lifts mean Sharpe AND lowers mean MDD monotonically (mirrors iter
005 SPY-track 30%→35%→40% which showed monotonic positive Sharpe in BOTH
datasets). Specifically, lh_56y MDD should drop from 62.39% (KMLM30+TLT10)
toward ~50-55% at KMLM40+TLT10, materially shrinking the binding constraint
on score criterion 2.

**H₂ (TLT dose alternative)**: As an orthogonal lever, pushing TLT from 10%
→ 15% (keeping KMLM 30%) tests whether adding more duration on top of the
proven KMLM30 base is steeper than adding more crisis-alpha. If TLT 15%
beats KMLM 35% on MDD with comparable CAGR cost, future iters should sweep
TLT instead of KMLM.

**H₃ (architecture preserves bars)**: All 3 configs continue passing the
3 strict bars (CAGR ≥ 11.21%, MDD ≤ 55.17%, gates ≥ 5/5 cross-met) since
each is a small extension of the iter 006 winner architecture.

Citation: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed regime gate;
`[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking — the
SPY-track dose-response was monotonic positive Sharpe through 40% KMLM
(iter 005 KILL #16/#17 BOTH not fired), and `[advances_fin_ml, p.31-34]`
factor framework supports treating NDX as a higher-vol US-Large-growth
tilt where the same crisis-alpha lever applies with potentially deeper
relief (since MDD baseline is higher).

---

## Configs (3, naming `a7_tqqq_*`)

### 1. `a7_tqqq_split_kmlm35_tlt10` — push KMLM to 35%

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {
    "TQQQSIM": 0.275,
    "QLDSIM": 0.275,
    "KMLMSIM": 0.35,
    "TLTSIM": 0.10
  },
  "off_weights": {"IEFSIM": 1.0},
  "signal_ticker": "QQQSIM",
  "lag_days": 1
}
```

Tests: H₁. Direct analog of iter 005 KMLM35-on-SPY-track ported to NDX.
TQQQ+QLD share the equity sleeve at 27.5% each (= 55% leveraged equity);
KMLM 35%, TLT 10%.

### 2. `a7_tqqq_split_kmlm40_tlt10` — push KMLM to 40%

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {
    "TQQQSIM": 0.25,
    "QLDSIM": 0.25,
    "KMLMSIM": 0.40,
    "TLTSIM": 0.10
  },
  "off_weights": {"IEFSIM": 1.0},
  "signal_ticker": "QQQSIM",
  "lag_days": 1
}
```

Tests: H₁ extension. Matches iter 005 `a5_kmlm40` dose on SPY-track. TQQQ+QLD
at 25% each (= 50% leveraged equity); KMLM 40%, TLT 10%.

### 3. `a7_tqqq_split_kmlm30_tlt15` — push TLT to 15% (alternative lever)

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {
    "TQQQSIM": 0.275,
    "QLDSIM": 0.275,
    "KMLMSIM": 0.30,
    "TLTSIM": 0.15
  },
  "off_weights": {"IEFSIM": 1.0},
  "signal_ticker": "QQQSIM",
  "lag_days": 1
}
```

Tests: H₂. Holds KMLM at 30% (same as iter 006 winner) but pushes TLT
+5pp. TQQQ+QLD at 27.5% each. Tests duration-on-top steepness vs
crisis-alpha extension.

---

## Pre-committed KILL conditions

KILL numbering continues from #21 (last used in iter 006). New: #22, #23.

### KILL #6 (standing — CAGR floor)

If best config across the iter has CAGR mean < 11.21% (the spy_beater bar),
the strategy class is structurally subordinate to SPY buy-hold. Direction
CLOSED.

**Citation**: `WINNER_AND_RANKING.md` Bar 1.

### KILL #19 (standing — TQQQ-track wipeout)

If any of the 3 configs has MDD > 70% on EITHER dataset, the dot-com
(lh_56y) regime breaks the regime-gate thesis at TQQQ-leverage levels even
with extended crisis-alpha. Direction A2 TQQQ-track extreme CLOSED — would
require pivot to QLD-only (2× NDX).

### KILL #22 — TQQQ-track KMLM dose inflection

If `a7_tqqq_split_kmlm40_tlt10` Sharpe < `a7_tqqq_split_kmlm35_tlt10` Sharpe
on BOTH datasets, the KMLM dose-response curve inflects between 35% and 40%
on the TQQQ-track. Sub-direction A2_kmlm_extreme CLOSED at 35%; iter 006's
KMLM30+TLT10 retains as practical baseline.

**Rationale**: iter 005 SPY-track sweep found NO inflection through 40% KMLM
(monotonic positive Sharpe in BOTH datasets), but the TQQQ-track has higher
volatility baseline and KMLM may saturate sooner since the equity sleeve is
already smaller in absolute notional terms.

### KILL #23 — TLT subordinate to KMLM on TQQQ-track

If `a7_tqqq_split_kmlm30_tlt15` MDD on lh_56y ≥ `a7_tqqq_split_kmlm35_tlt10`
MDD on lh_56y, KMLM is the steeper MDD lever on the TQQQ-track. Future iters
prefer extending KMLM dose. (Inverse: if TLT15 has materially LOWER MDD than
KMLM35 with comparable CAGR drag, future iters should sweep TLT instead.)

**Rationale**: SPY-track iter 003-005 found KMLM scales better at 25-30%
than TLT does at 15-20%. The TQQQ-track may invert this ordering since
NDX-equity correlation with bonds differs from SPY's.

---

## Expected outcomes

| config                          | expected CAGR mean | expected MDD mean | expected Sharpe |
|---------------------------------|-------------------:|------------------:|----------------:|
| a7_tqqq_split_kmlm35_tlt10      | 16-18%             | 44-50%            | 0.78-0.85       |
| a7_tqqq_split_kmlm40_tlt10      | 15-17%             | 41-47%            | 0.80-0.88       |
| a7_tqqq_split_kmlm30_tlt15      | 16-18%             | 45-51%            | 0.75-0.82       |

**Score outlook** (selected ≈ a7_kmlm40_tlt10 if H₁ holds):
- 1. CAGR 30 × clamp((0.16 - 0.05)/0.15, 0, 1) ≈ 22 pts (vs iter 006's 25)
- 2. MDD 20 × clamp((0.55 - 0.43)/0.40, 0, 1) ≈ 6 → 8-10 pts (vs iter 006's 7)
- 3. Gates likely 13 (cross_met)
- 4. DSR n=26 worst p ≈ 5e-3 → 10 pts
- 5. Sharpe ≈ 0.83 → 3 pts
- 6. Robustness ≈ 9-10 pts
- 7. Extra 0
- **Total expected**: ~67-72 (similar or slightly above iter 006)

**Score-90 path**: structurally improbable in this iter. The CAGR-MDD
tradeoff curve in iter 005 SPY-track showed +5 KMLM ≈ −0.4pp CAGR / −2.5pp
MDD — the TQQQ-track equivalent would lift criterion 2 by ~2 pts at cost
of ~3 pts on criterion 1 (net ~−1). This iter's value is the **direction
mapping** — confirm/reject monotonicity on TQQQ-track and steepness ordering.

---

## INCOMPLETE flags

1. **TQQQSIM/QLDSIM testfolio synths**: pre-2010 (TQQQ inception) and
   pre-2006 (QLD inception) is testfolio synth (NDX × 3 / NDX × 2 with
   daily-reset decay). Real-world TQQQ has higher trading drag, bid-ask
   spread, and tracking error than synth assumes (~0.5-1.5% additional
   annual drag plausible in stress regimes).
2. **QQQSIM signal data**: real QQQ ETF inception 1999-03; pre-1999 in
   `lh_56y` is NDX index synth. The 200d SMA gate timing in 1986-1999
   sub-window depends on testfolio's NDX synth fidelity.
3. **lh_56y window 1986-1999**: NDX synth-only zone. The 2000-02 dot-com
   regime is captured but TQQQSIM behavior there is fully synthetic.
4. **spy_real window (2003+) misses 2000-02 dot-com**: only `lh_56y`
   captures it via synth. Per-dataset MDD divergence (lh_56y 60+ vs
   spy_real 35-40%) is the dot-com tail, not a measurement artifact.
5. **LRS rebalance instantaneous, no transaction costs**: same caveat
   as all prior iters. 4-ticker daily rebalance for blend configs.
6. **PBO at N=3 (warning emitted)**: CSCV statistically unstable below
   N=4. PBO informative-only at this iter level; cumulative n_trials=26
   cross-iter grid carries the anti-overfit weight (DSR worst p target
   < 0.05).

---

## Next-iter sketch (depending on outcome)

- **If score lifts past 70 AND H₁/H₂ both confirmed (no KILL fires)**: extend
  with `a8_tqqq_split_kmlm45_tlt10` and/or KMLM35+TLT15 blend in iter 008.
- **If KILL #22 fires (KMLM inflects between 35% and 40%)**: lock KMLM35
  as TQQQ-track ceiling; pivot iter 008 to TLT-extension (KMLM35+TLT15)
  or off-regime upgrade (KMLM in OFF leg).
- **If KILL #23 fires (TLT15 ≥ KMLM35 MDD on lh_56y)**: KMLM is steeper.
  Continue KMLM extension. Drop TLT-sweep direction.
- **If score regresses (KMLM too aggressive, CAGR drag dominates)**:
  TQQQ-track scoring saturated near 67. Pivot iter 008 to **B1 HFEA
  classical** (TMFSIM synth required — TDD per INFRASTRUCTURE.md).
- **If KILL #19 fires (any MDD > 70%)**: TQQQ-track CLOSED entirely
  even with extended crisis-alpha. Pivot to QLD-only 2× NDX or B1 HFEA.

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA regime
  gate on LETFs; framework asset-agnostic; iter 006 confirmed transfer
  from SPY to QQQ.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking; iter
  005 confirmed KMLM dose-response monotonic positive Sharpe through 40%
  on SPY-track; this iter tests the same on TQQQ-track.
- `[advances_fin_ml, p.31-34]` cross-lib + factor framework (NDX as
  US-Large-growth tilt of SPY).
- `[advances_fin_ml, p.222-223]` DSR with cumulative n_trials=26.
- `[advances_fin_ml, p.208-211]` PBO via CSCV (informative at N=3).
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha — KMLM 30-40%
  range validated as Sharpe-improving zone.
- studies/_archive/ema_sma_threshold_nasdaq_real (prior project sweep —
  found SMA200 best on QQQ 2010-2024; relevant precedent).
