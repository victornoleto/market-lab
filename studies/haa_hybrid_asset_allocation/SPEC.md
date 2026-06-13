# HAA Hybrid Asset Allocation Study Spec

Status: active research-only scaffold, initiated 2026-06-13. No deployment,
paper-trade label or mandate change.

## Objective

Test Wouter Keller and Jan Willem Keuning's Hybrid Asset Allocation (HAA) rule
and three requested adaptations:

| Variant | Role | Preferred data |
|---|---|---|
| `only_etfs_canonical` | Reproduce the public HAA Balanced G8/T4 rule. | Testfol.io long-history synthetic ETF cache first; Tiingo real-inception as robustness. |
| `only_etfs_no_vnq` | Non-canonical Testfol.io fallback when `VNQSIM` is unavailable. | Testfol.io, with `BIL -> CASHX` proxy. |
| `only_stocks` | Adapt HAA's dual/canary momentum framework to stocks. | Local Tiingo subscription-era cache; final promotion would require survivorship-free/delisted data. |
| `stocks_plus_etfs` | Mixed offensive universe. | Local Tiingo cache for a consistent price source. |

## Rule

At each month-end close:

1. Compute momentum for each offensive, defensive and canary asset as the
   equal-weighted mean of 1, 3, 6 and 12-month total returns (`13612U`). This is
   the HAA-specific unweighted form, not the 13612W weighting used in VAA/DAA/BAA.
   Momentum ranking and absolute momentum are anchored by `[stocks_on_the_move,
   p.60]`.
2. If `TIP` momentum is non-positive, allocate 100% to the stronger defensive
   asset between `BIL` and `IEF`. The defensive sleeve and cost/turnover awareness
   follow `[systematic_trading, p.185-188]`.
3. If `TIP` momentum is positive, select the top `N` offensive assets by 13612U
   and allocate `1/N` to each. Default `N=4` follows the public HAA recipe. Monthly
   review cadence follows `[stocks_on_the_move, p.98-99]`.
4. If a selected offensive asset has non-positive momentum, replace that slot by
   the stronger defensive asset.
5. Apply month-end weights only to subsequent daily returns (`prev_weight × ret`),
   preventing look-ahead drift `[advances_fin_ml, p.31-34]`.

Primary external source: Keller & Keuning, `Dual and Canary Momentum with Rising
Yields/Inflation: Hybrid Asset Allocation`, SSRN `4346906`, plus public rule
summaries from TrendXplorer, Allocate Smartly and BestFolio.

## Data Policy

- Testfol.io is allowed for canonical ETF reproduction because HAA's published
  long-window evidence depends on pre-inception ETF/index proxy histories.
- Tiingo is mandatory for stock and mixed-universe tests in this repo. Do not
  silently fall back to yfinance for these variants; current-universe/yfinance
  stock tests are survivorship-biased `[advances_fin_ml, p.208-211]`.
- Because the Tiingo price cache appears lost, yfinance is allowed only with the
  explicit `--allow-biased-yfinance` flag. Those rows are screen-only and report
  `promotion_eligible=false`; they cannot support a winner or mandate change
  without survivorship-free/delisted validation `[advances_fin_ml, p.208-211]`.
- Testfol.io proxy aliases currently include `BIL -> CASHX` because `CASHX` is the
  available 3-month T-bill/cash proxy. `VNQSIM` is unavailable in the current
  cache/API sample, so `only_etfs_no_vnq` is labelled non-canonical.
- The current checkout has `data/tiingo/manifest.json`, but the price parquets
  are gitignored and must be restored to `data/tiingo/daily/prices/*.parquet`.
  Run `uv run python studies/haa_hybrid_asset_allocation/run.py --audit-only`.

## Validation

Any result above diagnostic status must report:

| Gate | Threshold | Citation |
|---|---|---|
| PBO | `< 0.5` over the declared variant matrix | `[advances_fin_ml, p.208-211]` |
| DSR | `p < 0.05` with honest `n_trials` | `[advances_fin_ml, p.273-275]` |
| Walk-forward | at least 6/8 positive OOS windows | `[testing_tuning, p.318-320]` |
| OOS | final 30% Sharpe positive | `[testing_tuning, p.327-335]` |
| FWD stress | post-2020 Sharpe positive | `[testing_tuning, p.327-335]` |
| Bootstrap | 99.9% CI low Sharpe > 0 | `[advances_fin_ml, p.196-202]` |
| Cross-implementation | vectorized vs holdings-loop CAGR delta <= 3pp | `[advances_fin_ml, p.31-34]` |

CAGR and MDD are tier/warning metrics under the mandate, not promotion gates.

## Initial Commands

```bash
uv run python studies/haa_hybrid_asset_allocation/run.py --audit-only
uv run python studies/haa_hybrid_asset_allocation/run.py --variant only_etfs_canonical
uv run python studies/haa_hybrid_asset_allocation/run.py --variant only_etfs_no_vnq
uv run python studies/haa_hybrid_asset_allocation/run.py --variant only_etfs_canonical --source yfinance --allow-biased-yfinance
uv run python studies/haa_hybrid_asset_allocation/run.py --variant only_stocks --source tiingo
uv run python studies/haa_hybrid_asset_allocation/run.py --variant only_stocks --source yfinance --allow-biased-yfinance --max-assets 20
uv run python studies/haa_hybrid_asset_allocation/run.py --variant stocks_plus_etfs --source tiingo
```

## Caveats

- `haa_bestfolio_no_qqq_seed` is intentionally labelled a seed, not a faithful
  reproduction: BestFolio's rendered public page says `9 offensive + 3 canary +
  2 defensive`, but does not expose the full offensive list. The implemented seed
  extends classic G8/T4 with `GLD` as a ninth broad diversifier until the exact
  variant definition is recovered.
- Stock variants are HAA-inspired adaptations, not the original HAA strategy.
- A good Tiingo result is still research-only until survivorship-free/delisted
  validation confirms it.
