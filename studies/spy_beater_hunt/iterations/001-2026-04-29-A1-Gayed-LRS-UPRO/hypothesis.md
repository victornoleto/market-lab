# Iter 001 — A1 Gayed LRS UPRO + 200d SMA gate

**Date**: 2026-04-29
**Tier (PROMISING_DIRECTIONS.md)**: Tier 1 — highest priority literature backing.
**Cumulative n_trials at iter start**: 0 → after iter: 4

## Hypothesis

A regime-gated leveraged equity strategy can beat SPY in BOTH CAGR (≥ 13.80%
mean across 3 datasets) AND MDD (≤ 40.85% mean) by:

1. Holding 100% UPROSIM (3× SPY synth) when SPY is in a bullish regime
   (price > 200d SMA), capturing the leveraged equity premium.
2. Rotating to a defensive sleeve (IEF / CASHX / KMLM mix) when SPY is in
   a bearish regime (price ≤ 200d SMA), avoiding the worst leveraged-equity
   drawdowns where daily-reset compounding decay is most punishing.
3. T+1 execution lag avoids peek-ahead.

## Citation

Primary: `[leverage_for_the_long_run, ch.3-4, p.40-60]` — Gayed shows the
200d-SMA gate dramatically reduces LETF volatility decay; backtests in the
book report ~18-22% CAGR with MDD 25-35% on real LETFs.

## Configs (4)

1. **a1_pure_lrs**: 100% UPROSIM when on, 100% IEFSIM when off.
   Most aggressive. KILL #6 monitor — if this can't reach mean CAGR ≥ 13.80%,
   the entire Tier 1 LRS-UPRO direction is structurally subordinate.
2. **a1_lrs_cash**: 100% UPROSIM when on, 100% CASHX when off.
   Pure cash off-regime; tests whether IEF duration adds or detracts.
3. **a1_lrs_split**: 50% UPROSIM + 50% SSOSIM when on, 100% IEFSIM when off.
   Half-aggressive; tests whether 2.5× average leverage beats 3×-or-cash extremes.
4. **a1_lrs_kmlm_off**: 100% UPROSIM when on, 50% IEFSIM + 50% KMLMSIM when off.
   KMLM crisis-alpha during off-regime; tests whether trend-following
   diversification helps in stress regimes (2008 / 2022).

## Datasets

- `lh_56y` (UPROSIM/SSOSIM start 1986-01-02; full ~40y window).
- `vt_real` (2008-06+ — SPY proxy era).
- `ndx_real` (2010-02+ — QQQ Tiingo era; serves as concentrated-growth check).

## Bar conditions (strict)

- Bar 1 (CAGR): mean(CAGR_lh_56y, CAGR_vt_real, CAGR_ndx_real) ≥ 0.1380
- Bar 2 (MDD):  mean(MDD_lh_56y, MDD_vt_real, MDD_ndx_real) ≤ 0.4085
- Bar 3 (Gates): 7-gate battery passes ≥ threshold on ≥ 2/3 datasets
  (lh_56y ≥5/7, vt_real ≥4/7, ndx_real ≥4/7)

## Expected outcomes

- Per Gayed literature: CAGR 16-22%, MDD 25-40%.
- KILL #6 if a1_pure_lrs (most aggressive config) doesn't reach CAGR 13.80%.

## Why might fail

- **Whipsaw cost**: signal flips back-forth in choppy markets (200d SMA is laggy).
- **2022 inflation**: 200d SMA was triggered for SPY, but TLT/IEF also crashed
  → off-regime sleeve may have lost money simultaneously.
- **LETF decay**: even with the gate, daily-reset decay is ~1-3%/y.
- **Synth fidelity**: UPROSIM/SSOSIM/KMLMSIM are testfolio synthetic series;
  real-world tracking error not modelled.

## INCOMPLETE flags

- UPROSIM/SSOSIM/TQQQSIM are testfolio cache synths (no real LETF inception
  data pre-2009 for UPRO / pre-2010 for TQQQ).
- KMLMSIM pre-1988 splice via FF MoM proxy (UMD academic) — overstates KMLM
  Sharpe by ~3× per `studies.long_term_portfolio.datasets.py` caveat.
- CASHX assumes T-bill returns; not realistic for 2010s zero-rate era when
  short rates were ~0%.
