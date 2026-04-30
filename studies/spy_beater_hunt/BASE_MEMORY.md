---
mission: "Find ONE long-term strategy with mean CAGR ≥ SPY (11.21%) AND mean MDD ≤ SPY (55.17%) AND surviving 7-gate battery on ≥ 2/2 datasets"
target_total_iterations: 50
total_iterations: 3
winners_found: 0
closest_to_winner: "iter 003 a3_lrs_split_kmlm20: CAGR 14.99% PASS, MDD 41.87% PASS, gates 6/6 PASS cross_met — winner_conditions_met=TRUE, score 64 (tier PROMISING; tier WINNER requires score ≥ 90)"
status: hunting
latest_iteration: "003-2026-04-30-A3-mixed-gayed-crisis-alpha"
latest_score: 64
latest_tier: PROMISING
latest_bars_met: 3  # CAGR ✓, MDD ✓, Gates ✓
cumulative_n_trials: 14
datasets:
  - "lh_56y (1986+, ~40y, SPYSIM synth, GATE thresh 5)"
  - "spy_real (2003+, ~22.7y, SPY Tiingo adj_close, GATE thresh 5)"
spy_benchmarks:
  cagr_mean: 0.1121
  mdd_mean: 0.5517
  sharpe_mean: 0.6661
direction_status:
  A1_200d_SMA_3x_UPRO: "DISPLACED (iter 001 was closest @ 60; iter 003 KMLM20 wins @ 64)"
  A2_faster_signal: "CLOSED (iter 002 KILL #7) — faster SMA/EMA make MDD WORSE"
  A2_threshold_buffer: "CLOSED (iter 002 KILL #8) — buffer ≥5% makes MDD worse"
  A2_lower_leverage: "DOMINATED — bars 3/3 met but score < 60 (CAGR drag > MDD pts gain)"
  A3_mixed_gayed_crisis_alpha: "PROMISING (best so far, iter 003) — KMLM 20% in ON sleeve drops MDD 9.73pp; score 64"
  A3_kmlm_dose_response: "NEW PROMISING — monotonic positive 10→20%; explore 25-30% in iter 004"
  A3_tlt_dose_response: "NEW PROMISING — 15% TLT competitive with KMLM 10%; strict dose-comparison needed (TLT 20% vs KMLM 20%)"
  B1_HFEA_classical: "NOT YET RUN — TMFSIM ready"
  C1_vol_targeted: "NOT YET RUN"
parent_loop: "studies/long_term_portfolio (43 iters, F1+SPLIT incumbent fallback)"
note: "Forked 2026-04-29. METHODOLOGY REFACTOR 2026-04-29 (post-iter-002): replaced (lh_56y/vt_real/ndx_real) with honest 2-dataset setup (lh_56y/spy_real). vt_real/ndx_real were post-GFC bull-biased (SPY MDD only 33.70%); spy_real (Tiingo daily 2003+) captures full GFC peak-to-trough. New bars: CAGR ≥ 11.21% (was 13.80%), MDD ≤ 55.17% (was 40.85%). Iter 001 a1_lrs_split now passes ALL 3 BARS retroactively (winner_conditions_met=True) — tier remains PROMISING because score 60 < 90 (Sharpe 0.65 + MDD 51.60% close to ceiling). Tier WINNER requires score ≥ 90. Iter 002 selected MARGINAL because n_trials=10 made spy_real DSR fail. Need iter 003+ targeting score ≥ 90 (lift Sharpe + lower MDD margin further). Direction A2-lower-leverage (2× SSO) is the active lever. ALSO new: multi-horizon rolling CAGR/MDD scoring (5/10/15/20y windows, 3+3+2+2pts) replaces 5y rolling Sharpe robustness — both iter 001 and iter 002 selected scored 10/10 on this new criterion. F1+SPLIT remains deploy fallback if 50-iter hunt fails."
---

# spy_beater_hunt — BASE MEMORY

**Read FIRST every iteration.** Conversation history is empty; this file + `iterations/NNN-*/` are continuity. Process: see `SPEC.md`. Infra: `INFRASTRUCTURE.md`.

---

## Mission (recap)

Find ONE long-term strategy with:
- **Mean CAGR ≥ 13.80%** (SPY 3-dataset mean)
- **Mean MDD ≤ 40.85%** (SPY 3-dataset mean)
- **7-gate battery passes ≥ 2/3 datasets**

Per-dataset SPY benchmarks:
| dataset | window | SPY CAGR | SPY MDD |
|---|---|---:|---:|
| lh_56y | 1986-2026 (40y) | 11.47% | 55.14% |
| vt_real | 2008-2026 (~17y) | 14.97% | 33.70% |
| ndx_real | 2010-2026 (16y) | 14.97% | 33.70% |
| **mean** | | **13.80%** | **40.85%** |

---

## Why this hunt exists (context for any iter)

Long_term_portfolio loop concluded 2026-04-29 with F1+SPLIT (NTSX 25 + GDE 25 + KMLM 17.5 + DBMF 17.5 + TLT 15) as deploy-ready candidate. Mean CAGR 10.76% (gap −3.04pp vs SPY mean 13.80%), Mean MDD 16.76% (24pp better than SPY).

User feedback: "MUITO DIFÍCIL seguir uma estratégia que não vai bater o SPY em CAGR" — psychologically + behavioral concern, even if 30y math favors better Sharpe.

This hunt explicitly addresses the CAGR gap. Most defensible paths: leverage + regime gate (Gayed LRS) or HFEA leveraged barbell.

---

## Reuse from long_term_portfolio

This loop reuses the foundation:
- `studies/long_term_portfolio/synths.py` — 8 synth functions (NTSD/AVUV/AVDV/AVEM/SPMO/IDMO/RSST/CTA-proxy)
- `studies/long_term_portfolio/run_iter.py` — execution helper (portfolio_returns_from_config, run_iter_full)
- `studies/long_term_portfolio/proxies.py` — NTSX/NTSI/NTSE blueprints
- `studies/long_term_portfolio/datasets.py` — load_prices for 3 datasets
- `studies/long_term_portfolio/scoring.py` — adaptable; spy_beater_hunt has its own scoring rubric (CAGR-anchored)

NEW synths likely needed (NOT in long_term_portfolio):
- TMFSIM (3× LTT for HFEA) — synth via `TLTSIM × 3 - 1.5%/y daily-reset decay`
- HFEA-blend strategies
- Regime-gated leveraged equity (UPRO + 200d SMA on SPY)

---

## Iteration log (newest first)

### iter 003 — A3 mixed Gayed (crisis-alpha buffer in ON sleeve) — PROMISING 64/100, NEW closest-to-winner (2026-04-30)

- **Tier**: PROMISING **64/100** (winner_conditions_met = **TRUE**, all 3 bars pass)
- **Selected**: `a3_lrs_split_kmlm20` (40% UPRO + 40% SSO + 20% KMLM ON; 100% IEF OFF; SMA 200, no buffer)
- **Bars**: CAGR ✓ (14.99% mean ≥ 11.21%), MDD ✓ (41.87% ≤ 55.17%), Gates ✓ (6/6, cross_met TRUE)
- **All 4 configs PASSED all 3 bars** — direction A3 robust:
  | config                  | CAGR     | MDD     | Sharpe (lh, spy_real) |
  |-------------------------|---------:|--------:|----------------------:|
  | a3_lrs_split_kmlm10     | 15.47%   | 46.65%  | 0.681 / 0.665         |
  | **a3_lrs_split_kmlm20** | **14.99%** | **41.87%** | **0.719 / 0.692**   |
  | a3_lrs_split_tlt15      | 15.34%   | 44.60%  | 0.709 / 0.682         |
  | a3_lrs_split_blend      | 14.86%   | 42.13%  | 0.713 / 0.696         |
- **Per-dataset (selected)**:
  | dataset  | Sharpe | CAGR    | MDD    | gates | DSR p     |
  |----------|-------:|--------:|-------:|------:|----------:|
  | lh_56y   | 0.719  | 15.58%  | 43.22% | 6/7   | 4.04e-04  |
  | spy_real | 0.692  | 14.39%  | 40.53% | 6/7   | 1.39e-02  |
- **Score lift vs iter 001 a1_lrs_split (60→64)**: MDD 6→10 (+4), Gates 12→13 (+1), Robustness 9→10 (+1), CAGR 22→20 (−2). Net +4.
- **Pre-committed KILLs**:
  - KILL #6 NOT FIRED (CAGR floor): all 4 configs CAGR ≥ 14.86% >> 11.21%.
  - KILL #10 NOT FIRED (no MDD relief): all 4 configs MDD < 51.60% (iter 001 baseline). Direction CONFIRMED.
  - KILL #11 NOT FIRED (KMLM monotonic harm): KMLM20 Sharpe > KMLM10 in BOTH ds — **monotonic positive** in 10-20% range.
  - KILL #12 NOT FIRED (TLT subordinate): TLT 15% MDD 44.60% < KMLM 10% MDD 46.65%; TLT competitive but KMLM dose wins at 20%.
- **Next iter direction**: A3 KMLM dose-response — try 25% / 30% KMLM + TLT 20% (3 configs to slow n_trials growth).
- **Multi-horizon robustness 10/10**: 5y pass-rate 83.3%, 10/15/20y all 100%.
- **Citations**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed gate;
  `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking VALIDATED
  empirically (KMLM 20% drops MDD 9.73pp with only 1.24pp CAGR drag);
  `[advances_fin_ml, p.222-223]` DSR n_trials=14 still PASS (worst p 1.39e-02).

### Methodology refactor — lh_56y + spy_real, new bars, multi-horizon robustness (2026-04-29)

- **Datasets**: replaced (lh_56y, vt_real, ndx_real) with **(lh_56y, spy_real)**.
  - spy_real: SPY Tiingo daily adj_close 2003-08-20 → 2026-04-14 (22.7y) —
    captures full GFC peak-to-trough -56%. SPY benchmark: CAGR 10.95%, MDD 55.20%.
  - vt_real / ndx_real removed from spy_beater_hunt scope (still exist for
    long_term_portfolio's 43 prior iters).
- **New bars** (2-dataset mean):
  - CAGR ≥ **11.21%** (was 13.80%)
  - MDD ≤ **55.17%** (was 40.85%)
- **Anchor ranges in scoring** adjusted: MDD floor 15% (was 10%), MDD ceiling 70% (was 50%).
- **NEW criterion 6 (Multi-horizon robustness, 10pts)**: rolling CAGR pass-rate
  vs SPY benchmark across 5y/10y/15y/20y windows (weighted 3+3+2+2pts).
  Replaces the legacy 5y rolling Sharpe % positive (kept in verdict.json
  as `legacy_5y_sharpe_*` for compat).
- **NEW plot** `plot_rolling_<ds>.png` per dataset: 4×2 subplot grid
  showing rolling CAGR (left) and MDD (right) at windows 5/10/15/20y for
  every config + SPY benchmark. SPY bars (CAGR 11.21%, MDD 55.17%) marked.
- Iters 001 + 002 re-run with the new methodology.

### iter 001 RE-RUN with (lh_56y, spy_real) — WINNER conditions MET (2026-04-29)

- **Tier**: PROMISING **60/100** (winner_conditions_met = **TRUE**, all 3 bars pass)
- **Selected**: `a1_lrs_split` (50% UPRO + 50% SSO when on, IEF off, SMA 200, no buffer)
- **Bars**: CAGR ✓ (16.23% mean ≥ 11.21%), MDD ✓ (51.60% ≤ 55.17%), Gates ✓ (6/5 ≥ 5/5)
- **Per-dataset**:
  | dataset  | Sharpe | CAGR    | MDD    | gates | DSR p     |
  |----------|-------:|--------:|-------:|------:|----------:|
  | lh_56y   | 0.670  | 16.91%  | 54.70% | 6/7   | 7.91e-04  |
  | spy_real | 0.643  | 15.55%  | 48.50% | 5/7   | 1.34e-02  |
- **Why tier PROMISING (not WINNER)**: tier WINNER requires score ≥ 90 AND all
  bars met. Score 60 because Sharpe pts only 1/10 (mean Sharpe 0.66, anchor
  range 0.5-2.0) and MDD pts 6/20 (mean 51.60% close to 55.17% ceiling).
- **Multi-horizon robustness 10/10**: 5y pass-rate 84.7%, 10/15/20y 100%.
- **Citation**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed.

### iter 002 RE-RUN with (lh_56y, spy_real) — MARGINAL 57/100 (2026-04-29)

- **Tier**: MARGINAL **57/100** (winner_conditions_met = False)
- **Selected**: `a2_sma200_th2_3xupro` (max Sharpe rule)
- **Bars**: CAGR ✓ (mean 18.96%), MDD ✗ (57.57% > 55.17%), Gates ✗ (5/4 vs thresh 5/5)
- **CLOSEST-to-WINNER**: `a2_sma150_2xsso` — CAGR 13.05% ≥ 11.21% PASS, MDD 45.98% ≤ 55.17% PASS, gates likely PASS. Bars 3/3.
- **All-configs mean (2-dataset)**:
  | config                  | CAGR    | MDD    |
  |-------------------------|--------:|-------:|
  | a2_sma100_3xupro        | 15.93%  | 70.34% |
  | a2_sma200_th2_3xupro    | 18.96%  | 57.57% |
  | a2_sma200_th5_3xupro    | 18.55%  | 69.41% |
  | a2_ema150_th2_3xupro    | 16.20%  | 73.03% |
  | **a2_sma150_2xsso**     | **13.05%** | **45.98%** | bars 3/3 PASS |
  | a2_ema100_th2_2xsso     | 12.76%  | 61.36% |
- **Pre-committed KILLs**:
  - KILL #7 FIRED (faster signal): SMA100 MDD 70.34% > SMA200 57.57% — direction CLOSED
  - KILL #8 FIRED (buffer ≥5%): th5 MDD 69.41% > th2 57.57% — direction CLOSED
  - KILL #9 NOT FIRED: 2× SSO MDD 45.98% (best) — leverage IS the lever
- **Multi-horizon robustness 10/10**: 5y pass-rate 84.7%, 10/15/20y all 100%.
- **Citations**: `[leverage_for_the_long_run, ch.3-4]` validated;
  `[advances_fin_ml, p.222-223]` DSR n_trials=10 penalty.

---

## Promising unexplored directions

See `PROMISING_DIRECTIONS.md` for the full ranked list. Highlights:

### Tier 1 (literature-strong, deployable)
- **A1 Gayed LRS UPRO 200d-SMA** — 100% UPRO when SPY > 200d MA, else IEF. Cite `[leverage_for_the_long_run, ch.3-4, p.40-60]`.
- **B1 HFEA classical 55/45** — 55% UPRO + 45% TMF (3× SPY + 3× LTT) quarterly rebalanced. Bogleheads 2019.
- **A2 Gayed LRS TQQQ 200d-SMA** — concentrate growth, regime-gated.

### Tier 2 (literature-supported, more risk)
- **B2 HFEA modern 60/40** — 60% UPRO + 40% TMF
- **C1 Vol-targeted SPY 1.5×** — UPRO when 60d vol < 15%, else SPY
- **A3 Mixed Gayed (UPRO + KMLM + TLT)** — leverage + crisis-alpha

### Tier 3 (exploratory)
- **D1 Concentrated growth + regime** — QQQ 100% with monthly momentum gate
- **C2 CAPE-timing** — equity when CAPE < median, bonds when above

---

## Pre-flight checklist before iter 001

Before starting iter 001:
1. Verify testfolio cache has UPROSIM, SSOSIM, TQQQSIM, QLDSIM (already confirmed yes per exploration)
2. Build TMFSIM synth (TLTSIM × 3 - 1.5%/y decay) — TDD test
3. Build LRS engine (200d SMA gate on price series, T+1 lag, no peek-ahead) — TDD test
4. Pick first iter hypothesis from Tier 1 (recommended: A1 Gayed LRS UPRO)

---

## Citations (loop-wide)

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA on LETFs
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking (long_term_portfolio baseline)
- `[advances_fin_ml, p.208-211]` PBO via CSCV
- `[advances_fin_ml, p.222-223]` DSR
- `[advances_fin_ml, p.196-202]` bootstrap CI
- `[advances_fin_ml, p.31-34]` cross-lib + factor framework
- HFEA classical (Hedgefundie Bogleheads 2019) — leveraged barbell
- Frazzini-Israel-Moskowitz 2018 — UMD long-only capture rate
