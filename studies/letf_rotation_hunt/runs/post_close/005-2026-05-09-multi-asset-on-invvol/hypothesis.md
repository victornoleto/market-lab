# 005-2026-05-09-multi-asset-on-invvol — HYPOTHESIS

**Iter:** 005 / 50 (loop)
**Slug:** multi-asset-on-invvol
**Date (UTC):** 2026-05-09
**n_configs:** 6 (≤ 8 protocol cap)
**cumulative_n_trials_global before:** 450
**cumulative_n_trials_global after:** 456

## Hypothesis

The winner's ON leg holds a **single asset (QLD)** during ON state. Iters 001
(yield-curve OFF), 002 (vol-DD killswitch), 003 (calendar gate), and 004
(stock-bond corr regime) all left the ON-leg structure untouched and tried
to add value via OFF-side or master-gate overrides — **all four failed to
add Sortino**. Iter 004's diagnosis was specific: the cross-asset *second
moment* (correlation) is mostly redundant with the trend signal already in
the winner's stack. The natural complement is to test cross-asset *first
moment* — diversifying the ON leg itself across distinct return sources
sized by inverse realised vol so each asset contributes equal volatility.

This is mechanically distinct from every closed-study tier:
- **T1** held a single LETF (QLD) on ON — single-asset.
- **T2 (HFEA)** stacked equity + bond at fixed 55/45 weights with no
  trend gate — fixed weights, always invested.
- **T3** added composite signal complexity to a single-asset rotation —
  single-asset.
- **T4 (Clenow / EWMAC)** ranked assets and held only the **top-K winners**
  from {UPRO, QLD, UGL, TMF} — winners-take-all selection, NOT a
  diversified basket.
- **T5 (Carver vol-target)** sized continuously by forecast magnitude
  × vol-target, but with a different driver (forecast strength, not
  inverse-vol weighting under a binary gate).
- **iter 023 (T3d multi-asset grid)** tested 3 ON assets {UPRO, QLD,
  TQQQ} × 4 OFF assets, but with **one ON asset per config** — never
  held multiple ON assets simultaneously.

Iter 005 holds **multiple ON assets simultaneously** sized by inverse
realised volatility under the winner's binary trend gate. When ON, capital
is allocated $w_i = (1/\sigma_i) / \sum_j (1/\sigma_j)$ across the basket
so that each asset contributes equal ex-ante volatility. When OFF,
canonical ZROZ leg (winner's OFF asset). The **trend gate is the winner's
vote-K=2 of {SMA250, SMA100, vol_21d<40%, AR(1)_30d>0} computed on QLD**
— same gate, same regime detection, only the ON-leg vehicle changes.

Why first-moment cross-asset matters here:
- Each LETF has a non-zero idiosyncratic component (NDX ≠ SPY ≠ Gold).
- Inverse-vol weighting equalises volatility contribution, so the
  highest-vol leg (UGL ≈ 30%, UPRO ≈ 30-40% during stress) does not
  dominate.
- During regimes where the trend gate is ON but one asset
  underperforms (e.g. NDX-tech bear in 2000-02 or Q1-2022), the basket
  partially absorbs the shock via the other legs.

| Iter | Mechanic | ON-leg structure |
|---|---|---|
| 001 | yield-curve OFF rotation | single QLD |
| 002 | vol-DD killswitch | single QLD |
| 003 | calendar / Halloween | single QLD |
| 004 | ρ(QLD,ZROZ) regime | single QLD |
| **005** | **inverse-vol ON basket** | **multi-asset {QLD, UPRO, UGL}** |

This iter is also the natural next step recommended in the "Next iter
ideas" section of iters 002, 003, AND 004 (multi-recommended → highest
remaining EV per LOOP_PROTOCOL §"Soft-halt hint").

## Citations

**Primary:** `[stocks_on_the_move, p.98]` — Clenow on volatility-parity
position sizing for systematic equity rotation: $w_i \propto 1/\sigma_i$,
"so each position contributes the same amount of volatility." Cited
multiple times in closed-study T4 (signals.py docstring) but never
applied with the winner's binary trend gate.

**Secondary:**
- `[systematic_trading, ch.10]` — Carver position sizing via inverse
  realised vol (instrument volatility scalar `IVS = vol_target / σ_i`),
  the canonical robust sizing rule for multi-asset systematic systems.
- `[risk_parity, ch.5, p.10]` (archived) — Carlson cap-efficient stacking;
  rationale for combining a leveraged equity LETF with a leveraged bond
  LETF with proper sizing extends naturally to combining multiple
  leveraged equity LETFs at the ON-leg.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (G2;
  global denominator = 450 + 6 = 456 after this iter).
- `[leverage_for_the_long_run, p.21 Table 12]` — LETF tracking drag /
  decay characteristics (UGL specifically) — relevant because UGL synth
  was calibrated in iter 000-v2 to real UGL post-2008 tracking.

## Configs

All configs share the trend ON signal `vote-of-2 of {SMA250, SMA100,
vol_21d<40%, AR(1)_30d>0}` computed on **QLDSIM** (winner replica gate).
The OFF asset is **ZROZSIM** for all configs. Only the ON-leg vehicle
differs. Volatility is realised vol of daily returns over the specified
window, computed at close of t-1 and applied to weights at open of t
(1-day lag — same convention as winner's other gates).

| # | Name | ON-leg basket | Vol window | Sizing rule |
|---|---|---|---:|---|
| 1 | `qld_voteK2_..._on_baseline` | {QLD} | — | single-asset (replica) |
| 2 | `qld_voteK2_..._on_basket2_qld_upro_invvol60` | {QLD, UPRO} | 60d | inverse-vol |
| 3 | `qld_voteK2_..._on_basket2_qld_ugl_invvol60` | {QLD, UGL} | 60d | inverse-vol |
| 4 | `qld_voteK2_..._on_basket3_qld_upro_ugl_invvol60` | {QLD, UPRO, UGL} | 60d | inverse-vol |
| 5 | `qld_voteK2_..._on_basket3_qld_upro_ugl_invvol120` | {QLD, UPRO, UGL} | 120d | inverse-vol |
| 6 | `qld_voteK2_..._on_basket3_qld_upro_ugl_eqweight` | {QLD, UPRO, UGL} | — | equal-weight |

Orthogonal grid (single-axis variation per pair):

- **Composition axis** (configs 2 vs 3): same-asset-class equity blend
  ({QLD, UPRO}: NDX 2x + SPY 3x) vs cross-asset blend ({QLD, UGL}:
  NDX 2x + Gold 2x). Tests whether the diversifier should be another
  equity LETF (intra-asset-class) or a true distinct asset class
  (cross-asset).
- **Expansion axis** (config 4 vs configs 2 and 3): adding the third
  asset to combine both diversification dimensions.
- **Window axis** (config 4 vs config 5): 60d vs 120d realised vol at
  fixed 3-asset basket. Faster window adapts quickly to vol regime
  shifts; slower window is more stable, fewer turnover-induced costs.
- **Sizing axis** (config 4 vs config 6): inverse-vol vs equal-weight
  at fixed 3-asset basket. Isolates whether the inverse-vol mechanism
  matters or whether the diversification effect alone (basket vs
  single-asset) drives the result.

The trend gate is computed on QLD only (not per-asset), keeping the
regime detection consistent with the winner — so the ON/OFF state is
identical across all 6 configs at every timestamp. This isolates the
ON-leg-vehicle effect cleanly from any signal-tuning effect.

Universe restriction: SOXLSIM and TMFSIM are **not** in the testfolio
cache; iter does not synthesize new symbols. The available LETF
universe (QLDSIM, UPROSIM, TQQQSIM, SSOSIM, UGLSIM) covers
NDX 2x/3x + SPY 2x/3x + Gold 2x — sufficient for an equity+gold basket
test. We pick QLD/UPRO/UGL to maximise distinct-index coverage with
the smallest config count (TQQQSIM and SSOSIM would be redundant
intra-index leverage variants).

## Datasets

Mirrors closed-study set for direct comparability:
- `lh_56y`: 1970-01-01 → 2026-04-30 (SPYSIM/QLDSIM/UPROSIM/UGLSIM/ZROZSIM/CASHX)
- `modern_1990`: 1990-01-01 → 2026-04-30
- `spy_real`: 2003-01-01 → 2026-04-30
- `ndx_real`: 2010-02-01 → 2026-04-30

The lh_56y window provides 4-5 distinct stock-gold-bond regime cycles
(1973-1980 inflation/gold, 1981-2000 disinflation, 2001-2010
financial-crisis era, 2011-2022 low-rate / 2022 inflation rebound).

## Pre-registered KILL_LOOP conditions

- **KILL_LOOP #1 (success-tag):** if any config has Sortino_lh56y > 1.3746
  AND `winner_conditions_met=True` AND pct_time_above_benchmark_lh56y ≥ 0.95
  → record `beats_winner=true` (loop continues per protocol §"Beats-winner
  test"). Probability assessed below.
- **KILL_LOOP #2 (decisive-fail):** if all 5 multi-asset configs return
  Sortino_lh56y < 1.10 → multi-asset ON basket adds no value; pivot next
  iter to a fundamentally different family (VIX-percentile / VRP overlay,
  bond duration timing, equity-factor tilts).
- **KILL_LOOP #3 (replica-sanity):** if config #1 (single-asset baseline)
  Sortino_lh56y differs from 1.2841 (iters 001/002/003/004 baseline) by > 0.05
  absolute → engine drift; flag INCOMPLETE and trust comparative deltas
  across configs only.
- **KILL_LOOP #4 (single-asset-domination):** if Sortino_lh56y of basket
  configs (2-6) is *uniformly below* baseline (1.2841) → confirms iter 023's
  finding that "QLD × Vote-K=2 is asset-specific edge that doesn't
  generalise"; multi-asset diversification sacrifices QLD's idiosyncratic
  ON-edge for risk reduction that the trend gate already provides.
- **KILL_LOOP #5 (turnover-blowup):** if any basket config has
  turnover_per_year > 3× baseline → the inverse-vol re-weighting itself
  is a curve-fit cost source (frequent rebalancing). Tag config
  "TURNOVER_HOT" — informational only.

## Expected outcomes (pre-registration; honest band)

- **Sortino_lh56y range expected:** 1.05–1.40 across all 6 configs. The
  wide band reflects competing forces: diversification *should* help on
  paper, but iter 023 already showed UPRO × Vote-K=2 single-asset Sharpe
  drops to 0.55-0.64 because the gate is NDX-tuned. In a basket the
  underperforming legs drag down the basket return, but inverse-vol
  weighting partially mutes this by under-weighting them when they
  are highly volatile (which they tend to be when the gate is mistimed).
- **Best plausible scenario:** config 4 (`basket3_qld_upro_ugl_invvol60`)
  achieves Sortino ~1.32-1.36 (just above baseline) by harvesting Gold's
  uncorrelated returns during 1973-1980 (when SPY+NDX were flat-to-down
  and gold rallied 700%). lh_56y improvement comes from this regime, not
  from 2000+. Edge over baseline likely +0.03 to +0.07; clears anti-curve-fit
  margin marginally if at all.
- **Plausible failure mode (most likely):** the basket Sortino is bounded
  *above* by the best single-asset (QLD) and *below* by the worst
  (UPRO/UGL when their trend regimes mistime). Given QLD-Vote-K=2 was
  empirically tuned for NDX, the basket's drag from non-NDX assets
  outweighs the diversification benefit. All basket configs cluster
  in [1.18, 1.28] band, below baseline by 0.00 to -0.10 Sortino.
- **WC compliance risk:** UGL has 1973-1980 outsize gains but also 1980-2000
  flat-to-negative returns. Holding UGL during a 20-year flat regime via
  inverse-vol weighting could push pct_time_above_benchmark below 0.95
  (the strict bar). UPRO ON-state during 2000-02 dotcom bear could also
  hurt pct_above. Configs 4-5-6 most exposed.
- **Equal-weight vs inverse-vol:** equal-weight (config 6) likely
  *underperforms* inverse-vol (config 4) because UPRO's higher leverage
  (3x SPY) makes it more volatile than QLD (2x NDX); equal-weight gives
  too much vol-budget to UPRO. This isolates the inverse-vol mechanism.
- **120d vs 60d window:** difference likely small (±0.02 Sortino). 60d
  reacts faster to regime vol shifts; 120d more stable. The trend signal
  itself does the heavy lifting on regime detection; vol-window choice
  is a sizing-rule refinement.
- **Beats-winner probability:** **~5-15%**. The hypothesis is plausible
  (multi-asset is a well-established diversification idea) but the
  conjunction (Sortino > 1.3746 AND WC met AND pct_above ≥ 0.95) is
  hard, AND the QLD-NDX-tuned gate gives single-asset QLD a structural
  advantage that the basket can't fully overcome. Most likely outcome
  is small Sortino edge (positive or negative) with WC borderline.

## INCOMPLETE flags / caveats

- **Trend gate computed on QLD only (not per-asset):** by design, to
  isolate the ON-leg vehicle effect. A separate iter could test
  per-asset trend gates with vote-K-style aggregation, but that would
  conflate trend-signal-tuning with multi-asset basket effect. Out of
  scope this iter.
- **Inverse-vol weights computed daily but rebalanced at signal-state
  changes:** continuous daily rebalancing would inflate turnover via
  vol-noise; we rebalance only on (a) ON→OFF transitions, (b) OFF→ON
  transitions, and (c) at month-end if still ON (Clenow standard
  monthly rebalancing). This balances cost vs reactivity.
- **UGL synth caveat (per iter 000-v2):** UGLSIM was calibrated in iter
  000-v2 with `LETF_EXPENSE_RATIOS["UGL"] = 0.030` after bisection on
  real UGL 2008-2026 tracking. Pre-2008 UGL synth inherits this
  calibration. Comparative deltas across configs in lh_56y window
  remain valid because all UGL-using configs see the same synth.
- **No tax/fees modeled this iter** (matching closed-study convention
  for hunt comparability). Multi-asset rebalancing in real deployment
  would have transaction costs ≥ baseline; gross results are upper
  bound for any deploy decision.
- **Volatility window choices are interpretable:** 60d ≈ Carver's
  default `[systematic_trading, ch.10]`; 120d ≈ half-year smoother. We
  do NOT sweep additional windows because a 4-step window grid (30/60/90/120)
  would inflate trial count (G1 PBO penalty per `[advances_fin_ml,
  p.208-211]`). Two-window comparison is sufficient to establish
  "faster vs slower" robustness.
- **Equal-weight comparator (config 6) does not use vol information at
  all** — it is the cleanest control for "is the diversification
  benefit dependent on vol-parity sizing?". A naïve cap-weighted
  alternative is omitted because we have no liquidity or AUM data
  in the synth universe.
- **2022 rates target unlikely to be rescued** — the rates loss in 2022
  was *trend-signal-driven* (vote-K=2 stayed ON during the early 2022
  drawdown). A multi-asset ON basket changes only the *vehicle* held
  during ON state; if all 3 basket assets fell in early 2022 (which
  they did — NDX, SPY, and Gold all had drawdowns in Q2-2022), the
  basket cannot help.
- **Synth caveat (pre-1985):** UPROSIM, UGLSIM, QLDSIM, ZROZSIM all
  derived from formula-based syntheses with calibrated expense ratios.
  Cross-asset correlations pre-1985 are mechanically tied to synth
  assumptions, but the inverse-vol weighting depends on each asset's
  own σ (not cross-asset correlation), so the basket compositions are
  computed deterministically across the lh_56y window.

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
