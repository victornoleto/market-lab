# Iteration 024 — Bond-curve carry-driven duration timing on the bond leg of a 0.9/0.6 SPY+bond stack

## Hypothesis

A static-leverage 0.9 SPY + 0.6 bond stack (iter 015's NTSX-style
structure, no vol-target overlay) where the **bond leg dynamically
allocates between long-duration TLT and near-cash SHV based on the
realized term-structure carry signal** (T10Y3M, 21-day SMA) captures
two sources of premium that static iter 015 misses:

1. **Bond term premium / roll-down carry** when the curve is steep
   (T10Y3M > 0): TLT earns yield + roll-down passive return.
2. **Duration-loss avoidance** when the curve is inverted (T10Y3M < 0):
   SHV switches to ~0-duration cash equivalent, sidestepping the
   2022-style TLT drawdown (TLT lost ~50% peak-to-trough in 2022, while
   SHV lost ~0%).

The mechanism is **CARRY-as-allocation-signal**, NOT
carry-as-leverage-haircut. The bond leg's notional stays at 0.6×; only
its duration profile rotates. Total portfolio leverage is fixed at
1.5× (0.9 + 0.6) — no Moreira-Muir vol-target, no σ²_port feedback.

This is the explicit Option C "Cross-asset CARRY as primary" direction
listed in `BASE_MEMORY.md` post-iter-023.

## Primary citation

`[ilmanen_expected_returns, ch.6-7]` — term premium and bond-curve
roll-down carry as a primary expected-return premium, distinct from
TSM (chapter on time-series momentum) and from variance-driven risk
premia.

## Additional citations

- `[risk_parity, ch.1, p.10-11]` — naïve fixed-weight risk parity
  (basis for the 0.9/0.6 NTSX-style ratio shared with iter 015/016).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (G2 gate criterion).
- `[stocks_on_the_move, p.229]` — 2 bps round-trip transaction cost
  (held constant from iter 023's cost model).
- `[systematic_trading, p.118-119, ch.7]` — slow-signal exit thresholds
  (background framework for the 21-day smoothing window choice).
- Web: Koijen, Moskowitz, Pedersen & Vrugt (2018). "Carry." *JFE*
  127(2), 197-225. — Demonstrates carry as a return-predictor across
  asset classes; Sharpe ~0.6 on a global cross-asset basket.
- Web: Cochrane & Piazzesi (2005). "Bond Risk Premia." *AER* 95(1),
  138-160. — Term-structure factor predicts bond excess returns over
  cash; the source of the carry premium being harvested.
- Web: Estrella & Mishkin (1998). "Predicting U.S. Recessions:
  Financial Variables as Leading Indicators." *Restat* 80(1), 45-61. —
  Establishes T10Y3M as canonical recession indicator (the SHV-mode
  trigger).

## Edge source

SPY 1x buy-hold captures equity drift only. A static 0.9/0.6 SPY+IEF
(iter 015) adds intermediate-duration bond carry but is locked into
~7y duration regardless of curve shape — getting punished in 2013
(taper tantrum), 2018 (rate hikes), and especially 2022 (-13% IEF
loss). **Bond carry duration timing** captures the upside of long
duration when the curve pays for it (TLT in steep regimes), and
preserves capital when the curve inverts (SHV in flat/inverted
regimes), without disturbing the equity leg or introducing variance
feedback.

## Datasets

- educational: SPY+TLT+SHV 2007-01-11 → 2026-04-15 (SHV-inception
  aligned, ~19y; benchmark is frozen SPYSIM 40y Sharpe 0.68 / CAGR
  11.47% / MDD 55.14%, same convention as iter 016).
- spy_real: SPY+TLT+SHV 2009-06-25 → 2026-04-15 (~17y post-GFC).
- ndx_real: QQQ+TLT+SHV 2010-02-12 → 2026-04-15 (~16y tech-heavy).

T10Y3M signal: `data/external/macro/t10y3m_daily.parquet` (FRED, daily,
1982-01-04 → 2026-04-23). 21-day SMA smoothing applied with 1-bar lag
to prevent look-ahead. SHV will be substituted for any window before
its 2007-01-11 inception (none of the 3 datasets reach back further,
so this is moot — but documented for the spec).

## Pre-committed cfg

```python
CFG = {
    "cfg_id": "bcdt_w90_60_t10y3m_sma21_ramp100bps_v1",
    "eq_weight": 0.9,                    # equity leg static notional
    "bd_weight": 0.6,                    # bond leg static notional (= TLT_alloc + SHV_alloc)
    "carry_signal": "T10Y3M",            # FRED 10Y - 3M Treasury spread
    "signal_smoothing_days": 21,         # SMA window
    "signal_lag_bars": 1,                # use prior day's smoothed signal
    "ramp_min_bps": 0.0,                 # T10Y3M = 0 → 0% TLT
    "ramp_max_bps": 100.0,               # T10Y3M ≥ 100 bps → 100% TLT
    "rebalance": "monthly",              # 21-bar rebalance to suppress noise
    "cost_bps_per_leg": 0.0002,          # 2 bps per unit Δposition (matches iter 023)
}
```

Allocation rule (executed on each rebalance day, held constant
between rebalances):
```
sig = T10Y3M_smoothed_21d.shift(1).clip(0, 100bps) / 100bps
alloc_TLT = sig
alloc_SHV = 1 - sig

position_SPY  = 0.9
position_TLT  = 0.6 * alloc_TLT
position_SHV  = 0.6 * alloc_SHV
```

Total deployed leverage = 0.9 + 0.6 = 1.5× (matches iter 015 exactly,
within 1pp of iter 016 at static-scale).

## Kill criteria (pre-committed — fail any → hypothesis falsified)

**Kill #A — Sharpe regress vs iter 015 base (static SPY+IEF)**:
If Sharpe Δ vs iter 015's per-dataset Sharpe (0.78 / 1.04 / 1.06) is
**< −0.03** on **≥ 2/3 datasets** (i.e., dynamic timing destroys
static blend's edge). Iter 015 Sharpe is the relevant comparator
because it shares the same 0.9/0.6 leverage structure; a regression
here means the duration timing layer is harmful.

**Kill #B — Signal too cautious (SHV-mode over-fires)**:
If `alloc_SHV` exceeds 60% of bars on **≥ 2/3 datasets**, the
strategy collapses to a ~60% SPY + ~24% cash + ~16% TLT blend, which
is just de-leveraged equity. Indicates the T10Y3M ramp is too
restrictive.

**Kill #C — MDD blow-up vs benchmark**:
If MDD exceeds benchmark + 5pp (educational > 60.14%; spy_real >
38.70%; ndx_real > 40.12%) on **≥ 2/3 datasets**, the dynamic timing
failed to provide protection AND the static blend was better.

**Kill #D — Turnover dominates premium**:
If turnover (sum of |Δposition| per year, summed across the bond
legs only since SPY is static) > 8 / year × cost = 1.6%/year drag,
the cost has eaten the carry premium. (Compare iter 023 which had
~35/yr/leg × 3 legs × 2bps = 2.1%/year drag and failed.)

If any of A/B/C/D triggers on the dominant condition, the
hypothesis is falsified, score the strategy honestly, document
finding in DEAD_ENDS.md if structurally novel.

## Expected budget

- Configs to test: **1** (single pre-committed cfg, no grid). Adds
  +1 to cumulative_n_trials → 4276 → 4277.
- Wall-time: ~10-15 minutes (pandas + numpy on existing parquets +
  validation suite at single-cfg granularity).
- Files to create:
  - `bond_carry_duration_timing.py` — pandas implementation.
  - `numpy_reference_bcdt.py` — numpy-pure reference for G7 cross-lib
    parity (±3pp CAGR).
  - `run_backtests.py` — driver across 3 datasets.
  - `compute_gates_and_score.py` — G1-G7 + scoring.
  - `results.json` — per-dataset metrics + returns_series.
  - `verdict.json` — score_strategy() output.
  - `final_report.md` — Stage 5 writeup.
  - `plot_vs_benchmark_spy_real.png` + `plot_vs_benchmark_ndx_real.png`.
- Tests:
  - `tests/test_iter_024_bond_carry_duration_timing.py` — TDD spec
    (signal computation, allocation rule, cross-lib parity).

## Implementation plan

1. Write TDD spec asserting:
   (a) signal computation matches expected ramp output for
   hand-traced T10Y3M values;
   (b) allocation always sums to bd_weight (0.6 ± 1e-12);
   (c) numpy reference matches pandas within 0.5 pp annualised
   return on a 5-year synthetic test.
2. Implement `bond_carry_duration_timing.py` (pandas, vectorised).
3. Implement `numpy_reference_bcdt.py` (loop-based, no pandas).
4. Run backtests on 3 datasets → save `results.json` with
   returns_series schema (per Stage 5 plot helper requirements).
5. Compute G1-G7 gates per dataset.
   - G1 PBO: single-cfg ⇒ trivially passes (PBO undefined for n=1;
     log as N/A → True for scoring purposes per single-cfg
     convention used in iter 015/016/018).
   - G2 DSR: single-cfg, n_trials=4277 cumulative → DSR via
     `validation/dsr.py`.
   - G3 WF 6/8 with MDD<25%: rolling 70/30 walk-forward.
   - G4 OOS 70/30 Sharpe > 0.
   - G5 FWD post-2020 stress Sharpe > 0.
   - G6 Bootstrap 99.9% CI low > 0 via
     `validation/permutation.py` or simple block bootstrap.
   - G7 Cross-lib ±3pp CAGR: pandas vs numpy reference.
6. Score via `scoring.score_strategy()` → tier + verdict.json.
7. Generate plots via `plot_helper.py --iter 024`.
8. Write `final_report.md` with honest assessment vs all 4 kill
   criteria + DEAD_ENDS update if structural novelty learned.

## Structural novelty check vs DEAD_ENDS

| dead-end pattern | this iteration | structurally distinct? |
|---|---|---|
| iter 009 — T10Y3M binary haircut on vol-managed blend | T10Y3M as duration ALLOCATION on STATIC (no-vol-target) blend; signal switches WHICH bond, not HOW MUCH portfolio | **YES** — different transformation (allocation vs scaler), different base (static vs vol-managed) |
| iter 012 — T10Y3M asymmetric haircut (equity-leg-only) | Same as above; equity leg untouched | **YES** — equity leg stays at 0.9 always, only bond allocation rotates |
| iter 013 — meta-labeling with yield-curve features on vol-managed blend | No ML model, no vol-managed base | **YES** — deterministic linear ramp, no classifier |
| iter 023 — TSM on small basket per-asset vol-target | No momentum signal, no per-asset vol-target | **YES** — carry (T10Y3M) is yield-based not price-based; turnover ~6/yr vs 35/yr |
| iter 015/016 — static fixed-weight blend | Same NTSX-style 0.9/0.6 ratio as iter 015 BUT bond leg now dynamic | **YES** — adds duration timing layer that iter 015 lacks |

The mechanism is genuinely orthogonal to the closed family of
T10Y3M-as-haircut overlays: it uses the same SIGNAL but applies a
**fundamentally different transformation** (intra-leg rotation, not
inter-leg or whole-portfolio scaling). Iter 009's "Don't re-test"
list explicitly bounds the closure to "binary-haircut overlay
variants on a vol-managed blend" — this is neither.

## Risk acknowledgement

- The static 1.5× leverage is fragile to simultaneous SPY+TLT
  drawdowns (e.g., 2022 H1 when SPY −20% AND TLT −25% ≈ correlation
  +0.4). The dynamic SHV switch should mitigate but doesn't fully
  protect (SHV mode requires T10Y3M < 0, which lagged the actual
  TLT bottom by ~2 months in 2022).
- DSR with cumulative n_trials = 4277 is the standing hunt-loop
  ceiling; even iter 016's STRONG candidate (Sharpe 0.98/1.14/1.19)
  worst-p was 0.226. To clear DSR p < 0.05 requires Sharpe edge
  closer to +0.30 / +0.30 / +0.30 (hard).
- Forward-stress G5 post-2020: 2022's TLT crash is the most
  recent stress event AND is exactly what this strategy is supposed
  to handle. If G5 fails, the thesis is wrong.

## Conclusion field (for Stage 4 update)

[Reserved — completed at end of Stage 4 with measured metrics.]
