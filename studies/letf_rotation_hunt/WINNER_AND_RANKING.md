# Winner conditions + scoring rubric — letf_rotation_hunt

> **Current status (2026-05-08): Sortino-first.** This file started as the
> Sharpe-era scoring rubric. After the post-close Sortino re-analysis and T5
> expansion, the operative winner is
> `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` with Sortino 1.3246. Sharpe is
> retained below as historical/secondary context and because DSR is explicitly a
> Deflated Sharpe Ratio gate `[advances_fin_ml, p.196-202]`.

## Scoring rubric (0-100 + 5 bonus)

| # | Criterion | max | Rule |
|---|---|---:|---|
| 1 | Sortino edge vs anchor | 30 | tier-aware. +10 per dataset Sortino ≥ anchor + 0.05; +5 ALL 3. Legacy Sharpe scoring remains audit-only. |
| 2 | MDD vs SPY (warning-only) | 15 | linear: 15 × clamp((SPY_MDD − cand_MDD) / SPY_MDD, 0, 1) |
| 3 | Gates hard-pass (G1/G2/G3/G6/G7) | 20 | 4 pts per gate |
| 4 | DSR p-value (hybrid) | 10 | 10 @ p<0.05 / 7 @ p<0.10 / 3 @ p<0.20 |
| 5 | OOS + FWD robustness | 10 | 5 pts G4 + 5 pts G5 |
| 6 | Crisis attribution vs SPY | 10 | 2.5 pts each: 2000-02, 2008, 2020, 2022 using benchmark-relative equity, not absolute MDD |
| 7 | Bonus | +5 | regime-spread, turnover < 50%, novelty |

## Tier mapping

| score | KILL pass | KILL fail |
|---:|---|---|
| ≥ 90 | 🏆 WINNER | 🥇 STRONG |
| 75-89 | 🥇 STRONG | 🥈 PROMISING |
| 60-74 | 🥈 PROMISING | 🥉 MARGINAL |
| 40-59 | 🥉 MARGINAL | 📉 NEAR_FAIL |
| < 40 | 📉 NEAR_FAIL | ❌ FAIL |

WINNER tier requires score ≥ 90 AND all strict bars (G1, G2, G6, G7 pass; Sortino edge ≥ +0.05; pct_time_above_benchmark ≥ 0.95) AND KILL rule passed. MDD is warning-only per mandate §2.3.

## Anchors

| Anchor | Sortino / Sharpe (window) | Use |
|---|---:|---|
| SPY 1× buy-hold (lh_56y) | Sortino ~0.958 / Sharpe 0.682 | Bar mínima absoluta |
| T3d canonical `sma200/50` | Sortino 1.222 / Sharpe 0.853 | Post-close Sortino threshold anchor |
| T3d operative `sma250/100` | Sortino 1.3246 / Sharpe 0.919 | Current study winner |
| Gayed 2× LRS canon (SSO 200d × OFF=BIL, lh_56y) | Sharpe ~0.61 | T1 sanity check |
| Each tier prev-best | varies | KILL advance threshold |

Spec ref: §3.1, §3.2, §3.3.
