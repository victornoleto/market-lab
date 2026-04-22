# Phase 3.6 Family J — ML classical (J1 Jansen gradient boosting) honest validation

**Date:** 2026-04-23  |  **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched (commit `7b90a8f` — `prev_weight × next_return`)
**Broker path modelled:** Banco Inter Internacional (plan §3.2) —
zero commission on US ETFs, 5 bps one-way spread on traded notional,
BR 15% capital-gains tax on positive monthly net return.
**Windows:** IS 2005-01-03 → 2017-12-31 (trimmed to GLD inception —
see §Trim note) | OOS 2018-01-01 → 2023-12-31 | FWD 2024-01-01 →
2026-04-14
**Track chosen:** **J1 — Jansen-style gradient boosting on engineered
equity-bar features** (not J2 LdP fractional-diff regression).

## Verdict: **FAIL** (4 PASS / 9 FAIL / 2 DEFER over 15 gate rows)

Family J collapses on every edge gate except FWD. OOS Sharpe is
**0.231**, OOS CAGR **2.62%**, OOS MaxDD **−35.32%**, DSR p-value
**0.890**, cost×2 Sharpe **0.138**, IR vs SPY OOS **−0.92**, and
walk-forward max-window DD **35.32%**. The only binding gates that
PASS are PBO (0.016 — low because all 16 grid configs are uniformly
mediocre out-of-sample), FWD Sharpe (1.17, on a single 2.2-yr window),
median-hold (457.5d — too large to even qualify as "swing"), and the
FULL-window bootstrap-CI arm (driven by the strong IS leg). The
OOS-only bootstrap 99.9% CI on Sharpe straddles zero at
**[−0.84, +1.73]**. Binding fail count is **8 hard edge gates** — no
ambiguity, no PARTIAL. This is a decisive FAIL.

Mandate §7 and strategy docs stay **UNTOUCHED** — FAIL means no
promotion, no draft entry in `docs/.pending/`. No structural failure
either: the sklearn GBM converged, the purged K-fold CV ran cleanly
(baseline accuracy 50.3% ± 2.0% on IS — consistent with the up-rate
of 0.561 being the naive-majority benchmark), the panel trained on
22 815 rows × 10 features × 7 tickers without NaN or shape issues,
and the pipeline produced all expected artifacts.

## Top-line metrics (winner config)

| Split | Bars | Sharpe | CAGR | MaxDD |
|-------|-----:|-------:|-----:|------:|
| IS (2005-01-03 → 2017-12-29) | 3271 | **1.250** | 24.16% | −20.76% |
| OOS (2018-01-01 → 2023-12-29) | 1510 | **0.231** | 2.62% | −35.32% |
| FWD (2024-01-01 → 2026-04-14) | 572 | **1.165** | 15.16% | −14.09% |
| FULL (2005-01-03 → 2026-04-14) | 5353 | 0.831 | 10.98% | −35.32% |
| **SPY OOS benchmark** | 1510 | 0.658 | 12.00% | −33.70% |

Portfolio underperforms SPY buy-hold in OOS by **−9.4 pp CAGR** with
a worse drawdown (−35.32% vs −33.70%). IS-to-OOS Sharpe decay is
**1.250 → 0.231** (−82%) — the GBM is learning IS-specific
correlations that do not generalise. IS MaxDD of −20.76% swells to
−35.32% on OOS, confirming regime-shift intolerance.

## Winner config (grid centre)

```
# Sklearn GradientBoostingClassifier — drop-in for LightGBM
n_estimators        = 300       [ml_for_algo_trading, p.388, p.397-399]
max_depth           = 3         [ml_for_algo_trading, p.397-398]
learning_rate       = 0.05      [ml_for_algo_trading, p.388]
random_state        = 42

# Labels & training protocol
label_horizon       = 5 days    [ml_for_asset_managers, p.10 §1.5]
label_type          = binary up/down (2-class)  [ml_for_asset_managers, p.21 §1.9]
threshold P(up)     = 0.55      [advances_fin_ml, p.208-211 CSCV]
purged_kfold_splits = 5         [advances_fin_ml, p.103-110]
purged_embargo      = 5 × H     [ml_for_asset_managers, p.8 §1.4.2]

# Portfolio & friction
position_size       = 0.50      [ml_for_algo_trading, ch.5 p.124-135]
rebalance_days      = 5         (= label horizon; no leak)
spread_one_way_pct  = 0.0005    [plan §3.2 Banco Inter + 5bps slip]
commission_per_trade = 0        [plan §3.2 Inter zero on US ETFs]
tax_rate            = 0.15      [mandate §1 + plan §3.2 BR CG]
```

### Feature set (panel-shared, 10 features)

Per [ml_for_algo_trading, ch.4 p.82-93]. Feature importances from the
full-IS GBM:

| Feature | Importance | Citation |
|---|---:|---|
| `vol_60` — 60d realized daily-ret std | 0.217 | [ml_for_algo_trading, p.99] |
| `corr_spy_60` — 60d rolling corr vs SPY | 0.172 | [ml_for_algo_trading, ch.7 p.188-191] |
| `vol_20` — 20d realized std | 0.140 | [ml_for_algo_trading, p.99] |
| `mom_zscore_60` — 60d momentum z-score | 0.139 | [stocks_on_the_move, p.81] |
| `ret_20` — 20d return | 0.112 | [ml_for_algo_trading, p.86] |
| `ret_5` — 5d return | 0.085 | [ml_for_algo_trading, p.86] |
| `rsi_14` — canonical RSI | 0.073 | [ml_for_algo_trading, p.86] |
| `ret_1` — 1d return | 0.043 | [ml_for_algo_trading, p.86] |
| `regime_spy200` — SPY > SMA200 binary | 0.013 | [stocks_on_the_move, p.66-67] |
| `dow` — day of week | 0.005 | [ml_for_algo_trading, p.86-87] |

**Observation:** the model is weighted 51.6% toward volatility + market-
corr features, which makes it a regime classifier rather than a
direction predictor — consistent with Family H's (AMH HMM) earlier
diagnosis and with the reported **median hold of 457.5 days** (only
10 distinct hold-runs over 21 years). This is volatility gating, not
swing trading.

### Universe

7-ETF multi-asset panel: `SPY, QQQ, TLT, GLD, EEM, XLF, XLE`.
Cites [ml_for_algo_trading, ch.4 p.82-93] multi-asset panel design;
[stocks_on_the_move, p.238-239] liquidity proxy; plan §2.1 universe
policy (broker-feasible ETFs, bond + commodity + EM diversifiers).

### Trim note

GLD inception (2004-11-18) is the latest universe member. IS start
relaxed from the plan default (2001-05-14) to **2005-01-03** to give
every ticker 200-day SMA warmup + 60-day feature warmup + 5-day label
forward window before the IS period begins. Trim is documented
honestly per plan §2.1 ("Trim honestly if universe ticker inception
is later").

### ML library note

LightGBM / XGBoost are **not installed** in the project's venv.
`sklearn.ensemble.GradientBoostingClassifier 1.8.0` substitutes per
[ml_for_algo_trading, p.390-400]: same leaf-wise depth + same
learning-rate / n_estimators philosophy. The training protocol
(n_est=300, depth=3, lr=0.05, seed=42) matches Jansen's recipe for
sklearn GBM on low-SNR finance data. This is a documented shortcut,
not a bug.

## §Differentiation from V2-L3 AFML (rejected lead)

V2-L3 AFML was retracted in Phase 3.5f under the honest engine. Family
J is **not** a re-run of V2-L3 — every layer of the pipeline differs:

| Axis | V2-L3 AFML (rejected) | Family J (this run) |
|---|---|---|
| Universe | Single ticker (XLF) | 7-ETF panel (SPY, QQQ, TLT, GLD, EEM, XLF, XLE) |
| Label paradigm | Triple-barrier + meta-label (precision filter over a primary EMA-50 cross) `[advances_fin_ml, p.50-60]` | Forward 5d **sign** binary classification — the classifier IS the edge generator `[ml_for_asset_managers, p.21 §1.9]` |
| Primary signal | EMA-50 cross (deterministic, pre-existing) | None — GBM predicts P(up) directly |
| Model | RandomForest on meta-labels | GradientBoostingClassifier on raw features |
| Training regime | Per-ticker, per-event | Panel-trained (single model across 7 tickers) |
| Sizing | Bet size from meta-label probability (AFML §3.7) | Flat 50% of equity per qualifying ticker, total capped at 100% |
| Validation | Fold-CV on meta-labels | Purged K-fold CV (5 splits, 5-day embargo per AFML §7.4) |

The plan brief explicitly called out V2-L3 as an excluded architecture;
Family J satisfies that exclusion across every axis.

## §Track choice (J1 vs J2)

The plan offered two tracks:

* **J1 — Jansen-style gradient boosting on engineered features.**
  Classic supervised learning with hand-designed financial features
  (returns lags, vol, RSI, corr vs market, regime indicator). Training
  recipe from Jansen ML4T [ml_for_algo_trading, ch.4 p.82-93; ch.12
  p.390-400].
* **J2 — LdP fractional-differentiation regression.** López de Prado's
  FFD-preserving-memory pipeline [advances_fin_ml, ch.5 p.75-95]: find
  minimum `d` such that FFD series is ADF-stationary at 5%, then feed
  FFD features into a regression head.

**Chosen: J1.** Three reasons:

1. **Sign classification dominates size regression on financial data**
   [ml_for_asset_managers, p.21 §1.9 FAQ]: "failing to predict the sign
   is an actual loss; failing to predict the size is an opportunity
   cost." J2's regression head is the strictly weaker formulation
   when our label domain is swing directional trades.
2. **Feature interpretability for citation discipline.** Each J1
   feature has a direct book citation (see feature table above). J2
   FFD features are composite and harder to defend individually.
3. **Runtime.** 16 GBM configs × 5-fold CV + full train × 7-ticker
   prediction span = 16 minutes wall-clock. J2 would also need ADF
   sweep per ticker per feature, roughly 2-3× runtime without moving
   the needle on the edge gates (which are what killed Family J
   regardless of feature set).

If J2 were run, we would expect an even worse OOS Sharpe: fractional
differentiation preserves memory for regression on *future return
magnitude*, but the OOS failure here is not a feature-memory problem
— it's that the IS→OOS regime shift (2017→2018: low-vol bull → rate-
shock regime) makes the IS-learned volatility/correlation map
invalid. Changing feature representation cannot fix that.

## Grid summary for PBO / DSR

16 configs across `{n_estimators: 100, 300} × {max_depth: 3, 5} ×
{threshold: 0.55, 0.60} × {label_horizon: 5, 10}`. Aligned matrix
shape 5353 × 16.

* **IS full-period Sharpe range:** 0.60 → 1.54
* **OOS Sharpe range:** −0.20 → +0.45
* **PBO (CSCV, 10 blocks, 252 combinations):** **0.016** — low not
  because the strategy is robust, but because *every* config is
  uniformly mediocre OOS. Low PBO + low OOS Sharpe = all configs are
  equally bad, rather than one config being overfit relative to
  others. This is a known PBO interpretation caveat
  [advances_fin_ml, p.208-211].
* **DSR p-value (n_trials=16):** **0.890** — observed Sharpe not
  distinguishable from noise-tested-at-16.

## Bootstrap CIs (stationary block bootstrap, 99.9%)

* **OOS 99.9% CI on Sharpe:** [−0.844, +1.728] — straddles zero,
  **gate 1 FAIL**.
* **FULL 99.9% CI on Sharpe:** [+0.363, +1.544] — all-positive,
  **gate 1b PASS**; driven by the strong IS leg.

## Walk-forward (8 windows, 30% DD cap)

* **Profitable ratio:** 8/8 (all windows have positive return) — but
* **Max window DD:** **35.32%** — above the 30% cap.

Gate 6 requires BOTH the 6/8 ratio AND the DD cap — fails because of
DD. A profitable-ratio-only WF would have PASSED.

## Cost×2 sensitivity (gate 13)

Canonical spread 5 bps one-way → doubled to 10 bps. OOS Sharpe drops
from **0.231 → 0.138**; gate 13 requires cost×2 OOS Sharpe > 1.0 →
**FAIL**. The strategy is already marginal at base cost and loses
the residual edge under stress.

## Cross-library concordance (gate 9)

Deferred per Phase 3.5b/3.5f precedent. Family J's pipeline is a pure
return-series simulator (no bar-level execution, no slippage model,
no leverage-drag quirks); an independent numpy replay of the return
math yields Δ = **0.0000 pp** on OOS CAGR. See
`reports/phase_3_6/j_ml_classical/cross_lib_check.md` for the full
rationale — bt/vectorbt/backtrader ports would reimplement the same
`prev_weight × ret − spread × |Δw|` math and are therefore redundant
for this engine shape.

## 13-Gate checklist

| # | Gate | Threshold | Value | Verdict |
|---|---|---|---|---|
| 1 | Bootstrap 99.9% CI low > 0 on OOS | > 0 | −0.844 | **FAIL** |
| 1b | Bootstrap 99.9% CI low > 0 on FULL | > 0 | +0.363 | PASS |
| 2 | OOS Sharpe ≥ 1.5 | ≥ 1.5 | 0.231 | **FAIL** |
| 3 | OOS CAGR ≥ 13% (CDI soft-floor) | ≥ 13% | 2.62% | **FAIL** |
| 3-hard | OOS CAGR ≥ 30% (hard target) | ≥ 30% | 2.62% | **FAIL** |
| 4 | OOS MaxDD ≥ −25% | ≥ −25% | −35.32% | **FAIL** |
| 5 | FWD Sharpe > 0 | > 0 | 1.165 | PASS |
| 6 | WF 8-window ≥6/8 AND max DD ≤ 30% | both | 8/8 + 35.32% DD | **FAIL** |
| 7 | Median hold ≥ 5 trading days | ≥ 5d | 457.5d | PASS* |
| 8 | IR vs SPY buy-hold OOS ≥ 0.3 | ≥ 0.3 | −0.922 | **FAIL** |
| 9 | Cross-lib ≥ 2/3 within ±3pp OOS CAGR | 2/3 | handroll Δ=0pp | DEFER (see §) |
| 10 | Data concordance ≤ 1pp | deferrable | single source | DEFER (Tiingo only) |
| 11 | PBO < 0.5 | < 0.5 | 0.016 | PASS** |
| 12 | DSR p < 0.05 | < 0.05 | 0.890 | **FAIL** |
| 13 | Cost×2 OOS Sharpe > 1.0 | > 1.0 | 0.138 | **FAIL** |

\* Gate 7 PASS is perverse — 457.5d is so long the strategy barely
rebalances, making the "swing" framing inapt (plan §0 targets 5-15d
holds). Reported honestly per the gate definition but does not
indicate the intended behaviour.

\** Gate 11 PASS is perverse — PBO is low because *every* grid config
is uniformly mediocre OOS, not because the winner is robust. Low PBO
+ low OOS Sharpe across the grid = all configs equally bad. See
§Grid summary.

**Binding fails:** 8 (gates 1, 2, 3, 4, 6, 8, 12, 13). Verdict:
**FAIL** (plan §5.3 — PARTIAL requires ≤1 binding fail; WINNER
requires 0).

## What killed it

1. **Gates 1, 2, 3, 4, 8 — the OOS edge is not there.** OOS Sharpe
   0.23, OOS CAGR 2.62%, IR vs SPY −0.92, MDD −35%. The IS→OOS
   Sharpe decay 1.25 → 0.23 is diagnostic: the GBM learned IS-era
   vol/correlation patterns that broke in the 2018 rate-shock
   regime, the 2020 COVID shock, and the 2022 bear.
2. **Gate 12 DSR p=0.890.** Across 16 grid configs, the observed
   winner Sharpe is indistinguishable from noise-tested-at-16.
3. **Gate 13 cost×2 Sharpe 0.138.** Even the tiny residual edge
   evaporates when spread doubles.
4. **Gate 6 WF DD 35.32%.** Despite 8/8 profitable windows, one
   window blew through the 30% cap.

## Positive signals (insufficient to rescue)

* FWD Sharpe 1.17 / CAGR 15.16% — but on a single 2.2-yr forward
  window, not robust enough to override 6 years of OOS failure.
* PBO 0.016 — honest, because all configs are equally mediocre.
* IS Sharpe 1.25 — shows there IS a pattern in IS data, it just
  doesn't transfer.

## Artifacts

* `reports/phase_3_6/j_ml_classical/AGGREGATE.md` — this document
* `reports/phase_3_6/j_ml_classical/AGGREGATE.json` — structured metrics
* `reports/phase_3_6/j_ml_classical/daily_returns.parquet` — winner OOS+FWD daily returns
* `reports/phase_3_6/j_ml_classical/daily_returns_cost2x.parquet` — cost×2 sensitivity returns
* `reports/phase_3_6/j_ml_classical/feature_importance.csv` — GBM feature ranking
* `reports/phase_3_6/j_ml_classical/config_grid.csv` — 16-config grid summary
* `reports/phase_3_6/j_ml_classical/cross_lib_check.md` — gate-9 rationale
* `src/ai_trade/backtest/strategies/phase3_6_j_ml_classical.py` — strategy module
* `scripts/run_phase3_6_j_ml_classical.py` — 13-gate runner
* `scripts/run_phase3_6_j_cross_lib.py` — cross-lib check
* `logs/phase3_6_j_ml_classical.log` — training / CV / run log

## Citations

* Overall ML4T workflow and GBM hyperparameter recipe:
  `[ml_for_algo_trading, preface p.xiii; ch.1 p.13; ch.4 p.82-93;
  ch.5 p.124-135; p.86; p.99; p.373; p.388; p.390-400; p.397-399]`.
* Panel features: `[ml_for_algo_trading, ch.7 p.188-191]` for
  market-beta factor; `[stocks_on_the_move, p.81]` for momentum z-score;
  `[stocks_on_the_move, p.66-67]` for regime filter.
* Classifier over regression for sign prediction:
  `[ml_for_asset_managers, p.21 §1.9 FAQ]`.
* Purged K-fold + embargo widths:
  `[ml_for_asset_managers, p.8 §1.4.2]`; `[advances_fin_ml, p.103-110]`.
* No walk-forward retraining (frozen IS-trained model):
  `[ml_for_asset_managers, p.3-8]`; `[advances_fin_ml, p.31-34]`.
* CSCV / PBO / DSR / bootstrap:
  `[advances_fin_ml, p.196-211; p.273-275; ch.11]`.
* V2-L3 AFML exclusion reference:
  `reports/phase_3_5f/honest_revalidation/v2_l3_afml/AGGREGATE.md`
  (retracted lead); `[advances_fin_ml, p.50-60]` for the triple-
  barrier meta-label paradigm we explicitly did **not** re-use.
* Plan mapping: `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md`
  (Family J brief, §5.5 gates).

---

## §Summary one-liner

Family J is a clean multi-asset GBM panel classifier that learned
IS-regime noise, fails 8 hard edge gates out-of-sample, and should
not be promoted. Contributes **+1 to the FAIL counter** (9 FAIL /
0 PARTIAL / 0 WINNER after this run; 1 slot to escalation).
