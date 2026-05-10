# Weekly Momentum Study Report

## Scope

This study tests weekly cross-sectional momentum on current S&P 500 constituents from the Tiingo cache. Signals rank adjusted-close appreciation over the configured lookback; execution uses the honest daily-bar timing model: Thursday signal, Friday sell, Monday buy. Momentum ranking follows `[stocks_on_the_move, p.60]`; the SPY/SMA market filter follows trend-risk filtering rationale `[stocks_on_the_move, p.66-67, p.81]`.

## Variants

| variant | lookback | top_k | market filter | CAGR | MDD | Sharpe | Sortino | Calmar | Vol | VaR 5% | worst day |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline_top1_cash` | 4 | 1 | none | 13.38% | -90.77% | 0.503 | 0.773 | 0.147 | 59.50% | 5.24% | -28.17% |
| `short_mom_top5_sma100` | 4 | 5 | SPY>SMA100 | 26.76% | -48.42% | 1.069 | 1.635 | 0.553 | 25.13% | 2.26% | -13.45% |
| `aggressive_lb60_k3_sma200` | 60 | 3 | SPY>SMA200 | 47.43% | -48.30% | 1.244 | 1.948 | 0.982 | 36.53% | 3.41% | -13.25% |
| `balanced_lb60_k10_sma100` | 60 | 10 | SPY>SMA100 | 28.12% | -33.61% | 1.154 | 1.715 | 0.837 | 23.96% | 2.37% | -11.60% |

SPY over the aligned full window: CAGR 14.03%, MDD -33.70%, Sharpe 0.853.

## Subperiod Robustness

| variant | period | strategy CAGR | SPY CAGR | strategy MDD | SPY MDD | strategy Sharpe | SPY Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|
| `baseline_top1_cash` | 2014-2019 | 35.48% | 11.90% | -47.79% | -19.34% | 0.924 | 0.925 |
| `baseline_top1_cash` | 2014-2020 | 40.04% | 12.79% | -47.79% | -33.70% | 0.905 | 0.776 |
| `baseline_top1_cash` | 2021-2026 | -16.95% | 14.05% | -90.77% | -24.50% | 0.064 | 0.858 |
| `baseline_top1_cash` | 2022-2026 | -30.77% | 10.84% | -90.35% | -24.50% | -0.151 | 0.667 |
| `short_mom_top5_sma100` | 2014-2019 | 13.31% | 11.90% | -33.26% | -19.34% | 0.756 | 0.925 |
| `short_mom_top5_sma100` | 2014-2020 | 20.70% | 12.79% | -33.26% | -33.70% | 0.944 | 0.776 |
| `short_mom_top5_sma100` | 2021-2026 | 37.58% | 14.05% | -48.42% | -24.50% | 1.249 | 0.858 |
| `short_mom_top5_sma100` | 2022-2026 | 35.00% | 10.84% | -43.84% | -24.50% | 1.189 | 0.667 |
| `aggressive_lb60_k3_sma200` | 2014-2019 | 17.58% | 11.90% | -48.30% | -19.34% | 0.727 | 0.925 |
| `aggressive_lb60_k3_sma200` | 2014-2020 | 22.64% | 12.79% | -48.30% | -33.70% | 0.837 | 0.776 |
| `aggressive_lb60_k3_sma200` | 2021-2026 | 93.60% | 14.05% | -38.11% | -24.50% | 1.689 | 0.858 |
| `aggressive_lb60_k3_sma200` | 2022-2026 | 98.43% | 10.84% | -36.31% | -24.50% | 1.711 | 0.667 |
| `balanced_lb60_k10_sma100` | 2014-2019 | 12.79% | 11.90% | -22.23% | -19.34% | 0.773 | 0.925 |
| `balanced_lb60_k10_sma100` | 2014-2020 | 15.83% | 12.79% | -22.23% | -33.70% | 0.856 | 0.776 |
| `balanced_lb60_k10_sma100` | 2021-2026 | 49.11% | 14.05% | -33.61% | -24.50% | 1.497 | 0.858 |
| `balanced_lb60_k10_sma100` | 2022-2026 | 51.28% | 10.84% | -31.42% | -24.50% | 1.523 | 0.667 |

## Candidate Verdict

- **Aggressive candidate:** `aggressive_lb60_k3_sma200` has the strongest full-period CAGR and Sharpe, but keeps equity-style crisis risk: MDD is still about -48%. It is a research lead, not a deployable strategy.
- **Balanced candidate:** `balanced_lb60_k10_sma100` has materially lower drawdown (-33.61%), Sharpe above SPY, and still beats SPY CAGR. It is the cleaner candidate for the next validation round.
- **Baseline top-1 is rejected as a lead:** post-2022 behavior and -90% drawdown are unacceptable despite strong early-period CAGR.

## Required Next Validation

- Replace current S&P 500 universe with point-in-time membership to reduce survivorship bias.
- Add realistic costs/slippage/taxes.
- Run proper parameter robustness: PBO/DSR/walk-forward/bootstrap per mandate `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.196-202]`.
- Check if the lb60/SMA filters are stable around nearby values instead of cherry-picked.

## Walk-Forward Diagnostic

Initial 3y-train / 1y-test walk-forward over 36 stock-universe configs is saved at
the original generated `studies/weekly_momentum/walk_forward/stocks/WALK_FORWARD_REPORT.md` bundle (not retained after final cleanup).

Result: walk-forward CAGR 14.94%, MDD -53.57%, Sharpe 0.642 versus SPY CAGR
14.69%, MDD -33.70%, Sharpe 0.835 over the same walk-forward test span.

Interpretation: the ex-post `lb60` candidates remain useful leads, but the
walk-forward selector did not yet produce a robust deployable rule. This is an
overfit/instability warning, not a pass.

## Controlled Sweep And Walk-Forward

The next controlled grid expanded the stock study to 200 configs per universe:
lookbacks `4,20,60,90,126`, `top_k` `3,5,10,20`, market filters
`none,sma100,sma200,ema100,ema200`, and `allow_negative_momentum` `0,1`.
The parameter family keeps the original weekly/monthly momentum premise
`[stocks_on_the_move, p.60]`; the walk-forward split remains the first overfit
diagnostic before CPCV/PBO/DSR/bootstrap `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.196-202]`.

| universe | sweep output | walk-forward CAGR | walk-forward MDD | walk-forward Sharpe | SPY CAGR | SPY MDD | SPY Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|
| current S&P 500 | generated bundle not retained | 42.30% | -50.84% | 1.216 | 14.69% | -33.70% | 0.835 |
| full stock cache | generated bundle not retained | 61.83% | -60.52% | 1.200 | 14.69% | -33.70% | 0.835 |

Reports:

- original generated `studies/weekly_momentum/walk_forward/stocks_sp500_controlled/WALK_FORWARD_REPORT.md` (not retained)
- original generated `studies/weekly_momentum/walk_forward/stocks_all_controlled/WALK_FORWARD_REPORT.md` (not retained)

Interpretation: the expanded walk-forward is much stronger than the initial
36-config diagnostic, but it is still **not deployable**. Both universes remain
biased/non-PIT, drawdowns are equity-crisis sized, and the full-cache result has
especially high coverage/listing-bias risk. The next hard validation step is
point-in-time universe reconstruction plus costs/slippage/taxes before
CPCV/PBO/DSR/bootstrap.

## Deploy Candidate Validation Round

Four research-only deploy candidates are frozen in `reports/DEPLOY_CANDIDATES.md`.
They were originally compared in a generated `deploy_candidates/CANDIDATE_VALIDATION_REPORT.md` bundle, which was not retained after final cleanup.
The fixed candidates test two specific parameter sets; the dynamic candidates
test the frozen walk-forward selector as a strategy process `[advances_fin_ml,
p.208-211]`.

| candidate | type | universe | CAGR | MDD | Sharpe | avg exposure | annualized turnover proxy | rolling 1y beat SPY | rolling 3y beat SPY |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `dynamic_wf_all_stocks` | dynamic WF | full stock cache | 61.83% | -60.52% | 1.200 | 87.84% | 28.41 | 81.23% | 100.00% |
| `dynamic_wf_sp500` | dynamic WF | current S&P 500 | 42.30% | -50.84% | 1.216 | 88.85% | 12.95 | 78.94% | 99.34% |
| `fixed_aggressive_sp500` | fixed | current S&P 500 | 47.43% | -48.30% | 1.244 | 77.22% | 14.85 | 75.70% | 98.60% |
| `fixed_balanced_sp500` | fixed | current S&P 500 | 28.12% | -33.61% | 1.154 | 76.81% | 13.57 | 68.67% | 84.42% |

Verdict: all four remain in the validation funnel, but none is deployable yet.
`dynamic_wf_all_stocks` is the most convex/high-return candidate and the highest
risk methodology-wise because the full cache is not a point-in-time investable
universe. `fixed_balanced_sp500` remains the cleanest drawdown candidate. Next
validation steps are costs/slippage/taxes, liquidity/listing diagnostics,
point-in-time universe work, and hard PBO/DSR/bootstrap `[advances_fin_ml,
p.196-202]`.

## Cost, Tax And Liquidity Stress

The candidate panel now applies one-way turnover cost stresses of `0/10/25/50`
bps, an annual DARF stress after `10` bps costs, and held-name ADV20 liquidity
diagnostics. Dollar-volume is used as the tradability proxy `[stocks_on_the_move,
p.81]`; DARF uses the repository's annual Lei 14.754/2023 engine.

| candidate | gross CAGR | 10 bps CAGR | 25 bps CAGR | 50 bps CAGR | 10 bps + DARF CAGR | median held ADV20 | held obs ADV20 < $5m |
|---|---:|---:|---:|---:|---:|---:|---:|
| `dynamic_wf_all_stocks` | 61.83% | 57.29% | 50.72% | 40.36% | 27.19% | $45.54m | 0.13% |
| `dynamic_wf_sp500` | 42.30% | 40.47% | 37.77% | 33.37% | 17.72% | $274.85m | 0.01% |
| `fixed_aggressive_sp500` | 47.43% | 45.25% | 42.05% | 36.87% | 16.64% | $291.71m | 0.01% |
| `fixed_balanced_sp500` | 28.12% | 26.39% | 23.84% | 19.70% | -3.38% | $262.00m | 0.02% |

Interpretation: cost stress does not kill gross edge, but annual realized-tax
drag is severe for the high-turnover fixed candidates and especially damages
`fixed_balanced_sp500`. Liquidity is not the first-order blocker at a $100k
reference AUM, including for `dynamic_wf_all_stocks`; the bigger unresolved risk
there remains non-PIT universe/listing bias and delisting survivorship.

## Anti-Overfit Gates And Plots

The original generated `deploy_candidates/CANDIDATE_VALIDATION_REPORT.md` bundle embedded, for every
candidate, a performance plot and a 1/3/5/10y rolling-CAGR plot versus SPY. The
same report also records first-pass anti-overfit gates: family PBO, DSR, OOS
window ratio and block-bootstrap lower CI. PBO is a grid/family test
`[advances_fin_ml, p.208-211]`; DSR/bootstrap follow the multiple-testing and
resampling controls `[advances_fin_ml, p.273-275]`, `[advances_fin_ml,
p.196-202]`.

The report also includes consolidated plots with all 4 candidates plus SPY:
normalized performance, candidate/SPY relative equity, and one combined
1/3/5/10y rolling-CAGR figure. The 10y rolling panel can be unavailable for the
combined candidate set because dynamic walk-forward candidates only begin after
the initial 3y train window and end at the last complete OOS block, leaving less
than 10 years of common live candidate history.

| candidate | family PBO | PBO pass | DSR p | DSR pass | OOS positive | OOS pass | bootstrap CAGR low 0.1% | bootstrap pass |
|---|---:|---|---:|---|---:|---|---:|---|
| `dynamic_wf_all_stocks` | 0.798 | no | 0.191 | no | 7/9 | yes | 0.30% | yes |
| `dynamic_wf_sp500` | 0.175 | yes | 0.191 | no | 7/9 | yes | 1.93% | yes |
| `fixed_aggressive_sp500` | 0.175 | yes | 0.046 | yes | 7/9 | yes | 8.15% | yes |
| `fixed_balanced_sp500` | 0.175 | yes | 0.092 | no | 7/9 | yes | 4.89% | yes |

Gate interpretation: `dynamic_wf_all_stocks` fails the PBO family gate despite
excellent raw performance, so it cannot be promoted without a new PIT/listing
robustness pass. `dynamic_wf_sp500` passes PBO/OOS/bootstrap but fails DSR after
the 200-trial penalty. `fixed_aggressive_sp500` is the only candidate passing
PBO context, DSR, OOS and bootstrap in this first gate pass, but it still has
large drawdown and tax/PIT caveats. `fixed_balanced_sp500` fails DSR and its
10 bps + DARF CAGR is negative, so it is downgraded operationally.

## Report Bundles

- `baseline_top1_cash`: `studies/weekly_momentum/results/stocks/lb4_sig3_sell1_sd0_k1_pos1_defcash_mf0/report.md`
- `short_mom_top5_sma100`: `studies/weekly_momentum/results/stocks/lb4_sig3_sell1_sd0_k5_pos1_defcash_mf100/report.md`
- `aggressive_lb60_k3_sma200`: `studies/weekly_momentum/results/stocks/lb60_sig3_sell1_sd0_k3_pos1_defcash_mf200/report.md`
- `balanced_lb60_k10_sma100`: `studies/weekly_momentum/results/stocks/lb60_sig3_sell1_sd0_k10_pos1_defcash_mf100/report.md`
