# Reddit Leveraged Portfolios vs RSC-US

Status: research-only comparison. This does not authorize deployment and does not change the maintenance-mode mandate `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Execution

The 5 Testfol.io payloads provided by the user were executed on 2026-06-05 without `authorization` and with `sleep 6` between calls to avoid rate-limit/403 risk.

| Request | HTTP | Raw response |
|---|---:|---|
| Backtest 1 | 200 | `raw/backtest_01.json` |
| Backtest 2 | 200 | `raw/backtest_02.json` |
| Backtest 3 | 200 | `raw/backtest_03.json` |
| Backtest 4 | 200 | `raw/backtest_04.json` |
| Backtest 5 | 200 | `raw/backtest_05.json` |

Saved artifacts:

| File | Purpose |
|---|---|
| `payloads/backtest_01.json`..`payloads/backtest_05.json` | Sanitized request bodies, no Bearer token. |
| `raw/backtest_01.json`..`raw/backtest_05.json` | Full Testfol.io API responses. |
| `derived/reddit_portfolio_instances.csv` | All 19 portfolio instances from the 5 calls. |
| `derived/reddit_unique_portfolios.csv` | 13 deduplicated portfolios. |
| `derived/comparison_common_1988.csv` | Derived equity-curve comparison vs RSC full-history series. |
| `derived/comparison_post2010.csv` | Derived equity-curve comparison vs RSC implementation series. |

Deduplication result:

| Portfolio | Occurrences |
|---|---:|
| SPY buy-hold | 3 |
| Reddit v2 SPY-3x stack, yearly | 4 |
| Reddit mine QQQ/TLT/GLD 3x, yearly | 2 |
| Other variants | 1 each |

## Headline

The best raw Reddit result is the 4-3-2-1 2x/margin portfolio, but it uses explicit borrowing via `CASHX?UE=1: -100`, so it is not a plain ETF-only portfolio. It requires margin, futures, swaps, or a return-stacked approximation. This is not equivalent to buying normal ETFs, and cost/financing sensitivity is mandatory before treating it as implementable `[systematic_trading, p.185-188]`.

The best high-return Reddit result without explicit negative cash is the "mine" portfolio from Backtest 2/3. It slightly beats canonical RSC-US on full-window CAGR/MDD/Calmar, but it relies on long-history synthetic 3x sleeves for QQQ, TLT and Gold. The Gold 3x sleeve is especially implementation-problematic because there is no clean long-lived 3x gold ETF equivalent; leverage decay and real-inception tracking need independent validation `[leverage_for_the_long_run, p.21]`.

Final decision for this repository: RSC-US `35% GDE / 40% RSST / 25% ZROZ` remains the better final anchor because it is close on full-history metrics, wins the practical post-2010 comparison against the Reddit "mine" portfolio, and is structurally aligned with the return-stacked implementation thesis rather than requiring raw margin or hard-to-source 3x sleeves `[risk_parity, p.80-81]`, `[testing_tuning, p.327-335]`.

## Raw Testfol.io Ranking

Window reported by Testfol.io: `1987-12-31..2026-06-05`, constrained by managed-futures simulations.

| Rank | Portfolio | CAGR | MDD | Calmar | Terminal | Reading |
|---:|---|---:|---:|---:|---:|---|
| 1 | 4-3-2-1 2x margin quarterly | 17.17% | -27.98% | 0.614 | 441.5x | Best raw theoretical result, but uses explicit borrowing. |
| 2 | Reddit mine QQQ/TLT/GLD 3x yearly | 16.11% | -27.65% | 0.583 | 311.4x | Best non-negative-cash Reddit lead, but synthetic 3x implementation caveat. |
| 3 | Reddit v2 SPY-3x stack yearly | 15.33% | -62.31% | 0.246 | 240.3x | High return, poor drawdown-adjusted quality. |
| 4 | SPY 2x buy-hold | 15.13% | -88.27% | 0.171 | 224.7x | Confirms unmanaged leverage is fragile. |
| 5 | Reddit v2 SPY-3x stack quarterly | 14.78% | -70.33% | 0.210 | 199.6x | Rebalance frequency does not rescue v2. |
| 13 | 4-3-2-1 unlevered quarterly | 10.60% | -15.85% | 0.669 | 47.9x | Best low-drawdown profile, but not a growth replacement. |

The v2 family is the least attractive group for our objective. It can show acceptable CAGR, especially post-2010, but full-window drawdowns in the `-62%..-85%` range dominate the analysis. CAGR and MDD are not hard gates in this repo, but these are still warning-tier diagnostics and the family has no validation evidence beyond a Reddit/Testfol.io parameter comparison `[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.208-211]`.

## Full-Window Comparison vs RSC

The derived comparison below uses equity curves from the Reddit responses and the saved RSC full-history series. The RSC full-equity series currently ends at `2026-04-17`, while the newer `metrics.csv` has RSC core through `2026-05-21`; the difference is small and does not change the ranking.

| Portfolio | Window | CAGR | MDD | Calmar | Terminal | Note |
|---|---|---:|---:|---:|---:|---|
| 4-3-2-1 unlevered | 1988-01-04..2026-05-21 | 10.62% | -15.85% | 0.670 | 48.1x | Highest Calmar, low-return defensive portfolio. |
| 4-3-2-1 2x margin | 1988-01-04..2026-05-21 | 17.21% | -27.98% | 0.615 | 442.5x | Best raw growth/risk mix, but margin-only. |
| Reddit mine QQQ/TLT/GLD 3x | 1988-01-04..2026-05-21 | 16.16% | -27.65% | 0.584 | 313.7x | Best Reddit non-negative-cash lead. |
| RSC-US 35/40/25 | 1988-01-04..2026-04-17 | 15.65% | -29.94% | 0.523 | 261.3x | Current implementable anchor. |
| B4 original 25/25/25/25 | 1988-01-04..2026-04-17 | 14.21% | -28.14% | 0.505 | 161.9x | Historical predecessor. |
| Reddit v2 SPY-3x yearly | 1988-01-04..2026-05-21 | 15.27% | -62.31% | 0.245 | 233.8x | Drawdown too severe for the return. |
| SPY buy-hold | 1988-01-04..2026-05-21 | 11.45% | -55.14% | 0.208 | 64.2x | Benchmark. |

Using the official `metrics.csv` row instead of the saved full-equity series, RSC-US `35/40/25` is `15.72%` CAGR, `-29.94%` MDD and `270.7x` terminal through `2026-05-21`. That still leaves Reddit mine slightly ahead on raw full-window CAGR and MDD, but the margin 4-3-2-1 remains the only Reddit portfolio with a large full-window terminal edge over RSC.

## Post-2010 Practical Comparison

The post-2010 window is important because it overlaps more with real ETF implementation and with the current RSC implementation table. It also reduces the weight of simulated pre-inception leveraged sleeves, although it does not remove all synthetic assumptions.

| Portfolio | Window | CAGR | MDD | Calmar | Terminal | Note |
|---|---|---:|---:|---:|---:|---|
| 4-3-2-1 unlevered | 2010-10-18..2026-05-21 | 8.56% | -11.20% | 0.764 | 3.6x | Defensive, but sacrifices too much growth. |
| RSC-US 35/40/25 | 2010-10-18..2026-05-21 | 14.72% | -21.46% | 0.686 | 8.5x | Beats Reddit mine on Calmar with similar terminal wealth. |
| RSC 17.5% RSSX + MF split | 2010-10-18..2026-05-21 | 16.64% | -25.28% | 0.658 | 11.0x | Stronger RSC implementation variant, with BTC proxy caveat. |
| RSC 10% RSSX + MF split | 2010-10-18..2026-05-21 | 15.97% | -24.28% | 0.658 | 10.1x | Cleaner optional enhancement than Reddit mine. |
| 4-3-2-1 2x margin | 2010-10-18..2026-05-21 | 15.22% | -25.65% | 0.593 | 9.1x | Still good, but loses to RSC variants on Calmar. |
| Reddit mine QQQ/TLT/GLD 3x | 2010-10-18..2026-05-21 | 15.02% | -26.30% | 0.571 | 8.9x | No longer dominates RSC. |
| Reddit v2 SPY-3x quarterly | 2010-10-18..2026-05-21 | 21.04% | -42.95% | 0.490 | 19.6x | Performance-first, materially worse drawdown-adjusted. |
| SPY buy-hold | 2010-10-18..2026-05-21 | 14.63% | -33.69% | 0.434 | 8.4x | Benchmark. |

This is the decisive table for implementation. Reddit mine is attractive in the 1988+ synthetic history, but the RSC core is better post-2010 on drawdown-adjusted return, and the RSC RSSX variants offer higher CAGR than mine while retaining a cleaner return-stacked framing. RSSX remains optional because its BTC sleeve must be treated conservatively, as already documented in the RSC report `[testing_tuning, p.327-335]`.

## Portfolio Structure Notes

Effective exposure matters more than nominal weights.

| Portfolio | Nominal construction | Approximate interpretation |
|---|---|---|
| RSC-US 35/40/25 | `35% GDE / 40% RSST / 25% ZROZ` | About `168%` positive exposure: US equity, gold, managed futures and long duration, packaged through return-stacked wrappers. |
| Reddit mine | `37.5% SCV / 12.5% QQQ 3x / 12.5% Gold 3x / 25% KMLM / 12.5% TLT 3x` | About `175%` positive exposure, but achieved via synthetic leveraged sleeves rather than return-stacked wrappers. |
| 4-3-2-1 2x | `200%` gross assets and `-100% CASHX` | Explicit margin portfolio. The user is correct: this is impractical as plain ETF-only unless approximated with margin, futures, swaps, or packaged return-stacked funds. |
| Reddit v2 | `50% SPY 3x` plus diversifiers | Large equity beta concentration; high CAGR in some windows but poor full-history drawdown. |

RSC and Reddit mine have similar gross exposure, but not the same implementation risk. RSC spends its capital budget on packaged stacks; Reddit mine spends it on levered QQQ, levered TLT and levered Gold. That difference is why the small full-window metric edge of Reddit mine is not enough to replace RSC as the final anchor `[leverage_for_the_long_run, p.21]`, `[systematic_trading, p.185-188]`.

## Verdict

Best raw/theoretical backtest: 4-3-2-1 2x margin quarterly.

Reason: highest high-return Calmar profile in the Reddit set, `17.17%` raw Testfol CAGR with `-27.98%` MDD. Rejected as final because it requires explicit leverage through negative cash and has no financing/cost/implementation validation.

Best Reddit lead worth preserving: Reddit mine QQQ/TLT/GLD 3x yearly.

Reason: best non-explicit-negative-cash Reddit portfolio, `16.11%` raw Testfol CAGR with `-27.65%` MDD, and it slightly beats RSC-US full-history metrics. Rejected as final because the edge is small and depends on synthetic 3x Gold/TLT/QQQ assumptions; post-2010 it loses to RSC-US on Calmar.

Best final for this repository: RSC-US `35% GDE / 40% RSST / 25% ZROZ`.

Reason: it remains the best implementable anchor after considering full-window metrics, post-2010 behavior, return-stacked construction, and mandate discipline. If a new branch is opened, the correct next experiment is not to adopt the Reddit portfolios directly, but to translate the 4-3-2-1/mine exposure idea into a return-stacked, no-margin implementation and validate it with the repository gates before any stronger claim `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
