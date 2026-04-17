# Phase B: Cross-Asset Transport + Cross-Strategy Correlation (Leads #4 & #5)

**Data:** Tiingo daily (2003-2026) + Tiingo 1h (2020-2026). All manifest maxima.

---

## Lead #4 — Cross-Asset Transport

### ETFRotation monthly momentum: expanded 8-ETF universe

Tested original_5 (SPY/QQQ/IWM/GLD/TLT) vs expanded_8 (adds XLK/XLF/EEM).
All ETFs have daily data from 2003+.

| Universe    | IS Sharpe | WF    | DSR p  | IS Gate | OOS 2025 | Stress 2026-Q1 |
|-------------|-----------|-------|--------|---------|----------|----------------|
| original_5  | 0.708     | 8/8   | 0.0009 | ✅ PASS | 1.477    | 1.081          |
| expanded_8  | 0.609     | 7/8   | 0.0035 | ✅ PASS | 1.120    | 1.081          |

**Verdict: TRANSPORT CONFIRMED.** Expanding the universe from 5 to 8 ETFs still
passes all IS gates. IS Sharpe drops slightly (0.708 → 0.609) because adding
XLK/XLF/EEM slightly dilutes the original momentum edge during IS. But the
mechanism is robust — it works on any reasonable universe of liquid ETFs, not
just the original 5. The OOS and Stress period are positive in both cases.

The momentum-rotation mechanism `[stocks_on_the_move, p.81]` is the edge, not
the specific universe. This is a healthy sign for production use.

### BollingerMR GARCH: XLF 1h transport (final untested hourly ETF)

XLF is the financial sector ETF. 1h data from 2020-04-15.

| Period      | Sharpe | Gate  |
|-------------|--------|-------|
| IS (2020-2024) | -0.106 | ❌ FAIL (WF 2/4, DSR p=0.5845) |
| OOS 2025    | -1.095 | —     |
| Stress 2026-Q1 | 1.380 | —  |

**Verdict: FAIL.** XLF has no mean-reversion edge at 1h. Combined with all
prior transport failures (QQQ, IWM, XLK, XLE, GLD, EEM, DIA, TLT), we can
conclusively state: **BollingerMR 1h MR edge is strictly SPY-specific.**

The SPY edge likely derives from its role as the benchmark aggregate index —
it absorbs systematic noise from arbitrage and ETF creation/redemption flows,
creating reliable mean-reversion patterns absent in sector or single-name ETFs.

Scripts: `scripts/run_cross_asset_transport_phase_b.py`

---

## Lead #5 — Cross-Strategy Correlation

Compared daily returns of BollingerMR_GARCH (1h resampled to daily) vs
ETFRotation_top1 over the 2019-12-02 → 2024-12-31 overlap (1277 common days).

| Metric | Value |
|--------|-------|
| Pearson ρ | **0.252** |
| BollingerMR daily Sharpe | 0.950 |
| ETFRotation daily Sharpe | 0.835 |
| 50/50 blend Sharpe | **1.020** |
| Threshold | 0.7 |

**Verdict: INDEPENDENT (ρ = 0.252 ≤ 0.7).**

The two strategies are genuinely independent edges:
- BollingerMR exploits 1h mean-reversion in SPY (entry on band touch, exit next day)
- ETFRotation exploits monthly cross-sectional momentum rotation across 5 ETFs

Different mechanisms, different timeframes, different paths (A vs B), and low
correlation (25%). Running both simultaneously provides real portfolio
diversification `[advances_fin_ml, ch.4]`. The 50/50 blend Sharpe of 1.020
exceeds both individual Sharpes — confirming diversification benefit.

Script: `scripts/run_cross_strategy_correlation_phase_b.py`

---

## Summary for Phase B status

Leads completed this iteration: #4 (cross-asset transport) + #5 (cross-strategy correlation).

Remaining Phase B leads: #6 (regime decomp), #7 (GARCH variant for ETFRotation),
#8 (risk-pct sensitivity at $1k), #9 (production-readiness summary jornada).
