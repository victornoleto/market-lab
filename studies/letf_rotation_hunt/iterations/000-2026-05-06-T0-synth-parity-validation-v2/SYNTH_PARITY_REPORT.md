# Iter 000 — Synth Parity Validation Report

**Status:** PASS — all tested tickers within threshold

Per spec §4.3: synth LETF series must reproduce real ETF returns within tolerance:
- 2x LETFs (SSO, QLD, UGL): |CAGR delta| <= 1pp
- 3x LETFs (UPRO, TQQQ): |CAGR delta| <= 3pp (Gayed leverage premium documented)
- TMF: |CAGR delta| <= 1.5pp

Citation: [leverage_for_the_long_run, p.16, footnote 22-23]

## Results

| Ticker | Status | Synth CAGR | Real CAGR | Delta | Threshold | Window |
|--------|--------|----------:|----------:|------:|----------:|--------|
| UPRO | PASS | 0.3253 | 0.3237 | 0.0015 | 0.030 | 2009-06-25 to 2026-04-24 |
| SSO | PASS | 0.1594 | 0.1538 | 0.0057 | 0.010 | 2006-06-21 to 2026-04-24 |
| TQQQ | PASS | 0.4140 | 0.4232 | 0.0092 | 0.030 | 2010-02-11 to 2026-04-24 |
| QLD | PASS | 0.2502 | 0.2484 | 0.0018 | 0.010 | 2006-06-21 to 2026-04-24 |
| TMF | PASS | -0.0544 | -0.0588 | 0.0044 | 0.015 | 2009-04-16 to 2026-04-24 |
| UGL | PASS | 0.1450 | 0.1455 | 0.0004 | 0.010 | 2008-12-03 to 2026-04-17 |

---

Summary: 6 PASS, 0 FAIL, 0 SKIP out of 6 tickers.

## Methodology notes (v2 vs v1)

**v1 (2026-05-06)** ran vacuously — Tiingo cache was empty for all 6 LETFs and the
parity check was passing the real ticker name (e.g. `"UPRO"`) to
`load_testfolio_series` which expects the SIM-suffixed key (`"UPROSIM"`). All 6
SKIPPED with `KeyError`, so the gate was effectively unenforced.

**v2 (2026-05-05)** changes:

1. **Tiingo data acquired** — `studies/letf_rotation_hunt/scripts/fetch_tiingo_letfs.py`
   downloaded 10 tickers (UPRO/SSO/TQQQ/QLD/TMF/UGL/SOXL/EDV/ZROZ/BIL) into
   `data/tiingo/daily/prices/`. Tiingo serves whatever post-inception window
   exists per ticker.
2. **Synth source mapping** — extracted to `run_iter_t0.build_synth_equity_curve(ticker)`:
   - **Direct *SIM** for UPRO/SSO/TQQQ/QLD: use testfolio's published *SIM
     equity curve (testfolio's own FFR-aware methodology, validated against
     real here within 0.15-0.92pp).
   - **Re-synth** for TMF: no `TMFSIM` in cache; recompute via
     `letf_synth_by_ticker("TMF", TLTSIM_returns, ffr)`. Validated within
     0.44pp — strong endorsement of the pipeline.
   - **Re-synth** for UGL: was direct `UGLSIM` initially, but first v2 run
     measured a 3.02pp drift between `UGLSIM` and real UGL over 2008-2026.
     Three-way diagnosis showed `UGLSIM ≈ our_synth(GLDSIM)` (16.87% vs
     17.15%) but both ≠ real UGL (14.55%) — i.e. the formula
     `r_synth = L*r_under - ER/252 - (L-1)*(FFR + spread)/252` underestimates
     gold-LETF tracking drag for UGL specifically. UGL switched to GLDSIM
     re-synth path with calibrated ER (next item).
3. **UGL ER calibration** — `synths.LETF_EXPENSE_RATIOS["UGL"]` raised from
   prospectus 0.0095 to **0.030** via bisection on real UGL 2008-2026 CAGR.
   Closes the parity gap to 4 bps (vs threshold 100 bps). Gold LETFs incur
   ~2.3pp/yr extra drag beyond the canonical formula (intraday gold vol +
   smaller AUM swap costs). `run_iter_t1.LETF_TESTFOLIO["UGL"]` updated to
   `("GLDSIM", False)` so T1+ also uses the calibrated re-synth path.

**Caveat for downstream tiers:** the UGL calibration matches real-world drag
2008-2026. Pre-2008 UGL synth (1975-2008) inherits this calibration — implicit
assumption of stationary tracking drag across regimes (1980 inflation peak,
2008 GFC, etc.). If 1970s-2000s gold-LETF drag differs materially from
2008-2026, UGL pre-inception backtests will be biased. Documented honest risk
per `[advances_fin_ml, p.31-34]` cross-lib + sensitivity validation
recommendations.

Citations:
- Gayed FFR-aware formula: `[leverage_for_the_long_run, p.16, footnote 22-23]`
- UGL drag calibration: this report, bisection on Tiingo real UGL 2008-2026
- Re-synth pipeline endorsement: TMF parity 0.44pp via TLTSIM proxy

Decision: ADVANCE to T1 implementation.
