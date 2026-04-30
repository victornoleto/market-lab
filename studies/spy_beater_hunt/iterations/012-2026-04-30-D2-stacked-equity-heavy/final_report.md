# spy_beater_hunt iter 012 — Final Report — `D2-stacked-equity-heavy`

**Tier**: **MARGINAL** — `score=52/100`, `winner_conditions_met=True`

**Strict bars** (CAGR-anchored, spy_beater rubric):
- CAGR bar (mean ≥ 13.80%): PASS (mean = 12.23%)
- MDD bar (mean ≤ 40.85%): PASS (mean = 52.65%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Primary citation**: [risk_parity, ch.5, p.10] Carlson capital-efficient stacking + [advances_fin_ml, p.31-34] factor framework (AVUV SCV factor) + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay (UPRO leg) + [advances_fin_ml, p.222-223] DSR cumulative_n_trials

---

## Selected config: `d2_ntsx_avuv`

Spec:

```json
{
  "type": "static",
  "weights": {
    "NTSXSIM": 0.5,
    "AVUVSIM": 0.5
  }
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 0.799 | 12.88% | 52.65% | 6/7 | 1.75e-05 |
| **spy_real** | 0.678 | 11.59% | 52.65% | 6/7 | 9.40e-03 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| d2_ntsx_avuv | 0.799 | 0.678 |
| d2_ntsx_upro_avuv | 0.625 | 0.608 |
| d2_upro_avuv | 0.586 | 0.572 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 14 | 30 | mean = 12.23%, bar = 11.21% |
| 2. MDD vs SPY | 6 | 20 | mean = 52.65%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 9.40e-03, n_trials = 38 |
| 5. Sharpe | 2 | 10 | mean = 0.738 |
| 6. Robustness | 7 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 58.3% | 52.65% |
| 10y | 65.6% | 52.65% |
| 15y | 81.7% | 52.65% |
| 20y | 81.0% | 52.65% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 36

## INCOMPLETE flags

- **Stale bar text in template header**: the "CAGR bar (mean ≥
  13.80%)" / "MDD bar (mean ≤ 40.85%)" labels above are 3-dataset-era
  (lh_56y + vt_real + ndx_real) numbers. The actual evaluation uses
  2-dataset bars (lh_56y + spy_real): **CAGR ≥ 11.21%, MDD ≤ 55.17%**
  per the 2026-04-29 methodology refactor (BASE_MEMORY frontmatter).
  All 3 bars correctly evaluated against the 2-dataset framework:
  d2_ntsx_avuv mean CAGR 12.23% ≥ 11.21% PASS; mean MDD 52.65% ≤ 55.17%
  PASS; gates cross_met=True PASS.
- **NTSX synth via proxies blueprint** (90% SPY + 60% IEF − 50%
  CASHX): no daily-reset decay (NTSX is futures-stacked, not LETF —
  realistic). 1986+ coverage matches lh_56y.
- **AVUV synth via avuv_synth_returns_from_cache**: 1926+ coverage,
  uses Avantis SCV synthesised from FF data 1926-2019.
- **PBO N=3 warning**: CSCV statistically unstable with N<4; this is
  pre-existing infra warning unchanged by this iter.

## Lesson

### Tier MARGINAL 52/100 — all 3 bars met but score WORST in entire hunt

iter 012 tested D2 (5th distinct architectural family: pure stacking
+ factor tilt + LETF, no regime gate). **Selected config**
`d2_ntsx_avuv` (50% NTSXSIM + 50% AVUVSIM) passes all 3 strict bars
(CAGR 12.23% ≥ 11.21%, MDD 52.65% ≤ 55.17%, gates cross_met) but
scores **52/100** — the WORST among the 11 substantive iters of the
hunt. This is **15pts BELOW closest-to-winner (iter 006/007 = 67)**
and **8pts BELOW iter 010 vol-target (60)**, the previous worst
PROMISING.

### KILL conditions outcomes

- **KILL #36 (D2 reinforces KILL #33 — 5th family caps ≤ 67) FIRED**:
  best D2 score = 52 << 67 ceiling. Architectural ceiling claim from
  iter 011 **strengthened from 4-family to 5-family evidence**. Hunt
  remains CLOSED, status: closed_no_winner, KILL #33 (architectural
  ceiling) reinforced.
- **KILL #37 (sanity-check breaks ceiling) NOT FIRED**: no D2 config
  scored ≥ 75 (best 52); no D2 config met all 3 bars with score ≥ 75.
  KILL #33 stands. Hunt does NOT reopen.
- **KILL #38 (pure equity LETF + factor fails MDD bar) FIRED**:
  `d2_upro_avuv` mean MDD = **85.48%** >> 55.17% bar. **Massively**
  fails — confirms pure leveraged equity + factor concentrate has
  catastrophic MDD without regime gate or stacking. Establishes that
  **regime gate OR stacking with bonds/cash is a NECESSARY component**
  for the spy_beater MDD bar; pure LETF + factor is structurally
  subordinate. Even d2_ntsx_upro_avuv (mixed stacking + LETF + factor)
  hits MDD 76.91% — adding stacking helps but not enough at 1.65x
  notional concentrated equity.

### Per-config table (mean across datasets)

| config              | mean CAGR | mean MDD | mean Sharpe | bar pass? | score |
|:--------------------|----------:|---------:|------------:|:---------:|------:|
| **d2_ntsx_avuv**    | **12.23%**| **52.65%**| **0.738**  | **3/3 ✓** | **52**|
| d2_ntsx_upro_avuv   | 15.22%    | 76.91%   | 0.617       | 2/3 (MDD✗)|  ~50  |
| d2_upro_avuv        | 15.66%    | 85.48%   | 0.579       | 2/3 (MDD✗)|  ~48  |

### Closest-to-winner gap (vs iter 006 a6_tqqq_split_kmlm30_tlt10)

| metric             | iter 006 (closest)| iter 012 (d2_ntsx_avuv) | gap     |
|:-------------------|------------------:|------------------------:|--------:|
| score              | 67                | **52**                  | **−15** |
| mean CAGR          | 17.33%            | 12.23%                  | −5.10pp |
| mean MDD           | 49.73%            | 52.65%                  | −2.92pp |
| mean Sharpe        | 0.759             | 0.738                   | −0.021  |
| CAGR pts           | 25                | 14                      | **−11** |
| MDD pts            | 7                 | 6                       | −1      |
| Sharpe pts         | 2                 | 2                       | 0       |
| Gates pts          | 13                | 13                      | 0       |
| DSR pts            | 10                | 10                      | 0       |
| Robustness pts     | 10                | 7                       | **−3**  |

D2 trades −5pp CAGR and −3 robustness pts for marginal MDD parity
within rubric. Sharpe lift over closest-to-winner is **negative
−0.021** despite stacking baseline. Robustness drop is the
multi-horizon CAGR pass-rate (5y window only 58.3%, 10y 65.6% — D2
underperforms SPY in many bull-window slices because AVUV factor lags
and NTSX 90/60 caps equity exposure at 0.95×).

### Direction implications

- **D2 family CLOSED at score 52**. Pure stacking + factor + LETF
  architecture is **decisively below 67-ceiling** even before considering
  regime-gate framework lift. Not a viable spy_beater path.
- **5-family architectural ceiling diagnostic strengthened**:
  | family                  | best score | best Sharpe |
  |:------------------------|-----------:|------------:|
  | A2 TQQQ-track LRS       | **67**     | 0.804       |
  | A1/A3 SPY-track LRS     | 66         | 0.744       |
  | B1/B2 HFEA barbell      | 63         | 0.739       |
  | C1 vol-target           | 60         | 0.721       |
  | **D2 stacked equity** ⬅ | **52**     | 0.738       |
- D2 is **furthest below ceiling** of all families — confirms that
  removing the regime gate framework does NOT unlock structural lift;
  the regime gate is a **necessary** component for any score-65+ in
  this rubric.
- **No KMLM/DBMF/TLT crisis-alpha tested in D2** because D2's premise
  was *pure equity stacking + factor*. Adding crisis-alpha would
  collapse D2 back into the C1/B2 architectural neighborhood already
  tested.

### Cross-family knowledge added by iter 012

1. **Regime gate is necessary, not contingent** for spy_beater rubric
   score ≥ 60. Pure stacking + factor (no gate) tops at 52.
2. **Pure LETF + factor MDD is catastrophic**: d2_upro_avuv MDD
   85.48% (lh_56y) — 2008 GFC + 2022 stress compound on 1.5× concentrated
   equity exposure. Even more extreme than iter 008 HFEA classical
   (67.48% MDD).
3. **Stacking (NTSX) without leverage helps MDD modestly** but caps
   CAGR at 12% range — confirms F1+SPLIT (which is bonds-heavy stacking)
   already represents the stacking architecture's score-ceiling
   neighborhood (~59 estimated for F1+SPLIT in spy_beater rubric per
   iter 011 KILL #35 analysis).
4. **AVUV factor tilt does NOT lift CAGR significantly over SPY in
   1986+ window**: d2_ntsx_avuv CAGR 12.23% ≈ SPY 11.21% + ~1pp factor
   premium. Modest lift consistent with `[advances_fin_ml, p.31-34]`
   factor framework but well below the 16-22% needed for score-67+
   in rubric.

### Surprising findings

1. **Robustness drops sharply in shorter windows** (5y 58.3%, 10y
   65.6%) — D2 underperforms SPY in low-vol bull regimes because
   AVUV (SCV) lags growth-led rallies (e.g., 2017-2019, 2023-2024).
   F1+SPLIT had a similar problem in long_term_portfolio. Stacking +
   factor architecture is **structurally low-beta in growth regimes**.
2. **Adding UPRO to NTSX+AVUV (d2_ntsx_upro_avuv)** kills MDD
   (52.65% → 76.91%) but only adds 3pp CAGR (12.23% → 15.22%).
   Sharpe **drops** from 0.738 to 0.617. UPRO daily-reset decay +
   2008 LETF wipeout dominates the architecture.
3. **Sharpe inversion at LETF dose**: monotonic NEGATIVE Sharpe as
   UPRO weight grows in D2 (0.738 → 0.617 → 0.579). Mirrors HFEA
   iter 008 finding: at >1× equity notional with no regime gate, more
   leverage = WORSE Sharpe.

### Path to 90 (D2 architecture)

**Architecturally unreachable**. Best D2 score 52 → gap 38 to score
90. Maximum plausible single-criterion lift: CAGR +10 (14→24, requires
mean CAGR 18%+ unrealistic without LETF) + MDD +12 + Sharpe +2 + Rob
+3 = **+27 pts** at independent-maxima. Optimistic ceiling 79 < 90.
Real Pareto-feasible ceiling ≈ 65 (CAGR↔MDD trade-off from D2 grid
visible: more LETF gives CAGR but kills MDD).

D2 ceiling **lower than 4 prior families** — confirms KILL #33 conclusion
that score 90 is structurally unreachable in spy_beater rubric.

### Updated 5-family architectural ceiling diagnostic

- **Best score across 5 control families = 67** (iter 006/007, A2)
- **D2 worst score** at 52 — adding it to the family-ceiling table
  does NOT change the upper bound (67) but **lowers the
  family-min-ceiling from 60 to 52**, widening the spread.
- Optimistic Pareto-loose ceiling = 67 + 19 = 86 < 90 (unchanged)
- Real Pareto-feasible ceiling ≈ 75 (unchanged)
- **Score-90 path: ARCHITECTURALLY UNREACHABLE** (KILL #33 reinforced)

### Why this iter was worth doing despite hunt being CLOSED

iter 011 INCOMPLETE flags listed Tier 3 D1/C2/D2 as untested. KILL
#33 fired on 4-family evidence; testing a 5th family was a **due
diligence step** that:
- **Confirmed KILL #33** (5th family scores 52, well below 67)
- **Confirmed KILL #38** (regime-gate or duration-stacking is
  necessary for MDD bar; pure LETF + factor MDD = 85%)
- **Strengthened the negative-result policy claim** from "4 families
  tested, 53 cumulative iters" to "5 families tested, 56 cumulative
  iters" — robust enough for mandate §1 confirmation.

DSR cumulative_n_trials = **38**, worst p-value = 9.40e-03 << 0.05.
Statistical confidence preserved.

### Suggested iter 013+ (none — hunt remains CLOSED)

Tier 3 D1 (concentrated growth + monthly momentum) and C2
(CAPE-timing) remain untested. Per KILL #36 firing, additional Tier 3
testing would NOT change the architectural-ceiling conclusion — D1 is
similar architecture to A2 TQQQ-track (already capped at 67) and C2
has 20+ years of out-of-sample failure. Recommendation: hunt remains
CLOSED.

If user requests further sanity checks (D1 or C2), template would be
similar 3-config sanity-check format with KILL #39+ pre-committed.

### Citations validated by iter 012

- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking —
  NTSX 90/60 stacking confirmed; mean CAGR 12.23% with NTSX+AVUV
  matches F1+SPLIT neighborhood; F1+SPLIT remains deploy fallback.
- `[advances_fin_ml, p.31-34]` factor framework — AVUV SCV factor
  premium ~1pp over SPY in 1986+ window, consistent with FF
  literature; insufficient for score-67+ in spy_beater rubric.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 38, worst
  p = 9.40e-03 << 0.05 bar; statistical confidence preserved.
- `[advances_fin_ml, p.208-211]` PBO grid-level — N=3 warning
  pre-existing; CSCV unstable at small N but cross-config selection
  bias controlled at iter level.
- `[advances_fin_ml, p.196-202]` bootstrap CI — gate G6 99.9% CI low
  > 0 (passed for d2_ntsx_avuv).
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LETF decay —
  UPRO leg confirmed catastrophic without regime gate (d2_upro_avuv
  MDD 85.48%).
- HFEA Bogleheads 2019 — D2 confirms regime-specific issue: pure
  equity stacking + LETF without bonds is structurally worse than
  HFEA classical (which at least has TMF buffer).
- Avantis 2019 AVUV mandate — SCV factor ~1pp premium over SPY in
  1986+ window confirmed; not enough for spy_beater bar.

### Status

**`spy_beater_hunt: status: closed_no_winner`** REMAINS as of 2026-04-30.

- Total iters: 12 / 50 target (closed at iter 011, sanity-checked at iter 012)
- Cumulative n_trials: 38
- KILL #33 (architectural ceiling) **REINFORCED across 5 families**
- KILL #36 fired (D2 ≤ 67)
- KILL #37 NOT fired (no D2 config ≥ 75)
- KILL #38 fired (pure equity LETF + factor MDD > 55%)
- F1+SPLIT incumbent fallback deploy-ready
- Mandate §1 100% Plano C unchanged

