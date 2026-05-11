# LETF Tax Comparison — Top-10 Swing Strategies

_Generated 2026-05-11T01:11:28.064546+00:00_

Spec: pre-publication agent spec removed from the public tree.

## Top-10 selection

| Rank | Config | Tier | Iter | Score |
|---:|---|---|---|---:|
| 1 | `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | T3d | 022-2026-05-06-T3d-extended-grid | 82.0 |
| 2 | `qld_voteK2_off_zroz_alt` | T3d | 023-2026-05-06-T3d-multi-asset-grid | 82.0 |
| 3 | `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | T3d | 022-2026-05-06-T3d-extended-grid | 82.0 |
| 4 | `qld_voteK2_off_edv` | T3d | 023-2026-05-06-T3d-multi-asset-grid | 82.0 |
| 5 | `qld_voteK2_off_tlt` | T3d | 023-2026-05-06-T3d-multi-asset-grid | 82.0 |
| 6 | `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | T3d | 022-2026-05-06-T3d-extended-grid | 79.0 |
| 7 | `qld_vote_k2_off_zroz` | T3d | 014-2026-05-06-T3d-vote-of-k | 78.0 |
| 8 | `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | T3d | 022-2026-05-06-T3d-extended-grid | 76.5 |
| 9 | `tqqq_voteK2_off_zroz` | T3d | 023-2026-05-06-T3d-multi-asset-grid | 76.5 |
| 10 | `qld_voteK2_off_ief` | T3d | 023-2026-05-06-T3d-multi-asset-grid | 76.5 |

## Per-strategy net Sharpe (lh_56y)

| Config | Gross | Model 1 (per-swing) | Model 2 (annual) | SPY edge gross | SPY edge M1 | SPY edge M2 |
|---|---:|---:|---:|---:|---:|---:|
| `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | 0.853 | 0.687 | 0.768 | +0.171 | +0.005 | +0.086 |
| `qld_voteK2_off_zroz_alt` | 0.853 | 0.687 | 0.768 | +0.171 | +0.005 | +0.086 |
| `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | 0.847 | 0.690 | 0.763 | +0.165 | +0.008 | +0.081 |
| `qld_voteK2_off_edv` | 0.794 | 0.641 | 0.715 | +0.112 | -0.041 | +0.033 |
| `qld_voteK2_off_tlt` | 0.794 | 0.641 | 0.715 | +0.112 | -0.041 | +0.033 |
| `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | 0.843 | 0.660 | 0.761 | +0.161 | -0.022 | +0.079 |
| `qld_vote_k2_off_zroz` | 0.853 | 0.687 | 0.768 | +0.171 | +0.005 | +0.086 |
| `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | 0.919 | 0.766 | 0.827 | +0.237 | +0.084 | +0.145 |
| `tqqq_voteK2_off_zroz` | 0.814 | 0.653 | 0.749 | +0.132 | -0.029 | +0.067 |
| `qld_voteK2_off_ief` | 0.781 | 0.635 | 0.703 | +0.099 | -0.047 | +0.021 |

_SPY 1× buy-and-hold Sharpe lh_56y: 0.682 (parent study anchor)._

## Plots

![Master summary](master_summary.png)

Per-strategy plots in `per_strategy_plots/` — `<NN>_<name>_equity.png` and `<NN>_<name>_ratio.png`.

## Citations

- Lei 14.754/2023 (Brazil) — 15% flat, indefinite carry-forward.
- `[advances_fin_ml, p.275]` — net-of-cost Sharpe evaluation.
- Parent study protocol: `README.md`, `BASE_MEMORY.md` and `KILL_RULES.md`.