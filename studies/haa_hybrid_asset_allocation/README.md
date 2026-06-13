# HAA Hybrid Asset Allocation

Research-only study for Keller/Keuning Hybrid Asset Allocation and the requested
`only_stocks`, `only_etfs`, and `stocks_plus_etfs` adaptations.

Canonical spec: `SPEC.md`.

Current verdict: **screen-only FAIL**. The consolidated yfinance screen is useful
diagnostically, but every yfinance row is `promotion_eligible=false` and the panel
PBO failed (`0.631`). Testfol.io long-history remains blocked until the missing
HAA sims are pulled into the local cache.

Latest yfinance screen highlights (`2026-06-13`, after-tax):

| Row | CAGR | MDD | Note |
|---|---:|---:|---|
| Canonical ETF | `9.39%` | `-15.19%` | Real-inception baseline. |
| ETF top4 | `12.41%` | `-30.05%` | Best ETF CAGR in screen. |
| Stocks top10 | `14.59%` | `-30.86%` | Best stock balance. |
| Mixed top10 | `12.12%` | `-25.18%` | Best mixed risk profile. |

Useful commands:

```bash
uv run python studies/haa_hybrid_asset_allocation/run.py --audit-only
uv run pytest tests/test_haa_hybrid_asset_allocation.py
uv run python studies/haa_hybrid_asset_allocation/run.py --variant only_etfs_canonical --source yfinance --allow-biased-yfinance
```

No output from this folder authorizes live trading or mandate changes. yfinance
rows are screen-only and explicitly ineligible for promotion `[advances_fin_ml,
p.208-211]`.
