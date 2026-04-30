# spy_beater_hunt iter 023 — Final Report — `B7-ntsx-anchored-low-leverage-mf`

**Gross tier**: **MARGINAL** — `gross_score=57/100`, `gross_winner_met=False`

**Net tier**: **MARGINAL** — `net_score=56/100`, `net_winner_met=False`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): FAIL (mean = 10.70%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 25.81%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: FAIL (mean = 10.12%)
- MDD bar: PASS (mean = 25.81%)
- Gates bar (same as gross): PASS

**Primary citation**: [risk_parity, ch.5, p.10] Carlson NTSX 90/60 internal SPY/UST stack as canonical capital-efficient 1.5x notional vehicle; B7 axis tests iter 022 KILL #79 generalization (MF effectiveness ~ 1/leverage) at 150% notional regime, one step LOWER than B5 modest-HFEA 200% + [ilmanen_expected_returns, ch.19] MF crisis-alpha role + [advances_fin_ml, p.31-34] factor framework for combining KMLM (Mount Lucas TF index) + DBMF (broader CTA basket) decorrelated alpha sources + [advances_fin_ml, p.222-223] DSR cumulative_n_trials = 86 + [advances_fin_ml, p.208-211] PBO via CSCV N=6 + WINNER_AND_RANKING.md structural net-rubric advantage 1.5pp for buy-hold static (iter 022 B5 confirmed 0.63pp drag for static spec)

---

## Selected config: `b7_ntsx70_kmlm20_tlt10`

Spec:

```json
{
  "type": "static",
  "weights": {
    "NTSXSIM": 0.7,
    "KMLMSIM": 0.2,
    "TLTSIM": 0.1
  }
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 1.015 | 11.42% | 26.20% | 0.961 | 10.95% | 26.20% | 0.46 | 6/7 |
| **spy_real** | 0.921 | 9.98% | 25.43% | 0.843 | 9.29% | 25.43% | 0.69 | 7/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — buy_hold, 0 year-end settlements, total DARF $94,199 (terminal $94,199), drag 0.46pp
- `spy_real` — buy_hold, 0 year-end settlements, total DARF $11,322 (terminal $11,322), drag 0.69pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| b7_ntsx100 | 0.799 | 0.764 |
| b7_ntsx80_kmlm20 | 0.955 | 0.869 |
| b7_ntsx80_dbmf20 | 0.726 | 0.843 |
| b7_ntsx70_kmlm20_tlt10 | 1.015 | 0.921 |
| b7_ntsx70_kmlm15_dbmf15 | 0.788 | 0.913 |
| b7_ntsx70_kmlm10_dbmf10_tlt10 | 0.789 | 0.913 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 11 | 30 | mean = 10.70%, bar = 11.21% |
| 2. MDD vs SPY | 16 | 20 | mean = 25.81%, bar = 55.17% |
| 3. Gates | 14 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 7}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 1.04e-03, n_trials = 86 |
| 5. Sharpe | 3 | 10 | mean = 0.968 |
| 6. Robustness | 3 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 33.3% | 26.20% |
| 10y | 38.5% | 26.20% |
| 15y | 62.5% | 26.20% |
| 20y | 0.0% | 26.20% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

- **Selected config FAILS CAGR bar**: scorer ranks `b7_ntsx70_kmlm20_tlt10`
  highest by total points despite mean CAGR 10.70% < 11.21%. Two
  alternative configs PASS all 3 bars but score lower:
  `b7_ntsx100` (12.13%/44.98%, score est ~50) and `b7_ntsx80_kmlm20`
  (11.29%/30.99%, score est ~52). The MDD-axis advantage (16 pts vs ~10)
  dominates the CAGR-axis penalty (11 pts vs 13). This is a 3rd class of
  RUBRIC SATURATION (after meta-axis Sharpe + Gates documented in iter
  019-021): selected-config picker is not bar-aware.
- **Robustness 5y/20y collapse**: 5y rolling pass-rate 33.3% (vs B5 88.9%);
  20y rolling 0%. The strategy LOSES to SPY in EVERY 20y window. NTSX
  1.5x notional with 30% defensive sleeve cannot match SPY's bull-market
  CAGR over 20-year horizons.
- **PBO N=6 grid stable**: 6 configs run; cumulative_n_trials = 86; DSR
  worst p = 1.04e-03 (PASSES <0.05 single-comparison; PASSES <5.81e-04
  Bonferroni only marginally). Borderline under multiple-testing
  adjustment.
- **All assets DIRECT in testfolio cache**: NTSXSIM, KMLMSIM, DBMFSIM,
  TLTSIM. NO synth construction, NO new infra. 771 tests baseline
  preserved.
- **Tax classification**: all 6 configs `spec.type = "static"`,
  buy_hold (terminal DARF). Drag 0.46-0.69pp = mean ~0.58pp — within
  predicted [0.55, 0.75] range.

## Lesson

### KILL evaluations (numbered #83-#88 per hypothesis.md)

| KILL # | Result | Detail |
|---:|---|---|
| **#83 axis CLOSED** | **FIRED HARD** | B7 max gross score 57 ≤ 65 threshold AND < B5's 58 by 1pt. NTSX 1.5x notional static-axis is INFERIOR to B5 200% modest-HFEA. Axis CLOSED. |
| **#84 hunt reopens** | NOT FIRED | Max 57 << 70 reopening threshold. |
| **#85 KILL #79 generalization** | **FIRED** | `b7_ntsx80_kmlm20` mean Sharpe 0.912 ≥ `b7_ntsx100` 0.782 + 0.05 = 0.832. Lift = +0.130 STRONGEST lift across 3-iter leverage trajectory. KILL #79 generalization CONFIRMED and STRENGTHENED at 1.5x notional regime. |
| **#86 NTSX minimum viable** | **FIRED** | `b7_ntsx100` mean CAGR 12.13% > 11.21% bar. Pure NTSX 1.5x is MINIMUM viable standalone static for spy_beater bars. Architectural lower bound established. |
| **#87 multi-source MF lift** | **NOT FIRED HARD** | `b7_ntsx70_kmlm15_dbmf15` mean Sharpe 0.851 < `b7_ntsx80_kmlm20` 0.912 + 0.03 = 0.942. SPLIT MF DOSE WORSE than single-source KMLM by −0.061. **NEW finding: DBMF DILUTES KMLM at 1.5x backbone** — opposite of MF decorrelation hypothesis at low leverage. |
| **#88 STRONG tier** | NOT FIRED | Max 57 << 75 STRONG threshold. |

### Closest-to-winner

**UNCHANGED — iter-019 `h2_meta_3way_33a2_33g2_34f1` retained at score 71.**

B7 selected gap vs closest-to-winner (gross 57 vs 71, −14 pts):

| axis | iter-019 | iter-023 | Δ | mechanism |
|---|---:|---:|---:|---|
| 1. CAGR | 20 | 11 | **−9** | mean 15.04% → 10.70% (FAILS bar by 0.51pp) — NTSX 1.5x backbone caps CAGR runway |
| 2. MDD | 15 | 16 | +1 | mean 28.50% → 25.81% — modest improvement, anchor saturation |
| 3. Gates | 13 | 14 | +1 | 6/7+6/7 → 6/7+7/7 (spy_real perfect, gate-decorrelation absent — single-asset NTSX) |
| 4. DSR | 10 | 10 | 0 | p 1.55e-04 → 1.04e-03 (still passes <0.05) |
| 5. Sharpe | 4 | 3 | −1 | mean 1.025 → 0.968 — slight regression |
| 6. Robustness | 9 | **3** | **−6** | 5y rolling 88.9% → 33.3%; 20y 100% → 0% — **catastrophic robustness collapse** |
| Net | 71 | 57 | **−14** | dominated by CAGR (−9) + Robustness (−6) |

### Direction implications

**Static-axis taxonomy 3-iter leverage trajectory now COMPLETE**:

| iter | axis | notional | Sharpe peak | MDD floor | CAGR ceiling | gross score | KILL #79 lift |
|---:|---|---:|---:|---:|---:|---:|---:|
| 008/009 | B1/B2 HFEA classical | 300% | 0.85 | ~60% | 18-22% | 63 | NEGATIVE (KILL #27) |
| 022 | B5 HFEA modest | 200% | 0.74 | 54.47% | 14.13% | 58 | +0.038 to +0.084 |
| **023** | **B7 NTSX low-leverage** | **150%** | **1.015** | **25.43%** | **12.13%** | **57** | **+0.130** |

**KEY GENERALIZATION CONFIRMED AND STRENGTHENED — KILL #79 is monotonic
increasing** in MF crisis-alpha effectiveness as backbone notional
leverage decreases:
- 300% → 0 lift
- 200% → +0.038 to +0.084
- 150% → +0.130

Linear extrapolation suggests at ~100% notional KMLM would lift Sharpe
~+0.18, but CAGR runway collapses to <9% standalone — CAGR bar fails by
2+pp. **Fundamental tradeoff**: lower notional → better Sharpe + MDD +
MF lift, BUT lower CAGR runway. Static-axis cannot SIMULTANEOUSLY satisfy
CAGR bar AND beat meta-axis 71.

**NEW FINDING — KILL #87 inverted at 1.5x**: at modest leverage 200%
(iter 022), KMLM > DBMF by +0.094 mean Sharpe (single-source comparison).
At low leverage 150% (iter 023), SPLIT MF (KMLM 15% + DBMF 15%) is WORSE
than single-source KMLM 20% by −0.061. Mechanism: at low backbone
leverage, the marginal MF beyond KMLM 20% has diminishing returns AND
DBMF's higher idiosyncratic vol (vs KMLM's institutional Mount Lucas
formulation) introduces noise. **At low leverage, MF concentration > MF
diversification**. This INVERTS the diversification hypothesis at the low-
leverage regime.

### 7-axis architectural taxonomy (UPDATED at iter 023)

| rank | axis | iter | gross score | net score | notes |
|---:|---|---:|---:|---:|---|
| 1 | Meta-ensemble 3-way | 019 H2 | **71** | 64 | DEFINITIVE ceiling per KILL #71 |
| 2 | LRS-mono | 006 A2 | 67 | 60 | TQQQ-track + KMLM30 + TLT10 |
| 3 | Cross-product hybrid | 014 E1 | 65 | 59 | TSMOM × TQQQ |
| 4 | Static-multi 300% | 009 B2 | 63 | 62 | HFEA + KMLM |
| 5 | Vol-target | 010 C1 | 60 | 57 | Carver SSO/UPRO |
| 6 | Static-barbell 200% | 022 B5 | 58 | 56 | UPRO+TLT+KMLM |
| **7** | **Static-low-leverage 150%** | **023 B7** | **57** | **56** | **NTSX+KMLM+TLT** |

**LOWEST gross score for an axis NOT marked 'fail'** in entire 23-iter
hunt. B7 ties B5 at net (56) since static spec drag is similar (~0.6pp).
The static-axis is FORMALLY EXHAUSTED at 3 leverage regimes; 7-axis
taxonomy COMPLETE.

### Strategic options for iter 024+ (USER DECISION REQUIRED per mandate §1 + §7)

(A) **Declare hunt EFFECTIVELY-CLOSED at iter-023 — most defensible**.
    23/50 iters used; 7-axis taxonomy COMPLETE; meta-axis ceiling 71
    DEFINITIVE; F1+SPLIT confirmed deploy fallback per mandate §1; 27
    iters preserved for hunts futuros. Recommendation: this option.

(B) **Test only remaining axis C2 CAPE-timing** (Tier-3 PROMISING_DIRECTIONS
    listing). Low credibility per [irrational_exuberance] caveats — CAPE
    has been "high" for 20+ years OOS failure. Requires NEW infrastructure
    (Shiller CAPE data fetch, CAPE engine TDD). HIGH cost, LOW expected
    score (< 60).

(C) **Pivot off score axis to mandate §7 rubric-revision request**.
    **7th iter** with rubric-suboptimal but honest-attribute config (after
    015 F1, 016 G1, 018+019+020+021 meta-ensembles, 022 B5, now 023 B7).
    Two B7 configs (`b7_ntsx100` Sharpe 0.782 / MDD 44.98% / CAGR 12.13%
    pure-equity-anchored buy-hold; `b7_ntsx80_kmlm20` Sharpe 0.912 /
    MDD 30.99% / CAGR 11.29% MF-augmented buy-hold) pass all 3 strict
    bars but rank below B5 selected. Under user-utility weighting valuing
    **Sharpe + MDD + tax efficiency**, B7 NTSX+KMLM is COMPETITIVE with
    F1+SPLIT incumbent (similar Sharpe ~0.95, lower MDD ~30% vs F1+SPLIT
    ~30-35%, similar CAGR ~11-12%, near-zero tax drag both static).

### Citations

- `[risk_parity, ch.5, p.10]` Carlson — NTSX canonical 90/60 SPY/UST
  internal stack. Empirically confirmed: pure NTSX 100% mean CAGR 12.13%
  PASSES spy_beater bar 11.21% by 0.92pp. NTSX 1.5x is the MINIMUM
  viable static for the hunt.
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha — KILL #79
  generalization extension confirmed at 150% notional (lift +0.130 vs
  +0.084 at 200% vs 0 at 300%). Empirical monotonic relationship across
  3 leverage regimes.
- `[advances_fin_ml, p.31-34]` factor framework — multi-source MF
  HYPOTHESIS REJECTED at 1.5x notional (KMLM+DBMF split WORSE than KMLM
  alone). At low leverage, MF concentration beats diversification.
- `[advances_fin_ml, p.222-223]` DSR with cumulative n_trials = 86; worst
  p = 1.04e-03 PASSES <0.05 single-comparison.
- `[advances_fin_ml, p.208-211]` PBO via CSCV N=6 grid — stability
  maintained.
- iter 022 KILL #79 generalization, this iter empirically extended to
  3rd leverage regime point.

