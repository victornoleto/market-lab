# Iter 008 — WLDU + Gayed 200d SMA (LETF Managed)

**Date:** 2026-04-27  
**Slug:** wldu-gayed  
**Status:** hypothesis  
**n_trials (pre-committed):** 1

---

## Hypothesis

Hold a synthetic 2× global equity LETF (WLDU = 2× VTSIM daily-resetting) when the S&P 500
(SPYSIM) closes above its 200-day SMA; rotate to CASHX otherwise. Monthly rebalance check
(Gayed canonical). This strategy captures 2× equity gains during sustained bull trends while
avoiding equity exposure entirely during bear regimes — something no stacked or rotating
strategy in the loop can do (HAA rotates to bonds, VAA holds partial-defensive, Plano C
never exits equity).

**Exact rule:**
- Signal each month-end: if SPYSIM_close > SMA(200d_SPYSIM) → risk-ON → hold 100% WLDU
- Otherwise → risk-OFF → hold 100% CASHX
- WLDU daily return: `2 × VTSIM_daily_ret − CASHX_daily_ret − 0.0075/252`
  (75bps/y drag = 50bps financing spread + 25bps effective expense)

---

## Primary Citation

`[leverage_for_the_long_run, ch.3-4, p.40-60]` — Gayed (2021)

From Table 8 [p.17]: 2× LRS (200-day MA), Oct 1928–Dec 2020:
- 2× LRS annual return: ~15.5% vs S&P 500 ~9.9%
- 2× LRS Sharpe: 0.61 vs S&P 500 Sharpe: 0.32
- Rule [p.13]: "hold leveraged S&P 500 when the index closes above its Moving Average;
  rotate to Treasury bills when the index closes below"
- Rule [p.16]: "Use 200-day Moving Average (SMA) as the primary MA period" — fewest
  transaction costs (~5 rotations/year), most widely referenced, robust across all periods

Note: Gayed tests on S&P 500. This iter applies the same regime filter to global equity (VTSIM).

**Secondary citation:** `[stocks_on_the_move, p.21-30]` (momentum / trend as regime signal,
confirming that trend-following improves risk-adjusted returns across asset classes)

---

## Edge Source

VT/Plano C/HAA/VAA miss what this captures: **complete equity exit**.

- VT b&h: holds equity through all bear markets
- Plano C V3_1 (RSSB/RSST/factor): always ~145% notional equity — 2022 saw MDD 44%+
- HAA SmartStack (WINNER): rotates to bonds/cash within dynamic allocation, but
  remains in equity-stacked positions during choppy regimes (90% weight can be NTSXSIM
  which still has 0.9× equity exposure even in defensive posture)
- VAA SmartStack: similar — B=0 still holds BNDSIM which correlates with equity in rate crises

WLDU with SMA filter: 0% equity exposure when SPYSIM < SMA(200d). During 2008-2009,
2022, even 2020 (Feb-end → CASHX for March):
- Earns T-bill yield + avoids equity drawdown
- Then re-enters at 2× when trend restores → captures bull market recovery at 2× leverage

The 2× leverage also provides a structural CAGR advantage vs 1.5× stacked strategies
(HAA notional ≈ 1.5×) IF whipsaw costs are contained.

---

## Datasets to Test

| dataset | window | benchmark | notes |
|---|---|---|---|
| educational | ~1987-2026 (~39y, SPYSIM binding) | VTSIM b&h | effective start after 200d SMA warmup |
| vt_real | 2008-06 → 2026-04 (~17y) | VTSIM proxy | pre-history since 1986, warmup satisfied |
| ndx_real | 2010-02 → 2026-04 (16y) | QQQ b&h Tiingo | structural CAGR gap to QQQ expected |

WLDU binding: VTSIM + SPYSIM + CASHX all available from 1986+.
Effective educational start: first month-end after SPYSIM has 200 days of history (~late 1986).

---

## Pre-committed Kill Criteria

1. **32y CAGR < 12%** → fail (2× LETF must justify decay risk vs simpler strategies; HAA WINNER
   achieves 14.14% at 1.5× notional — 2× should do at least as well given Gayed Table 8)
2. **Max single WF-window MDD > 35%** → fail (trend filter is the main risk-control mechanism;
   if SMA fails to protect in any window, the LETF exposure is catastrophic)
3. **Whipsaw cost > 1%/y (estimated)** → informational only (not a hard gate; note in report if
   frequency × magnitude suggests material drag vs HAA's near-zero whipsaw)

---

## Expected Budget

- Configs: 1 (single pre-committed: 200d SMA, monthly check, 75bps drag)
- n_trials: 1 (DSR honest per-iter convention; PBO trivial)
- Wall-time: ~5-10 minutes (no grid, single series computation)
- G7 cross-lib: numpy reference required (new simulation logic)

---

## Implementation Plan

1. Load testfolio cache (VTSIM, SPYSIM, CASHX, QQQSIM)
2. Build WLDU synthetic return series: `2*VTSIM_ret - CASHX_ret - 0.0075/252`
3. Compute SPYSIM 200d SMA signal (daily prices, sampled at month-ends)
4. Monthly allocation: 100% WLDU (risk-on) or 100% CASHX (risk-off)
5. Run on 3 datasets; compute metrics (Sharpe, CAGR, MDD)
6. 7-gate battery (G3 nominal + G3' adapted for NOTIONAL_FACTOR=2.0)
7. Numpy cross-lib reference for G7
8. Score via scoring.py (cumulative_n_trials=25)
9. Save results.json + verdict.json
10. Write final_report.md, update BASE_MEMORY.md + DEAD_ENDS.md if applicable
11. Run plot_helper.py for vt_real + ndx_real plots

---

## Structural Novelty vs Prior Iters

| iter | mechanism | same? |
|---|---|---|
| 001-002 | momentum rotation (multi-asset) | No — no momentum, no rotation |
| 003-007 | static/dynamic stacked portfolios | No — binary exit, no stacking |
| 005 (WINNER) | HAA canary + multi-asset dynamic | No — single asset, pure LETF |
| 006 | VAA breadth + fixed sleeve | No — no breadth, no fixed sleeve |
| 007 | Static buy-hold stacked | No — active trend filter |

This is the only iter testing a **pure LETF + binary trend filter** approach.
