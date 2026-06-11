# discussion/ — regimes, decorrelation, allocation plateau, Reddit post

Status: **discovery-only research package** (no deployment, no capital or
mandate change; maintenance mode per `docs/investment-mandate.md`).

Goal: a self-contained, reproducible analysis of the return-stacked lineup —
how each sleeve behaved across bull/bear regimes, how decorrelated the sleeves
really are, whether `35% GDE / 40% RSST / 25% ZROZ` sits on a robust plateau
(vs a lucky peak), and a set of Reddit-ready posts with figures.

## Deliverables

| File | Purpose |
|---|---|
| `REPORT.md` | **Consolidated conclusions — explicit answers to the three chartered questions** (best allocation? regime behavior/decorrelation? alternative allocations?) |
| `POST.md` | Master Reddit post (English, full version) |
| `POST_rETFs.md` / `POST_rLETFs.md` | Sub-tuned variants (gentler / HFEA-forward) |
| `IMAGE_CAPTIONS.md` | Gallery captions, post order |
| `METHODS.md` | Full methodology, proxy formulas, citations, limitations |
| `figures/01..12_*.png` | The 12 post figures |
| `tables/*.csv` | All numbers behind the posts (deterministic) |
| `PLAN.md` | Original execution plan (kept for provenance) |

## How to re-run

```bash
uv run python studies/return_stacked_core/discussion/make_all.py            # full offline rebuild (s00..s07)
uv run python studies/return_stacked_core/discussion/make_all.py --only s04 # single step
```

Pipeline: `s00` anchor gate (aborts unless the canonical RSC numbers reproduce)
→ `s01` proxy series (+meta sidecars) → `s02` episodes → `s03` correlations →
`s04` simplex/plateau → `s05` ablations → `s06` extended 1970+ → `s07` figures.
Figures consume only saved `series/` + `tables/` artifacts. No RNG; two runs
produce byte-identical tables.

External data (already fetched & committed where allowed):

- `data/ken_french/F-F_Momentum_Factor_daily.csv` + `F-F_Research_Data_Factors_daily.csv`
  — Ken French Data Library (data/ is gitignored; re-download documented in
  `s01b`/`ff_momentum_proxy.py` if missing — `s06` skips loudly without them).
- `data/external/aqr/carry_monthly.csv` — extracted by `s01b_fetch_aqr_carry.py`
  (AQR "Century of Factor Premia", research use with attribution).

## Headline results (this run, 2026-06-11)

- CORE 35/40/25 (2000-01-04..2026-05-21, monthly rebalance, simulated, gross):
  **CAGR 12.52%, MDD −30.76%, Sharpe 0.847, 22.5×** vs SPY 8.54%/−55.14%/0.522/8.7×.
- Simplex scan (231 nodes): plateau of **60 contiguous nodes** ≥95% of max
  Sharpe; CORE inside the plateau in **8/8 start dates**; argmax wanders
  (45/25/30 → 60/30/10) — "the argmax moves; the plateau barely does".
- 2022 exhibit: SPY −24%, ZROZ −40%, MF +38% ⇒ CORE −21% vs HFEA −65%.
- Crisis capture (32 worst SPY months, avg −7.9%): GLD +1.8%, MF +2.4%,
  ZROZ +3.8% mean monthly; BTC −4.4% and carry −0.8% (return stacks, not
  crisis stacks).
- Extended 1970+ (LOW fidelity): CORE-EXT-HAIRCUT 13.9%/−39.7% vs SPY
  11.1%/−55.1%; HFEA −90.3% MDD in the Volcker years.
- RSSY (monthly carry proxy): swap REDUCES Sharpe (0.88 vs 0.96) — carry
  didn't defend in 2008/2022 the way trend did.
- RSSX (2010-07+): Sharpe 1.47 vs core 1.04 on the same window — entirely
  BTC's decade; RSSX −41% in 2022 (worse than SPY). Satellite at most.

## Risk register

1. `datasets.load_prices("lh_56y")` is broken (cache lacks KMLMSIM) — the
   discussion loader (`discussion_data.py`) merges stores directly; never call
   the old loader here.
2. **MF-proxy sensitivity is the #1 caveat**: CORE's GFC return is −23.1% with
   the adjusted RSST tracking proxy vs −13.8% on the old 1988 saved curve
   (`tables/episodes_crosscheck.csv`; SPY rows match exactly = integrity gate).
3. RSSY is monthly-native (AQR carry); it must never enter daily tables —
   daily interpolation would fabricate low vol.
4. BTC survivorship/non-stationarity pre-2017 ⇒ RSSX rows are assumption-heavy.
5. Proxy-vs-live tracking unvalidated (GDE live 2022, RSST 2023, RSSX 2024).
6. Simplex scan is a descriptive map; selecting its argmax = multiple-testing
   bias `[advances_fin_ml, p.208-211]`. No "optimal" claims anywhere.
7. TMF synth here is financing-explicit (3× TLTPROXY − 2× CASHX − ER);
   `synths.tmf_synth_returns` omits the borrow and is not used.
8. Calendar: master = sleeve matrix (ends 2026-05-21; cache ends 05-22).
9. Pre-existing repo test failures (missing TLTSIM/tiingo/macro local data)
   are unrelated to this package; adding the Ken French CSVs fixed one
   previously-failing test and broke none (verified 2026-06-11).
