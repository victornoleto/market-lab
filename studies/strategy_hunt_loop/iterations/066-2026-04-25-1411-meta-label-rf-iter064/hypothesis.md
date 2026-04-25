# Iteration 066 — Tree-based meta-labeling on iter 064 base

## Hypothesis

**Apply a Random Forest meta-label classifier as a binary trade/cash gate
on the iter 064 saved combined stream.** At each bar `t`, the model
predicts `P(r_064[t] > 0 | features[t-1])` from 5 deterministic
pre-bar features. If `P > 0.5` → take the full iter 064 position;
else hold cash (rf=0). 5-fold purged k-fold with 21-day embargo
[advances_fin_ml, ch.7] generates the out-of-fold gated series; G7
cross-lib parity is verified on the post-prediction transform.

Construction:

```
iter 064:  r_064[t]
iter 066:  r_066[t] = sign[t-1] · r_064[t]  −  cost · |Δsign[t]|
           sign[t-1] = 1 if RF.predict_proba(X[t-1])[1] > 0.5 else 0
           X[t-1]    = [rolling21_sharpe_064, rolling63_mdd_064,
                        vix_lagged, t10y3m_lagged, spy_sma200_dist]
           cost      = 5 bps per signal flip
```

The classifier is **trained 5 times** (one per fold) on the
out-of-fold subset with purge=21d each side. Concatenated OOF
predictions form a single gated series with **zero in-sample peek**
on the bar being predicted [advances_fin_ml, p.103-110].

The thesis: iter 064 has narrow DSR margin (worst-p 0.0392) because
it is a high-Sharpe stream with a long left-tail of consecutive
losing days during regime transitions. If 5-10% of those down-days
are predictable from pre-bar features (vol regime, term-structure
sign, drawdown depth), a meta-label gating them out should
**lift Sharpe AND CAGR simultaneously** by avoiding a tail of
realised losses. This is structurally distinct from iter 013 (LR
meta-label, closed redundant w/ variance-scaling) because tree
classifiers exploit non-linear feature interactions and do not assume
a logistic decision boundary.

## Primary citation

`[advances_fin_ml, ch.3]` — López de Prado (2018), Chapter 3 "Labeling"
+ Chapter 17-18 (regime / non-linear binary gates). Meta-labeling
canonical pattern: primary model produces side; secondary model decides
whether to take it. Reports out-of-sample Sharpe uplift on equity
strategies with binary forward labels and tree-based classifiers.

## Additional citations

- `[advances_fin_ml, ch.7]` — purged k-fold cross-validation, p.103-110.
  5-fold CV with 21-day embargo prevents look-ahead via overlapping
  forward labels.
- `[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio with cumulative
  n_trials. iter 066 advances cumulative 4335 → 4336 (+1 single cfg,
  no in-sample tuning).
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
  Applied here on the post-prediction deterministic transform
  (predictions × r_064 − cost), since RF training is non-deterministic
  in general but the post-prediction collapse is pure linear algebra.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- Breiman, L. (2001), *Mach. Learn.* 45(1) 5-32, DOI
  10.1023/A:1010933404324 — Random Forest. Used here with 200 estimators,
  max_depth=4, random_state=42, class_weight='balanced'. Pre-committed,
  no grid search, no tuning.
- Lopez de Prado, M. (2020), *Mach. Learn. for Asset Managers*,
  Cambridge — independently confirms tree-based meta-labels'
  out-of-sample edge with proper purging.
- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen (2012); preserved
  verbatim via iter_046 saved stream inside iter 064.
- `[volatility_trading, p.218]` — Sinclair (2013); preserved via iter
  039 sub-component inside iter 046.
- Whaley (2009), JPM 35(3) 98-105, DOI 10.3905/JPM.2009.35.3.098 —
  VIX as ex-ante risk regime indicator (one of the 5 features).
- Faber (2007), SSRN 962461 — single-asset 200-day SMA TAA
  primitive; SPY 200d SMA distance is one of the 5 features.

## Edge source

iter 064 carries the Pareto-optimal 90 score with narrow DSR margin
(worst-p 0.039). What SPY 1x buy-hold misses: the regime transition
days where iter 064's risk-parity + VRP + QQQ-trend stack delivers
a concentrated negative return. If those days are correlated with
observable pre-bar state (high VIX, inverted T10Y3M, high recent
realised vol on the stream itself, deep recent MDD), a tree
classifier should learn the boundary and gate them out. The expected
uplift mechanism:

- **Sharpe**: gate out bars with `E[r_064[t]] < 0` per the classifier
  → reduces the realised left tail → Sharpe ↑.
- **CAGR**: gating preserves positive bars; cash on negative bars
  preserves capital. Compounding gain.
- **DSR**: tighter Sharpe → lower p-value. If meta-label is
  informative on ≥ 5% of bars, DSR worst-p should fall from 0.039 to
  ~0.02-0.025 across 3 datasets, clearing the strict 0.05 cut by a
  wider margin and lifting score.

## Datasets

- **educational** (SPYSIM synth 40y, 1986-01-04 → 2026-04-15): largest
  sample (~10000 bars after warmup), tests classifier behavior on
  heterogeneous market regimes (1987 crash, 2000-02 dot-com bust,
  2008 GFC, 2020 COVID, 2022 inflation tightening). Edu CAGR floor
  pass at iter 064 (9.49% > 9.18%) is the binding constraint to
  preserve here.
- **spy_real** (Tiingo SPY/UPRO 17y, 2009-06-26 → 2026-04-15, ~4226
  bars): post-GFC primary benchmark. iter 064 has CAGR floor gap
  −2.01 pp. Hypothesis: meta-label uplifts Sharpe enough that even
  modest CAGR uplift (~+0.5 pp) tips the floor at 11.98% via
  compounding.
- **ndx_real** (Tiingo QQQ/TQQQ 16y, 2010-02-12 → 2026-04-15, ~4090
  bars): QQQ benchmark. iter 064 has CAGR floor gap −5.18 pp; this
  remains the most demanding test.

## Kill criteria (pre-committed)

| # | Kill | Threshold | Rationale |
|---|---|---|---|
| **A** | Sharpe regress vs iter 064 by ≥ 0.05 on ≥ 2 datasets | Falsifies "meta-label is informative" — model would be adding noise |
| **B** | DSR worst-p ≥ 0.10 (2.5× iter 064's 0.039 ceiling) | Falsifies "Sharpe edge survives cumulative n_trials" |
| **C** | Score < 79 (iter 062/063 baseline) | iteration provides no value vs internal-LETF baseline |
| **D** | edu CAGR < 9.18% | Loses iter 064's 1st-ever non-LETF floor unlock — counter-fail |
| **E** | G7 cross-lib > 3 pp absolute CAGR (post-prediction transform) | Engine bug |
| **F** | corr(iter_066, iter_064) > 0.99 | Meta-label is a no-op (gate fires < 1% of bars) |
| **G** | pct_traded < 50% | Meta-label is over-aggressive (kills > 50% of bars → starves CAGR) |
| **H** | Average OOF AUC < 0.52 | Classifier is random — predict_proba carries no signal |

If 2+ kills fire ⇒ hypothesis falsified, iteration aborted-with-lesson.
If 0-1 kill fires AND score ≥ 90 AND winner_conditions met ⇒ **WINNER
candidate** for shell-loop halt. If 0-1 kill fires AND score ≥ 75 ⇒
STRONG and updates Top-K.

## Expected budget

- **Configs to test**: 1 (single pre-committed cfg, no grid, no tuning)
- **Wall-time**: ~45-60 min
  - 5-fold CV training: ~2-5 min per dataset × 3 = ~15 min
  - Backtests + gates: ~10 min
  - G3 walk-forward 8 windows + G6 bootstrap: ~15 min
  - Reporting: ~10 min
- **Files to create** in this iter dir:
  - `meta_label_rf.py` — RF classifier wrapper + purged k-fold
  - `feature_engineering.py` — 5 deterministic features from iter_064
    + macro
  - `numpy_reference_iter066.py` — pure-numpy reference for G7
    (post-prediction transform)
  - `combined_iter064_meta.py` — gated combine
    `pred[t-1] · r_064[t] − cost`
  - `run_backtests.py` — orchestrator across 3 datasets
  - `compute_gates_and_score.py` — gates + scoring helper
  - `tests/test_features.py` — TDD specs for feature engineering
  - `tests/test_meta_label.py` — TDD specs for purged k-fold +
    classifier
  - `tests/test_combined.py` — TDD specs for the gated combine + cost
  - `tests/test_g7_parity.py` — G7 numpy reference parity
  - `results.json` — full output schema
  - `verdict.json` — produced by `score_strategy()`
  - `final_report.md` — Stage 5 report
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
- **cumulative_n_trials advance**: 4335 → 4336 (+1)

## Implementation plan

1. **Feature engineering** (`feature_engineering.py`):
   - Load iter_064 saved stream from
     `iterations/064-*/results.json["returns_series"][ds]`
   - Load VIX, T10Y3M from `data/external/macro/`
   - Load SPY price for SMA200 distance (educational uses SPYSIM)
   - Compute 5 features at each bar t (using only data up to and
     including t-1):
     1. `roll21_sharpe`: rolling 21d Sharpe of iter_064 returns,
        shifted 1 (lagged)
     2. `roll63_mdd`: rolling 63d max drawdown of iter_064 cum returns,
        shifted 1
     3. `vix`: VIX[t-1] (forward-fill from prior available)
     4. `t10y3m`: T10Y3M[t-1]
     5. `sma200_dist`: (SPY_close[t-1] − SMA200(SPY)[t-1]) / SMA200
   - Drop bars with any NaN feature (warmup)
2. **Purged k-fold** (`meta_label_rf.py`):
   - Implement 5-fold purged k-fold per AFML Ch.7:
     - Split bars into 5 contiguous folds
     - For each fold k as test: drop train bars within `embargo=21`
       days of fold k's boundaries on either side
     - Train RF on remaining train bars
     - Predict on fold k → store OOF predictions
   - RandomForestClassifier(n_estimators=200, max_depth=4,
     random_state=42, n_jobs=1, class_weight='balanced')
   - Label: `r_064[t] > 0` (1 if positive, 0 otherwise)
3. **Combiner** (`combined_iter064_meta.py`):
   - For each bar t, compute:
     `r_066[t] = pred_oof[t-1] · r_064[t] − cost · |pred[t]−pred[t-1]|`
   - cost = 5 bps per signal flip
4. **TDD tests** (`tests/test_*.py`):
   - test feature engineering: SMA200 distance, rolling Sharpe lag
     correctness, VIX forward-fill no-peek
   - test purged k-fold: no contamination between train and test
     (no overlap with embargo)
   - test classifier wrapper: deterministic with same seed
   - test combiner: cost on flips correctness, no-peek invariants
   - test G7 parity: numpy reference matches pandas pipeline to 1e-10
     on post-prediction transform
   - target: 12-15 tests, all green in < 30s
5. **Run** (`run_backtests.py`):
   - For each dataset: load iter_064 series + features
   - Compute purged k-fold OOF predictions
   - Compute r_066 series + Sharpe / CAGR / MDD
   - Compute corr(iter_066, iter_064), pct_traded, avg AUC across folds
   - Compute Markowitz residual (vacuous for binary gate, expect 0)
   - Run G6 bootstrap (1000 resamples, 99.9% CI)
   - Run G7 cross-lib check (post-prediction transform)
   - Run G3 walk-forward 8 windows + G4 OOS 70/30 + G5 FWD post-2020
   - Persist `returns_series` (with required schema for plot helper)
6. **Gates + score** (`compute_gates_and_score.py`):
   - Compute G1-G7 per dataset
   - Apply rolling-window robustness (3 sub-windows per dataset)
   - Call `score_strategy(metrics, gates, cumulative_n_trials=4336)`
   - Write `verdict.json`
7. **Plots**: invoke `plot_helper.py --iter 066`
8. **Report + memory**: write `final_report.md`, update `BASE_MEMORY.md`
   (frontmatter + Iteration log + Top-K if score ≥ 84), append to
   `DEAD_ENDS.md` if structural closure (e.g., "tree-based meta-label
   on iter 064 base at depth=4, n=200" closure with verdict).

## Why this is structurally novel

- **vs iter 013** (LR meta-label, closed redundant): tree-based RF
  exploits non-linear feature interactions; LR cannot. Different
  function class.
- **vs iter 048** (output VIX gate, closed regression): RF combines
  5 features non-linearly; iter 048 was binary VIX threshold only.
- **vs iter 065** (calm-conditional ext lev, closed regression): no
  leverage added; pure binary gate (1.0 or 0.0) — sidesteps borrow
  drag entirely.
- **vs iter 050** (gold-TSM Markowitz combine, closed): no new asset;
  meta-labels on existing iter_064 stream's own bar-level state.
- **vs iter 042/044** (regime amp/freq on iter_041): operates on outer
  combined output, not inner-component weights; uses 5-feature
  classifier vs single-binary VIX gate.

The mechanism class — "non-linear classifier on rolling pre-bar
features producing binary trade/cash gate" — is **untested on iter
064 family** and represents the genuinely new axis identified by iter
065's closure summary.
