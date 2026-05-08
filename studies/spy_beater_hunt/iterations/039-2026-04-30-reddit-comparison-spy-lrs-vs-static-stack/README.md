# Iter 039 — Reddit r/LETFs comparison post

Reddit post comparing SPY 1× vs Gayed 200d-SMA LRS vs static capital-efficient stacks. Uses our internal lib (`spy_beater_hunt.run_iter`) for the headline backtest AND optionally pulls testfol.io results via `fetch_testfolio.py` for "replicate this in your browser" plots that match the lingua franca of r/LETFs.

## Files

| File | Source | Purpose |
|---|---|---|
| `backtest.py` + `verdict.json` + `results.json` | internal lib | iter framework run — 7-gate anti-overfit + per-config metrics |
| `reddit_plot_*.png` | internal lib | 4 PNGs from our backtest output |
| `final_report.md` | internal lib | iter framework summary |
| `REDDIT_POST.md` | hand-written | Reddit post text (English, ready to publish) |
| `fetch_testfolio.py` | this folder | POSTs 7 buy-hold + 2 LRS to testfol.io API |
| `plot_post.py` | this folder | regenerates 4 PNGs (`testfolio_*.png`) from testfolio responses |
| `testfolio_data/` | gitignored | testfolio API responses (token-derived) |

## Run testfolio comparison plots

```bash
# 1) Get fresh JWT from testfol.io (token expires ~1h after browser login)
#    Open testfol.io -> log in -> DevTools (F12) -> Network tab
#    -> run any backtest -> click /api/backtest request
#    -> Headers -> Request Headers -> copy value after 'authorization: Bearer '

export TESTFOLIO_TOKEN='eyJhbGc...'

# 2) Fetch (3 API calls — buy-hold batch + 2 LRS tactical)
python studies/spy_beater_hunt/iterations/039-*/fetch_testfolio.py

# 3) Plot + metrics summary
python studies/spy_beater_hunt/iterations/039-*/plot_post.py
```

Step 3 stdout prints a markdown table with `cagr / mdd / sharpe / sortino / std / end_val` for all 9 portfolios — paste into `REDDIT_POST.md` if testfolio numbers diverge from our internal lib's verdict.

## Portfolios (must match REDDIT_POST.md contenders table)

| Slug | Allocation | Role |
|---|---|---|
| `spy_1x` | 100% SPY (no rebal) | Benchmark |
| `popular_50_25_25` | 50/25/25 SSO/GLD/ZROZ | Popular r/LETFs reference |
| `l1_sleeping_pills` | 40/25/17.5/17.5 NTSX/GDE/KMLM/TLT | Sleeping pills (CEGB literature) |
| `l2_bogleheads` | 67/11/11/11 NTSX/GLD/KMLM/ZROZ | Bogleheads template |
| `b4_conservative` | 25/25/25/25 NTSX/GDE/RSST/**ZROZ** | Conservative |
| `b2_balanced` | 30/30/30/10 NTSX/GDE/RSST/TMF | Balanced (TMF dose-down) |
| `t1_aggressive` | 20/35/25/20 NTSX/GDE/RSST/TMF | Aggressive (gold-heavy) |
| `lrs_sso_200sma` | SPY > 200d-SMA -> SSO else **IEF** | Gayed 2× tactical |
| `lrs_upro_200sma` | SPY > 200d-SMA -> UPRO else **IEF** | Gayed 3× tactical |

Buy-hold uses **annual** rebalance (REDDIT_POST.md spec). LRS uses daily. Numbers are gross of taxes.

## Side note (Inter Internacional)

`b4_conservative` and `l2_bogleheads` use ZROZ (PIMCO 25+Y Zero Coupon Treasury). Less common than TLT — verify availability at Inter Internacional catalog before adopting personally for Plano B. Not a blocker for the Reddit post (US-focused audience).
