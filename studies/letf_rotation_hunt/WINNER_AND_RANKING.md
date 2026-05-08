# Winner conditions + scoring rubric — letf_rotation_hunt

## Scoring rubric (0-100 + 5 bonus)

| # | Criterion | max | Rule |
|---|---|---:|---|
| 1 | Sharpe edge vs anchor | 30 | tier-aware. +10 per dataset Sharpe ≥ anchor + 0.05; +5 ALL 3 |
| 2 | MDD vs SPY (warning-only) | 15 | linear: 15 × clamp((SPY_MDD − cand_MDD) / SPY_MDD, 0, 1) |
| 3 | Gates hard-pass (G1/G2/G3/G6/G7) | 20 | 4 pts per gate |
| 4 | DSR p-value (hybrid) | 10 | 10 @ p<0.05 / 7 @ p<0.10 / 3 @ p<0.20 |
| 5 | OOS + FWD robustness | 10 | 5 pts G4 + 5 pts G5 |
| 6 | Crisis attribution vs SPY | 10 | 2.5 pts each: 2000-02, 2008, 2020, 2022 (MDD ≤ SPY_MDD same window) |
| 7 | Bonus | +5 | regime-spread, turnover < 50%, novelty |

## Tier mapping

| score | KILL pass | KILL fail |
|---:|---|---|
| ≥ 90 | 🏆 WINNER | 🥇 STRONG |
| 75-89 | 🥇 STRONG | 🥈 PROMISING |
| 60-74 | 🥈 PROMISING | 🥉 MARGINAL |
| 40-59 | 🥉 MARGINAL | 📉 NEAR_FAIL |
| < 40 | 📉 NEAR_FAIL | ❌ FAIL |

WINNER tier requires score ≥ 90 AND all 5 strict bars (G1, G2, G6, G7 pass; Sharpe edge ≥ +0.05; MDD ≤ SPY) AND KILL rule passed.

## Anchors

| Anchor | Sharpe (window) | Use |
|---|---:|---|
| SPY 1× buy-hold (lh_56y) | 0.682 | Bar mínima absoluta |
| Gayed 2× LRS canon (SSO 200d × OFF=BIL, lh_56y) | ~0.61 | T1 sanity check |
| Each tier prev-best | varies | KILL advance threshold |

Spec ref: §3.1, §3.2, §3.3.
