# Flags — 2-leg LETF+QQQ EW (Phase 3.5b addendum Task A)

## Gate verdicts

| Gate | Threshold | Measured | Verdict |
|------|-----------|----------|---------|
| Diversification Ratio (full) | > 1.20 | 1.121 | ⚠️ **FAIL** |
| Diversification Ratio (IS) | > 1.20 | 1.135 | ⚠️ **FAIL** |
| Pearson ρ(LETF, QQQ) | — | 0.555 | — (doubling-down) |

## Why DR FAIL

The Diversification Ratio (Choueifaty-Coignard 2008,
`[advances_fin_ml, p.310]`) is `DR = (Σ wᵢ σᵢ) / σ_portfolio`. It
measures how much portfolio vol is reduced relative to the
weighted-average leg vol. DR = 1 iff legs are perfectly correlated;
the Phase 3 A3c gate demanded DR > 1.20 (20% vol compression).

With ρ=0.555 (both legs long US equity — LETF riding the
S&P, QQQ riding the Nasdaq-100, which is a subset of S&P), the
compression is mechanically bounded. Adding a second long-equity
US leg is **doubling-down on a single factor** (US large-cap
growth), not genuine diversification across factors.

## Why ship the report anyway

The 2-leg blend *does* beat the best single leg on OOS Sharpe
(A3c iter 37 measured 2.098 vs LETF-only 1.990, +0.108). There's
an additive edge — it's just not a *diversification* edge in the
HRP/IVP sense. The addendum rule (`specs/phase_3_5b_addendum_
operational.md` §0) is run-to-completion: show all metrics, flag
failures, let the user compare against the 3-leg default.

## Full-window metrics (this run)

| Metric | 2-leg LETF+QQQ EW |
|--------|-------------------|
| CAGR | 31.59% |
| Sharpe (full window) | 1.888 |
| MaxDD | 14.41% |
| Information Ratio vs SPY | 1.158 |

## Comparison vs 3-leg default (Phase 3.5b winner)

Reference: `reports/phase3_5b/portfolio_3leg_ew/summary.json` —
the 3-leg EW {LETF+QQQ+GLD} blend is the production default.

Expected shape from A3c/A3d verdicts:

* 2-leg OOS Sharpe ≈ 2.098 vs 3-leg OOS Sharpe ≈ 2.251 → 3-leg
  wins by ~7% on OOS Sharpe.
* 2-leg DR=1.12 vs 3-leg DR>1.30 (GLD is the decorrelator).
* 2-leg MaxDD typically worse than 3-leg (GLD dampens equity
  drawdowns during 2008-09, 2020-03, 2022).

**Decision:** 2-leg is a sub-optimal simplification when GLD is
tradable on the user's broker. Deploy only if (a) broker blocks
GLD or (b) user explicitly prefers pure-equity exposure and
accepts the higher MaxDD.

## Citations

* DR formula: `[advances_fin_ml, p.310]`.
* Naive EW immunity to Σ-estimation error: `[advances_fin_ml,
  p.298-299]`.
* IVP/HRP tradeoffs used as rationale for DR gate:
  `[advances_fin_ml, p.302-313, ch.16]`.
