# Legacy B4 Deep Dive

Status: compacted historical note. This preserves the 2026-05-05 B4 deep-dive
and global-fork conclusions that formerly lived under
`studies/long_term_portfolio/`. It does not supersede the canonical B4-v2 core,
does not authorize deployment, and does not change the mandate.

## Why This Is Legacy

The 2026-05-05 deep dive started from the old B4 reference:

```text
25% NTSX / 25% GDE / 25% RSST / 25% ZROZ
```

The current canonical B4-v2 research champion is different:

```text
35% GDE / 40% RSST / 25% ZROZ
```

The old deep dive answered useful implementation questions around BTC vehicles,
small-cap value, momentum and non-US sleeves, but it used shorter windows and a
different base allocation. Treat it as lineage and sensitivity analysis, not as
the current recommendation. The live mandate remains 100% passive Plano C outside
this repo `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Preserved Iter 056 Result: SCV + Momentum + BTC

Question: from the old B4 `25/25/25/25` base, does draining ZROZ into `10%` SCV,
`10%` momentum and `5-10%` BTC improve the portfolio? The run used Testfol.io,
monthly rebalance and a `2015-10-12..2026-05-04` common window limited by SPMO.

| Rank | Portfolio | CAGR | MDD | Sharpe | 3y vs SPY | 5y vs SPY | 10y vs SPY |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `P4b`: `25 NTSX / 20 GDE / 25 RSST / 10 AVUV / 10 SPMO / 10 BTGD` | `20.48%` | `-32.97%` | `1.017` | `98.5%` | `100%` | `100%` |
| 2 | `P3a`: `25 NTSX / 25 GDE / 25 RSST / 10 AVUV / 10 SPMO / 5 BTC` | `20.99%` | `-34.30%` | `1.006` | `98.3%` | `100%` | `100%` |
| 3 | `P3b`: same as `P3a`, but `MTUM` instead of `SPMO` | `20.65%` | `-34.61%` | `0.985` | `96.0%` | `100%` | `100%` |
| 4 | `P2`: old B4 + `5%` BTC spot from ZROZ | `17.37%` | `-28.49%` | `0.970` | `65.1%` | `80.3%` | `100%` |
| 5 | `P5b`: `10% RSSX`, funded from NTSX | `20.92%` | `-35.76%` | `0.965` | `97.2%` | `100%` | `100%` |

Preserved conclusion: `BTGD 10%` funded from `GDE` was the best short-window
variant because it added gold plus BTC without duplicating more S&P 500 exposure.
The result was not promoted because the window was only `10.56y`, BTC dominated
the regime, BTGD/RSSX proxy assumptions were high-caveat, and no full validation
stack was run `[risk_parity, ch.5, p.10]`, `[risk_parity, ch.2, p.37-41]`,
`[stocks_on_the_move, p.21-30]`, `[machine_trading, p.202, ch.7]`.

## BTC Vehicle Lesson

The original RSSX proxy was wrong. It modeled RSSX as:

```text
100% SPY + 100% BTC - borrow
```

The corrected proxy used the 2026-05-05 holdings snapshot:

```text
100% SPY + 65% Gold + 35% BTC - borrow
```

This correction moved RSSX from the apparent winner to the middle of the ranking.
The old conclusion to preserve is:

| Vehicle | Best short-window reading | Caveat |
|---|---|---|
| BTGD | Best in old-B4 context when raised to `10%` and funded from GDE. | Proxy used spot BTC/gold and missed futures roll costs. |
| BTC spot | Nearly as good and simpler. | Direct crypto sleeve adds operational/tax handling. |
| RSSX | Useful implementation idea, but not the old-B4 winner after correcting holdings. | Duplicates equity beta and depends on dynamic gold/BTC risk parity assumptions. |

In the current B4-v2 package, RSSX is treated only as an optional implementation
variant for the gold sleeve, not as a replacement for the `35/40/25` core.

## Preserved Iter 057 Result: Global Fork

Question: does adding a non-US Avantis-style sleeve to the old B4 base improve the
portfolio, and does it beat SPY or VT? The internal engine used long-history
synthetic proxies and clipped non-US rows to the available proxy window.

| Rank | Portfolio | Window | CAGR | MDD | Sharpe |
|---:|---|---|---:|---:|---:|
| 1 | Old B4 US-only `25/25/25/25` | `38.3y` | `14.62%` | `-28.38%` | `1.027` |
| 2 | `70/30` with NB1 `40%` factor non-US | `31.2y` | `12.92%` | `-35.95%` | `0.925` |
| 3 | `70/30` with NB2 `30%` factor non-US | `31.2y` | `12.87%` | `-35.99%` | `0.919` |
| 4 | `70/30` with AVNM-only non-US | `32.0y` | `12.56%` | `-36.38%` | `0.896` |
| 5 | `60/40` with NB1 `40%` factor non-US | `31.2y` | `12.30%` | `-38.78%` | `0.874` |

Preserved conclusion: the old B4 US-only base dominated the global fork on Sharpe.
The `70/30` global variants were defensible only as non-numeric country-regime
insurance. Factor tilt helped slightly versus AVNM-only, but the US/non-US split
dominated the result `[risk_parity, ch.2, p.37-41]`, `[stocks_on_the_move,
p.21-30]`.

## What Not To Carry Forward

- Do not treat `P4b BTGD 10%` as the current B4-v2 champion.
- Do not treat the old `25/25/25/25` B4 base as the canonical core.
- Do not treat the Q&A allocation `70% old B4 + 25% AVNM + 5% BTC` as a validated
  recommendation. It was a personal forward-looking discussion, not a tested
  B4-v2 artifact.
- Do not resume the deleted Testfol.io scripts without a new pre-registered
  hypothesis and explicit trial budget `[advances_fin_ml, p.222-223]`.

## Cleanup Result

The following active-tree artifacts were removed after this consolidation:

| Former artifact | Replacement |
|---|---|
| `studies/long_term_portfolio/B4_DEEP_DIVE_2026-05-05.md` | This legacy note. |
| `studies/long_term_portfolio/B4_GLOBAL_FORK_ANALYSIS.md` | This legacy note. |
| `studies/long_term_portfolio/B4_GLOBAL_FORK_compare_table.md` | Tables above. |
| `scripts/long_term_portfolio/*` | Removed stale regeneration helpers. |
| `studies/long_term_portfolio/iterations/056-*` and `057-*` run/report files | Key facts summarized above; details recoverable from git history if needed. |

Canonical B4-v2 files remain `B4_V2_STRATEGY.md`, `ROBUSTNESS_REPORT.md`,
`CLOSING_SUMMARY.md` and `DISCOVERY_LINEAGE.md`.
