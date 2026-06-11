# REPORT — evolution/: can anything beat RSC-US with MDD ≤ 30%?

Date: 2026-06-11. Status: **discovery-only research** (no deployment, no
capital/mandate change; maintenance mode per `docs/investment-mandate.md` §1).
Pre-registration: `PLAN.md` — **eight rounds**, every amendment registered
before running, no threshold ever adjusted after seeing results. Rebuild:
`uv run python studies/return_stacked_core/evolution/make_all.py`.

Charter (user, 2026-06-11): find a portfolio/adjustment to RSC-US
`35% GDE / 40% RSST / 25% ZROZ` (monthly; 12.52% CAGR / −30.76% MDD / 0.847
Sharpe on `2000-01-04..2026-05-21`) with **higher CAGR and MDD ≤ 30%**,
calling it better only if *definitively* better.

---

## Terminal verdict — **honest FAIL, fully exhausted.**

Eight pre-registered rounds, **95,601 static portfolio trials (74,193
unique) + ~131,000 band/frequency/ballast configurations + a 4-test
deep-validation battery**, across every mechanism family expressible with
the available 25-year data: weight re-allocation, new stacked sleeves
(RSBT/RSSB), unbundled diversifiers (GLD/KMLM/QQQ), leveraged carriers
(SSO/UPRO), plain ballast (IEF/CASHX), calendar frequency, and
tolerance-band rebalancing.

**Nothing passes all pre-registered gates. Nothing is promoted.**

The search converged on exactly ONE maximal candidate —
`45/25/30 GDE/RSST/ZROZ + 20% tolerance bands` — unique across all spaces
(the only G1-passing plateau node in the 3-, 4- and 5-asset band simplices
and the ballast menus). It scores **5/6 gauntlet gates + 2/4 battery
tests** and is NOT promoted. Two findings kill it under the study's own
rules:

1. **G2 neighborhood cap-fragility:** its ZROZ ≤ 25% weight neighbors
   breach −32% MDD under bands (−33.0/−33.6%) — under tolerance bands,
   ZROZ < 30% is structurally cap-unsafe.
2. **B3 bootstrap (decisive):** on 1,000 joint 63-day-block resampled
   paths, the CAGR spread vs CORE is positive in only 83.8% (needed 95%)
   and the MDD advantage drops to a coin flip (50.4%). **The band edge
   lives in the multi-month trend structure of the specific historical
   sequence** — destroy long-trend autocorrelation and it evaporates. It
   is a trend-persistence harvest, not a distribution-level property
   `[advances_fin_ml, p.222-223]`.

What the candidate DOES survive (recorded, because it is the strongest
near-miss in the study): B1 dense starts — beats CORE-monthly CAGR in
**61/68 quarterly starts (89.7%)**; B4 weekly trigger cadence (13.08% /
−29.87%); G1 7/8 biennial starts; G4 73% of rolling 5y windows; CAGR
> CORE at **all 21 bands 10-30%** (13.0-13.4%) with the cap grazed by
5-25bps at bands 12-18% and held comfortably at 22-30%
(`tables/deepval_b2_bands.csv`); 1988+ window ties CORE CAGR (13.63% vs
13.66%) with MDD 3.2pp shallower; turnover 1.44 rebalances/yr vs 12.
Anyone revisiting this must start from the two kill-findings above, treat
*ZROZ ≥ 30% target* as a hard rule, and accept that the edge is
conditional on believing multi-month trend persistence — the same premise,
explicitly, as the RSST/KMLM sleeves themselves.

**Why the goal is unsatisfiable in this space:** the cap (MDD ≤ 30%), the
neighborhood safety floor, and the start-date gate form a three-way squeeze
with zero joint solutions. Beating CORE from the 2010/2014 starts
(13.6-14.7% bar) requires a gold/trend tilt; every such tilt either breaks
the cap, has cap-fragile neighbors, or loses the 1988-2000 regime. CORE
35/40/25 sits where it does precisely because it balances the regimes the
tilts trade against each other — the plateau is already priced
`[risk_parity, ch.5]`, `[advances_fin_ml, p.208-211]`,
`[testing_tuning, p.327-335]`.

---

## Round-by-round (all pre-registered in PLAN.md)

| Round | Mechanism | Scope | Result |
|---|---|---|---|
| 1 | New stacked sleeves (RSBT/RSSB) + unbundled GLD/KMLM/QQQ | 30,107 trials | 271 screen / 0 gauntlet |
| 2 | Coverage closure (GLD+KMLM menu, 8-asset 10%-step) | +30,074 | 408 screen / 0 gauntlet |
| 3 | Leveraged carriers SSO/UPRO + decoupled diversifiers | +35,420 | carriers dominated; 0 gauntlet |
| 4 | Calendar frequency + tolerance bands | 95 configs | calendar = offset luck; **bands = real parameter plateau** |
| 5 | Full 3-asset simplex × bands {15/20/25}, full gauntlet | 693 configs | 0 finalists; `45/25/30 b20` fails only G2 |
| 6 | 4- and 5-asset simplices × bands (RSBT/KMLM/GLD) | ~74,000 configs | G1∩G2 = 0 everywhere; unique near-miss unchanged |
| 7 | Plain ballast IEF/CASHX (+GLD), monthly AND bands | ~57,000 configs | 0 finalists; ballast dilutes G1 instantly |
| 8 | Deep-validation battery on the unique candidate | 4 tests | **2/4 — B2 (band continuum) and B3 (bootstrap) FAIL → terminal honest FAIL** |

Supporting facts preserved:

- **G1 bar (CORE-monthly CAGR per start):** 12.5% (2000) → 13.6%
  (2002-2006) → 14.7% (2010, 2014). Only band candidates ever cleared 7/8.
- **1988+ diagnostic:** every static near-miss loses to CORE-1988 (13.66%)
  by 0.4-1.4pp; the band candidate ties it. `tables/longwindow_1988.csv`.
- **Annual rebalance = MDD knob, not CAGR knob:** keeps CORE in-cap at all
  12 offsets on 2000+ (worst −29.79%) but NOT on 1988+ (−31.81%);
  min-across-offsets CAGR never beats monthly. `tables/rebalance_freq.csv`.
- **EW 33/33/33 b50** is the drawdown-first standout: 12.94% / −24.69%
  (2000+) and 14.24% / −24.73% (1988+) — but G1 2/8 (loses gold-decade
  starts). `tables/bands.csv`.
- **RSBT (real ETF, bonds+trend):** standalone 6.40% / −28.5% vs ZROZ
  5.54% / −62.9%; implementation diversifier (CTAP tier), not a CAGR play.

## Multiple-testing accounting

| Item | Count |
|---|---:|
| Static grid trials (raw / deduped) | 95,601 / 74,193 |
| Band/frequency/ballast configs (e03, e05-e10) | ~131,700 |
| Battery tests on the unique candidate (e11) | 4 (B1 ✓, B2 ✗, B3 ✗, B4 ✓) |
| Gauntlet finalists, any round | **0** |
| Promoted | **nothing** |

## Files

| File | Contents |
|---|---|
| `PLAN.md` | Pre-registration, Rounds 1-8 amendments (each before running) |
| `evo_data.py` / `evo_engine.py` | Sleeve construction + offset/band engines (reuses `discussion/engine.py`) |
| `e00..e11_*.py`, `make_all.py` | Deterministic pipeline (e11 bootstrap uses fixed seed 42) |
| `tables/verification.csv` | Anchor gate (CORE + 45/25/30 reproduce to 1e-6) |
| `tables/grid_[A-O].csv` | Per-menu static metrics (gitignored ~20 MB, rebuild via `make_all.py --only e01`) |
| `tables/candidates.csv` / `gauntlet.csv` / `finalists.csv` | Static screen → gauntlet (finalists empty) |
| `tables/rebalance_freq.csv` / `bands.csv` / `bands_verdicts.csv` / `annual_1988.csv` | Round 4 |
| `tables/band_gauntlet.csv` / `band_simplex.csv` | Round 5 |
| `tables/band_menus_4asset.csv` / `band_menus_5asset.csv` | Round 6 |
| `tables/ballast_menus.csv` | Round 7 |
| `tables/deepval_*.csv` | Round 8 battery (B1 starts, B2 bands, B3 bootstrap, summary) |
| `tables/longwindow_1988.csv` | G5 diagnostic |
| `tables/n_trials.txt` | Trial accounting |

Caveats (inherited, repeat in any external claim): MF-proxy sensitivity is
caveat #1 of the discussion package; RSBT/RSSB are tracking proxies with
the repo's 200bps financing convention; all numbers simulated, gross of
taxes/fees; band triggers evaluated daily (B4 stresses weekly) with the
same reset-before-return convention as the calendar engine; B3 bootstrap
deliberately destroys >63-day autocorrelation — it is a strict test that
prices the trend-harvest mechanism at zero.
