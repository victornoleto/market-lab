# 004-2026-05-06-T1d-full-grid — SUMMARY

**Tier:** T1d
**Hypothesis:** Robustness mapping check: grid sweep of all (on, off, signal, period) combos. Tests whether T1c sequential winner (qld_sma200_off_zroz Sharpe 0.752) is robust to perturbations in the on/period/signal axes. Anti-curve-fit pre-registered: T1d-best Sharpe must exceed T1c-best + 0.05 = 0.802 to claim a new T1 winner; otherwise T1c stands.
**Primary citation:** [leverage_for_the_long_run, p.13, p.17 Table 8]; spec §2.2 + §3.4
**Engine SHA:** `255e5d8`
**Datetime UTC:** 2026-05-08T14:16:02.824358+00:00
**Configs tested:** 360

## TL;DR

Best config: **`qld_ema150_off_zroz`** (PROMISING, score 64.5/100). lh_56y: Sharpe 0.787 (edge vs SPY +0.105), CAGR 24.45%, MDD -58.0%.  **KILL T0:** PASS (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `upro_sma50_off_bil` | UPRO | BIL | sma | 50 |
| `upro_sma100_off_bil` | UPRO | BIL | sma | 100 |
| `upro_sma150_off_bil` | UPRO | BIL | sma | 150 |
| `upro_sma200_off_bil` | UPRO | BIL | sma | 200 |
| `upro_sma250_off_bil` | UPRO | BIL | sma | 250 |
| `upro_ema50_off_bil` | UPRO | BIL | ema | 50 |
| `upro_ema100_off_bil` | UPRO | BIL | ema | 100 |
| `upro_ema150_off_bil` | UPRO | BIL | ema | 150 |
| `upro_ema200_off_bil` | UPRO | BIL | ema | 200 |
| `upro_ema250_off_bil` | UPRO | BIL | ema | 250 |
| `upro_sma50_off_ief` | UPRO | IEF | sma | 50 |
| `upro_sma100_off_ief` | UPRO | IEF | sma | 100 |
| `upro_sma150_off_ief` | UPRO | IEF | sma | 150 |
| `upro_sma200_off_ief` | UPRO | IEF | sma | 200 |
| `upro_sma250_off_ief` | UPRO | IEF | sma | 250 |
| `upro_ema50_off_ief` | UPRO | IEF | ema | 50 |
| `upro_ema100_off_ief` | UPRO | IEF | ema | 100 |
| `upro_ema150_off_ief` | UPRO | IEF | ema | 150 |
| `upro_ema200_off_ief` | UPRO | IEF | ema | 200 |
| `upro_ema250_off_ief` | UPRO | IEF | ema | 250 |
| `upro_sma50_off_tlt` | UPRO | TLT | sma | 50 |
| `upro_sma100_off_tlt` | UPRO | TLT | sma | 100 |
| `upro_sma150_off_tlt` | UPRO | TLT | sma | 150 |
| `upro_sma200_off_tlt` | UPRO | TLT | sma | 200 |
| `upro_sma250_off_tlt` | UPRO | TLT | sma | 250 |
| `upro_ema50_off_tlt` | UPRO | TLT | ema | 50 |
| `upro_ema100_off_tlt` | UPRO | TLT | ema | 100 |
| `upro_ema150_off_tlt` | UPRO | TLT | ema | 150 |
| `upro_ema200_off_tlt` | UPRO | TLT | ema | 200 |
| `upro_ema250_off_tlt` | UPRO | TLT | ema | 250 |
| `upro_sma50_off_tmf` | UPRO | TMF | sma | 50 |
| `upro_sma100_off_tmf` | UPRO | TMF | sma | 100 |
| `upro_sma150_off_tmf` | UPRO | TMF | sma | 150 |
| `upro_sma200_off_tmf` | UPRO | TMF | sma | 200 |
| `upro_sma250_off_tmf` | UPRO | TMF | sma | 250 |
| `upro_ema50_off_tmf` | UPRO | TMF | ema | 50 |
| `upro_ema100_off_tmf` | UPRO | TMF | ema | 100 |
| `upro_ema150_off_tmf` | UPRO | TMF | ema | 150 |
| `upro_ema200_off_tmf` | UPRO | TMF | ema | 200 |
| `upro_ema250_off_tmf` | UPRO | TMF | ema | 250 |
| `upro_sma50_off_zroz` | UPRO | ZROZ | sma | 50 |
| `upro_sma100_off_zroz` | UPRO | ZROZ | sma | 100 |
| `upro_sma150_off_zroz` | UPRO | ZROZ | sma | 150 |
| `upro_sma200_off_zroz` | UPRO | ZROZ | sma | 200 |
| `upro_sma250_off_zroz` | UPRO | ZROZ | sma | 250 |
| `upro_ema50_off_zroz` | UPRO | ZROZ | ema | 50 |
| `upro_ema100_off_zroz` | UPRO | ZROZ | ema | 100 |
| `upro_ema150_off_zroz` | UPRO | ZROZ | ema | 150 |
| `upro_ema200_off_zroz` | UPRO | ZROZ | ema | 200 |
| `upro_ema250_off_zroz` | UPRO | ZROZ | ema | 250 |
| `upro_sma50_off_edv` | UPRO | EDV | sma | 50 |
| `upro_sma100_off_edv` | UPRO | EDV | sma | 100 |
| `upro_sma150_off_edv` | UPRO | EDV | sma | 150 |
| `upro_sma200_off_edv` | UPRO | EDV | sma | 200 |
| `upro_sma250_off_edv` | UPRO | EDV | sma | 250 |
| `upro_ema50_off_edv` | UPRO | EDV | ema | 50 |
| `upro_ema100_off_edv` | UPRO | EDV | ema | 100 |
| `upro_ema150_off_edv` | UPRO | EDV | ema | 150 |
| `upro_ema200_off_edv` | UPRO | EDV | ema | 200 |
| `upro_ema250_off_edv` | UPRO | EDV | ema | 250 |
| `sso_sma50_off_bil` | SSO | BIL | sma | 50 |
| `sso_sma100_off_bil` | SSO | BIL | sma | 100 |
| `sso_sma150_off_bil` | SSO | BIL | sma | 150 |
| `sso_sma200_off_bil` | SSO | BIL | sma | 200 |
| `sso_sma250_off_bil` | SSO | BIL | sma | 250 |
| `sso_ema50_off_bil` | SSO | BIL | ema | 50 |
| `sso_ema100_off_bil` | SSO | BIL | ema | 100 |
| `sso_ema150_off_bil` | SSO | BIL | ema | 150 |
| `sso_ema200_off_bil` | SSO | BIL | ema | 200 |
| `sso_ema250_off_bil` | SSO | BIL | ema | 250 |
| `sso_sma50_off_ief` | SSO | IEF | sma | 50 |
| `sso_sma100_off_ief` | SSO | IEF | sma | 100 |
| `sso_sma150_off_ief` | SSO | IEF | sma | 150 |
| `sso_sma200_off_ief` | SSO | IEF | sma | 200 |
| `sso_sma250_off_ief` | SSO | IEF | sma | 250 |
| `sso_ema50_off_ief` | SSO | IEF | ema | 50 |
| `sso_ema100_off_ief` | SSO | IEF | ema | 100 |
| `sso_ema150_off_ief` | SSO | IEF | ema | 150 |
| `sso_ema200_off_ief` | SSO | IEF | ema | 200 |
| `sso_ema250_off_ief` | SSO | IEF | ema | 250 |
| `sso_sma50_off_tlt` | SSO | TLT | sma | 50 |
| `sso_sma100_off_tlt` | SSO | TLT | sma | 100 |
| `sso_sma150_off_tlt` | SSO | TLT | sma | 150 |
| `sso_sma200_off_tlt` | SSO | TLT | sma | 200 |
| `sso_sma250_off_tlt` | SSO | TLT | sma | 250 |
| `sso_ema50_off_tlt` | SSO | TLT | ema | 50 |
| `sso_ema100_off_tlt` | SSO | TLT | ema | 100 |
| `sso_ema150_off_tlt` | SSO | TLT | ema | 150 |
| `sso_ema200_off_tlt` | SSO | TLT | ema | 200 |
| `sso_ema250_off_tlt` | SSO | TLT | ema | 250 |
| `sso_sma50_off_tmf` | SSO | TMF | sma | 50 |
| `sso_sma100_off_tmf` | SSO | TMF | sma | 100 |
| `sso_sma150_off_tmf` | SSO | TMF | sma | 150 |
| `sso_sma200_off_tmf` | SSO | TMF | sma | 200 |
| `sso_sma250_off_tmf` | SSO | TMF | sma | 250 |
| `sso_ema50_off_tmf` | SSO | TMF | ema | 50 |
| `sso_ema100_off_tmf` | SSO | TMF | ema | 100 |
| `sso_ema150_off_tmf` | SSO | TMF | ema | 150 |
| `sso_ema200_off_tmf` | SSO | TMF | ema | 200 |
| `sso_ema250_off_tmf` | SSO | TMF | ema | 250 |
| `sso_sma50_off_zroz` | SSO | ZROZ | sma | 50 |
| `sso_sma100_off_zroz` | SSO | ZROZ | sma | 100 |
| `sso_sma150_off_zroz` | SSO | ZROZ | sma | 150 |
| `sso_sma200_off_zroz` | SSO | ZROZ | sma | 200 |
| `sso_sma250_off_zroz` | SSO | ZROZ | sma | 250 |
| `sso_ema50_off_zroz` | SSO | ZROZ | ema | 50 |
| `sso_ema100_off_zroz` | SSO | ZROZ | ema | 100 |
| `sso_ema150_off_zroz` | SSO | ZROZ | ema | 150 |
| `sso_ema200_off_zroz` | SSO | ZROZ | ema | 200 |
| `sso_ema250_off_zroz` | SSO | ZROZ | ema | 250 |
| `sso_sma50_off_edv` | SSO | EDV | sma | 50 |
| `sso_sma100_off_edv` | SSO | EDV | sma | 100 |
| `sso_sma150_off_edv` | SSO | EDV | sma | 150 |
| `sso_sma200_off_edv` | SSO | EDV | sma | 200 |
| `sso_sma250_off_edv` | SSO | EDV | sma | 250 |
| `sso_ema50_off_edv` | SSO | EDV | ema | 50 |
| `sso_ema100_off_edv` | SSO | EDV | ema | 100 |
| `sso_ema150_off_edv` | SSO | EDV | ema | 150 |
| `sso_ema200_off_edv` | SSO | EDV | ema | 200 |
| `sso_ema250_off_edv` | SSO | EDV | ema | 250 |
| `tqqq_sma50_off_bil` | TQQQ | BIL | sma | 50 |
| `tqqq_sma100_off_bil` | TQQQ | BIL | sma | 100 |
| `tqqq_sma150_off_bil` | TQQQ | BIL | sma | 150 |
| `tqqq_sma200_off_bil` | TQQQ | BIL | sma | 200 |
| `tqqq_sma250_off_bil` | TQQQ | BIL | sma | 250 |
| `tqqq_ema50_off_bil` | TQQQ | BIL | ema | 50 |
| `tqqq_ema100_off_bil` | TQQQ | BIL | ema | 100 |
| `tqqq_ema150_off_bil` | TQQQ | BIL | ema | 150 |
| `tqqq_ema200_off_bil` | TQQQ | BIL | ema | 200 |
| `tqqq_ema250_off_bil` | TQQQ | BIL | ema | 250 |
| `tqqq_sma50_off_ief` | TQQQ | IEF | sma | 50 |
| `tqqq_sma100_off_ief` | TQQQ | IEF | sma | 100 |
| `tqqq_sma150_off_ief` | TQQQ | IEF | sma | 150 |
| `tqqq_sma200_off_ief` | TQQQ | IEF | sma | 200 |
| `tqqq_sma250_off_ief` | TQQQ | IEF | sma | 250 |
| `tqqq_ema50_off_ief` | TQQQ | IEF | ema | 50 |
| `tqqq_ema100_off_ief` | TQQQ | IEF | ema | 100 |
| `tqqq_ema150_off_ief` | TQQQ | IEF | ema | 150 |
| `tqqq_ema200_off_ief` | TQQQ | IEF | ema | 200 |
| `tqqq_ema250_off_ief` | TQQQ | IEF | ema | 250 |
| `tqqq_sma50_off_tlt` | TQQQ | TLT | sma | 50 |
| `tqqq_sma100_off_tlt` | TQQQ | TLT | sma | 100 |
| `tqqq_sma150_off_tlt` | TQQQ | TLT | sma | 150 |
| `tqqq_sma200_off_tlt` | TQQQ | TLT | sma | 200 |
| `tqqq_sma250_off_tlt` | TQQQ | TLT | sma | 250 |
| `tqqq_ema50_off_tlt` | TQQQ | TLT | ema | 50 |
| `tqqq_ema100_off_tlt` | TQQQ | TLT | ema | 100 |
| `tqqq_ema150_off_tlt` | TQQQ | TLT | ema | 150 |
| `tqqq_ema200_off_tlt` | TQQQ | TLT | ema | 200 |
| `tqqq_ema250_off_tlt` | TQQQ | TLT | ema | 250 |
| `tqqq_sma50_off_tmf` | TQQQ | TMF | sma | 50 |
| `tqqq_sma100_off_tmf` | TQQQ | TMF | sma | 100 |
| `tqqq_sma150_off_tmf` | TQQQ | TMF | sma | 150 |
| `tqqq_sma200_off_tmf` | TQQQ | TMF | sma | 200 |
| `tqqq_sma250_off_tmf` | TQQQ | TMF | sma | 250 |
| `tqqq_ema50_off_tmf` | TQQQ | TMF | ema | 50 |
| `tqqq_ema100_off_tmf` | TQQQ | TMF | ema | 100 |
| `tqqq_ema150_off_tmf` | TQQQ | TMF | ema | 150 |
| `tqqq_ema200_off_tmf` | TQQQ | TMF | ema | 200 |
| `tqqq_ema250_off_tmf` | TQQQ | TMF | ema | 250 |
| `tqqq_sma50_off_zroz` | TQQQ | ZROZ | sma | 50 |
| `tqqq_sma100_off_zroz` | TQQQ | ZROZ | sma | 100 |
| `tqqq_sma150_off_zroz` | TQQQ | ZROZ | sma | 150 |
| `tqqq_sma200_off_zroz` | TQQQ | ZROZ | sma | 200 |
| `tqqq_sma250_off_zroz` | TQQQ | ZROZ | sma | 250 |
| `tqqq_ema50_off_zroz` | TQQQ | ZROZ | ema | 50 |
| `tqqq_ema100_off_zroz` | TQQQ | ZROZ | ema | 100 |
| `tqqq_ema150_off_zroz` | TQQQ | ZROZ | ema | 150 |
| `tqqq_ema200_off_zroz` | TQQQ | ZROZ | ema | 200 |
| `tqqq_ema250_off_zroz` | TQQQ | ZROZ | ema | 250 |
| `tqqq_sma50_off_edv` | TQQQ | EDV | sma | 50 |
| `tqqq_sma100_off_edv` | TQQQ | EDV | sma | 100 |
| `tqqq_sma150_off_edv` | TQQQ | EDV | sma | 150 |
| `tqqq_sma200_off_edv` | TQQQ | EDV | sma | 200 |
| `tqqq_sma250_off_edv` | TQQQ | EDV | sma | 250 |
| `tqqq_ema50_off_edv` | TQQQ | EDV | ema | 50 |
| `tqqq_ema100_off_edv` | TQQQ | EDV | ema | 100 |
| `tqqq_ema150_off_edv` | TQQQ | EDV | ema | 150 |
| `tqqq_ema200_off_edv` | TQQQ | EDV | ema | 200 |
| `tqqq_ema250_off_edv` | TQQQ | EDV | ema | 250 |
| `qld_sma50_off_bil` | QLD | BIL | sma | 50 |
| `qld_sma100_off_bil` | QLD | BIL | sma | 100 |
| `qld_sma150_off_bil` | QLD | BIL | sma | 150 |
| `qld_sma200_off_bil` | QLD | BIL | sma | 200 |
| `qld_sma250_off_bil` | QLD | BIL | sma | 250 |
| `qld_ema50_off_bil` | QLD | BIL | ema | 50 |
| `qld_ema100_off_bil` | QLD | BIL | ema | 100 |
| `qld_ema150_off_bil` | QLD | BIL | ema | 150 |
| `qld_ema200_off_bil` | QLD | BIL | ema | 200 |
| `qld_ema250_off_bil` | QLD | BIL | ema | 250 |
| `qld_sma50_off_ief` | QLD | IEF | sma | 50 |
| `qld_sma100_off_ief` | QLD | IEF | sma | 100 |
| `qld_sma150_off_ief` | QLD | IEF | sma | 150 |
| `qld_sma200_off_ief` | QLD | IEF | sma | 200 |
| `qld_sma250_off_ief` | QLD | IEF | sma | 250 |
| `qld_ema50_off_ief` | QLD | IEF | ema | 50 |
| `qld_ema100_off_ief` | QLD | IEF | ema | 100 |
| `qld_ema150_off_ief` | QLD | IEF | ema | 150 |
| `qld_ema200_off_ief` | QLD | IEF | ema | 200 |
| `qld_ema250_off_ief` | QLD | IEF | ema | 250 |
| `qld_sma50_off_tlt` | QLD | TLT | sma | 50 |
| `qld_sma100_off_tlt` | QLD | TLT | sma | 100 |
| `qld_sma150_off_tlt` | QLD | TLT | sma | 150 |
| `qld_sma200_off_tlt` | QLD | TLT | sma | 200 |
| `qld_sma250_off_tlt` | QLD | TLT | sma | 250 |
| `qld_ema50_off_tlt` | QLD | TLT | ema | 50 |
| `qld_ema100_off_tlt` | QLD | TLT | ema | 100 |
| `qld_ema150_off_tlt` | QLD | TLT | ema | 150 |
| `qld_ema200_off_tlt` | QLD | TLT | ema | 200 |
| `qld_ema250_off_tlt` | QLD | TLT | ema | 250 |
| `qld_sma50_off_tmf` | QLD | TMF | sma | 50 |
| `qld_sma100_off_tmf` | QLD | TMF | sma | 100 |
| `qld_sma150_off_tmf` | QLD | TMF | sma | 150 |
| `qld_sma200_off_tmf` | QLD | TMF | sma | 200 |
| `qld_sma250_off_tmf` | QLD | TMF | sma | 250 |
| `qld_ema50_off_tmf` | QLD | TMF | ema | 50 |
| `qld_ema100_off_tmf` | QLD | TMF | ema | 100 |
| `qld_ema150_off_tmf` | QLD | TMF | ema | 150 |
| `qld_ema200_off_tmf` | QLD | TMF | ema | 200 |
| `qld_ema250_off_tmf` | QLD | TMF | ema | 250 |
| `qld_sma50_off_zroz` | QLD | ZROZ | sma | 50 |
| `qld_sma100_off_zroz` | QLD | ZROZ | sma | 100 |
| `qld_sma150_off_zroz` | QLD | ZROZ | sma | 150 |
| `qld_sma200_off_zroz` | QLD | ZROZ | sma | 200 |
| `qld_sma250_off_zroz` | QLD | ZROZ | sma | 250 |
| `qld_ema50_off_zroz` | QLD | ZROZ | ema | 50 |
| `qld_ema100_off_zroz` | QLD | ZROZ | ema | 100 |
| `qld_ema150_off_zroz` | QLD | ZROZ | ema | 150 |
| `qld_ema200_off_zroz` | QLD | ZROZ | ema | 200 |
| `qld_ema250_off_zroz` | QLD | ZROZ | ema | 250 |
| `qld_sma50_off_edv` | QLD | EDV | sma | 50 |
| `qld_sma100_off_edv` | QLD | EDV | sma | 100 |
| `qld_sma150_off_edv` | QLD | EDV | sma | 150 |
| `qld_sma200_off_edv` | QLD | EDV | sma | 200 |
| `qld_sma250_off_edv` | QLD | EDV | sma | 250 |
| `qld_ema50_off_edv` | QLD | EDV | ema | 50 |
| `qld_ema100_off_edv` | QLD | EDV | ema | 100 |
| `qld_ema150_off_edv` | QLD | EDV | ema | 150 |
| `qld_ema200_off_edv` | QLD | EDV | ema | 200 |
| `qld_ema250_off_edv` | QLD | EDV | ema | 250 |
| `soxl_sma50_off_bil` | SOXL | BIL | sma | 50 |
| `soxl_sma100_off_bil` | SOXL | BIL | sma | 100 |
| `soxl_sma150_off_bil` | SOXL | BIL | sma | 150 |
| `soxl_sma200_off_bil` | SOXL | BIL | sma | 200 |
| `soxl_sma250_off_bil` | SOXL | BIL | sma | 250 |
| `soxl_ema50_off_bil` | SOXL | BIL | ema | 50 |
| `soxl_ema100_off_bil` | SOXL | BIL | ema | 100 |
| `soxl_ema150_off_bil` | SOXL | BIL | ema | 150 |
| `soxl_ema200_off_bil` | SOXL | BIL | ema | 200 |
| `soxl_ema250_off_bil` | SOXL | BIL | ema | 250 |
| `soxl_sma50_off_ief` | SOXL | IEF | sma | 50 |
| `soxl_sma100_off_ief` | SOXL | IEF | sma | 100 |
| `soxl_sma150_off_ief` | SOXL | IEF | sma | 150 |
| `soxl_sma200_off_ief` | SOXL | IEF | sma | 200 |
| `soxl_sma250_off_ief` | SOXL | IEF | sma | 250 |
| `soxl_ema50_off_ief` | SOXL | IEF | ema | 50 |
| `soxl_ema100_off_ief` | SOXL | IEF | ema | 100 |
| `soxl_ema150_off_ief` | SOXL | IEF | ema | 150 |
| `soxl_ema200_off_ief` | SOXL | IEF | ema | 200 |
| `soxl_ema250_off_ief` | SOXL | IEF | ema | 250 |
| `soxl_sma50_off_tlt` | SOXL | TLT | sma | 50 |
| `soxl_sma100_off_tlt` | SOXL | TLT | sma | 100 |
| `soxl_sma150_off_tlt` | SOXL | TLT | sma | 150 |
| `soxl_sma200_off_tlt` | SOXL | TLT | sma | 200 |
| `soxl_sma250_off_tlt` | SOXL | TLT | sma | 250 |
| `soxl_ema50_off_tlt` | SOXL | TLT | ema | 50 |
| `soxl_ema100_off_tlt` | SOXL | TLT | ema | 100 |
| `soxl_ema150_off_tlt` | SOXL | TLT | ema | 150 |
| `soxl_ema200_off_tlt` | SOXL | TLT | ema | 200 |
| `soxl_ema250_off_tlt` | SOXL | TLT | ema | 250 |
| `soxl_sma50_off_tmf` | SOXL | TMF | sma | 50 |
| `soxl_sma100_off_tmf` | SOXL | TMF | sma | 100 |
| `soxl_sma150_off_tmf` | SOXL | TMF | sma | 150 |
| `soxl_sma200_off_tmf` | SOXL | TMF | sma | 200 |
| `soxl_sma250_off_tmf` | SOXL | TMF | sma | 250 |
| `soxl_ema50_off_tmf` | SOXL | TMF | ema | 50 |
| `soxl_ema100_off_tmf` | SOXL | TMF | ema | 100 |
| `soxl_ema150_off_tmf` | SOXL | TMF | ema | 150 |
| `soxl_ema200_off_tmf` | SOXL | TMF | ema | 200 |
| `soxl_ema250_off_tmf` | SOXL | TMF | ema | 250 |
| `soxl_sma50_off_zroz` | SOXL | ZROZ | sma | 50 |
| `soxl_sma100_off_zroz` | SOXL | ZROZ | sma | 100 |
| `soxl_sma150_off_zroz` | SOXL | ZROZ | sma | 150 |
| `soxl_sma200_off_zroz` | SOXL | ZROZ | sma | 200 |
| `soxl_sma250_off_zroz` | SOXL | ZROZ | sma | 250 |
| `soxl_ema50_off_zroz` | SOXL | ZROZ | ema | 50 |
| `soxl_ema100_off_zroz` | SOXL | ZROZ | ema | 100 |
| `soxl_ema150_off_zroz` | SOXL | ZROZ | ema | 150 |
| `soxl_ema200_off_zroz` | SOXL | ZROZ | ema | 200 |
| `soxl_ema250_off_zroz` | SOXL | ZROZ | ema | 250 |
| `soxl_sma50_off_edv` | SOXL | EDV | sma | 50 |
| `soxl_sma100_off_edv` | SOXL | EDV | sma | 100 |
| `soxl_sma150_off_edv` | SOXL | EDV | sma | 150 |
| `soxl_sma200_off_edv` | SOXL | EDV | sma | 200 |
| `soxl_sma250_off_edv` | SOXL | EDV | sma | 250 |
| `soxl_ema50_off_edv` | SOXL | EDV | ema | 50 |
| `soxl_ema100_off_edv` | SOXL | EDV | ema | 100 |
| `soxl_ema150_off_edv` | SOXL | EDV | ema | 150 |
| `soxl_ema200_off_edv` | SOXL | EDV | ema | 200 |
| `soxl_ema250_off_edv` | SOXL | EDV | ema | 250 |
| `ugl_sma50_off_bil` | UGL | BIL | sma | 50 |
| `ugl_sma100_off_bil` | UGL | BIL | sma | 100 |
| `ugl_sma150_off_bil` | UGL | BIL | sma | 150 |
| `ugl_sma200_off_bil` | UGL | BIL | sma | 200 |
| `ugl_sma250_off_bil` | UGL | BIL | sma | 250 |
| `ugl_ema50_off_bil` | UGL | BIL | ema | 50 |
| `ugl_ema100_off_bil` | UGL | BIL | ema | 100 |
| `ugl_ema150_off_bil` | UGL | BIL | ema | 150 |
| `ugl_ema200_off_bil` | UGL | BIL | ema | 200 |
| `ugl_ema250_off_bil` | UGL | BIL | ema | 250 |
| `ugl_sma50_off_ief` | UGL | IEF | sma | 50 |
| `ugl_sma100_off_ief` | UGL | IEF | sma | 100 |
| `ugl_sma150_off_ief` | UGL | IEF | sma | 150 |
| `ugl_sma200_off_ief` | UGL | IEF | sma | 200 |
| `ugl_sma250_off_ief` | UGL | IEF | sma | 250 |
| `ugl_ema50_off_ief` | UGL | IEF | ema | 50 |
| `ugl_ema100_off_ief` | UGL | IEF | ema | 100 |
| `ugl_ema150_off_ief` | UGL | IEF | ema | 150 |
| `ugl_ema200_off_ief` | UGL | IEF | ema | 200 |
| `ugl_ema250_off_ief` | UGL | IEF | ema | 250 |
| `ugl_sma50_off_tlt` | UGL | TLT | sma | 50 |
| `ugl_sma100_off_tlt` | UGL | TLT | sma | 100 |
| `ugl_sma150_off_tlt` | UGL | TLT | sma | 150 |
| `ugl_sma200_off_tlt` | UGL | TLT | sma | 200 |
| `ugl_sma250_off_tlt` | UGL | TLT | sma | 250 |
| `ugl_ema50_off_tlt` | UGL | TLT | ema | 50 |
| `ugl_ema100_off_tlt` | UGL | TLT | ema | 100 |
| `ugl_ema150_off_tlt` | UGL | TLT | ema | 150 |
| `ugl_ema200_off_tlt` | UGL | TLT | ema | 200 |
| `ugl_ema250_off_tlt` | UGL | TLT | ema | 250 |
| `ugl_sma50_off_tmf` | UGL | TMF | sma | 50 |
| `ugl_sma100_off_tmf` | UGL | TMF | sma | 100 |
| `ugl_sma150_off_tmf` | UGL | TMF | sma | 150 |
| `ugl_sma200_off_tmf` | UGL | TMF | sma | 200 |
| `ugl_sma250_off_tmf` | UGL | TMF | sma | 250 |
| `ugl_ema50_off_tmf` | UGL | TMF | ema | 50 |
| `ugl_ema100_off_tmf` | UGL | TMF | ema | 100 |
| `ugl_ema150_off_tmf` | UGL | TMF | ema | 150 |
| `ugl_ema200_off_tmf` | UGL | TMF | ema | 200 |
| `ugl_ema250_off_tmf` | UGL | TMF | ema | 250 |
| `ugl_sma50_off_zroz` | UGL | ZROZ | sma | 50 |
| `ugl_sma100_off_zroz` | UGL | ZROZ | sma | 100 |
| `ugl_sma150_off_zroz` | UGL | ZROZ | sma | 150 |
| `ugl_sma200_off_zroz` | UGL | ZROZ | sma | 200 |
| `ugl_sma250_off_zroz` | UGL | ZROZ | sma | 250 |
| `ugl_ema50_off_zroz` | UGL | ZROZ | ema | 50 |
| `ugl_ema100_off_zroz` | UGL | ZROZ | ema | 100 |
| `ugl_ema150_off_zroz` | UGL | ZROZ | ema | 150 |
| `ugl_ema200_off_zroz` | UGL | ZROZ | ema | 200 |
| `ugl_ema250_off_zroz` | UGL | ZROZ | ema | 250 |
| `ugl_sma50_off_edv` | UGL | EDV | sma | 50 |
| `ugl_sma100_off_edv` | UGL | EDV | sma | 100 |
| `ugl_sma150_off_edv` | UGL | EDV | sma | 150 |
| `ugl_sma200_off_edv` | UGL | EDV | sma | 200 |
| `ugl_sma250_off_edv` | UGL | EDV | sma | 250 |
| `ugl_ema50_off_edv` | UGL | EDV | ema | 50 |
| `ugl_ema100_off_edv` | UGL | EDV | ema | 100 |
| `ugl_ema150_off_edv` | UGL | EDV | ema | 150 |
| `ugl_ema200_off_edv` | UGL | EDV | ema | 200 |
| `ugl_ema250_off_edv` | UGL | EDV | ema | 250 |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `upro_sma50_off_bil` | 0.365 | 0.383 | 0.534 | 0.660 | 6.67% | 7.08% | 12.25% | 16.44% | -79.6% | -79.6% | -63.2% | -50.6% |
| `upro_sma100_off_bil` | 0.356 | 0.346 | 0.458 | 0.458 | 6.40% | 5.88% | 9.77% | 9.80% | -84.2% | -84.2% | -58.5% | -58.5% |
| `upro_sma150_off_bil` | 0.467 | 0.436 | 0.575 | 0.623 | 10.18% | 8.93% | 13.71% | 15.32% | -78.1% | -78.1% | -51.3% | -51.3% |
| `upro_sma200_off_bil` | 0.550 | 0.509 | 0.635 | 0.689 | 13.28% | 11.63% | 16.14% | 18.40% | -79.2% | -79.2% | -60.2% | -60.2% |
| `upro_sma250_off_bil` | 0.496 | 0.455 | 0.481 | 0.565 | 11.47% | 9.81% | 10.72% | 13.82% | -72.8% | -72.8% | -60.5% | -55.9% |
| `upro_ema50_off_bil` | 0.361 | 0.340 | 0.458 | 0.550 | 6.53% | 5.69% | 9.63% | 12.61% | -75.6% | -75.6% | -58.1% | -58.1% |
| `upro_ema100_off_bil` | 0.422 | 0.416 | 0.494 | 0.503 | 8.55% | 8.17% | 10.86% | 11.37% | -74.9% | -74.9% | -56.1% | -56.1% |
| `upro_ema150_off_bil` | 0.528 | 0.500 | 0.555 | 0.619 | 12.25% | 11.12% | 12.97% | 15.59% | -67.9% | -67.9% | -52.9% | -52.9% |
| `upro_ema200_off_bil` | 0.426 | 0.368 | 0.391 | 0.536 | 8.80% | 6.68% | 7.52% | 12.87% | -85.9% | -85.9% | -66.2% | -65.2% |
| `upro_ema250_off_bil` | 0.465 | 0.414 | 0.435 | 0.573 | 10.24% | 8.31% | 8.99% | 14.36% | -78.8% | -78.8% | -66.4% | -66.4% |
| `upro_sma50_off_ief` | 0.440 | 0.450 | 0.574 | 0.690 | 9.25% | 9.36% | 13.81% | 17.65% | -71.1% | -71.1% | -57.0% | -55.3% |
| `upro_sma100_off_ief` | 0.421 | 0.397 | 0.483 | 0.462 | 8.62% | 7.61% | 10.75% | 10.00% | -80.4% | -80.4% | -62.6% | -62.6% |
| `upro_sma150_off_ief` | 0.528 | 0.486 | 0.604 | 0.634 | 12.38% | 10.68% | 14.91% | 15.82% | -73.1% | -73.1% | -52.9% | -52.9% |
| `upro_sma200_off_ief` | 0.612 | 0.559 | 0.673 | 0.714 | 15.65% | 13.53% | 17.74% | 19.47% | -77.0% | -77.0% | -56.7% | -56.7% |
| `upro_sma250_off_ief` | 0.546 | 0.492 | 0.508 | 0.581 | 13.37% | 11.23% | 11.81% | 14.48% | -68.5% | -68.5% | -56.9% | -55.6% |
| `upro_ema50_off_ief` | 0.439 | 0.411 | 0.506 | 0.577 | 9.13% | 7.99% | 11.38% | 13.66% | -66.7% | -66.7% | -57.9% | -57.9% |
| `upro_ema100_off_ief` | 0.486 | 0.467 | 0.519 | 0.509 | 10.76% | 9.93% | 11.84% | 11.67% | -68.8% | -68.8% | -59.4% | -59.4% |
| `upro_ema150_off_ief` | 0.588 | 0.547 | 0.584 | 0.629 | 14.48% | 12.84% | 14.13% | 16.10% | -65.3% | -65.3% | -48.8% | -48.8% |
| `upro_ema200_off_ief` | 0.485 | 0.418 | 0.426 | 0.550 | 10.95% | 8.42% | 8.78% | 13.47% | -77.8% | -77.8% | -62.4% | -62.4% |
| `upro_ema250_off_ief` | 0.521 | 0.457 | 0.468 | 0.588 | 12.34% | 9.90% | 10.27% | 15.03% | -72.9% | -72.9% | -64.4% | -64.4% |
| `upro_sma50_off_tlt` | 0.454 | 0.455 | 0.551 | 0.659 | 9.86% | 9.67% | 13.40% | 17.16% | -70.5% | -70.5% | -62.8% | -62.8% |
| `upro_sma100_off_tlt` | 0.416 | 0.377 | 0.441 | 0.401 | 8.53% | 7.01% | 9.52% | 8.07% | -80.7% | -80.7% | -70.0% | -70.0% |
| `upro_sma150_off_tlt` | 0.523 | 0.472 | 0.576 | 0.599 | 12.41% | 10.38% | 14.35% | 14.94% | -73.4% | -73.4% | -61.0% | -61.0% |
| `upro_sma200_off_tlt` | 0.610 | 0.549 | 0.658 | 0.699 | 15.86% | 13.39% | 17.65% | 19.36% | -77.5% | -77.5% | -57.3% | -57.3% |
| `upro_sma250_off_tlt` | 0.548 | 0.485 | 0.499 | 0.571 | 13.64% | 11.10% | 11.78% | 14.38% | -69.1% | -69.1% | -59.6% | -57.0% |
| `upro_ema50_off_tlt` | 0.453 | 0.420 | 0.493 | 0.554 | 9.73% | 8.41% | 11.21% | 13.26% | -66.0% | -66.0% | -62.1% | -62.1% |
| `upro_ema100_off_tlt` | 0.481 | 0.450 | 0.477 | 0.454 | 10.75% | 9.50% | 10.68% | 9.98% | -67.6% | -67.6% | -66.7% | -66.7% |
| `upro_ema150_off_tlt` | 0.584 | 0.533 | 0.555 | 0.587 | 14.59% | 12.54% | 13.50% | 14.96% | -64.4% | -64.4% | -53.0% | -53.0% |
| `upro_ema200_off_tlt` | 0.480 | 0.403 | 0.401 | 0.512 | 10.93% | 7.96% | 8.12% | 12.34% | -78.0% | -78.0% | -63.5% | -61.8% |
| `upro_ema250_off_tlt` | 0.520 | 0.444 | 0.445 | 0.556 | 12.47% | 9.53% | 9.68% | 14.12% | -72.7% | -72.7% | -64.4% | -64.4% |
| `upro_sma50_off_tmf` | 0.506 | 0.478 | 0.466 | 0.524 | 13.08% | 11.59% | 11.70% | 14.30% | -82.8% | -82.8% | -82.8% | -82.8% |
| `upro_sma100_off_tmf` | 0.431 | 0.354 | 0.329 | 0.239 | 9.65% | 6.12% | 5.37% | 1.05% | -88.4% | -88.4% | -88.4% | -88.4% |
| `upro_sma150_off_tmf` | 0.518 | 0.444 | 0.469 | 0.452 | 13.65% | 10.08% | 11.83% | 10.37% | -83.9% | -83.9% | -83.9% | -83.9% |
| `upro_sma200_off_tmf` | 0.603 | 0.523 | 0.572 | 0.597 | 17.79% | 13.73% | 16.87% | 17.54% | -81.1% | -81.1% | -81.1% | -81.1% |
| `upro_sma250_off_tmf` | 0.540 | 0.455 | 0.436 | 0.485 | 14.80% | 10.62% | 10.31% | 11.99% | -78.9% | -78.9% | -78.9% | -78.9% |
| `upro_ema50_off_tmf` | 0.508 | 0.459 | 0.442 | 0.445 | 13.08% | 10.72% | 10.58% | 10.53% | -86.2% | -86.2% | -86.2% | -86.2% |
| `upro_ema100_off_tmf` | 0.482 | 0.420 | 0.357 | 0.298 | 11.95% | 8.98% | 6.68% | 3.74% | -86.5% | -86.5% | -86.5% | -86.5% |
| `upro_ema150_off_tmf` | 0.567 | 0.489 | 0.446 | 0.435 | 15.93% | 12.11% | 10.74% | 10.03% | -80.0% | -80.0% | -80.0% | -80.0% |
| `upro_ema200_off_tmf` | 0.481 | 0.385 | 0.336 | 0.388 | 11.96% | 7.43% | 5.71% | 7.81% | -81.4% | -81.4% | -81.4% | -81.4% |
| `upro_ema250_off_tmf` | 0.517 | 0.418 | 0.373 | 0.437 | 13.68% | 8.88% | 7.36% | 10.12% | -78.7% | -78.7% | -78.7% | -78.7% |
| `upro_sma50_off_zroz` | 0.537 | 0.513 | 0.545 | 0.641 | 13.57% | 12.24% | 13.87% | 17.28% | -68.0% | -68.0% | -68.0% | -68.0% |
| `upro_sma100_off_zroz` | 0.483 | 0.404 | 0.421 | 0.355 | 11.43% | 8.12% | 9.11% | 6.47% | -77.2% | -77.2% | -74.8% | -74.8% |
| `upro_sma150_off_zroz` | 0.575 | 0.499 | 0.572 | 0.579 | 15.16% | 11.79% | 14.94% | 14.73% | -70.7% | -70.7% | -67.5% | -67.5% |
| `upro_sma200_off_zroz` | 0.650 | 0.564 | 0.653 | 0.680 | 18.49% | 14.55% | 18.45% | 19.28% | -75.9% | -75.9% | -60.3% | -60.3% |
| `upro_sma250_off_zroz` | 0.589 | 0.500 | 0.505 | 0.564 | 16.07% | 12.07% | 12.50% | 14.50% | -69.2% | -69.2% | -61.4% | -61.4% |
| `upro_ema50_off_zroz` | 0.538 | 0.487 | 0.508 | 0.547 | 13.47% | 11.21% | 12.36% | 13.55% | -69.4% | -69.4% | -69.4% | -69.4% |
| `upro_ema100_off_zroz` | 0.544 | 0.481 | 0.462 | 0.420 | 13.76% | 11.00% | 10.64% | 8.91% | -71.8% | -71.8% | -71.8% | -71.8% |
| `upro_ema150_off_zroz` | 0.628 | 0.548 | 0.543 | 0.555 | 17.33% | 13.71% | 13.80% | 14.21% | -61.4% | -61.4% | -60.1% | -60.1% |
| `upro_ema200_off_zroz` | 0.527 | 0.423 | 0.401 | 0.482 | 13.28% | 8.90% | 8.39% | 11.42% | -74.8% | -74.8% | -66.8% | -66.8% |
| `upro_ema250_off_zroz` | 0.563 | 0.456 | 0.437 | 0.531 | 14.86% | 10.23% | 9.76% | 13.45% | -71.4% | -71.4% | -65.7% | -65.7% |
| `upro_sma50_off_edv` | 0.454 | 0.455 | 0.551 | 0.659 | 9.86% | 9.67% | 13.40% | 17.16% | -70.5% | -70.5% | -62.8% | -62.8% |
| `upro_sma100_off_edv` | 0.416 | 0.377 | 0.441 | 0.401 | 8.53% | 7.01% | 9.52% | 8.07% | -80.7% | -80.7% | -70.0% | -70.0% |
| `upro_sma150_off_edv` | 0.523 | 0.472 | 0.576 | 0.599 | 12.41% | 10.38% | 14.35% | 14.94% | -73.4% | -73.4% | -61.0% | -61.0% |
| `upro_sma200_off_edv` | 0.610 | 0.549 | 0.658 | 0.699 | 15.86% | 13.39% | 17.65% | 19.36% | -77.5% | -77.5% | -57.3% | -57.3% |
| `upro_sma250_off_edv` | 0.548 | 0.485 | 0.499 | 0.571 | 13.64% | 11.10% | 11.78% | 14.38% | -69.1% | -69.1% | -59.6% | -57.0% |
| `upro_ema50_off_edv` | 0.453 | 0.420 | 0.493 | 0.554 | 9.73% | 8.41% | 11.21% | 13.26% | -66.0% | -66.0% | -62.1% | -62.1% |
| `upro_ema100_off_edv` | 0.481 | 0.450 | 0.477 | 0.454 | 10.75% | 9.50% | 10.68% | 9.98% | -67.6% | -67.6% | -66.7% | -66.7% |
| `upro_ema150_off_edv` | 0.584 | 0.533 | 0.555 | 0.587 | 14.59% | 12.54% | 13.50% | 14.96% | -64.4% | -64.4% | -53.0% | -53.0% |
| `upro_ema200_off_edv` | 0.480 | 0.403 | 0.401 | 0.512 | 10.93% | 7.96% | 8.12% | 12.34% | -78.0% | -78.0% | -63.5% | -61.8% |
| `upro_ema250_off_edv` | 0.520 | 0.444 | 0.445 | 0.556 | 12.47% | 9.53% | 9.68% | 14.12% | -72.7% | -72.7% | -64.4% | -64.4% |
| `sso_sma50_off_bil` | 0.416 | 0.398 | 0.519 | 0.645 | 6.84% | 6.25% | 9.00% | 11.73% | -66.1% | -66.1% | -51.8% | -40.1% |
| `sso_sma100_off_bil` | 0.487 | 0.471 | 0.590 | 0.551 | 8.60% | 8.06% | 10.85% | 10.04% | -66.5% | -66.5% | -38.5% | -38.5% |
| `sso_sma150_off_bil` | 0.526 | 0.494 | 0.549 | 0.596 | 9.62% | 8.70% | 9.93% | 11.02% | -64.6% | -64.6% | -51.7% | -51.7% |
| `sso_sma200_off_bil` | 0.636 | 0.607 | 0.645 | 0.710 | 12.50% | 11.69% | 12.39% | 14.30% | -43.4% | -43.4% | -42.2% | -42.2% |
| `sso_sma250_off_bil` | 0.649 | 0.610 | 0.612 | 0.680 | 13.03% | 12.00% | 11.79% | 13.82% | -42.5% | -42.5% | -41.3% | -41.3% |
| `sso_ema50_off_bil` | 0.522 | 0.513 | 0.636 | 0.740 | 9.21% | 8.79% | 11.66% | 13.98% | -64.0% | -64.0% | -42.7% | -37.7% |
| `sso_ema100_off_bil` | 0.483 | 0.473 | 0.595 | 0.652 | 8.48% | 8.10% | 10.96% | 12.57% | -73.1% | -73.1% | -40.7% | -38.3% |
| `sso_ema150_off_bil` | 0.578 | 0.549 | 0.625 | 0.719 | 10.85% | 10.02% | 11.68% | 14.27% | -58.4% | -58.4% | -40.8% | -40.8% |
| `sso_ema200_off_bil` | 0.595 | 0.556 | 0.569 | 0.637 | 11.53% | 10.49% | 10.60% | 12.57% | -45.1% | -45.1% | -41.0% | -41.0% |
| `sso_ema250_off_bil` | 0.643 | 0.613 | 0.587 | 0.676 | 12.93% | 12.17% | 11.18% | 13.84% | -38.6% | -38.6% | -38.1% | -38.1% |
| `sso_sma50_off_ief` | 0.521 | 0.498 | 0.586 | 0.678 | 9.42% | 8.64% | 10.82% | 12.74% | -53.7% | -53.7% | -46.6% | -46.6% |
| `sso_sma100_off_ief` | 0.566 | 0.534 | 0.617 | 0.543 | 10.66% | 9.69% | 11.79% | 10.01% | -59.4% | -59.4% | -43.1% | -43.1% |
| `sso_sma150_off_ief` | 0.595 | 0.542 | 0.569 | 0.591 | 11.49% | 10.02% | 10.65% | 11.06% | -56.2% | -56.2% | -48.9% | -48.9% |
| `sso_sma200_off_ief` | 0.700 | 0.652 | 0.667 | 0.721 | 14.37% | 13.01% | 13.23% | 14.76% | -41.7% | -41.7% | -41.7% | -41.7% |
| `sso_sma250_off_ief` | 0.710 | 0.653 | 0.632 | 0.691 | 14.87% | 13.29% | 12.54% | 14.25% | -41.7% | -41.7% | -40.7% | -40.7% |
| `sso_ema50_off_ief` | 0.631 | 0.606 | 0.696 | 0.775 | 11.97% | 11.12% | 13.39% | 15.09% | -54.7% | -54.7% | -43.1% | -43.1% |
| `sso_ema100_off_ief` | 0.566 | 0.536 | 0.621 | 0.656 | 10.61% | 9.73% | 11.86% | 12.86% | -66.5% | -66.5% | -41.0% | -41.0% |
| `sso_ema150_off_ief` | 0.658 | 0.609 | 0.651 | 0.722 | 13.01% | 11.65% | 12.58% | 14.56% | -56.5% | -56.5% | -42.6% | -42.6% |
| `sso_ema200_off_ief` | 0.656 | 0.602 | 0.589 | 0.640 | 13.29% | 11.81% | 11.35% | 12.79% | -43.9% | -43.9% | -38.5% | -38.5% |
| `sso_ema250_off_ief` | 0.702 | 0.653 | 0.601 | 0.663 | 14.69% | 13.38% | 11.78% | 13.64% | -39.8% | -39.8% | -39.8% | -39.8% |
| `sso_sma50_off_tlt` | 0.535 | 0.506 | 0.558 | 0.619 | 10.17% | 9.23% | 10.83% | 12.25% | -57.0% | -57.0% | -57.0% | -57.0% |
| `sso_sma100_off_tlt` | 0.541 | 0.490 | 0.542 | 0.441 | 10.43% | 8.97% | 10.55% | 7.97% | -61.1% | -61.1% | -52.9% | -52.9% |
| `sso_sma150_off_tlt` | 0.569 | 0.501 | 0.500 | 0.504 | 11.25% | 9.33% | 9.48% | 9.39% | -56.0% | -56.0% | -54.7% | -54.7% |
| `sso_sma200_off_tlt` | 0.681 | 0.618 | 0.616 | 0.664 | 14.43% | 12.61% | 12.63% | 13.99% | -51.2% | -51.2% | -51.2% | -51.2% |
| `sso_sma250_off_tlt` | 0.690 | 0.619 | 0.582 | 0.639 | 14.88% | 12.86% | 11.86% | 13.46% | -45.1% | -45.1% | -45.1% | -45.1% |
| `sso_ema50_off_tlt` | 0.637 | 0.602 | 0.656 | 0.723 | 12.68% | 11.55% | 13.28% | 14.95% | -55.3% | -55.3% | -55.3% | -55.3% |
| `sso_ema100_off_tlt` | 0.546 | 0.497 | 0.551 | 0.562 | 10.53% | 9.12% | 10.76% | 11.14% | -67.1% | -67.1% | -51.3% | -51.3% |
| `sso_ema150_off_tlt` | 0.632 | 0.569 | 0.579 | 0.635 | 12.88% | 11.08% | 11.49% | 12.98% | -55.6% | -55.6% | -49.8% | -49.8% |
| `sso_ema200_off_tlt` | 0.635 | 0.569 | 0.537 | 0.574 | 13.22% | 11.35% | 10.59% | 11.58% | -46.1% | -46.1% | -46.1% | -46.1% |
| `sso_ema250_off_tlt` | 0.676 | 0.613 | 0.542 | 0.593 | 14.53% | 12.74% | 10.80% | 12.25% | -50.4% | -50.4% | -50.4% | -50.4% |
| `sso_sma50_off_tmf` | 0.554 | 0.512 | 0.455 | 0.422 | 13.85% | 12.13% | 10.76% | 9.32% | -82.6% | -82.6% | -82.6% | -82.6% |
| `sso_sma100_off_tmf` | 0.483 | 0.397 | 0.347 | 0.195 | 11.15% | 7.85% | 6.54% | 0.67% | -79.6% | -79.6% | -79.6% | -79.6% |
| `sso_sma150_off_tmf` | 0.493 | 0.392 | 0.313 | 0.267 | 11.55% | 7.70% | 5.31% | 2.99% | -80.5% | -80.5% | -80.5% | -80.5% |
| `sso_sma200_off_tmf` | 0.588 | 0.494 | 0.429 | 0.453 | 15.26% | 11.51% | 9.71% | 10.09% | -81.0% | -81.0% | -81.0% | -81.0% |
| `sso_sma250_off_tmf` | 0.596 | 0.500 | 0.405 | 0.444 | 15.60% | 11.74% | 8.78% | 9.68% | -73.7% | -73.7% | -73.7% | -73.7% |
| `sso_ema50_off_tmf` | 0.631 | 0.565 | 0.508 | 0.515 | 16.69% | 14.02% | 12.81% | 12.98% | -84.5% | -84.5% | -84.5% | -84.5% |
| `sso_ema100_off_tmf` | 0.501 | 0.410 | 0.360 | 0.314 | 11.77% | 8.29% | 7.04% | 5.11% | -78.8% | -78.8% | -78.8% | -78.8% |
| `sso_ema150_off_tmf` | 0.557 | 0.463 | 0.378 | 0.380 | 13.96% | 10.28% | 7.72% | 7.23% | -75.1% | -75.1% | -75.1% | -75.1% |
| `sso_ema200_off_tmf` | 0.548 | 0.462 | 0.368 | 0.364 | 13.67% | 10.26% | 7.35% | 6.62% | -74.0% | -74.0% | -74.0% | -74.0% |
| `sso_ema250_off_tmf` | 0.576 | 0.484 | 0.356 | 0.355 | 14.82% | 11.12% | 6.90% | 6.29% | -76.7% | -76.7% | -76.7% | -76.7% |
| `sso_sma50_off_zroz` | 0.614 | 0.573 | 0.555 | 0.573 | 13.83% | 12.16% | 11.99% | 12.12% | -64.9% | -64.9% | -64.9% | -64.9% |
| `sso_sma100_off_zroz` | 0.587 | 0.495 | 0.494 | 0.361 | 13.05% | 9.95% | 10.22% | 6.25% | -59.7% | -59.7% | -59.7% | -59.7% |
| `sso_sma150_off_zroz` | 0.602 | 0.497 | 0.464 | 0.446 | 13.62% | 10.08% | 9.35% | 8.39% | -61.2% | -61.2% | -61.2% | -61.2% |
| `sso_sma200_off_zroz` | 0.701 | 0.603 | 0.581 | 0.623 | 16.95% | 13.42% | 12.91% | 13.76% | -59.4% | -59.4% | -59.4% | -59.4% |
| `sso_sma250_off_zroz` | 0.707 | 0.607 | 0.547 | 0.600 | 17.27% | 13.64% | 11.96% | 13.14% | -52.9% | -52.9% | -52.9% | -52.9% |
| `sso_ema50_off_zroz` | 0.718 | 0.653 | 0.641 | 0.690 | 16.93% | 14.43% | 14.47% | 15.49% | -64.8% | -64.8% | -64.8% | -64.8% |
| `sso_ema100_off_zroz` | 0.598 | 0.501 | 0.507 | 0.494 | 13.33% | 10.11% | 10.57% | 9.99% | -61.5% | -61.5% | -59.1% | -59.1% |
| `sso_ema150_off_zroz` | 0.663 | 0.566 | 0.530 | 0.561 | 15.52% | 12.11% | 11.30% | 11.76% | -56.3% | -56.3% | -56.3% | -56.3% |
| `sso_ema200_off_zroz` | 0.652 | 0.560 | 0.504 | 0.520 | 15.37% | 12.12% | 10.60% | 10.67% | -53.7% | -53.7% | -53.7% | -53.7% |
| `sso_ema250_off_zroz` | 0.697 | 0.602 | 0.509 | 0.534 | 16.98% | 13.54% | 10.82% | 11.19% | -57.5% | -57.5% | -57.5% | -57.5% |
| `sso_sma50_off_edv` | 0.535 | 0.506 | 0.558 | 0.619 | 10.17% | 9.23% | 10.83% | 12.25% | -57.0% | -57.0% | -57.0% | -57.0% |
| `sso_sma100_off_edv` | 0.541 | 0.490 | 0.542 | 0.441 | 10.43% | 8.97% | 10.55% | 7.97% | -61.1% | -61.1% | -52.9% | -52.9% |
| `sso_sma150_off_edv` | 0.569 | 0.501 | 0.500 | 0.504 | 11.25% | 9.33% | 9.48% | 9.39% | -56.0% | -56.0% | -54.7% | -54.7% |
| `sso_sma200_off_edv` | 0.681 | 0.618 | 0.616 | 0.664 | 14.43% | 12.61% | 12.63% | 13.99% | -51.2% | -51.2% | -51.2% | -51.2% |
| `sso_sma250_off_edv` | 0.690 | 0.619 | 0.582 | 0.639 | 14.88% | 12.86% | 11.86% | 13.46% | -45.1% | -45.1% | -45.1% | -45.1% |
| `sso_ema50_off_edv` | 0.637 | 0.602 | 0.656 | 0.723 | 12.68% | 11.55% | 13.28% | 14.95% | -55.3% | -55.3% | -55.3% | -55.3% |
| `sso_ema100_off_edv` | 0.546 | 0.497 | 0.551 | 0.562 | 10.53% | 9.12% | 10.76% | 11.14% | -67.1% | -67.1% | -51.3% | -51.3% |
| `sso_ema150_off_edv` | 0.632 | 0.569 | 0.579 | 0.635 | 12.88% | 11.08% | 11.49% | 12.98% | -55.6% | -55.6% | -49.8% | -49.8% |
| `sso_ema200_off_edv` | 0.635 | 0.569 | 0.537 | 0.574 | 13.22% | 11.35% | 10.59% | 11.58% | -46.1% | -46.1% | -46.1% | -46.1% |
| `sso_ema250_off_edv` | 0.676 | 0.613 | 0.542 | 0.593 | 14.53% | 12.74% | 10.80% | 12.25% | -50.4% | -50.4% | -50.4% | -50.4% |
| `tqqq_sma50_off_bil` | 0.642 | 0.613 | 0.665 | 0.792 | 20.52% | 18.93% | 19.93% | 25.22% | -86.5% | -86.5% | -65.1% | -56.8% |
| `tqqq_sma100_off_bil` | 0.600 | 0.594 | 0.552 | 0.605 | 18.44% | 18.31% | 15.06% | 17.32% | -87.3% | -87.3% | -63.6% | -51.0% |
| `tqqq_sma150_off_bil` | 0.578 | 0.565 | 0.537 | 0.701 | 17.30% | 16.73% | 14.54% | 22.41% | -81.0% | -81.0% | -77.5% | -60.4% |
| `tqqq_sma200_off_bil` | 0.594 | 0.602 | 0.645 | 0.829 | 18.35% | 18.86% | 20.09% | 30.07% | -80.6% | -80.6% | -76.7% | -54.5% |
| `tqqq_sma250_off_bil` | 0.562 | 0.567 | 0.620 | 0.747 | 16.60% | 16.86% | 18.90% | 25.95% | -83.2% | -83.2% | -57.2% | -54.7% |
| `tqqq_ema50_off_bil` | 0.528 | 0.516 | 0.514 | 0.616 | 14.42% | 13.71% | 13.07% | 17.23% | -82.0% | -82.0% | -62.4% | -60.7% |
| `tqqq_ema100_off_bil` | 0.600 | 0.598 | 0.487 | 0.579 | 18.27% | 18.34% | 12.06% | 16.30% | -69.8% | -69.8% | -66.2% | -61.3% |
| `tqqq_ema150_off_bil` | 0.601 | 0.581 | 0.515 | 0.665 | 18.45% | 17.40% | 13.31% | 20.72% | -70.0% | -70.0% | -69.6% | -64.7% |
| `tqqq_ema200_off_bil` | 0.559 | 0.554 | 0.455 | 0.702 | 16.28% | 15.98% | 10.63% | 22.89% | -92.0% | -92.0% | -83.5% | -65.7% |
| `tqqq_ema250_off_bil` | 0.553 | 0.548 | 0.518 | 0.730 | 15.98% | 15.69% | 13.54% | 25.24% | -91.3% | -91.3% | -68.9% | -54.3% |
| `tqqq_sma50_off_ief` | 0.684 | 0.648 | 0.684 | 0.798 | 22.85% | 20.93% | 21.00% | 25.67% | -81.7% | -81.7% | -62.8% | -62.8% |
| `tqqq_sma100_off_ief` | 0.645 | 0.629 | 0.573 | 0.617 | 20.96% | 20.33% | 16.15% | 17.92% | -84.9% | -84.9% | -59.7% | -52.6% |
| `tqqq_sma150_off_ief` | 0.622 | 0.598 | 0.558 | 0.707 | 19.77% | 18.66% | 15.69% | 22.81% | -73.8% | -73.8% | -73.8% | -61.9% |
| `tqqq_sma200_off_ief` | 0.630 | 0.626 | 0.654 | 0.824 | 20.46% | 20.34% | 20.67% | 29.90% | -73.6% | -73.6% | -73.6% | -56.1% |
| `tqqq_sma250_off_ief` | 0.593 | 0.587 | 0.626 | 0.738 | 18.40% | 18.08% | 19.34% | 25.48% | -83.3% | -83.3% | -56.5% | -56.5% |
| `tqqq_ema50_off_ief` | 0.578 | 0.553 | 0.538 | 0.629 | 16.98% | 15.68% | 14.27% | 17.90% | -73.6% | -73.6% | -66.2% | -66.2% |
| `tqqq_ema100_off_ief` | 0.645 | 0.632 | 0.505 | 0.589 | 20.74% | 20.28% | 12.99% | 16.85% | -63.0% | -63.0% | -63.0% | -58.1% |
| `tqqq_ema150_off_ief` | 0.646 | 0.616 | 0.531 | 0.667 | 20.98% | 19.39% | 14.20% | 20.96% | -66.7% | -66.7% | -66.7% | -62.3% |
| `tqqq_ema200_off_ief` | 0.595 | 0.578 | 0.459 | 0.694 | 18.26% | 17.35% | 10.94% | 22.52% | -89.7% | -89.7% | -82.2% | -67.4% |
| `tqqq_ema250_off_ief` | 0.588 | 0.573 | 0.523 | 0.719 | 17.96% | 17.13% | 13.84% | 24.69% | -87.9% | -87.9% | -67.6% | -54.8% |
| `tqqq_sma50_off_tlt` | 0.676 | 0.638 | 0.662 | 0.758 | 22.61% | 20.48% | 20.32% | 24.34% | -82.5% | -82.5% | -71.0% | -71.0% |
| `tqqq_sma100_off_tlt` | 0.646 | 0.620 | 0.561 | 0.597 | 21.13% | 19.92% | 15.79% | 17.29% | -85.7% | -85.7% | -61.8% | -61.8% |
| `tqqq_sma150_off_tlt` | 0.621 | 0.589 | 0.544 | 0.676 | 19.82% | 18.20% | 15.15% | 21.48% | -72.5% | -72.5% | -71.9% | -64.0% |
| `tqqq_sma200_off_tlt` | 0.628 | 0.614 | 0.637 | 0.792 | 20.45% | 19.67% | 20.05% | 28.43% | -73.8% | -73.8% | -72.2% | -58.2% |
| `tqqq_sma250_off_tlt` | 0.590 | 0.576 | 0.609 | 0.711 | 18.33% | 17.43% | 18.68% | 24.20% | -83.4% | -83.4% | -59.1% | -59.1% |
| `tqqq_ema50_off_tlt` | 0.574 | 0.543 | 0.517 | 0.596 | 16.87% | 15.19% | 13.54% | 16.79% | -73.3% | -73.3% | -72.7% | -72.7% |
| `tqqq_ema100_off_tlt` | 0.653 | 0.631 | 0.508 | 0.588 | 21.32% | 20.33% | 13.29% | 17.00% | -62.2% | -62.2% | -62.2% | -58.1% |
| `tqqq_ema150_off_tlt` | 0.650 | 0.611 | 0.524 | 0.652 | 21.32% | 19.18% | 14.00% | 20.45% | -66.9% | -66.9% | -66.9% | -63.9% |
| `tqqq_ema200_off_tlt` | 0.595 | 0.568 | 0.447 | 0.671 | 18.36% | 16.86% | 10.45% | 21.52% | -90.3% | -90.3% | -82.8% | -68.9% |
| `tqqq_ema250_off_tlt` | 0.587 | 0.563 | 0.504 | 0.686 | 17.96% | 16.58% | 13.11% | 23.11% | -87.7% | -87.7% | -69.0% | -64.0% |
| `tqqq_sma50_off_tmf` | 0.660 | 0.612 | 0.559 | 0.585 | 23.04% | 19.88% | 16.90% | 18.14% | -89.5% | -89.5% | -89.5% | -89.5% |
| `tqqq_sma100_off_tmf` | 0.657 | 0.603 | 0.496 | 0.496 | 22.96% | 19.58% | 13.37% | 13.18% | -85.3% | -85.3% | -85.0% | -85.0% |
| `tqqq_sma150_off_tmf` | 0.632 | 0.574 | 0.485 | 0.551 | 21.39% | 17.75% | 12.77% | 15.89% | -81.4% | -81.4% | -81.4% | -81.4% |
| `tqqq_sma200_off_tmf` | 0.628 | 0.580 | 0.547 | 0.643 | 21.21% | 17.97% | 16.35% | 21.55% | -80.2% | -80.2% | -80.2% | -80.2% |
| `tqqq_sma250_off_tmf` | 0.585 | 0.541 | 0.520 | 0.575 | 18.44% | 15.38% | 14.71% | 17.42% | -84.2% | -84.2% | -84.1% | -84.1% |
| `tqqq_ema50_off_tmf` | 0.584 | 0.527 | 0.444 | 0.470 | 18.21% | 14.62% | 10.55% | 11.77% | -89.5% | -89.5% | -89.5% | -89.5% |
| `tqqq_ema100_off_tmf` | 0.673 | 0.622 | 0.472 | 0.521 | 23.87% | 20.76% | 12.06% | 14.55% | -82.2% | -82.2% | -82.2% | -82.2% |
| `tqqq_ema150_off_tmf` | 0.665 | 0.600 | 0.465 | 0.549 | 23.47% | 19.25% | 11.65% | 16.19% | -82.5% | -82.5% | -82.5% | -82.5% |
| `tqqq_ema200_off_tmf` | 0.595 | 0.537 | 0.371 | 0.542 | 19.00% | 15.23% | 6.54% | 15.40% | -91.9% | -91.9% | -90.3% | -81.3% |
| `tqqq_ema250_off_tmf` | 0.584 | 0.533 | 0.409 | 0.540 | 18.33% | 14.90% | 8.51% | 15.70% | -87.1% | -87.1% | -85.6% | -85.6% |
| `tqqq_sma50_off_zroz` | 0.707 | 0.656 | 0.655 | 0.731 | 25.00% | 21.91% | 20.68% | 23.77% | -80.7% | -80.7% | -76.4% | -76.4% |
| `tqqq_sma100_off_zroz` | 0.694 | 0.639 | 0.563 | 0.581 | 24.50% | 21.30% | 16.29% | 16.81% | -84.5% | -84.5% | -67.9% | -67.9% |
| `tqqq_sma150_off_zroz` | 0.662 | 0.603 | 0.541 | 0.649 | 22.66% | 19.21% | 15.30% | 20.44% | -68.6% | -68.6% | -68.6% | -67.5% |
| `tqqq_sma200_off_zroz` | 0.666 | 0.619 | 0.624 | 0.755 | 23.15% | 20.20% | 19.83% | 26.80% | -72.4% | -72.4% | -67.8% | -59.5% |
| `tqqq_sma250_off_zroz` | 0.624 | 0.581 | 0.600 | 0.688 | 20.62% | 17.84% | 18.58% | 23.21% | -83.7% | -83.7% | -65.8% | -65.8% |
| `tqqq_ema50_off_zroz` | 0.621 | 0.562 | 0.517 | 0.582 | 19.84% | 16.41% | 13.88% | 16.51% | -77.6% | -77.6% | -77.6% | -77.6% |
| `tqqq_ema100_off_zroz` | 0.709 | 0.657 | 0.527 | 0.588 | 25.17% | 22.23% | 14.50% | 17.30% | -63.9% | -63.9% | -63.9% | -63.9% |
| `tqqq_ema150_off_zroz` | 0.703 | 0.637 | 0.532 | 0.640 | 25.05% | 21.06% | 14.75% | 20.19% | -64.2% | -64.2% | -64.2% | -64.2% |
| `tqqq_ema200_off_zroz` | 0.637 | 0.580 | 0.442 | 0.649 | 21.19% | 17.70% | 10.33% | 20.68% | -88.5% | -88.5% | -83.4% | -69.0% |
| `tqqq_ema250_off_zroz` | 0.627 | 0.577 | 0.491 | 0.659 | 20.68% | 17.52% | 12.74% | 21.83% | -85.3% | -85.3% | -70.6% | -69.8% |
| `tqqq_sma50_off_edv` | 0.676 | 0.638 | 0.662 | 0.758 | 22.61% | 20.48% | 20.32% | 24.34% | -82.5% | -82.5% | -71.0% | -71.0% |
| `tqqq_sma100_off_edv` | 0.646 | 0.620 | 0.561 | 0.597 | 21.13% | 19.92% | 15.79% | 17.29% | -85.7% | -85.7% | -61.8% | -61.8% |
| `tqqq_sma150_off_edv` | 0.621 | 0.589 | 0.544 | 0.676 | 19.82% | 18.20% | 15.15% | 21.48% | -72.5% | -72.5% | -71.9% | -64.0% |
| `tqqq_sma200_off_edv` | 0.628 | 0.614 | 0.637 | 0.792 | 20.45% | 19.67% | 20.05% | 28.43% | -73.8% | -73.8% | -72.2% | -58.2% |
| `tqqq_sma250_off_edv` | 0.590 | 0.576 | 0.609 | 0.711 | 18.33% | 17.43% | 18.68% | 24.20% | -83.4% | -83.4% | -59.1% | -59.1% |
| `tqqq_ema50_off_edv` | 0.574 | 0.543 | 0.517 | 0.596 | 16.87% | 15.19% | 13.54% | 16.79% | -73.3% | -73.3% | -72.7% | -72.7% |
| `tqqq_ema100_off_edv` | 0.653 | 0.631 | 0.508 | 0.588 | 21.32% | 20.33% | 13.29% | 17.00% | -62.2% | -62.2% | -62.2% | -58.1% |
| `tqqq_ema150_off_edv` | 0.650 | 0.611 | 0.524 | 0.652 | 21.32% | 19.18% | 14.00% | 20.45% | -66.9% | -66.9% | -66.9% | -63.9% |
| `tqqq_ema200_off_edv` | 0.595 | 0.568 | 0.447 | 0.671 | 18.36% | 16.86% | 10.45% | 21.52% | -90.3% | -90.3% | -82.8% | -68.9% |
| `tqqq_ema250_off_edv` | 0.587 | 0.563 | 0.504 | 0.686 | 17.96% | 16.58% | 13.11% | 23.11% | -87.7% | -87.7% | -69.0% | -64.0% |
| `qld_sma50_off_bil` | 0.688 | 0.660 | 0.653 | 0.772 | 18.11% | 17.23% | 14.82% | 17.88% | -68.1% | -68.1% | -41.5% | -37.9% |
| `qld_sma100_off_bil` | 0.669 | 0.653 | 0.581 | 0.663 | 17.55% | 17.30% | 13.06% | 15.46% | -60.4% | -60.4% | -50.2% | -39.2% |
| `qld_sma150_off_bil` | 0.580 | 0.570 | 0.545 | 0.676 | 14.48% | 14.26% | 12.28% | 16.43% | -79.4% | -79.4% | -56.6% | -47.6% |
| `qld_sma200_off_bil` | 0.678 | 0.687 | 0.816 | 0.904 | 18.63% | 19.34% | 21.78% | 25.24% | -75.6% | -75.6% | -44.5% | -44.5% |
| `qld_sma250_off_bil` | 0.678 | 0.685 | 0.738 | 0.817 | 19.01% | 19.67% | 19.13% | 22.45% | -69.7% | -69.7% | -44.5% | -44.5% |
| `qld_ema50_off_bil` | 0.561 | 0.537 | 0.589 | 0.704 | 13.35% | 12.59% | 12.87% | 16.01% | -79.0% | -79.0% | -40.5% | -40.5% |
| `qld_ema100_off_bil` | 0.648 | 0.646 | 0.628 | 0.707 | 16.72% | 16.88% | 14.60% | 17.05% | -68.7% | -68.7% | -43.7% | -43.7% |
| `qld_ema150_off_bil` | 0.677 | 0.673 | 0.628 | 0.776 | 18.04% | 18.19% | 14.85% | 19.94% | -58.7% | -58.7% | -52.5% | -40.2% |
| `qld_ema200_off_bil` | 0.625 | 0.625 | 0.633 | 0.805 | 16.47% | 16.74% | 15.27% | 21.68% | -72.7% | -72.7% | -47.5% | -39.2% |
| `qld_ema250_off_bil` | 0.600 | 0.588 | 0.599 | 0.737 | 15.77% | 15.48% | 14.28% | 19.67% | -78.5% | -78.5% | -44.7% | -44.7% |
| `qld_sma50_off_ief` | 0.740 | 0.704 | 0.675 | 0.784 | 20.21% | 19.03% | 15.75% | 18.47% | -61.7% | -61.7% | -47.4% | -47.4% |
| `qld_sma100_off_ief` | 0.730 | 0.703 | 0.617 | 0.687 | 20.01% | 19.34% | 14.43% | 16.39% | -52.5% | -52.5% | -45.7% | -45.7% |
| `qld_sma150_off_ief` | 0.634 | 0.607 | 0.559 | 0.659 | 16.59% | 15.76% | 12.89% | 15.98% | -73.8% | -73.8% | -50.3% | -50.3% |
| `qld_sma200_off_ief` | 0.724 | 0.718 | 0.829 | 0.897 | 20.61% | 20.73% | 22.53% | 25.15% | -75.0% | -75.0% | -44.3% | -44.3% |
| `qld_sma250_off_ief` | 0.713 | 0.705 | 0.738 | 0.793 | 20.59% | 20.63% | 19.37% | 21.70% | -69.5% | -69.5% | -46.0% | -46.0% |
| `qld_ema50_off_ief` | 0.633 | 0.590 | 0.624 | 0.724 | 16.03% | 14.57% | 14.15% | 16.80% | -74.2% | -74.2% | -50.7% | -50.7% |
| `qld_ema100_off_ief` | 0.705 | 0.688 | 0.649 | 0.706 | 18.96% | 18.59% | 15.49% | 17.19% | -62.7% | -62.7% | -44.4% | -44.4% |
| `qld_ema150_off_ief` | 0.736 | 0.714 | 0.646 | 0.776 | 20.44% | 19.92% | 15.65% | 20.09% | -56.9% | -56.9% | -51.1% | -40.2% |
| `qld_ema200_off_ief` | 0.661 | 0.645 | 0.623 | 0.769 | 18.01% | 17.63% | 15.15% | 20.48% | -69.9% | -69.9% | -45.1% | -44.1% |
| `qld_ema250_off_ief` | 0.637 | 0.607 | 0.595 | 0.704 | 17.32% | 16.35% | 14.35% | 18.54% | -76.0% | -76.0% | -46.1% | -46.1% |
| `qld_sma50_off_tlt` | 0.729 | 0.689 | 0.642 | 0.719 | 20.20% | 18.84% | 15.33% | 17.35% | -63.0% | -63.0% | -59.6% | -59.6% |
| `qld_sma100_off_tlt` | 0.728 | 0.690 | 0.605 | 0.667 | 20.31% | 19.18% | 14.52% | 16.39% | -57.1% | -57.1% | -57.1% | -57.1% |
| `qld_sma150_off_tlt` | 0.629 | 0.589 | 0.534 | 0.610 | 16.68% | 15.29% | 12.40% | 14.73% | -74.6% | -74.6% | -53.8% | -53.8% |
| `qld_sma200_off_tlt` | 0.719 | 0.699 | 0.799 | 0.854 | 20.74% | 20.25% | 22.11% | 24.21% | -75.3% | -75.3% | -47.7% | -47.7% |
| `qld_sma250_off_tlt` | 0.700 | 0.678 | 0.697 | 0.737 | 20.31% | 19.72% | 18.40% | 20.05% | -69.9% | -69.9% | -56.9% | -56.9% |
| `qld_ema50_off_tlt` | 0.624 | 0.570 | 0.585 | 0.668 | 16.00% | 14.10% | 13.45% | 15.82% | -74.7% | -74.7% | -62.1% | -62.1% |
| `qld_ema100_off_tlt` | 0.697 | 0.667 | 0.624 | 0.660 | 19.04% | 18.08% | 15.16% | 16.26% | -65.0% | -65.0% | -55.1% | -55.1% |
| `qld_ema150_off_tlt` | 0.736 | 0.700 | 0.625 | 0.742 | 20.82% | 19.67% | 15.39% | 19.44% | -57.8% | -57.8% | -51.0% | -48.6% |
| `qld_ema200_off_tlt` | 0.650 | 0.619 | 0.584 | 0.706 | 17.81% | 16.79% | 14.19% | 18.63% | -71.4% | -71.4% | -52.3% | -52.3% |
| `qld_ema250_off_tlt` | 0.623 | 0.580 | 0.555 | 0.647 | 17.00% | 15.40% | 13.27% | 16.75% | -76.2% | -76.2% | -56.8% | -56.8% |
| `qld_sma50_off_tmf` | 0.670 | 0.622 | 0.487 | 0.485 | 20.87% | 18.57% | 12.46% | 12.18% | -85.8% | -85.8% | -85.8% | -85.8% |
| `qld_sma100_off_tmf` | 0.704 | 0.641 | 0.518 | 0.536 | 22.55% | 19.66% | 13.86% | 14.50% | -82.7% | -82.7% | -82.7% | -82.7% |
| `qld_sma150_off_tmf` | 0.608 | 0.534 | 0.418 | 0.403 | 17.96% | 14.35% | 9.47% | 8.26% | -78.4% | -78.4% | -78.4% | -78.4% |
| `qld_sma200_off_tmf` | 0.683 | 0.627 | 0.638 | 0.640 | 21.84% | 19.04% | 19.40% | 18.98% | -78.9% | -78.9% | -78.9% | -78.9% |
| `qld_sma250_off_tmf` | 0.639 | 0.581 | 0.516 | 0.501 | 19.82% | 16.91% | 13.80% | 12.58% | -82.5% | -82.5% | -82.5% | -82.5% |
| `qld_ema50_off_tmf` | 0.614 | 0.525 | 0.453 | 0.472 | 18.04% | 13.84% | 10.93% | 11.59% | -86.6% | -86.6% | -86.6% | -86.6% |
| `qld_ema100_off_tmf` | 0.663 | 0.597 | 0.496 | 0.464 | 20.45% | 17.31% | 12.84% | 11.24% | -81.1% | -81.1% | -81.1% | -81.1% |
| `qld_ema150_off_tmf` | 0.717 | 0.641 | 0.505 | 0.562 | 23.23% | 19.54% | 13.22% | 15.24% | -78.9% | -78.9% | -78.9% | -78.9% |
| `qld_ema200_off_tmf` | 0.595 | 0.525 | 0.408 | 0.442 | 17.43% | 14.00% | 9.00% | 9.95% | -81.0% | -81.0% | -81.0% | -81.0% |
| `qld_ema250_off_tmf` | 0.575 | 0.493 | 0.392 | 0.410 | 16.50% | 12.49% | 8.33% | 8.57% | -82.4% | -82.4% | -82.4% | -82.4% |
| `qld_sma50_off_zroz` | 0.752 | 0.701 | 0.622 | 0.674 | 22.59% | 20.34% | 15.77% | 16.97% | -67.5% | -67.5% | -67.5% | -67.5% |
| `qld_sma100_off_zroz` | 0.769 | 0.702 | 0.610 | 0.654 | 23.46% | 20.65% | 15.65% | 16.77% | -64.2% | -64.2% | -64.2% | -64.2% |
| `qld_sma150_off_zroz` | 0.672 | 0.594 | 0.517 | 0.566 | 19.47% | 16.11% | 12.40% | 13.68% | -71.7% | -71.7% | -57.5% | -57.5% |
| `qld_sma200_off_zroz` | 0.752 | 0.695 | 0.771 | 0.812 | 23.43% | 20.88% | 22.31% | 23.50% | -75.0% | -75.0% | -54.7% | -54.7% |
| `qld_sma250_off_zroz` | 0.719 | 0.662 | 0.657 | 0.682 | 22.29% | 19.69% | 17.88% | 18.51% | -70.1% | -70.1% | -63.7% | -63.7% |
| `qld_ema50_off_zroz` | 0.680 | 0.585 | 0.565 | 0.624 | 19.32% | 15.35% | 13.71% | 15.24% | -70.0% | -70.0% | -69.8% | -69.8% |
| `qld_ema100_off_zroz` | 0.738 | 0.669 | 0.611 | 0.623 | 22.00% | 19.03% | 15.64% | 15.69% | -63.2% | -63.2% | -62.0% | -62.0% |
| `qld_ema150_off_zroz` | 0.787 | 0.710 | 0.615 | 0.716 | 24.45% | 21.05% | 15.92% | 19.25% | -58.0% | -58.0% | -56.8% | -56.8% |
| `qld_ema200_off_zroz` | 0.683 | 0.613 | 0.552 | 0.648 | 20.23% | 17.15% | 13.75% | 17.02% | -73.1% | -73.1% | -60.0% | -60.0% |
| `qld_ema250_off_zroz` | 0.649 | 0.566 | 0.517 | 0.591 | 18.95% | 15.24% | 12.49% | 15.04% | -76.2% | -76.2% | -63.7% | -63.7% |
| `qld_sma50_off_edv` | 0.729 | 0.689 | 0.642 | 0.719 | 20.20% | 18.84% | 15.33% | 17.35% | -63.0% | -63.0% | -59.6% | -59.6% |
| `qld_sma100_off_edv` | 0.728 | 0.690 | 0.605 | 0.667 | 20.31% | 19.18% | 14.52% | 16.39% | -57.1% | -57.1% | -57.1% | -57.1% |
| `qld_sma150_off_edv` | 0.629 | 0.589 | 0.534 | 0.610 | 16.68% | 15.29% | 12.40% | 14.73% | -74.6% | -74.6% | -53.8% | -53.8% |
| `qld_sma200_off_edv` | 0.719 | 0.699 | 0.799 | 0.854 | 20.74% | 20.25% | 22.11% | 24.21% | -75.3% | -75.3% | -47.7% | -47.7% |
| `qld_sma250_off_edv` | 0.700 | 0.678 | 0.697 | 0.737 | 20.31% | 19.72% | 18.40% | 20.05% | -69.9% | -69.9% | -56.9% | -56.9% |
| `qld_ema50_off_edv` | 0.624 | 0.570 | 0.585 | 0.668 | 16.00% | 14.10% | 13.45% | 15.82% | -74.7% | -74.7% | -62.1% | -62.1% |
| `qld_ema100_off_edv` | 0.697 | 0.667 | 0.624 | 0.660 | 19.04% | 18.08% | 15.16% | 16.26% | -65.0% | -65.0% | -55.1% | -55.1% |
| `qld_ema150_off_edv` | 0.736 | 0.700 | 0.625 | 0.742 | 20.82% | 19.67% | 15.39% | 19.44% | -57.8% | -57.8% | -51.0% | -48.6% |
| `qld_ema200_off_edv` | 0.650 | 0.619 | 0.584 | 0.706 | 17.81% | 16.79% | 14.19% | 18.63% | -71.4% | -71.4% | -52.3% | -52.3% |
| `qld_ema250_off_edv` | 0.623 | 0.580 | 0.555 | 0.647 | 17.00% | 15.40% | 13.27% | 16.75% | -76.2% | -76.2% | -56.8% | -56.8% |
| `soxl_sma50_off_bil` | 0.671 | 0.654 | 0.645 | 0.748 | 23.12% | 22.10% | 19.83% | 24.28% | -87.0% | -87.0% | -52.0% | -52.0% |
| `soxl_sma100_off_bil` | 0.598 | 0.586 | 0.545 | 0.648 | 18.83% | 18.11% | 14.58% | 20.26% | -94.8% | -94.8% | -75.0% | -57.7% |
| `soxl_sma150_off_bil` | 0.608 | 0.602 | 0.778 | 0.908 | 19.68% | 19.23% | 28.46% | 35.88% | -98.6% | -98.6% | -63.2% | -55.2% |
| `soxl_sma200_off_bil` | 0.627 | 0.641 | 0.680 | 0.809 | 21.09% | 22.03% | 22.97% | 30.46% | -94.3% | -94.3% | -63.3% | -57.7% |
| `soxl_sma250_off_bil` | 0.635 | 0.678 | 0.697 | 0.837 | 21.66% | 24.73% | 24.08% | 32.76% | -86.7% | -86.7% | -66.4% | -63.2% |
| `soxl_ema50_off_bil` | 0.549 | 0.527 | 0.588 | 0.702 | 15.95% | 14.56% | 17.02% | 22.24% | -96.1% | -96.1% | -62.9% | -58.6% |
| `soxl_ema100_off_bil` | 0.641 | 0.650 | 0.703 | 0.776 | 21.56% | 22.13% | 23.57% | 27.40% | -92.4% | -92.4% | -65.6% | -47.3% |
| `soxl_ema150_off_bil` | 0.611 | 0.606 | 0.709 | 0.848 | 19.85% | 19.50% | 24.48% | 32.49% | -95.2% | -95.2% | -64.7% | -55.5% |
| `soxl_ema200_off_bil` | 0.637 | 0.639 | 0.720 | 0.793 | 21.68% | 21.78% | 25.43% | 29.91% | -91.8% | -91.8% | -59.4% | -59.4% |
| `soxl_ema250_off_bil` | 0.711 | 0.711 | 0.710 | 0.837 | 26.96% | 27.17% | 25.05% | 33.15% | -86.4% | -86.4% | -62.7% | -62.7% |
| `soxl_sma50_off_ief` | 0.709 | 0.685 | 0.670 | 0.760 | 25.49% | 24.08% | 21.20% | 25.01% | -84.5% | -84.5% | -58.5% | -58.5% |
| `soxl_sma100_off_ief` | 0.631 | 0.610 | 0.555 | 0.642 | 20.85% | 19.55% | 15.12% | 20.01% | -92.4% | -92.4% | -70.8% | -55.5% |
| `soxl_sma150_off_ief` | 0.634 | 0.616 | 0.779 | 0.895 | 21.34% | 20.15% | 28.70% | 35.17% | -98.3% | -98.3% | -60.8% | -56.9% |
| `soxl_sma200_off_ief` | 0.650 | 0.653 | 0.685 | 0.794 | 22.61% | 22.88% | 23.36% | 29.62% | -93.1% | -93.1% | -59.9% | -59.5% |
| `soxl_sma250_off_ief` | 0.658 | 0.691 | 0.703 | 0.829 | 23.22% | 25.67% | 24.52% | 32.32% | -84.0% | -84.0% | -67.3% | -67.3% |
| `soxl_ema50_off_ief` | 0.588 | 0.556 | 0.605 | 0.711 | 18.24% | 16.25% | 18.02% | 22.77% | -94.6% | -94.6% | -63.9% | -63.9% |
| `soxl_ema100_off_ief` | 0.679 | 0.677 | 0.723 | 0.781 | 23.96% | 23.92% | 24.84% | 27.74% | -90.6% | -90.6% | -60.2% | -48.4% |
| `soxl_ema150_off_ief` | 0.636 | 0.620 | 0.707 | 0.831 | 21.47% | 20.42% | 24.52% | 31.53% | -94.2% | -94.2% | -61.4% | -57.1% |
| `soxl_ema200_off_ief` | 0.665 | 0.656 | 0.730 | 0.785 | 23.54% | 22.96% | 26.18% | 29.47% | -91.7% | -91.7% | -61.9% | -61.9% |
| `soxl_ema250_off_ief` | 0.733 | 0.724 | 0.719 | 0.831 | 28.60% | 28.09% | 25.70% | 32.83% | -86.3% | -86.3% | -65.6% | -65.6% |
| `soxl_sma50_off_tlt` | 0.708 | 0.680 | 0.656 | 0.722 | 25.53% | 23.89% | 20.81% | 23.55% | -84.9% | -84.9% | -66.7% | -66.7% |
| `soxl_sma100_off_tlt` | 0.624 | 0.593 | 0.526 | 0.596 | 20.46% | 18.57% | 13.73% | 17.86% | -92.3% | -92.3% | -70.3% | -63.1% |
| `soxl_sma150_off_tlt` | 0.632 | 0.603 | 0.763 | 0.867 | 21.24% | 19.37% | 28.04% | 33.79% | -98.4% | -98.4% | -61.2% | -60.8% |
| `soxl_sma200_off_tlt` | 0.646 | 0.641 | 0.669 | 0.764 | 22.42% | 22.05% | 22.65% | 28.03% | -93.4% | -93.4% | -63.8% | -63.8% |
| `soxl_sma250_off_tlt` | 0.657 | 0.682 | 0.691 | 0.812 | 23.23% | 25.06% | 24.07% | 31.43% | -84.4% | -84.4% | -71.1% | -71.1% |
| `soxl_ema50_off_tlt` | 0.590 | 0.551 | 0.591 | 0.680 | 18.38% | 15.98% | 17.49% | 21.60% | -94.4% | -94.4% | -70.9% | -70.9% |
| `soxl_ema100_off_tlt` | 0.681 | 0.670 | 0.711 | 0.756 | 24.16% | 23.52% | 24.45% | 26.71% | -90.9% | -90.9% | -59.9% | -57.9% |
| `soxl_ema150_off_tlt` | 0.630 | 0.604 | 0.680 | 0.790 | 21.10% | 19.43% | 23.18% | 29.34% | -94.4% | -94.4% | -62.0% | -61.9% |
| `soxl_ema200_off_tlt` | 0.661 | 0.643 | 0.713 | 0.760 | 23.34% | 22.16% | 25.36% | 28.08% | -91.7% | -91.7% | -66.2% | -66.2% |
| `soxl_ema250_off_tlt` | 0.728 | 0.710 | 0.699 | 0.803 | 28.32% | 27.14% | 24.68% | 31.23% | -86.2% | -86.2% | -71.4% | -71.4% |
| `soxl_sma50_off_tmf` | 0.711 | 0.670 | 0.592 | 0.582 | 26.99% | 24.09% | 18.97% | 18.06% | -86.7% | -86.7% | -86.7% | -86.7% |
| `soxl_sma100_off_tmf` | 0.619 | 0.559 | 0.436 | 0.441 | 20.75% | 16.62% | 8.97% | 10.04% | -87.6% | -87.6% | -84.1% | -84.1% |
| `soxl_sma150_off_tmf` | 0.630 | 0.566 | 0.670 | 0.719 | 21.53% | 16.99% | 24.08% | 26.55% | -98.3% | -98.3% | -80.3% | -80.3% |
| `soxl_sma200_off_tmf` | 0.639 | 0.601 | 0.591 | 0.624 | 22.32% | 19.46% | 19.12% | 20.50% | -92.3% | -92.3% | -85.0% | -85.0% |
| `soxl_sma250_off_tmf` | 0.658 | 0.651 | 0.623 | 0.707 | 23.69% | 23.14% | 21.17% | 26.08% | -87.2% | -87.2% | -87.2% | -87.2% |
| `soxl_ema50_off_tmf` | 0.612 | 0.547 | 0.523 | 0.557 | 20.23% | 15.82% | 14.90% | 16.61% | -92.5% | -92.5% | -87.9% | -87.9% |
| `soxl_ema100_off_tmf` | 0.701 | 0.658 | 0.654 | 0.645 | 26.44% | 23.39% | 22.89% | 22.04% | -88.8% | -88.8% | -82.0% | -82.0% |
| `soxl_ema150_off_tmf` | 0.621 | 0.563 | 0.570 | 0.623 | 20.88% | 16.73% | 17.74% | 20.42% | -93.1% | -93.1% | -80.9% | -80.9% |
| `soxl_ema200_off_tmf` | 0.663 | 0.615 | 0.642 | 0.644 | 24.00% | 20.37% | 22.37% | 21.85% | -91.7% | -91.7% | -85.3% | -85.3% |
| `soxl_ema250_off_tmf` | 0.719 | 0.670 | 0.623 | 0.690 | 28.37% | 24.59% | 21.20% | 24.99% | -88.1% | -88.1% | -88.1% | -88.1% |
| `soxl_sma50_off_zroz` | 0.743 | 0.700 | 0.660 | 0.695 | 28.30% | 25.48% | 21.58% | 22.69% | -84.4% | -84.4% | -72.6% | -72.6% |
| `soxl_sma100_off_zroz` | 0.661 | 0.601 | 0.516 | 0.562 | 23.07% | 19.18% | 13.36% | 16.25% | -89.1% | -89.1% | -68.9% | -68.9% |
| `soxl_sma150_off_zroz` | 0.665 | 0.603 | 0.751 | 0.840 | 23.64% | 19.43% | 27.85% | 32.59% | -98.3% | -98.3% | -63.1% | -63.1% |
| `soxl_sma200_off_zroz` | 0.674 | 0.639 | 0.664 | 0.736 | 24.54% | 22.03% | 22.75% | 26.60% | -92.8% | -92.8% | -69.4% | -69.4% |
| `soxl_sma250_off_zroz` | 0.685 | 0.681 | 0.685 | 0.790 | 25.40% | 25.18% | 24.11% | 30.37% | -83.8% | -83.8% | -73.4% | -73.4% |
| `soxl_ema50_off_zroz` | 0.640 | 0.574 | 0.593 | 0.654 | 21.68% | 17.46% | 18.01% | 20.68% | -92.9% | -92.9% | -76.1% | -76.1% |
| `soxl_ema100_off_zroz` | 0.726 | 0.684 | 0.713 | 0.738 | 27.54% | 24.70% | 25.12% | 26.05% | -89.7% | -89.7% | -64.5% | -64.5% |
| `soxl_ema150_off_zroz` | 0.660 | 0.604 | 0.659 | 0.751 | 23.29% | 19.49% | 22.36% | 27.26% | -93.7% | -93.7% | -64.3% | -64.3% |
| `soxl_ema200_off_zroz` | 0.694 | 0.647 | 0.709 | 0.737 | 25.84% | 22.50% | 25.56% | 26.91% | -91.7% | -91.7% | -70.8% | -70.8% |
| `soxl_ema250_off_zroz` | 0.751 | 0.703 | 0.685 | 0.774 | 30.29% | 26.81% | 24.25% | 29.54% | -86.1% | -86.1% | -75.9% | -75.9% |
| `soxl_sma50_off_edv` | 0.708 | 0.680 | 0.656 | 0.722 | 25.53% | 23.89% | 20.81% | 23.55% | -84.9% | -84.9% | -66.7% | -66.7% |
| `soxl_sma100_off_edv` | 0.624 | 0.593 | 0.526 | 0.596 | 20.46% | 18.57% | 13.73% | 17.86% | -92.3% | -92.3% | -70.3% | -63.1% |
| `soxl_sma150_off_edv` | 0.632 | 0.603 | 0.763 | 0.867 | 21.24% | 19.37% | 28.04% | 33.79% | -98.4% | -98.4% | -61.2% | -60.8% |
| `soxl_sma200_off_edv` | 0.646 | 0.641 | 0.669 | 0.764 | 22.42% | 22.05% | 22.65% | 28.03% | -93.4% | -93.4% | -63.8% | -63.8% |
| `soxl_sma250_off_edv` | 0.657 | 0.682 | 0.691 | 0.812 | 23.23% | 25.06% | 24.07% | 31.43% | -84.4% | -84.4% | -71.1% | -71.1% |
| `soxl_ema50_off_edv` | 0.590 | 0.551 | 0.591 | 0.680 | 18.38% | 15.98% | 17.49% | 21.60% | -94.4% | -94.4% | -70.9% | -70.9% |
| `soxl_ema100_off_edv` | 0.681 | 0.670 | 0.711 | 0.756 | 24.16% | 23.52% | 24.45% | 26.71% | -90.9% | -90.9% | -59.9% | -57.9% |
| `soxl_ema150_off_edv` | 0.630 | 0.604 | 0.680 | 0.790 | 21.10% | 19.43% | 23.18% | 29.34% | -94.4% | -94.4% | -62.0% | -61.9% |
| `soxl_ema200_off_edv` | 0.661 | 0.643 | 0.713 | 0.760 | 23.34% | 22.16% | 25.36% | 28.08% | -91.7% | -91.7% | -66.2% | -66.2% |
| `soxl_ema250_off_edv` | 0.728 | 0.710 | 0.699 | 0.803 | 28.32% | 27.14% | 24.68% | 31.23% | -86.2% | -86.2% | -71.4% | -71.4% |
| `ugl_sma50_off_bil` | 0.301 | 0.316 | 0.447 | 0.476 | 4.47% | 4.88% | 9.01% | 9.30% | -66.0% | -66.0% | -66.0% | -66.0% |
| `ugl_sma100_off_bil` | 0.288 | 0.281 | 0.454 | 0.474 | 4.17% | 3.98% | 9.41% | 9.46% | -68.1% | -68.1% | -65.4% | -65.4% |
| `ugl_sma150_off_bil` | 0.327 | 0.298 | 0.492 | 0.610 | 5.24% | 4.46% | 10.79% | 13.47% | -70.6% | -70.6% | -62.8% | -51.7% |
| `ugl_sma200_off_bil` | 0.335 | 0.333 | 0.535 | 0.557 | 5.47% | 5.45% | 12.30% | 11.87% | -72.2% | -72.2% | -57.2% | -57.2% |
| `ugl_sma250_off_bil` | 0.374 | 0.363 | 0.522 | 0.530 | 6.56% | 6.32% | 11.97% | 11.09% | -66.7% | -66.7% | -66.7% | -66.7% |
| `ugl_ema50_off_bil` | 0.318 | 0.347 | 0.484 | 0.470 | 4.95% | 5.71% | 10.18% | 9.20% | -64.4% | -64.4% | -64.4% | -64.4% |
| `ugl_ema100_off_bil` | 0.327 | 0.308 | 0.440 | 0.531 | 5.22% | 4.72% | 9.02% | 11.16% | -61.2% | -61.2% | -61.2% | -61.2% |
| `ugl_ema150_off_bil` | 0.398 | 0.394 | 0.534 | 0.602 | 7.27% | 7.18% | 12.30% | 13.22% | -56.8% | -56.8% | -56.8% | -50.3% |
| `ugl_ema200_off_bil` | 0.381 | 0.393 | 0.549 | 0.571 | 6.77% | 7.20% | 12.92% | 12.34% | -55.2% | -54.9% | -53.9% | -53.9% |
| `ugl_ema250_off_bil` | 0.428 | 0.432 | 0.574 | 0.545 | 8.15% | 8.36% | 13.90% | 11.64% | -58.8% | -58.8% | -58.8% | -58.8% |
| `ugl_sma50_off_ief` | 0.347 | 0.358 | 0.458 | 0.479 | 5.73% | 6.02% | 9.40% | 9.49% | -63.4% | -63.4% | -63.4% | -63.4% |
| `ugl_sma100_off_ief` | 0.355 | 0.341 | 0.480 | 0.463 | 6.00% | 5.64% | 10.29% | 9.26% | -63.7% | -63.7% | -63.7% | -63.7% |
| `ugl_sma150_off_ief` | 0.396 | 0.360 | 0.529 | 0.618 | 7.21% | 6.22% | 12.07% | 13.84% | -58.6% | -58.6% | -55.9% | -52.5% |
| `ugl_sma200_off_ief` | 0.418 | 0.410 | 0.578 | 0.579 | 7.84% | 7.66% | 13.84% | 12.63% | -57.5% | -57.5% | -53.7% | -53.7% |
| `ugl_sma250_off_ief` | 0.472 | 0.451 | 0.576 | 0.568 | 9.41% | 8.95% | 13.88% | 12.33% | -59.5% | -59.5% | -59.5% | -59.5% |
| `ugl_ema50_off_ief` | 0.376 | 0.395 | 0.499 | 0.468 | 6.54% | 7.07% | 10.74% | 9.23% | -60.8% | -60.8% | -60.8% | -60.8% |
| `ugl_ema100_off_ief` | 0.387 | 0.360 | 0.462 | 0.526 | 6.93% | 6.20% | 9.77% | 11.13% | -59.5% | -59.5% | -59.5% | -59.5% |
| `ugl_ema150_off_ief` | 0.467 | 0.456 | 0.563 | 0.605 | 9.32% | 9.02% | 13.34% | 13.42% | -53.2% | -53.2% | -53.2% | -53.2% |
| `ugl_ema200_off_ief` | 0.472 | 0.478 | 0.599 | 0.607 | 9.43% | 9.73% | 14.74% | 13.55% | -52.4% | -52.4% | -52.4% | -52.4% |
| `ugl_ema250_off_ief` | 0.520 | 0.513 | 0.621 | 0.581 | 10.91% | 10.86% | 15.65% | 12.82% | -52.7% | -52.7% | -52.7% | -52.7% |
| `ugl_sma50_off_tlt` | 0.366 | 0.368 | 0.443 | 0.440 | 6.36% | 6.42% | 9.13% | 8.70% | -63.5% | -63.5% | -63.5% | -63.5% |
| `ugl_sma100_off_tlt` | 0.382 | 0.359 | 0.485 | 0.427 | 6.85% | 6.23% | 10.64% | 8.45% | -63.6% | -63.6% | -63.6% | -63.6% |
| `ugl_sma150_off_tlt` | 0.414 | 0.370 | 0.536 | 0.583 | 7.88% | 6.58% | 12.54% | 13.15% | -58.5% | -58.5% | -58.5% | -58.5% |
| `ugl_sma200_off_tlt` | 0.450 | 0.434 | 0.599 | 0.569 | 8.89% | 8.52% | 14.84% | 12.66% | -56.8% | -56.8% | -56.8% | -56.8% |
| `ugl_sma250_off_tlt` | 0.508 | 0.479 | 0.604 | 0.584 | 10.69% | 9.95% | 15.14% | 13.17% | -56.0% | -56.0% | -56.0% | -56.0% |
| `ugl_ema50_off_tlt` | 0.404 | 0.415 | 0.496 | 0.437 | 7.45% | 7.79% | 10.89% | 8.64% | -59.5% | -59.5% | -59.5% | -59.5% |
| `ugl_ema100_off_tlt` | 0.405 | 0.365 | 0.456 | 0.486 | 7.55% | 6.41% | 9.74% | 10.27% | -60.2% | -60.2% | -60.2% | -60.2% |
| `ugl_ema150_off_tlt` | 0.491 | 0.470 | 0.568 | 0.570 | 10.20% | 9.61% | 13.75% | 12.70% | -60.0% | -60.0% | -60.0% | -60.0% |
| `ugl_ema200_off_tlt` | 0.508 | 0.507 | 0.629 | 0.617 | 10.71% | 10.81% | 16.06% | 14.26% | -57.4% | -57.4% | -57.4% | -57.4% |
| `ugl_ema250_off_tlt` | 0.551 | 0.535 | 0.646 | 0.588 | 12.05% | 11.71% | 16.81% | 13.39% | -56.0% | -56.0% | -56.0% | -56.0% |
| `ugl_sma50_off_tmf` | 0.365 | 0.347 | 0.338 | 0.280 | 6.88% | 6.16% | 5.77% | 3.44% | -77.5% | -77.5% | -77.5% | -77.5% |
| `ugl_sma100_off_tmf` | 0.427 | 0.388 | 0.435 | 0.264 | 9.25% | 7.75% | 9.85% | 2.85% | -81.6% | -81.6% | -81.6% | -81.6% |
| `ugl_sma150_off_tmf` | 0.455 | 0.396 | 0.509 | 0.424 | 10.34% | 8.06% | 13.06% | 9.00% | -76.6% | -76.6% | -76.6% | -76.6% |
| `ugl_sma200_off_tmf` | 0.528 | 0.502 | 0.606 | 0.473 | 13.13% | 12.14% | 17.25% | 10.99% | -76.7% | -76.7% | -76.7% | -76.7% |
| `ugl_sma250_off_tmf` | 0.613 | 0.571 | 0.649 | 0.554 | 16.47% | 14.84% | 19.09% | 14.29% | -65.2% | -65.2% | -65.2% | -65.2% |
| `ugl_ema50_off_tmf` | 0.429 | 0.414 | 0.411 | 0.285 | 9.34% | 8.77% | 8.84% | 3.69% | -77.1% | -77.1% | -77.1% | -77.1% |
| `ugl_ema100_off_tmf` | 0.428 | 0.365 | 0.393 | 0.315 | 9.28% | 6.84% | 8.07% | 4.91% | -79.8% | -79.8% | -79.8% | -79.8% |
| `ugl_ema150_off_tmf` | 0.531 | 0.491 | 0.528 | 0.408 | 13.31% | 11.74% | 13.84% | 8.32% | -79.2% | -79.2% | -79.2% | -79.2% |
| `ugl_ema200_off_tmf` | 0.602 | 0.589 | 0.665 | 0.567 | 16.09% | 15.61% | 19.90% | 14.95% | -74.1% | -74.1% | -74.1% | -74.1% |
| `ugl_ema250_off_tmf` | 0.637 | 0.602 | 0.677 | 0.546 | 17.43% | 16.07% | 20.36% | 13.99% | -68.0% | -68.0% | -68.0% | -68.0% |
| `ugl_sma50_off_zroz` | 0.424 | 0.412 | 0.428 | 0.401 | 8.52% | 8.10% | 8.94% | 7.80% | -64.6% | -64.6% | -64.6% | -64.6% |
| `ugl_sma100_off_zroz` | 0.462 | 0.421 | 0.496 | 0.384 | 9.82% | 8.43% | 11.42% | 7.31% | -65.2% | -65.2% | -65.2% | -65.2% |
| `ugl_sma150_off_zroz` | 0.484 | 0.419 | 0.555 | 0.539 | 10.61% | 8.40% | 13.65% | 12.22% | -62.6% | -62.6% | -62.6% | -62.6% |
| `ugl_sma200_off_zroz` | 0.543 | 0.512 | 0.638 | 0.555 | 12.54% | 11.48% | 16.79% | 12.71% | -61.2% | -61.2% | -61.2% | -61.2% |
| `ugl_sma250_off_zroz` | 0.611 | 0.563 | 0.649 | 0.595 | 14.93% | 13.25% | 17.28% | 14.06% | -53.9% | -53.9% | -53.9% | -53.9% |
| `ugl_ema50_off_zroz` | 0.481 | 0.474 | 0.498 | 0.399 | 10.39% | 10.11% | 11.38% | 7.75% | -59.6% | -59.2% | -59.2% | -59.2% |
| `ugl_ema100_off_zroz` | 0.479 | 0.410 | 0.456 | 0.436 | 10.39% | 8.08% | 10.01% | 9.02% | -63.0% | -63.0% | -63.0% | -63.0% |
| `ugl_ema150_off_zroz` | 0.571 | 0.530 | 0.585 | 0.526 | 13.61% | 12.12% | 14.84% | 11.72% | -64.7% | -64.7% | -64.7% | -64.7% |
| `ugl_ema200_off_zroz` | 0.609 | 0.593 | 0.675 | 0.618 | 14.89% | 14.28% | 18.33% | 14.89% | -61.4% | -61.4% | -61.4% | -61.4% |
| `ugl_ema250_off_zroz` | 0.648 | 0.609 | 0.683 | 0.588 | 16.27% | 14.89% | 18.73% | 13.87% | -58.8% | -58.8% | -58.8% | -58.8% |
| `ugl_sma50_off_edv` | 0.366 | 0.368 | 0.443 | 0.440 | 6.36% | 6.42% | 9.13% | 8.70% | -63.5% | -63.5% | -63.5% | -63.5% |
| `ugl_sma100_off_edv` | 0.382 | 0.359 | 0.485 | 0.427 | 6.85% | 6.23% | 10.64% | 8.45% | -63.6% | -63.6% | -63.6% | -63.6% |
| `ugl_sma150_off_edv` | 0.414 | 0.370 | 0.536 | 0.583 | 7.88% | 6.58% | 12.54% | 13.15% | -58.5% | -58.5% | -58.5% | -58.5% |
| `ugl_sma200_off_edv` | 0.450 | 0.434 | 0.599 | 0.569 | 8.89% | 8.52% | 14.84% | 12.66% | -56.8% | -56.8% | -56.8% | -56.8% |
| `ugl_sma250_off_edv` | 0.508 | 0.479 | 0.604 | 0.584 | 10.69% | 9.95% | 15.14% | 13.17% | -56.0% | -56.0% | -56.0% | -56.0% |
| `ugl_ema50_off_edv` | 0.404 | 0.415 | 0.496 | 0.437 | 7.45% | 7.79% | 10.89% | 8.64% | -59.5% | -59.5% | -59.5% | -59.5% |
| `ugl_ema100_off_edv` | 0.405 | 0.365 | 0.456 | 0.486 | 7.55% | 6.41% | 9.74% | 10.27% | -60.2% | -60.2% | -60.2% | -60.2% |
| `ugl_ema150_off_edv` | 0.491 | 0.470 | 0.568 | 0.570 | 10.20% | 9.61% | 13.75% | 12.70% | -60.0% | -60.0% | -60.0% | -60.0% |
| `ugl_ema200_off_edv` | 0.508 | 0.507 | 0.629 | 0.617 | 10.71% | 10.81% | 16.06% | 14.26% | -57.4% | -57.4% | -57.4% | -57.4% |
| `ugl_ema250_off_edv` | 0.551 | 0.535 | 0.646 | 0.588 | 12.05% | 11.71% | 16.81% | 13.39% | -56.0% | -56.0% | -56.0% | -56.0% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `upro_sma50_off_bil` | 0.520 | 0.7362 | 3/8 >SPY (MDD 76% warn) | 0.566 | 0.732 | 0.030 | 0.00pp | NEAR_FAIL |
| `upro_sma100_off_bil` | 0.520 | 0.7530 | 3/8 >SPY (MDD 82% warn) | 0.366 | 0.497 | 0.029 | 0.00pp | NEAR_FAIL |
| `upro_sma150_off_bil` | 0.520 | 0.4948 | 3/8 >SPY (MDD 78% warn) | 0.525 | 0.722 | 0.118 | 0.00pp | NEAR_FAIL |
| `upro_sma200_off_bil` | 0.520 | 0.2974 | 5/8 >SPY (MDD 79% warn) | 0.554 | 0.636 | 0.185 | 0.00pp | NEAR_FAIL |
| `upro_sma250_off_bil` | 0.520 | 0.4223 | 4/8 >SPY (MDD 69% warn) | 0.524 | 0.492 | 0.127 | 0.00pp | NEAR_FAIL |
| `upro_ema50_off_bil` | 0.520 | 0.7435 | 3/8 >SPY (MDD 72% warn) | 0.423 | 0.626 | 0.012 | 0.00pp | NEAR_FAIL |
| `upro_ema100_off_bil` | 0.520 | 0.6061 | 3/8 >SPY (MDD 73% warn) | 0.460 | 0.635 | 0.077 | 0.00pp | NEAR_FAIL |
| `upro_ema150_off_bil` | 0.520 | 0.3467 | 6/8 >SPY (MDD 68% warn) | 0.584 | 0.747 | 0.178 | 0.00pp | NEAR_FAIL |
| `upro_ema200_off_bil` | 0.520 | 0.5981 | 3/8 >SPY (MDD 77% warn) | 0.476 | 0.529 | 0.052 | 0.00pp | NEAR_FAIL |
| `upro_ema250_off_bil` | 0.520 | 0.5006 | 5/8 >SPY (MDD 78% warn) | 0.490 | 0.497 | 0.092 | 0.00pp | NEAR_FAIL |
| `upro_sma50_off_ief` | 0.520 | 0.5622 | 4/8 >SPY (MDD 70% warn) | 0.583 | 0.729 | 0.105 | 0.00pp | NEAR_FAIL |
| `upro_sma100_off_ief` | 0.520 | 0.6095 | 4/8 >SPY (MDD 78% warn) | 0.357 | 0.461 | 0.080 | 0.00pp | NEAR_FAIL |
| `upro_sma150_off_ief` | 0.520 | 0.3476 | 3/8 >SPY (MDD 73% warn) | 0.511 | 0.673 | 0.179 | 0.00pp | NEAR_FAIL |
| `upro_sma200_off_ief` | 0.520 | 0.1798 | 4/8 >SPY (MDD 77% warn) | 0.562 | 0.617 | 0.252 | 0.00pp | NEAR_FAIL |
| `upro_sma250_off_ief` | 0.520 | 0.3065 | 5/8 >SPY (MDD 68% warn) | 0.536 | 0.465 | 0.188 | 0.00pp | NEAR_FAIL |
| `upro_ema50_off_ief` | 0.520 | 0.5660 | 4/8 >SPY (MDD 66% warn) | 0.435 | 0.598 | 0.102 | 0.00pp | NEAR_FAIL |
| `upro_ema100_off_ief` | 0.520 | 0.4492 | 3/8 >SPY (MDD 66% warn) | 0.462 | 0.608 | 0.144 | 0.00pp | NEAR_FAIL |
| `upro_ema150_off_ief` | 0.520 | 0.2212 | 5/8 >SPY (MDD 65% warn) | 0.588 | 0.721 | 0.249 | 0.00pp | NEAR_FAIL |
| `upro_ema200_off_ief` | 0.520 | 0.4501 | 4/8 >SPY (MDD 76% warn) | 0.487 | 0.508 | 0.119 | 0.00pp | NEAR_FAIL |
| `upro_ema250_off_ief` | 0.520 | 0.3625 | 5/8 >SPY (MDD 73% warn) | 0.495 | 0.473 | 0.156 | 0.00pp | NEAR_FAIL |
| `upro_sma50_off_tlt` | 0.520 | 0.5279 | 4/8 >SPY (MDD 69% warn) | 0.502 | 0.618 | 0.104 | 0.00pp | NEAR_FAIL |
| `upro_sma100_off_tlt` | 0.520 | 0.6221 | 3/8 >SPY (MDD 79% warn) | 0.269 | 0.318 | 0.069 | 0.00pp | NEAR_FAIL |
| `upro_sma150_off_tlt` | 0.520 | 0.3579 | 4/8 >SPY (MDD 73% warn) | 0.445 | 0.549 | 0.178 | 0.00pp | NEAR_FAIL |
| `upro_sma200_off_tlt` | 0.520 | 0.1822 | 4/8 >SPY (MDD 77% warn) | 0.526 | 0.552 | 0.256 | 0.00pp | NEAR_FAIL |
| `upro_sma250_off_tlt` | 0.520 | 0.3023 | 5/8 >SPY (MDD 69% warn) | 0.514 | 0.410 | 0.198 | 0.00pp | NEAR_FAIL |
| `upro_ema50_off_tlt` | 0.520 | 0.5313 | 4/8 >SPY (MDD 65% warn) | 0.372 | 0.481 | 0.118 | 0.00pp | NEAR_FAIL |
| `upro_ema100_off_tlt` | 0.520 | 0.4615 | 3/8 >SPY (MDD 67% warn) | 0.388 | 0.470 | 0.145 | 0.00pp | NEAR_FAIL |
| `upro_ema150_off_tlt` | 0.520 | 0.2290 | 5/8 >SPY (MDD 64% warn) | 0.527 | 0.611 | 0.246 | 0.00pp | NEAR_FAIL |
| `upro_ema200_off_tlt` | 0.520 | 0.4620 | 4/8 >SPY (MDD 76% warn) | 0.436 | 0.416 | 0.114 | 0.00pp | NEAR_FAIL |
| `upro_ema250_off_tlt` | 0.520 | 0.3656 | 5/8 >SPY (MDD 73% warn) | 0.452 | 0.394 | 0.157 | 0.00pp | NEAR_FAIL |
| `upro_sma50_off_tmf` | 0.520 | 0.3975 | 4/8 >SPY (MDD 83% warn) | 0.307 | 0.332 | 0.176 | 0.00pp | NEAR_FAIL |
| `upro_sma100_off_tmf` | 0.520 | 0.5861 | 4/8 >SPY (MDD 88% warn) | 0.072 | 0.003 | 0.081 | 0.00pp | NEAR_FAIL |
| `upro_sma150_off_tmf` | 0.520 | 0.3689 | 6/8 >SPY (MDD 84% warn) | 0.243 | 0.198 | 0.183 | 0.00pp | NEAR_FAIL |
| `upro_sma200_off_tmf` | 0.520 | 0.1918 | 4/8 >SPY (MDD 81% warn) | 0.394 | 0.321 | 0.269 | 0.00pp | NEAR_FAIL |
| `upro_sma250_off_tmf` | 0.520 | 0.3188 | 5/8 >SPY (MDD 79% warn) | 0.410 | 0.209 | 0.205 | 0.00pp | NEAR_FAIL |
| `upro_ema50_off_tmf` | 0.520 | 0.3945 | 4/8 >SPY (MDD 86% warn) | 0.220 | 0.180 | 0.174 | 0.00pp | NEAR_FAIL |
| `upro_ema100_off_tmf` | 0.520 | 0.4567 | 3/8 >SPY (MDD 86% warn) | 0.208 | 0.145 | 0.138 | 0.00pp | NEAR_FAIL |
| `upro_ema150_off_tmf` | 0.520 | 0.2608 | 6/8 >SPY (MDD 80% warn) | 0.347 | 0.296 | 0.229 | 0.00pp | NEAR_FAIL |
| `upro_ema200_off_tmf` | 0.520 | 0.4603 | 3/8 >SPY (MDD 81% warn) | 0.300 | 0.170 | 0.130 | 0.00pp | NEAR_FAIL |
| `upro_ema250_off_tmf` | 0.520 | 0.3717 | 5/8 >SPY (MDD 79% warn) | 0.318 | 0.167 | 0.172 | 0.00pp | NEAR_FAIL |
| `upro_sma50_off_zroz` | 0.520 | 0.3244 | 5/8 >SPY (MDD 68% warn) | 0.436 | 0.525 | 0.201 | 0.00pp | NEAR_FAIL |
| `upro_sma100_off_zroz` | 0.520 | 0.4544 | 4/8 >SPY (MDD 75% warn) | 0.196 | 0.211 | 0.144 | 0.00pp | NEAR_FAIL |
| `upro_sma150_off_zroz` | 0.520 | 0.2447 | 6/8 >SPY (MDD 71% warn) | 0.389 | 0.443 | 0.225 | 0.00pp | NEAR_FAIL |
| `upro_sma200_off_zroz` | 0.520 | 0.1229 | 4/8 >SPY (MDD 76% warn) | 0.485 | 0.490 | 0.303 | 0.00pp | NEAR_FAIL |
| `upro_sma250_off_zroz` | 0.520 | 0.2174 | 5/8 >SPY (MDD 69% warn) | 0.485 | 0.355 | 0.241 | 0.00pp | NEAR_FAIL |
| `upro_ema50_off_zroz` | 0.520 | 0.3235 | 4/8 >SPY (MDD 69% warn) | 0.327 | 0.381 | 0.203 | 0.00pp | NEAR_FAIL |
| `upro_ema100_off_zroz` | 0.520 | 0.3101 | 4/8 >SPY (MDD 72% warn) | 0.332 | 0.363 | 0.208 | 0.00pp | NEAR_FAIL |
| `upro_ema150_off_zroz` | 0.520 | 0.1526 | 6/8 >SPY (MDD 61% warn) | 0.471 | 0.521 | 0.288 | 0.00pp | NEAR_FAIL |
| `upro_ema200_off_zroz` | 0.520 | 0.3497 | 4/8 >SPY (MDD 75% warn) | 0.388 | 0.340 | 0.178 | 0.00pp | NEAR_FAIL |
| `upro_ema250_off_zroz` | 0.520 | 0.2694 | 5/8 >SPY (MDD 71% warn) | 0.408 | 0.327 | 0.210 | 0.00pp | NEAR_FAIL |
| `upro_sma50_off_edv` | 0.520 | 0.5279 | 4/8 >SPY (MDD 69% warn) | 0.502 | 0.618 | 0.104 | 0.00pp | NEAR_FAIL |
| `upro_sma100_off_edv` | 0.520 | 0.6221 | 3/8 >SPY (MDD 79% warn) | 0.269 | 0.318 | 0.069 | 0.00pp | NEAR_FAIL |
| `upro_sma150_off_edv` | 0.520 | 0.3579 | 4/8 >SPY (MDD 73% warn) | 0.445 | 0.549 | 0.178 | 0.00pp | NEAR_FAIL |
| `upro_sma200_off_edv` | 0.520 | 0.1822 | 4/8 >SPY (MDD 77% warn) | 0.526 | 0.552 | 0.256 | 0.00pp | NEAR_FAIL |
| `upro_sma250_off_edv` | 0.520 | 0.3023 | 5/8 >SPY (MDD 69% warn) | 0.514 | 0.410 | 0.198 | 0.00pp | NEAR_FAIL |
| `upro_ema50_off_edv` | 0.520 | 0.5313 | 4/8 >SPY (MDD 65% warn) | 0.372 | 0.481 | 0.118 | 0.00pp | NEAR_FAIL |
| `upro_ema100_off_edv` | 0.520 | 0.4615 | 3/8 >SPY (MDD 67% warn) | 0.388 | 0.470 | 0.145 | 0.00pp | NEAR_FAIL |
| `upro_ema150_off_edv` | 0.520 | 0.2290 | 5/8 >SPY (MDD 64% warn) | 0.527 | 0.611 | 0.246 | 0.00pp | NEAR_FAIL |
| `upro_ema200_off_edv` | 0.520 | 0.4620 | 4/8 >SPY (MDD 76% warn) | 0.436 | 0.416 | 0.114 | 0.00pp | NEAR_FAIL |
| `upro_ema250_off_edv` | 0.520 | 0.3656 | 5/8 >SPY (MDD 73% warn) | 0.452 | 0.394 | 0.157 | 0.00pp | NEAR_FAIL |
| `sso_sma50_off_bil` | 0.520 | 0.6208 | 2/8 >SPY (MDD 63% warn) | 0.550 | 0.766 | 0.081 | 0.00pp | NEAR_FAIL |
| `sso_sma100_off_bil` | 0.520 | 0.4451 | 3/8 >SPY (MDD 66% warn) | 0.487 | 0.741 | 0.157 | 0.00pp | NEAR_FAIL |
| `sso_sma150_off_bil` | 0.520 | 0.3519 | 4/8 >SPY (MDD 65% warn) | 0.496 | 0.631 | 0.159 | 0.00pp | NEAR_FAIL |
| `sso_sma200_off_bil` | 0.520 | 0.1425 | 4/8 >SPY (MDD 43% warn) | 0.590 | 0.629 | 0.291 | 0.00pp | NEAR_FAIL |
| `sso_sma250_off_bil` | 0.520 | 0.1256 | 5/8 >SPY (MDD 43% warn) | 0.680 | 0.705 | 0.292 | 0.00pp | NEAR_FAIL |
| `sso_ema50_off_bil` | 0.520 | 0.3617 | 3/8 >SPY (MDD 64% warn) | 0.589 | 0.787 | 0.171 | 0.00pp | NEAR_FAIL |
| `sso_ema100_off_bil` | 0.520 | 0.4557 | 3/8 >SPY (MDD 73% warn) | 0.583 | 0.817 | 0.130 | 0.00pp | NEAR_FAIL |
| `sso_ema150_off_bil` | 0.520 | 0.2393 | 4/8 >SPY (MDD 58% warn) | 0.722 | 0.918 | 0.225 | 0.00pp | NEAR_FAIL |
| `sso_ema200_off_bil` | 0.520 | 0.2079 | 5/8 >SPY (MDD 45% warn) | 0.629 | 0.769 | 0.236 | 0.00pp | NEAR_FAIL |
| `sso_ema250_off_bil` | 0.520 | 0.1334 | 5/8 >SPY (MDD 39% warn) | 0.671 | 0.663 | 0.283 | 0.00pp | NEAR_FAIL |
| `sso_sma50_off_ief` | 0.520 | 0.3626 | 3/8 >SPY (MDD 54% warn) | 0.565 | 0.744 | 0.185 | 0.00pp | NEAR_FAIL |
| `sso_sma100_off_ief` | 0.520 | 0.2634 | 3/8 >SPY (MDD 57% warn) | 0.460 | 0.700 | 0.235 | 0.00pp | NEAR_FAIL |
| `sso_sma150_off_ief` | 0.520 | 0.2089 | 4/8 >SPY (MDD 56% warn) | 0.467 | 0.553 | 0.228 | 0.00pp | NEAR_FAIL |
| `sso_sma200_off_ief` | 0.520 | 0.0710 | 4/8 >SPY (MDD 42% warn) | 0.583 | 0.584 | 0.357 | 0.00pp | NEAR_FAIL |
| `sso_sma250_off_ief` | 0.520 | 0.0628 | 6/8 >SPY (MDD 42% warn) | 0.694 | 0.689 | 0.367 | 0.00pp | NEAR_FAIL |
| `sso_ema50_off_ief` | 0.520 | 0.1505 | 3/8 >SPY (MDD 53% warn) | 0.604 | 0.742 | 0.303 | 0.00pp | NEAR_FAIL |
| `sso_ema100_off_ief` | 0.520 | 0.2650 | 4/8 >SPY (MDD 66% warn) | 0.573 | 0.763 | 0.221 | 0.00pp | NEAR_FAIL |
| `sso_ema150_off_ief` | 0.520 | 0.1148 | 4/8 >SPY (MDD 57% warn) | 0.735 | 0.899 | 0.302 | 0.00pp | NEAR_FAIL |
| `sso_ema200_off_ief` | 0.520 | 0.1162 | 4/8 >SPY (MDD 44% warn) | 0.641 | 0.763 | 0.309 | 0.00pp | NEAR_FAIL |
| `sso_ema250_off_ief` | 0.520 | 0.0697 | 5/8 >SPY (MDD 40% warn) | 0.665 | 0.628 | 0.344 | 0.00pp | NEAR_FAIL |
| `sso_sma50_off_tlt` | 0.520 | 0.3300 | 3/8 >SPY (MDD 57% warn) | 0.437 | 0.562 | 0.197 | 0.00pp | NEAR_FAIL |
| `sso_sma100_off_tlt` | 0.520 | 0.3171 | 3/8 >SPY (MDD 59% warn) | 0.334 | 0.523 | 0.213 | 0.00pp | NEAR_FAIL |
| `sso_sma150_off_tlt` | 0.520 | 0.2582 | 4/8 >SPY (MDD 56% warn) | 0.339 | 0.353 | 0.211 | 0.00pp | NEAR_FAIL |
| `sso_sma200_off_tlt` | 0.520 | 0.0881 | 4/8 >SPY (MDD 51% warn) | 0.498 | 0.456 | 0.338 | 0.00pp | NEAR_FAIL |
| `sso_sma250_off_tlt` | 0.520 | 0.0794 | 5/8 >SPY (MDD 45% warn) | 0.625 | 0.574 | 0.339 | 0.00pp | NEAR_FAIL |
| `sso_ema50_off_tlt` | 0.520 | 0.1406 | 3/8 >SPY (MDD 55% warn) | 0.494 | 0.542 | 0.302 | 0.00pp | NEAR_FAIL |
| `sso_ema100_off_tlt` | 0.520 | 0.3057 | 5/8 >SPY (MDD 66% warn) | 0.446 | 0.555 | 0.203 | 0.00pp | NEAR_FAIL |
| `sso_ema150_off_tlt` | 0.520 | 0.1479 | 5/8 >SPY (MDD 56% warn) | 0.623 | 0.716 | 0.279 | 0.00pp | NEAR_FAIL |
| `sso_ema200_off_tlt` | 0.520 | 0.1435 | 4/8 >SPY (MDD 46% warn) | 0.560 | 0.643 | 0.298 | 0.00pp | NEAR_FAIL |
| `sso_ema250_off_tlt` | 0.520 | 0.0930 | 5/8 >SPY (MDD 50% warn) | 0.586 | 0.515 | 0.323 | 0.00pp | NEAR_FAIL |
| `sso_sma50_off_tmf` | 0.520 | 0.2859 | 5/8 >SPY (MDD 83% warn) | 0.187 | 0.187 | 0.222 | 0.00pp | NEAR_FAIL |
| `sso_sma100_off_tmf` | 0.520 | 0.4539 | 4/8 >SPY (MDD 80% warn) | 0.061 | 0.140 | 0.146 | 0.00pp | NEAR_FAIL |
| `sso_sma150_off_tmf` | 0.520 | 0.4299 | 5/8 >SPY (MDD 80% warn) | 0.059 | -0.052 | 0.140 | 0.00pp | FAIL |
| `sso_sma200_off_tmf` | 0.520 | 0.2181 | 4/8 >SPY (MDD 81% warn) | 0.264 | 0.138 | 0.247 | 0.00pp | NEAR_FAIL |
| `sso_sma250_off_tmf` | 0.520 | 0.2032 | 5/8 >SPY (MDD 74% warn) | 0.415 | 0.274 | 0.272 | 0.00pp | NEAR_FAIL |
| `sso_ema50_off_tmf` | 0.520 | 0.1462 | 4/8 >SPY (MDD 84% warn) | 0.252 | 0.128 | 0.292 | 0.00pp | NEAR_FAIL |
| `sso_ema100_off_tmf` | 0.520 | 0.4096 | 5/8 >SPY (MDD 79% warn) | 0.166 | 0.114 | 0.141 | 0.00pp | NEAR_FAIL |
| `sso_ema150_off_tmf` | 0.520 | 0.2805 | 6/8 >SPY (MDD 75% warn) | 0.352 | 0.303 | 0.190 | 0.00pp | NEAR_FAIL |
| `sso_ema200_off_tmf` | 0.520 | 0.3006 | 4/8 >SPY (MDD 74% warn) | 0.344 | 0.333 | 0.204 | 0.00pp | NEAR_FAIL |
| `sso_ema250_off_tmf` | 0.520 | 0.2406 | 5/8 >SPY (MDD 77% warn) | 0.347 | 0.211 | 0.238 | 0.00pp | NEAR_FAIL |
| `sso_sma50_off_zroz` | 0.520 | 0.1730 | 4/8 >SPY (MDD 65% warn) | 0.331 | 0.414 | 0.282 | 0.00pp | NEAR_FAIL |
| `sso_sma100_off_zroz` | 0.520 | 0.2201 | 4/8 >SPY (MDD 60% warn) | 0.234 | 0.391 | 0.255 | 0.00pp | NEAR_FAIL |
| `sso_sma150_off_zroz` | 0.520 | 0.1938 | 5/8 >SPY (MDD 61% warn) | 0.233 | 0.210 | 0.259 | 0.00pp | NEAR_FAIL |
| `sso_sma200_off_zroz` | 0.520 | 0.0676 | 4/8 >SPY (MDD 59% warn) | 0.430 | 0.370 | 0.371 | 0.00pp | NEAR_FAIL |
| `sso_sma250_off_zroz` | 0.520 | 0.0632 | 5/8 >SPY (MDD 53% warn) | 0.566 | 0.482 | 0.380 | 0.00pp | NEAR_FAIL |
| `sso_ema50_off_zroz` | 0.520 | 0.0546 | 4/8 >SPY (MDD 65% warn) | 0.415 | 0.389 | 0.378 | 0.00pp | NEAR_FAIL |
| `sso_ema100_off_zroz` | 0.520 | 0.2010 | 5/8 >SPY (MDD 60% warn) | 0.341 | 0.391 | 0.238 | 0.00pp | NEAR_FAIL |
| `sso_ema150_off_zroz` | 0.520 | 0.1049 | 6/8 >SPY (MDD 56% warn) | 0.522 | 0.576 | 0.298 | 0.00pp | NEAR_FAIL |
| `sso_ema200_off_zroz` | 0.520 | 0.1189 | 5/8 >SPY (MDD 54% warn) | 0.483 | 0.547 | 0.305 | 0.00pp | NEAR_FAIL |
| `sso_ema250_off_zroz` | 0.520 | 0.0714 | 5/8 >SPY (MDD 57% warn) | 0.514 | 0.424 | 0.354 | 0.00pp | NEAR_FAIL |
| `sso_sma50_off_edv` | 0.520 | 0.3300 | 3/8 >SPY (MDD 57% warn) | 0.437 | 0.562 | 0.197 | 0.00pp | NEAR_FAIL |
| `sso_sma100_off_edv` | 0.520 | 0.3171 | 3/8 >SPY (MDD 59% warn) | 0.334 | 0.523 | 0.213 | 0.00pp | NEAR_FAIL |
| `sso_sma150_off_edv` | 0.520 | 0.2582 | 4/8 >SPY (MDD 56% warn) | 0.339 | 0.353 | 0.211 | 0.00pp | NEAR_FAIL |
| `sso_sma200_off_edv` | 0.520 | 0.0881 | 4/8 >SPY (MDD 51% warn) | 0.498 | 0.456 | 0.338 | 0.00pp | NEAR_FAIL |
| `sso_sma250_off_edv` | 0.520 | 0.0794 | 5/8 >SPY (MDD 45% warn) | 0.625 | 0.574 | 0.339 | 0.00pp | NEAR_FAIL |
| `sso_ema50_off_edv` | 0.520 | 0.1406 | 3/8 >SPY (MDD 55% warn) | 0.494 | 0.542 | 0.302 | 0.00pp | NEAR_FAIL |
| `sso_ema100_off_edv` | 0.520 | 0.3057 | 5/8 >SPY (MDD 66% warn) | 0.446 | 0.555 | 0.203 | 0.00pp | NEAR_FAIL |
| `sso_ema150_off_edv` | 0.520 | 0.1479 | 5/8 >SPY (MDD 56% warn) | 0.623 | 0.716 | 0.279 | 0.00pp | NEAR_FAIL |
| `sso_ema200_off_edv` | 0.520 | 0.1435 | 4/8 >SPY (MDD 46% warn) | 0.560 | 0.643 | 0.298 | 0.00pp | NEAR_FAIL |
| `sso_ema250_off_edv` | 0.520 | 0.0930 | 5/8 >SPY (MDD 50% warn) | 0.586 | 0.515 | 0.323 | 0.00pp | NEAR_FAIL |
| `tqqq_sma50_off_bil` | 0.520 | 0.1326 | 4/8 >SPY (MDD 85% warn) | 0.699 | 0.816 | 0.276 | 0.00pp | NEAR_FAIL |
| `tqqq_sma100_off_bil` | 0.520 | 0.1979 | 7/8 >SPY (MDD 87% warn) | 0.523 | 0.578 | 0.247 | 0.00pp | NEAR_FAIL |
| `tqqq_sma150_off_bil` | 0.520 | 0.2387 | 6/8 >SPY (MDD 70% warn) | 0.777 | 0.898 | 0.208 | 0.00pp | NEAR_FAIL |
| `tqqq_sma200_off_bil` | 0.520 | 0.2094 | 6/8 >SPY (MDD 70% warn) | 0.877 | 0.864 | 0.209 | 0.00pp | NEAR_FAIL |
| `tqqq_sma250_off_bil` | 0.520 | 0.2719 | 7/8 >SPY (MDD 83% warn) | 0.794 | 0.850 | 0.173 | 0.00pp | NEAR_FAIL |
| `tqqq_ema50_off_bil` | 0.520 | 0.3458 | 5/8 >SPY (MDD 77% warn) | 0.584 | 0.654 | 0.164 | 0.00pp | NEAR_FAIL |
| `tqqq_ema100_off_bil` | 0.520 | 0.1975 | 7/8 >SPY (MDD 66% warn) | 0.519 | 0.679 | 0.238 | 0.00pp | NEAR_FAIL |
| `tqqq_ema150_off_bil` | 0.520 | 0.1958 | 5/8 >SPY (MDD 65% warn) | 0.658 | 0.826 | 0.232 | 0.00pp | NEAR_FAIL |
| `tqqq_ema200_off_bil` | 0.520 | 0.2772 | 7/8 >SPY (MDD 72% warn) | 0.808 | 0.823 | 0.176 | 0.00pp | NEAR_FAIL |
| `tqqq_ema250_off_bil` | 0.520 | 0.2909 | 7/8 >SPY (MDD 78% warn) | 0.753 | 0.807 | 0.169 | 0.00pp | NEAR_FAIL |
| `tqqq_sma50_off_ief` | 0.520 | 0.0849 | 5/8 >SPY (MDD 82% warn) | 0.695 | 0.783 | 0.319 | 0.00pp | MARGINAL |
| `tqqq_sma100_off_ief` | 0.520 | 0.1288 | 7/8 >SPY (MDD 85% warn) | 0.527 | 0.551 | 0.290 | 0.00pp | NEAR_FAIL |
| `tqqq_sma150_off_ief` | 0.520 | 0.1616 | 6/8 >SPY (MDD 64% warn) | 0.787 | 0.880 | 0.249 | 0.00pp | NEAR_FAIL |
| `tqqq_sma200_off_ief` | 0.520 | 0.1501 | 6/8 >SPY (MDD 68% warn) | 0.877 | 0.823 | 0.252 | 0.00pp | NEAR_FAIL |
| `tqqq_sma250_off_ief` | 0.520 | 0.2116 | 7/8 >SPY (MDD 83% warn) | 0.791 | 0.805 | 0.206 | 0.00pp | NEAR_FAIL |
| `tqqq_ema50_off_ief` | 0.520 | 0.2396 | 5/8 >SPY (MDD 71% warn) | 0.593 | 0.637 | 0.221 | 0.00pp | NEAR_FAIL |
| `tqqq_ema100_off_ief` | 0.520 | 0.1285 | 7/8 >SPY (MDD 58% warn) | 0.526 | 0.675 | 0.279 | 0.00pp | NEAR_FAIL |
| `tqqq_ema150_off_ief` | 0.520 | 0.1268 | 6/8 >SPY (MDD 62% warn) | 0.660 | 0.798 | 0.282 | 0.00pp | NEAR_FAIL |
| `tqqq_ema200_off_ief` | 0.520 | 0.2071 | 7/8 >SPY (MDD 69% warn) | 0.807 | 0.780 | 0.213 | 0.00pp | NEAR_FAIL |
| `tqqq_ema250_off_ief` | 0.520 | 0.2201 | 6/8 >SPY (MDD 77% warn) | 0.746 | 0.764 | 0.207 | 0.00pp | NEAR_FAIL |
| `tqqq_sma50_off_tlt` | 0.520 | 0.0922 | 5/8 >SPY (MDD 83% warn) | 0.630 | 0.690 | 0.321 | 0.00pp | MARGINAL |
| `tqqq_sma100_off_tlt` | 0.520 | 0.1277 | 6/8 >SPY (MDD 86% warn) | 0.504 | 0.488 | 0.300 | 0.00pp | NEAR_FAIL |
| `tqqq_sma150_off_tlt` | 0.520 | 0.1629 | 6/8 >SPY (MDD 65% warn) | 0.761 | 0.813 | 0.252 | 0.00pp | NEAR_FAIL |
| `tqqq_sma200_off_tlt` | 0.520 | 0.1528 | 6/8 >SPY (MDD 69% warn) | 0.849 | 0.752 | 0.245 | 0.00pp | NEAR_FAIL |
| `tqqq_sma250_off_tlt` | 0.520 | 0.2157 | 7/8 >SPY (MDD 83% warn) | 0.757 | 0.723 | 0.204 | 0.00pp | NEAR_FAIL |
| `tqqq_ema50_off_tlt` | 0.520 | 0.2476 | 5/8 >SPY (MDD 71% warn) | 0.548 | 0.565 | 0.220 | 0.00pp | NEAR_FAIL |
| `tqqq_ema100_off_tlt` | 0.520 | 0.1182 | 7/8 >SPY (MDD 60% warn) | 0.521 | 0.646 | 0.297 | 0.00pp | NEAR_FAIL |
| `tqqq_ema150_off_tlt` | 0.520 | 0.1220 | 7/8 >SPY (MDD 64% warn) | 0.645 | 0.747 | 0.285 | 0.00pp | NEAR_FAIL |
| `tqqq_ema200_off_tlt` | 0.520 | 0.2067 | 6/8 >SPY (MDD 67% warn) | 0.786 | 0.715 | 0.212 | 0.00pp | NEAR_FAIL |
| `tqqq_ema250_off_tlt` | 0.520 | 0.2225 | 6/8 >SPY (MDD 78% warn) | 0.710 | 0.679 | 0.200 | 0.00pp | NEAR_FAIL |
| `tqqq_sma50_off_tmf` | 0.520 | 0.1094 | 5/8 >SPY (MDD 89% warn) | 0.424 | 0.386 | 0.299 | 0.00pp | NEAR_FAIL |
| `tqqq_sma100_off_tmf` | 0.520 | 0.1132 | 6/8 >SPY (MDD 85% warn) | 0.402 | 0.269 | 0.319 | 0.00pp | NEAR_FAIL |
| `tqqq_sma150_off_tmf` | 0.520 | 0.1460 | 5/8 >SPY (MDD 81% warn) | 0.647 | 0.565 | 0.274 | 0.00pp | NEAR_FAIL |
| `tqqq_sma200_off_tmf` | 0.520 | 0.1526 | 6/8 >SPY (MDD 80% warn) | 0.713 | 0.473 | 0.262 | 0.00pp | NEAR_FAIL |
| `tqqq_sma250_off_tmf` | 0.520 | 0.2244 | 6/8 >SPY (MDD 84% warn) | 0.616 | 0.424 | 0.203 | 0.00pp | NEAR_FAIL |
| `tqqq_ema50_off_tmf` | 0.520 | 0.2261 | 5/8 >SPY (MDD 89% warn) | 0.407 | 0.333 | 0.227 | 0.00pp | NEAR_FAIL |
| `tqqq_ema100_off_tmf` | 0.520 | 0.0946 | 5/8 >SPY (MDD 82% warn) | 0.455 | 0.494 | 0.329 | 0.00pp | NEAR_FAIL |
| `tqqq_ema150_off_tmf` | 0.520 | 0.1037 | 6/8 >SPY (MDD 82% warn) | 0.547 | 0.516 | 0.309 | 0.00pp | NEAR_FAIL |
| `tqqq_ema200_off_tmf` | 0.520 | 0.2069 | 6/8 >SPY (MDD 81% warn) | 0.662 | 0.444 | 0.230 | 0.00pp | NEAR_FAIL |
| `tqqq_ema250_off_tmf` | 0.520 | 0.2267 | 5/8 >SPY (MDD 86% warn) | 0.564 | 0.383 | 0.199 | 0.00pp | NEAR_FAIL |
| `tqqq_sma50_off_zroz` | 0.520 | 0.0644 | 5/8 >SPY (MDD 81% warn) | 0.578 | 0.608 | 0.334 | 0.00pp | MARGINAL |
| `tqqq_sma100_off_zroz` | 0.520 | 0.0744 | 6/8 >SPY (MDD 85% warn) | 0.479 | 0.440 | 0.348 | 0.00pp | NEAR_FAIL |
| `tqqq_sma150_off_zroz` | 0.520 | 0.1071 | 6/8 >SPY (MDD 62% warn) | 0.734 | 0.759 | 0.304 | 0.00pp | NEAR_FAIL |
| `tqqq_sma200_off_zroz` | 0.520 | 0.1030 | 7/8 >SPY (MDD 70% warn) | 0.812 | 0.684 | 0.301 | 0.00pp | NEAR_FAIL |
| `tqqq_sma250_off_zroz` | 0.520 | 0.1592 | 6/8 >SPY (MDD 84% warn) | 0.721 | 0.652 | 0.240 | 0.00pp | NEAR_FAIL |
| `tqqq_ema50_off_zroz` | 0.520 | 0.1633 | 5/8 >SPY (MDD 76% warn) | 0.513 | 0.503 | 0.268 | 0.00pp | NEAR_FAIL |
| `tqqq_ema100_off_zroz` | 0.520 | 0.0620 | 5/8 >SPY (MDD 64% warn) | 0.508 | 0.620 | 0.359 | 0.00pp | NEAR_FAIL |
| `tqqq_ema150_off_zroz` | 0.520 | 0.0663 | 7/8 >SPY (MDD 64% warn) | 0.625 | 0.704 | 0.347 | 0.00pp | NEAR_FAIL |
| `tqqq_ema200_off_zroz` | 0.520 | 0.1387 | 6/8 >SPY (MDD 64% warn) | 0.762 | 0.660 | 0.272 | 0.00pp | NEAR_FAIL |
| `tqqq_ema250_off_zroz` | 0.520 | 0.1536 | 6/8 >SPY (MDD 78% warn) | 0.674 | 0.606 | 0.235 | 0.00pp | NEAR_FAIL |
| `tqqq_sma50_off_edv` | 0.520 | 0.0922 | 5/8 >SPY (MDD 83% warn) | 0.630 | 0.690 | 0.321 | 0.00pp | MARGINAL |
| `tqqq_sma100_off_edv` | 0.520 | 0.1277 | 6/8 >SPY (MDD 86% warn) | 0.504 | 0.488 | 0.300 | 0.00pp | NEAR_FAIL |
| `tqqq_sma150_off_edv` | 0.520 | 0.1629 | 6/8 >SPY (MDD 65% warn) | 0.761 | 0.813 | 0.252 | 0.00pp | NEAR_FAIL |
| `tqqq_sma200_off_edv` | 0.520 | 0.1528 | 6/8 >SPY (MDD 69% warn) | 0.849 | 0.752 | 0.245 | 0.00pp | NEAR_FAIL |
| `tqqq_sma250_off_edv` | 0.520 | 0.2157 | 7/8 >SPY (MDD 83% warn) | 0.757 | 0.723 | 0.204 | 0.00pp | NEAR_FAIL |
| `tqqq_ema50_off_edv` | 0.520 | 0.2476 | 5/8 >SPY (MDD 71% warn) | 0.548 | 0.565 | 0.220 | 0.00pp | NEAR_FAIL |
| `tqqq_ema100_off_edv` | 0.520 | 0.1182 | 7/8 >SPY (MDD 60% warn) | 0.521 | 0.646 | 0.297 | 0.00pp | NEAR_FAIL |
| `tqqq_ema150_off_edv` | 0.520 | 0.1220 | 7/8 >SPY (MDD 64% warn) | 0.645 | 0.747 | 0.285 | 0.00pp | NEAR_FAIL |
| `tqqq_ema200_off_edv` | 0.520 | 0.2067 | 6/8 >SPY (MDD 67% warn) | 0.786 | 0.715 | 0.212 | 0.00pp | NEAR_FAIL |
| `tqqq_ema250_off_edv` | 0.520 | 0.2225 | 6/8 >SPY (MDD 78% warn) | 0.710 | 0.679 | 0.200 | 0.00pp | NEAR_FAIL |
| `qld_sma50_off_bil` | 0.520 | 0.0799 | 6/8 >SPY (MDD 68% warn) | 0.708 | 0.796 | 0.348 | 0.00pp | MARGINAL |
| `qld_sma100_off_bil` | 0.520 | 0.0998 | 7/8 >SPY (MDD 60% warn) | 0.570 | 0.725 | 0.311 | 0.00pp | NEAR_FAIL |
| `qld_sma150_off_bil` | 0.520 | 0.2346 | 6/8 >SPY (MDD 78% warn) | 0.760 | 0.815 | 0.182 | 0.00pp | NEAR_FAIL |
| `qld_sma200_off_bil` | 0.520 | 0.0912 | 7/8 >SPY (MDD 76% warn) | 0.947 | 0.936 | 0.296 | 0.00pp | MARGINAL |
| `qld_sma250_off_bil` | 0.520 | 0.0905 | 7/8 >SPY (MDD 70% warn) | 0.833 | 0.876 | 0.315 | 0.00pp | MARGINAL |
| `qld_ema50_off_bil` | 0.520 | 0.2736 | 5/8 >SPY (MDD 79% warn) | 0.669 | 0.809 | 0.190 | 0.00pp | NEAR_FAIL |
| `qld_ema100_off_bil` | 0.520 | 0.1242 | 6/8 >SPY (MDD 69% warn) | 0.662 | 0.802 | 0.282 | 0.00pp | NEAR_FAIL |
| `qld_ema150_off_bil` | 0.520 | 0.0914 | 7/8 >SPY (MDD 58% warn) | 0.823 | 0.886 | 0.298 | 0.00pp | NEAR_FAIL |
| `qld_ema200_off_bil` | 0.520 | 0.1580 | 7/8 >SPY (MDD 71% warn) | 0.850 | 0.892 | 0.243 | 0.00pp | NEAR_FAIL |
| `qld_ema250_off_bil` | 0.520 | 0.1982 | 7/8 >SPY (MDD 79% warn) | 0.731 | 0.807 | 0.208 | 0.00pp | NEAR_FAIL |
| `qld_sma50_off_ief` | 0.520 | 0.0416 | 5/8 >SPY (MDD 62% warn) | 0.708 | 0.760 | 0.396 | 0.00pp | PROMISING |
| `qld_sma100_off_ief` | 0.520 | 0.0477 | 7/8 >SPY (MDD 52% warn) | 0.588 | 0.702 | 0.379 | 0.00pp | MARGINAL |
| `qld_sma150_off_ief` | 0.520 | 0.1445 | 6/8 >SPY (MDD 74% warn) | 0.753 | 0.767 | 0.234 | 0.00pp | NEAR_FAIL |
| `qld_sma200_off_ief` | 0.520 | 0.0525 | 7/8 >SPY (MDD 75% warn) | 0.939 | 0.870 | 0.350 | 0.00pp | PROMISING |
| `qld_sma250_off_ief` | 0.520 | 0.0597 | 7/8 >SPY (MDD 70% warn) | 0.817 | 0.816 | 0.353 | 0.00pp | MARGINAL |
| `qld_ema50_off_ief` | 0.520 | 0.1458 | 5/8 >SPY (MDD 74% warn) | 0.683 | 0.788 | 0.273 | 0.00pp | NEAR_FAIL |
| `qld_ema100_off_ief` | 0.520 | 0.0658 | 6/8 >SPY (MDD 63% warn) | 0.666 | 0.777 | 0.343 | 0.00pp | NEAR_FAIL |
| `qld_ema150_off_ief` | 0.520 | 0.0445 | 7/8 >SPY (MDD 57% warn) | 0.831 | 0.858 | 0.378 | 0.00pp | MARGINAL |
| `qld_ema200_off_ief` | 0.520 | 0.1089 | 7/8 >SPY (MDD 70% warn) | 0.826 | 0.823 | 0.293 | 0.00pp | NEAR_FAIL |
| `qld_ema250_off_ief` | 0.520 | 0.1410 | 6/8 >SPY (MDD 76% warn) | 0.702 | 0.747 | 0.254 | 0.00pp | NEAR_FAIL |
| `qld_sma50_off_tlt` | 0.520 | 0.0483 | 5/8 >SPY (MDD 63% warn) | 0.616 | 0.629 | 0.377 | 0.00pp | MARGINAL |
| `qld_sma100_off_tlt` | 0.520 | 0.0491 | 6/8 >SPY (MDD 57% warn) | 0.558 | 0.614 | 0.381 | 0.00pp | MARGINAL |
| `qld_sma150_off_tlt` | 0.520 | 0.1513 | 6/8 >SPY (MDD 75% warn) | 0.711 | 0.683 | 0.238 | 0.00pp | NEAR_FAIL |
| `qld_sma200_off_tlt` | 0.520 | 0.0556 | 7/8 >SPY (MDD 75% warn) | 0.887 | 0.755 | 0.350 | 0.00pp | MARGINAL |
| `qld_sma250_off_tlt` | 0.520 | 0.0702 | 6/8 >SPY (MDD 70% warn) | 0.762 | 0.708 | 0.331 | 0.00pp | NEAR_FAIL |
| `qld_ema50_off_tlt` | 0.520 | 0.1589 | 5/8 >SPY (MDD 75% warn) | 0.611 | 0.659 | 0.259 | 0.00pp | NEAR_FAIL |
| `qld_ema100_off_tlt` | 0.520 | 0.0717 | 5/8 >SPY (MDD 65% warn) | 0.622 | 0.693 | 0.340 | 0.00pp | NEAR_FAIL |
| `qld_ema150_off_tlt` | 0.520 | 0.0443 | 7/8 >SPY (MDD 58% warn) | 0.795 | 0.776 | 0.365 | 0.00pp | MARGINAL |
| `qld_ema200_off_tlt` | 0.520 | 0.1231 | 6/8 >SPY (MDD 71% warn) | 0.761 | 0.702 | 0.272 | 0.00pp | NEAR_FAIL |
| `qld_ema250_off_tlt` | 0.520 | 0.1603 | 6/8 >SPY (MDD 76% warn) | 0.636 | 0.637 | 0.229 | 0.00pp | NEAR_FAIL |
| `qld_sma50_off_tmf` | 0.520 | 0.0978 | 5/8 >SPY (MDD 84% warn) | 0.356 | 0.269 | 0.316 | 0.00pp | NEAR_FAIL |
| `qld_sma100_off_tmf` | 0.520 | 0.0655 | 6/8 >SPY (MDD 83% warn) | 0.430 | 0.332 | 0.380 | 0.00pp | NEAR_FAIL |
| `qld_sma150_off_tmf` | 0.520 | 0.1824 | 6/8 >SPY (MDD 78% warn) | 0.517 | 0.363 | 0.223 | 0.00pp | NEAR_FAIL |
| `qld_sma200_off_tmf` | 0.520 | 0.0847 | 6/8 >SPY (MDD 79% warn) | 0.655 | 0.357 | 0.322 | 0.00pp | NEAR_FAIL |
| `qld_sma250_off_tmf` | 0.520 | 0.1355 | 6/8 >SPY (MDD 82% warn) | 0.535 | 0.335 | 0.278 | 0.00pp | NEAR_FAIL |
| `qld_ema50_off_tmf` | 0.520 | 0.1728 | 5/8 >SPY (MDD 87% warn) | 0.401 | 0.315 | 0.260 | 0.00pp | NEAR_FAIL |
| `qld_ema100_off_tmf` | 0.520 | 0.1054 | 5/8 >SPY (MDD 81% warn) | 0.446 | 0.400 | 0.323 | 0.00pp | NEAR_FAIL |
| `qld_ema150_off_tmf` | 0.520 | 0.0558 | 6/8 >SPY (MDD 79% warn) | 0.618 | 0.470 | 0.362 | 0.00pp | NEAR_FAIL |
| `qld_ema200_off_tmf` | 0.520 | 0.2056 | 6/8 >SPY (MDD 81% warn) | 0.504 | 0.300 | 0.229 | 0.00pp | NEAR_FAIL |
| `qld_ema250_off_tmf` | 0.520 | 0.2450 | 6/8 >SPY (MDD 82% warn) | 0.391 | 0.273 | 0.183 | 0.00pp | NEAR_FAIL |
| `qld_sma50_off_zroz` | 0.520 | 0.0350 | 5/8 >SPY (MDD 65% warn) | 0.541 | 0.521 | 0.389 | 0.00pp | PROMISING |
| `qld_sma100_off_zroz` | 0.520 | 0.0273 | 6/8 >SPY (MDD 64% warn) | 0.523 | 0.544 | 0.437 | 0.00pp | MARGINAL |
| `qld_sma150_off_zroz` | 0.520 | 0.0956 | 6/8 >SPY (MDD 72% warn) | 0.663 | 0.610 | 0.285 | 0.00pp | NEAR_FAIL |
| `qld_sma200_off_zroz` | 0.520 | 0.0356 | 6/8 >SPY (MDD 75% warn) | 0.833 | 0.652 | 0.389 | 0.00pp | PROMISING |
| `qld_sma250_off_zroz` | 0.520 | 0.0546 | 6/8 >SPY (MDD 70% warn) | 0.705 | 0.610 | 0.361 | 0.00pp | NEAR_FAIL |
| `qld_ema50_off_zroz` | 0.520 | 0.0879 | 5/8 >SPY (MDD 70% warn) | 0.549 | 0.548 | 0.324 | 0.00pp | NEAR_FAIL |
| `qld_ema100_off_zroz` | 0.520 | 0.0425 | 5/8 >SPY (MDD 63% warn) | 0.574 | 0.616 | 0.388 | 0.00pp | MARGINAL |
| `qld_ema150_off_zroz` | 0.520 | 0.0211 | 7/8 >SPY (MDD 58% warn) | 0.757 | 0.710 | 0.434 | 0.00pp | PROMISING |
| `qld_ema200_off_zroz` | 0.520 | 0.0850 | 6/8 >SPY (MDD 73% warn) | 0.699 | 0.597 | 0.309 | 0.00pp | NEAR_FAIL |
| `qld_ema250_off_zroz` | 0.520 | 0.1235 | 6/8 >SPY (MDD 76% warn) | 0.568 | 0.536 | 0.258 | 0.00pp | NEAR_FAIL |
| `qld_sma50_off_edv` | 0.520 | 0.0483 | 5/8 >SPY (MDD 63% warn) | 0.616 | 0.629 | 0.377 | 0.00pp | MARGINAL |
| `qld_sma100_off_edv` | 0.520 | 0.0491 | 6/8 >SPY (MDD 57% warn) | 0.558 | 0.614 | 0.381 | 0.00pp | MARGINAL |
| `qld_sma150_off_edv` | 0.520 | 0.1513 | 6/8 >SPY (MDD 75% warn) | 0.711 | 0.683 | 0.238 | 0.00pp | NEAR_FAIL |
| `qld_sma200_off_edv` | 0.520 | 0.0556 | 7/8 >SPY (MDD 75% warn) | 0.887 | 0.755 | 0.350 | 0.00pp | MARGINAL |
| `qld_sma250_off_edv` | 0.520 | 0.0702 | 6/8 >SPY (MDD 70% warn) | 0.762 | 0.708 | 0.331 | 0.00pp | NEAR_FAIL |
| `qld_ema50_off_edv` | 0.520 | 0.1589 | 5/8 >SPY (MDD 75% warn) | 0.611 | 0.659 | 0.259 | 0.00pp | NEAR_FAIL |
| `qld_ema100_off_edv` | 0.520 | 0.0717 | 5/8 >SPY (MDD 65% warn) | 0.622 | 0.693 | 0.340 | 0.00pp | NEAR_FAIL |
| `qld_ema150_off_edv` | 0.520 | 0.0443 | 7/8 >SPY (MDD 58% warn) | 0.795 | 0.776 | 0.365 | 0.00pp | MARGINAL |
| `qld_ema200_off_edv` | 0.520 | 0.1231 | 6/8 >SPY (MDD 71% warn) | 0.761 | 0.702 | 0.272 | 0.00pp | NEAR_FAIL |
| `qld_ema250_off_edv` | 0.520 | 0.1603 | 6/8 >SPY (MDD 76% warn) | 0.636 | 0.637 | 0.229 | 0.00pp | NEAR_FAIL |
| `soxl_sma50_off_bil` | 0.520 | 0.0970 | 6/8 >SPY (MDD 87% warn) | 0.728 | 0.876 | 0.324 | 0.00pp | NEAR_FAIL |
| `soxl_sma100_off_bil` | 0.520 | 0.2015 | 6/8 >SPY (MDD 93% warn) | 0.616 | 0.775 | 0.241 | 0.00pp | NEAR_FAIL |
| `soxl_sma150_off_bil` | 0.520 | 0.1839 | 6/8 >SPY (MDD 99% warn) | 0.942 | 0.965 | 0.213 | 0.00pp | NEAR_FAIL |
| `soxl_sma200_off_bil` | 0.520 | 0.1538 | 7/8 >SPY (MDD 94% warn) | 0.842 | 0.948 | 0.276 | 0.00pp | NEAR_FAIL |
| `soxl_sma250_off_bil` | 0.520 | 0.1427 | 7/8 >SPY (MDD 87% warn) | 0.796 | 0.847 | 0.284 | 0.00pp | NEAR_FAIL |
| `soxl_ema50_off_bil` | 0.520 | 0.2982 | 5/8 >SPY (MDD 95% warn) | 0.689 | 0.868 | 0.188 | 0.00pp | NEAR_FAIL |
| `soxl_ema100_off_bil` | 0.520 | 0.1339 | 7/8 >SPY (MDD 92% warn) | 0.756 | 0.846 | 0.281 | 0.00pp | NEAR_FAIL |
| `soxl_ema150_off_bil` | 0.520 | 0.1797 | 6/8 >SPY (MDD 95% warn) | 0.910 | 0.971 | 0.226 | 0.00pp | NEAR_FAIL |
| `soxl_ema200_off_bil` | 0.520 | 0.1402 | 6/8 >SPY (MDD 92% warn) | 0.793 | 0.884 | 0.263 | 0.00pp | NEAR_FAIL |
| `soxl_ema250_off_bil` | 0.520 | 0.0611 | 7/8 >SPY (MDD 86% warn) | 0.807 | 0.874 | 0.357 | 0.00pp | MARGINAL |
| `soxl_sma50_off_ief` | 0.520 | 0.0620 | 6/8 >SPY (MDD 85% warn) | 0.735 | 0.867 | 0.364 | 0.00pp | MARGINAL |
| `soxl_sma100_off_ief` | 0.520 | 0.1479 | 6/8 >SPY (MDD 91% warn) | 0.609 | 0.747 | 0.268 | 0.00pp | NEAR_FAIL |
| `soxl_sma150_off_ief` | 0.520 | 0.1437 | 6/8 >SPY (MDD 98% warn) | 0.928 | 0.924 | 0.244 | 0.00pp | NEAR_FAIL |
| `soxl_sma200_off_ief` | 0.520 | 0.1222 | 7/8 >SPY (MDD 93% warn) | 0.834 | 0.920 | 0.294 | 0.00pp | NEAR_FAIL |
| `soxl_sma250_off_ief` | 0.520 | 0.1131 | 6/8 >SPY (MDD 84% warn) | 0.788 | 0.819 | 0.306 | 0.00pp | NEAR_FAIL |
| `soxl_ema50_off_ief` | 0.520 | 0.2189 | 5/8 >SPY (MDD 94% warn) | 0.697 | 0.857 | 0.219 | 0.00pp | NEAR_FAIL |
| `soxl_ema100_off_ief` | 0.520 | 0.0889 | 7/8 >SPY (MDD 91% warn) | 0.763 | 0.842 | 0.311 | 0.00pp | MARGINAL |
| `soxl_ema150_off_ief` | 0.520 | 0.1413 | 6/8 >SPY (MDD 94% warn) | 0.897 | 0.935 | 0.256 | 0.00pp | NEAR_FAIL |
| `soxl_ema200_off_ief` | 0.520 | 0.1052 | 7/8 >SPY (MDD 92% warn) | 0.790 | 0.871 | 0.291 | 0.00pp | MARGINAL |
| `soxl_ema250_off_ief` | 0.520 | 0.0457 | 6/8 >SPY (MDD 86% warn) | 0.804 | 0.861 | 0.381 | 0.00pp | PROMISING |
| `soxl_sma50_off_tlt` | 0.520 | 0.0632 | 5/8 >SPY (MDD 85% warn) | 0.683 | 0.793 | 0.360 | 0.00pp | MARGINAL |
| `soxl_sma100_off_tlt` | 0.520 | 0.1590 | 5/8 >SPY (MDD 91% warn) | 0.560 | 0.660 | 0.261 | 0.00pp | NEAR_FAIL |
| `soxl_sma150_off_tlt` | 0.520 | 0.1473 | 6/8 >SPY (MDD 98% warn) | 0.886 | 0.851 | 0.235 | 0.00pp | MARGINAL |
| `soxl_sma200_off_tlt` | 0.520 | 0.1268 | 7/8 >SPY (MDD 93% warn) | 0.801 | 0.862 | 0.291 | 0.00pp | NEAR_FAIL |
| `soxl_sma250_off_tlt` | 0.520 | 0.1137 | 6/8 >SPY (MDD 84% warn) | 0.763 | 0.775 | 0.308 | 0.00pp | NEAR_FAIL |
| `soxl_ema50_off_tlt` | 0.520 | 0.2162 | 4/8 >SPY (MDD 94% warn) | 0.653 | 0.790 | 0.222 | 0.00pp | NEAR_FAIL |
| `soxl_ema100_off_tlt` | 0.520 | 0.0873 | 7/8 >SPY (MDD 91% warn) | 0.737 | 0.795 | 0.312 | 0.00pp | MARGINAL |
| `soxl_ema150_off_tlt` | 0.520 | 0.1506 | 6/8 >SPY (MDD 94% warn) | 0.850 | 0.859 | 0.245 | 0.00pp | NEAR_FAIL |
| `soxl_ema200_off_tlt` | 0.520 | 0.1094 | 5/8 >SPY (MDD 92% warn) | 0.761 | 0.824 | 0.285 | 0.00pp | NEAR_FAIL |
| `soxl_ema250_off_tlt` | 0.520 | 0.0488 | 6/8 >SPY (MDD 86% warn) | 0.776 | 0.819 | 0.368 | 0.00pp | MARGINAL |
| `soxl_sma50_off_tmf` | 0.520 | 0.0602 | 5/8 >SPY (MDD 85% warn) | 0.518 | 0.550 | 0.367 | 0.00pp | MARGINAL |
| `soxl_sma100_off_tmf` | 0.520 | 0.1650 | 6/8 >SPY (MDD 87% warn) | 0.405 | 0.389 | 0.267 | 0.00pp | NEAR_FAIL |
| `soxl_sma150_off_tmf` | 0.520 | 0.1499 | 5/8 >SPY (MDD 98% warn) | 0.713 | 0.568 | 0.232 | 0.00pp | NEAR_FAIL |
| `soxl_sma200_off_tmf` | 0.520 | 0.1362 | 6/8 >SPY (MDD 92% warn) | 0.666 | 0.629 | 0.283 | 0.00pp | NEAR_FAIL |
| `soxl_sma250_off_tmf` | 0.520 | 0.1119 | 6/8 >SPY (MDD 87% warn) | 0.646 | 0.574 | 0.300 | 0.00pp | NEAR_FAIL |
| `soxl_ema50_off_tmf` | 0.520 | 0.1768 | 4/8 >SPY (MDD 93% warn) | 0.510 | 0.557 | 0.253 | 0.00pp | NEAR_FAIL |
| `soxl_ema100_off_tmf` | 0.520 | 0.0683 | 6/8 >SPY (MDD 89% warn) | 0.634 | 0.620 | 0.347 | 0.00pp | MARGINAL |
| `soxl_ema150_off_tmf` | 0.520 | 0.1639 | 6/8 >SPY (MDD 93% warn) | 0.674 | 0.579 | 0.232 | 0.00pp | NEAR_FAIL |
| `soxl_ema200_off_tmf` | 0.520 | 0.1061 | 6/8 >SPY (MDD 92% warn) | 0.646 | 0.640 | 0.282 | 0.00pp | NEAR_FAIL |
| `soxl_ema250_off_tmf` | 0.520 | 0.0545 | 6/8 >SPY (MDD 88% warn) | 0.663 | 0.646 | 0.366 | 0.00pp | MARGINAL |
| `soxl_sma50_off_zroz` | 0.520 | 0.0400 | 5/8 >SPY (MDD 84% warn) | 0.635 | 0.729 | 0.387 | 0.00pp | PROMISING |
| `soxl_sma100_off_zroz` | 0.520 | 0.1087 | 6/8 >SPY (MDD 89% warn) | 0.514 | 0.590 | 0.302 | 0.00pp | NEAR_FAIL |
| `soxl_sma150_off_zroz` | 0.520 | 0.1045 | 6/8 >SPY (MDD 98% warn) | 0.842 | 0.779 | 0.256 | 0.00pp | MARGINAL |
| `soxl_sma200_off_zroz` | 0.520 | 0.0938 | 7/8 >SPY (MDD 93% warn) | 0.765 | 0.803 | 0.321 | 0.00pp | NEAR_FAIL |
| `soxl_sma250_off_zroz` | 0.520 | 0.0833 | 6/8 >SPY (MDD 84% warn) | 0.734 | 0.728 | 0.329 | 0.00pp | MARGINAL |
| `soxl_ema50_off_zroz` | 0.520 | 0.1351 | 4/8 >SPY (MDD 93% warn) | 0.605 | 0.721 | 0.278 | 0.00pp | NEAR_FAIL |
| `soxl_ema100_off_zroz` | 0.520 | 0.0499 | 7/8 >SPY (MDD 90% warn) | 0.711 | 0.759 | 0.361 | 0.00pp | MARGINAL |
| `soxl_ema150_off_zroz` | 0.520 | 0.1106 | 6/8 >SPY (MDD 94% warn) | 0.803 | 0.789 | 0.288 | 0.00pp | NEAR_FAIL |
| `soxl_ema200_off_zroz` | 0.520 | 0.0754 | 6/8 >SPY (MDD 92% warn) | 0.731 | 0.777 | 0.310 | 0.00pp | MARGINAL |
| `soxl_ema250_off_zroz` | 0.520 | 0.0360 | 6/8 >SPY (MDD 86% warn) | 0.746 | 0.774 | 0.393 | 0.00pp | PROMISING |
| `soxl_sma50_off_edv` | 0.520 | 0.0632 | 5/8 >SPY (MDD 85% warn) | 0.683 | 0.793 | 0.360 | 0.00pp | MARGINAL |
| `soxl_sma100_off_edv` | 0.520 | 0.1590 | 5/8 >SPY (MDD 91% warn) | 0.560 | 0.660 | 0.261 | 0.00pp | NEAR_FAIL |
| `soxl_sma150_off_edv` | 0.520 | 0.1473 | 6/8 >SPY (MDD 98% warn) | 0.886 | 0.851 | 0.235 | 0.00pp | MARGINAL |
| `soxl_sma200_off_edv` | 0.520 | 0.1268 | 7/8 >SPY (MDD 93% warn) | 0.801 | 0.862 | 0.291 | 0.00pp | NEAR_FAIL |
| `soxl_sma250_off_edv` | 0.520 | 0.1137 | 6/8 >SPY (MDD 84% warn) | 0.763 | 0.775 | 0.308 | 0.00pp | NEAR_FAIL |
| `soxl_ema50_off_edv` | 0.520 | 0.2162 | 4/8 >SPY (MDD 94% warn) | 0.653 | 0.790 | 0.222 | 0.00pp | NEAR_FAIL |
| `soxl_ema100_off_edv` | 0.520 | 0.0873 | 7/8 >SPY (MDD 91% warn) | 0.737 | 0.795 | 0.312 | 0.00pp | MARGINAL |
| `soxl_ema150_off_edv` | 0.520 | 0.1506 | 6/8 >SPY (MDD 94% warn) | 0.850 | 0.859 | 0.245 | 0.00pp | NEAR_FAIL |
| `soxl_ema200_off_edv` | 0.520 | 0.1094 | 5/8 >SPY (MDD 92% warn) | 0.761 | 0.824 | 0.285 | 0.00pp | NEAR_FAIL |
| `soxl_ema250_off_edv` | 0.520 | 0.0488 | 6/8 >SPY (MDD 86% warn) | 0.776 | 0.819 | 0.368 | 0.00pp | MARGINAL |
| `ugl_sma50_off_bil` | 0.520 | 0.8509 | 3/8 >SPY (MDD 53% warn) | 0.485 | 0.857 | -0.060 | 0.00pp | NEAR_FAIL |
| `ugl_sma100_off_bil` | 0.520 | 0.8683 | 3/8 >SPY (MDD 51% warn) | 0.573 | 0.910 | -0.093 | 0.00pp | NEAR_FAIL |
| `ugl_sma150_off_bil` | 0.520 | 0.8094 | 3/8 >SPY (MDD 52% warn) | 0.570 | 0.823 | -0.046 | 0.00pp | NEAR_FAIL |
| `ugl_sma200_off_bil` | 0.520 | 0.7937 | 1/8 >SPY (MDD 49% warn) | 0.526 | 0.808 | -0.053 | 0.00pp | NEAR_FAIL |
| `ugl_sma250_off_bil` | 0.520 | 0.7176 | 2/8 >SPY (MDD 54% warn) | 0.547 | 0.886 | -0.014 | 0.00pp | NEAR_FAIL |
| `ugl_ema50_off_bil` | 0.520 | 0.8235 | 4/8 >SPY (MDD 53% warn) | 0.509 | 0.828 | -0.045 | 0.00pp | NEAR_FAIL |
| `ugl_ema100_off_bil` | 0.520 | 0.8089 | 2/8 >SPY (MDD 49% warn) | 0.575 | 0.891 | -0.045 | 0.00pp | NEAR_FAIL |
| `ugl_ema150_off_bil` | 0.520 | 0.6637 | 2/8 >SPY (MDD 45% warn) | 0.583 | 0.793 | 0.027 | 0.00pp | NEAR_FAIL |
| `ugl_ema200_off_bil` | 0.520 | 0.7026 | 3/8 >SPY (MDD 44% warn) | 0.576 | 0.817 | 0.007 | 0.00pp | NEAR_FAIL |
| `ugl_ema250_off_bil` | 0.520 | 0.5919 | 3/8 >SPY (MDD 45% warn) | 0.553 | 0.821 | 0.062 | 0.00pp | NEAR_FAIL |
| `ugl_sma50_off_ief` | 0.520 | 0.7725 | 3/8 >SPY (MDD 49% warn) | 0.486 | 0.822 | -0.009 | 0.00pp | NEAR_FAIL |
| `ugl_sma100_off_ief` | 0.520 | 0.7572 | 2/8 >SPY (MDD 50% warn) | 0.571 | 0.846 | -0.019 | 0.00pp | NEAR_FAIL |
| `ugl_sma150_off_ief` | 0.520 | 0.6699 | 2/8 >SPY (MDD 49% warn) | 0.580 | 0.805 | 0.034 | 0.00pp | NEAR_FAIL |
| `ugl_sma200_off_ief` | 0.520 | 0.6161 | 2/8 >SPY (MDD 40% warn) | 0.554 | 0.791 | 0.051 | 0.00pp | NEAR_FAIL |
| `ugl_sma250_off_ief` | 0.520 | 0.4842 | 3/8 >SPY (MDD 45% warn) | 0.584 | 0.870 | 0.100 | 0.00pp | NEAR_FAIL |
| `ugl_ema50_off_ief` | 0.520 | 0.7127 | 4/8 >SPY (MDD 50% warn) | 0.511 | 0.784 | 0.018 | 0.00pp | NEAR_FAIL |
| `ugl_ema100_off_ief` | 0.520 | 0.6882 | 3/8 >SPY (MDD 50% warn) | 0.581 | 0.856 | 0.026 | 0.00pp | NEAR_FAIL |
| `ugl_ema150_off_ief` | 0.520 | 0.4946 | 2/8 >SPY (MDD 46% warn) | 0.585 | 0.755 | 0.114 | 0.00pp | NEAR_FAIL |
| `ugl_ema200_off_ief` | 0.520 | 0.4836 | 3/8 >SPY (MDD 44% warn) | 0.616 | 0.812 | 0.101 | 0.00pp | NEAR_FAIL |
| `ugl_ema250_off_ief` | 0.520 | 0.3643 | 3/8 >SPY (MDD 42% warn) | 0.607 | 0.831 | 0.163 | 0.00pp | NEAR_FAIL |
| `ugl_sma50_off_tlt` | 0.520 | 0.7343 | 3/8 >SPY (MDD 50% warn) | 0.469 | 0.751 | 0.012 | 0.00pp | NEAR_FAIL |
| `ugl_sma100_off_tlt` | 0.520 | 0.7011 | 2/8 >SPY (MDD 52% warn) | 0.545 | 0.747 | 0.006 | 0.00pp | NEAR_FAIL |
| `ugl_sma150_off_tlt` | 0.520 | 0.6262 | 2/8 >SPY (MDD 48% warn) | 0.548 | 0.767 | 0.053 | 0.00pp | NEAR_FAIL |
| `ugl_sma200_off_tlt` | 0.520 | 0.5387 | 1/8 >SPY (MDD 43% warn) | 0.547 | 0.760 | 0.083 | 0.00pp | NEAR_FAIL |
| `ugl_sma250_off_tlt` | 0.520 | 0.3929 | 3/8 >SPY (MDD 44% warn) | 0.594 | 0.837 | 0.143 | 0.00pp | NEAR_FAIL |
| `ugl_ema50_off_tlt` | 0.520 | 0.6502 | 3/8 >SPY (MDD 51% warn) | 0.497 | 0.695 | 0.053 | 0.00pp | NEAR_FAIL |
| `ugl_ema100_off_tlt` | 0.520 | 0.6486 | 3/8 >SPY (MDD 50% warn) | 0.554 | 0.779 | 0.046 | 0.00pp | NEAR_FAIL |
| `ugl_ema150_off_tlt` | 0.520 | 0.4361 | 2/8 >SPY (MDD 46% warn) | 0.546 | 0.699 | 0.129 | 0.00pp | NEAR_FAIL |
| `ugl_ema200_off_tlt` | 0.520 | 0.3932 | 2/8 >SPY (MDD 45% warn) | 0.628 | 0.803 | 0.142 | 0.00pp | NEAR_FAIL |
| `ugl_ema250_off_tlt` | 0.520 | 0.2947 | 2/8 >SPY (MDD 43% warn) | 0.628 | 0.822 | 0.191 | 0.00pp | NEAR_FAIL |
| `ugl_sma50_off_tmf` | 0.520 | 0.7369 | 3/8 >SPY (MDD 64% warn) | 0.331 | 0.448 | 0.006 | 0.00pp | NEAR_FAIL |
| `ugl_sma100_off_tmf` | 0.520 | 0.5958 | 2/8 >SPY (MDD 71% warn) | 0.385 | 0.373 | 0.062 | 0.00pp | NEAR_FAIL |
| `ugl_sma150_off_tmf` | 0.520 | 0.5268 | 3/8 >SPY (MDD 64% warn) | 0.403 | 0.551 | 0.095 | 0.00pp | NEAR_FAIL |
| `ugl_sma200_off_tmf` | 0.520 | 0.3450 | 3/8 >SPY (MDD 60% warn) | 0.468 | 0.570 | 0.185 | 0.00pp | NEAR_FAIL |
| `ugl_sma250_off_tmf` | 0.520 | 0.1756 | 3/8 >SPY (MDD 61% warn) | 0.550 | 0.645 | 0.255 | 0.00pp | NEAR_FAIL |
| `ugl_ema50_off_tmf` | 0.520 | 0.5902 | 4/8 >SPY (MDD 60% warn) | 0.362 | 0.368 | 0.069 | 0.00pp | NEAR_FAIL |
| `ugl_ema100_off_tmf` | 0.520 | 0.5934 | 4/8 >SPY (MDD 65% warn) | 0.402 | 0.473 | 0.080 | 0.00pp | NEAR_FAIL |
| `ugl_ema150_off_tmf` | 0.520 | 0.3395 | 4/8 >SPY (MDD 61% warn) | 0.380 | 0.444 | 0.171 | 0.00pp | NEAR_FAIL |
| `ugl_ema200_off_tmf` | 0.520 | 0.1928 | 3/8 >SPY (MDD 60% warn) | 0.583 | 0.667 | 0.251 | 0.00pp | NEAR_FAIL |
| `ugl_ema250_off_tmf` | 0.520 | 0.1391 | 3/8 >SPY (MDD 58% warn) | 0.624 | 0.719 | 0.295 | 0.00pp | NEAR_FAIL |
| `ugl_sma50_off_zroz` | 0.520 | 0.6036 | 3/8 >SPY (MDD 52% warn) | 0.458 | 0.691 | 0.064 | 0.00pp | NEAR_FAIL |
| `ugl_sma100_off_zroz` | 0.520 | 0.5076 | 3/8 >SPY (MDD 54% warn) | 0.511 | 0.647 | 0.098 | 0.00pp | NEAR_FAIL |
| `ugl_sma150_off_zroz` | 0.520 | 0.4533 | 2/8 >SPY (MDD 51% warn) | 0.505 | 0.703 | 0.113 | 0.00pp | NEAR_FAIL |
| `ugl_sma200_off_zroz` | 0.520 | 0.3128 | 3/8 >SPY (MDD 51% warn) | 0.538 | 0.727 | 0.181 | 0.00pp | NEAR_FAIL |
| `ugl_sma250_off_zroz` | 0.520 | 0.1792 | 3/8 >SPY (MDD 47% warn) | 0.599 | 0.799 | 0.256 | 0.00pp | NEAR_FAIL |
| `ugl_ema50_off_zroz` | 0.520 | 0.4594 | 4/8 >SPY (MDD 52% warn) | 0.487 | 0.624 | 0.122 | 0.00pp | NEAR_FAIL |
| `ugl_ema100_off_zroz` | 0.520 | 0.4654 | 3/8 >SPY (MDD 53% warn) | 0.518 | 0.700 | 0.125 | 0.00pp | NEAR_FAIL |
| `ugl_ema150_off_zroz` | 0.520 | 0.2515 | 3/8 >SPY (MDD 48% warn) | 0.498 | 0.630 | 0.216 | 0.00pp | NEAR_FAIL |
| `ugl_ema200_off_zroz` | 0.520 | 0.1816 | 2/8 >SPY (MDD 46% warn) | 0.628 | 0.781 | 0.263 | 0.00pp | NEAR_FAIL |
| `ugl_ema250_off_zroz` | 0.520 | 0.1244 | 2/8 >SPY (MDD 44% warn) | 0.638 | 0.795 | 0.302 | 0.00pp | NEAR_FAIL |
| `ugl_sma50_off_edv` | 0.520 | 0.7343 | 3/8 >SPY (MDD 50% warn) | 0.469 | 0.751 | 0.012 | 0.00pp | NEAR_FAIL |
| `ugl_sma100_off_edv` | 0.520 | 0.7011 | 2/8 >SPY (MDD 52% warn) | 0.545 | 0.747 | 0.006 | 0.00pp | NEAR_FAIL |
| `ugl_sma150_off_edv` | 0.520 | 0.6262 | 2/8 >SPY (MDD 48% warn) | 0.548 | 0.767 | 0.053 | 0.00pp | NEAR_FAIL |
| `ugl_sma200_off_edv` | 0.520 | 0.5387 | 1/8 >SPY (MDD 43% warn) | 0.547 | 0.760 | 0.083 | 0.00pp | NEAR_FAIL |
| `ugl_sma250_off_edv` | 0.520 | 0.3929 | 3/8 >SPY (MDD 44% warn) | 0.594 | 0.837 | 0.143 | 0.00pp | NEAR_FAIL |
| `ugl_ema50_off_edv` | 0.520 | 0.6502 | 3/8 >SPY (MDD 51% warn) | 0.497 | 0.695 | 0.053 | 0.00pp | NEAR_FAIL |
| `ugl_ema100_off_edv` | 0.520 | 0.6486 | 3/8 >SPY (MDD 50% warn) | 0.554 | 0.779 | 0.046 | 0.00pp | NEAR_FAIL |
| `ugl_ema150_off_edv` | 0.520 | 0.4361 | 2/8 >SPY (MDD 46% warn) | 0.546 | 0.699 | 0.129 | 0.00pp | NEAR_FAIL |
| `ugl_ema200_off_edv` | 0.520 | 0.3932 | 2/8 >SPY (MDD 45% warn) | 0.628 | 0.803 | 0.142 | 0.00pp | NEAR_FAIL |
| `ugl_ema250_off_edv` | 0.520 | 0.2947 | 2/8 >SPY (MDD 43% warn) | 0.628 | 0.822 | 0.191 | 0.00pp | NEAR_FAIL |

Hard-gate thresholds (spec §3.5): G1 PBO < 0.50, G2 DSR p < 0.05, G3 ≥5/8 windows + MDD < 50%, G4/G5 Sharpe > 0, G6 99% CI low > 0, G7 |Δ| ≤ 3pp.

## Plots

- `plots/01_equity_curves.png` — log-scale equity per config + SPY benchmark
- `plots/02_drawdown_curves.png` — peak-to-trough drawdown
- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR
- `plots/05_regime_attribution.png` — % of time signal=ON per config
- `plots/06_pct_beat_spy.png` — cumulative fraction of 3y windows where config beat SPY
- `plots/07_crisis_attribution.png` — MDD per crisis window vs SPY

## Tables

- `tables/per_config_metrics.csv` — one row per (config, dataset)
- `tables/gates_pass_fail.csv` — gate values + pass/fail flags

## Verdict

- **Best config:** `qld_ema150_off_zroz` (PROMISING, score 64.5)
- **KILL T0:** PASS (study viable)
- **Advance to next tier:** yes
- **Cumulative n_trials:** 382
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.787 (lh_56y) clears SPY+0.05 — single-LETF Gayed rotation has prima-facie edge in this universe. Proceeding to T1b period sweep.

## Next iter

