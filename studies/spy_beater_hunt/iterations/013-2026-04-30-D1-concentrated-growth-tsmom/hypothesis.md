# spy_beater_hunt iter 013 — D1 Concentrated Growth + TSMOM Gate (QQQ + 6/12m time-series momentum)

**Date**: 2026-04-30
**Type**: Post-impossibility Tier 3 sanity check on KILL #33 (architectural ceiling) — **6th distinct architectural family**
**Slug**: `D1-concentrated-growth-tsmom`
**Status of hunt entering this iter**: `closed_no_winner` (iter 011 IMPOSSIBILITY_RESULT, iter 012 5-family reinforcement)

---

## Why this iter exists (context)

Iter 011 declared IMPOSSIBILITY_RESULT and fired KILL #33 (structural
architectural ceiling at score 67 across 4 control families). Iter 012
tested D2 (5th family, stacked equity heavy) and reinforced KILL #33
(D2 best score 52 << 67). Iter 012 final report explicitly noted:

> "Tier 3 D1 (concentrated growth + monthly momentum) and C2
> (CAPE-timing) remain untested. Per KILL #36 firing, additional Tier
> 3 testing would NOT change the architectural-ceiling conclusion. ...
> If user requests further sanity checks (D1 or C2), template would
> be similar 3-config sanity-check format with KILL #39+ pre-committed."

This iter tests **D1** as the **6th distinct architectural family** to
either:
- **Reinforce KILL #33** (6th family also caps ≤ 67 → architectural
  ceiling claim strengthened from 5-family to 6-family evidence).
- **Invalidate KILL #33** (D1 surprisingly scores ≥ 75 → ceiling claim
  was premature; hunt reopens for iter 014+).

D1 is the most architecturally distinct from the 5 closed families:
- A1/A3 SPY-track LRS: regime-gated leverage on **SPY** via **200d SMA** (daily SMA cross)
- A2 TQQQ-track LRS: regime-gated 3× leverage on **NDX** via **200d SMA**
- B1/B2 HFEA: leveraged barbell (UPRO + TMF, no gate)
- C1 vol-target: dynamic leverage on SPY based on realised vol
- D2: stacked equity heavy (NTSX + UPRO + AVUV, no gate)
- **D1 (this iter)**: concentrated growth on **NDX** at **low/no leverage** (1× QQQ or 2× QLD) with **time-series momentum (TSMOM) gate** — single-anchor signal `price[t] > price[t - lookback]` per Moskowitz/Ooi/Pedersen 2012, distinct from SMA-cross.

D1 isolates whether the **TSMOM gate family** (single past-price anchor)
plus **moderate-leverage NDX concentration** breaks the score-67 ceiling
that A1/A2 (SMA gates) hit.

---

## Hypothesis

**H₁ (primary)**: A TSMOM-gated concentrated-growth strategy (1× QQQ
or 2× QLD with `price > price[t-126d]` 6-month gate, IEF when off)
**cannot exceed score 67** on the spy_beater rubric on (lh_56y,
spy_real). TSMOM is structurally similar to SMA cross at long lookbacks
(both detect trend) and offers no decisive structural advantage; NDX
without 3× LETF lacks CAGR uplift.

**H₂ (secondary)**: TSMOM lookback dose-response is **non-monotonic**
or **shallow** in (3m, 6m, 12m) range — short lookback (3m) whipsaws
in choppy markets (raises trade frequency, costs CAGR); long lookback
(12m) lags major reversals (deeper crash drawdowns). 6m is the
literature canonical (Faber GTAA / AQR TSMOM).

**H₃ (tertiary)**: 2× QLD + 6m TSMOM gate **fails MDD bar** OR has
Sharpe **strictly worse** than 1× QQQ + 6m TSMOM, because daily-reset
decay (~1-2%/y on 2× LETF) erodes the advantage of moderate leverage
over plain NDX.

---

## Configs (3 — keep cumulative n_trials low)

| name                  | underlying ON | OFF asset | lookback | thesis                                                                |
|-----------------------|--------------:|----------:|---------:|------------------------------------------------------------------------|
| d1_qqq_6m_tsmom       | 100% QQQSIM   | 100% IEFSIM| 126 days | Canonical 6m TSMOM (Faber GTAA equivalent). 1× NDX concentration.    |
| d1_qqq_12m_tsmom      | 100% QQQSIM   | 100% IEFSIM| 252 days | Long-lookback TSMOM (Moskowitz canonical 12m). Lag risk.            |
| d1_qld_6m_tsmom       | 100% QLDSIM   | 100% IEFSIM| 126 days | 2× QQQ moderate leverage + 6m TSMOM. Tests LETF decay vs gate lift.  |

All 3 use:
- **signal_ticker**: `QQQSIM` (NDX total return cache)
- **lookback_days**: per table
- **lag_days**: 1 (T+1 execution lag, no peek-ahead)
- **filter**: `momentum` (NEW gate type, added to lrs_engine.py via TDD)

**Cumulative n_trials**: prior 38 (iter 012) + 3 = **41**.

---

## Pre-committed KILL conditions (NEW for this iter)

KILLs #1-#38 already declared. Numbering continues at #39.

### KILL #39 (D1 reinforces KILL #33 — 6th family caps ≤ 67)

**Definition**: If best D1 config score ≤ 67, the architectural
ceiling claim from iter 011 is **strengthened from 5-family to
6-family evidence**. Hunt remains CLOSED.

**Trigger**: `max_score_d1 ≤ 67` AND no config PASSES all 3 bars with
score ≥ 75.

**Action if FIRED**: update BASE_MEMORY frontmatter
`architectural_ceiling: confirmed_6_families` and reinforce iter 011
verdict. F1+SPLIT remains deploy fallback.

### KILL #40 (sanity-check breaks ceiling — KILL #33 INVALIDATED)

**Definition**: If best D1 config score ≥ 75 with all 3 bars met, KILL
#33 was premature; ceiling is NOT structural. Hunt **REOPENS**.

**Trigger**: `max_score_d1 ≥ 75 AND all 3 bars met`.

**Action if FIRED**: revert BASE_MEMORY status to `hunting`, plan iter
014+ extending D1 sensitivity sweep (lookback × leverage × off-asset),
document KILL #33 retraction in FINAL_REPORT_spy_beater_failed.md.

### KILL #41 (TSMOM lookback monotonic — direction-closing dose-response)

**Definition**: Sharpe is **monotonic** (strictly positive OR strictly
negative) across lookback dose 6m → 12m on the QQQ track on BOTH
datasets. If monotonic POSITIVE on lookback (longer is always better),
the explored 6/12m range may be on the wrong side; if monotonic
NEGATIVE, longer lookback is uniformly worse and the direction is
sub-optimal at literature canonical 12m.

**Trigger**: `Sharpe(d1_qqq_6m) > Sharpe(d1_qqq_12m)` on both datasets
OR `Sharpe(d1_qqq_6m) < Sharpe(d1_qqq_12m)` on both datasets.

**Action if FIRED**: document direction has clear lookback preference;
no further D1 sensitivity sweep needed.

---

## Expected outcomes (priors)

| config           | expected mean CAGR | expected mean MDD | expected score | bar pass? |
|------------------|-------------------:|------------------:|---------------:|-----------|
| d1_qqq_6m_tsmom  | 11-14%             | 30-50%            | 55-65          | likely 3/3|
| d1_qqq_12m_tsmom | 10-13%             | 35-55%            | 50-62          | maybe 3/3 |
| d1_qld_6m_tsmom  | 14-18%             | 40-60%            | 55-65          | maybe 2/3 |

Most likely outcome: **all 3 configs score 50-67**, KILL #39 fires,
ceiling reinforced across 6 families. ~3% chance any config exceeds 75
(KILL #40 path — would require TSMOM to materially outperform SMA
which has weak literature support).

---

## INCOMPLETE flags

- **TSMOM in literature**: Moskowitz/Ooi/Pedersen 2012 documented
  TSMOM at MONTHLY frequency on monthly returns. This iter implements
  TSMOM on DAILY price-vs-past-price — operationally similar
  (`price[t] > price[t-126d]` ↔ "6m return > 0") but daily check
  rather than month-end. Standard practitioner adaptation.
- **QQQSIM coverage**: testfolio cache QQQSIM starts ~1985 (pre-NDX
  inception 1985-10-01) — synthesised from earlier NDX components.
  Coverage matches lh_56y (1986+) and spy_real (2003+).
- **QLDSIM coverage**: testfolio cache QLDSIM starts ~1985 with daily
  decay modelling.
- **No new synth required**: QQQSIM, QLDSIM, IEFSIM all in cache.
- **PBO N=3 warning**: CSCV statistically unstable with N<4; pre-existing
  infra warning, unchanged by this iter.
- **NEW module**: `momentum_gate` added to lrs_engine.py via TDD (3
  new tests for no-peek + initial-lookback + lookback param). Wired
  into `_lrs_returns_from_spec` via `filter="momentum"` and
  `lookback_days` field. Backwards-compat preserved: existing `sma`
  / `ema` / `sma_band` / `ema_band` filters unchanged.

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA on
  LETFs canonical; D1 tests TSMOM as alternative gate family.
- Moskowitz, Ooi, Pedersen (2012) "Time Series Momentum" J. Financial
  Economics 104(2): 228-250 — TSMOM canonical 12m. Literature support
  for D1 gate type.
- Faber 2007 "A Quantitative Approach to Tactical Asset Allocation"
  (GTAA) — 10-month SMA / 6-month TSMOM equivalence at monthly
  frequency.
- `[advances_fin_ml, p.31-34]` factor framework — D1 isolates the
  *gate-family* dimension distinct from leverage / regime axes
  already explored.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 41;
  preserves statistical integrity for verdict.
- `[advances_fin_ml, p.208-211]` PBO grid-level — selection bias
  controlled at 3-config × 2-dataset = 6-cell grid.
- `[advances_fin_ml, p.196-202]` bootstrap CI — gate G6 99.9% CI low
  > 0 required.
- HFEA Bogleheads 2019 — falsified iter 008/009; D1 here uses no
  bonds at all in ON sleeve, only IEF in OFF.

---

## What this iter does NOT test

- **D1 with TQQQ 3× leverage** — overlaps A2 TQQQ-track which already
  capped at 67. Adding TSMOM gate to TQQQ would not unlock structural
  uplift.
- **C2 CAPE-timing** — flagged as low-credibility per
  PROMISING_DIRECTIONS.md ("CAPE has been 'high' for 20+ years");
  remains untested. Could be future iter 014 if user requests further
  closure.
- **TSMOM with 1m or 24m lookback** — only canonical 6m and 12m tested
  to constrain n_trials.
- **TSMOM + crisis-alpha (KMLM/DBMF) in OFF sleeve** — keeps OFF as
  pure IEF for clean comparison to A1/A2 (which also used IEF as
  default OFF).

---

## Decision tree post-iter

| outcome                           | action                                             | KILL fired |
|-----------------------------------|----------------------------------------------------|-----------:|
| All 3 configs score ≤ 67          | Reinforce KILL #33 across 6 families. Hunt CLOSED. | #39        |
| Any config scores 68-74           | Document; hunt remains CLOSED at 67-cap            | none       |
| Any config scores ≥ 75 + 3 bars   | INVALIDATE KILL #33. Reopen hunt for iter 014+.    | #40        |
| Sharpe monotonic over 6m→12m      | TSMOM dose-response direction closed               | #41        |

Most likely path: **KILL #39 fires** (all configs ≤ 67), KILL #40
NOT fired, KILL #41 may or may not fire. Hunt remains CLOSED. F1+SPLIT
incumbent fallback unchanged. Mandate §1 100% Plano C unchanged.

---

## Why this iter is worth doing despite hunt being CLOSED

iter 011 INCOMPLETE flags listed Tier 3 D1/C2/D2 as untested. Iter 012
tested D2 (5th family, score 52). D1 closes the remaining Tier 3 with
LITERATURE backing (Moskowitz et al. is widely cited; Faber GTAA is
practitioner-canonical). Closing both D1 and D2 strengthens the
negative-result policy claim from "5 families, 56 cumulative iters" to
"6 families, 57 cumulative iters" — robust enough for mandate §1
confirmation.

DSR cumulative_n_trials = **41** after this iter; worst p-value bar at
p=0.05 still has comfortable margin (iter 012 worst was 9.40e-3 << 0.05).
