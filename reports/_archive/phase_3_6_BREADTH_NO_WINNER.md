# Phase 3.6 — BREADTH_NO_WINNER (§6.3 escalation)

**Date:** 2026-04-23
**Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched (commit `7b90a8f`), lookahead-clean; cross-lib Δ=0.000pp on 8/10 families.
**Pytest:** 918 green throughout (preserved by every candidate subagent).

---

## 0. Escalation trigger

Per plan §6.3: **10 FAIL candidates without any PASS** → write this report, stop loop, escalate to user.

All 10 families produced AGGREGATE.md + jornada + commit. No frozen files were touched. Mandate §7 and all strategy docs remain untouched. The sole open item is the user decision on path forward (§4 below).

---

## 1. Comparison table (all 10 families)

| # | Family | Paradigm | OOS Sharpe | OOS CAGR | OOS MDD | FWD Sharpe | PBO | IR vs SPY | cost×2 | Gates passed | What killed it |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A | `a_clenow_momentum` | Cross-sectional 90-day slope×R² momentum, top-N stocks, 200d regime | 0.25 | 2.67% | −26.6% | +1.18 | 0.25 ✅ | −0.63 | 0.23 | 3/13 | OOS edge absent (Sharpe 0.25), bootstrap CI straddles zero, universe-data gap pre-2013 |
| B | `b_risk_parity_inverse_vol` | Inverse-vol multi-asset ETF rotation, 21d rebal | 0.17 | 1.31% | −25.4% | +1.36 | 0.21 ✅ | −0.76 | 0.11 | 5/13 | Unleveraged RP = low-return by design (Qian); 2022 rate-shock broke bond+equity diversification |
| C | `c_gtaa_faber_10mo` | Faber 10-mo SMA on 5-asset basket | 0.41 | 3.89% | −20.7% | +1.61 | **0.91 ❌** | −0.50 | 0.41 | 5/13 | PBO 0.91 catastrophic — 10-mo MA is hindsight-fit; IS-best loses to OOS median 91% of CSCV splits |
| D | `d_chan_mr_pairs` | Cointegrated MR pairs (rolling OLS + EG gate), non-Kalman | −0.51 | −0.33% | −2.4% | +1.23 | 0.30 ✅ | −0.67 | −0.74 | 5/13 | Cointegration OFF 79-91% of bars — liquid ETF space too efficient for classical stat-arb (Chan p.88-89) |
| E | `e_ehlers_cycles` | Roofing filter + autocorrelation periodogram + adaptive RSI | −0.61 | −9.95% | −53.4% | +0.60 | 0.52 ❌ | −1.39 | −1.04 | 3/13 | "Cycles in trend = folly" (Ehlers, p.xi-xii); 697 trades × cost = 163% cum drag |
| F | `f_vol_target_managed_futures` | Carver EWMAC + portfolio 15% vol-target + IDM=√N | 0.11 | −0.14% | −36.5% | −0.07 | 0.60 ❌ | −0.33 | −0.45 | 1/13 | Pre-cost gross Sharpe 0.60 (signal works) but swap drag 311% cum at 2.22× avg leverage destroys edge (Carver speed-limit, p.185-188) |
| H | `h_amh_regime_switching` | Gaussian HMM on 20d realized moments (in-house EM+Viterbi) | 0.69 | 9.47% | −21.2% | +1.21 | 0.19 ✅ | −0.17 | 0.69 | 5/13 | State-conditional mean return IDENTICAL across IS regimes (+0.04%/d both) — HMM gates volatility, not direction |
| I | `i_stat_sound_indicators` | Masters/Aronson permutation + Bonferroni screen over 8 indicators | — | — | — | — | — | — | — | structural | 0/8 indicators survive p_corr<0.001 on IS — best Connors-RSI2 at p_corr=0.256; consistent with Aronson's 6,402-rule null finding (p.459) |
| J | `j_ml_classical` | Jansen-style sklearn GBM, purged kfold, 7-ETF panel, 5d sign label | 0.23 | 2.62% | −35.3% | +1.16 | 0.02 ✅ | −0.92 | 0.14 | 4/13 | IS→OOS Sharpe decay 1.25→0.23 (−82%) = regime-shift intolerance; 51.6% importance on vol/corr features = classifier-disguised-as-predictor |
| K | `k_universal_trend` | Penfold Donchian-50 + ATR(14)×3 trailing stop + P24 ETF proxy | 0.39 | 1.88% | **−9.9% ✅** | **+0.21 ✅** | **0.96 ❌** | −0.56 | −0.22 | 3/13 | PBO 0.96 catastrophic; UPI OOS 0.33 < Penfold's own 0.5 "low" threshold (p.259); P24 5/8 sector coverage insufficient |

Legend: ✅ = gate-pass; ❌ = catastrophic fail; — = undefined (structural).

---

## 2. Cross-family patterns

### 2.1 Best in class is still far from winner

- **Best OOS Sharpe = 0.69** (Family H, HMM regime) — gate 2 needs **1.5**. Gap = 0.81.
- **Best OOS CAGR = 9.47%** (Family H) — gate 3 (CDI soft-floor) needs **13%**. Gap = 3.5pp.
- **Best IR vs SPY = −0.17** (Family H) — gate 8 needs **+0.3**. No family beats SPY buy-hold.

Family H is the closest to a PARTIAL winner (5/13) but still misses the edge gates by material margins.

### 2.2 FWD-positive anomaly (diagnostic, not winner signal)

Seven of ten families have **positive FWD Sharpe** on 2024-01-01 → 2026-04-14 despite OOS failure:
- K +0.21, E +0.60, B +1.36, H +1.21, J +1.16, D +1.23, A +1.18, C +1.61

Two interpretations (neither is "winner"):
1. **Regime-shift signal:** the 2018-2023 OOS window (rate hike cycle, 2022 simultaneous bond+equity drawdown, COVID) was unusually hostile to mean-reversion and rotation mechanisms; 2024-2026 has been trend-benign. This is 2 years of data and cannot rescue a Sharpe 0.23 OOS over 6 years.
2. **Selection bias in FWD:** FWD is short (2.3 years) and post-2022; many strategies had peak-to-peak tailwinds. Bootstrap CI on FWD would overlap zero for most.

Neither reading justifies promoting any family to WINNER.

### 2.3 Engine cleanliness confirmed end-to-end

- 8 of 10 families: cross-lib Δ=**0.000pp** on OOS (bt / vectorbt / backtrader / hand-rolled pandas all agree).
- 1 family (D): Δ=0.37pp (passes ±3pp gate 9).
- 1 family (I): cross-lib deferred (structural-FAIL upstream).

The F2 engine fix (commit `7b90a8f`) holds across 10 independently-implemented strategies. The negative verdicts are **not** due to engine bias.

### 2.4 Catastrophic PBO in 3 families

C (0.91), E (0.52), F (0.60), K (0.96) all fail PBO<0.5. Pattern: families with many configurable hyperparameters (SMA windows, lookbacks, breakout lengths, ATR multipliers) rank their IS-best config poorly OOS. This is textbook overfit `[advances_fin_ml, p.208-211]` — selection across a wide hyperparameter surface on a mean-reverting regime does not generalize.

Families with low PBO (B, D, H, J, A all < 0.35) pass the overfit gate but still **fail the edge gates**: the strategies are honestly implemented, not overfit, and they genuinely do not have edge under realistic frictions on liquid US ETFs.

### 2.5 Distinct from V2 failures

Every Family D, F, H, J differentiator from its V2 cousin landed mechanistically:
- D (non-Kalman) produced 57 trades vs V2-L5 Kalman's 0 trades — different implementation, same no-edge destination.
- F (Carver continuous EWMAC, portfolio vol-target) vs V2-L1 TSMOM (binary past-return, per-leg vol) — different signal family, still no edge post-swap.
- H (Gaussian HMM on realized moments) vs V2-L2 Gayed (SMA/EMA cross on price) — different classifier, same vol-gater limit.
- J (Jansen GBM, panel features, purged kfold, 5d label) vs V2-L3 AFML (triple-barrier meta-label on XLF) — different ML paradigm, same regime-shift failure.

The V2 result ("6 canonical families fail honest gates") is robust to paradigm-family perturbation, not to implementation detail.

---

## 3. What this means

**Phase 3.6's null finding is itself informative**: 10 fundamentally-different paradigms, all literature-canonical, none reach even the relaxed gate thresholds on post-2018 liquid US ETF/stock universes. This is exactly the class of result predicted by:
- Aronson's 6,402-rule S&P 500 null study `[evidence_based_ta, p.459]`
- López de Prado's deflated-Sharpe framework `[advances_fin_ml, p.196-211]`
- Hsu/Kuan's 82% post-selection decay on S&P/DJIA rules (p.450)

"Honest gates + canonical literature + 25 years of Tiingo data = no winner" is not a bug; it is the post-2008 honest-backtest reality on this instrument universe.

---

## 4. Recommendations (per plan §6.3)

**Orchestrator does NOT choose; user chooses.** Four concrete paths:

### R1 — Broaden the instrument universe

**What:** re-run a subset of the 10 families on a wider basket. Specifically:
- Add BR IBOV ETFs (BOVA11, SMAL11, PIBB11, IVVB11) — currency-localized, may have edge invisible to US ETF lens.
- Add EM local indices (INDA, EWZ, EWY, FXI, VWO beyond EEM).
- Add futures contracts via a brokerage with futures access (Pepperstone has some, Interactive Brokers, Saxo). Would need new data feed — Tiingo EOD doesn't cover CME futures cleanly.
- Add news sentiment / earnings surprise data (Family L blocked by this gap).

**Prior probability of winner:** moderate. Families A, H, J looked promising within thresholds — wider universe could push them over.

**Cost:** 2-4 weeks. New data pipeline + re-implementation + re-validation.

**Risk:** if widening the universe introduces data issues (survivorship in BR ETFs, limited history in EM, futures roll-yield modeling) we re-validate garbage.

### R2 — Soften gates further with user sign-off

**What:** accept one of the "close" families (e.g., H at Sharpe 0.69 / CAGR 9.5%) as a "Plano B-minor" with explicit mandate §7 entry documenting the below-CDI reality.

**Prior:** this is **below the CDI floor already** (13%). Mandate §2 prohibits this unless user explicitly overrides. User already relaxed once (Sharpe 1.5 instead of 2.0, CDI instead of 30% CAGR). A second relaxation to "below CDI" violates the mandate's core invariant.

**Cost:** days. Re-document, re-run Family H winner config, commit.

**Risk:** strategy underperforms buy-hold SPY on a risk-adjusted basis. Violates mandate §2. Would require explicit mandate §7 override + probably §4.7 re-examination.

### R3 — Pivot to Plano C passive only (mandate §4.7 fallback)

**What:** invoke the mandate §4.7 clause "if all active strategies fail gates, re-allocate bucket A (20-40% active) to Plano C (passive)". Bucket A → 60-80% passive buy-hold. No active strategy.

**Prior:** this is the **honest default** per mandate §2.2 zero-bypass. The 10-family hunt plus the 6 V2 failures (total 16 distinct strategies) is strong evidence that the active edge is not findable in the current search space.

**Cost:** hours. Document decision + mandate §7 entry + strategy doc closure + jornada entry. No code change.

**Risk:** project-level ambition shrinks — the 2026-04-15 pivot to "intraday short-hold CFDs" gets abandoned in favor of passive allocation. User accepted this risk implicitly in mandate §4.7.

### R4 — Re-run `self_improve_loop` on fresh book-driven hypotheses

**What:** re-launch the self-improvement loop, feeding it the 33-book corpus + this BREADTH_NO_WINNER report + the 6 V2 verdicts + Wave 1-3 results. Loop generates fresh hypotheses that combine / mutate tested ideas.

**Prior:** low. The loop previously ran Phase 3.5e (38/144 trials, paused). Running it on the same corpus is unlikely to produce fundamentally new paradigms; at best it would find ensemble variants of tested families.

**Cost:** 2-3 weeks for another meaningful budget of LLM calls.

**Risk:** high token/API cost for low expected information gain. The 33-book corpus was already searched for these 10 + 6 V2 = 16 canonical families.

---

## 5. Orchestrator recommendation (informal, non-binding)

**R3 (pivot Plano C passive) is the cleanest honest path.** R1 (broaden universe) is the path with the highest technical upside but requires data-engineering investment. R2 (soften gates) violates mandate §2. R4 (re-run self-improve) is unlikely to surface new material beyond this report.

The user retains full authority to override.

---

## 6. Artifacts for the user review

- Running index (all 10 rows): `reports/phase_3_6/README.md`
- Per-family AGGREGATE.md: `reports/phase_3_6/<family_slug>/AGGREGATE.md`
- Per-family jornada entries: `jornada/2026-04-23-*-phase3.6-<slug>-FAIL.md`
- Commits on branch `phase3.6/swing-winner-hunt-20260423`:
  - Family A: `a6a7bb7`
  - Family B: `5d14dc2` (payload under Family-C-labeled message — see Caveats)
  - Family C: `7383f01`
  - Family D: `8189222`
  - Family E: `40f8c59`
  - Family F: `6fc87c3`
  - Family H: `8e1188b`
  - Family I: `f8fee06`
  - Family J: `de15860`
  - Family K: `b3788c9`

### Commit label caveat
`5d14dc2 feat(phase3_6): c_gtaa_faber_10mo honest validation — FAIL` contains Family B's payload (10 changed files all in `reports/phase_3_6/b_risk_parity_inverse_vol/` + Family B's strategy + runner). The title is wrong due to a concurrent-staging race between the Wave-1 B and C subagents. Content is correct (`git show 5d14dc2 --stat` confirms); title is misleading. No history rewrite performed — forensic record preserved.

---

## 7. Files NOT modified (invariants preserved)

- `docs/investment-mandate.md` — untouched
- `docs/self_improvement/memory.md` — untouched
- `docs/self_improvement/trial_count.json` — untouched
- All six `reports/phase_3_5f/honest_revalidation/*/AGGREGATE.md` — untouched
- `docs/.pending/*` — untouched (2026-04-22 mandate §7 entry pending user review, still awaits decision)
- All existing `docs/strategies/*.md` — untouched (no promotion without user sign-off)
- `reports/phase_3_5e/*`, `phase_3_5b/*`, `phase_3_5d/*` — untouched
- Buggy-baseline reports in `reports/phase3_5a_v2/v2_l2_*` — untouched (forensic banners from Phase 3.5f remain)

---

## 8. Citations

- López de Prado CSCV/PBO: `[advances_fin_ml, p.208-211]`
- López de Prado deflated-Sharpe: `[advances_fin_ml, p.196-211]`
- Aronson data-mining-bias: `[evidence_based_ta, p.459]`
- Hsu/Kuan rule-survivor: `[evidence_based_ta, p.450]`
- Chan ETF stat-arb compression: `[algo_trading_chan, p.88-89]`
- Ehlers trend-regime caveat: `[cycle_analytics, p.xi-xii]`
- Carver speed-limit: `[systematic_trading, p.185-188]`
- Qian unleveraged RP low-return: `[risk_parity, p.10, p.15-16, p.73-74]`
- Penfold UPI threshold: `[universal_trend_tactics, p.259]`
- Clenow 10-mo MA hindsight caveat: `[trading_evolved, p.211-212]`
- Investment mandate CDI floor + §4.7 fallback: `[docs/investment-mandate.md §2, §4.7]`

---

**End of BREADTH_NO_WINNER.md. User decision pending.**
