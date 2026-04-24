# Iteration 014 — EBP (Excess Bond Premium) credit-cycle binary haircut overlay on iter 008 blend, with mandatory pre-validation

## Hypothesis

Apply a single pre-committed **EBP** (Gilchrist-Zakrajšek 2012) macro
overlay on top of iter 008's vol-managed SPY+TLT blend (`vt15_L21_cap20`).
The overlay is a binary haircut on the **equity leg only** when EBP's
rolling z-score crosses a stress threshold, intended to reduce equity
exposure during credit-cycle tightening episodes (LTCM 1998, GFC 2008,
COVID 2020, late-2022 rate-hike stress).

Core structural claim: **EBP — the residual of corporate bond spreads
after stripping expected defaults — captures investor risk-appetite
swings that are partially orthogonal to both (a) yield-curve slope
signals (iter 009/012 closed T10Y3M family) and (b) realized-volatility
proxies (iter 013 closed ρ/VIX-z family)**. Iter 013 showed that
vol-proxy signals cointegrate with σ²_port at business-cycle scale,
producing 100% bottom-20% scale overlap and zero Sharpe lift. EBP's
fire-episodes are driven by credit-risk-premium dynamics (bank balance
sheets, insurance-company demand, dealer inventories) that can fire
ahead of or independently of broad equity vol spikes — which is
exactly what Gilchrist-Zakrajšek documented empirically.

To avoid repeating iter 009/012/013's redundancy failure, this
iteration enforces a **mandatory pre-validation gate before spending
DSR budget**: measure |ρ(EBP_daily_z, σ²_port(iter 008 blend))| over a
60-day rolling window on each of the 3 datasets. **If fraction of bars
with |ρ| > 0.30 exceeds 20% on any dataset → abort iteration, document
pre-validation failure as new dead-end, do NOT run full test.**

## Primary citation

`[adaptive_markets, p.131-132, ch.11]` — Lo's discussion of
**countercyclical capital buffers** and credit-cycle dynamics as a
distinct axis of systemic risk management, separate from rates and
equity-vol regimes. Lo frames credit-cycle stress as its own adaptive
landscape with own fire-episodes (LTCM 1998 hedge-fund attrition
[ch.7 p.244-246]; crowded-trade contagion [ch.8 p.287-288]) that
motivate signals observing that landscape directly rather than via
correlated equity-vol proxies.

## Additional citations

- `[risk_parity, p.23-24, ch.2]` — HY credit's Sharpe-equivalence with
  equity over 1984-2011 (~0.30 Sharpe each) is precisely why the
  pre-validation gate is mandatory: raw HY spreads would co-move with
  σ²_port(SPY+TLT). EBP is the residual AFTER removing that
  expected-default component — the **decomposition** is what may give
  orthogonality, not the raw spread.
- `[ml_for_algo_trading, ch.23, p.716]` — "never let the data speak";
  prioritize economically-motivated hypotheses. EBP is not a fitted
  feature — it is Gilchrist-Zakrajšek's canonical credit-risk-premium
  decomposition with pre-specified economic meaning.
- `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` lag rule extended here to
  macro monthly series: EBP value known at month-end `m` is lagged by
  1 bar before applying at daily bar `t` within month `m+1`.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (post-iter 013 = 4255; this iter adds at most 3 → 4258).
- `[systematic_trading, p.144, ch.9]` — tier-2 half-exposure de-lever
  (`haircut = 0.5` re-used from iter 009/012 family for consistency).
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).

- Web (primary paper): **Gilchrist, S. & Zakrajšek, E. (2012)**,
  "Credit Spreads and Business Cycle Fluctuations", *American Economic
  Review* 102(4), 1692-1720.
  DOI: [10.1257/aer.102.4.1692](https://doi.org/10.1257/aer.102.4.1692).
  The paper decomposes corporate bond spreads into (a) expected-default
  component and (b) the **excess bond premium (EBP)** residual — the
  latter is the signal tested here. GZ2012 show EBP forecasts both
  IP and unemployment 1-12 months ahead with statistical significance
  that rates-term-structure signals lack over the same horizons.

- Web (data): **Federal Reserve Board** publishes monthly EBP series at
  <https://www.federalreserve.gov/econresdata/notes/feds-notes/2016/updating-the-recession-risk-and-the-excess-bond-premium-20161006.html>.
  The project's `data/external/macro/ebp_monthly.parquet` covers
  1973-01 → 2026-03, columns `gz_spread`, `ebp`, `est_prob`. This
  iteration uses the `ebp` column (the GZ2012 residual).

## Edge source

SPY b&h does not capture investor risk-appetite regime shifts that
originate in corporate-bond / dealer-intermediation stress BEFORE they
transmit into equity realized volatility. When credit markets tighten
(EBP rises), bond-financed corporate activity slows 3-12 months before
equity markets reprice; a stress-triggered equity de-lever during the
EBP rise captures this anticipation that variance-scaling (reactive)
and T10Y3M (monetary-policy channel) both miss.

## Datasets

- **educational** (SPY+TLT, 2002-07-26 → 2026-04-15, 24y): longest
  TLT-available window; includes 2002 post-dot-com deleveraging,
  2008 GFC (the canonical EBP fire-episode), 2011 Euro crisis, 2020
  COVID, 2022-2023 stress. Tests whether EBP adds value across
  multiple regime types.
- **spy_real** (SPY+TLT, 2009-06-25 → 2026-04-15, 17y): post-GFC,
  benchmark SPY b&h Sharpe 0.90. Includes 2020 COVID and 2022 rate-hike
  stress — the canonical post-GFC EBP fires.
- **ndx_real** (QQQ+TLT, 2010-02-12 → 2026-04-15, 16y): tech-heavy;
  tests whether credit-cycle signal generalises to non-SPY equity
  composition. Note: QQQ-TLT correlation regime differs slightly from
  SPY-TLT.

## Kill criteria (pre-committed)

- **Kill #PV (pre-validation, ABORT BEFORE FULL RUN)**: if fraction of
  bars with |ρ(EBP_z, σ²_port)| > 0.30 exceeds 20% on ANY of the 3
  datasets → abort iteration at pre-val stage, write final_report with
  pre-val failure, add `(EBP-on-iter-008-blend, pre-val-failed)` to
  DEAD_ENDS. This is the primary defense against re-opening the 009/012
  /013 cointegration-failure mode.
- **Kill #1 (regression)**: Sharpe regresses > 0.02 on BOTH real-data
  slots (spy_real AND ndx_real) vs iter 008 baseline (spy 1.000,
  ndx 1.021) → triggered.
- **Kill #2 (CAGR floor)**: CAGR < 0.75 × benchmark on ≥ 2 datasets →
  triggered.
- **Kill #3 (score)**: final score < 65 → MARGINAL or worse → triggered.
- **Kill #4 (gate-fire degenerate)**: gate fires < 1% OR > 40% of bars
  on any dataset → signal miscalibrated (either too rare to matter or
  over-firing) → triggered.
- **Kill #5 (cross-lib)**: numpy-reference CAGR differs > 3pp from
  engine CAGR on any dataset → G7 FAIL → triggered.
- **Kill #6 (bottom-20 overlap)**: gate-fire bars overlap ≥ 80% with
  bottom-20% blend-scale bars on ≥ 2 datasets → post-hoc confirms
  cointegration the pre-val was supposed to catch → triggered.

## Expected budget

- Pre-validation step: ~1 min (3 datasets × 60-day rolling correlation).
- **If pre-val passes**: Configs to test = 1 ex-ante cfg × 3 datasets
  = **3 new trials** (cumulative_n_trials 4255 → 4258). Wall-time:
  ~15 min for backtests + gates + scoring.
- **If pre-val fails**: iteration aborts at pre-val stage.
  Wall-time: ~5 min total including final_report.
- Files to create:
  - `ebp_credit_overlay.py` — overlay module (EBP monthly → daily align,
    z-score, binary gate, equity-only haircut)
  - `overlay_numpy_reference.py` — hand-rolled numpy parity check
  - `pre_validation.py` — cointegration screen before committing full run
  - `run_backtests.py` — harness
  - `compute_gates_and_score.py` — 7-gate battery
  - `test_ebp_credit_overlay.py` (in `tests/`) — TDD for EBP alignment,
    z-score, gate, no-lookahead, numpy parity
  - `hypothesis.md` (this file), `results.json`, `verdict.json`,
    `final_report.md`

## Implementation plan

1. **TDD first** (`tests/test_ebp_credit_overlay.py`):
   - `test_ebp_monthly_to_daily_forward_fills_within_month`
   - `test_ebp_lag_shifts_month_boundary_correctly`
   - `test_ebp_zscore_uses_252_bar_trailing_window`
   - `test_ebp_gate_fires_when_z_exceeds_threshold`
   - `test_asymmetric_haircut_preserves_bond_leg`
   - `test_numpy_reference_matches_pandas_cagr`

2. **Implement `ebp_credit_overlay.py`**:
   - `load_ebp_daily(path, align_index)`: load monthly parquet, resample
     to daily forward-fill within month (EBP value set at month-start
     holds through the month until next month's value is known), then
     `.shift(1)` for no-lookahead. Annotation: the effective lag is
     "last month's published EBP drives today's haircut decision" —
     conservative because GZ2012's EBP is estimated AFTER month-end.
   - `compute_ebp_zscore(ebp_daily, window=252)`: rolling 252-bar
     z-score; mean/std computed on the LAGGED series so no future info
     leaks.
   - `compute_gate_series(ebp_z, threshold=1.0, haircut=0.5)`: binary
     gate — `z ≥ 1.0` → haircut 0.5; else 1.0. NaN → 1.0.
   - `apply_blend_with_credit_overlay(r_spy, r_tlt, ebp_z_lagged,
     target_vol, lookback, max_leverage, threshold, haircut, ...)`:
     reuses iter 006's `stock_bond_blend.apply_blend_variance_target`
     for un-gated positions; applies gate to SPY leg only (asymmetric
     pattern from iter 012); recomputes costs on gated positions.

3. **Pre-validation step** (`pre_validation.py`):
   - For each dataset, load iter 008 blend's `σ²_port` from the saved
     position/scale series (or re-run the un-gated blend quickly).
   - Compute 60-day rolling Pearson correlation between
     `EBP_z_lagged` and `σ²_port`.
   - Measure `frac_exceed = (|ρ_rolling| > 0.30).mean()`.
   - **If `frac_exceed > 0.20` on ANY dataset → write
     `pre_val_failed.json` and exit to final_report**. No blend run,
     no gate, no DSR spent.

4. **`overlay_numpy_reference.py`** (G7 cross-lib):
   - `ebp_zscore_np`, `apply_blend_with_credit_overlay_np` —
     hand-rolled numpy mirrors of the pandas implementation.

5. **`run_backtests.py`**: conditional on pre-val pass — runs 3
   datasets × 1 cfg, writes `results.json`.

6. **`compute_gates_and_score.py`**: reuses iter 008's G1-G7 battery
   + `CUMULATIVE_N_TRIALS = 4258` (if pre-val passed); scores via
   `scoring.score_strategy()`; writes `verdict.json`.

7. **Update BASE_MEMORY.md + DEAD_ENDS.md** per Stage 5, auto-prune
   if needed (current file at ~12 KB, well under 18 KB ceiling; new
   entry adds ~1.5 KB → no prune needed).

## Overlay configuration (pre-committed, ex-ante)

```python
OVERLAY_CFG = {
    "cfg_id": "ebp_z252_t100_h50_eq",
    "indicator": "ebp_monthly",       # Gilchrist-Zakrajšek 2012 residual
    "zscore_window": 252,             # 1-year trailing stability baseline
    "threshold": 1.0,                 # z > 1.0 = upper-tail credit stress
    "haircut": 0.5,                   # tier-2 [systematic_trading p.144]
    "applied_to": "equity",           # SPY leg only (respect flight-to-quality)
    "lag_bars": 1,                    # no look-ahead
    "align_method": "month_forward_fill",  # EBP known at month end
}

BLEND_CFG = {  # reused unchanged from iter 008
    "cfg_id": "vt15_L21_cap20",
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
}
COMBINED_CFG_ID = "vt15_L21_cap20+ebp_z252_t100_h50_eq"
```

Rationale for threshold=1.0: upper-tail stress gate; z=1.0 corresponds
to ~16% tail of standardized EBP distribution, which matches GZ2012's
empirical density of "stress episodes" (5-20% of observations, depending
on the sample). Symmetric to iter 009/012's threshold=0 on T10Y3M
(also upper-tail stress, inverted sign).

## Expected outcomes (scoring)

Plausible scenarios:

- **Best case** (pre-val passes, overlay preserves lead-time):
  Sharpe lift +0.03 to +0.10 on 1-2 datasets; score 75-85 STRONG,
  Kill triggers clean. **New hunt-loop high**.
- **Middle case** (pre-val passes, overlay fires on same bars as
  σ²_port): Sharpe regresses 0 to −0.03; score 55-70 MARGINAL/PROMISING
  with Kill #1 or #3 tripped; confirms EBP subordinate-axis to vol
  on blend — consistent with iter 009/012/013 family.
- **Pre-val failure case**: |ρ| > 0.30 on > 20% bars → abort, add to
  DEAD_ENDS, iteration closes in <30 min. Confirms EBP-on-blend is
  another instance of the cointegration dead-end family.
- **Worst case**: score 40-55 MARGINAL with Kill #1 + #3 + #6 all
  triggered, confirming the 100% bottom-20 overlap diagnostic extends
  from vol-proxy signals to macro credit signals on this mechanism.
  Closes the macro-overlay category entirely for iter 008's blend.

## Relation to dead-ends

This iteration is NOT in any closed dead-end:

- Not T10Y3M or yield-curve signal (DEAD_ENDS "T10Y3M overlay family
  CLOSED" — iter 012 structural cointegration).
- Not a vol-proxy feature or classifier (DEAD_ENDS "Meta-labeling
  with any vol-proxy feature set" — iter 013).
- Not a timeframe change (DEAD_ENDS "Weekly/monthly blends" — iter 011).
- Not a minor variation of a tested cfg.

Structural novelty: **credit-risk-premium signal with
pre-validation gate against vol cointegration**. The pre-validation
gate itself is novel — no prior iteration has attempted an empirical
screen before committing DSR budget.
