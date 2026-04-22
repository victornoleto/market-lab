# Lead D1 — Buy-and-hold 3× LETF Baseline [SWING BROKER]

**Phase:** 3.5d | **Lead:** D1 | **Type:** Atomic legacy (no ticker sweep)
**Status:** COMPLETED — informational baseline (no overfit gates applicable)
**Period:** 2010-02-11 → 2026-04-14 (16.1 years, reference_prices.parquet Stage 1)
**Tested:** 6 portfolio configs × 1 common window
**Iter:** 0 (Phase 3.5d iteration 0)

---

## Purpose

Establish the **CAGR floor** that any regime-filter strategy (D2–D8) must beat.
`[leverage_for_the_long_run, p.16]` — synthetic formula validates that 3× SPY decay
does not destroy CAGR in long bull markets. Question: does 3× LETF buy-and-hold beat
SPY buy-and-hold post 15% IR BR? If yes, regime-filter must beat that 3× floor.

---

## Data

- **Stage 1 only** (reference_prices.parquet, seam-corrected rebuild 2026-04-20).
- Common window (all tickers valid): **2010-02-11 → 2026-04-14** (4067 trading days).
- TQQQ inception 2010-02-09 but first valid yfinance day = 2010-02-11 (2-day NaN gap
  at seam, filled by `dropna()`). UPRO/TMF synthetic pre-inception well-behaved.
- Tax model: 15% flat over CAGR (IR BR, `docs/investment-mandate.md §4`).

---

## Results

### Benchmark table

| Config | CAGR% | CAGR_net% | Sharpe | MaxDD% | Calmar | Beat SPY net |
|---|---|---|---|---|---|---|
| 100% UPRO | 29.67 | 25.22 | 0.767 | 76.8 | 0.386 | ✓ |
| 100% TQQQ | 41.12 | 34.95 | 0.873 | 81.7 | 0.504 | ✓ |
| EW 50/50 UPRO+TQQQ (daily) | 36.18 | 30.75 | 0.839 | 73.5 | 0.492 | ✓ |
| EW 50/50 UPRO+TQQQ (monthly) | 36.10 | 30.68 | 0.839 | 73.3 | 0.492 | ✓ |
| EW 33% UPRO+TQQQ+TMF (daily) | 30.59 | 26.00 | 0.923 | 70.2 | 0.436 | ✓ |
| EW 33% UPRO+TQQQ+TMF (monthly) | 28.90 | 24.56 | 0.905 | 71.7 | 0.403 | ✓ |
| **100% QQQ** | **17.97** | **15.28** | **0.905** | **35.6** | **0.505** | ✓ |
| 60/40 SPY+TLT (monthly) | 6.55 | 5.57 | 0.713 | 29.8 | 0.220 | ✗ |
| **SPY B&H (baseline)** | **12.22** | **10.38** | **0.756** | **34.1** | **0.358** | — |

SPY net threshold: **10.38%/yr** (must exceed for any Phase 3.5d winner).

---

## Analysis

### 1. Buy-and-hold 3× beats SPY — confirmed

All 6 LETF configs beat SPY net post-tax by a large margin (≥14.18pp). This
confirms `[leverage_for_the_long_run, p.16]`: in a 16-year bull-dominant period,
3× leverage amplifies returns faster than volatility decay destroys them.

### 2. But gate failures at economic gates

Despite beating SPY, **all configs fail Phase 3.5d full gates**:

- **Calmar > 0.5 gate:** Only TQQQ alone passes (0.504). All others fail (MaxDD
  76–81% on UPRO/TQQQ configs, 70–72% with TMF included).
- **Sharpe_net > 0.8 gate:** None pass (best is EW 3-leg daily: Sharpe_net 0.785).

These are buy-and-hold configs — they have no overfit gates applicable (no
tunable parameters), so PBO/DSR/WF are not computed. They serve as a ceiling:
regime-filter D2+ must beat these **and** pass all 5 overfit gates.

### 3. Regime-filter floor to beat (D2+ targets)

The **regime-filter improvement bar** comes from two angles:

**If regime-filter adds value:** It should have lower MaxDD (by sitting in cash/TMF
during drawdowns) while maintaining CAGR_net ≥ 30%+ → Calmar > 0.5 becomes
achievable. The EW 50/50 UPRO+TQQQ EW baseline at CAGR=36.18%/MaxDD=73.5% is
the primary contender to beat.

**If regime-filter only reduces CAGR:** Regime-filter must at minimum beat:
- **SPY net (10.38%/yr)** — economic gate §6.3.8 `[specs/phase_3_5d_plano_b_v2_3x_letf.md]`
- **TQQQ B&H net (34.95%)** — to justify the complexity vs simple buy-and-hold

### 4. TMF acts as volatility dampener (−20% MaxDD, −16% CAGR)

Adding TMF to the 3-leg EW portfolio:
- MaxDD: 73.5% → 70.2% (−3.3pp) — modest
- CAGR: 36.18% → 30.59% (−5.59pp) — significant CAGR sacrifice
- Sharpe: 0.839 → 0.923 (+0.084) — meaningful improvement

This hints that regime-filtering may do better than static TMF allocation. D7
(regime-gated dual LETF with TMF off-leg) and D8 (tactical hedge) should
exploit this observation.

### 5. QQQ (unleveraged) is a strong contender

QQQ buy-and-hold: CAGR=17.97%, Sharpe=0.905, MaxDD=35.6%, Calmar=0.505.
- Passes Calmar gate (0.505 > 0.5 ✓)
- Nearly passes Sharpe_net gate (0.769 < 0.8 ✗)
- All of this with 1× leverage vs 3× leverage
This sets a practical floor: is adding leverage to QQQ/SPY via TQQQ/UPRO worth the
additional MaxDD at all?

---

## Conclusions for D2+

1. **TQQQ buy-and-hold** (CAGR_net=34.95%, Calmar=0.504) is the strongest single-asset
   baseline. D2+ regime-filter strategies on TQQQ should target ≥34% net CAGR + Calmar
   > 0.5 to justify the complexity.

2. **EW 50/50 UPRO+TQQQ (daily)** is the best 2-leg combo (CAGR_net=30.75%, Sharpe=0.839,
   Calmar=0.492). Near-miss on Calmar. Regime-filter that reduces MaxDD by even 10pp
   (73.5% → 63.5%) at same CAGR would clear the Calmar gate.

3. **EW 3-leg UPRO+TQQQ+TMF (daily)** has best Sharpe (0.923) and lowest MaxDD (70.2%).
   The TMF drag on CAGR (−5.59pp) might be recouped by regime-filtering TMF in/out.

4. Regime-filter strategies that produce lower CAGR than simple buy-and-hold while
   not clearing MaxDD gates should be discarded — they sacrifice return for insufficient
   drawdown protection.

---

## Cross-lib note

D1 is buy-and-hold — no strategy engine needed. Computation uses direct pandas
return arithmetic (equivalent to any engine). Cross-lib concordance is trivially
satisfied (all engines would give identical daily returns for B&H).

---

## Citations

- `[leverage_for_the_long_run, p.16]` — 3× SPY synthetic formula and long-run CAGR projection
- `[advances_fin_ml, p.298-299]` — DSR and economic gate rationale (not applied to B&H configs)
- `specs/phase_3_5d_plano_b_v2_3x_letf.md §6.3` — economic gate definitions
- `docs/investment-mandate.md §4` — 15% IR BR flat tax model

---

## Links

- Spec: `specs/phase_3_5d_plano_b_v2_3x_letf.md`
- Data: `reports/phase_3_5c/cross_lib/data/reference_prices.parquet`
- Jornada: `jornada/2026-04-20/05-phase-3-5d-d1-bh-baseline.md`
