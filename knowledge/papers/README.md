# Papers — Literature Sprint Knowledge Base

Academic papers, working papers, and practitioner research cataloged during
literature sprints. Unlike `books/summaries/` (full-book summaries with page
citations), this directory stores **paper-level entries with source URL as
the primary reference** — we do not have local raw text for most entries.

## Citation format

- Books (full raw ingested): `[book.slug, p.X]` or `[book.slug, ch.Y]`
- Papers (this directory): `[paper.<slug>, §section]`

Examples:

- `[book.leverage_for_the_long_run, p.17]` — cites Gayed 2016/2020 Table 8
- `[paper.zarattini_2024_intraday_spy, §results]` — cites the Zarattini-Aziz-Barbon
  2024 SSRN paper on intraday SPY momentum, results section per abstract

Entries clearly mark `Raw access: N/A` when the full paper is not locally
available. For any material decision, fetch the source URL and verify.

---

## Index by topic (Phase 3.7-1 literature sprint, 2026-04-22)

Source deliverable: `docs/research/2026-04-23-phase3.7-literature-sprint.md`

### T1 — LETF holding-period optimization + vol-decay mitigation

- [`hsieh_2025_letf_compounding.md`](hsieh_2025_letf_compounding.md) —
  Hsieh-Chang-Chen 2025, arXiv 2504.20116. Regime-conditional compounding
  (AR(1) / AR-GARCH); autocorrelation as the driver beyond vol drag. **Key for H2.**
- [`lin_2025_letf_arbitrage.md`](lin_2025_letf_arbitrage.md) —
  Lin-Lin-Wang-Yeh 2025, SSRN 5421274. US-vs-Japan asymmetric decay capture,
  Sharpe 2.12 on beta-neutral. **Low fit for Pepperstone (no SPXU CFD).**
- [`pauchlyova_2025_letf_allocation.md`](pauchlyova_2025_letf_allocation.md) —
  Quantpedia 2025. LETF as 20% sleeve in trend-filtered allocation.

### T2 — VIX term-structure + LETF rotation (post-Gayed)

- [`bozovic_2024_vix_managed.md`](bozovic_2024_vix_managed.md) —
  Božović 2024, IRFA v95. **VIX-managed portfolio scaling; minimal rebalancing;
  survives costs.** Anchor for Phase 3.7-3 H2.
- [`wang_2024_vix_cmf_ml.md`](wang_2024_vix_cmf_ml.md) —
  Wang et al 2024, PLoS One. ML walk-forward on VIX CMF term structure.
  IR 2.29 best config — but frictionless.

### T3 — Short-hold intraday / overnight in ETFs + CFD

- [`zarattini_2024_intraday_spy.md`](zarattini_2024_intraday_spy.md) —
  Zarattini-Aziz-Barbon 2024, SSRN 4824172. **Beat the Market: Sharpe 1.33 net
  on SPY intraday, 2007-2024.** Primary lead (H1) for Phase 3.7-3 hunt.
- [`maroy_2024_intraday_improvements.md`](maroy_2024_intraday_improvements.md) —
  Maróy 2024, SSRN 5095349. Extension with VWAP/Ladder exits, Sharpe > 3
  IS (needs PBO/DSR before trust).
- [`zirk_sadowski_2025_intraday_overnight.md`](zirk_sadowski_2025_intraday_overnight.md) —
  Zirk-Sadowski-Hryckiewicz 2025, Finance Research Letters. NYSE small-cap
  45-60 min anomaly evidence (supporting context).

### T4 — Confidence-weighted sizing / Kelly practice

- [`wysocki_2024_kelly_vix.md`](wysocki_2024_kelly_vix.md) —
  Wysocki 2024, arXiv 2508.16598. **Kelly-VIX hybrid sizing on SPX put-writing;
  PSR-validated.** Core reference for Phase 3.7-3 H4 sizing meta-layer.
- [`carta_2020_kelly_practical.md`](carta_2020_kelly_practical.md) —
  Carta-Conversano 2020, Frontiers Applied Math. Kelly daily rebalance +
  24mo window; frictionless.
- [`downey_2023_fractional_kelly.md`](downey_2023_fractional_kelly.md) —
  Downey 2023 blog. Monte-Carlo rationale for half/quarter-Kelly under edge
  uncertainty.

### T5 — BTC/ETH systematic trend post-2022

- [`zarattini_2025_crypto_trends.md`](zarattini_2025_crypto_trends.md) —
  Zarattini-Pagani-Barbon 2025, SSRN 5209907. **Donchian ensemble on top-20
  crypto, Sharpe > 1.5 net, alpha 10.8% vs BTC.** Primary lead (H3).
- [`grayscale_2023_btc_momentum.md`](grayscale_2023_btc_momentum.md) —
  Grayscale Research 2023. BTC MA-crossover baseline (IS only).
- [`palazzi_2025_crypto_passive.md`](palazzi_2025_crypto_passive.md) —
  Palazzi 2025, Journal of Futures Markets (paywalled). To fully ingest in
  Phase 3.7-2.

### T6 — FX majors carry + trend combination

- [`fan_2025_currency_factors.md`](fan_2025_currency_factors.md) —
  Fan-Kearney-Li-Liu 2025, Financial Review. Currency factor optimization
  framework with data-snooping correction. Carry Sharpe 0.71→1.29 after hedging.
- [`rohrbach_2017_fx_momentum.md`](rohrbach_2017_fx_momentum.md) —
  Rohrbach-Suremann-Osterrieder 2017. **G10 momentum confirmed-dead post-2008;
  edge survives in EM + crypto.**

### T7 — LETF pairs + synthetic hedging

- [`loviscek_2017_letf_pairs.md`](loviscek_2017_letf_pairs.md) —
  Applied Economics 2017. UPRO+SPXU short-pair; FINRA-margin-bound;
  **not viable on Pepperstone retail CFD.**

### T8 — Pepperstone cost structure 2025-2026

**Reference:** `docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md`
(existing in repo — not duplicated here). Summary table inside
`docs/research/2026-04-23-phase3.7-literature-sprint.md` §T8.

### T9 — Overnight anomaly in US indices

- [`glasserman_2024_overnight_news.md`](glasserman_2024_overnight_news.md) —
  Glasserman et al 2024, arXiv 2507.04481. Topic-modeling attribution of
  overnight returns to news; **authors explicitly disclaim viability as
  trading strategy** due to turnover.
- [`alphaarchitect_2021_overnight_costs.md`](alphaarchitect_2021_overnight_costs.md) —
  Alpha Architect 2021. Cost-adjusted overnight anomaly **does not survive
  retail frictions.**

### T10 — ML systematic trading post-2022

- [`li_ferreira_2025_network_momentum.md`](li_ferreira_2025_network_momentum.md) —
  Li-Ferreira 2025, arXiv 2501.07135. Network momentum ensemble on 28 futures;
  best Sharpe 0.35 net — **below Phase 3.6 gate 1.5; reinforces null.**
- [`scidirect_2024_backtest_overfit.md`](scidirect_2024_backtest_overfit.md) —
  ScienceDirect Knowledge-Based Systems 2024. Synthetic-controlled OOS-method
  comparison; ratifies CSCV/PBO/DSR as essential.

---

## How to use this directory

1. When designing a new strategy or writing a technical decision, search by
   topic and link the closest paper slug.
2. Before **any material implementation decision** based on a paper entry,
   fetch the primary source URL and verify — these entries are abstract-level
   summaries, not full-text ingestion.
3. When a paper enters the picture in a spec / PR, cite:
   `[paper.<slug>, §section]`.
4. If a new literature sprint produces additional papers, add files here and
   update this README index.

## Provenance

All entries in this directory originate from:

- **Phase 3.7-1 literature sprint**, 2026-04-22
- **Source sprint deliverable:** `docs/research/2026-04-23-phase3.7-literature-sprint.md`
- **Branch:** `phase3.6/swing-winner-hunt-20260423`
- **Commit authoring the sprint:** `77b730a3eec6d43cba86390cb79cca41b2d66435`

Future sprints append here with a new header + date stamp.
