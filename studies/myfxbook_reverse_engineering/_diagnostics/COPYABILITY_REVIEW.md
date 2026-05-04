# COPYABILITY_REVIEW — MyFxBook v4 Fase 3b

Diagnostic governance report only. No paper/live, no real AutoTrade, no monitor/cron, no capital allocation, and no Plano A reactivation.

## Verdict

`TOO_MANY_PASS_REQUIRES_HUMAN_GOVERNANCE`

Task 029 evaluated the frozen universe of 21 audit-only `pre_screen_go_systems` and produced 4 `PASS` systems plus 17 `STOP`. The pre-registered plan expected a diagnostic shortlist of 1-3; therefore this result cannot be converted automatically into top-3, monitor setup, paper/live, or real AutoTrade.

The 21 systems had already passed track-record pre-screen evidence via MCPT and PSR, but those tests only support historical plausibility of each EA's own series. MCPT remains a pre-screen against random sequencing `[evidence_based_ta, p.325-328]`; PSR remains the correct object for a single vendor return series `[advances_fin_ml, p.260-263]`. Neither test authorizes deployment.

## Resumo Dos 4 PASS

| system_id | copyability_score | strengths | caveats |
|---|---:|---|---|
| `8577442` | 0.958673 | Real account; 5 symbols with positive PnL; 0.966 positive-month ratio; 13 median trades/month; 3.5% modeled cost drag; top symbol share 42.2%. | Max no-trade gap 86.8 days is close to the 90-day gate; recent drawdown is 38.9% of historical max; still only diagnostic. |
| `1152318` | 0.940662 | Real account; 2 symbols with positive PnL; long track record from 2015 to 2021; 22.5 median trades/month; 6.1% modeled cost drag; top symbol share 52.7%. | Track record appears stale with last close in 2021; Fase 1 diagnostics show `mandate_24_pass=false`; still only diagnostic. |
| `10067081` | 0.896255 | Real account; 6 symbols with positive PnL; 1.000 positive-month ratio; recent activity through 2026-04; top symbol share 41.5%. | Very high frequency at 294 median trades/month is near the 300 upper gate; average net pips/trade is only 5.0, so copy cost/slippage is a central fragility `[systematic_trading, p.182-197]`. |
| `10062918` | 0.892554 | Real account; 2 symbols with positive PnL; 0.900 positive-month ratio; 17.5 median trades/month; 5.5% modeled cost drag; average net pips/trade 18.8. | Top symbol share is 57.5%, the highest among PASS; Fase 1 diagnostics show `mandate_24_pass=false`; still only diagnostic. |

These rows are not a recommendation order. The score column reports task 029 output only; selecting among the 4 PASS systems would itself be an additional selection procedure.

## Risco De Selecao

Choosing a top-N from 21 EAs after observing the scoreboard creates ranking-selection and multiple-testing risk. DSR is the relevant warning framework when many candidates are compared or selected ex post, because the best-looking record can be a product of the search process rather than a robust edge `[advances_fin_ml, p.273-275]`.

The same issue appears as data-mining risk: once the 4 PASS identities and scores are visible, adding a new tie-breaker, relaxing a gate, or emphasizing a favorable metric would contaminate the study unless that rule is separately pre-registered before use `[evidence_based_ta, p.247-260]`.

Therefore task 030 does not choose top-3, top-1, or any operational candidate. It only records that the frozen rules produced 4 PASS where the governance envelope expected 1-3.

## Concentracao E Operacional

The main STOP reason across the 17 rejected systems was `single_asset_pnl_share_gt_80pct`, affecting 13 systems. This matters because the mandate does not accept a single-asset winner as a reactivation thesis, and because symbol-specific history can overstate generality.

The PASS set is better diversified than the STOP set, but not uniformly low-risk:

| system_id | top symbol | top symbol PnL share | n positive symbols | live | median monthly trades | cost drag | avg net pips/trade |
|---|---|---:|---:|---:|---:|---:|---:|
| `8577442` | `USDCAD` | 0.422 | 5 | True | 13.0 | 0.035 | 28.502 |
| `1152318` | `AUDUSD` | 0.527 | 2 | True | 22.5 | 0.061 | 9.142 |
| `10067081` | `USDJPY` | 0.415 | 6 | True | 294.0 | 0.146 | 5.001 |
| `10062918` | `EURCHF` | 0.575 | 2 | True | 17.5 | 0.055 | 18.843 |

Operational caveats:

- All 4 PASS are Real accounts, so the task 029 `demo_warning` penalty is not the binding issue.
- `10067081` is the clearest cost/slippage concern because it trades near the upper frequency gate and has low net pips per trade; short-strategy copying can lose edge to spread and slippage `[systematic_trading, p.182-197]`.
- `8577442` is close to the operational no-trade gap gate, so a future read-only monitor plan would need to pre-register how to handle inactivity before observing new trades.
- `1152318` has a stale last close in the historical data, so any future decision must confirm whether the system is still operational before treating it as copyable.
- `10062918` passes the single-asset hard gate but remains more concentrated than the other PASS systems.

## Opcoes De Governanca

Allowed human choices after this report:

1. Stop v4 Fase 3b here and keep only the diagnostic record. This is the most conservative option and preserves Plano C 100%.
2. Authorize a new pre-registered tie-breaker task. The tie-breaker must be specified before it reads any new ranking outcome, must not alter task 029 thresholds, and must explicitly address multiple-testing/data-mining risk `[advances_fin_ml, p.273-275]` `[evidence_based_ta, p.247-260]`.
3. Authorize a future read-only/manual monitor plan. That plan may define how to observe new public MyFxBook trades, but must remain diagnostic and must not schedule cron, execute orders, connect real AutoTrade, or start paper/live without a separate human decision.

Not allowed from this session:

- Automatically select the top-3 from task 029.
- Treat `8577442`, `1152318`, `10067081`, or `10062918` as operational recommendations.
- Relax single-asset, cost, stability, or frequency thresholds after seeing the scoreboard.

## Guardrails

- Capital remains 100% Plano C; Plano A remains DORMANT.
- No paper/live account is authorized.
- No real AutoTrade is authorized.
- No monitor, cron, broker integration, or order execution was started.
- No thresholds or weights from `FILTER_COPY_PLAN.md` were changed.
- No `frozen_rules/`, `docs/investment-mandate.md`, or other hunts were modified.
- No PnL future, oracle, or cherry-pick was used.
- No single-asset winner is accepted as a deployment thesis.
