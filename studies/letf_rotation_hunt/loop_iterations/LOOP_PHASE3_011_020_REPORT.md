# letf_rotation_hunt — Phase 3 Performance Report (iters 011-020)

## TL;DR

- Phase 3 addressed the exact issue from iters 009-010: those were safer/Sortino beaters but not better compounders. The new phase explicitly targeted CAGR and terminal equity versus T3d-K2 while preserving PBO/global DSR controls.
- **Highest CAGR:** iter 011 `conditional-tqqq-leverage` at **36.69%** CAGR, edge **5.61%**, terminal equity **5.39x** T3d-K2, Sortino **1.2274**. It is a performance hit but not a Sortino beater.
- **Best balanced strict-superset:** iter 017 `postcrash-rearm-tqqq-streak` at **32.66%** CAGR, Sortino **1.4030**, terminal equity **1.61x**, PBO **0.440**.
- **First strict-superset:** iter 012. **First novel non-replica strict-superset:** iter 017. Iter 020 added more novel strict-supersets but did not improve over iter 017's best T40D60 anchor.
- Mandate §1 remains unchanged: 100% Plano C. These are research candidates, not automatic deployment instructions.

## Plots

![CAGR and Sortino](phase3_plots/01_phase3_cagr_sortino.png)

![Equity](phase3_plots/02_phase3_equity_vs_t3d.png)

![Relative Equity](phase3_plots/03_phase3_relative_equity.png)

![Rolling Winrate](phase3_plots/04_phase3_rolling_winrate_heatmap.png)

![CAGR Sortino Scatter](phase3_plots/05_phase3_cagr_sortino_scatter.png)

## Iteration Table

| Iter | Slug | CAGR | CAGR edge | Terminal ratio | Sortino | PBO | Score | Phase3 | Strict | Novel strict | Lesson |
|---:|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|---|
| 011 | `conditional-tqqq-leverage` | 36.69% | 5.61% | 5.39x | 1.2274 | 0.306 | 76.5 | Y | N | N | TQQQ upgrade restored performance but did not beat Sortino threshold. |
| 012 | `compound-tqqq-K4-x-ratevol-off` | 32.50% | 1.42% | 1.54x | 1.3769 | 0.496 | 76.5 | Y | Y | N | TQQQ K4 + ratevol OFF created first CAGR+Sortino strict-superset. |
| 013 | `triple-stack-K4lv25-graded-master` | 31.47% | 0.39% | 1.12x | 1.3951 | 0.544 | 72.5 | N | N | N | Triple stack improved risk metrics but PBO failed due parametric clustering. |
| 014 | `mechanism-mix-diverse-graded-blend` | 31.47% | 0.39% | 1.12x | 1.3951 | 0.440 | 76.5 | Y | Y | N | Mechanism diversity restored PBO and unlocked higher Sortino strict-superset. |
| 015 | `equity-tilted-basket-cagr-recovery` | 31.47% | 0.39% | 1.12x | 1.3951 | 0.333 | 76.5 | Y | Y | N | Static equity-tilted baskets could not clear CAGR floor without losing crisis rescue. |
| 016 | `regime-switch-on-leg-basket` | 31.47% | 0.39% | 1.12x | 1.3951 | 0.373 | 76.5 | Y | Y | N | Dynamic basket switching preserved crisis cushion but failed Phase 3 CAGR. |
| 017 | `postcrash-rearm-tqqq-streak` | 32.66% | 1.58% | 1.61x | 1.4030 | 0.440 | 76.5 | Y | Y | Y | Post-crash rearm produced first new non-replica strict-superset and better rolling performance. |
| 018 | `graded-rearm-depth-conditional` | 32.66% | 1.58% | 1.61x | 1.4030 | 0.813 | 72.5 | N | N | N | Graded rearm was parametric overfit; PBO blew up. |
| 019 | `spyrv-pct25-upgrade-mechmix` | 32.66% | 1.58% | 1.61x | 1.4030 | 0.198 | 76.5 | Y | Y | N | SPY realised-vol gate improved PBO diversity but not the best config. |
| 020 | `spy-mdd-rearm-gate` | 32.66% | 1.58% | 1.61x | 1.4030 | 0.433 | 76.5 | Y | Y | Y | MDD-depth gate produced new strict-supersets but did not beat iter 017 anchor. |

## Answer To The Performance Question

Yes: Phase 3 found strategies that improve performance versus T3d-K2, not just Sortino. Iter 011 is the clearest pure-performance result (36.69% CAGR, 5.42x terminal equity vs T3d-K2), but its Sortino is lower than the T3d threshold. Iter 012 is the first strict-superset: it beats T3d-K2 on CAGR, terminal equity and Sortino threshold simultaneously. Iter 017 is the strongest new non-replica strict-superset, improving CAGR to 32.66%, Sortino to 1.4030, and terminal equity to 1.62x while preserving PBO < 0.5.

The practical research incumbent after Phase 3 is therefore iter 017's `T40D60` post-crash rearm family, not the safer-but-slower iter 010 g25 bridge. Iter 020 confirms nearby depth-gated variants exist, but the MDD-depth filter does not improve over the iter 017 anchor.

## Rolling Window Diagnostics

| Iter | 1y win | 3y win | 5y win | 10y win | 3y mean ratio | 3y min ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 011 | 59.85% | 74.60% | 76.93% | 88.61% | 1.149x | 0.553x |
| 012 | 49.88% | 52.32% | 51.67% | 40.96% | 1.044x | 0.603x |
| 013 | 42.15% | 46.43% | 45.75% | 30.46% | 1.022x | 0.617x |
| 014 | 42.15% | 46.43% | 45.75% | 30.46% | 1.022x | 0.617x |
| 015 | 42.15% | 46.43% | 45.75% | 30.46% | 1.022x | 0.617x |
| 016 | 42.15% | 46.43% | 45.75% | 30.46% | 1.022x | 0.617x |
| 017 | 49.97% | 56.47% | 63.20% | 50.49% | 1.045x | 0.631x |
| 018 | 49.97% | 56.47% | 63.20% | 50.49% | 1.045x | 0.631x |
| 019 | 49.97% | 56.47% | 63.20% | 50.49% | 1.045x | 0.631x |
| 020 | 49.97% | 56.47% | 63.20% | 50.49% | 1.045x | 0.631x |

## Next Work

1. Continue with iter 021 around the T40D60 strict-superset, but avoid narrow parametric clusters that caused iter 018 PBO blow-up.
2. Test T_crash/D_arm with a mechanism-diverse grid, not a pure sweep, to preserve CSCV rank diversity [advances_fin_ml, p.208-211].
3. Run independent implementation/cross-library parity before any mandate §7 discussion.
