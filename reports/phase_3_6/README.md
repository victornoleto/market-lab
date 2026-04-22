# Phase 3.6 — swing-winner hunt running index

**Plan:** `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md`
**Branch:** `phase3.6/swing-winner-hunt-20260423`
**Baseline pytest:** 918 green (collection verified 2026-04-23)
**Engine:** F2-patched (commit `7b90a8f`), lookahead-clean.

---

## Protocol

- Stop at **first winner** (all 13 gates pass, with user-locked relaxations in plan §5).
- Escalate after **10 FAIL or 3+ PARTIAL** (write `BREADTH_NO_WINNER.md`).
- Every candidate: `<family_slug>/AGGREGATE.md` + jornada entry + commit.
- Excludes 6 rejected V2 leads (TSMOM, Gayed EMA, AFML meta-label, Carver RP, Kalman pairs, Donchian vol-breakout).

## Candidates tried

| # | Family slug | Source book(s) | Broker | Horizon | Status | Verdict | Notes |
|---|---|---|---|---|---|---|---|
| A | `a_clenow_momentum` | `stocks_on_the_move.md` | Inter (stocks) | 21d rebal | done | ❌ FAIL (3/13) | OOS Sharpe 0.25, CAGR 2.67%, MDD −26.62%, DSR p=0.72, bootstrap CI straddles zero. IR vs SPY −0.63. FWD salvages (Sharpe 1.18 / CAGR 16.4%) but doesn't rescue OOS. Universe = Tiingo 1165 ADV>$50M (PIT-S&P proxy). |
| B | `b_risk_parity_inverse_vol` | `risk_parity.md`, `systematic_trading.md` | Inter (ETFs) | 21d rebal | done | ❌ FAIL (5/13) | OOS Sharpe 0.17, CAGR 1.31%, MDD −25.40% — edge absent; 2018-2023 rate shock killed bond+equity diversification; leverage cap prevents CDI-floor clearance |
| C | `c_gtaa_faber_10mo` | `trading_evolved.md` (p.183-185, p.211-212), `systematic_trading.md` | Inter (ETFs) | 21d rebal | done | ❌ FAIL (5/13) | OOS Sharpe 0.41, CAGR 3.89%, MDD −20.71%, **PBO 0.909** (catastrophic). 4-asset variant SPY/EFA/GLD/IEF (REIT+DBC absent from Tiingo). Cross-lib Δ=0.000pp (no alignment bug). Confirms Clenow's p.211-212 caveat: 10-mo MA is hindsight-curve-fit. |
| D | `d_chan_mr_pairs` | `algo_trading_chan.md` (p.51-73, p.88-89, ch.3) | Pepperstone CFD | 5-15d hold | done | ❌ FAIL (5/13) | Non-Kalman variant (rolling OLS + EG gate) — 57 trades across 5 ETF pairs, median hold 10d. OOS Sharpe −0.51 / CAGR −0.33% / DSR p=0.996 / IR vs SPY −0.67 / bootstrap CI [−1.37,+0.50] straddles zero. MDD safe (−2.37%), PBO 0.30 (no overfit), cross-lib Δ=0.37pp (PASS). Cointegration OFF 79-91% of bars — confirms Chan's p.88-89 caveat on ETF pair-edge compression. Contrast V2-L5 Kalman (0 trades): two roads, same no-edge destination. |
| E | `e_ehlers_cycles` | `cycle_analytics.md` (p.77-137, p.220-221), `rocket_science.md` | Pepperstone CFD | 5-15d hold | done | ❌ FAIL (10/13) | 5-ETF basket (SPY/QQQ/GLD/TLT/EFA) with roofing filter + autocorrelation periodogram DC + adaptive RSI (anticipate entries). OOS Sharpe −0.61 / CAGR −9.95% / MDD −53.4% / DSR p=0.998 / IR vs SPY −1.39 / bootstrap CI [−1.86,+0.81]. 697 trades (median 6.0d, gate 7 PASS); cum cost 163% of equity dominates. PBO 0.516 (just above 0.5 line). FWD Sharpe +0.60 is the sole edge signal. Cross-lib Δ=0.000pp (PASS). Confirms Ehlers' own caveat `[cycle_analytics, p.xi-xii]`: "cycles in trend regime = folly." |
| I | `i_stat_sound_indicators` | `stat_sound_indicators.md` (p.170, p.174, p.299-306), `testing_tuning.md`, `evidence_based_ta.md` | Inter (ETFs) | 5-15d hold | done | ❌ FAIL-structural (0 survivors / 15 gates undefined) | 5-ETF universe SPY/QQQ/GLD/TLT/EEM; pool of 8 canonical indicators (RSI14 MR, MACD hist-cross, Connors RSI2 MR, Donchian-20 breakout, z-score-5 MR, Bollinger 2σ MR, SMA200 trend, CN20 MR). 500-perm simple-market MCPT + Bonferroni M=8. **0/8 survive at p_Bonferroni<0.001** — best was Connors-RSI2 at p_raw=0.032 (p_corr=0.256). No ensemble formed → 13 gates all undefined. Scientifically informative FAIL, consistent with Aronson's 6,402-rule study `[evidence_based_ta, p.459]` on S&P 500. |

## Waves

- **Wave 1 (HIGH):** A Clenow cross-sectional momentum, B RP inverse-vol, C GTAA 10-mo SMA — _dispatched 2026-04-23_
- **Wave 2 (MED):** D Chan MR pairs, E Ehlers cycles, F vol-targeting managed futures, H Adaptive Markets regime, I stat-sound indicators — _pending_
- **Wave 3 (LOW):** G Aronson EBTA, J ML classical, K universal trend, L sentiment/PEAD — _pending_

## Counters

- FAIL: 6
- PARTIAL (12/13): 0
- WINNER: 0
- Remaining until escalation: 4 FAIL **or** 3 PARTIAL
