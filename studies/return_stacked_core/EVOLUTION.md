# Return-Stacked Core Evolution

Status: compact intellectual lineage for the consolidated RSC folder.

This report preserves the path to **RSC-US `35% GDE / 40% RSST / 25% ZROZ`**
and the related **RSC-Global** variant. It replaces the need to navigate the
old `b4-v2`, `static_spy_beater_portfolio`, `spy_beater_hunt`,
`spy_beater_hunt_v2`, `long_term_portfolio` and `global_factor_tilt_loop`
trees for decision context.

## Final State

| Item | Verdict |
|---|---|
| Current canonical core | RSC-US `35% GDE / 40% RSST / 25% ZROZ`. |
| Main interpretation | Defensive return-stacked SPY challenger. |
| Global branch | RSC-Global `20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ`. |
| Deployment status | Research-only; no mandate change. |
| Main caution | Discovery was search-heavy; do not resume broad optimization without a new pre-registered mechanism `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. |

## Phase 1 - Original SPY-Beater Hunt

The original `spy_beater_hunt` tried to find a long-term SPY-beating portfolio
through LRS, HFEA, vol targeting, static stacks, factor tilts, BTC satellites
and meta-ensembles.

| Finding | Preserved Result |
|---|---|
| Strict winner count | `0` under the original score/gate framing. |
| Meta-ensemble ceiling | Best strategy-level score reached `74`, below WINNER tier. |
| Old practical B4 branch | Old B4/B4 Conservative became a historical deploy-readiness pick before later corrections. |
| RSST correction | Corrected old B4: CAGR `11.00%`, MDD `-29.60%`, Sharpe `0.671`; L1 CEGB: CAGR `9.66%`, MDD `-25.43%`, Sharpe `0.696`. |
| BTC sleeve | `B4 + 5% BTC` was economically interesting in BTC-favorable windows, but was not a gate-equivalent core. |

The useful output was not a validated strategy. It was a map of what failed and
why: local timing/overlay variants could improve isolated windows, but did not
survive the robustness discipline required by the project.

Source reports:

- `history/source_reports/spy_beater_hunt_ITERATION_LEDGER.md`
- `history/source_reports/spy_beater_hunt_TOP_STRATEGIES.md`
- `history/source_reports/spy_beater_hunt_LIVE_STRATEGY_B4_BTC5.md`

## Phase 2 - Long-Term Portfolio Static Stack

The `long_term_portfolio` loop moved from broad tactical ideas toward static,
capital-efficient ETF stacks.

| Step | Candidate | Verdict |
|---|---|---|
| Iter 011 | `35% NTSX / 25% GDE / 40% KMLM` | Strong early static family; weight selection not robust enough. |
| Iter 023 | `25% NTSX / 25% GDE / 35% KMLM / 15% TLT` | TLT reduced MDD across datasets and became strongest pre-B4 static candidate. |
| Phase 1 sleeves | NTSD, AVUV, AVDV, SPMO, IDMO, AVEM | Only SPMO showed modest robust positive signal; global factor sleeves mostly failed. |
| Phase 2 | US stacked/factor/MF finalists | Confirmed RSST/stacked-MF as the axis worth preserving. |

Important lesson: international and factor additions were not automatically
better. The branch repeatedly showed that ex-US/factor sleeves could reduce
concentration, but often paid for it with weaker Sharpe or lower CAGR. The
surviving mechanism was return stacking plus diversifiers, not generic factor
tilting `[risk_parity, ch.5, p.10]`, `[ilmanen_expected_returns, ch.19]`.

Source reports:

- `history/old_b4/iter011_ntsx_gde_kmlm_static.md`
- `history/old_b4/iter023_tlt_sleeve.md`
- `history/source_reports/long_term_PHASE_1_WINNERS.md`
- `history/source_reports/long_term_PHASE_2_WINNERS.md`

## Phase 3 - Old B4 25/25/25/25

The old B4 formulation was:

```text
25% NTSX / 25% GDE / 25% RSST / 25% ZROZ
```

It mattered because it combined four capital-efficient or crisis-aware sleeves:
US efficient core, equity+gold, equity+managed futures and zero-coupon duration.

Preserved metrics from the later B4-v2 comparison:

| Portfolio | CAGR | MDD | Sharpe | Calmar | Terminal |
|---|---:|---:|---:|---:|---:|
| Old B4 `25/25/25/25` | `14.43%` | `-27.92%` | `1.018` | `0.517` | `174x` |
| RSC-US `35/40/25` | `15.70%` | `-29.94%` | `1.040` | `0.524` | `265x` |

The old B4 remains useful as lineage, not as the current champion. The current
core removed NTSX and concentrated the exposure into GDE/RSST/ZROZ because the
later static optimizer found better long-horizon compounding with only modestly
worse full-period drawdown.

The old B4 deep dive also preserved two non-canonical findings:

| Finding | Result | Current read |
|---|---|---|
| `BTGD 10%` | Sharpe `1.017` in a short window. | Implementation idea, not current core. |
| Global fork `70/30` | Sharpe `0.925` versus old B4 US-only `1.027`. | Diversification fork, not replacement. |
| Corrected `RSSX` | `100% SPY + 65% Gold + 35% BTC`. | Useful caveat for RSSX split; BTC sensitivity matters. |

Source report: `history/source_reports/legacy_b4_deep_dive.md`.

## Phase 4 - Static Optimizer And RSC-US Discovery

The former `static_spy_beater_portfolio` workbench was the direct discovery path
to the current core. It searched long-only, monthly rebalanced ETF portfolios in
5% weight units and used rolling equity dominance plus p10 robustness to avoid
selecting only average-window winners `[testing_tuning, p.327-335]`.

Final discovered core:

```text
35% GDESIM / 40% RSSTSIM / 25% ZROZSIM
```

Rejected alternatives:

| Candidate family | Best or example | Why rejected |
|---|---|---|
| Aggressive LETF/TMF barbell | `40% TQQQSIM / 60% TMFSIM`; `35% TQQQSIM / 50% TMFSIM / 15% RSSTSIM` | CAGR was high, but MDD was `-81%..-84%`. |
| Negative-cash stacked | `35 GDE / 40 RSST / 5 SPY / 45 ZROZ / -25 CASHX` | Attractive CAGR/Calmar, but external negative cash was operationally disallowed. |
| Levered-equity boosters | `5% QLD` or `5% TQQQ` variants | Bought too little extra CAGR for much worse drawdown. |
| Factor/momentum sleeves | `VBRSIM`, `MTUMSIM`, `EFVSIM` | Did not displace the `35/40/25` core. |
| Stacked-ETF expansion | CTAP/RSBT/RSIT/HOLD/MATE/ESBG/GDT/ALLW probes | No alternative sleeve made top-5 across seeds. |

Source report: `history/source_reports/b4_v2_discovery_lineage.md`.

## Phase 5 - Publication And Robustness Package

The former `b4-v2` package turned the discovered core into a publication-quality
research package with plots, series, Monte Carlo diagnostics and robustness
tables.

Key conclusion:

| Diagnostic | Result |
|---|---|
| Full-history edge | RSC-US outperformed SPY with materially lower MDD. |
| Modern-window caveat | Post-2010 CAGR edge narrows and can disappear for some start dates. |
| Regime behavior | Best in crisis/rates shocks; can lag in strong equity recoveries. |
| Drag stress | Survives moderate extra drag, but edge compresses. |
| Monte Carlo | Lower downside terminal wealth risk than SPY, but diagnostic only. |

Canonical assets:

- `us_core/REPORT.md`
- `us_core/plots/`
- `us_core/series/`
- `ROBUSTNESS_REPORT.md`
- `robustness_tables/`

## Phase 6 - RSC-Global Branch

The global branch asks whether the RSC concept can include developed ex-US and
some international exposure without abandoning the core sleeves.

Clean candidate:

```text
20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ
```

Approximate equity split is `~64% US / 36% international`.

| Portfolio | CAGR | MDD | Sharpe | Terminal | Read |
|---|---:|---:|---:|---:|---|
| `100% VT` | `8.77%` | `-58.35%` | `0.562` | `25.2x` | Passive global benchmark. |
| `66/34 VTI/VEA` | `9.88%` | `-56.92%` | `0.635` | `37.1x` | US/developed benchmark. |
| RSC-US | `14.30%` | `-31.66%` | `0.960` | `168.7x` | Higher-return anchor. |
| RSC-Global simple NTSD/RSIT | `13.10%` | `-34.35%` | `0.894` | `112.5x` | Diversification variant. |

Interpretation: RSC-Global is useful if geographic breadth matters. It is not a
replacement for RSC-US on absolute return.

Source assets:

- `global_variant/REPORT.md`
- `global_variant/plots/`
- `history/global_factor_tilt/`

## Phase 7 - Follow-On Hunted But Failed

The later `spy_beater_hunt_v2` was an autonomous attempt to beat SPY buy-and-hold
while preserving hard overfit gates: PBO, DSR, walk-forward, OOS, FWD,
bootstrap and cross-library checks `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

| Item | Result |
|---|---|
| Iterations | `10` |
| Cumulative trials | `20` |
| Winners | `0` |
| Best economic lead | `clenow_relmom_90d_3x_cash` |
| Best lead metrics | CAGR `22.12%`, MDD `-88.88%`, terminal/SPY `39.14x`, PBO `0.000`, DSR `0.00616`, WF `7/8`. |
| Binding failure | Bootstrap 99.9% lower-bound. |

Conclusion: the no-winner result reinforces the current RSC posture. There were
economic ideas, but they were not robust enough to replace the static core.

Source report: `history/source_reports/spy_beater_hunt_v2_STRATEGY_COMPARISON.md`.

## Phase 8 - Non-Core Satellite: B4 + evo02

The `70% B4 + 30% evo02` result is preserved because it was a meaningful
core-satellite experiment, but it is not part of the RSC static core.

| Portfolio | CAGR | MDD | Sharpe | XIRR | Status |
|---|---:|---:|---:|---:|---|
| `70% old B4 + 30% evo02` | `20.01%` | `-21.60%` | `1.2038` | `19.74%` | Research-only satellite. |
| `75% old B4 + 25% evo02` | `19.15%` | `-22.58%` | `1.1998` | `18.85%` | Conservative alternative. |
| `100% old B4` | `14.62%` | `-28.38%` | `1.0234` | `14.17%` | Baseline. |

The evo02 sleeve came from GA/repair logic and requires OOS/FWD/WF/bootstrap,
PBO and DSR validation before it can be treated as more than a satellite idea
`[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

Preserved assets: `history/b4_evo02_70_30/`.

## What Not To Reopen Without A New Hypothesis

Do not restart any of these as local parameter sweeps:

| Closed direction | Reason |
|---|---|
| More B4 local weight tweaks | Multiple-testing risk without new mechanism. |
| Factor sleeve substitutions | Already failed to displace RSC-US in relevant tests. |
| Simple global equity additions | Repeatedly reduced return/Sharpe versus US core. |
| LETF/TMF aggressive barbells | Drawdown too extreme for this static-core objective. |
| Old SPY-beater timing/overlay loops | No strict winner; robustness gates were binding. |
| Clenow/LRS/KAMA/seasonality v2 families | Economic near-misses failed bootstrap/OOS/FWD. |

Acceptable future work must be pre-registered, mechanism-distinct and cite the
economic rationale before testing.
