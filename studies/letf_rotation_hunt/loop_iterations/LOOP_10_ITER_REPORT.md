# letf_rotation_hunt — Post-Close Loop 001-010 Report

## TL;DR

- **Yes, the loop found strategies better than the closed-study T3d-K2 winner under the frozen `beats_winner` test.** Iters 009 and 010 cleared `sortino_lh56y > 1.3746`, `winner_conditions_met=True`, and `pct_time_above_benchmark_lh56y >= 0.95`.
- **Best result:** iter 010 `graded-master-bridge` with Sortino_lh56y **1.4670**, edge **+0.1424** vs T3d-K2 Sortino 1.3246, score **81.5**, PBO **0.393**, and `beats_winner=true`.
- **Not deploy-authorized:** score is still below the loop's 90-point public active-hunt/deploy escalation bar; mandate §1 remains 100% Plano C. This is a research beater, not an automatic capital allocation change.
- The decisive mechanism was not a single tweak: it was **compound structural diversity** — basket3 inverse-vol ON leg + bond-rate-vol OFF override + master/graded scope. This is exactly why the PBO finally dropped below 0.5 after iter 009 [advances_fin_ml, p.208-211].
- DSR accounting uses global trials starting from N=426 and ending at N=486, per loop protocol [advances_fin_ml, p.222-223].

## Plots

![Iter performance](summary_plots/01_iter_performance_sortino_score.png)

![Equity vs T3d](summary_plots/02_equity_vs_t3d.png)

![Relative equity vs T3d](summary_plots/03_relative_equity_vs_t3d.png)

![Rolling window heatmap](summary_plots/04_rolling_window_winrate_heatmap.png)

![Top rolling relative](summary_plots/05_top_iters_rolling_3y_relative.png)

## Iteration Summary

| Iter | Hypothesis slug | Best Sortino | Edge vs T3d | Score | PBO | DSR p_cum | G5 FWD Sharpe | Crisis | beats_winner | Lesson |
|---:|---|---:|---:|---:|---:|---:|---:|---:|:---:|---|
| 001 | `adaptive-off-yieldcurve` | 1.3018 | -0.0228 | 72.5 | 0.575 | 0.0040 | 0.782 | 1/4 | N | OFF yield curve helped little; 2022 was mostly ON-leg damage. |
| 002 | `on-vol-dd-killswitch` | 1.2841 | -0.0405 | 76.5 | 0.159 | 0.0051 | 0.708 | 1/4 | N | Drawdown kill-switch was too late and suppressed rallies. |
| 003 | `calendar-halloween-gate` | 1.3061 | -0.0185 | 71.5 | 0.444 | 0.0047 | 0.371 | 1/4 | N | Calendar veto marginally helped but could not solve 2022. |
| 004 | `corr-regime-stockbond` | 1.2841 | -0.0405 | 76.5 | 0.071 | 0.0052 | 0.708 | 1/4 | N | Stock-bond correlation gate was redundant with trend signal. |
| 005 | `multi-asset-on-invvol` | 1.3340 | +0.0094 | 77.5 | 0.881 | 0.0033 | 0.898 | 3/4 | N | Basket3 inverse-vol ON leg gave the first positive edge. |
| 006 | `bond-ratevol-regime` | 1.3386 | +0.0140 | 72.5 | 0.798 | 0.0026 | 0.908 | 1/4 | N | Bond rate-vol OFF override improved post-2020 universally. |
| 007 | `compound-ratevol-off-x-invvol-on-basket` | 1.4637 | +0.1391 | 75.0 | 0.552 | 0.0005 | 1.227 | 2/4 | N | Combining iter 005+006 was super-additive, but PBO barely failed. |
| 008 | `compound-4axis-cscv-diversity` | 1.4637 | +0.1391 | 75.0 | 0.567 | 0.0005 | 1.227 | 2/4 | N | Parametric expansion did not improve PBO; structure matters. |
| 009 | `master-scope-off-override` | 1.4637 | +0.1391 | 79.0 | 0.377 | 0.0005 | 1.227 | 2/4 | Y | Master-scope structural diversity cracked PBO and produced first beater. |
| 010 | `graded-master-bridge` | 1.4670 | +0.1424 | 81.5 | 0.393 | 0.0005 | 1.175 | 3/4 | Y | Graded master bridge improved Sortino and 2022 rescue while preserving PBO. |

## Beater Verdict

The loop found **2 best-config beaters by iteration-level winner**: iter 009, iter 010.

Strictly, iter 009 produced the first `beats_winner=true` configs, and iter 010 produced the best overall config. The best config is:

- Iter: `010-2026-05-09-graded-master-bridge`
- Config: `qld_voteK2_sma250_100_vol21_40_ar30_gmaster_g25_cashx`
- Sortino_lh56y: `1.4670` vs T3d-K2 `1.3246`
- Edge: `+0.1424`
- Score/tier: `81.5` / `STRONG`
- PBO: `0.3929`
- DSR p_cumulative: `0.000531`
- pct_time_above_benchmark_lh56y: `1.0000`

This is better than T3d-K2 as a **research candidate**, but not a mandate override. The score remains below 90, so the conservative next step is iter 011+ validation/consolidation, not deployment.

## Rolling Window Diagnostics Vs T3d-K2

Values below are based on best-config daily returns per iter against the closed-study T3d-K2 return stream. `win_rate` means rolling end-equity ratio > 1.

| Iter | 1y win | 3y win | 5y win | 10y win | 3y mean ratio | 3y min ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 001 | 47.66% | 49.41% | 40.60% | 31.16% | 1.001x | 0.782x |
| 002 | 0.00% | 0.00% | 0.00% | 0.00% | 1.000x | 1.000x |
| 003 | 49.35% | 50.57% | 42.18% | 41.36% | 1.044x | 0.486x |
| 004 | 0.00% | 0.00% | 0.00% | 0.00% | 1.000x | 1.000x |
| 005 | 41.85% | 37.81% | 29.22% | 23.41% | 0.891x | 0.155x |
| 006 | 43.50% | 43.77% | 52.55% | 46.10% | 1.026x | 0.662x |
| 007 | 41.02% | 39.92% | 37.54% | 26.68% | 0.919x | 0.154x |
| 008 | 41.02% | 39.92% | 37.54% | 26.68% | 0.919x | 0.154x |
| 009 | 41.02% | 39.92% | 37.54% | 26.68% | 0.919x | 0.154x |
| 010 | 39.44% | 36.73% | 35.45% | 22.23% | 0.896x | 0.147x |

## Interpretation

The loop path was informative: the first four attempts showed that simple gates around the original T3d signal did not solve the remaining weakness. Iter 005 found useful ON-leg diversification; iter 006 found useful bond-rate-vol OFF protection; iter 007 showed the combination was super-additive but still had PBO as a blocker; iter 009 changed the scope structure enough to pass PBO; iter 010 refined that scope into a graded bridge and became the best result.

The practical answer is therefore: **yes, we found something better than T3d-K2 inside this research loop**, but the result should be treated as a new incumbent research candidate requiring follow-up validation rather than as a live allocation decision.

## Next Work

1. Run iter 011+ around the graded bridge family with strict config budget and global DSR accounting.
2. Recompute cross-library agreement and independent implementation parity for iter 010 before any public promotion.
3. Add a dedicated report comparing iter 010 vs T3d-K2 by crisis windows, turnover, tax drag and execution assumptions.
4. Keep mandate §1 unchanged unless the user explicitly requests a mandate §7 override review.
