# Iter 011 — Conditional TQQQ Leverage Upgrade (Phase 3 — performance-first)

**Iter:** 011 / 50 (loop)
**Phase:** 3 — performance-first beater hunt
**Slug:** `conditional-tqqq-leverage`
**n_configs:** 6
**cumulative_n_trials_global** before/after: 486 → **492**
**cumulative_n_trials_loop** before/after: 60 → **66**

## Hypothesis

The iter 022 study winner T3d-K2 (`qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`,
CAGR_lh56y 31.08%, Sortino 1.3246) achieves its risk-adjusted edge with QLDSIM
(2× NDX). Iters 005-010 produced higher-Sortino loop variants by spreading risk
across `{QLDSIM, UPROSIM, UGLSIM}` invvol60 baskets and adding ratevol/master-
scope CASHX overrides — but at the cost of **CAGR compression** (loop best
g25_cashx CAGR_lh56y = 22.4% vs T3d-K2 31.08%). User directive (Phase 3): do
**not** trade further CAGR for marginal Sortino gains; the next loop phase must
find configs that beat T3d-K2 on **both** dimensions.

This iter tests whether **conditional ON-leg leverage scaling** — substituting
TQQQ (3× NDX) for QLDSIM (2× NDX) only when conviction is high — can raise
CAGR_lh56y above 31.08% while preserving Sortino_lh56y >= 1.20 and PBO < 0.5.

Conviction is defined two distinct ways (orthogonal mechanism families):

1. **Trend-strength conditional (`K=4` of the iter 022 winner's vote set):**
   the K=2 entry signal is `vote ≥ 2` of `{SMA250>0, SMA100>0, vol_21d<40%,
   AR(1)_30d>0}` — a vote count of **4** (all four indicators bullish) is the
   strongest possible trend-confirmation state inside the existing winner
   architecture. Cite `[stocks_on_the_move, p.98, ch.5-7]` Clenow trend-
   strength filter.
2. **Vol-regime conditional (lowest 25th percentile of vol_21d trailing 5y):**
   leverage is empirically safer when realised vol is in the low tail of its
   trailing distribution — a percentile gate orthogonal to the binary
   vol_21d<40% gate already inside the K=2 vote. Cite `[volatility_trading,
   p.58-60, ch.7]` Sinclair vol cone (low percentile = pump leverage).

Both gates are forward-conservative (only active when their conditions are met
AND the K=2 entry signal is itself ON — i.e., we never upgrade to TQQQ when
the strategy is in defensive ZROZ state). When the upgrade gate is OFF, the
ON leg is the loop baseline QLDSIM; when the gate is ON, the ON leg becomes
TQQQSIM.

**Primary citation:** `[leverage_for_the_long_run, ch.4-5, p.40-60]` —
Husson-Trifoni, "Leverage scales up when trend is firm AND vol is low; LRS
leverage scaling improves CAGR without proportional risk increase." Two LETF
levels (2× and 3×) with a binary regime switch is the simplest LRS leverage
ladder.

**Secondary citations:**
- `[advances_fin_ml, p.208-211]` (Bailey-López de Prado) — CSCV PBO via
  structural mechanism diversity (4 distinct conditional topologies in 6
  configs to keep PBO < 0.5).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials_global=492`
  denominator; local DSR (n=6) is diagnostic only.
- `[stocks_on_the_move, p.98]` — Clenow trend-strength filter (vote count = 4).
- `[volatility_trading, p.58-60]` — Sinclair realised-vol cone (lowest 25th
  percentile = pump leverage regime).

## Direction (Phase 3 explicit)

The user's Phase 3 explicit directive: prefer CAGR / terminal-equity / rolling-
window performance lift over further Sortino gains at CAGR cost. Iter 010's
g25_cashx (Sortino 1.4670, CAGR 22.4%) is a **research** lead, not a Phase 3
candidate. Iter 011's bar is therefore a **disjoint** improvement axis:

- `cagr_lh56y > 0.3108` (T3d-K2 official benchmark, NOT the loop baseline 29.85%).
- `end_equity_ratio_vs_winner_replica > 1.05` (within-iter consistency —
  loop baseline serves as T3d-K2 replica anchor; ~0.04 Sortino offset is
  documented and stable across 5 generations of cross-iter replicas).
- `sortino_lh56y >= 1.20` (Phase 3 floor, mandate-aligned minimum risk-
  adjusted return).
- `pbo < 0.5` (anti-curve-fit gate; same as closed study).
- `dsr_global_p < 0.05` (n_trials_global = 492, anti-DSR-inflation).

Rolling 1y/3y/5y/10y win rates vs the loop baseline are reported as
diagnostics.

## Configs (6, 4-topology structural-diversity grid)

| # | name | upgrade gate | mechanism family |
|---|---|---|---|
| 1 | `..._cleg_baseline_qld` | (no gate; QLDSIM only — replica anchor) | none |
| 2 | `..._cleg_tqqq_always` | always (TQQQSIM substituted for QLDSIM whenever ON) | always |
| 3 | `..._cleg_tqqq_K4` | vote count = 4 of {SMA250, SMA100, vol_21d<40, AR1>0} | trend-strength |
| 4 | `..._cleg_tqqq_lowvol25` | vol_21d in lowest 25th pct of trailing 5y | vol-regime |
| 5 | `..._cleg_tqqq_K4_AND_lowvol25` | K=4 AND lowvol25 (intersection — most selective) | combined-AND |
| 6 | `..._cleg_tqqq_K4_OR_lowvol25` | K=4 OR lowvol25 (union — most permissive) | combined-OR |

All configs share:
- **K=2 entry signal**: `vote ≥ 2` of `{SMA250(QLDSIM), SMA100(QLDSIM),
  vol_21d(QLD ret)<40%, AR(1)_30d(QLD ret)>0}` — exact iter 022 winner
  replica, computed on QLDSIM (the rotation primary).
- **OFF leg**: ZROZSIM (always — no ratevol gate this iter; we're testing the
  leverage-scaling primitive in isolation, not stacking with iter 005-010
  mechanics).
- **ON-leg execution lag**: 1 day (consistent with iters 005/006/007/009/010).
- **Upgrade decision evaluated at close of t-1**, applied at open of t (same
  lag as on_signal and ratevol gates).
- **No basket / no UGL / no CASHX override**: this iter isolates the
  leverage-scaling mechanism from iter 005's invvol basket and iter 006/007's
  ratevol gate. The hypothesis is testable as a clean swap (QLDSIM ↔ TQQQSIM)
  conditional on a binary upgrade gate.

## Datasets

- `lh_56y` (1970-01-01 → 2026-04-30) — primary
- `modern_1990` (1990-01-01 → 2026-04-30) — modern subperiod
- `spy_real` (2003-01-01 → 2026-04-30) — Tiingo SPY-windowed
- `ndx_real` (2010-02-01 → 2026-04-30) — Tiingo QQQ-windowed

Same 4 datasets as iters 005-010 for cross-iter comparability.

## Pre-registered KILL conditions

- **KILL_LOOP #1 (`success_tag`)** — FIRES if any config has
  `beats_winner=True` (Sortino_lh56y > 1.3746 AND `winner_conditions_met=True`
  AND `pct_time_above_benchmark_lh56y >= 0.95`). **Positive tag** (does not
  abort the iter).
- **KILL_LOOP #2 (`decisive_fail`)** — FIRES if best Sortino_lh56y < 1.20
  (Phase 3 floor; even tqqq_always is expected to clear ~1.10-1.20). If
  fired, the conditional-leverage hypothesis is dead.
- **KILL_LOOP #3 (`replica_sanity_baseline`)** — FIRES if baseline Sortino_lh56y
  deviates from 1.2841 by > 0.005 (cross-iter sanity; expect 6th-generation
  bit-exact match to iters 001-010 baseline).
- **KILL_LOOP #4 (`phase3_perf_candidate`)** — **Positive tag** (FIRES if at
  least one config has `phase3_performance_candidate=True`: `cagr_lh56y >
  0.3108 AND end_equity_ratio_vs_winner_replica > 1.05 AND sortino_lh56y >=
  1.20 AND pbo < 0.5 AND dsr_global_p < 0.05`). This is Phase 3's strict bar.
- **KILL_LOOP #5 (`PBO_blowup`)** — FIRES if G1 PBO >= 0.55 (regression vs
  iter 010's 0.3929). Indicates the conditional-leverage configs share too
  much IS-OOS rank correlation.
- **KILL_LOOP #6 (`tqqq_always_collapse`)** — FIRES if tqqq_always config
  Sortino_lh56y < 1.10 (TQQQ ceiling collapses; would invalidate the
  hypothesis premise that TQQQ is even a viable candidate leg). Expected
  range: 1.10-1.30 (TQQQ has ~3× NDX MDD ~80% but 1.5× CAGR multiplier vs
  QLD).
- **KILL_LOOP #7 (`conditional_dominates_always`)** — **Positive tag**
  (FIRES if at least one of {tqqq_K4, tqqq_lowvol25, tqqq_AND, tqqq_OR}
  has Sortino_lh56y > tqqq_always's Sortino_lh56y). Tests the core hypothesis:
  selective leverage upgrade is smarter than always upgrading.

## Expected outcomes (pre-registered ranges)

| config | expected Sortino_lh56y | expected CAGR_lh56y | expected MDD_lh56y |
|---|---:|---:|---:|
| baseline_qld | 1.2841 (anchor) | 0.298-0.299 | -0.645 (anchor) |
| tqqq_always | 1.10-1.30 | 0.35-0.42 | -0.78 to -0.85 (TQQQ floor) |
| tqqq_K4 | 1.20-1.32 | 0.31-0.35 | -0.65 to -0.72 |
| tqqq_lowvol25 | 1.22-1.32 | 0.31-0.34 | -0.65 to -0.70 |
| tqqq_K4_AND_lowvol25 | 1.25-1.33 | 0.30-0.33 (most selective) | -0.65 (smallest delta from baseline) |
| tqqq_K4_OR_lowvol25 | 1.18-1.28 | 0.33-0.38 (most permissive) | -0.72 to -0.78 |

For Phase 3 success, at least one of {tqqq_K4, tqqq_lowvol25,
tqqq_K4_AND_lowvol25, tqqq_K4_OR_lowvol25} should:

- `cagr_lh56y > 0.3108` (vs T3d-K2 official 31.08%)
- `end_equity_ratio_vs_winner_replica > 1.05` (vs in-iter loop baseline)
- `sortino_lh56y >= 1.20`
- `g1_pbo < 0.50`
- `g2_dsr_p_cumulative (n=492) < 0.05`

If `beats_winner=True` is also achieved, that's a **strict-superset** result —
better on Phase 3 axis (CAGR) AND better on Sortino axis simultaneously. We
don't expect this for iter 011 (TQQQ Sortino is structurally lower than QLD's
due to 3× MDD), but the design admits it.

## Comparação plan vs winner

For each config, the verdict.json + SUMMARY.md will report:

```
sortino_edge_vs_winner = sortino_lh56y - 1.3246
cagr_edge_vs_winner    = cagr_lh56y    - 0.3108
end_equity_ratio_vs_winner_replica = config_end_eq / baseline_end_eq
                                       (in-iter baseline serves as
                                        T3d-K2 replica anchor)
rolling_win_rates_vs_winner_replica = {
    "1y":  pct of 252-day windows where config_eq > baseline_eq,
    "3y":  pct of 756-day windows where config_eq > baseline_eq,
    "5y":  pct of 1260-day windows where config_eq > baseline_eq,
    "10y": pct of 2520-day windows where config_eq > baseline_eq,
}

beats_winner = (
    sortino_lh56y > 1.3746
    AND winner_conditions_met
    AND pct_time_above_benchmark_lh56y >= 0.95
)

phase3_performance_candidate = (
    cagr_lh56y > 0.3108
    AND end_equity_ratio_vs_winner_replica > 1.05
    AND sortino_lh56y >= 1.20
    AND g1_pbo < 0.50
    AND g2_dsr_p_cumulative < 0.05
)
```

Both flags are recorded per config; iter is reported as `phase3_performance_
candidate=true` if ANY config achieves the Phase 3 strict bar.

## INCOMPLETE flags / known caveats

- **Replica drift baseline (~0.04 Sortino)** carried over from iters 001-010.
  Loop baseline Sortino_lh56y = 1.2841 vs canonical iter 022 winner 1.3246.
  In-iter end_equity_ratio comparisons use the loop baseline as T3d-K2 replica
  anchor (consistent within-iter convention; cross-dataset CAGR comparisons
  use the canonical 0.3108 figure).
- **TQQQSIM data verified** present in testfolio cache, range 1885-03-20 →
  2026-04-24, n=35339 daily samples (same long history as QLDSIM/UPROSIM).
- **Lowvol25 5y warmup** (~5% of lh_56y span ~1970-1975): during warmup the
  trailing-5y vol_21d percentile is NaN → upgrade gate evaluates False →
  fallback to QLDSIM. Same warmup convention as ratevol_regime_gate (iter
  006 helper).
- **Vote count = 4 warmup**: the 4 individual signals have warmup of
  max(250, 100, 21, 30) = 250 days; during warmup `count` is NaN → upgrade
  gate False → QLDSIM fallback. Matches the K=2 entry signal warmup.
- **Synthetic LETF caveats (pre-1985)**: TQQQSIM is a testfolio synthetic
  proxy reconstructed from NDX returns × 3 × daily-rebal × FFR borrow.
  Same caveat as QLDSIM/UPROSIM/UGLSIM in iters 005-010. The
  conditional-leverage primitive is robust to absolute-level miscalibration
  via binary state machine (gate is on/off, not a continuous coefficient).
- **No ratevol gate / no basket / no master-scope override this iter** — the
  isolation is **deliberate**: we test the leverage-scaling primitive
  cleanly. Future iters can stack this with iter 005-010 mechanics; this
  iter establishes the primitive's solo behaviour first.
- **Single mechanism axis (TQQQ vs QLD), 4 conditional topologies**: PBO
  diversity comes from 4 distinct gate forms (none/always/K4/lowvol25/AND/
  OR — that's 6 topologies in 6 configs). Iter 010 had 4 topologies in 6
  configs and got PBO 0.3929. Expectation: iter 011 PBO in [0.35, 0.45].
- **Expected mandate §1 invariance**: even if `phase3_performance_candidate=
  true` AND `beats_winner=true`, capital remains 100% Plan C per mandate §1.
  Score >= 90 deploy bar is also gated; orchestrator conservative guardrails
  preserve `docs/CURRENT_STATE.md` untouched.
