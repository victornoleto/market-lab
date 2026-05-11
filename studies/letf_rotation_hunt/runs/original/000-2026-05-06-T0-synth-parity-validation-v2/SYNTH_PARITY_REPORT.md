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

Decision: ADVANCE to T1 implementation.
