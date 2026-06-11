# PLAN — `discussion/` sub-study: regimes, decorrelation, allocation plateau, Reddit post

> **Status: EXECUTED 2026-06-11.** Plan written 2026-06-10; kept for provenance.
> See `README.md` for results and `METHODS.md` for deviations (cross-check
> semantics revised: SPY = integrity gate, CORE = documented proxy divergence;
> composition-check thresholds set from measured drift; AQR + Ken French data
> fetched successfully, so no fallbacks were needed).
> Discovery-only research; no mandate/capital change (maintenance mode preserved).
>
> **User decisions already made:** (1) universe includes RSSY/RSSX via new proxies;
> (2) allocation verdict framed as **frontier + plateau**, not a single optimum;
> (3) all docs and the final post in **English**.

## Context

The RSC study concluded with the canonical **35% GDE / 40% RSST / 25% ZROZ** allocation
(2000-01-04..2026-05-21: CAGR 12.40%, MDD −30.76%, Sharpe 0.838 vs SPY 8.39%/−55.14%/0.514).
This sub-study must:

1. Show how each asset (individual: SPY, GLD, MF, ZROZ, BTC; stacked: GDE, RSST, NTSX, RSSX, RSSY)
   behaved in bull/bear regimes and demonstrate the **decorrelation** between sleeves.
2. Test whether 35/40/25 is "best" — framed as **frontier + plateau** (anti-overfitting
   discipline `[advances_fin_ml, p.208-211]`).
3. Run ablations: remove ZROZ, NTSX swap, add SSO/UPRO, HFEA (55/45 UPRO/TMF) comparison,
   RSSX/RSSY extensions.
4. Produce an **English** Reddit-ready post (r/ETFs, r/LETFs) with ~12 figures.

## Verified facts that shape the design (checked 2026-06-10)

- `datasets.load_prices("lh_56y")` is **broken** (cache lacks KMLMSIM → KeyError at
  `datasets.py:132`). Do NOT use it; build a discussion-local loader.
- Data sources:
  - `data/testfolio/cache/history.parquet`: SPYSIM/SSOSIM/UPROSIM (1885+), GLDSIM (1968+),
    IEFSIM/ZROZSIM (1962+), CASHX, QQQSIM/TQQQSIM/QLDSIM etc. Ends 2026-05-22.
  - `us_core/series/remote_prices.parquet`: GDESIM 1968+, NTSXSIM 1962+, KMLMSIM 1988+,
    DBMFSIM 2000+, **BTCSIM 2010-07-19+** (prices).
  - `us_core/series/return_stacked_core_sleeve_returns.parquet`: aligned daily RETURNS
    2000-01-04..2026-05-21 for GDESIM, RSSTSIM, ZROZSIM, SPYSIM, KMLMSIM, DBMFSIM, GLDSIM,
    CASHX — **master calendar for the primary window**. Anchor reproduces on it with monthly
    rebalance (first-trading-day convention): 12.38%/−30.76%/0.837 — inside tolerance.
- Reusable simplex/monthly-rebalance engine: `us_core/four_asset_grid/run.py` —
  `generate_weight_vectors`:228, `monthly_rebalanced_equity`:239,
  `simulate_monthly_rebalanced_matrix`:333 (vectorized), `compute_metrics`:265.
  Adapt (it hardcodes a 4-asset list).
- RSSX spec exists: `scripts/build_stacked_sim_proxies.py:100` =
  `1.0*SPY + 0.8*GLD + 0.2*BTC − 0.8*CASHX`. The script can't run as-is (BTCSIM lives in
  remote_prices.parquet, not the cache) — replicate its `_build_proxy`:130 financing model
  locally; do NOT write into the shared cache.
- `synths.tmf_synth_returns_from_cache()` is broken (no TLTSIM in cache) and its formula
  omits the 2× cash borrow — don't use it.
- Ken French CSVs missing (`data/ken_french/` doesn't exist) — the extended 1970+ window
  requires a one-time download or must skip gracefully (loudly).
- Prior Reddit posts exist as style models: `us_core/REDDIT_POST_rETFs.md`,
  `us_core/REDDIT_POST_rLETFs.md`, `us_core/REDDIT_IMAGE_CAPTIONS.md`; plot style in
  `regenerate_color_plots.py` (figsize (11, 6.2), dpi 180, log equity, SPY black/thicker).
- Episode dates for dot-com/GFC/COVID/2022 must match `robustness_tables/us_regime_stress.csv`
  for cross-checking.

## Folder layout

```
studies/return_stacked_core/discussion/
├── README.md            # charter, re-run instructions, provenance, risk register, disclaimers
├── METHODS.md           # methodology + every proxy formula + book citations
├── POST.md              # master Reddit post (EN) + POST_rETFs.md / POST_rLETFs.md variants
├── IMAGE_CAPTIONS.md
├── make_all.py          # orchestrator: s00..s07 in order, fail-fast, --only sNN / --skip-network
├── discussion_data.py   # data layer: merged loaders (cache + remote_prices + sleeve matrix)
├── engine.py            # monthly-rebalance portfolio + metrics (adapted from four_asset_grid/run.py)
├── s00_verify_anchor.py # reproduce canonical numbers or abort
├── s01_build_series.py  # RSSXSIM, TMFSIM_D, TLTPROXY, RSST_EXT, portfolio curves → series/ (+ meta.json sidecars)
├── s01b_fetch_aqr_carry.py  # optional network: AQR carry data → data/external/aqr/
├── s02_episodes.py      # regime tables → tables/
├── s03_correlations.py  # full/rolling/conditional corr → tables/
├── s04_simplex.py       # 231-node simplex + plateau + start-date sensitivity → tables/
├── s05_ablations.py     # ablation battery → tables/
├── s06_extended_1970.py # 1970+ window (graceful skip if KF data absent)
├── s07_figures.py       # all figures from saved artifacts only → figures/
├── series/  tables/  figures/
```

Numbered deterministic scripts (no RNG; if ever needed, seed 42). Figures consume only
saved `series/` + `tables/`.

## New proxies (s01 → `series/` with formula+provenance sidecars)

| Series | Formula (daily returns) | Window |
|---|---|---|
| RSSXSIM | `1.0*SPY + 0.8*GLD + 0.2*BTC − 0.8*CASHX` (replicates build_stacked_sim_proxies spec) | 2010-07-20+ |
| TLTPROXY | cache `TLTSIM` if present, else `0.50*ZROZSIM + 0.50*IEFSIM` (≈17y duration ≈ TLT) | 1971+ |
| TMFSIM_D | `3*TLTPROXY − 2*CASHX − 0.0106/252` (financing-explicit `[leverage_for_the_long_run, ch.3-4]`) | 1971+ |
| RSSYSIM | `SPY + carry − 0.0200/12`; carry = AQR "Century of Factor Premia: Monthly" multi-asset carry composite scaled to 10% ann. vol. **Monthly-frequency native** — every RSSY table runs monthly for ALL members (√12 Sharpe, monthly MDD); never mixed into daily tables. Fallback if fetch infeasible: RSSY degrades to qualitative mention in POST.md; pipeline still completes. | per AQR file |
| RSST_EXT | `SPY + 1.0*KMLM_SPLICED − (CASHX + 0.0200/252)`; KMLM splice via `datasets._build_spliced_kmlmsim` fed with remote KMLMSIM; plus `RSST_EXT_HAIRCUT` (pre-1988 MF excess ×0.5, per datasets.py:14-17 warning) | 1970+ |

Helper: `MFBLEND = 0.70*DBMFSIM + 0.30*KMLMSIM` (mirrors `export_sleeve_returns.py`).
CASHX is an equity curve — financing legs use `pct_change()` of it, never assume zero.

## Analyses

### s02 — episodes (adapt `generate_robustness_report.regime_stress`:386)

Two tables (`tables/episodes_components.csv`, `tables/episodes_products.csv`); columns:
total return, episode MDD, spread vs SPY. BTC/RSSX rows `n/a` before 2010-07-20.

| Episode | Start | End | Window |
|---|---|---|---|
| Stagflation bear | 1973-01-11 | 1974-10-03 | extended |
| Gold/inflation bull | 1976-09-21 | 1980-01-21 | extended |
| Volcker rate shock | 1979-10-01 | 1982-08-12 | extended |
| 1987 crash | 1987-08-25 | 1987-12-04 | extended |
| Dot-com bust | 2000-03-24 | 2002-10-09 | primary |
| 2003-07 bull | 2002-10-09 | 2007-10-09 | primary |
| GFC | 2007-10-09 | 2009-03-09 | primary |
| QE bull | 2009-03-09 | 2020-02-19 | primary |
| US downgrade / euro crisis | 2011-04-29 | 2011-10-03 | primary |
| Taper tantrum (honesty episode — core loses to SPY) | 2013-05-02 | 2013-12-31 | primary |
| China/oil correction | 2015-05-21 | 2016-02-11 | primary |
| Q4-2018 | 2018-09-20 | 2018-12-24 | primary |
| COVID crash | 2020-02-19 | 2020-03-23 | primary |
| **Inflation/rates shock (key exhibit: stocks AND bonds down; MF/gold saved)** | 2022-01-03 | 2022-10-14 | primary |
| AI bull | 2022-10-14 | 2026-05-21 | primary |

### s03 — correlations

- Full-period Pearson, daily + monthly (pairwise max window, document `min_periods`).
- Rolling 252d for 6 pairs: SPY-GLD, SPY-MFBLEND, SPY-ZROZ, GLD-ZROZ, MFBLEND-ZROZ, GLD-MFBLEND.
- **Conditional**: monthly corr matrix + mean sleeve return in (a) SPY-down months,
  (b) SPY worst-decile months ("crisis capture") `[risk_parity, ch.5]`.

### s04 — simplex / plateau

- 5% grid → 231 nodes on {GDE, RSST, ZROZ}, monthly rebalance, primary window; metrics via
  `market_lab.backtest.metrics.performance` helpers (as four_asset_grid/run.py:23-31).
- Plateau methodology: neighbors = one 5pp transfer between two sleeves (≤6 neighbors);
  per-node `robustness_gap = sharpe − nbhd_min_sharpe`; plateau set = nodes ≥ 0.95×max Sharpe;
  report membership of 35/40/25, contiguity, top-10 by maximin (`nbhd_min_sharpe`).
- Start-date sensitivity: 8 starts (2000-01-04, 2002, 2004, …, 2014, fixed end); argmax
  trajectory + Jaccard overlap of plateau sets. Target claim: "the argmax moves; the plateau
  barely does."
- No "optimal" language anywhere; DSR/PBO caveats `[advances_fin_ml, p.222-223]`.
- Outputs: `tables/simplex_grid.csv`, `tables/simplex_plateau.csv`,
  `tables/simplex_start_sensitivity.csv`.

### s05 — ablations (monthly rebalance)

Primary window + recompute ALL rows on the BTC window (2010-07-20+) for apples-to-apples
vs RSSX (`tables/ablations_primary.csv`, `tables/ablations_btc_window.csv`); RSSY rows in
monthly-frequency table only (`tables/ablations_monthly_rssy.csv`).

| # | Config | Weights |
|---|---|---|
| A0 | CORE (anchor) | 35 GDE / 40 RSST / 25 ZROZ |
| A1 | Equal-weight | 33.4/33.3/33.3 |
| A2 | No-ZROZ renorm | 46.7 GDE / 53.3 RSST |
| A3 | ZROZ→cash | 35 GDE / 40 RSST / 25 CASHX |
| A4 | NTSX swap | 35 NTSX / 40 RSST / 25 ZROZ |
| A5 | DIY-SSO (capital-efficiency narrative; gross 1.35× vs core ~1.68×) | 35 SSO / 20 GLD / 25 MFBLEND / 20 ZROZ |
| A6-A8 | LETF baselines | 100% SSO; 100% UPRO; 60/40 SSO/ZROZ |
| A9 | HFEA (+ quarterly-rebalance sensitivity row) | 55 UPRO / 45 TMFSIM_D |
| A10 | RSSX swap (BTC window) | 35 RSSX / 40 RSST / 25 ZROZ |
| A11 | RSSX tilt (BTC window) | 17.5 GDE / 17.5 RSSX / 40 RSST / 25 ZROZ |
| A12 | RSSY swap (monthly only) | 35 GDE / 40 RSSY / 25 ZROZ |
| A13 | RSSY split (monthly only) | 35 GDE / 20 RSST / 20 RSSY / 25 ZROZ |
| A14-16 | Context rows | 100% SPY; 100% GDE; 100% RSST; 100% NTSX |

Columns: window, years, CAGR, MDD, vol, Sharpe, Sortino, Calmar, Ulcer, terminal ×,
ΔCAGR/ΔMDD/ΔSharpe vs A0.

### s06 — extended 1970+ (secondary, LOW fidelity)

Portfolios: CORE-EXT, CORE-EXT-HAIRCUT, NTSX-swap-EXT, HFEA, 100% SPY, 60/40 SPY/IEF.
Outputs: `tables/extended_metrics.csv`, `tables/extended_episodes.csv`, curves → `series/`.
Every artifact carries `fidelity: LOW` flag (UMD splice pre-1988 overstates MF Sharpe ~3×;
gold administered price pre-1971). Skips loudly if `data/ken_french/` CSVs absent
(README documents one-time download: `F-F_Momentum_Factor_daily` +
`F-F_Research_Data_Factors_daily` from the Ken French data library).

## Figures (s07; style from `regenerate_color_plots.py`)

| # | File | Content |
|---|---|---|
| 01 | components_equity_log | SPY/GLD/MFBLEND/ZROZ normalized, 2000+, log |
| 02 | products_equity_log | GDE/RSST/NTSX/CORE vs SPY, log |
| 03 | underwater_core_spy_hfea | drawdown curves, 2000+ |
| 04 | episode_bars_components | small-multiple bars per episode × component |
| 05 | episode_bars_products | same for products/portfolios |
| 06 | rolling_corr_252d | 6 pairs, zero line emphasized |
| 07 | spy_down_months | mean monthly sleeve return SPY-down vs SPY-up (paired bars) |
| 08 | simplex_sharpe_heatmap | ternary tripcolor, 35/40/25 starred, plateau outlined |
| 09 | frontier_cagr_mdd | 231-node scatter, color = ZROZ weight, Pareto front |
| 10 | hfea_vs_rsc | two-panel log equity + underwater ("2022 kills HFEA" exhibit) |
| 11 | extended_1970 | log equity with shaded regime bands, haircut variant, LOW-FIDELITY caption |
| 12 | ablation_summary | labeled scatter CAGR vs MDD, all ablation rows |

## POST.md structure (modeled on `us_core/REDDIT_POST_rETFs.md`)

Hook → **disclaimers block FIRST** (not financial advice; all pre-inception series are
simulated proxies with formulas disclosed; proxy ≠ live ETF; BTC survivorship caveat reused
from `build_stacked_sim_proxies.py:104-108`; RSSY = monthly academic carry proxy or omitted;
taxes/costs ignored) → TL;DR bullets → fund decomposition table → regime behavior
(figs 01-05) → decorrelation (figs 06-07) → "Is 35/40/25 special? No — it's a plateau"
(figs 08-09, explicit anti-curve-fitting line) → ablations (fig 12) → HFEA comparison
(figs 10-11) → what I'm NOT claiming → discussion questions.
Variants: `POST_rETFs.md` (less leverage jargon), `POST_rLETFs.md` (HFEA/SSO/UPRO-forward).
Reddit posts cite books by name; repo docs use `[slug, p.X]` (Regra 2).

## Execution order

1. Optional network (once): `s01b_fetch_aqr_carry.py`; manual Ken French download per README.
2. `s00` anchor gate (hard fail) → `s01` series → `s02`..`s06` → `s07` figures →
   author POST/METHODS/captions referencing only numbers present in `tables/`.

## Verification

- **s00 hard gate**: CORE monthly-rebalanced on sleeve matrix → CAGR 12.40 ± 0.15pp,
  MDD −30.76 ± 0.10pp, Sharpe 0.838 ± 0.010; SPY 8.39%/−55.14%/0.514 same tolerances.
  (Measured with first-day-of-month convention: 12.38/−30.76/0.837 — inside tolerance.
  Daily-rebalanced fixed weights give 12.83/0.857 — that is the WRONG convention.)
- GDE check: corr(GDESIM, `0.9*SPY+0.9*GLD−0.8*CASHX`) > 0.995 and |ΔCAGR| < 0.4pp/yr.
- NTSX check: corr(remote NTSXSIM, `proxies.py` 90/60/−50 blueprint) > 0.99 → `tables/verification.csv`.
- Episode cross-check: dot-com/GFC/COVID/2022 CORE rows match
  `robustness_tables/us_regime_stress.csv` within ±0.5pp.
- Determinism: run `make_all.py` twice → identical `sha256sum tables/*.csv`.
- `uv run pytest` still passes (813 baseline; nothing in `tests/` touched); no writes to the
  shared cache parquet.

## Repo hygiene

- Citations per Regra 2 in all docstrings/docs: `[risk_parity, ch.5]` (note: summary lives in
  `books/summaries/_archive/`), `[leverage_for_the_long_run, p.13, ch.3-4]`,
  `[advances_fin_ml, p.208-211, p.222-223]`, `[testing_tuning, p.327-335]`,
  `[systematic_trading, p.185-188]`.
- Update `docs/CURRENT_STATE.md` when executed (Regra 1); `PROJECT_HISTORY.md` only if
  narrative-worthy.
- Conventional commit: `feat(rsc): add discussion study — regimes, decorrelation, allocation plateau, reddit post`.

## Risk register (copy into discussion/README.md on execution)

1. `datasets.load_prices("lh_56y")` broken — never call it; use the discussion loader.
2. Ken French CSVs absent — extended window must skip LOUDLY; post degrades to 2000+ only.
3. Monthly carry vs daily mixing — frequency discipline above; never put RSSY in daily MDD tables.
4. BTC survivorship/non-stationarity — reuse caveat text from `build_stacked_sim_proxies.py:104-108`.
5. Proxy-vs-live tracking — RSST live only since 2023, GDE since 2022; spot-check via tiingo
   if available, else state untested tracking explicitly.
6. Simplex multiple testing — descriptive-map framing only; no "optimal" claims.
7. TMF formula divergence vs `synths.py` — document the financing-explicit decision in METHODS.md.
8. Calendar mismatch (cache 2026-05-22 vs sleeve matrix 2026-05-21) — master calendar = sleeve matrix.
