# Phase 3.8 B3 — Pauchlyova static+trend multi-asset allocation — Honest Validation

**Verdict: FAIL** — 0/8 configs pass all 13 gates (hard fails total: 31)

- **Git SHA:** `14f58d7d8b`
- **Universe:** LETF (UPRO synth pre-2009 + real post / SSO real post-2006) + TLT + SPY + GLD + SHV, all daily Tiingo
- **Windows (SHIFTED):** IS `2004-11-18 → 2015-12-31`, OOS `2016-01-01 → 2020-12-31`, FWD `2021-01-01 → 2026-04-15`
- **Cost model (rota B Inter, mandate §4.6):** commission=0 + spread=5.0bps/unit turnover + LETF ER=0.95% embedded + DARF=15% year-end + cash_sleeve=4.0%/yr (SHV pre-2007 proxy)
- **PBO grid:** 8 configs (2 letf_kind × 2 trend × 2 cadence) → PBO=0.524

## Data caveats (honest scope shift)

- **IS shifted to 2004-11-18** (GLD inception). Pauchlyova's original
  Quantpedia simulation extends to 1926 but needs synthetic 2x LETF +
  synthetic gold + synthetic long bond, which are beyond our honest
  data scope. We elected to start IS at the latest-starting component
  (GLD, 2004-11-18) rather than inject multi-asset synthesis.
- **SHV pre-2007-01-11 proxy:** flat 4%/yr cash rate per mandate §4.6
  long-run 3-mo T-bill approximation. Second-order effect since SHV
  base weight is only 10%.
- **Window lengths:** IS ~11y, OOS 5y, FWD 5.3y — meets the prompt's
  ≥7y IS + ≥3y OOS honest constraint. Commit-to-windows done BEFORE
  running any config to avoid OOS peek.

## B3-UPRO-trend-monthly — FAIL

- **Config hash:** `d763538ade`
- **Turnover:** ~37.5 rebals/yr (WATCHDOG — >20)

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.614 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 0.745 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 6.320% — tier **Folclore** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -14.931% — tier **Excelente** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.252 | **PASS** |
| 6 WF >= 6/8 positive | 7/8 profitable | **PASS** |
| 7 Median hold >= 5d | 3.0 trading days | **FAIL** |
| 8 IR vs SPY >= 0.2 | -0.519 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | n/a (non-winner) | **FAIL** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-0.000233099; FULL=-4.10322e-05 | **FAIL** |
| 11 PBO < 0.5 (HARD) | pbo=0.524 | **FAIL** |
| 12 DSR p < 0.05 (HARD) | n/a | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.528 (cagr=4.507%) | **FAIL** |

### Window summaries

#### IS (2004-11-18 → 2015-12-31)
- days=2,799, rebal+flips=414, median_hold=3.0d
- Sharpe(daily)=0.614, CAGR=5.152%, MDD=-16.829%

#### OOS (2016-01-01 → 2020-12-31)
- days=1,259, rebal+flips=157, median_hold=3.0d
- Sharpe(daily)=0.745, CAGR=6.320% (tier **Folclore**), MDD=-14.931% (tier **Excelente**)
- IR vs SPY buy-hold: -0.519

#### FWD (2021-01-01 → 2026-04-15)
- days=1,326, rebal+flips=231, median_hold=3.0d
- Sharpe(daily)=0.252, CAGR=1.790%, MDD=-20.480%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| china_2015 | 189 | -2.967 | -16.980% | -13.717% |
| covid_2020_03 | 62 | -1.004 | -18.016% | -14.931% |
| rate_shock_2022 | 251 | -2.228 | -11.325% | -10.816% |
| bank_crisis_2023 | 104 | -1.255 | -11.709% | -11.385% |
| rally_2024 | 251 | 2.115 | 24.889% | -6.228% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 7 / 8
- Window returns: 9.78%, 2.36%, 15.89%, 19.10%, 30.11%, -10.10%, 4.98%, 25.28%
- Window MDDs: 7.51%, 8.52%, 9.32%, 5.62%, 7.00%, 17.89%, 13.39%, 14.93%

## B3-UPRO-trend-quarterly — FAIL

- **Config hash:** `fdd44c282b`
- **Turnover:** ~30.3 rebals/yr (WATCHDOG — >20)

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.622 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 0.742 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 6.345% — tier **Folclore** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -14.755% — tier **Excelente** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.241 | **PASS** |
| 6 WF >= 6/8 positive | 7/8 profitable | **PASS** |
| 7 Median hold >= 5d | 3.0 trading days | **FAIL** |
| 8 IR vs SPY >= 0.2 | -0.517 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | n/a (non-winner) | **FAIL** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-0.000211573; FULL=-4.41896e-05 | **FAIL** |
| 11 PBO < 0.5 (HARD) | pbo=0.524 | **FAIL** |
| 12 DSR p < 0.05 (HARD) | n/a | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.530 (cagr=4.553%) | **FAIL** |

### Window summaries

#### IS (2004-11-18 → 2015-12-31)
- days=2,799, rebal+flips=334, median_hold=3.0d
- Sharpe(daily)=0.622, CAGR=5.301%, MDD=-16.835%

#### OOS (2016-01-01 → 2020-12-31)
- days=1,259, rebal+flips=119, median_hold=3.0d
- Sharpe(daily)=0.742, CAGR=6.345% (tier **Folclore**), MDD=-14.755% (tier **Excelente**)
- IR vs SPY buy-hold: -0.517

#### FWD (2021-01-01 → 2026-04-15)
- days=1,326, rebal+flips=196, median_hold=2.0d
- Sharpe(daily)=0.241, CAGR=1.698%, MDD=-20.537%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| china_2015 | 189 | -2.978 | -16.944% | -13.677% |
| covid_2020_03 | 62 | -0.968 | -17.403% | -14.755% |
| rate_shock_2022 | 251 | -2.226 | -11.315% | -10.807% |
| bank_crisis_2023 | 104 | -1.256 | -11.727% | -11.406% |
| rally_2024 | 251 | 2.105 | 24.827% | -6.194% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 7 / 8
- Window returns: 9.76%, 2.24%, 16.51%, 19.86%, 30.51%, -9.73%, 5.74%, 24.18%
- Window MDDs: 7.62%, 8.59%, 9.48%, 5.85%, 7.00%, 17.89%, 12.84%, 14.76%

## B3-UPRO-static-monthly — FAIL

- **Config hash:** `613cc8f3b0`
- **Turnover:** ~12.1 rebals/yr (OK)

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.536 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 1.037 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 13.417% — tier **Marginal** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -23.710% — tier **Válido** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.449 | **PASS** |
| 6 WF >= 6/8 positive | 7/8 profitable | **PASS** |
| 7 Median hold >= 5d | 21.0 trading days | **PASS** |
| 8 IR vs SPY >= 0.2 | -0.234 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | n/a (non-winner) | **FAIL** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-0.000141356; FULL=-2.54035e-06 | **FAIL** |
| 11 PBO < 0.5 (HARD) | pbo=0.524 | **FAIL** |
| 12 DSR p < 0.05 (HARD) | n/a | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.825 (cagr=10.879%) | **PASS** |

### Window summaries

#### IS (2004-11-18 → 2015-12-31)
- days=2,799, rebal+flips=134, median_hold=21.0d
- Sharpe(daily)=0.536, CAGR=6.471%, MDD=-44.316%

#### OOS (2016-01-01 → 2020-12-31)
- days=1,259, rebal+flips=60, median_hold=21.0d
- Sharpe(daily)=1.037, CAGR=13.417% (tier **Marginal**), MDD=-23.710% (tier **Válido**)
- IR vs SPY buy-hold: -0.234

#### FWD (2021-01-01 → 2026-04-15)
- days=1,326, rebal+flips=64, median_hold=21.0d
- Sharpe(daily)=0.449, CAGR=5.913%, MDD=-34.424%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| china_2015 | 189 | -0.210 | -3.159% | -8.482% |
| covid_2020_03 | 62 | -0.226 | -13.161% | -23.710% |
| rate_shock_2022 | 251 | -1.391 | -27.510% | -31.928% |
| bank_crisis_2023 | 104 | 1.093 | 14.108% | -7.767% |
| rally_2024 | 251 | 2.213 | 34.585% | -6.280% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 7 / 8
- Window returns: 20.88%, -26.01%, 36.51%, 28.81%, 30.17%, 8.08%, 6.85%, 62.42%
- Window MDDs: 7.21%, 37.90%, 24.23%, 8.10%, 8.23%, 10.50%, 13.69%, 23.71%

## B3-UPRO-static-quarterly — FAIL

- **Config hash:** `631e4342db`
- **Turnover:** ~4.1 rebals/yr (OK)

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.608 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 1.076 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 14.327% — tier **Marginal** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -21.317% — tier **Válido** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.437 | **PASS** |
| 6 WF >= 6/8 positive | 7/8 profitable | **PASS** |
| 7 Median hold >= 5d | 63.0 trading days | **PASS** |
| 8 IR vs SPY >= 0.2 | -0.139 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | n/a (non-winner) | **FAIL** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-6.56639e-05; FULL=1.66232e-05 | **FAIL** |
| 11 PBO < 0.5 (HARD) | pbo=0.524 | **FAIL** |
| 12 DSR p < 0.05 (HARD) | n/a | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.857 (cagr=11.660%) | **PASS** |

### Window summaries

#### IS (2004-11-18 → 2015-12-31)
- days=2,799, rebal+flips=45, median_hold=63.0d
- Sharpe(daily)=0.608, CAGR=7.243%, MDD=-39.135%

#### OOS (2016-01-01 → 2020-12-31)
- days=1,259, rebal+flips=20, median_hold=63.0d
- Sharpe(daily)=1.076, CAGR=14.327% (tier **Marginal**), MDD=-21.317% (tier **Válido**)
- IR vs SPY buy-hold: -0.139

#### FWD (2021-01-01 → 2026-04-15)
- days=1,326, rebal+flips=22, median_hold=63.0d
- Sharpe(daily)=0.437, CAGR=5.787%, MDD=-34.297%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| china_2015 | 189 | -0.217 | -3.381% | -8.374% |
| covid_2020_03 | 62 | 0.149 | -0.206% | -21.317% |
| rate_shock_2022 | 251 | -1.424 | -28.110% | -31.690% |
| bank_crisis_2023 | 104 | 1.002 | 13.583% | -8.652% |
| rally_2024 | 251 | 2.223 | 34.908% | -6.343% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 7 / 8
- Window returns: 20.57%, -23.61%, 40.47%, 32.30%, 30.60%, 6.83%, 8.25%, 68.19%
- Window MDDs: 7.35%, 33.61%, 20.84%, 8.00%, 8.52%, 10.45%, 12.88%, 21.32%

## B3-SSO-trend-monthly — FAIL

- **Config hash:** `c1b0912a38`
- **Turnover:** ~36.9 rebals/yr (WATCHDOG — >20)

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.557 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 0.834 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 6.140% — tier **Folclore** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -11.641% — tier **Excelente** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.239 | **PASS** |
| 6 WF >= 6/8 positive | 7/8 profitable | **PASS** |
| 7 Median hold >= 5d | 3.0 trading days | **FAIL** |
| 8 IR vs SPY >= 0.2 | -0.529 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | n/a (non-winner) | **FAIL** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-9.89744e-05; FULL=-3.68112e-05 | **FAIL** |
| 11 PBO < 0.5 (HARD) | pbo=0.524 | **FAIL** |
| 12 DSR p < 0.05 (HARD) | n/a | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.597 (cagr=4.481%) | **FAIL** |

### Window summaries

#### IS (2004-11-18 → 2015-12-31)
- days=2,799, rebal+flips=418, median_hold=3.0d
- Sharpe(daily)=0.557, CAGR=3.913%, MDD=-16.395%

#### OOS (2016-01-01 → 2020-12-31)
- days=1,259, rebal+flips=142, median_hold=5.0d
- Sharpe(daily)=0.834, CAGR=6.140% (tier **Folclore**), MDD=-11.641% (tier **Excelente**)
- IR vs SPY buy-hold: -0.529

#### FWD (2021-01-01 → 2026-04-15)
- days=1,326, rebal+flips=229, median_hold=3.0d
- Sharpe(daily)=0.239, CAGR=1.433%, MDD=-17.952%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| china_2015 | 189 | -3.425 | -16.421% | -13.144% |
| covid_2020_03 | 62 | -0.430 | -8.165% | -11.641% |
| rate_shock_2022 | 251 | -2.572 | -10.766% | -10.154% |
| bank_crisis_2023 | 104 | -1.346 | -10.749% | -9.259% |
| rally_2024 | 251 | 2.171 | 20.715% | -4.526% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 7 / 8
- Window returns: 9.22%, 1.76%, 11.86%, 16.25%, 22.62%, -10.24%, 4.12%, 25.60%
- Window MDDs: 5.94%, 8.07%, 10.64%, 5.21%, 5.40%, 17.15%, 10.17%, 11.64%

## B3-SSO-trend-quarterly — FAIL

- **Config hash:** `b280f49290`
- **Turnover:** ~29.8 rebals/yr (WATCHDOG — >20)

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.568 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 0.825 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 6.144% — tier **Folclore** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -11.526% — tier **Excelente** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.231 | **PASS** |
| 6 WF >= 6/8 positive | 7/8 profitable | **PASS** |
| 7 Median hold >= 5d | 3.0 trading days | **FAIL** |
| 8 IR vs SPY >= 0.2 | -0.528 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | n/a (non-winner) | **FAIL** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-9.97298e-05; FULL=-4.01835e-05 | **FAIL** |
| 11 PBO < 0.5 (HARD) | pbo=0.524 | **FAIL** |
| 12 DSR p < 0.05 (HARD) | n/a | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.593 (cagr=4.498%) | **FAIL** |

### Window summaries

#### IS (2004-11-18 → 2015-12-31)
- days=2,799, rebal+flips=340, median_hold=3.0d
- Sharpe(daily)=0.568, CAGR=4.042%, MDD=-16.368%

#### OOS (2016-01-01 → 2020-12-31)
- days=1,259, rebal+flips=104, median_hold=4.0d
- Sharpe(daily)=0.825, CAGR=6.144% (tier **Folclore**), MDD=-11.526% (tier **Excelente**)
- IR vs SPY buy-hold: -0.528

#### FWD (2021-01-01 → 2026-04-15)
- days=1,326, rebal+flips=193, median_hold=2.0d
- Sharpe(daily)=0.231, CAGR=1.385%, MDD=-17.973%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| china_2015 | 189 | -3.431 | -16.397% | -13.119% |
| covid_2020_03 | 62 | -0.394 | -7.593% | -11.526% |
| rate_shock_2022 | 251 | -2.570 | -10.757% | -10.144% |
| bank_crisis_2023 | 104 | -1.344 | -10.747% | -9.269% |
| rally_2024 | 251 | 2.167 | 20.772% | -4.511% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 7 / 8
- Window returns: 9.24%, 1.59%, 12.61%, 16.88%, 22.79%, -10.00%, 4.48%, 25.05%
- Window MDDs: 6.02%, 8.08%, 10.79%, 5.34%, 5.40%, 17.12%, 9.89%, 11.53%

## B3-SSO-static-monthly — FAIL

- **Config hash:** `0d3adc6187`
- **Turnover:** ~12.1 rebals/yr (OK)

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.642 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 1.103 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 11.382% — tier **Marginal** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -18.666% — tier **Válido** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.421 | **PASS** |
| 6 WF >= 6/8 positive | 7/8 profitable | **PASS** |
| 7 Median hold >= 5d | 21.0 trading days | **PASS** |
| 8 IR vs SPY >= 0.2 | -0.367 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | n/a (non-winner) | **FAIL** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-0.000100205; FULL=2.16121e-05 | **FAIL** |
| 11 PBO < 0.5 (HARD) | pbo=0.524 | **FAIL** |
| 12 DSR p < 0.05 (HARD) | n/a | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.866 (cagr=9.251%) | **PASS** |

### Window summaries

#### IS (2004-11-18 → 2015-12-31)
- days=2,799, rebal+flips=134, median_hold=21.0d
- Sharpe(daily)=0.642, CAGR=6.324%, MDD=-32.639%

#### OOS (2016-01-01 → 2020-12-31)
- days=1,259, rebal+flips=60, median_hold=21.0d
- Sharpe(daily)=1.103, CAGR=11.382% (tier **Marginal**), MDD=-18.666% (tier **Válido**)
- IR vs SPY buy-hold: -0.367

#### FWD (2021-01-01 → 2026-04-15)
- days=1,326, rebal+flips=64, median_hold=21.0d
- Sharpe(daily)=0.421, CAGR=4.654%, MDD=-29.940%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| china_2015 | 189 | -0.028 | -0.689% | -6.378% |
| covid_2020_03 | 62 | 0.120 | -0.556% | -18.666% |
| rate_shock_2022 | 251 | -1.467 | -23.752% | -27.727% |
| bank_crisis_2023 | 104 | 1.003 | 10.686% | -6.487% |
| rally_2024 | 251 | 2.210 | 28.639% | -5.532% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 7 / 8
- Window returns: 18.92%, -15.83%, 30.44%, 26.18%, 22.42%, 5.86%, 6.27%, 52.18%
- Window MDDs: 5.70%, 28.59%, 19.56%, 5.23%, 7.03%, 8.32%, 10.36%, 18.67%

## B3-SSO-static-quarterly — FAIL

- **Config hash:** `c332f82af2`
- **Turnover:** ~4.1 rebals/yr (OK)

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.694 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 1.140 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 11.906% — tier **Marginal** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -17.524% — tier **Válido** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.420 | **PASS** |
| 6 WF >= 6/8 positive | 7/8 profitable | **PASS** |
| 7 Median hold >= 5d | 63.0 trading days | **PASS** |
| 8 IR vs SPY >= 0.2 | -0.314 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | pandas_static(no-tax)=14.104%, bt=14.681%, |Δ|=0.578pp (static ablation cell of winner) | **PASS** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-6.01709e-05; FULL=3.8132e-05 | **FAIL** |
| 11 PBO < 0.5 (HARD) | pbo=0.524 | **FAIL** |
| 12 DSR p < 0.05 (HARD) | p=0.1498 | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.894 (cagr=9.700%) | **PASS** |

### Window summaries

#### IS (2004-11-18 → 2015-12-31)
- days=2,799, rebal+flips=45, median_hold=63.0d
- Sharpe(daily)=0.694, CAGR=6.710%, MDD=-29.755%

#### OOS (2016-01-01 → 2020-12-31)
- days=1,259, rebal+flips=20, median_hold=63.0d
- Sharpe(daily)=1.140, CAGR=11.906% (tier **Marginal**), MDD=-17.524% (tier **Válido**)
- IR vs SPY buy-hold: -0.314

#### FWD (2021-01-01 → 2026-04-15)
- days=1,326, rebal+flips=22, median_hold=63.0d
- Sharpe(daily)=0.420, CAGR=4.663%, MDD=-29.830%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| china_2015 | 189 | -0.024 | -0.670% | -6.427% |
| covid_2020_03 | 62 | 0.398 | 7.270% | -17.524% |
| rate_shock_2022 | 251 | -1.493 | -24.036% | -27.538% |
| bank_crisis_2023 | 104 | 0.941 | 10.379% | -7.020% |
| rally_2024 | 251 | 2.224 | 28.877% | -5.585% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 7 / 8
- Window returns: 18.81%, -14.87%, 32.45%, 28.27%, 22.74%, 5.39%, 6.92%, 55.22%
- Window MDDs: 5.92%, 26.14%, 17.71%, 5.36%, 7.12%, 8.41%, 9.91%, 17.52%

## Data provenance

- SPY: Tiingo `adj_close` 2001-05-14+ pct_change
- UPRO: synth 2004-11-18 → 2009-06-24 (synthesize_letf_returns_ffr_aware L=3, ER=0.95%) + Tiingo real 2009-06-25+
- SSO: synth 2004-11-18 → 2006-06-20 (synthesize_letf_returns_ffr_aware L=2, ER=0.95%) + Tiingo real 2006-06-21+
- TLT: Tiingo `adj_close` 2002-07-26+ pct_change
- GLD: Tiingo `adj_close` 2004-11-18+ pct_change
- SHV: Tiingo `adj_close` 2007-01-11+ pct_change; pre-2007 flat 4%/yr
- FFR proxy: Kenneth French daily `rf` × 252

## Citations

- `[phase3_7_literature_sprint, §T1 paper 3]` — Pauchlyova 2025 Quantpedia
- `[leverage_for_the_long_run, p.13-17, p.16]` — Gayed SMA-200 canonical
- `[advances_fin_ml, p.31-34]` — F2-alignment
- `[advances_fin_ml, p.208-211]` — PBO via CSCV
- `[advances_fin_ml, p.275]` — Deflated Sharpe Ratio
- `docs/investment-mandate.md §2.4` — 13-gate framework
- `docs/investment-mandate.md §2.2, §2.3, §7` — CAGR/MDD tiers warning-only
- `docs/investment-mandate.md §4.6` — rota B Inter cost model (DARF 15%)
