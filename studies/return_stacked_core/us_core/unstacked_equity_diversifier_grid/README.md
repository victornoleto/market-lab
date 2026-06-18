# Unstacked Equity + Diversifier Grid

Status: research-only diagnostic. No deployment, paper-trade label or mandate
change.

This study tests the user's hypothesis that a portfolio can hold about `100%`
effective S&P 500 exposure through SSO/UPRO-like daily-reset LETF proxies and
allocate the leftover capital to unstacked diversifiers: cash, gold, long
Treasuries and managed futures.

The canonical runner is `run.py`. It downloads each Testfol.io asset/custom
expression separately, so each series keeps its own maximum history before the
local grid decides which scenario's common window applies.

Default scenarios:

- `kmlm_long`: `CASH / GOLD / ZROZ / KMLM`, common window starts at KMLM.
- `dbmf_2000`: `CASH / GOLD / ZROZ / DBMF`, common window starts at DBMF.
- `mf_blend_2000`: `CASH / GOLD / ZROZ / 70% DBMF + 30% KMLM`.
- `kmlm_dbmf_split_2000`: `CASH / GOLD / ZROZ / KMLM / DBMF`.

Method references: embedded LETF leverage follows the daily-reset leverage
premise and caveats `[leverage_for_the_long_run, p.13]`; fixed-weight monthly
rebalancing and implementation robustness are diagnostics, not proof of a winner
`[systematic_trading, p.185-188]`, `[testing_tuning, p.327-335]`; grid selection
is explicitly checked with PBO/WF diagnostics `[advances_fin_ml, p.208-211]`.

Run:

```bash
uv run python studies/return_stacked_core/us_core/unstacked_equity_diversifier_grid/run.py
```

Use `--force-download` only when refreshing Testfol.io data. The runner does not
need an access token for the public `/api/backtest` route.
