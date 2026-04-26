# `data/testfolio/` — local cache (gitignored)

Synthetic ETF history pulled from <https://testfol.io>. Files in this
directory are gitignored because (a) they can be large (~100 MB total)
and (b) the API requires a personal Bearer token. Regenerate locally
with the puller script.

## How to pull / refresh

```bash
# Get a fresh JWT from testfol.io DevTools (Network tab → backtest request),
# save it to:
echo "eyJ..." > .testfolio_token   # gitignored

# Pull individual tickers:
uv run python scripts/testfolio_pull.py BNDSIM IEFSIM VTSIM ...
# Or pull + refresh the parquet cache in one go:
uv run python scripts/testfolio_pull.py --refresh-cache BNDSIM IEFSIM
```

After pulling raw JSONs, `scripts/extract_testfolio_json.py` merges
them into `data/testfolio/cache/history.parquet` (also gitignored).

## Tickers expected by the loops

The strategy_hunt_loop and global_factor_tilt_loop require these
synthetic tickers to be present in the cache. If the parquet is missing
any, the relevant validators will skip the affected datasets.

### Tier 1 — required for strategy_hunt_loop long-window validation
| ticker | role | inception |
|---|---|---|
| SPYSIM | S&P 500 TR proxy | 1986+ |
| QQQSIM | NASDAQ-100 TR proxy | 1986+ |
| GLDSIM | LBMA gold proxy | 1986+ |
| ZROZSIM | 25y zero-coupon Treasury | 1986+ (true since 1962) |
| BNDSIM | Bloomberg Aggregate Bond (AGG analog) | 1986+ |
| IEFSIM | 7-10y Treasury | 1962+ |

### Tier 2 — required for global_factor_tilt_loop
| ticker | role | inception |
|---|---|---|
| VTSIM | VT (Total World) | 1970+ |
| VXUSSIM | VXUS (Total Intl) | 1970+ |
| VEASIM | VEA (Intl Developed) | 1970+ |
| VWOSIM | VWO (Emerging Markets) | 1994+ |
| VBRSIM | VBR (US Small-Cap Value, AVUV proxy) | 1926+ |

### Tier 3 — extras for future loops (not currently required)
- VTISIM (VTI, US Total Market, 1926+)
- VVSIM (VOO, US Large Cap, 1926+)
- MTUMSIM, USMVSIM (factor sleeves)
- DBMFSIM, KMLMSIM (managed futures)
- NTSDSIM, RSSBSIM, GDESIM (return-stacked)
- All XL\*SIM (sector ETFs)
- TBILL, EFFRX (cash / risk-free)
- INFLATION (CPI)
- FF3, FF5 (Fama-French factors)
- BTCSIM, ETHSIM (crypto)

Full ticker catalog: see testfol.io documentation.

## Token management

- File: `.testfolio_token` (project root, gitignored)
- Format: Supabase JWT, expires every few hours
- Refresh: open testfol.io in browser → F12 Network → trigger any
  backtest → copy `authorization: Bearer ...` value → overwrite
  `.testfolio_token`
- The `testfolio_pull.py` script reads this file at runtime
