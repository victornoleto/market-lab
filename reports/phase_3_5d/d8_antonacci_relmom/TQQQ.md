# D8 Antonacci RelMom — TQQQ+GLD (iter 12) [SWING BROKER]

**Strategy:** Antonacci-style dual momentum: slope_dominant composite + relative momentum filter.
  Three configs test the hypothesis that RelMom exit improves FWD while preserving Sharpe.
**Window:** 2010-02-11 → 2026-04-14 (16.2yr)
**Best config:** `slope_dom_pure` — **NO PASS** (fails FWD, PBO)
**PBO (3 configs):** 0.794 (FAIL — IS-winner unstable across CSCV folds)

**Citations:** [stocks_on_the_move, p.81, ch.6], [leverage_for_the_long_run, p.13],
  [antonacci_dual_momentum, ch.4], [advances_fin_ml, p.208-211]

## Configs tested

| # | Config | Signal logic |
|---|--------|--------------|
| 1 | slope_dom_pure | (0.6·z_slope_MA200_SPY + 0.25·z_mom90_SPY + 0.15·z_invvol_TQQQ) > 0 |
| 2 | slope_dom_rm15 | config-1 AND TQQQ.pct_change(15d) > GLD.pct_change(15d) |
| 3 | sma200_rm20 | SPY > SMA200 AND TQQQ.pct_change(20d) > GLD.pct_change(20d) |

## Results

| Config | Sharpe | SN | CAGR_net% | MaxDD% | Calmar | WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | FWD>0 | PASS |
|--------|--------|----|-----------|--------|--------|----|-------|-------|-----|-------|----------|---------|--------|-------|------|
| slope_dom_pure | 0.997 | 0.847 | 28.8 | -49.4 | 0.686 | 7/8 | 1.32 | -1.344 | 0.794 | 0.001 | ✓ | ✓ | ✓ | ✗ | ✗ |
| slope_dom_rm15 | 0.897 | 0.762 | 19.8 | -42.0 | 0.554 | 7/8 | 1.00 | 0.573 | 0.794 | 0.004 | ✓ | ✓ | ✗ | ✓ | ✗ |
| sma200_rm20 | 0.875 | 0.744 | 22.7 | -49.1 | 0.543 | 8/8 | 1.19 | 0.523 | 0.794 | 0.005 | ✓ | ✓ | ✗ | ✓ | ✗ |

**SPY B&H net CAGR threshold:** 10.36%

## Structural diagnosis

PBO=0.794 is HIGH because the IS-winner changes by CSCV fold:
- In bull IS periods: slope_dom_pure wins (no restriction → more TQQQ)
- In volatile IS periods (containing tariff shock): slope_dom_rm15/sma200_rm20 win
- This instability → high PBO

**The fundamental contradiction for Phase 3.5d:**
- Low PBO requires a stable IS winner (one config dominates all IS periods)
- FWD pass requires a config that exits TQQQ during the tariff shock
- These two requirements are MUTUALLY EXCLUSIVE for this dataset:
  - slope_dom_pure: SN=0.847 ✓, FWD=-1.344 ✗
  - slope_dom_rm15: FWD=0.573 ✓, SN=0.762 ✗ (gap=-0.038)
  - D5 vol15_lk20: SN=0.855 ✓, FWD=0.182 ✓, PBO=0.599 ✗

**Maximum achievable SN while passing FWD:** 0.762 (slope_dom_rm15). Gate requires 0.800 (gap=0.038).
**Maximum achievable FWD Sharpe while passing SN>0.800:** requires slope_dom_pure → FWD=-1.344.

## Phase 3.5d conclusion

After 8 lead experiments (D1-D8), no configuration passes all 5 overfit gates + all 3 economic gates.
The binding constraints are the 2026 tariff shock in the FWD window (concentrated in Jan-Apr 2026).
This is a genuine stress test scenario that the FWD gate is designed to catch.
Moving to Phase 3.5e arbitration to decide: relax FWD gate vs. new strategy family.
