# LETF Rotation Hunt — Post-Close Loop Report

**Status:** post-close autonomous loop completed through iter 030 on 2026-05-10. This report is a continuation of `reports/STUDY_FINAL_REPORT.md`, not a rewrite of the closed study.
**Closed-study DSR/config trials:** 426.
**Post-close loop trials:** 180.
**Cumulative DSR/config trials after iter 030:** 606.
**Prior operative winner:** `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` (T3d-K2, Sortino 1.3246, CAGR 31.08%).
**New post-close loop winner:** **`qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120`** (iter 030, Sortino 1.3839, CAGR 36.68%, score 79.5 STRONG).

This continuation asked a narrower question than the closed study: after T3d-K2 proved to be the best closed-study family, could we improve it without relaxing PBO/DSR anti-overfit gates? The answer through iter 030 is yes: the loop found a performance-first extension that preserves the T3d-K2 core, adds a post-crash rearm primitive, and applies an LRS1.20 exposure overlay `[leverage_for_the_long_run, ch.4-5, p.40-60]`, while preserving CSCV/DSR controls `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

**Mandate §1 reminder:** capital remains 100% Plano C. This report is research only. No automatic deploy or reallocation follows.

---

## 0. Master Visual Summary

![Loop 001-030 CAGR and Sortino](post_close_loop/plots/01_loop_001_030_cagr_sortino.png)

*The post-close loop began by finding high-Sortino but low-CAGR variants (iters 007-010), then shifted to performance-first exploration (iters 011-020), then focused on the iter 017 rearm family (iters 021-030). The final winner pushes CAGR from T3d-K2's 31.08% to 36.68% while keeping Sortino above the beater threshold 1.3746.*

![Equity vs T3d SPY NDX](post_close_loop/plots/02_equity_vs_t3d_spy_ndx.png)

*Log equity curves versus the prior T3d-K2 winner and passive buy-and-hold SPY/NDX (NDX represented by QQQSIM). The final post-close winner is the green curve.*

![Relative equity vs benchmarks](post_close_loop/plots/03_relative_equity_vs_benchmarks.png)

*Same convention as `STUDY_FINAL_REPORT.md`: benchmark-relative equity matters more than absolute drawdown in isolation. The new winner remains above T3d-K2, SPY, and NDX/QQQ across most rolling horizons.*

![Drawdowns vs benchmarks](post_close_loop/plots/04_drawdowns_vs_benchmarks.png)

*Drawdown remains severe, as expected for 2.4× effective NDX exposure during ON windows. MDD remains warning-only per mandate §2.3; hard validation comes from PBO, DSR, walk-forward, OOS, FWD, bootstrap CI, and cross-lib checks.*

![LRS frontier](post_close_loop/plots/05_lrs_magnitude_frontier.png)

*Phase 4 mapped the LRS magnitude frontier on the rearm base. LRS1.05 → LRS1.20 raised CAGR monotonically while Sortino decayed roughly linearly and stayed above threshold through LRS1.20.*

![Tcrash scan](post_close_loop/plots/06_tcrash_scan_t35_t50.png)

*Iter 030 falsified the T40 anchor on the T_crash axis: T35D60 + LRS1.20 strictly dominates T40D60 + LRS1.20 on CAGR, Sortino, and terminal equity.*

![Rolling win-rate heatmap](post_close_loop/plots/07_iter030_rolling_winrate_heatmap.png)

*Rolling-window win rates for the new winner versus T3d-K2, SPY, and NDX/QQQ. The strategy beats T3d-K2 in 72.0% of rolling 1y windows, 79.7% of 3y, 83.3% of 5y, and 96.1% of 10y windows.*

Supporting tables:
- `post_close_loop/tables/post_close_loop_001_030_summary.csv`
- `post_close_loop/tables/iter030_rolling_win_rates.csv`

---

## 1. TL;DR

The closed study found T3d-K2 as the operative winner under Sortino: `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`, Sortino 1.3246, CAGR 31.08%, score 82 STRONG. It remained non-deploy because score < 90 and mandate §1 keeps capital in Plano C.

The post-close loop extended that winner in three stages:

| Stage | Iters | Result |
|---|---:|---|
| Sortino-first safety/mix probes | 001-010 | Found high-Sortino variants, but most sacrificed CAGR/terminal equity. Best Sortino-only was iter 010 at Sortino 1.4670 but CAGR only 22.39%. |
| Performance-first hunt | 011-020 | Moved from safety to CAGR/equity. Iter 017 introduced `T40D60` post-crash rearm and became the balanced incumbent: Sortino 1.4030, CAGR 32.66%, terminal ratio 1.61× vs T3d-K2. |
| Focused Phase 4 refinement | 021-030 | Validated rearm, mapped LRS magnitude, falsified regime-gating fixes, then found T35D60 + LRS1.20 as the new winner: Sortino 1.3839, CAGR 36.68%, terminal ratio 5.395× vs T3d-K2. |

The final winner is not a new strategy family. It is an extension of T3d-K2:

```text
T3d-K2 core
+ rearm-only post-crash window: T35D60
+ unconditional LRS1.20 exposure overlay during eligible ON/rearm days
```

Operationally, `T35D60` means: when the T3d-K2 master ON/OFF signal flips from OFF to ON after at least 35 consecutive OFF days, open a 60-trading-day rearm window. This is not a direct drawdown-percent trigger; it is a state-machine trigger derived from the T3d-K2 ON/OFF signal `[leverage_for_the_long_run, p.6-7, ch.3]`.

`LRS1.20` means 1.20× exposure to the QLD on-leg. Since QLD is approximately 2× NDX, the economic exposure is approximately 2.4× NDX during eligible ON windows. A no-margin deploy proxy would be approximately 80% TQQQ + 20% cash, but that proxy has not yet been formally validated and should not be treated as identical.

---

## 2. Headline Comparison

| Strategy | Role | Sortino | CAGR | MDD | PBO | DSR global | End equity vs T3d-K2 | Score | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| SPY buy&hold | Passive benchmark | n/a | n/a | n/a | n/a | n/a | n/a | n/a | benchmark |
| NDX/QQQ buy&hold | Tech beta benchmark | n/a | n/a | n/a | n/a | n/a | n/a | n/a | benchmark |
| T3d-K2 | closed-study winner | 1.3246 | 31.08% | -64.5% | pass | pass | 1.000× | 82.0 | STRONG |
| Iter 017 T40D60 | Phase 3 anchor | 1.4030 | 32.66% | -48.2% | 0.4405 | 9.92e-04 | 1.620× | 76.5 | STRONG |
| Iter 027 T40D60 + LRS1.20 | Phase 4 frontier before T scan | 1.3786 | 36.22% | -55.5% | 0.3929 | 1.55e-03 | 4.710× | 76.5 | STRONG |
| **Iter 030 T35D60 + LRS1.20** | **new post-close winner** | **1.3839** | **36.68%** | **-55.5%** | **0.0357** | **1.47e-03** | **5.395×** | **79.5** | **STRONG** |

Important nuance: the loop score remains below 90. Under project governance, this is still STRONG research, not a deployment authorization.

---

## 3. What Changed From T3d-K2?

### 3.1 T3d-K2 base logic

The closed-study winner is:

```text
qld_voteK2_sma250_100_vol21_40_ar30_off_zroz
```

Definition:
- Risk-on asset: QLD.
- Risk-off asset: ZROZ.
- ON when at least 2 of 4 signals fire:
  - price > SMA250
  - price > SMA100
  - 21d realized volatility < 40%
  - AR(1) 30d > 0
- OFF otherwise.

This remains the master signal. The post-close winner does not replace the core; it adds stateful rearm and LRS logic on top.

### 3.2 New winner logic

The new winner is:

```text
qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120
```

Implementation deltas:
- Same T3d-K2 master ON/OFF signal.
- `rearmonly`: upgrade activation is driven by the post-crash rearm gate only.
- `T35D60`: qualify an OFF→ON flip only if the prior contiguous OFF stretch was at least 35 trading days; then activate rearm for 60 trading days.
- `g25`: 25% upgrade blend parameter retained from the rearm family.
- `rvp70`: rate-vol percentile parameter retained from the rearm/LRS family.
- `cashx`: uses CASHX in the rearm-family off/overlay mechanics.
- `unclrs120`: unconditional LRS1.20 overlay on eligible ON/rearm exposure.

The key rearm mechanism is code-equivalent to:

```python
if today_on and yesterday_off and prior_contiguous_off_days >= 35:
    rearm_days_left = 60
```

Then LRS1.20 scales the eligible on-leg exposure. This is a simple daily state machine; it is deployable by script, but execution proxy validation remains pending.

---

## 4. Iteration Evolution 001-030

| Iter | Slug | Best Sortino | CAGR | PBO | Outcome |
|---:|---|---:|---:|---:|---|
| 001 | adaptive-off-yieldcurve | 1.3018 | 29.81% | 0.5754 | adaptive OFF failed PBO/return edge |
| 002 | on-vol-dd-killswitch | 1.2841 | 29.85% | 0.1587 | risk kill switch did not improve winner |
| 003 | calendar-halloween-gate | 1.3061 | 27.99% | 0.4444 | calendar veto reduced performance |
| 004 | corr-regime-stockbond | 1.2841 | 29.85% | 0.0714 | correlation gate did not beat winner |
| 005 | multi-asset-on-invvol | 1.3340 | 22.59% | 0.8810 | multi-asset mix failed PBO/performance |
| 006 | bond-ratevol-regime | 1.3386 | 30.54% | 0.7976 | rate-vol OFF idea failed PBO |
| 007 | compound-ratevol-off-x-invvol | 1.4637 | 23.25% | 0.5516 | strong Sortino, weak CAGR; PBO borderline |
| 008 | compound-4axis-cscv-diversity | 1.4637 | 23.25% | 0.5675 | diversity did not solve PBO enough |
| 009 | master-scope-off-override | 1.4637 | 23.25% | 0.3770 | first `beats_winner=true`, but low CAGR |
| 010 | graded-master-bridge | **1.4670** | 22.39% | 0.3929 | best Sortino-only, but not performance-first |
| 011 | conditional-tqqq-leverage | 1.2274 | **36.69%** | 0.3056 | huge CAGR, Sortino too low for beater |
| 012 | compound-tqqq-K4-x-ratevol-off | 1.3769 | 32.50% | 0.4960 | first strict-superset performance candidate |
| 013 | triple-stack-K4lv25-graded-master | 1.3951 | 31.47% | 0.5437 | good mechanics, PBO blocked |
| 014 | mechanism-mix-diverse-graded-blend | 1.3951 | 31.47% | 0.4405 | strict-superset; K4/lv25 anchor emerges |
| 015 | equity-tilted-basket-cagr-recovery | 1.3951 | 31.47% | 0.3333 | confirms same K4/lv25 region |
| 016 | regime-switch-on-leg-basket | 1.3951 | 31.47% | 0.3730 | confirms single/K4 structure |
| 017 | postcrash-rearm-tqqq-streak | 1.4030 | 32.66% | 0.4405 | T40D60 rearm anchor found |
| 018 | graded-rearm-depth-conditional | 1.4030 | 32.66% | 0.8135 | graded depth caused PBO blowup |
| 019 | spyrv-pct25-upgrade-mechmix | 1.4030 | 32.66% | 0.1984 | PBO improved; no new performance edge |
| 020 | spy-mdd-rearm-gate | 1.4030 | 32.66% | 0.4325 | MDD gate rejected; T40D60 remains anchor |
| 021 | rearm-component-ablation | 1.4689 | 22.65% | 0.5000 | ablation validates components; formal block |
| 022 | rearm-only-indep-pfv-confirm | 1.4176 | 32.44% | 0.4960 | independent rearm-only parity validated |
| 023 | rearm-leverage-overlay-and-k4mutex | 1.4202 | 33.16% | 0.6548 | qualitative LRS win, PBO clustering blowup |
| 024 | pbo-decoupled-unconditional-lrs105 | 1.4068 | 33.43% | 0.4365 | first formal Phase 4 improvement |
| 025 | pbo-decoupled-lrs110-rearm-magnitude | 1.3968 | 34.39% | 0.4365 | Pareto improvement over 024 |
| 026 | pbo-decoupled-lrs115-rearm-magnitude | 1.3874 | 35.32% | 0.4127 | LRS monotonicity holds |
| 027 | pbo-decoupled-lrs120-ceiling-probe | 1.3786 | 36.22% | 0.3929 | LRS1.20 frontier; best until iter 030 |
| 028 | pbo-decoupled-lrs120-ratevol-gated-calm | 1.3860 | 35.11% | 0.4127 | calm gate falsified modern-softness fix |
| 029 | pbo-decoupled-lrs120-ratevol-gated-stress | 1.4001 | 33.03% | 0.4563 | stress gate also falsified modern-softness fix |
| 030 | tcrash-scan-lrs120-rearmonly | **1.3839** | **36.68%** | **0.0357** | **new winner: T35D60 + LRS1.20** |

---

## 5. Phase 4 Findings

### 5.1 Rearm primitive validated

Iters 021-022 separated the rearm mechanism from the surrounding K4/OR scaffolding. The independent implementation reproduced the iter 017 rearm gate bit-exact, establishing that the mechanism was not an artifact of one helper implementation. The rearm-only T40D60 variant achieved Sortino 1.4176 and CAGR 32.44%.

### 5.2 Iter 023 identified the PBO failure mode

Iter 023 added LRS inside the rearm window and produced attractive raw results, but PBO blew out to 0.6548. The diagnosis was structural: too many configs shared the same rearm scaffolding, creating CSCV rank clustering. This became the design constraint for iters 024-030.

### 5.3 Iter 024 fixed the PBO structure

Iter 024 decoupled the LRS axis by testing a mechanism-mix layout with 3 non-rearm and 3 rearm-scaffolded configs. PBO dropped to 0.4365 and the first formal Phase 4 improvement appeared: LRS1.05 on rearm-only base, Sortino 1.4068, CAGR 33.43%.

### 5.4 Iters 025-027 mapped the LRS frontier

LRS magnitude was increased from 1.05 to 1.20:

| LRS | Sortino | CAGR | End equity vs T3d-K2 | PBO | Read |
|---:|---:|---:|---:|---:|---|
| 1.00 | 1.4176 | 32.44% | 1.516× | 0.4960 | rearm-only baseline |
| 1.05 | 1.4068 | 33.43% | 2.049× | 0.4365 | first formal improvement |
| 1.10 | 1.3968 | 34.39% | 2.730× | 0.4365 | Pareto improvement |
| 1.15 | 1.3874 | 35.32% | 3.610× | 0.4127 | monotonicity holds |
| 1.20 | 1.3786 | 36.22% | 4.710× | 0.3929 | frontier before T_crash scan |

Sortino declined almost linearly as exposure rose; CAGR and terminal equity rose strongly. LRS1.20 remained above the beater threshold but with limited headroom. This is why iter 027 was the best candidate before iter 030.

### 5.5 Iters 028-029 rejected rate-vol regime conditioning

Iter 028 applied LRS1.20 only in calm bond-rate-vol regimes. Iter 029 applied it only in stress regimes. Both preserved formal `phase4_anchor_improved=true`, but neither Pareto-dominated iter 027. More importantly, neither fixed the modern-era softness: 1990-2009 and 2010-2026 Sortino remained below the 1.20 Phase 3 subperiod floor.

Conclusion: modern softness is structural to the rearm primitive and modern QLD volatility cluster, not an issue solved by calm/stress conditioning.

### 5.6 Iter 030 falsified T40 and found T35

Iter 030 tested T_crash {35, 40, 45, 50} with D_arm fixed at 60 and LRS fixed at 1.20. Results were monotone: lower T_crash improved CAGR, Sortino, and terminal equity.

| T_crash | Flips | Sortino | CAGR | End equity vs T3d-K2 | Beats winner? |
|---:|---:|---:|---:|---:|:---:|
| **35** | **20** | **1.3839** | **36.68%** | **5.395×** | **yes** |
| 40 | 16 | 1.3786 | 36.22% | 4.710× | yes |
| 45 | 14 | 1.3689 | 35.77% | 4.133× | no, below 1.3746 threshold |
| 50 | 9 | 1.3379 | 34.27% | 2.635× | no, below 1.3746 threshold |

This means the iter 017 T40 anchor was not locally robust. T35D60 is the current post-close loop winner.

---

## 6. Benchmark-Relative Robustness

Rolling-window win rates for iter 030 T35D60 + LRS1.20:

| Benchmark | 1y | 3y | 5y | 10y |
|---|---:|---:|---:|---:|
| T3d-K2 | 72.0% | 79.7% | 83.3% | 96.1% |
| SPY buy&hold | 81.1% | 98.3% | 100.0% | 100.0% |
| NDX/QQQ buy&hold | 77.2% | 96.2% | 99.9% | 100.0% |

Mean rolling end-ratio versus T3d-K2:
- 1y: 1.05×
- 3y: 1.14×
- 5y: 1.24×
- 10y: 1.45×

The important result is not only that terminal equity is higher; the advantage is distributed across rolling windows, especially at 3y+ horizons.

---

## 7. New Winner: Practical Interpretation

### 7.1 State variables needed for script monitoring

The winner is operationally simple. A daily script needs:

```text
on_signal_today
on_signal_yesterday
rearm_days_left
target_exposure
```

Daily flow:
1. Update QLD/QQQ-equivalent price history.
2. Compute the T3d-K2 VoteK2 signal.
3. If signal is OFF, increment `off_count`.
4. If signal flips OFF→ON and `off_count >= 35`, set `rearm_days_left = 60`.
5. During the rearm window, apply the rearm-only upgrade and LRS1.20 exposure rule.
6. Save state after each close.

### 7.2 No-margin proxy

The backtest expression `LRS1.20` means 120% QLD exposure. Since QLD is roughly 2× QQQ, this is approximately 2.4× NDX exposure.

No-margin approximation:

```text
120% QLD ≈ 80% TQQQ + 20% cash
```

This is economically intuitive because 0.80 × 3× = 2.4×. It is not yet formally validated. TQQQ and QLD have different fees, tracking, and daily compounding path-dependence. The next deploy-readiness step should explicitly backtest this no-margin proxy.

---

## 8. Limitations and Risks

1. **Still not deploy-authorized.** Score is 79.5, below the 90 deploy threshold. Mandate §1 remains unchanged.
2. **Modern-era softness remains.** T35 improves performance but does not lift 1990-2009 or 2010-2026 Sortino above the Phase 3 subperiod floor of 1.20.
3. **LRS1.20 is close to the Sortino beater boundary.** The winner has more headroom than T40 LRS1.20, but the family still trades Sortino for CAGR.
4. **Execution proxy not validated.** 80% TQQQ + 20% cash is the natural no-margin proxy, but it requires a dedicated validation run.
5. **Synthetic data caveat.** Long-history results rely on testfolio synthetic series for LETFs and benchmarks. Real Tiingo ETF windows should be used as a forward/live consistency check.
6. **No tax/slippage rebuild yet.** The closed study's tax analysis covered the prior T3d-K2 winner; iter 030 needs its own M1/M2 tax/slippage evaluation before any real allocation discussion.

---

## 9. Recommended Next Work

1. **Validate no-margin proxy:** replace 120% QLD with 80% TQQQ + 20% CASHX on the exact T35D60 signal. This is the most deployment-relevant next test.
2. **Extend T_crash downward:** test {25, 30} because T35 dominated T40/T45/T50 monotonically. Use the iter 030 PBO-diverse layout.
3. **Open D_arm sensitivity:** test D_arm {30, 45, 60, 90} with T_crash fixed at the current best T35.
4. **Tax/slippage rebuild:** run M1/M2 tax comparison for the new winner and no-margin proxy.
5. **Forward monitor only:** build a daily monitor that emits signal state, `off_count`, `rearm_days_left`, target exposure, and benchmark-relative equity. No capital allocation without mandate override.

---

## 10. Verdict

The post-close loop materially improved the closed-study T3d-K2 winner.

The best current research candidate is:

```text
qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120
```

It improves the prior T3d-K2 winner from Sortino 1.3246 / CAGR 31.08% to Sortino 1.3839 / CAGR 36.68%, with end equity approximately 5.4× T3d-K2 and PBO 0.0357. It also Pareto-dominates the previous Phase 4 frontier point, iter 027 T40D60 + LRS1.20.

The research conclusion is strong: T3d-K2 was not the end of the family. The post-close loop found a better performance-first variant while preserving the hard statistical gates. The governance conclusion is unchanged: capital remains 100% Plano C until a formal mandate override and a deployment-specific validation suite are completed.
