# spy_beater_hunt iter 006 — Hypothesis — `A2-tqqq-track-split`

**Slug**: `A2-tqqq-track-split`
**Created**: 2026-04-30
**Cumulative n_trials**: prior 20 + 3 this iter = **23**
**Pivot rationale**: per iter 005 final_report Option B, the A3 KMLM dose lever is structurally
limited within the CAGR-anchored scoring rubric (CAGR axis 30 pts dominates MDD axis 20 pts).
BASE_MEMORY direction_status `A2_TQQQ_track: NOT YET RUN` — needs a structurally different
lever for a shot at score ≥ 90. This iter pivots from SPY-track (UPRO+SSO) to NDX-track
(TQQQ+QLD) while preserving the proven LRS architecture from iter 004 closest-to-winner
(`a4_lrs_split_kmlm30`).

---

## Hypothesis

**H₁**: A 200d SMA regime gate on QQQ rotating 50% TQQQ + 50% QLD ↔ 100% IEF (analog of
iter 001 baseline `a1_lrs_split` ported to NDX) achieves higher mean CAGR than the UPRO-track
baseline (16.23%) at comparable MDD, due to NDX's higher long-run CAGR. The 200d SMA on QQQ
should catch the 2000-02 dot-com peak before TQQQ-equivalent gets wiped.

**H₂**: The KMLM crisis-alpha lever validated on the SPY-track (iter 003-005 monotonic
positive Sharpe through 40% KMLM dose) **generalizes** to the NDX-track. Adding 30% KMLM
on top of split-TQQQ should reduce MDD with bounded CAGR drag, mirroring the SPY-track
dose-response curve.

**H₃**: The duration-on-top-of-trend finding from iter 005 (`a5_kmlm30_tlt10` matched/beat
`a4_kmlm30` Sharpe in both datasets) generalizes — adding 10pp TLT on top of KMLM30 inside
the NDX-track should improve Sharpe at small CAGR cost.

Citation: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed regime gate (originally
applied to SPY but the framework is asset-agnostic; Gayed himself documents the mechanism
on multiple risk-asset classes including NASDAQ);
`[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking (KMLM dose validated on
SPY-track; testing transfer to NDX-track);
`[advances_fin_ml, p.31-34]` factor framework (NDX is a US-Large-growth tilt of SPY's
broad-market exposure; same regime-gating logic should hold).

---

## Configs (3, naming `a6_tqqq_*`)

### 1. `a6_tqqq_split_lrs` — pure A2 baseline (analog of iter 001 winner)

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {"TQQQSIM": 0.5, "QLDSIM": 0.5},
  "off_weights": {"IEFSIM": 1.0},
  "signal_ticker": "QQQSIM",
  "lag_days": 1
}
```

Tests: H₁. Establishes the TQQQ-track CAGR/MDD ceiling with no crisis-alpha. Direct analog
of iter 001 `a1_lrs_split` (50% UPRO + 50% SSO ON, 100% IEF OFF).

### 2. `a6_tqqq_split_kmlm30` — port iter 004 closest-to-winner

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {"TQQQSIM": 0.35, "QLDSIM": 0.35, "KMLMSIM": 0.30},
  "off_weights": {"IEFSIM": 1.0},
  "signal_ticker": "QQQSIM",
  "lag_days": 1
}
```

Tests: H₂. Direct port of iter 004 `a4_lrs_split_kmlm30` (35% UPRO + 35% SSO + 30% KMLM)
to the NDX side. Validates KMLM dose-response transfer.

### 3. `a6_tqqq_split_kmlm30_tlt10` — port iter 005 Sharpe-best

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.0,
  "on_weights": {
    "TQQQSIM": 0.30,
    "QLDSIM": 0.30,
    "KMLMSIM": 0.30,
    "TLTSIM": 0.10
  },
  "off_weights": {"IEFSIM": 1.0},
  "signal_ticker": "QQQSIM",
  "lag_days": 1
}
```

Tests: H₃. Direct port of iter 005 `a5_lrs_split_kmlm30_tlt10` (30% UPRO + 30% SSO +
30% KMLM + 10% TLT) to the NDX side.

---

## Pre-committed KILL conditions

KILL numbering continues from #18 (last used in iter 005). New: #19, #20, #21.

### KILL #6 (standing — CAGR floor)

If best config across the iter has CAGR mean < 11.21% (the spy_beater bar), the strategy
class is structurally subordinate to SPY buy-hold. Direction CLOSED.

**Citation**: `WINNER_AND_RANKING.md` Bar 1.

### KILL #19 — TQQQ-track wipeout

If any of the 3 configs has MDD > 70% on EITHER dataset, the dot-com (lh_56y) or GFC
(spy_real) era carnage breaks the regime-gate thesis at TQQQ-leverage levels.
Direction A2 TQQQ-track CLOSED — TQQQ requires either deeper KMLM (> 30%) or moves to
QLD-only (2× NDX) at lower leverage to be viable.

**Rationale**: NDX -78% during 2000-02 with daily-reset 3× LETF would mean TQQQ -99%+
absent a working gate. If our 200d SMA gate misses enough of that drawdown, MDD blows out.

### KILL #20 — TQQQ-track no CAGR uplift vs SPY-track

If all 3 configs have CAGR mean < 16.23% (iter 001 `a1_lrs_split` UPRO-track baseline),
the NDX-track adds vol but no CAGR — the whole pivot rationale (use NDX higher long-run
CAGR to lift score 1_cagr above the SPY-track 17-19 pts plateau) fails.

Direction A2 TQQQ-track CLOSED in favor of returning to SPY-track variants.

### KILL #21 — KMLM doesn't generalize from SPY-track to TQQQ-track

If `a6_tqqq_split_kmlm30` Sharpe < `a6_tqqq_split_lrs` Sharpe on BOTH datasets, the KMLM
crisis-alpha lever proven on SPY-track does NOT transfer to NDX-track. Sub-direction
A2_kmlm CLOSED but `a6_tqqq_split_lrs` still scored as the A2 baseline.

**Rationale**: NDX has different correlation structure with crisis-alpha (KMLM trend-
following tends to short equity in crashes; works for SPY but TQQQ's 3× exposure may
overpower the hedge). If KMLM doesn't help, the dose-response transfer hypothesis (H₂) fails.

---

## Expected outcomes

| config                       | expected CAGR mean | expected MDD mean | expected Sharpe |
|------------------------------|-------------------:|------------------:|----------------:|
| a6_tqqq_split_lrs            | 18-24%             | 45-55%            | 0.60-0.75       |
| a6_tqqq_split_kmlm30         | 16-20%             | 32-42%            | 0.70-0.85       |
| a6_tqqq_split_kmlm30_tlt10   | 15-19%             | 30-38%            | 0.75-0.90       |

**Score outlook** (selected ≈ a6_tqqq_split_kmlm30):
- 1. CAGR 30 × clamp((0.18 - 0.05)/0.15, 0, 1) ≈ 26 pts (vs iter 004's 19)
- 2. MDD 20 × clamp((0.50 - 0.37)/0.40, 0, 1) ≈ 6.5 → 7 pts (vs iter 004's 12; NDX MDD wider)
- 3. Gates likely 12-13 (similar to prior iters)
- 4. DSR n=23 worst p ≈ 5e-3 → 10 pts
- 5. Sharpe ≈ 0.78 → 2 pts
- 6. Robustness ≈ 9 pts
- 7. Extra 0
- **Total expected**: ~66-73 (similar to iter 004 closest-to-winner, slightly higher upside)

**Score-90 path**: if MDD comes in at 30% (best case), 2_mdd lifts to 10 pts. Combined
with 26 pts CAGR + 13 gates + 10 DSR + 2 Sharpe + 9 robustness = 70. Still gap to 90.
The clean 90+ path likely needs both higher CAGR AND lower MDD simultaneously — possibly
achievable if H₂ transfers cleanly.

---

## INCOMPLETE flags

1. **TQQQSIM/QLDSIM testfolio synths**: pre-2010 (TQQQ inception) and pre-2006 (QLD
   inception) is testfolio synth (NDX × 3 with daily-reset decay; NDX × 2 for QLD).
   Real-world TQQQ has higher trading drag, bid-ask spread, and tracking error than
   synth assumes (~0.5-1.5% additional annual drag plausible for TQQQ in stress regimes).
2. **QQQSIM signal data**: real QQQ ETF inception 1999-03; pre-1999 in `lh_56y` window
   is NDX index synth. The 200d SMA gate timing in 1986-1999 sub-window depends on
   testfolio's NDX synth fidelity.
3. **lh_56y window 1986-1999**: NDX synth-only zone. The 2000-02 dot-com regime is
   present but TQQQSIM's behavior there is fully synthetic (no real trading data
   captures the actual 3× LETF performance during that crash because TQQQ didn't exist).
4. **spy_real window (2003+) misses 2000-02 dot-com**: only `lh_56y` captures it via synth.
5. **LRS rebalance instantaneous, no transaction costs**: same caveat as all prior iters.
   Daily 4-ticker rebalance for the blend config implies daily fixed-weight rebalance.
6. **PBO will be N=3 (warning emitted)**: CSCV statistically unstable below N=4. PBO
   informative-only at this iter level; the cumulative n_trials=23 cross-iter grid
   carries the anti-overfit weight.

---

## Next-iter sketch (depending on outcome)

- If KILL #19 fires (MDD wipeout): close A2 TQQQ-track → pivot to **B1 HFEA classical**
  (need to build TMFSIM synth) or **A2 lower-leverage QLD-only** variant.
- If KILL #20 fires (no CAGR uplift): close A2 → revisit C1 vol-targeting or B1 HFEA.
- If KILL #21 fires (KMLM doesn't generalize): keep A2 baseline `a6_tqqq_split_lrs`,
  scrap KMLM transfer thesis, try TLT-only on top of TQQQ-track.
- If all KILLs miss and score lifts to 70+: extend with `a7_tqqq_split_kmlm35` /
  `a7_tqqq_split_kmlm40` to find inflection (analog of iter 005 sweep on SPY-track).
- If score still capped at ~70: pivot to **B1 HFEA classical** in iter 007 (needs
  TMFSIM synth — TDD required).

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA regime gate on LETFs;
  framework is asset-agnostic.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking (KMLM dose lever).
- `[advances_fin_ml, p.31-34]` cross-lib + factor framework (NDX as US-Large-growth tilt).
- `[advances_fin_ml, p.222-223]` DSR with cumulative n_trials=23.
- `[advances_fin_ml, p.208-211]` PBO via CSCV (informative at N=3).
- studies/_archive/ema_sma_threshold_nasdaq_real (prior project sweep — found
  SMA200 best on QQQ 2010-2024; relevant precedent).
