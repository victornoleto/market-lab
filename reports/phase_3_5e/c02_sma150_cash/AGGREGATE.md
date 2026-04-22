# Phase 3.5e — c02 `sma150_cash` AGGREGATE

**Config:** Binary SMA150 regime filter, cash off-leg (0% yield).  
**Citation:** `[leverage_for_the_long_run, p.30]` (Gayed tests MA variants; SMA150 = sensitivity test vs canonical SMA200).  
**Window:** 2001-05-15 → 2026-04-17 (24.9 yr, 6 267 bars).  
**Trial count after c02:** 16 cumulative (c01: 12, c02: +4).  
**Verdict: DEAD — 0/4 pre-pass (DSR + Calmar + Sharpe_net fail universally).**

---

## Results table

| Asset | Sharpe_net | CAGR_net | MaxDD | Calmar | DSR_p | WF | OOS | FWD | Beats SPY |
|-------|-----------|---------|-------|--------|-------|-----|-----|-----|-----------|
| QLD   | 0.475 ✗   | 10.6%   | -49.4% | 0.252 ✗ | 0.141 ✗ | 8/8 ✓ | ✓ | ✓ | ✓ |
| SSO   | 0.388 ✗   | 6.6%    | -44.3% | 0.176 ✗ | 0.297 ✗ | 8/8 ✓ | ✓ | ✓ | ✓ |
| TQQQ  | 0.456 ✗   | 12.4%   | -65.5% | 0.222 ✗ | 0.185 ✗ | 8/8 ✓ | ✓ | ✓ | ✓ |
| UPRO  | 0.364 ✗   | 7.6%    | -61.6% | 0.145 ✗ | 0.371 ✗ | 8/8 ✓ | ✓ | ✓ | ✓ |

Gates: PBO @ aggregate-level (144-trial matrix); Sharpe_net > 0.8; Calmar > 0.5; DSR p < 0.05.

**Best asset: QLD** (Sharpe_net=0.475, gap −0.325 to gate).

---

## Gate analysis

### Gate 2 — DSR (p < 0.05)
All 4 assets fail. Cumulative n_trials at time of each test: 13, 14, 15, 16.  
The actual IS Sharpe values (0.456–0.559) are too low to survive DSR correction at these trial counts.  
QLD is closest at p=0.141 (gap = 3× the gate threshold).

### Gate 3 — WF ≥ 6/8
All 4 assets pass with 8/8. The SMA150 signal produces consistent directional periods across all 8 folds, even though the level is too low.

### Gate 4 — OOS
All 4 pass. OOS Sharpe exceeds IS Sharpe in all cases (OOS IS improvement 15–71%), which is encouraging structurally but irrelevant given the low absolute levels.

### Gate 5 — FWD
All 4 pass. Unlike c01 (sma200_cash/gld/tlt) which universally failed on Jan–Apr 2026 tariff shock, SMA150 stayed in cash during that period. **Key insight:** shorter MA caught the market breakdown faster, avoiding FWD failure.

### Economic gates — Calmar and Sharpe_net
All fail badly. Best Calmar=0.252 (gate 0.5, gap −0.248). Best Sharpe_net=0.475 (gate 0.8, gap −0.325). CAGR_net beats SPY for all assets but the risk-adjusted return is inadequate.

---

## Stage-2 concordance

| Asset | Δ CAGR | Status |
|-------|--------|--------|
| QLD   | N/A (no QQQSIM) | — |
| SSO   | +0.17 pp | CONCORDANT ✓ |
| TQQQ  | +0.05 pp | CONCORDANT ✓ |
| UPRO  | +0.12 pp | CONCORDANT ✓ |

Reference_prices.parquet is clean for these assets (Tiingo-first post-2026-04-21 rebuild).

---

## Cross-lib (bt) deltas

| Asset | bt CAGR | S1 CAGR | Δ pp | Status |
|-------|---------|---------|------|--------|
| QLD   | 15.46%  | 12.45%  | +3.01 | Borderline DIVERGENT |
| SSO   | 12.08%  | 7.78%   | +4.30 | DIVERGENT |
| TQQQ  | 19.30%  | 14.56%  | +4.74 | DIVERGENT |
| UPRO  | 15.60%  | 8.90%   | +6.70 | DIVERGENT |

**Pattern consistent:** bt synthetic pre-inception extension (pre-2001/2006/2009 for LETF histories) uses a different construction method than reference_prices.parquet. Divergence increases with leverage factor and time before inception. Not a data error — bt uses proxy reconstruction; this affects absolute levels but not the directional signal pattern.

---

## Structural diagnosis

SMA150 vs SMA200 comparison (c01 best: QLD, Sharpe_net~0.45):
- SMA150 reduces off-leg exposure time (more time invested) — QLD: 71.7% in-asset
- Shorter MA = more toggles but each toggle is slightly earlier
- Net effect: slightly better FWD (caught 2026 tariff shock earlier), similar Sharpe_net
- The off-leg (cash=0%) is the binding constraint — no yield in defensive state
- Conclusion: cash off-leg is structurally inferior for 24.9-year windows; dividend/interest drag dominates

**c03 (ema100_tlt)** has a fundamentally different structure: TLT provides yield and diversification in off-leg. This is the natural next test per spec order.

---

## Verdict

**DEAD — 0/4 pass.** Moving to Phase 3.5e dead ends.  
No assets pre-pass; all fail on DSR, Calmar, and Sharpe_net simultaneously.  
Structural finding: cash off-leg is insufficient for the economic gates regardless of MA period.
