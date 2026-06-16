# Spec — `studies/momentum_v2/` (consolidated momentum study)

**Status:** research-only, `promotion_eligible=false`. Created 2026-06-16.

## Purpose

Merge the two parallel momentum studies into one universe-organized package so
research continues "em uma pasta só":

- from `studies/momentum_13612_universes/` — the ranking/diagnostic intelligence:
  rolling relative-equity dominance, moving-average overlays, staggered offsets,
  crisis-window drawdowns, and the broad→evolution→validate funnel;
- from `studies/momentum/` — the data/validation foundation: the Postgres feed,
  survivorship filters, YAML config, and the hard validation gates.

The two source folders stay as read-only reference until momentum_v2 reproduces
their key results; they are not deleted by this work.

## Decisions (user-approved)

1. **Funnel in 3 phases** — `broad` (diagnostic map, no promotion) → `evolution`
   (MA overlays + fixed/staggered on the strongest finalists) → `validate`
   (honest hard gates on a small set with an exogenous trial count).
2. **Window** — primary `--start 1990-01-01`, robustness re-run `2000-01-01`.
3. **Selection lens** — after-tax **Sharpe + Calmar** (`evolution.selection_metrics`),
   reporting rolling dominance and crisis MDD alongside. (Initially rolling
   dominance; switched per the return/risk-adjusted objective. The dominance lens
   was independently regime-stable, so both are reported.)
4. **WF gate vs MDD** — drawdown is a warning-only tier (mandate §5), so the
   walk-forward gate is purely `≥6/8` profitable windows; `wf_max_drawdown` is set
   non-binding (`1.0`). A `−25%` per-window cap was stricter than the mandate.
5. **Postgres loader promoted** to `src/market_lab/backtest/data/postgres_source.py`
   (`PostgresSource`), shared and tested next to `YFinanceSource`/`TiingoSource`.

## Architecture

```
src/market_lab/backtest/data/postgres_source.py   # PostgresSource, UNIVERSE_SQL, PricePanel
studies/momentum_v2/
  core.py        # scoring (raw_13612, mom_12_1, vol_adjusted_13612, clenow_trend,
                 #   composite_mom_lowvol), lookback profiles, vectorized + holdings-loop
                 #   simulation, staggered offsets, BR annual tax, turnover, metrics
  dominance.py   # relative-equity + rolling dominance (weights 10/15/25/25/25%),
                 #   crisis windows (dotcom/gfc/covid/rates2022), cheap WF diagnostic
  overlays.py    # market SMA200 (monthly/daily), stock SMA100, combos; fixed/staggered
  filters.py     # survivorship-mitigation filters + per-ticker diagnostics
  grid.py        # broad-grid expansion (dedups lookback-independent score modes)
  validation.py  # unified result_row, PBO summary (sampled), validate-phase gates
  config.py      # base.yaml deep-merged with config/<universe>.yaml
  report.py      # markdown/json writers; survivorship disclaimer in every report
  plots.py       # equity-vs-benchmark panels, CAGR/MDD scatter, heatmaps
  run.py         # --universe --phase {broad|evolution|validate} --start,
                 #   --audit-only, --cache-panels/--refresh-cache
  universes/<universe>/<window>/{results,plots,reports,cache}/   # identical schema
```

Outputs are namespaced by start window (`<window>` = `from_1990`, `from_2000`, …)
so primary and robustness runs coexist without overwriting. `--cache-panels` stores
the filtered panel under `<window>/cache/` so all three phases of a window reuse one
Postgres load.

## Score modes & grid (`config/base.yaml`)

- Score modes: `raw_13612` `[stocks_on_the_move, p.60]`, `mom_12_1`,
  `vol_adjusted_13612` `[systematic_trading, p.137-148]`, `clenow_trend`
  `[stocks_on_the_move, p.70-77, p.98]`, `composite_mom_lowvol`. `mom_3_6_12` is
  `raw_13612` under the `lb3_6_12` profile.
- Lookback profiles: `1_3_6_12`, `3_6_12`, `6_12`, `6`. Lookback-independent modes
  (`mom_12_1`, `clenow_trend`) are emitted once.
- top_n `[3,5,10,15,20]` (excludes 1 = too volatile and 50 = unmanageable by hand);
  rebalance `[1,3,6,12]`; offsets `[0]` (set `all` to expand); weights
  `equal`/`inverse_vol`; absolute filter `[false,true]`. US-stocks default ≈ 840 configs.

## Funnel phases

- **broad** — vectorized simulation per config; after-tax (BR 15% annual) main
  metrics with gross alongside; rolling dominance + crisis MDD + turnover; sampled
  PBO (`broad_pbo_max_configs`). Diagnostic map only `[advances_fin_ml, p.273-275]`.
- **evolution** — top finalists by `rolling_rel_score` crossed with overlays ×
  {fixed, staggered}; MA gates per Clenow `[stocks_on_the_move, p.66-67, p.81-82,
  p.98-99]` and Gayed daily cash rotation `[leverage_for_the_long_run, p.9, p.13,
  p.16]`. Finalists selected by Sharpe + Calmar; report ordered by both.
- **validate** — hard gates on the small set with honest trial count (broad +
  evolution): PBO<0.5 (CSCV), DSR p<0.05, WF≥6/8 profitable windows (shared
  `wf_for_config`, MDD non-binding per mandate §5), bootstrap CI-low Sharpe>0,
  cross-library CAGR within ±3pp on the **base** strategy computed two ways
  (vectorized vs holdings-loop — must be the same strategy, not the overlaid curve
  vs the base) `[advances_fin_ml, p.208-211, p.31-34]`. A PASS here means the edge
  clears the statistical bar; it does **not** lift `promotion_eligible=false`.

## Survivorship stance

The Postgres universe (synced from yfinance) plus filters *mitigate* but do not
*eliminate* bias — fully delisted names were never synced, so historical screens
stay inflated. Every row is `promotion_eligible=false` and every report carries the
disclaimer `[advances_fin_ml, p.208-211]`. This is the binding blocker: the
canonical run *passes* the statistical gates, so promotion would require a
point-in-time membership + delisted-price feed (data quality), not more tuning.

## Verification

- Unit/integration: `uv run pytest tests/test_postgres_source.py tests/test_momentum_v2.py`.
- Baseline unaffected: `uv run pytest -q` (pre-existing env-only failures in
  cross_lib / macro_data_loader / long_term_portfolio synths need local data files
  and are unrelated).
- Canonical run (2026-06-16): full universe `2301/7136` pass filters; windows 1990 +
  2000, `840` broad + `144` evolution each (honest trials `984`). Both windows
  `overall_pass=True`: 1990 set-PBO `0.000` (finalists `clenow_trend lb1_3_6_12
  top15/top20 reb1`); 2000 set-PBO `0.357` (finalists `raw_13612 lb6 top20 reb3` +
  `…inverse_vol lb1_3_6_12 top20 reb3`); DSR p≈0, WF 8/8, bootstrap CI-low Sharpe
  `0.67–0.87`, cross-lib Δ≈`0.01pp`. Crisis overlays cut GFC MDD to `−12%`/`−20%`.
  Still `promotion_eligible=false` (survivorship).
