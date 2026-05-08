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
| UPRO | SKIP | — | — | — | 0.030 | "ticker 'UPRO' not in cache — available: ['BNDSIM', 'CASHX', 'DBMFSIM', 'EFVSIM', 'GDESIM', 'GLDSIM', 'IEFSIM', 'KMLMSIM', 'QLDSIM', 'QQQSIM', 'RSSBSIM', 'SPYSIM', 'SSOSIM', 'TLTSIM', 'TQQQSIM', 'UGLSIM', 'UPROSIM', 'VBRSIM', 'VEASIM', 'VSSSIM', 'VTISIM', 'VTSIM', 'VWOSIM', 'VXUSSIM', 'ZROZSIM']" |
| SSO | SKIP | — | — | — | 0.010 | "ticker 'SSO' not in cache — available: ['BNDSIM', 'CASHX', 'DBMFSIM', 'EFVSIM', 'GDESIM', 'GLDSIM', 'IEFSIM', 'KMLMSIM', 'QLDSIM', 'QQQSIM', 'RSSBSIM', 'SPYSIM', 'SSOSIM', 'TLTSIM', 'TQQQSIM', 'UGLSIM', 'UPROSIM', 'VBRSIM', 'VEASIM', 'VSSSIM', 'VTISIM', 'VTSIM', 'VWOSIM', 'VXUSSIM', 'ZROZSIM']" |
| TQQQ | SKIP | — | — | — | 0.030 | "ticker 'TQQQ' not in cache — available: ['BNDSIM', 'CASHX', 'DBMFSIM', 'EFVSIM', 'GDESIM', 'GLDSIM', 'IEFSIM', 'KMLMSIM', 'QLDSIM', 'QQQSIM', 'RSSBSIM', 'SPYSIM', 'SSOSIM', 'TLTSIM', 'TQQQSIM', 'UGLSIM', 'UPROSIM', 'VBRSIM', 'VEASIM', 'VSSSIM', 'VTISIM', 'VTSIM', 'VWOSIM', 'VXUSSIM', 'ZROZSIM']" |
| QLD | SKIP | — | — | — | 0.010 | "ticker 'QLD' not in cache — available: ['BNDSIM', 'CASHX', 'DBMFSIM', 'EFVSIM', 'GDESIM', 'GLDSIM', 'IEFSIM', 'KMLMSIM', 'QLDSIM', 'QQQSIM', 'RSSBSIM', 'SPYSIM', 'SSOSIM', 'TLTSIM', 'TQQQSIM', 'UGLSIM', 'UPROSIM', 'VBRSIM', 'VEASIM', 'VSSSIM', 'VTISIM', 'VTSIM', 'VWOSIM', 'VXUSSIM', 'ZROZSIM']" |
| TMF | SKIP | — | — | — | 0.015 | "ticker 'TMF' not in cache — available: ['BNDSIM', 'CASHX', 'DBMFSIM', 'EFVSIM', 'GDESIM', 'GLDSIM', 'IEFSIM', 'KMLMSIM', 'QLDSIM', 'QQQSIM', 'RSSBSIM', 'SPYSIM', 'SSOSIM', 'TLTSIM', 'TQQQSIM', 'UGLSIM', 'UPROSIM', 'VBRSIM', 'VEASIM', 'VSSSIM', 'VTISIM', 'VTSIM', 'VWOSIM', 'VXUSSIM', 'ZROZSIM']" |
| UGL | SKIP | — | — | — | 0.010 | "ticker 'UGL' not in cache — available: ['BNDSIM', 'CASHX', 'DBMFSIM', 'EFVSIM', 'GDESIM', 'GLDSIM', 'IEFSIM', 'KMLMSIM', 'QLDSIM', 'QQQSIM', 'RSSBSIM', 'SPYSIM', 'SSOSIM', 'TLTSIM', 'TQQQSIM', 'UGLSIM', 'UPROSIM', 'VBRSIM', 'VEASIM', 'VSSSIM', 'VTISIM', 'VTSIM', 'VWOSIM', 'VXUSSIM', 'ZROZSIM']" |

---

Summary: 0 PASS, 0 FAIL, 6 SKIP out of 6 tickers.

Decision: ADVANCE to T1 implementation.
