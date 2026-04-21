# Phase 3.5e — c03 `ema100_tlt` AGGREGATE

**Config:** Binary EMA100 regime filter, TLT off-leg (yield + diversification).  
**Citation:** `[leverage_for_the_long_run, p.31]` (Gayed tests EMA variants on SPY signal; TLT as defensive hedge outperforms cash in long bonds bull market).  
**Window:** 2002-07-26 → 2026-04-15 (23.7 yr, 5 967 bars). TLT-constrained start.  
**Trial count after c03:** 20 cumulative (c01: 12, c02: +4, c03: +4).  
**Verdict: DEAD — 0/4 pre-pass (DSR + OOS + Calmar + Sharpe_net fail universally).**

---

## Results table

| Asset | Sharpe_net | CAGR_net | MaxDD   | Calmar | DSR_p | WF    | OOS  | FWD  | Beats SPY |
|-------|-----------|---------|---------|--------|-------|-------|------|------|-----------|
| QLD   | 0.496 ✗   | 12.0%   | -64.8%  | 0.218 ✗ | 0.158 ✗ | 8/8 ✓ | ✗   | ✓   | ✓         |
| SSO   | 0.389 ✗   | 7.2%    | -57.9%  | 0.146 ✗ | 0.357 ✗ | 7/8 ✓ | ✗   | ✗   | ✗         |
| TQQQ  | 0.505 ✗   | 15.3%   | -76.3%  | 0.235 ✗ | 0.158 ✗ | 8/8 ✓ | ✗   | ✓   | ✓         |
| UPRO  | 0.391 ✗   | 8.8%    | -68.5%  | 0.152 ✗ | 0.370 ✗ | 7/8 ✓ | ✗   | ✗   | ✓         |

Gates: PBO @ aggregate-level (full 144-trial matrix); Sharpe_net > 0.8; Calmar > 0.5; DSR p < 0.05.

**Best asset: TQQQ** (Sharpe_net=0.505, gap −0.295 to gate).

---

## Gate analysis

### Gate 2 — DSR (p < 0.05)
All 4 assets fail. Cumulative n_trials at time of each test: 17, 18, 19, 20.  
p-values: QLD=0.158, SSO=0.357, TQQQ=0.158, UPRO=0.370.  
IS Sharpe values (0.457–0.594) are too low to survive DSR correction at these trial counts.  
The 23.7-year window is long enough — the signal itself is insufficient.

### Gate 3 — WF ≥ 6/8
QLD and TQQQ pass 8/8; SSO and UPRO pass 7/8 (one fold negative each, around 2020-2022).  
EMA100 produces consistent directional periods: mostly positive folds even at low Sharpe levels.

### Gate 4 — OOS (IS_Sharpe vs OOS_Sharpe)
All 4 assets fail. OOS period = 2021-07-14 → 2026-04-15 (4.75 yr).  
OOS Sharpe values: QLD=0.175, SSO=0.118, TQQQ=0.251, UPRO=0.211.  
IS Sharpe values: QLD=0.693, SSO=0.543, TQQQ=0.685, UPRO=0.522.  
Sharp IS→OOS degradation (~3×) reflects the 2021-2026 environment: equity bull run + TLT bear market  
(rates rising aggressively 2022-2023 hurt the off-leg returns significantly).

### Gate 5 — FWD (Jan–Apr 2026)
QLD and TQQQ pass (FWD Sharpe: 0.064, 0.066). SSO and UPRO fail (-0.172, -0.182).  
EMA100 on SPY signal caught the 2026 tariff shock for QQQ-linked assets but not SPY-linked ones.  
The QQQ index had a slightly different trajectory than SPY during the Jan-Apr 2026 tariff episode.

### Economic gates — Calmar and Sharpe_net
All fail badly. Best Calmar=0.235 (gate 0.5, gap −0.265). Best Sharpe_net=0.505 (gate 0.8, gap −0.295).  
CAGR_net beats SPY (7.88%) for QLD/TQQQ/UPRO but not SSO. Risk-adjusted returns inadequate across the board.

---

## Comparison vs c01 and c02

| Config       | Best Sharpe_net | Best CAGR_net | Best Calmar | FWD failures |
|-------------|----------------|--------------|-------------|--------------|
| c01 sma200   | ~0.45 (QLD)    | ~10%         | ~0.19       | 4/4 ✗        |
| c02 sma150   | 0.475 (QLD)    | 10.6%        | 0.252       | 0/4 ✓        |
| c03 ema100   | 0.505 (TQQQ)   | 15.3%        | 0.235       | 2/4 partial  |

EMA100+TLT is the best binary regime config tested so far:
- Higher absolute returns than SMA200/SMA150 variants (TLT yield in off-leg helps)
- Better Sharpe_net than c01 and c02
- But still far from the 0.800 gate — gap is −0.295 to gate (c02 was −0.325, c01 ~−0.350)
- The OOS degradation is structural: 2021-2026 was a hostile period for bond-based defensive strategies

---

## Stage-2 concordance

| Asset | Stage-2 source | Δ CAGR | Window     | Status      |
|-------|---------------|--------|------------|-------------|
| QLD   | N/A (no QQQSIM) | —    | —          | —           |
| SSO   | N/A (Tiingo SSO unavailable) | — | —    | —           |
| TQQQ  | yfinance direct | +0.73 pp | 2010-2026 | CONCORDANT ✓ |
| UPRO  | yfinance direct | +0.69 pp | 2009-2026 | CONCORDANT ✓ |

Reference_prices.parquet is clean (Tiingo-first post-2026-04-21 rebuild). Both TQQQ and UPRO Stage-2 deltas well within the ±3 pp concordance threshold.

---

## Cross-lib (bt) deltas

| Asset | bt CAGR | S1 CAGR | Δ pp  | Status       |
|-------|---------|---------|-------|--------------|
| QLD   | 14.33%  | 14.15%  | +0.19 | CONCORDANT ✓ |
| SSO   | 9.81%   | 8.46%   | +1.34 | CONCORDANT ✓ |
| TQQQ  | 17.96%  | 17.95%  | +0.01 | CONCORDANT ✓ |
| UPRO  | 12.40%  | 10.39%  | +2.01 | CONCORDANT ✓ |

All 4 assets concordant at cross-lib level (all Δ < 3 pp). This is the most consistent cross-lib result across all c0x configs so far. The shared 23.7-yr window reduces the synthetic extension divergence seen in c02.

---

## Structural diagnosis

The EMA100+TLT configuration is the best binary regime variant in this grid. Three structural problems:

1. **TLT bear market 2022-2023:** TLT fell ~-40% in 2022 when rates rose 400+ bps. Being in TLT as defensive hedge during this period produced negative off-leg returns. The off-leg was worse than cash during this window.

2. **OOS degradation (2021-2026):** IS Sharpe ~0.6-0.7 collapses to OOS Sharpe 0.12-0.25. This is not overfitting — it's a regime change. Binary on/off regimes work well in trending markets but the 2021-2026 chop + rising rates = difficult environment.

3. **DSR with 1 config variant:** Only 1 structural config tested per ticker (unlike D5's 7 correlated variants). DSR p-values around 0.16-0.37 suggest the Sharpe achieved is explained by chance given the 20-trial accumulated count. Needs higher IS Sharpe to pass.

**Next lead (c05 — mom12mo)** uses a fundamentally different mechanism: time-series momentum rather than price/MA crossover. `[dual_momentum, ch.6]`

---

## Verdict

**DEAD — 0/4 pass.** Moving to Phase 3.5e dead ends.  
EMA100+TLT is the best binary regime config but still 0.295 Sharpe_net below the gate.  
The OOS environment (2021-2026 rising rates) is hostile to bond-based defensive strategies.  
The gap from binary MA configs to the gate requires a fundamentally different signal structure.  
**c04 (sma200_shv) SKIPPED** — SHV not in reference_prices.parquet (confirmed: tickers = GLD/QLD/QQQ/SPXL/SPY/SSO/TLT/TMF/TQQQ/UGL/UPRO).  
**Next: c05 — mom12mo** (Antonacci 12-month absolute momentum). `[dual_momentum, ch.6]`
