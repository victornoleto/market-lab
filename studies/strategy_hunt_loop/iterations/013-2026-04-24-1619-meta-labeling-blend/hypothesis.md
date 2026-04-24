# Iteration 013 — Meta-labeling classifier (AFML ch.3) on iter 008 vol-managed SPY+TLT blend

## Hypothesis

A secondary logistic-regression classifier trained on **two features
orthogonal to the blend's realized-vol inputs** — rolling 60-day
SPY-TLT correlation and the rolling z-score of VIX — decides bar-by-bar
whether to take iter 008's pre-committed vol-managed SPY+TLT blend
position or go flat. Training is done via walk-forward: each year the
model is refit on the past 1000 trading days, then applied to the
subsequent 252-bar forward window with no look-ahead. When the
predicted probability that the next bar's blend return is positive
exceeds 0.5, we take the full iter 008 blend weights; otherwise we hold
cash.

This is the **meta-labeling** architecture of AFML chapter 3:

> "The secondary model decides the size of the bet, not its side…
> trained on features that are not available to the primary model."
> `[advances_fin_ml, ch.3, p.50-56]`

The primary model here is iter 008's deterministic inverse-variance +
variance-scaling blend — it always wants full weights. The secondary
model vetoes the full weights when its two orthogonal features signal
an unfavorable regime (e.g., SPY-TLT correlation turning positive, VIX
at historically elevated levels).

The 2022 stock-bond regime flip (SPY-TLT correlation transitioned
from −0.30 to +0.20) is the canonical example where iter 008 was hurt
structurally: variance-scaling kept full leverage while both legs fell
together. A meta-model with correlation as a feature can learn this
regime.

## Primary citation

`[advances_fin_ml, ch.3, p.50-56]` — meta-labeling architecture (López
de Prado 2018): secondary model decides bet size using features
orthogonal to primary signal. This is exactly the pattern we apply on
top of iter 008's blend.

## Additional citations

- `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` lag (no look-ahead);
  extended here to features (shift-1 guarantees forecast bar-t uses
  only info known at close of bar-t-1).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials; our
  meta-model adds 3 trials (1 pre-committed spec × 3 datasets).
- `[advances_fin_ml, ch.7, p.103-112]` — embargoed/purged walk-forward
  CV for financial ML; we use the simpler expanding-then-rolling window
  split which respects temporal order.
- `[regime_change, ch.2, p.5-6]` — regime-change principle as
  justification for feature choice (correlation regime indicator).
- `[systematic_trading, ch.12, p.190-192]` — VIX as a risk/sizing
  covariate (Carver's forecast-diversification framing).
- `[risk_parity, p.10-11, ch.1]` — base blend mechanism (iter 008).
- Moreira & Muir (2017), *JoF* 72(4), 1611-1644 — variance-scaling
  form used by the primary blend.
- Web: López de Prado (2018) AFML — *Advances in Financial Machine
  Learning*, Wiley. ISBN 978-1119482086. Chapter 3 defines
  meta-labeling.

## Edge source

SPY 1x buy-hold cannot express "skip the equity allocation when
cross-asset correlations break down" — that information requires
observing SPY-TLT joint dynamics, which a single-asset benchmark by
construction cannot use. Iter 008's blend uses the magnitudes of each
leg's variance but IGNORES the correlation term when allocating
weight; meta-labeling adds that missing information via ρ_60 plus the
forward-looking risk premium encoded in VIX.

## Datasets

- **educational** (SPY+TLT 2002-07-26 → 2026-04-15, 24y): longest TLT
  window — contains 2008 GFC, 2020 COVID, 2022 regime flip. Needed for
  meta-model to observe multiple regime transitions during training
  windows.
- **spy_real** (SPY+TLT 2009-06-25 → 2026-04-15, 17y): post-GFC. Tests
  whether the meta-model learns the 2022 regime switch with a training
  window that only saw 2010-2021 normal correlation regime first.
- **ndx_real** (QQQ+TLT 2010-02-12 → 2026-04-15, 16y): tech-heavy
  equity leg. Tests cross-ticker generalisation — same trained-model
  *architecture* refit on QQQ+TLT data.

## Kill criteria (pre-committed)

All five are single-observable, binary, and evaluated against iter
008's published reference metrics (Sharpe edu 0.865 / spy 1.000 / ndx
1.021). The first trigger halts further investigation and marks iter
013 as a dead-end or structural-overlay.

- **Kill #1 (thesis falsification)** — if Sharpe of the meta-labeled
  strategy regresses on **BOTH** spy_real and ndx_real vs iter 008 by
  more than 0.02, the classifier is adding no information (or actively
  harmful) on real data → meta-labeling on this blend is dead.
- **Kill #2 (CAGR collapse)** — if CAGR_candidate < 0.75 × benchmark
  CAGR on any 2 of 3 datasets, the classifier's "go flat" decisions
  destroy compounding without corresponding MDD reduction.
- **Kill #3 (score < 70)** — if final score after robustness bonus is
  below 70, the approach isn't materially better than the ranked
  iter 008/010 top (both 74). 70 is chosen as "non-regression
  tolerance" — 4 pts below current high still meaningful.
- **Kill #4 (degenerate classifier)** — if the meta-model's predicted
  probability has std < 0.05 over the full history on ≥ 2 datasets,
  the classifier has effectively collapsed to constant → it's not
  making real decisions, and any score uplift is statistical noise.
- **Kill #5 (cross-lib parity)** — if the numpy-reference implementation
  of the meta-labeling pipeline diverges from the engine's (pandas +
  sklearn) CAGR by more than 3 pp on any dataset, G7 fails and the
  pipeline has a hidden bug.

## Structural novelty verification (vs DEAD_ENDS.md)

| dead-end | structural distinction here |
|---|---|
| Binary macro overlay on blend (iter 009, 012) | Multi-feature, learned, non-binary (sigmoid probability output); uses features the blend CANNOT see (cross-asset correlation + options-implied risk) |
| Momentum overlay on blend (iter 007) | Features are correlation + VIX, not trend / return-based |
| Single-asset vol-adaptation (iter 004, 005) | Still a blend; meta-model sits on top of it |
| Weekly/monthly cadence (iter 011) | Daily cadence preserved |
| Sector rotation / equal-notional (iter 002, 003) | Not ranking-based; no universe expansion |
| Vol-managed N-leg saturation (iter 010) | Same 2-leg base; adds ML decision layer, not more legs |
| 12-config grid blend overfit (iter 006) | Single pre-committed model architecture (one feature set, one window, one threshold) |

**Conclusion: structurally novel.** The meta-labeling ML layer adds an
informationally orthogonal decision stage; no dead-end applies.

## Pre-committed configuration

| parameter | value | citation / rationale |
|---|---|---|
| primary model | iter 008 `vt15_L21_cap20` | `[risk_parity, p.10-11]` + Moreira-Muir 2017 |
| secondary model | `sklearn.linear_model.LogisticRegression(C=1.0, penalty="l2", solver="lbfgs", max_iter=1000, random_state=42)` | Default L2-regularised logistic; prevents overfit on 2 features |
| feature 1 | `ρ_60(SPY, TLT)` = rolling 60-day correlation of daily returns | `[regime_change, ch.2]` |
| feature 2 | VIX z-score (rolling 252-day mean & std) | `[systematic_trading, ch.12]` |
| label | `1` if next-bar blend net return > 0, else `0` | AFML ch.3 meta-labeling canonical |
| training window | rolling 1000 bars (≈ 4 years) | AFML ch.7 — long enough to see regime transitions |
| retrain cadence | every 252 bars (annual) | Budget: 17y ÷ 1y = ~17 refits per dataset |
| decision threshold | `p_hat > 0.5` → full blend; else flat | Default 50/50 cutoff |
| lag | features lagged by 1 bar | `[advances_fin_ml, p.162-164]` no look-ahead |
| warm-up | drop first 1260 bars (5y) — need training window + feature lookback | Ensures first decision uses a fully-populated window |

**Combined cfg_id**: `vt15_L21_cap20 × meta_lr_rho60_vixz252_w1000_r252`

## Expected budget

- **Configs tested**: 1 pre-committed architecture × 3 datasets = 3 trials.
- **Cumulative n_trials**: 4252 (post iter 012) → 4255 (post iter 013).
- **Wall-time**: ~60-90 min (data load + 17 retrains × 3 datasets +
  gates). Under the 2h cap.
- **Files to create**:
  - `meta_labeling.py` — feature engineering + training + gating loop.
  - `meta_labeling_numpy_reference.py` — numpy reference for G7.
  - `run_backtests.py` — 3-dataset runner (reuses iter 008 base).
  - `compute_gates_and_score.py` — 7-gate battery.
  - `tests/test_meta_labeling.py` — TDD specs (feature shift, no
    look-ahead, fitted-on-warm-up-bars-only, cross-lib parity).

## Implementation plan

1. **Write TDD specs** — feature lag ≥ 1 bar, training-window purity
   (no future bars), classifier rejects degenerate input (all-positive
   labels in a window), numpy-parity spec.
2. **Feature engineering** — implement `compute_features(r_spy, r_tlt,
   vix)` returning lagged `(ρ_60, vix_zscore_252)` at each bar.
3. **Meta-labeling pipeline** — implement `apply_blend_with_meta(...)`
   that (a) runs iter 008's blend un-gated, (b) generates binary
   labels for each bar, (c) walks forward retraining every 252 bars,
   (d) gates blend positions by predicted probability.
4. **3-dataset backtest** — `run_backtests.py` mirrors iter 009's
   pattern; writes `results.json` with metrics + returns + gate
   fire-rate + label base rate per dataset.
5. **Gate battery** — `compute_gates_and_score.py` mirrors iter 009's
   7-gate harness. G1 PBO is vacuous (N=1 single pre-committed cfg,
   same as iter 008/009). G7 uses numpy-reference implementation.
6. **Score + verdict** — uses `scoring.score_strategy` with
   `cumulative_n_trials=4255`.
7. **Final report + memory update** — honest verdict whether
   meta-labeling clears 74/100 ceiling or falls into the same
   "correlated-with-variance-scaling" trap as iter 009/012.

## Decision trigger for subsequent iterations

- If score > 74 AND Sharpe improves on 2/3 datasets: direction
  validated, iter 014 expands feature set (cross-asset momentum,
  implied-skew proxy, macro-state encoding).
- If score 65-74 AND Sharpe uplift on 1/3: direction marginal,
  iter 014 may try alternate classifier (random forest) or different
  feature pair.
- If score < 65 OR meta-classifier degenerate: meta-labeling on this
  blend with these features is a dead-end → add to DEAD_ENDS.md and
  pivot to Option G (return-stacked ETF rotation) or revisit the
  backlog (HMM regime-switching, cross-sectional factor).
