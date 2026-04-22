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
| F | `f_vol_target_managed_futures` | `systematic_trading.md` (p.118-119, p.137-148, p.170-174, p.282-285, p.185-188), `volatility_trading.md` | Pepperstone CFD | 10-20d hold | done | ❌ FAIL (12/13) | 6-asset multi-class MF basket (SPY/TLT/GLD/USO/EFA/IEF) with Carver continuous EWMAC 16:64 + portfolio-level 15% vol target + IDM=√N cap 2.5 + 10d rebal + position inertia 10%. OOS Sharpe 0.115 / CAGR −0.14% / MDD −36.5% / DSR p=0.94 / PBO 0.60 / cost×2 Sharpe −0.46. **Gross Sharpe 0.60 pré-custo** (signal works) mas swap drag 311% cumulativo em 25 anos @ 2.22× alavancagem média erases edge — confirms Carver speed-limit `[systematic_trading, p.185-188]`. Cross-lib Δ=0.000pp (PASS). Differentiates from V2-L1: continuous EWMAC vs binary past-return, portfolio-level IDM vs per-leg vol, 6 asset-class ETFs vs 30-asset FX-dominant. |
| H | `h_amh_regime_switching` | `adaptive_markets.md` (_archive, p.282-283 RULE 1A-5A, p.244-246 ch.7), `regime_change.md` (_archive, p.14-17 ch.2, p.25-27 ch.3), `fin_time_series_tsay.md` (_archive, p.186-187 §4.1.4) | Inter (ETFs) | 21d rebal | done | ❌ FAIL (8/13) | 3-asset SPY/TLT/GLD with in-house Gaussian HMM (Baum-Welch EM + Viterbi, no hmmlearn) on 20d realized σ/ρ/skew of SPY-TLT; 18-cell grid n∈{2,3,4}×feature∈{σ,σρ,σρskew}×cadence∈{10,21}d. Winner n2_sigma_rc21: OOS Sharpe 0.69 / CAGR 9.47% / MDD −21.18% / FWD Sh 1.21 / median hold 42d / PBO 0.194 / cross-lib Δ=0.000pp / data Δ=0.45pp. Fails bootstrap CI, Sharpe 1.5, CDI CAGR, WF DD 37%, IR −0.17, DSR p=0.56, cost×2 Sharpe 0.69. **Diagnostic:** HMM separates IS into low-vol (67%) + crisis (33%) cleanly, but state-conditional mean SPY return IDENTICAL across states (+0.04%/day both) — classifier gates volatility, not direction. Differentiator vs V2-L2 Gayed landed (HMM ≠ EMA cross), edge did not. |
| J | `j_ml_classical` | `ml_for_algo_trading.md` (ch.4 p.82-93, ch.12 p.388-400), `ml_for_asset_managers.md` (p.8 §1.4.2, p.21 §1.9), `advances_fin_ml.md` (p.103-110, p.208-211, p.31-34) | Inter (ETFs) | 5d rebal | done | ❌ FAIL (8/13) | Track J1 (Jansen GBM, not J2 FFD-reg). 7-ETF panel SPY/QQQ/TLT/GLD/EEM/XLF/XLE; sklearn GradientBoostingClassifier 300×depth3 lr0.05 substitutes LightGBM (absent in venv) per ch.12 p.390-400; 10 panel-shared features (vol_60/corr_spy/vol_20/mom_z/ret_{1,5,20}/RSI14/dow/regime_SPY200); forward 5d sign binary label; 50% equity per triggered ticker capped 100%. Purged 5-fold + 5×H embargo IS only, model frozen post-IS. Winner n300_d3_t55_h5: OOS Sharpe **0.231** / CAGR **2.62%** / MDD **−35.32%** / DSR p=0.890 / bootstrap OOS CI [−0.84,+1.73] / IR vs SPY −0.92 / WF 8/8 but DD 35.3% / cost×2 S=0.138 / PBO 0.016 (perverse — all 16 configs equally mediocre OOS). IS→OOS Sharpe decay 1.250→0.231 = regime-shift intolerance. Feature importance 51.6% on vol+corr = regime classifier, not swing predictor (median hold 457.5d in 10 runs). Differentiates from V2-L3 AFML on every axis (universe, label paradigm, model, training regime, sizing). FWD Sharpe 1.17 sole positive. Cross-lib Δ=0.000pp (handroll, gate 9 deferred per 3.5b/f precedent). |

## Waves

- **Wave 1 (HIGH):** A Clenow cross-sectional momentum, B RP inverse-vol, C GTAA 10-mo SMA — _dispatched 2026-04-23_
- **Wave 2 (MED):** D Chan MR pairs, E Ehlers cycles, F vol-targeting managed futures, H Adaptive Markets regime, I stat-sound indicators — _pending_
- **Wave 3 (LOW):** G Aronson EBTA, J ML classical, K universal trend, L sentiment/PEAD — _pending_

## Counters

- FAIL: 9
- PARTIAL (12/13): 0
- WINNER: 0
- Remaining until escalation: 1 FAIL **or** 3 PARTIAL
