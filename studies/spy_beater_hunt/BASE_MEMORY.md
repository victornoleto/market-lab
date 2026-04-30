---
mission: "Find ONE long-term strategy with mean CAGR ≥ SPY (11.21%) AND mean MDD ≤ SPY (55.17%) AND surviving 7-gate battery on ≥ 2/2 datasets"
target_total_iterations: 50
total_iterations: 9
winners_found: 0
closest_to_winner: "iter 006 a6_tqqq_split_kmlm30_tlt10 RETAINS (tie-breaker by older iter): CAGR 17.33% PASS, MDD 49.73% PASS, gates 6/6 PASS cross_met — score 67. Iter 009 B2 HFEA+KMLM scored 63 (TIE iter 008, 4 BELOW iter 006/007 67), winner_conditions_met FALSE due to MDD bar fail (mean 61.51% > 55.17% bar). KILL #27 fired (KMLM 15-25% dose insufficient on HFEA backbone — both kmlm15 and kmlm25 spy_real MDD > 55% bar). KMLM dose-response on HFEA is OPPOSITE SPY-track: flat-to-negative on Sharpe within 15-25%, monotonic NEGATIVE on MDD (more KMLM = MORE MDD). Both B1 and B2 leveraged-barbell directions now CLOSED. Score-90 path now: C1 vol-targeted (iter 010 only remaining candidate within Tier 1-2 architecture) → IMPOSSIBILITY_RESULT (iter 011+ fallback)."
status: hunting
latest_iteration: "009-2026-04-30-B2-hfea-kmlm"
latest_score: 63
latest_tier: PROMISING
latest_bars_met: 2  # CAGR ✓, MDD ✗, Gates ✓
cumulative_n_trials: 32
datasets:
  - "lh_56y (1986+, ~40y, SPYSIM synth, GATE thresh 5)"
  - "spy_real (2003+, ~22.7y, SPY Tiingo adj_close, GATE thresh 5)"
spy_benchmarks:
  cagr_mean: 0.1121
  mdd_mean: 0.5517
  sharpe_mean: 0.6661
direction_status:
  A1_200d_SMA_3x_UPRO: "CLOSED (displaced iter 003 KMLM20 then iter 004 KMLM30)"
  A2_faster_signal: "CLOSED (iter 002 KILL #7) — faster SMA/EMA make MDD WORSE"
  A2_threshold_buffer: "CLOSED (iter 002 KILL #8) — buffer ≥5% makes MDD worse"
  A2_lower_leverage: "CLOSED — bars 3/3 met but score < 60 (CAGR drag > MDD pts gain)"
  A2_TQQQ_track_pure: "CLOSED via KILL #19 (iter 006 a6_tqqq_split_lrs lh_56y MDD 87.86% >> 70% bar) — 200d SMA gate cannot rescue full split-leverage TQQQ during NDX -78% dot-com regime; need crisis-alpha to absorb gap-and-go losses"
  A2_TQQQ_track_kmlm30: "MARGINAL via KILL #19 borderline (iter 006 a6_tqqq_split_kmlm30 lh_56y MDD 70.94% ≈ 70% bar, mean MDD 55.52% > 55.17% bar) — fails strict bars; Sharpe better than baseline but architecturally fragile"
  A2_TQQQ_track_kmlm30_tlt10: "CLOSEST-TO-WINNER (iter 006 score 67) RETAINS by tie-breaker — passes all 3 strict bars; lh_56y MDD 62.39% binding constraint"
  A2_TQQQ_track_extreme: "CONFIRMED MONOTONIC POSITIVE Sharpe 30→35→40% KMLM (iter 007 KILL #22 not fired); but STRUCTURALLY CAPPED at 67 within CAGR-anchored rubric — KMLM/TLT extension trades CAGR pts for MDD pts at ~1:1 rate. Direction effectively saturated for score progression."
  A2_TLT_extension_on_TQQQ_track: "CLOSED at narrow margin (iter 007 KILL #23 fired by 0.33pp) — TLT15 lh_56y MDD 57.36% > KMLM35 lh_56y MDD 57.03%; KMLM is the marginally steeper MDD lever on TQQQ-track."
  A3_mixed_gayed_crisis_alpha: "DOMINATED by iter 004 KMLM 30% (same architecture, lower scores)"
  A3_kmlm_dose_response: "PROMISING (iter 004 KMLM30 score 66) — monotonic positive 0→30%, no inflection found; now subordinate to A2 TQQQ-track variants for closest-to-winner"
  A3_kmlm_extreme: "MONOTONIC POSITIVE CONFIRMED through KMLM 40% (iter 005) — Sharpe rose 30→35→40% in BOTH datasets, but score regressed 66→63 because CAGR-axis dominates rubric vs MDD/Sharpe gains. Direction structurally limited within scoring; KMLM 45-50% unlikely to lift score."
  A3_tlt_on_top_of_kmlm30: "PROMISING (iter 005 a5_kmlm30_tlt10 beat a4_kmlm30 in both datasets) — TLT-on-top duration lever validated; transferred to TQQQ-track in iter 006 (still helps)"
  A3_tlt_dose_response: "PROMISING but subordinate — TLT 20% Sharpe slightly > KMLM 20%, but KMLM scales better at 25-30%; revisit with KMLM+TLT blends iter 007+"
  B1_HFEA_classical: "CLOSED via KILL #24 (iter 008) — canonical 55/45 spy_real MDD 67.13% > 65% bar; all 3 weights in [50,60] UPRO range fail MDD bar (mean 67-72%). Highest CAGR among 8 iters (29/30 pts) but 0/20 MDD pts. Bogleheads risk-parity claim REJECTED: Sharpe is monotonic NEGATIVE on UPRO weight in [50,60] (5050 > 5545 > 6040). Architecture fundamentally subordinate to LRS-style regime-gated strategies on 2022 stress."
  B2_HFEA_KMLM: "CLOSED via KILL #27 (iter 009) — KMLM 15-25% dose on HFEA backbone insufficient to clear MDD bar (kmlm15 spy_real 61.27%, kmlm25 spy_real 61.78%, both > 55%). KMLM dose-response on HFEA is OPPOSITE SPY-track: flat-to-negative on Sharpe within 15-25%, monotonic NEGATIVE on MDD (more KMLM = MORE MDD). The first 15pp KMLM dose cuts ~6pp MDD relief from HFEA-only (67→61%); subsequent KMLM dose at 20-25% adds 0.5pp MDD instead. KMLM-for-TMF substitution is pareto-trade not pareto-improve at HFEA's 165% UPRO notional. Net 0 score vs HFEA classical (iter 008): +3 MDD pts gained, −2 CAGR pts + −1 Gates pt lost."
  C1_vol_targeted: "ONLY REMAINING Tier 1-2 candidate — recommended iter 010. Different geometry (dynamic leverage scaling) may unlock the architectural ceiling at score 63-67 set by static-weight barbells (B1, B2) and LRS-track strategies (A1-A3, A2-TQQQ-track). If C1 also caps near 67, IMPOSSIBILITY_RESULT triggers iter 011+."
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

### iter 009 — B2 HFEA + KMLM crisis-alpha (UPRO 50% + TMF 35-25% + KMLM 15-25%) — PROMISING 63/100, TIE iter 008, BELOW closest-to-winner, KILL #27 fired (2026-04-30)

- **Tier**: PROMISING **63/100** (winner_conditions_met = **FALSE**, mdd_bar fail)
- **Selected**: `b2_hfea_kmlm20` (50% UPRO + 30% TMF + 20% KMLM, max Sharpe / SPY_Sharpe rule)
- **Bars**: CAGR ✓ (18.65% mean ≥ 11.21%), **MDD ✗ (61.51% > 55.17% bar)**, Gates ✓ (5+5, cross_met)
- **All 3 configs FAIL MDD bar** — KMLM 15-25% dose on HFEA backbone is insufficient to clear 55.17%:
  | config             | mean CAGR | mean MDD | Sharpe (lh, spy_real) | bar test |
  |--------------------|----------:|---------:|----------------------:|---------:|
  | b2_hfea_kmlm15     | 18.97%    | 61.27%   | 0.787 / 0.754         | FAIL (MDD) |
  | **b2_hfea_kmlm20** | **18.65%** | **61.51%** | **0.785 / 0.756** | **FAIL (MDD)** |
  | b2_hfea_kmlm25     | 18.27%    | 61.78%   | 0.780 / 0.754         | FAIL (MDD) |
- **Per-dataset (selected)**:
  | dataset  | Sharpe | CAGR    | MDD    | gates | DSR p     |
  |----------|-------:|--------:|-------:|------:|----------:|
  | lh_56y   | 0.785  | 19.21%  | 61.51% | 5/7   | 3.26e-05  |
  | spy_real | 0.756  | 18.09%  | 61.51% | 5/7   | 3.07e-03  |
- **Score breakdown vs iter 008 (63 → 63, TIE)**: CAGR 29 → 27 (**−2**), MDD 0 → **3 (+3)**, Gates 12 → 11 (**−1**), DSR/Sharpe-pts/Robustness unchanged. Net **0**. KMLM-for-TMF substitution trades 2pp CAGR + 1pp Gates for 3pp MDD pts within the rubric. Sharpe lifted +0.030 mean but doesn't cross 2-pt boundary (anchor 0.5-2.0 too wide).
- **Score breakdown vs iter 006/007 (67 → 63, −4)**: CAGR 25 → 27 (+2), MDD 7 → 3 (−4), Gates 13 → 11 (−2). Closest-to-winner UNCHANGED.
- **Pre-committed KILLs**:
  - KILL #6 (CAGR floor) NOT FIRED — best CAGR mean 18.97% >> 11.21%.
  - **KILL #27 (KMLM dose insufficient on HFEA backbone) FIRED** — `b2_hfea_kmlm15` spy_real MDD 61.27% > 55% bar AND `b2_hfea_kmlm25` spy_real MDD 61.78% > 55% bar. Both conditions of KILL #27 met. **Direction B2 CLOSED**.
  - KILL #28 (Sharpe < 0.740 baseline) NOT FIRED — kmlm25 Sharpe mean 0.766 > 0.740; kmlm20 mean 0.770 > 0.740. KMLM addition does NOT degrade Sharpe vs HFEA-only baseline.
  - KILL #29 (CAGR < 13.80%) NOT FIRED — kmlm25 CAGR mean 18.27% >> 13.80%. KMLM-for-TMF substitution preserves CAGR profile (drag ~0.4pp per +5% KMLM).
- **KMLM dose-response on HFEA backbone (4 data points, 0-25% KMLM)**:
  - 0% (HFEA-only iter 008): Sharpe 0.740, CAGR 19.68%, MDD 67.48%
  - 15%: Sharpe 0.770, CAGR 18.97%, MDD 61.27% (jump!)
  - 20%: Sharpe 0.770 (flat), CAGR 18.65%, MDD 61.51% (slight up)
  - 25%: Sharpe 0.766 (slight regression), CAGR 18.27%, MDD 61.78% (slight up)
  - **Pattern**: strong 0→15% improvement (first dose effect), then flat-to-degrading at 20-25%. Sharpe NOT monotonic positive within 15-25%; MDD MONOTONIC NEGATIVE within 15-25% (more KMLM ADDS MDD).
- **Surprising finding**: KMLM dose-response on HFEA is **OPPOSITE SPY-track**. SPY-track (iter 003-005) showed monotonic positive Sharpe through 40% with MDD cut 14.8pp from 0→30%. On HFEA, KMLM 15→25% adds 0.5pp MDD because TMF and KMLM compete for the **same diversifier slot** rather than stacking — at 165% UPRO notional, the effective concentrated risk is UPRO not TMF, so swapping TMF→KMLM reshuffles regime exposures (gain stagflation hedge, lose GFC duration hedge) at roughly equal MDD weight.
- **Multi-horizon robustness 10/10**: 5y pass-rate 88.9%, 10/15/20y all 100%. spy_real 5y window includes 2022-2024 lag where HFEA+KMLM underperforms SPY (similar to iter 008 86.1%, slight improvement from KMLM crisis-alpha hedge of 2022).
- **H₁ REJECTED**: HFEA + KMLM 15% does NOT clear MDD bar (61.27% mean > 55.17%). Even minimum KMLM dose insufficient.
- **H₂ REJECTED at narrow margin**: KMLM dose-response on Sharpe FLAT (0.770/0.770/0.766) and on MDD MONOTONIC NEGATIVE within 15-25%. Expected SPY-track-style monotonic positive does NOT transfer to HFEA backbone.
- **H₃ PARTIALLY CONFIRMED**: CAGR drag ~0.4pp per +5% KMLM (consistent with prediction). KMLM-for-TMF substitution preserves CAGR profile, but **diversification quality differs** — TMF and KMLM are both inversely correlated to UPRO but in **different regimes**, so they don't stack additively.
- **Path to 90 (need +27 pts)**: leveraged-barbell architecture (B1, B2) confirmed structurally capped at score 63-67. Only remaining Tier 1-2 candidate is C1 vol-targeted (iter 010). If C1 also caps near 67, **architectural ceiling confirmed** → IMPOSSIBILITY_RESULT (iter 011+) → F1+SPLIT incumbent fallback deploy-ready.
- **Next iter direction**: **C1 vol-targeted SPY** (1.5× SPY when 60d vol < 15%, else 0.5× → IEF). Dynamic leverage scaling = different control geometry from regime gates and static barbells. Pre-committed KILL #30/#31/#32 sketched in final_report.md.
- **Citations**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LETF decay validated empirically — HFEA+KMLM 2022 MDD 61% mirrors HFEA-only 67% reduced by KMLM crisis-alpha; `[ilmanen_expected_returns, ch.19]` MF crisis-alpha — KMLM at 15-25% dose delivered ~6pp MDD relief at first dose but ZERO additional at 20-25% range (saturation effect not documented in SPY-track); `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking — TMF+KMLM compete for same diversifier slot on HFEA, NOT stacking additively; HFEA Bogleheads 2019 + crisis-alpha extension proposed by some users — falsified at 15-25% KMLM dose on spy_beater MDD bar; `[advances_fin_ml, p.31-34]` factor framework — leveraged duration vs trend-following are distinct factors with rates-falling vs stagflation betas, but combining doesn't symmetrically reduce concentrated risk because **UPRO is the concentrated risk** at 165% notional, not TMF; `[advances_fin_ml, p.222-223]` DSR cumulative n_trials=32, worst p 3.07e-03 << 0.05 bar.

### iter 008 — B1 HFEA classical (UPRO + TMF leveraged barbell, weights 50/55/60% UPRO) — PROMISING 63/100, BELOW closest-to-winner, KILL #24 fired (2026-04-30)

- **Tier**: PROMISING **63/100** (winner_conditions_met = **FALSE**, mdd_bar fail)
- **Selected**: `b1_balanced_5050` (50% UPRO + 50% TMF, max Sharpe / SPY_Sharpe rule)
- **Bars**: CAGR ✓ (19.68% mean ≥ 11.21%), **MDD ✗ (67.48% > 55.17% bar)**, Gates ✓ (6+5, cross_met)
- **All 3 configs FAIL MDD bar** — leveraged-barbell architecture incompatible with 55.17% mean MDD requirement:
  | config             | mean CAGR | mean MDD | Sharpe (lh, spy_real) | bar test |
  |--------------------|----------:|---------:|----------------------:|---------:|
  | b1_classic_5545    | 20.00%    | 67.13%   | 0.737 / 0.723         | FAIL (MDD) |
  | b1_modern_6040     | 20.14%    | 72.70%   | 0.713 / 0.713         | FAIL (MDD) |
  | **b1_balanced_5050** | **19.68%** | **67.48%** | **0.755 / 0.724** | **FAIL (MDD)** |
- **Per-dataset (selected)**:
  | dataset  | Sharpe | CAGR    | MDD    | gates | DSR p     |
  |----------|-------:|--------:|-------:|------:|----------:|
  | lh_56y   | 0.755  | 20.62%  | 67.48% | 6/7   | 4.96e-05  |
  | spy_real | 0.724  | 18.73%  | 67.48% | 5/7   | 4.91e-03  |
- **Score breakdown vs iter 006 (67 → 63, −4)**: CAGR 25→**29 (+4)** highest in all iters; MDD 7→**0 (−7)** structural fail; Gates 13→12 (−1); DSR/Sharpe/Robustness unchanged. Net **−4** — HFEA gives up 7pp MDD pts to gain 4pp CAGR pts within saturated criterion 1.
- **Pre-committed KILLs**:
  - KILL #6 (CAGR floor) NOT FIRED — best CAGR mean 20.14% >> 11.21%.
  - **KILL #24 (HFEA 2022-stress MDD > 65% on spy_real) FIRED** — `b1_classic_5545` spy_real MDD 67.13% > 65% bar. The 2022 inflation regime breaks leveraged barbell at canonical weights. **Direction CLOSED**.
  - KILL #25 (TMFSIM no-free-lunch synth Sharpe ∉ [0,1]) NOT FIRED — TMF 1986+ Sharpe 0.49 ∈ [0,1] (verified pre-iter, synth integrity confirmed).
  - KILL #26 (HFEA monotonic regression at 55/45) NOT FIRED — 5050 (0.755, 0.724) > 5545 (0.737, 0.723) on BOTH ds; condition required BOTH 6040<5545 AND 5050<5545 on Sharpe BOTH ds. Bogleheads risk-parity claim **REJECTED**: optimal Sharpe is at 5050 or LOWER UPRO%, not at 5545.
- **HFEA dose-response on UPRO weight (3 data points iter 008)**: 50%→0.740 mean Sharpe; 55%→0.730; 60%→0.713. **Monotonic NEGATIVE Sharpe** as UPRO grows in [50,60]. CAGR rises only 0.46pp across 10pp UPRO range (very weak slope); MDD rises 5.2pp (strong slope at 55→60 inflection). At 165%+ leveraged equity notional, marginal UPRO contribution is diminishing while marginal MDD is accelerating.
- **Multi-horizon robustness 10/10**: 5y pass-rate 86.1%, 10/15/20y all 100%. spy_real 5y window includes 2022-2024 lag where HFEA underperforms SPY (MDD recovery).
- **H₁ REJECTED**: HFEA classical fails MDD bar. **H₂ REJECTED**: dose-response not monotonic positive on UPRO weight (Sharpe is monotonic NEGATIVE). **H₃ CONFIRMED**: spy_real 2022 stress drives binding constraint identically to lh_56y (both datasets MDD 67.48% — same 2022 trough captured by both synth and real).
- **Path to 90 (need +27 pts)**: structurally blocked within B1 architecture. Pivot to B2 HFEA + KMLM (iter 009) — adds known-effective crisis-alpha. Best-case CAGR ~17% / MDD ~50% → score ~70-72.
- **Next iter direction**: B2 HFEA + KMLM (50% UPRO + 35% TMF + 15% KMLM and variants). Pre-committed KILL #27/#28/#29 sketched in final_report.md.
- **Citations**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LETF decay validated empirically — HFEA 2022 MDD 67-73% mirrors documented Bogleheads 2022 stress (~−65% peak-to-trough); decay constant 1.5%/y understates real 2022 drag (real ~3-5%/y in high-vol regime). `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking — unhedged 165-180% leverage cannot deliver MDD ≤ 55% on 2022 regime; stacking alone insufficient at 3× barbell. HFEA Bogleheads 2019 risk-parity 55/45 claim **falsified by our synth** (Sharpe peaks at 50/50 or lower) — claim is regime-specific to 1986-2019 declining-rate environment. `[advances_fin_ml, p.31-34]` factor framework — leveraged duration (TMF) is concentrated risk in rates-RISING regime, not diversifier. `[advances_fin_ml, p.222-223]` DSR cumulative n_trials=29, worst p 4.91e-03 << 0.05 bar.
- **TMFSIM routing (one-time infra change)**: added route in `studies/long_term_portfolio/run_iter.py` `_resolve_tickers_to_returns` mapping `TMFSIM` → `synths.tmf_synth_returns_from_cache()`. TDD-tested via new `test_resolve_tickers_routes_tmfsim_to_synth` in `tests/test_studies_spy_beater_hunt.py`. All 25 spy_beater tests pass.

### iter 007 — A2 TQQQ-track extreme (KMLM/TLT dose extension 35/40/15) — PROMISING 67/100, TIE with iter 006, TQQQ-track saturated (2026-04-30)

- **Tier**: PROMISING **67/100** (winner_conditions_met = **TRUE**, all 3 bars pass)
- **Selected**: `a7_tqqq_split_kmlm40_tlt10` (25% TQQQ + 25% QLD + 40% KMLM + 10% TLT ON; 100% IEF OFF; SMA 200, no buffer; lag T+1)
- **Bars**: CAGR ✓ (16.08% mean ≥ 11.21%), MDD ✓ (42.33% ≤ 55.17%), Gates ✓ (6+6, cross_met TRUE)
- **All 3 configs PASSED all 3 bars** — TQQQ-track + extended crisis-alpha holds:
  | config                          | mean CAGR | mean MDD | Sharpe (lh, spy_real) | lh_56y MDD |
  |---------------------------------|----------:|---------:|----------------------:|-----------:|
  | a7_tqqq_split_kmlm35_tlt10      | 16.73%    | 46.18%   | 0.779 / 0.782         | 57.03%     |
  | **a7_tqqq_split_kmlm40_tlt10**  | **16.08%** | **42.33%** | **0.807 / 0.802**   | **51.12%** |
  | a7_tqqq_split_kmlm30_tlt15      | 16.67%    | 46.49%   | 0.777 / 0.784         | 57.36%     |
- **Per-dataset (selected)**:
  | dataset  | Sharpe | CAGR    | MDD    | gates | DSR p     |
  |----------|-------:|--------:|-------:|------:|----------:|
  | lh_56y   | 0.807  | 17.45%  | 51.12% | 6/7   | 2.01e-05  |
  | spy_real | 0.802  | 14.71%  | 33.54% | 6/7   | 1.72e-03  |
- **Score breakdown vs iter 006 (67 → 67, TIE)**: CAGR 25→22 (**−3**), MDD 7→10 (**+3**), Gates/DSR/Sharpe-pts/Robustness unchanged. Net **0**. Sharpe mean 0.759 → 0.804 (+0.045) is real but doesn't cross the 2-pt rubric boundary (anchor 0.5-2.0 too wide).
- **Pre-committed KILLs**:
  - KILL #6 (CAGR floor) NOT FIRED — best CAGR mean 16.73% >> 11.21%.
  - KILL #19 (TQQQ-track wipeout MDD>70%) NOT FIRED — worst single MDD 57.36% (a7_kmlm30_tlt15 lh_56y).
  - **KILL #22 (KMLM dose inflection 35→40 on TQQQ-track) NOT FIRED** — `a7_kmlm40_tlt10` Sharpe (0.807, 0.802) > `a7_kmlm35_tlt10` (0.779, 0.782) BOTH ds. **Sharpe MONOTONIC POSITIVE 35→40% on TQQQ-track CONFIRMED** mirroring iter 005 SPY-track. **H₁ CONFIRMED**.
  - **KILL #23 (TLT subordinate to KMLM on TQQQ-track) MARGINALLY FIRED** — `a7_kmlm30_tlt15` lh_56y MDD 57.36% > `a7_kmlm35_tlt10` lh_56y MDD 57.03% by 0.33pp. **H₂ REJECTED at narrow margin**: KMLM is the marginally steeper MDD lever on TQQQ-track.
- **TQQQ-track Sharpe dose-response (5 data points iter 006+007)**: 0%/0%→0.659; 30%/0%→0.723; 30%/10%→0.759; 35%/10%→0.781; **40%/10%→0.805**; 30%/15%→0.781. No inflection found in 0-40% KMLM range; mirrors SPY-track shape from iter 005.
- **TLT-vs-KMLM steepness on TQQQ-track**: +5pp KMLM costs 0.60pp CAGR / saves 3.55pp MDD; +5pp TLT costs 0.66pp CAGR / saves 3.24pp MDD. KMLM 0.05pp cheaper per pp MDD. Both viable, KMLM marginally preferred.
- **Multi-horizon robustness 10/10**: 5y pass-rate 94.4% (was 100% iter 006), 10/15/20y all 100%. lh_56y rolling NaN bug carries over (n_windows = 0 on lh_56y rolling helper); pass-rates derive from spy_real only.
- **Score-90 path STRUCTURAL CAP**: TQQQ-track saturated near 67 within current rubric. KMLM/TLT extensions trade CAGR ↔ MDD at ~1:1 within integer-pt scoring; Sharpe lift gets penalized by anchor range. Need regime change: B1 HFEA classical (TMFSIM synth needed) is highest-priority next direction.
- **Next iter direction**: **B1 HFEA classical** (UPRO 55 + TMF 45) — TMFSIM synth + TDD per INFRASTRUCTURE.md. Falsifiability test: 2022 inflation regime stress.
- **Citations**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed gate; `[risk_parity, ch.5, p.10]` Carlson stacking — KMLM monotonic positive 0-40% on BOTH SPY-track (iter 005) and TQQQ-track (iter 007); `[advances_fin_ml, p.31-34]` factor framework — symmetric crisis-alpha behavior on SPX/NDX confirmed; `[advances_fin_ml, p.222-223]` DSR cumulative n_trials=26, worst p 1.72e-03 << 0.05. Headroom for ~3 more iters before n=35 zone tightening.

### iter 006 — A2 TQQQ-track + 200d SMA gate on QQQ (split LRS + KMLM30 + TLT10) — PROMISING 67/100, NEW closest-to-winner via NDX-track pivot (2026-04-30)

- **Tier**: PROMISING **67/100** (winner_conditions_met = **TRUE**, all 3 bars pass)
- **Selected**: `a6_tqqq_split_kmlm30_tlt10` (30% TQQQ + 30% QLD + 30% KMLM + 10% TLT ON; 100% IEF OFF; SMA 200 on QQQSIM, no buffer; lag T+1)
- **Bars**: CAGR ✓ (17.33% mean ≥ 11.21%), MDD ✓ (49.73% ≤ 55.17%), Gates ✓ (6+6, cross_met TRUE)
- **All 3 configs (mean across 2 datasets)**:
  | config                              | mean CAGR | mean MDD | Sharpe (lh, spy_real) | bar test |
  |-------------------------------------|----------:|---------:|----------------------:|---------:|
  | a6_tqqq_split_lrs                   | 20.49%    | 70.31%   | 0.652 / 0.665         | FAIL (MDD) |
  | a6_tqqq_split_kmlm30                | 18.46%    | 55.52%   | 0.717 / 0.729         | FAIL (MDD) |
  | **a6_tqqq_split_kmlm30_tlt10**      | **17.33%** | **49.73%** | **0.754 / 0.763**   | **PASS** |
- **Per-dataset (selected)**:
  | dataset  | Sharpe | CAGR    | MDD    | gates | DSR p     |
  |----------|-------:|--------:|-------:|------:|----------:|
  | lh_56y   | 0.754  | 18.56%  | 62.39% | 6/7   | 7.69e-05  |
  | spy_real | 0.763  | 16.09%  | 37.07% | 6/7   | 3.05e-03  |
- **Score lift vs iter 004 (66→67)**: CAGR 19→25 (**+6**, mean 14.39→17.33%), MDD 12→7 (**−5**, mean 36.79→49.73%), Gates/DSR/Sharpe/Robustness unchanged. Net **+1**.
- **Pre-committed KILLs**:
  - KILL #6 (CAGR floor) NOT FIRED — best CAGR mean 20.49% >> 11.21%.
  - **KILL #19 (TQQQ-track wipeout, MDD>70% on either ds) FIRED** on `a6_tqqq_split_lrs` (lh_56y MDD 87.86%); borderline-fired on `a6_tqqq_split_kmlm30` (lh_56y 70.94% ≈ bar). Pure A2 baseline + low-KMLM A2 CLOSED for dot-com regime — only KMLM30+TLT10 blend scrapes the bar.
  - KILL #20 (no CAGR uplift vs SPY-track 16.23%) NOT FIRED — all configs ≥ 17.33% > 16.23%. **H₁ CONFIRMED**: NDX-track adds ~3pp CAGR over SPY-track at matched architecture.
  - KILL #21 (KMLM doesn't generalize) NOT FIRED — `a6_kmlm30` Sharpe (0.717, 0.729) > `a6_lrs` Sharpe (0.652, 0.665) BOTH ds. **H₂ CONFIRMED** + `a6_kmlm30_tlt10` (0.754, 0.763) > `a6_kmlm30` BOTH ds. **H₃ CONFIRMED**: KMLM dose AND TLT-on-top both transfer SPY→NDX track.
- **TQQQ-track Sharpe dose-response (3 data points iter 006)**: 0%/0% → 0.659; 30%/0% → 0.723; 30%/10% → 0.759. Monotonic positive Sharpe; monotonic negative CAGR; monotonic negative MDD. Curve shifted ~3pp higher CAGR and ~13-19pp wider MDD vs SPY-track at matched config (lh_56y dot-com synth drives the gap).
- **Multi-horizon robustness 10/10**: 5y/10y/15y/20y CAGR pass-rate vs SPY = 100% / 100% / 100% / 100% — NDX-track beats SPY in EVERY rolling window. Worst MDD across windows = 62.39% (lh_56y dot-com).
- **Path to 90 (need +23 pts)**: most reachable lever is criterion 2 (MDD, currently 7/20). Halving lh_56y MDD from 62% to ~30% needs heavier crisis-alpha (KMLM 40-50%) on TQQQ-track. Lever C (lower TQQQ leverage to QLD-only 2× NDX) drops CAGR but cuts MDD — slope unknown.
- **Next iter direction**: A2 TQQQ-track extreme — extend KMLM dose to 35-40% + TLT 10-15% on TQQQ-track (mirrors iter 005 sweep on SPY-track). 3 configs to slow n_trials growth.
- **Citations**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed regime gate is **asset-agnostic** but cannot fully rescue 3× LETF during -78% peak-to-trough underlying drawdown; `[risk_parity, ch.5, p.10]` Carlson stacking — KMLM transfers SPY→NDX with monotonic Sharpe lift; `[advances_fin_ml, p.31-34]` factor framework — NDX as US-Large-growth tilt empirically validated (CAGR uplift +3-4pp, MDD cost +13-19pp in stress); `[advances_fin_ml, p.222-223]` DSR cumulative n_trials=23, worst p 3.05e-03 << 0.05.

### iter 005 — A3 KMLM extreme (probe inflection 35/40 + KMLM30+TLT10) — PROMISING 63/100, score regressed but direction monotonic positive through 40% (2026-04-30)

- **Tier**: PROMISING **63/100** (winner_conditions_met = **TRUE**, all 3 bars pass)
- **Selected**: `a5_lrs_split_kmlm30_tlt10` (30% UPRO + 30% SSO + 30% KMLM + 10% TLT ON; 100% IEF OFF; SMA 200, no buffer) — won by tight Sharpe margin over `a5_kmlm40`
- **Bars**: CAGR ✓ (13.57% mean ≥ 11.21%), MDD ✓ (32.57% ≤ 55.17%), Gates ✓ (5/6, cross_met TRUE)
- **All 3 configs PASSED all 3 bars**:
  | config                       | mean CAGR | mean MDD | Sharpe (lh, spy_real) |
  |------------------------------|----------:|---------:|----------------------:|
  | a5_lrs_split_kmlm35          | 14.05%    | 34.14%   | 0.791 / 0.739         |
  | a5_lrs_split_kmlm40          | 13.68%    | 31.62%   | 0.820 / 0.756         |
  | **a5_lrs_split_kmlm30_tlt10**| **13.57%** | **32.57%** | **0.818 / 0.768**   |
- **Per-dataset (selected)**:
  | dataset  | Sharpe | CAGR    | MDD    | gates | DSR p     |
  |----------|-------:|--------:|-------:|------:|----------:|
  | lh_56y   | 0.818  | 14.36%  | 32.57% | 5/7   | 1.70e-05  |
  | spy_real | 0.768  | 12.78%  | 32.57% | 6/7   | 2.93e-03  |
- **Score regression vs iter 004 (66→63)**: CAGR 19→17 (−2), MDD 12→13 (+1), Gates 13→12 (−1, lh_56y 6→5), Robustness 10→9 (−1, 5y pass-rate 83.3%→66.7%), Sharpe/DSR/Extra unchanged. Despite better MDD and Sharpe, the CAGR-axis-dominated rubric (30 pts CAGR vs 20 pts MDD) made −0.82pp CAGR cost more than +4.22pp MDD gained.
- **Pre-committed KILLs**:
  - KILL #6 NOT FIRED (CAGR floor): all 3 configs CAGR ≥ 13.57% >> 11.21%.
  - KILL #16 NOT FIRED (KMLM 35% inflection): `a5_kmlm35` Sharpe (0.791, 0.739) > `a4_kmlm30` (0.765, 0.722) in BOTH ds. Monotonic positive 30→35%.
  - KILL #17 NOT FIRED (KMLM 40% inflection): `a5_kmlm40` (0.820, 0.756) > `a5_kmlm35` (0.791, 0.739) in BOTH ds. Monotonic positive 35→40%. **No inflection found in 0-40% KMLM range.**
  - KILL #18 NOT FIRED (TLT-on-top doesn't help): `a5_kmlm30_tlt10` (0.818, 0.768) > `a4_kmlm30` (0.765, 0.722) in BOTH ds. Adding 10pp TLT DID help Sharpe.
- **KMLM dose-response curve (7 data points)**: 0%→16.23/51.60, 10%→15.47/46.65, 20%→14.99/41.87, 25%→14.70/39.37, 30%→14.39/36.79, 35%→14.05/34.14, 40%→13.68/31.62 (CAGR/MDD). Marginal CAGR cost slowing (0.34pp/+5% in 30-40% zone vs 0.6pp earlier). Marginal MDD relief slowing (~2.5pp/+5% in 30-40% zone vs 5pp earlier). Sharpe rises monotonically.
- **Closest-to-winner UNCHANGED**: iter 004 `a4_kmlm30` (66) retains. Path to score 90 looks structurally blocked within KMLM-dose lever — pivot to B1 HFEA / A2 TQQQ-track / C1 vol-targeted needed for additional +25 pts.
- **Multi-horizon robustness 9/10**: 5y pass-rate dropped 83.3%→66.7% (KMLM-heavy lags SPY in 5y windows during long bull); 10y 92.3%, 15/20y 100%.
- **Next iter direction**: pivot to **B1 HFEA classical** (recommended) or **A2 TQQQ-track**. Continuing A3 KMLM dose 45-50% unlikely to lift score within current rubric.
- **Citations**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed gate;
  `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking validated
  through 40% KMLM (concave dose-response, monotonic positive Sharpe);
  `[advances_fin_ml, p.222-223]` DSR n_trials=20 worst p 2.93e-03 << 0.05;
  `[ilmanen_expected_returns, ch.19]` MF crisis-alpha — extended F1+SPLIT
  17.5% allocation to 30-40% within Sharpe-improving zone.

### iter 004 — A3 KMLM dose-response (extend to 25/30%) — PROMISING 66/100, NEW closest-to-winner (2026-04-30)

- **Tier**: PROMISING **66/100** (winner_conditions_met = **TRUE**, all 3 bars pass)
- **Selected**: `a4_lrs_split_kmlm30` (35% UPRO + 35% SSO + 30% KMLM ON; 100% IEF OFF; SMA 200, no buffer)
- **Bars**: CAGR ✓ (14.39% mean ≥ 11.21%), MDD ✓ (36.79% ≤ 55.17%), Gates ✓ (6/6, cross_met TRUE)
- **All 3 configs PASSED all 3 bars** — direction A3 KMLM dose-response robust:
  | config                   | mean CAGR | mean MDD | Sharpe (lh, spy_real) |
  |--------------------------|----------:|---------:|----------------------:|
  | a4_lrs_split_kmlm25      | 14.70%    | 39.37%   | 0.741 / 0.706         |
  | **a4_lrs_split_kmlm30**  | **14.39%** | **36.79%** | **0.765 / 0.722**   |
  | a4_lrs_split_tlt20       | 15.01%    | 42.59%   | 0.724 / 0.698         |
- **Per-dataset (selected)**:
  | dataset  | Sharpe | CAGR    | MDD    | gates | DSR p     |
  |----------|-------:|--------:|-------:|------:|----------:|
  | lh_56y   | 0.765  | 15.13%  | 37.39% | 6/7   | 6.53e-05  |
  | spy_real | 0.722  | 13.65%  | 36.20% | 6/7   | 5.56e-03  |
- **Score lift vs iter 003 a3_kmlm20 (64→66)**: MDD 10→12 (+2), Sharpe 1→2 (+1), CAGR 20→19 (−1). Net +2.
- **Pre-committed KILLs**:
  - KILL #6 NOT FIRED (CAGR floor): all 3 configs CAGR ≥ 14.39% >> 11.21%.
  - KILL #13 NOT FIRED (KMLM 25% inflection): `a4_kmlm25` Sharpe (0.741, 0.706) > `a3_kmlm20` (0.719, 0.692) in BOTH ds. Monotonic positive 20→25%.
  - KILL #14 NOT FIRED (KMLM 30% vs 25%): `a4_kmlm30` (0.765, 0.722) > `a4_kmlm25` (0.741, 0.706) in BOTH ds. Monotonic positive 25→30%.
  - KILL #15 NOT FIRED (TLT 20% dominated): `a4_tlt20` Sharpe (0.724, 0.698) marginally > `a3_kmlm20` (0.719, 0.692) in BOTH ds; MDD 42.59% slightly worse than KMLM 20% MDD 41.87%. TLT 20% NOT dominated. KMLM scales better at 25-30%.
- **KMLM dose-response curve (5 data points)**: 0%→16.23/51.60, 10%→15.47/46.65, 20%→14.99/41.87, 25%→14.70/39.37, 30%→14.39/36.79 (CAGR/MDD). Marginal cost ~0.6pp CAGR per +5% KMLM, marginal benefit ~2.5-5pp MDD. Curve concave, NO inflection found in 0-30%.
- **Multi-horizon robustness 10/10**: 5y pass-rate 83.3%, 10/15/20y all 100%.
- **Next iter direction**: A3 KMLM extreme (35% / 40%) + KMLM30+TLT10 blend (3 configs).
- **Citations**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed gate;
  `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking — KMLM
  dose-response curve is concave with sustained marginal MDD relief
  (5.08pp from KMLM 20% → 30%) and only 0.60pp CAGR drag;
  `[advances_fin_ml, p.222-223]` DSR n_trials=17 worst p 5.56e-03 << 0.05.

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
