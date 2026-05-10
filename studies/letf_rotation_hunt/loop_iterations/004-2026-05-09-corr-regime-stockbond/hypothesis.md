# 004-2026-05-09-corr-regime-stockbond — HYPOTHESIS

**Iter:** 004 / 50 (loop)
**Slug:** corr-regime-stockbond
**Date (UTC):** 2026-05-09
**n_configs:** 6 (≤ 8 protocol cap)
**cumulative_n_trials_global before:** 444
**cumulative_n_trials_global after:** 450

## Hypothesis

The winner's two-leg rotation (QLD ON / ZROZ OFF) implicitly relies on the
**stock–bond correlation being negative** for the OFF leg to behave as a
hedge. Edward Qian (`risk_parity, p.80-81, ch.4`) documents that during
**Risk-on/Risk-off (RORO) regimes**, "almost all risky assets move together"
while safe assets (USTs) maintain a strongly negative correlation with risky
assets — but the regime can flip. The 2022_rates loss (which iters 001/002/003
all failed to rescue) is the canonical example: from Q4-2021 through Q4-2022,
60-day rolling ρ(QLD,ZROZ) crossed 0 and stayed positive, so when the trend
signal flipped OFF the strategy rotated *into* a falling-bond hedge that no
longer hedged. Qian Ch.5 formalises this via diversification return
(`risk_parity, p.110, ch.5`): when correlation flips positive,
diversification return collapses and the leveraged-OFF leg amplifies losses.

This iter tests a **stock–bond correlation regime master-gate**: when the
60-day rolling correlation between QLD daily returns and ZROZ daily returns
exceeds a threshold, the strategy redirects (a) the OFF leg to CASHX (FFR
proxy), or (b) the entire allocation to CASHX, since the diversification
hedge has structurally broken.

The correlation-regime gate is **mechanically orthogonal** to all three prior
loop iters:

| Iter | Mechanic | Information |
|---|---|---|
| 001 | yield-curve OFF rotation | term-premium level (slope) |
| 002 | vol-DD killswitch | own-strategy magnitude (drawdown × σ) |
| 003 | calendar / Halloween | exogenous date function (month) |
| **004** | **ρ(QLD,ZROZ) regime** | **cross-asset second moment** |

No prior iter tested cross-asset second-moment information.

## Citations

**Primary:** `[risk_parity, p.80-81, ch.4]` — Qian on Risk-on/Risk-off (RORO)
regime: stocks/commodities correlation reached 0.71 in 2009-2012 while USTs
held −0.58 to −0.53 vs risky assets. Documents the mechanism by which
stock–bond correlation can flip from negative (normal) to positive (RORO
breakdown), eliminating diversification value.

**Secondary:**
- `[risk_parity, p.110, ch.5]` — Qian on diversification return:
  $e_v = -0.5 \cdot w_1 w_2 \cdot 2\rho_{12}\sigma_1\sigma_2$. When $\rho > 0$
  the diversification return reverses sign and a leveraged 2-leg portfolio
  loses its compounding benefit.
- `[ml_for_algo_trading, ch.9]` — Jansen on regime classification with rolling
  state features; rolling correlation is the simplest second-moment regime
  feature (Markov-switching alternatives covered in `time_series_hamilton`
  ch.22 — archived but cited as theoretical backbone).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (G2/global
  denominator = 444 + 6 = 450 after this iter).
- `[systematic_trading, p.180-190]` — Carver carry / regime filter shape; same
  overlay pattern used by iters 001/002/003.

## Configs

All configs share the trend ON signal `vote-of-2 of {SMA250, SMA100,
vol_21d<40%, AR(1)_30d>0}` on QLDSIM (winner replica). The OFF asset and the
correlation-regime override differ per config.

| # | Name | Corr threshold | Window | Override scope |
|---|---|---:|---:|---|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_corrgate_off_baseline` | — (no gate) | — | baseline |
| 2 | `qld_voteK2_..._corrgate_t000_60d_offleg_cashx` | ρ > 0.00 | 60d | OFF leg → CASHX |
| 3 | `qld_voteK2_..._corrgate_t020_60d_offleg_cashx` | ρ > 0.20 | 60d | OFF leg → CASHX |
| 4 | `qld_voteK2_..._corrgate_t030_60d_offleg_cashx` | ρ > 0.30 | 60d | OFF leg → CASHX (stricter) |
| 5 | `qld_voteK2_..._corrgate_t020_120d_offleg_cashx` | ρ > 0.20 | 120d | OFF leg → CASHX (slower) |
| 6 | `qld_voteK2_..._corrgate_t020_60d_master_cashx` | ρ > 0.20 | 60d | entire portfolio → CASHX |

The grid sweeps **two orthogonal axes** + one mechanism switch:

- **Threshold axis (configs 2-4):** 0.00 / 0.20 / 0.30 at fixed 60d window.
  Threshold 0.00 = "any positive correlation triggers"; 0.20 = "meaningful
  positive correlation"; 0.30 = "strong RORO regime."
- **Window axis (config 5 vs config 3):** 60d vs 120d at fixed threshold 0.20.
  Tests whether faster regime detection (60d) is worth the noise vs slower
  (120d) which lags into-and-out-of regimes.
- **Override scope (config 6 vs config 3):** OFF-leg-only override vs
  whole-portfolio override at fixed threshold 0.20 / 60d. Tests whether the
  trend signal alone can navigate a RORO regime (OFF-leg switch is enough)
  or whether the entire vote-of-K stack should defer to RORO (master switch).

This is a clean orthogonal grid (not a single-axis sweep): G1 PBO should
benefit from the mechanic diversity, similar to iter 002's clean 0.159 PBO.

Signal lag (1-day) preserved: the correlation gate computed at close of t-1
applies at open of t — same convention as the winner's other gates.

## Datasets

Mirrors closed-study set for direct comparability:
- `lh_56y`: 1970-01-01 → 2026-04-30 (SPYSIM/QLDSIM/ZROZSIM/CASHX)
- `modern_1990`: 1990-01-01 → 2026-04-30
- `spy_real`: 2003-01-01 → 2026-04-30 (real SPY post-inception)
- `ndx_real`: 2010-02-01 → 2026-04-30 (real QQQ post-inception)

The QLD/ZROZ correlation regime is most informative in 2003+ where real-asset
data is available, but pre-1985 synth Bayesian-prior'd correlations should
still capture the broad regime structure (the stock–bond correlation regime
flips in 1973-1974, 1979-1981, 1994, 2022 — multiple regime crossings within
the lh_56y window provide statistical content).

## Pre-registered KILL_LOOP conditions

- **KILL_LOOP #1 (success-tag):** if any config has Sortino_lh56y > 1.3746
  AND `winner_conditions_met=True` AND pct_time_above_benchmark_lh56y ≥ 0.95
  → record `beats_winner=true` (loop continues per protocol §"Beats-winner
  test"). Probability assessed below in expected outcomes.
- **KILL_LOOP #2 (decisive-fail):** if all 5 corr-gate variants return
  Sortino_lh56y < 1.10 → cross-asset correlation regime gating is dead in
  this LETF context; pivot next iter to a fundamentally different mechanic
  (e.g. multi-asset rotation with inverse-vol weighting, breadth indicators,
  VIX-percentile / VRP).
- **KILL_LOOP #3 (replica-sanity):** if config #1 (baseline replica)
  Sortino_lh56y differs from 1.2841 (iters 001/002/003 baseline) by > 0.05
  absolute → engine drift; flag INCOMPLETE and trust comparative deltas
  across configs only.
- **KILL_LOOP #4 (over-suppression):** if any corr-gate variant's
  pct_time_above_benchmark_lh56y drops below 0.85 → corr-gate fires too
  often (likely the t000 threshold or master_cashx mechanism). Tag config
  "OVER_SUPPRESS" in SUMMARY — informational only.
- **KILL_LOOP #5 (corr-regime-non-event):** if all 5 corr-gate variants have
  `corrgate_active_pct_lh56y < 5%` (gate fires < 5% of trading days) → the
  hypothesis is unfalsifiable in this dataset because the regime crossings
  are too rare to test. Tag iter UNDERPOWERED.

## Expected outcomes (pre-registration; honest band)

- **Sortino_lh56y range expected:** 1.10–1.40 across all 6 configs.
- **Best plausible scenario:** config 3 (`t020_60d_offleg_cashx`) gains
  ~0.03–0.07 Sortino over baseline by sidestepping 2022 correctly while
  rarely firing in the long history (most positive ρ episodes are brief).
  pct_time_above_benchmark stays near 1.0000 because the gate only fires
  during defensive periods (when in OFF state).
- **Plausible failure mode (most likely):** the correlation gate is
  *correlated with the trend signal itself* in many regimes — when stocks
  are crashing the vote-of-K already flips OFF, so the corr-gate adds little
  marginal information. In that case all configs cluster within ±0.02
  Sortino of baseline.
- **Most realistic outcome:** tier PROMISING/STRONG with sortino_edge in
  [-0.05, +0.05] band. The single 2022 rescue (which would gain ~0.04 lh_56y
  Sortino if successful) can plausibly clear the +0.05 anti-curve-fit margin
  ONLY if the gate doesn't simultaneously trigger spurious-OFFs in 2008-Q4
  or 2020-Q1.
- **WC compliance:** OFF-leg-only configs (2-5) likely preserve WC because
  the override only fires when the strategy is already defensive. Master
  config (6) more likely to break WC because it overrides ON state during
  ρ>0.20 regimes (e.g., 1994 or 2008-Q3 brief positive crossings).
- **Beats-winner probability:** **~10-20%**. The mechanism is genuinely new
  (cross-asset second moment) and Qian's RORO thesis is well-grounded, BUT
  the conjunction (Sortino > 1.3746 AND WC met AND pct_above ≥ 0.95) is
  hard. Most likely outcome is a small positive Sortino edge that doesn't
  clear the +0.05 margin — informative for hypothesis-discrimination but
  not a deploy candidate.

## INCOMPLETE flags / caveats

- **Correlation gate is computed at close of t-1 with a 1-day lag** — no
  forward-looking leakage by construction. The 60d window means the gate
  state in early-2022 reflects pre-Jan-2022 correlation regime, so partial
  warmup is expected for the 2022 rescue specifically (gate likely fires
  by Mar-2022 at the earliest).
- **Synth caveat (pre-1985):** ZROZSIM is a duration-aware synthetic
  long-treasury proxy; its correlation with QLDSIM (formula-derived NDX)
  pre-1985 is mechanically tied to the synth assumptions. Comparative
  deltas across configs in the lh_56y window remain valid because all
  configs see the same synth baseline.
- **Tax/fees:** gross only this iter (matching closed-study convention).
  CASHX returns are FFR-tracked, so the override-to-cash period earns
  short-rate yield (which can be substantial — e.g. 2007 5% FFR or 2024
  5.5% FFR).
- **Threshold values are not arbitrary:** 0.00 = sign flip, 0.20 ≈ Qian's
  "meaningful positive" benchmark, 0.30 ≈ classical RORO regime threshold
  in academic literature. Sweep covers the interpretable range without
  over-fitting (compare to a [-0.5, +0.5] step-0.1 sweep which would have
  high G1 PBO inflation risk).
- **Window choice (60d vs 120d):** 60d is the standard regime-detection
  window in `[ml_for_algo_trading, ch.9]` and gives Q-on-Q sensitivity;
  120d is half-year, slower, more stable. We do NOT sweep additional
  windows because a 4-step window grid would inflate trial count without
  adding interpretive value.
- **Single 2022_rates target:** corr-regime is hypothesis-targeted at the
  2022 dual-fall, NOT a pan-crisis rescue. We expect at most modest
  improvements in 2000_dotcom (where stock-bond correlation also briefly
  went positive), no improvement in 2008_GFC (already rescued by vol-21d
  gate), no improvement in 2020_COVID (corr regime mostly normal).

## Beats-winner test (frozen per protocol §"Beats-winner test")

```python
beats_winner = (
    sortino_lh56y > 1.3746              # 1.3246 + 0.05 anti-curve-fit margin
    and winner_conditions_met
    and pct_time_above_benchmark_lh56y >= 0.95
)
sortino_edge_vs_winner = sortino_lh56y - 1.3246
```

`winner_benchmark_sortino = 1.3246`,
`winner_benchmark_iter = "022-2026-05-06-T3d-extended-grid"`,
`winner_benchmark_config = "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"`.
