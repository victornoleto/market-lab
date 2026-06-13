# HAA Hybrid Asset Allocation Study Report

Status: research-only. No deployment, paper-trade label or mandate change.

## Verdict

Screen-only FAIL: all result rows use yfinance, so `promotion_eligible=false`; current-universe yfinance data cannot support a winner without PIT/delisted validation [advances_fin_ml, p.208-211].

## Method

HAA ranks offensive assets by equal-weighted 1/3/6/12-month momentum, uses TIP as a canary, and replaces risk-off slots with the stronger defensive asset between BIL and IEF. Momentum and monthly cadence are anchored in `[stocks_on_the_move, p.60]` and `[stocks_on_the_move, p.98-99]`; validation gates follow `[advances_fin_ml, p.208-211]` and `[advances_fin_ml, p.273-275]`.

## Results

| Config | Source | Window | CAGR | MDD | Sharpe | Calmar | Gates ex-PBO | Promotion eligible |
|---|---|---|---|---|---|---|---|---|
| haa_balanced_g8_t4_yf | yfinance | 2004-12-31..2026-06-12 | 9.39% | -15.19% | 0.858 | 0.618 | 6/6 | False |
| haa_balanced_g8_t4_no_vnq_proxy_yf | yfinance | 2004-12-31..2026-06-12 | 8.61% | -14.95% | 0.814 | 0.576 | 6/6 | False |
| haa_bestfolio_no_qqq_seed_yf | yfinance | 2004-12-31..2026-06-12 | 9.76% | -13.97% | 0.868 | 0.699 | 6/6 | False |
| haa_only_etfs_yf_top4 | yfinance | 2004-12-31..2026-06-12 | 12.41% | -30.05% | 0.797 | 0.413 | 6/6 | False |
| haa_only_etfs_yf_top10 | yfinance | 2004-12-31..2026-06-12 | 8.52% | -17.77% | 0.796 | 0.480 | 6/6 | False |
| haa_only_etfs_yf_top20 | yfinance | 2004-12-31..2026-06-12 | 2.77% | -12.15% | 0.518 | 0.228 | 4/6 | False |
| haa_only_stocks_yf_top4_available18 | yfinance | 2004-12-31..2026-06-12 | 15.58% | -51.01% | 0.688 | 0.305 | 5/6 | False |
| haa_only_stocks_yf_top10_available18 | yfinance | 2004-12-31..2026-06-12 | 14.59% | -30.86% | 0.899 | 0.473 | 6/6 | False |
| haa_stocks_plus_etfs_yf_top4 | yfinance | 2004-12-31..2026-06-12 | 13.28% | -47.19% | 0.710 | 0.281 | 5/6 | False |
| haa_stocks_plus_etfs_yf_top10 | yfinance | 2004-12-31..2026-06-12 | 12.12% | -25.18% | 0.928 | 0.482 | 6/6 | False |
| haa_stocks_plus_etfs_yf_top20 | yfinance | 2004-12-31..2026-06-12 | 2.77% | -12.15% | 0.518 | 0.228 | 4/6 | False |

## PBO

| Item | Value |
|---|---|
| pbo | 0.6309523809523809 |
| n_combinations | 252 |
| pass_gate | False |

## Errors / Data Blocks

- haa_only_stocks_yf_top20 (yfinance): only 18 offensive yfinance assets remain after missing ['ABMD', 'ACAS']; top_n=20

## Caveats

- Testfol.io ETF histories are synthetic/modelled before ETF inception.
- `haa_balanced_g8_t4_no_vnq_proxy` is not canonical; it exists only because VNQSIM is unavailable in the current Testfol.io cache/API sample.
- Tiingo stock/ETF tests require restored `data/tiingo/daily/prices/*.parquet`; the manifest alone is not enough.
- yfinance runs require `--allow-biased-yfinance` and are current-universe/survivorship-biased screens only; `promotion_eligible=false` for those rows.
- Stock universes still need survivorship-free/delisted validation before any promotion claim.
