# ETF Focus Evolution Report

## TL;DR

Post-close ETF-specific evolution improved the ETF walk-forward diagnostic, but
did not create a deployable candidate.

| run | universe | configs | WF CAGR | WF MDD | WF Sharpe | PBO | DSR p | bootstrap low | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `focused_full_universe` | all cached ETFs, including leveraged/inverse | 36 | 11.29% | -26.03% | 0.712 | 0.313 | 0.152 | 0.06% | DSR fail |
| `focused_no_leveraged` | excludes leveraged/inverse ETFs | 36 | 6.65% | -20.33% | 0.647 | 0.310 | 0.232 | -0.67% | DSR/bootstrap fail |

The full-universe WF improved over the direct ADV-style ETF transplant
(`9.39%` CAGR, `0.604` Sharpe), mainly by using broader `k=10/20` ETF sleeves
and defensive `IEF/ZROZ` options. Removing leveraged/inverse ETFs cuts CAGR to
`6.65%`, which means the improvement is materially dependent on levered ETF
availability and cannot be treated as a clean ETF rotation edge. The focused
full-universe run passes diagnostic PBO/bootstrap but fails DSR, so it still does
not clear the mandate-style hard gate stack `[advances_fin_ml, p.273-275]`.

## Hypothesis Tested

ETF momentum was reframed as cross-asset/factor rotation rather than a direct
single-stock momentum transplant. The focused grid used:

- lookbacks `80,100,126`;
- `top_k` `10,20`;
- market filters `SPY>SMA200` and `SPY>SMA250`;
- defensive targets `cash`, `IEF`, `ZROZ`;
- 3y train -> 1y test walk-forward selection.

Cross-sectional momentum and regime filtering follow Clenow-style momentum/risk
filters `[stocks_on_the_move, p.60]`, `[stocks_on_the_move, p.66-67, p.81]`.
The walk-forward design is an anti-overfit diagnostic, not a full gate stack
`[advances_fin_ml, p.208-211]`.

## Evidence

- Full universe: `studies/weekly_momentum/evidence/etf_focus_evolution/focused_full_universe/REPORT.md`.
- No leveraged/inverse ETFs: `studies/weekly_momentum/evidence/etf_focus_evolution/focused_no_leveraged/REPORT.md`.
- Runner: `studies/weekly_momentum/scripts/etf_focus_evolution.py`.
- Earlier direct transplant WF: `studies/weekly_momentum/walk_forward/etfs_adv5m_best_config/WALK_FORWARD_REPORT.md`.
- Earlier fixed transplant: `studies/weekly_momentum/results/etfs/lb80_sig3_sell1_sd0_k5_neg0_defcash_mfsma250/report.md`.

## Decision

The ETF branch is closed with no deployable candidate. The focused
full-universe result is a useful diagnostic lead, but it is not enough to
override the closed-study verdict because:

- it has not passed PBO/DSR/bootstrap/cost/tax gates;
- the full-universe diagnostic fails DSR (`p=0.152`), and the no-leverage
  diagnostic fails DSR plus bootstrap;
- the cache is not a point-in-time investable ETF universe;
- the edge weakens materially when leveraged/inverse ETFs are excluded;
- the best readout is a narrow WF diagnostic, not a full honest validation stack.

Closure decision: stop this branch. More local parameter sweeps without a new
pre-registered hypothesis and accumulated trial-accounting validation would be
data-mining risk `[advances_fin_ml, p.208-211]`. A future restart must be a new
ETF-specific study with explicit leveraged-ETF policy, PBO/DSR/bootstrap,
costs/taxes, and point-in-time ETF-universe treatment.
