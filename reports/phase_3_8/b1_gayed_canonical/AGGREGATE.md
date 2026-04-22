# Phase 3.8 B1 — Gayed canonical SMA-200 LETF rotation — Honest Validation

**Verdict: FAIL** — 0/2 variants pass all 13 gates (hard fails total: 4)

- **Git SHA:** `3f6f5a7c16`
- **Universe:** SPY (SPX-TR stitched KF+Tiingo), LETF synth pre-inception + real post
- **Windows:** IS `1970-01-02 → 1999-12-31`, OOS `2000-01-01 → 2015-12-31`, FWD `2016-01-01 → 2026-04-15`
- **Cost model (rota B Inter, mandate §4.6):** commission=0 + spread=5.0bps/side + LETF ER=0.95% + DARF=15% year-end + cash_sleeve=4.0%/yr

## B1-UPRO-3x — FAIL

- **Config hash:** `1bc48acdd6`
- **Turnover:** ~5.3 trades/yr (OK)
- **OOS on-regime fraction:** 63.90%

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.758 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 0.371 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 6.856% — tier **Folclore** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -51.202% — tier **Reject** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.710 | **PASS** |
| 6 WF >= 6/8 positive | 8/8 profitable | **PASS** |
| 7 Median hold >= 5d | 16.0 trading days | **PASS** |
| 8 IR vs SPY >= 0.2 | 0.208 | **PASS** |
| 9 Cross-lib CAGR <= 3pp (HARD) | pandas(no-tax)=9.487%, vbt=9.487%, |Δ|=0.000pp (compared ex-tax to match vbt scope) | **PASS** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-0.0004973; FULL=0.00032036 | **FAIL** |
| 11 PBO < 0.5 (HARD) | pbo=0.238 | **PASS** |
| 12 DSR p < 0.05 (HARD) | p=0.4912 | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.282 (cagr=3.943%) | **FAIL** |

### Window summaries

#### IS (1970-01-02 → 1999-12-31)
- days=7,582, switches=137, median_hold=16.0d, on_regime=75.44%
- Sharpe(daily)=0.758, CAGR=20.843%, MDD=-46.987%
- Cumulative: switches=6.850%, tax=5581.964%

#### OOS (2000-01-01 → 2015-12-31)
- days=4,025, switches=109, median_hold=4.0d
- Sharpe(daily)=0.371, CAGR=6.856% (tier **Folclore**), MDD=-51.202% (tier **Reject**)
- IR vs SPY buy-hold: 0.208

#### FWD (2016-01-01 → 2026-04-15)
- days=2,585, switches=51, median_hold=4.0d
- Sharpe(daily)=0.710, CAGR=20.337%, MDD=-53.395%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| dotcom_2000_2002 | 752 | -0.444 | -3.514% | -19.912% |
| gfc_2007_2009 | 378 | -1.038 | -18.566% | -33.949% |
| euro_2011 | 170 | -2.311 | -57.019% | -43.836% |
| covid_2020_03 | 62 | -3.433 | -83.660% | -45.053% |
| rate_shock_2022 | 251 | -1.892 | -38.229% | -39.272% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 8 / 8
- Window returns: 120.23%, 73.66%, 459.30%, 77.89%, 345.31%, 161.72%, 16.62%, 71.40%
- Window MDDs: 39.45%, 46.99%, 33.22%, 46.33%, 37.81%, 32.81%, 49.40%, 51.20%

## B1-SSO-2x — FAIL

- **Config hash:** `cc7b1014ef`
- **Turnover:** ~5.3 trades/yr (OK)
- **OOS on-regime fraction:** 63.90%

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.821 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 0.391 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 6.101% — tier **Folclore** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -37.416% — tier **Warning** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.727 | **PASS** |
| 6 WF >= 6/8 positive | 8/8 profitable | **PASS** |
| 7 Median hold >= 5d | 16.0 trading days | **PASS** |
| 8 IR vs SPY >= 0.2 | 0.112 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | pandas(no-tax)=8.190%, vbt=8.190%, |Δ|=0.000pp (compared ex-tax to match vbt scope) | **PASS** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-0.000297392; FULL=0.000250218 | **FAIL** |
| 11 PBO < 0.5 (HARD) | pbo=0.238 | **PASS** |
| 12 DSR p < 0.05 (HARD) | p=0.4586 | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.286 (cagr=3.850%) | **FAIL** |

### Window summaries

#### IS (1970-01-02 → 1999-12-31)
- days=7,582, switches=137, median_hold=16.0d, on_regime=75.44%
- Sharpe(daily)=0.821, CAGR=16.301%, MDD=-33.570%
- Cumulative: switches=6.850%, tax=1764.942%

#### OOS (2000-01-01 → 2015-12-31)
- days=4,025, switches=109, median_hold=4.0d
- Sharpe(daily)=0.391, CAGR=6.101% (tier **Folclore**), MDD=-37.416% (tier **Warning**)
- IR vs SPY buy-hold: 0.112

#### FWD (2016-01-01 → 2026-04-15)
- days=2,585, switches=51, median_hold=4.0d
- Sharpe(daily)=0.727, CAGR=15.206%, MDD=-39.072%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| dotcom_2000_2002 | 752 | -0.215 | -1.188% | -13.586% |
| gfc_2007_2009 | 378 | -0.970 | -11.737% | -23.566% |
| euro_2011 | 170 | -2.185 | -40.842% | -30.332% |
| covid_2020_03 | 62 | -3.406 | -68.843% | -32.389% |
| rate_shock_2022 | 251 | -1.841 | -26.394% | -27.280% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 8 / 8
- Window returns: 87.06%, 72.67%, 270.03%, 69.11%, 206.96%, 108.25%, 22.97%, 55.50%
- Window MDDs: 27.90%, 33.57%, 22.72%, 32.54%, 26.53%, 22.41%, 35.18%, 37.42%

## Data provenance

- SPX-TR pre-2001-05-14: Kenneth French daily factors (`Mkt-RF + RF`)
- SPX-TR post-2001-05-14: Tiingo SPY `adj_close` pct_change
- UPRO-3x pre-2009-06-25: `synthesize_letf_returns_ffr_aware(L=3, ER=0.95%)`
- UPRO-3x post-2009-06-25: Tiingo UPRO `adj_close` pct_change
- SSO-2x pre-2006-06-21: `synthesize_letf_returns_ffr_aware(L=2, ER=0.95%)`
- SSO-2x post-2006-06-21: Tiingo SSO `adj_close` pct_change
- FFR proxy: Kenneth French daily `rf` × 252
- Cash sleeve: flat 4%/yr (mandate §4.6 proxy for long-term 3mo T-bill)

## Known limitations

- Single cash rate (4%/yr flat) is a simplification; real cash sleeve would
  track the daily 3mo T-bill curve. Second-order effect on long side.
- Year-end DARF model: 15% on the year's **net** gain; loss-carry NOT
  modelled (conservative per mandate §4.6 rota B).
- Real LETF data carries tracking error + ER vs theoretical synth. We
  preserve the real-LETF pct_change as-is; no additional ER drag is added
  in the post-inception stitch. Synth vs real 2020 diff bounded to ±5pp
  (smoke test `test_synth_upro_matches_real_within_5pp_2020`).

## Citations

- `[leverage_for_the_long_run, p.7-8, p.13-17, Table 8]` — canonical Gayed LRS
- `[leverage_for_the_long_run, p.16]` — SMA-200 ~5 trades/yr; ER 0.95%
- `[leverage_for_the_long_run, p.21]` — cash (not BIL) on RISK_OFF
- `[advances_fin_ml, p.31-34]` — F2-alignment prev_weight × ret
- `[advances_fin_ml, p.208-211]` — PBO via CSCV
- `[advances_fin_ml, p.275]` — Deflated Sharpe Ratio
- `[docs/investment-mandate.md §2.4]` — 13-gate framework
- `[docs/investment-mandate.md §2.2, §2.3, §7]` — CAGR/MDD tiers warning-only
- `[docs/investment-mandate.md §4.6]` — rota B Inter cost model (DARF 15%)
