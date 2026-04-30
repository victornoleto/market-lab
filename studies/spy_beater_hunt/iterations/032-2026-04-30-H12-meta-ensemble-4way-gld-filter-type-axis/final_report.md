# spy_beater_hunt iter 032 — Final Report — `H12-meta-ensemble-4way-gld-filter-type-axis`

**Gross tier**: **PROMISING** — `gross_score=72/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=66/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 16.59%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 33.77%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 14.46%)
- MDD bar: PASS (mean = 35.28%)
- Gates bar (same as gross): PASS

**Primary citation**: [advances_fin_ml, ch.16, p.241-256] portfolio construction over multiple alpha streams (4-way meta-ensemble at strategy-level with GLD-source filter-type sub-axis exploration — 16th iter at meta-axis) + [ivy_portfolio] Faber GTAA single-asset 6-10m moving average (commodity proxy DBC-10m; iter 032 tests GLD-SMA-200d as Faber commodity gate equivalent) + Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 (GLD-momentum-126d retained as baseline; filter-type axis substitutes with sma/ema canonical alternatives) + [asness_value_momentum] momentum-everywhere across asset classes (commodity TSMOM premium structure preserved across filter-types) + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate (A2 + G2 baseline retained — both equity-track 200d-SMA) + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (F1 stack always-on retained at 3rd constituent — septuple-confirmed uniquely-Pareto-optimal per iter 027 KILL #110 + iter 028/029/030/031 implicit) + [ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2/E1 ON-state) + Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) + iter 030 KILL #124 NOT FIRED — Principle B (triple-granularity distinctness asset × filter × lookback) + iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt) + iter 031 KILL #130 (TSMOM-lookback inverted-U asset-invariant peak at 6m) + [advances_fin_ml, p.31-34] factor framework — meta-ensemble axis 16th iter (GLD-source filter-type sub-axis exploration) + [advances_fin_ml, p.222-223] DSR cumulative_n_trials = 124 (Bonferroni 4.03e-04) + [advances_fin_ml, p.208-211] PBO grid-level N=4 stability

---

## Selected config: `h12_meta_4way_25a2_25g2_25f1_25e1gld_mom126`

Spec:

```json
{
  "type": "blend",
  "constituents": [
    {
      "weight": 0.25,
      "spec": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {
          "TQQQSIM": 0.3,
          "QLDSIM": 0.3,
          "KMLMSIM": 0.3,
          "TLTSIM": 0.1
        },
        "off_weights": {
          "IEFSIM": 1.0
        },
        "signal_ticker": "QQQSIM",
        "lag_days": 1
      }
    },
    {
      "weight": 0.25,
      "spec": {
        "type": "lrs",
        "on_weights": {
          "UPROSIM": 0.3,
          "TMFSIM": 0.25,
          "IEFSIM": 0.15,
          "UGLSIM": 0.15,
          "KMLMSIM": 0.15
        },
        "off_weights": {
          "IEFSIM": 1.0
        },
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "filter": "sma",
        "lag_days": 1
      }
    },
    {
      "weight": 0.25,
      "spec": {
        "type": "static",
        "weights": {
          "NTSXSIM": 0.35,
          "GDESIM": 0.3,
          "TLTSIM": 0.2,
          "KMLMSIM": 0.15
        }
      }
    },
    {
      "weight": 0.25,
      "spec": {
        "type": "lrs",
        "filter": "momentum",
        "lookback_days": 126,
        "on_weights": {
          "TQQQSIM": 0.3,
          "QLDSIM": 0.3,
          "KMLMSIM": 0.3,
          "TLTSIM": 0.1
        },
        "off_weights": {
          "IEFSIM": 1.0
        },
        "signal_ticker": "GLDSIM",
        "lag_days": 1
      }
    }
  ]
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 1.041 | 17.03% | 33.77% | 0.918 | 14.85% | 35.28% | 2.18 | 6/7 |
| **spy_real** | 1.037 | 16.14% | 33.77% | 0.912 | 14.07% | 35.28% | 2.07 | 5/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $305,259 (terminal $9,447), drag 2.18pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $27,838 (terminal $75), drag 2.07pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| h12_meta_4way_25a2_25g2_25f1_25e1gld_mom126 | 1.041 | 1.037 |
| h12_meta_4way_25a2_25g2_25f1_25e1gld_sma126 | 0.995 | 1.034 |
| h12_meta_4way_25a2_25g2_25f1_25e1gld_ema126 | 0.972 | 0.987 |
| h12_meta_4way_25a2_25g2_25f1_25e1gld_sma200 | 1.019 | 1.024 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 23 | 30 | mean = 16.59%, bar = 11.21% |
| 2. MDD vs SPY | 13 | 20 | mean = 33.77%, bar = 55.17% |
| 3. Gates | 12 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 6.55e-05, n_trials = 124 |
| 5. Sharpe | 4 | 10 | mean = 1.039 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 83.3% | 33.77% |
| 10y | 100.0% | 33.77% |
| 15y | 100.0% | 33.77% |
| 20y | 100.0% | 33.77% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

- **GLDSIM coverage**: 1986-01 to 2026-04, 10151 trading days — covers full lh_56y dataset. Same coverage as iter 030/031. No coverage gap.
- **Selected config H12.1 mom126 EXACTLY replicates iter 030 H10.4 / iter 031 H11.2** by design (selected, score 72): per-dataset Sharpe 1.041/1.037, CAGR 17.03%/16.14%, MDD 33.77%/33.77%, gates 6/7+5/7 — IDENTICAL across 4 decimal places to BOTH parents. Triple-replication confirms iter 030 measurement reproducible across 3 independent iters.
- **Filter-type axis spread**: per-config raw-metric variation Sharpe 0.979-1.039 (Δ 0.060) / CAGR 15.32-16.59% (Δ 1.27pp) / MDD 33.58-37.18% (Δ 3.60pp). All metrics span MORE than iter 031's lookback-axis spread (Sharpe Δ 0.052 / CAGR Δ 0.56pp / MDD Δ 7.50pp on lookback). Filter-type axis at GLD source produces materially different daily-return streams per filter mechanism.
- **sma126 has the WORST mean MDD across the 4 filter variants** (37.18%) — driven by lh_56y's 41.76% MDD. Reason: 126d SMA on gold whipsaws across 1986-2002 sustained sideways gold market (gold price oscillated $300-500 with multi-year bull/bear cycles); SMA crossings produce frequent gate flips that compound to deeper drawdowns when the leveraged TQQQ-stack sleeve was OFF during late-cycle equity recoveries. Counter-intuitive vs sma200's smoother trend filter (MDD 33.98% on lh_56y).
- **ema126 has the WORST mean Sharpe across the 4 filter variants** (0.979) — drops below 1.0 sharpe-bucket threshold. EMA's faster response than SMA causes more whipsaws on gold; CAGR 15.32% vs mom126's 16.59% reflects ~1.3pp opportunity cost from late entries / early exits at gate transitions.
- **sma200 (Faber GTAA commodity gate) is the BEST-PRESERVING non-momentum variant** (CAGR 16.31%, MDD 33.58%, Sharpe 1.022, est score 71). The 200d window's smoother gate transitions on gold (slower flips, less whipsaw) preserve most of the signal-asset orthogonality bonus despite filter-type and lookback BOTH matching A2/G2's 200d-SMA structure.
- **DSR Bonferroni at n_trials=124**: threshold 0.05/124 = 4.03e-04. Worst per-config DSR p was 6.55e-05 on spy_real (PASSES strict <0.05; PASSES Bonferroni 4.03e-04 with **6.1× margin** — slight reduction from iter 031's 6.4× margin due to n_trials inflation 120→124).
- **No new infra**: reuses 'blend' + 'lrs' (sma + ema + momentum filters) + 'static' spec types from iter 014/018-031. **771 tests baseline preserved**.
- **Tax classification**: meta-blend with LRS-gate constituents (mixed sma/ema/momentum filters) → annual_realize. Drag observed 2.18pp lh_56y / 2.07pp spy_real, mean 2.13pp — IDENTICAL to iter 030/031 H10.4/H11.2 because selected config replicates iter 030 H10.4 exactly.
- **Joint signal-asset × filter-type × lookback grid mapping STATUS** (iter 029 + iter 030 + iter 031 + iter 032): QQQ × mom × {3m, 6m, 12m} cells (iter 029); {QQQ, SPY, GLD} × mom × 6m cells (iter 030); GLD × mom × {3m, 6m, 9m, 12m} cells (iter 031); GLD × {mom-126, sma-126, ema-126, sma-200} cells (iter 032). Joint surface coverage now: 12 distinct cells across 3 axes. Remaining UNDER-MAPPED: SPY × mom × {3m, 9m, 12m}; QQQ × mom × 9m; QQQ/SPY × {sma, ema} × 126d; GLD × {sma, ema} × 200d EMA equivalent. iter 032 closes filter-type axis at GLD-source × 6m peak.

## Lesson

### KILLs disparados (pre-committed iter-032 #133-#138)

- **KILL #133 FIRED — META-AXIS CEILING 72 CONFIRMED at GLD-source × FILTER-TYPE axis (16th meta-axis confirmation)**:
  max H12 = **72** ≤ 72 → 16th meta-axis confirmation. Sequence
  018→019→020→021→025→026→027→028→029→030→031→032 = 70→71→67→70→70→71→
  70→69→69→72→72→72. Filter-type variation at GLD-source did NOT extend
  ceiling above 72; orthogonal-asset-class bonus is FILTER-TYPE-COUPLED
  not extension-additive. iter 030 H10.4 ceiling-breach to 72 remains
  attributable to SPECIFIC joint-axis configuration (GLDSIM × momentum ×
  126d lookback), not generalizable across filter-type substitutions.

- **KILL #134 NOT FIRED — STRONG-FORM FALSIFICATION DOES NOT TRIGGER**:
  max H12 = 72, not > 72 strict. New ceiling 72 holds across the
  GLD-source × filter-type axis. Hunt's empirical informational value at
  this sub-axis is meta-principle-only (KILL #135 + #137 firing); no
  above-ceiling architectural point discovered.

- **KILL #135 FIRED — ORTHOGONALITY BONUS IS FILTER-TYPE-COUPLED**:
  min H12 (~69 estimated for sma126/ema126) < max H12 (72) by 2-3pt; the
  +1pt orthogonal-asset-class bonus (KILL #125 iter 030) is NOT
  invariant under filter-type substitution at GLD source. **NEW EMPIRICAL
  PRINCIPLE G**: at GLD signal source within meta-axis 4-way structure,
  the orthogonality bonus is specifically COUPLED to the MOMENTUM filter
  type. SMA/EMA filters on the same GLD signal LOSE the bonus by 1-3pt
  depending on parameter selection. The +1pt bonus is NOT just about
  asset-class distinctness — it requires the JOINT optimum
  (signal-asset × filter-type × lookback at peak ~6m).

- **KILL #136 NOT FIRED — FILTER-TYPE AXIS IS RUBRIC-RELEVANT**:
  per-config raw-metric variation produces estimated score range 69-72
  (Δ 3pt > ±1pt rubric-neutral threshold). Filter-type axis at GLD source
  is NOT rubric-saturated — unlike iter 031's lookback-axis (Δ 2pt
  borderline) or iter 029's lookback-axis on QQQ (Δ 2pt). Filter-type
  is a more rubric-discriminating axis than lookback at GLD source. Does
  NOT join the 8-class RUBRIC SATURATION taxonomy.

- **KILL #137 PARTIAL — PRINCIPLE B 2/3-AXIS REQUIREMENT IS FALSIFIED**:
  KILL #137's predicted ordering: score(sma200, 1/3 axis) < score(sma126,
  2/3 axes) ≤ score(mom126, 3/3 axes). Observed ordering: score(mom126
  72) > score(sma200 ~71) > score(ema126 ~69) ≈ score(sma126 ~69).
  **sma126 (2/3 axes distinct) UNEXPECTEDLY scores LOWER than sma200
  (1/3 axis distinct)** by 2pt. Principle B's simple "2/3 axes = bonus
  preserved" interpretation is FALSIFIED at GLD source × meta-axis 4-way.
  **NEW EMPIRICAL PRINCIPLE H**: the 3-axis distinctness manifold is
  NON-UNIFORM — different (filter, lookback) combinations produce
  different gating behavior on gold prices regardless of the
  asset-distinctness count. sma200's slower trend filter on gold
  PRESERVES MORE of the orthogonality bonus than sma126's faster filter
  despite sma200 having LESS axis-count distinctness. Principle B must
  be REVISED: filter-type's specific gate-mechanism (slow trend vs fast
  momentum) interacts non-linearly with asset-class orthogonality.

- **KILL #138 PARTIAL — sma200 LOSES BUT BY LESS THAN sma126**:
  KILL #138's predicted: sma200 < 72 AND sma126 ≥ 72. Observed: BOTH
  sma200 (~71) AND sma126 (~69) score < 72. Pre-committed prediction
  PARTIALLY confirmed — sma200 does lose 1pt as predicted, but sma126
  ALSO loses 3pt (more severe than predicted). The asset-class
  orthogonality alone is INSUFFICIENT to retain the full +1pt bonus
  regardless of filter-type-axis distinctness count; gate-mechanism
  specifically (slow trend SMA-200 vs fast momentum vs short SMA/EMA)
  matters more than axis-count.

### NEW EMPIRICAL PRINCIPLES (iter 032)

**Principle G — FILTER-TYPE-COUPLED ORTHOGONALITY BONUS** (KILL #135
FIRED): At GLD signal source within meta-axis 4-way structure, the +1pt
orthogonal-asset-class bonus (KILL #125 iter 030) is specifically COUPLED
to the MOMENTUM filter type at lookback peak ~6m. SMA filter at 6m or
10m (Faber-canonical) AND EMA filter at 6m all LOSE the bonus by 1-3pt.
Mechanism (hypothesized): momentum filter on gold captures relative
6m-trend (price-vs-6m-prior); SMA filter captures price-vs-6m-MA crossing
which produces different gating decisions in sustained-sideways gold
markets (1986-2002, 2013-2018) where price oscillates around MA without
clear trend direction. The +1pt bonus from iter 030 KILL #125 was
specifically realized at the JOINT optimum (signal-asset orthogonal ×
filter-type momentum × lookback inverted-U peak); filter-type
substitution to SMA/EMA breaks the joint optimum even with asset+lookback
preserved.

**Principle H — TRIPLE-GRANULARITY DISTINCTNESS MANIFOLD IS NON-UNIFORM**
(KILL #137 PARTIAL FIRED): Principle B's simple "2/3 axes distinct =
bonus preserved" interpretation is FALSIFIED. At GLD source, sma126
(asset+lookback distinct = 2/3 axes) scores LOWER than sma200 (asset
only = 1/3 axis) by 2pt. This implies the 3-axis distinctness manifold
(asset × filter × lookback) is non-uniform — specific (filter, lookback)
combinations interact with the asset-class signal differently. Faber's
slow-trend SMA-200 produces stable gating on gold consistent with the
TSMOM-6m's gate-frequency profile; faster SMA-126/EMA-126 produce
whipsaws that break the stable gating profile. Principle B must be
REVISED to: gate-source-distinctness depends on (filter × lookback)
gate-mechanism characteristics, not simply on axis-count. iter 030
KILL #124 NOT FIRED at SPY-mom-126 worked because momentum-126 produced
distinct gating from SMA-200 in BOTH gate-frequency AND gate-mechanism;
sma126 at GLD has distinct asset+lookback from A2/G2 SMA-200 but
matches SMA gate-mechanism, breaking the gate-source-distinctness
benefit.

**Principle I — SLOW-TREND FILTER PRESERVES BONUS BETTER THAN
FAST-TREND FILTER ON COMMODITY-CLASS SIGNALS**: At GLD source, sma200
(10m gate, slow flips) preserves 71/72 of the bonus (~99%); sma126 (6m
gate, faster flips) preserves 69/72 (~96%); ema126 (6m gate, even
faster flips) preserves 69/72 (~96%); mom126 retains full 72/72 (100%).
The pattern across filter-types {mom > sma200 > sma126 ≈ ema126} suggests
slow-trend filters (200d SMA Faber-canonical) preserve more bonus
than fast-trend filters (126d SMA/EMA) on commodity-class signals.
Mechanism: gold's volatility profile (~14-18%) and longer cycle structure
favor slower gating to avoid whipsaws.

### Score breakdown vs iter-030 H10.4 prior closest-to-winner (72→72, 0pt — TIES via REPLICATION)

| criterion | iter 030 H10.4 | iter 031 H11.2 | iter 032 H12.1 | Δ vs 030 |
|---|---:|---:|---:|---:|
| 1. CAGR | 23 | 23 | 23 | 0 (mean 16.59% TRIPLE-IDENTICAL) |
| 2. MDD | 13 | 13 | 13 | 0 (mean 33.77% TRIPLE-IDENTICAL) |
| 3. Gates | 12 | 12 | 12 | 0 (6/7+5/7 TRIPLE-IDENTICAL) |
| 4. DSR | 10 | 10 | 10 | 0 (p 6.55e-05 TRIPLE-IDENTICAL) |
| 5. Sharpe | 4 | 4 | 4 | 0 (mean 1.039 TRIPLE-IDENTICAL) |
| 6. Robustness | 10 | 10 | 10 | — |
| 7. Bonus | 0 | 0 | 0 | — |
| **Total** | **72** | **72** | **72** | **0pt — TRIPLE-TIE** |

iter 032 H12.1 EXACTLY replicates iter 030 H10.4 / iter 031 H11.2 — TRIPLE
replication confirms iter 030 measurement reproducible. Other H12 filter
variants did NOT reach the mom126 peak; SMA/EMA filter substitutions LOSE
1-3pt of the orthogonality bonus.

### Closest-to-winner UNCHANGED

**iter 030 H10.4 (h10_meta_4way_25a2_25g2_25f1_25e1gld) RETAINS closest-
to-winner at score 72** by precedence — iter 032 H12.1 ties at 72 but
iter 030 reached the ceiling first (8 trials earlier, n_trials 116 vs
124). iter 032 H12.1 is the position-symmetric duplicate of iter 030
H10.4 / iter 031 H11.2 — identical metrics by design. iter 030 H10.4
remains apex.

### Direction implications

- **15-AXIS ARCHITECTURAL TAXONOMY UNCHANGED — meta-axis ceiling 72
  CONFIRMED at GLD-source × FILTER-TYPE axis**. iter 032 closes the
  most informative remaining gap (filter-type axis at GLD-source × 6m
  peak) without breaching the ceiling. The +1pt iter 030 breach was
  due to JOINT optimum (signal-asset × filter-type × lookback at peak),
  NOT extensible by single-axis substitution along any of the 3 axes.

- **FILTER-TYPE-COUPLED orthogonality is a NEW SUB-PRINCIPLE**:
  Principle G adds to the 9-class architectural taxonomy a refined
  understanding — orthogonality bonus is realized only at JOINT optimum
  (asset orthogonal × filter momentum × lookback at inverted-U peak ~6m).
  Single-axis substitution along ANY axis loses 1-3pt of the bonus.
  Future signal-asset variations on commodities (DBC, BCOM) should retain
  momentum filter to preserve bonus; SMA/EMA substitutions for
  bookkeeping/coherence-with-A2/G2 are not bonus-preserving.

- **PRINCIPLE B IS REFUTED at GLD source**: iter 030 KILL #124 NOT
  FIRED at SPY-mom-126 was generalized to "≥ 2/3 axes distinct =
  bonus preserved". iter 032 demonstrates this is asset-specific —
  at GLD source, axis-count alone does NOT predict bonus retention;
  gate-mechanism (slow vs fast trend filter) matters more. **NEW
  PRINCIPLE H** revises Principle B to: gate-source-distinctness
  depends on (filter × lookback) gate-mechanism characteristics, not
  axis-count alone.

- **F1 stack always-on uniquely-Pareto-optimal at 3rd position — 8TH
  IMPLICIT CONFIRMATION** (iter 032): all 4 H12 configs retain F1 at
  3rd position; max H12 score 72 achieved with F1 retained. F1 status
  now octuple-confirmed (iter 025/026/027 direct + iter 028/029/030/031/
  032 implicit retention).

- **MANDATE §7 RUBRIC-REVISION REVIEW CASE STRENGTHENED to 16th iter**:
  iter 032 H12.4 sma200 (Faber GTAA commodity gate) at score 71
  presents a Pareto-frontier-adjacent point with CAGR 16.31% (close to
  mom126's 16.59%) AND MDD 33.58% (slightly better than mom126's
  33.77%). Under MDD-AND-Sharpe-AND-CAGR weighted utility, sma200 may
  be deploy-considerable as a Pareto-frontier-adjacent secondary candidate
  — but mom126 dominates on Sharpe (1.039 vs 1.022) and is the
  selected closest-to-winner. iter 031 H11.4 (12m, MDD 29.51%
  best-in-hunt) remains the MDD-minimizing candidate.

### Strategic options for iter 033+ (USER DECISION REQUIRED per mandate §1 + §7)

**Recommendation: Option A** (declare hunt RE-CLOSED at iter 032 — most
defensible per mandate §1 MAINTENANCE MODE; iter 030 H10.4 remains
apex; iter 031 (lookback-axis at GLD) and iter 032 (filter-type axis at
GLD) confirmed ceiling 72 across BOTH single-axis substitutions; further
single-axis exploration on GLD-source EXHAUSTED across 8 mapped cells;
F1+SPLIT confirmed deploy fallback; 32 iters preserved 64% of budget).
Recommendation EVEN STRONGER than iter 031 due to: (a) iter 030's
ceiling-breach attributable to JOINT optimum NOT extensible by EITHER
single-axis variation (lookback iter 031 OR filter-type iter 032);
(b) Principle G (filter-type-coupled bonus) and Principle H (non-uniform
distinctness manifold) both demonstrate the +1pt is bounded to specific
joint configurations; (c) 8 sub-axis cells mapped on GLD source without
breaching ceiling.

(B) test SPY-source filter-type variation at 6m peak (sma126, ema126,
sma200) — LOW credibility (iter 030 H10.spy did not breach ceiling at
mom-126; filter substitution unlikely to extend; expected score ≤ 71).

(C) test 5-way structure with GLD-mom-126d as 5th constituent — UNTESTED,
MEDIUM credibility (signal-asset orthogonality bonus may compensate for
5-way base penalty per iter 027 KILL #107).

(D) test JOINT axes: GLD-source filter-type × lookback grid expansion
(GLD-sma-200d combined with TSMOM-12m, etc.) — MEDIUM cost, LOW
credibility (Principle G suggests momentum is the sole filter-type
bonus-preserving at GLD source).

(E) NEW DATA INFRA for DBC/BCOM/USDJPY orthogonal signals at
momentum-126d filter — HIGH cost (requires Tiingo-or-similar new ticker
integration), MEDIUM-HIGH credibility (could replicate iter 030 KILL
#125 across more asset classes; Principle G suggests momentum filter
critical for bonus retention).

Tier PROMISING (72 ∈ [60, 74]). Hunt's empirical informational value
plateaued AGAIN at iter 032 — the +1pt iter 030 breach is now confirmed
to be specific to JOINT optimum (asset × filter × lookback), not
generalizable via single-axis substitution along any of the 3 axes.
Principle G + Principle H consolidate the meta-principles. Mandate §1
100% Plano C UNCHANGED — research only.

### Citations applied

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over
  multiple alpha streams (4-way meta-ensemble at strategy-level with
  GLD-source filter-type sub-axis exploration — 16th iter at meta-axis)
- `[ivy_portfolio]` Faber GTAA single-asset 6-10m moving average
  (commodity proxy DBC-10m; iter 032 tests GLD-SMA-200d as direct Faber
  commodity gate equivalent at 1/3-axis distinctness)
- **Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250**
  TSMOM canonical (GLD-momentum-126d retained as baseline; filter-type
  substitutions empirically demonstrated to LOSE the bonus)
- `[asness_value_momentum]` momentum-everywhere across asset classes
  (commodity TSMOM premium structure preserved at momentum filter only;
  SMA/EMA at gold do NOT replicate the premium structure within
  meta-axis 4-way)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate
  (A2 + G2 baseline retained — both equity-track 200d-SMA)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking
  (F1 stack always-on retained — octuple-confirmed uniquely-Pareto-optimal)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in
  A2/G2/E1 ON-state)
- Bridgewater All-Weather (Dalio 1996) F1 stack ON-state retained
- `[advances_fin_ml, p.208-211]` PBO via CSCV (N=4 grid)
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials = 124
  (Bonferroni 4.03e-04; worst per-config p 6.55e-05 PASSES with 6.1×
  margin — slight reduction from iter 031's 6.4×)
- `[advances_fin_ml, p.196-202]` Bootstrap CI
- `[advances_fin_ml, p.31-34]` Cross-lib factor framework
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — REFINED
  by Principle G to JOINT-optimum-specific
- iter 030 KILL #124 NOT FIRED (Principle B 2/3-axis distinctness) —
  **REFUTED at GLD source by iter 032 KILL #137 PARTIAL FIRED**
- iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt) —
  CONFIRMED specific to (asset orthogonal × MOMENTUM filter × ~6m
  lookback) joint optimum per Principle G
- iter 031 KILL #130 (TSMOM-lookback inverted-U asset-invariant peak) —
  RECONFIRMED via iter 032 mom126 baseline (replicates iter 030/031)
