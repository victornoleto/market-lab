# METHODS — discussion sub-study

Full methodology for `studies/return_stacked_core/discussion/`. Repo docs cite
books as `[slug, p.X]` (CLAUDE.md Regra 2); the Reddit posts name sources in
plain English.

## 1. Data provenance

| Store | Contents | Role |
|---|---|---|
| `data/testfolio/cache/history.parquet` | SPYSIM/SSOSIM/UPROSIM (1885+), GLDSIM (1968+), IEFSIM/ZROZSIM (1962+), CASHX | price sims |
| `us_core/series/remote_prices.parquet` | GDESIM (1968+), NTSXSIM (1962+), KMLMSIM (1988+), DBMFSIM (2000+), BTCSIM (2010-07+) | saved Testfol.io pulls |
| `us_core/series/return_stacked_core_sleeve_returns.parquet` | aligned daily returns 2000-01-04..2026-05-21 | **master calendar (primary window)** |
| `data/ken_french/F-F_Momentum_Factor_daily.csv` + `F-F_Research_Data_Factors_daily.csv` | UMD + RF daily, 1926+ | pre-1988 MF splice (extended window) |
| `data/external/aqr/carry_monthly.csv` | AQR "Century of Factor Premia" carry columns, monthly 1926+ | RSSY sleeve proxy |

Ken French data: Ken French Data Library (one-time download, `s01b`-documented).
AQR data: AQR Capital Management, "Century of Factor Premia" (Ilmanen, Israel,
Moskowitz, Thapar, Wang), AQR Data Library, research use with attribution.

`datasets.load_prices("lh_56y")` is NOT used (slim cache lacks KMLMSIM —
verified broken 2026-06-10); `discussion_data.py` merges the stores directly.

## 2. Engine conventions

- Monthly rebalance, holdings reset to target weights at the first trading day
  of each month BEFORE applying that day's return (quarterly variant for the
  HFEA sensitivity row). Long-only at fund level; leverage embedded in the
  funds, never external margin `[leverage_for_the_long_run, p.13]`.
- Metrics: calendar-year CAGR; Sharpe/Sortino = daily mean/std (ddof=0)
  annualized by √252 (√12 for monthly-native tables); MDD on the equity curve;
  ulcer index `[systematic_trading, p.185-188]`.
- Financing legs always use `pct_change()` of the CASHX equity curve.
- No RNG anywhere in the pipeline; tables are byte-deterministic across runs.

## 3. Proxy formulas (daily simple returns)

| Series | Formula | Notes |
|---|---|---|
| GDESIM | saved sim ≈ `0.9·SPY + 0.9·GLD − 0.8·CASHX` | verified: corr_daily 0.988, corr_monthly 0.997, ΔCAGR 0.46pp/yr (ER 0.20% + tracking); daily gap = intra-month weight drift of the real fund's internal rebalance schedule |
| RSSTSIM | `SPY + 0.7·DBMF + 0.3·KMLM − (CASHX + 0.0200/252)` | repo tracking proxy (export_sleeve_returns.py); **most proxy-sensitive sleeve** — see §6 |
| NTSXSIM | saved sim ≈ `0.9·SPY + 0.6·IEF − 0.5·CASHX` | verified: corr_daily 0.985, corr_monthly 0.997 `[risk_parity, ch.5]` |
| RSSXSIM | `1.0·SPY + 0.8·GLD + 0.2·BTC − 0.8·CASHX` | spec from `scripts/build_stacked_sim_proxies.py`; BTC survivorship/non-stationarity bias — assumption-heavy |
| TLTPROXY | `0.5·ZROZ + 0.5·IEF` | duration blend ≈17y ≈ TLT (no TLTSIM in cache) |
| TMFSIM_D | `3·TLTPROXY − 2·CASHX − 0.0106/252` | financing-explicit `[leverage_for_the_long_run, ch.3-4]`. Decision: `synths.tmf_synth_returns` (3×TLT − 1.5%/yr flat) is NOT used — it omits the 2× cash borrow, which at 2022-25 rates flatters TMF by ~8-10pp/yr |
| RSSYSIM | `SPY_M + CARRY_SCALED − 0.0200/12` (monthly) | CARRY_SCALED = AQR All Macro Carry × 2.23 (10% ann-vol target; full-sample scalar, disclosed in-sample). **Monthly-native**: appears only in monthly tables — distributing monthly carry across days would fabricate a low-vol daily series |
| KMLM_SPLICED | UMD+RF (Ken French) pre-1988 chained into KMLMSIM | `[stocks_on_the_move, p.21-30]`; raw splice overstates MF-like Sharpe ~3× pre-1988 |
| RSST_EXT(_HAIRCUT) | `SPY + KMLM_SPLICED − (CASHX + 0.0200/252)`; haircut = pre-1988 MF excess over CASHX × 0.5 | extended window only, fidelity LOW |
| MFBLEND | `0.7·DBMF + 0.3·KMLM` | RSST's internal MF sleeve, used standalone in DIY configs |

## 4. Episode methodology (s02)

Full-period equity curves sliced at episode boundaries (`first trading day ≥
start`, last ≤ end); episode MDD re-anchored inside the slice. Portfolio rows
reflect a holder invested since window start (path-dependent monthly
rebalancing). Dot-com/GFC/COVID/2022 dates match
`robustness_tables/us_regime_stress.csv`. Conditional behavior of diversifiers
in equity drawdowns is the design target `[risk_parity, ch.5]`.

Cross-checks: SPY rows match the saved regime table exactly (integrity gate);
CORE rows diverge from the old 1988 saved curve **by design** (adjusted RSST
tracking proxy) — recorded in `tables/episodes_crosscheck.csv`, see §6.

## 5. Simplex / plateau methodology (s04)

231 nodes (5% grid) on {GDE, RSST, ZROZ}; per-node metrics on the primary
window plus 8 start dates (2000..2014). Plateau = nodes ≥ 95% of max Sharpe;
neighbors = one 5pp transfer between two sleeves; contiguity via BFS;
robustness ranked by maximin neighbor Sharpe. The scan is a DESCRIPTIVE MAP:
selecting its argmax would be selection bias under multiple testing
`[advances_fin_ml, p.208-211, p.222-223]`; plateau-over-peak is the robustness
criterion `[testing_tuning, p.327-335]`. Measured: plateau size 60, contiguous,
core inside in 8/8 start windows, core Sharpe percentile 0.74-0.99.

## 6. Known limitations (ranked by importance)

1. **MF-proxy sensitivity.** With the adjusted RSST tracking proxy, CORE's GFC
   episode is −23.1%; the old 1988 saved curve showed −13.8%. Same strategy,
   different MF proxy — crisis numbers are directional. Disclosed in all posts.
2. **Simulated pre-inception data everywhere.** GDE live 2022, RSST 2023,
   RSSX 2024; tracking of live funds vs sims is not validated here.
3. **BTC pre-2017 survivorship/non-stationarity** (RSSX rows).
4. **Carry proxy realism**: academic long-short carry composite ≠ RSSY's
   implementation; vol-scaling is in-sample.
5. **Extended window fidelity LOW**: UMD splice (haircut mitigates, does not
   fix), administered gold price pre-1971-08.
6. Gross of taxes, spreads, rebalance costs; ERs only partially modeled
   (financing spreads, TMF ER).
7. Survivorship in episode selection itself is mitigated by fixed, literature-
   standard episode dates (not optimized).

## 7. Reproduction

```bash
uv run python studies/return_stacked_core/discussion/make_all.py            # full offline rebuild
uv run python studies/return_stacked_core/discussion/make_all.py --only s04 # one step
# optional refresh of external data (network):
uv run --with openpyxl python studies/return_stacked_core/discussion/s01b_fetch_aqr_carry.py
```

`s00` aborts the pipeline unless the canonical anchor reproduces
(CORE 12.40%±0.15pp / −30.76%±0.10pp / Sharpe 0.838±0.010 and SPY
8.39%/−55.14%/0.514 — this run: 12.52%/−30.76%/0.847 and 8.54%/−55.14%/0.522).
Determinism verified: two consecutive `make_all.py` runs produce byte-identical
`tables/*.csv`.
