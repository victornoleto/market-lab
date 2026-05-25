# SPEC - spy_sso_upro_replacement

## Mission

Find a low-maintenance SPY replacement based on `SPYSIM`, `SSOSIM` and `UPROSIM` that has materially higher long-run return than SPY while controlling drawdowns with diversifier sleeves. The preferred branch is static or low-turnover because it is easier to maintain and avoids frequent realized-tax events. Tactical/LRS variants are reserved for a second phase if static portfolios cannot satisfy rolling robustness.

This is research-only. It does not authorize capital allocation and does not override maintenance mode.

## Main Question

Can a static or low-turnover mix of S&P 500 LETFs and diversifiers beat SPY in at least about 90% of long rolling windows while avoiding intolerable drawdowns?

The word "always" is intentionally treated as probabilistic. The primary robustness target is high rolling hit rate, not literal future guarantee `[testing_tuning, p.327-335]`.

## Data Universe

Primary Testfol.io cache assets:

| Asset | Role |
|---|---|
| `SPYSIM` | 1x S&P 500 baseline |
| `SSOSIM` | 2x S&P 500 LETF proxy |
| `UPROSIM` | 3x S&P 500 LETF proxy |
| `ZROZSIM` | zero-coupon long Treasury convexity |
| `GLDSIM` | gold diversifier |
| `IEFSIM` | intermediate Treasury ballast |
| `CASHX` | cash / dry powder |

Secondary diagnostics may include `QQQSIM`, `QLDSIM`, `TQQQSIM`, `XLKSIM`, `IWMSIM`, `DIA` and `VIXSIM`, but the initial thesis is specifically SPY/SSO/UPRO as the return engine.

## Portfolio Rules

- Long-only.
- Weights in 5% increments.
- Weights sum to 100%.
- No external margin or negative cash.
- Embedded ETF leverage is allowed only through explicit series such as `SSOSIM` and `UPROSIM` `[leverage_for_the_long_run, p.13]`.
- Initial search rebalances monthly; finalist diagnostics also test quarterly and annual rebalance cadence.

## Phase 1 - Static Grid

Run a full constrained static grid over:

`SPYSIM`, `SSOSIM`, `UPROSIM`, `ZROZSIM`, `GLDSIM`, `IEFSIM`, `CASHX`.

Initial constraints:

- Total S&P sleeve weight (`SPY + SSO + UPRO`) between 45% and 95%.
- `UPROSIM <= 55%`.
- `SSOSIM <= 80%`.
- Effective S&P exposure (`SPY + 2*SSO + 3*UPRO`) between 100% and 210%.
- At least 5% in a diversifier unless the candidate is `SPYSIM` benchmark.

## Metrics

Primary:

- Full-period CAGR vs SPY.
- Full-period max drawdown vs SPY.
- Rolling relative wealth hit rate vs SPY for 3y, 5y, 10y, 15y, 20y and 30y.
- Rolling p10 relative wealth vs SPY for the same horizons.
- Latest rolling 3y/5y/10y relative wealth vs SPY.

Secondary:

- Sharpe, Sortino and Calmar.
- Terminal wealth vs SPY.
- Rebalance cadence sensitivity: monthly, quarterly, annual.
- Named-regime stress: dot-com, GFC, Covid, 2022 rates shock and recent recovery.

## Success Targets

Preferred static target:

- Full-period CAGR > SPY.
- Minimum 10y+ rolling hit rate vs SPY >= 90%.
- 5y rolling hit rate reported as diagnostic, not initial hard gate.
- Full-period MDD no worse than SPY by more than 5pp, or absolute MDD better than -60%.
- Latest 5y and 10y relative wealth disclosed explicitly.

Strict target, if possible:

- Minimum 5y+ rolling hit rate vs SPY >= 90%.
- Full-period MDD no worse than SPY.

## Objective Pivot - Equity Dominance

After Phase 1/1b, the conservative drawdown-aware objective mostly selected
`~90% SPY + small leverage tilt` portfolios. That is a valid answer to a conservative
SPY-replacement question, but it is not the intended active/leverage question.

The follow-on objective ranks candidates by benchmark-relative equity:

- Primary curve: `portfolio_equity / SPY_equity`.
- Full-period MDD is diagnostic only, not a hard gate.
- A candidate may have worse absolute MDD than SPY if its relative equity remains
  above benchmark equity after a long warmup.
- `SPYSIM`/`SSOSIM`/`UPROSIM` are no longer optimized as a redundant free mix.
  Instead, an explicit target-leverage ladder maps adjacent ETFs only:
  `1x-2x = SPY/SSO`, `2x-3x = SSO/UPRO` `[leverage_for_the_long_run, p.13]`.
- Tactical SMA variants are allowed as active leverage candidates, with lagged
  signals to avoid same-close lookahead `[testing_tuning, p.327-335]`.

## Phase 2 - Low-Turnover Tactical If Needed

If static portfolios fail the preferred target, test monthly or quarterly LRS-style variants:

- Risk-on: explicit target leverage from `SSOSIM`/`UPROSIM` when lagged SPY is above its SMA.
- Risk-off: `ZROZSIM`, `GLDSIM`, `IEFSIM`, `CASHX` or simple baskets.
- Active update cadence: monthly or quarterly only; daily updates are excluded as non-operational.
- Static rebalance cadence: monthly, quarterly or annual.
- Explicit tax/turnover diagnostics required using the repository annual DARF model.

This follows the leverage-for-the-long-run premise that leverage plus a trend/risk-off rule can improve long-horizon LETF behavior, but it must be validated separately `[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.208-211]`.

## Practical Taxed Selection

The practical rerun excludes daily rebalance/update, models Brazil's annual 15% DARF through `AnnualDarfEngine`, and compares after-tax portfolio equity against after-tax SPY equity. The cadence mask is audited by event count: monthly `698`, quarterly `233`, annual `59` over the 1968-2026 common window.

Results:

- Active grid: `280` candidates, `3` practical after-tax dominance passes.
- Static grid: `567` candidates, `0` practical after-tax dominance passes.
- Best active: `SMA300 L2.75 off 60 ZROZ / 40 GLD monthly`, after-tax CAGR `16.76%`, MDD `-73.74%`, terminal `23.75x` vs after-tax SPY, min relative equity after 10y `1.28x`, 10y+ hit `92.0%`.
- Best static: `static L3.00 E60% GLD annual`, after-tax CAGR `13.11%`, MDD `-70.80%`, terminal `3.75x` vs after-tax SPY, min relative equity after 10y `0.68x`, 10y+ hit `53.1%`.

Verdict: active monthly risk-on/off is the only branch that currently passes the practical after-tax dominance definition. Static target-leverage portfolios can improve terminal wealth, but they do not maintain benchmark-relative equity dominance through adverse regimes. This is still selection, not validation or deployment `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`, `[leverage_for_the_long_run, p.13]`.

## Outputs

- `results/static_grid_summary.csv` - broad monthly grid triage.
- `results/static_exact_finalists.csv` - daily exact finalist diagnostics.
- `results/static_predefined_exact.csv` - daily exact diagnostics for named reference portfolios.
- `REPORT.md` - human-readable report and conclusion.
- `results/phase1b_fine_local_summary.csv` - 1% local-grid monthly triage around the lead family.
- `results/phase1b_exact_finalists.csv` - daily exact diagnostics for Phase 1b finalists.
- `results/phase1b_drag_stress.csv` - conservative annual drag stress for exact preferred finalists.
- `results/phase1b_rolling_drawdown.csv` - rolling daily drawdown diagnostics for leading finalists.
- `PHASE1B_REPORT.md` - focused robustness report and conclusion.
- `results/equity_dominance_candidates.csv` - explicit-leverage static and tactical candidates ranked by SPY-relative equity dominance.
- `EQUITY_DOMINANCE_REPORT.md` - objective-pivot report and conclusion.
- `results/practical_taxed_candidates.csv` - monthly/quarterly active and monthly/quarterly/annual static candidates ranked after annual DARF.
- `PRACTICAL_TAXED_REPORT.md` - practical no-daily, after-tax active-vs-static verdict.
